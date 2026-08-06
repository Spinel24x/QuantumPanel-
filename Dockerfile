FROM alpine:edge

RUN apk add --no-cache curl bash python3 py3-pip unzip openssh wget openssl iptables wireguard-tools

# Xray
RUN mkdir -p /opt/xray && \
    curl -L https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip -o /tmp/xray.zip && \
    unzip /tmp/xray.zip -d /opt/xray && \
    chmod +x /opt/xray/xray && rm /tmp/xray.zip

# udp2raw
RUN wget -q https://github.com/wangyu-/udp2raw/releases/download/20230206.0/udp2raw_binaries.tar.gz -O /tmp/u.tar.gz && \
    tar -xzf /tmp/u.tar.gz -C /tmp && \
    cp /tmp/udp2raw_x86 /usr/bin/udp2raw && chmod +x /usr/bin/udp2raw && rm -rf /tmp/u*

# SSH
RUN ssh-keygen -A && echo 'root:quantum123' | chpasswd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages
COPY . .
RUN chmod +x /app/start.sh

EXPOSE 8443 22 9000 51820 5555

CMD ["/bin/bash", "/app/start.sh"]
