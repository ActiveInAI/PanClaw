# Upstreams

Verified on 2026-05-16:

- OpenClaw: `openclaw/openclaw`, MIT, local-first personal AI assistant with channels and skills.
- Hermes Agent selected target: `NousResearch/hermes-agent`, not the low-signal `hermesagent` user account.
- WeChat official boundary: Official Account/Open Platform APIs only; personal account reverse engineering is excluded.
- WeCom group robot webhook: official WeCom developer documentation boundary.
- Feishu custom bot webhook: official Feishu Open Platform boundary.
- Lark custom bot webhook: official Lark Open Platform boundary.
- DingTalk custom robot webhook: official DingTalk Open Platform boundary.

Initial adapter targets requested by the product owner:

- PyMuPDF, python-docx, openpyxl
- Stable Diffusion WebUI API, Pillow
- Whisper, FFmpeg
- Blender Python API
- PyAutoGUI, Ansible
- psutil, Prometheus API
- Terraform, cloud provider Python SDKs
- AkShare, TuShare
- Playwright or Selenium
- BioPython, local medical RAG
- SymPy, Kiwix
- Scrapy, RSS
- FreeCAD Python API, GDAL
- Lunar calendar / traditional culture libraries

Each target must still pass license, maintenance, security and local installation review before being enabled for non-dry-run execution.

Official channel implementation notes live in [`OFFICIAL_CHANNELS.md`](./OFFICIAL_CHANNELS.md).
