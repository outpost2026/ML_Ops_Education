# MCP GT — Katalog chyb (generated from full JSONL)

**Entries:** 111 | **Format:** JSONL-derived markdown

#### GT-001 (CNC-001): scraping
**Server:** cnc-tools | **Status:** fixed

**Symptom:** `MCP error -32001` při `tool_git_status_all`/`tool_cross_repo_search`; audit `duration_s` 61.7–62.4 s (>60 s client timeout).
**Root cause:** Sériová iterace 14 repozitářů v jedné smyčce (14 × 4.4 s).
**Fix:** `ThreadPoolExecutor(max_workers=4)` → ~15 s.
**Pravidlo:** P1
**Tags:** p1

#### GT-002 (CNC-002): timeout
**Server:** cnc-tools | **Status:** fixed

**Symptom:** `tool_git_diff` error až po 60 s (30 s subprocess + 30 s client = dvojité čekání).
**Root cause:** Subprocess timeout (30 s) příliš blízko client timeoutu (60 s).
**Fix:** Subprocess timeout ≤15 s — fail fast.
**Pravidlo:** P2
**Tags:** p2 | timeout

#### GT-003 (CNC-003): devops
**Server:** cnc-tools | **Status:** fixed

**Symptom:** `git status`/`git diff` trvaly 3–5 s na read-only operaci.
**Root cause:** Git implicitně zapisuje `.git/index.lock`; chyběl `--no-optional-locks`.
**Fix:** `["git", "--no-optional-locks", ...]` ve všech subprocess voláních.
**Pravidlo:** P3
**Tags:** p3 | git

#### GT-004 (CNC-004): data-integrity
**Server:** cnc-tools | **Status:** fixed

**Symptom:** `tool_session_state` failuje `'str' object has no attribute 'get'`.
**Root cause:** `.ai_state.json` obsahoval string místo dict; `v.get()` padá na non-dict.
**Fix:** `isinstance(v, dict)` check + auto-repair mechanismus.
**Pravidlo:** P4
**Tags:** p4 | json

#### GT-005 (CNC-005): general
**Server:** cnc-tools | **Status:** fixed

**Symptom:** Bez audit logu nelze identifikovat zdroj timeoutu (šedá zóna subprocess/client timeout).
**Root cause:** Žádná per-tool duration telemetrie.
**Fix:** `@auditable` dekorátor na všech tool funkcích; povinné `ts`, `tool`, `duration_s`, `ok`.
**Pravidlo:** P5
**Tags:** p5

#### GT-006 (CNC-006): timeout
**Server:** cnc-tools | **Status:** fixed

**Symptom:** Jeden pomalý tool (62 s) blokuje celý STDIO server (half-duplex).
**Root cause:** FastMCP nemá per-tool timeout.
**Fix:** Wrapper s `concurrent.futures.TimeoutError` pro I/O tooly >10 s.
**Pravidlo:** P6
**Tags:** p6 | timeout

#### GT-007 (CNC-007): auth
**Server:** cnc-tools | **Status:** fixed

**Symptom:** LLM volá nástroje s `C:\_github\...` → „mimo povolený rozsah"; 2–3 iterace hádání cesty.
**Root cause:** `ALLOWED_ROOTS` je interní konstanta — LLM nemá mechanismus, jak ji zjistit.
**Fix:** `tool_workspace_info()` + workspace root do stderr při startu.
**Pravidlo:** P17
**Tags:** p17 | llm | path

#### GT-008 (CNC-008): encoding
**Server:** cnc-tools | **Status:** fixed

**Symptom:** `UnicodeEncodeError: 'charmap' codec` při tisku emoji/Unicode (Windows cp1250 console).
**Root cause:** Windows Console + Python stdout encoding = cp1250.
**Fix:** `sys.stdout.reconfigure(encoding='utf-8', errors='replace')` + `$env:PYTHONIOENCODING='utf-8'`.
**Pravidlo:** P18
**Tags:** p18 | encoding

#### GT-009 (CNC-009): timeout
**Server:** cnc-tools | **Status:** fixed

**Symptom:** Všechny git nástroje timeoutují -32001 po 60 s; git z bash <1 s.
**Root cause:** Python 3.11.0rc2 — nedokončený subprocess pipe management na Windows → pipe buffer deadlock.
**Fix:** Stable Python (3.11.9); `requires-python` vylučuje rc verze.
**Pravidlo:** P24
**Tags:** p24

#### GT-010 (CNC-010): timeout
**Server:** cnc-tools | **Status:** fixed

**Symptom:** Latentní deadlock i po fixu verze Pythonu.
**Root cause:** `StreamHandler(sys.stderr)` v audit.py — plná pipe buffer (4–64 KB) → event loop freeze → MCP timeout.
**Fix:** StreamHandler odstraněn, pouze FileHandler.
**Pravidlo:** P25
**Tags:** p25

#### GT-011 (CNC-011): subprocess
**Server:** cnc-tools | **Status:** fixed

**Symptom:** Git subprocess drží MCP STDIO handles → pipe se nikdy neuzavře → client timeout.
**Root cause:** `subprocess.run()` dědí všechny handles rodiče.
**Fix:** `asyncio.create_subprocess_exec()` + `stdin=asyncio.subprocess.DEVNULL`.
**Pravidlo:** P26
**Tags:** p26 | subprocess

#### GT-012 (CNC-012): tooling
**Server:** cnc-tools | **Status:** fixed

**Symptom:** 67 unit testů PASS, E2E odhalil 14 anomálií (git timeout, VCF binary, encoding) — transport-level vrstvy netestovány.
**Root cause:** Chyběla integration a E2E vrstva.
**Fix:** Pyramida unit → integration → E2E + smoke test po každé změně.
**Pravidlo:** P27
**Tags:** p27 | test

#### GT-013 (CNC-013 = LNKD-016 = JOBS merged): timeout
**Server:** cnc-tools | **Status:** fixed

**Symptom:** `analyze_saved_jobs` (N=27, ~85 s) a `get_saved_jobs` → -32001; JSON-RPC/stdio má client timeout 60–120 s; sekvenční scraping N×~3 s limit překračuje.
**Root cause:** MCP není navržen pro long-running batch operace.
**Fix:** (1) per-job tool místo batch, (2) CLI test skript bypassující transport, (3) time-budget (`limit` + `max_seconds`, vracet `unprocessed_ids`).
**Pravidlo:** P13
**Tags:** p13 | timeout

#### GT-014 (CNC-014): general
**Server:** cnc-tools | **Status:** fixed

**Symptom:** 6 toolů vracelo emoji markery ([OK], [FAIL], [!], [TIMEOUT]) místo ASCII-safe textu.
**Root cause:** Historický vizuální pozůstatek; nezachyceno code review ani testy.
**Fix:** Emoji → ASCII markery; CI-greppovatelný audit: `rg "[\u2600-\u27BF\U0001F000-\U0001FFFF]" src/`.
**Pravidlo:** P28
**Tags:** p28

#### GT-015 (LNKD-007): general
**Server:** linkedin-mcp-custom | **Status:** fixed

**Symptom:** Typová záměna BrowserContext vs Browser
**Root cause:** `get_or_create_browser()` vracelo `BrowserContext`, volající očekával `Browser` (Patchright rozlišuje process vs izolovaný session).
**Fix:** Singleton na úrovni `BrowserContext`; všechny tool funkce přijímají `context` a volají `context.new_page()`.
**Pravidlo:** P9
**Tags:** playwright

