; Isolated live-call proposal. Resident test origins and copy pages have no
; production allocation. The 1925-byte movement image is never rewritten.
.setcpu "6502"

SelectedCharacter = $6002
MikeAlternate = $730b
CurrentBankA = $0145
CurrentBankC = $7da1
FarCall = $015a
FarTargetLo = $016c
FarTargetHi = $016d
CommonCold = $ae00
CommonRetire = $b026
CommonSelectAfterLoad = $af03
CommonCopy = $ab72
PrivateCode = $a000
Header = $dfe0
Ready = $c033
Epoch = $c034
OldX = $c035
Temp = $c036

.segment "COLD"
JaySceneOrRetire:
 php
 pha
 jsr JayColdIdentity
 bcc OriginalRetire
 jsr CommonCold
 bcc SceneDone
 ; Same-owner warm scene changes discard the old actor only after the
 ; native caller has authenticated both headers. The constructor is hot.
 lda CurrentBankC
 pha
 lda #2
 sta CurrentBankC
 sta $5116
 lda #0
 sta Ready
 pla
 sta CurrentBankC
 sta $5116
SceneDone:
 pla
 plp
 rts
OriginalRetire:
 pla
 plp
 jmp CommonRetire

JaySelect:
 jsr JayColdIdentity
 bcc OriginalSelect
 lda #<Descriptor
 sta $06
 lda #>Descriptor
 sta $07
 lda #<ColdCookie
 sta $08
 lda #>ColdCookie
 sta $09
 sec
 rts
OriginalSelect:
 lda SelectedCharacter
 jmp CommonSelectAfterLoad

JayCopyOrLegacy:
 php
 pha
 jsr JayColdIdentity
 bcc OriginalCopy
 pla
 plp
 ; The old typed bootstrap has no raw16 case. Use its unchanged common
 ; scatter worker and return directly into CoCold's full-header commit.
 lda #$40
 sta FarTargetLo
 lda #$af
 sta FarTargetHi
 lda #$fb
 jmp FarCall
OriginalCopy:
 pla
 plp
 jmp CommonCopy

JayColdIdentity:
 lda SelectedCharacter
 cmp #16
 bne ColdForeign
 lda MikeAlternate
 and #$60
 cmp #$20
 beq ColdIdentityReturn
ColdForeign:
 clc
ColdIdentityReturn:
 rts
ColdCookie:
 .byte CookieBytes

.segment "DESCRIPTOR"
DescriptorData:
 .byte 2,2,1,$4b,1,$4c,1

.segment "HOT"
JayHot:
 php
 pha
 txa
 pha
 tya
 pha
 lda SelectedCharacter
 cmp #16
 bne GoLegacy
 lda MikeAlternate
 and #$60
 cmp #$20
 bne GoLegacy
 lda OperMode
 cmp #1
 bne GoLegacy
 lda OperMode_Task
 cmp #3
 bne GoLegacy
 lda GameEngineSubroutine
 cmp #8
 bne GoLegacy
 lda GamePauseStatus
 lsr A
 bcs GoLegacy
 lda NmiDisable
 bpl GoLegacy
 lda FamilyMainCommit
 lsr A
 bcc GoLegacy
 ; This fixture covers the actual fixed-camera opening only. Its external
 ; weapon fixture executes the authentic donor leaf with B released.
 lda SwimmingFlag
 ora WorldNumber
 ora LevelNumber
 ora ScreenLeft_PageLoc
 ora ScreenLeft_X_Pos
 ora Player_PageLoc
 bne GoLegacy
 lda SavedJoypadBits
 and #$40
 bne GoLegacy
 jmp CheckHeaders
GoLegacy:
 pla
 tay
 pla
 tax
 pla
 plp
 jmp MikeMovement

CheckHeaders:
 lda CurrentBankC
 pha
 ldx #3
CheckHeaderBank:
 stx CurrentBankC
 stx $5116
 ldy #15
CheckHeaderByte:
 lda Header,y
 cmp HotCookie,y
 bne RejectMapped
 dey
 bpl CheckHeaderByte
 dex
 cpx #1
 bne CheckHeaderBank
 lda Ready
 beq NewActor
 lda FrameCounter
 cmp Epoch
 beq DoneMapped
 jmp BeginUpdate
NewActor:
 jsr JayConstruct
BeginUpdate:
 lda FrameCounter
 sta Epoch
 lda Player_X_Position
 sta OldX
 lda PadNow
 sta PadPrevious
 lda SavedJoypadBits
 sta PadNow
 lda CurrentBankA
 pha
 lda #3
 sta CurrentBankA
 sta $5115
 jsr OriginalInput
 jsr PositionSetup
 ldx #0
 jsr Integrate
 pla
 sta CurrentBankA
 sta $5115
 jsr PublishPosition
DoneMapped:
 pla
 sta CurrentBankC
 sta $5116
 pla
 tay
 pla
 tax
 pla
 plp
 rts
RejectMapped:
 pla
 sta CurrentBankC
 sta $5116
 jmp GoLegacy

JayConstruct:
 ldx #50
CopyActorTemplate:
 lda DonorActorTemplate,x
 sta $c000,x
 dex
 bpl CopyActorTemplate
 lda Player_X_Position
 asl A
 asl A
 asl A
 asl A
 sta XLo
 lda Player_X_Position
 lsr A
 lsr A
 lsr A
 lsr A
 sta XHi
 lda Player_Y_Position
 clc
 adc #16
 pha
 asl A
 asl A
 asl A
 asl A
 sta YLo
 pla
 lsr A
 lsr A
 lsr A
 lsr A
 sta YHi
 lda #1
 sta Ready
 rts

PublishPosition:
 lda XHi
 asl A
 asl A
 asl A
 asl A
 sta Temp
 lda XLo
 lsr A
 lsr A
 lsr A
 lsr A
 ora Temp
 sta Player_X_Position
 sta Player_Pos_ForScroll
 sec
 sbc OldX
 sta Player_X_Scroll
 lda YHi
 asl A
 asl A
 asl A
 asl A
 sta Temp
 lda YLo
 lsr A
 lsr A
 lsr A
 lsr A
 ora Temp
 sec
 sbc #16
 sta Player_Y_Position
 lda DonorVY
 ldx #4
ScaleVY:
 cmp #$80
 ror A
 dex
 bne ScaleVY
 sta Player_Y_Speed
 lda DonorFlags
 and #4
 beq PublishState
 lda #1
 ldx DonorVY
 bmi PublishState
 lda #2
PublishState:
 sta Player_State
 rts
HotCookie:
 .byte CookieBytes
DonorActorTemplate:
 .byte TemplateBytes
