---
{
  "title": "What It Took to Build My First Kubernetes Homelab",
  "articleType": "commentary",
  "category": "Kubernetes",
  "categories": [
    "homelab",
    "kubernetes"
  ],
  "dateTime": "2026-07-28",
  "excerpt": "Three Linux nodes, one unreachable service and the lessons that made my first Kubernetes cluster worth keeping.",
  "introduction": "I built a three-node K3s cluster to practise deployments, debug networking and learn how Kubernetes reacts when a workload stops responding.",
  "image": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1600&q=84",
  "imageAlt": "Server racks representing a Kubernetes homelab",
  "sources": [
    {
      "label": "K3s quick start",
      "url": "https://docs.k3s.io/quick-start"
    },
    {
      "label": "Kubernetes documentation on liveness and readiness probes",
      "url": "https://kubernetes.io/docs/concepts/workloads/pods/probes/"
    }
  ]
}
---

I wanted a cluster I could break, rebuild and understand. Cloud sandboxes were useful, but a local cluster forced me to learn what was underneath the workloads as well as what happened inside Kubernetes.

## Choosing a three-node K3s cluster {#what-i-was-trying-to-build}

The goal was three modest Linux nodes, one control plane and two workers, all connected on the same network. I chose K3s because it kept the resource overhead low while preserving the Kubernetes APIs and workflows I wanted to practise.

## Preparing Linux before installing K3s {#preparing-the-nodes}

I assigned stable addresses, configured SSH keys and made sure hostnames and time synchronisation were correct. Those basic details prevented several confusing failures later, especially when certificates and node identity became involved.

```shell
sudo apt update
sudo apt install -y curl open-iscsi nfs-common
curl -sfL https://get.k3s.io | sh -
```

These commands record part of the original setup. For a new cluster, check the linked K3s quick start for requirements and the steps to join workers.

## When pods ran but the service was unreachable {#the-networking-problem}

Pods scheduled correctly but services were not reachable from another machine. Working through routes, firewall rules and the service network taught me to debug each layer separately instead of changing multiple settings at once.

## Deploying a dashboard and checking its health {#my-first-useful-workload}

I deployed a small internal dashboard with readiness and liveness probes, then exposed it through an ingress. Watching Kubernetes recover an unhealthy workload made reconciliation concrete. Readiness probes determine whether a pod should receive Service traffic. Repeated liveness failures tell the kubelet to restart the container.

- Keep node configuration in automation.
- Test DNS before blaming the application.
- Add resource requests from the start.
- Document how to rebuild every node.

## A cluster I could rebuild {#what-i-learned}

The cluster was not impressive because of its size. It was useful because it gave me a repeatable place to practise deployments, failure recovery and the operational reasoning behind Kubernetes. See how I used monitoring in the lab in my [Prometheus and Grafana notes](../setting-up-prometheus-and-grafana-in-my-homelab/).
