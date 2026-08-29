# RETRIEVAL PIPELINE: Výzkumná zpráva + Implementační plán

**Datum:** 2026-08-26 | **Autor:** outpost2026
**Metodika:** Komprese realismus (CPM) + veřejné zdroje + interní KB + MCP-Jobs skills ontology
**Status:** Plán (plan mode — žádné změny)

---

## PARADOX: Rediscovery ontologie přes vlastní projekt

Autor řeší konkrétní problém (vylepšení retrieval metrik pro GT postmortem katalog) a současně objevuje ontologii, která se shoduje s termíny z IT trhu práce. Tyto pojmy se vyskytují jako klíčové dovednosti v zájmových inzerátech v MCP-Jobs skills catalogu.

| Pojem v našem projektu | MCP-Jobs kategorie | MCP-Jobs weight | Typický inzerát |
|------------------------|-------------------|-----------------|-----------------|
| **Embeddings** | `AI_CONCEPT` | 0.50 | "Zkušenosti s embeddings modely" |
| **Vector Database** | `AI_TOOL` | 0.45 | "Pinecone, Weaviate, Qdrant" |
| **RAG** | `IT_SKILL` | 0.50 | "Retrieval-Augmented Generation" |
| **NLP** | `AI_FIELD` | 0.45 | "Zpracování přirozeného jazyka" |
| **LLM** | `IT_SKILL` | 0.60 | "Velké jazykové modely, LLMOps" |
| **PyTorch** | `ML_FRAMEWORK` | 0.60 | "PyTorch Lightning" |
| **scikit-learn** | `ML_FRAMEWORK` | 0.40 | "ML frameworky" |
| **MLOps** | `METHODOLOGY` | 0.50 | "ML operations, monitoring" |
| **Semantic Search** | (implicitní v `embeddings`) | — | "Semantic search pipeline" |
| **Cross-encoder** | (implicitní v `NLP`) | — | "Reranking, sentence similarity" |
| **BM25** | (implicitní v `NLP`) | — | "Full-text search, information retrieval" |
| **TF-IDF** | (implicitní v `NLP`) | — | "Text preprocessing, feature extraction" |
| **Hybrid Search** | (implicitní v `vector_db`) | — | "Hybrid search, RRF fusion" |

**PBL (Problem-Based Learning) insight:** Autor nejprve studoval tyto pojmy abstraktně. Nyní je aplikuje na konkrétní problém — a tím si je osvojuje hlouběji než čtením dokumentace.

---

## 1. ONTOLOGIE: Kompletní terminologie retrieval pipeline

### 1.1 Sparse Search (keyword-based)

| Term | Definice | Implementace | Náš případ |
|------|----------|--------------|------------|
| **BM25** (Best Matching 25) | Probabilistický retrieval model, založený na TF-IDF s length normalization. Vypočítává relevance dokumentu vůči query na základě četnosti termínů a inverzní dokumentové frekvence. | `rank_bm25` (pip) nebo z Python stdlib | `GT-001`, `P9`, `cnc-tools` = přesné termíny |
| **TF-IDF** (Term Frequency–Inverse Document Frequency) | Numerická reprezentace důležitosti termínu v dokumentu vůči korpusu. TF = četnost termínu, IDF = log(N/df) kde df = počet dokumentů s termínem. | `sklearn.TfidfVectorizer` nebo numpy | "timeout" má vysoké IDF (vzácný v korpusu) |
| **Inverted Index** | Datová struktura: pro každý termín seznam dokumentů, kde se vyskytuje. Umožňuje O(1) lookup. | BM25 interně | — |
| **Posting List** | Seznam dokumentů obsahujících daný termín + pozice. Základ inverted indexu. | BM25 interně | — |

**MCP-Jobs ekvivalent:** `NLP` (weight 0.45), `prompt_engineering` (weight 0.50)

### 1.2 Dense Search (semantic-based)

| Term | Definice | Implementace | Náš případ |
|------|----------|--------------|------------|
| **Embedding** (vektorová reprezentace) | K-dimenzionální vektor zachycující sémantický význam textu. "timeout problém" a "deadlock issue" mají blízké vektory. | OpenAI `text-embedding-3-small` (1536D), `sentence-transformers` (384-768D), TF-IDF (nD) | 108 entries → 108×384 matrix |
| **Cosine Similarity** | Míra podobnosti dvou vektorů: cos(θ) = (A·B)/(‖A‖·‖B‖). Hodnota 1 = identické, 0 = nesouvisející. | `numpy.dot(v1, v2)` po L2 normalizaci | Porovnání query vektoru s entry vektory |
| **ANN** (Approximate Nearest Neighbors) | Algoritmus pro rychlé hledání nejbližších sousedů ve vysokodimensionálním prostoru. Přesný NN je O(n), ANN je O(log n). | FAISS, Annoy, HNSW | Na 108 entries nepotřebujeme (brute-force stačí) |
| **HNSW** (Hierarchical Navigable Small World) | Grafová struktura pro ANN. Vrstvený graf: horní vrstvy = hrubý přehled, dolní = detailní hledání. | FAISS, Qdrant, Weaviate | — |
| **Flat vs Index Flat** | Flat = brute-force (přesný, pomalý). Index = přibližný (rychlý, nepřesný). | FAISS `IndexFlatIP` vs `IndexIVFFlat` | Flat stačí pro 108 entries |

**MCP-Jobs ekvivalent:** `embeddings` (weight 0.50), `vector_db` (weight 0.45), `PyTorch` (weight 0.60), `scikit-learn` (weight 0.40)

### 1.3 Hybrid Fusion

| Term | Definice | Implementace | Náš případ |
|------|----------|--------------|------------|
| **RRF** (Reciprocal Rank Fusion) | Algoritmus pro sloučení dvou ranked listů. Skóre = Σ 1/(k + rank_i). K=60 = standard. Funguje na ranku, ne na skóre → scale-invariant. | 3 řádky kódu | BM25 rank + Dense rank → merged rank |
| **MMR** (Maximal Marginal Relevance) | Re-ranking pro diverzitu. Upřednostňuje dokumenty, které jsou relevantní A odlišné od již vybraných. | `λ * sim(d,q) - (1-λ) * max(sim(d,d'))` | Implementováno — zhoršuje MRR na malém korpusu (108 entries) |
| **Weighted Score Fusion** | Lineární kombinace: `α * score_bm25 + (1-α) * score_dense`. α=0.5-0.7 = výchozí. | Jednoduché | Alternativa k RRF |

**MCP-Jobs ekvivalent:** `RAG` (weight 0.50), `agentic_systems` (weight 0.60)

### 1.4 Reranking

| Term | Definice | Implementace | Náš případ |
|------|----------|--------------|------------|
| **Cross-encoder** | Model, který společně hodnotí (query, document) pár. Přesnější než bi-encoder (samostatné encoding), ale pomalejší. | `cross-encoder/ms-marco-MiniLM-L-12-v2` (~130MB) | Rerank top-20 → top-5 |
| **Bi-encoder** | Model, který encoduje query a dokument nezávisle. Rychlejší, méně přesný. | `sentence-transformers` | Naše TF-IDF je ekvivalent |
| **Re-ranker** | Obecný termín pro model, který přehodnotí pořadí kandidátů z první fáze. | Cross-encoder, LLM-as-reranker | Finální fáze pipeline |
| **Latent space** | Prostor, ve kterém jsou embeddings reprezentovány. Dimenze = "features" které model rozumí. | Model-dependent | TF-IDF: dimenze = velikost slovníku |

