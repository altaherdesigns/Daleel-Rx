import os
import re
import hashlib
import random
import datetime
import pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
POSTS_DIR = REPO / "_posts"
IMG_DIR = REPO / "assets" / "img" / "posts"

NAVY = "#0b3b6f"
CYAN = "#17A2C4"


def set_output(name, value):
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a") as f:
            f.write(f"{name}={value}\n")


def slugify(title):
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s[:60]


def generate_header_svg(slug, width=1200, height=630):
    """Same deterministic on-brand generator used throughout the site."""
    seed = int(hashlib.md5(slug.encode()).hexdigest(), 16)
    rng = random.Random(seed)
    circles = []
    for _ in range(rng.randint(4, 7)):
        cx, cy = rng.uniform(0.1, 0.9) * width, rng.uniform(0.1, 0.9) * height
        r = rng.uniform(60, 220)
        color = NAVY if rng.random() < 0.6 else CYAN
        opacity = rng.uniform(0.08, 0.22)
        circles.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}" fill="{color}" fill-opacity="{opacity:.2f}"/>')
    needle = (f'<g transform="translate({width-90},{height-90})">'
              f'<circle r="34" fill="none" stroke="{NAVY}" stroke-width="2"/>'
              f'<path d="M0 -22 L7 0 L0 22 L-7 0 Z" fill="{CYAN}"/></g>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">'
           f'<rect width="{width}" height="{height}" fill="#ffffff"/>{"".join(circles)}{needle}</svg>')
    out_path = IMG_DIR / f"{slug}.svg"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(svg)


def main():
    body = os.environ.get("ISSUE_BODY", "")
    if not body.strip():
        raise SystemExit("Issue body is empty — nothing to publish.")

    m = re.search(r'^title:\s*"?(.+?)"?\s*$', body, re.MULTILINE)
    if not m:
        raise SystemExit('No `title:` line found in the pasted front matter — check the content.')
    title = m.group(1)
    slug = slugify(title)

    # Insert an image: line right after title: if the pasted content doesn't have one
    if not re.search(r'^image:', body, re.MULTILINE):
        body = re.sub(
            r'(^title:.*$)',
            rf'\1\nimage: "/assets/img/posts/{slug}.svg"',
            body, count=1, flags=re.MULTILINE,
        )

    generate_header_svg(slug)

    today = datetime.date.today().isoformat()
    (POSTS_DIR / f"{today}-{slug}.md").write_text(body.strip() + "\n")

    set_output("title", title.replace('"', "'"))
    set_output("slug", slug)


if __name__ == "__main__":
    main()
