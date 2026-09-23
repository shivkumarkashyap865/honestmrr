#!/usr/bin/env python3
"""HonestMRR promo v2 — Envato-style: 1080p, device mockups, kinetic type, 130BPM music bed."""
import math, os, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

BASE = os.path.dirname(os.path.abspath(__file__))
FF = imageio_ffmpeg.get_ffmpeg_exe()
VO = os.path.join(BASE, "vo.mp3")
MUS = os.path.join(BASE, "music.wav")
OUT = os.path.join(BASE, "honestmrr-promo-v2.mp4")
FR = os.path.join(BASE, "frames2")
os.makedirs(FR, exist_ok=True)

W, H, FPS = 1920, 1080, 24
BG = (16, 18, 26); BG2 = (22, 25, 36); ACC = (255, 138, 61); TXT = (240, 242, 250); MUT = (150, 156, 175); GRN = (80, 200, 120); RED = (235, 90, 90); GLASS = (255, 255, 255, 16)

def F(sz, bold=True):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/" + ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), sz)

probe = subprocess.run([FF, "-i", VO, "-f", "null", "-"], capture_output=True, text=True)
dur = 52.0
for line in probe.stderr.splitlines():
    if "Duration" in line:
        h, m, s = line.split("Duration:")[1].split(",")[0].strip().split(":")
        dur = float(h) * 3600 + float(m) * 60 + float(s)
TOTAL = dur + 1.2
N = int(TOTAL * FPS)
print("total", TOTAL, "frames", N)

def ease(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def fade(t, a, b): return max(0.0, min(1.0, (t - a) / max(1e-6, b - a)))

def bgimg():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im, "RGBA")
    for i in range(0, H, 4):
        d.line([(0, i), (W, i)], fill=(255, 255, 255, 2))
    d.ellipse([W - 700, -400, W + 400, 700], fill=(255, 138, 61, 12))
    d.ellipse([-500, H - 500, 600, H + 600], fill=(90, 120, 255, 10))
    return im, d

def rr(d, box, rad, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=rad, fill=fill, outline=outline, width=width)

def mark(d, cx, cy, s, alpha=255):
    if s < 8 or alpha <= 0: return
    x0, y0, x1, y1 = cx - s, cy - s, cx + s, cy + s
    rr(d, [x0, y0, x1, y1], int(s * .28), fill=(27, 29, 39, alpha), outline=(255, 255, 255, int(alpha * .3)), width=3)
    bw = s * .32
    for i, hgt in enumerate((.34, .56, .80)):
        bx = x0 + s * .2 + i * (bw + s * .12); bh = s * 1.45 * hgt
        rr(d, [bx, y1 - s * .18 - bh, bx + bw, y1 - s * .18], 5, fill=ACC + (alpha,))
    d.ellipse([x1 - s * .36, y0 - s * .18, x1 + s * .18, y0 + s * .36], fill=(255, 255, 255, alpha))
    d.text((x1 - s * .09, y0 + s * .09), "✓", font=F(max(8, int(s * .36))), fill=(27, 29, 39, alpha), anchor="mm")

def wordmark(d, cx, cy, sz, alpha=255):
    f = F(sz); w1 = d.textlength("Honest", font=f); w2 = d.textlength("MRR", font=f)
    x = cx - (w1 + w2) / 2
    d.text((x, cy), "Honest", font=f, fill=TXT + (alpha,), anchor="lm")
    d.text((x + w1, cy), "MRR", font=f, fill=ACC + (alpha,), anchor="lm")


