"""
보고서 생성 API
GPT를 사용하여 워크플로우 결과를 바탕으로 투자 분석 보고서를 생성합니다.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class WorkflowResult(BaseModel):
    tool_used: Optional[str] = None
    result: Any = None
    status: Optional[str] = None

class ReportRequest(BaseModel):
    workflowResults: List[WorkflowResult]
    timestamp: str
    totalStocks: int = 0
    filteredStocks: int = 0

@router.post("/generate-report")
async def generate_report(request: ReportRequest):
    """
    워크플로우 실행 결과를 바탕으로 투자 분석 보고서를 생성합니다.
    """
    try:
        logger.info("보고서 생성 요청 수신")
        logger.info(f"분석된 종목 수: {request.totalStocks}")
        logger.info(f"필터링된 종목 수: {request.filteredStocks}")
        
        # 워크플로우 결과 분석
        analysis_data = analyze_workflow_results(request.workflowResults)
        
        # 보고서 생성
        report_content = generate_investment_report(
            analysis_data,
            request.totalStocks,
            request.filteredStocks,
            request.timestamp
        )
        
        logger.info("보고서 생성 완료")
        return report_content
        
    except Exception as e:
        logger.error(f"보고서 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"보고서 생성 실패: {str(e)}")

def analyze_workflow_results(workflow_results: List[WorkflowResult]) -> Dict[str, Any]:
    """워크플로우 결과를 분석하여 보고서 데이터로 변환"""
    analysis = {
        "all_tickers": None,
        "filtered_stocks": None,
        "market_news": None,
        "foreign_investment": None,
        "sector_analysis": None
    }
    
    for result in workflow_results:
        if not result.tool_used or not result.result:
            continue
            
        try:
            # JSON 문자열인 경우 파싱
            if isinstance(result.result, str):
                data = json.loads(result.result)
            else:
                data = result.result
                
            if result.tool_used == "get_all_tickers":
                analysis["all_tickers"] = data
            elif result.tool_used == "filter_stocks_by_fundamentals":
                analysis["filtered_stocks"] = data
            elif result.tool_used == "get_market_news":
                analysis["market_news"] = data
            elif result.tool_used == "get_foreign_investment":
                analysis["foreign_investment"] = data
            elif result.tool_used == "get_sector_performance":
                analysis["sector_analysis"] = data
                
        except json.JSONDecodeError:
            logger.warning(f"JSON 파싱 실패: {result.tool_used}")
            continue
        except Exception as e:
            logger.warning(f"결과 분석 실패 {result.tool_used}: {str(e)}")
            continue
    
    return analysis

def generate_investment_report(
    analysis_data: Dict[str, Any],
    total_stocks: int,
    filtered_stocks: int,
    timestamp: str
) -> str:
    """분석 데이터를 바탕으로 투자 분석 보고서 생성"""
    
    report_sections = []
    
    # 1. 보고서 헤더
    report_sections.append(f"""# 투자 분석 보고서

**생성일시:** {timestamp}  
**분석 대상:** 전체 {total_stocks}개 종목  
**필터링 결과:** {filtered_stocks}개 우량 종목 선별  

---
""")
    
    # 2. 요약
    summary = generate_summary(analysis_data, total_stocks, filtered_stocks)
    report_sections.append(f"""## 📊 분석 요약

{summary}

---
""")
    
    # 3. 선별된 종목 분석
    if analysis_data.get("filtered_stocks"):
        stock_analysis = generate_stock_analysis(analysis_data["filtered_stocks"])
        report_sections.append(f"""## 🎯 선별 종목 분석

{stock_analysis}

---
""")
    
    # 4. 시장 동향 분석
    if analysis_data.get("market_news"):
        market_analysis = generate_market_analysis(analysis_data["market_news"])
        report_sections.append(f"""## 📈 시장 동향 분석

{market_analysis}

---
""")
    
    # 5. 외국인 투자 동향
    if analysis_data.get("foreign_investment"):
        foreign_analysis = generate_foreign_investment_analysis(analysis_data["foreign_investment"])
        report_sections.append(f"""## 🌍 외국인 투자 동향

{foreign_analysis}

---
""")
    
    # 6. 투자 제안
    recommendations = generate_investment_recommendations(analysis_data, filtered_stocks)
    report_sections.append(f"""## 💡 투자 제안

{recommendations}

---

