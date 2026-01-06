"""Unit tests for cfabric.describe module."""

import pytest
from unittest.mock import MagicMock, patch

from cfabric.describe import (
    CorpusOverview,
    CorpusDescription,
    FeatureDescription,
    FeatureCatalogEntry,
    TextFormatSample,
    TextFormatInfo,
    TextRepresentationInfo,
)


class TestTextFormatSample:
    """Tests for TextFormatSample dataclass."""

    def test_to_dict(self):
        sample = TextFormatSample(original="אָדָם", transliterated=">DM")
        result = sample.to_dict()
        assert result == {"original": "אָדָם", "transliterated": ">DM"}


class TestTextFormatInfo:
    """Tests for TextFormatInfo dataclass."""

    def test_to_dict_with_samples(self):
        samples = [
            TextFormatSample(original="א", transliterated=">"),
            TextFormatSample(original="ב", transliterated="B"),
        ]
        info = TextFormatInfo(
            name="lex-plain",
            original_spec="{lex}",
            transliteration_spec="{lex}",
            samples=samples,
            unique_characters=2,
            total_samples=2,
        )
        result = info.to_dict()
        assert result["name"] == "lex-plain"
        assert result["original_script"] == "{lex}"
        assert result["transliteration"] == "{lex}"
        assert len(result["samples"]) == 2
        assert result["unique_characters"] == 2
        assert result["total_samples"] == 2

    def test_to_dict_empty_samples(self):
        info = TextFormatInfo(
            name="text-plain",
            original_spec="{text}",
            transliteration_spec="{text}",
        )
        result = info.to_dict()
        assert result["samples"] == []
        assert result["unique_characters"] == 0


class TestTextRepresentationInfo:
    """Tests for TextRepresentationInfo dataclass."""

    def test_to_dict(self):
        info = TextRepresentationInfo(
            description="Test description",
            formats=[
                TextFormatInfo(
                    name="lex-plain",
                    original_spec="{lex}",
                    transliteration_spec="{lex}",
                )
            ],
        )
        result = info.to_dict()
        assert result["description"] == "Test description"
        assert len(result["formats"]) == 1
        assert result["formats"][0]["name"] == "lex-plain"


class TestFeatureCatalogEntry:
    """Tests for FeatureCatalogEntry dataclass."""

    def test_to_dict(self):
        entry = FeatureCatalogEntry(
            name="sp",
            kind="node",
            value_type="str",
            description="Part of speech",
        )
        result = entry.to_dict()
        assert result == {
            "name": "sp",
            "kind": "node",
            "value_type": "str",
            "description": "Part of speech",
        }

    def test_to_dict_empty_description(self):
        entry = FeatureCatalogEntry(
            name="lex",
            kind="node",
            value_type="str",
        )
        result = entry.to_dict()
        assert result["description"] == ""


class TestCorpusOverview:
    """Tests for CorpusOverview dataclass."""

    def test_to_dict(self):
        overview = CorpusOverview(
            name="test_corpus",
            node_types=[
                {"type": "word", "count": 100, "is_slot_type": True},
                {"type": "phrase", "count": 20, "is_slot_type": False},
            ],
            sections={"levels": ["book", "chapter", "verse"]},
        )
        result = overview.to_dict()
        assert result["name"] == "test_corpus"
        assert len(result["node_types"]) == 2
        assert result["node_types"][0]["type"] == "word"
        assert result["sections"]["levels"] == ["book", "chapter", "verse"]


class TestFeatureDescription:
    """Tests for FeatureDescription dataclass."""

    def test_to_dict_node_feature(self):
        desc = FeatureDescription(
            name="sp",
            kind="node",
            value_type="str",
            description="Part of speech",
            node_types=["word"],
            unique_values=15,
            sample_values=[
                {"value": "verb", "count": 100},
                {"value": "noun", "count": 80},
            ],
        )
        result = desc.to_dict()
        assert result["name"] == "sp"
        assert result["kind"] == "node"
        assert result["node_types"] == ["word"]
        assert result["unique_values"] == 15
        assert len(result["sample_values"]) == 2

    def test_to_dict_edge_feature(self):
        desc = FeatureDescription(
            name="mother",
            kind="edge",
            value_type="",
            description="Syntactic parent",
            node_types=["phrase", "clause"],
            has_values=False,
        )
        result = desc.to_dict()
        assert result["kind"] == "edge"
        assert result["has_values"] is False

    def test_to_dict_with_error(self):
        desc = FeatureDescription(
            name="nonexistent",
            kind="unknown",
            error="Feature 'nonexistent' not found",
        )
        result = desc.to_dict()
        assert "error" in result
        assert result["error"] == "Feature 'nonexistent' not found"
        assert "node_types" not in result
        assert "sample_values" not in result


class TestCorpusDescription:
    """Tests for CorpusDescription dataclass."""

    def test_to_dict(self):
        desc = CorpusDescription(
            name="test_corpus",
            node_types=[{"type": "word", "count": 100, "is_slot_type": True}],
            sections={"levels": ["book", "chapter"]},
            text_representations=TextRepresentationInfo(description="Test"),
            features=[{"name": "sp", "value_type": "str"}],
            edge_features=[{"name": "mother", "value_type": ""}],
        )
        result = desc.to_dict()
        assert result["name"] == "test_corpus"
        assert len(result["node_types"]) == 1
        assert result["sections"]["levels"] == ["book", "chapter"]
        assert result["text_representations"]["description"] == "Test"
        assert len(result["features"]) == 1
        assert len(result["edge_features"]) == 1
