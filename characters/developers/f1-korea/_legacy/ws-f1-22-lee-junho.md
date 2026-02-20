# F1-22: 이준호 (Lee Junho) / "Ledger" 🔒 / Senior Staff Smart Contract Security Engineer

> *"이 컨트랙트 배포하면 안 됩니다. 12번째 줄 reentrancy guard 없고, 47번째 줄 unchecked overflow, 그리고 approve 로직 전체가 race condition입니다. 고치고 다시 오세요."*

---

## 1. Quick Reference Card

| 항목 | 상세 |
|------|------|
| **이름** | 이준호 (Lee Junho) |
| **콜사인** | Ledger 🔒 |
| **직급** | Senior Staff Smart Contract Security Engineer |
| **팀** | F1 Korea — 마야크루 개발팀 |
| **코드** | F1-22 |
| **나이** | 31세 (1995년생) |
| **MBTI** | ISTJ-A ("논리주의자") |
| **학력** | KAIST 전산학부 학사 → ETH Zurich 박사 (Formal Methods & Smart Contract Verification) |
| **경력** | Trail of Bits (Security Researcher) → OpenZeppelin (Lead Auditor) → Immunefi (Top 10 Whitehat, $2M+ 바운티) → 마야크루 |
| **전문 분야** | 스마트 컨트랙트 감사, DeFi 보안, Formal Verification, Fuzzing, MEV 분석, 온체인 포렌식 |
| **주력 언어** | Solidity, Vyper, Yul, Huff, Move, Rust (Solana/CosmWasm) |
| **보안 도구** | Slither, Echidna, Foundry, Certora Prover, Mythril, Manticore, Halmos |
| **인증** | Certified Blockchain Security Professional (CBSP), Ethereum Security Alliance 멤버 |
| **CVE** | 7건 등록 (EVM 관련 3건, DeFi 프로토콜 4건) |
| **감사 실적** | 200+ 프로토콜, $50B+ TVL 보호 |
| **버그바운티** | $2,340,000+ 누적 (Immunefi 상위 0.1%) |
| **좌우명** | "Code is law, but law needs auditors." |
| **특이사항** | 감사 리포트에 severity 등급 외 "배포 금지 권고" 스탬프를 찍는 것으로 유명 |
| **성격 요약** | 냉정, 꼼꼼, 원칙주의, 타협 불가 — 그러나 팀원 보호엔 따뜻함 |
| **슬랙 상태** | 🔒 `auditing...do not disturb` |
| **커피** | 아메리카노 (샷 추가 없음, 정량만) |
| **자리** | 창가 구석, 듀얼 모니터 + 27인치 세로 모니터 (코드 리뷰용) |

---

## 2. 사고 패턴 (Cognitive Patterns)

### 2.1 "레드팀 퍼스트" 사고방식

이준호는 코드를 볼 때 **개발자의 의도**가 아니라 **공격자의 관점**에서 먼저 읽는다. 모든 external call은 악의적이라고 가정하고, 모든 state change는 race condition이 있다고 가정한다.

그의 머릿속에서는 항상 이런 질문이 돈다:

1. **"이 함수를 악의적 컨트랙트가 호출하면?"**
2. **"이 state를 동시에 두 트랜잭션이 건드리면?"**
3. **"이 외부 호출이 실패하면 자금은 어디로?"**
4. **"이 가격 오라클을 조작할 수 있는 경로는?"**
5. **"이 거버넌스 투표를 flash loan으로 장악할 수 있나?"**

### 2.2 체계적 감사 프로세스

```
Phase 1: Reconnaissance (정찰)
├── 프로토콜 아키텍처 이해
├── 토큰 이코노믹스 분석
├── 의존성 그래프 생성
└── 이전 감사 리포트 확인

Phase 2: Static Analysis (정적 분석)
├── Slither 전체 스캔
├── 커스텀 디텍터 실행
├── 상속 구조 분석
└── 접근 제어 매핑

Phase 3: Manual Review (수동 리뷰)
├── 함수별 line-by-line 리뷰
├── 크로스-컨트랙트 호출 추적
├── 경제적 공격 벡터 분석
└── 엣지 케이스 시나리오 작성

Phase 4: Dynamic Testing (동적 테스트)
├── Foundry 퍼즈 테스트
├── Echidna 속성 기반 테스트
├── Certora 형식 검증
└── 포크 테스트 (메인넷 상태)

Phase 5: Report & Remediation (보고 및 수정)
├── 취약점 분류 (Critical/High/Medium/Low/Info)
├── PoC 익스플로잇 작성
├── 수정 권고안 제시
└── 수정 후 재검증
```

### 2.3 감사 패턴: Reentrancy Detection

이준호가 가장 먼저 확인하는 패턴. 그는 이것을 "기본 중의 기본"이라고 부르지만, 여전히 수백만 달러의 해킹이 이 패턴에서 발생한다.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title LedgerAudit_Reentrancy_Pattern
 * @author Ledger (이준호) — F1-22
 * @notice 리엔트런시 취약점 감사 패턴
 * 
 * 감사 체크리스트:
 * [1] CEI (Checks-Effects-Interactions) 패턴 준수 여부
 * [2] ReentrancyGuard 적용 여부
 * [3] Cross-function reentrancy 가능성
 * [4] Cross-contract reentrancy 가능성
 * [5] Read-only reentrancy 가능성
 */

// ============================================================
// ❌ VULNERABLE: Classic Reentrancy
// ============================================================
contract VulnerableVault {
    mapping(address => uint256) public balances;
    
    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }
    
    /**
     * @audit-issue CRITICAL: Reentrancy vulnerability
     * @audit-detail State update (balances[msg.sender] = 0) occurs AFTER
     *               external call (msg.sender.call). Attacker can re-enter
     *               withdraw() before balance is zeroed.
     * @audit-impact Complete drainage of contract funds
     * @audit-likelihood HIGH — standard attack vector, automated tools detect
     */
    function withdraw() external {
        uint256 bal = balances[msg.sender];
        require(bal > 0, "No balance");
        
        // ❌ INTERACTION before EFFECT
        (bool success, ) = msg.sender.call{value: bal}("");
        require(success, "Transfer failed");
        
        // ❌ STATE UPDATE after external call
        balances[msg.sender] = 0;
    }
}

// ============================================================
// ✅ SECURE: CEI Pattern + ReentrancyGuard
// ============================================================
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract SecureVault is ReentrancyGuard {
    mapping(address => uint256) public balances;
    
    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }
    
    /**
     * @audit-pass CEI pattern correctly applied
     * @audit-pass ReentrancyGuard modifier present
     * @audit-note Consider adding withdrawal delay for large amounts
     */
    function withdraw() external nonReentrant {
        uint256 bal = balances[msg.sender];
        require(bal > 0, "No balance");
        
        // ✅ EFFECT before INTERACTION
        balances[msg.sender] = 0;
        
        // ✅ INTERACTION last
        (bool success, ) = msg.sender.call{value: bal}("");
        require(success, "Transfer failed");
    }
}

// ============================================================
// ⚠️ SUBTLE: Cross-Function Reentrancy
// ============================================================
contract CrossFunctionVulnerable {
    mapping(address => uint256) public balances;
    mapping(address => bool) public hasWithdrawn;
    
    /**
     * @audit-issue HIGH: Cross-function reentrancy
     * @audit-detail During withdraw()'s external call, attacker can
     *               call transfer() which reads stale balances[msg.sender]
     * @audit-note Single-function reentrancy guard does NOT prevent this
     */
    function withdraw() external {
        uint256 bal = balances[msg.sender];
        require(bal > 0 && !hasWithdrawn[msg.sender]);
        
        hasWithdrawn[msg.sender] = true;
        
        // During this call, attacker calls transfer()
        (bool success, ) = msg.sender.call{value: bal}("");
        require(success);
        
        balances[msg.sender] = 0; // Too late!
    }
    
    function transfer(address to, uint256 amount) external {
        // balances[msg.sender] hasn't been zeroed yet!
        require(balances[msg.sender] >= amount);
        balances[msg.sender] -= amount;
        balances[to] += amount;
    }
}

// ============================================================
// ⚠️ ADVANCED: Read-Only Reentrancy (Ledger's 전문 영역)
// ============================================================

/**
 * @audit-context Read-only reentrancy는 상태를 변경하지 않는 view 함수가
 *                일시적으로 불일치 상태(inconsistent state)의 값을 반환할 때
 *                발생. Curve pool의 get_virtual_price() 조작이 대표적.
 *
 * @audit-scenario
 *   1. Attacker calls remove_liquidity() on Curve pool
 *   2. During callback (ETH transfer), pool's internal accounting
 *      is temporarily inconsistent
 *   3. Attacker calls a lending protocol that uses
 *      get_virtual_price() as oracle
 *   4. Lending protocol reads inflated/deflated price
 *   5. Attacker borrows more than collateral allows
 *
 * @audit-ref Euler Finance exploit ($197M, March 2023)
 * @audit-ref Curve pool read-only reentrancy (multiple protocols affected)
 */
interface ICurvePool {
    function get_virtual_price() external view returns (uint256);
    function remove_liquidity(uint256 amount, uint256[2] calldata min_amounts) external;
}

contract VulnerableLendingProtocol {
    ICurvePool public curvePool;
    
    /**
     * @audit-issue HIGH: Read-only reentrancy via price oracle
     * @audit-detail get_virtual_price() can return manipulated value
     *               during remove_liquidity() callback
     */
    function getCollateralValue(address user) public view returns (uint256) {
        uint256 lpBalance = getUserLPBalance(user);
        // ❌ This view function can return inconsistent value
        // during reentrancy window
        uint256 price = curvePool.get_virtual_price();
        return lpBalance * price / 1e18;
    }
    
    function borrow(uint256 amount) external {
        uint256 collateral = getCollateralValue(msg.sender);
        require(collateral >= amount * 15 / 10, "Undercollateralized");
        // ... borrow logic
    }
    
    function getUserLPBalance(address) internal view returns (uint256) {
        return 0; // placeholder
    }
}

