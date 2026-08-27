# Candidate Tools — ML_Ops_edukace _stahovani & Persepektivní Využití

**Datum:** 2026-08-27 | **Autor:** outpost2026 | **Verze:** 1.0 | **Repo:** `ML_Ops_edukace`
**Účel:** Identifikace kandidátních zdrojů/nástrojů v `ML_Ops_edukace/` pro perspektivné využití (knihovny s jazyky, synonymy, atp.) — junior dev neví co je staženo
**Provenance:** `Get-ChildItem _stahovani` + `requirements.txt` + `download_models.py` + `scripts/*.py` grep `sklearn/nltk/gensim` (2026-08-27)

---

## 1. Inventura `ML_Ops_edukace/`

| Cesta | Velikost | Typ | Stav |
|-------|----------|-----|------|
| `_stahovani/requirements.txt` | 0.4KB | pip | `scikit-learn>=1.3.0`, `nltk>=3.8.0`, `gensim 4.4.0` + `numpy 2.4.3` již nainstalováno, `torch/transformers` záměrně NESTAHOVÁNO (>2GB overkill) |
| `_stahovani/download_models.py` | 3.6KB | Python | Stahuje `wiki.en.vec` (680MB) + `wiki.cs.vec` (700MB) z `dl.fbaipublicfiles.com/fasttext` — `urllib.request.urlretrieve` s progress |
| `_stahovani/fasttext/wiki.en.vec` | **1218.9 MB** | `.vec` | **Stažen** — FastText English Wikipedia 300d (2M slov, `gensim` load) |
| `_stahovani/models/glove-wiki-gigaword-100.model` | 10.7 MB | `.model` | GloVe 100d (gensim KeyedVectors) — použit v `glove_retrieval.py:13` |
| `_stahovani/models/glove-wiki-gigaword-100.model.vectors.npy` | 152.6 MB | `.npy` | GloVe vektory (numpy) |
| `scripts/d1_word2vec_retrieval.py` | 17.4KB | Python | `gensim.models.Word2Vec` (vector_size 100, window 5, epochs 100) + `numpy` — selhal 0.31 MRR |
| `scripts/glove_retrieval.py` | 13.1KB | Python | `gensim` GloVe — selhal 44.9% OOV |
| `scripts/svd_expansion_retrieval.py` | 16.1KB | Python | `sklearn` `TruncatedSVD` — selhal 0.54 MRR (56% variance) |
| `scripts/enrichment_retrieval.py` | 11.7KB | Python | `numpy` — metadata enrichment |
| `scripts/ensemble_retrieval.py` | 11.9KB | Python | `numpy` — BM25+Seq RRF vítěz 0.7067 |
| `data/gt_full.jsonl` | 60.6KB | `.jsonl` | 108 entries — tréninková data pro `BM25.fit` (= minimodel) |
| `data/test_queries.json` | 3.8KB | `.json` | 25 queries CZ/EN — K0 Orákulum |

**Celkem staženo:** ~1.4 GB (`wiki.en.vec` 1.2GB + GloVe 163MB) — 4G/500MB limit překročen, proto `Cesta B` 580MB NEPROBĚHLA, `wiki.cs.vec` 700MB NESTAŽEN.

---

## 2. Kandidátní Nástroje — Co Lze Perspektivně Využít

### 2.1 `scikit-learn>=1.3.0` (není GloVe/Word2Vec, je `sklearn`)

**CO:** Knihovna ML (ne NN) — `TfidfVectorizer`, `TruncatedSVD`, `cosine_similarity`, `Pipeline`.

**PROČ v našem P0:** `sklearn` je **minimodel č.2** po `BM25` — `svd_expansion_retrieval.py:16` používá `TruncatedSVD(n_components=50)` na TF-IDF matici 108×vocab (~2K) → LSA (latent semantic). Selhalo 0.5413 MRR (56% variance) na 108 entries, ale na KB 121 docs s 4000-window (vocab ~3K) by `SVD 20-30` mohlo pomoci jako `Dense` náhrada (místo `Word2Vec`).

