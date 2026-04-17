"""
TIK5 GUI Pack Page - Partition list and pack execution.
Includes full Pack Super and Pack Payload dialogs matching CLI.
"""
import os
import json
import customtkinter as ctk
from gui.pages.base_page import BasePage
from gui.theme import FONTS, COLORS


class PackSuperDialog(ctk.CTkToplevel):
    """Dialog for Pack Super configuration - matches CLI packsuper()."""

    def __init__(self, master, project_dir):
        super().__init__(master)
        self.title("Pack Super Image")
        self.geometry("520x480")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.result = None
        self._project_dir = project_dir
        self._super_dir = os.path.join(project_dir, "super")

        if not os.path.exists(self._super_dir):
            os.makedirs(self._super_dir)

        # Calculate auto size
        self._auto_size = self._calc_auto_size()

        ctk.CTkLabel(self, text="Pack Super Image", font=FONTS["heading"],
                     text_color=COLORS["text_primary"]).pack(pady=(15, 5))

        ctk.CTkLabel(self, text=f"Place partition images in:\n{self._super_dir}",
                     font=FONTS["small"], text_color=COLORS["text_muted"],
                     justify="center").pack(pady=(0, 10))

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="x", padx=20, pady=5)

        # Super type
        ctk.CTkLabel(form, text="Super Type:", font=FONTS["body"]).grid(
            row=0, column=0, sticky="w", pady=5, padx=5)
        self._type_var = ctk.StringVar(value="A_only")
        ctk.CTkOptionMenu(form, values=["A_only", "AB", "VAB"],
                          variable=self._type_var, width=200).grid(
            row=0, column=1, pady=5, padx=5)

        # Readonly
        ctk.CTkLabel(form, text="Readonly:", font=FONTS["body"]).grid(
            row=1, column=0, sticky="w", pady=5, padx=5)
        self._readonly_var = ctk.StringVar(value="1")
        ctk.CTkOptionMenu(form, values=["1", "0"],
                          variable=self._readonly_var, width=200).grid(
            row=1, column=1, pady=5, padx=5)

        # Sparse
        ctk.CTkLabel(form, text="Sparse Image:", font=FONTS["body"]).grid(
            row=2, column=0, sticky="w", pady=5, padx=5)
        self._sparse_var = ctk.StringVar(value="0")
        ctk.CTkOptionMenu(form, values=["0", "1"],
                          variable=self._sparse_var, width=200).grid(
            row=2, column=1, pady=5, padx=5)

        # Super size
        ctk.CTkLabel(form, text="Super Size:", font=FONTS["body"]).grid(
            row=3, column=0, sticky="w", pady=5, padx=5)
        self._size_var = ctk.StringVar(value=str(self._auto_size))
        size_options = ["9126805504", "10200547328", "16106127360",
                        str(self._auto_size), "Custom"]
        self._size_menu = ctk.CTkOptionMenu(
            form, values=size_options,
            variable=self._size_var, width=200,
            command=self._on_size_change
        )
        self._size_menu.grid(row=3, column=1, pady=5, padx=5)

        # Custom size entry
        self._custom_size_entry = ctk.CTkEntry(form, width=200, font=FONTS["body"],
                                               placeholder_text="Size in bytes")
        self._custom_size_entry.grid(row=4, column=1, pady=5, padx=5)
        self._custom_size_entry.grid_remove()

        # Auto-move partitions option
        self._move_parts = self._find_movable_partitions()
        if self._move_parts and not os.listdir(self._super_dir):
            self._move_var = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(
                self, text=f"Auto-move {len(self._move_parts)} partition images to super/",
                variable=self._move_var, font=FONTS["body"]
            ).pack(padx=20, pady=5, anchor="w")
        else:
            self._move_var = ctk.BooleanVar(value=False)

        # Partition list
        parts = self._list_super_parts()
        if parts:
            ctk.CTkLabel(self, text=f"Partitions in super/: {', '.join(parts)}",
                         font=FONTS["small"], text_color=COLORS["text_secondary"],
                         wraplength=480).pack(padx=20, pady=5)

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)
        ctk.CTkButton(btn_frame, text="Pack", font=FONTS["button"], width=120,
                      command=self._on_pack, fg_color=COLORS["accent"]).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancel", font=FONTS["button"], width=120,
                      command=self.destroy,
                      fg_color=COLORS["bg_card"]).pack(side="left", padx=10)

        self._center()
        self.wait_window()

    def _on_size_change(self, value):
        if value == "Custom":
            self._custom_size_entry.grid()
        else:
            self._custom_size_entry.grid_remove()

    def _calc_auto_size(self):
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        try:
            total = sum(
                os.path.getsize(os.path.join(self._super_dir, p))
                for p in os.listdir(self._super_dir)
                if os.path.isfile(os.path.join(self._super_dir, p))
            ) + 409600
            # versize algorithm from run.py
            diff_size = total
            for i_ in range(1, 20):
                i_ = i_ - 0.5
                t = int(1024 * 1024 * 1024 * i_) - total
                if t < 0:
                    continue
                if t < diff_size:
                    diff_size = t
                else:
                    return int(i_ * 1024 * 1024 * 1024)
            return total + 4096000
        except Exception:
            return 9126805504

    def _find_movable_partitions(self):
        ti_out = os.path.join(self._project_dir, "TI_out")
        if not os.path.exists(ti_out):
            return []
        movable = []
        try:
            from src.utils import gettype
            for f in os.listdir(ti_out):
                fp = os.path.join(ti_out, f)
                if os.path.isfile(fp) and f.endswith('.img'):
                    if f.startswith('dsp'):
                        continue
                    try:
                        if gettype(fp) in ['ext', 'erofs']:
                            movable.append(f)
                    except Exception:
                        pass
        except ImportError:
            pass
        return movable

    def _list_super_parts(self):
        try:
            return [f for f in os.listdir(self._super_dir)
                    if f.endswith('.img') and os.path.isfile(os.path.join(self._super_dir, f))]
        except OSError:
            return []

    def _on_pack(self):
        size = self._size_var.get()
        if size == "Custom":
            size = self._custom_size_entry.get()
        self.result = {
            "super_type": self._type_var.get(),
            "readonly": self._readonly_var.get(),
            "sparse": self._sparse_var.get(),
            "size": size,
            "move_parts": self._move_var.get(),
            "movable": self._move_parts,
        }
        self.destroy()

    def _center(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = self.master.winfo_rootx() + (self.master.winfo_width() - w) // 2
        y = self.master.winfo_rooty() + (self.master.winfo_height() - h) // 2
        self.geometry(f"+{x}+{y}")


class PackPayloadDialog(ctk.CTkToplevel):
    """Dialog for Pack Payload configuration - matches CLI packpayload()."""

    def __init__(self, master, project_dir):
        super().__init__(master)
        self.title("Pack Payload")
        self.geometry("520x400")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.result = None
        self._project_dir = project_dir
        self._payload_dir = os.path.join(project_dir, "payload")

        if not os.path.exists(self._payload_dir):
            os.makedirs(self._payload_dir)

        # Auto size
        self._auto_size = self._calc_auto_size()

        ctk.CTkLabel(self, text="Pack Payload", font=FONTS["heading"],
                     text_color=COLORS["text_primary"]).pack(pady=(15, 5))

        ctk.CTkLabel(self,
                     text=f"Place partition images in:\n{self._payload_dir}\n\n"
                          "Note: This is CPU/memory intensive.\nWithout official signature it has limited use.",
                     font=FONTS["small"], text_color=COLORS["warning"],
                     justify="center").pack(pady=(0, 10))

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="x", padx=20, pady=5)

        # Super size
        ctk.CTkLabel(form, text="Super Size:", font=FONTS["body"]).grid(
            row=0, column=0, sticky="w", pady=5, padx=5)
        self._size_var = ctk.StringVar(value=str(self._auto_size))
        size_options = ["9126805504", "10200547328", str(self._auto_size), "Custom"]
        ctk.CTkOptionMenu(form, values=size_options,
                          variable=self._size_var, width=200,
                          command=self._on_size_change).grid(
            row=0, column=1, pady=5, padx=5)

        self._custom_entry = ctk.CTkEntry(form, width=200, font=FONTS["body"],
                                          placeholder_text="Size in bytes")
        self._custom_entry.grid(row=1, column=1, pady=5, padx=5)
        self._custom_entry.grid_remove()

        # Auto-move option
        self._move_parts = self._find_movable_parts()
        if self._move_parts and not os.listdir(self._payload_dir):
            self._move_var = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(
                self, text=f"Auto-move {len(self._move_parts)} images to payload/",
                variable=self._move_var, font=FONTS["body"]
            ).pack(padx=20, pady=5, anchor="w")
        else:
            self._move_var = ctk.BooleanVar(value=False)

        # Clean previous
        if os.path.exists(self._payload_dir) and os.listdir(self._payload_dir):
            self._clean_var = ctk.BooleanVar(value=False)
            ctk.CTkCheckBox(
                self, text="Clean previous payload data",
                variable=self._clean_var, font=FONTS["body"]
            ).pack(padx=20, pady=5, anchor="w")
        else:
            self._clean_var = ctk.BooleanVar(value=False)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)
        ctk.CTkButton(btn_frame, text="Pack", font=FONTS["button"], width=120,
                      command=self._on_pack, fg_color=COLORS["accent"]).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancel", font=FONTS["button"], width=120,
                      command=self.destroy,
                      fg_color=COLORS["bg_card"]).pack(side="left", padx=10)

        self._center()
        self.wait_window()

    def _on_size_change(self, value):
        if value == "Custom":
            self._custom_entry.grid()
        else:
            self._custom_entry.grid_remove()

    def _calc_auto_size(self):
        try:
            total = sum(
                os.path.getsize(os.path.join(self._payload_dir, p))
                for p in os.listdir(self._payload_dir)
                if os.path.isfile(os.path.join(self._payload_dir, p))
            ) + 409600
            diff_size = total
            for i_ in range(1, 20):
                i_ = i_ - 0.5
                t = int(1024 * 1024 * 1024 * i_) - total
                if t < 0:
                    continue
                if t < diff_size:
                    diff_size = t
                else:
                    return int(i_ * 1024 * 1024 * 1024)
            return total + 4096000
        except Exception:
            return 9126805504

    def _find_movable_parts(self):
        ti_out = os.path.join(self._project_dir, "TI_out")
        if not os.path.exists(ti_out):
            return []
        return [f for f in os.listdir(ti_out)
                if f.endswith('.img') and os.path.isfile(os.path.join(ti_out, f))]

    def _on_pack(self):
        size = self._size_var.get()
        if size == "Custom":
            size = self._custom_entry.get()
        self.result = {
            "size": size,
            "move_parts": self._move_var.get(),
            "movable": self._move_parts,
            "clean": self._clean_var.get(),
        }
        self.destroy()

    def _center(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = self.master.winfo_rootx() + (self.master.winfo_width() - w) // 2
        y = self.master.winfo_rooty() + (self.master.winfo_height() - h) // 2
        self.geometry(f"+{x}+{y}")


class PackPage(BasePage):
    """Pack page with partition list and pack actions."""

    def __init__(self, master, app, **kwargs):
        super().__init__(master, app, title="Pack", **kwargs)

        header = self.create_header("Pack")
        ctk.CTkButton(
            header, text="< Back", font=FONTS["body"],
            width=70, command=lambda: app.show_page("project"),
            fg_color="transparent", hover_color=COLORS["bg_card"],
            text_color=COLORS["text_secondary"]
        ).pack(side="right")

        # Options bar
        opt_frame = ctk.CTkFrame(self, fg_color="transparent")
        opt_frame.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(opt_frame, text="Format:", font=FONTS["body"],
                     text_color=COLORS["text_secondary"]).pack(side="left", padx=(0, 5))
        self._format_var = ctk.StringVar(value="img")
        ctk.CTkOptionMenu(
            opt_frame, values=["br", "dat", "img"],
            variable=self._format_var, width=80, font=FONTS["body"]
        ).pack(side="left", padx=5)

        ctk.CTkLabel(opt_frame, text="FS:", font=FONTS["body"],
                     text_color=COLORS["text_secondary"]).pack(side="left", padx=(15, 5))
        self._fs_var = ctk.StringVar(value="ext")
        ctk.CTkOptionMenu(
            opt_frame, values=["ext", "erofs", "f2fs"],
            variable=self._fs_var, width=90, font=FONTS["body"]
        ).pack(side="left", padx=5)

        # Action bar
        action_bar = self.create_action_bar()

        ctk.CTkButton(
            action_bar, text="Pack All", font=FONTS["button"],
            command=self._pack_all, width=100,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"]
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            action_bar, text="Pack Selected", font=FONTS["button"],
            command=self._pack_selected, width=130,
            fg_color=COLORS["bg_card"], hover_color=COLORS["bg_card_hover"]
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            action_bar, text="Pack Super", font=FONTS["button"],
            command=self._pack_super, width=110,
            fg_color=COLORS["bg_card"], hover_color=COLORS["bg_card_hover"]
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            action_bar, text="Pack Payload", font=FONTS["button"],
            command=self._pack_payload, width=120,
            fg_color=COLORS["bg_card"], hover_color=COLORS["bg_card_hover"]
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            action_bar, text="Refresh", font=FONTS["button"],
            command=self._scan_partitions, width=80,
            fg_color="transparent", hover_color=COLORS["bg_card"],
            text_color=COLORS["text_secondary"]
        ).pack(side="right", padx=5)

        # Partition list
        self._part_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=COLORS["border"]
        )
        self._part_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self._parts = {}  # {index: (name, type, checkbox_var)}

    def on_show(self):
        self._scan_partitions()

    def _get_project_dir(self):
        project = self.app.current_project
        if not project:
            return None
        return os.path.join(self.app.localdir, project)

    def _scan_partitions(self):
        """Scan for packable partitions - matches CLI packChoo() logic."""
        for w in self._part_frame.winfo_children():
            w.destroy()
        self._parts.clear()

        project_dir = self._get_project_dir()
        if not project_dir:
            return
        config_dir = os.path.join(project_dir, "config")

        if not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)

        # Read parts_info (same as CLI: json_edit(project + "/config/parts_info").read())
        parts_info_file = os.path.join(config_dir, "parts_info")
        parts_info = {}
        if os.path.exists(parts_info_file):
            try:
                with open(parts_info_file, 'r') as f:
                    parts_info = json.load(f)
            except (json.JSONDecodeError, OSError):
                pass

        idx = 0
        for item in sorted(os.listdir(project_dir)):
            item_path = os.path.join(project_dir, item)
            if not os.path.isdir(item_path):
                continue

            part_type = None
            fs_config = os.path.join(config_dir, f"{item}_fs_config")
            comp_file = os.path.join(item_path, "comp")
            dtbinfo = os.path.join(config_dir, f"dtbinfo_{item}")
            dtboinfo = os.path.join(config_dir, f"dtboinfo_{item}")

            if os.path.exists(fs_config):
                part_type = parts_info.get(item, "ext")
            elif os.path.exists(comp_file):
                part_type = "bootimg"
            elif os.path.exists(dtbinfo):
                part_type = "dtb"
            elif os.path.exists(dtboinfo):
                part_type = "dtbo"
            else:
                continue

            idx += 1
            var = ctk.BooleanVar(value=False)

            row = ctk.CTkFrame(self._part_frame, fg_color="transparent")
            row.pack(fill="x", padx=5, pady=2)

            cb = ctk.CTkCheckBox(
                row, text=f"  {item}",
                font=FONTS["body"], variable=var,
                text_color=COLORS["text_primary"]
            )
            cb.pack(side="left")

            badge = ctk.CTkLabel(
                row, text=f"<{part_type}>",
                font=FONTS["small"],
                text_color=COLORS["text_muted"]
            )
            badge.pack(side="right", padx=10)

            self._parts[idx] = (item, part_type, var)

        # Update FS dropdown to match the most common original partition type
        fs_types = [t for _, t, _ in self._parts.values() if t in ("ext", "erofs", "f2fs")]
        if fs_types:
            from collections import Counter
            most_common = Counter(fs_types).most_common(1)[0][0]
            self._fs_var.set(most_common)

        if not self._parts:
            ctk.CTkLabel(
                self._part_frame,
                text="No packable partitions found.\nUnpack partition images first.",
                font=FONTS["body"],
                text_color=COLORS["text_muted"],
                justify="center"
            ).pack(pady=40)

    def _pack_all(self):
        items = [(n, t) for n, t, _ in self._parts.values()]
        if items:
            self._do_pack(items)

    def _pack_selected(self):
        items = [(n, t) for n, t, v in self._parts.values() if v.get()]
        if not items:
            self.app.console_print("No partitions selected.\n")
            return
        self._do_pack(items)

    def _do_pack(self, items):
        project_dir = self._get_project_dir()
        if not project_dir:
            return
        form = self._format_var.get()
        imgtype = self._fs_var.get()

        # For bootimg/dtb/dtbo, format/fs is irrelevant
        def _worker():
            import run as run_module
            localdir = self.app.localdir

            config_dir = os.path.join(project_dir, "config")
            parts_info_file = os.path.join(config_dir, "parts_info")
            json_ = {}
            if os.path.exists(parts_info_file):
                try:
                    with open(parts_info_file, 'r') as f:
                        json_ = json.load(f)
                except (json.JSONDecodeError, OSError):
                    pass

            for name, ptype in items:
                self.app.console_print(f"\nPacking: {name} ({ptype})...\n")
                try:
                    if ptype == 'bootimg':
                        run_module.dboot(
                            os.path.join(project_dir, name),
                            os.path.join(project_dir, f"{name}.img")
                        )
                    elif ptype == 'dtb':
                        run_module.makedtb(name, project_dir)
                    elif ptype == 'dtbo':
                        run_module.makedtbo(name, project_dir)
                    else:
                        # Use the partition's original FS type from parts_info,
                        # fall back to the dropdown selection
                        fs_type = json_.get(name, imgtype)
                        run_module.inpacker(name, project_dir, form, fs_type, json_)
                except Exception as e:
                    import traceback
                    self.app.console_print(f"[ERROR] {name}: {e}\n")
                    self.app.console_print(traceback.format_exc() + "\n")
            os.chdir(localdir)
            self.app.console_print("\nPack complete!\n")

        self.run_task(_worker)

    def _pack_super(self):
        """Open Pack Super dialog and execute."""
        project_dir = self._get_project_dir()
        if not project_dir:
            return

        dialog = PackSuperDialog(self.app, project_dir)
        if not dialog.result:
            return

        cfg = dialog.result

        def _worker():
            import shutil
            import run as run_module
            localdir = self.app.localdir
            super_dir = os.path.join(project_dir, "super")
            ti_out = os.path.join(project_dir, "TI_out")

            # Move partitions if requested
            if cfg["move_parts"] and cfg["movable"]:
                for f in cfg["movable"]:
                    src = os.path.join(ti_out, f)
                    dst = os.path.join(super_dir, f)
                    if os.path.exists(src):
                        self.app.console_print(f"Moving {f} to super/\n")
                        shutil.move(src, dst)

            # Remove existing super.img
            out_super = os.path.join(ti_out, "super.img")
            if os.path.exists(out_super):
                os.remove(out_super)

            self.app.console_print("Packing Super image...\n")
            try:
                run_module.insuper(
                    super_dir, out_super,
                    cfg["size"], cfg["super_type"],
                    cfg["sparse"], cfg["readonly"]
                )
            except Exception as e:
                import traceback
                self.app.console_print(f"[ERROR] {e}\n{traceback.format_exc()}\n")
            os.chdir(localdir)

        self.run_task(_worker)

    def _pack_payload(self):
        """Open Pack Payload dialog and execute."""
        project_dir = self._get_project_dir()
        if not project_dir:
            return

        import platform
        if platform.system() != 'Linux':
            self.app.console_print(
                f"[ERROR] Pack Payload only supported on Linux. Current: {platform.system()}\n")
            return

        dialog = PackPayloadDialog(self.app, project_dir)
        if not dialog.result:
            return

        cfg = dialog.result

        def _worker():
            import shutil
            import run as run_module
            from src.api import re_folder, f_remove
            localdir = self.app.localdir

            payload_dir = os.path.join(project_dir, "payload")
            ti_out = os.path.join(project_dir, "TI_out")

            # Clean if requested
            if cfg["clean"]:
                re_folder(payload_dir)
                re_folder(os.path.join(ti_out, "payload"))
                f_remove(os.path.join(ti_out, "payload", "dynamic_partitions_info.txt"))

            # Move parts if requested
            if cfg["move_parts"] and cfg["movable"]:
                for f in cfg["movable"]:
                    src = os.path.join(ti_out, f)
                    dst = os.path.join(payload_dir, f)
                    if os.path.exists(src):
                        self.app.console_print(f"Moving {f} to payload/\n")
                        shutil.move(src, dst)

            self.app.console_print("Packing Payload...\n")
            try:
                run_module.inpayload(cfg["size"], project_dir)
            except Exception as e:
                import traceback
                self.app.console_print(f"[ERROR] {e}\n{traceback.format_exc()}\n")
            os.chdir(localdir)

        self.run_task(_worker)
