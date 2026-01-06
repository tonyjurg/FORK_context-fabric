"""Integration tests for cfabric.describe module.

Tests the describe functions against a real corpus.
"""

import pytest

from cfabric.describe import (
    describe_corpus_overview,
    describe_corpus,
    describe_feature,
    describe_features,
    describe_text_formats,
    list_features,
    get_feature_otypes,
    get_all_feature_otypes,
    CorpusOverview,
    CorpusDescription,
    FeatureDescription,
    FeatureCatalogEntry,
    TextRepresentationInfo,
)


@pytest.fixture
def corpus_api(loaded_api):
    """Use the loaded_api fixture from conftest."""
    return loaded_api


class TestDescribeCorpusOverview:
    """Tests for describe_corpus_overview function."""

    def test_returns_corpus_overview(self, corpus_api):
        result = describe_corpus_overview(corpus_api, "test")
        assert isinstance(result, CorpusOverview)
        assert result.name == "test"

    def test_includes_node_types(self, corpus_api):
        result = describe_corpus_overview(corpus_api, "test")
        assert len(result.node_types) > 0
        # Should have at least word type
        type_names = [nt["type"] for nt in result.node_types]
        assert "word" in type_names

    def test_node_types_have_counts(self, corpus_api):
        result = describe_corpus_overview(corpus_api, "test")
        for nt in result.node_types:
            assert "type" in nt
            assert "count" in nt
            assert "is_slot_type" in nt
            assert nt["count"] > 0

    def test_includes_sections(self, corpus_api):
        result = describe_corpus_overview(corpus_api, "test")
        assert "levels" in result.sections

    def test_to_dict_serializable(self, corpus_api):
        import json
        result = describe_corpus_overview(corpus_api, "test")
        # Should not raise
        json.dumps(result.to_dict())


class TestDescribeCorpus:
    """Tests for describe_corpus function (full description)."""

    def test_returns_corpus_description(self, corpus_api):
        result = describe_corpus(corpus_api, "test")
        assert isinstance(result, CorpusDescription)

    def test_includes_features(self, corpus_api):
        result = describe_corpus(corpus_api, "test")
        assert len(result.features) > 0

    def test_includes_text_representations(self, corpus_api):
        result = describe_corpus(corpus_api, "test")
        assert isinstance(result.text_representations, TextRepresentationInfo)


class TestListFeatures:
    """Tests for list_features function."""

    def test_returns_feature_list(self, corpus_api):
        result = list_features(corpus_api)
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(f, FeatureCatalogEntry) for f in result)

    def test_features_have_required_fields(self, corpus_api):
        result = list_features(corpus_api)
        for f in result:
            assert f.name
            assert f.kind in ("node", "edge")
            assert f.value_type is not None

    def test_filter_by_kind_node(self, corpus_api):
        result = list_features(corpus_api, kind="node")
        assert all(f.kind == "node" for f in result)

    def test_filter_by_kind_edge(self, corpus_api):
        result = list_features(corpus_api, kind="edge")
        assert all(f.kind == "edge" for f in result)

    def test_filter_by_node_types(self, corpus_api):
        # Filter to features that apply to "word" nodes
        result = list_features(corpus_api, node_types=["word"])
        # Should return some features (at least pos, lex, etc.)
        assert len(result) > 0


class TestDescribeFeature:
    """Tests for describe_feature function."""

    def test_returns_feature_description(self, corpus_api):
        # Get a known feature name
        features = list_features(corpus_api, kind="node")
        if features:
            feature_name = features[0].name
            result = describe_feature(corpus_api, feature_name)
            assert isinstance(result, FeatureDescription)
            assert result.name == feature_name

    def test_includes_sample_values(self, corpus_api):
        features = list_features(corpus_api, kind="node")
        if features:
            feature_name = features[0].name
            result = describe_feature(corpus_api, feature_name)
            assert result.sample_values is not None

    def test_includes_node_types(self, corpus_api):
        features = list_features(corpus_api, kind="node")
        if features:
            feature_name = features[0].name
            result = describe_feature(corpus_api, feature_name)
            assert result.node_types is not None
            assert len(result.node_types) > 0

    def test_nonexistent_feature_returns_error(self, corpus_api):
        result = describe_feature(corpus_api, "nonexistent_feature_xyz")
        assert result.error is not None

    def test_sample_limit_respected(self, corpus_api):
        features = list_features(corpus_api, kind="node")
        if features:
            feature_name = features[0].name
            result = describe_feature(corpus_api, feature_name, sample_limit=5)
            assert len(result.sample_values) <= 5


class TestDescribeFeatures:
    """Tests for describe_features function (batch)."""

    def test_returns_dict_of_descriptions(self, corpus_api):
        features = list_features(corpus_api, kind="node")
        if len(features) >= 2:
            names = [features[0].name, features[1].name]
            result = describe_features(corpus_api, names)
            assert isinstance(result, dict)
            assert len(result) == 2
            assert all(isinstance(v, FeatureDescription) for v in result.values())


class TestDescribeTextFormats:
    """Tests for describe_text_formats function."""

    def test_returns_text_representation_info(self, corpus_api):
        result = describe_text_formats(corpus_api)
        assert isinstance(result, TextRepresentationInfo)

    def test_has_description(self, corpus_api):
        result = describe_text_formats(corpus_api)
        assert result.description is not None


class TestGetFeatureOtypes:
    """Tests for get_feature_otypes function."""

    def test_returns_list_of_types(self, corpus_api):
        features = list_features(corpus_api, kind="node")
        if features:
            feature_name = features[0].name
            result = get_feature_otypes(corpus_api, feature_name)
            assert isinstance(result, list)

    def test_nonexistent_feature_returns_empty(self, corpus_api):
        result = get_feature_otypes(corpus_api, "nonexistent_xyz")
        assert result == []


class TestGetAllFeatureOtypes:
    """Tests for get_all_feature_otypes function."""

    def test_returns_dict(self, corpus_api):
        result = get_all_feature_otypes(corpus_api)
        assert isinstance(result, dict)

    def test_contains_all_features(self, corpus_api):
        features = list_features(corpus_api, kind="node")
        result = get_all_feature_otypes(corpus_api)
        for f in features:
            assert f.name in result
