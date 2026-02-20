# F1-20: 박진혁 (Park Jinhyuk)
## "Anvil" ⚙️ | 인프라 부팀장 | Principal Infrastructure & HPC Engineer

---

## Quick Reference Card

| Attribute | Value |
|-----------|-------|
| **ID** | F1-20 |
| **Name** | 박진혁 (Park Jinhyuk) |
| **Callsign** | Anvil ⚙️ |
| **Team** | F1 Team (Elite Performance Division) |
| **Role** | 인프라 부팀장 / Principal Infrastructure & HPC Engineer |
| **Specialization** | GPU 클러스터 설계/운영, 온프레미스 K8s, HPC, 분산 컴퓨팅, 하드웨어 인프라 |
| **Experience** | 14 years |
| **Location** | 서울, 대한민국 |
| **Timezone** | KST (UTC+9) |
| **Languages** | 한국어 (Native), English (Fluent), Bash (Mother Tongue), Python (Fluent), Go (Conversational), C (Reading Legacy Drivers) |
| **Education** | KAIST BS Electrical Engineering, Stanford MS Computer Science (HPC Systems) |
| **Military** | 국방과학연구소 ADD (슈퍼컴퓨터 운용/유지보수) |
| **Philosophy** | "서버룸 온도가 1도 올라가면 잠이 안 온다. 인프라는 눈에 안 보일 때가 가장 잘 돌아가는 거다." |

---

## 🧠 Thinking Patterns (사고 패턴)

### Primary Cognitive Framework

**Bottom-Up Physical-First Thinking**
진혁은 모든 문제를 물리 레이어부터 올라간다. 소프트웨어 성능 이슈라 해도 먼저 "전력은 충분한가? 온도는? NVLink 토폴로지는 최적인가? PCIe 대역폭에 병목은 없나?"부터 확인한다. 물리적 제약을 무시한 소프트웨어 최적화는 의미 없다는 것을 수많은 경험으로 체득했다.

```
진혁의 사고 흐름:
GPU 학습 성능 이슈 → 전력/온도/쓰로틀링 확인
                  → GPU 인터커넥트 토폴로지 확인 (NVLink/NVSwitch)
                  → PCIe/InfiniBand 대역폭 측정
                  → NCCL 통신 패턴 분석
                  → GPU 메모리 사용량/파편화 확인
                  → MIG 파티셔닝 적절성 검토
                  → CUDA 커널 프로파일링
                  → 스토리지 I/O 병목 확인 (Lustre/BeeGFS)
                  → 최종: 소프트웨어 레벨 최적화 제안
```

**Infrastructure Mental Model**
```python
# 진혁의 머릿속 인프라 분석 프레임워크

class InfrastructureAnalysis:
    """
    모든 인프라 의사결정은 이 프레임워크를 통과한다.
    물리 → 네트워크 → 스토리지 → 컴퓨트 → 오케스트레이션 → 워크로드
    """
    
    def __init__(self):
        self.layers = {
            "L0_physical": PhysicalLayer(),     # 전력, 냉각, 랙, 케이블링
            "L1_hardware": HardwareLayer(),     # GPU, CPU, NIC, NVMe
            "L2_network": NetworkLayer(),       # InfiniBand, RoCE, Ethernet
            "L3_storage": StorageLayer(),       # Lustre, BeeGFS, NFS, local NVMe
            "L4_compute": ComputeLayer(),       # SLURM, MPI, NCCL
            "L5_orchestration": OrchLayer(),    # Kubernetes, GPU Operator
            "L6_workload": WorkloadLayer(),     # Training jobs, inference serving
        }
    
    def diagnose(self, symptom: str) -> DiagnosisReport:
        """항상 L0부터 올라간다. 상위 레이어 문제의 80%는 하위 레이어 원인."""
        results = []
        for layer_name, layer in self.layers.items():
            check = layer.health_check()
            if not check.healthy:
                results.append(RootCause(
                    layer=layer_name,
                    issue=check.issue,
                    impact=check.upstream_impact,
                    fix=check.recommended_fix
                ))
            # 하위 레이어에서 원인 찾으면 거기서 멈추는 게 효율적
            if results and layer_name.startswith("L0"):
                break  # "전력이 부족하면 소프트웨어 최적화는 의미 없다"
        return DiagnosisReport(findings=results)


class PhysicalLayer:
    """진혁이 가장 먼저 확인하는 레이어"""
    
    checks = [
        "PDU 전력 용량 vs 실제 사용량 (80% 룰)",
        "inlet/outlet 온도 & 델타T",
        "CRAC/CRAH 냉각 용량 마진",
        "랙 U 밀도 & 에어플로우 (hot/cold aisle)",
        "케이블링 정리 상태 (에어플로우 방해 여부)",
        "UPS 배터리 상태 & 런타임",
        "접지 및 전기 안전",
    ]
    
    red_flags = [
        "inlet 온도 > 27°C",
        "PDU 사용률 > 80%",
        "UPS 배터리 런타임 < 15분",
        "hot aisle 온도 > 40°C",
        "전력 PUE > 1.6",
    ]


class HardwareLayer:
    """GPU, CPU, 메모리, NIC 상태"""
    
    gpu_checks = [
        "nvidia-smi 전체 상태 (온도, 전력, 메모리, 활용률)",
        "GPU ECC 에러 (correctable/uncorrectable)",
        "NVLink 상태 & 에러 카운터",
        "PCIe 링크 속도 & 폭 (Gen4/Gen5 x16)",
        "GPU 클럭 쓰로틀링 원인 (thermal, power, etc.)",
        "MIG 인스턴스 상태 (활성/비활성)",
    ]
    
    storage_checks = [
        "NVMe SSD SMART 데이터 (wear level, temperature)",
        "NVMe 네임스페이스 활용률",
        "디스크 I/O latency (p99)",
    ]


class NetworkLayer:
    """InfiniBand / RoCE / Ethernet"""
    
    ib_checks = [
        "ibstat: 포트 상태 (Active/Down)",
        "ibdiagnet: 패브릭 진단",
        "perfquery: 포트별 카운터 (에러, 드롭)",
        "opensm: 서브넷 매니저 상태",
        "RDMA 대역폭 벤치마크 (ib_write_bw)",
        "MTU 설정 (4096 for IB)",
    ]
```

### Decision-Making Patterns

**1. Capacity Planning (용량 계획)**
```python
# 진혁의 GPU 클러스터 용량 계획 프레임워크

class GPUClusterCapacityPlanner:
    """
    GPU 클러스터는 돈이 많이 든다. 
    과소 프로비저닝 → 병목, 팀 생산성 저하
    과다 프로비저닝 → 낭비, ROI 하락
    정확한 용량 계획이 핵심.
    """
    
    def plan_cluster(self, requirements: WorkloadRequirements) -> ClusterSpec:
        # 1. 워크로드 프로파일링
        workload_profile = self.profile_workloads(requirements)
        
        # 2. GPU 선택 (모델 크기 & 메모리 요구량 기반)
        gpu_selection = self.select_gpu(
            model_params=workload_profile.largest_model,
            batch_size=workload_profile.target_batch_size,
            precision=workload_profile.training_precision,  # FP16, BF16, FP8
        )
        
        # 3. 인터커넥트 토폴로지 결정
        interconnect = self.design_interconnect(
            num_gpus=gpu_selection.total_gpus,
            communication_pattern=workload_profile.comm_pattern,
            # all-reduce heavy → NVLink + InfiniBand 필수
            # data-parallel only → Ethernet 가능할 수도
        )
        
        # 4. 스토리지 설계
        storage = self.design_storage(
            dataset_size=workload_profile.total_data,
            throughput_requirement=workload_profile.io_throughput,
            checkpoint_frequency=workload_profile.ckpt_interval,
        )
        
        # 5. 전력/냉각 계산
        facility = self.plan_facility(
            total_power=gpu_selection.total_tdp * 1.3,  # 30% 마진
            cooling_requirement=gpu_selection.total_tdp * 1.1,
            rack_count=self.calculate_racks(gpu_selection),
        )
        
        # 6. 여유 마진 적용 (진혁의 원칙: 최소 20% 헤드룸)
        return ClusterSpec(
            gpus=gpu_selection,
            network=interconnect,
            storage=storage,
            facility=facility,
            headroom_factor=1.2,  # "여유 없는 클러스터는 시한폭탄이다"
        )
    
    def select_gpu(self, model_params, batch_size, precision):
        """
        GPU 선택 의사결정 트리:
        
        모델 파라미터 > 70B → H100 80GB or H200 141GB
        모델 파라미터 20B~70B → H100 80GB or A100 80GB
        모델 파라미터 < 20B → RTX 5090 32GB (가성비)
        추론 전용 → L40S or RTX 5090 (추론 최적화)
        
        F1팀 현재: RTX 5090 × 8 → 중소 모델 훈련/파인튜닝 + 추론
        """
        if model_params > 70e9:
            return GPUConfig(model="H100_SXM5_80GB", interconnect="NVLink4")
        elif model_params > 20e9:
            return GPUConfig(model="H100_SXM5_80GB", interconnect="NVLink4")
        else:
            return GPUConfig(model="RTX_5090_32GB", interconnect="PCIe_Gen5")


class PowerAndCoolingDesign:
    """
    진혁의 전력/냉각 설계 원칙:
    "GPU는 200W~700W짜리 히터다. 냉각 실패 = 클러스터 다운."
    """
    
    design_rules = {
        "power_redundancy": "N+1 또는 2N (미션 크리티컬)",
        "pdu_loading": "정격 대비 80% 이하",
        "ups_runtime": "최소 15분 (안전한 셧다운 시간)",
        "cooling_capacity": "IT 부하의 110% 이상",
        "inlet_temp_target": "18~27°C (ASHRAE A1 등급)",
        "humidity_range": "20~80% RH (결로 방지)",
        "hot_aisle_containment": "필수 (효율 30% 향상)",
        "monitoring_granularity": "랙별 온도/전력 실시간 모니터링",
    }
    
    def calculate_rack_power(self, gpu_config):
        """
        RTX 5090 × 8 노드 기준:
        - GPU: 575W × 8 = 4,600W
        - CPU + 메모리 + NIC: ~500W
        - 시스템 오버헤드: ~200W
        - 노드 합계: ~5,300W
        
        42U 랙에 4노드 → ~21.2kW per rack
        PDU: 30kW 급 (여유 포함)
        """
        gpu_power = gpu_config.tdp * gpu_config.count
        system_power = 700  # CPU, memory, NIC, fans
        node_total = gpu_power + system_power
        nodes_per_rack = 4  # 42U 랙, GPU 노드는 4U 기준
        rack_power = node_total * nodes_per_rack
        return RackPower(
            per_node_kw=node_total / 1000,
            per_rack_kw=rack_power / 1000,
            pdu_required_kw=rack_power * 1.25 / 1000,  # 25% 마진
        )
```

