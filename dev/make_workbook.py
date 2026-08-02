#!/usr/bin/env python3
"""Generate the printable Orbit Workbook (5th-grade companion to Dan's Orbit Simulator)."""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                PageBreak, Flowable, KeepTogether, Table, TableStyle)

OUT = ("/Users/alexanderhardt/Library/CloudStorage/OneDrive-AIACOTechnology/"
       "Documents - AIACO Trading Development/Pipeline Data/TradeBlocks Data/"
       "Dan's orbit simulator/orbit-workbook.pdf")

NAVY = HexColor('#1a2a4a')
BLUE = HexColor('#2b6cb8')
GOLD = HexColor('#b8791f')
GREEN = HexColor('#2f7d4f')
LGRAY = HexColor('#8a8a8a')
FILL_IDEA = HexColor('#eaf2fb')
FILL_TRY = HexColor('#fdf3df')
FILL_ACT = HexColor('#edf7ee')

W, H = letter
MARGIN = 0.8 * inch

st_title = ParagraphStyle('t', fontName='Helvetica-Bold', fontSize=30, leading=36,
                          textColor=NAVY, alignment=TA_CENTER)
st_sub = ParagraphStyle('s', fontName='Helvetica', fontSize=15, leading=20,
                        textColor=NAVY, alignment=TA_CENTER)
st_h = ParagraphStyle('h', fontName='Helvetica-Bold', fontSize=19, leading=23,
                      textColor=NAVY, spaceAfter=6)
st_hn = ParagraphStyle('hn', fontName='Helvetica-Bold', fontSize=12, leading=15,
                       textColor=BLUE, spaceAfter=2)
st_b = ParagraphStyle('b', fontName='Helvetica', fontSize=12.5, leading=17.5)
st_bc = ParagraphStyle('bc', parent=st_b, alignment=TA_CENTER)
st_small = ParagraphStyle('sm', fontName='Helvetica', fontSize=9.5, leading=13,
                          textColor=LGRAY)
st_box_h = ParagraphStyle('bh', fontName='Helvetica-Bold', fontSize=12.5, leading=16,
                          textColor=NAVY)
st_key = ParagraphStyle('k', fontName='Helvetica', fontSize=10, leading=14)


class Box(Flowable):
    """A rounded, filled box containing paragraphs."""
    def __init__(self, heading, body_paras, fill, width=None, pad=10):
        super().__init__()
        self.heading = heading
        self.paras = body_paras if isinstance(body_paras, list) else [body_paras]
        self.fill = fill
        self.pad = pad
        self.w = width or (W - 2 * MARGIN)

    def wrap(self, availWidth, availHeight):
        self.w = min(self.w, availWidth)
        iw = self.w - 2 * self.pad
        self.head_p = Paragraph(self.heading, st_box_h) if self.heading else None
        self.h = 2 * self.pad
        if self.head_p:
            _, hh = self.head_p.wrap(iw, availHeight)
            self.h += hh + 4
        self.body_sizes = []
        for p in self.paras:
            _, ph = p.wrap(iw, availHeight)
            self.body_sizes.append(ph)
            self.h += ph + 3
        return self.w, self.h

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(self.fill)
        c.setStrokeColor(NAVY)
        c.setLineWidth(0.8)
        c.roundRect(0, 0, self.w, self.h, 8, stroke=1, fill=1)
        iw = self.w - 2 * self.pad
        y = self.h - self.pad
        if self.head_p:
            _, hh = self.head_p.wrap(iw, 1000)
            self.head_p.drawOn(c, self.pad, y - hh)
            y -= hh + 4
        for p, ph in zip(self.paras, self.body_sizes):
            p.wrap(iw, 1000)
            p.drawOn(c, self.pad, y - ph)
            y -= ph + 3
        c.restoreState()


class Diagram(Flowable):
    def __init__(self, draw_fn, height=2.1 * inch):
        super().__init__()
        self.draw_fn = draw_fn
        self.h = height
        self.w = W - 2 * MARGIN

    def wrap(self, availWidth, availHeight):
        self.w = availWidth
        return self.w, self.h

    def draw(self):
        c = self.canv
        c.saveState()
        c.translate(self.w / 2, self.h / 2)   # origin at center of the strip
        self.draw_fn(c, self.w, self.h)
        c.restoreState()


def earth(c, x, y, r, label=True):
    c.setFillColor(HexColor('#cfe0f2'))
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.2)
    c.circle(x, y, r, stroke=1, fill=1)
    if label:
        c.setFillColor(NAVY)
        c.setFont('Helvetica-Bold', 9)
        c.drawCentredString(x, y - 3, 'Earth')


