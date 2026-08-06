FROM alpine:edge

RUN apk add --no-cache curl bash python3 py3-pip wget

# دانلود GOST از GitHub Releases (نسخه 2.12)
RUN wget -q https://github.com/ginuerzh/gost/releases/download/v2.12.0/gost-linux-amd64-2.12.0.gz -O /tmp/gost.gz && \
    gunzip /tmp/gost.gz && \
    mv /tmp/gost /usr/bin/gost && \
    chmod +x /usr/bin/gost

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages

COPY . .
RUN chmod +x /app/start.sh

EXPOSE 8443 8000

CMD ["/bin/bash", "/app/start.sh"]
