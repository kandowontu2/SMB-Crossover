Meta Knight native graphics audit
================================

prepare_meta_native_nu.py decodes all90 linked descriptors and original cartridge
poses. Its original boss-room capture input must contain pose-*-state.json,
-oam.bin, -palette.bin and -chr.bin. It validates actual original OAM order,
physical patterns and palettes; source ROM is user-supplied and SHA-pinned.

The prepared moves-easy/run.lua and moves-hard/run.lua load the read-only
meta_native_observer_nu.lua plus a frozen copy of the existing component driver.
Those drivers explicitly seed terrain/player/enemy arenas. The observer never
writes emulated state. Run each through run_mesen_isolated.py with the same ROM.

Example sequence (replace paths):

    python tools/audit/prepare_meta_native_nu.py --rom candidate.nes --native-captures original-captures --output audit-output
    python tools/audit/run_mesen_isolated.py --output audit-output/moves-easy audit-output/moves-easy/run.lua candidate.nes --timeout 60 --option=--nes.ramPowerOnState=AllZeros --option=--nes.randomizeCpuPpuAlignment=false --option=--nes.randomizeMapperPowerOnState=false
    python tools/audit/run_mesen_isolated.py --output audit-output/moves-hard audit-output/moves-hard/run.lua candidate.nes --timeout 60 --option=--nes.ramPowerOnState=AllZeros --option=--nes.randomizeCpuPpuAlignment=false --option=--nes.randomizeMapperPowerOnState=false
    python tools/audit/check_meta_native_nu.py --rom candidate.nes --oracle audit-output/oracle.json --output audit-output/check --runs easy=audit-output/moves-easy hard=audit-output/moves-hard

The checker reconstructs actual DMA part order and intrinsic body/sword pixels,
checks native physical CHR and actual palette data, and independently evaluates
nontransparent scanline eligibility. It rejects missing records, palette/CHR
mismatches, wrong composition and permanently unadmitted parts. It observes the
Meta logical OAM reservation and asserts that no pivot splits the body span.

The v5 wrong-priority negative and v7 positive proofs are retained externally:
C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-meta-knight-native-audit
Local small summary: build/verification/meta-knight-native-audit/manifest.json.

Body palette36/14/0F is exact. Sword source30/37/17 is deliberately remapped to
30/27/16. This is not an audio-parity or campaign-clear assertion. Intrinsic
Meta composition excludes unrelated world-sprite occlusion. The component
arenas are not controller-only clears; separate cold fixed route proofs exist.
