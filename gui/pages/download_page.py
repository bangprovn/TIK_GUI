"""
TIK5 GUI Download Page - ROM download with URL input + progress.
"""
import os
import customtkinter as ctk
from gui.pages.base_page import BasePage
from gui.theme import FONTS, COLORS


class DownloadPage(BasePage):
    """Download ROM files page."""

    def __init__(self, master, app, **kwargs):
        super().__init__(master, app, title="Download", **kwargs)

        header = self.create_header("Download ROM")
        ctk.CTkButton(
            header, text="< Back", font=FONTS["body"],
            width=70, command=lambda: app.show_page("project"),
            fg_color="transparent", hover_color=COLORS["bg_card"],
            text_color=COLORS["text_secondary"]
        ).pack(side="right")

        # URL input
        url_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=10)
        url_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            url_frame, text="Download URL:", font=FONTS["body"],
            text_color=COLORS["text_primary"]
        ).pack(padx=15, pady=(10, 5), anchor="w")

        input_row = ctk.CTkFrame(url_frame, fg_color="transparent")
        input_row.pack(fill="x", padx=15, pady=(0, 10))

        self._url_entry = ctk.CTkEntry(
            input_row, font=FONTS["body"],
            placeholder_text="Enter ROM download URL..."
        )
        self._url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self._url_entry.bind("<Return>", lambda e: self._start_download())

        self._download_btn = ctk.CTkButton(
            input_row, text="Download", font=FONTS["button"],
            width=120, command=self._start_download,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"]
        )
        self._download_btn.pack(side="right")

        # Info
        ctk.CTkLabel(
            self, text="Downloads will be saved to the TIK root directory.",
            font=FONTS["small"],
            text_color=COLORS["text_muted"]
        ).pack(padx=25, pady=5, anchor="w")

    def _start_download(self):
        """Start ROM download."""
        url = self._url_entry.get().strip()
        if not url:
            self.app.console_print("Please enter a URL.\n")
            return

        def _worker():
            from src import downloader
            self.app.console_print(f"Downloading: {url}\n")
            try:
                downloader.download([url], self.app.localdir)
                self.app.console_print("Download complete!\n")
            except Exception as e:
                self.app.console_print(f"[ERROR] Download failed: {e}\n")

        self._download_btn.configure(state="disabled", text="Downloading...")

        def _on_done(r=None):
            self.app.after(0, lambda: self._download_btn.configure(
                state="normal", text="Download"))

        self.run_task(_worker, callback=_on_done)