def moon(c, x, y, r, label='Moon'):
    c.setFillColor(HexColor('#e3e0d8'))
    c.setStrokeColor(HexColor('#6e6a60'))
    c.setLineWidth(1)
    c.circle(x, y, r, stroke=1, fill=1)
    if label:
        c.setFillColor(HexColor('#6e6a60'))
        c.setFont('Helvetica-Bold', 8)
        c.drawCentredString(x, y + r + 4, label)


def ship(c, x, y, r=3.4):
    c.setFillColor(GOLD)
    c.setStrokeColor(black)
    c.setLineWidth(0.7)
    c.circle(x, y, r, stroke=1, fill=1)


def ellipse_path(c, cx, cy, rx, ry, dashed=False, color=BLUE, width=1.4):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.setDash([4, 3] if dashed else [])
    c.ellipse(cx - rx, cy - ry, cx + rx, cy + ry, stroke=1, fill=0)
    c.setDash([])



def star5(c, x, y, r, color=GOLD):
    import math
    c.saveState()
    c.setFillColor(color)
    c.setStrokeColor(color)
    p = c.beginPath()
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.45
        a = math.pi / 2 + i * math.pi / 5
        px, py = x + rr * math.cos(a), y + rr * math.sin(a)
        (p.moveTo if i == 0 else p.lineTo)(px, py)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.restoreState()

# ---------- diagrams ----------
def d_cover(c, w, h):
    earth(c, 0, 0, 34)
    ellipse_path(c, 0, 0, 62, 50)
    ellipse_path(c, -28, 0, 105, 62, dashed=True, color=GREEN)
    ship(c, 62, 0, 4.5)
    moon(c, w * 0.34, 18, 13)
    c.setStrokeColor(LGRAY)
    c.setLineWidth(0.8)
    c.setDash([2, 3])
    c.circle(w * 0.34, 18, 30, stroke=1, fill=0)
    c.setDash([])
    for sx, sy in [(-w*0.4, h*0.32), (-w*0.3, -h*0.3), (w*0.42, -h*0.25), (w*0.18, h*0.38), (-w*0.15, h*0.42)]:
        c.setFillColor(NAVY)
        c.circle(sx, sy, 1.4, stroke=0, fill=1)


def d_three_paths(c, w, h):
    # three little pictures: drop, throw, orbit
    for i, x0 in enumerate([-w * 0.31, 0, w * 0.31]):
        earth(c, x0, -h * 0.18, 22, label=False)
        c.setFillColor(NAVY)
        c.setFont('Helvetica-Bold', 10)
        c.drawCentredString(x0, -h * 0.18 - 3, 'Earth')
        c.setFont('Helvetica-Bold', 11)
        c.drawCentredString(x0, h * 0.38, ['A', 'B', 'C'][i])
        c.setStrokeColor(GOLD)
        c.setLineWidth(1.6)
        if i == 0:      # straight down
            c.line(x0, h * 0.28, x0, -h * 0.18 + 24)
        elif i == 1:    # arc to ground
            p = c.beginPath()
            p.moveTo(x0 - 20, h * 0.1)
            p.curveTo(x0 + 6, h * 0.08, x0 + 20, -h * 0.02, x0 + 22, -h * 0.18 + 20)
            c.drawPath(p)
        else:           # full circle
            c.ellipse(x0 - 32, -h * 0.18 - 32, x0 + 32, -h * 0.18 + 32, stroke=1, fill=0)
        ship(c, x0, h * 0.28 if i == 0 else (h * 0.1 if i == 1 else -h * 0.18 + 32))


def d_orbit_star(c, w, h):
    earth(c, 0, 0, 26)
    ellipse_path(c, 0, 0, 78, 58)
    ship(c, 78, 0)
    # star = burn point
    star5(c, 78, 14, 8)
    c.setFillColor(NAVY)
    c.setFont('Helvetica', 9)
    c.drawCentredString(78, -18, 'you fire here')


def d_two_markers(c, w, h):
    for i, x0 in enumerate([-w * 0.24, w * 0.24]):
        earth(c, x0, 0, 20, label=False)
        ellipse_path(c, x0, 0, 52, 40)
        mx = x0 + 52 if i == 0 else x0 - 52
        c.setStrokeColor(GOLD)
        c.setLineWidth(1.4)
        c.circle(mx, 0, 8, stroke=1, fill=0)
        c.setFillColor(GOLD)
        c.setFont('Helvetica-Bold', 10)
        c.drawCentredString(mx, -3.5, 'A' if i == 0 else 'B')
        c.setFillColor(NAVY)
        c.setFont('Helvetica-Bold', 10)
        c.drawCentredString(x0, -58, ['Picture 1: burn at A', 'Picture 2: burn at B'][i])


