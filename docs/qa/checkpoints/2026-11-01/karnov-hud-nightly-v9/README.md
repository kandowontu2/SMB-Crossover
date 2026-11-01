# Karnov equipment HUD WIP

The exact `99bf88c8` candidate replaces the single Downloads nightly without a
backup. Reopen the ROM and start fresh. Rygar → Select → Karnov → A/Start.

Select cycles earned Boots, Boomerang, Wings and NONE. Down+fresh B activates
the selected equipment. A jumps; B fires. Up/Down control flight. The HUD now
shows the full selected name, original icon, remaining stock and control hint.
Icon shapes are original; the two color planes are swapped for native HUD
contrast. No replacement wing artwork or equipment sprites were invented.

Three Mesen checks explicitly seed six original inventory bytes, then use real
controller input to verify activation, stock01, displayed name/icon, boots88px
jump, boomerang return and flight. They also check actual HUD/world CHR maps.
Separate controller-only runs defeat a Goomba with score/hit SFX, collect an
emerged mushroom, fire double shots, break bricks with debris and trigger a
question block. All90 menu identities/124 transitions pass sampled heading,
gray-portrait and rendering-mask checks. Each native run uses at most4PNGs.

Actual owning Main/IRQ/NMI checks cover equipment, combat, the HUD and cold
loader, with at least12bytes above stack-based code. The twelve-row loader
verifies both cache headers. Legal area transitions and retirement cancel the
HUD lease. Existing other-owner bytes remain exact outside documented imports.
Six source CPU suites cover health, rebound, life restart, terrain and scenes.

One additional controller route failed to reach a second enemy contact and is
preserved as a diagnostic, not a passing fatal-injury playthrough. Original
audio, six other equipment types, earned gear progression, full stages,
shortcuts, all powerups and constant60Hz remain unqualified or unfinished.
The source packets for Kirby's repair, Mario the Tank and Metal Storm are
preserved but are not admitted by this delivery. This remains86 selectable
work-in-progress identities, not a completed roster.
