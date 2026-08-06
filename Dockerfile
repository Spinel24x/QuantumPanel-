FROM alpine:edge

RUN apk add --no-cache curl bash python3 py3-pip

# Chisel - دانلود و نصب درست
RUN curl -L -o /tmp/chisel.gz https://github.com/jpillora/chisel/releases/download/v1.10.1/chisel_1.10.1_linux_amd64.gz && \
    gunzip /tmp/chisel.gz && \
    mv /tmp/chisel /usr/bin/chisel && \
    chmod +x /usr/bin/chisel

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages

COPY . .
RUN chmod +x /app/start.sh

EXPOSE 8443 8000

CMD ["/bin/bash", "/app/start.sh"]
