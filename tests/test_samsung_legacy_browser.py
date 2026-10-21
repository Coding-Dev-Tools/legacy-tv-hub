import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('legacy_browser', Path(__file__).resolve().parents[1]/'tools/samsung_legacy_browser.py')
browser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(browser)

HOST = '192.168.30.40'
DEVICE = b'<root xmlns="urn:schemas-upnp-org:device-1-0"><device><modelName>UN55HU7250</modelName><manufacturer>Samsung Electronics</manufacturer></device></root>'
RECEIVER = b'<root xmlns="urn:schemas-upnp-org:device-1-0"><device><modelName>UN55HU7250</modelName><serviceList><service><serviceType>urn:samsung.com:service:MultiScreenService:1</serviceType><SCPDURL>/smp_11_</SCPDURL></service></serviceList></device></root>'
APP = b'<service xmlns="urn:dial-multiscreen-org:schemas:dial"><name>Web Browser</name><state>stopped</state></service>'

class BrowserLaunchTests(unittest.TestCase):
    def fixture(self, *, device=DEVICE, advertised=None):
        calls = []
        def request(url, data=None, headers=None):
            calls.append((url, data, headers))
            if url.endswith('/smp_2_'): return 200, {}, device
            if url.endswith('/smp_10_'): return 200, {}, RECEIVER
            if url.endswith('/smp_11_'): return 200, {'Application-URL': advertised or 'http://'+HOST+':8080/ws/app/'}, b''
            return (201, {}, b'') if data is not None else (200, {}, APP)
        return calls, request

    def test_observed_launch_format_and_false_negative_state(self):
        calls, request = self.fixture()
        result = browser.launch(HOST, 'http://example.com/app/', request=request)
        posts = [call for call in calls if call[1] is not None]
        self.assertEqual(posts, [('http://'+HOST+':8080/ws/app/WebBrowser', b'http://example.com/app/', {'Host': HOST, 'Content-Type': 'text/plain'})])
        self.assertTrue(result['launch_request_accepted'])
        self.assertEqual(result['browser_state_advisory'], 'stopped')
        self.assertFalse(result['page_execution_verified'])

    def test_wrong_model_prevents_mutation(self):
        calls, request = self.fixture(device=DEVICE.replace(b'UN55HU7250', b'DIFFERENT'))
        with self.assertRaisesRegex(ValueError, 'identity'):
            browser.launch(HOST, 'https://example.com/', request=request)
        self.assertEqual(len(calls), 1)
        self.assertFalse(any(data is not None for _, data, _ in calls))

    def test_control_endpoint_cannot_redirect_to_another_device(self):
        calls, request = self.fixture(advertised='http://192.168.30.41:8080/ws/app/')
        with self.assertRaisesRegex(ValueError, 'unexpected'):
            browser.launch(HOST, 'https://example.com/', request=request)
        self.assertFalse(any(data is not None for _, data, _ in calls))
        self.assertTrue(all(HOST in url for url, _, _ in calls))

    def test_public_tv_addresses_and_unsafe_urls_fail_before_io(self):
        calls, request = self.fixture()
        for host in ('8.8.8.8', '127.0.0.1', '169.254.169.254', '::1'):
            with self.assertRaises(ValueError): browser.launch(host, 'https://example.com/', request=request)
        for url in ('javascript:alert(1)', 'file:///tmp/test', 'https://user:pass@example.com/', 'https://example.com/\r\nother', 'http://example.com:invalid/'):
            with self.assertRaises(ValueError): browser.launch(HOST, url, request=request)
        self.assertEqual(calls, [])

    def test_malformed_or_cross_origin_advertisement_is_rejected(self):
        for value in (None, 'http://'+HOST+':80018001/ws/apps/', 'http://'+HOST+':8080/ws/app/?token=value', 'http://user:pass@'+HOST+':8080/ws/app/', 'https://'+HOST+':8080/ws/app/'):
            with self.assertRaises(ValueError): browser.control_url(value, HOST)

    def test_appliance_redirect_cannot_move_a_request_to_a_different_host(self):
        with self.assertRaisesRegex(ValueError, 'redirect'):
            browser.NoRedirect().redirect_request(None, None, 302, '', {}, 'http://192.168.30.41/')

if __name__ == '__main__': unittest.main()
