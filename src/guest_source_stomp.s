; OldCharacter.hitEnemy tests bottom+enemy.stompable without a water ban.
; Original Bloopa and swimming Cheep cannot be stomped; flying Cheep can.
.pushseg
.segment "SRAM"
GuestBodyStompAllowed: .res 1
.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
.segment "LOWCODE"
.else
.segment "OAMALIGNED"
.endif
.if .not (::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5)
.proc GuestWaterStompPolicy
  lda GuestBodyStompAllowed
  rts
.endproc
.endif
.segment "SAMUS"
.proc GuestSourceStompPolicy
  lda AreaType
  sta GuestBodyStompAllowed
  lda CrossoverBehaviorVersion
  bne Done
  lda SelectedCharacter
  cmp #CHARACTER_SIMON+1
  bcs Done                    ; Later additions retain the existing policy.
  lda Enemy_ID,x
  cmp #Bloober
  beq Blocked
  cmp #GreyCheepCheep
  beq Blocked
  cmp #RedCheepCheep
  beq Blocked
  lda #1
  bne Store
Blocked:
  lda #0
Store:
  sta GuestBodyStompAllowed
Done:
  rts
.endproc
.popseg
