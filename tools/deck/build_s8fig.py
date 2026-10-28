# 8장 도식 교체 — 순위표를 세 칸 구조로 다시 그린 그림
from PIL import Image

FIG = ("C:/Users/lim/Desktop/claude_project/fashion_trend/docs/"
       "조기탐지_순위표_도식.png")
_s8 = S[7]
for _sh in list(_s8.shapes):
    if _sh.shape_type == 13:
        _x, _y, _w, _h = _sh.left, _sh.top, _sh.width, _sh.height
        drop(_sh)
        _iw, _ih = Image.open(FIG).size
        _nh = int(_w * _ih / _iw)
        _s8.shapes.add_picture(FIG, _x, _y + (_h - _nh) // 2, _w, _nh)
        break
