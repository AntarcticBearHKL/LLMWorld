import argparse
import json
import os
import sys
import threading
import time

import requests

import config


class LLMCallError(RuntimeError):
    pass


CREDENTIALS_FILE = config.MATILDA_CREDENTIALS_FILE

DEVICE_CODE_URL = config.MATILDA_BASE_URL + "/api/auth/oauth/device/code"
TOKEN_URL = config.MATILDA_BASE_URL + "/api/auth/oauth/token"

CLIENT_ID = config.MATILDA_CLIENT_ID
DEVICE_SCOPE = "openid offline_access"
GRANT_TYPE_DEVICE = "urn:ietf:params:oauth:grant-type:device_code"
GRANT_TYPE_REFRESH = "refresh_token"

# Credentials JSON schema: {"access_token": "<str>", "refresh_token": "<str>", "expires_at": <float epoch seconds>}
# Read/write lock: guarantees single-flight refresh during parallel calls (SubAgent.parallel_call uses ThreadPoolExecutor)
_lock = threading.RLock()
_cache = None


def _try_json(resp):
    try:
        return resp.json()
    except (json.JSONDecodeError, ValueError):
        return {}


def _read_file():
    if not os.path.exists(CREDENTIALS_FILE):
        raise LLMCallError("Matilda has not been authenticated yet; please first run: python src/matilda_auth.py")
    try:
        with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        raise LLMCallError(
            "Matilda credentials file is missing or corrupted; please re-authenticate: python src/matilda_auth.py"
        ) from e


def save_credentials(creds):
    global _cache
    with _lock:
        tmp_path = CREDENTIALS_FILE + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(creds, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, CREDENTIALS_FILE)
        _cache = dict(creds)


def _load_creds():
    global _cache
    if _cache is not None:
        return _cache
    creds = _read_file()
    _cache = creds
    return creds


def _refresh():
    creds = _read_file()
    refresh_token = creds.get("refresh_token")
    if not refresh_token:
        raise LLMCallError("Matilda is missing refresh_token; please re-authenticate: python src/matilda_auth.py")

    try:
        resp = requests.post(
            TOKEN_URL,
            data={
                "grant_type": GRANT_TYPE_REFRESH,
                "client_id": CLIENT_ID,
                "refresh_token": refresh_token,
            },
            timeout=30,
        )
    except requests.exceptions.RequestException as e:
        raise LLMCallError(f"Matilda token refresh network error: {e}") from e

    payload = _try_json(resp)
    if resp.status_code == 200:
        new_creds = {
            "access_token": payload["access_token"],
            # Reuse the old value when the response does not carry a new refresh_token
            "refresh_token": payload.get("refresh_token") or refresh_token,
            "expires_at": time.time() + float(payload.get("expires_in") or 3600),
        }
        save_credentials(new_creds)
        return new_creds

    if payload.get("error") == "invalid_grant":
        raise LLMCallError("Matilda refresh_token has expired; please run again: python src/matilda_auth.py")
    raise LLMCallError(
        f"Matilda token refresh failed (HTTP {resp.status_code}): "
        f"{payload.get('error_description') or payload}"
    )


def get_access_token():
    with _lock:
        creds = _load_creds()
        if not creds.get("access_token"):
            raise LLMCallError("Matilda has not been authenticated yet; please first run: python src/matilda_auth.py")
        now = time.time()
        # Reserve 60 seconds for clock skew
        if creds.get("expires_at", 0) - 60 <= now:
            creds = _refresh()
        return creds["access_token"]


def force_refresh():
    global _cache
    with _lock:
        _cache = _load_creds()
        _cache["expires_at"] = 0
        return get_access_token()


def run_device_flow():
    print("Requesting a device authorization code from Matilda...")
    try:
        resp = requests.post(
            DEVICE_CODE_URL,
            data={"client_id": CLIENT_ID, "scope": DEVICE_SCOPE},
            timeout=30,
        )
        resp.raise_for_status()
        payload = resp.json()
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"[Failed] Error obtaining device authorization code: {e}", file=sys.stderr)
        return 1

    device_code = payload["device_code"]
    user_code = payload["user_code"]
    expires_in = int(payload.get("expires_in", 900))
    interval = int(payload.get("interval", 5))
    verification_uri_complete = payload.get("verification_uri_complete") or payload.get("verification_uri")

    print("=" * 60)
    print("Please open the following link to complete authorization (log in to Matilda on your device):")
    print(verification_uri_complete)
    print(f"user code: {user_code}")
    print("=" * 60)

    deadline = time.time() + expires_in
    while True:
        if time.time() > deadline:
            print("[Failed] Device authorization timed out; please run again: python src/matilda_auth.py", file=sys.stderr)
            return 1

        try:
            poll = requests.post(
                TOKEN_URL,
                data={
                    "grant_type": GRANT_TYPE_DEVICE,
                    "client_id": CLIENT_ID,
                    "device_code": device_code,
                },
                timeout=30,
            )
        except requests.exceptions.RequestException as e:
            print(f"[Failed] Error polling token: {e}", file=sys.stderr)
            return 1

        payload = _try_json(poll)
        if poll.status_code == 200:
            break

        err = payload.get("error")
        desc = payload.get("error_description", "")
        if err == "authorization_pending":
            print(f"Waiting for user authorization... (continuing to poll in {interval}s)")
            time.sleep(interval)
            continue
        if err == "slow_down":
            interval += 5
            print(f"Server requires a lower polling frequency; interval adjusted to {interval}s")
            time.sleep(interval)
            continue
        if err in ("expired_token", "access_denied"):
            print(f"[Failed] Authorization flow aborted ({err}): {desc}", file=sys.stderr)
            return 1
        print(f"[Failed] Unknown token endpoint error ({err}): {desc}", file=sys.stderr)
        return 1

    access_token = payload["access_token"]
    refresh_token = payload.get("refresh_token", "")
    expires_at = time.time() + float(payload.get("expires_in") or 3600)
    save_credentials({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": expires_at,
    })
    print("[Success] Matilda credentials saved.")
    return 0


def print_status():
    if not os.path.exists(CREDENTIALS_FILE):
        print("Not authenticated: Matilda credentials file not found; please first run: python src/matilda_auth.py")
        return 0
    try:
        with _lock:
            creds = _load_creds()
    except LLMCallError as e:
        print(f"Credential error: {e}")
        return 1
    expired = creds.get("expires_at", 0) - 60 <= time.time()
    if not creds.get("access_token"):
        print("Credentials file is missing access_token; please re-authenticate: python src/matilda_auth.py")
        return 1
    if expired:
        print("Credentials have expired (will be auto-refreshed on the next call)")
    else:
        left = int(creds.get("expires_at", 0) - time.time())
        print(f"Credentials valid, about {left} seconds remaining")
    return 0


def logout():
    global _cache
    with _lock:
        _cache = None
        if os.path.exists(CREDENTIALS_FILE):
            os.remove(CREDENTIALS_FILE)
            print("Matilda credentials file deleted.")
        else:
            print("No Matilda credentials file found; nothing to clean up.")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Matilda OAuth 2.0 device flow authentication (RFC 8628)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--logout", action="store_true", help="Delete saved Matilda credentials")
    group.add_argument("--status", action="store_true", help="Show credential status")
    args = parser.parse_args(argv)

    if args.logout:
        return logout()
    if args.status:
        return print_status()
    return run_device_flow()


if __name__ == "__main__":
    sys.exit(main())
