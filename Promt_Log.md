# AI Prompt Documentation: Master's Thesis Quality Assurance

This document outlines the structured prompts used to guide AI tools (Gemini, NotebookLM, etc.) during the drafting and quality assurance phases of this thesis. All prompts were designed with strict constraints to ensure the author retained full intellectual ownership of the core arguments, methodologies, and findings.

> **Tool scope note:** Prompts marked *(General)* work with any capable LLM (Claude, Gemini, GPT-4, etc.). Prompts marked *(NotebookLM / Scholar Labs)* require an uploaded document corpus to function correctly — do not use them with a general LLM without providing the source documents explicitly.

---

## Part 1: Linguistic, Stylistic, and Formatting QA

### 1. Direct Linguistic Correction
**Role:** Software engineering researcher.
**Task:** Correct this text to make it proper thesis writing English.
**Constraints:**
* Retain the original technical meaning.
* Ensure the tone aligns with formal academic standards in software engineering.

**Text to review:**
[Insert Thesis Text Here]

---

### 2. Proofreading & Grammar (Surface-Level QA)
**Role:** Act as a strict academic copyeditor.
**Task:** Proofread the following text for spelling, grammar, and punctuation errors.
**Constraints:**
* Do NOT rewrite the sentences or alter my personal writing style.
* Do NOT add new information or change the meaning of the text.
* Output a list of suggested corrections, explaining the grammatical rule where necessary, so I can review them manually.

---

### 3. Clarity & Academic Tone (Stylistic QA)
**Role:** Act as a university writing center tutor.
**Task:** Review the provided paragraph for clarity, conciseness, and appropriate academic tone.
**Constraints:**
* Identify any sentences that are overly complex, passive, or difficult to read.
* Suggest 1–2 minor rephrasings for awkward sentences, but heavily favor my original vocabulary.
* If a specific technical term is used incorrectly in context, point it out.

---

### 4. Cross-Checking Translations & Terminology
**Role:** Expert bilingual (German/English) software engineering researcher.
**Task:** I have translated the following excerpt from a German source into English. Review the English translation to ensure that the specific technical terminology is standard in academic literature.
**Constraints:**
* Do not rewrite the paragraph unless the current translation is technically inaccurate.
* Specifically verify if the German term "[Insert German Term]" is best translated as "[Insert English Term]" in this specific context.

---

### 5. LaTeX Formatting and Debugging
**Role:** Expert LaTeX typesetter.
**Task:** Identify the compilation error in the following LaTeX code snippet.
**Constraints:**
* Fix ONLY the syntax/formatting error (e.g., missing brackets, incorrect table alignment).
* Do not alter any of the text, numbers, or data contained within the table/text block.
* Briefly explain what was causing the error so I can learn from it.

---

### 6. Stylistic Over-Reliance Check (Soft Plagiarism Detection)
**Task:** Analyze the following drafted section for stylistic over-reliance on generic academic phrasing.
**Constraints:**
* Flag any sentences that read like structural paraphrases of typical literature patterns rather than original synthesis.
* Identify overly repetitive sentence structures (e.g., starting too many sentences with "Furthermore" or "In addition").

---

## Part 2: Structural and Logical QA

### 7. Structural & Transitional Formulation
**Role:** Academic writing assistant.
**Task:** Formulate a transitional paragraph that bridges the end of Section [X] (focusing on [Topic A]) to the beginning of Section [Y] (focusing on [Topic B]).
**Constraints:**
* The output must be concise (maximum 2–3 sentences).
* Incorporate the following specific keywords where they arise naturally: "[Keyword 1]", "[Keyword 2]".
* Do not introduce any claim that is not already established in the preceding section. The transition serves only to connect the two topics — it must not advance any argument of its own.

---

### 8. Reverse-Outlining (Sanity Check)
**Task:** Create a brief, bulleted reverse-outline of the text provided below.
**Instructions:** For each paragraph, provide a single, one-sentence summary of its main argument to help me verify if the structural progression of my ideas is clear.

---

### 9. Structural Integrity Pass (Redundancy, Consistency & Tense)
**Task:** Review the following thesis chapter for informational density, macro-level consistency, and tense coherence. This is a combined structural pass covering three dimensions.
**Constraints:**
* **Redundancy:** Detect and flag repeated ideas or arguments across different paragraphs/sections. Identify unnecessary restatements or "filler" sentences that provide low informational value.
* **Terminology & notation:** Flag if the same core concept is referred to using different terms interchangeably. Ensure mathematical and software engineering notation remains strictly consistent.
* **Tense:** Flag any inconsistent verb tenses (e.g., accidentally mixing past and present tense when describing the methodology).
* Do not suggest rewrites — only flag and explain each issue so I can resolve it manually.

---

## Part 3: Deep Research and Argumentative QA