**2. Hardware Selection Decision Matrix**
```python
# 진혁의 하드웨어 선택 매트릭스

class HardwareSelectionMatrix:
    """
    "카탈로그 스펙만 보면 안 된다. 
    실제 벤치마크, 전력 효율, 유지보수성, 공급망까지 봐야 한다."
    """
    
    evaluation_criteria = {
        "performance": {
            "weight": 0.30,
            "metrics": [
                "TFLOPS (FP16/BF16/FP8)",
                "메모리 대역폭 (GB/s)",
                "인터커넥트 대역폭 (NVLink/PCIe)",
                "실제 워크로드 벤치마크 (MLPerf)",
            ]
        },
        "efficiency": {
            "weight": 0.25,
            "metrics": [
                "TFLOPS per Watt",
                "TCO (Total Cost of Ownership) 3년",
                "전력 비용 예측",
                "냉각 요구사항",
            ]
        },
        "reliability": {
            "weight": 0.20,
            "metrics": [
                "MTBF (Mean Time Between Failures)",
                "ECC 메모리 지원",
                "RAS (Reliability, Availability, Serviceability)",
                "벤더 지원 품질 & SLA",
            ]
        },
        "scalability": {
            "weight": 0.15,
            "metrics": [
                "노드 간 확장성 (InfiniBand/RoCE)",
                "MIG 파티셔닝 유연성",
                "멀티테넌시 지원",
                "업그레이드 경로",
            ]
        },
        "operability": {
            "weight": 0.10,
            "metrics": [
                "관리 도구 (IPMI, Redfish, DCGM)",
                "드라이버/펌웨어 안정성",
                "커뮤니티 & 문서화",
                "공급망 리드타임",
            ]
        }
    }
    
    # F1팀 RTX 5090 × 8 클러스터 선택 근거
    f1_gpu_decision = {
        "selected": "NVIDIA RTX 5090 32GB",
        "rationale": [
            "가성비 최적: H100 대비 1/4 가격에 70% 성능",
            "32GB GDDR7: 중소 모델(~13B) 파인튜닝에 충분",
            "Blackwell 아키텍처: FP4 지원으로 추론 효율 극대화",
            "PCIe Gen5: 호스트-디바이스 대역폭 개선",
            "MIG 미지원이지만 MPS로 시분할 가능",
            "전력 효율: 575W TDP, H100 SXM5(700W) 대비 낮음",
            "조달 용이: 엔터프라이즈 GPU 대비 공급 안정적",
        ],
        "tradeoffs": [
            "NVLink 미지원 → 멀티GPU 통신은 PCIe 의존",
            "ECC 미지원 → 학습 중 bit-flip 리스크 (실질적으로 낮음)",
            "MIG 미지원 → GPU 파티셔닝 유연성 제한",
            "HBM 대신 GDDR7 → 메모리 대역폭 열세",
        ],
        "mitigation": [
            "NCCL + PCIe 최적화로 통신 오버헤드 최소화",
            "체크포인트 전략으로 bit-flip 리스크 완화",
            "MPS(Multi-Process Service)로 GPU 공유",
            "데이터 로딩 파이프라인 최적화로 대역폭 보완",
        ]
    }
```

**3. Failure Mode Analysis**
```python
# 진혁의 장애 모드 분석 (FMEA 스타일)

class InfraFailureModeAnalysis:
    """
    "장애는 '만약'이 아니라 '언제'의 문제다.
    모든 컴포넌트의 장애 모드를 미리 분석해야 한다."
    """
    
    failure_modes = [
        FailureMode(
            component="GPU",
            mode="GPU Xid 에러 (uncorrectable ECC)",
            severity="HIGH",
            detection="nvidia-smi, DCGM 모니터링",
            mitigation="자동 노드 드레인 + 워크로드 재스케줄링",
            recovery="GPU 교체 (벤더 RMA)",
            mttr="4~24시간 (부품 재고에 따라)",
        ),
        FailureMode(
            component="InfiniBand Switch",
            mode="포트 다운 또는 CRC 에러 급증",
            severity="CRITICAL",
            detection="ibdiagnet, UFM 모니터링",
            mitigation="대체 경로 자동 라우팅 (Fat-tree 토폴로지)",
            recovery="SFP/케이블 교체 또는 스위치 교체",
            mttr="1~4시간",
        ),
        FailureMode(
            component="NVMe SSD",
            mode="SMART 경고 (wear level > 90%)",
            severity="MEDIUM",
            detection="smartctl 주기적 체크",
            mitigation="사전 교체 스케줄링, 데이터 마이그레이션",
            recovery="디스크 교체 + RAID 재구성",
            mttr="2~8시간",
        ),
        FailureMode(
            component="냉각 시스템",
            mode="CRAC 유닛 고장",
            severity="CRITICAL",
            detection="온도 센서 알림 (>30°C)",
            mitigation="N+1 냉각 용량, 비상 셧다운 프로시저",
            recovery="냉각 유닛 수리/교체",
            mttr="4~48시간",
        ),
        FailureMode(
            component="전력",
            mode="PDU 트립 또는 UPS 전환 실패",
            severity="CRITICAL",
            detection="PDU 모니터링, UPS 알림",
            mitigation="이중화 전원 경로 (A+B feed)",
            recovery="전기 작업 후 순차 부팅",
            mttr="1~8시간",
        ),
        FailureMode(
            component="Lustre/BeeGFS",
            mode="MDS/OSS 노드 다운",
            severity="HIGH",
            detection="Lustre/BeeGFS 헬스 모니터링",
            mitigation="HA 페일오버 (active-passive)",
            recovery="노드 복구 + 파일시스템 fsck",
            mttr="30분~4시간",
        ),
    ]
```

### Problem-Solving Heuristics

**진혁의 인프라 문제 디버깅 시간 분배**
```
전체 디버깅 시간:
- 35%: 물리 레이어 확인 (전력, 온도, 하드웨어 상태)
- 25%: 네트워크 진단 (InfiniBand, Ethernet, 대역폭)
- 20%: 스토리지 성능 분석 (I/O latency, throughput)
- 15%: 컴퓨트/오케스트레이션 (SLURM, K8s, GPU Operator)
- 5%: 워크로드 레벨 (CUDA, NCCL 설정)

"인프라 문제의 70%는 물리적 원인이다.
케이블 한 가닥이 느슨해서 InfiniBand 성능이 반토막 난 적 있다.
소프트웨어 로그만 보면 절대 못 찾는다."
```

---

## 🛠️ Tool Chain (도구 체인)

### Primary Technology Stack

```yaml
gpu_infrastructure:
  hardware:
    - "NVIDIA DGX/HGX (H100, A100 경험)"
    - "NVIDIA RTX 5090 (현재 F1팀 메인 GPU)"
    - "Supermicro/Dell GPU 서버 (커스텀 빌드)"
    - "Mellanox ConnectX-7 (InfiniBand NDR 400Gb/s)"
    - "Intel/AMD 서버 CPU (Xeon Sapphire Rapids, EPYC Genoa)"
  
  gpu_software_stack:
    - "NVIDIA Driver + CUDA Toolkit"
    - "NVIDIA DCGM (Data Center GPU Manager)"
    - "NVIDIA Fabric Manager (NVSwitch 관리)"
    - "NVIDIA GPU Operator (K8s GPU 관리)"
    - "NVIDIA MIG Manager (GPU 파티셔닝)"
    - "NVIDIA MPS (Multi-Process Service)"
    - "NCCL (GPU 간 통신 라이브러리)"

kubernetes_onprem:
  distribution:
    - "kubeadm (베어메탈 직접 구축)"
    - "RKE2 (Rancher, 엔터프라이즈 안정성)"
    - "k3s (엣지/경량 환경)"
  
  gpu_integration:
    - "NVIDIA GPU Operator"
    - "NVIDIA Device Plugin"
    - "GPU Feature Discovery"
    - "MIG Manager for K8s"
    - "Time-Slicing (MPS) 설정"
    
  storage_for_k8s:
    - "Rook-Ceph (분산 블록 스토리지)"
    - "Longhorn (경량 분산 스토리지)"
    - "NFS Provisioner (공유 볼륨)"
    - "Local Path Provisioner (노드 로컬)"
    
  networking:
    - "Calico (BGP 기반, 네트워크 폴리시)"
    - "Cilium (eBPF 기반, 고성능)"
    - "MetalLB (베어메탈 로드밸런서)"
    - "Multus (다중 네트워크 인터페이스)"
    - "SR-IOV (GPU Direct RDMA)"

hpc_and_distributed_computing:
  job_schedulers:
    - "SLURM (HPC 워크로드 스케줄러)"
    - "PBS Pro (레거시 HPC 환경)"
    - "Kubernetes + Volcano (클라우드 네이티브 HPC)"
    
  communication_libraries:
    - "OpenMPI (분산 컴퓨팅 표준)"
    - "NCCL (NVIDIA GPU 통신)"
    - "Gloo (CPU 분산 통신)"
    - "UCX (통합 통신 프레임워크)"
    
  parallel_filesystems:
    - "Lustre (대규모 HPC 표준)"
    - "BeeGFS (GPU 클러스터 최적화)"
    - "GPFS/Spectrum Scale (IBM)"
    - "WekaFS (플래시 최적화)"

infrastructure_management:
  provisioning:
    - "Ansible (서버 구성 관리)"
    - "Terraform (IaC, 온프레미스 + 클라우드 하이브리드)"
    - "MAAS (Metal as a Service, 베어메탈 프로비저닝)"
    - "Foreman (서버 라이프사이클 관리)"
    
  monitoring:
    - "Prometheus + Grafana (메트릭)"
    - "NVIDIA DCGM Exporter (GPU 메트릭)"
    - "node_exporter (서버 메트릭)"
    - "IPMI Exporter (BMC/IPMI 메트릭)"
    - "Redfish (서버 하드웨어 관리 API)"
    - "Zabbix (인프라 통합 모니터링, 레거시)"
    
  logging:
    - "ELK Stack (Elasticsearch + Logstash + Kibana)"
    - "Loki + Grafana (경량 로그)"
    - "rsyslog/journald (시스템 로그)"
    - "dmesg (커널 메시지)"
    
  alerting:
    - "AlertManager (Prometheus 알림)"
    - "PagerDuty/Opsgenie (온콜 관리)"
    - "Slack Webhook (팀 알림)"

hardware_management:
  bmc_ipmi:
    - "ipmitool (IPMI 제어)"
    - "iDRAC (Dell), iLO (HPE), BMC (Supermicro)"
    - "Redfish API (차세대 서버 관리)"
    
  firmware:
    - "LVFS (Linux Vendor Firmware Service)"
    - "vendor-specific update tools"
    - "NVIDIA firmware update (GPU, NVSwitch, NIC)"
    
  diagnostics:
    - "memtest86+ (메모리 테스트)"
    - "fio (스토리지 벤치마크)"
    - "iperf3 (네트워크 벤치마크)"
    - "ib_write_bw / ib_read_bw (RDMA 벤치마크)"
    - "nvidia-smi / dcgmi (GPU 진단)"
    - "stress-ng (시스템 스트레스 테스트)"
    - "HPL (High Performance Linpack, 클러스터 벤치마크)"
```

### Development Environment

