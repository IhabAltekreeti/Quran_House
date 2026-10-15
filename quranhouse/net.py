"""Bounded, allowlisted HTTP downloads (prevents SSRF via API-provided URLs)."""
import os
from urllib.parse import urlparse

import requests

from .errors import MediaError

DEFAULT_TIMEOUT = (10, 30)


def check_url(url: str, allowed_hosts) -> str:
    p = urlparse(url)
    if p.scheme != "https":
        raise MediaError(f"refusing non-https URL: {p.scheme}://{p.hostname}")
    host = (p.hostname or "").lower()
    if not any(host == h or host.endswith("." + h) for h in allowed_hosts):
        raise MediaError(f"refusing download from non-allowlisted host: {host}")
    return url


def download(url, dest, allowed_hosts, max_bytes, expected_ctype_prefixes, session=None):
    """Stream to dest.part, validate host after redirects, size, content-type; then rename."""
    check_url(url, allowed_hosts)
    s = session or requests
    with s.get(url, stream=True, timeout=DEFAULT_TIMEOUT, allow_redirects=True) as r:
        check_url(r.url, allowed_hosts)  # final URL after redirects
        if r.status_code != 200:
            raise MediaError(f"download failed: HTTP {r.status_code}")
        ctype = (r.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        if not any(ctype.startswith(p) for p in expected_ctype_prefixes):
            raise MediaError(f"unexpected content-type {ctype!r} (expected {expected_ctype_prefixes})")
        cl = r.headers.get("Content-Length")
        if cl and cl.isdigit() and int(cl) > max_bytes:
            raise MediaError(f"file too large: {cl} bytes > {max_bytes}")
        tmp = dest + ".part"
        n = 0
        try:
            with open(tmp, "wb") as f:
                for chunk in r.iter_content(1024 * 256):
                    n += len(chunk)
                    if n > max_bytes:
                        raise MediaError(f"file exceeded {max_bytes} bytes")
                    f.write(chunk)
            if n == 0:
                raise MediaError("downloaded file is empty")
            os.replace(tmp, dest)
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
    return n
