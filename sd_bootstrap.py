import os
import time
import subprocess
import requests
import sys

# ---- Config via environment ----
A1111_API_URL   = os.getenv("A1111_API_URL", "http://127.0.0.1:7860")

# Preferred: control service via sd-ctl API (remote-safe)
SDCTL_URL       = os.getenv("SDCTL_URL", "").rstrip("/")
SDCTL_KEY       = os.getenv("SDCTL_API_KEY", "")

# Fallback: control local systemd service
SD_SERVICE      = os.getenv("SD_SERVICE", "stable-diffusion")

# Behavior
SD_START_TIMEOUT = int(os.getenv("SD_START_TIMEOUT", "90"))  # seconds to wait for A1111 API
SD_AUTOSTOP      = os.getenv("SD_AUTOSTOP", "30m")           # forwarded to sd-ctl; empty disables one-shot autostop


# ---- Helpers ----
def _sdctl_headers():
    if not SDCTL_KEY:
        return {}
    return {"X-API-Key": SDCTL_KEY}

def sd_is_up(timeout: float = 2.0) -> bool:
    """
    Returns True when the A1111 HTTP API is responding.
    """
    try:
        r = requests.get(f"{A1111_API_URL}/sdapi/v1/sd-models", timeout=timeout)
        return r.ok
    except Exception:
        return False

def _start_via_sdctl():
    """
    Start SD through sd-ctl API and wait until it's up.
    """
    t = SD_START_TIMEOUT
    resp = requests.post(
        f"{SDCTL_URL}/api/sd/start?timeout={t}",
        headers=_sdctl_headers(),
        json={"autostop": SD_AUTOSTOP or None},
        timeout=t + 5,
    )
    resp.raise_for_status()

def _start_via_systemd():
    """
    Start SD via local systemd (works only if A1111 runs on this host).
    """
    subprocess.run(["sudo", "systemctl", "start", SD_SERVICE], check=True)
    if SD_AUTOSTOP:
        subprocess.run(
            [
                "sudo",
                "systemd-run",
                "--unit",
                "sd-autostop",
                "--on-active",
                SD_AUTOSTOP,
                "systemctl",
                "stop",
                SD_SERVICE,
            ],
            check=False,
        )

def start_sd():
    """
    Starts Stable Diffusion either via sd-ctl (preferred) or local systemd.
    """
    if SDCTL_URL:
        _start_via_sdctl()
    else:
        _start_via_systemd()

def ensure_sd() -> bool:
    """
    Ensure A1111 is up. Returns True if we started it in this call.
    Raises RuntimeError if it doesn't become ready in time.
    """
    if sd_is_up(timeout=1.5):
        return False

    start_sd()

    deadline = time.time() + SD_START_TIMEOUT
    while time.time() < deadline:
        if sd_is_up(timeout=1.5):
            return True
        time.sleep(2)

    raise RuntimeError("Stable Diffusion failed to become ready in time")


# ---- CLI harness for quick testing ----
if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "ensure"
    if action == "check":
        ok = sd_is_up()
        print("SD up?", ok)
        sys.exit(0 if ok else 1)
    elif action == "start":
        start_sd()
        print("Start command issued.")
    else:
        try:
            started = ensure_sd()
            print("ensure_sd started SD:", started)
        except Exception as e:
            print("ensure_sd failed:", e)
            sys.exit(1)