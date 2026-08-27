# Ontology Glossary — Sémantická Dif Analýza (BASE vs P0)

**Datum:** 2026-08-27 | **Autor:** outpost2026 | **Verze:** 1.0 | **Repo:** `ML_Ops_edukace`
**Typ:** Analýza geneze artefaktu | **EROI:** 9/10 | **Test:** 3. v řadě — geneze glosáře ML/RAG/QER z `_github` via 2 nástroje
**Korpus:** `B2B-Knowledge-Base` 121 docs + `ML_Ops_edukace` 8 + `mcp-retrieval` 6 = 135 docs (4000-window, avg_dl 414)
**Nástroje:** `BASE = cnc_tools_kb_search` (`score=sum 1 if w in text` `mcp-local-server/tools/kb_search.py:38`) vs `P0 = BM25(k1=1.5,b=0.75)+Seq+RRF(k=60)` (`mcp-retrieval/retrieval.py:27-141`)
**Dotazy:** 7 (`ONTO_Q0` original `ML RAG QER glossary ontologie` + 6 inferred QER/RTF/RAG) — `TEMP_workflow_sim/ONTOLOGY_GLOSSARY_DRY_RUN/ontology_test_queries.json`
**Výstup:** `GLOSSARY_ML_RAG_QER_via_BASE_v1.md` (25 termů, 18 docs) vs `GLOSSARY_ML_RAG_QER_via_P0_v1.md` (65 termů, 17 docs) — oba v `ML_Ops_edukace/` (kopie z `TEMP/.../results/`)

---

## 1. Metriky — ML (MRR/Prec@3/Recall/Hits) + tokeny/rychlost

| Systém | MRR | Prec@3 | Recall | Hits | Avg ms/q | Avg tok top5 | Build |
|--------|-----|--------|--------|------|----------|--------------|-------|
| **BASE** | 0.2905 | 0.1429 | 0.3333 | 6/7 | 150.5ms | ~176 tok | 0ms |
| **P0** | **0.5238** | **0.3810** | **0.5714** | **6/7** | **19.2ms** | **~161 tok** | 701ms (100ms amort) |
| **Delta** | **+80.3%** | **+166%** | **+71.4%** | 0 | **-87%** | -15 tok | — |

**Komprese (jako `EVALUATION.md:6.2`):** Bez retrieval `678493 tok (2.7MB)` → s top5 `176/161 tok` → **3848x / 4211x** (91% redukce LLM context, oba stejně).

**Per-query dual (sekvence):**

| Query | BASE MRR → P0 MRR | Top1 BASE → P0 | Proč |
|-------|-------------------|----------------|------|
| Q0 `ML RAG QER glossary ontologie` (original) | 0.50 → 0.33 | `SKILL_GAPS` → `RETRIEVAL_BOTTLENECK` | BASE `score=4` pro `SKILL_GAPS` (obsahuje `ML/RAG/QER` v `MCP-Jobs` contextu) → rank1, P0 `BM25 IDF` `QER` df=3 vzácné → rank1 `RETRIEVAL_BOTTLENECK` (obsahuje `QER` 12×) — oba hit, ale P0 přesnější `ML/RAG/QER` ontologie |
| Q1 `RAG QER RTF retrieval glossary` | 0.00 → 1.00 | `SKILL_GAPS` miss → `RETRIEVAL_BOTTLENECK` hit | BASE `score=sum` pro `RAG` (df 12) + `QER` (df 3) → `SKILL_GAPS` (obsahuje `RAG` 2×) rank1, ale expected `RETRIEVAL_BOTTLENECK` až rank6 → MRR 0.00; P0 `BM25` IDF `QER` vysoké + `RTF` df 2 → rank1 `RETRIEVAL_BOTTLENECK` → MRR 1.00 — **P0 IDF win** |
| Q2 `embedding vector database glossary` | 0.25 → 1.00 | `SQL_ADOPCE` → `RETRIEVAL_RESEARCH` | BASE `score=3` pro `SQL_ADOPCE` (obsahuje `glossary` 1×), P0 `BM25` `embedding` df 8 → rank1 `RETRIEVAL_RESEARCH` (obsahuje `Embedding` 5× + `Vector Database` 3×) |
| Q6 `ontology epistemika komprese` | 0.25 → 0.50 | `TRIMMING_PLAN` → `ontologie_kompresnich...` | BASE `TRIMMING_PLAN` (obsahuje `ontologie` 1×), P0 `ontologie_kompresnich_modelu` (obsahuje `ontologie` 8× + `komprese` 12×) → IDF `komprese` vysoké |

**Inferované QER (Q1-Q6) by BASE nepoložil efektivně** — P0 je položil s BM25 win na 3 ze 6.

---

## 2. Geneze glosářů — 2 analogie

### Via BASE (18 docs, 25 termů)

**Zdroje (dedup top5 per query):**
- `SKILL_GAPS_ROZBOR_Q3_2026_v2.md`, `SWE_GLOSSARY_zive_v1.md`, `SQL_ADOPCE_PLAN`, `TRIMMING_PLAN`, `SQL_KANDIDATI`, `KORELACE_STRUKTURY`, `HANDOFF_COMPACT`, `AGENTS.md`...

