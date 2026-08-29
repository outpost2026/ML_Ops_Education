# P0 Improvement Proposal — Syntéza 3 Testů

**Datum:** 2026-08-27 | **Autor:** outpost2026 | **Verze:** 1.0 | **Status:** Návrh (build mode)
**Východisko:** 3 dry-runy v `TEMP_workflow_sim` (P0 = `BM25(k1=1.5,b=0.75)+Seq+RRF(k=60)` window 4000) vs `BASE = score=sum 1 if w in text` (`mcp-local-server/tools/kb_search.py:38`)

---

## 1. Souhrn 3 Testů — ML metriky + tokeny + rychlost

| Test | Korpus | Dotazů | BASE MRR → P0 MRR | Prec@3 | Recall | Hits | ms/q BASE→P0 | Tok top5 | Verdikt |
|------|--------|--------|-------------------|--------|--------|------|--------------|----------|---------|
| **1. P0_DRY_RUN** (KB generický) | 121 docs (106 MD+15 JSON, 4000w, avg 415) | 10 (ACI, CI/CD, YOLO, MLOps, timeout, encoding, VCF RE...) | **0.4333→0.4917 +13.5%** (full -1.9%) | 0.2667→0.2667 0% | 0.6000→0.5000 -16.7% | 8/10→7/10 | 168→17ms (-89%) | 176→161 | **Smíšený** — P0 win na `YOLO`/`timeout`/`skill gaps` (+0.5 MRR), loss na `ACI`/`VCF RE` (rank None) |
| **2. SQL_RETRIEVAL** | 127 docs (KB 121 + MCP-Jobs 6) | 7 (SQL Q0-Q6, 1 original +2 agent +4 QER) | **0.6905→0.7786 +12.8%** | **0.4762→0.5238 +10%** | **0.4643→0.7262 +56%** | 6/7→7/7 | 168→17ms | 176→161 | **P0 win** — `SQL` df4 + `FTS5` df2 IDF vysoké |
| **3. ONTOLOGY_GLOSSARY** | 135 docs (KB 121 + ML_Ops 8 + mcp-retrieval 6) | 7 (ML RAG QER ontologie) | **0.2905→0.5238 +80%** | **0.1429→0.3810 +166%** | **0.3333→0.5714 +71%** | 6/7→6/7 | 150→19ms | 176→161 | **P0 win silný** — `QER` df3 `RTF` df2 vzácné → IDF |
| **VIBECODING** (bonus, 4. test) | 121 docs | 7 (vibecoding df4) | 0.7857→0.4286 -45% | 0.5714→0.3333 -41% | 0.7143→0.3333 -53% | 6/7→3/7 | 168→17ms | — | **BASE win** — single rare `vibecoding` substring stačí, P0 Seq šum |

**Tokenová komprese (všechny):** Bez retrieval `678493 tok (2.7MB)` → s top5 `~170 tok` → **3848x/4211x (91%)** jako `EVALUATION.md:6.2` (oba stejně).

**Pattern:** P0 vyhrává na **vzácných, víceslovných, QER/RTF** (df 2-5, 2-4 slova) kde `BM25 IDF` + `RRF` rankuje přesně; prohrává na **single rare** (`vibecoding` df4, 1 slovo) kde `score=sum` stačí a `SeqMatcher` přidá šum, a na **dlouhých 52KB** docs kde `b=0.75` penalizuje + `window 4000` ořeže `kalibrace` za hranicí.

---

## 2. Root Cause — 5 Bottlenecků (ověřeno ablacemi)