#### GT-016 (LNKD-008): general
**Server:** linkedin-mcp-custom | **Status:** fixed

**Symptom:** Shadow lokální proměnná (missing global)
**Root cause:** Zápis do globální proměnné bez `global` deklarace vytvoří lokální shadow — `close_browser()` nastavovala lokální `_context = None`.
**Fix:** `global _context, _page, _playwright` v každé zapisující funkci.
**Pravidlo:** P7
**Tags:** p7

#### GT-017 (LNKD-009): auth
**Server:** linkedin-mcp-custom | **Status:** fixed

**Symptom:** Auth navigační konflikt
**Root cause:** `is_logged_in()` volalo `page.goto("/feed/")` → opuštění cílové stránky; extrakce pokračovala na prázdné stránce.
**Fix:** Pořadí: (1) `ensure_authenticated(page)`, (2) navigace na target URL.
**Pravidlo:** P8
**Tags:** p8 | auth

#### GT-018 (LNKD-010): scraping
**Server:** linkedin-mcp-custom | **Status:** fixed

**Symptom:** Fragilita CSS selektorů
**Root cause:** LinkedIn A/B testy mění CSS class names bez varování → ephemeral selektory.
**Fix:** Dvě vrstvy: specifický CSS selector + text-based fallback (`innerText` matching).
**Pravidlo:** P9
**Tags:** p9

#### GT-019 (LNKD-011): general
**Server:** linkedin-mcp-custom | **Status:** fixed

**Symptom:** Paginační slepota
**Root cause:** (1) Přepisovač cílové stránky místo klikání na „Další", (2) po kliknutí bez čekání na DOM refresh.
**Fix:** `_click_next_page()` hledající „Další" + `wait_for_timeout(3000)` + `wait_for_selector`.
**Pravidlo:** P9
**Tags:** pagination

#### GT-020 (LNKD-012): auth
**Server:** linkedin-mcp-custom | **Status:** fixed

**Symptom:** Špatný git repo root v parents indexu
**Root cause:** `Path.parents` je 0-indexovaný od nejbližšího rodiče; použit `parents[2]` místo `parents[1]`.
**Fix:** Oprava indexu + `relative_to()` assert pro verifikaci.
**Pravidlo:** P10
**Tags:** p10 | git

#### GT-021 (LNKD-013): general
**Server:** linkedin-mcp-custom | **Status:** fixed

**Symptom:** Fragilní extrakce job ID
**Root cause:** Extrakce hledala jen `[href*="/jobs/view/"]`; ID je i v data atributech, script JSON blobu, `aria-label`.
**Fix:** 4-vrstvá extrakce: `<a href>` → element attributes → script JSON → full outerHTML regex.
**Pravidlo:** P9
**Tags:** extraction

#### GT-022 (LNKD-014): dedup
**Server:** linkedin-mcp-custom | **Status:** fixed

**Symptom:** KBWriter dedup fallback — industry vždy None
**Root cause:** `_find_entry_index()` porovnával `title|company` proti `title|company.industry` (vždy None) → company name se nikdy neukládala.
**Fix:** Ukládat `eroi.company` do `company.industry`.
**Pravidlo:** P9
**Tags:** dedup | dedup

#### GT-023 (LNKD-015): general
**Server:** linkedin-mcp-custom | **Status:** fixed

**Symptom:** Summary table non-idempotent
**Root cause:** `_update_summary_table()` vždy appendovala řádek bez kontroly existence ID.
**Fix:** Existence-check před appendem; existuje-li → replace.
**Pravidlo:** P9
**Tags:** idempotency

#### GT-024 (LNKD-017): general
**Server:** linkedin-mcp-custom | **Status:** fixed

**Symptom:** Python version mismatch (.venv vs system)
**Root cause:** `.python-version` = 3.12, `.venv` vytvořen se system Python 3.11; závislosti vyžadují ≥3.12.
**Fix:** `uv venv --python 3.12 && uv sync`.
**Pravidlo:** P11
**Tags:** python

#### GT-025 (LNKD-018): auth
**Server:** linkedin-mcp-custom | **Status:** fixed

**Symptom:** Console script not in PATH
**Root cause:** `uv sync` instaluje konzolové scripty do `.venv/Scripts/`, který není v system PATH.
**Fix:** `.bat` wrapper v repo root + `.venv/Scripts` do User PATH.
**Pravidlo:** P11
**Tags:** p11 | path

#### GT-026 (LNKD-020): auth
**Server:** linkedin-mcp-custom | **Status:** fixed

**Symptom:** Cookie lifecycle — silent expiry
**Root cause:** Session cookies mají neurčitou expiraci (dny až týdny); bez pre-checku nedetekovatelné.
**Fix:** Cookie age tracking + checkpoint detection + `ensure_authenticated()` před každým scrapingem.
**Pravidlo:** P15
**Tags:** p15

#### GT-027 (LNKD-021): data-integrity
**Server:** linkedin-mcp-custom | **Status:** fixed

**Symptom:** CI/CD cookie export — cookies nejsou JSON
**Root cause:** Patchright persistent context ukládá cookies do Chromium SQLite databáze, ne JSON.
**Fix:** `scripts/export_cookies.py`: `context.cookies()` → JSON → GitHub Secret → `context.add_cookies()`.
**Pravidlo:** P9
**Tags:** json | cookies

#### GT-028 (LNKD-022): auth
**Server:** linkedin-mcp-custom | **Status:** documented

**Symptom:** PAT workflow scope
**Root cause:** `git push` rejectnut — PAT postrádá `workflow` scope.
**Fix:** Doplnit `workflow` scope v GitHub Developer settings.
**Pravidlo:** P9
**Tags:** git

#### GT-029 (LNKD-024): tooling
**Server:** linkedin-mcp-custom | **Status:** fixed

**Symptom:** Scorer unit test discovery
**Root cause:** 6/27 nových testů měla očekávání neodpovídající skutečné scorer logice.
**Fix:** Testy opraveny na aktuální chování — slouží jako living documentation. ### 3.3 MCP-Jobs
**Pravidlo:** P27
**Tags:** test | testing

#### GT-030 (JOBS-022): auth
**Server:** mcp-jobs | **Status:** fixed

**Symptom:** Silent failure pattern
**Root cause:** Všichni 4 scrapery `except Exception: continue` → tichá ztráta dat při změně HTML struktury.
**Fix:** Per-card `logger.warning()`, skip counter, 0-ads `logger.error()` alert.
**Pravidlo:** P19
**Tags:** p19 | pattern

#### GT-031 (JOBS-023/SHELL-019/PS-034): parsing
**Server:** mcp-jobs | **Status:** fixed

**Symptom:** (a) Salary filter rejectuje český formát čísla, (b) PowerShell v bash stringu 3/3 selhání, (c) f-string SyntaxError při `python -c "..."`.
**Root cause:** Textová data nelze parsovat bez respektu locale/encoding; shell escaping na Windows je 3-vrstvý problém (PowerShell → cmd.exe → Python).
**Fix:** (1) `_SALARY_NUM_RE = re.compile(r'\d{1,3}(?:[ \u00a0]\d{3})+|\d+')` respektující český formát, (2) PowerShell operace jako `.ps1` soubory, (3) zákaz komplexního `python -c` na Windows.
**Pravidlo:** P16
**Tags:** p16 | regex

#### GT-032 (JOBS-024): parsing
**Server:** mcp-jobs | **Status:** fixed

