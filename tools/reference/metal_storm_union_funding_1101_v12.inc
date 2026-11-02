; Source compaction of the two real72-byte native callback selectors. Their
; public entry PCs and actual source target/flags/register contracts remain.
; This component does not grant menu admission or publish unowned RAM code.
.macro Ms12UnionDrops
 sta SafecallA_SMC+1
 txa
 pha
 tya
 pha
 php
 ldy #0
::Ms12CallbackSelect:
 lda SelectedCharacter
 cmp #2
 bne Ms12CallbackLegacy
 lda RdVariant
 cmp #1
 beq Ms12CallbackRogue
 lda #2
::Ms12CallbackLegacy:
 plp
 jsr HuZ2FromSelected
 php
 bcc Ms12CallbackPick
 iny
 bne Ms12CallbackPick       ; role0/3 +1 is always nonzero
::Ms12CallbackRogue:
 iny
 iny
::Ms12CallbackPick:
 lda Ms12CallbackLo,y
 sta FarcallJmpTarget_SMC+1
 lda Ms12CallbackHi,y
 sta FarcallJmpTarget_SMC+2
 lda Ms12CallbackBank,y
 sta NextBank_SMC+1
 jmp Ms12CallbackRestore
::Ms12CallbackLo:
 .byte <InventoryUpdateDrops,<Z2UpdateDropsGate,<RdHzUpdateDrops
 .byte <RemainingWeapons,<Z2RemainingWeaponsGate,<RdWxRemainingGate
::Ms12NativeKr:
 bne Ms12MetalRoute           ; originalCMP34 Z still live through twoJMPs
 lda #.lobyte(.bank(KrServiceVeneers)|$80)
 jmp ThFFBankReady
 .assert *-HuUpdateDrops=72,lderror,"Original native drops public span"
.endmacro

.macro Ms12UnionWeapons
 sta SafecallA_SMC+1
 txa
 pha
 tya
 pha
 php
 ldy #3
 bne Ms12CallbackSelect      ; fixed role3 and signed branch within72B
::Ms12CallbackRestore:
 ; StackP/Y/X. Move the genuine source-predicate flags over the savedY slot,
 ; then unwind without using foreground or NMI scratch. Discard the same
 ; Core JSR return as the original HuSourceCallbackTail: this is a tail call,
 ; not another native farcall frame.
 tsx
 ldy $0102,x
 lda $0101,x
 sta $0102,x
 pla
 plp
 pla
 tax
 pla
 pla
 jmp NextBank_SMC
::Ms12CallbackHi:
 .byte >InventoryUpdateDrops,>Z2UpdateDropsGate,>RdHzUpdateDrops
 .byte >RemainingWeapons,>Z2RemainingWeaponsGate,>RdWxRemainingGate
::Ms12CallbackBank:
 .byte .lobyte(.bank(InventoryUpdateDrops)|$80),.lobyte(.bank(Z2UpdateDropsGate)|$80),.lobyte(.bank(RdHzUpdateDrops)|$80)
 .byte .lobyte(.bank(RemainingWeapons)|$80),.lobyte(.bank(Z2RemainingWeaponsGate)|$80),.lobyte(.bank(RdWxRemainingGate)|$80)
::Ms12MetalRoute:
 ; The real native entry table supplies only rows0..35, with row36 reserved
 ; for typed callers. No arbitrary Y value is a legal public service row.
 lda #$ab
 sta FarcallJmpTarget_SMC+2
 tya
 sta FarcallJmpTarget_SMC+1
 asl
 adc FarcallJmpTarget_SMC+1
 adc #$6d
 sta FarcallJmpTarget_SMC+1
 lda #($80|78)
 sta NextBank_SMC+1
 jmp HuCommon::Restore
 .res 3,$ff
 .assert *-HuRemainingWeapons=72,lderror,"Original native weapons public span"
.endmacro
