# probes — 실측 탐침

설계서와 MODEL 의 수치는 전부 여기서 나왔다. **추측이 아니라 잰 값**이고,
새 가정을 세울 때 같은 방식으로 재 보라고 남겨 둔다.

```bash
# 레포 루트에서. .env 가 있어야 한다
PYTHONIOENCODING=utf-8 python probes/probe_seed2.py
```

| 스크립트 | 무엇을 쟀나 | 결론 |
|---|---|---|
| `probe_nest.py` | 상위어가 하위 조합어를 품는가 | **완전일치.** 포함 관계 아님 (53/53 주 위반) |
| `probe_shop.py` | 쇼핑인사이트 단독 재확인 + 수식어 순서 + 띄어쓰기 | 자식합 > 부모 53/53 · **순서를 가린다**(41.2 vs 1.2) · 띄어쓰기는 무시 |
| `probe_miss.py` | 규모 밴드별 관측률·바닥률·고유값비 | 월 140 도 관측률 0.93. **진짜 제약은 계단화**(고유값비 0.45) |
| `probe_solo.py` | 힌트를 묶으면 응답이 잘리는가 | **잘린다.** 스커트 15(묶음) → 165(단독) |
| `probe_seed2.py` | 시드 후보 36개 평가 | 결과는 `seed_eval.csv` · `seed_children.json` |

> `probe_nest.py` 와 `probe_seed.py`(옛 묶음 버전)의 수치는 **묶음 조회 왜곡이 섞여 있다.**
> 단독 조회로 다시 잰 `probe_solo.py` · `probe_seed2.py` 쪽이 맞다.
