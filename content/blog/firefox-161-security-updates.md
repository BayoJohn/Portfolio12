---
{
  "title": "Firefox 161 security fixes reach the desktop release channel",
  "author": "StackedByBayo",
  "dateTime": "2026-11-25",
  "articleType": "security-update",
  "category": "Browser Advisories",
  "categories": [
    "cybersecurity",
    "advisories"
  ],
  "securityDesk": [
    "advisories"
  ],
  "excerpt": "Mozilla’s November 24 advisory lists fixes for Firefox 161. Readers should check which update channel supplies their browser.",
  "sources": [
    {
      "label": "Mozilla security advisory for Firefox 161",
      "url": "https://www.mozilla.org/en-US/security/advisories/mfsa2026-131/",
      "date": "2026-11-24"
    },
    {
      "label": "Firefox 161 desktop release notes",
      "url": "https://www.firefox.com/en-US/firefox/161.0/releasenotes/",
      "date": "2026-11-24"
    }
  ],
  "securityEventDate": "2026-11-24",
  "security": {
    "affectedProducts": "Desktop Firefox Release channel.",
    "recommendedActions": [
      "Update through the channel that manages your browser.",
      "Restart if prompted and verify the installed version."
    ]
  }
}
---

Mozilla published its Firefox 161 security advisory on November 24, alongside the release-channel update. The advisory gives users of the desktop browser a release to check for. It also helps administrators distinguish the routine new features from the fixes that matter to their update plans.

## Check the channel before checking the version

A desktop copy installed directly from Mozilla can use a different update route from a Linux distribution package or a browser managed by an employer. Extended Support Release is also a separate branch. Check the version and channel you actually run, then use the approved update mechanism for that installation. If the browser asks you to restart to finish installing an update, do that before assuming you are on the new build.

## What the advisory can establish

Mozilla lists individual fixes and their impact. That information explains why the release matters, while an advisory alone does not establish that a particular computer was compromised. For a managed fleet, compare device inventory with the fixed release on each supported branch and verify installations after the restart. Report browsers that stay on the old version so they can be checked separately.

For the user-facing changes in the same release, see [our Software coverage](../firefox-161-tab-groups-update/).
