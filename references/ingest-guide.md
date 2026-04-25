# Ingest 详细指南

> 将文章/文档摄入知识库的完整流程

---

## 核心原则：幂等性

**什么是幂等性**：相同内容多次执行，结果不变，不产生重复数据。

**实现机制**：
1. 内容哈希计算 → ingestion ID
2. 状态检查 → 已处理则跳过
3. 操作记录 → 支持中断续传

---

## 预检阶段

### 1. 检查内容是否已处理

```bash
# 计算内容哈希（模拟）
# hash = sha256(content + title + identifier)

# 检查状态
node ../siyuan-skill/siyuan.js state-list | grep <expected-hash>
```

### 2. 决定执行策略

| 状态 | 行为 |
|-----|------|
| 不存在 | 全新执行 |
| completed | 返回已有结果（幂等） |
| failed/partial | 准备续传 |
| running | 等待或强制重置 |

---

## 执行阶段

### 方式一：wiki-ingest（推荐）

**执行步骤**：
1. 计算内容哈希
2. 检查状态 → 决定是否执行
3. 生成操作计划（创建源文档、更新实体、更新 index、追加 log）
4. 逐条执行操作
5. 实时更新状态

```bash
# 基本用法
node ../siyuan-skill/siyuan.js wiki-ingest --file article.md --title "标题"

# 高级选项
node ../siyuan-skill/siyuan.js wiki-ingest \
  --file article.md \
  --title "标题" \
  --identifier "来源URL" \
  --force  # 强制重新处理
```

### 方式二：手动 batch（高级）

适用于需要完全控制操作序列的场景。

```bash
# 1. 构造操作列表 ops.json
[
  {
    "action": "create",
    "path": "LLM-Wiki/wiki/sources/文档标题",
    "content": "摘要..."
  },
  {
    "action": "bi",
    "targetId": "2026xxxxxxxx-xxxxxxx",
    "content": "## 来自《来源》..."
  }
]

# 2. 执行（带状态管理）
node ../siyuan-skill/siyuan.js batch \
  --file ops.json \
  --state-aware \
  --content-hash <hash> \
  --resume
```

---

## 验证阶段

### 1. 验证产出物存在

```bash
# 检查源文档是否创建
node ../siyuan-skill/siyuan.js search "文档标题"

# 验证实体更新
node ../siyuan-skill/siyuan.js content <entityDocId>
```

### 2. 验证 refs 写入

```bash
# 验证链接真正写入图谱
node ../siyuan-skill/siyuan.js verify-refs <blockId>
```

### 3. 确认状态更新

```bash
# 状态应为 completed
node ../siyuan-skill/siyuan.js state-show <ingestion-id>
```

---

## 故障恢复

### 场景：Ingest 中断

```bash
# 1. 查看当前状态
node ../siyuan-skill/siyuan.js state-show <ingestion-id>
# 状态可能为：running, partial, failed

# 2. 自动续传（幂等，安全重试）
node ../siyuan-skill/siyuan.js wiki-ingest --file article.md --title "标题"

# 3. 或强制重置后重试
node ../siyuan-skill/siyuan.js state-reset <ingestion-id>
node ../siyuan-skill/siyuan.js wiki-ingest --file article.md --title "标题" --force
```

### 场景：重复创建

**症状**：相同内容出现多个文档

**修复**：
```bash
# 1. 手动删除重复文档（使用 siyuan-skill）
node ../siyuan-skill/siyuan.js delete <duplicateDocId>

# 2. 重置状态
node ../siyuan-skill/siyuan.js state-reset <ingestion-id>

# 3. 重新执行（使用 --force）
node ../siyuan-skill/siyuan.js wiki-ingest --file article.md --title "标题" --force
```

---

## 最佳实践

1. **始终使用 wiki-ingest**：内置幂等性，避免重复
2. **定期查看历史**：`wiki-ingest-history` 了解最近摄入
3. **及时处理失败**：failed 状态需要关注，partial 可自动续传
4. **保留来源信息**：使用 `--identifier` 记录原文 URL/文件名
