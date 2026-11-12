; Caller admits overlap, robot age >=12, and player vulnerability.
; A is the original collision flag, X the native enemy slot. Enemy damage
; precedes robot damage, including when that contact destroys the robot.
.setcpu "6502"
.segment "THROW_CONTACT"
SteveThrowContactDamage:
    cmp #0
    beq ThrowContactReturn
    bmi ThrowContactReturn
    pha
    and #$20
    bne ThrowContactRobotOnly
    jsr SteveThrowDamageEnemy
ThrowContactRobotOnly:
    pla
    jmp SteveRobotDamage
ThrowContactReturn:
    rts
