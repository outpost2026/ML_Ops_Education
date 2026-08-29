# ML/AI Engineering Playground
## v2.0 — Ground Truth → Ontologie → Kód → Feynman → PBL → Evidence

**Autor:** Ondřej Soušek / outpost2026  
**Datum:** 2026-08-28  
**Účel:** osobní edukační a rozvojový artefakt pro adopční sprint ML/AI/MLOps  
**Status:** living document / playground  
**Primární projekty:** `ML_Ops_Education`, `MCP-Jobs`, `linkedin-mcp-analyzer`, `B2B-Knowledge-Base`

---

# 0. Východisko a historie

Tento dokument je **v2 korekce** předchozího `ML_AI_MLOps_Education_Playground_v1.0.md`.

Důvod revize byl externí SNR audit. Audit správně identifikoval hlavní nedostatek v1:

> teorie byla vysvětlována, ale nebyla systematicky přivázána ke konkrétnímu kódu a experimentálním výsledkům.

Současně bylo při cross-auditu živého repozitáře zjištěno několik důležitých korekcí:

1. `retrieve.py` skutečně obsahuje vlastní implementaci BM25 i RRF, takže propojení s kódem je možné přes konkrétní řádky.
2. `Sec@3` se v aktuálním `EVALUATION.md` ani `RETRIEVAL_RESEARCH.md` jako standardní metrika nevyskytuje. Nemá být tedy v dokumentu svévolně „definováno“.
3. `TF-IDF` nelze označit za skutečný dense retrieval. Je to stále sparse/lexical reprezentace; SVD/LSA může vytvořit latentní reprezentaci, ale není to totéž jako embedding-based dense retrieval.
4. `BM25` je korektnější chápat jako **parametrizovaný retrieval/ranking model** z information retrieval. Zda jej nazvat ML závisí na šíři definice ML; pro adopci je důležitější rozumět jeho parametrizaci a evaluaci než spor o nálepku.

Živý stav repa `ML_Ops_Education` nyní obsahuje 108 GT entries, 25 test queries a implementace `retrieve.py`, `ensemble_retrieval.py`, `mmr_retrieval.py`, `hybrid_retrieval.py` a další experimentální varianty. citehttps://github.com/outpost2026/ML_Ops_Education

---

# 1. Ground Truth autora

## 1.1 Co už je reálně zvládnuté

Existuje praktická zkušenost s:

- Python
- ETL / ingestion
- normalizací
- PostgreSQL
- Docker
- CI/CD
- MCP
- LLM-assisted engineering
- deterministic testing
- benchmarky
- cloud deploymentem
- retrieval POC

`MCP-Jobs` poskytuje market-side substrate a skills katalog. `ML_Ops_Education` poskytuje experimentální laboratoř, v níž se na vlastním problému osvojuje ML/AI terminologie.

## 1.2 Co zatím nelze vydávat za hlubokou znalost

Především:

- statistické základy ML,
- information retrieval,
- dense retrieval,
- embeddings,
- evaluation metriky,
- model lifecycle,
- experiment tracking,
- serving,
- monitoring ML systémů,
- Kubernetes / production orchestration,
- hlubší MLOps architektura.

## 1.3 Správná pracovní formulace

> **Základní povědomí + schopnost následovat a rozvíjet implementaci + vznikající ontologie; nyní je potřeba převést terminologii z LLM-mediated knowledge do vlastního mentálního modelu.**

90 % dokumentace repa vytvořené pomocí AI není samo o sobě problém. Problém by vznikl tehdy, kdyby dokumentace byla považována za důkaz porozumění.

---

# 2. Zásadní pravidlo tohoto playgroundu

### Dokumentace není evidence znalosti.

Evidence je:

```text
termín
  ↓
vysvětlení vlastními slovy
  ↓
mechanismus
  ↓
mikropříklad
  ↓
kód
  ↓
měření
  ↓
failure mode
  ↓
vlastní interpretace
```

Proto bude mít každé důležité téma tři vrstvy:

```text
CONCEPT
   ↕
CODE
   ↕
EXPERIMENT
```

---

# 3. Portfolio jako jeden systém

