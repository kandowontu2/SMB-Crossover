; Private original-DK playable adapter. Shared roster does not admit raw28 yet.
; Activation must call DkConstruct BEFORE reading this exclusive active overlay.
.ifndef __DONKEY_KONG_STATE_V1
__DONKEY_KONG_STATE_V1=1
CHARACTER_DONKEY_KONG=28
DK_FIRST_CHR=820
DkReady=$5c00
DkLife=$5c01
DkArea=$5c02
DkWorld=$5c03
DkTier=$5c04
DkPrevious=$5c05
DkFresh=$5c06
DkAttack=$5c07                 ;0none,1rolling barrel,2vertical barrel.
DkAge=$5c08                    ;authored24-update pickup/hold/toss sequence.
DkSpawn=$5c09                  ;one publication at age16; cleared after commit.
DkWalk=$5c0a
DkWalkDelay=$5c0b
DkPose=$5c0c
DkPaletteAck=$5c0d
DkTemp=$5c0e
DkSlot=$5c0f
DkShots=$5c10                  ;3 records12B, ends5C33.
; kind,frame,animationCounter,lifetime,x,page,y,direction,hitReceipt,falling,0,0
DkQuery=$5c34                  ;actual terrain adapter outputs, not a seed.
; bit0 support below; bit1 blocked horizontal leading edge.
DkMirror=$5c35
DkArtPointer=$5c36             ;private pointer staging, not an indirect ZP alias.
DkRenderBuffer=$5c40           ;49-byte full48x32 native descriptor, ends5C70.
DkRenderPage=$5c71
DkShotBuffer=$5c72             ;9-byte complete native barrel descriptor.
.endif
