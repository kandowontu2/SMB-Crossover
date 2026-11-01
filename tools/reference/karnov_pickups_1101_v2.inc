; Original Karnov earned upgrades plus an explicit SMB item adapter.
; Source ROM SHA 0d49c112...; exact donor addresses are retained below.
; Services20/23/24 require the authenticated resident and mapped C2 state.
; 20/23 retain AXYP except C; 24 consumes AXY/P like native NrPickup.
; Source core changes only C000..C7FF and saves/restores foreground R0/R1.
; No NMI0..2, generic PlayerStatus tier, automatic block-hit award, or PPU write.
.import InvPickupOwner,InvPickup,InvRisePhase,InvPickupSaveLo,InvPickupSaveHi
.import PowerUpType,Enemy_State,Enemy_ID,Enemy_Flag
.import EraseEnemyObject,SetupFloateyNumber,Square2SoundQueue
.import VRAM_Buffer1,VRAM_Buffer1_Offset
.export KrPickupPrepare,KrPickupMature,KrPickupCollect,KrPickupReset
.export KrPickupSuperFireball,KrPickupGrantOption,KrPickupCoreEnd,KrPickupEnd
.export KrPickupOriginal_AD79,KrPickupOriginal_EF61,KrPickupOriginal_CF7E
.export KrPickupOriginal_C847,KrPickupPaletteQueue
.ifndef KR_PICKUP_NATIVE_HUD
 .export KrPickupOriginal_C534
.endif
.export KrPickupResetEnd,KrPickupAlignEnd,KrPickupMatureEnd
; Parent binds this no-return native boundary to its existing farcall macro.
.import KrPickupMarioFallback
KrPickupCycle=$c860
KrPickupSlot=$c861
KrPickupFloatey=$c862
KrPickupOldMarks=$c863

; Call once from KrNewLife, after clearing original state. Loader initializes
; this byte on first load; same-life scene seams retain earned cycle position.
.ifdef KR_PICKUP_SPLIT
 .pushseg
 .segment "KR_PICKUP_RAM"
.endif
KrPickupReset:
 lda #0
 sta KrPickupCycle
 rts
KrPickupResetEnd:
.ifdef KR_PICKUP_SPLIT
 .popseg
 .pushseg
 .segment "KR_PICKUP_ALIGN"
.endif

; AD79..ADB0. Original blue health is healed BEFORE adding a shot. Preserve
; source68bit40 and the complete69 hurt timer. Active source special weapons
; suppress shot upgrades exactly as in Karnov. Original collectible-tail map,
; score and sound requests AD B1..CA are replaced by native contact effects.
KrPickupSuperFireball:
KrPickupOriginal_AD79:
 lda KrState+$68
 bpl KrPickup_AD97
 lda KrState+$68
 and #$7f
 sta KrState+$68
 lda #$28
 sta KrState+$34
 lda #$16
 sta KrState+$35
 lda #$0f
 sta KrState+$36
 lda #1
 jmp KrPickupPaletteQueue
KrPickup_AD97:
 lda KrState+$65
 and #$0c
 bne KrPickup_ADB1
 lda KrState+$65
 and #3
 cmp #2
 bcs KrPickup_ADB1
 adc #1
 sta KrState+$44
 lda KrState+$65
 and #$fc
 ora KrState+$44
 sta KrState+$65
KrPickup_ADB1:rts
KrPickupAlignEnd:
.ifdef KR_PICKUP_SPLIT
 .popseg
.endif

; EF61..F027. Independently callable A=item0..9. Invalid A is rejected by
; the public wrapper. Original earned bits, BCD stock, selected option, K-mark
; life ledger, private HUD tiles/queue and pending redraw bits are retained.
KrPickupGrantOption:
 cmp #10
 bcc KrPickupGrantValid
 rts
KrPickupGrantValid:
 sta KrPickupRequested
 lda KrPointer
 sta KrSaved0
 lda KrPointer+1
 sta KrSaved1
 ; A was the requested item before pointer save.
 lda KrPickupRequested
 jsr KrPickupOriginal_EF61
 php
 pha
 lda KrSaved0
 sta KrPointer
 lda KrSaved1
 sta KrPointer+1
 pla
 plp
 rts