```text
                           JOB MARKET
                               │
                               ▼
                           MCP-Jobs
                              FIND
                               │
                         jobs / skills
                               │
                               ▼
                       LinkedIn Analyzer
                            EVALUATE
                       fit / gap / EROI
                               │
                               ▼
                       ML_Ops_Education
                         LEARN / BUILD
                               │
                  ┌────────────┴────────────┐
                  ▼                         ▼
              retrieval                  ML basics
             experiments                 MLOps basics
                  │                         │
                  └────────────┬────────────┘
                               ▼
                            EVIDENCE
                               │
                               ▼
                         updated skill
                               │
                               └────→ MARKET

                    B2B-Knowledge-Base
                       CALIBRATE
```

Současná architektura portfolia je tedy:

**FIND → EVALUATE → LEARN/BUILD → EVIDENCE → UPDATE**

---

# 4. SKILLS jako stav, nikoli seznam

Pro každý skill sledovat:

```yaml
skill_id:
market_relevance:
candidate_state:
learning_state:
evidence:
confidence:
next_action:
```

Doporučený stav:

```text
0 unknown
1 awareness
2 conceptual
3 guided implementation
4 independent implementation
5 debugging / trade-offs
6 architectural judgment
```

### Příklad

```yaml
skill_id: bm25
candidate_state: 2
learning_state: active
evidence:
  - retrieve.py
  - benchmark
gaps:
  - k1
  - b
  - saturation
  - length_normalization
next_action:
  - implement_toy_bm25
  - parameter_sweep
  - explain_without_llm
```

---

# 5. ML model bez mýtu neuronů

Nejprve úplně mimo neurální sítě.

Model je užitečné chápat jako:

> **funkci, která převádí vstup na výstup podle určitých nastavení / parametrů.**

Obecně:

```text
ŷ = f(x; θ)
```

kde:

- `x` = vstup
- `ŷ` = predikovaný výstup
- `f` = modelová funkce
- `θ` = parametry modelu

Pro supervised learning existuje navíc ground truth:

```text
y = skutečný / očekávaný výstup
```

a model se hodnotí podle rozdílu:

```text
y ↔ ŷ
```

### Důležitý mentální model

```text
REALITY
   ↓
x
   ↓
MODEL
   ↓
ŷ
   ↓
COMPARE WITH y
   ↓
ERROR / METRIC
```

---

# 6. Parametry θ vs. hyperparametry λ

## Parametry θ

Hodnoty, které model získává z dat nebo procesem fitování.

Pro lineární model:

```text
ŷ = w1*x1 + w2*x2 + b
```

tedy například:

```text
θ = {w1, w2, b}
```

## Hyperparametry λ

Nastavení učícího / rankingového procesu.

Příklady:

- learning rate
- batch size
- number of trees
- regularization strength
- BM25 `k1`
- BM25 `b`
- RRF `k`

Schematicky:

```text
λ
 ↓
learning / fitting procedure
 ↓
θ
 ↓
model
```

Ale:

> U jednoduchých retrieval metod není vždy užitečné násilně vnucovat klasický supervised-learning slovník. Důležitější je určit, co se nastavuje předem a co se odvozuje z dat.

---

# 7. Proč `BM25` není „neuronová síť“

BM25 v `retrieve.py` je explicitně parametrizovaný ranking mechanismus.

Živý kód:

```text
BM25.__init__(k1=1.5, b=0.75)
```

je v `retrieve.py` kolem řádků 846–852. Konstrukce indexu a statistik probíhá v `fit()` kolem řádků 854–879. citeturn724011view0

Neexistují zde:

```text
neurons
weights matrix
backpropagation
gradient descent
```

Místo toho je zde:

```text
document tokens
→ df
→ inverted index
→ avg document length
→ ranking formula
```

To je přesně důvod, proč se `ML_Ops_Education` hodí jako první vstup do ML/IR: umožňuje pochopit **modelování bez černé skříňky neuronové sítě**.

---

# 8. TF, DF, IDF

## Term Frequency

```text
TF(t,d) = počet výskytů termu t v dokumentu d
```

## Document Frequency

```text
DF(t) = počet dokumentů obsahujících t
```

## IDF

Intuice:

> běžné slovo je málo informativní; vzácné slovo je informativnější.

V aktuální implementaci je:

```python
idf = math.log((N - df + 0.5) / (df + 0.5) + 1)
```

viz `retrieve.py`, `_idf()`, přibližně řádky 881–889. citeturn724011view0

---

# 9. BM25 — mechanický rozklad

