#!/bin/bash

# Ensure the logs directory exists
mkdir -p /usr/src/app/logs

# Start Nginx
echo "Starting Nginx..."
nginx -g "daemon off;" &
NGINX_PID=$!

# Wait for Nginx to start
echo "Waiting for Nginx to start..."
sleep 5

# Obtain SSL certificates via Certbot
echo "Obtaining SSL certificates..."

# Request or renew SSL certificates
if [ ! -f "/etc/letsencrypt/live/travelculturehub.com/fullchain.pem" ]; then
  echo "Obtaining SSL certificate for travelculturehub.com, www.travelculturehub.com, flower.travelculturehub.com, and docs.travelculturehub.com..."
  certbot --nginx \
    -d travelculturehub.com \
    -d www.travelculturehub.com \
    --email ibhayk@gmail.com \
    --agree-tos \
    --no-eff-email \
    --non-interactive
else
  echo "Certificate for travelculturehub.com already exists."
fi

# Check if both succeeded
if [ $? -eq 0 ]; then
  echo "Certificates successfully obtained."
else
  echo "Failed to obtain one or more certificates."
  exit 1
fi

# Reload Nginx to apply the new certificates
echo "Reloading Nginx..."
nginx -s reload

if [ $? -eq 0 ]; then
  echo "Nginx reloaded successfully."
else
  echo "Failed to reload Nginx."
  exit 1
fi

# Set up automatic renewal cron job
echo "Setting up automatic SSL certificate renewal..."
cat <<EOL > /etc/cron.d/certbot-renew
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

0 0,12 * * * root certbot renew --quiet --deploy-hook "nginx -s reload" >> /usr/src/app/logs/certbot-renew.log 2>&1
EOL

chmod 0644 /etc/cron.d/certbot-renew
crontab /etc/cron.d/certbot-renew

# Start cron in the background
echo "Starting cron..."
cron -f &
CRON_PID=$!

# Wait for Nginx and Cron
wait $NGINX_PID
wait $CRON_PID

# Keep container alive
tail -f /dev/null
