
# ═══════════════ 10. 시드 — 지켜볼 기본 품목 ═══════════════
s = S[9]
drop_pics(s)
set_title(s, "① 지켜볼 기본 품목", width=18)
_, t = tb(s, L, TOP, W, 0.9)
line(t, "여기서 모든 추천 후보가 나옵니다. 이 목록이 맞는지 봐 주세요",
     32, NAVY, True, first=True)

NEW = {"조끼", "나시", "바지", "스커트", "팬츠", "반바지", "집업", "점퍼"}
groups = [
    ("상의", ["가디건", "니트", "조끼", "블라우스", "셔츠",
              "티셔츠", "맨투맨", "후드티", "나시"]),
    ("하의", ["바지", "스커트", "팬츠", "청바지",
              "반바지", "슬랙스", "레깅스"]),
    ("아우터", ["패딩", "코트", "자켓", "바람막이",
                "집업", "점퍼", "무스탕"]),
    ("원피스", ["원피스"]),
]
cw = (W - 3 * 0.55) / 4
cy, ch = TOP + 1.35, 6.9
for i, (head, items) in enumerate(groups):
    x = L + i * (cw + 0.55)
    card(s, x, cy, cw, ch, fill=PAPER)
    _, c = tb(s, x + 0.8, cy + 0.6, cw - 1.6, 0.7)
    mixed(c, [(head + "  ", NAVY, True), (str(len(items)) + "개", GRAY, False)], 25)
    rule(s, x + 0.8, cy + 1.5, cw - 1.6)
    _, c = tb(s, x + 0.8, cy + 1.85, cw - 1.6, ch - 2.4)
    for j, it in enumerate(items):
        line(c, it, 21, BLUE if it in NEW else INK, it in NEW,
             space_before=0 if j == 0 else 9, first=(j == 0), spacing=1.3)

# 관찰 전용 + 질문을 한 상자에
ay = cy + ch + 0.45
card(s, L, ay, W, 2.2, fill=C(0xFB, 0xF4, 0xE8), border=C(0xE8, 0xD4, 0xA8))
_, c = tb(s, L + 0.9, ay + 0.35, W - 1.8, 1.5)
mixed(c, [("관찰 전용 7개   ", NAVY, True),
          ("트렌치코트 · 롱스커트 · 와이드팬츠 · 미니스커트 · 카고팬츠 · 블레이저 · 점프수트"
           "   — 상위 품목이 품으므로 따로 찾지 않습니다", GRAY, False)], 18)
line(c, "안 떼오시는 품목이 섞여 있나요? 꼭 봐야 하는데 빠진 품목이 있나요?",
     21, INK, space_before=14, spacing=1.4)
line(c, "파란 글씨 8개는 저희가 새로 넣은 것입니다. "
        "조끼/베스트 · 바지/팬츠처럼 말이 둘인 건 어느 쪽을 쓰시나요?",
     19, C(0x8A, 0x5E, 0x10), space_before=6, spacing=1.4)

# ═══════════════ 11. 시드에 말을 붙여 후보를 만든다 ═══════════════
s = S[10]
drop_pics(s)
set_title(s, "② 후보는 이렇게 만듭니다", width=18)
_, t = tb(s, L, TOP, W, 0.9)
line(t, "조합을 저희가 지어내지 않습니다. 사람들이 실제로 검색한 말만 씁니다",
     32, NAVY, True, first=True)

by = TOP + 1.45
bh = 7.4

# ① 시드
w1 = 4.6
card(s, L, by, w1, bh, fill=TINT, border=None)
_, c = tb(s, L + 0.6, by + 0.7, w1 - 1.2, 1.2)
line(c, "① 시드 하나", 20, BLUE, True, first=True)
_, c = tb(s, L, by + 2.9, w1, 1.2, align=PP_ALIGN.CENTER)
line(c, "가디건", 40, NAVY, True, first=True, align=PP_ALIGN.CENTER)
_, c = tb(s, L + 0.6, by + 5.2, w1 - 1.2, 1.4)
line(c, "26개 중 하나를", 19, GRAY, first=True, spacing=1.4)
line(c, "네이버에 넣습니다", 19, GRAY, spacing=1.4)

arrow(s, L + w1 + 0.35, by + bh / 2 - 0.3, 0.8, 0.6)

# ② 연관검색어
x2, w2 = L + w1 + 1.5, 9.4
card(s, x2, by, w2, bh, fill=PAPER)
_, c = tb(s, x2 + 0.7, by + 0.7, w2 - 1.4, 1.2)
line(c, "② 같이 검색되는 말이 딸려 옵니다", 20, BLUE, True, first=True)
line(c, "네이버 검색광고가 월간 검색수와 함께 알려줍니다", 17, GRAY,
     space_before=6)
