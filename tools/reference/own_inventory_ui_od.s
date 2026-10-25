; The spring/stomp ownership lifecycle still runs at the original outer
; entry. Only skip unrelated alternate-specific UI dispatch for profiles
; whose original path ends at InventoryUiTick. Mac15 and vehicles18 keep
; their own HUD handlers; every other identity retains the old entry.
.pushseg
.segment "X5_BOUNCE"
.proc X5OwnInventoryUi
 php
 pha
 phx
 ldx SelectedCharacter
 cpx #13
 bcc Legacy
 cpx #15
 beq Legacy
 cpx #18
 beq Legacy
 cpx #20
 bcs Legacy
 plx
 pla
 plp
 farcall InventoryUiTick,jmp
Legacy:
 plx
 pla
 plp
 farcall RlUiDispatch,jmp
.endproc
.export X5OwnInventoryUi
.popseg
