import socks
import time
import threading
import argparse
import geoip2.database
import requests
from requests.exceptions import RequestException

# Proxycheck
# by superjulien 
# > https://github.com/Superjulien
# > https://framagit.org/Superjulien
# V0.97

VERSION = "0.97"

def count_proxy_tests(proxy_test_count):
    proxy_test_count[0] += 1

def display_version():
    print(f"Proxycheck {VERSION}")

def download_geoip_database(url, local_path):
    try:
        response = requests.get(url)
        with open(local_path, 'wb') as file:
            file.write(response.content)
    except Exception as e:
        print(f"Failed to download GeoIP database: {str(e)}")
        exit(1)

def check_anonymity_level(session, timeout):
    try:
        response = session.get("https://httpbin.org/headers", timeout=timeout)
        if response.status_code == 200:
            json_data = response.json()
            origin_ip = json_data.get("origin", "")
            headers = response.headers
            x_forwarded_for = headers.get("X-Forwarded-For", "")
            via = headers.get("Via", "")
            if x_forwarded_for:
                return "Transparent"
            elif via:
                return "Anonymous"
            else:
                return "Highly"
    except RequestException:
        return "Failed"

def test_proxy(proxy, results, lock, seen_ips, geoip_reader, country_filter, support_checks, timeout):
    def run_proxy_socks():
        start_time = time.time()
        s = socks.socksocket()
        s.settimeout(timeout)
        s.set_proxy(socks_protocol, ip, port)
        s.connect(('www.google.com', 80))
        end_time = time.time()
        s.close()
        speed = (end_time - start_time) * 1000
        response = geoip_reader.city(ip)
        country = response.country.name
        session = requests.Session()
        session.proxies = {'http': f'socks5://{ip}:{port}', 'https': f'socks5://{ip}:{port}'}
        if support_checks:
            anonymity_level = check_anonymity_level(session, timeout)
            response = session.get("https://httpbin.org/cookies/set?test=1", timeout=timeout)
            supports_cookies = response.status_code == 200 and "test=1" in response.text
            headers = {"Referer": "www.google.com"}
            data = {"key": "value"}
            response = session.post("https://httpbin.org/post", headers=headers, data=data, timeout=timeout)
            supports_referer = response.status_code == 200 and "www.google.com" in response.text
            supports_post = supports_referer
        elif args.anonymity != None :
            anonymity_level = check_anonymity_level(session, timeout)
        with lock:
            if socks_protocol == socks.SOCKS5:
                print_socks_protocol = "socks5"
            elif socks_protocol == socks.SOCKS4:
                print_socks_protocol = "socks4"
            if ip not in seen_ips and (country_filter is None or country_filter.lower() == country.lower()):
                if support_checks:
                    results.append((ip, port, print_socks_protocol, speed, country, supports_cookies, supports_referer, supports_post, anonymity_level))
                else:
                    results.append((ip, port, print_socks_protocol, speed, country,))
                seen_ips.add(ip)
                if support_checks:
                    print(f"[{country}] Proxy {ip}:{port} is a valid {print_socks_protocol} proxy, anonymity level: {anonymity_level}, supports: Cookies={supports_cookies}, Referer={supports_referer}, POST={supports_post}, Speed: {speed:.2f} ms.")
                else:
                    print(f"[{country}] Proxy {ip}:{port} is a valid {print_socks_protocol} proxy. Connection speed: {speed:.2f} ms.")
            return
    ip, port = proxy
    try:
        socks_protocol = socks.SOCKS5
        run_proxy_socks()
    except Exception as e:
        pass
    try:
        socks_protocol = socks.SOCKS4
        run_proxy_socks()
    except Exception as e:
        with lock:
            results.append(("invalid",))
            print(f"Proxy {ip}:{port} is invalid.")
    finally:
        count_proxy_tests(proxy_test_count)

def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def test_proxies_with_threads(proxy_list, num_threads, sleep_duration, geoip_reader, country_filter, support_checks, timeout):
    results = []
    chunk_size = len(proxy_list) // num_threads
    threads = []
    lock = threading.Lock()
    unique_proxies = set(proxy_list)
    for chunk in chunk_list(list(unique_proxies), chunk_size):
        for proxy in chunk:
            thread = threading.Thread(target=test_proxy, args=(proxy, results, lock, unique_proxies, geoip_reader, country_filter, support_checks, timeout))
            thread.start()
            threads.append(thread)
            if sleep_duration > 0:
                time.sleep(sleep_duration / 1000)
    for thread in threads:
        thread.join()
    return results

def load_proxies_from_file(filename):
    proxies = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split(':')
                    if len(parts) == 2:
                        ip, port = parts
                        proxies.append((ip, int(port)))
                    else:
                        print(f"Ignored: Invalid format for line: {line}")
    except FileNotFoundError:
        print(f"File {filename} not found.")
    return proxies

