import time
from django.shortcuts import redirect
from django.conf import settings

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.timeout = getattr(settings, "SESSION_TIMEOUT", 10 * 60)  # сек

    def __call__(self, request):
        session = request.session
        now = int(time.time())
        last_activity = session.get('last_activity', now)
        session['last_activity'] = now

        # если разница превышает таймаут — выходим
        if now - last_activity > self.timeout:
            session.flush()
            return redirect('/')  # или на /login/

        return self.get_response(request)
