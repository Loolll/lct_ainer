FROM node:lts-alpine

ENV	TZ=Europe/Moscow
RUN	ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN yarn add nuxt
RUN yarn add typescript
RUN yarn add --dev @nuxt/typescript-build @nuxt/types

COPY . /frontend
WORKDIR /frontend

RUN npm i
RUN npm install -g serve

ENV NODE_OPTIONS=--openssl-legacy-provider



