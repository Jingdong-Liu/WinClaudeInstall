"""Claude Code 一键安装器 — 主 GUI 入口."""

import tkinter as tk
from tkinter import ttk, messagebox
import threading

from detectors import (
    Detector, Status,
    NodeDetector, GitDetector, PythonDetector,
    PowerShellDetector, BashDetector, NpmDetector,
    ClaudeCodeDetector, CCSwitchDetector,
)
from utils.logger import setup_logger

DETECTORS = [
    PowerShellDetector,
    PythonDetector,
    NodeDetector,
    GitDetector,
    BashDetector,
    NpmDetector,
    ClaudeCodeDetector,
    CCSwitchDetector,
]

# 依赖按「从基础到最终」排序
DEPENDENCIES = [
    "PowerShell",
    "Python",
    "Node.js",
    "Git",
    "Bash",
    "npm",
    "Claude Code",
    "CC-Switch",
]

# ── Color Palette ──────────────────────────────────────────
BG = "#f8fafc"
CARD_BG = "#ffffff"
BORDER = "#e2e8f0"
TEXT_PRIMARY = "#1e293b"
TEXT_SECONDARY = "#475569"
TEXT_MUTED = "#94a3b8"
OK_COLOR = "#22c55e"
MISSING_COLOR = "#ef4444"
WARNING_COLOR = "#f59e0b"
BUTTON_BG = "#4f63e3"
BUTTON_SHADOW = "#3b82f6"

# ── Font Config ────────────────────────────────────────────
FONT_BTN = ("Segoe UI", 14, "bold")
FONT_STATUS = ("Segoe UI", 11, "normal")
FONT_SECTION = ("Segoe UI", 11, "bold")
FONT_ACTIVITY = ("Segoe UI", 12, "normal")

# ── Spacing ────────────────────────────────────────────────
PADDING_WINDOW = 16

# ── Status Display ─────────────────────────────────────────
STATUS_ICONS = {
    "ok": "✓",
    "missing": "✗",
    "warning": "⚠",
}

# Activity spinner frames
SPINNER = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


