#!/usr/bin/env python3
"""HonestMRR SaaS promo video builder — animated slides + voiceover."""
import math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

BASE = os.path.dirname(os.path.abspath(__file__))
FF = imageio_ffmpeg.get_ffmpeg_exe()
VO = os.path.join(BASE, "vo.mp3")
OUT = os.path.join(BASE, "honestmrr-promo.mp4")
FR = os.path.join(BASE, "frames")
os.makedirs(FR, exist_ok=True)

W, H, FPS = 1280, 720, 24
BG = (20, 22, 31); ACC = (255, 138, 61); TXT = (237, 239, 247); MUT = (154, 160, 180); GRN = (80, 200, 120); RED = (235, 90, 90)

def F(sz, bold=True):
    p = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/" + p, sz)

# audio duration
probe = subprocess.run([FF, "-i", VO, "-f", "null", "-"], capture_output=True, text=True)
dur = 36.0
for line in probe.stderr.splitlines():
    if "Duration" in line:
        h, m, s = line.split("Duration:")[1].split(",")[0].strip().split(":")
        dur = float(h) * 3600 + float(m) * 60 + float(s)
TOTAL = dur + 1.0
N = int(TOTAL * FPS)
print("audio dur", dur, "frames", N)

def ease(t): return t * t * (3 - 2 * t)
def fade(t, a, b): return max(0.0, min(1.0, (t - a) / (b - a)))

def bg():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im, "RGBA")
    d.ellipse([W - 420, -260, W + 260, 420], fill=(255, 138, 61, 14))
    d.ellipse([-300, H - 320, 380, H + 360], fill=(255, 138, 61, 10))
    return im, d

def mark(d, cx, cy, s, alpha=255):
    if s < 8 or alpha <= 0: return
    x0, y0, x1, y1 = cx - s, cy - s, cx + s, cy + s
    d.rounded_rectangle([x0, y0, x1, y1], radius=int(s * .28), fill=(27, 29, 39, alpha), outline=(255, 255, 255, int(alpha * .25)), width=2)
    bw = s * .34
    for i, hgt in enumerate((.34, .55, .78)):
        bx = x0 + s * .22 + i * (bw + s * .12)
        bh = s * 1.4 * hgt
        d.rounded_rectangle([bx, y1 - s * .2 - bh, bx + bw, y1 - s * .2], radius=4, fill=ACC + (alpha,))
    d.ellipse([x1 - s * .34, y0 - s * .16, x1 + s * .16, y0 + s * .34], fill=(255, 255, 255, alpha))
    d.text((x1 - s * .21, y0 - s * .05), "✓", font=F(int(s * .34)), fill=(27, 29, 39, alpha), anchor="mm")

def wordmark(d, cx, cy, sz, alpha=255):
    f = F(sz)
    w1 = d.textlength("Honest", font=f); w2 = d.textlength("MRR", font=f)
    x = cx - (w1 + w2) / 2
    d.text((x, cy), "Honest", font=f, fill=TXT + (alpha,)); d.text((x + w1, cy), "MRR", font=f, fill=ACC + (alpha,))

