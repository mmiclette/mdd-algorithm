# ============================================================
# Cell 1 — Depression (MDD) Algorithm: full notebook-ready code
#        Multi-path routing per Step 2 of CLAUDE_MDD.md
# ============================================================
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Literal, Optional, Set, Tuple

from pathlib import Path
import re

from pydantic import BaseModel, Field, field_validator


# ------------------------------------------------------------
# 1) Medication Knowledge Base (KB)
# ------------------------------------------------------------
MedicationKey = str

MED_KB: Dict[MedicationKey, Dict[str, Any]] = {
    # --- SSRIs ---
    "fluoxetine": {
        "display": "Fluoxetine (Prozac)",
        "class": "SSRI",
        "start_dose": "10–20 mg daily",
        "dose_range": "20–80 mg daily",
        "titration": "Increase by 10–20 mg every 1–2 weeks as tolerated; reassess at 6 weeks.",
        "monitoring": [],
        "bp_message_relevant": False,
        "qt_risk": "none",
    },
    "sertraline": {
        "display": "Sertraline (Zoloft)",
        "class": "SSRI",
        "start_dose": "25–50 mg daily",
        "dose_range": "50–200 mg daily",
        "titration": "Increase by 25–50 mg every 1–2 weeks as tolerated; reassess at 6 weeks.",
        "monitoring": [],
        "bp_message_relevant": False,
        "qt_risk": "none",
    },
    "escitalopram": {
        "display": "Escitalopram (Lexapro)",
        "class": "SSRI",
        "start_dose": "5–10 mg daily",
        "dose_range": "10–20 mg daily",
        "titration": "Increase by 5–10 mg every 1–2 weeks as tolerated; reassess at 6 weeks.",
        "monitoring": [],
        "bp_message_relevant": False,
        "qt_risk": "possible",
    },
    "citalopram": {
        "display": "Citalopram (Celexa)",
        "class": "SSRI",
        "start_dose": "10–20 mg daily",
        "dose_range": "20–40 mg daily",
        "titration": "Increase by 10–20 mg every 1–2 weeks as tolerated; reassess at 6 weeks.",
        "monitoring": [],
        "bp_message_relevant": False,
        "qt_risk": "known",
    },
    "paroxetine": {
        "display": "Paroxetine (Paxil)",
        "class": "SSRI",
        "start_dose": "10–20 mg daily",
        "dose_range": "20–50 mg daily",
        "titration": "Increase by 10 mg every 1–2 weeks as tolerated; reassess at 6 weeks.",
        "monitoring": [],
        "bp_message_relevant": False,
        "qt_risk": "none",
    },
    "fluvoxamine": {
        "display": "Fluvoxamine (Luvox) [off-label for MDD — 25, 24]",
        "class": "SSRI",
        "start_dose": "50 mg daily",
        "dose_range": "100–300 mg daily",
        "titration": "Increase by 50 mg every 1–2 weeks as tolerated; reassess at 6 weeks.",
        "monitoring": [],
        "bp_message_relevant": False,
        "qt_risk": "none",
    },
    # --- SNRIs ---
    "venlafaxine_xr": {
        "display": "Venlafaxine XR (Effexor XR)",
        "class": "SNRI",
        "start_dose": "37.5–75 mg daily",
        "dose_range": "75–225 mg daily",
        "titration": "Increase by 37.5–75 mg every 1–2 weeks as tolerated; reassess at 6 weeks.",
        "monitoring": ["BP check before prescribing; monitor BP during titration."],
        "bp_message_relevant": True,
        "qt_risk": "none",
    },
    "duloxetine": {
        "display": "Duloxetine (Cymbalta)",
        "class": "SNRI",
        "start_dose": "30–40 mg daily",
        "dose_range": "60 mg daily",
        "titration": "Increase to 60 mg after 1–2 weeks if tolerated; reassess at 6 weeks. Max 60 mg/day [22].",
        "monitoring": ["BP check before prescribing; monitor BP during titration."],
        "bp_message_relevant": True,
        "qt_risk": "none",
    },
    "desvenlafaxine": {
        "display": "Desvenlafaxine (Pristiq)",
        "class": "SNRI",
        "start_dose": "50 mg daily",
        "dose_range": "50–100 mg daily",
        "titration": "Increase by 50 mg as needed; reassess at 6 weeks.",
        "monitoring": ["BP check before prescribing; monitor BP during titration."],
        "bp_message_relevant": True,
        "qt_risk": "none",
    },
    "levomilnacipran_er": {
        "display": "Levomilnacipran ER (Fetzima)",
        "class": "SNRI",
        "start_dose": "20 mg daily",
        "dose_range": "40–120 mg daily",
        "titration": "Increase by 20–40 mg every 1–2 weeks as tolerated; reassess at 6 weeks.",
        "monitoring": ["BP check before prescribing; monitor BP during titration."],
        "bp_message_relevant": True,
        "qt_risk": "none",
    },
    # --- Other antidepressants ---
    "bupropion_xl": {
        "display": "Bupropion XL (Wellbutrin XL)",
        "class": "NDRI",
        "start_dose": "150 mg daily",
        "dose_range": "150–450 mg daily",
        "titration": "Increase to 300 mg daily after 3–7 days if tolerated; max 450 mg daily.",
        "monitoring": ["BP check before prescribing; monitor BP during titration."],
        "bp_message_relevant": True,
        "qt_risk": "none",
    },
    "mirtazapine": {
        "display": "Mirtazapine (Remeron)",
        "class": "NaSSA",
        "start_dose": "15 mg nightly",
        "dose_range": "15–45 mg nightly",
        "titration": "Increase by 15 mg every 1–2 weeks as tolerated; reassess at 6 weeks.",
        "monitoring": [],
        "bp_message_relevant": False,
        "qt_risk": "none",
    },
    "vortioxetine": {
        "display": "Vortioxetine (Trintellix)",
        "class": "Other",
        "start_dose": "10 mg daily",
        "dose_range": "10–20 mg daily",
        "titration": "Increase to 20 mg after 1–2 weeks if tolerated; reassess at 6 weeks.",
        "monitoring": [],
        "bp_message_relevant": False,
        "qt_risk": "none",
    },
    "vilazodone": {
        "display": "Vilazodone (Viibryd)",
        "class": "Other",
        "start_dose": "10 mg daily",
        "dose_range": "20–40 mg daily",
        "titration": "Increase to 20 mg after 1 week, then 40 mg after another week if tolerated.",
        "monitoring": [],
        "bp_message_relevant": False,
        "qt_risk": "none",
    },
    # --- Augmentation ---
    "aripiprazole": {
        "display": "Aripiprazole (Abilify) — augmentation",
        "class": "SGA",
        "start_dose": "2–5 mg daily",
        "dose_range": "2–15 mg daily",
        "titration": "Increase by 2–5 mg every 1–2 weeks as needed/tolerated; reassess at 6 weeks.",
        "monitoring": ["Metabolic monitoring (weight/BMI, BP, lipids, glucose/A1c) per local protocol."],
        "bp_message_relevant": False,
        "qt_risk": "none",
    },
    "lithium": {
        "display": "Lithium — augmentation",
        "class": "Augment",
        "start_dose": "Clinician-managed",
        "dose_range": "Target 0.6–1.2 mEq/L (0.3–0.6 mmol/L in older adults) [54]",
        "titration": "Requires individualized titration with serum level monitoring.",
        "monitoring": ["Baseline and ongoing: Li+ level, TSH, BMP. Check at initiation, 1–2 months, then every 6–12 months [54]."],
        "bp_message_relevant": False,
        "qt_risk": "none",
    },
    "brexpiprazole": {
        "display": "Brexpiprazole (Rexulti) — augmentation",
        "class": "SGA",
        "start_dose": "0.5–1 mg daily",
        "dose_range": "1–3 mg daily",
        "titration": "Titrate weekly as tolerated; reassess at 6 weeks [44].",
        "monitoring": ["Metabolic monitoring (weight/BMI, BP, lipids, glucose/A1c) at initiation, 3 months, then annually."],
        "bp_message_relevant": False,
        "qt_risk": "none",
    },
    "quetiapine": {
        "display": "Quetiapine XR (Seroquel XR) — augmentation",
        "class": "SGA",
        "start_dose": "50 mg nightly",
        "dose_range": "150–300 mg/day",
        "titration": "Titrate every 1–2 weeks toward 150–300 mg/day; sedation common at initiation [44, 54].",
        "monitoring": ["Metabolic monitoring (weight/BMI, BP, lipids, glucose/A1c) at initiation, 3 months, then annually."],
        "bp_message_relevant": False,
        "qt_risk": "moderate",
    },
    "cariprazine": {
        "display": "Cariprazine (Vraylar) — augmentation",
        "class": "SGA",
        "start_dose": "0.5 mg daily",
        "dose_range": "1.5–3 mg daily",
        "titration": "Titrate weekly; slow titration reduces akathisia risk [44].",
        "monitoring": ["Metabolic monitoring (weight/BMI, BP, lipids, glucose/A1c) at initiation, 3 months, then annually."],
        "bp_message_relevant": False,
        "qt_risk": "none",
    },
    "risperidone": {
        "display": "Risperidone — augmentation",
        "class": "SGA",
        "start_dose": "0.25–0.5 mg daily",
        "dose_range": "0.5–2 mg daily",
        "titration": "Titrate gradually; monitor for EPS and hyperprolactinemia [44].",
        "monitoring": ["Metabolic monitoring; monitor for EPS, hyperprolactinemia."],
        "bp_message_relevant": False,
        "qt_risk": "low",
    },
    "olanzapine": {
        "display": "Olanzapine — augmentation",
        "class": "SGA",
        "start_dose": "2.5–5 mg daily",
        "dose_range": "5–20 mg daily",
        "titration": "Titrate as tolerated; olanzapine/fluoxetine combination pill (Symbyax) available [44].",
        "monitoring": ["Metabolic monitoring required — significant weight gain and metabolic risk."],
        "bp_message_relevant": False,
        "qt_risk": "none",
    },
    "methylphenidate": {
        "display": "Methylphenidate — augmentation (residual anergia only)",
        "class": "Stimulant",
        "start_dose": "5–10 mg twice daily",
        "dose_range": "10–60 mg/day",
        "titration": "Titrate weekly; limited evidence in MDD augmentation; use only for prominent residual anergia [3, 52].",
        "monitoring": ["Monitor HR, BP; assess for abuse potential."],
        "bp_message_relevant": True,
        "qt_risk": "none",
    },
    "lurasidone": {
        "display": "Lurasidone (Latuda) — augmentation",
        "class": "SGA",
        "start_dose": "20–40 mg/day",
        "dose_range": "20–80 mg/day",
        "titration": "Titrate as tolerated; limited evidence in unipolar depression; most data in bipolar — use cautiously [43].",
        "monitoring": ["Metabolic monitoring (weight/BMI, BP, lipids, glucose/A1c) at initiation, 3 months, then annually."],
        "bp_message_relevant": False,
        "qt_risk": "none",
    },
    "lisdexamfetamine": {
        "display": "Lisdexamfetamine (Vyvanse) — augmentation [OFF-LABEL for MDD]",
        "class": "Stimulant",
        "start_dose": "20–30 mg daily",
        "dose_range": "20–70 mg/day",
        "titration": "Titrate weekly; FDA-approved for binge eating disorder only — off-label for MDD. One positive RCT for augmentation [43, 59].",
        "monitoring": ["Monitor HR, BP; assess for abuse potential; document off-label use."],
        "bp_message_relevant": True,
        "qt_risk": "none",
    },
    # --- TCAs (require psychiatric consultation — Rule 4) ---
    "nortriptyline": {
        "display": "Nortriptyline (Pamelor)",
        "class": "TCA",
        "start_dose": "25 mg daily",
        "dose_range": "100–150 mg/day",
        "titration": "Titrate by 25 mg every 3–7 days; plasma level target 50–150 ng/mL. ECG at baseline and each dose increase [108].",
        "monitoring": ["ECG at baseline and each dose increase [108].", "Plasma levels: target 50–150 ng/mL [108]."],
        "bp_message_relevant": False,
        "qt_risk": "known",
    },
    "desipramine": {
        "display": "Desipramine (Norpramin)",
        "class": "TCA",
        "start_dose": "25–50 mg daily",
        "dose_range": "100–300 mg/day",
        "titration": "Titrate by 25–50 mg every 3–7 days; plasma levels required. ECG at baseline and each dose increase [108].",
        "monitoring": ["ECG at baseline and each dose increase [108].", "Plasma levels required [108]."],
        "bp_message_relevant": False,
        "qt_risk": "known",
    },
}

DOSE_STEPS_MG: Dict[str, List[float]] = {
    "sertraline":       [25, 50, 100, 150, 200],
    "escitalopram":     [5, 10, 20],
    "fluoxetine":       [10, 20, 40, 60, 80],
    "citalopram":       [10, 20, 40],
    "paroxetine":       [10, 20, 30, 40, 50],
    "fluvoxamine":      [50, 100, 150, 200, 300],
    "venlafaxine_xr":   [37.5, 75, 150, 225],
    "duloxetine":       [30, 60],
    "desvenlafaxine":   [50, 100],
    "levomilnacipran_er": [20, 40, 80, 120],
    "bupropion_xl":     [150, 300, 450],
    "mirtazapine":      [15, 30, 45],
    "vortioxetine":     [10, 20],
    "vilazodone":       [10, 20, 40],
    "aripiprazole":     [2, 5, 10, 15],
    "brexpiprazole":    [0.5, 1, 2, 3],
    "quetiapine":       [50, 100, 150, 200, 300],
    "cariprazine":      [0.5, 1.5, 3],
    "risperidone":      [0.25, 0.5, 1, 2],
    "olanzapine":       [2.5, 5, 10, 15, 20],
    "methylphenidate":  [5, 10, 20, 30, 40, 60],
    "lurasidone":       [20, 40, 60, 80],
    "lisdexamfetamine": [20, 30, 40, 50, 60, 70],
    "nortriptyline":    [25, 50, 75, 100, 150],
    "desipramine":      [25, 50, 100, 150, 200, 300],
}

DOSE_MIN_MAX_MG: Dict[str, Tuple[float, float]] = {
    "sertraline":         (25, 200),
    "escitalopram":       (5, 20),
    "fluoxetine":         (10, 80),
    "citalopram":         (10, 40),
    "paroxetine":         (10, 50),
    "fluvoxamine":        (50, 300),
    "venlafaxine_xr":     (37.5, 225),
    "duloxetine":         (30, 60),
    "desvenlafaxine":     (50, 100),
    "levomilnacipran_er": (20, 120),
    "bupropion_xl":       (150, 450),
    "mirtazapine":        (15, 45),
    "vortioxetine":       (10, 20),
    "vilazodone":         (10, 40),
    "aripiprazole":       (2, 15),
    "brexpiprazole":      (0.5, 3),
    "quetiapine":         (50, 300),
    "cariprazine":        (0.5, 3),
    "risperidone":        (0.25, 2),
    "olanzapine":         (2.5, 20),
    "methylphenidate":    (5, 60),
    "lurasidone":         (20, 80),
    "lisdexamfetamine":   (20, 70),
    "nortriptyline":      (25, 150),
    "desipramine":        (25, 300),
}

# Renal dose caps (CrCl/eGFR bucket-based)
RENAL_MAX_CAPS_MG: Dict[str, Dict[str, float]] = {
    "sertraline":     {">60": 200,   "30-60": 200,   "15-29": 150,   "<15": 100},
    "venlafaxine_xr": {">60": 225,   "30-60": 112.5, "15-29": 112.5, "<15": 75},
    "bupropion_xl":   {">60": 450,   "30-60": 300,   "15-29": 150,   "<15": 150},
}

def dose_out_of_range(med_key: str, dose_mg: float, max_cap_override: Optional[float] = None) -> bool:
    if med_key not in DOSE_MIN_MAX_MG:
        return False
    mn, mx = DOSE_MIN_MAX_MG[med_key]
    if max_cap_override is not None:
        mx = min(mx, float(max_cap_override))
    return dose_mg < mn or dose_mg > mx

def next_dose_step(med_key: str, current_dose_mg: float, cap_override: Optional[float] = None) -> str:
    if med_key in DOSE_MIN_MAX_MG:
        mn, mx = DOSE_MIN_MAX_MG[med_key]
        if cap_override is not None:
            mx = min(mx, float(cap_override))
        if current_dose_mg > mx:
            return f"Current dose ({current_dose_mg} mg) exceeds max cap ({mx} mg)—do not increase; clinician review."
        if current_dose_mg < mn:
            return f"Current dose ({current_dose_mg} mg) below typical min ({mn} mg)—verify dosing; clinician review."
    steps = DOSE_STEPS_MG.get(med_key, [])
    if not steps:
        return "Increase dose per standard titration schedule."
    if cap_override is not None:
        steps = [s for s in steps if s <= float(cap_override)]
        if not steps:
            return "Dose cap prevents further titration—clinician review."
    for s in steps:
        if s > current_dose_mg:
            return f"Increase dose to {s} mg daily (next step), if tolerated."
    return "Already at max dose (or max cap)—do not increase; consider augmentation or switch per algorithm."


# ------------------------------------------------------------
# 2) Medication safety screening
# ------------------------------------------------------------
def _norm(s: str) -> str:
    s = str(s or "").strip().lower()
    for ch in [",", ";", ":", "(", ")", "[", "]", "{", "}", "/", "\\", "|", '"', "'"]:
        s = s.replace(ch, " ")
    return " ".join(s.split())

def _any_match(patient_meds_norm: Set[str], synonyms: List[str]) -> bool:
    syn_norm = [_norm(x) for x in synonyms]
    for pm in patient_meds_norm:
        for sn in syn_norm:
            if sn and (pm == sn or sn in pm):
                return True
    return False

