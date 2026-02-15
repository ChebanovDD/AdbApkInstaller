import unittest
from unittest.mock import patch
from install_apks import set_enabled_accessibility


class TestSetEnabledAccessibility(unittest.TestCase):
    """Tests for the set_enabled_accessibility function"""

    @patch('install_apks.run')
    def test_empty_services_list(self, mock_run):
        """Test with an empty list of services"""
        set_enabled_accessibility([])
        mock_run.assert_called_once_with('shell settings put secure enabled_accessibility_services ""')

    @patch('install_apks.run')
    def test_single_service(self, mock_run):
        """Test with a single accessibility service"""
        set_enabled_accessibility(['com.example.service/.AccessibilityService'])
        mock_run.assert_called_once_with(
            'shell settings put secure enabled_accessibility_services "com.example.service/.AccessibilityService"'
        )

    @patch('install_apks.run')
    def test_multiple_services(self, mock_run):
        """Test with multiple accessibility services"""
        services = ['com.example.service1/.Service1', 'com.example.service2/.Service2']
        set_enabled_accessibility(services)
        mock_run.assert_called_once_with(
            'shell settings put secure enabled_accessibility_services "com.example.service1/.Service1:com.example.service2/.Service2"'
        )

    @patch('install_apks.run')
    def test_services_joined_with_colon(self, mock_run):
        """Test that services are properly joined with colons"""
        services = ['service1', 'service2', 'service3']
        set_enabled_accessibility(services)
        expected_cmd = 'shell settings put secure enabled_accessibility_services "service1:service2:service3"'
        mock_run.assert_called_once_with(expected_cmd)

    @patch('install_apks.run')
    def test_correct_adb_command_format(self, mock_run):
        """Test that the ADB command format is correct"""
        services = ['com.android.talkback/.TalkBackService']
        set_enabled_accessibility(services)
        
        # Verify the call
        call_args = mock_run.call_args[0][0]
        self.assertIn('shell settings put secure enabled_accessibility_services', call_args)
        self.assertIn('com.android.talkback/.TalkBackService', call_args)
        self.assertTrue(call_args.startswith('shell settings put'))


if __name__ == '__main__':
    unittest.main()
