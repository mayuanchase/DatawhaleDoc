# 第一阶段：基于 Node.js 镜像构建前端项目
FROM node:18-alpine3.18 AS build-stage
WORKDIR /app
COPY package*.json ./
RUN dock
COPY . .
RUN npm run build


# 第二阶段：基于 Nginx 镜像构建最终镜像
FROM nginx:latest
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]