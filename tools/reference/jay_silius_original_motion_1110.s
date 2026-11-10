; Journey to Silius (USA), original player movement and contact slices.
; The 16-bit coordinates and signed velocities use 1/16-pixel units.
; External routines still execute in the pinned donor fixture.
.setcpu "6502"
OriginalSelectPRG = $c6ed
OriginalTerrainEvent = $ea06
OriginalSoundRequest = $ea67

; Screen projection, camera requests, and the original scripted fallback.
.segment "POSITION"
JayPositionSetup:
 lda $1c
 and #$fb
 sta $1c
 jsr ProjectRelative
 lda $ba
 beq OrdinaryPosition
 jmp ScriptedPosition
OrdinaryPosition:
 lda $14
 beq HorizontalScroll
 lda $16
 cmp #$11
 bcc L820C
 cmp #$f1
 bcc HorizontalScroll
 lda #$f0
 bne ClampScreenX
L820C:
 lda #$11
ClampScreenX:
 sta $16
 jsr XWorldFromScreen
HorizontalScroll:
 lda $33
 sta $00
 lda $32
 asl $00
 rol A
 and #$1f
 bne ZeroXScroll
 lda $14
 beq ZeroXScroll
 bmi L823A
 lda $0177
 and #$01
 beq ZeroXScroll
 lda $16
 cmp #$68
 beq TakeXScroll
 bcc ZeroXScroll
TakeXScroll:
 lda $14
 jmp SaveXScroll
L823A:
 lda $0177
 and #$02
 beq ZeroXScroll
 lda $16
 cmp #$98
 bcc TakeXScroll
ZeroXScroll:
 lda #$00
SaveXScroll:
 sta $34
 lda $31
 sta $00
 lda $30
 asl $00
 rol A
 and #$1f
 bne ZeroYScroll
 lda $15
 beq ZeroYScroll
 bmi L8272
 lda $0177
 and #$04
 beq ZeroYScroll
 lda $17
 cmp #$98
 beq TakeYScroll
 bcc ZeroYScroll
TakeYScroll:
 lda $15
 jmp SaveYScroll
L8272:
 lda $0177
 and #$08
 beq ZeroYScroll
 lda $17
 cmp #$68
 bcc TakeYScroll
ZeroYScroll:
 lda #$00
SaveYScroll:
 sta $35
 rts
ScriptedPosition:
 lda $14
 pha
 lda $16
 cmp #$04
 bcc L8295
 cmp #$e9
 bcc RestoreVX
 lda #$e8
 bne L829B
L8295:
 lda #$0c
 sta $14
 lda #$04
L829B:
 sta $16
 jsr XWorldFromScreen
 lda $0171
 bne ScriptedFailure
 lda $11
 sta $0d
 lda $10
 sta $0c
 lda $13
 sta $0f
 lda $12
 sta $0e
 lda $15
 sta $0b
 ldx #$00
 jsr ResolveMappedContact
 lda $0176
 beq RestoreVX
ScriptedFailure:
 lda #$24
 sta $d1
 lda #$03
 sta $d0
 lda #$10
 jsr OriginalTerrainEvent
 lda $19
 ora #$80
 sta $19
 lda #$01
 sta $1f
 dec $53
RestoreVX:
 pla
 sta $14
 rts
XWorldFromScreen:
 lda #$00
 sta $00
 lda $16
 asl A
 rol $00
 asl A
 rol $00
 asl A
 rol $00
 asl A
 rol $00
 clc
 adc $31
 sta $11
 lda $30
 adc $00
 sta $10
 lda $1c
 ora #$04
 sta $1c
 rts

; Signed 16-bit world minus camera, then divide by16 and publish visibility.
.segment "PROJECTION"
ProjectRelative:
 lda #$00
 sta $0171
 lda $19
 and #$df
 sta $19
 lda $11
 sec
 sbc $31
 sta $16
 lda $10
 sbc $30
 lsr A
 ror $16
 lsr A
 ror $16
 lsr A
 ror $16
 lsr A
 ror $16
 cmp #$00
 beq ProjectY
 cmp #$01
 beq LCDBE
 cmp #$0f
 bne Offscreen
 lda $16
 cmp #$a0
 bcc Offscreen
 bcs NearXBorder
LCDBE:
 lda $16
 cmp #$5f
 bcs Offscreen
