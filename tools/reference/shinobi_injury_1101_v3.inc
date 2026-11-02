; Original Tengen Shinobi injury entry and motion script.
; Requires original animator/interpreter leaves and injury pose 6.
.export ShInjuryScript
.segment "SHINOBI_KERNEL"
Sh_DA1B: LDX #$00
Sh_DA1D: LDA #$10
Sh_DA1F: STA ShState+$0413,X
Sh_DA22: LDA #$06
Sh_DA24: STA ShState+$0300,X
Sh_DA27: JSR Sh_83AB
Sh_DA2A: LDA ShState+$0363,X
Sh_DA2D: AND #$04
Sh_DA2F: BEQ Sh_DA38
Sh_DA31: LDA #$01
Sh_DA33: STA ShState+$03fd,X
Sh_DA36: BNE Sh_DA3D
Sh_DA38: LDA #$02
Sh_DA3A: STA ShState+$03fd,X
Sh_DA3D: LDA #$03
Sh_DA3F: STA ShState+$03a5,X
Sh_DA42: JSR Sh_8327
Sh_DA45: LDA #<ShInjuryScript
Sh_DA47: STA ShState+$043f,X
Sh_DA4A: LDA #>ShInjuryScript
Sh_DA4C: STA ShState+$044a,X
Sh_DA4F: LDA #$00
Sh_DA51: STA ShState+$0455,X
Sh_DA54: STA ShState+$041e,X
Sh_DA57: STA ShState+$0429,X
Sh_DA5A: JSR Sh_8086
Sh_DA5D: RTS
ShInjuryScript: .byte $8d,$04,$88,$04,$08,$88,$03,$04,$88,$02,$04,$8d,$08,$88,$02,$04,$88,$03,$04,$88,$04,$08,$88,$07,$7f,$8b
