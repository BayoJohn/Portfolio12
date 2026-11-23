---
{
  "title": "What I Learned Building a CI/CD Pipeline From Scratch",
  "articleType": "commentary",
  "category": "CI/CD",
  "categories": [
    "cicd"
  ],
  "dateTime": "2026-07-14",
  "readTime": "7 min read",
  "excerpt": "Lessons from connecting source control, testing, image builds and deployment into one repeatable workflow.",
  "introduction": "Connecting source control, tests, container builds and deployment revealed where automation creates confidence—and where it can hide risk.",
  "image": "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?auto=format&fit=crop&w=1600&q=84",
  "imageAlt": "Code editor representing a CI/CD workflow"
}
---

My first pipeline was a collection of commands that happened to run in sequence. Rebuilding it from scratch helped me understand that a good delivery pipeline is really a set of quality gates with clear inputs and outputs.

## Defining the delivery path

I mapped the path from pull request to production: lint, test, build, scan, publish and deploy. Writing the stages down first made it easier to decide which failures should block a release.

## Making builds reproducible

The image build had to produce the same result on a laptop and in the runner. Pinning base images, keeping dependencies explicit and using a clean build context removed most of the “works on my machine” surprises.

```yaml
- name: Test
  run: npm test
- name: Build image
  run: docker build -t app:${{ github.sha }} .
```

## What went wrong

At first, every push deployed immediately. A passing build was treated as proof that the application was ready, even though there was no smoke test and rollback required manual commands.

## Adding safer releases

I separated image publication from deployment, used immutable commit tags and added an environment approval. A post-deployment health check now verifies the release before the workflow reports success.

- Fail quickly on formatting and tests.
- Never deploy a mutable latest tag.
- Keep credentials scoped to one environment.
- Make rollback a documented pipeline action.

## What I would do differently

I would design rollback and observability alongside the happy path. Automation is valuable only when it makes both successful releases and failed releases easier to understand.
