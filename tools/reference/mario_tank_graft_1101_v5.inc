; ROM-only continuations. Shared entry never jumps to unloaded RAM2.
.segment "MT_CONTACT"
MtFreshV5:
 MtV4Far ThSceneInit,ThSceneInit_BANK
 MtV4Far MtColdLoadV4,159
 rts
MtFreshEndV5:
.segment "MT_MENU_RESOLVE"
MtReservationV5:
 php
 lda SelectedCharacter
 bne MtReservationLegacyV5
 lda MarioVariant
 cmp #7
 bne MtReservationLegacyV5
 lda PlayerStatus
 cmp #2
 bne MtReservationLegacyV5
 plp
 lda #24
 rts
MtReservationLegacyV5:
 plp
 MtV4FarTail MaaReservation,MaaReservation_BANK
MtReservationEndV5:
.segment "MT_DRAW_GATE"
MtDrawAllV5:
 MtV4Far HuDrawAll,HuDrawAll_BANK
 php
 pha
 MtV4Far MtRomReadyV3,MT_READY_BANK
 bcc MtDrawDoneV5
 pla
 plp
 MtV4Far MtArtPostV5,2
 rts
MtDrawDoneV5:
 pla
 plp
 rts
MtDrawAllEndV5:
.segment "MT_NAMES"
MtMarioNamesV5:
 .byte "     TOAD       ","     PEACH      "," MARIO THE TANK "
MtMarioNamesEndV5:
