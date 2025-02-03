import os
import time
import base64
import requests

VT_BASE = "https://www.virustotal.com/api/v3"
API_KEY = os.getenv("VT_API_KEY")
HEADERS = {"x-apikey": API_KEY} if API_KEY else {}

def _encode_url(raw_url: str) -> str:
    """Retourne l'identifiant VT de l'URL en base64url sans padding."""
    b = raw_url.encode("utf-8")
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")

def _fallback(url: str) -> dict:
    """Retourne un résultat neutre en cas d’erreur."""
    return {
        "url": url,
        "harmless": 0,
        "malicious": 0,
        "suspicious": 0,
        "permalink": url
    }

def check_url(url: str, timeout: int = 15, poll_interval: float = 1.0) -> dict:
    """
    Tente d'abord de récupérer un rapport existant (GET /urls/{id}).
    Si 404, soumet (POST /urls) et poll (/analyses/{analysis_id}) jusqu'à 'completed'.
    """
    encoded = _encode_url(url)

    try:
        r0 = requests.get(f"{VT_BASE}/urls/{encoded}", headers=HEADERS, timeout=timeout)
    except requests.RequestException as e:
        print(f"✖️ [ERROR] GET rapport VT échoué pour {url}: {e}", flush=True)
        return _fallback(url)

    if r0.status_code == 200:
        data = r0.json().get("data", {}).get("attributes", {})
        stats = data.get("last_analysis_stats", {})
        permalink = f"https://www.virustotal.com/gui/url/{encoded}/detection"
        return {
            "url": url,
            "harmless": stats.get("harmless", 0),
            "malicious": stats.get("malicious", 0),
            "suspicious": stats.get("suspicious", 0),
            "permalink": permalink
        }

    if r0.status_code != 404:
        print(f"✖️ [ERROR] VT GET /urls/{encoded} renvoie {r0.status_code} pour {url}", flush=True)
        return _fallback(url)

    try:
        resp = requests.post(f"{VT_BASE}/urls", headers=HEADERS, data={"url": url}, timeout=timeout)
    except requests.RequestException as e:
        print(f"✖️ [ERROR] POST soumission VT échouée pour {url}: {e}", flush=True)
        return _fallback(url)
    if resp.status_code != 200:
        print(f"✖️ [ERROR] VT POST /urls status {resp.status_code} pour {url}", flush=True)
        return _fallback(url)

    analysis_id = resp.json().get("data", {}).get("id")
    if not analysis_id:
        print(f"✖️ [ERROR] Pas d'analysis_id VT pour {url}", flush=True)
        return _fallback(url)

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r2 = requests.get(f"{VT_BASE}/analyses/{analysis_id}", headers=HEADERS, timeout=timeout)
        except requests.RequestException as e:
            print(f"✖️ [ERROR] Poll analyse {analysis_id} échoué: {e}", flush=True)
            break
        if r2.status_code == 200:
            body = r2.json().get("data", {}).get("attributes", {})
            if body.get("status") == "completed":
                stats = body.get("stats", {})
                permalink = f"https://www.virustotal.com/gui/url/{encoded}/detection"
                return {
                    "url": url,
                    "harmless": stats.get("harmless", 0),
                    "malicious": stats.get("malicious", 0),
                    "suspicious": stats.get("suspicious", 0),
                    "permalink": permalink
                }
        time.sleep(poll_interval)

    print(f"✖️ [ERROR] Timeout analyse VT pour {url}", flush=True)
    return _fallback(url)
