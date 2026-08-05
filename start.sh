#!/bin/sh

echo "🕳️ Starting Quantum Panel..."

mkdir -p /app/data

# UUID برای SSH
if [ ! -f /app/data/uuid.txt ]; then
    python3 -c "import uuid; print(str(uuid.uuid4()))" > /app/data/uuid.txt
fi

# استارت SSH
/usr/sbin/sshd -D -e &
echo "✅ SSH started on port 2222"

# استارت پنل
cd /app
exec python3 -m uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}