**Symptom:** Exclude čeština — domain-specific semantics
**Root cause:** Czech exclude termíny (`poptavam`, `shanim`) aplikovány globálně; na Bazosu značí validní poptávku zaměstnance.
**Fix:** Portal-specific exclude listy; jednoznačné multiword `hledam praci` ponecháno.
**Pravidlo:** P9
**Tags:** parsing

#### GT-033 (JOBS-025): packaging
**Server:** mcp-jobs | **Status:** mitigated

**Symptom:** ETL feedback loop dependency
**Root cause:** Žádný mechanismus pravidelného ověření funkčnosti scraperů; HTML portálů se mění bez varování.
**Fix:** ETL runner + session-start health check + `output/etl_latest.json`.
**Pravidlo:** P20
**Tags:** p20

#### GT-034 (JOBS-026): llm
**Server:** mcp-jobs | **Status:** mitigated

**Symptom:** LLM-assisted dev blind spots
**Root cause:** LLM detekuje degradaci existujícího kódu teoreticky, ale ne bez reálných dat.
**Fix:** Pravidelný ETL feedback loop + version comparison + testy na reálném HTML.
**Pravidlo:** P9
**Tags:** llm | llm

#### GT-035 (JOBS-027): general
**Server:** mcp-jobs | **Status:** fixed

**Symptom:** AST re-parse per ad
**Root cause:** `parse_boolean()` voláno pro každý inzerát zvlášť (8 query × 1000 ads = 8000 parsování).
**Fix:** `@functools.lru_cache(maxsize=128)` → 8 parsování.
**Pravidlo:** P9
**Tags:** parsing

#### GT-036 (JOBS-028): general
**Server:** mcp-jobs | **Status:** fixed

**Symptom:** Chybějící guardraily (pages + rate limiting)
**Root cause:** Bulk-scrape bez limitu — `pages=500` by spustilo stovky requestů.
**Fix:** Clamp guard + `request_delay=1.0` + `_throttle()`.
**Pravidlo:** P13
**Tags:** guardrails

#### GT-037 (JOBS-029): general
**Server:** mcp-jobs | **Status:** fixed

**Symptom:** Boolean auto-validace při config loadu
**Root cause:** `validate_boolean()` existovala, nikdo ji nevolal při loadu configu.
**Fix:** Volání v `UserConfig._from_raw()`.
**Pravidlo:** P9
**Tags:** config

#### GT-038 (JOBS-030): general
**Server:** mcp-jobs | **Status:** fixed

**Symptom:** MCP error kontrakt
**Root cause:** Každý tool řešil error handling jinak; per-provider errors embedded v datech.
**Fix:** Jednotný formát `[{"error": "..."}]` pro všechny tools.
**Pravidlo:** P9
**Tags:** mcp

#### GT-039 (JOBS-031): tooling
**Server:** mcp-jobs | **Status:** fixed

**Symptom:** Config error messages + lint
**Root cause:** `CategoryConfig(**c)` házel raw TypeError na neznámý YAML klíč.
**Fix:** try/except s popisnou zprávou; importy top-level.
**Pravidlo:** P9
**Tags:** config

#### GT-040 (JOBS-033): general
**Server:** mcp-jobs | **Status:** fixed

**Symptom:** L2 Resources — mcp-jobs://ads/{query_id}
**Root cause:** Search results jen v kontextu LLM — neadresovatelné po ukončení callu.
**Fix:** 3 resources `/list`, `/{query_id}`, `/{query_id}/report` + in-memory store.
**Pravidlo:** P21
**Tags:** p21

#### GT-041 (JOBS-034+035): encoding
**Server:** mcp-jobs | **Status:** implemented

**Symptom:** 6-layer encoding stack
**Root cause:** see source
**Fix:** see source
**Pravidlo:** P23
**Tags:** encoding | encoding

#### GT-042 (CNC-014 continuation): general
**Server:** mcp-jobs | **Status:** documented

**Symptom:** Session compact — MCP workdir vs source code
**Root cause:** see source
**Fix:** see source
**Pravidlo:** P17
**Tags:** session

#### GT-043 (lichess-001): general
**Server:** mcp-jobs | **Status:** fixed

**Symptom:** `python -m src.server` → `ModuleNotFoundError: No module named 'src'`; opencode hlásí status „invalid".
**Root cause:** `uv pip install -e .` vytvořilo `.pth` s jedinou řádkou `...\src`; kod importuje `from src.app import app` → potřebuje project root na sys.path (bez něj hledá `src/src/server.py`).
**Fix:** Druhá řádka do `.pth`: ``` C:\Users\PC\Documents\Repozitar_Dev\_github\lichess-analyzer-mcp C:\Users\PC\Documents\Repozitar_Dev\_github\lichess-analyzer-mcp\src ```
**Pravidlo:** P29
**Tags:** p29

#### GT-044 (lichess-002): general
**Server:** mcp-jobs | **Status:** fixed

**Symptom:** Server startne (logy na stderr), pak okamžitě `RuntimeError: Already running asyncio in this thread`.
**Root cause:** FastMCP `app.run()` interně volá `anyio.run(self.run_stdio_async)` — vlastní event loop; obalení do `asyncio.run(main())` vytváří druhou loop.
**Fix:** Sync main (kanonický pattern viz §4 P29).
**Pravidlo:** P29
**Tags:** p29

#### GT-045 (lichess-003): general
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** Cerebras vrací 200 OK, ale `message.content` je None → pipeline padá do fallback/raw JSON dumpu.
**Root cause:** Cerebras používá proprietární `reasoning` field místo standardního `content`.
**Fix:** Fallback chain v parseru (viz P30).
**Pravidlo:** P30
**Tags:** p30

#### GT-046 (lichess-004): llm
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** DeepSeek V4 Flash report useknutý uprostřed (2895 tok); chybí závěrečné sekce.
**Root cause:** Default 2000 tok nedostatečný pro 6 patternů + weakness report + 5 sekcí (real ~3500 tok).
**Fix:** `LLM_MAX_TOKENS=4000`.
**Pravidlo:** P31
**Tags:** p31 | llm

#### GT-047 (lichess-005): llm
**Server:** lichess-analyzer | **Status:** mitigated

**Symptom:** Uživatel nevidí, které providery cascade zkusila a který vyhrál.
**Root cause:** Cascade log vracen jen ve variantě with_logs; stav providerů není nikde perzistentní.
**Fix:** Log paralelně s reportem; header uvádí provider/model/tokens/cost/latency.
**Pravidlo:** P32
**Tags:** p32

#### GT-048 (lichess-006): general
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** `TypeError: unsupported format string passed to dict.__format__` po LLM callu; report se nezapíše.
**Root cause:** Timing formát změněn z float na dict; konzument zůstal na starém přístupu.
**Fix:** `.get("total", {}).get("duration", 0)` u všech konzumentů.
**Pravidlo:** P33
**Tags:** p33

#### GT-049 (lichess-007): cache
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** `compare_providers.py` čte 0 patternů z cached dumpu.
**Root cause:** Klíče dumpu (`patterns_detected`, `games_analyzed`) ≠ hledané (`patterns`, `analyses_data`).
**Fix:** Fallback chain přes `.get()`; cache/export schema dokumentovat a verzovat.
**Pravidlo:** P34
**Tags:** p34 | cache

#### GT-050 (lichess-008): chess-engine
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** 5 her = 24 min; 99.9 % času Stockfish (deterministický krok).
**Root cause:** see source
**Fix:** Cache-first: check `data/game_cache/{game_id}...json` (depth-gated) → hit = reuse, miss = analyze+store. Re-run 5 her = 0.1 s.
**Pravidlo:** P35
**Tags:** p35