rows = [("니트 가디건", "8,200", True),
        ("크롭 가디건", "3,400", True),
        ("버건디 가디건", "1,100", True),
        ("숄 가디건", "260", False),
        ("가디건 코디", "22,000", False),
        ("가디건 도매", "1,900", False)]
ry = by + 2.3
for name, vol, keep in rows:
    col = INK if keep else C(0xB0, 0xB6, 0xBE)
    _, c = tb(s, x2 + 0.9, ry, 4.6, 0.45)
    line(c, name, 20, col, keep, first=True)
    _, c = tb(s, x2 + 5.6, ry, 1.9, 0.45, align=PP_ALIGN.RIGHT)
    line(c, vol, 20, col, False, first=True, align=PP_ALIGN.RIGHT)
    _, c = tb(s, x2 + 7.7, ry, 1.5, 0.45)
    line(c, "채택" if keep else "제외", 17, BLUE if keep else C(0xB0, 0xB6, 0xBE),
         True, first=True)
    ry += 0.6

_, c = tb(s, x2 + 0.7, by + bh - 1.3, w2 - 1.4, 0.9)
line(c, "월 100~1만 건만 남깁니다. 너무 크면 이미 다 아는 말이고,",
     17, GRAY, first=True, spacing=1.35)
line(c, "너무 작으면 숫자가 흔들려 추세를 볼 수 없습니다.", 17, GRAY, spacing=1.35)

arrow(s, x2 + w2 + 0.35, by + bh / 2 - 0.3, 0.8, 0.6)

# ③ 추이 추적
x3 = x2 + w2 + 1.5
w3 = R - x3
card(s, x3, by, w3, bh, fill=TINT, border=None)
_, c = tb(s, x3 + 0.7, by + 0.7, w3 - 1.4, 1.2)
line(c, "③ 매주 추이를 봅니다", 20, BLUE, True, first=True)
picks = [("니트 가디건", "▲ 꾸준히 상승", BLUE),
         ("버건디 가디건", "▲ 최근 급가속", BLUE),
         ("크롭 가디건", "— 변화 없음", GRAY)]
py = by + 2.6
for name, note, col in picks:
    _, c = tb(s, x3 + 0.9, py, w3 - 1.8, 1.1)
    line(c, name, 21, NAVY, True, first=True)
    line(c, note, 19, col, True, space_before=5)
    py += 1.35

banner(s, by + bh + 0.6, 1.4,
       [("시드 26개가 후보 수백 개로 늘어납니다.  ", WHITE, True),
        ("그중 오르는 것과 꺾이는 것을 매주 추려 드립니다.", SKY, False)], size=23)

# ═══════════════ 12. 속성 축 ═══════════════
s = S[11]
drop_pics(s)
set_title(s, "③ 옷을 설명하는 11가지 기준", width=18)
_, t = tb(s, L, TOP, W, 0.9)
line(t, "'버건디 니트 가디건'을 색·소재·품목으로 쪼개야 무엇이 뜨는지 보입니다",
     32, NAVY, True, first=True)

axes = [
    ("아이템", "가디건 · 자켓 · 스커트"),
    ("실루엣", "오버사이즈 · A라인 · 벌룬"),
    ("핏", "크롭 · 루즈 · 레귤러"),
    ("기장", "미니 · 미디 · 롱"),
    ("색상", "버건디 · 올리브 · 파스텔"),
    ("소재", "니트 · 코듀로이 · 트위드"),
    ("패턴", "체크 · 스트라이프 · 플로럴"),
    ("디테일", "퍼 · 퀼팅 · 시스루 · 러플"),
    ("무드", "Y2K · 고프코어 · 올드머니"),
    ("상황", "데일리 · 출근 · 하객 · 여행"),
    ("시대", "90년대 · 2000년대 · 70년대"),
]
gx = (W - 3 * 0.5) / 4
gh = 1.72
ty = TOP + 1.4
for i, (name, ex) in enumerate(axes):
    r_, c_ = divmod(i, 4)
    x = L + c_ * (gx + 0.5)
    y = ty + r_ * (gh + 0.45)
    card(s, x, y, gx, gh, fill=PAPER)
    _, c = tb(s, x + 0.6, y + 0.35, gx - 1.2, gh - 0.7)
    line(c, name, 22, NAVY, True, first=True)
    line(c, ex, 18, GRAY, space_before=8)

