"""
TIK5 GUI Progress Bar Widget.
"""
import customtkinter as ctk
from gui.theme import FONTS, COLORS


class ProgressWidget(ctk.CTkFrame):
    """Progress bar with label showing current operation."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self._label = ctk.CTkLabel(
            self, text="", font=FONTS["small"],
            text_color=COLORS["text_secondary"]
        )
        self._label.pack(fill="x", padx=10)

        self._bar = ctk.CTkProgressBar(
            self, height=8, corner_radius=4,
            progress_color=COLORS["accent"]
        )
        self._bar.pack(fill="x", padx=10, pady=(2, 5))
        self._bar.set(0)
        self.hide()

    def show(self):
        self.pack(fill="x")

    def hide(self):
        self.pack_forget()

    def set_progress(self, value, description=""):
        """Set progress value (0.0 to 1.0) and description."""
        if not self.winfo_ismapped():
            self.show()
        self._bar.set(value)
        if description:
            self._label.configure(text=description)

    def set_indeterminate(self, description=""):
        """Show indeterminate progress."""
        if not self.winfo_ismapped():
            self.show()
        self._bar.set(0.5)
        if description:
            self._label.configure(text=description)

    def complete(self, description=""):
        """Show completion."""
        self._bar.set(1.0)
        if description:
            self._label.configure(text=description)
        self.after(2000, self.hide)