Aktuální implementace používá:

```text
k1 = 1.5
b  = 0.75
```

a počítá:

```text
idf × TF saturation × length normalization
```

Kód:

```python
numerator = tf * (k1 + 1)

denominator = tf + k1 * (
    1 - b + b * dl / avg_dl
)

score += idf * numerator / denominator
```

To je přímo aktuální implementace `retrieve.py` v `_score_doc()`, přibližně řádky 891–920. citeturn724011view0

---

# 10. Co přesně dělá `k1`

`k1` řídí chování saturace term frequency.

Bez saturace:

```text
TF 1 → 2 → 3 → 4 → 5
score
  ↑   ↑   ↑   ↑   ↑
```

S BM25:

```text
TF 1 → 2 → 3 → 4 → 5
score
  ↑    ↗    →    →    →
```

Další opakování termu stále pomáhá, ale jeho marginální efekt klesá.

V aktuálním kódu je `k1` uložen přímo jako atribut instance. citeturn724011view2

---

# 11. Co přesně dělá `b`

`b` ovládá sílu normalizace délky dokumentu.

Součást:

```text
dl / avg_dl
```

znamená:

> je tento dokument kratší nebo delší než průměr?

Intuice:

```text
b = 0
→ délka dokumentu prakticky nehraje roli

b = 1
→ délková normalizace je maximální
```

Aktuální default:

```text
b = 0.75
```

je přímo v `BM25.__init__()`. citeturn724011view0

---

# 12. Co je `k` — a proč je to nebezpečně matoucí

Písmeno `k` může označovat **zcela různé věci**.

## BM25

```text
k1
```

→ saturace TF.

## Precision@k

```text
k
```

→ počet prvních výsledků, které evaluujeme.

## RRF

```text
k
```

→ konstanta v:

```text
1 / (k + rank)
```

V aktuálním `retrieve.py` je RRF:

```python
def rrf_fusion(results_list, k=60):
```

a skóre:

```python
scores[doc_idx] += 1.0 / (k + rank)
```

přibližně řádky 1071–1085. citeturn724011view1

### Mentální pravidlo

```text
k1_BM25
≠
k_Precision
≠
k_RRF
```

Stejný symbol neznamená stejnou proměnnou.

---

# 13. RRF — co se skutečně děje v projektu

Aktuální engine vytváří tři rankingy:

```text
1. BM25(query)
2. BM25(expanded query)
3. fuzzy / SequenceMatcher
```

a potom:

```text
RRF
```

Konkrétně `RetrievalEngine.search()`:

```python
res_bm25 = self.bm25.search(...)
res_bm25_exp = self.bm25.search(...)
res_seq = search_fuzzy(...)

rrf_results = rrf_fusion(
    [res_bm25, res_bm25_exp, res_seq],
    k=60
)
```

přibližně řádky 1125–1139. citeturn724011view1

**Důležitá korekce vůči některým starším popisům projektu:** současný `retrieve.py` není BM25 + skutečný vector/dense retriever. Je to BM25 + synonymní query expansion + fuzzy similarity + RRF.

---

# 14. Sparse vs Dense — přesné rozlišení

## Sparse / lexical

Typické:

```text
TF-IDF
BM25
inverted index
```

Data jsou reprezentována pomocí termů / vah termů.

## Dense

Typické:

```text
embedding model
→ dense vector
→ nearest-neighbor similarity
```

Například:

```text
text
 ↓
embedding model
 ↓
[0.13, -0.52, 0.77, ...]
```

### Klíčová korekce

`TF-IDF` není dense retrieval.

Ani přidání SVD automaticky neznamená, že jsme přešli do moderního embedding-based dense retrieval.

V repu je `TF-IDF+SVD` experiment právě klasifikován jako latent semantic / experimentální cesta; výsledkem bylo MRR 0.5413 a experiment byl označen jako neúspěšný na malém korpusu. citeturn678812view2

---

# 15. Embedding

Embedding je naučená / vytvořená **vektorová reprezentace objektu**.

```text
text
 ↓
embedding function
 ↓
vector
```

Nejdůležitější není jednotlivá souřadnice.

Důležitá je geometrie:

```text
similar meaning
→ nearby vectors
```

Tím vzniká možnost semantic retrieval.

---

# 16. Cosine similarity

