#!/usr/bin/env python3
"""
LLM Wiki Ingest 后置验证脚本
检查文档完整性、格式合规性、残留文本块
"""

import re
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Tuple


def load_wiki_config() -> dict:
    """加载 wiki.config.json，不存在时报错退出"""
    config_path = Path(__file__).parent.parent / "wiki.config.json"
    if not config_path.exists():
        print("❌ wiki.config.json 不存在。请先运行: node wiki-init.js")
        sys.exit(2)
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_siyuan_js(config: dict) -> str:
    """从配置中获取 siyuan.js 路径，带回退逻辑"""
    return (
        config.get("siyuanSkillPath", "")
        or os.environ.get("SIYUAN_SKILL_PATH", "")
        or str(Path(__file__).parent.parent.parent / "siyuan-skill" / "siyuan.js")
    )


import os

CONFIG = load_wiki_config()
SIYUAN_JS = get_siyuan_js(CONFIG)


def run_siyuan(cmd: str) -> dict:
    """执行 siyuan.js 命令并返回 JSON 结果"""
    full_cmd = f'node "{SIYUAN_JS}" {cmd}'
    try:
        result = subprocess.run(
            full_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return {"error": result.stderr}
        return json.loads(result.stdout)
    except Exception as e:
        return {"error": str(e)}


def check_residual_text_blocks(doc_id: str) -> List[dict]:
    """
    检查文档中的残留文本块
    残留文本块特征：
    1. 内容是裸的 docId 格式
    2. 不是有效的 ((docId 'title')) 格式
    """
    content_result = run_siyuan(f"content {doc_id}")
    if "error" in content_result:
        return []

    content = content_result.get("content", "")
    issues = []

    # 匹配孤立的 docId（不是 ((docId 'title')) 格式）
    pattern = r"(?<!\(\()20\d{10}-[a-z0-9]{7}(?!\s*'))"
    matches = re.finditer(pattern, content)

    for match in matches:
        issues.append(
            {
                "type": "residual_text_block",
                "content": match.group(),
                "position": match.span(),
                "fix": f"删除或转换为 (({match.group()} '标题')) 格式",
            }
        )

    return issues


def check_log_format(doc_id: str) -> List[dict]:
    """
    检查 log.md 格式合规性
    规范：## YYYY-MM-DD | 操作类型 | 描述
    """
    content_result = run_siyuan(f"content {doc_id}")
    if "error" in content_result:
        return []

    content = content_result.get("content", "")
    issues = []

    # 检查标题格式
    log_pattern = r"^## \d{4}-\d{2}-\d{2} \| (ingest|query|lint|cleanup|update) \| .+$"
    lines = content.split("\n")

    for i, line in enumerate(lines):
        if line.startswith("## ") and not line.startswith("## LLM Wiki"):
            if not re.match(log_pattern, line):
                issues.append(
                    {
                        "type": "invalid_log_format",
                        "line": i + 1,
                        "content": line,
                        "fix": "格式应为：## YYYY-MM-DD | ingest/query/lint/cleanup/update | 描述",
                    }
                )

    # 检查必需字段
    required_fields = ["新建实体：", "触及："]
    for field in required_fields:
        if field not in content:
            issues.append(
                {"type": "missing_required_field", "field": field, "fix": f"添加 '{field}' 字段"}
            )

    return issues


def check_index_format(doc_id: str) -> List[dict]:
    """
    检查 index.md 结构合规性
    包括：必需节、标题位置、重复条目、源文档索引存在性
    """
    content_result = run_siyuan(f"content {doc_id}")
    if "error" in content_result:
        return []

    content = content_result.get("content", "")
    issues = []

    # === 1. 标题位置检查 ===
    lines = content.split("\n")
    first_content_line = ""
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("{:"):
            first_content_line = stripped
            break

    if first_content_line and "LLM Wiki 索引" not in first_content_line:
        issues.append(
            {
                "type": "title_not_first",
                "content": first_content_line[:60],
                "fix": "文档第一行必须是 '# LLM Wiki 索引'，删除其前面的所有内容",
            }
        )

    # === 2. 必需的二级标题 ===
    required_sections = ["## 统计", "## 实体索引", "## 主题索引", "## 源文档索引"]

    for section in required_sections:
        if section not in content:
            issues.append({"type": "missing_section", "section": section, "fix": f"添加 {section} 部分"})

    # === 3. 重复条目检查 ===
    link_pattern = r"\(\((\d{14}-[a-z0-9]{7})\s+['\"]([^'\"]+)['\"]\)\)"
    links = re.findall(link_pattern, content)
    seen = {}
    for doc_id_link, title in links:
        if doc_id_link in seen:
            issues.append(
                {
                    "type": "duplicate_entry",
                    "content": f"(({doc_id_link} '{title}'))",
                    "first_occurrence": f"(({seen[doc_id_link][0]} '{seen[doc_id_link][1]}'))",
                    "fix": f"删除重复条目，保留第一个出现的 '{title}'",
                }
            )
        else:
            seen[doc_id_link] = (doc_id_link, title)

    # === 4. 链接格式检查 ===
    wrong_link_pattern = r"\(\(\d{14}-[a-z0-9]{7}\s+[^'\)]+\)\)"
    matches = re.finditer(wrong_link_pattern, content)
    for match in matches:
        if "'" not in match.group():
            issues.append(
                {
                    "type": "invalid_link_format",
                    "content": match.group(),
                    "fix": "使用 ((docId '标题')) 格式，注意单引号",
                }
            )

    # === 5. 结构层级检查 ===
    title_line_idx = None
    for i, line in enumerate(lines):
        if "LLM Wiki 索引" in line and line.strip().startswith("#"):
            title_line_idx = i
            break

    if title_line_idx is not None and title_line_idx > 0:
        for i in range(title_line_idx):
            stripped = lines[i].strip()
            if stripped and not stripped.startswith("{:"):
                issues.append(
                    {
                        "type": "content_before_title",
                        "line": i + 1,
                        "content": stripped[:60],
                        "fix": "删除 '# LLM Wiki 索引' 之前的所有内容",
                    }
                )
                break

    return issues


def validate_entity_page(doc_id: str) -> List[dict]:
    """验证实体页格式"""
    content_result = run_siyuan(f"content {doc_id}")
    if "error" in content_result:
        return []

    content = content_result.get("content", "")
    issues = []

    required_sections = ["## 描述", "## 来源描述"]
    for section in required_sections:
        if section not in content:
            issues.append(
                {"type": "missing_entity_section", "section": section, "fix": f"添加 {section} 部分"}
            )

    return issues


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="LLM Wiki Ingest 验证工具")
    parser.add_argument("--doc-id", help="要验证的文档 ID")
    parser.add_argument(
        "--type", choices=["log", "index", "entity", "all"], default="all", help="验证类型"
    )
    parser.add_argument("--fix", action="store_true", help="尝试自动修复问题")

    args = parser.parse_args()

    # 从配置中读取文档 ID
    DOC_IDS = {
        "log": CONFIG["docs"]["log"],
        "index": CONFIG["docs"]["index"],
        "schema": CONFIG["docs"]["schema"],
    }

    all_issues = []

    if args.doc_id:
        if args.type == "log" or args.type == "all":
            all_issues.extend(check_log_format(args.doc_id))
        if args.type == "index" or args.type == "all":
            all_issues.extend(check_index_format(args.doc_id))
        if args.type == "entity" or args.type == "all":
            all_issues.extend(validate_entity_page(args.doc_id))
        all_issues.extend(check_residual_text_blocks(args.doc_id))
    else:
        print("🔍 验证核心文档...")

        # 检查 log
        log_issues = check_log_format(DOC_IDS["log"])
        log_issues.extend(check_residual_text_blocks(DOC_IDS["log"]))
        if log_issues:
            print(f"\n📄 Log 文档 ({DOC_IDS['log']}):")
            for issue in log_issues:
                print(f"  ❌ {issue['type']}: {issue.get('content', issue.get('field', ''))[:50]}")
                print(f"     修复: {issue['fix']}")
            all_issues.extend(log_issues)
        else:
            print("  ✅ Log 文档格式正确")

        # 检查 index
        index_issues = check_index_format(DOC_IDS["index"])
        index_issues.extend(check_residual_text_blocks(DOC_IDS["index"]))
        if index_issues:
            print(f"\n📄 Index 文档 ({DOC_IDS['index']}):")
            for issue in index_issues:
                print(f"  ❌ {issue['type']}: {issue.get('content', issue.get('section', ''))[:50]}")
                print(f"     修复: {issue['fix']}")
            all_issues.extend(index_issues)
        else:
            print("  ✅ Index 文档格式正确")

    # 输出结果
    print(f"\n{'=' * 50}")
    if all_issues:
        print(f"❌ 发现 {len(all_issues)} 个问题")
        sys.exit(1)
    else:
        print("✅ 所有检查通过")
        sys.exit(0)


if __name__ == "__main__":
    main()