| # | Bottleneck | Důkaz z 3 testů | Veřejný zdroj |
|---|------------|-----------------|---------------|
| **B1 Kurátorství** | 10 dotazů → 1 hit =10% swing; Q1 `ACI kalibrace` expected `VCF_Reverse` (ACI 6) vs `executive_summary` (ACI 12) → BM25 rank None na všech `b 0.0-1.0` + `win 2000-12000` (P0_DRY_RUN ablace) — expected není lexikálně top | BEIR nDCG@10 (Zilliz), `mini-rag` 12/32 |
| **B2 Window + délka** | `p0 window 4000` `kalibrace in 4000=False` pro 3 expected (P0_DRY_RUN §1), full avg 2329 build 20s vs 452ms, `b=0.75` penalizuje 64KB Glossaries → Q1 rank None | Elastic `b 0.3-0.5` pro heterogenní, `BM25F` +5-8% MAP (`0911.5046`), `Arpit` 120 vs 15 vs 800 tokens |
| **B3 CZ tokenizace** | `CI/CD → ci, cd` (stopword-like), `kalibrace/kalibraci` různé, `agentní→agentní` à-ž OK ale `df(agentní)=12` IDF nízké → Q3 `agentní práce` 0.00 oba | Libra UNINE light vs aggressive, `VandlJ`, `TechBloat à-ž`, `bm25s Stemmer("czech")` |
| **B4 IDF malý korpus** | N=121, `YOLO11` df2 IDF 3.5 win Q3, `VCF` df15 IDF 1.2 loss Q7; `vibecoding` df4 IDF 3.3 ale P0 miss kvůli Seq | `Arpit` k1 1.2-2.0, `EmergentMind` IDF floor |
| **B5 RRF k + synonym** | `k=60` pro N=121 málo ostré (rank0 0.0167 vs rank10 0.0143 14% dif) → `k=20` 30% dif lepší; `SYNONYM_MAP` `MLOps→pipeline` df vysoké → Q4 šum | Azure `k 10/60/100`, Chroma `w 75/25`, Qdrant RRF vs DBSF |

---

## 3. Návrh P0 v2 — 6 Mitigací (konkrétně, s kódem)

### P0 v2 Spec (vs v1)

| Param | v1 | **v2** | Proč |
|-------|----|--------|------|
| `k1` | 1.5 | **1.2** (pro KB) | GT 134 tok → 1.5, KB 415 tok → 1.2 (méně saturace, Arpit) |
| `b` | 0.75 | **0.25** | KB dl variance 5KB–64KB → `b 0.3` Elastic, `b 0.25` pro heterogenní (P0_DRY_RUN full -1.9% s 0.75) |
| `k` (RRF) | 60 | **20** | N=121-135 → `k=20` ostřejší 30% dif (Azure), `k=60` pro N>500 |
| `window` | 4000 | **8000 + chunk 512** | Q1 `kalibrace` za 4000 → 8000 nepomohlo, ale chunk 512 + `avg_dl` per chunk → B1 fix (BM25F) |
| `tokenize` | `[^a-z0-9à-ž\-_]+` | **+ `PyStemmer("czech")` light + `stopwords cs` + `CI/CD→ci_cd` preserve** | `kalibrace/kalibraci → kalibrac`, `ci` stopword |
| `SYNONYM` | 12 map vždy | **podmíněně `df<10`** | `MLOps` expand `pipeline` df vysoké → vypnout když `df>10` |
| `Seq` | vždy | **vypnout pro `df<5` single-term** | `vibecoding` df4 → Seq šum rank1 `AGENTS.md` |

**Kód P0 v2 (změny proti `p0_kb_search.py:16-44`):**

```python
# P0 v2 — diff
import Stemmer
stemmer = Stemmer.Stemmer("czech")  # light
STOP_CS = {"a","je","na","ci","se","ve","to","pro","od","do"}

def tokenize_v2(text):
    text = text.lower().replace("ci/cd","ci_cd")  # preserve
    text = re.sub(r"[^a-z0-9à-ž\-_]+", " ", text)
    toks = [t for t in text.split() if len(t)>=2 and t not in STOP_CS]
    return stemmer.stemWords(toks) if stemmer else toks  # kalibrace→kalibrac

# BM25 v2
bm25_v2 = BM25(k1=1.2, b=0.25).fit(docs_chunked)  # docs_chunked = chunk 512

# RRF v2
rrf_v2 = rrf_fusion([res_bm25, res_seq], k=20)  # bez expand pokud df>10
if df[query_term] < 10:
    res_exp = bm25_v2.search(expand_query(query), top_k=5)
    rrf_v2 = rrf_fusion([res_bm25, res_exp, res_seq], k=20)
else:
    rrf_v2 = rrf_fusion([res_bm25, res_seq], k=20)

# Seq vypnout pro single rare
if len(tokenize_v2(query))==1 and df.get(tokenize_v2(query)[0], 0) < 5:
    rrf_v2 = rrf_fusion([res_bm25], k=20)
```

