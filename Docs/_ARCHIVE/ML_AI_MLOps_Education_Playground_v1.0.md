# ML/AI Engineering Playground
## Ground Truth → Ontologie → Feynman → PBL → Evidence

**Autor:** Ondřej Soušek / outpost2026  
**Datum:** 2026-08-28  
**Účel:** osobní edukační a rozvojový artefakt pro adopční sprint ML/AI/MLOps  
**Status:** living document / playground  
**Primární projekty:** `ML_Ops_Education`, `MCP-Jobs`, `linkedin-mcp-analyzer`, `B2B-Knowledge-Base`

---

# 0. Jak tento dokument používat

Tento dokument není certifikační skript ani encyklopedie. Je to **mapa převodu cizí terminologie do vlastního mentálního modelu**.

Výchozí předpoklad:

> Vytvoření repa není samo o sobě důkazem hluboké znalosti.

Repo `ML_Ops_Education` vzniklo přibližně během dvou dnů a zhruba 90 % dokumentace bylo vytvořeno s pomocí LLM. Proto je současný stav realisticky:

**základní povědomí + schopnost následovat implementaci + vznikající ontologie, ale zatím nízká míra tacitní znalosti principů.**

To není problém. Je to přesně stav, pro který je vhodný PBL/Feynman přístup:

```text
nový termín
   ↓
vlastní vysvětlení
   ↓
matematická / logická kostra
   ↓
mikropříklad
   ↓
implementace
   ↓
porovnání s realitou
   ↓
nové vysvětlení bez LLM
```

**Cíl není „znát názvy“. Cíl je umět vysvětlit mechanismus a předvídat jeho chování.**

---

# 1. Ground Truth současné úrovně

## 1.1 Co už existuje

Portfolio již obsahuje praktickou zkušenost s:

- Python
- ETL / ingestion
- normalizací dat
- PostgreSQL
- Docker
- CI/CD
- MCP
- LLM-facing tooling
- deterministickými testy
- benchmarky
- cloud deploymentem
- retrieval experimenty

`MCP-Jobs` dnes funguje jako market-data substrate: provider ingestion → normalizace → matching → deduplikace → persistence → MCP/CLI. Repo má také vlastní skills catalog s 119 IT skills v 27 kategoriích.

`ML_Ops_Education` přidává experimentální vrstvu: knowledge representation, retrieval, ranking, evaluation a základní ML/AI terminologii.

## 1.2 Co zatím není bezpečné považovat za „umím“

Není bezpečné tvrdit hlubokou znalost:

- statistického učení,
- matematických základů ML,
- dense retrieval,
- embeddingů,
- vector databases,
- rankingových metrik,
- model lifecycle,
- experiment tracking,
- model serving,
- observability ML systémů,
- Kubernetes v produkčním kontextu,
- systematické MLOps architektury.

Současná úroveň je přesnější formulovat jako:

> **„Umím se v doméně orientovat, implementovat část konceptu podle specifikace/LLM asistence a vytvořit experiment; nyní potřebuji převést terminologii na vlastní tacitní model.“**

---

# 2. Místo „ML člověk“: správný cílový vektor

Pro nejbližší období není cílem stát se specialistou na training foundation modelů.

Praktičtější profil:

```text
Python / data engineering
        +
cloud / containers / CI
        +
AI application engineering
        +
retrieval / RAG
        +
MLOps fundamentals
        +
MCP / agentic integration
```

Tedy:

> **AI / automation / integration engineer s postupně rostoucí MLOps kompetencí**

To navazuje na již existující portfolio místo toho, aby ho rušilo.

---

# 3. Ekosystém: kde je `ML_Ops_Education`

```text
REAL WORLD
   │
   ├── CNC / CAM / RE
   │
   └── JOB MARKET
          │
          ▼
      MCP-Jobs
      FIND
          │
          ├── jobs
          └── demanded skills
                   │
                   ▼
          LinkedIn Analyzer
             EVALUATE
          FIT / GAP / EROI
                   │
                   ▼
          ML_Ops_Education
             LEARN / BUILD
                   │
          ┌────────┴────────┐
          ▼                 ▼
      experiment         artifact
          │                 │
          └────────┬────────┘
                   ▼
                 EVIDENCE
                   │
                   ▼
             skill state
                   │
                   └──────→ next market observation

B2B-Knowledge-Base
        ↑
        │
 epistemic / calibration layer
```

Nejde o to vytvořit jednu mega-aplikaci.

Každé repo má jinou funkci:

| Artefakt | Funkce |
|---|---|
| MCP-Jobs | FIND — pozorování trhu |
| LinkedIn Analyzer | EVALUATE — FIT/GAP/EROI |
| ML_Ops_Education | LEARN / BUILD — adopční laboratoř |
| Lichess Analyzer | VALIDATE — evidence → model → interpretation |
| B2B-Knowledge-Base | CALIBRATE — epistemický rámec |

