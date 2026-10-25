; Read-only broad phases. Any possibly solid block or enemy overlap still
; reaches the unchanged native dispatch, including its probe/contact order.
.pushseg
.segment "ROLL_CORE"
.proc RlBlocks
 lda #0
 sta MmBreakBlock
 sta MmProbeIndex
 ldy MmBulletType,x
 dey
 lda Left,y
 sta MmDamage
 lda Right,y
 ldy MmBulletDir,x
 cpy #1
 beq Extents
 ldy MmDamage
 sta MmDamage
 tya
Extents:
 clc
 adc MmBulletX,x
 sta MmBillEdgeX
 lda MmBulletPage,x
 adc #0
 sta MmBillEdgePage
 sec
 lda MmBulletX,x
 sbc MmDamage
 sta MmBillEdgeX+1
 lda MmBulletPage,x
 sbc #0
 sta MmBillEdgePage+1
 ldy MmBulletType,x
 lda Vertical-1,y
 sta MmDamage
 sec
 lda MmBulletY,x
 sbc MmDamage
 sta MmBillEdgeY
 clc
 lda MmBulletY,x
 adc MmDamage
 sta MmBillEdgeY+1
 ldy #1
Rows:lda MmBillEdgeY,y
 cmp #32
 bcc Outside
 cmp #240
 bcs Outside
 and #$f0
 sec
 sbc #32
 bcs SaveRow
Outside:lda #$ff
SaveRow:sta MmBillRow,y
 dey
 bpl Rows
Column:
 ldy MmProbeIndex
 lda MmBillEdgeX,y
 lsr
 lsr
 lsr
 lsr
 sta MmTemp
 lda MmBillEdgePage,y
 and #1
 asl
 asl
 asl
 asl
 ora MmTemp
 jsr GetBlockBufferAddr
 ldy MmBillRow
 cpy #$ff
 beq Bottom
 jsr CellEmpty
 bcs Native
Bottom:
 ldy MmBillRow+1
 cpy MmBillRow
 beq Next
 cpy #$ff
 beq Next
 jsr CellEmpty
 bcs Native
Next:
 lda MmProbeIndex
 bne Clear
 lda MmBillEdgeX
 eor MmBillEdgeX+1
 and #$f0
 beq Clear
 inc MmProbeIndex
 jmp Column
Clear:
 lda #4                        ; Same completed ordinary-probe index.
 sta MmProbeIndex
 ldx MmSlot
 rts
Native:
 ldx MmSlot
 farcall MegaManWeapons::Blocks,jmp
CellEmpty:
 lda (R6),y
 beq Empty
 cmp #$23
 beq Empty
 cmp #$26
 beq Empty
 cmp #$c2
 beq Empty
 cmp #$c3
 beq Empty
 sec
 rts
Empty:clc
 rts
Left:.byte 4,0,9
Right:.byte 4,0,7
Vertical:.byte 3,0,7
.endproc
.proc RlEnemies
 lda RlEnemyEnvelope
 bne Ready
 farcall GuestPrepareEnemies
 lda #1
 sta RlEnemyEnvelope
Ready:
 ldx MmSlot
 lda GuestEnemyMask
 beq Clear
 lda GuestEnemyWrapY
 bne Native
 ldy MmBulletType,x
 lda Radius-1,y
 sta MmDamage
 sec
 lda MmBulletY,x
 sbc MmDamage
 sta MmBillEdgeY
 clc
 lda MmBulletY,x
 adc MmDamage
 cmp MmBillEdgeY
 bcc Native                    ; Preserve native vertical seam handling.
 beq Native
 cmp GuestEnemyMinY
 bcc Clear
 lda GuestEnemyMaxY
 cmp MmBillEdgeY
 bcc Clear
Native:
 ; A real contact can mutate actor state or its box. Refresh before another
 ; shot may reuse this envelope; an unchanged miss can keep the cache.
 lda #0
 sta RlEnemyEnvelope
 farcall MegaManWeapons::Enemies,jmp
Clear:rts
Radius:.byte 3,0,7
.endproc
.popseg
