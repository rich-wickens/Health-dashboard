from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date
from decimal import Decimal
from .models import Smoking, Weight
from freezegun import freeze_time
from django.core.exceptions import ValidationError

class SmokingModelTests(TestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='password')
        # Create a Smoking instance for testing
        self.smoking = Smoking.objects.create(
            user=self.user,
            start_date=date(2019, 11, 6),
            quit_date=date(2022, 2, 28),
            cost_per_pack=Decimal('20.18'),
            cigarettes_per_day=25
        )

    @freeze_time("2024-06-29")
    def test_time_since_quit_breakdown(self):
        # Mock the current date to ensure consistent test results
        time_breakdown = self.smoking.time_since_quit_breakdown()
        # Assert the expected values for years, months, and days
        self.assertEqual(time_breakdown['years_months_days_hours_minutes_seconds']['years'], 2)
        self.assertEqual(time_breakdown['years_months_days_hours_minutes_seconds']['months'], 4)
        self.assertEqual(time_breakdown['years_months_days_hours_minutes_seconds']['days'], 1)
        # Assert the values for hours, minutes, and seconds are greater than or equal to 0
        self.assertGreaterEqual(time_breakdown['years_months_days_hours_minutes_seconds']['hours'], 0)
        self.assertGreaterEqual(time_breakdown['years_months_days_hours_minutes_seconds']['minutes'], 0)
        self.assertGreaterEqual(time_breakdown['years_months_days_hours_minutes_seconds']['seconds'], 0)

    @freeze_time("2024-06-29")
    def test_money_saved(self):
        # Calculate the expected money saved
        days_quit = (date(2024, 6, 29) - date(2022, 2, 28)).days
        packs_per_day = Decimal(25) / Decimal(20)
        expected_money_saved = Decimal(days_quit) * packs_per_day * Decimal('20.18')

        # Assert the money_saved method returns the expected value
        self.assertAlmostEqual(self.smoking.money_saved(), expected_money_saved, places=2)

    @freeze_time("2024-06-29")
    def test_negative_minutes(self):
        # Modify quit_date to the same as the current date to result in 0 days, minutes, and seconds
        self.smoking.quit_date = date(2024, 6, 29)
        self.smoking.save()

        # Call the method to get the time breakdown
        time_breakdown = self.smoking.time_since_quit_breakdown()

        # Assert the expected values for years, months, and days
        self.assertEqual(time_breakdown['years_months_days_hours_minutes_seconds']['years'], 0)
        self.assertEqual(time_breakdown['years_months_days_hours_minutes_seconds']['months'], 0)
        self.assertEqual(time_breakdown['years_months_days_hours_minutes_seconds']['days'], 0)
        # Assert the values for hours, minutes, and seconds are greater than or equal to 0
        self.assertGreaterEqual(time_breakdown['years_months_days_hours_minutes_seconds']['hours'], 0)
        self.assertGreaterEqual(time_breakdown['years_months_days_hours_minutes_seconds']['minutes'], 0)
        self.assertGreaterEqual(time_breakdown['years_months_days_hours_minutes_seconds']['seconds'], 0)

    @freeze_time("2024-06-01")
    def test_negative_months(self):
        # Modify quit_date to a time that would result in negative months
        self.smoking.quit_date = date(2023, 8, 29)
        self.smoking.save()

        # Call the method to get the time breakdown
        time_breakdown = self.smoking.time_since_quit_breakdown()

        # Assert the expected values for years, months, and days
        self.assertEqual(time_breakdown['years_months_days_hours_minutes_seconds']['years'], 0)
        self.assertEqual(time_breakdown['years_months_days_hours_minutes_seconds']['months'], 9)
        self.assertGreaterEqual(time_breakdown['years_months_days_hours_minutes_seconds']['days'], 0)
        self.assertGreaterEqual(time_breakdown['years_months_days_hours_minutes_seconds']['hours'], 0)
        self.assertGreaterEqual(time_breakdown['years_months_days_hours_minutes_seconds']['minutes'], 0)
        self.assertGreaterEqual(time_breakdown['years_months_days_hours_minutes_seconds']['seconds'], 0)

    @freeze_time("2024-01-01")
    def test_negative_months_from_negative_days(self):
        # Modify quit_date to a time just before the current date in the previous month
        self.smoking.quit_date = date(2023, 12, 31)
        self.smoking.save()

        # Call the method to get the time breakdown
        time_breakdown = self.smoking.time_since_quit_breakdown()

        # Assert the expected values for years, months, and days
        self.assertEqual(time_breakdown['years_months_days_hours_minutes_seconds']['years'], 0)
        self.assertEqual(time_breakdown['years_months_days_hours_minutes_seconds']['months'], 0)
        self.assertEqual(time_breakdown['years_months_days_hours_minutes_seconds']['days'], 1)
        self.assertGreaterEqual(time_breakdown['years_months_days_hours_minutes_seconds']['hours'], 0)
        self.assertGreaterEqual(time_breakdown['years_months_days_hours_minutes_seconds']['minutes'], 0)
        self.assertGreaterEqual(time_breakdown['years_months_days_hours_minutes_seconds']['seconds'], 0)

class WeightModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_bmi_calculation(self):
        weight_entry = Weight.objects.create(
            user=self.user,
            date=date.today(),
            height=1.75,
            weight=70.0,
            ethnicity='White'
        )
        self.assertAlmostEqual(weight_entry.bmi, 22.86, places=2)

    def test_get_bmi_category(self):
        weight_entry = Weight.objects.create(
            user=self.user,
            date=date.today(),
            height=1.75,
            weight=70.0,
            ethnicity='White'
        )
        self.assertEqual(weight_entry.get_bmi_category(), 'Healthy')

    def test_bmi_category_asian_black(self):
        weight_entry = Weight.objects.create(
            user=self.user,
            date=date.today(),
            height=1.65,
            weight=70.0,
            ethnicity='Asian'
        )
        self.assertEqual(weight_entry.get_bmi_category(), 'Overweight')

    def test_waist_circumference_healthy(self):
        weight_entry = Weight.objects.create(
            user=self.user,
            date=date.today(),
            height=1.75,
            weight=70.0,
            waist_circumference=80.0,
            ethnicity='White'
        )
        self.assertTrue(weight_entry.is_waist_circumference_healthy())

    def test_waist_circumference_unhealthy(self):
        weight_entry = Weight.objects.create(
            user=self.user,
            date=date.today(),
            height=1.75,
            weight=70.0,
            waist_circumference=90.0,
            ethnicity='White'
        )
        self.assertFalse(weight_entry.is_waist_circumference_healthy())

    def test_waist_circumference_none(self):
        weight_entry = Weight.objects.create(
            user=self.user,
            date=date.today(),
            height=1.75,
            weight=70.0,
            waist_circumference=None,
            ethnicity='White'
        )
        self.assertIsNone(weight_entry.is_waist_circumference_healthy())

    def test_string_representation(self):
        weight_entry = Weight.objects.create(
            user=self.user,
            date=date.today(),
            height=1.75,
            weight=70.0,
            ethnicity='White'
        )
        expected_str = f"{self.user.username} - {weight_entry.date} - BMI: {weight_entry.bmi:.2f} - {weight_entry.get_bmi_category()}"
        self.assertEqual(str(weight_entry), expected_str)

    def test_height_zero_validation(self):
        weight_entry = Weight(
            user=self.user,
            date=date.today(),
            height=0.0,
            weight=70.0,
            ethnicity='White'
        )
        with self.assertRaises(ValidationError):
            weight_entry.save()

    def test_negative_height_validation(self):
        weight_entry = Weight(
            user=self.user,
            date=date.today(),
            height=-1.75,
            weight=70.0,
            ethnicity='White'
        )
        with self.assertRaises(ValidationError):
            weight_entry.save()

    def test_negative_weight_validation(self):
        weight_entry = Weight(
            user=self.user,
            date=date.today(),
            height=1.75,
            weight=-70.0,
            ethnicity='White'
        )
        with self.assertRaises(ValidationError):
            weight_entry.save()

    def test_ethnicity_choice_validation(self):
        weight_entry = Weight(
            user=self.user,
            date=date.today(),
            height=1.75,
            weight=70.0,
            ethnicity='Invalid'
        )
        with self.assertRaises(ValidationError):
            weight_entry.save()        
