# PRISMA-LLM reporting instructions

PRISMA 2020 remains the primary reporting guideline for systematic reviews. PRISMA-LLM adds guidance for reviews that use LLMs or AI-enabled software in evidence-processing tasks.

For each substantive AI-assisted task:

1. Identify the review stage and task.
2. Complete the applicable checklist items.
3. Assign the method-complexity level that best describes the workflow.
4. Report the implementation, workflow, evaluation and limitation details required at that level.
5. Use stronger evaluation when AI outputs can affect review decisions, human verification is incomplete, the system is difficult to inspect, or errors are difficult to reverse.

The [fillable Excel workbook](PRISMA-LLM_reporting_checklist.xlsx) contains both checklist versions and fields for completion status, manuscript location and notes. The separate [evidence table](checklist_evidence.csv) records the empirical, workflow-derived and prior-guidance basis for the checklist.

## Quick reporting checklist

This 16-item checklist provides a page-sized overview. The expanded checklist below gives task-specific detail organized by PRISMA 2020 manuscript section.

| Section | Item | What to report | Applies when |
|---|---|---|---|
| Identification | **LLM-1: Title/abstract** | Identify substantive LLM or AI-enabled software use and the review stage(s) affected; distinguish review decisions/evidence processing from writing-only assistance. | All substantive AI-assisted review workflows |
| Rationale | **LLM-2: Purpose** | Explain why AI was used and which review burden or methodological problem it was intended to address. | All substantive AI-assisted review workflows |
| Methods | **LLM-3: System identification** | Report system/tool name, model/version, provider, access date, interface/API, deployment mode, and whether access was proprietary, open-weight, local, hosted or custom. | All substantive AI-assisted review workflows |
| Methods | **LLM-4: Task and disclosure level** | Specify each review task, assign the PRISMA-LLM implementation-disclosure level, and state whether outputs could alter retrieval, inclusion/exclusion, extraction, appraisal, synthesis or conclusions. | All substantive AI-assisted review workflows |
| Methods | **LLM-5: Inputs/document processing** | Describe records, abstracts, PDFs, tables, supplements, examples, labels and prior decisions supplied to the system, including parsing, OCR, section/table handling, chunking, context limits, truncation and retrieval. | Whenever documents or structured evidence are supplied to the system |
| Methods | **LLM-6: Prompts/settings** | Report prompts and system instructions, examples, schemas/rubrics, inference settings, repetitions/sampling, output constraints and model-specific settings needed to reproduce the workflow. | Whenever prompting or configurable model inference is used |
| Methods | **LLM-7: Outputs/post-processing** | Describe generated labels, rankings, extracted fields, judgments or text; output schemas; parsing/format repair; thresholds; confidence scores; and how model outputs became review decisions or analysis data. | Whenever AI outputs enter the review workflow |
| Methods | **LLM-8: Workflow development** | Report consequential prompt, schema, retrieval or orchestration changes, the rationale for the final workflow, and important failed or alternative configurations that informed it. | Whenever workflow development materially shaped the final method |
| Methods | **LLM-9: Task-specific workflow** | For screening, extraction, appraisal, annotation or LLM-as-judge use, report task-specific decision rules, reference standards, calibration, thresholds, edge-case handling and adjudication procedures. | Task-specific evidence processing or judging |
| Methods | **LLM-10: Human oversight** | State who reviewed AI outputs, what proportion was independently checked, how disagreements/corrections were handled, and who retained final responsibility for consequential decisions. | All workflows with human-AI interaction |
| Methods | **LLM-11: Evaluation plan** | Pre-specify performance, comparative, modification/optimization, resource/feasibility, and limitation/failure-mode evaluation as applicable; strengthen evaluation when task consequence, limited verification, opacity or irreversibility warrants it. | All substantive workflows; breadth depends on level and consequence |
| Results | **LLM-12: AI/human processing counts** | Report numbers of records, reports, fields, annotations, claims or judgments processed by AI, humans or both, including how automation altered the flow of records through the review. | Whenever processing can be counted or traced |
| Results | **LLM-13: Evaluation and errors** | Report task-specific performance and required comparative/modification/resource evidence, plus false positives/negatives, hallucinations, extraction/parsing failures, disagreements, corrections and audit outcomes. | Whenever evaluation is required or errors are observed |
| Discussion | **LLM-14: Limitations and implications** | Explain model/version dependence, prompt sensitivity, validation limits, proprietary opacity, remaining human workload and how observed or plausible failures could affect the evidence base or conclusions. | All substantive AI-assisted review workflows |
| Availability | **LLM-15: Reproducibility materials** | Provide prompts, system instructions, settings, schemas, code, validation samples, labels, audit logs and raw/parsed outputs when legally and ethically possible; report data-sharing, copyright, privacy, vendor and terms-of-service constraints. | All substantive workflows, subject to legal/ethical limits |
| Disclosure | **LLM-16: Support and interests** | Report sponsored access, credits, private model access, vendor involvement, material support and relevant competing interests. | Whenever applicable; explicitly state none if required by journal policy |

