# Glossary — ML/RAG/QER Ontologie v2 (hSNR, kurátorováno)

**Datum:** 2026-08-28 | **Autor:** outpost2026 | **Verze:** 2.0 (hSNR) | **Repo:** `ML_Ops_edukace`
**Typ:** Kurátorovaný glosář | **EROI:** 9/10 | **Status:** Kanon — náhrada raw `via_BASE` (25 termů, šum `Archivace`) + `via_P0` (65 termů, duplikace `0 Cache`)
**Provenance:** Syntéza `RETRIEVAL_RESEARCH.md:8` (8 termů), `MCP_ECOSYSTEM_ADAPTATION_v1.md:5` (4+1 pipeline), `RETRIEVAL_BOTTLENECK_ANALYSIS_v1.md` (B1-B5), `LLM_EDGE_CASE_RETRIEVAL_ANALOGIES` (2026-09-01, `NC` `IR-001`–`IR-004`), `EVALUATION.md:41` (MRR 0.7067), `TEMP/.../ONTOLOGY_GLOSSARY_DRY_RUN` (135 docs, 7 queries)
**Metoda:** `hSNR` = high signal-to-noise — pouze termy s `df 2-50` v `_github` + `MRR` dopad ≥1% v `EVALUATION` + `PBL` vysvětlitelnost bez LLM. Raw `via_BASE/P0` byly `2 kaskády retrieval pipeline` (substring vs BM25+RRF) — tento `v2` je jejich destilace (21 termů, 0 balastu).

> **Jak číst (Feynman):** Každý term `CO` (definice) → `PROČ` (problém) → `JAK` (vzorec/kód) → `EFEKT` (MRR/Prec). `hSNR` = `signál/(signál+šum)` — glosář obsahuje jen termy, které zlepšily `MRR` nebo `NC`.

---

## 1. Retrieval Jádro (sparse + dense + fúze)

| Term | Česky | CO | PROČ | JAK (vzorec/kód) | EFEKT (důkaz) |
|------|-------|----|------|------------------|---------------|
| **BM25** | Nejlepších 25 | Probabilistický `TF*IDF` s `length_norm` — `score = IDF * TF*(k1+1)/(TF+k1*(1-b+b*dl/avg))` | `TF-IDF` selhává na dlouhých docs (64KB Glossaries penalizace) | `retrieval.py:73` `k1=1.5 b=0.75` (v2 `k1=1.2 b=0.25` pro KB) | `MRR 0.6397` baseline, `P0` s BM25 `0.4917` window4000 |
| **TF-IDF** | Četnost–inverzní frekvence | `TF=log(N/df)` váha vzácného `timeout` df 5 vs `a` df 108 | Bez IDF `a` = `deadlock` (B4) | `Counter` + `math.log((N-df+0.5)/(df+0.5)+1)` | `IDF(YOLO11 df2)=3.5` win Q3 0.33→1.00 |
| **RRF** | Reciproká fúze ranků | `score=Σ 1/(k+rank)` — rank-based, scale-invariant, `k=60` default (Cormack 2009) | `Weighted α` preferuje dominantní zdroj (0.6532 vs 0.7067 +8.2%) | `retrieval.py:136` `k=60` (v2 `k=20` pro N=121) | `RRF 0.7067` vs `Weighted 0.6532` +8.2% (K3) |
| **Inverted Index** | Invertovaný index | `term → [(doc_id, tf)]` dict, ` Posting List` | O(1) lookup vs scan 121 docs 168ms→17ms | `BM25.fit` `inv[term].append((i,tf))` | Build 452ms once, 17ms/query |
| **QER** | Query-Encode-Retrieve | `Query → tokenize à-ž → BM25 → RRF` — inferuje `ontologie→POSTGRESQL_ontologie` | `QER` df3 vzácné → `BM25 IDF` win `MRR +80%` na ontologii | `p0_ontology_search.py:47` `tokenize` `[^a-z0-9à-ž\-_]+` | `ONTO_Q1` MRR 0.00→1.00 |
| **RTF** | Retrieve-Transform-Fuse | `Retrieve → Transform (window/chunk) → Fuse (RRF)` — `FTS5 BM25 MATCH` pro S2 | `RTF` `FTS5` df2 → `SQL_ADOPCE` rank1 | `MCP_ECOSYSTEM:5` 4+1 pipeline + `window 4000` | `SQL FTS5` MRR 1.00 |

## 2. Dense + Vektor

