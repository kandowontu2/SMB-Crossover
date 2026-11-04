; Mini-only source proposal. No source-wide hook is installed by this file.
; Source funding: ROM bank89 TnMacHeadProbe tail BCC0..BD5F (160B)
; and TnMacSideProbe tail BD72..BE23 (178B), src/tmnt_mac_probes.inc.
; The integrated builder binds the weapon and universal native draw return.
; Native gravity/terrain/explosion/enemy outcomes are retained adaptations.
; Two native actor slots are the user's normal-Mario pool adaptation.
.setcpu "6502"
.macpack longbranch
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
 sta Fireball_State+1
 sta FireballMetasprite
 sta FireballMetasprite+1
 jmp Done
Powered:
 lda A_B_Buttons
 and #$40
 jeq Update
 and PreviousA_B_Buttons
 jne Update
 ldx #0
 lda Fireball_State
 beq Spawn
 inx
 lda Fireball_State+1
 jne Update
Spawn:
 lda Player_Y_HighPos
 cmp #1
 jne Update
 lda #1
 sta Fireball_State,x
 sta Fireball_Y_HighPos,x
 lda #8                    ; existing native4x4 control (native edge convention).
 sta Fireball_BoundBoxCtrl,x
 lda #0
 sta FireballBouncingFlag,x
 sta SprObject_X_MoveForce+7,x
 sta SprObject_Y_MoveForce+7,x
 sta SprObject_YMoveForceFractional+7,x
 ldy #0
 lda PlayerFacingDir
 cmp #2
 beq Left
 lda #2                    ; visible X=base+6, original right spawn X+8.
 bne StoreX
Left:
 dey
 lda #$fa                  ; signed-6, visible X=base+6=original left spawn.
StoreX:
 clc
 adc Player_X_Position
 sta Fireball_X_Position,x
 tya
 adc Player_PageLoc
 sta Fireball_PageLoc,x
 ldy PlayerFacingDir
 lda XSpeeds-1,y
 sta Fireball_X_Speed,x
 lda Player_Y_Position
 clc
 adc #20                   ; visible Y=base+4=source MarioY.
 sta Fireball_Y_Position,x
 lda SavedJoypadBits
 and #8
 beq DownShot
 lda #$ff
 bne StoreYSpeed
DownShot:
 lda #1
StoreYSpeed:
 sta Fireball_Y_Speed,x
 lda #$20
 sta Square1SoundQueue
 jmp Update
XSpeeds: .byte $20,$e0

.segment "MINI_FB_HELPERS"
Update:
 ldx #0
 jsr UpdateSlot
 inx
 jsr UpdateSlot
Done:
 pla
 tay
 pla
 tax
 pla
 plp
 sec
 rts
UpdateSlot:
 lda Fireball_State,x
 beq SlotDone              ; no bank switch for an idle empty slot.
 jsr NativeCore
 lda Fireball_State,x
 cmp #1
 beq HideShot
 cmp #$80                  ; native collision still calls DrawFireball once.
 bne SlotDone              ; states81+ retain genuine native explosion art.
HideShot:
 lda #0
 sta FireballMetasprite,x  ; live ball is drawn by MiniFireballDraw.
SlotDone:
 rts
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
 ldy #0
DrawSlot:
 lda Fireball_State,y
 cmp #1
 bne NextDraw
 lda Fireball_X_Position,y
 sec
 sbc ScreenLeft_X_Pos
 sta $03
 lda Fireball_PageLoc,y
 sbc ScreenLeft_PageLoc
 bne NextDraw
 lda $03
 cmp #246
 bcs NextDraw
 lda Fireball_Y_Position,y
 cmp #236
 bcs NextDraw
 ldx CurrentOAMOffset
 cpx #252
 bcs NextDraw
 lda GuestOamRotationActive
 beq PhysicalReady
 txa
 clc
 adc RgOamRotation
 tax
PhysicalReady:
 lda Fireball_Y_Position,y
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
NextDraw:
 iny
 cpy #2
 bne DrawSlot
 rts

.segment "MINI_FB_ART"
MiniFireballArt:
 ; User-requested4x4 opaque extent, centered warm core, no resampling claim.
 .byte $f0,$90,$90,$f0,0,0,0,0
 .byte $00,$60,$60,$00,0,0,0,0
 .res 16,0
MiniFireballArtEnd:
