# 🎮 League of Legends 개인 매치 데이터 분석

## 핵심 결과와 해석

- 원본 500경기 중 3분 미만 9경기를 제외해 491경기를 분석했습니다. 승률은 51.32%입니다.
- 요일과 승패의 카이제곱 검정 p-value는 약 0.449로, 관계를 뒷받침하는 충분한 증거를 얻지 못했습니다. 효과가 없음을 증명한 결과는 아닙니다.
- TOP Jax는 26경기 17승(65.4%)이며 95% Wilson 구간은 약 46.2~80.6%로 넓습니다. 확정적인 최적 픽으로 해석하지 않습니다.
- 내 픽·정글 399개 조합 중 10경기 기준을 충족한 조합이 없어 추천을 보류했습니다.
- 한 계정의 반복 경기이며 독립성·일정 승률 가정은 근사입니다. 패치, 숙련도, 상대 실력을 통제하지 않았습니다.

## 재현

```bash
python -m pip install -r requirements.txt
```

저장된 CSV로 `notebooks/`의 두 노트북을 처음부터 실행합니다. API 키는 저장된 데이터 분석에 필요하지 않습니다.
새 수집에만 로컬 `.env`의 `RIOT_API_KEY`가 필요하며 저장소에 키를 커밋하지 않습니다.

## 분석 노트북

| 노트북 | 분석 내용 |
|---|---|
| [01_gameplay_analysis.ipynb](notebooks/01_gameplay_analysis.ipynb) | 플레이 지표와 승패의 관계: KDA·CS·골드, 데스·게임 길이·요일별 승률 |
| [02_champion_matchup_analysis.ipynb](notebooks/02_champion_matchup_analysis.ipynb) | 챔피언 선택과 조합: 내 픽, 상대 챔피언, 아군 정글 조합별 승률 |

두 노트북은 동일한 솔로랭크 데이터에 중복·핵심 정보 검증, 3분 미만 경기 제외, 한국 시간 변환을 적용합니다. 주요 챔피언 비교는 10경기 이상을 기준으로 합니다. 3분 미만 제외는 정확한 다시하기 판별이 아닌 대리 기준입니다.

Riot Games API를 활용하여 개인 League of Legends 매치 데이터를 수집하고,  
플레이 지표와 승패 간의 관계를 분석한 데이터 분석 프로젝트입니다.

단순히 승률을 확인하는 것을 넘어,

> **"어떤 플레이 특성이 승리와 관련되어 있으며, 실제 플레이 개선에 활용할 수 있는가?"**

를 중심으로 분석을 진행했습니다.

---

## 1. 프로젝트 개요

League of Legends를 플레이하면서 단순히 KDA나 승률만 확인하는 것이 아니라,  
실제 게임 데이터를 활용하여 나의 플레이 패턴과 승패 요인을 분석하고자 프로젝트를 진행했습니다.

Riot Games API를 통해 개인 매치 데이터를 직접 수집하고  
Python을 활용하여 데이터 전처리, 탐색적 데이터 분석(EDA), 시각화 및 통계 검정을 수행했습니다.

### 주요 분석 질문

- 승리 경기와 패배 경기의 플레이 지표에는 어떤 차이가 있는가?
- KDA, 데스, 골드, CS 등의 지표는 승패와 어떤 관계가 있는가?
- 챔피언별 승률 차이가 존재하는가?
- 포지션별 승률 차이가 존재하는가?
- 데스 횟수에 따라 승률이 어떻게 달라지는가?
- 게임 시간에 따라 승률이 달라지는가?
- 요일별 승률 차이가 실제로 의미 있는 차이인가?

---

## 2. 데이터 수집

### 데이터 출처