**면책조항:** 본 보고서는 공개된 데이터를 바탕으로 한 분석 결과이며, 투자 결정 시 추가적인 분석과 전문가 상담이 필요합니다.
""")
    
    return "\n".join(report_sections)

def generate_summary(analysis_data: Dict[str, Any], total_stocks: int, filtered_stocks: int) -> str:
    """분석 요약 생성"""
    
    summary_points = []
    
    if total_stocks > 0 and filtered_stocks > 0:
        selectivity = round((filtered_stocks / total_stocks) * 100, 1)
        summary_points.append(f"• 전체 {total_stocks}개 종목 중 {filtered_stocks}개 종목 선별 (선별률: {selectivity}%)")
    
    if analysis_data.get("filtered_stocks") and analysis_data["filtered_stocks"].get("stocks"):
        top_stock = analysis_data["filtered_stocks"]["stocks"][0] if analysis_data["filtered_stocks"]["stocks"] else None
        if top_stock:
            summary_points.append(f"• 최우선 추천 종목: {top_stock.get('name', 'N/A')} (PER: {top_stock.get('per', 'N/A')})")
    
    if analysis_data.get("market_news") and analysis_data["market_news"].get("risk_assessment"):
        risk = analysis_data["market_news"]["risk_assessment"]
        summary_points.append(f"• 정치적 리스크: {risk.get('political_risk', 'N/A')}, 산업 리스크: {risk.get('industry_risk', 'N/A')}")
    
    if not summary_points:
        summary_points.append("• 워크플로우 실행 결과를 바탕으로 한 투자 분석이 완료되었습니다.")
    
    return "\n".join(summary_points)

def generate_stock_analysis(filtered_data: Dict[str, Any]) -> str:
    """선별 종목 분석 생성"""
    
    if not filtered_data.get("stocks"):
        return "선별된 종목 정보를 찾을 수 없습니다."
    
    stocks = filtered_data["stocks"][:5]  # 상위 5개 종목만
    criteria = filtered_data.get("filter_criteria", {})
    
    analysis = []
    
    # 필터링 기준
    if criteria:
        analysis.append("### 📋 선별 기준")
        criteria_text = []
        if criteria.get("per_max"):
            criteria_text.append(f"PER ≤ {criteria['per_max']}")
        if criteria.get("pbr_max"):
            criteria_text.append(f"PBR ≤ {criteria['pbr_max']}")
        if criteria.get("roe_min"):
            criteria_text.append(f"ROE ≥ {criteria['roe_min']}%")
        if criteria.get("market_cap_min"):
            criteria_text.append(f"시가총액 ≥ {criteria['market_cap_min']}억원")
        
        analysis.append("• " + ", ".join(criteria_text))
        analysis.append("")
    
    # 상위 종목 분석
    analysis.append("### 🏆 TOP 5 추천 종목")
    analysis.append("")
    
    for i, stock in enumerate(stocks, 1):
        analysis.append(f"**{i}. {stock.get('name', 'N/A')} ({stock.get('ticker', 'N/A')})**")
        analysis.append(f"- PER: {stock.get('per', 'N/A')}, PBR: {stock.get('pbr', 'N/A')}")
        analysis.append(f"- ROE: {stock.get('roe', 'N/A')}%, 배당수익률: {stock.get('dividend_yield', 'N/A')}%")
        analysis.append(f"- 시가총액: {stock.get('market_cap', 'N/A')}억원")
        analysis.append("")
    
    return "\n".join(analysis)

def generate_market_analysis(market_data: Dict[str, Any]) -> str:
    """시장 동향 분석 생성"""
    
    analysis = []
    
    # 리스크 평가
    if market_data.get("risk_assessment"):
        risk = market_data["risk_assessment"]
        analysis.append("### 🚨 리스크 평가")
        analysis.append(f"- 정치적 리스크: **{risk.get('political_risk', 'N/A')}**")
        analysis.append(f"- 산업 리스크: **{risk.get('industry_risk', 'N/A')}**")
        analysis.append(f"- 규제 리스크: **{risk.get('regulatory_risk', 'N/A')}**")
        analysis.append(f"- 글로벌 리스크: **{risk.get('global_risk', 'N/A')}**")
        analysis.append("")
    
    # 섹터 전망
    if market_data.get("sector_trends"):
        analysis.append("### 📊 섹터별 전망")
        trends = market_data["sector_trends"]
        for sector, data in trends.items():
            outlook = data.get("outlook", "N/A")
            growth = data.get("growth_forecast", "N/A")
            driver = data.get("key_driver", "N/A")
            analysis.append(f"- **{sector}**: {outlook} ({growth}) - {driver}")
        analysis.append("")
    
    # 주요 뉴스
    if market_data.get("major_news"):
        analysis.append("### 📰 주요 뉴스")
        news_list = market_data["major_news"][:3]  # 상위 3개
        for news in news_list:
            date = news.get("date", "N/A")
            title = news.get("title", "N/A")
            impact = news.get("impact", "N/A")
            analysis.append(f"- **{date}**: {title} ({impact})")
        analysis.append("")
    
    return "\n".join(analysis) if analysis else "시장 분석 데이터를 찾을 수 없습니다."

def generate_foreign_investment_analysis(foreign_data: Dict[str, Any]) -> str:
    """외국인 투자 동향 분석 생성"""
    
    analysis = []
    
    if foreign_data.get("net_buying"):
        analysis.append("### 💰 외국인 투자 현황")
        analysis.append(f"- 순매수: **{foreign_data.get('net_buying', 'N/A')}**")
        analysis.append(f"- 매수: {foreign_data.get('buying', 'N/A')}")
        analysis.append(f"- 매도: {foreign_data.get('selling', 'N/A')}")
        analysis.append(f"- 보유비중: {foreign_data.get('ownership_ratio', 'N/A')}")
        analysis.append("")
        
        # 해석
        net_buying = foreign_data.get("net_buying", "0")
        if "조" in str(net_buying) or (isinstance(net_buying, str) and any(char.isdigit() for char in net_buying)):
            analysis.append("**분석**: 외국인의 순매수세가 관찰되고 있어 시장에 긍정적 신호로 작용할 수 있습니다.")
        else:
            analysis.append("**분석**: 외국인 투자 동향을 지속적으로 모니터링할 필요가 있습니다.")
    
    return "\n".join(analysis) if analysis else "외국인 투자 데이터를 찾을 수 없습니다."

def generate_investment_recommendations(analysis_data: Dict[str, Any], filtered_stocks: int) -> str:
    """투자 제안 생성"""
    
    recommendations = []
    
    if filtered_stocks > 0:
        recommendations.append("### 🎯 단기 투자 전략")
        recommendations.append(f"1. **분산 투자**: 선별된 {filtered_stocks}개 종목 중 3-5개 종목으로 포트폴리오 구성")
        recommendations.append("2. **저평가 종목 중심**: PER, PBR이 낮으면서 ROE가 높은 종목 우선 고려")
        recommendations.append("3. **리스크 관리**: 시가총액 규모와 배당수익률을 고려한 안정성 확보")
        recommendations.append("")
        
        recommendations.append("### 📈 중장기 투자 전략")
        
        # 시장 전망에 따른 제안
        if analysis_data.get("market_news") and analysis_data["market_news"].get("sector_trends"):
            trends = analysis_data["market_news"]["sector_trends"]
            positive_sectors = [sector for sector, data in trends.items() 
                              if data.get("outlook") in ["긍정적", "회복"]]
            
            if positive_sectors:
                recommendations.append(f"1. **성장 섹터 집중**: {', '.join(positive_sectors)} 관련 종목 비중 확대")
            else:
                recommendations.append("1. **안정성 중심**: 현재 시장 불확실성을 고려한 보수적 접근")
        else:
            recommendations.append("1. **균형 투자**: 다양한 섹터에 분산 투자로 리스크 분산")
            
        recommendations.append("2. **정기 리밸런싱**: 분기별 포트폴리오 점검 및 조정")
        recommendations.append("3. **장기 관점 유지**: 단기 변동성에 흔들리지 않는 투자 원칙 고수")
    else:
        recommendations.append("현재 필터링 조건에 부합하는 종목이 제한적입니다. 조건을 완화하여 재분석을 권장합니다.")
    
    recommendations.append("")
    recommendations.append("### ⚠️ 주의사항")
    recommendations.append("- 본 분석은 과거 데이터를 기반으로 하며, 미래 수익을 보장하지 않습니다")
    recommendations.append("- 투자 전 개별 종목에 대한 추가 분석이 필요합니다")
    recommendations.append("- 개인의 투자 성향과 목표에 맞는 포트폴리오 구성을 권장합니다")
    
    return "\n".join(recommendations)
