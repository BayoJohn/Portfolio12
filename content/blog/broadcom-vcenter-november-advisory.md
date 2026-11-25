---
{
  "title": "Broadcom’s vCenter advisory puts version checks first",
  "author": "StackedByBayo",
  "dateTime": "2026-11-25",
  "articleType": "security-update",
  "category": "Vendor Advisories",
  "categories": [
    "cybersecurity",
    "advisories"
  ],
  "securityDesk": [
    "advisories"
  ],
  "excerpt": "The November 19 VMware advisory includes a critical vCenter fix. Match the deployed branch to Broadcom’s response matrix before scheduling the update.",
  "sources": [
    {
      "label": "Broadcom VMSA-2026-0009.1",
      "url": "https://support.broadcom.com/web/ecx/support-content-notification/-/external/content/SecurityAdvisories/VMSA-2026-0009--VMware-vCenter--Tools--and-SDDC-Manager-updates-address-multiple-vulnerabilities--CVE-2026-123890--CVE-2026-123891--CVE-2026-123892--CVE-2026-123893--CVE-2026-123894-/39495",
      "date": "2026-11-20"
    }
  ],
  "securityEventDate": "2026-11-20",
  "security": {
    "severity": "Critical · 9.8 CVSS v3 base score (Broadcom)",
    "severitySource": "https://support.broadcom.com/web/ecx/support-content-notification/-/external/content/SecurityAdvisories/VMSA-2026-0009--VMware-vCenter--Tools--and-SDDC-Manager-updates-address-multiple-vulnerabilities--CVE-2026-123890--CVE-2026-123891--CVE-2026-123892--CVE-2026-123893--CVE-2026-123894-/39495",
    "affectedProducts": "VMware vCenter and the deployments listed in the affected-product matrix.",
    "recommendedActions": [
      "Use the exact fixed build listed for your deployment.",
      "Verify the deployed build and dependent service health after patching."
    ]
  }
}
---

Broadcom issued an advisory on November 19 for several VMware vulnerabilities and updated it on November 20. It rates CVE-2026-123890 critical and lists different fixed versions for different vCenter branches. For an administrator, the first task is to identify which component and release are actually installed.

## What Broadcom recommends

Use the fixed version in the response matrix for the deployment you manage. The advisory lists no workaround for the critical vCenter issue. Older installations may require a support discussion or an upgrade plan, so treat unknown or unsupported versions as an item that needs an owner and a decision. The VMware Tools and SDDC Manager entries have separate product conditions and should be reviewed independently.

| Deployment in Broadcom’s response matrix | Fixed version or guidance |
| --- | --- |
| VMware Cloud Foundation or VMware vSphere Foundation with vCenter 9.1.x.x | 9.1.1.0200 |
| VMware Cloud Foundation or VMware vSphere Foundation with vCenter 9.0.x.x | 9.0.2.0200 |
| VMware vCenter 8.0 | 8.0 U3m |
| VMware vCenter 7.0 | Broadcom directs extended-support customers to contact support |

## Confirm that the update landed

Verify the installed build and the health of the services that depend on it after the maintenance window. Record the checks that prove the change landed on each system. Broadcom’s base score is a severity assessment. It does not establish active exploitation.
