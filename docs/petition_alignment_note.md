# Petition Alignment Note

This document is written as a technical-evidence map for users who need to explain the repository in a professional or legal filing. It should be edited by counsel before use.

## Accurate description

RT-CInfer-Web is an open-source research implementation for real-time causal inference in e-commerce web infrastructure. It includes structural causal graphs, online doubly robust estimators, drift detection, counterfactual rollout simulation, uncertainty gates, reproducible synthetic benchmarks, examples, tests, and citation metadata.

## What can be verified directly

A reviewer can inspect:

- source code implementing SCM, identifiability, online DR estimation, and recommendation gates;
- synthetic-data generator and benchmark scripts;
- unit tests validating core functionality;
- documentation explaining assumptions and evidence boundaries;
- MIT license and citation metadata.

## What should not be overstated

Do not claim, unless separately documented, that this repository has:

- been deployed by Walmart or any other company;
- processed real commercial traffic;
- produced real revenue gains;
- been adopted by U.S. government operators;
- generated real customer or user data;
- existed before its actual creation date;
- accumulated citations, stars, forks, or external users that it has not actually accumulated.

## Suggested neutral wording

"I released RT-CInfer-Web as a public, MIT-licensed research prototype to make the technical progress of my proposed endeavor inspectable. The repository contains a reference implementation, reproducible synthetic benchmarks, documentation, tests, and citation metadata. It is intended to support future peer-reviewed publication, collaboration, and real-world validation."
