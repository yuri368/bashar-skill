# Bashar Sources Maintenance

## 范围

正式资料位于 `sources` 根目录和各主题目录。`_meta`、`_indexes` 是维护文件，不作为正文资料引用。

## 新增文档命名

- 放入最合适的主分类目录。
- 文件名使用目录内三位数编号：`NNN-标题.ext`。
- 不在文件名中保留来源占位前缀，例如 `Jimmy，`、`bxs、`、`ccc，`、`bbb、`、`xxx，`。
- 来源写入 `_meta/articles.jsonl` 的 `source_persona` 字段。

## 主类选择

主类表示用户最可能查找这篇文章的入口。一篇文件只放一个主类；跨主题关系用 `tags` 表达，不复制文件。

## 标签规则

- 标签规范维护在 `_meta/tags.yaml`。
- 每篇文档保留 3 到 12 个标签。
- 标签可以表示主题、概念、实践方式、来源人物或文本格式。

## 去重

- 先对文本做归一化：去掉 URL、空白、标点并统一大小写。
- 归一化哈希完全相同视为正文重复。
- 大段相同但不完全一致时，保留更完整或分类更准确的一份。
- 不要用复制文件实现多标签。

## 重建索引

重建时读取所有正式源文件，跳过 `_meta` 和 `_indexes`，重新生成：

- `_meta/articles.jsonl`
- `_indexes/categories.md`
- `_indexes/by-tag/*.md`

`articles.jsonl` 是维护底账；Markdown 索引是阅读入口。

## 当前生成时间

2026-04-17T05:10:57+08:00