#### GT-051 (lichess-009): llm
**Server:** lichess-analyzer | **Status:** mitigated

**Symptom:** Cerebras model ID z docs vrací 404; NVIDIA endpoint SSL hostname mismatch.
**Root cause:** Model ID != display name/docs; NVIDIA endpoint není standardní `/v1` schema.
**Fix:** Discovery vždy přes `/v1/models`; po změně endpointu test minimálním promptem (2026-07-20 vyřešeno).
**Pravidlo:** P36
**Tags:** p36

#### GT-052 (lichess-010): analytics
**Server:** lichess-analyzer | **Status:** documented

**Symptom:** SNR evaluation framework
**Root cause:** see source
**Fix:** see source
**Pravidlo:** P38
**Tags:** p38

#### GT-053 (lichess-011): general
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** DeepSeek Chat — cost ban policy
**Root cause:** see source
**Fix:** see source
**Pravidlo:** P37
**Tags:** p37

#### GT-054 (lichess-012): llm
**Server:** lichess-analyzer | **Status:** documented

**Symptom:** Multi-provider API key management
**Root cause:** see source
**Fix:** see source
**Pravidlo:** P39
**Tags:** p39

#### GT-055 (lichess-013): general
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** `LLM_MAX_TOKENS` tiše fallbackuje na 2000 bez varování o nedostatečnosti.
**Root cause:** see source
**Fix:** Startup warning při hodnotách pod doporučeným minimem.
**Pravidlo:** P40
**Tags:** p40

#### GT-056 (lichess-014): cache
**Server:** lichess-analyzer | **Status:** implemented

**Symptom:** Nová hra → LLM layer znovu na VŠECHNY hry; lineární růst prompt size a cost.
**Root cause:** see source
**Fix:** see source
**Pravidlo:** P41
**Tags:** p41 | cache | llm

#### GT-057 (lichess-015): timeout
**Server:** lichess-analyzer | **Status:** documented

**Symptom:** NVIDIA timeout na agregaci
**Root cause:** Prompt s summaries (~2500 znaků) → vyšší timeout pravděpodobnost na free NVIDIA tieru; Cerebras/DeepSeek uspějí.
**Fix:** Cascade resilience — timeout providera přeskočen; pro agregaci se summaries nepoužívat NVIDIA.
**Pravidlo:** P42
**Tags:** p42 | timeout

#### GT-058 (lichess-016): cache
**Server:** lichess-analyzer | **Status:** implemented

**Symptom:** Pipeline mode — monolit vs inkrementální cache
**Root cause:** see source
**Fix:** see source
**Pravidlo:** P43
**Tags:** p43 | cache

#### GT-059 (lichess-017): llm
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** _build_game_prompt wrong key names → low SNR
**Root cause:** see source
**Fix:** see source
**Pravidlo:** P44
**Tags:** p44

#### GT-060 (lichess-018): data-integrity
**Server:** lichess-analyzer | **Status:** implemented

**Symptom:** Iterační optimalizace — JSON validation, CI/CD, unit testy služeb, API key check
**Root cause:** see source
**Fix:** see source
**Pravidlo:** P45
**Tags:** p45 | json | test

#### GT-061 (lichess-019): llm
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** `GameAnalysis.mistakes` vždy prázdné; tahy s cp loss 150–299 končí v `blunders`.
**Root cause:** `game_analyzer.py:161-162` — `if classification in ("blunder", "mistake")` se sdíleným append targetem; chybí separátní elif větev.
**Fix:** Rozdělení na `if blunder` / `elif mistake`.
**Pravidlo:** P46
**Tags:** p46 | llm

#### GT-062 (lichess-020): llm
**Server:** lichess-analyzer | **Status:** documented

**Symptom:** Cross-LLM audit workflow validation (Methodology)
**Root cause:** see source
**Fix:** see source
**Pravidlo:** P47
**Tags:** p47 | llm

#### GT-063 (lichess-021): auth
**Server:** lichess-analyzer | **Status:** documented

**Symptom:** (1) Confidence hardcoded (0.6/0.5/0.8/0.7/0.7) nezávisle na N a síle evidence; (2) Pattern G `frequency` = zaokrouhlená blunder rate místo počtu postžených her → semantický mismatch filtru `frequency >= min_occurrences` (pattern projde/neprojde z jiného důvodu než zamýšleno).
**Root cause:** see source
**Fix:** see source
**Pravidlo:** P48
**Tags:** p48 | pattern

#### GT-064 (lichess-022): analytics
**Server:** lichess-analyzer | **Status:** documented

**Symptom:** `diagnostician.py:52` používá absolutní počet blunderů v middlegame → bias vůči dlouhým hram.
**Root cause:** see source
**Fix:** see source
**Pravidlo:** P48
**Tags:** analytics

#### GT-065 (lichess-023): auth
**Server:** lichess-analyzer | **Status:** mitigated

**Symptom:** `game_id`/`username` přímo v cestách bez sanitizace (`game_analyzer.py:14-15`, `lichess_client.py:47-48,74-77`) — `game_id="../../sensitive"` může zapisovat/číst mimo cache adresář.
**Root cause:** see source
**Fix:** see source
**Pravidlo:** P49
**Tags:** p49 | path | security

#### GT-066 (lichess-024): subprocess
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** `fetch_games(max_games=999)` tiše vrátí max 50 her; stejný clamp v `match_patterns` a `diagnose_player` — žádný warning, cache/index nekonzistence (načteno 50, index hlásí 63).
**Root cause:** see source
**Fix:** Clamp na 999 + odstranění tichých clampů + `get_pending_analysis()` kontrola rozdílu index vs cache.
**Pravidlo:** P50
**Tags:** p50

#### GT-067 (lichess-025): chess-engine
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** Tool volaný na N hrách z toho M neanalyzováno → nekompletní výsledky bez upozornění (falešný pocit kompletnosti).
**Root cause:** see source
**Fix:** `get_pending_analysis()` (index vs cache diff) + warning + batch tool `analyze_pending`.
**Pravidlo:** P51
**Tags:** p51

#### GT-068 (lichess-026): scraping
**Server:** lichess-analyzer | **Status:** documented

**Symptom:** `export_by_player(..., before=...)` → TypeError. Berserk 0.14 parametr neexponuje (přidán 0.15+); Lichess API ho podporuje, knihovna ne.
**Root cause:** see source
**Fix:** Reverze kódu; upgrade až bude berserk 0.15+ dostupný.
**Pravidlo:** P52
**Tags:** p52

#### GT-069 (lichess-027): cache
**Server:** lichess-analyzer | **Status:** workaround

**Symptom:** Nový tool registrován v Python/FastMCP, ale neviditelný v opencode client tool listu.
**Root cause:** Host drží tool-list snapshot z prvního initialize handshaku; nerevaliduje při reconnectu/session refresh. Tool existuje v procesu (`app._tool_manager.list_tools()`), volatelný přímo, ale ne přes UI.
**Fix:** see source
**Pravidlo:** P53
**Tags:** p53 | cache

#### GT-070 (lichess-028): auth
**Server:** lichess-analyzer | **Status:** documented

**Symptom:** Pattern G (Color as modulator) — new pattern detection
**Root cause:** see source
**Fix:** see source
**Pravidlo:** P54
**Tags:** p54 | pattern

