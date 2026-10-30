# 구성과 컴포넌트

모든 클래스는 `assets/base.css` 에 있다. 완성 예는 `examples/intro.body.html`(소개형) · `examples/design.body.html`(설계형).
아이콘은 `<svg class="i"><use href="#i-이름"/></svg>` (작게 `class="i sm"`). 쓸 수 있는 이름:
`up check shield spark search chat term gauge history bell book db server cloud layers plug code file gear link clock cal chart target flag users lock info alert bulb swap right down box rocket`
없는 아이콘은 body 맨 위에 `<svg width="0" height="0" style="position:absolute" aria-hidden="true"><symbol id="i-x" viewBox="0 0 24 24">…</symbol></svg>` 로 더한다 (24 격자, 선만, fill 없음).

## 문서 유형별 구성

본문 섹션(히어로와 start 사이)은 2~8개. 아래 순서는 출발점이다 — 원문에 없는 섹션은 빼고, 빈 섹션을 채우려고 내용을 만들지 않는다.
리듬: 넓은 면(벤토·비교) → 가는 선(흐름·표) → 숫자(스탯)처럼 모양이 다른 컴포넌트를 번갈아 둔다.

### 유형 판별

| 원문이 주로 말하는 것 | 유형 |
|---|---|
| 무엇인지, 무엇을 할 수 있는지, 어떻게 쓰는지 | 소개 |
| 왜 하는지, 무엇을 할지, 범위·일정·성공 기준 | 기획 |
| 어떻게 만드는지, 구조·데이터·API·결정 | 설계 |
| 무엇을 했고 결과가 어땠는지, 다음엔 무엇을 할지 | 보고 |
| 따라 하는 순서, 명령, 설정 | 가이드 |

섞여 있으면 독자가 문서를 다 읽고 해야 할 일로 고른다 (쓰기 시작 → 소개/가이드, 승인 → 기획, 구현·리뷰 → 설계, 판단 → 보고).

### 섹션 순서

**소개** (`examples/intro.body.html`)
히어로(제품 화면 모형 + float) → 흐름(쓰는 순서 4단계) → 기능 벤토(타일마다 `.demo`) → [숫자/FAQ] → start(접속 주소·연결 명령)

**기획**
히어로(문제 한 줄 + 목표 숫자 모형, `.meta-row`) → 배경(`.stats` + `.callout warn`) → 목표·범위(`.scope` + 성공 기준 `.stats`/`.checks`) → 사용자 흐름(`.flow`) → 기능 벤토 → 일정(`.roadmap`) → 위험·결정 필요(`.decs`) → start(승인·결정 요청)

**설계** (`examples/design.body.html`)
히어로(요약 + 현황/구조 모형, `.meta-row` + `nav.toc`) → 배경(`.stats` + `.callout`) → 구조(`.layers`/`.pipe`) → 처리 흐름(`.flow`) → 데이터(`.tbl`) → API(`.api` + `pre.term`) → 결정(`.compare` + `.decs`) → 일정(`.roadmap`) → [FAQ] → start(리뷰 요청·결정 필요 항목)

**보고**
히어로(`hero solo` 또는 결과 숫자 모형) → [조사·방법(`.tbl` / `.scope` / `.flow`)] → 결과(`.stats`, 목표 대비 `.bar`) → 한 일(`.roadmap` done 또는 `.hist`) → 잘된 점·문제(`.compare` 2열 또는 `.callout ok/bad`) → 원인·조치(`.decs`) → start(다음 액션)

**가이드**
히어로(완성 화면 또는 터미널 모형) → 준비물(`.checks`) → 단계(`.flow`) → 단계별 상세(벤토 w6 타일마다 `pre.term`) → 문제 해결(`.faq`) → start(복사 가능한 명령)

