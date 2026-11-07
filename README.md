# ML Ops Edukace: Retrieval Pipeline POC

**Datum:** 2026-08-26 | **Autor:** outpost2026
**Status:** Aktivní vývoj | **Původ:** GT postmortem formalizace → organický růst

<!-- gt-stats: entries=121 rules=106 source_version=24 -->

---

## Kontext

Projekt vznikl z jednoduchého trimmingu dat z `GT postmortem` dokumentu a organicky se rozvinul do širšího projektu zaměřeného na:

1. **Formalizaci GT postmortem** do JSONL formátu (121 entries, −50 % tokenů)
2. **Vylepšení retrieval pipeline** — od SequenceMatcher po BM25 + RRF + CLI nástroj
3. **Osvojení ML Ops ontologie** — terminologie z oblasti AI/ML, která se shoduje s IT skills z trhu práce (MCP-Jobs skills catalog)

---

## Struktura

```
ML_Ops_edukace/
├── data/                       # Datové soubory
│   ├── gt_full.jsonl           # 121 GT entries (hlavní dataset)
│   ├── gt_schema.json          # JSON Schema pro validaci
│   ├── gt_rules.json           # 106 P-rules (P1-P109 + P-GCP-01..05, title+text)
│   ├── gt_meta.json            # Metadata
│   ├── test_queries.json       # 25 test queries (CZ+EN)
│   ├── gt_sample.jsonl         # 22-entry sample (historický)
│   └── gt_catalog_full_render.md  # Generovaný markdown
├── scripts/                    # Implementace
│   ├── extract_v2_improved.py  # Vylepšený extractor (108 entries)
│   ├── benchmark_full.py       # Plný benchmark
│   ├── test_all.py             # Test runner
│   ├── render_full.py          # JSONL → gt_catalog_full_render.md
│   ├── render_md.py            # (historický) sample → markdown
│   ├── ensemble_retrieval.py   # BM25+Seq RRF (VÍTĚZ)
│   ├── svd_expansion_retrieval.py  # SVD + query expansion + weighted RRF
│   ├── mmr_retrieval.py        # MMR (diverzita)
│   ├── hybrid_retrieval.py     # BM25 + TF-IDF + RRF (Cesta A)
│   ├── d1_word2vec_retrieval.py    # Word2Vec (selhalo)
│   ├── glove_retrieval.py      # GloVe (selhalo)
│   ├── enrichment_retrieval.py # BM25 + metadata enrichment
│   ├── fix_root_cause.py       # Oprava root_cause z markdownu
│   ├── extract_v2.py           # Původní extractor (historický)
│   ├── fix_rules.py            # Oprava rules (historický)
│   ├── fix_rules2.py           # Oprava rules (historický)
│   └── check_missing.py        # Kontrola chybějících polí
├── results/                    # Výsledky benchmarků
│   ├── ensemble_benchmark.json # BM25+Seq RRF (VÍTĚZ)
│   ├── svd_expansion_benchmark.json  # SVD + expansion
│   ├── mmr_benchmark.json      # MMR (diverzita)
│   ├── full_benchmark.json     # Plný benchmark (108 entries)
│   ├── hybrid_benchmark.json   # BM25 + TF-IDF + RRF
│   ├── d1_word2vec_benchmark.json    # Word2Vec (selhalo)
│   ├── glove_benchmark.json    # GloVe (selhalo)
│   ├── enrichment_benchmark.json     # Metadata enrichment
│   ├── p0_baseline.json       # P0 balík: before/after s SHA-256 datasetu
│   ├── retrieval_comparison.json
│   └── compression_comparison.json
├── retrieve.py                 # CLI retrieval nástroj
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
| Dataset (aktuální) | 121 entries, 106 pravidel, SHA-256 `d7d75222…2a39` |
| Retrieval 121 entries, 50 dotazů | **MRR 0.6367**, Hits@5 38/50, Prec@3 0.5900, Recall@5 0.6233 |
| P0 balík (freshness + abstention + rules + re-extrakce) | MRR −0,2 %, hits ±0, pravidel 36 → **106** |
| CLI nástroj | `python -X utf8 retrieve.py "dotaz"` |

> Historické hodnoty z 26. 8. (0.6613 / 0.7067 / 0.84) pocházejí z jiných retrieverů a jiného datasetu a **nemají hash datasetu** → nejsou reprodukovatelné, nesrovnávat. Aktuální čísla viz `results/p0_baseline.json`.

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
# CLI retrieval nástroj (rychlý dotaz)
python -X utf8 retrieve.py "timeout v MCP serveru"

# Interactive mode
python -X utf8 retrieve.py --interactive

# Benchmark
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

*Vytvořeno: 2026-08-26 | Poslední aktualizace: 2026-11-04*