#### GT-071 (lichess-029): chess-engine
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** 30/101 BFS (30 %) má 0 engine_lines; postihuje i ground truth hry. `analyze_position(multipv=3)` vrací `[]`.
**Root cause:** see source
**Fix:** see source
**Pravidlo:** P55
**Tags:** p55 | engine

#### GT-072 (lichess-030): chess-engine
**Server:** lichess-analyzer | **Status:** documented

**Symptom:** kNAMNYUF ply 63: 607 cp (d12) vs 773 cp (d14) = 171cp rozdíl. ACPL z různých depth runů nejsou srovnatelné (RUN_003 vs RUN_004).
**Root cause:** Depth impactuje eval precision (~3× rychlejší d12 = méně přesný); K0 variance nekvantifikována ani reportována.
**Fix:** see source
**Pravidlo:** P57
**Tags:** p57

#### GT-073 (lichess-031): chess-engine
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** Volání bez `Limit(depth=depth)` — Stockfish sahá do libovolné hloubky na nestabilních pozicích (timeout risk, plýtvání compute).
**Root cause:** see source
**Fix:** `engine.analysis(board, chess.engine.Limit(depth=depth))`.
**Pravidlo:** P56
**Tags:** engine | depth

#### GT-074 (lichess-032): cache
**Server:** lichess-analyzer | **Status:** workaround

**Symptom:** Po opravě kódu vrací `use_cache=True` stale BFS s 0 engine_lines; uživatel musí cache ručně mazat.
**Root cause:** Cache JSON nemá `detector_version`/`code_version` klíč → nelze detekovat starší generaci kódu.
**Fix:** see source
**Pravidlo:** P58
**Tags:** p58 | cache

#### GT-075 (lichess-033): chess-engine
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** Stockfish PV multi-move SAN conversion — domain knowledge gap
**Root cause:** see source
**Fix:** see source
**Pravidlo:** P59
**Tags:** p59

#### GT-076 (lichess-034): chess-engine
**Server:** lichess-analyzer | **Status:** mitigated

**Symptom:** AssertionError uvnitř lock bloku korumpuje engine stav → selhávají všechny následující analýzy v runu.
**Root cause:** `_acquire_analysis_lock`/`_release` coupling mezi nezávislými calls; `finally` release provede i po AssertionError, ale engine může zůstat nekonzistentní.
**Fix:** see source
**Pravidlo:** P60
**Tags:** p60 | engine

#### GT-077 (lichess-035): filesystem
**Server:** lichess-analyzer | **Status:** pending

**Symptom:** BFS s méně než multipv_target engine_lines projdou bez upozornění — nelze identifikovat částečné výpadky.
**Root cause:** see source
**Fix:** see source
**Pravidlo:** P61
**Tags:** p61

#### GT-078 (lichess-036): tooling
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** `ruff check --fix` smazal 18 `from ...tools import X` importů z `server.py` (diff -18/+2) → registrace toolů přes `@app.tool()` zrušena; server by startoval bez toolů. Pytest 93/93 PROŠEL (testy server.py neimportují); detekce až díky `git diff --stat`.
**Root cause:** Registrační pattern side-effect imports vs F401 unused-import autofix. Baseline: 46 errorů (18× F401) na 3 souborech.
**Fix:** Importy obnoveny s `# noqa: F401` per line; verifikace registračním smoke checkem (`app._tool_manager._tools` = 18) + pytest; nový tool s noqa od počátku.
**Pravidlo:** P62
**Tags:** p62 | import

#### GT-079 (lichess-037): data-integrity
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** Data-correctness batch 1+2 — 6 merged bugů LLM input pipeline
**Root cause:** LLM prompt čten přes neexistující atributy/getattr defaulty bez signalizace — data bez markeru kvality = falešná autorita.
**Fix:** Reálná pole modelu + color-aware win_rate; `_resolve_colors()` z PGN headerů; KB_ROOT 4× ".." + import-time check + timestamp; klíč `{game_id}_{color}_llm.json`; `_run_engine_call(fn, timeout_s, engine=None)` cílí volající referenci; `evaluation_errors` čítač + prompt marker „Eval errors: N"; guard `and m.fen`.
**Pravidlo:** P63–P68
**Tags:** p63–p68 | llm

#### GT-080 (workspace-wide): encoding
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** GitHub GUI zobrazoval `02_ANALÝZY` jako mojibake; diagnostika: žádná strukturální inkonzistence (stejný SHA, 61=61 souborů), ale mojibake bytes v git objektech (cp1250 filesystem bytes místo UTF-8). Celkem 20 trackovaných ne-ASCII názvů v 6 repech (diakritika, mezery, U+2011 non-breaking hyphen).
**Root cause:** Encoding dluh — git ukládá path jako raw bytes; U+2011 vizuálně identický s `-` ale jiný codepoint → rozbíjí copy-paste/grep/RAG lookup. Každá ne-ASCII cesta = budoucí bug (cyklický encoding dluh).
**Fix:** (1) Konvence ASCII-NOM `[A-Za-z0-9._-]` (obsah zůstává UTF-8); (2) transliterace `Normalize(FormD)` + drop NonSpacingMark, mezera→`_`, U+2011→`-`; (3) rename přes filesystem objekty + `git mv` (obsah nedotčen); (4) `.gitignore` fix po renames; (5) content reference update (7 souborů); (6) guard `.scripts/ascii_filenames_check.ps1` (exit 0/1, 19/19 repo OK); (7) kontraktní validátor `.scripts/context_refs_check.py` — 1386 trackovaných souborů/19 rep, odhalil a opravil 31 broken referencí (GLOBAL_FORBIDDEN + REPO_FORBIDDEN mapa + F1_ALLOWLIST).
**Pravidlo:** P69
**Tags:** p69 | git

#### GT-081 (lichess-038): tooling
**Server:** lichess-analyzer | **Status:** documented

**Symptom:** Architektonický původ ruffu — CI gate, ne pre-commit hook
**Root cause:** see source
**Fix:** see source
**Pravidlo:** P62
**Tags:** p62

#### GT-083 (mcp-jobs-010): parsing
**Server:** lichess-analyzer | **Status:** documented

**Symptom:** Detail fetch sekvenčně uvnitř filter fáze → ~30 s jen na fetch při 46 matched ads; bottleneck eskaluje lineárně s počtem ads.
**Root cause:** see source
**Fix:** see source
**Pravidlo:** P70
**Tags:** p70

#### GT-085 (mcp-jobs-012): cache
**Server:** lichess-analyzer | **Status:** documented

**Symptom:** Selhaný detail fetch zapsán jako None — stejná hodnota jako „nezkoušeno" → opětovné fetch pokusy pro permanentně selhané URL.
**Root cause:** see source
**Fix:** see source
**Pravidlo:** P71
**Tags:** p71 | cache | pattern

#### GT-086 (mcp-jobs-013): tooling
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** CI failoval `ruff check` s 70 chybami bez jakékoli změny kódu.
**Root cause:** see source
**Fix:** Explicitní `[tool.ruff.lint]` select (stabilní E4/E7/E9/F + moderní UP/RUF/PIE/FURB/DTZ) + ignore BLE001 zdokumentovaný; E501 záměrně mimo (design trade-off); kódové fixy (RUF012 ClassVar, DTZ datetime.now(UTC), PIE810 tuple, RUF003 en-dash).
**Pravidlo:** P72
**Tags:** p72

