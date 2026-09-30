# 🚧 Pothole Detection Report Generator
### Smart Cities & Infrastructure | Domain 7 | PS-SC1

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-orange)](https://ultralytics.com)
[![Gradio](https://img.shields.io/badge/UI-Gradio-ff6b6b)](https://gradio.app)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

> An AI-powered road damage detection system where citizens upload road images, and the system automatically detects damage type, assesses severity, geo-tags the location, and generates a structured municipal complaint report as a downloadable PDF.

---

## 👥 Team B6

| Name | Role | Modules Owned |
|---|---|---|
| **Rumanakhaisar P** | ML & Detection Lead | `detector.py`, `train.py`, `utils.py`, `evaluation.py` |
| **Karen P** | Backend Logic Lead | `severity.py`, `geocoder.py`, `report.py`, `database.py` |
| **Vijeta H** | Output & PDF Lead | `pdf_generator.py`, `vlm.py`, `demo_images/` |
| **Soujanaya T** | UI & Integration Lead | `app.py`, `run_pipeline.py`, `config.py` |

---

## 🎯 Problem Statement

Municipal corporations need efficient systems to detect and prioritise road damage. Citizens often face difficulty reporting road issues with enough technical detail for authorities to act promptly.

**Our solution:** A VLM-based system where a citizen uploads a road image → the system detects and classifies road damage → assesses severity → accepts GPS coordinates → and auto-generates a structured complaint report ready for municipal submission.

---

## ✅ Deliverables

- [x] Image classification with VLM (damage type + severity)
- [x] Auto-generated structured complaint report (PDF)
- [x] GPS tag input with reverse geocoding
- [x] Demo on 5 real road images from RDD2022 India dataset

---

## 🏗️ System Architecture

```
Citizen uploads image + GPS coordinates
            │
            ▼
    ┌─────────────────┐
    │ Image Preprocess │  utils.py
    │ Resize + Normalize│
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  YOLOv8s Model  │  detector.py
    │  Damage Detection│
    └────────┬────────┘
             │
     ┌───────┴────────┐
     ▼                ▼
┌─────────┐    ┌─────────────┐
│Severity │    │  Geocoder   │  severity.py
│Estimator│    │  Nominatim  │  geocoder.py
└────┬────┘    └──────┬──────┘
     │                │
     └────────┬───────┘
              ▼
    ┌─────────────────┐
    │  VLM (Claude)   │  vlm.py
    │  Description    │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Report Generator│  report.py
    │ + PDF Creator   │  pdf_generator.py
    └────────┬────────┘
             │
      ┌──────┴──────┐
      ▼             ▼
  ┌───────┐   ┌──────────┐
  │SQLite │   │ Gradio UI│  database.py
  │  DB   │   │  app.py  │  app.py
  └───────┘   └──────────┘
```

---

## 🧠 Damage Classes

| Class ID | Class Name | RDD2022 Code | Description |
|---|---|---|---|
| 0 | Longitudinal Crack | D00 | Cracks parallel to traffic direction |
| 1 | Transverse Crack | D10 | Cracks perpendicular to traffic direction |
| 2 | Alligator Crack | D20 | Interconnected fatigue cracking |
| 3 | Pothole | D40 | Holes in road surface |

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Object Detection | YOLOv8s (Ultralytics) |
| Vision-Language Model | Claude Vision API (Anthropic) |
| UI Framework | Gradio 4.x |
| Reverse Geocoding | Nominatim / geopy (OpenStreetMap) |
| PDF Generation | ReportLab |
| Database | SQLite (built-in Python) |
| Training Dataset | RDD2022 India + Annotated Pothole Dataset |

---

## 📁 Project Structure

```
Team-B6/
│
├── app.py                  # Gradio UI (Member 4)
├── run_pipeline.py         # Master pipeline orchestrator (Member 4)
├── config.py               # All paths, constants, thresholds (Member 4)
│
├── detector.py             # YOLOv8 inference (Member 1)
├── utils.py                # Image preprocessing (Member 1)
├── evaluation.py           # mAP metrics evaluation (Member 1)
├── train.py                # YOLOv8 training script (Member 1)
├── data.yaml               # Dataset configuration (Member 1)
│
├── severity.py             # Severity + priority logic (Member 2)
├── geocoder.py             # GPS reverse geocoding (Member 2)
├── report.py               # Report dict assembler (Member 2)
├── database.py             # SQLite CRUD operations (Member 2)
│
├── vlm.py                  # Vision Language Model wrapper (Member 3)
├── pdf_generator.py        # PDF report generation (Member 3)
│
├── models/
│   └── best.pt             # Trained YOLOv8s weights
│
├── demo_images/            # 5 real road images for demo
│   ├── demo_01_pothole.jpg
│   ├── demo_02_alligator.jpg
│   ├── demo_03_longitudinal.jpg
│   ├── demo_04_transverse.jpg
│   └── demo_05_severe.jpg
│
├── outputs/                # Auto-generated at runtime
│   ├── annotated/          # YOLO-annotated images
│   ├── reports/            # Generated PDFs
│   └── database/
│       └── complaints.db
│
├── requirements.txt
├── .gitignore              # Excludes .env, models/, outputs/
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/Gen-AI-Hackathon-2026/Team-B6.git
cd Team-B6
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set environment variable for Claude API
```bash
# Windows (Command Prompt)
set ANTHROPIC_API_KEY=your_api_key_here

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="your_api_key_here"

# Mac/Linux
export ANTHROPIC_API_KEY=your_api_key_here
```
> ⚠️ Never commit your API key. It is read from the environment variable only.

### 5. Add trained model weights
Place your trained `best.pt` file in the `models/` folder:
```
Team-B6/models/best.pt
```

### 6. Run the application
```bash
python app.py
```
Opens at `http://localhost:7860`

---

## 🚀 Demo

### Running the 5-image demo
```bash
python evaluation.py
```
This runs inference on all 5 demo images and displays mAP metrics.

### Live demo (public URL)
```bash
python app.py --share
```

---

## 📊 Model Performance

| Metric | Value |
|---|---|
| Model | YOLOv8s |
| Training Dataset | RDD2022 India + Pothole Dataset (~3,900 images) |
| Epochs | 50 |
| Image Size | 640×640 |
| mAP@50 | *(update after training)* |
| mAP@50-95 | *(update after training)* |

---

## 📋 Requirements

```
ultralytics>=8.0.0
gradio==4.44.0
anthropic>=0.25.0
geopy>=2.4.0
reportlab>=4.0.0
Pillow>=9.0.0
opencv-python>=4.8.0
numpy>=1.24.0
pandas>=2.0.0
pyyaml>=6.0
```

---

## 🤝 How to Contribute (Team Members)

1. Pull latest before starting work: `git pull origin main`
2. Work only on your assigned files
3. Test your module independently using `python your_file.py`
4. Never push `.env` files or `best.pt` to GitHub
5. Push to your branch, create PR to main

---

## 📄 License

This project is submitted as part of the **Gen AI Hackathon 2026**.

---

*Built with ❤️ by Team B6 — Rumanakhaisar P, Karen P, Vijeta H, Soujanaya T*