**MCP-Jobs ekvivalent:** `LLM` (weight 0.60), `HuggingFace` (weight 0.50), `ML` (weight 0.50)

### 1.5 Metriky

| Term | Definice | Vzorec | Náš případ |
|------|----------|--------|------------|
| **Precision@K** | Podíl relevantních dokumentů v top-K výsledcích | relevantní_v_top_K / K | Precision@3 = kolik z top-3 je správně |
| **Recall** | Podíl nalezených relevantních dokumentů z celkového počtu | relevantní_v_top_K / celkový_relevantní | Recall = kolik z 25 queries našlo svůj GT |
| **MRR** (Mean Reciprocal Rank) | Průměr inverzních pozic prvního relevantního dokumentu | mean(1/rank_prvního) | MRR = jak brzo se správný GT objeví |
| **NDCG** (Normalized Discounted Cumulative Gain) | Ranking quality s graded relevance. Vyšší pozice = vyšší váha. | DCG/IDCG | NDCG@5 = kvalita top-5 s relevantními stupni |
| **Hit Rate** | Podíl queries s alespoň jedním relevantním dokumentem v top-K | hits / total_queries | Hit@5 = % queries které našly alespoň 1 relevantní |
| **MAP** (Mean Average Precision) | Průměr precision napříč recall úrovněmi | mean(AP per query) | — |

**MCP-Jobs ekvivalent:** (metriky se nevyskytují přímo v skills, ale souvisejí s `MLOps`)

---

## 2. ARCHITEKTURA: 4-stupňová pipeline

```
                    ┌─────────────────────────────────────────────────┐
                    │         RETRIEVAL PIPELINE (4 stages)           │
                    └─────────────────────────────────────────────────┘

    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
    │   STAGE 1    │    │   STAGE 2    │    │   STAGE 3    │    │   STAGE 4    │
    │   BM25       │    │   Dense      │    │   RRF        │    │   Rerank     │
    │  (sparse)    │    │  (semantic)  │    │  (fusion)    │    │  (precision) │
    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
           │                   │                   │                   │
           ▼                   ▼                   ▼                   ▼
    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
    │ Inverted     │    │ Embedding    │    │ Score        │    │ Cross-       │
    │ Index        │    │ Matrix       │    │ Combination  │    │ encoder      │
    │ (O(1) lookup)│    │ (N × D)      │    │ (rank-based) │    │ (pair score) │
    └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘

    Vstup: query ──→ [tokenize] ──→ BM25 scores ──→ rank list ──┐
    Vstup: query ──→ [encode]   ──→ cos sim     ──→ rank list ──┼──→ merged ──→ reranked ──→ top-5
                                                                   │
    Fusion: RRF = Σ 1/(k + rank) pro každý list                  │
    Rerank: cross-encoder(query, doc) → relevance score ──────────┘
```

---

## 3. IMPLEMENTAČNÍ CESTY (od 0 do plné ML)

### Cesta A: Zero-Download (numpy only)

| Stage | Implementace | Závislosti | Download |
|-------|-------------|------------|----------|
| BM25 | Z Python stdlib (Counter + math.log) | `collections`, `math` | 0 B |
| Dense | TF-IDF na numpy (hand-written) | `numpy` (už máme) | 0 B |
| RRF | 3 řádky kódu | `dict` | 0 B |
| Rerank | BM25 score jako proxy | — | 0 B |
| **Celkem** | | | **0 B** |

**Proč:** 4G/500MB limit + OpenAI credit exhausted. Ideální pro POC.

### Cesta B: Lightweight ML (pip install ~50MB)

| Stage | Implementace | Závislosti | Download |
|-------|-------------|------------|----------|
| BM25 | `pip install rank_bm25` | Python stdlib | ~50 KB |
| Dense | `pip install sentence-transformers` | PyTorch (~400MB) | ~450 MB |
| RRF | 3 řádky kódu | — | 0 B |
| Rerank | `cross-encoder/ms-marco-MiniLM-L-12-v2` | sentence-transformers | ~130 MB |
| **Celkem** | | | **~580 MB** |

**Proč:** Plná ML kvalita. Problém: 500MB data limit.

### Cesta C: OpenAI API (cloud)

| Stage | Implementace | Závislosti | Download |
|-------|-------------|------------|----------|
| BM25 | `pip install rank_bm25` | Python stdlib | ~50 KB |
| Dense | OpenAI `text-embedding-3-small` | `httpx` (už máme) | 0 B |
| RRF | 3 řádky kódu | — | 0 B |
| Rerank | OpenAI API (nebo Cohere Rerank) | `httpx` | 0 B |
| **Celkem** | | | **~50 KB** |

**Proč:** Nejlepší kvalita, 0 download. Problém: credit exhausted.

### Cesta D: Hybrid (zero-download + malý model)

| Stage | Implementace | Závislosti | Download |
|-------|-------------|------------|----------|
| BM25 | Z Python stdlib | `collections`, `math` | 0 B |
| Dense | GloVe pre-trained (glove-wiki-gigaword-100) | `gensim`, `numpy` | 128 MB |
| RRF | 3 řádky kódu | — | 0 B |
| Rerank | TF-IDF rerank (ad-hoc) | — | 0 B |
| **Celkem** | | | **~128 MB** |

**Proč:** Kompromis — GloVe embeddings jsou lepší než TF-IDF, 128MB se vejde do limitu.
**Výsledek:** Selhalo — 44.9% OOV rate, GloVe nezná naše doménové termíny.

---

## 4. DETAILNÍ IMPLEMENTAČNÍ PLÁN (Cesta A: Zero-Download)

### Krok 1: Tokenizace + BM25 (0 B, ~30 min) ✅ HOTOVO

**Co:** Implementovat BM25 z Python stdlib.

**Výsledek:** BM25 baseline — Recall +4.5%, MRR -3.3% vs SequenceMatcher.

### Krok 2: TF-IDF Dense (0 B, ~30 min) ✅ HOTOVO

**Co:** Implementovat TF-IDF jako "dense" náhradu.

**Výsledek:** TF-IDF — Recall +1.8%, MRR -11.3% vs SequenceMatcher.

### Krok 3: RRF Fusion (0 B, ~5 min) ✅ HOTOVO

**Co:** Sloučit BM25 + TF-IDF výsledky.

**Výsledek:** Hybrid RRF — Recall +4.5%, MRR -4.9% vs SequenceMatcher.

### Krok 4: Evaluace (0 B, ~20 min) ✅ HOTOVO

**Co:** Spustit 25 queries × 2 jazyky přes všechny pipeline.

