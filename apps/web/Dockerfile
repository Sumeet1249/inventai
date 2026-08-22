FROM node:18-alpine
WORKDIR /app
COPY apps/web/package*.json ./
RUN npm install
COPY apps/web/ .
RUN npm run build
EXPOSE 3001
CMD ["npm", "start"]
