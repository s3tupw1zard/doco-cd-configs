# Unmodified upstream source; build dependencies without credentials.
FROM oven/bun:1 AS bun
FROM node:22-bookworm
COPY --from=bun /usr/local/bin/bun /usr/local/bin/bun
ARG SCIRA_COMMIT=e1692f5bdec7ec3f6482a24e0c6cf9b483d810f9
WORKDIR /app
RUN git init && git remote add origin https://github.com/zaidmukaddam/scira.git \
    && git fetch --depth 1 origin "$SCIRA_COMMIT" \
    && git checkout --detach FETCH_HEAD \
    && test "$(git rev-parse HEAD)" = "$SCIRA_COMMIT" \
    && rm -rf .git \
    && bun install --frozen-lockfile \
    && chown -R node:node /app
USER node
ENV NEXT_TELEMETRY_DISABLED=1
EXPOSE 3000
# Next.js validates live environment variables during build. Run build at startup
# so credentials are never passed as image build arguments or copied into layers.
CMD ["sh", "-ec", "bun run build && bun run start --hostname 0.0.0.0 --port 3000"]