**Výsledky:**
- SequenceMatcher: MRR 0.6613 (baseline)
- BM25: MRR 0.6397 (-3.3%)
- BM25+Seq RRF: **MRR 0.7067 (+6.9%)** 🏆

### Krok 5: Ensemble BM25+Seq RRF (0 B, ~30 min) ✅ HOTOVO

**Co:** Kombinovat 5 BM25 konfigurací + SequenceMatcher přes RRF.

**Výsledek:** BM25+Seq RRF — MRR 0.7067, Recall 0.6883, Hits 43/50. **Poprvé poráží SequenceMatcher na MRR i Recall.**

### Krok 6: TF-IDF+SVD (30 MB, ~30 min) ✅ HOTOVO

**Co:** Latent Semantic Analysis přes scikit-learn.

**Výsledek:** Selhalo — MRR 0.5413 (-18.1%). Příliš agresivní pro malý korpus (56.4% explained variance).

### Krok 7: Query Expansion (0 B, ~20 min) ✅ HOTOVO

**Co:** Synonymní slovník pro klíčové termíny.

**Výsledek:** BM25+Expand = -4.9% MRR samostatně. **Exp+Seq RRF = +18.4% Prec@3, +6.9% MRR** — nejlepší Prec@3 dosud.

### Krok 8: Weighted RRF (0 B, ~5 min) ✅ HOTOVO

**Co:** Vážená fúze: α·BM25 + (1-α)·SequenceMatcher.

**Výsledek:** Weighted RRF (0.6/0.4) = +3.8% MRR. Lepší než rovnocenný, horší než standardní RRF.

---

## 5. INSPIRACE Z MCP-Jobs: Skills ontology jako retrieval metadata

MCP-Jobs skills catalog (94 skills, 146 aliases) ukazuje, jak kategorizovat informace. Aplikujeme stejný princip na GT katalog:

### 5.1 GT Entry = Skill Match

| GT pole | MCP-Jobs analog | Typ |
|---------|-----------------|-----|
| `server` | `category` | Kategorizace |
| `typ` | `category` (ML_FRAMEWORK, AI_TOOL, ...) | Typ problému |
| `status` | (analog: verdict SLEDOVAT/MEDIUM/NESLEDOVAT) | Stav |
| `rule` | `skill_id` | Identifikátor |
| `tags` | `aliases` | Vyhledávací termíny |
| `complexity` | `weight` (0.0-1.0) | Priorita |

### 5.2 Přínos pro retrieval

| Bez tags | S tags |
|----------|--------|
| BM25 hledá jen v `symptom`, `root_cause`, `fix` | BM25 hledá i v `tags`, `typ`, `server` |
| "timeout" → 5 entries | "timeout" + tag "timeout" → 3 entries (přesnější) |
| Recall: ~60% | Recall: ~75% (odhad) |

---

## 6. KOMPRESE REALISMUS: Aplikace CPM na retrieval

### 6.1 Tříkanálový model šumu (z CPM)

| Kanál | Retrieval analog | Řešení |
|-------|-----------------|--------|
| **K0 Orákulum** | Ground truth (test queries s expected GT IDs) | Určuje, zda retrieval funguje |
| **K1 Detektor** | BM25/TF-IDF skóre může být chybné | Cross-validation, A/B test |
| **K2 Kontrakt** | Query může být nejasný (ambiguity) | Query expansion, synonymní slovník |
| **K3 Dekodér** | LLM může špatně interpretovat retrieved chunks | Reranking, metadata enrichment |

### 6.2 Kompresní poměr retrieval

| Metrika | Bez retrieval | S retrieval (top-5) | Kompresní poměr |
|---------|--------------|---------------------|-----------------|
| Tokeny | 28,422 (všechny entries) | ~2,500 (5 entries × 500 T) | **11.4x** |
| Bytes | 118,592 | ~5,500 | **21.6x** |
| LLM context | 100% | ~9% | **91% redukce** |

---

## 7. ROZHODOVACÍ MATRIX (aktualizováno)

| Scénář | Cesta | MRR | Důvod |
|--------|-------|-----|-------|
| **Nejlepší výsledek** | **BM25+Seq RRF** | **0.7067** | Poprvé poráží SequenceMatcher na MRR i Recall |
| POC, žádný internet | A (Zero-Download) | 0.6397 | 0 B, BM25 stačí |
| POC, malý download | D (GloVe) | 0.2607 | ❌ Selhalo (44.9% OOV) |
| Plná kvalita | B (sentence-transformers) | ~0.75-0.80 | 580MB, nejlepší open-source |
| Plná kvalita + API | C (OpenAI) | ~0.80-0.85 | 0 download, nejlepší celkově |
| Produkce | **BM25+Seq RRF + CI/CD** | 0.7067 | MLOps, A/B test, drift detection |

---

## 8. GLOSÁŘ: ML Ops terminologie pro autora

| Pojem | Český ekvivalent | Vysvětlení (PBL kontext) |
|-------|------------------|--------------------------|
| **Embedding** | Vektorová reprezentace | Převod textu na čísla tak, aby podobné texty měly podobná čísla |
| **Vector Database** | Vektorová databáze | Databáze optimalizovaná pro hledání podobných vektorů (ne přesných hodnot) |
| **BM25** | Nejlepších 25 (algoritmus) | "Kolikrát se slovo vyskytuje × jak vzácné to slovo je" |
| **TF-IDF** | Četnost termínu–inverzní dokumentová frekvence | Číslo: jak důležité je slovo pro tento dokument v kontextu všech dokumentů |
| **Cosine Similarity** | Kosinusová podobnost | Úhel mezi dvěma vektory: 0° = identické, 90° = nesouvisející |
| **RRF** | Reciproká fúze ranků | Sloučení dvou žebříčků: 1/(k + pozice) |
| **Cross-encoder** | Přesný hodnotitel | Model který společně čte query + dokument a říká "tohle sedí" |
| **Bi-encoder** | Rychlý kodér | Model který čte query a dokument zvlášť, pak porovnává |
| **MRR** | Střední inverzní rank | "Jak brzo se správná odpověď objeví?" |
| **NDCG** | Normalizovaný diskontovaný kumulativní zisk | "Je první odpověď lepší než desátá?" |
| **Precision@K** | Přesnost na K | "Kolik z top-K je správně?" |
| **Recall** | Pokrytí | "Kolik z celkových relevantních jsme našli?" |
| **Latent space** | Latentní prostor | "Prostor kde se skrývají významy (ne slova)" |
| **HNSW** | Hierarchický navigovatelný malý svět | Graf pro rychlé hledání v milionech vektorů |
| **ANN** | Přibližné nejbližší sousedy | "Nemusíme najít přesně nejlepší, stačí dostatečně dobrý" |
| **MLOps** | ML operace | "Jak provozovat ML model v produkci" |
| **RAG** | Retrieval-Augmented Generation | "LLM + externí znalosti = méně halucinací" |

---

## 9. SOUVISLOSTI S EXISTUJÍCÍ KB

