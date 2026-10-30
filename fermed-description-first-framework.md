---
title: "FERMED: A Description-First Framework for Reviewable Medical Image Interpretation"
author: "Sami Halawa Ribas"
orcid: "0009-0002-2021-1983"
affiliation: "Independent Researcher, Madrid, Spain"
date: "2026-10-30"
version: "1.0"
document_type: "Technical proposal and evaluation protocol"
keywords: [medical imaging, vision-language models, ophthalmology, structured reporting, uncertainty, human review]
---

# FERMED: A Description-First Framework for Reviewable Medical Image Interpretation

**Sami Halawa Ribas**  
Independent Researcher, Madrid, Spain  
ORCID: [0009-0002-2021-1983](https://orcid.org/0009-0002-2021-1983)  
Correspondence: sami@samihalawa.com  
Technical proposal and evaluation protocol | 30 October 2026

## Abstract

Medical vision-language systems often combine image description, disease interpretation and report generation in a single response. This makes it difficult to identify whether an error arose from visual observation, clinical inference or communication. FERMED proposes a description-first workflow that separates these responsibilities through an explicit, inspectable interface. A visual module records image quality, observable findings and unavailable evidence; an interpretation module uses those observations to formulate bounded clinical hypotheses; and a consistency module checks whether each statement is supported by the recorded findings. A clinician retains access to the original image and decides whether to accept, revise or reject the report. Ophthalmic imaging provides a motivating application because apparently similar findings can support different interpretations and some diagnoses require information absent from a single image. The contribution is a model-agnostic architecture, a structured output contract and an evaluation protocol that measures observation fidelity separately from downstream decision performance. The protocol includes patient-level separation, external validation, description perturbations, matched-compute baselines, calibration and selective prediction. This paper does not report a trained FERMED model, patient cohort, diagnostic accuracy result or clinical validation. It establishes testable design hypotheses and a reproducible framework for evaluating them before any clinical use.

## 1. Motivation and contribution

A useful medical-image report must do more than supply a plausible label. It must describe what can actually be seen, identify limitations of acquisition, distinguish observations from interpretations and make the next review step clear. A fluent report can conceal failures in any of these operations. For example, an interpretation may be coherent given its written findings even when the findings themselves misrepresent the image. Conversely, a reliable description may be followed by an unsupported clinical conclusion. A single aggregate score cannot explain this difference.

FERMED treats the interface between observation and interpretation as an experimental object. Its central hypothesis is that explicitly recording visual findings can improve the reviewability of a medical-image workflow while preserving sufficient information for a downstream task. Neither improved accuracy nor reduced review burden follows automatically from this separation. The description can become an information bottleneck, and additional modules can repeat the same error. These possibilities are included in the proposed evaluation rather than assumed away.

The framework makes three contributions. First, it defines distinct roles for observation, interpretation, consistency checking and clinician adjudication. Second, it specifies a structured record that connects interpretive statements to their supporting observations. Third, it proposes experiments that locate the source of errors and compare the modular workflow with direct image-to-answer baselines. The present contribution is a technical proposal; the accompanying demonstrator communicates the workflow and does not establish the behavior of an operational inference system.

## 2. Relation to existing work

Vision-language research provides several ways to combine visual representations with language generation. BLIP-2 connects pretrained visual and language components through a learned intermediary [1]. LLaVA-Med studies adaptation of a conversational vision-language assistant to biomedical material [2]. These approaches motivate separating component roles, but their published results are not results for FERMED. A chosen foundation model would still require evaluation on the specific imaging task, population and acquisition conditions.

Retinal foundation models provide a complementary comparison. RETFound studies representation learning and adaptation for retinal tasks [3]. Such task-oriented predictors are important baselines: a description-generating system should not be compared only with other generative systems if the intended decision can be addressed by a dedicated classifier. A useful comparison asks what the description interface adds, what it loses and what review effort it requires.

The proposed workflow also distinguishes readable justification from evidential support. A generated rationale is text produced by a model; it is not proof of the model's internal reasoning or a verified causal explanation. FERMED therefore evaluates links between findings and claims, and tests the response to controlled changes in the findings. For numerical predictions, it treats calibration as a separate property from discrimination, following the distinction developed in calibration research [4].

## 3. Proposed architecture

### 3.1 Inputs and configuration

Each case contains an image or explicitly defined image set, acquisition metadata, an allowed task and a versioned configuration. The configuration fixes model identifiers, preprocessing, prompts, decoding parameters, output schema and stopping rules. Clinical context is supplied through a separate, documented channel so that experiments can distinguish image-derived information from contextual information. Missing context must remain missing rather than being inferred from typical patient profiles.

The initial research scope is a defined ophthalmic image task, not unrestricted diagnosis across medical specialties. An experiment might study whether a fundus photograph supports specified observable findings or a referral-relevant classification. It must state which conclusions cannot be established from that modality alone. Dataset labels, disease definitions and reference standards must match the question actually being asked.

### 3.2 Observation module

The visual module receives the image and an observation-oriented instruction. It records image quality, visible structures, localized findings, relevant absences and uncertainties. Each observation has a stable identifier, a location where applicable and an evidence status. The instruction asks for visible features rather than a predetermined diagnosis. However, a prompt alone cannot enforce that boundary; diagnostic language and unsupported findings must be measured during evaluation.

For a fundus photograph, the record may cover the optic disc, macula, vessels and visible retinal field. The module must be able to state that a structure is obscured or not assessable. It should not convert poor visibility into a normal finding. Measurements such as a ratio require an explicit method and uncertainty; otherwise, the system reports a qualitative description rather than an invented precise value. A clinician can inspect the original image beside this record.

### 3.3 Interpretation module

The interpretation module receives the structured observations, allowed contextual fields and task definition. In the primary modular condition it does not receive image pixels. It returns a bounded assessment and identifies the observation identifiers supporting each interpretive statement. It also records contradictory evidence, alternative explanations and information needed to distinguish them. A conclusion requiring an unavailable modality or examination must be marked unresolved.

The proposed base configuration uses pretrained components at inference time. Description generation is not training, and using a generated description as a prompt does not update model weights. Supervised adaptation or preference-based tuning could be studied later as separate experimental conditions, with their own datasets, provenance and held-out evaluation. They are not prerequisites silently assumed by this architecture.

### 3.4 Consistency review and clinician adjudication

A consistency module checks the schema, verifies that cited observations exist and flags claims that are unsupported, contradictory or outside the task. Deterministic checks cover mechanical properties; a language-model reviewer may assess semantic consistency. Agreement between models is not a reference standard. Review must therefore preserve unresolved flags and avoid converting a second model's approval into clinical validation.

At most one revision is proposed for the primary experimental configuration. The interpretation module may revise its answer using consistency feedback, but the original observation record remains immutable. A reviewer cannot repair an image-level error by rewriting the evidence until it matches the conclusion. Cases requiring a new image inspection are returned to a clinician or evaluated in a separately specified reinspection condition. The clinician's decision and edits are recorded independently from the generated report.

### 3.5 Output contract

The following illustrative schema defines relationships between fields. It contains no patient example or experimental result.

```json
{
  "case_id": "research-pseudonym",
  "quality": {"assessable": true, "limitations": []},
  "observations": [{"id": "O1", "region": "defined region",
    "finding": "observable feature", "uncertainty": "stated limitation"}],
  "assessment": [{"statement": "task-bounded interpretation",
    "supported_by": ["O1"], "unresolved": []}],
  "consistency_flags": [],
  "disposition": "clinician_review_required"
}
```

Quantified probabilities are optional and require a validated probability-generation and calibration procedure. The system must not turn linguistic confidence words into percentages. Provenance accompanies the record: model revision, configuration hash, preprocessing version and timestamp. Access controls and retention policies apply to both the image and the generated record.

### 3.6 Reference procedure

```text
freeze configuration and permitted task
check image availability, format and acquisition metadata
O = describe_image(image, observation_prompt, configuration)
if O is invalid or the task is not assessable:
    return limited report with reason and clinician-review disposition
I = interpret(O, permitted_context, task)
C = check_schema_and_support(O, I, task)
if C identifies a repairable interpretive inconsistency:
    I = revise_interpretation(O, I, C)  # do not rewrite O
    C = check_schema_and_support(O, I, task)
return O, I, C and provenance for independent clinician adjudication
```

## 4. Evaluation protocol

### 4.1 Questions and study registration

The primary question is whether the description-first workflow changes task performance at a comparable review burden relative to a direct image-to-answer baseline. Secondary questions concern observation fidelity, unsupported statements, consistency checking and abstention. Before evaluating a held-out cohort, investigators must fix the task, primary endpoint, clinically relevant operating threshold, baseline implementations, analysis plan and exclusion rules. Sample-size planning must account for outcome prevalence, patient clustering and the precision required around sensitivity or other primary measures.

This paper supplies no assumed effect size and no claim of completed recruitment. A later study should publish its registered protocol, amendments and deviations with the outcome report. Decisions made after seeing test results must be identified as exploratory. Prompt selection, model choice and stopping rules are part of model development and cannot be optimized on the final test cohort.

### 4.2 Data provenance, partitioning and reference standards

Each dataset must have documented access rights, intended use, label definitions, acquisition characteristics and inclusion criteria. Public availability alone does not establish permission for every use. Images from the same patient, both eyes, repeat visits and near-duplicate acquisitions must remain in a single development or evaluation partition. Deduplication should combine metadata checks with image-similarity review and document uncertain matches.

Training or prompt-development material, calibration data, internal test data and external validation data serve distinct purposes. Any adaptation uses only development material. Calibration and threshold selection use a separate validation set. An external cohort should differ meaningfully in site, device, population or time, and its performance must be reported separately. Investigators should assess possible foundation-model pretraining overlap and disclose where overlap cannot be determined.

The reference standard must be appropriate to the endpoint. An image label is not automatically a complete clinical diagnosis. For findings, independent qualified readers can annotate visibility, location and presence under a predefined rubric. Disease or referral labels may require examinations, longitudinal records or adjudication beyond a single image. Reader disagreement is retained and reported; consensus procedures and access to additional evidence must be specified before evaluation.

### 4.3 Baselines and ablations

The following comparisons separate architectural effects from additional computation and supervision.

| Condition | Purpose |
| --- | --- |
| Direct image-to-answer using the same visual backbone | Tests the value and cost of the description interface. |
| Direct generation with a matched token or inference budget | Controls for the modular workflow's extra computation. |
| Description followed by interpretation, with no consistency reviewer | Isolates the review stage. |
| Full proposed workflow | Tests the complete observation, interpretation and consistency design. |
| Clinician-authored descriptions supplied to the same interpreter | Estimates the downstream task's dependence on description quality. |
| Appropriate task-specific image classifier | Provides a nongenerative performance reference where available. |

Models, data access and tuning effort must be disclosed for every condition. Ablations remove structure fields, uncertainty fields or contextual inputs individually. Controlled description perturbations delete a relevant finding, insert a contradictory finding or change a location. The interpretation should respond appropriately to the changed evidence rather than reproducing a fixed answer. These tests assess functional dependence; they do not establish complete explanation faithfulness.

### 4.4 Metrics and statistical analysis

Observation evaluation measures finding-level precision and recall, unsupported findings, clinically consequential omissions, localization errors and correct identification of unassessable structures. Text-overlap scores may supplement these measures but cannot substitute for them: two descriptions can share words while disagreeing on a decisive abnormality. Reader scoring should use a published rubric, blinded ordering and inter-reader agreement estimates.

For classification, report the confusion matrix, sensitivity, specificity, positive and negative predictive values, discrimination and performance at the prespecified threshold. Predictive values must be interpreted in relation to the evaluated prevalence. Confidence intervals should account for patient clustering; comparisons between conditions should use paired analyses on the same cases. Report all prespecified endpoints, multiplicity handling and missing or failed outputs. An invalid or empty response cannot simply disappear from the denominator.

When probabilities are available, report reliability plots and a proper scoring rule such as the Brier score, alongside discrimination. Calibration fitting must exclude test cases [4]. For abstention, report coverage, error among accepted cases and the characteristics of deferred cases. Latency, hardware, memory, monetary cost where relevant and clinician editing time provide operational context. Clinical utility requires a separate human study with a defined workflow and outcome; model agreement alone is insufficient.

### 4.5 Robustness and failure analysis

Stratified analyses should cover acquisition quality, device or site and clinically relevant subgroups where sample sizes support interpretable estimates. Results for small groups require uncertainty reporting rather than broad equivalence claims. Investigators should test image transformations, irrelevant context, missing metadata and deliberately conflicting observations. Out-of-distribution testing should include images outside the allowed modality and conditions that the system cannot assess.

Each serious error is assigned to observation, interpretation, consistency review or workflow handling. Some errors span stages. The analysis should retain those interactions: a reviewer can correctly detect an unsupported statement while missing an earlier omitted feature. A blinded sample of apparently correct reports should also be reviewed to detect plausible but unsupported reasoning. Publication of de-identified error taxonomies and appropriately licensed examples would make failures easier to compare across systems.

## 5. Deployment and information handling

FERMED's modularity permits different deployment choices, but it does not by itself provide privacy, security or regulatory compliance. A local interpreter still receives potentially sensitive health information in the description. Removing image pixels does not make the text anonymous. Cloud-based visual processing can transmit the original image, while local processing depends on compatible models, hardware and operational configuration.

A research deployment should specify the trust boundary of each component, permitted network destinations, logging behavior, retention and deletion rules. Identifiers, image overlays and report text need separate review. Access controls should cover generated records as well as source images. External tools and retrieval sources must be defined; the interpreter should not silently obtain additional patient information or execute instructions embedded in images or documents.

The current proposal does not establish a production integration with an electronic health record, a clinical workflow standard or a medical-device approval. Such integrations are future engineering work requiring separate verification. The intended immediate use is research on reporting structure and error attribution, with qualified human review. No generated output in this proposal is a basis for autonomous clinical action.

## 6. Discussion and limitations

The strongest potential benefit of a description-first workflow is the ability to inspect and test its intermediate evidence. An explicit interface allows investigators to ask whether an observation was missed, whether the interpreter used it and whether a review stage introduced changes. It also permits a clinician-authored description to replace a generated one during controlled experiments. These are architectural properties, not demonstrated improvements in patient outcomes.

The approach has substantial limitations. Text may discard spatial relationships, subtle textures, scale and temporal information. A downstream module cannot recover details it never receives. More stages can increase latency, cost and correlated errors, and a consistency reviewer may reward fluent agreement. A report that is easier to read may also increase unwarranted trust. Evaluation must therefore include calibration, omissions and review behavior rather than only answer accuracy.

FERMED is distinct from a new pretrained model or a claim of cross-specialty clinical validation. Its present artifact is a workflow specification and static demonstrator. A reproducible implementation, frozen model configuration, licensed evaluation cohort and completed analysis remain necessary to test the hypotheses. Expansion to another modality requires a new task definition and validation; a shared software interface does not establish medical generalization.

## 7. Conclusion

FERMED proposes a reviewable separation between visual observations, clinical interpretation and consistency checking. Its contribution is a concrete interface and experimental protocol for examining that separation. The next empirical step is a registered, task-specific comparison against matched-compute and task-specific baselines, with independent reference standards and explicit failure accounting. Until that evaluation is completed, the framework should be understood as an architecture proposal rather than a validated diagnostic system.

## Declarations

**Author contribution.** Sami Halawa Ribas: conceptualization of the FERMED workflow, architecture design, demonstrator development and manuscript preparation.

**Funding.** No external funding is claimed for preparation of this technical proposal. This paper does not report a funded clinical study.

**Competing interests.** The author develops AI software and related services. The proposed framework's clinical efficacy is not established by this paper.

**Research ethics.** This proposal reports no analysis of participant data and claims no ethics approval, completed clinical trial or patient recruitment. Any subsequent study must establish the necessary permissions, oversight and participant protections for its particular data and setting.

**Data and code availability.** No patient dataset, trained FERMED weights, prediction files or empirical result package accompanies this proposal. The existing demonstrator is a static presentation of the concept. A public reproducible inference implementation is not claimed. The output contract, reference procedure and evaluation design are specified in this manuscript; future experimental releases should include versioned prompts, configurations, split manifests where permitted, analysis code and per-case outputs subject to data-use restrictions.

**AI assistance.** AI tools assisted literature checking, organization and language editing. The named author remains responsible for the manuscript's content and any subsequent submission. No AI system is listed as an author, and no model-generated experimental result is presented as an observation.

## References

1. Li J, Li D, Savarese S, Hoi S. BLIP-2: Bootstrapping Language-Image Pre-training with Frozen Image Encoders and Large Language Models. 2023. [arXiv:2301.12597](https://arxiv.org/abs/2301.12597).
2. Li C, Wong C, Zhang S, et al. LLaVA-Med: Training a Large Language-and-Vision Assistant for Biomedicine in One Day. 2023. [arXiv:2306.00890](https://arxiv.org/abs/2306.00890).
3. Zhou Y, Chia MA, Wagner SK, et al. A foundation model for generalizable disease detection from retinal images. *Nature*. 2023;622:156-163. [doi:10.1038/s41586-023-06555-x](https://doi.org/10.1038/s41586-023-06555-x).
4. Guo C, Pleiss G, Sun Y, Weinberger KQ. On Calibration of Modern Neural Networks. 2017. [arXiv:1706.04599](https://arxiv.org/abs/1706.04599).
