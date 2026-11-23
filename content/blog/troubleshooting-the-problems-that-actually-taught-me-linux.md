---
{
  "title": "The Linux Failures That Taught Me to Troubleshoot",
  "articleType": "commentary",
  "category": "Linux",
  "categories": [
    "linux"
  ],
  "dateTime": "2026-06-16",
  "excerpt": "A restart loop, an unreachable service and a disk with free space all had clues. Here’s where I found them.",
  "newsroomExcerpt": "Four Linux failures show what the journal, file permissions, network checks and inode counts can tell you.",
  "introduction": "Four Linux failures taught me to check the journal, process identity, network path and filesystem before changing settings.",
  "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1600&q=84",
  "imageAlt": "Computer hardware representing Linux systems troubleshooting"
}
---

Reading Linux documentation gave me vocabulary. Troubleshooting real failures taught me how the pieces connect and how to gather evidence before making a change.

## A restart loop and a clue in the journal {#the-service-that-would-not-start}

A systemd unit kept restarting with a generic failure. The useful clue was not in the application output but in the journal, where a working-directory permission error showed exactly which user was being denied.

```shell
systemctl status my-service
journalctl -u my-service --since "10 minutes ago"
namei -l /srv/my-service/config.yml
```

## Checking every directory in the path {#permissions-beyond-chmod}

Changing a file to mode `777` would have hidden the underlying mistake. Checking ownership, parent-directory traversal and the service account led to a narrow fix that preserved the intended access model.

## Following the request from DNS to the service {#following-a-network-request}

When a host could resolve a name but not reach the service, I learned to test DNS, routing, listening sockets and firewall rules independently. That sequence made network debugging far less mysterious.

```shell
dig service.internal
ip route
ss -lntp
curl -v http://service.internal:8080/health
```

`my-service` and `service.internal` stand for the unit and host being investigated. Use the corresponding names for your own system.

## When a disk has free space but no free inodes {#disk-space-that-looked-available}

One node reported free disk space but could not create files. The filesystem had exhausted its inodes because a failed job had created millions of tiny files. On filesystems that report inode totals, `df -i` shows inode usage, while `df -h` reports space in readable units.

- Read logs before restarting.
- Check the identity a process actually uses.
- Test one network layer at a time.
- Measure both disk blocks and inodes.

## Test one explanation at a time {#the-habit-that-mattered-most}

The biggest improvement was forming a hypothesis, running a command that could disprove it and recording the result. That habit gave me a repeatable way to investigate each failure. If commands and paths still feel unfamiliar, start with the [Linux terminal guide](../../academy/linux-terminal-essentials/).
