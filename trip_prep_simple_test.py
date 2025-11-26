# trip_prep_simple_test.py
"""
TripPrep 간단 테스트 버전
각 Agent를 단계별로 테스트
"""

import anthropic
import os
from typing import List, Dict


def test_agent1_search(destination: str, keywords: List[str]):
    """
    Agent 1 테스트: 간단한 웹 검색
    """
    print("\n" + "="*60)
    print("🔍 Agent 1 테스트: 검색 Agent")
    print("="*60)
    
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    # 테스트용으로 검색 쿼리 3개만 사용
    test_queries = [
        f"{destination} 필수 법적 요구사항",
        f"{destination} 여행 주의사항",
        f"{destination} {keywords[0]}" if keywords else f"{destination} 관광"
    ]
    
    print(f"\n📍 여행지: {destination}")
    print(f"🔑 키워드: {keywords}")
    print(f"\n실행할 검색 쿼리:")
    for i, q in enumerate(test_queries, 1):
        print(f"  {i}. {q}")
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] 검색 중: {query}")
        
        try:
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": f"'{query}'에 대해 웹 검색을 해서 핵심 정보 3-5가지만 간단히 정리해줘. 불릿 포인트로 작성해줘."
                }]
            )
            
            result = message.content[0].text
            results.append(f"### {query}\n{result}\n")
            
            # 결과 미리보기
            preview = result[:200] + "..." if len(result) > 200 else result
            print(f"✅ 완료! (결과 미리보기: {preview})")
            
        except Exception as e:
            print(f"❌ 실패: {str(e)}")
            results.append(f"### {query}\n검색 실패: {str(e)}\n")
    
    search_results = "\n".join(results)
    
    print("\n" + "="*60)
    print("✅ Agent 1 테스트 완료!")
    print("="*60)
    
    return search_results


def test_agent2_template(search_results: str, destination: str, keywords: List[str]):
    """
    Agent 2 테스트: 템플릿 커스터마이징
    """
    print("\n" + "="*60)
    print("🔧 Agent 2 테스트: 템플릿 커스터마이징 Agent")
    print("="*60)
    
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    base_template = """
<보고서 템플릿>
1. 해당 국가 특이사항
2. 필수 법적 요구사항
   a. 비자/무비자 규정
   b. 여권 유효기간
   c. 거주지 등록 의무
3. 항공
   a. 플랫폼 추천
   b. 저렴한 시기
4. 숙박
   a. 추천 지역
5. 통신
   a. USIM
   b. eSIM
6. 현지 결제 & 환전
7. 현지 교통수단
8. 필수 앱
9. 준비물
10. 사용자 키워드 관련 내용
</보고서 템플릿>
"""
    
    print(f"\n📋 기본 템플릿:")
    print(base_template)
    
    prompt = f"""
당신은 여행 보고서 템플릿을 커스터마이징하는 전문가입니다.

<기본_템플릿>
{base_template}
</기본_템플릿>

<여행지>
{destination}
</여행지>

<사용자_키워드>
{', '.join(keywords)}
</사용자_키워드>

<검색_결과>
{search_results}
</검색_결과>

작업:
1. 검색 결과에서 "필수", "의무", "등록", "금지", "제한", "주의" 같은 중요 키워드가 있는지 확인
2. 중요한 특수사항이 있으면 "1. 해당 국가 특이사항" 뒤에 새 섹션으로 추가
3. 사용자 키워드({', '.join(keywords)})를 "10. 사용자 키워드 관련 내용"에 구체적으로 추가

커스터마이징된 템플릿만 출력하세요 (설명 없이).
"""

    print("\n🤖 템플릿 커스터마이징 중...")
    
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        customized = message.content[0].text
        
        print("\n✅ 커스터마이징 완료!")
        print("\n📋 커스터마이징된 템플릿:")
        print(customized)
        
        print("\n" + "="*60)
        print("✅ Agent 2 테스트 완료!")
        print("="*60)
        
        return customized
        
    except Exception as e:
        print(f"\n❌ 실패: {str(e)}")
        print("기본 템플릿 반환")
        return base_template


