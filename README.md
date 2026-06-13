<img width="2314" height="2184" alt="diagram-export-6-13-2026-12_24_06-AM" src="https://github.com/user-attachments/assets/1b2b788e-d96f-41e8-b7e9-21f10d597c1a" />


# 🚦 Assiut Traffic Monitoring, Control & Decision Analysis Dashboard

An interactive real-time traffic monitoring, visualization, and decision analysis platform developed for the Assiut Traffic Management System.

The platform was designed to bridge the gap between traffic simulation, artificial intelligence, and operational decision-making by transforming raw traffic data into actionable insights. Beyond real-time monitoring, the system introduces an explainability and post-analysis framework capable of evaluating AI traffic control decisions and identifying opportunities for performance improvement.

🏆 Developed as part of the IEEE 1st Place Winning Assiut Traffic Management System.

---

# Demo Video

https://youtu.be/ED-FFY5QcNU?si=k-QB7oSDbM7Yhd4N

---

# Overview

Managing a city-scale traffic network requires more than optimizing traffic signals. Traffic operators need visibility into network conditions, intersection performance, congestion hotspots, environmental impact, and the behavior of intelligent traffic control systems.

To address this challenge, the platform was developed as a real-time monitoring and analytics environment capable of displaying live traffic conditions across nine major signalized intersections in Assiut Governorate while simultaneously analyzing the decisions made by Multi-Agent Reinforcement Learning agents.

The system combines traffic simulation, AI-driven control, operational analytics, explainability tools, and interactive visualizations into a unified decision-support platform.

---

# Dashboard Objectives

The platform was built around five primary objectives:

### 1. Network-Level Awareness

Provide traffic operators with a high-level view of overall network performance and traffic efficiency.

### 2. Intersection-Level Monitoring

Allow detailed inspection of every signalized intersection individually.

### 3. Congestion Identification

Instantly identify bottlenecks, congestion hotspots, and high-pressure traffic areas.

### 4. AI Decision Monitoring

Track how the traffic control system behaves, monitor selected signal phases, and evaluate their impact on traffic conditions.

### 5. Explainability & Continuous Improvement

Transform traffic control from a black-box AI system into an explainable and analyzable framework capable of identifying mistakes, understanding agent behavior, and improving future decision-making.

---

# System Architecture

The platform follows a layered architecture separating simulation, intelligence, communication, visualization, and post-analysis.

Traffic Simulation (SUMO)
↓
Multi-Agent Control System (MAPPO)
↓
Data Collection Layer
↓
Worker Thread
↓
PyQt Signal-Slot Communication
↓
Visualization Dashboard
↓
CSV Export & Analytics
↓
Agent Decision Analyzer

This architecture enables real-time monitoring while maintaining a responsive user interface and supporting advanced post-simulation analysis.

---

# Core Components

### main.py

Application entry point responsible for initializing the dashboard environment, loading runtime configurations, creating the main interface, and launching simulation workers.

### worker.py

Backend processing layer responsible for running traffic simulation and AI computations inside a dedicated `QThread`. It collects live traffic metrics, vehicle positions, intersection statistics, and agent outputs before streaming structured JSON updates to the dashboard.

### window.py

Controller layer that bridges backend services and frontend visualization components. It receives updates through PyQt signal-slot communication and synchronizes all dashboard elements in real time.

### assiut_map.html

Interactive visualization layer built with HTML, CSS, JavaScript, Leaflet.js, and OpenStreetMap. It renders maps, congestion heat maps, intersection analytics, vehicle movements, rankings, and operational KPIs.

### Agent Analyzer

Post-analysis and explainability module that evaluates MAPPO traffic signal decisions using exported CSV logs to understand why each phase was chosen and its impact on both local intersections and the whole network.

It also analyzes reward evolution, detects suboptimal actions, and identifies improvement opportunities to move from simple performance measurement to interpreting AI decision reasoning and consequences.

---

# Dashboard Hierarchy

