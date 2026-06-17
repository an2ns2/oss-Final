from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Midnight Bartender API",
    description="가중치 기반 칵테일 추천 룰 엔진",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Pydantic을 활용한 엄격한 데이터 검증 스키마 설계
class CocktailRequest(BaseModel):
    persona: str = Field(..., description="사용자의 현재 감정/성향")
    taste: str = Field(..., description="선호하는 맛")
    abv: str = Field(..., description="원하는 알코올 도수")

class CocktailResponse(BaseModel):
    drink: str
    comment: str
    ingredients: str

# 2. 데이터와 로직의 분리: 칵테일 메타데이터(Knowledge Base) 구축
# 추후 실제 DB(MySQL, MongoDB)나 AI 모델로 쉽게 전환할 수 있는 구조입니다.
COCKTAIL_DB: List[Dict[str, Any]] = [
    {
        "id": "godfather",
        "tags": {"persona": "[고독을 즐기는 늑대]", "taste": "☕ 인생의 쓴맛 (드라이함)", "abv": "20% 이상"},
        "result": {
            "drink": "갓파더 (Godfather)",
            "comment": "위스키와 아마레또의 묵직함. 고독을 씹어 삼키기엔 이만한 게 없죠.",
            "ingredients": "위스키, 아마레또 리큐르, 시나몬 스틱"
        }
    },
    {
        "id": "kahlua_milk",
        "tags": {"persona": "[침대와 물아일체 귀차니스트]", "taste": "🍫 스트레스 녹이는 달달함", "abv": "5~10%"},
        "result": {
            "drink": "깔루아 밀크 (Kahlua Milk)",
            "comment": "복잡한 쉐이킹 없이 우유만 부으면 끝납니다. 침대 위에서 넷플릭스 보며 홀짝이세요.",
            "ingredients": "깔루아(커피 리큐르), 우유, 얼음"
        }
    },
    {
        "id": "cinderella",
        "tags": {"persona": "[몽글몽글 감성 낭만파]", "taste": "🍋 침이 고이는 상큼함", "abv": "0~5%"},
        "result": {
            "drink": "신데렐라 (Cinderella - 논알콜)",
            "comment": "오렌지와 파인애플의 상큼함. 내일의 일상을 지켜야 하는 낭만파를 위한 완벽한 음료입니다.",
            "ingredients": "오렌지 주스, 파인애플 주스, 레몬즙, 탄산수"
        }
    },
    {
        "id": "faust",
        "tags": {"persona": "[다 부수고 싶은 반항아]", "taste": "☕ 인생의 쓴맛 (드라이함)", "abv": "20% 이상"},
        "result": {
            "drink": "파우스트 (Faust)",
            "comment": "악마에게 영혼을 팔아서라도 오늘 밤의 스트레스를 날려버리세요. 아주 독하고 붉은 술입니다.",
            "ingredients": "오버프루프 럼, 크레임 드 카시스, 피치 리큐르"
        }
    },
    {
        "id": "aperol_spritz",
        "tags": {"persona": "[주목받고 싶은 파티광]", "taste": "스파클링", "abv": "5~10%"},
        "result": {
            "drink": "아페롤 스프리츠 (Aperol Spritz)",
            "comment": "기분 좋은 탄산과 쌉싸름한 오렌지 향이 당신의 기분을 가볍게 끌어올려 줄 겁니다.",
            "ingredients": "아페롤, 프로세코(스파클링 와인), 탄산수, 오렌지 슬라이스"
        }
    }
]

# 3. 비즈니스 로직: 가중치 기반 스코어링 알고리즘
def calculate_similarity(request: CocktailRequest, tags: Dict[str, str]) -> int:
    """사용자 입력과 칵테일 태그 간의 유사도 점수를 계산합니다."""
    score = 0
    # 도수(abv)는 칵테일 선택의 절대적 기준이므로 가장 높은 가중치 부여
    if tags["abv"] in request.abv:
        score += 3
    # 맛(taste)은 중요한 기준이므로 중간 가중치
    if tags["taste"] in request.taste:
        score += 2
    # 페르소나는 보조 기준
    if tags["persona"] in request.persona:
        score += 1
        
    return score

@app.post("/recommend", response_model=CocktailResponse)
def recommend_cocktail(request: CocktailRequest):
    best_match = None
    highest_score = -1

    # DB를 순회하며 사용자 입력과 가장 유사도가 높은 칵테일을 탐색
    for cocktail in COCKTAIL_DB:
        score = calculate_similarity(request, cocktail["tags"])
        
        if score > highest_score:
            highest_score = score
            best_match = cocktail["result"]

    # 매칭 점수가 너무 낮거나 예외 상황일 경우의 Fallback (기본값)
    if highest_score == 0 or not best_match:
        return CocktailResponse(
            drink="바텐더의 비밀 레시피",
            comment="당신의 복잡한 마음을 위로할 특별한 한 잔입니다. 오늘은 제가 이끄는 대로 드셔보시죠.",
            ingredients="비밀 재료, 약간의 위로, 얼음"
        )

    return CocktailResponse(**best_match)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Midnight Bartender 추천 엔진이 가동 중입니다."}