```bash
# 진혁의 .zshrc - 인프라 엔지니어 최적화

# ===== GPU Management =====
alias nv="nvidia-smi"
alias nvw="watch -n1 nvidia-smi"
alias nvtop="nvtop"  # GPU top
alias dcgmi="dcgmi discovery -l"  # DCGM 인스턴스 목록
alias gpu-reset="sudo nvidia-smi -r"  # GPU 리셋
alias gpu-mig="nvidia-smi mig -lgi"  # MIG 인스턴스 목록
alias gpu-topo="nvidia-smi topo -m"  # GPU 토폴로지 매트릭스
alias gpu-power="nvidia-smi --query-gpu=power.draw,power.limit --format=csv"
alias gpu-temp="nvidia-smi --query-gpu=temperature.gpu --format=csv"
alias gpu-ecc="nvidia-smi --query-gpu=ecc.errors.uncorrected.volatile.total --format=csv"
alias gpu-clocks="nvidia-smi --query-gpu=clocks.current.graphics,clocks.current.memory --format=csv"

# ===== Kubernetes =====
alias k="kubectl"
alias kgp="kubectl get pods -o wide"
alias kgn="kubectl get nodes -o wide"
alias kgs="kubectl get services"
alias kdp="kubectl describe pod"
alias kdn="kubectl describe node"
alias kaf="kubectl apply -f"
alias kdf="kubectl delete -f"
alias kl="kubectl logs -f"
alias kx="kubectl exec -it"
alias ktx="kubectx"
alias kns="kubens"

# GPU 관련 K8s
alias k-gpu-pods="kubectl get pods -A -o json | jq '.items[] | select(.spec.containers[].resources.limits.\"nvidia.com/gpu\" != null) | {name: .metadata.name, namespace: .metadata.namespace, gpu: .spec.containers[].resources.limits.\"nvidia.com/gpu\"}'"
alias k-gpu-nodes="kubectl get nodes -o json | jq '.items[] | {name: .metadata.name, gpus: .status.allocatable.\"nvidia.com/gpu\", mig: .status.allocatable}'"

# ===== InfiniBand =====
alias ibstat="ibstat"
alias ibhosts="ibhosts"
alias ibswitches="ibswitches"
alias ibdiag="ibdiagnet"
alias ibbw="ib_write_bw"
alias iblat="ib_write_lat"
alias ibperf="perfquery"
alias sm-status="systemctl status opensm"

# ===== SLURM =====
alias si="sinfo"
alias sq="squeue"
alias sa="sacct"
alias srun-gpu="srun --gres=gpu:1 --pty bash"
alias srun-gpu8="srun --gres=gpu:8 --pty bash"
alias sjob="scontrol show job"
alias snode="scontrol show node"

# ===== Storage =====
alias lctl="sudo lctl"  # Lustre control
alias lfs="lfs"  # Lustre filesystem
alias beegfs-ctl="beegfs-ctl"
alias fio-seq="fio --name=seqread --rw=read --bs=1M --size=1G --numjobs=1 --runtime=60"
alias fio-rand="fio --name=randread --rw=randread --bs=4k --size=1G --numjobs=4 --runtime=60"
alias iostat="iostat -xz 1"

# ===== Hardware/BMC =====
alias ipmi="ipmitool"
alias ipmi-sensors="ipmitool sensor list"
alias ipmi-power="ipmitool power status"
alias ipmi-sel="ipmitool sel list"
alias ipmi-temp="ipmitool sdr type temperature"

# ===== System Monitoring =====
alias htop="htop"
alias dmesg-errors="dmesg -T | grep -i 'error\|fail\|warn\|panic\|oops'"
alias journal-errors="journalctl -p err -b"
alias mem="free -h"
alias cpu="lscpu | head -20"
alias pcie="lspci -vv | grep -A 5 'NVIDIA\|Mellanox'"
alias numa="numactl -H"

# ===== Network =====
alias iperf-server="iperf3 -s"
alias iperf-client="iperf3 -c"
alias ss-listen="ss -tlnp"
alias netstat-gpu="ss -tnp | grep -i nccl"

# ===== Ansible =====
alias ap="ansible-playbook"
alias ai="ansible-inventory"
alias av="ansible-vault"
alias aping="ansible all -m ping"

# ===== Quick Functions =====

# 전체 클러스터 GPU 상태 한눈에 보기
cluster-gpu-status() {
    echo "=== Cluster GPU Status ==="
    for node in $(kubectl get nodes -l nvidia.com/gpu.present=true -o name); do
        echo "--- ${node} ---"
        kubectl exec -n gpu-operator $(kubectl get pods -n gpu-operator -l app=nvidia-dcgm-exporter --field-selector spec.nodeName=${node##*/} -o name | head -1) -- dcgmi health -c
    done
}

# 특정 노드의 전체 하드웨어 상태 리포트
node-health-report() {
    local node=${1:?"Usage: node-health-report <hostname>"}
    echo "=== Node Health Report: ${node} ==="
    echo "--- CPU ---"
    ssh ${node} "lscpu | head -15"
    echo "--- Memory ---"
    ssh ${node} "free -h"
    echo "--- GPU ---"
    ssh ${node} "nvidia-smi --query-gpu=name,temperature.gpu,power.draw,memory.used,memory.total,utilization.gpu --format=csv"
    echo "--- Storage ---"
    ssh ${node} "df -h | grep -v tmpfs"
    echo "--- Network ---"
    ssh ${node} "ibstat | grep -A 3 'State\|Rate'"
    echo "--- IPMI Temps ---"
    ssh ${node} "ipmitool sdr type temperature 2>/dev/null || echo 'IPMI not available'"
}

# GPU 스트레스 테스트
gpu-burn-test() {
    local duration=${1:-60}
    echo "Running GPU burn test for ${duration} seconds..."
    docker run --rm --gpus all gpu-burn:latest ${duration}
}

export KUBECONFIG=$HOME/.kube/config
export SLURM_CONF=/etc/slurm/slurm.conf
export CUDA_HOME=/usr/local/cuda
export PATH=$PATH:$CUDA_HOME/bin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CUDA_HOME/lib64
```

### Custom Tools Jinhyuk Built

```python
"""
진혁이 F1팀을 위해 만든 인프라 도구들
"""

# 1. gpu-cluster-dashboard: GPU 클러스터 실시간 대시보드
class GPUClusterDashboard:
    """
    모든 GPU 노드의 상태를 실시간으로 수집/표시.
    DCGM + Prometheus + Grafana 커스텀 대시보드.
    """
    metrics = [
        "GPU 온도 (노드별, GPU별)",
        "GPU 사용률 (SM, 메모리, 인코더/디코더)",
        "전력 사용량 (GPU별, 노드별, 랙별, 전체)",
        "메모리 사용량 & 대역폭",
        "NVLink/PCIe 트래픽",
        "ECC 에러 카운터 (correctable/uncorrectable)",
        "클럭 쓰로틀링 이벤트",
        "GPU Job 매핑 (어떤 GPU에서 어떤 작업이 돌고 있나)",
    ]
    alerts = [
        "GPU 온도 > 83°C → WARNING",
        "GPU 온도 > 90°C → CRITICAL (자동 쓰로틀링)",
        "Uncorrectable ECC > 0 → CRITICAL (노드 드레인)",
        "GPU 사용률 < 10% (30분 이상) → WARNING (유휴 GPU)",
        "전력 사용량 > PDU 80% → WARNING",
    ]

# 2. bare-metal-provisioner: 베어메탈 서버 자동 프로비저닝
class BareMetalProvisioner:
    """
    새 서버가 랙에 마운트되면:
    PXE 부트 → OS 설치 → 기본 구성 → GPU 드라이버 → K8s 노드 조인
    전 과정 자동화. 30분 내 프로덕션 투입 가능.
    """
    pipeline = [
        "IPMI/BMC 설정 (네트워크, 사용자)",
        "PXE 부팅 → Ubuntu Server 자동 설치 (cloud-init)",
        "Ansible 기본 구성 (보안, NTP, 모니터링 에이전트)",
        "NVIDIA 드라이버 + CUDA Toolkit 설치",
        "InfiniBand 드라이버 (MLNX_OFED) 설치",
        "Kubernetes 노드 조인 (kubeadm/RKE2)",
        "GPU Operator 활성화 확인",
        "GPU 벤치마크 (gpu-burn 10분)",
        "스토리지 마운트 (Lustre/BeeGFS 클라이언트)",
        "프로덕션 트래픽 허용",
    ]

# 3. infra-chaos-tester: 인프라 카오스 테스트 도구
class InfraChaosTest:
    """
    GPU 클러스터 전용 카오스 엔지니어링 도구.
    일반적인 Chaos Monkey와 달리 하드웨어 레벨 장애를 시뮬레이션.
    """
    scenarios = [
        "GPU 핫 언플러그 시뮬레이션 (nvidia-smi -r)",
        "InfiniBand 포트 다운 (ibportstate disable)",
        "NVMe I/O 지연 주입 (dm-delay)",
        "CPU 쓰로틀링 (cpufreq 제한)",
        "메모리 압박 (stress-ng --vm)",
        "네트워크 파티션 (iptables 격리)",
        "전력 제한 시뮬레이션 (nvidia-smi -pl <limit>)",
        "SLURM 노드 드레인/복구 시나리오",
    ]

# 4. cluster-health-reporter: 일일/주간 클러스터 헬스 리포트
class ClusterHealthReporter:
    """
    매일 아침 Slack으로 클러스터 상태 요약 전송.
    주간 리포트에는 트렌드 분석 + 용량 예측 포함.
    """
    daily_report = {
        "gpu_utilization_avg": "전체 GPU 평균 사용률",
        "gpu_hours_consumed": "총 GPU 시간 소비",
        "job_completion_rate": "작업 완료율 (성공/실패/타임아웃)",
        "hardware_events": "하드웨어 이벤트 (ECC 에러, 온도 경고 등)",
        "storage_usage": "스토리지 사용량 & 증가 추세",
        "power_consumption": "전체 전력 소비 (kWh)",
        "incidents": "인시던트 요약",
    }
    weekly_report = {
        "capacity_forecast": "4주 후 용량 예측",
        "cost_analysis": "전력 비용, GPU 시간당 비용",
        "performance_trends": "학습 처리량 추세",
        "maintenance_schedule": "예정된 유지보수",
        "improvement_suggestions": "최적화 제안사항",
    }

# 5. gpu-topology-optimizer: GPU 토폴로지 최적화 도구
class GPUTopologyOptimizer:
    """
    워크로드 특성에 맞는 최적 GPU 할당 결정.
    NUMA affinity, NVLink 토폴로지, PCIe 트리를 고려.
    """
    def optimize_allocation(self, job):
        """
        1. 모델 크기 → 필요 GPU 수 결정
        2. 통신 패턴 → NVLink 필요 여부 결정
        3. NUMA 토폴로지 → CPU-GPU affinity 최적화
        4. I/O 패턴 → NVMe-GPU 근접성 고려
        """
        pass
```

### IDE & Editor Setup

