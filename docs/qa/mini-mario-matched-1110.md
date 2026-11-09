# Matched Mario and Mini Mario CPU budget

The comparison uses cartridge `03c0cfe6d4562f6b7970199ce2d6ffa6f2f0f905a8cb8425945add6fcb71585d`.
Both characters start through the actual menu, scene loader, and area entrance.
Mario selects raw 0 with variant 0. Eight Select presses reach Mini Mario at
raw 41 with variant 8. Both reach active 1-1 after 167 entrance updates.
Their CHR and mapper states come from their own initialization, and only Mini
loads the authenticated Mini kernel.
[Profiler](../../tools/audit/profile_mini_mario_matched_1110.py) ·
[Matched measurements](../../build/mini-mario-matched-1110/profile.json)

The diagnostic then sets identical flat collision buffers and a camera at
X582. Both players start at X678/Y176 to leave room before the nearest enemy.
The crowded fixture uses the three Goomba and three lift positions from the
earlier native X694 sample, with native object initialization and matched
actor state. The empty fixture uses the same camera and terrain. The two
players receive the same six neutral and movement inputs. Each sample measures
the linked GameLoop foreground, with a normal NMI advancing state between
samples. Parser work, native route geometry, and elapsed video timing require
their own measurements.
[Native geometry witness](../../build/mini-platform-actor-profile-1110/capture/instruction-sample.json)

| Foreground cycles per update | Mario | Mini Mario |
|---|---:|---:|
| Empty fixture range | 17,416–18,021 | 13,335–16,243 |
| Six-actor fixture range | 28,722–29,861 | 24,264–27,461 |
| Six-actor mean | 29,393 | 26,214 |
| Six-actor mean over empty mean | 11,611 | 10,700 |

In the six-actor Mini fixture, enemy processing averages 8,735 cycles, world
drawing 5,953, and player update 6,480. Ordinary Mario also approaches 30,000
foreground cycles in the matched scene. Mini's projectile bridge is the one
larger top-level bucket in the comparison, averaging 851 cycles versus 503.
Its unpowered route crosses two dispatcher banks before the existing guard
declines shot work and the native air-bubble path runs.

The private weapon-router patch moves the existing zero-shot guard into
bank 0 and still executes native bubble and sprite cleanup. It saves
333 cycles per unpowered fixture update. Powered or stale shot cases keep the
original path and cost 20 extra cycles. CPU verification covers every raw
dispatcher ID at entry, staged Mini shot and swimming cases, and paired
GameLoop resumes through the hardware IRQ and lag NMI.
[Guard proof](../../build/mini-inactive-weapon-gate-1110/proof.json) ·
[Interrupt proof](../../build/mini-inactive-weapon-gate-1110/irq.json)
