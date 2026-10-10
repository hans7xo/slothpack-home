# brand/ — 品牌资产母版

本目录存放**生成站点 Logo / favicon 用的母版**，不参与 Astro 构建（不在 `public/` 下，不会被部署）。

## 文件

| 文件 | 说明 |
|---|---|
| `logo-mark-master.png` | 头像标记母版，451×256，含透明通道。取自 v6 品牌插画的头部裁切 |
| `logo-glyph-master.png` | `</>` 符号母版，431×256，含透明通道。取自同一插画中笔记本屏幕上的现成符号 |

## 来源与约束（重要）

- 原始素材：`logo-v6-transparent.png`（1990×2107，PNG RGBA）与 `logo-v6-hoodie-strings.png`
  （**实为 JPEG，扩展名不符**），两者目前在 `C:\Users\ou\Desktop\`，**尚未纳入版本管理**。
- 标记**为裁切派生件**：头像标记裁在嘴上沿，因此不含插画中的香烟与烟气元素；
  `</>` 母版从笔记本屏幕上按亮度键控提取。
- 这两个母版都不是重新设计的图形，符合"不擅自设计 Logo"的约束。
- 母版是位图裁切，**在 96px 高度以上细看能看出是裁切件**。若将来需要任意尺寸清晰的正式标记，
  需要重新绘制矢量版（这一步需要你确认，不在已批准范围内）。

## 重新生成站点资产

```bash
python gen_logo_assets.py
```

输出到 `public/`：`logo-mark.png`（127×72，调色板压缩）、`favicon.ico`（16/32/48 三帧）、
`apple-touch-icon.png`（180×180）。

> `gen_favicon.py` 是项目初始化遗留脚本，存在两个问题：把 `favicon.ico` 写到项目根目录而不是
> `public/`，且生成的是纯色方块。已被 `gen_logo_assets.py` 取代，建议删除（待确认）。
