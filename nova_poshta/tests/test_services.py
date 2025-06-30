import pytest
from unittest.mock import patch, Mock
from nova_poshta.services import NovaPoshtaService
import requests


@pytest.mark.django_db
class TestNovaPoshtaService:
    def test_service_initialization(self, nova_poshta_service):
        """Тест ініціалізації сервісу"""
        assert nova_poshta_service.api_key == "test_api_key"
        assert nova_poshta_service.API_URL == "https://api.novaposhta.ua/v2.0/json/"
    
    @patch('nova_poshta.services.requests.post')
    @patch('nova_poshta.services.cache.get')
    @patch('nova_poshta.services.cache.set')
    def test_get_cities_success(self, mock_cache_set, mock_cache_get, mock_post, 
                                nova_poshta_service, mock_api_response_cities):
        """Тест успішного отримання міст"""
        # Налаштування моків
        mock_cache_get.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = mock_api_response_cities
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Виклик функції
        result = nova_poshta_service.get_cities("Київ")
        
        # Перевірки
        assert len(result) == 2
        assert result[0]['ref'] == "city_ref_1"
        assert result[0]['description'] == "Київ"
        assert result[1]['ref'] == "city_ref_2"
        assert result[1]['description'] == "Харків"
        
        # Перевірка що результат кешується
        mock_cache_set.assert_called_once()
    
    @patch('nova_poshta.services.requests.post')
    @patch('nova_poshta.services.cache.get')
    def test_get_cities_from_cache(self, mock_cache_get, mock_post, nova_poshta_service):
        """Тест отримання міст з кешу"""
        cached_data = [{"ref": "cached_ref", "description": "Cached City"}]
        mock_cache_get.return_value = cached_data
        
        result = nova_poshta_service.get_cities("Київ")
        
        assert result == cached_data
        # API не викликається коли є кеш
        mock_post.assert_not_called()
    
    @patch('nova_poshta.services.requests.post')
    @patch('nova_poshta.services.cache.get')
    def test_get_cities_api_error(self, mock_cache_get, mock_post, 
                                  nova_poshta_service, mock_api_error_response):
        """Тест обробки помилки API при отриманні міст"""
        mock_cache_get.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = mock_api_error_response
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = nova_poshta_service.get_cities("Київ")
        
        assert result == []
    
    @patch('nova_poshta.services.requests.post')
    @patch('nova_poshta.services.cache.get')
    def test_get_cities_request_exception(self, mock_cache_get, mock_post, nova_poshta_service):
        """Тест обробки помилки запиту при отриманні міст"""
        mock_cache_get.return_value = None
        mock_post.side_effect = requests.RequestException("Connection error")
        
        result = nova_poshta_service.get_cities("Київ")
        
        assert result == []
    
    @patch('nova_poshta.services.requests.post')
    @patch('nova_poshta.services.cache.get')
    @patch('nova_poshta.services.cache.set')
    def test_get_warehouses_success(self, mock_cache_set, mock_cache_get, mock_post,
                                    nova_poshta_service, mock_api_response_warehouses):
        """Тест успішного отримання відділень"""
        mock_cache_get.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = mock_api_response_warehouses
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = nova_poshta_service.get_warehouses("Київ")
        
        assert len(result) == 2
        assert result[0]['ref'] == "warehouse_ref_1"
        assert result[0]['description'] == "Відділення №1: вул. Тестова, 1"
        mock_cache_set.assert_called_once()
    
    @patch('nova_poshta.services.requests.post')
    @patch('nova_poshta.services.cache.get')
    def test_get_warehouses_api_error(self, mock_cache_get, mock_post,
                                      nova_poshta_service, mock_api_error_response):
        """Тест обробки помилки API при отриманні відділень"""
        mock_cache_get.return_value = None
        mock_response = Mock()
        mock_response.json.return_value = mock_api_error_response
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = nova_poshta_service.get_warehouses("Київ")
        
        assert result == []
