# 시각 확인

`vdoc.py check` 는 구조 규칙만 본다. 겹침·잘림·다크 모드 대비는 실제로 띄워 봐야 안다.

## 1. 미리보기 서버

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/vdoc.py" serve page.html --port 8765     # 백그라운드로 실행
```

- `http://127.0.0.1:8765/page.html` — 페이지 그대로
- `http://127.0.0.1:8765/__preview?w=390&theme=dark` — 폭·테마를 고정한 iframe (`w`, `theme=light|dark`)
  로드 뒤 `window.__overflow` 가 `true` 면 그 폭에서 가로 스크롤이 생긴 것이다.

## 2. 브라우저로 보기

**Aside 가 있으면** (`aside --version` 이 되면) `aside repl` 또는 MCP `mcp__aside__repl` 로 본다. `file://` 는 막혀 있으니 반드시 서버 주소를 쓴다.

```js
const vd = await openTab('http://127.0.0.1:8765/__preview?w=390&theme=dark');
await sleep(1500);
console.log(await vd.evaluate(() => ({ overflow: window.__overflow, h: document.documentElement.scrollHeight })));
const vh = await vd.evaluate(() => innerHeight), total = await vd.evaluate(() => document.documentElement.scrollHeight);
for (let y = 0; y < total; y += vh) {
  await vd.evaluate(v => scrollTo(0, v), y); await sleep(150);
  display(await vd.screenshot({ type: 'jpeg', quality: 45 }));
}
```

- `fullPage: true` 와 `clip` 은 Aside 에서 제대로 찍히지 않는다 → 위처럼 스크롤하며 뷰포트를 찍는다.
- 데스크톱은 `/__preview?w=1280` (라이트), 모바일은 `w=390&theme=dark` 두 벌이면 충분하다.

**다른 브라우저 도구**(Playwright MCP, Chrome DevTools MCP 등)가 있으면 같은 주소로 같은 두 벌을 본다. 아무 도구도 없으면 보고에 "시각 확인 못 함"을 적는다.

## 3. 볼 것

- 히어로: 모형이 글보다 높게 튀지 않는지, `float` 가 모형 글자를 가리지 않는지
- 흐름: 연결선이 첫·끝 노드 중앙에서 끝나는지 (`--n` 확인)
- 벤토: 줄마다 높이가 크게 어긋나지 않는지 — 어긋나면 설명 길이를 맞추거나 폭을 바꾼다
- 390px: 가로 스크롤 없음, 배지·버튼 줄바꿈 깨짐 없음, 표는 표 안에서만 스크롤
- 다크: 흰 배경 잔재(직접 쓴 색), 읽히지 않는 회색 글자 없음

확인이 끝나면 서버를 끈다.
