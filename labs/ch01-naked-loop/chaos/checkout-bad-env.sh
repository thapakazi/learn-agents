#!/usr/bin/env bash
# Ch1 chaos: a tiny env-var typo on the checkoutservice deployment.
#
# Symptom: every PlaceOrder dies in payment with a DNS resolution error.
# Cause:   PAYMENT_SERVICE_ADDR=paymentservice-typo:50051 — applied during a
#          "config cleanup" by someone who is now on PTO.
#
# The original scenario was a NetworkPolicy that ate DNS for checkout, but
# kindnet (the default kind CNI) does not enforce NetworkPolicy, so the
# manifest was a no-op on a stock cluster. This env-typo break reproduces the
# same diagnostic chain (symptom in logs, cause two hops away in deployment
# config) on any CNI. Bring back the netpol version in a later chapter once
# we move learners to a CNI that enforces it.
set -euo pipefail

kubectl -n shop set env deployment/checkoutservice \
  PAYMENT_SERVICE_ADDR=paymetnservce:50051

echo "💥 chaos applied. Rollout in ~30s. Then watch checkout errors appear."