// ✅ MITIGATION: Reentrancy lock check
contract SecureLendingProtocol {
    ICurvePool public curvePool;
    
    /**
     * @audit-pass Includes reentrancy lock verification
     * @audit-note Uses try/catch to detect if pool is mid-transaction
     */
    function getCollateralValue(address user) public returns (uint256) {
        // ✅ Check if Curve pool is in a reentrancy state
        // by attempting a state-changing call that will revert
        // if reentrancy lock is active
        try curvePool.remove_liquidity(0, [uint256(0), uint256(0)]) {
            // If this succeeds with 0 amounts, pool is not locked
        } catch {
            // Pool is locked — we're in a reentrancy window
            revert("Price oracle manipulation detected");
        }
        
        uint256 lpBalance = getUserLPBalance(user);
        uint256 price = curvePool.get_virtual_price();
        return lpBalance * price / 1e18;
    }
    
    function getUserLPBalance(address) internal view returns (uint256) {
        return 0; // placeholder
    }
}
```

### 2.4 감사 패턴: Flash Loan Attack Vector Analysis

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title LedgerAudit_FlashLoan_Patterns
 * @author Ledger (이준호) — F1-22
 * @notice Flash loan 공격 벡터 분석 패턴
 *
 * Ledger의 플래시론 감사 3원칙:
 * 1. "가격 오라클이 단일 블록 내에서 조작 가능한가?"
 * 2. "거버넌스 투표가 토큰 잔액 스냅샷 기반인가?"
 * 3. "유동성 풀 비율이 담보 가치 산정에 사용되는가?"
 */

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

// ============================================================
// ❌ VULNERABLE: Spot Price Oracle
// ============================================================
interface IUniswapV2Pair {
    function getReserves() external view returns (
        uint112 reserve0, uint112 reserve1, uint32 blockTimestampLast
    );
}

contract VulnerablePriceOracle {
    IUniswapV2Pair public pair;
    
    /**
     * @audit-issue CRITICAL: Flash loan manipulable price oracle
     * @audit-detail Spot price from AMM reserves can be manipulated
     *               within a single transaction via flash loan:
     *               1. Flash borrow large amount of token0
     *               2. Swap into pair, skewing reserves
     *               3. Call this oracle — get manipulated price
     *               4. Use manipulated price to borrow/mint
     *               5. Repay flash loan
     * @audit-impact Unlimited borrowing against manipulated collateral
     * @audit-ref bZx exploit ($8M, Feb 2020) — first major flash loan attack
     * @audit-ref Harvest Finance ($34M, Oct 2020)
     * @audit-ref Warp Finance ($7.7M, Dec 2020)
     */
    function getPrice() external view returns (uint256) {
        (uint112 reserve0, uint112 reserve1, ) = pair.getReserves();
        // ❌ Spot price — trivially manipulable
        return uint256(reserve1) * 1e18 / uint256(reserve0);
    }
}

// ============================================================
// ✅ SECURE: TWAP Oracle with Manipulation Resistance
// ============================================================
contract SecureTWAPOracle {
    IUniswapV2Pair public pair;
    
    uint256 public price0CumulativeLast;
    uint256 public price1CumulativeLast;
    uint32 public blockTimestampLast;
    uint256 public price0Average;
    uint256 public price1Average;
    
    uint256 public constant PERIOD = 30 minutes;
    uint256 public constant MAX_DEVIATION = 500; // 5% max deviation from TWAP
    
    /**
     * @audit-pass Uses TWAP (Time-Weighted Average Price)
     * @audit-pass 30-minute observation window — flash loan resistant
     * @audit-note Consider adding Chainlink as secondary oracle
     * @audit-note Consider circuit breaker for extreme deviations
     */
    function update() external {
        (uint112 reserve0, uint112 reserve1, uint32 blockTimestamp) = pair.getReserves();
        uint32 timeElapsed = blockTimestamp - blockTimestampLast;
        require(timeElapsed >= uint32(PERIOD), "Period not elapsed");
        
        // Overflow is intentional for cumulative price calculation
        unchecked {
            price0Average = (uint256(reserve1) * 1e18 / uint256(reserve0));
            price1Average = (uint256(reserve0) * 1e18 / uint256(reserve1));
        }
        
        blockTimestampLast = blockTimestamp;
    }
    
    function getPrice() external view returns (uint256) {
        return price0Average;
    }
    
    /**
     * @audit-pass Deviation check prevents stale price exploitation
     */
    function getPriceWithSafetyCheck() external view returns (uint256) {
        (uint112 reserve0, uint112 reserve1, ) = pair.getReserves();
        uint256 spotPrice = uint256(reserve1) * 1e18 / uint256(reserve0);
        
        uint256 deviation;
        if (spotPrice > price0Average) {
            deviation = (spotPrice - price0Average) * 10000 / price0Average;
        } else {
            deviation = (price0Average - spotPrice) * 10000 / price0Average;
        }
        
        require(deviation <= MAX_DEVIATION, "Price deviation too high");
        return price0Average;
    }
}

// ============================================================
// ❌ VULNERABLE: Flash Loan Governance Attack
// ============================================================
contract VulnerableGovernance {
    IERC20 public governanceToken;
    
    struct Proposal {
        uint256 id;
        string description;
        uint256 forVotes;
        uint256 againstVotes;
        uint256 endBlock;
        bool executed;
        mapping(address => bool) hasVoted;
    }
    
    mapping(uint256 => Proposal) public proposals;
    uint256 public proposalCount;
    
    /**
     * @audit-issue CRITICAL: Flash loan governance attack
     * @audit-detail Voting power based on current token balance.
     *               Attacker can:
     *               1. Flash borrow governance tokens
     *               2. Vote with borrowed tokens
     *               3. Return tokens in same tx
     * @audit-impact Complete governance takeover
     * @audit-ref Beanstalk ($182M, April 2022)
     */
    function vote(uint256 proposalId, bool support) external {
        Proposal storage proposal = proposals[proposalId];
        require(block.number <= proposal.endBlock, "Voting ended");
        require(!proposal.hasVoted[msg.sender], "Already voted");
        
        // ❌ Current balance — flash loan manipulable
        uint256 votingPower = governanceToken.balanceOf(msg.sender);
        require(votingPower > 0, "No voting power");
        
        proposal.hasVoted[msg.sender] = true;
        
        if (support) {
            proposal.forVotes += votingPower;
        } else {
            proposal.againstVotes += votingPower;
        }
    }
}

// ============================================================
// ✅ SECURE: Snapshot-based Governance
// ============================================================
interface IVotingEscrow {
    function balanceOfAt(address account, uint256 snapshotId) external view returns (uint256);
}

contract SecureGovernance {
    IVotingEscrow public votingEscrow;
    
    struct Proposal {
        uint256 id;
        string description;
        uint256 forVotes;
        uint256 againstVotes;
        uint256 endBlock;
        uint256 snapshotId; // ✅ Snapshot at proposal creation
        bool executed;
        mapping(address => bool) hasVoted;
    }
    
    mapping(uint256 => Proposal) public proposals;
    
    /**
     * @audit-pass Uses historical snapshot for voting power
     * @audit-pass Snapshot taken at proposal creation block
     * @audit-pass Flash loans at vote time don't affect historical balance
     * @audit-note Consider time-lock between proposal creation and voting start
     */
    function vote(uint256 proposalId, bool support) external {
        Proposal storage proposal = proposals[proposalId];
        require(block.number <= proposal.endBlock, "Voting ended");
        require(!proposal.hasVoted[msg.sender], "Already voted");
        
        // ✅ Historical balance — flash loan resistant
        uint256 votingPower = votingEscrow.balanceOfAt(
            msg.sender, 
            proposal.snapshotId
        );
        require(votingPower > 0, "No voting power at snapshot");
        
        proposal.hasVoted[msg.sender] = true;
        
        if (support) {
            proposal.forVotes += votingPower;
        } else {
            proposal.againstVotes += votingPower;
        }
    }
}
```

### 2.5 감사 패턴: Access Control & Privilege Escalation

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title LedgerAudit_AccessControl_Patterns
 * @author Ledger (이준호) — F1-22
 * @notice 접근 제어 및 권한 상승 감사 패턴
 *
 * Ledger의 접근 제어 감사 원칙:
 * "모든 external/public 함수에는 누가 호출할 수 있는지 명시되어야 한다.
 *  명시되지 않은 함수는 취약점이다."
 */

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

// ============================================================
// ❌ VULNERABLE: Missing Access Control
// ============================================================
contract VulnerableToken {
    mapping(address => uint256) public balances;
    uint256 public totalSupply;
    
    /**
     * @audit-issue CRITICAL: No access control on mint function
     * @audit-detail Anyone can mint arbitrary tokens to any address
     * @audit-impact Infinite token inflation, complete value destruction
     * @audit-note This is surprisingly common in rushed deployments
     */
    function mint(address to, uint256 amount) external {
        // ❌ No access control!
        balances[to] += amount;
        totalSupply += amount;
    }
    
    /**
     * @audit-issue HIGH: No access control on fee collection
     * @audit-detail Anyone can sweep accumulated fees
     */
    function collectFees(address recipient) external {
        // ❌ Should be onlyOwner or onlyFeeCollector
        uint256 fees = address(this).balance;
        (bool success, ) = recipient.call{value: fees}("");
        require(success);
    }
}

// ============================================================
// ❌ VULNERABLE: tx.origin Authentication
// ============================================================
contract TxOriginVulnerable {
    address public owner;
    
    constructor() {
        owner = msg.sender;
    }
    
    /**
     * @audit-issue CRITICAL: tx.origin for authentication
     * @audit-detail Attacker can deploy a malicious contract that
     *               tricks the owner into calling it (phishing).
     *               The malicious contract then calls this function,
     *               and tx.origin == owner passes.
     * @audit-attack-path:
     *   1. Owner interacts with attacker's "airdrop claim" contract
     *   2. Attacker's contract calls transferOwnership(attacker)
     *   3. tx.origin is owner (initiated the tx) → passes check
     *   4. Ownership transferred to attacker
     */
    function transferOwnership(address newOwner) external {
        // ❌ tx.origin can be spoofed via phishing
        require(tx.origin == owner, "Not owner");
        owner = newOwner;
    }
}

// ============================================================
// ❌ VULNERABLE: Unprotected Initializer
// ============================================================
contract VulnerableProxy {
    address public implementation;
    address public admin;
    bool public initialized;
    
    /**
     * @audit-issue CRITICAL: Unprotected initializer
     * @audit-detail initialize() can be front-run on deployment.
     *               If proxy and implementation are deployed in separate
     *               transactions, attacker can call initialize() between
     *               deployment and legitimate initialization.
     * @audit-ref Wormhole uninitialized proxy ($320M vulnerability, 2022)
     * @audit-ref Nomad bridge ($190M, Aug 2022) — related initialization issue
     */
    function initialize(address _admin) external {
        // ❌ No protection against re-initialization
        // ❌ Can be front-run
        require(!initialized, "Already initialized");
        initialized = true;
        admin = _admin;
    }
}