| KB dokument | Souvislost s retrieval pipeline |
|-------------|--------------------------------|
| `COMPRESSION_PATTERN_METHOD_v1.0.md` | K0-K3 noise model = retrieval quality layers |
| `RE_Methodology.md` §3.4 SNR Princip | Precision = signál/(signál+šum) |
| `ontologie_kompresnich_modelu_reality.md` | Latentní prostor, manifold, komprese |
| `DE_NOVO_SEMANTICKY_AUDIT_2026-08-15.md` | Skill acquisition chains, tematická rozptýlenost |
| MCP-Jobs `skills_config.json` | 94 skills, weights, categories = ontologie |

---

## 10. NEXT STEPS (aktualizováno)

| # | Krok | Cesta | Download | Stav |
|---|------|-------|----------|------|
| 1 | ~~Tokenizace + BM25 z stdlib~~ | A | 0 B | ✅ Hotovo |
| 2 | ~~TF-IDF na numpy~~ | A | 0 B | ✅ Hotovo |
| 3 | ~~RRF fusion~~ | A | 0 B | ✅ Hotovo |
| 4 | ~~Benchmark~~ | A | 0 B | ✅ Hotovo |
| 5 | ~~Ensemble BM25+Seq RRF~~ | A+B | 0 B | ✅ **VÍTĚZ** (0.71 MRR) |
| 6 | ~~GloVe pre-trained~~ | D | 128 MB | ✅ Selhalo (44.9% OOV) |
| 7 | ~~TF-IDF+SVD~~ | - | 30 MB | ✅ Selhalo (0.54 MRR) |
| 8 | ~~Query expansion~~ | - | 0 B | ✅ Exp+Seq RRF (nejlepší Prec@3) |
| 9 | ~~Opravit 30 entries s "see source" root_cause~~ | - | 0 B | ✅ Opraveno 19/30, zbývá 11 |
| 10 | ~~MMR (diverzita)~~ | - | 0 B | ✅ Selhalo (zhoršuje MRR na malém korpusu) |
| 11 | ~~CLI nástroj (retrieve.py)~~ | - | 0 B | ✅ Hotovo |
| 12 | Produkční implementace (API endpoint) | - | 0 B | Plán |

---

---

## 11. QER/RTF — Experimentální adopční laboratoř (RAG/QER/RTF) — CLI playground pro autora

**Status:** `ML_Ops_edukace` je experimentální, výukové & adopční repo — agregace poznatků z živého studia a tvorby POC `RAG` (Retrieval-Augmented Generation) / `QER` (Query-Encode-Retrieve) / `RTF` (Retrieve-Transform-Fuse). Stejnou metodou jako `SQL` ( `postgresql_zakladni_prikazy_2026-08-15.md` — `SELECT/WHERE/ILIKE/GROUP BY` ověřeno na 93 ads) si zde osvojuješ `IR` operace na vlastních datech (108 GT entries, 121 KB docs) — bez nutnosti internetu, `py -X utf8` + `stdlib`.
**Repo charakter:** živé studio, ne produkce. Každý příkaz níže je `PBL 60%` — spustitelný `dry-run` v `TEMP_workflow_sim/P0_DRY_RUN` i `ML_Ops_edukace/`, ověřený na 2026-08-27.
**Návaznost:** `MCP_ECOSYSTEM_ADAPTATION_v1.md` (P0/P1/P2/C), `RETRIEVAL_BOTTLENECK_ANALYSIS_v1.md` (B1-B5, `window 4000` vs `full`), `EVALUATION.md:41` (MRR 0.7067), `TEMP_workflow_sim/P0_DRY_RUN/results/DRY_RUN_REPORT.md` (+13.5% MRR na KB)
**Provenance:** source-read (live `py -3` runy v tempu: 121 docs fit 452ms, `BM25(k1=1.5,b=0.75)` + `RRF(k=60)` + `SYNONYM_MAP 12`, `TEMP_workflow_sim/P0_DRY_RUN/results/benchmark_results.json`)

### 11.0 Jak spustit (jako `SQL: scripts/db.ps1` — zde `py -X utf8`)

```powershell
# Pozice: musíš být v _github\ — ověř před každým příkazem (AGENTS.md §1)
Get-Location  # → C:\Users\PC\Documents\Repozitar_Dev\_github

# Interaktivní playground (jako psql — pager vypnut, nic neblokuje, UTF-8)
py -X utf8 ML_Ops_edukace\retrieve.py --interactive
# → > timeout v MCP serveru  (CZ/EN, synonym timeout→deadlock)

# Jednorázový dotaz bez vstupu do konzole (jako db.ps1 query "SELECT...")
py -X utf8 ML_Ops_edukace\retrieve.py "encoding problem na Windows"
py -X utf8 ML_Ops_edukace\retrieve.py "YOLO11 garden monitor"

# MCP-retrieval přímý Python (jako information_schema.columns)
py -X utf8 -c "from mcp_retrieval.retrieval import GTRetriever; r=GTRetriever(); print(r.search('cache invalidace', top_k=3))"
py -X utf8 -c "from mcp_retrieval.retrieval import GTRetriever; r=GTRetriever(); print(r.get_entry('GT-010'))"
py -X utf8 -c "from mcp_retrieval.retrieval import GTRetriever; r=GTRetriever(); print(r.stats())"

# Benchmark jako GROUP BY/HAVING (ověřeno na 108×50, jako 93 ads)
py -X utf8 ML_Ops_edukace\scripts\benchmark_full.py
py -X utf8 ML_Ops_edukace\scripts\test_all.py

# P0 dry-run na KB (121 docs, 10 dotazů — jako SELECT COUNT(*) FROM ads)
py -3 TEMP_workflow_sim\P0_DRY_RUN\benchmark.py
py -3 TEMP_workflow_sim\P0_DRY_RUN\baseline_kb_search.py "ACI kalibrace"
py -3 TEMP_workflow_sim\P0_DRY_RUN\p0_kb_search.py "timeout MCP server deadlock"
```

Konvence: příkazy `py -X utf8` (ne `python`) kvůli `cp1250` (`AGENTS.md §2.1`); `py -3` pro `TEMP_workflow_sim` (čisté `stdlib`); výstup `score` je `RRF` (0.03-0.04) nebo `BM25` (8-9), ne `MRR`.

### 11.1 Meta-příkazy (jako `\l \dt \d` — přehled o korpusu)

| Příkaz | Význam (SQL analog) | Příklad | Očekávaný výstup |
|--------|---------------------|---------|------------------|
| `r.stats()` | `\l` — seznam DB + velikosti | `py -X utf8 -c "from mcp_retrieval.retrieval import GTRetriever; print(GTRetriever().stats())"` | `{'total_entries':108, 'servers':{'cnc-tools':14}, 'unique_rules':85}` |
| `r.list_rules()` | `\dt` — seznam tabulek | `py -X utf8 -c "from mcp_retrieval.retrieval import GTRetriever; print(GTRetriever().list_rules()[:3])"` | `[{"rule_id":"P9","count":14},...]` |
| `r.get_entry("GT-010")` | `\d ads` — struktura tabulky | `py -X utf8 -c "from mcp_retrieval.retrieval import GTRetriever; print(GTRetriever().get_entry('GT-010'))"` | `{"id":"GT-010","symptom":"Latentní deadlock...","rule":"P25"}` |
| `ls ML_Ops_edukace/data` | `\di` — jen indexy | `Get-ChildItem ML_Ops_edukace\data -File` | `gt_full.jsonl 60.6KB, gt_rules.json 6.5KB, test_queries.json` |
| `Get-Content kb_test_queries.json` | `SELECT * FROM information_schema.columns` | `Get-Content TEMP_workflow_sim\P0_DRY_RUN\kb_test_queries.json` | `10` dotazů s `expected` (jako `ads` 93) |

