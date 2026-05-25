# Copyright 2026 Fuwang Feng
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pathlib import Path
import re
import shutil


ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = ROOT / "docs" / "paper"
FIG_DIR = PAPER_DIR / "figures" / "paper_v2_20260521"
OUT_DIR = PAPER_DIR / "submission"

TITLE = (
    "Measurement Validation Reveals Five Dissociable Operational Constructs "
    "Underlying Self-Model and Agency in Artificial Neural Architectures"
)


FIGURES = {
    "Figure 1 summarizes this validation-diagnosis-refinement workflow.": (
        "figure1_validation_framework_v2.png",
        "Figure 1. Validation-diagnosis-refinement workflow.",
    ),
    "The three diagnostic-refinement cycles are summarized in Figure 2.": (
        "figure2_diagnostic_refinement_cycles.png",
        "Figure 2. Three diagnostic-refinement cycles.",
    ),
    "This supports the interpretation that hard probes track functional meta-monitor quality, not merely module presence (Figure 5).": (
        "figure5_distributed_graded_controls.png",
        "Figure 5. Distributed graded meta-monitor controls.",
    ),
    "These correlations are visualized in Figure 3.": (
        "figure3_five_construct_validation.png",
        "Figure 3. Five validated operational constructs.",
    ),
    "This supports an operational triple dissociation among workspace, action-outcome, and meta-monitoring mechanisms (Figure 4).": (
        "figure4_triple_dissociation.png",
        "Figure 4. Mechanistic triple dissociation.",
    ),
    "The Transformer-inspired follow-up tested whether the mechanism pattern generalized to an attention-based substrate. The initial 2x2 run showed selective mechanism effects while also exposing architecture-specific measurement limits (Figure 6).": (
        "figure6_transformer_diagnostics.png",
        "Figure 6. Transformer follow-up diagnostics.",
    ),
}


def promote_headings(text: str) -> str:
    lines = []
    for line in text.splitlines():
        if line.startswith("# "):
            continue
        if line.startswith("#### "):
            lines.append("### " + line[5:])
        elif line.startswith("### "):
            lines.append("## " + line[4:])
        elif line.startswith("## "):
            lines.append("# " + line[3:])
        else:
            lines.append(line)
    return "\n".join(lines).strip() + "\n"


def insert_figures(text: str) -> str:
    for anchor, (filename, caption) in FIGURES.items():
        figure_md = f"\n\n![{caption}](figures/{filename}){{width=95%}}\n"
        if anchor in text and filename not in text:
            text = text.replace(anchor, anchor + figure_md)
    return text


def add_table_caption(text: str) -> str:
    table_header = "| Construct | n | Proxy-test r (95% CI) | p | Status | Mechanism |"
    caption = "**Table 1. Validated operational constructs and associated mechanisms.**\n\n"
    if table_header in text and caption not in text:
        text = text.replace(table_header, caption + table_header)
    return text


def normalize_markdown_for_submission(text: str) -> str:
    text = promote_headings(text)
    text = insert_figures(text)
    text = add_table_caption(text)
    # Pandoc treats backtick-heavy statistical text well, but escaped arrows are
    # safer in generated TeX/DOCX outputs when kept as plain text.
    text = text.replace("--", "\u2013")
    return text


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig_out = OUT_DIR / "figures"
    fig_out.mkdir(parents=True, exist_ok=True)

    for src in FIG_DIR.glob("figure*.png"):
        shutil.copy2(src, fig_out / src.name)

    shutil.copy2(PAPER_DIR / "references.bib", OUT_DIR / "references.bib")

    source = (PAPER_DIR / "measurement_validation_v2.md").read_text(encoding="utf-8")
    body = normalize_markdown_for_submission(source)

    yaml = f"""---
title: "{TITLE}"
author:
  - "Fuwang Feng, Independent Researcher"
date: ""
papersize: letter
fontsize: 11pt
geometry: margin=1in
linestretch: 1.08
colorlinks: true
linkcolor: blue
urlcolor: blue
---

"""
    out_md = OUT_DIR / "measurement_validation_submission.md"
    out_md.write_text(yaml + body, encoding="utf-8", newline="\n")

    print(out_md)
    print(fig_out)


if __name__ == "__main__":
    main()
