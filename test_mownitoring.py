#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch

import mownitoring

config_file = "./mownitoring.yml"


class TestMownitoing(unittest.TestCase):

    def test_readconf(self):
        machines = mownitoring.read_conf(config_file)

        # api_cfg
        self.assertEqual(mownitoring.api_cfg["pushover_token"],
                         "T0k3n")

        # machines
        self.assertIsInstance(machines["webserver.example.com"][0]["checks"],
                              list)
        self.assertEqual(machines["db.example.com"][2]["connection"]["ip"],
                         "192.0.2.2")
        self.assertIn("mailq", machines["mail.example.com"][0]["checks"])

        self.assertIn("pushover", machines["db.example.com"][1]["alert"])
        self.assertIn("syslog", machines["db.example.com"][1]["alert"])

        self.assertNotIn("T0k3n", machines)
        self.assertNotIn("token", machines)
        self.assertNotIn("Pushover", machines)

    @patch('syslog.syslog')
    def test_check_notifier(self, mock_syslog):
        test1 = mownitoring.check_notifier(["syslog"])
        self.assertIsInstance(test1, list)
        self.assertEqual(test1[0], mownitoring.notify_syslog)

        test2 = mownitoring.check_notifier(["nonexistent"])
        self.assertEqual(test2, [])

        test3 = mownitoring.check_notifier(["syslog", "pushover"])
        self.assertEqual(test3[0], mownitoring.notify_syslog)
        self.assertEqual(test3[1], mownitoring.notify_pushover)

        test4 = mownitoring.check_notifier(["syslog", "nonexistent"])
        self.assertEqual(test4, [mownitoring.notify_syslog])

    @patch('syslog.syslog')
    @patch('mownitoring.check_notifier')
    @patch('mownitoring.notify_syslog')
    def test_check_alert(self, mock_syslog, mock_check_notifier,
                         mock_notify_syslog):
        mownitoring.check_nrpe = Mock()
        mownitoring.check_nrpe.return_value = 2, 'disk nok'
        mock_check_notifier.return_value = [mownitoring.notify_syslog]
        mownitoring.check_alert("disk1", "webserver.example.com", "5666",
                                "webserver.example.com", ["syslog"])
        mock_syslog.assert_called_once_with("webserver.example.com!" +
                                            "disk1 disk nok")


if __name__ == '__main__':
    unittest.main()
