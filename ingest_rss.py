# ingest_rss.py
import feedparser
import yaml
import time
from datetime import datetime, timezone, timedelta
from db import init_db, insert_item

def load_config():
    with open("config.yaml") as f:
        return yaml.safe_load(f)

def normalize(entry, source_name):
    return {
        "id": entry.get("id") or entry.link,
        "source": source_name,
        "title": entry.title,
        "url": entry.link,
        "published": entry.get("published", datetime.utcnow().isoformat()),
        "content": entry.get("summary", "")[:2000]
    }

def main():
    cfg = load_config()
    print(f"[{cfg['project_name']}] Starting RSS ingestion…")
    conn = init_db()

    # calculate cutoff
    max_age = timedelta(days=cfg.get("max_age_days", 1))
    now = datetime.now(timezone.utc)

    total_fetched = 0
    total_skipped = 0

    for feed_url in cfg["rss_feeds"]:
        feed = feedparser.parse(feed_url)
        fetched = 0
        skipped = 0

        for entry in feed.entries:
            # parse published date
            pub_struct = entry.get("published_parsed")
            if not pub_struct:
                skipped += 1
                continue
            pub_dt = datetime.fromtimestamp(time.mktime(pub_struct), tz=timezone.utc)

            # skip if too old
            if now - pub_dt > max_age:
                skipped += 1
                continue

            item = normalize(entry, source_name="rss")
            insert_item(conn, item)
            fetched += 1

        print(f"[✔] {feed_url}: ingested {fetched}, skipped {skipped} old items")
        total_fetched += fetched
        total_skipped += skipped

    print(f"[{cfg['project_name']}] Done: {total_fetched} new rows, {total_skipped} skipped.")

if __name__ == "__main__":
    main()
