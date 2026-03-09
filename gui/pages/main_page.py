"""
TIK5 GUI Main/Home Page - Project list, create, delete, unpack ROM.
Handles ROM unpack flow with autounpack() using GUI prompts.
"""
import os
import time
import customtkinter as ctk
from gui.pages.base_page import BasePage
from gui.widgets.project_card import ProjectCard
from gui.widgets.file_drop import FileDropZone
from gui.widgets.dialogs import TextInputDialog, ConfirmDialog
from gui.theme import FONTS, COLORS


class MainPage(BasePage):
    """Home page showing project list and main actions."""

    def __init__(self, master, app, **kwargs):
        super().__init__(master, app, title="Home", **kwargs)

        # Header
        self.create_header("TIK5 - Android ROM Tool")

        # Action buttons bar
        action_bar = self.create_action_bar()

        ctk.CTkButton(
            action_bar, text="New Project", font=FONTS["button"],
            command=self._new_project, width=130,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"]
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            action_bar, text="Unpack ROM", font=FONTS["button"],
            command=self._unpack_rom, width=130,
            fg_color=COLORS["bg_card"], hover_color=COLORS["bg_card_hover"]
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            action_bar, text="Download ROM", font=FONTS["button"],
            command=self._download_rom, width=130,
            fg_color=COLORS["bg_card"], hover_color=COLORS["bg_card_hover"]
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            action_bar, text="Refresh", font=FONTS["button"],
            command=self._refresh, width=80,
            fg_color="transparent", hover_color=COLORS["bg_card"],
            text_color=COLORS["text_secondary"]
        ).pack(side="right", padx=5)

        # Drop zone
        self._drop_zone = FileDropZone(
            self, on_file_selected=self._on_file_dropped
        )
        self._drop_zone.pack(fill="x", padx=20, pady=10)

        # Project list label
        self._list_label = ctk.CTkLabel(
            self, text="Project List", font=FONTS["subheading"],
            text_color=COLORS["text_primary"], anchor="w"
        )
        self._list_label.pack(fill="x", padx=25, pady=(10, 5))

        # Scrollable project list
        self._project_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=COLORS["border"]
        )
        self._project_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

    def on_show(self):
        self._refresh()

    def _refresh(self):
        """Refresh the project list."""
        for widget in self._project_frame.winfo_children():
            widget.destroy()

        localdir = self.app.localdir
        projects = []
        skip_dirs = {'bin', 'src', 'gui', '__pycache__', 'build', 'dist', 'venv',
                     'node_modules', '.git', '.idea'}
        try:
            for item in sorted(os.listdir(localdir)):
                if item in skip_dirs or item.startswith('.'):
                    continue
                full_path = os.path.join(localdir, item)
                if os.path.isdir(full_path):
                    # Skip if it's a Python file directory
                    if item.endswith('.py') or item.endswith('.egg-info'):
                        continue
                    projects.append((item, full_path))
        except OSError:
            pass

        if not projects:
            ctk.CTkLabel(
                self._project_frame,
                text="No projects found.\nCreate a new project or unpack a ROM to get started.",
                font=FONTS["body"],
                text_color=COLORS["text_muted"],
                justify="center"
            ).pack(pady=40)
        else:
            for name, path in projects:
                card = ProjectCard(
                    self._project_frame,
                    project_name=name,
                    project_path=path,
                    on_click=self._open_project,
                    on_delete=self._delete_project,
                )
                card.pack(fill="x", padx=5, pady=3)

    def _new_project(self):
        """Create a new empty project."""
        dialog = TextInputDialog(
            self.app, title="New Project",
            prompt="Enter Project Name:"
        )
        name = dialog.result
        if not name:
            return

        localdir = self.app.localdir
        project_path = os.path.join(localdir, name)
        if os.path.exists(project_path):
            name = f"{name}_{time.strftime('%m%d%H%M%S')}"
            project_path = os.path.join(localdir, name)
            self.app.console_print(f"[WARNING] Project exists, renamed to: {name}\n")

        os.makedirs(os.path.join(project_path, "config"), exist_ok=True)
        self.app.console_print(f"Created project: {name}\n")
        self._refresh()
        self._open_project(name)

    def _open_project(self, project_name):
        """Open a project - navigate to project page."""
        self.app.set_current_project(project_name)
        self.app.show_page("project")

    def _delete_project(self, project_name):
        """Delete a project with confirmation."""
        dialog = ConfirmDialog(
            self.app,
            title="Delete Project",
            message=f"Are you sure you want to delete '{project_name}'?\n\nThis cannot be undone."
        )
        if dialog.result:
            import shutil
            project_path = os.path.join(self.app.localdir, project_name)
            try:
                # Handle Windows file naming issues (same as CLI rmdire())
                if os.name == 'nt':
                    from src.utils import call
                    for r, d, f in os.walk(project_path):
                        for i in d:
                            if i.endswith('.'):
                                call(['mv', str(os.path.join(r, i)), str(os.path.join(r, i[:1]))])
                        for i in f:
                            if i.endswith('.'):
                                call(['mv', os.path.join(r, i), os.path.join(r, i[:1])])
                shutil.rmtree(project_path)
                self.app.console_print(f"Deleted project: {project_name}\n")
            except PermissionError:
                self.app.console_print(f"[ERROR] Cannot delete: permission denied\n")
            except Exception as e:
                self.app.console_print(f"[ERROR] Failed to delete: {e}\n")
            self._refresh()

    def _unpack_rom(self):
        """Browse for ROM file."""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
        )
        if file_path:
            self._on_file_dropped(file_path)

    def _on_file_dropped(self, file_path):
        """Handle ROM file selection / drop - full unpack flow."""
        if not os.path.isfile(file_path):
            return

        import zipfile
        if not zipfile.is_zipfile(file_path):
            self.app.console_print(f"[ERROR] Not a valid ZIP file: {file_path}\n")
            return

        basename = os.path.basename(file_path).replace('.zip', '')
        dialog = TextInputDialog(
            self.app, title="Unpack ROM",
            prompt="Enter Project Name (leave empty for auto):",
            default=f"TI_{basename}"
        )
        project_name = dialog.result
        if project_name is None:
            return
        if not project_name:
            project_name = f"TI_{basename}"

        localdir = self.app.localdir
        if os.path.exists(os.path.join(localdir, project_name)):
            project_name = project_name + time.strftime("%m%d%H%M%S")
            self.app.console_print(f"Project exists, renamed to: {project_name}\n")

        project_path = os.path.join(localdir, project_name)
        os.makedirs(project_path, exist_ok=True)

        def _do_unpack():
            import zipfile as zf
            import shutil
            self.app.console_print(f"Unzipping ROM to {project_name}...\n")
            zf.ZipFile(file_path).extractall(project_path)
            self.app.console_print("Decomposing ROM...\n")

            # GUI-friendly autounpack: auto-extract all without prompts
            self._gui_autounpack(project_path)

            self.app.console_print(f"\nUnpack complete: {project_name}\n")

        def _on_done(result=None):
            self.app.after(0, self._refresh)
            self.app.after(100, lambda: self._open_project(project_name))

        self.run_task(_do_unpack, callback=_on_done)

    def _gui_autounpack(self, project_path):
        """GUI-friendly version of autounpack() that auto-unpacks everything
        without interactive prompts. Equivalent to CLI autounpack() with
        'unpack all' = 1 and 'delete payload' = 1."""
        import run as run_module
        import shutil

        localdir = self.app.localdir
        os.chdir(project_path)

        # Handle payload.bin first
        payload_path = os.path.join(project_path, "payload.bin")
        if os.path.exists(payload_path):
            self.app.console_print("Unpacking payload.bin (all partitions)...\n")
            try:
                from src.dumper import Dumper
                from src import utils
                with open(payload_path, 'rb') as pay:
                    all_parts = [p.partition_name for p in utils.payload_reader(pay).partitions]
                self.app.console_print(f"Partitions: {', '.join(all_parts)}\n")
                Dumper(payload_path, project_path, diff=False, old='old', images=all_parts).run()
            except Exception as e:
                self.app.console_print(f"[ERROR] payload.bin: {e}\n")

            # Cleanup waste files
            for waste in ['care_map.pb', 'apex_info.pb', 'payload.bin']:
                wp = os.path.join(project_path, waste)
                if os.path.exists(wp):
                    try:
                        os.remove(wp)
                    except Exception:
                        pass

            # Move config files
            config_dir = os.path.join(project_path, "config")
            if not os.path.isdir(config_dir):
                os.makedirs(config_dir)
            pp_file = os.path.join(project_path, "payload_properties.txt")
            if os.path.exists(pp_file):
                try:
                    shutil.move(pp_file, config_dir)
                except Exception:
                    pass
            meta_file = os.path.join(project_path, "META-INF", "com", "android", "metadata")
            if os.path.exists(meta_file):
                try:
                    shutil.move(meta_file, config_dir)
                except Exception:
                    pass

        # Unpack all remaining files
        for infile in os.listdir(project_path):
            os.chdir(project_path)
            fpath = os.path.join(project_path, infile)

            if os.path.isdir(fpath):
                continue
            if not os.path.exists(fpath):
                continue
            if os.path.getsize(fpath) == 0:
                continue
            if fpath.endswith('.list') or fpath.endswith('.patch.dat'):
                continue

            try:
                if infile.endswith('.new.dat.br'):
                    self.app.console_print(f"Unpacking: {infile}\n")
                    run_module.unpack(fpath, 'br', project_path)
                elif infile.endswith('.dat.1'):
                    self.app.console_print(f"Unpacking: {infile}\n")
                    run_module.unpack(fpath, 'dat.1', project_path)
                elif infile.endswith('.new.dat'):
                    self.app.console_print(f"Unpacking: {infile}\n")
                    run_module.unpack(fpath, 'dat', project_path)
                elif infile.endswith('.img'):
                    self.app.console_print(f"Unpacking: {infile}\n")
                    run_module.unpack(fpath, 'img', project_path)
            except Exception as e:
                self.app.console_print(f"[ERROR] {infile}: {e}\n")

        os.chdir(localdir)

    def _download_rom(self):
        """Open download dialog."""
        dialog = TextInputDialog(
            self.app, title="Download ROM",
            prompt="Enter download URL:"
        )
        url = dialog.result
        if not url:
            return

        def _do_download():
            from src import downloader
            self.app.console_print(f"Downloading: {url}\n")
            try:
                downloader.download([url], self.app.localdir)
                self.app.console_print("Download complete!\n")
            except Exception as e:
                self.app.console_print(f"[ERROR] Download failed: {e}\n")

        self.run_task(_do_download)
