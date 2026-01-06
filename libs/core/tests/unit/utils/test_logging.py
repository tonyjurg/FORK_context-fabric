"""Unit tests for cfabric.utils.logging module.

This module tests the logging configuration utilities.
"""

import logging
import pytest

from cfabric.utils.logging import (
    silentConvert,
    configure_logging,
    set_logging_level,
    VERBOSE,
    AUTO,
    TERSE,
    DEEP,
    SILENT_D,
    LEVEL_MAP,
)


class TestSilentConvert:
    """Tests for silentConvert() function."""

    def test_none_returns_default(self):
        """None should return default silent level."""
        assert silentConvert(None) == SILENT_D

    def test_false_returns_verbose(self):
        """False should return VERBOSE."""
        assert silentConvert(False) == VERBOSE

    def test_true_returns_deep(self):
        """True should return DEEP."""
        assert silentConvert(True) == DEEP

    def test_valid_strings(self):
        """Valid string levels should be returned as-is."""
        assert silentConvert(VERBOSE) == VERBOSE
        assert silentConvert(AUTO) == AUTO
        assert silentConvert(TERSE) == TERSE
        assert silentConvert(DEEP) == DEEP

    def test_invalid_string(self):
        """Invalid strings should return default silent level."""
        assert silentConvert("invalid") == SILENT_D


class TestConfigureLogging:
    """Tests for configure_logging() function."""

    def test_configures_cfabric_logger(self):
        """Should configure the cfabric logger."""
        configure_logging(silent=AUTO)
        logger = logging.getLogger("cfabric")
        assert logger.level == logging.INFO

    def test_verbose_sets_debug(self):
        """VERBOSE should set DEBUG level."""
        configure_logging(silent=VERBOSE)
        logger = logging.getLogger("cfabric")
        assert logger.level == logging.DEBUG

    def test_deep_sets_error(self):
        """DEEP should set ERROR level."""
        configure_logging(silent=DEEP)
        logger = logging.getLogger("cfabric")
        assert logger.level == logging.ERROR

    def test_terse_sets_warning(self):
        """TERSE should set WARNING level."""
        configure_logging(silent=TERSE)
        logger = logging.getLogger("cfabric")
        assert logger.level == logging.WARNING


class TestSetLoggingLevel:
    """Tests for set_logging_level() function."""

    def test_changes_level(self):
        """Should change the logging level."""
        configure_logging(silent=AUTO)
        set_logging_level(DEEP)
        logger = logging.getLogger("cfabric")
        assert logger.level == logging.ERROR


class TestLevelMap:
    """Tests for LEVEL_MAP constant."""

    def test_all_levels_mapped(self):
        """All silent levels should be in LEVEL_MAP."""
        assert VERBOSE in LEVEL_MAP
        assert AUTO in LEVEL_MAP
        assert TERSE in LEVEL_MAP
        assert DEEP in LEVEL_MAP

    def test_correct_mapping(self):
        """Levels should map to correct Python logging levels."""
        assert LEVEL_MAP[VERBOSE] == logging.DEBUG
        assert LEVEL_MAP[AUTO] == logging.INFO
        assert LEVEL_MAP[TERSE] == logging.WARNING
        assert LEVEL_MAP[DEEP] == logging.ERROR
