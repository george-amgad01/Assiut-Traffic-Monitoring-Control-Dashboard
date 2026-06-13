<img width="2314" height="2184" alt="diagram-export-6-13-2026-12_24_06-AM" src="https://github.com/user-attachments/assets/1b2b788e-d96f-41e8-b7e9-21f10d597c1a" />


Assiut Traffic Monitoring & Control Dashboard

An interactive real-time traffic monitoring and visualization platform developed for the Assiut Traffic Management System.

The dashboard was designed to bridge the gap between traffic simulation, artificial intelligence, and operational decision-making by transforming raw traffic data into actionable insights. 

🏆 Developed as part of the IEEE 1st Place Winning Assiut Traffic Management System.

---

# Overview

Managing a city-scale traffic network requires more than optimizing traffic signals. Traffic operators need visibility into network conditions, intersection performance, congestion hotspots, environmental impact, and the behavior of intelligent control systems.

To address this challenge, the dashboard was developed as a real-time monitoring and analytics platform capable of displaying live traffic conditions across nine major signalized intersections in Assiut Governorate.

The platform combines simulation data, reinforcement learning outputs, network analytics, and interactive visualizations into a single operational interface.

---

# Dashboard Objectives

The dashboard was built with five primary objectives:

### 1. Network-Level Awareness

Provide traffic operators with a high-level view of overall network performance.

### 2. Intersection-Level Monitoring

Allow detailed inspection of every signalized intersection individually.

### 3. Congestion Identification

Instantly identify bottlenecks and high-pressure traffic areas.

### 4. AI Decision Monitoring

Track how the traffic control system behaves and evaluate its effectiveness.

### 5. Data Analysis & Explainability

Store operational data for future analysis, model evaluation, and decision interpretation.

---

# System Architecture

The dashboard follows a layered architecture separating data generation, processing, communication, and visualization.

Traffic Simulation & AI Engine
↓
Data Collection Layer
↓
Worker Thread
↓
PyQt Signal-Slot Communication
↓
Window Controller
↓
HTML/JavaScript Visualization
↓
Interactive Dashboard

This design enables real-time updates while maintaining a responsive user interface.

---

# Core Components

### main.py

Entry point of the dashboard that initializes the PyQt application, loads runtime configurations, creates the main interface, and launches background simulation processes.

### worker.py

Backend processing layer responsible for running traffic simulation and AI computations in a dedicated `QThread`. It collects real-time traffic metrics, vehicle positions, and intersection statistics, then streams structured JSON updates to the dashboard without blocking the user interface.

### window.py

Controller layer that bridges the backend and frontend. It receives live updates through PyQt signal-slot communication and synchronizes dashboard components by forwarding data to the visualization layer.

### assiut_map.html

Frontend visualization layer built with HTML, CSS, JavaScript, Leaflet.js, and OpenStreetMap. It renders the traffic network, intersection analytics, congestion heat maps, vehicle movements, charts, and real-time performance indicators.
---

# Dashboard Hierarchy

The dashboard follows a hierarchical monitoring approach.

## Level 1 — Network Performance

Provides an overview of the entire traffic network.

Metrics include:

* Network Efficiency Score (NES)
* Average Delay
* Average Queue Length
* Average Waiting Time
* Total Reward
* Sustainability Indicators

This level helps operators evaluate overall network health.

---

## Level 2 — Intersection Performance

Displays detailed metrics for each intersection.

Metrics include:

* Queue Length
* Waiting Time
* Delay
* Throughput
* Average Speed
* CO₂ Emissions
* Current Signal Phase
* Emergency Vehicle Status

This layer enables localized traffic analysis.

---

## Level 3 — Live Ranking

Intersections are ranked dynamically according to performance.

The ranking system helps identify:

* Best performing intersections
* Worst performing intersections
* Potential bottlenecks

This allows operators to quickly focus on problematic areas.

---

## Level 4 — Heat Map

A visual congestion layer showing traffic intensity.

Heat maps provide:

* Instant congestion awareness
* Network pressure visualization
* Traffic hotspot identification

The intensity and radius of each heat region correspond to traffic conditions.

---

## Level 5 — Episode Summary & Analytics

Provides historical performance information.

Includes:

* Reward Trends
* Episode Statistics
* Training Progress
* Performance History

This layer supports long-term evaluation of the traffic control strategy.

---

# Real-Time Vehicle Visualization

The dashboard visualizes moving vehicles directly on the road network.

Each vehicle contains:

* Position
* Speed
* Direction
* Vehicle Type

This creates a realistic operational view of network activity.

---

# Emergency Vehicle Monitoring

Emergency vehicles are highlighted separately from normal traffic.

The dashboard allows operators to monitor:

* Emergency vehicle presence
* Traffic signal priority behavior
* Intersection response

This feature supports future emergency traffic management strategies.

---

# Sustainability Monitoring

Beyond congestion metrics, the dashboard includes environmental indicators.

Metrics include:

* CO₂ Emissions
* Traffic Efficiency
* Sustainability Scores

These indicators help evaluate the environmental impact of traffic control decisions.

---

# Data Export & Post Analysis

The dashboard supports exporting operational data into CSV files.

Exported data includes:

* Simulation Steps
* Intersection States
* Queue Lengths
* Delays
* Waiting Times
* Signal Phases
* Network Efficiency Scores
* Agent Decisions

These datasets can be used for:

* Performance Evaluation
* Statistical Analysis
* Explainable AI Research
* Traffic Pattern Discovery
* Decision Interpretation

The goal is to transform traffic control from a black-box system into an explainable and analyzable platform.

---

# Technologies Used

Backend

* Python
* PyQt5
* QThread
* TraCI

Frontend

* HTML
* CSS
* JavaScript
* Leaflet.js
* OpenStreetMap

Visualization

* Interactive Maps
* Heat Maps
* Ranking Systems
* KPI Monitoring
* Analytics Panels

Data Processing

* JSON Streaming
* CSV Export
* Performance Logging

---

# Screenshots
<img width="1916" height="960" alt="Screenshot 2026-06-07 203803" src="https://github.com/user-attachments/assets/ab140ecf-99f5-4fad-a51c-ee60a6e13e1a" />
<img width="352" height="281" alt="Screenshot 2026-06-07 210808" src="https://github.com/user-attachments/assets/70fd7840-c0e0-4c39-8735-21440abee3fb" />
<img width="1016" height="538" alt="Screenshot 2026-06-07 2043621" src="https://github.com/user-attachments/assets/31ad6932-a3f1-4254-aa0b-acd0809d1f62" />
<img width="426" height="449" alt="Screenshot 2026-06-07 213552" src="https://github.com/user-attachments/assets/8bc6e384-9eb6-43b0-b45b-423b32a07a61" />
<img width="354" height="213" alt="Screenshot 2026-06-07 204709" src="https://github.com/user-attachments/assets/38e1bad4-1db5-4508-821e-c93669390d00" />
<img width="1554" height="905" alt="Screenshot 2026-06-07 204621" src="https://github.com/user-attachments/assets/5df174a4-a6d7-481d-a2ae-e969bffe7a80" />
<img width="1139" height="948" alt="Screenshot 2026-06-07 212810" src="https://github.com/user-attachments/assets/46ca3557-0a6a-4a46-aca4-659bb5c0a552" />

# Demo Video
https://youtu.be/ED-FFY5QcNU?si=k-QB7oSDbM7Yhd4N

# Architecture Diagram
<img width="2775" height="1528" alt="diagram-export-6-12-2026-8_23_44-PM" src="https://github.com/user-attachments/assets/5b3620ce-4ca9-474a-86ea-1208ebb044c8" />
