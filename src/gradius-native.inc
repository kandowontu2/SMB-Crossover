; Original Gradius NSF engine/data, generated from executed operand/pointer provenance.
; Six pointer bytes retain their native zero-page addresses; channel state uses shared history.
.pushseg
.segment "VIC_NATIVE_AUDIO"
.scope GradiusMusic
VgEBF0:
VgEBF1 = *+1
  LDA #$c0
VgEBF2:
VgEBF3 = *+1
VgEBF4 = *+2
  STA $4017
VgEBF5:
VgEBF6 = *+1
VgEBF7 = *+2
  LDA VgEC28,x
VgEBF8:
  RTS
VgEBF9:
  .byte $00
VgEBFA:
  .byte $00
VgEBFB:
  .byte $00
VgEBFC:
  .byte $00
VgEBFD:
  .byte $00
VgEBFE:
  .byte $00
VgEBFF:
  .byte $00
VgEC00:
  .byte $50
VgEC01:
  .byte $00
VgEC02:
  .byte $53
VgEC03:
  .byte $bd
VgEC04:
  .byte $67
VgEC05:
  .byte $58
VgEC06:
  .byte $59
VgEC07:
  .byte $5a
VgEC08:
  .byte $5b
VgEC09:
  .byte $68
VgEC0A:
  .byte $69
VgEC0B:
  .byte $6a
VgEC0C:
  .byte $6b
VgEC0D:
  .byte $51
VgEC0E:
  .byte $52
VgEC0F:
  .byte $01
VgEC10:
  .byte $60
VgEC11:
  .byte $23
VgEC12:
  .byte $77
VgEC13:
  .byte $00
VgEC14:
  .byte $5c
VgEC15:
  .byte $5d
VgEC16:
  .byte $5e
VgEC17:
  .byte $5f
VgEC18:
  .byte $6c
VgEC19:
  .byte $6d
VgEC1A:
  .byte $6e
VgEC1B:
  .byte $6f
VgEC1C:
  .byte $78
VgEC1D:
  .byte $79
VgEC1E:
  .byte $7a
VgEC1F:
  .byte $7b
VgEC20:
  .byte $08
VgEC21:
  .byte $70
VgEC22:
  .byte $71
VgEC23:
  .byte $01
VgEC24:
  .byte $01
VgEC25:
  .byte $7c
VgEC26:
  .byte $7d
VgEC27:
  .byte $7e
VgEC28:
  .byte $90
VgEC29:
  .byte $93
VgEC2A:
  .byte $96
VgEC2B:
  .byte $59
VgEC2C:
  .byte $5b
VgEC2D:
  .byte $5d
VgEC2E:
  .byte $5f
VgEC2F:
  .byte $61
VgEC30:
  .byte $63
VgEC31:
  .byte $a5
VgEC32:
  .byte $e8
VgEC33:
  .byte $ac
VgEC34:
  .byte $af
VgEC35:
  .byte $f2
VgEC36:
  .byte $f7
VgEC37:
  .byte $01
VgEC38:
  .byte $02
VgEC39:
  .byte $03
VgEC3A:
  .byte $04
VgEC3B:
  .byte $05
VgEC3C:
  .byte $06
VgEC3D:
  .byte $07
VgEC3E:
  .byte $08
VgEC3F:
  .byte $09
VgEC40:
  .byte $0a
VgEC41:
  .byte $0b
VgEC42:
  .byte $0c
VgEC43:
  .byte $0d
VgEC44:
  .byte $0e
VgEC45:
  .byte $0f
VgEC46:
  .byte $36
VgEC47:
  .byte $3b
VgEC48:
  TAX
VgEC49:
VgEC4A = *+1
VgEC4B = *+2
  JSR VgEBF0
VgEC4C:
VgEC4D = *+1
  STA ::VgAudioRam+$2f
VgEC4E:
  TXA
VgEC4F:
  PHA
VgEC50:
  TYA
VgEC51:
  PHA
VgEC52:
VgEC53 = *+1
  LDA ::VgAudioRam+$2f
VgEC54:
  ROL A
VgEC55:
  ROL A
VgEC56:
  ROL A
VgEC57:
VgEC58 = *+1
  AND #$03
VgEC59:
VgEC5A = *+1
  STA ::VgAudioRam+$30
VgEC5B:
VgEC5C = *+1
  LDA ::VgAudioRam+$2f
VgEC5D:
VgEC5E = *+1
  AND #$3f
VgEC5F:
VgEC60 = *+1
  STA ::VgAudioRam+$2f
VgEC61:
  ASL A
VgEC62:
  CLC
VgEC63:
VgEC64 = *+1
  ADC ::VgAudioRam+$2f
VgEC65:
  TAY
VgEC66:
VgEC67 = *+1
  STY ::VgAudioRam+$38
VgEC68:
VgEC69 = *+1
VgEC6A = *+2
  LDA VgEFFB,y
VgEC6B:
VgEC6C = *+1
  STA ::VgAudioRam+$31
VgEC6D:
  LSR A
VgEC6E:
  LSR A
VgEC6F:
  TAY
VgEC70:
VgEC71 = *+1
VgEC72 = *+2
  LDX VgECE0,y
VgEC73:
VgEC74 = *+1
  LDA ::VgAudioRam+$2f
VgEC75:
VgEC76 = *+1
  jeq VgEC7B
VgEC77:
VgEC78 = *+1
  CMP ::VgAudioRam-$ae,x
VgEC79:
VgEC7A = *+1
  jcc VgECC3
VgEC7B:
VgEC7C = *+1
  LDA #$00
VgEC7D:
VgEC7E = *+1
  STA ::VgAudioRam-$ae,x
VgEC7F:
VgEC80 = *+1
  LDY ::VgAudioRam+$38
VgEC81:
VgEC82 = *+1
VgEC83 = *+2
  LDA VgEFFC,y
VgEC84:
VgEC85 = *+1
  STA ::VgAudioRam-$ad,x
VgEC86:
VgEC87 = *+1
  STA $f6
VgEC88:
VgEC89 = *+1
VgEC8A = *+2
  LDA VgEFFD,y
VgEC8B:
VgEC8C = *+1
  STA ::VgAudioRam-$ac,x
VgEC8D:
VgEC8E = *+1
  STA $f7
VgEC8F:
VgEC90 = *+1
  LDY #$01
VgEC91:
VgEC92 = *+1
  php
  pha
  tya
  sta ::VgAudioRam-$b0,x
  pla
  plp
VgEC93:
  DEY
VgEC94:
VgEC95 = *+1
  php
  pha
  tya
  sta ::VgAudioRam-$aa,x
  pla
  plp
VgEC96:
VgEC97 = *+1
  CPX #$d2
VgEC98:
VgEC99 = *+1
  jeq VgECA0
VgEC9A:
VgEC9B = *+1
  php
  pha
  tya
  sta ::VgAudioRam-$a9,x
  pla
  plp
VgEC9C:
VgEC9D = *+1
  php
  pha
  tya
  sta ::VgAudioRam-$a4,x
  pla
  plp
VgEC9E:
VgEC9F = *+1
  php
  pha
  tya
  sta ::VgAudioRam-$a5,x
  pla
  plp
VgECA0:
VgECA1 = *+1
  LDA ($f6),Y
VgECA2:
VgECA3 = *+1
  jne VgECA6
VgECA4:
VgECA5 = *+1
  STA ::VgAudioRam+$2f
VgECA6:
VgECA7 = *+1
  AND #$f0
VgECA8:
VgECA9 = *+1
  CMP #$20
VgECAA:
VgECAB = *+1
  jeq VgECAD
VgECAC:
  INY
VgECAD:
VgECAE = *+1
  php
  pha
  tya
  sta ::VgAudioRam-$a7,x
  pla
  plp
VgECAF:
VgECB0 = *+1
  LDY ::VgAudioRam+$31
VgECB1:
VgECB2 = *+1
  LDA #$00
VgECB3:
VgECB4 = *+1
  CPY #$08
VgECB5:
VgECB6 = *+1
  jeq VgECB9
VgECB7:
VgECB8 = *+1
  LDA #$30
VgECB9:
VgECBA = *+1
VgECBB = *+2
  .if ::VG_RAW_APU
  STA $4000,y
.else
  jsr ::GuestNativeStoreSTA00Y
.endif
VgECBC:
VgECBD = *+1
VgECBE = *+2
  .if ::VG_RAW_APU
  STA $4001,y
.else
  jsr ::GuestNativeStoreSTA01Y
.endif
VgECBF:
VgECC0 = *+1
  LDA ::VgAudioRam+$2f
VgECC1:
VgECC2 = *+1
  STA ::VgAudioRam-$ae,x
VgECC3:
VgECC4 = *+1
  CPX #$c1
VgECC5:
VgECC6 = *+1
  jne VgECCF
VgECC7:
VgECC8 = *+1
  LDA #$00
VgECC9:
VgECCA = *+1
  STA ::VgAudioRam+$40
VgECCB:
VgECCC = *+1
  STA ::VgAudioRam+$41
VgECCD:
VgECCE = *+1
  STA ::VgAudioRam+$42
VgECCF:
VgECD0 = *+1
  DEC ::VgAudioRam+$30
VgECD1:
VgECD2 = *+1
  jmi VgECDB
VgECD3:
VgECD4 = *+1
  LDY ::VgAudioRam+$38
VgECD5:
  INY
VgECD6:
  INY
VgECD7:
  INY
VgECD8:
VgECD9 = *+1
VgECDA = *+2
  JMP VgEC66
VgECDB:
  PLA
VgECDC:
  TAY
VgECDD:
  PLA
VgECDE:
  TAX
VgECDF:
  RTS
VgECE0:
  .byte $b0
VgECE1:
  .byte $c1
VgECE2:
  .byte $d2
VgECE3:
  .byte $e3
VgECE4:
  TYA
VgECE5:
VgECE6 = *+1
  php
  pha
  tya
  sta ::VgAudioRam-$ae,x
  pla
  plp
VgECE7:
VgECE8 = *+1
  CPX #$d2
VgECE9:
VgECEA = *+1
  jeq VgECEF
VgECEB:
VgECEC = *+1
  php
  pha
  tya
  sta ::VgAudioRam-$a4,x
  pla
  plp
VgECED:
VgECEE = *+1
  LDA #$30
VgECEF:
VgECF0 = *+1
  LDX ::VgAudioRam+$49
VgECF1:
VgECF2 = *+1
VgECF3 = *+2
  .if ::VG_RAW_APU
  STA $4000,x
.else
  jsr ::GuestNativeStoreSTA00X
.endif
VgECF4:
  RTS
VgECF5:
  INY
VgECF6:
VgECF7 = *+1
  LDA ($fa),Y
VgECF8:
VgECF9 = *+1
  STA ::VgAudioRam-$ad,x
VgECFA:
  INY
VgECFB:
VgECFC = *+1
  LDA ($fa),Y
VgECFD:
VgECFE = *+1
  STA ::VgAudioRam-$ac,x
VgECFF:
  RTS
VgED00:
VgED01 = *+1
  LDA #$00
VgED02:
VgED03 = *+1
  STA ::VgAudioRam-$aa,x
VgED04:
  INY
VgED05:
  INY
VgED06:
  INY
VgED07:
  TYA
VgED08:
  CLC
VgED09:
VgED0A = *+1
  ADC $fa
VgED0B:
VgED0C = *+1
  STA ::VgAudioRam-$ad,x
VgED0D:
VgED0E = *+1
  LDA #$00
VgED0F:
VgED10 = *+1
  ADC $fb
VgED11:
VgED12 = *+1
  STA ::VgAudioRam-$ac,x
VgED13:
VgED14 = *+1
  LDA #$01
VgED15:
VgED16 = *+1
  STA ::VgAudioRam-$b0,x
VgED17:
VgED18 = *+1
  jne VgED74
VgED19:
VgED1A = *+1
  LDA ::VgAudioRam-$aa,x
VgED1B:
  CLC
VgED1C:
VgED1D = *+1
  ADC #$01
VgED1E:
  INY
VgED1F:
VgED20 = *+1
  CMP ($fa),Y
VgED21:
VgED22 = *+1
  jeq VgED00
VgED23:
VgED24 = *+1
  jmi VgED28
VgED25:
  SEC
VgED26:
VgED27 = *+1
  SBC #$01
VgED28:
VgED29 = *+1
  STA ::VgAudioRam-$aa,x
VgED2A:
VgED2B = *+1
VgED2C = *+2
  JSR VgECF5
VgED2D:
VgED2E = *+1
VgED2F = *+2
  JMP VgED13
VgED30:
VgED31 = *+1
  LDX #$b0
VgED32:
VgED33 = *+1
  LDY #$00
VgED34:
VgED35 = *+1
  STX ::VgAudioRam+$48
VgED36:
VgED37 = *+1
  STY ::VgAudioRam+$49
VgED38:
VgED39 = *+1
  LDA ::VgAudioRam-$ae,x
VgED3A:
VgED3B = *+1
  jeq VgED3F
VgED3C:
VgED3D = *+1
VgED3E = *+2
  JSR VgED74
VgED3F:
VgED40 = *+1
  LDA ::VgAudioRam+$48
VgED41:
  CLC
VgED42:
VgED43 = *+1
  ADC #$11
VgED44:
VgED45 = *+1
  CMP #$f4
VgED46:
VgED47 = *+1
  jne VgED6B
VgED48:
VgED49 = *+1
  LDA ::VgAudioRam+$40
VgED4A:
VgED4B = *+1
  jeq VgED6A
VgED4C:
VgED4D = *+1
  INC ::VgAudioRam+$41
VgED4E:
VgED4F = *+1
  LDA ::VgAudioRam+$41
VgED50:
VgED51 = *+1
  CMP #$30
VgED52:
VgED53 = *+1
  jne VgED6A
VgED54:
VgED55 = *+1
  INC ::VgAudioRam+$42
VgED56:
VgED57 = *+1
  LDA #$00
VgED58:
VgED59 = *+1
  STA ::VgAudioRam+$41
VgED5A:
VgED5B = *+1
  LDA ::VgAudioRam+$43
VgED5C:
VgED5D = *+1
  CMP #$07
VgED5E:
VgED5F = *+1
  jpl VgED6A
VgED60:
VgED61 = *+1
  LDA #$00
VgED62:
VgED63 = *+1
  STA ::VgAudioRam+$24
VgED64:
VgED65 = *+1
VgED66 = *+2
  .if ::VG_RAW_APU
  STA $4008
.else
  jsr ::VgNativeStoreSTA08
.endif
VgED67:
VgED68 = *+1
VgED69 = *+2
  .if ::VG_RAW_APU
  STA $4009
.else
  jsr ::VgNativeStoreSTA09
.endif
VgED6A:
  RTS
VgED6B:
  TAX
VgED6C:
VgED6D = *+1
  LDA ::VgAudioRam+$49
VgED6E:
  CLC
VgED6F:
VgED70 = *+1
  ADC #$04
VgED71:
  TAY
VgED72:
VgED73 = *+1
  jcc VgED34
VgED74:
VgED75 = *+1
  LDY #$00
VgED76:
VgED77 = *+1
  LDA ::VgAudioRam-$ad,x
VgED78:
VgED79 = *+1
  STA $fa
VgED7A:
VgED7B = *+1
  LDA ::VgAudioRam-$ac,x
VgED7C:
VgED7D = *+1
  STA $fb
VgED7E:
VgED7F = *+1
  DEC ::VgAudioRam-$b0,x
VgED80:
VgED81 = *+1
  jeq VgEDA5
VgED82:
VgED83 = *+1
  LDA $15
VgED84:
VgED85 = *+1
  jeq VgEDA2
VgED86:
VgED87 = *+1
  LDA ::VgAudioRam-$ae,x
VgED88:
VgED89 = *+1
  CMP #$3b
VgED8A:
VgED8B = *+1
  jeq VgEDA2
VgED8C:
VgED8D = *+1
  INC ::VgAudioRam-$b0,x
VgED8E:
  TYA
VgED8F:
VgED90 = *+1
  STA ::VgAudioRam-$a9,x
VgED91:
VgED92 = *+1
  LDX ::VgAudioRam+$49
VgED93:
VgED94 = *+1
VgED95 = *+2
  .if ::VG_RAW_APU
  STA $4002,x
.else
  jsr ::GuestNativeStoreSTA02X
.endif
VgED96:
VgED97 = *+1
VgED98 = *+2
  .if ::VG_RAW_APU
  STA $4003,x
.else
  jsr ::GuestNativeStoreSTA03X
.endif
VgED99:
VgED9A = *+1
VgED9B = *+2
  .if ::VG_RAW_APU
  STA $4008
.else
  jsr ::VgNativeStoreSTA08
.endif
VgED9C:
VgED9D = *+1
  LDA #$30
VgED9E:
VgED9F = *+1
VgEDA0 = *+2
  .if ::VG_RAW_APU
  STA $400c
.else
  jsr ::VgNativeStoreSTA0c
.endif
VgEDA1:
  RTS
VgEDA2:
VgEDA3 = *+1
VgEDA4 = *+2
  JMP VgEE63
VgEDA5:
VgEDA6 = *+1
  LDA ($fa),Y
VgEDA7:
VgEDA8 = *+1
  CMP #$fd
VgEDA9:
VgEDAA = *+1
  jcc VgEDE3
VgEDAB:
VgEDAC = *+1
  jne VgEDC6
VgEDAD:
VgEDAE = *+1
  LDA ::VgAudioRam-$a7,x
VgEDAF:
VgEDB0 = *+1
  ORA #$80
VgEDB1:
VgEDB2 = *+1
  STA ::VgAudioRam-$a7,x
VgEDB3:
VgEDB4 = *+1
VgEDB5 = *+2
  JSR VgECF5
VgEDB6:
  INY
VgEDB7:
  TYA
VgEDB8:
  CLC
VgEDB9:
VgEDBA = *+1
  ADC $fa
VgEDBB:
VgEDBC = *+1
  STA $dd
VgEDBD:
VgEDBE = *+1
  LDA #$00
VgEDBF:
VgEDC0 = *+1
  ADC $fb
VgEDC1:
VgEDC2 = *+1
  STA $de
VgEDC3:
VgEDC4 = *+1
VgEDC5 = *+2
  JMP VgED13
VgEDC6:
VgEDC7 = *+1
  CMP #$fe
VgEDC8:
VgEDC9 = *+1
  jne VgEDCD
VgEDCA:
VgEDCB = *+1
VgEDCC = *+2
  JMP VgED19
VgEDCD:
VgEDCE = *+1
  LDA ::VgAudioRam-$a7,x
VgEDCF:
VgEDD0 = *+1
  jmi VgEDD4
VgEDD1:
VgEDD2 = *+1
VgEDD3 = *+2
  JMP VgECE4
VgEDD4:
VgEDD5 = *+1
  AND #$7f
VgEDD6:
VgEDD7 = *+1
  STA ::VgAudioRam-$a7,x
VgEDD8:
VgEDD9 = *+1
  LDA $dd
VgEDDA:
VgEDDB = *+1
  STA ::VgAudioRam-$ad,x
VgEDDC:
VgEDDD = *+1
  LDA $de
VgEDDE:
VgEDDF = *+1
  STA ::VgAudioRam-$ac,x
VgEDE0:
VgEDE1 = *+1
VgEDE2 = *+2
  JMP VgED13
VgEDE3:
VgEDE4 = *+1
  LDA ::VgAudioRam-$a7,x
VgEDE5:
VgEDE6 = *+1
  AND #$7f
VgEDE7:
VgEDE8 = *+1
  jeq VgEDEC
VgEDE9:
VgEDEA = *+1
VgEDEB = *+2
  JMP VgEEB0
VgEDEC:
VgEDED = *+1
  LDA ($fa),Y
VgEDEE:
VgEDEF = *+1
  AND #$f0
VgEDF0:
VgEDF1 = *+1
  CMP #$20
VgEDF2:
VgEDF3 = *+1
  jne VgEE07
VgEDF4:
VgEDF5 = *+1
  LDA ($fa),Y
VgEDF6:
VgEDF7 = *+1
  AND #$0f
VgEDF8:
VgEDF9 = *+1
  STA ::VgAudioRam-$af,x
VgEDFA:
  INY
VgEDFB:
VgEDFC = *+1
  LDA ($fa),Y
VgEDFD:
VgEDFE = *+1
  LDX ::VgAudioRam+$49
VgEDFF:
VgEE00 = *+1
VgEE01 = *+2
  .if ::VG_RAW_APU
  STA $4000,x
.else
  jsr ::GuestNativeStoreSTA00X
.endif
VgEE02:
VgEE03 = *+1
  LDX ::VgAudioRam+$48
VgEE04:
VgEE05 = *+1
  STA ::VgAudioRam-$a8,x
VgEE06:
  INY
VgEE07:
VgEE08 = *+1
  LDA ::VgAudioRam-$af,x
VgEE09:
VgEE0A = *+1
  STA ::VgAudioRam-$b0,x
VgEE0B:
VgEE0C = *+1
  CPX #$d2
VgEE0D:
VgEE0E = *+1
  jeq VgEE50
VgEE0F:
VgEE10 = *+1
  LDA ($fa),Y
VgEE11:
VgEE12 = *+1
  CMP #$11
VgEE13:
VgEE14 = *+1
  jne VgEE1D
VgEE15:
  INY
VgEE16:
VgEE17 = *+1
  LDA ($fa),Y
VgEE18:
VgEE19 = *+1
  STA ::VgAudioRam-$a4,x
VgEE1A:
  INY
VgEE1B:
VgEE1C = *+1
  jne VgEDEC
VgEE1D:
VgEE1E = *+1
  CMP #$10
VgEE1F:
VgEE20 = *+1
  jne VgEE2E
VgEE21:
  INY
VgEE22:
VgEE23 = *+1
  LDA ($fa),Y
VgEE24:
  INY
VgEE25:
VgEE26 = *+1
  LDX ::VgAudioRam+$49
VgEE27:
VgEE28 = *+1
VgEE29 = *+2
  .if ::VG_RAW_APU
  STA $4001,x
.else
  jsr ::GuestNativeStoreSTA01X
.endif
VgEE2A:
VgEE2B = *+1
  LDX ::VgAudioRam+$48
VgEE2C:
VgEE2D = *+1
  STA ::VgAudioRam-$a5,x
VgEE2E:
VgEE2F = *+1
  LDA ::VgAudioRam-$a8,x
VgEE30:
VgEE31 = *+1
  AND #$10
VgEE32:
VgEE33 = *+1
  jeq VgEE50
VgEE34:
VgEE35 = *+1
  LDA ::VgAudioRam-$a8,x
VgEE36:
VgEE37 = *+1
  AND #$f0
VgEE38:
VgEE39 = *+1
  STA ::VgAudioRam-$a8,x
VgEE3A:
VgEE3B = *+1
  LDA ($fa),Y
VgEE3C:
VgEE3D = *+1
  CMP #$f8
VgEE3E:
VgEE3F = *+1
  jne VgEE43
VgEE40:
  INY
VgEE41:
VgEE42 = *+1
  LDA ($fa),Y
VgEE43:
  LSR A
VgEE44:
  LSR A
VgEE45:
  LSR A
VgEE46:
  LSR A
VgEE47:
VgEE48 = *+1
  ORA ::VgAudioRam-$a8,x
