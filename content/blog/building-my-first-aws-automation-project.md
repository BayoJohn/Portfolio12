---
{
  "title": "Automating My First AWS Project With Terraform",
  "articleType": "commentary",
  "category": "Cloud",
  "categories": [
    "cloud"
  ],
  "dateTime": "2026-05-19",
  "excerpt": "A small AWS application gave me a reason to learn how Terraform plans, state and least-privilege permissions fit together.",
  "newsroomExcerpt": "A small AWS application became a practical lesson in Terraform plans, remote state and least-privilege permissions.",
  "introduction": "I used Terraform to turn a small AWS application into infrastructure I could review, recreate and remove.",
  "image": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1600&q=84",
  "imageAlt": "Cloud technology representing an AWS automation project"
}
---

I had created AWS resources through the console before, but I wanted to understand how to describe an entire small application as code and reproduce it in a clean account.

## A small application with three AWS services {#choosing-a-deliberately-small-project}

The application stored static files in S3, delivered them through CloudFront and used a Lambda function for a small API task. A limited scope let me focus on identity, state and repeatability.

## Splitting the Terraform module from environment settings {#describing-infrastructure-with-terraform}

I separated reusable resources into a module and kept environment values in a small root configuration. Remote state and locking were added before anyone else needed to run the project.

```hcl
module "web" {
  source      = "./modules/web"
  environment = "dev"
  domain_name = var.domain_name
}
```

This example depends on the project’s local `./modules/web` directory and its inputs. It shows what the root configuration passes to the module.

## Narrowing the Lambda role {#the-iam-mistake}

My first role was far too broad because it was convenient. Replacing it with actions tied to specific resources forced me to understand what the function actually needed and reduced the impact of a compromised credential.

## Reviewing a plan before applying it {#automating-validation-and-deployment}

The pipeline now runs formatting and validation, creates a plan for review and applies only after approval. The plan artifact makes infrastructure changes visible before they reach AWS.

- Tag resources for cost and ownership.
- Use least-privilege roles from the start.
- Keep state remote and protected.
- Include destroy and recovery procedures in the project notes.

## What I would add from day one {#what-i-would-do-differently}

I would add budget alerts and policy checks on day one. Infrastructure automation makes creation easy, so guardrails for cost and security need to be equally easy to use. I took a similar approach to review and recovery in my [CI/CD pipeline](../what-i-learned-building-a-ci-cd-pipeline-from-scratch/).
