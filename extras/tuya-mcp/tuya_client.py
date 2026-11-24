"""涂鸦云 OpenAPI 最小客户端：v2 HMAC-SHA256 签名 + token 缓存刷新。"""
from __future__ import annotations

import hashlib
import hmac
import json
import threading
import time
import uuid
from urllib.parse import urlencode

import requests

EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()


class TuyaError(RuntimeError):
    pass


class TuyaClient:
    def __init__(self, access_id: str, access_secret: str,
                 endpoint: str = "https://openapi.tuyacn.com", timeout: float = 10):
        self.access_id = access_id
        self.access_secret = access_secret
        self.endpoint = endpoint.rstrip("/")
        self.timeout = timeout
        self._token: str | None = None
        self._refresh: str | None = None
        self._expire_at = 0.0
        self._lock = threading.Lock()

    # ---------- 签名 ----------
    def _sign(self, method: str, path: str, params: dict | None, body: str,
              t: str, nonce: str, token: str = "") -> str:
        url = path
        if params:
            url += "?" + "&".join(f"{k}={params[k]}" for k in sorted(params))
        content_sha = hashlib.sha256(body.encode()).hexdigest() if body else EMPTY_SHA256
        string_to_sign = f"{method}\n{content_sha}\n\n{url}"
        message = self.access_id + token + t + nonce + string_to_sign
        return hmac.new(self.access_secret.encode(), message.encode(),
                        hashlib.sha256).hexdigest().upper()

    def _raw(self, method: str, path: str, params: dict | None = None,
             body: dict | None = None, token: str = "") -> dict:
        body_str = json.dumps(body, separators=(",", ":")) if body is not None else ""
        t = str(int(time.time() * 1000))
        nonce = uuid.uuid4().hex
        headers = {
            "client_id": self.access_id,
            "t": t,
            "nonce": nonce,
            "sign_method": "HMAC-SHA256",
            "sign": self._sign(method, path, params, body_str, t, nonce, token),
            "Content-Type": "application/json",
        }
        if token:
            headers["access_token"] = token
        url = self.endpoint + path + ("?" + urlencode(sorted(params.items())) if params else "")
        r = requests.request(method, url, headers=headers,
                             data=body_str or None, timeout=self.timeout)
        try:
            return r.json()
        except ValueError:
            raise TuyaError(f"HTTP {r.status_code}: {r.text[:200]}")

    # ---------- token ----------
    def _ensure_token(self) -> str:
        with self._lock:
            if self._token and time.time() < self._expire_at - 60:
                return self._token
            res = None
            if self._refresh:
                res = self._raw("GET", f"/v1.0/token/{self._refresh}")
                if not res.get("success"):
                    res = None
            if res is None:
                res = self._raw("GET", "/v1.0/token", params={"grant_type": 1})
            if not res.get("success"):
                raise TuyaError(f"获取 token 失败: code={res.get('code')} msg={res.get('msg')}")
            r = res["result"]
            self._token = r["access_token"]
            self._refresh = r.get("refresh_token")
            self._expire_at = time.time() + int(r.get("expire_time", 7200))
            return self._token

    def request(self, method: str, path: str, params: dict | None = None,
                body: dict | None = None) -> dict:
        res = self._raw(method, path, params, body, self._ensure_token())
        # 1010 = token 无效/过期，强制刷新重试一次
        if not res.get("success") and str(res.get("code")) in {"1010", "1011"}:
            with self._lock:
                self._token = None
                self._expire_at = 0
            res = self._raw(method, path, params, body, self._ensure_token())
        return res

    # ---------- 红外 ----------
    def list_remotes(self, infrared_id: str) -> dict:
        return self.request("GET", f"/v2.0/infrareds/{infrared_id}/remotes")

    def learning_codes(self, infrared_id: str, remote_id: str) -> dict:
        return self.request("GET", f"/v2.0/infrareds/{infrared_id}/remotes/{remote_id}/learning-codes")

    def send_learned(self, infrared_id: str, remote_id: str, code: str) -> dict:
        return self.request("POST", f"/v2.0/infrareds/{infrared_id}/remotes/{remote_id}/learning-codes",
                            body={"code": code})
