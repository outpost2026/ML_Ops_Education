# MCP Ecosystem Adaptation: From Naive Search to Hybrid Retrieval

**Datum:** 2026-08-27 | **Autor:** outpost2026 | **Verze:** 1.0 | **Repo:** `ML_Ops_edukace`
**Typ:** Edukační syntetický artefakt | **EROI:** 9/10 | **Status:** Nový — syntéza originálních POC + prospektivní výzkum
**Navazuje na:** `RETRIEVAL_RESEARCH.md` (ontologie + 4-stupňová pipeline), `EVALUATION.md` (108 entries benchmark), `retrieve.py` (CLI), `mcp-retrieval` (produkční MCP), `mcp-local-server` (cnc-tools)

> **Jak číst tento dokument (PBL + CO/PROČ/JAK/EFEKT):**
> Každá sekce vysvětluje **CO** je mechanismus, **PROČ** vznikl, **JAK** funguje uvnitř a **EFEKT** na reálný dev workflow autora v `opencode`. Cíl není opsat návod, ale pochopit vztahy: proč `score = sum(1 if w in text)` selhává na `GT-001` vs `P9`, proč `RRF(k=60)` je scale-invariant, proč `44.9% OOV` zabíjí GloVe. Na konci každé kapitoly je cvičení.

---

## 0. Executive Summary

MCP ekosystém autora v `opencode` (`opencode.jsonc:49-79` — 5 lokálních serverů, 42 nástrojů, 22 git rep) používá dvě generace vyhledávání nad lokálními zdroji:

- **Generace 0 — naivní:** `mcp-local-server/src/mcp_local_server/tools/kb_search.py:38` `score = sum(1 for w in words if w in content_lower)` — O(N) scan 110 MD, bez IDF/length norm, bez fúze. Funguje na `ACI kalibrace`, selhává na `timeout MCP server` (polysémie + CZ/EN).
- **Generace 1 — hybridní:** `mcp-retrieval/src/mcp_retrieval/retrieval.py:27-141` + `ML_Ops_edukace/retrieve.py:120` — **BM25(k1=1.5,b=0.75) + SequenceMatcher + RRF(k=60) + SYNONYM_MAP(12)** — ověřeno na 108 GT entries × 25 queries: **MRR 0.7067 (+6.9%), Prec@3 0.6733 (+16.1%), 43/50 hits vs 38/50 baseline** (`EVALUATION.md:37`).

Tento artefakt syntetizuje originální POC do přenositelného blueprintu a zkoumá **všechny varianty integrace** nové pipeline do ostatních MCP nástrojů — od drop-in náhrady až po sdílený core. Zachovává edukační charakter: každý termín je ontologie, ne slovník.

**Klíčové zjištění rešerše (2026-08-27, `git grep -i -E` 22 rep, 408 hits v `ML_Ops_edukace`):** Jediné dedikované MLOps/retrieval jsou `ML_Ops_edukace` (edukační POC, 42 files) a `mcp-retrieval` (produkční MCP, 12 files, 30 testů). Ostatních 20 rep obsahuje jen nahodilé zmínky (`RAG`, `embedding`) — žádná pipeline. `B2B-Knowledge-Base` (403 hits) má fragmenty (`SWE_GLOSSARY` kap.13/18/19, `YOLO11_GARDEN` glossář), ale žádný MLOps lifecycle.

---

## 1. Pedagogická východiska

### 1.1 PBL (Problem-Based Learning) — proč tento artefakt vznikl

Autor nečetl učebnici MLOps. Řešil konkrétní bolest: **„Agent neví, jestli bug už byl popsán v GT postmortemu → musí hledat ručně v 118KB markdownu“** (`mcp-retrieval/README.md:12-16`). Cestou narazil na pojmy, které se kryjí s `MCP-Jobs/src/mcp_jobs/skills_config.json:105-118` (94 skills, `embeddings 0.50`, `MLOps 0.50`, `RAG 0.50`). Tento artefakt je **vedlejší produkt řešení vlastního problému**, proto má vyšší retenci než abstraktní studium.

### 1.2 CO/PROČ/JAK/EFEKT (použito v celém dokumentu)

Převzato z `mcp-local-server/src/mcp_local_server/tools/kb_search.py:18` komentáře a `SWE_GLOSSARY_zive_v1.md:6`:
- **CO** — mechanismus bez marketingu (vzorec, datová struktura)
- **PROČ** — který ground-truth problém řeší (GT-XXX, P-rule)
- **JAK** — vnitřní kroky + analogie (knihovna, toaleta s lockem)
- **EFEKT** — měřitelný dopad (MRR, ms, bytes)

### 1.3 Cílová kompetence po přečtení

Čtenář (autor za 3 měsíce) dokáže: vysvětlit rozdíl `TF-IDF` vs `BM25` s length norm, odvodit `RRF = Σ 1/(k+rank)`, zdůvodnit proč `GloVe 44.9% OOV` selhalo na `GT-001/P9`, navrhnout integraci pro `tool_kb_search` i `tool_cross_repo_search` a zvolit variantu dle korpusu (<500 docs → BM25+Seq stačí).

---

## 2. Syntéza originálních artefaktů

### 2.1 `RETRIEVAL_RESEARCH.md` — ontologie + architektura

**Původ:** `ML_Ops_edukace/RETRIEVAL_RESEARCH.md:1-346` — 10 kapitol, 4-stupňová pipeline, 13 termínů, 4 implementační cesty (A 0B, B 580MB, C 50KB cloud, D 128MB GloVe), 8 kroků POC.

