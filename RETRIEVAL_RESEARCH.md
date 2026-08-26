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
| Dense | TF-IDF (numpy) + `fasttext` na Wikipedia subspace | `numpy`, `fasttext` | ~80 MB |
| RRF | 3 řádky kódu | — | 0 B |
| Rerank | TF-IDF rerank (ad-hoc) | — | 0 B |
| **Celkem** | | | **~80 MB** |

**Proč:** Kompromis — fasttext embeddings jsou lepší než TF-IDF, 80MB se vejde do limitu.

---

## 4. DETAILNÍ IMPLEMENTAČNÍ PLÁN (Cesta A: Zero-Download)

### Krok 1: Tokenizace + BM25 (0 B, ~30 min)

**Co:** Implementovat BM25 z Python stdlib.

**Ontologický kontext:**
- **Inverted Index** = pro každý termín seznam dokumentů (naše 108 entries)
- **IDF** = log(N/df) — termín "timeout" je v 5 entries → IDF = log(108/5) = 3.07
- **TF** = četnost termínu v dokumentu — "timeout" se v GT-001 vyskytuje 2× → TF = 2
- **BM25 score** = IDF × TF_upravené × length_normalized

```python
# Pseudokód
class BM25:
    def fit(self, docs):     # docs = [tokenized_entry_1, ...]
        self.inverted_index = {}  # term → [(doc_id, tf), ...]
        self.doc_lens = [len(d) for d in docs]
        self.avg_dl = mean(self.doc_lens)
    
    def search(self, query, top_k=5):
        scores = defaultdict(float)
        for term in query:
            if term in self.inverted_index:
                idf = log(N / df[term])
                for doc_id, tf in inverted_index[term]:
                    scores[doc_id] += idf * tf_uprated(tf, k1, b, dl, avg_dl)
        return sorted(scores.items(), key=-score)[:top_k]
```

### Krok 2: TF-IDF Dense (0 B, ~30 min)

**Co:** Implementovat TF-IDF jako "dense" náhradu.

**Ontologický kontext:**
- **Embedding** = vektor v N-dimenzionálním prostoru (N = velikost slovníku)
- **TF-IDF vektor** = každá dimenze = jeden termín, hodnota = TF × IDF
- **Cosine similarity** = dot produkt dvou L2-normalizovaných vektorů
- **Dense vs Sparse:** TF-IDF je technicky sparse (většina dimenzí = 0), ale funguje jako dense pro similarity

```python
# Pseudokód
class TFIDFEmbedding:
    def fit(self, docs):
        self.vocab = sorted(set(term for doc in docs for term in doc))
        self.idf = {t: log((N+1)/(df[t]+1))+1 for t in self.vocab}
        self.matrix = zeros((N, len(self.vocab)))  # N entries × vocab_size
        for i, doc in enumerate(docs):
            for term, tf in Counter(doc).items():
                self.matrix[i, vocab_idx[term]] = tf * self.idf[term]
            self.matrix[i] /= norm(self.matrix[i])  # L2 normalize
    
    def search(self, query, top_k=5):
        q_vec = encode_query(query)  # stejný postup
        scores = self.matrix @ q_vec  # cosine similarity
        return top_k by score
```

### Krok 3: RRF Fusion (0 B, ~5 min)

**Co:** Sloučit BM25 + TF-IDF výsledky.

**Ontologický kontext:**
- **Rank Fusion** = sloučení na úrovni pořadí (ne skóre)
- **RRF** = 1/(k+rank) — k=60 = standard, k=30 = favor top-1
- **Scale-invariant** — nezáleží na absolutních skóre, jen na pořadí

```python
def rrf_fusion(results_bm25, results_tfidf, k=60):
    scores = {}
    for rank, (doc_id, _) in enumerate(results_bm25, 1):
        scores[doc_id] = scores.get(doc_id, 0) + 1/(k + rank)
    for rank, (doc_id, _) in enumerate(results_tfidf, 1):
        scores[doc_id] = scores.get(doc_id, 0) + 1/(k + rank)
    return sorted(scores.items(), key=lambda x: -x[1])
```

### Krok 4: Evaluace (0 B, ~20 min)

**Co:** Spustit 25 queries × 2 jazyky přes všechny 4 pipeline.

**Ontologický kontext:**
- **Precision@3** = kvalita top-3 (málo šumu)
- **Recall** = kolik relevantních jsme našli
- **MRR** = jak brzo se první relevantní objeví
- **NDCG** = ranking quality s graded relevance

**Výstup:** `results/hybrid_benchmark.json` — porovnání SequenceMatcher vs BM25 vs TF-IDF vs Hybrid

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

## 7. ROZHODOVACÍ MATRIX

| Scénář | Cesta | Důvod |
|--------|-------|-------|
| POC, žádný internet | **A (Zero-Download)** | 0 B, numpy stačí |
| POC, malý download | **D (FastText)** | 80MB = lepší embeddings |
| Plná kvalita | **B (sentence-transformers)** | 580MB, nejlepší open-source |
| Plná kvalita + API | **C (OpenAI)** | 0 download, nejlepší celkově |
| Produkce | **B + CI/CD monitoring** | MLOps, A/B test, drift detection |

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

## 10. NEXT STEPS (po schválení autorem)

| # | Krok | Cesta | Download | Čas |
|---|------|-------|----------|-----|
| 1 | Tokenizace + BM25 z stdlib | A | 0 B | 30 min |
| 2 | TF-IDF na numpy | A | 0 B | 30 min |
| 3 | RRF fusion | A | 0 B | 5 min |
| 4 | Benchmark (SequenceMatcher vs BM25 vs TF-IDF vs Hybrid) | A | 0 B | 20 min |
| 5 | Aktualizace EVALUATION.md | A | 0 B | 10 min |
| 6 | (Volitelné) FastText embeddings | D | 80 MB | +30 min |
| 7 | (Volitelné) sentence-transformers + cross-encoder | B | 580 MB | +60 min |

---

*Výzkumná zpráva + implementační plán. Všechny termíny jsou cross-ref s MCP-Jobs skills catalog (94 skills) a interní KB (CPM, RE_Methodology, ontologie).*
*PBL princip: Autor řeší vlastní problém a současně si osvojuje ontologii z oblasti ML ops / AI dev.*