## Expanded reporting checklist

| Section | Item | What to report |
|---|---|---|
| Title | **LLM-T1: Title** | If LLMs or LLM-enabled software played a substantive role in the review workflow, consider indicating this in the title or subtitle, especially when they affected screening, extraction, synthesis, or other review decisions. |
| Abstract | **LLM-A1: Abstract** | Briefly summarize the LLM or software systems used, the review stages at which they were applied, and whether their outputs informed review decisions, extracted evidence, analysis, synthesis, or writing only. |
| Introduction | **LLM-I1: Rationale** | State the rationale for using LLMs or LLM-enabled software in the review, including the problem they were intended to address, such as screening burden, full-text retrieval, extraction burden, annotation, synthesis, quality control, or feasibility. |
| Methods | **LLM-M1: Protocol and deviations** | State whether LLM or software-mediated procedures were specified in the protocol. Report any additions, removals, or changes to LLM use after piloting, screening, extraction, annotation, or synthesis began. |
| Methods | **LLM-M2: System identification and access** | For each LLM, AI tool, or LLM-enabled software product, report the name, model or version, provider, access date, interface or API, deployment mode, and whether the system was proprietary, open, local, hosted, or custom-built. |
| Methods | **LLM-M3: Review stage, task, and disclosure level** | Specify the review stage and task for each system and assign a PRISMA-LLM implementation-disclosure level. Report whether outputs could alter search retrieval, inclusion or exclusion, extracted evidence, risk-of-bias judgments, synthesis, or conclusions; state the extent of human verification and who retained final responsibility. |
| Methods | **LLM-M4: Inputs and document processing** | Describe the input data provided to the system, including records, abstracts, PDFs, full texts, tables, supplements, labels, rubrics, examples, schemas, or prior human decisions. When full texts were used, describe PDF parsing, OCR, section extraction, table handling, chunking or splitting, context-window constraints, truncation or capping rules, retrieval setup, and whether supplementary materials were included. |
| Methods | **LLM-M5: Outputs, schemas, and post-processing** | Describe the outputs generated by the system, including labels, rankings, classifications, extracted fields, structured JSON, summaries, judgments, metrics, or drafted text. Report output schemas, parsing rules, confidence scores if used, automated post-processing, format repair, and how outputs were converted from free-form responses into review decisions, records, or analysis data. |
| Methods | **LLM-M6: Prompting and workflow development** | Report prompts, system instructions, settings, examples, and output constraints. When prompts or workflows were revised, explain the rationale for the final version, the failure modes that motivated changes, and important alternatives or failed attempts when they affected the final method. |
| Methods | **LLM-M7: Screening and selection workflow** | For title/abstract or full-text screening, report how LLM or software outputs were used to include, exclude, rank, prioritize, flag records, or determine what moved to full-text retrieval or later review stages. Report the number of records reviewed by humans, LLMs, or both; the audit procedure for false exclusions; disagreement handling; thresholds if used; and final human responsibility. |
| Methods | **LLM-M8: Data extraction workflow** | For LLM-assisted extraction, report the extraction schema, fields extracted, evidence sources used, output format, validation sample, manual verification rate, adjudication process, schema revisions or edge-case rules, and how missing, ambiguous, conflicting, tabular, or supplementary evidence was handled. |
| Methods | **LLM-M9: Annotation, harmonization, and LLM-as-judge use** | For annotation, harmonization, quality assessment, metric extraction, or LLM-as-judge workflows, report label definitions, rubrics, judge model or version where applicable, calibration examples or samples, human calibration labels, reference standards, human audit procedures, agreement checks, and whether LLM outputs were final evidence or intermediate assistance. |
| Methods | **LLM-M10: Human oversight and adjudication** | Describe human interaction with LLM outputs at each stage: who reviewed outputs, what proportion was checked, whether review was independent, how corrections were made, how disagreements were resolved, and who had final responsibility for review decisions. |
| Methods | **LLM-M11: Evaluation plan** | State the planned evaluation dimensions using the PRISMA-LLM reporting dimensions: performance, comparisons, modifications or optimization, resources and feasibility, and limitations or failure modes. Specify the minimum coverage implied by the implementation level and any stronger evaluation required by task consequence, limited human verification, system opacity, or irreversibility. |
| Methods | **LLM-M12: Data governance and reproducibility plan** | Describe how input, output, intermediate data, prompts, schemas, code, audit logs, and validation materials were stored and managed. Report privacy, copyright, terms-of-service, vendor-access, or data-sharing constraints that limit reproducibility. |
| Results | **LLM-R1: AI and human processing counts** | Report how many records, reports, fields, annotations, claims, judgments, or outputs were processed by LLMs or software, by humans, or by both. Where screening was automated or prioritized, distinguish human and LLM/software decisions in the text or flow diagram. |
| Results | **LLM-R2: Evaluation results** | Report evaluation results across the dimensions required for the workflow complexity level. Include task-specific performance evidence, comparative evidence, optimization or modification results, resource or feasibility evidence, and limitation or failure-mode evidence as applicable. |
| Results | **LLM-R3: Errors, disagreements, and corrections** | Report observed false positives, false negatives, hallucinations, failed extractions, parsing failures, prompt failures, disagreement patterns, corrected outputs, and audit outcomes. Describe how these errors affected the review workflow or final dataset. |
| Results | **LLM-R4: Resource and feasibility outcomes** | If the review claims efficiency, scalability, workload reduction, lower cost, or improved feasibility, report the evidence supporting those claims, such as human time, compute cost, API cost, runtime, number of records handled, or implementation burden. |
| Discussion | **LLM-D1: Limitations and failure modes** | Discuss limitations introduced by LLM or software use, including prompt sensitivity, model or version dependence, hallucination, extraction errors, missed records, validation limits, proprietary opacity, data-quality problems, and remaining human workload. Explain how these limitations may have affected the review process, evidence base, extracted data, synthesis, or conclusions. |
| Discussion | **LLM-D2: Experience and implications** | Discuss what was learned from using the LLM workflow, including what worked, what failed, what required human judgment, and what future reviewers should know before reusing a similar approach. |
| Other information | **LLM-O1: Availability of materials** | Provide stable record identifiers, prompts, system instructions, model and tool versions, settings, schemas, code, screening or extraction labels when applicable, validation samples, audit logs, raw and parsed outputs, annotation guidelines, calibration artifacts, and reproducibility materials when legally and ethically possible. |
| Other information | **LLM-O2: Support, access, and competing interests** | Report material support, sponsored access, credits, private model access, vendor involvement, or competing interests related to the LLM or software systems used in the review. |