**Termy (25, výběr):** `100% determinismus`, `Data Pipeline (ETL)`, `MLOps`, `Vector Database` (ale s šumem `Archivace 9 souborů`, `Credentials / secrets` — řádky s `|` ale ne glossary)

**Charakter:** Šum — substring `RAG in text` najde `RAG` v `MCP-Jobs` skills (df 12) i v `SQL_KANDIDATI` (obsahuje `RAG` náhodně), rank náhodný. Proto MRR 0.29.

### Via P0 (17 docs, 65 termů)

**Zdroje (dedup):**
- `ML_Ops_edukace/RETRIEVAL_BOTTLENECK_ANALYSIS_v1.md`, `RETRIEVAL_RESEARCH.md`, `MCP_ECOSYSTEM_ADAPTATION_v1.md`, `README.md`, `SWE_GLOSSARY`, `POSTGRESQL_ontologie`, `ontologie_kompresnich_modelu`...

**Termy (65, výběr):** `0 Cache`, `1 BM25`, `2 Fuzzy`, `BM25`, `Embedding`, `Vector Database`, `RAG`, `QER`, `RTF`, `HNSW`, `RRF`, `MMR`, `Cross-encoder`, `Bi-encoder`, `MRR`, `NDCG`, `Prec@3`, `Recall`, `Latent space`, `ANN`, `MLOps`, `TF-IDF`, `Cosine Similarity`...

**Charakter:** Bohatší na vzácné QER/RTF (df 2-4) — `QER` (Query-Encode-Retrieve), `RTF` (Retrieve-Transform-Fuse), `HNSW` (df 3), `RRF` (df 5) — protože P0 `BM25 IDF` preferuje vzácné. Proto MRR 0.5238 (+80%).

---

## 3. Sémantická dif analýza

| Dimenze | Via BASE | Via P0 | Dif |
|---------|----------|--------|-----|
| **Počet docs** | 18 | 17 | -1 (P0 přesnější, méně šumu `SQL_*`) |
| **Počet termů** | 25 | 65 | +40 (+160%) — P0 extrahoval `QER/RTF/HNSW/RRF` z `RETRIEVAL_*` docs, které BASE minul |
| **Společné** | 8 | 8 | `BM25`, `Embedding`, `RAG`, `MLOps`, `LLM`, `Vector Database`, `TF-IDF`, `MRR` — jádro ontologie |
| **Jen BASE (17)** | `100% determinismus`, `Archivace 9 souborů`, `Credentials`, `Data Pipeline (ETL)` — šum z `SQL_*` + `KORELACE` | — | `score=sum` najde časté `MLOps` (df 12) i v `SQL docs` |
| **Jen P0 (57)** | — | `QER`, `RTF`, `HNSW`, `RRF`, `MMR`, `Cross-encoder`, `Bi-encoder`, `ANN`, `NDCG`, `Latent space`, `Cosine Similarity` — vzácné, precizní | `BM25 IDF` vysoké pro df 2-4 |

**Sémantika:** BASE glosář je **širší, mělčí** (zahrnuje `Data Pipeline`, `Archivace` — ne ML/RAG/QER jádro) — vhodný pro `SQL` ontologii, ne pro `ML/RAG/QER`. P0 glosář je **užší, hlubší** (čistě `ML/RAG/QER` — `QER` 12 výskytů v `RETRIEVAL_BOTTLENECK`, `RTF` 8× v `MCP_ECOSYSTEM`) — vhodný pro genezi ML/RAG/QER artefaktu. To je `K2 Kontrakt` (query ambiguity) vs `K1 Detektor` (BM25 IDF).

**Token/rychlost:** Oba ~161-176 tok top5 (rozdíl <10%), P0 87% rychlejší po buildu (19 vs 150ms) — `inverted_index` O(1) vs scan O(N×L).

---

## 4. Doporučení — který glosář použít pro nový artefakt

- **Pro ML/RAG/QER ontologii (tento task):** `via P0` — 65 termů, obsahuje `QER/RTF/HNSW/RRF` (vzácné, pro artefakt klíčové), MRR +80%, `RETRIEVAL_RESEARCH.md Glossary` 8 termů je jádro, P0 přidává `QER/RTF` (nové).
- **Pro SQL/DB ontologii:** `via BASE` stačí (SQL df vysoké, `score=sum` OK) — viz `SQL_RETRIEVAL_DRY_RUN` kde P0 win jen +12.8%.

**Příště (I1-I4):** `ontology_test_queries.json` 7→25, `k=20` pro N=135 (místo 60), `czech light stemmer` pro `ontologie/ontologií`, `b=0.25` pro KB (dl variance).

*Artefakty: `GLOSSARY_ML_RAG_QER_via_BASE_v1.md` (25 termů, 18 docs) + `GLOSSARY_ML_RAG_QER_via_P0_v1.md` (65 termů, 17 docs) — oba v `ML_Ops_edukace/` (kopie z `TEMP/.../results/`), `benchmark_ontology_results.json`, `SEMANTIC_DIFF_ANALYSIS.md` — geneze via 2 nástroje prokázána.*
