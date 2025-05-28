# E-RATAS: A Scalable Framework for Automated Textual Exam Scoring

E-RATAS (Enhanced Rubric-Aware Tree-based Automated Scoring) is a scalable, interpretable, and modular framework for automatic grading of textual exam responses, including both **short and long-form open-ended answers**. It addresses the challenges of complex, structured rubrics and diverse response types using contextualized tree structures and LLM-based reasoning.

---

## 📦 Repository Structure

E-RATAS/
│
├── ACT/ # ACT construction engine
├── RKT/ # RKT construction engine
├── Matching_Scoring/ # Score and Reasoning modules
└── README.md # Project overview and setup instructions


---

## 🔍 What is E-RATAS?

E-RATAS transforms the automatic scoring of textual answers by introducing two contextual trees:
- **ACT (Answer Content Tree):** Represents the structure and semantics of student answers.
- **RKT (Rubric Knowledge Tree):** Represents structured rubrics with nested, semantically-aware rules.

Each node in ACT and RKT includes generated metadata (e.g., summaries, goals, influence scores), enabling fine-grained matching and scoring through transformer-based NLP models and generative LLMs.

![Architecture](https://github.com/datalab912/E-RATAS/assets/your_architecture_image.png)

---

## ⚙️ Core Modules

[Final-HLA.pdf](https://github.com/user-attachments/files/20491212/Final-HLA.pdf)

### 1. ACT Constructor (`/ACT`)
Builds the Answer Content Tree by:
- Extracting document structure (ToC or heading-based)
- Generating summaries (`ASG`) and goals (`CGD`)
- Organizing sections, subsections, paragraphs


### 2. RKT Constructor (`/RKT`)
Builds a hierarchical tree from the rubric by:
- Decomposing criteria into atomic components (`CTM`, `CRE`)
- Assigning metadata like scoring weights and section links

### 3. Matching & Scoring (`/Content_Criteria_Matching`, `/Matching_Scoring`)
- Computes semantic match scores using Sentence-BERT and GPT
- Assigns scores and interpretable reasons for each rubric–answer pair
- Aggregates to final score and justification

---
![Conseptual Model](https://github.com/user-attachments/assets/848e90a3-1de2-4fd3-8ca2-21ea90facc6d)

## 📐 Key Features

- ✔️ Handles **long, complex answers** up to 7000+ words
- ✔️ Supports advanced rubric types: `AND`, `OR`, `WHOLE`, `ESSENTIAL`, `COMPOSITE`
- ✔️ Integrates **LLMs** (e.g., GPT-4o, Pegasus, SBERT, LLaMA) through a flexible gateway
- ✔️ Implements **modular microservices** for each scoring engine
- ✔️ Produces **interpretable feedback** and hierarchical reasoning

---

## 🚀 Quick Start

> Prerequisites:
- Python 3.8+
- `requirements.txt` (coming soon)
- Access to your own GPT/OpenAI keys (if using LLMs)

```bash
# Clone the repo
git clone https://github.com/datalab912/E-RATAS.git
cd E-RATAS

# Create virtual environment
python -m venv env
source env/bin/activate  # or .\env\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run the system (example CLI or orchestrator endpoint to be added)


