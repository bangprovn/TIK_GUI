"""
TIK5 GUI Tools Page - Magisk patcher, AVB/encryption toggles, APK/JAR decompiler.
"""
import os
import customtkinter as ctk
from gui.pages.base_page import BasePage
from gui.theme import FONTS, COLORS
from gui.widgets.dialogs import ConfirmDialog, ChecklistDialog
from tkinter import filedialog


class ToolsPage(BasePage):
    """Other tools page: Magisk, AVB, encryption."""

    def __init__(self, master, app, **kwargs):
        super().__init__(master, app, title="Tools", **kwargs)

        header = self.create_header("Tools")
        ctk.CTkButton(
            header, text="< Back", font=FONTS["body"],
            width=70, command=lambda: app.show_page("project"),
            fg_color="transparent", hover_color=COLORS["bg_card"],
            text_color=COLORS["text_secondary"]
        ).pack(side="right")

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=10)

        # Magisk Patcher section
        self._build_section(content, "Magisk Patcher",
                            "Patch boot/vendor_boot images with Magisk",
                            "Patch Boot Image", self._magisk_patch)

        # Disable AVB section
        self._build_section(content, "Disable AVB Verification",
                            "Remove AVB verification from fstab files",
                            "Disable AVB", self._disable_avb)

        # Disable encryption section
        self._build_section(content, "Disable Data Encryption",
                            "Remove data encryption from fstab files",
                            "Disable Encryption", self._disable_encryption)

        # Deodex section
        self._build_section(content, "Deodex (vdexExtractor)",
                            "Extract .vdex files to .dex using vdexExtractor",
                            "Deodex", self._deodex)

        # Clean odex artifacts section
        self._build_section(content, "Clean Odex Artifacts",
                            "Remove all .dex, .vdex and .oat files from project",
                            "Clean", self._clean_odex_artifacts)

        # APK/JAR Decompiler section
        self._build_section(content, "APK/JAR Decompiler",
                            "Decompile APK and JAR files in project folder using apktool",
                            "Decompile", self._decompile_apk_jar)

    def _build_section(self, parent, title, description, button_text, command):
        """Build a tool section card."""
        card = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=10)
        card.pack(fill="x", pady=6)

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, padx=15, pady=12)

        ctk.CTkLabel(
            info, text=title, font=FONTS["subheading"],
            text_color=COLORS["text_primary"], anchor="w"
        ).pack(fill="x")

        ctk.CTkLabel(
            info, text=description, font=FONTS["small"],
            text_color=COLORS["text_muted"], anchor="w"
        ).pack(fill="x")

        ctk.CTkButton(
            card, text=button_text, font=FONTS["button"],
            width=160, command=command,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"]
        ).pack(side="right", padx=15, pady=12)

    def _magisk_patch(self):
        """Patch a boot image with Magisk."""
        project = self.app.current_project
        if not project:
            self.app.console_print("[ERROR] No project selected.\n")
            return

        project_dir = os.path.join(self.app.localdir, project)

        # Find boot images
        boot_files = []
        try:
            from src.utils import gettype
            for f in os.listdir(project_dir):
                fpath = os.path.join(project_dir, f)
                if os.path.isdir(fpath):
                    continue
                try:
                    if gettype(fpath) in ['boot', 'vendor_boot']:
                        boot_files.append(f)
                except Exception:
                    pass
        except ImportError:
            self.app.console_print("[ERROR] Cannot import detection functions.\n")
            return

        if not boot_files:
            self.app.console_print("No boot images found in project directory.\n")
            return

        # Select boot image
        if len(boot_files) == 1:
            boot_file = boot_files[0]
        else:
            # Show selection dialog
            from gui.widgets.dialogs import TextInputDialog
            options_text = "\n".join(f"[{i+1}] {f}" for i, f in enumerate(boot_files))
            dialog = TextInputDialog(
                self.app, title="Select Boot Image",
                prompt=f"Select image:\n{options_text}\nEnter number:",
                default="1"
            )
            if dialog.result is None:
                return
            try:
                idx = int(dialog.result) - 1
                boot_file = boot_files[idx]
            except (ValueError, IndexError):
                self.app.console_print("[ERROR] Invalid selection.\n")
                return

        # Select Magisk APK
        magisk_path = filedialog.askopenfilename(
            title="Select Magisk APK",
            filetypes=[("APK files", "*.apk"), ("All files", "*.*")]
        )
        if not magisk_path:
            return

        def _worker():
            import shutil
            from src.Magisk import Magisk_patch
            boot_path = os.path.join(project_dir, boot_file)
            self.app.console_print(f"\nPatching {boot_file} with Magisk...\n")
            try:
                patch = Magisk_patch(boot_path, '', MAGISAPK=magisk_path)
                patch.auto_patch()
                new_boot = os.path.join(self.app.localdir, 'new-boot.img')
                if os.path.exists(new_boot):
                    out = os.path.join(project_dir, "boot_patched.img")
                    shutil.move(new_boot, out)
                    self.app.console_print(f"Patched successfully: {out}\n")
                else:
                    self.app.console_print("[ERROR] Patch failed.\n")
            except Exception as e:
                self.app.console_print(f"[ERROR] {e}\n")

        self.run_task(_worker)

    def _disable_avb(self):
        """Disable AVB in fstab files."""
        project = self.app.current_project
        if not project:
            return

        dialog = ConfirmDialog(
            self.app, title="Disable AVB",
            message="Disable AVB verification in all fstab files?"
        )
        if not dialog.result:
            return

        project_dir = os.path.join(self.app.localdir, project)

        def _worker():
            count = 0
            for root, dirs, files in os.walk(project_dir):
                for f in files:
                    if f.startswith("fstab."):
                        fpath = os.path.join(root, f)
                        self.app.console_print(f"Processing: {fpath}\n")
                        try:
                            import run as run_module
                            run_module.Tool.dis_avb(fpath)
                            count += 1
                        except Exception as e:
                            self.app.console_print(f"[ERROR] {f}: {e}\n")
            self.app.console_print(f"\nProcessed {count} fstab files.\n")

        self.run_task(_worker)

    def _decompile_apk_jar(self):
        """Decompile APK/JAR files in project folder using apktool."""
        project = self.app.current_project
        if not project:
            self.app.console_print("[ERROR] No project selected.\n")
            return

        project_dir = os.path.join(self.app.localdir, project)

        # Scan for APK/JAR files recursively
        found_files = []
        for root, dirs, files in os.walk(project_dir):
            for f in files:
                if f.lower().endswith(('.apk', '.jar')):
                    rel = os.path.relpath(os.path.join(root, f), project_dir)
                    found_files.append(rel)

        if not found_files:
            self.app.console_print("No APK/JAR files found in project folder.\n")
            return

        found_files.sort()

        # Let user select which files to decompile
        dialog = ChecklistDialog(
            self.app, title="APK/JAR Decompiler",
            prompt=f"Found {len(found_files)} file(s). Select files to decompile:",
            items=found_files
        )
        if not dialog.result:
            return

        selected = dialog.result

        def _worker():
            import shutil
            import subprocess

            # Check java availability
            try:
                subprocess.run(
                    ["java", "-version"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name != 'posix' else 0
                )
            except FileNotFoundError:
                self.app.console_print("[ERROR] Java not found. Please install Java (JDK/JRE) and add it to PATH.\n")
                return

            # Locate apktool.jar
            apktool_jar = os.path.join(self.app.localdir, "bin", "apktool.jar")
            if not os.path.isfile(apktool_jar):
                # Try to find apktool on PATH
                apktool_on_path = shutil.which("apktool")
                if apktool_on_path:
                    apktool_cmd_base = [apktool_on_path]
                else:
                    self.app.console_print(
                        "[ERROR] apktool not found.\n"
                        "Please place apktool.jar in the bin/ folder or install apktool on PATH.\n"
                        "Download: https://apktool.org/\n"
                    )
                    return
            else:
                apktool_cmd_base = ["java", "-jar", apktool_jar]

            conf = subprocess.CREATE_NO_WINDOW if os.name != 'posix' else 0
            success = 0
            failed = 0

            for rel_path in selected:
                src_path = os.path.join(project_dir, rel_path)
                if not os.path.isfile(src_path):
                    self.app.console_print(f"[WARN] File not found: {rel_path}\n")
                    failed += 1
                    continue

                # Output to same directory with _decompiled suffix
                base_name = os.path.splitext(os.path.basename(rel_path))[0]
                out_dir = os.path.join(os.path.dirname(src_path), base_name + "_decompiled")

                self.app.console_print(f"\nDecompiling: {rel_path}\n")

                cmd = apktool_cmd_base + ["d", src_path, "-o", out_dir, "-f"]

                try:
                    proc = subprocess.Popen(
                        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                        creationflags=conf
                    )
                    for line in iter(proc.stdout.readline, b""):
                        try:
                            text = line.decode("utf-8").strip()
                        except (UnicodeDecodeError, Exception):
                            text = line.decode("gbk", errors="replace").strip()
                        if text:
                            self.app.console_print(text + "\n")
                    proc.wait()

                    if proc.returncode == 0:
                        self.app.console_print(f"Done: {rel_path} -> {os.path.relpath(out_dir, project_dir)}\n")
                        success += 1
                    else:
                        self.app.console_print(f"[ERROR] apktool returned code {proc.returncode} for {rel_path}\n")
                        failed += 1
                except Exception as e:
                    self.app.console_print(f"[ERROR] {rel_path}: {e}\n")
                    failed += 1

            self.app.console_print(f"\nDecompile finished: {success} succeeded, {failed} failed.\n")

        self.run_task(_worker)

    def _deodex(self):
        """Deodex .vdex files in the project directory."""
        project = self.app.current_project
        if not project:
            self.app.console_print("[ERROR] No project selected.\n")
            return

        project_dir = os.path.join(self.app.localdir, project)

        # Scan for .vdex files
        from src.deodex import find_vdex_files
        vdex_files = find_vdex_files(project_dir)
        if not vdex_files:
            self.app.console_print("No .vdex files found in project folder.\n")
            return

        rel_files = [os.path.relpath(f, project_dir) for f in vdex_files]

        dialog = ChecklistDialog(
            self.app, title="Deodex (vdexExtractor)",
            prompt=f"Found {len(rel_files)} .vdex file(s). Select files to deodex:",
            items=rel_files
        )
        if not dialog.result:
            return

        selected = dialog.result

        # Ask for output directory (default: project_dir/deodexed)
        out_dir = os.path.join(project_dir, "deodexed")

        def _worker():
            from src.deodex import deodex_files

            abs_files = [os.path.join(project_dir, rel) for rel in selected]
            self.app.console_print(f"\nDeodexing {len(selected)} file(s)...\n")
            deodex_files(
                vdex_files=abs_files,
                output_dir=out_dir,
                keep_tmp=False,
                log_func=self.app.console_print
            )

        self.run_task(_worker)

    def _clean_odex_artifacts(self):
        """Remove all .dex, .vdex, .oat files from the project directory."""
        project = self.app.current_project
        if not project:
            self.app.console_print("[ERROR] No project selected.\n")
            return

        project_dir = os.path.join(self.app.localdir, project)

        # Scan for files
        found = []
        for root, dirs, files in os.walk(project_dir):
            for f in files:
                if f.lower().endswith(('.dex', '.vdex', '.oat')):
                    found.append(os.path.relpath(os.path.join(root, f), project_dir))

        if not found:
            self.app.console_print("No .dex/.vdex/.oat files found in project folder.\n")
            return

        found.sort()

        dialog = ChecklistDialog(
            self.app, title="Clean Odex Artifacts",
            prompt=f"Found {len(found)} file(s). Select files to delete:",
            items=found
        )
        if not dialog.result:
            return

        selected = dialog.result

        dialog2 = ConfirmDialog(
            self.app, title="Confirm Deletion",
            message=f"Delete {len(selected)} file(s)? This cannot be undone."
        )
        if not dialog2.result:
            return

        def _worker():
            deleted = 0
            for rel in selected:
                fpath = os.path.join(project_dir, rel)
                try:
                    os.remove(fpath)
                    self.app.console_print(f"Deleted: {rel}\n")
                    deleted += 1
                except Exception as e:
                    self.app.console_print(f"[ERROR] {rel}: {e}\n")
            self.app.console_print(f"\nDeleted {deleted}/{len(selected)} file(s).\n")

        self.run_task(_worker)

    def _disable_encryption(self):
        """Disable data encryption in fstab files."""
        project = self.app.current_project
        if not project:
            return

        dialog = ConfirmDialog(
            self.app, title="Disable Encryption",
            message="Disable data encryption in all fstab files?"
        )
        if not dialog.result:
            return

        project_dir = os.path.join(self.app.localdir, project)

        def _worker():
            count = 0
            for root, dirs, files in os.walk(project_dir):
                for f in files:
                    if f.startswith("fstab."):
                        fpath = os.path.join(root, f)
                        self.app.console_print(f"Processing: {fpath}\n")
                        try:
                            import run as run_module
                            run_module.Tool.dis_data_encryption(fpath)
                            count += 1
                        except Exception as e:
                            self.app.console_print(f"[ERROR] {f}: {e}\n")
            self.app.console_print(f"\nProcessed {count} fstab files.\n")

        self.run_task(_worker)
