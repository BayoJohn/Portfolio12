---
{
  "title": "What My First CI/CD Pipeline Taught Me About Safer Releases",
  "articleType": "commentary",
  "category": "CI/CD",
  "categories": [
    "cicd"
  ],
  "dateTime": "2026-07-14",
  "excerpt": "A passing build once triggered deployment immediately. Here’s how I added checks and made rollback easier to reason about.",
  "newsroomExcerpt": "Adding health checks and commit-tagged images made releases easier to verify and roll back.",
  "introduction": "I rebuilt my first CI/CD pipeline around explicit tests, commit-tagged images and a health check after deployment.",
  "image": "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?auto=format&fit=crop&w=1600&q=84",
  "imageAlt": "Code editor representing a CI/CD workflow"
}
---

My first pipeline was a collection of commands that happened to run in sequence. Rebuilding it from scratch helped me understand that a good delivery pipeline is really a set of quality gates with clear inputs and outputs.

## Deciding what should block a release {#defining-the-delivery-path}

I mapped the path from pull request to production: lint, test, build, scan, publish and deploy. Writing the stages down first made it easier to decide which failures should block a release.

## Building a traceable image {#making-builds-reproducible}

The image build had to produce the same result on a laptop and in the runner. Pinning base images, keeping dependencies explicit and using a clean build context removed most of the “works on my machine” surprises.

```yaml
- name: Test
  run: npm test
- name: Build image
  run: docker build -t app:${{ github.sha }} .
```

These two steps show the test and image build portions of the workflow. The commit identifier in the image tag helps connect a build to its source.

## What a passing build missed {#what-went-wrong}

At first, every push deployed immediately. A passing build was treated as proof that the application was ready, even though there was no smoke test and rollback required manual commands.

## Checking the deployed application {#adding-safer-releases}

I separated image publication from deployment, used immutable commit tags and added an environment approval. A post-deployment health check now verifies the release before the workflow reports success.

- Fail quickly on formatting and tests.
- Never deploy a mutable `latest` tag.
- Keep credentials scoped to one environment.
- Make rollback a documented pipeline action.

## Plan rollback alongside deployment {#what-i-would-do-differently}

I would design rollback and observability alongside the happy path. I would start by documenting which image to roll back to and how to tell if it restored service. My [Docker deployment notes](../from-docker-containers-to-a-real-deployment-workflow/) explain how I used the registry and health checks.
