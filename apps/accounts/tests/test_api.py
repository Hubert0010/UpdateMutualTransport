"""Socle de l'API REST : jetons JWT, protection par défaut, limitation et pagination."""
from unittest.mock import patch

from django.core.cache import cache
from django.test import override_settings
from django.urls import path, reverse
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.serializers import ModelSerializer
from rest_framework.test import APITestCase
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.companies.tests.factories import PASSWORD, make_company


class WhoAmIView(APIView):
    def get(self, request):
        return Response({'email': request.user.email})


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['email']


class UserListView(ListAPIView):
    queryset = User.objects.order_by('email')
    serializer_class = UserSerializer


urlpatterns = [
    path('whoami/', WhoAmIView.as_view()),
    path('users/', UserListView.as_view()),
]


class ApiTestCase(APITestCase):
    def setUp(self):
        cache.clear()  # les compteurs de limitation sont stockés dans le cache


class TokenTests(ApiTestCase):
    url = '/api/v1/auth/token/'

    def setUp(self):
        super().setUp()
        self.company = make_company()

    def test_valid_credentials_return_tokens(self):
        response = self.client.post(self.url, {'email': 'contact@nagode.tg', 'password': PASSWORD}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.data), {'access', 'refresh'})

    def test_email_ignores_case(self):
        response = self.client.post(self.url, {'email': 'CONTACT@Nagode.tg', 'password': PASSWORD}, format='json')
        self.assertEqual(response.status_code, 200)

    def test_wrong_password_is_rejected(self):
        response = self.client.post(self.url, {'email': 'contact@nagode.tg', 'password': 'faux'}, format='json')
        self.assertEqual(response.status_code, 401)

    def test_inactive_account_is_rejected(self):
        self.company.user.is_active = False
        self.company.user.save()
        response = self.client.post(self.url, {'email': 'contact@nagode.tg', 'password': PASSWORD}, format='json')
        self.assertEqual(response.status_code, 401)

    def test_refresh_returns_a_new_access_token(self):
        tokens = self.client.post(self.url, {'email': 'contact@nagode.tg', 'password': PASSWORD}, format='json').data
        response = self.client.post(
            reverse('api_v1:accounts:token_refresh'), {'refresh': tokens['refresh']}, format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)

    def test_connection_attempts_are_limited(self):
        with patch.object(ScopedRateThrottle, 'THROTTLE_RATES', {'auth': '2/minute'}):
            statuses = [
                self.client.post(self.url, {'email': 'contact@nagode.tg', 'password': 'faux'}, format='json').status_code
                for _ in range(3)
            ]
        self.assertEqual(statuses, [401, 401, 429])

    def test_forged_forwarded_header_does_not_bypass_the_limit_behind_nginx(self):
        limit = {'auth': '1/minute'}
        with patch.object(ScopedRateThrottle, 'THROTTLE_RATES', limit), patch.object(api_settings, 'NUM_PROXIES', 1):
            statuses = [
                self.client.post(
                    self.url, {'email': 'contact@nagode.tg', 'password': 'faux'}, format='json',
                    HTTP_X_FORWARDED_FOR=f'10.0.0.{number}, 203.0.113.9',
                ).status_code
                for number in range(2)
            ]
        self.assertEqual(statuses, [401, 429])


@override_settings(ROOT_URLCONF='apps.accounts.tests.test_api')
class DefaultProtectionTests(ApiTestCase):
    def test_anonymous_request_is_rejected(self):
        response = self.client.get('/whoami/')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_invalid_token_is_rejected(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer faux')
        self.assertEqual(self.client.get('/whoami/').status_code, 401)

    def test_session_is_not_accepted(self):
        self.client.force_login(make_company().user)
        self.assertEqual(self.client.get('/whoami/').status_code, 401)

    def test_pagination_is_applied(self):
        for number in range(21):
            User.objects.create_user(email=f'user{number}@b.tg')
        self.client.force_authenticate(User.objects.first())
        response = self.client.get('/users/')
        self.assertEqual(response.data['count'], 21)
        self.assertEqual(len(response.data['results']), 20)


class JwtAccessTests(ApiTestCase):
    def test_access_token_opens_a_protected_view(self):
        make_company()
        tokens = self.client.post(
            '/api/v1/auth/token/', {'email': 'contact@nagode.tg', 'password': PASSWORD}, format='json',
        ).data
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        with override_settings(ROOT_URLCONF='apps.accounts.tests.test_api'):
            response = self.client.get('/whoami/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'email': 'contact@nagode.tg'})
