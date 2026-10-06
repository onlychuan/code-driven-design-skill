# Code-driven Design / 代码驱动设计

把卡片、标签、海报和包装插页做成可编辑的 HTML/CSS 原型，再按需要导出矢量 SVG 和 CMYK 印刷 PDF。

这个技能整理了从品牌参考到工厂交付的完整工作方式。它使用共享的设计数据，避免网页预览和印刷稿各做一套后产生偏差。仓库中的卡片仅为通用演示，实际项目会沿用你的品牌、语言和尺寸。

## 安装

### Windows：解压后双击

1. 下载 [最新安装包](https://github.com/onlychuan/code-driven-design-skill/releases/latest)。
2. 解压 ZIP。
3. 双击 `install.cmd`。

安装器只复制本技能，不需要管理员权限，不修改全局执行策略，也不自动安装 Python 或印刷依赖。已有同名技能时会停止；更新需显式使用 `-Force`，并保留旧版本备份。

也可以在解压后的目录运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
```

### macOS / Linux

解压安装包后，在目录内执行：

```sh
bash install.sh
```

默认用户级安装目录为 `~/.agents/skills/code-driven-design`。旧版或自定义环境可用 `-Destination` / `--dest` 指定**技能父目录**，例如：

```powershell
.\install.ps1 -Destination "$env:USERPROFILE\.codex\skills"
```

```sh
bash install.sh --dest "$HOME/.codex/skills"
```

技能会在下一轮对话被发现；若未出现，重启 Codex。当前官方目录与发现机制见 [OpenAI 官方技能文档](https://learn.chatgpt.com/docs/build-skills)。安装器不会自动修改 Codex 配置。

### 让 Codex 帮你安装

把下面这句话发给 Codex：

```text
$skill-installer 从 https://github.com/onlychuan/code-driven-design-skill 安装 skills/code-driven-design
```

### 可选：作为技能插件分发

仓库包含便携 `plugin.json` 和兼容 `.codex-plugin/plugin.json`。支持自定义 marketplace 的客户端可以添加本仓库，然后在插件目录点击安装：

```sh
codex plugin marketplace add onlychuan/code-driven-design-skill
```

不同客户端的 marketplace 支持可能不同；双击安装和 `$skill-installer` 是独立路径。GitHub 发布不代表已进入 OpenAI 公共插件目录。相关机制见 [官方插件封装文档](https://developers.openai.com/plugins/build/plugins)。

## 使用

```text
$code-driven-design 参考我的网站，设计一张随箱卡。成品 90×55mm、双面、英文，先给我交互预览，确认设计后导出工厂印刷稿。
```

```text
$code-driven-design 把这个已确认的 HTML 原样发布到 Sites，保留 iframe sandbox 和 CSP，上线后给我生产 URL。
```

```text
$code-driven-design 做一张 A5 活动海报，文案用中文，提供可编辑原型和带 3mm 出血的印刷 PDF。
```

## 包含什么

| 能力 | 做法 |
| --- | --- |
| 品牌提取 | 从网站、已提供素材和已确认设计中提取字体、颜色、网格、图像与语气 |
| 可交互原型 | HTML/CSS 展示，按需要加入方案切换及少量评审控件 |
| 共享设计源 | 毫米制 JSON 场景用于预览、SVG 与 PDF，尺寸和颜色集中维护 |
| 印刷交付 | CMYK 矢量 PDF、字体转曲、裁切框、出血框、裁切标记，以及工厂说明 |
| 二维码 | 使用真实目标地址，保留静区并验证导出的二维码 |
| 原样发布 | 用内容哈希确认附件、部署副本和归档一致，保留安全边界 |
| 交付流程 | 区分屏幕预览和印刷文件；按用户授权发布或邮件发送 |

## 本地示例

先安装 Python 3.10+。在仓库根目录运行：

```sh
python skills/code-driven-design/scripts/render_design.py skills/code-driven-design/assets/example-card.json --out ./output/demo
```

HTML 和普通 SVG 不需要第三方 Python 包。PDF、字体转曲和生成新的二维码可能需要可选依赖：

```sh
python -m pip install -r requirements-print.txt
```

印刷字体由使用者提供可用路径，并确认使用权。仓库不分发商业字体。所有示例颜色都是数字参考或工作配方；不宣称 Pantone 精确匹配、ICC 色彩转换或 PDF/X 认证。完整说明见 [印刷流程](skills/code-driven-design/references/print-production.md)。

渲染器支持的准确字段与命令见 [renderer.md](skills/code-driven-design/references/renderer.md)。可用本地示例，也可让 Codex按品牌直接编写更复杂的 HTML/CSS/SVG。

## 开发与验证

```sh
python -m unittest discover -s tests -v
python scripts/check_package.py
python scripts/package_release.py --out ./release
```

CI 在 Windows、macOS、Linux 上检查安装器和渲染器，并验证 PDF 输出。安装包带 SHA256 清单。源码、测试和安装器均可审查；MIT 许可。

本技能无需 API key、MCP 服务器或外部账户即可制作本地设计。Sites、邮件和内联可视化依赖当前环境中可用的相应工具，按需使用。
