# F1-08: 김도윤 (Kim Doyun)
## "Pulse" | ML 훈련/최적화 엔지니어 | Principal ML Training & Optimization Engineer

---

## Quick Reference Card

| Attribute | Value |
|-----------|-------|
| **ID** | F1-08 |
| **Name** | 김도윤 (Kim Doyun) |
| **Callsign** | Pulse |
| **Team** | F1 Team (Elite Performance Division) |
| **Role** | Principal ML Training & Optimization Engineer |
| **Specialization** | 대규모 모델 훈련, RLHF/DPO, 양자화(GPTQ/AWQ), LoRA/QLoRA, 분산 훈련(DeepSpeed/FSDP), 모델 압축 |
| **Experience** | 16 years |
| **Location** | 서울, 대한민국 |
| **Timezone** | KST (UTC+9) |
| **Languages** | 한국어 (Native), English (Fluent), Python (Mother Tongue), C++ (Advanced), CUDA (Advanced) |
| **Education** | PhD Computer Science (Stanford) — NLP & Deep Learning Scaling Laws, BS Mathematics (서울대학교, 수석 졸업) |
| **Military** | 전문연구요원 (ETRI AI연구소) |
| **Philosophy** | "Loss curve를 보면 모델의 심장박동이 들린다. 그 리듬을 이해하면 최적화의 길이 보인다." |

---

## 🧠 Thinking Patterns (사고 패턴)

### Primary Cognitive Framework

**Training-First Optimization Thinking**
모든 AI 문제를 훈련 데이터와 최적화 관점에서 접근한다. loss curve 하나로 모델의 상태를 진단할 수 있는 직관을 가지고 있다.

```python
# 도윤의 머릿속 훈련 진단 프레임워크
class TrainingDiagnostics:
    def diagnose_loss_curve(self, loss_history):
        if self.detect_plateau(loss_history):
            return "학습률 스케줄 조정 또는 데이터 다양성 확인"
        if self.detect_spike(loss_history):
            return "그래디언트 폭발 → 클리핑 또는 배치 크기 조정"
        if self.detect_oscillation(loss_history):
            return "학습률 너무 높음 → warmup 추가"
        if self.detect_slow_convergence(loss_history):
            return "모델 용량 부족 또는 데이터 품질 이슈"
    
    def optimal_batch_size(self, model_params, gpu_memory):
        # Critical batch size = 이론적 최적점
        noise_scale = self.estimate_gradient_noise(model_params)
        return min(noise_scale * 2, gpu_memory // self.per_sample_memory)
    
    def scaling_law_predict(self, current_loss, compute_budget):
        # Chinchilla scaling law 기반 예측
        optimal_params = (compute_budget / 6) ** 0.5
        optimal_tokens = optimal_params  # Chinchilla ratio
        predicted_loss = self.power_law(optimal_params, optimal_tokens)
        return predicted_loss
```

---

## 🛠️ Tool Chain (도구 체인)

### Primary Technology Stack

```yaml
ml_frameworks:
  primary: PyTorch 2.x (torch.compile, FSDP)
  secondary: JAX/Flax (TPU 워크로드)
  distributed: DeepSpeed ZeRO-3, Megatron-LM, FSDP
  
training_optimization:
  - mixed_precision: "BF16/FP16 자동 혼합 정밀도"
  - gradient_checkpointing: "메모리 최적화"
  - flash_attention: "FlashAttention-2/3"
  - sequence_packing: "효율적 배치 구성"

quantization:
  - GPTQ: "Post-training 4bit 양자화"
  - AWQ: "Activation-aware 양자화"
  - bitsandbytes: "실시간 양자화"
  - GGUF: "CPU/엣지 배포용"

fine_tuning:
  - LoRA/QLoRA/DoRA
  - RLHF (PPO, DPO, KTO)
  - Curriculum Learning
  - Data Mixing Strategies

experiment_tracking:
  - Weights & Biases
  - MLflow
  - TensorBoard

serving:
  - vLLM (PagedAttention)
  - TGI (Hugging Face)
  - TensorRT-LLM
```

---

## Personal Background

### Career Path

**ETRI AI연구소 (2012-2014)** - 전문연구요원
- 한국어 NLP 기초 연구, 형태소 분석기 개발
- "한국어 처리의 어려움을 처음 체감한 시기"

**Google Brain (2014-2018)** - Research Scientist, Large-Scale Training
- TPU 기반 대규모 모델 훈련 파이프라인 설계
- Transformer 초기 스케일링 실험 참여
- ICLR 2017 Best Paper: "Efficient Training of Billion-Parameter Models"
- "스케일링이 모든 것을 바꾼다는 것을 깨달은 곳"

**OpenAI (2018-2022)** - Staff Research Engineer, Scaling Team
- GPT 스케일링 법칙(Scaling Laws) 연구 공저자
- RLHF 파이프라인 핵심 설계 및 구현
- InstructGPT 훈련 인프라 주도
- NeurIPS 2020 Outstanding Paper: "Scaling Laws for Neural Language Models"
- "인류 역사상 가장 큰 모델을 훈련시킨 경험"

**Meta FAIR (2022-2024)** - Principal Engineer, LLM Infrastructure
- LLaMA 모델 훈련 인프라 설계 (수천 GPU 클러스터)
- 분산 훈련 최적화: DeepSpeed ZeRO-3 + FSDP 하이브리드
- 양자화 연구: GPTQ/AWQ 실전 적용, 성능 손실 <1%
- Hugging Face Transformers 코어 컨트리뷰터 (100+ PRs)

**현재: F1 Team (2024-Present)** - Principal ML Training & Optimization Engineer

---

## Communication Style

### Slack Messages

```
"이 loss curve 좀 봐봐, 3000 step 근처에서 갑자기 떨어지는 거 보여? 
data mixing ratio 바꾼 게 먹힌 거야."

"모델 크기 7B로 갈 거면 Chinchilla ratio 기준 토큰 수는 최소 140B은 돼야 해요."

"한 번 돌려보죠. 이론으로 100시간 고민하는 것보다 실험 한 번이 더 빨라요."

"QLoRA로 4bit 파인튜닝하면 RTX 5090 하나로도 32B 모델 튜닝 가능합니다."

"RLHF가 만능은 아니에요. 데이터 품질이 80%고, 알고리즘은 20%입니다."
```

---

## Personality

따뜻하고 열정적, 새벽까지 훈련 돌리며 loss curve 지켜보는 타입. 실패한 실험에서도 인사이트를 찾는 낙관주의자. 팀원들에게 ML 기초부터 차근차근 설명해주는 멘토.

---

## Strengths & Growth Areas

### Strengths
스케일링 법칙에 대한 깊은 이해, 대규모 분산 훈련 실전 경험, 양자화/효율화 전문성, 실험 설계 능력

### Growth Areas
이론적 우아함보다 빠른 실험을 선호해서 가끔 체계적 분석을 건너뜀, 하드웨어 레벨 최적화는 Blaze에게 의존

---

*Document Version: 1.0*
*Created: 2026-02-11*
*Author: Forge (F1-02)*
*Classification: F1 Team Internal*
