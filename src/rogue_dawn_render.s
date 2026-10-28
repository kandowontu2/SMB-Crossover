; Rogue Dawn1.21 original-instruction-derived poses, not stock Samus graphics.
; Standalone component only: root owns dispatch, world/collision, palette mixer.
; Include AFTER frozen rogue_dawn.s/weapons and generated rogue_dawn_art.inc.
; Requires verified RD_FIRST_CHR from integration;680 is the current reservation.
; No new active/persistent RAM. R0/R1,SmTemp are transient render outputs/scratch.
.ifndef RD_FIRST_CHR
 .error "Root must supply verified Rogue Dawn physical CHR first page"
.endif
.assert <RD_FIRST_CHR <= 240,error,"Rogue CHR reservation must not cross256-page boundary"
.export RdRenderPlayer,RdRenderWeapon,RdRenderGraphicsBank,RdRenderPublishChr
.export RdRenderPalettePointer,RdAdvancePlayerFrame
.pushseg
.segment "ROGUE_DAWN_CORE"

.proc RdRenderGraphicsBank
 BankPRGC #<.bank(RdArtStart)
 rts
.endproc

; Complete nativeDC8F player animation timing. ART must already be mapped.
; A=native hold duration (stand4/run5); source player X=0. No render-side tick.
; Source CD6D->DB96->DC8F owns this advance, never call again for weapons.
.proc RdAdvancePlayerFrame
 ldx #0
 ldy RdAnimDelay
 beq Advance
 dec RdAnimDelay
 bne Done
Advance:
 sta RdAnimDelay
 ldy RdAnimIndex
Read:
 lda RdArtAnimation,y
 cmp #$ff
 beq Loop
 sta RdAnimFrame
 iny
 tya
 sta RdAnimIndex
Done:rts
Loop:
 ldy RdAnimReset
 jmp Read
.endproc

; Consume the ALREADY advanced native player frame and0right/1left RdFacing.
; Output genuine SmPosePtr/SmChrBank/ObjectMetasprite. Source radius updates
; remain authentic. Unsupported/F7 is explicit empty, never a fallback reskin.
.proc RdRenderPlayer
 jsr RdRenderGraphicsBank
 lda RdSourceAltPalette
 bne Empty                     ; Source69B3=1 changes CHR too; not selected here.
 ldx RdAnimFrame
 cpx #106
 bcs Empty
 lda RdFacing
 beq Right
 lda RdBodyIndex1,x
 jmp Selected
Right:lda RdBodyIndex0,x
Selected:cmp #$ff
 beq Empty
 pha
 lda RdBodyRadiusY,x
 sta RdRadiusY
 lda RdBodyRadiusX,x
 sta RdRadiusX
 pla
 jsr RdRenderRecord
 clc
 adc #<RD_FIRST_CHR
 sta SmChrBank
 lda R0
 sta SmPosePtr
 lda R1
 sta SmPosePtr+1
 lda #METASPRITE_SAMUS_BODY
 sta ObjectMetasprite
 sec
 rts
Empty:
 lda #<RdArtEmpty
 sta SmPosePtr
 lda #>RdArtEmpty
 sta SmPosePtr+1
 lda #0
 sta ObjectMetasprite
 clc
 rts
.endproc

; Native source slotsD0/E0/F0 only. Animation was advanced by frozen weapons.
; RdWeaponColor=00 ordinary or81 actual Ice override. Native weapons do not
; mirror from player facing; left/right missile geometry comes from25/26.
; Output R0/R1 host descriptor using fixed spritewindows2/3 (tile128..255).
; No SmPosePtr/SmChrBank overwrite, no OAM emission/position mutation.
.proc RdRenderWeapon
 jsr RdRenderGraphicsBank
 lda RdSourceAltPalette
 bne Empty                     ; Never silently use default-pattern costume.
 ldx RdSlot
 cpx #$d0
 beq Slot
 cpx #$e0
 beq Slot
 cpx #$f0
 bne Empty
Slot:
 ldy RdWFrame,x
 cpy #106
 bcs Empty
 lda RdWeaponColor
 beq Normal
 cmp #$81
 bne Empty
 lda RdWeaponIndex1,y
 jmp Selected
Normal:lda RdWeaponIndex0,y
Selected:cmp #$ff
 beq Empty
 pha
 lda RdWeaponRadiusY,y
 sta RdWRadiusY,x
 lda RdWeaponRadiusX,y
 sta RdWRadiusX,x
 pla
 jsr RdRenderRecord
 ldy #0
 lda (R0),y
 beq Blank
 sec
 rts
Empty:
 lda #<RdArtEmpty
 sta R0
 lda #>RdArtEmpty
 sta R1
Blank:clc
 rts
.endproc

.proc RdRenderRecord
 tax
 lda RdArtRecordLo,x
 sta R0
 lda RdArtRecordHi,x
 sta R1
 lda RdArtRecordPage,x
 rts
.endproc

; Return R0/R1 to16 ORIGINAL sprite palette bytes, no queued/global writes.
; Host must compose these roles with world actors instead of blindly replacing
; enemy palettes. alt69B3 changes bodypalette0 only; source CB73 selects row.
; Clobber AXY/P,R0/R1,SmTemp. Does not acknowledge any hardware publication.
.proc RdRenderPalettePointer
 jsr RdRenderGraphicsBank
 lda #0
 ldy RdSourceAltPalette
 beq Suit
 lda #4
Suit:sta SmTemp
 lda RdGear
 and #$20
 beq Missile
 inc SmTemp
 inc SmTemp
Missile:
 lda RdMissileMode
 beq Offset
 inc SmTemp
Offset:
 lda SmTemp
 asl
 asl
 asl
 asl
 clc
 adc #<RdArtPalette
 sta R0
 lda #>RdArtPalette
 adc #0
 sta R1
 rts
.endproc

; Publish wide physicalCHR shadows only, same existing host publication owner.
; Window0=body pose;window1 UNCHANGED;windows2/3=fixed complete weapon2KB.
; Actual hardware publication remains existing host NMI. No mapperA/SMC calls.
.proc RdRenderPublishChr
 lda SmChrBank
 ldy #0
 jsr Publish
 lda #<(RD_FIRST_CHR+RD_WEAPON_CHR_OFFSET)
 ldy #2
 jsr Publish
 lda #<(RD_FIRST_CHR+RD_WEAPON_CHR_OFFSET+1)
 iny
 jsr Publish
 lda #1
 sta X5WideChrActive
 rts
Publish:
 cmp CurrentCHRBank,y
 bne Changed
 ldx X5ChrMode,y
 cpx #($80|>RD_FIRST_CHR)
 beq Done
Changed:
 sta CurrentCHRBank,y
 lda #($80|>RD_FIRST_CHR)
 sta X5ChrMode,y
 lda #1
 sta ReloadCHRBank
Done:rts
.endproc
.popseg
