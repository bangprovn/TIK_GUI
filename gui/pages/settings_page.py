"""
TIK5 GUI Settings Page - 4 tabs matching CLI structure.
"""
import os
import sys
import json
import customtkinter as ctk
from gui.pages.base_page import BasePage
from gui.theme import FONTS, COLORS


class SettingsPage(BasePage):
    """Settings page with tabbed interface."""

    def __init__(self, master, app, **kwargs):
        super().__init__(master, app, title="Settings", **kwargs)

        self.create_header("Settings")

        # Tab view
        self._tabview = ctk.CTkTabview(
            self, fg_color=COLORS["bg_content"],
            segmented_button_fg_color=COLORS["bg_card"],
            segmented_button_selected_color=COLORS["accent"],
        )
        self._tabview.pack(fill="both", expand=True, padx=15, pady=5)

        # Create tabs
        self._tabview.add("Packaging")
        self._tabview.add("Dynamic Partition")
        self._tabview.add("Tool Settings")
        self._tabview.add("About")

        self._build_packaging_tab()
        self._build_partition_tab()
        self._build_tool_tab()
        self._build_about_tab()

    def _get_settings(self):
        """Load current settings from file."""
        setfile = os.path.join(self.app.localdir, "bin", "settings.json")
        try:
            with open(setfile, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

    def _save_setting(self, key, value):
        """Save a single setting."""
        setfile = os.path.join(self.app.localdir, "bin", "settings.json")
        try:
            with open(setfile, 'r') as f:
                data = json.load(f)
            data[key] = value
            with open(setfile, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            # Reload settings in run.py if loaded
            try:
                import run
                if hasattr(run, 'settings'):
                    run.settings.load_set()
            except ImportError:
                pass
        except Exception as e:
            self.app.console_print(f"[ERROR] Failed to save setting: {e}\n")

    def _build_packaging_tab(self):
        tab = self._tabview.tab("Packaging")
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        s = self._get_settings()

        # Brotli level
        self._brcom_var = ctk.StringVar(value=s.get("brcom", "1"))
        self._add_setting_row(scroll, "Brotli Compression Level (1-9)",
                              self._brcom_var, "slider", key="brcom",
                              slider_range=(1, 9))

        # EXT4 size
        self._diysize_var = ctk.StringVar(value="Auto" if not s.get("diysize") else "Original")
        self._add_setting_row(scroll, "EXT4 Size Handle",
                              self._diysize_var, "option",
                              options=["Auto", "Original"],
                              key="diysize",
                              transform=lambda v: "1" if v == "Original" else "")

        # Packing method
        self._pack_e2_var = ctk.StringVar(value="mke2fs" if s.get("pack_e2") == "1" else "make_ext4fs")
        self._add_setting_row(scroll, "EXT4 Packing Method",
                              self._pack_e2_var, "option",
                              options=["make_ext4fs", "mke2fs"],
                              key="pack_e2",
                              transform=lambda v: "1" if v == "mke2fs" else "0")

        # EROFS compression
        self._erofs_var = ctk.StringVar(value=s.get("erofslim", "lz4hc,8"))
        self._add_setting_row(scroll, "EROFS Compression (e.g. lz4hc,8)",
                              self._erofs_var, "entry", key="erofslim")

        # UTC timestamp
        self._utc_var = ctk.StringVar(value=s.get("utcstamp", "1230768000"))
        self._add_setting_row(scroll, "UTC Timestamp",
                              self._utc_var, "entry", key="utcstamp")

        # Pack sparse
        self._sparse_var = ctk.StringVar(value="On" if s.get("pack_sparse") == "1" else "Off")
        self._add_setting_row(scroll, "Pack as Sparse Image",
                              self._sparse_var, "option",
                              options=["Off", "On"],
                              key="pack_sparse",
                              transform=lambda v: "1" if v == "On" else "0")

        # Image format
        self._imgtype_var = ctk.StringVar(value="Selectable" if s.get("diyimgtype") == "1" else "Original")
        self._add_setting_row(scroll, "Image Format Selection",
                              self._imgtype_var, "option",
                              options=["Original", "Selectable"],
                              key="diyimgtype",
                              transform=lambda v: "1" if v == "Selectable" else "")

        # EROFS old kernel
        self._erofs_kernel_var = ctk.StringVar(value="On" if s.get("erofs_old_kernel") == "1" else "Off")
        self._add_setting_row(scroll, "EROFS Old Kernel Support",
                              self._erofs_kernel_var, "option",
                              options=["Off", "On"],
                              key="erofs_old_kernel",
                              transform=lambda v: "1" if v == "On" else "0")

    def _build_partition_tab(self):
        tab = self._tabview.tab("Dynamic Partition")
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        s = self._get_settings()

        self._group_var = ctk.StringVar(value=s.get("super_group", "qti_dynamic_partitions"))
        self._add_setting_row(scroll, "Super Group Name",
                              self._group_var, "entry", key="super_group")

        self._meta_var = ctk.StringVar(value=s.get("metadatasize", "65536"))
        self._add_setting_row(scroll, "Metadata Size",
                              self._meta_var, "entry", key="metadatasize")

        self._block_var = ctk.StringVar(value=s.get("BLOCKSIZE", "4096"))
        self._add_setting_row(scroll, "Partition Block Size",
                              self._block_var, "entry", key="BLOCKSIZE")

        self._sblock_var = ctk.StringVar(value=s.get("SBLOCKSIZE", "4096"))
        self._add_setting_row(scroll, "Super Block Size",
                              self._sblock_var, "entry", key="SBLOCKSIZE")

        self._supername_var = ctk.StringVar(value=s.get("supername", "super"))
        self._add_setting_row(scroll, "Physical Partition Name",
                              self._supername_var, "entry", key="supername")

        self._fullsuper_var = ctk.StringVar(value="On" if s.get("fullsuper") == "-F" else "Off")
        self._add_setting_row(scroll, "Force Super Image Generation",
                              self._fullsuper_var, "option",
                              options=["Off", "On"],
                              key="fullsuper",
                              transform=lambda v: "-F" if v == "On" else "")

        self._slot_var = ctk.StringVar(value="On" if s.get("autoslotsuffixing") == "-x" else "Off")
        self._add_setting_row(scroll, "Slot Suffix",
                              self._slot_var, "option",
                              options=["Off", "On"],
                              key="autoslotsuffixing",
                              transform=lambda v: "-x" if v == "On" else "")

    def _build_tool_tab(self):
        tab = self._tabview.tab("Tool Settings")
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        s = self._get_settings()

        # Banner
        self._banner_var = ctk.StringVar(value=s.get("banner", "1"))
        self._add_setting_row(scroll, "Banner Style",
                              self._banner_var, "option",
                              options=["1", "2", "3", "4", "5", "6"],
                              key="banner")

        # Online mode
        self._online_var = ctk.StringVar(value="On" if s.get("online") == "true" else "Off")
        self._add_setting_row(scroll, "Online Mode",
                              self._online_var, "option",
                              options=["Off", "On"],
                              key="online",
                              transform=lambda v: "true" if v == "On" else "false")

        # Context patcher
        self._context_var = ctk.StringVar(value="On" if s.get("context") == "true" else "Off")
        self._add_setting_row(scroll, "Context Patcher",
                              self._context_var, "option",
                              options=["Off", "On"],
                              key="context",
                              transform=lambda v: "true" if v == "On" else "false")

        # Language
        try:
            from src import languages
            langs = [l for l in dir(languages)
                     if not l.startswith("_") and not l.endswith("_") and l != "default"]
        except ImportError:
            langs = ["English"]
        self._lang_var = ctk.StringVar(value=s.get("language", "English"))
        self._add_setting_row(scroll, "Language",
                              self._lang_var, "option",
                              options=langs,
                              key="language")

        # Check Update button
        update_row = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"], corner_radius=8, height=50)
        update_row.pack(fill="x", padx=5, pady=3)
        update_row.pack_propagate(False)
        ctk.CTkLabel(
            update_row, text="Check for Updates", font=FONTS["body"],
            text_color=COLORS["text_primary"], anchor="w"
        ).pack(side="left", padx=15, fill="x", expand=True)
        ctk.CTkButton(
            update_row, text="Check Now", font=FONTS["body"],
            width=120, command=self._check_update,
            fg_color=COLORS["accent"]
        ).pack(side="right", padx=15, pady=8)

    def _build_about_tab(self):
        tab = self._tabview.tab("About")
        frame = ctk.CTkFrame(tab, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        s = self._get_settings()

        # Banner art
        try:
            from src import banner
            banner_text = banner.banner1.strip()
        except ImportError:
            banner_text = "TIK5"

        ctk.CTkLabel(
            frame, text=banner_text,
            font=("Consolas", 10),
            text_color=COLORS["error"],
            justify="left"
        ).pack(pady=(0, 15))

        info_lines = [
            ("Open-source Android ROM processing tool", COLORS["text_secondary"]),
            ("", None),
            (f"Author: ColdWindScholar", COLORS["text_primary"]),
            (f"Version: {s.get('version', 'Unknown')} Alpha Edition", COLORS["text_primary"]),
            (f"License: GNU General Public License v3.0", COLORS["text_primary"]),
            ("", None),
            ("GitHub: https://github.com/ColdWindScholar/TIK", COLORS["accent"]),
            ("", None),
            ("Thanks to:", COLORS["warning"]),
            ("Affggh, Yeliqin666, YukongA", COLORS["text_secondary"]),
        ]

        for text, color in info_lines:
            if text:
                ctk.CTkLabel(
                    frame, text=text, font=FONTS["body"],
                    text_color=color or COLORS["text_primary"]
                ).pack(anchor="w", pady=1)
            else:
                ctk.CTkFrame(frame, height=1, fg_color=COLORS["border"]).pack(fill="x", pady=5)

    def _add_setting_row(self, parent, label, var, widget_type,
                         key=None, options=None, transform=None,
                         slider_range=None):
        """Add a setting row with label and control widget."""
        row = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=8, height=50)
        row.pack(fill="x", padx=5, pady=3)
        row.pack_propagate(False)

        ctk.CTkLabel(
            row, text=label, font=FONTS["body"],
            text_color=COLORS["text_primary"], anchor="w"
        ).pack(side="left", padx=15, fill="x", expand=True)

        def _on_change(*args):
            if key:
                value = var.get()
                if transform:
                    value = transform(value)
                self._save_setting(key, value)

        if widget_type == "option":
            menu = ctk.CTkOptionMenu(
                row, values=options or [], variable=var,
                width=140, font=FONTS["body"],
                command=lambda v: _on_change()
            )
            menu.pack(side="right", padx=15, pady=8)

        elif widget_type == "entry":
            entry = ctk.CTkEntry(row, textvariable=var, width=160, font=FONTS["body"])
            entry.pack(side="right", padx=15, pady=8)
            entry.bind("<FocusOut>", lambda e: _on_change())
            entry.bind("<Return>", lambda e: _on_change())

        elif widget_type == "slider":
            min_val, max_val = slider_range or (1, 9)

            val_label = ctk.CTkLabel(
                row, text=var.get(), font=FONTS["body"],
                text_color=COLORS["accent"], width=30
            )
            val_label.pack(side="right", padx=(0, 15))

            def _slider_changed(value):
                int_val = str(int(value))
                var.set(int_val)
                val_label.configure(text=int_val)
                if key:
                    self._save_setting(key, int_val)

            slider = ctk.CTkSlider(
                row, from_=min_val, to=max_val,
                number_of_steps=max_val - min_val,
                width=140, command=_slider_changed
            )
            try:
                slider.set(int(var.get()))
            except ValueError:
                slider.set(min_val)
            slider.pack(side="right", padx=5, pady=8)

    def on_show(self):
        """Refresh settings values when page is shown."""
        s = self._get_settings()
        # Update all variables from current settings
        try:
            self._brcom_var.set(s.get("brcom", "1"))
            self._diysize_var.set("Auto" if not s.get("diysize") else "Original")
            self._pack_e2_var.set("mke2fs" if s.get("pack_e2") == "1" else "make_ext4fs")
            self._erofs_var.set(s.get("erofslim", "lz4hc,8"))
            self._utc_var.set(s.get("utcstamp", "1230768000"))
            self._sparse_var.set("On" if s.get("pack_sparse") == "1" else "Off")
            self._imgtype_var.set("Selectable" if s.get("diyimgtype") == "1" else "Original")
            self._erofs_kernel_var.set("On" if s.get("erofs_old_kernel") == "1" else "Off")
            self._group_var.set(s.get("super_group", "qti_dynamic_partitions"))
            self._meta_var.set(s.get("metadatasize", "65536"))
            self._block_var.set(s.get("BLOCKSIZE", "4096"))
            self._sblock_var.set(s.get("SBLOCKSIZE", "4096"))
            self._supername_var.set(s.get("supername", "super"))
            self._fullsuper_var.set("On" if s.get("fullsuper") == "-F" else "Off")
            self._slot_var.set("On" if s.get("autoslotsuffixing") == "-x" else "Off")
            self._banner_var.set(s.get("banner", "1"))
            self._online_var.set("On" if s.get("online") == "true" else "Off")
            self._context_var.set("On" if s.get("context") == "true" else "Off")
            self._lang_var.set(s.get("language", "English"))
        except AttributeError:
            pass

    def _check_update(self):
        """Check for updates - runs CLI upgrade() in worker thread."""
        def _worker():
            try:
                import run as run_module
                run_module.upgrade()
            except Exception as e:
                self.app.console_print(f"[ERROR] Update check failed: {e}\n")

        self.run_task(_worker)
