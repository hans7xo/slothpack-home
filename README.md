# SlothPack — 主域品牌页

SlothPack 是一个面向懒人创作者的工具站项目：

- **主域 slothpack.com**：品牌展示页（本仓库，Astro 构建）
- **工具子域 tools.slothpack.com**：HTools 工具站（独立项目，不在本仓库）

> We pack. You relax. / 我们打包，你躺平。

## 品牌调性

慵懒、松弛、低饱和、大留白、极慢淡入。页面采用极简信纸布局（左对齐、40% 内容宽度、大留白），不做花哨动效。

## 技术栈

- [Astro](https://astro.build) 7.x（静态输出，`output: 'static'`）
- 纯 CSS（无 TypeScript、无 Tailwind）
- 部署目标：Cloudflare（Pages 或 Workers 静态资源，见「部署」一节）

## 本地开发

**Node 版本要求 `>= 22.12.0`**（见 `package.json` 的 `engines`）。Astro 7 会直接拒绝更低版本，
构建会以 `Node.js vX is not supported by Astro!` 失败。如果本机 PATH 上是 Node 20，需要先切到 22/24：

```powershell
$env:PATH = "<node-22-or-newer>\bin;$env:PATH"
node --version    # 确认 >= v22.12
```

```bash
npm install
npm run dev       # 开发服务器（localhost:4321）
npm run build     # 构建到 dist/
npm run preview   # 本地预览构建产物
```

> `dist/index.html` 用 `file://` 直接打开会丢样式（资源引用是绝对路径 `/css-variables.css`、`/logo-mark.png`），
> 必须走 HTTP 服务或部署后访问。这是 Astro 产物固有特性，不是缺陷。

## 项目结构

```
├── astro.config.mjs          # site: https://slothpack.com, output: static
├── wrangler.jsonc            # Workers 静态资源配置（线上真实部署形态待核实）
├── gen_logo_assets.py        # 从 brand/ 母版生成 Logo 与 favicon
├── gen_favicon.py            # 初始化遗留脚本，已失效（见 brand/README.md）
├── brand/                    # 品牌母版（不参与构建、不会被部署）
├── public/
│   ├── css-variables.css     # 共享设计令牌（旧命名 --color-*，tools 子域跨域直引）
│   ├── logo-mark.png         # 品牌标记 136×144（v6 完整插画，页面按 48px 高显示）
│   ├── favicon.ico           # 头像版，16 / 32 / 48 三尺寸
│   ├── apple-touch-icon.png  # 头像版，180×180
│   ├── favicon.svg           # 初始化遗留，未被引用
│   ├── og-image.png          # 社交分享图 1200×630
│   ├── robots.txt            # 爬虫规则（含 Sitemap 行，排除 404.html）
│   └── _headers              # CORS 与安全头
├── src/
│   ├── pages/
│   │   ├── index.astro       # 首页（信纸布局）
│   │   └── 404.astro         # 迷路兜底页
│   ├── layouts/
│   │   └── BaseLayout.astro  # 全局 head、字体、两套令牌、Header/Footer/SearchModal
│   ├── components/
│   │   ├── Header.astro      # 顶部导航（72px 粘性、移动端汉堡）
│   │   ├── Footer.astro
│   │   ├── SearchModal.astro # Cmd+K 搜索弹窗（目前只有界面，没有数据源）
│   │   ├── ToolCard.astro    # 下面三个为第二批组件，尚未在页面中使用
│   │   ├── PackCard.astro
│   │   └── EmptyState.astro
│   └── styles/
│       ├── theme.css         # 第二套令牌 --sloth-*（同时含 body 重置等全局样式）
│       └── global.css        # 全局样式、淡入动效、响应式
```

## 共享设计令牌

`public/css-variables.css` 是主域与 tools 子域共用的颜色/字体变量来源：

- 主域通过 `<link href="/css-variables.css">` 引用；
- tools 子域可跨域直引 `https://slothpack.com/css-variables.css`（`public/_headers` 已配置 `Access-Control-Allow-Origin: *`）。

> ⚠️ 已知问题：`src/styles/theme.css` 是**第二套令牌**（`--sloth-*`），`BaseLayout.astro` **两套都引入**。
> 首页 / 404 / `global.css` 用旧命名，Header / Footer / SearchModal 用新命名。两套色值一致，所以当前视觉正常，
> 但命名必须统一 —— 该改动会牵动 tools 子域，尚未处理。

## Logo 与 favicon

- **页面标记**：`public/logo-mark.png` = **v6 完整插画**，顶部导航 / 首页品牌行 / 页脚三处统一 **48px 高**。
  > ⚠️ 24px 下完整插画无法辨识（只是一团糊影），因此经确认把标记高度放宽到 **48px** ——
  > 这是对早期"三处统一 24px"规格的**有意修改**，不是笔误。
- **favicon**：`public/favicon.ico` 为**头像版**（16/32/48 三帧），`apple-touch-icon.png` 同源；
  头像母版已清除插画中的装饰弧线碎片与椅子角，脚本会做单一连通域自检。
- `</>` 符号母版保留在 `brand/logo-glyph-master.png`；若要换回符号版 favicon，改 `gen_logo_assets.py` 一处即可。
- 母版与再生成方式见 `brand/README.md`；改动母版后运行 `python gen_logo_assets.py`。
- 插画原图（1990×2107，透明底）目前只存在于桌面（`logo-v6-transparent.png`）；
  仓库内是长边 480px 的母版 `brand/logo-mark-master.png`。

## SEO

- `BaseLayout.astro` 输出 canonical、Open Graph、Twitter Card、JSON-LD（WebSite + Organization）与 `theme-color`；
  404 页带 `robots: noindex, follow`，且**不输出** canonical 与结构化数据。
- `public/robots.txt` + `public/sitemap.xml`（当前仅首页一条；新增页面时同步更新，或改用 `@astrojs/sitemap`）。
- 待办（需在 Cloudflare 后台处理）：`www` → 根域 301、HTTPS 强制、HSTS —— 实测三者目前**均未配置**。

## 页脚链接

主页、工具导航、提交工具、关于，共 **4 项**，全部使用**绝对路径**指向 `tools.slothpack.com`。

> 早期规划为 7 项（另含许可证、免责声明、隐私），当前实现只有 4 项。
> 注意：`tools.slothpack.com` 目前尚未解析上线，因此上述链接暂时都无法访问。

## 部署

1. GitHub 仓库：`slothpack-home`
2. Cloudflare 侧：**真实形态待核实**。仓库里同时存在两套互斥的约定：
   - Pages 约定：构建命令 `npm run build`，输出目录 `dist`，Node 22；
   - `wrangler.jsonc`（Workers 静态资源）：`assets.directory = ./dist`，`not_found_handling = "404-page"`。

   需要在 Cloudflare 后台确认线上究竟是哪一种，然后二选一并清理另一套配置。
3. 绑定 `slothpack.com` 与 `www.slothpack.com`
4. `www` → 根域 301：Cloudflare **Rules → Redirect Rules**
5. **不要**在 `public/` 下用 `_redirects` 写 404 状态码：Cloudflare 只接受 200/301/302/303/307/308，
   写 `404` 会导致部署失败（code 100324）

## 联系方式

support@slothpack.com · Telegram: @SlothPack