ay = ty + 3 * (gh + 0.45) + 0.45
card(s, L, ay, W, 2.5, fill=C(0xFB, 0xF4, 0xE8), border=C(0xE8, 0xD4, 0xA8))
_, c = tb(s, L + 0.9, ay, W - 1.8, 2.5, anchor=MSO_ANCHOR.MIDDLE)
mixed(c, [("여쭙고 싶은 것", C(0x8A, 0x5E, 0x10), True)], 24)
line(c, "실제로 떼오실 때 보시는 기준 중에, 이 11개로 설명이 안 되는 게 있나요?",
     21, INK, space_before=12, spacing=1.4)
line(c, "저희끼리는 '계절'과 '가격대'를 더 넣을지 고민 중입니다. "
        "반대로 안 쓰실 것 같은 축이 있으면 빼겠습니다.",
     19, GRAY, space_before=6, spacing=1.4)

# ═══════════════ 13. 필요한 데이터 ═══════════════
s = S[12]
drop_pics(s)
set_title(s, "④ 부탁드릴 데이터", width=18)
_, t = tb(s, L, TOP, W, 0.9)
line(t, "없어도 추천은 나갑니다. 다만 '몇 개를 떼올지'는 이게 있어야 답할 수 있습니다",
     32, NAVY, True, first=True)

dy, dh = TOP + 1.4, 6.9
hw = W / 2 - 0.35

# 왼쪽 — 판매자센터
card(s, L, dy, hw, dh, fill=PAPER)
_, c = tb(s, L + 0.9, dy + 0.7, hw - 1.8, 1.2)
mixed(c, [("① 에이블리 판매자센터", NAVY, True)], 25)
line(c, "통계 메뉴에 엑셀 다운로드 버튼이 있는지부터 봐 주세요", 18, GRAY,
     space_before=8)
rule(s, L + 0.9, dy + 2.3, hw - 1.8)
items = [("상품별 주간 판매수량", "꼭"), ("상품별 조회수", "꼭"),
         ("옵션명 (색상 · 사이즈)", "꼭"), ("찜 수", "되면"),
         ("상품명 · 등록일 · 가격", "되면"),
         ("몇 개월치까지 보이는지", "확인만")]
iy = dy + 2.75
for name, tag in items:
    _, c = tb(s, L + 0.9, iy, hw - 3.6, 0.5)
    line(c, "·  " + name, 21, INK, first=True)
    _, c = tb(s, L + hw - 2.6, iy, 1.7, 0.5, align=PP_ALIGN.RIGHT)
    line(c, tag, 18, BLUE if tag == "꼭" else GRAY, tag == "꼭",
         first=True, align=PP_ALIGN.RIGHT)
    iy += 0.68

# 오른쪽 — 기억
x2 = L + hw + 0.7
card(s, x2, dy, hw, dh, fill=TINT, border=None)
_, c = tb(s, x2 + 0.9, dy + 0.7, hw - 1.8, 1.2)
mixed(c, [("② 기억으로 알려주실 것", NAVY, True)], 25)
line(c, "다운로드가 안 되더라도 이것만으로 검증이 됩니다", 18, GRAY,
     space_before=8)
rule(s, x2 + 0.9, dy + 2.3, hw - 1.8)
_, c = tb(s, x2 + 0.9, dy + 2.75, hw - 1.8, dh - 3.4)
line(c, "최근 1년 크게 터진 상품 5~10개", 22, NAVY, True, first=True)
line(c, "품목 · 색상 · 떼온 시점 · 왜 샀는지", 19, GRAY, space_before=7)
line(c, "거의 안 팔린 상품 5~10개", 22, NAVY, True, space_before=22)
line(c, "품목 · 색상 · 떼온 시점 · 왜 안 됐다고 보시는지", 19, GRAY,
     space_before=7)
line(c, "'그때 우리 시스템이 이걸 미리 잡았을까'를 맞춰 보는 유일한 답지입니다.",
     19, INK, space_before=26, spacing=1.4)

wy = dy + dh + 0.7
card(s, L, wy, W, 2.0, fill=C(0xFB, 0xF4, 0xE8), border=C(0xE8, 0xD4, 0xA8))
_, c = tb(s, L + 0.9, wy, W - 1.8, 2.0, anchor=MSO_ANCHOR.MIDDLE)
mixed(c, [("색상은 꼭 따로 적어 주세요", C(0x8A, 0x5E, 0x10), True)], 23)
line(c, "상품명에 '(3color)'로만 적혀 있으면, 버건디가 떴는지 저희 쪽에서 "
        "확인할 방법이 없습니다. 색상은 트렌드의 절반입니다.",
     20, INK, space_before=10, spacing=1.4)

prs.save("out.pptx")
print("saved out.pptx")