VgEE49:
VgEE4A = *+1
  STA ::VgAudioRam-$a8,x
VgEE4B:
VgEE4C = *+1
  LDX ::VgAudioRam+$49
VgEE4D:
VgEE4E = *+1
VgEE4F = *+2
  .if ::VG_RAW_APU
  STA $4000,x
.else
  jsr ::GuestNativeStoreSTA00X
.endif
VgEE50:
VgEE51 = *+1
  LDA ($fa),Y
VgEE52:
VgEE53 = *+1
  AND #$07
VgEE54:
VgEE55 = *+1
  STA ::VgAudioRam+$44
VgEE56:
  INY
VgEE57:
VgEE58 = *+1
  LDA ($fa),Y
VgEE59:
VgEE5A = *+1
  STA ::VgAudioRam+$45
VgEE5B:
VgEE5C = *+1
  LDX ::VgAudioRam+$48
VgEE5D:
VgEE5E = *+1
VgEE5F = *+2
  JSR VgEF90
VgEE60:
VgEE61 = *+1
VgEE62 = *+2
  JMP VgEFD4
VgEE63:
VgEE64 = *+1
  LDA ::VgAudioRam-$a7,x
VgEE65:
VgEE66 = *+1
  AND #$7f
VgEE67:
VgEE68 = *+1
  jne VgEE6A
VgEE69:
  RTS
VgEE6A:
VgEE6B = *+1
  CPX #$d2
VgEE6C:
VgEE6D = *+1
  jne VgEE6F
VgEE6E:
  RTS
VgEE6F:
VgEE70 = *+1
  LDA $fa
VgEE71:
VgEE72 = *+1
  jne VgEE75
VgEE73:
VgEE74 = *+1
  DEC $fb
VgEE75:
VgEE76 = *+1
  DEC $fa
VgEE77:
VgEE78 = *+1
  LDY #$00
VgEE79:
VgEE7A = *+1
  LDA ($fa),Y
VgEE7B:
VgEE7C = *+1
  AND #$f0
VgEE7D:
VgEE7E = *+1
  CMP #$c0
VgEE7F:
VgEE80 = *+1
  jne VgEE82
VgEE81:
  RTS
VgEE82:
VgEE83 = *+1
  LDA ::VgAudioRam-$a3,x
VgEE84:
  SEC
VgEE85:
VgEE86 = *+1
  SBC #$01
VgEE87:
VgEE88 = *+1
  STA ::VgAudioRam-$a3,x
VgEE89:
VgEE8A = *+1
  CMP ::VgAudioRam-$b0,x
VgEE8B:
VgEE8C = *+1
  jne VgEE95
VgEE8D:
  SEC
VgEE8E:
VgEE8F = *+1
  SBC ::VgAudioRam-$a1,x
VgEE90:
VgEE91 = *+1
  jcc VgEE9A
VgEE92:
VgEE93 = *+1
  jeq VgEE9A
VgEE94:
  RTS
VgEE95:
  SEC
VgEE96:
VgEE97 = *+1
  SBC #$01
VgEE98:
VgEE99 = *+1
  STA ::VgAudioRam-$a3,x
VgEE9A:
VgEE9B = *+1
  LDA ::VgAudioRam-$a8,x
VgEE9C:
VgEE9D = *+1
  AND #$0f
VgEE9E:
  SEC
VgEE9F:
VgEEA0 = *+1
  SBC #$01
VgEEA1:
VgEEA2 = *+1
  jpl VgEEA4
VgEEA3:
  RTS
VgEEA4:
VgEEA5 = *+1
  LDA ::VgAudioRam-$a8,x
VgEEA6:
VgEEA7 = *+1
  SBC #$01
VgEEA8:
VgEEA9 = *+1
  STA ::VgAudioRam-$a8,x
VgEEAA:
VgEEAB = *+1
  LDX ::VgAudioRam+$49
VgEEAC:
VgEEAD = *+1
VgEEAE = *+2
  .if ::VG_RAW_APU
  STA $4000,x
.else
  jsr ::GuestNativeStoreSTA00X
.endif
VgEEAF:
  RTS
VgEEB0:
VgEEB1 = *+1
  LDA $15
VgEEB2:
VgEEB3 = *+1
  jeq VgEEB7
VgEEB4:
VgEEB5 = *+1
VgEEB6 = *+2
  JMP VgED8C
VgEEB7:
VgEEB8 = *+1
  LDA ($fa),Y
VgEEB9:
VgEEBA = *+1
  AND #$f0
VgEEBB:
VgEEBC = *+1
  CMP #$d0
VgEEBD:
VgEEBE = *+1
  jne VgEEE1
VgEEBF:
VgEEC0 = *+1
  LDA ($fa),Y
VgEEC1:
VgEEC2 = *+1
  AND #$0f
VgEEC3:
VgEEC4 = *+1
  STA ::VgAudioRam-$a6,x
VgEEC5:
  INY
VgEEC6:
VgEEC7 = *+1
  LDA ($fa),Y
VgEEC8:
VgEEC9 = *+1
  STA ::VgAudioRam-$ab,x
VgEECA:
  INY
VgEECB:
VgEECC = *+1
  CPX #$d2
VgEECD:
VgEECE = *+1
  jne VgEED2
VgEECF:
VgEED0 = *+1
VgEED1 = *+2
  JMP VgEDA5
VgEED2:
VgEED3 = *+1
  LDA ($fa),Y
VgEED4:
  LSR A
VgEED5:
  LSR A
VgEED6:
  LSR A
VgEED7:
  LSR A
VgEED8:
VgEED9 = *+1
  STA ::VgAudioRam-$a2,x
VgEEDA:
VgEEDB = *+1
  LDA ($fa),Y
VgEEDC:
VgEEDD = *+1
  AND #$0f
VgEEDE:
VgEEDF = *+1
  STA ::VgAudioRam-$a1,x
VgEEE0:
  INY
VgEEE1:
VgEEE2 = *+1
  LDA ($fa),Y
VgEEE3:
VgEEE4 = *+1
  AND #$f0
VgEEE5:
VgEEE6 = *+1
  CMP #$e0
VgEEE7:
VgEEE8 = *+1
  jne VgEEF0
VgEEE9:
VgEEEA = *+1
  LDA ($fa),Y
VgEEEB:
VgEEEC = *+1
  AND #$0f
VgEEED:
VgEEEE = *+1
  STA ::VgAudioRam-$a0,x
VgEEEF:
  INY
VgEEF0:
VgEEF1 = *+1
VgEEF2 = *+2
  JSR VgEFD4
VgEEF3:
  DEY
VgEEF4:
VgEEF5 = *+1
  LDA ($fa),Y
VgEEF6:
VgEEF7 = *+1
  AND #$0f
VgEEF8:
VgEEF9 = *+1
  STA ::VgAudioRam+$44
VgEEFA:
VgEEFB = *+1
  jeq VgEF07
VgEEFC:
VgEEFD = *+1
  LDA ::VgAudioRam-$a6,x
VgEEFE:
  CLC
VgEEFF:
VgEF00 = *+1
  ADC ::VgAudioRam-$a6,x
VgEF01:
VgEF02 = *+1
  DEC ::VgAudioRam+$44
VgEF03:
VgEF04 = *+1
  jne VgEEFF
VgEF05:
VgEF06 = *+1
  jeq VgEF09
VgEF07:
VgEF08 = *+1
  LDA ::VgAudioRam-$a6,x
VgEF09:
VgEF0A = *+1
  STA ::VgAudioRam-$b0,x
VgEF0B:
VgEF0C = *+1
  CPX #$d2
VgEF0D:
VgEF0E = *+1
  jeq VgEF54
VgEF0F:
  CLC
VgEF10:
VgEF11 = *+1
  ADC ::VgAudioRam-$a2,x
VgEF12:
VgEF13 = *+1
  STA ::VgAudioRam-$a3,x
VgEF14:
VgEF15 = *+1
  LDA ::VgAudioRam+$40
VgEF16:
VgEF17 = *+1
  jeq VgEF54
VgEF18:
VgEF19 = *+1
  CPX #$c1
VgEF1A:
VgEF1B = *+1
  jne VgEF54
VgEF1C:
VgEF1D = *+1
  LDA ::VgAudioRam+$42
VgEF1E:
VgEF1F = *+1
  CMP #$0b
VgEF20:
VgEF21 = *+1
  jcc VgEF26
VgEF22:
VgEF23 = *+1
  LDA #$0b
VgEF24:
VgEF25 = *+1
  STA ::VgAudioRam+$42
VgEF26:
VgEF27 = *+1
  LDA #$06
VgEF28:
VgEF29 = *+1
  STA ::VgAudioRam-$a2,x
VgEF2A:
VgEF2B = *+1
  LDA ::VgAudioRam+$13
VgEF2C:
VgEF2D = *+1
  CMP #$13
VgEF2E:
VgEF2F = *+1
  jne VgEF34
VgEF30:
VgEF31 = *+1
  LDA #$0d
VgEF32:
VgEF33 = *+1
  jne VgEF36
VgEF34:
VgEF35 = *+1
  LDA #$05
VgEF36:
VgEF37 = *+1
  STA ::VgAudioRam-$a1,x
VgEF38:
VgEF39 = *+1
  LDA ::VgAudioRam-$b0,x
VgEF3A:
  CLC
VgEF3B:
VgEF3C = *+1
  ADC ::VgAudioRam-$a2,x
VgEF3D:
VgEF3E = *+1
  STA ::VgAudioRam-$a3,x
VgEF3F:
VgEF40 = *+1
  LDA ::VgAudioRam-$ab,x
VgEF41:
VgEF42 = *+1
  AND #$0f
VgEF43:
  SEC
VgEF44:
VgEF45 = *+1
  SBC ::VgAudioRam+$42
VgEF46:
VgEF47 = *+1
  jpl VgEF4A
VgEF48:
VgEF49 = *+1
  LDA #$00
VgEF4A:
VgEF4B = *+1
  STA ::VgAudioRam+$43
VgEF4C:
VgEF4D = *+1
  LDA ::VgAudioRam-$ab,x
VgEF4E:
VgEF4F = *+1
  AND #$f0
VgEF50:
VgEF51 = *+1
  ORA ::VgAudioRam+$43
VgEF52:
VgEF53 = *+1
  jne VgEF56
VgEF54:
VgEF55 = *+1
  LDA ::VgAudioRam-$ab,x
VgEF56:
VgEF57 = *+1
  STA ::VgAudioRam-$a8,x
VgEF58:
VgEF59 = *+1
  LDX ::VgAudioRam+$49
VgEF5A:
VgEF5B = *+1
VgEF5C = *+2
  .if ::VG_RAW_APU
  STA $4000,x
.else
  jsr ::GuestNativeStoreSTA00X
.endif
VgEF5D:
VgEF5E = *+1
  LDA ($fa),Y
VgEF5F:
  LSR A
VgEF60:
  LSR A
VgEF61:
  LSR A
VgEF62:
  LSR A
VgEF63:
VgEF64 = *+1
  CMP #$0c
VgEF65:
VgEF66 = *+1
  jne VgEF73
VgEF67:
VgEF68 = *+1
  LDA #$00
VgEF69:
VgEF6A = *+1
  CPX #$08
VgEF6B:
VgEF6C = *+1
  jeq VgEF6F
VgEF6D:
VgEF6E = *+1
  LDA #$30
VgEF6F:
VgEF70 = *+1
VgEF71 = *+2
  .if ::VG_RAW_APU
  STA $4000,x
.else
  jsr ::GuestNativeStoreSTA00X
.endif
VgEF72:
  RTS
VgEF73:
VgEF74 = *+1
  LDX ::VgAudioRam+$48
VgEF75:
  ASL A
VgEF76:
  TAY
VgEF77:
VgEF78 = *+1
VgEF79 = *+2
  LDA VgEFE6,y
VgEF7A:
VgEF7B = *+1
  STA ::VgAudioRam+$44
VgEF7C:
  INY
VgEF7D:
VgEF7E = *+1
VgEF7F = *+2
  LDA VgEFE6,y
VgEF80:
VgEF81 = *+1
  STA ::VgAudioRam+$45
VgEF82:
VgEF83 = *+1
  LDY ::VgAudioRam-$a0,x
VgEF84:
  TYA
VgEF85:
VgEF86 = *+1
  CMP #$04
VgEF87:
VgEF88 = *+1
  jeq VgEF90
VgEF89:
VgEF8A = *+1
  LSR ::VgAudioRam+$44
VgEF8B:
VgEF8C = *+1
  ROR ::VgAudioRam+$45
VgEF8D:
  INY
VgEF8E:
VgEF8F = *+1
  jne VgEF84
VgEF90:
VgEF91 = *+1
  CPX #$d2
VgEF92:
VgEF93 = *+1
  jcs VgEFA9
VgEF94:
VgEF95 = *+1
  LDA ::VgAudioRam+$44
VgEF96:
VgEF97 = *+1
  jne VgEF9C
VgEF98:
VgEF99 = *+1
  LDA ::VgAudioRam+$45
VgEF9A:
VgEF9B = *+1
  jeq VgEFA9
VgEF9C:
VgEF9D = *+1
  LDA ::VgAudioRam-$a4,x
VgEF9E:
VgEF9F = *+1
  jeq VgEFA9
VgEFA0:
  CLC
VgEFA1:
VgEFA2 = *+1
  ADC ::VgAudioRam+$45
VgEFA3:
VgEFA4 = *+1
  STA ::VgAudioRam+$45
VgEFA5:
VgEFA6 = *+1
  jcc VgEFA9
VgEFA7:
VgEFA8 = *+1
  INC ::VgAudioRam+$44
VgEFA9:
VgEFAA = *+1
  LDA ::VgAudioRam+$44
VgEFAB:
VgEFAC = *+1
  ORA #$08
VgEFAD:
VgEFAE = *+1
  STA ::VgAudioRam+$44
VgEFAF:
VgEFB0 = *+1
  CPX #$d2
VgEFB1:
VgEFB2 = *+1
  jeq VgEFC5
VgEFB3:
VgEFB4 = *+1
  CMP ::VgAudioRam-$a9,x
VgEFB5:
VgEFB6 = *+1
  jne VgEFC3
VgEFB7:
VgEFB8 = *+1
  LDA ::VgAudioRam-$a8,x
VgEFB9:
VgEFBA = *+1
  AND #$10
VgEFBB:
VgEFBC = *+1
  jeq VgEFC5
VgEFBD:
VgEFBE = *+1
  LDA ::VgAudioRam-$a5,x
VgEFBF:
VgEFC0 = *+1
  jne VgEFC5
VgEFC1:
VgEFC2 = *+1
  jeq VgEFCC
VgEFC3:
VgEFC4 = *+1
  STA ::VgAudioRam-$a9,x
VgEFC5:
VgEFC6 = *+1
  LDA ::VgAudioRam+$44
VgEFC7:
VgEFC8 = *+1
  LDX ::VgAudioRam+$49
VgEFC9:
VgEFCA = *+1
VgEFCB = *+2
  .if ::VG_RAW_APU
  STA $4003,x
.else
  jsr ::GuestNativeStoreSTA03X
.endif
VgEFCC:
VgEFCD = *+1
  LDX ::VgAudioRam+$49
VgEFCE:
VgEFCF = *+1
  LDA ::VgAudioRam+$45
VgEFD0:
VgEFD1 = *+1
VgEFD2 = *+2
  .if ::VG_RAW_APU
  STA $4002,x
.else
  jsr ::GuestNativeStoreSTA02X
.endif
VgEFD3:
  RTS
VgEFD4:
  INY
VgEFD5:
  TYA
VgEFD6:
  CLC
VgEFD7:
VgEFD8 = *+1
  ADC $fa
VgEFD9:
VgEFDA = *+1
  LDX ::VgAudioRam+$48
VgEFDB:
VgEFDC = *+1
  STA ::VgAudioRam-$ad,x
VgEFDD:
VgEFDE = *+1
  jcc VgEFE5
VgEFDF:
VgEFE0 = *+1
  LDA $fb
VgEFE1:
VgEFE2 = *+1
  ADC #$00
VgEFE3:
VgEFE4 = *+1
  STA ::VgAudioRam-$ac,x
VgEFE5:
  RTS
VgEFE6:
  .byte $06
VgEFE7:
  .byte $ae
VgEFE8:
  .byte $06
VgEFE9:
  .byte $4e
VgEFEA:
  .byte $05
VgEFEB:
  .byte $f4
VgEFEC:
  .byte $05
VgEFED:
  .byte $9e
VgEFEE:
  .byte $05
VgEFEF:
  .byte $4e
VgEFF0:
  .byte $05
VgEFF1:
  .byte $01
VgEFF2:
  .byte $04
VgEFF3:
  .byte $b9
VgEFF4:
  .byte $04
VgEFF5:
  .byte $76
VgEFF6:
  .byte $04
VgEFF7:
  .byte $36
VgEFF8:
  .byte $03
VgEFF9:
  .byte $f9
VgEFFA:
  .byte $03
VgEFFB:
  .byte $c0
VgEFFC:
  .byte $03
VgEFFD:
  .byte $8a
VgEFFE:
  .byte $00
VgEFFF:
VgF000 = *+1
  .word VgF0D6
VgF001:
  .byte $00
VgF002:
VgF003 = *+1
  .word VgF0E5
VgF004:
  .byte $00
VgF005:
VgF006 = *+1
  .word VgF0F0
VgF007:
  .byte $00
VgF008:
VgF009 = *+1
  .word VgF0FB
VgF00A:
  .byte $00
VgF00B:
VgF00C = *+1
  .word VgF118
VgF00D:
  .byte $00
VgF00E:
VgF00F = *+1
  .word VgF127
VgF010:
  .byte $00
VgF011:
VgF012 = *+1
  .word VgF148
VgF013:
  .byte $00
VgF014:
VgF015 = *+1
  .word VgF16B
VgF016:
  .byte $00
VgF017:
VgF018 = *+1
  .word VgF178
VgF019:
  .byte $00
VgF01A:
VgF01B = *+1
  .word VgF185
VgF01C:
  .byte $00
VgF01D:
VgF01E = *+1
  .word VgF194
VgF01F:
  .byte $00
VgF020:
VgF021 = *+1
  .word VgF1A9
VgF022:
  .byte $00
VgF023:
VgF024 = *+1
  .word VgF1DE
VgF025:
  .byte $00
VgF026:
VgF027 = *+1
  .word VgF20F
VgF028:
  .byte $0c
VgF029:
VgF02A = *+1
  .word VgF25F
VgF02B:
  .byte $00
VgF02C:
VgF02D = *+1
  .word VgFE16
VgF02E:
  .byte $04
VgF02F:
VgF030 = *+1
  .word VgFE24
VgF031:
  .byte $08
VgF032:
VgF033 = *+1
  .word VgFE30
VgF034:
  .byte $00
VgF035:
VgF036 = *+1
  .word VgF3C4
VgF037:
  .byte $04
VgF038:
VgF039 = *+1
  .word VgF3DF
VgF03A:
  .byte $08
VgF03B:
VgF03C = *+1
  .word VgF454
VgF03D:
  .byte $00
VgF03E:
VgF03F = *+1
  .word VgFB35
VgF040:
  .byte $04
VgF041:
VgF042 = *+1
  .word VgFB8C
VgF043:
  .byte $08
VgF044:
VgF045 = *+1
  .word VgFC06
VgF046:
  .byte $04
VgF047:
VgF048 = *+1
  .word VgF4C9
VgF049:
  .byte $08
VgF04A:
VgF04B = *+1
  .word VgF5BA
VgF04C:
  .byte $04
VgF04D:
VgF04E = *+1
  .word VgF652
VgF04F:
  .byte $08
VgF050:
VgF051 = *+1
  .word VgF6B9
VgF052:
  .byte $04
VgF053:
VgF054 = *+1
  .word VgF7AC
VgF055:
  .byte $08
VgF056:
VgF057 = *+1
  .word VgF82E
VgF058:
  .byte $04
VgF059:
VgF05A = *+1
  .word VgFA3A
VgF05B:
  .byte $08
VgF05C:
VgF05D = *+1
  .word VgFADE
VgF05E:
  .byte $04
VgF05F:
VgF060 = *+1
  .word VgF8AB
VgF061:
  .byte $08
VgF062:
VgF063 = *+1
  .word VgF94D
VgF064:
  .byte $04
VgF065:
VgF066 = *+1
  .word VgFC94
VgF067:
  .byte $08
VgF068:
VgF069 = *+1
  .word VgFD07
VgF06A:
  .byte $00
VgF06B:
VgF06C = *+1
  .word VgFD99
VgF06D:
  .byte $04
VgF06E:
VgF06F = *+1
  .word VgFDAC
VgF070:
  .byte $08
VgF071:
VgF072 = *+1
  .word VgFDF9
VgF073:
  .byte $00
VgF074:
VgF075 = *+1
  .word VgFE87
VgF076:
  .byte $04
VgF077:
VgF078 = *+1
  .word VgFEB1
VgF079:
  .byte $08
VgF07A:
VgF07B = *+1
  .word VgFED9
VgF07C:
  .byte $0c
VgF07D:
VgF07E = *+1
  .word VgFE3D
VgF07F:
  .byte $00
VgF080:
VgF081 = *+1
  .word VgF27B
VgF082:
  .byte $04
VgF083:
VgF084 = *+1
  .word VgF27F
VgF085:
  .byte $08
VgF086:
VgF087 = *+1
  .word VgF302
VgF088:
  .byte $00
VgF089:
VgF08A = *+1
  .word VgF718
VgF08B:
  .byte $04
VgF08C:
VgF08D = *+1
  .word VgF74A
VgF08E:
  .byte $08
VgF08F:
VgF090 = *+1
  .word VgF77F
VgF091:
  .byte $00
VgF092:
VgF093 = *+1
  .word VgFF69
VgF094:
  .byte $04
VgF095:
VgF096 = *+1
  .word VgFF9F
VgF097:
  .byte $08
VgF098:
VgF099 = *+1
  .word VgFFCF
VgF09A:
  .byte $0c
VgF09B:
VgF09C = *+1
  .word VgFF5E
VgF09D:
  .byte $00
VgF09E:
VgF09F = *+1
  .word VgF240
VgF0A0:
  .byte $00
VgF0A1:
VgF0A2 = *+1
  .word VgF303
VgF0A3:
  .byte $04
VgF0A4:
VgF0A5 = *+1
  .word VgF307
VgF0A6:
  .byte $08
VgF0A7:
VgF0A8 = *+1
  .word VgF37E
VgF0A9:
  .byte $0c
VgF0AA:
VgF0AB = *+1
  .word VgF3BF
VgF0AC:
  .byte $00
VgF0AD:
VgF0AE = *+1
  .word VgF0BB
VgF0AF:
  .byte $00
VgF0B0:
  .byte $bd
VgF0B1:
  .byte $f0
VgF0B2:
  .byte $04
VgF0B3:
  .byte $bd
VgF0B4:
  .byte $f0
VgF0B5:
  .byte $08
VgF0B6:
  .byte $bd
VgF0B7:
  .byte $f0
VgF0B8:
  .byte $0c
VgF0B9:
  .byte $bd
VgF0BA:
  .byte $f0
VgF0BB:
  .byte $25
