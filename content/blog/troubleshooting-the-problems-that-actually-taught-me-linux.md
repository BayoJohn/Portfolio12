---
{
  "title": "Troubleshooting the Problems That Actually Taught Me Linux",
  "articleType": "commentary",
  "category": "Linux",
  "categories": [
    "linux"
  ],
  "dateTime": "2026-06-16",
  "readTime": "7 min read",
  "excerpt": "The permissions, networking and service failures that turned Linux concepts into practical operational knowledge.",
  "introduction": "The Linux lessons that stayed with me came from broken services, confusing permissions and networks that did not behave as expected.",
  "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1600&q=84",
  "imageAlt": "Computer hardware representing Linux systems troubleshooting"
}
---

Reading Linux documentation gave me vocabulary. Troubleshooting real failures taught me how the pieces connect and how to gather evidence before making a change.

## The service that would not start

A systemd unit kept restarting with a generic failure. The useful clue was not in the application output but in the journal, where a working-directory permission error showed exactly which user was being denied.

```shell
systemctl status my-service
journalctl -u my-service --since "10 minutes ago"
namei -l /srv/my-service/config.yml
```

## Permissions beyond chmod

Changing a file to 777 would have hidden the underlying mistake. Checking ownership, parent-directory traversal and the service account led to a narrow fix that preserved the intended access model.

## Following a network request

When a host could resolve a name but not reach the service, I learned to test DNS, routing, listening sockets and firewall rules independently. That sequence made network debugging far less mysterious.

```shell
dig service.internal
ip route
ss -lntp
curl -v http://service.internal:8080/health
```

## Disk space that looked available

One node reported free disk space but could not create files. The filesystem had exhausted its inodes because a failed job had created millions of tiny files.

- Read logs before restarting.
- Check the identity a process actually uses.
- Test one network layer at a time.
- Measure both disk blocks and inodes.

## The habit that mattered most

The biggest improvement was forming a hypothesis, running a command that could disprove it and recording the result. Linux became easier when troubleshooting became an investigation instead of a sequence of guesses.
