# PRISMA-LLM

[Paper on arXiv](https://arxiv.org/abs/2609.11559)

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

## Feedback

Please open a GitHub issue to suggest a
missing item, clarify applicability or propose a new workflow type.

## License

The analysis code is licensed under the
[Apache License 2.0](LICENSE). The checklist, framework materials and
documentation are licensed under
[Creative Commons Attribution 4.0 International](LICENSE-CONTENT).

## Citation

If you use PRISMA-LLM, please cite:

```bibtex
@article{zabaleta2026prismallm,
  title = {{PRISMA-LLM}: An Empirical Reporting Framework for {AI}-Assisted Systematic Reviews},
  author = {Zabaleta, Miguel and Lin, Baihan},
  journal = {arXiv preprint arXiv:2609.11559},
  year = {2026},
  doi = {10.48550/arXiv.2609.11559},
  url = {https://arxiv.org/abs/2609.11559}
}
```