def d_transfer(c, w, h):
    earth(c, 0, 0, 18)
    ellipse_path(c, 0, 0, 34, 34)                      # low orbit
    ellipse_path(c, 0, 0, 88, 88, dashed=True, color=GOLD)   # target
    ellipse_path(c, -27, 0, 61, 50, color=GREEN, dashed=True)  # transfer
    c.setFillColor(GREEN)
    c.setFont('Helvetica-Bold', 11)
    c.circle(34, 0, 7, stroke=1, fill=0)
    c.drawCentredString(34, -4, '1')
    c.circle(-88, 0, 7, stroke=1, fill=0)
    c.drawCentredString(-88, -4, '2')
    c.setFillColor(NAVY)
    c.setFont('Helvetica', 9)
    c.drawCentredString(0, -96, 'Burn 1 stretches the orbit up. Burn 2 makes it round again.')


def d_reentry(c, w, h):
    earth(c, 0, -6, 26)
    c.setStrokeColor(HexColor('#7fb2e0'))
    c.setLineWidth(5)
    c.circle(0, -6, 32, stroke=1, fill=0)   # atmosphere band
    ellipse_path(c, 26, -6, 62, 44, color=BLUE)
    ship(c, 88, -6)
    c.setFillColor(NAVY)
    c.setFont('Helvetica', 9)
    c.drawCentredString(0, -70, 'The low point dips into the air blanket - the air slows you down for free.')


def d_arrows(c, w, h):
    ship(c, 0, 0, 5)
    c.setFont('Helvetica-Bold', 10)
    arrows = [((60, 0), 'forward push', GREEN), ((0, 46), 'sideways push', GOLD), ((-60, 0), 'backward push', BLUE)]
    for (dx, dy), lab, col in arrows:
        c.setStrokeColor(col)
        c.setLineWidth(2)
        c.line(0, 0, dx, dy)
        # arrowhead
        import math
        ang = math.atan2(dy, dx)
        for s in (-1, 1):
            c.line(dx, dy, dx - 9 * math.cos(ang + s * 0.45), dy - 9 * math.sin(ang + s * 0.45))
        c.setFillColor(col)
        off = 12 if dy else 10
        c.drawCentredString(dx * 1.28 if dx else 0, dy + off if dy else -16, lab)


def d_open_closed(c, w, h):
    # closed orbit
    earth(c, -w * 0.24, -6, 20, label=False)
    ellipse_path(c, -w * 0.24, -6, 50, 38)
    c.setFillColor(NAVY)
    c.setFont('Helvetica-Bold', 10)
    c.drawCentredString(-w * 0.24, -60, 'slower: path stays closed')
    # open path
    earth(c, w * 0.24, -6, 20, label=False)
    c.setStrokeColor(BLUE)
    c.setLineWidth(1.4)
    p = c.beginPath()
    p.moveTo(w * 0.24 + 85, 52)
    p.curveTo(w * 0.24 + 10, 18, w * 0.24 + 10, -30, w * 0.24 + 85, -64)
    c.drawPath(p)
    c.drawCentredString(w * 0.24, -60 - 0, '')
    c.setFillColor(NAVY)
    c.drawCentredString(w * 0.24, -80 + 20, 'faster than escape speed:')
    c.drawCentredString(w * 0.24, -80 + 8, 'the path tears open!')


def d_moon_lead(c, w, h):
    earth(c, -w * 0.28, 0, 16)
    ellipse_path(c, -w * 0.28, 0, 26, 26)
    ship(c, -w * 0.28 + 26, 0)
    moon(c, w * 0.1, 52, 10, label='Moon NOW')
    c.setStrokeColor(LGRAY)
    c.setLineWidth(0.9)
    c.setDash([2, 3])
    c.circle(w * 0.33, -18, 10, stroke=1, fill=0)
    c.setDash([])
    c.setFillColor(LGRAY)
    c.setFont('Helvetica-Bold', 8)
    c.drawCentredString(w * 0.33, -18 - 20, 'Moon LATER (ghost)')
    ellipse_path(c, -w * 0.05, -8, 130, 52, dashed=True, color=GREEN)


def d_insertion(c, w, h):
    moon(c, 0, 0, 16, label='Moon')
    c.setStrokeColor(LGRAY)
    c.setLineWidth(0.9)
    c.setDash([3, 4])
    c.circle(0, 0, 78, stroke=1, fill=0)
    c.setDash([])
    # flyby curve
    c.setStrokeColor(BLUE)
    c.setLineWidth(1.4)
    p = c.beginPath()
    p.moveTo(120, 46)
    p.curveTo(20, 30, -30, 10, -26, -20)
    p.curveTo(-22, -50, 40, -60, 120, -58)
    c.drawPath(p)
    ellipse_path(c, 12, -22, 40, 26, dashed=True, color=GREEN)
    star5(c, -26, -20, 8, color=GREEN)
    c.setFillColor(NAVY)
    c.setFont('Helvetica', 9)
    c.drawCentredString(0, -95, 'Brake at the star (closest point) and the path closes into a loop!')


