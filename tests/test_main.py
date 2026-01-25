"""Tests for main module."""

import pytest

from src.main import hello


def test_hello_default():
    """Test hello with default argument."""
    assert hello() == "Hello, World!"


def test_hello_with_name():
    """Test hello with custom name."""
    assert hello("Alice") == "Hello, Alice!"


@pytest.mark.parametrize(
    "name,expected",
    [
        ("Bob", "Hello, Bob!"),
        ("", "Hello, !"),
        ("123", "Hello, 123!"),
    ],
)
def test_hello_parametrized(name: str, expected: str):
    """Test hello with various inputs."""
    assert hello(name) == expected
