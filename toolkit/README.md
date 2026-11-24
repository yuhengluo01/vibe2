# vibe2 · 强反差知识短片工具包

模板：`template/`（第一期《一张纸对折 42 次》的完整源码）
- `index.html`：Canvas 逐帧画面，只暴露 `window.draw(t)`（t = 成片秒数）
- `render.py`：`python3 render.py keys` 出关键帧，`python3 render.py full` 全片分段渲染到 parts/
- `sfx.py`：合成音效 → sfx.npy
- `cover.py`：强反差封面（左=铺垫帧，右=爆点帧，白色斜切＋底部大标题），用法见文件开头
- `mix_fold.py <时长秒>`：用户的 Vibe BGM（`bgm/vibe_bgm.mp3`）＋音效混音，带「铺垫压低 → 静音吸气 → 爆点全开」的 BGM 包络
- 节奏：铺垫 0–16.3s（安静）→ 16.3–17.0s 静音 → 17.0s 爆点 1 → … → 92.6–93.5s 静音 → 93.5s 爆点 2 → 110.5s 结束

成片放 `videos/YYYY-MM-DD-short-english-name.mp4`（<100MB），封面放 `videos/YYYY-MM-DD-short-english-name-cover.png`，并在根目录 `videos.json` 的 `videos` 数组追加条目（id, file, cover, title, caption, tags, date）。

## 已做选题
- 2026-11-24 一张纸对折 42 次（指数增长：42 次到月球，103 次超过可观测宇宙；棋盘麦粒）
