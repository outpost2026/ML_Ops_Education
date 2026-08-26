# MCP GROUND TRUTH — Agregovaná pitevní kniha

**Datum:** 2026-08-26 | **Verze:** 20 (souborová generace v2; interní řada pokračuje z v1/v19)
**Účel:** Jediný zdroj pravdivých ponaučení z vývoje všech MCP serverů v portfoliu. Nahrazuje: linkedin_mcp_pitevni_kniha_v1.md, mcp_jobs_pitevni_kniha_v1.md, sdilena_pitevni_kniha_mcp.md, MCP_komplexni_analyza_a_strategie_v1.md (pouze postmortem části), pitevni_kniha_mcp_v1.md (cnc-tools).
**Rozsah:** linkedin-mcp-custom, MCP-Jobs, mcp-local-server (cnc-tools), lichess-analyzer-mcp, GCP infrastructure (pitevni_kniha_v8)
**Určení:** Výukový materiál pro deva, instrukce pro LLM, ground truth pro rozhodování
**Provenance trimu:** v2 = trim iterace A nad v1/v19 (sémantická analýza 2026-08-26): dedup `Pravidlo:` textů entrií → ukazatele (kanonický text v §4), kanonizace P80–P83 a P90–P96 do §4, odstranění duplicitního changelogu a statistického narrativu, komprese sekundárních pasáží. Zachováno: všech 108 GT záznamů, 48 Provenance polí, file:line reference. Historie verzí = git log repa.
**Skill:** Před editací loadni `skill({name: "kb-workflow"})` → sekce Postmortem Workflow obsahuje pravidla pro konzistentní zápis GT/P a prevenci konfabulace.

---

## 1. Mapa superseded artefaktů

| Původní soubor | Co se přebírá | Co se zahazuje |
|----------------|---------------|----------------|
| `linkedin_mcp_pitevni_kniha_v1.md` | Entry 007-024 (plné znění) | Duplicitní statistiky, Session 3→4 timeline (historický) |
| `mcp_jobs_pitevni_kniha_v1.md` | Entry 022-035 (plné znění) | Cross-LLM audit metoda 032 (meta-poznatek, ne bug) |
| `sdilena_pitevni_kniha_mcp.md` | Průřezová pravidla P1-P23, Entry 001-028 (stručné) | Duplicitní popisy (odkazovaly na originály) |
| `pitevni_kniha_mcp_v1.md` (cnc-tools) | Entry 001-014, Diagnostický filtr, P24-P28 | Cross-referenční mapa (nyní redundantní) |
| `MCP_komplexni_analyza_a_strategie_v1.md` | §9 Secret exposure, EROI framework, §10-11 akční plány | §1 Fenomén MCP, §4 Rešerše, §6 Use case, §7 Predikce |
| `MCP_practical_workflow_guide_v1.md` | §7 Falsifikace, §8 Rozhodovací framework | §2 Filosofie, §3 Scénáře (není postmortem) |
| `GCP/pitevni_kniha_v8.md` | GT-GCP-001..005 (5 entries, GCP infra: 5vrstvá auth, cron context, immutable infra, statelessness, Hard Reset) | Zbytek (~30 záznamů): inferovatelné z obecných SE principů nebo příliš specifické |

---

## 2. Nálezy agregace (komprimováno ve v2)

Vyřešené rozpory statusů při agregaci: Entry 016 (Fixed), Entry 020 (Fixed), input validation (Implementováno, Session 16); jednotné číslování GT#ID se zdrojovým ID v závorce. Eliminované duplicity: encoding/shell/quoting (6 zápisů → GT-031), MCP transport timeout (3 výskyty → GT-013), EROI matice a secret exposure sloučeny. Odstraněn nepostmortem obsah (tržní analýza, predikce 2027, filosofické pasáže, tabulky veřejných serverů). Zachovány unikátní části: Diagnostický filtr, WF simulace v3, 6-layer encoding stack (GT-041), L2 Resources architektura (GT-040).

---

## 3. Katalog chyb

108 záznamů: GT-001..GT-105 + GT-GCP-001..005. V závorce původní ID ze zdrojového artefaktu.

**Číslování a rezervace:** GT-082 a GT-084 nebyly přiděleny (mezera vznikla ve v10); P78/P79 neexistují; P84–P89 jsou rezervovány epistemické řadě (Gate protokol destruktivních operací). Sekce katalogu čísluje 3.1–3.3 a 3.5–3.7 (mezera 3.4 historická, zachována kvůli externím referencím).

**Formát záznamu:** Symptom → Root cause → Fix → Pravidlo (ukazatel; kanonický text pravidla viz §4) → Provenance.

### 3.1 cnc-tools (mcp-local-server)

#### GT-001 (CNC-001): Sekvenční bottleneck — Cross-repo paralelizace
**Server:** cnc-tools | **Status:** Fixed

**Symptom:** `MCP error -32001` při `tool_git_status_all`/`tool_cross_repo_search`; audit `duration_s` 61.7–62.4 s (>60 s client timeout).
**Root cause:** Sériová iterace 14 repozitářů v jedné smyčce (14 × 4.4 s).
**Fix:** `ThreadPoolExecutor(max_workers=4)` → ~15 s.
**Pravidlo:** P1

#### GT-002 (CNC-002): Vnořené timeouty bez signalizace
**Server:** cnc-tools | **Status:** Fixed

**Symptom:** `tool_git_diff` error až po 60 s (30 s subprocess + 30 s client = dvojité čekání).
**Root cause:** Subprocess timeout (30 s) příliš blízko client timeoutu (60 s).
**Fix:** Subprocess timeout ≤15 s — fail fast.
**Pravidlo:** P2

#### GT-003 (CNC-003): Read-only git s write lockem
**Server:** cnc-tools | **Status:** Fixed

**Symptom:** `git status`/`git diff` trvaly 3–5 s na read-only operaci.
**Root cause:** Git implicitně zapisuje `.git/index.lock`; chyběl `--no-optional-locks`.
**Fix:** `["git", "--no-optional-locks", ...]` ve všech subprocess voláních.
**Pravidlo:** P3

#### GT-004 (CNC-004): JSON data corruption — session state
**Server:** cnc-tools | **Status:** Fixed

**Symptom:** `tool_session_state` failuje `'str' object has no attribute 'get'`.
**Root cause:** `.ai_state.json` obsahoval string místo dict; `v.get()` padá na non-dict.
**Fix:** `isinstance(v, dict)` check + auto-repair mechanismus.
**Pravidlo:** P4

#### GT-005 (CNC-005): Absence duration metriky
**Server:** cnc-tools | **Status:** Fixed

**Symptom:** Bez audit logu nelze identifikovat zdroj timeoutu (šedá zóna subprocess/client timeout).
**Root cause:** Žádná per-tool duration telemetrie.
**Fix:** `@auditable` dekorátor na všech tool funkcích; povinné `ts`, `tool`, `duration_s`, `ok`.
**Pravidlo:** P5

#### GT-006 (CNC-006): Absence timeout guardu
**Server:** cnc-tools | **Status:** Fixed

**Symptom:** Jeden pomalý tool (62 s) blokuje celý STDIO server (half-duplex).
**Root cause:** FastMCP nemá per-tool timeout.
**Fix:** Wrapper s `concurrent.futures.TimeoutError` pro I/O tooly >10 s.
**Pravidlo:** P6

#### GT-007 (CNC-007): LLM blind path navigation
**Server:** cnc-tools | **Status:** Fixed

**Symptom:** LLM volá nástroje s `C:\_github\...` → „mimo povolený rozsah"; 2–3 iterace hádání cesty.
**Root cause:** `ALLOWED_ROOTS` je interní konstanta — LLM nemá mechanismus, jak ji zjistit.
**Fix:** `tool_workspace_info()` + workspace root do stderr při startu.
**Pravidlo:** P17

#### GT-008 (CNC-008): Console encoding corruption
**Server:** cnc-tools | **Status:** Fixed

**Symptom:** `UnicodeEncodeError: 'charmap' codec` při tisku emoji/Unicode (Windows cp1250 console).
**Root cause:** Windows Console + Python stdout encoding = cp1250.
**Fix:** `sys.stdout.reconfigure(encoding='utf-8', errors='replace')` + `$env:PYTHONIOENCODING='utf-8'`.
**Pravidlo:** P18 + P23

#### GT-009 (CNC-009): Pre-release Python deadlock
**Server:** cnc-tools | **Status:** Fixed

**Symptom:** Všechny git nástroje timeoutují -32001 po 60 s; git z bash <1 s.
**Root cause:** Python 3.11.0rc2 — nedokončený subprocess pipe management na Windows → pipe buffer deadlock.
**Fix:** Stable Python (3.11.9); `requires-python` vylučuje rc verze.
**Pravidlo:** P24

#### GT-010 (CNC-010): StreamHandler stderr deadlock
**Server:** cnc-tools | **Status:** Fixed

**Symptom:** Latentní deadlock i po fixu verze Pythonu.
**Root cause:** `StreamHandler(sys.stderr)` v audit.py — plná pipe buffer (4–64 KB) → event loop freeze → MCP timeout.
**Fix:** StreamHandler odstraněn, pouze FileHandler.
**Pravidlo:** P25

#### GT-011 (CNC-011): subprocess.run handle inheritance
**Server:** cnc-tools | **Status:** Fixed

**Symptom:** Git subprocess drží MCP STDIO handles → pipe se nikdy neuzavře → client timeout.
**Root cause:** `subprocess.run()` dědí všechny handles rodiče.
**Fix:** `asyncio.create_subprocess_exec()` + `stdin=asyncio.subprocess.DEVNULL`.
**Pravidlo:** P26

#### GT-012 (CNC-012): MCP test pyramida
**Server:** cnc-tools | **Status:** Fixed

**Symptom:** 67 unit testů PASS, E2E odhalil 14 anomálií (git timeout, VCF binary, encoding) — transport-level vrstvy netestovány.
**Root cause:** Chyběla integration a E2E vrstva.
**Fix:** Pyramida unit → integration → E2E + smoke test po každé změně.
**Pravidlo:** P27

#### GT-013 (CNC-013 = LNKD-016 = JOBS merged): MCP transport timeout pro batch operace
**Server:** cross-repo | **Status:** Fixed

**Symptom:** `analyze_saved_jobs` (N=27, ~85 s) a `get_saved_jobs` → -32001; JSON-RPC/stdio má client timeout 60–120 s; sekvenční scraping N×~3 s limit překračuje.
**Root cause:** MCP není navržen pro long-running batch operace.
**Fix:** (1) per-job tool místo batch, (2) CLI test skript bypassující transport, (3) time-budget (`limit` + `max_seconds`, vracet `unprocessed_ids`).
**Pravidlo:** P13

#### GT-014 (CNC-014): WF simulace v3 — emoji v MCP outputu
**Server:** cnc-tools | **Status:** Fixed

**Symptom:** 6 toolů vracelo emoji markery ([OK], [FAIL], [!], [TIMEOUT]) místo ASCII-safe textu.
**Root cause:** Historický vizuální pozůstatek; nezachyceno code review ani testy.
**Fix:** Emoji → ASCII markery; CI-greppovatelný audit: `rg "[\u2600-\u27BF\U0001F000-\U0001FFFF]" src/`.
**Pravidlo:** P28

### 3.2 linkedin-mcp-custom

#### GT-015 (LNKD-007): Typová záměna BrowserContext vs Browser
**Server:** linkedin-mcp | **Status:** Fixed

**Root cause:** `get_or_create_browser()` vracelo `BrowserContext`, volající očekával `Browser` (Patchright rozlišuje process vs izolovaný session).
**Fix:** Singleton na úrovni `BrowserContext`; všechny tool funkce přijímají `context` a volají `context.new_page()`.

#### GT-016 (LNKD-008): Shadow lokální proměnná (missing global)
**Server:** linkedin-mcp | **Status:** Fixed

**Root cause:** Zápis do globální proměnné bez `global` deklarace vytvoří lokální shadow — `close_browser()` nastavovala lokální `_context = None`.
**Fix:** `global _context, _page, _playwright` v každé zapisující funkci.
**Pravidlo:** P7

#### GT-017 (LNKD-009): Auth navigační konflikt
**Server:** linkedin-mcp | **Status:** Fixed

**Root cause:** `is_logged_in()` volalo `page.goto("/feed/")` → opuštění cílové stránky; extrakce pokračovala na prázdné stránce.
**Fix:** Pořadí: (1) `ensure_authenticated(page)`, (2) navigace na target URL.
**Pravidlo:** P8

#### GT-018 (LNKD-010): Fragilita CSS selektorů
**Server:** linkedin-mcp | **Status:** Fixed

**Root cause:** LinkedIn A/B testy mění CSS class names bez varování → ephemeral selektory.
**Fix:** Dvě vrstvy: specifický CSS selector + text-based fallback (`innerText` matching).
**Pravidlo:** P9

#### GT-019 (LNKD-011): Paginační slepota
**Server:** linkedin-mcp | **Status:** Fixed

**Root cause:** (1) Přepisovač cílové stránky místo klikání na „Další", (2) po kliknutí bez čekání na DOM refresh.
**Fix:** `_click_next_page()` hledající „Další" + `wait_for_timeout(3000)` + `wait_for_selector`.

#### GT-020 (LNKD-012): Špatný git repo root v parents indexu
**Server:** linkedin-mcp | **Status:** Fixed

**Root cause:** `Path.parents` je 0-indexovaný od nejbližšího rodiče; použit `parents[2]` místo `parents[1]`.
**Fix:** Oprava indexu + `relative_to()` assert pro verifikaci.
**Pravidlo:** P10

#### GT-021 (LNKD-013): Fragilní extrakce job ID
**Server:** linkedin-mcp | **Status:** Fixed

**Root cause:** Extrakce hledala jen `[href*="/jobs/view/"]`; ID je i v data atributech, script JSON blobu, `aria-label`.
**Fix:** 4-vrstvá extrakce: `<a href>` → element attributes → script JSON → full outerHTML regex.

#### GT-022 (LNKD-014): KBWriter dedup fallback — industry vždy None
**Server:** linkedin-mcp | **Status:** Fixed

**Root cause:** `_find_entry_index()` porovnával `title|company` proti `title|company.industry` (vždy None) → company name se nikdy neukládala.
**Fix:** Ukládat `eroi.company` do `company.industry`.

#### GT-023 (LNKD-015): Summary table non-idempotent
**Server:** linkedin-mcp | **Status:** Fixed

**Root cause:** `_update_summary_table()` vždy appendovala řádek bez kontroly existence ID.
**Fix:** Existence-check před appendem; existuje-li → replace.

#### GT-024 (LNKD-017): Python version mismatch (.venv vs system)
**Server:** linkedin-mcp | **Status:** Fixed

**Root cause:** `.python-version` = 3.12, `.venv` vytvořen se system Python 3.11; závislosti vyžadují ≥3.12.
**Fix:** `uv venv --python 3.12 && uv sync`.

#### GT-025 (LNKD-018): Console script not in PATH
**Server:** linkedin-mcp | **Status:** Fixed

**Root cause:** `uv sync` instaluje konzolové scripty do `.venv/Scripts/`, který není v system PATH.
**Fix:** `.bat` wrapper v repo root + `.venv/Scripts` do User PATH.
**Pravidlo:** P11 + P12

#### GT-026 (LNKD-020): Cookie lifecycle — silent expiry
**Server:** linkedin-mcp | **Status:** Fixed

**Root cause:** Session cookies mají neurčitou expiraci (dny až týdny); bez pre-checku nedetekovatelné.
**Fix:** Cookie age tracking + checkpoint detection + `ensure_authenticated()` před každým scrapingem.
**Pravidlo:** P15

#### GT-027 (LNKD-021): CI/CD cookie export — cookies nejsou JSON
**Server:** linkedin-mcp | **Status:** Fixed

**Root cause:** Patchright persistent context ukládá cookies do Chromium SQLite databáze, ne JSON.
**Fix:** `scripts/export_cookies.py`: `context.cookies()` → JSON → GitHub Secret → `context.add_cookies()`.

#### GT-028 (LNKD-022): PAT workflow scope
**Server:** linkedin-mcp | **Status:** Documented

**Root cause:** `git push` rejectnut — PAT postrádá `workflow` scope.
**Fix:** Doplnit `workflow` scope v GitHub Developer settings.

#### GT-029 (LNKD-024): Scorer unit test discovery
**Server:** linkedin-mcp | **Status:** Fixed

**Root cause:** 6/27 nových testů měla očekávání neodpovídající skutečné scorer logice.
**Fix:** Testy opraveny na aktuální chování — slouží jako living documentation.

### 3.3 MCP-Jobs

#### GT-030 (JOBS-022): Silent failure pattern
**Server:** MCP-Jobs | **Status:** Fixed

