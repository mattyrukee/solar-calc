from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import PageBreak
from reportlab.graphics.shapes import Drawing, Rect, Line, String, Circle, Wedge
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF
from reportlab.platypus.flowables import Flowable
from reportlab.pdfgen import canvas as pdfcanvas
import io

PAGE_W, PAGE_H = landscape(A4)

# ── Brand palette ──────────────────────────────────────────────────────────────
NAVY      = colors.HexColor("#0D1B2A")
SLATE     = colors.HexColor("#1B3A5C")
STEEL     = colors.HexColor("#2C5F8A")
ACCENT    = colors.HexColor("#F4A824")
LIGHT_BG  = colors.HexColor("#F5F7FA")
MID_GRAY  = colors.HexColor("#8A9BB0")
WHITE     = colors.white
RED_SOFT  = colors.HexColor("#E05C5C")
GREEN_SOFT= colors.HexColor("#4CAF82")

# ── Canvas-level drawing helpers ───────────────────────────────────────────────
def draw_slide_background(c, style="default"):
    c.saveState()
    if style == "cover":
        c.setFillColor(NAVY)
        c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        # Gold accent bar left
        c.setFillColor(ACCENT)
        c.rect(0, 0, 8, PAGE_H, fill=1, stroke=0)
        # Subtle diagonal decoration
        c.setFillColor(SLATE)
        c.setStrokeColor(SLATE)
        from reportlab.graphics.shapes import Polygon
        pts = [PAGE_W*0.6, PAGE_H, PAGE_W, PAGE_H, PAGE_W, 0, PAGE_W*0.78, 0]
        p = c.beginPath()
        p.moveTo(PAGE_W*0.62, PAGE_H)
        p.lineTo(PAGE_W, PAGE_H)
        p.lineTo(PAGE_W, 0)
        p.lineTo(PAGE_W*0.80, 0)
        p.close()
        c.setFillColor(colors.HexColor("#162840"))
        c.drawPath(p, fill=1, stroke=0)
    elif style == "section":
        c.setFillColor(SLATE)
        c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        c.setFillColor(ACCENT)
        c.rect(0, 0, PAGE_W, 6, fill=1, stroke=0)
        c.rect(0, PAGE_H-6, PAGE_W, 6, fill=1, stroke=0)
    else:
        c.setFillColor(WHITE)
        c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        # Navy left sidebar
        c.setFillColor(NAVY)
        c.rect(0, 0, 6, PAGE_H, fill=1, stroke=0)
        # Light top bar
        c.setFillColor(LIGHT_BG)
        c.rect(6, PAGE_H-54, PAGE_W-6, 54, fill=1, stroke=0)
        # Gold accent under top bar
        c.setFillColor(ACCENT)
        c.rect(6, PAGE_H-57, PAGE_W-6, 3, fill=1, stroke=0)
        # Footer
        c.setFillColor(LIGHT_BG)
        c.rect(6, 0, PAGE_W-6, 30, fill=1, stroke=0)
        c.setFillColor(MID_GRAY)
        c.setFont("Helvetica", 7)
        c.drawString(20, 10, "Document Formatting Portfolio  •  Excel / PowerPoint / Documents Expert")
        c.drawRightString(PAGE_W - 14, 10, "Confidential")
    c.restoreState()

def draw_slide_title(c, title, subtitle=None, style="default"):
    c.saveState()
    if style == "cover":
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(26, PAGE_H - 60, "DOCUMENT FORMATTING  •  PORTFOLIO")
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 36)
        c.drawString(26, PAGE_H - 140, title)
        if subtitle:
            c.setFillColor(MID_GRAY)
            c.setFont("Helvetica", 16)
            c.drawString(26, PAGE_H - 175, subtitle)
    elif style == "section":
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 28)
        c.drawCentredString(PAGE_W/2, PAGE_H/2 + 20, title)
        if subtitle:
            c.setFillColor(ACCENT)
            c.setFont("Helvetica", 14)
            c.drawCentredString(PAGE_W/2, PAGE_H/2 - 20, subtitle)
    else:
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(22, PAGE_H - 38, title)
        if subtitle:
            c.setFillColor(STEEL)
            c.setFont("Helvetica", 10)
            c.drawString(22, PAGE_H - 52, subtitle)
    c.restoreState()

