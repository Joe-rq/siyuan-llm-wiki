# 四层元架构详解

本 Skill 基于**阳志平元反思技巧**设计，提供四层保护。

```
┌─────────────────────────────────────────────────────────┐
│           LLM Wiki 四层架构                              │
├─────────────────────────────────────────────────────────┤
│ Layer 1: 认知边界层 → 元反思 + 实体约束 + 问题重构       │
│ Layer 2: 意图防护层 → 兜底 + 三重防护 + 自我校验         │
│ Layer 3: 执行可靠层 → 后置验证 + 完整性 + 对齐验证       │
│ Layer 4: 持续优化层 → 倍速测试 + 同类扫描 + 积累飞轮     │
└─────────────────────────────────────────────────────────┘
```

---

## Layer 1: 认知边界层

| 机制 | 脚本 | 作用 |
|------|------|------|
| 实体约束 | `entity_check.py` | 单次处理 ≤4 个实体，超限自动拆分 |
| 元反思 | `meta_reflect.py` | 关键操作后强制回答 6 个问题 |

**强制规则**：
- 文章 >4 篇？必须拆分批次
- 实体 >4 个？使用 TaskCreate 并行
- 每批处理后？触发元反思检查点

---

## Layer 2: 意图防护层

| 机制 | 脚本 | 作用 |
|------|------|------|
| 三重防护 | `triple_protection.py` | 输入验证 → 执行监控 → 输出验证 |
| 兜底策略 | 内置 | `bi` 失败时降级为 `update` |

**关键防护点**：
- 写入前：检查是否为裸 docId、链接格式是否正确
- 执行中：捕获异常，启用兜底
- 写入后：验证残留文本块

---

## Layer 3: 执行可靠层

| 机制 | 脚本 | 作用 |
|------|------|------|
| 后置验证 | `validate_ingest.py` | 检查残留文本块、格式合规性 |
| 对齐验证 | `alignment_verify.py` | 对照 schema 检查实现偏差 |
| 幂等性 | 内置 | 相同内容自动去重 |

---

## Layer 4: 持续优化层

| 机制 | 脚本 | 作用 |
|------|------|------|
| 同类扫描 | `similar_scan.py` | 发现新问题后全库扫描 |
| 模式积累 | `pattern_accumulate.py` | 记录已知陷阱到 memory/patterns.md |

---

## 脚本工具速查

```bash
# Layer 1: 认知边界
python scripts/entity_check.py --items "a,b,c,d,e"     # 实体约束检查
python scripts/meta_reflect.py --template              # 元反思检查点

# Layer 2: 意图防护
python scripts/triple_protection.py --demo             # 三重防护演示

# Layer 3: 执行可靠
python scripts/validate_ingest.py                      # 后置验证
python scripts/alignment_verify.py -r "需求" -i "实现" # 对齐验证

# Layer 4: 持续优化
python scripts/similar_scan.py --type invalid_link     # 同类扫描
python scripts/pattern_accumulate.py --list            # 查看模式库
```

详见 [scripts/README.md](../scripts/README.md)。
