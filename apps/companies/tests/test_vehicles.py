import json
from datetime import date

from django.test import TestCase
from django.urls import reverse

from apps.companies.models import Vehicle

from .factories import make_company


class VehicleManagementTests(TestCase):
    def setUp(self):
        self.company = make_company(email='company1@b.tg')
        self.other = make_company(email='company2@b.tg')
        self.vehicle = Vehicle.objects.create(
            company=self.company, registration_number='TG-1234-BR',
            brand_model='Toyota Coaster', category=Vehicle.Category.MINIBUS,
            seats=30, technical_inspection_expiry=date(2027, 1, 1),
            insurance_policy_number='POL-001',
        )

    def test_vehicle_list_requires_login(self):
        self.assertEqual(self.client.get(reverse('vehicles:list')).status_code, 302)

    def test_company_only_sees_own_vehicles(self):
        self.client.force_login(self.other.user)
        self.assertNotContains(self.client.get(reverse('vehicles:list')), 'TG-1234-BR')

    def test_owner_sees_its_vehicle(self):
        self.client.force_login(self.company.user)
        response = self.client.get(reverse('vehicles:list'))
        self.assertContains(response, 'TG-1234-BR')
        self.assertContains(response, 'company1@b.tg')  # nom affiché par le gabarit
        self.assertNotContains(response, 'None')

    def test_owner_can_create_vehicle(self):
        self.client.force_login(self.company.user)
        response = self.client.post(reverse('vehicles:create'), {
            'registration_number': 'tg 9999 az', 'brand_model': 'Scania', 'category': 'vip', 'seats': 50,
            'technical_inspection_expiry': '2027-01-01', 'insurance_policy_number': 'POL-2', 'status': 'active',
        })
        self.assertRedirects(response, reverse('vehicles:list'))
        self.assertEqual(Vehicle.objects.get(registration_number='TG9999AZ').company, self.company)

    def test_owner_can_update_vehicle(self):
        self.client.force_login(self.company.user)
        response = self.client.post(reverse('vehicles:update', args=[self.vehicle.pk]), {
            'registration_number': 'TG-1234-BR', 'brand_model': 'Toyota Coaster 2026',
            'category': 'minibus', 'seats': 30, 'technical_inspection_expiry': '2027-01-01',
            'insurance_policy_number': 'POL-001', 'status': 'active',
        })
        self.assertRedirects(response, reverse('vehicles:list'))
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.brand_model, 'Toyota Coaster 2026')

    def test_maintenance_toggle(self):
        self.client.force_login(self.company.user)
        self.client.post(reverse('vehicles:maintenance', args=[self.vehicle.pk]))
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.status, Vehicle.Status.MAINTENANCE)

    def test_other_company_cannot_delete_vehicle(self):
        self.client.force_login(self.other.user)
        response = self.client.post(reverse('vehicles:delete', args=[self.vehicle.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Vehicle.objects.filter(pk=self.vehicle.pk).exists())


class VehicleApiTests(TestCase):
    def setUp(self):
        self.company = make_company(email='company1@b.tg')
        self.other = make_company(email='company2@b.tg')
        self.vehicle = Vehicle.objects.create(
            company=self.company, registration_number='TG-1234-BR', brand_model='Toyota Coaster',
            seats=30, technical_inspection_expiry=date(2027, 1, 1), insurance_policy_number='POL-001',
        )
        self.client.force_login(self.company.user)

    def test_list_is_scoped_to_the_company(self):
        self.assertEqual(self.client.get(reverse('vehicles:api')).json()['count'], 1)
        self.client.force_login(self.other.user)
        self.assertEqual(self.client.get(reverse('vehicles:api')).json()['count'], 0)

    def test_create(self):
        response = self.client.post(reverse('vehicles:api'), json.dumps({
            'registration_number': 'TG-1-A', 'brand_model': 'Scania', 'category': 'vip', 'seats': 50,
            'technical_inspection_expiry': '2027-06-30', 'insurance_policy_number': 'P', 'status': 'active',
        }), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Vehicle.objects.get(pk=response.json()['id']).company, self.company)

    def test_invalid_json_returns_400(self):
        response = self.client.post(reverse('vehicles:api'), '{oops', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_other_company_gets_404(self):
        self.client.force_login(self.other.user)
        url = reverse('vehicles:api_detail', args=[self.vehicle.pk])
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(self.client.delete(url).status_code, 404)
        self.assertTrue(Vehicle.objects.filter(pk=self.vehicle.pk).exists())

    def test_patch_changes_only_the_given_field(self):
        url = reverse('vehicles:api_detail', args=[self.vehicle.pk])
        response = self.client.patch(url, json.dumps({'seats': 25}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.seats, 25)
        self.assertEqual(self.vehicle.brand_model, 'Toyota Coaster')
