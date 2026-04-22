"""Claude Code Installer — Main GUI Entry Point."""

import tkinter as tk
from tkinter import ttk, messagebox, font as tk_font
import threading

from detectors import (
    Detector, Status,
    NodeDetector, GitDetector, PythonDetector,
    PowerShellDetector, BashDetector, NpmDetector,
)
from utils.logger import setup_logger

DETECTORS = [
    NodeDetector,
    GitDetector,
    PythonDetector,
    PowerShellDetector,
    BashDetector,
    NpmDetector,
]

# ── Color Palette ──────────────────────────────────────────
BG = "#f8fafc"          # Main background
CARD_BG = "#ffffff"     # Card background
BORDER = "#e2e8f0"      # Standard border
HEADER_BG_START = "#f8fafc"
HEADER_BG_END = "#e8ecf1"
TEXT_PRIMARY = "#1e293b"
TEXT_SECONDARY = "#475569"
TEXT_MUTED = "#94a3b8"
OK_COLOR = "#22c55e"
MISSING_COLOR = "#ef4444"
WARNING_COLOR = "#f59e0b"
MISSING_BORDER = "#fca5a5"
WARNING_BORDER = "#fcd34d"
BUTTON_BG = "#4f63e3"    # Midpoint of blue-indigo gradient
BUTTON_SHADOW = "#3b82f6"

# ── Font Config ────────────────────────────────────────────
FONT_BODY = ("Segoe UI", 10, "normal")
FONT_BODY_BOLD = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_SUBTITLE = ("Segoe UI", 12, "normal")
FONT_LABEL = ("Segoe UI", 13, "bold")
FONT_SECTION = ("Segoe UI", 11, "bold")
FONT_LOG = ("Cascadia Mono", 12, "normal")
FONT_LOG_FALLBACK = ("Consolas", 12, "normal")
FONT_CARD_NAME = ("Segoe UI", 13, "bold")
FONT_CARD_DETAIL = ("Segoe UI", 12, "normal")
FONT_BTN = ("Segoe UI", 14, "bold")

# ── Spacing ────────────────────────────────────────────────
PADDING_WINDOW = 16
PADDING_CARD = (10, 14)
CARD_GAP = 6

# ── Status Display ─────────────────────────────────────────
STATUS_ICONS = {
    "ok": "✓",
    "missing": "✗",
    "warning": "⚠",
}
STATUS_BORDER_COLORS = {
    "ok": BORDER,
    "missing": MISSING_BORDER,
    "warning": WARNING_BORDER,
}
STATUS_COLORS = {
    "ok": OK_COLOR,
    "missing": MISSING_COLOR,
    "warning": WARNING_COLOR,
}


