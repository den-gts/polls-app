import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

def test_health_check(api_client):
    response = api_client.get(reverse('health_check'))

    assert response.status_code == status.HTTP_200_OK