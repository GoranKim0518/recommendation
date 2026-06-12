from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import random
import os

app = FastAPI(title="Lunch Engine Backend", version="3.0")

# 요청 데이터 스키마
class RecommendationRequest(BaseModel):
    target_category: str
    target_soup_type: str
    target_cooking_style: str
    target_spiciness: str
    target_vibe: str

# menu_data.json을 읽어 반환
def load_menu_data():
    json_path = os.path.join(os.path.dirname(__file__), "menu_data.json")
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="menu_data.json 파일을 찾을 수 없습니다.")

# 입력 조건과 메뉴를 비교해 점수 계산
def calculate_best_match(req: RecommendationRequest):
    menu_pool = load_menu_data()
    
    # 같은 카테고리만 후보로 삼음
    candidates = [m for m in menu_pool if m["target_category"] == req.target_category]
    
    if not candidates:
        return "근처 백반집", "선택하신 기본 조건에 부합하는 메뉴가 없어 가장 무난한 백반집을 추천합니다.", 100

    scored_results = []
    
    for menu in candidates:
        score = 40.0  # 카테고리 일치 기본 점수
        
        # 조리 방식 일치 시 가중치 부여 (25점)
        if menu.get("target_cooking_style") == req.target_cooking_style:
            score += 25.0
        # '튀김/구이' 선택 시 카츠동은 튀김으로 인정
        elif req.target_cooking_style == "튀김/구이" and menu.get("menu_name") == "카츠동":
            score += 25.0
            
        # 국물 유무 일치 시 가중치 (20점)
        if menu.get("target_soup_type") == req.target_soup_type:
            score += 20.0
            
        # 매운맛 일치 시 가중치 (7.5점)
        if menu.get("target_spiciness") == req.target_spiciness:
            score += 7.5
            
        # 분위기/목적 일치 시 가중치 (7.5점)
        if menu.get("target_vibe") == req.target_vibe:
            score += 7.5
            
        scored_results.append({
            "name": menu["menu_name"],
            "score": int(score)
        })

    scored_results.sort(key=lambda x: x["score"], reverse=True)
    
    max_score = scored_results[0]["score"]
    best_candidates = [m for m in scored_results if m["score"] == max_score]
    
    winner = random.choice(best_candidates)
    
    rationale = f"지금 당기시는 스타일과 무려 {winner['score']}% 일치하는 오늘의 최적 추천 메뉴입니다!"
    
    return winner["name"], rationale, winner["score"]

@app.post("/api/recommend")
async def get_recommendation(request: RecommendationRequest):
    try:
        recommended_menu, rationale, match_score = calculate_best_match(request)
        return {
            "status": "success",
            "recommended_menu": recommended_menu,
            "rationale": rationale,
            "match_score": match_score
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"백엔드 연산 제어 오류: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)