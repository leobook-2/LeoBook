# fb_session.py: Browser context and anti-detect management for Football.com.
# Part of LeoBook Modules — Football.com
#
# Functions: get_user_session_dir(), load_user_fingerprint(),
#            cleanup_chrome_processes(), launch_browser_with_retry()

import asyncio
import os
import logging
import subprocess
from pathlib import Path
from typing import Optional
from playwright.async_api import Playwright, BrowserContext
from Core.Utils.constants import FB_MOBILE_USER_AGENT, FB_MOBILE_VIEWPORT

logger = logging.getLogger(__name__)

# Global fallback when no user_id is supplied (operator/system-level runs).
_GLOBAL_SESSION_DIR = Path("Data/Auth/ChromeData_v3")


def get_user_session_dir(user_id: Optional[str]) -> Path:
    """Return per-user persistent Chrome profile directory.

    Each user gets an isolated profile so their Football.com session, cookies,
    and stored credentials are never mixed with another user's.
    Falls back to the legacy global directory when user_id is None/empty.
    """
    if user_id and user_id.strip():
        return Path(f"Data/Auth/sessions/{user_id.strip()}")
    return _GLOBAL_SESSION_DIR


def load_user_fingerprint(user_id: str) -> dict:
    """Load per-user fingerprint overrides from Supabase user_device_fingerprint table.

    Fields:
      - proxy_server  → e.g. 'http://user:pass@1.2.3.4:8080'
      - user_agent    → full UA string to impersonate user's device
      - viewport_w    → viewport width  (int, default 390)
      - viewport_h    → viewport height (int, default 844)

    Returns a dict with resolved values (or defaults when row is absent/empty).
    """
    fp: dict = {
        'proxy_server': None,
        'user_agent': FB_MOBILE_USER_AGENT,
        'viewport': FB_MOBILE_VIEWPORT,
    }
    if not user_id:
        return fp
    try:
        from Data.Access.supabase_client import get_supabase_client
        sb = get_supabase_client()
        result = sb.table('user_device_fingerprint').select('*').eq('user_id', user_id).maybe_single().execute()
        row = result.data if result else None
        if not row:
            return fp
        if row.get('proxy_server'):
            fp['proxy_server'] = row['proxy_server']
        if row.get('user_agent'):
            fp['user_agent'] = row['user_agent']
        vw = int(row.get('viewport_w') or 0) or FB_MOBILE_VIEWPORT['width']
        vh = int(row.get('viewport_h') or 0) or FB_MOBILE_VIEWPORT['height']
        fp['viewport'] = {'width': vw, 'height': vh}
    except Exception as e:
        logger.debug(f"[fb_session] fingerprint load skipped for {user_id}: {e}")
    return fp

async def cleanup_chrome_processes():
    """Automatically terminate conflicting Chrome processes before launch."""
    try:
        if os.name == 'nt':
            subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)
            print("  [Cleanup] Cleaned up Chrome processes.")
        else:
            subprocess.run(["pkill", "-f", "chrome"], capture_output=True)
            print("  [Cleanup] Cleaned up Chrome processes.")
    except Exception as e:
        print(f"  [Cleanup] Warning: Could not cleanup Chrome processes: {e}")

async def launch_browser_with_retry(
    playwright: Playwright,
    user_data_dir: Path,
    max_retries: int = 3,
    fingerprint: Optional[dict] = None,
) -> BrowserContext:
    """Launch browser with retry logic, exponential backoff, and per-user fingerprint.

    Args:
        fingerprint: dict from load_user_fingerprint() (proxy_server, user_agent,
                     viewport). When None, falls back to global env vars / constants.
    """
    base_timeout = 60000
    backoff_multiplier = 1.2

    # Auto-detect headless environment
    # Codespace, CI, Docker, or any no-display env = force headless
    _is_headless_env = (
        os.environ.get("CODESPACES") == "true"
        or os.environ.get("CI") == "true"
        or os.environ.get("DISPLAY") is None
        or os.environ.get("LEOBOOK_HEADLESS", "").lower() == "true"
    )

    _launch_args = [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-extensions",
        "--disable-infobars",
        "--disable-blink-features=AutomationControlled",
        "--no-first-run",
        "--no-service-autorun",
        "--password-store=basic",
        "--new-window"
    ]
    if _is_headless_env:
        _launch_args += [
            "--headless=new",
            "--disable-gpu",
            "--disable-software-rasterizer",
        ]

    env_label = "CODESPACE/CI" if _is_headless_env else "LOCAL"
    logger.info(f"[Browser] Environment: {env_label} | Headless: {_is_headless_env}")

    # Resolve fingerprint overrides (per-user > env var > constant)
    fp = fingerprint or {}
    _proxy = fp.get('proxy_server') or (os.getenv("LEOBOOK_FB_PROXY") or "").strip()
    _ua = fp.get('user_agent') or (os.getenv("LEOBOOK_FB_USER_AGENT") or "").strip() or FB_MOBILE_USER_AGENT
    _viewport = fp.get('viewport') or FB_MOBILE_VIEWPORT

    for attempt in range(max_retries):
        timeout = int(base_timeout * (backoff_multiplier ** attempt))
        print(f"  [Launch] Attempt {attempt + 1}/{max_retries} with {timeout}ms timeout...")

        try:
            _ctx_kwargs = dict(
                user_data_dir=str(user_data_dir),
                headless=_is_headless_env,
                args=_launch_args,
                ignore_default_args=["--enable-automation"],
                viewport=_viewport,
                user_agent=_ua,
                timeout=timeout,
            )
            if _proxy:
                _ctx_kwargs["proxy"] = {"server": _proxy}
                logger.info("[Browser] Proxy active (per-user or operator-level).")
            context = await playwright.chromium.launch_persistent_context(**_ctx_kwargs)

            print(f"  [Launch] Browser launched successfully on attempt {attempt + 1}!")
            return context

        except Exception as e:
            print(f"  [Launch] Attempt {attempt + 1} failed: {e}")

            if attempt < max_retries - 1:
                lock_file = user_data_dir / "SingletonLock"
                if lock_file.exists():
                    try:
                        lock_file.unlink()
                        print(f"  [Launch] Removed SingletonLock before retry.")
                    except Exception as lock_e:
                        print(f"  [Launch] Could not remove lock file: {lock_e}")

                wait_time = 2 ** attempt
                print(f"  [Launch] Waiting {wait_time}s before next attempt...")
                await asyncio.sleep(wait_time)
            else:
                print(f"  [Launch] All {max_retries} attempts failed.")
                raise e
