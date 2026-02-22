"""Pytest configuration and shared fixtures."""

import pytest
import os


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    os.environ.setdefault("ANTHROPIC_API_KEY", "test-key-for-testing")
    yield
    if "ANTHROPIC_API_KEY" in os.environ and os.environ["ANTHROPIC_API_KEY"] == "test-key-for-testing":
        del os.environ["ANTHROPIC_API_KEY"]
