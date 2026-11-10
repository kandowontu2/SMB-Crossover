# Kirby: current-ROM inhale, shell and full1-1 checks

No new Kirby gameplay patch was needed for these cases. The existing repairs
now have actual Mesen checks on96 and the installed a5 ROM. Both images use
unchanged Kirby code. The new observers run through the shared stdout-only
queue/watchdog, without cheats, RAM writes, saves, PNGs or other capture files.
They start from the actual cold title and choose Easy Kirby, menu slot12/raw13.

## First native Goomba

The real first Goomba is constructed at worldX352/Y184. Close forward-B is
actually sampled at player285/target298, gap13. The startup suction captures
at gap9 on the next frame, action age7; native erasure leaves mouth7/copy1.
Kirby retains full HP6 and both lives. A medium-range press at gap55 instead
pulls the target to gap11 and captures at ordinary action age0, still HP6.

| Installed a5 case | Lua SHA256 | Native receipt SHA256 |
|---|---|---|
| Close startup, launch window10..16 | `e0ed4c210cc26cba0f52f5d875f33546d2c28dded01d4585bc9c9fe03a443ff1` | `0de03877100997ecb5670313d0c162f279b1c5d99aeae0b7b2c97150de772e04` |
| Medium, launch window34..56 | `ba1eaaef3ea749b84ff574339d00e143a565094ad5c822a065fb6592a5f85cc8` | `bfdafc4118f364b12b37855610b75e01f4eb198be3d25d888b9eb29511b26152` |

The unchanged close-startup observer initially rejected the medium test
because it required an early age1..8 capture within two frames of fresh B.
The derivative retains that close assertion and uses the original ordinary
age0 assertion for the separate medium case. No ROM change was made.
Launch windows1..3 and8..10 never issued B before native body contact; the
observed HP loss therefore is not a failed active inhale. A11..14 launch on96
again produced real fresh B at gap13 and a successful startup capture.
These are timing-boundary observations, not a claim of exhaustive inhale
coverage in both directions, water, every enemy or every physical alignment.

## Earned green shell

The controller traverses real1-1, inhales the naturally streamed green Koopa
originally at1712/184, presses Down to obtain copy2, then fires from the ground
at a separately streamed Goomba. The shell advances exactly3 world pixels per
update. At the actual native contact, center1791/198 overlaps the Goomba's
native box1797..1807/198..204: center differenceY14 would fail the old
origin-radius12 test, but the actual rectangles overlap. The real defeat runs,
enemy state becomes$22, and the shell is consumed.

The96 shell-only run receipt is
`9dbdd05c2ff0ac1e9d695205771218beb92c229d548d40c65e106d30b6f5b850`.
It retains HP5 across this encounter; one earlier, unrelated hit cost one HP.
The controller and native boxed-trajectory assertions are retained in
`tools/playthroughs/kirby_current_green_stdout_1110.lua`.

## Full non-shortcut1-1

The continuation uses the real copied attack on following walkers, then flies
over the final stair obstruction using Kirby's implemented Up ability. Its
earlier discovery controller stopped requesting inflation above Y100 and
stalled at X2961/Y96. The derivative allows the real ability above Y32 instead;
it does not alter physics or grant position. Earlier failed controls remain
as separate sources. The clear-line combat observer also retains a separate
negative; no geometry/health/invulnerability patch was invented from it.

The passing run reaches the native flag at frame4935, X3161/Y112, and active
underground1-2 at frame6026, X40/Y48. It retains copy2, HP5 and both lives, with
no further injury after the green encounter. It is not a no-injury full route.

- Controller: `kirby_current_green_stdout_1110_v5.lua`, SHA256
  `730a40160788c5fa41b3bf8b931bfd14834bb463ae75a04b18f07f12e0d2ff20`.
- 96 receipt: `352f5013225ea4d4f1895ae9ff465efa5244d2aefe095fbc3b1d61b213d68eb0`.
- Installed a5 receipt: `f1db85c692a31fa708a7e590cff76f69fd47269b99960700914e36874df2b175`.

The a5 repeat has identical physical frames and gameplay results, with only
the bound ROM hash changing. This closes the current-ROM first-Goomba/green
ground-shell recheck and adds one actual full1-1 route. Red shell, the full
enemy-copy ensemble, all native health pickups, shortcuts, every enemy kill,
audio output and exhaustive graphical review are separate remaining checks.