# ── Slide builders ─────────────────────────────────────────────────────────────

def slide_cover(c):
    draw_slide_background(c, "cover")
    draw_slide_title(c, "Document Formatting", "Expert Portfolio  •  Excel  /  PowerPoint  /  Word", "cover")

    c.saveState()
    # Divider line
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.5)
    c.line(26, PAGE_H - 195, 380, PAGE_H - 195)

    # Bullet competencies
    items = [
        "Professional slide deck design & layout",
        "Data visualisation  —  charts, tables, dashboards",
        "Style systems: consistent typography & colour hierarchies",
        "Before/after document audit & change documentation",
        "Brand-compliant templates for corporate use",
    ]
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.HexColor("#BDC8D8"))
    y = PAGE_H - 222
    for item in items:
        c.setFillColor(ACCENT)
        c.circle(34, y + 4, 3, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#BDC8D8"))
        c.drawString(46, y, item)
        y -= 22

    # Right-side decorative stat boxes
    boxes = [("100 %", "On-brand output"), ("48 hr", "Avg turnaround"), ("50 +", "Projects delivered")]
    bx = PAGE_W - 210
    by = PAGE_H - 120
    for val, label in boxes:
        c.setFillColor(colors.HexColor("#162840"))
        c.roundRect(bx, by, 170, 64, 6, fill=1, stroke=0)
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(bx + 85, by + 38, val)
        c.setFillColor(MID_GRAY)
        c.setFont("Helvetica", 9)
        c.drawCentredString(bx + 85, by + 18, label)
        by -= 80

    c.restoreState()

def slide_about(c):
    draw_slide_background(c)
    draw_slide_title(c, "About & Core Competencies", "What I bring to every engagement")

    c.saveState()
    # Left column – skills table
    col_x = 22
    col_y = PAGE_H - 80
    skills = [
        ("Layout & Typography",    92),
        ("Data Visualisation",     88),
        ("Brand Consistency",      95),
        ("Change Documentation",   90),
        ("Template Engineering",   85),
        ("Cross-app Formatting",   93),
    ]
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(NAVY)
    c.drawString(col_x, col_y, "SKILL PROFICIENCY")
    col_y -= 18
    bar_w = 260
    bar_h = 14
    for skill, pct in skills:
        c.setFillColor(LIGHT_BG)
        c.roundRect(col_x, col_y, bar_w, bar_h, 4, fill=1, stroke=0)
        c.setFillColor(STEEL)
        c.roundRect(col_x, col_y, bar_w * pct / 100, bar_h, 4, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.setFont("Helvetica", 9)
        c.drawString(col_x + 6, col_y + 3, skill)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 9)
        filled_end = col_x + bar_w * pct / 100
        if pct > 20:
            c.drawRightString(filled_end - 6, col_y + 3, f"{pct}%")
        col_y -= 24

    # Right column – tool icons represented as labelled boxes
    tools = [
        ("Microsoft\nExcel",     "#217346"),
        ("Microsoft\nPowerPoint","#B7472A"),
        ("Microsoft\nWord",      "#2B579A"),
        ("Google\nSlides",       "#F4B400"),
        ("Google\nSheets",       "#0F9D58"),
        ("Adobe\nAcrobat",       "#FF0000"),
    ]
    tx = PAGE_W / 2 + 20
    ty = PAGE_H - 90
    box_s = 70
    gap = 18
    cols = 3
    for i, (name, hex_col) in enumerate(tools):
        row = i // cols
        col = i % cols
        bx = tx + col * (box_s + gap)
        by = ty - row * (box_s + gap)
        c.setFillColor(colors.HexColor(hex_col))
        c.roundRect(bx, by, box_s, box_s, 8, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 9)
        lines = name.split("\n")
        line_y = by + box_s/2 + 5 * (len(lines)-1)
        for ln in lines:
            c.drawCentredString(bx + box_s/2, line_y, ln)
            line_y -= 13

    c.restoreState()

def slide_methodology(c):
    draw_slide_background(c)
    draw_slide_title(c, "My Document Improvement Process", "A repeatable, audit-friendly workflow")

    c.saveState()
    steps = [
        ("01", "Audit",       "Review original for structure, hierarchy,\nspacing, colour, and consistency issues."),
        ("02", "Benchmark",   "Identify the document's purpose & audience;\nset formatting standards to target."),
        ("03", "Redesign",    "Apply style system: typography scale, colour\npalette, grid alignment, and spacing rules."),
        ("04", "Data polish", "Rebuild charts/tables for clarity — correct\naxis labels, legends, and colour encoding."),
        ("05", "Document",    "Log every change with before/after evidence\nand rationale for full traceability."),
        ("06", "Deliver",     "Export in required format(s); provide\nedit-ready source files and a change log."),
    ]
    total = len(steps)
    start_x = 28
    step_w = (PAGE_W - 56) / total
    base_y = 80

    for i, (num, title, desc) in enumerate(steps):
        bx = start_x + i * step_w + 4
        # Connector line
        if i < total - 1:
            c.setStrokeColor(MID_GRAY)
            c.setLineWidth(1)
            c.setDash(3, 3)
            c.line(bx + step_w - 8, base_y + 110, bx + step_w - 8 + 8, base_y + 110)
            c.setDash()

        # Box
        box_w = step_w - 8
        c.setFillColor(LIGHT_BG)
        c.roundRect(bx, base_y, box_w, 155, 8, fill=1, stroke=0)
        # Number badge
        c.setFillColor(NAVY)
        c.circle(bx + box_w/2, base_y + 135, 18, fill=1, stroke=0)
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(bx + box_w/2, base_y + 130, num)
        # Title
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(bx + box_w/2, base_y + 100, title)
        # Description
        c.setFillColor(colors.HexColor("#4A5568"))
        c.setFont("Helvetica", 8)
        for j, ln in enumerate(desc.split("\n")):
            c.drawCentredString(bx + box_w/2, base_y + 80 - j*13, ln)

    c.restoreState()

def slide_before_after(c):
    draw_slide_background(c)
    draw_slide_title(c, "Before & After: Slide Transformation", "Real-world example of formatting improvements applied")

    c.saveState()
    mid = PAGE_W / 2
    y_top = PAGE_H - 75
    panel_h = PAGE_H - 115
    panel_w = mid - 40

    # ── BEFORE panel ──────────────────────────────────────────────────
    c.setFillColor(colors.HexColor("#FFF5F5"))
    c.roundRect(22, 35, panel_w, panel_h, 6, fill=1, stroke=0)
    c.setFillColor(RED_SOFT)
    c.roundRect(22, 35 + panel_h - 28, panel_w, 28, 6, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(22 + panel_w/2, 35 + panel_h - 12, "✗  BEFORE")

    issues = [
        ("Font chaos",      "4 different typefaces; no size hierarchy"),
        ("Poor contrast",   "Light grey text on white — fails WCAG AA"),
        ("Misaligned grid", "Elements not snapped; inconsistent margins"),
        ("Cluttered chart", "3-D pie chart with 11 unlabelled slices"),
        ("No whitespace",   "Paragraphs crammed edge-to-edge"),
        ("Inconsistent colour", "7 unrelated accent colours across slides"),
    ]
    iy = 35 + panel_h - 60
    for issue, detail in issues:
        c.setFillColor(RED_SOFT)
        c.circle(36, iy + 4, 4, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(46, iy, issue)
        c.setFillColor(colors.HexColor("#666666"))
        c.setFont("Helvetica", 8)
        c.drawString(46, iy - 12, detail)
        iy -= 34

    # ── AFTER panel ───────────────────────────────────────────────────
    ax = mid + 18
    c.setFillColor(colors.HexColor("#F0FFF8"))
    c.roundRect(ax, 35, panel_w, panel_h, 6, fill=1, stroke=0)
    c.setFillColor(GREEN_SOFT)
    c.roundRect(ax, 35 + panel_h - 28, panel_w, 28, 6, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(ax + panel_w/2, 35 + panel_h - 12, "✓  AFTER")

    fixes = [
        ("Unified type scale",   "2-font system: heading + body, 4-size scale"),
        ("WCAG AA contrast",     "All text passes 4.5 : 1 minimum ratio"),
        ("12-column grid",       "All elements locked to consistent margins"),
        ("Clean bar chart",      "Flat 2-D chart; direct labels; legend removed"),
        ("Breathing room",       "8-pt baseline grid; generous line spacing"),
        ("3-colour palette",     "Navy / steel / gold — applied consistently"),
    ]
    iy = 35 + panel_h - 60
    for fix, detail in fixes:
        c.setFillColor(GREEN_SOFT)
        c.circle(ax + 14, iy + 4, 4, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(ax + 24, iy, fix)
        c.setFillColor(colors.HexColor("#666666"))
        c.setFont("Helvetica", 8)
        c.drawString(ax + 24, iy - 12, detail)
        iy -= 34

    # Arrow between panels
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(mid, PAGE_H/2, "→")

    c.restoreState()

def slide_change_log(c):
    draw_slide_background(c)
    draw_slide_title(c, "Change Documentation Log", "Every revision tracked with category, rationale, and impact")

    c.saveState()
    headers = ["#", "Category", "Original State", "Change Applied", "Rationale", "Impact"]
    rows = [
        ["1",  "Typography",   "5 fonts, mixed sizes",    "2-font system, 4-level scale",    "Cognitive load reduction",    "HIGH"],
        ["2",  "Colour",       "7 arbitrary accents",     "3-colour brand palette",          "Brand consistency",           "HIGH"],
        ["3",  "Spacing",      "No baseline grid",        "8 pt baseline, 24 pt margins",    "Visual rhythm & alignment",   "MED"],
        ["4",  "Charts",       "3-D pie, no labels",      "Flat bar chart, direct labels",   "Data clarity, accessibility", "HIGH"],
        ["5",  "Tables",       "Plain borders, no zebra", "Alternating rows, bold headers",  "Scanability",                 "MED"],
        ["6",  "Hierarchy",    "Flat heading structure",  "H1/H2/H3 weight contrast",        "Reading flow",                "MED"],
        ["7",  "Contrast",     "Grey-on-white text",      "Navy on white (7 : 1 ratio)",     "WCAG AA compliance",          "HIGH"],
        ["8",  "Alignment",    "Ragged mixed alignment",  "Left-aligned body, centred heads","Grid consistency",            "LOW"],
    ]

    col_widths = [22, 75, 130, 145, 150, 52]
    tx = 22
    ty = PAGE_H - 78

    # Header row
    c.setFillColor(NAVY)
    c.rect(tx, ty - 2, sum(col_widths), 20, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 8)
    cx = tx
    for i, h in enumerate(headers):
        c.drawString(cx + 4, ty + 5, h)
        cx += col_widths[i]
    ty -= 22

    impact_colors = {"HIGH": RED_SOFT, "MED": ACCENT, "LOW": GREEN_SOFT}

    for row_i, row in enumerate(rows):
        row_bg = LIGHT_BG if row_i % 2 == 0 else WHITE
        c.setFillColor(row_bg)
        c.rect(tx, ty - 2, sum(col_widths), 18, fill=1, stroke=0)
        cx = tx
        for col_i, cell in enumerate(row):
            if col_i == 5:  # Impact badge
                badge_color = impact_colors.get(cell, MID_GRAY)
                c.setFillColor(badge_color)
                c.roundRect(cx + 2, ty, col_widths[col_i] - 4, 14, 4, fill=1, stroke=0)
                c.setFillColor(WHITE)
                c.setFont("Helvetica-Bold", 7)
                c.drawCentredString(cx + col_widths[col_i]/2, ty + 3, cell)
            else:
                c.setFillColor(NAVY if col_i == 0 else colors.HexColor("#333333"))
                c.setFont("Helvetica-Bold" if col_i == 0 else "Helvetica", 8)
                c.drawString(cx + 4, ty + 3, cell)
            cx += col_widths[col_i]
        ty -= 20

    c.restoreState()

def slide_data_viz(c):
    draw_slide_background(c)
    draw_slide_title(c, "Data Visualisation Principles", "Charts rebuilt for clarity, accuracy, and accessibility")

    c.saveState()
    # Left: Bad chart label
    bx, by = 28, 80
    bw, bh = 280, 175
    c.setFillColor(LIGHT_BG)
    c.roundRect(bx, by, bw, bh, 6, fill=1, stroke=0)
    c.setFillColor(RED_SOFT)
    c.roundRect(bx, by + bh - 24, bw, 24, 6, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(bx + bw/2, by + bh - 10, "✗  Common Chart Mistakes")

    mistakes = [
        "3-D effects that distort proportions",
        "Dual-axis charts with incompatible scales",
        "Pie charts with > 5 segments",
        "Missing axis labels or units",
        "Rainbow colour palette (not accessible)",
        "Truncated Y-axis to exaggerate change",
    ]
    my = by + bh - 45
    for m in mistakes:
        c.setFillColor(RED_SOFT)
        c.circle(bx + 12, my + 4, 3, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#333333"))
        c.setFont("Helvetica", 8)
        c.drawString(bx + 22, my, m)
        my -= 18

    # Right: Good practices
    gx = bx + bw + 30
    c.setFillColor(LIGHT_BG)
    c.roundRect(gx, by, bw, bh, 6, fill=1, stroke=0)
    c.setFillColor(GREEN_SOFT)
    c.roundRect(gx, by + bh - 24, bw, 24, 6, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(gx + bw/2, by + bh - 10, "✓  Best Practices Applied")

    goods = [
        "Flat 2-D bars with direct data labels",
        "Single-metric charts per visual",
        "Max 5 segments; group remainder as 'Other'",
        "Clear axis labels with units in parentheses",
        "Sequential / diverging palette, colourblind-safe",
        "Y-axis always starts at zero",
    ]
    gy = by + bh - 45
    for g in goods:
        c.setFillColor(GREEN_SOFT)
        c.circle(gx + 12, gy + 4, 3, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#333333"))
        c.setFont("Helvetica", 8)
        c.drawString(gx + 22, gy, g)
        gy -= 18

    # Mini sample bar chart (right side)
    cx2 = gx + bw + 30
    cy2 = by
    cw = PAGE_W - cx2 - 22
    ch = bh

    c.setFillColor(LIGHT_BG)
    c.roundRect(cx2, cy2, cw, ch, 6, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(cx2 + cw/2, cy2 + ch - 14, "Sample: Correctly formatted bar chart")

    data_vals = [42, 67, 55, 81, 73]
    labels    = ["Q1", "Q2", "Q3", "Q4", "Q5"]
    bar_area_w = cw - 30
    bar_area_h = ch - 50
    bar_w_each = bar_area_w / len(data_vals) - 8
    max_val = max(data_vals)
    for i, (val, lbl) in enumerate(zip(data_vals, labels)):
        bbar_x = cx2 + 15 + i * (bar_area_w / len(data_vals))
        bar_height = (val / max_val) * (bar_area_h - 20)
        c.setFillColor(STEEL)
        c.roundRect(bbar_x, cy2 + 28, bar_w_each, bar_height, 3, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(bbar_x + bar_w_each/2, cy2 + 28 + bar_height + 3, str(val))
        c.setFillColor(MID_GRAY)
        c.setFont("Helvetica", 7)
        c.drawCentredString(bbar_x + bar_w_each/2, cy2 + 16, lbl)

    # Y-axis line
    c.setStrokeColor(MID_GRAY)
    c.setLineWidth(0.5)
    c.line(cx2 + 13, cy2 + 26, cx2 + 13, cy2 + ch - 28)

    c.restoreState()

def slide_typography(c):
    draw_slide_background(c)
    draw_slide_title(c, "Typography & Style Systems", "Consistent type scales create visual order and trust")

    c.saveState()
    # Type scale showcase
    tx = 28
    ty = PAGE_H - 80

    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(tx, ty, "TYPE SCALE  —  HEADING HIERARCHY")
    ty -= 14

    scale = [
        ("H1 — Slide Title",    28, "Helvetica-Bold",  NAVY),
        ("H2 — Section Head",   20, "Helvetica-Bold",  SLATE),
        ("H3 — Sub-heading",    14, "Helvetica-Bold",  STEEL),
        ("Body copy",           10, "Helvetica",        colors.HexColor("#333333")),
        ("Caption / label",      8, "Helvetica-Oblique",MID_GRAY),
    ]
    for label, size, font, col in scale:
        c.setFillColor(col)
        c.setFont(font, size)
        c.drawString(tx, ty, label)
        c.setFillColor(MID_GRAY)
        c.setFont("Helvetica", 7)
        c.drawRightString(tx + 300, ty, f"{size} pt  •  {font.replace('Helvetica', 'Inter / Calibri')}")
        ty -= size + 10

    # Colour palette swatches
    ty -= 10
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(tx, ty, "COLOUR PALETTE")
    ty -= 14

    palette = [
        (NAVY,       "Navy #0D1B2A",    "Primary / Background"),
        (SLATE,      "Slate #1B3A5C",   "Secondary"),
        (STEEL,      "Steel #2C5F8A",   "Accent 1"),
        (ACCENT,     "Gold #F4A824",    "Highlight / CTA"),
        (MID_GRAY,   "Mid-gray #8A9BB0","Body text / labels"),
        (LIGHT_BG,   "Light #F5F7FA",   "Panel backgrounds"),
    ]
    sw = 54
    sh = 44
    gap = 10
    for i, (col, name, role) in enumerate(palette):
        sx = tx + i * (sw + gap)
        c.setFillColor(col)
        c.roundRect(sx, ty - sh, sw, sh, 4, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#333333"))
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(sx + sw/2, ty - sh - 11, name.split(" ")[1])
        c.setFillColor(MID_GRAY)
        c.setFont("Helvetica", 6.5)
        c.drawCentredString(sx + sw/2, ty - sh - 21, role)

    # Right side: spacing rules
    rx = PAGE_W / 2 + 20
    ry = PAGE_H - 80
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(rx, ry, "SPACING SYSTEM")
    ry -= 16

    spacing_rules = [
        ("Baseline grid",         "8 pt",  "All vertical rhythm snaps to 8 pt increments"),
        ("Section padding",       "24 pt", "Top/bottom padding between major sections"),
        ("Paragraph spacing",     "12 pt", "Space after each paragraph block"),
        ("Slide margins",         "20 pt", "Consistent edge clearance on all sides"),
        ("Table cell padding",    "6 pt",  "Internal cell padding, all sides"),
        ("Icon / text gap",       "8 pt",  "Space between bullet icon and text"),
    ]
    for rule, val, note in spacing_rules:
        c.setFillColor(ACCENT)
        c.roundRect(rx, ry - 2, 36, 13, 3, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(rx + 18, ry + 1, val)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(rx + 44, ry + 1, rule)
        c.setFillColor(MID_GRAY)
        c.setFont("Helvetica", 8)
        c.drawString(rx + 44, ry - 10, note)
        ry -= 30

    c.restoreState()

def slide_closing(c):
    draw_slide_background(c, "cover")
    c.saveState()

    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(PAGE_W/2, PAGE_H - 70, "READY TO ELEVATE YOUR DOCUMENTS")

    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(PAGE_W/2, PAGE_H/2 + 30, "Let's work together.")

    c.setFillColor(MID_GRAY)
    c.setFont("Helvetica", 13)
    c.drawCentredString(PAGE_W/2, PAGE_H/2 - 10,
        "Every document tells a story — let's make yours impossible to ignore.")

    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.5)
    c.line(PAGE_W/2 - 120, PAGE_H/2 - 30, PAGE_W/2 + 120, PAGE_H/2 - 30)

    deliverables = ["Formatted source file", "PDF export", "Full change log", "Style guide snippet"]
    dx = PAGE_W/2 - (len(deliverables) * 110) / 2
    dy = PAGE_H/2 - 80
    for d in deliverables:
        c.setFillColor(colors.HexColor("#162840"))
        c.roundRect(dx, dy, 100, 36, 6, fill=1, stroke=0)
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(dx + 50, dy + 13, d)
        dx += 110

    c.restoreState()

# ── Assemble PDF ───────────────────────────────────────────────────────────────
OUTPUT = "/home/user/solar-calc/portfolio_slide_deck.pdf"
c = pdfcanvas.Canvas(OUTPUT, pagesize=landscape(A4))

slides = [
    (slide_cover,      "cover"),
    (slide_about,      "default"),
    (slide_methodology,"default"),
    (slide_before_after,"default"),
    (slide_change_log, "default"),
    (slide_data_viz,   "default"),
    (slide_typography, "default"),
    (slide_closing,    "cover"),
]

for fn, style in slides:
    fn(c)
    c.showPage()

c.save()
print(f"PDF saved to {OUTPUT}")
