"""Minimal server-side Shopify Admin GraphQL client for a store owner's shop.

Uses Shopify's client-credentials grant (private/custom app on a store in the
same organization). This is not an OAuth installation flow for public apps.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

API_VERSION = "2026-07"
_token: str | None = None
_token_expires = 0.0


class ShopifyError(RuntimeError):
    pass


def configured() -> bool:
    return all(os.getenv(key) for key in ("SHOPIFY_STORE_DOMAIN", "SHOPIFY_CLIENT_ID", "SHOPIFY_CLIENT_SECRET"))


def _store_domain() -> str:
    domain = os.getenv("SHOPIFY_STORE_DOMAIN", "").strip().lower()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*\.myshopify\.com", domain):
        raise ShopifyError("SHOPIFY_STORE_DOMAIN must be a *.myshopify.com domain")
    return domain


def _request(url: str, payload: dict, headers: dict[str, str] | None = None) -> dict:
    request = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json", **(headers or {})}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            result = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        # Never include response body in errors: it can contain sensitive data.
        raise ShopifyError(f"Shopify returned HTTP {exc.code}") from None
    except (urllib.error.URLError, TimeoutError) as exc:
        raise ShopifyError(f"Shopify request failed: {getattr(exc, 'reason', 'timeout')}") from None
    return result


def _access_token() -> str:
    global _token, _token_expires
    if _token and time.time() < _token_expires - 60:
        return _token
    domain = _store_domain()
    body = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": os.environ["SHOPIFY_CLIENT_ID"],
        "client_secret": os.environ["SHOPIFY_CLIENT_SECRET"],
    }).encode()
    req = urllib.request.Request(f"https://{domain}/admin/oauth/access_token", data=body, headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        raise ShopifyError(f"Shopify token request failed with HTTP {exc.code}") from None
    except (urllib.error.URLError, TimeoutError) as exc:
        raise ShopifyError(f"Shopify token request failed: {getattr(exc, 'reason', 'timeout')}") from None
    _token = result.get("access_token")
    if not _token:
        raise ShopifyError("Shopify did not return an access token; check app credentials and scopes")
    _token_expires = time.time() + int(result.get("expires_in", 86400))
    return _token


def products(first: int = 12) -> list[dict]:
    domain = _store_domain()
    query = """query PortfolioProducts($first: Int!) { products(first: $first) { nodes { id title handle status productType featuredImage { url altText } variants(first: 20) { nodes { id title price compareAtPrice availableForSale } } } } }"""
    result = _request(f"https://{domain}/admin/api/{API_VERSION}/graphql.json", {"query": query, "variables": {"first": max(1, min(first, 50))}}, {"X-Shopify-Access-Token": _access_token()})
    if result.get("errors"):
        # Do not send query details or returned data through the UI.
        raise ShopifyError("Shopify GraphQL query failed; check Admin API scopes and app access")
    return result.get("data", {}).get("products", {}).get("nodes", [])
