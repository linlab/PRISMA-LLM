"""Scientific groupings and scoring rules used by the analysis."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any


APPROACH_ORDER = ["Traditional/DL/BERT", "Software/products", "LLMs"]
APPROACH_COLORS = {
    "Traditional/DL/BERT": "#4C78A8",
    "Software/products": "#F58518",
    "LLMs": "#54A24B",
}
ORIENTATION_ORDER = [
    "Custom ML/BERT/DL/rules",
    "LLM/software-facing",
    "Hybrid",
    "Other/unclear",
]
ORIENTATION_COLORS = {
    "Custom ML/BERT/DL/rules": "#4C78A8",
    "LLM/software-facing": "#F58518",
    "Hybrid": "#54A24B",
    "Other/unclear": "#B279A2",
}
STAGE_ORDER = [
    "Discovery / navigation",
    "Screening / selection",
    "Evidence construction",
]
STAGE_COLORS = {
    "Discovery / navigation": "#4C78A8",
    "Screening / selection": "#F58518",
    "Evidence construction": "#54A24B",
}
COMPLEXITY_ORDER = [
    "Software/product only",
    "Rule/traditional ML",
    "Neural non-LLM",
    "Prompt-only LLM",
    "Engineered/structured LLM",
    "Retrieval/adapted/agentic LLM",
    "LLM method unclear",
    "Other/unclear",
]
COMPLEXITY_COLORS = {
    "Software/product only": "#D9EAF7",
    "Rule/traditional ML": "#D69A62",
    "Neural non-LLM": "#A96F91",
    "Prompt-only LLM": "#9ECAE1",
    "Engineered/structured LLM": "#4292C6",
    "Retrieval/adapted/agentic LLM": "#08519C",
    "LLM method unclear": "#A7ADB4",
    "Other/unclear": "#D9DDE1",
}
COMPLEXITY_REPORTING_ORDER = [
    "Retrieval/adapted/agentic LLM",
    "Engineered/structured LLM",
    "Prompt-only LLM",
    "Software/product only",
]
SENTIMENT_ORDER = [
    "Descriptive/unclear",
    "Mixed/negative",
    "Positive + caveats",
    "Positive only",
]
SENTIMENT_COLORS = {
    "Descriptive/unclear": "#BAB0AC",
    "Mixed/negative": "#E45756",
    "Positive + caveats": "#F58518",
    "Positive only": "#54A24B",
}

HIGH_BAR = "high bar needed but not achieved"
LIMITATION_CATEGORIES = [
    HIGH_BAR,
    "limited validation or benchmarking of AI outputs",
    "performance sensitive to parameters or prompts",
    "small data, narrow scope, or limited data availability",
]

_RETRIEVAL_PATTERNS = [
    r"\brag\b", r"retrieval[- ]augmented", r"\bretrieval\b", r"query expansion",
    r"\bhyde\b", r"semantic re-ranking", r"fine[- ]tun", r"instruction tun",
    r"\blora\b", r"\bpeft\b", r"\bneftune\b", r"low[- ]rank", r"\bagentic\b",
    r"\bmulti[- ]agent\b", r"\bagent[- ]based\b", r"\breact agents?\b", r"actor[- ]critic",
]
_ENGINEERED_PATTERNS = [
    r"prompt engineering", r"prompt optimization", r"prompt templates?", r"prompt refinement",
    r"refinement prompts?", r"iterative refinement", r"iterative prompt", r"context-aware prompting",
    r"guided prompt", r"\bstructured\b", r"\bjson\b", r"schema[- ]constrained",
    r"few[- ]shot", r"similar[- ]shot", r"one[- ]shot", r"in[- ]context learning",
    r"chain[- ]of[- ]thought", r"\bcot\b", r"step[- ]by[- ]step", r"self[- ]consistency",
    r"self[- ]ask", r"multi[- ]step", r"repeated (?:parallel )?(?:prompting|calls)",
    r"result consolidation", r"synthesis step", r"\bvoting\b", r"\bensemble", r"\bconsensus\b",
    r"multi[- ]llm", r"llm[- ]as[- ](?:evaluator|judge)", r"\bcalibrat", r"cross[- ]critique",
    r"\brouting\b", r"custom(?:ized)? gpt", r"specialized gpt", r"\blangchain\b",
    r"explainable rationales", r"\bembeddings?\b", r"latent class analysis",
]
_PROMPT_PATTERNS = [
    r"^prompting$", r"\bzero[- ]shot\b", r"prompt[- ]based binary classification",
    r"llm[- ]based assessor",
]

RETRIEVAL_PATTERNS = [re.compile(value, re.I) for value in _RETRIEVAL_PATTERNS]
ENGINEERED_PATTERNS = [re.compile(value, re.I) for value in _ENGINEERED_PATTERNS]
PROMPT_PATTERNS = [re.compile(value, re.I) for value in _PROMPT_PATTERNS]


def approach_categories(approaches: list[dict[str, Any]]) -> set[str]:
    return {str(item.get("category")) for item in approaches if item.get("category")}


def approach_groups(approaches: list[dict[str, Any]]) -> list[str]:
    categories = approach_categories(approaches)
    groups: list[str] = []
    if categories & {"Traditional ML", "Deep Learning (non-LLM)", "BERT", "Rule-Based"}:
        groups.append("Traditional/DL/BERT")
    if "Existing Software / Online Products" in categories:
        groups.append("Software/products")
    if "Large Language Models (LLMs)" in categories:
        groups.append("LLMs")
    return groups or ["Other/unclear"]


def approach_orientation(approaches: list[dict[str, Any]]) -> str:
    categories = approach_categories(approaches)
    custom = bool(categories & {"Traditional ML", "Deep Learning (non-LLM)", "BERT", "Rule-Based"})
    llm_or_software = bool(
        categories & {"Large Language Models (LLMs)", "Existing Software / Online Products"}
    )
    if custom and llm_or_software:
        return "Hybrid"
    if llm_or_software:
        return "LLM/software-facing"
    if custom:
        return "Custom ML/BERT/DL/rules"
    return "Other/unclear"


def method_complexity(approaches: list[dict[str, Any]]) -> str:
    categories = approach_categories(approaches)
    if "Large Language Models (LLMs)" in categories:
        methods = [
            str(method).strip().lower()
            for item in approaches
            if item.get("category") == "Large Language Models (LLMs)"
            for method in (item.get("method") or [])
        ]
        if _matches(methods, RETRIEVAL_PATTERNS):
            return "Retrieval/adapted/agentic LLM"
        if _matches(methods, ENGINEERED_PATTERNS):
            return "Engineered/structured LLM"
        if _matches(methods, PROMPT_PATTERNS):
            return "Prompt-only LLM"
        return "LLM method unclear"
    if categories & {"BERT", "Deep Learning (non-LLM)"}:
        return "Neural non-LLM"
    if categories & {"Traditional ML", "Rule-Based"}:
        return "Rule/traditional ML"
    if "Existing Software / Online Products" in categories and not (
        categories - {"Existing Software / Online Products", "Other"}
    ):
        return "Software/product only"
    return "Other/unclear"


def _matches(labels: list[str], patterns: list[re.Pattern[str]]) -> bool:
    return any(pattern.search(label) for label in labels for pattern in patterns)


def stage_detail(stage: str) -> str:
    mapping = {
        "Search / retrieval": "Search/retrieval",
        "Topic modeling / clustering": "Topic modeling/clustering",
        "Text mining / information synthesis": "Text mining/synthesis",
        "Title/abstract (TA) screening": "Title/abstract screening",
        "Full-text (FT) screening": "Full-text screening",
        "Screening – ranking/prioritization only": "Ranking/prioritization",
        "Data extraction": "Data extraction",
        "Other methodological tasks (risk of bias, quality assessment)": "Risk/quality tasks",
        "Claim verification": "Claim verification",
    }
    return mapping.get(stage, stage or "Unknown")


def stage_group(detail: str) -> str:
    if detail in {"Search/retrieval", "Topic modeling/clustering", "Text mining/synthesis"}:
        return "Discovery / navigation"
    if detail in {"Title/abstract screening", "Full-text screening", "Ranking/prioritization"}:
        return "Screening / selection"
    if detail in {"Data extraction", "Risk/quality tasks", "Claim verification"}:
        return "Evidence construction"
    return "Other/mix"


def reporting_richness(
    eval_items: list[dict[str, Any]], limitations: list[dict[str, Any]]
) -> dict[str, int]:
    counts = Counter(item.get("category") for item in eval_items)
    dimensions = {
        "performance": counts["performance vs human annotation"],
        "comparative": counts["comparative results"],
        "modification": counts["feature or modification effects"],
        "resources": counts["runtime and cost"],
        "limitations": sum(
            (item.get("category") or "") not in {"", "none reported"}
            for item in limitations
        ),
    }
    scores = {name: capped_score(value) for name, value in dimensions.items()}
    scores["total"] = sum(scores.values())
    return scores


def capped_score(count: int) -> int:
    if count <= 0:
        return 0
    if count == 1:
        return 1
    if count <= 3:
        return 2
    return 3


def sentiment_group(eval_items: list[dict[str, Any]]) -> str:
    counts: Counter[str] = Counter()
    for item in eval_items:
        if item.get("category") != "overall sentiment / qualitative impression":
            continue
        for value in (item.get("mapping") or {}).get("overall_evaluation", []):
            counts[value] += 1
    if counts["positive"] and not (counts["mixed_or_conditional"] or counts["negative"]):
        return "Positive only"
    if counts["positive"] and (counts["mixed_or_conditional"] or counts["negative"]):
        return "Positive + caveats"
    if counts["mixed_or_conditional"] or counts["negative"]:
        return "Mixed/negative"
    return "Descriptive/unclear"


def clean_domain(value: Any) -> str:
    if value in {None, "", "unknown / not reported"}:
        return "mix"
    return str(value)


def normalize_bert_family(value: str) -> str:
    text = value.lower()
    if "bertopic" in text:
        return "BERTopic"
    if any(token in text for token in ["pubmed", "bio", "clinical", "bluebert", "biomed"]):
        return "Biomedical BERT variants"
    if any(token in text for token in ["scibert", "specter"]):
        return "Scientific embedding variants"
    if any(token in text for token in ["sentence", "sbert", "mpnet"]):
        return "Sentence embedding variants"
    if any(token in text for token in ["roberta", "deberta", "xlm", "distil", "longformer"]):
        return "General transformer variants"
    if "bert" in text or text == "base":
        return "Generic BERT"
    return "Other BERT-like"


def normalize_llm_family(value: str) -> str:
    text = value.strip().lower()
    if text in {"", "unknown", "unspecified", "unspecified-llm"}:
        return "Other / unclear LLM"
    if "gpt" in text or "chatgpt" in text:
        return "GPT / ChatGPT"
    if "claude" in text:
        return "Claude"
    if any(token in text for token in ["gemini", "bard", "palm"]):
        return "Gemini / Bard / PaLM"
    if "llama" in text:
        return "Llama"
    if "mistral" in text or "mixtral" in text:
        return "Mistral / Mixtral"
    if any(
        token in text
        for token in [
            "qwen", "deepseek", "gemma", "phi", "flan", "falcon", "zephyr",
            "jina", "med42", "meditron", "galactica", "biomedgpt", "openhermes",
            "platypus", "bart", "t5",
        ]
    ):
        return "Other open-weight / open-family"
    if any(token in text for token in ["perplexity", "bing", "grok", "vercel", "moonshot"]):
        return "Other proprietary / hosted"
    return "Other / unclear LLM"


def llm_access(families: list[str]) -> str:
    proprietary = {
        "gpt", "chatgpt", "claude", "gemini", "bard", "palm", "perplexity",
        "bing", "grok", "vercel", "moonshot",
    }
    open_weight = {
        "llama", "mistral", "mixtral", "qwen", "deepseek", "gemma", "phi",
        "flan-t5", "flant5", "zephyr", "falcon", "jina", "med42", "meditron",
        "galactica", "biomedgpt", "openhermes-neuralchat", "openhermes",
        "platypus 2", "bart", "t5",
    }
    normalized = {re.sub(r"\s+", " ", family.strip().lower()) for family in families}
    normalized -= {"", "unknown", "unspecified", "unspecified-llm"}
    has_proprietary = bool(normalized & proprietary)
    has_open = bool(normalized & open_weight)
    if has_proprietary and has_open:
        return "Mixed proprietary/open-weight"
    if has_proprietary:
        return "Proprietary/hosted"
    if has_open:
        return "Open-weight/open-family"
    return "Family not annotated"
