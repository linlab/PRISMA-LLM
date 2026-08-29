"""Reproduce the empirical analyses reported in the PRISMA-LLM manuscript."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from itertools import combinations, product
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import fisher_exact, mannwhitneyu

from definitions import (
    APPROACH_ORDER,
    COMPLEXITY_ORDER,
    COMPLEXITY_REPORTING_ORDER,
    HIGH_BAR,
    LIMITATION_CATEGORIES,
    ORIENTATION_ORDER,
    SENTIMENT_ORDER,
    STAGE_ORDER,
    approach_categories,
    approach_groups,
    approach_orientation,
    clean_domain,
    llm_access,
    method_complexity,
    normalize_bert_family,
    normalize_llm_family,
    reporting_richness,
    sentiment_group,
    stage_detail,
    stage_group,
)
from figures import generate_figures


START_MONTH = pd.Timestamp("2020-01-01")
END_MONTH = pd.Timestamp("2025-06-01")
ROLLING_MONTHS = 3
PUBLICATION_DATES = Path(__file__).resolve().parent / "data" / "publication_dates.csv"


METRIC_ALIASES = {
    "accuracy": ["accuracy", "accurate", "correct decisions", "correct assessment rate"],
    "agreement": ["agreement", "concordance", "concordant"],
    "auc": ["auc", "auroc", "area under the curve"],
    "balanced_accuracy": ["balanced accuracy"],
    "error_rate": ["error rate", "classification error"],
    "f1": ["f1", "f1-score", "f-score"],
    "fabricated": ["fabricated"],
    "incomplete": ["incomplete"],
    "incorrect": ["incorrect", "wrong"],
    "kappa": ["kappa", "cohen's kappa", "κ"],
    "map": ["map"],
    "missed": ["missed", "missing"],
    "ndcg": ["ndcg", "infndcg"],
    "npv": ["npv", "negative predictive value"],
    "precision": ["precision", "ppv", "positive predictive value"],
    "recall": ["recall", "sensitivity"],
    "rouge": ["rouge", "rouge-1", "rouge-2", "rouge-l"],
    "specificity": ["specificity"],
    "workload_reduction": ["workload reduction", "wss", "wss95", "wss95%"],
}
ALIAS_TO_METRIC = {
    alias: metric for metric, aliases in METRIC_ALIASES.items() for alias in aliases
}
METRIC_PATTERN = "|".join(
    re.escape(alias) for alias in sorted(ALIAS_TO_METRIC, key=len, reverse=True)
)
VALUE_PATTERN = r"(?:\d+\s*/\s*\d+|\d+(?:\.\d+)?(?:\s*(?:-|to)\s*\d+(?:\.\d+)?)?)"
UNIT_PATTERN = r"(?:%|pp|percentage points?)?"
METRIC_THEN_VALUE = re.compile(
    rf"(?P<metric>{METRIC_PATTERN})(?P<between>[^.;\n]{{0,70}}?)"
    rf"(?P<value>{VALUE_PATTERN})\s*(?P<unit>{UNIT_PATTERN})",
    re.I,
)
VALUE_THEN_METRIC = re.compile(
    rf"(?P<value>{VALUE_PATTERN})\s*(?P<unit>{UNIT_PATTERN})"
    rf"(?P<between>[\s()/-]{{0,20}}?)(?P<metric>{METRIC_PATTERN})",
    re.I,
)


def resolve_data_path(path: Path) -> Path:
    path = path.expanduser().resolve()
    if path.is_dir():
        path = path / "benchmark" / "de_harmonized.json"
    if not path.exists():
        raise FileNotFoundError(f"SciLitBench harmonized data not found: {path}")
    return path


def load_records(path: Path) -> list[dict[str, Any]]:
    with resolve_data_path(path).open(encoding="utf-8") as handle:
        payload = json.load(handle)
    records = payload.get("records")
    if not isinstance(records, list) or len(records) != 888:
        raise ValueError("Expected the 888-record SciLitBench harmonized release")
    return records


def load_publication_dates(path: Path = PUBLICATION_DATES) -> pd.DataFrame:
    dates = pd.read_csv(path)
    required = {"paper_id", "publication_year", "publication_month"}
    missing = required - set(dates.columns)
    if missing:
        raise ValueError(f"Publication-date table is missing columns: {sorted(missing)}")
    if len(dates) != 888 or dates["paper_id"].nunique() != 888:
        raise ValueError("Expected one publication-date row for each of 888 papers")
    dates["month_start"] = pd.to_datetime(
        {
            "year": dates["publication_year"],
            "month": dates["publication_month"],
            "day": 1,
        }
    )
    return dates


def build_paper_table(
    records: list[dict[str, Any]], publication_dates: pd.DataFrame
) -> pd.DataFrame:
    date_by_paper = publication_dates.set_index("paper_id").to_dict("index")
    rows: list[dict[str, Any]] = []
    for record in records:
        paper_id = str(record.get("pdf"))
        if paper_id not in date_by_paper:
            raise ValueError(f"Missing recovered publication date for {paper_id}")
        date = date_by_paper[paper_id]
        approaches = record.get("approach") or []
        evaluations = record.get("evaluation_results") or []
        limitations = record.get("limitations") or []
        stage_details = sorted(
            {stage_detail(str(value)) for value in (record.get("review_stage") or [])}
        )
        stages = sorted({stage_group(value) for value in stage_details})
        llm_families = [
            str(family)
            for item in approaches
            if item.get("category") == "Large Language Models (LLMs)"
            for family in (item.get("model_family") or [])
        ]
        bert_families = [
            str(family)
            for item in approaches
            if item.get("category") == "BERT"
            for family in (item.get("model_family") or [])
        ]
        richness = reporting_richness(evaluations, limitations)
        evaluation_categories = Counter(item.get("category") for item in evaluations)
        limitation_categories = {
            str(item.get("category"))
            for item in limitations
            if item.get("category")
        }
        categories = sorted(approach_categories(approaches))
        groups = approach_groups(approaches)
        domain = record.get("domain") or {}
        rows.append(
            {
                "paper_id": paper_id,
                "annotation_year": record.get("year"),
                "publication_year": int(date["publication_year"]),
                "publication_month": int(date["publication_month"]),
                "month_start": date["month_start"],
                "domain_high": clean_domain(domain.get("high_level")),
                "domain_medium": clean_domain(domain.get("medium_level")),
                "approach_categories": categories,
                "approach_groups": groups,
                "approach_orientation": approach_orientation(approaches),
                "method_complexity": method_complexity(approaches),
                "stage_groups": stages or ["Other/mix"],
                "stage_details": stage_details or ["Unknown"],
                "has_llm": "LLMs" in groups,
                "llm_families": sorted(set(llm_families)),
                "bert_families": sorted(set(bert_families)),
                "llm_access": llm_access(llm_families),
                "sentiment_group": sentiment_group(evaluations),
                "has_highbar_unmet": HIGH_BAR in limitation_categories,
                "limitation_categories": sorted(limitation_categories),
                "n_substantive_evaluation_items": sum(
                    category
                    not in {"overall sentiment / qualitative impression", "none reported"}
                    for category in evaluation_categories.elements()
                ),
                "has_no_evaluation_reported": "none reported" in evaluation_categories,
                **{f"richness_{name}": value for name, value in richness.items()},
            }
        )
    papers = pd.DataFrame(rows)
    if papers["paper_id"].nunique() != 888:
        raise ValueError("Derived paper table does not contain 888 unique papers")
    return papers


def parse_metric_pairs(text: str) -> list[tuple[str, float]]:
    found: list[tuple[str, float]] = []
    seen: set[tuple[str, str, str, int, int]] = set()
    for expression in [METRIC_THEN_VALUE, VALUE_THEN_METRIC]:
        for match in expression.finditer(text):
            metric = ALIAS_TO_METRIC[match.group("metric").lower()]
            value_text = match.group("value")
            unit = (match.group("unit") or "").strip()
            key = (metric, value_text, unit, match.start(), match.end())
            if key in seen:
                continue
            seen.add(key)
            value = bounded_value(value_text, unit)
            if value is not None:
                found.append((metric, value))
    return found


def bounded_value(value: str, unit: str) -> float | None:
    if "/" in value:
        return None
    match = re.search(r"\d+(?:\.\d+)?", value)
    if not match:
        return None
    number = float(match.group())
    if unit == "%" or number > 1:
        if number > 100:
            return None
        number /= 100
    return number if 0 <= number <= 1 else None


def exclusive_approach_group(record: dict[str, Any]) -> str:
    categories = approach_categories(record.get("approach") or [])
    if "Large Language Models (LLMs)" in categories:
        return "LLMs"
    if "Existing Software / Online Products" in categories:
        return "Software/products"
    if categories & {"Traditional ML", "Deep Learning (non-LLM)", "BERT", "Rule-Based"}:
        return "Traditional/DL/BERT"
    return "Other/unclear"


def model_class(record: dict[str, Any]) -> str:
    categories = approach_categories(record.get("approach") or [])
    has_llm = "Large Language Models (LLMs)" in categories
    has_bert = "BERT" in categories
    if has_llm and has_bert:
        return "Hybrid LLM+BERT"
    if has_llm:
        return "LLMs"
    if has_bert:
        return "BERT"
    return "Other"


def extract_paper_metrics(
    records: list[dict[str, Any]], dates: pd.DataFrame
) -> pd.DataFrame:
    year_by_paper = dates.set_index("paper_id")["publication_year"].to_dict()
    rows: list[dict[str, Any]] = []
    for record in records:
        paper_id = str(record.get("pdf"))
        details = [stage_detail(str(stage)) for stage in (record.get("review_stage") or [])]
        groups = sorted({stage_group(detail) for detail in details})
        approach = exclusive_approach_group(record)
        paper_model_class = model_class(record)
        domain = record.get("domain") or {}
        for item in record.get("evaluation_results") or []:
            if item.get("category") != "performance vs human annotation":
                continue
            for metric, value in parse_metric_pairs(str(item.get("quote") or "")):
                for detail, group in product(details, groups):
                    rows.append(
                        {
                            "paper_id": paper_id,
                            "publication_year": year_by_paper[paper_id],
                            "domain_medium": clean_domain(domain.get("medium_level")),
                            "approach_group": approach,
                            "model_class": paper_model_class,
                            "stage_detail": detail,
                            "stage_group": group,
                            "metric": metric,
                            "value": value,
                        }
                    )
    raw = pd.DataFrame(rows)
    return (
        raw.groupby(
            [
                "paper_id",
                "publication_year",
                "domain_medium",
                "approach_group",
                "model_class",
                "stage_detail",
                "stage_group",
                "metric",
            ],
            dropna=False,
        )["value"]
        .median()
        .reset_index()
    )


def paired_precision_recall(metrics: pd.DataFrame) -> pd.DataFrame:
    subset = metrics[
        metrics["stage_group"].eq("Screening / selection")
        | metrics["stage_detail"].eq("Data extraction")
    ].copy()
    subset["review_task"] = subset["stage_detail"].eq("Data extraction").map(
        {True: "Data extraction", False: "Screening/selection"}
    )
    paired = (
        subset.pivot_table(
            index=["paper_id", "approach_group", "review_task"],
            columns="metric",
            values="value",
            aggfunc="median",
        )
        .reset_index()
        .dropna(subset=["precision", "recall"])
    )
    return paired[
        paired["approach_group"].isin(
            ["Traditional/DL/BERT", "LLMs", "Software/products"]
        )
    ].reset_index(drop=True)


def precision_recall_summary(paired: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for (task, approach), group in paired.groupby(["review_task", "approach_group"]):
        rows.append(
            {
                "review_task": task,
                "approach_group": approach,
                "papers": group["paper_id"].nunique(),
                "precision_median": group["precision"].median(),
                "precision_q25": group["precision"].quantile(0.25),
                "precision_q75": group["precision"].quantile(0.75),
                "recall_median": group["recall"].median(),
                "recall_q25": group["recall"].quantile(0.25),
                "recall_q75": group["recall"].quantile(0.75),
            }
        )
    return pd.DataFrame(rows)


def all_summaries(
    records: list[dict[str, Any]], papers: pd.DataFrame, metrics: pd.DataFrame
) -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
    approach_prevalence, reporting_richness = yearly_reporting(papers)
    figure_data = {
        "figure_01_publication_growth": publication_growth(papers),
        "figure_02a_approach_orientation": monthly_orientation(papers),
        "figure_02b_review_stage_composition": monthly_stage_composition(papers),
        "figure_02c_llm_adoption_domain": monthly_llm_adoption(papers),
        "figure_03a_bert_family": model_family_composition(records, papers, "BERT"),
        "figure_03b_llm_family": model_family_composition(records, papers, "LLM"),
        "figure_04a_approach_prevalence": approach_prevalence,
        "figure_04b_reporting_richness": reporting_richness,
        "figure_05a_method_complexity_mix": monthly_complexity(papers),
        "figure_05b_reporting_context": complexity_reporting(papers),
        "figure_s1a_sentiment_over_time": monthly_sentiment(papers),
        "figure_s1b_highbar_concerns": highbar_by_sentiment(papers),
        "figure_s2_limitation_profiles": limitation_profiles(papers),
        "figure_s3_reporting_by_stage": reporting_by_stage(papers),
    }
    paired = paired_precision_recall(metrics)
    figure_data["figure_s4_precision_recall"] = paired

    corpus_fields, corpus_domains, evaluation_inventory, limitation_inventory = corpus_inventory(records)
    table_data = {
        "table_s1_record_fields": corpus_fields,
        "table_s1_domains": corpus_domains,
        "table_s1_evaluation_inventory": evaluation_inventory,
        "table_s1_limitation_inventory": limitation_inventory,
        "table_s3_precision_recall": precision_recall_summary(paired),
        "llm_access_by_domain": access_by_domain(papers),
        "llm_access_global_test": access_global_test(papers),
        "llm_access_pairwise_tests": access_pairwise_tests(papers),
        "metric_mann_whitney_tests": metric_mann_whitney(metrics),
    }
    return figure_data, table_data


def month_index() -> pd.DatetimeIndex:
    return pd.date_range(START_MONTH, END_MONTH, freq="MS")


def _rolling_share(
    counts: pd.DataFrame, category: str, categories: list[str], value: str = "papers"
) -> pd.DataFrame:
    wide = (
        counts.pivot_table(index="month_start", columns=category, values=value, fill_value=0)
        .reindex(index=month_index(), columns=categories, fill_value=0)
        .sort_index()
        .rolling(ROLLING_MONTHS, min_periods=1)
        .sum()
    )
    share = wide.div(wide.sum(axis=1), axis=0).fillna(0)
    return share.reset_index(names="month_start").melt(
        id_vars="month_start", var_name=category, value_name="share"
    )


def publication_growth(papers: pd.DataFrame) -> pd.DataFrame:
    monthly = papers.groupby("month_start")["paper_id"].nunique()
    observed_quarters = (
        papers.assign(period=papers["month_start"].dt.to_period("Q").dt.start_time)
        .groupby("period")["paper_id"]
        .nunique()
        .reindex(pd.date_range(papers["month_start"].min().to_period("Q").start_time, "2025-04-01", freq="QS"), fill_value=0)
    )
    fit_index = pd.date_range("2020-01-01", END_MONTH, freq="MS")
    fit_counts = monthly.reindex(fit_index, fill_value=0).to_numpy(dtype=float)
    positive = fit_counts > 0
    slope, intercept = np.polyfit(
        np.arange(len(fit_counts))[positive], np.log(fit_counts[positive]), 1
    )
    full_months = pd.date_range("2020-01-01", "2026-12-01", freq="MS")
    fitted = pd.DataFrame(
        {
            "month_start": full_months,
            "fitted_monthly_papers": np.exp(intercept + slope * np.arange(len(full_months))),
        }
    )
    fitted["period"] = fitted["month_start"].dt.to_period("Q").dt.start_time
    fitted_quarters = fitted.groupby("period")["fitted_monthly_papers"].sum()
    periods = pd.date_range(observed_quarters.index.min(), "2026-10-01", freq="QS")
    output = pd.DataFrame({"period": periods})
    output["observed_papers"] = output["period"].map(observed_quarters)
    output["fitted_papers"] = output["period"].map(fitted_quarters)
    output["projected"] = output["period"].gt(pd.Timestamp("2025-04-01"))
    output["monthly_growth_rate"] = np.exp(slope) - 1
    return output


def monthly_orientation(papers: pd.DataFrame) -> pd.DataFrame:
    subset = papers[papers["month_start"].between(START_MONTH, END_MONTH)]
    counts = (
        subset.groupby(["month_start", "approach_orientation"])["paper_id"]
        .nunique()
        .reset_index(name="papers")
    )
    return _rolling_share(counts, "approach_orientation", ORIENTATION_ORDER)


def monthly_stage_composition(papers: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    subset = papers[papers["month_start"].between(START_MONTH, END_MONTH)]
    for paper in subset.itertuples():
        stages = [stage for stage in paper.stage_groups if stage in STAGE_ORDER]
        if not stages:
            continue
        for stage in stages:
            rows.append(
                {
                    "month_start": paper.month_start,
                    "stage_group": stage,
                    "weight": 1 / len(stages),
                }
            )
    counts = (
        pd.DataFrame(rows)
        .groupby(["month_start", "stage_group"])["weight"]
        .sum()
        .reset_index()
    )
    return _rolling_share(counts, "stage_group", STAGE_ORDER, value="weight")


def monthly_llm_adoption(papers: pd.DataFrame) -> pd.DataFrame:
    domain_counts = papers.groupby("domain_high")["paper_id"].nunique()
    domains = domain_counts[domain_counts.ge(5)].index.tolist()
    subset = papers[
        papers["month_start"].between(pd.Timestamp("2023-01-01"), END_MONTH)
        & papers["domain_high"].isin(domains)
    ]
    frames: list[pd.DataFrame] = []
    index = pd.date_range("2023-01-01", END_MONTH, freq="MS")
    for domain in domains:
        group = subset[subset["domain_high"].eq(domain)]
        total = group.groupby("month_start")["paper_id"].nunique().reindex(index, fill_value=0)
        llm = (
            group[group["has_llm"]]
            .groupby("month_start")["paper_id"]
            .nunique()
            .reindex(index, fill_value=0)
        )
        total = total.rolling(ROLLING_MONTHS, min_periods=1).sum()
        llm = llm.rolling(ROLLING_MONTHS, min_periods=1).sum()
        frame = pd.DataFrame(
            {
                "month_start": index,
                "domain_high": domain,
                "papers": total,
                "llm_papers": llm,
                "llm_pct": 100 * llm.div(total.replace(0, np.nan)),
            }
        )
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def monthly_complexity(papers: pd.DataFrame) -> pd.DataFrame:
    subset = papers[papers["month_start"].between(START_MONTH, END_MONTH)]
    counts = (
        subset.groupby(["month_start", "method_complexity"])["paper_id"]
        .nunique()
        .reset_index(name="papers")
    )
    return _rolling_share(counts, "method_complexity", COMPLEXITY_ORDER)


def monthly_sentiment(papers: pd.DataFrame) -> pd.DataFrame:
    subset = papers[
        papers["has_llm"]
        & papers["month_start"].between(pd.Timestamp("2023-01-01"), END_MONTH)
    ]
    counts = (
        subset.groupby(["month_start", "sentiment_group"])["paper_id"]
        .nunique()
        .reset_index(name="papers")
    )
    wide = (
        counts.pivot_table(index="month_start", columns="sentiment_group", values="papers", fill_value=0)
        .reindex(
            index=pd.date_range("2023-01-01", END_MONTH, freq="MS"),
            columns=SENTIMENT_ORDER,
            fill_value=0,
        )
        .rolling(ROLLING_MONTHS, min_periods=1)
        .sum()
    )
    shares = wide.div(wide.sum(axis=1), axis=0).fillna(0)
    long = shares.reset_index(names="month_start").melt(
        id_vars="month_start", var_name="sentiment_group", value_name="share"
    )
    long["papers_in_window"] = long["month_start"].map(wide.sum(axis=1))
    return long


def yearly_reporting(papers: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    subset = papers[papers["publication_year"].ge(2015)]
    denominators = subset.groupby("publication_year")["paper_id"].nunique()
    rows: list[dict[str, Any]] = []
    for paper in subset.itertuples():
        groups: list[str] = []
        if set(paper.approach_categories) & {
            "Traditional ML",
            "Deep Learning (non-LLM)",
            "BERT",
        }:
            groups.append("Traditional/DL/BERT")
        if "Software/products" in paper.approach_groups:
            groups.append("Software/products")
        if "LLMs" in paper.approach_groups:
            groups.append("LLMs")
        for group in groups:
            rows.append(
                {
                    "paper_id": paper.paper_id,
                    "publication_year": paper.publication_year,
                    "approach_group": group,
                    "reporting_richness": paper.richness_total,
                }
            )
    exploded = pd.DataFrame(rows)
    adoption = (
        exploded.groupby(["publication_year", "approach_group"])["paper_id"]
        .nunique()
        .reset_index(name="group_papers")
    )
    adoption["all_papers"] = adoption["publication_year"].map(denominators)
    adoption["paper_share"] = adoption["group_papers"] / adoption["all_papers"]
    richness = (
        exploded.groupby(["publication_year", "approach_group"])["reporting_richness"]
        .mean()
        .reset_index(name="mean_reporting_richness")
    )
    return adoption, richness


def complexity_reporting(papers: pd.DataFrame) -> pd.DataFrame:
    subset = papers[
        papers["publication_year"].ge(2023)
        & papers["method_complexity"].isin(COMPLEXITY_REPORTING_ORDER)
    ]
    summary = (
        subset.groupby("method_complexity")
        .agg(
            papers=("paper_id", "nunique"),
            mean_reporting_richness=("richness_total", "mean"),
            no_evaluation_pct=("has_no_evaluation_reported", lambda values: 100 * values.mean()),
        )
        .reindex(COMPLEXITY_REPORTING_ORDER)
        .reset_index()
    )
    return summary


def highbar_by_sentiment(papers: pd.DataFrame) -> pd.DataFrame:
    subset = papers[papers["has_llm"]]
    return (
        subset.groupby("sentiment_group")
        .agg(
            papers=("paper_id", "nunique"),
            highbar_papers=("has_highbar_unmet", "sum"),
            highbar_pct=("has_highbar_unmet", lambda values: 100 * values.mean()),
        )
        .reindex(SENTIMENT_ORDER)
        .dropna(subset=["papers"])
        .reset_index()
    )


def reporting_by_stage(papers: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    subset = papers[papers["publication_year"].ge(2023)]
    for paper in subset.itertuples():
        for approach in paper.approach_groups:
            if approach not in APPROACH_ORDER:
                continue
            for stage in paper.stage_groups:
                if stage not in STAGE_ORDER:
                    continue
                rows.append(
                    {
                        "paper_id": paper.paper_id,
                        "approach_group": approach,
                        "stage_group": stage,
                        "evaluation_items": paper.n_substantive_evaluation_items,
                        "no_evaluation": paper.has_no_evaluation_reported,
                    }
                )
    return (
        pd.DataFrame(rows)
        .groupby(["stage_group", "approach_group"])
        .agg(
            papers=("paper_id", "nunique"),
            mean_evaluation_items=("evaluation_items", "mean"),
            no_evaluation_pct=("no_evaluation", lambda values: 100 * values.mean()),
        )
        .reset_index()
    )


def model_family_composition(
    records: list[dict[str, Any]], papers: pd.DataFrame, family_type: str
) -> pd.DataFrame:
    year_by_paper = papers.set_index("paper_id")["publication_year"].to_dict()
    rows: list[dict[str, str]] = []
    for record in records:
        paper_id = str(record.get("pdf"))
        if year_by_paper[paper_id] < 2015:
            continue
        domain = clean_domain((record.get("domain") or {}).get("high_level"))
        if domain == "Arts and Humanities":
            continue
        category = "BERT" if family_type == "BERT" else "Large Language Models (LLMs)"
        normalizer = normalize_bert_family if family_type == "BERT" else normalize_llm_family
        for item in record.get("approach") or []:
            if item.get("category") != category:
                continue
            for family in item.get("model_family") or []:
                group = normalizer(str(family))
                if family_type == "LLM" and group == "Other / unclear LLM":
                    continue
                rows.append(
                    {
                        "paper_id": paper_id,
                        "domain_high": domain,
                        "family_group": group,
                    }
                )
    mentions = pd.DataFrame(rows).drop_duplicates()
    summary = (
        mentions.groupby(["domain_high", "family_group"])["paper_id"]
        .nunique()
        .reset_index(name="mentions")
    )
    summary["field_mentions"] = summary.groupby("domain_high")["mentions"].transform("sum")
    summary["share"] = summary["mentions"] / summary["field_mentions"]
    return summary


def limitation_profiles(papers: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for paper in papers.itertuples():
        dimensions: list[tuple[str, str]] = []
        dimensions.extend(("approach", group) for group in paper.approach_groups if group in APPROACH_ORDER)
        dimensions.append(("domain_high", paper.domain_high))
        for family in paper.bert_families:
            dimensions.append(("bert_family", normalize_bert_family(family)))
        for family in paper.llm_families:
            group = normalize_llm_family(family)
            if group != "Other / unclear LLM":
                dimensions.append(("llm_family", group))
        present = set(paper.limitation_categories)
        for dimension, group in set(dimensions):
            for limitation in LIMITATION_CATEGORIES:
                rows.append(
                    {
                        "paper_id": paper.paper_id,
                        "dimension": dimension,
                        "group": group,
                        "limitation": limitation,
                        "has_limitation": limitation in present,
                    }
                )
    expanded = pd.DataFrame(rows)
    summary = (
        expanded.groupby(["dimension", "group", "limitation"])
        .agg(
            papers=("paper_id", "nunique"),
            limitation_papers=("has_limitation", "sum"),
            pct=("has_limitation", lambda values: 100 * values.mean()),
        )
        .reset_index()
    )
    return summary[summary["papers"].ge(5)].reset_index(drop=True)


def corpus_inventory(
    records: list[dict[str, Any]],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    field_counts = {
        "year": len(records),
        "domain": sum(len(record.get("domain") or {}) for record in records),
        "review stage": sum(len(record.get("review_stage") or []) for record in records),
        "approach": sum(len(record.get("approach") or []) for record in records),
        "evaluation results": sum(len(record.get("evaluation_results") or []) for record in records),
        "limitations": sum(len(record.get("limitations") or []) for record in records),
    }
    fields = pd.DataFrame(
        [{"field": name, "items": count} for name, count in field_counts.items()]
        + [{"field": "total", "items": sum(field_counts.values())}]
    )
    domain_counts = Counter(
        clean_domain((record.get("domain") or {}).get("high_level")) for record in records
    )
    domains = pd.DataFrame(
        [
            {"domain": domain, "papers": count, "share": count / len(records)}
            for domain, count in domain_counts.most_common()
        ]
    )
    evaluation = _category_inventory(records, "evaluation_results")
    limitations = _category_inventory(records, "limitations")
    return fields, domains, evaluation, limitations


def _category_inventory(records: list[dict[str, Any]], field: str) -> pd.DataFrame:
    item_counts: Counter[str] = Counter()
    papers_by_category: dict[str, set[str]] = {}
    for record in records:
        paper_id = str(record.get("pdf"))
        for item in record.get(field) or []:
            category = str(item.get("category"))
            item_counts[category] += 1
            papers_by_category.setdefault(category, set()).add(paper_id)
    return pd.DataFrame(
        [
            {
                "category": category,
                "items": count,
                "papers": len(papers_by_category[category]),
            }
            for category, count in item_counts.most_common()
        ]
    )


def access_by_domain(papers: pd.DataFrame) -> pd.DataFrame:
    subset = papers[papers["has_llm"]]
    counts = (
        subset.groupby(["domain_high", "llm_access"])["paper_id"]
        .nunique()
        .reset_index(name="papers")
    )
    counts["domain_papers"] = counts.groupby("domain_high")["papers"].transform("sum")
    counts["pct"] = 100 * counts["papers"] / counts["domain_papers"]
    return counts


def _closed_open_rows(papers: pd.DataFrame) -> pd.DataFrame:
    return papers[
        papers["has_llm"]
        & papers["llm_access"].isin(["Proprietary/hosted", "Open-weight/open-family"])
    ][["paper_id", "domain_high", "llm_access"]].drop_duplicates()


def access_global_test(papers: pd.DataFrame) -> pd.DataFrame:
    subset = _closed_open_rows(papers)
    observed = _chi_square(subset)
    rng = np.random.default_rng(20260630)
    labels = subset["llm_access"].to_numpy()
    simulated = np.empty(5000)
    for index in range(5000):
        permuted = subset.copy()
        permuted["llm_access"] = rng.permutation(labels)
        simulated[index] = _chi_square(permuted)
    p_value = (np.count_nonzero(simulated >= observed) + 1) / 5001
    return pd.DataFrame(
        [
            {
                "comparison": "llm_access_by_domain",
                "papers": len(subset),
                "domains": subset["domain_high"].nunique(),
                "chi_square": observed,
                "permutations": 5000,
                "p_value": p_value,
                "seed": 20260630,
            }
        ]
    )


def _chi_square(data: pd.DataFrame) -> float:
    table = pd.crosstab(data["domain_high"], data["llm_access"]).to_numpy(dtype=float)
    expected = table.sum(axis=1, keepdims=True) @ table.sum(axis=0, keepdims=True) / table.sum()
    return float((((table - expected) ** 2) / expected).sum())


def access_pairwise_tests(papers: pd.DataFrame) -> pd.DataFrame:
    subset = _closed_open_rows(papers)
    counts = (
        subset.groupby(["domain_high", "llm_access"])["paper_id"]
        .nunique()
        .unstack(fill_value=0)
    )
    rows: list[dict[str, Any]] = []
    for domain_a, domain_b in combinations(counts.index, 2):
        a = counts.loc[domain_a]
        b = counts.loc[domain_b]
        table = [
            [int(a.get("Proprietary/hosted", 0)), int(a.get("Open-weight/open-family", 0))],
            [int(b.get("Proprietary/hosted", 0)), int(b.get("Open-weight/open-family", 0))],
        ]
        odds_ratio, p_value = fisher_exact(table, alternative="two-sided")
        rows.append(
            {
                "domain_a": domain_a,
                "domain_b": domain_b,
                "domain_a_proprietary": table[0][0],
                "domain_a_open_weight": table[0][1],
                "domain_b_proprietary": table[1][0],
                "domain_b_open_weight": table[1][1],
                "odds_ratio": odds_ratio,
                "p_value": p_value,
            }
        )
    result = pd.DataFrame(rows)
    result["bh_q_value"] = _benjamini_hochberg(result["p_value"].to_numpy())
    return result.sort_values(["bh_q_value", "p_value"]).reset_index(drop=True)


def _benjamini_hochberg(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values)
    ranked = values[order]
    adjusted = ranked * len(values) / np.arange(1, len(values) + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    output = np.empty_like(adjusted)
    output[order] = np.minimum(adjusted, 1)
    return output


def metric_mann_whitney(metrics: pd.DataFrame) -> pd.DataFrame:
    subset = (
        metrics[
            metrics["model_class"].isin(["LLMs", "BERT"])
            & metrics["metric"].isin(["precision", "recall"])
        ]
        .groupby(
            ["paper_id", "model_class", "stage_group", "metric"],
            dropna=False,
            as_index=False,
        )["value"]
        .median()
    )
    rows: list[dict[str, Any]] = []
    for (stage, metric), group in subset.groupby(["stage_group", "metric"]):
        llm = group[group["model_class"].eq("LLMs")]["value"]
        bert = group[group["model_class"].eq("BERT")]["value"]
        if len(llm) < 5 or len(bert) < 5:
            continue
        test = mannwhitneyu(llm, bert, alternative="two-sided", method="asymptotic")
        rows.append(
            {
                "stage_group": stage,
                "metric": metric,
                "llm_values": len(llm),
                "bert_values": len(bert),
                "u_statistic": test.statistic,
                "p_value": test.pvalue,
            }
        )
    return pd.DataFrame(rows)


def export_paper_table(papers: pd.DataFrame, path: Path) -> None:
    export = papers.copy()
    export["month_start"] = export["month_start"].dt.strftime("%Y-%m-01")
    for column in [
        "approach_categories",
        "approach_groups",
        "stage_groups",
        "stage_details",
        "llm_families",
        "bert_families",
        "limitation_categories",
    ]:
        export[column] = export[column].apply(lambda values: " | ".join(values))
    path.parent.mkdir(parents=True, exist_ok=True)
    export.to_csv(path, index=False)


def export_frames(frames: dict[str, pd.DataFrame], directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for name, frame in frames.items():
        frame.to_csv(directory / f"{name}.csv", index=False)


def reproduce(scilitbench: Path, output_dir: Path) -> None:
    records = load_records(scilitbench)
    dates = load_publication_dates()
    papers = build_paper_table(records, dates)
    metrics = extract_paper_metrics(records, dates)
    figure_data, table_data = all_summaries(records, papers, metrics)

    output_dir = output_dir.expanduser().resolve()
    derived_dir = output_dir / "derived"
    figures_dir = output_dir / "figures"
    export_paper_table(papers, derived_dir / "paper_level_analysis.csv")
    metrics.to_csv(derived_dir / "reported_metrics.csv", index=False)
    export_frames(figure_data, output_dir / "figure_data")
    export_frames(table_data, output_dir / "table_data")
    generate_figures(figure_data, table_data, figures_dir)

    print(f"Reproduced analysis from {len(records)} papers")
    print(f"Outputs written to {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scilitbench",
        type=Path,
        required=True,
        help="Path to the SciLitBench repository or de_harmonized.json.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "outputs",
        help="Directory for derived data, plot data, tables and figures.",
    )
    args = parser.parse_args()
    reproduce(args.scilitbench, args.output_dir)


if __name__ == "__main__":
    main()
