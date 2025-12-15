# FROM node:20-alpine AS build
FROM gitlab.control.lth.se:5050/regler/frtn90/2025/agroup01/node:20-alpine
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install

COPY . .
RUN npm run build

# FROM nginx:alpine
FROM gitlab.control.lth.se:5050/regler/frtn90/2025/agroup01/nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
