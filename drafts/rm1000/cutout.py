"""Remove a plain dark-purple studio background from the host image (free, local). Flood-fills from the borders
by colour distance, then feathers the edge. Usage: python cutout.py in.png out.png"""
import sys
import numpy as np
from PIL import Image, ImageFilter
from collections import deque
im = Image.open(sys.argv[1]).convert("RGB"); a = np.asarray(im).astype(np.int32); h, w, _ = a.shape
border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]]); ref = np.median(border, axis=0)
r_, g_, b_ = a[..., 0], a[..., 1], a[..., 2]
purple = ((r_ - g_) > 8) & ((b_ - g_) > 14) & (np.abs(r_ - b_) < 60)   # tinted background, not neutral black cloth/hair
dist = np.where(purple, 0, 999); bg = np.zeros((h, w), bool); q = deque()
for y in range(h):
    for x in (0, w - 1): q.append((y, x))
for x in range(w):
    for y in (0, h - 1): q.append((y, x))
TH = 42
while q:
    y, x = q.popleft()
    if bg[y, x] or dist[y, x] > TH: continue
    bg[y, x] = True
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ny, nx = y + dy, x + dx
        if 0 <= ny < h and 0 <= nx < w and not bg[ny, nx]: q.append((ny, nx))
alpha = Image.fromarray(np.where(bg, 0, 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.6))
out = im.convert("RGBA"); out.putalpha(alpha); out.save(sys.argv[2])
print("bg ref", ref, "bg fraction", round(bg.mean(), 3))