class InstallerApp:
    """主应用程序窗口."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Claude Code 一键安装器")
        self.root.geometry("900x600")
        self.root.minsize(750, 480)

        self.logger = setup_logger()
        self.results: list = []
        self._spinner_idx = 0
        self._spinner_after = None
        self._progress_lines: list = []

        self._setup_style()
        self._build_ui()
        self._prepopulate_table()
        self._auto_detect()

    # ── Style ───────────────────────────────────────────────

    def _setup_style(self):
        """配置 ttk 样式."""
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame", background=BG)

        style.configure("Action.TButton", background=BUTTON_BG, foreground="white",
                        font=("Segoe UI", 13, "bold"), borderwidth=0, focuscolor="none",
                        padding=(16, 8))
        style.map("Action.TButton",
                  background=[("active", BUTTON_SHADOW), ("pressed", "#3730a3")],
                  foreground=[("active", "white")])

        style.configure("Status.TLabel", background=CARD_BG, foreground=TEXT_SECONDARY,
                        font=FONT_STATUS)

        style.configure("Activity.TLabel", background=CARD_BG, foreground=TEXT_PRIMARY,
                        font=FONT_ACTIVITY)

        style.configure("Table.Treeview", background=CARD_BG, foreground=TEXT_PRIMARY,
                        fieldbackground=CARD_BG, font=("Segoe UI", 11))
        style.configure("Table.Treeview.Heading", background=CARD_BG, foreground=TEXT_SECONDARY,
                        font=FONT_SECTION, borderwidth=0)
        style.map("Table.Treeview.Heading",
                  background=[("active", BG)])

        style.configure("Detecting.TButton", background="#f59e0b", foreground="white",
                        font=("Segoe UI", 13, "bold"), borderwidth=0, focuscolor="none",
                        padding=(16, 8))
        style.map("Detecting.TButton",
                  background=[("active", "#d97706"), ("disabled", "#fbbf24")],
                  foreground=[("active", "white")])

    # ── UI Building ─────────────────────────────────────────

    def _build_ui(self):
        """构建主界面."""
        self.root.configure(background=BG)

        # Main layout: 3 rows (content, progress, status bar)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=0)  # progress section
        self.root.rowconfigure(2, weight=0)  # status bar
        self.root.columnconfigure(0, weight=1)

        # ── Content Area ──
        content = ttk.Frame(self.root)
        content.grid(row=0, column=0, sticky="nsew", padx=PADDING_WINDOW, pady=PADDING_WINDOW)
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=0)  # button row
        content.rowconfigure(1, weight=1)  # table

        # ── Button Row ──
        btn_frame = ttk.Frame(content)
        btn_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self.detect_btn = ttk.Button(btn_frame, text="一键自动检测",
                                      style="Action.TButton", command=self._auto_detect)
        self.detect_btn.pack(side="left", padx=(0, 8))

        self.install_btn = ttk.Button(btn_frame, text="安装",
                                       style="Action.TButton", command=self._start_install)
        self.install_btn.pack(side="left", padx=(0, 8))

        self.download_install_btn = ttk.Button(btn_frame, text="下载并安装依赖",
                                                style="Action.TButton", command=self._download_and_install)
        self.download_install_btn.pack(side="left")

        # Result label (right-aligned)
        self.result_label = tk.Label(btn_frame, text="", bg=BUTTON_BG, fg="white",
                                      font=("Segoe UI", 11, "bold"), anchor="e",
                                      padx=8, pady=4)
        self.result_label.pack(side="right")

        # ── Table ──
        table_frame = ttk.Frame(content)
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        self.dep_table = ttk.Treeview(table_frame, columns=("name", "status", "version"),
                                       show="headings", height=14, style="Table.Treeview")

        self.dep_table.heading("name", text="依赖")
        self.dep_table.heading("status", text="是否完成安装")
        self.dep_table.heading("version", text="版本")

        self.dep_table.column("name", width=200, minwidth=120, anchor="center")
        self.dep_table.column("status", width=130, minwidth=100, anchor="center")
        self.dep_table.column("version", width=150, minwidth=80, anchor="center")

        self.dep_table.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                   command=self.dep_table.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.dep_table.configure(yscrollcommand=scrollbar.set)

        # ── Progress Section (below table) ──
        progress_frame = ttk.Frame(self.root)
        progress_frame.grid(row=1, column=0, sticky="ew", padx=PADDING_WINDOW, pady=(0, 4))

        self.progress_bar = ttk.Progressbar(progress_frame, mode="determinate",
                                             maximum=len(DEPENDENCIES))
        self.progress_bar.grid(row=0, column=0, sticky="ew")

        self.progress_label = tk.Label(progress_frame, text="", bg=BG,
                                        fg=TEXT_PRIMARY, font=("Segoe UI", 10),
                                        anchor="w", justify="left")
        self.progress_label.grid(row=1, column=0, sticky="w", pady=(4, 0))

        # ── Status Bar ──
        sep = tk.Frame(self.root, height=1, bg=BORDER)
        sep.grid(row=2, column=0, sticky="ew", pady=(0, 0))

        self.status_label = ttk.Label(self.root, text="就绪",
                                       style="Status.TLabel", anchor="center")
        self.status_label.grid(row=2, column=0, sticky="ew", padx=PADDING_WINDOW, pady=8)

    def _prepopulate_table(self):
        """Pre-fill the table with all dependencies."""
        for name in DEPENDENCIES:
            self.dep_table.insert("", "end", iid=name, values=(name, "待检测", "—"))

    def _update_row(self, name: str, status_icon: str, version: str):
        """Update a single row."""
        self.dep_table.item(name, values=(name, status_icon, version))

    # ── Activity Spinner ───────────────────────────────────

    def _start_spinner(self, message: str):
        """Start the animated activity label."""
        self._spinner_message = message
        self._spinner_idx = 0
        self._animate_spinner()

    def _animate_spinner(self):
        """Animate the spinner character."""
        frame = SPINNER[self._spinner_idx]
        self.status_label.configure(text=f"{frame} {self._spinner_message}")
        self._spinner_idx = (self._spinner_idx + 1) % len(SPINNER)
        self._spinner_after = self.root.after(150, self._animate_spinner)

    def _stop_spinner(self):
        """Stop the animated activity label."""
        if self._spinner_after:
            self.root.after_cancel(self._spinner_after)
            self._spinner_after = None

    # ── Status Management ──────────────────────────────────

    def _set_status(self, message: str):
        self.status_label.configure(text=message)

    def _set_progress(self, current: int, total: int, name: str, status=None):
        """Update progress bar and real-time results list."""
        self.progress_bar["value"] = current
        if status is not None:
            icon = STATUS_ICONS.get(status.value if hasattr(status, 'value') else str(status).lower(), "?")
            self._progress_lines.append(f"{icon} {name}")
            self.progress_label.configure(text="\n".join(self._progress_lines[-8:]))
        else:
            self.progress_label.configure(text=f"正在检测: {name} ({current}/{total})")

    # ── Detection ───────────────────────────────────────────

    def _auto_detect(self):
        """Run all detectors and update the table."""
        if getattr(self, "_detecting", False):
            return
        self._detecting = True
        self.results.clear()

        # Reset progress UI
        self._progress_lines.clear()
        self.progress_bar["value"] = 0
        self.progress_label.configure(text="")
        self.result_label.configure(text="", bg=BUTTON_BG)

        self.detect_btn.configure(style="Detecting.TButton")
        self.install_btn.configure(state="disabled")
        self.detect_btn.configure(state="disabled")
        self.download_install_btn.configure(state="disabled")
        self._set_status("正在检测环境，请稍候...")
        self._start_spinner("检测中")

        total = len(DETECTORS)

        def _detect():
            try:
                for i, det_cls in enumerate(DETECTORS, 1):
                    det = det_cls()
                    name = det.name
                    # Update "checking" status
                    self.root.after(0, lambda n=name, idx=i, t=total:
                        self._set_progress(idx, t, n, None))
                    status, detail = det.detect()
                    self.results.append((name, status, detail))
                    # Update with result
                    self.root.after(0, lambda n=name, s=status, idx=i, t=total:
                        self._set_progress(idx, t, n, s))
            except Exception as e:
                self.results.clear()
                self.root.after(0, lambda e=e: self._set_status(f"检测失败: {e}"))
            finally:
                self.root.after(0, self._on_detection_complete)

        threading.Thread(target=_detect, daemon=True).start()

    def _on_detection_complete(self):
        """Handle detection completion."""
        self._stop_spinner()
        self.detect_btn.configure(style="Action.TButton")

        # Update table rows with results + tags
        for name, status, detail in self.results:
            status_str = status.value if hasattr(status, 'value') else str(status).lower()
            status_icon = STATUS_ICONS.get(status_str, "—")
            version = detail if status_str == "ok" else "—"
            self._update_row(name, status_icon, version)
            tag = "ok" if status_str == "ok" else "issue"
            self.dep_table.item(name, tags=(tag,))

        self.dep_table.tag_configure("ok", foreground=OK_COLOR)
        self.dep_table.tag_configure("issue", foreground=MISSING_COLOR)

        # Determine button states
        has_issues = any(
            (s.value if hasattr(s, 'value') else str(s).lower()) in ("missing", "warning")
            for _, s, _ in self.results
        )

        if not self.results:
            self._set_status("检测完成，但未获取到任何结果")
            self.result_label.configure(text="检测失败", bg=MISSING_COLOR)
        elif not has_issues:
            self._set_status("所有依赖已就绪，无需安装")
            self.result_label.configure(text="检测完成：全部就绪", bg=OK_COLOR)
        else:
            self._set_status("检测到需要安装的组件，请点击「安装」")
            self.result_label.configure(text="部分需要安装", bg=WARNING_COLOR)

        self.install_btn.configure(state="normal" if has_issues else "disabled")
        self.detect_btn.configure(state="normal")
        self.download_install_btn.configure(state="normal" if has_issues else "disabled")
        self._detecting = False

    # ── Installation ───────────────────────────────────────

    def _start_install(self):
        """Handle install button click."""
        missing = [(n, s, d) for n, s, d in self.results
                    if (s.value if hasattr(s, 'value') else str(s).lower()) in ("missing", "warning")]
        if not missing:
            self._set_status("所有组件已安装完毕")
            return

        names = [n for n, _, _ in missing]
        if not messagebox.askokcancel("确认安装", f"即将安装以下组件：\n\n" + "\n".join(f"  · {n}" for n in names)):
            return

        self._do_install(missing)

    def _download_and_install(self):
        """Download and install all missing dependencies, including downloading bundled installers."""
        missing = [(n, s, d) for n, s, d in self.results
                    if (s.value if hasattr(s, 'value') else str(s).lower()) in ("missing", "warning")]
        if not missing:
            self._set_status("所有组件已安装完毕")
            return

        names = [n for n, _, _ in missing]
        if not messagebox.askokcancel("确认下载并安装",
                f"即将下载并安装以下组件：\n\n" + "\n".join(f"  · {n}" for n in names) +
                "\n\n（如果网络不可用，将尝试使用已捆绑的离线安装包）"):
            return

        self._do_install(missing)

    def _do_install(self, missing):
        """Run the install process."""
        self.install_btn.configure(state="disabled")
        self.detect_btn.configure(state="disabled")
        self.download_install_btn.configure(state="disabled")
        self._set_status("正在安装，请稍候...")

        threading.Thread(target=self._run_install, args=(missing,), daemon=True).start()

    def _run_install(self, missing):
        """Execute installation for each missing component."""
        from installers import NpmInstaller, WingetInstaller, DirectInstaller, BundledInstaller

        total = len(missing)
        for i, (name, status, detail) in enumerate(missing):
            self._start_spinner(f"正在安装 {name} ({i + 1}/{total})")
            self.root.after(0, lambda n=name, idx=i: self._set_status(f"正在安装 {n} ({idx + 1}/{total})..."))

            installers = []
            if name in ("npm", "Node.js", "Claude Code"):
                installers.append(NpmInstaller())
            installers.append(BundledInstaller(name))
            installers.append(WingetInstaller(name))
            installers.append(DirectInstaller(name))

            success = False
            for installer in installers:
                try:
                    if installer.install(None):
                        success = True
                        break
                except Exception:
                    pass

            if not success:
                self.root.after(0, lambda n=name: self._set_status(f"{n} 安装失败"))

        # Refresh after install
        self.root.after(0, lambda: self._set_status("安装完成，正在重新检测..."))
        self.root.after(0, lambda: self.install_btn.configure(state="normal"))
        self.root.after(0, lambda: self.detect_btn.configure(state="normal"))
        self.root.after(0, lambda: self.download_install_btn.configure(state="normal"))
        self.root.after(1000, lambda: self._auto_detect())


def main():
    root = tk.Tk()
    InstallerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
