"""Tests for MCP tools."""

import pytest

from cfabric_mcp import tools


class TestSearchSyntaxGuide:
    """Tests for the search syntax guide (section-based)."""

    def test_returns_guide(self):
        """Test that search_syntax_guide returns summary and sections."""
        result = tools.search_syntax_guide()
        assert "summary" in result
        assert "sections" in result
        assert "hint" in result
        assert len(result["summary"]) > 50  # Should have concise summary
        assert len(result["sections"]) > 0

    def test_guide_contains_sections(self):
        """Test that sections list contains key topics."""
        result = tools.search_syntax_guide()
        sections = result["sections"]
        assert "basics" in sections
        assert "relations" in sections
        assert "quantifiers" in sections

    def test_section_returns_content(self):
        """Test that calling with section returns content."""
        result = tools.search_syntax_guide(section="relations")
        assert "section" in result
        assert "content" in result
        assert result["section"] == "relations"
        assert len(result["content"]) > 0


class TestListLoadedCorpora:
    """Tests for listing corpora."""

    def test_empty_initially(self):
        """Test that no corpora are loaded initially."""
        # Clear any loaded corpora
        from cfabric_mcp.corpus_manager import corpus_manager

        for name in list(corpus_manager.list_corpora()):
            corpus_manager.unload(name)

        result = tools.list_loaded_corpora()
        assert result["corpora"] == []
        assert result["current"] is None
