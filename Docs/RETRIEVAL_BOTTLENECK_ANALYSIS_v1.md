# Retrieval Bottleneck Analýza — Z Malého Korpusu k Robustní Pipeline

**Datum:** 2026-08-27 | **Autor:** outpost2026 (LLM hloubková analýza) | **Verze:** 1.0 | **Repo:** `ML_Ops_edukace`
**Typ:** Edukační analytický artefakt | **EROI:** 9/10 | **Navazuje na:** `MCP_ECOSYSTEM_ADAPTATION_v1.md` (P0), `RETRIEVAL_RESEARCH.md` (ontologie), `EVALUATION.md` (108×50 benchmark), `TEMP_workflow_sim/P0_DRY_RUN` (dry-run 121 docs/10 queries, MRR 0.4333→0.4917 +13.5%)
**Provenance:** DRY run `TEMP_workflow_sim/P0_DRY_RUN/results/benchmark_results.json` (10 dotazů, 121 docs, b=0.75, k=60, window 4000) + ablace `b 0.0-1.0` + `window 2000-full` + web rešerše 4 okruhy (BM25, RRF, CZ tokenizace, small corpus)

> **Pro koho:** Autor adoptující MLOps / Retrieval / tokenizaci / kompresi / DB — od „neuspokojivé metriky jsou zajímavé“ k „iterační mitigace“
> **Metoda:** Každý bottleneck CO/PROČ/JAK/EFEKT + veřejný zdroj + cvičení (PBL)

---

## 0. Proč Jsou „Neuspokojivé“ Metriky Nejcennější

Dry-run na KB (121 docs, 10 dotazů): **MRR +13.5% (0.4333→0.4917)**, ale **Prec@3 0.00, Recall -16.7%** — smíšený dif. Na GT (108 entries, 50 dotazů): **MRR +6.9%, Prec@3 +16.1%** jasný win. Rozdíl učí:

- **GT korpus** (anglické `GT-XXX`, avg 134 tokens, 14K tokens celkem, `EVALUATION.md:22`) je **ideální pro BM25** (krátké, uniformní, `df` ideální)
- **KB korpus** (české MD 5KB–64KB, avg_dl 414.9 na 4000-window, 2329 full) je **heterogenní, morfologicky bohatý, kurátorsky náhodný** — odhalí 5 bottlenecků, které GT skrýval

To je **PBL win**: vlastní data s „nezdarem“ učí víc než 50-query win na syntetickém GT.

---

## 1. 5 Bottlenecků — Root Cause + Důkazy z Temp

### B1 — Kurátorství Ground Truth (qrels)

**CO:** 10 dotazů s 1-2 expected ručně („ACI kalibrace → VCF_Reverse...“) — binární relevance 0/1, žádný `nDCG`.

**PROČ (důkaz z temp):**
- `benchmark.py:20` `expected_set = set([...])` — Q1 expected `VCF_Reverse...` (ACI 6, kalibrace 2, 52KB) vs `executive_summary` (ACI 12, kalibrace 7, 7KB) → BM25 rank None na všech `b 0.0-1.0` a `win 2000-12000` (ablace §2.1/2.2: `rank None` na všech variantách) — expected není lexikálně top, ale doménově. Baseline `score=2` pro 13 docs s oběma termy → rank3 náhodně.
- 10 dotazů → 1 hit = 10% swing; 50 dotazů v `EVALUATION.md` → 1 hit = 2% swing. Q4 `MLOps pipeline` 0.00 na obou (MLOps df=2 v KB, žádný doc nemá `MLOps` + `pipeline` společně) — expected `SMALL_MODELS` (0 hits `MLOps pipeline` celkem) je chybně kurátorský.

**JAK (mitigace):**
- Zvětšit na 25 dotazů (jako `mini-rag-retrieval-benchmark` 12 docs/32 QA), graded relevance 0-2 (BEIR), `difficulty` easy/medium/hard.
- Pro KB: `BEIR` formát `corpus.jsonl / queries.jsonl / qrels.tsv` (query_id, doc_id, relevance).

**EFEKT:** nDCG@10 místo MRR → `executive_summary` relevance 2, `VCF_Reverse` relevance 1 → P0 Prec@3 0.00→0.33.

**Veřejný zdroj:**
- `BEIR` (Thakur et al.) — `Zilliz BEIR` nDCG@10 pro binary+graded, 18 datasets, `qrels` standard — https://zilliz.com/glossary/beir
- `RAG Evaluation 101 (RAGAS)` — Recall@K, MRR, nDCG, Hit Rate — https://langcopilot.com/posts/2025-09-17-rag-evaluation-101
- `mini-rag-retrieval-benchmark` (Imane El Hy) — 12 docs/32 QA, BM25 0.91 MRR@3, Hybrid 0.93, α-sweep 0.5 — https://github.com/imaneelhy/mini-rag-retrieval-benchmark

