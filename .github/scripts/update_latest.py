"""Rewrite the latest-updates block in README.md from the site's RSS feed."""
import email.utils
import pathlib
import re
import urllib.request
import xml.etree.ElementTree as ET

FEED = "https://shiningforu.com/rss.xml"
COUNT = 5

req = urllib.request.Request(FEED, headers={"User-Agent": "profile-readme"})
with urllib.request.urlopen(req, timeout=30) as resp:
    root = ET.fromstring(resp.read())

items = root.findall("./channel/item")[:COUNT]
if not items:
    raise SystemExit("feed has no items")

lines = []
for item in items:
    day = email.utils.parsedate_to_datetime(item.findtext("pubDate")).date().isoformat()
    title = item.findtext("title").replace("[", "\\[").replace("]", "\\]")
    lines.append(f"- {day} [{title}]({item.findtext('link')})")

path = pathlib.Path("README.md")
text = path.read_text(encoding="utf-8")
block = "<!-- latest:start -->\n" + "\n".join(lines) + "\n<!-- latest:end -->"
new, n = re.subn(r"<!-- latest:start -->.*?<!-- latest:end -->", lambda _: block, text, flags=re.S)
if n != 1:
    raise SystemExit("markers not found")
path.write_text(new, encoding="utf-8")
