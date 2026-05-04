# stocks-analyze-and-alert


# List of Issues with yfinance
- **OpenSSL errors** : ``` SSLError('Failed to perform, curl: (35) TLS connect error: error:00000000:invalid library (0):OPENSSL_internal:invalid library (0)  ```

Resolved at ✅ :- https://github.com/ranaroussi/yfinance/issues/2529

Changing the DNS server is the workaround.

Add either the google or cloudflare DNS server to /etc/resolv.conf (Unix systems)

For Google add following two lines:-

    `nameserver 8.8.8.8`
    `nameserver 8.8.4.4`

For Cloudflare add following two lines:-

    `nameserver 1.1.1.1`
    `nameserver 1.0.0.1`

Note!! One of the above two may fail ocassionally, or the response times might be too high depending on your geographical location. So try both.