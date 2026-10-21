"""Open a web app on an identified Samsung Legacy TV using its advertised DIAL endpoint.

This launches a browser URL. It cannot install firmware or verify service playback.
"""
import argparse
import ipaddress
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

PRIVATE_NETWORKS = tuple(ipaddress.ip_network(value) for value in ('10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16'))

def television_address(value):
    address = ipaddress.ip_address(value)
    if address.version != 4 or not any(address in network for network in PRIVATE_NETWORKS):
        raise ValueError('Use the TV\'s private LAN IPv4 address.')
    return str(address)

def application_url(value):
    if not isinstance(value, str) or any(ord(c) <= 32 for c in value) or any(c in value for c in '<>"\\'):
        raise ValueError('Use a complete HTTP or HTTPS application URL.')
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme not in {'http', 'https'} or not parsed.hostname or parsed.username is not None or parsed.password is not None:
        raise ValueError('Use an HTTP or HTTPS URL without embedded credentials.')
    try:
        parsed.port
        value.encode('ascii')
    except (ValueError, UnicodeError) as error:
        raise ValueError('Use an ASCII URL with a valid port; encode non-ASCII URL characters.') from error
    return value

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        raise ValueError('Refusing a redirect from the identified TV endpoint.')

class HTTP:
    def __init__(self):
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())

    def __call__(self, url, data=None, headers=None):
        request = urllib.request.Request(url, data=data, headers=headers or {}, method='POST' if data is not None else 'GET')
        with self.opener.open(request, timeout=8) as response:
            body = response.read(1024 * 1024 + 1)
            if len(body) > 1024 * 1024:
                raise ValueError('TV response exceeded the expected limit.')
            return response.status, dict(response.headers.items()), body

def control_url(value, host):
    if not isinstance(value, str) or any(ord(c) <= 32 for c in value):
        raise ValueError('The TV did not advertise a DIAL control endpoint.')
    parsed = urllib.parse.urlsplit(value)
    if (parsed.scheme != 'http' or parsed.hostname != host or parsed.port != 8080 or
            parsed.username is not None or parsed.password is not None or parsed.query or parsed.fragment or
            parsed.path not in {'/ws/app/', '/ws/apps/'}):
        raise ValueError('Refusing an unexpected DIAL control endpoint.')
    return value + 'WebBrowser'

def launch(host, url, expected_model='UN55HU7250', request=None):
    host = television_address(host)
    url = application_url(url)
    request = request or HTTP()
    base = 'http://' + host + ':7676'
    # These paths are observed on the first NT14U target, not a universal Samsung discovery implementation.
    status, _, body = request(base + '/smp_2_')
    device = ET.fromstring(body).find('.//{*}device')
    if status != 200 or device is None or device.findtext('{*}modelName') != expected_model or device.findtext('{*}manufacturer') != 'Samsung Electronics':
        raise ValueError('TV identity did not match; no launch was attempted.')
    status, _, body = request(base + '/smp_10_')
    receiver = ET.fromstring(body).find('.//{*}device')
    if status != 200 or receiver is None or receiver.findtext('{*}modelName') != expected_model:
        raise ValueError('Remote receiver identity did not match.')
    service = next((item for item in receiver.findall('{*}serviceList/{*}service') if item.findtext('{*}serviceType') == 'urn:samsung.com:service:MultiScreenService:1'), None)
    path = service.findtext('{*}SCPDURL') if service is not None else None
    if not path or not path.startswith('/smp_') or any(c not in '/smp_0123456789' for c in path):
        raise ValueError('No recognized local multiscreen service description.')
    status, headers, _ = request(base + path)
    if status != 200:
        raise ValueError('Cannot read the multiscreen service description.')
    endpoint = control_url(next((v for k, v in headers.items() if k.lower() == 'application-url'), None), host)
    # The bare Host value and a plain URL body were measured to work on NT14U.
    launch_headers = {'Host': host, 'Content-Type': 'text/plain'}
    status, _, body = request(endpoint, headers={'Host': host})
    description = ET.fromstring(body)
    if status != 200 or description.tag != '{urn:dial-multiscreen-org:schemas:dial}service' or description.findtext('{*}name') != 'Web Browser':
        raise ValueError('The expected browser service was not returned.')
    status, _, _ = request(endpoint, data=url.encode('ascii'), headers=launch_headers)
    if status != 201:
        raise ValueError('Browser launch was not accepted.')
    advisory = 'Unavailable'
    try:
        check_status, _, body = request(endpoint, headers={'Host': host})
        if check_status == 200:
            advisory = ET.fromstring(body).findtext('{*}state') or advisory
    except (OSError, ValueError, ET.ParseError):
        pass
    return {'model': expected_model, 'launch_request_accepted': True,
            'browser_state_advisory': advisory, 'page_execution_verified': False,
            'note': 'Confirm the page on the TV. NT14U can report stopped while a page is executing. This is not an installation or streaming-service test.'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tv', required=True, help='Private IPv4 address of the TV')
    parser.add_argument('--url', required=True, help='Complete URL of the web app to open')
    parser.add_argument('--expected-model', default='UN55HU7250', help='Exact expected model; the only physically tested target is UN55HU7250')
    args = parser.parse_args()
    try:
        print(json.dumps(launch(args.tv, args.url, args.expected_model), indent=2))
    except (OSError, ValueError, ET.ParseError) as error:
        # Network exceptions can contain a request URL. Do not log arbitrary URL data.
        parser.exit(1, 'Browser launch failed (' + type(error).__name__ + '). No firmware operation was attempted.\n')

if __name__ == '__main__':
    main()
