# Content Discovery

## Content Discovery Methods

- **robots.txt**
    - Controls which pages search engines can crawl and index
    - Can block specific search engines entirely
- **Favicon**
    - May reveal the framework or CMS in use
    - Check favicon database: https://wiki.owasp.org/index.php/OWASP_favicon_database
    - Get MD5 hash: `curl https://example.com/favicon.ico | md5sum`
- **sitemap.xml**
    - Lists files intended for search engine indexing
    - May expose old or hidden pages
- **Automated Discovery Tools**
    - gobuster - fast directory/file brute-forcing
    - dirb - web content scanner
    - ffuf - fast web fuzzer