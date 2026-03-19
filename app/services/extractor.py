import io
import httpx
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup


async def extract_text_from_pdf(file_bytes: bytes) -> str:
    """PDF 바이트에서 텍스트 추출"""
    reader = PdfReader(io.BytesIO(file_bytes))
    texts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            texts.append(text)
    return "\n".join(texts)


async def extract_text_from_url(url: str) -> str:
    """URL에서 텍스트 추출 (크롤링)"""
    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        response = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        html = response.text

    soup = BeautifulSoup(html, "html.parser")

    # 불필요한 태그 제거
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    # 주요 콘텐츠 추출 시도
    main = soup.find("main") or soup.find("article") or soup.find("body")
    if main:
        text = main.get_text(separator="\n", strip=True)
    else:
        text = soup.get_text(separator="\n", strip=True)

    # 빈 줄 정리
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def truncate_text(text: str, max_chars: int = 30000) -> str:
    """텍스트 길이 제한"""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[... 텍스트가 길어 일부 생략됨]"
