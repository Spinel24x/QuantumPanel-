FROM alpine:edge

RUN apk add --no-cache curl bash python3 py3-pip

# دانلود GOST
RUN curl -L https://github.com/ginuerzh/gost/releases/latest/download/gost-linux-amd64-3.0.0.gz -o /tmp/gost.gz && \
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
