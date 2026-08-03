
# 🚗 Road Monitor — Smart Subsidence Detection and Analysis for Greener Urban Mobility

> **Road Monitor** is an AI-powered system designed to detect, evaluate, and map road hazards (such as potholes and subsidence) using Computer Vision (YOLO26n). It aims to optimize driving routes, lower vehicle emissions, and improve urban safety.

---

## 👥 Team Members & Advisors

### Group 7

* **Hồ Trần Châu Thảo** — *Leader*
* **Phạm Minh Long**
* **Võ Nguyễn Trọng Phú**

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

## 🛠️ Data & AI Architecture

* **Dataset:** 665 public dataset images (Split: **70% Train / 20% Val / 10% Test**)
* **Model:** Fine-tuned **YOLO26n** (Confidence Threshold = 0.40)
* **Tools:** Roboflow, Google Colab, YOLO26n
* **Risk Score Metric:**

$$\text{Risk Score} = \text{Total pothole points}$$


* **Low:** $\text{RS} < 3$
* **Medium:** $3 \le \text{RS} < 7$
* **High:** $\text{RS} \ge 7$



### 📊 Model Performance Metrics

| Metric | Value |
| --- | --- |
| **Precision** | 0.82 |
| **Recall** | 0.70 |
| **F1 Score** | 0.75 |
| **mAP50** | 0.66 |
| **mAP50-95** | 0.43 |

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