VgF0BC:
  .byte $82
VgF0BD:
  .byte $00
VgF0BE:
  .byte $d5
VgF0BF:
  .byte $00
VgF0C0:
  .byte $8e
VgF0C1:
  .byte $00
VgF0C2:
  .byte $a9
VgF0C3:
  .byte $22
VgF0C4:
  .byte $b0
VgF0C5:
  .byte $e0
VgF0C6:
  .byte $6a
VgF0C7:
  .byte $d0
VgF0C8:
  .byte $6a
VgF0C9:
  .byte $b0
VgF0CA:
  .byte $6a
VgF0CB:
  .byte $a0
VgF0CC:
  .byte $6a
VgF0CD:
  .byte $90
VgF0CE:
  .byte $6a
VgF0CF:
  .byte $70
VgF0D0:
  .byte $6a
VgF0D1:
  .byte $50
VgF0D2:
  .byte $6a
VgF0D3:
  .byte $40
VgF0D4:
  .byte $6a
VgF0D5:
  .byte $ff
VgF0D6:
  .byte $23
VgF0D7:
  .byte $7f
VgF0D8:
  .byte $10
VgF0D9:
  .byte $83
VgF0DA:
  .byte $f0
VgF0DB:
  .byte $20
VgF0DC:
  .byte $b0
VgF0DD:
  .byte $24
VgF0DE:
  .byte $70
VgF0DF:
  .byte $28
VgF0E0:
  .byte $50
VgF0E1:
  .byte $2c
VgF0E2:
  .byte $30
VgF0E3:
  .byte $30
VgF0E4:
  .byte $ff
VgF0E5:
  .byte $21
VgF0E6:
  .byte $70
VgF0E7:
  .byte $f0
VgF0E8:
  .byte $1e
VgF0E9:
  .byte $f0
VgF0EA:
  .byte $15
VgF0EB:
  .byte $fe
VgF0EC:
  .byte $0a
VgF0ED:
VgF0EE = *+1
  .word VgF0E5
VgF0EF:
  .byte $ff
VgF0F0:
  .byte $26
VgF0F1:
  .byte $f2
VgF0F2:
  .byte $10
VgF0F3:
  .byte $81
VgF0F4:
  .byte $e0
VgF0F5:
  .byte $80
VgF0F6:
  .byte $28
VgF0F7:
  .byte $30
VgF0F8:
  .byte $a0
VgF0F9:
  .byte $80
VgF0FA:
  .byte $ff
VgF0FB:
  .byte $21
VgF0FC:
  .byte $b0
VgF0FD:
  .byte $f0
VgF0FE:
  .byte $40
VgF0FF:
  .byte $f0
VgF100:
  .byte $58
VgF101:
  .byte $f0
VgF102:
  .byte $78
VgF103:
  .byte $f0
VgF104:
  .byte $a0
VgF105:
  .byte $f0
VgF106:
  .byte $08
VgF107:
  .byte $a0
VgF108:
  .byte $18
VgF109:
  .byte $a0
VgF10A:
  .byte $38
VgF10B:
  .byte $a0
VgF10C:
  .byte $60
VgF10D:
  .byte $a0
VgF10E:
  .byte $08
VgF10F:
  .byte $80
VgF110:
  .byte $20
VgF111:
  .byte $80
VgF112:
  .byte $48
VgF113:
  .byte $80
VgF114:
  .byte $20
VgF115:
  .byte $60
VgF116:
  .byte $48
VgF117:
  .byte $ff
VgF118:
  .byte $21
VgF119:
  .byte $b0
VgF11A:
  .byte $f0
VgF11B:
  .byte $20
VgF11C:
  .byte $80
VgF11D:
  .byte $60
VgF11E:
  .byte $f0
VgF11F:
  .byte $20
VgF120:
  .byte $80
VgF121:
  .byte $60
VgF122:
  .byte $c0
VgF123:
  .byte $20
VgF124:
  .byte $40
VgF125:
  .byte $60
VgF126:
  .byte $ff
VgF127:
  .byte $21
VgF128:
  .byte $b0
VgF129:
  .byte $f0
VgF12A:
  .byte $80
VgF12B:
  .byte $f0
VgF12C:
  .byte $80
VgF12D:
  .byte $f0
VgF12E:
  .byte $48
VgF12F:
  .byte $f0
VgF130:
  .byte $68
VgF131:
  .byte $f0
VgF132:
  .byte $80
VgF133:
  .byte $f0
VgF134:
  .byte $90
VgF135:
  .byte $f0
VgF136:
  .byte $90
VgF137:
  .byte $f0
VgF138:
  .byte $40
VgF139:
  .byte $f0
VgF13A:
  .byte $58
VgF13B:
  .byte $f0
VgF13C:
  .byte $68
VgF13D:
  .byte $f0
VgF13E:
  .byte $68
VgF13F:
  .byte $f0
VgF140:
  .byte $38
VgF141:
  .byte $f0
VgF142:
  .byte $48
VgF143:
  .byte $f0
VgF144:
  .byte $48
VgF145:
  .byte $f0
VgF146:
  .byte $30
VgF147:
  .byte $ff
VgF148:
  .byte $21
VgF149:
  .byte $b0
VgF14A:
  .byte $10
VgF14B:
  .byte $83
VgF14C:
  .byte $f0
VgF14D:
  .byte $20
VgF14E:
  .byte $f0
VgF14F:
  .byte $50
VgF150:
  .byte $f0
VgF151:
  .byte $a8
VgF152:
  .byte $10
VgF153:
  .byte $8b
VgF154:
  .byte $f1
VgF155:
  .byte $28
VgF156:
  .byte $f0
VgF157:
  .byte $e8
VgF158:
  .byte $f0
VgF159:
  .byte $90
VgF15A:
  .byte $f0
VgF15B:
  .byte $66
VgF15C:
  .byte $10
VgF15D:
  .byte $83
VgF15E:
  .byte $f0
VgF15F:
  .byte $50
VgF160:
  .byte $f0
VgF161:
  .byte $a8
VgF162:
  .byte $10
VgF163:
  .byte $8b
VgF164:
  .byte $f1
VgF165:
  .byte $28
VgF166:
  .byte $f0
VgF167:
  .byte $e8
VgF168:
  .byte $f0
VgF169:
  .byte $90
VgF16A:
  .byte $ff
VgF16B:
  .byte $2b
VgF16C:
  .byte $82
VgF16D:
  .byte $10
VgF16E:
  .byte $84
VgF16F:
  .byte $02
VgF170:
  .byte $30
VgF171:
  .byte $28
VgF172:
  .byte $03
VgF173:
  .byte $10
VgF174:
  .byte $8f
VgF175:
  .byte $f4
VgF176:
  .byte $43
VgF177:
  .byte $ff
VgF178:
  .byte $26
VgF179:
  .byte $22
VgF17A:
  .byte $10
VgF17B:
  .byte $84
VgF17C:
  .byte $01
VgF17D:
  .byte $b0
VgF17E:
  .byte $29
VgF17F:
  .byte $64
VgF180:
  .byte $10
VgF181:
  .byte $01
VgF182:
  .byte $01
VgF183:
  .byte $f0
VgF184:
  .byte $ff
VgF185:
  .byte $28
VgF186:
  .byte $b0
VgF187:
  .byte $10
VgF188:
  .byte $83
VgF189:
  .byte $f2
VgF18A:
  .byte $60
VgF18B:
  .byte $23
VgF18C:
  .byte $21
VgF18D:
  .byte $10
VgF18E:
  .byte $8b
VgF18F:
  .byte $03
VgF190:
  .byte $ff
VgF191:
  .byte $02
VgF192:
  .byte $40
VgF193:
  .byte $ff
VgF194:
  .byte $29
VgF195:
  .byte $c2
VgF196:
  .byte $10
VgF197:
  .byte $8d
VgF198:
  .byte $f1
VgF199:
  .byte $00
VgF19A:
  .byte $f1
VgF19B:
  .byte $09
VgF19C:
  .byte $29
VgF19D:
  .byte $70
VgF19E:
  .byte $81
VgF19F:
  .byte $10
VgF1A0:
  .byte $41
VgF1A1:
  .byte $18
VgF1A2:
  .byte $31
VgF1A3:
  .byte $20
VgF1A4:
  .byte $2a
VgF1A5:
  .byte $70
VgF1A6:
  .byte $31
VgF1A7:
  .byte $2f
VgF1A8:
  .byte $ff
VgF1A9:
  .byte $21
VgF1AA:
  .byte $b0
VgF1AB:
  .byte $30
VgF1AC:
  .byte $44
VgF1AD:
  .byte $50
VgF1AE:
  .byte $8c
VgF1AF:
  .byte $b1
VgF1B0:
  .byte $28
VgF1B1:
  .byte $f1
VgF1B2:
  .byte $d4
VgF1B3:
  .byte $f2
VgF1B4:
  .byte $90
VgF1B5:
  .byte $f3
VgF1B6:
  .byte $5c
VgF1B7:
  .byte $f3
VgF1B8:
  .byte $ff
VgF1B9:
  .byte $f3
VgF1BA:
  .byte $ff
VgF1BB:
  .byte $fe
VgF1BC:
  .byte $02
VgF1BD:
VgF1BE = *+1
  .word VgF1A9
VgF1BF:
  .byte $30
VgF1C0:
  .byte $44
VgF1C1:
  .byte $50
VgF1C2:
  .byte $8c
VgF1C3:
  .byte $81
VgF1C4:
  .byte $28
VgF1C5:
  .byte $81
VgF1C6:
  .byte $d4
VgF1C7:
  .byte $82
VgF1C8:
  .byte $90
VgF1C9:
  .byte $83
VgF1CA:
  .byte $5c
VgF1CB:
  .byte $83
VgF1CC:
  .byte $ff
VgF1CD:
  .byte $83
VgF1CE:
  .byte $ff
VgF1CF:
  .byte $30
VgF1D0:
  .byte $44
VgF1D1:
  .byte $40
VgF1D2:
  .byte $8c
VgF1D3:
  .byte $61
VgF1D4:
  .byte $28
VgF1D5:
  .byte $61
VgF1D6:
  .byte $d4
VgF1D7:
  .byte $62
VgF1D8:
  .byte $90
VgF1D9:
  .byte $63
VgF1DA:
  .byte $5c
VgF1DB:
  .byte $63
VgF1DC:
  .byte $ff
VgF1DD:
  .byte $ff
VgF1DE:
  .byte $22
VgF1DF:
  .byte $f0
VgF1E0:
  .byte $d0
VgF1E1:
  .byte $72
VgF1E2:
  .byte $d0
VgF1E3:
  .byte $7f
VgF1E4:
  .byte $fe
VgF1E5:
  .byte $03
VgF1E6:
VgF1E7 = *+1
  .word VgF1E0
VgF1E8:
  .byte $21
VgF1E9:
  .byte $f0
VgF1EA:
  .byte $d0
VgF1EB:
  .byte $7c
VgF1EC:
  .byte $d0
VgF1ED:
  .byte $74
VgF1EE:
  .byte $d0
VgF1EF:
  .byte $7c
VgF1F0:
  .byte $c0
VgF1F1:
  .byte $70
VgF1F2:
  .byte $c0
VgF1F3:
  .byte $78
VgF1F4:
  .byte $c0
VgF1F5:
  .byte $70
VgF1F6:
  .byte $c0
VgF1F7:
  .byte $68
VgF1F8:
  .byte $c0
VgF1F9:
  .byte $78
VgF1FA:
  .byte $b0
VgF1FB:
  .byte $68
VgF1FC:
  .byte $b0
VgF1FD:
  .byte $60
VgF1FE:
  .byte $b0
VgF1FF:
  .byte $68
VgF200:
  .byte $a0
VgF201:
  .byte $60
VgF202:
  .byte $a0
VgF203:
  .byte $58
VgF204:
  .byte $a0
VgF205:
  .byte $60
VgF206:
  .byte $90
VgF207:
  .byte $58
VgF208:
  .byte $90
VgF209:
  .byte $50
VgF20A:
  .byte $90
VgF20B:
  .byte $58
VgF20C:
  .byte $80
VgF20D:
  .byte $4c
VgF20E:
  .byte $ff
VgF20F:
  .byte $25
VgF210:
  .byte $70
VgF211:
  .byte $f0
VgF212:
  .byte $3c
VgF213:
  .byte $22
VgF214:
  .byte $30
VgF215:
  .byte $f0
VgF216:
  .byte $78
VgF217:
  .byte $25
VgF218:
  .byte $70
VgF219:
  .byte $d0
VgF21A:
  .byte $3c
VgF21B:
  .byte $22
VgF21C:
  .byte $30
VgF21D:
  .byte $d0
VgF21E:
  .byte $78
VgF21F:
  .byte $25
VgF220:
  .byte $70
VgF221:
  .byte $b0
VgF222:
  .byte $3c
VgF223:
  .byte $22
VgF224:
  .byte $30
VgF225:
  .byte $b0
VgF226:
  .byte $78
VgF227:
  .byte $25
VgF228:
  .byte $70
VgF229:
  .byte $80
VgF22A:
  .byte $3c
VgF22B:
  .byte $22
VgF22C:
  .byte $30
VgF22D:
  .byte $80
VgF22E:
  .byte $78
VgF22F:
  .byte $25
VgF230:
  .byte $70
VgF231:
  .byte $60
VgF232:
  .byte $3c
VgF233:
  .byte $22
VgF234:
  .byte $30
VgF235:
  .byte $60
VgF236:
  .byte $78
VgF237:
  .byte $25
VgF238:
  .byte $70
VgF239:
  .byte $30
VgF23A:
  .byte $3c
VgF23B:
  .byte $22
VgF23C:
  .byte $30
VgF23D:
  .byte $30
VgF23E:
  .byte $78
VgF23F:
  .byte $ff
VgF240:
  .byte $25
VgF241:
  .byte $f0
VgF242:
  .byte $f0
VgF243:
  .byte $dd
VgF244:
  .byte $f0
VgF245:
  .byte $1d
VgF246:
  .byte $d0
VgF247:
  .byte $dd
VgF248:
  .byte $d0
VgF249:
  .byte $1d
VgF24A:
  .byte $b0
VgF24B:
  .byte $dd
VgF24C:
  .byte $b0
VgF24D:
  .byte $1d
VgF24E:
  .byte $90
VgF24F:
  .byte $dd
VgF250:
  .byte $90
VgF251:
  .byte $1d
VgF252:
  .byte $70
VgF253:
  .byte $dd
VgF254:
  .byte $70
VgF255:
  .byte $1d
VgF256:
  .byte $50
VgF257:
  .byte $dd
VgF258:
  .byte $50
VgF259:
  .byte $1d
VgF25A:
  .byte $30
VgF25B:
  .byte $dd
VgF25C:
  .byte $30
VgF25D:
  .byte $1d
VgF25E:
  .byte $ff
VgF25F:
  .byte $2f
VgF260:
  .byte $30
VgF261:
  .byte $f0
VgF262:
  .byte $0f
VgF263:
  .byte $d0
VgF264:
  .byte $0f
VgF265:
  .byte $b0
VgF266:
  .byte $0f
VgF267:
  .byte $90
VgF268:
  .byte $0f
VgF269:
  .byte $70
VgF26A:
  .byte $0f
VgF26B:
  .byte $50
VgF26C:
  .byte $0f
VgF26D:
  .byte $30
VgF26E:
  .byte $0f
VgF26F:
  .byte $2f
VgF270:
  .byte $30
VgF271:
  .byte $00
VgF272:
  .byte $00
VgF273:
  .byte $00
VgF274:
  .byte $00
VgF275:
  .byte $00
VgF276:
  .byte $00
VgF277:
  .byte $fe
VgF278:
  .byte $ff
VgF279:
VgF27A = *+1
  .word VgF25F
VgF27B:
  .byte $21
VgF27C:
  .byte $b0
VgF27D:
  .byte $11
VgF27E:
  .byte $01
VgF27F:
  .byte $21
VgF280:
  .byte $b0
VgF281:
  .byte $10
VgF282:
  .byte $96
VgF283:
  .byte $f0
VgF284:
  .byte $80
VgF285:
  .byte $f1
VgF286:
  .byte $00
VgF287:
  .byte $f1
VgF288:
  .byte $80
VgF289:
  .byte $f2
VgF28A:
  .byte $00
VgF28B:
  .byte $f2
VgF28C:
  .byte $80
VgF28D:
  .byte $f3
VgF28E:
  .byte $00
VgF28F:
  .byte $f3
VgF290:
  .byte $80
VgF291:
  .byte $f0
VgF292:
  .byte $80
VgF293:
  .byte $f0
VgF294:
  .byte $c0
VgF295:
  .byte $f1
VgF296:
  .byte $00
VgF297:
  .byte $f1
VgF298:
  .byte $40
VgF299:
  .byte $f1
VgF29A:
  .byte $80
VgF29B:
  .byte $f1
VgF29C:
  .byte $c0
VgF29D:
  .byte $f2
VgF29E:
  .byte $00
VgF29F:
  .byte $f2
VgF2A0:
  .byte $40
VgF2A1:
  .byte $f2
VgF2A2:
  .byte $80
VgF2A3:
  .byte $f2
VgF2A4:
  .byte $c0
VgF2A5:
  .byte $f3
VgF2A6:
  .byte $00
VgF2A7:
  .byte $f3
VgF2A8:
  .byte $40
VgF2A9:
  .byte $f3
VgF2AA:
  .byte $80
VgF2AB:
  .byte $f3
VgF2AC:
  .byte $c0
VgF2AD:
  .byte $e0
VgF2AE:
  .byte $80
VgF2AF:
  .byte $e0
VgF2B0:
  .byte $c0
VgF2B1:
  .byte $e1
VgF2B2:
  .byte $00
VgF2B3:
  .byte $d1
VgF2B4:
  .byte $40
VgF2B5:
  .byte $d1
VgF2B6:
  .byte $80
VgF2B7:
  .byte $d1
VgF2B8:
  .byte $c0
VgF2B9:
  .byte $c2
VgF2BA:
  .byte $00
VgF2BB:
  .byte $c2
VgF2BC:
  .byte $40
VgF2BD:
  .byte $c2
VgF2BE:
  .byte $80
VgF2BF:
  .byte $b2
VgF2C0:
  .byte $c0
VgF2C1:
  .byte $b3
VgF2C2:
  .byte $00
VgF2C3:
  .byte $b3
VgF2C4:
  .byte $40
VgF2C5:
  .byte $a3
VgF2C6:
  .byte $80
VgF2C7:
  .byte $a3
VgF2C8:
  .byte $c0
VgF2C9:
  .byte $a0
VgF2CA:
  .byte $80
VgF2CB:
  .byte $90
VgF2CC:
  .byte $c0
VgF2CD:
  .byte $91
VgF2CE:
  .byte $00
VgF2CF:
  .byte $91
VgF2D0:
  .byte $40
VgF2D1:
  .byte $81
VgF2D2:
  .byte $80
VgF2D3:
  .byte $81
VgF2D4:
  .byte $c0
VgF2D5:
  .byte $82
VgF2D6:
  .byte $00
VgF2D7:
  .byte $72
VgF2D8:
  .byte $40
VgF2D9:
  .byte $72
VgF2DA:
  .byte $80
VgF2DB:
  .byte $72
VgF2DC:
  .byte $c0
VgF2DD:
  .byte $63
VgF2DE:
  .byte $00
VgF2DF:
  .byte $62
VgF2E0:
  .byte $40
VgF2E1:
  .byte $63
VgF2E2:
  .byte $80
VgF2E3:
  .byte $53
VgF2E4:
  .byte $c0
VgF2E5:
  .byte $50
VgF2E6:
  .byte $80
VgF2E7:
  .byte $50
VgF2E8:
  .byte $c0
VgF2E9:
  .byte $41
VgF2EA:
  .byte $00
VgF2EB:
  .byte $41
VgF2EC:
  .byte $40
VgF2ED:
  .byte $41
VgF2EE:
  .byte $80
VgF2EF:
  .byte $31
VgF2F0:
  .byte $c0
VgF2F1:
  .byte $32
VgF2F2:
  .byte $00
VgF2F3:
  .byte $32
VgF2F4:
  .byte $40
VgF2F5:
  .byte $32
VgF2F6:
  .byte $80
VgF2F7:
  .byte $32
VgF2F8:
  .byte $c0
VgF2F9:
  .byte $33
VgF2FA:
  .byte $00
VgF2FB:
  .byte $33
VgF2FC:
  .byte $40
VgF2FD:
  .byte $33
VgF2FE:
  .byte $80
VgF2FF:
  .byte $33
VgF300:
  .byte $c0
VgF301:
  .byte $ff
VgF302:
  .byte $ff
VgF303:
  .byte $21
VgF304:
  .byte $b0
VgF305:
  .byte $11
VgF306:
  .byte $40
VgF307:
  .byte $22
VgF308:
  .byte $b0
VgF309:
  .byte $f0
VgF30A:
  .byte $00
VgF30B:
  .byte $f0
VgF30C:
  .byte $f0
VgF30D:
  .byte $e0
VgF30E:
  .byte $00
VgF30F:
  .byte $e0
VgF310:
  .byte $10
VgF311:
  .byte $e0
VgF312:
  .byte $30
VgF313:
  .byte $e0
VgF314:
  .byte $60
VgF315:
  .byte $e0
VgF316:
  .byte $a0
VgF317:
  .byte $e0
VgF318:
  .byte $f0
VgF319:
  .byte $d0
VgF31A:
  .byte $00
VgF31B:
  .byte $d0
VgF31C:
  .byte $f0
VgF31D:
  .byte $c0
VgF31E:
  .byte $00
VgF31F:
  .byte $c0
VgF320:
  .byte $10
VgF321:
  .byte $c0
VgF322:
  .byte $30
VgF323:
  .byte $c0
VgF324:
  .byte $60
VgF325:
  .byte $c0
VgF326:
  .byte $a0
VgF327:
  .byte $c0
VgF328:
  .byte $f0
VgF329:
  .byte $b0
VgF32A:
  .byte $00
VgF32B:
  .byte $b0
VgF32C:
  .byte $f0
VgF32D:
  .byte $a0
VgF32E:
  .byte $00
VgF32F:
  .byte $a0
VgF330:
  .byte $10
VgF331:
  .byte $a0
VgF332:
  .byte $30
VgF333:
  .byte $a0
VgF334:
  .byte $60
VgF335:
  .byte $a0
VgF336:
  .byte $a0
VgF337:
  .byte $a0
VgF338:
  .byte $f0
VgF339:
  .byte $90
VgF33A:
  .byte $00
VgF33B:
  .byte $90
VgF33C:
  .byte $f0
VgF33D:
  .byte $80
VgF33E:
  .byte $00
VgF33F:
  .byte $80
VgF340:
  .byte $10
VgF341:
  .byte $80
VgF342:
  .byte $30
VgF343:
  .byte $80
VgF344:
  .byte $60
VgF345:
  .byte $80
VgF346:
  .byte $a0
VgF347:
  .byte $80
VgF348:
  .byte $f0
VgF349:
  .byte $70
VgF34A:
  .byte $00
VgF34B:
  .byte $70
VgF34C:
  .byte $f0
VgF34D:
  .byte $60
VgF34E:
  .byte $00