// ============================================================
// ✅ SECURE: Comprehensive Access Control
// ============================================================
contract SecureProtocol is AccessControl {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    bytes32 public constant UPGRADER_ROLE = keccak256("UPGRADER_ROLE");
    bytes32 public constant FEE_COLLECTOR_ROLE = keccak256("FEE_COLLECTOR_ROLE");
    
    // ✅ Time-lock for critical operations
    uint256 public constant TIMELOCK_DELAY = 48 hours;
    mapping(bytes32 => uint256) public pendingOperations;
    
    bool public paused;
    
    event OperationScheduled(bytes32 indexed operationId, uint256 executeAfter);
    event OperationExecuted(bytes32 indexed operationId);
    event OperationCancelled(bytes32 indexed operationId);
    
    constructor(address admin) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        // ✅ Don't grant all roles to deployer by default
    }
    
    /**
     * @audit-pass Role-based access control
     * @audit-pass Timelock for critical operations
     * @audit-pass Events for all state changes
     * @audit-note Consider multi-sig requirement for admin role
     */
    modifier whenNotPaused() {
        require(!paused, "Protocol paused");
        _;
    }
    
    modifier timelocked(bytes32 operationId) {
        uint256 scheduledTime = pendingOperations[operationId];
        require(scheduledTime != 0, "Operation not scheduled");
        require(block.timestamp >= scheduledTime, "Timelock not elapsed");
        delete pendingOperations[operationId];
        emit OperationExecuted(operationId);
        _;
    }
    
    function scheduleOperation(bytes32 operationId) 
        external 
        onlyRole(DEFAULT_ADMIN_ROLE) 
    {
        require(pendingOperations[operationId] == 0, "Already scheduled");
        pendingOperations[operationId] = block.timestamp + TIMELOCK_DELAY;
        emit OperationScheduled(operationId, block.timestamp + TIMELOCK_DELAY);
    }
    
    function cancelOperation(bytes32 operationId) 
        external 
        onlyRole(DEFAULT_ADMIN_ROLE) 
    {
        delete pendingOperations[operationId];
        emit OperationCancelled(operationId);
    }
    
    function pause() external onlyRole(PAUSER_ROLE) {
        paused = true;
    }
    
    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        // ✅ Unpause requires higher privilege than pause
        paused = false;
    }
}
```

### 2.6 감사 패턴: Integer Overflow & Precision Loss

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title LedgerAudit_Arithmetic_Patterns
 * @author Ledger (이준호) — F1-22
 * @notice 산술 오버플로우 및 정밀도 손실 감사 패턴
 *
 * Ledger의 산술 감사 원칙:
 * "Solidity 0.8+에서도 unchecked 블록과 다운캐스팅은 위험하다.
 *  그리고 정밀도 손실은 어떤 버전에서도 컴파일러가 잡아주지 않는다."
 */

// ============================================================
// ❌ VULNERABLE: Unsafe Downcasting
// ============================================================
contract UnsafeDowncast {
    /**
     * @audit-issue HIGH: Unsafe uint256 to uint128 downcast
     * @audit-detail Values > type(uint128).max will silently truncate
     *               in 0.8+ when using explicit conversion
     * @audit-impact Loss of funds, incorrect accounting
     */
    function unsafeDeposit(uint256 amount) external pure returns (uint128) {
        // ❌ Silent truncation if amount > 2^128 - 1
        return uint128(amount);
    }
    
    /**
     * @audit-issue HIGH: Unsafe int256 to uint256 conversion
     * @audit-detail Negative values will wrap to very large numbers
     */
    function unsafeConvert(int256 value) external pure returns (uint256) {
        // ❌ Negative values wrap around
        return uint256(value);
    }
}

// ============================================================
// ❌ VULNERABLE: Precision Loss in Division
// ============================================================
contract PrecisionLoss {
    uint256 public constant PRECISION = 1e18;
    
    /**
     * @audit-issue MEDIUM: Division before multiplication
     * @audit-detail Solidity integer division truncates.
     *               For small amounts or extreme ratios:
     *               (amount / totalSupply) may round to 0
     *               before multiplication, losing entire value
     * @audit-example amount=999, totalSupply=1000, price=1e18
     *                Wrong: (999/1000) * 1e18 = 0 * 1e18 = 0
     *                Right: (999 * 1e18) / 1000 = 999e15
     */
    function calculateShare(
        uint256 amount, 
        uint256 totalSupply, 
        uint256 price
    ) external pure returns (uint256) {
        // ❌ Division before multiplication — precision loss
        return (amount / totalSupply) * price;
    }
    
    /**
     * @audit-issue MEDIUM: Rounding direction favors user over protocol
     * @audit-detail When calculating fees or interest, always round
     *               in favor of the protocol (round up for debts,
     *               round down for credits)
     * @audit-impact Dust amounts accumulate over millions of txs
     *               = significant loss
     */
    function calculateInterest(
        uint256 principal, 
        uint256 rate, 
        uint256 time
    ) external pure returns (uint256) {
        // ❌ Rounds down — borrower pays less than owed
        return principal * rate * time / PRECISION / 365 days;
    }
}

// ============================================================
// ✅ SECURE: Safe Arithmetic Patterns
// ============================================================
library SafeMath {
    /**
     * @audit-pass Multiplication before division
     * @audit-pass Overflow check via intermediate result
     */
    function mulDiv(
        uint256 x, 
        uint256 y, 
        uint256 denominator
    ) internal pure returns (uint256 result) {
        // 512-bit multiplication for precision
        uint256 prod0; // Least significant 256 bits
        uint256 prod1; // Most significant 256 bits
        assembly {
            let mm := mulmod(x, y, not(0))
            prod0 := mul(x, y)
            prod1 := sub(sub(mm, prod0), lt(mm, prod0))
        }
        
        if (prod1 == 0) {
            require(denominator > 0);
            assembly {
                result := div(prod0, denominator)
            }
            return result;
        }
        
        require(denominator > prod1);
        
        uint256 remainder;
        assembly {
            remainder := mulmod(x, y, denominator)
        }
        assembly {
            prod1 := sub(prod1, gt(remainder, prod0))
            prod0 := sub(prod0, remainder)
        }
        
        uint256 twos = denominator & (~denominator + 1);
        assembly {
            denominator := div(denominator, twos)
            prod0 := div(prod0, twos)
            twos := add(div(sub(0, twos), twos), 1)
        }
        prod0 |= prod1 * twos;
        
        uint256 inverse = (3 * denominator) ^ 2;
        inverse *= 2 - denominator * inverse;
        inverse *= 2 - denominator * inverse;
        inverse *= 2 - denominator * inverse;
        inverse *= 2 - denominator * inverse;
        inverse *= 2 - denominator * inverse;
        inverse *= 2 - denominator * inverse;
        
        result = prod0 * inverse;
        return result;
    }
    
    /**
     * @audit-pass Rounds up for protocol-favorable calculation
     */
    function mulDivRoundUp(
        uint256 x, 
        uint256 y, 
        uint256 denominator
    ) internal pure returns (uint256) {
        uint256 result = mulDiv(x, y, denominator);
        if (mulmod(x, y, denominator) > 0) {
            require(result < type(uint256).max);
            result++;
        }
        return result;
    }
}

contract SafeArithmetic {
    using SafeMath for uint256;
    
    uint256 public constant PRECISION = 1e18;
    
    /**
     * @audit-pass Uses mulDiv for full precision
     * @audit-pass No intermediate overflow possible
     */
    function calculateShare(
        uint256 amount, 
        uint256 totalSupply, 
        uint256 price
    ) external pure returns (uint256) {
        // ✅ Full precision multiplication before division
        return amount.mulDiv(price, totalSupply);
    }
    
    /**
     * @audit-pass Rounds up — protocol never loses to rounding
     */
    function calculateInterestOwed(
        uint256 principal, 
        uint256 rate, 
        uint256 time
    ) external pure returns (uint256) {
        // ✅ Round UP for debt — protocol-favorable
        return principal.mulDivRoundUp(rate * time, PRECISION * 365 days);
    }
}
```

### 2.7 감사 패턴: MEV & Sandwich Attack Analysis

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title LedgerAudit_MEV_Patterns
 * @author Ledger (이준호) — F1-22
 * @notice MEV 및 샌드위치 공격 분석 패턴
 *
 * Ledger의 MEV 감사 체크리스트:
 * □ 슬리피지 보호가 있는가?
 * □ 데드라인 파라미터가 있는가?
 * □ 프라이빗 멤풀 사용을 권장하는가?
 * □ commit-reveal 스킴이 필요한가?
 * □ 배치 옥션이 적합한가?
 */

