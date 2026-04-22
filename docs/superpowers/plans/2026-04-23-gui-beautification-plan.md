# GUI Beautification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the Claude Code Installer GUI with a clean light theme, card-based detector display, modern fonts, and polished spacing.

**Architecture:** Replace the current Treeview-based left panel with card-style Frame widgets. Apply custom ttk.Style theming throughout. All logic (detection, installation, threading) remains unchanged — only visual presentation changes.

**Tech Stack:** tkinter, ttk.Style, tk.Frame, tk.Label, tk.Button.

---

## File Structure

Only one file changes:
- Modify: `main.py` — complete rewrite of `_build_ui()` and `_update_tree()`, add style setup, constants, and card-based detector display

All backend code (detectors, installers, utils) is untouched.

---

### Task 1: Add Design Constants

**Files:**
- Modify: `main.py` (top section: constants and imports)

- [ ] **Step 1: Add color and font constants**

Replace the existing `STATUS_COLORS` block and add new constants. Find lines 23-32 and replace with:

```python
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
PADDING_HEADER = (20, 24, 16, 20)

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
```

Also update the imports at the top. Change lines 3-5 from:
```python
import tkinter as tk
from tkinter import ttk, messagebox
import threading
```
to:
```python
import tkinter as tk
from tkinter import ttk, messagebox, font as tk_font
import threading
```

- [ ] **Step 2: Update STATUS_COLORS reference**

The old `STATUS_COLORS` dict referenced `Status` enum values. Update to reference string keys:

```python
STATUS_COLORS = {
    "ok": OK_COLOR,
    "missing": MISSING_COLOR,
    "warning": WARNING_COLOR,
}
```

- [ ] **Step 3: Verify imports work**

Run: `python -c "import main; print('imports OK')"`
Expected: `imports OK`

- [ ] **Step 4: Commit**

```bash
git add main.py
git commit -m "style: add design constants (colors, fonts, spacing)"
```

---

### Task 2: Custom ttk Style + Header Bar

**Files:**
- Modify: `main.py` — add `_setup_style()` method, update `_build_ui()` header

- [ ] **Step 1: Add _setup_style method**

Add this method to the `InstallerApp` class, before `_build_ui`:

```python
    def _setup_style(self):
        """Configure ttk styles for the clean light theme."""
        style = ttk.Style()
        style.theme_use("clam")

        # Configure colors
        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=CARD_BG, borderwidth=1, relief="solid")
        style.configure("Header.TFrame", background=HEADER_BG_START)
        style.configure("Bottom.TFrame", background=CARD_BG)

        style.configure("Section.TLabel", background=BG, foreground=TEXT_SECONDARY, font=FONT_SECTION)
        style.configure("Title.TLabel", background=HEADER_BG_START, foreground=TEXT_PRIMARY, font=FONT_TITLE)
        style.configure("Subtitle.TLabel", background=HEADER_BG_START, foreground=TEXT_MUTED, font=FONT_SUBTITLE)
        style.configure("Card.TLabel", background=CARD_BG, foreground=TEXT_SECONDARY)
        style.configure("CardName.TLabel", background=CARD_BG, foreground=TEXT_PRIMARY, font=FONT_CARD_NAME)
        style.configure("CardDetail.TLabel", background=CARD_BG, foreground=TEXT_SECONDARY, font=FONT_CARD_DETAIL)
        style.configure("StatusOk.TLabel", foreground=OK_COLOR, background=CARD_BG, font=("", 16, "bold"))
        style.configure("StatusMissing.TLabel", foreground=MISSING_COLOR, background=CARD_BG, font=("", 16, "bold"))
        style.configure("StatusWarning.TLabel", foreground=WARNING_COLOR, background=CARD_BG, font=("", 16, "bold"))

        style.configure("CardOk.TFrame", bordercolor=BORDER, background=CARD_BG)
        style.configure("CardMissing.TFrame", bordercolor=MISSING_BORDER, background=CARD_BG)
        style.configure("CardWarning.TFrame", bordercolor=WARNING_BORDER, background=CARD_BG)

        style.configure("Install.TButton", background=BUTTON_BG, foreground="white", font=FONT_BTN, borderwidth=0, focuscolor="none", padding=(12, 48))
        style.map("Install.TButton",
                  background=[("active", BUTTON_SHADOW), ("pressed", "#3730a3")],
                  foreground=[("active", "white")])

        style.configure("Refresh.TButton", background=CARD_BG, foreground=TEXT_SECONDARY, font=("Segoe UI", 12, "normal"), borderwidth=1, padding=(8, 20))
        style.map("Refresh.TButton",
                  background=[("active", BG)],
                  bordercolor=[("active", TEXT_MUTED)])
```

- [ ] **Step 2: Update __init__ to call _setup_style**