# ---------- content helpers ----------
def P(text, style=st_b):
    return Paragraph(text, style)


def lesson_header(num, title, story):
    story.append(Paragraph(f'LESSON {num}', st_hn))
    story.append(Paragraph(title, st_h))


def write_line(label='', n=1):
    line = '_' * 58
    txt = (label + '<br/>' if label else '') + ('<br/>'.join([line] * n))
    return P(txt)


doc = BaseDocTemplate(OUT, pagesize=letter,
                      leftMargin=MARGIN, rightMargin=MARGIN,
                      topMargin=0.7 * inch, bottomMargin=0.7 * inch,
                      title="My Orbit Workbook", author="goodorigamiman")


def footer(canvas, doc_):
    canvas.saveState()
    canvas.setFont('Helvetica', 8.5)
    canvas.setFillColor(LGRAY)
    canvas.drawCentredString(W / 2, 0.42 * inch,
                             f'My Orbit Workbook  ·  page {doc_.page}  ·  use with Dan’s Orbit Simulator')
    canvas.restoreState()


frame = Frame(MARGIN, 0.7 * inch, W - 2 * MARGIN, H - 1.4 * inch, id='main')
doc.addPageTemplates([PageTemplate(id='page', frames=[frame], onPage=footer)])

story = []

# ================= COVER =================
story.append(Spacer(1, 40))
story.append(Paragraph('My Orbit Workbook', st_title))
story.append(Spacer(1, 8))
story.append(Paragraph('How to fly a spaceship around the Earth — and all the way to the Moon!', st_sub))
story.append(Spacer(1, 20))
story.append(Diagram(d_cover, 2.6 * inch))
story.append(Spacer(1, 30))
story.append(Paragraph('This workbook belongs to:', st_bc))
story.append(Spacer(1, 6))
story.append(Paragraph('_' * 40, st_bc))
story.append(Spacer(1, 30))
story.append(Paragraph('Works together with <b>Dan’s Orbit Simulator</b><br/>goodorigamiman.github.io/dans-orbit-simulator', st_bc))
story.append(PageBreak())

# ================= HOW TO USE + WORDS =================
story.append(Paragraph('How to use this workbook', st_h))
story.append(P('This book goes with the <b>Orbit Simulator</b> — the computer game where you '
               'fly a little spaceship around the Earth. The simulator has 9 lessons. '
               'This book has the same 9 lessons.'))
story.append(Spacer(1, 6))
story.append(P('For each lesson: <b>1)</b> read the Big Idea here, <b>2)</b> try it in the '
               'simulator, <b>3)</b> come back and finish the puzzles on paper. '
               'Answers are hiding on the last page — no peeking until you try!'))
story.append(Spacer(1, 14))
story.append(Paragraph('Space words (your astronaut dictionary)', st_h))
words = [
    ('orbit', 'the path a spaceship follows as it circles a planet or moon'),
    ('prograde', 'firing your engine FORWARD, the way you are already going (speeds you up)'),
    ('retrograde', 'firing your engine BACKWARD, against your motion (slows you down)'),
    ('high point', 'the tallest spot of your orbit (grown-ups say "apoapsis")'),
    ('low point', 'the lowest spot of your orbit (grown-ups say "periapsis")'),
    ('fuel push (delta-v)', 'how much total push your engine has given — the fuel money of space'),
    ('escape velocity', 'the speed where you break free and never come back'),
    ('sphere of influence', 'the Moon’s neighborhood — inside it, the Moon’s gravity is the boss'),
    ('transfer', 'a trip from one orbit to another'),
    ('capture', 'getting caught by a moon’s gravity so you loop around it'),
]
rows = [[Paragraph(f'<b>{w}</b>', st_b), Paragraph(d, st_b)] for w, d in words]
t = Table(rows, colWidths=[1.7 * inch, W - 2 * MARGIN - 1.7 * inch])
t.setStyle(TableStyle([
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('ROWBACKGROUNDS', (0, 0), (-1, -1), [white, HexColor('#f2f6fb')]),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
]))
story.append(t)
story.append(PageBreak())

