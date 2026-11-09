<!--
  Gabriele Lucia — GitHub profile.
  Look: bright white menu, cyan highlight, rounded tiles. Loosely inspired by a console home screen from the early 2010s.
  All graphics are drawn from scratch; the Mii-style avatar is my own.
  GitHub renders Markdown, images, tables and <details>. No custom CSS or JS.
-->

<div align="center">

<a href="https://oakvx.github.io/" title="Open my portfolio"><img src="./assets/welcome.png" width="100%" alt="Gabriele Lucia, software developer and graphic designer. A bright, menu-style banner with his Mii avatar and four tiles: Design, Web, Code, Systems." /></a>

<br/>

<a href="https://oakvx.github.io/"><b>PORTFOLIO</b></a> &nbsp; · &nbsp;
<a href="https://oakvx.github.io/chi-sono/"><b>ABOUT</b></a> &nbsp; · &nbsp;
<a href="https://oakvx.github.io/fuori-orario/"><b>AFTER HOURS</b></a> &nbsp; · &nbsp;
<a href="https://github.com/oakvx/synkris"><b>SYNKRIS</b></a> &nbsp; · &nbsp;
<a href="mailto:gabrielelucia07@gmail.com"><b>EMAIL</b></a>

<br/>

<sub>Sassuolo, Italy &nbsp; · &nbsp; Computer Engineering @ UNIMORE</sub>

<br/>

<a href="https://github.com/oakvx?tab=followers"><img alt="Followers" src="https://img.shields.io/github/followers/oakvx?style=flat-square&logo=github"/></a>
<a href="https://github.com/oakvx?tab=repositories"><img alt="Public repositories" src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fapi.github.com%2Fusers%2Foakvx&query=%24.public_repos&label=repositories&style=flat-square&logo=github"/></a>
<a href="https://github.com/oakvx/synkris"><img alt="synkris" src="https://img.shields.io/github/last-commit/oakvx/synkris/master?style=flat-square&label=synkris"/></a>
<a href="https://github.com/oakvx/bratAnimator"><img alt="bratAnimator" src="https://img.shields.io/github/last-commit/oakvx/bratAnimator?style=flat-square&label=bratAnimator"/></a>
<a href="https://github.com/oakvx/middleManPS4"><img alt="middleManPS4" src="https://img.shields.io/github/last-commit/oakvx/middleManPS4?style=flat-square&label=middleManPS4"/></a>

</div>

<h3>
<picture>
<source media="(prefers-color-scheme: dark)" srcset="./assets/headings/hello-dark.png" />
<img src="./assets/headings/hello-light.png" width="194" height="42" alt="Hi, I'm Gabriele." />
</picture>
</h3>

Computer engineering student, junior software developer and graphic designer. I work on both sides of a system: **the interface people touch and the logic behind it**. Current focus: local-first applications, consistency between a database and an external API, and evidence-driven reverse engineering.

<div align="center">

<img src="./assets/mii/standing.gif" width="115" alt="My Mii avatar, standing and waiting" />

</div>

<h2>
<picture>
<source media="(prefers-color-scheme: dark)" srcset="./assets/headings/right-now-dark.png" />
<img src="./assets/headings/right-now-light.png" width="159" height="48" alt="Right now" />
</picture>
</h2>

