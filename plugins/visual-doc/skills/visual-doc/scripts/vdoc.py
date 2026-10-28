#!/usr/bin/env python3
"""visual-doc 조립 · 점검 도구 (표준 라이브러리만 사용)

  vdoc.py build --title "제목" --body body.html --out page.html [--css extra.css]
  vdoc.py check page.html | body.html
  vdoc.py serve page.html [--port 8765]

serve 는 미리보기용 로컬 서버다. /__preview?w=390&theme=dark 가 페이지를 그 폭·테마로 iframe 에 띄운다.

build 는 body 조각(.wrap 안쪽 내용)에 base.css · 아이콘 스프라이트 · 공용 스크립트를 붙여
한 장짜리 HTML 을 만들고, 끝나면 check 를 돌린다. check 는 디자인 규칙 위반을 찾는다.
check 에 body 조각을 주면 <title> 검사를 건너뛰고 기본 아이콘 스프라이트를 있는 것으로 본다.
"""
from __future__ import annotations

import argparse
import html as htmllib
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS = SKILL_DIR / "assets"
FONTS = ("https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800"
         "&family=JetBrains+Mono:wght@400;500&display=swap")
ALLOWED_SCRIPT_HOSTS = ("https://cdnjs.cloudflare.com/", "https://cdn.jsdelivr.net/npm/", "https://unpkg.com/")
ALLOWED_STYLE_HOSTS = ("https://fonts.googleapis.com/",)

COMMON_JS = """
(function () {
  // data-copy="요소 id" 버튼: 클립보드 복사, 막히면 선택으로 대신한다
  document.querySelectorAll('button.copy[data-copy]').forEach(function (btn) {
    var label = btn.textContent;
    var reset = function () { setTimeout(function () { btn.textContent = label; }, 1600); };
    btn.addEventListener('click', function () {
      var code = document.getElementById(btn.getAttribute('data-copy'));
      if (!code) return;
      var select = function () {
        var r = document.createRange(); r.selectNodeContents(code);
        var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
        btn.textContent = '선택했어요'; reset();
      };
      try {
        navigator.clipboard.writeText(code.textContent).then(function () { btn.textContent = '복사했어요'; reset(); }, select);
      } catch (e) { select(); }
    });
  });
})();
"""


def prune_icons(sprite: str, html: str) -> str:
    used = set(re.findall(r'href="#(i-[\w-]+)"', html))
    def keep(m):
        return m.group(0) if m.group(1) in used else ""
    sprite = re.sub(r'\s*<symbol id="(i-[\w-]+)".*?</symbol>', keep, sprite, flags=re.S)
    return sprite


