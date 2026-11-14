# Private DK direct-contact merge over delivered12397

This is a source-only, in-memory rebase. It does not qualify a native full
clear or replace the installed ROM. The frozen769 and historical8623 APIs
remain strict and unchanged.

- Parent: `12397b1c2557834f6a2b7e23c9915d5dc40c6cabff7a6ee844c1adebf6564c52`.
- Private merge: `16c71bc6fb6427ddb0c43dc41d687e768bb4f86015a23204398023fbf3856bd1`.
- Extracted canonical DK image: `769afe8d7fcdb58bed5f9f43109d7aabab3d93b1a7afb0535926e51cffce94ff`.
- Historical merge over3684: `86238670d642b49c905207d4bad3eb84a7d43b41e25760a2cdf3c2e40aaacb35`.

`tools/audit/compose_dkjr_direct_postbg_current_1113.py` exports
`proposal(raw12397)`, `inverse(raw16c71)` and `private_image(raw16c71)`.
The inverse derives original owner bytes from retained source recipes and
strict inverses. It does not use an installed parent or a saved parent copy.
All APIs require their exact typed whole-ROM hash. Immutable image caches
only avoid repeated source reconstruction; proposal metadata is copied on
return.

The complete11433B DK ownership envelope is disjoint from the complete9011B
Bub/foreground envelope and196B postBG envelope. The merged image changes
exactly846 DK bytes from12397 and preserves every unowned byte, all six
new postBG operands, all four canonical49B resident mirrors and all eight
DMC request windows (6584B summed). Two construction orders agree: repair
the six operands on historical8623, or apply only the source-derived DK
delta directly to12397. No new RAM, CHR or native PRG capacity is allocated.

`check_dkjr_direct_postbg_current_1113.py` exits0 in session46080. It checks
the forward/inverse roundtrip, all complete DK envelope bytes against769,
eleven corrupt/wrong-typed image rejections, and two frozen controller
identity-only rebindings. A fresh Python child receives only the candidate
on stdin, blocks every Downloads-ROM read before importing the composer,
and independently reconstructs exact12397 and769 with zero Downloads reads.
The initial240-second invocation67284 hit its runtime bound and is not a
passing receipt. The successful retry uses a600-second bound and progress
markers. Neither invocation wrote generated files.

`controller(raw16c71, full=False)` binds the already-qualified first-item
Lua to `edffd3e8de816ee4810f6b903621a79a766b5df03522ed4bca484b2dc137dbde`.
`controller(..., full=True)` deliberately retains the frozen cd300 full
controller, rebinding it to
`e349756367bcd1bf846bbbb9ea6677c2e6900ebb6cf56e55c2afd6d52007409e`.
That full control policy has a native riser6 negative on769; its rebinding
does not repair or qualify traversal. A separate universal staircase
controller is being source-qualified. No merged native result is claimed.

All producers use bounded `build/dkjr-head-bridge-1113`, max-files1,
stdout/in-memory only. No ROM, capture, backup, release or IPS is produced.
Root owns the sole Mesen queue and any future local nightly delivery.
