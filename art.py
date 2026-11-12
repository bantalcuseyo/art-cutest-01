#!/usr/bin/env python3
"""a small astronaut hugging a crescent moon  (cutest-picture-01 entry art).

The crescent lies like a cradle: a tiny astronaut stands in its bowl, both arms
out to grip its two arms, both feet on its inner curve with a contact shadow,
rim light from the moon on his suit, quiet stars behind.

Drawn entirely from geometry; no external images. Deterministic output.
"""

import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W = H = 1024
SS = 3
HERE = os.path.dirname(os.path.abspath(__file__))

BG_STOPS = [(0.00, (0x24, 0x1a, 0x4d)), (0.55, (0x3b, 0x25, 0x60)), (1.00, (0x57, 0x2a, 0x5c))]
MOON_STOPS = [(0.00, (0xff, 0xf4, 0xd2)), (0.45, (0xff, 0xe7, 0xac)), (1.00, (0xf3, 0xce, 0x84))]
SUIT_STOPS = [(0.00, (0xff, 0xff, 0xff)), (0.55, (0xe9, 0xef, 0xfa)), (1.00, (0xcf, 0xd9, 0xec))]
VISOR = (0x2b, 0x23, 0x50)
GLOVE = (0xee, 0xf3, 0xfb)
BOOT = (0xb7, 0xc5, 0xdd)
SHADOW = (0x24, 0x1a, 0x3f)
PINK = (0xff, 0x86, 0xae)

RNG = np.random.default_rng(5)

# moon: two circles, 250 and 228, offset 80,-60; the group is rotated so the
# offset points straight up: the crescent lies like a cradle, horns up.
MOON_C = (512.0, 470.0)
MOON_R1, MOON_R2 = 250.0, 228.0
MOON_ROT = math.radians(-53.13)

CX = 512.0                       # astronaut centre line
FEET_Y = 590.0                   # boots rest on the moon's inner curve


# --------------------------------------------------------------------------- helpers
def vgrad(w, h, stops):
    ys = np.linspace(0.0, 1.0, h, dtype=np.float32)
    out = np.zeros((h, 3), dtype=np.float32)
    for i in range(len(stops) - 1):
        p0, c0 = stops[i]
        p1, c1 = stops[i + 1]
        seg = (ys >= p0) & (ys <= p1)
        f = (ys[seg] - p0) / max(p1 - p0, 1e-6)
        for k in range(3):
            out[seg, k] = c0[k] + (c1[k] - c0[k]) * f
    return np.repeat(out[:, None, :], w, axis=1)


def new_mask(ss=SS):
    return Image.new("L", (W * ss, H * ss), 0)


def down(mask):
    return mask.resize((W, H), Image.LANCZOS)


def comp(base, colour, mask):
    m = (np.asarray(mask, dtype=np.float32) / 255.0)[..., None]
    arr = np.broadcast_to(np.array(colour, dtype=np.float32), base.shape).astype(np.float32) \
        if isinstance(colour, tuple) else colour.astype(np.float32)
    return base * (1.0 - m) + arr * m


def screen(base, layer, opacity=1.0):
    b = base / 255.0
    l = np.clip(layer / 255.0, 0, 1) * opacity
    return np.clip((1.0 - (1.0 - b) * (1.0 - l)) * 255.0, 0, 255)


# --------------------------------------------------------------------------- moon
def moon_offset():
    ox, oy = 80.0, -60.0
    c, s = math.cos(MOON_ROT), math.sin(MOON_ROT)
    return (ox * c - oy * s, ox * s + oy * c)


def moon_mask_ss():
    m = new_mask()
    d = ImageDraw.Draw(m)
    cx, cy = MOON_C
    d.ellipse([(cx - MOON_R1) * SS, (cy - MOON_R1) * SS,
               (cx + MOON_R1) * SS, (cy + MOON_R1) * SS], fill=255)
    dx, dy = moon_offset()
    d.ellipse([(cx + dx - MOON_R2) * SS, (cy + dy - MOON_R2) * SS,
               (cx + dx + MOON_R2) * SS, (cy + dy + MOON_R2) * SS], fill=0)
    return m


def moon_cusps():
    d = math.hypot(80.0, -60.0)
    a = (d * d + MOON_R1 ** 2 - MOON_R2 ** 2) / (2 * d)
    h = math.sqrt(max(MOON_R1 ** 2 - a * a, 0.0))
    ux, uy = 80.0 / d, -60.0 / d
    mx, my = ux * a, uy * a
    out = []
    for sgn in (1, -1):
        px, py = mx - uy * h * sgn, my + ux * h * sgn
        c, s = math.cos(MOON_ROT), math.sin(MOON_ROT)
        out.append((MOON_C[0] + px * c - py * s, MOON_C[1] + px * s + py * c))
    return sorted(out)


