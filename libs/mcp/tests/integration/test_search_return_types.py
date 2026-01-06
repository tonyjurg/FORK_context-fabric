"""Integration tests for search return_type functionality.

Tests the different return_type options: results, count, statistics, passages.
"""

import pytest

from cfabric_mcp import tools
from cfabric_mcp.cache import reset_cache


class TestReturnTypeResults:
    """Tests for return_type='results'."""

    def test_returns_node_info_list(self, loaded_corpus):
        """Results should be list of node info dicts."""
        reset_cache()
        result = tools.search("word", return_type="results", corpus=loaded_corpus)

        assert "results" in result
        for r in result["results"]:
            # Each result is a list of node dicts (one per atom)
            assert isinstance(r, list)
            assert len(r) >= 1
            # Check node info structure
            node_info = r[0]
            assert "node" in node_info
            assert "otype" in node_info
            assert "text" in node_info

    def test_includes_section_ref(self, loaded_corpus):
        """Results should include section_ref field."""
        reset_cache()
        result = tools.search("word", return_type="results", corpus=loaded_corpus)

        # At least some results should have section_ref
        has_section_ref = any(
            "section_ref" in r[0] and r[0]["section_ref"]
            for r in result["results"]
        )
        assert has_section_ref

    def test_cursor_structure(self, loaded_corpus):
        """Cursor should have required fields."""
        reset_cache()
        result = tools.search("word", return_type="results", limit=2, corpus=loaded_corpus)

        cursor = result["cursor"]
        assert "id" in cursor
        assert "offset" in cursor
        assert "limit" in cursor
        assert "has_more" in cursor
        assert "expires_at" in cursor

        assert cursor["offset"] == 0
        assert cursor["limit"] == 2

    def test_limit_respected(self, loaded_corpus):
        """Limit should control number of results returned."""
        reset_cache()
        result = tools.search("word", return_type="results", limit=2, corpus=loaded_corpus)

        assert len(result["results"]) == 2
        assert result["total_count"] == 5  # Total is still 5

    def test_multi_atom_query_structure(self, loaded_corpus):
        """Multi-atom queries should return list of lists."""
        reset_cache()
        result = tools.search("phrase\n  word", return_type="results", corpus=loaded_corpus)

        assert len(result["results"]) > 0
        for r in result["results"]:
            # Should have 2 nodes per result (phrase and word)
            assert len(r) == 2
            assert r[0]["otype"] == "phrase"
            assert r[1]["otype"] == "word"


class TestReturnTypeCount:
    """Tests for return_type='count'."""

    def test_returns_only_count(self, loaded_corpus):
        """Count should return total_count without results."""
        reset_cache()
        result = tools.search("word", return_type="count", corpus=loaded_corpus)

        assert "total_count" in result
        assert result["total_count"] == 5
        # Should not include full results
        assert result.get("results") is None or "results" not in result

    def test_count_with_feature_filter(self, loaded_corpus):
        """Count should work with feature filters."""
        reset_cache()
        result = tools.search("word pos=noun", return_type="count", corpus=loaded_corpus)

        assert result["total_count"] == 2  # "world" and "morning"

    def test_count_multi_atom(self, loaded_corpus):
        """Count should work with multi-atom queries."""
        reset_cache()
        result = tools.search("phrase\n  word", return_type="count", corpus=loaded_corpus)

        assert "total_count" in result
        assert result["total_count"] > 0


