import google.generativeai as genai
from app.config import config

genai.configure(api_key=config.GEMINI_API_KEY)


async def answer_question(document_text: str, question: str) -> str:
    """문서 기반 Q&A"""
    model = genai.GenerativeModel(config.GEMINI_MODEL)
    prompt = f"""다음 문서를 기반으로 질문에 답하세요. 문서에 없는 내용은 "문서에서 찾을 수 없습니다"라고 답하세요.

문서:
{document_text[:30000]}

질문: {question}

답변:"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"답변 생성 중 오류가 발생했습니다: {str(e)}"


async def generate_document_summary(document_text: str) -> str:
    """문서 요약 생성"""
    model = genai.GenerativeModel(config.GEMINI_MODEL)
    prompt = f"""다음 문서를 3~5문장으로 요약해주세요.

문서:
{document_text[:10000]}

요약:"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"요약 생성 실패: {str(e)}"


async def suggest_questions(document_text: str) -> list[str]:
    """문서 기반 추천 질문 생성"""
    model = genai.GenerativeModel(config.GEMINI_MODEL)
    prompt = f"""다음 문서를 읽고 사용자가 물어볼 만한 질문 5개를 생성하세요. 각 줄에 하나씩 작성하세요.

문서:
{document_text[:5000]}

추천 질문:"""
    try:
        response = model.generate_content(prompt)
        lines = [line.strip().lstrip("0123456789.-) ") for line in response.text.splitlines() if line.strip()]
        return lines[:5]
    except Exception:
        return []
