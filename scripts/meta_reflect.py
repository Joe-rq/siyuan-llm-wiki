#!/usr/bin/env python3
"""
元反思检查点 - Layer 1 认知边界
每次关键操作后必须回答的 6 个问题
"""

import argparse
from typing import List


META_REFLECTION_QUESTIONS = [
    {
        "id": 1,
        "question": "正确性",
        "description": "实现是否正确？有无语法/逻辑错误？"
    },
    {
        "id": 2,
        "question": "目标达成",
        "description": "是否实现了初始需求的目标？"
    },
    {
        "id": 3,
        "question": "功能完整性",
        "description": "是否存在重大逻辑缺失？"
    },
    {
        "id": 4,
        "question": "向后兼容",
        "description": "是否破坏了旧功能？"
    },
    {
        "id": 5,
        "question": "安全性",
        "description": "是否存在漏洞或安全隐患？"
    },
    {
        "id": 6,
        "question": "优化空间",
        "description": "是否有更好的实现方式？"
    }
]


def print_checklist(task_name: str = ""):
    """打印元反思检查清单"""
    header = f"## 元反思检查清单"
    if task_name:
        header += f" - {task_name}"

    print(header)
    print()
    print("执行后必须回答以下问题：")
    print()

    for q in META_REFLECTION_QUESTIONS:
        print(f"{q['id']}. **{q['question']}**：{q['description']}")

    print()
    print("<!-- 请在每个问题后标记：✅ 通过 / ❌ 未通过 / ⚠️ 需关注 -->")


def validate_answers(answers: List[str]) -> bool:
    """
    验证元反思答案
    如果任何一个问题标记为 ❌ 或 ⚠️，需要详细说明
    """
    has_issues = False

    for i, answer in enumerate(answers):
        if "❌" in answer or "⚠️" in answer:
            has_issues = True
            print(f"问题 {i+1} 需要关注: {answer}")

    return not has_issues


def main():
    parser = argparse.ArgumentParser(description="元反思检查点工具")
    parser.add_argument("--task", type=str, help="任务名称")
    parser.add_argument("--template", action="store_true",
                        help="输出模板格式")
    parser.add_argument("--check", type=str,
                        help="检查答案（逗号分隔，如：✅,✅,✅,✅,✅,⚠️）")

    args = parser.parse_args()

    if args.template:
        print_checklist(args.task)
        return

    if args.check:
        answers = args.check.split(",")
        if len(answers) != 6:
            print("错误: 需要提供 6 个答案，用逗号分隔")
            return

        if validate_answers(answers):
            print("✅ 所有检查通过，可以继续")
        else:
            print("\n⚠️ 发现问题，建议暂停并解决后再继续")
        return

    # 默认输出检查清单
    print_checklist(args.task)


if __name__ == "__main__":
    main()
