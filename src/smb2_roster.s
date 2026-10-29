; Private raw25 component. ROOT owns shared dispatcher/linker integration.
.include "smb2_roster_state.inc"
.pushseg
.segment "PARODIUS_BELLS"
 .res 9,$ff                     ; existing1591B owner endsA637, appendA640.
S2ComponentStart:
.assert S2ComponentStart=$a640,lderror,"SMB2 CORE actual append start"
.popseg
.include "smb2_roster_native.inc"
.include "smb2_roster_core.s"
.include "smb2_roster_terrain.s"
.include "smb2_roster_objects.s"
.include "smb2_roster_render.s"
.pushseg
.segment "PARODIUS_BELLS"
S2ComponentEnd:
.assert S2ComponentEnd<=$c000,lderror,"SMB2 CORE must fit approved118 tail"
.segment "CD_GFX"
 .res 234,$ff                   ; existing3350B owner endsCD16, appendCE00.
S2ArtAppend:
.assert S2ArtAppend=$ce00,lderror,"SMB2 ART actual append start"
.popseg
.include "smb2_roster_art.inc"