---

# 4. `SKILLS` jako spojovací vrstva

Dosavadní model:

```text
JOB ──requires──> SKILL
```

Nový model:

```text
JOB
 │
 └── requires → SKILL
                 ▲
                 │
             evidence
                 │
             CANDIDATE
                 │
             learning
                 │
           implementation
                 │
               PBL
```

Vzniká smyčka:

```text
MARKET
  ↓
DEMAND
  ↓
GAP
  ↓
LEARNING PRIORITY
  ↓
PBL IMPLEMENTATION
  ↓
EVIDENCE
  ↓
UPDATED SKILL STATE
  ↓
MARKET
```

To je správný význam `SKILLS`: nikoli katalog technologií, ale **stav kompetence v čase**.

---

# 5. Zásadní rozlišení: technologie ≠ skill ≠ capability ≠ evidence

Příklad: Kubernetes.

```text
technologie:
Kubernetes

koncept:
orchestrace kontejnerů

capability:
umím nasadit aplikaci, službu, healthcheck,
resource limits, rolling update, základní debugging

evidence:
MCP-Jobs skutečně běží v K8s deploymentu
```

Stejný princip platí pro MLOps:

```text
MLflow
  ≠
„viděl jsem MLflow“

skill:
experiment tracking

capability:
umím logovat parametry, metriky, artefakty,
porovnat runs a reprodukovat experiment

evidence:
fungující experiment v mém projektu
```

---

# 6. Basic ontology: co je vlastně Machine Learning

## 6.1 Praktická definice

Machine Learning je metoda, při níž systém **odvodí část rozhodovacího pravidla z dat místo toho, aby celé pravidlo napsal člověk ručně**.

Klasický program:

```text
x ──fixed rules──> y
```

ML systém:

```text
data + desired behavior
        ↓
      learning
        ↓
      model
        ↓
x ──model──> y
```

To je důležitější než jakákoli zmínka o neuronech.

## 6.2 Model obecně

Abstraktně:

```text
ŷ = f(x; θ)
```

kde:

- `x` = vstupní data / features
- `ŷ` = predikovaný výstup
- `f` = struktura/model
- `θ` = parametry, které se učí z trénovacích dat

### Co jsou parametry θ?

Parametry jsou hodnoty, které model **nastavuje během učení**.

Například lineární model:

```text
ŷ = w1*x1 + w2*x2 + b
```

Parametry:

```text
θ = {w1, w2, b}
```

Model se je snaží najít tak, aby predikce odpovídaly datům.

---

# 7. Parametry vs. hyperparametry

Toto je kritický rozdíl.

## Parametry

Model je získá učením:

```text
θ = learned from data
```

Příklad:

- weights
- intercept / bias
- koeficienty
- parametry neuronové sítě

## Hyperparametry

Nastavuje je člověk nebo outer-loop search **před / mimo samotné učení parametrů**.

```text
λ = configuration of the learning procedure
```

Příklady:

- learning rate
- počet stromů
- maximální hloubka stromu
- batch size
- regularization strength
- `k1`, `b` u BM25

Zjednodušeně:

```text
hyperparameters λ
        ↓
learning procedure
        ↓
parameters θ
        ↓
model f
```

---

# 8. X, y a ŷ

## `x` — input

Co model dostane jako vstup.

Příklad:

```text
x = [salary, title_embedding, location, skills]
```

## `y` — skutečný / očekávaný výstup

Ground truth.

```text
y = relevant
```

## `ŷ` — predikce modelu

```text
ŷ = 0.83 probability
```

Rozdíl:

```text
y  = reality
ŷ  = model's estimate
```

Learning se snaží minimalizovat chybu mezi nimi.

---

# 9. Loss function

Model potřebuje způsob, jak poznat:

> „Tahle predikce byla špatně.“

Proto definujeme:

```text
L(y, ŷ)
```

Příklad u regrese:

```text
L = (y - ŷ)^2
```

Model se snaží nalézt takové `θ`, aby byla celková chyba co nejmenší.

Obecně:

```text
θ* = argminθ Σ L(y_i, f(x_i; θ))
```

Toto je základní kostra supervised learning.

Není nutné znát pokročilý kalkulus, aby byl princip jasný:

> **data → predikce → chyba → úprava parametrů → lepší predikce**

---

# 10. Train / validation / test

Rozdělení dat:

```text
DATASET
 ├── train
 ├── validation
 └── test
```

## Train

Model se učí.

## Validation

Pomáhá volit model/hyperparametry.

## Test

Finální nezávislé ověření generalizace.

### Klíčová otázka

Proč nestačí změřit model jen na training datech?

