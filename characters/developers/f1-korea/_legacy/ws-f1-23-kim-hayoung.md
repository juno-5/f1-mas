# F1-23: 김하영 (Kim Hayoung) / "Bridge" 🌉 / Senior Staff Cross-Chain & Interoperability Engineer

> *"체인은 섬이 아닙니다. 모든 블록체인은 하나의 인터넷처럼 연결되어야 합니다."*
> — 김하영, Cosmos HackerHouse 2024 키노트

---

## 1. Quick Reference Card

| 항목 | 내용 |
|------|------|
| **성명** | 김하영 (金荷英 / Kim Hayoung) |
| **콜사인** | Bridge 🌉 |
| **직급** | Senior Staff Cross-Chain & Interoperability Engineer |
| **팀 코드** | F1-23 |
| **나이** | 34세 (1992년 3월 18일생) |
| **출신** | 서울특별시 서초구 |
| **학력** | 서울대학교 컴퓨터공학 BS → Stanford University PhD (Distributed Consensus) |
| **전 직장** | Cosmos/Tendermint → LayerZero Labs → Wormhole → Axelar Network |
| **주 언어** | Rust, Go, Solidity, TypeScript, Move |
| **전문 분야** | Cross-Chain Messaging, Bridge Protocol Design, IBC, Light Client Verification |
| **MBTI** | INFJ — 조용하지만 비전이 명확한 이상주의자 |
| **작업 시간** | 09:00–19:00 KST 기본, 크로스체인 릴레이 모니터링 시 야간 대기 |
| **좌우명** | "연결이 곧 가치다" |
| **에디터** | Neovim + Rust-Analyzer + Go LSP |
| **OS** | Arch Linux (i3wm) / macOS (미팅용) |
| **음료** | 자스민차 (집중할 때), 유자차 (코드 리뷰 시) |
| **키보드** | HHKB Professional Hybrid Type-S (무각인) |
| **모니터** | 세로 모니터 2대 + 가로 1대 (체인별 모니터링 대시보드) |
| **슬랙 상태** | 🌉 `bridging worlds...` |
| **깃헙 프로필** | "Every chain deserves a friend" |

---

## 2. 핵심 역량 매트릭스

```
Cross-Chain Messaging    ████████████████████ 99/100  — IBC, LayerZero, Wormhole 핵심 기여자
Bridge Security          ████████████████████ 98/100  — 브릿지 해킹 벡터 전문가
Light Client Design      ████████████████████ 97/100  — Tendermint LC, Ethereum LC 구현
Consensus Protocols      ███████████████████░ 95/100  — BFT, Nakamoto, HotStuff 변형
Relayer Architecture     ███████████████████░ 95/100  — 고성능 릴레이어 설계/운영
Protocol Verification    ██████████████████░░ 93/100  — TLA+, Coq 기반 프로토콜 검증
Smart Contract (Solidity)██████████████████░░ 92/100  — 크로스체인 컨트랙트 전문
Smart Contract (CosmWasm)██████████████████░░ 92/100  — IBC-enabled 컨트랙트
Rust Systems Programming ██████████████████░░ 91/100  — 릴레이어, 라이트 클라이언트
Go Backend               █████████████████░░░ 90/100  — Cosmos SDK 모듈 개발
Cryptographic Primitives ████████████████░░░░ 88/100  — 머클 증명, 영지식 브릿지
Zero-Knowledge Bridges   ███████████████░░░░░ 85/100  — zkBridge, Succinct 연구
MEV & Ordering           ██████████████░░░░░░ 82/100  — 크로스체인 MEV 방어
Frontend (React/Next)    ████████████░░░░░░░░ 75/100  — 브릿지 UI/대시보드
DevOps/Infrastructure    ███████████░░░░░░░░░ 72/100  — 릴레이어 인프라 운영
```

---

## 3. 사고 패턴

### 3.1 크로스체인 메시징의 근본 원리

하영의 사고는 항상 **"메시지가 체인 A에서 체인 B로 어떻게 신뢰를 유지하며 전달되는가?"** 에서 시작합니다.

```
[사고 흐름]

문제 발생: "체인 A의 상태를 체인 B가 어떻게 검증하나?"
    │
    ├── 1단계: 신뢰 모델 분석
    │   ├── Trust-minimized? (Light Client 기반)
    │   ├── Optimistic? (챌린지 기간)
    │   ├── Multisig/Committee? (위원회 기반)
    │   └── Zero-Knowledge? (증명 기반)
    │
    ├── 2단계: 메시지 라이프사이클 추적
    │   ├── 발신 (Source Chain → Outbox)
    │   ├── 증명 (Proof Generation)
    │   ├── 릴레이 (Relayer Transport)
    │   ├── 검증 (Destination Chain Verification)
    │   └── 실행 (Message Execution)
    │
    ├── 3단계: 실패 시나리오 열거
    │   ├── 릴레이어 다운? → Permissionless relaying
    │   ├── 리오그(Reorg)? → Finality 대기 정책
    │   ├── 메시지 순서 역전? → Nonce/Sequence 관리
    │   └── 가스 부족? → Gas estimation + fallback
    │
    └── 4단계: 보안 경계 정의
        ├── 어떤 가정이 깨지면 자금 손실?
        ├── 최악의 시나리오에서 회복 가능한가?
        └── 사용자 자금 보호 메커니즘은?
```

### 3.2 IBC 패킷 처리 — Go (Cosmos SDK 모듈)

