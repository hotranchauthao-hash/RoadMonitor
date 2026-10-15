
# 🚗 Road Monitor — Smart Subsidence Detection and Analysis for Greener Urban Mobility

> **Road Monitor** is an AI-powered system designed to detect, evaluate, and map road hazards (such as potholes and subsidence) using Computer Vision (YOLO26n). It aims to optimize driving routes, lower vehicle emissions, and improve urban safety.

---

## 👥 Team

| Name | Role |
| --- | --- |
| Hồ Trần Châu Thảo | Project Leader |
| Võ Nguyễn Trọng Phú | Technical Developer & Lead Researcher |
| Phạm Minh Long | AI Researcher |


### Advisors

* **Trịnh Trần Quốc Bảo**
* **Âu Đoàn Trung**

---

## 📌 Problem & Inspiration

* **Environmental & Traffic Impact:**
  * Increases fuel consumption by **3% to 5%** due to sudden braking and stop-and-go driving.
  * Causes a **25% to 45%** surge in $\text{CO}_2$ emissions per kilometer.
  * Contributes to **40% to 60%** of urban PM2.5 pollution.


* **Inspiration:** Preventable road hazards cause unnecessary pain and frustration to loved ones. Beyond saving lives, mitigating these hazards improves overall living quality and the environment.

---

## 💡 Solution Overview

1. **Detect:** Automatically identify potholes from road images using computer vision.
2. **Map & Score:** Map detected potholes with severity scores (*Minor, Moderate, Severe*) to support maintenance prioritization.
3. **Eco Benefit:** Reduce fuel waste, traffic congestion, and carbon emissions caused by poor road conditions.

---

## 🧰 Tech Stack

| Layer | Technology |
| --- | --- |
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla) |
| **Map** | Leaflet.js 1.9.4 |
| **Backend** | Python 3.9+, FastAPI |
| **AI Model** | YOLO26n (via Ultralytics) |
| **Image Processing** | Pillow (PIL) |
| **Server** | Uvicorn (ASGI) |
| **Data Storage** | JSON flat-file (`db.json`) |


## 🛠️ Data & AI Architecture

* **Dataset:** 665 public dataset images (Split: **70% Train / 20% Val / 10% Test**)
* **Model:** Fine-tuned **YOLO26n** (Confidence Threshold = 0.40)
* **Tools:** Roboflow, Google Colab, YOLO26n
* **Risk Score Metric:**

$$\text{Risk Score} = \text{Total pothole points}$$


* **Low:** $\text{RS} < 3$
* **Medium:** $3 \le \text{RS} < 7$
* **High:** $\text{RS} \ge 7$



## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────┐
│                   Frontend                       │
│         road_ai_monitor.html                     │
│  • Leaflet.js map with severity markers          │
│  • Live detection feed (sidebar)                 │
│  • Admin panel: CCTV grid + drag-and-drop upload │
│  • Auto-train modal with progress tracking       │
└────────────────────┬────────────────────────────┘
                     │ REST API (HTTP/JSON)
┌────────────────────▼────────────────────────────┐
│                FastAPI Backend                   │
│                  server.py                       │
│  POST /detect   — single image inference         │
│  POST /auto     — batch folder inference         │
│  GET  /db       — load detection history         │
│  PUT  /db       — save detection history         │
│  DELETE /db     — clear detection history        │
│  GET  /stats    — detection summary by severity  │
│  GET  /health   — model status check             │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│              YOLOv8n Model (best.pt)             │
│  • Trained on 665 road images                    │
│  • Classifies severity: Minor / Moderate / Severe│
│  • Returns bounding boxes + confidence scores    │
└─────────────────────────────────────────────────┘
```



### 📊 Model Performance Metrics

| Metric | Value |
| --- | --- |
| **Precision** | 0.82 |
| **Recall** | 0.70 |
| **F1 Score** | 0.75 |
| **mAP50** | 0.66 |
| **mAP50-95** | 0.43 |



## 🚀 Setup & Usage

### Prerequisites
- Python 3.9+
- A trained model weight file (`best.pt`) placed in the `AI Train/` folder

### Installation

```bash
cd "Code and server"
pip install -r requirements.txt
```

### Running the Server

```bash
python server.py
```

The dashboard will be available at `http://localhost:8000`.

### Auto-Detection Mode

To run batch detection on a folder of images:
```bash
# Place images in a folder named "pic1" next to server.py, then open:
http://localhost:8000  → Admin Panel → Auto Train
```

### Mock Mode

If `best.pt` is not present, the server runs in **mock mode** — returning simulated detections so the dashboard can be tested without a trained model.



## 📁 Folder Structure

```
RoadMonitor/
├── AI Train/
│   ├── best.pt          # Best YOLO model weights
│   └── last.pt          # Last checkpoint weights
├── Code and server/
│   ├── road_ai_monitor.html  # Frontend dashboard
│   ├── server.py             # FastAPI backend
│   └── requirements.txt      # Python dependencies
├── Slide/
│   └── Nhóm 7.mp4       # Project presentation video
└── README.md
```

---

## ⚠️ Limitations & Future Works

### Limitations

1. **Limited Camera Coverage:** Cannot access all traffic cameras.
2. **Missing Night Data:** Dataset currently lacks nighttime images.
3. **Simplified Risk Metric:** Pothole count alone is insufficient for precise road condition assessment.

### Future Works

* [ ] Incorporate nighttime images into the dataset.
* [ ] Convert camera measurements accurately from pixels to centimeters.
* [ ] Utilize pothole size and depth to assess road conditions more accurately.
* [ ] Partner/integrate features with Google Maps.

---

## 📚 Key References

1. **MIT Concrete Sustainability Hub** (*Pavement-Vehicle Interaction Model*) & **Vietnam University of Transportation**.
2. **The World Bank Group** & **UC Berkeley** (*Traffic Emissions Studies*).
3. **World Health Organization (WHO)** & **UNEP** (*Joint Report on Non-Exhaust Emissions*).
4. **UC Riverside (CE-CERT)** (*Eco-Routing Frameworks*).



## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

Please ensure your code follows the existing style and that the server starts without errors before submitting.
