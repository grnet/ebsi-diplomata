ARG OPTION_UI_CODEDIR=/srv/ui

# Stage 1: Build UI
FROM alpine:3.11.8 AS builder-ui
ARG GIT_COMMIT=none
LABEL stage=ui-intermediate-$GIT_COMMIT

ARG OPTION_UI_CODEDIR
WORKDIR ${OPTION_UI_CODEDIR}
ADD package.json .
ADD yarn.lock .
# Install yarn and dependencies
RUN apk add yarn
RUN yarn install --network-timeout 1000000
# Add UI code to image
ADD . ${OPTION_UI_CODEDIR}
# Build UI
RUN yarn run export

# Stage 2: Build final nginx image
FROM nginx:1.17.5
ARG OPTION_UI_CODEDIR
ARG GIT_COMMIT=none
LABEL git_commit=$GIT_COMMIT

COPY --from=builder-ui ${OPTION_UI_CODEDIR}/out /usr/share/nginx/html

