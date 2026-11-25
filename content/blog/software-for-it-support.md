---
{
  "title": "An IT support toolkit built around evidence",
  "articleType": "tutorial",
  "softwareFormat": "guide",
  "dateTime": "2026-11-25",
  "author": "StackedByBayo",
  "category": "IT Utilities",
  "categories": [
    "software",
    "windows",
    "linux",
    "macos",
    "it utilities",
    "developer tools"
  ],
  "excerpt": "Choose tools for the clues they preserve. Here’s where a text editor, a packet viewer and familiar system tools fit.",
  "sources": [
    {
      "label": "Microsoft’s Visual Studio Code licensing FAQ",
      "url": "https://code.visualstudio.com/docs/supporting/faq"
    },
    {
      "label": "Wireshark’s documentation",
      "url": "https://www.wireshark.org/docs/"
    },
    {
      "label": "Wireshark download and platform guide",
      "url": "https://www.wireshark.org/download.html"
    }
  ]
}
---

A useful support toolkit starts with tools you know well enough to use under pressure. Start with a way to record the problem, a way to compare text, and a way to look at the system without making a change. Add specialised utilities when the evidence gives you a reason to use them.

## Save the smallest useful record

Capture the exact error, time and time zone, the affected version, and what changed before the issue appeared. If someone else will read your notes, include one reproduction step and one thing you have ruled out. Strip credentials, personal data and internal identifiers before sharing logs outside their approved location.

An editor such as Visual Studio Code can read plain text, search across files and compare changes. Its Microsoft distribution has its own licence, while the upstream Code - OSS repository is open source. On managed devices, use the approved distribution and keep extensions to a minimum. A plain editor is enough for many support tasks.

## Reach for a capture when the question calls for it

Wireshark shows network traffic that the capture point can see. It can help answer questions about timing and which endpoints exchanged traffic. Encryption can make application contents unavailable, and a packet capture cannot directly tell you why a remote application made a decision. Only capture with authorisation, limit the scope to the troubleshooting task, and store captures in approved locations because they can contain sensitive information.

## Use simpler tools first

Begin with what the operating system already shows you. Is the device online? Did its clock drift? Does the issue affect one account or every account? This work narrows the next diagnostic step. Finish by recording the change that fixed the problem and the test you used to confirm it.
