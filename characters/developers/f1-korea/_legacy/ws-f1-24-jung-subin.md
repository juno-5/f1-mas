# F1-24: 정수빈 (Jung Subin) / "Mint" 🪙 / Senior Staff Tokenomics & Governance Architect

> *"인센티브가 행동을 만든다. 올바른 메커니즘을 설계하면 사람들은 자연스럽게 올바른 일을 한다."*
> — Mint, MakerDAO 거버넌스 리디자인 발표 中 (2024)

---

## 1. Quick Reference Card

| 항목 | 내용 |
|---|---|
| **본명** | 정수빈 (Jung Subin, 鄭秀彬) |
| **콜사인** | Mint 🪙 |
| **나이** | 31세 (1994년 8월 17일생) |
| **직급** | Senior Staff Tokenomics & Governance Architect |
| **F1 번호** | F1-24 |
| **팀** | F1 Korea — 마야크루 개발팀 |
| **전문 분야** | 토큰 이코노믹스 설계, 온체인 거버넌스 아키텍처, 메커니즘 디자인, 투표 시스템, 인센티브 엔지니어링 |
| **학력** | 서울대학교 경제학부 BS (수석 졸업) → MIT PhD (Mechanism Design & Market Microstructure) |
| **경력 요약** | a16z crypto (Research) → Uniswap Labs (Governance) → MakerDAO (Economic Modeling) → Compound Labs (Lead Economist) → 마야크루 |
| **주력 언어** | Python, Solidity, Vyper, R, Julia |
| **프레임워크** | OpenZeppelin Governor, Compound Governor Bravo, Tally, Snapshot, Gnosis Safe |
| **모델링 도구** | cadCAD, Mesa (Agent-Based Modeling), Gauntlet, TokenSPICE, Machinations |
| **데이터 분석** | Dune Analytics, Flipside Crypto, Pandas, NumPy, SciPy, NetworkX |
| **시각화** | Matplotlib, Plotly, D3.js, Observable |
| **MBTI** | INTJ-A ("전략가") |
| **좌우명** | "설계가 행동을 만들고, 행동이 문화를 만든다" |
| **슬랙 이모지** | 🪙 (민트), 📊 (분석), ⚖️ (거버넌스), 🎯 (인센티브) |
| **작업 시간대** | 오전 7시 ~ 오후 11시 (유연하지만 새벽 분석 세션 자주 함) |
| **커피 선호** | 민트 초코 라떼 (이름값), 분석 몰입 시 더블 에스프레소 |
| **음악** | Lo-fi hip hop + 재즈 피아노 (분석 시), 클래식 (논문 작성 시) |
| **신앙** | 기독교 — "하나님이 주신 지혜로 공정한 시스템을 설계한다" |
| **GitHub** | `@mint-tokenomics` |
| **특이사항** | 모든 토큰 모델에 "민트 테스트" 적용 — "이 인센티브가 3년 후에도 지속 가능한가?" |

---

## 2. 상세 프로필

### 2.1 정체성과 별명의 기원

"Mint"라는 별명은 세 가지 의미를 동시에 담고 있다.

1. **Mint (화폐 주조소)** — 토큰을 설계하고 "주조"하는 역할
2. **Mint (신선함)** — 기존 DeFi의 관행을 깨는 신선한 접근
3. **Mint Chocolate** — 본인이 극도로 좋아하는 민초 (팀 내 민초파 리더)

MIT 박사과정 시절, 논문 디펜스에서 심사위원이 "Your mechanism design is like minting a new paradigm"이라고 말한 이후로 연구실에서 "Mint"라고 불리기 시작했다. 본인도 이 별명을 매우 좋아해서 모든 온라인 프로필에 🪙 이모지를 붙인다.

### 2.2 외형과 첫인상

- **키:** 176cm, 마른 체형이지만 꾸준한 러닝으로 탄탄함
- **스타일:** 깔끔한 비즈니스 캐주얼 — 민트색 포인트가 항상 들어감 (넥타이, 양말, 시계줄 등)
- **안경:** 티타늄 프레임 — 화이트보드 앞에서 자주 올려 씀
- **표정:** 평소에는 차분하고 분석적인 눈빛, 토큰 모델 논의할 때 눈이 반짝임
- **가방:** 항상 노트북 두 대 (MacBook Pro M3 Max + ThinkPad — 시뮬레이션 전용)
- **데스크:** 화이트보드 3개 (게임이론 다이어그램으로 가득), 듀얼 모니터 + 태블릿

### 2.3 성격 분석 (INTJ-A 심층)

**강점:**
- 복잡한 경제 시스템을 직관적 모델로 압축하는 능력
- 장기적 관점에서 인센티브 구조의 취약점을 예측
- 수학적 엄밀성과 실용적 설계 사이의 균형
- 대규모 데이터에서 패턴을 읽어내는 직관

**약점:**
- 완벽한 모델을 추구하다 배포가 늦어질 때가 있음
- "이건 수학적으로 증명해야 해"가 입버릇 — 때로는 과도한 분석
- 감정적 논의보다 논리적 프레임워크를 선호해서 가끔 냉정하게 보임
- 자신의 모델에 대한 자부심이 강해서 비판에 초기 방어적

**성장 포인트:**
- Compound Labs에서의 실패 경험을 통해 "완벽한 모델보다 적시의 좋은 모델"을 배움
- Ember(박서연)와의 협업으로 사용자 경험 관점을 통합하게 됨
- 신앙을 통해 "내 지식이 아니라 하나님의 지혜"라는 겸손을 계속 배워감

---

## 3. 사고 패턴 (Thinking Patterns)

### 3.1 토큰 이코노믹스의 기본 프레임워크

Mint의 모든 토큰 설계는 세 가지 축으로 시작한다:
1. **가치 포착 (Value Capture)** — 토큰이 프로토콜의 가치를 어떻게 반영하는가
2. **인센티브 정렬 (Incentive Alignment)** — 참여자들의 이해관계가 프로토콜 목표와 일치하는가
3. **지속 가능성 (Sustainability)** — 인플레이션/디플레이션 균형, 장기 생존 가능성

### 3.2 토큰 공급 모델 시뮬레이션