; Public caller stores A here before pointer preservation through the entry
; trampoline below; private byte864 has no actor/health ownership.
KrPickupRequested=$c864
KrPickupOriginal_EF61:
 pha
 ldx #0
 ldy #$8f
 jsr KrPickupOriginal_C847
.ifdef KR_PICKUP_NATIVE_HUD
 ; C534 only changes unused donor HUD tiles/B4..B9. Its final valid-table
 ; ADC #$10 always clearsV. Native HUD publication is an explicit boundary.
 clv
.else
 ldx #$ff
 jsr KrPickupOriginal_C534
.endif
 pla
 sta KrState+$4b
 jsr KrPickupDispatch
 .word KrPickup_EF88,KrPickup_EF94,KrPickup_EFB8,KrPickup_EFA0
 .word KrPickup_EFAC,KrPickup_EFC0,KrPickup_EFBD,KrPickup_EFC3
 .word KrPickup_EFB8,KrPickup_EFD4
KrPickup_EF88:
 lda KrState+$bd
 jsr KrPickupOriginal_CF7E
 sta KrState+$bd
 lda #4
 jmp KrPickup_EFB5
KrPickup_EF94:
 lda KrState+$bb
 jsr KrPickupOriginal_CF7E
 sta KrState+$bb
 lda #4
 jmp KrPickup_EFB5
KrPickup_EFA0:
 lda KrState+$be
 jsr KrPickupOriginal_CF7E
 sta KrState+$be
 lda #5
 jmp KrPickup_EFB5
KrPickup_EFAC:
 lda KrState+$bc
 jsr KrPickupOriginal_CF7E
 sta KrState+$bc
 lda #5
KrPickup_EFB5:
 jsr KrPickupPaletteQueue
KrPickup_EFB8:
 lda KrState+$4b
 jmp KrPickup_F01A
KrPickup_EFBD:jmp KrPickup_EFCF
KrPickup_EFC0:jmp KrPickup_EFCF
KrPickup_EFC3:
 lda KrState+$bf
 jsr KrPickupOriginal_CF7E
 sta KrState+$bf
 lda #6
 jsr KrPickupPaletteQueue
KrPickup_EFCF:
 lda #0
 jmp KrPickup_F01A
KrPickup_EFD4:
 inc KrState+$071c
 inc KrState+$ba
 lda KrState+$ba
 and #$0f
 cmp #$0a
 bcc KrPickup_EFEA
 lda KrState+$ba
 clc
 adc #$10
 and #$f0
 sta KrState+$ba
KrPickup_EFEA:
 lda KrState+$ba
 cmp #$50
 bcc KrPickup_F01C
 lda #0
 sta KrState+$ba
 lda #$19
 jsr KrPickupSourceSound
 inc KrState+$040b
 lda KrState+$040b
 and #$0f
 cmp #$0a
 bcc KrPickup_F01C
 lda KrState+$040b
 clc
 adc #$10
 and #$f0
 sta KrState+$040b
 cmp #$a0
 bcc KrPickup_F01C
 lda #$99
 sta KrState+$040b
 rts
KrPickup_F01A:sta KrState+$8e
KrPickup_F01C:
 lda #$10
 ora KrState+$5f
 sta KrState+$5f
 lda #$17
 jmp KrPickupSourceSound

; C847..C869 specialized to the one declared pointer target $008F.
; All scratch and returned AXY/flags are original; data pointer59/5A is private
; state, not a host ZP pair. Only the indirect ORA/STA is resolved statically.
KrPickupOriginal_C847:
 sta KrState+$58
 txa
 pha
 tya
 pha
 sty KrState+$59
 stx KrState+$5a
 lda KrState+$58
 lsr
 lsr
 lsr
 tay
 lda KrState+$58
 and #7
 tax
 lda KrPickupBits,x
 ora KrState+$8f,y
 sta KrState+$8f,y
 pla
 tay
 pla
 tax
 lda KrState+$58
 rts
KrPickupBits:.byte 1,2,4,8,16,32,64,128