**Root cause:** Všichni 4 scrapery `except Exception: continue` → tichá ztráta dat při změně HTML struktury.
**Fix:** Per-card `logger.warning()`, skip counter, 0-ads `logger.error()` alert.
**Pravidlo:** P19

#### GT-031 (JOBS-023/SHELL-019/PS-034): Salary regex / shell escaping / PS quoting
**Server:** MCP-Jobs / cross-repo | **Status:** Fixed / Mitigated

**Symptom:** (a) Salary filter rejectuje český formát čísla, (b) PowerShell v bash stringu 3/3 selhání, (c) f-string SyntaxError při `python -c "..."`.
**Root cause (společný):** Textová data nelze parsovat bez respektu locale/encoding; shell escaping na Windows je 3-vrstvý problém (PowerShell → cmd.exe → Python).
**Fix:** (1) `_SALARY_NUM_RE = re.compile(r'\d{1,3}(?:[ \u00a0]\d{3})+|\d+')` respektující český formát, (2) PowerShell operace jako `.ps1` soubory, (3) zákaz komplexního `python -c` na Windows.
**Pravidlo:** P16 + P22

#### GT-032 (JOBS-024): Exclude čeština — domain-specific semantics
**Server:** MCP-Jobs | **Status:** Fixed

**Root cause:** Czech exclude termíny (`poptavam`, `shanim`) aplikovány globálně; na Bazosu značí validní poptávku zaměstnance.
**Fix:** Portal-specific exclude listy; jednoznačné multiword `hledam praci` ponecháno.

#### GT-033 (JOBS-025): ETL feedback loop dependency
**Server:** MCP-Jobs | **Status:** Mitigated

**Root cause:** Žádný mechanismus pravidelného ověření funkčnosti scraperů; HTML portálů se mění bez varování.
**Fix:** ETL runner + session-start health check + `output/etl_latest.json`.
**Pravidlo:** P20

#### GT-034 (JOBS-026): LLM-assisted dev blind spots
**Server:** cross-repo | **Status:** Mitigated

**Root cause:** LLM detekuje degradaci existujícího kódu teoreticky, ale ne bez reálných dat.
**Fix:** Pravidelný ETL feedback loop + version comparison + testy na reálném HTML.

#### GT-035 (JOBS-027): AST re-parse per ad
**Server:** MCP-Jobs | **Status:** Fixed

**Root cause:** `parse_boolean()` voláno pro každý inzerát zvlášť (8 query × 1000 ads = 8000 parsování).
**Fix:** `@functools.lru_cache(maxsize=128)` → 8 parsování.

#### GT-036 (JOBS-028): Chybějící guardraily (pages + rate limiting)
**Server:** MCP-Jobs | **Status:** Fixed

**Root cause:** Bulk-scrape bez limitu — `pages=500` by spustilo stovky requestů.
**Fix:** Clamp guard + `request_delay=1.0` + `_throttle()`.

#### GT-037 (JOBS-029): Boolean auto-validace při config loadu
**Server:** MCP-Jobs | **Status:** Fixed

**Root cause:** `validate_boolean()` existovala, nikdo ji nevolal při loadu configu.
**Fix:** Volání v `UserConfig._from_raw()`.

#### GT-038 (JOBS-030): MCP error kontrakt
**Server:** MCP-Jobs | **Status:** Fixed

**Root cause:** Každý tool řešil error handling jinak; per-provider errors embedded v datech.
**Fix:** Jednotný formát `[{"error": "..."}]` pro všechny tools.

#### GT-039 (JOBS-031): Config error messages + lint
**Server:** MCP-Jobs | **Status:** Fixed

**Root cause:** `CategoryConfig(**c)` házel raw TypeError na neznámý YAML klíč.
**Fix:** try/except s popisnou zprávou; importy top-level.

#### GT-040 (JOBS-033): L2 Resources — mcp-jobs://ads/{query_id}
**Server:** MCP-Jobs | **Status:** Fixed

**Root cause:** Search results jen v kontextu LLM — neadresovatelné po ukončení callu.
**Fix:** 3 resources `/list`, `/{query_id}`, `/{query_id}/report` + in-memory store.
**Pravidlo:** P21

#### GT-041 (JOBS-034+035): 6-layer encoding stack
**Server:** cross-repo | **Status:** Implemented

Systematické řešení encoding/quoting na Windows — defense in depth:

| # | Vrstva | Mechanismus |
|---|--------|-------------|
| 6 | PS autoload | `_github/_init.ps1` → `$PROFILE` |
| 5 | AI guardrails | `.ai_guardrails.json` shell_rules |
| 4 | Dokumentace | `docs/powershell_encoding.md` |
| 3 | Project helpers | `scripts/init.ps1` wrappery |
| 2 | Batch launcher | `set PYTHONIOENCODING=utf-8` + `PYTHONUTF8=1` |
| 1 | Python runtime | `ensure_utf8_stdout()` |

#### GT-042 (CNC-014 continuation): Session compact — MCP workdir vs source code
**Server:** cross-repo | **Status:** Documented

**Lesson:** Session compact = přepnutí kontextu MCP toolů, ne source code. Všechny bash příkazy musí mít explicitní `workdir` parametr.

#### GT-043 (lichess-001): Editable install — .pth jen src/
**Server:** lichess-analyzer | **Status:** Fixed

**Symptom:** `python -m src.server` → `ModuleNotFoundError: No module named 'src'`; opencode hlásí status „invalid".
**Root cause:** `uv pip install -e .` vytvořilo `.pth` s jedinou řádkou `...\src`; kod importuje `from src.app import app` → potřebuje project root na sys.path (bez něj hledá `src/src/server.py`).
**Fix:** Druhá řádka do `.pth`:
```
C:\Users\PC\Documents\Repozitar_Dev\_github\lichess-analyzer-mcp
C:\Users\PC\Documents\Repozitar_Dev\_github\lichess-analyzer-mcp\src
```
**Pravidlo:** P29 (část .pth)

#### GT-044 (lichess-002): async main() + asyncio.run(app.run()) — event loop konflikt
**Server:** lichess-analyzer | **Status:** Fixed

**Symptom:** Server startne (logy na stderr), pak okamžitě `RuntimeError: Already running asyncio in this thread`.
**Root cause:** FastMCP `app.run()` interně volá `anyio.run(self.run_stdio_async)` — vlastní event loop; obalení do `asyncio.run(main())` vytváří druhou loop.
**Fix:** Sync main (kanonický pattern viz §4 P29).
**Pravidlo:** P29

### 3.5 lichess-analyzer-mcp — LLM Reasoning Pipeline

#### GT-045 (lichess-003): Cerebras API — reasoning místo content
**Server:** lichess-analyzer | **Status:** Fixed

**Symptom:** Cerebras vrací 200 OK, ale `message.content` je None → pipeline padá do fallback/raw JSON dumpu.
**Root cause:** Cerebras používá proprietární `reasoning` field místo standardního `content`.
**Fix:** Fallback chain v parseru (viz P30).
**Pravidlo:** P30

#### GT-046 (lichess-004): LLM_MAX_TOKENS clipping
**Server:** lichess-analyzer | **Status:** Fixed

**Symptom:** DeepSeek V4 Flash report useknutý uprostřed (2895 tok); chybí závěrečné sekce.
**Root cause:** Default 2000 tok nedostatečný pro 6 patternů + weakness report + 5 sekcí (real ~3500 tok).
**Fix:** `LLM_MAX_TOKENS=4000`.
**Pravidlo:** P31

#### GT-047 (lichess-005): Cascade provider silence
**Server:** lichess-analyzer | **Status:** Mitigated

**Symptom:** Uživatel nevidí, které providery cascade zkusila a který vyhrál.
**Root cause:** Cascade log vracen jen ve variantě with_logs; stav providerů není nikde perzistentní.
**Fix:** Log paralelně s reportem; header uvádí provider/model/tokens/cost/latency.
**Pravidlo:** P32

#### GT-048 (lichess-006): Timing dict type change — silent crash
**Server:** lichess-analyzer | **Status:** Fixed

**Symptom:** `TypeError: unsupported format string passed to dict.__format__` po LLM callu; report se nezapíše.
**Root cause:** Timing formát změněn z float na dict; konzument zůstal na starém přístupu.
**Fix:** `.get("total", {}).get("duration", 0)` u všech konzumentů.
**Pravidlo:** P33

#### GT-049 (lichess-007): Cache dump key mismatch
**Server:** lichess-analyzer | **Status:** Fixed

**Symptom:** `compare_providers.py` čte 0 patternů z cached dumpu.
**Root cause:** Klíče dumpu (`patterns_detected`, `games_analyzed`) ≠ hledané (`patterns`, `analyses_data`).
**Fix:** Fallback chain přes `.get()`; cache/export schema dokumentovat a verzovat.
**Pravidlo:** P34

#### GT-050 (lichess-008): Stockfish re-analýza při každém běhu — 24 min pipeline
**Server:** lichess-analyzer | **Status:** Fixed

**Symptom:** 5 her = 24 min; 99.9 % času Stockfish (deterministický krok).
**Fix:** Cache-first: check `data/game_cache/{game_id}...json` (depth-gated) → hit = reuse, miss = analyze+store. Re-run 5 her = 0.1 s.
**Pravidlo:** P35

#### GT-051 (lichess-009): Provider model ID — UI vs API discrepancy
**Server:** lichess-analyzer | **Status:** Mitigated

**Symptom:** Cerebras model ID z docs vrací 404; NVIDIA endpoint SSL hostname mismatch.
**Root cause:** Model ID != display name/docs; NVIDIA endpoint není standardní `/v1` schema.
**Fix:** Discovery vždy přes `/v1/models`; po změně endpointu test minimálním promptem (2026-07-20 vyřešeno).
**Pravidlo:** P36

#### GT-052 (lichess-010): SNR evaluation framework
**Server:** lichess-analyzer | **Status:** Documented

Metodologický problém porovnání LLM providerů objektivně, bez subjektivního biasu:

| Kriterium | Váha |
|---|---|
| Grounding k patternum | 30% |
| Konfidence % citace | 20% |
| Phase ACPL citace | 15% |
| Hallucinace (míň = líp) | 20% |
| Struktura/délka | 10% |
| Tréninková konkrétnost | 5% |

**Aplikace:** DeepSeek V4 Flash 93/100, NVIDIA 57, Cerebras 54.
**Pravidlo:** P38

#### GT-053 (lichess-011): DeepSeek Chat — cost ban policy
**Server:** lichess-analyzer | **Status:** Fixed (policy)

**Decision:** DeepSeek Chat (3.6× dražší než V4 Flash za stejnou/horší kvalitu) vyřazen z default cascade; ponechán pro explicitní volání.
**Pravidlo:** P37

#### GT-054 (lichess-012): Multi-provider API key management
**Server:** lichess-analyzer | **Status:** Documented

Tři klíče s odlišným nakládáním (NVIDIA free/rate-limited, Cerebras free+$5, DeepSeek paid credit).
**Best practice:** `.env` lokálně, `auth.json` v `~/.local/share/opencode/` centrálně, oba v `.gitignore`.
**Pravidlo:** P39

#### GT-055 (lichess-013): Env var silent fallback na default
**Server:** lichess-analyzer | **Status:** Fixed

**Symptom:** `LLM_MAX_TOKENS` tiše fallbackuje na 2000 bez varování o nedostatečnosti.
**Fix:** Startup warning při hodnotách pod doporučeným minimem.
**Pravidlo:** P40

#### GT-056 (lichess-014): Per-game LLM cache — Level 2
**Server:** lichess-analyzer | **Status:** Implemented

**Symptom:** Nová hra → LLM layer znovu na VŠECHNY hry; lineární růst prompt size a cost.
**Řešení:** Dvouúrovňová cache — L1 Stockfish (`{game_id}_{color}_d{depth}.json`) + L2 per-game LLM analýza (`{game_id}_{color}_llm.json`); agregace používá L2 summaries; nová hra = 1 L2 call + 1 agregacní call. Implementace `src/services/game_llm_cache.py`.
**Pravidlo:** P41

#### GT-057 (lichess-015): NVIDIA timeout na agregaci
**Server:** lichess-analyzer | **Status:** Documented

**Root cause:** Prompt s summaries (~2500 znaků) → vyšší timeout pravděpodobnost na free NVIDIA tieru; Cerebras/DeepSeek uspějí.
**Fix:** Cascade resilience — timeout providera přeskočen; pro agregaci se summaries nepoužívat NVIDIA.
**Pravidlo:** P42

#### GT-058 (lichess-016): Pipeline mode — monolit vs inkrementální cache
**Server:** lichess-analyzer | **Status:** Implemented

**Poznatek:** Monolit efektivnější pro N≤30 (méně tokenů, kratší čas); inkrementální cache se amortizuje pro velké N (44% úspora při N>100).
**Řešení:** `run_coaching_pipeline(mode="auto")` — auto-detekce + explicitní override `PIPELINE_MODE` env var.
**Pravidlo:** P43

#### GT-059 (lichess-017): _build_game_prompt wrong key names → low SNR
**Server:** lichess-analyzer | **Status:** Fixed | **Typ:** Application logic — Key mapping bug

Per-game LLM výstupy měly low SNR. Debug odhalil 3 bugy: (1) wrong keys v `_build_game_prompt()` (`move_number/san/cp_loss` místo `ply/move_san/centipawn_loss`) — LLM dostával `move ?, loss ?cp`, (2) `accuracy: 0.0` — auto_annotate nepočítalo accuracy, (3) `phase_stats: {}` — nikdy neplněno.

**Řešení:** Správné klíče; `_compute_accuracy()`/`_compute_phase_stats()` v `auto_annotate()`; repair skript pro 18 stale cache souborů; 13 contract testů.

**Essence (contract testing):** Producer (`GameAnalysis.to_dict()`) i consumer (`_build_game_prompt()`) prošly unit testy izolovaně — nikdo netestoval konzistenci klíčů mezi nimi. Doména: Consumer-Driven Contract Testing (enterprise: Pact; lightweight varianta: schema test na reálných datech + placeholder detection `assert "?" not in prompt`). Detail ontologie: `01_METODIKY/05_testing/contract_testing_ontologie_v1.md`.

**Výsledek:** `"accuracy 0.0%", "move ?, loss ?cp"` → `"přesnost 94,6%", "move 27, Ng3 (blunder), cp_loss 497"`.
**Pravidlo:** P44

#### GT-060 (lichess-018): Iterační optimalizace — JSON validation, CI/CD, unit testy služeb, API key check
**Server:** lichess-analyzer | **Status:** Implemented

Meta-analýza po GT-059 odhalila 4 slabiny → (1) `_validate_json_output()` před cachováním LLM outputu (garbage → cascade zkusí dalšího providera), (2) GitHub Actions CI (ruff + pytest, Python 3.12), (3) unit testy `engine_client.py` s mocknutým Stockfishem (5 testů), (4) `verify_api_keys()` při startupu — ping max_tokens=1, timeout=10s, detekce 401/402/429.
**Stav:** 33/33 testů pass.
**Pravidlo:** P45

#### GT-061 (lichess-019): mistakes list always empty (Cross-LLM Audit N1)
**Server:** lichess-analyzer | **Status:** Fixed | **Typ:** Application logic — Classification branch bug

**Symptom:** `GameAnalysis.mistakes` vždy prázdné; tahy s cp loss 150–299 končí v `blunders`.
**Root cause:** `game_analyzer.py:161-162` — `if classification in ("blunder", "mistake")` se sdíleným append targetem; chybí separátní elif větev.
**Fix:** Rozdělení na `if blunder` / `elif mistake`.
**Dopad:** 100 % tahů 150–299 cp chybně klasifikováno (coaching report, diagnostician, pattern detection); latentní od v1.0. Detection gap: contract testy kontrolují klíče, ne větvění kategorií.
**Pravidlo:** P46
**Provenance:** Overeno source-read (game_analyzer.py:161-162, v2 audit code path verification 2026-07-24). Popis presne odpovida kodu. Zadna konfabulace.

#### GT-062 (lichess-020): Cross-LLM audit workflow validation (Methodology)
**Server:** lichess-analyzer | **Status:** Documented | **Typ:** Methodology — Development process

Dvoufázový audit 2026-07-24: v1 twin scan (de novo, bez kodu) → 8 nálezů (4 structural, 4 pattern-based); v2 code review → 7 nálezů (5 implementation, 2 security confirmed).
**Výsledky:** 12 unikátních nálezů; v1→v2 confirm rate 71 %; v2-only nálezy 2 (mistakes bug N1, Pattern G semantic N4); efektivita 9.6 nálezů/hod (15/1.55h); twin time-to-audit ~13h (subjektivní odhad autora) → 5 min audit script.
**Závěr:** Twin scan zachytí architekturní/strukturní problémy, unikají mu implementační detaily (chybějící elif, semantic mismatch). Code review nutný pro nízkourovnové verifikace. Ani jedna fáze nestáčí sama.
**Pravidlo:** P47
**Provenance:** Agregace z audit session — casove udaje (1.55h) mereny, "~13h" subjektivni odhad autora. Metodologie v1+v2 overena externim auditorem (Claude, 2026-07-24).

