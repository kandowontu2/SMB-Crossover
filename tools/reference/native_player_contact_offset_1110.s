.setcpu "6502"

SelectedCharacter = $6002
FrameCounter = $0e
Engine = $0f
EnemyState = $1f
MaskedOffscreen = $05a8
ObjectOffset = $0d
EnemyContact = $063d
CheckPlayerVertical = $9b3a
PlayerCollisionCore = $9512

.segment "CONTACT"
.export PlayerEnemyCollision, InlineOffset, Rejected
PlayerEnemyCollision:
    ; Luigi alone keeps the native even/odd contact poll.
    lda SelectedCharacter
    cmp #8
    bne Vertical
    lda FrameCounter
    lsr
    bcs Rejected
Vertical:
    jsr CheckPlayerVertical
    bcs Rejected
    lda MaskedOffscreen,x
    bne Rejected
    lda EnemyState,x
    and #$20
    ora Engine
    cmp #8
    bne Rejected
InlineOffset:
    ; Both actual object-bank ingresses supply X=ObjectOffset, including
    ; Bowser's duplicate index. Retain the full byte arithmetic and ADC V.
    ; PlayerCollisionCore overwrites A/N/Z/C before using any of them.
    txa
    asl
    asl
    clc
    adc #4
    tay
    jsr PlayerCollisionCore
    ldx ObjectOffset
    bcs CheckForPower
    lda EnemyContact,x
    and #$fe
    sta EnemyContact,x
Rejected:
    rts
CheckForPower:
    .assert *-PlayerEnemyCollision=$37,error,"Retain the power-up contact entry"
