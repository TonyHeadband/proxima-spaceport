FROM node:20.19-bullseye-slim

# Create app directory
WORKDIR /app

# Install dependencies based on package-lock or package.json
COPY package*.json ./
RUN npm install --silent --no-audit --no-fund

# Copy source
COPY . .

# Build args
ARG DEV="false"
ENV DEV=${DEV}

# Expose Vite dev server default port
EXPOSE 5173

# In DEV mode run the Vite dev server, otherwise build and run preview
CMD ["sh", "-c", "if [ \"$DEV\" = \"true\" ]; then npm run dev -- --host 0.0.0.0; else npm run build && npm run preview -- --host 0.0.0.0 --port 5173; fi"]