#### GT-063 (lichess-021): Pattern detection — hardcoded confidence + semantic mismatch
**Server:** lichess-analyzer | **Status:** Documented | **Typ:** Application logic — Pattern confidence & semantics

**Symptom:** (1) Confidence hardcoded (0.6/0.5/0.8/0.7/0.7) nezávisle na N a síle evidence; (2) Pattern G `frequency` = zaokrouhlená blunder rate místo počtu postžených her → semantický mismatch filtru `frequency >= min_occurrences` (pattern projde/neprojde z jiného důvodu než zamýšleno).
**Řešení:** Confidence = f(N, evidence_strength); minimální N=5 pro confidence >0.5; Pattern G frequency = len(game_ids).
**Pravidlo:** P48
**Provenance:** Tento zaznam obsahoval v puvodni v3 konfabulaci — Pattern G byl popsan jako "closed center positional match" (tahy d4 d5, e6, c6), coz neodpovida skutecnemu kodu. Opraveno ve v4 na zaklade externiho cross-auditu (Claude, 2026-07-24). Reference: `04_KNOWLEDGE_BASE/01_MCP/MCP_GT_ANALYZA_kvalita_originalita_semantika.md`, nalezy B1.

#### GT-064 (lichess-022): Diagnostician — absolutní count vs per-move rate
**Server:** lichess-analyzer | **Status:** Documented | **Typ:** Application logic — Normalization

**Symptom:** `diagnostician.py:52` používá absolutní počet blunderů v middlegame → bias vůči dlouhým hram.
**Řešení:** Normalizace `blunder_rate = blunder_count / moves_in_phase`; threshold na rate.
**Provenance:** Nalez N3 z cross-LLM audit v1 (twin scan). Overitelne v diagnostician.py:52. Popis precizni — zadna konfabulace.

#### GT-065 (lichess-023): Path traversal via unsanitized game_id/username (Security)
**Server:** lichess-analyzer | **Status:** Mitigated | **Typ:** Security — Path traversal

**Symptom:** `game_id`/`username` přímo v cestách bez sanitizace (`game_analyzer.py:14-15`, `lichess_client.py:47-48,74-77`) — `game_id="../../sensitive"` může zapisovat/číst mimo cache adresář.
**Řešení:** `re.sub(r'[^a-zA-Z0-9_-]', '_', value)` na všech user-supplied identifikátorech před konstrukcí cesty.
**Pravidlo:** P49
**Provenance:** Nalez F2 — jadro (sanitizace chybi) spravne, ale puvodni v3 obsahovala fabrikovane code snippety (LOGS_DIR neexistuje). Opraveno ve v4 na skutecna API. Overeno source-read.

#### GT-066 (lichess-024): Pipeline consistency — max_games hidden clamp
**Server:** lichess-analyzer | **Status:** Fixed | **Typ:** Application logic — Hidden limit

**Symptom:** `fetch_games(max_games=999)` tiše vrátí max 50 her; stejný clamp v `match_patterns` a `diagnose_player` — žádný warning, cache/index nekonzistence (načteno 50, index hlásí 63).
**Fix:** Clamp na 999 + odstranění tichých clampů + `get_pending_analysis()` kontrola rozdílu index vs cache.
**Pravidlo:** P50
**Provenance:** Overeno source-read fetch_games.py, match_patterns.py, diagnose_player.py (2026-07-26).

#### GT-067 (lichess-025): Pending analysis — missing warning mechanism
**Server:** lichess-analyzer | **Status:** Fixed | **Typ:** Application logic — Cache consistency gap

**Symptom:** Tool volaný na N hrách z toho M neanalyzováno → nekompletní výsledky bez upozornění (falešný pocit kompletnosti).
**Fix:** `get_pending_analysis()` (index vs cache diff) + warning + batch tool `analyze_pending`.
**Pravidlo:** P51
**Provenance:** Overeno source-read (2026-07-26).

#### GT-068 (lichess-026): Berserk 0.14 — no before pagination parameter
**Server:** lichess-analyzer | **Status:** Documented | **Typ:** Environment — Library limitation

**Symptom:** `export_by_player(..., before=...)` → TypeError. Berserk 0.14 parametr neexponuje (přidán 0.15+); Lichess API ho podporuje, knihovna ne.
**Dopad:** Historie mimo recent okno (~30–60 her) nedostupná; pro coaching nekritické.
**Fix:** Reverze kódu; upgrade až bude berserk 0.15+ dostupný.
**Pravidlo:** P52
**Provenance:** Overeno runtime error (2026-07-26), verifikováno pip show berserk = 0.14.0.

#### GT-069 (lichess-027): opencode MCP tool cache — tool registered but invisible
**Server:** lichess-analyzer | **Status:** Workaround | **Typ:** Infrastructure — opencode host caching

**Symptom:** Nový tool registrován v Python/FastMCP, ale neviditelný v opencode client tool listu.
**Root cause:** Host drží tool-list snapshot z prvního initialize handshaku; nerevaliduje při reconnectu/session refresh. Tool existuje v procesu (`app._tool_manager.list_tools()`), volatelný přímo, ale ne přes UI.
**Workaround:** (1) Restart celého opencode (ne jen MCP server), (2) nebo přímé Python volání.
**Pravidlo:** P53
**Provenance:** Overeno prakticky — list_tools neobsahuje analyze_pending (2026-07-26).

#### GT-070 (lichess-028): Pattern G (Color as modulator) — new pattern detection
**Server:** lichess-analyzer | **Status:** Documented | **Typ:** Application logic — New pattern

**Nález:** Na 63 hrách (44W/17L/2D) detekován vzácný pattern: 1.47× více blunderů jako White; confidence 49 % (N=63, base 0.4 × evidence 1.22). Dříve skryt nízkým N a hardcoded confidence (před GT-063 fixem). Signalizuje specifický psychologický/opening-preference problém → separátní tréninkový přístup.
**Pravidlo:** P54
**Provenance:** Detekován match_patterns(max_games=63) na datech 2026-07-26. Overeno vizualni kontrolou blunder distribuce.

### 3.6 lichess-analyzer-mcp — DBCL Phase 2 & RUN_004 (2026-07-27)

#### GT-071 (lichess-029): engine_lines silent fail — AssertionError v board.san() pro PV illegal moves
**Server:** lichess-analyzer | **Status:** Fixed | **Typ:** Application logic — Silent data corruption

**Symptom:** 30/101 BFS (30 %) má 0 engine_lines; postihuje i ground truth hry. `analyze_position(multipv=3)` vrací `[]`.
**Root cause (dvojitý silent fail):** (1) `engine_client.py:86` — `board.san(m)` validuje všechny PV tahy proti ROOT pozici, ale PV jsou sekvenční: po prvním tahu se board mění → třetí tah `g5e6` kontrolováno proti rootu kde g5 je prázdné → AssertionError; (2) `game_analyzer.py:329-333` — `try/except Exception: pass` error kompletně skryje; (3) AssertionError propaguje přes engine lock a korumpuje stav pro následující volání.

```
PV:   f3g5(Nf3-g5), g6e5(Nxg6xe5), g5e6(Ng5xe6)
Root: f3->g5 OK    g6->e5 OK     g5->e6 FAILS (g5 empty!)
Fix:  board.copy() -> push postupne -> OK
```

**Fix (trojí):** Sekvenční konverze na `board.copy()` + try/except; silent pass → `_logger.warning()`; `engine.analysis(board, Limit(depth=depth))`.
**Verifikace:** 5/5 dříve padajících FENů vrací 3/3 PV lines.
**Pravidla:** P55 + P56
**Provenance:** Overeno source-read + runtime debug script. AssertionError reprodukován izolovaně na FEN r1b4k/1p4pp/np1Nr1n1/4P3/8/5N1P/P1P1B3/1R2K2R w K - 1 25 (2026-07-27).

#### GT-072 (lichess-030): K0 variance — depth=12 vs depth=14 cp_loss rozdíl ~22 %
**Server:** lichess-analyzer | **Status:** Documented | **Typ:** Methodology — Measurement noise

**Symptom:** kNAMNYUF ply 63: 607 cp (d12) vs 773 cp (d14) = 171cp rozdíl. ACPL z různých depth runů nejsou srovnatelné (RUN_003 vs RUN_004).
**Root cause:** Depth impactuje eval precision (~3× rychlejší d12 = méně přesný); K0 variance nekvantifikována ani reportována.
**Fix (navrh):** Každý run reportuje K0 metriky (depth, engine_version, Threads, Hash, nps); INC ground truth re-fetch na jednotné depth; logovat depth mismatch při cache load.
**Pravidlo:** P57
**Provenance:** RUN_004 data. Potvrzeno CPM dokumentem §3 (K0 channel).

#### GT-073 (lichess-031): engine.analysis() bez depth limit — depth drift
**Server:** lichess-analyzer | **Status:** Fixed | **Typ:** Application logic — Missing parameter

**Symptom:** Volání bez `Limit(depth=depth)` — Stockfish sahá do libovolné hloubky na nestabilních pozicích (timeout risk, plýtvání compute).
**Fix:** `engine.analysis(board, chess.engine.Limit(depth=depth))`.
**Provenance:** Source-read engine_client.py:81 (2026-07-27). Fix souběžně s GT-071.

#### GT-074 (lichess-032): Cache invalidation — stale BFS after code fix
**Server:** lichess-analyzer | **Status:** Workaround | **Typ:** Infrastructure — Cache governance

**Symptom:** Po opravě kódu vrací `use_cache=True` stale BFS s 0 engine_lines; uživatel musí cache ručně mazat.
**Root cause:** Cache JSON nemá `detector_version`/`code_version` klíč → nelze detekovat starší generaci kódu.
**Workaround:** Manuální clear před re-runem po code change.
**Fix (navrh):** Při cache load porovnat detector_version; mismatch → re-analyze.
**Pravidlo:** P58
**Provenance:** Prakticke overeni po fixu GT-071 (2026-07-27).

#### GT-075 (lichess-033): Stockfish PV multi-move SAN conversion — domain knowledge gap
**Server:** lichess-analyzer | **Status:** Fixed | **Typ:** Domain knowledge — Assumption error

**Blind spot:** Předpoklad, že PV linie obsahují jen single-move evaluations. Realita: PV v multi-PV módu jsou sekvenční variace, ne paralelní alternativy — každý tah aplikovat na kopii boardu postupně.
**Pravidlo:** P59
**Provenance:** Runtime debug (2026-07-27).

#### GT-076 (lichess-034): Engine lock error propagation
**Server:** lichess-analyzer | **Status:** Mitigated | **Typ:** Architecture — Lock coupling

**Symptom:** AssertionError uvnitř lock bloku korumpuje engine stav → selhávají všechny následující analýzy v runu.
**Root cause:** `_acquire_analysis_lock`/`_release` coupling mezi nezávislými calls; `finally` release provede i po AssertionError, ale engine může zůstat nekonzistentní.
**Mitigace:** GT-071 fix eliminuje AssertionError v normálním provozu; zombie recovery = engine restart při timeout locku (120s).
**Pravidlo:** P60
**Provenance:** Analyzováno pri debugu GT-071 (2026-07-27).

#### GT-077 (lichess-035): Chybí per-game log truncated BFS
**Server:** lichess-analyzer | **Status:** Pending | **Typ:** Application logic — Missing logging

**Symptom:** BFS s méně než multipv_target engine_lines projdou bez upozornění — nelze identifikovat částečné výpadky.
**Fix (navrh):** `truncated` flag v BlunderFactSheet (`len(engine_lines) < multipv_target`) + warning per BFS.
**Pravidlo:** P61
**Provenance:** RUN_004 data (71/101 s 3 lines, 30/101 s 0 před fixem GT-071); trackování částečných výpadků nadále chybí (2026-07-27).

#### GT-078 (lichess-036): ruff --fix smazal side-effect tool imports — F401 destruktivní autofix
**Server:** lichess-analyzer | **Status:** Fixed | **Typ:** Tooling — Destructive autofix

**Symptom:** `ruff check --fix` smazal 18 `from ...tools import X` importů z `server.py` (diff -18/+2) → registrace toolů přes `@app.tool()` zrušena; server by startoval bez toolů. Pytest 93/93 PROŠEL (testy server.py neimportují); detekce až díky `git diff --stat`.
**Root cause:** Registrační pattern side-effect imports vs F401 unused-import autofix. Baseline: 46 errorů (18× F401) na 3 souborech.
**Fix:** Importy obnoveny s `# noqa: F401` per line; verifikace registračním smoke checkem (`app._tool_manager._tools` = 18) + pytest; nový tool s noqa od počátku.
**Pravidlo:** P62
**Provenance:** source-read — git diff po ruff --fix (diff -18/+2), smoke check 18 toolu, commit c92940f (2026-08-01).

#### GT-079 (lichess-037): Data-correctness batch 1+2 — 6 merged bugů LLM input pipeline
**Server:** lichess-analyzer | **Status:** Fixed | **Typ:** Data integrity — LLM input correctness

**Bug list (fix batche 2026-08-02):**
1. **B100 getattr garbage:** `opening_report` četl neexistující atributy (`opening_name`, `player_color`, `acpl`, `result`) přes getattr s defaultem → 100 % garbage do promptu bez detekce.
2. **B98 hardcoded perspektiva:** `opponent_pool` hardcodoval barvy → u her autora černým analyzoval vlastní tahy jako oponentovy; n1_count vždy 0; ACPL placeholder „?".
3. **B121/B119 KB cesta:** `KB_ROOT = 3× ".."` ukazoval do repa (adresář by vznikl uvnitř repa); filenames bez timestampu → same-day overwrite.
4. **B31 cache kolize barev:** klíč `{game_id}_llm.json` bez barvy → dual-cache sdílí soubor → last-writer-wins přepíše opačnou perspektivu.
5. **B5 timeout kill reference:** timeout kvitil sdružený `_engine`, ale `evaluate_move` používá lokální engine → kolaterální zabití konkurující analýzy.
6. **B16 tichá degradace:** `except: pass` + `cp_loss = 0` → chybný tah klasifikován „best" → ACPL systematicky optimistický bez markeru. (+B113: `chess.Board(fen="")` ValueError na legacy cache.)

**Root cause (společný):** LLM prompt čten přes neexistující atributy/getattr defaulty bez signalizace — data bez markeru kvality = falešná autorita.
**Fix:** Reálná pole modelu + color-aware win_rate; `_resolve_colors()` z PGN headerů; KB_ROOT 4× ".." + import-time check + timestamp; klíč `{game_id}_{color}_llm.json`; `_run_engine_call(fn, timeout_s, engine=None)` cílí volající referenci; `evaluation_errors` čítač + prompt marker „Eval errors: N"; guard `and m.fen`.
**Pravidla:** P63–P68; P41 aktualizováno (color v klíči).
**Provenance:** source-read — CODE_REVIEW_2026-08-01.md, session plany 00_STRATEGIE/session_plan_fix_batch1/2_2026-08-02.md, commity fc5fc69 + 552bc9d, testy 93→109→121 (2026-08-02).

#### GT-080 (workspace-wide): Ne-ASCII názvy souborů — mojibake v git objektech (ASCII-NOM)
**Server:** workspace (cross-repo) | **Status:** Fixed | **Typ:** Encoding — filename nomenklatura

**Symptom:** GitHub GUI zobrazoval `02_ANALÝZY` jako mojibake; diagnostika: žádná strukturální inkonzistence (stejný SHA, 61=61 souborů), ale mojibake bytes v git objektech (cp1250 filesystem bytes místo UTF-8). Celkem 20 trackovaných ne-ASCII názvů v 6 repech (diakritika, mezery, U+2011 non-breaking hyphen).
**Root cause:** Encoding dluh — git ukládá path jako raw bytes; U+2011 vizuálně identický s `-` ale jiný codepoint → rozbíjí copy-paste/grep/RAG lookup. Každá ne-ASCII cesta = budoucí bug (cyklický encoding dluh).
**Fix:** (1) Konvence ASCII-NOM `[A-Za-z0-9._-]` (obsah zůstává UTF-8); (2) transliterace `Normalize(FormD)` + drop NonSpacingMark, mezera→`_`, U+2011→`-`; (3) rename přes filesystem objekty + `git mv` (obsah nedotčen); (4) `.gitignore` fix po renames; (5) content reference update (7 souborů); (6) guard `.scripts/ascii_filenames_check.ps1` (exit 0/1, 19/19 repo OK); (7) kontraktní validátor `.scripts/context_refs_check.py` — 1386 trackovaných souborů/19 rep, odhalil a opravil 31 broken referencí (GLOBAL_FORBIDDEN + REPO_FORBIDDEN mapa + F1_ALLOWLIST).
**Pravidlo:** P69
**Provenance:** source-read — renames commity KB 533a9c6, dxf 0bff7b7, GCP fdcf1df, kazuistiky a613eb2, lichess 19c735b, vcf 79591d5; broken ref fixes: GCP d9ea2b1, lichess 9e41386, linkedin 210be0b, mcp-local 9ab5820, dxf de87a32, Vcf-compiler 0a8844d, outpost2026_profile cce09b3; validator exit 0 (2026-08-02).

