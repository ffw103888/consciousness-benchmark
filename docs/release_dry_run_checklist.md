# Release Dry-Run Checklist

Use this checklist before making the repository public or uploading the
preprint package.

## Local Package

- Confirm the manuscript PDF opens:
  `docs/paper/submission/measurement_validation_submission.pdf`
- Confirm the supplementary PDF opens:
  `docs/paper/submission/measurement_validation_supplementary.pdf`
- Confirm the submission zip exists and is not git-ignored:
  `docs/paper/measurement_validation_submission_package.zip`
- Confirm `CITATION.cff` appears in the repository root.
- Confirm README links resolve locally.

## OSF / Zenodo Dry Run

- Create a private draft project or sandbox upload.
- Upload the manuscript PDF, supplementary PDF, and submission package.
- Use the title:
  `Measurement Validation Reveals Five Dissociable Operational Constructs Underlying Self-Model and Agency in Artificial Neural Architectures`
- Use author:
  `Fuwang Feng, Independent Researcher`
- Use keywords:
  `construct validity`, `agency`, `self-model`, `artificial neural architectures`, `benchmark`
- Confirm the rendered PDF figures are legible in the browser preview.
- Do not make the draft public until the release order is confirmed.

## Repository Release

- Keep the repository private until the preprint is public.
- After the preprint is public, update README with the preprint URL.
- Push a `v0.1.0` tag after the public release.
- Verify GitHub shows "Cite this repository" from `CITATION.cff`.

## Post-Release

- Send individualized notes only after the preprint and repository are both public.
- Monitor GitHub Issues and email for corrections.
- If a material error is found, prepare a single coherent v2 rather than many small revisions.
