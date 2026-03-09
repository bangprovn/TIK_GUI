"""
TIK5 GUI App - Main window, sidebar navigation, page manager.
"""
import os
import sys
import queue
import customtkinter as ctk

from gui.theme import setup_appearance, FONTS, COLORS
from gui.adapter import GUIAdapter
from gui.widgets.console import ConsoleWidget
from gui.widgets.progress import ProgressWidget
from gui.widgets.dialogs import InputPromptBar

from gui.pages.main_page import MainPage
from gui.pages.project_page import ProjectPage
from gui.pages.unpack_page import UnpackPage
from gui.pages.pack_page import PackPage
from gui.pages.settings_page import SettingsPage
from gui.pages.plugin_page import PluginPage
from gui.pages.tools_page import ToolsPage
from gui.pages.download_page import DownloadPage
from gui.pages.pack_rom_page import PackRomPage


class TIKApp(ctk.CTk):
    """Main TIK5 GUI Application."""

    WINDOW_TITLE = "TIK5 - Android ROM Tool"
    WINDOW_SIZE = "1100x720"
    MIN_SIZE = (900, 600)

    # Sidebar items: (key, label, icon_text)
    STATIC_NAV = [
        ("home", "Home", "H"),
        ("settings", "Settings", "S"),
    ]

    PROJECT_NAV = [
        ("project", "Project", "P"),
        ("unpack", "Unpack", "U"),
        ("pack", "Pack", "K"),
        ("plugin", "Plugins", "L"),
        ("pack_rom", "Pack ROM", "R"),
        ("tools", "Tools", "T"),
        ("download", "Download", "D"),
    ]

    def __init__(self):
        setup_appearance()
        super().__init__()

        self.title(self.WINDOW_TITLE)
        self.geometry(self.WINDOW_SIZE)
        self.minsize(*self.MIN_SIZE)

        # State
        self.localdir = os.getcwd()
        self.current_project = None
        self._current_page = None

        # Adapter for I/O redirection
        self.adapter = GUIAdapter()

        # Layout: sidebar + main area
        self._build_layout()

        # Create all pages
        self._pages = {}
        self._create_pages()

        # Start polling output queue
        self._poll_output()

        # Show home page
        self.show_page("home")

    def _build_layout(self):
        """Build the main window layout."""
        # Root grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self._sidebar = ctk.CTkFrame(
            self, width=180, corner_radius=0,
            fg_color=COLORS["bg_sidebar"]
        )
        self._sidebar.grid(row=0, column=0, sticky="nsw")
        self._sidebar.grid_propagate(False)

        # Sidebar header
        logo_frame = ctk.CTkFrame(self._sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=10, pady=(15, 5))

        ctk.CTkLabel(
            logo_frame, text="TIK5",
            font=("Segoe UI", 24, "bold"),
            text_color=COLORS["accent"]
        ).pack()
        ctk.CTkLabel(
            logo_frame, text="Android ROM Tool",
            font=FONTS["small"],
            text_color=COLORS["text_muted"]
        ).pack()

        # Separator
        ctk.CTkFrame(
            self._sidebar, height=1,
            fg_color=COLORS["border"]
        ).pack(fill="x", padx=15, pady=10)

        # Navigation buttons container
        self._nav_frame = ctk.CTkFrame(self._sidebar, fg_color="transparent")
        self._nav_frame.pack(fill="both", expand=True, padx=5)

        self._nav_buttons = {}
        self._build_nav()

        # Right side: content + console
        self._right = ctk.CTkFrame(self, fg_color=COLORS["bg_content"], corner_radius=0)
        self._right.grid(row=0, column=1, sticky="nsew")
        self._right.grid_rowconfigure(0, weight=3)
        self._right.grid_rowconfigure(1, weight=0)
        self._right.grid_rowconfigure(2, weight=1)
        self._right.grid_columnconfigure(0, weight=1)

        # Content area (pages go here)
        self._content = ctk.CTkFrame(self._right, fg_color=COLORS["bg_content"], corner_radius=0)
        self._content.grid(row=0, column=0, sticky="nsew")

        # Progress bar
        self._progress = ProgressWidget(self._right)
        self._progress.grid(row=1, column=0, sticky="ew")

        # Console area
        self._console = ConsoleWidget(self._right, height=180)
        self._console.grid(row=2, column=0, sticky="nsew", padx=5, pady=(0, 5))

        # Input prompt bar (hidden by default)
        self._input_bar = InputPromptBar(
            self._right, on_submit=self._on_input_submit
        )

    def _build_nav(self):
        """Build sidebar navigation buttons."""
        for widget in self._nav_frame.winfo_children():
            widget.destroy()
        self._nav_buttons.clear()

        # Static items
        for key, label, icon in self.STATIC_NAV:
            self._add_nav_button(key, label, icon)

        # Project items (only shown when project is selected)
        if self.current_project:
            ctk.CTkFrame(
                self._nav_frame, height=1,
                fg_color=COLORS["border"]
            ).pack(fill="x", padx=10, pady=8)

            proj_label = ctk.CTkLabel(
                self._nav_frame,
                text=f"  {self.current_project[:18]}",
                font=FONTS["small"],
                text_color=COLORS["text_muted"],
                anchor="w"
            )
            proj_label.pack(fill="x", padx=5)

            for key, label, icon in self.PROJECT_NAV:
                self._add_nav_button(key, label, icon)

    def _add_nav_button(self, key, label, icon_text):
        """Add a navigation button to sidebar."""
        btn = ctk.CTkButton(
            self._nav_frame,
            text=f"  {label}",
            font=FONTS["sidebar"],
            anchor="w",
            height=36,
            corner_radius=8,
            fg_color="transparent",
            hover_color=COLORS["bg_card"],
            text_color=COLORS["text_secondary"],
            command=lambda k=key: self.show_page(k),
        )
        btn.pack(fill="x", padx=5, pady=2)
        self._nav_buttons[key] = btn

    def _create_pages(self):
        """Create all page instances."""
        page_classes = {
            "home": MainPage,
            "project": ProjectPage,
            "unpack": UnpackPage,
            "pack": PackPage,
            "settings": SettingsPage,
            "plugin": PluginPage,
            "tools": ToolsPage,
            "download": DownloadPage,
            "pack_rom": PackRomPage,
        }

        for key, cls in page_classes.items():
            page = cls(self._content, self)
            page.place(relx=0, rely=0, relwidth=1, relheight=1)
            self._pages[key] = page

    def show_page(self, page_name):
        """Switch to the given page."""
        if page_name not in self._pages:
            return

        # Hide current page
        if self._current_page and self._current_page in self._pages:
            self._pages[self._current_page].on_hide()

        # Show new page
        self._current_page = page_name
        page = self._pages[page_name]
        page.tkraise()
        page.on_show()

        # Update nav button highlighting
        for key, btn in self._nav_buttons.items():
            if key == page_name:
                btn.configure(
                    fg_color=COLORS["accent"],
                    text_color=COLORS["text_primary"],
                    font=FONTS["sidebar_active"]
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COLORS["text_secondary"],
                    font=FONTS["sidebar"]
                )

    def set_current_project(self, project_name):
        """Set or clear the current project."""
        self.current_project = project_name
        self._build_nav()
        if self._current_page:
            # Re-highlight current page
            for key, btn in self._nav_buttons.items():
                if key == self._current_page:
                    btn.configure(
                        fg_color=COLORS["accent"],
                        text_color=COLORS["text_primary"],
                        font=FONTS["sidebar_active"]
                    )

    def console_print(self, text):
        """Thread-safe print to console."""
        self.adapter.output_queue.put(("output", text))

    def _on_input_submit(self, value):
        """Handle input from the input prompt bar."""
        self._input_bar.hide()
        self.console_print(f"> {value}\n")
        self.adapter.provide_input(value)

    def _poll_output(self):
        """Poll the adapter output queue and update GUI."""
        try:
            while True:
                msg_type, data = self.adapter.output_queue.get_nowait()

                if msg_type == "output":
                    self._console.append(str(data))
                elif msg_type == "input_request":
                    self._input_bar.show(str(data))
                elif msg_type == "clear":
                    self._console.clear()
                elif msg_type == "progress":
                    value, desc = data
                    self._progress.set_progress(value, desc)
                elif msg_type == "progress_done":
                    self._progress.complete(str(data))
                elif msg_type == "task_done":
                    self._progress.complete("Done")
                elif msg_type == "task_error":
                    self._progress.hide()

        except queue.Empty:
            pass

        self.after(50, self._poll_output)

    def start(self):
        """Start the application."""
        # Attach adapter for I/O redirection
        self.adapter.patch_rich()
        self.adapter.attach()
        self.adapter.patch_cls()

        self.mainloop()

        # Cleanup
        self.adapter.detach()
