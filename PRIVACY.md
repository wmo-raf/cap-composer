# Data Protection and Privacy Statement — CAP Composer

**Version:** 1.0 · **Date:** September 2026 · **Maintainer:** WMO Regional Office for Africa (wmo-raf)

This document describes how CAP Composer handles data, which privacy and data-protection frameworks its design follows, and how responsibilities are divided between WMO (the software developer) and the institutions that deploy it. It complements [LEGAL.md](LEGAL.md) (liability terms), [LICENSE](LICENSE) (MIT) and the [user documentation](https://climweb.readthedocs.io/en/latest/_docs/manage_cap/index.html).

> This statement is provided in good faith to support Digital Public Good and institutional due-diligence reviews. It is not legal advice. Deploying institutions remain responsible for their own compliance assessment under the laws that apply to them.

---

## 1. What CAP Composer is, and who is responsible for the data

CAP Composer is free, open-source software (Django/Wagtail) that National Meteorological and Hydrological Services (NMHSs) and disaster-management agencies install on their own infrastructure to author, approve and publish public hazard warnings in the [Common Alerting Protocol (CAP) 1.2](https://docs.oasis-open.org/emergency/cap/v1.2/CAP-v1.2-os.html) standard.

| Role | Who | Notes |
|---|---|---|
| Software developer / publisher | WMO Regional Office for Africa | Publishes the code. **Operates no central instance, receives no data from deployments.** |
| Data controller | The deploying institution (NMHS / agency) | Decides who gets an account, what alerts are issued, and how long records are kept. |
| Data processor(s) | None by default | Each deployment is self-hosted. If the institution connects an external email or MQTT service, that provider becomes its processor under the institution's own agreement. |

CAP Composer contains **no telemetry, analytics, tracking or "phone home" functionality**. WMO has no technical access to any deployed instance.

## 2. Inventory of data processed

Alert content is public, non-personal information about hazards. The only personal data in CAP Composer is the account data of the authorised staff who operate it. No data about members of the public is processed.

| Category | Examples | Personal data? | Purpose | Lawful basis (GDPR Art. 6) | Retention |
|---|---|---|---|---|---|
| Staff user accounts | Username, display name, work email, hashed password, role/group, 2FA secret, last-login timestamp | **Yes** (staff only) | Authentication, role-based access, audit trail of who drafted/approved/published an alert | Art. 6(1)(e) public task; Art. 6(1)(b)/(c) for the employment relationship | Until the account is removed by the institution's administrator |
| Alert content (CAP message) | Event, severity, urgency, headline, description, instruction, affected area/polygons, effective/expiry times | No | Public hazard warning | n/a | Kept as public record of warnings issued; institution sets its archive policy |
| CAP `sender`, `contact`, `web` fields | Name of the issuing institution, institutional email or duty-office phone, institutional website | No (institutional identifiers, not individuals) | Required by the CAP standard so recipients can verify the source and follow up | n/a | Same as the alert |
| Workflow metadata | Draft/review/approval comments, revision history, moderation log | Contains staff identifiers | Accountability and collaboration between authorised staff | Art. 6(1)(e) | Same as the alert or per institutional policy |
| Reference data | Administrative boundaries, hazard types, alert areas, predefined templates | No | Alert composition | n/a | Indefinite |
| Server logs | IP address, user-agent, requested URL (nginx / application logs) | Yes (technical) | Security and troubleshooting | Art. 6(1)(f) legitimate interest / 6(1)(e) | Default log rotation; configurable by the operator |

**Not processed:** data about the public who receive alerts (no subscriber lists, no location tracking, no cookies beyond the session cookie required for admin login), special-category data, children's data, payment data.

## 3. How GDPR principles are implemented

The EU General Data Protection Regulation (Regulation (EU) 2016/679) applies directly only to controllers established in the EU/EEA or targeting EU data subjects. Most CAP Composer deployments are outside that scope. WMO nonetheless adopts GDPR as the **design benchmark**, because it is the most widely recognised standard and because most African and other national data-protection laws (see §5) follow the same principles.

| GDPR principle / obligation | How CAP Composer implements it |
|---|---|
| **Lawfulness, fairness, transparency** (Art. 5(1)(a)) | Processing is limited to public-task alerting by a public authority. This document and the open-source code provide transparency. |
| **Purpose limitation** (Art. 5(1)(b)) | Staff data is used only for authentication and workflow accountability. No secondary use, profiling or marketing. |
| **Data minimisation** (Art. 5(1)(c)) | Only fields required to operate the workflow and to comply with the CAP standard are collected. No optional personal fields are added by the software. |
| **Accuracy** (Art. 5(1)(d)) | Administrators and users can edit account details at any time through the admin interface. |
| **Storage limitation** (Art. 5(1)(e)) | Accounts can be deactivated or deleted by administrators. Alert records are retained as public warning records; retention is set by the institution. |
| **Integrity and confidentiality** (Art. 5(1)(f), Art. 32) | Passwords stored using Django's salted PBKDF2 hashing; optional enforced two-factor authentication; role-based permissions (Wagtail groups); configurable admin URL; secrets kept in environment variables, not in code; HTTPS via the bundled nginx configuration; Docker-based isolation. |
| **Accountability** (Art. 5(2)) | Revision history and moderation log record who did what and when. This document supports the institution's record of processing. |
| **Data protection by design and by default** (Art. 25) | No tracking or analytics; no public-user data model; personal data confined to the staff-account model; 2FA available out of the box. |
| **Records of processing** (Art. 30) | Section 2 of this document can be adopted directly into the institution's record of processing activities. |
| **Data subject rights** (Art. 15–22) | Staff can view and correct their own profile. Administrators can export (via Django admin / database), rectify, restrict (deactivate) or erase an account on request. |
| **Data Protection Impact Assessment** (Art. 35) | Not required: processing is low-risk, small-scale, staff-only and involves no special categories, no systematic monitoring and no new technology. Institutions may nevertheless use §2–§3 as the basis for a DPIA if their national authority requires one. |
| **International transfers** (Chapter V) | None by design. All data stays on the institution's own servers. |
| **Processors** (Art. 28) | None by default. The institution is responsible for a processing agreement with any email/SMS/MQTT provider it chooses to connect. |

## 4. Alignment with the UN Personal Data Protection and Privacy Principles

WMO is a UN specialized agency. The [UN Personal Data Protection and Privacy Principles](https://unsceb.org/privacy-principles) (adopted by the UN High-Level Committee on Management, 2018) guide how the software was designed.

| UN Principle | Implementation in CAP Composer |
|---|---|
| 1. Fair and legitimate processing | Processing serves the public-safety mandate of the issuing authority. |
| 2. Purpose specification | Purposes are fixed and documented in §2. |
| 3. Proportionality and necessity | Only staff-account and CAP-mandated fields; no data about the public. |
| 4. Retention | Controlled by the institution; accounts deletable; alert archive is a public record. |
| 5. Accuracy | Editable profiles; revision history. |
| 6. Confidentiality | Role-based access; hashed credentials; 2FA. |
| 7. Security | See Art. 32 row in §3; security issues can be reported per the repository's security policy. |
| 8. Transparency | Open-source code (MIT); this statement; public documentation. |
| 9. Transfers | None by design (self-hosted). |
| 10. Accountability | Audit trail; clear controller/developer split in §1. |

## 5. Other applicable frameworks

- **Common Alerting Protocol v1.2 (OASIS standard; adopted by WMO and ITU-T X.1303)** — defines the alert data model. CAP Composer produces conforming messages; the standard contains no fields for data about the public.
- **WMO Unified Data Policy (Resolution 1, Cg-Ext(2021))** — warnings are "core" data intended for free and unrestricted public exchange, which is why alert content is treated as public information.
- **African Union Convention on Cyber Security and Personal Data Protection (Malabo Convention, 2014)** — the regional reference for most deployments; its principles mirror those in §3.
- **National data-protection laws** of the deploying country (for example Kenya Data Protection Act 2019, Nigeria Data Protection Act 2023, Ghana Data Protection Act 2012, Rwanda Law No. 058/2021, Loi 2013-450 in Côte d'Ivoire). The deploying institution is the controller under these laws.

## 6. What deploying institutions must do

- Appoint an administrator responsible for creating, reviewing and removing staff accounts.
- Enable enforced 2FA and serve the admin interface over HTTPS.
- Keep the CAP `contact` field institutional (duty office, not an individual), as is already standard practice.
- Set a log-rotation and alert-archive retention policy.
- Sign a processing agreement with any third-party email/SMS/MQTT provider they connect.
- Register the processing with their national data-protection authority if national law requires it.

## 7. Contact

Questions about this statement or the software's data handling: open an issue in this repository or contact the WMO Regional Office for Africa. Questions about a specific deployment should be directed to the deploying institution.