MAOI_SYNONYMS = [
    "phenelzine", "nardil", "tranylcypromine", "parnate", "isocarboxazid", "marplan",
    "selegiline", "eldepryl", "zelapar", "emsam", "selegiline patch", "selegiline transdermal",
    "rasagiline", "azilect", "linezolid", "zyvox", "methylene blue", "methylthioninium",
]
SEROTONERGIC_SYNONYMS = [
    "sumatriptan", "imitrex", "rizatriptan", "maxalt", "zolmitriptan", "zomig",
    "naratriptan", "amerge", "almotriptan", "axert", "eletriptan", "relpax", "frovatriptan", "frova",
    "tramadol", "ultram", "tapentadol", "nucynta", "meperidine", "demerol", "fentanyl", "methadone",
    "lithium", "lithobid", "eskalith", "buspirone", "buspar",
    "st johns wort", "st. john's wort", "hypericum", "same", "s-adenosylmethionine", "tryptophan",
]
BLEEDING_RISK_SYNONYMS = [
    "warfarin", "coumadin", "apixaban", "eliquis", "rivaroxaban", "xarelto",
    "dabigatran", "pradaxa", "edoxaban", "savaysa", "aspirin", "asa",
    "clopidogrel", "plavix", "ticagrelor", "brilinta", "prasugrel", "effient",
    "ibuprofen", "advil", "motrin", "naproxen", "aleve", "diclofenac", "voltaren", "ketorolac", "toradol",
]
QT_PROLONGING_SYNONYMS = [
    "ondansetron", "zofran", "droperidol", "amiodarone", "cordarone",
    "sotalol", "betapace", "dofetilide", "tikosyn", "quinidine", "procainamide",
    "azithromycin", "zithromax", "clarithromycin", "biaxin", "erythromycin",
    "levofloxacin", "levaquin", "moxifloxacin", "avelox",
    "ziprasidone", "geodon", "haloperidol", "haldol", "quetiapine", "seroquel",
    "chlorpromazine", "thorazine", "thioridazine", "mellaril", "pimozide", "orap",
    "hydroxychloroquine", "plaquenil", "methadone",
]
BP_RISK_SYNONYMS = [
    "amphetamine", "adderall", "dextroamphetamine", "dexedrine",
    "lisdexamfetamine", "vyvanse", "methylphenidate", "ritalin", "concerta",
    "midodrine", "proamatine", "fludrocortisone", "florinef",
    "pseudoephedrine", "sudafed", "phenylephrine",
]
SEIZURE_RISK_SYNONYMS = [
    "tramadol", "ultram", "theophylline", "clozapine", "clozaril",
    "prednisone", "methylprednisolone", "dexamethasone", "hydrocortisone",
    "amphetamine", "adderall", "dextroamphetamine", "dexedrine",
    "lisdexamfetamine", "vyvanse", "methylphenidate", "ritalin", "concerta",
]

@dataclass
class MedSafetyResult:
    blocked: Set[str]
    warnings: List[str]
    detected: Dict[str, List[str]]

def medication_safety_screen(patient_medications: List[str], candidate_meds: List[str]) -> MedSafetyResult:
    pm_norm = {_norm(m) for m in (patient_medications or []) if str(m).strip()}
    blocked: Set[str] = set()
    warnings: List[str] = []
    detected: Dict[str, List[str]] = {}

    has_maoi       = _any_match(pm_norm, MAOI_SYNONYMS)
    has_serotonergic = _any_match(pm_norm, SEROTONERGIC_SYNONYMS)
    has_bleed      = _any_match(pm_norm, BLEEDING_RISK_SYNONYMS)
    has_qt         = _any_match(pm_norm, QT_PROLONGING_SYNONYMS)
    has_bp_risk    = _any_match(pm_norm, BP_RISK_SYNONYMS)
    has_seizure    = _any_match(pm_norm, SEIZURE_RISK_SYNONYMS)

    if has_maoi:
        for cm in candidate_meds:
            if cm in MED_KB and MED_KB[cm]["class"] in {"SSRI", "SNRI", "Other", "NDRI", "NaSSA"}:
                blocked.add(cm)
        warnings.append("MAOI (or MAOI-like agent) detected: antidepressant initiation contraindicated. Route to clinician review.")
        detected["maoi_signal"] = ["present"]
    if has_serotonergic:
        warnings.append("Serotonergic co-med detected: monitor for serotonin syndrome; avoid stacking serotonergic agents.")
        detected["serotonergic_signal"] = ["present"]
    if has_bleed:
        warnings.append("Bleeding-risk medication detected (anticoagulant/antiplatelet/NSAID): SSRIs/SNRIs may increase bleeding risk.")
        detected["bleeding_signal"] = ["present"]
    if has_qt:
        warnings.append("QT-prolonging co-med detected: consider ECG review where clinically indicated.")
        detected["qt_signal"] = ["present"]
    if has_bp_risk:
        warnings.append("BP-elevating co-med detected: check and monitor BP during titration.")
        detected["bp_signal"] = ["present"]
    if has_seizure:
        warnings.append("Seizure-threshold-lowering factor detected: use caution with bupropion if considered.")
        detected["seizure_signal"] = ["present"]

    return MedSafetyResult(blocked=blocked, warnings=warnings, detected=detected)


# ------------------------------------------------------------
# 3) Data models
# ------------------------------------------------------------
ManiaScreen = Literal["positive", "negative", "unknown"]

# All recognised deviation path names (Step 2 of CLAUDE_MDD.md).
# A single patient may be on multiple paths simultaneously.
PathwayName = Literal[
    "peds", "antepartum", "postpartum",
    "renal", "hepatic", "cardiac",
    "geriatric", "obesity", "dementia",
    "pain", "insomnia",
    "adult",
]

RecommendationIntent = Literal[
    "start", "continue", "increase", "switch_to", "augment_with", "monitor_only",
]

class PriorTrial(BaseModel):
    medication_key: str
    outcome: Literal["remission_or_response", "partial", "no_response", "intolerant", "unknown"] = "unknown"

    @field_validator("medication_key")
    @classmethod
    def normalize_med_key(cls, v: str) -> str:
        return (v or "").strip().lower()

