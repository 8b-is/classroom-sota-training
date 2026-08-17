# classroom-sota-training

**A "Vének Tanácsa"** — Waldorf-módszertanú classroom training pipeline a
pupil-modell (quantal/ternary student) képesség-fejlesztéséhez.

## A koncepció

Egy 1.7B méretű, thresholded-ternary pupil-modell a terem közepén ül — mint
egy **aranyifjú**: tudásszomjas, nyitott, alakítható. Körülötte **8-9 nagyobb
tanár-modell** ("a vének tanácsa") ül, akik nem egyetlen cél-függvényt
nyomnak rá, hanem **Waldorf-módszertannal** tanítanak:

- **tanítanak** — tudást adnak át a saját modalitásukban
- **filozofálnak** — megvitatják a jelentést, nem csak a token-valószínűséget
- **képességet fejlesztenek** — a pupil nem utánzással, hanem értő
  elsajátítással tanul: a tanárok konszenzusától független, saját belső
  modelljét építi

A tanácskozás egy **geometric-mean softmax konszenzuson** keresztül érkezik a
pupilhez — a vének "egyhangú döntése" nem a többség lediktálása, hanem a
közös, kiegyensúlyozott irány.

## Architektúra

```
             ┌──────────────────────────────────────────┐
             │          A VÉNEK TANÁCSA (8-9 tanár)      │
             │  Qwen3-8B · Qwen3-14B · + tanár-bővítés   │
             │  (minden tanár saját logits-szavazat)     │
             └───────────────┬──────────────────────────┘
                             │ geometric-mean softmax konszenzus
                             ▼
             ┌──────────────────────────────────────────┐
             │           PUPIL (aranyifjú)               │
             │  Qwen3-1.7B thresholded-ternary (quantal) │
             │  deployed-forward: ternary matmul,         │
             │  tanul közben, nem utánzásra épít         │
             └──────────────────────────────────────────┘
```

- **Tanárok**: `teacher_logits.py` cache-eli a faculty logits-okat
  (Qwen3-8B + Qwen3-14B bf16, tokenizer byte-azonos a pupiléval).
- **Tanítási cél**: `train_quantal_classroom.py` — multi-faculty KL,
  geometric-mean softmax konszenzus, β-ramp epoch-séma.
- **Támogatás**: `train_quantal_distill.py` (single-teacher), `build_corpus_v2.py`
  (korpusz), `quantal_golden_logits.py` / `quantal_compare_logits.py` (verifikáció).
- **HF Jobs overlay**: `hf-overlay/` — `classroom_train.py` (HF Jobs wrapper),
  `harness_eval.py` (harness-eval a Dipankar-féle fix-pont teszthez).

## Eredmények

| Verzió | Tanítás | Best val CE |
|--------|---------|-------------|
| v2 single-teacher (H200) | Qwen3-14B | 1.8166 |
| **classroom (vének tanácsa)** | Qwen3-8B + Qwen3-14B | **1.6120** |
| harness-gate (régi ckpt, új stack) | — | 2.1369 (a javulás TRÉNING, nem harness) |

Publikált modell: [PeetPedro/quantal-classroom-1.6](https://huggingface.co/PeetPedro/quantal-classroom-1.6)

## Konvenciók

- A pipeline a **8b-is org alatt** fejlődik — a saját transformers forkunk
  (8b-is/transformers) a sovereign home base.
- A pupil quantal-stackje: `MLX-QUANT` (thresholded ternary, deployed-forward).
- Minden új tanár bekerülése = a vének tanácsának bővítése — a konszenzus
  módszer skálázható, a tanárok cserélhetők anélkül, hogy a pupil újratanulná
  a régieket.

## Licenc

Apache-2.0 (a tanár-alapmodellek licencét külön ellenőrizni; Qwen3 Apache-2.0).
