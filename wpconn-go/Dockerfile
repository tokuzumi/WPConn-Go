# syntax=docker/dockerfile:1

# Base stage
FROM golang:alpine AS base
WORKDIR /app
RUN apk add --no-cache git

# Development stage (with Air for hot-reload)
FROM base AS dev
RUN go install github.com/air-verse/air@latest
COPY go.mod go.sum ./
RUN go mod download
CMD ["air", "-c", ".air.toml"]

# Builder stage for production
FROM base AS builder
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /main ./cmd/main.go

# Production stage
FROM alpine:latest AS prod
WORKDIR /root/
COPY --from=builder /main .
COPY .env .
CMD ["./main"]
