; ExLoad and the37-row authenticated transport are resident in this same A bank.
; The two fragments fit only the existing Excitebike grants. No Sh span grows.
.export ExScene,ExSceneOwn,ExSceneEnd
.segment "EX_SCENE_GATE"
ExScene:
 php
 pha
 lda SelectedCharacter
 cmp #37
 beq ExSceneJumpOwn
 pla
 plp
 jmp ExPriorScene
ExSceneJumpOwn:
 jmp ExSceneOwn
.segment "EX_SCENE_OWN"
ExSceneOwn:
 jsr ExLoad
 bcc ExSceneReturn
 lda #<(ExServiceVeneers+108)
 sta FarcallJmpTarget_SMC+1
 lda #>(ExServiceVeneers+108)
 sta FarcallJmpTarget_SMC+2
 jsr ExServiceVeneers+108
ExSceneReturn:
 pla
 plp
 rts
ExSceneEnd:
