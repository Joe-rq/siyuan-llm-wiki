#!/usr/bin/env python3
"""
模式积累 - Layer 4 持续优化
将经验沉淀到模式库，形成知识复利
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

PATTERNS_FILE = Path(__file__).parent.parent / "memory" / "patterns.md"


def load_patterns() -> list:
    """加载已有模式"""
    if not PATTERNS_FILE.exists():
        return []

    content = PATTERNS_FILE.read_text(encoding="utf-8")
    patterns = []

    # 简单解析：按 ## 分割
    sections = content.split("\n## ")
    for section in sections[1:]:  # 跳过第一个空内容
        lines = section.strip().split("\n")
        if not lines:
            continue

        name = lines[0].strip()
        body = "\n".join(lines[1:])

        patterns.append({
            "name": name,
            "body": body
        })

    return patterns


def save_pattern(name: str, problem: str, solution: str, category: str = ""):
    """保存新模式"""
    PATTERNS_FILE.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d")

    entry = f"""## {name}

**类别**: {category or "未分类"}
**日期**: {timestamp}

**问题描述**:
{problem}

**解决方案**:
{solution}

**如何应用**:
- 触发条件：
- 应对措施：

---

"""

    if PATTERNS_FILE.exists():
        content = PATTERNS_FILE.read_text(encoding="utf-8")
    else:
        content = "# LLM Wiki 模式库\n\n> 记录已知问题和最佳实践\n\n"

    content += entry
    PATTERNS_FILE.write_text(content, encoding="utf-8")

    return True


def list_patterns():
    """列出所有模式"""
    patterns = load_patterns()

    if not patterns:
        print("模式库为空")
        return

    print(f"共有 {len(patterns)} 个模式:\n")
    for i, p in enumerate(patterns, 1):
        print(f"{i}. {p['name']}")


def search_pattern(keyword: str):
    """搜索模式"""
    patterns = load_patterns()

    matches = []
    for p in patterns:
        if keyword.lower() in p['name'].lower() or keyword.lower() in p['body'].lower():
            matches.append(p)

    if not matches:
        print(f"未找到包含 '{keyword}' 的模式")
        return

    print(f"找到 {len(matches)} 个匹配:\n")
    for p in matches:
        print(f"## {p['name']}")
        print(p['body'][:500] + "..." if len(p['body']) > 500 else p['body'])
        print()


def main():
    parser = argparse.ArgumentParser(description="模式积累工具")
    parser.add_argument("--name", type=str, help="模式名称")
    parser.add_argument("--problem", type=str, help="问题描述")
    parser.add_argument("--solution", type=str, help="解决方案")
    parser.add_argument("--category", type=str, default="", help="类别")
    parser.add_argument("--list", action="store_true", help="列出所有模式")
    parser.add_argument("--search", type=str, help="搜索模式")

    args = parser.parse_args()

    if args.list:
        list_patterns()
        return

    if args.search:
        search_pattern(args.search)
        return

    if args.name and args.problem and args.solution:
        save_pattern(args.name, args.problem, args.solution, args.category)
        print(f"✅ 已保存模式: {args.name}")
        print(f"📁 位置: {PATTERNS_FILE}")
        return

    print("用法示例:")
    print(f'  python pattern_accumulate.py --name "bi命令陷阱" \\\')
    print(f'    --problem "使用bi插入链接列表时出现残留文本块" \\\')
    print(f'    --solution "改用update重写或使用-开头的列表格式" \\\')
    print(f'    --category "思源操作"')
    print()
    print("其他命令:")
    print("  --list          列出所有模式")
    print("  --search KEY    搜索模式")


if __name__ == "__main__":
    main()
