; ROM29 owns this wrapper; A3 cache code cannot load or replace itself.
.export KrSceneInit
KrSceneInit:
 farcall ThSceneInit
 php
 pha
 txa
 pha
 tya
 pha
 jsr KrSelected
 bcc KrSceneDone
 jsr KrLoad
 bcc KrSceneDone
 lda #<(KrServiceVeneers+45)
 sta FarcallJmpTarget_SMC+1
 lda #>(KrServiceVeneers+45)
 sta FarcallJmpTarget_SMC+2
 jsr KrServiceVeneers+45    ; same-ROM-bank genuine guarded service15
KrSceneDone:
 pla
 tay
 pla
 tax
 pla
 plp
 rts

