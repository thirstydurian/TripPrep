# test_tavily.py
"""
Tavily API 테스트 코드
.env 파일에서 API 키를 읽어와서 검색 테스트
"""

from dotenv import load_dotenv
import os
from tavily import TavilyClient

# .env 파일 로드
load_dotenv()

# 환경변수에서 API 키 가져오기
tavily_api_key = os.getenv("TAVILY_API_KEY")

# API 키 확인
if not tavily_api_key:
    print("❌ 오류: TAVILY_API_KEY가 .env 파일에 설정되지 않았습니다!")
    print("\n.env 파일에 다음과 같이 추가하세요:")
    print("TAVILY_API_KEY=your-tavily-api-key")
    exit(1)

print("✅ TAVILY_API_KEY 로드 성공!")
print(f"   키 앞 10자: {tavily_api_key[:10]}...\n")

# Tavily 클라이언트 초기화
tavily = TavilyClient(api_key=tavily_api_key)

# 검색 테스트
print("🔍 검색 테스트 시작...")
print("   검색어: 일본 도쿄 입국 규정\n")

try:
    # 검색 실행
    results = tavily.search("일본 도쿄 입국 규정")
    
    print("="*60)
    print("📋 검색 결과")
    print("="*60)
    
    # 결과 출력
    if 'results' in results:
        for i, result in enumerate(results['results'], 1):
            print(f"\n[결과 {i}]")
            print(f"제목: {result.get('title', 'N/A')}")
            print(f"URL: {result.get('url', 'N/A')}")
            print(f"내용:\n{result.get('content', 'N/A')}")
            print("-"*60)
    else:
        print("검색 결과가 없습니다.")
    
    print("\n✅ 테스트 완료!")
    
except Exception as e:
    print(f"\n❌ 오류 발생: {str(e)}")
    print("\nAPI 키가 올바른지, 인터넷 연결이 정상인지 확인하세요.")