#### GT-087 (mcp-jobs-014): timeout
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** `search_from_config` přes MCP → -32001; CLI běh fungoval (34.5 s). Server „neodpovídá".
**Root cause:** see source
**Fix:** see source
**Pravidlo:** P13
**Tags:** p13 | timeout

#### GT-088 (mcp-jobs-015): tooling
**Server:** lichess-analyzer | **Status:** documented

**Symptom:** Po `pytest tests/test_db.py` s nastavenou DATABASE_URL zmizela data z PostgreSQL (ads 70→3, pipeline_runs 5→2) — historické ETL runs nevratně.
**Root cause:** Fixture `conn()` dělá `TRUNCATE ... RESTART IDENTITY CASCADE`; skip guard kontroluje jen existenci env var; testy se připojují na stejnou DB jako dev/produkce. Produkční layer je INSERT-only → destrukce výhradně z test kódu.
**Fix:** see source
**Pravidlo:** P73
**Tags:** p73 | test

#### GT-089 (mcp-jobs-016): timeout
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** I po submit+poll (GT-087) timeouť i rychlé tooly (`search_status`, `health_check`) při plném runu; ad-hoc searchy a CLI fungovaly.
**Root cause:** see source
**Fix:** see source
**Pravidlo:** P25
**Tags:** p25 | timeout

#### GT-090 (mcp-jobs-017): dedup
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** Live DB 167 řádků, ale jen 135 unikátních inzerátů — 52 duplicit / 20 skupin; UNIQUE constraint duplicity nechytil.
**Root cause:** jobs.cz `?searchId=<UUID>`, prace.cz `?rps=<int>` — session parametry mění raw URL každý běh → `ON CONFLICT (url)` insertuje znovu. Profesia měla vlastní `_clean_detail_url()`, jobs/prace.cz žádný → nekonzistentní ochrana napříč providery.
**Fix:** Centrální `normalize_url()` (strip searchId/search_id/rps/utm_*; preserve page/sort) v `Ad.__post_init__` — kanonický URL u zdroje dat. DB vyčištěna 167→135.
**Pravidlo:** P74
**Tags:** p74 | dedup

#### GT-091 (mcp-jobs-018): data-integrity
**Server:** lichess-analyzer | **Status:** implemented

**Symptom:** 9 cross-portal skupin stejného inzerátu (LMC network jobs.cz+prace.cz; ManpowerGroup jenprace+profesia); pipeline dedup selhával na variantách `Praha-Uhříněves` vs `Praha – Uhříněves` (en-dash U+2013 vs hyphen) a nepersistoval do DB.
**Root cause:** Fuzzy klíč nenormalizovaný; dedup jen in-memory; pipeline a DB používaly RŮZNÉ klíče.
**Fix:** Sdílený `fuzzy_key()` (lowercase → NFKD strip diakritiky → dash→hyphen → whitespace kolaps) v pipeline I `upsert_ads`; DB fuzzy sloupce + index; batched lookup `unnest(%s::text[])` (1 round-trip); priorita bohatost dat (description 8 > salary 4 > company 2 > location 1), tie-break first-seen. Live DB 135→125, 0 duplicit.
**Pravidlo:** P75
**Tags:** p75 | dedup

#### GT-092 (mcp-jobs-019): scraping
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** Volnamista scraper 0 ads — deterministická consent/bot-detekce stránka (5/5 live runů, ne intermittent).
**Root cause:** Default HttpClient posílá UA Chrome/120 + Accept hlavičku — tato kombinace spouští headrovou fingerprint detekci Seznamu (ne rate-limit, ne captcha).
**Fix:** Provider vlastní `_SEZNAM_HEADERS` = UA Chrome/126 BEZ Accept, aplikované v `__init__` (přepíše injektovaný HttpClient; mockeri respektováni). Listing i detail. Verifikace 5/5 → 0/5.
**Pravidlo:** P76
**Tags:** p76

#### GT-093 (mcp-jobs-020): tooling
**Server:** lichess-analyzer | **Status:** documented

**Symptom:** Test projde izolovaně, failuje v plné sadě (187 testů) — `_query_store` obsahuje 2 záznamy místo 1.
**Root cause:** Modulový globální dict sdílený testy bez per-test resetu; collection order určuje výsledek.
**Fix:** see source
**Pravidlo:** P73
**Tags:** p73 | test

#### GT-094 (mcp-jobs-021): scraping
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** ERROR profesia „likely broken (page layout change)" — dev hlásil podezření na layout change.
**Root cause:** Config pages:10, ale profesia Praha má 8 stránek (157 ads); stránky 9-10 existují (200 OK, normální title, paginace) ale mají legitimně 0 karet — za koncem seznamu. Selektor funkční (live ověřeno).
**Fix:** `parse_listings(page: int = 1)` parametr (base.py signatura + všech 6 providerů); page 1 + 0 karet = ERROR (reálný layout change/blok), page > 1 + 0 karet = INFO „end of listing reached". `scrape_all` předává page; `new == 0` break zůstává vrstvou 2. Live: scrape_all(max_pages=10) → 157 ads, 0 failed.
**Pravidlo:** P77
**Tags:** p77

#### GT-095 (mcp-jobs-022): encoding
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** Dashboard salary pracecz hodnoty 45/43/42 tis. Kč místo reálných 47915/46625/44500 — systematicky podhodnocené, žádná chyba, data vypadala platná.
**Root cause:** Salary formát `65 000 – 80 000 Kc` s en-dash U+2013; regex/SUBSTRING matchoval jen ASCII hyphen → extrakce jen lower bound; en-dash v 35/61 unikátních formátů. En-dash a hyphen-minus vizuálně identické — vizuální kontrola kodu ani outputu neodhalí.
**Fix:** `REGEXP_SPLIT_TO_ARRAY(salary, '[-\u2013]')` + `REGEXP_REPLACE(parts[N], '[^0-9]', '', 'g')`; CTE lower/upper/avg. Live: pracecz avg 42 → 47915 Kč.
**Pravidlo:** P80
**Tags:** p80 | regex

#### GT-096 (mcp-jobs-023): dedup
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** Dashboard „Cross-Query Overlap" hlásil vždy 0 — intuitivně nesmysl (stejné firmy inzerují na více portálech).
**Root cause:** `GROUP BY url`, ale url má UNIQUE constraint — každý inzerát má unikátní URL i když je to stejný job jinde. Cross-portal stejné inzeráty mají vždy různá URL.
**Fix:** `GROUP BY title, company HAVING COUNT(DISTINCT portal) > 1`; metrika přejmenována na Cross-Portal Overlap. Audit: 4 reálné duplicity.
**Pravidlo:** P81
**Tags:** p81 | dedup

#### GT-097 (mcp-jobs-024): packaging
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** `ImportError: cannot import name 'render_ads_tab' from 'dashboard.tabs.ads'` při startu streamlit dashboardu.
**Root cause:** `tabs/ads.py` importoval `run_query` z app.py, app.py importuje tabs → cyklus; Python nedokončí inicializaci modulu.
**Fix:** Zavislost jako parametr — `render_ads_tab(conn, run_query, where_sql, where_params)`; moduly se nikdy navzájem neimportují.
**Pravidlo:** P82
**Tags:** p82 | import

#### GT-098 (mcp-jobs-025): tooling
**Server:** lichess-analyzer | **Status:** implemented