NearXBorder:
 lda #$7f
 sta $0171
 lda $19
 ora #$20
 sta $19
ProjectY:
 lda $13
 sec
 sbc $33
 sta $17
 lda $12
 sbc $32
 lsr A
 ror $17
 lsr A
 ror $17
 lsr A
 ror $17
 lsr A
 ror $17
 cmp #$00
 beq LCE0B
 cmp #$01
 beq LCDFA
 cmp #$0f
 bne Offscreen
 lda $17
 cmp #$c0
 bcc Offscreen
 bcs NearYBorder
LCDFA:
 lda $17
 cmp #$3f
 bcs Offscreen
NearYBorder:
 lda #$7f
 sta $0171
 lda $19
 ora #$20
 sta $19
LCE0B:
 rts
Offscreen:
 lda #$ff
 sta $0171
 lda $19
 ora #$20
 sta $19
 rts

; Original player gravity/horizontal tail entry.
.segment "INTEGRATE_ENTRY"
JayIntegrate:
 jsr VerticalGravity
 jmp IntegrateHorizontal

; Gravity before tentative position. The resolver owns the final commit.
.segment "INTEGRATOR"
VerticalGravity:
 lda $15
 cmp #$3c
 beq StoreTentativeVY
 clc
 adc #$04
StoreTentativeVY:
 sta $0b
 sta $01
 clc
 adc $13
 sta $0f
 lda $0b
 bmi ExtendNegativeVY
 lda #$00
 beq StoreTentativeYHigh
ExtendNegativeVY:
 lda #$ff
StoreTentativeYHigh:
 adc $12
 sta $0e
 rts
IntegrateHorizontal:
 lda $14
 clc
 adc $11
 sta $0d
 lda $14
 bmi ExtendNegativeVX
 lda #$00
 beq StoreTentativeXHigh
ExtendNegativeVX:
 lda #$ff
StoreTentativeXHigh:
 adc $10
 sta $0c
 jmp ResolveMappedContact

; Map actual donor room bank3, resolve side before vertical, restore PRG.
.segment "CONTACT"
ResolveMappedContact:
 lda #$00
 sta $0150
 lda $f1
 sta $d4
 lda #$03
 jsr OriginalSelectPRG
 jsr ResolveContact
 lda $d4
 jmp OriginalSelectPRG
ResolveContact:
 lda #$00
 sta $0176
 sta $017f
 sta $15
 lda $14
 bne LCE7B
 lda $19
 and #$01
 bne ResolveVertical
 ldy #$08
 bne QueryHorizontal
LCE7B:
 bmi LCE9A
 ldy #$06
 bne QueryHorizontal
SideBlocked:
 lda #$00
 sta $14
 lda $19
 and #$01
 bne LCE93
 lda $ba
 bne LCE93
 lda #$00
 sta $34
LCE93:
 lda #$ff
 sta $0176
 bne ResolveVertical
LCE9A:
 ldy #$04
QueryHorizontal:
 jsr ProbeTerrain
 bne SideBlocked
 lda $0c
 sta $10
 lda $0d
 sta $11
ResolveVertical:
 lda $0b
 beq LCF01
 bmi LCEB3
 ldy #$02
 bne QueryVertical
LCEB3:
 ldy #$00
QueryVertical:
 jsr ProbeTerrain
 bne VerticalBlocked
 lda $19
 and #$01
 bne AcceptVerticalMove
 lda $1c
 and #$01
 bne VerticalBlocked
AcceptVerticalMove:
 lda $19
 ora #$04
 sta $19
 lda $0e
 sta $12
 lda $0f
 sta $13
 lda $0b
 sta $15
 rts
VerticalBlocked:
 lda #$ff
 sta $017f
 lda $19
 and #$04
 beq LCF01
 lda $0b
 bmi CancelUpwardVelocity
 lda $19
 and #$fb
 sta $19
 and #$01
 bne SnapToFloor
 lda #$15
 jsr OriginalSoundRequest
SnapToFloor:
 lda $0e
 sta $12
 lda $0f
 and #$80
 sta $13
LCF01:
 rts
CancelUpwardVelocity:
 lda #$00
 sta $15
 rts

; Native ordered multi-point geometry and original tile class effects.
.segment "PROBE"
ProbeTerrain:
 lda PlayerProbeIndex,X
 sta $02
 lda PlayerProbeIndex+1,X
 sta $03
 lda ($02),Y
 sta $00
 iny
 lda ($02),Y
 sta $01
 ldy #$00
 lda ($00),Y
 sta $0a
 iny
