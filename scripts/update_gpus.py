import json
import re
import sys
import time
from pathlib import Path

try:
    from curl_cffi import requests as cffi_requests
    USE_CFFI = True
except ImportError:
    import requests
    USE_CFFI = False

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependencies. Run: pip install -r requirements.txt")
    sys.exit(1)

GPUS_FILE = Path("src/lib/data/gpus.json")
TPU_BASE = "https://www.techpowerup.com"
TPU_SPECS = "https://www.techpowerup.com/gpu-specs/"

MANUFACTURERS = ["NVIDIA", "AMD", "Intel"]
MIN_VRAM = 4  # GB — filters out potato-tier old cards


def session():
    if USE_CFFI:
        return cffi_requests.Session(impersonate="chrome120")
    s = requests.Session()
    s.headers["User-Agent"] = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    return s


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def load_db():
    if not GPUS_FILE.exists():
        return [], set()
    data = json.loads(GPUS_FILE.read_text(encoding="utf-8"))
    return data, {g["id"] for g in data}


def save_db(data):
    GPUS_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def scrape_list(http, manufacturer):
    """Pull the GPU listing page for one manufacturer and return parsed rows."""
    resp = http.get(TPU_SPECS, params={"mfgr": manufacturer}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    # The GPU table has class="processors" on TechPowerUp
    table = soup.find("table", {"class": "processors"})
    if not table:
        tables = soup.find_all("table")
        table = next(
            (t for t in tables if t.find("a", href=re.compile(r"/gpu-specs/\S+\.c\d+"))),
            None,
        )
    if not table:
        return []

    rows = []
    for row in table.find_all("tr")[1:]:
        link = row.find("a", href=re.compile(r"/gpu-specs/"))
        if not link:
            continue

        name = link.get_text(strip=True)
        detail_url = TPU_BASE + link["href"]

        # Try to grab VRAM from any cell in the row
        vram = None
        for cell in row.find_all("td"):
            m = re.search(r"(\d+(?:\.\d+)?)\s*(GB|MB)", cell.get_text(), re.I)
            if m:
                v = float(m.group(1))
                if "MB" in m.group(2).upper():
                    v /= 1024
                vram = v
                break

        if vram is None or vram < MIN_VRAM:
            continue

        rows.append({"name": name, "manufacturer": manufacturer, "vram_gb": vram, "url": detail_url})

    return rows


def scrape_bandwidth(http, detail_url):
    """Visit a GPU detail page and pull the memory bandwidth figure."""
    try:
        resp = http.get(detail_url, timeout=15)
        # Primary pattern: "Bandwidth" near a "xxx GB/s" value
        m = re.search(r"Bandwidth[^\d]*?([\d,.]+)\s*GB/s", resp.text, re.I | re.S)
        if m:
            return float(m.group(1).replace(",", ""))
        # Fallback: grab all "xxx GB/s" values and pick the largest sensible one
        candidates = [
            float(x.replace(",", ""))
            for x in re.findall(r"([\d,.]+)\s*GB/s", resp.text)
            if float(x.replace(",", "")) > 10
        ]
        return max(candidates) if candidates else None
    except Exception:
        return None


def main():
    http = session()
    backend = "curl_cffi (Chrome 120)" if USE_CFFI else "requests"
    print(f"Backend: {backend}\n")

    db, known_ids = load_db()
    added = 0

    for mfr in MANUFACTURERS:
        print(f"Fetching {mfr} GPUs...")
        try:
            rows = scrape_list(http, mfr)
        except Exception as e:
            print(f"  Failed to fetch {mfr} list: {e}")
            continue

        print(f"  {len(rows)} candidates found")
        for row in rows:
            gid = slug(row["name"])
            if gid in known_ids:
                continue

            print(f"  + {row['name']} ({row['vram_gb']}GB)... ", end="", flush=True)
            bw = scrape_bandwidth(http, row["url"])
            time.sleep(0.3)

            if bw is None:
                print("no bandwidth data, skipping")
                continue

            entry = {
                "id": gid,
                "name": row["name"],
                "manufacturer": mfr,
                "vram_gb": row["vram_gb"],
                "bandwidth_gbps": round(bw, 1),
            }
            db.append(entry)
            known_ids.add(gid)
            added += 1
            save_db(db)
            print(f"{bw} GB/s")

    print(f"\nTotal GPUs in DB: {len(db)}  (+{added} new)")


if __name__ == "__main__":
    main()