def icon(d, kind, cx, cy, s, alpha=255):
    if kind == "bars":
        bw = s * .26
        for i, hgt in enumerate((.45, .7, 1.0)):
            bx = cx - s * .5 + i * (bw + s * .12)
            rr(d, [bx, cy + s * .5 - s * hgt, bx + bw, cy + s * .5], 4, fill=ACC + (alpha,))
    elif kind == "check":
        d.ellipse([cx - s * .5, cy - s * .5, cx + s * .5, cy + s * .5], fill=GRN + (alpha,))
        d.text((cx, cy + s * .03), "✓", font=F(int(s * .7)), fill=(16, 18, 26, alpha), anchor="mm")
    elif kind == "arrow":
        d.line([(cx - s * .35, cy + s * .35), (cx + s * .25, cy - s * .3)], fill=GRN + (alpha,), width=max(3, s // 8))
        d.polygon([(cx + s * .4, cy - s * .45), (cx + s * .05, cy - s * .32), (cx + s * .28, cy - s * .05)], fill=GRN + (alpha,))
    elif kind == "dollar":
        d.ellipse([cx - s * .5, cy - s * .5, cx + s * .5, cy + s * .5], fill=ACC + (alpha,))
        d.text((cx, cy + s * .03), "$", font=F(int(s * .72)), fill=(16, 18, 26, alpha), anchor="mm")

# ---------- scene 1: kinetic type ----------
def sc_kinetic(t):
    im, d = bgimg()
    words = [("REVENUE.", TXT, 0.0), ("VERIFIED.", ACC, 0.92), ("PUBLIC.", GRN, 1.84)]
    for txt, col, bt in words:
        lt = t - bt
        if lt < 0: continue
        k = ease(min(1, lt / .18))
        sz = int(150 * (1.45 - .45 * k))
        a = int(255 * min(1, lt / .12)) if lt < 2.6 else int(255 * max(0, 1 - (lt - 2.6) / .3))
        d.text((W // 2, H // 2 - 40), txt, font=F(sz), fill=col + (max(0, min(255, a)),), anchor="mm")
    lt = t - 2.76
    if lt > 0:
        a = int(255 * ease(min(1, lt / .3)))
        d.text((W // 2, H // 2 + 90), "the leaderboard where proof is mandatory", font=F(40, False), fill=MUT + (a,), anchor="mm")
    return im

# ---------- browser mockup ----------
def browser_screen(d, x0, y0, x1, y1, pan):
    rr(d, [x0, y0, x1, y1], 22, fill=(255, 255, 255, 10), outline=(255, 255, 255, 45), width=2)
    rr(d, [x0, y0, x1, y0 + 64], 22, fill=(255, 255, 255, 14))
    d.rectangle([x0, y0 + 40, x1, y0 + 64], fill=(255, 255, 255, 14))
    for i, c in enumerate((RED, (240, 190, 80), GRN)):
        d.ellipse([x0 + 26 + i * 34, y0 + 22, x0 + 46 + i * 34, y0 + 42], fill=c)
    rr(d, [x0 + 150, y0 + 16, x1 - 40, y0 + 48], 16, fill=(0, 0, 0, 90))
    d.text((x0 + 175, y0 + 32), "shivkumarkashyap865.github.io/honestmrr", font=F(20, False), fill=MUT, anchor="lm")
    ny = y0 + 64
    wordmark(d, x0 + 150, ny + 44, 34)
    for i, lb in enumerate(("Leaderboard", "Buy/Sell", "Stats", "Services")):
        d.text((x0 + 330 + i * 170, ny + 44), lb, font=F(24, False), fill=MUT, anchor="lm")
    rr(d, [x1 - 260, ny + 20, x1 - 40, ny + 68], 24, fill=ACC + (255,))
    d.text((x1 - 150, ny + 44), "+ Add Startup", font=F(24), fill=(20, 22, 31), anchor="mm")
    hy = ny + 110
    d.text((x0 + 80 - pan, hy + 40), "The database of", font=F(56), fill=TXT, anchor="lm")
    d.text((x0 + 80 - pan, hy + 110), "honest startup revenues", font=F(56), fill=ACC, anchor="lm")
    rr(d, [x0 + 80 - pan, hy + 160, x0 + 380 - pan, hy + 220], 30, fill=ACC + (255,))
    d.text((x0 + 230 - pan, hy + 190), "Explore rankings", font=F(26), fill=(20, 22, 31), anchor="mm")
    for i in range(3):
        cx = x1 - 560 + i * 200
        rr(d, [cx - pan // 2, hy + 20, cx + 170 - pan // 2, hy + 240], 18, fill=(255, 255, 255, 12 + i * 6), outline=(255, 138, 61, 40 + i * 40), width=2)
        icon(d, ("bars", "arrow", "check")[i], cx + 45 - pan // 2, hy + 55, 44)
        d.text((cx + 20 - pan // 2, hy + 120), ("Stats", "Growth", "Verified")[i], font=F(26), fill=TXT, anchor="lm")
        d.text((cx + 20 - pan // 2, hy + 165), ("$412k total", "+18% mo/mo", "proof-linked")[i], font=F(20, False), fill=MUT, anchor="lm")
    ty = hy + 290
    rows = [("Freshworks", 420), ("Razorpay", 360), ("Zoho", 310), ("Meesho", 260)]
    for i, (nm, bw) in enumerate(rows):
        y = ty + i * 66
        rr(d, [x0 + 80, y, x1 - 80, y + 52], 12, fill=(255, 255, 255, 8))
        d.text((x0 + 110, y + 26), f"#{i+1}  {nm}", font=F(24), fill=TXT, anchor="lm")
        d.text((x1 - 110, y + 26), f"${bw}k", font=F(22), fill=MUT, anchor="rm")
        rr(d, [x0 + 480, y + 16, x0 + 480 + bw, y + 36], 10, fill=ACC)

def sc_browser(t):
    im, d = bgimg()
    k = ease(min(1, t / .8))
    pan = int(60 * (t / 6.0))
    a = int(255 * k)
    x0, y0, x1, y1 = 260, 150, W - 260, H - 130
    d.text((W // 2, 90), "ONE PUBLIC LEADERBOARD", font=F(44), fill=TXT + (a,), anchor="mm")
    browser_screen(d, x0, y0 + int(40 * (1 - k)), x1, y1, pan)
    return im

# ---------- phone mockup ----------
def sc_phone(t):
    im, d = bgimg()
    d.text((W // 2 - 300, 200), "Verified revenue,", font=F(72), fill=TXT, anchor="lm")
    d.text((W // 2 - 300, 290), "on your phone.", font=F(72), fill=ACC, anchor="lm")
    for i, ln in enumerate(("proof-linked listings", "Founder Verified badges", "buy / sell marketplace")):
        a = int(255 * ease(fade(t, .8 + i * .5, 1.3 + i * .5)))
        d.ellipse([W // 2 - 300, 400 + i * 70, W // 2 - 268, 432 + i * 70], fill=GRN + (a,))
        d.text((W // 2 - 284, 416 + i * 70), "✓", font=F(22), fill=(16, 18, 26, a), anchor="mm")
        d.text((W // 2 - 240, 416 + i * 70), ln, font=F(36, False), fill=MUT + (a,), anchor="lm")
    k = ease(fade(t, .3, 1.1))
    px0, py0, px1, py1 = W - 700, 120 + int(60 * (1 - k)), W - 300, H - 80
    rr(d, [px0, py0, px1, py1], 48, fill=(10, 11, 16, 255), outline=(255, 255, 255, 60), width=3)
    sx0, sy0, sx1, sy1 = px0 + 18, py0 + 18, px1 - 18, py1 - 18
    rr(d, [sx0, sy0, sx1, sy1], 34, fill=(20, 22, 31, 255))
    d.rounded_rectangle([px0 + 140, py0 + 26, px1 - 140, py0 + 44], 9, fill=(0, 0, 0, 255))
    wordmark(d, (sx0 + sx1) // 2, sy0 + 70, 34)
    d.text(((sx0 + sx1) // 2, ), ) if False else None
    d.text(((sx0 + sx1) // 2, sy0 + 120), "Revenue Leaderboard", font=F(26), fill=MUT, anchor="mm")
    rows = [("Freshworks", 300), ("Razorpay", 260), ("Zoho", 220), ("Meesho", 190), ("Postman", 160)]
    for i, (nm, bw) in enumerate(rows):
        y = sy0 + 160 + i * 120
        kk = ease(fade(t, .9 + i * .25, 1.4 + i * .25))
        rr(d, [sx0 + 20, y, sx1 - 20, y + 100], 16, fill=(255, 255, 255, 12))
        d.text((sx0 + 40, y + 30), f"#{i+1} {nm}", font=F(24), fill=TXT, anchor="lm")
        d.text((sx1 - 40, y + 30), f"${bw}k", font=F(22), fill=GRN, anchor="rm")
        rr(d, [sx0 + 40, y + 62, sx0 + 40 + int((sx1 - sx0 - 80) * (bw / 320) * kk), y + 80], 9, fill=ACC)
    return im

# ---------- analytics / counters ----------
def sc_analytics(t):
    im, d = bgimg()
    d.text((W // 2, 120), "REAL NUMBERS. LIVE PIPELINE.", font=F(52), fill=TXT, anchor="mm")
    p = ease(fade(t, .4, 2.2))
    stats = [("23", "companies live"), ("33", "pages, 0 trackers"), ("0.02MB", "per page load"), ("7-day", "review turnaround")]
    for i, (num, lab) in enumerate(stats):
        x = 240 + i * 380
        a = int(255 * ease(fade(t, .3 + i * .3, .8 + i * .3)))
        rr(d, [x, 220, x + 340, 420], 22, fill=GLASS, outline=(255, 138, 61, 50), width=2)
        d.text((x + 170, 300), num, font=F(64), fill=ACC + (a,), anchor="mm")
        d.text((x + 170, 370), lab, font=F(26, False), fill=MUT + (a,), anchor="mm")
    cx0, cy0, cx1, cy1 = 240, 500, W - 240, 940
    rr(d, [cx0, cy0, cx1, cy1], 22, fill=GLASS, outline=(255, 255, 255, 30), width=2)
    pts = [(0, .75), (.12, .6), (.24, .66), (.36, .45), (.5, .5), (.62, .3), (.75, .34), (.88, .15), (1, .08)]
    n = max(2, int(len(pts) * p))
    xy = [(cx0 + 60 + (cx1 - cx0 - 120) * fx, cy0 + 60 + (cy1 - cy0 - 120) * fy) for fx, fy in pts[:n]]
    if len(xy) > 1:
        d.line(xy, fill=ACC, width=6, joint="curve")
        for x, y in xy: d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=TXT)
    d.text((cx0 + 60, cy0 + 40), "verified MRR growth", font=F(26, False), fill=MUT, anchor="lm")
    return im

# ---------- features ----------
def sc_features(t):
    im, d = bgimg()
    d.text((W // 2, 140), "BUILT FOR TRUST.", font=F(64), fill=TXT, anchor="mm")
    cards = [("check", "Founder Verified", "every badge = checked proof link"), ("dollar", "Marketplace", "startups for acquisition, 3% fee"), ("bars", "Benchmarks", "category stats for SaaS founders")]
    for i, (ic, ti, su) in enumerate(cards):
        k = ease(fade(t, .3 + i * .55, .95 + i * .55))
        x = 200 + i * 520; y = 300 + int(50 * (1 - k))
        rr(d, [x, y, x + 480, y + 420], 26, fill=(255, 255, 255, int(16 * k)), outline=(255, 138, 61, int(70 * k)), width=2)
        icon(d, ic, x + 240, y + 110, 84, int(255 * k))
        d.text((x + 240, y + 230), ti, font=F(44), fill=TXT + (int(255 * k),), anchor="mm")
        d.text((x + 240, y + 300), su, font=F(26, False), fill=MUT + (int(255 * k),), anchor="mm")
    a = int(255 * ease(fade(t, 2.4, 3.0)))
    d.text((W // 2, 830), "free submissions · no trackers · static & fast", font=F(32, False), fill=MUT + (a,), anchor="mm")
    return im

# ---------- CTA ----------
def sc_cta(t):
    im, d = bgimg()
    k = ease(min(1, t / .7))
    mark(d, W // 2, 300, int(110 * k), int(255 * k))
    wordmark(d, W // 2, 480, 96, int(255 * k))
    a2 = int(255 * ease(fade(t, .6, 1.2)))
    d.text((W // 2, 580), "where revenue tells the truth", font=F(40, False), fill=MUT + (a2,), anchor="mm")
    a3 = int(255 * ease(fade(t, 1.0, 1.6)))
    rr(d, [W // 2 - 560, 660, W // 2 + 560, 760], 50, fill=ACC + (a3,))
    d.text((W // 2, 710), "shivkumarkashyap865.github.io/honestmrr", font=F(42), fill=(20, 22, 31, a3), anchor="mm")
    a4 = int(255 * ease(fade(t, 1.5, 2.1)))
    d.text((W // 2, 850), "Submit your startup — free.", font=F(36), fill=TXT + (a4,), anchor="mm")
    return im

SCENES = [(0.0, 3.4, sc_kinetic), (3.4, 10.5, sc_browser), (10.5, 18.5, sc_phone),
          (18.5, 27.5, sc_analytics), (27.5, 35.5, sc_features), (35.5, 44.5, sc_browser),
          (44.5, TOTAL + 1, sc_cta)]
XF = 0.5

def frame(t):
    cur = None; prev = None; lt = 0; plt = 0
    for i, (a, b, fn) in enumerate(SCENES):
        if a <= t < b:
            cur = (fn, t - a)
            if i > 0 and t - a < XF:
                pa, pb, pfn = SCENES[i - 1]
                prev = (pfn, min(pb - a - 0.001 - pa + (t - a), pb - pa))
            break
    if cur is None:
        fn, lt = SCENES[-1][2], TOTAL
        return fn(lt)
    im = cur[0](cur[1])
    if prev:
        pim = prev[0](prev[1])
        al = ease((t - SCENES[[s[0] for s in SCENES].index(prev and [s for s in SCENES if s[2] == prev[0]][0][0])] if False else 0)) if False else None
        k = ease(min(1, max(0, (cur[1]) / XF)))
        mask = Image.new("L", im.size, int(255 * k))
        im = Image.composite(im, pim, mask)
    return im

# zoom + vignette per frame
def post(im, t):
    z = 1.03 + 0.015 * math.sin(t * .8)
    nw, nh = int(W * z), int(H * z)
    im = im.resize((nw, nh)).crop(((nw - W) // 2, (nh - H) // 2, (nw - W) // 2 + W, (nh - H) // 2 + H))
    return im

if os.path.exists(os.path.join(FR, f"{N-1:04d}.png")):
    print("frames cached, skipping render")
else:
    print("rendering frames...")
    for i in range(N):
        t = i / FPS
        post(frame(t), t).save(os.path.join(FR, f"{i:04d}.png"))
    print("frames done")

# ---------- 130 BPM music bed ----------
sr = 44100; n = int(TOTAL * sr)
mix = np.zeros(n, dtype=np.float64)
beat = 60.0 / 130.0
ks = int(.28 * sr); kt = np.arange(ks) / sr
kf = 45 + 110 * np.exp(-kt * 26); kph = 2 * np.pi * np.cumsum(kf) / sr
kick = np.sin(kph) * np.exp(-kt * 16)
hs = int(.05 * sr); ht = np.arange(hs) / sr
hat = np.random.default_rng(7).standard_normal(hs) * np.exp(-ht * 110)
hat = np.diff(hat, prepend=0)
nb = int(4 * beat * sr)
chords = [[220, 261.63, 329.63], [174.61, 220, 261.63], [261.63, 329.63, 392], [196, 246.94, 293.66]]
bt = 0; bi = 0
while bt * beat < TOTAL - 4 * beat:
    st = int(bt * beat * sr)
    tt = np.arange(nb) / sr
    env = np.minimum(1, tt / .25) * np.minimum(1, (nb / sr - tt) / .6 + .0)
    env = np.clip(env, 0, 1)
    pad = sum(np.sin(2 * np.pi * f * tt) + .6 * np.sin(2 * np.pi * f * 1.003 * tt) for f in chords[bi % 4]) / 3.2
    seg = mix[st:st + nb]
    seg += pad * env * .16
    bi += 1; bt += 4
b = 0
while b * beat < TOTAL:
    st = int(b * beat * sr)
    seg = mix[st:min(n, st + ks)]
    if len(seg): seg += kick[:len(seg)] * .55
    st2 = int((b + .5) * beat * sr)
    if st2 + hs < n: mix[st2:st2 + hs] += hat * .12
    b += 1
mix = mix / np.max(np.abs(mix)) * .5
with wave.open(MUS, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print("music done")

subprocess.run([FF, "-y", "-framerate", str(FPS), "-i", os.path.join(FR, "%04d.png"),
                "-i", VO, "-i", MUS,
                "-filter_complex", "[2:a]volume=0.55[m];[1:a][m]amix=inputs=2:duration=first:normalize=0[a]",
                "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19",
                "-c:a", "aac", "-b:a", "160k", "-shortest", OUT], check=True, capture_output=True)
print("VIDEO V2 READY:", OUT, os.path.getsize(OUT), "bytes")