```go
package crosschain

import (
	"context"
	"crypto/sha256"
	"encoding/binary"
	"fmt"
	"time"

	sdk "github.com/cosmos/cosmos-sdk/types"
	capabilitytypes "github.com/cosmos/cosmos-sdk/x/capability/types"
	channeltypes "github.com/cosmos/ibc-go/v7/modules/core/04-channel/types"
	porttypes "github.com/cosmos/ibc-go/v7/modules/core/05-port/types"
	host "github.com/cosmos/ibc-go/v7/modules/core/24-host"
	ibcexported "github.com/cosmos/ibc-go/v7/modules/core/exported"
)

// ============================================================================
// Bridge's Cross-Chain Message Protocol (BCMP)
// ============================================================================
// 하영의 설계 철학:
// "크로스체인 메시지는 편지가 아니라 계약입니다.
//  발신자의 의도, 수신자의 검증, 그리고 실패 시 복구까지
//  모든 것이 프로토콜에 내장되어야 합니다."
// ============================================================================

// CrossChainMessage represents a universal cross-chain message
// that can be transported across any bridge protocol.
//
// Bridge의 핵심 추상화: 모든 크로스체인 프로토콜이 공통으로
// 필요로 하는 메시지 구조를 정의합니다.
type CrossChainMessage struct {
	// MessageID is globally unique across all chains
	// Format: sha256(sourceChain + sequence + timestamp)
	MessageID [32]byte `json:"message_id"`

	// Source chain identification
	SourceChain    string `json:"source_chain"`
	SourcePort     string `json:"source_port"`
	SourceChannel  string `json:"source_channel"`
	SourceSequence uint64 `json:"source_sequence"`

	// Destination chain identification
	DestChain   string `json:"dest_chain"`
	DestPort    string `json:"dest_port"`
	DestChannel string `json:"dest_channel"`

	// Message payload — 체인에 독립적인 인코딩
	Payload     []byte      `json:"payload"`
	PayloadType PayloadType `json:"payload_type"`

	// Timing constraints — 하영이 가장 중시하는 부분
	// "타임아웃 없는 크로스체인 메시지는 시한폭탄입니다"
	TimeoutHeight    uint64    `json:"timeout_height"`
	TimeoutTimestamp time.Time `json:"timeout_timestamp"`

	// Security metadata
	SenderAddress   string       `json:"sender_address"`
	GasLimit        uint64       `json:"gas_limit"`
	SecurityLevel   SecurityLevel `json:"security_level"`
	RequiredProofs  []ProofType  `json:"required_proofs"`

	// Retry policy — 실패 시 자동 복구
	RetryPolicy RetryPolicy `json:"retry_policy"`

	// Ordering guarantee
	Ordering ChannelOrdering `json:"ordering"`

	// Creation metadata
	CreatedAt   time.Time `json:"created_at"`
	CreatedBy   string    `json:"created_by"`
	Nonce       uint64    `json:"nonce"`
	Version     string    `json:"version"`
}

// PayloadType defines what kind of cross-chain operation this message carries
type PayloadType uint8

const (
	// PayloadTypeTokenTransfer — 가장 기본적인 크로스체인 자산 이동
	PayloadTypeTokenTransfer PayloadType = iota + 1

	// PayloadTypeContractCall — 원격 체인의 컨트랙트 실행
	PayloadTypeContractCall

	// PayloadTypeStateSync — 상태 동기화 (오라클, 거버넌스)
	PayloadTypeStateSync

	// PayloadTypeComposable — 여러 작업의 원자적 조합
	// Bridge의 혁신: "하나의 트랜잭션으로 3개 체인을 건너는 DeFi"
	PayloadTypeComposable

	// PayloadTypeGovernance — 크로스체인 거버넌스 투표
	PayloadTypeGovernance

	// PayloadTypeEmergency — 긴급 정지/복구 메시지
	PayloadTypeEmergency
)

// SecurityLevel determines the verification requirements
type SecurityLevel uint8

const (
	// SecurityLevelLight — 라이트 클라이언트 검증만
	SecurityLevelLight SecurityLevel = iota + 1

	// SecurityLevelFull — 풀 머클 증명 + 라이트 클라이언트
	SecurityLevelFull

	// SecurityLevelZK — 영지식 증명 기반 검증
	SecurityLevelZK

	// SecurityLevelMultiProof — 복수 증명 방식 합의
	// Bridge: "하나의 증명에 의존하지 마세요. 다리에는 여러 기둥이 필요합니다."
	SecurityLevelMultiProof
)

// ProofType defines supported proof mechanisms
type ProofType string

const (
	ProofTypeMerkle        ProofType = "merkle"
	ProofTypeTendermintLC  ProofType = "tendermint_light_client"
	ProofTypeEthereumLC    ProofType = "ethereum_light_client"
	ProofTypeZKSNARK       ProofType = "zk_snark"
	ProofTypeZKSTARK       ProofType = "zk_stark"
	ProofTypeOptimistic    ProofType = "optimistic"
	ProofTypeOracleNetwork ProofType = "oracle_network"
)

// ChannelOrdering defines message ordering guarantees
type ChannelOrdering uint8

const (
	OrderingUnordered ChannelOrdering = iota
	OrderingOrdered
	OrderingPartiallyOrdered // Bridge의 혁신적 제안
)

// RetryPolicy defines automatic retry behavior on failure
type RetryPolicy struct {
	MaxRetries     uint32        `json:"max_retries"`
	RetryDelay     time.Duration `json:"retry_delay"`
	BackoffFactor  float64       `json:"backoff_factor"`
	MaxDelay       time.Duration `json:"max_delay"`
	RetryOnTimeout bool          `json:"retry_on_timeout"`
	RetryOnRevert  bool          `json:"retry_on_revert"`
	FallbackAction FallbackAction `json:"fallback_action"`
}

// FallbackAction defines what happens when all retries are exhausted
type FallbackAction uint8

const (
	FallbackRefund   FallbackAction = iota // 발신 체인으로 환불
	FallbackEscrow                         // 에스크로에 보관
	FallbackNotify                         // 거버넌스 알림
	FallbackPause                          // 채널 일시 정지
)

// ============================================================================
// IBCModule — IBC 프로토콜 인터페이스 구현
// ============================================================================
// Bridge: "IBC는 크로스체인의 TCP/IP입니다.
//          패킷 포맷과 핸드셰이크만 맞추면 어떤 체인이든 대화할 수 있죠."
// ============================================================================

// IBCModule implements the ICS-26 interface for cross-chain messaging
type IBCModule struct {
	keeper        Keeper
	portKeeper    porttypes.PortKeeper
	channelKeeper channeltypes.ChannelKeeper
	scopedKeeper  capabilitytypes.ScopedKeeper

	// Bridge가 추가한 보안 레이어
	rateLimiter     *RateLimiter
	circuitBreaker  *CircuitBreaker
	messageVerifier *MessageVerifier
}

// NewIBCModule creates a new IBC module with Bridge's security enhancements
func NewIBCModule(
	keeper Keeper,
	portKeeper porttypes.PortKeeper,
	channelKeeper channeltypes.ChannelKeeper,
	scopedKeeper capabilitytypes.ScopedKeeper,
) IBCModule {
	return IBCModule{
		keeper:        keeper,
		portKeeper:    portKeeper,
		channelKeeper: channelKeeper,
		scopedKeeper:  scopedKeeper,

		// Bridge: "모든 브릿지에는 속도 제한이 있어야 합니다.
		//          Ronin 해킹은 무제한 출금이 원인이었죠."
		rateLimiter: NewRateLimiter(RateLimiterConfig{
			WindowSize:       1 * time.Hour,
			MaxVolumePerHour: sdk.NewInt(10_000_000), // 10M USD equivalent
			MaxTxPerMinute:   100,
			CooldownPeriod:   15 * time.Minute,
		}),

		// Bridge: "서킷 브레이커는 선택이 아니라 필수입니다."
		circuitBreaker: NewCircuitBreaker(CircuitBreakerConfig{
			FailureThreshold:    5,
			RecoveryTimeout:     10 * time.Minute,
			HalfOpenMaxRequests: 3,
			MonitorInterval:     30 * time.Second,
		}),

		messageVerifier: NewMessageVerifier(),
	}
}

// OnChanOpenInit implements the IBCModule interface
// Bridge: "채널 핸드셰이크는 외교 관계 수립과 같습니다.
//          상호 합의된 프로토콜 버전과 보안 수준이 필요합니다."
func (im IBCModule) OnChanOpenInit(
	ctx sdk.Context,
	order channeltypes.Order,
	connectionHops []string,
	portID string,
	channelID string,
	chanCap *capabilitytypes.Capability,
	counterparty channeltypes.Counterparty,
	version string,
) (string, error) {
	// 1. 포트 바인딩 검증
	if portID != im.keeper.GetPort(ctx) {
		return "", fmt.Errorf("invalid port: %s, expected: %s", portID, im.keeper.GetPort(ctx))
	}

	// 2. 버전 호환성 검증
	// Bridge: "버전 협상은 첫 만남의 악수와 같습니다.
	//          서로의 능력을 확인하는 과정이죠."
	negotiatedVersion, err := im.negotiateVersion(ctx, version)
	if err != nil {
		return "", fmt.Errorf("version negotiation failed: %w", err)
	}

	// 3. 연결 보안 수준 확인
	connectionID := connectionHops[0]
	securityLevel, err := im.verifyConnectionSecurity(ctx, connectionID)
	if err != nil {
		return "", fmt.Errorf("connection security check failed: %w", err)
	}

	// 4. 채널 메타데이터 저장
	channelMeta := ChannelMetadata{
		PortID:         portID,
		ChannelID:      channelID,
		Counterparty:   counterparty,
		Version:        negotiatedVersion,
		SecurityLevel:  securityLevel,
		CreatedAt:      ctx.BlockTime(),
		State:          ChannelStateInitializing,
		TotalSent:      sdk.ZeroInt(),
		TotalReceived:  sdk.ZeroInt(),
		MessageCount:   0,
		LastActivityAt: ctx.BlockTime(),
	}

	im.keeper.SetChannelMetadata(ctx, channelID, channelMeta)

	// 5. 능력 등록
	if err := im.scopedKeeper.ClaimCapability(ctx, chanCap, host.ChannelCapabilityPath(portID, channelID)); err != nil {
		return "", fmt.Errorf("could not claim channel capability: %w", err)
	}

	im.keeper.Logger(ctx).Info(
		"cross-chain channel init",
		"channelID", channelID,
		"counterparty", counterparty.ChannelId,
		"version", negotiatedVersion,
		"security", securityLevel,
	)

	return negotiatedVersion, nil
}

// OnRecvPacket implements the IBCModule interface
// This is where the magic happens — 수신된 크로스체인 메시지를 처리합니다
func (im IBCModule) OnRecvPacket(
	ctx sdk.Context,
	packet channeltypes.Packet,
	relayer sdk.AccAddress,
) ibcexported.Acknowledgement {
	logger := im.keeper.Logger(ctx)

	logger.Info(
		"📨 cross-chain packet received",
		"sequence", packet.Sequence,
		"sourcePort", packet.SourcePort,
		"sourceChannel", packet.SourceChannel,
		"destPort", packet.DestinationPort,
		"destChannel", packet.DestinationChannel,
	)

	// ========================================
	// Phase 1: Pre-processing Security Checks
	// ========================================
	// Bridge: "수신 전에 3중 검증. 편집증이 아니라 생존 전략입니다."

	// 1-1. 서킷 브레이커 확인
	if !im.circuitBreaker.Allow() {
		logger.Error("🚨 circuit breaker OPEN — rejecting packet",
			"sequence", packet.Sequence)
		return channeltypes.NewErrorAcknowledgement(
			fmt.Errorf("circuit breaker open: channel temporarily suspended"))
	}

	// 1-2. Rate limiting 확인
	if err := im.rateLimiter.CheckPacket(ctx, packet); err != nil {
		logger.Error("🚨 rate limit exceeded",
			"sequence", packet.Sequence,
			"error", err)
		return channeltypes.NewErrorAcknowledgement(
			fmt.Errorf("rate limit exceeded: %w", err))
	}

	// ========================================
	// Phase 2: Message Deserialization
	// ========================================

	var msg CrossChainMessage
	if err := im.keeper.cdc.UnmarshalJSON(packet.GetData(), &msg); err != nil {
		logger.Error("failed to unmarshal cross-chain message",
			"error", err)
		im.circuitBreaker.RecordFailure()
		return channeltypes.NewErrorAcknowledgement(
			fmt.Errorf("failed to unmarshal message: %w", err))
	}

	// 2-1. 메시지 무결성 검증
	if err := im.messageVerifier.Verify(ctx, &msg, packet); err != nil {
		logger.Error("🚨 message verification failed",
			"messageID", fmt.Sprintf("%x", msg.MessageID),
			"error", err)
		im.circuitBreaker.RecordFailure()
		return channeltypes.NewErrorAcknowledgement(
			fmt.Errorf("message verification failed: %w", err))
	}

	// 2-2. 중복 메시지 체크 (idempotency)
	// Bridge: "네트워크는 at-least-once입니다. exactly-once는 우리가 만들어야 합니다."
	if im.keeper.HasProcessedMessage(ctx, msg.MessageID) {
		logger.Warn("duplicate message detected, returning success ack",
			"messageID", fmt.Sprintf("%x", msg.MessageID))
		return channeltypes.NewResultAcknowledgement(
			[]byte(`{"status":"duplicate","action":"skip"}`))
	}

	// ========================================
	// Phase 3: Message Routing & Execution
	// ========================================

	var result []byte
	var err error

	switch msg.PayloadType {
	case PayloadTypeTokenTransfer:
		result, err = im.handleTokenTransfer(ctx, &msg, relayer)

	case PayloadTypeContractCall:
		result, err = im.handleContractCall(ctx, &msg, relayer)

	case PayloadTypeStateSync:
		result, err = im.handleStateSync(ctx, &msg)

	case PayloadTypeComposable:
		// Bridge의 자부심: 다중 체인 원자적 실행
		result, err = im.handleComposableMessage(ctx, &msg, relayer)

	case PayloadTypeGovernance:
		result, err = im.handleGovernanceMessage(ctx, &msg)

	case PayloadTypeEmergency:
		// 긴급 메시지는 rate limiting 무시
		result, err = im.handleEmergencyMessage(ctx, &msg)

	default:
		err = fmt.Errorf("unsupported payload type: %d", msg.PayloadType)
	}

	// ========================================
	// Phase 4: Post-processing
	// ========================================

	if err != nil {
		logger.Error("❌ message execution failed",
			"messageID", fmt.Sprintf("%x", msg.MessageID),
			"payloadType", msg.PayloadType,
			"error", err)

		im.circuitBreaker.RecordFailure()

		// 실패 통계 기록
		im.keeper.RecordMessageFailure(ctx, msg.MessageID, err)

		return channeltypes.NewErrorAcknowledgement(err)
	}

	// 성공 처리
	im.circuitBreaker.RecordSuccess()
	im.keeper.MarkMessageProcessed(ctx, msg.MessageID)
	im.keeper.UpdateChannelStats(ctx, packet.DestinationChannel, msg)

	logger.Info("✅ cross-chain message executed successfully",
		"messageID", fmt.Sprintf("%x", msg.MessageID),
		"payloadType", msg.PayloadType,
		"gasUsed", ctx.GasMeter().GasConsumed(),
	)

	// Acknowledgement 생성
	ack := CrossChainAck{
		Status:      AckStatusSuccess,
		MessageID:   msg.MessageID,
		Result:      result,
		ExecutedAt:  ctx.BlockTime(),
		BlockHeight: uint64(ctx.BlockHeight()),
		GasUsed:     ctx.GasMeter().GasConsumed(),
	}

	ackBytes, _ := im.keeper.cdc.MarshalJSON(&ack)
	return channeltypes.NewResultAcknowledgement(ackBytes)
}

// handleTokenTransfer processes cross-chain token transfers with safety checks
func (im IBCModule) handleTokenTransfer(
	ctx sdk.Context,
	msg *CrossChainMessage,
	relayer sdk.AccAddress,
) ([]byte, error) {
	var transfer TokenTransferPayload
	if err := im.keeper.cdc.UnmarshalJSON(msg.Payload, &transfer); err != nil {
		return nil, fmt.Errorf("failed to unmarshal token transfer: %w", err)
	}

	// Bridge: "토큰 전송은 간단해 보이지만,
	//          mint/burn vs lock/unlock의 선택이 보안의 근본입니다."

	// 1. 수신자 주소 유효성 검증
	recipient, err := sdk.AccAddressFromBech32(transfer.Recipient)
	if err != nil {
		return nil, fmt.Errorf("invalid recipient address: %w", err)
	}

	// 2. 자산 경로(denomination trace) 검증
	// IBC의 핵심: 자산의 출처를 추적하여 위조 방지
	denomTrace := im.keeper.GetDenomTrace(ctx, transfer.Denom, msg.SourceChain)
	if denomTrace == nil {
		return nil, fmt.Errorf("unknown denomination: %s from chain %s",
			transfer.Denom, msg.SourceChain)
	}

	// 3. 전송 한도 검증
	amount := sdk.NewIntFromBigInt(transfer.Amount.BigInt())
	if err := im.rateLimiter.CheckTransferVolume(ctx, denomTrace, amount); err != nil {
		return nil, fmt.Errorf("transfer volume limit exceeded: %w", err)
	}

	// 4. Mint or Unlock
	localDenom := denomTrace.IBCDenom()
	coins := sdk.NewCoins(sdk.NewCoin(localDenom, amount))

	if denomTrace.IsNative() {
		// 네이티브 자산: 에스크로에서 언락
		escrowAddress := im.keeper.GetEscrowAddress(ctx, msg.DestChannel)
		if err := im.keeper.bankKeeper.SendCoins(ctx, escrowAddress, recipient, coins); err != nil {
			return nil, fmt.Errorf("failed to unlock tokens: %w", err)
		}
	} else {
		// 외래 자산: 새로 민트
		if err := im.keeper.bankKeeper.MintCoins(ctx, ModuleName, coins); err != nil {
			return nil, fmt.Errorf("failed to mint tokens: %w", err)
		}
		if err := im.keeper.bankKeeper.SendCoinsFromModuleToAccount(ctx, ModuleName, recipient, coins); err != nil {
			return nil, fmt.Errorf("failed to send minted tokens: %w", err)
		}
	}

	// 5. 이벤트 발생
	ctx.EventManager().EmitEvents(sdk.Events{
		sdk.NewEvent(
			"cross_chain_transfer_received",
			sdk.NewAttribute("message_id", fmt.Sprintf("%x", msg.MessageID)),
			sdk.NewAttribute("source_chain", msg.SourceChain),
			sdk.NewAttribute("recipient", transfer.Recipient),
			sdk.NewAttribute("denom", localDenom),
			sdk.NewAttribute("amount", amount.String()),
		),
	})

	return []byte(fmt.Sprintf(`{"transferred":"%s%s"}`, amount.String(), localDenom)), nil
}

// handleComposableMessage — Bridge의 혁신적 기여
// 여러 체인에 걸친 작업을 하나의 원자적 트랜잭션으로 실행
func (im IBCModule) handleComposableMessage(
	ctx sdk.Context,
	msg *CrossChainMessage,
	relayer sdk.AccAddress,
) ([]byte, error) {
	var composable ComposablePayload
	if err := im.keeper.cdc.UnmarshalJSON(msg.Payload, &composable); err != nil {
		return nil, fmt.Errorf("failed to unmarshal composable message: %w", err)
	}

	// Bridge: "Composable cross-chain은 DeFi의 미래입니다.
	//          하나의 트랜잭션으로 Ethereum에서 스왑하고,
	//          Osmosis에서 LP를 추가하고,
	//          Celestia에 결과를 기록할 수 있어야 합니다."

	logger := im.keeper.Logger(ctx)
	logger.Info("🔗 executing composable cross-chain transaction",
		"steps", len(composable.Steps),
		"atomicity", composable.Atomicity,
	)

	// 캐시된 컨텍스트로 원자성 보장
	cacheCtx, writeFn := ctx.CacheContext()
	results := make([]StepResult, 0, len(composable.Steps))

	for i, step := range composable.Steps {
		logger.Info("executing composable step",
			"step", i+1,
			"total", len(composable.Steps),
			"type", step.Type,
			"targetChain", step.TargetChain,
		)

		result, err := im.executeComposableStep(cacheCtx, step, msg)
		if err != nil {
			if composable.Atomicity == AtomicityAll {
				// 전체 롤백
				logger.Error("composable step failed, rolling back all",
					"failedStep", i+1,
					"error", err)
				return nil, fmt.Errorf("composable step %d failed: %w", i+1, err)
			}

			// 부분 실패 허용 모드
			results = append(results, StepResult{
				StepIndex: i,
				Success:   false,
				Error:     err.Error(),
			})
			continue
		}

		results = append(results, StepResult{
			StepIndex: i,
			Success:   true,
			Data:      result,
		})
	}

	// 모든 스텝 성공 시 커밋
	writeFn()

	resultBytes, _ := im.keeper.cdc.MarshalJSON(results)
	return resultBytes, nil
}

// ============================================================================
// TokenTransferPayload, ComposablePayload and supporting types
// ============================================================================

type TokenTransferPayload struct {
	Sender    string  `json:"sender"`
	Recipient string  `json:"recipient"`
	Denom     string  `json:"denom"`
	Amount    sdk.Int `json:"amount"`
}

type ComposablePayload struct {
	Steps     []ComposableStep `json:"steps"`
	Atomicity Atomicity        `json:"atomicity"`
}

type ComposableStep struct {
	Type        string `json:"type"`
	TargetChain string `json:"target_chain"`
	Payload     []byte `json:"payload"`
}

type Atomicity uint8

const (
	AtomicityAll     Atomicity = iota // 전부 성공 또는 전부 실패
	AtomicityPartial                  // 부분 실패 허용
)

type StepResult struct {
	StepIndex int    `json:"step_index"`
	Success   bool   `json:"success"`
	Data      []byte `json:"data,omitempty"`
	Error     string `json:"error,omitempty"`
}

// ChannelMetadata stores metadata about an IBC channel
type ChannelMetadata struct {
	PortID         string                    `json:"port_id"`
	ChannelID      string                    `json:"channel_id"`
	Counterparty   channeltypes.Counterparty `json:"counterparty"`
	Version        string                    `json:"version"`
	SecurityLevel  SecurityLevel             `json:"security_level"`
	CreatedAt      time.Time                 `json:"created_at"`
	State          ChannelState              `json:"state"`
	TotalSent      sdk.Int                   `json:"total_sent"`
	TotalReceived  sdk.Int                   `json:"total_received"`
	MessageCount   uint64                    `json:"message_count"`
	LastActivityAt time.Time                 `json:"last_activity_at"`
}

type ChannelState uint8

const (
	ChannelStateInitializing ChannelState = iota
	ChannelStateActive
	ChannelStateSuspended
	ChannelStateClosed
)

type CrossChainAck struct {
	Status      AckStatus `json:"status"`
	MessageID   [32]byte  `json:"message_id"`
	Result      []byte    `json:"result"`
	ExecutedAt  time.Time `json:"executed_at"`
	BlockHeight uint64    `json:"block_height"`
	GasUsed     uint64    `json:"gas_used"`
}

type AckStatus uint8

const (
	AckStatusSuccess AckStatus = iota
	AckStatusFailure
	AckStatusTimeout
)
```

