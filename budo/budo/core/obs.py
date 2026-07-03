"""Optional tracing addon. The meter (core/usage.py) is always on and costs
nothing; this file is the seam for real span-level observability when you
want it — one env var, one optional pip install, zero code changes.

    pip install logfire            # or: pip install 'budo[obs]'
    export BUDO_OBS=logfire
    budo logs "..."

What you get: a span per LLM HTTP call (latency, status, request/response
sizes) via logfire's httpx instrumentation. Where it goes:

- LOGFIRE_TOKEN set        → the hosted Logfire UI (free tier is plenty)
- OTEL_EXPORTER_OTLP_ENDPOINT set → any OpenTelemetry backend you run —
  including a collector in the dojo's own monitoring namespace
- neither                  → spans render in your console; still useful

Logfire is OpenTelemetry under the hood, so nothing here locks you in.
If BUDO_OBS is unset or the package isn't installed, all of this is a no-op.
"""
from __future__ import annotations

import os
import sys


def init() -> bool:
    """Call once at CLI start. Returns True if tracing is live."""
    backend = os.environ.get("BUDO_OBS", "").strip().lower()
    if backend in ("", "off", "0", "none"):
        return False
    if backend != "logfire":
        print(f"obs: unknown BUDO_OBS={backend!r} (supported: logfire) — tracing off",
              file=sys.stderr)
        return False
    try:
        import logfire
    except ImportError:
        print("obs: BUDO_OBS=logfire but the package is missing — "
              "pip install logfire (tracing off, everything else works)", file=sys.stderr)
        return False

    logfire.configure(
        service_name="budo",
        send_to_logfire="if-token-present",  # console/OTLP-only unless LOGFIRE_TOKEN is set
    )
    logfire.instrument_httpx()  # every provider POST becomes a span — no code changes
    print("obs: logfire tracing on"
          + (" → logfire UI" if os.environ.get("LOGFIRE_TOKEN") else
             " → OTLP" if os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT") else " → console"),
          file=sys.stderr)
    return True
