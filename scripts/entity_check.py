#!/usr/bin/env python3
"""
实体约束检查 - Layer 1 认知边界
单次处理 ≤ 4 个实体，超限自动拆分
"""

import argparse
import json
from typing import List, Any

MAX_ENTITIES = 4  # 认知边界：单次处理上限


def constrain_entities(entities: List[Any]) -> List[List[Any]]:
    """
    将实体列表拆分为多个批次，每批不超过 MAX_ENTITIES

    Returns:
        List[List[Any]]: 批次列表
    """
    if len(entities) <= MAX_ENTITIES:
        return [entities]

    batches = []
    for i in range(0, len(entities), MAX_ENTITIES):
        batch = entities[i:i + MAX_ENTITIES]
        batches.append(batch)

    return batches


def validate_entity_count(entities: List[Any]) -> dict:
    """
    验证实体数量并返回建议
    """
    count = len(entities)
    batches = constrain_entities(entities)

    return {
        "total": count,
        "max_allowed": MAX_ENTITIES,
        "exceeded": count > MAX_ENTITIES,
        "batches": batches,
        "batch_count": len(batches),
        "recommendation": f"拆分为 {len(batches)} 个批次处理" if count > MAX_ENTITIES else "无需拆分"
    }


def main():
    parser = argparse.ArgumentParser(description="实体约束检查工具")
    parser.add_argument("--items", type=str, help="逗号分隔的实体列表")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")

    args = parser.parse_args()

    if not args.items:
        print("用法: python entity_check.py --items 'item1,item2,item3,item4,item5'")
        return

    entities = [item.strip() for item in args.items.split(",") if item.strip()]
    result = validate_entity_count(entities)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"实体总数: {result['total']}")
        print(f"认知上限: {result['max_allowed']}")
        print(f"是否超限: {'是 ⚠️' if result['exceeded'] else '否 ✅'}")

        if result['exceeded']:
            print(f"\n建议: {result['recommendation']}")
            print("\n批次分配:")
            for i, batch in enumerate(result['batches'], 1):
                print(f"  批次 {i}: {', '.join(batch)}")

        # 返回码：超限返回 1，正常返回 0
        exit(1 if result['exceeded'] else 0)


if __name__ == "__main__":
    main()