**Symptom:** Po 5 krocích refactoru (filters, metrics, package split, bulk status) chybělo testování integrity modulů; contract testy byly v artifactu v sekci „Later/backlog" — bez explicitního dotazu by zůstaly neimplementovány.
**Root cause:** see source
**Fix:** `tests/test_dashboard_contract.py` — 9 testů: purity (metrics/styling nesmí importovat streamlit), interface (signatury), layers (směry importů).
**Pravidlo:** P83
**Tags:** p83 | test

#### GT-099 (mcp-jobs-026): data-integrity
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** Klik na řádek tabulky → `Minified React error #185` (Maximum update depth exceeded), prohlížeč kolabuje; pytest 237/237 PASS — chyba jen v runtime.
**Root cause:** Známá třída bugů streamlit#7949/#9490: `st.dataframe(use_container_width=True, on_select="rerun")` uvnitř st.tabs + podmíněné bloky renderované POD tabulkou → layout shift → resize loop gridu. Aggravátor: pandas 3.0.5 ve venv mimo vlastní pin <3.0 (lokálně padá, v Dockeru ne). Procesová vrstva: commit `8ff1c6e` odstranil on_select (fungovalo), commit `1602982` ho vrátil s jiným guardem BEZ reprodukce originálního scénáře → reintrodukce.
**Fix:** Detail panel NAD tabulku + selection persistence (`session_state.ads_selected_ids`) + jediný `st.rerun()` při změně výběru; pandas downgrade do specifikace. Sidebar varianta zamítnuta UX.
**Pravidlo:** P90
**Tags:** p90

#### GT-100 (mcp-jobs-027): general
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** `No secrets found...` 2× při startu dashboardu, přestože kód má try/except kolem st.secrets.
**Root cause:** Pouhý dotek `st.secrets` (i přes getattr `_file_path`) spustí parse, který NEJDŘÍV tiskne warning (streamlit/runtime/secrets.py:111) a AŽ POTOM vyhodí výjimku — try/except zachytí výjimku, proběhlý tisk nikdy.
**Fix:** Existence-check secrets.toml PŘED dotykem API (`Path.home()/".streamlit"/secrets.toml`, cwd varianta); st.secrets čten jen při fyzické existenci (`src/mcp_jobs/db.py:get_database_url`).
**Pravidlo:** P91
**Tags:** p91

#### GT-101 (mcp-jobs-028): data-integrity
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** Bug lokálně reprodukovatelný, v Dockeru ne (a naopak); `pip show mcp-jobs` 0.2.0 vs kód/pyproject 0.4.0-0.5.0.
**Root cause:** Čtyři zdroje tvrdí o pandas 4 různé věci: pyproject `<3.0`, requirements.txt (chybí úplně), deploy/dashboard_requirements.txt `==2.3.3`, venv realita `3.0.5`. Samostatně: editable instalace před version bumpama — dist-info štítek 0.2.0 zůstal navíc (metadata se nepřegenerovávají sama).
**Fix:** Jeden zdroj pravdy (pyproject), deriváty synchronizovány; `pip install "pandas>=2,<3"`; reinstall `-e .` (štítek 0.5.0); `pip check` ve verification gate.
**Pravidlo:** P92
**Tags:** p92

#### GT-102 (mcp-jobs-029): data-integrity
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** ŽÁDNÝ symptom — po `pip install .` (wheel) by všechny tech_score v DB byly NULL bez jediné chyby v logu.
**Root cause:** `skills_config.json` vedle kódu, ale mimo `[tool.setuptools.package-data]` → wheel ho neobsahuje → SkillsCatalog FileNotFoundError → broad-except tiše vrátil `{}`. Editable install a Docker COPY fungovaly — rozpad až na Azure wheel deployi.
**Fix:** `[tool.setuptools.package-data] mcp_jobs = ["skills_config.json"]` + build verifikace `pip wheel . --no-deps` + ZipFile.namelist() inspekce — ověřeno buildem, ne konfigurací.
**Pravidlo:** P93
**Tags:** p93

#### GT-103 (mcp-jobs-030): general
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** Analyza tab: `TypeError: portal_effectiveness() missing 1 required positional argument 'high_signal_queries'` a `tech_score_distribution() takes 1 positional argument but 2 were given` — až v runtime.
**Root cause:** Dispatcher hledal podle JMÉNA `"queries" in signature.parameters`; ale `high_signal_queries` ≠ queries, některé funkce berou jen `(conn)`. Dvě kolize téhož typu: jméno ≠ kontrakt.
**Fix:** Explicitní větve pro speciální případy + generický tail váže POZICÍ dle arity (`len(params) >= 2` → `fn(conn, queries)`; konvence metrics.py: 2. poziční parametr = query filtr).
**Pravidlo:** P94
**Tags:** p94

#### GT-104 (mcp-jobs-031): general
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** `data/dashboard.log` plný INFO z vlastního loggeru, ale streamlit „Uncaught app exception" tracebacks jen na console — v logu nikdy.
**Root cause:** Streamlit logger má vlastní handler chain s `propagate=False` → záznamy nikdy nedorazí k root handleru. Sekundárně: setup volaný z main() běží při KAŽDÉM rerunu → bez guardu duplicitní FileHandlery.
**Fix:** FileHandler přímo na `logging.getLogger("streamlit")` (+ propagate=False proti duplicitám přes root) + idempotence guard flag.
**Pravidlo:** P95
**Tags:** p95

#### GT-105 (mcp-jobs-032): tooling
**Server:** lichess-analyzer | **Status:** fixed

**Symptom:** `test_store_and_list_resources` občas FAIL (`assert len(listing) == 1` dostal 2); izolovaně PASS; full suite občas PASS.
**Root cause:** Jiný test submitnul REÁLNÝ pipeline job (live scrape); jeho thread zavolal `_store_results()` AŽ PO clear() sdíleného store v pozdějším testu → asynchronní mutace. GT-093 = sekvenční (ordering) varianta; tato časová (thread timing) — horší detekovatelnost.
**Fix:** Monkeypatch stub `_run_pipeline` v submit testu (žádný live scrape, žádný background zápis); full suite 237/237 PASS 2× za sebou.
**Pravidlo:** P96
**Tags:** p96 | test

#### GT-GCP-001 (GCP-009..015): infrastructure
**Server:** gcp | **Status:** fixed

**Symptom:** Opakované `403 Insufficient Permission` / `403 Scopes Error` / SA storage quota, přestože kód má správné SCOPES a složka sdílena. Debug po jedné vrstvě = nikdy celek.
**Root cause:** Autentizace je 5vrstvá, interakce vrstev není popsána v jednom dokumentu: (1) IAM role, (2) Access Scopes (výchozí=uzamčeno), (3) Metadata Server (tokeny), (4) Workspace vs Cloud (`auth/drive` ≠ `cloud-platform`), (5) Service Account quota (SA na osobním účtu = 0 bajtů).
**Fix:** see source
**Pravidlo:** P-GCP-01
**Tags:** p-gcp-01 | gcp

#### GT-GCP-002 (GCP-019..023): infrastructure
**Server:** gcp | **Status:** fixed

**Symptom:** Skript přes SSH funguje, přes crontab: `ModuleNotFoundError`, `sudo: a terminal is required`, `shutdown: command not found`.
**Root cause:** Crontab běží v vakuu — žádný $PATH, žádný TTY (sudo blokováno), žádný $VIRTUAL_ENV, `/sbin/shutdown` mimo PATH; plus GCP default region vs Cloud Shell default mismatch.
**Fix:** ```bash /home/user/venv/bin/python /home/user/project/main.py # absolutní cesty /sbin/shutdown -h now # absolutní cesta echo "$USER ALL=(root) NOPASSWD: /sbin/shutdown" > /etc/sudoers.d/shutdown ```
**Pravidlo:** P-GCP-02
**Tags:** p-gcp-02 | gcp

