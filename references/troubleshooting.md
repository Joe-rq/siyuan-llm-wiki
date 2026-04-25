# 故障排除

> 常见问题及恢复方法

---

## Ingest 问题

### 问题：重复创建相同内容

**症状**：相同内容出现多个文档

**原因**：
1. 未使用 wiki-ingest，直接使用 batch
2. 状态文件损坏或被删除
3. 强制重跑后未清理旧文档

**解决**：
```bash
# 1. 删除重复文档
node ../siyuan-skill/siyuan.js delete <duplicateDocId>

# 2. 重置状态
node ../siyuan-skill/siyuan.js state-reset <ingestion-id>

# 3. 重新执行
node ../siyuan-skill/siyuan.js wiki-ingest --file article.md --title "标题"
```

**预防**：始终使用 wiki-ingest，不直接使用 batch

---

### 问题：Ingest 中断后无法续传

**症状**：状态为 running 或 partial，重新执行报错

**解决**：
```bash
# 查看当前状态
node ../siyuan-skill/siyuan.js state-show <ingestion-id>

# 方法1：直接重试（幂等，自动跳过已完成的）
node ../siyuan-skill/siyuan.js wiki-ingest --file article.md --title "标题"

# 方法2：强制重置后重试
node ../siyuan-skill/siyuan.js state-reset <ingestion-id>
node ../siyuan-skill/siyuan.js wiki-ingest --file article.md --title "标题"
```

---

### 问题：状态文件损坏

**症状**：state-show 报错 "状态文件损坏"

**解决**：
```bash
# 删除损坏的状态文件
rm .claude/skills/siyuan-skill/state/ingestions/<hash>.json

# 重新执行（视为新任务）
node ../siyuan-skill/siyuan.js wiki-ingest --file article.md --title "标题"
```

---

## Query 问题

### 问题：查询不到预期结果

**症状**：graph-traverse 返回空或结果不完整

**排查**：
```bash
# 1. 确认实体页存在
node ../siyuan-skill/siyuan.js search "实体名"

# 2. 确认有文档引用该实体（入链）
node ../siyuan-skill/siyuan.js graph-traverse <entityId> --inbound

# 3. 确认链接格式正确
# 必须是 ((docId '标题'))，不是 [[标题]] 或 ((标题))
```

**解决**：修正链接格式，重新执行 verify-refs

---

## 状态管理问题

### 问题：状态目录占用空间过大

**解决**：
```bash
# 查看状态目录大小
du -sh .claude/skills/siyuan-skill/state/

# 清理 completed 超过 30 天的状态（手动）
find .claude/skills/siyuan-skill/state/ingestions/ \
  -name "*.json" -mtime +30 -delete
```

**注意**：不要删除 running/partial 的状态

---

### 问题：并发执行导致状态损坏

**症状**：同时运行两个 wiki-ingest，状态异常

**原因**：文件锁超时或进程崩溃未释放锁

**解决**：
```bash
# 1. 删除残留的锁文件
rm .claude/skills/siyuan-skill/state/ingestions/.*.lock

# 2. 重置受影响的状态
node ../siyuan-skill/siyuan.js state-reset <ingestion-id>

# 3. 避免并发：串行执行 wiki-ingest
```

---

## 通用恢复流程

### 终极重置：从头开始

如果状态完全混乱，可以彻底重置：

```bash
# 1. 备份现有状态（可选）
cp -r .claude/skills/siyuan-skill/state/ \
  .claude/skills/siyuan-skill/state-backup-$(date +%Y%m%d)/

# 2. 删除所有状态
rm -rf .claude/skills/siyuan-skill/state/ingestions/*

# 3. 重新执行所有任务
# 注意：已处理的内容会重新处理
```

---

## 获取帮助

如果以上方法无法解决：

1. 查看详细日志：`cat .claude/skills/siyuan-skill/state/ingestions/<hash>.json`
2. 检查思源笔记 API 是否正常：`node ../siyuan-skill/siyuan.js notebooks`
3. 查看命令帮助：`node ../siyuan-skill/siyuan.js <command> --help`