Protože model může **memorovat** data místo toho, aby se naučil obecné pravidlo.

---

# 11. Overfitting / underfitting

## Underfitting

Model je příliš jednoduchý:

```text
real pattern
   ↓
model neumí zachytit
```

## Overfitting

Model se přizpůsobí konkrétním training datům příliš dobře:

```text
training performance ↑
generalization ↓
```

Mentální model:

> **Učení ≠ zapamatování.**

Cílem je generalizace.

---

# 12. Retrieval není totéž co generativní AI

Toto je pro `ML_Ops_Education` zásadní.

Retrieval systém řeší:

> **Které existující položky mají nejvyšší relevanci k dotazu?**

Generativní model řeší:

> **Jak vytvořit nový výstup na základě vstupu a kontextu?**

RAG:

```text
query
 ↓
retrieve
 ↓
relevant context
 ↓
LLM
 ↓
answer
```

Proto můžeš mít kvalitní LLM a přesto mizerný systém, pokud retrieval vrací špatný kontext.

---

# 13. Sparse vs. Dense search

## Sparse retrieval

Reprezentace je založená na explicitních znacích/tokenových vahách.

Typické:

- inverted index
- TF-IDF
- BM25

Příklad:

```text
query = "kubernetes python"

document A = "python kubernetes docker"
document B = "machine learning researcher"
```

Sparse retrieval se ptá:

> Jak dobře se překrývají tokeny a jejich statistická významnost?

## Dense retrieval

Text převedeš na vektor:

```text
text
 ↓
embedding model
 ↓
[0.13, -0.44, 0.72, ...]
```

Dotaz i dokument jsou v prostoru reprezentací.

Hledá se podobnost:

```text
similarity(query_vector, document_vector)
```

Výhoda:

> může zachytit sémantickou příbuznost i při jiném slovním vyjádření.

Nevýhoda:

> více záleží na embedding modelu a jeho reprezentaci.

---

# 14. TF-IDF

TF-IDF znamená:

**Term Frequency – Inverse Document Frequency**

Myšlenka:

> Slovo, které se často vyskytuje v tomto dokumentu, ale málo v celém korpusu, je informativnější.

Jednoduchá intuice:

```text
TF  = jak často je term v dokumentu
IDF = jak vzácný je term v celém korpusu
```

Typická forma:

```text
TF-IDF(t,d) = TF(t,d) × IDF(t)
```

Pokud je „Python“ v každém dokumentu, jeho IDF je nízké.

Pokud je „Kubeflow“ v několika málo dokumentech, IDF je vyšší.

TF-IDF tedy není „AI magie“.

Je to statistická metoda vážení slov.

---

# 15. BM25

BM25 je pokročilejší ranking metoda navazující na klasický probabilistic information retrieval.

Záměr:

> dát vyšší skóre dokumentům, které mají dobrý tokenový match, ale zároveň korigovat délku dokumentu a efekt opakování termu.

Jedna běžná forma:

```text
score(D,Q) =
Σ IDF(q_i) *
      [ TF(q_i,D) * (k1 + 1) ]
      --------------------------------
      [ TF(q_i,D) + k1 * (1 - b + b * |D| / avgdl) ]
```

Pro základní porozumění stačí rozdělit rovnici na tři části:

```text
IDF
 ×
term-frequency saturation
 ×
document-length normalization
```

## Co je `k1`?

`k1` je hyperparametr určující, **jak rychle se efekt opakovaného výskytu termu nasycuje**.

Bez saturation bych mohl přidávat stejný výraz znovu a znovu a skóre by rostlo téměř lineárně.

BM25 říká:

> první relevantní výskyty jsou důležité, další už méně.

Zjednodušeně:

```text
TF: 1 → 2 → 3 → 4 → 5
efekt:
   ↑   ↑   ↑   →   →
```

Vyšší `k1` obecně dovoluje term frequency ovlivňovat skóre déle / méně agresivně saturuje.

## Co je `b`?

`b` řídí sílu normalizace délky dokumentu.

```text
b = 0
→ délka se prakticky ignoruje

b = 1
→ plná délková normalizace
```

Typicky bývá mezi 0 a 1.

Mentální model:

> `k1` = jak moc záleží na opakování termu  
> `b` = jak moc penalizujeme / korigujeme délku dokumentu

## Co je „k“ v `Precision@k`?

Tady jde o úplně jiný koncept.

`k` zde nepatří BM25.

```text
Precision@3
```

znamená:

> podívej se pouze na první 3 výsledky.

Tedy:

```text
k = cutoff
```

To není model parameter.

To je **evaluation parameter**.

Tento rozdíl musí být v hlavě pevně oddělen:

```text
BM25 k1
BM25 b
Precision@k
```

jsou tři různé věci.

