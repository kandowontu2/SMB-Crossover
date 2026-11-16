# Jay full status/size tail: independent prelease review

The read-only review passed on exact public `00bb2664647a4ef47b5dfa01c96d50549581d215a33d19a2a6390d1e09078e21`. It executed no 6502 code, applied no proposed overlay, and produced no build files. This closes the new ten-byte tail's source capacity and current consumer/alias review; it does not qualify a repaired ROM.

Audit: `tools/audit/audit_jay_size_tail_consumers_00bb_1116.py`, SHA256 `50f8f78557d9b3f40cb584973d1c087eaab71ce4ed14beb4bdb142aa061c99f6`, API `run(raw00bb)`. Terminal receipt: `d5ae67c67fcf125b8c57b9fa5b3391b7fa7255040727a08eb7a330e82bea22cf`. The bounded invocation used `build/jay-size-tail-independent-source-1116`, max-files 1 / 600 seconds; the root remains absent, with zero generated files.

The reviewed detached plan is `plan_jay_status_size_publication_00bb_1116.py`, SHA256 `6ece60af99ca5d56cd31768c895067a88719fef2ad5d098c35154a86d0aa407d`, descriptor receipt `428e0f3b12cbde2eff093a7c3dd04be37c381bedb269374ebf9f87a6c5e24a1f`. It predicts 116 owned / 72 changed bytes in six spans and whole-image hash `13272464e34237f09c7fce87ac276b20da299f8028640cc51155759d6c642a4d`. These are detached descriptor results, not a composed or tested candidate.

## Capacity and temporal aliases

The pinned producer `check_jay_silius_shotgun_transport_1111.py` explicitly declares a 64-byte TRANSFER slot at staged raw3 A7C0, initializes its carrier with EA, then writes only the 54-byte copier. The current complete 64 bytes hash to `71db90e86f33ef16986a93beeda89963654e2df422147dfe632ad5e2b43433af`. This establishes ten source-owned bytes, rather than inferring ownership from fill. The successful JMP D000 at B7F1..B7F3 and CopyFailed CLC/RTS at B7F4/B7F5 stay exact.

The proposed tail occupies warm raw3 B7F6..B7FF (C-window alias D7F6..D7FF). During cold copy the same source bytes temporarily appear at A7F6..A7FF / C7F6..C7FF. CopyAlternate copies/compares A400..AFDF to B400..BFDF, including that tail as data. Its success enters the unchanged original decoder, which writes/compares the complete primary A000..A8BF before returning to cookie commit. Thus the temporary A7F6 bytes are replaced by the unchanged primary ProgressMux. Failure returns through the preserved CLC/RTS while admission headers remain invalid. The current Steve cold source calls this copier before packet decode and its final cookie commit. This phase-order review binds the current descriptor tables, exact primary, original decoder stage and source; actual successor cold execution remains a postlease gate.

The unchanged primary is 2240 bytes, SHA256 `81902bfd3f641209e2c47749fbd14377203112545a3f945f9b9b1ba6c70db092`. The current decoded packet has 22 typed rows / 10855 bytes, SHA256 `966b8a3cb9bded031dd3e87e0efe9fd439a3e666fa381f3d06ae98a27ef0c318`. None of its raw3 scatter rows overwrites the warm B7F6 tail.

## Current readers and entries

The admitted primary, service/support/motion/extra rows, cold copier, all 22 decoded packet rows, Steve boot and cold code were scanned with their actual raw-bank types. The conservative word scan includes RTS-minus-one leads. It found one real control edge: raw3 B67B JMP A7F6, which enters the unchanged warm primary ProgressMux, not the new B7F6 tail. There is no existing control or relative-branch entry into the proposed warm tail. The only proposed new entry is Main B82C JSR B7F6.

The remaining words are fully classified: service/extra `SEC; SBC BFB7,X` creates an instruction-crossing B7FD coincidence; the raw2 C7F5,Y arithmetic and D7F5..D7FD stores address companion data in raw2, not raw3 aliases. A conservative 256-byte indexed-read extent search finds one actual read, ADC A77D,Y. Its compiled ParserPhase < 8 guard followed by TAY limits it to A77D..A784, the exact eight-byte PhaseAdvance table. The other two candidates begin inside a JMP high byte and a BPL displacement.

Five all-PRG LoHi/raw3 triplet leads were retained and bound to source data. Bank46+3887 and bank107+7403 match complete current music assets. Bank120+7401 is inside the exact 1153-byte S2_DMC_E120 Request16 sample. Bank121+1734 and +2007 lie within exact named ROLL_ART sprite records RlP9O1D1 and RlP10O1D2; the current cfg partitions both inside ROLL_ART, before RD_WX_AUX. These are audio/sample/quad-sprite bytes, not code pointers. No unclassified lead remains in this scoped census. Root's independent current metadata inspection agrees with those five ownership assignments.

The prior moved-reject/retired-leaf review remains `audit_jay_private_label_consumers_00bb_1116.py`, SHA256 `0168fa038f575833dabde4fa70b3ef84d80ed9709c6a8857d6480b2e25002745`, receipt `23be4ccb`; the actual shared-owner ingress review remains receipt `30805c18`. This review adds the new B7F6 tail and temporary aliases without replacing those scopes.

## Proposed contract and remaining gates

The final detached form is Main B82C `20f6b74c32b8`, tail B7F6 `ad3e5f0aa9004cd7beea`, leaf BED7 `8d59072a8d5b0760`. It shares one helper JSR depth, returns to B82F, then jumps to unchanged Supported B832. CopyFailed remains intact. The plan updates all three existing AA cookie roles and preserves the primary carriers and all 34 Metal repair bytes.

Failed status-only df0e remains unqualified. Genuine heart receipt `5d02c293721c27839e8637f5e81bb804d59105a0ecc5e5ca5ab892418bf54d87` demonstrated Size1/Status1/Stars80 and actual CrossoverBlockSize returning Y1, whereas original JnMovement publishes status plus Size0. The successor restores both fields; it does not authorize a new Jay gun, physics, geometry or helper change.

A new root lease is required before proposed CPU or composition. After that, strict inverse/unowned equality, all three actual header identities, cold/failure paths, full public/foreign AXYP and live stack, lifecycle, size/head consumer parity and genuine Flower credit plus 25 completed worker returns remain mandatory. In particular, the new Size0-before-Status order differs from original Status-before-Size0 and needs actual reached IRQ/busy-NMI proof. No new CPU, image, native, installation or delivery result is claimed here.