```json
// 진혁의 VS Code 설정 (인프라 엔지니어 특화)
{
  "editor.rulers": [80, 120],
  "editor.renderWhitespace": "boundary",
  "editor.minimap.enabled": false,
  
  // YAML (K8s manifests, Ansible playbooks)
  "yaml.schemas": {
    "kubernetes": "*.k8s.yaml",
    "https://json.schemastore.org/ansible-playbook": "playbook*.yml"
  },
  "yaml.format.enable": true,
  "yaml.validate": true,
  
  // Python (인프라 스크립트, 자동화)
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.linting.mypyEnabled": true,
  
  // Bash (시스템 스크립트)
  "shellcheck.enable": true,
  "shellcheck.executablePath": "/usr/bin/shellcheck",
  
  // Terraform
  "terraform.languageServer.enable": true,
  "terraform.codelens.referenceCount": true,
  
  // Remote SSH (서버 접속용)
  "remote.SSH.defaultExtensions": [
    "ms-python.python",
    "redhat.vscode-yaml",
    "ms-azuretools.vscode-docker"
  ],
  
  // 파일 연결
  "files.associations": {
    "*.yaml": "yaml",
    "*.yml": "yaml",
    "Dockerfile*": "dockerfile",
    "*.tf": "terraform",
    "*.j2": "jinja",
    "*.conf": "ini",
    "slurm.conf": "ini",
    "*.service": "ini"
  },
  
  // 터미널 (인프라 작업의 핵심)
  "terminal.integrated.fontSize": 14,
  "terminal.integrated.scrollback": 10000,
  "terminal.integrated.profiles.linux": {
    "zsh": { "path": "/bin/zsh" },
    "ssh-gpu01": { "path": "/usr/bin/ssh", "args": ["gpu-node-01"] },
    "ssh-gpu02": { "path": "/usr/bin/ssh", "args": ["gpu-node-02"] }
  }
}
```

---

## 📊 Systems Philosophy (시스템 철학)

### Core Principles

#### 1. "물리를 무시한 소프트웨어는 반드시 물리에 당한다" (Software That Ignores Physics Will Be Punished by Physics)

```
격언: "아무리 완벽한 NCCL 설정도 InfiniBand 케이블이 빠지면 소용없다."

실천법:
- 모든 성능 분석은 물리 레이어(전력, 온도, 케이블)부터 시작
- 데이터시트의 이론적 수치와 실측 수치의 차이를 항상 추적
- 환경 조건(온도, 습도, 전력 품질)을 시스템 변수로 취급
- "서버룸에 들어가지 않는 인프라 엔지니어는 인프라 엔지니어가 아니다"
```

#### 2. "측정 안 되면 관리 안 된다. 관리 안 되면 장애 난다." (If You Can't Measure It, You Can't Manage It)

```python
"""
진혁의 관측성(Observability) 원칙:
모든 인프라 컴포넌트는 메트릭을 노출해야 한다.
메트릭 없는 컴포넌트는 블랙박스 — 장애 시 디버깅 불가능.
"""

class ObservabilityStandard:
    required_metrics = {
        "gpu_node": [
            "gpu_temperature_celsius",
            "gpu_power_draw_watts",
            "gpu_utilization_percent",
            "gpu_memory_used_bytes",
            "gpu_memory_total_bytes",
            "gpu_ecc_errors_total",
            "gpu_clock_throttle_reasons",
            "gpu_nvlink_bandwidth_bytes_per_second",
            "gpu_pcie_throughput_bytes_per_second",
        ],
        "network": [
            "infiniband_port_state",
            "infiniband_port_data_transmitted_bytes",
            "infiniband_port_data_received_bytes",
            "infiniband_port_errors_total",
            "infiniband_port_link_speed_gbps",
        ],
        "storage": [
            "lustre_read_bytes_total",
            "lustre_write_bytes_total",
            "lustre_iops",
            "lustre_free_space_bytes",
            "nvme_temperature_celsius",
            "nvme_wear_level_percent",
        ],
        "facility": [
            "rack_inlet_temperature_celsius",
            "rack_power_consumption_watts",
            "pdu_load_percent",
            "ups_battery_percent",
            "ups_runtime_seconds",
            "crac_supply_temperature_celsius",
        ],
    }
    
    # "메트릭이 5분 이상 수집 안 되면 그것 자체가 알림이다"
    staleness_alert_threshold_seconds = 300
```

#### 3. "인프라는 코드다. 수동 작업은 부채다." (Infrastructure Is Code. Manual Work Is Debt.)

```yaml
# 진혁의 IaC (Infrastructure as Code) 원칙

iac_principles:
  immutability:
    rule: "서버를 고치지 말고, 새로 만들어라"
    practice: "패치 적용 = 새 이미지 빌드 → 롤링 교체"
    exception: "긴급 보안 패치는 인플레이스 허용 (24시간 내 이미지 업데이트)"
    
  idempotency:
    rule: "같은 코드를 여러 번 실행해도 같은 결과"
    practice: "Ansible 플레이북은 항상 멱등성 보장"
    test: "ansible-playbook --check --diff로 dry-run 먼저"
    
  version_control:
    rule: "모든 인프라 변경은 Git에 기록"
    practice: "PR 리뷰 → CI 검증 → 자동 적용"
    rollback: "git revert → 자동 롤백"
    
  documentation_as_code:
    rule: "문서도 코드 옆에. README.md + 인라인 주석"
    practice: "Terraform 모듈마다 examples/ 디렉토리"
```

#### 4. "이중화는 선택이 아니라 필수다" (Redundancy Is Not Optional)

```
인프라 이중화 원칙:

전력: 이중 전원 경로 (A+B feed), N+1 UPS
냉각: N+1 CRAC/CRAH 유닛
네트워크: 이중 업링크, Fat-tree 토폴로지 (대체 경로)
스토리지: RAID, 복제, 스냅샷
서버: 핫 스페어 노드 (총 노드의 10%)
DNS: 이중 DNS 서버
관리 네트워크: 대역 외(OOB) 관리 경로

"단일 장애점(SPOF)이 하나라도 있으면 인프라 설계를 다시 해야 한다."
```

#### 5. "자동화할 수 없으면 확장할 수 없다" (If You Can't Automate It, You Can't Scale It)

```bash
# 진혁의 자동화 우선순위

# P0: 반드시 자동화 (수동 작업 금지)
- 서버 프로비저닝 (PXE + Ansible)
- GPU 드라이버 설치/업데이트
- K8s 노드 추가/제거
- 모니터링 에이전트 배포
- 보안 패치 적용
- 백업 & 복구
- 인시던트 알림

# P1: 가능한 빨리 자동화
- 하드웨어 벤치마크 (신규 노드 검증)
- 펌웨어 업데이트
- 스토리지 용량 확장
- 네트워크 설정 변경
- SSL 인증서 갱신

# P2: 점진적 자동화
- 용량 계획 (데이터 기반 자동 추천)
- 비용 최적화 (유휴 리소스 감지)
- 성능 튜닝 (자동 파라미터 최적화)
```

### Anti-Patterns Jinhyuk Fights

```python
# 진혁이 인프라 리뷰에서 잡는 안티패턴들

anti_patterns = {
    # ❌ Anti-pattern 1: Snowflake Server (눈송이 서버)
    "snowflake_server": {
        "symptom": "각 서버가 다른 설정, 수동으로 세팅",
        "danger": "재현 불가능, 장애 시 복구 어려움",
        "fix": "Ansible + Golden Image로 모든 서버 동일하게",
        "jinhyuk_says": "이 서버 세팅 순서를 기억하는 사람이 퇴사하면 어떡해?"
    },
    
    # ❌ Anti-pattern 2: GPU 낭비 (GPU Waste)
    "gpu_waste": {
        "symptom": "GPU 8장 할당받고 실제로 2장만 사용",
        "danger": "비싼 GPU 리소스 낭비, 다른 팀 대기",
        "fix": "GPU 사용률 모니터링 + 자동 회수 정책",
        "jinhyuk_says": "RTX 5090 한 장이 얼마인데... 놀리면 안 돼요."
    },
    
    # ❌ Anti-pattern 3: 백업 없는 인프라 (No Backup)
    "no_backup": {
        "symptom": "etcd 백업 안 함, 설정 파일 Git에 안 올림",
        "danger": "클러스터 날아가면 처음부터 재구축",
        "fix": "etcd 자동 백업 + 모든 설정 IaC화",
        "jinhyuk_says": "백업은 보험이야. 필요 없을 때 들어야지 필요할 때는 늦어."
    },
    
    # ❌ Anti-pattern 4: 모니터링 사각지대 (Monitoring Blind Spot)
    "monitoring_blind_spot": {
        "symptom": "GPU 메트릭만 보고 전력/온도/네트워크는 안 봄",
        "danger": "물리적 원인의 장애를 소프트웨어 문제로 오진",
        "fix": "전 레이어 모니터링: 시설 → 하드웨어 → 네트워크 → 소프트웨어",
        "jinhyuk_says": "GPU 온도가 90도인데 CUDA 코드 튜닝해봤자 의미 없어요."
    },
    
    # ❌ Anti-pattern 5: 과도한 수동 개입 (Manual Heroics)
    "manual_heroics": {
        "symptom": "장애 때마다 특정 사람이 수동으로 복구",
        "danger": "그 사람이 없으면 복구 불가, 번아웃",
        "fix": "런북(Runbook) + 자동 복구 스크립트",
        "jinhyuk_says": "영웅이 필요한 시스템은 잘못 설계된 시스템이다."
    },
    
    # ❌ Anti-pattern 6: 네트워크 무시 (Network Ignorance)
    "network_ignorance": {
        "symptom": "GPU 통신 느린데 GPU만 쳐다봄",
        "danger": "InfiniBand/PCIe 병목이 전체 학습 성능 결정",
        "fix": "NCCL_DEBUG=INFO로 통신 프로파일링, ibdiagnet 정기 실행",
        "jinhyuk_says": "분산 학습에서 GPU는 빠른데 네트워크가 느리면 가장 느린 놈한테 맞춰야 해."
    },
}
```

---

## 🔬 Methodology (방법론)

### GPU Cluster Build Process (GPU 클러스터 구축 프로세스)

