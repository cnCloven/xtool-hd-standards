# 汽车诊断软件开发团队 · 部门规范知识库

本仓库是 HD 部门日常开发规范的**共建源**。给诊断软件开发同事看、改、继续往下补。

仓库地址：https://github.com/cnCloven/xtool-hd-standards

> 内部资料，请勿外传到仓库以外的公开渠道。

---

## 1. 背景：这套规范要解决什么

部门日常工作分散在编码、Git、华为云 Bug、版本挂网、车系跟进表等环节。过去约定多靠口头和零散 Wiki，新人上手慢，脚本也读不了各品牌各写各的跟进表。

这套知识库把约定收成**可点击跳转的 HTML 章节**，再打包成**一份带目录链接和内嵌截图的 PDF** 对外分发（邮件、OA、新人资料包）。目标：

- 写的人改 HTML，看的人打开 HTML 或 PDF 都能跳到对应章节
- 跟进表列名 / 表名固定，后续可用通用脚本读取所有品牌
- 每次改完能打出带时间戳的新 PDF，旧版自动进 `backup/`

---

## 2. 先记住三条

1. **HTML 是唯一源文件。** 改规范只改 `NN-*.html` 和 `规范总览.html`。不要打开 PDF 改字，也不要改 `build/bundle.html`。
2. **截图用相对路径。** 文件放到 `images/`，HTML 里写 `src="images/xxx.jpg"`。不要把 base64 贴进 HTML（文件会大到没法编辑）。
3. **改完打包再提交。** 本地跑一遍打包脚本，确认新 PDF 里目录能点、图还在，再 push。

---

## 3. 仓库里有什么

```
规范总览.html              封面 + 章节索引（用浏览器打开它开始读）
01-编码规范.html … 06-*.html
images/                    截图原图
柴油日常开发规范_时间戳.pdf  当前对外分发的合并 PDF
backup/                    往期 PDF
tools/build_pdf.py         把所有 HTML 合成一份 PDF
.claude/skills/hd-spec-docs/   给 Claude Code 用的维护 skill（人也可以当操作手册）
```

用浏览器直接打开 [规范总览.html](规范总览.html) 即可在章节间跳转，不需要起服务器。

---

## 4. 当前进展（2026-09-08）

| 编号 | 文件 | 已有内容 | 仍缺 |
|---|---|---|---|
| 01 | [01-编码规范.html](01-编码规范.html) | 命名约定、C++14 无异常、注释 / Doxygen 样例 | 代码评审流程 |
| 02 | [02-Git规范.html](02-Git规范.html) | `master`/`dev` 分支、提交信息格式 | 里程碑 / 看板 |
| 03 | [03-华为云Bug处理.html](03-华为云Bug处理.html) | Bug 推进节点、每月 10 日 OA 免测、Bug 转需求 | — |
| 04 | [04-版本发布.html](04-版本发布.html) | 包名、版本号 +0.1/+0.01、OA 标题、自测；含两张截图 | — |
| 05 | [05-团队协作.html](05-团队协作.html) | 跟进表三张固定表（`ECU总表` / `项目计划` / `特殊功能`）及列名；含两张填写示例 | 特殊功能表示例图；其它协作约定 |
| 06 | [06-新人入职.html](06-新人入职.html) | 空章节 | 整章待写 |

当前分发 PDF：仓库根目录最新的 `柴油日常开发规范_YYYYMMDD_HHMMSS.pdf`。

05 跟进表要点（脚本按**表名**读，名称不能写错）：

| 工作表顺序 | 表名（必须完全一致） | 作用 |
|---|---|---|
| 第 1 张 | `ECU总表` | 当前车系全部诊断内容 |
| 第 2 张 | `项目计划` | 任务拆分；含开发状态、版本号 |
| 第 3 张 | `特殊功能` | 特殊功能清单及底层/工程索引 |
| 第 4 张起 | 自定义 | 不得占用上面三个名字 |

---

## 5. 日常怎么改已有章节