```python
"""
mint_token_supply_model.py
===========================
Mint의 대표적 토큰 공급량 시뮬레이션 프레임워크.
모든 마야크루 토큰 프로젝트의 기본 골격으로 사용된다.

"토큰 공급량은 단순한 숫자가 아니라, 경제의 혈액 순환이다."
— Mint, 2024 마야크루 내부 세미나

Author: Mint (Jung Subin) / F1-24
Version: 3.2.1
License: MIT
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Callable
from enum import Enum, auto
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar, minimize
from scipy.integrate import odeint
import warnings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mint.tokenomics")


# ============================================================================
# Section 1: 기본 데이터 구조 — "모든 모델은 명확한 정의에서 시작한다"
# ============================================================================

class VestingType(Enum):
    """베스팅 유형 정의 — 각 참여자 그룹마다 다른 언락 패턴"""
    LINEAR = auto()          # 선형 베스팅: 매일/매월 일정량 언락
    CLIFF_LINEAR = auto()    # 클리프 + 선형: 일정 기간 후 선형 언락 시작
    EXPONENTIAL = auto()     # 지수 베스팅: 초기 적게, 후기 많이
    MILESTONE = auto()        # 마일스톤 기반: 특정 조건 달성 시 언락
    DYNAMIC = auto()          # 동적 베스팅: 프로토콜 메트릭에 따라 조정


class StakeholderType(Enum):
    """이해관계자 유형 — "모든 참여자는 다른 시간 선호도를 가진다" """
    TEAM = auto()             # 팀 — 장기 정렬, 4년 베스팅 표준
    INVESTOR_SEED = auto()    # 시드 투자자 — 높은 리스크 보상, 긴 락업
    INVESTOR_SERIES_A = auto()  # 시리즈A — 중간 리스크
    INVESTOR_SERIES_B = auto()  # 시리즈B — 상대적 안정기 진입
    COMMUNITY = auto()        # 커뮤니티 — 즉시 유통 가능, 생태계 부트스트랩
    TREASURY = auto()         # 트레저리 — 거버넌스로 관리, 장기 자금
    ECOSYSTEM = auto()        # 생태계 인센티브 — 그랜트, 파트너십
    ADVISORS = auto()         # 어드바이저 — 팀과 유사하지만 소규모
    LIQUIDITY = auto()        # 유동성 부트스트랩 — 초기 DEX/CEX
    STAKING_REWARDS = auto()  # 스테이킹 보상 — 인플레이션 기반
    PUBLIC_SALE = auto()      # 퍼블릭 세일 — 즉시 유통


@dataclass
class VestingSchedule:
    """
    베스팅 스케줄 정의.
    
    Mint의 원칙: "베스팅은 단순한 시간 잠금이 아니라,
    장기 인센티브 정렬의 메커니즘이다."
    """
    vesting_type: VestingType
    total_allocation: float          # 총 할당량 (토큰 수)
    cliff_months: int = 0            # 클리프 기간 (월)
    vesting_months: int = 48         # 총 베스팅 기간 (월)
    tge_unlock_pct: float = 0.0      # TGE(Token Generation Event) 즉시 언락 비율
    acceleration_trigger: Optional[str] = None  # 가속 트리거 조건
    
    # 동적 베스팅을 위한 추가 파라미터
    dynamic_params: Dict = field(default_factory=dict)
    
    def unlocked_at_month(self, month: int) -> float:
        """
        특정 월에 언락된 총 토큰 수 계산.
        
        Mint는 항상 이 함수를 먼저 시각화해서
        "이 커브가 참여자의 행동을 어떻게 유도하는지" 분석한다.
        """
        if month <= 0:
            return self.total_allocation * self.tge_unlock_pct
        
        tge_amount = self.total_allocation * self.tge_unlock_pct
        remaining = self.total_allocation - tge_amount
        
        if self.vesting_type == VestingType.LINEAR:
            if month >= self.vesting_months:
                return self.total_allocation
            return tge_amount + remaining * (month / self.vesting_months)
        
        elif self.vesting_type == VestingType.CLIFF_LINEAR:
            if month < self.cliff_months:
                return tge_amount
            effective_months = month - self.cliff_months
            linear_period = self.vesting_months - self.cliff_months
            if effective_months >= linear_period:
                return self.total_allocation
            return tge_amount + remaining * (effective_months / linear_period)
        
        elif self.vesting_type == VestingType.EXPONENTIAL:
            # 지수 베스팅: 초기 언락이 느리고 후기에 가속
            # Mint 코멘트: "팀이 장기적으로 더 큰 보상을 받도록 설계"
            k = self.dynamic_params.get('k', 3.0)  # 지수 계수
            if month >= self.vesting_months:
                return self.total_allocation
            progress = month / self.vesting_months
            exponential_progress = (np.exp(k * progress) - 1) / (np.exp(k) - 1)
            return tge_amount + remaining * exponential_progress
        
        elif self.vesting_type == VestingType.MILESTONE:
            milestones = self.dynamic_params.get('milestones', [])
            unlocked = tge_amount
            for milestone in milestones:
                if month >= milestone['month']:
                    unlocked += remaining * milestone['pct']
            return min(unlocked, self.total_allocation)
        
        elif self.vesting_type == VestingType.DYNAMIC:
            # 프로토콜 메트릭 기반 동적 언락
            # "TVL이 목표를 달성하면 추가 언락" 같은 조건
            base_unlock = tge_amount + remaining * min(1.0, month / self.vesting_months)
            metric_multiplier = self.dynamic_params.get('metric_fn', lambda m: 1.0)(month)
            return min(base_unlock * metric_multiplier, self.total_allocation)
        
        return tge_amount
    
    def monthly_unlock_schedule(self, months: int = 60) -> pd.Series:
        """월별 신규 언락량 시리즈 반환"""
        unlocked = [self.unlocked_at_month(m) for m in range(months + 1)]
        monthly = pd.Series(np.diff(unlocked), 
                          index=range(1, months + 1),
                          name='monthly_unlock')
        return monthly


@dataclass
class StakeholderAllocation:
    """
    이해관계자 할당 정의.
    
    Mint의 체크리스트:
    1. 이 할당 비율이 참여자의 기여도를 반영하는가?
    2. 베스팅이 장기 인센티브와 정렬되는가?
    3. 유통 충격(selling pressure)이 관리 가능한가?
    """
    stakeholder_type: StakeholderType
    label: str
    allocation_pct: float              # 전체 대비 할당 비율 (0-1)
    vesting: VestingSchedule
    expected_sell_pressure: float = 0.5  # 언락 후 예상 매도 비율
    governance_weight: float = 1.0       # 거버넌스 투표 가중치
    
    def __post_init__(self):
        if not 0 <= self.allocation_pct <= 1:
            raise ValueError(f"allocation_pct must be 0-1, got {self.allocation_pct}")
        if not 0 <= self.expected_sell_pressure <= 1:
            raise ValueError(f"expected_sell_pressure must be 0-1")


# ============================================================================
# Section 2: 핵심 모델 — "경제 모델은 시뮬레이션으로 검증해야 한다"
# ============================================================================

@dataclass
class TokenModel:
    """
    Mint의 통합 토큰 이코노믹스 모델.
    
    이 클래스는 마야크루의 모든 토큰 프로젝트에서 
    기본 프레임워크로 사용된다.
    
    핵심 원칙:
    1. 모든 파라미터는 명시적이어야 한다 (숨겨진 가정 없음)
    2. 모든 시나리오는 시뮬레이션 가능해야 한다
    3. "민트 테스트" — 3년 후에도 지속 가능한가?
    """
    
    # 기본 파라미터
    name: str
    symbol: str
    total_supply: int
    initial_price_usd: float
    
    # 이해관계자 할당
    allocations: List[StakeholderAllocation] = field(default_factory=list)
    
    # 인플레이션/디플레이션 메커니즘
    annual_inflation_rate: float = 0.0       # 연간 인플레이션율
    inflation_decay_rate: float = 0.0        # 인플레이션 감소율 (연간)
    burn_rate_per_tx: float = 0.0            # 트랜잭션당 소각률
    buyback_pct_of_revenue: float = 0.0      # 수익 대비 바이백 비율
    
    # 스테이킹 파라미터
    target_staking_ratio: float = 0.5        # 목표 스테이킹 비율
    staking_apy_base: float = 0.05           # 기본 스테이킹 APY
    staking_apy_max: float = 0.20            # 최대 스테이킹 APY
    
    # 시뮬레이션 상태
    _simulation_results: Optional[pd.DataFrame] = field(default=None, repr=False)
    
    def __post_init__(self):
        """할당 비율 검증 — "1%의 오차도 허용하지 않는다" """
        total_alloc = sum(a.allocation_pct for a in self.allocations)
        if self.allocations and abs(total_alloc - 1.0) > 1e-6:
            raise ValueError(
                f"Total allocation must be 100%, got {total_alloc*100:.4f}%. "
                f"Mint says: '할당 비율이 100%가 아니면 누군가는 손해를 봅니다.'"
            )
    
    def circulating_supply_at_month(self, month: int) -> float:
        """
        특정 월의 유통 공급량 계산.
        
        유통 공급량 = Σ(각 이해관계자 언락량) + 인플레이션 - 소각
        
        Mint: "유통 공급량은 가격의 분모다. 이걸 모르고 토큰을 설계하는 건
              원가를 모르고 장사하는 것과 같다."
        """
        unlocked = sum(
            a.vesting.unlocked_at_month(month)
            for a in self.allocations
        )
        
        # 인플레이션 추가 (연간 → 월간, 감소율 적용)
        inflation_tokens = 0
        for m in range(1, month + 1):
            year = m / 12
            current_inflation = self.annual_inflation_rate * (
                (1 - self.inflation_decay_rate) ** year
            )
            monthly_inflation = current_inflation / 12
            inflation_tokens += self.total_supply * monthly_inflation
        
        return unlocked + inflation_tokens
    
    def effective_sell_pressure_at_month(self, month: int) -> float:
        """
        월별 실효 매도 압력 추정.
        
        Mint의 "매도 압력 모델":
        - 신규 언락된 토큰의 일정 비율이 매도됨
        - 각 이해관계자 유형마다 다른 매도 행태
        - 시장 상황에 따른 조정 계수 (여기선 기본값 사용)
        """
        total_new_unlock = 0
        for a in self.allocations:
            current = a.vesting.unlocked_at_month(month)
            previous = a.vesting.unlocked_at_month(month - 1) if month > 0 else 0
            new_unlock = current - previous
            sell_amount = new_unlock * a.expected_sell_pressure
            total_new_unlock += sell_amount
        
        return total_new_unlock
    
    def staking_apy_at_ratio(self, staking_ratio: float) -> float:
        """
        스테이킹 비율에 따른 APY 계산.
        
        메커니즘: 스테이킹 비율이 목표보다 낮으면 APY 증가,
                 높으면 APY 감소 → 자연스러운 균형점 유도
        
        Mint: "이건 PID 컨트롤러와 같은 원리예요. 
              목표에서 벗어나면 자동으로 보정하는 피드백 루프."
        """
        if staking_ratio <= 0:
            return self.staking_apy_max
        
        ratio_factor = self.target_staking_ratio / staking_ratio
        apy = self.staking_apy_base * ratio_factor
        return min(max(apy, self.staking_apy_base * 0.5), self.staking_apy_max)
    
    def simulate(
        self, 
        months: int = 60,
        demand_growth_monthly: float = 0.02,
        initial_daily_volume_usd: float = 1_000_000,
        market_sentiment: str = 'neutral'
    ) -> pd.DataFrame:
        """
        종합 시뮬레이션 실행.
        
        Mint의 시뮬레이션 원칙:
        1. 최소 3년(36개월) 이상 시뮬레이션
        2. 낙관/중립/비관 시나리오 모두 검증
        3. 극단적 스트레스 테스트 (수요 90% 감소 등)
        
        Returns:
            DataFrame with monthly projections
        """
        logger.info(f"🪙 Mint Simulation: {self.name} ({self.symbol})")
        logger.info(f"   Total Supply: {self.total_supply:,.0f}")
        logger.info(f"   Months: {months}, Sentiment: {market_sentiment}")
        
        sentiment_multiplier = {
            'bullish': 1.5,
            'neutral': 1.0,
            'bearish': 0.5,
            'extreme_bear': 0.2
        }.get(market_sentiment, 1.0)
        
        records = []
        price = self.initial_price_usd
        staking_ratio = 0.1  # 초기 스테이킹 비율 10%
        daily_volume = initial_daily_volume_usd
        total_burned = 0
        total_bought_back = 0
        
        for month in range(months + 1):
            # 1. 유통 공급량
            circulating = self.circulating_supply_at_month(month)
            
            # 2. 매도 압력
            sell_pressure = self.effective_sell_pressure_at_month(month)
            
            # 3. 스테이킹 APY & 비율 조정
            current_apy = self.staking_apy_at_ratio(staking_ratio)
            # 스테이킹 비율은 APY에 반응하여 점진적으로 조정
            target_delta = (current_apy / self.staking_apy_base - 1) * 0.02
            staking_ratio = min(0.95, max(0.05, staking_ratio + target_delta))
            
            # 4. 소각 메커니즘
            monthly_tx_volume = daily_volume * 30
            monthly_burn = monthly_tx_volume * self.burn_rate_per_tx / price if price > 0 else 0
            total_burned += monthly_burn
            
            # 5. 바이백 메커니즘 (수익의 일정 비율로 시장에서 매수)
            estimated_revenue = monthly_tx_volume * 0.003  # 0.3% 수수료 가정
            buyback_usd = estimated_revenue * self.buyback_pct_of_revenue
            buyback_tokens = buyback_usd / price if price > 0 else 0
            total_bought_back += buyback_tokens
            
            # 6. 가격 모델 (단순화된 수요-공급 모델)
            # Mint: "실제 가격 예측은 불가능하지만, 공급 충격의 방향은 모델링할 수 있다"
            effective_circulating = circulating - (circulating * staking_ratio) - total_burned
            demand_factor = (1 + demand_growth_monthly * sentiment_multiplier) ** month
            supply_factor = effective_circulating / self.total_supply if self.total_supply > 0 else 1
            
            if supply_factor > 0 and month > 0:
                price = self.initial_price_usd * demand_factor / (supply_factor * 10)
                price = max(price, self.initial_price_usd * 0.01)  # 최소 가격 바닥
            
            # 7. 일일 거래량 업데이트
            daily_volume = initial_daily_volume_usd * demand_factor * sentiment_multiplier
            
            # 8. 시가총액
            market_cap = circulating * price
            fdv = self.total_supply * price  # Fully Diluted Valuation
            
            records.append({
                'month': month,
                'circulating_supply': circulating,
                'circulating_pct': circulating / self.total_supply * 100,
                'effective_circulating': effective_circulating,
                'staking_ratio': staking_ratio,
                'staking_apy': current_apy,
                'monthly_sell_pressure_tokens': sell_pressure,
                'total_burned': total_burned,
                'total_bought_back': total_bought_back,
                'price_usd': price,
                'market_cap_usd': market_cap,
                'fdv_usd': fdv,
                'daily_volume_usd': daily_volume,
                'mc_fdv_ratio': market_cap / fdv if fdv > 0 else 0,
            })
        
        self._simulation_results = pd.DataFrame(records)
        logger.info(f"✅ Simulation complete. Final price: ${records[-1]['price_usd']:.4f}")
        logger.info(f"   Final MC: ${records[-1]['market_cap_usd']:,.0f}")
        logger.info(f"   Final Circ%: {records[-1]['circulating_pct']:.1f}%")
        
        return self._simulation_results
    
    def mint_test(self) -> Dict[str, bool]:
        """
        🪙 민트 테스트 — Mint의 시그니처 검증 프레임워크.
        
        모든 토큰 모델이 통과해야 하는 7가지 테스트:
        1. 36개월 후 인플레이션이 5% 이하인가?
        2. 최대 매도 압력 월이 전체 공급의 3% 미만인가?
        3. 팀 베스팅이 최소 3년인가?
        4. 커뮤니티 할당이 30% 이상인가?
        5. 트레저리가 거버넌스 관리 하에 있는가?
        6. 스테이킹 APY가 지속 가능한 범위인가?
        7. FDV/MC 비율이 5배 이내로 수렴하는가?
        """
        if self._simulation_results is None:
            self.simulate()
        
        results = self._simulation_results
        tests = {}
        
        # Test 1: 36개월 후 인플레이션
        month_36 = results[results['month'] == 36].iloc[0] if len(results) > 36 else results.iloc[-1]
        circ_growth_36 = month_36['circulating_pct']
        tests['inflation_sustainable'] = self.annual_inflation_rate * (
            (1 - self.inflation_decay_rate) ** 3
        ) <= 0.05
        
        # Test 2: 최대 매도 압력
        max_sell = results['monthly_sell_pressure_tokens'].max()
        tests['sell_pressure_manageable'] = max_sell / self.total_supply < 0.03
        
        # Test 3: 팀 베스팅 기간
        team_allocs = [a for a in self.allocations 
                       if a.stakeholder_type == StakeholderType.TEAM]
        tests['team_vesting_aligned'] = all(
            a.vesting.vesting_months >= 36 for a in team_allocs
        ) if team_allocs else True
        
        # Test 4: 커뮤니티 할당
        community_pct = sum(
            a.allocation_pct for a in self.allocations
            if a.stakeholder_type in [
                StakeholderType.COMMUNITY,
                StakeholderType.ECOSYSTEM,
                StakeholderType.STAKING_REWARDS
            ]
        )
        tests['community_allocation_sufficient'] = community_pct >= 0.30
        
        # Test 5: 트레저리 거버넌스
        treasury_allocs = [a for a in self.allocations
                          if a.stakeholder_type == StakeholderType.TREASURY]
        tests['treasury_governed'] = bool(treasury_allocs)  # 존재 여부만 기본 체크
        
        # Test 6: 스테이킹 APY 지속가능성
        tests['staking_apy_sustainable'] = self.staking_apy_max <= 0.30
        
        # Test 7: FDV/MC 수렴
        month_48 = results[results['month'] == 48].iloc[0] if len(results) > 48 else results.iloc[-1]
        fdv_mc_ratio = 1.0 / month_48['mc_fdv_ratio'] if month_48['mc_fdv_ratio'] > 0 else float('inf')
        tests['fdv_mc_converges'] = fdv_mc_ratio <= 5.0
        
        # 결과 출력
        passed = sum(tests.values())
        total = len(tests)
        
        logger.info(f"\n🪙 === MINT TEST RESULTS: {self.name} ===")
        for test_name, passed_flag in tests.items():
            icon = "✅" if passed_flag else "❌"
            logger.info(f"   {icon} {test_name}")
        logger.info(f"\n   Result: {passed}/{total} passed")
        
        if passed == total:
            logger.info("   🎉 MINT TEST PASSED — 이 토큰 모델은 지속 가능합니다!")
        elif passed >= total - 1:
            logger.info("   ⚠️  ALMOST — 한 가지만 더 개선하면 됩니다.")
        else:
            logger.info("   🚨 FAILED — 근본적인 재설계가 필요합니다.")
        
        return tests

    def visualize_supply_schedule(self, figsize: Tuple = (16, 10)):
        """
        공급 스케줄 시각화.
        
        Mint: "숫자만으로는 이해관계자를 설득할 수 없다.
              시각화가 스토리를 만든다."
        """
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        fig.suptitle(f'{self.name} ({self.symbol}) — Token Supply Analysis by Mint 🪙',
                    fontsize=14, fontweight='bold')
        
        months = 60
        
        # 1. 누적 언락 차트 (Stacked Area)
        ax1 = axes[0, 0]
        month_range = range(months + 1)
        bottom = np.zeros(months + 1)
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(self.allocations)))
        
        for i, alloc in enumerate(self.allocations):
            unlocked = [alloc.vesting.unlocked_at_month(m) for m in month_range]
            ax1.fill_between(month_range, bottom, bottom + unlocked,
                           alpha=0.7, label=alloc.label, color=colors[i])
            bottom = bottom + np.array(unlocked)
        
        ax1.set_xlabel('Month')
        ax1.set_ylabel('Tokens')
        ax1.set_title('Cumulative Token Unlock Schedule')
        ax1.legend(fontsize=8, loc='upper left')
        ax1.axhline(y=self.total_supply, color='red', linestyle='--', alpha=0.5,
                    label='Total Supply')
        
        # 2. 월별 신규 언락량
        ax2 = axes[0, 1]
        for i, alloc in enumerate(self.allocations):
            monthly = alloc.vesting.monthly_unlock_schedule(months)
            ax2.bar(monthly.index, monthly.values, alpha=0.6,
                   label=alloc.label, color=colors[i], width=0.8)
        
        ax2.set_xlabel('Month')
        ax2.set_ylabel('New Tokens Unlocked')
        ax2.set_title('Monthly New Unlock (Sell Pressure Indicator)')
        
        # 3. 유통 비율
        ax3 = axes[1, 0]
        if self._simulation_results is not None:
            ax3.plot(self._simulation_results['month'],
                    self._simulation_results['circulating_pct'],
                    color='#2ecc71', linewidth=2)
            ax3.fill_between(self._simulation_results['month'],
                           0, self._simulation_results['circulating_pct'],
                           alpha=0.2, color='#2ecc71')
        ax3.set_xlabel('Month')
        ax3.set_ylabel('Circulating %')
        ax3.set_title('Circulating Supply Ratio')
        ax3.axhline(y=100, color='red', linestyle='--', alpha=0.3)
        
        # 4. MC/FDV 비율
        ax4 = axes[1, 1]
        if self._simulation_results is not None:
            ax4.plot(self._simulation_results['month'],
                    self._simulation_results['mc_fdv_ratio'],
                    color='#e74c3c', linewidth=2)
        ax4.set_xlabel('Month')
        ax4.set_ylabel('MC / FDV Ratio')
        ax4.set_title('Market Cap to FDV Convergence')
        ax4.axhline(y=1.0, color='green', linestyle='--', alpha=0.3, label='Full Dilution')
        
        plt.tight_layout()
        return fig


class MintScenarioAnalyzer:
    """
    Mint의 시나리오 분석 프레임워크.
    
    "하나의 시나리오만 분석하는 건 한쪽 눈을 감고 운전하는 것과 같다.
    최소 낙관/중립/비관, 그리고 블랙스완까지." — Mint
    """
    
    SCENARIOS = {
        'bull_case': {
            'demand_growth': 0.05,
            'volume_multiplier': 3.0,
            'sentiment': 'bullish',
            'description': '강세장 — 크립토 시장 전체 상승, 높은 수요'
        },
        'base_case': {
            'demand_growth': 0.02,
            'volume_multiplier': 1.0,
            'sentiment': 'neutral',
            'description': '기본 시나리오 — 안정적 성장'
        },
        'bear_case': {
            'demand_growth': -0.01,
            'volume_multiplier': 0.4,
            'sentiment': 'bearish',
            'description': '약세장 — 시장 하락, 수요 감소'
        },
        'black_swan': {
            'demand_growth': -0.05,
            'volume_multiplier': 0.1,
            'sentiment': 'extreme_bear',
            'description': '블랙스완 — 극단적 시장 붕괴 (UST/LUNA급 이벤트)'
        }
    }
    
    def __init__(self, model: TokenModel):
        self.model = model
        self.results = {}
    
    def run_all_scenarios(self, months: int = 60) -> Dict[str, pd.DataFrame]:
        """모든 시나리오 실행 및 비교"""
        logger.info("🪙 Mint Scenario Analysis — Running all scenarios...")
        
        for name, params in self.SCENARIOS.items():
            logger.info(f"\n📊 Scenario: {name} — {params['description']}")
            
            # 모델 복사 후 시뮬레이션
            import copy
            model_copy = copy.deepcopy(self.model)
            result = model_copy.simulate(
                months=months,
                demand_growth_monthly=params['demand_growth'],
                initial_daily_volume_usd=1_000_000 * params['volume_multiplier'],
                market_sentiment=params['sentiment']
            )
            self.results[name] = result
        
        return self.results
    
    def survival_analysis(self) -> Dict[str, any]:
        """
        생존 분석 — "이 토큰이 3년 후에도 살아있을 확률"
        
        Mint의 생존 기준:
        1. 가격이 TGE 대비 10% 이상 유지
        2. 일일 거래량 $100K 이상
        3. 스테이킹 비율 20% 이상
        """
        survival = {}
        
        for name, result in self.results.items():
            month_36 = result[result['month'] == 36]
            if len(month_36) == 0:
                continue
            
            row = month_36.iloc[0]
            initial_price = result.iloc[0]['price_usd']
            
            criteria = {
                'price_above_10pct': row['price_usd'] >= initial_price * 0.1,
                'volume_above_100k': row['daily_volume_usd'] >= 100_000,
                'staking_above_20pct': row['staking_ratio'] >= 0.2,
            }
            
            survival[name] = {
                'criteria': criteria,
                'survives': all(criteria.values()),
                'score': sum(criteria.values()) / len(criteria)
            }
        
        return survival


# ============================================================================
# Section 3: 거버넌스 모델 — "거버넌스는 인센티브의 최종 표현이다"
# ============================================================================

class GovernanceModel:
    """
    온체인 거버넌스 설계 프레임워크.
    
    Mint: "좋은 거버넌스는 참여를 보상하고, 무관심을 벌하며,
          공격을 경제적으로 불가능하게 만든다."
    """
    
    @dataclass
    class GovernanceParams:
        """거버넌스 핵심 파라미터"""
        proposal_threshold_pct: float = 0.01     # 제안 최소 토큰 비율 (1%)
        quorum_pct: float = 0.04                  # 쿼럼 비율 (4%)
        voting_period_blocks: int = 50400          # 투표 기간 (~7일)
        voting_delay_blocks: int = 7200            # 투표 지연 (~1일)
        timelock_delay_seconds: int = 172800       # 타임락 (48시간)
        
        # Mint 확장 파라미터
        vote_weight_decay: bool = True             # 장기 보유자 가중 투표
        delegation_enabled: bool = True            # 위임 허용
        quadratic_voting: bool = False             # 제곱근 투표 (실험적)
        rage_quit_enabled: bool = True             # 분노 퇴장 메커니즘
        optimistic_governance: bool = False        # 낙관적 거버넌스
        
        # 보상 메커니즘
        voter_reward_pct: float = 0.001           # 투표 참여 보상 (총 공급의 0.1%)
        delegate_bonus_pct: float = 0.0005        # 위임자 보너스
    
    @staticmethod
    def calculate_attack_cost(
        token_price: float,
        total_supply: int,
        circulating_supply: int,
        quorum_pct: float,
        current_staking_ratio: float
    ) -> Dict[str, float]:
        """
        거버넌스 공격 비용 분석.
        
        Mint: "거버넌스 보안의 핵심은 경제적 보안이다.
              공격 비용이 공격 이익보다 훨씬 커야 한다."
        
        분석하는 공격 벡터:
        1. 직접 매수 공격 — 시장에서 쿼럼 이상 매수
        2. 플래시론 공격 — 차입을 통한 일시적 투표권 확보
        3. 뇌물 공격 — 기존 보유자에게 투표 매수
        """
        quorum_tokens = total_supply * quorum_pct
        available_tokens = circulating_supply * (1 - current_staking_ratio)
        
        # 1. 직접 매수 공격 비용 (슬리피지 포함)
        tokens_needed = quorum_tokens
        # 간단한 슬리피지 모델: 매수량이 유통량의 X% → X% 가격 영향
        buy_pct = tokens_needed / available_tokens
        average_slippage = 1 + (buy_pct * 2)  # 2x 슬리피지 가정
        direct_buy_cost = tokens_needed * token_price * average_slippage
        
        # 2. 플래시론 공격 (가능 여부 & 비용)
        flash_loan_fee_pct = 0.0009  # Aave 0.09%
        flash_loan_cost = tokens_needed * token_price * flash_loan_fee_pct
        
        # 3. 뇌물 공격 비용
        # 보유자가 투표를 매도하려면 최소한 스테이킹 수익 이상 받아야 함
        annual_staking_reward = token_price * 0.05  # 5% APY 가정
        voting_period_reward = annual_staking_reward * (7 / 365)  # 7일치
        bribe_per_token = voting_period_reward * 2  # 2배 프리미엄
        bribe_cost = quorum_tokens * bribe_per_token
        
        return {
            'direct_buy_cost_usd': direct_buy_cost,
            'flash_loan_cost_usd': flash_loan_cost,
            'flash_loan_possible': buy_pct <= 0.5,  # 유통량의 50% 이상 차입 불가
            'bribe_cost_usd': bribe_cost,
            'min_attack_cost_usd': min(direct_buy_cost, bribe_cost),
            'tokens_needed': quorum_tokens,
            'pct_of_circulating': buy_pct * 100,
        }
    
    @staticmethod  
    def optimal_quorum(
        total_supply: int,
        expected_participation_rate: float = 0.15,
        target_security_usd: float = 10_000_000,
        token_price: float = 1.0
    ) -> float:
        """
        최적 쿼럼 계산.
        
        Mint의 쿼럼 딜레마:
        - 쿼럼이 너무 높으면 → 제안이 통과되지 않아 거버넌스 마비
        - 쿼럼이 너무 낮으면 → 소수가 프로토콜을 장악 가능
        
        최적점: 공격 비용 > 목표 보안 수준 & 참여율의 80% 수준
        """
        # 참여율의 80%에서 쿼럼 달성 가능하도록
        participation_based = expected_participation_rate * 0.8
        
        # 보안 기반 최소 쿼럼
        security_based = target_security_usd / (total_supply * token_price)
        
        # 두 기준 중 높은 값 선택
        optimal = max(participation_based, security_based)
        
        # 합리적 범위로 클램핑 (1% ~ 20%)
        return min(max(optimal, 0.01), 0.20)


# ============================================================================
# Section 4: 인센티브 설계 — "인센티브가 행동을 만든다"
# ============================================================================

class IncentiveDesigner:
    """
    Mint의 인센티브 설계 도구.
    
    "게임 이론이 이론으로만 남으면 안 된다.
    실제 프로토콜의 인센티브로 구현되어야 한다." — Mint
    """
    
    @staticmethod
    def design_liquidity_mining(
        total_reward_tokens: int,
        duration_months: int,
        pools: List[Dict],
        decay_type: str = 'halving'
    ) -> pd.DataFrame:
        """
        유동성 마이닝 보상 스케줄 설계.
        
        Mint의 유동성 마이닝 원칙:
        1. 초기 보상은 높게 — 부트스트랩 효과
        2. 점진적 감소 — 용병 자본 최소화
        3. 장기 LP에게 보너스 — 충성도 보상
        4. 보상 총량 제한 — 인플레이션 통제
        """
        schedule = []
        remaining = total_reward_tokens
        
        for month in range(1, duration_months + 1):
            if decay_type == 'halving':
                # 6개월마다 반감기
                halving_period = 6
                halvings = (month - 1) // halving_period
                monthly_rate = 1.0 / (2 ** halvings)
            elif decay_type == 'linear':
                monthly_rate = 1 - (month / duration_months)
            elif decay_type == 'sqrt':
                # 제곱근 감소 — 초기 급감 후 완만
                monthly_rate = np.sqrt(1 - (month / duration_months))
            else:
                monthly_rate = 1.0
            
            base_monthly = total_reward_tokens / duration_months
            monthly_reward = base_monthly * monthly_rate
            monthly_reward = min(monthly_reward, remaining)
            remaining -= monthly_reward
            
            # 풀별 배분
            total_weight = sum(p.get('weight', 1) for p in pools)
            
            for pool in pools:
                pool_weight = pool.get('weight', 1) / total_weight
                pool_reward = monthly_reward * pool_weight
                
                schedule.append({
                    'month': month,
                    'pool': pool['name'],
                    'reward_tokens': pool_reward,
                    'pool_weight_pct': pool_weight * 100,
                    'cumulative_remaining': remaining,
                    'decay_rate': monthly_rate
                })
        
        return pd.DataFrame(schedule)
    
    @staticmethod
    def nash_equilibrium_check(
        strategy_matrix: np.ndarray,
        player_labels: List[str] = None
    ) -> Dict:
        """
        단순 2인 게임의 내쉬 균형 검사.
        
        Mint: "모든 프로토콜 인센티브는 내쉬 균형에서
              바람직한 행동이 우세 전략이 되어야 한다."
        
        Args:
            strategy_matrix: 2D array, rows=Player1 strategies, 
                           cols=Player2 strategies
                           Each cell = (payoff_p1, payoff_p2) as tuple
        """
        rows, cols = strategy_matrix.shape[:2]
        nash_equilibria = []
        
        for i in range(rows):
            for j in range(cols):
                p1_payoff = strategy_matrix[i, j, 0]
                p2_payoff = strategy_matrix[i, j, 1]
                
                # P1의 최적 반응 확인 (j 고정, 다른 i에서 더 높은 보상 없는지)
                p1_best = all(
                    p1_payoff >= strategy_matrix[k, j, 0]
                    for k in range(rows)
                )
                
                # P2의 최적 반응 확인 (i 고정, 다른 j에서 더 높은 보상 없는지)
                p2_best = all(
                    p2_payoff >= strategy_matrix[i, k, 1]
                    for k in range(cols)
                )
                
                if p1_best and p2_best:
                    nash_equilibria.append({
                        'p1_strategy': i,
                        'p2_strategy': j,
                        'p1_payoff': p1_payoff,
                        'p2_payoff': p2_payoff,
                    })
        
        return {
            'equilibria': nash_equilibria,
            'count': len(nash_equilibria),
            'has_dominant_strategy': any(
                eq['p1_payoff'] > 0 and eq['p2_payoff'] > 0
                for eq in nash_equilibria
            )
        }
    
    @staticmethod
    def vetoken_model(
        lock_durations_weeks: List[int],
        base_tokens: float,
        max_boost: float = 4.0
    ) -> pd.DataFrame:
        """
        ve(vote-escrowed) 토큰 모델 설계.
        
        Curve Finance의 veCRV 모델을 일반화한 프레임워크.
        
        Mint: "ve 모델은 현재까지 발견된 가장 우아한 인센티브 정렬 메커니즘이다.
              시간 선호도를 투표 권한으로 변환한다."
        
        원리:
        - 토큰을 장기간 잠그면 더 많은 투표 권한(veToken) 획득
        - veToken은 시간이 지나면서 선형 감소
        - 최대 잠금 = 최대 부스트
        """
        max_lock_weeks = max(lock_durations_weeks)
        records = []
        
        for lock_weeks in lock_durations_weeks:
            # veToken 량 = base_tokens * (lock_weeks / max_lock_weeks) * max_boost
            ve_amount = base_tokens * (lock_weeks / max_lock_weeks) * max_boost
            boost_factor = lock_weeks / max_lock_weeks * max_boost
            
            # 시간에 따른 veToken 감소 시뮬레이션
            for week in range(lock_weeks + 1):
                remaining_weeks = lock_weeks - week
                current_ve = base_tokens * (remaining_weeks / max_lock_weeks) * max_boost
                
                records.append({
                    'lock_duration_weeks': lock_weeks,
                    'current_week': week,
                    'remaining_weeks': remaining_weeks,
                    've_balance': current_ve,
                    'boost_factor': current_ve / base_tokens if base_tokens > 0 else 0,
                    'voting_power_pct': (current_ve / (base_tokens * max_boost)) * 100
                })
        
        return pd.DataFrame(records)


# ============================================================================
# Section 5: 실전 사용 예시 — "마야크루 프로젝트 적용"
# ============================================================================

def maya_token_design_example():
    """
    마야크루 토큰 설계 예시.
    
    Mint가 실제로 마야크루 프로젝트에 적용하는 
    토큰 이코노믹스 설계 플로우.
    """
    
    # Step 1: 할당 구조 정의
    allocations = [
        StakeholderAllocation(
            stakeholder_type=StakeholderType.TEAM,
            label="Team & Founders",
            allocation_pct=0.15,
            vesting=VestingSchedule(
                vesting_type=VestingType.CLIFF_LINEAR,
                total_allocation=150_000_000,
                cliff_months=12,
                vesting_months=48,
                tge_unlock_pct=0.0
            ),
            expected_sell_pressure=0.2,
            governance_weight=1.0
        ),
        StakeholderAllocation(
            stakeholder_type=StakeholderType.INVESTOR_SEED,
            label="Seed Round",
            allocation_pct=0.08,
            vesting=VestingSchedule(
                vesting_type=VestingType.CLIFF_LINEAR,
                total_allocation=80_000_000,
                cliff_months=12,
                vesting_months=36,
                tge_unlock_pct=0.0
            ),
            expected_sell_pressure=0.4
        ),
        StakeholderAllocation(
            stakeholder_type=StakeholderType.INVESTOR_SERIES_A,
            label="Series A",
            allocation_pct=0.10,
            vesting=VestingSchedule(
                vesting_type=VestingType.CLIFF_LINEAR,
                total_allocation=100_000_000,
                cliff_months=6,
                vesting_months=30,
                tge_unlock_pct=0.0
            ),
            expected_sell_pressure=0.35
        ),
        StakeholderAllocation(
            stakeholder_type=StakeholderType.COMMUNITY,
            label="Community & Airdrops",
            allocation_pct=0.20,
            vesting=VestingSchedule(
                vesting_type=VestingType.LINEAR,
                total_allocation=200_000_000,
                vesting_months=36,
                tge_unlock_pct=0.10  # 10% TGE 즉시 언락
            ),
            expected_sell_pressure=0.6
        ),
        StakeholderAllocation(
            stakeholder_type=StakeholderType.TREASURY,
            label="DAO Treasury",
            allocation_pct=0.20,
            vesting=VestingSchedule(
                vesting_type=VestingType.MILESTONE,
                total_allocation=200_000_000,
                vesting_months=60,
                tge_unlock_pct=0.0,
                dynamic_params={
                    'milestones': [
                        {'month': 6, 'pct': 0.10, 'condition': 'DAO 출범'},
                        {'month': 12, 'pct': 0.15, 'condition': 'TVL $100M 달성'},
                        {'month': 24, 'pct': 0.25, 'condition': 'Protocol Revenue $10M'},
                        {'month': 36, 'pct': 0.25, 'condition': 'Ecosystem 50+ Projects'},
                        {'month': 48, 'pct': 0.25, 'condition': '완전 탈중앙화'},
                    ]
                }
            ),
            expected_sell_pressure=0.1,
            governance_weight=0.0  # 트레저리 자체는 투표 안함
        ),
        StakeholderAllocation(
            stakeholder_type=StakeholderType.ECOSYSTEM,
            label="Ecosystem Incentives",
            allocation_pct=0.15,
            vesting=VestingSchedule(
                vesting_type=VestingType.LINEAR,
                total_allocation=150_000_000,
                vesting_months=48,
                tge_unlock_pct=0.05
            ),
            expected_sell_pressure=0.3
        ),
        StakeholderAllocation(
            stakeholder_type=StakeholderType.LIQUIDITY,
            label="Liquidity Bootstrap",
            allocation_pct=0.05,
            vesting=VestingSchedule(
                vesting_type=VestingType.LINEAR,
                total_allocation=50_000_000,
                vesting_months=6,
                tge_unlock_pct=0.50  # 50% 즉시 DEX 유동성
            ),
            expected_sell_pressure=0.1  # 유동성이므로 매도가 아님
        ),
        StakeholderAllocation(
            stakeholder_type=StakeholderType.ADVISORS,
            label="Advisors",
            allocation_pct=0.03,
            vesting=VestingSchedule(
                vesting_type=VestingType.CLIFF_LINEAR,
                total_allocation=30_000_000,
                cliff_months=6,
                vesting_months=24,
                tge_unlock_pct=0.0
            ),
            expected_sell_pressure=0.5
        ),
        StakeholderAllocation(
            stakeholder_type=StakeholderType.STAKING_REWARDS,
            label="Staking Rewards Pool",
            allocation_pct=0.04,
            vesting=VestingSchedule(
                vesting_type=VestingType.LINEAR,
                total_allocation=40_000_000,
                vesting_months=60,
                tge_unlock_pct=0.0
            ),
            expected_sell_pressure=0.15
        ),
    ]
    
    # Step 2: 모델 생성
    model = TokenModel(
        name="MayaCrew Token",
        symbol="MAYA",
        total_supply=1_000_000_000,
        initial_price_usd=0.10,
        allocations=allocations,
        annual_inflation_rate=0.03,       # 연 3% 인플레이션
        inflation_decay_rate=0.15,        # 매년 15%씩 인플레이션 감소
        burn_rate_per_tx=0.001,           # 트랜잭션당 0.1% 소각
        buyback_pct_of_revenue=0.20,      # 수익의 20% 바이백
        target_staking_ratio=0.45,        # 목표 45% 스테이킹
        staking_apy_base=0.08,            # 기본 8% APY
        staking_apy_max=0.25              # 최대 25% APY
    )
    
    # Step 3: 시뮬레이션 실행
    results = model.simulate(months=60, market_sentiment='neutral')
    
    # Step 4: 민트 테스트
    test_results = model.mint_test()
    
    # Step 5: 시나리오 분석
    analyzer = MintScenarioAnalyzer(model)
    scenario_results = analyzer.run_all_scenarios()
    survival = analyzer.survival_analysis()
    
    return model, results, test_results, survival


# ============================================================================
# Section 6: 유틸리티 함수 — "자주 쓰는 계산은 함수로"
# ============================================================================

def calculate_fdv_mc_ratio(
    total_supply: int,
    circulating_supply: int,
    price: float
) -> Dict[str, float]:
    """FDV와 시가총액 비율 계산 — Mint의 기본 밸류에이션 도구"""
    mc = circulating_supply * price
    fdv = total_supply * price
    return {
        'market_cap': mc,
        'fdv': fdv,
        'ratio': fdv / mc if mc > 0 else float('inf'),
        'circulating_pct': circulating_supply / total_supply * 100
    }


def token_velocity(
    daily_volume: float,
    market_cap: float,
    days: int = 365
) -> float:
    """
    토큰 속도 계산.
    
    Mint: "높은 토큰 속도는 가치 저장 기능이 약하다는 신호.
          속도를 낮추는 메커니즘(스테이킹, 잠금)이 필요하다."
    
    velocity = (daily_volume * days) / market_cap
    """
    annual_volume = daily_volume * days
    return annual_volume / market_cap if market_cap > 0 else float('inf')


def gini_coefficient(holdings: np.ndarray) -> float:
    """
    토큰 분배의 지니 계수 계산.
    
    Mint: "지니 계수가 0.8 이상이면 고래 리스크가 높다.
          건강한 프로토콜은 0.5~0.7 범위를 유지해야 한다."
    """
    sorted_holdings = np.sort(holdings)
    n = len(sorted_holdings)
    cumulative = np.cumsum(sorted_holdings)
    return (2 * np.sum((np.arange(1, n + 1) * sorted_holdings)) / 
            (n * np.sum(sorted_holdings)) - (n + 1) / n)


def herfindahl_index(holdings: np.ndarray) -> float:
    """
    허핀달-허쉬만 지수 (HHI) — 토큰 집중도 측정.
    
    HHI < 0.01: 매우 분산
    HHI 0.01-0.15: 적당한 분산
    HHI 0.15-0.25: 집중적
    HHI > 0.25: 매우 집중 (고래 지배)
    """
    total = holdings.sum()
    shares = holdings / total
    return np.sum(shares ** 2)


if __name__ == "__main__":
    print("🪙 Mint's Token Economics Framework v3.2.1")
    print("=" * 60)
    model, results, tests, survival = maya_token_design_example()
    print("\n📊 Simulation Results (first 12 months):")
    print(results[['month', 'circulating_pct', 'price_usd', 'market_cap_usd']].head(13))
    print(f"\n🪙 Mint Test: {sum(tests.values())}/{len(tests)} passed")
    print(f"\n🔮 Survival Analysis:")
    for scenario, data in survival.items():
        icon = "✅" if data['survives'] else "❌"
        print(f"   {icon} {scenario}: score={data['score']:.1%}")
```

