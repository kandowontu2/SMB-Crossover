; Defeat can target a different actor from the last shared relative-position
; calculation. Anchor the score to that target's current world position.
.pushseg
.segment "SCORE_POPUP_COLD"
.proc ScorePopupSetup
  sta FloateyNum_Control,x
  lda #$30
  sta FloateyNum_Timer,x
  lda Enemy_Y_Position,x
  sta FloateyNum_Y_Pos,x
  php                            ; Existing callers retain C/V across setup.
  lda Enemy_X_Position,x
  sec
  sbc ScreenLeft_X_Pos
  plp
  ora #0                         ; Return A/N/Z for the actual screen X.
  sta FloateyNum_X_Pos,x
  jsr BillNativeCaptureP
.if ::MAPPER_MMC3
  ; Same existing rare-call stack ABI as the other native cold targets.
  ; Original selector is seven bytes above SP after saving X here.
  txa
  pha
  tsx
  lda $0107,x
  sta BillNativeReturnSelector
  pla
  tax
  lda BillNativeReturnSelector
.else
  lda #0
  sta BillNativeReturnSelector
.endif
  rts
.endproc
.assert * <= $c000,error,"Score anchor exceeds the reserved64-byte A tail"
.popseg
