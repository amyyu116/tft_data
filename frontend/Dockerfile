FROM node:20
WORKDIR /app
COPY package*.json ./
RUN npm install
RUN chmod -R +x node_modules/.bin
COPY . .
EXPOSE 3000
CMD ["npm", "start"]