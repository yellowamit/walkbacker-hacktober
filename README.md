# 🌿 WalkBacker: Touch Grass Offline AI Expedition Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![RAM Optimized](https://img.shields.io/badge/RAM_Budget-%3C1GB_(8GB_Device_Safe)-brightgreen.svg)]()
[![Challenge](https://img.shields.io/badge/DEV_Challenge-Touch_Grass_(Week_1)-orange.svg)](https://dev.to/challenges/hacktoberfest-week1-2026-10-05)

**WalkBacker** is an offline-first, screen-minimal AI expedition agent and trail companion built for the **Hacktoberfest Open-Source AI Challenge Week 1: "Touch Grass"**.

It is engineered to get people off their glowing screens and into the natural world. Unlike conventional trail apps that trap users into staring at GPS dots and notifications, WalkBacker enforces the **60-Second Screen Rule**: configure your walk in under a minute, slip your phone into your pocket, and let hands-free audio cues and a safe reverse-compass guide your return.

---

## 🎯 Key Features

- **⏱️ The 60-Second Screen Rule**: Plan your nature walk in under a minute. The AI synthesizes a **Pocket Field Card** that can be reviewed in 30 seconds before putting your phone away.
- **🧠 4-Stage Chain of Thought (CoT) Engine**:
  - `Stage 1: Environmental & Solar Analysis`: Calculates solar elevation and civil twilight without internet.
  - `Stage 2: Sensory Touch-Grass Missions`: Formulates tactile and acoustic tasks (leaf venation, tree bark textures, bird song listening).
  - `Stage 3: Safe Navigation & Turnaround Mathematics`: Calculates exact outbound turnaround time ($T_{\text{outbound}} = \frac{T}{2} \times 0.85$) and computes reverse azimuth.
  - `Stage 4: Screen Minimization Protocol`: Formulates hands-free audio guidance and turnaround alarm.
- **🧭 WalkBacker Compass & Breadcrumb Radar**: High-contrast, sunlight-readable single-needle compass pointing directly back to trailhead base with real-time distance.
- **🎧 Offline Audio Cues & Turnaround Chime**: Uses native browser Web Speech synthesis and AudioContext to sound a gentle chime and vocal guidance into headphones with zero cellular data.
- **🔍 Offline Nature Identifier (Trail Lens)**: Instant offline botanical and songbird identification key for trailside observations without internet.
- **💾 Open Standards Export**: 1-click GPX and GeoJSON exports for OsmAnd, Organic Maps, Garmin, and QGIS.
- **⚡ 8GB RAM Hardware Guardrails**: Operates at **~85 MB process RAM**; protects low-memory devices with strict memory safety boundaries and lazy-loading for open-weight models (`SmolLM2-135M` / `Qwen2.5-0.5B`).

---

## 💻 Hardware & Memory Specification (8GB RAM Target)

| Component | RAM Footprint | Execution Strategy |
| :--- | :--- | :--- |
| **WalkBacker Server & Backend** | **~85 MB** | Asynchronous FastAPI + Starlette core |
| **Edge Zero-RAM CoT Engine** | **0 MB added** | Deterministic astronomical & ecological reasoning |
| **Local Open-Weight Model (Optional)** | **~350 MB** | `SmolLM2-135M-Instruct` CPU inference |
| **System Headroom on 8GB PC** | **> 2.5 GB Free** | Zero page swapping or system lag guaranteed |

---

## 🚀 Quickstart Guide

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/your-username/walkbacker-hacktober.git
cd walkbacker-hacktober

python -m pip install -r requirements.txt
```

### 2. Launch WalkBacker
```bash
python run.py
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser or phone on the local Wi-Fi.

### 3. Run Automated Tests
```bash
python -m pytest tests/test_walkbacker.py -v
```

---

## 📁 Repository Structure

```
walkbacker-hacktober/
├── backend/
│   ├── main.py              # FastAPI server & static delivery
│   ├── config.py            # Configuration & memory caps
│   ├── agent/
│   │   ├── cot_reasoner.py  # 4-stage Chain of Thought reasoning engine
│   │   ├── model_loader.py  # RAM-safety guardrails for 8GB devices
│   │   └── prompts.py       # CoT prompts & nature vibe catalog
│   ├── nature/
│   │   ├── identifier.py    # Offline trait & morphological classifier
│   │   └── taxonomy_db.py   # Curated autumn flora, fungi & songbird DB
│   └── navigation/
│       ├── breadcrumb.py    # Haversine distance, dead reckoning & solar equations
│       └── gpx_exporter.py  # GPX & GeoJSON trail exporter
├── frontend/                # Outdoor sunlight-optimized UI
│   ├── index.html           # Main interface & Pocket Mode
│   ├── css/style.css        # Sunlight contrast theme & E-ink aesthetic
│   └── js/
│       ├── app.js           # State manager & API client
│       ├── compass.js       # Device orientation controller
│       └── audio_cue.js     # Offline speech synthesis & tone generator
├── docs/
│   ├── CHAIN_OF_THOUGHT.md  # Live context & decision ledger
│   ├── ARCHITECTURE.md      # Memory budget & technical design
│   └── DEV_SUBMISSION.md    # Official DEV.to challenge submission draft
├── tests/
│   └── test_walkbacker.py   # 9/9 automated unit tests
├── requirements.txt         # Lightweight dependencies
└── run.py                   # Server startup script
```

---

## 🌿 Why Open Innovation Matters

1. **Trail Dead Zones**: Cellular signal vanishes in dense woods, valleys, and national parks. Open-weight models run locally where closed APIs fail.
2. **Absolute Privacy**: No tracking of your walking routes, coordinates, or habits. All computations happen on-device.
3. **Low-Memory Inclusion**: Designed specifically for 8GB RAM consumer laptops, making AI accessible without high-end cloud subscriptions.
4. **Zero Cost**: Completely free and open-source under the MIT License.

---

## 📜 License
MIT License. Feel free to use, modify, and take it outside to touch grass!
