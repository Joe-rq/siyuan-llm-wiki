# Query 查询模式

> 基于 GraphRAG 的知识库查询方法

---

## 核心原则

**真正的 GraphRAG 必须基于 refs 表 SQL 查询**，而非解析 Markdown 文本。

思源笔记的 refs 表记录了所有文档间的链接关系：
- `def_block_id`: 被引用的块/文档 ID
- `ref_block_id`: 引用的块/文档 ID
- `content`: 引用上下文

---

## 查询模式一：实体探索

### 场景：了解某个实体的所有信息

```bash
# 1. 定位实体页
node ../siyuan-skill/siyuan.js search "RAG"

# 2. 查询入链（哪些文档引用了这个实体）
node ../siyuan-skill/siyuan.js graph-traverse <entityDocId>

# 3. 顺着关系继续探索
# 查看引用文档的内容，找到更多相关实体
node ../siyuan-skill/siyuan.js content <relatedDocId>
```

### 输出示例

```markdown
## GraphRAG 查询路径

### Step 1: 定位起点实体
- 实体页：((<ENTITY_DOC_ID> 'RAG'))

### Step 2: 查询 refs 表
结果：3 条入链
- ((<SOURCE_DOC_ID> 'LLM Wiki Pattern'))
- ((<RELATED_DOC_ID> 'OB vs 思源双链对比'))
- ((<RELATED_ENTITY_ID> 'RAG 应用案例'))

### Step 3: 顺着链接爬行
从 'LLM Wiki Pattern' 中发现新实体：
- ((<GRAPH_ENTITY_ID> '知识图谱'))
- ((<VECTOR_ENTITY_ID> '向量检索'))

### Step 4: 综合回答
基于以上 5 个相关文档，RAG 的定义是...
来源标注：
- 定义来自：((<ENTITY_DOC_ID> 'RAG'))
- 应用场景来自：((<RELATED_ENTITY_ID> 'RAG 应用案例'))
```

---

## 查询模式二：关联发现

### 场景：发现两个实体之间的关系

```bash
# 1. 分别查询两个实体的入链
node ../siyuan-skill/siyuan.js graph-traverse <entityAId> --inbound
node ../siyuan-skill/siyuan.js graph-traverse <entityBId> --inbound

# 2. 人工对比找出共同引用
# （目前需手动对比两个结果集中的共同文档）
```

> 注：高级 SQL 查询功能需要直接使用思源 API。详见 [思源 API 文档](https://github.com/siyuan-note/siyuan/blob/master/API_zh_CN.md)。

---

## 查询模式三：路径探索

### 场景：从实体 A 到实体 B 的路径

```bash
# 1. 获取 A 的所有出链（A 引用了谁）
node ../siyuan-skill/siyuan.js graph-traverse <entityAId> --outbound

# 2. 获取 B 的所有入链（谁引用了 B）
node ../siyuan-skill/siyuan.js graph-traverse <entityBId> --inbound

# 3. 人工查找交集
# 对比 A 的 outbound 结果和 B 的 inbound 结果
# 共同出现的 docId 就是中间节点 C
# 路径为：A -> C -> B
```

---

## 查询模式四：时间线重建

### 场景：按时间顺序了解某个主题的发展

```bash
# 查询所有相关文档
# 1. 先获取实体的入链文档列表
node ../siyuan-skill/siyuan.js graph-traverse ${entityId} --inbound --format json

# 2. 逐个查看文档的创建时间（在思源笔记界面中查看）
# 或使用 siyuan-skill 的 info 命令获取文档元数据
node ../siyuan-skill/siyuan.js info ${docId}
```

> 注：复杂 SQL 查询需直接使用思源 API。详见 [思源 API 文档](https://github.com/siyuan-note/siyuan/blob/master/API_zh_CN.md)。

---

## 输出格式规范

### 必须包含

1. **查询路径**：展示如何从起点到达答案
2. **来源标注**：每个事实都标注来源 docId
3. **置信度**：说明信息的可靠程度

### 示例模板

```markdown
## 查询：张三参与过哪些项目？

### 查询路径
1. 搜索实体页 "张三" → ((2026xxxxxxxx-xxxxxxx '张三'))
2. 查询入链 → 发现 3 个来源文档
3. 遍历来源文档的 refs → 发现 5 个项目提及

### 结果
| 项目 | 角色 | 来源 |
|-----|------|-----|
| 项目A | 负责人 | ((2026xxx... '项目A总结')) |
| 项目B | 参与者 | ((2026xxx... '项目B复盘')) |

### 置信度
- 项目A：高（直接引用张三实体页）
- 项目B：中（在正文中提及，未直接链接）
```

---

## 常见错误

❌ **解析 Markdown 文本找链接**
```
错误：读取文档内容，正则匹配 [[xxx]] 或 ((xxx))
原因：文本中的链接不一定写入 refs 表
```

✅ **正确做法：始终查询 refs 表**
```
正确：SQL 查询 refs 表，获取真实的链接关系
```

---

## 最佳实践

1. **优先使用 graph-traverse**：封装了 refs 查询
2. **SQL 查询作为补充**：复杂关系场景使用
3. **记录查询路径**：回答中展示如何从起点到答案
4. **交叉验证**：多个来源确认的事实更可靠