---

# 16. Precision@K

Příklad:

Top 5 výsledků:

```text
1 relevant
2 relevant
3 irrelevant
4 relevant
5 irrelevant
```

Pak:

```text
Precision@5 = 3 / 5 = 0.60
```

Interpretace:

> Z prvních `k` vrácených položek bylo kolik skutečně relevantních?

Formálně:

```text
Precision@k =
relevant results in top-k
-------------------------
k
```

---

# 17. Recall@K

Recall se ptá na něco jiného:

> Kolik ze všech relevantních dokumentů se podařilo dostat do top-k?

```text
Recall@k =
relevant results in top-k
-------------------------
all relevant results
```

Příklad:

Existuje 10 relevantních dokumentů.

Do top-5 se dostanou 4.

```text
Recall@5 = 4 / 10 = 0.40
```

Proto:

```text
Precision = čistota výsledků
Recall    = pokrytí relevantních výsledků
```

---

# 18. MRR

**Mean Reciprocal Rank**

MRR řeší velmi konkrétní otázku:

> Jak vysoko se objeví PRVNÍ relevantní výsledek?

Pro jeden dotaz:

```text
relevant at rank 1 → 1/1 = 1.00
relevant at rank 2 → 1/2 = 0.50
relevant at rank 3 → 1/3 = 0.33
relevant at rank 10 → 1/10 = 0.10
none → 0
```

Potom se hodnoty zprůměrují přes dotazy.

Proto:

> MRR je vhodné, když je pro uživatele nejdůležitější najít alespoň jeden správný výsledek co nejdříve.

To odpovídá experimentům v `ML_Ops_Education`.

---

# 19. MAP

MAP = Mean Average Precision.

Na rozdíl od MRR neřeší pouze první relevantní výsledek.

Sleduje:

> jak dobře je v celém rankingovém prefixu umístěno více relevantních výsledků.

Zjednodušeně:

```text
MRR
→ první relevantní výsledek

MAP
→ kvalita pořadí více relevantních výsledků
```

---

# 20. nDCG

nDCG = Normalized Discounted Cumulative Gain.

Hodí se zejména, když relevance není binární.

Například:

```text
0 = nerelevantní
1 = slabě relevantní
2 = relevantní
3 = velmi relevantní
```

A současně záleží na pozici:

```text
relevant at rank 1
>
relevant at rank 5
```

nDCG tedy kombinuje:

```text
relevance grade
+
position
```

a normalizuje výsledek vůči ideálnímu pořadí.

Mentální model:

> nDCG = „jak dobrý je ranking, když mi záleží na kvalitě i pozici výsledků“.

---

# 21. RRF — Reciprocal Rank Fusion

RRF je způsob, jak spojit více rankingů.

Příklad:

```text
BM25 ranking
Dense ranking
```

Místo nuceného převádění jejich skóre do stejné škály můžeme kombinovat jejich **pozice**.

Základní forma:

```text
RRF(d) = Σ 1 / (k + rank_i(d))
```

kde:

- `rank_i(d)` = pořadí dokumentu v konkrétním rankeru
- `k` = stabilizační konstanta
- suma běží přes jednotlivé rankery

Pozor:

Toto `k` v RRF je opět **jiné `k`** než:

- BM25 `k1`
- Precision@k

Stejná literka ≠ stejný koncept.

---

# 22. Proč hybrid retrieval dává smysl

Sparse a dense retrieval mají jiné chyby.

```text
Sparse
  ↑
přesný lexical match

Dense
  ↑
sémantická podobnost
```

Může nastat:

```text
query:
"container orchestration"

BM25:
najde "container orchestration"

Dense:
najde "Kubernetes cluster management"
```

Ani jedno není univerzálně lepší.

Hybrid retrieval:

```text
query
 ├── BM25
 │
 └── Dense
       ↓
      RRF
       ↓
 combined ranking
```

To je velmi důležitá myšlenka pro další vývoj `ML_Ops_Education`.

---

# 23. „Sec@3“ — explicitní nejistota

`Sec@3` není běžně používaná standardní retrieval metrika.

Proto se nesmí automaticky „dovysvětlit“.

První krok:

```text
SEC@3
  ↓
UNKNOWN / NEED VERIFICATION
```

Pravděpodobně může jít o překlep nebo lokální označení pro jinou metriku, například:

- Precision@3
- Recall@3
- Success@3

Správný epistemický postup:

> **Neznám termín → nehádat → dohledat definici ve zdroji / experimentu.**

Toto je přesně případ, kde „confidence < threshold“ má vytvořit otázku, nikoli smyšlenou odpověď.

---

# 24. Embedding

Embedding je číselná reprezentace objektu vektorem.

```text
text
 ↓
embedding model
 ↓
vector
```