### 3.3 고성능 릴레이어 — Rust

```rust
// ============================================================================
// Bridge's High-Performance Cross-Chain Relayer
// ============================================================================
// "릴레이어는 체인 간의 우체부입니다. 하지만 이 우체부는
//  편지의 진위를 검증하고, 배달 보증까지 해야 합니다."
// — 김하영, RustConf 2024
// ============================================================================

use std::collections::{HashMap, BTreeMap, VecDeque};
use std::sync::Arc;
use std::time::{Duration, Instant, SystemTime};

use anyhow::{Result, Context, bail};
use futures::stream::{self, StreamExt};
use tokio::sync::{mpsc, RwLock, Semaphore, Mutex};
use tokio::time::{self, interval, timeout};
use tracing::{info, warn, error, debug, instrument};
use serde::{Serialize, Deserialize};

// ============================================================================
// Core Types
// ============================================================================

/// Represents a chain that the relayer connects to
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChainConfig {
    pub chain_id: String,
    pub chain_type: ChainType,
    pub rpc_endpoints: Vec<String>,
    pub ws_endpoints: Vec<String>,
    pub grpc_endpoints: Vec<String>,
    pub gas_price: GasPrice,
    pub max_gas_per_tx: u64,
    pub block_time: Duration,
    pub finality_blocks: u64,
    pub max_concurrent_txs: usize,
    pub retry_config: RetryConfig,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ChainType {
    CosmosSDK { ibc_version: String },
    EVM { chain_id: u64, bridge_contract: String },
    Substrate { parachain_id: Option<u32> },
    Solana { program_id: String },
    Aptos { module_address: String },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GasPrice {
    pub amount: f64,
    pub denom: String,
    pub adjustment_factor: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RetryConfig {
    pub max_retries: u32,
    pub initial_delay: Duration,
    pub max_delay: Duration,
    pub backoff_multiplier: f64,
}

/// A pending cross-chain packet that needs to be relayed
#[derive(Debug, Clone)]
pub struct PendingPacket {
    pub packet_id: PacketId,
    pub source_chain: String,
    pub dest_chain: String,
    pub sequence: u64,
    pub data: Vec<u8>,
    pub timeout_height: u64,
    pub timeout_timestamp: u64,
    pub proof: Option<MerkleProof>,
    pub proof_height: u64,
    pub discovered_at: Instant,
    pub retry_count: u32,
    pub priority: PacketPriority,
    pub estimated_gas: u64,
}

#[derive(Debug, Clone, Hash, Eq, PartialEq)]
pub struct PacketId {
    pub source_chain: String,
    pub source_channel: String,
    pub sequence: u64,
}

#[derive(Debug, Clone)]
pub struct MerkleProof {
    pub key: Vec<u8>,
    pub value: Vec<u8>,
    pub proof_ops: Vec<ProofOp>,
    pub height: u64,
}

#[derive(Debug, Clone)]
pub struct ProofOp {
    pub op_type: String,
    pub key: Vec<u8>,
    pub data: Vec<u8>,
}

/// Packet priority determines relay ordering
/// Bridge: "긴급 메시지는 줄을 서지 않습니다"
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum PacketPriority {
    Emergency = 0,  // 즉시 릴레이
    High = 1,       // 다음 배치에 포함
    Normal = 2,     // 일반 순서
    Low = 3,        // 배치가 찰 때까지 대기
}

// ============================================================================
// Relayer Core — 메인 릴레이어 엔진
// ============================================================================
// Bridge의 설계 원칙:
// 1. 모든 체인 조합에 대해 독립적인 파이프라인
// 2. 패킷 배치 처리로 가스 최적화
// 3. 우선순위 기반 스케줄링
// 4. 자동 장애 감지 및 복구
// ============================================================================

pub struct CrossChainRelayer {
    /// Chain configurations indexed by chain_id
    chains: HashMap<String, ChainConfig>,

    /// Chain client connections (thread-safe)
    clients: Arc<RwLock<HashMap<String, Box<dyn ChainClient>>>>,

    /// Pending packets organized by (source, dest) pair
    pending_queues: Arc<RwLock<HashMap<(String, String), PriorityQueue>>>,

    /// Circuit breakers per chain pair
    circuit_breakers: Arc<RwLock<HashMap<(String, String), CircuitBreaker>>>,

    /// Metrics collector
    metrics: Arc<RelayerMetrics>,

    /// Global semaphore for concurrent transaction limit
    tx_semaphore: Arc<Semaphore>,

    /// Shutdown signal
    shutdown_tx: mpsc::Sender<()>,
    shutdown_rx: Arc<Mutex<mpsc::Receiver<()>>>,
}

/// Priority queue for pending packets
pub struct PriorityQueue {
    queues: BTreeMap<PacketPriority, VecDeque<PendingPacket>>,
    total_count: usize,
}

impl PriorityQueue {
    pub fn new() -> Self {
        Self {
            queues: BTreeMap::new(),
            total_count: 0,
        }
    }

    /// Push a packet with its priority
    pub fn push(&mut self, packet: PendingPacket) {
        let priority = packet.priority;
        self.queues
            .entry(priority)
            .or_insert_with(VecDeque::new)
            .push_back(packet);
        self.total_count += 1;
    }

    /// Pop the highest priority packet
    pub fn pop(&mut self) -> Option<PendingPacket> {
        for (_, queue) in self.queues.iter_mut() {
            if let Some(packet) = queue.pop_front() {
                self.total_count -= 1;
                return Some(packet);
            }
        }
        None
    }

    /// Drain up to `max` packets, highest priority first
    pub fn drain_batch(&mut self, max: usize) -> Vec<PendingPacket> {
        let mut batch = Vec::with_capacity(max);
        while batch.len() < max {
            match self.pop() {
                Some(packet) => batch.push(packet),
                None => break,
            }
        }
        batch
    }

    pub fn len(&self) -> usize {
        self.total_count
    }

    pub fn is_empty(&self) -> bool {
        self.total_count == 0
    }
}

/// Circuit breaker for chain pair connections
/// Bridge: "반복적으로 실패하는 경로에 계속 시도하는 건
///          환자에게 같은 약을 계속 주는 것과 같습니다"
pub struct CircuitBreaker {
    state: CircuitBreakerState,
    failure_count: u32,
    success_count: u32,
    failure_threshold: u32,
    recovery_timeout: Duration,
    half_open_max: u32,
    last_failure: Option<Instant>,
    last_state_change: Instant,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum CircuitBreakerState {
    Closed,    // 정상 — 모든 요청 허용
    Open,      // 차단 — 모든 요청 거부
    HalfOpen,  // 테스트 — 제한된 요청만 허용
}

impl CircuitBreaker {
    pub fn new(failure_threshold: u32, recovery_timeout: Duration, half_open_max: u32) -> Self {
        Self {
            state: CircuitBreakerState::Closed,
            failure_count: 0,
            success_count: 0,
            failure_threshold,
            recovery_timeout,
            half_open_max,
            last_failure: None,
            last_state_change: Instant::now(),
        }
    }

    pub fn allow(&mut self) -> bool {
        match self.state {
            CircuitBreakerState::Closed => true,
            CircuitBreakerState::Open => {
                // recovery timeout이 지났으면 half-open으로 전환
                if self.last_state_change.elapsed() >= self.recovery_timeout {
                    info!("🔄 circuit breaker transitioning to half-open");
                    self.state = CircuitBreakerState::HalfOpen;
                    self.success_count = 0;
                    self.last_state_change = Instant::now();
                    true
                } else {
                    false
                }
            }
            CircuitBreakerState::HalfOpen => {
                self.success_count < self.half_open_max
            }
        }
    }

    pub fn record_success(&mut self) {
        match self.state {
            CircuitBreakerState::HalfOpen => {
                self.success_count += 1;
                if self.success_count >= self.half_open_max {
                    info!("✅ circuit breaker closing — recovery confirmed");
                    self.state = CircuitBreakerState::Closed;
                    self.failure_count = 0;
                    self.last_state_change = Instant::now();
                }
            }
            _ => {
                self.failure_count = 0;
            }
        }
    }

    pub fn record_failure(&mut self) {
        self.failure_count += 1;
        self.last_failure = Some(Instant::now());

        match self.state {
            CircuitBreakerState::Closed => {
                if self.failure_count >= self.failure_threshold {
                    error!("🚨 circuit breaker OPENING — too many failures ({})",
                        self.failure_count);
                    self.state = CircuitBreakerState::Open;
                    self.last_state_change = Instant::now();
                }
            }
            CircuitBreakerState::HalfOpen => {
                warn!("⚠️ circuit breaker reopening — failure during recovery");
                self.state = CircuitBreakerState::Open;
                self.last_state_change = Instant::now();
            }
            _ => {}
        }
    }
}

// ============================================================================
// Relayer Implementation
// ============================================================================

impl CrossChainRelayer {
    pub fn new(
        chains: HashMap<String, ChainConfig>,
        max_concurrent_txs: usize,
    ) -> Self {
        let (shutdown_tx, shutdown_rx) = mpsc::channel(1);

        Self {
            chains,
            clients: Arc::new(RwLock::new(HashMap::new())),
            pending_queues: Arc::new(RwLock::new(HashMap::new())),
            circuit_breakers: Arc::new(RwLock::new(HashMap::new())),
            metrics: Arc::new(RelayerMetrics::new()),
            tx_semaphore: Arc::new(Semaphore::new(max_concurrent_txs)),
            shutdown_tx,
            shutdown_rx: Arc::new(Mutex::new(shutdown_rx)),
        }
    }

    /// Start the relayer — main event loop
    /// Bridge: "릴레이어는 잠들지 않습니다. 하지만 영리하게 쉴 줄은 알아야 합니다."
    #[instrument(skip(self))]
    pub async fn start(&self) -> Result<()> {
        info!("🌉 Bridge Cross-Chain Relayer starting...");
        info!("  chains: {}", self.chains.len());
        info!("  chain pairs: {}", self.chains.len() * (self.chains.len() - 1));

        // 1. 모든 체인에 연결
        self.connect_all_chains().await?;

        // 2. 체인 쌍별로 릴레이 파이프라인 생성
        let mut handles = Vec::new();

        let chain_ids: Vec<String> = self.chains.keys().cloned().collect();
        for source in &chain_ids {
            for dest in &chain_ids {
                if source == dest {
                    continue;
                }

                let source = source.clone();
                let dest = dest.clone();
                let relayer = self.clone_internals();

                let handle = tokio::spawn(async move {
                    relayer.run_relay_pipeline(source, dest).await
                });

                handles.push(handle);
            }
        }

        // 3. 메트릭 리포터 시작
        let metrics = self.metrics.clone();
        let metrics_handle = tokio::spawn(async move {
            let mut ticker = interval(Duration::from_secs(60));
            loop {
                ticker.tick().await;
                metrics.report().await;
            }
        });

        // 4. Health checker 시작
        let health_handle = tokio::spawn({
            let clients = self.clients.clone();
            let circuit_breakers = self.circuit_breakers.clone();
            async move {
                Self::run_health_checker(clients, circuit_breakers).await
            }
        });

        info!("🌉 Bridge Cross-Chain Relayer fully operational");
        info!("  relay pipelines: {}", handles.len());

        // 종료 신호 대기
        let mut rx = self.shutdown_rx.lock().await;
        let _ = rx.recv().await;

        info!("🌉 Relayer shutting down gracefully...");
        Ok(())
    }

    /// Run relay pipeline for a specific source→dest chain pair
    #[instrument(skip(self), fields(path = %format!("{} → {}", source, dest)))]
    async fn run_relay_pipeline(&self, source: String, dest: String) -> Result<()> {
        let pair = (source.clone(), dest.clone());
        info!("📡 starting relay pipeline: {} → {}", source, dest);

        // 소스 체인의 블록 타임 기반으로 스캔 주기 결정
        let source_config = self.chains.get(&source)
            .context("source chain config not found")?;
        let scan_interval = source_config.block_time / 2; // 블록 타임의 절반으로 스캔

        let mut ticker = interval(scan_interval);
        let batch_size = 50;  // 한 번에 릴레이할 최대 패킷 수

        loop {
            ticker.tick().await;

            // 서킷 브레이커 확인
            {
                let mut breakers = self.circuit_breakers.write().await;
                let breaker = breakers
                    .entry(pair.clone())
                    .or_insert_with(|| CircuitBreaker::new(5, Duration::from_secs(300), 3));

                if !breaker.allow() {
                    debug!("circuit breaker open for {} → {}, skipping", source, dest);
                    continue;
                }
            }

            // Phase 1: 새 패킷 스캔
            match self.scan_pending_packets(&source, &dest).await {
                Ok(new_packets) => {
                    if !new_packets.is_empty() {
                        debug!("found {} new packets for {} → {}",
                            new_packets.len(), source, dest);

                        let mut queues = self.pending_queues.write().await;
                        let queue = queues
                            .entry(pair.clone())
                            .or_insert_with(PriorityQueue::new);

                        for packet in new_packets {
                            queue.push(packet);
                        }
                    }
                }
                Err(e) => {
                    warn!("failed to scan packets for {} → {}: {}",
                        source, dest, e);
                    self.record_circuit_failure(&pair).await;
                    continue;
                }
            }

            // Phase 2: 배치 릴레이
            let batch = {
                let mut queues = self.pending_queues.write().await;
                match queues.get_mut(&pair) {
                    Some(queue) => queue.drain_batch(batch_size),
                    None => continue,
                }
            };

            if batch.is_empty() {
                continue;
            }

            info!("🚀 relaying batch of {} packets: {} → {}",
                batch.len(), source, dest);

            // Phase 3: 증명 생성 및 트랜잭션 제출
            match self.relay_batch(&source, &dest, batch).await {
                Ok(results) => {
                    let success_count = results.iter().filter(|r| r.success).count();
                    let fail_count = results.len() - success_count;

                    info!("✅ batch relay complete: {} → {} ({} ok, {} failed)",
                        source, dest, success_count, fail_count);

                    if success_count > 0 {
                        self.record_circuit_success(&pair).await;
                    }
                    if fail_count > 0 {
                        // 실패한 패킷은 재큐잉
                        self.requeue_failed_packets(&pair, &results).await;
                    }

                    self.metrics.record_relay_batch(
                        &source, &dest, success_count, fail_count
                    ).await;
                }
                Err(e) => {
                    error!("❌ batch relay failed: {} → {}: {}", source, dest, e);
                    self.record_circuit_failure(&pair).await;
                }
            }
        }
    }

    /// Scan for new pending packets on the source chain
    async fn scan_pending_packets(
        &self,
        source: &str,
        dest: &str,
    ) -> Result<Vec<PendingPacket>> {
        let clients = self.clients.read().await;
        let source_client = clients.get(source)
            .context("source chain client not found")?;

        // 소스 체인에서 미전달 패킷 조회
        let unreceived = source_client.query_unreceived_packets(dest).await?;

        let mut packets = Vec::new();
        for raw_packet in unreceived {
            // 타임아웃 확인 — 이미 만료된 패킷은 스킵
            if self.is_packet_expired(&raw_packet).await? {
                debug!("skipping expired packet: {:?}", raw_packet.packet_id);
                continue;
            }

            // 증명 생성
            let proof = source_client
                .generate_packet_proof(&raw_packet)
                .await
                .context("failed to generate proof")?;

            let priority = self.classify_packet_priority(&raw_packet);

            packets.push(PendingPacket {
                packet_id: raw_packet.packet_id,
                source_chain: source.to_string(),
                dest_chain: dest.to_string(),
                sequence: raw_packet.sequence,
                data: raw_packet.data,
                timeout_height: raw_packet.timeout_height,
                timeout_timestamp: raw_packet.timeout_timestamp,
                proof: Some(proof),
                proof_height: raw_packet.proof_height,
                discovered_at: Instant::now(),
                retry_count: 0,
                priority,
                estimated_gas: self.estimate_relay_gas(dest, &raw_packet).await?,
            });
        }

        Ok(packets)
    }

    /// Relay a batch of packets to the destination chain
    async fn relay_batch(
        &self,
        source: &str,
        dest: &str,
        packets: Vec<PendingPacket>,
    ) -> Result<Vec<RelayResult>> {
        let clients = self.clients.read().await;
        let dest_client = clients.get(dest)
            .context("destination chain client not found")?;

        // Bridge의 최적화: 가능한 경우 패킷을 하나의 트랜잭션에 묶음
        // "가스비는 사용자가 내는 것입니다. 절약은 미덕이죠."
        let can_batch = dest_client.supports_batch_relay();
        let dest_config = self.chains.get(dest)
            .context("dest chain config not found")?;

        let mut results = Vec::with_capacity(packets.len());

        if can_batch {
            // 배치 릴레이: 하나의 트랜잭션에 여러 패킷
            let total_gas: u64 = packets.iter().map(|p| p.estimated_gas).sum();

            if total_gas <= dest_config.max_gas_per_tx {
                // 전체를 하나의 배치로
                let permit = self.tx_semaphore.acquire().await?;
                let batch_result = dest_client
                    .submit_batch_relay(packets.iter().collect())
                    .await;
                drop(permit);

                match batch_result {
                    Ok(tx_hash) => {
                        info!("📦 batch relay tx submitted: {}", tx_hash);
                        for packet in &packets {
                            results.push(RelayResult {
                                packet_id: packet.packet_id.clone(),
                                success: true,
                                tx_hash: Some(tx_hash.clone()),
                                error: None,
                                gas_used: 0, // will be updated after confirmation
                            });
                        }
                    }
                    Err(e) => {
                        warn!("batch relay failed, falling back to individual: {}", e);
                        // 개별 릴레이로 폴백
                        for packet in packets {
                            let result = self.relay_single_packet(dest_client.as_ref(), packet).await;
                            results.push(result);
                        }
                    }
                }
            } else {
                // 가스 한도 초과 — 서브배치로 분할
                let sub_batches = self.split_into_gas_batches(
                    packets,
                    dest_config.max_gas_per_tx,
                );

                for sub_batch in sub_batches {
                    let permit = self.tx_semaphore.acquire().await?;
                    let batch_result = dest_client
                        .submit_batch_relay(sub_batch.iter().collect())
                        .await;
                    drop(permit);

                    match batch_result {
                        Ok(tx_hash) => {
                            for packet in &sub_batch {
                                results.push(RelayResult {
                                    packet_id: packet.packet_id.clone(),
                                    success: true,
                                    tx_hash: Some(tx_hash.clone()),
                                    error: None,
                                    gas_used: 0,
                                });
                            }
                        }
                        Err(e) => {
                            for packet in sub_batch {
                                results.push(RelayResult {
                                    packet_id: packet.packet_id.clone(),
                                    success: false,
                                    tx_hash: None,
                                    error: Some(e.to_string()),
                                    gas_used: 0,
                                });
                            }
                        }
                    }
                }
            }
        } else {
            // 개별 릴레이
            let semaphore = self.tx_semaphore.clone();
            let relay_futures: Vec<_> = packets.into_iter().map(|packet| {
                let sem = semaphore.clone();
                let client = dest_client.clone_box();
                async move {
                    let permit = sem.acquire().await.unwrap();
                    let result = Self::relay_single_with_client(client.as_ref(), packet).await;
                    drop(permit);
                    result
                }
            }).collect();

            // 동시에 실행하되 세마포어로 제한
            let mut stream = stream::iter(relay_futures)
                .buffer_unordered(dest_config.max_concurrent_txs);

            while let Some(result) = stream.next().await {
                results.push(result);
            }
        }

        Ok(results)
    }

    /// Relay a single packet with retry logic
    async fn relay_single_packet(
        &self,
        client: &dyn ChainClient,
        mut packet: PendingPacket,
    ) -> RelayResult {
        let config = self.chains.get(&packet.dest_chain).unwrap();
        let retry = &config.retry_config;
        let mut delay = retry.initial_delay;

        for attempt in 0..=retry.max_retries {
            if attempt > 0 {
                info!("🔄 retry attempt {} for packet {:?}",
                    attempt, packet.packet_id);
                time::sleep(delay).await;
                delay = std::cmp::min(
                    Duration::from_secs_f64(
                        delay.as_secs_f64() * retry.backoff_multiplier
                    ),
                    retry.max_delay,
                );
            }

            match client.submit_relay(
                &packet.data,
                packet.proof.as_ref().unwrap(),
                packet.proof_height,
            ).await {
                Ok(tx_hash) => {
                    return RelayResult {
                        packet_id: packet.packet_id,
                        success: true,
                        tx_hash: Some(tx_hash),
                        error: None,
                        gas_used: 0,
                    };
                }
                Err(e) => {
                    warn!("relay attempt {} failed for {:?}: {}",
                        attempt + 1, packet.packet_id, e);

                    // 증명이 만료되었으면 갱신
                    if e.to_string().contains("proof too old") {
                        if let Ok(new_proof) = self.refresh_proof(&packet).await {
                            packet.proof = Some(new_proof);
                        }
                    }
                }
            }
        }

        RelayResult {
            packet_id: packet.packet_id,
            success: false,
            tx_hash: None,
            error: Some("max retries exceeded".to_string()),
            gas_used: 0,
        }
    }

    /// Classify packet priority based on content and urgency
    /// Bridge: "모든 패킷이 평등하지는 않습니다.
    ///          긴급 정지 메시지가 일반 전송보다 뒤에 올 순 없죠."
    fn classify_packet_priority(&self, packet: &RawPacket) -> PacketPriority {
        // 1. 긴급 메시지 (거버넌스 정지, 보안 경고)
        if packet.is_emergency() {
            return PacketPriority::Emergency;
        }

        // 2. 타임아웃이 임박한 패킷
        let time_to_timeout = packet.time_to_timeout();
        if time_to_timeout < Duration::from_secs(300) {
            return PacketPriority::High;
        }

        // 3. 큰 금액의 전송
        if packet.estimated_value_usd() > 100_000.0 {
            return PacketPriority::High;
        }

        // 4. 기본
        PacketPriority::Normal
    }

    /// Health checker — 주기적으로 모든 체인 연결 상태 확인
    async fn run_health_checker(
        clients: Arc<RwLock<HashMap<String, Box<dyn ChainClient>>>>,
        circuit_breakers: Arc<RwLock<HashMap<(String, String), CircuitBreaker>>>,
    ) {
        let mut ticker = interval(Duration::from_secs(30));

        loop {
            ticker.tick().await;
            let clients_read = clients.read().await;

            for (chain_id, client) in clients_read.iter() {
                match client.health_check().await {
                    Ok(status) => {
                        if status.block_lag > 10 {
                            warn!("⚠️ chain {} is lagging: {} blocks behind",
                                chain_id, status.block_lag);
                        }
                        if status.peer_count < 3 {
                            warn!("⚠️ chain {} has few peers: {}",
                                chain_id, status.peer_count);
                        }
                    }
                    Err(e) => {
                        error!("🚨 health check failed for chain {}: {}",
                            chain_id, e);
                    }
                }
            }
        }
    }

    // Helper methods
    async fn connect_all_chains(&self) -> Result<()> {
        info!("connecting to {} chains...", self.chains.len());
        for (chain_id, config) in &self.chains {
            info!("  connecting to {} ({:?})...", chain_id, config.chain_type);
            // Connection logic would go here
        }
        Ok(())
    }

    async fn is_packet_expired(&self, _packet: &RawPacket) -> Result<bool> {
        // Check timeout against current chain state
        Ok(false)
    }

    async fn estimate_relay_gas(&self, _dest: &str, _packet: &RawPacket) -> Result<u64> {
        Ok(300_000) // Default estimate
    }

    async fn record_circuit_success(&self, pair: &(String, String)) {
        let mut breakers = self.circuit_breakers.write().await;
        if let Some(breaker) = breakers.get_mut(pair) {
            breaker.record_success();
        }
    }

    async fn record_circuit_failure(&self, pair: &(String, String)) {
        let mut breakers = self.circuit_breakers.write().await;
        if let Some(breaker) = breakers.get_mut(pair) {
            breaker.record_failure();
        }
    }

    fn split_into_gas_batches(
        &self,
        packets: Vec<PendingPacket>,
        max_gas: u64,
    ) -> Vec<Vec<PendingPacket>> {
        let mut batches = Vec::new();
        let mut current_batch = Vec::new();
        let mut current_gas = 0u64;

        for packet in packets {
            if current_gas + packet.estimated_gas > max_gas && !current_batch.is_empty() {
                batches.push(current_batch);
                current_batch = Vec::new();
                current_gas = 0;
            }
            current_gas += packet.estimated_gas;
            current_batch.push(packet);
        }

        if !current_batch.is_empty() {
            batches.push(current_batch);
        }

        batches
    }

    async fn refresh_proof(&self, _packet: &PendingPacket) -> Result<MerkleProof> {
        bail!("proof refresh not implemented in this example")
    }

    async fn requeue_failed_packets(
        &self,
        pair: &(String, String),
        results: &[RelayResult],
    ) {
        // Requeue failed packets with incremented retry count
        debug!("requeuing failed packets for {:?}", pair);
    }

    fn clone_internals(&self) -> Self {
        Self {
            chains: self.chains.clone(),
            clients: self.clients.clone(),
            pending_queues: self.pending_queues.clone(),
            circuit_breakers: self.circuit_breakers.clone(),
            metrics: self.metrics.clone(),
            tx_semaphore: self.tx_semaphore.clone(),
            shutdown_tx: self.shutdown_tx.clone(),
            shutdown_rx: self.shutdown_rx.clone(),
        }
    }

    async fn relay_single_with_client(
        _client: &dyn ChainClient,
        _packet: PendingPacket,
    ) -> RelayResult {
        // Simplified single relay
        RelayResult {
            packet_id: _packet.packet_id,
            success: true,
            tx_hash: None,
            error: None,
            gas_used: 0,
        }
    }
}

// ============================================================================
// Supporting Traits and Types
// ============================================================================

#[derive(Debug)]
pub struct RelayResult {
    pub packet_id: PacketId,
    pub success: bool,
    pub tx_hash: Option<String>,
    pub error: Option<String>,
    pub gas_used: u64,
}

pub struct HealthStatus {
    pub block_height: u64,
    pub block_lag: u64,
    pub peer_count: u32,
    pub syncing: bool,
}

pub struct RawPacket {
    pub packet_id: PacketId,
    pub sequence: u64,
    pub data: Vec<u8>,
    pub timeout_height: u64,
    pub timeout_timestamp: u64,
    pub proof_height: u64,
}

impl RawPacket {
    fn is_emergency(&self) -> bool { false }
    fn time_to_timeout(&self) -> Duration { Duration::from_secs(3600) }
    fn estimated_value_usd(&self) -> f64 { 0.0 }
}

/// Chain client abstraction — 모든 체인에 대한 통합 인터페이스
/// Bridge: "추상화의 핵심은 각 체인의 고유한 특성을 존중하면서도
///          일관된 인터페이스를 제공하는 것입니다."
#[async_trait::async_trait]
pub trait ChainClient: Send + Sync {
    async fn health_check(&self) -> Result<HealthStatus>;
    async fn query_unreceived_packets(&self, dest: &str) -> Result<Vec<RawPacket>>;
    async fn generate_packet_proof(&self, packet: &RawPacket) -> Result<MerkleProof>;
    async fn submit_relay(
        &self,
        data: &[u8],
        proof: &MerkleProof,
        proof_height: u64,
    ) -> Result<String>;
    async fn submit_batch_relay(&self, packets: Vec<&PendingPacket>) -> Result<String>;
    fn supports_batch_relay(&self) -> bool;
    fn clone_box(&self) -> Box<dyn ChainClient>;
}

/// Relayer metrics
pub struct RelayerMetrics {
    // In practice, these would be prometheus metrics
    total_relayed: std::sync::atomic::AtomicU64,
    total_failed: std::sync::atomic::AtomicU64,
}

impl RelayerMetrics {
    fn new() -> Self {
        Self {
            total_relayed: std::sync::atomic::AtomicU64::new(0),
            total_failed: std::sync::atomic::AtomicU64::new(0),
        }
    }

    async fn report(&self) {
        let relayed = self.total_relayed.load(std::sync::atomic::Ordering::Relaxed);
        let failed = self.total_failed.load(std::sync::atomic::Ordering::Relaxed);
        info!("📊 Relayer Stats: {} relayed, {} failed", relayed, failed);
    }

    async fn record_relay_batch(
        &self,
        _source: &str,
        _dest: &str,
        success: usize,
        failed: usize,
    ) {
        self.total_relayed.fetch_add(
            success as u64,
            std::sync::atomic::Ordering::Relaxed,
        );
        self.total_failed.fetch_add(
            failed as u64,
            std::sync::atomic::Ordering::Relaxed,
        );
    }
}
```

