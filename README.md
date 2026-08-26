# ML Ops Edukace: Retrieval Pipeline POC

**Datum:** 2026-08-26 | **Autor:** outpost2026
**Status:** Aktivní vývoj | **Původ:** GT postmortem formalizace → organický růst

---

## Kontext

Projekt vznikl z jednoduchého trimmingu dat z `GT postmortem` dokumentu a organicky se rozvinul do širšího projektu zaměřeného na:

1. **Formalizaci GT postmortem** do JSONL formátu (108 entries, -50% tokenů)
2. **Vylepšení retrieval pipeline** — od SequenceMatcher po BM25 + Dense + RRF
3. **Osvojení ML Ops ontologie** — terminologie z oblasti AI/ML, která se shoduje s IT skills z trhu práce (MCP-Jobs skills catalog)

---

## Struktura

```
ML_Ops_edukace/
├── data/                       # Datové soubory
│   ├── gt_full.jsonl           # 108 GT entries (hlavní dataset)
│   ├── gt_schema.json          # JSON Schema pro validaci
│   ├── gt_rules.json           # 23 P-rules
│   ├── gt_meta.json            # Metadata
│   ├── test_queries.json       # 25 test queries (CZ+EN)
│   ├── gt_sample.jsonl         # 22-entry sample (historický)
│   └── gt_catalog_full_render.md  # Generovaný markdown
├── scripts/                    # Implementace
│   ├── extract_v2_improved.py  # Vylepšený extractor (108 entries)
│   ├── benchmark_full.py       # Plný benchmark
│   ├── test_all.py             # Test runner
│   ├── render_md.py            # JSONL → markdown
│   ├── extract_v2.py           # Původní extractor (historický)
│   ├── fix_rules.py            # Oprava rules (historický)
│   ├── fix_rules2.py           # Oprava rules (historický)
│   └── check_missing.py        # Kontrola chybějících polí
├── results/                    # Výsledky benchmarků
│   ├── full_benchmark.json     # Plný benchmark (108 entries)
│   ├── retrieval_comparison.json
│   └── compression_comparison.json
├── RETRIEVAL_RESEARCH.md       # Výzkumná zpráva + plán
├── EVALUATION.md               # Evaluace výsledků
└── README.md                   # Tento soubor
```

---

## Metodika

- **Komprese realismus (CPM)** — z `05_EPISTEMIKA/00_kompresni_realismus/`
- **SNR Princip** — z `04_KNOWLEDGE_BASE/01_reverse_engineering/RE_Methodology.md`
- **Tříkanálový model šumu (K0-K3)** — z CPM

---

## KLÍČOVÉ NÁLEZY

| Nález | Hodnota |
|-------|---------|
| JSONL komprese vs v2 markdown | -49.7% bytes, -49.1% tokens |
| JSONL MRR vs v2 (fuzzy) | +5.4% (0.661 vs 0.627) |
| JSONL Precision@3 vs v2 | -3.3% (0.580 vs 0.600) |
| Retrieval metrik: SequenceMatcher | Baseline (0.627 MRR) |
| Cílová metrika: BM25+TF-IDF+RRF | ~0.75-0.80 MRR (odhad) |

---

## ML Ops ontologie (cross-ref s MCP-Jobs)

| Pojem | MCP-Jobs kategorie | Weight | V našem projektu |
|-------|-------------------|--------|------------------|
| Embeddings | AI_CONCEPT | 0.50 | TF-IDF jako náhrada |
| Vector Database | AI_TOOL | 0.45 | numpy matrix |
| RAG | IT_SKILL | 0.50 | Retrieval pipeline |
| NLP | AI_FIELD | 0.45 | BM25, TF-IDF |
| PyTorch | ML_FRAMEWORK | 0.60 | (volitelné pro dense) |
| scikit-learn | ML_FRAMEWORK | 0.40 | (volitelné pro TF-IDF) |
| MLOps | METHODOLOGY | 0.50 | Benchmark pipeline |

---

## Spuštění

```bash
# Windows
$env:PYTHONIOENCODING='utf-8'
python -X utf8 scripts/benchmark_full.py

# Alternativa
python -X utf8 scripts/test_all.py
```

---

## Navazující projekty

- `B2B-Knowledge-Base/04_KNOWLEDGE_BASE/01_MCP/` — GT postmortem (v2 markdown)
- `MCP-Jobs/` — Skills catalog (94 skills, IT ontology)
- `linkedin-mcp-custom/` — LinkedIn scraping pipeline

---

*Vytvořeno: 2026-08-26 | Poslední aktualizace: 2026-08-26*