Příklad:

```text
"Python developer"
→ [0.17, -0.04, 0.62, ...]
```

Samotná čísla nemají jednoduchý lidský význam.

Důležitá je:

> **geometrie prostoru reprezentace.**

Podobné významy by měly být reprezentovány vektorově blíž.

---

# 25. Vector database

Vector DB není „ML model“.

Je to infrastruktura pro efektivní:

```text
store vectors
+
search nearest / similar vectors
```

Tedy:

```text
embedding
   ↓
vector DB
   ↓
nearest-neighbor retrieval
```

Rozlišení:

```text
embedding model
→ vytváří reprezentaci

vector DB
→ ukládá a vyhledává reprezentace
```

---

# 26. AI model, framework, library, platform

Častý zdroj chaosu.

```text
model
→ naučená reprezentace / funkce

framework
→ nástroje pro práci s modely

library
→ programátorské stavební bloky

platform
→ vyšší celek pro deployment / management

service
→ API / infrastruktura poskytovaná jako služba
```

Příklad:

```text
PyTorch
= framework

scikit-learn
= ML library

MLflow
= lifecycle / experiment tooling

Kubernetes
= orchestration platform

PostgreSQL
= database

LLM
= model
```

---

# 27. MLOps: co to vlastně řeší

MLOps není „DevOps, akorát s neurony“.

Je to soubor postupů pro provoz ML systémů v čase.

Typický lifecycle:

```text
data
 ↓
preparation
 ↓
training
 ↓
evaluation
 ↓
model registry
 ↓
deployment
 ↓
serving
 ↓
monitoring
 ↓
feedback
 ↓
retraining / update
```

Software engineering často stačí:

```text
code
→ build
→ deploy
→ monitor
```

ML přidává:

```text
data
+
model
+
model version
+
experiment
+
evaluation
+
drift
```

Proto je MLOps z velké části **řízení reprodukovatelnosti a změny v systémech, jejichž chování závisí na datech**.

---

# 28. Reproducibility

ML experiment bez reprodukovatelnosti je slabý důkaz.

Potřebuješ být schopen říct:

```text
dataset version
+
code version
+
model version
+
hyperparameters
+
environment
+
metrics
=
experiment result
```

To je velmi blízké již existujícímu deterministic-engineering myšlení v portfoliu.

Transfer:

```text
golden master / regression
        ↓
experiment tracking
        ↓
reproducible ML experiment
```

---

# 29. Experiment tracking

Typická metadata experimentu:

```text
run_id
dataset
model
hyperparameters
metrics
artifacts
timestamp
git commit
```

Příklad:

```text
run_042
model=BM25
k1=1.5
b=0.75
MRR=0.7067
git=abc123
```

Tím se z „funguje mi to“ stává:

> **ověřitelný experiment.**

---

# 30. Model registry

Model registry odděluje:

```text
experiment
```

od:

```text
candidate / production model
```

Například:

```text
model v17
  ↓
evaluation
  ↓
approved
  ↓
staging
  ↓
production
```

---

# 31. Serving

Training:

```text
data → model
```

Serving:

```text
request → model → prediction
```

To jsou různé provozní problémy.

Training řeší:

- compute
- dataset
- optimization

Serving řeší:

- latency
- throughput
- availability
- batching
- memory
- concurrency
- rollback

---

# 32. Monitoring ML systému

Nestačí:

```text
CPU = 40 %
```

Potřebujeme také sledovat:

```text
system metrics
+
data metrics
+
model metrics
```

Například:

### System

- latency
- CPU
- RAM
- error rate

### Data

- missing values
- distribution shifts
- schema changes

### Model

- precision / recall
- relevance
- drift
- calibration
- business metric

---

# 33. Data drift a model drift

## Data drift

Změní se distribuce vstupních dat:

```text
training world
     ↓
new world
```

Například:

```text
historically:
"Python developer"

new market:
"AI engineer / agent platform"
```

## Model performance degradation

I když technicky vše běží, kvalita predikcí může klesat.

Proto:

> **„service is up“ ≠ „model is good“.**

---

# 34. AI engineering vs. MLOps

Praktické rozlišení:

```text
AI Engineering
→ jak postavit AI-powered application

MLOps
→ jak ji spolehlivě provozovat a řídit v čase
```

AI Engineering:

- LLM API
- RAG
- agents
- tool use
- prompt/context orchestration
- evaluation

MLOps:

- versioning
- experiments
- deployment
- monitoring
- reproducibility
- lifecycle

V praxi se překrývají.

---

# 35. Příklad přímo na `MCP-Jobs`

Představ si, že chceš predikovat relevanci pracovní nabídky.

```text
job
 ↓
feature extraction
 ↓
model
 ↓
relevance probability
 ↓
ranking
```