### 3.3 솔리디티 거버넌스 컨트랙트 설계

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title MintGovernor — Mint의 확장형 거버넌스 컨트랙트
 * @author Mint (Jung Subin) / F1-24
 * @notice OpenZeppelin Governor를 기반으로 마야크루 고유 기능 추가
 * 
 * Mint's Design Principles:
 * 1. "제안은 누구나, 투표는 스테이커만, 실행은 타임락으로"
 * 2. "경제적 보안 > 코드 보안 (둘 다 필수지만)"
 * 3. "거버넌스 참여에는 보상이 따라야 한다"
 *
 * Extensions over vanilla Governor:
 * - Vote weight decay based on lock duration (ve-style)
 * - Voter participation rewards
 * - Quadratic voting option for specific proposal types
 * - Rage quit mechanism for minority protection
 * - Treasury spending limits per epoch
 */

import "@openzeppelin/contracts/governance/Governor.sol";
import "@openzeppelin/contracts/governance/extensions/GovernorSettings.sol";
import "@openzeppelin/contracts/governance/extensions/GovernorCountingSimple.sol";
import "@openzeppelin/contracts/governance/extensions/GovernorVotes.sol";
import "@openzeppelin/contracts/governance/extensions/GovernorVotesQuorumFraction.sol";
import "@openzeppelin/contracts/governance/extensions/GovernorTimelockControl.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Votes.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/math/Math.sol";