def count_lines(file_path):
    try:
        with open(file_path, 'r') as file:
            return sum(1 for line in file)
    except FileNotFoundError:
        return 0

def verify_proxies(filename):
    seen_ips = set()
    total_lines = 0
    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split(':')
                    if len(parts) == 2:
                        ip, port = parts
                        seen_ips.add((ip, int(port)))
                        total_lines += 1
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return 0
    return len(seen_ips)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Proxycheck')
    parser.add_argument('-t', '--threads', type=int, default=1,
                        help='Number of threads (default: 1)')
    parser.add_argument('-ms', '--sleep_ms', type=int, default=0,
                        help='Sleep duration in milliseconds between scans (default: 0)')
    parser.add_argument('-c', '--country', type=str, default=None,
                        help='Filter results by country (default: None)')
    parser.add_argument('-s', '--support', action='store_true',
                        help='Enable support checks (Anonymity level, Cookies, Referer, POST)')
    parser.add_argument('-ap', '--all_print', action='store_true',
                    help='Enable all print top socks information on text top file')
    parser.add_argument('-a', '--anonymity', type=str, default=None,
                    help='Filter results by anonymity level (e.g., Transparent, Anonymous, Highly)')
    parser.add_argument('proxy_file', metavar='proxy_file', nargs='?', default=None,
                        help='Path to the proxy list file')
    parser.add_argument('-v', '--version', action='store_true', help='Display the version and exit')
    parser.add_argument('-to', '--timeout', type=float, default=10.0,
                        help='Set the timeout for proxy connections in seconds (default: 10.0)')
    args = parser.parse_args()
    if args.version:
        display_version()
        exit(0)
    if args.proxy_file is None:
        print(f"\n")
        print("Error: Please provide the path to the proxy list file.")
        print(f"\n")
        parser.print_help()
        exit(1)
    geoip_database_url = 'https://git.io/GeoLite2-City.mmdb'
    download_geoip_database(geoip_database_url, 'GeoLite2-City.mmdb')
    proxy_list = load_proxies_from_file(args.proxy_file)
    proxy_test_count = [0]
    if proxy_list:
        anonymity_filter = args.anonymity
        total_proxies = verify_proxies(args.proxy_file)
        num_threads = args.threads
        sleep_duration = args.sleep_ms
        country_filter = args.country
        support_checks = args.support
        all_print = args.all_print
        timeout = args.timeout
        start_scan_time = time.time()
        geoip_reader = geoip2.database.Reader('GeoLite2-City.mmdb')
        results = test_proxies_with_threads(proxy_list, num_threads, sleep_duration, geoip_reader, country_filter, support_checks, timeout)
        end_scan_time = time.time()
        total_scan_time = end_scan_time - start_scan_time
        socks5_results = [result for result in results if result != ("invalid",) and result[2] == "socks5"]
        socks4_results = [result for result in results if result != ("invalid",) and result[2] == "socks4"]
        socks5_results.sort(key=lambda x: x[3])
        socks4_results.sort(key=lambda x: x[3])
        socks5_results = socks5_results[::-1]
        socks4_results = socks4_results[::-1]
        output_files = ['top_socks5.txt', 'top_socks4.txt']
        protocol_results_list = [socks5_results, socks4_results]
        with open(output_files[0], 'w') as socks5_file, open(output_files[1], 'w') as socks4_file:
            for protocol_results, output_file in zip(protocol_results_list, [socks5_file, socks4_file]):
                seen_ips = set()
                for result in protocol_results:
                    if support_checks:
                        ip, port, protocol, speed, country, supports_cookies, supports_referer, supports_post, anonymity_level = result
                    else:
                        ip, port, protocol, speed, country = result
                    if (country_filter is None or country_filter.lower() == country.lower()) and (anonymity_filter is None or anonymity_filter.lower() == anonymity_filter.lower()) and ip not in seen_ips:
                        output_file.write(f"{ip}:{port}")
                        if all_print:
                            output_file.write(f" - Country: {country}, Speed: {speed:.2f} ms")
                        if all_print and support_checks:
                            output_file.write(f", Anonymity level: {anonymity_level}, Cookies: {supports_cookies}, Referer: {supports_referer}, POST: {supports_post}")
                        output_file.write("\n")
                        seen_ips.add(ip)
        socks5_lines = count_lines('top_socks5.txt')
        socks4_lines = count_lines('top_socks4.txt')
        print("-------------------------------------------------")
        print(f"Valid SOCKS5 proxies found: {socks5_lines}")
        print(f"Valid SOCKS4 proxies found: {socks4_lines}")
        print(f"Total number of proxies tested: {str(proxy_test_count)[1:-1]}/{total_proxies}")
        print(f"Total scan time: {total_scan_time:.2f} seconds")
    else:
        print("No proxies were loaded from the file.")