### 11.2 SELECT — základ a variace (jako `SELECT * FROM ads`)

```powershell
# Všechny entry (jako SELECT * FROM ads;)
py -X utf8 -c "from mcp_retrieval.retrieval import GTRetriever; r=GTRetriever(); r.load(); print([e['id'] for e in r.entries[:5]])"
# → ['GT-001','GT-002','GT-003','GT-004','GT-005']

# Vybrané sloupce (jako SELECT title, company FROM ads;)
py -X utf8 -c "from mcp_retrieval.retrieval import GTRetriever; r=GTRetriever(); print([(e['id'], e['server'], e['rule']) for e in r.entries[:3]])"
# → [('GT-001','mcp-retrieval','P1'),...]

# Alias (jako AS nazev)
py -X utf8 -c "from mcp_retrieval.retrieval import GTRetriever; r=GTRetriever(); print([{'dotaz':e['symptom'][:40]} for e in r.entries[:1]])"
# Bez duplicit (jako SELECT DISTINCT portal FROM ads;)
py -X utf8 -c "from mcp_retrieval.retrieval import GTRetriever; r=GTRetriever(); print(set(e['server'] for e in r.entries))"
# → {'mcp-retrieval','cnc-tools','mcp-jobs','linkedin-mcp-custom','gcp'}

# Kolik unikátních (jako COUNT(DISTINCT company))
py -X utf8 -c "from mcp_retrieval.retrieval import GTRetriever; r=GTRetriever(); print(len(set(e['rule'] for e in r.entries)))"
# → 85 (jako 93 ads → 12 firem)

# Limit + offset (jako LIMIT 5 OFFSET 5)
py -X utf8 -c "from mcp_retrieval.retrieval import GTRetriever; r=GTRetriever(); print([e['id'] for e in r.entries[5:10]])"
```

### 11.3 WHERE — filtrování (jako auto-filtr v Excelu)

```powershell
# Přesná shoda (jako WHERE company = 'T-Mobile')
py -X utf8 -c "from mcp_retrieval.retrieval import GTRetriever; r=GTRetriever(); print([e['id'] for e in r.entries if e['server']=='cnc-tools'][:3])"
# → ['GT-010','GT-087',...]

# Nerovnost / rozsah (jako WHERE id > 10)
py -X utf8 -c "from mcp_retrieval.retrieval import GTRetriever; r=GTRetriever(); print([e['id'] for e in r.entries if e['server']!='gcp'][:3])"

# Kombinace AND/OR (jako WHERE status='new' AND portal='jobs')
py -X utf8 -c "from mcp_retrieval.retrieval import GTRetriever; r=GTRetriever(); print([e['id'] for e in r.entries if e['server']=='mcp-retrieval' and 'P9' in e['rule']])"
# Závorky mění prioritu (jako (status='new' OR status='seen') AND portal='jobs')
py -X utf8 -c "from mcp_retrieval.retrieval import GTRetriever; r=GTRetriever(); print([e['id'] for e in r.entries if (e['server']=='cnc-tools' or e['server']=='gcp') and e['rule']=='P25'])"
```

### 11.4 Kontextové vyhledávání ILIKE (jako `%engineer%` — zde `gt_search` / `BM25`)

**Klíčový vzor:** `ILIKE '%slovo%'` = case-insensitive, `%` = cokoliv. V retrieval je to `gt_search("slovo")` = `BM25 + Seq + RRF` (místo `ILIKE`).

```powershell
# Obsahuje slovo kdekoli (jako ILIKE '%engineer%')
py -X utf8 ML_Ops_edukace\retrieve.py "timeout"
# → [1] GT-010 (score 0.0487) Symptom: Latentní deadlock...  (jako SELECT title FROM ads WHERE title ILIKE '%timeout%';)

# Více slov (jako ILIKE '%python%' OR ILIKE '%ai%')
py -X utf8 -c "from mcp_retrieval.retrieval import GTRetriever; r=GTRetriever(); print(r.search('timeout deadlock', top_k=3))"
# Slovo uprostřed / začátek / konec — v retrieval nerozlišuje, BM25 je bag-of-words (jako ILIKE '%ai%' vs 'junior%' vs '%python' — zde vše OR)

# Hledání ve více sloupcích (jako title ILIKE '%python%' OR company ILIKE '%python%')
py -X utf8 -c "from mcp_retrieval.retrieval import GTRetriever; r=GTRetriever(); print(r.search('encoding cp1250', top_k=3))"
# → hledá v symptom+root_cause+fix+server+tags+rule (build_searchable_text)

# Hledání v názvu NEBO popisu (nejdůležitější vzor — zde symptom NEBO fix)
py -X utf8 ML_Ops_edukace\retrieve.py "Playwright cookie expirace"
# → GT-026 (jako ILIKE '%python%' OR description ILIKE '%python%')

# Regex (jako ~* '(python|ai)') — zde SYNONYM_MAP: timeout→deadlock
py -X utf8 -c "from mcp_retrieval.retrieval import GTRetriever; r=GTRetriever(); print(r.search('zaseknuti', top_k=3))"
# → najde GT-001 (timeout) via SYNONYM_MAP (jako regex)
```

**Pozn.:** pro běžné hledání stačí `gt_search("slovo")`. Regex je `SYNONYM_MAP` 12 termů.

### 11.5 ORDER BY — řazení (jako `ORDER BY company`)

```powershell
# Vzestupně / sestupně (jako ORDER BY company ASC/DESC) — v retrieval je to score DESC
py -X utf8 -c "from mcp_retrieval.retrieval import GTRetriever; r=GTRetriever(); res=r.search('cache', top_k=5); print([(x['id'], x['score']) for x in res])"
# → [('GT-074',0.042),('GT-050',0.038),...]  (ORDER BY score DESC)

# Podle více sloupců (jako ORDER BY company, title) — zde RRF = ORDER BY rank1, rank2
py -X utf8 TEMP_workflow_sim\P0_DRY_RUN\p0_kb_search.py "YOLO11 garden monitor"
# → 04_KNOWLEDGE_BASE/.../YOLO11_GARDEN... [0.0492] (rank1 BM25 + rank1 Seq → RRF nejvyšší)

# Podle aliasu (jako ORDER BY pocet DESC) — zde alias score
py -X utf8 -c "from mcp_retrieval.retrieval import GTRetriever; r=GTRetriever(); print(sorted(r.search('docker', top_k=5), key=lambda x: x['score'], reverse=True)[:2])"
```

### 11.6 GROUP BY + COUNT — agregace (jako kontingenční tabulka)

