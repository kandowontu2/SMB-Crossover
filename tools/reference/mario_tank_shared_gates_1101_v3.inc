; Measured source-loan proposal only. No menu admission or carrier allocation.
; Every shared boundary is ROM resident. Exact identity and a complete header
; must pass before even one conditional-RAM opcode may execute.
; Predicate consumes A/N/Z/C, retains X/Y and leaves both C map/shadow restored.
.segment "MT_READY"
MtRomReadyV3:
 lda SelectedCharacter
 bne MtReadyNoV3
 lda MarioVariant
 cmp #7
 bne MtReadyNoV3
 txa
 pha
 lda CurrentBankC
 pha
 lda #2
 sta CurrentBankC
 sta $5116
 ldx #15
MtReadyByteV3:
 lda $dfe0,x
 cmp MtSharedCookieV3,x
 bne MtReadyBadV3
 dex
 bpl MtReadyByteV3
 sec
 bcs MtReadyRestoreV3
MtReadyBadV3:
 clc
MtReadyRestoreV3:
 pla
 sta CurrentBankC
 sta $5116
 pla
 tax
 rts
MtReadyNoV3:
 clc
 rts
MtSharedCookieV3:
 .byte MT_COOKIE_BYTES
MtRomReadyEndV3:

; Incoming A/P retained across predicate. X/Y survive predicate + real
; FarCallCommon. Native and worker results are returned unchanged. No scratch,
; no new SMC convention, no unchecked conditional RAM continuation.
.macro MtSharedGateV3 Entry,SegName,Worker,Native,NativeBank
 .local Legacy
.segment SegName
Entry:
 php
 pha
 MtGateRawFar MtRomReadyV3,MT_READY_BANK
 bcc Legacy
 pla
 plp
 MtGateRawFar Worker,2
 rts
Legacy:
 pla
 plp
 MtGateRawFar Native,NativeBank
 rts
.endmacro

MtSharedGateV3 MtRomMovementAllV3,"MT_G31",MtHostMovement,BmMarioMovement,BmMarioMovement_BANK
MtSharedGateV3 MtRomContactV3,"MT_G31",MtHostContact,S2BoundaryImmunity,S2BoundaryImmunity_BANK
MtSharedGateV3 MtRomSideV3,"MT_G21",MtTerrainSideProbe,MtSideLegacyCloneV3,MT_SIDE_BANK
MtSharedGateV3 MtRomInjuryV3,"MT_G37",MtHostInjury,CmHostMarioInjury,CmHostMarioInjury_BANK
MtSharedGateV3 MtRomBeginPowerupV3,"MT_G25",MtHostBeginPowerup,MarioSourceBeginPowerup,MarioSourceBeginPowerup_BANK
MtSharedGateV3 MtRomGrowthV3,"MT_G58",MtHostGrowthUpdate,MarioSourcePowerupUpdate,MarioSourcePowerupUpdate_BANK
MtSharedGateV3 MtRomHeadV3,"MT_G12",MtTerrainHeadProbe,MaaHead,MaaHead_BANK
.segment "MT_G21"
MtSideLegacyCloneV3:
 ; Authenticated original27B MmNativeSideShortcut, including its native
 ; absolute exits. Relative branches remain within this relocated fragment.
 .byte MT_SIDE_BYTES
MtSideLegacyCloneEndV3:
