#!/usr/bin/env python3
"""
同类扫描 - Layer 4 持续优化
发现新问题时，全库扫描同类问题
"""

import argparse
import subprocess
import json
import os
import re
import sys
from pathlib import Path
from typing import List, Dict


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


CONFIG = load_wiki_config()
SIYUAN_JS = get_siyuan_js(CONFIG)


def run_siyuan(cmd: str) -> dict:
    """执行 siyuan.js 命令"""
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


def search_pattern(pattern: str, notebook_id: str = None) -> List[Dict]:
    """在思源中搜索匹配模式的文档"""
    result = run_siyuan(f'search "{pattern}"')
    if "error" in result:
        return []
    matches = result.get("results", [])
    return matches


def scan_similar_issues(issue_type: str, target_id: str = None) -> List[Dict]:
    """
    扫描同类问题

    issue_type 支持：
    - residual_text: 残留文本块
    - invalid_link: 无效链接格式
    - missing_section: 缺失标准章节
    """
    issues = []

    if issue_type == "residual_text":
        issues.append(
            {"type": "info", "message": "残留文本扫描需要遍历所有 wiki/ 文档"}
        )

    elif issue_type == "invalid_link":
        pattern = r"\(\([^(]*\)\)"
        matches = search_pattern("((")
        for m in matches:
            content = m.get("content", "")
            if re.search(r"\(\(\d{14}-[a-z0-9]{7}[^']", content):
                issues.append(
                    {
                        "doc_id": m.get("id"),
                        "title": m.get("title"),
                        "issue": "链接缺少单引号包围的标题",
                    }
                )

    elif issue_type == "missing_section":
        # 从配置中读取 entities 目录 ID
        entities_dir_id = CONFIG["dirs"]["wiki_entities"]
        entities_result = run_siyuan(f"ls {entities_dir_id}")
        if "error" not in entities_result:
            for doc in entities_result.get("files", []):
                doc_id = doc.get("id")
                content_result = run_siyuan(f"content {doc_id}")
                content = content_result.get("content", "")

                if "## 描述" not in content:
                    issues.append(
                        {
                            "doc_id": doc_id,
                            "title": doc.get("title"),
                            "issue": "缺失 '## 描述' 章节",
                        }
                    )

    return issues


def main():
    parser = argparse.ArgumentParser(description="同类问题扫描工具")
    parser.add_argument(
        "--type",
        choices=["residual_text", "invalid_link", "missing_section", "all"],
        default="all",
        help="扫描的问题类型",
    )
    parser.add_argument("--fix", action="store_true", help="尝试自动修复")

    args = parser.parse_args()

    print("🔍 扫描同类问题...")
    print("=" * 60)

    all_issues = []

    if args.type in ["residual_text", "all"]:
        issues = scan_similar_issues("residual_text")
        if issues:
            print(f"\n📄 残留文本问题:")
            for i in issues:
                print(f"   • {i}")
            all_issues.extend(issues)

    if args.type in ["invalid_link", "all"]:
        issues = scan_similar_issues("invalid_link")
        if issues:
            print(f"\n🔗 无效链接格式 ({len(issues)} 个):")
            for i in issues[:10]:
                print(f"   • {i.get('title', 'Unknown')}: {i.get('issue')}")
            all_issues.extend(issues)

    if args.type in ["missing_section", "all"]:
        issues = scan_similar_issues("missing_section")
        if issues:
            print(f"\n📋 缺失标准章节 ({len(issues)} 个):")
            for i in issues[:10]:
                print(f"   • {i.get('title', 'Unknown')}: {i.get('issue')}")
            all_issues.extend(issues)

    print("\n" + "=" * 60)
    print(f"总计发现 {len(all_issues)} 个同类问题")

    if all_issues and args.fix:
        print("\n⚠️ 自动修复功能尚未实现，请手动修复")


if __name__ == "__main__":
    main()
