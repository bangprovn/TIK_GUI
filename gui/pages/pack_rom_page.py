"""
TIK5 GUI Pack ROM Page - Pack directly or hybrid ROM.
"""
import os
import customtkinter as ctk
from gui.pages.base_page import BasePage
from gui.theme import FONTS, COLORS
from gui.widgets.dialogs import TextInputDialog


class PackRomPage(BasePage):
    """Pack ROM page with direct and hybrid options."""

    def __init__(self, master, app, **kwargs):
        super().__init__(master, app, title="Pack ROM", **kwargs)

        header = self.create_header("Pack ROM")
        ctk.CTkButton(
            header, text="< Back", font=FONTS["body"],
            width=70, command=lambda: app.show_page("project"),
            fg_color="transparent", hover_color=COLORS["bg_card"],
            text_color=COLORS["text_secondary"]
        ).pack(side="right")

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=10)

        # Pack Directly
        card1 = ctk.CTkFrame(content, fg_color=COLORS["bg_card"], corner_radius=10)
        card1.pack(fill="x", pady=8)

        info1 = ctk.CTkFrame(card1, fg_color="transparent")
        info1.pack(side="left", fill="both", expand=True, padx=15, pady=12)

        ctk.CTkLabel(info1, text="Pack Directly", font=FONTS["subheading"],
                     text_color=COLORS["text_primary"], anchor="w").pack(fill="x")
        ctk.CTkLabel(info1, text="Create ZIP from TI_out directory with ROM files",
                     font=FONTS["small"], text_color=COLORS["text_muted"],
                     anchor="w").pack(fill="x")

        ctk.CTkButton(
            card1, text="Pack Direct", font=FONTS["button"],
            width=140, command=self._pack_direct,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"]
        ).pack(side="right", padx=15, pady=12)

        # Pack Hybrid
        card2 = ctk.CTkFrame(content, fg_color=COLORS["bg_card"], corner_radius=10)
        card2.pack(fill="x", pady=8)

        info2 = ctk.CTkFrame(card2, fg_color="transparent")
        info2.pack(side="left", fill="both", expand=True, padx=15, pady=12)

        ctk.CTkLabel(info2, text="Pack Hybrid ROM", font=FONTS["subheading"],
                     text_color=COLORS["text_primary"], anchor="w").pack(fill="x")
        ctk.CTkLabel(info2, text="Create flashable OTA with device restrictions",
                     font=FONTS["small"], text_color=COLORS["text_muted"],
                     anchor="w").pack(fill="x")

        ctk.CTkButton(
            card2, text="Pack Hybrid", font=FONTS["button"],
            width=140, command=self._pack_hybrid,
            fg_color="#ff9800", hover_color="#ffa726"
        ).pack(side="right", padx=15, pady=12)

    def _pack_direct(self):
        """Pack ROM directly."""
        project = self.app.current_project
        if not project:
            return

        project_dir = os.path.join(self.app.localdir, project)

        def _worker():
            import shutil
            import run as run_module

            self.app.console_print("Preparing for packing...\n")

            ti_out = os.path.join(project_dir, 'TI_out')
            if not os.path.exists(ti_out):
                os.makedirs(ti_out)

            for v in ['firmware-update', 'META-INF', 'exaid.img', 'dynamic_partitions_op_list']:
                src = os.path.join(project_dir, v)
                dst = os.path.join(ti_out, v)
                if os.path.isdir(src) and not os.path.isdir(dst):
                    shutil.copytree(src, dst)
                elif os.path.isfile(src) and not os.path.isfile(dst):
                    shutil.copy(src, ti_out)

            for root, dirs, files in os.walk(project_dir):
                for f in files:
                    if f.endswith('.br') or f.endswith('.dat') or f.endswith('.list'):
                        dst = os.path.join(ti_out, f)
                        if not os.path.isfile(dst) and os.access(os.path.join(project_dir, f), os.F_OK):
                            shutil.copy(os.path.join(project_dir, f), ti_out)

            run_module.zip_file(
                os.path.basename(project_dir) + ".zip",
                ti_out,
                project_dir + os.sep,
                self.app.localdir + os.sep
            )
            self.app.console_print("Pack ROM complete!\n")

        self.run_task(_worker)

    def _pack_hybrid(self):
        """Pack hybrid ROM."""
        project = self.app.current_project
        if not project:
            return

        dialog = TextInputDialog(
            self.app, title="Device Code",
            prompt="Enter device code for hybrid ROM:"
        )
        if not dialog.result:
            return

        device_code = dialog.result
        project_dir = os.path.join(self.app.localdir, project)

        def _worker():
            import run as run_module
            from src import utils

            self.app.console_print(f"Packing hybrid ROM for device: {device_code}\n")
            ti_out = os.path.join(project_dir, 'TI_out') + os.sep
            binner = os.path.join(self.app.localdir, 'bin')
            try:
                utils.dbkxyt(ti_out, device_code, os.path.join(binner, 'extra_flash.zip'))
                run_module.zip_file(
                    os.path.basename(project_dir) + ".zip",
                    os.path.join(project_dir, 'TI_out'),
                    project_dir + os.sep,
                    self.app.localdir + os.sep
                )
                self.app.console_print("Hybrid ROM pack complete!\n")
            except Exception as e:
                self.app.console_print(f"[ERROR] {e}\n")

        self.run_task(_worker)
