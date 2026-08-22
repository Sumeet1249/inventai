# InventAI 🚀

**InventAI** is an autonomous engineering platform that turns raw ideas into 3D CAD models, physics simulations, market analysis, academic research synthesis, and patent drafts in minutes. It relies on a multi-agent orchestrated architecture powered by LLMs.

---

## 🌟 Key Features

1. **CAD Generation Agent**: Uses AI to write CadQuery scripts to generate parametric 3D models (GLTF, STEP, STL).
2. **Physics Simulation Agent**: Implements DeepXDE (Physics-Informed Neural Networks) to calculate structural stress, safety factors, and generate stress heatmaps.
3. **Business Intelligence Agent**: Uses web scraping and LLMs to analyze market size, calculate BOM (Bill of Materials), and estimate MSRP.
4. **Research RAG Agent**: Synthesizes data from academic databases (arXiv, PubMed, IEEE) to provide literature reviews and technological validation.
5. **Patent Analysis Agent**: Evaluates the idea against existing prior art to score novelty, identify innovation gaps, and draft a foundational patent application.
6. **Report Generation Agent**: Packages all outputs from the other agents into a unified, professional PDF/DOCX engineering report.

---

## 🏗 Architecture

InventAI uses a highly modular microservices architecture:

- **Web Frontend**: Next.js 15 app with a modern, white-themed responsive UI.
- **Innovation Engine**: The central orchestrator running LangGraph, coordinating parallel agents.
- **Microservices**: Dedicated FastAPI services for each agent (CAD, Physics, Business, Research, Patent, Report).
- **API Gateway**: Nginx reverse proxy routing requests between the frontend and microservices.
- **AI Core**: Shared library for robust model handling (Google Gemini, OpenAI, HuggingFace embeddings).

---

## 🚀 How to Run the Project

### 1. Prerequisites

Before you begin, ensure you have the following installed and running:

- **Docker Desktop**: Must be installed and **running** before executing any commands.
- Node.js 18+ (Optional, for local frontend dev)
- Python 3.11+ (Optional, for local backend dev)

### 2. Environment Setup

Create a `.env` file in the root directory and add your API keys. You can use the provided `.env.example` file as a template:

```bash {"metadata":"[object Object]"}
cp .env.example .env
```

Open the `.env` file and add your required keys:

```ini {"metadata":"[object Object]"}
# Required keys
GOOGLE_API_KEY=your_gemini_api_key
HF_TOKEN=your_huggingface_token
```

_(Optionally add `OPENAI_API_KEY` for fallback generation)._

### 3. Start the Platform

Run the entire platform using Docker Compose. This will build and spin up the Nginx gateway, Next.js frontend, and all 7 FastAPI microservices.

```bash {"metadata":"[object Object]"}
# 1. Start all containers (in detached mode)
docker compose up -d --build

# 2. Wait a few minutes for the initial build and startup to complete.

# 3. Access the Application
# The frontend will be available at:
http://localhost:3001
```

*(Note: If you encounter an error regarding `prometheus.yml` being a directory, ensure the file `infrastructure/monitoring/prometheus.yml` exists as a file, not a folder, before running docker compose).*

### Usage

1. Navigate to `http://localhost:3001/projects/new`.
2. Enter your invention idea. For a comprehensive test of all 6 agents, you can paste the following detailed example:

   > **Example Idea: Foldable Bridge Inspection Drone**
   > A modular, foldable quadcopter drone designed specifically for bridge and tunnel infrastructure inspection. The frame is constructed from carbon fiber reinforced polymer (CFRP) with a 450mm diagonal motor-to-motor span that folds to 180mm for transport. It uses 4x T-Motor MN3510 motors with 12-inch propellers, powered by a 6S 10,000mAh LiPo battery providing 35-minute flight time.

> The drone integrates:
>
> - Dual 4K optical cameras (nadir + oblique) with 3-axis gimbal stabilization
> - Pulsed ultrasonic transducers (200kHz) for concrete crack detection up to 300mm depth
> - FLIR thermal camera for moisture and delamination mapping
> - 16-line LiDAR (Velodyne VLP-16) for sub-centimeter 3D point cloud generation
> - Edge AI compute module (NVIDIA Jetson Orin NX 16GB) running YOLOv8 trained on 50,000 labeled bridge defect images
>
> The AI system automatically classifies cracks (hairline, structural, fatigue), corrosion levels (Grade 1-5 per ASTM D610), and spalling with confidence scores. Results are uploaded in real-time to a cloud dashboard via 4G LTE, generating automated inspection reports compliant with AASHTO and FHWA standards. Target market: Departments of Transportation, railway authorities, and civil engineering consultancies. Target unit price: $12,000 with $2,400/year SaaS subscription.

3. Click **Launch 6 AI Agents**.
4. Watch the live dashboard as agents generate your CAD model, run physics simulations, analyze the market, and draft your patent in real-time!

---

## 🛠 Tech Stack

- **Frontend**: Next.js, React, Tailwind CSS, TanStack Query
- **Backend**: FastAPI, LangGraph, LangChain, CadQuery, DeepXDE
- **Models**: Gemini 2.0 Flash (Primary), GPT-4 (Fallback), sentence-transformers (Embeddings)
- **Infrastructure**: Docker, Docker Compose, Nginx

---

## 👨‍💻 Developed by

**Coders Team** | Netaji Subhash Engineering College
