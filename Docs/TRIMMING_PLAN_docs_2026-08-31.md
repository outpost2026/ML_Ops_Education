# Trimming Plán — docs/ 13 MD → 8+5 ARCHIVE

**Datum:** 2026-08-31 | **Autor:** outpost2026 | **Repo:** `ML_Ops_edukace` | **Subdir:** `docs/` (kanon, `ea464a9` mv z kořene)
**Metodika:** Sémantická analýza `PBL 60/20/10/10` + `SNR` + `Jaccard` + `EROI` (jako `B2B-Knowledge-Base/01_METODIKY/TRIMMING_PLAN_04_KNOWLEDGE_BASE_2026-08-01.md`)
**Vstup:** `docs/` 13 MD, 207KB, 4130 řádků, `RAG/QER/RTF/MLOps` ontologie, duplicity `Jacc>0.15`

---

## 1. Sémantická mapa 13 MD

| # | Soubor | KB | Řádků | Jádro | Duplicita Jacc | EROI | SNR |
|---|--------|----|-------|-------|----------------|------|-----|
| 1 | `RETRIEVAL_RESEARCH.md` | 44.5 | 481 | Kanon 4-stage pipeline, 8 termů glossary, 8 kroků Cesta A 0B MRR 0.7067 | — | 9/10 | **Keep** — single source, `hSNR` note `IR-001`–`IR-004` v :10 |
| 2 | `EVALUATION.md` | 14 | 259 | Benchmark 108×50, 12 tabulek, MRR/Prec/Recall, komprese -49% | — | 9/10 | **Keep** — ground truth `GT 118KB→59KB` |
| 3 | `MCP_ECOSYSTEM_ADAPTATION_v1.md` | 34.6 | 319 | 5 MCP 42 tools, 4 varianty P0/P1/P2/C, 4+1 pipeline | — | 9/10 | **Keep** — prospektivní výzkum `5` serverů |
| 4 | `RETRIEVAL_BOTTLENECK_ANALYSIS_v1.md` | 13.4 | 130 | 5 bottlenecků B1-B5, ablace `b 0-1`, `win 2000-full` | Jacc 0.20 s P0_IMPROVEMENT | 9/10 | **Keep** — `B1-B5` + `window 4000` |
| 5 | `P0_IMPROVEMENT_PROPOSAL_v1.md` | 8.5 | 87 | P0 v1→v2 `k1 1.5→1.2 b 0.75→0.25 k 60→20` + chunk 512 | Jacc 0.20 s BOTTLENECK | 9/10 | **Keep** — `I1-I4` 8h |
| 6 | `CANDIDATE_TOOLS_ANALYSIS_v1.md` | 9.2 | 91 | `_stahovani` 1.2GB wiki.en.vec + `nltk`/`sklearn` | — | 8/10 | **Keep** — `wiki.en.vec` junior neví |
| 7 | `GLOSSARY_ML_RAG_QER_v2.md` | 6.7 | 47 | **hSNR 21 termů** (BM25/RAG/QER/RTF/HNSW/NC) 0 balastu | vs via_BASE/P0 0.35 | 9/10 | **Keep** — kanon `v2` destilace ( `via_*` raw) |
| 8 | `ML_AI_MLOps_Education_Playground_v2.0.md` | 29.8 | 1542 | **Korekce v1** — SNR audit, `retrieve.py` linky, `Sec@3` odstraněno, `TF-IDF≠dense` | Jacc 0.22 s v1 | 9/10 | **Keep** — living doc `v2` (v1 superseded) |
| 9 | `GLOSSARY_ML_RAG_QER_via_BASE_v1.md` | 5.3 | 53 | Raw 25 termů via `score=sum` (šum `Archivace`, `Credentials`) | **Jacc 0.35** s via_P0 | 7/10 | **ARCHIVE** — raw kaskáda, nahrazeno `v2` 21 hSNR |
| 10 | `GLOSSARY_ML_RAG_QER_via_P0_v1.md` | 10 | 92 | Raw 65 termů via `BM25+RRF` (duplikace `0 Cache`) | Jacc 0.35 | 8/10 | **ARCHIVE** — raw kaskáda, `v2` je destilace |
| 11 | `ONTOLOGY_GLOSSARY_DIFF_ANALYSIS_v1.md` | 6.8 | 52 | Diff `25 vs 65` (8 společných, 17 only_base, 57 only_p0) | — | 8/10 | **ARCHIVE** — diff `via_*` → `v2` single source, historický |
| 12 | `ML_AI_MLOps_Education_Playground_v1.0.md` | 33.2 | 1572 | `v1` — 90% LLM, `2246` ř. `Ground Truth→Feynman` bez kód linků | Jacc 0.22 s v2 | 7/10 | **ARCHIVE** — superseded `v2` (SNR audit korekce) |
| 13 | `Glossary_MLops_deepseek.md` | 15.1 | 207 | Deepseek 15KB `BM25` 19×, `MCP` 4×, Feynman `θ/λ`, `Precision@K` | — | 7/10 | **ARCHIVE** — generický `ML` (15KB) vs `RETRIEVAL_RESEARCH:8` 8 termů + `v2` 21 hSNR, `via_P0` 10KB duplikuje |

