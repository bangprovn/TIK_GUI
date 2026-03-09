"""
TIK5 GUI Base Page - Base class for all pages.
"""
import customtkinter as ctk
from gui.theme import FONTS, COLORS


class BasePage(ctk.CTkFrame):
    """Base class for all GUI pages."""

    def __init__(self, master, app, title="", **kwargs):
        super().__init__(master, fg_color=COLORS["bg_content"], **kwargs)
        self.app = app
        self.page_title = title

    def on_show(self):
        """Called when this page becomes visible. Override to refresh data."""
        pass

    def on_hide(self):
        """Called when this page is hidden. Override for cleanup."""
        pass

    def run_task(self, func, *args, **kwargs):
        """Convenience: run a task via the app's adapter."""
        return self.app.adapter.run_task(func, *args, **kwargs)

    def create_header(self, text=None):
        """Create a standard page header."""
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header.pack(fill="x", padx=20, pady=(15, 10))

        label = ctk.CTkLabel(
            header, text=text or self.page_title,
            font=FONTS["heading"],
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        label.pack(side="left")
        return header

    def create_action_bar(self, parent=None):
        """Create a horizontal bar for action buttons."""
        bar = ctk.CTkFrame(parent or self, fg_color="transparent", height=40)
        bar.pack(fill="x", padx=20, pady=5)
        return bar

    def create_scrollable(self, parent=None):
        """Create a scrollable frame."""
        frame = ctk.CTkScrollableFrame(
            parent or self,
            fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
        )
        frame.pack(fill="both", expand=True, padx=15, pady=5)
        return frame