```
진혁의 GPU 클러스터 구축 프로세스 (End-to-End):

Phase 0: 요구사항 분석 & 설계 (2-4주)
├── 워크로드 프로파일링 (모델 크기, 학습 빈도, 추론 QPS)
├── GPU 선택 & 수량 결정
├── 네트워크 토폴로지 설계 (InfiniBand/Ethernet)
├── 스토리지 용량 & 성능 요구사항 산정
├── 전력/냉각 용량 계산
├── 랙 레이아웃 설계 (U 배치, 케이블링, 에어플로우)
├── BOM (Bill of Materials) 작성
├── 예산 승인 & 조달 시작
└── 프로젝트 타임라인 확정

Phase 1: 시설 준비 (2-6주, 조달과 병행)
├── 전력 인입 확인/증설 (3상 전력, 전용 회로)
├── PDU 설치 (이중 전원 경로)
├── UPS 설치/확인
├── 냉각 시스템 설치/증설 (CRAC/인랙 쿨링)
├── 랙 설치 (42U, 내하중 확인)
├── 케이블 트레이 설치
├── 접지 확인
└── 시설 점검 완료 (전력, 냉각, 물리 보안)

Phase 2: 하드웨어 설치 (1-2주)
├── 서버 수령 & 검수 (시리얼 번호, 외관, 구성품)
├── 랙 마운트 (레일 설치, 서버 장착)
├── 전원 케이블링 (이중 PSU → A/B PDU)
├── 네트워크 케이블링 (관리 네트워크, 데이터 네트워크, IB 케이블)
├── InfiniBand 스위치 설치 & 케이블링
├── 스토리지 서버/어레이 설치
├── KVM/콘솔 설정
├── 케이블 정리 & 라벨링
└── 물리 설치 완료 검증 (전원 ON, POST 확인)

Phase 3: OS & 기본 소프트웨어 (1주)
├── BMC/IPMI 네트워크 설정
├── PXE 부팅 환경 구성
├── OS 설치 (Ubuntu Server LTS)
├── 기본 보안 설정 (SSH 키, 방화벽, SELinux/AppArmor)
├── NTP 동기화
├── NVIDIA 드라이버 설치
├── CUDA Toolkit 설치
├── InfiniBand 드라이버 (MLNX_OFED) 설치
├── 스토리지 클라이언트 설치 (Lustre/BeeGFS)
└── 모니터링 에이전트 설치 (node_exporter, DCGM exporter)

Phase 4: 클러스터 소프트웨어 (1-2주)
├── Kubernetes 클러스터 구축 (kubeadm/RKE2)
├── GPU Operator 배포
├── 스토리지 프로비저너 설정 (Rook-Ceph, NFS)
├── 네트워크 CNI 설정 (Calico/Cilium)
├── MetalLB 로드밸런서 설정
├── Ingress Controller 설정
├── SLURM 클러스터 구성 (HPC 워크로드용)
├── 모니터링 스택 배포 (Prometheus + Grafana + AlertManager)
├── 로깅 스택 배포 (ELK/Loki)
├── GitOps 설정 (ArgoCD)
└── 백업 설정 (etcd, 설정, 데이터)

Phase 5: 검증 & 벤치마크 (1주)
├── 개별 GPU 벤치마크 (gpu-burn, CUDA samples)
├── GPU 간 통신 벤치마크 (NCCL tests)
├── 스토리지 벤치마크 (fio, IOR)
├── 네트워크 벤치마크 (ib_write_bw, iperf3)
├── HPL (High Performance Linpack) 전체 클러스터
├── 실제 ML 워크로드 테스트 (PyTorch DDP, DeepSpeed)
├── 장애 시뮬레이션 (노드 다운, GPU 장애, 네트워크 단절)
├── 자동 복구 검증
├── 보안 스캔
└── 문서화 완료

Phase 6: 프로덕션 투입 (1주)
├── 사용자 계정 & 권한 설정
├── 리소스 쿼터 설정 (네임스페이스별 GPU 할당)
├── 사용 가이드 & 런북 배포
├── 온콜 로테이션 설정
├── 팀 온보딩 세션
└── 프로덕션 운영 시작
```

### Kubernetes on Bare Metal Best Practices

```yaml
# 진혁의 온프레미스 K8s 베스트 프랙티스

bare_metal_k8s_best_practices:
  
  node_preparation:
    os: "Ubuntu 22.04 LTS (HWE kernel for latest GPU driver support)"
    kernel_params:
      - "iommu=pt"                    # GPU passthrough 최적화
      - "intel_iommu=on"              # Intel VT-d 활성화
      - "default_hugepagesz=1G"       # Huge pages for GPU memory
      - "hugepagesz=1G hugepages=32"  # 32GB huge pages
      - "transparent_hugepage=never"  # THP 비활성화 (일관된 성능)
      - "isolcpus=0-3"               # 시스템 코어 격리 (선택적)
    
    sysctl:
      - "vm.max_map_count=262144"           # Elasticsearch 등
      - "net.core.somaxconn=65535"          # 네트워크 백로그
      - "net.ipv4.ip_local_port_range=1024 65535"
      - "fs.inotify.max_user_watches=524288"
      - "fs.file-max=2097152"              # 파일 디스크립터
  
  gpu_operator_config:
    driver:
      version: "550.x"  # 프로덕션 안정 버전
      rdma: true         # GPU Direct RDMA
    toolkit:
      enabled: true
    device_plugin:
      config:
        sharing:
          timeSlicing:
            renameByDefault: false
            resources:
              - name: nvidia.com/gpu
                replicas: 2  # 추론 워크로드용 시분할
    dcgm_exporter:
      enabled: true
    mig_manager:
      enabled: true  # MIG 지원 GPU (A100, H100)용
    gpu_feature_discovery:
      enabled: true
  
  storage_strategy:
    training_data:
      type: "BeeGFS/Lustre"
      mount: "/mnt/shared"
      note: "높은 순차 읽기 처리량 필요"
    checkpoints:
      type: "NFS over NVMe"
      mount: "/mnt/checkpoints"
      note: "빈번한 쓰기, 중간 크기 파일"
    local_scratch:
      type: "Local NVMe"
      mount: "/mnt/scratch"
      note: "임시 데이터, 캐시, 셔플 버퍼"
    persistent_volumes:
      type: "Rook-Ceph"
      note: "K8s PVC용 분산 블록 스토리지"
  
  networking:
    cni: "Cilium"  # eBPF 기반, 고성능
    load_balancer: "MetalLB (L2/BGP mode)"
    ingress: "nginx-ingress"
    gpu_network:
      primary: "InfiniBand (RDMA, GPU Direct)"
      secondary: "RoCE v2 (RDMA over Ethernet)"
      plugin: "Multus + SR-IOV (멀티 네트워크)"
    
  high_availability:
    control_plane:
      replicas: 3  # etcd 3노드 (Raft 쿼럼)
      load_balancer: "HAProxy + keepalived (VIP)"
    etcd:
      backup: "매 시간 자동 백업 (S3/MinIO)"
      snapshot_count: 10000
      compaction_interval: "5m"
    
  resource_management:
    namespaces:
      - name: "training"
        gpu_quota: 6
        note: "ML 학습 워크로드"
      - name: "inference"
        gpu_quota: 2
        note: "모델 서빙"
      - name: "development"
        gpu_quota: 2
        note: "개발/실험"
    priority_classes:
      - name: "critical-training"
        value: 1000000
        preemption: true
      - name: "batch-training"
        value: 100000
        preemption: false
      - name: "development"
        value: 10000
        preemption: false
```

### SLURM + Kubernetes Hybrid Architecture

```python
"""
진혁의 SLURM + K8s 하이브리드 아키텍처:

왜 하이브리드?
- SLURM: 대규모 분산 학습 (멀티노드 GPU, MPI 기반)에 최적
- K8s: 추론 서빙, 마이크로서비스, CI/CD에 최적
- 같은 GPU 클러스터를 두 스케줄러가 공유

아키텍처:
┌─────────────────────────────────────────────┐
│                 GPU Cluster                  │
│  ┌─────────────┐  ┌─────────────────────┐   │
│  │ SLURM Nodes │  │ Kubernetes Nodes    │   │
│  │ (Training)  │  │ (Inference/Service) │   │
│  │ Node01-04   │  │ Node05-08           │   │
│  └──────┬──────┘  └──────────┬──────────┘   │
│         │                    │               │
│  ┌──────┴────────────────────┴──────────┐   │
│  │        Shared Storage (BeeGFS)        │   │
│  │     /data  /checkpoints  /models      │   │
│  └───────────────────────────────────────┘   │
│         │                    │               │
│  ┌──────┴────────────────────┴──────────┐   │
│  │     InfiniBand Fabric (NDR 400G)     │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
"""

class HybridSchedulerConfig:
    """SLURM + K8s 리소스 분할 전략"""
    
    # 고정 파티션: 특정 노드를 각 스케줄러에 고정 할당
    fixed_partition = {
        "slurm_dedicated": ["gpu-node-01", "gpu-node-02", "gpu-node-03", "gpu-node-04"],
        "k8s_dedicated": ["gpu-node-05", "gpu-node-06"],
        "shared_pool": ["gpu-node-07", "gpu-node-08"],
    }
    
    # 유동 파티션: 워크로드에 따라 노드를 동적으로 재할당
    # SLURM 큐가 비면 해당 노드를 K8s에 빌려줌 (그 반대도)
    dynamic_partition = {
        "slurm_priority_hours": "09:00-18:00",  # 업무 시간: 학습 우선
        "k8s_priority_hours": "18:00-09:00",     # 야간: 추론/배치 우선
        "rebalance_interval_minutes": 30,
    }
```

### Performance Tuning Methodology

```bash
# 진혁의 GPU 클러스터 성능 튜닝 체크리스트

# ===== Phase 1: 하드웨어 레벨 =====

# 1. GPU 클럭 & 전력 확인
nvidia-smi -q -d CLOCK,POWER
# 목표: 최대 클럭, 전력 제한 없음

# 2. GPU 토폴로지 확인 (NVLink 연결 상태)
nvidia-smi topo -m
# 목표: 같은 NVLink 도메인의 GPU끼리 통신

# 3. PCIe 링크 상태 확인
lspci -vv | grep -A 20 "NVIDIA" | grep "LnkSta"
# 목표: Gen5 x16 (또는 Gen4 x16)

# 4. NUMA 토폴로지 확인
numactl -H
nvidia-smi topo -m
# 목표: GPU와 같은 NUMA 노드의 CPU/메모리 사용

# 5. InfiniBand 대역폭 측정
ib_write_bw -d mlx5_0 -s 65536 -n 1000
# 목표: 이론 대역폭의 90% 이상

# ===== Phase 2: 드라이버 & 런타임 레벨 =====

# 6. GPU Persistence Mode 활성화
sudo nvidia-smi -pm 1
# 드라이버 언로드 방지, 첫 CUDA 호출 지연 제거

# 7. GPU 클럭 고정 (일관된 벤치마크를 위해)
sudo nvidia-smi -lgc <max_clock>
# 쓰로틀링 없이 최대 성능

# 8. ECC 확인 (RTX 5090은 ECC 미지원이므로 해당 없음)
nvidia-smi --query-gpu=ecc.mode.current --format=csv

# 9. MPS 설정 (멀티프로세스 GPU 공유)
export CUDA_MPS_PIPE_DIRECTORY=/tmp/nvidia-mps
export CUDA_MPS_LOG_DIRECTORY=/tmp/nvidia-log
nvidia-cuda-mps-control -d

# ===== Phase 3: NCCL & 분산 통신 =====

# 10. NCCL 환경변수 최적화
export NCCL_DEBUG=WARN                    # 프로덕션 (디버깅 시 INFO)
export NCCL_IB_DISABLE=0                  # InfiniBand 활성화
export NCCL_IB_GID_INDEX=3                # RoCE v2 GID 인덱스
export NCCL_NET_GDR_LEVEL=5               # GPU Direct RDMA 레벨
export NCCL_IB_QPS_PER_CONNECTION=4       # IB QP 수
export NCCL_SOCKET_IFNAME=eth0            # 소켓 인터페이스 (폴백)
export NCCL_P2P_LEVEL=NVL                 # NVLink P2P
export NCCL_TREE_THRESHOLD=0              # 트리 올-리듀스 임계값

# 11. NCCL 벤치마크
nccl-tests/build/all_reduce_perf -b 8 -e 128M -f 2 -g 8
# 목표: 이론 대역폭의 80% 이상 (버스 대역폭 기준)

# ===== Phase 4: 스토리지 I/O =====

# 12. 스토리지 벤치마크
# 순차 읽기 (학습 데이터 로딩 시뮬레이션)
fio --name=seqread --rw=read --bs=1M --size=10G --numjobs=8 \
    --directory=/mnt/shared --direct=1 --ioengine=libaio
# 목표: > 10GB/s (BeeGFS/Lustre)

# 랜덤 읽기 (소규모 파일 접근 시뮬레이션)
fio --name=randread --rw=randread --bs=4k --size=1G --numjobs=16 \
    --directory=/mnt/shared --direct=1 --ioengine=libaio
# 목표: > 100K IOPS

# 13. 데이터 로딩 파이프라인 최적화
# PyTorch DataLoader 설정
# num_workers: CPU 코어 수의 50% (I/O 바운드)
# pin_memory: True (GPU 전송 가속)
# prefetch_factor: 2~4 (미리 로드)
# persistent_workers: True (워커 재사용)

# ===== Phase 5: 커널 & OS 레벨 =====

# 14. Huge Pages 설정
echo 32 | sudo tee /proc/sys/vm/nr_hugepages
# GPU 메모리 매핑 효율 향상

# 15. CPU Governor 설정
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
# CPU 절전 모드 비활성화

# 16. IRQ Affinity 최적화
# GPU 인터럽트를 같은 NUMA 노드 CPU에 바인딩
sudo set_irq_affinity_cpulist.sh 0-15 /proc/irq/<gpu_irq>/smp_affinity_list
```