Typická míra podobnosti vektorů:

```text
cos(A,B) = (A·B) / (||A|| ||B||)
```

Intuice:

> porovnáváme úhel mezi vektory, ne pouze jejich absolutní délku.

Při normalizovaných vektorech se cosine similarity redukuje na dot product.

---

# 17. Vector DB

Vector database:

```text
embedding storage
+
nearest-neighbor search
```

Není sama o sobě model.

Rozlišení:

```text
embedding model
→ tvoří reprezentaci

vector DB
→ ukládá a vyhledává reprezentace
```

---

# 18. Precision@K

Otázka:

> Jak čistých je prvních `K` výsledků?

```text
Precision@K =
relevant in top-K
----------------
K
```

Příklad:

```text
top-5 = R R N R N

Precision@5 = 3/5 = 0.60
```

V projektu je `Precision@3` uváděna jako „kolik z top-3 je správně“. citeturn678812view3

---

# 19. Recall@K

Otázka:

> Kolik ze všech relevantních výsledků se dostalo do top-K?

```text
Recall@K =
relevant in top-K
----------------
all relevant
```

Příklad:

```text
all relevant = 10
found in top-5 = 4

Recall@5 = 0.40
```

Mentální kontrast:

```text
Precision = čistota
Recall    = pokrytí
```

---

# 20. MRR

MRR odpovídá otázce:

> Jak vysoko je PRVNÍ relevantní výsledek?

```text
rank 1 → 1.00
rank 2 → 0.50
rank 3 → 0.33
rank 10 → 0.10
none → 0
```

V `ML_Ops_Education` je MRR jednou z hlavních metrik a aktuální benchmark uvádí:

```text
SequenceMatcher        0.6613
BM25                    0.6397
BM25 + Seq RRF          0.7067
```

Nejde jen o číslo. Toto je experimentální evidence, že kombinace rankingů v konkrétním malém korpusu překonala baseline na MRR. citeturn678812view2

---

# 21. MAP a nDCG

## MAP

Sleduje kvalitu pořadí více relevantních výsledků přes dotazy.

Mentální model:

```text
MRR
→ zajímá mě první relevantní

MAP
→ zajímá mě pořadí více relevantních
```

## nDCG

Hodí se tam, kde relevance může být graded:

```text
0
1
2
3
```

a zároveň záleží na pozici.

Mentální model:

```text
relevance
+
position
```

---

# 22. RRF

Základní forma:

```text
RRF(d) = Σ 1/(k + rank_i(d))
```

RRF nevyžaduje, aby byly raw score jednotlivých retrieverů na stejné škále.

Pracuje s pořadím.

Proto:

```text
BM25 score = 8.2
Dense score = 0.87
```

nemusí být přímo srovnatelné.

Ale:

```text
BM25 rank = 2
Dense rank = 4
```

srovnávat lze.

---

# 23. Co je skutečný retrieval pipeline současného repa

```text
query
  │
  ├── tokenize
  │
  ├── query expansion
  │
  ├── BM25 original
  │
  ├── BM25 expanded
  │
  └── SequenceMatcher
         │
         ▼
       RRF(k=60)
         │
         ▼
       top-k
```

Implementační reference:

- `tokenize()` — `retrieve.py`
- `BM25` — `retrieve.py`
- `expand_query()` — `retrieve.py`
- `search_fuzzy()` — `retrieve.py`
- `rrf_fusion()` — `retrieve.py`
- `RetrievalEngine.search()` — `retrieve.py`

citeturn724011view0turn724011view1

---

# 24. Co projekt skutečně naměřil

Výzkumná zpráva uvádí:

```text
SequenceMatcher
MRR = 0.6613

BM25
MRR = 0.6397

BM25 + Seq RRF
MRR = 0.7067

TF-IDF + SVD
MRR = 0.5413

Query Expansion + Seq RRF
→ nejlepší Precision@3
```

Konkrétně experiment s query expansion zlepšil Precision@3 o 18.4 % proti příslušné baseline kombinaci a přidal 6.9 % MRR v reportovaném experimentu. citeturn678812view2

### Důležitý závěr

Nejlepší algoritmus není automaticky ten „nejmodernější“.

Na malém korpusu:

```text
jednoduchý model
+
dobrá reprezentace
+
dobrá ensemble strategie
```

může porazit složitější přístup.

---

