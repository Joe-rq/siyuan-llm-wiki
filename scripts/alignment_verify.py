#!/usr/bin/env python3
"""
对齐验证 - Layer 3 执行可靠
"A 不完善 B 补全"：对照需求检查实现偏差
"""

import argparse
import difflib
from typing import List, Tuple


def parse_requirements(requirements: str) -> List[str]:
    """解析需求列表"""
    return [r.strip() for r in requirements.split(";") if r.strip()]


def parse_implementation(impl: str) -> List[str]:
    """解析实现列表"""
    return [i.strip() for i in impl.split(";") if i.strip()]


def check_alignment(requirements: List[str], implementation: List[str]) -> Tuple[List[str], List[str], List[str]]:
    """
    对照需求检查实现

    Returns:
        matched: 已匹配的需求
        missing: 未实现的需求
        extra: 额外的实现
    """
    matched = []
    missing = []
    extra = implementation.copy()

    for req in requirements:
        # 模糊匹配
        best_match = None
        best_ratio = 0

        for impl in extra:
            ratio = difflib.SequenceMatcher(None, req.lower(), impl.lower()).ratio()
            if ratio > best_ratio and ratio > 0.6:  # 阈值 60%
                best_ratio = ratio
                best_match = impl

        if best_match:
            matched.append(f"{req} <-> {best_match}")
            extra.remove(best_match)
        else:
            missing.append(req)

    return matched, missing, extra


def print_report(matched: List[str], missing: List[str], extra: List[str]):
    """打印对齐验证报告"""
    print("=" * 60)
    print("对齐验证报告")
    print("=" * 60)

    print(f"\n✅ 已匹配 ({len(matched)}):")
    for m in matched:
        print(f"   • {m}")

    if missing:
        print(f"\n❌ 未实现 ({len(missing)}):")
        for m in missing:
            print(f"   • {m}")

    if extra:
        print(f"\n⚠️ 额外实现 ({len(extra)}):")
        for e in extra:
            print(f"   • {e}")

    print("\n" + "=" * 60)

    if not missing and not extra:
        print("🎯 完全对齐")
    elif not missing:
        print("✅ 需求全覆盖，但有额外功能")
    else:
        print(f"⚠️ 存在 {len(missing)} 个需求未实现")

    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="对齐验证工具 - A 不完善 B 补全"
    )
    parser.add_argument(
        "-r", "--requirements",
        type=str,
        help="需求列表（分号分隔，如：'创建实体;更新索引;记录日志'）"
    )
    parser.add_argument(
        "-i", "--implementation",
        type=str,
        help="实现列表（分号分隔）"
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="严格模式：任何缺失都视为失败"
    )

    args = parser.parse_args()

    if not args.requirements or not args.implementation:
        print("用法示例:")
        print('  python alignment_verify.py \\\')
        print('    -r "创建实体;更新索引;记录日志" \\\')
        print('    -i "已创建实体;已更新索引"')
        return

    requirements = parse_requirements(args.requirements)
    implementation = parse_implementation(args.implementation)

    matched, missing, extra = check_alignment(requirements, implementation)
    print_report(matched, missing, extra)

    # 返回码
    if missing:
        exit(1)
    if args.strict and extra:
        exit(1)
    exit(0)


if __name__ == "__main__":
    main()
