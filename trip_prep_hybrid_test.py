# trip_prep_hybrid_test.py
"""
TripPrep 하이브리드 테스트 버전
- Claude 지식 기반 정보 생성 (90%)
- 웹 검색은 최신 법적 요구사항만 (10%)
- 모델: Claude Haiku 4.5 (비용 절감)
"""

import anthropic
import os
from typing import List, Dict


# 사용 모델 설정
MODEL = "claude-haiku-4-20250514"


def generate_basic_info_from_knowledge(client: anthropic.Anthropic, 
                                       destination: str, 
                                       keywords: List[str]) -> str:
    """
    Claude의 기존 지식을 활용하여 기본 정보 생성
    웹 검색 없이 일반적인 여행 정보 제공
    """
    print(f"\n📚 Claude 지식 기반으로 기본 정보 생성 중...")
    
    prompt = f"""
당신은 여행 준비 전문가입니다. {destination} 여행에 대한 기본 정보를 제공해주세요.

<여행지>
{destination}
</여행지>

<사용자 관심사>
{', '.join(keywords) if keywords else '일반 관광'}
</사용자 관심사>

다음 항목들에 대해 간단히 정리해주세요:

1. 항공
   - 주요 공항
   - 항공권 예약 팁
   - 저렴한 시기 (일반적으로)

2. 숙박
   - 추천 지역
   - 숙박 시설 종류
   - 예약 플랫폼

3. 통신
   - USIM 옵션
   - eSIM 가능 여부
   - 로밍 vs 현지 유심

4. 현지 결제 & 환전
   - 통용되는 결제 수단
   - 환전 팁
   - 추천 카드

5. 교통수단
   - 주요 교통수단
   - 교통카드
   - 택시/대중교통 이용 팁

6. 필수 앱
   - 지도 앱
   - 번역 앱
   - 교통 앱
   - 기타 유용한 앱

7. 준비물
   - 전압/어댑터
   - 기후별 옷차림
   - 필수 휴대품

8. 사용자 관심사 관련 정보
   - {', '.join(keywords)} 관련 추천 장소나 팁

각 항목을 2-3문장으로 간결하게 작성해주세요.
"""

    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=3000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        result = message.content[0].text
        print(f"✅ 기본 정보 생성 완료!")
        return result
        
    except Exception as e:
        print(f"❌ 실패: {str(e)}")
        return f"기본 정보 생성 실패: {str(e)}"


def execute_critical_web_search(client: anthropic.Anthropic,
                                destination: str,
                                keywords: List[str]) -> str:
    """
    핵심 최신 정보만 웹 검색
    - 법적 요구사항
    - 입국 규정
    - 특별 주의사항
    """
    print(f"\n🔍 최신 정보 웹 검색 중...")
    
    # 최소한의 검색 쿼리 (2-3개)
    critical_queries = [
        f"{destination} 입국 규정 외교부",
        f"{destination} 필수 법적 요구사항 비자",
    ]
    
    # 사용자 키워드가 있으면 1개 추가
    if keywords:
        critical_queries.append(f"{destination} {keywords[0]} 최신 정보")
    
    print(f"검색 쿼리 ({len(critical_queries)}개):")
    for i, q in enumerate(critical_queries, 1):
        print(f"  {i}. {q}")
    
    all_results = []
    
    for i, query in enumerate(critical_queries, 1):
        print(f"\n[{i}/{len(critical_queries)}] 검색 중: {query}")
        
        try:
            message = client.messages.create(
                model=MODEL,
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": f"다음 검색어로 웹 검색을 수행하고, 가장 중요한 정보 3-5가지만 불릿 포인트로 정리해줘. 특히 '필수', '의무', '금지', '주의' 같은 중요한 정보에 집중해줘.\n\n검색어: {query}"
                }]
            )
            
            result = message.content[0].text
            all_results.append(f"### {query}\n{result}\n")
            
            # 미리보기
            preview = result[:150] + "..." if len(result) > 150 else result
            print(f"✅ 완료! (미리보기: {preview})")
            
        except Exception as e:
            print(f"❌ 실패: {str(e)}")
            all_results.append(f"### {query}\n검색 실패\n")
    
    print(f"\n✅ 웹 검색 완료! (총 {len(critical_queries)}회)")
    
    return "\n".join(all_results)


def test_hybrid_agent1(destination: str, keywords: List[str]):
    """
    Agent 1 테스트: 하이브리드 검색
    """
    print("\n" + "="*60)
    print("🔍 Agent 1 테스트: 하이브리드 검색 Agent")
    print("="*60)
    
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    print(f"\n📍 여행지: {destination}")
    print(f"🔑 키워드: {keywords}")
    print(f"🤖 사용 모델: {MODEL}")
    
    # Phase 1: Claude 지식으로 기본 정보
    basic_info = generate_basic_info_from_knowledge(client, destination, keywords)
    
    # Phase 2: 웹 검색으로 최신 정보
    latest_info = execute_critical_web_search(client, destination, keywords)
    
    search_results = {
        'basic_info': basic_info,
        'latest_info': latest_info
    }
    
    print("\n" + "="*60)
    print("✅ Agent 1 테스트 완료!")
    print("="*60)
    
    return search_results


