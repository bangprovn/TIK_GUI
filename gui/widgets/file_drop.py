"""
TIK5 GUI File Drop Zone Widget.
"""
import customtkinter as ctk
from gui.theme import FONTS, COLORS
from tkinter import filedialog


class FileDropZone(ctk.CTkFrame):
    """Drag-and-drop zone for ROM files. Falls back to file dialog on click."""

    def __init__(self, master, on_file_selected=None,
                 hint_text="Drag & drop ROM file here or click to browse",
                 filetypes=None, **kwargs):
        super().__init__(
            master, fg_color=COLORS["bg_card"],
            corner_radius=10, cursor="hand2",
            border_width=2, border_color=COLORS["border"],
            **kwargs
        )
        self._on_file_selected = on_file_selected
        self._filetypes = filetypes or [
            ("ROM files", "*.zip"),
            ("All files", "*.*"),
        ]
        self.configure(height=100)

        self._icon_label = ctk.CTkLabel(
            self, text="[+]",
            font=("Segoe UI", 28),
            text_color=COLORS["text_muted"]
        )
        self._icon_label.pack(pady=(15, 5))

        self._hint_label = ctk.CTkLabel(
            self, text=hint_text,
            font=FONTS["small"],
            text_color=COLORS["text_muted"]
        )
        self._hint_label.pack(pady=(0, 15))

        # Click to browse
        for widget in [self, self._icon_label, self._hint_label]:
            widget.bind("<Button-1>", self._browse)

        # Try to setup drag-and-drop if tkinterdnd2 is available
        self._setup_dnd()

    def _setup_dnd(self):
        """Try to setup drag-and-drop support."""
        try:
            self.drop_target_register("DND_Files")
            self.dnd_bind("<<Drop>>", self._on_drop)
            self.dnd_bind("<<DragEnter>>", self._on_drag_enter)
            self.dnd_bind("<<DragLeave>>", self._on_drag_leave)
        except (AttributeError, Exception):
            pass

    def _on_drop(self, event):
        """Handle file drop."""
        file_path = event.data
        if file_path.startswith("{") and file_path.endswith("}"):
            file_path = file_path[1:-1]
        if self._on_file_selected:
            self._on_file_selected(file_path)

    def _on_drag_enter(self, event):
        self.configure(border_color=COLORS["accent"])

    def _on_drag_leave(self, event):
        self.configure(border_color=COLORS["border"])

    def _browse(self, event=None):
        """Open file dialog."""
        file_path = filedialog.askopenfilename(filetypes=self._filetypes)
        if file_path and self._on_file_selected:
            self._on_file_selected(file_path)
