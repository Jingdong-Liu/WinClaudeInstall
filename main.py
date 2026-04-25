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

FONT_BTN = ("Segoe UI", 14, "bold")
FONT_STATUS = ("Segoe UI", 11, "normal")
FONT_SECTION = ("Segoe UI", 11, "bold")

PADDING_WINDOW = 16

STATUS_ICONS = {
    "ok": "✓",
    "missing": "✗",
    "warning": "⚠",
}

SPINNER = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

DETECT_CMDS = {
    "PowerShell": ["pwsh -Command '$PSVersionTable.PSVersion.ToString()'",
                   "powershell -Command '$PSVersionTable.PSVersion.ToString()'"],
    "Python": "python --version",
    "Node.js": "node --version",
    "Git": "git --version",
    "Bash": "bash --version",
    "npm": "npm --version",
    "Claude Code": "claude --version",
    "CC-Switch": "npm list -g cc-switch",
}


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
        self._row_buttons: dict = {}  # name -> button widget

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
                        font=FONT_BTN, borderwidth=1, focuscolor="none",
                        padding=(20, 10), relief="flat")
        style.map("Action.TButton",
                  background=[("active", BUTTON_SHADOW), ("pressed", "#3730a3"),
                              ("disabled", "#93a1f6")],
                  foreground=[("active", "white"), ("disabled", "#e2e8f0")],
                  relief=[("pressed", "sunken"), ("active", "flat"), ("disabled", "flat")])

        style.configure("Status.TLabel", background=CARD_BG, foreground=TEXT_SECONDARY,
                        font=FONT_STATUS)

        style.configure("Install.TButton", background=BUTTON_BG, foreground="white",
                        font=("Segoe UI", 9, "normal"), borderwidth=0, focuscolor="none",
                        padding=(6, 3))
        style.map("Install.TButton",
                  background=[("active", BUTTON_SHADOW), ("pressed", "#3730a3")],
                  foreground=[("active", "white")])

        style.configure("Detecting.TButton", background=WARNING_COLOR, foreground="white",
                        font=FONT_BTN, borderwidth=1, focuscolor="none",
                        padding=(20, 10), relief="flat")
        style.map("Detecting.TButton",
                  background=[("active", "#d97706"), ("disabled", "#fcd34d")],
                  foreground=[("active", "white")],
                  relief=[("pressed", "sunken"), ("active", "flat"), ("disabled", "flat")])

        style.configure("Table.Treeview", background=CARD_BG, foreground=TEXT_PRIMARY,
                        fieldbackground=CARD_BG, font=("Segoe UI", 11))
        style.configure("Table.Treeview.Heading", background=CARD_BG, foreground=TEXT_SECONDARY,
                        font=FONT_SECTION, borderwidth=0)
        style.map("Table.Treeview.Heading",
                  background=[("active", BG)])

    # ── UI Building ─────────────────────────────────────────

    def _build_ui(self):
        """构建主界面."""
        self.root.configure(background=BG)

        # Main layout: 2 rows (content + terminal split, progress)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=0)  # progress
        self.root.columnconfigure(0, weight=1)

        # ── Content Area (table + terminal, split with PanedWindow) ──
        content = ttk.Frame(self.root)
        content.grid(row=0, column=0, sticky="nsew", padx=PADDING_WINDOW, pady=PADDING_WINDOW)
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=1)

        # PanedWindow for table/terminal split
        self.paned = tk.PanedWindow(content, orient="vertical",
                                     bg=BG, sashwidth=6, sashrelief="raised",
                                     cursor="sb_v_double_arrow")
        self.paned.grid(row=0, column=0, sticky="nsew")

        # Top pane: button row + table
        top_frame = tk.Frame(content, bg=BG)
        self._build_button_row(top_frame)
        self._build_table_area(top_frame)
        self.paned.add(top_frame, minsize=200)

        # Bottom pane: terminal
        terminal_pane = tk.Frame(content, bg=BG)
        self._build_terminal(terminal_pane)
        self.paned.add(terminal_pane, minsize=60)

        # ── Progress Section (full width) ──
        progress_frame = tk.Frame(self.root, bg=BG)
        progress_frame.grid(row=1, column=0, sticky="ew", padx=PADDING_WINDOW, pady=(0, 8))

        self.progress_bar = ttk.Progressbar(progress_frame, mode="determinate",
                                             maximum=len(DEPENDENCIES))
        self.progress_bar.pack(fill="x", side="top")

        # Cartoon dog canvas overlayed on progress bar tip
        self.dog_canvas = tk.Canvas(progress_frame, width=24, height=22,
                                     bg=BG, highlightthickness=0, bd=0)
        self._draw_dog()
        self.dog_canvas.place(x=0, y=0, width=24, height=22)

        self.progress_label = tk.Label(progress_frame, text="", bg=BG,
                                        fg=TEXT_PRIMARY, font=("Segoe UI", 10),
                                        anchor="w", justify="left")
        self.progress_label.pack(fill="x", side="top", pady=(4, 0))

        # Reposition dog canvas when progress bar updates
        self.progress_bar.bind("<Configure>", self._reposition_dog)
        # Also reposition after a short delay for initial layout
        self.progress_bar.after(200, self._reposition_dog)

    def _draw_dog(self):
        """Draw a cartoon dog head (WeChat style) on the dog canvas."""
        c = self.dog_canvas
        # Dog head - round tan face
        c.create_oval(2, 2, 22, 20, fill="#e8b960", outline="#c4943e", width=1)
        # Left ear - floppy triangle
        c.create_polygon(2, 6, 0, 14, 6, 8, fill="#c4943e", outline="#a07830", width=1)
        # Right ear - floppy triangle
        c.create_polygon(22, 6, 24, 14, 18, 8, fill="#c4943e", outline="#a07830", width=1)
        # Eyes - two dots with eyebrows (doge style)
        c.create_oval(7, 8, 10, 11, fill="#333", outline="")
        c.create_oval(14, 8, 17, 11, fill="#333", outline="")
        # Small eyebrows (the classic doge expression)
        c.create_line(6, 7, 11, 6, fill="#333", width=1)
        c.create_line(13, 6, 18, 7, fill="#333", width=1)
        # Nose
        c.create_oval(10, 12, 14, 15, fill="#333", outline="")
        # Mouth - simple curve
        c.create_arc(9, 14, 15, 19, start=180, extent=180, outline="#333", width=1)

    def _build_button_row(self, parent):
        """Build the button row at top of content area."""
        btn_frame = tk.Frame(parent, bg=BG)
        btn_frame.pack(fill="x", pady=(0, 8))

        # Detect button - standalone pill
        detect_bg = tk.Frame(btn_frame, bg=BUTTON_BG, bd=0, relief="flat", padx=12, pady=4)
        detect_bg.pack(side="left", padx=0)
        self.detect_btn = tk.Button(detect_bg, text=" 一键自动检测 ",
                                     bg=BUTTON_BG, fg="white", font=FONT_BTN,
                                     activebackground=BUTTON_SHADOW, activeforeground="white",
                                     bd=0, cursor="hand2", relief="flat",
                                     command=self._auto_detect)
        self.detect_btn.pack(side="left")

        # White gap between buttons
        tk.Label(btn_frame, text="   ", bg="white").pack(side="left", padx=0)

        # Install button - standalone pill
        install_bg = tk.Frame(btn_frame, bg=BUTTON_BG, bd=0, relief="flat", padx=12, pady=4)
        install_bg.pack(side="left", padx=0)
        self.install_btn = tk.Button(install_bg, text=" 一键安装 ",
                                      bg=BUTTON_BG, fg="white", font=FONT_BTN,
                                      activebackground=BUTTON_SHADOW, activeforeground="white",
                                      bd=0, cursor="hand2", relief="flat",
                                      command=self._start_install)
        self.install_btn.pack(side="left")

        # Result label (right-aligned, subtle - no background)
        self.result_label = tk.Label(btn_frame, text="", bg=BG,
                                      font=("Segoe UI", 11, "bold"), anchor="e")
        self.result_label.pack(side="right", fill="x", expand=True)

    def _reposition_dog(self, event=None):
        """Move dog canvas to the tip of the progress bar fill, keeping it visible."""
        try:
            bar_w = self.progress_bar.winfo_width()
            bar_h = self.progress_bar.winfo_height()
            value = self.progress_bar["value"]
            max_val = self.progress_bar["maximum"]
            if max_val == 0 or bar_w <= 0:
                return
            ratio = value / max_val
            dog_w = 24
            dog_h = 22
            # Position at the tip of the fill
            dog_x = int(ratio * bar_w - dog_w // 2)
            # Keep dog visible: clamp so right edge isn't clipped by window border
            max_x = bar_w - dog_w - 2
            dog_x = min(dog_x, max_x)
            dog_x = max(dog_x, 0)
            # Vertically centered on the progress bar
            dog_y = max(0, (bar_h - dog_h) // 2)
            self.dog_canvas.place(x=dog_x, y=dog_y, width=dog_w, height=dog_h)
        except Exception:
            pass

    def _build_table_area(self, parent):
        """Build the dependency table with per-row install buttons as 4th column."""
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill="both", expand=True)

        # Treeview columns: 依赖, 状态, 版本, 操作
        self.dep_table = ttk.Treeview(table_frame, columns=("name", "status", "version", "action"),
                                       show="headings", height=14, style="Table.Treeview")

        self.dep_table.heading("name", text="依赖")
        self.dep_table.heading("status", text="是否完成安装")
        self.dep_table.heading("version", text="版本")
        self.dep_table.heading("action", text="操作")

        self.dep_table.column("name", width=160, minwidth=90, anchor="center")
        self.dep_table.column("status", width=120, minwidth=80, anchor="center")
        self.dep_table.column("version", width=140, minwidth=70, anchor="center")
        self.dep_table.column("action", width=110, minwidth=70, anchor="center")

        self.dep_table.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical",
                                   command=self.dep_table.yview)
        scrollbar.pack(side="right", fill="y")
        self.dep_table.configure(yscrollcommand=scrollbar.set)

        self._row_buttons: dict = {}  # iid -> button widget

    def _build_terminal(self, parent):
        """Build the terminal output section."""
        terminal_header = tk.Label(parent, text="检测过程", bg=BG,
                                    fg=TEXT_SECONDARY, font=("Segoe UI", 10, "bold"),
                                    anchor="w")
        terminal_header.pack(fill="x", pady=(8, 0))

        terminal_inner = tk.Frame(parent, bg="#1e1e1e", bd=1, relief="sunken")
        terminal_inner.pack(fill="both", expand=True, pady=(4, 0))

        self.terminal_text = tk.Text(terminal_inner, bg="#1e1e1e", fg="#d4d4d4",
                                      font=("Cascadia Code", 10, "normal"),
                                      bd=0, highlightthickness=0, wrap="word",
                                      state="disabled", height=6)
        self.terminal_text.pack(fill="both", expand=True)

        # Pre-configure terminal text tags
        self.terminal_text.tag_configure("info", foreground="#569cd6")
        self.terminal_text.tag_configure("ok", foreground="#4ec9b0")
        self.terminal_text.tag_configure("error", foreground="#f44747")
        self.terminal_text.tag_configure("command", foreground="#ce9178")
        self.terminal_text.tag_configure("normal", foreground="#d4d4d4")
        self.terminal_text.tag_configure("detail", foreground="#6a9955")

    def _prepopulate_table(self):
        """Pre-fill the table with all dependencies."""
        for name in DEPENDENCIES:
            self.dep_table.insert("", "end", iid=name, values=(name, "待检测", "—", "—"))

    def _update_row(self, name: str, status_icon: str, version: str):
        """Update a single row."""
        action_text = self._row_buttons.get(name, "—")
        self.dep_table.item(name, values=(name, status_icon, version, action_text))

    # ── Activity Spinner ───────────────────────────────────

    def _start_spinner(self, message: str):
        """Start the animated activity label."""
        self._spinner_message = message
        self._spinner_idx = 0
        self._animate_spinner()

    def _animate_spinner(self):
        """Animate the spinner character."""
        frame = SPINNER[self._spinner_idx]
        self.result_label.configure(text=f"{frame} {self._spinner_message}")
        self._spinner_idx = (self._spinner_idx + 1) % len(SPINNER)
        self._spinner_after = self.root.after(150, self._animate_spinner)

    def _stop_spinner(self):
        """Stop the animated activity label."""
        if self._spinner_after:
            self.root.after_cancel(self._spinner_after)
            self._spinner_after = None

    def _set_progress(self, current: int, total: int, name: str, status=None, detail=""):
        """Update progress bar, terminal output, and table in real-time."""
        self.progress_bar["value"] = current - 1 if current > 0 else 0
        self.root.after(10, self._reposition_dog)
        if status is not None:
            status_str = status.value if hasattr(status, 'value') else str(status).lower()
            status_icon = STATUS_ICONS.get(status_str, "—")
            version = detail if status_str == "ok" else "—"
            self._update_row(name, status_icon, version)

            icon = STATUS_ICONS.get(status_str, "?")
            detail_text = f"{name} → {version}" if status_str == "ok" else f"{name} → 未安装"
            self._write_terminal(f"  {icon} {detail_text}\n",
                                 color="ok" if status_str == "ok" else "error")
            # Update progress label with completed detection
            self.progress_label.configure(text=f"正在检测: {name} ({current}/{total})")
        else:
            self.progress_label.configure(text=f"正在检测: {name} ({current}/{total})")
            cmd = DETECT_CMDS.get(name, "")
            if isinstance(cmd, list):
                cmd = cmd[0]
            self._write_terminal(f"> {cmd}\n", color="command")
            self._write_terminal(f"  检测 {name}...\n", color="info")

    def _write_terminal(self, text: str, color: str = "normal"):
        """Append text to the terminal widget with color."""
        self.terminal_text.configure(state="normal")
        self.terminal_text.insert("end", text, color)
        self.terminal_text.see("end")
        self.terminal_text.configure(state="disabled")

    def _clear_terminal(self):
        """Clear the terminal output."""
        self.terminal_text.configure(state="normal")
        self.terminal_text.delete("1.0", "end")
        self.terminal_text.configure(state="disabled")

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
        self.result_label.configure(text="", fg=BG)
        self._clear_terminal()

        self.detect_btn.configure(bg=WARNING_COLOR, state="disabled")

        self._start_spinner("检测中")

        total = len(DETECTORS)

        def _detect():
            try:
                for i, det_cls in enumerate(DETECTORS, 1):
                    det = det_cls()
                    name = det.name
                    self.root.after(0, lambda n=name, idx=i, t=total:
                        self._set_progress(idx, t, n, None))
                    status, detail = det.detect()
                    self.results.append((name, status, detail))
                    self.root.after(0, lambda n=name, s=status, d=detail, idx=i, t=total:
                        self._set_progress(idx, t, n, s, d))
            except Exception as e:
                import traceback
                err_msg = traceback.format_exc()
                self.logger.error(f"Detection error: {err_msg}")
                self.results.clear()
                self.root.after(0, self._on_detection_complete)
                return
            self.root.after(0, self._on_detection_complete)

        threading.Thread(target=_detect, daemon=True).start()

    def _on_detection_complete(self):
        """Handle detection completion."""
        self._stop_spinner()
        self.detect_btn.configure(bg=BUTTON_BG)

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

        # Fill progress bar to 100%
        self.progress_bar["value"] = len(DEPENDENCIES)
        self.root.after(10, self._reposition_dog)

        if not self.results:
            self.result_label.configure(text="检测失败", fg=MISSING_COLOR)
            self.progress_label.configure(text="检测失败", fg=MISSING_COLOR)
        elif not has_issues:
            self.result_label.configure(text="✓ 检测完成：全部就绪", fg=OK_COLOR)
            self.progress_label.configure(text="✓ 检测完成，所有依赖已就绪", fg=OK_COLOR)
        else:
            missing_count = sum(1 for _, s, _ in self.results
                                if (s.value if hasattr(s, 'value') else str(s).lower()) in ("missing", "warning"))
            self.result_label.configure(text=f"{missing_count} 项需要安装", fg=WARNING_COLOR)
            self.progress_label.configure(text=f"检测完成 — {missing_count} 项未安装，可点击行内按钮单独安装", fg=WARNING_COLOR)

        # Update per-row install buttons
        self._update_row_buttons(has_issues)

        self.detect_btn.configure(state="normal")
        self._detecting = False

    def _update_row_buttons(self, has_issues):
        """Create/update per-row install buttons as Treeview window widgets."""
        # Destroy old buttons
        for btn in self._row_buttons.values():
            btn.destroy()
        self._row_buttons.clear()

        for name, status, detail in self.results:
            status_str = status.value if hasattr(status, 'value') else str(status).lower()
            btn_text = "安装" if status_str in ("missing", "warning") else "重装"
            btn = ttk.Button(self.dep_table, text=btn_text,
                              style="Install.TButton",
                              command=lambda n=name: self._install_single(n))
            # Store reference for scroll sync
            self._row_buttons[name] = btn
            self.dep_table.set(name, "action", btn_text)

        # Bind scroll to reposition window widgets
        self.dep_table.bind("<Configure>", self._reposition_buttons, add=True)
        self.dep_table.bind("<Map>", self._reposition_buttons, add=True)
        # Initial positioning
        self.dep_table.after(100, self._reposition_buttons)

    def _reposition_buttons(self, event=None):
        """Reposition window widgets in the Treeview action column."""
        for name, btn in self._row_buttons.items():
            try:
                bbox = self.dep_table.bbox(name, "action")
                if bbox:
                    x, y, width, height = bbox
                    btn.place(x=x, y=y, width=width, height=height)
            except Exception:
                pass

    def _install_single(self, name: str):
        """Install a single dependency."""
        from installers import NpmInstaller, WingetInstaller, DirectInstaller, BundledInstaller

        # Disable the row button
        if name in self._row_buttons:
            self._row_buttons[name].configure(state="disabled")

        self.detect_btn.configure(state="disabled")
        self._start_spinner(f"正在安装 {name}...")

        def _install():
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

            if success:
                self.root.after(0, lambda: self._stop_spinner())
            else:
                self.root.after(0, lambda: self._stop_spinner())

            self.root.after(0, lambda: self.detect_btn.configure(state="normal"))
            self.root.after(1500, lambda: self._auto_detect())

        threading.Thread(target=_install, daemon=True).start()

    # ── Installation ───────────────────────────────────────

    def _start_install(self):
        """Handle install button click."""
        missing = [(n, s, d) for n, s, d in self.results
                    if (s.value if hasattr(s, 'value') else str(s).lower()) in ("missing", "warning")]
        if not missing:
            self.result_label.configure(text="所有组件已安装完毕", fg=OK_COLOR)
            return

        names = [n for n, _, _ in missing]
        if not messagebox.askokcancel("确认安装", f"即将安装以下组件：\n\n" + "\n".join(f"  · {n}" for n in names)):
            return

        self._do_install(missing)

    def _do_install(self, missing):
        """Run the install process."""
        self.detect_btn.configure(state="disabled")
        self._start_spinner("正在安装，请稍候...")

        threading.Thread(target=self._run_install, args=(missing,), daemon=True).start()

    def _run_install(self, missing):
        """Execute installation for each missing component."""
        from installers import NpmInstaller, WingetInstaller, DirectInstaller, BundledInstaller

        total = len(missing)
        for i, (name, status, detail) in enumerate(missing):
            self._start_spinner(f"正在安装 {name} ({i + 1}/{total})")

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
                self.root.after(0, self._stop_spinner)

        self.root.after(0, self._stop_spinner)
        self.root.after(0, lambda: self.detect_btn.configure(state="normal"))
        self.root.after(1000, lambda: self._auto_detect())


def main():
    root = tk.Tk()
    InstallerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
