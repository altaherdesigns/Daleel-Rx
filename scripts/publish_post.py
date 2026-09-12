import os
import re
import json
import hashlib
import random
import datetime
import pathlib
import anthropic

try:
    import requests
except ImportError:
    requests = None

REPO = pathlib.Path(__file__).resolve().parent.parent
BACKLOG = REPO / "docs" / "blog-topics.md"
POSTS_DIR = REPO / "_posts"
IMG_DIR = REPO / "assets" / "img" / "posts"

NAVY = "#0b3b6f"
CYAN = "#17A2C4"

BANNED_PATTERNS = [
    r"\bCME\b", r"\bsponsor(ed|ship)?\b", r"\bcredits? earned\b",
    r"\bguarantee[sd]?\b", r"\bcure[sd]?\b", r"\btrusted by\b",
    r"\bsafe (in|during) pregnancy\b", r"\bcontraindicated\b",
    r"\d+\s?mg\b", r"\bAED\s?\d", r"\bfree trial\b",
]


def set_output(name, value):
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a") as f:
            f.write(f"{name}={value}\n")


def next_topic(lines=None):
    lines = lines if lines is not None else BACKLOG.read_text().splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"- \[ \] (?!REVIEW:)(.+)", line)
        if m:
            return i, m.group(1).strip(), lines
    return None, None, lines


def mark_done(lines, idx, topic):
    today = datetime.date.today().isoformat()
    lines[idx] = f"- [x] {topic} — {today}"
    BACKLOG.write_text("\n".join(lines) + "\n")


def count_open(lines):
    return sum(1 for l in lines if re.match(r"- \[ \] (?!REVIEW:)", l))


def replenish_backlog(client, lines):
    prompt = """List 5 new blog topics for a UAE pharmacy reference site, aimed at UAE
pharmacists. Each must be answerable with general or regulatory information only — none
may require asserting a safety verdict about a specific drug or molecule. Respond with
ONLY a JSON array of 5 short topic strings, nothing else."""
    resp = client.messages.create(
        model="claude-sonnet-5", max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text").strip()
    text = re.sub(r"^```(json)?|```$", "", text, flags=re.MULTILINE).strip()
    topics = json.loads(text)
    lines = lines + [f"- [ ] {t}" for t in topics]
    BACKLOG.write_text("\n".join(lines) + "\n")
    return lines


def slugify(title):
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s[:60]


def safety_check(title, body, sources):
    text = f"{title}\n{body}"
    for pat in BANNED_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return False, f"Blocked phrase pattern matched: {pat}"
    if not sources:
        return False, "No sources returned"
    if requests:
        for s in sources:
            try:
                r = requests.head(s["url"], timeout=8, allow_redirects=True)
                if r.status_code >= 400:
                    return False, f"Source URL returned {r.status_code}: {s['url']}"
            except Exception as e:
                return False, f"Source URL unreachable: {s['url']} ({e})"
    return True, ""


def generate_header_svg(slug, out_path, width=1200, height=630):
    """Deterministic on-brand abstract header — same slug always regenerates the same image."""
    seed = int(hashlib.md5(slug.encode()).hexdigest(), 16)
    rng = random.Random(seed)
    circles = []
    for _ in range(rng.randint(4, 7)):
        cx, cy = rng.uniform(0.1, 0.9) * width, rng.uniform(0.1, 0.9) * height
        r = rng.uniform(60, 220)
        color = NAVY if rng.random() < 0.6 else CYAN
        opacity = rng.uniform(0.08, 0.22)
        circles.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}" fill="{color}" fill-opacity="{opacity:.2f}"/>')
    needle = (
        f'<g transform="translate({width-90},{height-90})">'
        f'<circle r="34" fill="none" stroke="{NAVY}" stroke-width="2"/>'
        f'<path d="M0 -22 L7 0 L0 22 L-7 0 Z" fill="{CYAN}"/></g>'
    )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">'
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>{"".join(circles)}{needle}</svg>'
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(svg)
    return f"/assets/img/posts/{out_path.name}", None


