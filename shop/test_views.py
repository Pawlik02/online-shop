from .views import cart
from django.contrib.auth.models import User, AnonymousUser
from django.test import RequestFactory
from django.urls import reverse
from .models import Cart, Profile
from mixer.backend.django import mixer
import pytest

@pytest.mark.django_db
class TestViews:
    def test_cart_authenticated(self):
        user = mixer.blend(User)
        profile = mixer.blend(Profile, user=user)
        mixer.blend(Cart, profile=profile)
        path = reverse("shop:cart")
        request = RequestFactory().get(path)
        request.user = user
        response = cart(request)
        assert response.status_code == 200

    def test_cart_unauthenticated(self):
        path = reverse("shop:cart")
        request = RequestFactory().get(path)
        request.user =  AnonymousUser()
        response = cart(request)
        assert "login" in response.url