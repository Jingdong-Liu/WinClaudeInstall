# GUI Beautification Design — Claude Code Installer

## Design Decisions

**Theme:** Clean & Light (Windows 11 / Apple inspired)

**Layout:** Improved two-column (left: detector cards, right: log panel)

**Fonts:**
- Body: `Segoe UI` (English) + `Microsoft YaHei UI` (Chinese)
- Log: `Cascadia Mono` + `Consolas` (monospace fallback)

---

## Visual Design

### Color Palette

| Element | Color |
|---------|-------|
| Background | `#f8fafc` (slate-50) |
| Card background | `#ffffff` |
| Card border | `#e2e8f0` (slate-200) |
| Text primary | `#1e293b` (slate-800) |
| Text secondary | `#475569` (slate-600) |
| Text muted | `#94a3b8` (slate-400) |
| Success (OK) | `#22c55e` (green-500) |
| Error (Missing) | `#ef4444` (red-500) |
| Warning | `#f59e0b` (amber-500) |
| Button gradient start | `#3b82f6` (blue-500) |
| Button gradient end | `#6366f1` (indigo-500) |
| Button shadow | `rgba(59, 130, 246, 0.3)` |

### Missing/Warning Card Borders

- OK items: standard `#e2e8f0` border
- MISSING items: `#fca5a5` border (red-300)
- WARNING items: `#fcd34d` border (amber-300)

### Window Dimensions

- Size: 900x560 (increased from 800x500)
- Min size: 750x450

---

## Layout Structure

### Header Bar
- Gradient background: `#f8fafc` to `#e8ecf1`
- Left: 36x36 rounded icon box (blue-indigo gradient) with "C"
- Title: "Claude Code Installer" (18px, weight 600, `#1e293b`)
- Subtitle: "一键安装环境检测与执行" (12px, `#64748b`)
- Bottom border: 1px `#e2e8f0`
- Padding: 20px 24px 16px

### Left Panel (Detector Cards)
- Section label: "ENVIRONMENT CHECK" (13px, weight 600, uppercase, letter-spacing 0.5px)
- Each detector as a card:
  - White background, 1px border, 8px border-radius
  - Shadow: `0 1px 2px rgba(0,0,0,0.04)`
  - Padding: 10px 14px
  - Flex row: icon (16px, colored) + name (13px, weight 500, 90px min-width) + detail (12px, right-aligned)
  - Gap between cards: 6px
- Refresh button: white bg, 1px border, 6px radius, 8px 20px padding

### Right Panel (Log)
- Section label: "INSTALLATION LOG" (same style as left)
- Log container:
  - White background, 1px border, 8px radius
  - Shadow: `0 1px 3px rgba(0,0,0,0.04)`
  - Padding: 14px
  - Font: Cascadia Mono/Consolas monospace, 12px
  - Line height: 1.7
  - Text color: `#475569`
  - Log entries with colored status icons

### Bottom Bar
- White background, top border: 1px `#e2e8f0`
- Centered install button:
  - Gradient: `#3b82f6` to `#6366f1`
  - White text, 15px, weight 600
  - 8px border-radius, 12px 48px padding
  - Shadow: `0 4px 12px rgba(59,130,246,0.3)`

---

## Implementation Approach

Since tkinter's `ttk` theming is limited, the beautification will use:

1. **Custom ttk.Style** — override default ttk styles for buttons, labels, treeview
2. **Frame backgrounds** — use `ttk.Frame` with styled backgrounds to create card effect
3. **Custom colors** — configure ttk styles with the color palette
4. **Font constants** — define font strings at module level for consistency
5. **Spacing** — use padding and gap constants instead of hardcoded values

### Limitations Acknowledged

- tkinter cannot do CSS-like gradients, box-shadows, or rounded corners natively
- "Cards" will be implemented as styled frames with borders and background colors
- Gradient button will use a solid color closest to the gradient midpoint (`#4f63e3`)
- The visual effect will be clean and modern within tkinter's capabilities