The dashboard follows a hierarchical monitoring approach designed for traffic operators and researchers.

### Level 1 — Network Performance

Provides a network-wide overview using key indicators such as:

* Network Efficiency Score (NES)
* Average Delay
* Average Queue Length
* Average Waiting Time
* Cumulative Reward
* Sustainability Indicators

### Level 2 — Intersection Performance

Provides detailed metrics for each signalized intersection:

* Queue Length
* Waiting Time
* Delay
* Throughput
* Average Speed
* CO₂ Emissions
* Signal Phase Status
* Emergency Vehicle Detection

### Level 3 — Live Ranking

Dynamically ranks intersections according to operational performance, helping identify best-performing and problematic locations.

### Level 4 — Heat Map

Visualizes traffic pressure and congestion intensity across the network using a real-time heat layer.

### Level 5 — Episode Summary & Analytics

Provides historical insights including:

* Reward Trends
* Episode Statistics
* Training Progress
* Performance History

---

# Agent Decision Analysis

Post-analysis and explainability module that evaluates MAPPO traffic signal decisions using exported CSV logs to understand why each phase was chosen and its impact on both local intersections and the whole network.

It also analyzes reward evolution, detects suboptimal actions, and identifies improvement opportunities to move from simple performance measurement to interpreting AI decision reasoning and consequences.

The analysis pipeline follows:

Traffic State
↓
Selected Phase
↓
Traffic Outcome
↓
Performance Evaluation
↓
Decision Quality Assessment

---

# Data Export & Post Analysis

The platform supports exporting operational data into structured CSV files.

Exported datasets include:

* Simulation Steps
* Traffic States
* Queue Lengths
* Waiting Times
* Delays
* Throughput
* Signal Phases
* Agent Decisions
* Network Efficiency Scores
* Reward Values

These datasets can be used for:

* Performance Evaluation
* Statistical Analysis
* Traffic Pattern Discovery
* Explainable AI Research
* Decision Trace Analysis
* Future Machine Learning Models
* Agent Performance Improvement

---

# Technologies Used

### Backend

* Python
* PyQt5
* QThread
* TraCI
* JSON Streaming

### Frontend

* HTML
* CSS
* JavaScript
* Leaflet.js
* OpenStreetMap

### Traffic Simulation

* SUMO
* SUMO-GUI

### Artificial Intelligence

* Multi-Agent Reinforcement Learning (MAPPO)

### Analytics & Explainability

* CSV Export
* Decision Analysis
* Performance Evaluation
* Agent Explainability Pipeline
* Post-Simulation Analytics

---
# Screenshots
<img width="1916" height="960" alt="Screenshot 2026-06-07 203803" src="https://github.com/user-attachments/assets/ab140ecf-99f5-4fad-a51c-ee60a6e13e1a" />
<img width="352" height="281" alt="Screenshot 2026-06-07 210808" src="https://github.com/user-attachments/assets/70fd7840-c0e0-4c39-8735-21440abee3fb" />
<img width="1016" height="538" alt="Screenshot 2026-06-07 2043621" src="https://github.com/user-attachments/assets/31ad6932-a3f1-4254-aa0b-acd0809d1f62" />
<img width="426" height="449" alt="Screenshot 2026-06-07 213552" src="https://github.com/user-attachments/assets/8bc6e384-9eb6-43b0-b45b-423b32a07a61" />
<img width="354" height="213" alt="Screenshot 2026-06-07 204709" src="https://github.com/user-attachments/assets/38e1bad4-1db5-4508-821e-c93669390d00" />
<img width="1554" height="905" alt="Screenshot 2026-06-07 204621" src="https://github.com/user-attachments/assets/5df174a4-a6d7-481d-a2ae-e969bffe7a80" />
<img width="1139" height="948" alt="Screenshot 2026-06-07 212810" src="https://github.com/user-attachments/assets/46ca3557-0a6a-4a46-aca4-659bb5c0a552" />