class TestReturnTypeStatistics:
    """Tests for return_type='statistics'."""

    def test_returns_nodes_dict(self, loaded_corpus):
        """Statistics should return nodes dict with distributions."""
        reset_cache()
        result = tools.search(
            "word", return_type="statistics", corpus=loaded_corpus
        )

        assert "nodes" in result
        assert "total_count" in result
        assert len(result["nodes"]) >= 1

    def test_node_stats_structure(self, loaded_corpus):
        """Each node stat should have type, count, distributions."""
        reset_cache()
        result = tools.search(
            "word", return_type="statistics", corpus=loaded_corpus
        )

        for key, stats in result["nodes"].items():
            assert "type" in stats
            assert "count" in stats
            assert "distributions" in stats
            assert stats["type"] == "word"
            assert stats["count"] == 5

    def test_aggregate_features_filters(self, loaded_corpus):
        """aggregate_features should limit which features are included."""
        reset_cache()
        result = tools.search(
            "word",
            return_type="statistics",
            aggregate_features=["pos"],
            corpus=loaded_corpus,
        )

        # Should only have 'pos' in distributions
        for key, stats in result["nodes"].items():
            dists = stats["distributions"]
            if dists:
                assert "pos" in dists
                # Should not have other features unless they match
                for feat in dists:
                    assert feat == "pos"

    def test_distribution_values_structure(self, loaded_corpus):
        """Distribution values should be list of {value, count} dicts."""
        reset_cache()
        result = tools.search(
            "word",
            return_type="statistics",
            aggregate_features=["pos"],
            corpus=loaded_corpus,
        )

        for key, stats in result["nodes"].items():
            if "pos" in stats["distributions"]:
                pos_dist = stats["distributions"]["pos"]
                assert isinstance(pos_dist, list)
                for item in pos_dist:
                    assert "value" in item
                    assert "count" in item
                    assert isinstance(item["count"], int)

    def test_distribution_sorted_by_frequency(self, loaded_corpus):
        """Distribution values should be sorted by count descending."""
        reset_cache()
        result = tools.search(
            "word",
            return_type="statistics",
            aggregate_features=["pos"],
            corpus=loaded_corpus,
        )

        for key, stats in result["nodes"].items():
            if "pos" in stats["distributions"]:
                pos_dist = stats["distributions"]["pos"]
                counts = [item["count"] for item in pos_dist]
                assert counts == sorted(counts, reverse=True)

    def test_top_n_limits_values(self, loaded_corpus):
        """top_n should limit number of distribution values."""
        reset_cache()
        result = tools.search(
            "word",
            return_type="statistics",
            aggregate_features=["pos"],
            top_n=1,
            corpus=loaded_corpus,
        )

        for key, stats in result["nodes"].items():
            if "pos" in stats["distributions"]:
                assert len(stats["distributions"]["pos"]) <= 1

    def test_group_by_section(self, loaded_corpus):
        """group_by_section should add section_distribution."""
        reset_cache()
        result = tools.search(
            "word",
            return_type="statistics",
            group_by_section=True,
            corpus=loaded_corpus,
        )

        assert "section_distribution" in result
        assert "book" in result["section_distribution"]

    def test_multi_atom_separate_stats(self, loaded_corpus):
        """Multi-atom queries should have stats per atom position."""
        reset_cache()
        result = tools.search(
            "phrase\n  word",
            return_type="statistics",
            corpus=loaded_corpus,
        )

        # Should have 2 entries (one for phrase, one for word)
        assert len(result["nodes"]) == 2

        # Check types are different
        types = [stats["type"] for stats in result["nodes"].values()]
        assert "phrase" in types
        assert "word" in types

    def test_specific_pos_distribution(self, loaded_corpus):
        """Verify actual POS distribution values."""
        reset_cache()
        result = tools.search(
            "word",
            return_type="statistics",
            aggregate_features=["pos"],
            corpus=loaded_corpus,
        )

        # Get the word stats
        word_stats = list(result["nodes"].values())[0]
        pos_dist = word_stats["distributions"].get("pos", [])

        # Extract values
        pos_values = {item["value"]: item["count"] for item in pos_dist}

        # Should have: 2 adjectives, 2 nouns, 1 interjection
        assert pos_values.get("adjective") == 2
        assert pos_values.get("noun") == 2
        assert pos_values.get("interjection") == 1