**Klíčové převzaté:**

| Sekce originálu | Syntéza pro tento artefakt |
|-----------------|---------------------------|
| §1.1 Sparse (`BM25`, `TF-IDF`, `Inverted Index`) `RETRIEVAL_RESEARCH.md:35-43` | `BM25 = TF * IDF * length_norm` — `TF` saturuje (`k1=1.5`), `IDF=log((N-df+0.5)/(df+0.5)+1)` penalizuje `a`, `je`; `Posting List` je základ `inverted_index` v `retrieval.py:42` |
| §1.2 Dense (`Embedding`, `Cosine`, `HNSW`, `ANN`) `RETRIEVAL_RESEARCH.md:46-54` | Dense nahrazen `SequenceMatcher` pro zero-download — trade-off: sémantika vs 0B; `HNSW` až pro >10K docs, pro 108 stačí `Flat` brute-force |
| §1.3 Hybrid (`RRF`, `MMR`, `Weighted`) `RETRIEVAL_RESEARCH.md:58-64` | `RRF(k=60)` 3 řádky `retrieval.py:136-141` — rank-based → scale-invariant (nezáleží na skóre BM25 vs Seq) |
| §2 Pipeline diagram `RETRIEVAL_RESEARCH.md:94-119` | Převzat jako Obr. 1 níže, rozšířen o 5. stage `Cache` pro MCP |
| §3 Cesty A-D `RETRIEVAL_RESEARCH.md:123-173` | Validováno v `EVALUATION.md:37` — A vítěz, D selhalo (OOV) |

**Co originál neřešil:** Integrace do `cnc-tools` (žádný `kb_search.py` audit), prospektivní využití pro `MCP-Jobs`/`lichess`.

### 2.2 `EVALUATION.md` — důkazy

**Původ:** `ML_Ops_edukace/EVALUATION.md:1-333` — plný benchmark 50 queries × 108 entries, 12 tabulek, 5 next steps.

**Převzaté metriky (Obr. 2):**

| Varianta | MRR | Recall | Prec@3 | Hits | Stav | Ponaučení pro adaptaci |
|----------|-----|--------|--------|------|------|------------------------|
| `SequenceMatcher` | 0.6613 | 0.6333 | 0.5800 | 38/50 | Baseline | Fuzzy stačí na překlepy, ale bez IDF |
| `BM25` | 0.6397 | 0.6617 | 0.5967 | 40/50 | +4.5% Recall | Keyword recall lepší, MRR horší |
| `BM25+Seq RRF` | **0.7067** | **0.6883** | 0.6733 | **43/50** | **Vítěz MRR** | **Fúze kompenzuje slabiny** |
| `Exp+Seq RRF` | 0.7067 | 0.6933 | **0.6867** | 43/50 | **Vítěz Prec@3** | Synonyma pomáhají jen v RRF |
| `GloVe` | 0.2607 | 0.3200 | 0.2700 | 20/50 | Selhalo 44.9% OOV | Pre-trained nezná `GT-001`, `P9`, `cnc-tools` |
| `SVD` | 0.5413 | 0.5867 | 0.5267 | 35/50 | Selhalo 56.4% variance | Agresivní dim. redukce na malém korpusu |
| `MMR λ=0.7` | 0.5987 | 0.6183 | 0.5467 | 37/50 | Zhoršuje | Diverzita až pro >500 docs |

**Klíčový poznatek pro adaptaci:** `Hybrid RRF trpí když jedna složka je slabá` (`EVALUATION.md:68`) — proto GloVe/Word2Vec nelze míchat bez vážení. Pro MCP ekosystém (110 MD, 94 skills, 17 chess patternů) platí: **BM25+Seq stačí, dense až při >1K docs**.

### 2.3 `retrieve.py` + `mcp-retrieval/retrieval.py` — referenční implementace

**Duplikát:** `ML_Ops_edukace/retrieve.py:27-141` a `mcp-retrieval/src/mcp_retrieval/retrieval.py:27-141` sdílejí 180 řádků (`BM25` class, `SYNONYM_MAP`, `expand_query`, `rrf_fusion`). Rozdíl: `retrieve.py` má CLI (`print_results`, `interactive_mode`), `mcp-retrieval` má `GTRetriever` class + `load()` + `stats()` + `FastMCP` wrapper (`server.py:22`).

**Převzaté building blocks:**
- `tokenize(text): re.sub(r"[^a-z0-9à-ž\-_]+"," ", lower).split()` — zachovává `à-ž` pro CZ (`retrieval.py:14`)
- `BM25.fit(documents)` — `df`, `inverted_index`, `avg_dl` (`retrieval.py:37-43`)
- `SYNONYM_MAP` 12 termů (`retrieval.py:78`) — `timeout→deadlock/zaseknuti`, `encoding→cp1250/utf-8` — CZ/EN most
- `build_searchable_text(entry)` — `symptom+root_cause+fix+server+tags+rule` (`retrieval.py:113`)

### 2.4 `mcp-local-server` — starý mechanismus

**Audit 2026-08-27:**

