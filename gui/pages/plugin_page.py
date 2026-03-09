"""
TIK5 GUI Plugin Page - Plugin list, install/uninstall/run.
Includes dynamic form generation from main.json schema.
"""
import os
import json
import customtkinter as ctk
from gui.pages.base_page import BasePage
from gui.theme import FONTS, COLORS
from tkinter import filedialog


class PluginFormDialog(ctk.CTkToplevel):
    """Dynamic form dialog generated from plugin main.json schema.
    Replaces CLI plug_parse() interactive prompts with proper GUI widgets."""

    def __init__(self, master, json_path):
        super().__init__(master)
        self.title("Plugin Configuration")
        self.geometry("520x500")
        self.resizable(True, True)
        self.transient(master)
        self.grab_set()

        self.result = None  # (gavs, value) or None
        self._gavs = {}
        self._values = []
        self._widgets = {}

        try:
            with open(json_path, 'r', encoding='UTF-8') as f:
                data = json.load(f)
        except Exception as e:
            ctk.CTkLabel(self, text=f"Parse Error: {e}", font=FONTS["body"],
                         text_color=COLORS["error"]).pack(pady=20)
            ctk.CTkButton(self, text="Close", command=self.destroy).pack(pady=10)
            self._center()
            self.wait_window()
            return

        plugin_title = data.get('main', {}).get('info', {}).get('title', 'Plugin')
        ctk.CTkLabel(self, text=plugin_title, font=FONTS["heading"],
                     text_color=COLORS["text_primary"]).pack(pady=(15, 10))

        # Scrollable form
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=5)

        # Parse and build controls
        for group_name, group_data in data.get('main', {}).items():
            if group_name == 'info':
                continue
            if not isinstance(group_data, dict) or 'controls' not in group_data:
                continue

            for con in group_data['controls']:
                con_type = con.get('type', '')
                set_var = con.get('set', '')
                text = con.get('text', '')

                if set_var:
                    self._values.append(set_var)

                if con_type == 'text':
                    if text != plugin_title:
                        ctk.CTkLabel(scroll, text=f"--- {text} ---",
                                     font=FONTS["subheading"],
                                     text_color=COLORS["warning"]).pack(fill="x", pady=(8, 3))

                elif con_type == 'filechose':
                    self._build_filechose(scroll, set_var, text)

                elif con_type == 'radio':
                    options_str = con.get('opins', '')
                    self._build_radio(scroll, set_var, text, options_str)

                elif con_type == 'input':
                    self._build_input(scroll, set_var, text)

                elif con_type == 'checkbutton':
                    self._build_checkbutton(scroll, set_var, text)

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)
        ctk.CTkButton(btn_frame, text="Run", font=FONTS["button"], width=120,
                      command=self._on_run, fg_color=COLORS["accent"]).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancel", font=FONTS["button"], width=120,
                      command=self.destroy,
                      fg_color=COLORS["bg_card"]).pack(side="left", padx=10)

        self._center()
        self.wait_window()

    def _build_filechose(self, parent, var_name, text):
        """File chooser widget."""
        frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=8)
        frame.pack(fill="x", pady=3, padx=3)

        ctk.CTkLabel(frame, text=text or "Select file:", font=FONTS["body"],
                     text_color=COLORS["text_primary"]).pack(padx=10, pady=(5, 2), anchor="w")

        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=(0, 5))

        entry = ctk.CTkEntry(row, font=FONTS["body"])
        entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        def browse():
            path = filedialog.askopenfilename()
            if path:
                entry.delete(0, "end")
                entry.insert(0, path)

        ctk.CTkButton(row, text="Browse", width=70, font=FONTS["small"],
                      command=browse).pack(side="right")

        self._widgets[var_name] = ('entry', entry)

    def _build_radio(self, parent, var_name, text, options_str):
        """Radio button selection."""
        frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=8)
        frame.pack(fill="x", pady=3, padx=3)

        if text:
            ctk.CTkLabel(frame, text=text, font=FONTS["body"],
                         text_color=COLORS["text_primary"]).pack(padx=10, pady=(5, 2), anchor="w")

        options = options_str.split()
        radio_var = ctk.StringVar()
        first_value = None

        for opt in options:
            if '|' in opt:
                label, value = opt.split('|', 1)
            else:
                label = value = opt
            if first_value is None:
                first_value = value
                radio_var.set(value)
            ctk.CTkRadioButton(
                frame, text=label, variable=radio_var, value=value,
                font=FONTS["body"]
            ).pack(padx=15, pady=2, anchor="w")

        frame.pack_configure(pady=3)
        self._widgets[var_name] = ('radio', radio_var)

    def _build_input(self, parent, var_name, text):
        """Text input."""
        frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=8)
        frame.pack(fill="x", pady=3, padx=3)

        if text:
            ctk.CTkLabel(frame, text=text, font=FONTS["body"],
                         text_color=COLORS["text_primary"]).pack(padx=10, pady=(5, 2), anchor="w")

        entry = ctk.CTkEntry(frame, font=FONTS["body"])
        entry.pack(fill="x", padx=10, pady=(0, 5))

        self._widgets[var_name] = ('entry', entry)

    def _build_checkbutton(self, parent, var_name, text):
        """Checkbox."""
        frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=8)
        frame.pack(fill="x", pady=3, padx=3)

        var = ctk.IntVar(value=0)
        ctk.CTkCheckBox(
            frame, text=text or var_name, variable=var,
            font=FONTS["body"]
        ).pack(padx=10, pady=5, anchor="w")

        self._widgets[var_name] = ('check', var)

    def _on_run(self):
        """Collect values from all widgets."""
        gavs = {}
        for var_name, (wtype, widget) in self._widgets.items():
            if wtype == 'entry':
                gavs[var_name] = widget.get()
            elif wtype == 'radio':
                gavs[var_name] = widget.get()
            elif wtype == 'check':
                gavs[var_name] = widget.get()
        self.result = (gavs, self._values)
        self.destroy()

    def _center(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = self.master.winfo_rootx() + (self.master.winfo_width() - w) // 2
        y = self.master.winfo_rooty() + (self.master.winfo_height() - h) // 2
        self.geometry(f"+{x}+{y}")


class PluginPage(BasePage):
    """Plugin management page."""

    def __init__(self, master, app, **kwargs):
        super().__init__(master, app, title="Plugins", **kwargs)

        header = self.create_header("Plugins")
        ctk.CTkButton(
            header, text="< Back", font=FONTS["body"],
            width=70, command=lambda: app.show_page("project"),
            fg_color="transparent", hover_color=COLORS["bg_card"],
            text_color=COLORS["text_secondary"]
        ).pack(side="right")

        # Action bar
        action_bar = self.create_action_bar()

        ctk.CTkButton(
            action_bar, text="Install MPK", font=FONTS["button"],
            command=self._install_mpk, width=120,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"]
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            action_bar, text="Refresh", font=FONTS["button"],
            command=self._refresh, width=80,
            fg_color="transparent", hover_color=COLORS["bg_card"],
            text_color=COLORS["text_secondary"]
        ).pack(side="right", padx=5)

        # Plugin list
        self._plugin_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=COLORS["border"]
        )
        self._plugin_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self._plugins = {}

    def on_show(self):
        self._refresh()

    def _get_subs_dir(self):
        return os.path.join(self.app.localdir, "bin", "subs")

    def _refresh(self):
        """Refresh plugin list."""
        for w in self._plugin_frame.winfo_children():
            w.destroy()
        self._plugins.clear()

        subs_dir = self._get_subs_dir()
        if not os.path.exists(subs_dir):
            os.makedirs(subs_dir, exist_ok=True)

        idx = 0
        for sub in sorted(os.listdir(subs_dir)):
            info_file = os.path.join(subs_dir, sub, "info.json")
            if not os.path.isfile(info_file):
                continue

            try:
                with open(info_file, 'r', encoding='utf-8') as f:
                    info = json.load(f)
            except (json.JSONDecodeError, OSError):
                continue

            idx += 1
            name = info.get('name', sub)
            author = info.get('author', 'Unknown')
            version = info.get('version', '')
            describe = info.get('describe', '')
            depend = info.get('depend', '')

            self._plugins[idx] = (sub, name)

            card = ctk.CTkFrame(self._plugin_frame, fg_color=COLORS["bg_card"], corner_radius=8)
            card.pack(fill="x", padx=5, pady=3)

            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)

            ctk.CTkLabel(
                info_frame, text=name, font=FONTS["subheading"],
                text_color=COLORS["text_primary"], anchor="w"
            ).pack(fill="x")

            meta_parts = []
            if version:
                meta_parts.append(f"v{version}")
            meta_parts.append(f"by {author}")
            if depend:
                meta_parts.append(f"depends: {depend}")
            ctk.CTkLabel(
                info_frame, text=" | ".join(meta_parts), font=FONTS["small"],
                text_color=COLORS["text_muted"], anchor="w"
            ).pack(fill="x")

            if describe:
                ctk.CTkLabel(
                    info_frame, text=describe, font=FONTS["small"],
                    text_color=COLORS["text_secondary"], anchor="w",
                    wraplength=400
                ).pack(fill="x")

            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(side="right", padx=10, pady=10)

            # Check if plugin has main.sh (runnable)
            has_main = os.path.exists(os.path.join(subs_dir, sub, "main.sh"))

            if has_main:
                ctk.CTkButton(
                    btn_frame, text="Run", font=FONTS["small"],
                    width=60, height=28,
                    command=lambda s=sub, n=name: self._run_plugin(s, n),
                    fg_color=COLORS["accent"]
                ).pack(side="left", padx=3)

            ctk.CTkButton(
                btn_frame, text="Uninstall", font=FONTS["small"],
                width=80, height=28,
                command=lambda s=sub, n=name: self._uninstall_plugin(s, n),
                fg_color=COLORS["error"]
            ).pack(side="left", padx=3)

        if idx == 0:
            ctk.CTkLabel(
                self._plugin_frame,
                text="No plugins installed.\nClick 'Install MPK' to add one.",
                font=FONTS["body"],
                text_color=COLORS["text_muted"],
                justify="center"
            ).pack(pady=40)

    def _install_mpk(self):
        """Install an MPK plugin."""
        file_path = filedialog.askopenfilename(
            filetypes=[("MPK files", "*.mpk"), ("ZIP2 files", "*.zip2"), ("All files", "*.*")]
        )
        if not file_path:
            return

        def _worker():
            import run as run_module
            try:
                if file_path.endswith('.zip2'):
                    from src import zip2mpk
                    mpk_path = zip2mpk.main(file_path, os.getcwd())
                    run_module.installmpk(mpk_path)
                else:
                    run_module.installmpk(file_path)
            except Exception as e:
                import traceback
                self.app.console_print(f"[ERROR] Install failed: {e}\n{traceback.format_exc()}\n")

        def _on_done(r=None):
            self.app.after(0, self._refresh)

        self.run_task(_worker, callback=_on_done)

    def _run_plugin(self, sub_id, name):
        """Run a plugin with GUI form for main.json configuration."""
        project = self.app.current_project
        if not project:
            self.app.console_print("[ERROR] No project selected.\n")
            return

        project_dir = os.path.join(self.app.localdir, project)
        subs_dir = self._get_subs_dir()
        plugin_path = os.path.join(subs_dir, sub_id)
        main_json = os.path.join(plugin_path, "main.json")

        # Collect configuration via GUI form if main.json exists
        gavs = None
        value = None
        if os.path.exists(main_json):
            dialog = PluginFormDialog(self.app, main_json)
            if dialog.result is None:
                return
            gavs, value = dialog.result

        def _worker():
            import run as run_module
            from src.utils import call
            from src.api import f_remove
            try:
                gen = run_module.gen_sh_engine(project_dir, gavs, value)
                call(["busybox", "ash", gen,
                      os.path.join(plugin_path, "main.sh").replace(os.sep, "/")])
                f_remove(gen)
                self.app.console_print(f"\nPlugin '{name}' completed.\n")
            except Exception as e:
                import traceback
                self.app.console_print(f"[ERROR] Plugin run failed: {e}\n{traceback.format_exc()}\n")

        self.run_task(_worker)

    def _uninstall_plugin(self, sub_id, name):
        """Uninstall a plugin with dependency resolution."""
        from gui.widgets.dialogs import ConfirmDialog

        # Check dependencies first
        subs_dir = self._get_subs_dir()
        dependents = []
        for i in os.listdir(subs_dir):
            info_file = os.path.join(subs_dir, i, "info.json")
            if not os.path.isfile(info_file):
                continue
            try:
                with open(info_file, 'r', encoding='UTF-8') as f:
                    data = json.load(f)
                for dep in data.get('depend', '').split():
                    if dep == sub_id:
                        dependents.append(data.get('name', i))
            except (json.JSONDecodeError, OSError):
                pass

        msg = f"Uninstall '{name}'?"
        if dependents:
            msg += f"\n\nThe following plugins depend on it and will also be removed:\n"
            msg += "\n".join(f"  - {d}" for d in dependents)

        dialog = ConfirmDialog(self.app, title="Uninstall Plugin", message=msg)
        if not dialog.result:
            return

        def _worker():
            import run as run_module
            try:
                run_module.unmpk(sub_id, name, subs_dir)
                self.app.console_print(f"Uninstalled: {name}\n")
            except Exception as e:
                self.app.console_print(f"[ERROR] Uninstall failed: {e}\n")

        def _on_done(r=None):
            self.app.after(0, self._refresh)

        self.run_task(_worker, callback=_on_done)
