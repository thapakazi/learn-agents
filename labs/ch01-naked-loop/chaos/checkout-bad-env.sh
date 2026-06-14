#!/usr/bin/env bash
# Ch1 chaos: a tiny env-var typo on the checkoutservice deployment.
#
# Symptom: every PlaceOrder dies in payment with a DNS resolution error.
#          The pod stays Running and Ready (probes are gRPC against its own
#          port). Only the customer flow exposes the break — and the error
#          text lands in `frontend`'s logs, not checkoutservice's.
# Cause:   PAYMENT_SERVICE_ADDR=paymetnservce:50051 — a tired transposition
#          applied during a "config cleanup" by someone who is now on PTO.
set -euo pipefail

kubectl -n shop set env deployment/checkoutservice \
  PAYMENT_SERVICE_ADDR=paymetnservce:50051

echo "💥 chaos applied. Rollout in ~30s. Then watch checkout errors appear."
