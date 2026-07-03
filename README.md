# 🚨 ResQAI – AI Emergency Command Center

**ResQAI** is an AI-powered emergency response support system designed to help crisis management teams quickly assess disaster situations, estimate required medical and field resources, evaluate hospital capacity, and generate structured emergency response plans.

Built for the **Google × Kaggle Capstone Project**, ResQAI combines **Google Gemini AI**, **Python**, and **Gradio** to transform raw incident details into an actionable emergency command dashboard.

---

## 📌 Problem Statement

During disasters such as floods, earthquakes, tsunamis, cyclones, or mass-casualty incidents, responders often face a major challenge:

- information arrives in fragments,
- there is very little time to manually assess the scale of damage,
- hospitals may become overloaded,
- emergency teams must estimate resources quickly,
- and command decisions need to be made under pressure.

Traditional emergency workflows can be slow because teams must manually analyze:
- severity of the incident,
- number of people affected,
- medical urgency,
- hospital bed requirements,
- doctor/nurse deployment,
- field response planning,
- and operational priorities.

This delay can directly affect rescue speed, medical response quality, and coordination efficiency.

---

## 💡 Solution Overview

**ResQAI** solves this problem by acting as an **AI Emergency Command Center**.

The user enters key incident details such as:
- **Location**
- **Disaster Type**
- **People Affected**
- **Medical Situation**

Using these inputs, ResQAI generates a structured emergency response analysis, including:

- **Incident severity / risk classification**
- **Resource estimation**
- **Hospital capacity and triage planning**
- **Medical operations guidance**
- **Weather-aware situational intelligence**
- **Strategic response plan**
- **Complete emergency report**

This helps responders and decision-makers move from **raw incident data → actionable emergency plan** in a faster and more organized way.

---

## ✨ Key Features

### 1) Incident Intake
ResQAI accepts core emergency details:
- disaster location
- disaster type
- estimated affected population
- medical condition summary

### 2) AI Risk Assessment
The system analyzes the emergency and labels its urgency level, such as:
- High Risk
- Immediate response required

### 3) Resource Command Center
ResQAI estimates required field resources such as:
- field doctors
- field nurses
- ambulances
- relief tents
- drinking water
- food packets

### 4) Hospital Capacity & Triage Planning
The app estimates:
- critical, moderate, and minor patients
- ICU beds needed
- general beds needed
- total hospital load
- trauma doctors and hospital nurses needed
- whether a field hospital may be required

### 5) Incident Assessment
The platform generates a structured natural-language summary of the emergency and highlights the seriousness of the event.

### 6) Weather Intelligence
ResQAI adds environmental context and disaster-related situational awareness to help teams understand conditions that may affect rescue and logistics.

### 7) Medical Operations Guidance
The app recommends medical response priorities and treatment planning considerations for emergency teams.

### 8) Strategic Response Plan
It generates a step-by-step operational plan for command teams, including rescue, triage, evacuation, coordination, and supply deployment priorities.

### 9) Complete Emergency Report
All outputs are consolidated into a single structured emergency report for quick command review.

---

## 🏗️ System Architecture
### 1. Input Layer
The user enters:
- location
- disaster type
- people affected
- medical situation
### 2. Validation Layer
The system checks whether the inputs are complete and usable for analysis.
### 3. AI Intelligence Layer
The core AI engine interprets the emergency context and produces a structured response using prompt-based reasoning.
### 4. Risk & Incident Analysis Layer
This layer determines the seriousness of the event and generates an incident summary.
### 5. Resource Planning Layer
This module estimates operational needs such as:
ambulances
- field doctors
- field nurses
- tents
- food
- water
6. Hospital Capacity & Triage Layer
This module predicts:
- patient severity distribution
- ICU/general bed requirements
- overload risk
- need for field hospital support
7. Medical & Strategic Response Layer
This layer converts the emergency into practical actions by generating:
- medical operations recommendations
- response priorities
- deployment strategy
- command response plan
8. Reporting Layer
All outputs are displayed inside the command center dashboard as a complete emergency report.
### High-Level Workflow

```text
User Inputs Incident Details
        ↓
Input Validation Layer
        ↓
AI Emergency Analysis Engine
        ↓
Risk Assessment + Incident Interpretation
        ↓
Resource Estimation Engine
        ↓
Hospital Capacity & Triage Estimation
        ↓
Weather / Situation Intelligence
        ↓
Medical Operations Planning
        ↓
Strategic Response Plan Generation
        ↓
Final Emergency Report Dashboard

```
🛠️Tech Stack
1)Python
2)Gradio – frontend / interactive dashboard UI
3)Google Gemini AI – emergency reasoning and report generation
4)Hugging Face Spaces – deployment and hosting
5)Prompt engineering / structured AI output generation

---

## How to Run Locally
### 1)Clone this repository:
git clone https://github.com/YOUR-USERNAME/resqai-emergency-command-center.git
### 2)Move into the project folder:
cd resqai-emergency-command-center
### 3)Install dependencies:
pip install -r requirements.txt
### 4)Run the app:
python app.py

---

🎯 Use Cases
ResQAI can be useful for:
- disaster response simulation
- emergency command center prototypes
- hospital surge planning support
- triage planning demonstrations
- hackathons and capstone projects focused on public safety
- AI-assisted crisis management workflows

---

## 🔮 Future Improvements
Possible future upgrades include:
- real-time weather API integration
- GIS / map-based incident visualization
- multi-hospital live capacity integration
- SMS / alert dispatch system
- PDF emergency report export
- multilingual emergency support
- historical disaster pattern analysis
- role-based dashboards for doctors, hospitals, and field responders

---

## 🌍 Live Demo
### Hugging Face Space
https://huggingface.co/spaces/Ariyan05/resqai-emergency-command-center

---

## 👨‍💻 Author
Ashfaque Ahamed Khan