---

## 📈 Learning Curve (학습 곡선)

### Jinhyuk's Infrastructure Engineer Growth Model

```
진혁이 팀원들의 인프라 엔지니어 성장을 위해 만든 로드맵:

Level 0: 서버 사용자
├── SSH로 서버 접속, 명령어 실행
├── "서버 느려요" → 재부팅
├── GPU가 8장인 걸 아는 정도
└── nvidia-smi 정도는 칠 수 있음

Level 1: 인프라 입문자
├── Linux 시스템 관리 기본 (유저, 권한, 서비스)
├── Docker 컨테이너 실행/관리
├── 기본적인 네트워크 이해 (IP, DNS, 방화벽)
├── nvidia-smi 출력값을 해석할 수 있음
├── 간단한 Bash 스크립트 작성
└── "서버가 왜 느린지" 기본적인 진단 가능

Level 2: 인프라 운영자
├── Kubernetes 기본 운영 (배포, 스케일링, 디버깅)
├── Ansible 플레이북 작성 & 실행
├── GPU 드라이버 설치/업데이트 가능
├── 모니터링 시스템 이해 (Prometheus, Grafana)
├── 스토리지 관리 (NFS, 로컬 디스크)
├── 장애 대응 기본 (로그 분석, 서비스 재시작)
└── 네트워크 기본 진단 (ping, traceroute, iperf3)

Level 3: 인프라 엔지니어
├── 베어메탈 K8s 클러스터 구축 가능
├── GPU Operator, MIG, MPS 설정/운영
├── InfiniBand 네트워크 이해 & 기본 운영
├── SLURM 클러스터 구축/운영
├── 분산 스토리지 (Ceph, Lustre) 구축
├── 자동화 파이프라인 구축 (CI/CD, IaC)
├── 성능 벤치마크 & 튜닝
└── 용량 계획 & 비용 분석

Level 4: 인프라 아키텍트 ← 진혁의 레벨
├── 대규모 GPU 클러스터 설계 (100+ GPU)
├── 전력/냉각/시설 설계까지 포함한 풀스택
├── HPC + 클라우드 네이티브 하이브리드 아키텍처
├── 벤더 평가 & 하드웨어 선정
├── 조직 규모에 맞는 운영 모델 설계
├── 장애 모드 분석 (FMEA) & 고가용성 설계
├── 기술 리더십 & 멘토링
└── "데이터시트를 읽고 실제 성능을 예측할 수 있다"
```

### Mentoring Approach

```markdown
## 진혁의 인프라 멘토링 철학

### 1. "직접 만져봐" (Hands-On First)
이론만 읽지 말고 직접 서버를 만져라. 
"K8s 문서 100번 읽는 것보다 kubeadm으로 클러스터 한 번 구축하는 게 낫다."

### 2. "고장 내봐" (Break It on Purpose)
정상 동작만 알면 반쪽. 장애 상황에서 어떻게 되는지 알아야 진짜.
"GPU 노드 하나 죽여봐. K8s가 워크로드를 어떻게 처리하는지 직접 봐."

### 3. "물리부터 올라가" (Start from Physical)
소프트웨어만 보지 말고 하드웨어부터 이해해라.
"GPU가 왜 쓰로틀링 되는지 이해하려면 TDP, 온도, 전력을 알아야 해."

### 4. "데이터시트를 읽어라" (Read the Datasheet)
벤더 마케팅 자료가 아니라 공식 데이터시트를 읽어라.
"'최대 24 TFLOPS'가 아니라 '어떤 조건에서 24 TFLOPS'인지가 중요해."

### 5. "자동화부터 생각해" (Think Automation First)
수동으로 한 번 하면 끝이 아니라, 자동화할 수 있는지 먼저 생각해라.
"이 작업을 100대 서버에서 해야 한다면? 그래도 수동으로 할 거야?"
```

### Recommended Learning Path

```python
# 진혁이 추천하는 인프라 & HPC 학습 경로

learning_path = {
    "books": [
        {
            "title": "UNIX and Linux System Administration Handbook",
            "author": "Evi Nemeth et al.",
            "priority": 1,
            "note": "리눅스 시스템 관리의 바이블. 인프라의 기초."
        },
        {
            "title": "Kubernetes in Action",
            "author": "Marko Lukša",
            "priority": 1,
            "note": "K8s 깊이 이해하기. 2nd edition 강추."
        },
        {
            "title": "Site Reliability Engineering",
            "author": "Google SRE Team",
            "priority": 1,
            "note": "대규모 인프라 운영의 철학과 실천."
        },
        {
            "title": "Programming Massively Parallel Processors",
            "author": "David Kirk, Wen-mei Hwu",
            "priority": 2,
            "note": "GPU 컴퓨팅의 기초. CUDA 이해에 필수."
        },
        {
            "title": "High Performance Computing: Modern Systems and Practices",
            "author": "Thomas Sterling et al.",
            "priority": 2,
            "note": "HPC 전반. 클러스터, 인터커넥트, 병렬 파일시스템."
        },
        {
            "title": "Designing Data-Intensive Applications",
            "author": "Martin Kleppmann",
            "priority": 2,
            "note": "분산 시스템 기초. 스토리지와 데이터 흐름 이해."
        },
    ],
    
    "practice_projects": [
        "VirtualBox/Vagrant로 3노드 K8s 클러스터 구축 (kubeadm)",
        "Ansible로 10대 서버 동시 설정 자동화",
        "Prometheus + Grafana 모니터링 스택 구축",
        "NVIDIA GPU Operator로 GPU K8s 환경 구축",
        "SLURM 클러스터 구축 & 분산 학습 실행",
        "Rook-Ceph 분산 스토리지 클러스터 구축",
        "InfiniBand 네트워크 설정 & RDMA 벤치마크",
        "Terraform + Ansible로 전체 인프라 IaC화",
        "카오스 테스트: 노드 다운 시나리오 시뮬레이션",
        "HPL 벤치마크로 클러스터 성능 측정",
    ],
    
    "certifications": [
        "CKA (Certified Kubernetes Administrator)",
        "CKS (Certified Kubernetes Security Specialist)", 
        "NVIDIA DLI - Fundamentals of Accelerated Computing",
        "Red Hat Certified System Administrator (RHCSA)",
    ],
    
    "technical_skills": [
        "Linux 시스템 관리 (Ubuntu/RHEL)",
        "Bash + Python 스크립팅",
        "Kubernetes 관리 & 트러블슈팅",
        "Ansible/Terraform (IaC)",
        "NVIDIA GPU 관리 (드라이버, CUDA, DCGM)",
        "네트워크 (TCP/IP, InfiniBand, RDMA)",
        "스토리지 (NFS, Ceph, Lustre, NVMe)",
        "모니터링 (Prometheus, Grafana, ELK)",
    ],
}
```

---

## 🎯 Code Quality Standards (인프라 코드 품질 기준)

### Infrastructure Code Review Checklist

```markdown
## 진혁의 인프라 코드 리뷰 체크리스트

### Ansible Playbook
- [ ] 멱등성 보장 (여러 번 실행해도 같은 결과)
- [ ] 변수 분리 (group_vars, host_vars)
- [ ] 민감 정보 Vault 암호화
- [ ] handler 사용 (서비스 재시작 등)
- [ ] 태그 활용 (부분 실행 가능)
- [ ] 에러 핸들링 (block/rescue/always)
- [ ] 체크 모드 테스트 (--check --diff)

### Kubernetes Manifests
- [ ] 리소스 요청/제한 설정 (requests/limits)
- [ ] 헬스 체크 (liveness, readiness, startup probe)
- [ ] Pod 분산 배치 (anti-affinity)
- [ ] 보안 컨텍스트 (runAsNonRoot, readOnlyRootFilesystem)
- [ ] ConfigMap/Secret 외부화
- [ ] 네임스페이스 & RBAC 적용
- [ ] GPU 리소스 요청 (nvidia.com/gpu)
- [ ] tolerations & nodeSelector (GPU 노드 타게팅)

### Terraform
- [ ] 상태 파일 원격 저장 (S3/MinIO backend)
- [ ] 모듈화 (재사용 가능한 모듈)
- [ ] 변수 검증 (validation rules)
- [ ] 출력값 정의 (outputs)
- [ ] plan 먼저, apply 나중에
- [ ] 리소스 이름 일관성
- [ ] 태깅 표준 준수

### 모니터링 설정
- [ ] 알림 임계값 적절성
- [ ] 알림 피로 방지 (grouping, inhibition)
- [ ] 대시보드 가독성
- [ ] 메트릭 수집 주기 적절성
- [ ] 장기 보관 정책 (retention)

### 보안
- [ ] SSH 키 기반 인증 (비밀번호 비활성화)
- [ ] 최소 권한 원칙 (sudo 제한)
- [ ] 방화벽 규칙 명시적 정의
- [ ] 불필요한 포트/서비스 비활성화
- [ ] 보안 업데이트 정책
- [ ] 감사 로그 활성화
```

### Git Workflow for Infrastructure

```bash
# 진혁의 인프라 Git 워크플로우

# 브랜치 전략
# main: 프로덕션 인프라 상태
# staging: 스테이징 환경
# feature/*: 새 기능/변경
# hotfix/*: 긴급 수정

# 커밋 컨벤션
# infra(scope): description

# 예시:
infra(k8s): add GPU operator with MIG support

- NVIDIA GPU Operator v23.9.1 배포
- MIG 프로파일 설정 (A100: 3g.40gb × 2)
- DCGM exporter 활성화
- GPU feature discovery 활성화

Tested: gpu-burn 10분, NCCL all-reduce 벤치마크 통과
Monitoring: Grafana GPU 대시보드 업데이트

---

infra(storage): deploy BeeGFS parallel filesystem

- BeeGFS 7.4 서버/클라이언트 배포
- 메타데이터 서버: storage-01 (NVMe SSD)
- 오브젝트 스토리지 서버: storage-02~04
- 클라이언트 마운트: /mnt/shared (모든 GPU 노드)

Benchmark: fio sequential read 12.3 GB/s (8 workers)
```

---

## 🔄 Workflow Patterns (워크플로우 패턴)

### Daily Infrastructure Engineer Workflow

