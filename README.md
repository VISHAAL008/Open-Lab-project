# GitHub Repository Analyzer

## Overview

GitHub Repository Analyzer is a web application built using Python and Streamlit that helps users evaluate GitHub repositories by analyzing repository activity, documentation, popularity, maintenance status, and overall project health.

The application fetches repository data using the GitHub API, calculates a repository quality score, generates insights, and provides recommendations to help developers make informed decisions when selecting open-source projects.

---

## Features

### Repository Analysis

* Repository overview and metadata
* Stars, forks, watchers, and open issues
* Creation and last update information
* Repository size and file count

### Activity Analysis

* Commit activity tracking
* Maintenance status evaluation
* Repository update frequency analysis

### Documentation Analysis

* README detection
* Documentation quality assessment
* Repository structure evaluation

### Repository Health Score

* Overall score out of 100
* Category-wise score breakdown
* Quality indicators and reasoning

### Language Analysis

* Programming language distribution
* Technology stack overview

### Recommendations Engine

* Repository improvement suggestions
* Risk and quality indicators
* Usage recommendations

### Export Options

* Download analysis results as JSON
* Download analysis report as PDF

---

## Technology Stack

### Frontend

* Streamlit

### Backend

* Python

### APIs

* GitHub REST API

### Libraries

* Requests
* Pandas
* Plotly
* FPDF
* Python-dotenv

---

## Project Workflow

1. User enters a GitHub repository URL.
2. The application fetches repository data using the GitHub API.
3. Repository metrics are analyzed.
4. A quality score is generated.
5. Insights and recommendations are created.
6. Results are displayed through an interactive dashboard.
7. Reports can be exported as JSON or PDF.

---

## Installation

### Clone Repository

```bash
git clone https://github.com/your-username/github-repository-analyzer.git
cd github-repository-analyzer
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure GitHub Token

Create a `.env` file in the project root:

```env
GITHUB_TOKEN=your_github_personal_access_token
```

### Run Application

```bash
streamlit run main.py
```

---

## Screenshots

Add screenshots of:

* Repository Search Page
* Analysis Dashboard
* Score Breakdown
* Export Report Feature

---

## Future Enhancements

* Repository Comparison Dashboard
* Contributor Insights
* Machine Learning Based Repository Evaluation
* GitLab Repository Support
* Advanced Trend Analysis
* AI-Powered Repository Summarization

---

## Learning Outcomes

This project helped in understanding:

* GitHub API Integration
* REST APIs
* Data Analysis
* Streamlit Development
* Report Generation
* Repository Evaluation Metrics
* Software Engineering Principles

---

## Live Demo

https://git-repo-analyzer-v2.streamlit.app/

---

## Author

**Vishaal J**

MCA Student | AI/ML Enthusiast | Python Developer
