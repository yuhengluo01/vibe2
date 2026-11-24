"""强反差封面：左边是安静铺垫的一帧，右边是爆点的一帧，中间一道白色斜切，底部大标题。

用法（在工程目录里运行，index.html 在同目录）：
  python3 cover.py 输出.png <铺垫秒数> <爆点秒数> "标题第一行" "标题第二行（黄色）" ["左侧小标签"] ["右侧小标签"]
注意：index.html 的 captions()/watermark() 开头要有 if(window.COVER)return; 封面才会去掉字幕和水印。
例：
  python3 cover.py out-cover.png 16.0 22.75 "一张纸对折 42 次" "能撞上月球？" "第 10 次 · 10 厘米" "第 42 次 · 44 万公里"
"""
import sys, os, io, asyncio
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
out, t_calm, t_boom, line1, line2 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4], sys.argv[5]
lab_calm = sys.argv[6] if len(sys.argv) > 6 else ""
lab_boom = sys.argv[7] if len(sys.argv) > 7 else ""
BLACK = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"

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
        await pg.goto("file://" + os.path.join(os.getcwd(), "index.html")); await pg.evaluate("window.ready"); await pg.evaluate("window.COVER=true")
        shots = []
        for t in (t_calm, t_boom):
            await pg.evaluate(f"window.draw({t})")
            shots.append(Image.open(io.BytesIO(await pg.locator("canvas").screenshot(type="png"))).convert("RGB"))
        await b.close()
        return shots

calm, boom = asyncio.run(grab())
W, H = 1920, 1080
cover = Image.new("RGB", (W, H))
# right: boom frame, crop away its left HUD a little and scale to fill
bc = boom.crop((300, 0, 1920, 1080)).resize((int(1620 * 1.0), 1080))
cover.paste(bc, (W - bc.width, 0))
# left: calm frame centred on the subject, slightly desaturated
cc = calm.crop((460, 0, 1460, 1080))
cc = ImageEnhance.Color(cc).enhance(0.7)
mask = Image.new("L", (W, H), 0)
ImageDraw.Draw(mask).polygon([(0, 0), (860, 0), (700, H), (0, H)], fill=255)
left = Image.new("RGB", (W, H)); left.paste(cc, (0, 0))
cover.paste(left, (0, 0), mask)
d = ImageDraw.Draw(cover, "RGBA")
# white slash with glow
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
gd.line([(860, 0), (700, H)], fill=(255, 255, 255, 255), width=34)
glow = glow.filter(ImageFilter.GaussianBlur(18)); cover.paste(glow, (0, 0), glow)
d.line([(860, 0), (700, H)], fill=(255, 255, 255, 255), width=10)
# bottom gradient band for the title
band = Image.new("RGBA", (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(band)
for y in range(560, H):
    a = int(225 * min(1, (y - 560) / 300))
    bd.line([(0, y), (W, y)], fill=(0, 0, 0, a))
cover.paste(band, (0, 0), band); d = ImageDraw.Draw(cover, "RGBA")
# small labels
if lab_calm:
    f = font(SERIF, 38); d.text((60, 70), lab_calm, font=f, fill=(235, 225, 205, 235))
if lab_boom:
    f = font(BLACK, 44); tw = d.textlength(lab_boom, font=f); d.text((W - 80 - tw, H - 190), lab_boom, font=f, fill=(255, 210, 31, 255))
# title
f1, f2 = font(BLACK, 112), font(BLACK, 150)
def shadow_text(xy, s, f, fill):
    x, y = xy
    for dx, dy in ((0, 6), (4, 4), (-3, 5)):
        d.text((x + dx, y + dy), s, font=f, fill=(0, 0, 0, 200))
    d.text((x, y), s, font=f, fill=fill)
shadow_text((70, 700), line1, f1, (255, 255, 255, 255))
shadow_text((64, 840), line2, f2, (255, 210, 31, 255))
f3 = font(BLACK, 30); s = "VIBE 知识大赏"; tw = d.textlength(s, font=f3)
d.rounded_rectangle([W - 80 - tw - 36, H - 112, W - 80, H - 58], radius=10, fill=(255, 210, 31, 255))
d.text((W - 80 - tw - 18, H - 106), s, font=f3, fill=(20, 20, 20, 255))
cover.save(out)
print("cover ok", out)