def fetch_unsplash_image(slug):
    """Optional: real stock photography. Only runs if UNSPLASH_ACCESS_KEY is set."""
    key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not key or not requests:
        return None
    try:
        r = requests.get(
            "https://api.unsplash.com/photos/random",
            params={"query": "pharmacy medicine healthcare", "orientation": "landscape"},
            headers={"Authorization": f"Client-ID {key}"},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        img_resp = requests.get(data["urls"]["regular"], timeout=15)
        img_resp.raise_for_status()

        out_path = IMG_DIR / f"{slug}.jpg"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(img_resp.content)

        # Unsplash API guideline: ping this whenever a photo is actually used
        requests.get(data["links"]["download_location"], headers={"Authorization": f"Client-ID {key}"}, timeout=10)

        credit = (
            f'Photo by <a href="{data["user"]["links"]["html"]}">{data["user"]["name"]}</a>'
            f' on <a href="https://unsplash.com">Unsplash</a>'
        )
        return f"/assets/img/posts/{slug}.jpg", credit
    except Exception:
        return None


PROMPT_TEMPLATE = """You are drafting one blog post for daleelrx.com, a personal,
non-commercial UAE pharmacy reference project run by a licensed pharmacist. Audience:
UAE pharmacists and pharmacy professionals.

Rules, non-negotiable:
- Never state or imply a safety verdict about a specific drug or molecule (e.g. "safe in
  pregnancy", "contraindicated with X"). If the topic edges toward that, write around it.
- Every factual or regulatory claim must come from a source you actually find via web
  search in this session. Never invent a URL, law number, or statistic.
- No CME, sponsorship, pricing, or "trusted by" language.
- UAE business English, active voice, no filler, 450-600 words.

Topic: {topic}

Respond with ONLY a JSON object, no other text, in exactly this shape:
{{"title": "...", "body_markdown": "...", "sources": [{{"name": "...", "url": "..."}}]}}
body_markdown is plain Markdown using ## for subheadings, no YAML front matter inside it.
"""


def main():
    client = anthropic.Anthropic()
    idx, topic, lines = next_topic()

    if count_open(lines) <= 2:
        lines = replenish_backlog(client, lines)
        if topic is None:
            idx, topic, lines = next_topic(lines)

    if topic is None:
        set_output("published", "false")
        set_output("reason", "No topics available even after replenishing the backlog.")
        return

    resp = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=3000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": PROMPT_TEMPLATE.format(topic=topic)}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text").strip()
    text = re.sub(r"^```(json)?|```$", "", text, flags=re.MULTILINE).strip()
    data = json.loads(text)
    title, body, sources = data["title"], data["body_markdown"].strip(), data.get("sources", [])

    ok, reason = safety_check(title, body, sources)
    if not ok:
        set_output("published", "false")
        set_output("reason", f"Draft for '{title}' failed the safety check: {reason}")
        return  # backlog item stays unchecked — picked up again next run once you fix it

    slug = slugify(title)
    result = fetch_unsplash_image(slug) or generate_header_svg(slug, IMG_DIR / f"{slug}.svg")
    image_path, credit = result

    front = ["---", f'title: "{title}"', f'image: "{image_path}"']
    if credit:
        front.append(f'image_credit: \'{credit}\'')
    if sources:
        front.append("sources:")
        for s in sources:
            front.append(f'  - name: "{s["name"]}"')
            front.append(f'    url: "{s["url"]}"')
    front.append("---")

    today = datetime.date.today().isoformat()
    (POSTS_DIR / f"{today}-{slug}.md").write_text("\n".join(front) + "\n\n" + body + "\n")

    mark_done(lines, idx, topic)
    set_output("published", "true")
    set_output("title", title.replace('"', "'"))


if __name__ == "__main__":
    main()