섹션마다 컴포넌트는 아래 [섹션 컴포넌트](#섹션-컴포넌트) 표의 "쓰는 내용" 열로 고른다. 화면이 있는 기능은 히어로 `.stage` 나 타일 `.demo` 로 보여 준다.

### 히어로 모형 고르기

독자가 처음 3초에 "이게 뭔지" 알게 하는 장면 하나를 만든다. 실제 화면이 있으면 그 화면을 줄여서(`.search`·`.result`·`.fact`·`.steps`), 없으면 핵심 숫자(`.stats` 2칸) + 상태 목록(`.fact` + pill)으로.
값은 원문에서 가져오고 `예시 화면이에요` 를 단다. 모형으로 보여 줄 게 정말 없으면 `hero solo`.

## 뼈대

```html
<header class="hero">                       <!-- 오른쪽 모형이 없으면 class="hero solo" -->
  <div class="hero-text">
    <span class="badge-line rise"><i></i>문서 성격 · 버전</span>
    <h1 class="rise d1">첫 줄<br><em>핵심 구절</em> 마무리</h1>
    <p class="lead rise d2">두세 문장 요약</p>
    <div class="hero-tags rise d3"><span class="tag">키워드</span>…</div>       <!-- 또는 .meta-row / nav.toc -->
  </div>
  <div class="stage rise d2" aria-label="…"> <div class="mock"><div class="mock-bar"><i></i><i></i><i></i></div><div class="mock-body">…</div></div>
    <div class="float">…</div>                <!-- 선택: 겹쳐 뜨는 카드 -->
    <span class="ex">예시 화면이에요</span></div>
</header>

<section class="sec" aria-labelledby="x-t">   <!-- 흐름(.flow)이 있으면 class="sec wide" -->
  <div class="sec-head"><span class="eyebrow">한 단어</span><h2 id="x-t">말하는 제목</h2><p>선택: 한 문장</p></div>
  …컴포넌트…
</section>

<section class="start" aria-labelledby="go-t"> <!-- 마지막 블록, 파란 면 -->
  <div><h2 id="go-t">행동을 권하는 제목</h2><p class="sub">한두 문장</p></div>
  <div class="start-list">
    <div class="s-item"><span class="k">라벨</span><span class="v">주소·값(mono)</span></div>        <!-- 글이면 .t -->
    <div class="s-item"><span class="k">라벨</span><div class="cmd"><code id="c1">명령</code><button class="copy" type="button" data-copy="c1">복사</button></div></div>
  </div>
</section>
```

`.meta-row`: `<div class="meta-row"><span>작성 <b>팀</b></span><span>상태 <b>리뷰 중</b></span></div>`
`nav.toc`: `<nav class="toc" aria-label="목차"><a href="#arch-t">구조</a>…</nav>` — 섹션 6개 이상일 때.

## 섹션 컴포넌트

| 컴포넌트 | 쓰는 내용 | 마크업 요점 |
|---|---|---|
| `.flow` | 3~5단계 순서·절차·파이프라인 (6단계 이상이면 묶거나 `.roadmap`) | `<ol class="flow" style="--n:4"><li><div class="node">아이콘</div><span class="n">01</span><b>단계</b><span class="d">설명</span></li>` 마지막 노드는 자동으로 채워진다 |
| `.bento` + `.tile` | 기능·특징 4~8개 | 6열. `tile w2/w3/w4/w6`, **한 줄 합 6** (3+3, 4+2, 2+4, 2+2+2, 6). 타일 = `.t-ic` + `h3` + `p.d` + 선택 `.demo` |
| `.stats` > `.stat` | KPI·규모·현황 숫자 2~4개 | `<div class="stat"><span class="k">라벨</span><span class="v">99.5<small>%</small></span><span class="s">보조</span></div>` 강조 하나만 `.stat.hl`, 증감 `.delta.up/.down`, 진척 `<div class="bar" style="--p:62%"><i></i></div>` |
| `.callout` | 문제·주의·핵심 결론 한 개 | `<div class="callout warn"><svg class="i"><use href="#i-alert"/></svg><div><b>제목</b><p>설명</p></div></div>` 종류: 기본(파랑 info) `ok` `warn` `bad` |
| `.layers` | 계층 구조·시스템 구성 | `.layer` = `<span class="k">이름<small>영문</small></span><div class="boxes"><span class="box">…</span></div>`, 사이에 `<div class="layer-arrow"><svg class="i"><use href="#i-down"/></svg></div>`. 바뀌는 부분 `.box.hl`, 새로 만드는 것 `.box.new` |
| `.pipe` | 짧은 가로 데이터 흐름 (A→B→C) | `<div class="pipe"><span class="box">A<small>설명</small></span><span class="to"><svg class="i"><use href="#i-right"/></svg></span>…</div>` |
| `.tbl-wrap` > `table.tbl` | 데이터 모델·필드·비교 수치·권한 매트릭스 | 코드값 칸 `td.mono`, 숫자 칸 `td.num`. 반드시 `.tbl-wrap` 으로 감싼다 |
| `.api` | 엔드포인트 목록 | `<div class="api-row"><span class="mth get">GET</span><code>/path</code><span class="d">설명</span></div>` 메서드: `get post put patch delete` |
| `pre.term` | 명령·요청 예시·로그·설정 | `<span class="p">강조</span>` `<span class="c">주석</span>`, 줄바꿈은 그대로 |
| `.compare` > `.opt` | 대안 비교 2~3개 | 채택안 `.opt.pick` + `pill blue`. 장단점 `<ul class="pc"><li class="pro">…</li><li class="con">…</li><li class="neu">…</li></ul>` |
| `.decs` > `.dec` | 결정 기록·이슈·결함 목록 | `<div class="dec"><span class="id">D-01</span><div><b>결정</b><p>이유</p></div><span class="pill ok">확정</span></div>` 미결은 `pill warn` `결정 필요`. id 는 원문 ID 그대로, 없으면 `01`·`02` 순번 (접두어를 지어내지 않는다) |
| `.decs.compact` + `.dec-h` | 7개 이상 긴 목록을 묶음별로 | `<div class="decs compact"><div class="dec-h">VMware <small>5</small></div><div class="dec">…</div>…</div>` 행은 `<b>` 한 줄, `<p>` 생략 가능 |
| `.scope` | 포함·제외 범위 | `<div class="scope"><div class="in"><span class="k">이번에 해요</span><ul>…</ul></div><div class="out"><span class="k">이번엔 안 해요</span><ul>…</ul></div></div>` |
| `.roadmap` | 일정·마일스톤·단계별 계획 | `<ol class="roadmap" style="--n:4"><li class="done|now"><span class="when">W1 · 10/06</span><b>단계</b><ul><li>…</li></ul></li>` |
| `.checks` | 준비물·완료 조건·체크리스트 | `<ul class="checks"><li class="on"><span><b>항목</b> 설명</span></li>` 완료는 `.on` |
| `.faq` | 예상 질문·Q&A·주의사항 | `<details open><summary>질문</summary><div>답</div></details>` |

## 타일 안 `.demo` 조각 (기능을 "보여 주기")

| 조각 | 보여 주는 것 |
|---|---|
| `.drop` + `.exts` | 업로드·입력 형식 |
| `.steps` > `.step` (`now` `todo`) | 진행 상태·승인 단계 |
| `.variants` + `.arrow-row` | 여러 입력이 하나로 모임 (정규화·매핑) |
| `.bubble.me` / `.bubble.ai` | 대화·질의응답 |
| `.term` | CLI·연동 사용 예 |
| `.ranks` > `.rank` + `pill` | 순위·품질·상태 목록 |
| `.hist` > `.h-row` | 변경 이력·감사 로그 |
| `.notice` | 알림 카드 (아바타 + 제목 + 버튼) |
| `.roles` + `pill` | 역할·권한·라벨 묶음 |
| `.search` + `.result` + `.fact` | 검색·조회 결과, 사실 + 메타(mono) |

배지: `pill blue`(분류·강조) `pill grey`(중립 상태·태그 — `기록만`, `보류`, `참고`) `pill ok`(완료·성공) `pill warn`(주의·결정 필요) `pill bad`(실패·위험). 상태색은 독자가 행동해야 하는 정도로 고른다.

어디서나 쓰는 유틸: `.mono`(ID·커밋·버전·시각), `.muted`(보조 글자색), `.ex`(예시 표시).

## 전용 CSS 가 필요할 때

컴포넌트로 안 되는 배치만 `extra.css` 로 더한다. 규칙: 토큰(`var(--…)`)만, 클래스 이름은 섹션 접두어(`.risk-…`), 640px 이하 규칙을 같이 쓴다.
복잡한 다이어그램은 인라인 SVG 로 그리고 선·글자색은 `currentColor` 를 쓰거나 CSS(`style="stroke:var(--accent)"`, 클래스)로 토큰을 준다 — `stroke="var(…)"` 같은 속성값에는 토큰이 먹지 않는다.