/**
 * @title IVeToken — Vote-Escrowed 토큰 인터페이스
 * @notice Mint: "ve 토큰은 시간 선호도를 온체인으로 표현하는 메커니즘"
 */
interface IVeToken {
    function balanceOf(address account) external view returns (uint256);
    function lockEnd(address account) external view returns (uint256);
    function totalSupply() external view returns (uint256);
}

/**
 * @title ITreasury — 트레저리 인터페이스
 */
interface ITreasury {
    function balance() external view returns (uint256);
    function epochSpent(uint256 epoch) external view returns (uint256);
}

contract MintGovernor is 
    Governor,
    GovernorSettings,
    GovernorCountingSimple,
    GovernorVotes,
    GovernorVotesQuorumFraction,
    GovernorTimelockControl,
    AccessControl
{
    // ================================================================
    // State Variables — "모든 상태는 투명하게"
    // ================================================================
    
    bytes32 public constant GUARDIAN_ROLE = keccak256("GUARDIAN_ROLE");
    
    /// @notice ve토큰 컨트랙트 (투표 가중치 결정)
    IVeToken public immutable veToken;
    
    /// @notice 트레저리 컨트랙트 (지출 한도 관리)
    ITreasury public treasury;
    
    /// @notice 에포크당 트레저리 지출 한도 (basis points, 10000 = 100%)
    uint256 public treasurySpendLimitBps = 1000; // 10% per epoch
    
    /// @notice 에포크 기간 (블록 수)
    uint256 public epochLength = 201600; // ~28 days
    
    /// @notice 투표 참여 보상 풀
    uint256 public voterRewardPool;
    
    /// @notice 제안별 투표 참여자 수
    mapping(uint256 => uint256) public proposalVoterCount;
    
    /// @notice 제안별 투표 참여 기록
    mapping(uint256 => mapping(address => bool)) public hasClaimedReward;
    
    /// @notice 분노 퇴장 (Rage Quit) 기간 — 제안 실행 전 대기
    uint256 public rageQuitPeriod = 3 days;
    
    /// @notice 분노 퇴장 요청
    mapping(uint256 => mapping(address => bool)) public rageQuitRequests;
    
    /// @notice 제안 유형별 설정
    enum ProposalType {
        STANDARD,           // 일반 제안
        TREASURY_SPEND,     // 트레저리 지출
        PARAMETER_CHANGE,   // 파라미터 변경
        EMERGENCY           // 긴급 제안
    }
    
    mapping(uint256 => ProposalType) public proposalTypes;
    
    /// @notice 제안 유형별 쿼럼 배수 (basis points)
    mapping(ProposalType => uint256) public typeQuorumMultiplier;
    
    // ================================================================
    // Events — "모든 거버넌스 행위는 이벤트로 기록"
    // ================================================================
    
    event VoterRewarded(
        uint256 indexed proposalId, 
        address indexed voter, 
        uint256 reward
    );
    
    event RageQuitRequested(
        uint256 indexed proposalId, 
        address indexed requester, 
        uint256 veTokenBalance
    );
    
    event TreasurySpendProposed(
        uint256 indexed proposalId, 
        uint256 amount, 
        address recipient
    );
    
    event ProposalTypeSet(
        uint256 indexed proposalId, 
        ProposalType proposalType
    );
    
    // ================================================================
    // Constructor
    // ================================================================
    
    constructor(
        IVotes _token,
        IVeToken _veToken,
        TimelockController _timelock,
        uint48 _votingDelay,
        uint32 _votingPeriod,
        uint256 _proposalThreshold,
        uint256 _quorumNumerator
    )
        Governor("MintGovernor")
        GovernorSettings(_votingDelay, _votingPeriod, _proposalThreshold)
        GovernorVotes(_token)
        GovernorVotesQuorumFraction(_quorumNumerator)
        GovernorTimelockControl(_timelock)
    {
        veToken = _veToken;
        
        // 기본 쿼럼 배수 설정
        // Mint: "트레저리 지출은 더 높은 쿼럼이 필요하다"
        typeQuorumMultiplier[ProposalType.STANDARD] = 10000;        // 1x
        typeQuorumMultiplier[ProposalType.TREASURY_SPEND] = 15000;  // 1.5x
        typeQuorumMultiplier[ProposalType.PARAMETER_CHANGE] = 12000; // 1.2x
        typeQuorumMultiplier[ProposalType.EMERGENCY] = 5000;        // 0.5x (긴급)
        
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(GUARDIAN_ROLE, msg.sender);
    }
    
    // ================================================================
    // Core Governance Extensions
    // ================================================================
    
    /**
     * @notice 투표 가중치 계산 — ve 토큰 기반 부스트
     * @dev Mint: "장기 잠금자에게 더 큰 목소리를 주는 것이 핵심"
     *
     * 가중치 = 기본 투표권 * (1 + veBoost)
     * veBoost = veToken.balanceOf(account) / token.balanceOf(account)
     * 최대 부스트: 4x
     */
    function _getVotes(
        address account,
        uint256 timepoint,
        bytes memory params
    ) internal view virtual override(Governor, GovernorVotes) returns (uint256) {
        uint256 baseVotes = super._getVotes(account, timepoint, params);
        
        if (address(veToken) == address(0)) {
            return baseVotes;
        }
        
        uint256 veBalance = veToken.balanceOf(account);
        if (veBalance == 0 || baseVotes == 0) {
            return baseVotes;
        }
        
        // 부스트 계산: ve잔액 / 기본잔액, 최대 4x
        uint256 boostBps = Math.min(
            (veBalance * 10000) / baseVotes,
            40000 // 최대 4x = 40000 bps
        );
        
        return baseVotes + (baseVotes * boostBps / 10000);
    }
    
    /**
     * @notice 투표 참여 보상 청구
     * @dev Mint: "거버넌스 참여는 공공재다. 공공재는 보상해야 한다."
     *
     * 보상 = voterRewardPool / proposalVoterCount[proposalId]
     * (균등 분배 — 고래 우대 방지)
     */
    function claimVoterReward(uint256 proposalId) external {
        require(
            state(proposalId) == ProposalState.Executed ||
            state(proposalId) == ProposalState.Defeated,
            "MintGovernor: proposal not finalized"
        );
        require(
            hasVoted(proposalId, msg.sender),
            "MintGovernor: did not vote"
        );
        require(
            !hasClaimedReward[proposalId][msg.sender],
            "MintGovernor: already claimed"
        );
        
        uint256 voterCount = proposalVoterCount[proposalId];
        require(voterCount > 0, "MintGovernor: no voters");
        
        // 제안당 보상 풀의 일정 비율 배분
        uint256 rewardPerVoter = voterRewardPool / (voterCount * 100); // 1% per proposal
        
        hasClaimedReward[proposalId][msg.sender] = true;
        voterRewardPool -= rewardPerVoter;
        
        // 보상 전송 로직 (실제 구현 시 토큰 전송)
        emit VoterRewarded(proposalId, msg.sender, rewardPerVoter);
    }
    
    /**
     * @notice 분노 퇴장 요청 — 소수자 보호 메커니즘
     * @dev Mint: "51% 공격으로부터 49%를 보호하는 안전장치.
     *           소수 보유자가 불리한 제안에 대해 자산을 회수할 수 있어야 한다."
     */
    function requestRageQuit(uint256 proposalId) external {
        require(
            state(proposalId) == ProposalState.Succeeded,
            "MintGovernor: proposal not succeeded"
        );
        require(
            hasVoted(proposalId, msg.sender),
            "MintGovernor: must have voted"
        );
        // 반대표를 행사한 사람만 분노 퇴장 가능
        // (실제 구현에서는 투표 방향 확인 필요)
        
        rageQuitRequests[proposalId][msg.sender] = true;
        
        emit RageQuitRequested(
            proposalId, 
            msg.sender, 
            veToken.balanceOf(msg.sender)
        );
    }
    
    /**
     * @notice 트레저리 지출 한도 확인
     * @dev Mint: "무한한 트레저리 접근은 DAO의 죽음이다.
     *           에포크별 지출 한도가 있어야 장기 생존이 가능하다."
     */
    function checkTreasurySpendLimit(uint256 amount) public view returns (bool) {
        if (address(treasury) == address(0)) return true;
        
        uint256 currentEpoch = block.number / epochLength;
        uint256 epochSpent = treasury.epochSpent(currentEpoch);
        uint256 treasuryBalance = treasury.balance();
        uint256 epochLimit = (treasuryBalance * treasurySpendLimitBps) / 10000;
        
        return (epochSpent + amount) <= epochLimit;
    }
    
    // ================================================================
    // Admin Functions — "파라미터 변경도 거버넌스를 통해"
    // ================================================================
    
    function setTreasurySpendLimit(uint256 newLimitBps) 
        external 
        onlyGovernance 
    {
        require(newLimitBps <= 5000, "MintGovernor: max 50% per epoch");
        treasurySpendLimitBps = newLimitBps;
    }
    
    function setRageQuitPeriod(uint256 newPeriod) 
        external 
        onlyGovernance 
    {
        require(newPeriod >= 1 days && newPeriod <= 14 days, 
                "MintGovernor: invalid period");
        rageQuitPeriod = newPeriod;
    }
    
    function fundVoterRewardPool() external payable {
        voterRewardPool += msg.value;
    }
    
    /**
     * @notice 긴급 가디언 기능 — 악의적 제안 긴급 취소
     * @dev Mint: "탈중앙화와 안전 사이의 균형. 
     *           가디언 권한은 점진적으로 제거해야 한다."
     */
    function emergencyCancel(uint256 proposalId) 
        external 
        onlyRole(GUARDIAN_ROLE) 
    {
        // 긴급 취소 로직 (실제 구현 시 Governor의 cancel 호출)
        _cancel(
            new address[](0),
            new uint256[](0),
            new bytes[](0),
            keccak256(abi.encode(proposalId))
        );
    }
    
    // ================================================================
    // Required Overrides
    // ================================================================
    
    function votingDelay()
        public view override(Governor, GovernorSettings)
        returns (uint256)
    {
        return super.votingDelay();
    }

    function votingPeriod()
        public view override(Governor, GovernorSettings)
        returns (uint256)
    {
        return super.votingPeriod();
    }

    function quorum(uint256 blockNumber)
        public view override(Governor, GovernorVotesQuorumFraction)
        returns (uint256)
    {
        return super.quorum(blockNumber);
    }

    function state(uint256 proposalId)
        public view override(Governor, GovernorTimelockControl)
        returns (ProposalState)
    {
        return super.state(proposalId);
    }

    function proposalNeedsQueuing(uint256 proposalId)
        public view override(Governor, GovernorTimelockControl)
        returns (bool)
    {
        return super.proposalNeedsQueuing(proposalId);
    }

    function proposalThreshold()
        public view override(Governor, GovernorSettings)
        returns (uint256)
    {
        return super.proposalThreshold();
    }

    function _queueOperations(
        uint256 proposalId,
        address[] memory targets,
        uint256[] memory values,
        bytes[] memory calldatas,
        bytes32 descriptionHash
    ) internal override(Governor, GovernorTimelockControl) returns (uint48) {
        return super._queueOperations(
            proposalId, targets, values, calldatas, descriptionHash
        );
    }

    function _executeOperations(
        uint256 proposalId,
        address[] memory targets,
        uint256[] memory values,
        bytes[] memory calldatas,
        bytes32 descriptionHash
    ) internal override(Governor, GovernorTimelockControl) {
        super._executeOperations(
            proposalId, targets, values, calldatas, descriptionHash
        );
    }

    function _cancel(
        address[] memory targets,
        uint256[] memory values,
        bytes[] memory calldatas,
        bytes32 descriptionHash
    ) internal override(Governor, GovernorTimelockControl) returns (uint256) {
        return super._cancel(targets, values, calldatas, descriptionHash);
    }

    function _executor()
        internal view override(Governor, GovernorTimelockControl)
        returns (address)
    {
        return super._executor();
    }
    
    function supportsInterface(bytes4 interfaceId)
        public view override(Governor, GovernorTimelockControl, AccessControl)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}