Model může dostat:

```text
x =
[
  skill_overlap,
  salary_fit,
  location_fit,
  role_similarity,
  experience_match
]
```

Ground truth:

```text
y = relevant / irrelevant
```

Prediction:

```text
ŷ = P(relevant | x)
```

Evaluation:

```text
Precision@K
Recall@K
MRR
nDCG
```

Deployment:

```text
container
 ↓
API
 ↓
cloud
 ↓
monitoring
```

Tím se čisté „ML“ propojí s již známým engineering stackem.

---

# 36. Feynman test

U každého nového termínu musí být možné odpovědět bez LLM:

### Level 1 — jednou větou

> Co to je?

### Level 2 — mechanismus

> Jak to funguje?

### Level 3 — trade-off

> Kdy to selhává nebo proč to není vždy nejlepší?

### Level 4 — implementace

> Jak bych to implementoval?

### Level 5 — měření

> Jak dokážu, že to funguje?

### Level 6 — integrace

> Jak se to připojí k MCP-Jobs / mému stacku?

Dokud Level 3–5 nejdou vysvětlit vlastními slovy, skill je stále **learning**, ne mastered.

---

# 37. Skill state model

Doporučený model:

```text
0 = unknown
1 = awareness
2 = conceptual
3 = guided implementation
4 = independent implementation
5 = debugging / trade-offs
6 = architectural judgment
```

Příklad:

```yaml
skill: BM25
state: 2

evidence:
  - read_formula
  - inspected_ML_Ops_Education

gaps:
  - k1
  - b
  - term_frequency_saturation
  - document_length_normalization

next:
  - implement_from_scratch
  - compare_k1_b
  - benchmark
```

---

# 38. PBL protokol

Každý nový skill:

```text
1. Market relevance
2. Define concept
3. Build toy example
4. Implement
5. Benchmark
6. Break it
7. Explain failure
8. Integrate into existing project
9. Record evidence
10. Re-test without LLM
```

To poslední je kritické.

### Anti-vibe checkpoint

Po dokončení:

> Zavři LLM.

A zkus:

```text
- napsat definici
- nakreslit flow
- vysvětlit parametry
- predikovat výsledek experimentu
- vysvětlit failure mode
```

---

# 39. Doporučené pořadí adopce

## Fáze A — Retrieval fundamentals

1. TF-IDF
2. BM25
3. Precision@K
4. Recall@K
5. MRR
6. MAP
7. nDCG
8. RRF
9. sparse vs dense

## Fáze B — Representation

10. embeddings
11. cosine similarity
12. vector search
13. chunking
14. reranking
15. hybrid retrieval

## Fáze C — ML fundamentals

16. model
17. parameters
18. hyperparameters
19. loss
20. train/validation/test
21. overfitting
22. generalization
23. classification/regression

## Fáze D — MLOps

24. experiment tracking
25. model registry
26. reproducibility
27. serving
28. containerization
29. CI/CD for ML
30. monitoring
31. data drift
32. model drift

## Fáze E — AI Engineering

33. RAG
34. tool calling
35. agents
36. evaluation
37. structured outputs
38. MCP
39. observability for LLM systems

---

# 40. První praktické laboratoře

## LAB 01 — BM25 z nuly

Cíl:

> implementovat minimální BM25 bez knihovny.

Musíš umět vysvětlit:

- TF
- IDF
- `k1`
- `b`
- document length
- average document length
- saturation

### Acceptance test

Bez LLM vysvětlit každou část rovnice.

---

## LAB 02 — Precision / Recall / MRR

Vytvoř 10 umělých query a relevance labels.

Ruční výpočet:

```text
P@1
P@3
P@5

R@3
R@5

MRR
```

Pak porovnat s implementací.

### Acceptance test

Dokážeš předem říct, která změna rankingu zvýší MRR a která jen Recall?

---

## LAB 03 — Sparse vs Dense

Na stejném datasetu porovnej:

```text
BM25
vs
embedding similarity
vs
BM25 + dense + RRF
```

Měř:

```text
Precision@3
Recall@10
MRR
nDCG
latency
```

### Acceptance test

Ne jen „které číslo je vyšší“, ale:

> **proč se chování jednotlivých retrieverů liší.**

---

## LAB 04 — RAG minimum

Postav:

```text
documents
 ↓
chunking
 ↓
index
 ↓
retrieval
 ↓
top-k context
 ↓
LLM
 ↓
answer
```

A odděl:

```text
retrieval quality
od
generation quality
```

---

## LAB 05 — MLOps minimum

Jednoduchý model:

```text
dataset v1
 ↓
train.py
 ↓
model.pkl
 ↓
metrics.json
```

Potom:

```text
dataset v2
 ↓
new run
 ↓
compare
 ↓
register winner
```