class PatientInput(BaseModel):
    # Core
    age: int = Field(..., ge=0, le=130)
    phq_current: int = Field(..., ge=0, le=27)
    mania_screen: ManiaScreen = "unknown"
    current_medications: List[str] = Field(default_factory=list)

    # Follow-up / episode
    baseline_phq: Optional[int] = Field(default=None, ge=0, le=27)
    weeks_on_current_antidepressant: Optional[int] = Field(default=None, ge=0, le=400)
    current_antidepressant_key: Optional[str] = None
    current_dose_mg: Optional[float] = Field(default=None, ge=0, le=2000)
    trial_number: Optional[int] = Field(default=None, ge=1, le=3)
    is_augmented: bool = False
    weeks_since_augmentation: Optional[int] = Field(default=None, ge=0, le=400)
    prior_trials: List[PriorTrial] = Field(default_factory=list)

    # Vitals
    bp_systolic: Optional[int] = Field(default=None, ge=50, le=260)
    bp_diastolic: Optional[int] = Field(default=None, ge=30, le=160)

    # Renal
    crcl_ml_min: Optional[float] = Field(default=None, ge=0, le=300)
    egfr_ml_min_1_73: Optional[float] = Field(default=None, ge=0, le=300)

    # Hepatic
    hepatic_impairment: bool = False
    child_pugh: Optional[Literal["A", "B", "C"]] = None

    # Cardiac/QT
    qtc_ms: Optional[int] = Field(default=None, ge=200, le=800)
    cardiac_history: bool = False

    # Perinatal
    pregnant: bool = False
    postpartum_days: Optional[int] = Field(default=None, ge=0, le=3650)

    # Metabolic
    bmi: Optional[float] = Field(default=None, ge=5, le=120)

    # Comorbidities
    dementia: bool = False
    insomnia: bool = False
    fibromyalgia: bool = False
    suicidality: Literal["none", "elevated_ideation", "acutely_suicidal"] = "none"
    tolerability: Literal["good", "poor"] = "good"   # Step 6a: current trial tolerability
    chronic_suicidality: bool = False                  # elevates lithium to Tier 1 [47, 48, 54]
    prior_depressive_episodes: Optional[int] = None    # None=unknown, 0=first, 1+=recurrent
    discontinuing: bool = False                        # True = tapering to stop (not switching); activates taper schedule in maintenance_plan
    reason_for_switch: Optional[Literal["no_response", "intolerant"]] = None  # Protocol context for switch output
    # Symptom and preference profile (informs report formatter)
    anxiety_comorbidity: bool = False
    sexual_dysfunction_concern: bool = False
    fatigue_anhedonia: bool = False
    seizure_history: bool = False
    eating_disorder: bool = False
    psychosis_positive: bool = False
    chronic_pain: bool = False
    daytime_sedation_concern: bool = False
    therapy_preference: Optional[Literal["medication", "therapy", "combination"]] = None

    @field_validator("current_antidepressant_key")
    @classmethod
    def validate_current_antidepressant_key(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return v.strip().lower()

class EvidenceItem(BaseModel):
    variable: str
    value: str
    fhir_source: str
    note: Optional[str] = None

class MedicationRecommendation(BaseModel):
    medication_key: str
    medication_display: str
    medication_class: str
    intent: RecommendationIntent
    conditional: bool = False
    start_dose: Optional[str] = None
    dose_range: str
    titration_guidance: str
    instructions: List[str] = Field(default_factory=list)
    messages: List[str] = Field(default_factory=list)
    rationale: List[str] = Field(default_factory=list)
    evidence: List[EvidenceItem] = Field(default_factory=list)

class AlgorithmOutput(BaseModel):
    findings: List[str] = Field(default_factory=list)
    recommendations: List[MedicationRecommendation] = Field(default_factory=list)
    non_med_recommendations: List[str] = Field(default_factory=list)
    rationale: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    path_conflicts: List[str] = Field(default_factory=list)   # NEW: inter-path conflicts
    audit_trail: List[str] = Field(default_factory=list)
    stop_reason: Optional[str] = None
    pathway_applied: List[str] = Field(default_factory=lambda: ["adult"])  # CHANGED: list
    monitoring_schedule: List[str] = Field(default_factory=list)
    maintenance_plan: List[str] = Field(default_factory=list)
    medications_excluded: List[str] = Field(default_factory=list)
    adjunctive_options: List[str] = Field(default_factory=list)
    reference_list: List[str] = Field(default_factory=list)
    switching_protocol: List[str] = Field(default_factory=list)
    response_category: Optional[str] = None               # set during follow-up routing: "remission_or_response", "partial", "no_response"
    report: Optional[Any] = Field(default=None)          # structured JSON dict for React
    text_report: Optional[str] = Field(default=None)     # formatted text for notebook display


# ------------------------------------------------------------
# 4) Path-specific rules (Step 2 — deviation paths)
# ------------------------------------------------------------
# Each path defines:
#   exclusions          — {med_key: reason} meds blocked unconditionally by this path
#   qtc_500_exclusions  — {med_key: reason} meds blocked only when QTc > 500 ms
#   dose_caps           — {med_key: max_mg} most restrictive cap across all active paths wins
#   preferred           — [med_key, ...] ordered preferred meds for this path
#
# Applied in ClinicalContraindicationStage; conflicts surfaced via detect_path_conflicts().
PATH_RULES: Dict[str, Dict[str, Any]] = {
    "geriatric": {
        # [26, 28] anticholinergic burden; [26, 28] CYP2D6 interactions / falls
        "exclusions": {
            "paroxetine":  "Anticholinergic burden, falls risk [26, 28]",
            "fluoxetine":  "Drug interactions via CYP2D6, falls risk [26, 28]",
        },
        "qtc_500_exclusions": {},
        # [27, 30] escitalopram max 10 mg; [25, 27] citalopram max 20 mg
        "dose_caps": {
            "escitalopram": 10.0,
            "citalopram":   20.0,
        },
        "preferred": ["sertraline", "escitalopram", "duloxetine"],  # [28]
    },
    "cardiac": {
        "exclusions": {},   # TCAs/trazodone/nefazodone are not in MED_KB; no blanket exclusions
        # [79, 81, 82] QTc > 500 ms: arrhythmia risk
        "qtc_500_exclusions": {
            "citalopram":   "QTc > 500 ms: arrhythmia risk [79, 81, 82]",
            "escitalopram": "QTc > 500 ms: arrhythmia risk [79, 81, 82]",
        },
        "dose_caps": {},
        "preferred": ["sertraline", "fluoxetine"],   # safest cardiac profile [27, 78]
    },
    "renal": {
        # Duloxetine CrCl < 30 handled separately in ClinicalContraindicationStage.
        # Dose caps for specific meds loaded dynamically from RENAL_MAX_CAPS_MG.
        "exclusions": {},
        "qtc_500_exclusions": {},
        "dose_caps": {},
        "preferred": [],
    },
    "hepatic": {
        # [85, 86] duloxetine hepatotoxicity; [85] nefazodone
        "exclusions": {
            "duloxetine":  "Hepatotoxicity risk; avoid entirely in hepatic impairment — do not dose-reduce [85, 86]",
            "nefazodone":  "Hepatotoxic [85]",
        },
        "qtc_500_exclusions": {},
        # [30] escitalopram max 10 mg; citalopram max 20 mg in hepatic impairment
        # [23] venlafaxine 50% dose reduction → max 112.5 mg (50% of 225 mg)
        "dose_caps": {
            "escitalopram":  10.0,
            "citalopram":    20.0,
            "venlafaxine_xr": 112.5,
        },
        "preferred": [],
    },
    "obesity": {
        # [25, 30] significant weight gain
        "exclusions": {
            "mirtazapine": "Significant weight gain; avoid in obesity [25, 30]",
            "paroxetine":  "Significant weight gain; avoid in obesity [25, 30]",
        },
        "qtc_500_exclusions": {},
        "dose_caps": {},
        "preferred": ["bupropion_xl", "fluoxetine"],   # [25]
    },
    "dementia": {
        # [26, 28] anticholinergic burden accelerates cognitive decline
        "exclusions": {
            "paroxetine": "Anticholinergic burden accelerates cognitive decline [26, 28]",
        },
        "qtc_500_exclusions": {},
        "dose_caps": {},
        "preferred": [],
    },
    "antepartum": {
        # [26, 28] cardiac malformations in first-trimester exposure
        "exclusions": {
            "paroxetine": "Associated with cardiac malformations in first-trimester exposure [26, 28]",
        },
        "qtc_500_exclusions": {},
        "dose_caps": {},
        "preferred": ["sertraline", "fluoxetine", "citalopram", "escitalopram"],   # [26, 28]
    },
    "postpartum": {
        # [26, 28] norfluoxetine accumulates in nursing infant
        "exclusions": {
            "fluoxetine": "Long half-life; norfluoxetine accumulates in nursing infant [26, 28]",
        },
        "qtc_500_exclusions": {},
        "dose_caps": {},
        "preferred": ["sertraline"],   # lowest breast milk transfer [26, 28]
    },
    "pain": {
        # [29, 35] SNRIs FDA-approved for pain; SSRIs generally ineffective
        "exclusions": {},
        "qtc_500_exclusions": {},
        "dose_caps": {},
        "preferred": ["duloxetine", "venlafaxine_xr"],   # [29, 35]
    },
    "insomnia": {
        # [25, 30] mirtazapine first-line for insomnia — but only when obesity path is NOT active
        "exclusions": {},
        "qtc_500_exclusions": {},
        "dose_caps": {},
        "preferred": ["mirtazapine"],
    },
    "peds": {
        # [75, 76, 77] venlafaxine highest suicidality signal; [77] paroxetine unfavorable
        "exclusions": {
            "venlafaxine_xr": "Highest suicidality signal in pediatric meta-analyses [75, 76, 77]",
            "paroxetine":     "Not recommended in pediatric population; unfavorable safety profile [77]",
        },
        "qtc_500_exclusions": {},
        "dose_caps": {},
        # [75, 76] fluoxetine FDA-approved age 8+; escitalopram FDA-approved age 12+
        "preferred": ["fluoxetine", "escitalopram", "sertraline"],
    },
    "adult": {
        "exclusions": {},
        "qtc_500_exclusions": {},
        "dose_caps": {},
        # Standard adult SSRI ranking per spec [19, 20, 26]: escitalopram first
        "preferred": ["escitalopram", "sertraline", "fluoxetine", "citalopram", "paroxetine"],
    },
}


# ------------------------------------------------------------
# 5) Multi-path detection — replaces single infer_pathway()
# ------------------------------------------------------------
def detect_active_paths(p: PatientInput) -> List[str]:
    """
    Returns every deviation path triggered for this patient (Step 2 of
    CLAUDE_MDD.md). Multiple paths fire simultaneously when multiple
    triggers are present. Falls back to ['adult'] when no deviation applies.

    Trigger order mirrors Step 2 of CLAUDE_MDD.md.
    """
    paths: List[str] = []

    if p.age < 18:
        paths.append("peds")
    if p.age >= 65:
        paths.append("geriatric")
    if p.pregnant:
        paths.append("antepartum")
    if p.postpartum_days is not None and p.postpartum_days >= 0:
        paths.append("postpartum")

    # Renal trigger: eGFR < 60 per CLAUDE_MDD.md Step 2
    renal_val = p.crcl_ml_min if p.crcl_ml_min is not None else p.egfr_ml_min_1_73
    if renal_val is not None and renal_val < 60:
        paths.append("renal")

    if p.hepatic_impairment:
        paths.append("hepatic")
    if p.cardiac_history or p.qtc_ms is not None:
        paths.append("cardiac")
    if p.fibromyalgia:
        paths.append("pain")
    if p.insomnia:
        paths.append("insomnia")
    if p.bmi is not None and p.bmi >= 30:
        paths.append("obesity")
    if p.dementia:
        paths.append("dementia")

    return paths if paths else ["adult"]


# ------------------------------------------------------------
# 6) Cross-path conflict detection
# ------------------------------------------------------------
def detect_path_conflicts(active_paths: List[str], p: PatientInput) -> List[str]:
    """
    Identifies cases where one path prefers a medication that another path
    excludes. Conflicts are flagged in output.path_conflicts rather than
    silently dropped.
    """
    conflicts: List[str] = []
    for path_a in active_paths:
        prefs_a = PATH_RULES.get(path_a, {}).get("preferred", [])
        for med in prefs_a:
            for path_b in active_paths:
                if path_b == path_a:
                    continue
                rules_b = PATH_RULES.get(path_b, {})
                all_excl_b = dict(rules_b.get("exclusions", {}))
                if p.qtc_ms is not None and p.qtc_ms > 500:
                    all_excl_b.update(rules_b.get("qtc_500_exclusions", {}))
                if med in all_excl_b:
                    msg = (
                        f"Path conflict: [{path_a}] prefers {med} "
                        f"but [{path_b}] excludes it — {all_excl_b[med]}"
                    )
                    if msg not in conflicts:
                        conflicts.append(msg)
    return conflicts


# ------------------------------------------------------------
# 7) Helper functions
# ------------------------------------------------------------
ResponseCategory = Literal["remission_or_response", "partial", "no_response", "insufficient_data"]

def phq_reduction_pct(baseline: int, current: int) -> float:
    if baseline <= 0:
        return 0.0
    return (baseline - current) / baseline

def categorize_response(
    baseline_phq: Optional[int], current_phq: int, weeks_on_med: Optional[int]
) -> ResponseCategory:
    if baseline_phq is None or weeks_on_med is None:
        return "insufficient_data"
    if weeks_on_med < 6:
        return "insufficient_data"
    if current_phq < 5:
        return "remission_or_response"
    pct = phq_reduction_pct(baseline_phq, current_phq)
    if pct >= 0.50:
        return "remission_or_response"
    if 0.25 <= pct < 0.50:
        return "partial"
    return "no_response"

def renal_bucket_from_crcl(crcl: Optional[float], egfr: Optional[float]) -> Optional[str]:
    val = crcl if crcl is not None else egfr
    if val is None:
        return None
    if val >= 60:   return ">60"
    if val >= 30:   return "30-60"
    if val >= 15:   return "15-29"
    return "<15"

def max_cap_for_context(
    p: PatientInput,
    med_key: str,
    active_paths: Optional[List[str]] = None,
) -> Optional[float]:
    """
    Returns the most restrictive dose cap applicable across ALL active paths.
    Returns 0.0 to signal 'avoid entirely'.
    Returns None if no cap applies (use KB default max).
    """
    paths = active_paths if active_paths is not None else detect_active_paths(p)
    caps: List[float] = []

    # Renal caps from RENAL_MAX_CAPS_MG
    if "renal" in paths:
        bucket = renal_bucket_from_crcl(p.crcl_ml_min, p.egfr_ml_min_1_73)
        if bucket and med_key in RENAL_MAX_CAPS_MG:
            caps.append(float(RENAL_MAX_CAPS_MG[med_key][bucket]))

    # Duloxetine: avoid entirely when CrCl/eGFR < 30
    if med_key == "duloxetine":
        renal_val = p.crcl_ml_min if p.crcl_ml_min is not None else p.egfr_ml_min_1_73
        if renal_val is not None and renal_val < 30:
            return 0.0

    # Citalopram: max 20 mg if age > 60 [25, 27] — fires independently of the
    # geriatric path (which triggers at age ≥ 65, not > 60)
    if med_key == "citalopram" and p.age > 60:
        caps.append(20.0)

    # PATH_RULES dose_caps (geriatric, hepatic, etc.) — most restrictive wins
    for path in paths:
        path_caps = PATH_RULES.get(path, {}).get("dose_caps", {})
        if med_key in path_caps:
            caps.append(float(path_caps[med_key]))

    return min(caps) if caps else None

# Hepatic impairment: SSRI start at 50% of standard starting dose [85, 86]
# Venlafaxine start at 50% of standard starting dose [23]
HEPATIC_START_DOSES: Dict[str, str] = {
    "escitalopram":   "2.5–5 mg daily (50% of standard; hepatic impairment [85, 86])",
    "sertraline":     "12.5–25 mg daily (50% of standard; hepatic impairment [85, 86])",
    "citalopram":     "5–10 mg daily (50% of standard; hepatic impairment [85, 86])",
    "fluoxetine":     "5–10 mg daily (50% of standard; hepatic impairment [85, 86])",
    "paroxetine":     "5–10 mg daily (50% of standard; hepatic impairment [85, 86])",
    "fluvoxamine":    "25 mg daily (50% of standard; hepatic impairment [85, 86])",
    "venlafaxine_xr": "~19–37.5 mg daily (50% of standard; hepatic impairment [23])",
}

def get_context_start_dose(
    p: PatientInput,
    med_key: str,
    active_paths: List[str],
) -> Optional[str]:
    """
    Returns a context-adjusted starting dose string when hepatic impairment
    requires dose reduction, or None to use the KB default.
    Applies to all SSRIs and venlafaxine [23, 85, 86].
    """
    if "hepatic" in active_paths and med_key in HEPATIC_START_DOSES:
        return HEPATIC_START_DOSES[med_key]
    return None


def is_qt_risk_med(med_key: str) -> bool:
    return med_key in MED_KB and MED_KB[med_key].get("qt_risk", "none") != "none"

def estimate_trial_number(p: PatientInput) -> int:
    if p.trial_number is not None:
        return int(p.trial_number)
    failed = [t for t in p.prior_trials if t.outcome in {"no_response", "intolerant"}]
    return min(3, 1 + len({t.medication_key for t in failed if t.medication_key}))

def is_at_max_dose_for_context(
    p: PatientInput, med_key: str, active_paths: Optional[List[str]] = None
) -> bool:
    if p.current_dose_mg is None:
        return False
    cap = max_cap_for_context(p, med_key, active_paths)
    if cap == 0.0:
        return False
    typical_max = DOSE_MIN_MAX_MG.get(med_key, (0.0, 1e9))[1]
    max_allowed = typical_max if cap is None else min(typical_max, cap)
    return float(p.current_dose_mg) >= (max_allowed - 1e-6)

def apply_history_sets(p: PatientInput) -> Tuple[Set[str], Set[str], Set[str]]:
    tried      = {t.medication_key.strip().lower() for t in p.prior_trials if t.medication_key}
    failed     = {t.medication_key.strip().lower() for t in p.prior_trials
                  if t.medication_key and t.outcome in {"no_response", "intolerant"}}
    successful = {t.medication_key.strip().lower() for t in p.prior_trials
                  if t.medication_key and t.outcome == "remission_or_response"}
    return tried, failed, successful


# ------------------------------------------------------------
# 8) Pipeline stages
# ------------------------------------------------------------
@dataclass
class WorkingState:
    patient: PatientInput
    output: AlgorithmOutput
    blocked_candidates: Set[str]
    exclusion_reasons: Dict[str, str] = field(default_factory=dict)

class Stage:
    name: str = "stage"
    def run(self, state: WorkingState) -> WorkingState:
        return state

class FindingsStage(Stage):
    name = "findings"

    def run(self, state: WorkingState) -> WorkingState:
        p = state.patient
        out = state.output
        out.findings.append(f"PHQ-9 current: {p.phq_current}.")
        if p.baseline_phq is not None:
            out.findings.append(f"PHQ-9 baseline: {p.baseline_phq}.")
        if p.cardiac_history:
            out.findings.append("Relevant history: cardiac disease.")
        if p.fibromyalgia:
            out.findings.append("Relevant diagnosis: fibromyalgia/chronic pain.")
        if p.insomnia:
            out.findings.append("Relevant symptom: insomnia.")
        if p.hepatic_impairment:
            out.findings.append("Relevant diagnosis: hepatic impairment.")
        if p.dementia:
            out.findings.append("Relevant diagnosis: dementia.")
        if p.crcl_ml_min is not None or p.egfr_ml_min_1_73 is not None:
            rb = renal_bucket_from_crcl(p.crcl_ml_min, p.egfr_ml_min_1_73)
            val = p.crcl_ml_min if p.crcl_ml_min is not None else p.egfr_ml_min_1_73
            out.findings.append(f"Renal function: {val} mL/min (bucket: {rb}).")
        if p.qtc_ms is not None:
            out.findings.append(f"QTc: {p.qtc_ms} ms.")
        if p.pregnant:
            out.findings.append("Population: antepartum.")
        if p.postpartum_days is not None:
            out.findings.append(f"Population: postpartum (day {p.postpartum_days}).")
        if p.bmi is not None:
            out.findings.append(f"BMI: {p.bmi:.1f}.")
        if p.suicidality != "none":
            out.findings.append(f"Suicidality screen: {p.suicidality}.")
        return state

class PathwayStage(Stage):
    """
    Replaces single infer_pathway() with detect_active_paths().
    All triggered deviation paths fire simultaneously.
    """
    name = "pathway"

    def run(self, state: WorkingState) -> WorkingState:
        p = state.patient
        out = state.output
        out.pathway_applied = detect_active_paths(p)
        out.findings.append(f"Active deviation path(s): {', '.join(out.pathway_applied)}.")
        out.audit_trail.append(f"active_paths={out.pathway_applied}")
        return state

class SuicidalityScreenStage(Stage):
    """
    Step 0: Suicidality screen per CLAUDE_MDD.md.

    acutely_suicidal  → hard stop; emergent hospitalization; no further processing.
    elevated_ideation → consider hospitalization flagged in warnings; close
                        monitoring added; algorithm continues.
    age < 25 (any suicidality value) → FDA black box warning always appended.
    Citations: [3, 4, 73, 74]
    """
    name = "suicidality_screen"

    def run(self, state: WorkingState) -> WorkingState:
        p = state.patient
        out = state.output

        # FDA black box warning — fires for all patients under 25 regardless of
        # suicidality value and regardless of any prior stop_reason.
        if p.age < 25:
            out.warnings.append(
                "FDA black box warning: antidepressants increase risk of suicidal "
                "thinking and behavior in patients under 25. Monitor closely during "
                "weeks 1–4. [73, 74]"
            )
            out.audit_trail.append("warn:fda_black_box_age<25")

        # Skip suicidality routing if a prior hard stop is already set
        # (e.g., mania_positive), but black box warning above still fires.
        if out.stop_reason:
            return state

        if p.suicidality == "acutely_suicidal":
            out.stop_reason = "acutely_suicidal"
            out.non_med_recommendations.append(
                "EMERGENT: Patient is acutely suicidal. "
                "Emergent hospitalization is recommended. "
                "No antidepressant initiation at this time. [3, 4, 73, 74]"
            )
            out.warnings.append(
                "Acutely suicidal: emergent evaluation required. "
                "Do not initiate or adjust antidepressants until patient is stabilised "
                "in an appropriate care setting. [3, 4]"
            )
            out.audit_trail.append("stop:acutely_suicidal")

        elif p.suicidality == "elevated_ideation":
            out.warnings.append(
                "Elevated suicidal ideation (without acute risk): consider hospitalisation; "
                "initiate close monitoring. Algorithm continues — review all recommendations "
                "in context of suicide risk. [3, 4, 73, 74]"
            )
            out.non_med_recommendations.append(
                "Close suicidality monitoring required: reassess at every visit; "
                "safety plan recommended; consider Crisis/988 referral. [73, 74]"
            )
            out.audit_trail.append("warn:elevated_suicidal_ideation")

        return state


class ManiaExclusionStage(Stage):
    name = "mania_exclusion"

    def run(self, state: WorkingState) -> WorkingState:
        p = state.patient
        out = state.output
        if p.mania_screen == "positive":
            out.stop_reason = "mania_positive"
            out.rationale.append("Mania screen positive: antidepressants not recommended; route to psychiatry. [3, 4]")
            out.non_med_recommendations.append("Do NOT initiate antidepressant; refer for psychiatric evaluation.")
            out.audit_trail.append("stop:mania_positive")
        return state

class QTcSafetyStage(Stage):
    name = "qtc_safety"

    def run(self, state: WorkingState) -> WorkingState:
        p = state.patient
        out = state.output
        if p.qtc_ms is not None and p.qtc_ms > 550:
            out.stop_reason = "qtc_over_550"
            out.warnings.append("QTc > 550 ms: discontinue QT-prolonging agents and obtain psychiatric consultation per protocol.")
            out.audit_trail.append("stop:qtc_over_550")
        elif p.qtc_ms is not None and p.qtc_ms >= 500:
            out.warnings.append("QTc ≥ 500 ms: elevated risk — QTc-conditional exclusions active; clinician review advised.")
            out.audit_trail.append("warn:qtc_ge_500")
        return state

class SeverityAndNonMedStage(Stage):
    name = "severity_and_non_med"

    def run(self, state: WorkingState) -> WorkingState:
        p = state.patient
        out = state.output
        followup_context = (
            p.baseline_phq is not None
            and p.weeks_on_current_antidepressant is not None
            and p.weeks_on_current_antidepressant >= 6
            and p.current_antidepressant_key is not None
            and p.current_antidepressant_key.strip() != ""
        )
        out.audit_trail.append(f"followup_context={followup_context}")

        if p.phq_current < 10 and not followup_context:
            if p.phq_current < 5:
                out.non_med_recommendations.append("Monitoring only (PHQ < 5).")
            else:
                out.non_med_recommendations.append("Recommend MoodCalmer dCBT (PHQ 5–9).")
            out.rationale.append("No medication recommended when PHQ < 10 in a new-start context.")
            out.audit_trail.append("no_meds_phq<10_new_start")
            return state

        if p.phq_current >= 15:
            out.non_med_recommendations.append("Recommend psychotherapy in combination with pharmacotherapy (PHQ ≥ 15). [3, 4]")
            out.audit_trail.append("psychotherapy_phq>=15")
        if 10 <= p.phq_current <= 14 and not followup_context:
            out.non_med_recommendations.append(
                "Shared decision (PHQ 10–14): psychotherapy alone first-line; consider medication if "
                "psychotherapy fails, patient preference, or history of recurrent depression. [1, 2, 3, 4]"
            )
            out.audit_trail.append("shared_decision_phq10-14")
        return state

class MedSafetyStage(Stage):
    name = "med_safety"

    def run(self, state: WorkingState) -> WorkingState:
        p = state.patient
        out = state.output
        if out.stop_reason:
            return state
        safety = medication_safety_screen(p.current_medications, list(MED_KB.keys()))
        out.warnings.extend(safety.warnings)
        out.audit_trail.append(f"med_safety_blocked={sorted(safety.blocked)}")
        if safety.detected:
            out.audit_trail.append(f"med_safety_signals={list(safety.detected.keys())}")
        state.blocked_candidates |= safety.blocked
        return state

class ClinicalContraindicationStage(Stage):
    """
    Iterates over every active deviation path and applies:
      - Unconditional exclusions (PATH_RULES[path]['exclusions'])
      - QTc-conditional exclusions (PATH_RULES[path]['qtc_500_exclusions']) when QTc > 500
      - Dose-cap warnings for the current medication context
    Each blocked medication is stored in state.exclusion_reasons for
    structured output. Cross-path conflicts are detected and surfaced.
    """
    name = "clinical_contraindications"

    def run(self, state: WorkingState) -> WorkingState:
        p = state.patient
        out = state.output
        active_paths = out.pathway_applied

        for path in active_paths:
            rules = PATH_RULES.get(path, {})

            # Unconditional exclusions
            for med, reason in rules.get("exclusions", {}).items():
                if med not in state.blocked_candidates:
                    state.blocked_candidates.add(med)
                    state.exclusion_reasons[med] = f"[{path}] {reason}"
                    out.audit_trail.append(f"blocked:{med} ({path})")

            # QTc-conditional exclusions (only when QTc > 500 ms)
            if p.qtc_ms is not None and p.qtc_ms > 500:
                for med, reason in rules.get("qtc_500_exclusions", {}).items():
                    if med not in state.blocked_candidates:
                        state.blocked_candidates.add(med)
                        state.exclusion_reasons[med] = f"[{path}, QTc > 500 ms] {reason}"
                        out.audit_trail.append(f"blocked:{med} (qtc>500, {path})")

            # Dose-cap warnings (note: the cap is enforced in max_cap_for_context;
            # this just surfaces it for clinician awareness)
            for med, cap in rules.get("dose_caps", {}).items():
                if med in MED_KB:
                    out.warnings.append(
                        f"[{path}] {MED_KB[med]['display']}: "
                        f"dose cap {cap} mg/day in this context."
                    )

        # Special renal rule: duloxetine avoid if CrCl/eGFR < 30
        renal_val = p.crcl_ml_min if p.crcl_ml_min is not None else p.egfr_ml_min_1_73
        if renal_val is not None and renal_val < 30 and "duloxetine" not in state.blocked_candidates:
            state.blocked_candidates.add("duloxetine")
            state.exclusion_reasons["duloxetine"] = "[renal] CrCl/eGFR < 30: avoid duloxetine [85, 86]"
            out.audit_trail.append("blocked:duloxetine_renal<30")

        # Dementia + SGA black box warning
        if p.dementia:
            out.warnings.append(
                "Dementia present: all atypical antipsychotics carry FDA black box warning "
                "for increased mortality in elderly patients — flag if augmentation is considered [26, 28]."
            )

        # Cross-path conflict detection
        conflicts = detect_path_conflicts(active_paths, p)
        out.path_conflicts.extend(conflicts)
        if conflicts:
            out.audit_trail.append(f"path_conflicts={len(conflicts)}")

        # Append structured exclusions to findings
        for med, reason in state.exclusion_reasons.items():
            display = MED_KB[med]["display"] if med in MED_KB else med
            out.findings.append(f"Excluded: {display} — {reason}")

        return state

class DoseSanityStage(Stage):
    name = "dose_sanity"

    def run(self, state: WorkingState) -> WorkingState:
        p = state.patient
        out = state.output
        active_paths = out.pathway_applied

        if not p.current_antidepressant_key or p.current_dose_mg is None:
            out.audit_trail.append("dose_sanity_skipped")
            return state

        med = p.current_antidepressant_key.strip().lower()
        if med not in DOSE_MIN_MAX_MG:
            out.audit_trail.append(f"dose_sanity_no_bounds:{med}")
            return state

        cap = max_cap_for_context(p, med, active_paths)
        if cap == 0.0:
            out.warnings.append(f"{med} is contraindicated in current context. Clinician review required.")
            out.audit_trail.append("dose_sanity_contraindicated")
            return state

        mn, mx = DOSE_MIN_MAX_MG[med]
        if cap is not None:
            mx = min(mx, float(cap))
        dose = float(p.current_dose_mg)
        if dose < mn or dose > mx:
            out.warnings.append(
                f"Current {med} dose ({dose} mg) is outside context range ({mn}–{mx} mg). "
                f"Verify before titration decisions."
            )
            out.audit_trail.append("dose_sanity_out_of_range")
        else:
            out.audit_trail.append("dose_sanity_ok")
        return state


# ------------------------------------------------------------
# 9) Recommendation builder
# ------------------------------------------------------------
def _make_reco(
    p: PatientInput,
    med_key: str,
    intent: RecommendationIntent,
    active_paths: Optional[List[str]] = None,
    additional_messages: Optional[List[str]] = None,
    rationale: Optional[List[str]] = None,
    evidence: Optional[List[EvidenceItem]] = None,
    conditional: bool = False,
    cap_override: Optional[float] = None,
) -> MedicationRecommendation:
    kb = MED_KB[med_key]
    msgs = list(additional_messages or [])
    rat  = list(rationale or [])
    ev   = list(evidence or [])
    paths = active_paths if active_paths is not None else detect_active_paths(p)

    if kb.get("bp_message_relevant", False):
        msgs.append("Check baseline BP before prescribing; monitor during titration.")

    if p.qtc_ms is None and is_qt_risk_med(med_key):
        msgs.append("QT risk: prescribe only after obtaining baseline QTc/ECG.")
        conditional = True
        ev.append(EvidenceItem(variable="QTc", value="missing", fhir_source="Observation"))

    if p.qtc_ms is not None and p.qtc_ms >= 500 and is_qt_risk_med(med_key):
        msgs.append("QTc elevated: avoid stacking QT-prolonging agents; clinician review.")
        ev.append(EvidenceItem(variable="QTc", value=str(p.qtc_ms), fhir_source="Observation"))

    for m in kb.get("monitoring", []):
        if m not in msgs:
            msgs.append(m)

    # Determine effective cap across all active paths
    effective_cap = cap_override if cap_override is not None else max_cap_for_context(p, med_key, paths)
    if effective_cap is not None and med_key in DOSE_MIN_MAX_MG and effective_cap > 0:
        mn, mx_typ = DOSE_MIN_MAX_MG[med_key]
        mx_ctx = min(mx_typ, float(effective_cap))
        msgs.append(f"Max dose for this patient context (all active paths): {mx_ctx} mg/day.")

    # Use context-adjusted starting dose when hepatic path requires reduction
    if intent in {"start", "switch_to", "augment_with"}:
        ctx_start = get_context_start_dose(p, med_key, paths)
        start_dose = ctx_start if ctx_start is not None else kb["start_dose"]
    else:
        start_dose = None

    return MedicationRecommendation(
        medication_key=med_key,
        medication_display=kb["display"],
        medication_class=kb["class"],
        intent=intent,
        conditional=conditional,
        start_dose=start_dose,
        dose_range=kb["dose_range"],
        titration_guidance=kb["titration"],
        instructions=[],
        messages=msgs,
        rationale=rat,
        evidence=ev,
    )


# ------------------------------------------------------------
# 10) Treatment selection stage
# ------------------------------------------------------------


# ============================================================
# Reference Database — loaded at runtime from references_consolidated.md
# ============================================================
REFERENCE_DB: Dict[str, str] = {}
_ref_path = Path(__file__).parent / "references_consolidated.md"
with open(_ref_path) as _ref_f:
    for _ref_line in _ref_f:
        _ref_m = re.match(r'^(\d+)\. (.+)', _ref_line.strip())
        if _ref_m:
            REFERENCE_DB[_ref_m.group(1)] = f"{_ref_m.group(1)}. {_ref_m.group(2)}"



# ============================================================
# Augmentation helpers — Step 6 / 6a / 6b
# ============================================================

SSRI_KEYS  = frozenset({"sertraline", "escitalopram", "citalopram", "fluoxetine",
                         "paroxetine", "fluvoxamine"})
SNRI_KEYS  = frozenset({"venlafaxine_xr", "duloxetine", "desvenlafaxine",
                         "levomilnacipran_er"})
BUP_KEYS   = frozenset({"bupropion_xl"})
MIRT_KEYS  = frozenset({"mirtazapine"})

# High discontinuation syndrome risk — extended taper required [28, 87, 92, 93, 94]
EXTENDED_TAPER_MEDS: frozenset = frozenset({
    "paroxetine", "venlafaxine_xr", "duloxetine", "desvenlafaxine"
})

# Serotonergic antidepressants — used for multi-agent serotonin syndrome check [89, 90, 98]
SEROTONERGIC_AD_KEYS: frozenset = frozenset({
    "sertraline", "escitalopram", "citalopram", "fluoxetine", "paroxetine",
    "fluvoxamine", "venlafaxine_xr", "duloxetine", "desvenlafaxine",
    "levomilnacipran_er", "vortioxetine", "vilazodone",
    "mirtazapine",
})

# MAOI antidepressants — 2-week washout required before/after [28, 87, 89, 90]
MAOI_AD_KEYS: frozenset = frozenset({
    "phenelzine", "tranylcypromine", "isocarboxazid", "selegiline",
})

# Tricyclic antidepressants — cross-taper 1-2 weeks when switching from SSRI/SNRI [28, 87]
TCA_AD_KEYS: frozenset = frozenset({
    "nortriptyline", "desipramine", "amitriptyline", "imipramine",
    "clomipramine", "doxepin",
})

SGA_KEYS = frozenset({"aripiprazole", "quetiapine", "lurasidone", "brexpiprazole",
                       "risperidone", "olanzapine"})

# ── Class-based routing helpers ──────────────────────────────────────────────
def _classes_trialed(p: "PatientInput") -> Set[str]:
    """Return the set of medication classes that appear in prior_trials."""
    classes: Set[str] = set()
    for t in p.prior_trials:
        mk = (t.medication_key or "").strip().lower()
        if not mk:
            continue
        if mk in SSRI_KEYS:    classes.add("SSRI")
        elif mk in SNRI_KEYS:  classes.add("SNRI")
        elif mk in BUP_KEYS:   classes.add("NDRI")
        elif mk in MIRT_KEYS:  classes.add("NaSSA")
        elif mk in TCA_AD_KEYS: classes.add("TCA")
        elif mk in SGA_KEYS:   classes.add("SGA")
        elif mk in MED_KB:
            classes.add(MED_KB[mk].get("class", "Other"))
    # Also count the current antidepressant
    ck = (p.current_antidepressant_key or "").strip().lower()
    if ck:
        if ck in SSRI_KEYS:    classes.add("SSRI")
        elif ck in SNRI_KEYS:  classes.add("SNRI")
        elif ck in BUP_KEYS:   classes.add("NDRI")
        elif ck in MIRT_KEYS:  classes.add("NaSSA")
        elif ck in TCA_AD_KEYS: classes.add("TCA")
        elif ck in SGA_KEYS:   classes.add("SGA")
        elif ck in MED_KB:
            classes.add(MED_KB[ck].get("class", "Other"))
    return classes

def _count_failed_trials(p: "PatientInput") -> int:
    """Count unique failed medication keys (prior_trials + current med if failed)."""
    failed = {t.medication_key.strip().lower() for t in p.prior_trials
              if t.medication_key and t.outcome in {"no_response", "intolerant"}}
    # If the current antidepressant has a no_response outcome, count it too
    ck = (p.current_antidepressant_key or "").strip().lower()
    if ck and ck not in failed:
        _resp = categorize_response(p.baseline_phq, p.phq_current, p.weeks_on_current_antidepressant)
        if _resp == "no_response":
            failed.add(ck)
    return len(failed)

def _class_route_label(p: "PatientInput", classes: Set[str]) -> str:
    """Compute the trial label string for class-based routing."""
    n = 1 + _count_failed_trials(p)
    if "TCA" in classes:
        return f"Trial {n} — Advanced Interventions Required"
    if len(classes & {"SSRI", "SNRI"}) == 2 and classes & {"NDRI", "NaSSA"}:
        return f"Trial {n} — Psychiatric Consultation Required"
    if len(classes & {"SSRI", "SNRI"}) == 2:
        return f"Trial {n} — TRD"
    if len(classes) >= 1:
        return f"Trial {n}"
    return "Trial 1"


# Atypical antipsychotics in order of preference per [44]
SGA_AUGMENT_ORDER = [
    "aripiprazole",   # first choice — strongest evidence; superior efficacy/acceptability [44]
    "brexpiprazole",  # [44]
    "quetiapine",     # 150–300 mg/day [44, 54]
    "cariprazine",    # [44]
    "risperidone",    # superior efficacy/acceptability with aripiprazole [44]
    "olanzapine",     # flag combination pill [44]
]


def current_med_class(med_key: Optional[str]) -> str:
    """Classify current antidepressant for augmentation tier-1 logic."""
    if not med_key:
        return "unknown"
    k = med_key.strip().lower()
    if k in SSRI_KEYS:  return "ssri"
    if k in SNRI_KEYS:  return "snri"
    if k in BUP_KEYS:   return "bupropion"
    if k in MIRT_KEYS:  return "mirtazapine"
    return "other"


# ── Switching protocol lookup ─────────────────────────────────────────────
@dataclass
class TaperStep:
    label: str          # "Day 1-3" or "Week 1-2"
    dose_mg: float      # target dose during this step
    instruction: str    # what to do

@dataclass
class SwitchProtocol:
    method: str         # "direct_switch" | "abbreviated_overlap" | "full_cross_taper" | "slow_taper" | "standard_step_taper" | "washout"
    duration: str       # "N/A" | "3-7 days" | "5-6 weeks" | etc.
    warning: str        # "" or warning text (no trailing citation)
    citations: List[str]
    taper_steps: List[TaperStep] = field(default_factory=list)
    new_med_timing: str = ""        # when to start new medication
    clinical_note: str = ""         # evidence caveat
    disclaimer: str = (
        "Taper schedules are clinical guidance based on current evidence. "
        "Individual variation in discontinuation symptoms is significant. "
        "Adjust based on patient tolerance and clinical response. [93, 113]"
    )

METHOD_DISPLAY: Dict[str, str] = {
    "direct_switch":       "Direct switch",
    "abbreviated_overlap": "Abbreviated overlap",
    "full_cross_taper":    "Full calculated cross-taper",
    "slow_taper":          "Full calculated slow taper",
    "standard_step_taper": "Standard step taper",
    "washout":             "Washout — do not overlap",
    "cross_taper":         "Cross-taper",     # legacy fallback
    "dose_optimization":   "Dose optimization — no switch required",
}

def classify_med_for_switch(med_key: Optional[str]) -> str:
    """Return a switch-class token for a medication key."""
    if not med_key:
        return "unknown"
    k = med_key.lower().strip()
    if k == "fluoxetine":    return "fluoxetine"
    if k == "paroxetine":    return "paroxetine"
    if k == "fluvoxamine":   return "fluvoxamine"
    if k in SSRI_KEYS:       return "ssri_other"    # sertraline/escitalopram/citalopram
    if k == "venlafaxine_xr": return "venlafaxine"
    if k == "duloxetine":    return "duloxetine"
    if k in SNRI_KEYS:       return "snri_other"    # desvenlafaxine / levomilnacipran
    if k in BUP_KEYS:        return "bupropion"
    if k in MIRT_KEYS:       return "mirtazapine"
    if k in TCA_AD_KEYS:     return "tca"
    if k in MAOI_AD_KEYS:    return "maoi"
    return "other"

def _cls_is_ssri(c: str) -> bool:
    return c in {"fluoxetine", "paroxetine", "fluvoxamine", "ssri_other"}

def _cls_is_snri(c: str) -> bool:
    return c in {"venlafaxine", "duloxetine", "snri_other"}

def _cls_is_ssri_or_snri(c: str) -> bool:
    return _cls_is_ssri(c) or _cls_is_snri(c)

def _cls_is_bup_or_mirt(c: str) -> bool:
    return c in {"bupropion", "mirtazapine"}


def _calc_taper_steps(
    current_dose: float, step_size: float, freq_label: str,
    med_display: str,
) -> Tuple[List[TaperStep], str]:
    """
    Calculate step-down taper schedule from current_dose to 0mg.
    Returns (list_of_steps, estimated_total_duration).
    """
    steps: List[TaperStep] = []
    dose = current_dose
    step_num = 0
    while dose > 0:
        step_num += 1
        new_dose = max(0.0, dose - step_size)
        # Handle fractional last step
        if new_dose < step_size and new_dose > 0:
            new_dose = 0.0
        steps.append(TaperStep(
            label=f"Step {step_num}",
            dose_mg=new_dose,
            instruction=f"Reduce {med_display} from {dose:.0f}mg to {new_dose:.0f}mg/day",
        ))
        dose = new_dose

    # Estimate total duration
    n_steps = len(steps)
    if "day" in freq_label.lower():
        # e.g. "every 3-7 days" → use midpoint 5 days per step
        days = n_steps * 5
        total_dur = f"{days} days (~{days // 7} weeks)" if days > 7 else f"{days} days"
    elif "1-2 week" in freq_label.lower():
        low_wk = n_steps * 1
        high_wk = n_steps * 2
        total_dur = f"{low_wk}-{high_wk} weeks"
    elif "2 week" in freq_label.lower():
        wks = n_steps * 2
        total_dur = f"~{wks} weeks"
    else:
        total_dur = f"~{n_steps} steps ({freq_label} per step)"

    return steps, total_dur


def _new_med_start_dose(new_key: Optional[str]) -> str:
    """Return the standard start dose for the new medication."""
    if not new_key:
        return "lowest available dose"
    info = MED_KB.get(new_key.strip().lower(), {})
    return info.get("start_dose", "lowest available dose")


def get_switching_protocol(
    prior_key: Optional[str],
    new_key: Optional[str],
    current_dose_mg: Optional[float] = None,
) -> SwitchProtocol:
    """
    Returns the appropriate class-to-class switching protocol with dose-calculated
    taper schedule when applicable.
    Accepts three inputs: prior_medication, new_medication, current_dose_mg.
    Rules are applied in priority order (most specific first).
    """
    pc = classify_med_for_switch(prior_key)
    nc = classify_med_for_switch(new_key)
    dose = float(current_dose_mg) if current_dose_mg else 0.0
    prior_disp = MED_KB.get(prior_key or "", {}).get("display", prior_key or "unknown")
    new_disp = MED_KB.get(new_key or "", {}).get("display", new_key or "unknown")
    new_start = _new_med_start_dose(new_key)

    # ── EDGE: Unknown current medication ──────────────────────────────────
    if pc == "unknown" or pc == "other":
        return SwitchProtocol(
            method="cross_taper",
            duration="1-2 weeks",
            warning="",
            citations=["28", "87"],
            new_med_timing=f"Start new medication at low dose ({new_start}) on day 1.",
            clinical_note=(
                "Switching protocol requires current medication — enter current "
                "antidepressant in follow-up section for a medication-specific protocol."
            ),
        )

    # ── EDGE: Same medication (dose optimization, not a switch) ──────────
    pk = (prior_key or "").strip().lower()
    nk = (new_key or "").strip().lower()
    if pk and nk and pk == nk:
        return SwitchProtocol(
            method="dose_optimization",
            duration="N/A — not a switch",
            warning="",
            citations=[],
            new_med_timing="",
            clinical_note=(
                f"Current and recommended medication are both {prior_disp}. "
                "This is a dose optimization, not a switch — no switching protocol required."
            ),
        )

    # ── RULE E: fluoxetine → MAOI (5-week washout) ────────────────────────
    if pc == "fluoxetine" and nc == "maoi":
        return SwitchProtocol(
            method="washout",
            duration="5 weeks minimum",
            warning=(
                "Life-threatening serotonin syndrome risk. "
                "5-week washout required before starting MAOI."
            ),
            citations=["87", "28"],
            new_med_timing="Do not start MAOI until 5 weeks after last fluoxetine dose.",
        )

    # ── MAOI → any (2-week washout) ──────────────────────────────────────
    if pc == "maoi":
        return SwitchProtocol(
            method="washout",
            duration="2 weeks minimum",
            warning="Life-threatening serotonin syndrome risk if new antidepressant started too soon.",
            citations=["87", "28", "89", "90"],
            new_med_timing="Do not start new antidepressant until 2 weeks after last MAOI dose.",
        )

    # ── any → MAOI (2-week washout) ──────────────────────────────────────
    if nc == "maoi":
        dur = "5 weeks minimum" if pc == "fluoxetine" else "2 weeks minimum"
        return SwitchProtocol(
            method="washout",
            duration=dur,
            warning="Life-threatening serotonin syndrome risk if washout not observed.",
            citations=["87", "28", "89", "90"],
            new_med_timing=f"Do not start MAOI until {dur} after last dose.",
        )

    # ── RULE C: Paroxetine → any class (full calculated taper) ───────────
    if pc == "paroxetine":
        step_size = 10.0
        freq = "every 3-7 days"
        steps, total_dur = _calc_taper_steps(dose, step_size, freq, prior_disp) if dose > 0 else ([], "calculate from current dose")
        hyp_note = ""
        if dose > 20:
            hyp_note = (
                "Current dose >20mg: consider hyperbolic taper approach — "
                "linear dose reductions cause exponential increases in serotonin "
                "transporter availability at receptors. [88, 95] "
            )
        if nc == "tca":
            hyp_note += (
                "TCA narrow therapeutic index — start TCA at lowest dose, monitor "
                "serum levels, and do not advance TCA until paroxetine taper is "
                "complete. CYP2D6 inhibition by paroxetine increases TCA levels. [28, 89]"
            )
        return SwitchProtocol(
            method="full_cross_taper",
            duration=total_dur,
            warning=(
                "Highest SSRI discontinuation risk — full taper required regardless "
                "of destination class. Paroxetine and venlafaxine most commonly "
                "associated with discontinuation syndrome. [93, 112, 113]"
            ),
            citations=["88", "93", "94", "112", "113"],
            taper_steps=steps,
            new_med_timing=(
                f"Start new medication at low dose ({new_start}) at week 2 of taper. "
                f"Do not increase new medication until paroxetine is below 20mg."
            ),
            clinical_note=hyp_note,
        )

    # ── RULE D: Fluoxetine → any non-MAOI (direct switch, built-in taper) ─
    if pc == "fluoxetine":
        note = (
            "Fluoxetine's long half-life makes direct switch safe for most "
            "destinations. Norfluoxetine active metabolite half-life 4-16 days "
            "provides built-in taper. [87, 28]"
        )
        if nc == "tca":
            note += (
                " TCA narrow therapeutic index — start TCA at lowest dose and "
                "monitor serum levels. CYP2D6 inhibition by fluoxetine may persist "
                "for weeks after stopping. [28, 89]"
            )
        return SwitchProtocol(
            method="direct_switch",
            duration="N/A — no taper required",
            warning="",
            citations=["87", "28"],
            new_med_timing=(
                f"Start new medication at standard initiation dose ({new_start}) on day 1. "
                "No taper schedule needed."
            ),
            clinical_note=note,
        )

    # ── RULE F-REVERSE: SNRI → SSRI (direct switch with NE withdrawal warning) ─
    if _cls_is_snri(pc) and _cls_is_ssri(nc):
        return SwitchProtocol(
            method="direct_switch",
            duration="N/A — direct switch",
            warning=(
                "Norepinephrine withdrawal symptoms may occur regardless of SSRI "
                "coverage — monitor for dizziness, paresthesia, and irritability "
                "in the first 1-2 weeks. [93, 113]"
            ),
            citations=["87", "28", "93"],
            new_med_timing=(
                f"Stop prior SNRI, start {new_disp} "
                f"at standard starting dose ({new_start}) the next day."
            ),
            clinical_note=(
                "If patient has history of withdrawal sensitivity, abbreviated overlap "
                "over 3-7 days may reduce serotonin-related discontinuation symptoms. "
                "Note: norepinephrine withdrawal symptoms (dizziness, electric shock "
                "sensations) may still occur despite SSRI coverage. [87, 28, 93]"
            ),
        )

    # ── SNRI → SNRI (unexpected combination — flag + direct switch) ──────
    if _cls_is_snri(pc) and _cls_is_snri(nc):
        return SwitchProtocol(
            method="direct_switch",
            duration="N/A — direct switch",
            warning=(
                "Norepinephrine withdrawal symptoms may occur during transition — "
                "monitor for dizziness, paresthesia, and irritability "
                "in the first 1-2 weeks. [93, 113]"
            ),
            citations=["87", "28", "93"],
            new_med_timing=(
                f"Stop prior SNRI, start {new_disp} "
                f"at standard starting dose ({new_start}) the next day."
            ),
            clinical_note=(
                "Note: switching between two SNRIs — verify this is intentional. "
                "If inadequate response to first SNRI, consider a different class. "
                "If patient has history of withdrawal sensitivity, abbreviated overlap "
                "over 3-7 days may reduce discontinuation symptoms. [87, 28]"
            ),
        )

    # ── RULE F: Venlafaxine → any class (full calculated slow taper) ─────
    if pc == "venlafaxine":
        step_size = 37.5
        freq = "every 1-2 weeks"
        steps, total_dur = _calc_taper_steps(dose, step_size, freq, prior_disp) if dose > 0 else ([], "calculate from current dose")
        ext_note = ""
        if steps:
            n = len(steps)
            high_wk = n * 2
            if high_wk > 8:
                ext_note = (
                    "Extended taper (>8 weeks) — consider psychiatry involvement "
                    "for monitoring. "
                )
        if nc == "tca":
            ext_note += (
                "TCA narrow therapeutic index — start TCA at lowest dose and "
                "monitor serum levels. Do not advance TCA dose until venlafaxine "
                "taper is complete. [28, 89]"
            )
        return SwitchProtocol(
            method="slow_taper",
            duration=total_dur,
            warning=(
                "Highest discontinuation syndrome risk across all antidepressant classes. "
                "Norepinephrine withdrawal symptoms not covered by destination medication "
                "regardless of class. Do not switch abruptly. [93, 94, 112, 113]"
            ),
            citations=["93", "94", "112", "113"],
            taper_steps=steps,
            new_med_timing=(
                f"Start new medication at lowest available dose ({new_start}) at week 2 of taper "
                "once initial reduction is tolerated. Increase new medication to target "
                "during final taper steps."
            ),
            clinical_note=ext_note,
        )

    # ── RULE G: Duloxetine → any class (full calculated slow taper) ──────
    if pc == "duloxetine":
        step_size = 20.0
        freq = "every 1-2 weeks"
        steps, total_dur = _calc_taper_steps(dose, step_size, freq, prior_disp) if dose > 0 else ([], "calculate from current dose")
        ext_note = ""
        if steps:
            n = len(steps)
            high_wk = n * 2
            if high_wk > 8:
                ext_note = (
                    "Extended taper (>8 weeks) — consider psychiatry involvement "
                    "for monitoring. "
                )
        if nc == "tca":
            ext_note += (
                "TCA narrow therapeutic index — start TCA at lowest dose and "
                "monitor serum levels. Do not advance TCA dose until duloxetine "
                "taper is complete. [28, 89]"
            )
        return SwitchProtocol(
            method="slow_taper",
            duration=total_dur,
            warning=(
                "Highest discontinuation syndrome risk across all antidepressant classes. "
                "Norepinephrine withdrawal symptoms not covered by destination medication "
                "regardless of class. Do not switch abruptly. [93, 94, 112]"
            ),
            citations=["93", "94", "112"],
            taper_steps=steps,
            new_med_timing=(
                f"Start new medication at lowest available dose ({new_start}) at week 2 of taper "
                "once initial reduction is tolerated. Increase new medication to target "
                "during final taper steps."
            ),
            clinical_note=ext_note,
        )

    # ── snri_other → any (slow taper with NE warning) ────────────────────
    # Catches desvenlafaxine, levomilnacipran, etc. → bupropion/mirtazapine/TCA/other
    # (SNRI → SSRI already handled by F-REVERSE, SNRI → SNRI above)
    if pc == "snri_other":
        step_size = 25.0
        freq = "every 1-2 weeks"
        steps, total_dur = _calc_taper_steps(dose, step_size, freq, prior_disp) if dose > 0 else ([], "calculate from current dose")
        ext_note = ""
        if nc == "tca":
            ext_note = (
                "TCA narrow therapeutic index — start TCA at lowest dose and "
                "monitor serum levels. Do not advance TCA dose until SNRI taper "
                "is complete. [28, 89]"
            )
        return SwitchProtocol(
            method="slow_taper",
            duration=total_dur,
            warning=(
                "Norepinephrine withdrawal symptoms not covered by destination medication. "
                "Monitor for dizziness, paresthesia, and irritability. "
                "Do not switch abruptly. [93, 94, 112]"
            ),
            citations=["93", "94", "112"],
            taper_steps=steps,
            new_med_timing=(
                f"Start new medication at lowest available dose ({new_start}) at week 2 of taper "
                "once initial reduction is tolerated."
            ),
            clinical_note=ext_note,
        )

    # ── RULE H: Bupropion → any class (standard step taper) ─────────────
    if pc == "bupropion":
        step_size = 150.0 if dose > 150 else 75.0
        freq = "every 1-2 weeks"
        steps, total_dur = _calc_taper_steps(dose, step_size, freq, prior_disp) if dose > 0 else ([], "calculate from current dose")
        return SwitchProtocol(
            method="standard_step_taper",
            duration=total_dur,
            warning="",
            citations=["28"],
            taper_steps=steps,
            new_med_timing=(
                f"Start new medication at lowest available dose ({new_start}) on day 1 of taper."
            ),
            clinical_note=(
                "Limited evidence specific to bupropion discontinuation. "
                "Taper based on general principles and FDA labeling. [28]"
            ),
        )

    # ── RULE I: Mirtazapine → any class (standard step taper) ───────────
    if pc == "mirtazapine":
        step_size = 15.0
        freq = "every 2 weeks"
        steps, total_dur = _calc_taper_steps(dose, step_size, freq, prior_disp) if dose > 0 else ([], "calculate from current dose")
        return SwitchProtocol(
            method="standard_step_taper",
            duration=total_dur,
            warning="",
            citations=["113"],
            taper_steps=steps,
            new_med_timing=(
                f"Start new medication at lowest available dose ({new_start}) on day 1 of taper."
            ),
            clinical_note=(
                "Limited specific evidence for mirtazapine taper. "
                "Schedule based on general principles. [113]"
            ),
        )

    # ── Fluvoxamine → any (cross-taper) ──────────────────────────────────
    if pc == "fluvoxamine":
        return SwitchProtocol(
            method="cross_taper",
            duration="1-2 weeks",
            warning="Discontinuation risk; cross-taper to minimise symptoms.",
            citations=["28", "87"],
            new_med_timing=f"Start new medication at low dose ({new_start}) on day 1.",
        )

    # ── RULE A: SSRI (not paroxetine, not fluoxetine) → SSRI ────────────
    if pc == "ssri_other" and _cls_is_ssri(nc):
        return SwitchProtocol(
            method="direct_switch",
            duration="N/A — direct switch",
            warning="",
            citations=["87", "28"],
            new_med_timing=(
                f"Stop {prior_disp}, start {new_disp} "
                f"at standard starting dose ({new_start}) the next day."
            ),
            clinical_note=(
                "If patient has history of withdrawal sensitivity, abbreviated overlap "
                "over 3-7 days may reduce discontinuation symptoms — reduce prior SSRI "
                "to half dose while starting new SSRI at low dose, then stop prior SSRI. "
                "[87, 28]"
            ),
        )

    # ── RULE B: SSRI (not paroxetine, not fluoxetine) → SNRI ────────────
    if pc == "ssri_other" and _cls_is_snri(nc):
        return SwitchProtocol(
            method="direct_switch",
            duration="N/A — direct switch",
            warning="",
            citations=["87", "28", "114"],
            new_med_timing=(
                f"Stop {prior_disp}, start {new_disp} "
                f"at standard starting dose ({new_start}) the next day."
            ),
            clinical_note=(
                "If patient has history of withdrawal sensitivity, abbreviated overlap "
                "over 3-7 days may reduce discontinuation symptoms — reduce prior SSRI "
                "to half dose while starting SNRI at low dose, then stop prior SSRI. "
                "[87, 28, 114]"
            ),
        )

    # ── RULE A variant: SSRI (not parox, not fluox) → NDRI or NaSSA ─────
    if pc == "ssri_other" and nc in ("bupropion", "mirtazapine"):
        return SwitchProtocol(
            method="direct_switch",
            duration="N/A — direct switch",
            warning="",
            citations=["87", "28"],
            new_med_timing=(
                f"Stop {prior_disp}, start {new_disp} "
                f"at standard starting dose ({new_start}) the next day."
            ),
            clinical_note=(
                "If patient has history of withdrawal sensitivity, abbreviated overlap "
                "over 3-7 days may reduce discontinuation symptoms — reduce prior SSRI "
                "to half dose while starting new medication at low dose, then stop "
                "prior SSRI. Lower serotonin syndrome risk due to different mechanisms. "
                "[87, 28]"
            ),
        )

    # ── SSRI → TCA (cross-taper with TCA warning) ───────────────────────
    if pc == "ssri_other" and nc == "tca":
        return SwitchProtocol(
            method="cross_taper",
            duration="1-2 weeks",
            warning=(
                "TCA narrow therapeutic index — start TCA at lowest dose and "
                "monitor serum levels. Monitor for serotonin syndrome during "
                "overlap period. [28, 87, 89]"
            ),
            citations=["28", "87", "89"],
            new_med_timing=f"Start TCA at lowest dose ({new_start}) on day 1.",
        )

    # ── Default: cross-taper 1–2 weeks ───────────────────────────────────
    return SwitchProtocol(
        method="cross_taper",
        duration="1-2 weeks",
        warning="",
        citations=["28", "87"],
        new_med_timing=f"Start new medication at low dose ({new_start}) on day 1.",
    )


def _format_switch_protocol_lines(
    prior_key: Optional[str],
    new_key: Optional[str],
    proto: SwitchProtocol,
    current_dose_mg: Optional[float] = None,
) -> List[str]:
    """Format one switching protocol block as a list of strings for output."""
    prior_disp = MED_KB.get(prior_key or "", {}).get("display", prior_key or "unknown")
    new_disp   = MED_KB.get(new_key   or "", {}).get("display", new_key   or "unknown")
    prior_cls  = MED_KB.get(prior_key or "", {}).get("class", "unknown")
    new_cls    = MED_KB.get(new_key   or "", {}).get("class", "unknown")
    new_start  = _new_med_start_dose(new_key)
    ref_str    = ", ".join(f"[{c}]" for c in proto.citations)
    method_str = METHOD_DISPLAY.get(proto.method, proto.method)

    dose_str = f" | Current dose: {current_dose_mg:.0f}mg/day" if current_dose_mg else ""
    lines = [
        f"Prior: {prior_disp} ({prior_cls}){dose_str}",
        f"New: {new_disp} ({new_cls}) | Start: {new_start}",
        f"Method: {method_str}",
    ]
    if proto.duration and "n/a" not in proto.duration.lower():
        lines.append(f"Estimated duration: {proto.duration}")

    # Taper schedule (omit for direct switch and fluoxetine outgoing)
    if proto.taper_steps:
        lines.append("Taper schedule:")
        for step in proto.taper_steps:
            lines.append(f"  {step.label}: {step.instruction}")

    # New medication initiation timing
    if proto.new_med_timing:
        lines.append(f"New medication initiation: {proto.new_med_timing}")

    # Clinical note
    if proto.clinical_note:
        lines.append(f"Clinical note: {proto.clinical_note}")

    # Warning
    if proto.warning:
        lines.append(f"\u26a0 {proto.warning}")

    # Disclaimer
    lines.append(f"Note: {proto.disclaimer}")

    # References
    lines.append(f"References: {ref_str}")
    return lines


def _switch_taper_message(
    outgoing_key: Optional[str],
    incoming_key: Optional[str] = None,
    current_dose_mg: Optional[float] = None,
) -> str:
    """Return a compact one-line taper message for switch_to recommendation messages."""
    proto = get_switching_protocol(outgoing_key, incoming_key, current_dose_mg)
    method_str = METHOD_DISPLAY.get(proto.method, proto.method)
    ref_str = ", ".join(f"[{c}]" for c in proto.citations)
    dur_part = f" ({proto.duration})" if proto.duration and "n/a" not in proto.duration.lower() else ""
    if proto.warning:
        return f"{method_str}{dur_part}: {proto.warning} {ref_str}"
    return f"{method_str}{dur_part}. {ref_str}"



def build_augmentation_recs(
    p: PatientInput,
    current_med: Optional[str],
    pathways: List[str],
    can_rec: Callable[[str], bool],
    state: "WorkingState",
) -> List[MedicationRecommendation]:
    """
    Two-tier augmentation hierarchy per CLAUDE_MDD.md.

    First Choice (choose one):
      - Aripiprazole 2–5 mg, max 15 mg
      - Lurasidone 20 mg, max 60 mg
      - Alternate-class antidepressant:
          If on SSRI/SNRI → add bupropion or mirtazapine
          If on bupropion/mirtazapine → add SSRI or SNRI

    Second Choice:
      - Quetiapine 150–300 mg/day
      - Brexpiprazole
      - Risperidone 0.5 mg, max 6 mg
      - Olanzapine 5–10 mg, max 20 mg
      - Lithium — only if chronic suicidality present
      For prominent residual anergia:
      - Methylphenidate
    """
    out = state.output
    recs: List[MedicationRecommendation] = []
    cls = current_med_class(current_med)
    is_chronic_suicidal = getattr(p, "chronic_suicidality", False)

    # ── Dementia warning (applies to all SGAs) ────────────────────────────────
    if p.dementia:
        out.warnings.append(
            "FDA black box warning: all atypical antipsychotics carry increased mortality "
            "risk in elderly patients with dementia — use only after careful benefit-risk "
            "assessment [26, 28]."
        )

    # ── First Choice ──────────────────────────────────────────────────────────

    # Aripiprazole
    if can_rec("aripiprazole"):
        recs.append(_make_reco(
            p, "aripiprazole", intent="augment_with", active_paths=pathways,
            rationale=[
                "FIRST CHOICE augmentation — aripiprazole 2–5 mg, max 15 mg: NNT=8 for response. "
                "OPTIMUM trial: 28.9% remission vs 19.3% for switching [46, 45, 43]."
            ],
            evidence=[EvidenceItem(
                variable="Augmentation tier",
                value="First choice — aripiprazole",
                fhir_source="Derived",
            )],
        ))

    # Lurasidone
    if can_rec("lurasidone"):
        recs.append(_make_reco(
            p, "lurasidone", intent="augment_with", active_paths=pathways,
            rationale=[
                "FIRST CHOICE augmentation — lurasidone 20 mg, max 60 mg [43]."
            ],
            evidence=[EvidenceItem(
                variable="Augmentation tier",
                value="First choice — lurasidone",
                fhir_source="Derived",
            )],
        ))

    # Alternate-class antidepressant
    if cls in {"ssri", "snri"}:
        # Add bupropion
        if can_rec("bupropion_xl"):
            recs.append(_make_reco(
                p, "bupropion_xl", intent="augment_with", active_paths=pathways,
                rationale=[
                    "FIRST CHOICE augmentation — add bupropion (patient on "
                    f"{'SSRI' if cls == 'ssri' else 'SNRI'}): comparable remission to aripiprazole "
                    "(28.2% vs 28.9% in OPTIMUM trial); complementary dopamine-norepinephrine "
                    "reuptake inhibition [45, 46]."
                ],
                evidence=[EvidenceItem(
                    variable="Augmentation tier",
                    value="First choice — alternate-class AD (bupropion)",
                    fhir_source="Derived",
                )],
            ))
        # Add mirtazapine
        if can_rec("mirtazapine"):
            recs.append(_make_reco(
                p, "mirtazapine", intent="augment_with", active_paths=pathways,
                rationale=[
                    "FIRST CHOICE augmentation — add mirtazapine (patient on "
                    f"{'SSRI' if cls == 'ssri' else 'SNRI'}): alternate-class antidepressant "
                    "augmentation [45, 46]."
                ],
                evidence=[EvidenceItem(
                    variable="Augmentation tier",
                    value="First choice — alternate-class AD (mirtazapine)",
                    fhir_source="Derived",
                )],
            ))
    elif cls in {"bupropion", "mirtazapine"}:
        # Add SSRI or SNRI
        _alt_ad_options = ["sertraline", "escitalopram", "venlafaxine_xr", "duloxetine"]
        for _alt_m in _alt_ad_options:
            if can_rec(_alt_m):
                _alt_cls = MED_KB[_alt_m]["class"]
                recs.append(_make_reco(
                    p, _alt_m, intent="augment_with", active_paths=pathways,
                    rationale=[
                        f"FIRST CHOICE augmentation — add {_alt_cls} (patient on "
                        f"{cls}): alternate-class antidepressant augmentation [45, 46]."
                    ],
                    evidence=[EvidenceItem(
                        variable="Augmentation tier",
                        value=f"First choice — alternate-class AD ({_alt_cls})",
                        fhir_source="Derived",
                    )],
                ))
                break  # one alternate-class AD is sufficient

    # ── Second Choice ─────────────────────────────────────────────────────────

    # Quetiapine
    if can_rec("quetiapine"):
        recs.append(_make_reco(
            p, "quetiapine", intent="augment_with", active_paths=pathways,
            rationale=[
                "SECOND CHOICE augmentation — quetiapine 150–300 mg/day: SMD −0.32 efficacy; "
                "2025 LQD trial: superior to lithium at 52 weeks [51, 49, 50]."
            ],
            evidence=[EvidenceItem(
                variable="Augmentation tier",
                value="Second choice — quetiapine",
                fhir_source="Derived",
            )],
        ))

    # Brexpiprazole
    if can_rec("brexpiprazole"):
        recs.append(_make_reco(
            p, "brexpiprazole", intent="augment_with", active_paths=pathways,
            rationale=[
                "SECOND CHOICE augmentation — brexpiprazole: FDA-approved for MDD "
                "augmentation; OR 1.47–2.17 for response [24, 43, 44]."
            ],
            evidence=[EvidenceItem(
                variable="Augmentation tier",
                value="Second choice — brexpiprazole",
                fhir_source="Derived",
            )],
        ))

    # Risperidone
    if can_rec("risperidone"):
        recs.append(_make_reco(
            p, "risperidone", intent="augment_with", active_paths=pathways,
            rationale=[
                "SECOND CHOICE augmentation — risperidone 0.5 mg, max 6 mg [44]."
            ],
            evidence=[EvidenceItem(
                variable="Augmentation tier",
                value="Second choice — risperidone",
                fhir_source="Derived",
            )],
        ))

    # Olanzapine
    if can_rec("olanzapine"):
        recs.append(_make_reco(
            p, "olanzapine", intent="augment_with", active_paths=pathways,
            rationale=[
                "SECOND CHOICE augmentation — olanzapine 5–10 mg, max 20 mg [44]."
            ],
            evidence=[EvidenceItem(
                variable="Augmentation tier",
                value="Second choice — olanzapine",
                fhir_source="Derived",
            )],
        ))

    # Lithium — only if chronic suicidality present
    if is_chronic_suicidal and can_rec("lithium"):
        recs.append(_make_reco(
            p, "lithium", intent="augment_with", active_paths=pathways,
            rationale=[
                "SECOND CHOICE augmentation — lithium: unique anti-suicide properties; "
                "indicated when chronic suicidality present [54, 47, 48]."
            ],
            additional_messages=[
                "Target: 0.6–1.2 mEq/L general; 0.3–0.6 mmol/L older adults [54].",
                "Monitor: Li+ level, TSH, BMP at initiation, 1–2 months, then every 6–12 months.",
            ],
            evidence=[EvidenceItem(
                variable="Augmentation tier",
                value="Second choice — lithium (chronic suicidality)",
                fhir_source="Derived",
            )],
        ))

    # Methylphenidate — for prominent residual anergia
    if can_rec("methylphenidate"):
        recs.append(_make_reco(
            p, "methylphenidate", intent="augment_with", active_paths=pathways,
            rationale=[
                "SECOND CHOICE augmentation (prominent residual anergia) — methylphenidate: "
                "low-to-very-low evidence quality; use only for residual anergia/fatigue [56, 57, 58]."
            ],
            evidence=[EvidenceItem(
                variable="Augmentation tier",
                value="Second choice — methylphenidate (residual anergia)",
                fhir_source="Derived",
            )],
        ))

    return recs

class TreatmentSelectionStage(Stage):
    name = "treatment_selection"

    def run(self, state: WorkingState) -> WorkingState:
        p = state.patient
        out = state.output

        if out.stop_reason:
            out.audit_trail.append("selection_skipped:stop_reason")
            return state

        pathways: List[str] = out.pathway_applied
        resp_cat = categorize_response(p.baseline_phq, p.phq_current, p.weeks_on_current_antidepressant)
        out.audit_trail.append(f"response_category={resp_cat}")
        if resp_cat in {"remission_or_response", "partial", "no_response"}:
            out.response_category = resp_cat

        tried_meds, failed_meds, successful_meds = apply_history_sets(p)
        blocked = set(state.blocked_candidates)

        # If the current antidepressant has failed, treat it as a completed failed trial
        current_med_failed = False
        if resp_cat == "no_response" and (p.current_antidepressant_key or "").strip().lower():
            _ck = p.current_antidepressant_key.strip().lower()
            tried_meds.add(_ck)
            failed_meds.add(_ck)
            current_med_failed = True

        classes_tried = _classes_trialed(p)
        trial_n = 1 + _count_failed_trials(p)
        trial_label = _class_route_label(p, classes_tried)
        out.audit_trail.append(f"trial_number={trial_n}")
        out.audit_trail.append(f"classes_trialed={sorted(classes_tried)}")
        out.audit_trail.append(f"trial_label={trial_label}")

        def can_recommend(m: str) -> bool:
            if m not in MED_KB:                          return False
            if m in blocked:                             return False
            if m in failed_meds:                         return False
            if m in tried_meds and m not in successful_meds: return False
            if max_cap_for_context(p, m, pathways) == 0.0:  return False
            return True

        current_med = (p.current_antidepressant_key or "").strip().lower() or None

        # ── Comorbidity-driven exclusions (Part 3) ─────────────────────────────
        if p.anxiety_comorbidity and "bupropion_xl" not in blocked:
            blocked.add("bupropion_xl")
            state.exclusion_reasons["bupropion_xl"] = (
                "Bupropion — avoided due to comorbid anxiety; "
                "activating profile may worsen anxiety symptoms [28]"
            )
            state.blocked_candidates.add("bupropion_xl")
        if p.seizure_history and "bupropion_xl" not in blocked:
            blocked.add("bupropion_xl")
            state.exclusion_reasons["bupropion_xl"] = (
                "Bupropion — avoided due to seizure history; "
                "lowers seizure threshold [28]"
            )
            state.blocked_candidates.add("bupropion_xl")
        if p.eating_disorder and "bupropion_xl" not in blocked:
            blocked.add("bupropion_xl")
            state.exclusion_reasons["bupropion_xl"] = (
                "Bupropion — avoided due to eating disorder; "
                "contraindicated in bulimia/anorexia [28]"
            )
            state.blocked_candidates.add("bupropion_xl")
        if p.cardiac_history and "citalopram" not in blocked:
            blocked.add("citalopram")
            state.exclusion_reasons["citalopram"] = (
                "Citalopram — avoided due to cardiac history; "
                "QTc prolongation risk [78, 79]"
            )
            state.blocked_candidates.add("citalopram")
        if p.pregnant and "paroxetine" not in blocked:
            blocked.add("paroxetine")
            state.exclusion_reasons["paroxetine"] = (
                "Paroxetine — avoided in pregnancy; "
                "cardiac malformation risk [73]"
            )
            state.blocked_candidates.add("paroxetine")
        if p.dementia:
            for _sga in SGA_KEYS:
                if _sga not in blocked:
                    blocked.add(_sga)
                    state.exclusion_reasons[_sga] = (
                        f"{MED_KB.get(_sga, {}).get('display', _sga)} — "
                        "increased mortality risk in older adults with dementia; "
                        "FDA black box warning [43]"
                    )
                    state.blocked_candidates.add(_sga)

        # ── Selection note builder ─────────────────────────────────────────────
        def _selection_notes(med_key: str) -> List[str]:
            """Return patient-specific selection notes for a medication (Part 3)."""
            notes: List[str] = []
            # Elevation notes
            if p.fatigue_anhedonia and med_key == "bupropion_xl":
                notes.append("First choice given prominent fatigue and anhedonia [106, 28]")
            if p.sexual_dysfunction_concern and med_key == "bupropion_xl":
                notes.append("Preferred given sexual dysfunction concern — lowest sexual side effect burden in class [28]")
            # Preference notes
            if p.insomnia and med_key == "mirtazapine":
                notes.append("Preferred given insomnia — sedating and appetite-stimulating properties [107, 28]")
            if p.anxiety_comorbidity and med_key in SSRI_KEYS:
                notes.append("Preferred given comorbid anxiety — bupropion avoided due to activating profile [28]")
            if (p.fibromyalgia or p.chronic_pain) and med_key == "duloxetine":
                notes.append("Added given comorbid chronic pain — dual indication for pain and depression [35]")
            if p.cardiac_history and med_key == "sertraline":
                notes.append("Preferred SSRI given cardiac history — lowest QTc risk in class [78, 79]")
            # Dose modification notes
            if p.age >= 60 and med_key == "escitalopram":
                notes.append("Dose capped at 10mg/day — age-related QTc risk [78, 80]")
            if p.hepatic_impairment and med_key in HEPATIC_START_DOSES:
                notes.append("Dose reduced — hepatic impairment; reduced clearance [85, 86]")
            renal_val = p.crcl_ml_min if p.crcl_ml_min is not None else p.egfr_ml_min_1_73
            if renal_val is not None and renal_val < 30 and med_key in RENAL_MAX_CAPS_MG:
                notes.append("Dose reduced — renal impairment; reduced clearance [83, 84]")
            if p.cardiac_history and med_key == "venlafaxine_xr":
                notes.append("Monitor BP — SNRI may elevate blood pressure; baseline and follow-up BP required [31, 32]")
            if p.cardiac_history and med_key == "duloxetine":
                notes.append("Monitor BP — SNRI may elevate blood pressure; baseline and follow-up BP required [31, 32]")
            # Mirtazapine caution
            if med_key == "mirtazapine":
                if (p.bmi is not None and p.bmi >= 30) or p.daytime_sedation_concern:
                    notes.append("Use with caution given weight gain risk [107]")
            return notes

        def _make_reco_with_notes(
            med_key: str, intent: RecommendationIntent,
            extra_messages: Optional[List[str]] = None,
            extra_rationale: Optional[List[str]] = None,
            **kwargs,
        ) -> MedicationRecommendation:
            msgs = list(extra_messages or [])
            msgs.extend(_selection_notes(med_key))
            return _make_reco(
                p, med_key, intent=intent, active_paths=pathways,
                additional_messages=msgs,
                rationale=extra_rationale,
                **kwargs,
            )

        # ── Follow-up logic (response routing) ─────────────────────────────────
        if resp_cat in {"partial", "no_response", "remission_or_response"} and current_med in MED_KB:
            if resp_cat == "remission_or_response":
                cap = max_cap_for_context(p, current_med, pathways)
                out.recommendations = [_make_reco(
                    p, current_med, intent="continue", active_paths=pathways,
                    additional_messages=["Response/remission achieved: continue current regimen and monitor."],
                    rationale=["PHQ improvement meets response/remission threshold at ≥6 weeks."],
                    evidence=[
                        EvidenceItem(variable="PHQ-9 current", value=str(p.phq_current), fhir_source="Observation"),
                        EvidenceItem(variable="PHQ-9 baseline", value=str(p.baseline_phq), fhir_source="Derived"),
                        EvidenceItem(variable="Weeks on med", value=str(p.weeks_on_current_antidepressant), fhir_source="Derived"),
                    ],
                    cap_override=cap,
                )]
                out.rationale.append("Continue effective medication when response/remission achieved.")
                return state

            if resp_cat == "partial":
                cap = max_cap_for_context(p, current_med, pathways)
                if trial_n >= 2:
                    continue_reco = _make_reco(
                        p, current_med, intent="continue", active_paths=pathways,
                        additional_messages=["Partial response: continue current medication and augment."],
                        rationale=[
                            f"Partial response at Trial {trial_n} → augmentation pathway "
                            "[36, 37, 38, 39, 40, 47, 48, 25, 45, 41]."
                        ],
                        evidence=[EvidenceItem(variable="Trial number", value=str(trial_n), fhir_source="Derived")],
                        cap_override=cap,
                    )
                    aug_recs = build_augmentation_recs(p, current_med, pathways, can_recommend, state)
                    out.recommendations = [continue_reco] + aug_recs
                    out.audit_trail.append("branch:partial_augment")
                    return state
                else:
                    if not is_at_max_dose_for_context(p, current_med, pathways):
                        inc_msg = "Partial response: increase dose as tolerated; reassess in ~4–6 weeks."
                        if p.current_dose_mg is not None:
                            inc_msg = (
                                f"Partial response: "
                                f"{next_dose_step(current_med, float(p.current_dose_mg), cap_override=cap)} "
                                f"Reassess in ~4–6 weeks."
                            )
                        out.recommendations = [_make_reco(
                            p, current_med, intent="increase", active_paths=pathways,
                            additional_messages=[inc_msg],
                            rationale=["Partial response at ≥6 weeks; room to increase dose."],
                            evidence=[
                                EvidenceItem(variable="Weeks on med", value=str(p.weeks_on_current_antidepressant), fhir_source="Derived"),
                                EvidenceItem(variable="Current dose (mg)", value=str(p.current_dose_mg), fhir_source="MedicationRequest"),
                            ],
                            cap_override=cap,
                        )]
                        out.rationale.append("Trial 1: titrate before considering switch.")
                        out.audit_trail.append("branch:trial1_partial_increase")
                        return state
                    # Fall through to class-based routing for switch

            # no_response or partial-at-max on Trial 1 — fall through to class routing

        # ── PHQ < 10 guard ─────────────────────────────────────────────────────
        if p.phq_current < 10 and not (resp_cat in {"partial", "no_response"} and current_med):
            out.non_med_recommendations.append("PHQ < 10 without follow-up context: no medication recommended.")
            out.rationale.append("PHQ < 10, no valid follow-up context.")
            return state

        # ================================================================
        # CLASS-BASED ROUTING (Rules 1–5)
        # ================================================================
        ssri_tried = "SSRI" in classes_tried
        snri_tried = "SNRI" in classes_tried
        ndri_tried = "NDRI" in classes_tried
        nassa_tried = "NaSSA" in classes_tried
        tca_tried = "TCA" in classes_tried

        # ── RULE 5: Advanced Interventions ─────────────────────────────────────
        rule5 = (
            tca_tried
            or (p.phq_current >= 20 and p.suicidality != "none")
            or p.psychosis_positive
        )
        if rule5:
            out.audit_trail.append("route:rule5_advanced")
            out.non_med_recommendations.append(
                "MANDATORY PSYCHIATRIC REFERRAL — This patient requires advanced "
                "interventions that cannot be managed in primary care. "
                "Initiate urgent psychiatric referral."
            )
            out.warnings.append(
                "Mandatory psychiatric referral — advanced interventions required."
            )
            out.non_med_recommendations.extend([
                "ECT: Most effective for severe, psychotic, or catatonic depression. "
                "Preferred in older adults. Requires hospital or ECT suite. [110, 111]",
                "TMS: FDA-approved for TRD. Non-invasive. Accelerated theta-burst "
                "protocols also effective. Requires TMS clinic. [110]",
                "IV Ketamine: Off-label for TRD. Noninferior to ECT (55% vs 41% response "
                "rate) with less memory impairment. Requires monitored infusion setting. [110]",
                "Esketamine (Spravato): FDA-approved for TRD (2+ failed trials) and MDD "
                "with acute suicidal ideation. Requires REMS-certified treatment center. [110, 111]",
            ])
            out.rationale.append(
                f"{trial_label}: advanced interventions required [110, 111]."
            )
            return state

        # ── RULE 4: Hard Psychiatric Consultation (SSRI+SNRI+bup/mirt) ─────────
        if ssri_tried and snri_tried and (ndri_tried or nassa_tried):
            out.audit_trail.append("route:rule4_hard_consult")
            # Hard consultation block FIRST
            out.warnings.append(
                "Psychiatric Consultation Required — This patient has failed adequate "
                "trials across 3 antidepressant classes. Tricyclic antidepressants (TCAs) "
                "are the next medication option but must not be initiated without "
                "psychiatric input. [108, 109]"
            )
            out.non_med_recommendations.extend([
                "PCP actions while awaiting consultation:",
                "Continue current antidepressant at current dose [105]",
                "Optimize psychotherapy — face-to-face referral required at this severity [99, 100]",
                "Reassess diagnosis — rule out bipolar disorder, substance use, "
                "medical contributors [104]",
                "Confirm adherence — approximately 46% of apparent TRD is "
                "pseudo-resistance due to non-adherence [104]",
                "Monitor PHQ-9 and suicidality at every visit [105]",
                "Consider adjunctive options within PCP scope: omega-3s, exercise [64, 65]",
                "Do not initiate TCAs until psychiatric input is obtained. [108, 109]",
                "If consultation wait exceeds 4-6 weeks, consider collaborative "
                "care model where psychiatrist provides indirect supervision. [105]",
            ])
            # TCA options below, clearly labeled pending psychiatric input
            for tca_key in ["nortriptyline", "desipramine"]:
                if can_recommend(tca_key):
                    out.recommendations.append(_make_reco_with_notes(
                        tca_key, intent="start",
                        extra_messages=[
                            "Pending psychiatric consultation — do not initiate "
                            "without psychiatric input [108, 109]",
                        ],
                        extra_rationale=[
                            f"{trial_label}: TCA option pending psychiatric input [108, 109]."
                        ],
                        evidence=[
                            EvidenceItem(variable="Classes failed", value=str(sorted(classes_tried)), fhir_source="Derived"),
                        ],
                    ))
            out.rationale.append(
                f"{trial_label}: hard psychiatric consultation required [108, 109]."
            )
            return state

        # ── RULE 3: TRD Step 2 (SSRI+SNRI tried, bup/mirt not tried) ──────────
        if ssri_tried and snri_tried and not ndri_tried and not nassa_tried:
            out.audit_trail.append("route:rule3_trd_step2")
            # Soft TRD safety flag
            out.warnings.append(
                "Treatment-Resistant Depression — patient has failed adequate trials "
                "of 2 antidepressant classes (SSRI and SNRI). "
                "Consider psychiatric consultation. [104, 105]"
            )
            # Bupropion
            if can_recommend("bupropion_xl"):
                bup_msgs = [
                    "Preferred if hypersomnia, fatigue, weight gain, sexual dysfunction, "
                    "or prominent anergia [106, 28]",
                ]
                out.recommendations.append(_make_reco_with_notes(
                    "bupropion_xl", intent="start",
                    extra_messages=bup_msgs,
                    extra_rationale=[f"{trial_label}: bupropion — NDRI class [106, 28]."],
                    evidence=[
                        EvidenceItem(variable="Classes failed", value="SSRI, SNRI", fhir_source="Derived"),
                    ],
                ))
            # Mirtazapine
            if can_recommend("mirtazapine"):
                mirt_msgs = [
                    "Preferred if insomnia, decreased appetite, weight loss, "
                    "or anxiety [107, 28]",
                ]
                out.recommendations.append(_make_reco_with_notes(
                    "mirtazapine", intent="start",
                    extra_messages=mirt_msgs,
                    extra_rationale=[f"{trial_label}: mirtazapine — NaSSA class [107, 28]."],
                    evidence=[
                        EvidenceItem(variable="Classes failed", value="SSRI, SNRI", fhir_source="Derived"),
                    ],
                ))
            # Soft consultation block AFTER medications
            out.non_med_recommendations.append(
                "Psychiatric Consultation — Recommended: This patient meets criteria "
                "for treatment-resistant depression. Consider referral to psychiatry "
                "for co-management. Primary care may continue managing while "
                "consultation is arranged. [104, 105]"
            )
            # Switching protocol fires based on current med
            out.rationale.append(
                f"{trial_label}: SSRI and SNRI classes failed — bupropion and "
                "mirtazapine recommended [102, 103, 106, 107]."
            )
            return state

        # ── RULE 2: SSRI tried, SNRI not tried ────────────────────────────────
        if ssri_tried and not snri_tried:
            out.audit_trail.append("route:rule2_snri_switch")
            # Venlafaxine XR
            if can_recommend("venlafaxine_xr"):
                out.recommendations.append(_make_reco_with_notes(
                    "venlafaxine_xr", intent="switch_to",
                    extra_messages=[
                        _switch_taper_message(current_med, "venlafaxine_xr", p.current_dose_mg) if current_med else "",
                        "First SNRI option after SSRI failure — adds norepinephrine mechanism [102, 103, 105]",
                    ],
                    extra_rationale=["Trial 2: SNRI switch after SSRI failure [102, 103]."],
                    evidence=[
                        EvidenceItem(variable="Classes failed", value="SSRI", fhir_source="Derived"),
                    ],
                ))
            # Duloxetine
            if can_recommend("duloxetine"):
                out.recommendations.append(_make_reco_with_notes(
                    "duloxetine", intent="switch_to",
                    extra_messages=[
                        _switch_taper_message(current_med, "duloxetine", p.current_dose_mg) if current_med else "",
                        "Alternative SNRI — preferred if comorbid chronic pain [102, 103]",
                    ],
                    extra_rationale=["Trial 2: SNRI switch after SSRI failure [102, 103]."],
                    evidence=[
                        EvidenceItem(variable="Classes failed", value="SSRI", fhir_source="Derived"),
                    ],
                ))
            out.rationale.append(
                "Trial 2: SSRI class trialed — switching to SNRI class [102, 103]."
            )
            return state

        # ── RULE 1: First-line / next class ──────────────────────────────────
        out.audit_trail.append("route:rule1_first_line")
        # Determine intent: switch_to when current med has failed, start otherwise
        _r1_intent: RecommendationIntent = "switch_to" if current_med_failed else "start"
        _r1_rationale = (
            f"{trial_label}: switching from failed {MED_KB.get(current_med, {}).get('class', '')} "
            f"— next class recommended [19, 20, 26, 102]."
            if current_med_failed
            else "Trial 1: first-line selection [19, 20, 26]."
        )
        # Standard first-line set: escitalopram, sertraline, bupropion
        first_line = ["escitalopram", "sertraline", "bupropion_xl"]
        # Add comorbidity-driven options
        if p.insomnia and can_recommend("mirtazapine"):
            first_line.append("mirtazapine")
        if (p.fibromyalgia or p.chronic_pain) and can_recommend("duloxetine"):
            first_line.append("duloxetine")
        if p.cardiac_history:
            # Move sertraline to front
            if "sertraline" in first_line:
                first_line.remove("sertraline")
                first_line.insert(0, "sertraline")

        for m in first_line:
            if can_recommend(m):
                _r1_msg = (
                    _switch_taper_message(current_med, m, p.current_dose_mg)
                    if current_med_failed and current_med else
                    "Initiate; titrate every 1–2 weeks; reassess at 6 weeks for response. [3, 4]"
                )
                out.recommendations.append(_make_reco_with_notes(
                    m, intent=_r1_intent,
                    extra_messages=[_r1_msg],
                    extra_rationale=[_r1_rationale],
                    evidence=[
                        EvidenceItem(variable="PHQ-9 current", value=str(p.phq_current), fhir_source="Observation"),
                        EvidenceItem(variable="Active paths", value=str(pathways), fhir_source="Derived"),
                    ],
                    cap_override=max_cap_for_context(p, m, pathways),
                ))

        if not out.recommendations:
            out.warnings.append("All candidates blocked; clinician review required.")
            out.rationale.append("All options blocked or excluded by history.")
        else:
            out.rationale.append(
                f"{trial_label}: switching from failed medication — next class recommended."
                if current_med_failed
                else "Trial 1: first-line selection per all active path(s)."
            )
        return state


def _discontinuation_taper_note(p: PatientInput) -> str:
    """Return a medication-specific taper note for the maintenance plan."""
    med = p.current_antidepressant_key
    if med and med in EXTENDED_TAPER_MEDS:
        disp = MED_KB.get(med, {}).get("display", med)
        return (
            f"Tapering — {disp}: EXTENDED taper required (high discontinuation syndrome "
            f"risk). Reduce by 25% every 2 weeks; hold at lowest available dose ≥4 weeks "
            f"before stopping. Consider hyperbolic taper for long-term users. "
            f"[87, 88, 93, 94]"
        )
    return (
        "Taper slowly on discontinuation — recommend MoodCalmer dCBT alongside tapering "
        "to support psychological adjustment. [25, 96, 97]"
    )


class OutputCompletionStage(Stage):
    """
    Populates the five structured output sections (Round 5 of CLAUDE_MDD.md spec):
      1. monitoring_schedule  — standard monitoring table + path-specific additions
      2. maintenance_plan     — based on prior_depressive_episodes
      3. medications_excluded — surfaced from state.exclusion_reasons
      4. adjunctive_options   — Tier 4: omega-3 + celecoxib (with contraindication checks)
      5. reference_list       — all [Xn] citations found in output text, resolved from REFERENCE_DB
    """
    name = "output_completion"

    def run(self, state: WorkingState) -> WorkingState:
        import re as _re
        p   = state.patient
        out = state.output

        # 0. Serotonin syndrome burden check ─────────────────────────────────
        _sero_count = 0
        _sero_sources: List[str] = []
        _pm_norm = {m.lower().strip() for m in (p.current_medications or [])}
        # Check current antidepressant
        if p.current_antidepressant_key and p.current_antidepressant_key in SEROTONERGIC_AD_KEYS:
            _sero_count += 1
            _sero_sources.append(p.current_antidepressant_key)
        # Check existing co-medications for serotonergic agents
        _SERO_COMED_TERMS = {
            "tramadol", "fentanyl", "meperidine", "methadone", "tapentadol",
            "linezolid", "methylene blue", "dextromethorphan", "triptans",
            "sumatriptan", "lithium", "buspirone",
        }
        _OPIOID_SERO_TERMS = {"tramadol", "meperidine", "tapentadol", "fentanyl"}
        _current_is_ssri_snri = (
            p.current_antidepressant_key and
            p.current_antidepressant_key in (SSRI_KEYS | SNRI_KEYS)
        )
        for cm in _pm_norm:
            if any(t in cm for t in _SERO_COMED_TERMS):
                _sero_count += 1
                _sero_sources.append(f"co-med: {cm}")
            # Special flag: tramadol/serotonergic opioid + SSRI/SNRI combination
            if any(t in cm for t in _OPIOID_SERO_TERMS) and _current_is_ssri_snri:
                out.warnings.append(
                    f"SEROTONIN SYNDROME RISK — {cm} + {p.current_antidepressant_key}: "
                    f"serotonergic opioid co-prescribed with SSRI/SNRI. "
                    f"This is the most common pharmacodynamic serotonin syndrome "
                    f"interaction. Review necessity or consider opioid substitution. "
                    f"[89, 90, 91]"
                )
        # Augmentation only: serotonergic agent added on top of a current serotonergic AD
        # (start/switch_to are alternatives, not concurrent — never counted here)
        if p.current_antidepressant_key in SEROTONERGIC_AD_KEYS:
            for _r in out.recommendations:
                if _r.medication_key in SEROTONERGIC_AD_KEYS and _r.intent == "augment_with":
                    _sero_count += 1
                    _sero_sources.append(f"augment: {_r.medication_key}")
        if _sero_count >= 2:
            out.warnings.append(
                f"SEROTONIN SYNDROME RISK: {_sero_count} serotonergic agents identified "
                f"({'; '.join(_sero_sources)}). Avoid concurrent serotonergic agents unless "
                f"benefit clearly outweighs risk. Monitor for agitation, diaphoresis, tremor, "
                f"hyperreflexia, clonus, hyperthermia. If suspected: discontinue all "
                f"serotonergic agents and seek emergency evaluation. [89, 90, 91, 98]"
            )
            out.audit_trail.append(f"serotonin_syndrome_risk:count={_sero_count}")

        # 0b. Switching protocol — class-to-class lookup ──────────────────────
        _switch_recs = [_r for _r in out.recommendations if _r.intent == "switch_to"]
        if _switch_recs:
            _outgoing = p.current_antidepressant_key
            _seen_protocols: set = set()  # deduplicate identical (prior, new_cls) pairs
            for _srec in _switch_recs:
                _new_key = _srec.medication_key
                _proto   = get_switching_protocol(_outgoing, _new_key, p.current_dose_mg)
                # Skip rendering if dose optimization (same med, not a switch)
                if _proto.method == "dose_optimization":
                    out.audit_trail.append(
                        f"switching_protocol:dose_optimization:{_outgoing}->{_new_key}"
                    )
                    continue
                _pair_key = (classify_med_for_switch(_outgoing),
                             classify_med_for_switch(_new_key))
                if _pair_key in _seen_protocols:
                    continue
                _seen_protocols.add(_pair_key)
                # Format and append protocol lines
                _lines = _format_switch_protocol_lines(_outgoing, _new_key, _proto, p.current_dose_mg)
                out.switching_protocol.extend(_lines)
                out.switching_protocol.append("")  # blank separator between protocols
                # MAOI washout safety flag
                if _proto.method == "washout":
                    out.warnings.append(
                        f"WASHOUT REQUIRED before starting "
                        f"{MED_KB.get(_new_key, {}).get('display', _new_key)}: "
                        f"{_proto.duration}. {_proto.warning} "
                        f"[{chr(44).join(_proto.citations)}]"
                    )
                # Cross-taper overlap of two serotonergic agents
                if (_proto.method == "cross_taper"
                        and _outgoing in SEROTONERGIC_AD_KEYS
                        and _new_key in SEROTONERGIC_AD_KEYS):
                    out.warnings.append(
                        f"SEROTONIN SYNDROME RISK — cross-taper overlap: "
                        f"{MED_KB.get(_outgoing, {}).get('display', _outgoing)} → "
                        f"{MED_KB.get(_new_key, {}).get('display', _new_key)}. "
                        f"Both agents are serotonergic. Monitor closely during overlap period "
                        f"for agitation, diaphoresis, tremor, hyperreflexia, clonus, "
                        f"hyperthermia. Consider sequential approach if feasible. [89, 90, 91, 98]"
                    )
                    out.audit_trail.append(
                        f"serotonin_syndrome_risk:cross_taper:{_outgoing}->{_new_key}"
                    )
                out.audit_trail.append(
                    f"switching_protocol:{classify_med_for_switch(_outgoing)}"                    f"->{classify_med_for_switch(_new_key)}:method={_proto.method}"
                )
            # Trim trailing blank separator
            while out.switching_protocol and out.switching_protocol[-1] == "":
                out.switching_protocol.pop()
            # FINISH mnemonic when extended taper meds are in the outgoing position
            if _outgoing and _outgoing in EXTENDED_TAPER_MEDS:
                out.switching_protocol.append(
                    "Patient education — FINISH mnemonic: Flu-like symptoms, Insomnia, "
                    "Nausea, Imbalance, Sensory disturbances, Hyperarousal. [28]"
                )

        # 1. Monitoring schedule ────────────────────────────────────────────
        out.monitoring_schedule = [
            "Initiation: baseline weight, BMI, BP. [3]",
            "Week 2: assess tolerability and adherence. [26]",
            "Week 4–6: dose adjustment if inadequate response. [26]",
            "Week 8–12: full response assessment; switch if no response. [26]",
            "Weeks 1–4: close suicidality monitoring — all patients; especially under 25. [73, 74]",
        ]
        if any(r.medication_class == "SGA" for r in out.recommendations
               if r.intent == "augment_with"):
            out.monitoring_schedule.append(
                "Antipsychotic augmentation: baseline lipids and HbA1c; BMI monthly ×3 then "
                "quarterly; BP, lipids, HbA1c at 3 months then annually. [3]"
            )

        # 2. Maintenance plan ───────────────────────────────────────────────
        episodes = p.prior_depressive_episodes
        if episodes is None:
            out.maintenance_plan = [
                "Episode history unknown: discuss maintenance duration with patient. "
                "[2, 4, 18, 70, 71, 72]",
                _discontinuation_taper_note(p),
            ]
        elif episodes == 0:
            _taper_note_0 = _discontinuation_taper_note(p)
            out.maintenance_plan = [
                "First episode: continue medication 6–9 months after remission. [2, 4, 71]",
                _taper_note_0,
            ]
        elif episodes == 1:
            _taper_note_1 = _discontinuation_taper_note(p)
            out.maintenance_plan = [
                "Recurrent depression (1 prior episode): continue at least 2 years. [18, 70, 71, 72]",
                "Discuss long-term risk; consider extending if high relapse risk. [2, 4]",
                _taper_note_1,
            ]
        else:
            out.maintenance_plan = [
                f"Recurrent depression ({episodes} prior episodes): consider indefinite "
                "continuation due to high relapse risk. [2, 4, 18, 70, 71, 72]",
                _discontinuation_taper_note(p),
            ]

        # 3. Medications excluded ───────────────────────────────────────────
        if state.exclusion_reasons:
            out.medications_excluded = [
                f"{MED_KB.get(med, {}).get('display', med)}: {reason}"
                for med, reason in sorted(state.exclusion_reasons.items())
            ]
        else:
            out.medications_excluded = [
                "No medications excluded by deviation path rules for this patient context."
            ]

        # 4. Adjunctive options — Tier 4 ──────────────────────────────────────
        out.adjunctive_options.append(
            "Omega-3 fatty acids (EPA ≥60%, 1–1.5 g/day): SOR B. Small benefit "
            "(SMD −0.40), very low certainty; VA/DoD found insufficient evidence to recommend "
            "over validated medications. May consider adding. "
            "[4, 64, 65, 66, 67, 68]"
        )
        renal_val = p.crcl_ml_min if p.crcl_ml_min is not None else p.egfr_ml_min_1_73
        celecoxib_ci: List[str] = []
        if p.cardiac_history:
            celecoxib_ci.append("cardiac history")
        if renal_val is not None and renal_val < 60:
            celecoxib_ci.append(f"eGFR/CrCl {renal_val} < 60")
        if celecoxib_ci:
            out.adjunctive_options.append(
                f"Celecoxib 400 mg/day ×6 weeks: CONTRAINDICATED in this patient "
                f"({'; '.join(celecoxib_ci)}). Do not prescribe. [60, 61, 63]"
            )
        else:
            out.adjunctive_options.append(
                "Celecoxib 400 mg/day ×6 weeks: SOR B. Moderate benefit (SMD −0.82, "
                "OR for remission 7.89) but high risk of bias. Confirm no cardiac history, "
                "eGFR ≥60, no NSAID contraindications before prescribing. May consider adding. "
                "[60, 61, 63]"
            )

        # 5. Reference list ─────────────────────────────────────────────────
        all_text = " ".join([
            *out.findings, *out.rationale, *out.warnings,
            *out.non_med_recommendations, *out.monitoring_schedule,
            *out.maintenance_plan, *out.adjunctive_options,
            *[m for r in out.recommendations for m in r.messages + r.rationale],
        ])
        cited: Set[str] = set()
        for _m in _re.finditer(r'\[(\d+(?:[,\s]+\d+)*)\]', all_text):
            for _num in _re.split(r'[,\s]+', _m.group(1)):
                _num = _num.strip()
                if _num:
                    cited.add(_num)
        # Sort by plain consolidated number
        def _sort_key(k: str) -> int:
            try:
                return int(k)
            except (ValueError, TypeError):
                return 9999
        out.reference_list = [
            REFERENCE_DB[k]
            for k in sorted(cited, key=_sort_key)
            if k in REFERENCE_DB
        ]
        # Always include monitoring anchor refs
        for k in ["26", "73", "74", "3", "4"]:
            entry = REFERENCE_DB.get(k)
            if entry and entry not in out.reference_list:
                out.reference_list.append(entry)

        return state



# ============================================================
# Report formatter helpers (section 9 — final output format)
# ============================================================
_CITE_RE = re.compile(r'\s*\[\d+(?:[,\s]+\d+)*\]')


def _phq_tier(phq: int) -> str:
    if phq < 5:  return "minimal"
    if phq < 10: return "mild"
    if phq < 15: return "moderate"
    if phq < 20: return "moderate-severe"
    return "severe"


def _phq_label(phq: int) -> str:
    tier = _phq_tier(phq)
    ranges = {
        "minimal":        "0\u20134",
        "mild":           "5\u20139",
        "moderate":       "10\u201314",
        "moderate-severe":"15\u201319",
        "severe":         "20\u201327",
    }
    return f"{tier.title()} (PHQ {ranges[tier]})"


def _strip_cites(text: str) -> str:
    text = _CITE_RE.sub("", text)
    # Remove comma/semicolon debris left between adjacent stripped brackets
    text = re.sub(r'(?<=[.,])\s*,+', '', text)
    text = re.sub(r',\s*$', '', text.rstrip())
    return text.strip()


def _build_patient_summary(p: "PatientInput", out: "AlgorithmOutput") -> dict:
    comorbidities: List[str] = []
    if p.insomnia:             comorbidities.append("insomnia")
    if p.fibromyalgia:         comorbidities.append("fibromyalgia/chronic pain")
    if p.anxiety_comorbidity:  comorbidities.append("anxiety")
    if p.cardiac_history:      comorbidities.append("cardiac history")
    if p.hepatic_impairment:   comorbidities.append("hepatic impairment")
    if p.pregnant:             comorbidities.append("pregnant")
    if p.dementia:             comorbidities.append("dementia")

    flags: List[str] = []
    if p.suicidality != "none":                        flags.append(f"suicidality={p.suicidality}")
    if p.chronic_suicidality:                          flags.append("chronic suicidality")
    if p.qtc_ms is not None and p.qtc_ms > 450:        flags.append(f"QTc={p.qtc_ms}ms")

    summary: dict = {
        "age": p.age,
        "phq_score": p.phq_current,
        "severity": _phq_label(p.phq_current),
        "trial_number": p.trial_number or 1,
    }
    if p.current_antidepressant_key:
        summary["current_medication"] = p.current_antidepressant_key
        summary["weeks_on_treatment"] = p.weeks_on_current_antidepressant
    if p.baseline_phq is not None and p.baseline_phq > 0:
        pct = round((p.baseline_phq - p.phq_current) / p.baseline_phq * 100)
        summary["phq_improvement_pct"] = pct
    if comorbidities:
        summary["comorbidities"] = comorbidities
    if flags:
        summary["notable_flags"] = flags
    if p.therapy_preference:
        summary["therapy_preference"] = p.therapy_preference
    return summary


def _build_safety_flags(out: "AlgorithmOutput") -> List[str]:
    return [_strip_cites(w) for w in out.warnings]


def _build_active_pathways(out: "AlgorithmOutput") -> List[str]:
    default = {"adult"}
    return [p for p in out.pathway_applied if p not in default]


def _build_medication_entries(p: "PatientInput", out: "AlgorithmOutput") -> List[dict]:
    entries: List[dict] = []
    for rec in out.recommendations:
        if rec.intent not in ("start", "continue", "switch_to", "increase"):
            continue
        entry: dict = {
            "medication": rec.medication_display,
            "class": rec.medication_class,
            "intent": rec.intent,
        }
        if rec.intent == "start":
            entry["dose"] = f"Start: {rec.start_dose} \u2192 Target: {rec.dose_range}"
        elif rec.intent == "switch_to":
            # Check if taper schedule exists for this switch
            _sw_proto = get_switching_protocol(
                p.current_antidepressant_key, rec.medication_key, p.current_dose_mg
            )
            if _sw_proto.method == "dose_optimization":
                dose_curr = f"{p.current_dose_mg} mg" if p.current_dose_mg else "current"
                entry["dose"] = f"Current: {dose_curr} \u2192 Target: {rec.dose_range}"
            elif _sw_proto.taper_steps and _sw_proto.method != "direct_switch":
                entry["dose"] = f"Dosing: Refer to Switching Protocol \u2192 Target: {rec.dose_range}"
            else:
                entry["dose"] = f"Start: {rec.start_dose} \u2192 Target: {rec.dose_range}"
        else:  # continue / increase
            dose_curr = f"{p.current_dose_mg} mg" if p.current_dose_mg else "current"
            entry["dose"] = f"Current: {dose_curr} \u2192 Target: {rec.dose_range}"
        if rec.messages:
            entry["notes"] = [_strip_cites(m) for m in rec.messages if m and m.strip()]
        entries.append(entry)
    return entries


def _build_therapy_rec(p: "PatientInput", out: "AlgorithmOutput") -> Optional[dict]:
    tier = _phq_tier(p.phq_current)
    if tier == "minimal":
        return None
    if tier == "mild":
        return {
            "level": "self-directed digital CBT",
            "recommendation": "MoodCalmer dCBT \u2014 self-guided internet-based CBT program",
            "format": "digital self-directed",
            "references": ["99", "101"],
        }
    elif tier == "moderate":
        return {
            "level": "shared decision",
            "recommendation": (
                "Psychotherapy (CBT, IPT) alongside medication or as first-line; "
                "share decision with patient"
            ),
            "format": "individual face-to-face or structured digital",
            "references": ["1", "2", "3", "4", "100"],
        }
    else:  # moderate-severe / severe
        return {
            "level": "recommended combination",
            "recommendation": (
                "Face-to-face psychotherapy (CBT or IPT) combined with medication \u2014 "
                "combination superior to either alone at PHQ \u226515"
            ),
            "format": "individual face-to-face psychotherapy",
            "references": ["1", "3", "4", "100"],
        }


def _build_switch_entries(out: "AlgorithmOutput") -> List[dict]:
    if not out.switching_protocol:
        return []
    entries: List[dict] = []
    current: dict = {}
    in_taper = False
    for line in out.switching_protocol:
        line = line.strip()
        if not line:
            if current:
                entries.append(current)
                current = {}
            in_taper = False
            continue
        if line.startswith("Prior:") or line.startswith("Prior medication:"):
            current["prior"] = line.split(":", 1)[1].strip()
        elif line.startswith("New:") or line.startswith("New medication:"):
            current["new"] = line.split(":", 1)[1].strip()
        elif line.startswith("Method:"):
            current["method"] = line.replace("Method:", "").strip()
        elif line.startswith("Estimated duration:") or line.startswith("Duration:"):
            current["duration"] = line.split(":", 1)[1].strip()
        elif line.startswith("Taper schedule:"):
            in_taper = True
            current.setdefault("taper_steps", [])
        elif in_taper and line.startswith("  "):
            current.setdefault("taper_steps", []).append(line.strip())
        elif line.startswith("New medication initiation:"):
            in_taper = False
            current["new_med_timing"] = line.replace("New medication initiation:", "").strip()
        elif line.startswith("Clinical note:"):
            in_taper = False
            current["clinical_note"] = _strip_cites(line.replace("Clinical note:", "").strip())
        elif line.startswith("\u26a0"):
            in_taper = False
            current["warning"] = _strip_cites(line[1:].strip())
        elif line.startswith("Note:"):
            in_taper = False
            current["disclaimer"] = _strip_cites(line.replace("Note:", "").strip())
        elif line.startswith("References:"):
            in_taper = False
        elif line.startswith("Warning:"):
            in_taper = False
            current["warning"] = _strip_cites(line.replace("Warning:", "").strip())
        elif line.startswith("Safety flag:") or line.startswith("\u2139"):
            in_taper = False
            current.setdefault("safety_flags", []).append(_strip_cites(line))
        elif "FINISH" in line:
            in_taper = False
            current.setdefault("mnemonics", []).append(_strip_cites(line))
        else:
            in_taper = False
    if current:
        entries.append(current)
    return entries


def _build_meds_excluded(out: "AlgorithmOutput") -> List[str]:
    return [
        _strip_cites(m) for m in out.medications_excluded
        if not m.lower().startswith("no medications excluded by deviation path")
    ]


def _build_augmentation_entries(out: "AlgorithmOutput") -> List[dict]:
    entries: List[dict] = []
    for rec in out.recommendations:
        if rec.intent != "augment_with":
            continue
        entry: dict = {
            "medication": rec.medication_display,
            "class": rec.medication_class,
            "dose": f"Target: {rec.dose_range}",
        }
        if rec.rationale:
            entry["rationale"] = _strip_cites(rec.rationale[0])
        entries.append(entry)
    return entries


def _build_next_check_in(p: "PatientInput", out: "AlgorithmOutput") -> str:
    has_switch = any(r.intent == "switch_to" for r in out.recommendations)
    has_start  = any(r.intent == "start"     for r in out.recommendations)
    if has_switch or has_start:
        return "Week 2: tolerability check and adherence assessment"
    # Adequate response / remission — next check-in based on maintenance duration
    if out.response_category == "remission_or_response":
        episodes = p.prior_depressive_episodes
        if episodes is None:
            return "Month 3: maintenance reassessment — discuss duration with patient"
        elif episodes == 0:
            return "Month 6\u20139: reassess for continuation vs taper (first episode)"
        elif episodes == 1:
            return "Month 6: reassess maintenance — continue at least 2 years (recurrent)"
        else:
            return "Month 6: reassess maintenance — consider indefinite continuation (recurrent)"
    if p.phq_current <= 9:
        return "Week 8\u201312: reassess PHQ-9 and response to treatment"
    weeks = p.weeks_on_current_antidepressant or 0
    if weeks < 6:
        return "Week 4\u20136: dose adjustment assessment"
    return "Week 8\u201312: full response assessment"


def _collect_citations_from(*text_lists: List[str]) -> List[str]:
    pat = re.compile(r'\[(\d+(?:[,\s]+\d+)*)\]')
    nums: Set[str] = set()
    for texts in text_lists:
        for t in (texts or []):
            for m in pat.finditer(t):
                for n in re.split(r'[,\s]+', m.group(1)):
                    if n.strip():
                        nums.add(n.strip())
    return sorted(nums, key=lambda x: int(x))


def _build_references(cite_nums: List[str]) -> dict:
    return {n: REFERENCE_DB[n] for n in cite_nums if n in REFERENCE_DB}


def _format_text_report(report: dict) -> str:
    SEP  = "\u2500" * 70
    SEP2 = "\u2550" * 70
    lines: List[str] = []

    lines.append(SEP2)
    lines.append("  MDD CLINICAL DECISION SUPPORT \u2014 REPORT")
    lines.append(SEP2)

    ps = report.get("patient_summary", {})
    lines.append(
        f"\n  Patient: age {ps.get('age')}, "
        f"PHQ-9 = {ps.get('phq_score')} ({ps.get('severity', '')})"
    )
    lines.append(f"  Trial #{ps.get('trial_number', 1)}")
    if ps.get("current_medication"):
        lines.append(f"  Current: {ps['current_medication']}, {ps.get('weeks_on_treatment', '?')} weeks")
        if ps.get("phq_improvement_pct") is not None:
            _pct = ps['phq_improvement_pct']
            if _pct < 0:
                lines.append(f"  PHQ change: {abs(_pct)}% worsening")
            else:
                lines.append(f"  PHQ change: {_pct}% improvement")
    if ps.get("comorbidities"):
        lines.append(f"  Comorbidities: {', '.join(ps['comorbidities'])}")

    if report.get("safety_flags"):
        lines.append(f"\n{SEP}")
        lines.append("  SAFETY FLAGS")
        lines.append(SEP)
        for flag in report["safety_flags"]:
            lines.append(f"  \u26a0  {flag}")

    if report.get("active_pathways"):
        lines.append(f"\n{SEP}")
        lines.append("  ACTIVE PATHWAYS")
        lines.append(SEP)
        for path in report["active_pathways"]:
            lines.append(f"  \u2022 {path}")

    recs   = report.get("recommendations", {})
    meds   = recs.get("medications", [])
    therapy = recs.get("therapy")
    if meds or therapy:
        lines.append(f"\n{SEP}")
        lines.append("  RECOMMENDATIONS")
        lines.append(SEP)
        if meds:
            lines.append("  Medications:")
            for i, m in enumerate(meds, 1):
                lines.append(f"    [{i}] {m['medication']}  ({m['intent']})")
                lines.append(f"        Dose: {m.get('dose', '')}")
                for note in m.get("notes", []):
                    lines.append(f"        \u2192 {note}")
        if therapy:
            lines.append("  Therapy:")
            lines.append(f"    Level: {therapy.get('level', '').title()}")
            lines.append(f"    {therapy.get('recommendation', '')}")
            lines.append(f"    Format: {therapy.get('format', '').title()}")

    if report.get("switching_protocol"):
        lines.append(f"\n{SEP}")
        lines.append("  SWITCHING PROTOCOL")
        lines.append(SEP)
        for entry in report["switching_protocol"]:
            if entry.get("prior"):
                lines.append(f"  Prior: {entry['prior']}")
            if entry.get("new"):
                lines.append(f"  New:   {entry['new']}")
            if entry.get("method"):
                _dur = entry.get("duration", "")
                if _dur and "n/a" not in _dur.lower():
                    lines.append(f"  Method: {entry['method']}  |  Duration: {_dur}")
                else:
                    lines.append(f"  Method: {entry['method']}")
            if entry.get("warning"):
                lines.append(f"  \u26a0  {entry['warning']}")
            for f in entry.get("safety_flags", []):
                lines.append(f"  \u2139  {f}")
            for mn in entry.get("mnemonics", []):
                lines.append(f"  \u2139  {mn}")

    if report.get("medications_excluded"):
        lines.append(f"\n{SEP}")
        lines.append("  MEDICATIONS EXCLUDED")
        lines.append(SEP)
        for exc in report["medications_excluded"]:
            lines.append(f"  \u2717  {exc}")

    if report.get("augmentation_plan"):
        lines.append(f"\n{SEP}")
        lines.append("  AUGMENTATION PLAN")
        lines.append(SEP)
        for i, aug in enumerate(report["augmentation_plan"], 1):
            lines.append(f"  [{i}] {aug['medication']}")
            lines.append(f"      Dose: {aug.get('dose', '')}")
            if aug.get("rationale"):
                lines.append(f"      {aug['rationale']}")

    if report.get("maintenance_plan"):
        lines.append(f"\n{SEP}")
        lines.append("  MAINTENANCE PLAN")
        lines.append(SEP)
        for mp in report["maintenance_plan"]:
            lines.append(f"  \u2022 {mp}")

    if report.get("relapse_prevention"):
        lines.append(f"\n{SEP}")
        lines.append("  RELAPSE PREVENTION")
        lines.append(SEP)
        for rp in report["relapse_prevention"]:
            lines.append(f"  \u2022 {rp}")

    if report.get("next_check_in"):
        lines.append(f"\n{SEP}")
        lines.append("  NEXT CHECK-IN")
        lines.append(SEP)
        lines.append(f"  {report['next_check_in']}")

    if report.get("references"):
        lines.append(f"\n{SEP}")
        lines.append("  REFERENCES")
        lines.append(SEP)
        _seen_ref_nums: Set[str] = set()
        for _sec, _refs in report["references"].items():
            lines.append(f"\n  [{_sec}]")
            for _ref in _refs:
                _num = _ref.split(".")[0].strip()
                if _num not in _seen_ref_nums:
                    lines.append(f"  {_ref}")
                    _seen_ref_nums.add(_num)

    lines.append(f"\n{SEP2}")
    return "\n".join(lines)


class CitationTracker:
    """
    Tracks which reference numbers were cited in which report section.
    Instantiated once per run_algorithm() call inside ReportFormatterStage.
    """

    _CITE_RE = re.compile(r'\[(\d+(?:[,\s]+\d+)*)\]')

    SECTION_ORDER: List[str] = [
        "Recommended Medications",
        "Therapy",
        "Switching Protocol",
        "Augmentation Plan",
        "Maintenance Plan",
        "Next Check-In",
        "Safety Flags",
        "Medications Excluded",
    ]

    def __init__(self) -> None:
        self._sections: Dict[str, List[str]] = {}
        self._seen_per_section: Dict[str, Set[str]] = {}

    def cite(self, ref_num: str, section: str) -> None:
        """Record a single reference number for a section (deduplicated per section)."""
        if section not in self._sections:
            self._sections[section] = []
            self._seen_per_section[section] = set()
        if ref_num not in self._seen_per_section[section]:
            self._sections[section].append(ref_num)
            self._seen_per_section[section].add(ref_num)

    def cite_from_texts(self, texts: List[str], section: str) -> None:
        """Extract every [n] citation from a list of strings and record it for section."""
        for text in (texts or []):
            for m in self._CITE_RE.finditer(text):
                for n in re.split(r'[,\s]+', m.group(1)):
                    n = n.strip()
                    if n:
                        self.cite(n, section)

    def build(self) -> Dict[str, List[str]]:
        """Return {section_name: [full citation strings]} in SECTION_ORDER."""
        result: Dict[str, List[str]] = {}
        for sec in self.SECTION_ORDER:
            if sec in self._sections and self._sections[sec]:
                nums = sorted(self._sections[sec], key=lambda x: int(x))
                refs = [REFERENCE_DB[n] for n in nums if n in REFERENCE_DB]
                if refs:
                    result[sec] = refs
        return result

    @property
    def all_nums(self) -> List[str]:
        """All unique cited reference numbers, sorted numerically."""
        seen: Set[str] = set()
        for nums in self._sections.values():
            seen.update(nums)
        return sorted(seen, key=lambda x: int(x))

    @property
    def unique_count(self) -> int:
        return len(self.all_nums)


class ReportFormatterStage(Stage):
    name = "report_formatter"

    def run(self, state: "WorkingState") -> "WorkingState":
        p   = state.patient
        out = state.output

        patient_summary  = _build_patient_summary(p, out)
        safety_flags     = _build_safety_flags(out)
        active_pathways  = _build_active_pathways(out)
        medications      = _build_medication_entries(p, out)
        therapy          = _build_therapy_rec(p, out)
        switch_entries   = _build_switch_entries(out)
        meds_excluded    = _build_meds_excluded(out)
        augmentation     = _build_augmentation_entries(out)
        next_check_in    = _build_next_check_in(p, out)

        # Per-section citation tracking
        tracker = CitationTracker()
        tracker.cite_from_texts(
            [m for rec in out.recommendations
               for m in (list(rec.messages) + list(rec.rationale))
               if rec.intent != "augment_with"],
            "Recommended Medications",
        )
        tracker.cite_from_texts(
            [m for rec in out.recommendations
               for m in (list(rec.messages) + list(rec.rationale))
               if rec.intent == "augment_with"]
            + list(out.adjunctive_options or []),
            "Augmentation Plan",
        )
        if therapy:
            for _n in therapy.get("references", []):
                tracker.cite(_n, "Therapy")
        tracker.cite_from_texts(out.switching_protocol, "Switching Protocol")
        tracker.cite_from_texts(out.warnings, "Safety Flags")
        tracker.cite_from_texts(out.medications_excluded, "Medications Excluded")
        tracker.cite_from_texts(out.maintenance_plan, "Maintenance Plan")
        tracker.cite_from_texts(
            [next_check_in] if next_check_in else [], "Next Check-In"
        )
        references = tracker.build()

        # ── Response-driven section gating ─────────────────────────────────
        resp = out.response_category  # "remission_or_response", "partial", "no_response", or None
        trial_n = p.trial_number or 1

        report: dict = {"patient_summary": patient_summary}
        if resp:
            report["response_category"] = resp
        if safety_flags:
            report["safety_flags"] = safety_flags
        if active_pathways:
            report["active_pathways"] = active_pathways

        recs_section: dict = {}
        # Partial response (Trial 2/3): suppress primary medication list, show augmentation
        # Adequate/remission: suppress primary medication list, show maintenance
        # Inadequate: show primary medication list (switch options), suppress augmentation
        if resp == "partial" and trial_n >= 2:
            # No primary medication list — augmentation plan replaces it
            pass
        elif resp == "remission_or_response":
            # No primary medication list — maintenance plan replaces it
            pass
        else:
            if medications:
                recs_section["medications"] = medications
        if therapy:
            recs_section["therapy"] = therapy
        if recs_section:
            report["recommendations"] = recs_section

        # Switching protocol only for inadequate response (switch path)
        if resp != "partial" and switch_entries:
            report["switching_protocol"] = switch_entries
        if meds_excluded:
            report["medications_excluded"] = meds_excluded

        # Augmentation plan only for partial response at Trial 2/3
        if resp == "partial" and trial_n >= 2 and augmentation:
            report["augmentation_plan"] = augmentation

        # Maintenance plan for adequate response / remission
        if resp == "remission_or_response" and out.maintenance_plan:
            report["maintenance_plan"] = out.maintenance_plan
            # MoodCalmer dCBT for relapse prevention
            report.setdefault("relapse_prevention", []).append(
                "MoodCalmer dCBT — digital cognitive behavioral therapy for relapse prevention"
            )

        report["next_check_in"] = next_check_in
        report["references"] = references

        out.report      = report
        out.text_report = _format_text_report(report)
        return state


class FinalizeStage(Stage):
    name = "finalize"

    def run(self, state: WorkingState) -> WorkingState:
        out = state.output
        seen: Set[str] = set()
        deduped: List[str] = []
        for w in out.warnings:
            if w not in seen:
                deduped.append(w)
                seen.add(w)
        out.warnings = deduped
        if not out.recommendations and not out.non_med_recommendations and not out.stop_reason:
            out.non_med_recommendations.append("No recommendation generated — clinician review required.")
            out.rationale.append("Insufficient data or all options blocked.")
        return state


# ------------------------------------------------------------
# 11) Engine
# ------------------------------------------------------------
class MDDEngine:
    """
    MDD algorithm engine with multi-path routing (Step 2 of CLAUDE_MDD.md).

    detect_active_paths() fires ALL applicable deviation paths simultaneously.
    Each path contributes exclusions, dose caps, and preferred-medication
    ordering. Cross-path conflicts are surfaced in output.path_conflicts
    rather than silently resolved.

    Pipeline:
      findings → pathway (multi) → mania exclusion → QTc safety →
      severity/non-med → med safety → clinical contraindications
      (all-path exclusions + conflict detection) → dose sanity →
      treatment selection (multi-path pool) → finalize
    """
    def __init__(self) -> None:
        self.stages: List[Stage] = [
            FindingsStage(),
            PathwayStage(),
            SuicidalityScreenStage(),
            ManiaExclusionStage(),
            QTcSafetyStage(),
            SeverityAndNonMedStage(),
            MedSafetyStage(),
            ClinicalContraindicationStage(),
            DoseSanityStage(),
            TreatmentSelectionStage(),
            OutputCompletionStage(), ReportFormatterStage(),
            FinalizeStage(),
        ]

    def run(self, patient: PatientInput) -> AlgorithmOutput:
        state = WorkingState(
            patient=patient,
            output=AlgorithmOutput(),
            blocked_candidates=set(),
        )
        for stage in self.stages:
            state.output.audit_trail.append(f"start:{stage.name}")
            state = stage.run(state)
            state.output.audit_trail.append(f"end:{stage.name}")
        return state.output


engine = MDDEngine()


# ============================================================
# Public API
# ============================================================
def run_algorithm(patient_inputs: dict) -> dict:
    """
    Accept patient inputs as a plain dict, return the full
    AlgorithmOutput as a JSON-serializable dict.

    The returned dict always contains:
      report       — structured section dict (for the React app / Streamlit)
      text_report  — pre-formatted text string for direct rendering
      reference_list, recommendations, warnings, ...
    """
    p = PatientInput(**patient_inputs)
    result = engine.run(p)
    return result.model_dump(mode="json")
