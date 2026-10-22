FROM node:24-alpine AS build
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
ENV VITE_API_URL=/api
RUN npm run build

FROM caddy:2-alpine
COPY --from=build /frontend/dist /srv
COPY deploy/Caddyfile /etc/caddy/Caddyfile
EXPOSE 8080
