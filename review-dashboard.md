# QA Review Dashboard (待审批知识库)

> 这里汇总了所有由 AI 抓取或大模型提取的、尚未核验的知识库块记录。确认正确后，请移除块的 `custom-ai-status` 属性以允许其正式入库。

## Pending Reviews 待评估列表 ⚠️

{{ SELECT * FROM blocks WHERE ial like '%custom-ai-status="pending_review"%' ORDER BY updated DESC }}

---

**使用指南**
1. 每天扫一眼上述嵌入块区域的变动
2. 大模型刚插入的内容会有明显被引用的痕迹，可前往原始页面查看整段上下文。
3. 若有错误，直接修改文本，然后右键清除自定义属性中的 `ai-status`。
4. 若正确，同样右键属性或者调用 `siyuan-skill` 将属性置空：
```bash
node ../siyuan-skill/siyuan.js block-attrs <blockId> --remove "custom-ai-status"
```
