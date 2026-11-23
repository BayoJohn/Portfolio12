---
{
  "title": "Building My First Kubernetes Homelab",
  "articleType": "commentary",
  "category": "Kubernetes",
  "categories": [
    "homelab",
    "kubernetes"
  ],
  "dateTime": "2026-07-28",
  "readTime": "6 min read",
  "excerpt": "How I set up my first Kubernetes cluster on Linux, worked through a networking problem and deployed my first useful workload.",
  "introduction": "How a small group of Linux machines became a practical Kubernetes environment for learning real cluster operations.",
  "image": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1600&q=84",
  "imageAlt": "Server racks representing a Kubernetes homelab"
}
---

I wanted a cluster I could break, rebuild and understand. Cloud sandboxes were useful, but a local cluster forced me to learn what was underneath the workloads as well as what happened inside Kubernetes.

## What I was trying to build

The goal was three modest Linux nodes, one control plane and two workers, all connected on the same network. I chose k3s because it kept the resource overhead low while preserving the Kubernetes APIs and workflows I wanted to practise.

## Preparing the nodes

I assigned stable addresses, configured SSH keys and made sure hostnames and time synchronisation were correct. Those basic details prevented several confusing failures later, especially when certificates and node identity became involved.

```shell
sudo apt update
sudo apt install -y curl open-iscsi nfs-common
curl -sfL https://get.k3s.io | sh -
```

## The networking problem

Pods scheduled correctly but services were not reachable from another machine. Working through routes, firewall rules and the service network taught me to debug each layer separately instead of changing multiple settings at once.

## My first useful workload

I deployed a small internal dashboard with readiness and liveness probes, then exposed it through an ingress. Watching Kubernetes replace an unhealthy pod made reconciliation feel concrete instead of theoretical.

- Keep node configuration in automation.
- Test DNS before blaming the application.
- Add resource requests from the start.
- Document how to rebuild every node.

## What I learned

The cluster was not impressive because of its size. It was useful because it gave me a repeatable place to practise deployments, failure recovery and the operational reasoning behind Kubernetes.