| Nástroj | Soubor | Dnes | Problém |
|---------|--------|------|---------|
| `tool_kb_search` | `kb_search.py:38,60` `score=sum(1 for w in words if w in content_lower)` | Per-query `rglob("*.md"+"*.json")` scan, `first_pos` snippet, `module` filtr, `@cached(ttl=300)` | Bez IDF → `a` == `deadlock`; bez length norm → dlouhé MD dominují; bez fúze → `MLOps` nenajde `ML Ops`; bez synonym → `timeout` ≠ `zaseknuti` |
| `tool_cross_repo_search` | `cross_repo_search.py:30` `git grep -i --line-number --heading` + `ThreadPool(4)` + `BLOCKED_DIRS={.venv}` | Paralelní grep 22 rep, `TIMEOUT_PER_REPO=15`, case-insensitive | Správně pro **code search** (definice `ALLOWED_ROOTS`), ale bez rank → 200 výsledků bez relevance; vhodný pro `tool_aci_lookup` (přesný termín), ne pro `proč padá VCF writer` |
| `tool_kb_read_doc` | `kb_read_doc.py:44` `INDEX.md` metadata lookup | `EREI` + `Typ/Účel` z tabulky | Žádný retrieval, jen čtení — kandidát pro `citation` stage |
| `tool_kb_overview/by_module` | `kb_overview.py:8`, `kb_by_module.py:9` | Agregace bez search | Neupgradovat — jen listing |

**Závěr syntézy:** Starý `kb_search` je **baseline pro KB docs** (110 MD, CZ/EN, 2K tokens/entry). Nový `GTRetriever` je **vítěz pro GT entries** (108 jsonl, doménové ID `GT-001`). Oba mají <500 docs → stejná optimalizace platí.

---

## 3. MCP Ekosystém — inventura 2026-08-27

> Zdroj: `opencode.jsonc:49-79`, `CONTEXT_REPOS.md:1-755`, `git ls-files` 22 rep, `opencode --version` + `mcp_audit.log`

```
opencode (plan agent, default)
├── cnc-tools      21 tools  FastMCP  mcp-local-server/.venv  timeout 60s   [KB+FS+git+VCF+RE]
├── mcp-retrieval   4 tools  FastMCP  mcp-retrieval/.venv     timeout 60s   [GT retrieval] ★ NOVÝ
├── mcp-jobs        5+1 prompt  FastMCP  MCP-Jobs/.venv       timeout 180s  [CZ job portals]
├── lichess-analyzer 8 tools FastMCP  lichess-analyzer/.venv timeout 300s  [Stockfish+patterns]
└── linkedin-analyzer 8 tools FastMCP  linkedin-mcp-custom/.venv timeout 120s [EROI scoring]

Non-MCP, ale souvisí: dxf_integrace (semantic embedding POC), rag_indexer (legacy), ML_Ops_edukace (POC repo)
```

### 3.1 Detail per-server (co by získalo z retrieval)

**`cnc-tools` (P0/P1 cíl):** `server.py:53` `FastMCP("cnc-tools")` — `ALLOWED_ROOTS=[_github]`, `FORBIDDEN_PATTERNS=.env/*.key` (`config.py:14`), 67 testů. Nástroje s fulltextem: `kb_search`, `cross_repo_search`, `kb_read_doc`. Ostatní (`vcf_*`, `git_*`, `aci_lookup`, `session_state`) jsou deterministické — neupgradovat.

**`mcp-retrieval` (referenční):** `server.py:22` `FastMCP("mcp-retrieval")`, `retrieval.py:27` `GTRetriever`, `data/gt_full.jsonl` 108 entries, `gt_rules.json` 85 P-rules. Již v `AGENTS.md §7` povinné `gt_search()` před bugfixem. **Není kandidát na upgrade, je zdroj.**

**`MCP-Jobs` (P2):** `src/mcp_jobs/skills_config.json:105-118` 94 skills, 146 aliasů, `scoring.weights` `domain 0.35/tech 0.25`, `domain_keywords` 3 vrstvy. `search_jobs_v2` dělá `category bulk scrape + boolean filter + location/salary` — keyword only, žádná sémantika. Kandidát na **rerank** pro `RAG/vector_db` dotazy (malý korpus 94 → BM25+synonym stačí).

**`lichess-analyzer` (P2):** `patterns/chess_pattern_v5.json` 17 patternů A-Q1 (65% implementováno), `src/services/pattern_detector.py` 11 detektorů, `GameAnalysis` ACPL/blunder. Retrieval je `pattern matching` (deterministický `SequenceMatcher` na PGN), ne docs — upgrade až po `cnc-tools`. Vzdálená analogie: `pattern library ≈ skill catalog`.

**`linkedin-analyzer` (ne):** `linkedin_mcp_custom` 8 tools, EROI 6 dimenzí, `25/25` testů. Vyhledávání je **scrape + EROI scoring**, ne retrieval — neupgradovat.

---

## 4. Gap Analýza — proč starý mechanismus nestačí

### 4.1 Kvantitativní (z `EVALUATION.md:41-95`)

- `kb_search.py:38` `score = počet slov` → `MRR 0.6613` baseline by na GT datasetu byl `~0.58` (odhad: bez IDF, bez fúze). Nový `0.7067` je **+21% relat.** proti starému.
- `cross_repo_search.py:30` vrací 200 výsledků seřazených dle `git grep` pořadí (lexikograficky dle repa), ne dle relevance → `opencode` agent musí číst 200× `read_file` → token waste `~200*1KB=200KB`.
- `BM25` bez `IDF` na KB (110 MD, průměr 600B) → term `a` (df=108) má stejnou váhu jako `deadlock` (df=3) → `score` šum.

### 4.2 Kvalitativní (PBL příklady)