#### GT-081 (lichess-038): Architektonický původ ruffu — CI gate, ne pre-commit hook
**Server:** lichess-analyzer | **Status:** Documented | **Typ:** Tooling — Guardrail adoption architektura

**Zjištění (git source-read):** (1) Ruff config od prvního commitu `4dd503a` (2026-07-18) — defaultní sada F+E4/E7/E9; (2) enforcement 2026-07-20 `1ca173e` — CI krok `ruff check` = CI gate, ne pre-commit hook; (3) eskalace pravidel `98f0546` — select F/E/W/I/N/UP/S (chyby→styl→pojmenování→bezpečnost); (4) rozšíření CI `e41ef52` — mypy + pytest --cov; (5) `.pre-commit-config.yaml` NIKDY neexistoval.
**Závěr:** Ruff = struktura vrstva (quality gate) od kostry projektu. CI gate (`--check`, read-only) ≠ pre-commit hook (lokální mutace); `--fix` patří do rukou člověka s git diff review, ne do automatizace — separace kontroly a mutace (poruchový vzor GT-078). Kontrast: linkedin-mcp-custom používá pre-commit hook — dvě instance téhož principu, různé enforcement pointy.
**Pravidlo:** P62 (kontext rozšířen)
**Provenance:** source-read — git log -S ruff + git show na commitech 4dd503a, 1ca173e, 98f0546, e41ef52; prázdná historie .pre-commit-config.yaml (2026-08-02).

#### GT-083 (mcp-jobs-010): 3-fázová pipeline — collect → parallel fetch → filter
**Server:** MCP-Jobs | **Status:** Documented | **Typ:** Architecture — Pipeline design pattern

**Symptom:** Detail fetch sekvenčně uvnitř filter fáze → ~30 s jen na fetch při 46 matched ads; bottleneck eskaluje lineárně s počtem ads.
**Fix (pipeline.py:77-128):** (1) Collect unikátních URL přes všechny query (set dedup), (2) parallel fetch `ThreadPoolExecutor(max_workers=4)` + per-portal throttle 0.5s, neúspěch = `_FAILED` sentinel (GT-085), (3) filter nad naplněnou cache.
**Výsledek:** 58.5→36.3 s (1.61×), identické výsledky.
**Pravidlo:** P70
**Provenance:** source-read — pipeline.py:77-128, _fetch_details_parallel; fresh run metriky (2026-08-06).

#### GT-085 (mcp-jobs-012): Cache failure sentinel (_FAILED pattern)
**Server:** MCP-Jobs | **Status:** Documented | **Typ:** Reliability — Cache state management

**Symptom:** Selhaný detail fetch zapsán jako None — stejná hodnota jako „nezkoušeno" → opětovné fetch pokusy pro permanentně selhané URL.
**Fix (pipeline.py:19,114,181,196,200):** Sentinel `_FAILED = object()`; zápis `detail if detail else _FAILED`; čtení `if cached is not _FAILED and cached`.
**Pravidlo:** P71
**Provenance:** source-read — pipeline.py; cross-LLM review finding BUG-001 (Claude Sonnet 5, 2026-08-06).

#### GT-086 (mcp-jobs-013): Ruff default rule set drift — nepřítomnost lint configu
**Server:** MCP-Jobs | **Status:** Fixed | **Typ:** Tooling — Dependency/lint determinismus

**Symptom:** CI failoval `ruff check` s 70 chybami bez jakékoli změny kódu.
**Root cause (řetězec):** `ruff>=0.6` bez horní hranice → CI nainstaloval 0.16.3; projekt neměl žádný `[tool.ruff]` config → aktivní default pravidla driftující s verzí (nová UP045/BLE001/DTZ005/RUF012/PIE810/FURB136).
**Fix:** Explicitní `[tool.ruff.lint]` select (stabilní E4/E7/E9/F + moderní UP/RUF/PIE/FURB/DTZ) + ignore BLE001 zdokumentovaný; E501 záměrně mimo (design trade-off); kódové fixy (RUF012 ClassVar, DTZ datetime.now(UTC), PIE810 tuple, RUF003 en-dash).
**Pravidlo:** P72
**Provenance:** source-read — pyproject.toml, ci.yml ruff step, ruff 0.16.3 reprodukce, --fix diff review (2026-08-18).

#### GT-087 (mcp-jobs-014): MCP timeout -32001 — sync pipeline + client timeout sémantika; fix async submit+poll
**Server:** MCP-Jobs | **Status:** Fixed | **Typ:** Architecture — Async job pattern

**Symptom:** `search_from_config` přes MCP → -32001; CLI běh fungoval (34.5 s). Server „neodpovídá".
**Root cause (2 fakta):** (1) Sync pipeline v toolu = 34–45s reálné latence > client-side JSON-RPC/stdio timeout; (2) opencode `timeout: 180000` platí JEN pro ListTools, NE pro tool calls — prokázáno probe přes správný stdio_client (33.9 s OK).
**Fix (server.py):** Async submit+poll — `ThreadPoolExecutor(max_workers=2)` + `_JOB_STORE`; search tooly vrátí okamžitě `{job_id, status}` (~0.02 s); nový tool `search_status(job_id)` → `{status, elapsed_s, result}`; fast-path validace zůstává sync.
**Verifikace:** E2E — submit 0.02 s, poll done po 42.2 s; 6 registrovaných toolů.
**Pravidlo:** P13 (rozšířeno — 4. varianta fixu, jediná bez CLI)
**Provenance:** source-read — server.py job runner; E2E probe mcp stdio_client; opencode.jsonc config (2026-08-18).

#### GT-088 (mcp-jobs-015): Test fixture TRUNCATE proti sdílené dev DB
**Server:** MCP-Jobs | **Status:** Documented | **Typ:** Testing — Test isolation & destructive operations

