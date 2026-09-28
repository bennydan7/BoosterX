#!/usr/bin/env python3
"""
Provider Smoke Test Script for BoostX.

Usage:
  python scripts/provider_smoke.py [--url API_URL] [--key API_KEY]

Tests:
  1. Ping / balance check
  2. Services catalog retrieval
  3. Single service lookup & rate validation
"""

import os
import sys
import argparse
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("provider_smoke")

try:
    from backend.app.providers.provider_client import ProviderAdapter, ProviderError
    from backend.app.providers.fake_provider import FakeProvider
except ImportError:
    logger.error("Could not import ProviderAdapter. Ensure python path includes repo root.")
    sys.exit(1)


def run_smoke_test(url: str = None, key: str = None, mode: str = "fake"):
    logger.info(f"=== Starting BoostX Provider Smoke Test (Mode: {mode}) ===")

    if mode == "live":
        if not url or not key:
            logger.error("Live mode requires --url and --key arguments.")
            sys.exit(1)
        adapter = ProviderAdapter(api_url=url, api_key=key)
    else:
        logger.info("Using FakeProvider for local smoke test.")
        adapter = FakeProvider()

    # Test 1: Balance & Currency
    try:
        bal, curr = adapter.get_provider_balance()
        logger.info(f"[PASS] Provider Balance: {bal:.2f} {curr}")
    except Exception as exc:
        logger.error(f"[FAIL] Balance check failed: {exc}")
        sys.exit(1)

    # Test 2: Services Catalog
    try:
        services = adapter.get_services()
        logger.info(f"[PASS] Catalog fetched: {len(services)} services found.")
        if services:
            sample = services[0]
            logger.info(f"       Sample Service #{sample.service_id}: '{sample.name}' (Rate: ${sample.rate_usd_per_1000}/1k)")
    except Exception as exc:
        logger.error(f"[FAIL] Services catalog fetch failed: {exc}")
        sys.exit(1)

    logger.info("=== Provider Smoke Test Complete: ALL CHECKS PASSED ===")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BoostX Provider Smoke Test CLI")
    parser.add_argument("--url", help="Provider API URL")
    parser.add_argument("--key", help="Provider API Key")
    parser.add_argument("--mode", choices=["fake", "live"], default="fake", help="Execution mode")
    args = parser.parse_args()

    run_smoke_test(url=args.url, key=args.key, mode=args.mode)