# 25. MMR není MRR

Toto jsou dvě zcela rozdílné věci.

## MRR

Evaluation metric:

```text
Mean Reciprocal Rank
```

## MMR

Retrieval / reranking objective:

```text
Maximal Marginal Relevance
```

MMR se snaží získat výsledky, které jsou:

```text
relevantní k query
+
odlišné od již vybraných
```

V projektu byl MMR experimentován, ale na malém korpusu zhoršoval MRR. citeturn678812view2

---

# 26. `Sec@3` — epistemická korekce

Aktuální audit repa nepotvrdil v:

- `EVALUATION.md`
- `RETRIEVAL_RESEARCH.md`

metrický termín `Sec@3`.

Proto:

```text
Sec@3 = UNKNOWN
```

a ne:

```text
Sec@3 = Success@3
```

ani:

```text
Sec@3 = Precision@3
```

### Správný postup

```text
grep -R "Sec@3" .
grep -R "Sec@" .
grep -R "Success@3" .
grep -R "Precision@3" .
```

V aktuálním webově dostupném zdroji `EVALUATION.md` nebyla shoda pro `Sec@3` ani `Success@3`. citeturn724011view3turn724011view4

**Learning rule: neznámý termín se ověřuje, nikoli domýšlí.**

---

# 27. Dataset D, reprezentace Φ(D), model f, hyperparametry λ

Toto je jeden z nejdůležitějších mentálních modelů pro další adopci.

```text
RAW DATA
   D
   │
   ▼
REPRESENTATION
 Φ(D)
   │
   ▼
MODEL
 f
   │
   ▼
OUTPUT / RANK
   │
   ▼
METRIC
```

Například:

```text
D = GT documents

Φ(D) =
tokenization
+
selected fields
+
window/chunking

f =
BM25 + RRF

λ =
k1, b, k

M =
MRR / Precision@3 / Recall
```

Toto je mnohem přesnější mental model než:

> „upravoval jsem data, aby score vyšlo lépe.“

Data jsou vstupní evidence. Reprezentace a model jsou transformace.

---

# 28. Data leakage / p-hacking

Pokud je dataset současně ground truth pro měření a autor jej začne selektivně měnit proto, aby metrika rostla, test přestává být čistý.

Proto:

```text
D
→ fixed evaluation ground truth

Φ(D), f, λ
→ lze experimentálně měnit

metric
→ pozorujeme

D
→ měníme pouze z oprávněného důvodu,
  ne proto, aby „vyšla lepší metrika“
```

V existující `RETRIEVAL_RESEARCH.md` je tento problém správně explicitně diskutován v kontextu `D`, `Φ(D)`, `f` a `λ`. citeturn678812view2

---

# 29. General ML lifecycle

Obecná kostra:

```text
data
 ↓
representation / features
 ↓
model
 ↓
fit / training
 ↓
evaluation
 ↓
artifact
 ↓
deployment
 ↓
monitoring
 ↓
feedback
```

Ne každá část každého AI systému používá supervised training.

Proto rozlišovat:

```text
training
retrieval
inference
evaluation
deployment
```

---

# 30. Training vs inference

## Training / fitting

```text
data
→ parameters / index / representation
```

## Inference / retrieval

```text
new input
→ existing model / index
→ output
```

V BM25:

```text
fit(documents)
→ vytvoří statistiky / index
```

a potom:

```text
search(query)
→ ranking
```

To je analogie, která je vynikající pro první pochopení lifecycle bez neural networks. citeturn724011view0

---

# 31. MLOps

MLOps řeší:

> **jak udržet ML systém reprodukovatelný, nasaditelný, pozorovatelný a řízený v čase.**

Základ:

```text
experiment
→ artifact
→ version
→ deployment
→ monitoring
→ feedback
```

Specifická ML vrstva oproti běžnému software:

```text
data
+
model behavior
+
evaluation
+
drift
```

---

# 32. Experiment tracking

Minimální experiment:

```text
run_id
dataset
code_version
parameters
metrics
artifact
timestamp
```

Příklad:

```text
run_042
method=BM25
k1=1.5
b=0.75
RRF_k=60
MRR=0.7067
git=abc123
```

To je analogie k deterministickému engineeringu:

```text
input
+
configuration
+
version
→ reproducible result
```

---

# 33. Model registry

