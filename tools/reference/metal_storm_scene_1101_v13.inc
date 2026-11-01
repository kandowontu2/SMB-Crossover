; Foreground scene ingress in the unused tail of Metal's granted bank21.
; Preserve the complete existing scene chain, including Mario the Tank.
.export Ms13Scene
.segment "MS11_CHECK"
Ms13Scene:
 Ms8Far KrSceneInit,29
 php
 pha
 lda SelectedCharacter
 cmp #35
 bne Ms13SceneDone
 Ms8Far Ms8Load,116
Ms13SceneDone:
 pla
 plp
 rts
Ms13SceneEnd:
.assert Ms13SceneEnd-Ms8Check<=118,lderror,"Metal bank21 scene/check lease"

; ROM-only state reset after a successful cold or authenticated warm load.
; No source RAM opcode executes here. The constructor runs on next movement.
.export Ms13Fresh
.segment "MS11_COPY"
Ms13Fresh:
 lda CurrentBankC
 pha
 lda #2
 sta CurrentBankC
 sta $5116
 lda #0
 sta $c800
 pla
 sta CurrentBankC
 sta $5116
 sec
 rts
Ms13FreshEnd:
.assert Ms13FreshEnd-Ms8Copy<=122,lderror,"Metal bank36 copy/reset lease"