VgF34F:
  .byte $60
VgF350:
  .byte $10
VgF351:
  .byte $60
VgF352:
  .byte $30
VgF353:
  .byte $60
VgF354:
  .byte $60
VgF355:
  .byte $60
VgF356:
  .byte $a0
VgF357:
  .byte $60
VgF358:
  .byte $f0
VgF359:
  .byte $50
VgF35A:
  .byte $00
VgF35B:
  .byte $50
VgF35C:
  .byte $f0
VgF35D:
  .byte $40
VgF35E:
  .byte $00
VgF35F:
  .byte $40
VgF360:
  .byte $10
VgF361:
  .byte $40
VgF362:
  .byte $30
VgF363:
  .byte $40
VgF364:
  .byte $60
VgF365:
  .byte $40
VgF366:
  .byte $a0
VgF367:
  .byte $40
VgF368:
  .byte $f0
VgF369:
  .byte $30
VgF36A:
  .byte $00
VgF36B:
  .byte $30
VgF36C:
  .byte $f0
VgF36D:
  .byte $30
VgF36E:
  .byte $00
VgF36F:
  .byte $30
VgF370:
  .byte $10
VgF371:
  .byte $30
VgF372:
  .byte $30
VgF373:
  .byte $30
VgF374:
  .byte $60
VgF375:
  .byte $30
VgF376:
  .byte $a0
VgF377:
  .byte $30
VgF378:
  .byte $f0
VgF379:
  .byte $30
VgF37A:
  .byte $00
VgF37B:
  .byte $30
VgF37C:
  .byte $f0
VgF37D:
  .byte $ff
VgF37E:
  .byte $21
VgF37F:
  .byte $10
VgF380:
  .byte $00
VgF381:
  .byte $80
VgF382:
  .byte $01
VgF383:
  .byte $00
VgF384:
  .byte $01
VgF385:
  .byte $80
VgF386:
  .byte $02
VgF387:
  .byte $00
VgF388:
  .byte $02
VgF389:
  .byte $80
VgF38A:
  .byte $03
VgF38B:
  .byte $00
VgF38C:
  .byte $30
VgF38D:
  .byte $80
VgF38E:
  .byte $00
VgF38F:
  .byte $80
VgF390:
  .byte $01
VgF391:
  .byte $00
VgF392:
  .byte $01
VgF393:
  .byte $80
VgF394:
  .byte $02
VgF395:
  .byte $00
VgF396:
  .byte $02
VgF397:
  .byte $80
VgF398:
  .byte $03
VgF399:
  .byte $00
VgF39A:
  .byte $03
VgF39B:
  .byte $80
VgF39C:
  .byte $00
VgF39D:
  .byte $60
VgF39E:
  .byte $00
VgF39F:
  .byte $80
VgF3A0:
  .byte $00
VgF3A1:
  .byte $a0
VgF3A2:
  .byte $00
VgF3A3:
  .byte $c0
VgF3A4:
  .byte $00
VgF3A5:
  .byte $e0
VgF3A6:
  .byte $01
VgF3A7:
  .byte $00
VgF3A8:
  .byte $01
VgF3A9:
  .byte $20
VgF3AA:
  .byte $01
VgF3AB:
  .byte $40
VgF3AC:
  .byte $01
VgF3AD:
  .byte $60
VgF3AE:
  .byte $01
VgF3AF:
  .byte $80
VgF3B0:
  .byte $01
VgF3B1:
  .byte $a0
VgF3B2:
  .byte $01
VgF3B3:
  .byte $c0
VgF3B4:
  .byte $01
VgF3B5:
  .byte $e0
VgF3B6:
  .byte $02
VgF3B7:
  .byte $00
VgF3B8:
  .byte $02
VgF3B9:
  .byte $c0
VgF3BA:
  .byte $02
VgF3BB:
  .byte $e0
VgF3BC:
  .byte $03
VgF3BD:
  .byte $00
VgF3BE:
  .byte $ff
VgF3BF:
  .byte $2f
VgF3C0:
  .byte $04
VgF3C1:
  .byte $00
VgF3C2:
  .byte $0f
VgF3C3:
  .byte $ff
VgF3C4:
  .byte $d4
VgF3C5:
  .byte $7a
VgF3C6:
  .byte $29
VgF3C7:
  .byte $e0
VgF3C8:
  .byte $41
VgF3C9:
  .byte $e1
VgF3CA:
  .byte $b1
VgF3CB:
  .byte $e0
VgF3CC:
  .byte $41
VgF3CD:
  .byte $63
VgF3CE:
  .byte $b3
VgF3CF:
  .byte $63
VgF3D0:
  .byte $43
VgF3D1:
  .byte $e1
VgF3D2:
  .byte $b1
VgF3D3:
  .byte $e0
VgF3D4:
  .byte $41
VgF3D5:
  .byte $e1
VgF3D6:
  .byte $b1
VgF3D7:
  .byte $e0
VgF3D8:
  .byte $41
VgF3D9:
  .byte $61
VgF3DA:
  .byte $fe
VgF3DB:
  .byte $04
VgF3DC:
VgF3DD = *+1
  .word VgF3C4
VgF3DE:
  .byte $ff
VgF3DF:
  .byte $d8
VgF3E0:
  .byte $ff
VgF3E1:
  .byte $33
VgF3E2:
  .byte $e2
VgF3E3:
  .byte $bc
VgF3E4:
  .byte $c0
VgF3E5:
  .byte $b0
VgF3E6:
  .byte $c0
VgF3E7:
  .byte $9c
VgF3E8:
  .byte $c0
VgF3E9:
  .byte $90
VgF3EA:
  .byte $c0
VgF3EB:
  .byte $7c
VgF3EC:
  .byte $c0
VgF3ED:
  .byte $70
VgF3EE:
  .byte $c0
VgF3EF:
  .byte $9c
VgF3F0:
  .byte $c2
VgF3F1:
  .byte $d8
VgF3F2:
  .byte $7f
VgF3F3:
  .byte $2f
VgF3F4:
  .byte $e2
VgF3F5:
  .byte $80
VgF3F6:
  .byte $60
VgF3F7:
  .byte $80
VgF3F8:
  .byte $a1
VgF3F9:
  .byte $b1
VgF3FA:
  .byte $a1
VgF3FB:
  .byte $81
VgF3FC:
  .byte $60
VgF3FD:
  .byte $80
VgF3FE:
  .byte $60
VgF3FF:
  .byte $80
VgF400:
  .byte $40
VgF401:
  .byte $fe
VgF402:
  .byte $02
VgF403:
VgF404 = *+1
  .word VgF3F1
VgF405:
  .byte $60
VgF406:
  .byte $40
VgF407:
  .byte $60
VgF408:
  .byte $81
VgF409:
  .byte $91
VgF40A:
  .byte $81
VgF40B:
  .byte $61
VgF40C:
  .byte $80
VgF40D:
  .byte $60
VgF40E:
  .byte $4a
VgF40F:
  .byte $10
VgF410:
  .byte $30
VgF411:
  .byte $40
VgF412:
  .byte $61
VgF413:
  .byte $40
VgF414:
  .byte $30
VgF415:
  .byte $10
VgF416:
  .byte $80
VgF417:
  .byte $60
VgF418:
  .byte $80
VgF419:
  .byte $a1
VgF41A:
  .byte $b1
VgF41B:
  .byte $a1
VgF41C:
  .byte $81
VgF41D:
  .byte $60
VgF41E:
  .byte $80
VgF41F:
  .byte $60
VgF420:
  .byte $80
VgF421:
  .byte $40
VgF422:
  .byte $fe
VgF423:
  .byte $02
VgF424:
VgF425 = *+1
  .word VgF416
VgF426:
  .byte $60
VgF427:
  .byte $40
VgF428:
  .byte $60
VgF429:
  .byte $81
VgF42A:
  .byte $91
VgF42B:
  .byte $82
VgF42C:
  .byte $61
VgF42D:
  .byte $80
VgF42E:
  .byte $44
VgF42F:
  .byte $60
VgF430:
  .byte $40
VgF431:
  .byte $24
VgF432:
  .byte $40
VgF433:
  .byte $20
VgF434:
  .byte $00
VgF435:
  .byte $00
VgF436:
  .byte $40
VgF437:
  .byte $60
VgF438:
  .byte $81
VgF439:
  .byte $60
VgF43A:
  .byte $80
VgF43B:
  .byte $a1
VgF43C:
  .byte $b1
VgF43D:
  .byte $a1
VgF43E:
  .byte $81
VgF43F:
  .byte $60
VgF440:
  .byte $80
VgF441:
  .byte $60
VgF442:
  .byte $80
VgF443:
  .byte $40
VgF444:
  .byte $80
VgF445:
  .byte $60
VgF446:
  .byte $80
VgF447:
  .byte $a1
VgF448:
  .byte $b1
VgF449:
  .byte $a1
VgF44A:
  .byte $81
VgF44B:
  .byte $60
VgF44C:
  .byte $80
VgF44D:
  .byte $60
VgF44E:
  .byte $80
VgF44F:
  .byte $40
VgF450:
  .byte $fe
VgF451:
  .byte $ff
VgF452:
VgF453 = *+1
  .word VgF405
VgF454:
  .byte $d1
VgF455:
  .byte $1b
VgF456:
  .byte $e0
VgF457:
  .byte $c0
VgF458:
  .byte $d4
VgF459:
  .byte $1b
VgF45A:
  .byte $41
VgF45B:
  .byte $e1
VgF45C:
  .byte $b1
VgF45D:
  .byte $e0
VgF45E:
  .byte $41
VgF45F:
  .byte $63
VgF460:
  .byte $b3
VgF461:
  .byte $63
VgF462:
  .byte $43
VgF463:
  .byte $e1
VgF464:
  .byte $b1
VgF465:
  .byte $e0
VgF466:
  .byte $41
VgF467:
  .byte $e1
VgF468:
  .byte $b1
VgF469:
  .byte $e0
VgF46A:
  .byte $41
VgF46B:
  .byte $61
VgF46C:
  .byte $fe
VgF46D:
  .byte $04
VgF46E:
VgF46F = *+1
  .word VgF458
VgF470:
  .byte $fd
VgF471:
VgF472 = *+1
  .word VgF4AA
VgF473:
  .byte $e2
VgF474:
  .byte $42
VgF475:
  .byte $c0
VgF476:
  .byte $42
VgF477:
  .byte $c0
VgF478:
  .byte $92
VgF479:
  .byte $c0
VgF47A:
  .byte $92
VgF47B:
  .byte $c0
VgF47C:
  .byte $fe
VgF47D:
  .byte $05
VgF47E:
VgF47F = *+1
  .word VgF473
VgF480:
  .byte $fd
VgF481:
VgF482 = *+1
  .word VgF4AA
VgF483:
  .byte $e2
VgF484:
  .byte $72
VgF485:
  .byte $c0
VgF486:
  .byte $72
VgF487:
  .byte $c0
VgF488:
  .byte $e1
VgF489:
  .byte $02
VgF48A:
  .byte $c0
VgF48B:
  .byte $02
VgF48C:
  .byte $c0
VgF48D:
  .byte $fe
VgF48E:
  .byte $02
VgF48F:
VgF490 = *+1
  .word VgF483
VgF491:
  .byte $e2
VgF492:
  .byte $52
VgF493:
  .byte $c0
VgF494:
  .byte $52
VgF495:
  .byte $c0
VgF496:
  .byte $a2
VgF497:
  .byte $c0
VgF498:
  .byte $a2
VgF499:
  .byte $c0
VgF49A:
  .byte $fe
VgF49B:
  .byte $02
VgF49C:
VgF49D = *+1
  .word VgF491
VgF49E:
  .byte $32
VgF49F:
  .byte $c0
VgF4A0:
  .byte $32
VgF4A1:
  .byte $c0
VgF4A2:
  .byte $82
VgF4A3:
  .byte $c0
VgF4A4:
  .byte $82
VgF4A5:
  .byte $c0
VgF4A6:
  .byte $fe
VgF4A7:
  .byte $ff
VgF4A8:
VgF4A9 = *+1
  .word VgF470
VgF4AA:
  .byte $d2
VgF4AB:
  .byte $8f
VgF4AC:
  .byte $e2
VgF4AD:
  .byte $b2
VgF4AE:
  .byte $c0
VgF4AF:
  .byte $b2
VgF4B0:
  .byte $c0
VgF4B1:
  .byte $e1
VgF4B2:
  .byte $42
VgF4B3:
  .byte $c0
VgF4B4:
  .byte $42
VgF4B5:
  .byte $c0
VgF4B6:
  .byte $fe
VgF4B7:
  .byte $08
VgF4B8:
VgF4B9 = *+1
  .word VgF4AA
VgF4BA:
  .byte $e2
VgF4BB:
  .byte $92
VgF4BC:
  .byte $c0
VgF4BD:
  .byte $92
VgF4BE:
  .byte $c0
VgF4BF:
  .byte $e1
VgF4C0:
  .byte $22
VgF4C1:
  .byte $c0
VgF4C2:
  .byte $22
VgF4C3:
  .byte $c0
VgF4C4:
  .byte $fe
VgF4C5:
  .byte $03
VgF4C6:
VgF4C7 = *+1
  .word VgF4BA
VgF4C8:
  .byte $ff
VgF4C9:
  .byte $d6
VgF4CA:
  .byte $f7
VgF4CB:
  .byte $63
VgF4CC:
  .byte $e3
VgF4CD:
  .byte $21
VgF4CE:
  .byte $21
VgF4CF:
  .byte $e2
VgF4D0:
  .byte $21
VgF4D1:
  .byte $e3
VgF4D2:
  .byte $20
VgF4D3:
  .byte $21
VgF4D4:
  .byte $21
VgF4D5:
  .byte $20
VgF4D6:
  .byte $d6
VgF4D7:
  .byte $fe
VgF4D8:
  .byte $65
VgF4D9:
  .byte $e1
VgF4DA:
  .byte $01
VgF4DB:
  .byte $01
VgF4DC:
  .byte $d6
VgF4DD:
  .byte $f6
VgF4DE:
  .byte $53
VgF4DF:
  .byte $e3
VgF4E0:
  .byte $21
VgF4E1:
  .byte $21
VgF4E2:
  .byte $e2
VgF4E3:
  .byte $21
VgF4E4:
  .byte $e3
VgF4E5:
  .byte $20
VgF4E6:
  .byte $21
VgF4E7:
  .byte $21
VgF4E8:
  .byte $20
VgF4E9:
  .byte $d6
VgF4EA:
  .byte $fe
VgF4EB:
  .byte $c7
VgF4EC:
  .byte $e1
VgF4ED:
  .byte $00
VgF4EE:
  .byte $e2
VgF4EF:
  .byte $b0
VgF4F0:
  .byte $e1
VgF4F1:
  .byte $01
VgF4F2:
  .byte $c0
VgF4F3:
  .byte $e3
VgF4F4:
  .byte $01
VgF4F5:
  .byte $01
VgF4F6:
  .byte $d6
VgF4F7:
  .byte $f6
VgF4F8:
  .byte $53
VgF4F9:
  .byte $c0
VgF4FA:
  .byte $20
VgF4FB:
  .byte $21
VgF4FC:
  .byte $21
VgF4FD:
  .byte $20
VgF4FE:
  .byte $d6
VgF4FF:
  .byte $ff
VgF500:
  .byte $46
VgF501:
  .byte $e1
VgF502:
  .byte $00
VgF503:
  .byte $e2
VgF504:
  .byte $b0
VgF505:
  .byte $e1
VgF506:
  .byte $01
VgF507:
  .byte $42
VgF508:
  .byte $32
VgF509:
  .byte $22
VgF50A:
  .byte $32
VgF50B:
  .byte $41
VgF50C:
  .byte $51
VgF50D:
  .byte $d6
VgF50E:
  .byte $f6
VgF50F:
  .byte $53
VgF510:
  .byte $e3
VgF511:
  .byte $41
VgF512:
  .byte $41
VgF513:
  .byte $d6
VgF514:
  .byte $fb
VgF515:
  .byte $90
VgF516:
  .byte $e1
VgF517:
  .byte $61
VgF518:
  .byte $d6
VgF519:
  .byte $f6
VgF51A:
  .byte $53
VgF51B:
  .byte $e3
VgF51C:
  .byte $40
VgF51D:
  .byte $41
VgF51E:
  .byte $41
VgF51F:
  .byte $40
VgF520:
  .byte $d6
VgF521:
  .byte $fe
VgF522:
  .byte $63
VgF523:
  .byte $e1
VgF524:
  .byte $60
VgF525:
  .byte $50
VgF526:
  .byte $61
VgF527:
  .byte $c0
VgF528:
  .byte $62
VgF529:
  .byte $61
VgF52A:
  .byte $c2
VgF52B:
  .byte $61
VgF52C:
  .byte $60
VgF52D:
  .byte $91
VgF52E:
  .byte $91
VgF52F:
  .byte $c0
VgF530:
  .byte $62
VgF531:
  .byte $61
VgF532:
  .byte $c2
VgF533:
  .byte $61
VgF534:
  .byte $60
VgF535:
  .byte $91
VgF536:
  .byte $90
VgF537:
  .byte $a0
VgF538:
  .byte $d6
VgF539:
  .byte $ba
VgF53A:
  .byte $45
VgF53B:
  .byte $e3
VgF53C:
  .byte $80
VgF53D:
  .byte $e2
VgF53E:
  .byte $30
VgF53F:
  .byte $60
VgF540:
  .byte $a0
VgF541:
  .byte $e1
VgF542:
  .byte $00
VgF543:
  .byte $30
VgF544:
  .byte $60
VgF545:
  .byte $30
VgF546:
  .byte $00
VgF547:
  .byte $e2
VgF548:
  .byte $70
VgF549:
  .byte $60
VgF54A:
  .byte $30
VgF54B:
  .byte $d4
VgF54C:
  .byte $ba
VgF54D:
  .byte $45
VgF54E:
  .byte $e3
VgF54F:
  .byte $80
VgF550:
  .byte $e2
VgF551:
  .byte $30
VgF552:
  .byte $60
VgF553:
  .byte $a0
VgF554:
  .byte $e1
VgF555:
  .byte $00
VgF556:
  .byte $30
VgF557:
  .byte $d6
VgF558:
  .byte $ba
VgF559:
  .byte $45
VgF55A:
  .byte $e3
VgF55B:
  .byte $70
VgF55C:
  .byte $e2
VgF55D:
  .byte $20
VgF55E:
  .byte $50
VgF55F:
  .byte $90
VgF560:
  .byte $b0
VgF561:
  .byte $e1
VgF562:
  .byte $20
VgF563:
  .byte $50
VgF564:
  .byte $20
VgF565:
  .byte $e2
VgF566:
  .byte $b0
VgF567:
  .byte $70
VgF568:
  .byte $50
VgF569:
  .byte $20
VgF56A:
  .byte $d4
VgF56B:
  .byte $ba
VgF56C:
  .byte $45
VgF56D:
  .byte $e3
VgF56E:
  .byte $40
VgF56F:
  .byte $e2
VgF570:
  .byte $20
VgF571:
  .byte $50
VgF572:
  .byte $90
VgF573:
  .byte $b0
VgF574:
  .byte $e1
VgF575:
  .byte $20
VgF576:
  .byte $d6
VgF577:
  .byte $ba
VgF578:
  .byte $45
VgF579:
  .byte $e3
VgF57A:
  .byte $30
VgF57B:
  .byte $e2
VgF57C:
  .byte $10
VgF57D:
  .byte $40
VgF57E:
  .byte $80
VgF57F:
  .byte $a0
VgF580:
  .byte $e1
VgF581:
  .byte $10
VgF582:
  .byte $40
VgF583:
  .byte $10
VgF584:
  .byte $e2
VgF585:
  .byte $a0
VgF586:
  .byte $50
VgF587:
  .byte $40
VgF588:
  .byte $10
VgF589:
  .byte $e3
VgF58A:
  .byte $30
VgF58B:
  .byte $a0
VgF58C:
  .byte $e2
VgF58D:
  .byte $10
VgF58E:
  .byte $e3
VgF58F:
  .byte $20
VgF590:
  .byte $d6
VgF591:
  .byte $ba
VgF592:
  .byte $57
VgF593:
  .byte $e1
VgF594:
  .byte $08
VgF595:
  .byte $d6
VgF596:
  .byte $fc
VgF597:
  .byte $74
VgF598:
  .byte $e3
VgF599:
  .byte $01
VgF59A:
  .byte $00
VgF59B:
  .byte $31
VgF59C:
  .byte $31
VgF59D:
  .byte $d6
VgF59E:
  .byte $ba
VgF59F:
  .byte $57
VgF5A0:
  .byte $e1
VgF5A1:
  .byte $08
VgF5A2:
  .byte $d6
VgF5A3:
  .byte $fc
VgF5A4:
  .byte $74
VgF5A5:
  .byte $e3
VgF5A6:
  .byte $01
VgF5A7:
  .byte $00
VgF5A8:
  .byte $61
VgF5A9:
  .byte $61
VgF5AA:
  .byte $c0
VgF5AB:
  .byte $60
VgF5AC:
  .byte $61
VgF5AD:
  .byte $61
VgF5AE:
  .byte $50
VgF5AF:
  .byte $64
VgF5B0:
  .byte $60
VgF5B1:
  .byte $50
VgF5B2:
  .byte $30
VgF5B3:
  .byte $0c
VgF5B4:
  .byte $31
VgF5B5:
  .byte $31
VgF5B6:
  .byte $fe
VgF5B7:
  .byte $ff
VgF5B8:
VgF5B9 = *+1
  .word VgF4C9
VgF5BA:
  .byte $d6
VgF5BB:
  .byte $0a
VgF5BC:
  .byte $e3
VgF5BD:
  .byte $21
VgF5BE:
  .byte $21
VgF5BF:
  .byte $e2
VgF5C0:
  .byte $21
VgF5C1:
  .byte $e3
VgF5C2:
  .byte $20
VgF5C3:
  .byte $21
VgF5C4:
  .byte $21
VgF5C5:
  .byte $20
VgF5C6:
  .byte $d6
VgF5C7:
  .byte $0c
VgF5C8:
  .byte $e2
VgF5C9:
  .byte $21
VgF5CA:
  .byte $21
VgF5CB:
  .byte $fe
VgF5CC:
  .byte $03
VgF5CD:
VgF5CE = *+1
  .word VgF5BA
VgF5CF:
  .byte $21
VgF5D0:
  .byte $20
VgF5D1:
  .byte $11
VgF5D2:
  .byte $10
VgF5D3:
  .byte $01
VgF5D4:
  .byte $00
VgF5D5:
  .byte $10
VgF5D6:
  .byte $11
VgF5D7:
  .byte $20
VgF5D8:
  .byte $20
VgF5D9:
  .byte $31
VgF5DA:
  .byte $e3
VgF5DB:
  .byte $41
VgF5DC:
  .byte $41
VgF5DD:
  .byte $e2
VgF5DE:
  .byte $41
VgF5DF:
  .byte $e3
VgF5E0:
  .byte $40
VgF5E1:
  .byte $41
VgF5E2:
  .byte $41
VgF5E3:
  .byte $40
VgF5E4:
  .byte $e2
VgF5E5:
  .byte $40
