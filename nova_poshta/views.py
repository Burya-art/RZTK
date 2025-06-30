from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import NovaPoshtaService
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Ініціалізація сервісу
nova_poshta_service = NovaPoshtaService(settings.NOVA_POSHTA_API_KEY)


@csrf_exempt
def get_cities(request):
    """Отримує список міст через Nova Poshta API"""
    city = request.GET.get('city', '')
    if not city:
        return JsonResponse({'error': "Місто обов'язкове"}, status=400)

    cities = nova_poshta_service.get_cities(city)
    logger.debug(f"Returned cities for {city}: {cities}")
    return JsonResponse({'cities': cities})


@csrf_exempt
def get_warehouses(request):
    """Отримує список відділень Nova Poshta"""
    city = request.GET.get('city', '')
    if not city:
        return JsonResponse({'error': "Місто обов'язкове"}, status=400)

    warehouses = nova_poshta_service.get_warehouses(city)
    logger.debug(f"Returned warehouses for {city}: {warehouses}")
    return JsonResponse({'warehouses': warehouses})