# SlothPack — 主域品牌页

SlothPack 是一个面向懒人创作者的工具站项目：

- **主域 slothpack.com**：品牌展示页（本仓库，Astro 构建）
- **工具子域 tools.slothpack.com**：HTools 工具站（独立项目）

> We pack. You relax. / 我们打包，你躺平。

## 品牌调性

慵懒、松弛、低饱和、大留白、极慢淡入。页面采用极简信纸布局（左对齐、40% 内容宽度、大留白），不做花哨动效。

## 技术栈

- [Astro](https://astro.build)（静态输出，`output: 'static'`）
- 纯 CSS（无 TypeScript、无 Tailwind）
- 部署：Cloudflare Pages（构建命令 `npm run build`，输出目录 `dist`，Node 22）

## 本地开发

```bash
npm install
npm run dev       # 开发服务器（localhost:4321）
npm run build     # 构建到 dist/
npm run preview   # 本地预览构建产物
```

## 项目结构

```
├── public/
│   ├── css-variables.css   # 共享设计令牌（单一来源，tools 子域共用）
│   ├── og-image.png        # 社交分享图（1200×630）
│   ├── favicon.ico         # 占位图标
│   └── _headers            # CORS 与安全头
├── src/
│   ├── pages/
│   │   ├── index.astro     # 首页（信纸布局）
│   │   └── 404.astro       # 迷路兜底页
│   ├── layouts/
│   │   └── BaseLayout.astro
│   ├── components/
│   │   ├── Header.astro    # 顶部导航
│   │   └── Footer.astro    # 页脚（链接指向 tools 子域）
│   └── styles/
│       └── global.css      # 全局样式、淡入动效、响应式
└── astro.config.mjs        # site: https://slothpack.com, output: static
```

## 共享设计令牌

`public/css-variables.css` 是主域与 tools 子域共用的颜色/字体变量**单一来源**：

- 主域通过 `<link href="/css-variables.css">` 引用；
- tools 子域可跨域直引 `https://slothpack.com/css-variables.css`（`public/_headers` 已配置 `Access-Control-Allow-Origin: *`）。

## 页脚链接

工具、分类、提交、关于、许可证、免责声明、隐私 全部使用**绝对路径**指向 tools.slothpack.com 对应页面（如 `https://tools.slothpack.com/license`），主域点击不会 404。

## 部署

1. GitHub 仓库：`slothpack-home`
2. Cloudflare Pages 连接仓库：preset **Astro**，构建命令 `npm run build`，输出目录 `dist`，Node 22
3. 绑定 `slothpack.com` 与 `www.slothpack.com`（CNAME → `slothpack-home.pages.dev`）
4. www → 根域 301：Cloudflare **Rules → Redirect Rules**（`http.host eq "www.slothpack.com"` → 301 → `https://slothpack.com/`，保留 query）

## Logo

当前为 `[LOGO]` 文字占位（统一 24px 高），favicon 为占位图标，待正式品牌资产到位后替换。

## 联系方式

support@slothpack.com · Telegram: @SlothPack
