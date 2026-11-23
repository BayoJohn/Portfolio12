---
{
  "title": "What Prometheus and Grafana Showed Me About My Homelab",
  "articleType": "commentary",
  "category": "Monitoring",
  "categories": [
    "monitoring",
    "homelab"
  ],
  "dateTime": "2026-06-30",
  "excerpt": "Two metrics, fewer alerts and a storage slowdown that became easier to investigate once I could see what the hosts were doing.",
  "introduction": "I used Prometheus and Grafana to investigate what changed before a service slowed down and to trim alerts that had no clear response.",
  "image": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=1600&q=84",
  "imageAlt": "Analytics dashboard representing monitoring and observability",
  "sources": [
    {
      "label": "Prometheus query functions",
      "url": "https://prometheus.io/docs/prometheus/latest/querying/functions/"
    }
  ]
}
---

Before I added monitoring, I usually discovered a problem by opening an application and finding it unavailable. Prometheus and Grafana gave the lab a memory: I could see what changed before the failure.

## Starting with hosts and workload state {#starting-with-a-small-scope}

I began with Node Exporter on each machine and kube-state-metrics in the cluster. CPU, memory, disk space and workload state covered the questions I was actually asking without collecting everything available.

## Using metrics to narrow a problem {#building-dashboards-around-questions}

Instead of filling a dashboard with attractive graphs, I organised panels around operational questions: Is the node under pressure? Are pods restarting? Is storage latency rising? Is the service responding?

```promql
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
kube_pod_container_status_restarts_total
```

The first query estimates non-idle CPU time per instance over five minutes. The second is a cumulative restart counter. To see whether restarts happened recently, look at how the counter changed over a time window.

## Alerts that tell you where to look {#the-alerting-lesson}

My first alerts were too sensitive and quickly became noise. I added duration windows, removed alerts with no clear action and wrote a short annotation explaining what to check first.

## Connecting a slowdown to backup activity {#a-failure-i-could-finally-explain}

A recurring application slowdown lined up with a spike in disk wait time during backups. Seeing those signals together gave me a place to investigate at the host level.

- Monitor symptoms as well as resources.
- Every alert needs an owner and an action.
- Keep dashboard variables consistent.
- Back up Grafana and Prometheus configuration.

## Keep the signals you can act on {#what-i-learned}

Observability did not prevent every incident, but it made the system explain itself. The dashboards helped me narrow down where to look and gave me a way to check whether a change helped. For the environment behind them, see [how I put together the cluster](../building-my-first-kubernetes-homelab/).
