FROM alpine:latest

RUN apk add --no-cache openssh python3 py3-pip curl unzip

# نصب SSH
RUN ssh-keygen -A && \
    echo 'root:Quantum2024!@#' | chpasswd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/#Port 22/Port 2222/' /etc/ssh/sshd_config

# نصب wstunnel
RUN curl -L https://github.com/erebe/wstunnel/releases/latest/download/wstunnel-x64-linux -o /usr/bin/wstunnel && \
    chmod +x /usr/bin/wstunnel

# پایتون
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages

COPY . .

EXPOSE 8000 2222

CMD ["/bin/sh", "/app/start.sh"]