Přidej:

```text
git commit
run_id
hyperparameters
metrics
artifact
```

---

# 41. Jak propojit Azure s adopčním sprintem

Azure není cíl.

Je to prostředí, ve kterém se osvojují:

```text
cloud resource model
+
networking
+
identity
+
managed database
+
container deployment
+
monitoring
+
cost control
```

Pro `MCP-Jobs` proto dává smysl:

```text
MCP-Jobs
 ↓
Docker
 ↓
Azure PostgreSQL
 ↓
Azure VM / container hosting
 ↓
firewall
 ↓
health checks
 ↓
monitoring
```

Tím se cloud skill učí skrze existující systém.

---

# 42. Market → skill → learning

`MCP-Jobs` má skills catalog a market-side skill signal.

Není nutné učit se vše.

Pro každý skill:

```text
market_frequency
×
role_relevance
×
current_gap
×
learning_cost
×
portfolio_synergy
=
learning_priority
```

To je důležitější než prostý seznam „co všechno musím umět“.

---

# 43. EROI pro adopci

Praktická rozhodovací matice:

| Skill | Market relevance | Gap | Learning cost | Portfolio synergy | Priority |
|---|---:|---:|---:|---:|---:|
| Docker | high | low | low | high | high |
| PostgreSQL | high | medium | low | very high | very high |
| Kubernetes | high | high | medium/high | high | high |
| BM25 | medium/high | high | low | very high | very high |
| embeddings | high | high | medium | very high | very high |
| MLflow | medium/high | high | medium | medium | medium |
| PyTorch | medium | high | high | medium | medium |
| model serving | high | high | medium | high | high |

Hodnoty nejsou definitivní pravda. Jsou pracovní heuristika pro rozhodování.

---

# 44. Co znamená „umím“ pro tuto fázi

Ne:

> „Mám repo, které používá BM25.“

Ale:

> „Dokážu bez LLM vysvětlit, proč BM25 funguje, co dělá `k1` a `b`, jak změna parametrů ovlivní ranking, kdy BM25 selže a jak to změřím.“

Ne:

> „Použil jsem embeddings.“

Ale:

> „Umím vysvětlit, proč dense retrieval zachytí sémantiku, jak vzniká embedding, co znamená cosine similarity a jak oddělím retrieval quality od generation quality.“

Ne:

> „Dělal jsem MLOps.“

Ale:

> „Umím popsat lifecycle modelu od datasetu přes experiment, evaluation, registry, deployment až po monitoring.“

---

# 45. Anti-vibe / anti-hallucination pravidla

## Rule 1

**Unknown term ≠ permission to guess.**

## Rule 2

Každá metrika musí mít:

```text
definition
formula
example
failure mode
```

## Rule 3

Každý model musí mít:

```text
input
output
parameters
hyperparameters
loss/evaluation
```

## Rule 4

Každý experiment musí mít:

```text
hypothesis
baseline
change
measurement
result
interpretation
```

## Rule 5

Každý skill musí mít:

```text
market evidence
learning evidence
implementation evidence
```

---

# 46. Co má být na konci adopčního sprintu v hlavě

Ne:

```text
50 nových buzzwords
```

ale tato kostra:

```text
DATA
 ↓
REPRESENTATION
 ↓
MODEL
 ↓
LEARNING / RETRIEVAL
 ↓
EVALUATION
 ↓
DEPLOYMENT
 ↓
MONITORING
 ↓
FEEDBACK
```

A uvnitř:

```text
x → model(x; θ) → ŷ

θ = learned parameters
λ = hyperparameters

retrieval:
query → candidates → ranking → top-k

evaluation:
Precision
Recall
MRR
MAP
nDCG

MLOps:
experiment
→ registry
→ deployment
→ monitoring

AI engineering:
retrieve
→ reason / generate
→ evaluate
→ observe
```

---

# 47. Nejbližší praktický backlog

## Sprint 1 — retrieval ontology

- [ ] TF-IDF vysvětlit bez LLM
- [ ] BM25 vysvětlit bez LLM
- [ ] `k1` vysvětlit
- [ ] `b` vysvětlit
- [ ] implementovat BM25 toy version
- [ ] Precision@K
- [ ] Recall@K
- [ ] MRR
- [ ] MAP
- [ ] nDCG
- [ ] RRF
- [ ] potvrdit význam `Sec@3`

## Sprint 2 — dense retrieval

- [ ] embedding
- [ ] cosine similarity
- [ ] vector DB
- [ ] sparse vs dense
- [ ] hybrid retrieval
- [ ] reranking

## Sprint 3 — ML basics

- [ ] `x`, `y`, `ŷ`
- [ ] `θ`
- [ ] `λ`
- [ ] loss
- [ ] train/validation/test
- [ ] overfitting
- [ ] generalization