```powershell
# Počet entries podle serveru (jako SELECT portal, COUNT(*) FROM ads GROUP BY portal;)
py -X utf8 -c "from mcp_retrieval.retrieval import GTRetriever; r=GTRetriever(); s=r.stats(); print(s['servers'])"
# → {'cnc-tools':14,'mcp-retrieval':59,...} (jako GROUP BY server)

# Počet podle rule (jako GROUP BY company)
py -X utf8 -c "from mcp_retrieval.retrieval import GTRetriever; r=GTRetriever(); print(r.list_rules()[:3])"
# → [{'rule_id':'P9','count':14},...] (jako P9 = nejčastější firma)

# Jen s 2+ výskyty (jako HAVING COUNT(*) >= 2)
py -X utf8 -c "from mcp_retrieval.retrieval import GTRetriever; r=GTRetriever(); print([x for x in r.list_rules() if x['count']>=2][:3])"

# Top podle počtu (jako ORDER BY COUNT(*) DESC LIMIT 5)
py -X utf8 -c "from mcp_retrieval.retrieval import GTRetriever; r=GTRetriever(); print(sorted(r.list_rules(), key=lambda x: x['count'], reverse=True)[:5])"

# Další agregace (jako COUNT(*), MIN(id), MAX(id))
py -X utf8 -c "from mcp_retrieval.retrieval import GTRetriever; r=GTRetriever(); r.load(); print({'celkem':len(r.entries), 'min':'GT-001','max':'GT-108'})"

# Benchmark jako GROUP BY/HAVING — duplicity VCF (jako GROUP BY sha256 HAVING count(*)>1 v SQL_ADOPCE_PLAN S2)
py -X utf8 ML_Ops_edukace\scripts\benchmark_full.py
# → MRR 0.7067, Prec@3 0.6733 (jako SELECT COUNT(*) FROM pipeline_runs GROUP BY profile)
```

### 11.7 UPDATE + SET — změna stavu (jako `UPDATE ads SET status='applied' WHERE id=7`)

**V retrieval je UPDATE = přidání/úprava entry v `gt_full.jsonl` + re-index.**

```powershell
# Přidání nové entry (jako INSERT — zde ručně do JSONL, pak re-index)
Add-Content ML_Ops_edukace\data\gt_full.jsonl '{"id":"GT-109","symptom":"Nový timeout v P0","root_cause":"b=0.75 penalizuje dlouhé MD","fix":"b=0.25 nebo chunk 512","server":"mcp-local-server","rule":"P99","tags":["timeout"]}'
py -X utf8 -c "from mcp_retrieval.retrieval import GTRetriever; r=GTRetriever(data_dir='ML_Ops_edukace/data'); r.load(); print(r.stats())"
# → total_entries 109 (jako RETURNING id, title, status)

# Hromadně (jako WHERE company='T-Mobile') — zde batch fix 19/30 root_cause
py -X utf8 ML_Ops_edukace\scripts\fix_root_cause.py  # opraví "see source" → plný root_cause (jako UPDATE ... WHERE root_cause LIKE 'see source')
# → Opraveno 19/30, zbývá 11 (jako UPDATE 19)

# Pravidlo: UPDATE bez WHERE změní vše — v retrieval: `reindex` bez filtru přegeneruje vše (render_md.py)
py -X utf8 ML_Ops_edukace\scripts\render_md.py  # generuje gt_catalog_full_render.md (jako materialized view)
```

### 11.8 Transakce — bezpečné zkoušení (jako `BEGIN; ... ROLLBACK;`)

```powershell
# Dry-run v TEMP (jako BEGIN; UPDATE ...; ROLLBACK; — nic se nezměnilo v zdrojáku)
py -3 TEMP_workflow_sim\P0_DRY_RUN\benchmark.py  # 121 docs, 10 dotazů, MRR +13.5% — vše v tempu, mcp-local-server zůstává clean
# → BEGIN (temp) → BM25 fit 452ms → benchmark → ROLLBACK (smazáním TEMP) nic v produkci

# Commit (jako COMMIT; — až po ověření)
# Po ověření v tempu: ruční P0 do mcp-local-server/tools/kb_search.py (jako COMMIT po 1 session)
# Práh zastavení S2 (SQL_ADOPCE_PLAN §4): pokud KROK 0 přesáhne 1 session → redukce na FTS5-path index

# SAVEPOINT — záchytný bod (jako SAVEPOINT bod1; ... ROLLBACK TO SAVEPOINT bod1;)
# V retrieval: git stash před P0, pak git stash pop pokud MRR <0.65
git stash push -m "pred P0"
# ... P0 implementace ...
py -X utf8 mcp-local-server\scripts\test_kb_search.py  # test
git stash pop  # nebo git reset --hard
```

### 11.9 DELETE — mazání (s opatrností)

```powershell
# Smaž entry (jako DELETE FROM ads WHERE id=7;)
# V JSONL: odfiltruj GT-109
py -X utf8 -c "import pathlib, json; p=pathlib.Path('ML_Ops_edukace/data/gt_full.jsonl'); lines=[l for l in p.read_text(encoding='utf-8').splitlines() if '\"GT-109\"' not in l]; p.write_text('\n'.join(lines)+'\n', encoding='utf-8'); print('smazano GT-109')"
# Vrať smazané (jako RETURNING)
py -X utf8 -c "from mcp_retrieval.retrieval import GTRetriever; print(len(GTRetriever().entries))"  # → 108

# Bezpečně: DELETE bez WHERE smaže VŠE — vždy WHERE id. Pro jistotu v transakci (TEMP)
# DRY-RUN: SELECT COUNT(*) FROM ads WHERE profile='default'; (jako ověření před DELETE)
py -X utf8 -c "from mcp_retrieval.retrieval import GTRetriever; r=GTRetriever(); print(len([e for e in r.entries if e['server']=='gcp']))"  # → 5 (ověř před mazáním gcp)
```

### 11.10 Práce s pipeline_runs (JSONB analog — `gt_rules.json` + `benchmark_results.json`)

```powershell
# Všechny běhy (jako SELECT * FROM pipeline_runs;)
Get-Content ML_Ops_edukace\results\ensemble_benchmark.json | ConvertFrom-Json | Select-Object -ExpandProperty mrr
# → 0.7067

# JSONB: hodnota z metadata (jako metadata->>'new_ads')
py -X utf8 -c "import json, pathlib; j=json.loads(pathlib.Path('ML_Ops_edukace/results/ensemble_benchmark.json').read_text(encoding='utf-8')); print(j['hits'])"
# → 43/50

# Počet běhů na profil (jako GROUP BY profile)
py -X utf8 -c "import json, pathlib, collections; d=json.loads(pathlib.Path('TEMP_workflow_sim/P0_DRY_RUN/results/benchmark_results.json').read_text(encoding='utf-8')); print(d['baseline']['hits'], d['p0']['hits'])"
# → 8/10 vs 7/10
```

### 11.11 Kontrolní otázky (jako `postgresql_zakladni_prikazy` §11 — ověř, že rozumíš)