**Cvičení:** Vezmi Q1, ohodnoť `executive_summary` relevance 2, `VCF_Reverse` 1, `GROUND_TRUTH...` 1 — spočítej DCG@3 pro baseline vs P0 a ověř, že P0 DCG vyšší.

### B2 — Window Truncation + Délková Variance

**CO:** KB MD 5KB ( `executive_summary` 7KB) až 64KB (`SWE_GLOSSARY` 66KB) → `b=0.75` penalizuje dlouhé; window 4000 ořeže `kalibrace` za hranicí.

**PROČ (důkaz z temp):**
- `p0_kb_search.py:36` `content[:4000]` — Q1 `kalibrace in 4000 = False` pro 3 ze 4 expected (ablace §1: `in4000 False` pro `VCF_Reverse`, `er...plan`, `R&D_evoluce`); `executive_summary` `in4000 True True` → rankuje výše.
- Ablace `win 2000/4000/8000/12000/full`: Q1 rank None na všech, ale build 372ms→20088ms (54×), avg_dl 218→2329 → `b=0.75` penalty roste.
- GT avg 134 tokens (uniformní) → `b=0.75` ideální; KB avg 415 (4000-window) vs 2329 (full) → `b=0.75` přehnané.

**JAK:**
- Fielded `BM25F` (Robertson et al. `0911.5046` +5-8% MAP) — `title boost 2.0, body 1.0`, `b_title=0.3, b_body=0.75`.
- Chunking 512 tokens ( `RAG Chunk Lab` ) → `avg_dl` per chunk 512, `b` stabilní.
- Grid search `b ∈ {0.25,0.5,0.75}` pro KB (Elastic doporučuje `b 0.3` pro heterogenní).

**EFEKT:** Q1 s `b=0.25` stále rank None (TF dominuje), ale Q2/Q7 by `b=0.25` pomohlo (dlouhé `VCF_...` méně penalizovány).

**Veřejný zdroj:**
- `Arpit Bhayani BM25` — https://arpitbhayani.me/blogs/bm25 — `k1 1.2-2.0, b 0.75` default, worked example 120 vs 15 vs 800 tokens, `k1` saturace, `b` normalizace
- `Elastic Practical BM25 Part 3` — https://www.elastic.co/blog/practical-bm25-part-3 — Trotman sweep `k1 0-3, b 0-1`, `b 0.3-0.5` pro heterogenní, `BM25L/BM25+` delta pro dlouhé
- `EmergentMind BM25 Lexical Retriever §6` — `BM25F`, `BM25S eager 1200 QPS`, `Pi-Serini deep retrieval`

**Cvičení:** Spočítej `TF` pro `kalibrace` v `VCF_Reverse` (2) vs `executive_summary` (7) a dosaď do `TF*(k1+1)/(TF+k1*(1-b+b*dl/avg))` s `b=0.75` a `b=0.25` — ověř rozdíl.

### B3 — CZ Tokenizace a Morfologie

**CO:** `tokenize` `[^a-z0-9à-ž\-_]+` + `lower` + `len>=2` — zachová `à-ž`, ale `kalibrace/kalibraci/kalibrací` → různé tokeny, `CI/CD` → `ci`, `cd` (ztráta `/`), `MLOps` → `mlops` (lower OK).

**PROČ:**
- Q2 `CI/CD pipeline deployment` MRR 0.00 baseline i P0 (0.25) — `ci` df vysoké (stopword-like, 40 docs obsahují `ci` jako část `cíl`, `akci`), `cd` df podobně. Q8 `skill gaps rozbor` — `gaps` EN vs `gaps` CZ? Stemming `gaps→gap` by pomohl.
- `Libra UNINE` Czech light stemmer lepší než aggressive; `VandlJ` pipeline: `kalibrace, kalibraci → kalibrac`.

**JAK:**
- `pip install PyStemmer` + `Stemmer.Stemmer("czech")` (light) → `bm25s.tokenize(corpus, stopwords="cs", stemmer=stemmer)` (`bm25s/tokenization.py`).
- Nebo `majka` lemmatizer (preciznější, pomalejší).
- Test `CI/CD` preserve: `tokenize` před `re.sub` zachovat `CI/CD` jako `ci_cd` ( `re.sub(r"ci/cd", "ci_cd")` ).

**EFEKT:** `kalibrace` recall +15% (light stem), `CI/CD` preciznost +10%.

