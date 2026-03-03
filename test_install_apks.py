import unittest
from unittest.mock import patch
import install_apks
from install_apks import set_enabled_accessibility, get_enabled_accessibility


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


class TestGetEnabledAccessibility(unittest.TestCase):
    """Tests for the get_enabled_accessibility function"""

    @patch('install_apks.run')
    def test_returns_empty_list_on_null(self, mock_run):
        mock_run.return_value = "null"
        self.assertEqual(get_enabled_accessibility(), [])
        mock_run.assert_called_once_with(
            'shell settings get secure enabled_accessibility_services',
            capture=True
        )

    @patch('install_apks.run')
    def test_returns_empty_list_on_empty_string(self, mock_run):
        mock_run.return_value = ""
        self.assertEqual(get_enabled_accessibility(), [])

    @patch('install_apks.run')
    def test_parses_single_service(self, mock_run):
        mock_run.return_value = "com.example.service/.AccessibilityService"
        self.assertEqual(
            get_enabled_accessibility(),
            ['com.example.service/.AccessibilityService']
        )

    @patch('install_apks.run')
    def test_parses_multiple_services(self, mock_run):
        mock_run.return_value = "svc1:svc2:svc3"
        self.assertEqual(get_enabled_accessibility(), ['svc1', 'svc2', 'svc3'])


class TestModeInstallDelay(unittest.TestCase):
    """Ensure a delay occurs between installation and permission application"""

    @patch('install_apks.time.sleep')
    @patch('install_apks.apply_permissions_to_package')
    @patch('install_apks.install_apk')
    @patch('install_apks.APK_DIR')
    def test_delay_after_install(self, mock_apk_dir, mock_install_apk, mock_apply, mock_sleep):
        # prepare fake APK listing
        import pathlib
        fake_path = pathlib.Path('app.apk')
        mock_apk_dir.glob.return_value = [fake_path]

        # permissions_map matching the fake apk name
        permissions_map = {
            'app': {'package': 'com.example.app', 'install_flags': '-r -g'}
        }

        mock_install_apk.return_value = True

        # run the installation mode; it should invoke sleep before applying perms
        from install_apks import mode_install
        mode_install(permissions_map)

        mock_sleep.assert_called_once_with(install_apks.INSTALL_DELAY)
        mock_apply.assert_called_once_with('com.example.app', permissions_map['app'])


if __name__ == '__main__':
    unittest.main()
