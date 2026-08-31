import unittest

from src.maintenance_failover import MaintenanceRequest, decide


class MaintenanceDecisionTests(unittest.TestCase):
    def test_electrical_signal_requires_human_review(self):
        request = MaintenanceRequest("B-204", "Water is leaking near the electrical panel")
        self.assertEqual(decide(request), type(decide(request))("dispatch licensed staff", "human_review", 1))

    def test_routine_request_is_queued(self):
        result = decide(MaintenanceRequest("B-204", "The bathroom fan is noisy"))
        self.assertEqual((result.status, result.reminder_hours), ("queued", 24))


if __name__ == "__main__":
    unittest.main()
