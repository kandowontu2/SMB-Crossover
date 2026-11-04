; Mini-only source proposal. No source-wide hook is installed by this file.
; Source funding: ROM bank89 TnMacHeadProbe tail BCC0..BD5F (160B)
; and TnMacSideProbe tail BD72..BE23 (178B), src/tmnt_mac_probes.inc.
; The integrated builder binds the weapon and universal native draw return.
; Native gravity/terrain/explosion/enemy outcomes are retained adaptations.
; One live actor follows the original Mini OnAttack admission.
.setcpu "6502"
.export MiniFireballTail,MiniFireballDraw,MiniFireballDrawReturn
.export MiniFireballArt,MiniFireballArtEnd

PlayerStatus=$075b
Player_X_Position=$75
Player_PageLoc=$5c
Player_Y_Position=$bd
Player_Y_HighPos=$a4
PlayerFacingDir=$053e
A_B_Buttons=$0558
PreviousA_B_Buttons=$055b
SavedJoypadBits=$dc
Fireball_State=$25
Fireball_X_Position=$7c
Fireball_PageLoc=$63
Fireball_Y_Position=$c4
Fireball_Y_HighPos=$ab
Fireball_X_Speed=$4d
Fireball_Y_Speed=$95
FireballMetasprite=$06e8
FireballBouncingFlag=$3a
Fireball_BoundBoxCtrl=$064c
CurrentOAMOffset=$06de
GuestOamRotationActive=$6c0b
RgOamRotation=$6c08
ScreenLeft_X_Pos=$071f
ScreenLeft_PageLoc=$071d
Sprite_Data=$0200
FarcallTarget=$016c
FarCall=$015a
SprObject_X_MoveForce=$05cf
SprObject_Y_MoveForce=$0602
SprObject_YMoveForceFractional=$05e5
Square1SoundQueue=$0105

.segment "MINI_FB_ATTACK"
MiniFireballTail:
 php
 pha
 txa
 pha
 tya
 pha
 lda PlayerStatus
 cmp #2
 beq Powered
 lda #0
 sta Fireball_State
 sta FireballMetasprite
 jmp Done
Powered:
 lda A_B_Buttons
 and #$40
 beq Update
 and PreviousA_B_Buttons
 bne Update
 lda Fireball_State
 bne Update
 lda Player_Y_HighPos
 cmp #1
 bne Update
 lda #1
 sta Fireball_State
 sta Fireball_Y_HighPos
 lda #8                    ; existing native4x4 control (native edge convention).
 sta Fireball_BoundBoxCtrl
 lda #0
 sta FireballBouncingFlag
 sta SprObject_X_MoveForce+7
 sta SprObject_Y_MoveForce+7
 sta SprObject_YMoveForceFractional+7
 ldy #0
 ldx PlayerFacingDir
 cpx #2
 beq Left
 lda #2                    ; visible X=base+6, original right spawn X+8.
 bne StoreX
Left:
 dey
 lda #$fa                  ; signed-6, visible X=base+6=original left spawn.
StoreX:
 clc
 adc Player_X_Position
 sta Fireball_X_Position
 tya
 adc Player_PageLoc
 sta Fireball_PageLoc
 lda XSpeeds-1,x
 sta Fireball_X_Speed
 lda Player_Y_Position
 clc
 adc #20                   ; visible Y=base+4=source MarioY.
 sta Fireball_Y_Position
 lda SavedJoypadBits
 and #8
 beq DownShot
 lda #$ff
 bne StoreYSpeed
DownShot:
 lda #1
StoreYSpeed:
 sta Fireball_Y_Speed
 lda #$20
 sta Square1SoundQueue
Update:
 lda Fireball_State
 beq Done                  ; do not bank-switch for an idle empty pool.
 ldx #0
 jsr NativeCore
 lda Fireball_State
 cmp #1
 beq HideShot
 cmp #$80                  ; native collision still calls DrawFireball once.
 bne Done                  ; states81+ retain genuine native explosion art.
HideShot:
 lda #0
 sta FireballMetasprite    ; live ball is drawn by MiniFireballDraw.
Done:
 pla
 tay
 pla
 tax
 pla
 plp
 sec
 rts
XSpeeds: .byte $20,$e0

.segment "MINI_FB_HELPERS"
NativeCore:
 lda #$a7
 sta FarcallTarget
 lda #$ae
 sta FarcallTarget+1
 lda #$80
 jmp FarCall               ; actual original bank0 FireballObjCore=$AEA7.

; Universal MiniNativeDraw return: both fast and original native render paths.
; Keep its original public AXYP-except-C contract, including hidden poses.
MiniFireballDrawReturn:
 php
 pha
 txa
 pha
 tya
 pha
 jsr MiniFireballDraw
 pla
 tay
 pla
 tax
 pla
 plp
 sec
 rts

; Called AFTER native Mini body draw, with the normal OAM ring valid.
; Only the live ball is appended; native impact/explosion metasprites remain.
MiniFireballDraw:
 lda Fireball_State
 cmp #1
 bne DrawDone
 lda Fireball_X_Position
 sec
 sbc ScreenLeft_X_Pos
 sta $03
 lda Fireball_PageLoc
 sbc ScreenLeft_PageLoc
 bne DrawDone
 lda $03
 cmp #246
 bcs DrawDone
 lda Fireball_Y_Position
 cmp #236
 bcs DrawDone
 ldx CurrentOAMOffset
 cpx #252
 bcs DrawDone
 txa
 ldy GuestOamRotationActive
 beq PhysicalReady
 clc
 adc RgOamRotation
 tax
PhysicalReady:
 lda Fireball_Y_Position
 clc
 adc #3                    ; OAM Y+1 then visible row0 =>base+4.
 sta Sprite_Data,x
 lda #$6f                  ; slot5 + metadata offset$2E0, 8x16 lowbit1.
 sta Sprite_Data+1,x
 lda #2
 sta Sprite_Data+2,x
 lda $03
 clc
 adc #6
 sta Sprite_Data+3,x
 lda CurrentOAMOffset
 clc
 adc #4
 sta CurrentOAMOffset
DrawDone:
 rts

.segment "MINI_FB_ART"
MiniFireballArt:
 ; User-requested4x4 opaque extent, centered warm core, no resampling claim.
 .byte $f0,$90,$90,$f0,0,0,0,0
 .byte $00,$60,$60,$00,0,0,0,0
 .res 16,0
MiniFireballArtEnd:
