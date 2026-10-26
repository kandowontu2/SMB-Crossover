; Source STA replacements preserve A/X/Y/P and timer retriggers.
.macro TnDirectWriter Name,Offset
.proc Name
 sta a:GuestNativeApu+Offset
 php
 inc a:GuestNativeDirty+Offset
 plp
 rts
.endproc
.endmacro
.macro TnIndexedWriter Name,Offset
.proc Name
 sta a:GuestNativeApu+Offset,x
 php
 inc a:GuestNativeDirty+Offset,x
 plp
 rts
.endproc
.endmacro
TnDirectWriter TnSourceSTA00,0
TnDirectWriter TnSourceSTA01,1
TnDirectWriter TnSourceSTA04,4
TnDirectWriter TnSourceSTA05,5
TnDirectWriter TnSourceSTA08,8
TnDirectWriter TnSourceSTA0C,12
TnIndexedWriter TnSourceSTA00X,0
TnIndexedWriter TnSourceSTA01X,1
TnIndexedWriter TnSourceSTA02X,2
TnIndexedWriter TnSourceSTA03X,3

.proc TnSourceSTA00Y
 ; NSF initialization also clears4010..4013, outside the16-byte image.
 sta a:TnAudioWriterA
 php
 txa
 pha
 tya
 tax
 cpx #16
 bcs Dmc
 lda a:TnAudioWriterA
 sta a:GuestNativeApu,x
 inc a:GuestNativeDirty,x
 jmp Restore
Dmc:
 lda a:TnAudioWriterA
 cpx #17
 beq Dac
 cpx #18
 beq Address
 cpx #19
 beq Length
 jsr TnSourceSTA10
 jmp Restore
Dac:jsr TnSourceSTA11
 jmp Restore
Address:jsr TnSourceSTA12
 jmp Restore
Length:jsr TnSourceSTA13
Restore:
 pla
 tax
 lda a:TnAudioWriterA
 plp
 rts
.endproc
.proc TnSourceSTA10
 sta a:TnAudioDmcRegs
 sta $4010
 rts
.endproc
.proc TnSourceSTA11
 sta a:TnAudioDmcRegs+1
 sta a:TnAudioDacHold
 sta $4011
 rts
.endproc
.proc TnSourceSTA12
 sta a:TnAudioDmcRegs+2
 php
 pha
 clc
 adc #((TnMusicDpcm-$c000)/64)-1
 sta $4012
 pla
 plp
 rts
.endproc
.proc TnSourceSTA13
 sta a:TnAudioDmcRegs+3
 sta $4013
 rts
.endproc
.proc TnSourceSTA15
 sta a:TnAudioVirtualEnable
 php
 pha
 and #15
 sta a:GuestNativeEnable
 lda a:TnAudioVirtualEnable
 and #$10
 beq Off
 lda #4                        ; Separate native-music DMC owner.
 bne Owner
Off:lda #0
Owner:jsr Cv3DmcOwnerWrite
 lda a:GuestMixMask
 and #8                        ; World pulses use MMC5 expansion voices.
 ora a:GuestNativeEnable
 sta a:GuestCombinedEnable
 lda a:TnAudioVirtualEnable
 and #$10
 ora a:GuestCombinedEnable
 sta a:GuestCombinedEnable
 sta $4015                    ; Preserve source off/on edges, not a poll.
 pla
 plp
 rts
.endproc
.export TnSourceSTA00,TnSourceSTA01,TnSourceSTA04,TnSourceSTA05,TnSourceSTA08,TnSourceSTA0C
.export TnSourceSTA00X,TnSourceSTA01X,TnSourceSTA02X,TnSourceSTA03X,TnSourceSTA00Y
.export TnSourceSTA10,TnSourceSTA11,TnSourceSTA12,TnSourceSTA13,TnSourceSTA15
