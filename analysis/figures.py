"""Render the empirical manuscript figures from exported plot data."""

from __future__ import annotations

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.ticker import PercentFormatter

from definitions import (
    APPROACH_COLORS,
    APPROACH_ORDER,
    COMPLEXITY_COLORS,
    COMPLEXITY_ORDER,
    ORIENTATION_COLORS,
    ORIENTATION_ORDER,
    SENTIMENT_COLORS,
    SENTIMENT_ORDER,
    STAGE_COLORS,
    STAGE_ORDER,
)


def generate_figures(
    figure_data: dict[str, pd.DataFrame],
    table_data: dict[str, pd.DataFrame],
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _plot_growth(
        figure_data["figure_01_publication_growth"],
        table_data["table_s1_domains"],
        table_data["table_s1_record_fields"],
        output_dir / "figure_01_publication_growth.png",
    )
    _plot_area(
        figure_data["figure_02a_approach_orientation"],
        "approach_orientation",
        "share",
        ORIENTATION_ORDER,
        ORIENTATION_COLORS,
        "Share of papers",
        output_dir / "figure_02a_approach_orientation.png",
        chatgpt=True,
    )
    _plot_area(
        figure_data["figure_02b_review_stage_composition"],
        "stage_group",
        "share",
        STAGE_ORDER,
        STAGE_COLORS,
        "Share of stage focus",
        output_dir / "figure_02b_review_stage_composition.png",
        chatgpt=True,
    )
    _plot_domain_adoption(
        figure_data["figure_02c_llm_adoption_domain"],
        output_dir / "figure_02c_llm_adoption_domain.png",
    )
    _plot_family(
        figure_data["figure_03a_bert_family"],
        output_dir / "figure_03a_bert_family.png",
    )
    _plot_family(
        figure_data["figure_03b_llm_family"],
        output_dir / "figure_03b_llm_family.png",
    )
    _plot_year_lines(
        figure_data["figure_04a_approach_prevalence"],
        "paper_share",
        "Share of papers with approach",
        output_dir / "figure_04a_approach_adoption.png",
        percent=True,
    )
    _plot_year_lines(
        figure_data["figure_04b_reporting_richness"],
        "mean_reporting_richness",
        "Mean richness score / paper",
        output_dir / "figure_04b_reporting_richness.png",
    )
    _plot_area(
        figure_data["figure_05a_method_complexity_mix"],
        "method_complexity",
        "share",
        COMPLEXITY_ORDER,
        COMPLEXITY_COLORS,
        "Share of papers",
        output_dir / "figure_05a_method_complexity_mix.png",
        milestones=True,
    )
    _plot_complexity_reporting(
        figure_data["figure_05b_reporting_context"],
        output_dir / "figure_05b_reporting_context.png",
    )
    _plot_area(
        figure_data["figure_s1a_sentiment_over_time"],
        "sentiment_group",
        "share",
        SENTIMENT_ORDER,
        SENTIMENT_COLORS,
        "Share of LLM papers",
        output_dir / "figure_s1a_sentiment_over_time.png",
    )
    _plot_highbar(
        figure_data["figure_s1b_highbar_concerns"],
        output_dir / "figure_s1b_highbar_concerns.png",
    )
    _plot_limitation_panels(
        figure_data["figure_s2_limitation_profiles"], output_dir
    )
    _plot_stage_reporting(
        figure_data["figure_s3_reporting_by_stage"], output_dir
    )
    _plot_precision_recall(
        figure_data["figure_s4_precision_recall"], output_dir
    )


def _save(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path, dpi=300, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)


def _plot_growth(
    data: pd.DataFrame,
    domains: pd.DataFrame,
    record_fields: pd.DataFrame,
    path: Path,
) -> None:
    fig = plt.figure(figsize=(12, 4.5))
    grid = fig.add_gridspec(1, 2, width_ratios=[1.15, 2.15], wspace=0.32)
    left = fig.add_subplot(grid[0, 0])
    right = fig.add_subplot(grid[0, 1])
    record_count = int(
        record_fields.loc[record_fields["field"].eq("year"), "items"].iloc[0]
    )
    annotation_count = int(
        record_fields.loc[record_fields["field"].eq("total"), "items"].iloc[0]
    )
    left.axis("off")
    left.text(0, 0.97, "Corpus scope", fontsize=14, weight="bold", va="top")
    left.text(0, 0.81, f"{record_count:,} paper-level records", fontsize=11)
    left.text(0, 0.70, f"{annotation_count:,} annotation items", fontsize=11)
    labels = {
        "Life Sciences and Medicine": "Life sciences/medicine",
        "Engineering and Technology": "Engineering/technology",
        "Social Sciences and Management": "Social sciences/management",
        "mix": "Mixed domain",
        "Natural Sciences": "Natural sciences",
        "Arts and Humanities": "Arts/humanities",
    }
    y = 0.54
    for row in domains.itertuples():
        left.text(0, y, labels.get(str(row.domain), str(row.domain)), fontsize=8.8)
        left.text(0.98, y, f"{row.papers}  ({100 * row.share:.1f}%)", ha="right", fontsize=8.8)
        y -= 0.085

    observed = data[data["observed_papers"].notna()]
    fitted = data[data["period"].between(pd.Timestamp("2020-01-01"), pd.Timestamp("2025-04-01"))]
    projected = data[data["period"].ge(pd.Timestamp("2025-04-01"))]
    right.bar(observed["period"], observed["observed_papers"], width=70, color="#4C78A8", alpha=0.72)
    right.plot(fitted["period"], fitted["fitted_papers"], color="#D62728", lw=2.1)
    right.plot(projected["period"], projected["fitted_papers"], color="#D62728", lw=2.1, ls="--")
    right.axvspan(pd.Timestamp("2025-07-01"), pd.Timestamp("2026-12-31"), color="#EFEFEF", zorder=0)
    right.axvline(pd.Timestamp("2022-11-01"), color="#666666", ls=":", lw=1.1)
    right.text(pd.Timestamp("2022-11-01"), right.get_ylim()[1] * 0.92, "ChatGPT", ha="right", va="top", fontsize=9)
    right.set_ylabel("Papers per 3-month period")
    right.set_xlim(pd.Timestamp("2010-01-01"), pd.Timestamp("2026-12-31"))
    right.xaxis.set_major_locator(mdates.YearLocator(5))
    right.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    right.spines[["top", "right"]].set_visible(False)
    _save(fig, path)


def _plot_area(
    data: pd.DataFrame,
    category: str,
    value: str,
    order: list[str],
    colors: dict[str, str],
    ylabel: str,
    path: Path,
    *,
    chatgpt: bool = False,
    milestones: bool = False,
) -> None:
    wide = (
        data.pivot_table(index="month_start", columns=category, values=value, fill_value=0)
        .reindex(columns=order, fill_value=0)
        .sort_index()
    )
    fig, ax = plt.subplots(figsize=(9.7, 3.25))
    ax.stackplot(
        wide.index,
        *[wide[column] for column in order],
        labels=order,
        colors=[colors[column] for column in order],
        alpha=0.95,
    )
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    if chatgpt:
        ax.axvline(pd.Timestamp("2022-11-01"), color="#555555", ls=":", lw=1.1)
        if category == "approach_orientation":
            is_largest = wide["LLM/software-facing"].eq(wide.max(axis=1))
            candidates = wide.index[
                is_largest & (wide.index >= pd.Timestamp("2022-11-01"))
            ]
            if len(candidates):
                crossover = candidates[0]
                ax.axvline(crossover, color="#333333", lw=1.2)
                ax.scatter(
                    crossover,
                    -0.045,
                    marker="^",
                    color="#333333",
                    s=28,
                    transform=ax.get_xaxis_transform(),
                    clip_on=False,
                )
    if milestones:
        for date, label in [
            ("2022-11-01", "ChatGPT"),
            ("2023-03-01", "GPT-4"),
            ("2023-11-01", "GPTs/Retrieval"),
        ]:
            ax.axvline(pd.Timestamp(date), color="#555555", ls=":", lw=0.9)
            ax.text(pd.Timestamp(date), 1.01, label, ha="right", va="bottom", fontsize=8)
    ax.legend(frameon=False, ncol=min(4, len(order)), loc="upper center", bbox_to_anchor=(0.5, 1.22), fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    _save(fig, path)


def _plot_domain_adoption(data: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.7, 3.8))
    for domain, group in data.groupby("domain_high"):
        group = group[group["papers"].gt(0)]
        ax.plot(group["month_start"], group["llm_pct"], marker="o", ms=3, lw=2, label=domain)
    ax.set_ylabel("Papers using LLMs (%)")
    ax.set_ylim(0, 105)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.23), fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    _save(fig, path)


