"""Integration tests for search tools.

Tests search(), search_syntax_guide() with a real corpus.

Note: Search results return node info dictionaries in the format:
    [{'node': 1, 'otype': 'word', 'text': 'hello', ...}, ...]
For multi-atom queries, results are lists of dicts:
    [[{phrase_info}, {word_info}], ...]
"""

import pytest

from cfabric_mcp import tools


def get_node_id(result_item):
    """Extract node ID from a result item.

    Result items can be:
    - A list with a single dict: [{'node': 1, ...}]
    - A list with multiple dicts: [{'node': 6, ...}, {'node': 1, ...}]
    """
    if isinstance(result_item, list):
        # Return the node from the first element
        return int(result_item[0]["node"])
    elif isinstance(result_item, dict):
        return int(result_item["node"])
    return None


def get_all_node_ids(results):
    """Extract all first-atom node IDs from search results.

    For single-atom queries, returns list of node IDs.
    For multi-atom queries, returns list of first-atom node IDs.
    """
    return [get_node_id(r) for r in results]


class TestSearch:
    """Tests for searching the corpus."""

    def test_search_all_words(self, loaded_corpus):
        """Should find all word nodes."""
        result = tools.search("word", corpus=loaded_corpus)

        assert "results" in result
        assert len(result["results"]) == 5

    def test_search_all_phrases(self, loaded_corpus):
        """Should find all phrase nodes."""
        result = tools.search("phrase", corpus=loaded_corpus)

        assert len(result["results"]) == 2

    def test_search_all_sentences(self, loaded_corpus):
        """Should find all sentence nodes."""
        result = tools.search("sentence", corpus=loaded_corpus)

        assert len(result["results"]) == 1

    def test_search_by_feature_value(self, loaded_corpus):
        """Should find nodes by feature value."""
        result = tools.search("word word=hello", corpus=loaded_corpus)

        assert len(result["results"]) == 1
        # Result is a list containing node info dict
        assert get_node_id(result["results"][0]) == 1

    def test_search_by_pos_adjective(self, loaded_corpus):
        """Should find adjectives."""
        result = tools.search("word pos=adjective", corpus=loaded_corpus)

        assert len(result["results"]) == 2
        node_ids = get_all_node_ids(result["results"])
        assert 2 in node_ids  # beautiful
        assert 4 in node_ids  # good

    def test_search_by_pos_noun(self, loaded_corpus):
        """Should find nouns."""
        result = tools.search("word pos=noun", corpus=loaded_corpus)

        assert len(result["results"]) == 2
        node_ids = get_all_node_ids(result["results"])
        assert 3 in node_ids  # world
        assert 5 in node_ids  # morning

    def test_search_embedded_pattern(self, loaded_corpus):
        """Should find embedded patterns (phrase containing word)."""
        result = tools.search("phrase\n  word", corpus=loaded_corpus)

        assert len(result["results"]) > 0
        # Each result is a list of dicts: [phrase_info, word_info]
        for r in result["results"]:
            phrase_node = int(r[0]["node"])
            word_node = int(r[1]["node"])
            assert phrase_node in [6, 7]  # phrase nodes
            assert word_node in [1, 2, 3, 4, 5]  # word nodes

    def test_search_phrase_with_specific_word(self, loaded_corpus):
        """Should find phrase containing specific word."""
        result = tools.search("phrase\n  word word=hello", corpus=loaded_corpus)

        assert len(result["results"]) == 1
        phrase_info, word_info = result["results"][0]
        assert int(phrase_info["node"]) == 6  # phrase containing "hello"
        assert int(word_info["node"]) == 1  # "hello"

    def test_search_sentence_with_word(self, loaded_corpus):
        """Should find sentence containing word."""
        result = tools.search("sentence\n  word", corpus=loaded_corpus)

        assert len(result["results"]) == 5  # one for each word
        for r in result["results"]:
            sentence_node = int(r[0]["node"])
            assert sentence_node == 8  # only sentence

    def test_search_respects_limit(self, loaded_corpus):
        """Should respect limit parameter."""
        result = tools.search("word", limit=2, corpus=loaded_corpus)

        assert len(result["results"]) == 2

    def test_search_returns_template(self, loaded_corpus):
        """Result should include the search template."""
        template = "word pos=noun"
        result = tools.search(template, corpus=loaded_corpus)

        assert result["template"] == template

    def test_invalid_template_returns_error(self, loaded_corpus):
        """Should return error for invalid template."""
        result = tools.search("invalid:::syntax<<<", corpus=loaded_corpus)

        # May return error or empty results depending on error handling
        assert "error" in result or len(result.get("results", [])) == 0


class TestSearchSyntaxGuide:
    """Tests for the search syntax guide (section-based documentation)."""

    def test_returns_guide(self):
        """Default call should return summary and section list."""
        result = tools.search_syntax_guide()

        assert "summary" in result
        assert "sections" in result
        assert "hint" in result
        assert len(result["summary"]) > 50
        assert len(result["sections"]) > 0

    def test_guide_contains_sections(self):
        """Sections list should contain key documentation topics."""
        result = tools.search_syntax_guide()
        sections = result["sections"]

        assert "basics" in sections
        assert "relations" in sections
        assert "quantifiers" in sections

    def test_returns_summary(self):
        """Should return a summary."""
        result = tools.search_syntax_guide()

        assert "summary" in result
        assert len(result["summary"]) > 0

    def test_section_returns_content(self):
        """Calling with section should return content for that section."""
        result = tools.search_syntax_guide(section="relations")

        assert "section" in result
        assert "content" in result
        assert result["section"] == "relations"
        assert len(result["content"]) > 0


