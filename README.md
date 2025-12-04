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
![image](https://github.com/user-attachments/assets/69389c72-3b4a-4aa2-8e16-a4ad91e3c948)



---



## ⚙️ Core Modules



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





# E-RATAS Downstream Component Responsibilities

The E-RATAS framework employs a set of tightly integrated Downstream Tasks (DNTs) that collectively operationalize rubric-aware reasoning, knowledge construction, and automated scoring. Each DNT module contributes a distinct functional capability, while also enabling and depending on the others. Because these modules are mutually interdependent, none of them can be removed or ablated without collapsing essential functionality or breaking rubric alignment.

E-RATAS is intentionally designed as a modular, agentic architecture rather than a single end-to-end function. Each DNT behaves as a specialized “agent” with a clear contract: some agents construct and refine the rubric knowledge (CSC, CTM, CRE), others build rich representations of student answers (CGD, ASE, ASG), and others perform alignment and scoring (SSM, SSR). This decomposition allows us to explicitly encode rubric structure, support subject-agnostic deployment, apply different model families and inference strategies per module, and monitor intermediate states (e.g., topics, relationships, content goals) for debugging, evaluation, and human-in-the-loop quality control. It also enables better job/token management, parallel execution, and incremental upgrades of individual components without retraining the entire system.

If E-RATAS were implemented as a single monolithic end-to-end model, many of these advantages would be lost. Rubric structures, sub-conditions, relationships, and answer abstractions would be implicitly entangled inside a black-box representation, making it difficult to guarantee rubric coverage, enforce consistency across criteria, or adapt to new exams and rubrics without full retraining. We would also lose the ability to inspect intermediate reasoning, conduct targeted error analysis, reuse modules across subjects, or independently improve specific capabilities (e.g., better topic modeling or relationship extraction) while keeping others fixed. For these reasons, the modular agentic design is not just an engineering preference, but a technical requirement to achieve scalable, explainable, and rubric-faithful automatic scoring.

Below is a detailed description of the role and responsibility of each downstream module.

## 1. SR-based Scoring and Reasoning (SSR)

The SSR module produces the final scoring decisions by reasoning over rubric-aligned semantic structures. It interprets the student response through representations created by ACT and RKT, evaluating the degree to which content goals, sub-conditions, and rubric relationships are satisfied. SSR generates both numerical scores and reasoning chains that justify those scores, enhancing transparency, explainability, and instructional value.

SSR depends on all upstream modules—including SSM, CGD, ASE, ASG, CSC, CTM, and CRE—to provide structured rubric knowledge and organized answer representation. Without these signals, SSR would be forced to operate on raw text, making rubric-aligned reasoning impossible. Therefore, SSR cannot be removed or ablated, as it is the central scoring mechanism of E-RATAS.

## 2. SR and SC Matching (SSM)

The SSM module aligns extracted student response content (SR) with rubric sub-conditions (SC). It performs fine-grained semantic matching, determining whether the student has fully, partially, or not at all satisfied each rubric requirement. SSM enables detailed coverage analysis and supports criterion-level scoring and feedback generation.

SSM relies on CSC for sub-condition types, CTM for thematic clusters, CRE for relationship structure, and CGD/ASE/ASG for structured answer representations. If SSM is removed, SSR loses its alignment layer and becomes unable to map answer evidence to rubric expectations. Thus, SSM is essential and cannot be ablated without invalidating rubric-aware scoring.

## 3. Criteria Sub-condition Classification (CSC)

The CSC module transforms rubric text into structured units by classifying each rubric component into its sub-condition type. CSC helps the system distinguish between content requirements, structural requirements, reasoning expectations, constraints, and supporting details. This classification provides the foundation for constructing the RKT.

CSC is deeply interconnected with CTM, CRE, SSM, and SSR. CTM uses CSC to group SCs into conceptual themes, CRE uses CSC categories to extract relationships, and SSM relies on CSC types for proper alignment of student content. Removing CSC breaks the RKT construction pipeline, making CSR non-removable and non-ablatable.

## 4. Criteria Topic Modeling (CTM)

The CTM module identifies conceptual themes among criteria and sub-conditions, grouping related rubric components using topic models and embedding-based clustering. This reveals the latent structure of complex rubrics, improving interpretability and supporting holistic reasoning across related concepts.

CTM depends on CSC for normalized SC categories and informs CRE and SSM by providing topic-level organization. Without CTM, rubric elements become isolated, eliminating thematic grouping and degrading scoring stability. CTM provides functionality not replicated elsewhere in the architecture; therefore, CTM cannot be removed or ablated.

## 5. Criteria Relationship Extraction (CRE)

The CRE module extracts logical, hierarchical, sequential, and causal relationships between rubric elements. These relationships form the backbone of the RKT, enabling structured reasoning and representing rubrics as interconnected knowledge graphs rather than flat lists.

CRE relies on CSC and CTM and directly supports both SSM and SSR. Relationship information is essential for evaluating coherence, prerequisite satisfaction, and reasoning quality in student answers. Removing CRE collapses the RKT structure and disrupts the entire scoring pipeline. Thus, CRE is essential and cannot be ablated.

## 6. Content Goal Detection (CGD)

The CGD module identifies the primary semantic units—content goals—within a student response. It extracts key ideas that correspond to rubric expectations, allowing the system to operate on clear, distilled meaning rather than raw, verbose text. CGD provides robustness to paraphrasing, irrelevance, and stylistic variation.

CGD works closely with ASE and ASG as part of the ACT construction process, and its outputs feed into SSM and SSR. Without CGD, the system cannot reliably identify the relevant information in long answers, breaking alignment and scoring. Therefore, CGD is non-optional and cannot be ablated.

## 7. Answer Structure Extraction (ASE)

The ASE module analyzes the organization and logical flow of the student answer. It identifies structural elements such as sequencing, argument flow, evidence placement, and decomposition into sub-parts. ASE maps these into the ACT representation, enabling structural scoring and reasoning.

ASE depends on CGD and contributes to ASG, SSM, and SSR. Without ASE, E-RATAS loses the ability to evaluate coherence, organization, and multi-part alignment—critical for many real-world rubrics. Ablating ASE would collapse the ACT pipeline, making ASE essential and non-removable.

## 8. Abstractive Summary Generation (ASG)

The ASG module produces multi-level abstractive summaries of student answers. These summaries compress long responses into hierarchical representations of key content, improving clarity, robustness, and alignment with rubric structures. ASG helps normalize verbosity, reduce noise, and create consistent inputs for downstream modules.

ASG relies on CGD and ASE and supports SSM and SSR by providing distilled semantic representations. Without ASG, the system must process raw text directly, reducing accuracy and stability in rubric alignment. Thus, ASG is a required component and cannot be ablated.

Interdependence of All DNT Modules

All DNT modules—SSR, SSM, CSC, CTM, CRE, CGD, ASE, ASG—are mutually dependent and collectively form the complete E-RATAS reasoning and scoring pipeline. Each module executes a unique role that is not reproducible by any other part of the system. Removing or ablating any module breaks essential representations, disrupts rubric alignment, and invalidates the scoring process.
E-RATAS is therefore designed as a modular yet interdependent architecture, where the full scoring and reasoning capability emerges from the coordination of all downstream components.

# Dataset Description and Samples
## Dataset Creation Process

To evaluate E-RATAS in realistic educational settings, we constructed a high-fidelity dataset grounded in project-based, graduate-level coursework, where students produce long, unrestricted, text-based answers. Unlike typical short-answer datasets, these responses frequently span multiple pages, contain heterogeneous structures, and incorporate diverse writing styles. The associated rubrics are rich, multi-layered, and representative of real-world scoring practices, including detailed sub-conditions, hierarchical criteria, mixed scoring rules (additive, conditional, prerequisite-based), and explicit expectations on structure, reasoning, evidence, and content coverage. This complexity makes the dataset an ideal benchmark for testing rubric-aware systems such as E-RATAS.

The motivation behind creating this dataset stems from a gap in existing public corpora, which generally contain either short responses, simplified rubrics, or constrained question formats. Our dataset captures realistic diversity in answer quality, depth, coherence, and organization, along with rubrics that demonstrate authentic combinations of structural requirements, content goals, and interdependent scoring rules. This provides a rigorous environment for evaluating downstream tasks such as CGD, ASE, ASG, CSC, CTM, CRE, SSM, and SSR, and reflects the operational challenges faced in automated scoring systems for non-STEM, open-ended assessments.

We reviewed and analyzed four consecutive semesters of student submissions. Two independent human graders evaluated the reports, and only responses with validated, agreement-based scores were included in the dataset. From this validated pool, we selected samples that maximize diversity in length, complexity, organization, and overall quality, ensuring that E-RATAS is tested across the full spectrum of student performance—from minimal responses to highly detailed, multi-page narratives.

The final dataset consists of two distinct subsets:

- Midterm Response Set (12 to ~2,000 words)
Short-to-medium length responses drawn from students’ midterm project reports. These samples include partial reasoning, incomplete structures, varied writing quality, and uneven coverage—ideal for evaluating E-RATAS modules under typical assessment conditions.

- Long-form Final Report Set (~2,000 to 7,000 words)
Extended, high-detail responses taken from final project submissions. These rich documents include sectioned structures, multi-step argumentation, evidence integration, and complex narrative flow—critical for evaluating ACT construction (CGD, ASE, ASG) and deep RKT alignment (CSC, CTM, CRE).

Importantly, no part of the dataset was ever used in prompt design, fine-tuning, module engineering, or template creation for the downstream tasks. All DNT prompts, architectures, and design decisions were developed independently of the dataset to prevent leakage and ensure objective evaluation.

## Sample Dataset Inputs

Below are references to the sample data structures included in the repository:

**Sample Rubric (RKT Construction Input):**
RKT/Input

**Sample Student Answer (ACT Construction Input):**
ACT/src/input
(contains example answers used to generate ACT trees via CGD, ASE, and ASG)

These samples illustrate the formatting conventions and data structures expected by the E-RATAS pipelines, and can be used for initial testing or replication of model behaviors across DNT modules.


# Sample Engine Output JSONs

This repository includes several example outputs generated by the E-RATAS engines, providing concrete illustrations of how ACT trees, RKT structures, and scoring/feedback outcomes are represented in machine-readable formats. These samples help developers, researchers, and evaluators understand the internal data flow between modules and verify the behavior of each downstream task (DNT).

- **Sample ACT Tree (Generated by the ACT Engine)**
Located at:
ACT/src/ACT/src/output
These files demonstrate how the system performs Content Goal Detection (CGD), Answer Structure Extraction (ASE), and Abstractive Summary Generation (ASG) to construct a hierarchical ACT representation. The ACT JSON contains nodes, semantic goals, relationships, summaries, and structural metadata used by downstream scoring tasks.

- **Sample ACT + RKT JSON Inputs for the Scoring & Reasoning Engine**
Located at:
Matching_Scoring/input_data
and
Matching_Scoring/input_ReflectiveJournalSample
These examples show how the ACT and RKT engines jointly prepare structured knowledge—criteria, sub-conditions, topics, relationships, content goals, and summaries—which the scoring engine (SSR + SSM) uses for rubric-aligned evaluation. These files serve as the expected input schema for the full Scoring & Reasoning pipeline.

- These samples collectively illustrate how each engine transforms unstructured text into structured intermediate representations, enabling explainable end-to-end scoring.

#Prompting
## Prompt Engineering Workflow

The E-RATAS system is built using a rigorous, modular, and data-independent prompting methodology. Prompt design follows a structured workflow that ensures reliability, generalizability, and strict separation between evaluation data and prompt engineering efforts:

1. Chain-of-Thought–Driven Specification
For all DNT modules, prompts are designed to elicit step-by-step reasoning, controlled decomposition, rule interpretation, and structured extraction. Each module uses a tailored Chain of Thought (CoT), aligned with its specific functionality (e.g., topic modeling, relationship extraction, structural parsing, content-goal detection, scoring).

2. Hierarchical Command and Instruction Design
Prompts follow a standardized "Command → Rules → Structure → Output Contract" design.
This ensures predictable JSON outputs, retry robustness, and consistent formatting across hundreds of rubric elements and thousands of answer variations.

3. Few-Shot Examples Using External Course Materials
To avoid contamination or leakage into evaluation, all few-shot examples used during prompt development come exclusively from unrelated STEM courses, not from the project-based dataset used for E-RATAS testing.
No content, structure, rubric elements, or answer segments from the evaluation dataset were ever used during prompt crafting.

4. Crowdsourced Iterative Improvement
Prompts were refined through iterative testing across:
– multiple reviewers,
– diverse answer styles,
– synthetic edge cases,
– complex rubric interactions.
This process ensures robustness to ambiguous, incomplete, or excessively long responses.

5. Strict Data Separation Policy
At no point was any real student data or rubric element from the evaluation set used to iterate, enhance, or optimize prompts for any DNT module.

This methodology ensures fairness, generalizability, and scientific rigor in evaluating downstream tasks and the complete E-RATAS pipeline.

# Sample Prompts

The repository provides sample prompts for all major engines used in E-RATAS. These examples illustrate prompt structure, output formatting, and module-specific reasoning workflows.

**1. Direct GPT Scoring Prompt**

Matching_Scoring/direct_scoring_AssisstantCreation.py
A baseline prompt for direct end-to-end GPT scoring, provided for comparison against the full modular E-RATAS pipeline.

**2. ACT Engine Prompts**

Main ACT assistant:
ACT/src/ACT/src/assisstant.py

Topic modeling for ACT construction:
ACT/src/ACT/src/topic_modeling/assisstant.py
These prompts guide CGD, ASE, and ASG to build the ACT tree and extract structural representations.

**3. Scoring Engine Prompts (SSR + SSM)**

Located in:
Matching_Scoring/GPT_assissatnt/*
and
Matching_Scoring/Final_Score_01AssisstantCreation.py
Matching_Scoring/Score_01AssisstantCreation.py
Matching_Scoring/Score_100AssisstantCreation.py
These prompts implement rubric-aware semantic matching, reasoning, and scoring logic based on ACT + RKT inputs.

**4. RKT Engine Prompts**

Title generation assistant:
RKT/Final_TitleGenerationAssisstantCreation.py

Topic modeling and rubric clustering assistant:
RKT/FinalTopicModelingAssisstantCreation.py
These prompts are responsible for constructing the full RKT: CSC, CTM, and CRE outputs.

# Sample Structural Feedback Outputs and sxcoring reasoing output

E-RATAS generates detailed, structured feedback for each student response, including hierarchical scoring traces, rubric-aligned reasoning chains, and structural quality analysis.

## Sample JSON Outputs (Real-World Student Responses)

Scoring and reasoning sample outputs:
Matching_Scoring/output_2

Reflective journal scoring sample:
Matching_Scoring/output_ReflectiveJournal_light

These JSON files contain:

matched rubric sub-conditions,

coverage analysis,

reasoning explanations,

score breakdowns,

structural and content-goal insights,

ACT-referenced feedback components.

They serve as examples of how E-RATAS produces transparent, interpretable evaluation artifacts.

## Structural Feedback Image Examples

<img width="815" height="1349" alt="RKT design22 (1)" src="https://github.com/user-attachments/assets/79b785e1-8446-4766-937a-0e9ff7002bf6" />


<img width="679" height="848" alt="RKT design23232343 (1)" src="https://github.com/user-attachments/assets/32745527-1b04-410b-b9e0-bc6b8f4c0e1c" />

<img width="1882" height="1168" alt="Scoring Analysis (1)" src="https://github.com/user-attachments/assets/1ae2a7fa-1d9b-4fe2-ab2d-949b04e9fc54" />




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
