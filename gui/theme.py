"""
TIK5 GUI Theme - Colors, fonts, appearance settings.
"""
import customtkinter as ctk

# Appearance
DEFAULT_MODE = "dark"
DEFAULT_THEME = "blue"

# Colors (dark mode palette)
COLORS = {
    "bg_dark": "#1a1a2e",
    "bg_sidebar": "#16213e",
    "bg_content": "#1a1a2e",
    "bg_console": "#0f0f1a",
    "bg_card": "#222244",
    "bg_card_hover": "#2a2a55",
    "accent": "#0f7dff",
    "accent_hover": "#1a8cff",
    "text_primary": "#e0e0e0",
    "text_secondary": "#a0a0b0",
    "text_muted": "#666680",
    "success": "#00c853",
    "warning": "#ffc107",
    "error": "#ff5252",
    "border": "#333355",
}

# Font configurations
FONTS = {
    "title": ("Segoe UI", 20, "bold"),
    "heading": ("Segoe UI", 16, "bold"),
    "subheading": ("Segoe UI", 14, "bold"),
    "body": ("Segoe UI", 13),
    "small": ("Segoe UI", 11),
    "console": ("Consolas", 12),
    "console_small": ("Consolas", 10),
    "sidebar": ("Segoe UI", 14),
    "sidebar_active": ("Segoe UI", 14, "bold"),
    "button": ("Segoe UI", 13),
}

# ANSI color code to tag name mapping
ANSI_COLORS = {
    "30": "black",
    "31": "red",
    "32": "green",
    "33": "yellow",
    "34": "blue",
    "35": "magenta",
    "36": "cyan",
    "37": "white",
    "91": "bright_red",
    "92": "bright_green",
    "93": "bright_yellow",
    "94": "bright_blue",
    "95": "bright_magenta",
    "96": "bright_cyan",
}

# Tag colors for console widget
TAG_COLORS = {
    "black": "#333333",
    "red": "#ff5252",
    "green": "#00c853",
    "yellow": "#ffc107",
    "blue": "#448aff",
    "magenta": "#e040fb",
    "cyan": "#18ffff",
    "white": "#e0e0e0",
    "bright_red": "#ff8a80",
    "bright_green": "#69f0ae",
    "bright_yellow": "#ffff00",
    "bright_blue": "#82b1ff",
    "bright_magenta": "#ea80fc",
    "bright_cyan": "#84ffff",
}

# Background ANSI codes
ANSI_BG_COLORS = {
    "40": "bg_black",
    "41": "bg_red",
    "42": "bg_green",
    "43": "bg_yellow",
    "44": "bg_blue",
    "45": "bg_magenta",
    "46": "bg_cyan",
    "47": "bg_white",
}

TAG_BG_COLORS = {
    "bg_black": "#333333",
    "bg_red": "#ff5252",
    "bg_green": "#00c853",
    "bg_yellow": "#ffc107",
    "bg_blue": "#1565c0",
    "bg_magenta": "#e040fb",
    "bg_cyan": "#18ffff",
    "bg_white": "#e0e0e0",
}


def setup_appearance():
    """Initialize CustomTkinter appearance."""
    ctk.set_appearance_mode(DEFAULT_MODE)
    ctk.set_default_color_theme(DEFAULT_THEME)