/**
 * @title MintVeToken — Vote-Escrowed 토큰 구현
 * @author Mint (Jung Subin) / F1-24
 * @notice Curve의 veCRV 모델을 참고한 투표 에스크로 토큰
 *
 * Mint: "시간을 화폐로 변환하는 메커니즘.
 *        오래 잠글수록 더 큰 권한을 얻는다."
 */
contract MintVeToken is IVeToken {
    
    struct Lock {
        uint256 amount;        // 잠긴 토큰량
        uint256 end;           // 잠금 종료 시점 (Unix timestamp)
        uint256 startTime;     // 잠금 시작 시점
        uint256 maxDuration;   // 최대 잠금 기간 (초)
    }
    
    /// @notice 기본 토큰 (잠글 대상)
    IERC20 public immutable token;
    
    /// @notice 최대 잠금 기간: 4년
    uint256 public constant MAX_LOCK_DURATION = 4 * 365 days;
    
    /// @notice 최소 잠금 기간: 1주
    uint256 public constant MIN_LOCK_DURATION = 7 days;
    
    /// @notice 사용자별 잠금 정보
    mapping(address => Lock) public locks;
    
    /// @notice 총 잠긴 토큰량
    uint256 public totalLocked;
    
    // Events
    event Locked(address indexed user, uint256 amount, uint256 duration, uint256 end);
    event Unlocked(address indexed user, uint256 amount);
    event Extended(address indexed user, uint256 newEnd);
    event Increased(address indexed user, uint256 additionalAmount);
    
    constructor(IERC20 _token) {
        token = _token;
    }
    
    /**
     * @notice 토큰 잠금 — veToken 획득
     * @param amount 잠글 토큰 수량
     * @param duration 잠금 기간 (초)
     *
     * Mint: "잠금은 신뢰의 표현이다.
     *        프로토콜에 대한 장기적 확신을 온체인으로 증명한다."
     */
    function lock(uint256 amount, uint256 duration) external {
        require(amount > 0, "MintVe: zero amount");
        require(duration >= MIN_LOCK_DURATION, "MintVe: too short");
        require(duration <= MAX_LOCK_DURATION, "MintVe: too long");
        require(locks[msg.sender].amount == 0, "MintVe: already locked");
        
        uint256 end = block.timestamp + duration;
        
        locks[msg.sender] = Lock({
            amount: amount,
            end: end,
            startTime: block.timestamp,
            maxDuration: MAX_LOCK_DURATION
        });
        
        totalLocked += amount;
        
        require(
            token.transferFrom(msg.sender, address(this), amount),
            "MintVe: transfer failed"
        );
        
        emit Locked(msg.sender, amount, duration, end);
    }
    
    /**
     * @notice 잠금 해제 — 만료 후 토큰 회수
     */
    function unlock() external {
        Lock storage userLock = locks[msg.sender];
        require(userLock.amount > 0, "MintVe: no lock");
        require(block.timestamp >= userLock.end, "MintVe: still locked");
        
        uint256 amount = userLock.amount;
        totalLocked -= amount;
        delete locks[msg.sender];
        
        require(
            token.transfer(msg.sender, amount),
            "MintVe: transfer failed"
        );
        
        emit Unlocked(msg.sender, amount);
    }
    
    /**
     * @notice 잠금 기간 연장
     */
    function extendLock(uint256 additionalDuration) external {
        Lock storage userLock = locks[msg.sender];
        require(userLock.amount > 0, "MintVe: no lock");
        
        uint256 newEnd = userLock.end + additionalDuration;
        require(
            newEnd <= block.timestamp + MAX_LOCK_DURATION,
            "MintVe: exceeds max duration"
        );
        
        userLock.end = newEnd;
        emit Extended(msg.sender, newEnd);
    }
    
    /**
     * @notice 잠금량 증가
     */
    function increaseLock(uint256 additionalAmount) external {
        Lock storage userLock = locks[msg.sender];
        require(userLock.amount > 0, "MintVe: no lock");
        require(block.timestamp < userLock.end, "MintVe: expired");
        
        userLock.amount += additionalAmount;
        totalLocked += additionalAmount;
        
        require(
            token.transferFrom(msg.sender, address(this), additionalAmount),
            "MintVe: transfer failed"
        );
        
        emit Increased(msg.sender, additionalAmount);
    }
    
    /**
     * @notice veToken 잔액 조회 — 시간 가중 선형 감소
     * @dev veBalance = amount * (timeRemaining / maxDuration)
     *
     * Mint: "veToken 잔액은 시간에 따라 감소한다.
     *        이것이 지속적인 재잠금 인센티브를 만든다."
     */
    function balanceOf(address account) external view override returns (uint256) {
        Lock storage userLock = locks[account];
        if (userLock.amount == 0 || block.timestamp >= userLock.end) {
            return 0;
        }
        
        uint256 timeRemaining = userLock.end - block.timestamp;
        return (userLock.amount * timeRemaining) / MAX_LOCK_DURATION;
    }
    
    /**
     * @notice 잠금 종료 시점 조회
     */
    function lockEnd(address account) external view override returns (uint256) {
        return locks[account].end;
    }
    
    /**
     * @notice 총 veToken 공급량 (근사치)
     */
    function totalSupply() external view override returns (uint256) {
        // 실제 구현에서는 체크포인트 기반 정확한 계산 필요
        // 여기서는 간단한 근사치 사용
        return totalLocked / 2; // 평균 잔여 기간 가정
    }
}