| Otázka | Odpověď (retrieval analog) |
|--------|----------------------------|
| Jak najdeš všechny GT entry s `timeout`? | `py -X utf8 -c "from mcp_retrieval.retrieval import GTRetriever; print([e['id'] for e in GTRetriever().entries if 'timeout' in e['symptom'].lower()])"` nebo `retrieve.py "timeout"` |
| Jak najdeš entry obsahující `encoding` NEBO `cp1250`? | `r.search("encoding cp1250", top_k=3)` — BM25 OR (jako `title ILIKE '%encoding%' OR description ILIKE '%cp1250%'`) |
| Kolik GT entries máš celkem? | `r.stats()['total_entries']` → 108 (jako `COUNT(*) FROM ads`) |
| Který server má nejvíc entries? | `sorted(r.stats()['servers'].items(), key=lambda x: x[1], reverse=True)[0]` → `mcp-retrieval 59` (jako `GROUP BY server ORDER BY COUNT(*) DESC LIMIT 1`) |
| Jak přidáš entry a ověříš? | `Add-Content gt_full.jsonl '{...}'` + `GTRetriever().load(); print(stats())` (jako `INSERT ... RETURNING`) |
| Jak zrušíš změnu, kterou sis omylem udělal? | Transakce: `git stash` / `TEMP` dry-run `ROLLBACK` (před `COMMIT` do `mcp-local-server`) |
| Jak najdeš `MLOps` NEBO `pipeline`? | `retrieve.py "MLOps pipeline"` — BM25 `IDF(MLOps)` vysoké (df 2), `pipeline` df nízké → rankuje `MLOps` výše |
| Jak zjistíš, co je v korpusu za sloupce? | `r.entries[0].keys()` → `id, symptom, root_cause, fix, server, rule, tags` (jako `\d ads`) |
| Jak zrušíš jen část změn? | `SAVEPOINT` — `git stash push` před `b=0.75→0.25`, `git stash pop` pokud MRR klesne |
| Jak ukončíš interactive? | `quit` / `exit` / `Ctrl+C` v `retrieve.py --interactive` (jako `\q` v psql) |
| Jak zjistíš počet docs per module? | `py -3 -c "import pathlib; kb=pathlib.Path('B2B-Knowledge-Base'); print({m: len(list((kb/m).rglob('*.md'))) for m in ['00_STRATEGIE','01_METODIKY','02_ANALYZY']})"` (jako `COUNT(*) GROUP BY module`) |
| Jak ověříš `b` param? | `py -3 TEMP.../benchmark.py` s `b=0.25 vs 0.75` (jako `\timing` + `EXPLAIN ANALYZE`) |

### 11.12 Pravidla pro práci (jako `postgresql_zakladni_prikazy` §12)

1. **Vždy `top_k`** u `r.search` — jinak 108 výsledků (jako `SELECT *` bez `LIMIT`).
2. **Transakce = TEMP** — `TEMP_workflow_sim/P0_DRY_RUN` chrání produkci (jako `BEGIN; ... ROLLBACK;`).
3. **Středník `;` v SQL → `top_k` v retrieval** — zapomeneš-li `top_k`, vrátí 5 default (jako `LIMIT`).
4. **`\q` v psql → `quit` v `retrieve.py --interactive`** — pager vypnut, nic neblokuje.
5. **Data jsou reálná** — 108 GT, 121 KB docs — `MRR` po experimentu ověř (`benchmark_results.json`).
6. **`WHERE` nevidí agregace, `HAVING` ano** — v retrieval: `WHERE count>5` selže, `HAVING COUNT(*)>5` (jako `GROUP BY sha256 HAVING count(*)>1` v `SQL_ADOPCE_PLAN S2`).
7. **`NULL` není 0** — `IS NULL` / `COALESCE` (v JSONL: chybějící `root_cause` → `"see source"`).
8. **`--interactive` neblokuje** — `pager=off` analog, `Ctrl+C` ukončí.

---

---

## 12. Teze „Trénujeme minimální ML model BM25“ — verifikace a formalizace (P0 jako příklad)

**Teze autora (subjektivní, k ověření):** „Trénujeme vlastní minimodel ML → POC ML pipeline (P0). BM25 má `k1/b/k + SYNONYM_MAP`, ladíme je, žádní neuroni.“

### 12.0 Co je ML model obecně (definice, bez mýtu neuronů)

**ML model = funkce `f(x; θ) → y` s parametry `θ` odvozenými z dat `D`, hodnocená metrikou `M`, laditelná hyperparametry `λ`, schopná generalizace na `x` mimo `D`.**

| Složka | Příklad NN (hluboký) | Příklad BM25 (minimální) | Shoda s definicí |
|--------|----------------------|--------------------------|------------------|
| **Data `D`** | `108 GT entries` (texty) | `108 GT entries` (texty) + `121 KB docs` | Ano — `D` je archiv `_github` (md, json, docx) |
| **Parametry `θ` (naučené)** | `váhy W` (miliony, gradient descent) | `df` (document frequency per term), `avg_dl`, `inverted_index` (posting lists) — odvozeno `BM25.fit(docs)` (`mcp-retrieval/retrieval.py:52-64` `df[term]+=1`, `inv[term].append`) | Ano — `θ` je statistika korpusu, ne váhy |
| **Hyperparametry `λ` (laděné člověkem)** | `learning_rate, layers, dropout` | `k1=1.5, b=0.75, k=60` (`retrieval.py:47`) + `SYNONYM_MAP 12` (`retrieval.py:78`) + `window 4000` + `tokenize à-ž` | Ano — ladíme `k1/b/k` grid `k1 0.8-2.0, b 0.3-0.9` (Arpit, Elastic), jako `learning_rate` |
| **Vstup `x`** | `query` + `doc` | `query` (`timeout v MCP serveru`) + `doc` (`GT-001`) | Ano |
| **Výstup `y`** | `score` / `rank` | `BM25 score` (`retrieval.py:73-88` `TF*(k1+1)/(TF+k1*(1-b+b*dl/avg)) * IDF`) + `RRF` rank | Ano |
| **Metrika `M`** | `accuracy, F1` | `MRR, Prec@3, Recall, Hits` (`EVALUATION.md:41` MRR 0.7067) | Ano |
| **Neurony** | `perceptron` (`y = σ(W·x + b)`) | **Žádné** — `BM25` je `bag-of-words` probabilistický (`Robertson & Jones 1976`), ne `perceptron` | Není potřeba — neurony jsou jen 1 druh `θ` (nelineární `σ`) |

**Verdikt teze 1:** **Korektní s nuancí.** BM25 je **minimální statistický ML model** (široká definice ML: `učení z dat → parametrizovaná funkce → evaluace`). Není to **hluboký neuronový model** (úzká definice ML = `NN`). Proto „minimodel“ sedí: 0 neuronů, 3 hyperparametry `k1/b/k` + 12 synonym, `fit` odvodí `θ = {df, avg_dl, inv}` z `D` (jako `Word2Vec` by trénoval `W` z 108 entries — selhalo 0.31 MRR). Ladíme `λ`, ne `θ` gradientem — to je **hyperparam tuning** (grid search), ne `backprop`, ale stále MLops (jako `MCP-Jobs` ladí `weights tech 0.25/domain 0.35`).