VgF5E6:
  .byte $30
VgF5E7:
  .byte $41
VgF5E8:
  .byte $e3
VgF5E9:
  .byte $41
VgF5EA:
  .byte $41
VgF5EB:
  .byte $e2
VgF5EC:
  .byte $41
VgF5ED:
  .byte $e3
VgF5EE:
  .byte $40
VgF5EF:
  .byte $41
VgF5F0:
  .byte $41
VgF5F1:
  .byte $40
VgF5F2:
  .byte $71
VgF5F3:
  .byte $71
VgF5F4:
  .byte $41
VgF5F5:
  .byte $41
VgF5F6:
  .byte $e2
VgF5F7:
  .byte $41
VgF5F8:
  .byte $e3
VgF5F9:
  .byte $40
VgF5FA:
  .byte $41
VgF5FB:
  .byte $41
VgF5FC:
  .byte $40
VgF5FD:
  .byte $51
VgF5FE:
  .byte $70
VgF5FF:
  .byte $d6
VgF600:
  .byte $81
VgF601:
  .byte $e0
VgF602:
  .byte $ab
VgF603:
  .byte $c0
VgF604:
  .byte $d6
VgF605:
  .byte $10
VgF606:
  .byte $a0
VgF607:
  .byte $d6
VgF608:
  .byte $81
VgF609:
  .byte $a1
VgF60A:
  .byte $9b
VgF60B:
  .byte $c0
VgF60C:
  .byte $d6
VgF60D:
  .byte $10
VgF60E:
  .byte $90
VgF60F:
  .byte $d6
VgF610:
  .byte $81
VgF611:
  .byte $91
VgF612:
  .byte $8b
VgF613:
  .byte $c0
VgF614:
  .byte $d6
VgF615:
  .byte $10
VgF616:
  .byte $50
VgF617:
  .byte $d6
VgF618:
  .byte $81
VgF619:
  .byte $52
VgF61A:
  .byte $d6
VgF61B:
  .byte $0a
VgF61C:
  .byte $e3
VgF61D:
  .byte $21
VgF61E:
  .byte $21
VgF61F:
  .byte $e2
VgF620:
  .byte $21
VgF621:
  .byte $e3
VgF622:
  .byte $20
VgF623:
  .byte $21
VgF624:
  .byte $21
VgF625:
  .byte $20
VgF626:
  .byte $51
VgF627:
  .byte $51
VgF628:
  .byte $21
VgF629:
  .byte $21
VgF62A:
  .byte $e2
VgF62B:
  .byte $21
VgF62C:
  .byte $e3
VgF62D:
  .byte $20
VgF62E:
  .byte $21
VgF62F:
  .byte $21
VgF630:
  .byte $20
VgF631:
  .byte $81
VgF632:
  .byte $81
VgF633:
  .byte $c0
VgF634:
  .byte $80
VgF635:
  .byte $81
VgF636:
  .byte $81
VgF637:
  .byte $70
VgF638:
  .byte $d6
VgF639:
  .byte $40
VgF63A:
  .byte $84
VgF63B:
  .byte $d6
VgF63C:
  .byte $0a
VgF63D:
  .byte $80
VgF63E:
  .byte $70
VgF63F:
  .byte $60
VgF640:
  .byte $d6
VgF641:
  .byte $2c
VgF642:
  .byte $22
VgF643:
  .byte $d6
VgF644:
  .byte $0a
VgF645:
  .byte $80
VgF646:
  .byte $e2
VgF647:
  .byte $01
VgF648:
  .byte $21
VgF649:
  .byte $01
VgF64A:
  .byte $21
VgF64B:
  .byte $00
VgF64C:
  .byte $31
VgF64D:
  .byte $31
VgF64E:
  .byte $fe
VgF64F:
  .byte $ff
VgF650:
VgF651 = *+1
  .word VgF5BA
VgF652:
  .byte $d7
VgF653:
  .byte $7e
VgF654:
  .byte $73
VgF655:
  .byte $e1
VgF656:
  .byte $c0
VgF657:
  .byte $20
VgF658:
  .byte $21
VgF659:
  .byte $c0
VgF65A:
  .byte $10
VgF65B:
  .byte $11
VgF65C:
  .byte $c0
VgF65D:
  .byte $20
VgF65E:
  .byte $20
VgF65F:
  .byte $20
VgF660:
  .byte $e2
VgF661:
  .byte $91
VgF662:
  .byte $e1
VgF663:
  .byte $11
VgF664:
  .byte $fe
VgF665:
  .byte $04
VgF666:
VgF667 = *+1
  .word VgF656
VgF668:
  .byte $d7
VgF669:
  .byte $fd
VgF66A:
  .byte $73
VgF66B:
  .byte $c0
VgF66C:
  .byte $e2
VgF66D:
  .byte $50
VgF66E:
  .byte $51
VgF66F:
  .byte $a1
VgF670:
  .byte $80
VgF671:
  .byte $a0
VgF672:
  .byte $c0
VgF673:
  .byte $e1
VgF674:
  .byte $11
VgF675:
  .byte $10
VgF676:
  .byte $31
VgF677:
  .byte $c0
VgF678:
  .byte $e2
VgF679:
  .byte $50
VgF67A:
  .byte $51
VgF67B:
  .byte $a1
VgF67C:
  .byte $80
VgF67D:
  .byte $a0
VgF67E:
  .byte $c0
VgF67F:
  .byte $e1
VgF680:
  .byte $11
VgF681:
  .byte $10
VgF682:
  .byte $fe
VgF683:
  .byte $02
VgF684:
VgF685 = *+1
  .word VgF66B
VgF686:
  .byte $c0
VgF687:
  .byte $20
VgF688:
  .byte $21
VgF689:
  .byte $c0
VgF68A:
  .byte $10
VgF68B:
  .byte $11
VgF68C:
  .byte $c0
VgF68D:
  .byte $20
VgF68E:
  .byte $20
VgF68F:
  .byte $20
VgF690:
  .byte $e2
VgF691:
  .byte $91
VgF692:
  .byte $e1
VgF693:
  .byte $11
VgF694:
  .byte $fe
VgF695:
  .byte $02
VgF696:
VgF697 = *+1
  .word VgF686
VgF698:
  .byte $c0
VgF699:
  .byte $20
VgF69A:
  .byte $21
VgF69B:
  .byte $c0
VgF69C:
  .byte $11
VgF69D:
  .byte $e2
VgF69E:
  .byte $90
VgF69F:
  .byte $e1
VgF6A0:
  .byte $c0
VgF6A1:
  .byte $20
VgF6A2:
  .byte $21
VgF6A3:
  .byte $c0
VgF6A4:
  .byte $11
VgF6A5:
  .byte $e2
VgF6A6:
  .byte $90
VgF6A7:
  .byte $d5
VgF6A8:
  .byte $fe
VgF6A9:
  .byte $23
VgF6AA:
  .byte $e1
VgF6AB:
  .byte $21
VgF6AC:
  .byte $11
VgF6AD:
  .byte $21
VgF6AE:
  .byte $11
VgF6AF:
  .byte $e2
VgF6B0:
  .byte $91
VgF6B1:
  .byte $e1
VgF6B2:
  .byte $11
VgF6B3:
  .byte $21
VgF6B4:
  .byte $11
VgF6B5:
  .byte $fe
VgF6B6:
  .byte $ff
VgF6B7:
VgF6B8 = *+1
  .word VgF652
VgF6B9:
  .byte $d7
VgF6BA:
  .byte $10
VgF6BB:
  .byte $e3
VgF6BC:
  .byte $91
VgF6BD:
  .byte $e2
VgF6BE:
  .byte $10
VgF6BF:
  .byte $20
VgF6C0:
  .byte $21
VgF6C1:
  .byte $11
VgF6C2:
  .byte $d7
VgF6C3:
  .byte $28
VgF6C4:
  .byte $62
VgF6C5:
  .byte $d7
VgF6C6:
  .byte $10
VgF6C7:
  .byte $10
VgF6C8:
  .byte $21
VgF6C9:
  .byte $e3
VgF6CA:
  .byte $b1
VgF6CB:
  .byte $fe
VgF6CC:
  .byte $04
VgF6CD:
VgF6CE = *+1
  .word VgF6BC
VgF6CF:
  .byte $d7
VgF6D0:
  .byte $1a
VgF6D1:
  .byte $e2
VgF6D2:
  .byte $01
VgF6D3:
  .byte $d7
VgF6D4:
  .byte $10
VgF6D5:
  .byte $50
VgF6D6:
  .byte $30
VgF6D7:
  .byte $81
VgF6D8:
  .byte $41
VgF6D9:
  .byte $51
VgF6DA:
  .byte $21
VgF6DB:
  .byte $01
VgF6DC:
  .byte $01
VgF6DD:
  .byte $50
VgF6DE:
  .byte $30
VgF6DF:
  .byte $81
VgF6E0:
  .byte $41
VgF6E1:
  .byte $51
VgF6E2:
  .byte $21
VgF6E3:
  .byte $fe
VgF6E4:
  .byte $02
VgF6E5:
VgF6E6 = *+1
  .word VgF6CF
VgF6E7:
  .byte $e3
VgF6E8:
  .byte $91
VgF6E9:
  .byte $e2
VgF6EA:
  .byte $10
VgF6EB:
  .byte $20
VgF6EC:
  .byte $21
VgF6ED:
  .byte $11
VgF6EE:
  .byte $d7
VgF6EF:
  .byte $28
VgF6F0:
  .byte $62
VgF6F1:
  .byte $d7
VgF6F2:
  .byte $10
VgF6F3:
  .byte $10
VgF6F4:
  .byte $21
VgF6F5:
  .byte $e3
VgF6F6:
  .byte $b1
VgF6F7:
  .byte $fe
VgF6F8:
  .byte $02
VgF6F9:
VgF6FA = *+1
  .word VgF6E8
VgF6FB:
  .byte $91
VgF6FC:
  .byte $e2
VgF6FD:
  .byte $10
VgF6FE:
  .byte $20
VgF6FF:
  .byte $21
VgF700:
  .byte $11
VgF701:
  .byte $e3
VgF702:
  .byte $91
VgF703:
  .byte $e2
VgF704:
  .byte $10
VgF705:
  .byte $20
VgF706:
  .byte $21
VgF707:
  .byte $11
VgF708:
  .byte $d5
VgF709:
  .byte $10
VgF70A:
  .byte $e3
VgF70B:
  .byte $91
VgF70C:
  .byte $e2
VgF70D:
  .byte $11
VgF70E:
  .byte $21
VgF70F:
  .byte $11
VgF710:
  .byte $21
VgF711:
  .byte $11
VgF712:
  .byte $21
VgF713:
  .byte $11
VgF714:
  .byte $fe
VgF715:
  .byte $ff
VgF716:
VgF717 = *+1
  .word VgF6B9
VgF718:
  .byte $d6
VgF719:
  .byte $3f
VgF71A:
  .byte $f0
VgF71B:
  .byte $e1
VgF71C:
  .byte $60
VgF71D:
  .byte $30
VgF71E:
  .byte $e2
VgF71F:
  .byte $b0
VgF720:
  .byte $fe
VgF721:
  .byte $04
VgF722:
VgF723 = *+1
  .word VgF71B
VgF724:
  .byte $e1
VgF725:
  .byte $b0
VgF726:
  .byte $60
VgF727:
  .byte $30
VgF728:
  .byte $fe
VgF729:
  .byte $04
VgF72A:
VgF72B = *+1
  .word VgF724
VgF72C:
  .byte $e0
VgF72D:
  .byte $30
VgF72E:
  .byte $e1
VgF72F:
  .byte $b0
VgF730:
  .byte $60
VgF731:
  .byte $30
VgF732:
  .byte $60
VgF733:
  .byte $b0
VgF734:
  .byte $e0
VgF735:
  .byte $60
VgF736:
  .byte $30
VgF737:
  .byte $e1
VgF738:
  .byte $b0
VgF739:
  .byte $60
VgF73A:
  .byte $b0
VgF73B:
  .byte $e0
VgF73C:
  .byte $30
VgF73D:
  .byte $b0
VgF73E:
  .byte $60
VgF73F:
  .byte $30
VgF740:
  .byte $60
VgF741:
  .byte $30
VgF742:
  .byte $e1
VgF743:
  .byte $b0
VgF744:
  .byte $d6
VgF745:
  .byte $ff
VgF746:
  .byte $d3
VgF747:
  .byte $e0
VgF748:
  .byte $33
VgF749:
  .byte $ff
VgF74A:
  .byte $d6
VgF74B:
  .byte $3f
VgF74C:
  .byte $77
VgF74D:
  .byte $e2
VgF74E:
  .byte $30
VgF74F:
  .byte $e3
VgF750:
  .byte $b0
VgF751:
  .byte $60
VgF752:
  .byte $fe
VgF753:
  .byte $04
VgF754:
VgF755 = *+1
  .word VgF74D
VgF756:
  .byte $e2
VgF757:
  .byte $60
VgF758:
  .byte $30
VgF759:
  .byte $e3
VgF75A:
  .byte $b0
VgF75B:
  .byte $fe
VgF75C:
  .byte $04
VgF75D:
VgF75E = *+1
  .word VgF756
VgF75F:
  .byte $e2
VgF760:
  .byte $b0
VgF761:
  .byte $60
VgF762:
  .byte $30
VgF763:
  .byte $e3
VgF764:
  .byte $b0
VgF765:
  .byte $e2
VgF766:
  .byte $30
VgF767:
  .byte $60
VgF768:
  .byte $e1
VgF769:
  .byte $30
VgF76A:
  .byte $e2
VgF76B:
  .byte $b0
VgF76C:
  .byte $60
VgF76D:
  .byte $30
VgF76E:
  .byte $60
VgF76F:
  .byte $b0
VgF770:
  .byte $e1
VgF771:
  .byte $60
VgF772:
  .byte $30
VgF773:
  .byte $e2
VgF774:
  .byte $b0
VgF775:
  .byte $e1
VgF776:
  .byte $30
VgF777:
  .byte $e2
VgF778:
  .byte $b0
VgF779:
  .byte $60
VgF77A:
  .byte $d6
VgF77B:
  .byte $ff
VgF77C:
  .byte $d3
VgF77D:
  .byte $b3
VgF77E:
  .byte $ff
VgF77F:
  .byte $d6
VgF780:
  .byte $30
VgF781:
  .byte $e3
VgF782:
  .byte $b3
VgF783:
  .byte $d6
VgF784:
  .byte $11
VgF785:
  .byte $b0
VgF786:
  .byte $b0
VgF787:
  .byte $d6
VgF788:
  .byte $30
VgF789:
  .byte $b2
VgF78A:
  .byte $62
VgF78B:
  .byte $e2
VgF78C:
  .byte $33
VgF78D:
  .byte $d6
VgF78E:
  .byte $11
VgF78F:
  .byte $30
VgF790:
  .byte $30
VgF791:
  .byte $d6
VgF792:
  .byte $30
VgF793:
  .byte $32
VgF794:
  .byte $e3
VgF795:
  .byte $b2
VgF796:
  .byte $e2
VgF797:
  .byte $63
VgF798:
  .byte $d6
VgF799:
  .byte $11
VgF79A:
  .byte $60
VgF79B:
  .byte $60
VgF79C:
  .byte $d6
VgF79D:
  .byte $30
VgF79E:
  .byte $62
VgF79F:
  .byte $e3
VgF7A0:
  .byte $b2
VgF7A1:
  .byte $e2
VgF7A2:
  .byte $b3
VgF7A3:
  .byte $d6
VgF7A4:
  .byte $0e
VgF7A5:
  .byte $e3
VgF7A6:
  .byte $b0
VgF7A7:
  .byte $b0
VgF7A8:
  .byte $d6
VgF7A9:
  .byte $30
VgF7AA:
  .byte $b3
VgF7AB:
  .byte $ff
VgF7AC:
  .byte $d6
VgF7AD:
  .byte $fd
VgF7AE:
  .byte $53
VgF7AF:
  .byte $e1
VgF7B0:
  .byte $02
VgF7B1:
  .byte $01
VgF7B2:
  .byte $00
VgF7B3:
  .byte $01
VgF7B4:
  .byte $21
VgF7B5:
  .byte $21
VgF7B6:
  .byte $e3
VgF7B7:
  .byte $71
VgF7B8:
  .byte $71
VgF7B9:
  .byte $e1
VgF7BA:
  .byte $32
VgF7BB:
  .byte $32
VgF7BC:
  .byte $51
VgF7BD:
  .byte $51
VgF7BE:
  .byte $e3
VgF7BF:
  .byte $71
VgF7C0:
  .byte $70
VgF7C1:
  .byte $71
VgF7C2:
  .byte $70
VgF7C3:
  .byte $d6
VgF7C4:
  .byte $bf
VgF7C5:
  .byte $65
VgF7C6:
  .byte $e1
VgF7C7:
  .byte $77
VgF7C8:
  .byte $50
VgF7C9:
  .byte $40
VgF7CA:
  .byte $00
VgF7CB:
  .byte $e2
VgF7CC:
  .byte $74
VgF7CD:
  .byte $50
VgF7CE:
  .byte $40
VgF7CF:
  .byte $00
VgF7D0:
  .byte $e3
VgF7D1:
  .byte $74
VgF7D2:
  .byte $e2
VgF7D3:
  .byte $42
VgF7D4:
  .byte $72
VgF7D5:
  .byte $e1
VgF7D6:
  .byte $01
VgF7D7:
  .byte $77
VgF7D8:
  .byte $50
VgF7D9:
  .byte $40
VgF7DA:
  .byte $00
VgF7DB:
  .byte $e2
VgF7DC:
  .byte $74
VgF7DD:
  .byte $50
VgF7DE:
  .byte $40
VgF7DF:
  .byte $00
VgF7E0:
  .byte $e3
VgF7E1:
  .byte $74
VgF7E2:
  .byte $e2
VgF7E3:
  .byte $72
VgF7E4:
  .byte $e1
VgF7E5:
  .byte $02
VgF7E6:
  .byte $41
VgF7E7:
  .byte $77
VgF7E8:
  .byte $50
VgF7E9:
  .byte $40
VgF7EA:
  .byte $00
VgF7EB:
  .byte $e2
VgF7EC:
  .byte $52
VgF7ED:
  .byte $20
VgF7EE:
  .byte $40
VgF7EF:
  .byte $d4
VgF7F0:
  .byte $bd
VgF7F1:
  .byte $64
VgF7F2:
  .byte $53
VgF7F3:
  .byte $43
VgF7F4:
  .byte $53
VgF7F5:
  .byte $73
VgF7F6:
  .byte $53
VgF7F7:
  .byte $73
VgF7F8:
  .byte $d6
VgF7F9:
  .byte $be
VgF7FA:
  .byte $73
VgF7FB:
  .byte $80
VgF7FC:
  .byte $a0
VgF7FD:
  .byte $e1
VgF7FE:
  .byte $00
VgF7FF:
  .byte $20
VgF800:
  .byte $30
VgF801:
  .byte $20
VgF802:
  .byte $00
VgF803:
  .byte $e2
VgF804:
  .byte $a0
VgF805:
  .byte $80
VgF806:
  .byte $a0
VgF807:
  .byte $80
VgF808:
  .byte $70
VgF809:
  .byte $50
VgF80A:
  .byte $70
VgF80B:
  .byte $50
VgF80C:
  .byte $30
VgF80D:
  .byte $22
VgF80E:
  .byte $52
VgF80F:
  .byte $a2
VgF810:
  .byte $e1
VgF811:
  .byte $32
VgF812:
  .byte $83
VgF813:
  .byte $d6
VgF814:
  .byte $bf
VgF815:
  .byte $65
VgF816:
  .byte $77
VgF817:
  .byte $50
VgF818:
  .byte $40
VgF819:
  .byte $00
VgF81A:
  .byte $e2
VgF81B:
  .byte $71
VgF81C:
  .byte $70
VgF81D:
  .byte $e1
VgF81E:
  .byte $01
VgF81F:
  .byte $20
VgF820:
  .byte $31
VgF821:
  .byte $34
VgF822:
  .byte $30
VgF823:
  .byte $51
VgF824:
  .byte $54
VgF825:
  .byte $50
VgF826:
  .byte $71
VgF827:
  .byte $71
VgF828:
  .byte $50
VgF829:
  .byte $79
VgF82A:
  .byte $fe
VgF82B:
  .byte $ff
VgF82C:
VgF82D = *+1
  .word VgF7AC
VgF82E:
  .byte $d6
VgF82F:
  .byte $1f
VgF830:
  .byte $e1
VgF831:
  .byte $92
VgF832:
  .byte $d6
VgF833:
  .byte $11
VgF834:
  .byte $91
VgF835:
  .byte $90
VgF836:
  .byte $91
VgF837:
  .byte $b1
VgF838:
  .byte $b1
VgF839:
  .byte $d6
VgF83A:
  .byte $12
VgF83B:
  .byte $e3
VgF83C:
  .byte $71
VgF83D:
  .byte $71
VgF83E:
  .byte $d6
VgF83F:
  .byte $1d
VgF840:
  .byte $e0
VgF841:
  .byte $02
VgF842:
  .byte $02
VgF843:
  .byte $21
VgF844:
  .byte $21
VgF845:
  .byte $d6
VgF846:
  .byte $12
VgF847:
  .byte $e3
VgF848:
  .byte $71
VgF849:
  .byte $70
VgF84A:
  .byte $71
VgF84B:
  .byte $70
VgF84C:
  .byte $e2
VgF84D:
  .byte $01
VgF84E:
  .byte $e1
VgF84F:
  .byte $01
VgF850:
  .byte $fe
VgF851:
  .byte $08
VgF852:
VgF853 = *+1
  .word VgF84C
VgF854:
  .byte $e3
VgF855:
  .byte $a1
VgF856:
  .byte $e2
VgF857:
  .byte $a1
VgF858:
  .byte $fe
VgF859:
  .byte $08
VgF85A:
VgF85B = *+1
  .word VgF854
VgF85C:
  .byte $e3
VgF85D:
  .byte $91
VgF85E:
  .byte $e2
VgF85F:
  .byte $91
VgF860:
  .byte $fe
VgF861:
  .byte $04
VgF862:
VgF863 = *+1
  .word VgF85C
VgF864:
  .byte $e3
VgF865:
  .byte $21
VgF866:
  .byte $e2
VgF867:
  .byte $21
VgF868:
  .byte $e3
VgF869:
  .byte $21
VgF86A:
  .byte $e2
VgF86B:
  .byte $21
VgF86C:
  .byte $e3
VgF86D:
  .byte $41
VgF86E:
  .byte $e2
VgF86F:
  .byte $41
VgF870:
  .byte $e3
VgF871:
  .byte $41
VgF872:
  .byte $e2
VgF873:
  .byte $41
VgF874:
  .byte $e3
VgF875:
  .byte $51
VgF876:
  .byte $e2
VgF877:
  .byte $51
VgF878:
  .byte $fe
VgF879:
  .byte $04
VgF87A:
VgF87B = *+1
  .word VgF874
VgF87C:
  .byte $e3
VgF87D:
  .byte $71
VgF87E:
  .byte $e2
VgF87F:
  .byte $71
VgF880:
  .byte $fe
