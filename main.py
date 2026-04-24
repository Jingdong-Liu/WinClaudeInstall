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
    NodeDetector,
    GitDetector,
    PythonDetector,
    PowerShellDetector,
    BashDetector,
    NpmDetector,
    ClaudeCodeDetector,
    CCSwitchDetector,
]

DEPENDENCIES = [
    "Node.js",
    "Git",
    "PowerShell",
    "Python",
    "npm",
    "Bash",
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
FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_SECTION = ("Segoe UI", 11, "bold")
FONT_LOG = ("Cascadia Mono", 12, "normal")
FONT_LOG_FALLBACK = ("Consolas", 12, "normal")
FONT_BTN = ("Segoe UI", 14, "bold")
FONT_STATUS = ("Segoe UI", 11, "normal")
FONT_STEP = ("Segoe UI", 13, "normal")
FONT_STEP_NUM = ("Segoe UI", 12, "bold")

# ── Spacing ────────────────────────────────────────────────
PADDING_WINDOW = 16
CARD_GAP = 6

# ── Step Definitions ───────────────────────────────────────
STEPS = [
    ("1", "环境检测"),
    ("2", "安装"),
    ("3", "测试"),
]
STEP_ACTIVE_COLOR = BUTTON_BG
STEP_DONE_COLOR = OK_COLOR
STEP_DEFAULT_COLOR = TEXT_MUTED

# ── Status Display ─────────────────────────────────────────
STATUS_ICONS = {
    "ok": "✓",
    "missing": "✗",
    "warning": "⚠",
}


class InstallerApp:
    """主应用程序窗口."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Claude Code 一键安装器")
        self.root.geometry("960x620")
        self.root.minsize(800, 520)

        self.logger = setup_logger()
        self.results: list = []

        self._setup_style()
        self._build_ui()
        self._prepopulate_table()

    # ── Style ───────────────────────────────────────────────

    def _setup_style(self):
        """配置 ttk 样式."""
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame", background=BG)
        style.configure("Step.TFrame", background=BG)

        style.configure("Action.TButton", background=BUTTON_BG, foreground="white",
                        font=("Segoe UI", 13, "bold"), borderwidth=0, focuscolor="none",
                        padding=(16, 8))
        style.map("Action.TButton",
                  background=[("active", BUTTON_SHADOW), ("pressed", "#3730a3")],
                  foreground=[("active", "white")])

        style.configure("Status.TLabel", background=CARD_BG, foreground=TEXT_SECONDARY,
                        font=FONT_STATUS)

        style.configure("Table.Treeview", background=CARD_BG, foreground=TEXT_PRIMARY,
                        fieldbackground=CARD_BG, font=("Segoe UI", 11))
        style.configure("Table.Treeview.Heading", background=CARD_BG, foreground=TEXT_SECONDARY,
                        font=FONT_SECTION, borderwidth=0)
        style.map("Table.Treeview.Heading",
                  background=[("active", BG)])

    # ── UI Building ─────────────────────────────────────────

    def _build_ui(self):
        """构建新的三步引导式界面."""
        self.root.configure(background=BG)

        # Main layout: 2 rows (content, status bar)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=0)
        self.root.columnconfigure(0, weight=1)

        # ── Content Area ──
        content = ttk.Frame(self.root)
        content.grid(row=0, column=0, sticky="nsew", padx=PADDING_WINDOW, pady=PADDING_WINDOW)
        content.columnconfigure(0, weight=0)   # Left step panel (fixed width)
        content.columnconfigure(1, weight=1)   # Right main panel
        content.rowconfigure(0, weight=1)

        # ── Left Panel: Step Navigator ──
        self.step_frame = ttk.Frame(content, style="Step.TFrame", width=160)
        self.step_frame.grid(row=0, column=0, sticky="ns", padx=(0, 16))
        self.step_frame.pack_propagate(False)

        self._build_steps()

        # ── Right Panel ──
        self.main_frame = ttk.Frame(content)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.rowconfigure(0, weight=0)  # Buttons
        self.main_frame.rowconfigure(1, weight=1)  # Table
        self.main_frame.columnconfigure(0, weight=1)

        # Action buttons
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        self.detect_btn = ttk.Button(btn_frame, text="一键自动检测",
                                      style="Action.TButton", command=self._auto_detect)
        self.detect_btn.pack(side="left", padx=(0, 8))

        self.install_btn = ttk.Button(btn_frame, text="安装",
                                       style="Action.TButton", command=self._start_install)
        self.install_btn.pack(side="left")

        # Table
        table_frame = ttk.Frame(self.main_frame)
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        self.dep_table = ttk.Treeview(table_frame, columns=("name", "status", "version"),
                                       show="headings", height=14, style="Table.Treeview")

        self.dep_table.heading("name", text="依赖")
        self.dep_table.heading("status", text="是否完成安装")
        self.dep_table.heading("version", text="版本")

        self.dep_table.column("name", width=200, minwidth=120)
        self.dep_table.column("status", width=120, minwidth=100)
        self.dep_table.column("version", width=140, minwidth=80)

        self.dep_table.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                   command=self.dep_table.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.dep_table.configure(yscrollcommand=scrollbar.set)

        # ── Status Bar ──
        sep = tk.Frame(self.root, height=1, bg=BORDER)
        sep.grid(row=1, column=0, sticky="ew", pady=(0, 0))

        self.status_label = ttk.Label(self.root, text="就绪",
                                       style="Status.TLabel", anchor="center")
        self.status_label.grid(row=1, column=0, sticky="ew", padx=PADDING_WINDOW, pady=8)

    def _build_steps(self):
        """Render the 3-step navigator on the left panel."""
        self._step_circles = []
        self._step_labels = []

        for i, (num, label) in enumerate(STEPS):
            # Step row
            row = ttk.Frame(self.step_frame, style="Step.TFrame")
            row.pack(fill="x", pady=2)

            # Circle
            circle = tk.Label(row, text=num, bg=STEP_DEFAULT_COLOR, fg="white",
                              font=FONT_STEP_NUM, width=2, height=2, relief="flat")
            circle.pack(side="left", pady=2)
            self._step_circles.append(circle)

            # Label
            lbl = tk.Label(row, text=label, bg=BG, fg=TEXT_SECONDARY,
                           font=FONT_STEP, anchor="w")
            lbl.pack(side="left", padx=8, pady=6, fill="x", expand=True)
            self._step_labels.append(lbl)

            # Divider line (not after last step)
            if i < len(STEPS) - 1:
                tk.Frame(self.step_frame, height=1, bg=BORDER).pack(fill="x", padx=16, pady=4)

    def _prepopulate_table(self):
        """Pre-fill the table with dependency names before detection."""
        for name in DEPENDENCIES:
            self.dep_table.insert("", "end", iid=name, values=(name, "待检测", "—"))

    def _update_row(self, name: str, status_icon: str, version: str):
        """Update a specific row in the table by dependency name."""
        self.dep_table.item(name, values=(name, status_icon, version))

    # ── Step & Status Management ────────────────────────────

    def _set_step_active(self, index: int):
        """Mark a step as currently active."""
        for i, circle in enumerate(self._step_circles):
            if i < index:
                circle.configure(bg=STEP_DONE_COLOR, text="✓")
                self._step_labels[i].configure(fg=OK_COLOR)
            elif i == index:
                circle.configure(bg=STEP_ACTIVE_COLOR, text=STEPS[i][0])
                self._step_labels[i].configure(fg=TEXT_PRIMARY)
            else:
                circle.configure(bg=STEP_DEFAULT_COLOR, text=STEPS[i][0])
                self._step_labels[i].configure(fg=TEXT_MUTED)

    def _set_step_done(self, index: int):
        """Mark a step as completed."""
        circle = self._step_circles[index]
        circle.configure(bg=STEP_DONE_COLOR, text="✓")
        self._step_labels[index].configure(fg=OK_COLOR)

    def _set_status(self, message: str):
        """Update the status bar label."""
        self.status_label.configure(text=message)

    # ── Detection ───────────────────────────────────────────

    def _auto_detect(self):
        """Run all detectors and update the table."""
        if getattr(self, "_detecting", False):
            return
        self._detecting = True
        self.results.clear()
        self.install_btn.configure(state="disabled")
        self.detect_btn.configure(state="disabled")
        self._set_step_active(0)
        self._set_status("正在检测环境，请稍候...")

        def _detect():
            try:
                for det_cls in DETECTORS:
                    det = det_cls()
                    status, detail = det.detect()
                    self.results.append((det.name, status, detail))

                self.root.after(0, self._update_tree)
                self.root.after(0, self._on_detection_complete)
            except Exception as e:
                self.root.after(0, lambda e=e: self._set_status(f"检测失败: {e}"))
                self.root.after(0, self._on_detection_complete)

        threading.Thread(target=_detect, daemon=True).start()

    def _on_detection_complete(self):
        """Handle detection completion."""
        has_issues = any(
            (s.value if hasattr(s, 'value') else str(s).lower()) in ("missing", "warning")
            for _, s, _ in self.results
        )
        if not has_issues:
            self._set_step_done(0)
            self._set_status("所有依赖已就绪，无需安装")
        else:
            self._set_step_done(0)
            self._set_status("检测到需要安装的组件，请点击「安装」")
        self.install_btn.configure(state="normal" if has_issues else "disabled")
        self.detect_btn.configure(state="normal")
        self._detecting = False

    def _update_tree(self):
        """Update table rows with detector results."""
        for name, status, detail in self.results:
            status_str = status.value if hasattr(status, 'value') else str(status).lower()
            status_icon = STATUS_ICONS.get(status_str, "—")
            version = detail if status_str == "ok" else "—"
            self._update_row(name, status_icon, version)

    # ── Installation ────────────────────────────────────────

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

        self.install_btn.configure(state="disabled")
        self.detect_btn.configure(state="disabled")
        self._set_step_active(1)
        self._set_status("正在安装，请稍候...")

        threading.Thread(target=self._run_install, args=(missing,), daemon=True).start()

    def _run_install(self, missing):
        """Execute installation for each missing component."""
        from installers import NpmInstaller, WingetInstaller, DirectInstaller, BundledInstaller

        total = len(missing)
        for i, (name, status, detail) in enumerate(missing):
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
                except Exception as e:
                    pass

            if not success:
                self.root.after(0, lambda n=name: self._set_status(f"{n} 安装失败"))

        # Refresh after install
        self.root.after(0, lambda: self._set_step_done(1))
        self.root.after(0, lambda: self._set_status("安装完成，正在重新检测..."))
        self.root.after(0, lambda: self.install_btn.configure(state="normal"))
        self.root.after(0, lambda: self.detect_btn.configure(state="normal"))
        self.root.after(1000, lambda: self._auto_detect())


def main():
    root = tk.Tk()
    InstallerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
