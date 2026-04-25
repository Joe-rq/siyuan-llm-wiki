# LLM Wiki 命令参考

> 本文档包含 siyuan-skill 命令的详细参数说明。SKILL.md 中只保留核心用法，详细信息请参考此处。

---

## 目录

### 核心工作流命令

1. [wiki-ingest](#wiki-ingest) - 摄入文章到知识库（幂等性）
2. [wiki-ingest-history](#wiki-ingest-history) - 查看摄入历史记录
3. [state-list](#state-list) - 查看所有摄入状态
4. [state-show](#state-show) - 查看单个摄入详情
5. [state-reset](#state-reset) - 重置摄入状态

### 知识查询命令

6. [graph-traverse](#graph-traverse) - 图谱遍历
7. [verify-refs](#verify-refs) - 链接验证

### 审核工作流命令

8. [review-list](#review-list) - 审核列表
9. [review-action](#review-action) - 审核操作
10. [review-stats](#review-stats) - 审核统计

### 矛盾检测命令

11. [contradiction-detect](#contradiction-detect) - 矛盾检测
12. [contradiction-list](#contradiction-list) - 矛盾列表
13. [contradiction-resolve](#contradiction-resolve) - 解决矛盾

### 质量与批量命令

14. [quality-check](#quality-check) - 质量检查
15. [quality-gate](#quality-gate) - 质量门禁
16. [batch](#batch) - 批量操作

---

## wiki-ingest

摄入文章/文档到知识库。支持幂等性（相同内容多次执行不重复创建）。

### 语法

```bash
node ../siyuan-skill/siyuan.js wiki-ingest --file <path> --title <title> [options]
```

### 选项

| 选项 | 简写 | 说明 | 必需 |
|------|------|------|------|
| `--file <path>` | `-f` | 要摄入的文件路径 | 是 |
| `--title <title>` | `-t` | 文章标题 | 是 |
| `--identifier <id>` | `-i` | 来源标识符（URL/文件名） | 否 |
| `--force` | 无 | 强制重新处理（忽略幂等性） | 否 |
| `--notebook <id>` | 无 | 指定目标笔记本ID | 否 |

### 幂等性机制

```
内容 → 计算哈希 → 检查状态 → 已处理则跳过/未处理则执行 → 记录状态
```

| 状态 | 行为 |
|------|------|
| 首次执行 | 完整执行并记录状态 |
| 重复执行 | 返回 `deduplicated`，不创建重复数据 |
| `--force` | 无视状态，强制重新处理 |

### 示例

```bash
# 基本用法
node ../siyuan-skill/siyuan.js wiki-ingest --file article.md --title "文章标题"

# 带来源标识
node ../siyuan-skill/siyuan.js wiki-ingest --file article.md --title "文章标题" --identifier "https://example.com/article"

# 强制重新处理
node ../siyuan-skill/siyuan.js wiki-ingest --file article.md --title "文章标题" --force
```

### 返回值

```json
{
  "success": true,
  "data": {
    "ingestionId": "ingest_abc123",
    "status": "completed",
    "sourceDocId": "<SOURCE_DOC_ID>",
    "entitiesUpdated": ["RAG", "知识图谱"],
    "entitiesCreated": ["新实体"]
  }
}
```

### 执行流程

1. **计算哈希**：`sha256(content + title + identifier)`
2. **检查状态**：查看是否已处理过相同内容
3. **生成计划**：创建源文档、更新实体页、更新 index、追加 log
4. **执行操作**：逐条执行并实时更新状态
5. **完成记录**：保存最终状态和产出物ID

---

## wiki-ingest-history

查看知识库摄入历史记录。

### 语法

```bash
node ../siyuan-skill/siyuan.js wiki-ingest-history [options]
```

### 选项

| 选项 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--limit <n>` | `-n` | 限制返回数量 | 10 |
| `--status <status>` | 无 | 按状态过滤 | 无 |
| `--format <format>` | 无 | 输出格式：json/table | table |

### 状态值

| 状态 | 说明 |
|------|------|
| `completed` | 已完成 |
| `deduplicated` | 已去重（重复内容） |
| `running` | 执行中 |
| `partial` | 部分成功 |
| `failed` | 失败 |

### 示例

```bash
# 查看最近10条
node ../siyuan-skill/siyuan.js wiki-ingest-history

# 查看最近5条
node ../siyuan-skill/siyuan.js wiki-ingest-history --limit 5

# 只查失败的
node ../siyuan-skill/siyuan.js wiki-ingest-history --status failed

# JSON格式输出
node ../siyuan-skill/siyuan.js wiki-ingest-history --format json
```

---

## state-list

查看所有摄入状态。

### 语法

```bash
node ../siyuan-skill/siyuan.js state-list [options]
```

### 选项

| 选项 | 说明 |
|------|------|
| `--status <status>` | 按状态过滤 |
| `--since <date>` | 起始日期（ISO格式） |

### 示例

```bash
# 列出所有状态
node ../siyuan-skill/siyuan.js state-list

# 只看失败的
node ../siyuan-skill/siyuan.js state-list --status failed

# 查看最近7天的
node ../siyuan-skill/siyuan.js state-list --since 2026-04-01
```

---

## state-show

查看单个摄入详情。

### 语法

```bash
node ../siyuan-skill/siyuan.js state-show <ingestion-id>
```

### 参数

| 参数 | 说明 |
|------|------|
| `ingestion-id` | 摄入ID（从 state-list 或 wiki-ingest 输出获取） |

### 示例

```bash
node ../siyuan-skill/siyuan.js state-show ingest_abc123
```

### 返回值

```json
{
  "ingestionId": "ingest_abc123",
  "status": "completed",
  "contentHash": "sha256:abc...",
  "title": "文章标题",
  "identifier": "https://example.com/article",
  "createdAt": "2026-04-07T10:30:00Z",
  "completedAt": "2026-04-07T10:30:05Z",
  "outputs": {
    "sourceDocId": "<SOURCE_DOC_ID>",
    "entityUpdates": [...]
  },
  "error": null
}
```

---

## state-reset

重置摄入状态（故障恢复用）。

### 语法

```bash
node ../siyuan-skill/siyuan.js state-reset <ingestion-id> [options]
```

### 参数

| 参数 | 说明 |
|------|------|
| `ingestion-id` | 要重置的摄入ID |

### 选项

| 选项 | 说明 |
|------|------|
| `--hard` | 硬重置（删除状态文件，下次视为全新） |

### 使用场景

| 场景 | 命令 |
|------|------|
| 状态卡在 running | `state-reset <id>` 后重新执行 |
| 需要彻底重新处理 | `state-reset <id> --hard` 后执行 `--force` |

### 示例

```bash
# 软重置（状态变为 pending，可重新执行）
node ../siyuan-skill/siyuan.js state-reset ingest_abc123

# 硬重置（彻底删除状态）
node ../siyuan-skill/siyuan.js state-reset ingest_abc123 --hard
```

---

## graph-traverse

遍历图谱关系（基于 refs 表 SQL 查询）。

### 语法

```bash
node ../siyuan-skill/siyuan.js graph-traverse <blockId> [options]
```

### 选项

| 选项 | 简写 | 说明 |
|------|------|------|
| `--inbound` | `-i` | 查询入链（谁引用了这个块） |
| `--outbound` | `-o` | 查询出链（这个块引用了谁） |
| `--neighbors` | `-n` | 获取 1-hop 邻居（默认） |
| `--format` | `-f` | 输出格式：json（默认）/ markdown |

### 示例

```bash
# 查询实体 RAG 的所有图谱关系
node ../siyuan-skill/siyuan.js graph-traverse <ENTITY_DOC_ID>

# 只查入链，Markdown 格式输出
node ../siyuan-skill/siyuan.js graph-traverse <ENTITY_DOC_ID> --inbound --format markdown

# 只查出链
node ../siyuan-skill/siyuan.js graph-traverse <ENTITY_DOC_ID> --outbound
```

### 返回值

```json
{
  "success": true,
  "data": {
    "blockId": "<ENTITY_DOC_ID>",
    "inbound": [
      { "block_id": "xxx", "content": "...", "path": "/wiki/entities/...", "type": "d" }
    ],
    "outbound": [
      { "def_block_id": "yyy", "content": "...", "path": "/wiki/sources/...", "type": "d" }
    ]
  }
}
```

---

## verify-refs

验证块的 refs 关系是否正确写入图谱。

### 语法

```bash
node ../siyuan-skill/siyuan.js verify-refs <blockId> [options]
```

### 选项

| 选项 | 说明 |
|------|------|
| `--recursive` | 递归验证文档下所有块 |

### 示例

```bash
# 验证单个块
node ../siyuan-skill/siyuan.js verify-refs <ENTITY_DOC_ID>

# 递归验证文档
node ../siyuan-skill/siyuan.js verify-refs <ENTITIES_DIR_ID> --recursive
```

### 返回值

```json
{
  "success": true,
  "data": {
    "blockId": "<ENTITY_DOC_ID>",
    "declaredLinks": 3,
    "actualRefs": 3,
    "missing": [],
    "status": "valid"
  }
}
```

---

## quality-check

检查文档质量。

### 语法

```bash
node ../siyuan-skill/siyuan.js quality-check <docId> [options]
```

### 选项

| 选项 | 说明 |
|------|------|
| `--detail` | 显示详细维度得分 |

### 质量维度

| 维度 | 权重 | 评估标准 |
|------|------|----------|
| informationDensity | 30% | 字数 ≥500(满分), ≥200(良好), <50(不及格) |
| sourceTraceability | 30% | 使用 `((docId '标题'))` 双链引用来源 |
| refsVerification | 15% | 文本中的链接是否真正写入 refs 表 |
| crossSourceJudgment | 15% | synthesis 页面需有对比分析和结论 |
| formatCompliance | 10% | 无伪链接，思源格式正确 |

### 示例

```bash
# 基础检查
node ../siyuan-skill/siyuan.js quality-check <ENTITY_DOC_ID>

# 详细输出
node ../siyuan-skill/siyuan.js quality-check <ENTITY_DOC_ID> --detail
```

### 返回值

```json
{
  "success": true,
  "data": {
    "totalScore": 75,
    "percentage": 75,
    "passed": true,
    "dimensions": {
      "informationDensity": { "score": 25, "max": 30 },
      "sourceTraceability": { "score": 30, "max": 30 },
      "refsVerification": { "score": 15, "max": 15 },
      "crossSourceJudgment": { "score": 5, "max": 15 },
      "formatCompliance": { "score": 10, "max": 10 }
    },
    "recommendations": ["建议增加跨源判断"]
  }
}
```

---

## review-action

对待审核内容执行操作。

### 语法

```bash
node ../siyuan-skill/siyuan.js review-action <blockId> <action> [options]
node ../siyuan-skill/siyuan.js review-action --ids id1,id2,id3 <action> [options]
node ../siyuan-skill/siyuan.js review-action --auto-approve
```

### 操作类型

| 操作 | 说明 |
|------|------|
| `approve` | 通过审核 |
| `reject` | 拒绝（会添加拒绝标记） |
| `flag` | 标记需关注 |

### 选项

| 选项 | 说明 |
|------|------|
| `--reason <text>` | 添加审核原因 |
| `--ids id1,id2,id3` | 批量操作指定 ID |
| `--auto-approve` | 自动通过高置信度内容 |

### 高置信度判断标准

- 有 2 个及以上双链引用（来源明确）：+30 分
- 内容长度适中（100-2000 字）：+10 分
- 无矛盾标记（⚠️、矛盾、冲突）：+10 分
- 有结构化内容（标题、列表）：+10 分
- **阈值**：≥70 分且无风险因素

### 示例

```bash
# 单个通过
node ../siyuan-skill/siyuan.js review-action <ENTITY_DOC_ID> approve --reason "信息准确"

# 批量通过
node ../siyuan-skill/siyuan.js review-action --ids id1,id2,id3 approve

# 自动通过高置信度
node ../siyuan-skill/siyuan.js review-action --auto-approve
```

---

## review-list

列出待审核内容。

### 语法

```bash
node ../siyuan-skill/siyuan.js review-list [options]
```

### 选项

| 选项 | 说明 |
|------|------|
| `--detail` | 显示内容摘要 |
| `--limit <n>` | 限制返回数量 |
| `--status <status>` | 按状态过滤：pending_review/approved/rejected/flagged |

---

## review-stats

查看审核统计。

### 语法

```bash
node ../siyuan-skill/siyuan.js review-stats [options]
```

### 选项

| 选项 | 说明 |
|------|------|
| `--period <days>` | 统计最近 N 天 |

---

## contradiction-detect

检测内容矛盾。

### 语法

```bash
node ../siyuan-skill/siyuan.js contradiction-detect [options]
```

### 选项

| 选项 | 说明 |
|------|------|
| `--period <hours>` | 检测最近 N 小时变动（默认 24） |
| `--entity <docId>` | 检测特定实体 |
| `--notebook <id>` | 指定笔记本 |

### 矛盾类型

| 类型 | 说明 |
|------|------|
| `numerical_discrepancy` | 数值不一致（年份、数量、百分比） |
| `temporal_conflict` | 时间线冲突 |
| `attribution_mismatch` | 归属不一致 |

---

## contradiction-list

列出检测到的矛盾。

### 语法

```bash
node ../siyuan-skill/siyuan.js contradiction-list [options]
```

### 选项

| 选项 | 说明 |
|------|------|
| `--detail` | 显示详细信息 |
| `--status <status>` | 按状态过滤：pending/resolved/invalid/superseded |
| `--severity <level>` | 按严重程度过滤：high/medium/low |

---

## contradiction-resolve

解决矛盾。

### 语法

```bash
node ../siyuan-skill/siyuan.js contradiction-resolve <entityId> <contradictionId> <status> [--reason <text>]
```

### 状态

| 状态 | 说明 |
|------|------|
| `resolved` | 已解决 |
| `invalid` | 无效矛盾（误报） |
| `superseded` | 被新信息取代 |

---

## batch

批量执行操作。

### 语法

```bash
node ../siyuan-skill/siyuan.js batch --file ops.json [options]
```

### 选项

| 选项 | 说明 |
|------|------|
| `--file <path>` | 操作文件路径 |
| `--review-mode` | 标记为 pending_review 状态 |
| `--verify-refs` | 操作后自动验证 refs |

### 操作文件格式

```json
[
  {
    "action": "create",
    "path": "LLM-Wiki/wiki/entities/实体名",
    "content": "内容..."
  },
  {
    "action": "bi",
    "targetId": "docId",
    "content": "追加块内容..."
  }
]
```

---

## quality-gate

入库前质量拦截。

### 语法

```bash
node ../siyuan-skill/siyuan.js quality-gate --file ops.json [options]
```

### 选项

| 选项 | 说明 |
|------|------|
| `--preview` | 预览模式（不拦截，仅生成报告） |
| `--strict` | 严格模式（通过门槛 70 分） |

### 通过标准

| 模式 | 门槛 |
|------|------|
| 普通 | ≥60 分 |
| 严格 | ≥70 分 |

### 质量等级

| 等级 | 分数 | 含义 |
|------|------|------|
| A | ≥80 | 优秀，可直接入库 |
| B | 60-79 | 良好，建议微调后入库 |
| C | 40-59 | 及格，需要改进 |
| D | <40 | 不及格，禁止入库 |
