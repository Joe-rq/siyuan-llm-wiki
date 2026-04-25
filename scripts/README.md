# LLM Wiki 脚本工具

四层元架构的可执行实现。

---

## 快速开始

```bash
# 1. 检查实体约束（超限自动拆分）
python scripts/entity_check.py --items "文章1,文章2,文章3,文章4,文章5"

# 2. 元反思检查点
python scripts/meta_reflect.py --task "ingest文章"

# 3. 三重防护执行
python scripts/triple_protection.py --demo

# 4. 后置验证
python scripts/validate_ingest.py

# 5. 对齐验证
python scripts/alignment_verify.py -r "需求1;需求2;需求3" -i "实现1;实现2"

# 6. 同类扫描
python scripts/similar_scan.py --type invalid_link

# 7. 模式积累
python scripts/pattern_accumulate.py --name "新模式" --problem "问题" --solution "方案"
```

---

## 脚本索引

### Layer 1: 认知边界层

| 脚本 | 功能 | 使用场景 |
|------|------|----------|
| `entity_check.py` | 实体约束检查 | 单次处理 >4 个实体时 |
| `meta_reflect.py` | 元反思检查点 | 关键操作后强制反思 |

### Layer 2: 意图防护层

| 脚本 | 功能 | 使用场景 |
|------|------|----------|
| `triple_protection.py` | 三重防护执行 | 关键写入操作 |

### Layer 3: 执行可靠层

| 脚本 | 功能 | 使用场景 |
|------|------|----------|
| `validate_ingest.py` | 后置验证 | 每次写入后检查 |
| `alignment_verify.py` | 对齐验证 | 对照需求检查实现 |

### Layer 4: 持续优化层

| 脚本 | 功能 | 使用场景 |
|------|------|----------|
| `similar_scan.py` | 同类扫描 | 发现新问题后全库检查 |
| `pattern_accumulate.py` | 模式积累 | 记录新发现的问题 |

---

## 详细说明

### entity_check.py

```bash
# 检查并自动拆分
python entity_check.py --items "a,b,c,d,e"

# 输出 JSON
python entity_check.py --items "a,b,c,d,e" --json
```

### validate_ingest.py

```bash
# 验证所有核心文档
python validate_ingest.py

# 验证特定文档
python validate_ingest.py --doc-id <INDEX_DOC_ID>

# 验证特定类型
python validate_ingest.py --doc-id <id> --type log
```

### pattern_accumulate.py

```bash
# 保存新模式
python pattern_accumulate.py \
  --name "bi命令陷阱" \
  --problem "使用bi插入链接列表时出现残留文本块" \
  --solution "改用update重写" \
  --category "思源操作"

# 列出所有模式
python pattern_accumulate.py --list

# 搜索模式
python pattern_accumulate.py --search "链接"
```

---

## 集成到工作流

### Ingest 工作流

```bash
# 1. 实体约束检查
python scripts/entity_check.py --items "文章1,文章2,...,文章8"
# → 拆分为 2 批

# 2. 处理每批
for batch in batches:
    # 元反思检查点
    python scripts/meta_reflect.py --template

    # 三重防护执行
    python scripts/triple_protection.py --content "..."

    # 后置验证
    python scripts/validate_ingest.py --doc-id <id>

# 3. 同类扫描
python scripts/similar_scan.py --type all

# 4. 模式积累
python scripts/pattern_accumulate.py --name "..." --problem "..." --solution "..."
```

---

## 模式库位置

`memory/patterns.md` - 记录已知问题和最佳实践
