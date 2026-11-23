---
{
  "title": "From Docker Run to a Repeatable Deployment",
  "articleType": "commentary",
  "category": "Docker",
  "categories": [
    "cicd",
    "homelab"
  ],
  "dateTime": "2026-06-02",
  "excerpt": "What changed when I added versioned images, a registry and health checks to a Docker project that previously ran only locally.",
  "newsroomExcerpt": "How commit-tagged Docker images, a registry and readiness checks made deployments repeatable.",
  "introduction": "My Docker workflow changed when I had to answer three release questions. Which image is running? Is it ready? How can I roll back?",
  "image": "https://images.unsplash.com/photo-1587620962725-abab7fe55159?auto=format&fit=crop&w=1600&q=84",
  "imageAlt": "Developer workstation representing a Docker deployment workflow",
  "sources": [
    {
      "label": "Docker documentation on multi-stage builds",
      "url": "https://docs.docker.com/build/building/multi-stage/"
    }
  ]
}
---

My early Docker projects ended at `docker run`. That was enough for development, but it did not answer how an image should be versioned, configured, checked or replaced safely.

## Deciding what each release needed {#what-i-was-trying-to-improve}

I wanted every commit to produce a traceable image and every deployment to use the same documented configuration. The running container needed a health signal, persistent data needed an explicit home and secrets could not live in the image.

## Separating build tools from the runtime {#building-smaller-predictable-images}

A multi-stage Dockerfile separated build tools from the runtime. I pinned dependencies for more predictable builds and ran the application as a non-root user. The example shows the build stage. The final runtime stage is omitted.

```dockerfile
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
```

## Shipping the image built by CI {#using-the-registry-as-a-boundary}

The pipeline tagged images with the Git commit and pushed them to a registry. Deployment machines pulled that exact tag, which removed local build differences and made rollback straightforward.

## Checking readiness before calling a release successful {#health-checks-changed-releases}

A running process did not always mean a ready application. Adding a health endpoint allowed the deployment workflow to wait for a real response before considering a release successful.

- Use immutable image tags.
- Keep configuration outside the image.
- Run containers with the least privilege possible.
- Test recovery of persistent volumes.

## The release starts with a traceable image {#what-i-learned}

Containers became operationally useful when I treated the image as one artifact in a larger release system. The workflow around the container mattered as much as the Dockerfile. My [CI/CD pipeline notes](../what-i-learned-building-a-ci-cd-pipeline-from-scratch/) cover how I wired checks into a release.