| Dotaz autora (reálný z `opencode` historie) | Starý `kb_search` | Nový `GTRetriever` |
|-------------------------------------------|-------------------|---------------------|
| `timeout v MCP serveru` | `score 1` pro `MCP_GROUND_TRUTH_postmortem_agregovany_v2.md` (obsahuje `timeout`), `score 1` pro `SQL_ADOPCE_PLAN.md` (obsahuje `timeout` v jiném kontextu) — nerozliší | `BM25 IDF(timeout)=log((108-5+0.5)/(5+0.5))` vysoké, `SYNONYM_MAP[timeout]=deadlock` → `BM25(exp)` najde `GT-010 P25`, `RRF` fúze → `GT-010` top1 |
| `encoding problem Windows` | `score 2` pro `přehrada.md` (obsahuje `problem`), miss `cp1250` | `SYNONYM_MAP[encoding]=cp1250/utf-8` → `BM25(exp)` najde `GT-019`, `SeqMatcher` zachytí `Windows` |
| `MLOps pipeline` (CZ/EN) | `score 1` pro `MLOps` jen v `skills_config.json`, 0 pro `ML Ops` s mezerou | `tokenize` `à-ž` + `SYNONYM_MAP` + `build_searchable_text` s `tags` → `MLOps` i `ML operations` |

### 4.3 Kdy upgrade nepomůže (důležité pro edukační charakter)

- **Malý korpus + obecný pre-trained:** `GloVe 128MB` → `0.2607 MRR` (`EVALUATION.md:89`) — 44.9% OOV na `GT-001`, `P9`. Poučení: **pro <500 doménových docs nepoužívej obecný embedding, použij BM25+Seq**.
- **Diverzita na malém korpusu:** `MMR λ=0.7` → `0.5987` (`EVALUATION.md:126`) — diverzita zhoršuje. Pro KB (110) a jobs (94) platí: relevance > diverzita.
- **Code search:** `cross_repo_search` pro `ALLOWED_ROOTS` (`config.py:14`) je správně `git grep` — BM25 by zpomalil a `def`/`class` jsou přesné termíny. Upgrade jen pro **docs search**, ne pro `rg "def write"`.

---

## 5. Architektura — 4 (+1) stupňová pipeline pro MCP

```
                    ┌──────────────────────────────────────────────────────────┐
                    │   RETRIEVAL PIPELINE PRO MCP (4+1 stages)              │
                    │   Edukační verze — každá stage má CO/PROČ/JAK/EFEKT     │
                    └──────────────────────────────────────────────────────────┘

    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
    │  STAGE 0     │    │  STAGE 1     │    │  STAGE 2     │    │  STAGE 3     │    │  STAGE 4     │
    │  Cache       │    │  BM25        │    │  Fuzzy       │    │  RRF         │    │  Citation    │
    │  (in-memory) │    │  (sparse)    │    │  (SeqMatcher)│    │  (fusion)    │    │  (KB read)   │
    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
           │                   │                   │                   │                   │
           ▼                   ▼                   ▼                   ▼                   ▼
    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
    │ @cached      │    │ Inverted     │    │ Sequence     │    │ Σ 1/(60+r)   │    │ kb_read_doc  │
    │ ttl=300      │    │ Index        │    │ Ratio        │    │ rank-based   │    │ + INDEX.md   │
    │ + file mtime │    │ O(1) lookup  │    │ CZ/EN        │    │ scale-invar  │    │ metadata     │
    └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘

    Dotaz: "timeout MCP" ──→ [tokenize à-ž] ──→ BM25(orig) ──→ rank1 ──┐
    Dotaz: "timeout MCP" ──→ [expand timeout→deadlock] ──→ BM25(exp) ──→ rank2 ──┼──→ RRF ──→ top5 ──→ kb_read_doc(path) → LLM context
    Dotaz: "timeout MCP" ──→ [fuzzy] ──→ SeqMatcher ──→ rank3 ────────┘
                                                                                    │
                                                                                    └──→ citation: "Podle GT-010 (P25)..."
```

**CO/PROČ/JAK/EFEKT per stage (edukační):**

| Stage | CO | PROČ v MCP | JAK (kód) | EFEKT |
|-------|----|-----------|-----------|-------|
| **0 Cache** | `@cached(ttl_seconds=300)` (`kb_search.py:10`, `cache.py:8`) + `file_mtime` check | `rglob("*.md")` 110 souborů × `read_text` = 30ms/query → cache → 0ms | `BM25.fit()` once, `inverted_index` dict | 90% úspora na opakovaných dotazech v session |
| **1 BM25** | `TF * IDF * length_norm` (`retrieval.py:45-55`) `k1=1.5` saturuje TF, `b=0.75` normalizuje `dl/avg_dl` | `score = sum(1...)` nerozliší `a` vs `deadlock`; IDF ano | `Counter` + `math.log((N-df+0.5)/(df+0.5)+1)` | +4.5% Recall (`EVALUATION.md:48`) |
| **2 Fuzzy** | `SequenceMatcher(None,q,t[:300]).ratio()` (`retrieval.py:128`) | CZ/EN překlep `MLOps` vs `ML Ops`, `cp1250` vs `utf-8` | `max(keyword_score, seq_score)` | Zachytí 28 ties (`EVALUATION.md:57`) |
| **3 RRF** | `score=Σ 1/(60+rank)` (`retrieval.py:136`) | BM25 a Seq mají jiné škály (3.2 vs 0.87) — rank je invariantní | 3 řádky `defaultdict(float)` | **+6.9% MRR** (`EVALUATION.md:112`) |
| **4 Citation** | `kb_read_doc(path)` (`kb_read_doc.py:10`) + `INDEX.md` metadata | LLM bez citace halucinuje `GT-XXX` (incident §6 `DATA-FABRICATION-001`) | `AGENTS.md §7` povinné `gt_search` → `gt_get_entry` | Backpropagation `P-rule` do `opencode` odpovědi |

