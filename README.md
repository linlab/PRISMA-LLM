# PRISMA-LLM

PRISMA-LLM adds reporting guidance for systematic reviews that use LLMs or
AI-enabled software in evidence-processing tasks. It supplements PRISMA 2020
with implementation, evaluation, limitation and reproducibility requirements.

## Start here

- [Reporting instructions](framework/reporting_instructions.md), including the
  quick and expanded checklists and the requirements by method-complexity level
- [Fillable reporting checklist](framework/PRISMA-LLM_reporting_checklist.xlsx)
- [Evidence and guidance informing the checklist](framework/checklist_evidence.csv)
- [Reproduce the empirical analysis](analysis/README.md)

## Empirical analysis

The analysis reads the harmonized corpus from the public
[SciLitBench](https://github.com/linlab/SciLitBench) repository. One command
regenerates the paper-level analysis data, plot data, tables and figure panels;
see [`analysis/README.md`](analysis/README.md).

## Repository map

```text
framework/   Reporting instructions, fillable checklist and supporting evidence
analysis/    Reproduction code and publication-date tables
```

## Status

Version 0.1.0 is the initial release. Formal consensus development,
usability testing, prospective validation and review by the PRISMA Executive
remain future work.

## Citation and feedback

Citation metadata are in [`CITATION.cff`](CITATION.cff) and will be updated with
the preprint identifier after posting. Please open a GitHub issue to suggest a
missing item, clarify applicability or propose a new workflow type.

## License

The analysis code is licensed under the
[Apache License 2.0](LICENSE). The checklist, framework materials and
documentation are licensed under
[Creative Commons Attribution 4.0 International](LICENSE-CONTENT).