1. **先把对应 HTML 从头读完**，看清标题层级、卡片、已有 class、交叉链接和文末「变更记录」，再动手。不要凭记忆覆盖结构。
2. 只改这一章需要动的部分。文案风格对齐现有章节：禁止用红条、强制核对用橙条、说明用蓝条。
3. 在该章「变更记录」表**追加一行**（日期 `YYYY-MM-DD` / 修改人 / 改了什么）。页头不要写「最近更新」。
4. 若章节从空变成有内容，去掉 [规范总览.html](规范总览.html) 卡片上的「待补充」徽章。
5. 打包 PDF（见第 7 节），检查目录跳转和截图。
6. `git pull` → `git add` 你改过的 HTML / 图片 / 新 PDF → commit → `git push`。

章与章互相引用时写文件名，例如：

```html
详见 <a href="04-版本发布.html">04 版本与发布规范</a>
```

打包脚本会把它改成 PDF 内部锚点。不要手写 `#sec-04`（浏览器单独打开章节时会失效）。

---

## 6. 如何新增一章规范

编号来自文件名前两位数字，下一章一般是 `07`。

1. 复制模板：

   `.claude/skills/hd-spec-docs/assets/chapter-template.html`

   存成仓库根目录的 `07-短标题.html`（短标题用中文，不要空格）。

2. 改 `<title>`、面包屑、`<h1>`、正文。文末保留「变更记录」表，写上初始一行。

3. 在 [规范总览.html](规范总览.html) 的 `.toc-grid` 里追加卡片：

```html
<a class="toc-item" href="07-短标题.html">
  <div class="n">07</div><div class="t">章节标题</div>
  <span class="s">待补充</span>
</a>
```

有完整正文后删掉 `<span class="s">待补充</span>`。撰写中用 `<span class="s wip">撰写中</span>`。

4. 需要截图时：文件放 `images/`（建议 `07-英文短名.png`），正文用：

```html
<figure>
  <img src="images/07-example.png" alt="界面名称">
  <figcaption>图 1-1:要点说明</figcaption>
</figure>
```

若该章还没有 `figure` 样式，从 [04-版本发布.html](04-版本发布.html) 或 [05-团队协作.html](05-团队协作.html) 拷一段 `figure` CSS 过来。

5. 运行打包。脚本若提示「总览未收录」或「总览链到不存在的文件」，按提示改到零警告。

更细的 HTML / CSS 约定见 [.claude/skills/hd-spec-docs/references/html-conventions.md](.claude/skills/hd-spec-docs/references/html-conventions.md)。

---

## 7. 打包 PDF

本机需要：Python 3、`playwright`、`pypdf`。第一次：

```bash
python -m pip install playwright pypdf
python -m playwright install chromium
```

之后在仓库根目录：

```bat
tools\build_pdf.bat
```

或：

```bash
python tools/build_pdf.py
```

脚本会：

- 生成 `柴油日常开发规范_YYYYMMDD_HHMMSS.pdf`（目录可点到各章，截图编进文件）
- 把根目录里其它 `柴油日常开发规范*.pdf` 移到 `backup/`
- 写出可丢弃的中间文件 `build/bundle.html`

打开新 PDF 快速核对：封面六张卡片能跳、章节蓝头「知识库首页」能回封面、04 / 05 的截图还在。

若提示某个 PDF「正被占用」，关掉预览窗口后再打包，或把那份手动拖进 `backup/`。

---

## 8. Git 协作建议

```bash
git clone git@github.com:cnCloven/xtool-hd-standards.git
git checkout -b 你的分支
# 改 HTML / 加图 / 打包
git add 改过的文件
git commit -m "docs: 说明改了哪一章、改了什么"
git push -u origin 你的分支
```

然后提 Pull Request 到 `main`。尽量一章一次提交，避免和别人同时改同一个 HTML。

不要提交：

- `.claude/settings.local.json`（本机权限）
- `build/`（打包中间文件）
- `__pycache__/`

这些已在 `.gitignore` 里。

---

## 9. 用 Claude Code 协助时

在本仓库打开 Claude Code，直接说「新增一章 xx 规范」或「把规范打成 PDF」即可。项目 skill `hd-spec-docs` 会按上面同一套流程改 HTML 并打包。

人改和 AI 改遵守同一规则：**先读目标 HTML，再改，再打包。**
