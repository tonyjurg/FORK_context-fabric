"""Integration tests for new MCP tools.

Tests describe_corpus(), search_continue(), get_passages(), get_node_features(),
and search return_type parameter.
"""

import pytest

from cfabric_mcp import tools
from cfabric_mcp.cache import reset_cache


class TestDescribeCorpus:
    """Tests for describe_corpus tool."""

    def test_returns_corpus_name(self, loaded_corpus):
        """Should return corpus name."""
        result = tools.describe_corpus(corpus=loaded_corpus)

        assert "name" in result
        assert result["name"] == loaded_corpus

    def test_includes_node_types(self, loaded_corpus):
        """Should include node types with counts."""
        result = tools.describe_corpus(corpus=loaded_corpus)

        assert "node_types" in result
        node_types = result["node_types"]
        assert len(node_types) > 0

        # Check structure
        for nt in node_types:
            assert "type" in nt
            assert "count" in nt
            assert "is_slot_type" in nt

    def test_includes_sections(self, loaded_corpus):
        """Should include section structure."""
        result = tools.describe_corpus(corpus=loaded_corpus)

        assert "sections" in result
        sections = result["sections"]
        assert "levels" in sections

    def test_includes_features_metadata(self, loaded_corpus):
        """Features should be accessed via list_features, not describe_corpus."""
        # describe_corpus is now slimmed down - no features
        result = tools.describe_corpus(corpus=loaded_corpus)
        assert "features" not in result  # Use list_features() instead

        # list_features should return feature metadata
        features_result = tools.list_features(corpus=loaded_corpus)
        assert "features" in features_result
        features = features_result["features"]
        assert len(features) > 0

        # Features should have metadata but no sample values
        for feat in features:
            assert "name" in feat
            assert "value_type" in feat
            assert "sample_values" not in feat

    def test_no_search_hints(self, loaded_corpus):
        """Should not include search hints (removed)."""
        result = tools.describe_corpus(corpus=loaded_corpus)

        assert "search_hints" not in result

    def test_describe_feature_returns_samples(self, loaded_corpus):
        """describe_feature should return sample values."""
        result = tools.describe_feature("pos", corpus=loaded_corpus)

        assert result["name"] == "pos"
        assert result["kind"] == "node"
        assert "unique_values" in result
        assert "sample_values" in result
        assert len(result["sample_values"]) > 0


class TestSearchReturnTypes:
    """Tests for search return_type parameter."""

    def test_return_type_count(self, loaded_corpus):
        """return_type='count' should return just total count."""
        reset_cache()
        result = tools.search("word", return_type="count", corpus=loaded_corpus)

        assert "total_count" in result
        assert result["total_count"] == 5
        assert "results" not in result or result.get("results") is None

    def test_return_type_results(self, loaded_corpus):
        """return_type='results' should return paginated results with cursor."""
        reset_cache()
        result = tools.search("word", return_type="results", limit=2, corpus=loaded_corpus)

        assert "results" in result
        assert len(result["results"]) == 2
        assert "cursor" in result
        assert result["cursor"]["has_more"] is True

    def test_return_type_statistics(self, loaded_corpus):
        """return_type='statistics' should return feature distributions."""
        reset_cache()
        result = tools.search(
            "word", return_type="statistics", aggregate_features=["pos"], corpus=loaded_corpus
        )

        assert "total_count" in result
        assert "nodes" in result
        assert len(result["nodes"]) > 0

    def test_return_type_passages(self, loaded_corpus):
        """return_type='passages' should return formatted passages."""
        reset_cache()
        result = tools.search("word", return_type="passages", limit=3, corpus=loaded_corpus)

        assert "passages" in result
        assert len(result["passages"]) == 3
        for passage in result["passages"]:
            assert "text" in passage
            assert "node" in passage


