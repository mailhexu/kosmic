---
type: Domain Topic
id: workstation/usage/unlimited-ocr
domain: workstation
audience: usage
artifact_role: guideline
status: draft
summary: OCR local PDFs with the GPU-backed Baidu Unlimited-OCR setup; use the per-page crop_mode runner for dense or scanned pages that fail stock multi-page OCR.
triggers: [OCR, PDF, Unlimited-OCR, blurry scan, crop_mode]
source_project: native
source_sha256: empty
aliases: [pdf ocr]
---

# Unlimited-OCR for local PDFs

OCR local PDFs, especially academic papers with equations, tables, and figures, with the local checkout of Baidu Unlimited-OCR on the NVIDIA GPU.

## Runtime

Use the explicit interpreter. Do not activate a virtual environment or use bare `uv pip`:

```bash
OCR_HOME="$HOME/projects/Unlimited-OCR"
OCR_PY="$OCR_HOME/.venv/bin/python"
```

This setup uses the Transformers implementation on the local GPU. Do not use the repository's SGLang `fa3` recipe on an RTX 3090; FlashAttention 3 is Hopper-specific.

## Stock multi-page run

1. Check the page count with `pdfinfo <pdf>`.
2. Run: `"$OCR_PY" "$OCR_HOME/ocr_pdfs.py" <pdf-or-dir> <output-root>`. A directory input OCRs every `*.pdf` recursively.
3. Output for `<name>.pdf` lands in `<output-root>/<name>/`: `result.md` (LaTeX equations, Markdown tables, `<PAGE>` markers), `images/`, and `result_with_boxes_*.jpg` visualizations.
4. The runner replaces an existing output directory. Inspect the destination first and get approval before re-running a target.

## Per-page crop_mode run for blurry pages

Stock multi-page OCR can return a tiny `result.md` full of "The image is too blurry to recognize any text content" on dense or old scanned PDFs. Use the per-page runner instead:

```bash
"$OCR_PY" "$OCR_HOME/ocr_pdf_perpage.py" INPUT.pdf OUTPUT_DIR
```

It renders pages at 300 dpi, calls `model.infer(prompt="<image>OCR:", image_size=640, crop_mode=True, save_results=True)`, and concatenates pages into `OUTPUT_DIR/result.md`. Expect about 90 seconds per page on an RTX 3090.

Known-good parameters are exactly `image_size=640, crop_mode=True`. Passing `base_size=1024` or `image_size=1024` fails with `CUDA error: CUBLAS_STATUS_EXECUTION_FAILED`. GPU memory is not the cause; 22 GB free still failed.

## Verify

1. Count `<PAGE` markers in `result.md` and compare with `pdfinfo` `Pages`.
2. Read the beginning and a mid-file page. Confirm real body text, not "too blurry" lines.
3. Tables arrive as HTML `<table>`; math as `\( ... \)` LaTeX.
4. Report the exact output path and any visible OCR limits. Do not silently correct model output.

## First-time installation

Install only when `$OCR_PY` or the runner is missing. Clone `https://github.com/baidu/Unlimited-OCR.git`, create a Python 3.12 venv with `uv venv --python 3.12`, and install with `uv pip install --python "$OCR_PY"`: torch 2.10.0, torchvision 0.25.0, transformers 4.57.1, Pillow 12.1.1, matplotlib 3.10.8, einops, addict, easydict, pymupdf 1.27.2.2, psutil 7.2.2. Verify `torch.cuda.is_available()` and the intended GPU before the first long inference.
