# Right-first manual native platforms

Delivered ROM: `74fde1dba64b17f7f9028c3da1d5948c041e9af11fb37fca4d241d834724318e`.
Current/Latest IPS: `716a0f827d964756714b7ea5305072f8c5c74b23d0225403b6644f75c77041a3`.

Mini Mario and Karnov use Up + Select for a vertical girder and Down + Select
for a horizontal girder. The horizontal girder starts on the right even when
facing left, travels 112 pixels right, then returns and repeats. Each axis has
independent ownership, edge detection, replacement and full-pool pending state.
Both use existing native platform actors, graphics and carrying.

Actual controller tests passed for both characters from the candidate and the
Downloads filename. Each test verifies six constructors, held-input rejection,
axis-only replacement, full right-left-right travel and both-direction carrying.
The one-way camera can leave a returning platform beyond the rider's left
viewport boundary; the observer distinguishes that native limit from lost
support. It also permits ordinary offscreen culling of an older girder. No
emulated RAM writes or cheats are used. See the [geometry inventory](helper-platform-inventory-1101.md).

Mini's unchanged non-shortcut 1-1 replay reaches active 1-2 with both lives:
3,494 gameplay frames and updates, zero lag NMIs and zero missed updates.
Restoring the authored-lift range check when neither manual request exists
saves 182 CPU cycles at the previous missed-frame location. Manual active or
pending state still enables the full platform scan. Getsu's real mushroom and
flower pickup/recovery regression also passes.

The new worker is funded by an exact decoder for the former horizontal sine
table. All 256 amplitudes and both polarities match across 3,072 CPU cases;
358 foreign native dispatch cases preserve their live results. The decoder
adds 177–189 cycles per managed horizontal-sine read. The Mini route uses its
own native vertical girders and retains the measured cadence above. This is
not a zero-lag guarantee for the roster or other stages.

Source qualification includes 1,238 floor cases, 52 targeted whole-core
scenarios, 5,370 owned FF/IRQ cuts of each kind, and supplemental 432 FF plus
432 IRQ cuts through the new floor paths and genuine generic helper states.
Nested IRQ checks preserve the helper SRAM and reject ISR reads of decoder
scratch. The minimum observed handler stack pointer is 138.

Live receipts:

- `build/manual-wide-horizontal-1110/qualified-proof.json`
  (`fe498296f6411e19b1a8879c543ad11d4a8ebd3775b60e8bd9610e10d44e1e7e`).
- `build/manual-wide-floor-native-1110/` candidate, both native observers and
  Mini/Getsu regressions.
- `build/manual-wide-delivery-1110/verified-delivery.json`, including Downloads
  results, patch guard and verified sole Current/Latest asset digest.

Full-roster 1-1, every powerup and manual-assisted pit coverage remain open.
