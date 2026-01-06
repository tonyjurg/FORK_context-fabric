"""Integration tests for corpus info tools.

Tests list_loaded_corpora() and get_corpus_info() with a real corpus.
"""

import pytest

from cfabric_mcp import tools


class TestListLoadedCorpora:
    """Tests for listing loaded corpora."""

    def test_returns_loaded_corpus(self, loaded_corpus):
        """Should list the loaded corpus."""
        result = tools.list_loaded_corpora()

        assert "corpora" in result
        assert "current" in result
        assert loaded_corpus in result["corpora"]
        assert result["current"] == loaded_corpus

    def test_shows_current_corpus(self, loaded_corpus):
        """Current corpus should be set to loaded corpus."""
        result = tools.list_loaded_corpora()
        assert result["current"] == loaded_corpus


class TestGetCorpusInfo:
    """Tests for getting corpus information."""

    def test_returns_corpus_info(self, loaded_corpus):
        """Should return detailed corpus information."""
        result = tools.get_corpus_info(loaded_corpus)

        assert "name" in result
        assert "path" in result
        assert result["name"] == loaded_corpus

    def test_includes_node_types(self, loaded_corpus):
        """Should include node type information."""
        result = tools.get_corpus_info(loaded_corpus)

        assert "node_types" in result
        node_types = result["node_types"]

        # mini_corpus has: word, phrase, sentence
        type_names = [t["type"] for t in node_types]
        assert "word" in type_names
        assert "phrase" in type_names
        assert "sentence" in type_names

    def test_word_count(self, loaded_corpus):
        """Should show correct word count."""
        result = tools.get_corpus_info(loaded_corpus)

        node_types = {t["type"]: t for t in result["node_types"]}
        assert node_types["word"]["count"] == 5

    def test_phrase_count(self, loaded_corpus):
        """Should show correct phrase count."""
        result = tools.get_corpus_info(loaded_corpus)

        node_types = {t["type"]: t for t in result["node_types"]}
        assert node_types["phrase"]["count"] == 2

    def test_sentence_count(self, loaded_corpus):
        """Should show correct sentence count."""
        result = tools.get_corpus_info(loaded_corpus)

        node_types = {t["type"]: t for t in result["node_types"]}
        assert node_types["sentence"]["count"] == 1

    def test_includes_features(self, loaded_corpus):
        """Should include feature information."""
        result = tools.get_corpus_info(loaded_corpus)

        # Features are split into node_features and edge_features (as lists of names)
        assert "node_features" in result
        assert "edge_features" in result

        # mini_corpus has word, pos, number, score features
        assert "word" in result["node_features"]
        assert "pos" in result["node_features"]

    def test_default_corpus_is_current(self, loaded_corpus):
        """get_corpus_info() without args should use current corpus."""
        result = tools.get_corpus_info()

        assert result["name"] == loaded_corpus


class TestDescribeCorpus:
    """Tests for describe_corpus tool."""

    def test_returns_name(self, loaded_corpus):
        """Should return corpus name."""
        result = tools.describe_corpus(loaded_corpus)
        assert result["name"] == loaded_corpus

    def test_includes_node_types(self, loaded_corpus):
        """Should include node types with counts."""
        result = tools.describe_corpus(loaded_corpus)

        assert "node_types" in result
        types = {t["type"]: t for t in result["node_types"]}
        assert "word" in types
        assert types["word"]["count"] == 5

    def test_includes_features_metadata(self, loaded_corpus):
        """Features should be accessed via list_features, not describe_corpus."""
        # describe_corpus is now slimmed down - no features
        result = tools.describe_corpus(loaded_corpus)
        assert "features" not in result  # Use list_features() instead

        # list_features should return feature metadata
        features_result = tools.list_features(corpus=loaded_corpus)
        assert "features" in features_result
        assert len(features_result["features"]) > 0

        # Find pos feature
        pos_feat = next((f for f in features_result["features"] if f["name"] == "pos"), None)
        assert pos_feat is not None
        assert "name" in pos_feat
        assert "value_type" in pos_feat
        assert "description" in pos_feat
        # No sample_values in list_features (use describe_feature instead)
        assert "sample_values" not in pos_feat

    def test_no_search_hints(self, loaded_corpus):
        """Should not include search hints (removed for simplicity)."""
        result = tools.describe_corpus(loaded_corpus)

        assert "search_hints" not in result

    def test_describe_feature_returns_samples(self, loaded_corpus):
        """describe_feature should return sample values."""
        result = tools.describe_feature("pos", corpus=loaded_corpus)

        assert result["name"] == "pos"
        assert result["kind"] == "node"
        assert "sample_values" in result
        assert len(result["sample_values"]) > 0


class TestJSONSerialization:
    """Tests that tool outputs are JSON-serializable.

    This catches issues like numpy.int32 values that work in Python
    but fail when serialized to JSON for MCP responses.
    """

    def test_corpus_info_serializable(self, loaded_corpus):
        """get_corpus_info output must be JSON-serializable."""
        import json

        result = tools.get_corpus_info(loaded_corpus)
        # This will raise TypeError if any values are not serializable
        json.dumps(result)

    def test_describe_corpus_serializable(self, loaded_corpus):
        """describe_corpus output must be JSON-serializable."""
        import json

        result = tools.describe_corpus(loaded_corpus)
        # This will raise TypeError if any values are not serializable
        json.dumps(result)

    def test_search_results_serializable(self, loaded_corpus):
        """search results must be JSON-serializable."""
        import json

        result = tools.search("word", corpus=loaded_corpus)
        json.dumps(result)

    def test_search_statistics_serializable(self, loaded_corpus):
        """search statistics must be JSON-serializable."""
        import json

        result = tools.search("word", return_type="statistics", corpus=loaded_corpus)
        json.dumps(result)

    def test_search_passages_serializable(self, loaded_corpus):
        """search passages must be JSON-serializable."""
        import json

        result = tools.search("word", return_type="passages", corpus=loaded_corpus)
        json.dumps(result)

    def test_get_node_features_serializable(self, loaded_corpus):
        """get_node_features output must be JSON-serializable."""
        import json

        result = tools.get_node_features([1, 2], ["pos", "word"], corpus=loaded_corpus)
        json.dumps(result)
