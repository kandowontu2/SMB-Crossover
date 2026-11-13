# Prince sword controls and native Goomba import

Parent: `3b7990bc59b490a1c5e488133a7c65d05526944d63b7e987f0b3f44df733343d`.
Sword derivative: `a0dc025be05d1a9e697bb47f1affaea9d33f70be3d7fbee240b520e433f12327`.
Affected identity: Prince of Persia/raw38. No helper platform or new actor was
added to stage data. Root owns physical Mesen, installation and publication.
All helper verification uses bounded CPU processes and writes zero outputs.

## Required original controls

The actual mature native flower collector grants original sword inventory1
and action91. A placed-actor fixture executes PowerUpObjHandler,
HandlePowerUpCollision and HuPickup; it does not write sword mode2 or call the
private collector as a substitute for native overlap/maturity handling.
The fixture starts with native PlayerStatus1, places one mature kind1 flower
in slot5 overlapping the player, and observes that actor erased.

Original sword drawing is automatic when a nearby, opposing eligible enemy is
imported. Original5:8999, current RAM2:DC15, increments inventory1→2 and selects
draw action55. A selects attack58; original strike requires pose154. B from
the original stance selects parry62. After the defeat, the observed original
sequence includes sheath93, inventory1 and standing action0. This verifies the
parry action/animation, not a successful block of an incoming enemy attack.

The original reach threshold is asymmetric: approach within38 source pixels
facing right or32 facing left. The controller first waits through draw55,
presses and releases B, lets parry finish, walks forward until within reach,
then presses A. Native ProcFireball_Bubble is the actual deferred row34 ingress
after movement; MegaManFullShotBank is not that ingress.

## Concrete port defect and repair

The current Prince proxy's load at DDEB reads native Enemy_BoundBoxCtrl and
then compares only with3. Ordinary native Goombas use9. A Goomba therefore
never became an original combat opponent, so flower-earned inventory1 could
not trigger automatic drawing against it. The unchanged parent reproduces
this failure; A remains an unarmed hop and inventory stays1.

The repair replaces that three-byte LDA with JSR to a leaf that reads the
same field and normalizes only value9→3 in A. The existing CMP3, native kind
cutoff7, active flag, defeated-state, vertical-page and distance checks remain
in charge. Native Enemy_BoundBoxCtrl itself stays9. All other field values
retain their old admission result, including ordinary box3.

The13-byte leaf occupies RAM2 D466..D46E and D751..D756. Exact sharing of
identical pose-packet bytes frees the first8 bytes; all239 decoded geometry
records remain identical. Removing the five existing NOPs from the moving
support predicate frees the other5 bytes. Its relative branches are relocated
and its semantics stay identical. There are no external literal JSR/JMP
entries into the shifted tail. The support publication observer moves from
**D74B to D746**; root's replay has been updated accordingly.

The original codec and runtime/state streams are unchanged. Streams are
6428/5930/1231 bytes, leaving715 bytes in the existing carrier. No new RAM
banks or CHR pages are claimed. Cookie: `a726024146cc2049b14dcc581a3340fe`.
The source stores only the original478-byte pose index and133-byte support
preimage needed for exact reversal. `transform(raw)` returns image/chunks/layout;
`reverse(raw)` returns the exact3b7990 parent bytes. No backup ROM is retained.

## Passed CPU gates