**Celkem:** 13 MD, 207KB, `RAG 6-23×`, `MLOps 10-19×`, `BM25 6-65×` — jádro `RETRIEVAL_RESEARCH` 44KB, `MCP_ECOSYSTEM` 34KB, `Playground v2` 29KB = 107KB (52% obsahu) pro `PBL`.

---

## 2. Návrh trimmingu — 8 Keep + 5 ARCHIVE

**Keep 8 (kanon, 132KB, 64%):** `RETRIEVAL_RESEARCH`, `EVALUATION`, `MCP_ECOSYSTEM`, `RETRIEVAL_BOTTLENECK`, `P0_IMPROVEMENT`, `CANDIDATE`, `GLOSSARY v2` (21 hSNR), `Playground v2` (korekce).

**ARCHIVE 5 (75KB, 36%):** `via_BASE` + `via_P0` (raw 2 kaskády → `v2`), `ONTOLOGY_DIFF` (diff raw → `v2`), `Playground v1` (superseded `v2`), `Glossary_deepseek` (15KB generický vs `v2` 21 hSNR + `RETRIEVAL_RESEARCH:8`).

**Důvod (SNR):** `via_BASE/P0` Jacc 0.35 duplikace, `v2` je `hSNR` 21/25+65 destilace — `via_*` balast `100% determinismus`, `Archivace` (25 termů) vs `0 Cache` (65 termů) → `v2` 0 balastu. `Playground v1→v2` Jacc 0.22, v2 odstranilo `Sec@3` + `TF-IDF≠dense`. `Glossary_deepseek` 15KB duplikuje `RETRIEVAL_RESEARCH:8` 8 termů, ale bez `QER/RTF/NC` (`EVALUATION` 0.7067).

**Provedení (build mode, po schválení):**
```powershell
New-Item -ItemType Directory -Path "docs/_ARCHIVE" -Force
Move-Item -Path "docs/GLOSSARY_ML_RAG_QER_via_BASE_v1.md" -Destination "docs/_ARCHIVE/"
Move-Item -Path "docs/GLOSSARY_ML_RAG_QER_via_P0_v1.md" -Destination "docs/_ARCHIVE/"
Move-Item -Path "docs/ONTOLOGY_GLOSSARY_DIFF_ANALYSIS_v1.md" -Destination "docs/_ARCHIVE/"
Move-Item -Path "docs/ML_AI_MLOps_Education_Playground_v1.0.md" -Destination "docs/_ARCHIVE/"
Move-Item -Path "docs/Glossary_MLops_deepseek.md" -Destination "docs/_ARCHIVE/"
# Výsledek: docs/ 8 MD (132KB) + docs/_ARCHIVE/ 5 MD (75KB) = 13 celkem, 0 ztráta, git mv zachová historii
```

**Validace (jako `00_STRATEGIE` trimming):** `git status` → `D  docs/via_BASE` `A  docs/_ARCHIVE/via_BASE` (8×), `git ls-files docs/` 8 vs `docs/_ARCHIVE/` 5, `Get-ChildItem docs -Recurse` 13, `py -3 -m json.tool docs/_ARCHIVE/...` OK.

**Alternativa (ponechat):** Pokud chceš `Glossary_deepseek` 15KB jako `via_P0` reference (Feynman `θ/λ` 19×), ponech v `docs/` → pak `ARCHIVE 4` (via_BASE, via_P0, Diff, Playground v1) = 68KB 32%.

**Doporučení:** **ARCHIVE 5** — `v2` je kanon 21 hSNR, raw `via_*` + `v1` + `deepseek` jsou `PBL` mezikroky (jako `B2B-KB/_ARCHIVE`).

*Navrženo 2026-08-31 — PBL 60/20/10/10: trimming = `signál/(signál+šum)` 132KB/207KB = 64% keep.*