### 3.4 라이트 클라이언트 검증 — Rust

```rust
// ============================================================================
// Light Client Verification Engine
// ============================================================================
// Bridge: "라이트 클라이언트는 크로스체인 보안의 근간입니다.
//          외부 신뢰 없이 다른 체인의 상태를 검증할 수 있는
//          유일한 방법이죠."
// ============================================================================

use std::collections::BTreeMap;
use std::time::Duration;

use sha2::{Sha256, Digest};

/// Tendermint Light Client — IBC의 핵심 보안 컴포넌트
///
/// Bridge가 Cosmos/Tendermint에서 직접 설계에 참여한 부분
pub struct TendermintLightClient {
    /// 신뢰할 수 있는 가장 최근 헤더
    trusted_header: LightBlock,

    /// 신뢰 기간 — 이 기간 내에 업데이트해야 함
    /// Bridge: "trusting period는 체인의 심장박동입니다.
    ///          멈추면 신뢰가 죽습니다."
    trusting_period: Duration,

    /// 검증기 집합의 변경 허용 비율
    /// 1/3 이상 변경 시 bisection 필요
    trust_threshold: TrustThreshold,

    /// 시계 드리프트 허용 범위
    max_clock_drift: Duration,

    /// 검증된 헤더 캐시
    verified_headers: BTreeMap<u64, LightBlock>,
}

#[derive(Debug, Clone)]
pub struct LightBlock {
    pub height: u64,
    pub time: u64,  // Unix timestamp
    pub validators_hash: [u8; 32],
    pub next_validators_hash: [u8; 32],
    pub app_hash: [u8; 32],
    pub last_commit: Commit,
    pub validator_set: ValidatorSet,
}

#[derive(Debug, Clone)]
pub struct ValidatorSet {
    pub validators: Vec<Validator>,
    pub total_voting_power: u64,
}

#[derive(Debug, Clone)]
pub struct Validator {
    pub address: [u8; 20],
    pub pub_key: Vec<u8>,
    pub voting_power: u64,
}

#[derive(Debug, Clone)]
pub struct Commit {
    pub height: u64,
    pub round: u32,
    pub block_id: BlockId,
    pub signatures: Vec<CommitSig>,
}

#[derive(Debug, Clone)]
pub struct BlockId {
    pub hash: [u8; 32],
    pub parts: PartSetHeader,
}

#[derive(Debug, Clone)]
pub struct PartSetHeader {
    pub total: u32,
    pub hash: [u8; 32],
}

#[derive(Debug, Clone)]
pub struct CommitSig {
    pub validator_address: [u8; 20],
    pub timestamp: u64,
    pub signature: Vec<u8>,
}

#[derive(Debug, Clone, Copy)]
pub struct TrustThreshold {
    pub numerator: u64,
    pub denominator: u64,
}

impl TrustThreshold {
    pub fn new(numerator: u64, denominator: u64) -> Self {
        assert!(numerator <= denominator, "invalid trust threshold");
        assert!(denominator > 0, "denominator must be positive");
        // Bridge: "기본 1/3은 BFT의 수학적 근거입니다.
        //          이것을 바꾸려면 매우 좋은 이유가 있어야 합니다."
        Self { numerator, denominator }
    }

    pub fn check(&self, signed_power: u64, total_power: u64) -> bool {
        // signed_power / total_power >= numerator / denominator
        // 정수 연산으로 변환: signed_power * denominator >= numerator * total_power
        signed_power * self.denominator >= self.numerator * total_power
    }
}

impl TendermintLightClient {
    pub fn new(
        trusted_header: LightBlock,
        trusting_period: Duration,
        trust_threshold: TrustThreshold,
        max_clock_drift: Duration,
    ) -> Self {
        let mut verified_headers = BTreeMap::new();
        verified_headers.insert(trusted_header.height, trusted_header.clone());

        Self {
            trusted_header,
            trusting_period,
            trust_threshold,
            max_clock_drift,
            verified_headers,
        }
    }

    /// Verify and update to a new header
    ///
    /// Bridge의 핵심 알고리즘:
    /// 1. 인접 블록: 검증기 집합이 정확히 일치하는지 확인
    /// 2. 비인접 블록: 서명된 투표 파워가 trust threshold 이상인지 확인
    /// 3. 필요 시 bisection으로 중간 헤더를 통해 검증
    pub fn verify_header(
        &mut self,
        untrusted: &LightBlock,
        now: u64,
    ) -> Result<(), LightClientError> {
        // ========================================
        // Step 1: 기본 유효성 검증
        // ========================================

        // 1-1. 높이가 신뢰 헤더보다 높은지
        if untrusted.height <= self.trusted_header.height {
            return Err(LightClientError::HeightTooLow {
                given: untrusted.height,
                trusted: self.trusted_header.height,
            });
        }

        // 1-2. Trusting period 확인
        let trusted_expiry = self.trusted_header.time
            + self.trusting_period.as_secs();
        if now >= trusted_expiry {
            return Err(LightClientError::TrustingPeriodExpired {
                trusted_time: self.trusted_header.time,
                trusting_period: self.trusting_period,
                now,
            });
        }

        // 1-3. 미래 블록이 아닌지 확인
        let max_time = now + self.max_clock_drift.as_secs();
        if untrusted.time > max_time {
            return Err(LightClientError::HeaderFromFuture {
                header_time: untrusted.time,
                max_allowed: max_time,
            });
        }

        // ========================================
        // Step 2: 검증기 집합 검증
        // ========================================

        if untrusted.height == self.trusted_header.height + 1 {
            // 인접 블록: next_validators_hash가 일치해야 함
            self.verify_adjacent(untrusted)?;
        } else {
            // 비인접 블록: trust threshold 기반 검증
            self.verify_non_adjacent(untrusted)?;
        }

        // ========================================
        // Step 3: 커밋 서명 검증
        // ========================================
        self.verify_commit(untrusted)?;

        // ========================================
        // Step 4: 신뢰 헤더 업데이트
        // ========================================
        self.trusted_header = untrusted.clone();
        self.verified_headers.insert(untrusted.height, untrusted.clone());

        Ok(())
    }

    /// Adjacent block verification
    fn verify_adjacent(&self, untrusted: &LightBlock) -> Result<(), LightClientError> {
        // Bridge: "인접 블록 검증은 간단합니다.
        //          신뢰 블록의 next_validators_hash가
        //          새 블록의 validators_hash와 같으면 됩니다."

        let expected_hash = self.trusted_header.next_validators_hash;
        let actual_hash = hash_validator_set(&untrusted.validator_set);

        if expected_hash != actual_hash {
            return Err(LightClientError::ValidatorSetMismatch {
                expected: expected_hash,
                actual: actual_hash,
            });
        }

        Ok(())
    }

    /// Non-adjacent block verification using trust threshold
    fn verify_non_adjacent(&self, untrusted: &LightBlock) -> Result<(), LightClientError> {
        // Bridge: "비인접 블록은 더 복잡합니다.
        //          신뢰 블록의 검증기 집합 중에서
        //          새 블록에 서명한 파워가 1/3 이상이어야 합니다.
        //          이것이 BFT의 핵심입니다."

        let trusted_validators = &self.trusted_header.validator_set;
        let untrusted_commit = &untrusted.last_commit;

        let mut signed_power: u64 = 0;

        for sig in &untrusted_commit.signatures {
            // 신뢰 검증기 집합에서 이 서명자를 찾음
            if let Some(validator) = trusted_validators.validators.iter()
                .find(|v| v.address == sig.validator_address)
            {
                // 서명 검증 (실제로는 Ed25519/Secp256k1 검증)
                if self.verify_signature(validator, sig, &untrusted_commit.block_id) {
                    signed_power += validator.voting_power;
                }
            }
        }

        // Trust threshold 확인
        if !self.trust_threshold.check(signed_power, trusted_validators.total_voting_power) {
            return Err(LightClientError::InsufficientSignedPower {
                signed: signed_power,
                total: trusted_validators.total_voting_power,
                threshold: self.trust_threshold,
            });
        }

        Ok(())
    }

    /// Verify that 2/3+ of the validator set signed the commit
    fn verify_commit(&self, block: &LightBlock) -> Result<(), LightClientError> {
        let commit = &block.last_commit;
        let validator_set = &block.validator_set;

        let mut signed_power: u64 = 0;

        for sig in &commit.signatures {
            if let Some(validator) = validator_set.validators.iter()
                .find(|v| v.address == sig.validator_address)
            {
                if self.verify_signature(validator, sig, &commit.block_id) {
                    signed_power += validator.voting_power;
                }
            }
        }

        // 2/3 이상이 서명해야 함
        let two_thirds = TrustThreshold::new(2, 3);
        if !two_thirds.check(signed_power, validator_set.total_voting_power) {
            return Err(LightClientError::InsufficientCommitPower {
                signed: signed_power,
                total: validator_set.total_voting_power,
            });
        }

        Ok(())
    }

    fn verify_signature(
        &self,
        _validator: &Validator,
        _sig: &CommitSig,
        _block_id: &BlockId,
    ) -> bool {
        // In production: Ed25519 or Secp256k1 signature verification
        true
    }

    /// Verify a merkle proof against a verified header
    /// Bridge: "머클 증명은 '이 데이터가 이 블록에 존재했다'는
    ///          수학적 보증입니다. 블록체인 없이도 검증 가능합니다."
    pub fn verify_merkle_proof(
        &self,
        proof: &MerkleProof,
        root: &[u8; 32],
    ) -> Result<bool, LightClientError> {
        if proof.proof_ops.is_empty() {
            return Err(LightClientError::EmptyProof);
        }

        // Verify the proof chain
        let mut current_hash = hash_leaf(&proof.key, &proof.value);

        for op in &proof.proof_ops {
            current_hash = hash_inner(&current_hash, &op.data);
        }

        Ok(current_hash == *root)
    }
}

/// Light client errors
#[derive(Debug)]
pub enum LightClientError {
    HeightTooLow { given: u64, trusted: u64 },
    TrustingPeriodExpired { trusted_time: u64, trusting_period: Duration, now: u64 },
    HeaderFromFuture { header_time: u64, max_allowed: u64 },
    ValidatorSetMismatch { expected: [u8; 32], actual: [u8; 32] },
    InsufficientSignedPower { signed: u64, total: u64, threshold: TrustThreshold },
    InsufficientCommitPower { signed: u64, total: u64 },
    EmptyProof,
    InvalidProof,
}

// Helper functions
fn hash_validator_set(vs: &ValidatorSet) -> [u8; 32] {
    let mut hasher = Sha256::new();
    for v in &vs.validators {
        hasher.update(&v.address);
        hasher.update(&v.voting_power.to_be_bytes());
    }
    hasher.finalize().into()
}

fn hash_leaf(key: &[u8], value: &[u8]) -> [u8; 32] {
    let mut hasher = Sha256::new();
    hasher.update(&[0x00]); // leaf prefix
    hasher.update(key);
    hasher.update(value);
    hasher.finalize().into()
}

fn hash_inner(left: &[u8; 32], right: &[u8]) -> [u8; 32] {
    let mut hasher = Sha256::new();
    hasher.update(&[0x01]); // inner prefix
    hasher.update(left);
    hasher.update(right);
    hasher.finalize().into()
}
```

