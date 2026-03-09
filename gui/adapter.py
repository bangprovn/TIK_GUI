"""
TIK5 GUI Adapter - I/O redirection, threading bridge, Rich patching.

This module redirects stdout/stderr and input() to the GUI console widget,
and runs CLI operations in worker threads so the GUI stays responsive.
"""
import builtins
import os
import queue
import sys
import threading
import re


class OutputRedirector:
    """Redirects sys.stdout.write to a queue for GUI consumption."""

    def __init__(self, output_queue):
        self._queue = output_queue
        self._original = sys.stdout

    def write(self, text):
        if text:
            self._queue.put(("output", text))

    def flush(self):
        pass

    def fileno(self):
        return getattr(self._original, 'fileno', lambda: -1)()

    def isatty(self):
        return False

    @property
    def encoding(self):
        return getattr(self._original, 'encoding', 'utf-8')


class InputRedirector:
    """Replaces builtins.input to post requests to GUI and block until answered."""

    def __init__(self, output_queue):
        self._queue = output_queue
        self._event = threading.Event()
        self._response = ""

    def __call__(self, prompt=""):
        if prompt:
            self._queue.put(("output", str(prompt)))
        self._event.clear()
        self._queue.put(("input_request", str(prompt)))
        self._event.wait()
        return self._response

    def provide_response(self, response):
        """Called from GUI thread to unblock the worker thread."""
        self._response = response
        self._event.set()


class SafeChdir:
    """Thread-safe os.chdir wrapper using a lock."""

    def __init__(self, lock):
        self._lock = lock
        self._original_chdir = os.chdir

    def __call__(self, path):
        with self._lock:
            self._original_chdir(path)

    def restore(self):
        os.chdir = self._original_chdir


class GUIAdapter:
    """
    Manages I/O redirection between CLI code and the GUI.
    """

    def __init__(self):
        self.output_queue = queue.Queue()
        self._output_redirector = OutputRedirector(self.output_queue)
        self._input_redirector = InputRedirector(self.output_queue)
        self._original_stdout = None
        self._original_stderr = None
        self._original_input = None
        self._original_stdout_write = None
        self._worker_thread = None
        self._task_lock = threading.Lock()
        self._chdir_lock = threading.Lock()
        self._safe_chdir = None
        self._attached = False

    def attach(self):
        """Redirect stdout/stderr/input to GUI and make chdir thread-safe."""
        if self._attached:
            return
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        self._original_input = builtins.input
        self._original_stdout_write = sys.stdout.write

        sys.stdout = self._output_redirector
        sys.stderr = self._output_redirector
        builtins.input = self._input_redirector

        # Make os.chdir thread-safe
        self._safe_chdir = SafeChdir(self._chdir_lock)
        os.chdir = self._safe_chdir

        self._attached = True

    def detach(self):
        """Restore original I/O."""
        if not self._attached:
            return
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr
        builtins.input = self._original_input
        if self._safe_chdir:
            self._safe_chdir.restore()
        self._attached = False

    def provide_input(self, response):
        """Provide input response from GUI to blocked worker thread."""
        self._input_redirector.provide_response(response)

    def run_task(self, func, *args, callback=None, **kwargs):
        """Run a function in a worker thread."""
        if self._worker_thread and self._worker_thread.is_alive():
            self.output_queue.put(("output", "\n[!] A task is already running.\n"))
            return False

        def _worker():
            try:
                result = func(*args, **kwargs)
                self.output_queue.put(("task_done", result))
                if callback:
                    callback(result)
            except Exception as e:
                import traceback
                tb = traceback.format_exc()
                self.output_queue.put(("output", f"\n[ERROR] {type(e).__name__}: {e}\n{tb}\n"))
                self.output_queue.put(("task_error", str(e)))

        self._worker_thread = threading.Thread(target=_worker, daemon=True)
        self._worker_thread.start()
        return True

    @property
    def is_busy(self):
        return self._worker_thread is not None and self._worker_thread.is_alive()

    def patch_rich(self):
        """
        Patch Rich library to work with GUI output instead of terminal.
        Call this before importing run.py modules that use Rich.
        """
        os.environ["TERM"] = "dumb"
        os.environ["NO_COLOR"] = "1"

        try:
            import rich.progress
            _original_track = rich.progress.track

            def gui_track(sequence, description="Working...", **kwargs):
                items = list(sequence)
                total = len(items)
                for i, item in enumerate(items):
                    progress = (i + 1) / total if total > 0 else 1.0
                    self.output_queue.put(("progress", (progress, description)))
                    yield item
                self.output_queue.put(("progress_done", description))

            rich.progress.track = gui_track
        except ImportError:
            pass

        try:
            import rich.console
            import rich.table
            _OrigConsole = rich.console.Console

            adapter_queue = self.output_queue

            class GUIConsole(_OrigConsole):
                def status(self_inner, *args, **kwargs):
                    return _GUIStatus(self_inner, adapter_queue, *args, **kwargs)

                def print(self_inner, *args, **kwargs):
                    """Redirect Console().print() including Tables to text output."""
                    parts = []
                    for arg in args:
                        if isinstance(arg, rich.table.Table):
                            parts.append(_render_table(arg))
                        else:
                            # Strip Rich markup
                            text = re.sub(r'\[/?[^\]]*\]', '', str(arg))
                            parts.append(text)
                    adapter_queue.put(("output", " ".join(parts) + "\n"))

            def _render_table(table):
                """Render a Rich Table to plain text."""
                lines = []
                # Header
                headers = [str(c.header) for c in table.columns]
                headers_clean = [re.sub(r'\[/?[^\]]*\]', '', h) for h in headers]
                if headers_clean:
                    lines.append(" | ".join(headers_clean))
                    lines.append("-" * max(40, sum(len(h) + 3 for h in headers_clean)))
                # Rows
                if table.columns:
                    num_rows = max((len(c._cells) for c in table.columns), default=0)
                    for i in range(num_rows):
                        row_cells = []
                        for col in table.columns:
                            cell = str(col._cells[i]) if i < len(col._cells) else ""
                            cell = re.sub(r'\[/?[^\]]*\]', '', cell)
                            row_cells.append(cell)
                        lines.append(" | ".join(row_cells))
                return "\n".join(lines)

            class _GUIStatus:
                def __init__(self_inner, console, output_q, status_text="", **kwargs):
                    self_inner._output_q = output_q
                    clean = re.sub(r'\[/?[^\]]*\]', '', str(status_text))
                    self_inner._text = clean

                def __enter__(self_inner):
                    self_inner._output_q.put(("output", f"  {self_inner._text}\n"))
                    self_inner._output_q.put(("progress", (0.5, self_inner._text)))
                    return self_inner

                def __exit__(self_inner, *args):
                    self_inner._output_q.put(("progress_done", self_inner._text))

            rich.console.Console = GUIConsole
        except ImportError:
            pass

    def patch_cls(self):
        """Patch src.api.cls() to clear console widget instead of terminal."""
        try:
            import src.api
            src.api.cls = lambda: self.output_queue.put(("clear", None))
        except ImportError:
            pass
