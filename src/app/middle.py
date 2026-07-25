from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from core.config import setting

from app.middleware.rate_limiter import RateLimiterStore
from app.middleware.hmac_token import TokenController
from app.middleware.session import SessionStorage, SessionToken

import time

def add_middleware(app):
    app.add_middleware(
    CORSMiddleware,
    allow_origins=setting.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
)

limiter = RateLimiterStore(max_tokens=10, refill_rate=2, interval=1.0)

controller = TokenController()

session_store = SessionStorage()

SESSION_COOKIE_NAME = "session_id"
SESSION_TTL_SECONDS = 1800 


def add_sessionid_middleware(app):
    @app.middleware("http")
    async def session_middleware(request: Request, call_next):
        session_id = request.cookies.get(SESSION_COOKIE_NAME)
        is_new_session = False
 
        if session_id and session_store.touch(session_id, SESSION_TTL_SECONDS):
            pass
        else:
            session_id = session_store.generate(ttl_seconds=SESSION_TTL_SECONDS)
            is_new_session = True
 
        request.state.session_id = session_id
        response = await call_next(request)
 
        if is_new_session:
            response.set_cookie(
                key=SESSION_COOKIE_NAME,
                value=session_id,
                httponly=True,
                samesite="lax",
                secure=True,
                max_age=SESSION_TTL_SECONDS,
            )
        return response


def add_signature_middlware(app):
    @app.middleware("http")
    async def signature_middleware(request: Request, call_next):

        received_signature = request.headers.get("x-signature")

        if not received_signature:
            received_signature = controller.create_signature()
            request.scope["headers"].append((b"x-signature", bytes(received_signature, "utf-8")))

        if not controller.compare_signatures(received_signature):
            return JSONResponse(status_code=403, content={"detail": "Signature invalid"})
        
        response = await call_next(request)
        return response


def add_ratelimiter_middleware(app):
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        """Enforces per-IP rate limiting and adds standard rate limit headers."""
        client_ip = request.client.host
        bucket = limiter.get_bucket(client_ip)

        if not bucket.allow_request():
            retry_after = bucket.get_reset_time() - time.time()
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Try again later."},
                headers={
                    "Retry-After": str(max(1, int(retry_after))),
                    "X-RateLimit-Limit": str(bucket.max_tokens),
                    "X-RateLimit-Remaining": str(bucket.get_remaining()),
                    "X-RateLimit-Reset": str(int(bucket.get_reset_time())),
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(bucket.max_tokens)
        response.headers["X-RateLimit-Remaining"] = str(bucket.get_remaining())
        response.headers["X-RateLimit-Reset"] = str(int(bucket.get_reset_time()))
        return response