def band_top(m: np.ndarray, x: int) -> float:
    col = np.nonzero(m[:, x])[0]
    return float(col[0]) if col.size else 0.0


# --------------------------------------------------------------------------- astronaut
HEAD_R = 66.0
HEAD_Y = FEET_Y - 224.0
VISOR_E = (CX + 10, HEAD_Y - 2, 45.0, 41.0)


def astronaut_masks(hand_l, hand_r):
    """(suit, visor, gloves, boots, arms) at SS; both hands land on the moon."""
    suit = new_mask()
    sd = ImageDraw.Draw(suit)

    # torso: shoulders wider than hips
    sd.polygon([(x * SS, y * SS) for x, y in
                [(CX - 54, 452), (CX + 54, 452), (CX + 46, 506),
                 (CX + 34, 540), (CX - 34, 540), (CX - 46, 506)]], fill=255)
    sd.rounded_rectangle([(CX - 40) * SS, 518 * SS, (CX + 40) * SS, 552 * SS],
                         radius=15 * SS, fill=255)
    # shoulder pads
    for sgn in (-1, 1):
        sd.rounded_rectangle([(CX + sgn * 54 - 14) * SS, 442 * SS,
                              (CX + sgn * 54 + 14) * SS, 482 * SS],
                             radius=13 * SS, fill=255)
    # legs
    sd.line([((CX - 16) * SS, 536 * SS), ((CX - 22) * SS, FEET_Y * SS - 6)],
            fill=255, width=int(28 * SS))
    sd.line([((CX + 16) * SS, 536 * SS), ((CX + 22) * SS, FEET_Y * SS - 2)],
            fill=255, width=int(28 * SS))

    # arms: tubes out to the moon's two arms; 40 wide, 38 wide (brief)
    upper_l = [(CX - 58, 462), (CX - 122, 506), (hand_l[0] + 26, hand_l[1] + 34), hand_l]
    upper_r = [(CX + 58, 462), (CX + 122, 502), (hand_r[0] - 26, hand_r[1] + 30), hand_r]
    for pts, wd in ((upper_l, 40), (upper_r, 38)):
        sd.line([(x * SS, y * SS) for x, y in pts], fill=255, width=int(wd * SS), joint="curve")
        for x, y in pts:
            r = wd * 0.5 * SS
            sd.ellipse([x * SS - r, y * SS - r, x * SS + r, y * SS + r], fill=255)

    # neck (the helmet is its own layer so it can tilt)
    sd.rectangle([(CX - 26) * SS, (HEAD_Y + 46) * SS, (CX + 26) * SS, 456 * SS], fill=255)

    head = new_mask()
    hd = ImageDraw.Draw(head)
    hd.ellipse([(CX - HEAD_R) * SS, (HEAD_Y - HEAD_R) * SS,
                (CX + HEAD_R) * SS, (HEAD_Y + HEAD_R) * SS], fill=255)

    arms = new_mask()
    ad = ImageDraw.Draw(arms)
    for pts, wd in ((upper_l, 40), (upper_r, 38)):
        ad.line([(x * SS, y * SS) for x, y in pts], fill=255, width=int(wd * SS), joint="curve")
        for x, y in pts:
            r = wd * 0.5 * SS
            ad.ellipse([x * SS - r, y * SS - r, x * SS + r, y * SS + r], fill=255)

    gloves = new_mask()
    gd = ImageDraw.Draw(gloves)
    for (x, y), r, th in ((hand_l, 30.0, -1), (hand_r, 28.0, 1)):
        gd.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=255)
        tx, ty = x + th * r * 0.80, y - r * 0.52          # thumb over the edge
        gd.ellipse([(tx - 11) * SS, (ty - 11) * SS, (tx + 11) * SS, (ty + 11) * SS], fill=255)

    boots = new_mask()
    bd = ImageDraw.Draw(boots)
    for x, y in ((CX - 22, FEET_Y - 2), (CX + 22, FEET_Y + 2)):
        bd.ellipse([(x - 27) * SS, (y - 13) * SS, (x + 29) * SS, (y + 17) * SS], fill=255)

    visor = new_mask()
    ImageDraw.Draw(visor).ellipse([(VISOR_E[0] - VISOR_E[2]) * SS, (VISOR_E[1] - VISOR_E[3]) * SS,
                                   (VISOR_E[0] + VISOR_E[2]) * SS, (VISOR_E[1] + VISOR_E[3]) * SS],
                                  fill=255)
    tilt = 6.0
    piv = (CX * SS, (HEAD_Y + 44) * SS)
    head = head.rotate(tilt, resample=Image.BICUBIC, center=piv)
    visor = visor.rotate(tilt, resample=Image.BICUBIC, center=piv)
    return suit, head, visor, gloves, boots, arms


