---
{
  "title": "Building My First AWS Automation Project",
  "category": "Cloud",
  "categories": [
    "cloud"
  ],
  "dateTime": "2026-05-19",
  "readTime": "7 min read",
  "excerpt": "Using Terraform and managed AWS services to make a small cloud application reproducible from the beginning.",
  "introduction": "My first AWS automation project turned a manually assembled cloud experiment into infrastructure I could review, recreate and safely remove.",
  "image": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1600&q=84",
  "imageAlt": "Cloud technology representing an AWS automation project"
}
---

I had created AWS resources through the console before, but I wanted to understand how to describe an entire small application as code and reproduce it in a clean account.

## Choosing a deliberately small project

The application stored static files in S3, delivered them through CloudFront and used a Lambda function for a small API task. A limited scope let me focus on identity, state and repeatability.

## Describing infrastructure with Terraform

I separated reusable resources into a module and kept environment values in a small root configuration. Remote state and locking were added before anyone else needed to run the project.

```hcl
module "web" {
  source      = "./modules/web"
  environment = "dev"
  domain_name = var.domain_name
}
```

## The IAM mistake

My first role was far too broad because it was convenient. Replacing it with actions tied to specific resources forced me to understand what the function actually needed and reduced the impact of a compromised credential.

## Automating validation and deployment

The pipeline now runs formatting and validation, creates a plan for review and applies only after approval. The plan artifact makes infrastructure changes visible before they reach AWS.

- Tag resources for cost and ownership.
- Use least-privilege roles from the start.
- Keep state remote and protected.
- Include destroy and recovery procedures in the project notes.

## What I would do differently

I would add budget alerts and policy checks on day one. Infrastructure automation makes creation easy, so guardrails for cost and security need to be equally easy to use.