Registry odděluje experimentální artefakt od schválené verze.

```text
experiment
 ↓
evaluation
 ↓
candidate
 ↓
approved
 ↓
production
```

U retrieval systému může být analogií:

```text
retrieval configuration
 ↓
benchmark
 ↓
approved configuration
 ↓
deployed retriever
```

---

# 34. Serving

Training:

```text
dataset → model
```

Serving:

```text
request → model → response
```

Serving řeší:

- latency
- throughput
- concurrency
- memory
- availability
- errors
- rollback

---

# 35. Monitoring

Musíme rozlišit:

```text
system health
data health
model quality
```

Například:

```text
CPU
RAM
latency
error rate
```

vs.

```text
input distribution
schema validity
missing values
```

vs.

```text
precision
recall
ranking quality
drift
```

Důležitá věta:

> **„Service is healthy“ neznamená „model je kvalitní“.**

---

# 36. AI Engineering

Prakticky:

```text
AI Engineering
→ stavba AI-powered applications

MLOps
→ provoz a lifecycle model-based systems
```

AI Engineering zahrnuje zejména:

- retrieval
- RAG
- tool calling
- agents
- structured outputs
- evaluation
- orchestration

MLOps:

- experiment tracking
- versioning
- serving
- deployment
- monitoring
- reproducibility

V praxi se oblasti překrývají.

---

# 37. RAG

Minimální model:

```text
documents
 ↓
chunk
 ↓
index
 ↓
query
 ↓
retrieval
 ↓
top-k context
 ↓
LLM
 ↓
answer
```

Klíčové rozlišení:

```text
retrieval quality
≠
generation quality
```

Můžeš mít:

```text
excellent LLM
+
bad retrieval
=
bad RAG
```

---

# 38. PBL laboratoře přímo nad kódem

## LAB 01 — BM25 from scratch

### Cíl

Přepsat minimální BM25 mimo současný `retrieve.py`.

### Acceptance

Bez LLM vysvětlit:

- TF
- DF
- IDF
- `k1`
- `b`
- `dl`
- `avg_dl`
- saturation

### Reference

`retrieve.py`:

- `BM25.__init__`
- `BM25.fit`
- `BM25._idf`
- `BM25._score_doc`

citeturn724011view0

---

## LAB 02 — Parameter sweep

Vyzkoušet:

```text
k1 ∈ ...
b  ∈ ...
```

a sledovat:

```text
MRR
Precision@3
Recall
```

### Acceptance

Před experimentem formulovat predikci:

> Co očekávám, že se stane?

A po experimentu:

> Proč výsledek dopadl takto?

---

## LAB 03 — Metriky ručně

Na několika query vytvořit:

```text
relevance labels
```

a ručně spočítat:

```text
P@1
P@3
P@5
R@3
R@5
MRR
```

### Acceptance

Výsledek ručního výpočtu musí souhlasit s implementací.

---

## LAB 04 — Sparse vs dense

Postavit:

```text
BM25
vs
embedding retrieval
vs
hybrid
```

a měřit:

```text
Precision@K
Recall@K
MRR
nDCG
latency
```

### Acceptance

Nestačí určit vítěze.

Nutné vysvětlit:

> **proč** daný přístup na konkrétním datasetu vyhrál / selhal.

---

## LAB 05 — RAG minimum

```text
GT docs
 ↓
chunking
 ↓
BM25 / dense
 ↓
top-k
 ↓
LLM
```

Oddělit retrieval a generation evaluation.

---

## LAB 06 — MLOps minimum

```text
dataset v1
 ↓
run 1
 ↓
metrics
 ↓
artifact
```

potom:

```text
dataset/model/config v2
 ↓
run 2
 ↓
comparison
```

Zaznamenat:

```text
git commit
run_id
parameters
metrics
artifact
```

---

# 39. Feynman verification matrix

Každý skill musí projít:

| Level | Test |
|---|---|
| 1 | Co to je? |
| 2 | Jak to funguje? |
| 3 | Kdy selhává? |
| 4 | Jak to implementuji? |
| 5 | Jak změřím, že funguje? |
| 6 | Jak se napojí na můj systém? |

### Mastery threshold pro tento sprint

Minimálně:

```text
Level 1–3 = conceptual
Level 4     = implemented
Level 5     = verified
Level 6     = integrated
```

---