[Riot Games API](https://developer.riotgames.com/)

사용한 API

- Account-V1 API
- Match-V5 API

Riot ID를 이용해 PUUID를 조회한 후  
Match-V5 API를 통해 개인의 최근 매치 데이터를 수집했습니다.

### 데이터 수집 과정

```text
Riot ID
   ↓
PUUID 조회
   ↓
Match ID 조회
   ↓
각 Match 상세 데이터 조회
   ↓
본인 Participant 데이터 추출
   ↓
CSV 저장
```

## 3. 데이터셋 구성

Riot Games Match-V5 API를 통해 수집한 데이터를 가공하여  
`data/processed/my_lol_games.csv` 파일로 저장했습니다.

데이터는 **1개의 행(Row)이 1개의 게임**을 의미하며,  
각 열(Column)은 해당 경기에서의 개인 플레이 정보로 구성되어 있습니다.

### CSV 구조

| 컬럼명 | 설명 | 예시 |
|---|---|---|
| `match_id` | Riot Match ID | KR_XXXXXXXXXX |
| `game_date` | 게임 시작 일시 | 2026-09-09 15:34:02 |
| `game_duration_min` | 게임 진행 시간(분) | 31.52 |
| `champion` | 플레이한 챔피언 | TwistedFate |
| `position` | 플레이 포지션 | MIDDLE |
| `win` | 승패 여부 (승리=1, 패배=0) | 1 |
| `kills` | 킬 수 | 7 |
| `deaths` | 데스 수 | 4 |
| `assists` | 어시스트 수 | 12 |
| `kda` | KDA `(K+A)/max(D,1)` | 4.75 |
| `cs` | 총 CS | 221 |
| `cs_per_min` | 분당 CS | 7.01 |
| `gold` | 총 획득 골드 | 13,842 |
| `gold_per_min` | 분당 획득 골드 | 439.15 |
| `damage` | 챔피언 대상 총 피해량 | 25,430 |
| `damage_per_min` | 분당 챔피언 피해량 | 806.79 |
| `vision_score` | 시야 점수 | 27 |
| `double_kills` | 더블킬 횟수 | 1 |
| `triple_kills` | 트리플킬 횟수 | 0 |
| `quadra_kills` | 쿼드라킬 횟수 | 0 |
| `penta_kills` | 펜타킬 횟수 | 0 |
| `game_mode` | 게임 모드 | CLASSIC |

### CSV 예시

```csv
match_id,game_date,game_duration_min,champion,position,win,kills,deaths,assists,kda,cs,cs_per_min,gold,gold_per_min,damage,damage_per_min,vision_score
KR_XXXXXXXXXX,2026-09-09 15:34:02,31.52,TwistedFate,MIDDLE,1,7,4,12,4.75,221,7.01,13842,439.15,25430,806.79,27
KR_XXXXXXXXXX,2026-09-08 13:21:15,27.84,Hwei,MIDDLE,0,5,8,7,1.50,194,6.97,10932,392.67,28120,1010.06,22
```

### 주요 파생 변수

Riot API에서 제공되는 원본 데이터를 그대로 사용하는 것뿐만 아니라,  
분석에 필요한 지표를 추가로 생성했습니다.

**KDA**

```text
KDA = (Kills + Assists) / max(Deaths, 1)
```

**분당 CS**

```text
CS/min = CS / 게임 시간(분)
```

**분당 골드**

```text
Gold/min = Gold / 게임 시간(분)
```

**분당 피해량**

```text
Damage/min = Damage / 게임 시간(분)
```

게임 시간으로 나눈 지표를 사용함으로써 게임 길이가 서로 다른 경기들을  
보다 동일한 기준에서 비교할 수 있도록 했습니다.

---

## 4. 데이터 전처리

수집한 데이터에 대해 분석 전 다음 항목을 확인했습니다.

- 결측치 확인
- 중복 Match ID 확인
- 데이터 타입 변환
- 게임 시간을 분 단위로 변환
- KDA 및 분당 지표 생성
- 분석 목적에 따른 구간 변수 생성

```python
df.info()
df.isnull().sum()
df.duplicated(subset="match_id").sum()
```

추가 분석을 위해 다음과 같은 파생 변수도 생성했습니다.

```text
day_of_week     → 게임 요일
duration_group  → 게임 시간 구간
```

예를 들어 `game_duration_min`을 기준으로 게임 시간을 다음과 같이 구간화하여  
게임 길이에 따른 승률 차이를 분석했습니다.

```text
15분 이하
15~20분
20~25분
25~30분
30~35분
35~40분
40분 이상
```