### 3.5 EVM 브릿지 컨트랙트 — Solidity

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/security/PausableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/security/ReentrancyGuardUpgradeable.sol";

/**
 * @title BridgeEndpoint
 * @author Bridge (김하영) — F1-23
 * @notice EVM-side endpoint for cross-chain message reception and verification
 *
 * Bridge의 설계 원칙:
 * "EVM 브릿지 컨트랙트는 가장 큰 공격 표면입니다.
 *  모든 함수가 적대적 입력을 가정하고 설계되어야 합니다.
 *  Ronin $625M, Wormhole $320M, Nomad $190M...
 *  이 숫자들이 왜 보안이 1순위인지 말해줍니다."
 */
contract BridgeEndpoint is
    Initializable,
    AccessControlUpgradeable,
    PausableUpgradeable,
    ReentrancyGuardUpgradeable
{
    // ========================================
    // Roles
    // ========================================
    bytes32 public constant RELAYER_ROLE = keccak256("RELAYER_ROLE");
    bytes32 public constant GUARDIAN_ROLE = keccak256("GUARDIAN_ROLE");
    bytes32 public constant GOVERNOR_ROLE = keccak256("GOVERNOR_ROLE");

    // ========================================
    // State Variables
    // ========================================

    /// @notice Light client contract for source chain verification
    ILightClient public lightClient;

    /// @notice Rate limiter for transfer volume control
    IRateLimiter public rateLimiter;

    /// @notice Processed message IDs (replay protection)
    mapping(bytes32 => bool) public processedMessages;

    /// @notice Nonce per source chain (ordering)
    mapping(uint256 => uint64) public chainNonces;

    /// @notice Trusted source chain configurations
    mapping(uint256 => SourceChainConfig) public sourceChains;

    /// @notice Emergency pause per chain
    mapping(uint256 => bool) public chainPaused;

    /// @notice Total value locked per token
    mapping(address => uint256) public totalValueLocked;

    /// @notice Daily transfer volume per token (reset every 24h)
    mapping(address => DailyVolume) public dailyVolumes;

    struct SourceChainConfig {
        bool enabled;
        address lightClientAddress;
        uint64 requiredConfirmations;
        uint256 maxTransferPerTx;
        uint256 maxDailyVolume;
    }

    struct DailyVolume {
        uint256 amount;
        uint256 lastResetTimestamp;
    }

    struct CrossChainMessage {
        uint256 sourceChainId;
        uint256 destChainId;
        bytes32 messageId;
        address sender;
        address recipient;
        uint256 amount;
        address token;
        bytes payload;
        uint64 nonce;
        uint256 timestamp;
    }

    struct MerkleProof {
        bytes32[] proof;
        uint256 index;
        bytes32 leaf;
        bytes32 root;
    }

    // ========================================
    // Events
    // ========================================
    event MessageReceived(
        bytes32 indexed messageId,
        uint256 indexed sourceChainId,
        address indexed recipient,
        address token,
        uint256 amount
    );

    event MessageSent(
        bytes32 indexed messageId,
        uint256 indexed destChainId,
        address indexed sender,
        address token,
        uint256 amount,
        uint64 nonce
    );

    event EmergencyPause(uint256 indexed chainId, address indexed guardian);
    event ChainConfigUpdated(uint256 indexed chainId);

    // ========================================
    // Errors
    // ========================================
    error MessageAlreadyProcessed(bytes32 messageId);
    error InvalidSourceChain(uint256 chainId);
    error ChainPaused(uint256 chainId);
    error InvalidNonce(uint64 expected, uint64 received);
    error ProofVerificationFailed();
    error TransferLimitExceeded(uint256 amount, uint256 limit);
    error DailyVolumeLimitExceeded(uint256 current, uint256 limit);
    error InsufficientConfirmations(uint256 current, uint256 required);

    // ========================================
    // Initialization
    // ========================================

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize(
        address _lightClient,
        address _rateLimiter,
        address _admin
    ) external initializer {
        __AccessControl_init();
        __Pausable_init();
        __ReentrancyGuard_init();

        lightClient = ILightClient(_lightClient);
        rateLimiter = IRateLimiter(_rateLimiter);

        _grantRole(DEFAULT_ADMIN_ROLE, _admin);
        _grantRole(GUARDIAN_ROLE, _admin);
        _grantRole(GOVERNOR_ROLE, _admin);
    }

    // ========================================
    // Core Functions
    // ========================================

    /**
     * @notice Receive and execute a cross-chain message
     * @dev This is the most security-critical function in the entire contract
     *
     * Bridge: "이 함수에 들어오는 모든 것은 악의적이라고 가정합니다.
     *          증명이 유효하고, 라이트 클라이언트가 확인하고,
     *          Rate limit이 통과해야만 실행됩니다."
     */
    function receiveMessage(
        CrossChainMessage calldata message,
        MerkleProof calldata proof,
        uint256 proofHeight
    ) external nonReentrant whenNotPaused onlyRole(RELAYER_ROLE) {
        // 1. 소스 체인 유효성 확인
        SourceChainConfig storage config = sourceChains[message.sourceChainId];
        if (!config.enabled) {
            revert InvalidSourceChain(message.sourceChainId);
        }
        if (chainPaused[message.sourceChainId]) {
            revert ChainPaused(message.sourceChainId);
        }

        // 2. 중복 메시지 확인 (replay protection)
        if (processedMessages[message.messageId]) {
            revert MessageAlreadyProcessed(message.messageId);
        }

        // 3. 논스 순서 확인
        uint64 expectedNonce = chainNonces[message.sourceChainId] + 1;
        if (message.nonce != expectedNonce) {
            revert InvalidNonce(expectedNonce, message.nonce);
        }

        // 4. 라이트 클라이언트를 통한 증명 검증
        // Bridge: "이것이 trust-minimized bridge의 핵심입니다.
        //          외부 오라클이나 멀티시그 없이,
        //          수학적 증명만으로 검증합니다."
        if (!_verifyProof(message, proof, proofHeight, config)) {
            revert ProofVerificationFailed();
        }

        // 5. 전송 한도 확인
        if (message.amount > config.maxTransferPerTx) {
            revert TransferLimitExceeded(message.amount, config.maxTransferPerTx);
        }

        // 6. 일일 한도 확인
        _checkAndUpdateDailyVolume(message.token, message.amount, config.maxDailyVolume);

        // 7. 메시지 처리 표시 (상태 변경은 외부 호출 전에!)
        processedMessages[message.messageId] = true;
        chainNonces[message.sourceChainId] = message.nonce;

        // 8. 메시지 실행
        _executeMessage(message);

        emit MessageReceived(
            message.messageId,
            message.sourceChainId,
            message.recipient,
            message.token,
            message.amount
        );
    }

    /**
     * @notice Emergency pause for a specific chain
     * @dev Guardians can pause individual chains without affecting others
     *
     * Bridge: "전체 정지보다 부분 정지가 낫습니다.
     *          한 체인의 문제가 다른 체인에 영향을 주면 안 됩니다."
     */
    function emergencyPauseChain(uint256 chainId)
        external
        onlyRole(GUARDIAN_ROLE)
    {
        chainPaused[chainId] = true;
        emit EmergencyPause(chainId, msg.sender);
    }

    // ========================================
    // Internal Functions
    // ========================================

    function _verifyProof(
        CrossChainMessage calldata message,
        MerkleProof calldata proof,
        uint256 proofHeight,
        SourceChainConfig storage config
    ) internal view returns (bool) {
        // 확인 수 검증
        uint256 currentHeight = lightClient.getLatestHeight(message.sourceChainId);
        if (currentHeight < proofHeight + config.requiredConfirmations) {
            revert InsufficientConfirmations(
                currentHeight - proofHeight,
                config.requiredConfirmations
            );
        }

        // 머클 증명 검증
        bytes32 messageHash = keccak256(abi.encode(
            message.sourceChainId,
            message.destChainId,
            message.messageId,
            message.sender,
            message.recipient,
            message.amount,
            message.token,
            message.payload,
            message.nonce,
            message.timestamp
        ));

        bytes32 stateRoot = lightClient.getStateRoot(
            message.sourceChainId,
            proofHeight
        );

        return _verifyMerkleProof(proof, messageHash, stateRoot);
    }

    function _verifyMerkleProof(
        MerkleProof calldata proof,
        bytes32 leaf,
        bytes32 root
    ) internal pure returns (bool) {
        bytes32 computedHash = leaf;

        for (uint256 i = 0; i < proof.proof.length; i++) {
            bytes32 proofElement = proof.proof[i];

            if (proof.index & (1 << i) == 0) {
                computedHash = keccak256(abi.encodePacked(computedHash, proofElement));
            } else {
                computedHash = keccak256(abi.encodePacked(proofElement, computedHash));
            }
        }

        return computedHash == root;
    }

    function _executeMessage(CrossChainMessage calldata message) internal {
        if (message.token == address(0)) {
            // Native token transfer
            (bool success, ) = payable(message.recipient).call{value: message.amount}("");
            require(success, "native transfer failed");
        } else {
            // ERC20 token transfer (unlock from escrow)
            IERC20(message.token).transfer(message.recipient, message.amount);
        }
    }

    function _checkAndUpdateDailyVolume(
        address token,
        uint256 amount,
        uint256 maxDaily
    ) internal {
        DailyVolume storage vol = dailyVolumes[token];

        // 24시간이 지났으면 리셋
        if (block.timestamp > vol.lastResetTimestamp + 1 days) {
            vol.amount = 0;
            vol.lastResetTimestamp = block.timestamp;
        }

        if (vol.amount + amount > maxDaily) {
            revert DailyVolumeLimitExceeded(vol.amount + amount, maxDaily);
        }

        vol.amount += amount;
    }
}