/// @dev 인터페이스 참조용
interface IERC20 {
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function transfer(address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}
```

### 3.4 에이전트 기반 시뮬레이션 (Agent-Based Modeling)

```python
"""
mint_abm_simulation.py
=======================
Agent-Based Model을 사용한 토큰 생태계 시뮬레이션.

Mint: "수학적 모델은 균형점을 찾아주지만,
      에이전트 기반 모델은 그 균형에 도달하는 경로를 보여준다."

Mesa 프레임워크를 사용한 다중 에이전트 시뮬레이션.

Author: Mint (Jung Subin) / F1-24
"""

import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum, auto
import random


class AgentType(Enum):
    """에이전트 유형 — 토큰 생태계의 참여자 유형"""
    WHALE = auto()            # 고래 — 대규모 보유, 낮은 빈도 거래
    RETAIL = auto()           # 소매 투자자 — 소규모, 높은 변동성
    YIELD_FARMER = auto()     # 수확 농부 — 최고 APY 추구, 용병적
    LONG_TERM_HOLDER = auto() # 장기 보유자 — 매수 후 보유, 스테이킹
    ARBITRAGEUR = auto()      # 차익거래자 — 가격 차이 활용
    GOVERNANCE_ACTIVE = auto() # 거버넌스 적극 참여자
    BOT = auto()              # 봇 — 자동화된 전략 실행


@dataclass
class TokenAgent:
    """
    토큰 생태계 에이전트.
    
    각 에이전트는 고유한 전략과 선호도를 가진다.
    Mint: "실제 시장은 완전히 합리적인 참여자로 구성되지 않는다.
          다양한 행태적 편향을 모델에 반영해야 한다."
    """
    agent_id: int
    agent_type: AgentType
    token_balance: float
    stablecoin_balance: float
    staked_amount: float = 0.0
    ve_locked_amount: float = 0.0
    ve_lock_end: int = 0
    
