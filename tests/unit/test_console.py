"""Unit tests for :mod:`src.core.console` (stdout/stderr compatibility)."""

from __future__ import annotations

import sys

import pytest

from src.core.console import ensure_utf8_stdio


class _RecordingStream:
    """Minimal stdout-like stream that records ``reconfigure`` calls."""

    def __init__(self, *, fail: bool = False) -> None:
        self.calls: list[dict] = []
        self._fail = fail

    def reconfigure(self, **kwargs) -> None:
        self.calls.append(kwargs)
        if self._fail:
            raise ValueError("stream is closed")


class _NoReconfigureStream:
    """Stream without a ``reconfigure`` attribute (like some test captures)."""

    def write(self, data: str) -> int:  # pragma: no cover - trivial
        return len(data)


@pytest.mark.unit
def test_sets_utf8_on_both_streams(monkeypatch):
    out, err = _RecordingStream(), _RecordingStream()
    monkeypatch.setattr(sys, "stdout", out)
    monkeypatch.setattr(sys, "stderr", err)

    ensure_utf8_stdio()

    assert out.calls == [{"encoding": "utf-8", "errors": "replace"}]
    assert err.calls == [{"encoding": "utf-8", "errors": "replace"}]


@pytest.mark.unit
def test_custom_errors_policy_is_forwarded(monkeypatch):
    out = _RecordingStream()
    monkeypatch.setattr(sys, "stdout", out)
    monkeypatch.setattr(sys, "stderr", out)

    ensure_utf8_stdio(errors="backslashreplace")

    assert out.calls == [
        {"encoding": "utf-8", "errors": "backslashreplace"},
        {"encoding": "utf-8", "errors": "backslashreplace"},
    ]


@pytest.mark.unit
def test_stream_without_reconfigure_is_skipped(monkeypatch):
    monkeypatch.setattr(sys, "stdout", _NoReconfigureStream())
    monkeypatch.setattr(sys, "stderr", _NoReconfigureStream())

    ensure_utf8_stdio()  # не должно бросать исключение


@pytest.mark.unit
def test_closed_stream_is_tolerated(monkeypatch):
    monkeypatch.setattr(sys, "stdout", _RecordingStream(fail=True))
    monkeypatch.setattr(sys, "stderr", _RecordingStream(fail=True))

    ensure_utf8_stdio()  # ValueError внутри потока не должен всплывать


@pytest.mark.unit
def test_is_idempotent(monkeypatch):
    out = _RecordingStream()
    monkeypatch.setattr(sys, "stdout", out)
    monkeypatch.setattr(sys, "stderr", out)

    ensure_utf8_stdio()
    ensure_utf8_stdio()

    assert len(out.calls) == 4