### 10. Research Logic, Flow & Argument Robustness (Combined Peer Review)
**Role:** Skeptical peer reviewer in software engineering.
**Task:** Analyze the logical flow, argumentation, and argumentative robustness of the following thesis subsection. This is a combined deep QA pass.
**Constraints:**
* Do NOT write new arguments, generate citations, or add content.
* Evaluate the transitions between paragraphs: do they connect logically? Flag any "logical leaps" where a claim is made without sufficient preceding evidence.
* Are my underlying assumptions made explicitly clear?
* Are obvious counterarguments or limitations regarding this approach acknowledged?
* Flag any instances where my conclusions are stated more strongly than the provided evidence supports.

---

### 11. Citation & Source Integrity Check
**Task:** Review the following literature review section for citation integrity.
**Constraints:**
* Flag any definitive factual claims that are missing a corresponding citation.
* Highlight potentially redundant or over-cited claims.

---

### 12. Concept Exploration *(NotebookLM / Scholar Labs)*
**Task:** Analyze the uploaded set of papers regarding [Specific Framework/Concept].
**Instructions:** Extract the primary limitations or challenges mentioned by the authors.
**Constraints:**
* Base your answer strictly on the uploaded documents. Do not pull in outside knowledge.
* Provide exact citations (Author, Year, Page) for every bullet point so I can manually verify it.

---

### 13. Cross-Paper Concept Synthesis *(NotebookLM / Scholar Labs)*
**Task:** Compare how the provided documents define and approach [Specific Concept/Framework].
**Constraints:**
* Identify where the authors agree and where their methodologies diverge.
* Base the comparison strictly on the provided texts.

---

## Part 4: Specific Section Checks (Methodology, Abstract, Conclusion)

### 14. Methodology Soundness Check
**Role:** Senior Software Engineering Researcher.
**Task:** Review my methodology chapter for scientific soundness and reproducibility.
**Constraints:**
* Are the variables, metrics, and technical environments clearly and unambiguously defined?
* Are there any obvious missing controls or hidden biases in the evaluation setup?
* Based solely on this text, could another researcher reproduce the setup?

---

### 15. Research Gap & Contribution Clarity
**Task:** Evaluate the introduction/literature review transition provided below.
**Constraints:**
* Is the specific research gap clearly and explicitly stated?
* Is the gap framed as a *gap in knowledge* (something unknown) or a *gap in application* (something known but not yet applied in this context)? Flag if the framing is ambiguous or conflates the two.
* Is my proposed contribution easily distinguishable from the prior work I cited?
* Are my claims of novelty justified by the text?

---

### 16. Figures, Tables, and Cross-Reference QA
**Task:** Review the text to ensure all visual data is properly integrated.
**Constraints:**
* Check if all figures and tables are explicitly referenced in the text (e.g., via LaTeX `\ref{}`) before they appear.
* Evaluate if the captions are descriptive enough to be understood independently of the main text.
* Ensure the claims made in the text accurately align with the data presented in the referenced tables.

---

### 17. Quantitative Claims Verification
**Task:** Review the following section for internal quantitative consistency.
**Constraints:**
* For every percentage, probability, simulation result, or numerical claim stated in prose, verify that it matches the value in the referenced figure or table.
* Flag any discrepancy between a prose claim and its corresponding data source, even if minor (e.g., rounding differences, off-by-one values).
* Do not alter any numbers — only flag inconsistencies for my manual review.

---

### 18. Conclusion Quality Check
**Task:** Review my thesis conclusion against my original research questions.
**Constraints:**
* Does this conclusion explicitly answer the stated research questions?
* Flag if I have accidentally introduced new information, arguments, or literature that belongs in the main body.
* Ensure the limitations of the work are properly reflected.

---

### 19. Abstract Draft Review
**Task:** Review the following draft of my thesis abstract.
**Constraints:**
* Verify that it clearly contains: the problem statement, the methodology, the primary results, and the core contribution.
* Flag any vague language or unnecessary filler.

---

### 20. Final Consistency Audit (Submission-Stage Check)
**Task:** Perform a late-stage triple-consistency check across the three provided texts: (1) the abstract, (2) the introduction's research questions, and (3) the conclusion.
**Constraints:**
* Verify that every research question stated in the introduction is explicitly answered in the conclusion.
* Verify that the abstract accurately reflects both the methodology and the conclusions — flag any mismatch in scope, framing, or claimed results.
* Flag any terminology used in the abstract that differs from how the same concept is labeled in the introduction or conclusion.
* Do not suggest rewrites — produce a structured list of flagged inconsistencies only.

---

## Part 5: Secure Data Processing

### 21. Categorizing Internal/Sensitive Notes *(TU Wien Internal AI)*
**Task:** Review the following raw, anonymized system architecture notes and group them into logical categories for my methodology chapter.
**Constraints:**
* Maintain strict neutrality. Do not analyze the data or draw conclusions from it; only categorize it.
* Suggested categories should align with standard software engineering reporting (e.g., Performance Metrics, Security Protocols, Data Integrity).