def wrap(d, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

# scene boundaries (fractions of TOTAL)
S = [0, .14, .30, .48, .68, .84, 1.01]

def draw(t):
    im, d = bg()
    u = t / TOTAL
    if u < S[1]:  # logo intro
        k = ease(fade(t, .2, 1.2))
        mark(d, W // 2, 280, int(90 * k), int(255 * k))
        a = int(255 * ease(fade(t, .8, 1.6)))
        wordmark(d, W // 2, 420, 74, a)
        f = F(26, False)
        a2 = int(255 * ease(fade(t, 1.4, 2.2)))
        d.text((W // 2, 500), "The database of honest startup revenues", font=f, fill=MUT + (a2,), anchor="mm")
    elif u < S[2]:  # problem
        a = int(255 * ease(fade(t, S[1] * TOTAL, S[1] * TOTAL + .6)))
        d.text((W // 2, 150), "Any founder can fake", font=F(52), fill=TXT + (a,), anchor="mm")
        d.text((W // 2, 215), "an MRR screenshot.", font=F(52), fill=RED + (a,), anchor="mm")
        k = ease(fade(t, S[1] * TOTAL + .5, S[1] * TOTAL + 1.3))
        x0, y0, x1, y1 = W // 2 - 260, 300, W // 2 + 260, 560
        d.rounded_rectangle([x0, y0, x1, y1], radius=18, fill=(255, 255, 255, int(14 * k)), outline=(255, 255, 255, int(40 * k)), width=2)
        d.text((x0 + 30, y0 + 30), "dashboard_final_FINAL.png", font=F(22, False), fill=MUT + (int(255 * k),))
        d.text((x0 + 30, y0 + 90), "MRR:  $48,000", font=F(44), fill=TXT + (int(255 * k),))
        d.text((x0 + 30, y0 + 160), "(trust me bro)", font=F(24, False), fill=MUT + (int(255 * k),))
        if k > .9:
            d.ellipse([x1 - 70, y1 - 70, x1 + 10, y1 + 10], fill=RED)
            d.text((x1 - 30, y1 - 30), "✗", font=F(44), fill=(255, 255, 255), anchor="mm")
    elif u < S[3]:  # proof link
        a = int(255 * ease(fade(t, S[2] * TOTAL, S[2] * TOTAL + .6)))
        d.text((W // 2, 160), "Nobody can fake", font=F(52), fill=TXT + (a,), anchor="mm")
        d.text((W // 2, 225), "a proof link.", font=F(52), fill=GRN + (a,), anchor="mm")
        k = ease(fade(t, S[2] * TOTAL + .5, S[2] * TOTAL + 1.3))
        x0, y0, x1, y1 = W // 2 - 320, 320, W // 2 + 320, 470
        d.rounded_rectangle([x0, y0, x1, y1], radius=18, fill=(255, 255, 255, int(14 * k)), outline=(80, 200, 120, int(90 * k)), width=2)
        d.text((x0 + 30, y0 + 45), "🔗  stripe.com/dashboard/honestmrr", font=F(30, False), fill=TXT + (int(255 * k),))
        d.text((x0 + 30, y0 + 100), "live revenue evidence · verified", font=F(22, False), fill=GRN + (int(255 * k),))
        if k > .9:
            d.ellipse([x1 - 70, y1 - 70, x1 + 10, y1 + 10], fill=GRN)
            d.text((x1 - 30, y1 - 30), "✓", font=F(44), fill=(20, 22, 31), anchor="mm")
        d.text((W // 2, 560), "Stripe · Razorpay · live dashboards", font=F(24, False), fill=MUT + (a,), anchor="mm")
    elif u < S[4]:  # leaderboard
        a = int(255 * ease(fade(t, S[3] * TOTAL, S[3] * TOTAL + .6)))
        d.text((W // 2, 110), "The verified revenue leaderboard", font=F(44), fill=TXT + (a,), anchor="mm")
        rows = [("Freshworks", 420), ("Razorpay", 360), ("Zoho", 310), ("Meesho", 260), ("Postman", 210)]
        k = ease(fade(t, S[3] * TOTAL + .4, S[3] * TOTAL + 1.6))
        for i, (nm, bw) in enumerate(rows):
            y = 190 + i * 88
            d.rounded_rectangle([180, y, 1100, y + 68], radius=14, fill=(255, 255, 255, 12))
            d.text((210, y + 34), f"#{i+1}  {nm}", font=F(26), fill=TXT, anchor="lm")
            d.text((1070, y + 34), f"${bw}k MRR", font=F(24), fill=MUT, anchor="rm")
            d.rounded_rectangle([480, y + 24, 480 + int(bw * 1.3 * k), y + 44], radius=10, fill=ACC)
        d.text((W // 2, 660), "ranked by verified MRR + 30-day growth", font=F(22, False), fill=MUT + (a,), anchor="mm")
    elif u < S[5]:  # features
        a = int(255 * ease(fade(t, S[4] * TOTAL, S[4] * TOTAL + .6)))
        d.text((W // 2, 120), "One database. Three superpowers.", font=F(46), fill=TXT + (a,), anchor="mm")
        cards = [("✅", "Founder Verified badge", "proof-checked revenue"), ("💰", "Buy / Sell marketplace", "startups for acquisition"), ("📊", "SaaS benchmarks", "category stats & growth")]
        for i, (ic, ti, su) in enumerate(cards):
            k = ease(fade(t, S[4] * TOTAL + .3 + i * .5, S[4] * TOTAL + .9 + i * .5))
            x0 = 120 + i * 360; y0, y1 = 240, 520
            d.rounded_rectangle([x0, y0, x0 + 320, y1], radius=18, fill=(255, 255, 255, int(14 * k)), outline=(255, 138, 61, int(60 * k)), width=2)
            d.text((x0 + 160, y0 + 70), ic, font=F(56), fill=TXT + (int(255 * k),), anchor="mm")
            d.text((x0 + 160, y0 + 150), ti, font=F(26), fill=TXT + (int(255 * k),), anchor="mm")
            d.text((x0 + 160, y0 + 195), su, font=F(20, False), fill=MUT + (int(255 * k),), anchor="mm")
        d.text((W // 2, 600), "free submissions · 7-day review", font=F(24, False), fill=MUT + (a,), anchor="mm")
    else:  # CTA
        k = ease(fade(t, S[5] * TOTAL, S[5] * TOTAL + .8))
        mark(d, W // 2, 200, int(70 * k), int(255 * k))
        wordmark(d, W // 2, 320, 64, int(255 * k))
        d.text((W // 2, 420), "Submit your startup — free.", font=F(38), fill=TXT + (int(255 * k),), anchor="mm")
        d.rounded_rectangle([W // 2 - 430, 470, W // 2 + 430, 545], radius=37, fill=ACC + (int(255 * k),))
        d.text((W // 2, 508), "shivkumarkashyap865.github.io/honestmrr", font=F(30), fill=(20, 22, 31, int(255 * k)), anchor="mm")
        d.text((W // 2, 610), "where revenue tells the truth", font=F(24, False), fill=MUT + (int(255 * k),), anchor="mm")
    return im

for i in range(N):
    draw(i / FPS).save(os.path.join(FR, f"{i:04d}.png"))
print("frames done")
subprocess.run([FF, "-y", "-framerate", str(FPS), "-i", os.path.join(FR, "%04d.png"),
                "-i", VO, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                "-c:a", "aac", "-b:a", "128k", "-shortest", OUT], check=True, capture_output=True)
print("VIDEO READY:", OUT, os.path.getsize(OUT), "bytes")
