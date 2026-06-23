"""Unit tests for safety_checker"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import safety_checker


class TestBasicFunctions:
    """Test basic utility functions"""
    
    def test_random_user_agent(self):
        """Test user agent selection"""
        ua = safety_checker.get_random_user_agent()
        assert isinstance(ua, str)
        assert len(ua) > 0
    
    def test_xss_payloads_exist(self):
        """Test XSS payload list"""
        assert len(safety_checker.XSS_PAYLOADS) > 0
        assert any("script" in p for p in safety_checker.XSS_PAYLOADS)
    
    def test_sqli_payloads_exist(self):
        """Test SQL injection payload list"""
        assert len(safety_checker.SQLI_PAYLOADS) > 0
        assert any("OR" in p or "UNION" in p for p in safety_checker.SQLI_PAYLOADS)
    
    def test_common_dirs_exist(self):
        """Test directory list"""
        assert "admin" in safety_checker.COMMON_DIRS
        assert "api" in safety_checker.COMMON_DIRS
        assert len(safety_checker.COMMON_DIRS) > 0


class TestURLHandling:
    """Test URL parsing and handling"""
    
    def test_parse_forms_empty_soup(self):
        """Test form parsing with empty content"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup("<html></html>", "html.parser")
        forms = safety_checker.parse_forms(soup)
        assert isinstance(forms, list)
        assert len(forms) == 0
    
    def test_parse_forms_with_form(self):
        """Test form parsing with actual form"""
        from bs4 import BeautifulSoup
        html = '<form action="/login" method="post"><input name="user" type="text"><input name="pass" type="password"></form>'
        soup = BeautifulSoup(html, "html.parser")
        forms = safety_checker.parse_forms(soup)
        assert len(forms) == 1
        assert forms[0]["method"] == "POST"
        assert forms[0]["has_password"] == True


class TestReportGeneration:
    """Test report generation"""
    
    def test_report_structure(self):
        """Test basic report structure"""
        report = {"url": "https://example.com", "timestamp": "2024-01-01"}
        assert "url" in report
        assert "timestamp" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
