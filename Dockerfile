FROM alpine:edge

# ============================================
# نصب فقط چیزایی که واقعاً لازمه
# ============================================
RUN apk add --no-cache \
    openssh \
    openssh-server \
    python3 \
    py3-pip \
    curl \
    bash

# ============================================
# تنظیم SSH Server
# ============================================
RUN ssh-keygen -A && \
    echo 'root:Quantum2024!@#' | chpasswd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/#Port 22/Port 2222/' /etc/ssh/sshd_config && \
    sed -i 's/#AllowTcpForwarding yes/AllowTcpForwarding yes/' /etc/ssh/sshd_config && \
    sed -i 's/#GatewayPorts no/GatewayPorts yes/' /etc/ssh/sshd_config && \
    sed -i 's/#TCPKeepAlive yes/TCPKeepAlive yes/' /etc/ssh/sshd_config && \
    sed -i 's/#ClientAliveInterval 0/ClientAliveInterval 60/' /etc/ssh/sshd_config && \
    sed -i 's/#ClientAliveCountMax 3/ClientAliveCountMax 3/' /etc/ssh/sshd_config && \
    echo 'Port 2222' >> /etc/ssh/sshd_config && \
    echo 'Port 443' >> /etc/ssh/sshd_config && \
    echo 'Port 80' >> /etc/ssh/sshd_config

# ============================================
# پایتون
# ============================================
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages

COPY . .
RUN chmod +x /app/start.sh

EXPOSE 8000 2222 443 80

CMD ["/bin/bash", "/app/start.sh"]
