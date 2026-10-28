"""PPT 8장 삽입용 도식 — 조기 탐지 + 세 칸짜리 주간 순위표."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

installed = {f.name for f in font_manager.fontManager.ttflist}
for name in ("Malgun Gothic", "NanumGothic", "AppleGothic", "Gulim"):
    if name in installed:
        matplotlib.rcParams["font.family"] = name
        break
matplotlib.rcParams["axes.unicode_minus"] = False

NAVY = "#00305C"
BLUE = "#1F6FB2"
SKY = "#EAF4FB"
PAPER = "#F5F7FA"
GRAY = "#8A949E"
INK = "#1A1A1A"
LINE = "#C9D6E3"
RED = "#9B3B3B"
GOLD = "#8A5E10"

fig = plt.figure(figsize=(14.8, 5.0), dpi=200)
fig.patch.set_facecolor("white")

# ─────────────────────────── 왼쪽: 트렌드 곡선 ───────────────────────────
ax = fig.add_axes([0.042, 0.14, 0.455, 0.74])
ax.set_facecolor("white")

x = np.linspace(0, 100, 400)
y = 100 * np.exp(-((x - 66) ** 2) / (2 * 17.0 ** 2))

DETECT, KNOWN = 34, 64

ax.fill_between(x, 0, y, where=(x >= DETECT) & (x <= KNOWN), color=SKY, zorder=1)
ax.plot(x, y, color=BLUE, lw=2.6, zorder=3, solid_capstyle="round")

for xp, col in ((DETECT, NAVY), (KNOWN, GRAY)):
    yp = float(np.interp(xp, x, y))
    ax.plot([xp, xp], [0, yp], color=col, lw=1.1, ls=(0, (4, 3)), zorder=2)
    ax.add_patch(Circle((xp, yp), 1.6, facecolor="white", edgecolor=col,
                        lw=2.0, zorder=5, clip_on=False))

ax.annotate("조기 탐지 시점", xy=(DETECT, float(np.interp(DETECT, x, y))),
            xytext=(DETECT - 23, 82), fontsize=12.5, color=NAVY, weight="bold",
            va="bottom",
            arrowprops=dict(arrowstyle="-", color=NAVY, lw=1.1,
                            connectionstyle="angle3,angleA=0,angleB=70"))
ax.text(DETECT - 23, 76, "아직 작지만\n빠르게 가속 중", fontsize=10.5,
        color=INK, va="top", linespacing=1.6)

ax.annotate("일반적으로 알게 되는 시점", xy=(KNOWN, float(np.interp(KNOWN, x, y))),
            xytext=(KNOWN + 6, 118), fontsize=11.5, color=GRAY, va="bottom",
            arrowprops=dict(arrowstyle="-", color=GRAY, lw=1.1,
                            connectionstyle="angle3,angleA=0,angleB=80"))
ax.text(KNOWN + 6, 112, "이미 늦음 — 입고되면 꺾인다", fontsize=10.2,
        color=GRAY, va="top")

mid = (DETECT + KNOWN) / 2
ax.annotate("", xy=(DETECT, 17), xytext=(KNOWN, 17),
            arrowprops=dict(arrowstyle="<->", color=NAVY, lw=1.4))
ax.text(mid, 24, "사입 적기", ha="center", va="bottom", fontsize=12,
        color=NAVY, weight="bold")
ax.text(mid, 11, "사입 → 촬영·등록 → 초기 반응  2~6주", ha="center", va="top",
        fontsize=10, color=NAVY)

ax.set_xlim(-2, 102)
ax.set_ylim(0, 132)
ax.set_xticks([])
ax.set_yticks([])
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
ax.spines["left"].set_color(LINE)
ax.spines["bottom"].set_color(LINE)
ax.set_xlabel("시간", fontsize=10.5, color=GRAY, labelpad=6)
ax.set_ylabel("관심도", fontsize=10.5, color=GRAY, labelpad=16,
              rotation=0, ha="right", va="center")
ax.set_title("① 유행의 조짐을 먼저 잡는다", fontsize=14.5, color=NAVY,
             weight="bold", loc="left", pad=14)

# ─────────────────────────── 오른쪽: 세 칸 순위표 ───────────────────────────
bx = fig.add_axes([0.555, 0.14, 0.43, 0.74])
bx.set_xlim(0, 10)
bx.set_ylim(0, 10)
bx.axis("off")
bx.set_title("② 매주 한 장 — 세 칸으로 전달", fontsize=14.5, color=NAVY,
             weight="bold", loc="left", pad=14)


def block(y0, h, title, note, rows, accent, fill):
    bx.add_patch(FancyBboxPatch((0.1, y0), 9.8, h,
                                boxstyle="round,pad=0.02,rounding_size=0.25",
                                facecolor=fill, edgecolor=LINE, lw=0.9))
    bx.text(0.6, y0 + h - 0.42, title, fontsize=11.5, color=accent,
            weight="bold", va="center")
    bx.text(2.5, y0 + h - 0.42, note, fontsize=9.3, color=GRAY, va="center")
    ry = y0 + h - 1.05
    for name, val in rows:
        bx.text(0.75, ry, name, fontsize=10.6, color=INK, va="center")
        bx.text(9.4, ry, val, fontsize=10.6, color=accent, weight="bold",
                ha="right", va="center")
        ry -= 0.62


block(6.95, 2.75, "주력", "늘 떼오는 품목 — 작년 같은 주 대비",
      [("가디건", "94%"), ("청바지", "108%"), ("무지 니트", "87%")],
      NAVY, PAPER)

block(2.95, 3.75, "뜨는 것", "작지만 빨라지는 것",
      [("버건디 니트 가디건", "▲ 42%"), ("스웨이드 크롭 자켓", "▲ 31%"),
       ("벌룬 스커트", "▲ 24%"), ("코듀로이 와이드팬츠", "▲ 18%")],
      BLUE, SKY)

block(0.15, 2.5, "꺾이는 것", "컸는데 식는 것 — 재고 경보",
      [("체크 코트", "▼ 27%"), ("플리스 집업", "▼ 19%")],
      RED, "#FBF2F2")

fig.patches.append(FancyArrowPatch((0.513, 0.50), (0.547, 0.50),
                                   transform=fig.transFigure,
                                   arrowstyle="-|>", mutation_scale=22,
                                   color=NAVY, lw=2.0))

OUT = (r"C:\Users\lim\Desktop\claude_project\fashion_trend\docs"
       r"\조기탐지_순위표_도식.png")
fig.savefig(OUT, dpi=200, facecolor="white", bbox_inches="tight", pad_inches=0.22)
print("saved:", OUT)