## Sprint 4 — MLOps

- [ ] experiment tracking
- [ ] model/artifact versioning
- [ ] reproducibility
- [ ] model registry
- [ ] serving
- [ ] monitoring
- [ ] drift

## Sprint 5 — AI engineering

- [ ] RAG
- [ ] evaluation
- [ ] tool calling
- [ ] MCP
- [ ] agentic workflow
- [ ] observability

---

# 48. Definition of done

Skill je pro tuto fázi „adopted“, pokud platí:

```text
[1] dokážu definovat
[2] dokážu vysvětlit mechanismus
[3] znám hlavní parametr(y)
[4] umím uvést failure mode
[5] umím vytvořit mikropříklad
[6] umím implementovat minimální verzi
[7] umím změřit výsledek
[8] umím vysvětlit výsledek bez LLM
```

Skill je „verified“ teprve tehdy, když existuje reálný artefakt.

---

# 49. Nejvyšší SNR mentální model

Celou doménu lze pro začátek komprimovat na jednu otázku:

> **Jak převést data na užitečné rozhodnutí a jak prokázat, že cesta od dat k rozhodnutí funguje?**

ML:

```text
data → learned function → prediction
```

Retrieval:

```text
query → representation → ranking → relevant context
```

AI engineering:

```text
context + model + tools → useful action
```

MLOps:

```text
experiment → deployment → observation → controlled change
```

Epistemický rámec:

```text
observation
→ representation
→ inference
→ validation
→ intervention
→ new observation
```

Celé portfolio lze chápat jako jeden opakovaný pattern:

> **bordel → struktura → model → evidence → akce → feedback**

---

# 50. References / současný stav systému

- `ML_Ops_Education`: https://github.com/outpost2026/ML_Ops_Education
- `MCP-Jobs`: https://github.com/outpost2026/MCP-Jobs
- `linkedin-mcp-analyzer`: https://github.com/outpost2026/linkedin-mcp-analyzer
- `outpost2026 portfolio`: https://github.com/outpost2026
- Google ML Glossary: https://developers.google.com/machine-learning/glossary/metrics
- Dense Retrieval survey: https://doi.org/10.1145/3637870
- Retrieval/RAG evaluation review: https://www.mdpi.com/2504-2289/9/12/320

Poznámka: standardní definice Precision@K, Recall@K a MRR jsou konzistentní s běžnou IR literaturou; nDCG je vhodné chápat jako position-aware metric s možností graded relevance. Viz uvedené zdroje.

---

# 51. One-page cheat sheet

```text
ML MODEL
ŷ = f(x; θ)

x = input
y = ground truth
ŷ = prediction
θ = learned parameters
λ = hyperparameters

TRAINING
data → prediction → loss → parameter update

RETRIEVAL
query → representation → candidates → ranking → top-k

SPARSE
TF-IDF / BM25

DENSE
embeddings / vector similarity

HYBRID
sparse + dense → RRF

METRICS
Precision@K = purity of top-k
Recall@K    = coverage of relevant set
MRR         = first relevant rank
MAP         = multi-hit ranking quality
nDCG        = graded/position-aware ranking quality

BM25
k1 = TF saturation behavior
b  = document-length normalization

RRF
rank fusion across retrievers

MLOPS
data → train → evaluate → registry → deploy → monitor → feedback

AI ENGINEERING
retrieve → context → model → tools → output → evaluate

SKILLS
market demand
→ gap
→ learning
→ implementation
→ evidence
→ updated state
```

---

# 52. Final calibration

Současný stav není:

> „junior ML engineer“.

Je přesnější:

> **začínající AI/ML engineering generalista s neobvykle silným praktickým software/data substrátem, který teprve konsoliduje základní ontologii ML, retrieval a MLOps.**

Silná stránka:

```text
stavění systémů
```

Hlavní deficit:

```text
hloubka formálního modelu ML/IR terminologie
```

Proto je následující krok jasný:

> **méně nových technologií, více mechanistického porozumění již použitým technologiím.**

První cíl není „postavit další ML repo“.

První cíl je, aby `TF-IDF`, `BM25`, `k1`, `b`, `Precision@K`, `Recall@K`, `MRR`, `MAP`, `nDCG`, `RRF`, `embedding`, `x`, `y`, `ŷ`, `θ`, `λ`, `loss`, `overfitting` přestaly být **slova, která model za autora vysvětluje**, a staly se **nástroji, kterými autor sám myslí**.

---

## Status

**Artifact type:** educational playground / capability acquisition map  
**Next update trigger:** po dokončení první série Feynman + PBL laboratoří  
**Recommended first deep-dive:** `BM25 → k1/b → Precision@K → Recall@K → MRR → RRF → sparse vs dense`