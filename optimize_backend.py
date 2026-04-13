import sys
import os

def optimize_verification_guard():
    file_path = r'd:\cryptomentorAI\website-backend\app\middleware\verification_guard.py'
    if not os.path.exists(file_path): return
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ensure cache header is there
    if '_VERIFICATION_CACHE = {}' not in content:
        content = content.replace('return status or "none"', 'return status or "none"\n\nimport time as _time\n_VERIFICATION_CACHE = {} # tg_id: (status, expiry)\n_CACHE_TTL = 120 # 2 minutes')

    # Apply dispatch cache
    old_dispatch_start = """        # Check verification status from the central table.
        try:
            s = _client()"""
            
    new_dispatch_start = """        # Check cache first
        now = _time.time()
        cached_status, expiry = _VERIFICATION_CACHE.get(tg_id, (None, 0))
        if cached_status and now < expiry:
            if cached_status != APPROVED_STATUS:
                logger.info(f"[Guard:Cache:{tg_id}] Blocked — status: {cached_status}")
                return JSONResponse(status_code=403, content={"error": "verification_required", "status": cached_status})
            return await call_next(request)

        # Check verification status from the central table.
        try:
            s = _client()"""

    if old_dispatch_start in content and new_dispatch_start not in content:
        content = content.replace(old_dispatch_start, new_dispatch_start)
    
    # Update cache after fetch
    old_status_calc = """            status = _normalize_verification_status(raw_status)

            if status != APPROVED_STATUS:"""
            
    new_status_calc = """            status = _normalize_verification_status(raw_status)
            
            # Update cache
            _VERIFICATION_CACHE[tg_id] = (status, now + _CACHE_TTL)

            if status != APPROVED_STATUS:"""

    if old_status_calc in content and new_status_calc not in content:
        content = content.replace(old_status_calc, new_status_calc)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Optimized VerificationGuardMiddleware")

optimize_verification_guard()
print("All optimizations applied.")