### Mitigace per bottleneck

- **B1:** `ontology_test_queries.json` 7→25 dotazů, graded 0-2, `difficulty` (mini-rag), nDCG@10 (BEIR)
- **B2:** `chunk 512` + `BM25F title boost 2.0` (0911.5046) → `RETRIEVAL_RESEARCH.md:11` CLI playground `SELECT` analog
- **B3:** `PyStemmer czech` light (Libra) + `à-ž` preserve (TechBloat)
- **B4:** `k1=1.2` grid, `b=0.25` grid `b∈{0.25,0.5,0.75}` (Trotman), stopwords `ci`
- **B5:** `k=20` + `w=[0.7 BM25,0.3 Seq]` (Chroma), expand podmíněně

---

## 4. Očekávaný efekt P0 v2 (extrapolace z 3 testů)

| Test | v1 MRR → v2 (odhad) | Důvod |
|------|---------------------|-------|
| P0_DRY_RUN 10Q | 0.4917 → **0.60 (+22%)** | `b 0.25` + `chunk` fix Q1/Q7 (`ACI`/`VCF RE`) z 0.00→0.33, `k=20` + `Seq off` pro single rare |
| SQL 7Q | 0.7786 → **0.85 (+9%)** | `b 0.25` + `8000` window → `SQL FTS5` df2 → rank1 stabilní, `prec` +10% |
| Ontology 7Q | 0.5238 → **0.65 (+24%)** | `QER` df3 + `czech stem` `ontologie/ontologií` → `komprese` df 8 → MRR +24% (jako GT 0.7067) |
| Vibecoding 7Q | 0.4286 → **0.65 (+52%)** | `Seq off` pro `vibecoding` df4 → baseline win 0.7857 → P0 v2 0.65 (ne 0.42), `k=20` ostřejší |

**Token/rychlost:** `chunk 512` → `avg_dl` 512 (místo 414) → build 600ms (vs 452ms), query 15ms (vs 17ms) — stále 87% rychlejší než baseline 150ms, tok 161→155 (-4%).

---

## 5. Implementační kroky (8h, I1-I4)

| Krok | Co | Soubor | Čas | Metrika |
|------|----|--------|-----|---------|
| **I1** | Re-kurátorství 25Q + nDCG | `ontology_test_queries.json` 7→25, `vibecoding_test_queries.json` 7→25 | 1h | nDCG@10 ≥0.70 |
| **I2** | Grid `k1/b/k` | `p0_ontology_search.py:47` `BM25(k1=1.2,b=0.25)` + `rrf_fusion(k=20)` | 2h | MRR +20% |
| **I3** | CZ stemmer | `tokenize_v2` + `PyStemmer` + `STOP_CS` | 2h | `kalibrace` recall +15% |
| **I4** | Chunk 512 + BM25F | `content[:4000]` → `chunk 512` + `title boost` | 3h | `ACI` rank None→3 |

**Po I1-I4:** P0 v2 do `mcp-local-server/tools/kb_search.py:10` s `@cached` + `file_mtime` (P0 z `MCP_ECOSYSTEM_ADAPTATION_v1.md:6`), `TEMP` suchý běh zůstane jako `BEGIN;...ROLLBACK;`.

---

## 6. Doporučení — kdy P0 v1 vs v2

- **Dnes (P0 v1):** Pro **SQL/Ontology** (vzácné `QER/FTS5` df 2-4) nasaď P0 v1 s `MCP-Jobs/docs` rozšířením — win +12% / +80% prokázán. Pro **vibecoding single rare** a **KB generický 10Q** zůstaň na baseline.
- **Po I1-I4 (P0 v2):** Pro **všechny 3** — `b 0.25` + `k 20` + `czech stem` + `chunk` + `Seq off` → MRR ≥0.60 na všech.

*Syntéza 3 testů: P0 v1 je hybrid pro vzácné víceslovné QER, P0 v2 je robustní pro malý český heterogenní korpus 121-135 docs — cesta z `score=sum` (substring) k `BM25F+RRF` (IDF+rank).*
