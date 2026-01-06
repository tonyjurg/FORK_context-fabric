"""Integration tests for multi-corpus functionality.

Tests tools with multiple corpora loaded simultaneously to verify:
1. All corpora are listed correctly
2. Corpus-specific queries return data from the correct corpus
3. Data isolation between corpora is maintained

Test corpora:
- corpus_a: 5 words (hello, beautiful, world, good, morning), 2 phrases, 1 sentence
- corpus_b: 3 words (alpha, beta, gamma), 1 phrase, 1 sentence
- corpus_c: 4 words (red, green, blue, yellow), 2 phrases, 1 sentence
"""

import pytest

from cfabric_mcp import tools


class TestMultiCorpusListing:
    """Tests for listing multiple corpora."""

    def test_lists_all_three_corpora(self, multi_corpus):
        """Should list all three loaded corpora."""
        corpus_a, corpus_b, corpus_c = multi_corpus
        result = tools.list_loaded_corpora()

        assert corpus_a in result["corpora"]
        assert corpus_b in result["corpora"]
        assert corpus_c in result["corpora"]
        assert len(result["corpora"]) == 3

    def test_current_is_last_loaded(self, multi_corpus):
        """Current corpus should be the last one loaded (corpus_c)."""
        corpus_a, corpus_b, corpus_c = multi_corpus
        result = tools.list_loaded_corpora()

        assert result["current"] == corpus_c


class TestMultiCorpusInfo:
    """Tests for getting info from specific corpora."""

    def test_corpus_a_info(self, multi_corpus):
        """corpus_a should have 5 words, 2 phrases, 1 sentence."""
        corpus_a, corpus_b, corpus_c = multi_corpus
        result = tools.get_corpus_info(corpus_a)

        assert result["name"] == corpus_a
        node_types = {t["type"]: t["count"] for t in result["node_types"]}
        assert node_types["word"] == 5
        assert node_types["phrase"] == 2
        assert node_types["sentence"] == 1

    def test_corpus_b_info(self, multi_corpus):
        """corpus_b should have 3 words, 1 phrase, 1 sentence."""
        corpus_a, corpus_b, corpus_c = multi_corpus
        result = tools.get_corpus_info(corpus_b)

        assert result["name"] == corpus_b
        node_types = {t["type"]: t["count"] for t in result["node_types"]}
        assert node_types["word"] == 3
        assert node_types["phrase"] == 1
        assert node_types["sentence"] == 1

    def test_corpus_c_info(self, multi_corpus):
        """corpus_c should have 4 words, 2 phrases, 1 sentence."""
        corpus_a, corpus_b, corpus_c = multi_corpus
        result = tools.get_corpus_info(corpus_c)

        assert result["name"] == corpus_c
        node_types = {t["type"]: t["count"] for t in result["node_types"]}
        assert node_types["word"] == 4
        assert node_types["phrase"] == 2
        assert node_types["sentence"] == 1

    def test_default_uses_current(self, multi_corpus):
        """Default should return corpus_c (last loaded)."""
        corpus_a, corpus_b, corpus_c = multi_corpus
        result = tools.get_corpus_info()

        assert result["name"] == corpus_c


class TestMultiCorpusSearchIsolation:
    """Tests that search queries are isolated between corpora."""

    def test_search_word_counts_differ(self, multi_corpus):
        """Searching for 'word' returns different counts per corpus."""
        corpus_a, corpus_b, corpus_c = multi_corpus

        result_a = tools.search("word", corpus=corpus_a)
        result_b = tools.search("word", corpus=corpus_b)
        result_c = tools.search("word", corpus=corpus_c)

        assert len(result_a["results"]) == 5
        assert len(result_b["results"]) == 3
        assert len(result_c["results"]) == 4

    def test_search_with_constraint_isolated(self, multi_corpus):
        """Search with feature constraint should be corpus-specific."""
        corpus_a, corpus_b, corpus_c = multi_corpus

        # Search for nouns in each corpus
        result_a = tools.search("word pos=noun", corpus=corpus_a)
        result_b = tools.search("word pos=noun", corpus=corpus_b)
        result_c = tools.search("word pos=noun", corpus=corpus_c)

        # corpus_a has 2 nouns (world, morning)
        # corpus_b has 2 nouns (alpha, gamma)
        # corpus_c has 0 nouns (all adjectives)
        assert len(result_a["results"]) == 2
        assert len(result_b["results"]) == 2
        assert len(result_c["results"]) == 0

    def test_search_adjectives_per_corpus(self, multi_corpus):
        """Search for adjectives returns corpus-specific counts."""
        corpus_a, corpus_b, corpus_c = multi_corpus

        result_a = tools.search("word pos=adjective", corpus=corpus_a)
        result_b = tools.search("word pos=adjective", corpus=corpus_b)
        result_c = tools.search("word pos=adjective", corpus=corpus_c)

        # corpus_a has 2 adjectives (beautiful, good)
        # corpus_b has 0 adjectives
        # corpus_c has 4 adjectives (all words)
        assert len(result_a["results"]) == 2
        assert len(result_b["results"]) == 0
        assert len(result_c["results"]) == 4


class TestMultiCorpusDescribeCorpus:
    """Tests for describe_corpus with multiple corpora."""

    def test_describe_corpus_returns_correct_corpus(self, multi_corpus):
        """describe_corpus should return data for the specified corpus."""
        corpus_a, corpus_b, corpus_c = multi_corpus

        result_a = tools.describe_corpus(corpus=corpus_a)
        result_b = tools.describe_corpus(corpus=corpus_b)
        result_c = tools.describe_corpus(corpus=corpus_c)

        assert result_a["name"] == corpus_a
        assert result_b["name"] == corpus_b
        assert result_c["name"] == corpus_c

    def test_describe_corpus_node_types_differ(self, multi_corpus):
        """Each corpus should have different node type counts."""
        corpus_a, corpus_b, corpus_c = multi_corpus

        result_a = tools.describe_corpus(corpus=corpus_a)
        result_b = tools.describe_corpus(corpus=corpus_b)
        result_c = tools.describe_corpus(corpus=corpus_c)

        def get_word_count(result):
            for nt in result["node_types"]:
                if nt["type"] == "word":
                    return nt["count"]
            return 0

        assert get_word_count(result_a) == 5
        assert get_word_count(result_b) == 3
        assert get_word_count(result_c) == 4


class TestMultiCorpusErrorHandling:
    """Tests for error handling with invalid corpus names."""

    def test_invalid_corpus_in_search(self, multi_corpus):
        """Search with invalid corpus should raise error."""
        with pytest.raises(KeyError):
            tools.search("word", corpus="nonexistent")

    def test_invalid_corpus_in_describe(self, multi_corpus):
        """describe_corpus with invalid corpus should raise error."""
        with pytest.raises(KeyError):
            tools.describe_corpus(corpus="nonexistent")
