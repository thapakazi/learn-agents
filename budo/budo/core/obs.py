"""Optional tracing addon — plain OpenTelemetry, self-hosted backend.

The meter (core/usage.py) is always on and costs nothing. This file adds
span-level tracing when you want to *see* a run: one span per LLM call,
carrying the model name, token usage, and latency, in a UI built for
debugging agent loops.

The dojo backend is Phoenix (arize-ai/phoenix) — a single container that
serves both the UI and an OTLP collector on port 6006, deployed into the
lab cluster next to Prometheus and Loki (Ch0: `just obs`, then `just phoenix`
to port-forward). No accounts, no SaaS; destroyable with the cluster.

    pip install 'budo[obs]'        # opentelemetry-sdk + OTLP exporter (Ch0: just deps-obs)
    export BUDO_OBS=phoenix        # → http://localhost:6006/v1/traces (the port-forward)
    budo logs "..."                # open http://localhost:6006 and watch the run

Other values:
    BUDO_OBS=otlp      → wherever OTEL_EXPORTER_OTLP_TRACES_ENDPOINT points
                         (any OpenTelemetry backend: Tempo, Jaeger, a collector...)
    BUDO_OBS=console   → spans printed to stderr; no server needed
    BUDO_OBS unset     → everything in this file is a no-op

It's all standard OTLP — swapping backends is an env var, never a code change.
"""
from __future__ import annotations

import os
import sys
from contextlib import contextmanager

_tracer = None  # set by init() when tracing is live

PHOENIX_DEFAULT = "http://localhost:6006/v1/traces"


def _reachable(endpoint: str, timeout: float = 1.0) -> bool:
    """Cheap TCP check so a missing backend costs one sentence, not a
    retry-storm of export warnings at CLI exit."""
    import socket
    from urllib.parse import urlparse
    u = urlparse(endpoint)
    try:
        with socket.create_connection((u.hostname, u.port or 80), timeout=timeout):
            return True
    except OSError:
        return False


def init() -> bool:
    """Call once at CLI start. Returns True if tracing is live."""
    global _tracer
    backend = os.environ.get("BUDO_OBS", "").strip().lower()
    if backend in ("", "off", "0", "none"):
        return False
    if backend not in ("phoenix", "otlp", "console"):
        print(f"obs: unknown BUDO_OBS={backend!r} (supported: phoenix, otlp, console) "
              "— tracing off", file=sys.stderr)
        return False

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError:
        print("obs: BUDO_OBS set but OpenTelemetry is missing — "
              "pip install 'budo[obs]' (tracing off, everything else works)", file=sys.stderr)
        return False

    if backend == "console":
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter
        exporter = ConsoleSpanExporter(out=sys.stderr)
        where = "console"
    else:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        if backend == "phoenix":
            endpoint = os.environ.get("BUDO_OBS_ENDPOINT", PHOENIX_DEFAULT)
            if not _reachable(endpoint):
                print(f"obs: phoenix not answering at {endpoint} — is the `just phoenix` "
                      "port-forward running? (tracing off, everything else works)",
                      file=sys.stderr)
                return False
        else:  # otlp — honor the standard OTel env vars
            endpoint = (os.environ.get("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT")
                        or os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"))
            if not endpoint:
                print("obs: BUDO_OBS=otlp needs OTEL_EXPORTER_OTLP_ENDPOINT — tracing off",
                      file=sys.stderr)
                return False
        exporter = OTLPSpanExporter(endpoint=endpoint)
        where = endpoint

    provider = TracerProvider(resource=Resource.create({"service.name": "budo"}))
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    _tracer = trace.get_tracer("budo")
    print(f"obs: tracing on → {where}", file=sys.stderr)
    return True


@contextmanager
def llm_span(model: str):
    """Wrap one LLM call. Yields the span (or None when tracing is off);
    the caller decorates it via set_usage(). Zero cost when disabled."""
    if _tracer is None:
        yield None
        return
    with _tracer.start_as_current_span(f"chat {model}") as span:
        span.set_attribute("gen_ai.system", "openai-compatible")
        span.set_attribute("gen_ai.request.model", model)
        yield span


def set_usage(span, usage: dict | None) -> None:
    """Stamp the usage block onto the span (OTel gen_ai semantic conventions)."""
    if span is None or not usage:
        return
    span.set_attribute("gen_ai.usage.input_tokens", usage.get("prompt_tokens", 0) or 0)
    span.set_attribute("gen_ai.usage.output_tokens", usage.get("completion_tokens", 0) or 0)