def test_agent3_report(template: str, search_results: str, destination: str, keywords: List[str]):
    """
    Agent 3 테스트: 보고서 작성
    """
    print("\n" + "="*60)
    print("📝 Agent 3 테스트: 보고서 작성 Agent")
    print("="*60)
    
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    prompt = f"""
당신은 여행 준비 보고서를 작성하는 전문 작가입니다.

<여행지>
{destination}
</여행지>

<키워드>
{', '.join(keywords)}
</키워드>

<템플릿>
{template}
</템플릿>

<검색_결과>
{search_results}
</검색_결과>

작업:
1. 검색 결과를 바탕으로 템플릿의 각 항목을 채워주세요
2. 중요한 주의사항은 ⚠️로 강조
3. 마크다운 형식으로 작성 (## 헤더 사용)
4. 제목은 "# {destination} 여행 준비 보고서"

간단한 테스트이므로 각 섹션을 2-3문장 정도로 간결하게 작성해주세요.

마지막에 면책조항 추가:
---
⚠️ 이 보고서는 테스트용이며, 여행 전 공식 사이트에서 최신 정보를 확인하세요.
"""

    print("\n🤖 보고서 작성 중...")
    
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        report = message.content[0].text
        
        print("\n✅ 보고서 작성 완료!")
        print("\n" + "="*60)
        print("📄 생성된 보고서:")
        print("="*60)
        print(report)
        
        print("\n" + "="*60)
        print("✅ Agent 3 테스트 완료!")
        print("="*60)
        
        return report
        
    except Exception as e:
        print(f"\n❌ 실패: {str(e)}")
        return f"# 오류\n보고서 작성 실패: {str(e)}"


def run_full_test():
    """
    전체 프로세스 테스트 (3개 Agent 순차 실행)
    """
    print("\n" + "="*70)
    print("🚀 TripPrep 전체 시스템 테스트 시작")
    print("="*70)
    
    # 테스트 데이터
    destination = "일본 도쿄"
    keywords = ["온천", "라멘"]
    
    print(f"\n📍 테스트 여행지: {destination}")
    print(f"🔑 테스트 키워드: {keywords}")
    
    input("\n▶️  Enter를 눌러 Agent 1 (검색) 시작...")
    
    # Agent 1: 검색
    search_results = test_agent1_search(destination, keywords)
    
    input("\n▶️  Enter를 눌러 Agent 2 (템플릿 커스터마이징) 시작...")
    
    # Agent 2: 템플릿 커스터마이징
    customized_template = test_agent2_template(search_results, destination, keywords)
    
    input("\n▶️  Enter를 눌러 Agent 3 (보고서 작성) 시작...")
    
    # Agent 3: 보고서 작성
    report = test_agent3_report(customized_template, search_results, destination, keywords)
    
    # 결과 저장
    filename = f"test_report_{destination.replace(' ', '_')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)
    
    print("\n" + "="*70)
    print("✨ 전체 테스트 완료!")
    print("="*70)
    print(f"\n📁 보고서가 저장되었습니다: {filename}")
    
    return report


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║          TripPrep 간단 테스트 프로그램                    ║
╚══════════════════════════════════════════════════════════╝

이 프로그램은 3개의 Agent를 단계별로 테스트합니다:
  1. 검색 Agent (웹 검색)
  2. 템플릿 커스터마이징 Agent
  3. 보고서 작성 Agent

각 단계마다 결과를 확인할 수 있습니다.
    """)
    
    choice = input("테스트를 시작하시겠습니까? (y/n): ")
    
    if choice.lower() == 'y':
        run_full_test()
    else:
        print("\n테스트를 취소했습니다.")
