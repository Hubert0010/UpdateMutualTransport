"""API JSON de la flotte, en attendant la mise en place de l'API REST."""
import json

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from apps.accounts.decorators import company_required

from ..forms.vehicle import VehicleForm
from ..models import Vehicle
from ..services.vehicles import get_owned_vehicle


@company_required
@require_http_methods(["GET", "POST"])
def vehicle_api(request):
    if request.method == "GET":
        qs = Vehicle.objects.filter(company=request.user.company)
        return JsonResponse({"results": [serialize(v) for v in qs], "count": qs.count()})
    try:
        data = json.loads(request.body or "{}")
        form = VehicleForm(data, company=request.user.company)
        if not form.is_valid():
            return JsonResponse({"errors": form.errors.get_json_data()}, status=400)
        vehicle = form.save(commit=False)
        vehicle.company = request.user.company
        vehicle.save()
        return JsonResponse(serialize(vehicle), status=201)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"detail": "Corps JSON invalide."}, status=400)


@company_required
@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
def vehicle_api_detail(request, pk):
    vehicle = get_owned_vehicle(request.user.company, pk)
    if request.method == "GET":
        return JsonResponse(serialize(vehicle))
    if request.method == "DELETE":
        vehicle.delete()
        return JsonResponse({"detail": "Véhicule supprimé."})
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Corps JSON invalide."}, status=400)
    if request.method == "PATCH":
        data = {**{field: getattr(vehicle, field) for field in VehicleForm().fields}, **data}
        data["technical_inspection_expiry"] = vehicle.technical_inspection_expiry.isoformat()
    form = VehicleForm(data, instance=vehicle, company=request.user.company)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors.get_json_data()}, status=400)
    return JsonResponse(serialize(form.save()))


def serialize(v):
    return {
        "id": v.pk, "registration_number": v.registration_number, "brand_model": v.brand_model,
        "category": v.category, "category_label": v.get_category_display(), "seats": v.seats,
        "has_ac": v.has_ac, "has_wifi": v.has_wifi, "has_usb": v.has_usb,
        "technical_inspection_expiry": v.technical_inspection_expiry.isoformat(),
        "insurance_policy_number": v.insurance_policy_number, "status": v.status,
        "status_label": v.get_status_display(), "notes": v.notes,
    }
