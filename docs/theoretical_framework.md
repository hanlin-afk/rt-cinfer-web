# Theoretical Framework

## From correlation to structural optimization

Standard Web Vitals dashboards often identify associations: slow LCP correlates with mobile devices, large images, complex routes, or high RTT. These associations are operationally useful but insufficient for intervention planning because they do not answer the counterfactual question: *what would happen if this intervention were changed while the user and page context remained comparable?*

RT-CInfer-Web frames intervention selection as a structural causal problem. The default graph treats user context, traffic source, network conditions, page complexity, and content size as common causes of both treatment assignment and outcomes.

## Structural causal model

A simplified SCM contains:

- exogenous context variables: device, traffic, region, hour;
- endogenous page variables: route complexity, JavaScript size, image size;
- treatment variables: cache, compression, JavaScript deferral, layout reservation;
- outcome variables: LCP, FID, CLS.

The causal graph is explicit in `src/rt_cinfer_web/scm/graph.py`.

## Doubly robust score

The estimator uses an augmented inverse-propensity weighted score:

\[
\psi_i = \hat{\mu}_1(X_i) - \hat{\mu}_0(X_i)
+ \frac{A_i(Y_i - \hat{\mu}_1(X_i))}{\hat{e}(X_i)}
- \frac{(1-A_i)(Y_i - \hat{\mu}_0(X_i))}{1-\hat{e}(X_i)}
\]

This score combines two nuisance components:

- a treatment assignment model \(\hat{e}(X)\), and
- potential outcome models \(\hat{\mu}_1(X), \hat{\mu}_0(X)\).

The estimator is called "doubly robust" because, under standard assumptions, it remains consistent if either the propensity model or the outcome model is correctly specified. In this repository, the implementation is a transparent online baseline rather than a final statistical guarantee for every production setting.

## Streaming adaptation

The online setting differs from offline causal estimation because the distribution of users, campaigns, page templates, and network conditions can shift. RT-CInfer-Web therefore combines:

- rolling score histories;
- Page-Hinkley metric drift detection;
- population stability index for feature drift;
- uncertainty gates that can hold recommendations during unstable periods.

## Recommendation gate

A recommendation is issued only when:

1. the graph-based adjustment check passes;
2. treatment overlap is adequate;
3. the sample size is above the configured threshold;
4. the confidence interval is narrow enough;
5. the interval supports a beneficial direction.

This design intentionally favors conservative recommendations over false precision.
