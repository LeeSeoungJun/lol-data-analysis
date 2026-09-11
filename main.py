import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv


# ==========================================
# 설정
# ==========================================

print("프로그램 시작")

load_dotenv()

API_KEY = os.getenv("RIOT_API_KEY")

GAME_NAME = "divert"
TAG_LINE = "KR1"

# 가져올 게임 수
GAME_COUNT = 500

HEADERS = {
    "X-Riot-Token": API_KEY
}

if not API_KEY:
    raise Exception(".env에서 RIOT_API_KEY를 찾을 수 없습니다.")


# ==========================================
# Riot API 요청 함수
# ==========================================

def riot_get(url):

    while True:

        response = requests.get(
            url,
            headers=HEADERS
        )

        if response.status_code == 200:
            return response.json()

        elif response.status_code == 429:

            # Riot 서버가 알려주는 대기 시간
            retry_after = int(
                response.headers.get("Retry-After", 10)
            )

            print(
                f"API 요청 제한 발생 → "
                f"{retry_after}초 대기"
            )

            time.sleep(retry_after + 1)

        else:

            print(
                "API 오류:",
                response.status_code
            )

            print(response.text)

            return None


# ==========================================
# 1. Riot ID → PUUID
# ==========================================

print("\nRiot 계정 정보를 가져오는 중...")


account_url = (
    "https://asia.api.riotgames.com/"
    "riot/account/v1/accounts/"
    f"by-riot-id/{GAME_NAME}/{TAG_LINE}"
)


account_data = riot_get(account_url)


if account_data is None:

    raise Exception(
        "Riot 계정 정보를 가져오지 못했습니다."
    )


puuid = account_data["puuid"]


print("게임 이름:", account_data["gameName"])
print("태그:", account_data["tagLine"])
print("PUUID 확인 완료")


# ==========================================
# 2. 최근 Match ID 가져오기
# ==========================================

print(
    f"\n최근 게임 {GAME_COUNT}개를 "
    f"가져오는 중..."
)


match_ids = []


# Riot API는 한 번에 최대 100개
for start in range(
    0,
    GAME_COUNT,
    100
):

    count = min(
        100,
        GAME_COUNT - start
    )

    print(
        f"{start + 1} ~ "
        f"{start + count}번째 게임 "
        f"ID 가져오는 중..."
    )


    match_url = (
        "https://asia.api.riotgames.com/"
        "lol/match/v5/"
        f"matches/by-puuid/{puuid}/ids"
        f"?start={start}"
        f"&count={count}"
    )


    ids = riot_get(match_url)


    if ids is None:

        print(
            "Match ID 요청 실패"
        )

        break


    if len(ids) == 0:

        print(
            "더 이상 가져올 게임이 없습니다."
        )

        break


    match_ids.extend(ids)


    # 요청 사이 짧은 대기
    time.sleep(0.2)


print(
    f"\n가져온 게임 수: "
    f"{len(match_ids)}"
)


if len(match_ids) == 0:

    raise Exception(
        "Match ID를 가져오지 못했습니다."
    )


# ==========================================
# 3. 게임 상세 데이터 수집
# ==========================================

results = []


for index, match_id in enumerate(
    match_ids,
    start=1
):

    print(
        f"[{index}/{len(match_ids)}] "
        f"{match_id}"
    )


    match_url = (
        "https://asia.api.riotgames.com/"
        "lol/match/v5/"
        f"matches/{match_id}"
    )


    match_data = riot_get(
        match_url
    )


    if match_data is None:

        print(
            "게임 데이터 요청 실패 → 건너뜀"
        )

        continue


    info = match_data["info"]


    # ======================================
    # 내 데이터 찾기
    # ======================================

    me = None


    for player in info["participants"]:

        if player["puuid"] == puuid:

            me = player

            break


    if me is None:

        print(
            "내 플레이어 정보를 "
            "찾지 못했습니다."
        )

        continue


    # ======================================
    # 기본 데이터
    # ======================================

    game_duration = info[
        "gameDuration"
    ]


    # 초 → 분
    game_minutes = (
        game_duration / 60
    )


    kills = me["kills"]

    deaths = me["deaths"]

    assists = me["assists"]


    # CS
    cs = (
        me.get(
            "totalMinionsKilled",
            0
        )
        +
        me.get(
            "neutralMinionsKilled",
            0
        )
    )


    gold = me[
        "goldEarned"
    ]


    damage = me[
        "totalDamageDealtToChampions"
    ]


    vision_score = me.get(
        "visionScore",
        0
    )


    # ======================================
    # 분당 지표
    # ======================================

    if game_minutes > 0:

        cs_per_min = (
            cs / game_minutes
        )

        gold_per_min = (
            gold / game_minutes
        )

        damage_per_min = (
            damage / game_minutes
        )

    else:

        cs_per_min = 0
        gold_per_min = 0
        damage_per_min = 0


    # ======================================
    # KDA
    # ======================================

    if deaths > 0:

        kda = (
            kills + assists
        ) / deaths

    else:

        kda = (
            kills + assists
        )


    # ======================================
    # 데이터 저장
    # ======================================

    results.append({

        "match_id":
            match_id,

        "game_date":
            pd.to_datetime(
                info[
                    "gameStartTimestamp"
                ],
                unit="ms"
            ),

        "game_duration_min":
            round(
                game_minutes,
                2
            ),

        "champion":
            me["championName"],

        "position":
            me.get(
                "teamPosition",
                ""
            ),

        "win":
            int(
                me["win"]
            ),

        "kills":
            kills,

        "deaths":
            deaths,

        "assists":
            assists,

        "kda":
            round(
                kda,
                2
            ),

        "cs":
            cs,

        "cs_per_min":
            round(
                cs_per_min,
                2
            ),

        "gold":
            gold,

        "gold_per_min":
            round(
                gold_per_min,
                2
            ),

        "damage":
            damage,

        "damage_per_min":
            round(
                damage_per_min,
                2
            ),

        "vision_score":
            vision_score,

        "double_kills":
            me.get(
                "doubleKills",
                0
            ),

        "triple_kills":
            me.get(
                "tripleKills",
                0
            ),

        "quadra_kills":
            me.get(
                "quadraKills",
                0
            ),

        "penta_kills":
            me.get(
                "pentaKills",
                0
            ),

        "game_mode":
            info.get(
                "gameMode",
                ""
            )

    })


    # API 호출 간격
    time.sleep(0.15)


# ==========================================
# 4. DataFrame 생성
# ==========================================

df = pd.DataFrame(
    results
)


if len(df) == 0:

    raise Exception(
        "수집된 게임 데이터가 없습니다."
    )


# 중복 제거
df = df.drop_duplicates(
    subset="match_id"
)


# 날짜순 정렬
df = df.sort_values(
    "game_date",
    ascending=False
)


# ==========================================
# 5. CSV 저장
# ==========================================

file_name = (
    "my_lol_games.csv"
)


df.to_csv(
    file_name,
    index=False,
    encoding="utf-8-sig"
)


# ==========================================
# 6. 결과 출력
# ==========================================

print(
    "\n=============================="
)

print(
    "데이터 수집 완료!"
)

print(
    "=============================="
)


print(
    f"게임 수: {len(df)}"
)

print(
    f"저장 파일: {file_name}"
)


print(
    "\n최근 게임:"
)

print(
    df.head()
)


print(
    "\n승률:"
)

print(
    f"{df['win'].mean() * 100:.2f}%"
)