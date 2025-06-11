FROM nginx:latest

# Reinstall Nginx to ensure mime.types is available
RUN apt-get update -y && \
    apt-get install --reinstall nginx -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Certbot and Nginx plugin for Certbot
RUN apt-get update -y && \
    apt-get install -y certbot python3-certbot-nginx cron && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create directories for SSL certificates and the challenge
RUN mkdir -p /etc/nginx/ssl /var/www/certbot

# Copy Nginx configuration and your HTML directory
COPY nginx.conf /etc/nginx/nginx.conf
COPY html/ /var/www/html/

# Copy mime.types if needed (or use the default Nginx one)
COPY mime.types /etc/nginx/mime.types

# Expose HTTP and HTTPS ports
EXPOSE 80 443

# Copy the entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
RUN apk add certbot certbot-nginx

# Use the custom entrypoint script to manage Nginx and Certbot
ENTRYPOINT ["/entrypoint.sh"]

# Ensure that Nginx runs in the foreground (entrypoint script will handle reloading)
CMD ["nginx", "-g", "daemon off;"]
