; Original conservative Sonic contact adapter. Existing native overlap owns
; eligibility; this leaf only handles live canonical Koopa/Goomba actors.
.setcpu "6502"
SelectedCharacter = $6002
GuestBodyNoStomp = $6f18
EnemyFlag = $10
EnemyID = $17
EnemyState = $1f
PlayerYSpeed = $8e
ObjectOffset = $0d
Flags = $c030
Vx = $c020
Vy = $c060
JumpLatch = $c058
Charge = $c098
Ready = $c119
Hurt = $c34f

.segment "INGRESS"
; This replaces the existing64-byte Kirby/legacy gate. Every real incoming
; FarCall, and Mini's LDA SavedA/JMP tail, already supplies identical SavedA.
; Omitting its redundant store and joining Kirby's carry-preserving epilogue
; funds raw43's typed body ingress. The existing Co saved frame stays exact.
SonicContactIngress:
 php
 pha
 lda SelectedCharacter
 cmp #13
 beq KirbyBody
 cmp #43
 beq SonicBody
 pla
 plp
 lda #$a1
 sta $016c
 lda #$b5
 sta $016d
 lda #$8a
 jmp $015a
KirbyBody:
 pla
 plp
 txa
 pha
 tya
 pha
 lda $0753
 sta $7fe3
 lda $7fe1
 sta GuestBodyNoStomp
 jsr $aa27
 ; PLA/TAY/PLA/TAX leave the native helper's C intact, exactly as the
 ; former duplicated SEC/CLC epilogues did.
 pla
 tay
 pla
 tax
 rts
SonicBody:
 pla
 plp
 lda #$ad
 ; Shared existing native stub: STA TargetLow, high=$B0, bank=$C1,
 ; genuine FarCall. B0AD is the authenticated public NrBody row11.
 jmp RestoreContactSlot

.segment "BODY_GATE"
; The original classifiers and both typed/native target setters remain.
; Five source NOPs plus the SMB2 setter's trailing NOP fund a real wrapper.
; Generic auth rejection returns X=0; native collision still owns its real
; ObjectOffset, so restore it before either handled or injury continuation.
NativeBodyGate:
 lda SelectedCharacter
 eor #25
 beq Smb2Body
 eor #62
 beq BubbleBody
 jmp $b157
RestoreContactSlot:
 jsr $bf27
 ldx ObjectOffset
 rts
Smb2Body:
 lda #$15
 sta $016c
 lda #$bb
 sta $016d
 lda #$f6
 bne $bf00
BubbleBody:
 lda #$29
 sta $016c
 lda #$b0
 sta $016d
 lda #$c1
 bne $bf00
 nop

.segment "BODY"
SonicOriginalBody:
 lda $0753
 sta $7fe3
 lda #1
 sta GuestBodyNoStomp
 lda Ready
 beq OrdinaryContact
 lda Charge
 bne OrdinaryContact
 lda Hurt
 and #$40
 bne OrdinaryContact
 lda Flags
 and #5
 beq OrdinaryContact
 lda Flags
 bpl AirAttack
 lda Vx
 ora Vx+1
 ora Vx+2
 beq OrdinaryContact
AirAttack:
 cpx #6
 bcs OrdinaryContact
 lda EnemyFlag,x
 beq OrdinaryContact
 bmi OrdinaryContact
 lda EnemyState,x
 cmp #2
 bcs OrdinaryContact
 lda EnemyID,x
 cmp #2
 bcc Defeat
 cmp #6
 bne OrdinaryContact
Defeat:
 txa
 pha
 tya
 pha
 ; Native terminal defeat awards the native score/popup/sound. The actor
 ; allowlist excludes Piranha and unsupported inventory-drop families.
 lda EnemyID,x
 jsr $9b04
 pla
 tay
 pla
 tax
 lda Flags
 bmi ContactHandled
 lda Vy+2
 bmi ContactHandled
 lda #0
 sta Vy
 sta JumpLatch
 lda #$fc
 sta Vy+1
 sta PlayerYSpeed
 lda #$ff
 sta Vy+2
ContactHandled:
 sec
 rts
OrdinaryContact:
 clc
 rts
