---
{
  "title": "Setting Up Prometheus and Grafana in My Homelab",
  "articleType": "commentary",
  "category": "Monitoring",
  "categories": [
    "monitoring",
    "homelab"
  ],
  "dateTime": "2026-06-30",
  "readTime": "6 min read",
  "excerpt": "How host metrics, a few focused dashboards and an alerting lesson helped me troubleshoot my homelab.",
  "introduction": "A practical monitoring stack changed homelab troubleshooting from guesswork into a process guided by useful signals.",
  "image": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=1600&q=84",
  "imageAlt": "Analytics dashboard representing monitoring and observability"
}
---

Before I added monitoring, I usually discovered a problem by opening an application and finding it unavailable. Prometheus and Grafana gave the lab a memory: I could see what changed before the failure.

## Starting with a small scope

I began with node exporter on each machine and kube-state-metrics in the cluster. CPU, memory, disk space and workload state covered the questions I was actually asking without collecting everything available.

## Building dashboards around questions

Instead of filling a dashboard with attractive graphs, I organised panels around operational questions: Is the node under pressure? Are pods restarting? Is storage latency rising? Is the service responding?

```promql
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
kube_pod_container_status_restarts_total
```

## The alerting lesson

My first alerts were too sensitive and quickly became noise. I added duration windows, removed alerts with no clear action and wrote a short annotation explaining what to check first.

## A failure I could finally explain

A recurring application slowdown lined up with a spike in disk wait time during backups. The dashboard connected an application symptom to a host-level cause in minutes.

- Monitor symptoms as well as resources.
- Every alert needs an owner and an action.
- Keep dashboard variables consistent.
- Back up Grafana and Prometheus configuration.

## What I learned

Observability did not prevent every incident, but it made the system explain itself. That feedback turned each homelab failure into a much better learning opportunity.
