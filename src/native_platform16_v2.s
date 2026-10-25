; V2: normal native GIRDER_SMALL pose IDs remain unchanged. Do not include the
; v1 render patch. Include native_platform16.s for aliases/native bbox/descriptor.
; Root's resident entry farcalls this once before CrossoverGraphicsBank.
.pushseg
.segment "CROSSOVER_HELPERS"
.proc HpPrepareNativePointers
  ldx #6
  lda #0
Clear:
  sta HpNativeDrawHi,x
  dex
  bpl Clear
  lda ObjectMetasprite
  cmp #METASPRITE_SAMUS_BODY
  bne Helpers
  lda SmPosePtr
  sta HpNativeDrawLo
  lda SmPosePtr+1
  sta HpNativeDrawHi
Helpers:
  ldy #0                       ; Valid16-pixel helper count, no scratch RAM.
  ldx #6
Slot:
  lda Enemy_Flag-1,x
  cmp #1                       ; A live primary native actor, not its duplicate.
  bne Next
  lda Enemy_ID-1,x
  cmp #$25
  beq Tag
  cmp #$28
  bne Next
Tag:
  lda Enemy_State-1,x
  and #$e0                     ; Marker bits and native disabled/dead bit7.
  cmp #$40
  beq OrdinaryWidth
  cmp #$60
  bne Next
  lda #METASPRITE_PLATFORM_GIRDER_SMALL
  bne SetSmall
OrdinaryWidth:
  lda Enemy_BoundBoxCtrl-1,x
  cmp #6
  beq Large
  lda #METASPRITE_PLATFORM_GIRDER_SMALL
  bne SetPose
Large:
  lda #METASPRITE_PLATFORM_GIRDER_LARGE
SetPose:
  sta EnemyMetasprite-1,x
  jmp Next
SetSmall:
  sta EnemyMetasprite-1,x
  lda #<HpNativeSmallDescriptor
  sta HpNativeDrawLo,x
  lda #>HpNativeSmallDescriptor
  sta HpNativeDrawHi,x
  iny
Next:
  dex
  bne Slot
  tya
  beq Done
  ; Refresh the bounded descriptor only when it can actually be consumed.
  ; This makes earlier root scratch use safe; keep the slab stable after here.
  ldx #8
Copy:
  lda HpNativeInitSmallDescriptor::Descriptor,x
  sta HpNativeSmallDescriptor,x
  dex
  bpl Copy
Done:
  rts
.endproc
.popseg
