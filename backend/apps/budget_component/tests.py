from django.test import TestCase
from apps.organization.models import Company, Department, Position
from apps.budget_component.models import BudgetComponent, TemplateRAPHeader


class BudgetComponentAutoDeactivateTestCase(TestCase):
    def setUp(self):
        # 1. Create a Company
        self.company = Company.objects.create(
            company_code='TST',
            company_name='Test Company'
        )
        
        # 2. Create a Department
        self.department = Department.objects.create(
            company=self.company,
            code='DEPT-A',
            name='Department A'
        )
        
        # 3. Create a Position
        self.position = Position.objects.create(
            department=self.department,
            code='POS-A',
            name='Position A'
        )

    def test_create_new_active_deactivates_existing_active(self):
        # Create first budget component as active
        bc1 = BudgetComponent.objects.create(
            company=self.company,
            department=self.department,
            position=self.position,
            cost_category=BudgetComponent.CostCategory.CAPEX,
            is_active=True
        )
        
        # Create template header for it
        tpl1 = TemplateRAPHeader.objects.create(
            budget_component=bc1,
            template_name="Template RAP 1",
            is_active=True
        )
        
        self.assertTrue(bc1.is_active)
        self.assertTrue(tpl1.is_active)
        
        # Create second budget component as active for the same position and cost category
        bc2 = BudgetComponent.objects.create(
            company=self.company,
            department=self.department,
            position=self.position,
            cost_category=BudgetComponent.CostCategory.CAPEX,
            is_active=True
        )
        
        # Refresh from db
        bc1.refresh_from_db()
        tpl1.refresh_from_db()
        
        # bc1 and its template should be deactivated
        self.assertFalse(bc1.is_active)
        self.assertFalse(tpl1.is_active)
        self.assertTrue(bc2.is_active)

    def test_create_inactive_does_not_deactivate_existing_active(self):
        bc1 = BudgetComponent.objects.create(
            company=self.company,
            department=self.department,
            position=self.position,
            cost_category=BudgetComponent.CostCategory.CAPEX,
            is_active=True
        )
        
        bc2 = BudgetComponent.objects.create(
            company=self.company,
            department=self.department,
            position=self.position,
            cost_category=BudgetComponent.CostCategory.CAPEX,
            is_active=False
        )
        
        bc1.refresh_from_db()
        self.assertTrue(bc1.is_active)
        self.assertFalse(bc2.is_active)

    def test_update_inactive_to_active_deactivates_existing_active(self):
        bc1 = BudgetComponent.objects.create(
            company=self.company,
            department=self.department,
            position=self.position,
            cost_category=BudgetComponent.CostCategory.CAPEX,
            is_active=True
        )
        
        bc2 = BudgetComponent.objects.create(
            company=self.company,
            department=self.department,
            position=self.position,
            cost_category=BudgetComponent.CostCategory.CAPEX,
            is_active=False
        )
        
        # Verify first is active, second is inactive
        self.assertTrue(bc1.is_active)
        self.assertFalse(bc2.is_active)
        
        # Activate bc2
        bc2.is_active = True
        bc2.save()
        
        bc1.refresh_from_db()
        self.assertFalse(bc1.is_active)
        self.assertTrue(bc2.is_active)

    def test_null_position_does_not_deactivate_others(self):
        # Creating two active components with null position should not deactivate each other
        bc1 = BudgetComponent.objects.create(
            company=self.company,
            department=self.department,
            position=None,
            cost_category=BudgetComponent.CostCategory.CAPEX,
            is_active=True
        )
        
        bc2 = BudgetComponent.objects.create(
            company=self.company,
            department=self.department,
            position=None,
            cost_category=BudgetComponent.CostCategory.CAPEX,
            is_active=True
        )
        
        bc1.refresh_from_db()
        self.assertTrue(bc1.is_active)
        self.assertTrue(bc2.is_active)
