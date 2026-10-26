Unchanged731 ownership diagnostic -- no game patch/adoption

One450-frame read-only run, same controller and unchanged731 ROM. All five
original input/PPU/timing/result files and all275 captured frames exactly
match the existing731 reference.402 full256-byte source/destination DMA
pairs pass.432 Main releases,51 completed Rosters,26 no-draw carry images,
343 stale source-epoch transfers and40 protected lag NMIs were observed.
50 distinct Rosters transferred;51 remained pending at the endpoint.

Read ERRATUM.txt first. The49 counterfactual alternations assume normal
V-flip; actual V-flip was not captured. Source fairness is not pixel/shot
fairness. There was no new state byte or scheduling code in this run.

selected-actual-epochs.json retains actual372/445/450 ownership/stack
links, not invented Main instructions. Full raw captures, ROMs, settings,
audio and source ZIPs stay external. external-actual-bindings.json pins
their965 exact paths/hashes for independent review. Original source/native
reports and finite stack/mock tools are included unchanged. Reviewers v1
and v2 had assertion/oracle mistakes; v3 corrected their source bookkeeping
without rerunning native or weakening any original physical256-byte guard.

Versioned prerequisites: the included tools import audit helpers pinned
in external-actual-bindings.json. Those existing helpers are already in
tools/audit; no large repeated tool/source bundles are copied here.
No native grant/retry, implementation, production/default/settings or Git
operation is performed by this checkpoint builder.
