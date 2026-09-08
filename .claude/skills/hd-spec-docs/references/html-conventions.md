# HTML 规范源文件约定

## 文件命名

| 文件 | 角色 |
|---|---|
| `规范总览.html` | 封面 + TOC，固定名 |
| `NN-短标题.html` | 章节。`NN` 两位数字，短标题无空格、无路径分隔符 |
| `images/NN-slug.png` | 该章截图。slug 用英文/数字/连字符 |

浏览器互跳靠文件名：`href="04-版本发布.html"`、`href="规范总览.html"`。打包脚本按同样规则改写成 `#sec-04` / `#top`。

改文件名时必须同步改：总览 TOC、其他章的交叉链接、面包屑（面包屑是纯文本，不依赖文件名，但编号要一致）。

## 章节骨架

与 [../assets/chapter-template.html](../assets/chapter-template.html) 一致：

1. `<!DOCTYPE html>` + `lang="zh-CN"` + `<meta charset="UTF-8">`
2. `<title>NN - 中文标题</title>`（与文件名编号一致）
3. 内联 `<style>`，色板与现有文件相同（见下方 CSS）
4. `<header>`：面包屑 → 知识库首页、`<h1>NN · 标题</h1>`（不要写「最近更新」占位）
5. `<main>`：若干 `.card`，每张卡一个 `<h2>`
6. 最后一张卡：「变更记录」三列表（日期 / 修改人 / 内容）
7. `<footer>© 汽车诊断软件开发团队 · 内部资料</footer>`

编码 UTF-8 无 BOM，换行 LF。

## 总览 TOC 卡片

```html
<a class="toc-item" href="01-编码规范.html">
  <div class="n">01</div>
  <div class="t">编码规范 &amp; 代码评审</div>
  <!-- 无实质内容时： -->
  <span class="s">待补充</span>
  <!-- 撰写中： -->
  <span class="s wip">撰写中</span>
</a>
```

有完整正文后去掉徽章。`.legend` 里保留图例即可。

## CSS 类目录

源文件各自内联一份 CSS，保证单文件可打开。新增章节从模板拷，不要换色。

| 类 | 用途 |
|---|---|
| `.card` | 一节内容块 |
| `.note` | 蓝条说明 |
| `.warn` | 橙条警告 / 必须核对 |
| `.danger` | 红条禁止 / 强制 |
| `.ok` | 绿条正向要求 |
| `.purpose` | 章首「目的」说明（05 在用） |
| `.empty` | 待补充占位，内含 `.icon` / `.t` / `.s` |
| `figure` / `figcaption` | 截图 + 图题 |
| `figure.placeholder` | 计划有图但还没截 |
| `pre > code` | 多行代码 / 提交信息 / 包名示例 |
| `code` | 行内标识符、分支名、版本号 |
| `.toc-grid` / `.toc-item` | 仅总览 |

色板：`--primary:#0b5cad`、`--primary-dark:#073d75`、`--bg:#f6f8fb`、`--warn:#d98014`、`--ok:#1a8a3f`、`--danger:#c0392b`。

改皮肤要同时改所有 HTML 的 `:root` 以及 `tools/build_pdf.py` 里的 `SHARED_CSS`。

## 标题层级

- `h1` 仅出现在 header，一章一个。
- `h2` 对应卡片主标题（一、编码规范 / 1. Bug 推进要求）。
- `h3` / `h4` 卡片内部小节。不要跳级。

## 截图

源 HTML **必须**相对路径，禁止把 data-URI 写进源文件（单文件会到几百 KB，编辑器和 Read 工具都会失败）。

```html
<figure>
  <img src="images/04-oa-form.png" alt="OA 流程发起页面截图">
  <figcaption>图 3-1:OA 单填写示例,标注"软件包名称 + 版本号 + 备注"位置</figcaption>
</figure>
```

尚未截图时：

```html
<figure class="placeholder">
  <div class="img-tip">待补充截图</div>
  <figcaption>图 x-x:说明需要拍什么界面</figcaption>
</figure>
```

`alt` 写界面名称，`figcaption` 写「图 章内序号:要点」。

把已烤进 HTML 的 data-URI 还原：

```bash
python tools/embed_images.py --extract 04-版本发布.html
```

## 交叉链接

- 章 → 总览：`href="规范总览.html"`（面包屑已有）
- 章 → 章：`href="04-版本发布.html"`，不要写死 `#sec-04`（那是合集里的 id，独立浏览无效）
- 外链：完整 `http(s)://`，可 `target="_blank"`

## 空章节 / 空小节

整章没写：main 里一张 `.empty` 卡，总览给「待补充」。

某一 `h2` 还没写：该卡内部用 `.empty`，不要删标题（目录结构要稳定）。

## 变更记录

每章末尾保留。新增行插在表体最下（或最上，但全仓库统一：现有文件都是自上往下按时间加，继续往下追加）。

日期格式 `YYYY-MM-DD`。
