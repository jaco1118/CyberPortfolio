# Authenticaiton Bypass

## Username Enumeration with ffuf

### Objective

Use `ffuf` to enumerate valid usernames by fuzzing login endpoints and identifying different error responses.

### Environment

- **Target:** http://target_ip/login
- **Wordlist:** `/usr/share/wordlists/seclists/Usernames/Names/names.txt`
- **Tool:** ffuf v2.x

### Step 1: Username Enumeration

**Error Sentence Identification:** The application returns "Invalid username" for non-existent users and "Invalid password" for valid usernames.

**Command:**

```bash
ffuf -w /usr/share/wordlists/seclists/Usernames/Names/names.txt \
     -X POST \
     -d "username=FUZZ&password=test123" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -u http://target_ip/login \
     -mr "Invalid password"

```

**Arguments Explained:**

- `-w`: Wordlist path for fuzzing
- `-X POST`: HTTP method (POST request)
- `-d`: POST data with FUZZ placeholder for username
- `-H "Content-Type: application/x-www-form-urlencoded"`: HTTP header specifying content type
- `-u`: Target URL
- `-mr`: Match regexp - only show responses containing "Invalid password" (indicating valid username)

### Step 2: Password Brute Force

After identifying valid username(s), use `ffuf` to brute force the password.

**Command:**

```bash
ffuf -w /usr/share/wordlists/seclists/Usernames/Names/names.txt:W1 \
     -w /usr/share/wordlists/rockyou.txt:W2 \
     -X POST \
     -d "username=W1&password=W2" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -u http://target_ip/login \
     -fc 401

```

**Arguments Explained:**

- `-w wordlist:W1`: First wordlist (usernames) assigned to W1 placeholder
- `-w wordlist:W2`: Second wordlist (passwords) assigned to W2 placeholder
- `-d "username=W1&password=W2"`: POST data using both placeholders
- `-fc 401`: Filter out HTTP status code 401 (Unauthorised) to show only successful logins

### Findings

- **Valid usernames found:** admin, john, sarah
- **Valid credentials:** admin:password123 (example)
- **Response time difference:** Valid usernames showed 200-300ms response, invalid showed 50-100ms

### Analysis & Mitigation

- **Cause:** Application returns different error messages for invalid usernames vs invalid passwords, enabling username enumeration
- **Mitigation:** Implement generic error messages (e.g., "Invalid credentials"), add rate limiting, implement CAPTCHA after failed attempts, use account lockout policies
- **Detection idea:** Monitor for rapid sequential login attempts from single IP, alert on high volume of 401 responses, implement Web Application Firewall (WAF) rules

---

## Parameter Pollution Detection

### Objective

Identify HTTP Parameter Pollution (HPP) vulnerabilities where servers merge GET and POST parameters, potentially allowing attackers to override URL parameters via POST body.

### Environment

- **Target:** Application with `?email=` parameter in URL
- **Tools:** curl, Burp Suite
- **Vulnerable configuration:** Server-side code using `$_REQUEST` or similar merged parameter arrays

### Step 1: Observation

Observe `?email=` in URL → Identify that the application accepts email parameter via GET request.

### Step 2: Injection Test

Try adding `email=attacker@you.test` in POST body (or duplicate keys) via curl/Burp.

**Command (curl):**

```bash
curl -X POST "http://target_ip/endpoint?email=victim@example.com" \
     -d "email=attacker@you.test" \
     -H "Content-Type: application/x-www-form-urlencoded"

```

**Burp Suite Method:**

- Intercept the request
- Add duplicate `email` parameter in POST body
- Forward and observe response

### Step 3: Verification

Verify response/side-effect → Check which email address was processed by the server (check confirmation emails, database entries, or response messages).

### Step 4: Confirmation

Confirm vulnerability if server uses merged parameters (e.g., `$_REQUEST`) and honours POST over GET.

### Findings

- **Parameter precedence:** POST parameters override GET parameters
- **Vulnerable code pattern:** Use of `$_REQUEST` in PHP or similar merged parameter handling
- **Impact:** Attackers can override intended parameters, potentially leading to unauthorised actions

### Analysis & Mitigation

- **Cause:** Server-side code merges GET and POST parameters without explicit precedence handling
- **Mitigation:** Use explicit parameter sources (`$_GET`, `$_POST`) instead of `$_REQUEST`, implement strict input validation, document expected parameter sources
- **Detection idea:** Monitor for duplicate parameters in requests, implement Web Application Firewall (WAF) rules to detect HPP patterns, log parameter sources for audit trails