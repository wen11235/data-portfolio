# A Comparative Study for Brain Tumor Segmentation in MRI Scans

**TL;DR:** Trained and compared 4 U-Net variants for pixel-level brain tumor segmentation (best: EfficientNet-B0 U-Net, 0.854 Dice on tumor-containing slices) — then went further and showed the benchmark itself is misleading depending on evaluation protocol, that the model is badly overconfident on its failures, and that zero-shot transfer to a new hospital's scanner fails hard but recovers almost completely after fine-tuning.

[📄 Full report](report.html) · [📓 Notebook](notebooks/brain_tumor_segmentation.ipynb) · [📑 Original PDF write-up](Final_Report.pdf)

*Originally built as a graduate coursework deliverable (Information Management), included here because the methodology — architecture comparison, evaluation-protocol sensitivity, failure analysis, confidence calibration, transfer learning — generalizes directly to any applied ML problem, not just medical imaging.*

## Problem

Brain tumor segmentation from MRI is a pixel-level (not image-level) prediction task with severe class imbalance — tumor pixels are a small minority of each scan. The project's real question isn't "which architecture wins," it's: **when should you trust a segmentation model's output, and when will it quietly fail?**

## Data

[LGG MRI Segmentation](https://www.kaggle.com/datasets/mateuszbuda/lgg-mri-segmentation) (Kaggle) — 3,929 2D MRI slices with binary tumor masks; filtered to 1,373 tumor-positive slices (961 train / 206 val / 206 test). A second dataset, [BRISC2025](https://www.kaggle.com/datasets/briscdataset/brisc2025), was used only for the transfer-learning experiment. Not included in this repo (large medical imaging data, requires Kaggle credentials + GPU to reproduce — see the notebook's first cells).

## Method

1. **4 architectures**: Vanilla U-Net (from scratch), Attention U-Net, ResNet34 U-Net, EfficientNet-B0 U-Net (last two with pretrained encoders).
2. **3 loss functions**: BCE-Dice, Dice-only, Tversky — to study how the optimization objective trades off precision vs recall under class imbalance.
3. **2 evaluation protocols**: full dataset (including tumor-free slices) vs positive-only (tumor-containing slices only) — deliberately compared against each other, see finding below.
4. **Tumor-size stratified evaluation**, **failure-mode categorization**, **prediction-confidence analysis**, and **cross-dataset transfer learning** (zero-shot + fine-tuned on BRISC2025).

## Results

| Model | Full-dataset Dice | Positive-only Dice | IoU | Precision | Recall |
|---|---|---|---|---|---|
| Vanilla U-Net | 0.834 | 0.785 | 0.658 | 0.711 | 0.905 |
| ResNet34 U-Net | 0.857 | 0.849 | 0.766 | 0.852 | 0.879 |
| **EfficientNet-B0 U-Net** | **0.912** | **0.854** | **0.770** | 0.850 | 0.882 |

Pretrained encoders (ResNet34, EfficientNet-B0) clearly beat a from-scratch baseline. EfficientNet-B0 wins on both protocols while using the **fewest parameters (6.25M vs ResNet34's 24.4M)** at nearly identical inference speed (~15ms/image) — the strongest accuracy-per-parameter tradeoff of the four.

### The most important finding: evaluation protocol changes the conclusion

Under full-dataset evaluation, EfficientNet-B0 looks dramatically ahead (0.912 vs ResNet34's 0.857). Restricting to tumor-containing slices only, that gap nearly disappears (0.854 vs 0.849). Full-dataset evaluation rewards correctly predicting *empty* masks on tumor-free slices — which inflates the score without reflecting real segmentation quality. **Reporting a single headline Dice score without stating which protocol produced it is misleading**, and this generalizes well past medical imaging to any benchmark with an easy-majority-class subset.

### Performance collapses on very small tumors

| Tumor size | Mean Dice | n |
|---|---|---|
| Medium | 0.923 | 46 |
| Small | 0.894 | 117 |
| Very small | **0.674** | 43 |

Aggregate Dice hides this: the cases most likely to matter clinically (small, early-stage lesions) are exactly where the model is least reliable, and where performance variance is highest.

### The model is confidently wrong

This is the sharpest result in the project. Failed segmentations (mean Dice 0.374) had **average confidence 0.998** — essentially indistinguishable from high-quality segmentations (mean Dice 0.924, confidence 0.996). Raw softmax confidence does not separate successes from failures at all here. For any application where a confidence score might gate a human review step, that's a real problem, not a footnote.

### Zero-shot transfer fails; fine-tuning mostly fixes it

| Setting | Dice |
|---|---|
| Zero-shot, LGG → BRISC2025 | 0.452 |
| Fine-tuned, LGG → BRISC2025 | **0.816** |

Strong in-domain performance did not transfer to a different scanner/protocol out of the box — but the learned features were still useful once adapted, recovering most of the original performance with limited fine-tuning.

## What I'd improve with more time

Being upfront about this rather than presenting it as finished:

- **Single train/val/test split, single seed** per experiment — no confidence intervals or significance testing on the architecture comparison, so the ResNet34 vs EfficientNet-B0 gap (0.849 vs 0.854) is within noise range and shouldn't be over-read.
- **2D slices, not 3D volumes** — discards cross-slice spatial context that a 3D-aware model (or even slice-sequence input) could use.
- **Confidence analysis used raw softmax output**, not a calibrated uncertainty method (temperature scaling, MC dropout, deep ensembles) — the poor-calibration finding is real, but a proper calibration method is the natural next step, not just a diagnosis.
- **Single primary dataset** for the main benchmarking — BRISC2025 was only used for transfer learning, not as a second in-domain benchmark.

## Skills demonstrated

PyTorch, U-Net / ResNet / EfficientNet / Attention U-Net architectures, `segmentation_models.pytorch`, custom loss functions (Dice, Tversky, BCE-Dice), evaluation methodology design, failure analysis, model calibration/uncertainty analysis, transfer learning.
