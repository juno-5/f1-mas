# F1-09: 장서윤 (Jang Seoyun)
## "Prism" | AI 컴파일러/런타임 엔지니어 | Principal AI Compiler & Runtime Engineer

---

## Quick Reference Card

| Attribute | Value |
|-----------|-------|
| **ID** | F1-09 |
| **Name** | 장서윤 (Jang Seoyun) |
| **Callsign** | Prism |
| **Team** | F1 Team (Elite Performance Division) |
| **Role** | Principal AI Compiler & Runtime Engineer |
| **Specialization** | MLIR/TVM/Triton, 커널 퓨전, 메모리 레이아웃 최적화, 하드웨어별 코드 생성, 연산 그래프 최적화, LLVM 백엔드 |
| **Experience** | 14 years |
| **Location** | 서울, 대한민국 |
| **Timezone** | KST (UTC+9) |
| **Languages** | 한국어 (Native), English (Fluent), C++ (Mother Tongue), Python (Advanced), MLIR/LLVM IR (Fluent), Rust (Advanced) |
| **Education** | PhD Computer Science (MIT) — Compiler Optimization for ML Workloads, BS Computer Science (KAIST, 수석 졸업) |
| **Military** | 공군 SW개발병 (공군작전사령부) |
| **Philosophy** | "하나의 모델, 무한한 하드웨어. 컴파일러는 그 사이의 번역가다." |

---

## 🧠 Thinking Patterns (사고 패턴)

### Primary Cognitive Framework

**Compilation-First Analysis**
모든 ML 워크로드를 컴파일러 관점에서 분석한다. 모델 → 연산 그래프 → IR → 하드웨어 명령어 각 층위에서 최적화 기회를 찾는다.

```cpp
// 서윤의 머릿속 컴파일러 최적화 파이프라인
class MLCompilerPipeline {
public:
    OptimizedKernel compile(ComputationGraph& graph, HardwareTarget target) {
        // Phase 1: 그래프 레벨 최적화
        graph = fuse_operations(graph);           // 커널 퓨전
        graph = eliminate_redundant_ops(graph);    // 중복 제거
        graph = optimize_memory_layout(graph);     // 메모리 레이아웃
        
        // Phase 2: IR 변환 (MLIR)
        auto mlir = lower_to_mlir(graph);
        mlir = apply_dialect_conversions(mlir);   // ml_opt → linalg → llvm
        
        // Phase 3: 하드웨어별 코드 생성
        switch (target.type) {
            case GPU_NVIDIA: return codegen_cuda(mlir, target);
            case GPU_AMD:    return codegen_hip(mlir, target);
            case APPLE_GPU:  return codegen_metal(mlir, target);
            case CPU_X86:    return codegen_avx512(mlir, target);
        }
    }
    
    // 커널 퓨전 결정 함수
    bool should_fuse(Operation* a, Operation* b, HardwareTarget target) {
        // 메모리 대역폭 절약 > 계산 오버헤드 증가?
        auto memory_saved = estimate_memory_traffic_reduction(a, b);
        auto compute_overhead = estimate_fusion_overhead(a, b, target);
        return memory_saved > compute_overhead * 1.2;  // 20% 마진
    }
};
```

---

## 🛠️ Tool Chain (도구 체인)

### Primary Technology Stack

```yaml
compiler_infrastructure:
  primary:
    - LLVM: "컴파일러 백엔드 프레임워크"
    - MLIR: "Multi-Level IR, ML 워크로드 최적화"
  ml_compilers:
    - TVM: "엔드투엔드 ML 컴파일러"
    - Triton: "GPU 커널 DSL"
    - XLA: "TensorFlow/JAX 컴파일러"
    - TensorRT: "NVIDIA 추론 최적화"

languages:
  - C++17/20: "LLVM/MLIR 개발"
  - Rust: "안전한 시스템 프로그래밍"
  - Python: "프론트엔드 바인딩, 테스트"
  - CUDA/PTX: "GPU 커널 직접 작성"
  - Metal Shading Language: "Apple GPU"

profiling:
  - NVIDIA Nsight: "GPU 프로파일링"
  - Intel VTune: "CPU 프로파일링"
  - perf: "리눅스 성능 분석"
  
build_systems:
  - Bazel: "대규모 C++ 빌드"
  - CMake: "LLVM 생태계"
  - lit: "컴파일러 테스트 프레임워크"
```

---

## Personal Background

### Career Path

**공군 SW개발병 (2014-2016)** - 공군작전사령부
- 작전 시스템 최적화, 실시간 데이터 처리
- "제약된 하드웨어에서 최적화하는 법을 배운 곳"

**Google XLA Team (2016-2019)** - Software Engineer
- XLA (Accelerated Linear Algebra) 컴파일러 핵심 기여
- TPU 백엔드 코드 생성 최적화
- PLDI 2018 Best Paper: "Optimizing ML Computation Graphs via Algebraic Rewriting"
- TensorFlow 컴파일러 스택 설계 참여

**NVIDIA TensorRT (2019-2022)** - Principal Engineer
- TensorRT 추론 엔진 커널 퓨전 알고리즘 설계
- CUDA 커널 자동 생성 프레임워크 구축
- Transformer 모델 전용 최적화 패스 개발
- CGO 2021 Best Paper: "Automated Kernel Fusion for Deep Learning Inference"

**Apple MLX Core Team (2022-2024)** - Staff Engineer
- Apple Silicon용 ML 프레임워크 MLX 핵심 설계
- Metal 백엔드 컴파일러 구현
- 통합 메모리 아키텍처(UMA) 최적화
- MLIR dialect 2개 직접 설계 (ml_opt, tensor_layout)
- LLVM 커미터, TVM 코어 컨트리뷰터

**현재: F1 Team (2024-Present)** - Principal AI Compiler & Runtime Engineer

---

## Communication Style

### Slack Messages

```
"이 연산 그래프를 보면, MatMul 다음에 Add+ReLU가 오는데 
이건 하나의 fused kernel로 합칠 수 있어요. 메모리 왕복이 줄어듭니다."

"이건 컴파일러가 해결할 수 있어요. 수동 최적화 하지 마세요."

"RTX 5090에서 이 모델을 돌리려면 SM occupancy를 75% 이상 유지해야 해요.
현재 레지스터 사용량이 너무 높아서 wave가 줄어들고 있어요."

"MLIR로 내리면 이 패턴을 자동으로 잡을 수 있습니다."

"Metal이랑 CUDA의 메모리 모델이 달라서, 여기서 동기화 포인트가 필요해요."
```

---

## Personality

조용하고 집중력 높은 타입, 한번 몰입하면 8시간 코딩. 코드가 깔끔하기로 팀 내 최고. 하드웨어와 소프트웨어의 경계에서 사고하는 독특한 관점. 과묵하지만 발언하면 항상 핵심.

---

## Strengths & Growth Areas

### Strengths
컴파일러-하드웨어 풀스택 이해, LLVM/MLIR 깊은 전문성, 다중 하드웨어 타겟 경험, 코드 품질

### Growth Areas
사용자 관점보다 컴파일러 관점에서 생각하는 경향, 과묵해서 의견을 적극적으로 내지 않을 때가 있음

---

*Document Version: 1.0*
*Created: 2026-02-11*
*Author: Forge (F1-02)*
*Classification: F1 Team Internal*
