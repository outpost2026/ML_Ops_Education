# RETRIEVAL_RESEARCH.md — Hluboký ponor do základních konceptů

> **Cíl tohoto dokumentu:** Vysvětlit klíčové koncepty informačního retrívalu a hodnocení tak, aby byly **plně srozumitelné i pro začátečníka** – metodou Feynmana, na základě **vlastního projektu** `ML_Ops_Education`. Žádné mýty, žádné „černé skříňky“. Každý termín je definován, odvozen a propojen s tvým kódem.

---

## 0. Co je to ML model obecně (bez mýtu neuronů)

Než se pustíme do konkrétních termínů, musíme si ujasnit, co **vůbec** znamená „ML model“. Většina lidí si pod tím představí neuronovou síť – to je **omyl**. Neuronová síť je **jedna z mnoha** architektur, ne definice ML.

### Definice

**Strojové učení (ML)** je proces, kdy **počítač z dat odvodí pravidla** (parametry) tak, aby **optimalizoval nějakou cílovou metriku** na nových, neviděných datech.

**ML model** je **matematická funkce** \( f: x \rightarrow y \), která:
- má **parametry** \( \theta \) (řecké písmeno „théta“) – **učí se z dat**,
- má **hyperparametry** \( \lambda \) (řecké písmeno „lambda“) – **nastavuje je člověk** před učením,
- přijímá **vstup** \( x \) (např. dotaz „timeout v MCP serveru“),
- vrací **výstup** \( y \) (např. seřazený seznam GT entry).

### Parametry \( \theta \) vs. Hyperparametry \( \lambda \)

| | **Parametry \( \theta \)** | **Hyperparametry \( \lambda \)** |
|---|---|---|
| **Kdo je nastavuje?** | Model **sám** z trénovacích dat | **Člověk** před tréninkem |
| **Mění se během učení?** | **Ano** – to je „učení se“ | **Ne** – jsou fixní pro daný běh |
| **Příklad** | Váhy v neuronové síti, **IDF váhy v BM25**, průměrná délka dokumentu | Počet vrstev, learning rate, **k1, b, k v RRF** |

### Tvrůj projekt jako ML model

Tvůj `mcp_retrieval` **je** ML model – **přesně podle definice**:

- **Vstup \( x \):** textový dotaz (např. `"timeout MCP server"`)
- **Výstup \( y \):** seřazený seznam GT entry s relevančním skóre
- **Parametry \( \theta \):** `df` (document frequency) – **odvozené z tvých 108 GT entries**, průměrná délka dokumentu `avg_dl`
- **Hyperparametry \( \lambda \):** `k1=1.5`, `b=0.75`, `k=60` (RRF) – **nastavil jsi ty** (a pak je ladil na P0-v2)
- **Trénovací data:** 108 GT entries (`gt_full.jsonl`)
- **Cílová metrika:** **MRR** – maximalizuješ ji laděním hyperparametrů

**Tímto způsobem jsi již vytvořil a provozoval ML model – bez jediné neuronky.** Gratuluji. 🎉

---

## 1. Základní metriky hodnocení retrívalu

### 1.1 Precision@K a Recall@K

**Problém:** Jak zjistíme, jestli náš retríval funguje dobře?

**Řešení:** Položíme **sadu testovacích dotazů**, u každého víme, **které dokumenty jsou relevantní** (tzv. **ground truth**). Pak změříme, jak dobře náš systém tyto dokumenty najde.

| Metrika | Definice | Vzorec | Příklad |
|---------|----------|--------|---------|
| **Precision@K** | **Podíl relevantních dokumentů** mezi **top K** vrácenými výsledky | \( \frac{\text{relevantní v top K}}{K} \) | Když vrátíš 5 dokumentů a 3 jsou relevantní → Precision@5 = 3/5 = **60 %**  |
| **Recall@K** | **Podíl všech relevantních dokumentů**, které jsi **zachytil** v top K | \( \frac{\text{relevantní v top K}}{\text{celkem relevantních}} \) | Když je v korpusu 10 relevantních dokumentů a ty jich vrátíš 3 v top 5 → Recall@5 = 3/10 = **30 %**  |

**Intuice:** Precision říká „z toho, co jsem našel, kolik bylo dobrých?“. Recall říká „ze všech dobrých, kolik jsem našel?“.

