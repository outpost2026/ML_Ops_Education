# Glossary — ML/RAG/QER ontologie via BASE (cnc_tools_kb_search)

**Datum:** 2026-08-27 | **Zdroj:** 18 docs retrieved via BASE (cnc_tools_kb_search) | **Korpus:** 121 KB + 14 ML/RAG/QER = 135 docs
**Metriky:** MRR 0.2905 Prec@3 0.1429 Recall 0.3333 Hits 6/7
**Dotazy:** 7 (ML RAG QER ontologie) — `ONTO_Q0` original + 6 inferred QER/RTF/RAG

## Zdroje (retrieved top5 per query, dedup)

- `01_METODIKY/04_skill_acquisition/SKILL_GAPS_ROZBOR_Q3_2026_v2.md`
- `01_METODIKY/06_SWE_glossary/SWE_GLOSSARY_zive_v1.md`
- `02_ANALYZY/04_workspace_audit/SQL_KANDIDATI_IMERZE_2026-08-15.md`
- `00_STRATEGIE/01_positioning/SQL_ADOPCE_PLAN_2026-08-16.md`
- `01_METODIKY/TRIMMING_PLAN_04_KNOWLEDGE_BASE_2026-08-01.md`
- `02_ANALYZY/07_CV_automatizace/CV_YOLO11_ADOPTION_ASSESSMENT_v1.md`
- `02_ANALYZY/00_linkedin/metadata_stacku.json`
- `README.md`
- `01_METODIKY/04_skill_acquisition/ADOPCNI_METODOLOGIE_2026_v1.md`
- `02_ANALYZY/04_workspace_audit/DE_NOVO_SEMANTICKY_AUDIT_STRUKTURY_KB_2026-08-15.md`
- `02_ANALYZY/04_workspace_audit/KORELACE_STRUKTURY_KB_2026-08-15.md`
- `05_EPISTEMIKA/00_kompresni_realismus/Kompresni_modelovani_v_praxi_synteza_v1.md`
- `05_EPISTEMIKA/02_agentni_pravidla/HANDOFF_COMPACT.md`
- `05_EPISTEMIKA/01_kalibracni_matice/kalibracni_matice.json`
- `01_METODIKY/05_testing/Falsifikacni_test_single_game_discovery_v1.md`
- `04_KNOWLEDGE_BASE/01_MCP/MCP_GROUND_TRUTH_postmortem_agregovany_v2.md`
- `05_EPISTEMIKA/03_kognitivni_ontologie_nastroju/POSTGRESQL_ontologie_epistemika_2026-08-18.md`
- `AGENTS.md`

## Glossary — ontologie ML/RAG/QER

