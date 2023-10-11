# ProxyCheck

[![Version](https://img.shields.io/badge/Version-0.97-blue.svg)](https://github.com/Superjulien/Proxycheck) [![License](https://img.shields.io/badge/License-GNU_GPLv3-blue.svg)](https://choosealicense.com/licenses/gpl-3.0/) [![Python](https://img.shields.io/badge/Python_3-14354C?&logo=python&logoColor=white.svg)](https://www.python.org/)

Proxycheck is a proxy testing script that aims to provide comprehensive information about SOCKS proxies. It uses threading to efficiently test multiple proxies simultaneously and includes support for geolocation using GeoIP, checking anonymity levels, and verifying specific features of the proxies.

## Features

- **Multithreaded Testing**: Utilizes multithreading to test proxies concurrently for improved efficiency.
- **Anonymity Check**: Determines the anonymity level of the proxy by making requests to `https://httpbin.org/headers`.
- **Support Checks**: Optionally checks if the proxy supports cookies, referer, and POST requests.
- **GeoIP Integration**: Uses GeoIP data to identify the country of the proxy.
- **Output Files**: Generates output files 'top_socks5.txt' and 'top_socks4.txt' with detailed results.
- **Command-line Interface**: Configurable through command-line arguments for flexibility.

## Requirements

- Python 3.x
- Required Python packages: `PySocks`, `geoip2`, `requests`

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/Superjulien/Proxycheck.git
    ```
2. Navigate to the Directory:

    ```bash
    cd Proxycheck
    ```

3. Install the required packages:

    ```bash
    pip3 install PySocks geoip2 requests
    ```

## Usage

Run Proxycheck from the command line:

```bash
python3 proxycheck.py proxies.txt
```

or with the desired options:

```bash
python3 proxycheck.py -t 4 -ms 500 -c US -s -ap -a Anonymous proxies.txt
```

### Command-line Options

- `-h, --help`: Show help message and exit
- `-t, --threads`: Number of threads (default: 1)
- `-ms, --sleep_ms`: Sleep duration in milliseconds between scans (default: 0)
- `-c, --country`: Filter results by country (default: None)
- `-s, --support`: Enable support checks (Anonymity level, Cookies, Referer, POST)
- `-ap, --all_print`: Enable all print top SOCKS information on text top file
- `-a, --anonymity`: Filter results by anonymity level (e.g., Transparent, Anonymous, Highly)
- `proxy_file`: Path to the proxy list file
- `-v, --version`: Display the version and exit
- `-to, --timeout`: Set the timeout for proxy connections in seconds (default: 10.0)

### Output

Results are saved to 'top_socks5.txt' and 'top_socks4.txt' in the following format:

```
192.168.1.0:8192 - Country: Serbia, Speed: 7392.70 ms, Anonymity level: Highly, Cookies: False, Referer: True, POST: True
```

## Configuration and Optimization

### Changing the GeoIP Database URL

To change the GeoIP database download URL in the Proxycheck script, follow these steps:

1. **Find a New GeoIP Database URL:**
   - Look for a reliable source to download the GeoIP database in MMDB format. Ensure that the source supports direct downloads via a URL.

2. **Replace the Current URL in the Script:**
   - Open the `proxycheck.py` script in a text editor or development environment.

   - Locate the line containing the `geoip_database_url` variable:

     ```python
     geoip_database_url = 'https://git.io/GeoLite2-City.mmdb'
     ```

   - Replace the current URL with the new URL you found:

     ```python
     geoip_database_url = 'https://new-url/to/the/database.mmdb'
     ```

   Make sure the new URL points to the latest version of the GeoIP database you want to use.

3. **Save the Changes:**
   - Save the script after making the modifications.

4. **Run the Script:**
   - Execute the script to check if the new URL works correctly and if the GeoIP database is successfully downloaded.

   ```bash
   python3 proxycheck.py -t 4 -ms 500 -to 50 -c US -s -ap proxies.txt
   ```
   
### Optimizing Proxy Discovery

The performance and effectiveness of proxy testing can be influenced by adjusting the sleep duration (`-ms`) and timeout (`-to`) parameters in the command-line options. Here's how you can experiment with these parameters to potentially discover more valid proxies:

#### 1. **Sleep Duration (`-ms`)**

- The sleep duration represents the time (in milliseconds) that the script pauses between scans of different proxies. Adjusting this value can impact the rate at which proxies are tested.

- **Suggestion:** Experiment with different sleep durations to find an optimal balance. Smaller values (e.g., 100 ms) may lead to faster testing but could increase the chance of getting rate-limited or blocked by certain servers. Larger values (e.g., 1000 ms) provide more time between scans but may slow down the overall testing process.

  ```bash
  python3 proxycheck.py -t <num_threads> -ms <your_chosen_sleep_duration> ...
  ```

#### 2. **Timeout (`-to`)**

- The timeout represents the maximum time (in seconds) that the script waits for a response from a proxy before considering it as invalid. Adjusting this value can impact the script's ability to detect valid proxies in different network conditions.

- **Suggestion:** If you're facing connectivity issues or the script marks proxies as invalid too quickly, consider increasing the timeout value. On the other hand, if the script takes too long to mark proxies as invalid, you may want to decrease the timeout.

  ```bash
  python3 proxycheck.py -t <num_threads> -to <your_chosen_timeout> ...
  ```

## How It Works

Proxycheck is designed to efficiently test and validate SOCKS proxies. Here's a breakdown of how the script works:

1. **Initialization**

    - The script begins by initializing necessary components, including the version, command-line argument parser, and the GeoIP database.

2. **GeoIP Database Download**

    - The GeoIP database is downloaded using the provided URL. This database is crucial for determining the geolocation of each tested proxy.

3. **Proxy List Loading and Verification**

    - Proxies are loaded from the specified text file. The script ensures the uniqueness of proxies and counts the total number of valid proxies.

4. **Threading for Concurrent Testing**

    - The script utilizes threading to test multiple proxies simultaneously, improving the efficiency of the process.

5. **Proxy Testing and Feature Checking**

    - For each proxy, the script tests its validity and checks various features:
      - Connection speed using SOCKS5 and SOCKS4 protocols.
      - Geolocation using the GeoIP database.
      - Anonymity level (Transparent, Anonymous, Highly).
      - Optional support for cookies, referer, and POST requests.

6. **Results Output**

    - Results are categorized and stored in separate files for SOCKS5 and SOCKS4 proxies. The output includes information such as IP address, port, country, speed, and feature support.

7. **Additional Information Output**

    - Optionally, additional information is outputted to a text file if the `-ap` (all print) flag is used, providing more detailed information about each tested proxy.

8. **Summary and Statistics**

    - The script concludes by printing a summary, including the total number of valid SOCKS5 and SOCKS4 proxies found, the total number of proxies tested, and the total scan time.

9. **Files Generated**
    
    - Valid SOCKS5 proxies are stored in `top_socks5.txt`.
    - Valid SOCKS4 proxies are stored in `top_socks4.txt`.

## Upcoming Features

1. **Security Testing:**
   - Implement security tests to detect potentially malicious proxies.

2. **Improved Error Handling:**
   - Add more detailed error messages to facilitate debugging.
   - Handle errors specific to different stages of the process.

3. **Logging:**
   - Integrate a logging system to record results, errors, and other useful information to a file.

4. **Testing Other Proxy Protocols:**
   - Extend the script to support other proxy protocols in addition to SOCKS, such as HTTP or HTTPS.

5. **Advanced Filtering Options:**
   - Add advanced filtering options, for example, based on latency, etc.

6. **IPv6 Support:**
   - Allow testing of IPv6 proxies in addition to the currently supported IPv4 proxies.

7. **Result Export Options:**
    - Add options to export results in different formats such as CSV, JSON, etc.

8. **Advanced Network Performance Testing:**
    - Add more advanced network performance tests to assess the quality of connections.

## Sponsoring

This software is provided to you free of charge, with the hope that if you find it valuable, you'll consider making a donation to a charitable organization of your choice :

- SPA (Society for the Protection of Animals): The SPA is one of the oldest and most recognized organizations in France for the protection of domestic animals. It provides shelters, veterinary care, and works towards responsible adoption.

  [![SPA](https://img.shields.io/badge/Sponsoring-SPA-red.svg)](https://www.la-spa.fr/)

- French Popular Aid: This organization aims to fight against poverty and exclusion by providing food aid, clothing, and organizing recreational activities for disadvantaged individuals.

  [![SPF](https://img.shields.io/badge/Sponsoring-Secours%20Populaire%20Français-red.svg)](https://www.secourspopulaire.fr)

- Doctors Without Borders (MSF): MSF provides emergency medical assistance to populations in danger around the world, particularly in conflict zones and humanitarian crises.

  [![MSF](https://img.shields.io/badge/Sponsoring-Médecins%20Sans%20Frontières-red.svg)](https://www.msf.fr)

- Restaurants of the Heart : Restaurants of the Heart provides meals, emergency accommodation, and social services to the underprivileged.

  [![RDC](https://img.shields.io/badge/Sponsoring-Restaurants%20du%20Cœur-red.svg)](https://www.restosducoeur.org)

- French Red Cross: The Red Cross offers humanitarian aid, emergency relief, first aid training, as well as social and medical activities for vulnerable individuals.

   [![CRF](https://img.shields.io/badge/Sponsoring-Croix%20Rouge%20Française-red.svg)](https://www.croix-rouge.fr)

Every small gesture matters and contributes to making a real difference.

## License

Proxycheck is open-source software released under the [GNU GPLv3 License](https://choosealicense.com/licenses/gpl-3.0/). This license allows users of this software to use it, modify it, distribute it, and share it freely while preserving transparency and collaboration.

## Support
For support email : 

[![Gmail: superjulien](https://img.shields.io/badge/Gmail-Contact%20Me-purple.svg)](mailto:contact.superjulien@gmail.com) [![Tutanota: superjulien](https://img.shields.io/badge/Tutanota-Contact%20Me-green.svg)](mailto:contacts.superjulien@tutanota.com)
