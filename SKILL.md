---
name: "llm-wiki"
description: "基于思源笔记的 LLM Wiki 知识库工作流。支持全自动摄入、查询知识图谱、质量检查、矛盾检测。依赖 siyuan-skill。触发词：整理笔记、处理这篇文章、知识库查询、检查知识质量、摄入文档。"
license: "MIT"
compatibility: "requires siyuan-skill, node, python3"
metadata:
  author: dazexcl
  version: 1.0.0
  title: LLM Wiki
  description_zh: 基于思源笔记的 LLM 知识库工作流
---

# LLM Wiki Skill

> 让 LLM 持续维护你的结构化知识库。
>
> **不是 RAG，而是 Wiki**：LLM 主动构建和维护知识库，每次摄入都更新相关页面、建立交叉链接、发现矛盾。

---

## 前置条件

- [思源笔记](https://b3log.org/siyuan/) 已安装并运行
- [Claude Code](https://claude.ai/code) 已安装
- [siyuan-skill](https://github.com/dazexcl/siyuan-skill) 已配置

## 初始化

首次使用前，运行初始化脚本创建知识库结构：

```bash
# 先安装 siyuan-skill，然后初始化 LLM Wiki
node wiki-init.js

# 或指定 siyuan-skill 路径
node wiki-init.js --skill-path /path/to/siyuan-skill/siyuan.js

# 预览模式（不实际创建）
node wiki-init.js --dry-run
```

初始化完成后，所有文档 ID 记录在 `wiki.config.json` 中。

## 快速开始

### 全自动摄入（推荐）

```
/wiki <docId>
```

全自动执行，无需确认。完成后报告：新建实体、更新索引、检测矛盾。

**只有以下情况才打断你**：文档无法读取、检测到矛盾、实体 >15 个、API 连续失败。

### 交互式摄入

```
/wiki ingest <docId> -i
```

适用于复杂文档或首次学习知识库结构。每步确认：提取实体 → 冲突检测 → 创建 → 更新索引。

---

## 命令索引

### 知识摄入

| 命令 | 用途 |
|------|------|
| `/wiki <docId>` | 一键摄入（全自动） |
| `/wiki ingest <docId> -i` | 交互式摄入 |
| `wiki-ingest --file <path>` | 从文件摄入 |
| `wiki-ingest-history` | 查看摄入历史 |

### 知识查询

| 命令 | 用途 |
|------|------|
| `graph-traverse <docId>` | 遍历知识图谱关系 |
| `verify-refs <docId>` | 验证双链正确性 |
| `search <query>` | 搜索知识库内容 |

### 质量检查

| 命令 | 用途 |
|------|------|
| `contradiction-detect` | 检测内容矛盾 |
| `quality-check <docId>` | 检查文档质量 |

---

## 核心理念

### 链接格式（重要）

```
✅ 正确：((<docId> '显示标题'))
❌ 错误：((RAG))           ← 缺少 docId，改名会断链
❌ 错误：[[RAG]]           ← Obsidian 格式
❌ 错误：<docId>            ← 裸 docId（残留文本块）
```

### Index 更新规则

**禁止 prepend**：新内容不能插入到页面顶部，必须合并到已有分类中。

**标准分类（8 类）**：笔记方法论、人物、LLM/Agent 技术、向量数据库、技术概念、投资/金融、工具、系统/概念

新增分类规则：新领域内容 ≥5 个实体且不匹配任何已有分类时，才可新增。

### 命令选择规则（重要）

> **选错命令会导致结构混乱**，必须严格按照下表选择：

| 文档类型 | 更新方式 | 命令 | 原因 |
|---------|---------|------|------|
| **index** | 重写整页 | `update` | 需要合并到已有分类，禁止 prepend |
| **log** | 重写整页 | `update` | 保持格式统一，避免裸 docId |
| **实体页** | 追加块 | `bi` | 块级追加新描述 |
| **主题页** | 追加块 | `bi` | 追加相关实体链接 |

**禁止操作**：
- ❌ 用 `bi` 更新 index/log → 导致 prepend 和裸 docId
- ❌ 用 `update` 更新实体页 → 覆盖已有描述

---

## 四层元架构

基于阳志平元反思技巧，提供四层保护：

| Layer | 机制 | 脚本 |
|-------|------|------|
| 认知边界 | 实体约束、元反思 | `entity_check.py`, `meta_reflect.py` |
| 意图防护 | 三重防护、兜底策略 | `triple_protection.py` |
| 执行可靠 | 后置验证、幂等性 | `validate_ingest.py` |
| 持续优化 | 同类扫描、模式积累 | `similar_scan.py`, `pattern_accumulate.py` |

详见 [references/architecture.md](./references/architecture.md)。

---

## 与 siyuan-skill 的分工

| 需求 | 使用 |
|------|------|
| 知识库工作流（摄入、查询、检查） | **llm-wiki**（本 skill） |
| 底层文档操作（CRUD） | [siyuan-skill](https://github.com/dazexcl/siyuan-skill) |

---

## 详细文档

| 文档 | 内容 |
|------|------|
| [auto-mode.md](./references/auto-mode.md) | 全自动模式详解：执行逻辑、异常处理、输出格式 |
| [architecture.md](./references/architecture.md) | 四层元架构详解：每层机制和脚本工具 |
| [ingest-guide.md](./references/ingest-guide.md) | 摄入流程详细说明 |
| [commands.md](./references/commands.md) | 所有命令参数详解 |
| [query-patterns.md](./references/query-patterns.md) | 知识图谱查询模式 |
| [troubleshooting.md](./references/troubleshooting.md) | 故障排除指南 |

---

## 故障排除速查

| 问题 | 解决方案 |
|------|----------|
| 重复摄入相同内容 | `state-reset <id>` 后重试 |
| Ingest 中断 | 直接重新执行，自动续传 |
| 残留文本块 | `python scripts/validate_ingest.py --doc-id <id>` |
| 链接格式错误 | `python scripts/similar_scan.py --type invalid_link` |
| 初始化失败 | 检查思源笔记 API 连通性和 siyuan-skill 路径 |
