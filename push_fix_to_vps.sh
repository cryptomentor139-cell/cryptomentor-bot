#!/bin/bash
# Script untuk push fix config.py ke VPS dan restart bot

VPS_IP="147.93.156.165"
VPS_USER="root"
VPS_PATH="/root/cryptomentor-bot/whitelabel-1"

echo "=== Pushing Fix to VPS ==="
echo ""

# Step 1: Copy fixed config.py to VPS
echo "Step 1: Copying fixed config.py to VPS..."
scp "Whitelabel #1/config.py" ${VPS_USER}@${VPS_IP}:${VPS_PATH}/config.py

if [ $? -eq 0 ]; then
    echo "✅ File copied successfully"
else
    echo "❌ Failed to copy file"
    exit 1
fi

echo ""
echo "Step 2: Restarting whitelabel1 service..."

# Step 2: SSH to VPS and restart service
ssh ${VPS_USER}@${VPS_IP} << 'ENDSSH'
cd /root/cryptomentor-bot/whitelabel-1
sudo systemctl restart whitelabel1
sleep 3
sudo systemctl status whitelabel1
echo ""
echo "=== Recent Logs ==="
sudo journalctl -u whitelabel1 -n 20 --no-pager
ENDSSH

echo ""
echo "=== Done! ==="
echo ""
echo "To view live logs, run:"
echo "ssh ${VPS_USER}@${VPS_IP} 'sudo journalctl -u whitelabel1 -f'"
