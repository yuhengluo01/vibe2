"""强反差封面（抖音竖版 3:4，1080×1440）：上半是安静铺垫的一帧，下半是爆点的一帧，
中间一道白色斜切，大标题压在画面正中间（不要放到底部）。

用法（在工程目录里运行，index.html 在同目录）：
  python3 cover.py 输出.png <铺垫秒数> <爆点秒数> "标题第一行" "标题第二行（黄色）" ["上方小标签"] ["下方小标签"]
注意：index.html 的 captions()/watermark() 开头要有 if(window.COVER)return; 封面才会去掉字幕和水印。
例：
  python3 cover.py out-cover.png 16.0 22.75 "一张纸对折 42 次" "能撞上月球？" "第 10 次 · 10 厘米" "第 42 次 · 44 万公里"
可选环境变量：CALM_X / BOOM_X = 主体在 1920 宽原画面里的横向中心（默认 960），CALM_Y0 / BOOM_Y0 = 裁切起始 y（默认 141 / 0），SRC_W = 从原画面截取的宽度（默认 1300，越小越放大）。
画面里自己画的字（计数器、悬念句等）也要在 window.COVER 为 true 时隐藏，否则会被切一半留在封面上。
"""
import sys, os, io, asyncio
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

out, t_calm, t_boom, line1, line2 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4], sys.argv[5]
lab_top = sys.argv[6] if len(sys.argv) > 6 else ""
lab_bot = sys.argv[7] if len(sys.argv) > 7 else ""
CALM_X, BOOM_X = int(os.environ.get("CALM_X", 960)), int(os.environ.get("BOOM_X", 960))
CALM_Y0, BOOM_Y0 = int(os.environ.get("CALM_Y0", 141)), int(os.environ.get("BOOM_Y0", 0))
BLACK = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
W, H = 1080, 1440

def font(path, size):
    for idx in (2, 0):  # index 2 = SC in the Noto CJK collections
        try:
            return ImageFont.truetype(path, size, index=idx)
        except Exception:
            pass
    return ImageFont.load_default()

async def grab():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--font-render-hinting=none"])
        pg = await b.new_page(viewport={"width": 1920, "height": 1080})
        await pg.goto("file://" + os.path.join(os.getcwd(), "index.html")); await pg.evaluate("window.ready")
        await pg.evaluate("window.COVER=true")
        shots = []
        for t in (t_calm, t_boom):
            await pg.evaluate(f"window.draw({t})")
            shots.append(Image.open(io.BytesIO(await pg.locator("canvas").screenshot(type="png"))).convert("RGB"))
        await b.close()
        return shots

SRC_W = int(os.environ.get("SRC_W", 1300))   # how wide a slice of the 1920 frame goes into the cover
def crop(img, cx, y0, w=SRC_W):
    h = round(w * 780 / W)
    x0 = max(0, min(1920 - w, cx - w // 2)); y0 = max(0, min(1080 - h, y0))
    return img.crop((x0, y0, x0 + w, y0 + h)).resize((W, 780), Image.LANCZOS)

calm, boom = asyncio.run(grab())
cover = Image.new("RGB", (W, H))
# bottom: boom frame; top: calm frame (slightly desaturated) cut by a diagonal
cover.paste(crop(boom, BOOM_X, BOOM_Y0), (0, H - 780))
top = Image.new("RGB", (W, H)); top.paste(ImageEnhance.Color(crop(calm, CALM_X, CALM_Y0)).enhance(0.7), (0, 0))
SL = [(0, 800), (W, 660)]                      # the white slash
mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).polygon([(0, 0), (W, 0), SL[1], SL[0]], fill=255)
cover.paste(top, (0, 0), mask)
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(glow).line(SL, fill=(255, 255, 255, 255), width=34)
glow = glow.filter(ImageFilter.GaussianBlur(18)); cover.paste(glow, (0, 0), glow)
d = ImageDraw.Draw(cover, "RGBA"); d.line(SL, fill=(255, 255, 255, 255), width=10)
# soft dark band behind the centred title
band = Image.new("RGBA", (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(band)
for y in range(470, 1010):
    a = int(170 * (1 - abs(y - 740) / 270) ** 0.8)
    bd.line([(0, y), (W, y)], fill=(0, 0, 0, a))
cover.paste(band, (0, 0), band); d = ImageDraw.Draw(cover, "RGBA")

def centred(s, f, y, fill):
    tw = d.textlength(s, font=f)
    if tw > W - 80:  # shrink to fit
        f = font(BLACK, int(f.size * (W - 80) / tw)); tw = d.textlength(s, font=f)
    x = (W - tw) / 2
    for dx, dy in ((0, 7), (5, 5), (-4, 6)):
        d.text((x + dx, y + dy), s, font=f, fill=(0, 0, 0, 210))
    d.text((x, y), s, font=f, fill=fill)

centred(line1, font(BLACK, 100), 590, (255, 255, 255, 255))
centred(line2, font(BLACK, 140), 715, (255, 210, 31, 255))
if lab_top:
    d.text((50, 50), lab_top, font=font(SERIF, 40), fill=(235, 225, 205, 240))
if lab_bot:
    f = font(BLACK, 44); d.text((50, H - 120), lab_bot, font=f, fill=(255, 210, 31, 255))
f3 = font(BLACK, 30); s = "VIBE 知识大赏"; tw = d.textlength(s, font=f3)
d.rounded_rectangle([W - 50 - tw - 36, 46, W - 50, 100], radius=10, fill=(255, 210, 31, 255))
d.text((W - 50 - tw - 18, 52), s, font=f3, fill=(20, 20, 20, 255))
cover.save(out)
print("cover ok", out, cover.size)
