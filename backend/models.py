from pydantic import BaseModel, Field

class RecommendationRequest(BaseModel):
    target_category: str = Field(..., description="음식 카테고리 (한/중/양/일)")
    target_soup_type: str = Field(..., description="국물 유무 상태")
    target_cooking_style: str = Field(..., description="원하는 조리 방식 및 식감")
    target_spiciness: str = Field(..., description="매운맛 강도")
    target_vibe: str = Field(..., description="식사 목적 및 분위기")

class RecommendationResponse(BaseModel):
    recommended_menu: str = Field(..., description="추천된 최종 메뉴명")
    rationale: str = Field(..., description="알고리즘 분석 근거 문구")
    match_score: int = Field(..., description="조건 매칭률 점수 (0-100)")