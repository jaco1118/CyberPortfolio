# Subdomain Enum

- OSINT - SSL/TLS Certicates
    - [crt.sh](https://crt.sh/)
- OSINT - Search Engines
    - `site:*.domain.com -site:www.domain.com`
- DNS Brutefoce
    - `gobuster dns -d [example.com](http://example.com) -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -t 40 -o gobuster_dns.txt`
    - `python3 [sublist3r.py](http://sublist3r.py/) -d [example.com](http://example.com/) -o subdomains.txt -t 25 -e google,bing -v`

### Subdomain enumeration — concise plaintext workflow

1. Run Sublist3r for quick passive results.
2. Query crt.sh for certificate names.
3. Run Amass passive for additional OSINT.
4. Run subfinder/assetfinder for more passive hits.
5. Aggregate and dedupe all passive outputs into `passive.txt`.
6. Resolve `passive.txt` to IPs (dnsx or massdns) and save `resolved.txt`.
7. Check for wildcard DNS (dig random-<rand>.domain). If wildcard, note and treat results with IP/content filters.
8. If passive is insufficient, run DNS brute-force (gobuster dns or massdns+altdns) and append to candidates.
9. Resolve brute results and merge with `resolved.txt`.
10. Probe for web services (httpx) to produce `alive.txt` (URLs with status/title).
11. Run quick port scan on `alive.txt` or `resolved.txt` (naabu or nmap top-ports) and save `ports.txt`.
12. Perform vhost discovery (gobuster vhost) and check for takeover candidates (subjack/nuclei takeover templates).
13. Run content discovery on live hosts (ffuf/gobuster with appropriate wordlists), filter noise by response size/title.
14. Validate and triage findings manually (verify interesting hosts, check headers, CVEs).
15. Produce final list `final.txt` and short report: host, service, evidence, risk, recommended action.

Notes: passive → resolve → brute → probe → scan → fuzz → triage. Detect wildcard early. Save raw outputs. Only test authorized targets.