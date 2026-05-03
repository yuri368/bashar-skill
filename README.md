# Bashar Skill

> 一个 **原文优先、可检索、可迭代** 的 Bashar / 巴夏 Codex Skill。  
> 目标不是把巴夏内容压缩成二手鸡汤，而是让 Codex 在回答时尽量从本地原文、主题索引、词汇定义和对话结构中长出来。

------

## 这是什么？

`bashar-skill` 是一个面向 Codex 的 Bashar / 巴夏资料库 Skill。

它把以下内容组织在一起：

- Bashar-only 原文资料库
- 巴夏核心词汇定义
- 人工维护的主题索引
- 预计算全文检索索引
- 本地检索脚本
- Codex Skill 行为规则
- 长期迭代记录

它适合用来回答、检索和整理这些主题：

- 跟随最高兴奋
- 限制性信念
- 恐惧与负面信念
- 定义与核心信念
- 同步性
- 显化
- 行动与祈祷
- 臣服与允许
- 平行实相
- 巴夏式对话结构与追问节奏

------

## 为什么做这个 Skill？

很多 Bashar / 巴夏内容在传播中会被过度总结、转译、心理学化或鸡汤化。

这个 Skill 的目标是：

1. **先找原文，再回答**
2. **少做二手总结**
3. **保留巴夏式对话节奏**
4. **把关键词定义固定到原文锚点上**
5. **让 Skill 能随着使用继续校准和进化**

简单说：

> 不是让 AI “装作懂巴夏”，  
> 而是让 AI 先回到 Bashar-only 资料库，再基于原文回应。

------

## 核心特性

### 1. 原文优先

当用户要求：

- “巴夏原文怎么说？”
- “资料库里有没有？”
- “找一下关于恐惧的原文”
- “按巴夏的说法回答”
- “这个和原文冲突吗？”

Skill 会优先检索 `sources/`，再根据来源回答。

------

### 2. Bashar-only 资料筛选

本仓库发布包由本地完整 Skill 导出，并筛选为 Bashar-only 副本。

当前发布结果：

| 项目                         |    数量 |
| ---------------------------- | ------: |
| 保留 `source_persona=Bashar` | 2699 条 |
| 剔除非 Bashar 来源           |  258 条 |
| 预计算索引记录               | 2699 条 |
| 已索引正文文件               | 2504 个 |

------

### 3. 关键词定义库

`巴夏词汇定义.md` 用来记录巴夏原文中的关键词定义。

例如：

- 定义
- 核心信念
- 兴奋
- 恐惧
- 职业 / 目标
- 臣服
- 祈祷
- 责任

这个文件不做自由发挥式总结，只保存有来源路径的短原文锚点。

------

### 4. 主题索引

`巴夏主题索引.md` 是人工维护的高价值入口。

每个主题默认控制在 3 篇以内，最多 5 篇，避免资料入口无限膨胀。

主题来源使用固定格式：

```markdown
- `[1][-]` `sources/...` —— 用途
```

含义：

| 标记  | 含义                               |
| ----- | ---------------------------------- |
| `[1]` | 最高优先级                         |
| `[2]` | 次优先级                           |
| `[3]` | 扩展或对照                         |
| `[+]` | 已锁定，默认不替换、不删除、不降级 |
| `[-]` | 可正常迭代                         |

------

### 5. 预计算检索索引

`sources/_meta/search_index.jsonl` 是预计算全文检索索引。

`scripts/search_sources.py` 会优先使用该索引；如果索引不存在，会自动回退到 `articles.jsonl`。

------

### 6. 可迭代 Skill

这个 Skill 不是一次性提示词，而是一个长期迭代系统。

当用户指出：

- “这个不像巴夏”
- “这和原文冲突”
- “以后不要这样说”
- “这个表达保留”
- “把这个加入 Skill”
- “继续优化这个 Skill”

就应该修改对应文件，并把变更写入 `迭代历史.md`。

------

## 仓库结构

```text
bashar-skill/
├─ SKILL.md
├─ README.md
├─ 巴夏词汇定义.md
├─ 巴夏主题索引.md
├─ 迭代历史.md
├─ agents/
│  └─ openai.yaml
├─ scripts/
│  ├─ search_sources.py
│  ├─ build_search_index.py
│  └─ export_github_package.py
└─ sources/
   ├─ _meta/
   │  ├─ articles.jsonl
   │  └─ search_index.jsonl
   ├─ _indexes/
   └─ ...
```