---

## 6. Varianty integrace — všechny možnosti (prospektivní výzkum)

> Každá varianta obsahuje: **scope, kódové změny, závislosti, download, čas, metriky, EROI, rizika, kdy zvolit, cvičení.**

### Varianta P0 — Drop-in BM25+RRF do `tool_kb_search` (DOPORUČENO)

**CO:** Nejmenší změna s největším dopadem. Nahradí `kb_search.py:38` scoring.

**PROČ:** 80% dotazů autora je KB docs (`ACI kalibrace`, `CI/CD`, `Moodpasta follow-up` — `kb_search.py:40` příklady). P0 přináší +6.9% MRR bez změny API.

**JAK — kódové změny (`mcp-local-server/src/mcp_local_server/tools/kb_search.py`):**

```python
# PŘED (kb_search.py:37-42):
content_lower = content.lower()
score = sum(1 for w in words if w in content_lower)  # bez IDF

# PO (inspirováno retrieval.py:27-141):
from mcp_retrieval.retrieval import BM25, rrf_fusion, tokenize, expand_query
# Build once (cached):
texts = [f.read_text(encoding="utf-8") for f in KB_ROOT.rglob("*.md")]
bm25 = BM25(k1=1.5,b=0.75).fit(texts)  # inverted_index + avg_dl
# Per query:
expanded = expand_query(query)  # SYNONYM_MAP
res_bm25 = bm25.search(query, top_k=20)
res_exp = bm25.search(expanded, top_k=20)
res_seq = search_fuzzy(query, texts, top_k=20)
rrf = rrf_fusion([res_bm25,res_exp,res_seq], k=60)  # → top max_results
```

Zachovat `@cached(ttl=300)` + `module` filtr (`kb_search.py:33`), přidat `file_mtime` invalidaci.

**Závislosti:** 0 — `math`, `collections`, `difflib`, `re` (stdlib). Žádný `pip install`.

**Čas:** 2-3 h (1 h kód + 1 h testy + 0.5 h benchmark).

**Metriky (očekávané, extrapolace z `EVALUATION.md:112`):** `MRR +6-8%`, `Prec@3 +15%`, latency `+1-2ms` (BM25 fit 30ms once, search 1ms), tokens `−49%` už v `EVALUATION.md:22` (dual-layer JSONL).

**EROI:** 9/10 — vysoký dopad / nízký náklad / nízké riziko.

**Rizika:** `tokenize` musí zachovat `à-ž` (`retrieval.py:14`) pro CZ; `SYNONYM_MAP` CZ/EN musí být omezen na 12 termů (jinak šum jako `enrichment v1` `EVALUATION.md:72`).

**Kdy zvolit:** Vždy jako první krok. Pokud P0 stačí (cílový `MRR≥0.70` splněn), P1/P2 odlož.

**Cvičení:** Spusť `py -3 -X utf8 -c "from mcp_retrieval.retrieval import BM25; b=BM25(); b.fit(['timeout v MCP','encoding cp1250']); print(b.search('timeout', top_k=2))"` a ověř `IDF(timeout) > IDF(v)`.

---

### Varianta P1 — Full Hybrid + Query Expansion + Dedup Core

**CO:** P0 + `SYNONYM_MAP` + `build_searchable_text` + sjednocení duplikátu `retrieve.py` ↔ `mcp-retrieval`.

**PROČ:** `Exp+Seq RRF` má **nejlepší Prec@3 0.6867 (+18.4%)** (`EVALUATION.md:112`) — klíčové pro `Prec@3` v `opencode` (LLM vidí top3). Duplikát 180 řádků je tech debt (drift).

**JAK — 3 podkroky:**

**P1a — Synonym + expansion (`retrieval.py:78-109` → `kb_search.py`):**
```python
SYNONYM_MAP = {"timeout":["deadlock",...], "encoding":["cp1250","utf-8"], ...} # 12
def expand_query(q): return tokenize(q) + flatten(SYNONYM_MAP[t][:2] for t in tokenize(q) if t in SYNONYM_MAP)
```

**P1b — Searchable text s metadaty (`retrieval.py:113` → `kb_search.py`):**
```python
def build_kb_searchable_text(path, content):
    # Front-matter + INDEX.md metadata + obsah
    meta = _lookup_metadata(path)  # kb_read_doc.py:62
    return f"{meta} {content[:2000]}"  # TITLE + EROI + 2K chars
# BM25 hledá i v `tags`, `Typ`, `EROI` — recall +15% (odhad z RETRIEVAL_RESEARCH.md:246)
```

**P1c — Dedup core (nový balíček):**
```
C:/_github/libs/retrieval_core/  # nebo mcp-retrieval jako lib
  ├── bm25.py          # BM25 class (retrieval.py:27)
  ├── fusion.py        # rrf_fusion + weighted (retrieval.py:136)
  ├── expansion.py     # SYNONYM_MAP + expand_query (retrieval.py:78)
  └── tokenize.py      # tokenize à-ž (retrieval.py:14)
```
`mcp-local-server/pyproject.toml:7` přidá `retrieval-core = {path="../libs/retrieval_core"}`, `ML_Ops_edukace/retrieve.py:1` importuje odtud. Eliminuje drift.

**Závislosti:** 0 (P1a/b), 0 (P1c je refactor).

**Čas:** 4-5 h (1.5 h P1a/b + 2 h P1c + 1 h migrace `retrieve.py`).

**Metriky:** `Prec@3 0.6867` (vs 0.6733 P0), `Recall 0.6933` (vs 0.6883) — malý gain, ale CZ/EN robustnost.

