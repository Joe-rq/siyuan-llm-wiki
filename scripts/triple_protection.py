#!/usr/bin/env python3
"""
三重防护 - Layer 2 意图防护
输入验证 → 执行监控 → 输出验证
"""

import argparse
import re
from typing import Callable, Optional, Tuple


class TripleProtection:
    """三重防护执行器"""

    def __init__(
        self,
        input_validator: Optional[Callable] = None,
        output_validator: Optional[Callable] = None,
        fallback: Optional[Callable] = None
    ):
        self.input_validator = input_validator
        self.output_validator = output_validator
        self.fallback = fallback
        self.errors = []

    def validate_input(self, data: str) -> Tuple[bool, str]:
        """第一重：输入验证"""
        if self.input_validator:
            return self.input_validator(data)

        # 默认验证：检查是否为有效 markdown
        if not data or not data.strip():
            return False, "输入为空"

        # 检查是否为思源链接格式
        invalid_patterns = [
            (r'^\d{14}-[a-z0-9]{7}$', "孤立的 docId，应使用 ((docId 'title')) 格式"),
            (r'\(\(\d{14}-[a-z0-9]{7}\s+[^\'"]', "链接格式错误，标题必须用单引号包围"),
        ]

        for pattern, msg in invalid_patterns:
            if re.search(pattern, data, re.MULTILINE):
                return False, f"输入格式问题: {msg}"

        return True, "OK"

    def execute(self, operation: Callable, data: str) -> Tuple[bool, str]:
        """第二重：执行监控"""
        try:
            result = operation(data)
            return True, result
        except Exception as e:
            error_msg = str(e)
            self.errors.append(error_msg)

            # 尝试兜底策略
            if self.fallback:
                try:
                    fallback_result = self.fallback(data)
                    return True, f"[FALLBACK] {fallback_result}"
                except Exception as fallback_e:
                    return False, f"执行失败: {error_msg}; 兜底也失败: {fallback_e}"

            return False, f"执行失败: {error_msg}"

    def validate_output(self, output: str) -> Tuple[bool, str]:
        """第三重：输出验证"""
        if self.output_validator:
            return self.output_validator(output)

        # 默认验证
        if not output or not output.strip():
            return False, "输出为空"

        # 检查是否包含错误标记
        if "[FALLBACK]" in output:
            return True, "降级输出"

        return True, "OK"

    def run(self, operation: Callable, data: str) -> dict:
        """执行完整的三重防护流程"""
        result = {
            "success": False,
            "input_valid": False,
            "execution_success": False,
            "output_valid": False,
            "input_check": "",
            "output": "",
            "output_check": "",
            "errors": []
        }

        # 第一重：输入验证
        input_ok, input_msg = self.validate_input(data)
        result["input_valid"] = input_ok
        result["input_check"] = input_msg

        if not input_ok:
            result["errors"].append(f"输入验证失败: {input_msg}")
            return result

        # 第二重：执行监控
        exec_ok, exec_result = self.execute(operation, data)
        result["execution_success"] = exec_ok
        result["output"] = exec_result

        if not exec_ok:
            result["errors"].append(f"执行失败: {exec_result}")
            return result

        # 第三重：输出验证
        output_ok, output_msg = self.validate_output(exec_result)
        result["output_valid"] = output_ok
        result["output_check"] = output_msg

        if not output_ok:
            result["errors"].append(f"输出验证失败: {output_msg}")
            return result

        result["success"] = True
        return result


def demo_operation(data: str) -> str:
    """示例操作：模拟写入思源"""
    if "error" in data.lower():
        raise ValueError("模拟执行错误")
    return f"成功处理: {data[:50]}..."


def demo_fallback(data: str) -> str:
    """示例兜底策略"""
    return f"降级处理: {data[:30]}..."


def main():
    parser = argparse.ArgumentParser(description="三重防护工具")
    parser.add_argument("--content", type=str, help="要处理的内容")
    parser.add_argument("--demo", action="store_true", help="运行示例")

    args = parser.parse_args()

    if args.demo:
        print("🛡️ 三重防护演示\n")

        # 创建防护器
        protector = TripleProtection(
            fallback=demo_fallback
        )

        # 测试用例
        test_cases = [
            ("正常内容", "((<ENTITY_DOC_ID> 'RAG')) 是检索增强生成"),
            ("空内容", ""),
            ("孤立 docId", "<ENTITY_DOC_ID>"),
            ("执行错误", "触发 error 的内容"),
        ]

        for name, content in test_cases:
            print(f"\n测试: {name}")
            print("-" * 40)
            result = protector.run(demo_operation, content)

            print(f"  输入验证: {'✅' if result['input_valid'] else '❌'} {result['input_check']}")
            print(f"  执行结果: {'✅' if result['execution_success'] else '❌'}")
            print(f"  输出验证: {'✅' if result['output_valid'] else '❌'} {result['output_check']}")
            print(f"  最终状态: {'🎯 成功' if result['success'] else '⚠️ 失败'}")

            if result['errors']:
                print(f"  错误: {result['errors']}")

        return

    if not args.content:
        print("用法:")
        print("  python triple_protection.py --content '要处理的内容'")
        print("  python triple_protection.py --demo")
        return

    protector = TripleProtection()
    result = protector.run(demo_operation, args.content)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    import json
    main()