#### GT-GCP-003 (GCP-032): devops
**Server:** gcp | **Status:** fixed

**Symptom:** Uložení souboru v Cloud Shellu se neprojeví v běhu funkce; snaha „opravit běžící skript" selhává.
**Root cause:** Cloud Function = neměnný kontejnerový otisk z doby deploye; Ctrl+S = změna lokální kopie; hotfix za běhu nemožný; `--source .` bere soubory z aktuálního adresáře konzole.
**Fix:** Cyklus Upravit → Ctrl+S → `gcloud deploy` (žádný krok nelze vynechat); před deployem `cat main.py`.
**Pravidlo:** P-GCP-03
**Tags:** p-gcp-03 | deploy

#### GT-GCP-004 (GCP-024): infrastructure
**Server:** gcp | **Status:** fixed

**Symptom:** Skript těží stejné inzeráty dokola; `OSError: [Errno 30] Read-only file system`.
**Root cause:** Cloud Functions: po doběhu se smaže celý FS včetně /tmp/ (RAM-mapped, efemérní); relativní cesty → zápis do read-only root FS.
**Fix:** Pattern START: download z GCS → /tmp/, WORK: zapisovat do /tmp/, END: upload do GCS. Jediná trvalá paměť = GCS Bucket.
**Pravidlo:** P-GCP-04
**Tags:** p-gcp-04

#### GT-GCP-005 (GCP-037): general
**Server:** gcp | **Status:** documented

**Symptom:** Ztráta přehledu o stavu kódu; kupí se chyby z nepozornosti; pocit bezmoci nad systémem.
**Root cause:** Pracovní paměť má limit — po ~2 h inkrementálních změn bez kontextového resetu je kognitivní zátěž nefaktorovatelná; debug session → kaskáda drobných změn → ztráta orientace.
**Fix:** see source
**Pravidlo:** P-GCP-05
**Tags:** p-gcp-05

#### GT-107 (kultura-db-001): subprocess
**Server:** kultura-db | **Status:** fixed

**Symptom:** `refresh_dashboards.ps1:20 char:30` -> `throw ("{0} exit={1}")` = jediny signal padu; zadny traceback, zadny per-run log. Beh 25.09.2026 07:42 zemrel po kroku 3, dnesni behy opakovane cervene, po restartu PC 2x zelene. Identifikace skutecne priciny trvala ~30 min mtime forenzniky misto precteni vyjimky.
**Root cause:** (1) `Invoke-PyStep` vola `& python @PyArgs` bez `2>&1` a bez zapisu do logu - python stderr/traceback runner opousti, `$LASTEXITCODE` se transformuje na hole `exit=N` -> chyba bez kontextu. (2) Okno smrti dolozeno mtime: posledni zapis v repu `data/db/kultura.db` `07:42:14.778` = commit kroku 3; kroky 6-9 nenabehly (`data/poc_export/*.csv` mtime 24.09 21:18, footer dashboardu `Pull: 2026-09-24T21:18:13`, meteo_daily.csv 108 vs 109 radku v DB) -> smrt v okne prveho zapisu kroku 4/5/6. Read-only simulace kroku 4/5/6 (monkeypatch `sqlite3.connect` -> mode=ro, guard na `open`) cista (`SIM_STEP4_OK`, `SIM_STEP5_OK`) -> kod bez vady. [hypoteza, P~=0.6] transient zamek (SQLite default busy timeout 5 s, nebo file-level handle) drzeny procesem, ktery restart PC odstranil; presna vyjimka se nezachytila. (3) Overena past pri oprave: v PS 5.1 `& prog 2>&1` pod `$ErrorActionPreference='Stop'` vyhodi `NativeCommandError` NA RADKU VOLANI - script konci exit=1 misto skutecneho `exit=7`, a to i kdyz proces skoncil `exit=0` a na stderr slo jen varovani. Nasazeni logovani bez docasneho prepnuti EAP by pridalo novy typ padu na radku 19 drive, nez pobehne vlastni `throw` na radku 20.
**Fix:** (1) `Invoke-PyStep`: docasny `$ErrorActionPreference='Continue'` uvnitr try/finally, `$code=$LASTEXITCODE` zachycen OKAMZITE po pipeline, vystup smerovan `2>&1 | ForEach-Object` zaroven do per-run logu (UTF8, live) a na konzoli, `throw` nese label + exit code + log path + tail 20 radku. (2) Hlavicka per-run logu `reports/refresh_run_<ts>.log`: cas, `$PSVersionTable.PSVersion`, `(Get-Command python).Source`, cwd, `git rev-parse --short HEAD` + preflight `Get-Command python` (fail-fast). (3) `sqlite3.connect(..., timeout=30)` na 12 call site v ceste kaskady (kroky 1-10, vc. forecast_7day:32,338 krok 7 a hsnr_params:28 krok 9 - puvodne neuplnych 9 doplneno o kroky 7/9). (4) Gate overen negativni cestou: `sys.exit(3)` -> throw s exit=3 + stderr v logu; `RuntimeError` -> traceback v logu.
**Pravidlo:** P98
**Tags:** p98 | powershell | exit-code | observability | subprocess

#### GT-108 (kultura-db-002): encoding
**Server:** kultura-db | **Status:** fixed

**Symptom:** `scripts/generate/refresh_dashboards.ps1` obsahuje ne-ASCII bajty `E2 80 94` (UTF-8 em-dash) na radku 15 v komentari, soubor je BEZ BOM. Hlavicka souboru (radky 8-9) pritom vyslovne zakazuje jakoukoli ne-ASCII stopu a popisuje presny mechanismus padu. Invariant porusen potreti.
**Root cause:** PS 5.1 cte `.ps1` bez BOM v aktualni ANSI codepage (cp1250); UTF-8 sekvence `E2 80 94` dekoduje cp1250 tak, ze bajt `0x94` = prava uvozovka -> phantom quote, ktery rozbije parsovani skriptu. Dnes je bajt v komentari (neboli), ale: (a) hlavicka dokumentuje pravidlo, ktere sam soubor porusuje; (b) regrese se vratila i po dvou opravach - pravidlo popisane v komentari bez spustitelne kontroly se porusi (8151a0f 0 ne-ASCII -> 988edfc 9 ne-ASCII -> 75fb74c 0 -> 7de30d6 3 = soucasny stav).
**Fix:** (1) Emdash na radku 15 nahrazen pomlkou - `non_ascii` v souboru 3 -> 0 (overeno poctem bajtu >127). (2) Invariant spustitelnym gate: `check_ps1_ascii()` v `scripts/verify/check_consistency.py` sekce [6] - pro kazdy `scripts/**/*.ps1` kontrola `all(b < 128)`, pri poruseni vypise offset prveho ne-ASCII bajtu a ukonci script exit 1 (bezi v uz existujicim kroku [10/10], zadny novy krok). Overeno negativnim testem (docasny .ps1 s E2 80 94 -> CHYBA + offset 17 + exit 1) i pozitivnim (1/1 ciste ASCII, exit 0). Komplement GT-080/P69 (nazvy souboru) a GT-014/P28 (emoji ve vystupu) - tato entry pokryva OBSAH .ps1.
**Pravidlo:** P99
**Tags:** p99 | encoding | ascii | powershell | invariant

