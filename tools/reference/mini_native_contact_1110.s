; Route only Mini's ordinary native contact directly. SMB2 and Bub/Bob
; retain their exact authenticated services, and Kirby keeps its old tail.
.setcpu "6502"
.export ContactGate, MiniContact, MiniContactEnd

Selected = $6002
SavedA = $016a
Target = $016c
NextBank = $0162
AreaType = $0753
GuestBodyStompAllowed = $7fe3
GuestBodyNoStomp = $6f18
ObjectOffset = $0d
LegacyBody = $abdc
FarJump = $bf00

.segment "GATE"
ContactGate:
    lda Selected
    eor #25
    beq @smb2
    eor #25^39
    beq @bubble
    jmp MiniContact
    .res 19-(*-ContactGate),$ea
@smb2:
    lda #$15
    sta Target
    lda #$bb
    sta Target+1
    lda #$f6
    .assert *=$bf22,lderror,"Retain the shared farcall predecessor"
    bne *+(FarJump-$bf22)
    nop
@bubble:
    lda #$29
    sta Target
    lda #$b0
    sta Target+1
    lda #$c1
    .assert *=$bf31,lderror,"Retain the shared farcall predecessor"
    bne *+(FarJump-$bf31)
    nop
    .assert *-ContactGate=49,error,"Keep the next native pointer entry fixed"

.segment "CONTACT"
MiniContact:
    eor #39^41
    beq @ordinary_mini
    lda SavedA                 ; Real outer FarCall had set N/Z from this A.
    jmp LegacyBody
@ordinary_mini:
    lda AreaType
    sta GuestBodyStompAllowed
    lda #1                     ; Retain the native Hard-mode body policy.
    sta GuestBodyNoStomp
    lda #$a1
    sta Target
    lda #$b5
    sta Target+1
    lda #$8a
    sta NextBank
    lda ObjectOffset           ; Old callee returned its preserved slot.
    clc
    rts                        ; The real outer FarCall publishes return A.
MiniContactEnd:
    .res 41-(*-MiniContact),$ff
