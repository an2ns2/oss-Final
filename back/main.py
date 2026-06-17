from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Dict, Any
from fastapi.middleware.cors import CORSMiddleware
import json
import random
import os

app = FastAPI(
    title="Midnight Bartender API",
    description="JSON DB 및 가중치 기반 칵테일 추천 엔진",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Pydantic 스키마: 도수(abv)를 int형으로 변경
class CocktailRequest(BaseModel):
    persona: str = Field(..., description="사용자의 현재 감정/성향")
    taste: str = Field(..., description="선호하는 맛")
    abv: int = Field(..., description="원하는 알코올 도수 (0~40)")

class CocktailResponse(BaseModel):
    drink: str
    comment: str
    ingredients: str

# 2. JSON 데이터베이스 로드 함수
def load_cocktail_db():
    # 파일 경로를 안전하게 구성하여 JSON 파일을 읽어옴
    current_dir = os.path.dirname(os.path.realpath(__file__))
    json_path = os.path.join(current_dir, "cocktails.json")
    
    with open(json_path, 'r', encoding='utf-8') as file:
        return json.load(file)

COCKTAIL_DB = load_cocktail_db()

# 3. 비즈니스 로직: 가중치 기반 스코어링 알고리즘
def calculate_similarity(request: CocktailRequest, tags: Dict[str, Any]) -> int:
    score = 0
    
    # [가중치 3점] 도수(abv)가 DB에 정의된 해당 칵테일의 최소/최대 범위 안에 있는지 확인
    if tags["min_abv"] <= request.abv <= tags["max_abv"]:
        score += 3
        
    # [가중치 2점] 맛 일치 여부
    if tags["taste"] == request.taste:
        score += 2
        
    # [가중치 1점] 성향 일치 여부
    if tags["persona"] == request.persona:
        score += 1
        
    return score

@app.post("/recommend", response_model=CocktailResponse)
def recommend_cocktail(request: CocktailRequest):
    best_matches = []  # 단일 딕셔너리가 아닌, 최고점 후보들을 담을 '리스트'로 변경
    highest_score = -1

    # DB 순회 탐색
    for cocktail in COCKTAIL_DB:
        score = calculate_similarity(request, cocktail["tags"])
        
        # 1. 기존 최고점보다 높은 점수를 발견한 경우: 후보군 리스트를 초기화하고 새로 담음
        if score > highest_score:
            highest_score = score
            best_matches = [cocktail["result"]]
            
        # 2. [타이브레이킹 핵심] 기존 최고점과 동점인 경우: 후보군 리스트에 추가 (버리지 않음)
        elif score == highest_score:
            best_matches.append(cocktail["result"])

    # 예외 처리: 매칭되는 조건이 아예 없을 경우 (highest_score가 0인 경우도 방어)
    if highest_score == 0 or not best_matches:
        return CocktailResponse(
            drink="바텐더의 비밀 레시피",
            comment="당신의 복잡한 마음을 위로할 특별한 한 잔입니다. 오늘은 제가 이끄는 대로 드셔보시죠.",
            ingredients="비밀 재료, 약간의 위로, 얼음"
        )

    # 3. 최고점 후보군 중에서 무작위로 하나를 최종 선택하여 반환
    final_choice = random.choice(best_matches)

    return CocktailResponse(**final_choice)

@app.get("/")
def read_root():
    return {"status": "ok", "message": f"DB Loaded. {len(COCKTAIL_DB)} cocktails ready."}