# ================= LESSON 1 =================
lesson_header(1, 'What is an orbit?', story)
story.append(Box('The Big Idea', [
    P('A spaceship in orbit is <b>falling</b> the whole time! It moves sideways SO fast '
      'that as it falls, the round Earth curves away underneath it. So it keeps falling… '
      'and keeps missing the ground… forever. That is an orbit: <b>falling sideways and '
      'always missing.</b>'),
], FILL_IDEA))
story.append(Spacer(1, 8))
story.append(Box('Try it in the simulator', [
    P('Open Lesson 1. Just watch the ship go around once or twice. Slide the <b>time warp</b> '
      'to make time go faster. Nothing is holding the ship up!'),
], FILL_TRY))
story.append(Spacer(1, 8))
story.append(Box('Your turn', [
    P('<b>1.</b> A ball is let go near Earth in three different ways. '
      '<b>Circle the picture</b> that shows an orbit:'),
], FILL_ACT))
story.append(Diagram(d_three_paths, 2.3 * inch))
story.append(Box(None, [
    P('<b>2.</b> Fill in the blank:  An orbit is falling <b>_______________</b> forever.'),
    P('<b>3.</b> True or false (circle one):  Astronauts float because there is no gravity in space. '
      '&nbsp;&nbsp;<b>TRUE&nbsp;&nbsp;/&nbsp;&nbsp;FALSE</b>'),
    P('<i>Hint: they float because they are FALLING, together with their ship!</i>', st_small),
], FILL_ACT))
story.append(PageBreak())

# ================= LESSON 2 =================
lesson_header(2, 'Raise the far side', story)
story.append(Box('The Big Idea', [
    P('Here is the most surprising rule in all of space flying: when you fire your engine, '
      'your orbit does NOT change where you are. It changes on the <b>OPPOSITE side</b> of '
      'the planet — half a lap away! Speeding up makes the <b>far side</b> of your loop '
      'stretch up higher.'),
], FILL_IDEA))
story.append(Spacer(1, 8))
story.append(Box('Try it in the simulator', [
    P('Open Lesson 2. Hold the <b>Prograde (forward)</b> button and watch the orange "changes here" '
      'marker — it is always across from you! Push your high point above 1,000 km.'),
], FILL_TRY))
story.append(Spacer(1, 8))
story.append(Box('Your turn', [
    P('<b>1.</b> The ship fires its engine at the gold star. '
      '<b>Draw a big X</b> where the orbit will get higher:'),
], FILL_ACT))
story.append(Diagram(d_orbit_star, 2.0 * inch))
story.append(Box(None, [
    P('<b>2.</b> Fill in the blank:  A burn changes the <b>_______________</b> side of the orbit.'),
    P('<b>3.</b> Copy the rule (this one is worth remembering forever):'),
    P('<i>"Where I burn decides how much. Where the orbit changes is across from me."</i>'),
    write_line(n=2),
], FILL_ACT))
story.append(PageBreak())

# ================= LESSON 3 =================
lesson_header(3, 'Where you burn matters', story)
story.append(Box('The Big Idea', [
    P('Same engine. Same push. Different spot = a totally different orbit! '
      'If you burn at point A, the bulge grows across from A. If you burn at point B, '
      'the bulge grows across from B. The <b>place</b> you burn picks the <b>shape</b> '
      'of your new orbit.'),
], FILL_IDEA))
story.append(Spacer(1, 8))
story.append(Box('Try it in the simulator', [
    P('Open Lesson 3. Burn 40 m/s near marker A, look at the shape. Then reset and burn '
      'the same amount near B. Compare!'),
], FILL_TRY))
story.append(Spacer(1, 8))
story.append(Box('Your turn', [
    P('<b>1.</b> In each picture, <b>draw the bulge</b> (the stretched part of the orbit) '
      'where it belongs:'),
], FILL_ACT))
story.append(Diagram(d_two_markers, 2.1 * inch))
story.append(Box(None, [
    P('<b>2.</b> Predict, then check in the simulator:  If you burn at the TOP of the orbit, '
      'the bulge appears at the <b>___________________</b> of the orbit.'),
    P('<b>3.</b> Circle one:  The engine decides <b>how much</b> the orbit changes. '
      'The burn spot decides <b>WHERE / WHY</b> it changes.'),
], FILL_ACT))
story.append(PageBreak())

