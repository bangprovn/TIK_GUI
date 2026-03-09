"""
TIK5 GUI Project Card Widget - Clickable card for project list.
"""
import os
import customtkinter as ctk
from gui.theme import FONTS, COLORS


class ProjectCard(ctk.CTkFrame):
    """Clickable project card showing name and basic info."""

    def __init__(self, master, project_name, project_path,
                 on_click=None, on_delete=None, **kwargs):
        super().__init__(
            master, fg_color=COLORS["bg_card"],
            corner_radius=10, cursor="hand2", **kwargs
        )
        self.project_name = project_name
        self.project_path = project_path
        self._on_click = on_click
        self._on_delete = on_delete

        self.configure(height=80)

        # Project icon/indicator
        self._indicator = ctk.CTkFrame(
            self, width=6, height=50,
            fg_color=COLORS["accent"], corner_radius=3
        )
        self._indicator.pack(side="left", padx=(10, 8), pady=15)

        # Info section
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, pady=10)

        self._name_label = ctk.CTkLabel(
            info_frame, text=project_name,
            font=FONTS["subheading"],
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        self._name_label.pack(fill="x")

        # Status info
        status = self._get_status()
        self._status_label = ctk.CTkLabel(
            info_frame, text=status,
            font=FONTS["small"],
            text_color=COLORS["text_muted"],
            anchor="w"
        )
        self._status_label.pack(fill="x")

        # Bind click events to all children
        for widget in [self, self._indicator, info_frame, self._name_label, self._status_label]:
            widget.bind("<Button-1>", self._clicked)
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)

        # Right-click for delete
        for widget in [self, info_frame, self._name_label, self._status_label]:
            widget.bind("<Button-3>", self._right_clicked)

    def _get_status(self):
        """Get project status string."""
        parts = []
        config_path = os.path.join(self.project_path, "config")
        if os.path.exists(config_path):
            parts.append("Configured")
        else:
            parts.append("Incomplete")

        ti_out = os.path.join(self.project_path, "TI_out")
        if os.path.exists(ti_out):
            parts.append("Has output")

        # Count image files
        img_count = 0
        try:
            for f in os.listdir(self.project_path):
                if f.endswith(('.img', '.br', '.dat', '.bin')):
                    img_count += 1
        except OSError:
            pass
        if img_count > 0:
            parts.append(f"{img_count} files")

        return " | ".join(parts)

    def _clicked(self, event=None):
        if self._on_click:
            self._on_click(self.project_name)

    def _right_clicked(self, event=None):
        if self._on_delete:
            self._on_delete(self.project_name)

    def _on_enter(self, event=None):
        self.configure(fg_color=COLORS["bg_card_hover"])

    def _on_leave(self, event=None):
        self.configure(fg_color=COLORS["bg_card"])