VgF881:
  .byte $04
VgF882:
VgF883 = *+1
  .word VgF87C
VgF884:
  .byte $e3
VgF885:
  .byte $01
VgF886:
  .byte $e2
VgF887:
  .byte $01
VgF888:
  .byte $fe
VgF889:
  .byte $04
VgF88A:
VgF88B = *+1
  .word VgF884
VgF88C:
  .byte $e3
VgF88D:
  .byte $31
VgF88E:
  .byte $e2
VgF88F:
  .byte $31
VgF890:
  .byte $e3
VgF891:
  .byte $31
VgF892:
  .byte $d6
VgF893:
  .byte $10
VgF894:
  .byte $e2
VgF895:
  .byte $30
VgF896:
  .byte $30
VgF897:
  .byte $e3
VgF898:
  .byte $51
VgF899:
  .byte $e2
VgF89A:
  .byte $51
VgF89B:
  .byte $e3
VgF89C:
  .byte $51
VgF89D:
  .byte $e2
VgF89E:
  .byte $50
VgF89F:
  .byte $50
VgF8A0:
  .byte $00
VgF8A1:
  .byte $01
VgF8A2:
  .byte $01
VgF8A3:
  .byte $00
VgF8A4:
  .byte $d6
VgF8A5:
  .byte $81
VgF8A6:
  .byte $09
VgF8A7:
  .byte $fe
VgF8A8:
  .byte $ff
VgF8A9:
VgF8AA = *+1
  .word VgF82E
VgF8AB:
  .byte $da
VgF8AC:
  .byte $7b
VgF8AD:
  .byte $45
VgF8AE:
  .byte $e2
VgF8AF:
  .byte $40
VgF8B0:
  .byte $90
VgF8B1:
  .byte $40
VgF8B2:
  .byte $91
VgF8B3:
  .byte $40
VgF8B4:
  .byte $41
VgF8B5:
  .byte $40
VgF8B6:
  .byte $61
VgF8B7:
  .byte $70
VgF8B8:
  .byte $77
VgF8B9:
  .byte $40
VgF8BA:
  .byte $60
VgF8BB:
  .byte $70
VgF8BC:
  .byte $60
VgF8BD:
  .byte $40
VgF8BE:
  .byte $90
VgF8BF:
  .byte $40
VgF8C0:
  .byte $91
VgF8C1:
  .byte $42
VgF8C2:
  .byte $90
VgF8C3:
  .byte $b1
VgF8C4:
  .byte $e1
VgF8C5:
  .byte $07
VgF8C6:
  .byte $e2
VgF8C7:
  .byte $b0
VgF8C8:
  .byte $e1
VgF8C9:
  .byte $00
VgF8CA:
  .byte $e2
VgF8CB:
  .byte $b0
VgF8CC:
  .byte $90
VgF8CD:
  .byte $70
VgF8CE:
  .byte $90
VgF8CF:
  .byte $e1
VgF8D0:
  .byte $20
VgF8D1:
  .byte $e2
VgF8D2:
  .byte $90
VgF8D3:
  .byte $e1
VgF8D4:
  .byte $21
VgF8D5:
  .byte $e2
VgF8D6:
  .byte $92
VgF8D7:
  .byte $e1
VgF8D8:
  .byte $20
VgF8D9:
  .byte $00
VgF8DA:
  .byte $e2
VgF8DB:
  .byte $b0
VgF8DC:
  .byte $90
VgF8DD:
  .byte $e1
VgF8DE:
  .byte $00
VgF8DF:
  .byte $50
VgF8E0:
  .byte $00
VgF8E1:
  .byte $51
VgF8E2:
  .byte $02
VgF8E3:
  .byte $50
VgF8E4:
  .byte $40
VgF8E5:
  .byte $20
VgF8E6:
  .byte $00
VgF8E7:
  .byte $46
VgF8E8:
  .byte $20
VgF8E9:
  .byte $70
VgF8EA:
  .byte $00
VgF8EB:
  .byte $50
VgF8EC:
  .byte $e2
VgF8ED:
  .byte $b0
VgF8EE:
  .byte $e1
VgF8EF:
  .byte $45
VgF8F0:
  .byte $da
VgF8F1:
  .byte $fc
VgF8F2:
  .byte $89
VgF8F3:
  .byte $e3
VgF8F4:
  .byte $b0
VgF8F5:
  .byte $e2
VgF8F6:
  .byte $40
VgF8F7:
  .byte $e3
VgF8F8:
  .byte $b0
VgF8F9:
  .byte $e2
VgF8FA:
  .byte $20
VgF8FB:
  .byte $e3
VgF8FC:
  .byte $b0
VgF8FD:
  .byte $e2
VgF8FE:
  .byte $40
VgF8FF:
  .byte $e1
VgF900:
  .byte $00
VgF901:
  .byte $01
VgF902:
  .byte $02
VgF903:
  .byte $c0
VgF904:
  .byte $31
VgF905:
  .byte $31
VgF906:
  .byte $20
VgF907:
  .byte $e2
VgF908:
  .byte $01
VgF909:
  .byte $21
VgF90A:
  .byte $31
VgF90B:
  .byte $21
VgF90C:
  .byte $01
VgF90D:
  .byte $21
VgF90E:
  .byte $c0
VgF90F:
  .byte $b1
VgF910:
  .byte $b1
VgF911:
  .byte $e1
VgF912:
  .byte $20
VgF913:
  .byte $11
VgF914:
  .byte $20
VgF915:
  .byte $10
VgF916:
  .byte $e2
VgF917:
  .byte $b0
VgF918:
  .byte $90
VgF919:
  .byte $e3
VgF91A:
  .byte $b1
VgF91B:
  .byte $e2
VgF91C:
  .byte $11
VgF91D:
  .byte $21
VgF91E:
  .byte $11
VgF91F:
  .byte $21
VgF920:
  .byte $11
VgF921:
  .byte $c0
VgF922:
  .byte $e1
VgF923:
  .byte $01
VgF924:
  .byte $02
VgF925:
  .byte $70
VgF926:
  .byte $70
VgF927:
  .byte $70
VgF928:
  .byte $70
VgF929:
  .byte $60
VgF92A:
  .byte $70
VgF92B:
  .byte $e3
VgF92C:
  .byte $01
VgF92D:
  .byte $21
VgF92E:
  .byte $31
VgF92F:
  .byte $21
VgF930:
  .byte $30
VgF931:
  .byte $30
VgF932:
  .byte $51
VgF933:
  .byte $da
VgF934:
  .byte $7c
VgF935:
  .byte $33
VgF936:
  .byte $e1
VgF937:
  .byte $94
VgF938:
  .byte $90
VgF939:
  .byte $64
VgF93A:
  .byte $60
VgF93B:
  .byte $33
VgF93C:
  .byte $20
VgF93D:
  .byte $10
VgF93E:
  .byte $da
VgF93F:
  .byte $fc
VgF940:
  .byte $89
VgF941:
  .byte $01
VgF942:
  .byte $e2
VgF943:
  .byte $b1
VgF944:
  .byte $a1
VgF945:
  .byte $da
VgF946:
  .byte $fb
VgF947:
  .byte $33
VgF948:
  .byte $9b
VgF949:
  .byte $fe
VgF94A:
  .byte $ff
VgF94B:
VgF94C = *+1
  .word VgF8AB
VgF94D:
  .byte $d5
VgF94E:
  .byte $12
VgF94F:
  .byte $e3
VgF950:
  .byte $91
VgF951:
  .byte $e2
VgF952:
  .byte $41
VgF953:
  .byte $fe
VgF954:
  .byte $06
VgF955:
VgF956 = *+1
  .word VgF94F
VgF957:
  .byte $01
VgF958:
  .byte $71
VgF959:
  .byte $fe
VgF95A:
  .byte $04
VgF95B:
VgF95C = *+1
  .word VgF957
VgF95D:
  .byte $01
VgF95E:
  .byte $e3
VgF95F:
  .byte $b1
VgF960:
  .byte $e2
VgF961:
  .byte $61
VgF962:
  .byte $e3
VgF963:
  .byte $b1
VgF964:
  .byte $e3
VgF965:
  .byte $91
VgF966:
  .byte $e2
VgF967:
  .byte $41
VgF968:
  .byte $e3
VgF969:
  .byte $91
VgF96A:
  .byte $e2
VgF96B:
  .byte $41
VgF96C:
  .byte $e3
VgF96D:
  .byte $91
VgF96E:
  .byte $e2
VgF96F:
  .byte $41
VgF970:
  .byte $fe
VgF971:
  .byte $02
VgF972:
VgF973 = *+1
  .word VgF964
VgF974:
  .byte $01
VgF975:
  .byte $71
VgF976:
  .byte $fe
VgF977:
  .byte $06
VgF978:
VgF979 = *+1
  .word VgF974
VgF97A:
  .byte $21
VgF97B:
  .byte $91
VgF97C:
  .byte $fe
VgF97D:
  .byte $06
VgF97E:
VgF97F = *+1
  .word VgF97A
VgF980:
  .byte $e2
VgF981:
  .byte $51
VgF982:
  .byte $e1
VgF983:
  .byte $01
VgF984:
  .byte $fe
VgF985:
  .byte $06
VgF986:
VgF987 = *+1
  .word VgF980
VgF988:
  .byte $e2
VgF989:
  .byte $41
VgF98A:
  .byte $b1
VgF98B:
  .byte $fe
VgF98C:
  .byte $06
VgF98D:
VgF98E = *+1
  .word VgF988
VgF98F:
  .byte $e3
VgF990:
  .byte $b1
VgF991:
  .byte $e2
VgF992:
  .byte $41
VgF993:
  .byte $e3
VgF994:
  .byte $b1
VgF995:
  .byte $e2
VgF996:
  .byte $21
VgF997:
  .byte $e3
VgF998:
  .byte $b1
VgF999:
  .byte $e2
VgF99A:
  .byte $41
VgF99B:
  .byte $fe
VgF99C:
  .byte $02
VgF99D:
VgF99E = *+1
  .word VgF98F
VgF99F:
  .byte $e3
VgF9A0:
  .byte $51
VgF9A1:
  .byte $e2
VgF9A2:
  .byte $01
VgF9A3:
  .byte $e3
VgF9A4:
  .byte $51
VgF9A5:
  .byte $e2
VgF9A6:
  .byte $31
VgF9A7:
  .byte $e3
VgF9A8:
  .byte $51
VgF9A9:
  .byte $e2
VgF9AA:
  .byte $51
VgF9AB:
  .byte $fe
VgF9AC:
  .byte $02
VgF9AD:
VgF9AE = *+1
  .word VgF99F
VgF9AF:
  .byte $fd
VgF9B0:
VgF9B1 = *+1
  .word VgFA18
VgF9B2:
  .byte $e3
VgF9B3:
  .byte $71
VgF9B4:
  .byte $e2
VgF9B5:
  .byte $21
VgF9B6:
  .byte $e3
VgF9B7:
  .byte $41
VgF9B8:
  .byte $b1
VgF9B9:
  .byte $41
VgF9BA:
  .byte $e2
VgF9BB:
  .byte $21
VgF9BC:
  .byte $e3
VgF9BD:
  .byte $41
VgF9BE:
  .byte $e2
VgF9BF:
  .byte $41
VgF9C0:
  .byte $fe
VgF9C1:
  .byte $02
VgF9C2:
VgF9C3 = *+1
  .word VgF9B6
VgF9C4:
  .byte $e3
VgF9C5:
  .byte $41
VgF9C6:
  .byte $b1
VgF9C7:
  .byte $61
VgF9C8:
  .byte $e2
VgF9C9:
  .byte $11
VgF9CA:
  .byte $e3
VgF9CB:
  .byte $71
VgF9CC:
  .byte $e2
VgF9CD:
  .byte $21
VgF9CE:
  .byte $e3
VgF9CF:
  .byte $61
VgF9D0:
  .byte $e2
VgF9D1:
  .byte $11
VgF9D2:
  .byte $fe
VgF9D3:
  .byte $02
VgF9D4:
VgF9D5 = *+1
  .word VgF9CA
VgF9D6:
  .byte $e3
VgF9D7:
  .byte $51
VgF9D8:
  .byte $e2
VgF9D9:
  .byte $01
VgF9DA:
  .byte $e3
VgF9DB:
  .byte $51
VgF9DC:
  .byte $e2
VgF9DD:
  .byte $31
VgF9DE:
  .byte $e3
VgF9DF:
  .byte $51
VgF9E0:
  .byte $e2
VgF9E1:
  .byte $51
VgF9E2:
  .byte $fe
VgF9E3:
  .byte $02
VgF9E4:
VgF9E5 = *+1
  .word VgF9D6
VgF9E6:
  .byte $fd
VgF9E7:
VgF9E8 = *+1
  .word VgFA18
VgF9E9:
  .byte $e3
VgF9EA:
  .byte $a1
VgF9EB:
  .byte $e2
VgF9EC:
  .byte $51
VgF9ED:
  .byte $fd
VgF9EE:
VgF9EF = *+1
  .word VgFA2D
VgF9F0:
  .byte $e3
VgF9F1:
  .byte $61
VgF9F2:
  .byte $e2
VgF9F3:
  .byte $11
VgF9F4:
  .byte $e3
VgF9F5:
  .byte $61
VgF9F6:
  .byte $e2
VgF9F7:
  .byte $41
VgF9F8:
  .byte $e3
VgF9F9:
  .byte $61
VgF9FA:
  .byte $e2
VgF9FB:
  .byte $61
VgF9FC:
  .byte $e3
VgF9FD:
  .byte $31
VgF9FE:
  .byte $a1
VgF9FF:
  .byte $31
VgFA00:
  .byte $e2
VgFA01:
  .byte $11
VgFA02:
  .byte $e3
VgFA03:
  .byte $31
VgFA04:
  .byte $e2
VgFA05:
  .byte $31
VgFA06:
  .byte $e3
VgFA07:
  .byte $01
VgFA08:
  .byte $71
VgFA09:
  .byte $01
VgFA0A:
  .byte $a1
VgFA0B:
  .byte $01
VgFA0C:
  .byte $e2
VgFA0D:
  .byte $01
VgFA0E:
  .byte $fd
VgFA0F:
VgFA10 = *+1
  .word VgFA2D
VgFA11:
  .byte $fd
VgFA12:
VgFA13 = *+1
  .word VgFA2D
VgFA14:
  .byte $fe
VgFA15:
  .byte $ff
VgFA16:
VgFA17 = *+1
  .word VgF94D
VgFA18:
  .byte $e3
VgFA19:
  .byte $51
VgFA1A:
  .byte $e2
VgFA1B:
  .byte $01
VgFA1C:
  .byte $e3
VgFA1D:
  .byte $71
VgFA1E:
  .byte $e2
VgFA1F:
  .byte $21
VgFA20:
  .byte $e3
VgFA21:
  .byte $81
VgFA22:
  .byte $e2
VgFA23:
  .byte $31
VgFA24:
  .byte $e3
VgFA25:
  .byte $71
VgFA26:
  .byte $e2
VgFA27:
  .byte $21
VgFA28:
  .byte $e3
VgFA29:
  .byte $81
VgFA2A:
  .byte $e2
VgFA2B:
  .byte $31
VgFA2C:
  .byte $ff
VgFA2D:
  .byte $e3
VgFA2E:
  .byte $91
VgFA2F:
  .byte $e2
VgFA30:
  .byte $41
VgFA31:
  .byte $e3
VgFA32:
  .byte $91
VgFA33:
  .byte $e2
VgFA34:
  .byte $71
VgFA35:
  .byte $e3
VgFA36:
  .byte $91
VgFA37:
  .byte $e2
VgFA38:
  .byte $91
VgFA39:
  .byte $ff
VgFA3A:
  .byte $d5
VgFA3B:
  .byte $7e
VgFA3C:
  .byte $55
VgFA3D:
  .byte $e2
VgFA3E:
  .byte $31
VgFA3F:
  .byte $a1
VgFA40:
  .byte $31
VgFA41:
  .byte $a1
VgFA42:
  .byte $c1
VgFA43:
  .byte $31
VgFA44:
  .byte $d5
VgFA45:
  .byte $b9
VgFA46:
  .byte $31
VgFA47:
  .byte $e1
VgFA48:
  .byte $a1
VgFA49:
  .byte $e0
VgFA4A:
  .byte $31
VgFA4B:
  .byte $e1
VgFA4C:
  .byte $a1
VgFA4D:
  .byte $e0
VgFA4E:
  .byte $31
VgFA4F:
  .byte $c1
VgFA50:
  .byte $e1
VgFA51:
  .byte $a1
VgFA52:
  .byte $d5
VgFA53:
  .byte $7e
VgFA54:
  .byte $55
VgFA55:
  .byte $e2
VgFA56:
  .byte $21
VgFA57:
  .byte $91
VgFA58:
  .byte $21
VgFA59:
  .byte $91
VgFA5A:
  .byte $c1
VgFA5B:
  .byte $21
VgFA5C:
  .byte $d5
VgFA5D:
  .byte $b9
VgFA5E:
  .byte $31
VgFA5F:
  .byte $e1
VgFA60:
  .byte $91
VgFA61:
  .byte $e0
VgFA62:
  .byte $21
VgFA63:
  .byte $e1
VgFA64:
  .byte $91
VgFA65:
  .byte $e0
VgFA66:
  .byte $21
VgFA67:
  .byte $c1
VgFA68:
  .byte $e1
VgFA69:
  .byte $91
VgFA6A:
  .byte $d5
VgFA6B:
  .byte $7e
VgFA6C:
  .byte $55
VgFA6D:
  .byte $e2
VgFA6E:
  .byte $31
VgFA6F:
  .byte $a1
VgFA70:
  .byte $31
VgFA71:
  .byte $a1
VgFA72:
  .byte $c1
VgFA73:
  .byte $31
VgFA74:
  .byte $d5
VgFA75:
  .byte $b9
VgFA76:
  .byte $31
VgFA77:
  .byte $e1
VgFA78:
  .byte $a1
VgFA79:
  .byte $e0
VgFA7A:
  .byte $31
VgFA7B:
  .byte $e1
VgFA7C:
  .byte $a1
VgFA7D:
  .byte $e0
VgFA7E:
  .byte $31
VgFA7F:
  .byte $c1
VgFA80:
  .byte $e1
VgFA81:
  .byte $a1
VgFA82:
  .byte $d5
VgFA83:
  .byte $7f
VgFA84:
  .byte $55
VgFA85:
  .byte $e2
VgFA86:
  .byte $61
VgFA87:
  .byte $e1
VgFA88:
  .byte $11
VgFA89:
  .byte $e2
VgFA8A:
  .byte $61
VgFA8B:
  .byte $e1
VgFA8C:
  .byte $53
VgFA8D:
  .byte $33
VgFA8E:
  .byte $13
VgFA8F:
  .byte $01
VgFA90:
  .byte $11
VgFA91:
  .byte $11
VgFA92:
  .byte $e2
VgFA93:
  .byte $31
VgFA94:
  .byte $a1
VgFA95:
  .byte $31
VgFA96:
  .byte $a1
VgFA97:
  .byte $31
VgFA98:
  .byte $a1
VgFA99:
  .byte $d5
VgFA9A:
  .byte $ba
VgFA9B:
  .byte $31
VgFA9C:
  .byte $e0
VgFA9D:
  .byte $31
VgFA9E:
  .byte $a1
VgFA9F:
  .byte $31
VgFAA0:
  .byte $a1
VgFAA1:
  .byte $31
VgFAA2:
  .byte $a1
VgFAA3:
  .byte $d5
VgFAA4:
  .byte $7e
VgFAA5:
  .byte $55
VgFAA6:
  .byte $e2
VgFAA7:
  .byte $21
VgFAA8:
  .byte $91
VgFAA9:
  .byte $21
VgFAAA:
  .byte $91
VgFAAB:
  .byte $21
VgFAAC:
  .byte $91
VgFAAD:
  .byte $d5
VgFAAE:
  .byte $ba
VgFAAF:
  .byte $31
VgFAB0:
  .byte $e0
VgFAB1:
  .byte $21
VgFAB2:
  .byte $91
VgFAB3:
  .byte $21
VgFAB4:
  .byte $91
VgFAB5:
  .byte $21
VgFAB6:
  .byte $91
VgFAB7:
  .byte $d5
VgFAB8:
  .byte $7e
VgFAB9:
  .byte $55
VgFABA:
  .byte $e2
VgFABB:
  .byte $11
VgFABC:
  .byte $81
VgFABD:
  .byte $11
VgFABE:
  .byte $81
VgFABF:
  .byte $c1
VgFAC0:
  .byte $e1
VgFAC1:
  .byte $11
VgFAC2:
  .byte $e2
VgFAC3:
  .byte $01
VgFAC4:
  .byte $61
VgFAC5:
  .byte $01
VgFAC6:
  .byte $61
VgFAC7:
  .byte $c1
VgFAC8:
  .byte $e1
VgFAC9:
  .byte $01
VgFACA:
  .byte $c1
VgFACB:
  .byte $e2
VgFACC:
  .byte $b1
VgFACD:
  .byte $b1
VgFACE:
  .byte $b1
VgFACF:
  .byte $b1
VgFAD0:
  .byte $c1
VgFAD1:
  .byte $a1
VgFAD2:
  .byte $c1
VgFAD3:
  .byte $b1
VgFAD4:
  .byte $c3
VgFAD5:
  .byte $e1
VgFAD6:
  .byte $05
VgFAD7:
  .byte $31
VgFAD8:
  .byte $73
VgFAD9:
  .byte $6d
VgFADA:
  .byte $fe
VgFADB:
  .byte $ff
VgFADC:
VgFADD = *+1
  .word VgFA3D
VgFADE:
  .byte $d5
VgFADF:
  .byte $12
VgFAE0:
  .byte $e2
VgFAE1:
  .byte $01
VgFAE2:
  .byte $61
VgFAE3:
  .byte $a1
VgFAE4:
  .byte $fe
VgFAE5:
  .byte $04
VgFAE6:
VgFAE7 = *+1
  .word VgFAE1
VgFAE8:
  .byte $e3
VgFAE9:
  .byte $b1
VgFAEA:
  .byte $e2
VgFAEB:
  .byte $51
VgFAEC:
  .byte $91
VgFAED:
  .byte $fe
VgFAEE:
  .byte $04
VgFAEF:
VgFAF0 = *+1
  .word VgFAE8
VgFAF1:
  .byte $01
VgFAF2:
  .byte $61
VgFAF3:
  .byte $a1
VgFAF4:
  .byte $fe
VgFAF5:
  .byte $04
VgFAF6:
VgFAF7 = *+1
  .word VgFAF1
VgFAF8:
  .byte $e2
VgFAF9:
  .byte $31
VgFAFA:
  .byte $a1
VgFAFB:
  .byte $e1
VgFAFC:
  .byte $11
VgFAFD:
  .byte $fe
VgFAFE:
  .byte $04
VgFAFF:
VgFB00 = *+1
  .word VgFAF8
VgFB01:
  .byte $e2
VgFB02:
  .byte $01
VgFB03:
  .byte $61
VgFB04:
  .byte $a1
VgFB05:
  .byte $fe
VgFB06:
  .byte $04
VgFB07:
VgFB08 = *+1
  .word VgFB02
