# Current menu corrections in progress

Base: `d0b445a71d6c539804d7c559fafc2c328ebf97ab4e35e8f3273f94ff8a25d01d`.
The installed Downloads nightly has not changed for this work yet.

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
delivery. No new menu candidate has been qualified or delivered yet.

Other queue results retained: Goku full1-1 ended at the240second emulator
timeout, without a completion receipt (10345 input polls); this is not a pass.
Bub wide-pit controller crossed four opening pipes and the first two gaps,
including1376..1424, but later failed with source injury/death. Neither failure
justifies claiming full1-1 completion. No helper was added in these runs.
