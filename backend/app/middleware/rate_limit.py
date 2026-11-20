"""
Rate Limiting Middleware
Protects API from abuse with request rate limiting.
"""

import time
from collections import defaultdict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Tuple


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using token bucket algorithm.
    
    Limits:
    - 100 requests per minute per IP
    - 1000 requests per hour per IP
    """
    
    def __init__(self, app, requests_per_minute: int = 100, requests_per_hour: int = 1000):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
        # Storage: {ip: [(timestamp, count_minute, count_hour)]}
        self.request_counts: Dict[str, Tuple[float, int, int]] = defaultdict(lambda: (time.time(), 0, 0))
        
        # Cleanup interval
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5 minutes
    
    def _cleanup_old_entries(self):
        """Remove old entries to prevent memory leak."""
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            # Remove entries older than 1 hour
            cutoff = current_time - 3600
            self.request_counts = {
                ip: data for ip, data in self.request_counts.items()
                if data[0] > cutoff
            }
            self.last_cleanup = current_time
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host
        current_time = time.time()
        
        # Get current counts
        last_time, minute_count, hour_count = self.request_counts[client_ip]
        
        # Reset minute counter if 60 seconds passed
        if current_time - last_time >= 60:
            minute_count = 0
            last_time = current_time
        
        # Reset hour counter if 3600 seconds passed
        if current_time - last_time >= 3600:
            hour_count = 0
        
        # Increment counters
        minute_count += 1
        hour_count += 1
        
        # Check limits
        if minute_count > self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {self.requests_per_minute} requests per minute. Try again later."
            )
        
        if hour_count > self.requests_per_hour:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {self.requests_per_hour} requests per hour. Try again later."
            )
        
        # Update counts
        self.request_counts[client_ip] = (last_time, minute_count, hour_count)
        
        # Periodic cleanup
        self._cleanup_old_entries()
        
        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining-Minute"] = str(self.requests_per_minute - minute_count)
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Hour"] = str(self.requests_per_hour - hour_count)
        
        return response