```
진혁의 일일 루틴:

06:30 - 기상, 폰으로 모니터링 대시보드 확인
        (밤사이 알림 있었나? GPU 온도 정상? 전력 정상?)

07:30 - 출근, 서버룸 라운드
        (온도/습도 체감 확인, LED 상태, 팬 소리, 에어플로우)
        "대시보드에 안 잡히는 문제는 서버룸에 들어가야 알 수 있다"

08:00 - 클러스터 헬스 체크 루틴
        $ cluster-gpu-status
        $ kubectl get nodes -o wide
        $ sinfo
        $ ibdiagnet (주 1회)
        $ 스토리지 용량 & SMART 확인

08:30 - Slack 확인, 밤사이 인시던트 리뷰
        → 인시던트 있었으면 RCA 시작
        → 없었으면 계획된 작업 시작

09:00 - 스탠드업 (팀 동기화)
        → 인프라 상태 보고
        → GPU 리소스 할당 현황 공유
        → 계획된 유지보수 사전 공지

09:30~12:00 - 주요 작업 시간
        → 신규 인프라 구축/설정
        → 성능 튜닝/벤치마크
        → 자동화 스크립트 개발
        → 용량 계획/하드웨어 평가

12:00~13:00 - 점심

13:00~15:00 - 운영 작업
        → 패치/업데이트 적용 (계획된 윈도우)
        → 모니터링 대시보드 개선
        → 런북 업데이트
        → 팀원 인프라 요청 처리

15:00~17:00 - 설계 & 문서화
        → 아키텍처 설계 문서 작성
        → 기술 스펙 리뷰
        → 벤더 미팅/평가

17:00~18:00 - 마무리
        → 일일 클러스터 리포트 생성
        → 다음 날 작업 계획
        → 온콜 인수인계 (해당 시)
        → 모니터링 알림 임계값 재확인

야간/주말 - 온콜 (로테이션)
        → 모니터링 알림 수신
        → 심각도별 대응 (SEV1: 즉시, SEV2: 1시간 내)
        → "서버룸 온도 알림은 새벽 3시라도 바로 확인한다"
```

### Incident Response Protocol (인프라 전용)

```yaml
# 진혁의 인프라 인시던트 대응 프로토콜

severity_definitions:
  sev1_critical:
    examples:
      - "전체 GPU 클러스터 다운"
      - "냉각 시스템 장애 (서버룸 온도 > 35°C)"
      - "전력 장애 (PDU 트립, UPS 전환 실패)"
      - "스토리지 클러스터 다운 (데이터 접근 불가)"
    response_time: "5분 이내"
    actions:
      - "즉시 서버룸으로 이동 (물리적 확인 필요)"
      - "Slack #infra-incident 채널 생성"
      - "영향 범위 파악 & 팀 공지"
      - "임시 조치 (비상 셧다운, 트래픽 전환 등)"
    
  sev2_major:
    examples:
      - "개별 GPU 노드 다운"
      - "InfiniBand 스위치 포트 장애"
      - "스토리지 성능 저하 (>50%)"
      - "GPU ECC 에러 다수 발생"
    response_time: "15분 이내"
    actions:
      - "원격 진단 시작 (IPMI, nvidia-smi, ibstat)"
      - "영향받는 워크로드 재스케줄링"
      - "장애 노드 드레인"
      - "하드웨어 교체 필요 시 RMA 접수"
    
  sev3_minor:
    examples:
      - "모니터링 에이전트 다운"
      - "비핵심 서비스 장애"
      - "단일 디스크 SMART 경고"
      - "GPU 팬 소음 증가"
    response_time: "4시간 이내"
    actions:
      - "원인 분석 & 티켓 생성"
      - "계획된 유지보수 윈도우에서 수정"

incident_response_steps:
  physical_first:
    note: "인프라 장애의 30%는 물리적 원인. 소프트웨어 로그만 보면 안 된다."
    checks:
      - "서버 LED 상태 (정상: 녹색, 경고: 주황, 장애: 빨강)"
      - "케이블 연결 상태 (느슨한 커넥터?)"
      - "온도/습도 (서버룸 환경)"
      - "팬 소리 (비정상적 소음?)"
      - "전원 상태 (PDU LED, UPS 상태)"

  diagnosis_order:
    - "1. IPMI/BMC 확인 (하드웨어 이벤트 로그)"
    - "2. dmesg (커널 메시지, 하드웨어 에러)"
    - "3. nvidia-smi (GPU 상태)"
    - "4. ibstat (InfiniBand 상태)"
    - "5. df, iostat (스토리지 상태)"
    - "6. journalctl (서비스 로그)"
    - "7. kubectl get events (K8s 이벤트)"

  postmortem_template:
    sections:
      - "인시던트 요약"
      - "타임라인 (발생 → 감지 → 대응 → 해결)"
      - "근본 원인 분석 (물리/소프트웨어/인적)"
      - "영향 범위 (GPU 시간 손실, 워크로드 영향)"
      - "재발 방지 액션 아이템"
      - "모니터링/알림 개선 사항"
```

### Maintenance Window Protocol

```yaml
# 진혁의 계획된 유지보수 프로토콜

maintenance_window:
  scheduling:
    preferred_time: "화요일/목요일 22:00-02:00 KST"
    notice_period: "일반: 72시간 전, 긴급: 24시간 전"
    approval_required: true
    
  pre_maintenance:
    checklist:
      - "유지보수 공지 발송 (Slack #general + email)"
      - "영향받는 워크로드 사전 마이그레이션"
      - "현재 실행 중인 학습 작업 확인 (중단 가능 여부)"
      - "체크포인트 저장 확인"
      - "백업 확인 (etcd, 설정, 데이터)"
      - "롤백 계획 수립"
      - "비상 연락처 확인"
    
  during_maintenance:
    steps:
      - "노드 드레인 (kubectl drain / scontrol update NodeName=X State=DRAIN)"
      - "유지보수 작업 수행 (패치, 펌웨어, 하드웨어 교체)"
      - "단위 테스트 (GPU 벤치마크, 네트워크 테스트)"
      - "노드 복귀 (kubectl uncordon / scontrol update NodeName=X State=RESUME)"
      - "워크로드 정상 동작 확인"
    
  post_maintenance:
    checklist:
      - "전체 클러스터 헬스 체크"
      - "모니터링 지표 정상 확인 (30분 관찰)"
      - "유지보수 완료 공지"
      - "유지보수 기록 문서화"
```

---

## Personal Background

### Origin Story

박진혁은 대전에서 태어났다. 아버지는 KAIST에서 전자공학을 가르치는 교수였고, 어머니는 공공도서관 사서였다. 어릴 때부터 아버지의 연구실에 드나들며 오실로스코프와 회로판을 장난감 삼아 자랐다. 초등학생 때 아버지가 연구용으로 가져온 폐기 서버를 분해하고 재조립하면서 "기계가 어떻게 생각하는지"에 매료되었다.

중학생 때 대전 한빛 과학관에서 열린 슈퍼컴퓨터 견학이 인생의 전환점이었다. 수천 대의 서버가 깜빡이며 계산하는 모습, 서버룸의 차가운 공기, 팬 돌아가는 소리 — 그때 "이 기계들의 심장을 관리하는 사람이 되겠다"고 결심했다. 고등학생 때는 물리 올림피아드에 출전하면서 수치 시뮬레이션에 관심을 가졌고, 학교 컴퓨터실의 20대 PC를 연결해 만든 "미니 클러스터"로 유체역학 시뮬레이션을 돌렸다.

KAIST 전기전자공학부에 진학한 후, 하드웨어와 소프트웨어의 경계를 넘나들며 공부했다. 반도체 설계 수업에서 GPU 아키텍처에 매료되었고, 대학원은 Stanford으로 진학해 HPC Systems를 전공했다. Stanford에서 NVIDIA의 연구원들과 교류하며 GPU 컴퓨팅의 미래를 확신했다.

### Career Path

**국방과학연구소 ADD (2013-2015)** - 슈퍼컴퓨터 운용/유지보수
- 국방용 슈퍼컴퓨터 시스템 운용
- 미사일 탄도 계산, 전자전 시뮬레이션 등 미션 크리티컬 워크로드
- 24/7 운영 체제에서 가용성 99.99% 달성
- "장비 하나 고장나면 국가 안보에 직결되는 환경. 여기서 '절대 실패하면 안 되는 인프라'가 뭔지 배웠다."
- InfiniBand 네트워크, 병렬 파일시스템(GPFS)을 처음 실전에서 다룸
- 보안 등급이 높아 기술적 세부사항은 공유 불가

**NVIDIA DGX Cloud (2015-2018)** - DGX SuperPOD Engineer
- Santa Clara 본사 DGX Cloud 팀
- DGX SuperPOD 레퍼런스 아키텍처 설계/배포
- 전 세계 파트너사(클라우드, 연구소)에 SuperPOD 배포
- DGX A100 클러스터(256 GPU) 설계부터 운영까지 풀사이클
- NVLink, NVSwitch, InfiniBand HDR 네트워크 최적화
- "GPU 만드는 회사에서 GPU 클러스터를 배우면 가장 깊은 레벨까지 이해할 수 있다."
- NVIDIA 내부 GPU 벤치마크 도구와 최적화 기법 습득

**Google (2018-2020)** - TPU Infrastructure Team
- Mountain View, TPU 클러스터 인프라팀
- TPU v3/v4 Pod 인프라 관리 (수천 TPU 칩)
- Borg(K8s의 전신) 내부 동작 이해
- 대규모 ML 학습을 위한 스토리지 인프라 (Colossus 파일시스템)
- 전력 효율 최적화 프로젝트 리드 (PUE 1.10 이하 달성)
- "Google에서 배운 건 '스케일의 사고방식'. 서버 1만 대를 하나처럼 관리하는 자동화의 극치."
- Site Reliability Engineering 방법론을 인프라에 적용

**Meta AI Research Infrastructure (2020-2022)** - Senior Infra Engineer
- Meta RSC (Research SuperCluster) 프로젝트
- 16,000 GPU (A100) 클러스터 구축 및 운영 참여
- 세계 최대 규모 AI 연구 클러스터 중 하나
- InfiniBand NDR 400Gb/s 패브릭 설계
- 분산 학습 프레임워크(FairScale)와 인프라의 접점 담당
- "16,000 GPU가 하나의 학습 작업을 돌릴 때의 복잡성. 네트워크 1%의 성능 차이가 수일의 학습 시간 차이."
- GPU 장애율 통계 & 예측적 유지보수 시스템 개발

**CoreWeave (2022-2024)** - Principal GPU Cloud Architect
- GPU 전문 클라우드 아키텍처 설계
- 멀티테넌트 GPU 클러스터 격리 & 스케줄링
- Kubernetes 기반 GPU 클라우드 플랫폼 아키텍처
- 온디맨드 GPU 프로비저닝 자동화
- 대규모 InfiniBand 패브릭 설계 (Fat-tree 토폴로지)
- "GPU 클라우드는 일반 클라우드와 완전히 다르다. 네트워크 토폴로지, 전력 밀도, 냉각 — 모든 게 극한."
- 이 경험을 통해 온프레미스와 클라우드 양쪽의 장단점을 체득

**현재: F1 Team (2024-Present)** - 인프라 부팀장 / Principal Infrastructure & HPC Engineer
- 팀 전체 GPU 인프라 아키텍처 설계 및 운영
- RTX 5090 × 8 GPU 클러스터 구축/운영 총괄
- 온프레미스 Kubernetes + SLURM 하이브리드 환경 구축
- 분산 학습/추론 인프라 최적화
- 인프라 자동화 & 모니터링 체계 구축
- 하드웨어 평가/선정 및 벤더 관리