# 40. Anti-vibe checkpoint

Po každém větším tématu:

```text
CLOSE LLM
```

a vlastními slovy:

```text
1. definice
2. mechanismus
3. vzorec
4. příklad
5. failure mode
6. kódová reference
7. experiment
```

Pokud lze vysvětlit pouze při otevřeném LLM:

```text
skill ≠ adopted
```

---

# 41. Co je skutečná evidence skillu

### Awareness

> Viděl jsem BM25.

### Conceptual

> Umím vysvětlit TF, IDF, `k1`, `b`.

### Implementation

> Umím jej implementovat.

### Experimental

> Umím měřit jeho vliv na MRR.

### Engineering

> Umím vysvětlit failure modes a trade-offs.

### Integration

> Umím ho zasadit do retrieval pipeline.

### Architectural

> Umím říct, kdy BM25 použít a kdy ne.

---

# 42. Market relevance bez technology collecting

Každý nový skill projde filtrem:

```text
market relevance
×
current gap
×
learning cost
×
portfolio synergy
×
evidence potential
```

To vede k preferenci:

```text
1 skill
→ 1 PBL experiment
→ 1 implementation
→ 1 evidence artifact
```

místo:

```text
10 tutorialů
→ 20 buzzwords
→ 0 evidence
```

---

# 43. Doporučená adopční sekvence

## A — retrieval ontology

```text
TF-IDF
→ BM25
→ k1
→ b
→ Precision@K
→ Recall@K
→ MRR
→ MAP
→ nDCG
→ RRF
→ sparse vs dense
```

## B — representation

```text
embedding
→ cosine similarity
→ vector search
→ chunking
→ reranking
→ hybrid retrieval
```

## C — ML basics

```text
x
y
ŷ
θ
λ
loss
train/validation/test
overfitting
generalization
```

## D — MLOps

```text
experiment tracking
→ artifact versioning
→ registry
→ deployment
→ serving
→ monitoring
→ drift
```

## E — AI engineering

```text
RAG
→ tool calling
→ agents
→ evaluation
→ MCP
→ observability
```

---

# 44. Praktická korelace s `MCP-Jobs`

Nejúčinnější budou experimenty, které se vracejí k existujícímu systému:

```text
MCP-Jobs
 │
 ├── jobs
 ├── skills
 ├── PostgreSQL
 ├── MCP
 └── Docker
       │
       ▼
 new AI/ML capability
       │
       ▼
 measurable effect
```

Příklad:

```text
skill:
dense retrieval

implementace:
job descriptions → embeddings

evaluation:
MRR / Recall@K

integration:
skill retrieval in MCP-Jobs

evidence:
benchmark + code + result
```

---

# 45. Azure / Cloud jako capability, ne cíl

Azure deployment není „učím se Azure“.

Skutečné capabilities:

```text
cloud resources
networking
identity
managed DB
containers
firewall
health checks
monitoring
cost control
```

Stejný princip platí:

```text
Kubernetes
≠ badge

MLflow
≠ badge

Azure
≠ badge
```

Cílem je capability, kterou lze prokázat.

---

# 46. One-page mental model

```text
DATA
 ↓
REPRESENTATION
 ↓
MODEL / RETRIEVER
 ↓
OUTPUT
 ↓
EVALUATION
 ↓
DEPLOYMENT
 ↓
MONITORING
 ↓
FEEDBACK
```

### ML

```text
ŷ = f(x; θ)
```

### Hyperparameters

```text
λ → controls procedure/model configuration
```

### Retrieval

```text
query
→ candidates
→ ranking
→ top-k
```

### Sparse

```text
TF-IDF / BM25
```

### Dense

```text
embedding / vector similarity
```

### Hybrid

```text
sparse + dense
→ fusion
```

### Evaluation

```text
Precision
Recall
MRR
MAP
nDCG
```

### MLOps

```text
experiment
→ artifact
→ version
→ deploy
→ observe
→ update
```

---

# 47. Nejbližší praktický sprint

## Sprint 1 — skutečně dostat retrieval do hlavy

1. `k1`
2. `b`
3. BM25 equation
4. TF / DF / IDF
5. Precision@K
6. Recall@K
7. MRR
8. RRF
9. rozdíl MRR × MMR
10. sparse × dense

### Výstup

Jedna vlastní stránka vysvětlení bez LLM + toy implementation.