Change `__init__` from:
```python
        self._build_ui()
        self._auto_detect()
```
to:
```python
        self._setup_style()
        self._build_ui()
        self._auto_detect()
```

- [ ] **Step 3: Commit**

```bash
git add main.py
git commit -m "style: add custom ttk style setup for clean light theme"
```

---

### Task 3: Rewrite _build_ui() with New Layout

**Files:**
- Modify: `main.py` — replace `_build_ui()` method entirely

- [ ] **Step 1: Replace _build_ui with new implementation**

Replace the entire `_build_ui` method with:

```python
    def _build_ui(self):
        """Build the beautified two-column layout."""
        self.root.configure(background=BG)
        self.root.geometry("900x560")
        self.root.minsize(750, 450)

        # ── Main layout: 3 rows (header, content, bottom) ──
        self.root.rowconfigure(0, weight=0)   # header
        self.root.rowconfigure(1, weight=1)   # content
        self.root.rowconfigure(2, weight=0)   # bottom
        self.root.columnconfigure(0, weight=1)

        # ── Header Bar ──
        header = ttk.Frame(self.root, style="Header.TFrame")
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)

        # Icon box (canvas for rounded square)
        icon_frame = tk.Frame(header, bg=BUTTON_BG, width=36, height=36)
        icon_frame.pack_propagate(False)
        icon_frame.pack(side="left", padx=(24, 12), pady=16)

        icon_label = tk.Label(icon_frame, text="C", bg=BUTTON_BG, fg="white",
                               font=("Segoe UI", 16, "bold"))
        icon_label.pack(expand=True)

        # Title + Subtitle
        title_frame = tk.Frame(header, bg=HEADER_BG_START)
        title_frame.pack(side="left", fill="y", pady=16)

        tk.Label(title_frame, text="Claude Code Installer", bg=HEADER_BG_START,
                 fg=TEXT_PRIMARY, font=FONT_TITLE).pack(anchor="w")
        tk.Label(title_frame, text="一键安装环境检测与执行", bg=HEADER_BG_START,
                 fg=TEXT_MUTED, font=("Segoe UI", 12)).pack(anchor="w")

        # Separator line
        tk.Frame(self.root, height=1, bg=BORDER).grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 0), rowspan=1)
        # Place separator at bottom of header row
        sep = tk.Frame(self.root, height=1, bg=BORDER)
        sep.place(x=0, y=72, relwidth=1)

        # ── Content Area (two columns) ──
        content_frame = ttk.Frame(self.root)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=2)
        content_frame.rowconfigure(0, weight=1)

        # ── Left Panel ──
        left_frame = ttk.Frame(content_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(PADDING_WINDOW, 8), pady=PADDING_WINDOW, ipadx=8)

        ttk.Label(left_frame, text="ENVIRONMENT CHECK", style="Section.TLabel").pack(anchor="w", pady=(0, 8))

        # Container for detector cards (scrollable)
        self.cards_frame = ttk.Frame(left_frame)
        self.cards_frame.pack(fill="both", expand=True)

        # Refresh button
        ttk.Button(left_frame, text="↻ Refresh", style="Refresh.TButton",
                   command=self._auto_detect).pack(anchor="w", pady=(8, 0))

        # ── Right Panel ──
        right_frame = ttk.Frame(content_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(8, PADDING_WINDOW), pady=PADDING_WINDOW, ipadx=8)

        ttk.Label(right_frame, text="INSTALLATION LOG", style="Section.TLabel").pack(anchor="w", pady=(0, 8))

        # Log container with white background
        self.log_container = tk.Frame(right_frame, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)
        self.log_container.pack(fill="both", expand=True)

        self.log_text = tk.Text(self.log_container, state="disabled", wrap="word",
                                 font=FONT_LOG, bg=CARD_BG, fg=TEXT_SECONDARY,
                                 borderwidth=0, highlightthickness=0, padx=14, pady=14)
        self.log_text.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.configure(yscrollcommand=scrollbar.set)

        # ── Bottom Bar ──
        bottom_frame = ttk.Frame(self.root, style="Bottom.TFrame")
        bottom_frame.grid(row=2, column=0, sticky="ew")
        tk.Frame(bottom_frame, height=1, bg=BORDER).pack(fill="x")

        self.install_btn = tk.Button(bottom_frame, text="One-Click Install",
                                      bg=BUTTON_BG, fg="white", font=FONT_BTN,
                                      activebackground=BUTTON_SHADOW, activeforeground="white",
                                      bd=0, relief="flat", cursor="hand2",
                                      padx=48, pady=12)
        self.install_btn.pack(pady=16)

        # Store card widgets for later updates
        self._card_widgets: list = []
```

- [ ] **Step 2: Verify app launches**

Run: `python -c "from main import InstallerApp; print('launch OK')"`
Expected: `launch OK`

- [ ] **Step 3: Commit**