**Symptom:** Po `pytest tests/test_db.py` s nastavenou DATABASE_URL zmizela data z PostgreSQL (ads 70→3, pipeline_runs 5→2) — historické ETL runs nevratně.
**Root cause:** Fixture `conn()` dělá `TRUNCATE ... RESTART IDENTITY CASCADE`; skip guard kontroluje jen existenci env var; testy se připojují na stejnou DB jako dev/produkce. Produkční layer je INSERT-only → destrukce výhradně z test kódu.
**Fix (doporučený, neaplikován):** Separátní test DB nebo transakce s rollbackem; TRUNCATE jen na data vytvořená testem samým.
**Pravidlo:** P73
**Provenance:** source-read — tests/test_db.py:27-39, db.py:upsert_ads; psql SELECT stav po smazání; output/*.json neporušené (2026-08-18).

#### GT-089 (mcp-jobs-016): MCP timeout -32001 — stderr pipe full přes logging.lastResort
**Server:** MCP-Jobs | **Status:** Fixed | **Typ:** Transport — stderr hygiene (P25, komplement GT-010)

**Symptom:** I po submit+poll (GT-087) timeouť i rychlé tooly (`search_status`, `health_check`) při plném runu; ad-hoc searchy a CLI fungovaly.
**Root cause (nový mechanismus, ne duplicita GT-010/GT-087):** Žádný logging config → root logger aktivoval `logging.lastResort` (implicitní StreamHandler stderr); full run generuje stovky warningů → naplní sdílenou STDIO pipe (4–64 KB) → event loop freeze → i poll tooly timeoutují. Submit+poll NECHÁNÍ před tímto deadlockem.
**Fix (cli.py):** `logging.basicConfig(filename=data/mcp-jobs.log, level=INFO, encoding="utf-8", force=True)` — FileHandler only; startup stderr printy max 1 řádek.
**Verifikace:** E2E — před fixem poll -32001; po fixu oba config runs done 61 s bez timeoutu; 155 testů PASS.
**Pravidlo:** P25 (rozšířeno o implicitní cesty)
**Provenance:** source-read — cli.py/server.py (žádný logging config), pipeline.py warning volume; E2E logy 2026-08-19 (poll -32001 před, done 61s po fixu).

#### GT-090 (mcp-jobs-017): URL tracking parametry rozbíjejí UNIQUE(url) dedup
**Server:** MCP-Jobs | **Status:** Fixed | **Typ:** Data correctness — dedup logika (DB)

**Symptom:** Live DB 167 řádků, ale jen 135 unikátních inzerátů — 52 duplicit / 20 skupin; UNIQUE constraint duplicity nechytil.
**Root cause:** jobs.cz `?searchId=<UUID>`, prace.cz `?rps=<int>` — session parametry mění raw URL každý běh → `ON CONFLICT (url)` insertuje znovu. Profesia měla vlastní `_clean_detail_url()`, jobs/prace.cz žádný → nekonzistentní ochrana napříč providery.
**Fix:** Centrální `normalize_url()` (strip searchId/search_id/rps/utm_*; preserve page/sort) v `Ad.__post_init__` — kanonický URL u zdroje dat. DB vyčištěna 167→135.
**Pravidlo:** P74
**Provenance:** source-read — utils.py, models.py, providers/*; live DB audit (2026-08-20).

#### GT-091 (mcp-jobs-018): Cross-portal fuzzy dedup — bohatší data vyhrávají, tie-break first-seen
**Server:** MCP-Jobs | **Status:** Implemented | **Typ:** Data correctness — dedup logika (DB)

**Symptom:** 9 cross-portal skupin stejného inzerátu (LMC network jobs.cz+prace.cz; ManpowerGroup jenprace+profesia); pipeline dedup selhával na variantách `Praha-Uhříněves` vs `Praha – Uhříněves` (en-dash U+2013 vs hyphen) a nepersistoval do DB.
**Root cause:** Fuzzy klíč nenormalizovaný; dedup jen in-memory; pipeline a DB používaly RŮZNÉ klíče.
**Fix:** Sdílený `fuzzy_key()` (lowercase → NFKD strip diakritiky → dash→hyphen → whitespace kolaps) v pipeline I `upsert_ads`; DB fuzzy sloupce + index; batched lookup `unnest(%s::text[])` (1 round-trip); priorita bohatost dat (description 8 > salary 4 > company 2 > location 1), tie-break first-seen. Live DB 135→125, 0 duplicit.
**Pravidlo:** P75
**Provenance:** source-read — utils.py, pipeline.py, db.py, schema.sql; live DB audit (2026-08-20).

#### GT-092 (mcp-jobs-019): Seznam.cz bot-detekce — UA Chrome/120 + Accept
**Server:** MCP-Jobs | **Status:** Fixed | **Typ:** Provider integrace — anti-bot

**Symptom:** Volnamista scraper 0 ads — deterministická consent/bot-detekce stránka (5/5 live runů, ne intermittent).
**Root cause:** Default HttpClient posílá UA Chrome/120 + Accept hlavičku — tato kombinace spouští headrovou fingerprint detekci Seznamu (ne rate-limit, ne captcha).
**Fix:** Provider vlastní `_SEZNAM_HEADERS` = UA Chrome/126 BEZ Accept, aplikované v `__init__` (přepíše injektovaný HttpClient; mockeri respektováni). Listing i detail. Verifikace 5/5 → 0/5.
**Pravidlo:** P76
**Provenance:** source-read — providers/volnamista.py:31-56, http.py; live verifikace (2026-08-19).

#### GT-093 (mcp-jobs-020): MCP test-ordering pollution — sdílený globální store
**Server:** MCP-Jobs | **Status:** Documented | **Typ:** Testování — order-dependent flake

**Symptom:** Test projde izolovaně, failuje v plné sadě (187 testů) — `_query_store` obsahuje 2 záznamy místo 1.
**Root cause:** Modulový globální dict sdílený testy bez per-test resetu; collection order určuje výsledek.
**Fix (mitigace):** Reset v fixture (teardown); plná izolace globálního stavu odložena (pre-existing).
**Pravidlo:** Rozšíření P73 — izolace se týká i in-process globálního stavu
**Provenance:** source-read — tests/test_server.py:241-246, server.py _query_store; reproducibly order-dependent (2026-08-26 session).

#### GT-094 (mcp-jobs-021): Falešný ERROR „container selector returned 0 cards" na end-of-list stránkách
**Server:** MCP-Jobs | **Status:** Fixed | **Typ:** Scraping — false-positive detekce layout change

**Symptom:** ERROR profesia „likely broken (page layout change)" — dev hlásil podezření na layout change.
**Root cause:** Config pages:10, ale profesia Praha má 8 stránek (157 ads); stránky 9-10 existují (200 OK, normální title, paginace) ale mají legitimně 0 karet — za koncem seznamu. Selektor funkční (live ověřeno).
**Fix:** `parse_listings(page: int = 1)` parametr (base.py signatura + všech 6 providerů); page 1 + 0 karet = ERROR (reálný layout change/blok), page > 1 + 0 karet = INFO „end of listing reached". `scrape_all` předává page; `new == 0` break zůstává vrstvou 2. Live: scrape_all(max_pages=10) → 157 ads, 0 failed.
**Pravidlo:** P77
**Provenance:** source-read — providers/profesia.py:85-156, base.py:136-138; live verifikace 10 stránek (2026-08-26 session); testy +2, 189 PASS.

#### GT-095 (mcp-jobs-022): Unicode en-dash v salary regex — ticha data korekce
**Server:** MCP-Jobs | **Status:** Fixed | **Typ:** Data correctness — regex Unicode mismatch

**Symptom:** Dashboard salary pracecz hodnoty 45/43/42 tis. Kč místo reálných 47915/46625/44500 — systematicky podhodnocené, žádná chyba, data vypadala platná.
**Root cause:** Salary formát `65 000 – 80 000 Kc` s en-dash U+2013; regex/SUBSTRING matchoval jen ASCII hyphen → extrakce jen lower bound; en-dash v 35/61 unikátních formátů. En-dash a hyphen-minus vizuálně identické — vizuální kontrola kodu ani outputu neodhalí.
**Fix:** `REGEXP_SPLIT_TO_ARRAY(salary, '[-\u2013]')` + `REGEXP_REPLACE(parts[N], '[^0-9]', '', 'g')`; CTE lower/upper/avg. Live: pracecz avg 42 → 47915 Kč.
**Pravidlo:** P80
**Provenance:** source-read — dashboard.py:584-600; DB audit 61 formátů; live overeni (2026-08-26 session).

#### GT-096 (mcp-jobs-023): Cross-portal overlap metrika — URL-based dedup misleading
**Server:** MCP-Jobs | **Status:** Fixed | **Typ:** Analytics correctness — misleading metric

**Symptom:** Dashboard „Cross-Query Overlap" hlásil vždy 0 — intuitivně nesmysl (stejné firmy inzerují na více portálech).
**Root cause:** `GROUP BY url`, ale url má UNIQUE constraint — každý inzerát má unikátní URL i když je to stejný job jinde. Cross-portal stejné inzeráty mají vždy různá URL.
**Fix:** `GROUP BY title, company HAVING COUNT(DISTINCT portal) > 1`; metrika přejmenována na Cross-Portal Overlap. Audit: 4 reálné duplicity.
**Pravidlo:** P81
**Provenance:** source-read — dashboard.py:545-576; DB audit; live dashboard overeni (2026-08-26 session).

#### GT-097 (mcp-jobs-024): Circular import po modular refactoru
**Server:** MCP-Jobs | **Status:** Fixed | **Typ:** Architecture — circular import

**Symptom:** `ImportError: cannot import name 'render_ads_tab' from 'dashboard.tabs.ads'` při startu streamlit dashboardu.
**Root cause:** `tabs/ads.py` importoval `run_query` z app.py, app.py importuje tabs → cyklus; Python nedokončí inicializaci modulu.
**Fix:** Zavislost jako parametr — `render_ads_tab(conn, run_query, where_sql, where_params)`; moduly se nikdy navzájem neimportují.
**Pravidlo:** P82
**Provenance:** source-read — dashboard/tabs/ads.py:14-18, dashboard/app.py:112-113 (2026-08-26 session).

#### GT-098 (mcp-jobs-025): Contract testy chyběly při refactoru — artifact měl v backlogu
**Server:** MCP-Jobs | **Status:** Implemented | **Typ:** Process — missing test layer

**Symptom:** Po 5 krocích refactoru (filters, metrics, package split, bulk status) chybělo testování integrity modulů; contract testy byly v artifactu v sekci „Later/backlog" — bez explicitního dotazu by zůstaly neimplementovány.
**Fix:** `tests/test_dashboard_contract.py` — 9 testů: purity (metrics/styling nesmí importovat streamlit), interface (signatury), layers (směry importů).
**Pravidlo:** P83
**Provenance:** source-read — tests/test_dashboard_contract.py:1-141; contract_testing_ontologie_v1.md; artifact Section 6 (chybna priorita) (2026-08-26 session).

#### GT-099 (mcp-jobs-026): Streamlit React #185 — layout shift kolem st.dataframe(on_select) + reintrodukce fixu
**Server:** MCP-Jobs | **Status:** Fixed | **Typ:** Frontend — UI render loop + process regression

**Symptom:** Klik na řádek tabulky → `Minified React error #185` (Maximum update depth exceeded), prohlížeč kolabuje; pytest 237/237 PASS — chyba jen v runtime.
**Root cause:** Známá třída bugů streamlit#7949/#9490: `st.dataframe(use_container_width=True, on_select="rerun")` uvnitř st.tabs + podmíněné bloky renderované POD tabulkou → layout shift → resize loop gridu. Aggravátor: pandas 3.0.5 ve venv mimo vlastní pin <3.0 (lokálně padá, v Dockeru ne). Procesová vrstva: commit `8ff1c6e` odstranil on_select (fungovalo), commit `1602982` ho vrátil s jiným guardem BEZ reprodukce originálního scénáře → reintrodukce.
**Fix:** Detail panel NAD tabulku + selection persistence (`session_state.ads_selected_ids`) + jediný `st.rerun()` při změně výběru; pandas downgrade do specifikace. Sidebar varianta zamítnuta UX.
**Pravidlo:** P90
**Provenance:** source-read — git show 8ff1c6e, 1602982; dashboard/tabs/ads.py; upstream issues; venv vs pyproject. Manuální smoke test autor 2026-08-26.

#### GT-100 (mcp-jobs-027): print-before-raise — st.secrets warning nelze chytit try/except
**Server:** MCP-Jobs | **Status:** Fixed | **Typ:** API side effect — output before exception

**Symptom:** `No secrets found...` 2× při startu dashboardu, přestože kód má try/except kolem st.secrets.
**Root cause:** Pouhý dotek `st.secrets` (i přes getattr `_file_path`) spustí parse, který NEJDŘÍV tiskne warning (streamlit/runtime/secrets.py:111) a AŽ POTOM vyhodí výjimku — try/except zachytí výjimku, proběhlý tisk nikdy.
**Fix:** Existence-check secrets.toml PŘED dotykem API (`Path.home()/".streamlit"/secrets.toml`, cwd varianta); st.secrets čten jen při fyzické existenci (`src/mcp_jobs/db.py:get_database_url`).
**Pravidlo:** P91
**Provenance:** source-read — site-packages streamlit/runtime/secrets.py:111, src/mcp_jobs/db.py:92-108; git show 8ff1c6e.

#### GT-101 (mcp-jobs-028): Dependency truth drift — 4 zdroje pravdy + stale editable metadata
**Server:** MCP-Jobs | **Status:** Fixed | **Typ:** Environment — dependency contract divergence

**Symptom:** Bug lokálně reprodukovatelný, v Dockeru ne (a naopak); `pip show mcp-jobs` 0.2.0 vs kód/pyproject 0.4.0-0.5.0.
**Root cause:** Čtyři zdroje tvrdí o pandas 4 různé věci: pyproject `<3.0`, requirements.txt (chybí úplně), deploy/dashboard_requirements.txt `==2.3.3`, venv realita `3.0.5`. Samostatně: editable instalace před version bumpama — dist-info štítek 0.2.0 zůstal navíc (metadata se nepřegenerovávají sama).
**Fix:** Jeden zdroj pravdy (pyproject), deriváty synchronizovány; `pip install "pandas>=2,<3"`; reinstall `-e .` (štítek 0.5.0); `pip check` ve verification gate.
**Pravidlo:** P92
**Provenance:** source-read — pyproject.toml, requirements.txt, deploy/dashboard_requirements.txt, pip list/pip show (2026-08-26 session).

#### GT-102 (mcp-jobs-029): Wheel bez package-data — tichá totální degradace scoringu
**Server:** MCP-Jobs | **Status:** Fixed | **Typ:** Packaging — missing data files + silent except

**Symptom:** ŽÁDNÝ symptom — po `pip install .` (wheel) by všechny tech_score v DB byly NULL bez jediné chyby v logu.
**Root cause:** `skills_config.json` vedle kódu, ale mimo `[tool.setuptools.package-data]` → wheel ho neobsahuje → SkillsCatalog FileNotFoundError → broad-except tiše vrátil `{}`. Editable install a Docker COPY fungovaly — rozpad až na Azure wheel deployi.
**Fix:** `[tool.setuptools.package-data] mcp_jobs = ["skills_config.json"]` + build verifikace `pip wheel . --no-deps` + ZipFile.namelist() inspekce — ověřeno buildem, ne konfigurací.
**Pravidlo:** P93
**Provenance:** source-read — pyproject package-data, skills_catalog.py:_load_config, db.py:_extract_skills; wheel build + namelist check 2026-08-26.

#### GT-103 (mcp-jobs-030): Name-based introspekce selhává na heterogenních signaturách
**Server:** MCP-Jobs | **Status:** Fixed | **Typ:** Frontend — dispatcher design

**Symptom:** Analyza tab: `TypeError: portal_effectiveness() missing 1 required positional argument 'high_signal_queries'` a `tech_score_distribution() takes 1 positional argument but 2 were given` — až v runtime.
**Root cause:** Dispatcher hledal podle JMÉNA `"queries" in signature.parameters`; ale `high_signal_queries` ≠ queries, některé funkce berou jen `(conn)`. Dvě kolize téhož typu: jméno ≠ kontrakt.
**Fix:** Explicitní větve pro speciální případy + generický tail váže POZICÍ dle arity (`len(params) >= 2` → `fn(conn, queries)`; konvence metrics.py: 2. poziční parametr = query filtr).
**Pravidlo:** P94
**Provenance:** source-read — dashboard/app.py run_metric, dashboard/metrics.py signatury, data/dashboard.log tracebacky (2026-08-26 session).

#### GT-104 (mcp-jobs-031): Framework logger hierarchy — tracebacky míjejí root handler
**Server:** MCP-Jobs | **Status:** Fixed | **Typ:** Logging — logger hierarchy + idempotency

**Symptom:** `data/dashboard.log` plný INFO z vlastního loggeru, ale streamlit „Uncaught app exception" tracebacks jen na console — v logu nikdy.
**Root cause:** Streamlit logger má vlastní handler chain s `propagate=False` → záznamy nikdy nedorazí k root handleru. Sekundárně: setup volaný z main() běží při KAŽDÉM rerunu → bez guardu duplicitní FileHandlery.
**Fix:** FileHandler přímo na `logging.getLogger("streamlit")` (+ propagate=False proti duplicitám přes root) + idempotence guard flag.
**Pravidlo:** P95
**Provenance:** source-read — dashboard/app.py _setup_logging; pozorování log vs console (2026-08-26 session).

#### GT-105 (mcp-jobs-032): Flaky test race — background job thread + live network I/O v unit testech
**Server:** MCP-Jobs | **Status:** Fixed | **Typ:** Testing — async race + live I/O (příbuzné GT-093)

**Symptom:** `test_store_and_list_resources` občas FAIL (`assert len(listing) == 1` dostal 2); izolovaně PASS; full suite občas PASS.
**Root cause:** Jiný test submitnul REÁLNÝ pipeline job (live scrape); jeho thread zavolal `_store_results()` AŽ PO clear() sdíleného store v pozdějším testu → asynchronní mutace. GT-093 = sekvenční (ordering) varianta; tato časová (thread timing) — horší detekovatelnost.
**Fix:** Monkeypatch stub `_run_pipeline` v submit testu (žádný live scrape, žádný background zápis); full suite 237/237 PASS 2× za sebou.
**Pravidlo:** P96
**Provenance:** source-read — tests/test_server.py submit test, server.py _submit_job/_run_pipeline; reprodukce flake (2026-08-26 session).

### 3.7 GCP Infrastructure & Serverless (z pitevní knihy v8)

Samostatná řada GT-GCP-001..005 (nepřekrývá se s GT-001..GT-105). Přeneseno z `GCP/pitevni_kniha_v8.md` — sémantická analýza + reevaluace (2026-08-21) potvrdila 5 entries s neinferovatelným hSNR datem; ~30 zbývajících záznamů inferovatelných z tréninkových dat LLM nebo příliš specifických (Bazoš scraping).

#### GT-GCP-001 (GCP-009..015): 5vrstvý GCP autentizační stack
**Doména:** GCP Infrastructure | **Status:** Fixed | **Typ:** Authentication — Multi-layer identity conflict

**Symptom:** Opakované `403 Insufficient Permission` / `403 Scopes Error` / SA storage quota, přestože kód má správné SCOPES a složka sdílena. Debug po jedné vrstvě = nikdy celek.
**Root cause:** Autentizace je 5vrstvá, interakce vrstev není popsána v jednom dokumentu: (1) IAM role, (2) Access Scopes (výchozí=uzamčeno), (3) Metadata Server (tokeny), (4) Workspace vs Cloud (`auth/drive` ≠ `cloud-platform`), (5) Service Account quota (SA na osobním účtu = 0 bajtů).
**Fix (checklist při 403):** (1) `gcloud iam roles describe`, (2) VM → Edit → Access Scopes → full access, (3) `curl -H "Metadata-Flavor: Google"`, (4) Workspace: `Credentials.from_service_account_file()`, ne `google.auth.default()`, (5) osobní účty: bez SA (alternativa Telegram Bot API).
**Pravidlo:** P-GCP-01
**Provenance:** source-read (pitevni_kniha_v8.md:009-015, 7 záznamů konsolidovaných)

#### GT-GCP-002 (GCP-019..023): Cron Context na GCP VM
**Doména:** GCP Infrastructure | **Status:** Fixed | **Typ:** Orchestration — Cron environment isolation

**Symptom:** Skript přes SSH funguje, přes crontab: `ModuleNotFoundError`, `sudo: a terminal is required`, `shutdown: command not found`.
**Root cause:** Crontab běží v vakuu — žádný $PATH, žádný TTY (sudo blokováno), žádný $VIRTUAL_ENV, `/sbin/shutdown` mimo PATH; plus GCP default region vs Cloud Shell default mismatch.
**Fix:**
```bash
/home/user/venv/bin/python /home/user/project/main.py   # absolutní cesty
/sbin/shutdown -h now                                    # absolutní cesta
echo "$USER ALL=(root) NOPASSWD: /sbin/shutdown" > /etc/sudoers.d/shutdown
```
**Pravidlo:** P-GCP-02
**Provenance:** source-read (pitevni_kniha_v8.md:019-023, 5 záznamů konsolidovaných)

#### GT-GCP-003 (GCP-032,036): Immutable Infrastructure — save ≠ deploy
**Doména:** GCP Infrastructure | **Status:** Fixed | **Typ:** Serverless — Deployment model

**Symptom:** Uložení souboru v Cloud Shellu se neprojeví v běhu funkce; snaha „opravit běžící skript" selhává.
**Root cause:** Cloud Function = neměnný kontejnerový otisk z doby deploye; Ctrl+S = změna lokální kopie; hotfix za běhu nemožný; `--source .` bere soubory z aktuálního adresáře konzole.
**Fix:** Cyklus Upravit → Ctrl+S → `gcloud deploy` (žádný krok nelze vynechat); před deployem `cat main.py`.
**Pravidlo:** P-GCP-03
**Provenance:** source-read (pitevni_kniha_v8.md:032, 036)

#### GT-GCP-004 (GCP-024,025,044): Serverless Statelessness — /tmp/ jako RAM
**Doména:** GCP Infrastructure | **Status:** Fixed | **Typ:** Serverless — State management

**Symptom:** Skript těží stejné inzeráty dokola; `OSError: [Errno 30] Read-only file system`.
**Root cause:** Cloud Functions: po doběhu se smaže celý FS včetně /tmp/ (RAM-mapped, efemérní); relativní cesty → zápis do read-only root FS.
**Fix:** Pattern START: download z GCS → /tmp/, WORK: zapisovat do /tmp/, END: upload do GCS. Jediná trvalá paměť = GCS Bucket.
**Pravidlo:** P-GCP-04
**Provenance:** source-read (pitevni_kniha_v8.md:024, 025, 044)

#### GT-GCP-005 (GCP-037): Kognitivní přehlcení — Hard Reset protokol
**Doména:** Cross-cutting | **Status:** Documented | **Typ:** Meta — Cognitive ergonomics

**Symptom:** Ztráta přehledu o stavu kódu; kupí se chyby z nepozornosti; pocit bezmoci nad systémem.
**Root cause:** Pracovní paměť má limit — po ~2 h inkrementálních změn bez kontextového resetu je kognitivní zátěž nefaktorovatelná; debug session → kaskáda drobných změn → ztráta orientace.
**Fix („Tlustá čára"):** (1) Smazat poškozený soubor, (2) vložit 100% ověřený blok, (3) smazat data v Bucketu, (4) začít z bodu nula.
**Pravidlo:** P-GCP-05
**Provenance:** source-read (pitevni_kniha_v8.md:037)

---

## 4. Průřezová pravidla P1–P96 + P-GCP-01..05 (kanon; P84–P89 rezervovány epistemické řadě)

### P1 — Paralelizace
Jakmile tool iteruje N>1 nezávislých zdrojů (repozitáře, soubory, API), použij `ThreadPoolExecutor`. Počet workerů: min(4, N). I/O-bound operace skálují lineárne do ~8 vláken.

### P2 — Časové konstanty
Subprocess timeout v MCP toolu musí být max 25% MCP client timeoutu. Client timeout 60s → subprocess timeout 15s. Fail fast, fail loud.

### P3 — Read-only locky
Kazdý read-only subprocess call (git, grep, diff) používej `["git", "--no-optional-locks"]`. Eliminuje filesystem lock contention.

### P4 — JSON defenziva
Kazdý JSON state deserializer: `try/except` + `isinstance(v, dict)` guard + auto-repair. Počítej s corrupt daty.

### P5 — Diagnostika
`@auditable` na kazdém toolu. Povinné: `ts`, `tool`, `duration_s`, `ok`. Bez metriky není diagnostika.

### P6 — Timeout guard
I/O tool s potenciálem >10s → wrapper s `concurrent.futures.TimeoutError`.

### P7 — Globální proměnné
Kazdá funkce, která zapisuje do modulové globální proměnné, musí mít `global jméno`. Python bez `global` vytvorí lokální shadow — tichá ztráta dat.

### P8 — Pořadí operací
Auth/navigace/destruktivní operace: auth first, navigace second. Nic mezi ně nevkládat.

### P9 — Žádné CSS třídy v selektorech
Používej sémantické HTML atributy (`href`, `aria-label`, `role`). CSS třídy jsou ephemeral — A/B testy je mení bez varování.

### P10 — Verifikace cest
`Path.parents` je 0-indexovaný od nejbližšího rodice. Ověř `relative_to()` pred prvním pouzitím.

### P11 — Console script distribution
Po `uv sync` vzdy explicitně ověř, z ekonzolový script je dostupný:
```bash
.venv/Scripts/<tool> --help   # musí fungovat
where <tool>                   # musí najít exe
```
Pokud `where` selze → pridej `.venv/Scripts` do PATH nebo vytvor `.bat` wrapper.

### P12 — Cross-shell launcher
Kazdý CLI nástroj na Windows musí mít `.bat` wrapper v repo root:
```batch
@echo off
"%~dp0.venv\Scripts\<tool>.exe" %*
```

### P13 — Long-running batch operations
MCP tool, který iteruje N>10 I/O operací, musí být buď:
1. Asynchronní s progress streamingem (MCP `ctx.info()`), nebo
2. Nahrazen CLI entry pointem, který obchází MCP transport timeout, nebo
3. **Async submit+poll pattern** (GT-087): tool vrátí okamžitě `{job_id}`, práce běží v `ThreadPoolExecutor` na pozadí, klient polluje `search_status(job_id)` → `{status, elapsed_s, result}`. Jediná varianta, která drží produkční deliverable **bez CLI**.

Současně: client timeout config (např. opencode `timeout` v `opencode.jsonc`) se vztahuje na **ListTools (fetching tools), NE na tool calls** — konfigurovaný timeout nechrání long-running calls; řešení je P13 pattern, ne zvětšení timeoutu (GT-087).

**Varování (GT-089):** submit+poll NEchrání před stderr deadlockem — pokud timeouting `search_status`/`health_check` (ne jen submit), je server frozen (stderr pipe full, lastResort/StreamHandler), ne job běžící; root logger MUSÍ být na FileHandler (P25).

### P14 — Windows path quoting
- Vzdy `pathlib.Path` (nikdy string concatenation)
- Pri predání cesty subprocessu: `str(resolved_path)` + explicitní quoting
- Testuj cesty v cmd.exe, PowerShell i Git Bash
- `_github\` prefix ~70 chars → riziko MAX_PATH (260 chars)

### P15 — Session monitoring
Pred kazdým pipeline runem: (1) `is_logged_in()` + log `page.url`, (2) pokud auth selze, loguj response body (může být checkpoint), (3) `--login` flow bez restartu MCP serveru.

### P16 — PowerShell v bash = piš .ps1 soubor
Nikdy nevkládej PowerShell one-linery do bash stringů. Vzdy: napiš `.ps1` script, spust pres `powershell -File scripts/operace.ps1`.

### P17 — Workspace context export
Kazdý MCP server pro LLM agenty musí:
1. Při startu vypsat workspace root do stderr: `print(f"[server] Workspace root: {root}", file=sys.stderr)`
2. Poskytnout `tool_workspace_info()` vracející root, guardrails profil, index summary
3. Kontextové soubory prednačíst do cache pri startu

### P18 — Console encoding na Windows (Unicode safety)
1. `$env:PYTHONIOENCODING='utf-8'` pred kazdým python príkazem
2. `sys.stdout.reconfigure(encoding='utf-8', errors='replace')` v startupu
3. Emoji zakázána v kódu (.ai_guardrails.json)

### P19 — Structured logging v scrape path
Kazdý scrape modul musí mít: per-card `logger.warning()`, skip counter, 0-ads `logger.error()` alert.

### P20 — ETL health check / session-start protocol
Kazdý MCP server s externími zdroji musí mít: ETL runner + session-start health check + alert threshold (>20% pokles matched ads).

### P21 — L2 Resources (URI-adresovatelná data)
Tool vyrobí data jednou, resource je zpřístupňuje opakovaně. URI schema: `server://{namespace}/{id}`.

### P22 — Windows PowerShell: nikdy `python -c` s komplexním kódem
`python -c "..."` s f-stringy, vnorenými uvozovkami, cykly je křehký. Root cause: Windows API `CommandLineToArgvW` delí argument na mezerách.

### P23 — Windows encoding: PYTHONIOENCODING + PYTHONUTF8 + -X utf8
Tri úrovne ochrany: (1) shell-level env var, (2) process-level `-X utf8`, (3) code-level `sys.stdout.reconfigure()`.

### P24 — Python version audit
- Nikdy pre-release Python (< stable) pro MCP servery
- `requires-python = ">=3.12.0,!=3.11.0rc1,!=3.11.0rc2"` v pyproject.toml
- Version check pri startu serveru

### P25 — stderr hygiene
- Nikdy StreamHandler(sys.stderr) v MCP serveru
- Logovat jen do FileHandler nebo rotating file
- Audit log = file-based, ne stderr-based
- Rozšířeno (GT-089): zákaz platí i pro IMPLICITNÍ cesty na stderr — `logging.lastResort` (root logger bez konfigurace = implicitní StreamHandler stderr) a `print(file=sys.stderr)`. Root logger MUSÍ být konfigurován na FileHandler od prvního startu: `logging.basicConfig(filename=..., level=..., force=True)`. Startup stderr printy max. 1 krátký řádek (P17).

### P26 — asyncio subprocess
- Vsechna I/O v MCP tools pres `asyncio.create_subprocess_exec()`
- `stdin=asyncio.subprocess.DEVNULL` pro git operace
- `asyncio.wait_for(proc.communicate(), timeout=15)` pro fail-fast
- Vzdy `cwd=` explicitně
- `subprocess.run` zakázán v MCP tools

### P27 — MCP test pyramida
1. Unit vrstva — testy logiky jednotlivých nástrojů
2. Integration vrstva — testy MCP request/response (pres FastMCP.call_tool)
3. E2E vrstva — testy pres reálný STDIO transport
4. Smoke test po kazdé změně: `git_status(B2B-Knowledge-Base)` <5s

### P28 — Encoding audit v CI
Kazdý build musí kontrolovat, ze zdrojové soubory neobsahují emoji:
```bash
rg "[\u2600-\u27BF\U0001F000-\U0001FFFF]" src/
```

### P29 — FastMCP main() sync, nikdy async wrapper
`app.run()` (FastMCP) interně volá `anyio.run()` = spoustí vlastní event loop. main() musí byt sync:

```python
# SPRAVNE
def main():
    app.run()

if __name__ == "__main__":
    main()

# CHYBNE — RuntimeError: Already running asyncio
async def main():
    await app.run()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

**Rozsireni:** Po `pip install -e .` se `src` layoutem over `.pth` obsahuje project root, nejen `src/`.

### P30 — LLM response format fallback
`data["choices"][0]["message"]["content"]` není univerzální. Cerebras pouzívá `reasoning` místo `content`. Pouzívat `msg.get("content") or msg.get("reasoning")`.

### P31 — LLM max_tokens pro coaching
Coaching pipeline s 6+ patterny a 5 sekcemi vyzaduje `max_tokens >= 4000`. Default 2000 testovat na reprezentativním vzorku.

### P32 — Cascade status exposure
Cascade fallback musí expose per-provider status (attempted/skipped/error + tokens + cost) do výstupu. Nikdy netlacit stav provideru.

### P33 — Data format change consistency
Po zmene datového formatu aktualizovat VŠECHNY konzumenty. Testovat s reprezentativními daty, ne jen unit testy.

### P34 — Cache schema versioning
Cache/export JSON schema explicitne dokumentovat a verze kontrolovat. Konzumenti pouzívat fallback chain pres `.get()`.

### P35 — Deterministické kroky cacheovat
Stockfish analyza (deterministická) cacheovat pres `game_id + depth`. LLM inference ne — kazdý běh = nová odpoved.

### P36 — Provider model ID overení
Vzdy volat `/v1/models` API pro discovery. Docs a UI jsou nespolehlivé. Testovat s minimálním promptem.

### P37 — Cost/benefit provider governance
Kazdý provider v LLM cascade musí mít explicitní cost schválení. Drazsí alternativy (>2× cena za stejnou kvalitu) blokovat.

### P38 — SNR evaluation framework
Porovnání LLM výstupu: vzdy pouzít SNR framework (grounding 30%, confidence 20%, phase data 15%, hallucinations 20%, structure 10%, concreteness 5%).

### P39 — Multi-API key management
`.env` pro lokální vývoj, `auth.json` pro opencode, `.gitignore` pro oba. Kazdý provider muze mít jiný key management (free vs paid, shared vs dedicated).

### P40 — Env var warning na suboptimal values
Env var s dopadem na kvalitu musí logovat varování pri hodnotách pod doporuceným minimem. Příklad: `LLM_MAX_TOKENS=2000` → warning "recommended >=4000".

### P41 — Dvouúrovnová LLM cache (Level 2)
Per-game LLM analyzu cacheovat do `{game_id}_llm.json`. Agregace pouzívá summaries z cache místo raw dat. Nová hra = 1 L2 call + 1 agregace, ne full re-run. **Aktualizace (v8):** u multi-perspektiva pipeline (dual-cache white+black) MUSÍ klíc obsahovat perspektivu — `{game_id}_{color}_llm.json`. Jinak oba pohledy sdílí soubor a last-writer-wins prepluje opacnou perspektivu. Reference: GT-079.

### P42 — Cascade resilience
Timeout nebo error jednoho providera v cascade nesmí blokovat pipeline. Cascade je resilience pattern — dalsí provider v poradí prevezme.

### P43 — Pipeline mode (monolit vs inkrementalni)
N≤30 → monolit (1 LLM call). N>30 → inkrementalni (per-game cache + aggregate). Golden rules: rychlá analýza = monolit, hromadná / PGN import = inkrementalni. Explicitní override pres `PIPELINE_MODE` env var.

### P44 — Contract testy mezi moduly (Consumer-Driven Contract)
Kazdy modul v pipeline (Stockfish analyzer → prompt builder → LLM) musi mit contract test, ktery overuje konzistenci klícu mezi producerem a consumerem. Consumer definuje kontrakt (jake klíce potrebuje). Test je schema test na realnych datech + placeholder detection. Profesionalni nastroj: Pact. Lightweight varianta: `assert key in data` + `assert "?" not in prompt`. Reference: `01_METODIKY/05_testing/contract_testing_ontologie_v1.md`.

### P45 — API key health check pri startupu
`verify_api_keys()` v `server.py`. Lightweight ping (max_tokens=1, timeout=10s, per-provider). Detekuje neplatny/vyprseny/rate-limited klic pred prvnim tool volanim. Fail fast. Reference: GT-060.

### P46 — Classification branches must be mutually exclusive
Kazda kategorie v if/elif chainu musi mit vlastni append target. Spolecny cil = tichy data corruption. Unit test overuje, ze zadne dve kategorie nesdileji stejny cil. Reference: GT-061.

### P47 — Cross-LLM audit gate
Pred major release: v1 twin scan (architektura, struktura, bez kodu) + v2 code review (implementace, verifikace). Ani jedna faze nestaci sama. Reference: GT-062.

### P48 — Pattern confidence weighted by sample size
`confidence = min(0.95, base * (1 - 1/(N+1))) * evidence_factor`. Minimal sample N >= 5. Hardcoded confidence neodrazi silu evidence. Reference: GT-063.

### P49 — Sanitize user-supplied identifiers before filesystem use
`re.sub(r'[^a-zA-Z0-9_-]', '_', value)` na vsech vstupech (game_id, username, job_id) pred konstrukci File Path. Zaden user input nesmi byt primo segment v ceste. Reference: GT-065.

### P50 — Parametr clamp musí být signalizován
Pokud clamp (max/min) implicitně ořezává uživatelský vstup, musí logovat warning: `f"[clamp] {param}={value} clamped to {clamped}"`. Tichý ořez = nekonzistentní chování. Reference: GT-066.

### P51 — Pending analysis warning
Každý tool závislý na per-game cache musí před zpracováním zkontrolovat pending count a varovat uživatele. Struktura: cache-first → pending warning → processing → výsledek. Reference: GT-067.

### P52 — Ověř parametr knihovny před použitím
`pip show <library> | grep Version` před použitím nového API parametru. API dokumentace Lichess a berserk dokumentace mohou být desynchronizované. Reference: GT-068.

### P53 — MCP tool list je initialize snapshot
Po přidání nového toolu: (1) restart MCP server, (2) restart opencode session, (3) ověř v `list_tools`. Tool list se neaktualizuje za běhu. Reference: GT-069.

### P54 — Pattern discovery validace
Nový pattern musí být validován: (a) N >= 30 pro statistickou signifikanci, (b) ratio >= 1.4 pro praktickou relevanti, (c) potvrzen v 2+ nezávislých analýzách. Reference: GT-070.

### P55 — Silent except je bug
Každý `except Exception: pass` je bug unless proven otherwise. Silent excepty musí být zalogovány. Reference: GT-071.

### P56 — Stockfish PV SAN konverze
Stockfish PV multi-tahové sekvence musí být konvertovány do SAN sekvenčně na kopii boardu. `board.san(m)` validuje proti aktuální pozici, ne proti rootu. Reference: GT-071, GT-075.

### P57 — K0 noise channel
K0 (orákulum/engine) je samostatný noise channel. Každý run reportuje: depth, engine_version, Threads, Hash, nps_benchmark. ACPL z různých depth nejsou srovnatelné bez K0 korekce. Reference: GT-072.

### P58 — Cache version governance
Cache klíč musí obsahovat verzi kódu (`detector_version`). Při cache load: version mismatch → log warning → re-analyze. Nikdy nepoužívat stale cache po code change. Reference: GT-074.

### P59 — PV jsou sekvenční variace
Stockfish PV v multi-PV módu jsou sekvenční variace, ne paralelní alternativy. Každý PV tah aplikovat na kopii boardu. Nikdy nevalidovat N-tý PV tah proti root pozici. Reference: GT-075.

### P60 — Engine lock isolation
Engine lock vytváří coupling mezi analysis call. Exception uvnitř lock bloku může korumpovat stav engine pro následující volání. Mitigace: (a) žádné AssertionError uvnitř locku, (b) engine restart při timeout locku. Reference: GT-076.

### P61 — Truncated engine lines signalizace
Engine lines count pod multipv_target musí být signalizován. Flag `truncated` a `logger.warning()` per BFS. Reference: GT-077.

### P62 — Ruff --fix je destruktivní, side-effect importy s noqa
Ruff `--fix` maže side-effect importy (F401 unused import) — u registračního patternu `@app.tool()` to ruší registrace toolů. Side-effect importy MUSÍ mít `# noqa: F401` per line. Po každém `ruff --fix`: povinně `git diff` + registrační smoke check (`app._tool_manager._tools` count). Pytest destruktivní smazání registrace nezachytí. Doplnění (GT-081): ruff v automatizaci (CI) běží jako `--check` (read-only) — kontrola. `--fix` je **lidská** operace s `git diff` review — mutace. Separace kontroly od mutace je povinná; `--fix` nikdy do CI gate. Reference: GT-078, GT-081.

### P63 — getattr s defaultem maskuje neexistující atributy
`getattr(obj, "neexistujici", default)` vrací default **bez jakékoli signalizace** — u LLM input pipeline to znamená 100 % garbage v promptu (detekováno na `opening_report`, `opponent_pool`: `opening_name`, `player_color`, `acpl`, `result`). Model pole MUSÍ být čtená přes reálné atributy (`a.game.opening`, `a.total_acpl`) — pak neexistující atribut vyhodí AttributeError při testech. Jestliže default je nutný: logovat warning při použití. Reference: GT-079.

### P64 — Contract evoluce na živých datech je additive
Rozšíření povinného klíčového seznamu contract testu, který iteruje REÁLNÁ cache data, zlomí běh na starších souborech (149× cache bez nového klíče). Nový data klíč = (a) additive test `assert data.get(key, default)` MÍSTO rozšíření `PROMPT_TOP_LEVEL_KEYS`, (b) `.get(key, default)` v deserializaci — ne KeyError. Evoluce contractu nikdy nesmí vynutit migraci legacy dat. Reference: GT-079.

### P65 — Timeout cleanup cílí referenci, která volala
`evaluate_move` používá LOKÁLNÍ engine (vlastní instance), ale timeout handler kvitil sdružený `_engine` → kolaterální zabití konkurující analýzy + zbytečný restart. Cleanup funkce MUSÍ přijmout referenci (`_run_engine_call(fn, timeout_s, engine=None)`) a zabít právě ten objekt, který volání spustil. Reference: GT-079.

### P66 — Fail-fast nad tichou substitucí
Validace nemá akceptovat hodnotu, kterou implementace neumí, a nahradit ji substitucí — hlásí neimplementovaný vstup chybou (`source='chesscom' → error dict`). Tichá substituce = klidná špatná data. Výjimka: degradace s markerem (P67). Reference: GT-079.

### P67 — Degradace dat potřebuje počitatelný marker
`except Exception: pass` + `cp_loss = 0` při selhání evaluate_move klasifikovalo chybný tah jako "best" → ACPL systematicky optimistický bez indikace. Degradace MUSÍ být (a) spočítaná (`GameAnalysis.evaluation_errors` čítač, error dict i výjimka → +1), (b) vystavená do LLM promptu (`Eval errors: N (ACPL may be optimistic)`). Rozšíření P55 (log) o měřitelnou expozici. Reference: GT-079.

### P68 — Legacy cache pole s defaultem má guard před parserem
Starší cache soubory mají pole s prázdným/default defaultem (`m.fen=""`) → `chess.Board(fen="")` vyhodí ValueError a zhrotí celou detekci. Pole, které parser zpracovává, musí mít guard na prázdnou hodnotu (`and m.fen`), konzistentní napříč všemi detekčními funkcemi. Reference: GT-079.

### P69 — Názvy souborů/adresářů jen ASCII (konvence ASCII-NOM)
Názvy souborů a adresářů povolují POUZE `[A-Za-z0-9._-]` — žádná diakritika, mezery, ani non-breaking hyphen (U+2011). Obsah souborů zůstává UTF-8 s diakritikou (konvence platí pro názvy, ne obsah). Důvod: ne-ASCII názvy (a) generují mojibake v git objektech (cp1250 vs UTF-8 — GT-080), (b) U+2011 je vizuálně identický s `-` ale jiný codepoint → rozbíjí copy-paste/grep/RAG, (c) cyklický encoding dluh. Transliterace: `Normalize(FormD)` + drop NonSpacingMark, mezera→`_`, U+2011→`-`, ostatní ne-ASCII→`_`. Ověření: `.scripts/ascii_filenames_check.ps1` (exit 0 = OK). Reference: GT-080.

### P70 — Scraping pipeline s detail fetch = 3 fáze
(1) Collect unikátních URL přes všechny query (set pro dedup), (2) parallel fetch s per-portal throttle (ThreadPoolExecutor, max_workers=4), (3) filter nad naplněnou cache. Sekvenční detail fetch = bottleneck, který eskaluje lineárně s počtem matched ads. Reference: GT-083.

### P71 — Cache failure sentinel: 3 stavy (nezkoušeno / úspěch / selhalo)
Cache pro výsledky s možným selháním MUSÍ rozlišovat 3 stavy: (1) nezkoušeno (`None`/absence klíče), (2) úspěch (hodnota), (3) selhalo (sentinel `_FAILED = object()`). Bez sentinelu = opětovné fetch pokusy pro permanentně selhané URL. Reference: GT-085.

### P72 — Lint rule set je součást dependency kontraktu
Bez explicitního `[tool.ruff.lint] select` driftuje rule set s verzí nástroje (ruff>=0.6 bez horní hranice → nová default pravidla → CI fail bez změny kódu). Deterministický `select` (stabilní E4/E7/E9/F + explicitně vybraná moderní pravidla) = single source of truth; intencionální výjimky (BLE001 graceful degradation, E501 design trade-off) se dokumentují v `ignore`, ne v kódu. Komplement GT-081. Reference: GT-086.

### P73 — Test izolace: žádné destruktivní operace proti sdílené DB
Testy NESMÍ destruktivně zasahovat do dat, která sama nevytvořily. `TRUNCATE`/`DROP`/`DELETE` v test fixture je povolen POUZE proti izolované test DB (dedikovaná databáze/schéma/transakce s rollbackem). Společná `DATABASE_URL` pro testy a produkci/dev = kritická chyba (vysoká pravděpodobnost destrukce). Reference: GT-088.

### P74 — Tracking/session parametry NESMÍ být součástí dedup klíče
Scrape URL často obsahují session/tracking parametry, které se mění každý běh: jobs.cz `searchId=<UUID>`, prace.cz `rps=<int>`, profesia `search_id`, `utm_*`. UNIQUE(url) pak nechytí duplicity stejného inzerátu (52 duplicit / 20 skupin v live DB). Stripping patří do **centrálního bodu** (`Ad.__post_init__` / `normalize_url`), ne do per-provider kódu — per-provider řešení drifuje (profesia měla `_clean_detail_url`, jobs/pracecz žádný). Zachovat ostatní query parametry (`page`, sort), odstranit jen tracking. Reference: GT-090.

### P75 — Cross-portal dedup: sdílený fuzzy klíč + DB enforcement + deterministická priorita
Stejný inzerát je cross-publikovaný napříč portály (LMC network: jobs.cz+prace.cz, ManpowerGroup: jenprace+profesia). In-memory dedup nestačí napříč běhy. Vyžaduje: (a) **sdílený normalizovaný fuzzy klíč** (lowercase → NFKD strip diakritiky → en/em-dash→hyphen → kolaps whitespace) mezi pipeline `_dedup` i DB `upsert_ads` — jinak divergence; (b) **DB-level enforcement** (fuzzy sloupce + index, batched lookup `unnest(%s::text[])` = 1 round-trip, ne per-ad SELECT); (c) **deterministickou prioritu vítěze** — bohatost dat (description > salary > company > location), tie-break first-seen (existující radka si podrží URL+portal, bez churn), nikoli hardcoded portál ranking. Reference: GT-091.

### P76 — Anti-bot/consent-page detekce je kombinace hlaviček, ne samotný UA
Bot-detekce (Seznam.cz) reaguje na kombinaci `User-Agent` + `Accept` hlavičky — default HttpClient s UA Chrome/120 + Accept deterministicky vrací consent page (5/5 reprodukce). Fix = per-portal header varianta (UA Chrome/126 BEZ Accept) aplikovaná v `__init__` providera, respektující mockeri. Default HttpClient NEJEDNÁ jako univerzální řešení pro všechny portály. Deterministickou blokaci vždy ověř live testem (5/5), ne předpokladem. Reference: GT-092.

### P77 — 0 karet na stránce N>1 = end-of-list (INFO), ne layout change (ERROR)
`parse_listings` logoval ERROR "container selector returned 0 cards — likely broken" pro libovolnou stránku. False-positive: config `pages` (10) > reálný počet stránek (profesia Praha = 8) → trailing stránky existují s 200 OK a normálním title, ale 0 karet = za koncem seznamu. Rozlišení podle page kontextu: **page 1 + 0 karet = ERROR** (reálný layout change/blok), **page > 1 + 0 karet = INFO** "end of listing reached, stopping". `parse_listings` přijímá `page` parametr (default 1, abstraktní signatura v base.py), `scrape_all` předává aktuální stránku. Není to chyba v datech — je to normální ukončení paginace. Reference: GT-094.

### P80 — Unicode-aware parsing regionálních formátů
Při parsování textových dat s regionálními formáty testuj regex proti reálným datům včetně Unicode variací (en-dash U+2013, non-breaking space U+00A0, různé quote znaky). Nikdy nepředpokládej ASCII-only vstup v multilingual scraping pipeline. En-dash a hyphen-minus jsou vizuálně identické — nutný DB audit, ne vizuální kontrola kódu. Reference: GT-095.

### P81 — Cross-portal dedup signál: title+company, ne URL
Cross-portal analytika nikdy nepoužívá URL jako dedup klíč (každý portál má unikátní URL schéma → overlap metrika vždy 0). Používej title+company (nebo fuzzy_title+fuzzy_company). URL-based dedup platí jen uvnitř jednoho portálu. Reference: GT-096.

### P82 — Modular refactor: žádné vzájemné importy
Při refactoru na balíčky: závislosti se předávají jako parametry (dependency injection), ne importem. Vzor: `tabs/*.py` importuje `metrics`, `filters`, `components`, nikdy `app.py`. Reference: GT-097.

### P83 — Contract testy při package splitu mandatory
Contract testy jsou součástí kroku package split, ne backlogu. Povinné vrstvy: (a) purity (zakázané importy), (b) interface (signatury funkcí), (c) layers (směry importů). Bez nich je modulární architektura křehká. Reference: GT-098.

> **Rezervace P84–P89:** epistemická řada — Gate protokol destruktivních operací. Kanon: `05_EPISTEMIKA/02_agentni_pravidla/EPISTEMICKE-PRAVIDLA-AGENTNI-PRACE.md` §5.4. (P78/P79 nebyly přiděleny.)

### P90 — Frontend smoke test gate + reintrodukce fixu
UI layout změny kolem interaktivních komponent ověř ručním smoke testem — pytest nerenderuje frontend. Znovu-povolení dříve odstraněného triggeru bez reprodukce originálního selhání = reintrodukce bugu; fix bez post-fix verifikace na stejném scénáři není fix. Reference: GT-099.

### P91 — Print-before-raise defense
API s print-before-raise side efektem se neprobouzí „dotykem a try/except" — proběhlý výstup nelze chytit výjimkou. Ověř stav přímo (existence souboru / dokumentovaný flag) nebo potlač konkrétní logger. Reference: GT-100.

### P92 — Dependency kontrakt = jeden zdroj pravdy
pyproject = kontrakt; requirements/deploy soubory = ručně synchronizované deriváty. Po každém version bumpu `pip install -e .` (dist-info metadata se nepřegenerují sama). Verification gate obsahuje `pip check`. Při „u mě padá, u tebe ne" porovnej i `pip list`, ne jen kód. Reference: GT-101.

### P93 — Package-data build verification
Data soubory vedle modulu deklaruj v `[tool.setuptools.package-data]` A ověř build inspekcí (`pip wheel` + namelist) — konfigurace sama není důkaz. Broad-except kolem kritické funkce bez logování maskuje totální rozpad funkce (komplement P55). Reference: GT-102.

### P94 — Structural dispatch over name matching
Když rodina funkcí nemá stabilní jmenný kontrakt, váž strukturou (pozice/arity), ne jmény parametrů — jména jsou v Pythonu jen doporučení. Dispatcher pokrývající rodinu ověř runtime smoke testem celé rodiny, ne vzorkem. Reference: GT-103.

### P95 — Framework logger direct attach + idempotentní setup
Loggery s vlastním chainem (`propagate=False`) potřebují handler připojený přímo na svůj uzel — root config nestačí. Setup funkce volané z render cyklu musí být idempotentní (guard flag), jinak duplicity handlerů/registrací. Reference: GT-104.

### P96 — Žádný live I/O v unit testech
Async/background cesty v testech vždy stubovat (monkeypatch runneru před submittem). Unit testy nesmí provádět live network I/O. Flaky test = determinismus bug, ne „občas se stane" — dvě zelená pásma full-suite za sebou = minimum gate. Reference: GT-105.

### P-GCP-01 — Při 403 v GCP ověřit všech 5 autentizačních vrstev
IAM role → Access Scopes (nejčastější příčina) → Metadata Server identity → Workspace vs Cloud scope mismatch → Service Account quota. Nejčastější selhání: vrstva 2 nebo 4. Reference: GT-GCP-001.

### P-GCP-02 — Crontab ≠ SSH
Absolutní cesty ke všemu: Python interpret, systémové binárky, pracovní adresář. `sudo` jen s NOPASSWD v sudoers.d. GCP region explicitní, ne default. Reference: GT-GCP-002.

### P-GCP-03 — Serverless = Immutable
Uložení souboru ≠ nasazení; oprava za běhu = nemožná. Každá změna = `gcloud deploy`. Reference: GT-GCP-003.

### P-GCP-04 — GCS je jediná trvalá paměť
GCP Cloud Functions: `/tmp/` = RAM, po doběhu smaže vše. Start = download z GCS, konec = upload do GCS. Žádný trvalý stav v kontejneru. Reference: GT-GCP-004.

### P-GCP-05 — Hard Reset protokol
Při zacyklení v chybách >30 minut: smazat poškozený soubor → vložit ověřený blok kódu → smazat data → začít z nuly. Reset není prohra, je optimalizace času. Reference: GT-GCP-005.

---

## 5. Diagnostický filtr — 82 checkpointů

### A — Časové konstanty
1. Je subprocess timeout kratsí nez MCP client timeout? (P2)
2. Je subprocess timeout ≤15s pro git operace? (P2)
3. Mají vsechny subprocess volání explicitní `timeout=`? (P2)

### B — Paralelizace
4. Iteruje tool pres N>1 nezávislých zdrojů? → paralelizovat (P1)
5. Je `git_status_all` implementován s `ThreadPoolExecutor`? (P1)
6. Je `cross_repo_search` s `ThreadPoolExecutor`? (P1)
7. Je počet workerů 4-8 pro I/O-bound? (P1)

### C — Git operace
8. Mají vsechny git subprocess volání `--no-optional-locks`? (P3)
9. Je timeout pro git grep/log/diff jednotný? (P2)
10. Vrací timeoutnutý subprocess error okamzitě? (P2)

### D — JSON storage
11. Má JSON state load `try/except`? (P4)
12. Má kazdá deserializovaná hodnota `isinstance(v, dict)`? (P4)
13. Existuje auto-repair pro poskozené záznamy? (P4)

### E — Diagnostika
14. Mají vsechny nástroje `@auditable` dekorátor? (P5)
15. Loguje audit `duration_s` pro kazdý tool call? (P5)
16. Je audit log JSON lines? (P5)

### F — Timeout guard
17. Má tool s dlouhým během (>10s) timeout wrapper? (P6)
18. Vrací timeoutnutý tool error místo blokování serveru? (P6)

### G — Workspace context
19. Vypisuje server při startu workspace root do stderr? (P17)
20. Existuje tool vracející workspace info? (P17)
21. Jsou kontextové soubory prednačteny při startu? (P17)

### H — Console encoding
22. Je `PYTHONIOENCODING=utf-8` nastaveno? (P18, P23)
23. Má server `sys.stdout.reconfigure(encoding='utf-8')`? (P18)
24. Jsou emoji vyloucena ze zdrojového kódu? (P28)

### I — Python version & deploy
25. Je Python stabilní release (ne rc/alpha/beta)? (P24)
26. Je `requires-python` explicitní v pyproject.toml? (P24)
27. Existuje version check při startu serveru? (P24)

### J — stderr hygiene
28. Je StreamHandler(sys.stderr) odstraněn? (P25)
29. Jsou vsechny print/log výstupy směrovány do souboru? (P25)
30. Je audit log file-based, ne stderr-based? (P25)
31. Je root logger konfigurován na FileHandler od startu (žádný logging.lastResort / implicitní StreamHandler stderr)? (P25, GT-089)

### K — async subprocess
32. Jsou vsechna subprocess volání async? (P26)
33. Mají git operace `stdin=DEVNULL`? (P26)
34. Je timeout ≤15s + `asyncio.wait_for`? (P26)
35. Jsou `cwd` a env parametry explicitní? (P26)

### L — Test pyramida
36. Existuje MCP integration test (tool → framework, bez STDIO)? (P27)
37. Existuje MCP E2E test (pres reálný STDIO)? (P27)
38. Bězí smoke test (`git_status` <5s) po kazdé zmene? (P27)
39. Jsou transport-level anomálie pokryty testy? (P27)

### M — Diagnostika / monitorování
40. Je `git log -5` promptnejsi nez `-20`?
41. Existuje `ping()` tool pro ověření, ze server zije?
42. Je MCP client timeout konfigurovatelný per-tool?
43. Je v logu timestamp + duration pro kazdý subprocess call?
44. Lze rozlišit "server mrtev" od "tool zpracovává"? (GT-089: timeouting poll = server frozen, ne běh jobu)

### N — Encoding & Console (rozsířeno)
45. Je PYTHONIOENCODING=utf-8? (P18, P23)
46. Má server `sys.stdout.reconfigure('utf-8')`? (P18)
47. Jsou emoji a Unicode supplementary zakázány v kódu? (P28)
48. Vrací tool ceské znaky bez chyby? (P23)

### O — Server initialization (P29)
49. Je main() sync `def main(): app.run()`? Nikdy `async` + `asyncio.run()` (P29)
50. Ma `.pth` soubor po `pip install -e .` project root + `src/`, ne jen `src/`? (P29)

### P — Pipeline consistency & cache governance (P50-P54)
51. Je parametr clamp explicitně signalizován warningem při ořezu? (P50)
52. Kontroluje tool před zpracováním pending count a varuje uživatele? (P51)
53. Je verze knihovny ověřena před použitím nového API parametru? (P52)
54. Je nový tool viditelný v `list_tools` po restartu serveru + opencode session? (P53)
55. Je nový pattern validován N>=30, ratio>=1.4, 2+ analýzami? (P54)

### Q — Engine & PV pipeline integrity (P55-P61)
56. Je každý `except` blok zalogován (ne silent pass)? (P55)
57. Jsou Stockfish PV multi-tahové sekvence konvertovány sekvenčně na kopii boardu? (P56, P59)
58. Reportuje každý run K0 metriky (depth, engine_version, Threads, Hash)? (P57)
59. Obsahuje cache klíč detector_version? Je version mismatch detekován při cache load? (P58)
60. Je engine lock dostatečně izolovaný proti error propagaci? (P60)
61. Je engine lines count pod multipv_target signalizován (truncated flag, warning)? (P61)
62. Existuje mechanismus pro re-analyzi při code change (cache invalidation)? (P58)

### R — Data correctness & contract evolution (P63-P68)
63. Jsou model pole čtená přes reálné atributy (`a.field`), ne `getattr(a, "x", default)`? (P63)
64. Je nový data klíč přidán additive (`.get(key, default)` + additive test), ne rozšířením povinného seznamu testovaného na živých datech? (P64)
65. Kvituje timeout/cleanup handler referenci, která volání spustila (lokální vs sdružený engine)? (P65)
66. Hlásí validace neimplementovaný vstup chybou (fail-fast), ne tichou substitucí? (P66)
67. Má degradace dat počitatelný marker (čítač + expozice v LLM promptu)? (P67)
68. Má pole legacy cache s prázdným defaultem guard před parserem (chess.Board(fen=""))? (P68)

### S — Filename nomenklatura (P69, ASCII-NOM)
69. Jsou všechny trackované názvy souborů/adresářů ASCII `[A-Za-z0-9._-]` (žádná diakritika, mezery, U+2011)? (P69) — ověř `.scripts/ascii_filenames_check.ps1`, exit 0
70. Neobsahuje žádný trackovaný soubor staré cesty/názvy po renames (broken reference)? — ověř `.scripts/context_refs_check.py`, exit 0 (kontrakt: GLOBAL_FORBIDDEN + REPO_FORBIDDEN rename mapa + F1_ALLOWLIST)

### T — Lint determinismus & long-running tools (P72, P13)

71. Je lint rule set deterministický — explicitní `[tool.ruff.lint] select`, NE defaultní sada driftující s verzí nástroje? Intencionální výjimky (graceful degradation, line-length) dokumentované v `ignore`, ne v kódu? (P72)
72. Je long-running tool (>10s) async — submit+poll (okamžitý `job_id` + status poll), nebo má explicitní progress streaming / CLI bypass? Client timeout config (např. opencode `timeout`) se nevztahuje na tool calls, jen na ListTools — timeout calls řeší pattern, ne zvětšení timeoutu. (P13)
73. Používají integrační testy izolovanou test DB (dedikovaná databáze/schéma/transakce s rollbackem), ne sdílenou produkční/dev DB? Neobsahuje žádný test fixture destruktivní `TRUNCATE`/`DROP`/`DELETE` proti datům, která test nevytvořil? (P73)

### U — Dedup & anti-bot integrita scrapingu (P74-P77)

74. Jsou tracking/session parametry (`searchId`, `rps`, `search_id`, `utm_*`) odstraněny z URL v centrálním bodě (`Ad.__post_init__`), ne per-provider? Kanonický URL je stabilní napříč běhy (UNIQUE dedup funguje)? (P74)
75. Je cross-portal dedup DB-level (fuzzy sloupce + index) se sdíleným normalizovaným klíčem (NFKD diakritika, en/em-dash→hyphen) mezi pipeline a DB? Má deterministickou prioritu vítěze (bohatost dat, tie-break first-seen)? Používá batched lookup (1 round-trip), ne per-ad SELECT? (P75)
76. Je deterministická anti-bot/consent-page blokace ověřena live testem (5/5 reprodukce) a fixnuta per-portal header variantou (UA+Accept kombinace), ne univerzálním UA? (P76)
77. Loguje stránka s 0 kartami ERROR jen pro page 1 (layout change), a pro page > 1 INFO (end-of-list)? Přijímá `parse_listings` page kontext a `scrape_all` ho předává? (P77)

### V — GCP Infrastructure & Serverless (P-GCP-01..05)

78. Při 403 v GCP: ověřeno všech 5 autentizačních vrstev (IAM role, Access Scopes, Metadata Server, Workspace/Cloud, SA quota)? Nejčastější příčina: Access Scopes nebo Workspace/Cloud mismatch. (P-GCP-01)
79. Crontab na GCP VM: absolutní cesty ke všemu (Python, binárky, adresáře)? sudo s NOPASSWD v sudoers.d? GCP region = správný (ne default)? (P-GCP-02)
80. Serverless immutable: každá změna = `gcloud deploy`, ne hotfix za běhu? `Ctrl+S` = změna lokální kopie, ne deploy. (P-GCP-03)
81. GCP Cloud Functions: `/tmp/` = RAM, po doběhu smaže vše. Start = download z GCS, konec = upload. Žádná trvalá paměť v kontejneru. (P-GCP-04)
82. Při zacyklení v chybách >30 minut: proveden Hard Reset (smazat poškozený soubor → ověřený blok → smazat data → začít z nuly)? Reset = optimalizace, ne prohra. (P-GCP-05)

---

## 6. EROI rozhodovací framework

### 6.1 Kdy MCP NEPOUZÍT

| Situace | Proc MCP nefunguje | Co místo toho |
|---------|-------------------|---------------|
| Sub-100ms operace (ctení 1 souboru) | JSON-RPC overhead > samotná operace | CLI nebo skript |
| Hromadné operace (git status na 13 repo) | Sériové volání 13x tool je pomalejší | Dávkový skript |
| Jednorázové ad-hoc príkazy | Tool musíš definovat, otestovat, dokumentovat | CLI |
| Credentials / secrets | Riziko úniku do LLM kontextu | OS env var + gh CLI |
| 100% determinismus | LLM se muze rozhodnout tool nepouzít | Skript/Makefile |
| Rychle se menící API | Kazdá zmena toolu = restart serveru | Jupyter / skript |

### 6.2 EROI matice

| | Jednoduché rešení | Slozité rešení |
|--|------------------|----------------|
| **Vysoká potřeba MCP** | MCP dává smysl (doménové nástroje, multi-client) | MCP dává smysl |
| **Nízká potřeba MCP** | Nepouzívat (prímý príkaz stací) | Zatím nepouzívat |

### 6.3 Rozhodovací flowchart

```
Potrebuju provést operaci?
├─ Jednorázová? → CLI / rucne
├─ >3×?
│  ├─ Cistě lokální, bez doménového kontextu? → Python skript
│  └─ Potrebuji to zpřístupnit LLM / více klientům?
│     ├─ Read-only a bezpečnostne citlivé? → MCP tool (povolené cesty, audit)
│     ├─ Vyžaduje doménové know-how? → MCP tool (tool description = dokumentace)
│     └─ Write operace? → MCP tool (jen se zárukou bezpecnosti)
└─ >50×? → Zvaž samostatný balícek / pip modul
```

### 6.4 Template pro nový tool

| Otázka | Váha |
|--------|------|
| Frekvence pouzití (>5×/mesíc?) | tool pokud ano |
| Počet klientů (>1?) | tool pokud ano |
| Doménová znalost (střední+?) | tool pokud ano |
| Bezpecnostní riziko (střední+?) | tool (s audit) |
| Write operace? | tool (s validací) |

---

## 7. Dědičnost — checklist pro nový MCP projekt

Při zakládání nového MCP repozitáře:

1. **Console script** (P11+P12) — `[project.scripts]` v pyproject.toml + `.bat` wrapper
2. **Path quoting** (P14) — pathlib.Path pro vsechny cesty
3. **Windows encoding** (P18+P23) — PYTHONIOENCODING + PYTHONUTF8 + -X utf8
4. **Workspace context** (P17) — workspace info tool pri startu
5. **Audit logging** (P5) — @auditable na vsech tool funcích
6. **Test pyramida** (P27) — unit > integration > E2E + smoke test
7. **ETL health check** (P20) — session-start ETL pro scrapers
8. **L2 Resources** (P21) — URI-adresovatelná data
9. **Async subprocess** (P26) — asyncio.create_subprocess_exec, ne subprocess.run
10. **Python version audit** (P24) — requires-python + startup check
11. **FastMCP sync main** (P29) — `def main(): app.run()`. Nikdy `async def` + `asyncio.run()`.
12. **Editable install path** (P29) — po `pip install -e .` se `src` layoutem over `.pth` ma project root + `src/`
13. **LLM response format fallback** (P30) — `msg.get("content") or msg.get("reasoning")` pro kazdého providera
14. **LLM max_tokens** (P31) — `max_tokens >= 4000` pro coaching pipeline
15. **Cascade log exposure** (P32) — per-provider status, tokens, cost v kazdém reportu
16. **API key management** (P39) — `.env` + `auth.json` + `.gitignore` pro vsechny providery
17. **Per-game LLM cache** (P41) — `{game_id}_{color}_llm.json` (perspektiva v klíči u dual-cache pipeline)
18. **Cascade resilience** (P42) — timeout jednoho providera neblokuje pipeline
19. **Contract testing** (P44) — Consumer-Driven Contract mezi Stockfish → prompt builder → LLM
20. **API key health check** (P45) — `verify_api_keys()` při startupu, detekuje 401/402/429
21. **Mutual exclusive classifications** (P46) — kazda kategorie v if/elif ma vlastni append target. Unit test overi separaci.
22. **Cross-LLM audit gate** (P47) — v1 twin scan + v2 code review pred major release.
23. **Pattern confidence weighting** (P48) — `f(N, evidence_strength)`, hardcoded confidence zakazano.
24. **Path sanitization** (P49) — `re.sub(r'[^a-zA-Z0-9_-]', '_', value)` na user inputech pred filesystem use.
25. **Parametr clamp signalizace** (P50) — clamp nesmi byt tichy, logovat warning pri orezavani.
26. **Pending analysis warning** (P51) — detekce + signalizace neanalyzo-vanych her pred kazdym tool zpracovanim.
27. **Library version check** (P52) — `pip show <library>` pred pouzitim noveho API parametru.
28. **Tool list snapshot** (P53) — po pridani toolu restartovat server + opencode session, overit `list_tools`.
29. **Pattern discovery validation** (P54) — N>=30, ratio>=1.4, potvrzeno 2+ analyzami.
30. **Silent except audit** (P55) — kazdy `except Exception: pass` nahradit logovanim
31. **Stockfish PV SAN konverze** (P56, P59) — sekvencni board.copy() pro PV multi-tahove sekvence
32. **K0 metriky v reportu** (P57) — depth, engine_version, Threads, Hash, nps benchmark
33. **Cache governance** (P58) — detector_version v cache klíci, version mismatch → re-analyze
34. **Engine lock isolation** (P60) — per-call isolation, restart pri timeout locku
35. **Truncated engine lines signal** (P61) — flag truncated + logger.warning() per BFS
36. **Cache invalidation mechanismus** (P58) — automaticka detekce stale cache po code change
37. **Lint autofix guard** (P62) — side-effect importy s `# noqa: F401`, po `ruff --fix` vzdy `git diff` + registracni smoke check
38. **Model field access** (P63) — data do LLM promptu pres realne atributy modelu, ne `getattr` s defaultem; default = warning
39. **Additive contract evolution** (P64) — novy klic pres `.get(key, default)` + additive test, nikdy rozsireni povinneho seznamu na zivych datech
40. **Cleanup target reference** (P65) — timeout/cleanup handler kviti referenci, ktera volala (parametr, ne sdruzeny global)
41. **Fail-fast validation** (P66) — neimplementovany vstup = error dict, ne ticha substituce
42. **Degradation marker** (P67) — pocitatelny citac degradace + expozice v LLM promptu
43. **Legacy field guard** (P68) — pole cache s prazdnym defaultem guard pred parserem (konzistentni s detekcnimi funkcemi)
44. **ASCII filenames** (P69) — vsechny nazvy souboru/adresaru ASCII `[A-Za-z0-9._-]`; overeni `.scripts/ascii_filenames_check.ps1` (exit 0)
45. **Lint determinismus** (P72) — explicitni `[tool.ruff.lint] select` (stabilni E4/E7/E9/F + explicitni moderni pravidla); intencionalni vyjimky (BLE001, E501) v `ignore` s komentarem; horni hranice na ruff v deps
46. **Async submit+poll** (P13) — long-running tool vrati okamzite `{job_id}`, prace v ThreadPoolExecutor, `search_status(job_id)` poll; client timeout config (opencode `timeout`) chrani ListTools, ne calls
47. **Test izolace** (P73) — integracni testy proti dedikovane test DB (databaze/schema/transakce s rollbackem), nikdy TRUNCATE/DROP/DELETE proti sdilene produkci/dev DB; sdilena DATABASE_URL testu a produkce = kriticka chyba
48. **URL canonicalizace** (P74) — tracking/session parametry (searchId, rps, search_id, utm_*) odstraneny v centralnim bode Ad.__post_init__; kanonicky URL = dedup klic, per-provider cleanup zakazan (drift)
49. **DB-level cross-portal dedup** (P75) — sdileny normalizovany fuzzy klic (NFKD + dash→hyphen) mezi pipeline a DB, fuzzy sloupce + index, batched lookup, priorita vitez dle bohatosti dat (description>salary>company>location), tie-break first-seen
50. **Anti-bot per-portal headers** (P76) — deterministicka anti-bot/consent blokace (UA+Accept kombinace) overena live testem (5/5), fix per-portal header variantou v __init__ providera
51. **End-of-list vs layout change** (P77) — 0 karet na strance page>1 = INFO end-of-list (config `pages` > realny pocet stranek), ERROR jen pro page 1. `parse_listings` prijima `page` kontext (default 1), `scrape_all` ho predava. Reference: GT-094.
52. **GCP 5vrstvá autentizace** (P-GCP-01) — při 403 v GCP ověřit 5 vrstev: IAM role, Access Scopes, Metadata Server, Workspace/Cloud, SA quota. Nejčastější: Access Scopes nebo Workspace/Cloud mismatch. Source: GT-GCP-001.
53. **Cron ≠ SSH** (P-GCP-02) — crontab na GCP VM = absolutní cesty, sudo s NOPASSWD v sudoers.d, GCP region explicitní (ne default). Source: GT-GCP-002.
54. **Serverless immutable** (P-GCP-03) — Cloud Function = neměnný kontejnerový otisk. Ctrl+S = lokální kopie. Oprava = gcloud deploy. Source: GT-GCP-003.
55. **GCS je jediná trvalá paměť** (P-GCP-04) — Cloud Functions /tmp/ = RAM, po doběhu smaže vše. Start = download z GCS, konec = upload. Source: GT-GCP-004.
56. **Hard Reset protokol** (P-GCP-05) — při zacyklení >30 minut: smazat poškozený soubor, vložit ověřený blok, smazat data, začít z nuly. Source: GT-GCP-005.
57. **Unicode-aware regex** (P80) — při parsování textových dat s regionálními formáty: otestovat regex proti reálným datům VCETNE Unicode variací (en-dash U+2013, non-breaking space U+00A0, různé quote znaky). Nikdy nepředpokládat ASCII-only vstup v multilingual scraping pipeline. En-dash a hyphen-minus vypadají identicky — vizuální kontrola nepomůže, nutný DB audit. Source: GT-095.
58. **Cross-portal dedup: title+company, ne URL** (P81) — cross-portal analytika: nikdy nepoužívat URL jako dedup klíč napříč portály (každý portál má unikátní URL schéma). Používat title+company (nebo fuzzy_title+fuzzy_company) jako dedup signál. URL-based dedup funguje jen uvnitř jednoho portálu. Source: GT-096.
59. **Modular dependency injection** (P82) — při refactoru na balíčky: žádné vzájemné importy mezi moduly. Závislosti se předávají jako parametry. Vzor: `tabs/*.py` importuje `metrics`, `filters`, `components`, nikdy `app.py`. Source: GT-097.
60. **Contract tests mandatory při splitu** (P83) — při refactoru na balíčky: contract testy součástí kroku 4 (package split), ne backlog. Povinné: purity (zakázané importy), interface (signatury), layers (směry importů). Source: GT-098.
61. **Frontend smoke test gate** (P90) — UI layout změny kolem `st.dataframe(on_select)` ověřovat ručním během; pytest nerenderuje frontend. Znovu-povolení odstraněného triggeru bez reprodukce = reintrodukce. Source: GT-099.
62. **Print-before-raise defense** (P91) — API s warning-before-exception side efektem neověřovat dotykem+try/except; ověřit stav přímo (existence souboru). Source: GT-100.
63. **Single dependency source of truth** (P92) — pyproject = kontrakt, requirements/deploy = synchronizované deriváty; po version bump `pip install -e .`; `pip check` ve verification gate. Source: GT-101.
64. **Package-data build verification** (P93) — data soubory deklarovány v package-data + ověřeny wheel namelist inspekcí; broad-except bez logování maskuje totální rozpad. Source: GT-102.
65. **Structural dispatch over name matching** (P94) — dispatcher rodiny funkcí váže pozicí/arity, ne názvy parametrů; runtime smoke test celé rodiny. Source: GT-103.
66. **Framework logger direct attach** (P95) — loggery s propagate=False potřebují handler přímo na uzlu; setup v render cyklu idempotentní (guard flag). Source: GT-104.
67. **No live I/O in unit tests** (P96) — async/background cesty stubovat monkeypatchem; flaky = determinismus bug; 2 zelená pásma = minimum gate. Source: GT-105.

---

## 8. Statistiky

| Metrika | Hodnota |
|---------|---------|
| Celkem GT | **108** (GT-001..GT-105, mezery GT-082/GT-084 + GT-GCP-001..GT-GCP-005) |
| Fixed (vč. „Fixed / Mitigated", „Fixed (policy)") | 74 |
| Implemented | 6 |
| Mitigated | 6 |
| Documented | 18 |
| Workaround | 3 |
| Pending | 1 |
| **Kontrolní součet** | **108** |

Rozpad: environment/CI 11 · application logic 63 · cross-repo 17 · cross-LLM audit 5 (GT-061..065) · DBCL Phase 2 7 (GT-071..077) · data-correctness batch 1 (GT-079) · ASCII-NOM 1 (GT-080) · GCP infra 5 (GT-GCP-001..005).

---

*MCP_GROUND_TRUTH_postmortem_agregovany_v2.md — 2026-08-26 — v20 (souborová generace v2) — trim iterace A nad v1/v19 dle sémantické analýzy 2026-08-26: (1) dedup `Pravidlo:` textů entrií → ukazatele, kanonický text výhradně §4; (2) kanonizace P80–P83 a P90–P96 do §4 (ve v1 definovány pouze inline); (3) odstranění duplicitního footer changelogu, per-version poznámek ve statistikách a sebekorekčního narrativu (plná historie verzí = git log repa; komprese −30 % při zachování 108 GT záznamů, 48 Provenance polí a všech file:line referencí); (4) integritní opravy: titulek §4 (P1–P96), titulek §5 (82 checkpointů), reference GT-083 P71→P70, dokumentace mezer GT-082/GT-084 a P78/P79, stale rozsah v úvodu §3.7. Originál v1 zachován do validace v2 (rozhodnutí autora 2026-08-26); po validaci přesunout do `_ARCHIVE/`. Header/footer verze 20 konzistentní.*
