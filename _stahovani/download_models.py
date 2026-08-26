"""
Stahovani pre-trained modelu pro retrieval pipeline.
Spustit: python -X utf8 _stahovani\download_models.py

Zdroje:
- fasttext: https://dl.fbaipublicfiles.com/fasttext/vectors-wiki/wiki.en.vec
- fasttext CS: https://dl.fbaipublicfiles.com/fasttext/vectors-wiki/wiki.cs.vec
"""

import os
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# KONFIGURACE
# ============================================================

DOWNLOADS = {
    "wiki.en.vec": {
        "url": "https://dl.fbaipublicfiles.com/fasttext/vectors-wiki/wiki.en.vec",
        "size_mb": 680,
        "description": "FastText English Wikipedia vectors (300d)",
    },
    "wiki.cs.vec": {
        "url": "https://dl.fbaipublicfiles.com/fasttext/vectors-wiki/wiki.cs.vec",
        "size_mb": 700,
        "description": "FastText Czech Wikipedia vectors (300d)",
    },
}


def download_file(url, dest_path, description=""):
    """Stahne soubor s progress reportem."""
    print("Stahuji: %s" % description)
    print("  URL: %s" % url)
    print("  Cil: %s" % dest_path)

    if os.path.exists(dest_path):
        size_mb = os.path.getsize(dest_path) / (1024 * 1024)
        print("  Preskoceno (jiz existuje, %.1f MB)" % size_mb)
        return True

    t0 = time.time()
    last_update = t0

    def progress(block_num, block_size, total_size):
        nonlocal last_update
        now = time.time()
        if now - last_update < 1.0:  # Update kazdou sekundu
            return
        last_update = now
        downloaded = block_num * block_size
        if total_size > 0:
            pct = downloaded / total_size * 100
            speed = downloaded / (now - t0) / 1024 / 1024
            print(
                "  %.1f%% (%.1f MB / %.1f MB) - %.1f MB/s"
                % (pct, downloaded / 1024 / 1024, total_size / 1024 / 1024, speed)
            )

    try:
        urllib.request.urlretrieve(url, dest_path, reporthook=progress)
        elapsed = time.time() - t0
        size_mb = os.path.getsize(dest_path) / (1024 * 1024)
        print(
            "  Hotovo: %.1f MB za %.1f s (%.1f MB/s)"
            % (size_mb, elapsed, size_mb / elapsed)
        )
        return True
    except Exception as e:
        print("  CHYBA: %s" % e)
        return False


def main():
    print("=" * 60)
    print("STAHOVANI MODELU PRO RETRIEVAL PIPELINE")
    print("=" * 60)
    print()

    # Stahnout requirements
    print("Krok 1: Instalace Python balicku")
    print("-" * 40)
    req_path = os.path.join(BASE, "requirements.txt")
    if os.path.exists(req_path):
        ret = os.system("pip install -r %s" % req_path)
        if ret == 0:
            print("  Balicky nainstalovany.")
        else:
            print("  VAROVANI: Nektere balicky se nepodarilo nainstalovat.")
    print()

    # Stahnout fasttext
    print("Krok 2: Stahovani fasttext modelu")
    print("-" * 40)
    for filename, info in DOWNLOADS.items():
        dest = os.path.join(BASE, "fasttext", filename)
        download_file(info["url"], dest, info["description"])
        print()

    print("=" * 60)
    print("HOTOVO")
    print("=" * 60)
    print()
    print("Stazene soubory:")
    fasttext_dir = os.path.join(BASE, "fasttext")
    if os.path.exists(fasttext_dir):
        for f in os.listdir(fasttext_dir):
            path = os.path.join(fasttext_dir, f)
            size_mb = os.path.getsize(path) / (1024 * 1024)
            print("  %s (%.1f MB)" % (f, size_mb))


if __name__ == "__main__":
    main()