def _plot_family(data: pd.DataFrame, path: Path) -> None:
    wide = data.pivot_table(index="domain_high", columns="family_group", values="share", fill_value=0)
    wide = wide.loc[data.groupby("domain_high")["field_mentions"].max().sort_values(ascending=False).index]
    fig, ax = plt.subplots(figsize=(8.2, 4.5))
    left = np.zeros(len(wide))
    cmap = plt.get_cmap("tab20")
    for index, column in enumerate(wide.columns):
        ax.barh(wide.index, wide[column], left=left, label=column, color=cmap(index))
        left += wide[column].to_numpy()
    ax.invert_yaxis()
    ax.set_xlabel("Share of field mentions")
    ax.set_xlim(0, 1)
    ax.xaxis.set_major_formatter(PercentFormatter(1))
    ax.legend(frameon=False, bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    _save(fig, path)


def _plot_year_lines(
    data: pd.DataFrame,
    y: str,
    ylabel: str,
    path: Path,
    *,
    percent: bool = False,
) -> None:
    fig, ax = plt.subplots(figsize=(5.4, 4.0))
    for group in APPROACH_ORDER:
        subset = data[data["approach_group"].eq(group)]
        ax.plot(
            subset["publication_year"], subset[y], marker="o", lw=2.2,
            color=APPROACH_COLORS[group], label=group,
        )
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Year")
    if percent:
        ax.yaxis.set_major_formatter(PercentFormatter(1))
    else:
        ax.set_ylim(0, 15)
    ax.legend(frameon=False, fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    _save(fig, path)


def _plot_complexity_reporting(data: pd.DataFrame, path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(9.7, 3.8))
    positions = np.arange(len(data))
    colors = [COMPLEXITY_COLORS[value] for value in data["method_complexity"]]
    axes[0].barh(positions, data["mean_reporting_richness"], color=colors)
    axes[0].set_xlabel("Mean score (0–15)")
    axes[1].barh(positions, data["no_evaluation_pct"], color=colors)
    axes[1].set_xlabel("Papers (%)")
    axes[1].xaxis.set_major_formatter(lambda value, _: f"{value:.0f}%")
    for ax in axes:
        ax.set_yticks(positions, data["method_complexity"])
        ax.invert_yaxis()
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(w_pad=2.5)
    _save(fig, path)


def _plot_highbar(data: pd.DataFrame, path: Path) -> None:
    data = data.copy()
    fig, ax = plt.subplots(figsize=(7.5, 3.5))
    colors = [SENTIMENT_COLORS[value] for value in data["sentiment_group"]]
    ax.barh(data["sentiment_group"], data["highbar_pct"], color=colors)
    for index, row in data.reset_index(drop=True).iterrows():
        ax.text(row.highbar_pct + 1, index, f"{row.highbar_pct:.0f}%  (n={int(row.papers)})", va="center", fontsize=9)
    ax.set_xlabel("Papers reporting a high-bar concern (%)")
    ax.set_xlim(0, 90)
    ax.spines[["top", "right"]].set_visible(False)
    _save(fig, path)


def _plot_limitation_panels(data: pd.DataFrame, output_dir: Path) -> None:
    cmap = LinearSegmentedColormap.from_list("limitations", ["#EEF6FB", "#7EB8D4", "#D7193F"])
    labels = {
        "approach": "figure_s2a_by_approach.png",
        "domain_high": "figure_s2b_by_domain.png",
        "bert_family": "figure_s2c_by_bert_family.png",
        "llm_family": "figure_s2d_by_llm_family.png",
    }
    short = {
        "high bar needed but not achieved": "High bar unmet",
        "limited validation or benchmarking of AI outputs": "Limited validation",
        "performance sensitive to parameters or prompts": "Parameter/prompt sensitivity",
        "small data, narrow scope, or limited data availability": "Small/narrow data",
    }
    for dimension, filename in labels.items():
        subset = data[data["dimension"].eq(dimension)]
        wide = subset.pivot_table(index="group", columns="limitation", values="pct", fill_value=0)
        wide = wide.loc[subset.groupby("group")["papers"].max().sort_values(ascending=False).index]
        fig, ax = plt.subplots(figsize=(5.5, max(3.2, 0.42 * len(wide))))
        image = ax.imshow(wide, aspect="auto", cmap=cmap, vmin=0, vmax=70)
        ax.set_xticks(range(len(wide.columns)), [short[column] for column in wide.columns], rotation=30, ha="right")
        ax.set_yticks(range(len(wide.index)), wide.index)
        for row in range(len(wide)):
            for column in range(len(wide.columns)):
                ax.text(column, row, f"{wide.iloc[row, column]:.0f}", ha="center", va="center", fontsize=8)
        fig.colorbar(image, ax=ax, label="Papers reporting limitation (%)")
        _save(fig, output_dir / filename)
    fig, ax = plt.subplots(figsize=(5.2, 0.7))
    fig.colorbar(
        plt.cm.ScalarMappable(norm=Normalize(0, 70), cmap=cmap),
        cax=ax,
        orientation="horizontal",
        label="Papers reporting limitation (%)",
    )
    _save(fig, output_dir / "figure_s2_shared_colorbar.png")


def _plot_stage_reporting(data: pd.DataFrame, output_dir: Path) -> None:
    _plot_grouped_bars(
        data,
        "mean_evaluation_items",
        "Items per paper",
        output_dir / "figure_s3a_evaluation_items.png",
    )
    _plot_grouped_bars(
        data,
        "no_evaluation_pct",
        "Papers (%)",
        output_dir / "figure_s3b_no_evaluation.png",
        percent=True,
    )


def _plot_grouped_bars(
    data: pd.DataFrame, value: str, ylabel: str, path: Path, *, percent: bool = False
) -> None:
    fig, ax = plt.subplots(figsize=(5.8, 3.8))
    x = np.arange(len(STAGE_ORDER))
    width = 0.24
    for index, approach in enumerate(APPROACH_ORDER):
        values = (
            data[data["approach_group"].eq(approach)]
            .set_index("stage_group")[value]
            .reindex(STAGE_ORDER)
        )
        ax.bar(x + (index - 1) * width, values, width, color=APPROACH_COLORS[approach], label=approach)
    ax.set_xticks(x, STAGE_ORDER, rotation=15, ha="right")
    ax.set_ylabel(ylabel)
    if percent:
        ax.yaxis.set_major_formatter(lambda number, _: f"{number:.0f}%")
    ax.legend(frameon=False, fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    _save(fig, path)


def _plot_precision_recall(data: pd.DataFrame, output_dir: Path) -> None:
    names = {
        "Screening/selection": "figure_s4a_screening_precision_recall.png",
        "Data extraction": "figure_s4b_extraction_precision_recall.png",
    }
    for task, filename in names.items():
        subset = data[data["review_task"].eq(task)]
        fig, ax = plt.subplots(figsize=(5.2, 4.2))
        for approach in APPROACH_ORDER:
            group = subset[subset["approach_group"].eq(approach)]
            if group.empty:
                continue
            ax.scatter(group["precision"], group["recall"], s=25, alpha=0.38, color=APPROACH_COLORS[approach], label=f"{approach} (n={len(group)})")
            ax.scatter(group["precision"].median(), group["recall"].median(), s=125, marker="D", edgecolor="black", color=APPROACH_COLORS[approach])
        ax.axvline(0.8, color="#777777", ls=":")
        ax.axhline(0.8, color="#777777", ls=":")
        ax.set_xlim(0, 1.02)
        ax.set_ylim(0, 1.02)
        ax.set_xlabel("Reported precision")
        ax.set_ylabel("Reported recall")
        ax.legend(frameon=False, fontsize=7)
        _save(fig, output_dir / filename)