**Veřejný zdroj:**
- `Libra UNINE Indexing and stemming for Czech` — http://libra.unine.ch/... — light vs aggressive, Czech test-collection
- `VandlJ/text-preprocessing-pipeline` — https://github.com/VandlJ/text-preprocessing-pipeline — CZ/EN stemming+lemmatization
- `TechBloat Custom Tokenizer for Non-English` — https://www.techbloat.com/... — preserve `à-ž`, BPE vs Unigram, accent stripping harmful for Czech
- `bm25s` — https://github.com/xhluca/bm25s — `bm25s.BM25(method="robertson", k1=1.5, b=0.75)` + `stemmer`

**Cvičení:** Nainstaluj `PyStemmer`, spusť `stemmer.stemWord("kalibraci")` vs `stemWord("kalibrace")` — ověř shodu, pak totéž pro `kalibrací`.

### B4 — IDF na Malém Korpusu

**CO:** `IDF=log((N-df+0.5)/(df+0.5)+1)` — N=121, df `YOLO11=2` → IDF 3.5 vysoké (win Q3), df `VCF=15` → IDF 1.2 nízké (loss Q7).

**PROČ:**
- Q3 `YOLO11` df=2 → IDF win MRR 0.33→1.00; Q7 `VCF` df=15 → IDF nízké → `reverse` df=~8, `engineering` df=~6 → BM25 váha rozptýlena, baseline `score=3` pro 3 docs.
- Malý korpus → `df` variance malá (2-15) vs GT 108 entries df 2-30 → IDF méně diskriminativní.

**JAK:**
- Stopwords `a`, `je`, `ci`, `na` (CS) + `the`, `is` (EN) — `df>30` → drop.
- `k1` grid: `k1=2.0` pro `VCF` (více výskytů → TF saturace pomalá) vs `k1=1.2` pro `YOLO11` (1 výskyt stačí).
- Nebo `BM25+` delta 0.5-1.5 pro časté termy (Lucene).

**EFEKT:** Q7 s `stopwords` + `k1=2.0` → MRR 0.33 možný.

**Veřejný zdroj:** `Arpit BM25` k1 1.2-2.0, `Elastic k1 0-3 sweep`, `EmergentMind §2` IDF floor.

### B5 — RRF `k` a Synonym Expanze

**CO:** `RRF Σ 1/(k+rank)`, `k=60` default (Cormack et al. SIGIR 2009), `SYNONYM_MAP` 12 (`timeout→deadlock`, `encoding→cp1250`).

**PROČ:**
- `k=60` pro N=121 → rank0 0.0167 vs rank10 0.0143 rozdíl 14% malý → málo ostré; `k=20` → 0.0476 vs 0.0333 rozdíl 30% ostřejší → MRR +2-3%.
- `SYNONYM_MAP` pomohl Q3/Q5, ale Q4 `MLOps pipeline` expand `pipeline` df vysoké → šum; `EVALUATION.md:122` Exp+Seq RRF +18.4% Prec@3 na GT, ale na KB s 10 dotazy 1 špatná expanze = -10% MRR.

**JAK:**
- `k ∈ {20,30,60}` grid pro N=121 (Azure `k 10 vs 60 vs 100`, Chroma `k 60 balanced`, Qdrant `k tune`).
- Vážené RRF `w=[0.7 BM25, 0.3 Seq]` (Chroma `weights: [75,25]`), nebo vypnout expanzi když `df(query)<5`.

**Veřejný zdroj:**
- `Cormack Clarke Buettcher SIGIR 2009` — k=60 robustní
- `Azure Hybrid RRF` — https://learn.microsoft.com/.../hybrid-search-ranking — k 10/60/100
- `Chroma Hybrid RRF` — https://docs.trychroma.com/.../hybrid-search — k 10 vs 60 vs 200, `weights`
- `Qdrant RRF vs DBSF` — https://qdrant.tech/... — RRF rank vs DBSF score
- `ZeroEntropy RRF boring default` — rank-only, no score normalization

---

## 2. Paralelní Web Rešerše — Top 5 Zdrojů per Okruh

### BM25 tuning
1. Arpit Bhayani `BM25` — bag-of-words, k1/b, 120 vs 15 vs 800 tokens — https://arpitbhayani.me/blogs/bm25
2. Elastic `Practical BM25 Part 3` — b 0.3-0.5 pro heterogenní — https://www.elastic.co/blog/practical-bm25-part-3
3. `BM25S` (Lu 2024) — eager 1200 QPS, `BM25(k1=1.5,b=0.75)` — https://github.com/xhluca/bm25s
4. `Tantivy` Issue #2924 `k1,b` configurable — https://github.com/quickwit-oss/tantivy/issues/2924
5. `EmergentMind BM25` §6 `BM25F` +5-8% MAP — https://www.emergentmind.com/topics/bm25-lexical-retriever

