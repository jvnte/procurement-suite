# Build stage
FROM node:20-alpine as build

WORKDIR /app

# Accept build arguments
ARG VITE_AGENT_API_URL
ARG VITE_INTAKE_API_URL

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source files
COPY . .

# Set environment variables for build
ENV VITE_AGENT_API_URL=$VITE_AGENT_API_URL
ENV VITE_INTAKE_API_URL=$VITE_INTAKE_API_URL

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration (if needed for SPA routing)
RUN echo 'server { \
    listen 80; \
    server_name localhost; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
