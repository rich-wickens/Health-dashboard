from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date
from decimal import Decimal
from .models import Smoking
from freezegun import freeze_time

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
