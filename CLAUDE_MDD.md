# CLAUDE.md — Adult Major Depressive Disorder Treatment Algorithm

## Project Overview

This notebook implements a clinical decision support tool for adult major depressive disorder
(MDD) treatment selection. It uses a decision tree and random forest model to evaluate patient
inputs and produce structured treatment recommendations with rationale and citations.

The primary source document is the Adult MDD Decision Support Algorithm (VA/DoD-aligned).
Specialist corrections and additions are integrated below and supersede the source document
where noted. Every recommendation the algorithm produces must include an inline rationale
statement and cite the specific references that support that decision. References appear inline
(e.g. [4, 19]) and the full reference list appends to every output.

Three reference sets exist:
- [R#] = References from the source algorithm document (numbered 1-34 in that document)
- [S#] = Specialist supplementary references (numbered 1-33 in the corrections document)
- [T#] = Trial logic and treatment-resistance references (partial response clarification document)

---

## Master Decision Flow

The algorithm evaluates every patient in this sequence. Do not skip steps.

### Step 0: Triage and Safety Screen

**Bipolar screen:**
- Any recent or remote manic or hypomanic episode → route to Bipolar Decision Support
- Do not initiate antidepressant monotherapy; antidepressants can precipitate mania
- Citations: [3, 4]

**Suicidality screen:**
- Acutely suicidal → emergent hospitalization
- Elevated suicidal ideation without acute risk → consider hospitalization; close monitoring
- FDA black box warning applies to all antidepressants in patients under 25 years old
- Citations: [3, 4, 73, 74]

---

### Step 1: Severity Stratification and Initial Treatment Selection

Severity is determined by PHQ-9 score. Assign `depression_severity_category` before routing.

| PHQ-9 Score | Category |
|---|---|
| 5–9 | Mild |
| 10–14 | Moderate |
| 15–19 | Moderate-Severe |
| ≥ 20 | Severe |

**Mild to Moderate (PHQ 5–14):**
- Psychotherapy alone is first-line [1, 2, 3, 4]
- Supported modalities: CBT, interpersonal therapy, problem-solving therapy, behavioral
  activation [3, 4, 5, 6]
- Consider pharmacotherapy alone or in combination if: patient fails psychotherapy, patient
  preference, or history of recurrent depression [2, 4]
- Citations for psychotherapy positioning: [1, 2, 3, 4, 5, 6]

**Mild (PHQ 5–10) — self-help:**
- MoodCalmer dCBT is the preferred self-help program and can be recommended by name

**Severe (PHQ ≥ 15):**
- Combination pharmacotherapy and psychotherapy is required [3, 4]
- Psychotherapy alone is insufficient at this severity level
- Citations: [3, 4]

---

### Step 2: Check for Deviation Path Triggers

Evaluate all deviation triggers before selecting a first-trial medication. A patient may
trigger multiple deviation paths simultaneously. Apply all that are relevant.

Deviation paths and their triggers are fully defined in the Deviation Paths section below.

Triggers to evaluate (in order):
1. Age < 18 → Pediatric path
2. Age ≥ 65 → Geriatric path
3. Pregnant or postpartum → Pregnancy/Postpartum path
4. eGFR < 60 → Renal path
5. Hepatic impairment present → Hepatic path
6. Cardiac disease, QTc prolongation, or QTc-prolonging medications → Cardiac path
7. Anxiety comorbidity → Anxiety path
8. Chronic pain or fibromyalgia → Pain path
9. Prominent insomnia → Insomnia path
10. Obesity (BMI ≥ 30) → Obesity path
11. Dementia → Dementia path

---

### Step 3: First Trial Antidepressant Selection

**Standard adult first-line options (SOR A) [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]:**
- SSRI: sertraline, escitalopram, citalopram, fluoxetine
- SNRI: venlafaxine, duloxetine
- Atypical: bupropion, mirtazapine

**SSRI ranking within standard adult track (corrected order per specialist review):**
1. Escitalopram — best efficacy and acceptability [19, 20, 26]
2. Sertraline — excellent tolerability, broad indications [19, 26]
3. Fluoxetine — long half-life, CYP2D6 interactions limit use [19, 26]
4. Citalopram — QTc concerns limit dosing flexibility [25, 27]
5. Paroxetine — anticholinergic burden; avoid in elderly, dementia, obesity [26, 28]
6. Fluvoxamine — not FDA-approved for MDD (off-label); poorest tolerability [24, 25]

**SNRI positioning:**
- First-line alongside SSRIs for moderate-severe depression [7, 25, 29]
- Preferred over SSRI when: chronic pain or fibromyalgia [29, 35], prominent fatigue or
  anhedonia [32], severe depression (PHQ ≥ 20) [33]

**Adjunctive pharmacotherapy (consider at any point during treatment, SOR B):**
- Omega-3 fatty acids [60, 64, 65, 66]
- COX-2 inhibitor (e.g., celecoxib) [60, 61, 62, 66]
- Citations: [60, 61, 62, 64, 65, 66]

**Comorbidity-driven first-line selection:**

| Comorbidity | Preferred First-Line | Avoid | Citations |
|---|---|---|---|
| Anxiety | SSRI or SNRI | — | [34] |
| Chronic pain / fibromyalgia | Duloxetine, then venlafaxine | SSRIs (ineffective for pain) | [25, 29, 35] |
| Prominent insomnia | Mirtazapine (if no obesity) | — | [25, 30] |
| Fatigue / anhedonia | Duloxetine, venlafaxine, bupropion | — | [25, 32] |
| Sexual dysfunction concern | Bupropion, mirtazapine, vilazodone | SSRIs (high risk) | [24, 25] |
| Obesity | Bupropion, fluoxetine | Mirtazapine, paroxetine | [25, 30] |

---

### Step 4: Starting Dose and Titration

Start at the lower end of the therapeutic range. Higher doses increase adverse effects without
improving efficacy. Citations: [22, 26]

**Standard starting doses:**

| Medication | Start | Target Range | Max | Notes |
|---|---|---|---|---|
| Escitalopram | 10 mg/day | 10–20 mg | 20 mg | Max 10 mg if age ≥ 65 [27, 30] |
| Sertraline | 50 mg/day | 50–100 mg | 200 mg | — |
| Citalopram | 20 mg/day | 20–40 mg | 40 mg | Max 20 mg if age ≥ 60 [25, 27] |
| Fluoxetine | 20 mg/day | 20–40 mg | 80 mg | — |
| Venlafaxine IR | 37.5–75 mg/day | 75–150 mg | 375 mg divided | Divided 2–3x/day [22] |
| Venlafaxine ER | 37.5–75 mg/day | 75–150 mg | 225 mg | — |
| Duloxetine | 40–60 mg/day | 60 mg | 60 mg | — |
| Bupropion IR | 100 mg twice daily | — | 450 mg | Doses ≥ 6h apart (seizure risk) |
| Bupropion SR | 150 mg/day | 150 mg twice daily | 400 mg | Doses ≥ 8h apart |
| Bupropion ER | 150 mg/day | 300 mg/day | 450 mg | — |
| Mirtazapine | 15 mg nightly | 30 mg | 45 mg | At bedtime [22] |

**Titration cadence:**
- Follow up and titrate dose every 1–2 weeks during active medication management [3, 4]

---

### Step 5: Response Assessment and Trial Logic

An adequate trial is defined as 4–12 weeks at maximally tolerated dose. Citations: [25, 36, 37, 38, 39, 40, 47, 48]

**Response categories:**
- Adequate response at or before max dose → continue, proceed to maintenance
- Partial response at max dose → augmentation pathway (see Step 6)
- Inadequate response or not tolerable at max dose → switch pathway (see Step 7)

---

### Step 6: Partial Response — Augmentation Pathway

Use when patient achieves meaningful but incomplete improvement at maximally tolerated dose.
Citations: [21, 36, 37, 38, 39, 40, 42, 45, 47, 48]

#### Tier 1 — First-Choice Augmentation (co-equal options; choose based on tolerability and patient preference)

- **Aripiprazole:** 2–5 mg/day start, max 15 mg/day. NNT=8 for response. OPTIMUM trial:
  28.9% remission vs 19.3% for switching. [43, 45, 46]
- **Add bupropion (if patient is currently on SSRI or SNRI):** Comparable remission to
  aripiprazole (28.2% vs 28.9% in OPTIMUM trial). Complementary dopamine-norepinephrine
  reuptake inhibition mechanism. [45, 46]
- **NOTE — Mirtazapine augmentation is NOT a first-choice option:** High-quality evidence
  shows no clinically meaningful benefit (MD on BDI-II −1.7, 95% CI −4.03 to 0.63) and
  significantly higher discontinuation rates than placebo. Do not include mirtazapine in
  first-choice augmentation. [43, 51]
- **Exception — Chronic suicidality:** Consider lithium as first choice due to unique
  anti-suicide properties. [47, 48, 54]

#### Tier 2 — Second-Choice Augmentation (after Tier 1 failure or contraindication)

- **Quetiapine:** 150–300 mg/day. Strong efficacy (SMD −0.32) but higher discontinuation
  rates (RR 1.57). 2025 LQD trial found quetiapine superior to lithium over 52 weeks.
  [49, 50, 51]
- **Brexpiprazole:** FDA-approved for MDD augmentation. OR 1.47–2.17 for response.
  [24, 43, 44]
- **Cariprazine:** FDA-approved for MDD augmentation. OR 1.34 for response; not significant
  for remission. [24, 43, 44]
- **Lurasidone:** Limited evidence in unipolar depression; most data in bipolar. Use
  cautiously. [43]

**Monitoring for Tier 2 atypical antipsychotics:**
- BMI: monthly for 3 months, then every 3 months
- Blood pressure, lipids, HbA1c: at initiation, after 3 months, then annually
- Consider ECG at initiation; monitor for extrapyramidal symptoms
- Note: all atypical antipsychotics carry increased mortality risk in elderly patients with
  dementia (FDA black box) — flag prominently if augmentation is considered [26, 28]

#### Tier 3 — Targeted Augmentation (specific indications only)

- **Lithium:** Reserve for chronic suicidality (unique anti-suicide properties) or after
  atypical antipsychotics fail. STAR*D showed only 15.9% remission; 2025 LQD trial found
  quetiapine superior. Target 0.6–1.2 mEq/L general population; 0.3–0.6 mmol/L in older
  adults. Monitor: Li+ level, TSH, BMP at initiation, 1–2 months, then every 6–12 months.
  [47, 48, 49, 50, 54]
- **Methylphenidate:** Residual anergia or fatigue only. Low-to-very-low evidence quality.
  Not for broad augmentation. [56, 57, 58]
- **Lisdexamfetamine:** One positive RCT for augmentation; FDA-approved for binge eating
  disorder only — flag as off-label for MDD. [43, 59]

#### Tier 4 — Optional Adjuncts (parallel to main pathway, never replace Tier 1–2)

- **Omega-3 fatty acids (EPA ≥60%, 1–1.5 g/day):** SOR B. Small benefit (SMD −0.40), very
  low certainty. VA/DoD concluded insufficient evidence to recommend over validated
  medications. Present as "may consider adding." [4, 64, 65, 66, 67, 68]
- **Celecoxib 400 mg/day × 6 weeks:** SOR B. Moderate benefit (SMD −0.82, OR for remission
  7.89) but high risk of bias. Contraindicated: cardiac history, eGFR < 60, NSAID
  contraindications. Present as "may consider adding." [60, 61, 63]

---

### Step 6a: Partial Response at Second Trial

Guidelines do not explicitly specify this branch. Apply clinical judgment guided by the
following evidence-based framework. Citations: [45, 53, 54, 55]

**If partial response at second trial with good tolerability:**
- Augmentation strategies remain reasonable before advancing to a third trial [45, 53]
- Apply same four-tier augmentation hierarchy as Step 6
- If first augmentation was aripiprazole: consider switching to quetiapine or adding
  bupropion (if on SSRI/SNRI) [45]
- If first augmentation was bupropion: consider adding aripiprazole or switching to
  quetiapine [45]
- Reassess: diagnostic accuracy, medication adherence, comorbid conditions contributing to
  treatment resistance [45, 53, 54]
- Citations: [45, 53, 54]

**If partial response at second trial with poor tolerability:**
- Switch to third trial medication (untried class) per Step 7
- Citations: [25, 55]

---

### Step 6b: Partial Response at Third Trial

Third trial partial response indicates treatment complexity that exceeds routine primary care
management. Citations: [45, 53, 54, 55]

- Psychiatric consultation is advisable [53, 55]
- Reassess diagnostic accuracy, adherence, and comorbidities before escalating [45, 53, 54]
- Consider advanced interventions: electroconvulsive therapy, ketamine/esketamine,
  transcranial magnetic stimulation [45, 53, 54]
- STAR*D data: cumulative remission rates reach 67% across four treatment levels, but provide
  no definitive guidance on partial response management after multiple trials [25]
- Citations: [25, 45, 53, 54, 55]

---

### Step 7: Inadequate Response — Class-Based Routing

Routing is determined by which medication **classes** appear in the patient's prior trials,
not by trial count alone. The algorithm evaluates `_classes_trialed(p)` — the set of
medication classes (SSRI, SNRI, NDRI, NaSSA, TCA, SGA) present in `prior_trials` and
`current_antidepressant_key`. Rules are evaluated in reverse priority order (Rule 5 first,
Rule 1 as fallback). Citations: [102, 103, 104, 105, 106, 107, 108, 109, 110, 111]

**Rule 1 — First Line (no prior trials):**
- Offer escitalopram, sertraline, bupropion XL [19, 20, 26]
- Add mirtazapine if insomnia; add duloxetine if chronic pain/fibromyalgia
- Comorbidity-driven exclusions: bupropion excluded if anxiety, seizure history, or
  eating disorder [28]; citalopram excluded if cardiac history [78, 79]; paroxetine
  excluded if pregnant [73]; all SGAs excluded if dementia [43]

**Rule 2 — SNRI Switch (SSRI tried, SNRI not tried):**
- Recommend venlafaxine XR and duloxetine as switch options [102, 103, 105]
- Include switching protocol from current SSRI to SNRI
- No TRD flag at this stage

**Rule 3 — TRD Step 2 (SSRI + SNRI tried, NDRI/NaSSA not tried):**
- Recommend bupropion XL and mirtazapine [106, 107, 28]
- Soft TRD warning: "Treatment-Resistant Depression — consider psychiatric
  consultation" [104, 105]
- Soft consultation block appears AFTER medication recommendations
- Include symptom-driven selection notes for each medication

**Rule 4 — Hard Psychiatric Consultation (SSRI + SNRI + (NDRI or NaSSA) tried):**
- Hard consultation warning appears FIRST [108, 109]
- TCA options (nortriptyline, desipramine) listed below, labeled "pending psychiatric
  input" — do not initiate without psychiatric consultation [108, 109]
- PCP actions while awaiting consultation: continue current med, optimize psychotherapy,
  reassess diagnosis, confirm adherence, monitor PHQ-9 and suicidality [104, 105]

**Rule 5 — Advanced Interventions (TCA tried, OR PHQ ≥ 20 + suicidality, OR psychosis):**
- Mandatory psychiatric referral [110, 111]
- No medications recommended — only advanced interventions:
  ECT, TMS, IV ketamine, esketamine (Spravato) [110, 111]

**Trial adequacy definition:**
Adequate trial = 4–12 weeks at maximally tolerated dose [25]
Prior medication names must be tracked to exclude previously failed agents [26]

**Comorbidity-driven exclusions (applied at all rules):**
- Anxiety → exclude bupropion (activating profile) [28]
- Seizure history → exclude bupropion (lowers seizure threshold) [28]
- Eating disorder → exclude bupropion (contraindicated in bulimia/anorexia) [28]
- Cardiac history → exclude citalopram (QTc prolongation risk) [78, 79]
- Pregnant → exclude paroxetine (cardiac malformation risk) [73]
- Dementia → exclude all SGAs (increased mortality, FDA black box) [43]

**Selection notes (every factor that changes selection must produce a visible note):**
- Elevation notes: fatigue/anhedonia → bupropion preferred [106, 28];
  sexual dysfunction → bupropion preferred [28]
- Preference notes: insomnia → mirtazapine preferred [107, 28];
  anxiety → SSRIs preferred [28]; chronic pain → duloxetine added [35];
  cardiac → sertraline preferred [78, 79]
- Dose modification notes: age ≥ 60 + escitalopram → 10mg cap [78, 80];
  hepatic impairment → dose reduced [85, 86]; renal impairment → dose reduced [83, 84];
  cardiac + SNRI → BP monitoring [31, 32]

---

### Step 7a: Switching and Tapering Protocols

Apply this section whenever Step 7 routes to a switch (no response or intolerance after
adequate trial). Tapering guidance also applies to maintenance discontinuation (Step 9).

#### SWITCHING PROTOCOLS BY CLASS

**Rule A — SSRI → SSRI (direct switch):**
- Stop prior SSRI, start new SSRI at standard starting dose the next day [28, 87]
- If patient has history of withdrawal sensitivity, consider abbreviated overlap over
  3–7 days instead [28, 87]
- Exception: paroxetine or fluvoxamine as prior — use cross-taper (see Rule E)

**Rule B — SSRI → SNRI (direct switch):**
- Stop prior SSRI, start new SNRI at standard starting dose the next day [28, 87, 114]
- If patient has history of withdrawal sensitivity, consider abbreviated overlap over
  3–7 days instead [28, 87, 114]
- Exception: paroxetine or fluvoxamine as prior — use cross-taper (see Rule E)

**Rule F-REVERSE — SNRI → SSRI (direct switch with NE withdrawal warning):**
- Stop prior SNRI, start new SSRI at standard starting dose the next day [28, 87, 93]
- Norepinephrine withdrawal symptoms (dizziness, headache, fatigue, irritability) may
  occur regardless of SSRI serotonergic coverage because SSRIs do not replace
  norepinephrine reuptake inhibition [93]
- If patient has history of withdrawal sensitivity, abbreviated overlap over 3–7 days
  may reduce NE withdrawal symptoms [28, 87]

**Fluoxetine → any antidepressant (Rule C):**
- Direct switch safe — norfluoxetine metabolite half-life 7–15 days provides built-in
  taper [28, 87]
- Exception: switching to MAOI requires 5-week washout [28, 87]

**Paroxetine → any antidepressant (Rule D):**
- Mandatory slow taper due to high discontinuation risk and CYP2D6 inhibition [28, 87, 92]
- Dose-calculated step-down taper; start new medication at Week 2 [28, 87]

**SSRI or SNRI → bupropion or mirtazapine (Rule E):**
- Cross-taper 1–2 weeks preferred [28, 87]
- Lower serotonin syndrome risk due to different mechanisms [28, 87]

**Venlafaxine → any antidepressant (Rule F):**
- Slow taper 2–4 weeks minimum; dose-calculated step-down [28, 87, 92, 93, 94]
- Highest discontinuation syndrome risk among all antidepressants [93]
- Start new medication at Week 2 of taper [28, 87]

**Duloxetine → any antidepressant (Rule G):**
- Slow taper 2–4 weeks minimum; dose-calculated step-down [28, 87, 92, 93]
- Start new medication at Week 2 of taper [28, 87]

**Bupropion → any antidepressant (Rule H):**
- Standard step-down taper over 1–2 weeks [28, 87]
- Start new medication at Week 2 [28, 87]

**Mirtazapine → any antidepressant (Rule I):**
- Standard step-down taper over 1–2 weeks [28, 87]
- Start new medication at Week 2 [28, 87]

**To or from MAOI:**
- SSRI, SNRI, or TCA to MAOI: 2-week washout minimum [28, 87, 89, 90]
- Fluoxetine to MAOI: 5-week washout required [28, 87]
- MAOI to any antidepressant: 2-week washout minimum [28, 87]
- Never overlap MAOIs with serotonergic agents — life-threatening serotonin syndrome
  risk [89, 90]

#### TAPERING ON DISCONTINUATION (no switch)

**Standard approaches [28, 94]:**
- Conservative: reduce by 25% every 4 weeks
- Moderate: reduce by 12.5% every 2 weeks
- Minimum duration: 2–4 weeks; extend to several months for high-risk medications

**Hyperbolic tapering — increasingly recommended [88, 95]:**
- Linear dose reductions cause exponential increases in serotonin transporter availability
  at receptors
- Hyperbolic taper reduces receptor-level effect by fixed amounts rather than fixed doses
- Example for paroxetine 40 mg: 40→30→20→10→5→2.5→1.25→0 mg, each step over 4 weeks

**High-risk medications requiring extended taper [28, 92, 93, 94]:**
- Paroxetine, venlafaxine, duloxetine, desvenlafaxine
- Abrupt discontinuation causes symptoms in 30–50% of patients
- Gradual taper reduces this to approximately 5%
- Symptom onset: 2–4 days after stopping (1–2 weeks for fluoxetine)
- Peak at 1–2 weeks; most resolve within 1 week but can persist months

2025 network meta-analysis: slow tapering combined with psychological support prevents
relapse similarly to antidepressant continuation and outperforms abrupt or fast
discontinuation under 4 weeks. Recommend MoodCalmer dCBT alongside all tapering.
[96, 97]

#### SEROTONIN SYNDROME

**Highest-risk combinations [89, 90, 91]:**
- MAOI + SSRI or SNRI — most dangerous
- SSRI or SNRI + tramadol or serotonergic opioids
- Paroxetine + tramadol — most common pharmacodynamic interaction
- Multiple serotonergic agents simultaneously

**Clinical triad [89, 90]:**
- Mental status changes: agitation, confusion
- Autonomic dysfunction: hyperthermia, tachycardia, diaphoresis
- Neuromuscular abnormalities: hyperreflexia, myoclonus, tremor

Note: serotonin syndrome can occur with a single serotonergic agent at normal doses in
approximately 40% of cases, most often fluoxetine or venlafaxine [91, 98]

**Patient education — FINISH mnemonic [28]:**
Flu-like symptoms, Insomnia, Nausea, Imbalance, Sensory disturbances, Hyperarousal

#### OUTPUT RULES

- When Step 7 routes a patient to a switch, include the appropriate switching protocol
  in the output based on the medication being discontinued
- When paroxetine, venlafaxine, duloxetine, or desvenlafaxine are being discontinued or
  switched from, flag extended taper requirement prominently in the output
- When the maintenance plan involves eventual discontinuation, include the appropriate
  taper schedule in the maintenance section
- Add serotonin syndrome warning to output whenever two or more serotonergic agents are
  present in current_medications

---

### Step 8: Treatment-Resistant Depression

TRD is now integrated into the class-based routing system (Step 7, Rules 3–5).
Citations: [104, 105, 108, 109, 110, 111]

- Rule 3 (SSRI + SNRI failed): soft TRD flag, psychiatric consultation recommended [104, 105]
- Rule 4 (SSRI + SNRI + NDRI/NaSSA failed): hard consultation required, TCA options
  pending psychiatric input [108, 109]
- Rule 5 (TCA failed, or PHQ ≥ 20 + suicidality, or psychosis): mandatory psychiatric
  referral, advanced interventions only (ECT, TMS, ketamine, esketamine) [110, 111]
- Reassess diagnostic accuracy, medication adherence, and comorbid conditions at every
  TRD escalation step [104, 105]

---

### Step 9: Maintenance Therapy

Citations: [2, 4, 18, 70, 71, 72]

- First episode: continue medication 6–9 months after remission [2, 4, 71]
- Recurrent episode: continue at least 2 years [18, 70, 71, 72]
- High relapse risk: consider extending indefinitely [2, 4]
- Taper slowly on discontinuation — especially paroxetine and venlafaxine (discontinuation
  syndrome risk) [25]

---

## Deviation Paths

### Pediatric Path (age < 18)

**Trigger:** age < 18
**Pathway rationale:** FDA approvals are limited in pediatric MDD; venlafaxine carries the
highest suicidality signal in this population; psychotherapy is preferred for mild-moderate
severity; black box warning applies to all antidepressants in patients under 25.
**Citations:** [5, 73, 74, 75, 76, 77]

**Medication order:**
1. Fluoxetine — FDA-approved for ages 8+; strongest evidence in pediatric MDD [75, 76]
2. Escitalopram — FDA-approved for ages 12+ [75, 76]
3. Sertraline — modest evidence; not FDA-approved for pediatric MDD but used off-label [75, 76]

**Contraindications within pediatric path:**
- Venlafaxine: contraindicated — highest suicidality signal in pediatric meta-analyses [75, 76, 77]
- Paroxetine: not recommended — unfavorable safety profile in this population [77]

**Psychotherapy:**
- Mild to moderate severity: psychotherapy preferred first-line over medication [5, 76]
- Add medication if psychotherapy fails or severity is moderate-severe

---

### Geriatric Path (age ≥ 65)

**Trigger:** age ≥ 65
**Pathway rationale:** Anticholinergic burden, falls risk, drug interactions, and QTc
sensitivity require specific exclusions and reduced dose ceilings.
**Citations:** [26, 27, 28]

**Medication exclusions:**
- Paroxetine: avoid — anticholinergic burden, falls risk [26, 28]
- Fluoxetine: avoid — drug interactions via CYP2D6, falls risk [26, 28]
- TCAs: avoid unless no other options — cardiac conduction risk, anticholinergic burden [78]

**Preferred medications:**
- Sertraline, escitalopram, duloxetine [28]

**Dose ceilings:**
- Citalopram: max 20 mg (QTc risk) [25, 27]
- Escitalopram: max 10 mg [27, 30]

---

### Pregnancy Path (antepartum)

**Trigger:** pregnant (add `trimester` variable)
**Pathway rationale:** Teratogenicity data and neonatal adaptation syndrome inform medication
selection; psychotherapy is preferred first-line.
**Citations:** [26, 28]

**Rules:**
- Psychotherapy preferred first-line [26, 28]
- Avoid: paroxetine — associated with cardiac malformations in first-trimester exposure [26, 28]
- Generally safe: sertraline, fluoxetine, citalopram, escitalopram [26, 28]

---

### Postpartum / Breastfeeding Path

**Trigger:** postpartum flag or breastfeeding flag
**Pathway rationale:** Infant exposure through breast milk differs by medication half-life
and protein binding.
**Citations:** [26, 28]

**Rules:**
- Preferred: sertraline — lowest breast milk transfer levels [26, 28]
- Avoid: fluoxetine — long half-life and active metabolite norfluoxetine accumulate in
  nursing infant [26, 28]

---

### Renal Impairment Path (eGFR < 60)

**Trigger:** eGFR < 60
**Pathway rationale:** Reduced renal clearance requires dose adjustments for renally-cleared
antidepressants.
**Citations:** [23, 83, 84]

**Dose adjustments:**
- eGFR ≥ 60: no adjustment for most antidepressants [83]
- eGFR 30–59: 25–50% dose reduction for venlafaxine and desvenlafaxine [23]
- eGFR < 30: 50% dose reduction [83]
- Hemodialysis: 50% dose reduction; administer dose after dialysis session [23]

---

### Hepatic Impairment Path

**Trigger:** hepatic impairment present (any severity)
**Pathway rationale:** Hepatic metabolism impairment affects clearance of most antidepressants;
some require avoidance rather than dose reduction.
**Citations:** [23, 30, 85, 86]

**Exclusions:**
- Duloxetine: avoid entirely — hepatotoxicity risk; do not dose-reduce, avoid completely [85, 86]
- Nefazodone: avoid [85]

**Dose adjustments:**
- Venlafaxine: 50% dose reduction [23]
- Citalopram: max 20 mg [30]
- Escitalopram: max 10 mg [30]
- All SSRIs: start at 50% of usual starting dose [85, 86]

---

### Cardiac Disease Path

**Trigger:** cardiac disease history, QTc > 450 ms, or concomitant QTc-prolonging medications
**Pathway rationale:** Arrhythmia risk, QTc prolongation, and post-MI safety data require
specific medication selection and ECG monitoring.
**Citations:** [27, 78, 79, 80, 81, 82]

**ECG baseline indicated if:**
- Age > 60 [78, 79]
- Cardiac disease history [78, 79]
- Concomitant QTc-prolonging medications [79]
- Electrolyte abnormalities [79]

**Rules:**
- QTc > 500 ms: avoid citalopram, escitalopram, TCAs [79, 81, 82]
- Cardiac disease present: prefer sertraline, fluoxetine — safest cardiac profile [27, 78]
- Avoid: TCAs, trazodone, nefazodone — arrhythmia risk [78]
- Venlafaxine: minimal QTc effect, acceptable with monitoring [79]
- Uncontrolled hypertension (SBP > 140 or DBP > 90): use SNRIs with caution [25]

**Citalopram-specific QTc rules:**
- > 40 mg: contraindicated (FDA black box) [25]
- > 20 mg: contraindicated if age > 60 [27]

**Escitalopram-specific QTc rules:**
- > 20 mg: caution for QTc prolongation [30]
- > 10 mg: caution if age > 60 [27]

---

### Anxiety Comorbidity Path

**Trigger:** anxiety comorbidity present
**Preferred:** SSRI or SNRI — no clear efficacy difference between them for this indication
**Citations:** [34]

---

### Chronic Pain / Fibromyalgia Path

**Trigger:** chronic pain or fibromyalgia comorbidity
**Pathway rationale:** SNRIs are FDA-approved for pain indications; SSRIs lack evidence for
pain outcomes and should not anchor the recommendation in this pathway.
**Citations:** [25, 29, 35]

**Medication order:**
1. Duloxetine — FDA-approved for fibromyalgia, diabetic neuropathy, chronic musculoskeletal
   pain [25, 29, 35]
2. Venlafaxine — second-line for pain [29, 35]
3. SSRIs — generally ineffective for pain; do not rank as preferred in this path [31, 35]

---

### Insomnia Path (prominent insomnia)

**Trigger:** insomnia_severity indicates prominent insomnia
**Rules:**
- Mirtazapine first-line only if prominent insomnia AND no obesity concern [25, 30]
- Alternative: trazodone (off-label for insomnia)
- If obesity present: do not use mirtazapine; consider alternative with less weight effect
**Citations:** [25, 30]

---

### Obesity Path (BMI ≥ 30)

**Trigger:** BMI ≥ 30
**Rules:**
- Avoid: mirtazapine (significant weight gain), paroxetine (significant weight gain) [25, 30]
- Preferred: bupropion (weight neutral or loss), fluoxetine (weight neutral or loss) [25]
**Citations:** [25, 30]

---

### Dementia Path

**Trigger:** dementia diagnosis present
**Rules:**
- Paroxetine specifically contraindicated — anticholinergic burden accelerates cognitive
  decline [26, 28]
- Avoid all high-anticholinergic agents
- All atypical antipsychotics carry increased mortality risk in elderly with dementia
  (FDA black box) — flag prominently if augmentation is considered
**Citations:** [26, 28]

---

### Severe Depression Path (PHQ ≥ 20)

**Trigger:** PHQ-9 ≥ 20
**Rules:**
- Combination therapy (medication + psychotherapy) required [26, 29]
- SNRI or SSRI both appropriate first-line [26]
- Flag for psychiatry referral consideration [26]
**Citations:** [3, 4, 26, 29]

---

## Contraindication Exclusion Map

When the algorithm excludes a medication, the output must state the reason and cite the source.

| Medication Excluded | Condition | Reason | Citations |
|---|---|---|---|
| All antidepressants (monotherapy) | Manic/hypomanic history | Can precipitate mania | [3, 4] |
| Paroxetine | Age ≥ 65 | Anticholinergic burden, falls | [26, 28] |
| Paroxetine | Dementia | Anticholinergic burden, cognitive decline | [26, 28] |
| Paroxetine | Pregnancy | Cardiac malformations (first trimester) | [26, 28] |
| Paroxetine | Pediatric | No FDA approval; unfavorable safety | [77] |
| Paroxetine | Obesity | Significant weight gain | [25, 30] |
| Fluoxetine | Age ≥ 65 | Drug interactions, falls risk | [26, 28] |
| Fluoxetine | Postpartum breastfeeding | Infant accumulation via breast milk | [26, 28] |
| Fluoxetine, paroxetine | Tamoxifen co-administration | CYP2D6 inhibition reduces tamoxifen efficacy | [30] |
| Venlafaxine | Pediatric | Highest suicidality signal in meta-analyses | [75, 76, 77] |
| Duloxetine | Hepatic impairment (any) | Hepatotoxicity; avoid entirely | [85, 86] |
| Citalopram > 40 mg | Any patient | FDA black box QTc | [25] |
| Citalopram > 20 mg | Age > 60 | QTc risk | [27] |
| Escitalopram > 10 mg | Age > 60 | QTc risk | [27, 30] |
| Citalopram, escitalopram, TCAs | QTc > 500 ms | Arrhythmia risk | [79, 81, 82] |
| TCAs, trazodone, nefazodone | Cardiac disease | Arrhythmia risk, cardiotoxicity | [78] |
| Mirtazapine, paroxetine | Obesity | Significant weight gain | [25, 30] |
| Fluvoxamine | MDD indication | Not FDA-approved for MDD — flag as off-label | [24, 25] |
| Nefazodone | Hepatic impairment | Hepatotoxic | [85] |

---

## Monitoring Schedule

Include in every output. Citations: [3, 4, 26, 73, 74]

| Timepoint | Action | Citations |
|---|---|---|
| Initiation | Baseline weight, BMI, BP (if augmenting with antipsychotic: lipids, HbA1c, ECG) | [3] |
| Week 2 | Assess tolerability and adherence | [26] |
| Week 4–6 | Dose adjustment if inadequate response | [26] |
| Week 8–12 | Full response assessment; switch if no response | [26] |
| Weeks 1–4 | Close suicidality monitoring — all patients; especially under 25 | [73, 74] |
| If antipsychotic added | BMI monthly x3 months then quarterly; BP, lipids, HbA1c at 3 months then annually | [3] |

---

## Output Format Instructions

Every output must follow this structure:

1. **Patient summary** — key inputs that drove routing decisions
2. **Pathway taken** — standard adult or deviation path name, trigger reason, citations
3. **Ranked medication list** — for each medication:
   - Name, starting dose, target dose range
   - Rationale (one sentence, active voice)
   - Inline citations
   - Any dose modifications applied and their reason with citations
4. **Medications excluded** — each excluded drug, reason, and citations
5. **Switching protocol** *(only when Step 7 routes to a switch)* — for each
   prior → new medication pair:
   - Prior medication: name (class)
   - New medication: name (class)
   - Method: direct switch / cross-taper / slow taper / washout
   - Duration: N/A or duration
   - Warning: warning text with citations (blank if none)
   - Safety flag (Section 2): serotonin syndrome warning when two or more
     serotonergic agents overlap, or when MAOI washout period is at risk, or
     when tramadol/serotonergic opioid is co-prescribed with SSRI/SNRI
6. **Augmentation plan** — if applicable, with trial number and citations
7. **Adjunctive options** — omega-3, COX-2 inhibitor if appropriate [60, 61, 62, 64, 65, 66]
8. **Monitoring schedule** — per table above with citations
9. **Maintenance plan** — duration based on episode history [2, 4, 18, 70, 71, 72]
10. **Full reference list** — only those cited in the output

---

## Citation Note

If a decision type is not covered in this CLAUDE.md, output [citation needed] and flag it
for the user to resolve. Do not infer or fabricate citation assignments.

---

## References


### Psychotherapy and General Management

1. Thase ME et al. Treatment of major depression with psychotherapy or psychotherapy-pharmacotherapy combinations. Arch Gen Psychiatry. 1997;54(11):1009-1015.
2. Depression in Adults: recognition and management. NICE. 2009.
3. APA Practice Guideline for the Treatment of Patients With Major Depressive Disorder. 3rd ed. 2010.
4. VA/DoD Clinical Practice Guidelines for the Management of Major Depressive Disorder. Version 3.0. 2016.
5. APA Clinical Practice Guideline for the Treatment of Depression Across Three Age Cohorts. 2019.
6. Clinical Practice Review for Major Depressive Disorder. Anxiety & Depression Association of America. 2020.
7. VA/DoD Clinical Practice Guidelines for the Management of Major Depressive Disorder. 2022. [Brockington R et al.]

### First-Line Pharmacotherapy — Efficacy and Comparative Evidence

8. Arroll B et al. Efficacy and tolerability of tricyclic antidepressants and SSRIs compared with placebo. Ann Fam Med. 2005;3(5):449-456.
9. Arroll B et al. Antidepressants versus placebo for depression in primary care. Cochrane Database Syst Rev. 2009(3):CD007954.
10. Cipriani A et al. Escitalopram versus other antidepressive agents for depression. Cochrane Database Syst Rev. 2009(2):CD006532.
11. Cipriani A et al. Comparative efficacy and acceptability of 12 new-generation antidepressants. Lancet. 2009;373(9665):746-758.
12. Cipriani A et al. Sertraline versus other antidepressive agents for depression. Cochrane Database Syst Rev. 2010(4):CD006117.
13. Gartlehner G et al. Comparative benefits and harms of second-generation antidepressants. Ann Intern Med. 2011;155(11):772-785.
14. Ramsberg J et al. Effectiveness and cost-effectiveness of antidepressants in primary care. PLoS One. 2012;7(8):e42003.
15. Magni LR et al. Fluoxetine versus other types of pharmacotherapy for depression. Cochrane Database Syst Rev. 2013(7):CD004185.
16. Maneeton N et al. Efficacy, tolerability, and acceptability of bupropion for major depressive disorder. Drug Des Devel Ther. 2013;7:1053-1062.
17. Khoo AL et al. Network Meta-Analysis and Cost-Effectiveness Analysis of New Generation Antidepressants. CNS Drugs. 2015;29(8):695-712.
18. Kennedy SH et al. CANMAT 2016 Clinical Guidelines: Section 3. Pharmacological Treatments. Can J Psychiatry. 2016;61(9):540-560.
19. Cipriani A et al. Comparative efficacy and acceptability of 21 antidepressant drugs for acute treatment of adults with MDD. Lancet. 2018;391(10128):1357-1366.
20. Andrade C. Relative Efficacy and Acceptability of Antidepressant Drugs: Commentary on network meta-analysis. J Clin Psychiatry. 2018;79(2):18f12254.
21. Gartlehner G et al. Nonpharmacologic and Pharmacologic Treatments of Adult Patients With MDD: Systematic Review for ACP Clinical Guideline. Ann Intern Med. 2023;176(2):196-211.

### Dosing and Optimal Dose Evidence

22. Furukawa TA et al. Optimal Dose of SSRIs, Venlafaxine, and Mirtazapine in Major Depression: dose-response meta-analysis. Lancet Psychiatry. 2019;6(7):601-609.
23. Venlafaxine. FDA Prescribing Information. Updated 2023-08-31.
24. FDA Orange Book. [FDA drug approvals and indications]

### Primary Care and General Clinical Reviews

25. Park LT, Zarate CA. Depression in the Primary Care Setting. N Engl J Med. 2019;380(6):559-568.
26. Simon GE, Moise N, Mohr DC. Management of Depression in Adults: A Review. JAMA. 2024;332(2):141-152.
27. Whooley MA. Diagnosis and Treatment of Depression in Adults With Comorbid Medical Conditions. JAMA. 2012;307(17):1848-57.
28. Kovich H, Kim W, Quaste AM. Pharmacologic Treatment of Depression. Am Fam Physician. 2023;107(2):173-181.
29. Coles S, Wise D. Management of Major Depressive Disorder in Adults: CANMAT Guidelines. Am Fam Physician. 2025;112(4):458-461.
30. National Comprehensive Cancer Network. Survivorship Guidelines. Updated 2026-02-02.

### SNRIs and Symptom-Driven Selection

31. Stahl SM et al. SNRIs: Pharmacology, Clinical Efficacy, and Tolerability. CNS Spectr. 2005;10(9):732-47.
32. Sakurai H et al. Pharmacological Management of Depression: Japanese Expert Consensus on symptom-driven selection. J Affect Disord. 2020;266:626-632.
33. Bartova L et al. Real-World Characteristics of European Patients Receiving SNRIs as First-Line Treatment. J Affect Disord. 2023;332:105-114.
34. Gosmann NP et al. SSRIs and SNRIs for Anxiety, OCD, and Stress Disorders: Network Meta-Analysis. PLoS Med. 2021;18(6):e1003664.

### Pain and Fibromyalgia

35. Ferreira GE et al. Efficacy, Safety, and Tolerability of Antidepressants for Pain in Adults: Overview of Systematic Reviews. BMJ. 2023;380:e072415.

### Switching and Augmentation — Core Trials

36. Rush AJ et al. Bupropion-SR, sertraline, or venlafaxine-XR after failure of SSRIs for depression (STAR*D). N Engl J Med. 2006;354(12):1231-1242.
37. Trivedi MH et al. Medication augmentation after the failure of SSRIs for depression (STAR*D). N Engl J Med. 2006;354(12):1243-1252.
38. Blier P et al. Combination of antidepressant medications from treatment initiation for MDD. Am J Psychiatry. 2010;167(3):281-288.
39. Gaynes BN et al. Treating depression after initial treatment failure: switch and augmenting strategies in STAR*D. J Clin Psychopharmacol. 2012;32(1):114-119.
40. Santaguida PL et al. Treatment for Depression After Unsatisfactory Response to SSRIs. AHRQ Comparative Effectiveness Reviews. 2012.
41. Henssler J et al. Combining Antidepressants vs Antidepressant Monotherapy for Acute Depression: Systematic Review and Meta-analysis. JAMA Psychiatry. 2022;79(4):300-312.
42. Pérez V et al. The DEPRE'5 Study: Treatment Strategies in MDD After Failed SSRI. Br J Psychiatry. 2025.

### Augmentation — Atypical Antipsychotics

43. Nuñez NA et al. Augmentation Strategies for Treatment Resistant Major Depression: Systematic Review and Network Meta-Analysis. J Affect Disord. 2022;302:385-400.
44. Yan Y et al. Efficacy and Acceptability of Second-Generation Antipsychotics With Antidepressants in Unipolar Depression Augmentation: Network Meta-Analysis. Psychological Medicine. 2022;52(12):2224-2231.
45. Gaddey HL, Mason B, Naik A. Depression: Managing Resistance and Partial Response to Treatment. Am Fam Physician. 2024;109(5):410-416.
46. Lenze EJ et al. Antidepressant Augmentation versus Switch in Treatment-Resistant Geriatric Depression (OPTIMUM trial). N Engl J Med. 2023;388(12):1067-1079.

### Augmentation — Lithium

47. Nelson JC et al. Lithium augmentation of tricyclic and second generation antidepressants in major depression. J Affect Disord. 2014;168:269-275.
48. Bauer M et al. Role of lithium augmentation in the management of major depressive disorder. CNS Drugs. 2014;28(4):331-342.
49. Kerr-Gaffney J et al. Clinical and Cost-Effectiveness of Lithium Versus Quetiapine Augmentation for TRD: LQD Trial. Health Technology Assessment. 2025;29(12):1-118.
50. Cleare AJ et al. Clinical and Cost-Effectiveness of Lithium Versus Quetiapine Augmentation: LQD RCT. Lancet Psychiatry. 2025;12(4):276-288.

### Treatment-Resistant Depression

51. Davies P et al. Pharmacological Interventions for Treatment-Resistant Depression in Adults. Cochrane Database Syst Rev. 2019;12:CD010557.
52. Arnold MJ, Fulleborn S, Farrell J. Medications for Treatment-Resistant Depression in Adults. Am Fam Physician. 2021;103(1):16-18.
53. Ruberto VL, Jha MK, Murrough JW. Pharmacological Treatments for Patients With Treatment-Resistant Depression. Pharmaceuticals. 2020;13(6):E116.
54. Steffens DC. Treatment-Resistant Depression in Older Adults. N Engl J Med. 2024;390(7):630-639.
55. Giakoumatos CI, Osser D. The Psychopharmacology Algorithm Project at Harvard South Shore: Update on Unipolar Nonpsychotic Depression. Harvard Review of Psychiatry. 2019;27(1):33-52.

### Stimulants for Residual Symptoms

56. Bahji A, Mesbah-Oskui L. Comparative Efficacy and Safety of Stimulant-Type Medications for Depression: Network Meta-Analysis. J Affect Disord. 2021;292:416-423.
57. McIntyre RS et al. The Efficacy of Psychostimulants in Major Depressive Episodes: Systematic Review and Meta-Analysis. J Clin Psychopharmacol. 2017;37(4):412-418.
58. Candy M et al. Psychostimulants for Depression. Cochrane Database Syst Rev. 2008;(2):CD006722.
59. Corp SA et al. A Review of the Use of Stimulants in Treating Bipolar Depression and MDD. J Clin Psychiatry. 2014;75(9):1010-8.

### Adjunctive — Anti-inflammatory

60. Köhler O et al. Effect of Anti-inflammatory Treatment on Depression: Systematic Review and Meta-analysis of RCTs. JAMA Psychiatry. 2014;71(12):1381-1391.
61. Bai S et al. Efficacy and Safety of Anti-inflammatory Agents for MDD: Systematic Review and Meta-Analysis. J Neurol Neurosurg Psychiatry. 2020;91(1):21-32.
62. Faridhosseini F et al. Celecoxib: a new augmentation strategy for depressive mood episodes. Hum Psychopharmacol. 2014;29(3):216-223.
63. Gędek A et al. Celecoxib for Mood Disorders: Systematic Review and Meta-Analysis of RCTs. J Clin Med. 2023;12(10):3497.

### Adjunctive — Omega-3

64. Liao Y et al. Efficacy of omega-3 PUFAs in depression: A meta-analysis. Transl Psychiatry. 2019;9(1):190.
65. Mocking RJ et al. Meta-analysis and meta-regression of omega-3 supplementation for MDD. Transl Psychiatry. 2016;6(3):e756.
66. Ravindran AV et al. CANMAT 2016 Guidelines: Section 5. Complementary and Alternative Medicine. Can J Psychiatry. 2016;61(9):576-587.
67. Appleton KM et al. Omega-3 Fatty Acids for Depression in Adults. Cochrane Database Syst Rev. 2021;11:CD004692.
68. Norouziasl R et al. Efficacy and Safety of N-3 Fatty Acids for Depression: Dose-Response Meta-Analysis. Br J Nutr. 2024;131(4):658-671.
69. Okereke OI et al. Long-term Supplementation With Marine Omega-3 Fatty Acids vs Placebo on Risk of Depression. JAMA. 2021;326(23):2385-2394.

### Maintenance Therapy

70. Trivedi MH et al. Psychosocial outcomes during 2 years of maintenance treatment with venlafaxine ER. J Affect Disord. 2010;126(3):420-429.
71. Borges S et al. Review of maintenance trials for MDD: a 25-year perspective from the FDA. J Clin Psychiatry. 2014;75(3):205-214.
72. Baldessarini RJ et al. Duration of initial antidepressant treatment and subsequent relapse. J Clin Psychopharmacol. 2015;35(1):75-76.

### Pediatric Depression

73. US Preventive Services Task Force. Screening for Depression and Suicide Risk in Children and Adolescents. JAMA. 2022;328(15):1534-1542.
74. Miller L, Campo JV. Depression in Adolescents. N Engl J Med. 2021;385(5):445-449.
75. Hetrick SE et al. New Generation Antidepressants for Depression in Children and Adolescents. Cochrane Database Syst Rev. 2021;5:CD013674.
76. Cipriani A et al. Comparative Efficacy and Tolerability of Antidepressants in Children and Adolescents. Lancet. 2016;388(10047):881-90.
77. Thapar A et al. Depression in Young People. Lancet. 2022;400(10352):617-631.

### Cardiac Safety and QTc

78. Jha MK et al. Screening and Management of Depression in Patients With Cardiovascular Disease. J Am Coll Cardiol. 2019;73(14):1827-1845.
79. Giraud EL et al. QT Interval Prolongation Potential of Anticancer and Supportive Drugs. Lancet Oncol. 2022;23(9):e406-e415.
80. Cao S et al. Arrhythmic Events With Antidepressants: FDA FAERS Analysis. Front Psychiatry. 2025;16:1637471.
81. Castro VM et al. QT Interval and Antidepressant Use: Cross Sectional Study. BMJ. 2013;346:f288.
82. Beach SR et al. Meta-Analysis of SSRI-Associated QTc Prolongation. J Clin Psychiatry. 2014;75(5):e441-9.

### Renal Impairment

83. Nagler EV et al. Antidepressants for Depression in Stage 3-5 Chronic Kidney Disease: ERBP Recommendations. Nephrol Dial Transplant. 2012;27(10):3736-45.
84. KDIGO 2024 Clinical Practice Guideline for the Evaluation and Management of Chronic Kidney Disease. Kidney International. 2024;105(4S):S117-S314.

### Hepatic Impairment

85. Mullish BH et al. Depression and Antidepressants in Patients With Chronic Liver Disease or Liver Transplantation. Aliment Pharmacol Ther. 2014;40(8):880-92.
86. Mauri MC et al. Pharmacokinetics of Antidepressants in Patients With Hepatic Impairment. Clin Pharmacokinet. 2014;53(12):1069-81.

### Switching and Class-Based Routing

102. Papakostas GI, Fava M, Thase ME. Treatment of SSRI-resistant Depression: Meta-Analysis Comparing Within- Versus Across-Class Switches. Biol Psychiatry. 2008;63(7):699-704.
103. Pérez V et al. The DEPRE'5 Study: Pragmatic RCT Comparing Treatment Strategies in Major Depression After Failed SSRI Treatment. Br J Psychiatry. 2025.
104. McIntyre RS et al. Treatment-Resistant Depression: Definition, Prevalence, Detection, Management, and Investigational Interventions. World Psychiatry. 2023;22(3):394-412.
105. Steffens DC. Treatment-Resistant Depression in Older Adults. N Engl J Med. 2024;390(7):630-639.
106. Strobl EV. Consistent Differential Effects of Bupropion and Mirtazapine in Major Depression. J Affect Disord. 2025;388:119551.
107. Watanabe N et al. Mirtazapine Versus Other Antidepressive Agents for Depression. Cochrane Database Syst Rev. 2011;(12):CD006528.
108. Potter WZ, Rudorfer MV, Manji H. The Pharmacologic Treatment of Depression. N Engl J Med. 1991;325(9):633-42.
109. Gaddey HL, Mason B, Naik A. Depression: Managing Resistance and Partial Response to Treatment. Am Fam Physician. 2024;109(5):410-416.
110. Anand A et al. Ketamine versus ECT for Nonpsychotic Treatment-Resistant Major Depression. N Engl J Med. 2023;388(25):2315-2325.
111. Marques MG et al. Next-Step Treatment Options for Treatment-Resistant Depression: Mayo Clinic Depression Center Panel. J Clin Psychiatry. 2026;87(1):25cs16066.
112. Horowitz MA, Taylor D. Tapering of SSRI Treatment to Mitigate Withdrawal Symptoms. Lancet Psychiatry. 2019;6(6):538-546.
113. Van Leeuwen E et al. Tapering Antidepressants Combined with Psychological Support vs Continuation: A Network Meta-Analysis. JAMA Psychiatry. 2024;81(9):869-878.
114. Perahia DG et al. Switching to Duloxetine from Selective Serotonin Reuptake Inhibitor Antidepressants: A Multicenter Trial Comparing 2 Switching Techniques. J Clin Psychiatry. 2008;69(1):95-105.
