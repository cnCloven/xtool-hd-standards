---
name: hd-spec-docs
description: This skill should be used when the user asks to 新增规范, 添加规范, 修改规范, 更新规范, 调整规范, 补充规范, 打包PDF, 生成PDF, 合并HTML, 规范转PDF, 插入截图, 编码图片, 更新知识库, or mentions 部门规范 / 柴油日常开发规范 HTML/PDF. Maintains the automotive diagnostic team's HTML spec knowledge base and packs all chapters into one PDF with internal jump links and embedded images.
---

# 部门规范 HTML → PDF

HTML 是规范的**唯一源文件**。PDF 是打包产物，禁止反向从 PDF 改内容。

本仓库是汽车诊断软件开发团队的规范知识库。独立 HTML 可在浏览器互跳；打包后的 PDF 用命名锚点做目录/章节跳转，截图以 data-URI 嵌进 PDF。

## 何时读哪份文件

| 场景 | 去哪 |
|---|---|
| 增删改某一章正文、截图、索引 | 按下面工作流直接改 HTML，再打包 |
| 文件名、CSS 类、章节骨架、截图约定 | 读 [references/html-conventions.md](references/html-conventions.md) |
| 新建一章的空文件 | 复制 [assets/chapter-template.html](assets/chapter-template.html) |
| 打包 PDF | 运行 `tools/build_pdf.py`，不要手写合并/打印脚本 |

## 仓库地图

```
规范总览.html          封面 + 文档索引（TOC 卡片）
01-编码规范.html       章节，文件名 NN-短标题.html
…06-新人入职.html
images/                截图源文件（HTML 用相对路径引用）
backup/                往期 PDF 归档（每次新打包后由脚本移入）
柴油日常开发规范_YYYYMMDD_HHMMSS.pdf  当前对外分发的合并 PDF
tools/build_pdf.py     合并 HTML、编码图片、Chromium 打印 PDF
tools/embed_images.py  仅在需要「单文件 HTML」时才把图烤进源文件
```

章节号来自文件名前两位数字，不是数组下标。`07-xxx.html` 对应 PDF 锚点 `#sec-07`。

## 工作流

### A. 修改已有规范

1. **改之前必须完整阅读目标 HTML**（整文件，不要只扫标题）。先弄清 header / 卡片划分 / 标题层级 / 已有 class / 交叉链接 / 变更记录，再动手。禁止凭记忆覆盖结构。
2. 只改这一章需要动的部分（通常是 `<main>`，以及必要时的截图）。
3. 更新该章末尾「变更记录」表：日期 / 修改人 / 内容。日期用当天（会话里的 currentDate）。页头不要写「最近更新」。
4. 若标题或完成状态变了，同步改 [规范总览.html](../../../规范总览.html) 对应 TOC 卡片（标题、`待补充` / `撰写中` 徽章）。
5. 从仓库根目录运行打包（见下方）。

不要顺手改其他章的正文。不要把截图改成 base64 写进源 HTML（Read/编辑会爆）。

### B. 新增一章

1. 扫描根目录已有 `NN-*.html`，取未占用的两位编号（通常是 max+1）。
2. 复制 `assets/chapter-template.html` 为 `NN-短标题.html`（短标题用中文，无空格）。
3. 填写 `<title>`、面包屑、`<h1>`、正文、变更记录。页头不要写「最近更新」。
4. 在 `规范总览.html` 的 `.toc-grid` 追加一张卡片：

```html
<a class="toc-item" href="07-示例.html">
  <div class="n">07</div><div class="t">示例标题</div>
  <span class="s">待补充</span>   <!-- 有实质内容后删掉徽章 -->
</a>
```

5. 截图放到 `images/NN-slug.png`，正文用 `<figure>` 引用（见 conventions）。
6. 打包 PDF。脚本会警告「总览未收录的章节」或「总览链到不存在的文件」——两者都要修到零警告。

### C. 插入 / 更换截图

