# Supplementary Materials: Multi-Model BI for Institutional Reporting

**Author:** Valentin Schnabl  
**Institution:** TU Wien  
**Thesis Title:** Multi-Model Business Intelligence Exploration for Monitoring and Improving Institutional Reporting  
**Year:** 2026

## Overview
This repository serves as the digital appendix for the Master's Thesis listed above. It acts as a transparency log and storage for supplementary artifacts that support the research methodology, specifically regarding the optimization of the **ReposiTUm** data acquisition workflow.

## Contents

### 1. AI Usage Documentation & Prompt Logs
In accordance with the *Declaration on the Use of Generative AI* included in the thesis, this section provides a transparent record of how AI tools (Gemini, DeepL, TU Wien Internal AI) were utilized.
* **Prompt_Log.md**: A log of prompts used for linguistic refinement, structural transitions, and concept exploration.

### 2. Empirical Data Extraction (SQL)
This section contains the Oracle SQL scripts used to mine the ReposiTUm persistence layer for workflow metrics.
* **sql_scripts.md**: Scripts to calculate inter-departmental latency and user rework durations & 
Logic used to quantify the "Hidden Factory" by mapping rejections to specific workflow steps (FIS, Library, Faculty).

### 3. Workflow Simulation & Results

This section contains the dynamic validation models and their visual outputs, demonstrating the active touch-time reductions of the proposed TO-BE architectures.
* **simulation.py**: The Python script executing the 10,000-trial Monte Carlo simulation to evaluate active human administrative effort across the AS-IS baseline and the proposed workflow packages.
* **simulation_results.pdf**: A composite visualization of the simulation trials, featuring density distributions, a notched box plot, and a Cumulative Distribution Function (CDF).
* **labor_composition_stacked_bar.pdf**: A stacked bar chart illustrating the structural shift in labor composition, explicitly detailing the breakdown between Researcher Entry Time and Validator Review Time across the tested models.


## Disclaimer
All core intellectual content, analytical findings, and research contributions in the associated thesis are the original work of the author. The AI logs provided here are for reproducibility and transparency purposes only, demonstrating the "Human-in-the-Loop" verification process.

## Contact
* **Valentin Schnabl**
* **Advisor:** Ao. Univ. Prof. Dipl.-Ing. Dr.techn. Stefan Biffl
