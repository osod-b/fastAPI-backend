from datetime import datetime, timezone, timedelta
from threading import Lock
from typing import Optional
import uuid

from pydantic.dataclasses import dataclass


@dataclass
class SessionToken:
    token_id: str
    created: str
    expires: str
    used: bool = False  # was missing -- validate()/consume() need this field

    @classmethod
    def new(cls, ttl_seconds: int = 600):
        now = datetime.now(timezone.utc)
        return cls(
            token_id=str(uuid.uuid4()),   # was missing () -- every id was identical
            created=now.isoformat(),
            expires=(now + timedelta(seconds=ttl_seconds)).isoformat(),
        )

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > datetime.fromisoformat(self.expires)


class SessionStorage:
    def __init__(self):
        self._tokens: dict[str, SessionToken] = {}
        self._lock = Lock()

    def generate(self, ttl_seconds: int = 600) -> str:
        token = SessionToken.new(ttl_seconds=ttl_seconds)
        with self._lock:
            self._tokens[token.token_id] = token
        return token.token_id

    def validate(self, token_id: str) -> bool:
        with self._lock:
            token = self._tokens.get(token_id)
            if token is None:
                return False
            if token.used or token.is_expired():
                return False
            return True

    def consume(self, token_id: str) -> bool:
        """One-time use: validates and burns the token atomically."""
        with self._lock:
            token = self._tokens.get(token_id)
            if token is None:
                return False
            if token.used or token.is_expired():
                return False
            token.used = True
            return True

    def touch(self, token_id: str, extend_seconds: int = 1800) -> bool:
        """
        Sliding expiry: extends a still-valid, unconsumed token's lifetime.
        Required by session_middleware -- was missing, would have raised
        AttributeError: 'SessionStorage' object has no attribute 'touch'.
        """
        with self._lock:
            token = self._tokens.get(token_id)
            if token is None or token.used or token.is_expired():
                return False
            token.expires = (
                datetime.now(timezone.utc) + timedelta(seconds=extend_seconds)
            ).isoformat()
            return True

    def cleanup_expired(self) -> int:
        with self._lock:
            expired_ids = [tid for tid, t in self._tokens.items() if t.is_expired()]
            for tid in expired_ids:
                del self._tokens[tid]
            return len(expired_ids)