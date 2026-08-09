"""تبويبات الواجهة — ملف واحد لكل تبويب."""

from tabs.about import render_about_tab
from tabs.batch import render_batch_tab
from tabs.dashboard import render_dashboard_tab
from tabs.live import render_live_tab
from tabs.single import render_single_tab

__all__ = [
    "render_about_tab",
    "render_batch_tab",
    "render_dashboard_tab",
    "render_live_tab",
    "render_single_tab",
]
