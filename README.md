# Code-driven Design / 代码驱动设计

用代码完成视觉设计：Logo、Icon、卡片、网页和界面、信息图、交互演示、HTML 演示文稿与品牌视觉；让设计可以预览、操作、修改，并按需求导出或发布。

核心方法是 **理解需求 → 提取视觉规则 → 用代码构建 → 真实交互预览 → 迭代 → 交付**。屏幕设计使用响应式布局、组件和状态，图解使用关系或数据，印刷设计才使用毫米、出血和 CMYK。卡片是其中一个应用场景。

## 适用场景

| 场景 | 可以交付 |
| --- | --- |
| Logo 与品牌标识 | 标志、字标及组合形式，按使用场景提供彩色／单色／反白矢量资产 |
| Icon 与图标系统 | 统一网格、线宽、端点及光学重量的 SVG 图标族，按实际小尺寸检验 |
| 网站与落地页 | 品牌页面、产品介绍、专题页及响应式布局 |
| 界面与组件原型 | 工作台、应用页面、表单状态、筛选与比较交互 |
| 信息图与流程图 | 结构、关系、步骤、对比和可展开说明 |
| 交互解释与小工具 | 控件影响结果的机制演示、计算器、情景模拟 |
| HTML 演示文稿 | 可键盘翻页的展示、交互页面和图解 |
| 品牌与印刷视觉 | 卡片、标签、海报、邀请函、包装插页及按需生产文件 |

它用于有视觉成品目标的工作。纯后端修复、独立数据诊断、照片生成等任务使用相应工作流；需要这些能力时可以协作，而不替代它们。现有仓库、已确认设计和语言偏好都会保留。

## 安装

### Windows：解压后双击

1. 下载 [最新安装包](https://github.com/onlychuan/code-driven-design-skill/releases/latest)。
2. 解压 ZIP。
3. 双击 `install.cmd`。

安装器只复制本技能，不需要管理员权限，不修改全局执行策略，也不自动安装 Python 或印刷依赖。已有同名技能时会停止；更新需显式使用 `-Force`，并保留旧版本备份。备份放在技能扫描目录之外，避免重复显示同名技能。

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
$code-driven-design 为我的品牌设计一个 Logo。先给可编辑矢量方案和小尺寸预览，再交付独立 SVG、单色和反白版本。
```

```text
$code-driven-design 延续我现有界面的图标风格，做一套搜索、设置、上传、下载 Icon，交付单独 SVG 和统一规范。
```

```text
$code-driven-design 参考我的品牌网站，做一个新品发布页面，有真实的规格切换交互，并适配手机。先给我可运行预览。
```

```text
$code-driven-design 把这套装机步骤做成可点击展开的流程图，每一步显示零件和说明，给我单文件 HTML。
```

```text
$code-driven-design 做一个调节输入就能看到结果变化的机制演示，标清假设和演示数据。
```

```text
$code-driven-design 把我的销售内容做成 HTML 演示文稿，支持键盘翻页，保留可编辑源文件。
```

```text
$code-driven-design 把这个已确认的 HTML 原样发布到 Sites，保留 iframe sandbox 和 CSP，上线后给我生产 URL。
```

```text
$code-driven-design 做一张 A5 活动海报，文案用中文，先给可编辑原型，再导出带 3mm 出血的印刷 PDF。
```

## 包含什么

| 能力 | 做法 |
| --- | --- |
| 品牌提取 | 从网站、已提供素材和已确认设计中提取字体、颜色、网格、图像与语气 |
| 标志与图标 | 以真实矢量源为核心，检查字体依赖、小尺寸、背景版本及图标家族一致性 |
| 视觉系统 | 用设计 tokens 管理字体、颜色、间距、布局与状态，避免每个页面各做一套 |
| 真实交互 | 根据实际目的构建筛选、选择、展开、翻页、参数改变和结果反馈 |
| 内容与状态 | 把文案、数据、关系和交互状态从重复标记中提取，便于后续修改 |
| 屏幕验证 | 检查响应式、键盘操作、焦点、文字边界、内容状态和输入输出行为 |
| 图解验证 | 核对关系、流程与计算逻辑，标明真实来源、假设或演示数据 |
| 印刷交付（可选） | 毫米制场景、SVG、CMYK PDF、转曲、页面框和工厂说明 |
| 二维码（按需） | 使用真实目标地址，保留静区并验证导出的二维码 |
| 原样发布 | 用内容哈希确认附件、部署副本和归档一致，保留安全边界 |
| 格式与发布 | 交付用户需要的格式；PPTX、分析图表等调用相应流程，发布与邮件按用户授权进行 |

## 本地示例

三个数字示例可以直接用浏览器打开，无需安装运行时：

- [Logo／Icon 资产工作台](skills/code-driven-design/assets/logo-icon-study.html)：实际尺寸对照、颜色和线宽控制，以及独立 SVG 导出。
- [交互界面](skills/code-driven-design/assets/interactive-interface.html)：响应式工作台，带真实示例状态。
- [交互解释器](skills/code-driven-design/assets/interactive-explainer.html)：SVG 机制图，控件改变可视结果。

这些文件是可修改的起点，主题和内容都可以替换，不规定所有设计长成相同布局。图像、复杂动效、WebGL 或框架项目应按具体需求选择合适实现。

Logo／Icon 流程见 [logo-icons.md](skills/code-driven-design/references/logo-icons.md)。SVG 成品应包含真实矢量几何；字标应按交付要求转曲，或明确说明保留文本的字体依赖。PNG 是按需栅格输出，HTML 是预览载体；不将卡片截图或嵌入 PNG 的 SVG 当作可编辑矢量标志。

### 可选的物理场景渲染器

印刷小工具需要 Python 3.10+。在仓库根目录运行：

```sh
python skills/code-driven-design/scripts/render_design.py skills/code-driven-design/assets/example-card.json --out ./output/demo
```

该小工具的 HTML、普通 SVG 和二维码生成不需要第三方 Python 包。PDF 与字体转曲需要可选依赖：

```sh
python -m pip install -r requirements-print.txt
```

印刷字体由使用者提供可用路径，并确认使用权。仓库不分发商业字体。所有示例颜色都是数字参考或工作配方；不宣称 Pantone 精确匹配、ICC 色彩转换或 PDF/X 认证。完整说明见 [印刷流程](skills/code-driven-design/references/print-production.md)。

渲染器字段和命令见 [renderer.md](skills/code-driven-design/references/renderer.md)。它仅服务于适合固定尺寸场景的印刷设计；网站、界面和信息图可直接用 HTML/CSS/SVG/canvas 或既有框架编写。

## 开发与验证

```sh
python -m unittest discover -s tests -v
python scripts/check_package.py
python scripts/package_release.py --out ./release
```

CI 在 Windows、macOS、Linux 上检查安装器和渲染器，并验证 PDF 输出。安装包带 SHA256 清单。源码、测试和安装器均可审查；MIT 许可。

本技能无需 API key、MCP 服务器或外部账户即可制作本地设计。Sites、邮件和内联可视化依赖当前环境中可用的相应工具，按需使用。
