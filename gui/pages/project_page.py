"""
TIK5 GUI Project Page - Hub with buttons for unpack/pack/plugins/tools.
"""
import os
import customtkinter as ctk
from gui.pages.base_page import BasePage
from gui.theme import FONTS, COLORS


class ProjectPage(BasePage):
    """Project hub page with navigation to sub-operations."""

    def __init__(self, master, app, **kwargs):
        super().__init__(master, app, title="Project", **kwargs)

        # Header (updated dynamically)
        self._header_frame = ctk.CTkFrame(self, fg_color="transparent", height=50)
        self._header_frame.pack(fill="x", padx=20, pady=(15, 5))

        self._back_btn = ctk.CTkButton(
            self._header_frame, text="< Back", font=FONTS["body"],
            width=70, command=self._go_home,
            fg_color="transparent", hover_color=COLORS["bg_card"],
            text_color=COLORS["text_secondary"]
        )
        self._back_btn.pack(side="left")

        self._title_label = ctk.CTkLabel(
            self._header_frame, text="Project",
            font=FONTS["heading"],
            text_color=COLORS["text_primary"]
        )
        self._title_label.pack(side="left", padx=15)

        self._status_label = ctk.CTkLabel(
            self._header_frame, text="",
            font=FONTS["small"],
            text_color=COLORS["text_muted"]
        )
        self._status_label.pack(side="left")

        # Button grid
        self._grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._grid_frame.pack(fill="both", expand=True, padx=20, pady=10)

        buttons = [
            ("Unpack", "Unpack partition images", "unpack", COLORS["accent"]),
            ("Pack", "Pack partition images", "pack", "#2196f3"),
            ("Plugins", "Manage and run plugins", "plugin", "#9c27b0"),
            ("Pack ROM", "Create flashable ROM", "pack_rom", "#ff9800"),
            ("Tools", "Magisk, AVB, encryption", "tools", "#f44336"),
            ("Download", "Download ROM files", "download", "#4caf50"),
        ]

        for i, (text, desc, page_name, color) in enumerate(buttons):
            row = i // 3
            col = i % 3
            self._create_nav_button(
                self._grid_frame, text, desc, page_name, color, row, col
            )
            self._grid_frame.grid_columnconfigure(col, weight=1)
        self._grid_frame.grid_rowconfigure(0, weight=1)
        self._grid_frame.grid_rowconfigure(1, weight=1)

    def _create_nav_button(self, parent, text, description, page_name, color, row, col):
        """Create a large navigation button."""
        frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=12, cursor="hand2")
        frame.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        indicator = ctk.CTkFrame(frame, width=50, height=4, fg_color=color, corner_radius=2)
        indicator.pack(pady=(15, 10))

        title = ctk.CTkLabel(frame, text=text, font=FONTS["subheading"],
                             text_color=COLORS["text_primary"])
        title.pack(pady=(5, 3))

        desc = ctk.CTkLabel(frame, text=description, font=FONTS["small"],
                            text_color=COLORS["text_muted"])
        desc.pack(pady=(0, 15))

        for w in [frame, indicator, title, desc]:
            w.bind("<Button-1>", lambda e, p=page_name: self._navigate(p))
            w.bind("<Enter>", lambda e, f=frame: f.configure(fg_color=COLORS["bg_card_hover"]))
            w.bind("<Leave>", lambda e, f=frame: f.configure(fg_color=COLORS["bg_card"]))

    def on_show(self):
        project = self.app.current_project
        if project:
            self._title_label.configure(text=f"Project: {project}")
            project_path = os.path.join(self.app.localdir, project)
            if os.path.exists(os.path.join(project_path, "config")):
                self._status_label.configure(text="Configured")
            else:
                self._status_label.configure(text="(Incomplete)", text_color=COLORS["warning"])

    def _navigate(self, page_name):
        self.app.show_page(page_name)

    def _go_home(self):
        self.app.set_current_project(None)
        self.app.show_page("home")
