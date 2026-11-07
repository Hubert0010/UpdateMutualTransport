"""Pages de gestion de la flotte."""
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from apps.accounts.decorators import company_required

from ..forms.vehicle import VehicleForm
from ..models import Vehicle
from ..services.vehicles import get_owned_vehicle



@company_required
def vehicle_list(request):
    vehicles = Vehicle.objects.filter(company=request.user.company)
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    category = request.GET.get("category", "")
    if query:
        vehicles = vehicles.filter(Q(registration_number__icontains=query) | Q(brand_model__icontains=query))
    if status in Vehicle.Status.values:
        vehicles = vehicles.filter(status=status)
    if category in Vehicle.Category.values:
        vehicles = vehicles.filter(category=category)
    all_vehicles = Vehicle.objects.filter(company=request.user.company)
    context = {
        "vehicles": vehicles,
        "form": VehicleForm(),
        "total_count": all_vehicles.count(),
        "active_count": all_vehicles.filter(status=Vehicle.Status.ACTIVE).count(),
        "maintenance_count": all_vehicles.filter(status=Vehicle.Status.MAINTENANCE).count(),
        "total_seats": sum(all_vehicles.values_list("seats", flat=True)),
        "query": query, "selected_status": status, "selected_category": category,
        "status_choices": Vehicle.Status.choices, "category_choices": Vehicle.Category.choices,
    }
    return render(request, "vehicles/vehicle_list.html", context)


@company_required
@require_http_methods(["GET", "POST"])
def vehicle_create(request):
    form = VehicleForm(request.POST or None, company=request.user.company)
    if request.method == "POST" and form.is_valid():
        vehicle = form.save(commit=False)
        vehicle.company = request.user.company
        vehicle.save()
        messages.success(request, f"Le véhicule {vehicle.registration_number} a été ajouté.")
        return redirect("vehicles:list")
    messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    return render(request, "vehicles/vehicle_form.html", {"form": form, "page_title": "Ajouter un véhicule"})


@company_required
@require_http_methods(["GET", "POST"])
def vehicle_update(request, pk):
    vehicle = get_owned_vehicle(request.user.company, pk)
    form = VehicleForm(request.POST or None, instance=vehicle, company=request.user.company)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Les informations du véhicule ont été mises à jour.")
        return redirect("vehicles:list")
    return render(request, "vehicles/vehicle_form.html", {"form": form, "vehicle": vehicle, "page_title": "Modifier le véhicule"})


@company_required
@require_POST
def vehicle_delete(request, pk):
    vehicle = get_owned_vehicle(request.user.company, pk)
    plate = vehicle.registration_number
    vehicle.delete()
    messages.success(request, f"Le véhicule {plate} a été supprimé.")
    return redirect("vehicles:list")


@company_required
@require_POST
def vehicle_toggle_maintenance(request, pk):
    vehicle = get_owned_vehicle(request.user.company, pk)
    vehicle.status = Vehicle.Status.MAINTENANCE if vehicle.status == Vehicle.Status.ACTIVE else Vehicle.Status.ACTIVE
    vehicle.save(update_fields=["status", "updated_at"])
    messages.success(request, f"Statut de {vehicle.registration_number} : {vehicle.get_status_display()}.")
    return redirect("vehicles:list")