VgFB09:
  .byte $e3
VgFB0A:
  .byte $b1
VgFB0B:
  .byte $e2
VgFB0C:
  .byte $51
VgFB0D:
  .byte $91
VgFB0E:
  .byte $fe
VgFB0F:
  .byte $04
VgFB10:
VgFB11 = *+1
  .word VgFB09
VgFB12:
  .byte $e3
VgFB13:
  .byte $81
VgFB14:
  .byte $e2
VgFB15:
  .byte $41
VgFB16:
  .byte $81
VgFB17:
  .byte $e3
VgFB18:
  .byte $81
VgFB19:
  .byte $e2
VgFB1A:
  .byte $41
VgFB1B:
  .byte $81
VgFB1C:
  .byte $e3
VgFB1D:
  .byte $91
VgFB1E:
  .byte $e2
VgFB1F:
  .byte $31
VgFB20:
  .byte $71
VgFB21:
  .byte $e3
VgFB22:
  .byte $91
VgFB23:
  .byte $e2
VgFB24:
  .byte $31
VgFB25:
  .byte $73
VgFB26:
  .byte $21
VgFB27:
  .byte $21
VgFB28:
  .byte $21
VgFB29:
  .byte $23
VgFB2A:
  .byte $13
VgFB2B:
  .byte $21
VgFB2C:
  .byte $c3
VgFB2D:
  .byte $d5
VgFB2E:
  .byte $81
VgFB2F:
  .byte $3b
VgFB30:
  .byte $3d
VgFB31:
  .byte $fe
VgFB32:
  .byte $ff
VgFB33:
VgFB34 = *+1
  .word VgFADE
VgFB35:
  .byte $d6
VgFB36:
  .byte $f6
VgFB37:
  .byte $11
VgFB38:
  .byte $e0
VgFB39:
  .byte $60
VgFB3A:
  .byte $50
VgFB3B:
  .byte $30
VgFB3C:
  .byte $10
VgFB3D:
  .byte $e1
VgFB3E:
  .byte $b0
VgFB3F:
  .byte $e0
VgFB40:
  .byte $10
VgFB41:
  .byte $30
VgFB42:
  .byte $50
VgFB43:
  .byte $fe
VgFB44:
  .byte $02
VgFB45:
VgFB46 = *+1
  .word VgFB35
VgFB47:
  .byte $60
VgFB48:
  .byte $40
VgFB49:
  .byte $20
VgFB4A:
  .byte $10
VgFB4B:
  .byte $e1
VgFB4C:
  .byte $b0
VgFB4D:
  .byte $e0
VgFB4E:
  .byte $10
VgFB4F:
  .byte $20
VgFB50:
  .byte $40
VgFB51:
  .byte $fe
VgFB52:
  .byte $02
VgFB53:
VgFB54 = *+1
  .word VgFB47
VgFB55:
  .byte $60
VgFB56:
  .byte $50
VgFB57:
  .byte $30
VgFB58:
  .byte $10
VgFB59:
  .byte $e1
VgFB5A:
  .byte $b0
VgFB5B:
  .byte $e0
VgFB5C:
  .byte $10
VgFB5D:
  .byte $30
VgFB5E:
  .byte $50
VgFB5F:
  .byte $fe
VgFB60:
  .byte $02
VgFB61:
VgFB62 = *+1
  .word VgFB55
VgFB63:
  .byte $60
VgFB64:
  .byte $40
VgFB65:
  .byte $20
VgFB66:
  .byte $10
VgFB67:
  .byte $e1
VgFB68:
  .byte $b0
VgFB69:
  .byte $e0
VgFB6A:
  .byte $10
VgFB6B:
  .byte $20
VgFB6C:
  .byte $40
VgFB6D:
  .byte $60
VgFB6E:
  .byte $80
VgFB6F:
  .byte $90
VgFB70:
  .byte $80
VgFB71:
  .byte $60
VgFB72:
  .byte $40
VgFB73:
  .byte $20
VgFB74:
  .byte $40
VgFB75:
  .byte $d6
VgFB76:
  .byte $f5
VgFB77:
  .byte $11
VgFB78:
  .byte $60
VgFB79:
  .byte $50
VgFB7A:
  .byte $d6
VgFB7B:
  .byte $f4
VgFB7C:
  .byte $11
VgFB7D:
  .byte $30
VgFB7E:
  .byte $10
VgFB7F:
  .byte $d6
VgFB80:
  .byte $f3
VgFB81:
  .byte $00
VgFB82:
  .byte $e1
VgFB83:
  .byte $b0
VgFB84:
  .byte $e0
VgFB85:
  .byte $10
VgFB86:
  .byte $d6
VgFB87:
  .byte $f2
VgFB88:
  .byte $00
VgFB89:
  .byte $30
VgFB8A:
  .byte $50
VgFB8B:
  .byte $ff
VgFB8C:
  .byte $d6
VgFB8D:
  .byte $fd
VgFB8E:
  .byte $66
VgFB8F:
  .byte $e2
VgFB90:
  .byte $13
VgFB91:
  .byte $12
VgFB92:
  .byte $60
VgFB93:
  .byte $b1
VgFB94:
  .byte $a3
VgFB95:
  .byte $61
VgFB96:
  .byte $e1
VgFB97:
  .byte $12
VgFB98:
  .byte $e2
VgFB99:
  .byte $40
VgFB9A:
  .byte $45
VgFB9B:
  .byte $10
VgFB9C:
  .byte $20
VgFB9D:
  .byte $40
VgFB9E:
  .byte $90
VgFB9F:
  .byte $b0
VgFBA0:
  .byte $e1
VgFBA1:
  .byte $10
VgFBA2:
  .byte $e2
VgFBA3:
  .byte $62
VgFBA4:
  .byte $32
VgFBA5:
  .byte $63
VgFBA6:
  .byte $b1
VgFBA7:
  .byte $30
VgFBA8:
  .byte $50
VgFBA9:
  .byte $60
VgFBAA:
  .byte $80
VgFBAB:
  .byte $91
VgFBAC:
  .byte $60
VgFBAD:
  .byte $21
VgFBAE:
  .byte $91
VgFBAF:
  .byte $60
VgFBB0:
  .byte $b1
VgFBB1:
  .byte $80
VgFBB2:
  .byte $41
VgFBB3:
  .byte $80
VgFBB4:
  .byte $b1
VgFBB5:
  .byte $13
VgFBB6:
  .byte $12
VgFBB7:
  .byte $60
VgFBB8:
  .byte $b1
VgFBB9:
  .byte $a3
VgFBBA:
  .byte $61
VgFBBB:
  .byte $e1
VgFBBC:
  .byte $12
VgFBBD:
  .byte $e2
VgFBBE:
  .byte $40
VgFBBF:
  .byte $45
VgFBC0:
  .byte $10
VgFBC1:
  .byte $20
VgFBC2:
  .byte $40
VgFBC3:
  .byte $90
VgFBC4:
  .byte $b0
VgFBC5:
  .byte $e1
VgFBC6:
  .byte $10
VgFBC7:
  .byte $31
VgFBC8:
  .byte $e2
VgFBC9:
  .byte $60
VgFBCA:
  .byte $62
VgFBCB:
  .byte $b1
VgFBCC:
  .byte $e1
VgFBCD:
  .byte $11
VgFBCE:
  .byte $33
VgFBCF:
  .byte $e2
VgFBD0:
  .byte $b1
VgFBD1:
  .byte $82
VgFBD2:
  .byte $e1
VgFBD3:
  .byte $1b
VgFBD4:
  .byte $c0
VgFBD5:
  .byte $d6
VgFBD6:
  .byte $7d
VgFBD7:
  .byte $24
VgFBD8:
  .byte $e2
VgFBD9:
  .byte $92
VgFBDA:
  .byte $62
VgFBDB:
  .byte $95
VgFBDC:
  .byte $60
VgFBDD:
  .byte $80
VgFBDE:
  .byte $91
VgFBDF:
  .byte $82
VgFBE0:
  .byte $42
VgFBE1:
  .byte $19
VgFBE2:
  .byte $d6
VgFBE3:
  .byte $7d
VgFBE4:
  .byte $66
VgFBE5:
  .byte $30
VgFBE6:
  .byte $40
VgFBE7:
  .byte $60
VgFBE8:
  .byte $b2
VgFBE9:
  .byte $61
VgFBEA:
  .byte $50
VgFBEB:
  .byte $60
VgFBEC:
  .byte $80
VgFBED:
  .byte $e1
VgFBEE:
  .byte $12
VgFBEF:
  .byte $e2
VgFBF0:
  .byte $81
VgFBF1:
  .byte $60
VgFBF2:
  .byte $80
VgFBF3:
  .byte $90
VgFBF4:
  .byte $e1
VgFBF5:
  .byte $22
VgFBF6:
  .byte $e2
VgFBF7:
  .byte $91
VgFBF8:
  .byte $80
VgFBF9:
  .byte $90
VgFBFA:
  .byte $b0
VgFBFB:
  .byte $e1
VgFBFC:
  .byte $42
VgFBFD:
  .byte $d6
VgFBFE:
  .byte $7c
VgFBFF:
  .byte $33
VgFC00:
  .byte $69
VgFC01:
  .byte $67
VgFC02:
  .byte $fe
VgFC03:
  .byte $ff
VgFC04:
VgFC05 = *+1
  .word VgFB8C
VgFC06:
  .byte $d6
VgFC07:
  .byte $0f
VgFC08:
  .byte $fd
VgFC09:
VgFC0A = *+1
  .word VgFC6B
VgFC0B:
  .byte $e2
VgFC0C:
  .byte $21
VgFC0D:
  .byte $e1
VgFC0E:
  .byte $20
VgFC0F:
  .byte $20
VgFC10:
  .byte $fe
VgFC11:
  .byte $02
VgFC12:
VgFC13 = *+1
  .word VgFC0B
VgFC14:
  .byte $e2
VgFC15:
  .byte $41
VgFC16:
  .byte $e1
VgFC17:
  .byte $40
VgFC18:
  .byte $40
VgFC19:
  .byte $fe
VgFC1A:
  .byte $02
VgFC1B:
VgFC1C = *+1
  .word VgFC14
VgFC1D:
  .byte $fd
VgFC1E:
VgFC1F = *+1
  .word VgFC6B
VgFC20:
  .byte $e2
VgFC21:
  .byte $11
VgFC22:
  .byte $e1
VgFC23:
  .byte $10
VgFC24:
  .byte $10
VgFC25:
  .byte $fe
VgFC26:
  .byte $04
VgFC27:
VgFC28 = *+1
  .word VgFC20
VgFC29:
  .byte $fd
VgFC2A:
VgFC2B = *+1
  .word VgFC87
VgFC2C:
  .byte $fd
VgFC2D:
VgFC2E = *+1
  .word VgFC87
VgFC2F:
  .byte $e3
VgFC30:
  .byte $90
VgFC31:
  .byte $e2
VgFC32:
  .byte $90
VgFC33:
  .byte $40
VgFC34:
  .byte $90
VgFC35:
  .byte $fe
VgFC36:
  .byte $04
VgFC37:
VgFC38 = *+1
  .word VgFC2F
VgFC39:
  .byte $e3
VgFC3A:
  .byte $b0
VgFC3B:
  .byte $e2
VgFC3C:
  .byte $b0
VgFC3D:
  .byte $60
VgFC3E:
  .byte $b0
VgFC3F:
  .byte $fe
VgFC40:
  .byte $02
VgFC41:
VgFC42 = *+1
  .word VgFC39
VgFC43:
  .byte $e2
VgFC44:
  .byte $10
VgFC45:
  .byte $e1
VgFC46:
  .byte $10
VgFC47:
  .byte $e2
VgFC48:
  .byte $80
VgFC49:
  .byte $e1
VgFC4A:
  .byte $10
VgFC4B:
  .byte $fe
VgFC4C:
  .byte $02
VgFC4D:
VgFC4E = *+1
  .word VgFC43
VgFC4F:
  .byte $fd
VgFC50:
VgFC51 = *+1
  .word VgFC87
VgFC52:
  .byte $e2
VgFC53:
  .byte $40
VgFC54:
  .byte $e1
VgFC55:
  .byte $40
VgFC56:
  .byte $e2
VgFC57:
  .byte $b0
VgFC58:
  .byte $e1
VgFC59:
  .byte $40
VgFC5A:
  .byte $fe
VgFC5B:
  .byte $02
VgFC5C:
VgFC5D = *+1
  .word VgFC52
VgFC5E:
  .byte $e2
VgFC5F:
  .byte $61
VgFC60:
  .byte $e1
VgFC61:
  .byte $60
VgFC62:
  .byte $60
VgFC63:
  .byte $fe
VgFC64:
  .byte $04
VgFC65:
VgFC66 = *+1
  .word VgFC5E
VgFC67:
  .byte $fe
VgFC68:
  .byte $ff
VgFC69:
VgFC6A = *+1
  .word VgFC06
VgFC6B:
  .byte $e3
VgFC6C:
  .byte $61
VgFC6D:
  .byte $e2
VgFC6E:
  .byte $60
VgFC6F:
  .byte $60
VgFC70:
  .byte $fe
VgFC71:
  .byte $04
VgFC72:
VgFC73 = *+1
  .word VgFC6B
VgFC74:
  .byte $e3
VgFC75:
  .byte $91
VgFC76:
  .byte $e2
VgFC77:
  .byte $90
VgFC78:
  .byte $90
VgFC79:
  .byte $fe
VgFC7A:
  .byte $04
VgFC7B:
VgFC7C = *+1
  .word VgFC74
VgFC7D:
  .byte $e3
VgFC7E:
  .byte $b1
VgFC7F:
  .byte $e2
VgFC80:
  .byte $b0
VgFC81:
  .byte $b0
VgFC82:
  .byte $fe
VgFC83:
  .byte $04
VgFC84:
VgFC85 = *+1
  .word VgFC7D
VgFC86:
  .byte $ff
VgFC87:
  .byte $e2
VgFC88:
  .byte $20
VgFC89:
  .byte $e1
VgFC8A:
  .byte $20
VgFC8B:
  .byte $e2
VgFC8C:
  .byte $90
VgFC8D:
  .byte $e1
VgFC8E:
  .byte $20
VgFC8F:
  .byte $fe
VgFC90:
  .byte $02
VgFC91:
VgFC92 = *+1
  .word VgFC87
VgFC93:
  .byte $ff
VgFC94:
  .byte $d5
VgFC95:
  .byte $7a
VgFC96:
  .byte $33
VgFC97:
  .byte $e1
VgFC98:
  .byte $05
VgFC99:
  .byte $e2
VgFC9A:
  .byte $75
VgFC9B:
  .byte $e1
VgFC9C:
  .byte $03
VgFC9D:
  .byte $e2
VgFC9E:
  .byte $a5
VgFC9F:
  .byte $75
VgFCA0:
  .byte $53
VgFCA1:
  .byte $e1
VgFCA2:
  .byte $05
VgFCA3:
  .byte $e2
VgFCA4:
  .byte $75
VgFCA5:
  .byte $40
VgFCA6:
  .byte $70
VgFCA7:
  .byte $e1
VgFCA8:
  .byte $00
VgFCA9:
  .byte $40
VgFCAA:
  .byte $59
VgFCAB:
  .byte $43
VgFCAC:
  .byte $21
VgFCAD:
  .byte $05
VgFCAE:
  .byte $e2
VgFCAF:
  .byte $75
VgFCB0:
  .byte $e1
VgFCB1:
  .byte $03
VgFCB2:
  .byte $e2
VgFCB3:
  .byte $a5
VgFCB4:
  .byte $75
VgFCB5:
  .byte $51
VgFCB6:
  .byte $7e
VgFCB7:
  .byte $30
VgFCB8:
  .byte $50
VgFCB9:
  .byte $7a
VgFCBA:
  .byte $20
VgFCBB:
  .byte $40
VgFCBC:
  .byte $50
VgFCBD:
  .byte $70
VgFCBE:
  .byte $90
VgFCBF:
  .byte $b0
VgFCC0:
  .byte $e1
VgFCC1:
  .byte $05
VgFCC2:
  .byte $e2
VgFCC3:
  .byte $75
VgFCC4:
  .byte $e1
VgFCC5:
  .byte $03
VgFCC6:
  .byte $e2
VgFCC7:
  .byte $a5
VgFCC8:
  .byte $75
VgFCC9:
  .byte $53
VgFCCA:
  .byte $e1
VgFCCB:
  .byte $05
VgFCCC:
  .byte $e2
VgFCCD:
  .byte $75
VgFCCE:
  .byte $00
VgFCCF:
  .byte $40
VgFCD0:
  .byte $70
VgFCD1:
  .byte $e1
VgFCD2:
  .byte $00
VgFCD3:
  .byte $2c
VgFCD4:
  .byte $e2
VgFCD5:
  .byte $a0
VgFCD6:
  .byte $e1
VgFCD7:
  .byte $00
VgFCD8:
  .byte $20
VgFCD9:
  .byte $35
VgFCDA:
  .byte $e2
VgFCDB:
  .byte $a5
VgFCDC:
  .byte $a0
VgFCDD:
  .byte $e1
VgFCDE:
  .byte $00
VgFCDF:
  .byte $20
VgFCE0:
  .byte $40
VgFCE1:
  .byte $55
VgFCE2:
  .byte $15
VgFCE3:
  .byte $10
VgFCE4:
  .byte $30
VgFCE5:
  .byte $51
VgFCE6:
  .byte $7b
VgFCE7:
  .byte $00
VgFCE8:
  .byte $20
VgFCE9:
  .byte $40
VgFCEA:
  .byte $50
VgFCEB:
  .byte $7b
VgFCEC:
  .byte $00
VgFCED:
  .byte $20
VgFCEE:
  .byte $40
VgFCEF:
  .byte $50
VgFCF0:
  .byte $d1
VgFCF1:
  .byte $7a
VgFCF2:
  .byte $33
VgFCF3:
  .byte $ac
VgFCF4:
  .byte $9c
VgFCF5:
  .byte $8c
VgFCF6:
  .byte $7c
VgFCF7:
  .byte $6c
VgFCF8:
  .byte $5c
VgFCF9:
  .byte $d5
VgFCFA:
  .byte $7b
VgFCFB:
  .byte $77
VgFCFC:
  .byte $40
VgFCFD:
  .byte $31
VgFCFE:
  .byte $20
VgFCFF:
  .byte $d5
VgFD00:
  .byte $7a
VgFD01:
  .byte $33
VgFD02:
  .byte $18
VgFD03:
  .byte $fe
VgFD04:
  .byte $ff
VgFD05:
VgFD06 = *+1
  .word VgFC94
VgFD07:
  .byte $d5
VgFD08:
  .byte $13
VgFD09:
  .byte $fd
VgFD0A:
VgFD0B = *+1
  .word VgFD86
VgFD0C:
  .byte $e2
VgFD0D:
  .byte $01
VgFD0E:
  .byte $e3
VgFD0F:
  .byte $b1
VgFD10:
  .byte $91
VgFD11:
  .byte $71
VgFD12:
  .byte $fe
VgFD13:
  .byte $02
VgFD14:
VgFD15 = *+1
  .word VgFD0C
VgFD16:
  .byte $51
VgFD17:
  .byte $41
VgFD18:
  .byte $21
VgFD19:
  .byte $01
VgFD1A:
  .byte $51
VgFD1B:
  .byte $41
VgFD1C:
  .byte $21
VgFD1D:
  .byte $01
VgFD1E:
  .byte $fd
VgFD1F:
VgFD20 = *+1
  .word VgFD86
VgFD21:
  .byte $e3
VgFD22:
  .byte $31
VgFD23:
  .byte $21
VgFD24:
  .byte $01
VgFD25:
  .byte $e4
VgFD26:
  .byte $a1
VgFD27:
  .byte $fe
VgFD28:
  .byte $02
VgFD29:
VgFD2A = *+1
  .word VgFD21
VgFD2B:
  .byte $e3
VgFD2C:
  .byte $21
VgFD2D:
  .byte $01
VgFD2E:
  .byte $e4
VgFD2F:
  .byte $b1
VgFD30:
  .byte $91
VgFD31:
  .byte $e3
VgFD32:
  .byte $71
VgFD33:
  .byte $51
VgFD34:
  .byte $41
VgFD35:
  .byte $21
VgFD36:
  .byte $fd
VgFD37:
VgFD38 = *+1
  .word VgFD86
VgFD39:
  .byte $e2
VgFD3A:
  .byte $01
VgFD3B:
  .byte $e3
VgFD3C:
  .byte $b1
VgFD3D:
  .byte $91
VgFD3E:
  .byte $71
VgFD3F:
  .byte $fe
VgFD40:
  .byte $02
VgFD41:
VgFD42 = *+1
  .word VgFD39
VgFD43:
  .byte $a1
VgFD44:
  .byte $91
VgFD45:
  .byte $71
VgFD46:
  .byte $51
VgFD47:
  .byte $a1
VgFD48:
  .byte $81
VgFD49:
  .byte $71
VgFD4A:
  .byte $51
VgFD4B:
  .byte $e2
VgFD4C:
  .byte $31
VgFD4D:
  .byte $21
VgFD4E:
  .byte $01
VgFD4F:
  .byte $e3
VgFD50:
  .byte $a1
VgFD51:
  .byte $fe
VgFD52:
  .byte $02
VgFD53:
VgFD54 = *+1
  .word VgFD4B
VgFD55:
  .byte $e2
VgFD56:
  .byte $11
VgFD57:
  .byte $01
VgFD58:
  .byte $e3
VgFD59:
  .byte $a1
VgFD5A:
  .byte $81
VgFD5B:
  .byte $fe
VgFD5C:
  .byte $02
VgFD5D:
VgFD5E = *+1
  .word VgFD55
VgFD5F:
  .byte $e3
VgFD60:
  .byte $71
VgFD61:
  .byte $21
VgFD62:
  .byte $71
VgFD63:
  .byte $e2
VgFD64:
  .byte $21
VgFD65:
  .byte $e3
VgFD66:
  .byte $71
VgFD67:
  .byte $e2
VgFD68:
  .byte $21
VgFD69:
  .byte $71
VgFD6A:
  .byte $21
VgFD6B:
  .byte $fe
VgFD6C:
  .byte $02
VgFD6D:
VgFD6E = *+1
  .word VgFD5F
VgFD6F:
  .byte $d1
VgFD70:
  .byte $30
VgFD71:
  .byte $e3
VgFD72:
  .byte $7f
VgFD73:
  .byte $c3
VgFD74:
  .byte $7f
VgFD75:
  .byte $c3
VgFD76:
  .byte $7f
VgFD77:
  .byte $c3
VgFD78:
  .byte $7f
VgFD79:
  .byte $c6
VgFD7A:
  .byte $d5
VgFD7B:
  .byte $0a
VgFD7C:
  .byte $70
VgFD7D:
  .byte $71
VgFD7E:
  .byte $70
VgFD7F:
  .byte $d5
VgFD80:
  .byte $7f
VgFD81:
  .byte $77
VgFD82:
  .byte $fe
VgFD83:
  .byte $ff
VgFD84:
VgFD85 = *+1
  .word VgFD07
VgFD86:
  .byte $e2
VgFD87:
  .byte $01
