FROM alpine:edge

RUN apk add --no-cache curl bash python3 py3-pip wget

# ============================================
# استفاده از udp2raw + tinyfecvpn
# یا مستقیم socat برای TCP Tunnel
# ============================================

# socat برای TCP forwarding
RUN apk add --no-cache socat

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages

COPY . .
RUN chmod +x /app/start.sh

EXPOSE 8443 9000

CMD ["/bin/bash", "/app/start.sh"]
