---
{
  "title": "From Docker Containers to a Real Deployment Workflow",
  "articleType": "commentary",
  "category": "Docker",
  "categories": [
    "cicd",
    "homelab"
  ],
  "dateTime": "2026-06-02",
  "readTime": "6 min read",
  "excerpt": "A Docker project grows from a local container into a release workflow with versioned images, a registry and health checks.",
  "introduction": "Running a container was the easy part; building a deployment workflow meant making releases repeatable, observable and recoverable.",
  "image": "https://images.unsplash.com/photo-1587620962725-abab7fe55159?auto=format&fit=crop&w=1600&q=84",
  "imageAlt": "Developer workstation representing a Docker deployment workflow"
}
---

My early Docker projects ended at docker run. That was enough for development, but it did not answer how an image should be versioned, configured, checked or replaced safely.

## What I was trying to improve

I wanted every commit to produce a traceable image and every deployment to use the same documented configuration. The running container needed a health signal, persistent data needed an explicit home and secrets could not live in the image.

## Building smaller, predictable images

A multi-stage Dockerfile separated build tools from the runtime. Pinning dependencies and running as a non-root user made the artifact both smaller and less surprising.

```dockerfile
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
```

## Using the registry as a boundary

The pipeline tagged images with the Git commit and pushed them to a registry. Deployment machines pulled that exact tag, which removed local build differences and made rollback straightforward.

## Health checks changed releases

A running process did not always mean a ready application. Adding a health endpoint allowed the deployment workflow to wait for a real response before considering a release successful.

- Use immutable image tags.
- Keep configuration outside the image.
- Run containers with the least privilege possible.
- Test recovery of persistent volumes.

## What I learned

Containers became operationally useful when I treated the image as one artifact in a larger release system. The workflow around the container mattered as much as the Dockerfile.