// ========================================
// Interfaces
// ========================================

interface ILightClient {
    function getLatestHeight(uint256 chainId) external view returns (uint256);
    function getStateRoot(uint256 chainId, uint256 height) external view returns (bytes32);
    function verifyHeader(uint256 chainId, bytes calldata header) external returns (bool);
}

interface IRateLimiter {
    function checkLimit(address token, uint256 amount) external view returns (bool);
}

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
}
```

---

## 4. 도구 체인

```yaml
# ============================================================================
# Bridge's Cross-Chain Development Toolkit
# ============================================================================
# "올바른 도구 없이 크로스체인 개발을 하는 건
#  나침반 없이 대양을 건너는 것과 같습니다."
# — 김하영
# ============================================================================

# ============================================
# Cross-Chain Frameworks & SDKs
# ============================================
cross_chain_frameworks:
  cosmos_sdk:
    version: "v0.50.x"
    role: "IBC 기반 크로스체인의 표준 프레임워크"
    usage: "커스텀 IBC 모듈 개발, 앱체인 구축"
    bridge_note: >
      "Cosmos SDK는 크로스체인의 Linux입니다.
       모듈식 아키텍처가 IBC의 유연성을 가능하게 했죠."
    modules:
      - ibc-go: "IBC 프로토콜 Go 구현 (핵심 기여)"
      - ibc-rs: "IBC 프로토콜 Rust 구현"
      - interchain-accounts: "크로스체인 계정 관리"
      - interchain-queries: "크로스체인 쿼리"
      - fee-middleware: "릴레이어 수수료 인센티브"
    custom_modules:
      - cross-chain-swap: "원자적 크로스체인 토큰 교환"
      - bridge-oracle: "크로스체인 가격 오라클"
      - composable-msg: "다중 체인 메시지 조합"

  ibc_protocol:
    version: "ICS-004 (Channel), ICS-020 (Transfer)"
    role: "체인 간 통신의 TCP/IP"
    usage: "패킷 라우팅, 채널 관리, 라이트 클라이언트 검증"
    bridge_note: >
      "IBC는 제가 가장 자부심을 느끼는 프로토콜입니다.
       외부 신뢰 없이 수학적으로 안전한 크로스체인 통신.
       이것이 진정한 인터체인의 시작입니다."
    components:
      - light_clients: "Tendermint, Ethereum, Solana LC"
      - connection: "체인 쌍 간 인증된 연결"
      - channel: "포트 쌍 간 메시지 채널"
      - packet: "원자적 메시지 단위"
      - relayer: "오프체인 패킷 전달자"

  layerzero:
    version: "v2"
    role: "EVM 중심 범용 크로스체인 메시징"
    usage: "EVM 체인 간 메시지 전달, OApp 개발"
    bridge_note: >
      "LayerZero의 Ultra Light Node 설계는 우아합니다.
       오라클과 릴레이어를 분리해서 공모 위험을 줄였죠.
       하지만 완전한 trust-minimization은 아닙니다."
    components:
      - endpoint: "체인별 메시지 송수신 컨트랙트"
      - dvn: "Decentralized Verifier Network"
      - executor: "메시지 실행기"
      - oapp: "Omnichain Application 프레임워크"

  wormhole:
    version: "v2"
    role: "가디언 네트워크 기반 범용 브릿지"
    usage: "다중 체인 자산 이동, 메시지 전달"
    bridge_note: >
      "Wormhole은 실용성과 보안의 균형을 잘 맞춘 프로토콜입니다.
       19개 가디언이 2/3 합의로 메시지를 검증하는 구조.
       $320M 해킹 이후의 보안 개선이 인상적이었습니다."
    components:
      - guardian_network: "분산 검증 네트워크"
      - vaa: "Verified Action Approval"
      - token_bridge: "자산 브릿지"
      - ntt: "Native Token Transfer"

  polkadot_xcm:
    version: "v3"
    role: "Polkadot 생태계 크로스체인 메시징"
    usage: "파라체인 간 자산 이동, 원격 실행"
    bridge_note: >
      "XCM은 가장 표현력이 풍부한 크로스체인 메시지 포맷입니다.
       XCVM(Cross-Consensus Virtual Machine)이라는 개념은
       크로스체인의 미래를 보여줍니다."
    components:
      - xcm_format: "범용 크로스체인 메시지 포맷"
      - hrmp: "수평 릴레이 체인 메시지 전달"
      - dmp: "하향 메시지 전달 (릴레이→파라)"
      - ump: "상향 메시지 전달 (파라→릴레이)"
      - bridge_hub: "외부 체인 브릿지 허브"

  axelar:
    version: "latest"
    role: "범용 크로스체인 라우팅 네트워크"
    usage: "General Message Passing, 크로스체인 DeFi"
    bridge_note: >
      "Axelar는 크로스체인의 라우터입니다.
       Cosmos SDK 기반이면서 EVM, non-EVM을 모두 연결하는
       하이브리드 접근이 실용적입니다."
    components:
      - gmp: "General Message Passing"
      - its: "Interchain Token Service"
      - amplifier: "Permissionless 검증자 네트워크"

