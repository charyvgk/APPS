#!/usr/bin/env python3
"""Generate Central Flagging Mechanism architecture presentation (PDF)."""

from __future__ import annotations

import math
from pathlib import Path

from reportlab.lib.colors import Color, HexColor, white, black
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Central_Flagging_Mechanism.pdf"

# Visual system — deep teal / ink / amber (avoid purple/cream AI defaults)
INK = HexColor("#0B1F2A")
TEAL = HexColor("#0E7C7B")
TEAL_DARK = HexColor("#065A59")
TEAL_LIGHT = HexColor("#E6F4F4")
AMBER = HexColor("#D97706")
AMBER_SOFT = HexColor("#FEF3C7")
CORAL = HexColor("#C2410C")
SLATE = HexColor("#334155")
MUTED = HexColor("#64748B")
SURFACE = HexColor("#F7FAFB")
LINE = HexColor("#CBD5E1")
GOOD = HexColor("#047857")
GOOD_SOFT = HexColor("#D1FAE5")
BAD = HexColor("#B91C1C")
BAD_SOFT = HexColor("#FEE2E2")

PAGE = landscape(A4)
W, H = PAGE


def register_fonts() -> tuple[str, str, str]:
    candidates = [
        ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"),
    ]
    for reg, bold, ital in candidates:
        if Path(reg).exists() and Path(bold).exists():
            pdfmetrics.registerFont(TTFont("Body", reg))
            pdfmetrics.registerFont(TTFont("BodyBold", bold))
            if Path(ital).exists():
                pdfmetrics.registerFont(TTFont("BodyItalic", ital))
            else:
                pdfmetrics.registerFont(TTFont("BodyItalic", reg))
            return "Body", "BodyBold", "BodyItalic"
    return "Helvetica", "Helvetica-Bold", "Helvetica-Oblique"


BODY, BOLD, ITALIC = register_fonts()


def gradient_rect(c: canvas.Canvas, x, y, w, h, c1: Color, c2: Color, steps=48):
    for i in range(steps):
        t = i / (steps - 1)
        r = c1.red + (c2.red - c1.red) * t
        g = c1.green + (c2.green - c1.green) * t
        b = c1.blue + (c2.blue - c1.blue) * t
        c.setFillColor(Color(r, g, b))
        yy = y + h * i / steps
        c.rect(x, yy, w, h / steps + 0.5, fill=1, stroke=0)


def draw_footer(c: canvas.Canvas, page: int, total: int, label: str = "Central Flagging Mechanism"):
    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    c.line(18 * mm, 12 * mm, W - 18 * mm, 12 * mm)
    c.setFillColor(MUTED)
    c.setFont(BODY, 8)
    c.drawString(18 * mm, 7 * mm, label)
    c.drawRightString(W - 18 * mm, 7 * mm, f"{page} / {total}")


def draw_slide_bg(c: canvas.Canvas, accent_bar: bool = True):
    c.setFillColor(SURFACE)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    # subtle top wash
    gradient_rect(c, 0, H - 28 * mm, W, 28 * mm, HexColor("#DCEEEF"), SURFACE, 24)
    if accent_bar:
        c.setFillColor(TEAL)
        c.rect(0, 0, 4 * mm, H, fill=1, stroke=0)


def title_block(c: canvas.Canvas, title: str, subtitle: str | None = None, y: float | None = None):
    y = y if y is not None else H - 22 * mm
    c.setFillColor(INK)
    c.setFont(BOLD, 24)
    c.drawString(18 * mm, y, title)
    if subtitle:
        c.setFillColor(MUTED)
        c.setFont(BODY, 11)
        c.drawString(18 * mm, y - 7 * mm, subtitle)
    c.setStrokeColor(TEAL)
    c.setLineWidth(2.2)
    c.line(18 * mm, y - 10 * mm if subtitle else y - 4 * mm, 18 * mm + 42 * mm, y - 10 * mm if subtitle else y - 4 * mm)
    return y - (18 * mm if subtitle else 12 * mm)


def rounded_box(c, x, y, w, h, fill, stroke=None, radius=6):
    c.setFillColor(fill)
    if stroke:
        c.setStrokeColor(stroke)
        c.setLineWidth(1)
        c.roundRect(x, y, w, h, radius, fill=1, stroke=1)
    else:
        c.roundRect(x, y, w, h, radius, fill=1, stroke=0)


