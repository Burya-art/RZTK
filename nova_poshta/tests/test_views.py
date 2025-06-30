import pytest
from unittest.mock import patch
from django.test import Client
from django.urls import reverse
import json


@pytest.mark.django_db  
class TestNovaPoshtaViews:
    @patch('nova_poshta.views.nova_poshta_service.get_cities')
    def test_get_cities_success(self, mock_get_cities, client):
        """Тест успішного отримання міст через view"""
        mock_cities = [
            {"ref": "city_ref_1", "description": "Київ"},
            {"ref": "city_ref_2", "description": "Харків"}
        ]
        mock_get_cities.return_value = mock_cities
        
        response = client.get('/nova-poshta/cities/?city=Київ')
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert 'cities' in data
        assert len(data['cities']) == 2
        assert data['cities'][0]['description'] == "Київ"
        mock_get_cities.assert_called_once_with("Київ")
    
    def test_get_cities_missing_parameter(self, client):
        """Тест помилки при відсутності параметру city"""
        response = client.get('/nova-poshta/cities/')
        
        assert response.status_code == 400
        data = json.loads(response.content)
        assert 'error' in data
        assert data['error'] == "Місто обов'язкове"
    
    @patch('nova_poshta.views.nova_poshta_service.get_cities')
    def test_get_cities_empty_parameter(self, mock_get_cities, client):
        """Тест помилки при порожньому параметрі city"""
        response = client.get('/nova-poshta/cities/?city=')
        
        assert response.status_code == 400
        data = json.loads(response.content)
        assert 'error' in data
        mock_get_cities.assert_not_called()
    
    @patch('nova_poshta.views.nova_poshta_service.get_warehouses')
    def test_get_warehouses_success(self, mock_get_warehouses, client):
        """Тест успішного отримання відділень через view"""
        mock_warehouses = [
            {"ref": "warehouse_ref_1", "description": "Відділення №1"},
            {"ref": "warehouse_ref_2", "description": "Відділення №2"}
        ]
        mock_get_warehouses.return_value = mock_warehouses
        
        response = client.get('/nova-poshta/warehouses/?city=Київ')
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert 'warehouses' in data
        assert len(data['warehouses']) == 2
        assert data['warehouses'][0]['description'] == "Відділення №1"
        mock_get_warehouses.assert_called_once_with("Київ")
    
    def test_get_warehouses_missing_parameter(self, client):
        """Тест помилки при відсутності параметру city для відділень"""
        response = client.get('/nova-poshta/warehouses/')
        
        assert response.status_code == 400
        data = json.loads(response.content)
        assert 'error' in data
        assert data['error'] == "Місто обов'язкове"
    
    @patch('nova_poshta.views.nova_poshta_service.get_cities')
    def test_get_cities_post_method(self, mock_get_cities, client):
        """Тест що POST метод також працює через @csrf_exempt"""
        mock_cities = [{"ref": "city_ref_1", "description": "Київ"}]
        mock_get_cities.return_value = mock_cities
        
        response = client.post('/nova-poshta/cities/?city=Київ')
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert 'cities' in data
