#!/usr/bin/env python3
"""
前端功能测试脚本
测试 UI 渲染、静态资源加载和基本功能
"""
import requests
import re
from bs4 import BeautifulSoup

BASE_URL = "http://127.0.0.1:5000"

def test_page_load():
    """测试页面加载"""
    print("📄 测试页面加载...")
    response = requests.get(BASE_URL)
    assert response.status_code == 200, "页面加载失败"
    assert "text/html" in response.headers.get("content-type", ""), "不是 HTML 页面"

    # 解析 HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # 检查关键元素
    assert soup.find('h1', class_='glow-text'), "缺少标题"
    assert soup.find('div', id='imageContainer'), "缺少图片容器"
    assert soup.find('textarea', id='promptInput'), "缺少输入框"
    assert soup.find('button', id='btnGenerate'), "缺少生成按钮"
    assert soup.find('button', id='btnRandom'), "缺少随机按钮"
    assert soup.find('div', id='styleTabs'), "缺少风格选择器"

    # 检查风格标签
    style_tabs = soup.find_all('button', class_='style-tab')
    assert len(style_tabs) >= 5, "应该至少有5种风格"

    print("  ✅ 页面加载正常")
    return True

def test_static_files():
    """测试静态文件加载"""
    print("\n📦 测试静态文件...")

    files_to_test = [
        '/static/style.css',
        '/static/main.js'
    ]

    for file in files_to_test:
        response = requests.get(f"{BASE_URL}{file}")
        assert response.status_code == 200, f"{file} 加载失败"
        print(f"  ✅ {file} 加载正常")

    return True

def test_css_features():
    """测试 CSS 特性"""
    print("\n🎨 测试 CSS 特性...")

    response = requests.get(f"{BASE_URL}/static/style.css")
    css_content = response.text

    # 检查关键 CSS 类
    required_classes = [
        'glow-text',
        'image-showcase',
        'style-tabs',
        'sidebar',
        'blob',
        'particle',
        'progress-bar'
    ]

    for css_class in required_classes:
        # 检查 .class 或 直接的类名
        pattern = f'.{css_class}|class="{css_class}"'
        assert re.search(pattern, css_content), f"缺少 CSS 类: {css_class}"
        print(f"  ✅ CSS 类 {css_class} 存在")

    return True

def test_js_features():
    """测试 JavaScript 特性"""
    print("\n⚙️ 测试 JavaScript 功能...")

    response = requests.get(f"{BASE_URL}/static/main.js")
    js_content = response.text

    # 检查关键功能
    required_features = [
        'generateImage',
        'addToHistory',
        'updateHistoryList',
        'stylePresets',
        'createParticles',
        'downloadBtn',
        'shareBtn',
        'pollForResult',
        'updateProgress',
        'sleep'
    ]

    for feature in required_features:
        assert feature in js_content, f"缺少 JS 功能: {feature}"
        print(f"  ✅ JS 功能 {feature} 存在")

    return True

def test_api_endpoints():
    """测试 API 端点"""
    print("\n🔌 测试 API 端点...")

    # 测试不存在的 task_id
    response = requests.get(f"{BASE_URL}/api/status/nonexistent-task")
    assert response.status_code == 404, "应该返回 404 for not found task"

    data = response.json()
    assert data.get("status") == "not_found", "状态应该是 not_found"
    print("  ✅ /api/status/<task_id> 端点正常")

    # 测试 generate 端点需要 POST
    response = requests.get(f"{BASE_URL}/api/generate")
    assert response.status_code == 405, "GET /api/generate 应该返回 405"
    print("  ✅ /api/generate 只接受 POST 方法")

    # 模拟回调并检查状态查询
    mock_task_id = "test-callback-task-id"
    callback_payload = {
        "success": True,
        "task_id": mock_task_id,
        "trace_id": "trace-test-id",
        "data": [
            {
                "prompt": "test prompt",
                "image_url": "https://example.com/test.png"
            }
        ]
    }
    callback_response = requests.post(
        f"{BASE_URL}/api/banana/callback",
        json=callback_payload
    )
    assert callback_response.status_code == 200, "callback 端点应返回 200"

    status_response = requests.get(f"{BASE_URL}/api/status/{mock_task_id}")
    assert status_response.status_code == 200, "callback 写入后应可查询任务状态"
    status_data = status_response.json()
    assert status_data.get("status") == "completed", "回调成功后状态应为 completed"
    assert status_data.get("image_url") == "https://example.com/test.png", "image_url 不匹配"
    print("  ✅ /api/banana/callback 异步回调正常")

    return True

