# Paper Evidence Matrix

| Claim | Evidence | Status |
|---|---|---|
| Selective > Uniform | 3-seed validation matched-budget ablation | `SUPPORTED ON 3W; NOT SUPPORTED ON TEP` |
| D/E captures fault semantics | D_ONLY/E_ONLY/FINAL + heatmaps | `SUPPORTED with D-primary/E-complementary wording` |
| Soft allocation matters | Hard vs Soft 3-seed validation ablation | `SUPPORTED ON 3W; NOT SUPPORTED ON TEP` |
| Gain is not from less noise | Soft matched vs unmatched + equal Uniform budget | `SUPPORTED ON 3W; NOT SUPPORTED ON TEP` |
| Diffusion and contrastive learning are complementary | 2×2 CE_REP/Hard-SupCon × NoAug/FINAL, paired 3-seed interaction | `SUPPORTED ON 3W; INVERSE INTERACTION ON TEP / DATASET-DEPENDENT` |
| DCBR mitigates over-augmentation | TEP FINAL/DCBR/SCALING 5-seed development evidence | `SUPPORTED AS DEVELOPMENT EVIDENCE` |
| Cross-WELL benefit | per-WELL replay + bootstrap CI | `PARTIAL; CI crosses zero` |
| Practicality | canonical training time, peak GPU memory, parameters, 3× augmentation/inference benchmark | `SUPPORTED WITH FRERA AUGMENTATION-TIMING LIMITATION` |
| Early-fault score rise | 40 TEP fault-run checkpoint replay, onset alignment and bootstrap bands | `SUPPORTED ON TEP AS DEVELOPMENT EVIDENCE` |
| Critical-ratio sensitivity | 0.20/0.30/0.40, dual-dataset 3-seed downstream results with matched-budget audit | `SUPPORTED AS DATASET-DEPENDENT SENSITIVITY; 0.30 IS A TEP LOCAL TROUGH` |
| External automated augmentation coverage | AutoDA-Timeseries source/protocol audit | `METHOD_NATIVE_ONLY; SUPPLEMENTARY CANDIDATE` |
| Recent time-series baseline comparison | AutoTCL, SoftCLT, TF-C, and TS2Vec over three grouped outer splits and five matched seeds; paired 2,000-resample WELL/Run bootstrap | `POST-HOC FIVE-SEED EXTENSION COMPLETE; TRACK A/B BOUNDARIES APPLY` |
| Industrial diffusion+contrastive DiCL baseline | GitHub/scholarly-source feasibility audit | `NOT FAIRLY REPRODUCIBLE / DO NOT RANK` |
| Limited-data robustness | Complete legal grouped matrix: 3W 100/25/10%; TEP 100/25%; TEP10 E-identifiability hold | `COMPLETE LEGAL MATRIX; DATASET/REGIME-DEPENDENT; NO UNIVERSAL SCARCITY BENEFIT` |
| Missingness robustness | TEP MCAR30 only; 3W native missingness | `PARTIAL` |
| Generalization | completed frozen nested/grouped outer matrix; split-first aggregation and 2,000× WELL/Run bootstrap | `OUTER EVALUATION COMPLETE; DATASET-SPECIFIC EFFECTS IN paper_final_outer_summary.md` |
| Criticality reliability | R-v1 map-noise audit superseded by 15-cell true grouped-bootstrap R-v2 | `R-v2 CORRECTNESS PASS; DIAGNOSTIC ONLY; NOT A CONTROLLER` |
| Paderborn external validation | 1200/1200 grid audit and 45-cell bearing-grouped D-only matrix; paired D-only vs Uniform Macro-F1 delta -0.0030, 95% CI [-0.0491, 0.0538] | `D-ONLY EXTERNAL NO SUPPORT; VALID TRANSFER BOUNDARY EVIDENCE` |

## Frozen contribution mapping

- Contribution 1: Fault-Semantic Criticality Modeling — **WHERE**.
- Contribution 2: Soft Criticality-Aware Selective Diffusion — **HOW TO ALLOCATE**.
- Contribution 3: Domain-Calibrated Budget Routing — **HOW MUCH**.
- R-v2 is reliability diagnostic/boundary analysis, not a controller or fourth forward module.

任何标为 UNSUPPORTED/PENDING 的 claim 不得进入摘要、贡献列表或结论。SVR 保持 `NO_GO_SVR`，不进入最终方法。0.30 因方法冻结保持不变，但不得表述为 TEP 上由本轮 sensitivity 证明的局部最优值。