# ================= LESSON 4 =================
lesson_header(4, 'The two-burn transfer', story)
story.append(Box('The Big Idea', [
    P('One burn can only stretch ONE side of your orbit. So how do you move your WHOLE '
      'orbit higher? You need <b>two burns</b>: <b>Burn 1</b> stretches the far side up. '
      'Then you coast to the top and do <b>Burn 2</b>, which lifts the side you left '
      'behind. Two burns, two places — and your orbit is a big circle. '
      'Real rocket scientists call this a <b>Hohmann transfer</b>.'),
], FILL_IDEA))
story.append(Spacer(1, 8))
story.append(Box('Try it in the simulator', [
    P('Open Lesson 4. Use the <b>flight plan</b>: add burn 1 at the low point and burn 2 at '
      'the high point, look at the dashed preview, then press Execute and watch both burns fly.'),
], FILL_TRY))
story.append(Spacer(1, 8))
story.append(Diagram(d_transfer, 2.9 * inch))
story.append(Box('Your turn', [
    P('<b>1.</b> Put these steps in order. Write 1, 2, 3, 4:'),
    P('___ Coast (no engine) halfway around, up to the new high point<br/>'
      '___ Fire forward to stretch the far side up<br/>'
      '___ Enjoy your new, bigger circle!<br/>'
      '___ Fire forward again to lift the low side'),
    P('<b>2.</b> Fill in the blank:  Moving BOTH sides of an orbit takes <b>________</b> burns.'),
], FILL_ACT))
story.append(PageBreak())

# ================= LESSON 5 =================
lesson_header(5, 'Coming home', story)
story.append(Box('The Big Idea', [
    P('To come home, you do NOT point at the Earth and fire. You simply <b>slow down</b>. '
      'Braking lowers the opposite side of your orbit until it dips into the '
      '<b>air blanket</b> around Earth (the atmosphere). Then the air rubs against your '
      'ship and slows you down the rest of the way — for free!'),
], FILL_IDEA))
story.append(Spacer(1, 8))
story.append(Box('Try it in the simulator', [
    P('Open Lesson 5. Hold <b>Retrograde (backward)</b> until your low point drops under 80 km. '
      'Then keep coasting and watch re-entry happen.'),
], FILL_TRY))
story.append(Spacer(1, 8))
story.append(Diagram(d_reentry, 2.15 * inch))
story.append(Box('Your turn', [
    P('<b>1.</b> Circle the right way to come home:'),
    P('&nbsp;&nbsp;&nbsp;a) Point at the Earth and fire the engine hard<br/>'
      '&nbsp;&nbsp;&nbsp;b) Slow down, and let the orbit dip into the air'),
    P('<b>2.</b> Fill in the blank:  The <b>___________________</b> slows the ship down for '
      'free at the end.'),
    P('<b>3.</b> True or false:  You never "fly down" — you slow down HERE and the orbit '
      'dips over THERE. &nbsp;&nbsp;<b>TRUE&nbsp;&nbsp;/&nbsp;&nbsp;FALSE</b>'),
], FILL_ACT))
story.append(PageBreak())

# ================= LESSON 6 =================
lesson_header(6, 'Steering the burn', story)
story.append(Box('The Big Idea', [
    P('Engines can point in different directions! A <b>forward</b> push makes your orbit '
      'BIGGER. A <b>backward</b> push makes it SMALLER. A <b>sideways</b> push mostly just '
      '<b>tilts and turns</b> the orbit — it hardly grows at all. That is why real '
      'astronauts almost always burn forward or backward: it buys the most orbit for '
      'your fuel.'),
], FILL_IDEA))
story.append(Spacer(1, 8))
story.append(Box('Try it in the simulator', [
    P('Open Lesson 6. Slide <b>Steer</b> to 60° or more, then hold Prograde and burn 40 m/s. '
      'See how little the orbit grows? Now try the same burn with Steer at 0°.'),
], FILL_TRY))
story.append(Spacer(1, 8))
story.append(Diagram(d_arrows, 1.8 * inch))
story.append(Box('Your turn', [
    P('<b>1.</b> Draw a line to match each push to what it does:'),
    P('forward push&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;tilts / turns the orbit<br/><br/>'
      'sideways push&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;makes the orbit bigger<br/><br/>'
      'backward push&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;makes the orbit smaller'),
    P('<b>2.</b> Circle one:  To grow your orbit with the least fuel, push '
      '<b>FORWARD / SIDEWAYS</b>.'),
], FILL_ACT))
story.append(PageBreak())

