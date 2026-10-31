# Playable unlock work — October 30

The current Downloads WIP is **64 enabled identities**, exact ROM `f56e55cd69b93821e66548848305cf9822e2ac0e8a25752d7192332cded53b78`. This corrects the black Peach reported by the user: the preceding `98048319` mistakenly used an enemy palette. Its earlier tests checked an incorrect expected row and therefore missed the bug. The genuine donor palette selector and actual OAM establish normal Peach's P2 row, `16 30 27`. Only3 ROM constants change; every label and allCHR remain identical. The new two bounded native checks pass for SMB1 Toad and Peach:180 controlled Main updates each, menu/lives palette and visible pixels, jump/landing, and360 real interrupt restores per run. Root reviewed all8 actual PPU PNGs. Both the previous64 and62 builds are backed up. Historical receipts remain unchanged; the [correction receipt](functional-roster-ready64-peach-fix-2026-10-30.json) supersedes their palette-authenticity claim.

The earlier exact `dfdb194a` build passed eight bounded native checks for SMB2 Mario/Luigi/Toad/Peach and FF Fighter/White Mage/Black Mage/Thief; root reviewed its36 PNGs. Those tests apply to that older hash. This is not a full1-1 or every-powerup qualification. Goku remains an Arthur Select alternate.

The user's current priority is playable unlocks, including laggy WIP characters, followed by polish. FF mandatory black shadows, White Mage's reported damage problem and the retained Fighter render-deadline failure remain open. The complete goal still includes every identity clearing1-1 and exercising every powerup; it has not been completed or paused.

## Next integrations

- **SMB1 Toad / Peach — installed:** `f56e55cd` retains the authentic supplied Benj Edwards sprites, native Mario movement and recovered Peach float vertical/ground/head-support behavior, with Peach's normal palette corrected. Select order is Mario, Luigi, Toad, Peach, Super Maaa, Kamikaze, Celeste. The original menu admission checked all83 profiles/664 Start/A cases. The correction checks48 Peach palette packets and288 unchanged foreign palette pairs; its entire ROM difference is the3 palette bytes. After the user closed Mesen, both new native checks passed. The special donor float enemy/ceiling/platform consumers and fire/star/area palette progression remain partial, and both HUDs still say MARIO.
- **Battletoads Rash / Zitz:** original PRG reproduced and source motion/basic-punch/art recovered. The actual buffered8KB loader, cookie checks, private36-service router and1380 real interrupt seams pass source checks. Source for the existing rare-service transport is being compacted to admit the new owner without moving public entries. Gameplay adapters and native play remain unfinished.
- **SMB1 / SMB3 Bowser:** original movement/fire/body source cores and authentic art are recovered. Split loader/router/preview workers fit within the explicitly granted1281B across six existing PRG islands; the first assembled implementation uses913B. Actual world, combat and gameplay ingress remain unfinished.
- **Contra Force Burns / Smith / Iron / Beans:** original full PRG reproduced byte-for-byte. Four distinct source walks, variable jumps and twelve original class/gear projectile allocations execute in CPU fixtures. All156 source body views now pack losslessly into9 pose-local CHR pages. Actual host movement, weapons, lifecycle and allocation work is ongoing.

The Battletoads, Bowser and Contra Force source milestones do not count as additional installed unlocks.

## Remaining scope

Existing pending identities include Karnov, Shinobi, Thomas, Metal Storm, both Bowsers, all six WWF wrestlers, Excitebike, Prince of Persia and all four Contra Force characters. Battletoads, SMB3 Toad/Peach from infidelity's supplied hack, Mega Giant Mario and **Getsu Fuma as a Simon alternate** are also required. Getsu Fuma was added in the user's latest goal edit; that addition has not been implemented yet.

Keep the explicit donor correction for Kamikaze: `Kamikaze_V1_SMB1_Hack.nes` supplies the current naked Mario graphics. Celeste Mario remains small. Credit Benj Edwards for the supplied SMB1 Toad/Peach source and infidelity for the SMB3 alternates.

## Storage and verification

The workspace cap remains70GB. New emulator runs reserve at most64 files /512MiB and produce only a handful of selected full-frame PNGs. No new videos or per-frame capture forests are being made. Source checkpoints and retained failures are pushed separately; frozen historical receipts are not rewritten to claim later validation.
