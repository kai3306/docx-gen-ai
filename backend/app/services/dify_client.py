import json
import time
from typing import Optional
from app.core.config import settings


MOCK_TEST_CASES = {
    "login": {
        "test_cases": [
            {"title": "正常登录", "steps": ["打开登录页面", "输入有效用户名和密码", "点击登录按钮"], "expected": "登录成功，跳转到首页"},
            {"title": "空用户名登录", "steps": ["打开登录页面", "密码输入有效值", "用户名留空", "点击登录按钮"], "expected": "提示'请输入用户名'"},
            {"title": "空密码登录", "steps": ["打开登录页面", "用户名输入有效值", "密码留空", "点击登录按钮"], "expected": "提示'请输入密码'"},
            {"title": "错误密码登录", "steps": ["打开登录页面", "输入有效用户名", "输入错误密码", "点击登录按钮"], "expected": "提示'用户名或密码错误'"},
        ]
    },
    "search": {
        "test_cases": [
            {"title": "正常搜索", "steps": ["打开搜索页面", "输入关键词", "点击搜索按钮"], "expected": "显示相关搜索结果"},
            {"title": "空搜索", "steps": ["打开搜索页面", "搜索框留空", "点击搜索按钮"], "expected": "提示'请输入搜索关键词'"},
            {"title": "无结果搜索", "steps": ["打开搜索页面", "输入不存在的关键词", "点击搜索按钮"], "expected": "显示'未找到相关结果'"},
        ]
    },
    "upload": {
        "test_cases": [
            {"title": "上传有效文件", "steps": ["打开上传页面", "选择符合格式要求的文件", "点击上传"], "expected": "文件上传成功"},
            {"title": "上传超大文件", "steps": ["打开上传页面", "选择超过限制大小的文件", "点击上传"], "expected": "提示'文件大小超过限制'"},
            {"title": "上传不支持格式", "steps": ["打开上传页面", "选择不支持格式的文件", "点击上传"], "expected": "提示'不支持的文件格式'"},
        ]
    },
}

MOCK_TEST_RESULTS = {
    "login": {
        "test_results": [
            {"case_title": "正常登录", "result": "通过", "actual": "登录成功，跳转到首页", "note": ""},
            {"case_title": "空用户名登录", "result": "通过", "actual": "提示'请输入用户名'", "note": ""},
            {"case_title": "空密码登录", "result": "通过", "actual": "提示'请输入密码'", "note": ""},
            {"case_title": "错误密码登录", "result": "通过", "actual": "提示'用户名或密码错误'", "note": ""},
        ]
    },
    "search": {
        "test_results": [
            {"case_title": "正常搜索", "result": "通过", "actual": "显示相关搜索结果", "note": ""},
            {"case_title": "空搜索", "result": "未通过", "actual": "页面无响应", "note": "缺少空搜索提示"},
            {"case_title": "无结果搜索", "result": "通过", "actual": "显示'未找到相关结果'", "note": ""},
        ]
    },
    "upload": {
        "test_results": [
            {"case_title": "上传有效文件", "result": "通过", "actual": "文件上传成功", "note": ""},
            {"case_title": "上传超大文件", "result": "通过", "actual": "提示'文件大小超过限制'", "note": ""},
            {"case_title": "上传不支持格式", "result": "通过", "actual": "提示'不支持的文件格式'", "note": ""},
        ]
    },
}

DEFAULT_TEST_CASES = {
    "test_cases": [
        {"title": "正常功能验证", "steps": ["准备测试数据", "执行功能操作", "检查结果"], "expected": "功能正常"},
        {"title": "异常输入测试", "steps": ["准备异常测试数据", "执行功能操作", "检查异常处理"], "expected": "正确提示错误信息"},
        {"title": "边界值测试", "steps": ["准备边界测试数据", "执行功能操作", "检查结果"], "expected": "边界值处理正确"},
    ]
}

DEFAULT_TEST_RESULTS = {
    "test_results": [
        {"case_title": "正常功能验证", "result": "通过", "actual": "功能正常", "note": ""},
        {"case_title": "异常输入测试", "result": "通过", "actual": "正确提示错误信息", "note": ""},
        {"case_title": "边界值测试", "result": "未通过", "actual": "边界值处理异常", "note": "需开发修复"},
    ]
}


def _find_mock_data(source_text: str, data_type: str):
    source_lower = source_text.lower()
    matched_key = None

    for keyword in MOCK_TEST_CASES:
        if keyword in source_lower:
            matched_key = keyword
            break

    if not matched_key:
        return None

    if data_type == "test_case":
        return MOCK_TEST_CASES[matched_key]
    elif data_type == "test_result":
        return MOCK_TEST_RESULTS[matched_key]

    return None


def generate(source_text: str, generate_type: str, template_path: Optional[str] = None) -> dict:
    """
    Call Dify workflow to generate document data.

    In mock mode, returns pre-defined mock data based on keywords in source text.
    In production mode, calls the actual Dify API.
    """
    if settings.MOCK_DIFY:
        time.sleep(1)

        mock_data = _find_mock_data(source_text, generate_type)
        if mock_data:
            return mock_data

        if generate_type == "test_case":
            return DEFAULT_TEST_CASES
        elif generate_type == "test_result":
            return DEFAULT_TEST_RESULTS
        return {"error": "unknown_generate_type"}

    import requests
    payload = {
        "inputs": {
            "source_text": source_text,
            "generate_type": generate_type,
            "template_path": template_path or "",
        },
        "response_mode": "blocking",
    }
    headers = {
        "Authorization": f"Bearer {settings.DIFY_API_KEY}",
        "Content-Type": "application/json",
    }
    resp = requests.post(f"{settings.DIFY_API_URL}/workflows/run", json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()
