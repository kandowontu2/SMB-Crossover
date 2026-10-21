; Old Link normal death:9flash,4wait,16spin,9gray,2cross75ms events,
; then an independent650ms timer. Pit death retains the native separate path.
.pushseg
.segment "TITLE"
.proc EasyLinkDeathTick
  lda MmDeathAge
  bne Tick
  lda #0
  sta RgBillBurstDelay           ; phase
  sta RgBillCadence              ; per-phase eventcounter
  sta RgDeathLanded              ; completed spins
  lda #RG_POSE_DIEFLASH1
  sta RgBillBurst
  lda #1                        ; initiateNormalDeath fixes scaleX=1.
  sta PlayerFacingDir
Tick:
  inc MmDeathAge
  inc RgClock
  lda RgClock
  cmp #36
  bcc :+
    lda #0
    sta RgClock
  :
  lda RgBillBurstDelay
  cmp #5
  bne Event
  dec RgDeathDelay
  jne Done
  lda #6
  sta GameEngineSubroutine
  lda #0
  sta TimerControl
  rts
Event:
  lda RgClock
Modulo9:
  cmp #9
  bcc :+
    sbc #9
    bcs Modulo9
  :
  cmp #0
  beq Moderate
  cmp #5
  jne Done
Moderate:
  lda RgBillBurstDelay
  beq Flash
  cmp #1
  beq Wait
  cmp #2
  beq Spin
  cmp #3
  beq Gray
  ; Two checkFrame events advance cross1→cross2→hidden.
  inc RgBillCadence
  lda RgBillCadence
  cmp #2
  beq Hidden
  lda #RG_POSE_DIECROSS2
  bne Pose
Flash:
  lda #RG_POSE_DIEFLASH2
  cmp RgBillBurst
  bne :+
    lda #RG_POSE_DIEFLASH1
  :
  sta RgBillBurst
  inc RgBillCadence
  lda RgBillCadence
  cmp #9
  bne Done
  lda #RG_POSE_DIE1
  bne NextPhase
Wait:
  inc RgBillCadence
  lda RgBillCadence
  cmp #4
  bne Done
  lda #DeathMusic
  sta EventMusicQueue
  lda #RG_POSE_DIE1
  bne NextPhase
Spin:
  inc RgBillBurst
  lda RgBillBurst
  cmp #RG_POSE_DIE4+1
  bne Done
  lda #RG_POSE_DIE1
  sta RgBillBurst
  inc RgDeathLanded
  lda RgDeathLanded
  cmp #4
  bne Done
  inc RgBillBurstDelay
  rts
Gray:
  lda #RG_POSE_DIEGRAY
  sta RgBillBurst
  inc RgBillCadence
  lda RgBillCadence
  cmp #9
  bne Done
  lda #RG_POSE_DIECROSS1
NextPhase:
  sta RgBillBurst
  inc RgBillBurstDelay
  lda #0
  sta RgBillCadence
Done:
  rts
Hidden:
  lda #39
  sta RgDeathDelay
  inc RgBillBurstDelay
  lda #$ff
Pose:
  sta RgBillBurst
  rts
.endproc
.proc EasyLinkDeathVisual
  lda MmDeathAge
  bne :+
    lda #RG_POSE_DIEFLASH1
    sec
    rts
  :
  lda RgBillBurst
  cmp #$ff
  bne Visible
  lda #0
  sta ObjectMetasprite
  clc
  rts
Visible:
  sec
  rts
.endproc
.popseg