| Term | Definice (zkráceně) | Zdroj |
|------|---------------------|-------|
| **100% determinismus** |   100% determinismus   LLM se muze rozhodnout tool nepouzít   Skript/Makefile   | `MCP_GROUND_TRUTH_pos` |
| **Archivace 9 souborů** |   Archivace 9 souborů   Žádné mazání, ale 4 pitevní knihy má nahrazovat 1 GT — 5 | `TRIMMING_PLAN_04_KNO` |
| **Credentials / secrets** |   Credentials / secrets   Riziko úniku do LLM kontextu   OS env var + gh CLI   | `MCP_GROUND_TRUTH_pos` |
| **Data Pipeline (ETL)** |   **Data Pipeline (ETL)**   Produkční   Meteo miner, RAG, scraping   ✅ Přímý — z | `CV_YOLO11_ADOPTION_A` |
| **Datum: 2026-07-28** | **Datum:** 2026-07-28   **Autor:** outpost2026 + LLM (falsifikační test) | `Kompresni_modelovani` |
| **Datum: 2026-08-02** | **Datum:** 2026-08-02   **Autor:** outpost2026 + LLM (falsifikační test) | `Falsifikacni_test_si` |
| **Glossary termíny z SQL imerze** |   Glossary termíny z SQL imerze   5+ nových kontextovaných termínů (JOIN, index, | `SQL_KANDIDATI_IMERZE` |
| **Koncept mapy = otrava** |   **Koncept mapy = otrava**   Střední   Nízký   Mermaid diagramy generované LLM, | `ADOPCNI_METODOLOGIE_` |
| **LLM nástroje** |   **LLM nástroje**   `05_EPISTEMIKA/01_kalibracni_matice` + `01_METODIKY/00_agen | `DE_NOVO_SEMANTICKY_A` |
| **Merge PET felt ontologie** |   Merge PET felt ontologie   Konflikt registru barev = dvě pravdy v RAG; jeden k | `TRIMMING_PLAN_04_KNO` |
| **PBL přepisování LLM kódu bez pochopení** |   **PBL přepisování LLM kódu bez pochopení**   Střední   Vysoký   Anti-blackbox: | `ADOPCNI_METODOLOGIE_` |
| **RAG ontologie pravidel** |   RAG ontologie pravidel   KB_moduly_RAG_v1.0.md (v32) + ontologie v3.2.md   Ste | `TRIMMING_PLAN_04_KNO` |
| **S2 KROK 0** |   **S2** KROK 0   **Master dir index SQLite+FTS5** — 1 schema + 1 crawler + 5 an | `SQL_ADOPCE_PLAN_2026` |
| **SQLite + FTS5 (MATCH, BM25)** |   **SQLite + FTS5** (MATCH, BM25)   **NEOVČIČENO**   KROK 0 (V3 revize)   | `SQL_ADOPCE_PLAN_2026` |
| **SRS opuštěno po 2 týdnech** |   SRS opuštěno po 2 týdnech   Vysoká   Střední   10 min/den fixní, LLM generuje  | `SQL_ADOPCE_PLAN_2026` |
| **Server: lichess-analyzer** | **Server:** lichess-analyzer   **Status:** Fixed   **Typ:** Data integrity — LLM | `MCP_GROUND_TRUTH_pos` |
| **Stack** |   **Stack**   Markdown, JSON, Git, RAG-ready struktura, agentní přístup přes ope | `README.md` |
| **Verze: 1.0** | **Verze:** 1.0   **Datum:** 2026-07-18   **Účel:** Jediný zdroj pravidel pro LLM | `AGENTS.md` |
| **Verze: 1.0-compact** | **Verze:** 1.0-compact   **Datum:** 2026-06-22   **Účel:** Sémantická komprese K | `HANDOFF_COMPACT.md` |
| **Vlastnost** |   Vlastnost   Křemík (LLM)   Uhlík (mozek)   | `HANDOFF_COMPACT.md` |
| **`CNC_2_LLM`** |   `CNC_2_LLM`   DXF geometrický indexer + sémantický embedding pro ERP   PRIVATE | `HANDOFF_COMPACT.md` |
| **`Free_LLM_openrouter.txt`** |   `Free_LLM_openrouter.txt`   01_METODIKY/00_agentni_prace   05_EPISTEMIKA/01_ka | `DE_NOVO_SEMANTICKY_A` |
| **`mcp_jobs_pitevni_kniha_v1.md`** |   `mcp_jobs_pitevni_kniha_v1.md`   Entry 022-035 (plné znění)   Cross-LLM audit  | `MCP_GROUND_TRUTH_pos` |
| **docx → archive** |   docx → archive   Binární duplikát bez RAG hodnoty, 546 KB   100% binární úspor | `TRIMMING_PLAN_04_KNO` |
| **ffts-grep (mneves75)** |   **ffts-grep** (mneves75)   Rust, single binary   SQLite FTS5 + BM25, ~10 ms na | `SQL_KANDIDATI_IMERZE` |

## Poznámka PBL
Glosář je syntéza z retrieved docs, ne ruční výběr — `via base` = `score=sum` (substring), `via P0` = `BM25+RRF` (IDF+RRF). Rozdíl je v rankingu vzácných `QER/RTF/BM25` (df 2-4) vs častých `LLM/MCP` (df 50+).
