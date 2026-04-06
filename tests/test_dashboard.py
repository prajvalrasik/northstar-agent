import unittest

from northstar_agent.interfaces.dashboard import render_dashboard_html


class DashboardTests(unittest.TestCase):
    def test_dashboard_contains_expected_sections(self):
        html = render_dashboard_html()

        self.assertIn("Northstar Agent", html)
        self.assertIn("Pending approvals", html)
        self.assertIn("Recent activity", html)
        self.assertIn("Saved memories", html)
        self.assertIn("fetchJson('/chat'", html)

    def test_dashboard_uses_escape_helper_and_no_inline_handlers(self):
        html = render_dashboard_html()

        self.assertIn("function escapeHtml(value)", html)
        self.assertIn("data-thread-id=", html)
        self.assertNotIn("onclick=\"resolveApproval", html)


if __name__ == "__main__":
    unittest.main()
