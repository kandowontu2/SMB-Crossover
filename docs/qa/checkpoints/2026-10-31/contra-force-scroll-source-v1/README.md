# Contra Force native scrolling publication

The original bounded controller run reached X239 with camera0 and no new terrain or enemies. CF bypassed the native graphics tail that normally publishes Player_Rel_XPos to Player_Pos_ForScroll. The native scroll and parser routines themselves were behaving correctly.

This source child preserves all prior native and private entry PCs. A five-byte CF graphics prefix now calls a12-byte helper in its already-owned unused A3 tail; the helper copies the two genuine native publisher instructions, then the overwritten original CF prefix. The original movement/jump/weapons/art and every non-CF ROM byte are unchanged. The real carrier and full cookie are regenerated (version3).

The inherited source fixture started the native scroll-position field at96. That counterexample is retained and explicitly narrows earlier cold-source coverage. New cohorts start this field at its real AllZeros0 before the genuine menu/Start/parser; no CF cache/state, camera, terrain or enemy is seeded. All four reach X369/camera257 with genuine new terrain and a native Goomba using ordinary jump avoidance.512 full-flag graphics pairs and288 actual native ISR cuts pass;86 menu pairs and10240 Start masks are unchanged.

The separate crouch-fire probes remain failed combat evidence, including a settled duck and fresh B pulses. They are not relabeled as successful shooting or rolled into scrolling success. Root must run a bounded advancing-camera smoke before another full route. No native launch, Download change, staging or commit was performed here.
