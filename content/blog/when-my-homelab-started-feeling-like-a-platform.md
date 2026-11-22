---
{
  "featured": true,
  "title": "When My Homelab Started Feeling Like a Platform",
  "category": "Homelab",
  "categories": [
    "homelab",
    "kubernetes"
  ],
  "dateTime": "2026-08-10",
  "readTime": "8 min read",
  "excerpt": "A hands-on journey through Kubernetes, monitoring, automation and self-hosted infrastructure as my homelab evolved into something that started feeling like a real platform.",
  "introduction": "A hands-on journey through Kubernetes, monitoring, automation and self-hosted infrastructure.",
  "image": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=1600&q=84",
  "imageAlt": "Computer equipment representing a self-hosted homelab"
}
---

My homelab began as a place to run containers and learn Linux. It became much more useful when I stopped treating each service as an isolated experiment and started treating the whole environment as a platform.

## From individual services to a system

The first version was simple: a few Docker Compose files, manually configured ports and notes scattered across different folders. It worked, but rebuilding anything required remembering decisions that were never captured in code.

I started standardising configuration, keeping infrastructure changes in Git and defining a repeatable path from a commit to a running workload. That shift made the lab easier to recover and far more useful for learning operational habits.

> Reliability started improving when rebuilding the environment became a normal workflow instead of an emergency procedure.

## Adding Kubernetes and GitOps

Kubernetes gave me a consistent way to describe applications, health checks, storage and networking. GitOps then made Git the source of truth for what the cluster should be running.

```terminal
kubectl get pods -A
kubectl get nodes -o wide
kubectl describe deployment portfolio -n production
```

The workflow became deliberately boring:

1. Change a manifest or Helm value in Git.
2. Let the delivery workflow validate the change.
3. Allow the GitOps controller to reconcile the cluster.
4. Confirm health through metrics, logs and workload status.

## Observability changed how I debugged

Prometheus and Grafana did more than add dashboards. They helped me move from guessing about failures to asking specific questions about CPU pressure, memory, latency and availability.

```shell
docker compose up -d
terraform apply

git add .
git commit -m "Update monitoring stack"
git push origin main
```

### What I would improve next

- Automated backups with regular restore tests.
- More deliberate alerting and service-level objectives.
- Network policies and stronger secrets management.
- Better runbooks for common failure scenarios.

## The useful lesson

The hardware was never the most important part. The real value came from building repeatable workflows, observing the results and recovering from mistakes. That is when the homelab stopped feeling like a collection of machines and started feeling like a platform.
