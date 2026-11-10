.setcpu "6502"

EnemyFlag = $10
ProxyGetsu = $bfe4
ProxyLink = $bff2

.segment "ADMISSION"
.export GfPostAdmission
GfPostAdmission:
    cmp #4
    beq Link
    jsr GfNativeActors
    beq Empty
    jmp ProxyGetsu
Link:
    jmp ProxyLink
Empty:
    ldx #$ff                    ; Matches the loaded zero-contact return.
    clc
    rts

.segment "FLAGS"
.export GfNativeActors
GfNativeActors:
    lda EnemyFlag
    ora EnemyFlag+1
    ora EnemyFlag+2
    ora EnemyFlag+3
    ora EnemyFlag+4
    ora EnemyFlag+5
    rts