# --------------------------------------------------------------------------- draw
def build():
    yy, xx = np.mgrid[0:H, 0:W]
    bg = vgrad(W, H, BG_STOPS)

    # --- quiet stars
    st = new_mask()
    sd = ImageDraw.Draw(st)
    for _ in range(150):
        x, y = RNG.uniform(0, W), RNG.uniform(0, H)
        r = RNG.uniform(0.7, 2.6)
        sd.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS],
                   fill=int(RNG.uniform(90, 215)))
    st = down(st).filter(ImageFilter.GaussianBlur(0.6))
    bg = screen(bg, np.stack([np.asarray(st, dtype=np.float32)] * 3, -1)
                * np.array([1.0, 0.96, 0.92], dtype=np.float32), 0.55)

    # --- moon
    m_1024 = down(moon_mask_ss())
    mm = np.asarray(m_1024) > 127
    glow = m_1024.filter(ImageFilter.GaussianBlur(46))
    bg = screen(bg, np.stack([np.asarray(glow, dtype=np.float32)] * 3, -1)
                * np.array([1.0, 0.86, 0.58], dtype=np.float32), 0.55)
    bg = comp(bg, vgrad(W, H, MOON_STOPS), m_1024)
    er = m_1024.filter(ImageFilter.MinFilter(13))
    inner = np.asarray(m_1024, dtype=np.float32) - np.asarray(er, dtype=np.float32)
    inner_i = Image.fromarray(np.clip(inner, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(9))
    bg = screen(bg, np.stack([np.asarray(inner_i, dtype=np.float32)] * 3, -1)
                * np.array([1.0, 0.95, 0.75], dtype=np.float32), 0.45)

    # hands grip the moon's two arms, just inside the horns
    c1, c2 = moon_cusps()
    hx_l = c1[0] + 14.0
    hx_r = c2[0] - 14.0
    hand_l = (hx_l, band_top(mm, int(hx_l)) + 16)
    hand_r = (hx_r, band_top(mm, int(hx_r)) + 16)

    # --- contact shadow: the astronaut stands on the moon's inner curve
    sh = new_mask()
    ImageDraw.Draw(sh).ellipse([(CX - 96) * SS, (FEET_Y - 20) * SS,
                                (CX + 96) * SS, (FEET_Y + 44) * SS], fill=255)
    sh = down(sh).filter(ImageFilter.GaussianBlur(20))
    al = (np.asarray(sh, dtype=np.float32) / 255.0)[..., None] * 0.45
    bg = bg * (1 - al) + np.array(SHADOW, dtype=np.float32) * al

    # --- astronaut
    suit_ss, head_ss, visor_ss, gloves_ss, boots_ss, arms_ss = astronaut_masks(hand_l, hand_r)
    suit_1024, visor_1024 = down(suit_ss), down(visor_ss)
    head_1024 = down(head_ss)
    gloves_1024, boots_1024, arms_1024 = down(gloves_ss), down(boots_ss), down(arms_ss)

    # shadow of the figure on the moon, so white never sits flat on cream
    a_sh = Image.fromarray(np.asarray(suit_1024, dtype=np.uint8)).transform(
        (W, H), Image.AFFINE, (1, 0, -10, 0, 1, -16), resample=Image.BILINEAR)
    a_sh = a_sh.filter(ImageFilter.GaussianBlur(16))
    am = (np.asarray(a_sh, dtype=np.float32) / 255.0)[..., None] * \
         (np.asarray(m_1024, dtype=np.float32) / 255.0)[..., None] * 0.40
    bg = bg * (1 - am)

    bg = comp(bg, vgrad(W, H, SUIT_STOPS), suit_1024)
    shade = np.clip(((yy - HEAD_Y) / 260.0) * 0.20 + ((xx - CX) / 300.0) * 0.10, -0.06, 0.26)
    bg = bg * (1 - shade[..., None] * (np.asarray(suit_1024, dtype=np.float32) / 255.0)[..., None])
    bg = comp(bg, vgrad(W, H, SUIT_STOPS), head_1024)
    hs = np.clip(((yy - (HEAD_Y - HEAD_R)) / (2 * HEAD_R)) * 0.16, 0, 0.16)
    bg = bg * (1 - hs[..., None] * (np.asarray(head_1024, dtype=np.float32) / 255.0)[..., None])
    bg = comp(bg, BOOT, boots_1024)
    sole = np.asarray(boots_1024, dtype=np.float32) * \
           (np.clip((yy - (FEET_Y - 8)) / 22.0, 0, 1) ** 1.2)
    bg = bg * (1 - (sole / 255.0)[..., None] * 0.35)
    bg = comp(bg, VISOR, visor_1024)

    # visor: hairline rim + sky reflection
    rim = np.asarray(visor_1024, dtype=np.float32) - np.asarray(
        visor_1024.filter(ImageFilter.MinFilter(5)), dtype=np.float32)
    rim_i = Image.fromarray(np.clip(rim, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.6))
    bg = screen(bg, np.stack([np.asarray(rim_i, dtype=np.float32)] * 3, -1)
                * np.array([0.92, 0.95, 1.0], dtype=np.float32), 0.55)
    hl = new_mask()
    ImageDraw.Draw(hl).ellipse([(VISOR_E[0] - 26) * SS, (VISOR_E[1] - 40) * SS,
                                (VISOR_E[0] + 22) * SS, (VISOR_E[1] - 8) * SS], fill=150)
    hl = down(hl).filter(ImageFilter.GaussianBlur(8))
    hl = np.minimum(np.asarray(hl, dtype=np.float32), np.asarray(visor_1024, dtype=np.float32))
    bg = screen(bg, np.stack([hl] * 3, -1) * np.array([0.60, 0.64, 0.95], dtype=np.float32), 0.95)

    # crisp crescent reflection in the visor
    vr = new_mask()
    vd = ImageDraw.Draw(vr)
    vcx, vcy = VISOR_E[0] - 14, VISOR_E[1] - 8
    vd.ellipse([(vcx - 26) * SS, (vcy - 24) * SS, (vcx + 26) * SS, (vcy + 24) * SS], fill=255)
    vd.ellipse([(vcx - 18) * SS, (vcy - 30) * SS, (vcx + 34) * SS, (vcy + 18) * SS], fill=0)
    vr = down(vr).rotate(6.0, resample=Image.BICUBIC,
                         center=(VISOR_E[0], VISOR_E[1])).filter(ImageFilter.GaussianBlur(1.8))
    vr = np.minimum(np.asarray(vr, dtype=np.float32), np.asarray(visor_1024, dtype=np.float32))
    bg = screen(bg, np.stack([vr] * 3, -1) * np.array([0.92, 0.94, 1.0], dtype=np.float32), 0.75)

    # chest light
    ch = new_mask()
    ImageDraw.Draw(ch).ellipse([(CX - 10) * SS, 492 * SS, (CX + 10) * SS, 512 * SS], fill=255)
    chg = down(ch).filter(ImageFilter.GaussianBlur(15))
    bg = screen(bg, np.stack([np.asarray(chg, dtype=np.float32)] * 3, -1)
                * np.array(PINK, dtype=np.float32) / 255.0, 0.9)
    bg = comp(bg, PINK, down(ch).filter(ImageFilter.GaussianBlur(1.0)))

    # --- gloves last, on top of the moon: the grip
    bg = comp(bg, GLOVE, gloves_1024)
    g_edge = np.asarray(gloves_1024, dtype=np.float32) - np.asarray(
        gloves_1024.filter(ImageFilter.MinFilter(5)), dtype=np.float32)
    ge = Image.fromarray(np.clip(g_edge, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.4))
    bg = screen(bg, np.stack([np.asarray(ge, dtype=np.float32)] * 3, -1)
                * np.array([0.95, 0.97, 1.0], dtype=np.float32), 0.5)

    # --- rim light from the moon: strongest along the lower silhouette
    er2 = suit_1024.filter(ImageFilter.MinFilter(9))
    edge = np.asarray(suit_1024, dtype=np.float32) - np.asarray(er2, dtype=np.float32)
    edge = edge * np.clip((yy - 400.0) / 170.0, 0, 1) ** 0.7
    edge_i = Image.fromarray(np.clip(edge, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(7))
    bg = screen(bg, np.stack([np.asarray(edge_i, dtype=np.float32)] * 3, -1)
                * np.array([1.0, 0.93, 0.74], dtype=np.float32), 0.7)

    # --- vignette + grain
    nx = (xx - W / 2) / (W / 2)
    ny = (yy - H / 2) / (H / 2)
    r = np.sqrt(nx ** 2 + ny ** 2) / math.sqrt(2)
    arr = bg * (1.0 - 0.20 * r ** 2.2)[..., None]
    arr = arr + RNG.normal(0, 3.5, (H, W, 3))
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    for name, img in (("ART_MASK_OUT", suit_1024), ("ART_MOON_OUT", m_1024),
                      ("ART_GLOVE_OUT", gloves_1024), ("ART_BOOT_OUT", boots_1024)):
        if os.environ.get(name):
            Image.fromarray(np.asarray(img, dtype=np.uint8)).save(os.environ[name])
    return out


def main():
    img = build()
    path = os.path.join(HERE, "entry.png")
    img.save(path, format="JPEG", quality=93, subsampling=0, optimize=True)
    print("wrote", path, os.path.getsize(path), "bytes", img.size)


if __name__ == "__main__":
    main()