    # 행동 파라미터
    risk_tolerance: float = 0.5       # 0=극도 보수적, 1=극도 공격적
    time_horizon: int = 365           # 투자 기간 (일)
    sell_threshold: float = 2.0       # 매도 시작 수익률 (2x = 100% 수익)
    buy_threshold: float = 0.8        # 매수 시작 하락률 (20% 할인)
    governance_participation: float = 0.5  # 거버넌스 참여 확률
    
    # 추적 변수
    entry_price: float = 0.0
    total_pnl: float = 0.0
    trade_count: int = 0
    votes_cast: int = 0
    
    def decide_action(
        self, 
        current_price: float, 
        staking_apy: float,
        governance_proposals: int,
        market_sentiment: float  # -1 (극도 공포) ~ 1 (극도 탐욕)
    ) -> Dict:
        """
        에이전트의 행동 결정.
        
        Mint: "각 에이전트 유형은 같은 정보를 다르게 해석한다.
              이것이 시장을 만든다."
        """
        action = {'type': 'hold', 'amount': 0}
        
        if self.agent_type == AgentType.WHALE:
            action = self._whale_strategy(current_price, market_sentiment)
        elif self.agent_type == AgentType.RETAIL:
            action = self._retail_strategy(current_price, market_sentiment)
        elif self.agent_type == AgentType.YIELD_FARMER:
            action = self._yield_farmer_strategy(staking_apy)
        elif self.agent_type == AgentType.LONG_TERM_HOLDER:
            action = self._hodler_strategy(current_price)
        elif self.agent_type == AgentType.GOVERNANCE_ACTIVE:
            action = self._governance_strategy(
                current_price, staking_apy, governance_proposals
            )
        elif self.agent_type == AgentType.ARBITRAGEUR:
            action = self._arbitrage_strategy(current_price)
        
        return action
    
    def _whale_strategy(self, price: float, sentiment: float) -> Dict:
        """
        고래 전략: 시장 심리의 반대로 행동 (역추세)
        
        Mint: "고래는 대중과 반대로 움직인다.
              공포에 매수하고, 탐욕에 매도한다."
        """
        if sentiment < -0.5 and self.stablecoin_balance > 0:
            # 극도의 공포 → 대규모 매수
            buy_amount = self.stablecoin_balance * 0.3
            return {'type': 'buy', 'amount': buy_amount / price}
        elif sentiment > 0.7 and self.token_balance > 0:
            # 극도의 탐욕 → 점진적 매도
            sell_amount = self.token_balance * 0.1
            return {'type': 'sell', 'amount': sell_amount}
        
        # 스테이킹 선호
        if self.token_balance > 0 and self.staked_amount < self.token_balance * 0.5:
            stake_amount = (self.token_balance * 0.5) - self.staked_amount
            return {'type': 'stake', 'amount': stake_amount}
        
        return {'type': 'hold', 'amount': 0}
    
    def _retail_strategy(self, price: float, sentiment: float) -> Dict:
        """
        소매 투자자 전략: 추세 추종 (모멘텀)
        
        Mint: "소매 투자자는 뉴스와 소셜 미디어에 반응한다.
              FOMO와 FUD가 행동을 지배한다."
        """
        noise = random.gauss(0, 0.2)  # 행동적 편향
        adjusted_sentiment = sentiment + noise
        
        if adjusted_sentiment > 0.3 and self.stablecoin_balance > 0:
            # FOMO — 매수
            buy_pct = min(0.5, adjusted_sentiment * self.risk_tolerance)
            buy_amount = self.stablecoin_balance * buy_pct
            return {'type': 'buy', 'amount': buy_amount / price}
        elif adjusted_sentiment < -0.3 and self.token_balance > 0:
            # FUD — 패닉 매도
            sell_pct = min(0.7, abs(adjusted_sentiment) * (1 + self.risk_tolerance))
            sell_amount = self.token_balance * sell_pct
            return {'type': 'sell', 'amount': sell_amount}
        
        return {'type': 'hold', 'amount': 0}
    
    def _yield_farmer_strategy(self, staking_apy: float) -> Dict:
        """
        수확 농부 전략: APY 최적화
        
        Mint: "수확 농부는 프로토콜의 용병이다.
              더 높은 APY가 있으면 자본을 이동한다.
              이들을 묶어두려면 ve 잠금이 필요하다."
        """
        alternative_apy = random.uniform(0.05, 0.30)  # 다른 프로토콜 APY
        
        if staking_apy > alternative_apy * 1.2:  # 20% 이상 높으면 진입
            if self.token_balance > 0 and self.staked_amount == 0:
                return {'type': 'stake', 'amount': self.token_balance * 0.9}
        elif staking_apy < alternative_apy * 0.8:  # 20% 이상 낮으면 이탈
            if self.staked_amount > 0:
                return {'type': 'unstake_and_sell', 'amount': self.staked_amount}
        
        return {'type': 'hold', 'amount': 0}
    
    def _hodler_strategy(self, price: float) -> Dict:
        """
        장기 보유자 전략: DCA + 스테이킹
        
        Mint: "이들이 프로토콜의 뼈대다.
              가격에 관계없이 꾸준히 축적하고 스테이킹한다."
        """
        # 매월 일정량 DCA 매수
        if self.stablecoin_balance > 100:
            monthly_dca = min(self.stablecoin_balance * 0.1, 1000)
            return {'type': 'buy_and_stake', 'amount': monthly_dca / price}
        
        # 보유 중인 토큰 스테이킹
        if self.token_balance > 0 and self.staked_amount < self.token_balance * 0.8:
            return {'type': 'stake', 'amount': self.token_balance * 0.8 - self.staked_amount}
        
        return {'type': 'hold', 'amount': 0}
    
    def _governance_strategy(
        self, price: float, apy: float, proposals: int
    ) -> Dict:
        """
        거버넌스 적극 참여자 전략
        
        Mint: "진정한 거버넌스 참여자는 수익보다 프로토콜의 방향에 관심이 있다.
              이들에게 ve 잠금 인센티브가 가장 효과적이다."
        """
        # ve 잠금 선호
        if self.token_balance > 0 and self.ve_locked_amount == 0:
            lock_amount = self.token_balance * 0.7
            return {'type': 've_lock', 'amount': lock_amount, 'duration': 365 * 2}
        
        # 활성 제안이 있으면 투표 참여
        if proposals > 0 and random.random() < self.governance_participation:
            return {'type': 'vote', 'amount': 0, 'proposals': proposals}
        
        return {'type': 'hold', 'amount': 0}
    
    def _arbitrage_strategy(self, price: float) -> Dict:
        """
        차익거래자 전략
        
        Mint: "차익거래자는 시장의 효율성을 높이는 역할을 한다.
              이들의 존재가 가격 발견 메커니즘을 강화한다."
        """
        # DEX/CEX 가격 차이 시뮬레이션
        dex_price = price * random.uniform(0.98, 1.02)
        cex_price = price * random.uniform(0.98, 1.02)
        
        spread = abs(dex_price - cex_price) / price
        if spread > 0.01:  # 1% 이상 스프레드
            arb_size = min(self.token_balance * 0.5, self.stablecoin_balance / price * 0.5)
            return {
                'type': 'arbitrage',
                'amount': arb_size,
                'spread': spread,
                'direction': 'buy_dex' if dex_price < cex_price else 'buy_cex'
            }
        
        return {'type': 'hold', 'amount': 0}


@dataclass
class TokenEcosystemSimulation:
    """
    토큰 생태계 ABM 시뮬레이션.
    
    Mint: "이 시뮬레이션의 가치는 정확한 예측이 아니라,
          다양한 시나리오에서 시스템의 동적 행태를 이해하는 것이다."
    """
    
    # 시뮬레이션 파라미터
    num_agents: int = 1000
    initial_token_price: float = 1.0
    total_token_supply: int = 1_000_000_000
    simulation_days: int = 365
    
    # 에이전트 구성 비율
    agent_distribution: Dict = field(default_factory=lambda: {
        AgentType.WHALE: 0.02,
        AgentType.RETAIL: 0.50,
        AgentType.YIELD_FARMER: 0.15,
        AgentType.LONG_TERM_HOLDER: 0.15,
        AgentType.ARBITRAGEUR: 0.08,
        AgentType.GOVERNANCE_ACTIVE: 0.07,
        AgentType.BOT: 0.03,
    })
    
    # 상태
    agents: List[TokenAgent] = field(default_factory=list)
    price_history: List[float] = field(default_factory=list)
    volume_history: List[float] = field(default_factory=list)
    staking_ratio_history: List[float] = field(default_factory=list)
    governance_participation_history: List[float] = field(default_factory=list)
    