| Gate | Scope and result | Receipt SHA256 |
|---|---|---|
| Original-controller combat | Four episodes: native Koopa ID0/box3 and Goomba ID6/box9, both facings. Each uses the real placed mature-flower collector, observed0→1→2→1 sword writes, draw55, completed parry62, attack58/pose154, exactly one actual FE:9AF8 native defeat, sheath93 and idle0. Final native enemy state34, HP5/two lives. No drawn-mode or hit/death outcome seed; enemy placement and lack of enemy AI are explicit. | `711b4a4c3620c2fd2f4de43177335a5c2da4bc0f794ea22d48732e51681eea8e` |
| Proxy admission | 2311 actual calls; all256 native kind IDs, all256 box controls, both facings, seven active/state/page/distance negatives. Only3/9 admitted for kind<7; native box fields preserved. | `5cee02a11de8ece38cedc318495f2e61f810ef645ff0b319fce5ab1a8319cf66` |
| Support parity | 1024 actual old/new decisions, all256 tiles and original idle/walk/careful-step actions. Returned AXYP, source state, scratch and query output match. | `d01cd012d9d6e95e3cb4c918cf68804c26e600ba2d22b0bba06fd4beab3f669e` |
| Renderer parity | All408 original frame/facing poses and2578 parts execute actual project/export/draw. OAM, CHR maps, registers, scratch and emitted source packets match. Two cold-derived models are reused; each pose's input/OAM is reset and preceding equal render state retained. | `7414cf34d2ad08dcea8c8dec69e3c9d18cdb923526a2bd41cdd47306d2d37e87` |
| IRQ and complete cold |87 IRQ+87 lag-NMI proxy cuts/minimumSP196;53+53 compact-support cuts/minimumSP197. Complete current resident/PPU staging, reread, three decoders, finalizer, constructor, exact live runtime/metadata, both headers and authentication pass. All6428/5930/1231 input bytes consumed; metadata/state unread margins407/131. Exact reverse passes. | `e423126f5d88bd00971003a5076f96e6a69aac09ebc0feb4b9bb7bd0ed85a692` |

Reproduce each mode through the bounded runner, with an unused output root,
`--max-files 1 --timeout 120 -- python -B` and the appropriate checker:

```text
tools/audit/check_prince_sword_controls_1112.py --candidate
tools/audit/check_prince_sword_box_1112.py --matrix
tools/audit/check_prince_sword_box_1112.py --support
tools/audit/check_prince_sword_box_1112.py --render
tools/audit/check_prince_sword_box_1112.py --interrupts --cold
```

The checker reconstructs its exact frozen parent in memory when Downloads is
the known combined c5ce8c delivery, using the reversible root composition.
Intermediate harness failures were a pose keyword passed to the wrong fixture,
software B-bit normalization, a missing layout field, and a historical renderer
fixture exceeding its120-second bound. They produced no accepted receipts or
generated files; the passed modes above supersede those attempts. The ordinary
C280 loader retains the earlier193 forced-blank cold cuts; those unchanged cold
instruction cuts are not recounted as new sword coverage.

## Root physical evidence and remaining scope

Root reports the sword-only a0dc025 candidate naturally collects the first
mushroom, ending frame2160/X417/Y176 with HP5/two lives; receipt
`50413ea06514f78e09061467af402e33273140882822120995cfeb72bdb31b4c`.
The combined sword/reach/menu c5ce8c candidate also passes controller-only1-1
into active1-2 at frame16379 with two lives; receipt
`60479ff4e2bda39d132807db13310ba272cf68d5eebbb6f98a21ddd75d21491f`.
These are root-supplied observations. Physical placed-flower combat, natural
flower acquisition, Downloads revalidation and release publication are separate
root gates and are not claimed by this helper's CPU fixtures.

For a minimal disclosed physical combat scene: after Prince becomes active,
place one mature native kind1 flower overlapping him, wait through action91 to
idle0, then place a native Goomba ID6/box9 approximately64 pixels ahead facing
him. Neutral allows automatic draw; B in stance171 parries; forward within the
appropriate reach threshold and A exercises attack and the actual native kill.
Never seed source inventory or drawn mode.

## Safe descent investigation

Original5:8574..8589 reduces HP and writes damage clocks without writing sword
inventory C6EE. The native PlayerStatus mushroom/flower progression byte is a
separate adaptation; source fall damage is not evidence that a flower-earned
sword should be removed. Root's third-pipe landing trace reaches the original
HP debit with fall counter3, distinguishing it from the separate later Goomba
contact that drains HP through the defender.

Action68 is the original reverse-climb descent. Down alone from standing
pose15 reaches D838→D83C; D85E additionally requires C04FE=0. F65B then probes
behind Prince: right-facing actorX−44, left-facing actorX+0, using the original
coarse source column. F688 requires empty material0; any floor1 or wall20 exits
before alignment and action68. At native X752/right-facing actor760 this probes
rawX716/coarse704. This source audit identifies the actual position/material
gate; it does not establish a successful controller-only descent from that cap.
Root's Down and Down+B observations only crouch there. No guessed input sequence
or fall-physics change is presented as a verified solution.