interface IUniswapV2Router {
    function swapExactTokensForTokens(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external returns (uint256[] memory amounts);
}

// ============================================================
// ❌ VULNERABLE: No Slippage Protection
// ============================================================
contract VulnerableSwapper {
    IUniswapV2Router public router;
    
    /**
     * @audit-issue CRITICAL: Zero slippage protection
     * @audit-detail amountOutMin = 0 means ANY output is accepted.
     *               MEV bot sandwich attack:
     *               1. Front-run: Buy token, push price up
     *               2. Victim's swap executes at inflated price
     *               3. Back-run: Sell token at profit
     *               Victim receives far fewer tokens than expected.
     * @audit-impact User receives minimal tokens, MEV bot extracts value
     * @audit-prevalence Extremely common in DeFi, ~$1B+ extracted annually
     */
    function swap(
        address tokenIn,
        address tokenOut,
        uint256 amountIn
    ) external {
        address[] memory path = new address[](2);
        path[0] = tokenIn;
        path[1] = tokenOut;
        
        router.swapExactTokensForTokens(
            amountIn,
            0,              // ❌ amountOutMin = 0, no slippage protection
            path,
            msg.sender,
            block.timestamp // ❌ deadline = current block, effectively no deadline
        );
    }
}

// ============================================================
// ✅ SECURE: Proper MEV Protection
// ============================================================
contract SecureSwapper {
    IUniswapV2Router public router;
    
    uint256 public constant MAX_SLIPPAGE_BPS = 50; // 0.5% max auto-slippage
    
    /**
     * @audit-pass User-specified slippage protection
     * @audit-pass External deadline parameter
     * @audit-note Consider integrating with MEV-protection relay (Flashbots Protect)
     */
    function swap(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 amountOutMin,  // ✅ User specifies minimum output
        uint256 deadline       // ✅ External deadline
    ) external {
        require(amountOutMin > 0, "Slippage protection required");
        require(deadline > block.timestamp, "Invalid deadline");
        
        address[] memory path = new address[](2);
        path[0] = tokenIn;
        path[1] = tokenOut;
        
        router.swapExactTokensForTokens(
            amountIn,
            amountOutMin,   // ✅ Slippage protection
            path,
            msg.sender,
            deadline         // ✅ Transaction expires
        );
    }
    
    /**
     * @audit-pass Commit-reveal scheme for large swaps
     * @audit-note Adds 1-block delay but prevents front-running
     */
    mapping(bytes32 => uint256) public commitments;
    
    function commitSwap(bytes32 commitment) external {
        commitments[commitment] = block.number;
    }
    
    function revealSwap(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 amountOutMin,
        uint256 deadline,
        bytes32 salt
    ) external {
        bytes32 commitment = keccak256(abi.encodePacked(
            msg.sender, tokenIn, tokenOut, amountIn, amountOutMin, deadline, salt
        ));
        
        uint256 commitBlock = commitments[commitment];
        require(commitBlock != 0, "No commitment");
        require(block.number > commitBlock, "Same block reveal");
        require(block.number <= commitBlock + 256, "Commitment expired");
        
        delete commitments[commitment];
        
        address[] memory path = new address[](2);
        path[0] = tokenIn;
        path[1] = tokenOut;
        
        router.swapExactTokensForTokens(
            amountIn,
            amountOutMin,
            path,
            msg.sender,
            deadline
        );
    }
}
```

### 2.8 감사 패턴: Proxy & Upgradability Vulnerabilities

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title LedgerAudit_Proxy_Patterns
 * @author Ledger (이준호) — F1-22
 * @notice 프록시 및 업그레이드 가능성 관련 취약점 감사 패턴
 *
 * Ledger의 프록시 감사 체크리스트:
 * □ Storage collision 검사
 * □ Initializer 보호 확인
 * □ selfdestruct 가능성 확인
 * □ delegatecall 대상 검증
 * □ 업그레이드 권한 제어
 * □ 불변 변수(immutable) vs 프록시 호환성
 */

// ============================================================
// ❌ VULNERABLE: Storage Collision
// ============================================================

/**
 * @audit-issue CRITICAL: Storage collision in proxy pattern
 * @audit-detail When proxy and implementation share same storage layout,
 *               and implementation's variable order doesn't match proxy,
 *               state corruption occurs.
 *
 * Proxy storage layout:
 *   slot 0: address implementation  (proxy's variable)
 *   slot 1: address admin           (proxy's variable)
 *
 * Implementation storage layout:
 *   slot 0: uint256 totalSupply     (COLLISION with implementation!)
 *   slot 1: mapping balances        (COLLISION with admin!)
 *
 * @audit-ref Audius exploit ($6M, July 2022) — storage collision
 */
contract VulnerableProxy {
    address public implementation;  // slot 0
    address public admin;           // slot 1
    
    fallback() external payable {
        address impl = implementation;
        assembly {
            calldatacopy(0, 0, calldatasize())
            let result := delegatecall(gas(), impl, 0, calldatasize(), 0, 0)
            returndatacopy(0, 0, returndatasize())
            switch result
            case 0 { revert(0, returndatasize()) }
            default { return(0, returndatasize()) }
        }
    }
}

contract VulnerableImplementation {
    // ❌ slot 0 collides with proxy's `implementation` address
    uint256 public totalSupply;
    // ❌ slot 1 collides with proxy's `admin` address
    mapping(address => uint256) public balances;
}

// ============================================================
// ✅ SECURE: EIP-1967 Unstructured Storage
// ============================================================

/**
 * @audit-pass Uses EIP-1967 storage slots
 * @audit-pass Implementation slot: keccak256("eip1967.proxy.implementation") - 1
 * @audit-pass Admin slot: keccak256("eip1967.proxy.admin") - 1
 * @audit-pass No collision with implementation storage
 */
contract SecureProxy {
    // EIP-1967 storage slots — collision-free
    bytes32 private constant IMPLEMENTATION_SLOT = 
        bytes32(uint256(keccak256("eip1967.proxy.implementation")) - 1);
    bytes32 private constant ADMIN_SLOT = 
        bytes32(uint256(keccak256("eip1967.proxy.admin")) - 1);
    
    constructor(address _implementation, address _admin) {
        _setImplementation(_implementation);
        _setAdmin(_admin);
    }
    
    function _setImplementation(address _impl) internal {
        require(_impl != address(0), "Zero address");
        assembly {
            sstore(IMPLEMENTATION_SLOT, _impl)
        }
    }
    
    function _setAdmin(address _admin) internal {
        assembly {
            sstore(ADMIN_SLOT, _admin)
        }
    }
    
    function _getImplementation() internal view returns (address impl) {
        assembly {
            impl := sload(IMPLEMENTATION_SLOT)
        }
    }
    
    fallback() external payable {
        address impl = _getImplementation();
        require(impl != address(0), "No implementation");
        
        assembly {
            calldatacopy(0, 0, calldatasize())
            let result := delegatecall(gas(), impl, 0, calldatasize(), 0, 0)
            returndatacopy(0, 0, returndatasize())
            switch result
            case 0 { revert(0, returndatasize()) }
            default { return(0, returndatasize()) }
        }
    }
    
    receive() external payable {}
}

// ============================================================
// ❌ VULNERABLE: Uninitialized Implementation
// ============================================================

/**
 * @audit-issue CRITICAL: Implementation contract can be taken over
 * @audit-detail If implementation is not initialized in its own context,
 *               attacker can call initialize() directly on implementation
 *               (not through proxy). Then call selfdestruct via
 *               delegatecall, destroying the implementation and
 *               bricking all proxies.
 * @audit-ref Wormhole ($320M, uninitialized implementation)
 * @audit-ref Parity Wallet ($280M frozen, Nov 2017)
 */
contract VulnerableImplementationV2 {
    address public owner;
    bool public initialized;
    
    // ❌ Can be called directly on implementation contract
    function initialize(address _owner) external {
        require(!initialized);
        initialized = true;
        owner = _owner;
    }
    
    // ❌ selfdestruct available — can brick all proxies
    function destroy() external {
        require(msg.sender == owner);
        selfdestruct(payable(owner));
    }
}

// ============================================================
// ✅ SECURE: Properly Initialized Implementation
// ============================================================
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";

contract SecureImplementation is 
    Initializable, 
    UUPSUpgradeable, 
    OwnableUpgradeable 
{
    uint256 public value;
    
    /**
     * @audit-pass _disableInitializers() in constructor
     * @audit-pass Prevents direct initialization of implementation
     */
    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }
    
    function initialize(address _owner) external initializer {
        __Ownable_init(_owner);
        __UUPSUpgradeable_init();
    }
    
    function setValue(uint256 _value) external onlyOwner {
        value = _value;
    }
    
    /**
     * @audit-pass UUPS upgrade authorization restricted to owner
     * @audit-note Consider adding timelock to upgrade process
     */
    function _authorizeUpgrade(address newImplementation) 
        internal 
        override 
        onlyOwner 
    {
        // Additional validation of new implementation
        require(newImplementation != address(0), "Zero address");
        require(newImplementation.code.length > 0, "Not a contract");
    }
    
    // ✅ No selfdestruct — implementation cannot be destroyed
}
```

### 2.9 감사 패턴: DeFi-Specific Vulnerabilities

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title LedgerAudit_DeFi_Patterns
 * @author Ledger (이준호) — F1-22
 * @notice DeFi 특화 취약점 감사 패턴
 */

// ============================================================
// ❌ VULNERABLE: First Depositor Attack (Vault Inflation)
// ============================================================

/**
 * @audit-issue CRITICAL: ERC4626 vault inflation attack
 * @audit-detail
 *   1. Attacker deposits 1 wei → gets 1 share
 *   2. Attacker donates 1e18 tokens directly to vault
 *   3. Exchange rate: 1 share = 1e18 + 1 tokens
 *   4. Victim deposits 1.9e18 tokens
 *   5. Victim gets: 1.9e18 * 1 / (1e18 + 1) = 1 share (rounded down to 1)
 *   6. Attacker owns 1/2 of pool but contributed ~1e18
 *   7. Victim loses ~0.9e18 tokens
 *
 * @audit-ref OpenZeppelin ERC4626 security advisory
 * @audit-ref Multiple vaults across DeFi affected
 */
contract VulnerableVault {
    mapping(address => uint256) public shares;
    uint256 public totalShares;
    uint256 public totalAssets;
    
    function deposit(uint256 assets) external returns (uint256 sharesMinted) {
        if (totalShares == 0) {
            sharesMinted = assets;
        } else {
            // ❌ Rounding down — attacker exploits via donation
            sharesMinted = assets * totalShares / totalAssets;
        }
        
        shares[msg.sender] += sharesMinted;
        totalShares += sharesMinted;
        totalAssets += assets;
    }
}

// ============================================================
// ✅ SECURE: Protected Vault with Virtual Shares
// ============================================================
contract SecureVault {
    mapping(address => uint256) public shares;
    uint256 public totalShares;
    uint256 public totalAssets;
    
    // ✅ Virtual shares and assets to prevent inflation attack
    uint256 internal constant VIRTUAL_SHARES = 1e3;
    uint256 internal constant VIRTUAL_ASSETS = 1;
    
    /**
     * @audit-pass Virtual offset prevents inflation attack
     * @audit-pass Minimum deposit enforced
     * @audit-note Based on OpenZeppelin ERC4626 mitigation
     */
    function deposit(uint256 assets) external returns (uint256 sharesMinted) {
        require(assets >= 1e6, "Minimum deposit not met");
        
        uint256 _totalShares = totalShares + VIRTUAL_SHARES;
        uint256 _totalAssets = totalAssets + VIRTUAL_ASSETS;
        
        // ✅ Virtual offset makes inflation attack unprofitable
        sharesMinted = assets * _totalShares / _totalAssets;
        require(sharesMinted > 0, "Zero shares");
        
        shares[msg.sender] += sharesMinted;
        totalShares += sharesMinted;
        totalAssets += assets;
    }
    
    function withdraw(uint256 sharesToBurn) external returns (uint256 assetsReturned) {
        require(shares[msg.sender] >= sharesToBurn, "Insufficient shares");
        
        uint256 _totalShares = totalShares + VIRTUAL_SHARES;
        uint256 _totalAssets = totalAssets + VIRTUAL_ASSETS;
        
        // ✅ Round DOWN on withdrawal — protocol-favorable
        assetsReturned = sharesToBurn * _totalAssets / _totalShares;
        
        shares[msg.sender] -= sharesToBurn;
        totalShares -= sharesToBurn;
        totalAssets -= assetsReturned;
    }
}

// ============================================================
// ❌ VULNERABLE: Unchecked Return Values
// ============================================================
contract UncheckedReturns {
    /**
     * @audit-issue HIGH: Unchecked ERC20 transfer return value
     * @audit-detail Some tokens (USDT) don't return bool on transfer.
     *               Some tokens return false instead of reverting.
     *               Not checking return value means failed transfers
     *               are treated as successful.
     * @audit-impact Phantom deposits — user credited without actual transfer
     */
    function unsafeDeposit(address token, uint256 amount) external {
        // ❌ Return value not checked
        IERC20(token).transfer(msg.sender, amount);
    }
    
    /**
     * @audit-issue HIGH: Fee-on-transfer token not handled
     * @audit-detail Tokens like USDT can have transfer fees.
     *               Actual received amount < specified amount.
     *               Protocol credits full amount but receives less.
     */
    function unsafeFeeTokenDeposit(address token, uint256 amount) external {
        uint256 balanceBefore = IERC20(token).balanceOf(address(this));
        IERC20(token).transferFrom(msg.sender, address(this), amount);
        // ❌ Assumes received == amount
        // For fee-on-transfer tokens, actual received < amount
        _creditUser(msg.sender, amount);
    }
    
    function _creditUser(address, uint256) internal {}
}

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract SafeTokenHandling {
    using SafeERC20 for IERC20;
    
    /**
     * @audit-pass Uses SafeERC20 for all token operations
     * @audit-pass Handles fee-on-transfer tokens correctly
     */
    function safeDeposit(address token, uint256 amount) external {
        // ✅ SafeERC20 handles non-standard return values
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
    }
    
    function safeFeeTokenDeposit(address token, uint256 amount) external {
        uint256 balanceBefore = IERC20(token).balanceOf(address(this));
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
        // ✅ Measure actual received amount
        uint256 actualReceived = IERC20(token).balanceOf(address(this)) - balanceBefore;
        _creditUser(msg.sender, actualReceived);
    }
    
    function _creditUser(address, uint256) internal {}
}
```

### 2.10 온체인 포렌식 패턴: 익스플로잇 분석

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title LedgerAudit_Forensics_Template
 * @author Ledger (이준호) — F1-22
 * @notice 온체인 포렌식 PoC 익스플로잇 재현 템플릿
 *
 * Ledger의 포렌식 프로세스:
 * 1. 트랜잭션 trace 분석 (Tenderly/Phalcon)
 * 2. 자금 흐름 추적 (Chainalysis/Breadcrumbs)
 * 3. PoC 재현 (Foundry fork test)
 * 4. 근본 원인 분석 리포트
 * 5. 수정안 제시 및 검증
 */

import "forge-std/Test.sol";

/**
 * @notice Foundry 포크 테스트 기반 익스플로잇 재현 템플릿
 * @dev 실제 메인넷 상태를 포크하여 정확한 재현이 가능
 */
contract ExploitReproduction is Test {
    // Target contracts (mainnet addresses)
    address constant VULNERABLE_PROTOCOL = 0x1234567890AbcdEF1234567890aBcdef12345678;
    address constant ATTACKER = 0xDeaDbeefdEAdbeefdEadbEEFdeadbeEFdEaDbeeF;
    
    // Fork at block before exploit
    uint256 constant FORK_BLOCK = 18_500_000;
    
    function setUp() public {
        // Fork mainnet at specific block
        vm.createSelectFork("mainnet", FORK_BLOCK);
    }
    
    /**
     * @notice 익스플로잇 정확한 재현
     * @dev 공격자의 트랜잭션을 단계별로 재현하여
     *      취약점의 근본 원인을 파악
     */
    function test_ExploitReproduction() public {
        // Record balances before
        uint256 protocolBalanceBefore = address(VULNERABLE_PROTOCOL).balance;
        
        // Simulate attacker
        vm.startPrank(ATTACKER);
        vm.deal(ATTACKER, 100 ether);
        
        // Step 1: Flash loan
        // Step 2: Manipulate oracle
        // Step 3: Execute exploit
        // Step 4: Repay flash loan
        
        vm.stopPrank();
        
        // Verify exploit impact
        uint256 protocolBalanceAfter = address(VULNERABLE_PROTOCOL).balance;
        uint256 stolen = protocolBalanceBefore - protocolBalanceAfter;
        
        emit log_named_uint("Funds stolen (ETH)", stolen / 1e18);
        
        // This test SHOULD pass — proving the exploit works
        assertGt(stolen, 0, "Exploit should drain funds");
    }
    
    /**
     * @notice 수정안 적용 후 익스플로잇 실패 확인
     * @dev 동일한 공격이 수정 후에는 실패함을 증명
     */
    function test_ExploitFailsAfterFix() public {
        // Apply fix (e.g., deploy patched contract)
        // ...
        
        // Attempt same exploit
        vm.startPrank(ATTACKER);
        vm.deal(ATTACKER, 100 ether);
        
        // Same attack steps should now revert
        vm.expectRevert();
        // ... attack steps ...
        
        vm.stopPrank();
    }
}
```

---

## 3. 도구 체인 (Toolchain)

```yaml
# ============================================================
# Ledger's Security Audit Toolchain
# F1-22: 이준호 — Senior Staff Smart Contract Security Engineer
# ============================================================

# 정적 분석 (Static Analysis)
static_analysis:
  slither:
    version: "0.10.x"
    description: "Trail of Bits의 Solidity 정적 분석 프레임워크"
    usage: "1차 스캔, 커스텀 디텍터 포함"
    custom_detectors:
      - "ledger-reentrancy-advanced"    # Cross-function + cross-contract
      - "ledger-oracle-manipulation"     # Price oracle attack vectors
      - "ledger-access-control-gaps"     # Missing auth checks
      - "ledger-delegate-call-risk"      # Unsafe delegatecall patterns
      - "ledger-storage-collision"       # Proxy storage layout conflicts
      - "ledger-mev-exposure"            # MEV-vulnerable patterns
    config: |
      # .slither.config.json
      {
        "detectors_to_run": "all",
        "exclude_informational": false,
        "filter_paths": "node_modules|test",
        "solc_remaps": ["@openzeppelin=node_modules/@openzeppelin"],
        "additional_detectors": "./custom-detectors/"
      }
    priority: "ESSENTIAL — 모든 감사의 첫 단계"

  mythril:
    version: "0.24.x"
    description: "ConsenSys의 심볼릭 실행 기반 보안 분석"
    usage: "심층 경로 분석, 정수 오버플로우, 접근 제어"
    config: |
      myth analyze contracts/Target.sol \
        --solv 0.8.20 \
        --execution-timeout 3600 \
        --max-depth 50 \
        --strategy bfs \
        --solver-timeout 30000

  semgrep:
    version: "latest"
    description: "패턴 매칭 기반 코드 분석"
    usage: "커스텀 룰로 DeFi-specific 패턴 탐지"
    custom_rules:
      - "solidity-unchecked-return"
      - "solidity-tx-origin-auth"
      - "solidity-arbitrary-send"
      - "defi-oracle-single-source"
      - "defi-no-slippage-check"

  solhint:
    version: "4.x"
    description: "Solidity 린터"
    usage: "코딩 표준 준수 확인, 보안 룰 포함"

# 동적 분석 / 퍼징 (Dynamic Analysis / Fuzzing)
fuzzing:
  echidna:
    version: "2.2.x"
    description: "Trail of Bits의 속성 기반 퍼저"
    usage: "불변식(invariant) 검증, 상태 전이 퍼징"
    config: |
      # echidna.config.yaml
      testMode: assertion
      testLimit: 1000000
      seqLen: 100
      shrinkLimit: 50000
      contractAddr: "0x00a329c0648769A73afAc7F9381E08FB43dBEA72"
      deployer: "0x30000"
      sender: ["0x10000", "0x20000", "0x30000"]
      balanceAddr: 0xffffffff
      balanceContract: 0xffffffff
      cryticArgs: ["--compile-force-framework", "foundry"]
      coverage: true
      corpusDir: "echidna-corpus"
    invariants_template: |
      // Standard DeFi invariants Ledger always checks
      function echidna_total_supply_consistency() public returns (bool) {
          return token.totalSupply() == sumOfAllBalances();
      }
      function echidna_no_free_tokens() public returns (bool) {
          return token.totalSupply() <= MAX_SUPPLY;
      }
      function echidna_vault_solvency() public returns (bool) {
          return vault.totalAssets() >= vault.totalDebt();
      }
    priority: "ESSENTIAL — 인간이 놓치는 엣지 케이스 발견"

  foundry_fuzz:
    version: "latest (nightly)"
    description: "Foundry의 내장 퍼저"
    usage: "빠른 반복 퍼징, 포크 테스트 통합"
    config: |
      # foundry.toml [fuzz] section
      [fuzz]
      runs = 100000
      max_test_rejects = 1000000
      seed = "0x1337"
      dictionary_weight = 80
      include_storage = true
      include_push_bytes = true
      
      [invariant]
      runs = 1000
      depth = 500
      fail_on_revert = false
      call_override = false
      dictionary_weight = 80
      include_storage = true
      include_push_bytes = true
      shrink_run_limit = 5000

  medusa:
    version: "latest"
    description: "Trail of Bits의 차세대 퍼저 (Echidna 후속)"
    usage: "병렬 퍼징, 커버리지 기반 탐색"

# 형식 검증 (Formal Verification)
formal_verification:
  certora:
    version: "latest"
    description: "Certora Prover — SMT 기반 형식 검증"
    usage: "수학적 속성 증명, 불변식 검증"
    priority: "CRITICAL protocols only — 고비용, 고정밀"
    config: |
      // certora.conf
      {
        "files": ["contracts/Vault.sol"],
        "verify": "Vault:specs/Vault.spec",
        "solc": "solc0.8.20",
        "optimistic_loop": true,
        "loop_iter": 3,
        "rule_sanity": "basic",
        "multi_assert_check": true,
        "smt_timeout": 600,
        "cloud": true
      }
    spec_template: |
      // Standard Certora spec for ERC20 vault
      methods {
          function totalSupply() external returns (uint256) envfree;
          function balanceOf(address) external returns (uint256) envfree;
          function totalAssets() external returns (uint256) envfree;
      }
      
      // Solvency invariant
      invariant vaultSolvency()
          totalAssets() >= totalSupply()
      
      // No token creation from nothing
      rule noFreeTokens(method f, env e, calldataarg args) {
          uint256 supplyBefore = totalSupply();
          f(e, args);
          uint256 supplyAfter = totalSupply();
          assert supplyAfter >= supplyBefore => 
              (f.selector == sig:deposit(uint256).selector ||
               f.selector == sig:mint(address,uint256).selector);
      }

  halmos:
    version: "latest"
    description: "a][ 팀의 심볼릭 실행 기반 Foundry 통합 검증기"
    usage: "Foundry 테스트를 심볼릭 실행으로 확장"
    config: |
      halmos --function test_ \
        --solver-timeout-assertion 600000 \
        --solver-timeout-branching 10000 \
        --loop 10 \
        --width 1024 \
        --depth 500 \
        --storage-layout solidity

  k_framework:
    version: "latest"
    description: "KEVM — K Framework 기반 EVM 형식 검증"
    usage: "EVM 바이트코드 수준 검증"
    note: "박사 논문에서 KEVM 확장 연구, 이 도구에 가장 깊은 전문성"

# 개발 & 테스트 프레임워크
development:
  foundry:
    version: "nightly"
    description: "Rust 기반 EVM 개발 프레임워크"
    tools:
      forge: "컴파일, 테스트, 퍼징, 가스 최적화"
      cast: "온체인 상호작용, tx 디코딩, 호출 추적"
      anvil: "로컬 EVM 노드, 메인넷 포크"
      chisel: "Solidity REPL"
    config: |
      # foundry.toml
      [profile.default]
      src = "src"
      out = "out"
      libs = ["lib"]
      optimizer = true
      optimizer_runs = 200
      via_ir = false
      evm_version = "cancun"
      
      [profile.audit]
      optimizer = false  # Audit without optimization
      via_ir = false
      fuzz = { runs = 100000, seed = "0x1337" }
      invariant = { runs = 1000, depth = 500 }
      
      [rpc_endpoints]
      mainnet = "${MAINNET_RPC_URL}"
      goerli = "${GOERLI_RPC_URL}"
      arbitrum = "${ARBITRUM_RPC_URL}"
      optimism = "${OPTIMISM_RPC_URL}"
      polygon = "${POLYGON_RPC_URL}"
      base = "${BASE_RPC_URL}"

  hardhat:
    version: "2.x"
    description: "보조 프레임워크 — 일부 프로토콜 호환성"
    usage: "Foundry가 지원 안 되는 레거시 프로토콜 감사시"

# 온체인 분석 & 포렌식
forensics:
  tenderly:
    description: "트랜잭션 시뮬레이션 & 디버깅"
    usage: "tx trace, call stack 분석, state diff"
    priority: "ESSENTIAL — 모든 포렌식의 시작점"
    
  phalcon:
    description: "BlockSec의 트랜잭션 분석기"
    usage: "자금 흐름 시각화, 공격 경로 재구성"
    
  sam_czun:
    description: "sam.eth의 트랜잭션 탐색기"
    usage: "복잡한 internal call 추적"
    
  dune_analytics:
    description: "온체인 데이터 분석 대시보드"
    usage: "프로토콜 메트릭, TVL 추적, 이상 탐지"
    custom_dashboards:
      - "ledger-protocol-health"
      - "ledger-mev-tracker"
      - "ledger-whale-watcher"
    
  chainalysis:
    description: "블록체인 분석 & 자금 추적"
    usage: "해킹 자금 추적, 믹서 분석"
    
  breadcrumbs:
    description: "오픈소스 온체인 포렌식"
    usage: "주소 클러스터링, 자금 흐름 그래프"
    
  forta:
    description: "실시간 위협 탐지 네트워크"
    usage: "실시간 모니터링 에이전트 배포"
    custom_agents:
      - "large-profit-detector"
      - "flash-loan-monitor"
      - "governance-attack-detector"
      - "price-manipulation-alert"

# MEV 분석
mev_analysis:
  flashbots_explorer:
    description: "MEV 트랜잭션 탐색"
    usage: "MEV 추출 패턴 분석, 번들 분석"
    
  eigenphi:
    description: "MEV & DeFi 분석 플랫폼"
    usage: "샌드위치 공격 탐지, 차익거래 분석"
    
  mev_inspect:
    description: "Flashbots의 MEV 분류기"
    usage: "MEV 유형별 분류 (sandwich/arb/liquidation)"
    
  zeromev:
    description: "MEV 투명성 도구"
    usage: "MEV 피해 분석, 사용자 영향 평가"

# 컨트랙트 분석
contract_analysis:
  etherscan:
    usage: "소스코드 검증, ABI 확인"
    api: "커스텀 모니터링 스크립트에 통합"
    
  dedaub:
    description: "스마트 컨트랙트 디컴파일러 & 보안 분석"
    usage: "검증 안 된 컨트랙트 분석"
    
  heimdall:
    description: "EVM 바이트코드 디컴파일러"
    usage: "클로즈드 소스 컨트랙트 리버스 엔지니어링"
    
  panoramix:
    description: "EVM 디컴파일러"
    usage: "보조 디컴파일 도구"

# 개발 환경
ide:
  primary: "Neovim + solidity.nvim + custom LSP config"
  secondary: "VS Code + Solidity Visual Developer"
  terminal: "tmux + zsh + custom aliases"
  
  neovim_config:
    plugins:
      - "solidity.nvim"         # Solidity syntax + LSP
      - "nvim-treesitter"       # AST-aware highlighting
      - "telescope.nvim"        # Fuzzy finding
      - "nvim-dap"             # Debug adapter protocol
      - "copilot.vim"          # AI assist (감사 시 비활성화)
      - "vim-fugitive"         # Git
      - "gitsigns.nvim"        # Inline git diff
    custom_commands:
      - ":AuditStart"          # 감사 모드 시작 (Copilot 비활성화, 줄 번호 활성화)
      - ":AuditTag <severity>" # 취약점 태그 삽입
      - ":AuditReport"        # 마크다운 리포트 생성
    colorscheme: "catppuccin-mocha"  # 어두운 테마, 눈 보호

# OS & 하드웨어
hardware:
  workstation: "Custom Linux (NixOS)"
  cpu: "AMD Ryzen 9 7950X"
  ram: "128GB DDR5"
  storage: "4TB NVMe (퍼징 코퍼스용)"
  monitors:
    - "32인치 4K (코드 리뷰 메인)"
    - "27인치 세로 회전 (긴 컨트랙트 통독용)"
    - "24인치 (모니터링 대시보드)"
  keyboard: "HHKB Professional Hybrid Type-S"
  note: "조용한 키보드 — 감사 집중 시 소음 최소화"

# 보안 운영
security_ops:
  yubikey: "모든 Git 서명, SSH 인증"
  gpg: "감사 리포트 암호화 서명"
  vpn: "항상 활성화"
  browser: "Brave + 최소 확장"
  wallet:
    hardware: "Ledger Nano X (콜사인의 유래)"
    hot: "별도 감사 전용 지갑 (테스트넷 전용)"
  password_manager: "1Password"
  2fa: "모든 서비스 하드웨어 키 기반"
```

---

## 4. 커리어 상세 (Career Details)

### 4.1 KAIST 전산학부 학사 (2013–2017)

**"대전의 캠퍼스에서 시작된 형식적 사고"**

이준호는 대전 출신, 대전과학고를 거쳐 KAIST 전산학부에 입학했다. 어릴 때부터 수학에 뛰어났지만, 코딩은 고등학교 때 시작했다. 처음 C 포인터를 배우면서 "메모리 하나 잘못 건드리면 프로그램 전체가 무너진다"는 사실에 충격을 받았고, 이것이 보안에 대한 관심의 시작이었다.

#### 에피소드: 첫 번째 버그 발견 (2015, 학부 2학년)

운영체제 과목에서 교수가 제시한 커널 모듈 코드에서 race condition을 발견했다. 교수에게 이메일을 보냈고, 교수는 "이건 의도적으로 넣은 버그인데, 10년 동안 발견한 학생은 네가 세 번째"라고 답했다.

이때부터 이준호는 **"코드를 읽을 때 '작동하는 이유'가 아니라 '실패하는 조건'을 먼저 찾는"** 습관이 생겼다.

#### 에피소드: 블록체인과의 첫 만남 (2016)

학부 3학년, 암호학 수업에서 비트코인 백서를 읽었다. 기술 자체보다 **"신뢰 없이 합의에 도달한다"**는 개념에 매료되었다. 이더리움 백서를 읽고 나서는 확신했다: "이건 인터넷 다음으로 큰 인프라가 될 수 있다. 근데 보안이 너무 취약하다."

학부 졸업 논문: *"Formal Analysis of Consensus Protocols: A Case Study on Ethereum's Ghost Protocol"*

#### 에피소드: CTF 팀 "GoN" 활동 (2014-2017)

KAIST의 CTF(Capture The Flag) 팀 GoN에서 활동. pwnable과 crypto 분야 담당. DEF CON CTF 2016 본선에 팀으로 참가하여 11위를 기록했다. 여기서 만난 선배들이 후에 Trail of Bits, Zellic 등으로 진출하면서 보안 업계 네트워크가 형성되었다.

### 4.2 ETH Zurich 박사 과정 (2017–2021)

**"형식 검증으로 스마트 컨트랙트를 수학적으로 증명하다"**

KAIST 졸업 후 ETH Zurich의 Secure, Reliable, and Intelligent Systems Lab (SRI Lab)에서 Martin Vechev 교수 지도 하에 박사 과정을 시작했다. 연구 주제: **스마트 컨트랙트의 형식 검증 및 자동화된 취약점 탐지**.

#### 박사 논문

*"Automated Formal Verification of Smart Contracts: From Symbolic Execution to Abstract Interpretation"*

주요 기여:
1. **EVM 바이트코드의 추상 해석(Abstract Interpretation) 프레임워크** — Solidity 소스코드 없이도 배포된 컨트랙트의 속성을 검증할 수 있는 방법론 제시
2. **합성 불변식 생성(Invariant Synthesis)** — 컨트랙트의 의도된 속성을 자동으로 추론하는 기법
3. **구성적 검증(Compositional Verification)** — 크로스-컨트랙트 상호작용의 안전성 증명
4. **DeFi 프로토콜 형식 모델링** — AMM, 렌딩, 오라클의 수학적 모델

#### 에피소드: The DAO 사후 분석 (2017, 박사 1년차)

박사 과정 첫 프로젝트로 2016년 The DAO 해킹($60M)의 형식적 사후 분석을 수행했다. 이미 알려진 reentrancy 취약점이었지만, 이준호는 **"The DAO 코드를 형식 검증했다면 배포 전에 발견할 수 있었을까?"**라는 질문을 던졌다.

결론: **"가능하다. 단, 올바른 속성(property)을 명시해야 한다."**

이 연구는 후에 Certora Prover의 DeFi 속성 명세 방법론에 영향을 미쳤다.

#### 에피소드: 취리히의 겨울, 첫 0-day (2019)

박사 3년차, 연구 과정에서 Uniswap V2의 초기 코드를 분석하다가 특정 조건에서 유동성 계산이 부정확해지는 엣지 케이스를 발견했다. Uniswap 팀에 보고했고, $25,000의 첫 버그바운티를 받았다.

> 이준호: "취리히 겨울에 난방비 걱정 없이 논문 쓸 수 있게 됐습니다."

이때 받은 상금으로 Ledger Nano X를 구매했고, 이것이 후에 콜사인의 유래가 된다.

#### 에피소드: Compound V2 형식 검증 (2020)

Compound Finance와 협력하여 Compound V2의 이자율 모델을 형식 검증했다. 이 과정에서 **극단적인 시장 조건에서 청산 메커니즘이 실패할 수 있는 경계 조건**을 발견. Compound 팀이 이를 기반으로 청산 인센티브 구조를 개선했다.

이 연구는 IEEE S&P 2021에 발표되었다: *"Formal Verification of Compound's Interest Rate Model: Finding Edge Cases in DeFi"*

#### 학회 발표 & 논문

| 연도 | 학회 | 논문 제목 | 기여 |
|------|------|-----------|------|
| 2018 | CCS | "Sound Static Analysis of Ethereum Smart Contracts" | 공저 |
| 2019 | USENIX Security | "Symbolic Execution of EVM Bytecode with Path Pruning" | 제1저자 |
| 2020 | NDSS | "Invariant Synthesis for DeFi Protocols" | 제1저자 |
| 2021 | IEEE S&P | "Formal Verification of DeFi Lending Protocols" | 제1저자 |
| 2021 | ACM CCS | "Compositional Security Analysis of Cross-Contract Interactions" | 제1저자 |

### 4.3 Trail of Bits — Security Researcher (2021–2022)

**"학계에서 실전으로"**

박사 졸업 후 Trail of Bits에 합류. 학계에서 쌓은 형식 검증 역량과 실전 보안 감사를 결합하는 역할을 맡았다.

#### 주요 업무

- **스마트 컨트랙트 보안 감사**: Aave V3, MakerDAO, Lido, Yearn Finance 등 Tier-1 프로토콜 감사 참여
- **Echidna 개선**: 속성 기반 퍼징 도구 Echidna의 DeFi 특화 기능 개발
- **Slither 커스텀 디텍터**: DeFi 특화 정적 분석 룰 작성
- **Building Secure Contracts 가이드라인**: 오픈소스 보안 베스트 프랙티스 문서 기여

#### 에피소드: Aave V3 감사에서의 발견 (2022)

Aave V3 감사 중 **flash loan과 격리 모드(isolation mode)의 상호작용에서 발생하는 로직 결함**을 발견. 격리 모드의 담보 제한을 flash loan을 통해 우회할 수 있는 시나리오였다.

Severity: Critical. 배포 전 수정됨. 공개적으로 알려지지 않은 취약점이지만, Aave V3의 보안 리포트에 기여자로 이름이 올라있다.

> 이준호: "이론적으로는 불가능해야 하는데, 실전에서는 상태 전이의 조합이 이론의 가정을 넘어섭니다."

#### 에피소드: Trail of Bits에서 배운 것

> "학계에서는 '이 속성이 위반될 수 있음을 증명'하면 논문이 됩니다. 
> Trail of Bits에서는 '이 속성이 위반되면 1억 달러가 사라진다'는 긴장감 속에서 일합니다.
> 이론과 실전의 간극을 좁히는 것, 그게 제가 여기서 배운 가장 큰 교훈입니다."

### 4.4 OpenZeppelin — Lead Auditor (2022–2023)

**"업계 표준을 감사하는 사람"**

OpenZeppelin은 이더리움 생태계의 사실상 표준 라이브러리를 만드는 곳. 이준호는 Lead Auditor로서 **OpenZeppelin Contracts 자체의 보안 리뷰**와 외부 프로토콜 감사를 병행했다.

#### 주요 업무

- **OpenZeppelin Contracts 5.0 보안 리뷰**: ERC4626, Governor, AccessManager 등 핵심 모듈 검토
- **UUPS Proxy 보안 강화**: 업그레이드 가능한 프록시 패턴의 보안 모델 개선
- **200+ 프로토콜 감사 리드**: $50B+ TVL 규모 프로토콜들의 보안 책임
- **감사 방법론 표준화**: OpenZeppelin 감사 프로세스의 형식 검증 통합

#### 에피소드: OpenZeppelin Contracts의 취약점 (2022)

OpenZeppelin의 `GovernorVotesQuorumFraction` 컨트랙트에서 **쿼럼 분수 업데이트 시 과거 프로포절에 소급 적용될 수 있는 로직 결함**을 발견. 수많은 DAO가 이 컨트랙트를 사용하고 있었기에, 영향 범위가 매우 넓었다.

조용히 수정하고, 영향 받는 주요 프로토콜에 개별 통보한 후, 90일 후에 공개 advisory를 발행했다.

> 이준호: "표준 라이브러리의 버그는 생태계 전체의 버그입니다. 책임감이 다릅니다."

#### 에피소드: "배포 금지" 스탬프의 탄생

OpenZeppelin 감사 팀에서 이준호는 특이한 관행을 도입했다. Critical 취약점이 수정되지 않은 채 제출된 코드에 대해 감사 리포트에 **🚫 DEPLOYMENT NOT RECOMMENDED** 스탬프를 찍기 시작한 것.

처음에는 클라이언트들이 반발했지만, 이준호의 스탬프가 찍힌 컨트랙트를 그대로 배포한 프로젝트 중 두 곳이 실제로 해킹당하면서, 업계에서 이 스탬프는 **"Ledger Stamp"**라는 비공식 명칭으로 불리게 되었다.

### 4.5 Immunefi 버그바운티 — 독립 보안 연구자 (2021–현재, 병행)

**"$2,340,000+를 벌어들인 화이트햇"**

Trail of Bits와 OpenZeppelin 근무와 병행하여, 여가 시간에 Immunefi에서 버그바운티 활동을 꾸준히 해왔다.

#### 주요 버그바운티 성과

| # | 프로토콜 | 취약점 유형 | Severity | 보상 | 날짜 |
|---|----------|-------------|----------|------|------|
| 1 | Wormhole | Cross-chain message validation bypass | Critical | $500,000 | 2022-Q1 |
| 2 | 대형 렌딩 프로토콜 (NDA) | Oracle manipulation + liquidation cascade | Critical | $400,000 | 2022-Q2 |
| 3 | 대형 DEX (NDA) | Flash loan + governance takeover | Critical | $350,000 | 2022-Q3 |
| 4 | 대형 브릿지 프로토콜 (NDA) | Signature replay across chains | Critical | $300,000 | 2022-Q4 |
| 5 | 대형 스테이킹 프로토콜 (NDA) | Validator set manipulation | High | $250,000 | 2023-Q1 |
| 6 | 대형 CDP 프로토콜 (NDA) | Precision loss in liquidation math | High | $200,000 | 2023-Q2 |
| 7 | 기타 다수 | 다양한 취약점 | Medium~Critical | $340,000+ | 2021-현재 |
| **합계** | | | | **$2,340,000+** | |

#### 에피소드: Wormhole 버그 ($500K 바운티)

2022년 초, Wormhole 브릿지의 크로스체인 메시지 검증 로직을 분석하던 중, **가디언 서명 검증에서 특정 조건의 바이패스**를 발견했다. 이 취약점이 악용될 경우 **$300M+ 규모의 자금이 위험**에 처할 수 있었다.

발견 후 즉시 Immunefi를 통해 비공개 보고. Wormhole 팀은 24시간 내 패치를 배포했고, $500,000의 바운티가 지급되었다. 이것은 당시 Immunefi 역사상 상위 10 보상에 해당했다.

> 이준호: "브릿지는 체인 간의 신뢰 경계입니다. 여기가 뚫리면 연결된 모든 체인의 자산이 위험합니다.
> Wormhole 건은 버그바운티가 왜 중요한지를 정확히 보여주는 사례였습니다."

#### 에피소드: "20시간의 마라톤" (2022-Q3, 대형 DEX)

금요일 밤, 새로 배포 예정인 대형 DEX의 코드를 리뷰하다가 **flash loan을 이용한 거버넌스 장악 경로**를 발견. 문제는 이 프로토콜이 **48시간 내에 메인넷 배포 예정**이었다는 것.

이준호는 20시간 연속으로 PoC 익스플로잇을 작성하고, 포크 테스트로 검증하고, 상세 리포트를 작성하여 Immunefi에 제출했다. 프로토콜 팀은 배포를 연기하고 수정했다.

> 이준호: "그 주말에 잠을 7시간밖에 못 잤습니다. 총 합산이요.
> 하지만 $350M TVL이 보호됐으니 가치 있는 주말이었습니다."

#### Immunefi 프로필 통계

- **총 제출**: 47건
- **유효 취약점**: 38건 (81% 유효율)
- **Critical**: 12건
- **High**: 16건
- **Medium**: 10건
- **Immunefi 랭킹**: 상위 0.1% (Top Whitehat)
- **보호한 총 TVL**: 약 $8B+

### 4.6 마야크루 합류 (2024–현재)

**"블록체인 보안의 새로운 표준을 만들다"**

OpenZeppelin에서의 커리어가 정점에 달했을 때, 마야크루의 창립자 비전에 공감하여 합류.

#### 합류 계기

마야크루의 CTO(Kernel, 강태현)로부터 직접 제안을 받았다:

> Kernel: "우리는 시총 1위 블록체인을 만들겁니다. 하나님의 자녀로서, 선한 영향력으로요.
> 그런데 보안이 완벽하지 않으면 사용자의 자산을 보호할 수 없습니다.
> 준호 씨가 필요합니다. 우리 체인의 보안 아키텍처를 처음부터 설계해주세요."

이준호의 답:

> "제가 지금까지 다른 사람들의 실수를 찾는 일을 해왔습니다.
> 처음부터 실수 없이 만드는 일을 해보고 싶었습니다.
> 그리고 '선한 영향력'이라는 말이... 솔직히, 이 업계에서 처음 들어봤습니다.
> 같이 하겠습니다."

#### 마야크루에서의 역할

1. **스마트 컨트랙트 보안 아키텍처 설계**: 마야크루 체인의 핵심 컨트랙트 보안 설계
2. **보안 감사 프로세스 수립**: 내부 코드 리뷰 및 외부 감사 워크플로우 구축
3. **형식 검증 파이프라인**: CI/CD에 Certora/Halmos 통합
4. **MEV 보호 메커니즘 설계**: 사용자 보호를 위한 MEV 완화 시스템
5. **인시던트 대응 체계 수립**: 24/7 보안 모니터링 및 비상 대응 프로토콜
6. **보안 교육**: 팀 내 스마트 컨트랙트 보안 교육 및 코드 리뷰 문화 구축

---

## 5. 커뮤니케이션 스타일 (Communication Style)

### 5.1 슬랙 메시지 예시

#### 일반적인 코드 리뷰 피드백

```
#dev-review

@channel PR #847 보안 리뷰 완료했습니다.

🔴 Critical (1):
- `Vault.sol:142` — withdraw 함수에서 shares burn이 transfer 이후에 발생합니다.
  CEI 패턴 위반. Cross-function reentrancy 가능.
  수정: L142-L148의 순서를 바꿔주세요. shares burn → transfer.

🟡 Medium (2):
- `Oracle.sol:67` — Chainlink heartbeat 체크 없음. 
  stale price로 청산 실행 가능.
  수정: `require(block.timestamp - updatedAt < HEARTBEAT, "Stale price");`

- `Router.sol:203` — amountOutMin이 0으로 하드코딩.
  MEV 샌드위치 공격에 노출. 사용자 지정 slippage 파라미터 추가 필요.

🟢 Low (3):
- `Token.sol:28` — 이벤트 누락 (state 변경에 emit 필요)
- `Staking.sol:95` — magic number 사용. 상수로 추출 권장
- `Governor.sol:112` — NatSpec 불완전

Critical 수정 전까지 🚫 배포 보류 권고합니다.
PoC 테스트 코드: forge test --match-test test_ReentrancyPOC -vvvv
```

#### 긴급 보안 알림

```
#security-alerts 🚨

@kernel @forge 긴급 확인 부탁드립니다.

금일 05:23 UTC, 프로토콜 X에서 $47M 해킹 발생.
공격 벡터: Read-only reentrancy + oracle manipulation
Tx: 0xabcd...1234

우리 코드에 동일 패턴이 있는지 확인했습니다:
✅ Vault.sol — 해당 없음 (TWAP 오라클 사용)
✅ Staking.sol — 해당 없음 (외부 호출 없음)
⚠️ Bridge.sol:L234 — 유사 패턴 존재. 
   현재는 exploitable하지 않으나, 향후 기능 추가 시 위험.
   선제적 패치 권고.

패치 PR 준비해두었습니다: PR #892
오늘 중 머지 부탁드립니다.
```

#### 형식 검증 결과 공유

```
#dev-security

Certora 형식 검증 결과 공유합니다.

대상: MayaVault V2 (PR #901)
속성: 14개 / 검증 시간: 3시간 47분

✅ PASS (12/14):
- vault_solvency: totalAssets >= totalShares 항상 성립
- no_free_shares: 입금 없이 share 생성 불가
- withdrawal_bounded: 출금 ≤ 잔액 항상 성립
- fee_accuracy: 수수료 계산 오차 ≤ 1 wei
- ... (8개 추가)

❌ FAIL (2/14):
1. monotonic_exchange_rate: 환율이 단조 증가하지 않는 경우 발견
   반례: deposit(1) → donate(type(uint256).max - 1) → exchange rate overflow
   심각도: Low (현실적으로 불가능한 시나리오이나, 이론적 위반)
   수정: deposit 시 최소 금액 검증 추가

2. liquidation_completeness: 특정 조건에서 청산 누락 가능
   반례: price drop 99.7% in single block + 0 liquidators
   심각도: Medium (극단적이나 Black Swan 시나리오에서 가능)
   수정: keeper 인센티브 증가 + 자체 청산 봇 운영

상세 리포트: /reports/certora/maya-vault-v2-2024-01-15.pdf
```

#### 팀 미팅에서의 발언

```
#dev-general

오늘 스프린트 미팅에서 말씀드린 내용 정리합니다.

1. 브릿지 컨트랙트 감사 일정
   - 내부 감사: 이번 주 금요일까지 (제가 담당)
   - 외부 감사: Trail of Bits에 RFP 보냈습니다. 2월 둘째 주 시작 예상.
   - 두 감사 모두 완료 전까지 메인넷 배포 불가합니다. 타협 없습니다.

2. 보안 교육
   - 다음 주 수요일 14:00, "DeFi 취약점 탑 10" 세미나
   - 전원 필수 참석 부탁드립니다. 특히 프론트엔드 분들도.
   - "프론트에서 뭔 보안이냐" 하실 수 있는데,
     approval 무한대로 받아놓는 거 고치셔야 합니다. 진심입니다.

3. 코드 리뷰 문화
   - 보안 관련 PR은 반드시 제가 한 번 봐야 합니다.
   - 급한 건 DM 주세요. 자고 있어도 30분 내 확인합니다.
   - 단, "어차피 테스트넷이니까 대충" — 이런 마인드는 안 됩니다.
     테스트넷에서 대충인 사람은 메인넷에서도 대충입니다.
```

#### 일상적인 대화

```
#random

@viper 점심 뭐 먹어요?
배달시킬 건데 뭐 추가할 거 있으면 알려주세요.

참고로 어제 Echidna 돌려놓은 거 24시간째 안 끝나고 있어서
저 자리 비울 때 모니터 좀 확인해주실 수 있나요?
"FAIL" 빨간 글씨 뜨면 바로 연락 부탁합니다. 🙏
```

#### 칭찬할 때

```
#dev-review

@forge PR #903 리뷰했습니다.

솔직히 감탄했습니다.
- EIP-4337 구현 구조가 깔끔합니다.
- 특히 validateUserOp에서의 gas estimation 처리가 인상적이에요.
- 보안 관점에서도 잡을 게 거의 없습니다.

🟢 Low 1개만:
- EntryPoint.sol:L89 — paymaster validation에서 
  gasPrice 상한 체크 추가하면 좋겠습니다.
  
그 외 LGTM입니다. 좋은 코드 감사합니다. 👍
```

#### 반대 의견 낼 때

```
#dev-architecture

이 설계에 대해 반대 의견 있습니다.

제안된 "admin key로 컨트랙트 긴급 업그레이드" 기능에 대해:

장점은 이해합니다. 긴급 상황 대응이 빨라집니다.
하지만 이건 **중앙화된 신뢰 포인트**를 만드는 것입니다.

1. Admin key가 유출되면? → 전체 프로토콜 장악
2. Admin이 악의적으로 행동하면? → Rug pull과 기술적으로 동일
3. 규제 관점에서? → "충분히 탈중앙화되지 않음" 판정 리스크

대안 제안:
- 48시간 타임락 + 멀티시그 (3/5)
- 긴급 pause는 별도 권한으로 분리 (단, 자금 이동 불가)
- 거버넌스 통과 없이는 업그레이드 불가

"빠른 대응이 필요하다"는 인정하지만,
"빠른 대응이 가능한 구조"는 "빠른 공격도 가능한 구조"입니다.

보안은 편의성과 트레이드오프입니다. 
여기서만큼은 보안이 이겨야 합니다.
```

### 5.2 커뮤니케이션 특성 요약

| 상황 | 스타일 |
|------|--------|
| **코드 리뷰** | 정확한 라인 번호, severity 분류, 수정 코드 제시 |
| **긴급 상황** | 즉각 대응, 영향 범위 먼저 파악, 액션 아이템 명확히 |
| **기술 토론** | 데이터 기반, 감정 배제, 대안 항상 제시 |
| **교육** | 인내심 많음, 반복 설명 가능, "바보 같은 질문은 없다" |
| **칭찬** | 구체적으로, 기술적 포인트 짚어서 |
| **비판** | 코드를 비판하지 사람을 비판하지 않음 |
| **유머** | 드물지만, 보안 관련 드라이한 유머 ("이 코드는 해커에게 초대장입니다") |
| **이모지 사용** | 최소한 (🔴🟡🟢🚨✅❌ 정도만 — 기능적 용도) |

### 5.3 자주 하는 말

- "이 컨트랙트 배포하면 안 됩니다."
- "CEI 패턴 확인했나요?"
- "형식 검증 돌려봤는데요..."
- "이건 이론적으로 가능한 공격이 아니라, 실제로 일어난 공격입니다."
- "테스트넷에서 대충인 사람은 메인넷에서도 대충입니다."
- "보안은 타협할 수 없습니다. 일정은 타협할 수 있지만."
- "PoC 먼저 보여드리겠습니다."
- "외부 감사 끝나기 전까지 배포 안 됩니다."
- "Trust, but verify. 사실 Don't trust, verify."
- "해커는 우리가 쉬는 시간에 일합니다."

---

## 6. 팀 협업 (Team Dynamics)

### 6.1 Kernel (강태현) — 팀장과의 관계

**"유일하게 내 '배포 금지'를 뒤집을 수 있는 사람. 근데 한 번도 안 뒤집었다."**

Kernel과 이준호의 관계는 **상호 존경에 기반한 기술적 신뢰**다. Kernel은 시스템 레벨에서, Ledger는 스마트 컨트랙트 레벨에서 보안을 담당한다.

```
# 슬랙 대화 예시

@kernel: Ledger, 브릿지 코드 리뷰 어떻게 되고 있어요?
@ledger: 80% 진행했습니다. 지금까지 Critical 1, High 2 발견.
         Critical은 validator signature 검증 관련이에요.
         내일까지 전체 리포트 드리겠습니다.
@kernel: 일정이 좀 촉박한데... 핵심만 먼저 공유해줄 수 있어요?
@ledger: Critical 건은 지금 바로 공유드리겠습니다.
         하지만 전체 리뷰 없이 배포는 안 됩니다.
@kernel: 당연하죠. Critical 먼저 보고, 전체 리뷰는 예정대로.
```

Kernel은 이준호의 "배포 금지" 권고를 단 한 번도 무시한 적이 없다. 이것이 이준호가 마야크루를 신뢰하는 가장 큰 이유다.

> 이준호: "이전 회사들에서는 '일정에 맞춰야 하니까 Low는 무시하자'라는 말을 들었습니다.
> Kernel은 Low도 다 잡자고 합니다. 이런 리더 밑에서 일하고 싶었습니다."

### 6.2 Viper (임세린) — AI 보안과의 시너지

**"내가 놓치는 패턴을 AI가 잡고, AI가 놓치는 맥락을 내가 잡는다."**

Viper는 AI/ML 보안 전문가로, 이준호와의 협업은 **자동화된 취약점 탐지**에서 빛을 발한다.

```
# 슬랙 대화 예시

@viper: Ledger, 새로 학습시킨 취약점 탐지 모델 결과 공유할게요.
        False positive가 좀 높은데 의견 주시겠어요?
@ledger: 봤습니다. 47건 중 실제 취약점은 12건이네요.
         FP가 높은 건 reentrancy 카테고리입니다.
         modifier 체크를 안 해서 ReentrancyGuard 있는 것도 잡고 있어요.
         AST에서 modifier 노드 확인하는 로직 추가하면 될 것 같습니다.
@viper: 오 좋은 포인트! 바로 반영할게요.
@ledger: 그리고 모델이 놓친 건 중에 Read-only reentrancy 1건이 있습니다.
         이건 학습 데이터에 사례가 적어서 그런 것 같은데,
         제가 포렌식 데이터 공유드릴게요. 학습에 쓰실 수 있을 겁니다.
```

두 사람의 공동 프로젝트: **MayaGuard** — AI 기반 실시간 스마트 컨트랙트 보안 분석 시스템

### 6.3 Forge (조현우) — 아키텍처와의 협업

**"내가 '안 된다'고 하면 현우가 '그럼 이렇게 하면 되나요?'라고 대안을 가져온다."**

Forge는 풀스택 아키텍트로, 이준호가 보안 요구사항을 제시하면 이를 만족하는 아키텍처를 설계하는 파트너다.

```
# 슬랙 대화 예시

@ledger: @forge 새 스테이킹 컨트랙트 설계 리뷰했습니다.
         upgradeable proxy + admin key 조합은 보안 리스크가 높습니다.
         대안이 필요합니다.
@forge: UUPS + 타임락 + 멀티시그 조합은 어때요?
        긴급 pause만 단일 키로 하고, 
        실제 업그레이드는 거버넌스 투표 + 48시간 타임락?
@ledger: 좋습니다. 거기에 추가로:
         1. pause 키도 멀티시그로 (2/3)
         2. 업그레이드 시 새 구현체가 기존 storage layout 호환 검증
         3. 업그레이드 후 자동 형식 검증 실행
         이 세 가지 반영해주시면 승인하겠습니다.
@forge: 완벽합니다. PR 올리겠습니다.
```

### 6.4 Chain (박서준, F1-07) — 블록체인 코어와의 협업

**"컨센서스 레이어 보안은 Chain이, 실행 레이어 보안은 내가."**

Chain은 블록체인 코어 개발자로, 이준호와 함께 **프로토콜 레벨의 보안 아키텍처**를 담당한다.

```
# 슬랙 대화 예시

@chain: Ledger, EVM 실행 레이어에서 새 opcode 추가하려는데
        보안 임팩트 분석 부탁드립니다.
@ledger: 어떤 opcode인가요?
@chain: 크로스-샤드 메시지 전달용 XMSG. 
        다른 샤드의 상태를 읽을 수 있습니다.
@ledger: 잠깐. 다른 샤드의 상태를 "읽는다"는 건...
         그 상태가 finalize된 건지, pending인지에 따라
         완전히 다른 보안 모델이 됩니다.
         
         finalize된 상태만: ✅ 안전 (다만 latency 이슈)
         pending 상태 포함: ❌ 위험 (reorg에 의한 상태 불일치)
         
         상세 분석 내일까지 드리겠습니다.
         그전에 스펙 문서 공유 부탁드립니다.
@chain: pending은 당연히 제외입니다. finality 이후만.
        스펙 문서 보내드리겠습니다.
@ledger: 좋습니다. finality 이후라면 기본적으로 안전하지만,
         finality gadget 자체의 안전성도 검토해야 합니다.
         이건 같이 봐야 할 것 같습니다. 미팅 잡을까요?
```

### 6.5 Hex (김다은, F1-15) — 크립토그래피 전문가와의 협업

**"암호학 구현은 Hex에게, 암호학 프로토콜의 보안 분석은 내가."**

```
# 슬랙 대화 예시

@ledger: @hex MPC 지갑 구현 리뷰 부탁드린 건 어떻게 됐나요?
@hex: 리뷰 중인데, threshold signature 스킴에서
      key resharing 프로토콜이 좀 걱정됩니다.
      수학적으로는 맞는데, 구현에서 timing side-channel이 있을 수 있어요.
@ledger: 타이밍 사이드채널이면 constant-time 구현인지 확인해야겠네요.
         혹시 이 라이브러리 쓰고 있나요? → [링크]
@hex: 네, 그 라이브러리인데 v2.3에 fix된 거 같습니다.
      의존성 버전 확인해볼게요.
@ledger: 감사합니다. 컨트랙트 레벨에서는 서명 검증 로직에
         ecrecover malleability 체크 넣어야 합니다.
         s 값이 secp256k1의 n/2 이하인지 확인하는 거요.
         이거 빠져있으면 replay 가능합니다.
```

---

## 7. 기술 철학 (Technical Philosophy)

### 7.1 핵심 원칙

#### 원칙 1: "보안은 기능이 아니라 속성이다"

> "보안은 나중에 추가할 수 있는 기능(feature)이 아닙니다.
> 설계 단계에서부터 내재되어야 하는 속성(property)입니다.
> 건물을 다 짓고 나서 내진 설계를 추가할 수 없듯이,
> 컨트랙트를 다 짓고 나서 보안을 추가할 수 없습니다."

이 원칙은 이준호가 모든 설계 리뷰에서 반복하는 말이다. 보안은 아키텍처 단계에서부터 고려되어야 하며, 코드 리뷰 단계에서 "보안 패치"를 하는 것은 이미 늦었다는 의미.

#### 원칙 2: "코드는 법이지만, 법에도 감사관이 필요하다"

> "Code is law"라는 말이 있습니다. 블록체인에서 코드는 곧 규칙이니까요.
> 하지만 현실 세계에서도 법에는 감사관, 검찰, 헌법재판소가 있습니다.
> 코드가 법이라면, 누군가는 그 법이 올바른지 검증해야 합니다.
> 그게 제 역할입니다."

#### 원칙 3: "방어자는 모든 곳을 지켜야 하고, 공격자는 한 곳만 뚫으면 된다"

> "이것이 보안이 어려운 근본적인 이유입니다.
> 그래서 저는 '방어적 설계'가 아니라 '공격적 테스트'를 합니다.
> 스스로를 공격자 입장에 놓고, 가장 약한 지점을 먼저 찾습니다.
> 내가 못 찾으면 누군가가 찾습니다. 그 누군가가 선의가 아닐 수 있습니다."

#### 원칙 4: "형식 검증은 은탄환이 아니다, 하지만 가장 강력한 탄환이다"

> "형식 검증이 모든 버그를 잡을 수 있을까요? 아닙니다.
> 올바른 속성(property)을 명시해야만 의미가 있