def test_hybrid_agent2(search_results: Dict, destination: str, keywords: List[str]):
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
    
    print(f"\n📋 기본 템플릿 확인 완료")
    print(f"🤖 사용 모델: {MODEL}")
    
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

<웹_검색_최신_정보>
{search_results['latest_info']}
</웹_검색_최신_정보>

작업:
1. 웹 검색 결과에서 "필수", "의무", "등록", "금지", "제한", "주의", "경고" 같은 중요 키워드 확인
2. 중요한 특수사항이 발견되면 "1. 해당 국가 특이사항" 뒤에 별도 섹션으로 추가
   예: "1-1. ⚠️ 필수 거주지 등록 절차" 같은 형태
3. 사용자 키워드({', '.join(keywords)})를 "10. 사용자 키워드 관련 내용"에 구체적으로 추가

커스터마이징된 템플릿만 출력하세요 (설명 없이).
"""

    print("\n🤖 템플릿 커스터마이징 중...")
    
    try:
        message = client.messages.create(
            model=MODEL,
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


def test_hybrid_agent3(template: str, search_results: Dict, 
                       destination: str, keywords: List[str]):
    """
    Agent 3 테스트: 보고서 작성
    """
    print("\n" + "="*60)
    print("📝 Agent 3 테스트: 보고서 작성 Agent")
    print("="*60)
    
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    print(f"🤖 사용 모델: {MODEL}")
    
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

<기본_정보_Claude_지식>
{search_results['basic_info']}
</기본_정보_Claude_지식>

<최신_정보_웹_검색>
{search_results['latest_info']}
</최신_정보_웹_검색>

작업:
1. 기본 정보는 Claude 지식을 활용
2. 법적 요구사항, 입국 규정 등은 웹 검색 최신 정보를 우선 사용
3. ⚠️로 중요 주의사항 강조
4. 마크다운 형식 (## 헤더)
5. 제목: "# {destination} 여행 준비 보고서"

각 섹션을 2-3문장으로 간결하게 작성해주세요.

마지막에 면책조항:
---
⚠️ **면책 조항**
- 이 보고서는 2025년 11월 기준으로 작성되었습니다.
- 법적 요구사항은 웹 검색 기반이나, 여행 전 외교부 및 대사관에서 최신 정보를 반드시 확인하세요.
- 기타 정보는 일반적인 가이드이며 변동 가능합니다.
"""

    print("\n🤖 보고서 작성 중...")
    
    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=4000,
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


def run_hybrid_test():
    """
    하이브리드 방식 전체 테스트
    """
    print("\n" + "="*70)
    print("🚀 TripPrep 하이브리드 시스템 테스트")
    print("="*70)
    print(f"\n💡 특징:")
    print(f"   - Claude 지식 활용 (90%)")
    print(f"   - 웹 검색 최소화 (10%, 2-3회)")
    print(f"   - 모델: {MODEL}")
    print(f"   - 비용 효율적!")
    
    # 테스트 데이터
    destination = "일본 도쿄"
    keywords = ["온천", "라멘"]
    
    print(f"\n📍 테스트 여행지: {destination}")
    print(f"🔑 테스트 키워드: {keywords}")
    
    input("\n▶️  Enter를 눌러 Agent 1 (하이브리드 검색) 시작...")
    
    # Agent 1: 하이브리드 검색
    search_results = test_hybrid_agent1(destination, keywords)
    
    input("\n▶️  Enter를 눌러 Agent 2 (템플릿 커스터마이징) 시작...")
    
    # Agent 2: 템플릿 커스터마이징
    customized_template = test_hybrid_agent2(search_results, destination, keywords)
    
    input("\n▶️  Enter를 눌러 Agent 3 (보고서 작성) 시작...")
    
    # Agent 3: 보고서 작성
    report = test_hybrid_agent3(customized_template, search_results, destination, keywords)
    
    # 결과 저장
    filename = f"hybrid_report_{destination.replace(' ', '_')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)
    
    print("\n" + "="*70)
    print("✨ 하이브리드 테스트 완료!")
    print("="*70)
    print(f"\n📁 보고서가 저장되었습니다: {filename}")
    print(f"\n💰 예상 비용:")
    print(f"   - 웹 검색: 2-3회 (최소화)")
    print(f"   - 모델: {MODEL} (저렴함)")
    print(f"   - 토큰: 약 20-30K (효율적)")
    
    return report


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║     TripPrep 하이브리드 테스트 (비용 효율 버전)         ║
╚══════════════════════════════════════════════════════════╝

이 버전의 특징:
  ✅ Claude 지식으로 대부분 정보 생성 (빠르고 저렴)
  ✅ 웹 검색은 필수 최신 정보만 (2-3회)
  ✅ Haiku 4.5 모델 사용 (비용 절감)
  ✅ 품질은 유지하면서 비용은 최소화

검색 API 설정:
  - claude.ai 웹 인터페이스처럼 자동 검색됩니다
  - 별도 API 키 불필요
    """)
    
    choice = input("테스트를 시작하시겠습니까? (y/n): ")
    
    if choice.lower() == 'y':
        run_hybrid_test()
    else:
        print("\n테스트를 취소했습니다.")
