FROM nginx:stable-alpine
COPY . /usr/share/nginx/html
# Remove default config if you want to change CORS or add proxy
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
