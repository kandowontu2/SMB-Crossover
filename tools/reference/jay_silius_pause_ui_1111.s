; Fund the Jay callback from the exact existing native UI dispatcher and leaf.
.setcpu "6502"

.segment "UI_DISPATCH"
UiClassify:
 cpx #13
 bcc LowCharacter
 cpx #15
 beq LegacyCharacter
 cpx #18
 beq LegacyCharacter
 cpx #20
 bcs UpperCharacter
; Existing external raw41 routing still targets this exact entry.
GenericCharacter:
 pla
 tax
 pla
 plp
 jsr NativeInventoryUi
 php
 pha
 lda #<JayHot
 sta $016c
 lda #>JayHot
 sta $016d
 lda #$de
 jsr $015a
 pla
 plp
 rts
LowCharacter:
 cpx #9
 bne LegacyCharacter
 lda $5fe5
 and #$20
 bne UpperCharacter
LegacyCharacter:
 jmp LegacyUi
UpperCharacter:
 jmp $a7f4

.segment "UI_LEGACY"
LegacyUi:
 pla
 tax
 pla
 plp
 sta $016a
 lda #$61
 sta $016c
 lda #$b9
 sta $016d
 lda #$ce
 jmp $015a

.segment "UI_NATIVE"
NativeInventoryUi:
 lda $6f1d
 beq NormalInput
 lda #0
 sta $7d8d
 lda $6f1c
 cmp #4
 beq HurtHistory
 cmp #5
 beq HurtHistory
 cmp #10
 beq HurtHistory
 lda #0
 beq SaveHurtHistory
HurtHistory:
 lda $dc
SaveHurtHistory:
 sta $7d8c
 rts
NormalInput:
 ldx $dc
 txa
 eor $7d8c
 and $dc
 sta $7d8d
 stx $7d8c
 ldx $6002
 lda #0
 cpx #17
 beq NativeDone
 cmp $7d9e
 beq NativeDone
 sta $7d9e
 inc $0146
 inc $7d8e
NativeDone:
 lsr a
 rts

.segment "PAUSE_SUPPORT"
PauseMux:
 cpy #$d6
 beq PauseWeapons
 cpy #$e2
 bne MovePrivate
 jmp $b2c1
MovePrivate:
 ldx #1
 ldy #$ff
 sec
 ora #0
 jmp PrivateUpdate

; Called after native PauseRoutine on the real GameLoop UI path. Its private
; cache headers and raw16/variant20 identity have already passed JayHot.
PauseWeapons:
 lda $0771
 cmp #1
 bne PauseReturn
 lda Ready
 bne HasActor
 lda #0
 sta WeaponReady
 sec
 rts
HasActor:
 lda WeaponReady
 bne SampleSelect
 jsr ResetWeapons
SampleSelect:
 lda $dc
 and #$20
 tax
 eor PreviousSelect
 and $dc
 sta SelectEdge
 stx PreviousSelect
 lda $6f1d
 bne PauseReturn
 lda $0777
 lsr a
 bcc PauseReturn
 lda SelectEdge
 beq PauseReturn
 lda #0
 sta SelectLock
 lda PadNow
 pha
 lda #$20
 sta PadNow
 jsr PausedSelect
 pla
 sta PadNow
PauseReturn:
 sec
 rts
ResetWeapons:
 lda #63
 sta WeaponAmmo
 lda #2
 sta WeaponUnlocks
 lda #0
 sta WeaponSelection
 sta PreviousSelect
 sta SelectEdge
 lda #1
 sta WeaponReady
 rts