**V tvém projektu:** V `results/mmr_benchmark.json` máš `"Prec": 0.6733` – to je Precision@3 (tvá výchozí `top_k=3`). Znamená to, že v průměru **67,3 %** z prvních 3 výsledků bylo relevantních.

---

### 1.2 MRR (Mean Reciprocal Rank)

**Problém:** Precision a Recall neberou v úvahu **pořadí** – je jedno, jestli je relevantní dokument na 1. nebo 5. místě.

**Řešení:** MRR měří, **jak vysoko** je **první relevantní dokument**.

#### Definice krok za krokem:

1. **Reciprocal Rank (RR)** pro jeden dotaz = \( \frac{1}{\text{pozice prvního relevantního dokumentu}} \)
   - Je-li první relevantní dokument na **1. místě** → RR = \( 1/1 = 1.0 \) (perfektní)
   - Je-li na **3. místě** → RR = \( 1/3 \approx 0.333 \)
   - Není-li žádný relevantní → RR = 0

2. **Mean Reciprocal Rank (MRR)** = **průměr RR** přes **všechny testovací dotazy**

\[
MRR = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{rank_i}
\]

**V tvém projektu:**
- Baseline (SequenceMatcher): MRR = **0.6613**
- Tvoje vylepšení (BM25+Seq+RRF): MRR = **0.7067** → **zlepšení o 6,9 %**
- To znamená: v průměru je první relevantní dokument na pozici \( 1/0.7067 \approx 1.41 \) – tedy **téměř vždy na 1. nebo 2. místě**.

> MRR je **hlavní metrika**, kterou jsi optimalizoval – a proto je v README uvedena jako první.

---

### 1.3 Hit@K (neboli Success@K)

**Definice:** Podíl dotazů, kde **alespoň jeden relevantní dokument** byl v top K výsledcích.

**V tvém projektu:** Hits = **43/50** – z 50 testovacích dotazů mělo 43 alespoň jeden relevantní výsledek v top K. To je **86% úspěšnost**.

---

## 2. Základní retrívalové modely

### 2.1 TF-IDF (Term Frequency – Inverse Document Frequency)

**Problém:** Jak zjistit, které **slovo v dokumentu je důležité**?

**Intuice:** 
- Slovo, které se v dokumentu **často** opakuje → **důležité** pro tento dokument (TF)
- Slovo, které se **vyskytuje v mnoha dokumentech** → **méně důležité** (IDF)

#### Definice:

1. **TF (Term Frequency):** \( \text{tf}(t, d) = \frac{\text{počet výskytů termu } t \text{ v dokumentu } d}{\text{celkový počet termů v } d} \)

2. **IDF (Inverse Document Frequency):** \( \text{idf}(t) = \log \frac{N}{\text{df}(t)} \)
   - \( N \) = celkový počet dokumentů
   - \( \text{df}(t) \) = počet dokumentů, ve kterých se term \( t \) vyskytuje

3. **TF-IDF:** \( \text{tf-idf}(t, d) = \text{tf}(t, d) \times \text{idf}(t) \)

**Příklad:** Slovo „timeout“ se vyskytuje v 10 z 108 dokumentů. \( \text{idf} = \log(108/10) \approx 2.38 \). V dokumentu, kde se objeví 3×, má TF-IDF \( \approx 3/100 \times 2.38 \approx 0.071 \).

**V tvém projektu:** TF-IDF je základ, na kterém staví BM25 – BM25 je **vylepšená verze TF-IDF**.

---

### 2.2 BM25 (Best Matching 25)

**Problém s TF-IDF:** 
- TF-IDF lineárně roste s počtem výskytů – slovo, které se objeví 10×, má 10× vyšší váhu než slovo, které se objeví 1×. To ale neodpovídá realitě – **první výskyt je mnohem důležitější než desátý**.
- TF-IDF neřeší **délku dokumentu** – dlouhý dokument má přirozeně více výskytů každého slova.

**Řešení:** BM25 přidává **dvě věci**:
1. **Saturaci term frequency** – každý další výskyt přidává méně a méně (řízeno hyperparametrem `k1`)
2. **Normalizaci délkou dokumentu** – dlouhé dokumenty jsou penalizovány (řízeno hyperparametrem `b`)

#### Vzorec BM25:

