# LLM Wiki 快速开始

> 5 分钟上手 LLM Wiki 知识库工作流

---

## 前提条件

1. 思源笔记已安装并运行
2. 已配置好 LLM-Wiki 笔记本（笔记本 ID: `<NOTEBOOK_ID>`）

---

## 场景一：处理一篇文章（Ingest）

### 方式 A：从文件摄入（推荐）

```bash
# 1. 准备文章文件 article.md

# 2. 执行摄入（自动去重）
node ../siyuan-skill/siyuan.js wiki-ingest --file article.md --title "文章标题"

# 3. 验证结果
node ../siyuan-skill/siyuan.js wiki-ingest-history --limit 5
```

### 方式 B：从标准输入摄入

```bash
# 使用管道传入内容
echo "这里是文章内容..." | node ../siyuan-skill/siyuan.js wiki-ingest \
  --file - \
  --title "文本标题"

# 或从其他命令管道
cat article.md | node ../siyuan-skill/siyuan.js wiki-ingest --file - --title "文章标题"
```

> 注：`--file -` 表示从标准输入读取内容

### 幂等性验证

重复执行相同命令，第二次应返回：
```json
{
  "status": "deduplicated",
  "message": "该内容已处理，使用 --force 强制重新处理"
}
```

---

## 场景二：查询知识库（Query）

```bash
# 1. 找到实体页 docId
node ../siyuan-skill/siyuan.js search "RAG"

# 2. 查询实体关系
node ../siyuan-skill/siyuan.js graph-traverse <entityDocId>

# 3. 顺着关系继续探索
node ../siyuan-skill/siyuan.js graph-traverse <relatedDocId>
```

---

## 场景三：质量检查（Lint）

```bash
# 检测矛盾
node ../siyuan-skill/siyuan.js contradiction-detect

# 查看矛盾列表
node ../siyuan-skill/siyuan.js contradiction-list

# 检查单页质量
node ../siyuan-skill/siyuan.js quality-check <docId>
```

---

## 关键概念

### 链接格式（重要）

```
✅ 正确：((<ENTITY_DOC_ID> 'RAG'))
❌ 错误：((RAG))           ← 缺少 docId
❌ 错误：[[RAG]]           ← 这是 Obsidian 格式
```

**为什么**：思源笔记使用 ID 寻址，改名不会断链。

### 状态管理

```bash
# 查看摄入状态
node ../siyuan-skill/siyuan.js state-list

# 查看单个 ingestion 详情
node ../siyuan-skill/siyuan.js state-show <ingestion-id>

# 重置状态（用于修复）
node ../siyuan-skill/siyuan.js state-reset <ingestion-id>
```

---

## 下一步

- **详细 Ingest 流程**：见 [ingest-guide.md](./ingest-guide.md)
- **Query 查询模式**：见 [query-patterns.md](./query-patterns.md)
- **故障排除**：见 [troubleshooting.md](./troubleshooting.md)
