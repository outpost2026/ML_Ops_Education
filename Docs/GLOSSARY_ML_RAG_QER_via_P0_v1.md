# Glossary — ML/RAG/QER ontologie via P0 (BM25+Seq+RRF)

**Datum:** 2026-08-27 | **Zdroj:** 17 docs retrieved via P0 (BM25+Seq+RRF) | **Korpus:** 121 KB + 14 ML/RAG/QER = 135 docs
**Metriky:** MRR 0.5238 Prec@3 0.381 Recall 0.5714 Hits 6/7
**Dotazy:** 7 (ML RAG QER ontologie) — `ONTO_Q0` original + 6 inferred QER/RTF/RAG

## Zdroje (retrieved top5 per query, dedup)

- `ML_Ops_edukace/RETRIEVAL_BOTTLENECK_ANALYSIS_v1.md`
- `ML_Ops_edukace/README.md`
- `01_METODIKY/06_SWE_glossary/SWE_GLOSSARY_zive_v1.md`
- `ML_Ops_edukace/RETRIEVAL_RESEARCH.md`
- `01_METODIKY/04_skill_acquisition/ADOPCNI_METODOLOGIE_2026_v1.md`
- `ML_Ops_edukace/MCP_ECOSYSTEM_ADAPTATION_v1.md`
- `02_ANALYZY/03_kodove_analyzy/vcf_compiler_architektura_deepdive.md`
- `01_METODIKY/04_skill_acquisition/AZURE_MIGRACE_PLAN_2026-08-25.md`
- `00_STRATEGIE/01_positioning/SQL_ADOPCE_PLAN_2026-08-16.md`
- `README.md`
- `05_EPISTEMIKA/00_kompresni_realismus/Kompresni_modelovani_v_praxi_synteza_v1.md`
- `05_EPISTEMIKA/01_kalibracni_matice/kalibracni_matice.json`
- `05_EPISTEMIKA/00_kompresni_realismus/Brain as a Geometric Processor - Appendix v1.1 (Thermodynamic Upgrade).md`
- `05_EPISTEMIKA/00_kompresni_realismus/ontologie_kompresnich_modelu_reality_appendix.md`
- `05_EPISTEMIKA/03_kognitivni_ontologie_nastroju/POSTGRESQL_ontologie_epistemika_2026-08-18.md`
- `05_EPISTEMIKA/03_kognitivni_ontologie_nastroju/IT_gramotnost_hranice_SQL_databazi_2026-08-15.md`
- `AGENTS.md`

## Glossary — ontologie ML/RAG/QER