------

## 快速安装

将仓库克隆到 Codex skills 目录，并保持目录名为 `bashar`：

```powershell
git clone https://github.com/yuri368/bashar-skill.git $env:USERPROFILE\.codex\skills\bashar
```

如果你的 Codex skills 根目录不是：

```powershell
$env:USERPROFILE\.codex\skills
```

请把命令最后的路径替换成你的实际 skills 目录。

------

## 如何触发

在 Codex 中提到这些关键词时，Skill 会更容易被使用：

```text
bashar
巴夏
跟随兴奋
限制性信念
核心信念
恐惧
同步性
显化
平行实相
找原文
资料库里有没有
继续优化这个 skill
```

------

## 常用检索命令

### 搜索“兴奋”

```powershell
python scripts/search_sources.py 兴奋 --limit 5
```

### 搜索“信念 / 定义”

```powershell
python scripts/search_sources.py 信念 定义 --limit 5
```

### 搜索正文里的“恐惧”

```powershell
python scripts/search_sources.py 恐惧 --content --limit 5
```

### 搜索“祈祷 / 行动”并扫描正文

```powershell
python scripts/search_sources.py 祈祷 行动 --content --format 文本 --limit 5

```

### 搜索“平行实相”

```powershell
python scripts/search_sources.py 平行实相 --limit 5

```

默认只检索：

```text
source_persona=Bashar

```

如果你明确需要比较其他来源，可以关闭 persona 筛选：

```powershell
python scripts/search_sources.py 关键词 --persona ""

```

------

## 重建搜索索引

修改 `sources/` 或 `sources/_meta/articles.jsonl` 后，运行：

```powershell
python scripts/build_search_index.py

```

重建后，`scripts/search_sources.py` 会继续优先使用：

```text
sources/_meta/search_index.jsonl

```

------

## 推荐工作流

当你想让 Codex 按 Bashar 资料回答时，可以这样使用：

```text
用 bashar skill 回答：我现在很迷茫，不知道下一步该做什么。

```

或者：

```text
用 bashar skill 查一下：巴夏关于恐惧是信使的原文在哪里？

```

更适合资料整理的用法：

```text
继续优化 bashar skill：
把“恐惧与负面信念”的主题索引重新检查一遍，
如果有更合适的原文入口，就更新主题索引和迭代历史。

```

------

## Skill 的回答原则

这个 Skill 的核心原则写在 `SKILL.md` 中，简化来说是：

1. 能查原文，就先查原文。
2. 不把巴夏内容过度心理学化、管理学化、鸡汤化。
3. 遇到关键词时，优先查 `巴夏词汇定义.md`。
4. 遇到主题问题时，优先查 `巴夏主题索引.md`。
5. 回答要保留巴夏式的短句、追问、重新定义和行动落地。
6. 如果 Skill 与原文冲突，原文优先，直接校准 Skill。

------

## 维护规则

修改时建议遵守：

1. 与巴夏原文冲突时，以原文校准 `SKILL.md`。
2. 新增词汇定义时，写入 `巴夏词汇定义.md`，并保留来源路径。
3. 新增主题入口时，写入 `巴夏主题索引.md`。
4. 修改资料库后，重建 `sources/_meta/search_index.jsonl`。
5. 每次实质修改后，更新 `迭代历史.md`。

------

## 发布包重建

本仓库由本地完整 Skill 通过导出脚本生成：

```powershell
python scripts/export_github_package.py --target H:\ProgramFiles\AIStudio\profile\.codex\skills\bashar-github --force

```

导出脚本会只复制 `source_persona=Bashar` 的资料，并重建 Bashar-only 的索引文件。

------

## 注意事项

这个仓库用于个人资料整理、Codex Skill 使用和 Bashar 文本检索。

`sources/` 中的文本来源复杂，仓库保留原路径和元数据。使用、发布、引用或再分发前，请自行确认适用场景和相关权利边界。

------

## License

本仓库目前没有设置开源许可证。

`SKILL.md`、脚本和索引结构主要用于个人 Skill 迭代与资料检索。  
`sources/` 中的资料请按其原始来源和实际使用场景自行判断。