# ================= LESSON 7 =================
lesson_header(7, 'Breaking free (escape velocity)', story)
story.append(Box('The Big Idea', [
    P('At every height there is a magic speed called <b>escape velocity</b>. Go slower, '
      'and gravity always bends your path into a loop that comes back. Go faster, and the '
      'loop <b>tears open</b> — you fly away and NEVER come back. Near Earth, circling '
      'speed is about 7.7 km every second. Escape speed is about 10.9 — '
      'about <b>1.4 times</b> faster. That "1.4 times" rule works at every planet and moon!'),
], FILL_IDEA))
story.append(Spacer(1, 8))
story.append(Box('Try it in the simulator', [
    P('Open Lesson 7. Execute the big burn (or hold Prograde a long time) and watch the '
      '"high point" number climb… and climb… until it says <b>infinity</b> (a sideways 8). '
      'Your path is open — you broke free!'),
], FILL_TRY))
story.append(Spacer(1, 8))
story.append(Diagram(d_open_closed, 2.1 * inch))
story.append(Box('Your turn', [
    P('<b>1.</b> Near Earth: 7.7 km/s = circling speed. 10.9 km/s = escape speed. '
      'A ship is going 9 km/s. Circle one: it <b>STAYS / LEAVES</b>.'),
    P('<b>2.</b> Fill in the blank:  When you break free, the high point reads '
      '<b>________</b> (a sideways 8!).'),
    P('<b>3.</b> True or false:  Once past escape speed you can still turn back if you '
      'brake soon. &nbsp;&nbsp;<b>TRUE&nbsp;&nbsp;/&nbsp;&nbsp;FALSE</b>'),
], FILL_ACT))
story.append(PageBreak())

# ================= LESSON 8 =================
lesson_header(8, 'Lead the Moon', story)
story.append(Box('The Big Idea', [
    P('The Moon is always <b>moving</b>. If you aim at where the Moon is NOW, you will '
      'arrive at empty space — the Moon will have moved on! You must throw yourself at '
      'where the Moon <b>WILL BE</b>, like leading a running friend with a football. '
      'Space pilots call the right moment to leave a <b>transfer window</b>.'),
], FILL_IDEA))
story.append(Spacer(1, 8))
story.append(Box('Try it in the simulator', [
    P('Open Lesson 8. Mission control loaded your departure burn already. See the '
      '<b>ghost Moon</b>? That is where the Moon will be when you arrive. Execute the '
      'plan and coast into the Moon’s neighborhood (the dashed circle).'),
], FILL_TRY))
story.append(Spacer(1, 8))
story.append(Diagram(d_moon_lead, 2.2 * inch))
story.append(Box('Your turn', [
    P('<b>1.</b> You throw a ball to a friend who is running. Where do you throw it? Circle one:'),
    P('&nbsp;&nbsp;&nbsp;a) Right at your friend&nbsp;&nbsp;&nbsp;'
      'b) At the spot your friend is running TO'),
    P('<b>2.</b> Fill in the blank:  The dashed circle around the Moon is its sphere of '
      '<b>___________________</b> — inside it, the Moon’s gravity is the boss.'),
    P('<b>3.</b> In the picture above, <b>draw an arrow</b> from the rocket’s path to the '
      'ghost Moon — that’s your meeting spot!'),
], FILL_ACT))
story.append(PageBreak())

# ================= LESSON 9 =================
lesson_header(9, 'Catching the Moon (lunar orbit insertion)', story)
story.append(Box('The Big Idea', [
    P('You arrive at the Moon going TOO FAST to stay. Do nothing, and the Moon’s '
      'gravity slings you right back out into space! <b>Arriving is braking:</b> at your '
      'closest point to the Moon, fire <b>backward</b> until your path closes into a loop. '
      'Now the Moon’s gravity can hold you — you are <b>captured</b>. Every real Moon '
      'mission does exactly this. And careful: the Moon has <b>no air</b>, so nothing '
      'slows you down for free there!'),
], FILL_IDEA))
story.append(Spacer(1, 8))
story.append(Box('Try it in the simulator', [
    P('Open Lesson 9. Mission control loaded the braking burn. Execute it — or try '
      'flying past WITHOUT braking first, and feel the slingshot throw you home!'),
], FILL_TRY))
story.append(Spacer(1, 8))
story.append(Diagram(d_insertion, 2.95 * inch))
story.append(Box('Your turn', [
    P('<b>1.</b> Fill in the blank:  To get captured, brake when you are '
      '<b>___________________</b> to the Moon.'),
    P('<b>2.</b> Circle one:  On the Moon there is <b>NO AIR / THICK AIR</b>, so all your '
      'braking must come from your engine.'),
    P('<b>3.</b> True or false:  If you skip the brake, the Moon slings you back toward '
      'Earth. &nbsp;&nbsp;<b>TRUE&nbsp;&nbsp;/&nbsp;&nbsp;FALSE</b>'),
], FILL_ACT))
story.append(PageBreak())

