# Bashar Skill

原文优先的可迭代 Bashar / 巴夏 Codex skill。

这个仓库把 `SKILL.md`、巴夏词汇定义、主题索引、检索脚本和 Bashar-only 资料库放在一起。目标不是把巴夏内容重新总结成一套二手理论，而是在使用 skill 时尽量从本地原文、对话结构和词汇定义里回应。

## 包含什么

- `SKILL.md`：skill 的主入口和行为规则。
- `巴夏词汇定义.md`：只记录巴夏原文中的关键词定义。
- `巴夏主题索引.md`：人工维护的主题入口，每个主题默认 3 篇以内，最多 5 篇。
- `迭代历史.md`：记录本 skill 的长期迭代轨迹。
- `sources/`：Bashar-only 原文资料库。
- `sources/_meta/articles.jsonl`：资料元数据。
- `sources/_meta/search_index.jsonl`：预计算全文检索索引。
- `scripts/search_sources.py`：检索资料库。
- `scripts/build_search_index.py`：重建预计算索引。
- `agents/openai.yaml`：Codex UI 展示信息。

## 资料筛选

这个 GitHub 发布包不是直接上传完整本地资料库，而是通过 `scripts/export_github_package.py` 从本地工作 skill 导出的 Bashar-only 副本。

本次发布结果：

- 保留 `source_persona=Bashar`：2699 条
- 剔除非 Bashar 来源：258 条
- 预计算索引记录：2699 条
- 已索引正文文件：2504 个

可用下面的命令复查：

```powershell
python - <<'PY'
import json
from collections import Counter
from pathlib import Path

rows = [
    json.loads(line)
    for line in Path("sources/_meta/articles.jsonl").read_text(encoding="utf-8").splitlines()
    if line.strip()
]
print(len(rows), Counter(row.get("source_persona", "") for row in rows))
PY
```

期望输出类似：

```text
2699 Counter({'Bashar': 2699})
```

## 安装

把仓库克隆到 Codex skills 目录，目录名保持 `bashar`：

```powershell
git clone https://github.com/yuri368/bashar-skill.git $env:USERPROFILE\.codex\skills\bashar
```

如果你的 Codex skills 根目录不在 `$env:USERPROFILE\.codex\skills`，把命令最后的路径换成你的实际 skills 目录。

## 使用

在 Codex 中提到 `bashar`、`巴夏`、`跟随兴奋`、`限制性信念`、`找原文` 等触发词时，skill 会被使用。

常用检索：

```powershell
python scripts/search_sources.py 兴奋 --limit 5
python scripts/search_sources.py 信念 定义 --limit 5
python scripts/search_sources.py 恐惧 --content --limit 5
python scripts/search_sources.py 祈祷 行动 --content --format 文本 --limit 5
python scripts/search_sources.py 平行实相 --limit 5
```

默认只检索 `source_persona=Bashar`。如果你明确要比较其他来源，可以使用：

```powershell
python scripts/search_sources.py 关键词 --persona ""
```

## 重建索引

修改 `sources/` 或 `sources/_meta/articles.jsonl` 后，运行：

```powershell
python scripts/build_search_index.py
```

`scripts/search_sources.py` 会优先使用 `sources/_meta/search_index.jsonl`；如果索引不存在，会自动回退到 `articles.jsonl`。

## 主题索引规则

`巴夏主题索引.md` 是人工维护的高价值入口。

每条来源格式：

```markdown
- `[1][-]` `sources/...` —— 用途
```

含义：

- `[1]` 最高优先级，`[2]` 次优先级，`[3]` 扩展或对照。
- `[+]` 表示锁定，没有用户明确说明不参与替换、删除或降级。
- `[-]` 表示可正常迭代。
- 每个主题最多 5 篇；没有明确必要时保持 3 篇以下。

## 迭代方式

这个 skill 是可迭代的。修改时优先遵守：

1. 与巴夏原文冲突时，以原文校准 `SKILL.md`。
2. 新增词汇定义时，写入 `巴夏词汇定义.md`，并保留来源路径。
3. 新增主题入口时，写入 `巴夏主题索引.md`。
4. 修改资料库后，重建 `sources/_meta/search_index.jsonl`。
5. 每次实质修改后，更新 `迭代历史.md`。

## 发布包重建

本仓库由本地完整 skill 通过导出脚本生成：

```powershell
python scripts/export_github_package.py --target H:\ProgramFiles\AIStudio\profile\.codex\skills\bashar-github --force
```

导出脚本会只复制 `source_persona=Bashar` 的资料，并重建 Bashar-only 的 `_indexes`。

## 许可

本仓库目前没有设置开源许可证。`SKILL.md`、脚本和索引结构用于个人 skill 迭代与资料检索；`sources/` 中的文本来源复杂，保留原路径和元数据，使用前请自行确认适用场景。

