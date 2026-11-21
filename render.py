#!/usr/bin/env python3
"""Draw an invented passport spread for the fictional Republic of Narellia.

Original artwork generated programmatically with PIL. Writes entry.png
(1024x1024) next to this file. Deterministic: no randomness.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
HERE = os.path.dirname(os.path.abspath(__file__))

F_SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
F_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
F_MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, s, f):
    box = draw.textbbox((0, 0), s, font=f)
    return box[2] - box[0]


def centered(draw, cx, y, s, f, fill):
    draw.text((cx - text_w(draw, s, f) / 2, y), s, font=f, fill=fill)


# ---------- palette ----------
DESK = (52, 58, 66)
PAGE = (238, 236, 224)
PAGE_EDGE = (205, 200, 182)
INK = (38, 44, 58)
FAINT = (150, 156, 168)
RULE = (120, 126, 140)
NAVY = (24, 48, 92)
TEAL = (18, 96, 92)
STAMP_BLUE = (36, 64, 150)
STAMP_RED = (150, 44, 44)
STAMP_GREEN = (28, 110, 70)


def wave_pattern(draw, box, color):
    """Faint guilloche of overlapping sine waves (the sea, on every page)."""
    x0, y0, x1, y1 = box
    step = 26
    for row, yy in enumerate(range(y0 + 8, y1 - 8, step)):
        pts = []
        for x in range(x0 + 4, x1 - 4, 4):
            pts.append((x, yy + 5 * math.sin((x + row * 37) / 34.0)))
        draw.line(pts, fill=color, width=1)


def draw_portrait(draw, box):
    """Flat, passport-photo style portrait of the holder."""
    x0, y0, x1, y1 = box
    # photo background
    draw.rectangle(box, fill=(196, 206, 214))
    cx = (x0 + x1) // 2
    # shoulders / coat (dark harbour-master blue)
    draw.polygon(
        [(cx - 78, y1), (cx - 60, y0 + 150), (cx - 26, y0 + 132),
         (cx + 26, y0 + 132), (cx + 60, y0 + 150), (cx + 78, y1)],
        fill=(44, 58, 84),
    )
    # shirt triangle + collar
    draw.polygon([(cx - 20, y0 + 136), (cx + 20, y0 + 136), (cx, y0 + 176)],
                 fill=(232, 230, 222))
    # neck
    draw.rectangle([cx - 13, y0 + 108, cx + 13, y0 + 142], fill=(198, 152, 120))
    # head
    draw.ellipse([cx - 42, y0 + 26, cx + 42, y0 + 122], fill=(214, 168, 132))
    # hair (dark, swept back, tied) + bun
    draw.pieslice([cx - 46, y0 + 16, cx + 46, y0 + 96], 180, 360, fill=(52, 40, 34))
    draw.ellipse([cx - 14, y0 + 4, cx + 14, y0 + 30], fill=(52, 40, 34))
    draw.rectangle([cx - 46, y0 + 58, cx - 38, y0 + 100], fill=(52, 40, 34))
    draw.rectangle([cx + 38, y0 + 58, cx + 46, y0 + 100], fill=(52, 40, 34))
    # ears
    draw.ellipse([cx - 48, y0 + 70, cx - 38, y0 + 88], fill=(214, 168, 132))
    draw.ellipse([cx + 38, y0 + 70, cx + 48, y0 + 88], fill=(214, 168, 132))
    # eyes, brows, nose, mouth
    for sgn in (-1, 1):
        ex = cx + sgn * 17
        draw.arc([ex - 8, y0 + 62, ex + 8, y0 + 72], 200, 340, fill=(40, 32, 28), width=2)
        draw.ellipse([ex - 2, y0 + 66, ex + 2, y0 + 70], fill=(40, 32, 28))
        draw.line([(ex - 9, y0 + 57), (ex + 9, y0 + 55)], fill=(52, 40, 34), width=3)
    draw.line([(cx, y0 + 74), (cx - 3, y0 + 90)], fill=(178, 134, 102), width=2)
    draw.arc([cx - 11, y0 + 92, cx + 11, y0 + 104], 15, 165, fill=(150, 84, 76), width=2)
    # frame
    draw.rectangle(box, outline=(90, 96, 108), width=2)


def field(draw, x, y, label, value, lw=196):
    """One data-page field: small caps label above value, thin rule under."""
    draw.text((x, y), label, font=font(F_SANS, 11), fill=FAINT)
    draw.text((x, y + 14), value, font=font(F_SANS_B, 17), fill=INK)
    draw.line([(x, y + 40), (x + lw, y + 40)], fill=RULE, width=1)


def make_stamp(kind, lines, color, w, h, angle):
    """Render one ink stamp on its own layer, rotated, semi-transparent."""
    pad = 30
    layer = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    ink = color + (205,)
    if kind == "rect":
        d.rounded_rectangle([pad, pad, pad + w, pad + h], radius=8, outline=ink, width=3)
        d.rounded_rectangle([pad + 5, pad + 5, pad + w - 5, pad + h - 5], radius=6,
                            outline=ink, width=1)
    else:  # round
        d.ellipse([pad, pad, pad + w, pad + h], outline=ink, width=3)
        d.ellipse([pad + 6, pad + 6, pad + w - 6, pad + h - 6], outline=ink, width=1)
    total = sum(s for _, s in lines) + 4 * (len(lines) - 1)
    y = pad + (h - total) / 2
    for txt, size in lines:
        f = font(F_SANS_B, size)
        d.text((pad + (w - text_w(d, txt, f)) / 2, y), txt, font=f, fill=ink)
        y += size + 4
    return layer.rotate(angle, expand=True, resample=Image.BICUBIC)


def paste_stamp(img, stamp, cx, cy):
    img.alpha_composite(stamp, (int(cx - stamp.width / 2), int(cy - stamp.height / 2)))


def main():
    img = Image.new("RGBA", (W, H), DESK + (255,))
    d = ImageDraw.Draw(img)

    # open spread: two pages with a soft centre fold
    spread = (36, 66, 988, 958)
    d.rounded_rectangle(spread, radius=10, fill=PAGE)
    wave_pattern(d, (spread[0] + 6, spread[1] + 6, 512, spread[3] - 6), (216, 222, 226))
    wave_pattern(d, (512, spread[1] + 6, spread[2] - 6, spread[3] - 6), (216, 222, 226))
    # fold shading
    for i in range(18):
        shade = 232 - i * 3
        d.line([(512 - i, spread[1] + 4), (512 - i, spread[3] - 4)], fill=(shade, shade - 2, shade - 14))
        d.line([(512 + i, spread[1] + 4), (512 + i, spread[3] - 4)], fill=(shade, shade - 2, shade - 14))
    d.rounded_rectangle(spread, radius=10, outline=PAGE_EDGE, width=2)

    # ================= left page: data page =================
    lx0, lx1 = 62, 488
    # header: country in both official languages
    centered(d, (lx0 + lx1) / 2, 92, "REPUBLIC OF NARELLIA", font(F_SERIF_B, 25), NAVY)
    centered(d, (lx0 + lx1) / 2, 124, "REPUBLIKA NARELLIA", font(F_SERIF_B, 15), NAVY)
    centered(d, (lx0 + lx1) / 2, 148, "PASSPORT  ·  PASPORTA", font(F_SANS_B, 14), TEAL)
    d.line([(lx0, 176), (lx1, 176)], fill=NAVY, width=2)
    # small crest: a wave inside a ring
    ccx, ccy = (lx0 + lx1) // 2, 206
    d.ellipse([ccx - 20, ccy - 20, ccx + 20, ccy + 20], outline=NAVY, width=2)
    pts = [(ccx - 14 + i, ccy + 4 * math.sin(i / 5.0)) for i in range(29)]
    d.line(pts, fill=TEAL, width=2)
    pts = [(ccx - 14 + i, ccy + 8 + 4 * math.sin(i / 5.0 + 1.2)) for i in range(29)]
    d.line(pts, fill=TEAL, width=2)

    # portrait + right-hand fields
    draw_portrait(d, (lx0, 244, lx0 + 168, 244 + 212))
    fx = lx0 + 190
    field(d, fx, 244, "TYPE / TIP", "P")
    field(d, fx, 296, "COUNTRY CODE / KOD", "NAR")
    field(d, fx, 348, "PASSPORT No. / NUMER", "NAR 8841207")
    field(d, fx, 400, "PERSONAL No. / NUMER PERS", "4419 2077")

    # name block under portrait
    ny = 478
    d.text((lx0, ny), "SURNAME / NOM FAMILIA", font=font(F_SANS, 11), fill=FAINT)
    d.text((lx0, ny + 14), "SELVANE", font=font(F_SANS_B, 24), fill=INK)
    d.text((lx0, ny + 48), "GIVEN NAMES / NOMI", font=font(F_SANS, 11), fill=FAINT)
    d.text((lx0, ny + 62), "MARO", font=font(F_SANS_B, 24), fill=INK)
    d.line([(lx0, ny + 96), (lx1, ny + 96)], fill=RULE, width=1)

    # two-column fields
    col2 = lx0 + 222
    field(d, lx0, 588, "NATIONALITY / NATSION", "NARELLIAN")
    field(d, col2, 588, "DATE OF BIRTH / DAT NAS", "02 SEP 1991")
    field(d, lx0, 640, "PLACE OF BIRTH / LOK NAS", "PORT NAREL")
    field(d, col2, 640, "SEX / SEKS", "F")
    field(d, lx0, 692, "DATE OF ISSUE / DAT EMIT", "14 MAR 2023")
    field(d, col2, 692, "DATE OF EXPIRY / DAT FIN", "13 MAR 2033")
    field(d, lx0, 744, "ISSUING AUTHORITY / AUTORIT", "PORT NAREL")
    field(d, col2, 744, "OCCUPATION / PROFES", "TIDEWARDEN")

    # endorsement: the telling detail
    ey = 800
    d.rounded_rectangle([lx0, ey, lx1, ey + 58], radius=4, outline=TEAL, width=1)
    d.text((lx0 + 10, ey + 7), "ENDORSEMENT / NOTA", font=font(F_SANS_B, 10), fill=TEAL)
    d.text((lx0 + 10, ey + 22), "TIDEWARDEN OF THE OUTER REEFS.",
           font=font(F_SANS, 12), fill=INK)
    d.text((lx0 + 10, ey + 39), "MAY BOARD ANY NARELLIAN VESSEL WITHOUT FARE.",
           font=font(F_SANS, 12), fill=INK)

    # machine-readable zone
    mz = 872
    d.rectangle([lx0 - 8, mz - 8, lx1 + 8, mz + 56], fill=(246, 244, 236))
    d.text((lx0, mz), "P<NARSELVANE<<MARO<<<<<<<<<<<<<<<<<<<<<<<<<<",
           font=font(F_MONO_B, 16), fill=INK)
    d.text((lx0, mz + 24), "NAR8841207NAR9109023F3303134<<<<<<<<<<<<<<02",
           font=font(F_MONO_B, 16), fill=INK)

    # ================= right page: visas & stamps =================
    rx0, rx1 = 540, 962
    centered(d, (rx0 + rx1) / 2, 92, "VISAS", font(F_SERIF_B, 25), NAVY)
    centered(d, (rx0 + rx1) / 2, 124, "VIZAE", font(F_SERIF_B, 15), NAVY)
    d.line([(rx0, 176), (rx1, 176)], fill=NAVY, width=2)
    d.text((rx1 - 30, 918), "7", font=font(F_SANS, 13), fill=FAINT)
    d.text((lx0 + 6, 940), "2", font=font(F_SANS, 13), fill=FAINT)

    # travel history, all after issue (14 MAR 2023), before expiry (13 MAR 2033):
    # Korvath Apr-May 2024, Delmbria Oct-Nov 2024, home next day.
    paste_stamp(img, make_stamp("rect", [("KORVATH", 20), ("ARRIVAL", 15),
                                         ("22 APR 2024", 16), ("PORT SORIN", 11)],
                                STAMP_BLUE, 208, 108, -7), 662, 262)
    paste_stamp(img, make_stamp("rect", [("KORVATH", 20), ("DEPARTURE", 15),
                                         ("09 MAY 2024", 16), ("PORT SORIN", 11)],
                                STAMP_RED, 208, 108, 5), 858, 262)
    paste_stamp(img, make_stamp("round", [("DELMBRIA", 17), ("ENTRY", 14),
                                          ("18 OCT 2024", 14)],
                                STAMP_GREEN, 148, 148, -11), 660, 428)
    paste_stamp(img, make_stamp("round", [("DELMBRIA", 17), ("EXIT", 14),
                                          ("02 NOV 2024", 14)],
                                STAMP_BLUE, 148, 148, 9), 856, 428)

    # fee stamp: the maritime state's paperwork in miniature
    paste_stamp(img, make_stamp("rect", [("TIDE FEE PAID", 14), ("40 M", 18),
                                         ("PORT NAREL", 11)],
                                TEAL, 176, 92, -4), 662, 586)

    # home arrival, back in Port Narel the day after leaving Delmbria
    paste_stamp(img, make_stamp("rect", [("NARELLIA", 20), ("RETURNED HOME", 14),
                                         ("03 NOV 2024", 16), ("PORT NAREL", 11)],
                                STAMP_BLUE, 216, 108, 6), 856, 586)

    # one handwritten-style officer note, kept small and bureaucratic
    d.text((rx0 + 6, 700), "Reef rotation ends 30 NOV 2025 — report to",
           font=font(F_SANS, 13), fill=(70, 76, 92))
    d.text((rx0 + 6, 720), "the Harbour Office, Port Narel, on return.",
           font=font(F_SANS, 13), fill=(70, 76, 92))
    d.text((rx0 + 6, 746), "— K. Aldan, Border Post 3",
           font=font(F_SANS, 13), fill=(70, 76, 92))

    out = os.path.join(HERE, "entry.png")
    img.convert("RGB").save(out, "PNG", optimize=True)
    print(out, os.path.getsize(out))


if __name__ == "__main__":
    main()
