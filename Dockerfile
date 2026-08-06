FROM alpine:edge

# ============================================
# نصب پیش‌نیازها
# ============================================
RUN apk add --no-cache \
    curl \
    unzip \
    nginx \
    bash \
    openssl \
    python3 \
    py3-pip

# ============================================
# نصب Xray
# ============================================
RUN mkdir -p /opt/xray && \
    curl -L https://github.com/XTLS/Xray-core/releases/latest/download/Xray-linux-64.zip -o /tmp/xray.zip && \
    unzip /tmp/xray.zip -d /opt/xray && \
    chmod +x /opt/xray/xray && \
    rm /tmp/xray.zip

# ============================================
# ساخت گواهی SSL خودامضا
# ============================================
RUN mkdir -p /etc/nginx/ssl && \
    openssl req -x509 -nodes -days 3650 -newkey rsa:4096 \
    -keyout /etc/nginx/ssl/key.pem \
    -out /etc/nginx/ssl/cert.pem \
    -subj "/C=US/ST=Quantum/L=Space/O=Quantum/CN=localhost"

# ============================================
# پایتون و پنل
# ============================================
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages

COPY . .
RUN chmod +x /app/start.sh

# پورت‌ها
EXPOSE 8443 8000

CMD ["/bin/bash", "/app/start.sh"]