**EROI:** 8/10 — střední gain / střední náklad / nízké riziko. Odložit pokud P0 splní cíl.

**Rizika:** `expand_query` samostatně `-4.9% MRR` (`EVALUATION.md:122`) — musí být jen v `RRF`, ne samostatně. `build_searchable_text` nesmí duplikovat `tags` (enrichment `EVALUATION.md:72` zhoršilo MRR).

**Kdy zvolit:** Když autor často dotazuje CZ (`zaseknuti`, `kodovani`) a P0 Prec@3 <0.65.

**Cvičení:** Porovnej `kb_search("timeout")` vs `kb_search("zaseknuti")` — po P1a by měly vrátit stejné `GT-010`.

---

### Varianta P2 — Prospektivní pro ostatní MCP (MCP-Jobs, lichess)

**CO:** Aplikovat pipeline na `MCP-Jobs/skills_config.json` (94 skills) a `lichess-analyzer/patterns/chess_pattern_v5.json` (17 patternů).

**PROČ:** Oba jsou katalogy s `aliases` (146 aliasů jobs, 11 pattern aliases) — stejný problém jako `SYNONYM_MAP`. `skills_config.json:105` `embeddings` má alias `embeddingy`, `vector_db` má `pinecone/weaviate/qdrant` — BM25 s `aliases` jako `tags` zlepší recall bez dense.

**JAK — `MCP-Jobs` (P2-Jobs):**

```python
# Dnes: MCP-Jobs/src/mcp_jobs/matcher.py — boolean AND/OR/NOT + direct/partial/no_match
# Nově: volitelný rerank stage po boolean filtru
from retrieval_core.bm25 import BM25
skills_texts = [f"{s['display_name']} {' '.join(s['aliases'])} {s['category']}" for s in skills.values()]
bm25 = BM25().fit(skills_texts)  # 94 docs, avg_dl=8
# Query "vector database" → BM25 najde vector_db (alias pinecone) i embeddings → RRF → rerank top10
```

Nedělat dense — `GloVe 44.9% OOV` na `GT-*` (`EVALUATION.md:96`) by se opakovalo na `P9`, `TIA Portal`.

**JAK — `lichess-analyzer` (P2-Chess):**

Poznámka: `lichess-analyzer` má deterministický `pattern_detector.py:22` (ACPL, blunder) — retrieval je `pattern matching`, ne docs. Upgrade jen jako **ontologická analogie** v dokumentaci: `pattern library ≈ skill catalog`, `ACPL ≈ MRR`, `blunder ≈ GT-XXX`. Žádný kód, jen edukační paralela.

**Závislosti:** 0 (BM25 je stdlib). Pro `MCP-Jobs` přidat `retrieval_core` jako volitelný `rerank=True` flag (backward compat).

**Čas:** 6-8 h (3 h Jobs + 1 h chess docs + 2 h testy).

**Metriky (odhad, malý korpus 94):** `Recall +5%` (aliasy), `MRR +3%` — podobně jako `enrichment v1` `EVALUATION.md:72`. Dense by zhoršil (`EVALUATION.md:122`).

**EROI:** 6/10 — nízký gain / střední náklad / nízké riziko. Odložit po P0/P1.

**Rizika:** `MCP-Jobs` má `ThreadPoolExecutor` 4 + `TIMEOUT_PER_REPO` 15s (`cross_repo_search.py:14`) — přidání BM25 nesmí blokovat `search_jobs_v2` (36s pipeline `CONTEXT_REPOS.md:540`). Rerank jen na `top20` po boolean filtru.

**Kdy zvolit:** Až když `P0 MRR≥0.70` a autor požádá o sémantický `search_jobs_v2("retrieval augmented generation")` → má najít `RAG`.

**Cvičení:** Najdi v `skills_config.json` skill pro dotaz `ML operations` — dnes `MLOps` `0.50 partial_match` najde, ale `ML operations` s aliasem by měl najít stejně.

---

### Varianta C — Sdílený Retrieval Core + Embeddings Future (dlouhodobě)

**CO:** `mcp-retrieval` se stane **sdílenou knihovnou** pro celý ekosystém + příprava na dense až při >1K docs.