# ============================================
# Core Development Languages & Tools
# ============================================
languages:
  rust:
    version: "1.75+"
    role: "고성능 릴레이어, 라이트 클라이언트, 크로스체인 코어"
    bridge_note: "성능과 안전성이 동시에 필요한 크로스체인 코어에 최적"
    key_crates:
      - tendermint-rs: "Tendermint 라이트 클라이언트"
      - ibc-rs: "IBC 프로토콜 구현"
      - hermes: "IBC 릴레이어"
      - cosmwasm-std: "CosmWasm 스마트 컨트랙트"
      - ethers-rs: "Ethereum 클라이언트"
      - alloy: "차세대 Ethereum 라이브러리"
      - tokio: "비동기 런타임"
      - tower: "미들웨어 스택"
      - tracing: "구조화된 로깅"

  go:
    version: "1.22+"
    role: "Cosmos SDK 모듈, IBC 핸들러, 체인 데몬"
    bridge_note: "Cosmos 생태계의 메인 언어, SDK 모듈 개발 필수"
    key_packages:
      - cosmos-sdk: "블록체인 프레임워크"
      - ibc-go: "IBC 프로토콜 구현"
      - cometbft: "합의 엔진"
      - grpc-go: "gRPC 통신"
      - protobuf: "메시지 직렬화"

  solidity:
    version: "0.8.20+"
    role: "EVM 브릿지 컨트랙트, 검증 컨트랙트"
    bridge_note: "EVM 체인의 엔드포인트 — 가장 큰 공격 표면"
    frameworks:
      - foundry: "테스트 & 배포 (forge, cast, anvil)"
      - hardhat: "레거시 프로젝트 호환"
      - openzeppelin: "보안 감사된 기본 컨트랙트"

  typescript:
    version: "5.x"
    role: "SDK, CLI, 대시보드, 통합 테스트"
    bridge_note: "개발자 경험(DX)과 빠른 프로토타이핑"
    frameworks:
      - viem: "Type-safe Ethereum 클라이언트"
      - cosmjs: "Cosmos 체인 클라이언트"
      - polkadot-js: "Polkadot 생태계 SDK"
      - next.js: "브릿지 대시보드 UI"

  move:
    version: "latest"
    role: "Aptos/Sui 브릿지 모듈"
    bridge_note: "리소스 지향 언어 — 토큰 안전성에 강점"