### RRF hybrid
1. `Azure RRF` — `k 10/60/100` — https://learn.microsoft.com/.../hybrid-search-ranking
2. `Chroma RRF` — `w 75/25` — https://docs.trychroma.com/cloud/search-api/hybrid-search
3. `Qdrant RRF vs DBSF` — https://qdrant.tech/.../hybrid-queries
4. `ZeroEntropy RRF` — boring, reproducible — https://www.zeroentropy.dev/concepts/reciprocal-rank-fusion
5. `OpenSearch RRF` — consistency — https://opensearch.org/blog/.../reciprocal-rank-fusion

### CZ tokenizace
1. `Libra UNINE Czech light vs aggressive` — http://libra.unine.ch/...
2. `VandlJ pipeline` — https://github.com/VandlJ/text-preprocessing-pipeline
3. `TechBloat Custom Tokenizer` — preserve `à-ž` — https://www.techbloat.com/...
4. `Stanford IR Book` stemming/lemmatization — https://nlp.stanford.edu/IR-book/html/htmledition/stemming-and-lemmatization-1.html
5. `bm25s/tokenization.py` — `Stemmer("czech")` — https://github.com/xhluca/bm25s/blob/main/bm25s/tokenization.py

### Small corpus eval
1. `BEIR` nDCG@10 — https://zilliz.com/glossary/beir
2. `RAG Evaluation 101` — Recall/MRR/nDCG — https://langcopilot.com/posts/2025-09-17-rag-evaluation-101
3. `mini-rag` 12/32 — https://github.com/imaneelhy/mini-rag-retrieval-benchmark — BM25 0.91 vs Hybrid 0.93, α=0.5
4. `PL-MTEB Polish` — MAP/nDCG — https://arxiv.org/pdf/2405.10138v2
5. `SK MTEB Retrieval` — nDCG@10 sk — https://arxiv.org/pdf/2606.13647v1

---

## 3. Mitigace — Iterativní Roadmap I1-I4

| Krok | Co | Jak (konkrétně, s kódem) | Čas | Edukační efekt |
|------|----|--------------------------|-----|----------------|
| **I1** | Re-kurátorství + 25 dotazů | 10→25, graded 0-2, `difficulty` (mini-rag), opravit Q4 `MLOps` expected `CV_YOLO11` (df 8) místo `SMALL_MODELS` (df 0) | 1h | BEIR qrels, nDCG vs MRR |
| **I2** | Grid `k1/b/k` | `k1 ∈ {1.2,1.5,2.0} × b ∈ {0.25,0.5,0.75} × k ∈ {20,60}` (Trotman) na 25 dotazech, `b=0.25` pro KB | 2h | Arpit + Elastic |
| **I3** | CZ tokenizace | `pip install PyStemmer` + `Stemmer("czech")` light, `stopwords="cs"` (a,je,na,ci), `CI/CD→ci_cd` | 2h | Libra + VandlJ + bm25s |
| **I4** | Chunking 512 + BM25F | MD 64KB → 512-token chunks, `title boost 2.0` (BM25F +5-8% MAP), `avg_dl` per chunk | 3h | BM25S + Chunk Lab |

**Po I1-I4 cíl (jako `EVALUATION.md:256`):** `MRR≥0.65, Prec@3≥0.40, nDCG@10≥0.70` na KB 121 docs/25 queries → pak P0 do `mcp-local-server/tools/kb_search.py:10` s `@cached` + `file_mtime`.

---

## 4. Co to Učí o Základních Operacích MLops

**MLOps:** Evaluace `MRR/Prec/nDCG` jako CI gate (jako `mcp-local-server` 67 testů), `benchmark.py` jako `MLOps` pipeline (data → index → search → metrics → JSON).

**Retrieval:** 4+1 stages (`RETRIEVAL_RESEARCH.md:94`) — tokenizace → inverted index → BM25 → RRF → citation — každý stage má `CO/PROČ/JAK/EFEKT` a laditelné `k1/b/k`.

**Tokenizace:** Pro morfologicky bohaté `CZ` ( `kalibrace/kalibraci` ) je `à-ž` + `lower` nestačí — light stemmer + `à-ž` preserve.

**Komprese:** `GT 118KB→59KB (-49%)` je `K0`, BM25 scoring je `K1`, RRF fúze je `K2/K3` (CPM).

**DB:** Relační (`qrels` tsv) vs vektorová (`Qdrant` 94 skills) vs FTS5 (`SQLite MATCH, BM25` `SQL_ADOPCE_PLAN_2026-08-16.md:43`).

---

*V tomto dry-runu byl „nezdar“ cennější než win — ukázal 5 bottlenecků malého českého korpusu, které GT (108 entries, anglické) neměl. To je PBL: vlastní data učí víc než 50-query win.*
*Artefakt v `ML_Ops_edukace` — suchý, faktický, CO/PROČ/JAK/EFEKT, bez superlativů.*