---

## Sprint 2 — experiment

```text
BM25 parameter sweep
+
query expansion
+
RRF
```

Výstup:

```text
hypothesis
→ experiment
→ metrics
→ interpretation
```

---

## Sprint 3 — dense retrieval

```text
embedding
→ cosine
→ vector search
→ compare against BM25
```

---

## Sprint 4 — MLOps

```text
experiment tracking
→ artifact
→ deployment
→ monitoring
```

---

# 48. Definition of Done

Skill je pro tento sprint „adopted“, pokud:

```text
[1] definice
[2] mechanismus
[3] parametry
[4] failure mode
[5] mikropříklad
[6] vlastní implementace
[7] vlastní měření
[8] vysvětlení bez LLM
```

Skill je „verified“, pokud existuje:

```text
code
+
experiment
+
metric
+
interpretation
```

Skill je „integrated“, pokud je použit v existujícím projektu.

---

# 49. Nejvyšší SNR interpretace celého projektu

`ML_Ops_Education` není primárně „ML kurz“.

Je to:

> **laboratoř pro převod nové technologické ontologie do vlastního engineeringu.**

Jeho nejcennější funkce je:

```text
UNKNOWN TERM
   ↓
Feynman explanation
   ↓
toy model
   ↓
code
   ↓
benchmark
   ↓
failure
   ↓
interpretation
   ↓
skill evidence
```

Tento mechanismus je přirozeným pokračováním přístupu již používaného v ostatních repozitářích:

```text
real-world problem
→ structured representation
→ deterministic processing
→ validation
→ iteration
```

---

# 50. Finální kalibrace autora

Současný profil není korektní popsat jako:

> „ML engineer“.

Ani jako:

> „MLOps engineer“.

Přesnější je:

> **začínající AI/ML engineering generalista s již vybudovaným praktickým software/data/integration základem, který nyní konsoliduje formální ontologii ML, retrieval a MLOps.**

### Silná strana

```text
stavění systémů
```

### Aktuální hlavní gap

```text
hloubka modelů + terminologie + formalizované vyhodnocení
```

### Strategická odpověď

```text
méně nových technologií
+
více mechanistického porozumění
+
více experimentů
+
více evidence
```

---

# 51. Audit trail / code references

## `ML_Ops_Education`

Repository:
https://github.com/outpost2026/ML_Ops_Education

### `retrieve.py`

- BM25 class: přibližně řádky 846–920
- `k1`, `b`: 848–852
- `fit()`: 854–879
- `_idf()`: 881–889
- `_score_doc()`: 891–920
- `tokenize()`: 993–999
- `fuzzy_score()`: 1039–1061
- `rrf_fusion()`: 1075–1085
- `RetrievalEngine.search()`: 1125–1166

citeturn724011view0turn724011view1

### `RETRIEVAL_RESEARCH.md`

Obsahuje:

- benchmark progression,
- MRR výsledky,
- Precision@3 výsledky,
- sparse/latent retrieval experimenty,
- RRF,
- MMR,
- skills ontology,
- interpretaci `D`, `Φ(D)`, `f`, `λ`.

citeturn678812view2

### `EVALUATION.md`

Samostatná evaluační dokumentace repa.

citeturn881451view1

---

# 52. Pracovní závěr

Nejbližší cíl není:

```text
„umět ML“
```

ale:

> **získat takovou kontrolu nad základní ontologií, aby LLM přestalo být tlumočníkem terminologie a stalo se pouze akcelerátorem vlastního myšlení.**

První praktický práh je:

```text
TF-IDF
BM25
k1
b
Precision@K
Recall@K
MRR
RRF
sparse
dense
embedding
x
y
ŷ
θ
λ
loss
```

Každý z těchto pojmů musí být možné:

```text
vysvětlit
→ spočítat
→ implementovat
→ změřit
→ kritizovat
```

To je skutečná adopce.

---

## Status

**Artifact:** v2.0  
**Revision reason:** cross-audit + live repository verification  
**Primary correction:** theory ↔ code ↔ experiment linkage  
**Epistemic correction:** `Sec@3` remains unresolved; TF-IDF ≠ true dense retrieval; BM25 terminology clarified  
**Recommended first deep dive:** `BM25 → k1/b → Precision@K → Recall@K → MRR → RRF → sparse vs dense`