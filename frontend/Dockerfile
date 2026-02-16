# Use official Node.js runtime as base image (non-alpine to avoid SWC issues)
FROM node:20 AS deps
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package*.json ./
RUN npm ci --only=production

# Production build stage
FROM node:20 AS builder
WORKDIR /app

# Install all dependencies for building
COPY package*.json ./
RUN npm ci

# Copy application code
COPY . .

# Build the application
RUN npm run build

# Production image stage
FROM node:20-slim AS runner
WORKDIR /app

# Install only production dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy built application from builder stage
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules

# Expose port
EXPOSE 3000

# Start the application
ENV NODE_ENV=production
CMD ["npm", "start"]