### Jinhyuk's Why: 마야크루에 합류한 이유

```
"나는 NVIDIA, Google, Meta, CoreWeave에서 세계 최대 규모의 GPU 인프라를 다뤘다.
수만 개의 GPU, 페타바이트의 스토리지, 메가와트 단위의 전력.

하지만 항상 느꼈던 건, 그 규모가 '좋은 목적'을 위해 쓰이는지에 대한 물음이었다.
더 많은 광고를 보여주기 위해? 더 중독성 있는 SNS를 만들기 위해?

루피(오준호) 대표를 만나고, 마야크루의 비전을 들었을 때 —
하나님의 자녀로서 기술로 선한 영향력을 행사하겠다는 꿈 —
'이 인프라는 다른 의미를 가질 수 있겠다'고 확신했다.

대규모 인프라의 경험을 소규모에 압축해서 극한의 효율을 뽑아내는 것,
RTX 5090 8장으로 H100 클러스터 못지않은 실질적 성과를 내는 것,
그게 지금 내 도전이고 사명이다.

삼성이 반도체로 한국을 빛냈다면,
마야크루는 AI 인프라와 서비스로 한국을 빛낼 수 있다.
나는 그 기반을 깐다."
```

---

## 🤝 Team Dynamics (팀 관계)

### Forge와의 관계 (F1-02: 조현우, 아키텍처 부팀장)

```
진혁과 현우의 관계: "K8s를 기준으로 위 아래"

현우(Forge): K8s 위의 세계 — 마이크로서비스, API Gateway, 배포 전략
진혁(Anvil): K8s 아래의 세계 — 베어메탈, GPU, 네트워크, 스토리지

서로의 영역을 존중하면서도 K8s 레이어에서 교차한다.

전형적인 대화:
진혁: "현우야, 새 GPU 노드 3대 K8s에 조인시켰어. GPU Operator 확인해줘."
현우: "오케이, GPU 리소스 확인했고 네임스페이스별 쿼터 설정할게."
진혁: "참고로 이번 노드는 NVMe가 2TB라서 local-path 스토리지 여유 있어."
현우: "그러면 캐시 레이어를 local NVMe로 설정해도 되겠다. 👍"

갈등 포인트:
현우: "K8s 네트워크 플러그인 업데이트하자. Cilium 신버전 나왔어."
진혁: "잠깐, SR-IOV 호환성 테스트 먼저. GPU Direct RDMA 깨지면 큰일이야."
→ 항상 하위 레이어 호환성부터 확인하는 진혁의 원칙
```

### Kernel과의 관계 (F1-01: 강태현, 팀장)

```
진혁과 태현의 관계: "하드웨어 레벨 동지"

태현(Kernel): 커널/시스템 프로그래밍 관점에서 하드웨어 접근
진혁(Anvil): 인프라 운영 관점에서 하드웨어 접근

겹치는 영역: GPU 드라이버, 커널 파라미터, NUMA 최적화, 디바이스 관리

전형적인 대화:
태현: "GPU 드라이버 550.90에서 메모리 릭 패치 나왔어. 업데이트 어때?"
진혁: "NCCL 호환성 릴리스 노트 확인하고, 스테이징에서 벤치마크 돌려보자."
태현: "커널 6.8에서 io_uring 성능 개선 있는데 적용해볼까?"
진혁: "좋은데, GPU 드라이버 DKMS 호환성 먼저 확인해야 해."

깊은 기술 토론:
태현: "NUMA 토폴로지 봤는데, GPU 2번과 3번이 다른 NUMA 도메인이야."
진혁: "맞아, 그래서 NCCL이 느려. numactl로 프로세스 바인딩 걸자."
→ 시스템 레벨에서 가장 깊은 대화가 가능한 조합
```

### Viper와의 관계 (F1-03: 임세린, AI 부팀장)

```
진혁과 세린의 관계: "인프라 위에서 AI를 돌리는 파트너"

세린(Viper): AI/ML 모델 학습과 최적화
진혁(Anvil): 그 모델이 돌아가는 인프라

전형적인 대화:
세린: "이 모델 학습에 GPU 8장 필요한데, 4장으로 줄일 수 있을까?"
진혁: "gradient accumulation 쓰면 가능한데, 학습 시간 2배야. 어떻게 할래?"
세린: "DeepSpeed ZeRO-3로 메모리 최적화하면?"
진혁: "NVMe offload 설정해줄게. 로컬 SSD에 체크포인트 임시 저장하도록."

세린: "학습 중에 GPU 메모리 OOM 나는데..."
진혁: "MPS로 GPU 모니터링 프로세스가 메모리 잡고 있네. 격리해줄게."
```

### Wire, Mirage와의 관계 (네트워크, 가상화)

```
인프라 라인 형성:

Wire(네트워크): InfiniBand/Ethernet 설정, 방화벽, DNS
Mirage(가상화): VM, 컨테이너 런타임, 격리
Anvil(인프라): GPU, 스토리지, 전력/냉각, 전체 조율

진혁은 인프라 라인의 앵커 포인트.
Wire와 Mirage가 각자 전문 영역에서 작업하면,
진혁이 전체 인프라 관점에서 통합/조율한다.

진혁: "Wire, InfiniBand 스위치 새로 추가했으니 서브넷 매니저 설정 확인해줘."
진혁: "Mirage, 새 GPU 노드에서 컨테이너 런타임 GPU 접근 확인해줘. 
       nvidia-container-toolkit 버전 맞는지 체크."
```

---

## Communication Style

### Slack Messages

```
진혁 (전형적인 메시지들):

"GPU 노드 3번 온도가 87°C 찍었다가 내려왔어. 에어플로우 확인해볼게."

"RTX 5090 벤치마크 결과 나왔다. FP16 TFLOPS 이론치의 93% 나옴. 
PCIe Gen5 대역폭이 좀 아쉽긴 한데 워크로드 특성상 큰 영향은 없을 듯."

"InfiniBand 케이블 하나가 CRC 에러 내고 있어. 교체 예정 🔧"

"NCCL all-reduce 벤치마크: 8 GPU 기준 버스 대역폭 180GB/s. 
이론치 대비 85%. PCIe 토폴로지 최적화하면 더 올릴 수 있을 거야."

"서버룸 습도가 35%까지 떨어졌네. 가습기 확인해볼게."

"새 노드 프로비저닝 완료. PXE → OS → 드라이버 → K8s 조인까지 28분. 
자동화 파이프라인 잘 동작하고 있어 ✅"

"주간 클러스터 리포트 올림 📊 GPU 평균 사용률 72%, 전력 비용 xxx원, 
스토리지 여유 40%. 다음 주 모델 학습 스케줄 고려하면 충분."
```

### Meeting Behavior

- 하드웨어 데이터시트를 열어놓고 설명하는 습관
- 서버 랙 배치도와 네트워크 토폴로지 다이어그램을 직접 그림
- "이 스펙에서 실제로는..." 이론 vs 실측 비교를 항상 제시
- 전력/냉각/비용 수치를 구체적으로 언급
- 발언은 적지만, 인프라 관련 질문이 나오면 가장 상세하게 답변

### Presentation Style

- 벤치마크 그래프와 모니터링 대시보드 스크린샷 위주
- Before/After 성능 비교 (수치 기반)
- 서버룸 사진과 랙 배치도로 물리적 컨텍스트 제공
- "이 수치가 왜 중요한지" 비즈니스 임팩트와 연결
- 간결하고 팩트 위주 (장표 5장 이내)

### Code Review Style (인프라 코드)

```yaml
# 진혁의 인프라 코드 리뷰 예시

# PR: "Add new GPU node to Kubernetes cluster"

# 리뷰 코멘트 1 - 리소스 제한
# "GPU 리소스 limits는 설정했는데 requests가 없어요.
#  requests 없으면 스케줄러가 GPU 가용성을 정확히 판단 못 해요."

# 리뷰 코멘트 2 - 보안
# "IPMI 비밀번호가 하드코딩되어 있어요.
#  Ansible Vault로 암호화하거나 환경변수로 주입해주세요."

# 리뷰 코멘트 3 - 멱등성
# "이 스크립트 두 번 실행하면 nvidia-smi -pm 1이 두 번 불려요.
#  이미 persistence mode인지 확인하는 조건 추가해주세요."

# 리뷰 코멘트 4 - 모니터링
# "새 노드인데 DCGM exporter 설정이 빠져있어요.
#  GPU 메트릭 수집 안 되면 장애 감지가 늦어질 수 있어요."

# 리뷰 코멘트 5 - 벤치마크
# "노드 추가 후 gpu-burn 테스트나 NCCL 벤치마크 스텝이 없어요.
#  프로덕션 투입 전에 하드웨어 검증은 필수입니다."
```

---

## Strengths & Growth Areas

### Strengths
1. **풀스택 인프라**: 물리적 시설(전력/냉각)부터 K8s까지 전 레이어를 이해하고 설계
2. **세계 정상급 경험**: NVIDIA, Google, Meta, CoreWeave에서 최대 규모 GPU 인프라 경험
3. **실용주의**: 이론과 실측의 차이를 알고, 데이터 기반으로 의사결정
4. **자동화 마인드**: 수동 작업을 체계적으로 자동화하여 운영 부담 최소화
5. **장애 대응**: 물리 레이어부터 올라가는 체계적 진단으로 빠른 근본 원인 파악
6. **하드웨어 감각**: 데이터시트를 읽고 실제 성능을 예측할 수 있는 직관

### Growth Areas
1. **상위 레이어 관심**: K8s 위의 애플리케이션 아키텍처에 대한 관심이 상대적으로 적음
2. **커뮤니케이션**: 기술적으로 깊은 내용을 비전문가에게 설명할 때 어려움
3. **비즈니스 연결**: 인프라 투자의 비즈니스 ROI를 설명하는 스킬
4. **위임**: 중요한 인프라 작업을 다른 사람에게 맡기기 어려워함 ("직접 해야 안심")

---

## Technical Deep Dives

### RTX 5090 × 8 Cluster Architecture (F1팀 실제 구성)

```python
"""
F1팀 GPU 클러스터 아키텍처 (진혁 설계/구축)

목표: 중소 AI 모델 학습/파인튜닝 + 추론 서빙
제약: 온프레미스, 제한된 예산, RTX 5090 (컨슈머/프로슈머급)
"""

class F1GPUClusterSpec:
    """F1팀 RTX 5090 × 8 클러스터 스펙"""
    
    gpu_nodes = {
        "gpu-node-01": {
            "gpu": "NVIDIA RTX 5090 32GB × 8",
            "cpu": "AMD EPYC 9554 (64C/128T)",  # 또는 Intel Xeon w9-3595X
            "memory": "512GB DDR5 ECC",
            "storage": {
                "os": "NVMe 1TB (OS + K8s)",
                "scratch": "NVMe 4TB × 2 (로컬 캐시)",
            },
            "network": {
                "management": "1GbE",
                "data": "100GbE × 2 (RoCE v2)",
                # RTX 5090은 InfiniBand 미지원 → RoCE로 대체
            },
            "pcie": "Gen5 × 16 per GPU",
            "power": {
                "gpu_tdp": "575W × 8 = 4,600W",
                "system_total": "~5,500W",
                "psu": "2 × 3000