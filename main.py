"""Claude Code Installer — Main GUI Entry Point."""

import tkinter as tk
from tkinter import ttk, messagebox
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

STATUS_ICONS = {
    Status.OK: "✓",
    Status.MISSING: "✗",
    Status.WARNING: "⚠",
}
STATUS_COLORS = {
    Status.OK: "#22c55e",
    Status.MISSING: "#ef4444",
    Status.WARNING: "#f59e0b",
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

        self._build_ui()
        self._auto_detect()

    def _build_ui(self):
        """Build the two-column layout with bottom button bar."""
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=1)

        left_frame = ttk.Frame(self.root, padding=10)
        left_frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(left_frame, text="Environment Check", font=("", 11, "bold")).pack(anchor="w")

        columns = ("status", "name", "detail")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=12)
        self.tree.heading("status", text="")
        self.tree.heading("name", text="Component")
        self.tree.heading("detail", text="Status")
        self.tree.column("status", width=30, anchor="center")
        self.tree.column("name", width=120)
        self.tree.column("detail", width=150)
        self.tree.pack(fill="both", expand=True, pady=5)

        for status, color in STATUS_COLORS.items():
            self.tree.tag_configure(status.value, foreground=color)

        ttk.Button(left_frame, text="Refresh", command=self._auto_detect).pack(anchor="w", pady=5)

        right_frame = ttk.Frame(self.root, padding=10)
        right_frame.grid(row=0, column=1, sticky="nsew")

        ttk.Label(right_frame, text="Installation Log", font=("", 11, "bold")).pack(anchor="w")

        self.log_text = tk.Text(right_frame, state="disabled", wrap="word", font=("", 9))
        self.log_text.pack(fill="both", expand=True, pady=5)

        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.configure(yscrollcommand=scrollbar.set)

        bottom_frame = ttk.Frame(self.root, padding=10)
        bottom_frame.grid(row=1, column=0, columnspan=2)

        self.install_btn = ttk.Button(
            bottom_frame,
            text="\U0001f680 One-Click Install",
            command=self._start_install,
        )
        self.install_btn.pack(pady=5)

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
                    self._log(f"  [{STATUS_ICONS[status]}] {det.name}: {detail}")

                self.root.after(0, self._update_tree)
                self.root.after(0, self._on_detection_complete)
                self.root.after(0, lambda: self._log("Detection complete."))
            except Exception as e:
                self.root.after(0, lambda e=e: self._log(f"ERROR: Detection failed -- {e}"))
                self.root.after(0, self._on_detection_complete)

        threading.Thread(target=_detect, daemon=True).start()

    def _on_detection_complete(self):
        """Enable install button only if issues were found."""
        has_issues = any(s in (Status.MISSING, Status.WARNING) for _, s, _ in self.results)
        self.install_btn.configure(state="normal" if has_issues else "disabled")
        self._detecting = False

    def _update_tree(self):
        """Populate the treeview with detection results."""
        self.tree.delete(*self.tree.get_children())
        for name, status, detail in self.results:
            icon = STATUS_ICONS[status]
            self.tree.insert("", "end", values=(icon, name, detail), tags=(status.value,))

    def _start_install(self):
        """Handle one-click install button."""
        missing = [(n, s, d) for n, s, d in self.results if s in (Status.MISSING, Status.WARNING)]
        if not missing:
            messagebox.showinfo("All Good", "All dependencies are installed and up to date!")
            return

        lines = ["The following components need installation:"]
        for name, status, detail in missing:
            lines.append(f"  {STATUS_ICONS[status]} {name}: {detail}")
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