def build(args) -> int:
    body = Path(args.body).read_text(encoding="utf-8").strip()
    css = (ASSETS / "base.css").read_text(encoding="utf-8")
    if args.css:
        css += "\n/* ---------- 이 문서 전용 ---------- */\n" + Path(args.css).read_text(encoding="utf-8")
    sprite = prune_icons((ASSETS / "icons.svg").read_text(encoding="utf-8"), body)
    js = COMMON_JS if "data-copy=" in body else ""
    page = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{htmllib.escape(args.title, quote=False)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<style>
{css}
</style>
</head>
<body>
{sprite.strip()}

<div class="wrap">
{body}
</div>
{"<script>" + js + "</script>" if js else ""}
</body>
</html>
"""
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print(f"built {out} ({len(page.encode('utf-8')):,} bytes)")
    return check_file(out, base_css=(ASSETS / "base.css").read_text(encoding="utf-8"))


class Scan(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr", "use", "path",
            "circle", "rect", "ellipse"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # (tag, classes)
        self.bentos = []         # 각 .bento 의 직계 tile 폭 목록
        self.lists = []          # (.flow/.roadmap, --n, li 수)
        self.sections = []       # (classes, has_h2, has_eyebrow, 첫 컴포넌트)
        self.title = None
        self._in_title = False
        self.scripts, self.styles, self.icon_refs, self.icon_ids = [], [], set(), set()
        self.inline_styles = []
        self.bare_tables = 0
        self.blocks = []         # 최상위 블록 순서: "hero" / "sec" / "start"
        self.stages = []         # 각 .stage 안에 .ex 가 있는지

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get("class") or "").split()
        if a.get("style"):
            self.inline_styles.append(a["style"])
        if tag == "title":
            self._in_title = True
        if tag == "script" and a.get("src"):
            self.scripts.append(a["src"])
        if tag == "link" and a.get("rel") == "stylesheet":
            self.styles.append(a.get("href", ""))
        if tag == "use" and (a.get("href") or "").startswith("#"):
            self.icon_refs.add(a["href"][1:])
        if tag == "symbol" and a.get("id"):
            self.icon_ids.add(a["id"])
        parent = self.stack[-1] if self.stack else None
        if parent and "bento" in parent[1] and "tile" in cls:
            w = next((int(c[1:]) for c in cls if re.fullmatch(r"w[2346]", c)), None)
            self.bentos[-1].append(w)
        if parent and parent[0] in ("ol", "ul") and ({"flow", "roadmap"} & set(parent[1])) and tag == "li":
            self.lists[-1][2] += 1
        if tag == "table" and not (parent and "tbl-wrap" in parent[1]):
            self.bare_tables += 1
        if "bento" in cls:
            self.bentos.append([])
        if {"flow", "roadmap"} & set(cls):
            m = re.search(r"--n:\s*(\d+)", a.get("style") or "")
            self.lists.append([("flow" if "flow" in cls else "roadmap"), int(m.group(1)) if m else 4, 0])
        if tag == "header" and "hero" in cls:
            self.blocks.append("hero")
        if tag == "section":
            self.blocks.append("start" if "start" in cls else "sec")
            self.sections.append({"cls": cls, "h2": False, "eyebrow": False, "comp": None})
        if parent and parent[0] == "section" and self.sections[-1]["comp"] is None:
            self.sections[-1]["comp"] = next((c for c in cls if c in COMPONENTS), None)
        if "stage" in cls:
            self.stages.append(False)
        elif "ex" in cls and any("stage" in c for _, c in self.stack):
            self.stages[-1] = True
        if self.sections and self._inside("section"):
            if tag == "h2":
                self.sections[-1]["h2"] = True
            if "eyebrow" in cls:
                self.sections[-1]["eyebrow"] = True
        if tag not in self.VOID:
            self.stack.append((tag, cls))

    def _inside(self, tag):
        return any(t == tag for t, _ in self.stack)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag in self.VOID:
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if self._in_title:
            self.title = (self.title or "") + data


# 섹션의 주 컴포넌트 (섹션 직계 자식의 클래스로 판별)
COMPONENTS = {"flow", "bento", "stats", "callout", "layers", "pipe", "tbl-wrap", "api", "term", "compare",
              "decs", "scope", "roadmap", "checks", "faq"}

# 색 값을 직접 쓴 흔적. 선택자(#id)는 보지 않도록 선언 값에만 적용한다
RAW_COLOR = re.compile(
    r"#[0-9a-fA-F]{3,8}\b"
    r"|\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch|color)\("
    r"|\b(?:white|black|red|green|blue|gray|grey|yellow|orange|purple|pink|brown|navy|teal|silver"
    r"|maroon|olive|lime|aqua|cyan|magenta|fuchsia|gold|indigo|violet)\b", re.I)


def raw_colors_in_decls(decls: str) -> list[str]:
    """`prop: value; …` 문자열에서 값 쪽의 직접 색만 찾는다 (사용자 정의 속성 --x 는 토큰 정의라 제외)."""
    hits = []
    for decl in re.sub(r'"[^"]*"|\'[^\']*\'', "", decls).split(";"):
        prop, sep, value = decl.partition(":")
        if sep and not prop.strip().startswith("--"):
            hits += [m.group(0) for m in RAW_COLOR.finditer(value)]
    return hits


def dark_token_drift(css: str) -> bool:
    """base.css 의 다크 토큰 두 벌(prefers-color-scheme · data-theme=dark)이 서로 다른지."""
    media = re.search(r'@media \(prefers-color-scheme: dark\)\s*\{\s*:root:not\(\[data-theme="light"\]\)\s*\{([^}]*)\}', css)
    attr = re.search(r':root\[data-theme="dark"\]\s*\{([^}]*)\}', css)
    if not (media and attr):
        return False
    norm = lambda body: sorted(d.strip() for d in body.split(";") if d.strip())
    return norm(media.group(1)) != norm(attr.group(1))


def check_file(path: Path, base_css: str | None = None) -> int:
    html = Path(path).read_text(encoding="utf-8")
    is_page = re.search(r"<html[\s>]", html, flags=re.I) is not None
    s = Scan()
    s.feed(html)
    errors, warns = [], []

    if not is_page:
        # body 조각: build 가 붙일 기본 스프라이트를 있는 것으로 본다
        s.icon_ids |= set(re.findall(r'<symbol id="(i-[\w-]+)"', (ASSETS / "icons.svg").read_text(encoding="utf-8")))
    elif not s.title or not s.title.strip():
        errors.append("<title> 이 없어요")
    elif len(s.title.split()) > 4:
        warns.append(f"<title> 은 2~4 단어 이름으로 써요: '{s.title.strip()}'")

    if "start" not in s.blocks:
        errors.append("마지막에 .start 블록(다음 행동)이 없어요")
    elif s.blocks[-1] != "start":
        errors.append(".start 블록은 맨 마지막에 둬요")
    body_secs = s.blocks.count("sec")
    if s.blocks and not 2 <= body_secs <= 8:
        warns.append(f"본문 섹션이 {body_secs} 개예요 (히어로와 start 사이 2~8개)")
    comps = [sec["comp"] for sec in s.sections if "start" not in sec["cls"]]
    for i in range(len(comps) - 2):
        if comps[i] and comps[i] == comps[i + 1] == comps[i + 2]:
            warns.append(f"같은 컴포넌트(.{comps[i]})가 섹션 3개 연속이에요 — 모양이 다른 컴포넌트를 섞어요")
            break
    if not all(s.stages):
        errors.append('화면 모형(.stage)에 <span class="ex">예시 화면이에요</span> 가 없어요')

    for i, widths in enumerate(s.bentos, 1):
        if None in widths:
            errors.append(f"bento #{i}: 폭 클래스(w2/w3/w4/w6)가 없는 tile 이 있어요")
            continue
        acc, rows = 0, []
        for w in widths:
            acc += w
            if acc > 6:
                errors.append(f"bento #{i}: 한 줄 합이 6 을 넘어요 {widths}")
                break
            if acc == 6:
                rows.append(acc)
                acc = 0
        else:
            if acc:
                errors.append(f"bento #{i}: 마지막 줄 합이 {acc} 예요 (6 이 되게) {widths}")

    for kind, n, count in s.lists:
        if count and count != n:
            errors.append(f".{kind}: 항목 {count} 개인데 --n 이 {n} 이에요 (style=\"--n:{count}\")")

    for sec in s.sections:
        if "start" in sec["cls"]:
            continue
        if not sec["h2"]:
            warns.append(f"section({' '.join(sec['cls']) or '-'}) 에 h2 가 없어요")
        elif not sec["eyebrow"]:
            warns.append(f"section({' '.join(sec['cls']) or '-'}) 에 eyebrow 가 없어요")

    for src in s.scripts:
        if not src.startswith(ALLOWED_SCRIPT_HOSTS):
            errors.append(f"허용되지 않은 외부 스크립트: {src}")
        elif not re.search(r"@\d+\.\d+\.\d+", src):
            errors.append(f"외부 스크립트는 정확한 버전을 적어요: {src}")
    for href in s.styles:
        if not href.startswith(ALLOWED_STYLE_HOSTS):
            errors.append(f"허용되지 않은 외부 스타일시트: {href}")

    missing = s.icon_refs - s.icon_ids
    if missing:
        errors.append(f"스프라이트에 없는 아이콘: {sorted(missing)}")

    raw_colors = [st for st in s.inline_styles if raw_colors_in_decls(st)]
    if raw_colors:
        errors.append(f"인라인 style 에 색 값을 직접 썼어요 (토큰을 써요): {raw_colors[:3]}")
    if base_css is not None:
        styles = re.findall(r"<style>(.*?)</style>", html, flags=re.S)
        extra = "".join(styles).replace(base_css, "")
        extra = re.sub(r"/\*.*?\*/", "", extra, flags=re.S)
        extra = re.sub(r":root\s*\{[^}]*\}", "", extra)
        hits = [h for block in re.findall(r"\{([^{}]*)\}", extra) for h in raw_colors_in_decls(block)]
        if hits:
            errors.append(f"전용 CSS 에 색 값을 직접 썼어요 (토큰을 써요): {hits[:5]}")
        if dark_token_drift(base_css):
            errors.append("base.css 의 다크 토큰 두 벌(prefers-color-scheme · data-theme=dark)이 서로 달라요")

    if s.bare_tables:
        warns.append("표는 .tbl-wrap 으로 감싸야 좁은 화면에서 가로 스크롤이 표 안에서만 생겨요")

    for e in errors:
        print(f"ERROR  {e}")
    for w in warns:
        print(f"WARN   {w}")
    print(f"check: {len(errors)} error, {len(warns)} warn")
    return 1 if errors else 0


PREVIEW = """<!doctype html><html><head><meta charset="utf-8"><title>preview</title>
<style>html,body{margin:0;background:#888}iframe{display:block;margin:0 auto;border:0;background:#fff}</style></head>
<body><iframe id="f"></iframe><script>
var q = new URLSearchParams(location.search), f = document.getElementById('f');
f.style.width = (q.get('w') || '390') + 'px';
f.onload = function () {
  var d = f.contentDocument;
  if (q.get('theme')) d.documentElement.setAttribute('data-theme', q.get('theme'));
  var fit = function () { f.style.height = d.documentElement.scrollHeight + 'px'; };
  fit(); setTimeout(fit, 300); setTimeout(fit, 1200);
  window.__overflow = d.documentElement.scrollWidth > d.documentElement.clientWidth;
};
f.src = '/' + (q.get('src') || '__PAGE__');
</script></body></html>"""


def serve(args) -> int:
    import functools
    import http.server
    page = Path(args.file).resolve()
    html = PREVIEW.replace("__PAGE__", page.name).encode("utf-8")

    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path.startswith("/__preview"):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(html)))
                self.end_headers()
                self.wfile.write(html)
                return
            super().do_GET()

        def log_message(self, *a):
            pass

    handler = functools.partial(Handler, directory=str(page.parent))
    with http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler) as httpd:
        base = f"http://127.0.0.1:{args.port}"
        print(f"page     {base}/{page.name}", flush=True)
        print(f"preview  {base}/__preview?w=390            (모바일 · 라이트)", flush=True)
        print(f"preview  {base}/__preview?w=390&theme=dark (모바일 · 다크)", flush=True)
        print(f"preview  {base}/__preview?w=1280&theme=dark (데스크톱 · 다크)", flush=True)
        httpd.serve_forever()
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--title", required=True)
    b.add_argument("--body", required=True)
    b.add_argument("--out", required=True)
    b.add_argument("--css")
    c = sub.add_parser("check")
    c.add_argument("file")
    v = sub.add_parser("serve")
    v.add_argument("file")
    v.add_argument("--port", type=int, default=8765)
    args = p.parse_args()
    if args.cmd == "build":
        return build(args)
    if args.cmd == "serve":
        return serve(args)
    base = (ASSETS / "base.css").read_text(encoding="utf-8")
    return check_file(Path(args.file), base_css=base)


if __name__ == "__main__":
    sys.exit(main())
