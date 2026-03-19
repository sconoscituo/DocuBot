from enum import Enum

class PlanType(str, Enum):
    FREE = "free"
    PRO = "pro"      # 월 9,900원
    BUSINESS = "business"  # 월 29,900원

PLAN_LIMITS = {
    PlanType.FREE:     {"documents": 3,   "questions_per_month": 50,  "share_link": False},
    PlanType.PRO:      {"documents": 30,  "questions_per_month": 500, "share_link": True},
    PlanType.BUSINESS: {"documents": 999, "questions_per_month": 9999,"share_link": True},
}
PLAN_PRICES_KRW = {PlanType.FREE: 0, PlanType.PRO: 9900, PlanType.BUSINESS: 29900}