class TestReturnTypePassages:
    """Tests for return_type='passages'."""

    def test_returns_passages_list(self, loaded_corpus):
        """Passages should return list of passage dicts."""
        reset_cache()
        result = tools.search("word", return_type="passages", corpus=loaded_corpus)

        assert "passages" in result
        assert isinstance(result["passages"], list)

    def test_passage_structure(self, loaded_corpus):
        """Each passage should have reference, text, node, type."""
        reset_cache()
        result = tools.search("word", return_type="passages", corpus=loaded_corpus)

        for passage in result["passages"]:
            assert "reference" in passage
            assert "text" in passage
            assert "node" in passage
            assert "type" in passage

    def test_passage_text_content(self, loaded_corpus):
        """Passages should include actual text."""
        reset_cache()
        result = tools.search("word", return_type="passages", corpus=loaded_corpus)

        # At least some passages should have text
        has_text = any(p["text"] for p in result["passages"])
        assert has_text

    def test_passages_limit(self, loaded_corpus):
        """Limit should control number of passages."""
        reset_cache()
        result = tools.search(
            "word", return_type="passages", limit=2, corpus=loaded_corpus
        )

        assert len(result["passages"]) == 2

    def test_has_more_flag(self, loaded_corpus):
        """has_more should indicate if more passages exist."""
        reset_cache()
        result = tools.search(
            "word", return_type="passages", limit=2, corpus=loaded_corpus
        )

        assert result["has_more"] is True

        # Get all passages
        result_all = tools.search(
            "word", return_type="passages", limit=100, corpus=loaded_corpus
        )
        assert result_all["has_more"] is False

    def test_total_count_included(self, loaded_corpus):
        """Passages response should include total_count."""
        reset_cache()
        result = tools.search(
            "word", return_type="passages", limit=2, corpus=loaded_corpus
        )

        assert "total_count" in result
        assert result["total_count"] == 5


class TestStatisticsEdgeCases:
    """Edge case tests for statistics."""

    def test_empty_results_statistics(self, loaded_corpus):
        """Statistics with no results should return empty nodes."""
        reset_cache()
        result = tools.search(
            "word word=nonexistent",
            return_type="statistics",
            corpus=loaded_corpus,
        )

        assert result["total_count"] == 0
        assert result["nodes"] == {}

    def test_statistics_no_aggregate_features(self, loaded_corpus):
        """Without aggregate_features, should auto-select features."""
        reset_cache()
        result = tools.search(
            "word",
            return_type="statistics",
            corpus=loaded_corpus,
        )

        # Should have some distributions
        word_stats = list(result["nodes"].values())[0]
        assert len(word_stats["distributions"]) > 0

    def test_statistics_invalid_aggregate_feature(self, loaded_corpus):
        """Invalid feature in aggregate_features should be ignored."""
        reset_cache()
        result = tools.search(
            "word",
            return_type="statistics",
            aggregate_features=["nonexistent_feature"],
            corpus=loaded_corpus,
        )

        # Should not error, just have empty distributions
        word_stats = list(result["nodes"].values())[0]
        assert "nonexistent_feature" not in word_stats["distributions"]


class TestPassagesEdgeCases:
    """Edge case tests for passages."""

    def test_empty_results_passages(self, loaded_corpus):
        """Passages with no results should return empty list."""
        reset_cache()
        result = tools.search(
            "word word=nonexistent",
            return_type="passages",
            corpus=loaded_corpus,
        )

        assert result["total_count"] == 0
        assert result["passages"] == []

    def test_multi_atom_passages_uses_first(self, loaded_corpus):
        """Multi-atom queries should use first atom for passage."""
        reset_cache()
        result = tools.search(
            "phrase\n  word",
            return_type="passages",
            corpus=loaded_corpus,
        )

        # Passages should be for phrases (first atom)
        for passage in result["passages"]:
            assert passage["type"] == "phrase"
