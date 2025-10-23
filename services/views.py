from django.shortcuts import render, get_object_or_404
from .models import ServiceCategory, Service


def service_list(request):
    """Список всех услуг"""
    categories = ServiceCategory.objects.filter(is_active=True).prefetch_related(
        "services"
    )
    context = {"categories": categories}
    return render(request, "services/service_list.html", context)


def service_detail(request, slug):
    """Детальная страница услуги"""
    service = get_object_or_404(Service, slug=slug, is_active=True)
    context = {"service": service}
    return render(request, "services/service_detail.html", context)
