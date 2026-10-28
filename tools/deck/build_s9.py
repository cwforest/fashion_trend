# ═══════════════ 9. 프로젝트 개관 — 매주 도는 순서 ═══════════════
s = S[8]
drop_pics(s)
_, t = tb(s, L, TOP, W, 0.9)
line(t, "매주 같은 순서로 돕니다. 사람이 들여다보는 건 마지막 한 장뿐입니다",
     32, NAVY, True, first=True)

# ── 1단계: 후보를 모으는 두 갈래 ──
ay, ah = TOP + 1.35, 2.3
iw = W / 2 - 0.45
ins = [
    ("품목 26개를 네이버에 넣는다", "같이 검색된 말이 딸려 온다",
     "가디건 → 니트 가디건 · 버건디 가디건", BLUE),
    ("패션 기사와 커뮤니티를 훑는다", "처음 보는 말을 주워 온다",
     "작년엔 없던 이름이 올해 생긴다", GOLD),
]
for i, (head, sub, ex, col) in enumerate(ins):
    x = L + i * (iw + 0.9)
    card(s, x, ay, iw, ah, fill=PAPER)
    _, c = tb(s, x + 0.9, ay + 0.45, iw - 1.8, ah - 0.9)
    line(c, head, 24, NAVY, True, first=True)
    line(c, sub, 21, col, True, space_before=8)
    line(c, ex, 18, GRAY, space_before=7)
    down_arrow(s, x + iw / 2 - 0.28, ay + ah + 0.15, 0.56, 0.55)

# ── 2단계: 후보 목록 ──
by, bh = ay + ah + 0.85, 1.2
card(s, L, by, W, bh, fill=TINT, border=None)
_, c = tb(s, L, by, W, bh, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
mixed(c, [("이번 주 지켜볼 후보  ", NAVY, True),
          ("수백 개", BLUE, True)], 26, align=PP_ALIGN.CENTER)

down_arrow(s, L + W / 2 - 0.28, by + bh + 0.15, 0.56, 0.55)

# ── 3단계: 걸러내는 세 단계 ──
cy, ch = by + bh + 0.8, 2.1
cw = (W - 2 * 0.6) / 3
steps = [
    ("매주 추이를 본다", "얼마나 검색되고 눌리는지를 주 단위로 쌓는다"),
    ("오르는 속도를 본다", "지금 큰 것이 아니라 빨라지고 있는 것을 고른다"),
    ("계절을 걷어낸다", "겨울이라 코트가 오르는 건 유행이 아니다"),
]
for i, (head, body) in enumerate(steps):
    x = L + i * (cw + 0.6)
    card(s, x, cy, cw, ch, fill=PAPER)
    chip(s, x + 0.8, cy + 0.5, 0.8, str(i + 1), size=22)
    _, c = tb(s, x + 1.9, cy + 0.52, cw - 2.7, 0.7)
    line(c, head, 23, NAVY, True, first=True)
    _, c = tb(s, x + 0.8, cy + 1.45, cw - 1.6, 0.9)
    line(c, body, 19, GRAY, first=True, spacing=1.4)

# ── 4단계: 결과 ──
ry = cy + ch + 0.45
_, c = tb(s, L, ry, W, 0.6)
mixed(c, [("월요일 아침, 한 장.  ", NAVY, True),
          ("세 칸으로 나눠 드립니다.", GRAY, False)], 24)

by2, bh2 = ry + 0.72, 1.72
card(s, L, by2, W, bh2, fill=NAVY, border=None)
outs = [("주력", "늘 떼오는 품목 — 작년 같은 주 대비 지금 수요"),
        ("뜨는 것", "작지만 빨라지는 것 — 떼올 만한 후보 10개"),
        ("꺾이는 것", "컸는데 식는 것 — 재고 경보")]
ow = W / 3
for i, (head, body) in enumerate(outs):
    x = L + i * ow
    if i:
        sp = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, I(x), I(by2 + 0.35),
                                Pt(1), I(bh2 - 0.7))
        sp.fill.solid()
        sp.fill.fore_color.rgb = C(0x1C, 0x4C, 0x82)
        sp.line.fill.background()
        sp.shadow.inherit = False
    _, c = tb(s, x + 0.8, by2, ow - 1.2, bh2, anchor=MSO_ANCHOR.MIDDLE)
    line(c, head, 22, SKY, True, first=True)
    line(c, body, 17, WHITE, space_before=8, spacing=1.35)
