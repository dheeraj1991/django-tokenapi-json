from django.http import HttpResponseForbidden
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
import json

from functools import wraps

def token_required(view_func):
    """Decorator which ensures the user has provided a correct user and token pair."""

    @csrf_exempt
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = None
        token = None
        basic_auth = request.META.get('HTTP_AUTHORIZATION')
	if not (user and token):
		request.app_data = request.read()
		request_data = request.app_data
		json_data = json.loads(request_data)
		user = json_data['user']
		token = json_data['token']
	print user,token

        if basic_auth:
            auth_method, auth_string = basic_auth.split(' ', 1)
            if auth_method.lower() == 'basic':
                auth_string = auth_string.strip().decode('base64')
                user, token = auth_string.split(':', 1)

        if not (user and token):
            user = request.REQUEST.get('user')
            token = request.REQUEST.get('token')

        if user and token:
            user = authenticate(pk=user, token=token)
            if user:
                login(request, user)
                return view_func(request, *args, **kwargs)

        return HttpResponseForbidden()
    return _wrapped_view