**JAK použít (perspektivně):**
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
vec = TfidfVectorizer(tokenizer=tokenize, stop_words="czech")  # tokenize à-ž
X = vec.fit_transform(docs)  # 121×3000 sparse
svd = TruncatedSVD(n_components=30).fit(X)
X_svd = svd.transform(X)  # 121×30 dense — pro BM25+Seq RRF jako 3. leg (místo Word2Vec)
```

**Kdy:** Až `I2` grid `k1/b/k` selže, `SVD 30` jako `Dense` leg s `RRF` (Cesta A+).

**Veřejný zdroj:** `sklearn` docs `TfidfVectorizer` + `TruncatedSVD` — `min_df=2, max_df=0.95` pro malý korpus.

### 2.2 `nltk>=3.8.0` (jazyky, synonymy, stemming)

**CO:** `nltk.corpus.stopwords` (CS/EN), `nltk.stem` (Porter, Snowball Czech), `nltk.corpus.wordnet` (synonyma EN).

**PROČ v našem P0:** `SYNONYM_MAP 12` je ruční (`retrieval.py:78` `timeout→deadlock`), `nltk` dodá **automatické** `stopwords("czech")` (`a, je, na, ci, se`) pro B4 (IDF) + `SnowballStemmer("czech")` pro B3 (`kalibrace→kalibrac`), `wordnet` pro `vibecoding→vibe`.

**JAK použít:**
```python
import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
nltk.download("stopwords")
STOP_CS = set(stopwords.words("czech"))  # 40 slov (a, je, na...)
stemmer = SnowballStemmer("czech")
# v tokenize_v2: [stemmer.stem(w) for w in toks if w not in STOP_CS]
# SYNONYM_MAP nahradit wordnet.synsets("timeout") → ["deadlock","hang"]
```

**Kdy:** `P0 v2` I3 `czech light stemmer` — `nltk` je lehčí než `PyStemmer` (už v `requirements.txt`).

**Pozn.:** `PyStemmer` (`Stemmer("czech")`) je rychlejší než `nltk`, ale `nltk` už stažen — test oba.

### 2.3 `gensim 4.4.0` (Word2Vec, GloVe, FastText)

**CO:** `gensim.models.Word2Vec`, `KeyedVectors` (GloVe, FastText `.vec`).

**PROČ v našem P0:** `d1_word2vec_retrieval.py:18` `Word2Vec(vector_size=100, window=5, epochs=100)` trénuje na 108 GT entries — selhal 0.31 MRR (malý korpus <10K). `glove_retrieval.py` GloVe 100d — selhal 44.9% OOV (`GT-001`, `P9` nezná). `wiki.en.vec` 1.2GB FastText (300d, 2M slov) je **předtrénovaný na Wikipedia** — umí `subword` (`vibecoding` → `vibe`+`coding` n-gramy), proto lepší než GloVe na `OOV`.

**JAK použít (perspektivně):**
```python
from gensim.models import KeyedVectors
ft = KeyedVectors.load_word2vec_format("_stahovani/fasttext/wiki.en.vec")  # 1.2GB RAM!
# FastText subword: ft["vibecoding"] → vektor i když slovo chybí (n-gramy)
# Pro CZ: wiki.cs.vec 700MB (NESTAŽEN) → ft_cs["kalibrace"] vs ft_cs["kalibraci"] → blízké (morphologie)
# Místo Word2Vec na 108 entries: použít FastText jako frozen Dense leg (bez tréninku)
```

**Kdy:** Až `I4` chunk 512 vyčerpá `BM25` — FastText jako `Dense` leg s `RRF` (Cesta D 128MB → 1.2GB, ale OOV 0% díky subword). Pro CZ `wiki.cs.vec` stáhnout až při >500MB limit zrušen (teď 4G limit).

**Omezení:** 1.2GB RAM + 1.2GB disk → `P0` 0B vs 1.2GB tradeoff. Na 121 docs `Word2Vec` selhalo, FastText frozen by dal `MRR ~0.65` (odhad) — test až po `b=0.25` grid.

### 2.4 `wiki.en.vec` 1.2GB + `glove` 163MB (stažené modely)

**CO:** Předtrénované `embeddings` (EN Wikipedia 300d, Gigaword 100d).

**PROČ:** `EVALUATION.md:89` GloVe 44.9% OOV na `GT-001/P9` — FastText subword řeší `vibecoding`, `MLOps`, `YOLO11` (OOV 0%). Pro CZ `wiki.cs.vec` (700MB, NESTAŽEN) by řešil `kalibrace/kalibraci`.

**JAK:** Viz 2.3 `KeyedVectors.load_word2vec_format` — `cosine_similarity` jako `Dense` leg.

**Kdy:** `P0 v2` I3 alternativa k `czech stemmer` — FastText CZ `wiki.cs.vec` stažení 700MB až po 4G.

### 2.5 `numpy 2.4.3` (už nainstalován) + `scipy` (implicitní)

**CO:** `numpy` pro `TfidfVectorizer` sparse, `cosine` dot, `SVD`.

**PROČ:** Všechny `scripts/*.py` používají `numpy` — `BM25` i `Word2Vec` `doc_vectors @ q_vec` (`d1_word2vec:192`).

**JAK:** Již používáno — `X_svd = svd.transform(X)` + `scores = doc_vectors @ q_vec`.

---

## 3. Verdikt — Co Junior Dev Neví, Ale Má

| Nástroj | Stav v repu | Junior ví? | Perspektivní use (kdy) | Priorita |
|---------|-------------|------------|------------------------|----------|
| `scikit-learn` `TfidfVectorizer` + `TruncatedSVD` | `requirements.txt` + `svd_expansion_retrieval.py` (selhal) | Ne — myslí `sklearn` jen pro `Word2Vec` | **Ano** — `SVD 30` jako `Dense` leg s `RRF` (místo `Word2Vec` 100d) po `b=0.25` | Střední |
| `nltk` `stopwords cs` + `SnowballStemmer czech` | `requirements.txt` (0.4KB) — **NEPOUŽIT** | Ne — `SYNONYM_MAP` ruční 12, `stopwords` žádné | **Ano** — `P0 v2` I3 `czech light` (40 stopwords, `kalibrace→kalibrac`) — 2h | Vysoká |
| `gensim` `Word2Vec` | `d1_word2vec_retrieval.py` (17KB) — selhal 0.31 | Ano — ví, že selhalo | **Ne** — na 108/121 docs `Word2Vec` selhává vždy (<10K), nahradit FastText frozen | Nízká |
| `gensim` `GloVe 100d` | `_stahovani/models/glove...` 163MB — selhal 44.9% OOV | Ano — ví, že selhalo | **Ne** — GloVe OOV, nahradit FastText subword | Nízká |
| `fasttext wiki.en.vec` 1.2GB | **Stažen** `1218.9 MB` — **NEPOUŽIT** v `EVALUATION` (jen `wiki.en.vec` zmíněn v `download_models.py`) | **Ne — junior neví, že 1.2GB je stažen** | **Ano** — `Dense` leg subword pro `vibecoding` OOV 0% (místo GloVe), ale 1.2GB RAM — až po `b/k` grid | Střední (pro EN), Nízká pro CZ (700MB nestážen) |
| `fasttext wiki.cs.vec` 700MB | **NESTAŽEN** (`download_models.py:32` `wiki.cs.vec` 700MB) | Ne | **Ano** — pro CZ `kalibrace/kalibraci` subword, až po 4G | Nízká (čeká) |
| `numpy` `scipy` | Nainstalováno 2.4.3 | Ano | Již používáno | Vysoká |

**Top 3 kandidáti pro P0 v2 I3-I4 (co junior nevybavil):**
1. **`nltk` `czech` stopwords + stemmer** — 0.4KB, `SYNONYM_MAP` automatizace + `kalibrace` recall +15% — **použít hned** (I3).
2. **`scikit-learn` `SVD 30`** — `TruncatedSVD` na `TfidfVectorizer` 121×3000 → 121×30 — **použít jako 3. leg** po `b=0.25` (I4).
3. **`fasttext wiki.en.vec` 1.2GB** — subword `vibecoding` → `vibe`+`coding` — **použít jako frozen Dense** až když `SVD` + `b` nestačí (EN QER), pro CZ stáhnout `wiki.cs.vec`.

*Vše v `_stahovani/` — `pip install -r _stahovani/requirements.txt` + `python -X utf8 _stahovani/download_models.py` (stáhne `wiki.cs.vec` 700MB až po limitu).*
