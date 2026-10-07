import { defineConfig } from 'astro/config';

// SlothPack 主域品牌页 —— 纯静态输出，无需适配器
export default defineConfig({
  site: 'https://slothpack.com',
  output: 'static',
  compressHTML: true,
  trailingSlash: 'ignore',
});
