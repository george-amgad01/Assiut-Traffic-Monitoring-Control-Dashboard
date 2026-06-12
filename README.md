<img width="2775" height="1528" alt="diagram-export-6-12-2026-8_23_44-PM" src="https://github.com/user-attachments/assets/5b3620ce-4ca9-474a-86ea-1208ebb044c8" />


Assiut Traffic Monitoring & Control Dashboard

An interactive real-time traffic monitoring and visualization platform developed for the Assiut Traffic Management System.

The dashboard was designed to bridge the gap between traffic simulation, artificial intelligence, and operational decision-making by transforming raw traffic data into actionable insights. It provides a unified interface for monitoring the entire traffic network, analyzing individual intersections, visualizing congestion patterns, evaluating AI-driven traffic control decisions, and supporting post-simulation analysis.

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

## main.py

Acts as the application entry point.

Responsibilities:

* Initialize the PyQt application
* Configure runtime settings
* Create dashboard components
* Launch simulation workers
* Manage application lifecycle

The main file is responsible for bootstrapping the entire dashboard environment.

---

## worker.py

The worker serves as the backend processing layer.

Responsibilities:

* Execute traffic simulation processes
* Collect live traffic metrics
* Track vehicle positions
* Process intersection statistics
* Generate structured JSON payloads
* Stream updates to the dashboard

The worker operates inside a dedicated QThread to prevent the user interface from freezing during intensive simulation and AI computations.

Without this separation, the dashboard would become unresponsive while the traffic control system is running.

---

## window.py

Acts as the dashboard controller.

Responsibilities:

* Receive backend updates
* Handle signal-slot communication
* Synchronize frontend components
* Push updates to JavaScript
* Manage dashboard events

This layer acts as the communication bridge between Python and the web-based frontend.

---

## assiut_map.html

The visualization layer of the system.

Built using:

* HTML
* CSS
* JavaScript
* Leaflet.js
* OpenStreetMap

Responsibilities:

* Render traffic maps
* Display intersection information
* Visualize congestion
* Show vehicle movements
* Update charts and KPIs
* Present operational analytics

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

# Technical Challenges

One of the biggest engineering challenges was maintaining dashboard responsiveness while continuously processing traffic simulation and AI-generated data.

This challenge was solved through:

* PyQt5 QThread Architecture
* Asynchronous Processing
* Signal-Slot Communication
* JSON-Based Data Streaming

This architecture enables smooth real-time visualization without dashboard freezing.

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

# Future Enhancements

* Explainable AI Dashboard
* Traffic Forecasting
* Real-Time Camera Integration
* Predictive Congestion Analysis
* Emergency Vehicle Priority Control
* Smart City Control Center Integration

---

# Screenshots
<img width="1916" height="960" alt="Screenshot 2026-06-07 203803" src="https://github.com/user-attachments/assets/ab140ecf-99f5-4fad-a51c-ee60a6e13e1a" />
<img width="1554" height="905" alt="Screenshot 2026-06-07 204621" src="https://github.com/user-attachments/assets/5df174a4-a6d7-481d-a2ae-e969bffe7a80" />
<img width="1139" height="948" alt="Screenshot 2026-06-07 212810" src="https://github.com/user-attachments/assets/46ca3557-0a6a-4a46-aca4-659bb5c0a552" />

# Demo Video


# Architecture Diagram
<img width="2775" height="1528" alt="diagram-export-6-12-2026-8_23_44-PM" src="https://github.com/user-attachments/assets/5b3620ce-4ca9-474a-86ea-1208ebb044c8" />
