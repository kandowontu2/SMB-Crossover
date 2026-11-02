# Bub/Bob private frontend: native menu pass, 2026-11-02

The static frontend passes the actual controller-only menu run. It remains
private and confirmation-blocked: Bub/Bob gameplay, backend integration,
delivery and full1-1 are not qualified by this menu result. No install or Git
operation was performed by the frontend worker; root owns Mesen and delivery.

Candidate: build/bub-menu-candidate-1102-v2/candidate.nes, SHA256
90a7108003343ad9f5f9719f860f44f09d1e1932194d5eac1c89bc473e932dd8.
It changes exactly1249 bytes within the formal frontend grants over Metal
parent1cd8e192. Other Metal/Ex/Arthur payloads and cookies remain exact. The
later WWF1966 parent change at file792580 (99b7e0→3aaf88) is disjoint and must
be carried by root before eventual combined delivery. It is not in this ROM.

Native-menu3 passes2380 physical frames,33 positions and55 observations:
both source-colored Bub/Bob previews, BT2/CF4, Prince lock, blocked new A/Start,
real simultaneous Select/confirm, title return, options and selector rebuild.
Actual hardware CHR, palette, sprite DMA and the four new BG cells are checked.
There are zero active-display PPUDATA writes and zero late enables. No gameplay
launch or helper platform is part of the run.

All four PNGs were inspected. Zitz and Beans remain coherent. Bub and Bob have
distinct original green/red/white and blue/pink/white colors. Their authentic
16x16 body is intentionally small. The gray icon occupies the new leftX32,
topY160 card (body topY168), separate from the colored center portrait. Names
are BUB/BOB without a pending star, with the ordinary roster cursor. No new
graphical defect was observed; cosmetic resizing was not introduced.

Preserved negative runs:

- native-menu: Mesen DBG importer failed before Lua/gameplay on an incomplete
  synthetic segment900000. The original DBG is retained as
  candidate-importer-negative.dbg. metadata-repair.json binds the corrected
  minimal12-segment/71-global package; ROM bytes did not change.
- native-menu2: reached Bob, then expected Bob after Select+A. The existing
  MnMenuEdges policy applies masked Select through CheckDirection before
  restoring the full input and confirming. Thus actual Bob→Bub was correct.
  The six ordered CPU traces and eight state1 deferred-Select cases in
  ordered-input-v3/CPU-ordered-input.json prove matching names, source palettes
  and OAM, and one deferred toggle. Native-menu3 corrects only expectations:
  Select+A changes Bob→Bub and Select+Start changes Bub→Bob. All visual and
  blocked-confirmation assertions remain exact.

The seven frozen proposal sources and checkpoint v3 remain immutable. New
candidate, metadata and observer recipes have distinct filenames. The final
minimal candidate.dbg/.lbl pair is included in the current compact checkpoint;
the original compose_v2 synthetic DBG requires the explicit metadata repair
before native use. Restore only the small named metadata/negative inputs from
the checkpoint if its exact repair recipe is needed after cleanup.

Prepared, not executed: native-ordered-bt-start and native-ordered-cf-start.
These use original Select-before-confirm ordering to select Zitz/Beans, check
the exact shared P1 restoration queue before menu exit, then require the proper
active owner. Revised Bub/Bob launch plans begin on the predecessor identity;
their preparer rejects the actual SEC gate until backend approval/rebinding.
Raw39 still has SEC at physical66 AD64 in this candidate.

frontend-current-freeze-v3.json records the narrow source stage list, exact
inputs, positive and negative receipts, four PNG hashes and compact archive.
