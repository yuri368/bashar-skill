# Bashar Skill

一个面向 Codex / AI Agent 的 Bashar（巴夏）原文资料检索与回答辅助 Skill。

本项目用于整理、检索和引用 Bashar 相关原文资料，帮助 AI 在回答巴夏相关问题时，尽量回到可追溯的原始文本，而不是生成泛化、鸡汤化或脱离语境的灵性解释。

> 当前项目仍处于早期版本，资料结构、索引质量、主题整理和回答规则都还在持续完善中。

---

## 版本

当前版本：`v0.2.0`

版本规则采用轻量语义化版本：

- `v0.1.0`：Bashar 资料库基础发布版。
- `v0.2.0`：统一正文资料编码为 UTF-8，补充原文直搜优先规则，重建全文检索索引，并建立版本号记录。
- 后续 `v0.2.x`：错字、路径、索引小修。
- 后续 `v0.x.0`：检索规则、资料结构、回答协议等可感知能力升级。
- `v1.0.0`：资料结构、索引、安装与回答行为进入稳定可复用状态。

---

## 包含什么

- `SKILL.md`：skill 的主入口和行为规则。
- `巴夏词汇定义.md`：只记录巴夏原文中的关键词定义。
- `巴夏主题索引.md`：人工维护的主题入口，每个主题默认 3 篇以内，最多 5 篇。
- `迭代历史.md`：记录本 skill 的长期迭代轨迹。
- `sources/`：Bashar 资料库。
- `sources/_meta/articles.jsonl`：资料元数据。
- `sources/_meta/search_index.jsonl`：预计算全文检索索引。
- `scripts/search_sources.py`：检索资料库。
- `scripts/build_search_index.py`：重建预计算索引。
- `agents/openai.yaml`：Codex UI 展示信息。

---

## 项目定位

`bashar-skill` 目前主要用于个人资料整理和 Codex Skill 使用，并顺带发布到 GitHub。

项目中大部分内容由 Codex 辅助生成，当前版本不保证资料整理、索引质量和回答规则完全可靠。使用时建议自行判断，并根据原文继续校准。

它是一个围绕 Bashar 原文资料建立的本地知识 Skill，目标是让 AI 在处理 Bashar 相关问题时，先检索资料库，再基于原文组织回答。

本项目的核心原则是：

> 先找原文，再组织回答。

---

## Bashar 简介

Bashar 是 Darryl Anka 传讯的一个意识体名称。Bashar 的资料常围绕信念系统、定义、兴奋、同步性、显化、恐惧、行动、关系和自我认知等主题展开。

本项目不负责证明或反驳 Bashar 信息的真实性，而是把相关文本整理成一个可被 AI 检索、引用和校准的本地资料库。

---

## 核心功能

- 根据用户问题检索 Bashar 资料库。
- 优先使用原文和对话结构，而不是直接抽象成二手总结。
- 对高频主题建立人工索引，例如兴奋、定义、恐惧、同步性、关系、显化等。
- 用词汇定义文件约束核心概念，避免随意改写术语含义。
- 通过脚本重建搜索索引，改善本地资料检索。

---

## 仓库结构

```text
bashar/
├── SKILL.md
├── README.md
├── VERSION
├── 巴夏词汇定义.md
├── 巴夏主题索引.md
├── 迭代历史.md
├── agents/
│   └── openai.yaml
├── scripts/
│   ├── build_search_index.py
│   ├── search_sources.py
│   └── export_github_package.py
└── sources/
    ├── _indexes/
    ├── _meta/
    └── ...
```

---

## 安装方式

如果你使用 Codex Skill，可以将本仓库放到本地 skills 目录中，例如：

```powershell
git clone https://github.com/yuri368/bashar-skill.git C:\Users\Yuri368\.codex\skills\bashar
```

或在已有 skill 目录中更新：

```powershell
git pull
```

---

## 触发方式

在 Codex 中，提到以下词汇时通常会触发本 skill：

- 巴夏
- Bashar
- 跟随兴奋
- 兴奋公式
- 同步性
- 定义
- 显化
- 恐惧
- 传讯

---

## 常用检索

重建索引：

```powershell
python scripts/build_search_index.py
```

搜索资料：

```powershell
python scripts/search_sources.py "跟随兴奋"
```

如果主题索引还不完善，应直接搜索 `sources/` 中的原文资料，并交叉使用多个关键词。

---

## 维护规则

- 新增或修改资料后，优先重建搜索索引。
- 修改 skill 行为后，在 `迭代历史.md` 记录原因和影响。
- 主题索引只是入口，不是最终权威；回答应回到原文资料。
- 不把自己的概括写成 Bashar 原文。
- 不把所有内容混成泛灵性表达；尽量保留 Bashar 的原始术语和问答语境。

---

## 发布与导出

这个 GitHub 发布包来自本地工作 skill。发布前应确认：

- 正文资料可以用 UTF-8 正常读取。
- `sources/_meta/search_index.jsonl` 已重建。
- `README.md`、`VERSION`、`迭代历史.md` 已同步版本说明。
- Git tag 与 `VERSION` 文件一致。

自动提交并推送到 GitHub：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/publish_to_github.ps1 -Message "发布本次 Bashar 资料库更新"
```

发布新版本并自动打 tag：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/publish_to_github.ps1 -Message "发布 v0.2.1" -Version 0.2.1
```

脚本会在推送前检查远端分支状态、重建检索索引、扫描正文 UTF-8 编码、运行一次 `Bashar` 检索 smoke test，然后提交并推送当前分支。使用 `-DryRun` 可以预览会执行的步骤。

---

## 当前限制

- 主题索引仍需人工继续校准。
- 词汇定义库还不完整。
- 部分原文来源路径和元数据可能需要进一步清理。
- 检索结果质量依赖于索引构建质量。
- 当前主要面向个人使用和 Codex Skill 场景，并非完整公开资料站。

---

## 注意事项

本仓库主要用于个人资料整理、Codex Skill 使用和 Bashar 文本检索。

`sources/` 中的文本来源复杂，仓库保留原路径和元数据。使用、发布、引用或再分发前，请自行确认适用场景和相关权利边界。

本项目不是 Bashar、Darryl Anka 或相关机构的官方项目。

---

## License

本仓库目前没有设置开源许可证。

`SKILL.md`、脚本和索引结构主要用于个人 Skill 迭代与资料检索。

`sources/` 中的资料请按其原始来源和实际使用场景自行判断。