class InstallerApp:
    """Main application window."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Claude Code Installer")
        self.root.geometry("800x500")
        self.root.minsize(700, 400)

        self.logger = setup_logger()
        self.results: list = []

        self._setup_style()
        self._build_ui()
        self._auto_detect()

    def _setup_style(self):
        """Configure ttk styles for the clean light theme."""
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame", background=BG)
        style.configure("Header.TFrame", background=HEADER_BG_START)
        style.configure("Bottom.TFrame", background=CARD_BG)

        style.configure("Section.TLabel", background=BG, foreground=TEXT_SECONDARY, font=FONT_SECTION)
        style.configure("Title.TLabel", background=HEADER_BG_START, foreground=TEXT_PRIMARY, font=FONT_TITLE)
        style.configure("Subtitle.TLabel", background=HEADER_BG_START, foreground=TEXT_MUTED, font=("Segoe UI", 12))
        style.configure("Card.TLabel", background=CARD_BG, foreground=TEXT_SECONDARY)
        style.configure("CardName.TLabel", background=CARD_BG, foreground=TEXT_PRIMARY, font=FONT_CARD_NAME)
        style.configure("CardDetail.TLabel", background=CARD_BG, foreground=TEXT_SECONDARY, font=FONT_CARD_DETAIL)
        style.configure("StatusOk.TLabel", foreground=OK_COLOR, background=CARD_BG, font=("", 16, "bold"))
        style.configure("StatusMissing.TLabel", foreground=MISSING_COLOR, background=CARD_BG, font=("", 16, "bold"))
        style.configure("StatusWarning.TLabel", foreground=WARNING_COLOR, background=CARD_BG, font=("", 16, "bold"))

        style.configure("Install.TButton", background=BUTTON_BG, foreground="white", font=FONT_BTN, borderwidth=0, focuscolor="none")
        style.map("Install.TButton",
                  background=[("active", BUTTON_SHADOW), ("pressed", "#3730a3")],
                  foreground=[("active", "white")])

        style.configure("Refresh.TButton", background=CARD_BG, foreground=TEXT_SECONDARY, font=("Segoe UI", 12), borderwidth=1, padding=(8, 20))
        style.map("Refresh.TButton",
                  background=[("active", BG)],
                  bordercolor=[("active", TEXT_MUTED)])

    def _build_ui(self):
        """Build the beautified two-column layout."""
        self.root.configure(background=BG)
        self.root.geometry("900x560")
        self.root.minsize(750, 450)

        # Main layout: 3 rows (header, content, bottom)
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=0)
        self.root.columnconfigure(0, weight=1)

        # Header Bar
        header = ttk.Frame(self.root, style="Header.TFrame")
        header.grid(row=0, column=0, sticky="ew")

        icon_frame = tk.Frame(header, bg=BUTTON_BG, width=36, height=36)
        icon_frame.pack_propagate(False)
        icon_frame.pack(side="left", padx=(24, 12), pady=16)

        tk.Label(icon_frame, text="C", bg=BUTTON_BG, fg="white",
                 font=("Segoe UI", 16, "bold")).pack(expand=True)

        title_frame = tk.Frame(header, bg=HEADER_BG_START)
        title_frame.pack(side="left", fill="y", pady=16)

        tk.Label(title_frame, text="Claude Code Installer", bg=HEADER_BG_START,
                 fg=TEXT_PRIMARY, font=FONT_TITLE).pack(anchor="w")
        tk.Label(title_frame, text="一键安装环境检测与执行", bg=HEADER_BG_START,
                 fg=TEXT_MUTED, font=("Segoe UI", 12)).pack(anchor="w")

        # Separator at bottom of header
        tk.Frame(self.root, height=1, bg=BORDER).grid(row=0, column=0, sticky="ew")

        # Content Area (two columns)
        content_frame = ttk.Frame(self.root)
        content_frame.grid(row=1, column=0, sticky="nsew")
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=2)
        content_frame.rowconfigure(0, weight=1)

        # Left Panel
        left_frame = ttk.Frame(content_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(PADDING_WINDOW, 8), pady=PADDING_WINDOW)

        ttk.Label(left_frame, text="ENVIRONMENT CHECK", style="Section.TLabel").pack(anchor="w", pady=(0, 8))

        # Container for detector cards
        self.cards_frame = ttk.Frame(left_frame)
        self.cards_frame.pack(fill="both", expand=True)

        # Refresh button
        ttk.Button(left_frame, text="Refresh", style="Refresh.TButton",
                   command=self._auto_detect).pack(anchor="w", pady=(8, 0))

        # Right Panel
        right_frame = ttk.Frame(content_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(8, PADDING_WINDOW), pady=PADDING_WINDOW)

        ttk.Label(right_frame, text="INSTALLATION LOG", style="Section.TLabel").pack(anchor="w", pady=(0, 8))

        # Log container with white background
        self.log_container = tk.Frame(right_frame, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)
        self.log_container.pack(fill="both", expand=True)

        self.log_text = tk.Text(self.log_container, state="disabled", wrap="word",
                                 font=FONT_LOG, bg=CARD_BG, fg=TEXT_SECONDARY,
                                 borderwidth=0, highlightthickness=0, padx=14, pady=14)
        self.log_text.pack(fill="both", expand=True)

        # Ensure monospace font is available
        available_fonts = set(tk_font.families())
        if "Cascadia Mono" not in available_fonts:
            self.log_text.configure(font=FONT_LOG_FALLBACK)

        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.configure(yscrollcommand=scrollbar.set)

        # Bottom Bar
        bottom_frame = ttk.Frame(self.root, style="Bottom.TFrame")
        bottom_frame.grid(row=2, column=0, sticky="ew")
        tk.Frame(bottom_frame, height=1, bg=BORDER).pack(fill="x")

        self.install_btn = tk.Button(self.root, text="One-Click Install",
                                      bg=BUTTON_BG, fg="white", font=FONT_BTN,
                                      activebackground=BUTTON_SHADOW, activeforeground="white",
                                      bd=0, relief="flat", cursor="hand2",
                                      padx=48, pady=12)
        self.install_btn.grid(row=2, column=0, pady=8)

        # Store card widgets for later updates
        self._card_widgets: list = []

    def _log(self, message: str):
        """Append message to the log panel (thread-safe)."""
        def _append():
            self.log_text.configure(state="normal")
            self.log_text.insert("end", message + "\n")
            self.log_text.see("end")
            self.log_text.configure(state="disabled")
        self.root.after(0, _append)

    def _auto_detect(self):
        """Run all detectors and update the tree view."""
        if getattr(self, "_detecting", False):
            return
        self._detecting = True
        self.results.clear()
        self.install_btn.configure(state="disabled")
        self._log("Starting environment detection...")

        def _detect():
            try:
                for det_cls in DETECTORS:
                    det = det_cls()
                    status, detail = det.detect()
                    self.results.append((det.name, status, detail))
                    status_key = status.value if hasattr(status, 'value') else str(status).lower()
                    self._log(f"  [{STATUS_ICONS[status_key]}] {det.name}: {detail}")

                self.root.after(0, self._update_tree)
                self.root.after(0, self._on_detection_complete)
                self.root.after(0, lambda: self._log("Detection complete."))
            except Exception as e:
                self.root.after(0, lambda e=e: self._log(f"ERROR: Detection failed -- {e}"))
                self.root.after(0, self._on_detection_complete)

        threading.Thread(target=_detect, daemon=True).start()

    def _on_detection_complete(self):
        """Enable install button only if issues were found."""
        has_issues = any(
            (s.value if hasattr(s, 'value') else str(s).lower()) in ("missing", "warning")
            for _, s, _ in self.results
        )
        self.install_btn.configure(state="normal" if has_issues else "disabled")
        self._detecting = False

    def _update_tree(self):
        """Render detector results as styled cards."""
        for widget in self._card_widgets:
            widget.destroy()
        self._card_widgets.clear()

        for name, status, detail in self.results:
            status_str = status.value if hasattr(status, 'value') else str(status).lower()
            self._create_card(name, status_str, detail)

    def _create_card(self, name: str, status: str, detail: str):
        """Create a single detector card widget."""
        icon = STATUS_ICONS.get(status, "?")
        border_color = STATUS_BORDER_COLORS.get(status, BORDER)
        text_color = STATUS_COLORS.get(status, TEXT_SECONDARY)

        # Card frame with colored border
        card = tk.Frame(self.cards_frame, bg=CARD_BG,
                         highlightbackground=border_color, highlightthickness=1,
                         relief="flat")
        card.pack(fill="x", pady=(0, CARD_GAP))
        self._card_widgets.append(card)

        # Inner frame for padding
        inner = tk.Frame(card, bg=CARD_BG)
        inner.pack(fill="x", padx=10, pady=8)

        # Icon
        tk.Label(inner, text=icon, bg=CARD_BG, fg=text_color,
                  font=("", 16, "bold"), width=2).pack(side="left")

        # Name
        tk.Label(inner, text=name, bg=CARD_BG, fg=TEXT_PRIMARY,
                  font=FONT_CARD_NAME, anchor="w", width=14).pack(side="left", padx=(4, 0))

        # Detail (right-aligned)
        tk.Label(inner, text=detail, bg=CARD_BG, fg=text_color,
                  font=FONT_CARD_DETAIL, anchor="e").pack(side="right", fill="x", expand=True)

    def _start_install(self):
        """Handle one-click install button."""
        missing = [(n, s, d) for n, s, d in self.results
                    if (s.value if hasattr(s, 'value') else str(s).lower()) in ("missing", "warning")]
        if not missing:
            messagebox.showinfo("All Good", "All dependencies are installed and up to date!")
            return

        lines = ["The following components need installation:"]
        for name, status, detail in missing:
            status_key = status.value if hasattr(status, 'value') else str(status).lower()
            lines.append(f"  {STATUS_ICONS[status_key]} {name}: {detail}")
        lines.append("\nProceed with installation?")

        if not messagebox.askokcancel("Confirm Install", "\n".join(lines)):
            return

        self.install_btn.configure(state="disabled")
        self._log("\nStarting installation...")

        threading.Thread(target=self._run_install, args=(missing,), daemon=True).start()

    def _run_install(self, missing):
        """Execute installation for each missing component."""
        from installers import NpmInstaller, WingetInstaller, DirectInstaller

        for name, status, detail in missing:
            self._log(f"\n--- Installing {name} ---")

            # NpmInstaller only applies to Claude Code, not system dependencies
            installers = []
            if name == "npm" or name == "Node.js":
                installers.append(NpmInstaller())
            installers.append(WingetInstaller(name))
            installers.append(DirectInstaller(name))

            success = False
            for installer in installers:
                self._log(f"Trying: {installer.name}")
                try:
                    if installer.install(self._log):
                        success = True
                        self._log(f"  {name} installed successfully!")
                        break
                    else:
                        self._log(f"  {installer.name} returned failure")
                except Exception as e:
                    self._log(f"  {installer.name} failed: {e}")

            if not success:
                self._log(f"  ERROR: All installation methods failed for {name}")

        self.root.after(0, lambda: self.install_btn.configure(state="normal"))
        self.root.after(0, lambda: self._log("\nInstallation complete."))
        self.root.after(0, lambda: messagebox.showinfo("Done", "Installation complete. Please refresh to verify."))


def main():
    root = tk.Tk()
    InstallerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