def test_responsive_design():
    """测试响应式设计"""
    print("\n📱 测试响应式设计...")

    response = requests.get(f"{BASE_URL}/static/style.css")
    css_content = response.text

    # 检查媒体查询
    assert '@media' in css_content, "缺少媒体查询"
    assert 'max-width: 480px' in css_content, "缺少移动端适配"
    assert 'max-width: 768px' in css_content, "缺少平板适配"

    print("  ✅ 响应式设计正常")
    return True

def test_html_structure():
    """测试 HTML 结构"""
    print("\n🏗️ 测试 HTML 结构...")

    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 检查 meta 标签
    assert soup.find('meta', {'charset': True}), "缺少 charset"
    assert soup.find('meta', {'name': 'viewport'}), "缺少 viewport"
    assert soup.find('meta', {'name': 'description'}), "缺少 description"

    # 检查导航
    assert soup.find('nav', class_='top-nav'), "缺少导航栏"
    assert soup.find('div', class_='logo'), "缺少 Logo"
    assert soup.find('button', id='historyBtn'), "缺少历史记录按钮"
    assert soup.find('button', id='themeBtn'), "缺少主题切换按钮"

    # 检查图片操作按钮
    assert soup.find('div', id='imageActions'), "缺少图片操作区"
    assert soup.find('button', id='downloadBtn'), "缺少下载按钮"
    assert soup.find('button', id='shareBtn'), "缺少分享按钮"
    assert soup.find('button', id='regenerateBtn'), "缺少重新生成按钮"

    # 检查历史记录侧边栏
    assert soup.find('div', id='historySidebar'), "缺少历史记录侧边栏"
    assert soup.find('div', id='overlay'), "缺少遮罩层"

    # 检查页脚
    assert soup.find('footer', class_='footer'), "缺少页脚"

    print("  ✅ HTML 结构完整")
    return True

def test_style_presets():
    """测试风格预设"""
    print("\n🎭 测试风格预设...")

    response = requests.get(f"{BASE_URL}/static/main.js")
    js_content = response.text

    # 检查风格定义
    required_styles = ['alternate', 'cyberpunk', 'anime', 'realistic', 'fantasy']

    for style in required_styles:
        # 检查风格定义（支持多种格式）
        found = (
            f"'{style}'" in js_content or
            f'"{style}"' in js_content or
            f"'{style}':" in js_content or
            f'"{style}":' in js_content or
            f'data-style="{style}"' in js_content or
            f'{style}:' in js_content  # 对象字面量格式
        )
        assert found, f"缺少风格: {style}"
        print(f"  ✅ 风格 {style} 存在")

    return True

def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("🧪 开始前端功能测试")
    print("=" * 50)

    tests = [
        test_page_load,
        test_static_files,
        test_css_features,
        test_js_features,
        test_responsive_design,
        test_html_structure,
        test_style_presets,
        test_api_endpoints
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ❌ 测试失败: {e}")
            failed += 1
        except Exception as e:
            print(f"  ❌ 测试出错: {e}")
            failed += 1

    print("\n" + "=" * 50)
    print(f"✅ 通过: {passed} | ❌ 失败: {failed}")
    print("=" * 50)

    return failed == 0

if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
