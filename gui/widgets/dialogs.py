"""
TIK5 GUI Dialogs - Confirm, text input, file picker modals.
"""
import customtkinter as ctk
from gui.theme import FONTS, COLORS


class ConfirmDialog(ctk.CTkToplevel):
    """Simple confirmation dialog."""

    def __init__(self, master, title="Confirm", message="Are you sure?",
                 yes_text="Yes", no_text="No"):
        super().__init__(master)
        self.title(title)
        self.geometry("400x180")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.result = False

        ctk.CTkLabel(
            self, text=message, font=FONTS["body"],
            wraplength=350
        ).pack(pady=(30, 20), padx=20)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame, text=yes_text, font=FONTS["button"],
            width=100, command=self._on_yes,
            fg_color=COLORS["accent"]
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame, text=no_text, font=FONTS["button"],
            width=100, command=self._on_no,
            fg_color=COLORS["bg_card"], hover_color=COLORS["bg_card_hover"]
        ).pack(side="left", padx=10)

        self._center()
        self.wait_window()

    def _on_yes(self):
        self.result = True
        self.destroy()

    def _on_no(self):
        self.result = False
        self.destroy()

    def _center(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = self.master.winfo_rootx() + (self.master.winfo_width() - w) // 2
        y = self.master.winfo_rooty() + (self.master.winfo_height() - h) // 2
        self.geometry(f"+{x}+{y}")


class TextInputDialog(ctk.CTkToplevel):
    """Text input dialog."""

    def __init__(self, master, title="Input", prompt="Enter value:",
                 default="", ok_text="OK", cancel_text="Cancel"):
        super().__init__(master)
        self.title(title)
        self.geometry("420x180")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.result = None

        ctk.CTkLabel(
            self, text=prompt, font=FONTS["body"]
        ).pack(pady=(20, 10), padx=20, anchor="w")

        self._entry = ctk.CTkEntry(self, font=FONTS["body"], width=380)
        self._entry.pack(padx=20)
        if default:
            self._entry.insert(0, default)
        self._entry.focus_set()
        self._entry.bind("<Return>", lambda e: self._on_ok())

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)

        ctk.CTkButton(
            btn_frame, text=ok_text, font=FONTS["button"],
            width=100, command=self._on_ok,
            fg_color=COLORS["accent"]
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame, text=cancel_text, font=FONTS["button"],
            width=100, command=self._on_cancel,
            fg_color=COLORS["bg_card"], hover_color=COLORS["bg_card_hover"]
        ).pack(side="left", padx=10)

        self._center()
        self.wait_window()

    def _on_ok(self):
        self.result = self._entry.get()
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()

    def _center(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = self.master.winfo_rootx() + (self.master.winfo_width() - w) // 2
        y = self.master.winfo_rooty() + (self.master.winfo_height() - h) // 2
        self.geometry(f"+{x}+{y}")


class ChecklistDialog(ctk.CTkToplevel):
    """Dialog with a scrollable list of checkboxes for multi-select."""

    def __init__(self, master, title="Select Items", prompt="Choose items:",
                 items=None, ok_text="OK", cancel_text="Cancel",
                 select_all_text="Select All"):
        super().__init__(master)
        self.title(title)
        self.geometry("520x420")
        self.resizable(False, True)
        self.transient(master)
        self.grab_set()

        self.result = None  # list of selected items or None if cancelled
        self._vars = []

        ctk.CTkLabel(
            self, text=prompt, font=FONTS["body"],
            wraplength=480, anchor="w"
        ).pack(pady=(15, 5), padx=20, anchor="w")

        # Select all / Deselect all buttons
        ctrl_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctrl_frame.pack(fill="x", padx=20)
        ctk.CTkButton(
            ctrl_frame, text=select_all_text, font=FONTS["small"],
            width=90, command=self._select_all,
            fg_color=COLORS["bg_card"], hover_color=COLORS["bg_card_hover"],
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=(0, 5))
        ctk.CTkButton(
            ctrl_frame, text="Deselect All", font=FONTS["small"],
            width=90, command=self._deselect_all,
            fg_color=COLORS["bg_card"], hover_color=COLORS["bg_card_hover"],
            text_color=COLORS["text_secondary"]
        ).pack(side="left")

        # Scrollable checkbox list
        scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_card"],
                                         corner_radius=8)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        for item in (items or []):
            var = ctk.BooleanVar(value=True)
            self._vars.append((item, var))
            ctk.CTkCheckBox(
                scroll, text=item, font=FONTS["body"], variable=var,
                fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"]
            ).pack(fill="x", pady=2, padx=5)

        # OK / Cancel
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame, text=ok_text, font=FONTS["button"],
            width=100, command=self._on_ok,
            fg_color=COLORS["accent"]
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame, text=cancel_text, font=FONTS["button"],
            width=100, command=self._on_cancel,
            fg_color=COLORS["bg_card"], hover_color=COLORS["bg_card_hover"]
        ).pack(side="left", padx=10)

        self._center()
        self.wait_window()

    def _select_all(self):
        for _, var in self._vars:
            var.set(True)

    def _deselect_all(self):
        for _, var in self._vars:
            var.set(False)

    def _on_ok(self):
        self.result = [item for item, var in self._vars if var.get()]
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()

    def _center(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = self.master.winfo_rootx() + (self.master.winfo_width() - w) // 2
        y = self.master.winfo_rooty() + (self.master.winfo_height() - h) // 2
        self.geometry(f"+{x}+{y}")


class InputPromptBar(ctk.CTkFrame):
    """Inline input bar that appears in the console area when input() is called."""

    def __init__(self, master, on_submit=None, **kwargs):
        super().__init__(master, fg_color=COLORS["bg_card"], corner_radius=8, **kwargs)

        self._on_submit = on_submit

        self._label = ctk.CTkLabel(
            self, text="Input:", font=FONTS["body"],
            text_color=COLORS["text_secondary"]
        )
        self._label.pack(side="left", padx=(10, 5), pady=5)

        self._entry = ctk.CTkEntry(
            self, font=FONTS["body"], width=300,
            placeholder_text="Type here..."
        )
        self._entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self._entry.bind("<Return>", self._submit)

        self._btn = ctk.CTkButton(
            self, text="Send", width=60, font=FONTS["button"],
            command=self._submit, fg_color=COLORS["accent"]
        )
        self._btn.pack(side="right", padx=(5, 10), pady=5)

        # Radio buttons for [1/0] style prompts
        self._radio_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._radio_var = ctk.StringVar(value="1")

    def show(self, prompt=""):
        """Show the input bar with the given prompt."""
        self._entry.delete(0, "end")

        # Detect [1/0] style prompts
        if "[1/0]" in prompt or "[1/0]" in prompt:
            self._show_radio_prompt(prompt, ["1", "0"])
        elif "[1]" in prompt and "[2]" in prompt:
            self._show_entry_prompt(prompt)
        else:
            self._show_entry_prompt(prompt)

        self.pack(fill="x", padx=5, pady=5)
        self._entry.focus_set()

    def _show_entry_prompt(self, prompt):
        """Show standard text entry."""
        self._radio_frame.pack_forget()
        self._entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self._btn.pack(side="right", padx=(5, 10), pady=5)
        clean = prompt.strip().rstrip(":")
        if clean:
            self._label.configure(text=clean[:60])

    def _show_radio_prompt(self, prompt, options):
        """Show radio button prompt for binary choices."""
        self._entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self._btn.pack(side="right", padx=(5, 10), pady=5)
        clean = prompt.strip().rstrip(":")
        if clean:
            self._label.configure(text=clean[:60])

    def hide(self):
        """Hide the input bar."""
        self.pack_forget()

    def _submit(self, event=None):
        value = self._entry.get()
        self.hide()
        if self._on_submit:
            self._on_submit(value)
