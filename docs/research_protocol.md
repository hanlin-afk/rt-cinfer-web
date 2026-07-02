# Research Protocol

## 1. Objective

RT-CInfer-Web studies whether real-time causal inference can provide safer and more interpretable optimization decisions for e-commerce Web Vitals than correlation-only dashboards. The target infrastructure setting is a production-like web delivery stack with changing users, devices, routes, network conditions, content size, and cache behavior.

## 2. Primary estimands

The main estimand is the average treatment effect of a candidate intervention on a Web Vital metric:

\[
\tau = E[Y(1) - Y(0)]
\]

Examples:

- `edge_cache_enabled -> lcp_ms`
- `image_optimization_enabled -> lcp_ms`
- `js_deferral_enabled -> fid_ms`
- `layout_reserve_enabled -> cls`

For LCP/FID/CLS, a negative effect is beneficial because lower values indicate better user experience.

## 3. Data schema

The reference implementation expects event-level records with:

- user/device context: `device_mobile`, `traffic_paid`, `region_west`
- infrastructure context: `network_rtt_ms`, `js_kb`, `image_kb`
- page context: `route_complexity`, `personalization_score`
- temporal context: `hour_sin`, `hour_cos`
- interventions: `edge_cache_enabled`, `image_optimization_enabled`, `js_deferral_enabled`, `layout_reserve_enabled`
- outcomes: `lcp_ms`, `fid_ms`, `cls`

The synthetic generator intentionally creates confounded treatment assignment so that naive treated-control comparisons are biased.

## 4. Identification assumptions

The default backdoor adjustment strategy assumes that observed context variables capture the major common causes of intervention assignment and Web Vitals outcomes. The software checks that:

1. configured covariates include observed common causes in the default graph;
2. post-treatment descendants are not adjusted for;
3. treatment overlap is not degenerate;
4. recommendations are gated when sample size or uncertainty is inadequate.

The software does not prove untestable assumptions. Instead, it makes them explicit and machine-checkable.

## 5. Online estimation design

Each batch is processed as follows:

1. standardize context features using running moments;
2. predict treatment propensity with an online logistic model;
3. predict potential outcomes with separate online linear models;
4. compute AIPW/doubly robust scores;
5. update nuisance models after scoring;
6. maintain rolling scores for standard errors and confidence intervals;
7. evaluate drift and recommendation gates.

## 6. Counterfactual preflight testing

Before a rollout, the simulator applies `do(treatment = 1)` to recent traffic and recomputes the target metric through structural equations. This does not replace a real randomized experiment. It provides a transparent preflight estimate to decide whether a guarded canary is worth considering.

## 7. Reproducibility

Reproducibility is provided through deterministic random seeds, synthetic-data generation, benchmark scripts, unit tests, and a citation file. All benchmark outputs should be labeled synthetic.

## 8. Evidence boundaries

This repository supports technical verification of implementation progress. It does not by itself establish real-world adoption, production deployment, commercial impact, or government use. Those claims require separate documentary evidence.
