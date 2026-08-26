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
| **MMR** (Maximal Marginal Relevance) | Re-ranking pro diverzitu. Upřednostňuje dokumenty, které jsou relevantní A odlišné od již vybraných. | `λ * sim(d,q) - (1-λ) * max(sim(d,d'))` | Můžeme přidat jako bonus |
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
| 9 | Opravit 30 entries s "see source" root_cause | - | 0 B | Čeká na autorizaci |
| 10 | Produkční implementace (API endpoint) | - | 0 B | Plán |

---

*Výzkumná zpráva + implementační plán. Vítěz: BM25+Seq RRF (MRR=0.7067). Exp+Seq RRF (Prec@3=0.6867).*
*PBL princip: Autor řeší vlastní problém a současně si osvojuje ontologii z oblasti ML ops / AI dev.*