**Proč bez neuronů:** Neurony jsou potřeba pro `dense` sémantiku (`embedding` 384D → `cosine` → `HNSW`), kde `W` kóduje `latent space`. BM25 je `sparse` lexikální — nepotřebuje `W`, stačí `TF*IDF` + `length_norm` (jako `TF-IDF` na `numpy` v `Cesta A`). Proto `Cesta B` 580MB (`sentence-transformers`) přidá neurony, `Cesta A` 0B ne — a na 108 entries `Cesta A+RRF` vyhrává (0.7067 vs `GloVe` 0.26, `SVD` 0.54).

**Proč ladíme `k1/b/k + SYNONYM_MAP`:** `k1` řídí **saturaci TF** (`f=0→0, f=1→0.6, f=10→0.95` s `k1=1.5` — Arpit), `b` řídí **length_norm** (`dl/avg_dl` pro KB 64KB vs 7KB), `k=60` řídí **RRF ostrost** (`k=10` 30% dif vs `k=60` 14% pro N=121), `SYNONYM_MAP` je **ruční embedding** (`timeout→deadlock` jako `GloVe` 300D, ale 0B). Vše je `λ` — ladíme `MRR` na `test_queries.json` (25×50), jako `learning_rate` ladí `accuracy`.

### 12.1 Teze deva „Nejdřív kalibrovat model, pak měnit data“ — verifikace (cause/effect)

**Teze autora (subjektivní):** „Jelikož je POC edukativní, musíme nejdřív kalibrovat/trénovat model, teprve pak lze teoreticky měnit tréninková data (`_github` 207 souborů md/json/docx) do přijatelného formátu. Ale možná je ML princip opačný: data zůstávají originální, trénujeme model, aby zlepšil `MRR` — nelze invertovat příčinu/následek (měnit data aby pipeline lépe zpracovala).“

**Verifikace — obě části jsou částečně pravdivé, ale ML rozlišuje 3 vrstvy:**

| Vrstva | Co | Příklad v našem P0 | Měnit? | ML princip |
|--------|----|--------------------|--------|------------|
| **1. Raw data `D` (ground truth)** | Originální archiv `_github` (207 md/json, 35 VCF) — neměnné, `K0 Orákulum` (`RETRIEVAL_RESEARCH.md:6` CPM) | `GT 118KB md` (118592 B) → `gt_full.jsonl` 59KB (-49% komprese) — `D` jako zdroj, ne cíl | **Ne** (kromě dedup) | `D` je `orákulum` — ground truth pro `MRR` (25 queries). Invertovat `D` aby `M` stouplo je **data leakage** (p-hacking). `P0_DRY_RUN` ukázal `ACI` rank None i po `win 2000-full` — vina není `D`, ale `λ` (`b=0.75` penalty). |
| **2. Feature engineering `Φ(D)` (reprezentace)** | `tokenize à-ž`, `window 4000`, `chunk 512`, `stopwords cs`, `czech stem` (`kalibrace→kalibrac`), `lower` | `content[:4000]` vs `content` full (P0_DRY_RUN: `kalibrace in 4000=False` pro 3 expected → `window` → `chunk`) | **Ano** — to je kalibrace **reprezentace**, ne `D` | `Φ(D)` je `transform` (`ETL` `T` = Transform) — měnit `Φ` aby `M` stouplo je **feature engineering** (jako `SQL` `ILIKE` vs `~*` regex, `postgresql_zakladni_prikazy §4`). |
| **3. Model `f` + `λ`** | `BM25(k1/b)`, `RRF(k)`, `SYNONYM_MAP` | `k1 1.5→1.2, b 0.75→0.25, k 60→20` ( `P0_IMPROVEMENT_PROPOSAL_v1.md:3` ) | **Ano** — to je kalibrace **modelu** | `λ` ladíme grid search `k1 0.8-2.0, b 0.3-0.9` (Elastic, Trotman) na `MRR`. |

**Princip ML (bez inverze):**
- **Data `D` zůstávají originální** (raw md/json) — neměníme `D` aby `MRR` stouplo (to by bylo `data dredging`). Měníme `Φ(D)` a `λ` aby `f(Φ(D); θ, λ)` lépe mapovalo `D` na `y` (rank). To je **cause `D` → effect `M` přes `Φ` a `f`**, ne obráceně.
- **Ale `Φ(D)` měnit lze a má se** — `window 4000` vs `full` (P0_DRY_RUN: `kalibrace` za 4000 → chunk 512 fix), `tokenize à-ž` vs `+czech stem` (B3), `stopwords` (B4) — to není `D`, ale `feature`.
- **Edukační POC pořadí:** `D` fix → `Φ` + `f` kalibrace na `MRR` (EVALUATION 50 queries) → **pak** lze uvažovat `D` augmentaci (11 `see source` → plný `root_cause` via `fix_root_cause.py` — to je `D` čištění, ne `D` falšování, a `EVALUATION.md:9` 19/30 opraveno).

**Příklad P0:** `ACI kalibrace` rank None na `b=0.75` i `b=0.0` → `D` ( `executive_summary` ACI 12 vs `VCF_Reverse` ACI 6 ) je správný, `MRR` nízké kvůli `expected` kurátorství (B1) + `Φ` (window) — ne `D`. Oprava: `Φ` (chunk) + `λ` (`b=0.25`), ne `D` (`executive_summary` nemazat).

**Verdikt teze 2:** **Korektní s doplněním.** Ano, nejdřív kalibruj `f`/`λ` + `Φ(D)` na fixním `D` (jako `SQL` nejdřív `SELECT`/`JOIN` na existující DB `S1` v `SQL_ADOPCE_PLAN_2026-08-16.md:42`, pak teprve `DDL` `S6`). Ne, neměň `D` aby `MRR` stouplo — měň `Φ` (tokenizace, window, chunk) a `λ` (k1/b/k). `D` měň jen čištěním (`see source`).

### 12.2 Shrnutí — proč teze sedí (PBL)

- **Minimodel BM25:** 0 neuronů, 3 `λ` + 12 synonym, `θ` = `df/avg_dl/inv` z `D` → `MRR` 0.7067 (+6.9% vs `score=sum` 0.6613) — P0 je **POC ML pipeline** (data→fit→search→RRF→eval→tune) jako `EVALUATION.md:112` 8 kroků 0B.
- **Cause/effect:** `D` (orákulum) → `Φ(D)` + `f` (kalibrace) → `M` (MRR) — ne `M` → `D`. Proto `P0_IMPROVEMENT_PROPOSAL I1-I4` nejdřív `k1/b/k` + `stem` (Φ/f), pak `D` (11 `see source`).

---

*Výzkumná zpráva + implementační plán. Vítěz: BM25+Seq RRF (MRR=0.7067). Exp+Seq RRF (Prec@3=0.6867).*
*PBL princip: Autor řeší vlastní problém a současně si osvojuje ontologii z oblasti ML ops / AI dev.*