1. 把 PNG/JPG 存到 `images/`，命名 `NN-英文短名.png`（例：`04-soft-version.png`）。
2. 在章节 HTML 里用相对路径，不要 data-URI：

```html
<figure>
  <img src="images/04-soft-version.png" alt="软件版本查询页面截图">
  <figcaption>图 2-1:挂网版本查询入口与核对要点</figcaption>
</figure>
```

3. 打包时 `build_pdf.py` 会把图编成 data-URI 写进 `build/bundle.html` 再打进 PDF。源 HTML 保持小文件。
4. 只有用户明确要求「发出去的单个 HTML 也要自带图」时，才运行 `python tools/embed_images.py 04-版本发布.html`。之后若还要继续改这一章，先 `--extract` 还原相对路径。

### D. 打包 PDF

从仓库根目录：

```bash
python tools/build_pdf.py
```

Windows 也可双击或运行 `tools/build_pdf.bat`。Python 不在 PATH 时用完整解释器路径调用该脚本。缺 playwright 时：

```bash
python -m pip install playwright pypdf
python -m playwright install chromium
```

默认产物：

- 根目录 `柴油日常开发规范_YYYYMMDD_HHMMSS.pdf`（文件名末尾带打包时的日期时间）
- 根目录里其余 `柴油日常开发规范*.pdf` 全部移入 `backup/`
- 中间文件 `build/bundle.html`（含编码后的图，可丢，下次会再生）

常用参数：`--out 自定义.pdf` 覆盖默认文件名；`--bundle-only` 只出 HTML 合集；`--format Letter` 对齐 2026-06 那版 US Letter（默认 A4）。

打包后核对脚本打印的「命名锚点 / 链接注释 / 内嵌图片」。至少应有 `top`、`sec-01`…`sec-NN`，目录卡片可点，章节面包屑「知识库首页」回到封面，`04` 章两张截图在 PDF 里可见。

## PDF 约定（对齐历史成品）

| 项 | 规则 |
|---|---|
| 页面 | A4，打印背景色（蓝头、提示条、代码块） |
| 跳转 | 封面 TOC → `#sec-NN`；面包屑首页 → `#top`；章间 `href="04-版本发布.html"` 在合集里改写成 `#sec-04` |
| 外链 | `http(s)://` 保持 URI，不改写 |
| 图片 | PDF 内嵌，不依赖外部文件 |
| 书签 | Chromium `outline=True` 按标题生成 |
| 页脚 | 「内部资料 · 请勿外传 · 页码」 |
| 元数据 Title | `汽车诊断软件开发团队规范知识库` |

不要再用 pypdf 把多份独立 PDF 拼起来后手写 GoTo——2026-07 那两份带时间戳的 PDF 就是这种做法，链接矩形会错位。唯一推荐路径是：先合成一份带 `id` 的 bundle HTML，再 Chromium 打印。

## 视觉与文案

- 色板、卡片、`.note` / `.warn` / `.danger` / `.ok` 必须与现有章节一致，禁止另起一套皮肤。
- 禁止项用 `.danger` + `⛔ 禁止`；强制核对用 `.warn`；正向要求用 `.ok`；补充说明用 `.note`。
- 未写完的节用 `.empty` 占位（图标 📝 + 「本节内容待补充」），并在总览给徽章。
- 每章保留「变更记录」表。跨章引用写 `详见 <a href="04-版本发布.html">04 版本与发布规范</a>`，让打包脚本改写锚点。

## 不要做的事

- 不要为了打包去改写各章源 HTML 的 `id` / 拆文件。合集由脚本生成。
- 不要把 `build/bundle.html` 当源文件编辑。
- 不要删除 `backup/` 里的往期 PDF，除非用户明确要求。
- 改任何 HTML 之前必须先完整阅读该文件。
- 不要引入 WeasyPrint（本机缺 GTK）。不要用 Word/Markdown 冒充源文件。