; C534..C58B plus its exact20-byte C58C..C59F option tile lookup.
; This is private source HUD bookkeeping; native HUD publication is separate.
.ifndef KR_PICKUP_NATIVE_HUD
KrPickupOriginal_C534:
 asl
 tay
 txa
 pha
 lda KrPickupOptionTiles,y
 sta KrState+$58
 tax
 lda KrPickupOptionTiles+1,y
 tay
 clc
 adc KrState+$a1
 sta KrState+$b4
 lda #0
 adc KrState+$a2
 sta KrState+$b5
 txa
 sta KrState+$0564,y
 sta KrState+$b6
 inx
 txa
 sta KrState+$0565,y
 sta KrState+$b7
 lda KrState+$58
 clc
 adc #$10
 tax
 sta KrState+$0584,y
 sta KrState+$b8
 inx
 txa
 sta KrState+$0585,y
 sta KrState+$b9
 pla
 bne KrPickup_C58B
 lda #$b7
 sta KrState+$b6
 sta KrState+$0564,y
 lda #$b5
 sta KrState+$b7
 sta KrState+$0565,y
 lda #$bc
 sta KrState+$b8
 sta KrState+$0584,y
 lda #$b6
 sta KrState+$b9
 sta KrState+$0585,y
KrPickup_C58B:rts
KrPickupOptionTiles:
 .byte $82,$2b,$84,$2d,$86,$2f,$88,$31,$8a,$33
 .byte $a0,$35,$8e,$37,$8c,$39,$a2,$3b,$80,$3d
.endif

; CF7E..CF99: original binary arithmetic on packed BCD, capped at99.
KrPickupOriginal_CF7E:
 tax
 clc
 adc #1
 tay
 and #$0f
 cmp #$0a
 bcs KrPickup_CF8B
 tya
 rts
KrPickup_CF8B:
 txa
 and #$f0
 clc
 adc #$10
 tay
 cmp #$a0
 bcs KrPickup_CF98
 tya
 rts
KrPickup_CF98:txa
 rts
; C2C7..C2DE source command ring. Opcodes1/4/5/6 request source palette/HUD
; work. This queue is evidence-preserved; it is not native PPU hardware.
KrPickupPaletteQueue:
 ldy KrState+$070f
 cpy #8
 bcs KrPickup_C2DE
 ldx KrState+$0710
 sta KrState+$0712,x
 inx
 txa
 and #7
 sta KrState+$0710
 inc KrState+$070f
KrPickup_C2DE:rts
KrPickupSourceSound:
 sta KrSoundEvent
 rts
; Exact inline-word dispatcher C831..C846. Foreground3/4 is restored by
; KrPickupGrantOption; this local copy also works if the module lives inROM29.
KrPickupDispatch:
 asl
 tay
 pla
 sta KrPointer
 pla
 sta KrPointer+1
 iny
 lda (KrPointer),y
 tax
 iny
 lda (KrPointer),y
 sta KrPointer+1
 stx KrPointer
 jmp (KrPointer)
KrPickupCoreEnd:

; Service20 tags a real object. It grants NOTHING. Native movement/drawing
; continue until service23 admits contact after mushroom/flower emergence.
KrPickupPrepare:
 php
 pha
 cpx #6
 bcs KrPickupPrepareNo
 lda KrReady
 cmp #$a7
 bne KrPickupPrepareNo
 ; UnionPwrUpCore uses Mario PlayerStatus before this hook. Translate that
 ; object's ordinary0/1 type from earned SOURCE state instead. Source injured
 ; or single-shot=>mushroom; healthy double/triple=>flower. Stars/1UP stay.
 lda PowerUpType,x
 cmp #2
 bcs KrPickupTag
 lda KrState+$68
 bmi KrPickupSpawnMushroom
 lda KrState+$65
 and #$0c
 beq KrPickupSpawnBase
 lda KrState+$68
 jmp KrPickupSpawnLevel
KrPickupSpawnBase:
 lda KrState+$65
KrPickupSpawnLevel:
 and #3
 beq KrPickupSpawnMushroom
 lda #1
 bne KrPickupSpawnStore
KrPickupSpawnMushroom:
 lda #0
KrPickupSpawnStore:
 sta PowerUpType,x
