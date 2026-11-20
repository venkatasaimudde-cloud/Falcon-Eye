"""
Test suite verifying the Falcon Eye Navigation and AI Logo Sidebar Toggle functionality.
"""
import re

def test_index_html_sidebar_elements():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Header AI Logo Toggle Button
    assert 'id="header-ai-logo-btn"' in content
    assert 'class="header-ai-logo-btn"' in content
    assert 'fa-eye' in content

    # 2. Sidebar Overlay for responsive mobile drawer
    assert 'id="sidebar-overlay"' in content
    assert 'class="sidebar-overlay"' in content

    # 3. Sidebar Brand and Close buttons
    assert 'id="sidebar-brand-logo"' in content
    assert 'id="sidebar-close-icon-btn"' in content

    # 4. App container starts in collapsed state
    assert 'id="app-container" class="sidebar-collapsed"' in content

    # 5. All 10 existing navigation menu items preserved in order
    expected_items = [
        "command-center",
        "live-monitoring",
        "ai-detection",
        "crowd-intelligence",
        "face-privacy",
        "drone-intelligence",
        "geospatial",
        "emergency-response",
        "multilingual",
        "settings"
    ]
    matches = re.findall(r'data-view="([^"]+)"', content)
    assert matches == expected_items, f"Navigation order mismatch: {matches} vs {expected_items}"

def test_css_sidebar_transitions():
    with open("frontend/css/style.css", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Desktop transition
    assert "#app-container.sidebar-collapsed #sidebar" in content
    assert "#app-container.sidebar-open #sidebar" in content
    assert "transition: margin-left" in content or "margin-left:" in content

    # 2. Header AI logo styling & hover effects
    assert ".header-ai-logo-btn" in content
    assert ".header-ai-logo-btn:hover .brand-logo" in content
    assert ".sidebar-overlay" in content

    # 3. Responsive media query for drawer
    assert "@media (max-width: 900px)" in content

def test_js_sidebar_toggle_logic():
    with open("frontend/js/app.js", "r", encoding="utf-8") as f:
        content = f.read()

    assert "initSidebarToggle" in content
    assert "window.toggleSidebar" in content
    assert "isSidebarOpen" in content
    assert "Escape" in content
    assert "updateSidebarUI" in content