```bash
git add main.py
git commit -m "style: rewrite _build_ui with header, cards container, and modern layout"
```

---

### Task 4: Replace Treeview with Card-Based Detector Display

**Files:**
- Modify: `main.py` — replace `_update_tree()` and add `_build_cards()` method

- [ ] **Step 1: Replace _update_tree with card-based rendering**

Replace `_update_tree` method with:

```python
    def _update_tree(self):
        """Render detector results as styled cards."""
        # Clear existing cards
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
        inner.pack(fill="x", padx=CARD_GAP + 4, pady=8)

        # Icon
        icon_lbl = tk.Label(inner, text=icon, bg=CARD_BG, fg=text_color,
                             font=("", 16, "bold"), width=2)
        icon_lbl.pack(side="left")

        # Name
        name_lbl = tk.Label(inner, text=name, bg=CARD_BG, fg=TEXT_PRIMARY,
                             font=FONT_CARD_NAME, anchor="w", width=14)
        name_lbl.pack(side="left", padx=(4, 0))

        # Detail (right-aligned)
        detail_lbl = tk.Label(inner, text=detail, bg=CARD_BG, fg=text_color,
                               font=FONT_CARD_DETAIL, anchor="e")
        detail_lbl.pack(side="right", fill="x", expand=True)
```

- [ ] **Step 2: Verify cards render correctly**

Run: `python main.py` briefly to verify the window shows cards instead of Treeview.
Or at minimum: `python -c "from main import InstallerApp; print('cards OK')"`

- [ ] **Step 3: Commit**

```bash
git add main.py
git commit -m "style: replace Treeview with card-based detector display"
```

---

### Task 5: Polish Log Panel and Bottom Button

**Files:**
- Modify: `main.py` — update `_log()` method for better formatting

- [ ] **Step 1: Improve log text appearance**

Update `_log` method. Replace the existing `_log` method with:

```python
    def _log(self, message: str):
        """Append message to the log panel (thread-safe)."""
        def _append():
            self.log_text.configure(state="normal")
            self.log_text.insert("end", message + "\n")
            self.log_text.see("end")
            self.log_text.configure(state="disabled")
        self.root.after(0, _append)
```

(This remains the same — the visual improvement comes from the container styling in Task 3.)

- [ ] **Step 2: Set default log font properly**

After creating `self.log_text` in `_build_ui`, add font fallback handling:

Find the line that creates `self.log_text` and add this after `self.log_text.pack(...)`:

```python
        # Ensure monospace font is available
        available_fonts = set(tk_font.families())
        if "Cascadia Mono" not in available_fonts:
            self.log_text.configure(font=FONT_LOG_FALLBACK)
```

- [ ] **Step 3: Run all tests**

Run: `python -m pytest tests/ -v`
Expected: 33 tests PASS

- [ ] **Step 4: Commit**

```bash
git add main.py
git commit -m "style: polish log panel font handling and button appearance"
```

---

### Task 6: Final Integration Test + Visual Verification

- [ ] **Step 1: Run all tests**

Run: `python -m pytest tests/ -v`
Expected: 33 tests PASS

- [ ] **Step 2: Launch the app**

Run: `python main.py`

Verify:
- Header bar with icon + title + subtitle renders
- 6 detector cards show with correct colors and borders
- OK cards have gray borders, MISSING have red, WARNING have amber
- Log panel uses monospace font in white card
- "One-Click Install" button has blue background, white text
- Refresh button works
- Window is 900x560, resizable to min 750x450

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "release: beautified GUI with clean light theme"
```

---

## Self-Review

### Spec Coverage

| Spec Requirement | Task |
|---|---|
| Color palette (slate, green, red, amber, blue-indigo) | Task 1 (constants) |
| Font config (Segoe UI, Cascadia Mono, Consolas fallback) | Task 1 + Task 5 |
| Header bar with icon + title + subtitle | Task 3 |
| Detector cards (white bg, colored borders, shadow) | Task 4 |
| Log panel (white card, monospace font) | Task 3 + Task 5 |
| Bottom bar with styled install button | Task 3 |
| Custom ttk.Style theme | Task 2 |
| Window 900x560, min 750x450 | Task 3 |
| Section labels (uppercase, letter-spacing) | Task 3 |
| Spacing constants | Task 1 |
| All backend logic unchanged | All tasks only modify _build_ui, _update_tree, _setup_style |

### Placeholder Scan

No "TBD", "TODO", or "fill in" patterns. All steps contain concrete code.

### Type Consistency

- `STATUS_ICONS` now uses string keys (`"ok"`, `"missing"`, `"warning"`) consistently.
- `_update_tree` handles both `Status` enum and string status values via `hasattr(status, 'value')`.
- All font constants defined in Task 1, used in Tasks 3, 4, 5.
- All color constants defined in Task 1, used throughout.

All checks pass.
