# LLM Wiki

<p align="center">
<img src="https://img.shields.io/badge/Powered%20by-Siyuan-6B6DFF?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjQgMjQiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEyIDJMMiA3djEwbDEwIDUgMTAtNVY3TDEyIDJ6IiBmaWxsPSIjNkI2REZGIi8+PC9zdmc+&logoColor=white" alt="Siyuan Notes">
<img src="https://img.shields.io/badge/Agent-Claude%20Code-FF6B35?style=for-the-badge" alt="Claude Code">
<img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License">
</p>

> 让 LLM 持续维护你的结构化知识库。
>
> **不是 RAG，而是 Wiki**：LLM 主动构建和维护知识库，每次摄入都更新相关页面、建立交叉链接、发现矛盾。知识编译一次，持续更新。

## 为什么用思源笔记？

| 特性 | 思源 | Obsidian |
|------|------|----------|
| 数据模型 | 块（block）为单位，可精确操作 | 文件为单位，改一段=重写整文件 |
| 双链存储 | refs 表（SQL 可查） | 解析文本得到（每次重新计算） |
| API | 原生设计，所有操作可用 | 插件 API，主要面向插件生态 |
| LLM 协作 | 可追加/修改特定块 | 只能生成整篇 markdown |

**核心价值**：思源让 LLM 真正成为知识库的"编辑"，而不是文档生成器。

## 安装

### 前置条件

- [思源笔记](https://b3log.org/siyuan/) 已安装并运行
- [Claude Code](https://claude.ai/code) 已安装
- [siyuan-skill](https://github.com/dazexcl/siyuan-skill) 已安装

### 步骤

```bash
# 1. 克隆本项目到 Claude Code 的 skills 目录
cd ~/.claude/skills/
git clone https://github.com/dazexcl/llm-wiki.git

# 2. 初始化知识库（创建笔记本、目录结构、核心文档）
cd llm-wiki
node wiki-init.js

# 3. 验证
node wiki-init.js --dry-run  # 预览模式
```

初始化完成后，`wiki.config.json` 会记录所有文档 ID，脚本运行时自动读取。

### 已有笔记本？

如果你已经有一个 LLM-Wiki 笔记本，可以直接编辑 `wiki.config.json`：

```bash
cp config.example.json wiki.config.json
# 编辑 wiki.config.json，填入你的笔记本和文档 ID
```

## 四大核心操作

### 1. Ingest（摄入）

```
/wiki <docId>
```

全自动执行：读取 → 摘要 → 提取实体 → 冲突检测 → 创建/更新 → 更新索引 → 追加日志。

交互模式：`/wiki ingest <docId> -i`（每步确认）

### 2. Query（图谱查询）

```
用户：RAG 和 GraphRAG 有什么关系？

LLM：
  1. 搜索定位 RAG 实体页
  2. 查询 refs 表，找到关联文档
  3. 遍历图谱，找到 GraphRAG
  4. 综合回答，标注来源链接
```

### 3. Lint（健康检查）

```
检查结果：
❌ 孤立实体：某实体（无入链）
❌ 伪链接残留：[[知识管理]] 应改为 ((docId '知识管理'))
⚠️ 缺失来源页
```

### 4. 审核工作流

```bash
# 查看待审核内容
review-list

# 单个通过
review-action <blockId> approve

# 批量通过高置信度内容
review-action --auto-approve
```

## 知识库结构

```
LLM-Wiki/
├── index.md              # 知识库入口，实体索引
├── log.md                # 变更日志
├── schema.md             # 工作流规范
├── raw/                  # 原始文档存档
└── wiki/
    ├── entities/         # 实体页（人物、概念、项目...）
    ├── topics/           # 主题页（跨实体综合）
    ├── sources/          # 来源摘要
    └── synthesis/        # 综合判断
```

## 最佳实践

### 链接格式

```markdown
✅ 正确：((<docId> '显示标题'))
❌ 错误：[[标题]]           ← Obsidian 格式
❌ 错误：((<docId> 标题))   ← 标题缺少单引号
```

### 块级操作优先

```bash
# 追加新信息（推荐）
bi <docId> "新内容块"

# 修改特定段落
bu <blockId> "更新内容"

# 重写整页（谨慎使用）
update <docId> "完整内容"
```

### 命令选择规则

| 文档类型 | 更新方式 | 命令 | 原因 |
|---------|---------|------|------|
| index | 重写整页 | `update` | 需要合并到已有分类，禁止 prepend |
| log | 重写整页 | `update` | 保持格式统一 |
| 实体页 | 追加块 | `bi` | 块级追加新描述 |
| 主题页 | 追加块 | `bi` | 追加相关实体链接 |

### 渐进式构建

1. 第一轮：快速摄入，创建基础结构
2. 第二轮：发现重复实体，合并
3. 第三轮：添加交叉链接
4. 第四轮：综合判断沉淀

## 四层元架构

| Layer | 机制 | 脚本 |
|-------|------|------|
| 认知边界 | 实体约束（≤4/次）、元反思 | `entity_check.py`, `meta_reflect.py` |
| 意图防护 | 三重防护、兜底策略 | `triple_protection.py` |
| 执行可靠 | 后置验证、幂等性 | `validate_ingest.py` |
| 持续优化 | 同类扫描、模式积累 | `similar_scan.py`, `pattern_accumulate.py` |

## 配置说明

`wiki.config.json`（由 wiki-init.js 生成，也可手动编辑）：

```json
{
  "notebook": { "id": "<NOTEBOOK_ID>", "name": "LLM-Wiki" },
  "docs": { "index": "<ID>", "log": "<ID>", "schema": "<ID>" },
  "dirs": {
    "raw": "<ID>", "wiki": "<ID>",
    "wiki_entities": "<ID>", "wiki_topics": "<ID>",
    "wiki_sources": "<ID>", "wiki_synthesis": "<ID>"
  },
  "siyuanSkillPath": "<path_to_siyuan_js>"
}
```

## 文档

| 文档 | 内容 |
|------|------|
| [SKILL.md](./SKILL.md) | 技能定义（Claude Code 入口） |
| [auto-mode.md](./references/auto-mode.md) | 全自动模式详解 |
| [architecture.md](./references/architecture.md) | 四层元架构详解 |
| [ingest-guide.md](./references/ingest-guide.md) | 摄入流程详细说明 |
| [commands.md](./references/commands.md) | 所有命令参数详解 |
| [query-patterns.md](./references/query-patterns.md) | 知识图谱查询模式 |
| [troubleshooting.md](./references/troubleshooting.md) | 故障排除指南 |

## 常见问题

### 初始化失败？

1. 确认思源笔记已启动：`node siyuan.js notebooks`
2. 确认 siyuan-skill 路径正确：`node wiki-init.js --skill-path /path/to/siyuan.js`
3. 使用 `--dry-run` 预览操作

### 如何迁移现有笔记？

1. 在思源创建 `raw/` 目录
2. 把现有笔记粘贴到 `raw/`
3. 对 Claude 说"帮我处理 raw/xxx.md"
4. Claude 会自动创建结构化版本

## License

MIT
