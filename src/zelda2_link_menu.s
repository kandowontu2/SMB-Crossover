.pushseg
.segment "Z2_LOGIC"
.proc Z2MenuPrepare
 farcall ProtoMenuPrepare
 lda #0
 sta SsChrActive
 sta Z2UiState
 sta Z2PanelActive
 sta Z2PanelPending
 sta Z2HudCacheValid
 rts
.endproc
.popseg