KrPickupTag:
 lda #34
 sta InvPickupOwner,x
 lda #$fc
 sta InvPickup,x
 lda #0
 sta InvRisePhase,x
 sta InvPickupSaveLo,x
 sta InvPickupSaveHi,x
 pla
 plp
 sec
 rts
KrPickupPrepareNo:
 pla
 plp
 clc
 rts
.ifdef KR_PICKUP_SPLIT
 .pushseg
 .segment "KR_PICKUP_RAM"
.endif
KrPickupMature:
 php
 pha
 cpx #6
 bcs KrPickupMatureNo
 lda KrReady
 cmp #$a7
 bne KrPickupMatureNo
 lda PowerUpType,x
 cmp #2
 bcs KrPickupMatureYes
 lda Enemy_State,x
 bpl KrPickupMatureNo
KrPickupMatureYes:
 pla
 plp
 sec
 rts
KrPickupMatureNo:
 pla
 plp
 clc
 rts
KrPickupMatureEnd:
.ifdef KR_PICKUP_SPLIT
 .popseg
.endif

; Service24 is called only AFTER native body collision. Native stars/1UPs
; use their original consumer. Mushroom->SuperFireball; flower heals/advances
; the same source shot progression, then cycles original options0..9 only
; once healthy triple-shot is already earned. This mapping is a host policy.
KrPickupCollect:
 cpx #6
 jcs KrPickupCollectNo
 lda KrReady
 cmp #$a7
 jne KrPickupCollectNo
 lda Enemy_Flag,x
 jeq KrPickupCollectNo
 lda Enemy_ID,x
 cmp #PowerUpObject
 jne KrPickupCollectNo
 lda PowerUpType,x
 cmp #2
 bcc KrPickupContactForm
 jmp KrPickupMarioFallback
KrPickupContactForm:
 lda Enemy_State,x
 jpl KrPickupCollectNo
 stx KrPickupSlot
 lda #6
 sta KrPickupFloatey
 lda PowerUpType,x
 beq KrPickupUseFireball
 lda KrState+$68
 bmi KrPickupUseFireball
 lda KrState+$65
 and #$0c
 beq KrPickupBaseShot
 lda KrState+$68
 jmp KrPickupHaveShot
KrPickupBaseShot:lda KrState+$65
KrPickupHaveShot:
 and #3
 cmp #2
 bcc KrPickupUseFireball
 lda KrState+$ba
 sta KrPickupOldMarks
 lda KrPickupCycle
 sta KrPickupRequested
 jsr KrPickupGrantOption
 inc KrPickupCycle
 lda KrPickupCycle
 cmp #10
 bcc KrPickupAfterGrant
 lda #0
 sta KrPickupCycle
KrPickupAfterGrant:
 lda KrState+$ba
 bne KrPickupNativeEffects
 lda KrPickupOldMarks
 beq KrPickupNativeEffects
 lda #$0b
 sta KrPickupFloatey
 bne KrPickupNativeEffects
KrPickupUseFireball:
 jsr KrPickupSuperFireball
KrPickupNativeEffects:
 ; Opaque player colors only, preserving shared backdrop/sky and R0..R7.
 ldx VRAM_Buffer1_Offset
 cpx #72
 bcs KrPickupNoPalette
 lda #$3f
 sta VRAM_Buffer1,x
 lda #$11
 sta VRAM_Buffer1+1,x
 lda #3
 sta VRAM_Buffer1+2,x
 lda #$28
 sta VRAM_Buffer1+3,x
 lda #$16
 sta VRAM_Buffer1+4,x
 lda #$0f
 sta VRAM_Buffer1+5,x
 lda #0
 sta VRAM_Buffer1+6,x
 txa
 clc
 adc #6
 sta VRAM_Buffer1_Offset
KrPickupNoPalette:
 lda #Sfx_PowerUpGrab
 sta Square2SoundQueue
 ldx KrPickupSlot
 jsr EraseEnemyObject
 lda #0
 sta InvPickupOwner,x
 sta InvPickup,x
 sta InvRisePhase,x
 sta InvPickupSaveLo,x
 sta InvPickupSaveHi,x
 lda KrPickupFloatey
 jmp SetupFloateyNumber
KrPickupCollectNo:clc
 rts
KrPickupEnd:
