from django.urls import path

from .auth import TokenRefreshThrottledView, TokenView

app_name = 'accounts'

urlpatterns = [
    path('token/', TokenView.as_view(), name='token'),
    path('token/refresh/', TokenRefreshThrottledView.as_view(), name='token_refresh'),
]
