#!/usr/bin/env python3
"""
Automated n8n account setup + API key creation via Playwright.

Reads  : ~/.claude/.secrets/n8n.env  (N8N_EMAIL, N8N_PASSWORD, N8N_BASE_URL)
Writes : N8N_API_KEY back into the same file

Usage  : python3 n8n-setup-account.py
         (called automatically by setup.sh --with-n8n)
"""

import os
import re
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

SECRETS_PATH = Path.home() / ".claude" / ".secrets" / "n8n.env"
LOG_DIR = Path.home() / ".claude" / "logs"


# ── helpers ──────────────────────────────────────────────────────────────────

def load_env(path: Path) -> dict:
    env = {}
    try:
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return env


def write_key(path: Path, key: str, value: str) -> None:
    content = path.read_text()
    if re.search(rf"^{re.escape(key)}=", content, re.MULTILINE):
        content = re.sub(rf"^{re.escape(key)}=.*$", f"{key}={value}", content, flags=re.MULTILINE)
    else:
        content = content.rstrip("\n") + f"\n{key}={value}\n"
    path.write_text(content)
    os.chmod(path, 0o600)


def wait_for_n8n(base_url: str, timeout: int = 120) -> bool:
    print(f"Waiting for n8n at {base_url}", end="", flush=True)
    start = time.time()
    while time.time() - start < timeout:
        try:
            urllib.request.urlopen(f"{base_url}/healthz", timeout=3)
            print(" ready")
            return True
        except Exception:
            print(".", end="", flush=True)
            time.sleep(2)
    print(" timed out")
    return False