VgFD88:
  .byte $e3
VgFD89:
  .byte $b1
VgFD8A:
  .byte $91
VgFD8B:
  .byte $71
VgFD8C:
  .byte $fe
VgFD8D:
  .byte $02
VgFD8E:
VgFD8F = *+1
  .word VgFD86
VgFD90:
  .byte $a1
VgFD91:
  .byte $91
VgFD92:
  .byte $71
VgFD93:
  .byte $51
VgFD94:
  .byte $fe
VgFD95:
  .byte $02
VgFD96:
VgFD97 = *+1
  .word VgFD90
VgFD98:
  .byte $ff
VgFD99:
  .byte $d6
VgFD9A:
  .byte $38
VgFD9B:
  .byte $00
VgFD9C:
  .byte $e1
VgFD9D:
  .byte $00
VgFD9E:
  .byte $10
VgFD9F:
  .byte $20
VgFDA0:
  .byte $30
VgFDA1:
  .byte $40
VgFDA2:
  .byte $50
VgFDA3:
  .byte $60
VgFDA4:
  .byte $70
VgFDA5:
  .byte $80
VgFDA6:
  .byte $90
VgFDA7:
  .byte $a0
VgFDA8:
  .byte $b0
VgFDA9:
  .byte $e0
VgFDAA:
  .byte $00
VgFDAB:
  .byte $ff
VgFDAC:
  .byte $d6
VgFDAD:
  .byte $3a
VgFDAE:
  .byte $33
VgFDAF:
  .byte $e3
VgFDB0:
  .byte $00
VgFDB1:
  .byte $10
VgFDB2:
  .byte $20
VgFDB3:
  .byte $30
VgFDB4:
  .byte $40
VgFDB5:
  .byte $50
VgFDB6:
  .byte $60
VgFDB7:
  .byte $70
VgFDB8:
  .byte $80
VgFDB9:
  .byte $90
VgFDBA:
  .byte $a0
VgFDBB:
  .byte $b0
VgFDBC:
  .byte $e2
VgFDBD:
  .byte $00
VgFDBE:
  .byte $d6
VgFDBF:
  .byte $fd
VgFDC0:
  .byte $55
VgFDC1:
  .byte $e2
VgFDC2:
  .byte $30
VgFDC3:
  .byte $e1
VgFDC4:
  .byte $30
VgFDC5:
  .byte $e2
VgFDC6:
  .byte $a0
VgFDC7:
  .byte $e1
VgFDC8:
  .byte $00
VgFDC9:
  .byte $e2
VgFDCA:
  .byte $50
VgFDCB:
  .byte $e1
VgFDCC:
  .byte $30
VgFDCD:
  .byte $e2
VgFDCE:
  .byte $a0
VgFDCF:
  .byte $e1
VgFDD0:
  .byte $00
VgFDD1:
  .byte $e2
VgFDD2:
  .byte $70
VgFDD3:
  .byte $e1
VgFDD4:
  .byte $30
VgFDD5:
  .byte $e2
VgFDD6:
  .byte $a0
VgFDD7:
  .byte $e1
VgFDD8:
  .byte $00
VgFDD9:
  .byte $e2
VgFDDA:
  .byte $50
VgFDDB:
  .byte $e1
VgFDDC:
  .byte $30
VgFDDD:
  .byte $e2
VgFDDE:
  .byte $a0
VgFDDF:
  .byte $e1
VgFDE0:
  .byte $00
VgFDE1:
  .byte $fe
VgFDE2:
  .byte $02
VgFDE3:
VgFDE4 = *+1
  .word VgFDBE
VgFDE5:
  .byte $70
VgFDE6:
  .byte $70
VgFDE7:
  .byte $50
VgFDE8:
  .byte $70
VgFDE9:
  .byte $fe
VgFDEA:
  .byte $04
VgFDEB:
VgFDEC = *+1
  .word VgFDE5
VgFDED:
  .byte $a0
VgFDEE:
  .byte $a0
VgFDEF:
  .byte $80
VgFDF0:
  .byte $a0
VgFDF1:
  .byte $fe
VgFDF2:
  .byte $04
VgFDF3:
VgFDF4 = *+1
  .word VgFDED
VgFDF5:
  .byte $fe
VgFDF6:
  .byte $ff
VgFDF7:
VgFDF8 = *+1
  .word VgFDBE
VgFDF9:
  .byte $d6
VgFDFA:
  .byte $10
VgFDFB:
  .byte $e2
VgFDFC:
  .byte $00
VgFDFD:
  .byte $10
VgFDFE:
  .byte $20
VgFDFF:
  .byte $30
VgFE00:
  .byte $40
VgFE01:
  .byte $50
VgFE02:
  .byte $60
VgFE03:
  .byte $70
VgFE04:
  .byte $80
VgFE05:
  .byte $90
VgFE06:
  .byte $a0
VgFE07:
  .byte $b0
VgFE08:
  .byte $e1
VgFE09:
  .byte $00
VgFE0A:
  .byte $d6
VgFE0B:
  .byte $25
VgFE0C:
  .byte $e2
VgFE0D:
  .byte $31
VgFE0E:
  .byte $d6
VgFE0F:
  .byte $09
VgFE10:
  .byte $30
VgFE11:
  .byte $30
VgFE12:
  .byte $fe
VgFE13:
  .byte $ff
VgFE14:
VgFE15 = *+1
  .word VgFE0A
VgFE16:
  .byte $d7
VgFE17:
  .byte $7f
VgFE18:
  .byte $53
VgFE19:
  .byte $e1
VgFE1A:
  .byte $b0
VgFE1B:
  .byte $e0
VgFE1C:
  .byte $20
VgFE1D:
  .byte $70
VgFE1E:
  .byte $b0
VgFE1F:
  .byte $d7
VgFE20:
  .byte $7f
VgFE21:
  .byte $a3
VgFE22:
  .byte $72
VgFE23:
  .byte $ff
VgFE24:
  .byte $d7
VgFE25:
  .byte $ba
VgFE26:
  .byte $74
VgFE27:
  .byte $e3
VgFE28:
  .byte $20
VgFE29:
  .byte $70
VgFE2A:
  .byte $b0
VgFE2B:
  .byte $e2
VgFE2C:
  .byte $20
VgFE2D:
  .byte $e3
VgFE2E:
  .byte $b2
VgFE2F:
  .byte $ff
VgFE30:
  .byte $d7
VgFE31:
  .byte $15
VgFE32:
  .byte $e1
VgFE33:
  .byte $20
VgFE34:
  .byte $70
VgFE35:
  .byte $b0
VgFE36:
  .byte $e0
VgFE37:
  .byte $20
VgFE38:
  .byte $d7
VgFE39:
  .byte $40
VgFE3A:
  .byte $e1
VgFE3B:
  .byte $b2
VgFE3C:
  .byte $ff
VgFE3D:
  .byte $2f
VgFE3E:
  .byte $30
VgFE3F:
  .byte $00
VgFE40:
  .byte $00
VgFE41:
  .byte $f8
VgFE42:
  .byte $10
VgFE43:
  .byte $09
VgFE44:
  .byte $f8
VgFE45:
  .byte $10
VgFE46:
  .byte $09
VgFE47:
  .byte $f8
VgFE48:
  .byte $20
VgFE49:
  .byte $09
VgFE4A:
  .byte $f8
VgFE4B:
  .byte $20
VgFE4C:
  .byte $09
VgFE4D:
  .byte $22
VgFE4E:
  .byte $30
VgFE4F:
  .byte $30
VgFE50:
  .byte $09
VgFE51:
  .byte $40
VgFE52:
  .byte $09
VgFE53:
  .byte $50
VgFE54:
  .byte $09
VgFE55:
  .byte $70
VgFE56:
  .byte $09
VgFE57:
  .byte $80
VgFE58:
  .byte $09
VgFE59:
  .byte $90
VgFE5A:
  .byte $09
VgFE5B:
  .byte $a0
VgFE5C:
  .byte $09
VgFE5D:
  .byte $b0
VgFE5E:
  .byte $09
VgFE5F:
  .byte $c0
VgFE60:
  .byte $09
VgFE61:
  .byte $d0
VgFE62:
  .byte $09
VgFE63:
  .byte $e0
VgFE64:
  .byte $09
VgFE65:
  .byte $23
VgFE66:
  .byte $30
VgFE67:
  .byte $f0
VgFE68:
  .byte $0a
VgFE69:
  .byte $e0
VgFE6A:
  .byte $0b
VgFE6B:
  .byte $d0
VgFE6C:
  .byte $0c
VgFE6D:
  .byte $c0
VgFE6E:
  .byte $0d
VgFE6F:
  .byte $b0
VgFE70:
  .byte $0e
VgFE71:
  .byte $a0
VgFE72:
  .byte $0e
VgFE73:
  .byte $90
VgFE74:
  .byte $0e
VgFE75:
  .byte $80
VgFE76:
  .byte $0e
VgFE77:
  .byte $70
VgFE78:
  .byte $0e
VgFE79:
  .byte $60
VgFE7A:
  .byte $0e
VgFE7B:
  .byte $50
VgFE7C:
  .byte $0e
VgFE7D:
  .byte $40
VgFE7E:
  .byte $0e
VgFE7F:
  .byte $28
VgFE80:
  .byte $30
VgFE81:
  .byte $30
VgFE82:
  .byte $0e
VgFE83:
  .byte $f8
VgFE84:
  .byte $20
VgFE85:
  .byte $0f
VgFE86:
  .byte $ff
VgFE87:
  .byte $21
VgFE88:
  .byte $bf
VgFE89:
  .byte $73
VgFE8A:
  .byte $ff
VgFE8B:
  .byte $73
VgFE8C:
  .byte $00
VgFE8D:
  .byte $fe
VgFE8E:
  .byte $0a
VgFE8F:
VgFE90 = *+1
  .word VgFE87
VgFE91:
  .byte $63
VgFE92:
  .byte $ff
VgFE93:
  .byte $63
VgFE94:
  .byte $00
VgFE95:
  .byte $53
VgFE96:
  .byte $ff
VgFE97:
  .byte $53
VgFE98:
  .byte $00
VgFE99:
  .byte $43
VgFE9A:
  .byte $ff
VgFE9B:
  .byte $43
VgFE9C:
  .byte $00
VgFE9D:
  .byte $33
VgFE9E:
  .byte $ff
VgFE9F:
  .byte $33
VgFEA0:
  .byte $00
VgFEA1:
  .byte $fe
VgFEA2:
  .byte $19
VgFEA3:
VgFEA4 = *+1
  .word VgFE9D
VgFEA5:
  .byte $43
VgFEA6:
  .byte $ff
VgFEA7:
  .byte $43
VgFEA8:
  .byte $00
VgFEA9:
  .byte $53
VgFEAA:
  .byte $ff
VgFEAB:
  .byte $53
VgFEAC:
  .byte $00
VgFEAD:
  .byte $fe
VgFEAE:
  .byte $ff
VgFEAF:
VgFEB0 = *+1
  .word VgFE87
VgFEB1:
  .byte $2f
VgFEB2:
  .byte $b0
VgFEB3:
  .byte $00
VgFEB4:
  .byte $00
VgFEB5:
  .byte $00
VgFEB6:
  .byte $00
VgFEB7:
  .byte $26
VgFEB8:
  .byte $30
VgFEB9:
  .byte $10
VgFEBA:
  .byte $94
VgFEBB:
  .byte $f0
VgFEBC:
  .byte $10
VgFEBD:
  .byte $e0
VgFEBE:
  .byte $10
VgFEBF:
  .byte $d0
VgFEC0:
  .byte $10
VgFEC1:
  .byte $c0
VgFEC2:
  .byte $10
VgFEC3:
  .byte $b0
VgFEC4:
  .byte $10
VgFEC5:
  .byte $a0
VgFEC6:
  .byte $10
VgFEC7:
  .byte $90
VgFEC8:
  .byte $10
VgFEC9:
  .byte $80
VgFECA:
  .byte $10
VgFECB:
  .byte $70
VgFECC:
  .byte $10
VgFECD:
  .byte $60
VgFECE:
  .byte $10
VgFECF:
  .byte $50
VgFED0:
  .byte $10
VgFED1:
  .byte $40
VgFED2:
  .byte $10
VgFED3:
  .byte $30
VgFED4:
  .byte $10
VgFED5:
  .byte $fe
VgFED6:
  .byte $ff
VgFED7:
VgFED8 = *+1
  .word VgFEB9
VgFED9:
  .byte $25
VgFEDA:
  .byte $03
VgFEDB:
  .byte $00
VgFEDC:
  .byte $56
VgFEDD:
  .byte $00
VgFEDE:
  .byte $55
VgFEDF:
  .byte $00
VgFEE0:
  .byte $54
VgFEE1:
  .byte $00
VgFEE2:
  .byte $53
VgFEE3:
  .byte $00
VgFEE4:
  .byte $52
VgFEE5:
  .byte $00
VgFEE6:
  .byte $51
VgFEE7:
  .byte $00
VgFEE8:
  .byte $50
VgFEE9:
  .byte $00
VgFEEA:
  .byte $4f
VgFEEB:
  .byte $00
VgFEEC:
  .byte $4e
VgFEED:
  .byte $00
VgFEEE:
  .byte $4d
VgFEEF:
  .byte $00
VgFEF0:
  .byte $4c
VgFEF1:
  .byte $00
VgFEF2:
  .byte $4b
VgFEF3:
  .byte $00
VgFEF4:
  .byte $4a
VgFEF5:
  .byte $00
VgFEF6:
  .byte $49
VgFEF7:
  .byte $00
VgFEF8:
  .byte $48
VgFEF9:
  .byte $00
VgFEFA:
  .byte $47
VgFEFB:
  .byte $00
VgFEFC:
  .byte $46
VgFEFD:
  .byte $00
VgFEFE:
  .byte $45
VgFEFF:
  .byte $00
VgFF00:
  .byte $44
VgFF01:
  .byte $00
VgFF02:
  .byte $43
VgFF03:
  .byte $00
VgFF04:
  .byte $42
VgFF05:
  .byte $00
VgFF06:
  .byte $41
VgFF07:
  .byte $00
VgFF08:
  .byte $40
VgFF09:
  .byte $00
VgFF0A:
  .byte $3f
VgFF0B:
  .byte $00
VgFF0C:
  .byte $3e
VgFF0D:
  .byte $00
VgFF0E:
  .byte $3d
VgFF0F:
  .byte $00
VgFF10:
  .byte $3c
VgFF11:
  .byte $00
VgFF12:
  .byte $3b
VgFF13:
  .byte $00
VgFF14:
  .byte $3a
VgFF15:
  .byte $00
VgFF16:
  .byte $39
VgFF17:
  .byte $00
VgFF18:
  .byte $38
VgFF19:
  .byte $00
VgFF1A:
  .byte $37
VgFF1B:
  .byte $00
VgFF1C:
  .byte $36
VgFF1D:
  .byte $00
VgFF1E:
  .byte $35
VgFF1F:
  .byte $00
VgFF20:
  .byte $34
VgFF21:
  .byte $00
VgFF22:
  .byte $33
VgFF23:
  .byte $00
VgFF24:
  .byte $32
VgFF25:
  .byte $00
VgFF26:
  .byte $31
VgFF27:
  .byte $00
VgFF28:
  .byte $30
VgFF29:
  .byte $00
VgFF2A:
  .byte $2f
VgFF2B:
  .byte $00
VgFF2C:
  .byte $2e
VgFF2D:
  .byte $00
VgFF2E:
  .byte $2d
VgFF2F:
  .byte $00
VgFF30:
  .byte $2c
VgFF31:
  .byte $00
VgFF32:
  .byte $2b
VgFF33:
  .byte $00
VgFF34:
  .byte $2a
VgFF35:
  .byte $00
VgFF36:
  .byte $29
VgFF37:
  .byte $00
VgFF38:
  .byte $28
VgFF39:
  .byte $00
VgFF3A:
  .byte $27
VgFF3B:
  .byte $00
VgFF3C:
  .byte $26
VgFF3D:
  .byte $00
VgFF3E:
  .byte $25
VgFF3F:
  .byte $00
VgFF40:
  .byte $24
VgFF41:
  .byte $00
VgFF42:
  .byte $23
VgFF43:
  .byte $00
VgFF44:
  .byte $22
VgFF45:
  .byte $00
VgFF46:
  .byte $21
VgFF47:
  .byte $00
VgFF48:
  .byte $20
VgFF49:
  .byte $00
VgFF4A:
  .byte $1f
VgFF4B:
  .byte $00
VgFF4C:
  .byte $1e
VgFF4D:
  .byte $00
VgFF4E:
  .byte $1d
VgFF4F:
  .byte $00
VgFF50:
  .byte $1c
VgFF51:
  .byte $00
VgFF52:
  .byte $1b
VgFF53:
  .byte $00
VgFF54:
  .byte $1a
VgFF55:
  .byte $00
VgFF56:
  .byte $19
VgFF57:
  .byte $00
VgFF58:
  .byte $18
VgFF59:
  .byte $00
VgFF5A:
  .byte $17
VgFF5B:
  .byte $00
VgFF5C:
  .byte $16
VgFF5D:
  .byte $ff
VgFF5E:
  .byte $21
VgFF5F:
  .byte $30
VgFF60:
  .byte $30
VgFF61:
  .byte $04
VgFF62:
  .byte $a0
VgFF63:
  .byte $08
VgFF64:
  .byte $30
VgFF65:
  .byte $08
VgFF66:
  .byte $30
VgFF67:
  .byte $04
VgFF68:
  .byte $ff
VgFF69:
  .byte $dc
VgFF6A:
  .byte $34
VgFF6B:
  .byte $24
VgFF6C:
  .byte $e1
VgFF6D:
  .byte $c3
VgFF6E:
  .byte $90
VgFF6F:
  .byte $90
VgFF70:
  .byte $dc
VgFF71:
  .byte $37
VgFF72:
  .byte $24
VgFF73:
  .byte $e0
VgFF74:
  .byte $90
VgFF75:
  .byte $dc
VgFF76:
  .byte $34
VgFF77:
  .byte $24
VgFF78:
  .byte $e1
VgFF79:
  .byte $90
VgFF7A:
  .byte $fe
VgFF7B:
  .byte $08
VgFF7C:
VgFF7D = *+1
  .word VgFF6E
VgFF7E:
  .byte $dc
VgFF7F:
  .byte $33
VgFF80:
  .byte $24
VgFF81:
  .byte $90
VgFF82:
  .byte $90
VgFF83:
  .byte $dc
VgFF84:
  .byte $36
VgFF85:
  .byte $24
VgFF86:
  .byte $e0
VgFF87:
  .byte $90
VgFF88:
  .byte $dc
VgFF89:
  .byte $33
VgFF8A:
  .byte $24
VgFF8B:
  .byte $e1
VgFF8C:
  .byte $90
VgFF8D:
  .byte $dc
VgFF8E:
  .byte $33
VgFF8F:
  .byte $24
VgFF90:
  .byte $90
VgFF91:
  .byte $90
VgFF92:
  .byte $dc
VgFF93:
  .byte $35
VgFF94:
  .byte $24
VgFF95:
  .byte $e0
VgFF96:
  .byte $90
VgFF97:
  .byte $dc
VgFF98:
  .byte $33
VgFF99:
  .byte $24
VgFF9A:
  .byte $e1
VgFF9B:
  .byte $90
VgFF9C:
  .byte $90
VgFF9D:
  .byte $90
VgFF9E:
  .byte $ff
VgFF9F:
  .byte $dc
VgFFA0:
  .byte $bc
VgFFA1:
  .byte $4a
VgFFA2:
  .byte $e2
VgFFA3:
  .byte $c3
VgFFA4:
  .byte $91
VgFFA5:
  .byte $e1
VgFFA6:
  .byte $40
VgFFA7:
  .byte $21
VgFFA8:
  .byte $00
VgFFA9:
  .byte $e2
VgFFAA:
  .byte $b0
VgFFAB:
  .byte $e1
VgFFAC:
  .byte $01
VgFFAD:
  .byte $e2
VgFFAE:
  .byte $b0
VgFFAF:
  .byte $90
VgFFB0:
  .byte $b1
VgFFB1:
  .byte $90
VgFFB2:
  .byte $71
VgFFB3:
  .byte $90
VgFFB4:
  .byte $90
VgFFB5:
  .byte $e1
VgFFB6:
  .byte $40
VgFFB7:
  .byte $21
VgFFB8:
  .byte $7a
VgFFB9:
  .byte $dc
VgFFBA:
  .byte $b8
VgFFBB:
  .byte $4a
VgFFBC:
  .byte $e2
VgFFBD:
  .byte $91
VgFFBE:
  .byte $e1
VgFFBF:
  .byte $40
VgFFC0:
  .byte $dc
VgFFC1:
  .byte $b5
VgFFC2:
  .byte $4a
VgFFC3:
  .byte $21
VgFFC4:
  .byte $00
VgFFC5:
  .byte $dc
VgFFC6:
  .byte $b3
VgFFC7:
  .byte $4a
VgFFC8:
  .byte $e2
VgFFC9:
  .byte $b0
VgFFCA:
  .byte $e1
VgFFCB:
  .byte $01
VgFFCC:
  .byte $e2
VgFFCD:
  .byte $b0
VgFFCE:
  .byte $ff
VgFFCF:
  .byte $dc
VgFFD0:
  .byte $4a
VgFFD1:
  .byte $e2
VgFFD2:
  .byte $c3
VgFFD3:
  .byte $91
VgFFD4:
  .byte $90
VgFFD5:
  .byte $41
VgFFD6:
  .byte $40
VgFFD7:
  .byte $41
VgFFD8:
  .byte $50
VgFFD9:
  .byte $40
VgFFDA:
  .byte $20
VgFFDB:
  .byte $71
VgFFDC:
  .byte $40
VgFFDD:
  .byte $71
VgFFDE:
  .byte $91
VgFFDF:
  .byte $90
VgFFE0:
  .byte $40
VgFFE1:
  .byte $40
VgFFE2:
  .byte $40
VgFFE3:
  .byte $51
VgFFE4:
  .byte $50
VgFFE5:
  .byte $40
VgFFE6:
  .byte $20
VgFFE7:
  .byte $71
VgFFE8:
  .byte $70
VgFFE9:
  .byte $81
VgFFEA:
  .byte $91
VgFFEB:
  .byte $90
VgFFEC:
  .byte $41
VgFFED:
  .byte $41
VgFFEE:
  .byte $ff
VgFFEF:
  .byte $ff
VgFFF0:
  .byte $ff
VgFFF1:
  .byte $ff
VgFFF2:
  .byte $ff
VgFFF3:
  .byte $ff
VgFFF4:
  .byte $ff
VgFFF5:
  .byte $ff
VgFFF6:
  .byte $ff
VgFFF7:
  .byte $ff
VgFFF8:
  .byte $ff
VgFFF9:
  .byte $ff
VgFFFA:
  .byte $6a
VgFFFB:
  .byte $80
VgFFFC:
  .byte $10
VgFFFD:
  .byte $80
VgFFFE:
  .byte $bd
VgFFFF:
  .byte $80
.endscope
GradiusNativeInit = GradiusMusic::VgEC48
GradiusNativePlay = GradiusMusic::VgED30
.popseg
