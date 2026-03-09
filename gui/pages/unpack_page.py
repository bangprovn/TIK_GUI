"""
TIK5 GUI Unpack Page - File list with checkboxes, unpack selected/all.
Handles all file types from CLI: br, dat, dat.1, img, sparse, payload,
ozip, ofp, ops, win, win000, dtb.
"""
import os
import customtkinter as ctk
from gui.pages.base_page import BasePage
from gui.theme import FONTS, COLORS


class UnpackPage(BasePage):
    """Unpack page with file detection and unpack execution."""

    def __init__(self, master, app, **kwargs):
        super().__init__(master, app, title="Unpack", **kwargs)

        header = self.create_header("Unpack")

        ctk.CTkButton(
            header, text="< Back", font=FONTS["body"],
            width=70, command=lambda: app.show_page("project"),
            fg_color="transparent", hover_color=COLORS["bg_card"],
            text_color=COLORS["text_secondary"]
        ).pack(side="right")

        # Action bar
        action_bar = self.create_action_bar()

        ctk.CTkButton(
            action_bar, text="Unpack All", font=FONTS["button"],
            command=self._unpack_all, width=120,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"]
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            action_bar, text="Unpack Selected", font=FONTS["button"],
            command=self._unpack_selected, width=140,
            fg_color=COLORS["bg_card"], hover_color=COLORS["bg_card_hover"]
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            action_bar, text="Refresh", font=FONTS["button"],
            command=self._scan_files, width=80,
            fg_color="transparent", hover_color=COLORS["bg_card"],
            text_color=COLORS["text_secondary"]
        ).pack(side="right", padx=5)

        # Info label
        self._info_label = ctk.CTkLabel(
            self, text="", font=FONTS["small"],
            text_color=COLORS["text_muted"], anchor="w"
        )
        self._info_label.pack(fill="x", padx=25, pady=(0, 3))

        # File list
        self._file_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=COLORS["border"]
        )
        self._file_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self._files = {}  # {index: (filename, filetype, checkbox_var)}

    def on_show(self):
        self._scan_files()

    def _get_project_dir(self):
        project = self.app.current_project
        if not project:
            return None
        return os.path.join(self.app.localdir, project)

    def _scan_files(self):
        """Scan project directory for unpackable files."""
        for w in self._file_frame.winfo_children():
            w.destroy()
        self._files.clear()

        project_dir = self._get_project_dir()
        if not project_dir or not os.path.isdir(project_dir):
            return

        try:
            from src.utils import gettype
        except ImportError:
            self.app.console_print("[ERROR] Could not import src.utils.gettype\n")
            return

        idx = 0
        # Scan in the same order as CLI unpack_choo()
        scan_order = [
            ('.new.dat.br', 'Brotli', 'br'),
            ('.new.dat', 'DAT', 'dat'),
            ('.dat.1', 'Split DAT', 'dat.1'),
            ('.img', 'IMG', None),  # type detected dynamically
            ('.bin', 'BIN', 'payload'),
            ('.ozip', 'OZIP', 'ozip'),
            ('.ofp', 'OFP', 'ofp'),
            ('.ops', 'OPS', 'ops'),
            ('.win', 'WIN', 'win'),
            ('.win000', 'Split WIN', 'win000'),
            ('.dtb', 'DTB', 'dtb'),
        ]

        all_files = sorted(os.listdir(project_dir))
        current_category = None

        for ext, cat_name, default_type in scan_order:
            for fname in all_files:
                if not fname.endswith(ext):
                    continue
                # Avoid double-matching: .new.dat should not match .new.dat.br files
                if ext == '.new.dat' and fname.endswith('.new.dat.br'):
                    continue
                if ext == '.win' and fname.endswith('.win000'):
                    continue
                if ext == '.dat.1' and not fname.endswith('.new.dat.1'):
                    # Only match split dat files
                    pass

                fpath = os.path.join(project_dir, fname)
                if not os.path.isfile(fpath):
                    continue
                if os.path.getsize(fpath) == 0:
                    continue

                file_type = default_type
                detail_text = cat_name

                # Special detection for various types
                if ext == '.bin':
                    try:
                        if gettype(fpath) != 'payload':
                            continue
                    except Exception:
                        continue
                    detail_text = "Payload"
                elif ext == '.img':
                    try:
                        detected = gettype(fpath)
                    except Exception:
                        detected = "unknown"
                    if detected == 'sparse':
                        file_type = 'sparse'
                    elif detected == 'super':
                        file_type = 'img'
                    else:
                        file_type = 'img'
                    detail_text = detected.upper() if detected != "unknow" else "UNKNOWN"
                elif ext == '.ozip':
                    try:
                        if gettype(fpath) != 'ozip':
                            continue
                    except Exception:
                        continue
                elif ext == '.dtb':
                    try:
                        if gettype(fpath) != 'dtb':
                            continue
                    except Exception:
                        continue

                # Show category header
                if cat_name != current_category:
                    current_category = cat_name
                    cat_label = ctk.CTkLabel(
                        self._file_frame,
                        text=f"  [{cat_name}] Files",
                        font=FONTS["subheading"],
                        text_color=COLORS["warning"],
                        anchor="w"
                    )
                    cat_label.pack(fill="x", pady=(8, 2))

                idx += 1
                var = ctk.BooleanVar(value=False)

                row = ctk.CTkFrame(self._file_frame, fg_color="transparent")
                row.pack(fill="x", padx=5, pady=1)

                cb = ctk.CTkCheckBox(
                    row, text=f"  {fname}",
                    font=FONTS["body"], variable=var,
                    text_color=COLORS["text_primary"]
                )
                cb.pack(side="left")

                badge = ctk.CTkLabel(
                    row, text=f"<{detail_text}>",
                    font=FONTS["small"],
                    text_color=COLORS["text_muted"]
                )
                badge.pack(side="right", padx=10)

                self._files[idx] = (fname, file_type, var)

        self._info_label.configure(
            text=f"  {idx} files found in {project_dir}" if idx else ""
        )

        if not self._files:
            ctk.CTkLabel(
                self._file_frame,
                text="No unpackable files found.\nPlace ROM files in the project directory and click Refresh.",
                font=FONTS["body"],
                text_color=COLORS["text_muted"],
                justify="center"
            ).pack(pady=40)

    def _unpack_all(self):
        """Unpack all detected files."""
        if not self._files:
            return
        items = [(f, t) for f, t, _ in self._files.values()]
        self._do_unpack(items)

    def _unpack_selected(self):
        """Unpack selected files only."""
        items = [(f, t) for f, t, v in self._files.values() if v.get()]
        if not items:
            self.app.console_print("No files selected.\n")
            return
        self._do_unpack(items)

    def _do_unpack(self, items):
        """Run unpack operations with proper handling of interactive types."""
        project_dir = self._get_project_dir()
        if not project_dir:
            return

        # Pre-collect GUI inputs for types that need interactive prompts
        pre_inputs = {}
        for fname, ftype in items:
            if ftype == 'ofp':
                pre_inputs[fname] = self._ask_ofp_processor(fname)
                if pre_inputs[fname] is None:
                    return
            elif ftype == 'payload':
                pre_inputs[fname] = self._ask_payload_partitions(
                    os.path.join(project_dir, fname))
                if pre_inputs[fname] is None:
                    return

        def _worker():
            import run as run_module
            localdir = self.app.localdir
            os.chdir(project_dir)
            for fname, ftype in items:
                fpath = os.path.join(project_dir, fname)
                if not os.path.exists(fpath):
                    fpath = fname  # fallback to relative

                self.app.console_print(f"\nUnpacking: {fname} [{ftype}]\n")
                try:
                    if ftype == 'ofp':
                        # Handle OFP with pre-selected processor
                        processor = pre_inputs.get(fname, '1')
                        self._unpack_ofp(fpath, processor, project_dir)
                    elif ftype == 'payload':
                        # Handle payload with pre-selected partitions
                        partitions = pre_inputs.get(fname, 'all')
                        self._unpack_payload(fpath, partitions, project_dir)
                    else:
                        run_module.unpack(fpath, ftype, project_dir)
                except Exception as e:
                    import traceback
                    self.app.console_print(f"[ERROR] {fname}: {e}\n")
                    self.app.console_print(traceback.format_exc() + "\n")
            os.chdir(localdir)
            self.app.console_print("\nUnpack complete!\n")

        self.run_task(_worker)

    def _ask_ofp_processor(self, fname):
        """Ask user to select OFP processor type via GUI dialog."""
        from gui.widgets.dialogs import TextInputDialog
        dialog = TextInputDialog(
            self.app,
            title=f"OFP Processor - {fname}",
            prompt="Select the ROM processor type:\n[1] Qualcomm\n[2] MTK\nEnter number:",
            default="1"
        )
        return dialog.result

    def _ask_payload_partitions(self, fpath):
        """Ask user to select payload partitions via GUI dialog."""
        try:
            from src import utils
            with open(fpath, 'rb') as pay:
                parts = [p.partition_name for p in utils.payload_reader(pay).partitions]
        except Exception as e:
            self.app.console_print(f"[WARN] Could not read payload partitions: {e}\n")
            return 'all'

        from gui.widgets.dialogs import TextInputDialog
        parts_str = ", ".join(parts)
        dialog = TextInputDialog(
            self.app,
            title="Payload Partitions",
            prompt=f"Available partitions:\n{parts_str}\n\n"
                   f"Enter partition names (space-separated) or 'all':",
            default="all"
        )
        return dialog.result

    @staticmethod
    def _unpack_ofp(fpath, processor, project_dir):
        """Unpack OFP file with given processor type."""
        if processor == '2':
            from src import ofp_mtk_decrypt
            ofp_mtk_decrypt.main(fpath, project_dir)
        else:
            from src import ofp_qc_decrypt
            ofp_qc_decrypt.main(fpath, project_dir)

    @staticmethod
    def _unpack_payload(fpath, partitions, project_dir):
        """Unpack payload.bin with given partition selection."""
        from src.dumper import Dumper
        from src import utils
        import json
        import os as _os

        # Read partition list
        with open(fpath, 'rb') as pay:
            all_parts = [p.partition_name for p in utils.payload_reader(pay).partitions]

        if partitions == 'all' or not partitions:
            selected = all_parts
        else:
            selected = [p.strip() for p in partitions.split() if p.strip()]

        Dumper(fpath, project_dir, diff=False, old='old', images=selected).run()

        # Update parts_info
        config_dir = _os.path.join(project_dir, 'config')
        if not _os.path.exists(config_dir):
            _os.makedirs(config_dir)
        parts_file = _os.path.join(config_dir, 'parts_info')
        try:
            with open(parts_file, 'r') as f:
                parts_info = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            parts_info = {}
        with open(parts_file, 'w') as f:
            json.dump(parts_info, f, indent=2)