| Term | Česky | CO | PROČ | JAK | EFEKT |
|------|-------|----|------|-----|-------|
| **Embedding** | Vektorová reprezentace | `K-dim` vektor sémantiky — `timeout` ≈ `deadlock` | `GloVe OOV 44.9%` na `GT-001/P9` → `MRR 0.2607` selhal | `Word2Vec` `vector_size 100` (`d1_word2vec:145`) vs `TF-IDF` 2K-D | `GloVe` 0.26 vs `BM25` 0.63 — dense selhává na malém korpusu |
| **Vector Database** | Vektorová DB | `Qdrant/Weaviate` pro `ANN` `cosine` | `121 docs` brute-force stačí, `1M` → `HNSW` | `Qdrant RRF vs DBSF` | `vector_db` weight 0.45 `MCP-Jobs` |
| **HNSW** | Hierarchický malý svět | `FAISS` graf `vrstva hrubý→detailní` | `ANN` O(log n) vs O(n) | `FAISS` `IndexFlatIP` vs `HNSW` | `HNSW` až pro >1M, 121 docs `Flat` |
| **Cosine Similarity** | Kosinusová podobnost | `cos=(A·B)/(‖A‖‖B‖)` 1=identické | Dense `q_vec @ doc_vec` | `numpy.dot` po L2 | `Word2Vec` `doc_vectors @ q_vec` `0.31 MRR` |
| **ANN** | Přibližní sousedé | `HNSW`/`FAISS` rychlé, nepřesné | `Flat` přesný 17ms/query pro 121 | `FAISS` | `ANN` až pro >10K |

## 3. Evaluace

| Term | Česky | CO | Vzorec | PBL příklad | EFEKT |
|------|-------|----|--------|-------------|-------|
| **MRR** | Střední inverzní rank | `mean(1/rank_prvního)` | `rank1→1.0, rank2→0.5` | `YOLO11` rank3→rank1 `0.33→1.00` | `MRR 0.7067` vítěz |
| **Precision@K** | Přesnost na K | `relevant/K` | `3/3=1.00` | `ONTO_Q2` `Prec 0.1429→0.381 +166%` | `Prec@3` 0.6733 |
| **Recall** | Pokrytí | `relevant/celkem` | `2/3=0.66` | `SQL` `0.4643→0.7262 +56%` | `Recall` 0.6883 |
| **NDCG** | Diskontovaný zisk | `DCG/IDCG` `log` discount | `rank1` weight 1, `rank3` 0.5 | `BEIR` nDCG@10 graded | `nDCG` pro `QER` (graded 0-2) |
| **Hit Rate** | Zásah | `hits/total` | `43/50=0.86` | `Hits` 43/50 P0 | `Hit Rate` 0.86 |
| **NC** | Numerická konzistence | `1-abs(gt-pred)/max(gt,1e-6)` | `144M vs 156M → 0.92` | `LLM_EDGE_CASE IR-004` `NC≥0.99` | `NC 1.0` pro `tool calling` (IR-001) |

## 4. MLOps

| Term | Česky | CO | PROČ | JAK | EFEKT |
|------|-------|----|------|-----|-------|
| **MLOps** | ML operace | `data→fit→search→RRF→eval→tune` pipeline | `EVALUATION` 8 kroků 0B, `TEMP` 4 dry-runy | `benchmark_full.py` + `P0_DRY_RUN` | `MLOps` weight 0.50 `MCP-Jobs` |
| **RAG** | Retrieval-Augmented Generation | `LLM + externí znalosti` → méně halucinací | `LLM` `MRR ~0.7` ale `NC<0.5` (RF kolaps) → `RAG` + `NC` `1.0` | `RAG` `IR-001` tool calling | `RAG` 0.50 `IT_SKILL` |
| **QER** (nový) | Query-Encode-Retrieve | Inferuje `SQL→SQL ontologie` (P0 QER) | `SQL` df4 → `QER` df3 `MRR +80%` | `ontology_test_queries.json` 7Q | `QER` df3 vzácné |
| **RTF** (nový) | Retrieve-Transform-Fuse | `FTS5 BM25` pro `S2` | `window`/`chunk` transform | `window 4000` `kalibrace in 4000=False` | `RTF` `b 0.25` |

---

## Zdroj vs Balast (proč `v2` je `hSNR`)

| `v2` hSNR (21 termů) | `via_BASE` balast (odstraněno 17) | `via_P0` balast (odstraněno 57) | Důvod |
|----------------------|-----------------------------------|--------------------------------|-------|
| `BM25, RRF, QER, RTF, HNSW, NC` (vzácné df 2-4, `MRR` +8-80%) | `100% determinismus`, `Archivace 9 souborů`, `Credentials`, `Data Pipeline (ETL)` (šum `|` řádky, ne glossary) | `0 Cache, 1 BM25, 2 Fuzzy` (duplikace `via_P0` 65 `0 Cache` řádky) | `hSNR = signál/(signál+šum)` — `via_*` byly raw `2 kaskády` (substring vs BM25+RRF), `v2` je destilace `RETRIEVAL_RESEARCH:8` 8 termů + `P0` 13 termů |

**Provenance:** `v2` je `single source` 21 termů, `via_BASE/P0` archivovány jako `_ARCHIVE` (jako `KB/_ARCHIVE`), `v2` je kanon 21 (jako `BEIR` nDCG@10).

*Kurátorováno 2026-08-28 — `hSNR` = high signal-to-noise, 21 termů s `MRR` dopadem, 0 balastu.*