# ================= BIG QUIZ =================
story.append(Paragraph('The Big Astronaut Quiz', st_h))
story.append(P('You made it through all 9 lessons! Show what you know. (Answers on the last page.)'))
story.append(Spacer(1, 10))
story.append(Box('Part 1 — Match the word to its meaning (draw lines)', [
    P('prograde&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;the lowest spot of an orbit<br/><br/>'
      'retrograde&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;firing your engine forward<br/><br/>'
      'high point&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;getting caught by the Moon’s gravity<br/><br/>'
      'low point&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;the speed of no return<br/><br/>'
      'escape velocity&nbsp;&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;firing your engine backward<br/><br/>'
      'capture&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;the tallest spot of an orbit'),
], FILL_ACT))
story.append(Spacer(1, 10))
story.append(Box('Part 2 — True or false (circle)', [
    P('1. A burn changes the orbit on the opposite side. &nbsp;&nbsp;<b>T / F</b>'),
    P('2. One burn is enough to make your whole orbit bigger and round. &nbsp;&nbsp;<b>T / F</b>'),
    P('3. To come home from Earth orbit, you slow down. &nbsp;&nbsp;<b>T / F</b>'),
    P('4. To aim for the Moon, fire toward where the Moon is right now. &nbsp;&nbsp;<b>T / F</b>'),
    P('5. Sideways pushes are the best way to make an orbit bigger. &nbsp;&nbsp;<b>T / F</b>'),
    P('6. At the Moon, you must brake with your engine — there is no air to help. &nbsp;&nbsp;<b>T / F</b>'),
], FILL_ACT))
story.append(PageBreak())

# ================= CERTIFICATE =================
story.append(Spacer(1, 50))
story.append(Paragraph('Certificate of Orbit Mastery', ParagraphStyle(
    'cert', parent=st_title, fontSize=24, leading=30)))
story.append(Spacer(1, 24))
story.append(Paragraph('This certifies that space pilot', st_bc))
story.append(Spacer(1, 10))
story.append(Paragraph('_' * 40, st_bc))
story.append(Spacer(1, 20))
story.append(Paragraph('has learned how orbits really work:<br/><br/>'
                       'burns change the <b>opposite side</b> · big moves take <b>two burns</b> ·<br/>'
                       'coming home means <b>slowing down</b> · breaking free takes <b>escape velocity</b> ·<br/>'
                       'you aim where the Moon <b>will be</b> · and <b>arriving is braking</b>.',
                       st_bc))
story.append(Spacer(1, 36))
t2 = Table([[Paragraph('_' * 22 + '<br/>Teacher / Mission Control', st_bc),
             Paragraph('_' * 22 + '<br/>Date', st_bc)]],
           colWidths=[(W - 2 * MARGIN) / 2] * 2)
story.append(t2)
story.append(PageBreak())

# ================= ANSWER KEY =================
story.append(Paragraph('Answer key (no peeking until you tried!)', st_h))
ak = [
    ('Lesson 1', '1: picture C.  2: "sideways".  3: FALSE — they float because they are falling with their ship.'),
    ('Lesson 2', '1: the X goes on the LEFT side, straight across from the star.  2: "opposite".'),
    ('Lesson 3', '2: bottom.  3: WHERE.'),
    ('Lesson 4', '1: order is 2, 1, 4, 3.  2: two.'),
    ('Lesson 5', '1: b.  2: "air" (the atmosphere).  3: TRUE.'),
    ('Lesson 6', '1: forward = bigger, sideways = tilts/turns, backward = smaller.  2: FORWARD.'),
    ('Lesson 7', '1: STAYS (9 is less than 10.9).  2: infinity (the sideways 8).  3: TRUE.'),
    ('Lesson 8', '1: b.  2: "influence".'),
    ('Lesson 9', '1: closest.  2: NO AIR.  3: TRUE.'),
    ('Quiz Part 1', 'prograde = forward · retrograde = backward · high point = tallest spot · '
                    'low point = lowest spot · escape velocity = speed of no return · capture = caught by the Moon.'),
    ('Quiz Part 2', '1 T · 2 F (you need two burns) · 3 T · 4 F (aim where it WILL be) · '
                    '5 F (forward pushes grow orbits best) · 6 T.'),
]
rows = [[Paragraph(f'<b>{a}</b>', st_key), Paragraph(b, st_key)] for a, b in ak]
t3 = Table(rows, colWidths=[1.2 * inch, W - 2 * MARGIN - 1.2 * inch])
t3.setStyle(TableStyle([
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('ROWBACKGROUNDS', (0, 0), (-1, -1), [white, HexColor('#f2f6fb')]),
    ('TOPPADDING', (0, 0), (-1, -1), 3),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
]))
story.append(t3)
story.append(Spacer(1, 18))
story.append(P('Made to go with Dan’s Orbit Simulator — '
               'goodorigamiman.github.io/dans-orbit-simulator', st_small))

doc.build(story)
print('wrote', OUT)
