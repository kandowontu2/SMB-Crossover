# Kirby/Meta music source study: ON, uninstalled

This is a provisional instruction-level study. No game source, music asset or
published ROM was changed. Current working gameplay remains OJ. Native hardware
source-call comparisons and a complete DPCM plan remain required before using
these results as a soundtrack repair.

The original58-song Kirby NSF is SHA-256
`eecc93d7b56379d399896c3608ef83a304a0cc54bef4f715fac585054c8eda17`.
The pinned source is initialized exactly once per selected song, then its real
banked6502play routine executes15000calls. No NSF host is present to advance to
another song. NES arithmetic,4KiBbanking and ordered APU stores are modeled.
Lossless original event groups are retained externally.

| Assigned song | Repeated source-call sequence | Estimated existing codec size |
|---|---:|---:|
| Kirby normal, song2 |Start1, period5120|7278bytes|
| Meta normal/hurry, song13 |Start215, period3072|4696bytes|

Each loop repeats exactly through the retained15000call window. This finding
addresses the earlier source-capture flaw: the installed older report found no
loops in15000video-frame captures that could include NSF host song advancement.
Neither the new source-call data nor its smaller size is installed yet. The
estimates do not include a completed initialization/pickup/mixer/DPCM integration.

The source reads4015once per play call. A separate differential executes both
possible DPCM-status paths for both15000call sequences. All53755/76837ordered
APU stores, application RAM and final bank mappings match. The idle path takes
9extra cycles through five source NOPs; returned A/P may differ, and the explicit
NSF call wrapper initializes its input registers. This proves these two paths'
tested music-state equivalence, not actual sample playback or arbitrary hardware
timing. Native mean CPU is approximately2168/2661cycles, with peaks10743/10351;
there is no claim that importing this driver would improve game lag.

Remaining work includes independent Mesen original-call authentication before
host advancement, initialization state, remaining assigned songs, DPCM sample
handling, codec/player call timing, actual source/mixer SFX and restoration,
bank/RAM ownership, native performance and exact-build roster regressions.

Evidence:
`C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-kirby-source-on/source-v1`
and `status-paths-v1`. The full active goal remains incomplete.
