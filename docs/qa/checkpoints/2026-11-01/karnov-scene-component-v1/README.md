# Karnov scene/Main integration — private progress

The actual InitScreen consumer now calls a ROM29 wrapper. The complete old
Wf/Bw/S2/Th scene chain runs first, with exactly the same old-owner outputs.
Only selected Karnov then cold-loads the guarded code and constructs its source
state. All 85 admitted menu identities retain their old scene RAM, registers,
flags, maps, CHR latches and loader reads in the comparison cohort.

Source gear, option stock and health survive an area transfer in the same life;
input/action/flight counters and projectiles reset. A lost life or player change
constructs fresh state. An earned extra life no longer fails the movement guard.
These progression fields are explicit fixtures, not controller-earned items.

The real post-BG callback now routes runtime34 directly to its guarded service.
The selector consumes existing fixed-size HotRender padding. It adds four CPU
cycles for each existing owner, preserving their original child/AXYP/SP across
255 comparisons; it adds no extra old-owner farcall or RAM-cache load.

The first level-engine run exposed a jump-apex freeze: a zero-pixel falling step
was misclassified as a ceiling collision, resetting gravity indefinitely. The
fix excludes an already-falling source state from that reset. Four added contact
boundaries and the real 120-Main jump/landing test cover the correction.

For that test, Rygar starts through the real existing menu, then raw34 is assigned
once as an explicit integration fixture. The normal native parser, InitScreen,
entrance, player controller, source movement/weapon updates, PlayerBGCollision,
post-terrain reconciliation, draw and NMI run afterward. This is CPU/mapper
execution, not a native emulator replay, and Karnov is not yet selectable.

Live Main interrupt checks also exposed a tight stack margin. Drawing now calls
its shared graphics body without nesting a second complete register save. The
post-terrain and bounding-box leaves save only the registers they actually use.
Their external register/scratch contracts remain covered by the same checks;
the Main ISR test now requires twelve bytes of reserve above the SMC operands.
Movement saves A/X/Y/P and the foreground pointer pair, keeping R2..R7 untouched.
Future native combat/audio/terrain callback leaves must preserve those scratch
bytes and recheck the live Main stack; do not spend the reserve on nested saves.

Shared dispatch, exact water arithmetic, source body/shot pixels, projectile
motion, native block-query ABI and real interrupt cuts repeat on this candidate.
Cold portraits/names/menu resolution, direct-ID table closure, native combat,
health, earned options/upgrades, original audio and native controller tests remain.
The Downloads nightly stays at the tested 85-character build.

The ZIP contains exact sources/assets and compact receipts, excluding ROM,
object/debug binaries and videos/capture forests. Old linker objects and donor
ROMs remain external inputs. No recursive historical source graph was copied.