## Reporting expectations by method-complexity level

The levels describe technical implementation complexity and set cumulative reporting requirements. Task consequence, human verification and error reversibility determine whether a workflow needs stronger evaluation.

| Level | Workflow type | Implementation and workflow reporting | Evaluation and limitation reporting |
|---|---|---|---|
| **1** | Off-the-shelf tool or software | Tool or product name, version or access date, provider or interface, role in the review, inputs and outputs, user-controlled settings if any, human oversight, and availability or validation constraints. | Report limitations or failure modes. Report other evaluation dimensions when relevant to the task or claims. |
| **2** | Prompt-only LLM | Level 1 details plus model identity, prompts or system instructions, settings, repetitions or sampling strategy, output format, and prompt constraints used for the task. | Report limitations or failure modes and task-specific performance evidence. Report comparative, modification and resource evidence when relevant. |
| **3** | Few-shot, structured, or engineered workflow | Level 2 details plus examples, schemas, rubrics, batching or prompt chains, voting or ensemble rules, LLM-as-judge setup if used, post-processing rules, and the rationale for the final workflow. | Report limitations or failure modes, task-specific performance, comparative evidence, and modifications or optimization. Report resource or feasibility evidence when relevant. |
| **4** | Retrieval-augmented, adapted, or single-agent workflow | Level 3 details plus retrieval sources, document parsing, chunking or context-window rules, embedding or retrieval settings, adaptation or fine-tuning procedure, thresholds, agent actions, failure handling, and resource constraints. | Report all five dimensions: task-specific performance, comparative evidence, modifications or optimization, resources or feasibility, and limitations or failure modes. |
| **5** | Multi-agent or swarm workflow | Level 4 details plus agent roles, coordination or debate protocol, handoff and termination rules, shared memory or state, conflict resolution, audit logs, and materials needed to reproduce the coordinated workflow. | Report all five dimensions plus coordination-specific failures, disagreement resolution, and evidence for any claimed benefit of cross-agent checking. |

## When stronger evaluation is needed

Use stronger validation at any level when one or more of the following applies:

- AI outputs can alter search retrieval, inclusion or exclusion, extracted evidence, appraisal, synthesis, or conclusions.
- Human verification covers only a sample of the outputs.
- The system is proprietary, hosted, mutable, or otherwise difficult to inspect.
- Errors are difficult to reconstruct, reverse, or detect after downstream processing.