def bullet(c, x, y, text, color=SLATE, size=11, max_width=220 * mm):
    c.setFillColor(TEAL)
    c.circle(x + 1.6 * mm, y + 1.2 * mm, 1.1 * mm, fill=1, stroke=0)
    c.setFillColor(color)
    c.setFont(BODY, size)
    # simple wrap
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if c.stringWidth(trial, BODY, size) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    for i, line in enumerate(lines):
        c.drawString(x + 5 * mm, y - i * 5.2 * mm, line)
    return y - max(1, len(lines)) * 5.2 * mm - 2.2 * mm


def chip(c, x, y, text, bg, fg, pad_x=3.2 * mm, pad_y=1.6 * mm):
    c.setFont(BOLD, 8)
    tw = c.stringWidth(text, BOLD, 8)
    rounded_box(c, x, y, tw + pad_x * 2, 5.5 * mm, bg, radius=3)
    c.setFillColor(fg)
    c.drawString(x + pad_x, y + pad_y, text)
    return tw + pad_x * 2


# ---------- Diagram helpers ----------

def box_node(c, x, y, w, h, title, lines=None, fill=white, stroke=TEAL, title_color=INK):
    rounded_box(c, x, y, w, h, fill, stroke=stroke, radius=5)
    c.setFillColor(title_color)
    c.setFont(BOLD, 9)
    c.drawCentredString(x + w / 2, y + h - 5.5 * mm, title)
    if lines:
        c.setFont(BODY, 7.5)
        c.setFillColor(SLATE)
        for i, line in enumerate(lines):
            c.drawCentredString(x + w / 2, y + h - 10 * mm - i * 3.8 * mm, line)
    return (x + w / 2, y, x + w / 2, y + h)  # cx, bottom, cx, top


def arrow(c, x1, y1, x2, y2, color=SLATE, label=None, dashed=False):
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.2)
    if dashed:
        c.setDash(3, 2)
    else:
        c.setDash()
    c.line(x1, y1, x2, y2)
    c.setDash()
    ang = math.atan2(y2 - y1, x2 - x1)
    size = 3.2 * mm
    path = c.beginPath()
    path.moveTo(x2, y2)
    path.lineTo(x2 - size * math.cos(ang - 0.4), y2 - size * math.sin(ang - 0.4))
    path.lineTo(x2 - size * math.cos(ang + 0.4), y2 - size * math.sin(ang + 0.4))
    path.close()
    c.drawPath(path, fill=1, stroke=0)
    if label:
        c.setFont(BODY, 7)
        c.setFillColor(MUTED)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        c.drawCentredString(mx, my + 2 * mm, label)