\[
\text{score}(Q, D) = \sum_{t \in Q} \text{idf}(t) \cdot \frac{\text{tf}(t, D) \cdot (k_1 + 1)}{\text{tf}(t, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{\text{avgdl}}\right)}
\]

Kde:
- \( \text{tf}(t, D) \) = počet výskytů termu \( t \) v dokumentu \( D \)
- \( |D| \) = délka dokumentu (počet termů)
- \( \text{avgdl} \) = průměrná délka dokumentu v korpusu
- \( k_1 \) = hyperparametr – řídí **saturaci TF** 
- \( b \) = hyperparametr – řídí **normalizaci délkou**

---

### 2.3 Hyperparametry \( k_1 \) a \( b \) – podrobně

#### \( k_1 \) – saturace term frequency

**Co dělá:** Řídí, jak rychle **přestane být každý další výskyt termu přínosný**.

| Hodnota \( k_1 \) | Efekt |
|-------------------|-------|
| **0.0** | Každý výskyt **nepřidává žádnou váhu** – jen to, zda se term v dokumentu vůbec vyskytuje |
| **1.2** (default) | Standardní saturace – každý další výskyt přidává méně |
| **> 2.0** | TF téměř lineární – 10× výskyt = skoro 10× váha |

**V tvém projektu:** Původně `k1=1.5`, v P0-v2 navrhuješ `k1=1.2` – **nižší saturace** pro malý korpus, kde se termy vyskytují řídce.

#### \( b \) – normalizace délkou

**Co dělá:** Řídí, **jak moc** je dlouhý dokument penalizován.

| Hodnota \( b \) | Efekt |
|-----------------|-------|
| **0.0** | **Žádná** normalizace – délka dokumentu **nevadí** |
| **0.75** (default) | Standardní normalizace |
| **1.0** | **Plná** normalizace – dlouhé dokumenty jsou silně penalizovány |

**V tvém projektu:** Původně `b=0.75`, v P0-v2 navrhuješ `b=0.25` – **slabší normalizace**, protože tvůj korpus obsahuje dlouhé KB dokumenty, které by neměly být příliš penalizovány.

---

### 2.4 Sparse search vs. Dense search

| | **Sparse search** | **Dense search** |
|---|---|---|
| **Reprezentace** | **Řídký vektor** – většina hodnot je 0 (např. TF-IDF, BM25) | **Hustý vektor** – všechny hodnoty jsou nenulové (např. embedding z neuronky) |
| **Porovnání** | **Lexikální shoda** – hledá přesná slova | **Sémantická shoda** – hledá význam |
| **Výhody** | Přesné vyhledávání, interpretovatelné, rychlé | Chytá synonyma, kontext, význam |
| **Nevýhody** | Nechytá synonyma, "časový limit" ≠ "timeout" | Pomalejší, náročný na data, "černá skříňka" |
| **Příklady** | TF-IDF, BM25, Boolean search | Word2Vec, GloVe, BERT embeddings |

**V tvém projektu:**
- **Sparse:** BM25 – tvůj **vítězný přístup** (MRR 0.7067)
- **Dense:** Word2Vec (MRR 0.31) a GloVe (MRR 0.26) – **selhaly** kvůli malému korpusu a OOV (out-of-vocabulary) problémům

**Poučení:** Na malém, specializovaném korpusu (108 GT entries) **sparse vyhrává nad dense**. To je cenná praktická zkušenost.

---

## 3. Fúze výsledků – RRF

### 3.1 Problém

Máš **několik retrívalových systémů**:
- BM25 na **původním** dotazu
- BM25 na **rozšířeném** dotazu (synonyma)
- **SequenceMatcher** (fuzzy vyhledávání)

Každý vrátí jiné pořadí dokumentů. **Jak je sloučit do jednoho finálního pořadí?**

### 3.2 Řešení: RRF (Reciprocal Rank Fusion)

**Intuice:** Dokument, který je **vysoko ve všech seznamech**, by měl být vysoko i ve finálním výsledku.

**Vzorec RRF**:

\[
\text{RRF\_score}(d) = \sum_{i=1}^{m} \frac{1}{k + \text{rank}_i(d)}
\]

Kde:
- \( m \) = počet retrívalových systémů (u tebe 3)
- \( \text{rank}_i(d) \) = pozice dokumentu \( d \) v \( i \)-tém seznamu (1 = nejlepší)
- \( k \) = **hyperparametr** – konstanta, která **tlumí vliv** nízkých ranků