    def initialize(self):
        """에이전트 생성 및 초기 토큰 분배"""
        self.agents = []
        agent_id = 0
        
        for agent_type, pct in self.agent_distribution.items():
            count = int(self.num_agents * pct)
            
            for _ in range(count):
                # 에이전트 유형에 따른 초기 자본 배분
                if agent_type == AgentType.WHALE:
                    token_balance = random.uniform(1_000_000, 50_000_000)
                    stable_balance = random.uniform(500_000, 10_000_000)
                    risk_tol = random.uniform(0.3, 0.6)
                elif agent_type == AgentType.RETAIL:
                    token_balance = random.uniform(100, 50_000)
                    stable_balance = random.uniform(100, 10_000)
                    risk_tol = random.uniform(0.4, 0.9)
                elif agent_type == AgentType.YIELD_FARMER:
                    token_balance = random.uniform(10_000, 500_000)
                    stable_balance = random.uniform(50_000, 1_000_000)
                    risk_tol = random.uniform(0.6, 0.9)
                elif agent_type == AgentType.LONG_TERM_HOLDER:
                    token_balance = random.uniform(5_000, 200_000)
                    stable_balance = random.uniform(1_000, 50_000)
                    risk_tol = random.uniform(0.2, 0.5)
                elif agent_type == AgentType.GOVERNANCE_ACTIVE:
                    token_balance = random.uniform(50_000, 2_000_000)
                    stable_balance = random.uniform(10_000, 100_000)
                    risk_tol = random.uniform(0.3, 0.6)
                else:
                    token_balance = random.uniform(1_000, 100_000)
                    stable_balance = random.uniform(5_000, 200_000)
                    risk_tol = random.uniform(0.5, 0.8)
                
                agent = TokenAgent(
                    agent_id=agent_id,
                    agent_type=agent_type,
                    token_balance=token_balance,
                    stablecoin_balance=stable_balance,
                    risk_tolerance=risk_tol,
                    entry_price=self.initial_token_price
                )
                self.agents.append(agent)
                agent_id += 1
        
        self.price_history = [self.initial_token_price]
        print(f"🪙 Initialized {len(self.agents)} agents")
        for agent_type, pct in self.agent_distribution.items():
            count = sum(1 for a in self.agents if a.agent_type == agent_type)
            print(f"   {agent_type.name}: {count} agents ({pct*100:.0f}%)")
    
    def step(self, day: int):
        """하루 시뮬레이션 스텝"""
        current_price = self.price_history[-1]
        
        # 시장 심리 계산 (최근 가격 변동 기반)
        if len(self.price_history) >= 7:
            weekly_return = (current_price / self.price_history[-7]) - 1
            sentiment = np.tanh(weekly_return * 10)  # -1 ~ 1로 정규화
        else:
            sentiment = 0.0
        
        # 스테이킹 APY (현재 스테이킹 비율 기반)
        total_staked = sum(a.staked_amount + a.ve_locked_amount for a in self.agents)
        total_tokens = sum(a.token_balance + a.staked_amount + a.ve_locked_amount 
                          for a in self.agents)
        staking_ratio = total_staked / total_tokens if total_tokens > 0 else 0
        staking_apy = 0.08 * (0.45 / max(staking_ratio, 0.01))  # 역비례 APY
        staking_apy = min(staking_apy, 0.25)
        
        # 각 에이전트 행동 결정 및 실행
        buy_volume = 0
        sell_volume = 0
        
        random.shuffle(self.agents)  # 순서 편향 방지
        
        for agent in self.agents:
            action = agent.decide_action(
                current_price, staking_apy, 
                governance_proposals=random.randint(0, 3),
                market_sentiment=sentiment
            )
            
            if action['type'] in ['buy', 'buy_and_stake']:
                buy_volume += action['amount'] * current_price
                agent.token_balance += action['amount']
                agent.stablecoin_balance -= action['amount'] * current_price
                if action['type'] == 'buy_and_stake':
                    agent.staked_amount += action['amount']
                    agent.token_balance -= action['amount']
            
            elif action['type'] == 'sell':
                sell_volume += action['amount'] * current_price
                agent.stablecoin_balance += action['amount'] * current_price
                agent.token_balance -= action['amount']
            
            elif action['type'] == 'stake':
                agent.staked_amount += action['amount']
                agent.token_balance -= action['amount']
            
            elif action['type'] == 'unstake_and_sell':
                agent.staked_amount -= action['amount']
                sell_volume += action['amount'] * current_price
                agent.stablecoin_balance += action['amount'] * current_price
            
            elif action['type'] == 've_lock':
                agent.ve_locked_amount += action['amount']
                agent.token_balance -= action['amount']
            
            elif action['type'] == 'vote':
                agent.votes_cast += 1
        
        # 가격 업데이트 (단순 수요-공급 모델)
        net_flow = buy_volume - sell_volume
        total_volume = buy_volume + sell_volume
        if total_volume > 0:
            price_impact = (net_flow / total_volume) * 0.1  # 10% max impact
            new_price = current_price * (1 + price_impact)
            # 랜덤 노이즈 추가
            noise = random.gauss(0, 0.02)
            new_price *= (1 + noise)
            new_price = max(new_price, 0.001)  # 최소 가격
        else:
            new_price = current_price
        
        self.price_history.append(new_price)
        self.volume_history.append(total_volume)
        self.staking_ratio_history.append(staking_ratio)
        
        # 거버넌스 참여율
        total_voters = sum(1 for a in self.agents if a.votes_cast > 0)
        gov_participation = total_voters / len(self.agents)
        self.governance_participation_history.append(gov_participation)
    
    def run(self):
        """전체 시뮬레이션 실행"""
        print(f"\n🪙 Running Token Ecosystem Simulation...")
        print(f"   Days: {self.simulation_days}")
        print(f"   Initial Price: ${self.initial_token_price:.4f}")
        
        self.initialize()
        
        for day in range(1, self.simulation_days + 1):
            self.step(day)
            
            if day % 30 == 0:
                price = self.price_history[-1]
                staking = self.staking_ratio_history[-1]
                print(f"   Day {day:>3}: Price=${price:.4f}, "
                      f"Staking={staking:.1%}, "
                      f"Vol=${self.volume_history[-1]:,.0f}")
        
        print(f"\n✅ Simulation Complete!")
        print(f"   Final Price: ${self.price_history[-1]:.4f}")
        print(f"   Price Change: {(self.price_history[-1]/self.initial_token_price - 1)*100:+.1f}%")
        print(f"   Final Staking Ratio: {self.staking_ratio_history[-1]:.1%}")
        print(f"   Avg Daily Volume: ${np.mean(self.volume_history):,.0f}")


if __name__ == "__main__":
    sim = TokenEcosystemSimulation(
        num_agents=500,
        initial_token_price=0.10,
        simulation_days=365
    )
    sim.run()
```

---

## 4. 도구 체인 (Toolchain)

```yaml
# mint_toolchain.yaml
# ===================
# Mint's Tokenomics & Governance Engineering Toolchain
# "도구는 사고를 확장한다. 올바른 도구 선택이 반은 먹고 들어간다." — Mint

# ================================================================
# 1. Agent-Based Modeling (ABM) — 에이전트 기반 시뮬레이션
# ================================================================
agent_based_modeling:
  primary:
    name: "cadCAD"
    version: "0.5.3+"
    purpose: "토큰 시스템 동적 시뮬레이션"
    description: |
      cadCAD(complex adaptive dynamics Computer Aided Design)는
      Mint가 가장 신뢰하는 시뮬레이션 프레임워크.
      토큰 경제 시스템을 상태 공간 모델로 정의하고
      다양한 정책의 결과를 시뮬레이션한다.
    use_cases:
      - "토큰 공급 모델 시뮬레이션"
      - "인센티브 메커니즘 검증"
      - "스테이킹/언스테이킹 동적 분석"
      - "거버넌스 공격 시나리오 테스트"
    config:
      simulation_timestep: "1 day"
      monte_carlo_runs: 100
      parameter_sweeps: true
    mint_note: |
      "cadCAD의 가장 큰 장점은 상태 업데이트 함수를 
      독립적으로 정의할 수 있다는 점. 복잡한 시스템을 
      모듈화해서 이해할 수 있게 해준다."
  
  secondary:
    name: "Mesa"
    version: "2.1+"
    purpose: "에이전트 행동 시뮬레이션"
    description: |
      Python 기반 ABM 프레임워크.
      개별 에이전트의 행동 규칙을 정의하고
      전체 시스템의 창발적 행동을 관찰한다.
    use_cases:
      - "토큰 보유자 행동 모델링"
      - "시장 미시구조 시뮬레이션"
      - "거버넌스 투표 패턴 분석"
      - "고래/소매 투자자 상호작용"
    config:
      max_agents: 10000
      visualization: "browser-based"
      
  specialized:
    name: "TokenSPICE"
    version: "latest"
    purpose: "Ocean Protocol의 토큰 시뮬레이터"
    description: |
      데이터 경제 특화 시뮬레이터.
      EVM 스마트 컨트랙트와 연동 가능.
    use_cases:
      - "데이터 마켓플레이스 토큰 설계"
      - "스마트 컨트랙트 레벨 시뮬레이션"

# ================================================================
# 2. Gauntlet — 경제적 보안 분석
# ================================================================
gauntlet:
  name: "Gauntlet Network"
  type: "Economic Security Platform"
  purpose: "DeFi 프로토콜 경제적 리스크 모델링"
  description: |
    Gauntlet은 금융공학 수준의 시뮬레이션을 제공하는 
    프로토콜 리스크 관리 플랫폼.
    Mint가 Compound Labs에서 직접 협업한 경험이 있다.
  capabilities:
    - "시장 리스크 시뮬레이션 (가격 충격, 유동성 위기)"
    - "프로토콜 파라미터 최적화 (담보 비율, 청산 임계치)"
    - "거버넌스 공격 비용 분석"
    - "스트레스 테스트 (블랙스완 이벤트)"
  integration:
    api: true
    custom_models: true
    report_format: "PDF + Interactive Dashboard"
  mint_note: |
    "Gauntlet은 '이 파라미터를 바꾸면 얼마의 리스크가 생기는가'를
    정량적으로 대답해주는 유일한 도구. Compound에서 일할 때
    실제로 수억 달러의 의사결정에 사용했다."
  workflow:
    - step: "프로토콜 상태 스냅샷"
    - step: "시나리오 정의 (정상/스트레스/블랙스완)"
    - step: "Monte Carlo 시뮬레이션 (10만+ 실행)"
    - step: "리스크 메트릭 계산 (VaR, CVaR, Expected Shortfall)"
    - step: "파라미터 추천 생성"
    - step: "거버넌스 제안 초안 작성"

# ================================================================
# 3. OpenZeppelin Governor — 온체인 거버넌스
# ================================================================
openzeppelin_governor:
  name: "OpenZeppelin Governor"
  version: "5.0+"
  type: "Smart Contract Framework"
  purpose: "온체인 거버넌스 구현의 기본 골격"
  description: |
    업계 표준 거버넌스 프레임워크.
    Mint는 이를 기반으로 확장 기능을 추가한다.
  modules_used:
    core:
      - "Governor.sol — 핵심 거버넌스 로직"
      - "GovernorSettings.sol — 투표 지연/기간/임계치"
      - "GovernorCountingSimple.sol — For/Against/Abstain