NextSample:
 lda ($00),Y
 iny
 clc
 adc $0f
 lda ($00),Y
 adc $0e
 sta $02
 and #$0f
 cmp #$0f
 bne CheckScrollRow
 lda $0b
 bmi AdvanceWrappedRow
 dec $02
 jmp CheckScrollRow
AdvanceWrappedRow:
 inc $02
CheckScrollRow:
 lda $02
 and #$f0
 sta $09
 lda $32
 and #$f0
 cmp $09
 beq ReadSampleX
 inc $02
ReadSampleX:
 iny
 lda ($00),Y
 iny
 clc
 adc $11
 lda ($00),Y
 adc $10
 sta $03
 iny
 sty $08
 lda $19
 and #$01
 bne QueryNativeTile
 lda $b0
 cmp #$80
 beq MarkSpecialContact
QueryNativeTile:
 jsr ReadPackedNativeTile
 bne ClassifyOccupiedNibble
 ldy $08
 dec $0a
 bne NextSample
 rts
ClassifyOccupiedNibble:
 sta $02
 lda $03
 and #$01
 bne ClassifyTile
 lsr $02
 lsr $02
 lsr $02
 lsr $02
ClassifyTile:
 lda #$00
 sta $df
 lda $02
 cmp #$01
 beq SolidTile
 cmp #$02
 beq LCFA3
 cmp #$03
 beq LCFB8
 cmp #$04
 beq NudgeRight
 cmp #$05
 beq NudgeLeft
SolidTile:
 lda #$ff
 rts
LCFA3:
 lda $19
 and #$01
 bne MarkSpecialContact
 lda #$80
 sta $b0
 lda #$00
 rts
MarkSpecialContact:
 lda #$ff
 sta $0150
 lda #$00
 rts
LCFB8:
 lda $19
 and #$90
 bne LCFD8
 lda $19
 and #$01
 bne LCFDB
 lda $0170
 cmp #$03
 bne LCFD3
 lda #$10
 jsr OriginalTerrainEvent
 lda #$00
 rts
LCFD3:
 lda #$02
 jsr OriginalTerrainEvent
LCFD8:
 lda #$00
 rts
LCFDB:
 lda #$00
 rts
NudgeRight:
 lda #$08
 sta $df
 clc
 adc $11
 sta $11
 lda $10
 adc #$00
 sta $10
 lda #$ff
 rts
NudgeLeft:
 lda #$f8
 sta $df
 clc
 adc $11
 sta $11
 lda $10
 adc #$ff
 sta $10
 lda #$ff
 rts

; Read the packed donor metatile nibble through the original room table.
.segment "TILE_READ"
ReadPackedNativeTile:
 lda $03
 lsr A
 lsr A
 lsr A
 lsr A
 sta $05
 lda $02
 and #$f0
 ora $05
 asl A
 tay
 lda ($44),Y
 sta $05
 iny
 lda ($44),Y
 sta $06
 lda $02
 and #$0f
 asl A
 asl A
 asl A
 sta $04
 lda $03
 lsr A
 and #$07
 ora $04
 sta $04
 stx $07
 lda $03
 and #$01
 tax
 lda NativeNibbleMask,X
 ldx $07
 ldy $04
 and ($05),Y
 rts

; Exact player X=0 index and five two-point signed coordinate lists.
; Each sample is Y low/high then X low/high. Other actors have their own indices.
.segment "PROBE_INDEX"
NativeNibbleMask:
.byte $f0,$0f
PlayerProbeIndex:
.word PlayerProbeList
.segment "PLAYER_PROBES"
PlayerProbeList:
.word HeadProbes,FootProbes,LeftProbes,RightProbes,SupportProbes
HeadProbes:
.byte $02,$00,$ff,$40,$00,$00,$ff,$c0,$ff
FootProbes:
.byte $02,$00,$01,$30,$00,$00,$01,$c0,$ff
LeftProbes:
.byte $02,$80,$ff,$58,$ff,$80,$00,$58,$ff
RightProbes:
.byte $02,$80,$ff,$a8,$00,$80,$00,$a8,$00
SupportProbes:
.byte $02,$a0,$00,$00,$00,$80,$ff,$00,$00