def draw_sequence_actor(c, x, y_top, y_bot, name, color=TEAL):
    # head
    c.setFillColor(color)
    c.circle(x, y_top + 4 * mm, 3 * mm, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont(BOLD, 8)
    c.drawCentredString(x, y_top + 9 * mm, name)
    c.setStrokeColor(LINE)
    c.setDash(2, 2)
    c.setLineWidth(0.8)
    c.line(x, y_top, x, y_bot)
    c.setDash()
    return x


def seq_msg(c, x1, x2, y, text, color=SLATE, reply=False):
    arrow(c, x1, y, x2, y, color=color)
    c.setFont(BODY, 7)
    c.setFillColor(color if not reply else MUTED)
    c.drawCentredString((x1 + x2) / 2, y + 2.2 * mm, text)


# ---------- Slides ----------

def slide_title(c, page, total):
    gradient_rect(c, 0, 0, W, H, INK, TEAL_DARK, 64)
    # atmospheric arcs
    c.setStrokeColor(Color(1, 1, 1, alpha=0.08))
    c.setLineWidth(18)
    c.circle(W * 0.85, H * 0.2, 90 * mm, fill=0, stroke=1)
    c.circle(W * 0.1, H * 0.9, 70 * mm, fill=0, stroke=1)

    c.setFillColor(AMBER)
    c.setFont(BOLD, 10)
    c.drawString(22 * mm, H - 28 * mm, "ARCHITECTURE BRIEFING")

    c.setFillColor(white)
    c.setFont(BOLD, 36)
    c.drawString(22 * mm, H - 52 * mm, "Central Flagging Mechanism")

    c.setFont(BODY, 14)
    c.setFillColor(HexColor("#B6D7D7"))
    c.drawString(22 * mm, H - 64 * mm,
                 "From fragmented project flags to a namespaced platform of record")

    # three pillars
    items = [
        ("Problem", "Duplicated flags, drift, and\noperational risk across apps"),
        ("Approach", "One control plane with\nproject-name namespaces"),
        ("Outcome", "Consistent evaluation,\nauditability, faster delivery"),
    ]
    for i, (t, d) in enumerate(items):
        x = 22 * mm + i * 85 * mm
        rounded_box(c, x, 28 * mm, 78 * mm, 36 * mm, Color(1, 1, 1, alpha=0.08), radius=6)
        c.setFillColor(AMBER)
        c.setFont(BOLD, 11)
        c.drawString(x + 5 * mm, 54 * mm, t)
        c.setFillColor(white)
        c.setFont(BODY, 9)
        for j, line in enumerate(d.split("\n")):
            c.drawString(x + 5 * mm, 46 * mm - j * 5 * mm, line)

    c.setFillColor(HexColor("#94B8B8"))
    c.setFont(BODY, 9)
    c.drawString(22 * mm, 14 * mm, "Senior Software Architect  ·  Feature Flag Platform Strategy")
    c.setFillColor(HexColor("#94B8B8"))
    c.drawRightString(W - 22 * mm, 14 * mm, f"{page} / {total}")


def slide_agenda(c, page, total):
    draw_slide_bg(c)
    y = title_block(c, "Agenda", "What we will cover")
    items = [
        ("01", "Current state — individual project flagging"),
        ("02", "Sequence: how per-project flags work today"),
        ("03", "Drawbacks of isolated flag stores"),
        ("04", "Drawbacks of the same flags copied across projects"),
        ("05", "Target architecture — central flagging with namespaces"),
        ("06", "How the central model closes every gap"),
        ("07", "Pros, operating model, and recommendation"),
    ]
    for i, (num, text) in enumerate(items):
        yy = y - i * 14 * mm
        rounded_box(c, 18 * mm, yy - 3 * mm, 14 * mm, 10 * mm, TEAL_LIGHT, radius=3)
        c.setFillColor(TEAL_DARK)
        c.setFont(BOLD, 11)
        c.drawCentredString(25 * mm, yy, num)
        c.setFillColor(INK)
        c.setFont(BODY, 13)
        c.drawString(38 * mm, yy, text)
    draw_footer(c, page, total)


def slide_current_state(c, page, total):
    draw_slide_bg(c)
    y = title_block(c, "Current State: Individual Project Flags",
                    "Each application owns its own flag definitions, storage, and evaluation")

    apps = [
        ("Payments", ["feature.checkout_v2", "kill.legacy_gateway", "exp.upi_retry"]),
        ("Lending", ["feature.checkout_v2", "kill.soft_pull", "exp.risk_model_b"]),
        ("Onboarding", ["feature.kyc_async", "kill.legacy_otp", "exp.selfie_qa"]),
        ("Admin Portal", ["feature.bulk_export", "ui.dark_nav", "kill.report_v1"]),
    ]
    for i, (name, flags) in enumerate(apps):
        x = 16 * mm + i * 68 * mm
        rounded_box(c, x, 42 * mm, 62 * mm, 78 * mm, white, stroke=LINE, radius=6)
        c.setFillColor(TEAL)
        c.roundRect(x, 108 * mm, 62 * mm, 12 * mm, 6, fill=1, stroke=0)
        c.rect(x, 108 * mm, 62 * mm, 6 * mm, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont(BOLD, 10)
        c.drawCentredString(x + 31 * mm, 112 * mm, name)
        c.setFillColor(MUTED)
        c.setFont(BODY, 7.5)
        c.drawCentredString(x + 31 * mm, 100 * mm, "local flag store")
        for j, f in enumerate(flags):
            rounded_box(c, x + 4 * mm, 86 * mm - j * 12 * mm, 54 * mm, 9 * mm, TEAL_LIGHT, radius=3)
            c.setFillColor(TEAL_DARK)
            c.setFont(BODY, 7)
            c.drawCentredString(x + 31 * mm, 89 * mm - j * 12 * mm, f)

    # bottom callout
    rounded_box(c, 16 * mm, 18 * mm, W - 32 * mm, 18 * mm, AMBER_SOFT, stroke=AMBER, radius=5)
    c.setFillColor(CORAL)
    c.setFont(BOLD, 10)
    c.drawString(22 * mm, 28 * mm, "Observation")
    c.setFillColor(SLATE)
    c.setFont(BODY, 9)
    c.drawString(22 * mm, 21.5 * mm,
                 "Same semantic flags (e.g. checkout_v2) reappear with different owners, lifecycles, and truth — no shared control plane.")
    draw_footer(c, page, total)


def slide_individual_sequence(c, page, total):
    draw_slide_bg(c)
    y = title_block(c, "Sequence: Individual Flagging Mechanism",
                    "Request path when every project evaluates flags locally")

    y_top = H - 48 * mm
    y_bot = 38 * mm
    actors = [
        (40 * mm, "Client"),
        (95 * mm, "App Service"),
        (155 * mm, "Local Flag DB"),
        (215 * mm, "Config Repo"),
        (265 * mm, "Ops / Dev"),
    ]
    xs = [draw_sequence_actor(c, x, y_top, y_bot, name) for x, name in actors]

    # messages
    msgs = [
        (0, 1, "1. API request", TEAL),
        (1, 2, "2. Load flag snapshot / query", SLATE),
        (2, 1, "3. Return boolean / variant", MUTED),
        (1, 1, "", TEAL),  # placeholder skip
        (3, 1, "4. Deploy config change (async)", AMBER),
        (4, 3, "5. Edit flags in repo / console", CORAL),
        (1, 0, "6. Response after local eval", TEAL),
    ]
    ys = [y_top - 12 * mm - i * 11 * mm for i in range(7)]
    seq_msg(c, xs[0], xs[1], ys[0], msgs[0][2], msgs[0][3])
    seq_msg(c, xs[1], xs[2], ys[1], msgs[1][2], msgs[1][3])
    seq_msg(c, xs[2], xs[1], ys[2], msgs[2][2], msgs[2][3])
    # self note
    c.setStrokeColor(AMBER)
    c.setDash(2, 2)
    c.line(xs[1] + 2 * mm, ys[3], xs[1] + 22 * mm, ys[3])
    c.line(xs[1] + 22 * mm, ys[3], xs[1] + 22 * mm, ys[3] - 6 * mm)
    c.line(xs[1] + 22 * mm, ys[3] - 6 * mm, xs[1] + 2 * mm, ys[3] - 6 * mm)
    c.setDash()
    c.setFillColor(AMBER)
    c.setFont(BODY, 7)
    c.drawString(xs[1] + 24 * mm, ys[3] - 2 * mm, "3b. Evaluate rules in-process (no shared audit)")
    seq_msg(c, xs[3], xs[1], ys[4], msgs[4][2], msgs[4][3])
    seq_msg(c, xs[4], xs[3], ys[5], msgs[5][2], msgs[5][3])
    seq_msg(c, xs[1], xs[0], ys[6], msgs[6][2], msgs[6][3])

    # drawback callouts on right
    rounded_box(c, W - 78 * mm, 42 * mm, 60 * mm, 78 * mm, BAD_SOFT, stroke=BAD, radius=5)
    c.setFillColor(BAD)
    c.setFont(BOLD, 9)
    c.drawString(W - 72 * mm, 110 * mm, "Drawbacks visible here")
    issues = [
        "Flag truth is per service",
        "Config deploy lag & drift",
        "No cross-app consistency",
        "Manual multi-repo edits",
        "Weak central audit trail",
        "Hard to kill globally",
    ]
    yy = 102 * mm
    for t in issues:
        c.setFillColor(BAD)
        c.circle(W - 70 * mm, yy + 1 * mm, 1 * mm, fill=1, stroke=0)
        c.setFillColor(SLATE)
        c.setFont(BODY, 7.5)
        c.drawString(W - 66 * mm, yy, t)
        yy -= 8 * mm

    draw_footer(c, page, total)


def slide_drawbacks_individual(c, page, total):
    draw_slide_bg(c)
    y = title_block(c, "Drawbacks: Individual Project Flags",
                    "Why per-project ownership does not scale")

    cards = [
        ("Fragmented truth", "Each app is its own source of truth. Operators cannot answer “is X on?” without checking N systems."),
        ("Operational toil", "Enable/disable requires code deploys, repo PRs, or hopping between consoles — slow during incidents."),
        ("Inconsistent SDKs", "Different libraries, caching TTLs, and evaluation semantics produce divergent user experiences."),
        ("Poor governance", "No unified RBAC, approval workflow, or change audit across the estate."),
        ("Limited targeting", "Percentage rollouts, cohorts, and environment promotion are reinvented (or missing) per project."),
        ("Cost & complexity", "Duplicate storage, pipelines, and tribal knowledge increase maintenance load."),
    ]
    for i, (t, d) in enumerate(cards):
        col = i % 3
        row = i // 3
        x = 16 * mm + col * 90 * mm
        yy = y - 8 * mm - row * 52 * mm
        rounded_box(c, x, yy - 38 * mm, 84 * mm, 46 * mm, white, stroke=LINE, radius=6)
        c.setFillColor(CORAL)
        c.rect(x, yy - 38 * mm, 2.2 * mm, 46 * mm, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont(BOLD, 11)
        c.drawString(x + 7 * mm, yy - 2 * mm, t)
        c.setFillColor(SLATE)
        c.setFont(BODY, 8.5)
        # wrap
        words = d.split()
        line, ly = "", yy - 10 * mm
        for w in words:
            trial = (line + " " + w).strip()
            if c.stringWidth(trial, BODY, 8.5) < 72 * mm:
                line = trial
            else:
                c.drawString(x + 7 * mm, ly, line)
                ly -= 4.5 * mm
                line = w
        if line:
            c.drawString(x + 7 * mm, ly, line)
    draw_footer(c, page, total)


def slide_drawbacks_duplication(c, page, total):
    draw_slide_bg(c)
    y = title_block(c, "Drawbacks: Same Flags Across Different Projects",
                    "Copy-paste “shared” flags create a false sense of consistency")

    # comparison table header
    headers = ["Concern", "What happens today", "Business impact"]
    widths = [45 * mm, 105 * mm, 95 * mm]
    x0 = 16 * mm
    yy = y - 4 * mm
    c.setFillColor(INK)
    c.roundRect(x0, yy - 2 * mm, sum(widths), 10 * mm, 3, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont(BOLD, 9)
    x = x0
    for h, w in zip(headers, widths):
        c.drawString(x + 3 * mm, yy + 1.5 * mm, h)
        x += w

    rows = [
        ("Semantic drift", "Same key name, different meaning or default per repo", "Wrong cohort sees feature; support tickets spike"),
        ("Lifecycle mismatch", "Flag retired in one app, still live in another", "Dead code paths; surprise behavior in prod"),
        ("Partial rollout", "Turned on in Payments, forgotten in Lending", "Broken journeys across product boundaries"),
        ("Security gaps", "Sensitive kill-switch not mirrored everywhere", "Incident blast radius stays open longer"),
        ("Analytics noise", "Events tagged inconsistently for “same” experiment", "Invalid A/B conclusions and wasted spend"),
        ("Ownership fog", "No single owner for a cross-cutting flag", "Change freezes and slow decisioning"),
    ]
    for i, (a, b, d) in enumerate(rows):
        ryy = yy - 14 * mm - i * 12 * mm
        bg = white if i % 2 == 0 else TEAL_LIGHT
        c.setFillColor(bg)
        c.rect(x0, ryy - 3 * mm, sum(widths), 12 * mm, fill=1, stroke=0)
        c.setStrokeColor(LINE)
        c.setLineWidth(0.4)
        c.line(x0, ryy - 3 * mm, x0 + sum(widths), ryy - 3 * mm)
        vals = [a, b, d]
        x = x0
        for j, (val, w) in enumerate(zip(vals, widths)):
            c.setFillColor(INK if j == 0 else SLATE)
            c.setFont(BOLD if j == 0 else BODY, 8)
            c.drawString(x + 3 * mm, ryy, val)
            x += w
    draw_footer(c, page, total)


def slide_solution_overview(c, page, total):
    draw_slide_bg(c)
    y = title_block(c, "Solution: Central Flagging Application",
                    "One control plane · project-name namespaces · shared evaluation")

    # central hub
    cx, cy = W / 2, 78 * mm
    rounded_box(c, cx - 48 * mm, cy - 22 * mm, 96 * mm, 48 * mm, TEAL, radius=8)
    c.setFillColor(white)
    c.setFont(BOLD, 12)
    c.drawCentredString(cx, cy + 14 * mm, "Central Flag Service")
    c.setFont(BODY, 8)
    c.drawCentredString(cx, cy + 6 * mm, "API  ·  Admin UI  ·  Audit  ·  SDK config")
    c.drawCentredString(cx, cy - 2 * mm, "Namespaces = project names")
    c.setFont(BOLD, 8)
    c.drawCentredString(cx, cy - 12 * mm, "payments / lending / onboarding / …")

    satellites = [
        (30 * mm, 115 * mm, "Payments\nSDK"),
        (95 * mm, 125 * mm, "Lending\nSDK"),
        (200 * mm, 125 * mm, "Onboarding\nSDK"),
        (255 * mm, 115 * mm, "Admin\nPortal"),
        (40 * mm, 28 * mm, "CI / CD\nPromotion"),
        (130 * mm, 22 * mm, "Observability\n& Audit"),
        (220 * mm, 28 * mm, "Identity\nRBAC"),
    ]
    for x, yy, label in satellites:
        rounded_box(c, x, yy, 42 * mm, 18 * mm, white, stroke=TEAL, radius=5)
        c.setFillColor(INK)
        c.setFont(BOLD, 8)
        for i, line in enumerate(label.split("\n")):
            c.drawCentredString(x + 21 * mm, yy + 10 * mm - i * 4 * mm, line)
        # line to hub
        arrow(c, x + 21 * mm, yy + (0 if yy > cy else 18 * mm),
              cx + (x - cx) * 0.18, cy + (10 * mm if yy > cy else -10 * mm),
              color=TEAL, dashed=True)

    draw_footer(c, page, total)


def slide_central_sequence(c, page, total):
    draw_slide_bg(c)
    y = title_block(c, "Sequence: Central Flagging (Namespaced)",
                    "Single evaluation path with project namespace isolation and shared governance")

    y_top = H - 48 * mm
    y_bot = 36 * mm
    actors = [
        (32 * mm, "Client"),
        (78 * mm, "App + SDK"),
        (135 * mm, "Flag API"),
        (190 * mm, "Namespace Store"),
        (245 * mm, "Admin / Ops"),
        (285 * mm, "Audit Log"),
    ]
    xs = [draw_sequence_actor(c, x, y_top, y_bot, name, color=TEAL if i != 4 else AMBER)
          for i, (x, name) in enumerate(actors)]

    steps = [
        (0, 1, "1. Request", TEAL),
        (1, 2, "2. eval(ns=payments, key=…)", TEAL),
        (2, 3, "3. Read namespaced rules", SLATE),
        (3, 2, "4. Flag definition + targeting", SLATE),
        (2, 1, "5. Decision + reason codes", TEAL),
        (2, 5, "6. Emit evaluation audit", MUTED),
        (4, 2, "7. Toggle / rollout (RBAC)", AMBER),
        (2, 5, "8. Change audit event", MUTED),
        (1, 0, "9. Consistent response", GOOD),
    ]
    for i, (a, b, text, col) in enumerate(steps):
        seq_msg(c, xs[a], xs[b], y_top - 10 * mm - i * 9.2 * mm, text, col)

    draw_footer(c, page, total)


def slide_namespace_model(c, page, total):
    draw_slide_bg(c)
    y = title_block(c, "Data Model: Project Namespaces",
                    "Isolation where you need it · sharing where you intend it")

    # tree-like layout
    rounded_box(c, 16 * mm, 95 * mm, 80 * mm, 28 * mm, TEAL, radius=6)
    c.setFillColor(white)
    c.setFont(BOLD, 11)
    c.drawCentredString(56 * mm, 110 * mm, "Organization")
    c.setFont(BODY, 8)
    c.drawCentredString(56 * mm, 102 * mm, "flag.company.internal")

    ns = [
        ("ns:payments", ["checkout_v2", "upi_retry", "kill.gateway"]),
        ("ns:lending", ["risk_model_b", "soft_pull", "checkout_v2 → ref"]),
        ("ns:onboarding", ["kyc_async", "selfie_qa"]),
        ("ns:global", ["maintenance_mode", "kill.edge_cdn"]),
    ]
    for i, (name, flags) in enumerate(ns):
        x = 16 * mm + i * 68 * mm
        rounded_box(c, x, 48 * mm, 62 * mm, 38 * mm, white, stroke=TEAL, radius=5)
        c.setFillColor(TEAL_DARK)
        c.setFont(BOLD, 9)
        c.drawString(x + 3 * mm, 76 * mm, name)
        c.setFillColor(SLATE)
        c.setFont(BODY, 7.5)
        for j, f in enumerate(flags):
            c.drawString(x + 3 * mm, 68 * mm - j * 5 * mm, "• " + f)
        arrow(c, 56 * mm, 95 * mm, x + 31 * mm, 86 * mm, color=TEAL)

    # notes
    points = [
        "Default: flags live under the owning project namespace (hard isolation).",
        "Optional: explicit references or global namespace for true cross-cutting kill switches.",
        "SDK always calls with project namespace — no accidental cross-project reads.",
        "Admin UI scopes operators to namespaces via RBAC.",
    ]
    yy = 38 * mm
    for p in points:
        yy = bullet(c, 16 * mm, yy, p, max_width=250 * mm)
    draw_footer(c, page, total)


def slide_mapping(c, page, total):
    draw_slide_bg(c)
    y = title_block(c, "Closing Every Drawback",
                    "Traceability from problem → central capability")

    rows = [
        ("Fragmented truth", "Single platform of record with namespaced keys"),
        ("Deploy toil / slow kills", "Admin API + UI toggles without app redeploy"),
        ("SDK inconsistency", "One SDK / one evaluation contract for all apps"),
        ("Weak governance", "RBAC, approvals, environments, full audit log"),
        ("Copied flag drift", "One definition; projects subscribe by namespace/ref"),
        ("Partial cross-app rollout", "Coordinated targeting or explicit global flags"),
        ("Ownership fog", "Namespace owners + mandatory metadata"),
        ("Analytics noise", "Stable flag IDs & reason codes in telemetry"),
    ]
    # header
    c.setFillColor(INK)
    c.roundRect(16 * mm, y - 2 * mm, W - 32 * mm, 9 * mm, 3, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont(BOLD, 9)
    c.drawString(20 * mm, y + 1 * mm, "Drawback (today)")
    c.drawString(120 * mm, y + 1 * mm, "Fulfilled by central flagging")

    for i, (left, right) in enumerate(rows):
        ryy = y - 14 * mm - i * 11 * mm
        c.setFillColor(white if i % 2 == 0 else TEAL_LIGHT)
        c.rect(16 * mm, ryy - 3 * mm, W - 32 * mm, 11 * mm, fill=1, stroke=0)
        c.setFillColor(BAD)
        c.setFont(BOLD, 8)
        c.drawString(20 * mm, ryy, left)
        c.setFillColor(GOOD)
        c.setFont(BODY, 8)
        c.drawString(120 * mm, ryy, "→  " + right)
    draw_footer(c, page, total)


def slide_pros(c, page, total):
    draw_slide_bg(c)
    y = title_block(c, "Pros of the Central Flagging Application",
                    "What teams gain once the control plane exists")

    pros = [
        ("Consistency", "Identical evaluation semantics across every project namespace."),
        ("Speed", "Instant kill switches and progressive delivery without waiting on deploys."),
        ("Safety", "Environment promotion, approvals, and blast-radius controls."),
        ("Clarity", "Namespace ownership makes who-owns-what unambiguous."),
        ("Observability", "Central audit of changes and evaluation samples."),
        ("Reuse", "Shared building blocks (targeting, segments, schedules) once."),
        ("Cost control", "Retire N flag stores / consoles / bespoke scripts."),
        ("Product velocity", "Experimentation becomes a platform capability, not a one-off."),
    ]
    for i, (t, d) in enumerate(pros):
        col = i % 4
        row = i // 4
        x = 16 * mm + col * 68 * mm
        yy = y - 10 * mm - row * 55 * mm
        rounded_box(c, x, yy - 40 * mm, 62 * mm, 48 * mm, GOOD_SOFT if row == 0 else TEAL_LIGHT,
                    stroke=GOOD if row == 0 else TEAL, radius=6)
        c.setFillColor(GOOD if row == 0 else TEAL_DARK)
        c.setFont(BOLD, 11)
        c.drawString(x + 4 * mm, yy - 4 * mm, t)
        c.setFillColor(SLATE)
        c.setFont(BODY, 8)
        words = d.split()
        line, ly = "", yy - 12 * mm
        for w in words:
            trial = (line + " " + w).strip()
            if c.stringWidth(trial, BODY, 8) < 54 * mm:
                line = trial
            else:
                c.drawString(x + 4 * mm, ly, line)
                ly -= 4.2 * mm
                line = w
        if line:
            c.drawString(x + 4 * mm, ly, line)
    draw_footer(c, page, total)


def slide_architecture_rights(c, page, total):
    """Right-sized architecture diagram (logical view)."""
    draw_slide_bg(c)
    y = title_block(c, "Target Architecture (Logical View)",
                    "Control plane, data plane, and project namespaces")

    # layers
    layers = [
        (H - 55 * mm, "Experience", [("Admin UI", TEAL), ("Change Approvals", AMBER), ("Dashboards", SLATE)]),
        (H - 85 * mm, "Control Plane", [("Flag API", TEAL), ("AuthZ / RBAC", INK), ("Webhook / Events", MUTED)]),
        (H - 115 * mm, "Data Plane", [("Eval Edge / CDN", TEAL_DARK), ("SDK Cache", TEAL), ("Streaming Sync", SLATE)]),
        (H - 145 * mm, "Persistence", [("Namespace Store", INK), ("Audit Log", CORAL), ("Segments", MUTED)]),
    ]
    for yy, label, boxes in layers:
        c.setFillColor(MUTED)
        c.setFont(BOLD, 8)
        c.drawString(16 * mm, yy + 8 * mm, label.upper())
        c.setStrokeColor(LINE)
        c.setDash(1, 2)
        c.line(42 * mm, yy + 10 * mm, W - 16 * mm, yy + 10 * mm)
        c.setDash()
        for i, (name, col) in enumerate(boxes):
            x = 50 * mm + i * 70 * mm
            rounded_box(c, x, yy - 2 * mm, 62 * mm, 14 * mm, white, stroke=col, radius=4)
            c.setFillColor(col)
            c.setFont(BOLD, 9)
            c.drawCentredString(x + 31 * mm, yy + 3 * mm, name)

    # projects strip
    c.setFillColor(TEAL_LIGHT)
    c.roundRect(16 * mm, 22 * mm, W - 32 * mm, 22 * mm, 5, fill=1, stroke=0)
    c.setFillColor(TEAL_DARK)
    c.setFont(BOLD, 9)
    c.drawString(22 * mm, 35 * mm, "Consumers (SDK):")
    c.setFont(BODY, 9)
    c.setFillColor(SLATE)
    c.drawString(60 * mm, 35 * mm, "payments   ·   lending   ·   onboarding   ·   admin   ·   …each bound to its namespace")
    c.setFillColor(MUTED)
    c.setFont(BODY, 8)
    c.drawString(22 * mm, 27 * mm, "Eval path is local-first (cached) with central authority for definitions — low latency, strong consistency of config.")
    draw_footer(c, page, total)


def slide_conclusion(c, page, total):
    gradient_rect(c, 0, 0, W, H, INK, TEAL_DARK, 64)
    c.setFillColor(AMBER)
    c.setFont(BOLD, 10)
    c.drawString(22 * mm, H - 28 * mm, "RECOMMENDATION")

    c.setFillColor(white)
    c.setFont(BOLD, 28)
    c.drawString(22 * mm, H - 48 * mm, "Adopt a central flagging platform")
    c.setFont(BODY, 13)
    c.setFillColor(HexColor("#B6D7D7"))
    c.drawString(22 * mm, H - 60 * mm, "with project-name namespaces as the isolation boundary")

    conclusions = [
        "Individual flag stores create fragmented truth, slow incidents, and inconsistent UX.",
        "Duplicating the “same” flags across repos guarantees drift, partial rollouts, and ownership fog.",
        "A central application restores a single control plane while namespaces preserve project autonomy.",
        "Every listed drawback maps to a concrete platform capability — not a process workaround.",
    ]
    yy = H - 80 * mm
    for text in conclusions:
        c.setFillColor(AMBER)
        c.circle(26 * mm, yy + 1.5 * mm, 1.4 * mm, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont(BODY, 11)
        c.drawString(32 * mm, yy, text)
        yy -= 12 * mm

    rounded_box(c, 22 * mm, 28 * mm, W - 44 * mm, 28 * mm, Color(1, 1, 1, alpha=0.1), radius=6)
    c.setFillColor(white)
    c.setFont(BOLD, 12)
    c.drawString(30 * mm, 44 * mm, "Next step")
    c.setFont(BODY, 10)
    c.setFillColor(HexColor("#D5ECEC"))
    c.drawString(30 * mm, 34 * mm,
                 "Stand up the central service + SDK, migrate one critical namespace (e.g. payments), then roll out by project.")
    c.setFillColor(HexColor("#94B8B8"))
    c.setFont(BODY, 9)
    c.drawRightString(W - 22 * mm, 14 * mm, f"{page} / {total}")


def build():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT), pagesize=PAGE)
    slides = [
        slide_title,
        slide_agenda,
        slide_current_state,
        slide_individual_sequence,
        slide_drawbacks_individual,
        slide_drawbacks_duplication,
        slide_solution_overview,
        slide_central_sequence,
        slide_namespace_model,
        slide_architecture_rights,
        slide_mapping,
        slide_pros,
        slide_conclusion,
    ]
    total = len(slides)
    for i, fn in enumerate(slides, 1):
        fn(c, i, total)
        c.showPage()
    c.save()
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
