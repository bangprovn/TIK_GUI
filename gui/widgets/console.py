"""
TIK5 GUI Console Widget - Scrollable text output with ANSI color support.
"""
import re
import customtkinter as ctk
from gui.theme import FONTS, COLORS, ANSI_COLORS, TAG_COLORS, ANSI_BG_COLORS, TAG_BG_COLORS
import tkinter as tk


class ConsoleWidget(ctk.CTkFrame):
    """Scrollable console output with ANSI color parsing."""

    # Regex to match ANSI escape sequences
    ANSI_RE = re.compile(r'\033\[([0-9;]*)m')

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.configure(fg_color=COLORS["bg_console"], corner_radius=8)

        # Header with label and clear button
        self._header = ctk.CTkFrame(self, fg_color="transparent", height=30)
        self._header.pack(fill="x", padx=5, pady=(5, 0))

        self._label = ctk.CTkLabel(
            self._header, text="Console",
            font=FONTS["small"], text_color=COLORS["text_muted"]
        )
        self._label.pack(side="left", padx=5)

        self._clear_btn = ctk.CTkButton(
            self._header, text="Clear", width=50, height=22,
            font=FONTS["small"], command=self.clear,
            fg_color="transparent", hover_color=COLORS["bg_card"],
            text_color=COLORS["text_secondary"]
        )
        self._clear_btn.pack(side="right", padx=5)

        # Text widget (using tkinter Text inside CTk for tag support)
        self._text_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_console"], corner_radius=0)
        self._text_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        self._text = tk.Text(
            self._text_frame,
            bg=COLORS["bg_console"],
            fg=COLORS["text_primary"],
            font=FONTS["console"],
            wrap="word",
            state="disabled",
            relief="flat",
            borderwidth=0,
            insertbackground=COLORS["text_primary"],
            selectbackground=COLORS["accent"],
            padx=8,
            pady=4,
        )

        self._scrollbar = ctk.CTkScrollbar(self._text_frame, command=self._text.yview)
        self._text.configure(yscrollcommand=self._scrollbar.set)

        self._scrollbar.pack(side="right", fill="y")
        self._text.pack(side="left", fill="both", expand=True)

        # Configure color tags
        for tag_name, color in TAG_COLORS.items():
            self._text.tag_configure(tag_name, foreground=color)
        for tag_name, color in TAG_BG_COLORS.items():
            self._text.tag_configure(tag_name, background=color)
        self._text.tag_configure("bold", font=(*FONTS["console"][:2], "bold"))

        # Auto-scroll flag
        self._auto_scroll = True

    def append(self, text):
        """Append text to console, parsing ANSI color codes."""
        self._text.configure(state="normal")

        segments = self._parse_ansi(text)
        for content, tags in segments:
            if content:
                self._text.insert("end", content, tuple(tags) if tags else ())

        self._text.configure(state="disabled")

        if self._auto_scroll:
            self._text.see("end")

    def _parse_ansi(self, text):
        """Parse text with ANSI codes into (content, tags) segments."""
        segments = []
        current_tags = []
        last_end = 0

        for match in self.ANSI_RE.finditer(text):
            # Text before this escape sequence
            before = text[last_end:match.start()]
            if before:
                segments.append((before, list(current_tags)))

            # Parse the escape codes
            codes = match.group(1).split(';')
            for code in codes:
                code = code.strip()
                if code == '0' or code == '':
                    current_tags = []
                elif code == '1':
                    if 'bold' not in current_tags:
                        current_tags.append('bold')
                elif code in ANSI_COLORS:
                    # Remove previous fg color
                    current_tags = [t for t in current_tags if t not in TAG_COLORS]
                    current_tags.append(ANSI_COLORS[code])
                elif code in ANSI_BG_COLORS:
                    # Remove previous bg color
                    current_tags = [t for t in current_tags if t not in TAG_BG_COLORS]
                    current_tags.append(ANSI_BG_COLORS[code])

            last_end = match.end()

        # Remaining text after last escape
        remaining = text[last_end:]
        if remaining:
            segments.append((remaining, list(current_tags)))

        return segments

    def clear(self):
        """Clear all console text."""
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")
        self._text.configure(state="disabled")

    def set_label(self, text):
        """Update the console header label."""
        self._label.configure(text=text)