| Term | Definice (zkráceně) | Zdroj |
|------|---------------------|-------|
| ***Vytvořeno: 2026-08-27** | *Vytvořeno: 2026-08-27   Zdroj: syntéza 5 originálních artefaktů + nový výzkum 2 | `MCP_ECOSYSTEM_ADAPTA` |
| **0 Cache** |   **0 Cache**   `@cached(ttl_seconds=300)` (`kb_search.py:10`, `cache.py:8`) + ` | `MCP_ECOSYSTEM_ADAPTA` |
| **1 BM25** |   **1 BM25**   `TF * IDF * length_norm` (`retrieval.py:45-55`) `k1=1.5` saturuje | `MCP_ECOSYSTEM_ADAPTA` |
| **2 Fuzzy** |   **2 Fuzzy**   `SequenceMatcher(None,q,t[:300]).ratio()` (`retrieval.py:128`)   | `MCP_ECOSYSTEM_ADAPTA` |
| **2 Unit** |   2 Unit   `.venv/Scripts/python -m pytest mcp-local-server/tests/ -k kb_search  | `MCP_ECOSYSTEM_ADAPTA` |
| **3 RRF** |   **3 RRF**   `score=Σ 1/(60+rank)` (`retrieval.py:136`)   BM25 a Seq mají jiné  | `MCP_ECOSYSTEM_ADAPTA` |
| **4 Citation** |   **4 Citation**   `kb_read_doc(path)` (`kb_read_doc.py:10`) + `INDEX.md` metada | `MCP_ECOSYSTEM_ADAPTA` |
| **ANN** |   **ANN**   Přibližné nejbližší sousedy   "Nemusíme najít přesně nejlepší, stačí | `RETRIEVAL_RESEARCH.m` |
| **ANN (Approximate Nearest Neighbors)** |   **ANN** (Approximate Nearest Neighbors)   Algoritmus pro rychlé hledání nejbli | `RETRIEVAL_RESEARCH.m` |
| **BM25** |   **BM25**   (implicitní v `NLP`)   —   "Full-text search, information retrieval | `RETRIEVAL_RESEARCH.m` |
| **BM25 (Best Matching 25)** |   **BM25** (Best Matching 25)   Probabilistický retrieval model, založený na TF- | `RETRIEVAL_RESEARCH.m` |
| **Bi-encoder** |   **Bi-encoder**   Model, který encoduje query a dokument nezávisle. Rychlejší,  | `RETRIEVAL_RESEARCH.m` |
| **Datum: 2026-07-28** | **Datum:** 2026-07-28   **Autor:** outpost2026 + LLM (falsifikační test) | `Kompresni_modelovani` |
| **Datum: 2026-08-27** | **Datum:** 2026-08-27   **Autor:** outpost2026 (LLM hloubková analýza)   **Verze | `RETRIEVAL_BOTTLENECK` |
| **Dense** |   Dense   TF-IDF na numpy (hand-written)   `numpy` (už máme)   0 B   | `RETRIEVAL_RESEARCH.m` |
| **Embedding** |   **Embedding**   Vektorová reprezentace   Převod textu na čísla tak, aby podobn | `RETRIEVAL_RESEARCH.m` |
| **Embedding (vektorová reprezentace)** |   **Embedding** (vektorová reprezentace)   K-dimenzionální vektor zachycující sé | `RETRIEVAL_RESEARCH.m` |
| **Embeddings** |   Embeddings   AI_CONCEPT   0.50   TF-IDF jako náhrada   | `README.md` |
| **HNSW** |   **HNSW**   Hierarchický navigovatelný malý svět   Graf pro rychlé hledání v mi | `RETRIEVAL_RESEARCH.m` |
| **Hybrid Search** |   **Hybrid Search**   (implicitní v `vector_db`)   —   "Hybrid search, RRF fusio | `RETRIEVAL_RESEARCH.m` |
| **Inverted Index** |   **Inverted Index**   Datová struktura: pro každý termín seznam dokumentů, kde  | `RETRIEVAL_RESEARCH.m` |
| **Jak najdeš `MLOps` NEBO `pipeline`?** |   Jak najdeš `MLOps` NEBO `pipeline`?   `retrieve.py "MLOps pipeline"` — BM25 `I | `RETRIEVAL_RESEARCH.m` |
| **K1 Detektor** |   **K1 Detektor**   BM25/TF-IDF skóre může být chybné   Cross-validation, A/B te | `RETRIEVAL_RESEARCH.m` |
| **K3 Dekodér** |   **K3 Dekodér**   LLM může špatně interpretovat retrieved chunks   Reranking, m | `RETRIEVAL_RESEARCH.m` |
| **Koncept mapy = otrava** |   **Koncept mapy = otrava**   Střední   Nízký   Mermaid diagramy generované LLM, | `ADOPCNI_METODOLOGIE_` |
| **Kritérium** |   Kritérium   Vector 1 (VCF Optimalizátor)   Vector 2 (Deep RE)   | `vcf_compiler_archite` |
| **LLM** |   **LLM**   `IT_SKILL`   0.60   "Velké jazykové modely, LLMOps"   | `RETRIEVAL_RESEARCH.m` |
| **LLM context** |   LLM context   100%   ~9%   **91% redukce**   | `RETRIEVAL_RESEARCH.m` |
| **Latent space** |   **Latent space**   Prostor, ve kterém jsou embeddings reprezentovány. Dimenze  | `RETRIEVAL_RESEARCH.m` |
| **MLOps** |   MLOps   METHODOLOGY   0.50   Benchmark pipeline   | `README.md` |
| **MMR (Maximal Marginal Relevance)** |   **MMR** (Maximal Marginal Relevance)   Re-ranking pro diverzitu. Upřednostňuje | `RETRIEVAL_RESEARCH.m` |
| **NLP** |   NLP   AI_FIELD   0.45   BM25, TF-IDF   | `README.md` |
| **Nejlepší výsledek** |   **Nejlepší výsledek**   **BM25+Seq RRF**   **0.7067**   Poprvé poráží Sequence | `RETRIEVAL_RESEARCH.m` |
| **PBL přepisování LLM kódu bez pochopení** |   **PBL přepisování LLM kódu bez pochopení**   Střední   Vysoký   Anti-blackbox: | `ADOPCNI_METODOLOGIE_` |
| **POC, žádný internet** |   POC, žádný internet   A (Zero-Download)   0.6397   0 B, BM25 stačí   | `RETRIEVAL_RESEARCH.m` |
| **Posting List** |   **Posting List**   Seznam dokumentů obsahujících daný termín + pozice. Základ  | `RETRIEVAL_RESEARCH.m` |
| **Produkce** |   Produkce   **BM25+Seq RRF + CI/CD**   0.7067   MLOps, A/B test, drift detectio | `RETRIEVAL_RESEARCH.m` |
| **RAG** |   RAG   IT_SKILL   0.50   Retrieval pipeline   | `README.md` |
| **RRF** |   RRF   3 řádky kódu   `dict`   0 B   | `RETRIEVAL_RESEARCH.m` |
| **RRF (Reciprocal Rank Fusion)** |   **RRF** (Reciprocal Rank Fusion)   Algoritmus pro sloučení dvou ranked listů.  | `RETRIEVAL_RESEARCH.m` |
| **Re-ranker** |   **Re-ranker**   Obecný termín pro model, který přehodnotí pořadí kandidátů z p | `RETRIEVAL_RESEARCH.m` |
| **Rerank** |   Rerank   BM25 score jako proxy   —   0 B   | `RETRIEVAL_RESEARCH.m` |
| **Retrieval metrik: BM25+Seq RRF** |   Retrieval metrik: BM25+Seq RRF   **0.7067 MRR** (vítěz)   | `README.md` |
| **S2 KROK 0** |   **S2** KROK 0   **Master dir index SQLite+FTS5** — 1 schema + 1 crawler + 5 an | `SQL_ADOPCE_PLAN_2026` |
| **SQLite + FTS5 (MATCH, BM25)** |   **SQLite + FTS5** (MATCH, BM25)   **NEOVČIČENO**   KROK 0 (V3 revize)   | `SQL_ADOPCE_PLAN_2026` |
| **SRS opuštěno po 2 týdnech** |   **SRS opuštěno po 2 týdnech**   Vysoká   Střední   Autonomie: 10 min/den fixní | `ADOPCNI_METODOLOGIE_` |
| **Stack** |   **Stack**   Markdown, JSON, Git, RAG-ready struktura, agentní přístup přes ope | `README.md` |
| **TF-IDF** |   **TF-IDF**   (implicitní v `NLP`)   —   "Text preprocessing, feature extractio | `RETRIEVAL_RESEARCH.m` |
| **Vector Database** |   Vector Database   AI_TOOL   0.45   numpy matrix   | `README.md` |
| **Verze: 1.0** | **Verze:** 1.0   **Datum:** 2026-07-18   **Účel:** Jediný zdroj pravidel pro LLM | `AGENTS.md` |
| **Vlastnost / Režim** |   Vlastnost / Režim   Uhlíkový mozek (20W)   Statické LLM (Křemík)   Hybridní B2 | `Brain as a Geometric` |
| **Weighted Score Fusion** |   **Weighted Score Fusion**   Lineární kombinace: `α * score_bm25 + (1-α) * scor | `RETRIEVAL_RESEARCH.m` |
| **`BM25+Seq RRF`** |   `BM25+Seq RRF`   **0.7067**   **0.6883**   0.6733   **43/50**   **Vítěz MRR**  | `MCP_ECOSYSTEM_ADAPTA` |
| **`BM25`** |   `BM25`   0.6397   0.6617   0.5967   40/50   +4.5% Recall   Keyword recall lepš | `MCP_ECOSYSTEM_ADAPTA` |
| **`Exp+Seq RRF`** |   `Exp+Seq RRF`   0.7067   0.6933   **0.6867**   43/50   **Vítěz Prec@3**   Syno | `MCP_ECOSYSTEM_ADAPTA` |
| **`MCP-Jobs/skills_config.json`** |   `MCP-Jobs/skills_config.json`   94 skills, 146 aliasů, váhy `MLOps 0.50`   `sk | `MCP_ECOSYSTEM_ADAPTA` |
| **`MLOps pipeline` (CZ/EN)** |   `MLOps pipeline` (CZ/EN)   `score 1` pro `MLOps` jen v `skills_config.json`, 0 | `MCP_ECOSYSTEM_ADAPTA` |
| **`ML_Ops_edukace/EVALUATION.md`** |   `ML_Ops_edukace/EVALUATION.md`   12 tabulek, vítěz `BM25+Seq RRF`, neúspěchy ` | `MCP_ECOSYSTEM_ADAPTA` |
| **`ML_Ops_edukace/retrieve.py`** |   `ML_Ops_edukace/retrieve.py`   `BM25` class, `SYNONYM_MAP`, `rrf_fusion` 180 ř | `MCP_ECOSYSTEM_ADAPTA` |
| **`MMR λ=0.7`** |   `MMR λ=0.7`   0.5987   0.6183   0.5467   37/50   Zhoršuje   Diverzita až pro > | `MCP_ECOSYSTEM_ADAPTA` |
| **`encoding problem Windows`** |   `encoding problem Windows`   `score 2` pro `přehrada.md` (obsahuje `problem`), | `MCP_ECOSYSTEM_ADAPTA` |
| **`mcp-retrieval/retrieval.py`** |   `mcp-retrieval/retrieval.py`   `GTRetriever`, `BM25(k1=1.5,b=0.75)`, `SYNONYM_ | `MCP_ECOSYSTEM_ADAPTA` |
| **`timeout v MCP serveru`** |   `timeout v MCP serveru`   `score 1` pro `MCP_GROUND_TRUTH_postmortem_agregovany_v2.md` (obsahuje `tim | `MCP_ECOSYSTEM_ADAPTA` |
| **`tool_kb_search`** |   `tool_kb_search`   `kb_search.py:38,60` `score=sum(1 for w in words if w in co | `MCP_ECOSYSTEM_ADAPTA` |
| **scikit-learn** |   scikit-learn   ML_FRAMEWORK   0.40   (volitelné pro TF-IDF)   | `README.md` |

## Poznámka PBL
Glosář je syntéza z retrieved docs, ne ruční výběr — `via base` = `score=sum` (substring), `via P0` = `BM25+RRF` (IDF+RRF). Rozdíl je v rankingu vzácných `QER/RTF/BM25` (df 2-4) vs častých `LLM/MCP` (df 50+).