def save_screenshot(page, label: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    path = LOG_DIR / f"n8n-setup-{label}.png"
    try:
        page.screenshot(path=str(path))
        print(f"  screenshot → {path}")
    except Exception:
        pass


def click_first(page, selectors: list[str], timeout: int = 5000) -> bool:
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            if loc.count() > 0:
                loc.click(timeout=timeout)
                return True
        except Exception:
            pass
    return False


def fill_first(page, selectors: list[str], value: str) -> bool:
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            if loc.count() > 0:
                loc.fill(value)
                return True
        except Exception:
            pass
    return False


# ── n8n flow steps ───────────────────────────────────────────────────────────

def handle_setup_wizard(page, base_url: str, email: str, password: str) -> None:
    """Fill the first-run owner-account form."""
    print("  First-run setup wizard detected — creating owner account...")

    page.wait_for_selector(
        'input[id="email"], input[type="email"], input[placeholder*="email" i]',
        timeout=15000,
    )

    fill_first(page, ['input[id="email"]', 'input[type="email"]', 'input[placeholder*="email" i]'], email)
    fill_first(page, ['input[id="firstName"]', 'input[name="firstName"]', 'input[placeholder*="first" i]'], "Claude")
    fill_first(page, ['input[id="lastName"]', 'input[name="lastName"]', 'input[placeholder*="last" i]'], "User")
    fill_first(page, ['input[type="password"]'], password)

    click_first(page, ['button[type="submit"]', 'button:has-text("Get started")', 'button:has-text("Next")'])

    # Wait until we're no longer on /setup
    try:
        page.wait_for_url(
            lambda url: "/setup" not in url,
            timeout=20000,
        )
    except Exception:
        time.sleep(3)

    print("  Owner account created")


def handle_login(page, base_url: str, email: str, password: str) -> None:
    """Sign in to an existing n8n instance."""
    print("  Login page detected — signing in...")

    page.wait_for_selector(
        'input[type="email"], input[id="email"]',
        timeout=10000,
    )
    fill_first(page, ['input[id="email"]', 'input[type="email"]'], email)
    fill_first(page, ['input[type="password"]'], password)
    click_first(page, ['button[type="submit"]', 'button:has-text("Sign in")'])

    try:
        page.wait_for_url(
            lambda url: "signin" not in url and "login" not in url,
            timeout=15000,
        )
    except Exception:
        time.sleep(2)

    print("  Logged in")


def dismiss_wizard_screens(page) -> None:
    """Click through any post-setup welcome/survey screens."""
    for _ in range(4):
        time.sleep(1)
        clicked = click_first(
            page,
            [
                'button:has-text("Skip")',
                'button:has-text("Skip setup")',
                'button:has-text("Get started")',
                'button:has-text("Next")',
                'button:has-text("Continue")',
                '[data-test-id="skip-button"]',
            ],
            timeout=2000,
        )
        if not clicked:
            break


def create_api_key(page, base_url: str) -> str:
    """Navigate to /settings/api, create a key named 'claude-code', return the key string."""
    print("  Navigating to Settings → API...")
    page.goto(f"{base_url}/settings/api", wait_until="networkidle", timeout=15000)
    time.sleep(1)

    # Click the create button (text varies by n8n version)
    opened = click_first(
        page,
        [
            'button:has-text("Create an API key")',
            'button:has-text("Add first API key")',
            'button:has-text("Create API key")',
            'button:has-text("Add API key")',
            '[data-test-id="api-key-create-button"]',
            'button:has-text("Create")',
        ],
        timeout=10000,
    )
    if not opened:
        raise RuntimeError("Could not find 'Create API key' button on /settings/api")

    time.sleep(0.8)  # modal animation

    # Some versions ask for a key name/label
    fill_first(
        page,
        [
            'input[name="keyName"]',
            'input[placeholder*="name" i]',
            'input[placeholder*="label" i]',
            '[data-test-id="api-key-name-input"] input',
            '.el-dialog input[type="text"]',
            '[role="dialog"] input[type="text"]',
        ],
        "claude-code",
    )

    # Confirm creation inside the modal
    click_first(
        page,
        [
            '[role="dialog"] button:has-text("Create")',
            '.el-dialog button:has-text("Create")',
            '[data-test-id="api-key-create-confirm"]',
            'button:has-text("Save")',
            'button:has-text("Generate")',
        ],
        timeout=8000,
    )

    time.sleep(1)

    # Extract the key — try multiple patterns
    api_key = None

    # 1. read-only / disabled input
    for sel in [
        'input[readonly]',
        'input[disabled]',
        '[data-test-id="api-key-value"] input',
        '.el-dialog input[readonly]',
        '[role="dialog"] input[readonly]',
    ]:
        loc = page.locator(sel)
        if loc.count() > 0:
            val = (loc.first.get_attribute("value") or loc.first.input_value() or "").strip()
            if val and len(val) > 20 and "@" not in val:
                api_key = val
                break

    # 2. <code> or <pre> element
    if not api_key:
        for sel in ["code", "pre", ".n8n-text code", ".el-dialog code"]:
            loc = page.locator(sel)
            if loc.count() > 0:
                val = loc.first.inner_text().strip()
                if val and len(val) > 20:
                    api_key = val
                    break

    # 3. data-test-id="api-key-value"
    if not api_key:
        loc = page.locator('[data-test-id="api-key-value"]')
        if loc.count() > 0:
            api_key = loc.first.inner_text().strip()

    if not api_key:
        save_screenshot(page, "api-key-modal")
        raise RuntimeError("Could not extract API key from the modal")

    # Dismiss modal
    click_first(
        page,
        [
            'button:has-text("Done")',
            'button:has-text("Close")',
            'button:has-text("OK")',
            '[aria-label="Close"]',
        ],
        timeout=3000,
    )

    return api_key


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    if not SECRETS_PATH.exists():
        sys.exit(f"ERROR: {SECRETS_PATH} not found\n"
                 "  Create it: cp .secrets-template/n8n.env.example ~/.claude/.secrets/n8n.env && chmod 600 ~/.claude/.secrets/n8n.env")

    env = load_env(SECRETS_PATH)
    email = env.get("N8N_EMAIL", "")
    password = env.get("N8N_PASSWORD", "")
    base_url = env.get("N8N_BASE_URL", "http://localhost:5678").rstrip("/")
    existing_key = env.get("N8N_API_KEY", "")

    if not email or not password:
        sys.exit("ERROR: N8N_EMAIL and N8N_PASSWORD must be set in ~/.claude/.secrets/n8n.env")

    if existing_key and not existing_key.startswith("your-") and len(existing_key) > 20:
        print(f"N8N_API_KEY already set ({existing_key[:16]}...) — nothing to do")
        return

    if not wait_for_n8n(base_url):
        sys.exit(f"ERROR: n8n not reachable at {base_url} — is the container running?")

    try:
        from playwright.sync_api import sync_playwright  # noqa: PLC0415
    except ImportError:
        sys.exit("ERROR: playwright not installed\n"
                 "  Run: pip3 install playwright && python3 -m playwright install chromium")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            print("Loading n8n...")
            page.goto(base_url, wait_until="networkidle", timeout=30000)
            url = page.url
            print(f"  URL: {url}")

            if "/setup" in url:
                handle_setup_wizard(page, base_url, email, password)
                dismiss_wizard_screens(page)
            elif any(x in url for x in ["/signin", "/login"]):
                handle_login(page, base_url, email, password)
            else:
                print("  Already authenticated")

            api_key = create_api_key(page, base_url)

        except Exception as exc:
            save_screenshot(page, "error")
            browser.close()
            sys.exit(f"ERROR: {exc}")

        browser.close()

    write_key(SECRETS_PATH, "N8N_API_KEY", api_key)
    print(f"✓ N8N_API_KEY saved to {SECRETS_PATH}")
    print(f"  Key: {api_key[:20]}...")


if __name__ == "__main__":
    main()
