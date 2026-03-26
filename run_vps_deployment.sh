#!/bin/bash

# Run deployment on VPS from local machine
# This script will SSH to VPS and run the deployment

set -e

VPS_IP="147.93.156.165"
VPS_USER="root"

echo "=========================================="
echo "Deploying License System to VPS"
echo "=========================================="
echo ""
echo "VPS: $VPS_USER@$VPS_IP"
echo ""

# Upload deployment script to VPS
echo "Step 1: Uploading deployment script to VPS..."
scp deploy_license_to_vps.sh $VPS_USER@$VPS_IP:/root/cryptomentor-bot/

# SSH to VPS and run deployment
echo ""
echo "Step 2: Running deployment on VPS..."
ssh $VPS_USER@$VPS_IP << 'ENDSSH'
cd /root/cryptomentor-bot
chmod +x deploy_license_to_vps.sh
./deploy_license_to_vps.sh
ENDSSH

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "You can now test the bot in Telegram:"
echo "  1. Open Telegram and find your bot"
echo "  2. Send /start command"
echo "  3. Bot should respond with license check"
echo ""