- **Building:** [synk / SYNKRIS](https://github.com/oakvx/synkris), an on-premise appointment and messaging system. 1.2.0-rc.6, a test release, not for live customer data.
- **Maintaining:** [Brat Animator](https://github.com/oakvx/bratAnimator), a client-side lyric-video editor with a deterministic Canvas compositor.
- **Researching:** [middleManPS4](https://github.com/oakvx/middleManPS4) (v0.17): PS4 payloads, ELF/Orbis analysis and network metadata, on hardware I own.
- **Studying:** Computer Engineering at the University of Modena and Reggio Emilia.

<h2>
<picture>
<source media="(prefers-color-scheme: dark)" srcset="./assets/headings/projects-dark.png" />
<img src="./assets/headings/projects-light.png" width="130" height="48" alt="Projects" />
</picture>
</h2>

<h3>
<picture>
<source media="(prefers-color-scheme: dark)" srcset="./assets/headings/backend-app-logic-dark.png" />
<img src="./assets/headings/backend-app-logic-light.png" width="264" height="42" alt="Backend &amp; App Logic" />
</picture>
</h3>

<table>
<tr>
<td width="33.33%" valign="top">
<a href="https://oakvx.github.io/bratAnimator/"><img src="./assets/brat-animator.png" width="100%" alt="Brat Animator: JavaScript, Canvas and WebCodecs" /></a>
<br/>
<b>Brat Animator</b><br/>
Static web app, no backend. Timestamp-driven Canvas 2D compositor (preview and export share the same frames), WebCodecs MP4 export with a capability probe, IndexedDB project storage, <code>.brat.zip</code> archives, PWA with a versioned service worker.
<br/>
<sub>JavaScript · Canvas 2D · WebCodecs · IndexedDB · Service Worker</sub>
<br/>
<a href="https://github.com/oakvx/bratAnimator">Code</a> · <a href="https://oakvx.github.io/bratAnimator/">Try it</a> · <a href="https://oakvx.github.io/projects/brat-animator/">Case study</a>
</td>
<td width="33.33%" valign="top">
<a href="https://github.com/oakvx/synkris"><img src="./assets/synk.png" width="100%" alt="synk by SYNKRIS: Node.js, PHP, PostgreSQL, Google Calendar and WhatsApp Web" /></a>
<br/>
<b>synk / SYNKRIS</b> · 1.2.0-rc.6<br/>
Docker Compose stack: Node.js bot, PHP dashboard, PostgreSQL 16. A GiST exclusion constraint prevents double booking; Google Calendar side effects go through a transactional outbox with leases and fencing tokens, plus a compensation saga. WhatsApp via WhatsApp Web, optional local Ollama.
<br/>
<sub>Node.js · PHP · PostgreSQL · Docker · Google Calendar API</sub><br/>
<sub>Proprietary, source-available. Real-provider testing and security review pending.</sub>
<br/>
<a href="https://github.com/oakvx/synkris"><b>Repository</b></a> · <a href="https://oakvx.github.io/projects/synk/">Case study</a> · <a href="https://oakvxish.github.io/synkris.github.io/">Project site</a>
</td>
<td width="33.33%" valign="top">
<a href="https://oakvx.github.io/projects/beautify/"><img src="./assets/beautify.png" width="100%" alt="Beautify: PHP and MySQL" /></a>
<br/>
<b>Beautify</b><br/>
Diploma project: multi-salon CRM in PHP/MySQL covering clients, staff roles, appointments, stock and analytics, with per-salon data separation and shared availability checks.
<br/>
<sub>PHP · MySQL</sub>
<br/>
<a href="https://github.com/oakvxish/maturita">Code</a> · <a href="https://oakvx.github.io/projects/beautify/">Case study</a>
</td>
</tr>
</table>

<h3>
<picture>
<source media="(prefers-color-scheme: dark)" srcset="./assets/headings/reverse-engineering-dark.png" />
<img src="./assets/headings/reverse-engineering-light.png" width="252" height="42" alt="Reverse Engineering" />
</picture>
</h3>

<table>
<tr>
<td width="100%" valign="top">
<a href="https://github.com/oakvx/middleManPS4"><img src="./assets/middleman-ps4.png" width="100%" alt="middleManPS4: Python, ELF and Orbis analysis, optional Ghidra export" /></a>
<br/>
<b>middleManPS4</b> · research / WIP · v0.17
<br/><br/>
Python (stdlib only) host tooling and C payloads around three questions: how a payload is loaded, what is inside the binaries, what is visible on the wire. Includes ELF validation and sending to <code>elfldr</code>, read-only firmware readout, an offline ELF/Orbis/PSF/NID toolkit with JSON/Markdown reports and optional Ghidra export, passive DNS/TCP/TLS metadata tools, and an offline workbench with integrity-checked reports.
<br/><br/>
<sub>Tested on one console (PS4, 12.52, GoldHEN) where documented. Read-only diagnostics and offline analysis; no PSN bypass or firmware-spoofing claims.</sub>
<br/><br/>
<a href="https://github.com/oakvx/middleManPS4">Code, evidence and roadmap</a>
</td>
</tr>
</table>

<h3>
<picture>
<source media="(prefers-color-scheme: dark)" srcset="./assets/headings/design-web-dark.png" />
<img src="./assets/headings/design-web-light.png" width="185" height="42" alt="Design &amp; Web" />
</picture>
</h3>

<table>
<tr>
<td width="50%" valign="top">
<a href="https://oakvx.github.io/"><img src="./assets/portfolio.png" width="100%" alt="My site: HTML, CSS and JavaScript" /></a>
<br/>
<b>Portfolio</b><br/>
Static site, no build step: vanilla HTML/CSS/JS, generated EN pages, CI checks for links, SEO, accessibility and sitemap, reduced-motion support.
<br/>
<a href="https://github.com/oakvx/oakvx.github.io">Code</a> · <a href="https://oakvx.github.io/">Visit</a>
</td>
<td width="50%" valign="top">
<a href="https://oakvx.github.io/autoOfficina/"><img src="./assets/spinotto-felice.png" width="100%" alt="Spinotto Felice: a fictional small-business website demo" /></a>
<br/>
<b>Spinotto Felice</b> (fictional demo)<br/>
Reusable small-business site: responsive layout, light/dark themes, FAQ, saved preferences.
<br/>
<a href="https://github.com/oakvx/autoOfficina">Code</a> · <a href="https://oakvx.github.io/autoOfficina/">Live demo</a> · <a href="https://oakvx.github.io/projects/autoofficina/">Case study</a>
</td>
</tr>
<tr>
<td width="50%" valign="top">
<a href="https://oakvx.github.io/topGun/"><img src="./assets/top-gun.png" width="100%" alt="Top Gun Fly School: an unofficial one-file landing-page demo" /></a>
<br/>
<b>Top Gun Fly School</b> (unofficial demo)<br/>
Single-file landing page. Not for bookings or flight information.
<br/>
<a href="https://github.com/oakvx/topGun">Code</a> · <a href="https://oakvx.github.io/topGun/">Live demo</a>
</td>
<td width="50%" valign="top">
<a href="https://oakvxish.github.io/synkris.github.io/"><img src="./assets/synkris-site.png" width="100%" alt="Synkris: coming-soon website with interactive demonstrations" /></a>
<br/>
<b>Synkris site</b><br/>
Static project site with illustrative scenarios. The application lives in <a href="https://github.com/oakvx/synkris"><b>oakvx/synkris</b></a>; the site is not a booking service.
<br/>
<a href="https://github.com/oakvxish/synkris.github.io">Website code</a> · <a href="https://oakvxish.github.io/synkris.github.io/">Visit</a>
</td>
</tr>
</table>

<sub><b>Demo credits:</b> Spinotto Felice's structure and style are mine; its fictional content and AI-generated images are by <a href="https://www.albertopecchini.it">Alberto Pecchini</a>. The business is invented; the demo takes no real orders or bookings.</sub>

<div align="center">

<a href="https://github.com/oakvx?tab=repositories"><b>All repositories →</b></a>

</div>

<h2>
<picture>
<source media="(prefers-color-scheme: dark)" srcset="./assets/headings/focus-toolbox-dark.png" />
<img src="./assets/headings/focus-toolbox-light.png" width="241" height="48" alt="Focus &amp; toolbox" />
</picture>
</h2>

<img src="./assets/toolkit.png" width="100%" alt="Four tiles: Web (HTML, CSS, JS, Canvas), Backend (Node.js, PHP, Git), Data (PostgreSQL, MySQL, SQL Server), Systems (Windows, Active Directory, PLC basics)" />

| Area | Tools |
| :-- | :-- |
| Web | HTML, CSS, JavaScript, Canvas 2D, WebCodecs, MediaRecorder, IndexedDB, service workers, accessibility, SEO |
| Backend | Node.js, Express, PHP, Docker Compose, Git, CI (GitHub Actions) |
| Data | PostgreSQL (constraints, outbox/queue patterns, `SKIP LOCKED`), MySQL, SQL Server (T-SQL) |
| Reverse engineering | Python, C payloads, ELF/Orbis/PSF/NID, Ghidra, passive DNS/TLS/TCP metadata |
| Systems | Windows, Active Directory, IT support, industrial software, PLC basics |

> **Principles:** local-first when it fits · explicit states over assumed success · evidence over assumptions · accessible motion.

<h2>
<picture>
<source media="(prefers-color-scheme: dark)" srcset="./assets/headings/where-ive-been-dark.png" />
<img src="./assets/headings/where-ive-been-light.png" width="238" height="48" alt="Where I've been" />
</picture>
</h2>

| When | What |
| :-- | :-- |
| **2026 →** | **Computer Engineering**, University of Modena and Reggio Emilia (UNIMORE) |
| **Aug–Sep 2026** | **Software & automation apprentice**, Format SRL: industrial software, PLC support, SQL Server, T-SQL |
| **2023–Jun 2026** | **Freelance web developer & SEO consultant** for local businesses around Sassuolo and Scandiano |
| **May–Jun 2025** | **Erasmus+ at Starbotica, Seville:** IT support, Windows, Active Directory, local networks |
| **2021–2026** | **Computer Science & Telecommunications**, IIS A. Volta, Sassuolo; Beautify was my diploma project |

<h2>
<picture>
<source media="(prefers-color-scheme: dark)" srcset="./assets/headings/after-hours-dark.png" />
<img src="./assets/headings/after-hours-light.png" width="169" height="48" alt="After hours" />
</picture>
</h2>

| | |
| :-- | :-- |
| **Languages** | Italian (native) · English (C1) · Spanish (B1) · Greek (B1) · Chinese (A2) |
| **Consoles** | Modded Nintendo 3DS (three), Wii U, Wii, PlayStation 4 |

<a href="https://oakvx.github.io/fuori-orario/"><b>Open After Hours →</b></a>

<details>
<summary><b>My avatar, in motion</b></summary>

Animations of my avatar made for my website.

<p align="center">
<img src="./assets/mii/dancing.gif" width="125" alt="Avatar dancing" />
<img src="./assets/mii/laughing.gif" width="125" alt="Avatar laughing" />
<img src="./assets/mii/idlewainting.gif" width="125" alt="Avatar waiting around" />
<img src="./assets/mii/almostfalling.gif" width="125" alt="Avatar almost falling over" />
<img src="./assets/mii/angrystomping.gif" width="125" alt="Avatar stomping angrily" />
</p>

</details>

<details>
<summary><b>Leggi in italiano</b></summary>

Sono **Gabriele Lucia**, di Sassuolo. Studio Ingegneria Informatica all'UNIMORE e mi divido tra sviluppo software, grafica e interfacce.

- **Backend e logica applicativa:** [synk / SYNKRIS](https://github.com/oakvx/synkris) (Node.js, PHP, PostgreSQL, Google Calendar, WhatsApp Web; RC di collaudo), Brat Animator (compositor Canvas e export nel browser) e Beautify.
- **Reverse engineering:** [middleManPS4](https://github.com/oakvx/middleManPS4), laboratorio per payload PS4, analisi offline di ELF/Orbis e osservabilità di rete sulla mia console.
- **Design e web:** portfolio, demo Spinotto Felice, landing Top Gun Fly School e sito Synkris.

Ho lavorato come sviluppatore web freelance e consulente SEO, ho fatto supporto IT durante l'Erasmus a Siviglia e mi sono occupato di software industriale, PLC e SQL Server.

</details>

<div align="center">

<a href="mailto:gabrielelucia07@gmail.com"><img src="./assets/contact.png" width="100%" alt="Got a project, a job or a weird idea? gabrielelucia07@gmail.com" /></a>

<a href="mailto:gabrielelucia07@gmail.com">Email</a> &nbsp; · &nbsp;
<a href="https://oakvx.github.io/">Portfolio</a> &nbsp; · &nbsp;
<a href="https://github.com/oakvx">GitHub</a> &nbsp; · &nbsp;
<a href="https://github.com/oakvx/synkris">SYNKRIS</a>

<sub>© 2026 Gabriele Lucia · Graphics and avatar are my own work.</sub>

</div>
