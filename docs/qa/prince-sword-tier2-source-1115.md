# Prince earned-sword persistence, current7a80

Source-only implementation of the reproduced `effff079` upgrade loss. The
current full1-1 native53c1/source clear remains frozen. This candidate has no
native, delivery or full-route qualification yet.

The proposed policy uses existing native PlayerStatus075B: Mushroom changes
0→1 and preserves1/2; Flower publishes2 and private sheathedSword1; HostInit
restores Sword1 only for native2. Death, Continue, menu entry and new game
retain their existing power-loss policy. No shared loader, new status storage,
SourceMask, physics, art or controls changes.

Actual current executable contracts:

| Path | Evidence and relevant behavior |
| --- | --- |
| Weapon dispatch | NrObjectWeaponTail/ProcFireball_Bubble tier1/2 units: no native fireball, counter, shot pose or sound. Prince dispatch bypasses Mario fireballs. |
| Palette | GetPlayerColors/NrColors have no reached075B read; complete VRAM buffers and CHR latches match1/2. SetupIntermediate preserves2 and identical visual output. |
| Damage | NrInjuryStatus uses private HP; ForceInjury has identical private-HP behavior and does not read075B. This is an admitted injury primitive, not a natural contact or one-hit-damage claim. |
| Reveal/inventory | PwrUpJmp current CMP2/LSR normalization reveals Flower for both1/2. InventorySupported rejects Prince; generic RemainingPower returns the tier but does not authorize another character's weapon. |
| Area | InitializeArea clears only through074B; native075B survives. The frozen genuine-earned public reload diagnostic independently proves that retention. |
| Death/new game | KillPlayer and Continue explicitly clear075B. InitializeGame's InitializeMemory limit076F includes075B. |
| Menu/swap | Actual compiled screen entry clears075B2→0; Select toggling inside an already-open menu preserves it. TransposePlayers copies075F..0765/0766..076C, excluding075B. Source UI lacks real vblank. |

The read-only inventory receipt is
`c282707ad1de1882c383cbaa45a06fcc80e6ee14b3dde488f7ee7b179a330e63`.
Its134 raw operand candidates are explicitly not134 executable consumers.
The28 actual existing-code units receipt is
`45d965a0de5eb0dd822752696c07cca327ac1b75ce1e38b5b4b96bb03c04465d`.
Those units declare diagnostic tier/button inputs; they do not prove earned2.

Exact source-only grant:
`allocations/prince-sword-tier2-source-1115.json`, SHA
`c787391be64b6118f6d8183f405fd114ba82fd397adf75320be326a33af6bd51`.
Frozen plan4d515e09 receipt2ae5e407 has these158 owned/79 changed bytes:

| Decoded extent | Live location | Preimage SHA256 | Proposed SHA256 |
| --- | --- | --- | --- |
| stream2[0,80) | C0B0..C100 | c988607848391b5f80cbef683e0875d7485178a905ff8b4503fc7d33641f2c01 | 33f0263bca451128f3ac80aafd5ee055e8bbdde2c4659f05c88ecb67c6cf24fd |
| stream2[1452,1529) | dedicated C7B3..C800 copy | 21cf8aafac46a1e7b430f10ec072649d8e8116121e67fbbc768b98a8e8b600e5 | 481bf9d0b585fecec76026ca616fe059f4e8f1cf9895ed7c8f5a373eed530647 |
| stream1[6012,6013) | DF7C JMP low operand | EA | EB |

Constructor adds7 instructions bytes within its8-byte tail, retaining all
original stores. LDA075B/LSRA/STAC6EE maps0/1→0 and2→1. Only real public
constructor caller is NativeInit's JSR C0B0; it immediately overwritesA/N/Z
with LDA C084. X/Y and final SEC remain. The other C0B0 word occurrence is
the cold copy's STA C0B0,Y. Correction to earlier diagnosis prose: C6D1 is
the donor bank selector, not an established max-HP field; its store is exact.

Pickup saves3 bytes by using the Type LSR carry through mature-state LDA/BPL.
Types>=2 retain native dispatch;0/1 retain mature gating. Incoming A/flags
are overwritten inside NativeCall before dispatch. Flower costs4 additional
bytes; preserving native2 in the Mushroom helper costs2. Result75 meaningful
bytes plus2 tail bytes. NativeDeathUpdate movesC7EA→C7EB, so its actual
published Prince death JMP low operand changesEA→EB. Other raw C7xx words
outside these live callers lie in the frozen3174-byte pose-data envelope.

Detached1728 pickup and9 constructor suffix CPU cases pass, receipt
`e5e1d7a383ed16ea1f7c9792152370ff6a81c8ec50e49c4ba0c160113c89ad65`.
They use declared service oracles, preserve live caller stack/X/Y/C, and are
not gameplay. Initial fixture corrections excluded retired JSR return bytes,
gave the native-call oracle its actual SEC result, used DisableScreenFlag and
cleared Mirror_PPUMASK before compiled menu entry. No game defect inferred.

Strict composer `compose_prince_sword_tier2_1115.proposal(parent7a80)` yields
`5cfa2a0f1e98fc74d616a922f0f7273396dc98ff20c5afe04441ca04e7f914df`.
Portable inverse reconstructs exact7a80 using inline158-byte preimages,
without reading Downloads. Physical changes1199 are confined to the existing
45 carrier pages and cookie535471..535487. Packed6469/5995/1263, headerword10
1259→1263 only, cookiea726028d9d5e0c8ab00f6ca1af5c7599, spare577 bytes.
All other decoded/physical bytes, graphics, loader, art and tables are exact.

Factory `replay_prince_sword_tier2_full_1115.controller(raw)`, variant3, SHA
`982fbb9103c12abd939f72348d75cf2434ba45792cf067ab73b40e0a30ed9c02`,
compiles Lua
`df467cb383f0c180d304350377a0f7d3201221d479820c730de525db289c7f18`.
It retains frozen53c1 navigation/combat, updates exact ROM/cookie bindings,
checks both cookies+4185 immutable bytes at firstBBC1, and asserts actual
1-2 native075B2/privateSword1 after25 living grounded completed Main returns.
The first metadata attempt's120-second reconstruction bound expired without
outputs; the deliberate300-second successor compiled successfully.

Source earned/full/paired-ISR job81116 is pending. It uses actual encoded
cold bytes and explicit public component clones of genuinely earned Flower;
no actor, health, position or upgrade outcome seeds. Equal-facing F090 exit,
all abilities/items/audio and idle lag remain separate open gates. No Mesen,
ROM files, patches, backups, releases or generated build files were created.