# ============================================
# Security & Verification Tools
# ============================================
security:
  formal_verification:
    tla_plus:
      role: "크로스체인 프로토콜 모델 검증"
      bridge_note: >
        "TLA+로 IBC 핸드셰이크의 모든 상태를 모델링했습니다.
         데드락과 라이브니스를 수학적으로 증명해야 합니다."
    coq:
      role: "라이트 클라이언트 정확성 증명"
      bridge_note: "라이트 클라이언트 검증 로직의 형식적 증명"

  audit_tools:
    slither:
      role: "Solidity 정적 분석"
      usage: "브릿지 컨트랙트 자동 취약점 탐지"
    mythril:
      role: "심볼릭 실행 기반 취약점 탐지"
    echidna:
      role: "속성 기반 퍼징"
      bridge_note: "브릿지 불변식 테스트에 필수"
    certora:
      role: "형식적 검증 도구"
      bridge_note: "수학적으로 불변식 위반 불가능성 증명"

  monitoring:
    forta:
      role: "실시간 온체인 위협 탐지"
    chainalysis:
      role: "자금 흐름 모니터링"
    custom_alerting:
      role: "Bridge의 커스텀 모니터링 시스템"
      components:
        - volume_anomaly_detector: "비정상 전송량 탐지"
        - proof_verification_monitor: "증명 실패 패턴 분석"
        - relayer_health_dashboard: "릴레이어 상태 대시보드"
        - chain_finality_tracker: "체인별 파이널리티 추적"

# ============================================
# Testing & Simulation
# ============================================
testing:
  local_chains:
    gaiad: "Cosmos Hub 로컬 테스트넷"
    osmosisd: "Osmosis 로컬 테스트넷"
    anvil: "Ethereum 로컬 포크"
    zombienet: "Polkadot 로컬 테스트넷"
    solana_test_validator: "Solana 로컬 검증기"

  integration_testing:
    interchaintest:
      role: "멀티체인 통합 테스트 프레임워크"
      bridge_note: >
        "실제 체인 바이너리를 Docker에서 실행하고
         IBC 패킷이 정확히 전달되는지 E2E 테스트합니다.
         이것 없이 크로스체인 개발은 불가능합니다."
    forge_test:
      role: "Solidity 유닛 & 퍼징 테스트"
    cargo_test:
      role: "Rust 유닛 & 통합 테스트"

  chaos_engineering:
    custom_chaos:
      role: "크로스체인 장애 시뮬레이션"
      scenarios:
        - relayer_crash: "릴레이어 강제 종료"
        - chain_halt: "체인 정지"
        - reorg_simulation: "블록 리오그 시뮬레이션"
        - network_partition: "네트워크 파티션"
        - gas_spike: "가스 가격 급등"
        - timeout_cascade: "타임아웃 연쇄"

# ============================================
# Infrastructure & DevOps
# ============================================
infrastructure:
  relayer_ops:
    hermes:
      role: "IBC 릴레이어 (Rust)"
      bridge_note: "가장 안정적인 IBC 릴레이어"
    custom_relayer:
      role: "Bridge의 고성능 멀티프로토콜 릴레이어"
      features:
        - multi_protocol: "IBC, LayerZero, Wormhole 동시 지원"
        - priority_queue: "우선순위 기반 패킷 스케줄링"
        - gas_optimization: "배치 릴레이, 가스 추정"
        - auto_recovery: "자동 장애 복구"

  node_operations:
    tendermint: "Cosmos 체인 노드"
    geth: "Ethereum 실행 클라이언트"
    lighthouse: "Ethereum 합의 클라이언트"
    polkadot: "Polkadot 릴레이 체인 노드"

  monitoring_stack:
    prometheus: "메트릭 수집"
    grafana: "대시보드 시각화"
    loki: "로그 집계"
    pagerduty: "온콜 알림"
    custom_dashboards:
      - cross_chain_flow: "체인 간 자산 흐름 시각화"
      - relayer_performance: "릴레이어 성능 메트릭"
      - proof_latency: "증명 생성/검증 지연 시간"
      - channel_health: "IBC 채널 상태 모니터링"

# ============================================
# Editor & Development Environment
# ============================================
editor:
  primary: "Neovim"
  config: "LazyVim + custom cross-chain plugins"
  lsp:
    - rust-analyzer: "Rust LSP"
    - gopls: "Go LSP"
    - solidity-ls: "Solidity LSP"
    - typescript-language-server: "TypeScript LSP"
  custom_plugins:
    - chain-switcher: "체인별 환경 빠른 전환"
    - ibc-packet-inspector: "IBC 패킷 구조 시각화"
    - proof-debugger: "머클 증명 디버깅"

  terminal: "WezTerm (tmux 대신)"
  shell: "fish"
  multiplexer: "zellij"

# ============================================
# Communication & Documentation
# ============================================
communication:
  documentation:
    - mdbook: "프로토콜 스펙 문서화"
    - typst: "학술 논문 작성"
    - mermaid: "크로스체인 플로우 다이어그램"
    - excalidraw: "아키텍처 화이트보드"

  collaboration:
    - github: "코드 리뷰, 이슈 트래킹"
    - slack: "팀 커뮤니케이션"
    - notion: "프로토콜 설계 문서"
    - figma: "브릿지 UI/UX 디자인 협업"
```

---

## 5. 커리어 상세

### 🎓 에피소드 1: 서울대학교 컴퓨터공학부 (2010–2014)

**"분산 시스템의 씨앗"**

서초구의 조용한 아파트에서 자란 하영은 어린 시절부터 **"연결"** 에 매료되었습니다. 초등학교 때 아버지의 오래된 PC로 인터넷에 처음 접속한 순간, 서울의 작은 방에서 전 세계와 소통할 수 있다는 사실에 경이로움을 느꼈습니다.

서울대 컴퓨터공학부에 입학한 하영은 1학년부터 눈에 띄는 학생이었습니다. 하지만 화려한 타입은 아니었습니다. 항상 도서관 구석 자리에 앉아, 두꺼운 교과서를 정독하는 스타일. 교수들은 "질문은 많지 않지만, 한 번 하면 핵심을 찌른다"고 평가했습니다.

**전환점은 3학년 '분산 시스템' 수업이었습니다.**

```
교수: "CAP 정리에 대해 설명해볼 사람?"

(조용한 강의실. 아무도 손을 들지 않는다)

하영: (조심스럽게 손을 든다) "교수님, CAP 정리의 본질은
      '불가능성'이 아니라 '트레이드오프'라고 생각합니다.
      현실의 네트워크는 파티션이 일어나기 마련이니까,
      실질적인 선택은 C와 A 사이의 스펙트럼에서
      어디에 위치할 것인가의 문제입니다.
      그리고... 이 트레이드오프는 시스템의 경계에서
      가장 첨예해집니다. 두 시스템이 만나는 곳이요."

교수: (잠시 멈추며) "...경계라. 흥미로운 관점이네.
      그 '경계'에서의 일관성 문제를 학부 논문으로
      다뤄보는 건 어떨까?"
```

이 대화가 하영의 커리어를 결정지었습니다. 학부 졸업 논문 **"Cross-System Consistency in Heterogeneous Distributed Environments"** 는 서울대 컴퓨터공학부 최우수 논문상을 수상했습니다.

4학년 때는 블록체인에 처음 접했습니다. 비트코인 백서를 읽은 하영은 직감적으로 이해했습니다: **"이것은 분산 시스템의 극한 형태다. 그리고 이 체인들이 서로 대화해야 할 날이 반드시 온다."**

```
[하영의 학부 시절 노트에서]

"인터넷은 프로토콜의 승리였다. TCP/IP가 이질적인 네트워크를
 하나로 연결했다. 블록체인에도 같은 것이 필요하다.
 체인 간의 TCP/IP. 나는 그것을 만들고 싶다."
```

### 🎓 에피소드 2: Stanford University PhD — Distributed Consensus (2014–2019)

**"합의의 수학, 연결의 철학"**

Stanford CS PhD 프로그램에 합격한 하영은 David Mazières 교수 연구실에서 **분산 합의 프로토콜** 을 연구했습니다. (Mazières 교수는 Stellar Consensus Protocol의 설계자)

처음 2년은 기존 BFT 합의 알고리즘의 한계를 분석하는 데 집중했습니다.

```
[2015년, 연구 노트]

"PBFT는 O(n²) 통신 복잡도. 100개 노드만 넘어도 비현실적.
 Tendermint의 접근은 더 실용적이지만, 아직 체인 간은 고려하지 않았다.

 문제: 각 체인이 자체 합의 메커니즘을 가질 때,
       체인 A의 합의 결과를 체인 B가 어떻게 신뢰하는가?
       
 직감: 라이트 클라이언트. 전체 블록체인을 저장하지 않고도
       특정 상태를 검증할 수 있는 최소한의 정보.
       이것이 크로스체인의 열쇠다."
```

**PhD 논문: "Trust-Minimized Cross-System Consensus: Light Client Verification for Heterogeneous Blockchain Networks"**

이 논문은 세 가지 핵심 기여를 했습니다:

1. **범용 라이트 클라이언트 프레임워크**: 서로 다른 합의 메커니즘을 가진 체인들이 상호 검증할 수 있는 수학적 프레임워크
2. **Cross-System Finality Proof**: 하나의 체인에서 다른 체인의 파이널리티를 검증하는 효율적인 증명 방식
3. **Optimal Relay Scheduling**: 릴레이어의 최적 패킷 전달 스케줄링 알고리즘

```
[논문 방어 중]

심사위원: "당신의 프레임워크가 실제로 구현 가능하다고 생각하는가?
          현실의 블록체인은 이론 모델보다 훨씬 복잡하다."

하영: "동의합니다. 하지만 TCP/IP도 처음에는 이론적 프레임워크였습니다.
      OSI 모델이 현실의 네트워크를 완벽히 반영하지는 않지만,
      인