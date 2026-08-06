FROM alpine:edge

RUN apk add --no-cache curl bash python3 py3-pip unzip openssh

# Xray
RUN mkdir -p /opt/xray && \
    curl -L https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip -o /tmp/xray.zip && \
    unzip /tmp/xray.zip -d /opt/xray && \
    chmod +x /opt/xray/xray && \
    rm /tmp/xray.zip

# Chisel
RUN curl -L -o /usr/bin/chisel https://github.com/jpillora/chisel/releases/download/v1.10.1/chisel_1.10.1_linux_amd64 && \
    chmod +x /usr/bin/chisel

# SSH Setup
RUN ssh-keygen -A && \
    echo 'root:quantum123' | chpasswd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    echo 'AllowTcpForwarding yes' >> /etc/ssh/sshd_config

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages

COPY . .
RUN chmod +x /app/start.sh

EXPOSE 8443 2222 9000

CMD ["/bin/bash", "/app/start.sh"]
