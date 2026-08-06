FROM alpine:edge

RUN apk add --no-cache curl bash python3 py3-pip wget unzip

# دانلود SlipStream Server
RUN wget -q https://github.com/abumq/slipstream/releases/latest/download/slipstream-linux-amd64 -O /usr/bin/slipstream && \
    chmod +x /usr/bin/slipstream

# پایتون
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages

COPY . .
RUN chmod +x /app/start.sh

EXPOSE 8443 9000

CMD ["/bin/bash", "/app/start.sh"]
