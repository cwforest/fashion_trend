# 수기 관찰 기록

`observations.csv`에 **매주 같은 요일**에 추가한다. 행을 덮어쓰지 말고 계속 아래에 쌓을 것.

## 컬럼
| 컬럼 | 값 | 비고 |
|---|---|---|
| `observed_at` | YYYY-MM-DD | 관찰한 날 |
| `source` | ably / zigzag / musinsa / sinsang / instagram / tiktok | |
| `rank` | 정수 또는 공란 | 랭킹이 있는 소스만 |
| `item` ~ `style` | `config/taxonomy.yaml`의 값 | 모르면 **비워둘 것** |
| `price_krw` | 정수 | 소매가. 신상마켓은 도매가 |
| `note` | 자유 | "여러 도매에서 동시 출현" 같은 메모가 제일 값지다 |

## 규칙
- **빈칸이 오답보다 낫다.** 애매하면 비워라
- 분류 값은 taxonomy에 없으면 새로 써도 된다. 나중에 taxonomy에 흡수한다
- 주 1회를 거르더라도 형식은 지킬 것. 형식이 깨지면 데이터가 아니라 메모가 된다