**PROČ:** Dnes 3 kopie BM25 (`mcp-retrieval/retrieval.py`, `ML_Ops_edukace/retrieve.py`, plánovaný `kb_search.py`) — drift (incident #2 `INCIDENT_ANALYZA_02` — harness-level gate). `RETRIEVAL_RESEARCH.md:123` cesta B (580MB `sentence-transformers`) je připravena pro budoucí dense.

**JAK:**

```
C:/_github/
├── libs/retrieval_core/              # NOVÝ — single source
│   ├── pyproject.toml (name="retrieval-core", version 0.1.0)
│   ├── src/retrieval_core/
│   │   ├── bm25.py          # BM25(k1=1.5,b=0.75) — retrieval.py:27
│   │   ├── fusion.py        # rrf_fusion(k=60), weighted_fusion
│   │   ├── expansion.py     # SYNONYM_MAP, expand_query
│   │   ├── tokenize.py      # tokenize à-ž
│   │   └── metrics.py       # MRR, Prec@K, Recall, NDCG — RETRIEVAL_RESEARCH.md:79
│   └── tests/test_bm25.py   # 3 testy z mcp-retrieval/tests/test_retrieval.py:36
├── mcp-local-server/pyproject.toml:7  dependencies += ["retrieval-core @ file://../libs/retrieval_core"]
├── mcp-retrieval/pyproject.toml       dependencies += ["retrieval-core"]
├── ML_Ops_edukace/retrieve.py         from retrieval_core import BM25  # místo lokální class
└── ML_Ops_edukace/_stahovani/         # future: sentence-transformers 384D (Cesta B) — až při >1K docs
```

**Budoucí dense (podmínka >1K docs):** `pip install sentence-transformers` 450MB + `cross-encoder/ms-marco-MiniLM-L-12-v2` 130MB (`RETRIEVAL_RESEARCH.md:137`) — až když KB >500 MD nebo GT >500 entries. Dnes (110+108) je BM25 vítěz.

**Závislosti:** Refactor 3 repa, `pyproject.toml` path dependency.

**Čas:** 8-10 h (4 h core + 2 h migrace + 2 h CI).

**Metriky:** 0% gain dnes, ale `−100% drift` do budoucna. Připravenost na `Cesta B` `MRR ~0.75-0.80` (`RETRIEVAL_RESEARCH.md:277`).

**EROI:** 7/10 (dlouhodobě) — 5/10 krátkodobě. Odložit po P0.

**Rizika:** Path dependency v `pyproject.toml` vyžaduje `uv`/`pip -e`. Nutný `harness-level gate` pro `DATA-FABRICATION-001`.

**Kdy zvolit:** Když se přidá 4. kopie BM25 nebo když KB přesáhne 500 MD.

**Cvičení:** Nakresli dependency graf `mcp-local-server → retrieval_core ← mcp-retrieval` a ověř, že `libs/retrieval_core` nemá závislost na `mcp-*`.

---

## 7. Rozhodovací matice — kdy kterou variantu

| Scénář | Korpus | Dotaz jazyk | Cíl MRR | Zvol | Důvod |
|--------|--------|-------------|---------|------|-------|
| **KB docs denně** (autor dnes) | 110 MD | CZ/EN mix | ≥0.70 | **P0** | 80% zisk za 30% času, 0 download |
| **CZ dotazy často** (`zaseknuti`) | 110 MD | CZ | Prec@3 ≥0.68 | **P1a/b** | Synonyma + metadata, +2 h |
| **Drift 3 kopií** | — | — | 0 drift | **P1c/C** | Single source, až při 3. kopii |
| **Job search sémantika** | 94 skills | EN | Recall +5% | **P2-Jobs** | Aliases jako tags, nízký gain |
| **Chess patterns** | 17 | EN | — | **P2-Chess docs only** | Analogie, žádný kód |
| **>1K docs budoucně** | >500 MD | CZ/EN | ≥0.75 | **C dense** | Až při >1K, dnes OOV 44.9% |

Doporučená sekvence: **P0 (ihned) → měření → pokud Prec@3<0.68 → P1a/b → pokud drift → P1c/C → pokud Jobs request → P2**.

---

## 8. Validační plán (po schválení, mimo tento artefakt)

| Krok | Příkaz | Očekávaný výsledek | Soubor |
|------|--------|-------------------|--------|
| 1 Benchmark KB | `py -3 ML_Ops_edukace/scripts/benchmark_full.py --kb` | `MRR≥0.70`, `Prec@3≥0.65` na 110 MD | `results/kb_benchmark_P0.json` |
| 2 Unit | `.venv/Scripts/python -m pytest mcp-local-server/tests/ -k kb_search -v` | 3 nové testy pass (BM25, RRF, synonym) | `tests/test_kb_search.py` |
| 3 Smoke cross_repo | `py -3 -c "from mcp_local_server.tools.cross_repo_search import cross_repo_search; print(cross_repo_search('ACI kalibrace'))"` | top3 obsahuje `vcf_color_service/config.json` | — |
| 4 Gate | `py -X utf8 .scripts/ascii_filenames_check.ps1` | exit 0 (`GT-080`) | — |
| 5 Rollback | `git revert <P0 commit>` + `cache.clear()` | návrat na `sum(1...)` do 1 min | — |

**Metriky definice:** `MRR=mean(1/rank_prvního)`, `Prec@3=relevant_v_top3/3`, `Recall=relevant_v_topK/celkem` (`RETRIEVAL_RESEARCH.md:79`).

---

## 9. Rizika a mitigace

| Riziko | Pravděpodobnost | Dopad | Mitigace |
|--------|----------------|-------|----------|
| `SYNONYM_MAP` šum (enrichment `EVALUATION.md:72` MRR -6.7%) | Střední | MRR pokles | P1a jen v RRF, ne samostatně; limit 12 termů, CZ/EN validace |
| `tokenize` bez `à-ž` → `MLOps` ≠ `ML Ops` | Nízká | Recall -10% | Použít `retrieval.py:14` regex `[^a-z0-9à-ž\-_]` |
| `cross_repo_search` zpomalení (BM25 na 22 rep) | Nízká | +200ms | BM25 jen pro `kb_search`, `cross_repo` zůstane `git grep` (code search) |
| Path dependency `libs/retrieval_core` | Střední | CI fail | `pip -e` + `uv.lock`, `hatchling` build |
| `DATA-FABRICATION-001` — halucinace `GT-XXX` | Vysoká (LLM) | Incident #2 | `AGENTS.md §6` chain: `gt_search` → `gt_get_entry` → citace, harness gate |

---

## 10. Edukační cvičení (pro čtenáře = autora)

1. **BM25 ručně:** Vezmi 3 KB soubory (`SWE_GLOSSARY`, `RE_Methodology`, `GROUND_TRUTH_aktualni_stav`), spočítej `TF("timeout")`, `IDF`, `BM25` s `k1=1.5,b=0.75`. Ověř, že `timeout` v `RE_Methodology` (df=1) má vyšší IDF než `a` (df=3).
2. **RRF:** Měj `rank1=[A,B,C]`, `rank2=[B,A,D]`, spočítej `RRF(A)=1/(60+1)+1/(60+2)`, `RRF(B)=1/(60+2)+1/(60+1)` — proč je fúze stejná? Kdy by nebyla?
3. **OOV:** Proč `GloVe` s `glove-wiki-gigaword-100` (400K slov) nezná `GT-001`? Co je `OOV rate`? Jak ho snížit bez tréningu? (Odpověď: `SYNONYM_MAP` + `ID` jako token).
4. **Kdy ne MMR:** Na 108 entries `MMR` zhoršilo `MRR 0.690→0.598` (`EVALUATION.md:126`). Proč diverzita škodí na malém korpusu? Kdy by pomohla? (Odpověď: >500 docs, různé `server`).
5. **P0 smoke:** Uprav lokálně `kb_search.py:38` na `BM25` (P0 snippet kap.6), spusť `tool_kb_search("MLOps pipeline")` a porovnej top3 před/po.

---

## 11. Provenance a souvislosti

| Zdroj | Co převzato | Řádek |
|-------|-------------|-------|
| `ML_Ops_edukace/RETRIEVAL_RESEARCH.md` | Ontologie 13 termů, 4 cesty, 8 kroků, K0-K3, CPM | `RETRIEVAL_RESEARCH.md:35-79` |
| `ML_Ops_edukace/EVALUATION.md` | 12 tabulek, vítěz `BM25+Seq RRF`, neúspěchy `GloVe/SVD/MMR` | `EVALUATION.md:37-126` |
| `ML_Ops_edukace/retrieve.py` | `BM25` class, `SYNONYM_MAP`, `rrf_fusion` 180 řádků | `retrieve.py:27-141` |
| `mcp-retrieval/retrieval.py` | `GTRetriever`, `BM25(k1=1.5,b=0.75)`, `SYNONYM_MAP` 12 | `retrieval.py:27-141` |
| `mcp-retrieval/README.md` | 4 tools, pipeline diagram, `AGENTS.md §7` gate | `README.md:66-193` |
| `mcp-local-server/tools/kb_search.py` | Starý `score=sum(1...)`, `@cached`, `module` filtr | `kb_search.py:10,38` |
| `mcp-local-server/tools/cross_repo_search.py` | `git grep -i`, `ThreadPool(4)`, `BLOCKED_DIRS` | `cross_repo_search.py:14,30` |
| `MCP-Jobs/skills_config.json` | 94 skills, 146 aliasů, váhy `MLOps 0.50` | `skills_config.json:105-118` |
| `B2B-Knowledge-Base/01_METODIKY/06_SWE_glossary` | Kap.13 ML/CV, kap.18 DevOps — doplnit MLOps | `SWE_GLOSSARY_zive_v1.md:30` |
| `opencode.jsonc` | 5 MCP serverů, timeouts, `default_agent:plan` | `opencode.jsonc:49-79` |

**Nový výzkum v tomto artefaktu:** Inventura 5 MCP × 42 tools (kap.3), gap `naivní vs hybrid` s CZ/EN příklady (kap.4), 4 (+1) pipeline s `Cache` stage (kap.5), 4 varianty P0/P1/P2/C s EROI a kdy zvolit (kap.6), rozhodovací matice 6 scénářů (kap.7) — žádný z originálů neobsahoval MCP prospektivu.

---

## 12. Next Steps (aktualizováno)

| # | Krok | Varianta | Soubor | Stav |
|---|------|----------|--------|------|
| 1 | ~~RETRIEVAL_RESEARCH — 4 cesty, 8 kroků~~ | — | `RETRIEVAL_RESEARCH.md` | ✅ 2026-08-26 |
| 2 | ~~EVALUATION — 108 entries benchmark~~ | — | `EVALUATION.md` | ✅ 2026-08-26 |
| 3 | ~~mcp-retrieval — produkční MCP (30 testů)~~ | — | `mcp-retrieval/` | ✅ 2026-08-27 |
| 4 | **Tento artefakt — syntéza + prospektiva** | — | `MCP_ECOSYSTEM_ADAPTATION_v1.md` | ✅ 2026-08-27 (právě) |
| 5 | P0 — BM25+RRF do `tool_kb_search` | **P0** | `mcp-local-server/tools/kb_search.py` | Plán — 2-3 h, 0 B |
| 6 | P1a/b — synonym+metadata | P1 | `kb_search.py` + `SYNONYM_MAP` | Plán — +2 h |
| 7 | P1c/C — sdílený `libs/retrieval_core` | P1c/C | `libs/retrieval_core/` | Plán — 8-10 h |
| 8 | P2-Jobs — rerank pro `skills_config.json` | P2 | `MCP-Jobs/src/mcp_jobs/` | Backlog |
| 9 | Validace KB benchmark (110 MD) | — | `results/kb_benchmark_P0.json` | Po P0 |

---

*Edukační artefakt — cíl: autor rozumí, proč `BM25+Seq RRF` je vítěz na <500 docs a kdy zvolit kterou variantu integrace. PBL: řeší vlastní opencode workflow, ne abstraktní MLOps.*
*Vytvořeno: 2026-08-27 | Zdroj: syntéza 5 originálních artefaktů + nový výzkum 22 rep. Vítěz pipeline: `BM25+Seq RRF (MRR 0.7067)` — přenositelný na `tool_kb_search`.*