class TestSearchContinue:
    """Tests for search_continue (cursor-based pagination)."""

    def test_continue_with_valid_cursor(self, loaded_corpus):
        """Should continue search with valid cursor."""
        reset_cache()

        # First search
        result1 = tools.search("word", limit=2, corpus=loaded_corpus)
        cursor_id = result1["cursor"]["id"]

        # Continue with offset
        result2 = tools.search_continue(cursor_id, offset=2, limit=2)

        assert "results" in result2
        assert len(result2["results"]) == 2
        assert "cursor" in result2

    def test_continue_returns_remaining_results(self, loaded_corpus):
        """Continuation should return remaining results."""
        reset_cache()

        # First search - get first 2
        result1 = tools.search("word", limit=2, corpus=loaded_corpus)
        cursor_id = result1["cursor"]["id"]
        first_nodes = [r[0]["node"] for r in result1["results"]]

        # Continue - get next 2
        result2 = tools.search_continue(cursor_id, offset=2, limit=2)
        second_nodes = [r[0]["node"] for r in result2["results"]]

        # Should have different nodes
        assert set(first_nodes).isdisjoint(set(second_nodes))

    def test_continue_with_invalid_cursor(self):
        """Should return error for invalid cursor."""
        result = tools.search_continue("invalid-cursor-id")

        assert "error" in result

    def test_cursor_shows_has_more(self, loaded_corpus):
        """Cursor should accurately report has_more."""
        reset_cache()

        # Get last page
        result = tools.search("word", limit=10, corpus=loaded_corpus)

        assert result["cursor"]["has_more"] is False


class TestGetPassages:
    """Tests for get_passages tool."""

    def test_get_single_passage(self, loaded_corpus):
        """Should get passage for single section reference."""
        result = tools.get_passages(
            sections=[["test_sentence", 1, 1]],
            corpus=loaded_corpus,
        )

        assert "passages" in result
        assert result["total"] == 1

    def test_get_multiple_passages(self, loaded_corpus):
        """Should get passages for multiple section references."""
        result = tools.get_passages(
            sections=[
                ["test_sentence", 1, 1],
                ["test_sentence", 1, 2],
            ],
            corpus=loaded_corpus,
        )

        assert result["total"] == 2

    def test_invalid_section_returns_error(self, loaded_corpus):
        """Should return error for invalid section."""
        result = tools.get_passages(
            sections=[["nonexistent", 99, 99]],
            corpus=loaded_corpus,
        )

        assert result["total"] == 1
        assert result["found"] == 0
        assert "error" in result["passages"][0]


class TestGetNodeFeatures:
    """Tests for get_node_features tool."""

    def test_get_features_for_nodes(self, loaded_corpus):
        """Should get feature values for specified nodes."""
        result = tools.get_node_features(
            nodes=[1, 2, 3],
            features=["word", "pos"],
            corpus=loaded_corpus,
        )

        assert "nodes" in result
        assert result["total"] == 3
        for node_data in result["nodes"]:
            assert "node" in node_data
            assert "type" in node_data

    def test_includes_requested_features(self, loaded_corpus):
        """Should include values for requested features."""
        result = tools.get_node_features(
            nodes=[1],
            features=["word"],
            corpus=loaded_corpus,
        )

        assert "word" in result["nodes"][0]

    def test_returns_feature_list(self, loaded_corpus):
        """Should return list of requested features."""
        features = ["word", "pos"]
        result = tools.get_node_features(
            nodes=[1, 2],
            features=features,
            corpus=loaded_corpus,
        )

        assert result["features_requested"] == features


class TestCacheIntegration:
    """Tests for cache integration with search."""

    def test_cache_reused_for_different_return_types(self, loaded_corpus):
        """Same template should reuse cached results for different return_types."""
        reset_cache()
        template = "word pos=adjective"

        # First call - count
        result1 = tools.search(template, return_type="count", corpus=loaded_corpus)

        # Second call - results (should hit cache)
        result2 = tools.search(template, return_type="results", corpus=loaded_corpus)

        # Third call - statistics (should hit cache)
        result3 = tools.search(template, return_type="statistics", corpus=loaded_corpus)

        # All should have same total count
        assert result1["total_count"] == 2
        assert result2["total_count"] == 2
        assert result3["total_count"] == 2

    def test_cache_returns_cursor_for_pagination(self, loaded_corpus):
        """Cached results should support pagination via cursor."""
        reset_cache()
        template = "word"

        # First call
        result1 = tools.search(template, limit=2, corpus=loaded_corpus)
        cursor_id = result1["cursor"]["id"]

        # Paginate using cursor
        result2 = tools.search_continue(cursor_id, offset=2, limit=2)

        # Should get different results
        assert len(result2["results"]) == 2