**Proč \( k \) je důležité:**
- \( k \) **malé** (např. 1) – rozdíl mezi 1. a 2. místem je velký (\( 1/1=1.0 \) vs \( 1/2=0.5 \))
- \( k \) **velké** (např. 60) – rozdíl je menší (\( 1/61 \approx 0.016 \) vs \( 1/62 \approx 0.016 \))

**V tvém projektu:**
- Původně `k=60` (standardní hodnota z literatury)
- V P0-v2 navrhuješ `k=20` – **větší váha pro top ranky**, aby se více prosadily dokumenty, které jsou vysoko ve všech seznamech

---

## 4. MMR (Maximal Marginal Relevance) – pro úplnost

**Problém:** Někdy nechceš jen **relevantní** dokumenty, ale chceš, aby byly **různorodé** – aby pokrývaly různé aspekty dotazu.

**Řešení:** MMR **vyvažuje** relevanci a diverzitu.

\[
MMR = \arg\max_{D_i \in R} \left[ \lambda \cdot \text{Sim}_1(D_i, Q) - (1 - \lambda) \cdot \max_{D_j \in S} \text{Sim}_2(D_i, D_j) \right]
\]

Kde:
- \( \lambda \) = hyperparametr – váha relevance vs. diverzita
- První část = relevance k dotazu
- Druhá část = penalizace za podobnost s již vybranými dokumenty

**V tvém projektu:** MMR jsi testoval (MRR 0.598) – nevyhrál, ale je to užitečný koncept pro případy, kdy chceš různorodé výsledky (např. při sumarizaci).

---

## 5. Propojení s tvým kódem – kde to všechno najdeš

| Koncept | Kde v projektu | Soubor |
|---------|----------------|--------|
| **TF-IDF / BM25** | Implementace BM25 od nuly | `retrieval.py` – třída `BM25` |
| **SequenceMatcher** | Fuzzy vyhledávání | `retrieval.py` – `fuzzy_score()` |
| **RRF** | Fúze 3 výsledkových listů | `retrieval.py` – `rrf_fusion()` |
| **MRR benchmark** | Vyhodnocení všech přístupů | `results/mmr_benchmark.json` |
| **Word2Vec / GloVe** | Dense retríval (selhal) | `scripts/d1_word2vec_retrieval.py` |
| **SVD** | Dimenziální redukce | `scripts/svd_expansion_retrieval.py` |

---

## 6. Shrnutí – mentální mapa

```
                        INFORMAČNÍ RETRÍVAL
                               │
              ┌────────────────┼────────────────┐
              │                │                │
         SPARSE            DENSE           HYBRID
         (BM25)        (Word2Vec)     (BM25+RRF) ← TVŮJ VÍTĚZ
              │                │                │
         Hodnotí se metrikami:
         ┌─────────────────────────────────────┐
         │  Precision@K  │  Recall@K  │  MRR   │
         └─────────────────────────────────────┘
                        │
              BM25 má hyperparametry:
         ┌─────────────────────────────────────┐
         │  k1 (saturace TF)  │  b (normalizace)│
         └─────────────────────────────────────┘
                        │
              Fúze více systémů = RRF
         ┌─────────────────────────────────────┐
         │  k (RRF konstanta) – tlumí ranky    │
         └─────────────────────────────────────┘
```

---

## 7. Závěr – co sis osvojil

Tímto dokumentem jsi **prošel kompletní pipeline** informačního retrívalu:

1. **Víš, co je ML model** – a že jsi jeden vytvořil **bez neuronů**
2. **Rozumíš metrikám** – Precision, Recall, MRR – a víš, proč je MRR tvá hlavní metrika
3. **Chápeš BM25** – včetně hyperparametrů \( k_1 \) a \( b \) – a víš, proč měníš jejich hodnoty
4. **Rozlišuješ sparse a dense** – a víš, proč na tvém korpusu vyhrál sparse
5. **Umíš fúzovat výsledky** – pomocí RRF a víš, co dělá hyperparametr \( k \)

**Všechno toto jsi implementoval, otestoval a změřil – na reálných datech.**

To je **mnohem víc**, než co většina juniorních ML inženýrů umí. 🚀

---

*Zpracováno: 2026-08-28 | Na základě projektu `ML_Ops_Education` a `mcp-retrieval`*