# Current menu corrections in progress

Base: `d0b445a71d6c539804d7c559fafc2c328ebf97ab4e35e8f3273f94ff8a25d01d`.
DELIVERED: Downloads nightly matches candidate22d099 below, no backup.
Actual Downloads Bob launch passes; pre/post automatic-patch guards pass.
Latest release Current has exactly one IPS, SHA256
`185934ef14df893744e374bc7ead90db1471307a3d7c2cd0917741217a6bccf9`,
verified against GitHub asset digest. Patch reconstructs exact installed ROM.

Current root candidate: `build/menu-family-root-candidate-1102-v1/mr-gimmick-family.nes`,
SHA256 `22d09909bf952ef007d1582589dc869073262784bf38b92d2c7b206ce3c45b19`.
All32-slot/all-alternate native browse passes5180frames/125observations,
fourPNG screenshots, zero active-display PPUDATA writes and zero late enables.
Bub/Rash screenshots viewed: right-facing Bub and populated Battletoads icon.
Separate native Bub and Bob normal-A launches pass actual owner/Fresh checks.
Mr. Gimmick native launch passes (session76580 terminal exit0).
Actual Downloads test18811 terminal exit0. Published receipt:
`build/menu-family-delivery-1102-v1/published-receipt.json`.
Root producer snapshots helper v18 and changes its overbroad simultaneous-key
test to ordinary Start/A: Select+Start on Excitebike chooses locked Prince,
so that old expectation was invalid. No gameplay patch was made for that test.

User requirements: Mr. Gimmick replaces the Gimmick label; Bub and Bob are his
Select alternates, with no standalone Bub/Bob position. Bub and Bob face right
in the roster/selected preview; check gameplay direction as well. Remove stale
coming-soon diamonds from playable characters. Add Battletoads roster art.

Actual compiled menu inventory finds 93 distinct names, 92 accepting Start/A.
Prince of Persia remains blocked. Nine playable names retain tile63: Shinobi,
Thomas, Metal Storm, Ted DiBiase, Bam Bam Bigelow, Honky Tonk Man, Randy Savage,
Andre the Giant, and Excitebike. The data-only patch clears precisely those
nine bytes; rerun actual name/Start/A calls pass, including Prince remaining
marked and blocked. Receipt: `build/playable-marker-cleanup-1102-v1/patches.json`.

Battletoads art was reconstructed from actual current cold-menu OAM and CHR
page915. Its occupied body is24x33 pixels; fit to32px height for the roster.
Slot23 is blank at nametable column25,row12, with room for3x4 tiles. Fourteen
tiles are available when removing the standalone Bub icon and protecting all
other nametable references. Source pixels and viewed image are under
`build/battletoads-silhouette-1102-v1`.

The Sol6.1 xhigh Bub helper owns Mr. Gimmick family selection, facing, menu
stream integration and candidate source proof. Root owns native testing and
delivery. Menu browse and allthree family launches are now qualified and
delivered. Runtime facing review and broader fullstage qualification remain open.

Other queue results retained: Goku full1-1 ended at the240second emulator
timeout, without a completion receipt (10345 input polls); this is not a pass.
Bub wide-pit controller crossed four opening pipes and the first two gaps,
including1376..1424, but later failed with source injury/death. Neither failure
justifies claiming full1-1 completion. No helper was added in these runs.
