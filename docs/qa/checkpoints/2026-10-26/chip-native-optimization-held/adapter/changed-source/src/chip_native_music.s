; Full original NSF data; separately relocated genuine player.
.pushseg
ChNativeRam=XgLzHistory
ChNativeZp=XgLzHistory+$80
ChNativeTempX=XgLzHistory+$a0
ChNativeTempY=XgLzHistory+$a1
ChNativeTempA=XgLzHistory+$a2
ChNativeDispatchBase=XgLzHistory+$a3
ChNativePointer=XgLzCopy
ChNativeMappedC5=XgLzPosition
ChNativeMappedC1=XgLzDistance
.segment "CHIP_NATIVE_CODE"
ChNativeStart:
.assert ChNativeStart=$d469,lderror,"Chip code follows relocated genuine Mac records"
::ChNativeP8000:
  JMP ::ChNativeP803A
::ChNativeP8003:
  JMP ::ChNativeP80C9
::ChNativeP8006:
  LDA #$00
::ChNativeP8008:
  STA ::ChNativeZp+$02
::ChNativeP800A:
  LDY #$08
::ChNativeP800C:
  ASL ::ChNativeZp+$02
::ChNativeP800E:
  ROL ::ChNativeZp+$01
::ChNativeP8010:
  BCC ::ChNativeP801F
::ChNativeP8012:
  CLC
::ChNativeP8013:
  LDA ::ChNativeZp+$02
::ChNativeP8015:
  ADC ::ChNativeZp+$04
::ChNativeP8017:
  STA ::ChNativeZp+$02
::ChNativeP8019:
  LDA ::ChNativeZp+$01
::ChNativeP801B:
  ADC #$00
::ChNativeP801D:
  STA ::ChNativeZp+$01
::ChNativeP801F:
  DEY
::ChNativeP8020:
  BNE ::ChNativeP800C
::ChNativeP8022:
  RTS
::ChNativeP802C:
  LDA (ChNativeMappedC1),y
::ChNativeP802E:
  PHA
::ChNativeP802F:
  INY
::ChNativeP8030:
  LDA (ChNativeMappedC1),y
::ChNativeP8032:
  STA ::ChNativeZp+$02
::ChNativeP8034:
  PLA
::ChNativeP8035:
  STA ::ChNativeZp+$01
::ChNativeP8037:
  jmp ChNativeJump
::ChNativeP803A:
  LDA ::ChNativeZp+$00
::ChNativeP803C:
  LSR A
::ChNativeP803D:
  BCS ::ChNativeP80A2
::ChNativeP803F:
  LDA ::ChNativeZp+$10
::ChNativeP8041:
  ORA ::ChNativeZp+$11
::ChNativeP8043:
  BEQ ::ChNativeP8048
::ChNativeP8045:
  JSR ::ChNativeP820C
::ChNativeP8048:
  CLC
::ChNativeP8049:
  LDA ::ChNativeZp+$0a
::ChNativeP804B:
  ADC ::ChNativeZp+$08
::ChNativeP804D:
  STA ::ChNativeZp+$08
::ChNativeP804F:
  LDA ::ChNativeZp+$09
::ChNativeP8051:
  ADC #$00
::ChNativeP8053:
  STA ::ChNativeZp+$07
::ChNativeP8055:
  LDA ::ChNativeZp+$0f
::ChNativeP8057:
  PHA
::ChNativeP8058:
  LDX #$03
::ChNativeP805A:
  LDA ::ChNativeZp+$0f
::ChNativeP805C:
  LSR A
::ChNativeP805D:
  BCC ::ChNativeP8062
::ChNativeP805F:
  JSR ::ChNativeP8295
::ChNativeP8062:
  LDA ::ChNativeZp+$00
::ChNativeP8064:
  AND #$02
::ChNativeP8066:
  BNE ::ChNativeP806F
::ChNativeP8068:
  TXA
::ChNativeP8069:
  PHA
::ChNativeP806A:
  JSR ::ChNativeP8348
::ChNativeP806D:
  PLA
::ChNativeP806E:
  TAX
::ChNativeP806F:
  LSR ::ChNativeZp+$0f
::ChNativeP8071:
  DEX
::ChNativeP8072:
  BPL ::ChNativeP805A
::ChNativeP8074:
  PLA
::ChNativeP8075:
  STA ::ChNativeZp+$0f
::ChNativeP8077:
  LSR ::ChNativeZp+$00
::ChNativeP8079:
  ASL ::ChNativeZp+$00
::ChNativeP807B:
  LDA ::ChNativeZp+$0c
::ChNativeP807D:
  AND #$7f
::ChNativeP807F:
  BEQ ::ChNativeP80A2
::ChNativeP8081:
  LDY #$00
::ChNativeP8083:
  STY ::ChNativeZp+$01
::ChNativeP8085:
  LDY #$04
::ChNativeP8087:
  ASL A
::ChNativeP8088:
  ROL ::ChNativeZp+$01
::ChNativeP808A:
  DEY
::ChNativeP808B:
  BNE ::ChNativeP8087
::ChNativeP808D:
  CLC
::ChNativeP808E:
  ADC ::ChNativeZp+$00
::ChNativeP8090:
  STA ::ChNativeZp+$00
::ChNativeP8092:
  LDA ::ChNativeZp+$01
::ChNativeP8094:
  ADC ::ChNativeZp+$0d
::ChNativeP8096:
  BCC ::ChNativeP80A0
::ChNativeP8098:
  LDA ::ChNativeZp+$0c
::ChNativeP809A:
  AND #$80
::ChNativeP809C:
  STA ::ChNativeZp+$0c
::ChNativeP809E:
  LDA #$ff
::ChNativeP80A0:
  STA ::ChNativeZp+$0d
::ChNativeP80A2:
  RTS
::ChNativeP80A3:
  TXA
::ChNativeP80A4:
  AND #$03
::ChNativeP80A6:
  EOR #$03
::ChNativeP80A8:
  ASL A
::ChNativeP80A9:
  ASL A
::ChNativeP80AA:
  TAY
::ChNativeP80AB:
  LDA #$30
::ChNativeP80AD:
  CPY #$08
::ChNativeP80AF:
  BNE ::ChNativeP80B3
::ChNativeP80B1:
  LDA #$00
::ChNativeP80B3:
  jsr GuestNativeStoreSTA00Y
::ChNativeP80B6:
  RTS
::ChNativeP80B7:
  PHA
::ChNativeP80B8:
  TXA
::ChNativeP80B9:
  AND #$03
::ChNativeP80BB:
  EOR #$03
::ChNativeP80BD:
  ASL A
::ChNativeP80BE:
  ASL A
::ChNativeP80BF:
  STY ::ChNativeZp+$04
::ChNativeP80C1:
  ORA ::ChNativeZp+$04
::ChNativeP80C3:
  TAY
::ChNativeP80C4:
  PLA
::ChNativeP80C5:
  jsr GuestNativeStoreSTA00Y
::ChNativeP80C8:
  RTS
::ChNativeP80C9:
  INC ::ChNativeZp+$00
::ChNativeP80CB:
  JSR ::ChNativeP80D1
::ChNativeP80CE:
  DEC ::ChNativeZp+$00
::ChNativeP80D0:
  RTS
::ChNativeP80D1:
  CMP #$f0
::ChNativeP80D3:
  BCC ::ChNativeP80D8
::ChNativeP80D5:
  JMP ::ChNativeP8165
::ChNativeP80D8:
  CMP $ac00
::ChNativeP80DB:
  BCC ::ChNativeP80E3
::ChNativeP80DD:
  SEC
::ChNativeP80DE:
  SBC $ac00
::ChNativeP80E1:
  BCS ::ChNativeP80D8
::ChNativeP80E3:
  ASL A
::ChNativeP80E4:
  TAX
::ChNativeP80E5:
  LDA $ac04,x
::ChNativeP80E8:
  STA ::ChNativeZp+$01
  STA ChNativeMappedC1
::ChNativeP80EA:
  LDA $ac03,x
::ChNativeP80ED:
  STA ::ChNativeZp+$02
  jsr ChNativeMapC1High
::ChNativeP80EF:
  ORA ::ChNativeZp+$01
::ChNativeP80F1:
  BEQ ::ChNativeP8139
::ChNativeP80F3:
  LDY #$00
::ChNativeP80F5:
  LDA (ChNativeMappedC1),y
::ChNativeP80F7:
  BEQ ::ChNativeP813A
::ChNativeP80F9:
  INX
::ChNativeP80FA:
  STA ::ChNativeZp+$04
::ChNativeP80FC:
  AND #$7f
::ChNativeP80FE:
  CMP ::ChNativeZp+$0e
::ChNativeP8100:
  BCC ::ChNativeP8139
::ChNativeP8102:
  STA ::ChNativeZp+$0e
::ChNativeP8104:
  BNE ::ChNativeP8110
::ChNativeP8106:
  LDA ::ChNativeZp+$16
::ChNativeP8108:
  BPL ::ChNativeP8110
::ChNativeP810A:
  LDA ::ChNativeZp+$04
::ChNativeP810C:
  BMI ::ChNativeP8110
::ChNativeP810E:
  STY ::ChNativeZp+$17
::ChNativeP8110:
  STY ::ChNativeZp+$16
::ChNativeP8112:
  ASL ::ChNativeZp+$04
::ChNativeP8114:
  ROR ::ChNativeZp+$16
::ChNativeP8116:
  BPL ::ChNativeP811A
::ChNativeP8118:
  STX ::ChNativeZp+$17
::ChNativeP811A:
  INC ::ChNativeZp+$01
::ChNativeP811C:
  LDA ::ChNativeZp+$01
::ChNativeP811E:
  STA ::ChNativeZp+$10
::ChNativeP8120:
  BNE ::ChNativeP8124
::ChNativeP8122:
  INC ::ChNativeZp+$02
::ChNativeP8124:
  LDA ::ChNativeZp+$02
::ChNativeP8126:
  STA ::ChNativeZp+$11
::ChNativeP8128:
  TYA
::ChNativeP8129:
  STA ::ChNativeZp+$12
::ChNativeP812B:
  STA ::ChNativeZp+$13
::ChNativeP812D:
  STA ::ChNativeZp+$14
::ChNativeP812F:
  STA ::ChNativeZp+$15
::ChNativeP8131:
  LDY #$27
::ChNativeP8133:
  STA ::ChNativeRam+$00,y
::ChNativeP8136:
  DEY
::ChNativeP8137:
  BPL ::ChNativeP8133
::ChNativeP8139:
  RTS
::ChNativeP813A:
  LDX #$01
::ChNativeP813C:
  STX ::ChNativeZp+$09
::ChNativeP813E:
  LDX #$99
::ChNativeP8140:
  STX ::ChNativeZp+$0a
::ChNativeP8142:
  STA ::ChNativeZp+$08
::ChNativeP8144:
  STA ::ChNativeZp+$0b
::ChNativeP8146:
  STA ::ChNativeZp+$0c
::ChNativeP8148:
  STA ::ChNativeZp+$0d
::ChNativeP814A:
  LDX #$53
::ChNativeP814C:
  STA ::ChNativeRam+$28,x
::ChNativeP814F:
  DEX
::ChNativeP8150:
  BPL ::ChNativeP814C
::ChNativeP8152:
  LDX #$03
::ChNativeP8154:
  INY
::ChNativeP8155:
  LDA (ChNativeMappedC1),y
::ChNativeP8157:
  STA ::ChNativeRam+$54,x
::ChNativeP815A:
  INY
::ChNativeP815B:
  LDA (ChNativeMappedC1),y
::ChNativeP815D:
  STA ::ChNativeRam+$50,x
::ChNativeP8160:
  DEX
::ChNativeP8161:
  BPL ::ChNativeP8154
::ChNativeP8163:
  BMI ::ChNativeP81A8
::ChNativeP8165:
  STY ::ChNativeZp+$03
::ChNativeP8167:
  AND #$07
::ChNativeP8169:
  jsr ChNativeDispatch8169
::ChNativeP817C:
  JSR ::ChNativeP819B
::ChNativeP817F:
  LDA #$00
::ChNativeP8181:
  STA ::ChNativeZp+$0e
::ChNativeP8183:
  STA ::ChNativeZp+$10
::ChNativeP8185:
  STA ::ChNativeZp+$11
::ChNativeP8187:
  STA ::ChNativeZp+$17
::ChNativeP8189:
  STA ::ChNativeZp+$18
::ChNativeP818B:
  LDA ::ChNativeZp+$0f
::ChNativeP818D:
  BEQ ::ChNativeP819A
::ChNativeP818F:
  EOR #$0f
::ChNativeP8191:
  STA ::ChNativeZp+$0f
::ChNativeP8193:
  JSR ::ChNativeP81A8
::ChNativeP8196:
  LDA #$00
::ChNativeP8198:
  STA ::ChNativeZp+$0f
::ChNativeP819A:
  RTS
::ChNativeP819B:
  LDA #$00
::ChNativeP819D:
  LDX #$03
::ChNativeP819F:
  STA ::ChNativeRam+$54,x
::ChNativeP81A2:
  STA ::ChNativeRam+$50,x
::ChNativeP81A5:
  DEX
::ChNativeP81A6:
  BPL ::ChNativeP819F
::ChNativeP81A8:
  LDA ::ChNativeZp+$0f
::ChNativeP81AA:
  PHA
::ChNativeP81AB:
  LDX #$03
::ChNativeP81AD:
  LDA ::ChNativeZp+$0f
::ChNativeP81AF:
  LSR A
::ChNativeP81B0:
  BCS ::ChNativeP81C2
::ChNativeP81B2:
  JSR ::ChNativeP80A3
::ChNativeP81B5:
  LDA ::ChNativeRam+$54,x
::ChNativeP81B8:
  ORA ::ChNativeRam+$50,x
::ChNativeP81BB:
  BEQ ::ChNativeP81C2
::ChNativeP81BD:
  LDA #$ff
::ChNativeP81BF:
  STA ::ChNativeRam+$7c,x
::ChNativeP81C2:
  LSR ::ChNativeZp+$0f
::ChNativeP81C4:
  DEX
::ChNativeP81C5:
  BPL ::ChNativeP81AD
::ChNativeP81C7:
  PLA
::ChNativeP81C8:
  STA ::ChNativeZp+$0f
::ChNativeP81CA:
  LDA #$08
::ChNativeP81CC:
  jsr GuestNativeStoreSTA01
::ChNativeP81CF:
  jsr GuestNativeStoreSTA05
::ChNativeP81D2:
  LDA #$0f
::ChNativeP81D4:
  jsr GuestNativeStatusSTA
::ChNativeP81D7:
  RTS
::ChNativeP81D8:
  LDA ::ChNativeZp+$00
::ChNativeP81DA:
  ORA #$02
::ChNativeP81DC:
  STA ::ChNativeZp+$00
::ChNativeP81DE:
  BNE ::ChNativeP81A8
::ChNativeP81E0:
  LDA ::ChNativeZp+$00
::ChNativeP81E2:
  AND #$fd
::ChNativeP81E4:
  STA ::ChNativeZp+$00
::ChNativeP81E6:
  RTS
::ChNativeP81E7:
  ASL ::ChNativeZp+$03
::ChNativeP81E9:
  BEQ ::ChNativeP81EE
::ChNativeP81EB:
  SEC
::ChNativeP81EC:
  ROR ::ChNativeZp+$03
::ChNativeP81EE:
  LDA ::ChNativeZp+$00
::ChNativeP81F0:
  AND #$0f
::ChNativeP81F2:
  STA ::ChNativeZp+$00
::ChNativeP81F4:
  LDY ::ChNativeZp+$03
::ChNativeP81F6:
  STY ::ChNativeZp+$0c
::ChNativeP81F8:
  BEQ ::ChNativeP8201
::ChNativeP81FA:
  LDY #$ff
::ChNativeP81FC:
  CPY ::ChNativeZp+$0d
::ChNativeP81FE:
  BNE ::ChNativeP8203
::ChNativeP8200:
  INY
::ChNativeP8201:
  STY ::ChNativeZp+$0d
::ChNativeP8203:
  RTS
::ChNativeP8204:
  LDA #$00
::ChNativeP8206:
  SEC
::ChNativeP8207:
  SBC ::ChNativeZp+$03
::ChNativeP8209:
  STA ::ChNativeZp+$18
::ChNativeP820B:
  RTS
::ChNativeP820C:
  LDA ::ChNativeZp+$13
::ChNativeP820E:
  BEQ ::ChNativeP8215
::ChNativeP8210:
  DEC ::ChNativeZp+$13
::ChNativeP8212:
  DEC ::ChNativeZp+$15
::ChNativeP8214:
  RTS
::ChNativeP8215:
  JSR ::ChNativeP833D
::ChNativeP8218:
  STA ::ChNativeZp+$04
::ChNativeP821A:
  ASL A
::ChNativeP821B:
  BCC ::ChNativeP822A
::ChNativeP821D:
  STY ::ChNativeZp+$0e
::ChNativeP821F:
  LDA ::ChNativeZp+$17
::ChNativeP8221:
  LSR A
::ChNativeP8222:
  BCC ::ChNativeP8227
::ChNativeP8224:
  JMP ::ChNativeP80E3
::ChNativeP8227:
  JMP ::ChNativeP817F
::ChNativeP822A:
  LSR ::ChNativeZp+$04
::ChNativeP822C:
  BCC ::ChNativeP825D
::ChNativeP822E:
  JSR ::ChNativeP833D
::ChNativeP8231:
  ASL A
::ChNativeP8232:
  BEQ ::ChNativeP8240
::ChNativeP8234:
  ASL ::ChNativeZp+$16
::ChNativeP8236:
  PHP
::ChNativeP8237:
  CMP ::ChNativeZp+$16
::ChNativeP8239:
  BEQ ::ChNativeP824D
::ChNativeP823B:
  PLP
::ChNativeP823C:
  ROR ::ChNativeZp+$16
::ChNativeP823E:
  INC ::ChNativeZp+$16
::ChNativeP8240:
  JSR ::ChNativeP833D
::ChNativeP8243:
  TAX
::ChNativeP8244:
  JSR ::ChNativeP833D
::ChNativeP8247:
  STA ::ChNativeZp+$10
::ChNativeP8249:
  STX ::ChNativeZp+$11
::ChNativeP824B:
  BNE ::ChNativeP8215
::ChNativeP824D:
  TYA
::ChNativeP824E:
  PLP
::ChNativeP824F:
  ROR A
::ChNativeP8250:
  STA ::ChNativeZp+$16
::ChNativeP8252:
  CLC
::ChNativeP8253:
  LDA #$02
::ChNativeP8255:
  ADC ::ChNativeZp+$10
::ChNativeP8257:
  STA ::ChNativeZp+$10
::ChNativeP8259:
  BCC ::ChNativeP825D
::ChNativeP825B:
  INC ::ChNativeZp+$11
::ChNativeP825D:
  LSR ::ChNativeZp+$04
::ChNativeP825F:
  BCC ::ChNativeP8266
::ChNativeP8261:
  JSR ::ChNativeP833D
::ChNativeP8264:
  STA ::ChNativeZp+$14
::ChNativeP8266:
  LSR ::ChNativeZp+$04
::ChNativeP8268:
  BCC ::ChNativeP826F
::ChNativeP826A:
  JSR ::ChNativeP833D
::ChNativeP826D:
  STA ::ChNativeZp+$12
::ChNativeP826F:
  JSR ::ChNativeP833D
::ChNativeP8272:
  STA ::ChNativeZp+$13
::ChNativeP8274:
  STA ::ChNativeZp+$01
::ChNativeP8276:
  LDA ::ChNativeZp+$14
::ChNativeP8278:
  STA ::ChNativeZp+$04
::ChNativeP827A:
  JSR ::ChNativeP8006
::ChNativeP827D:
  LDY ::ChNativeZp+$01
::ChNativeP827F:
  INY
::ChNativeP8280:
  STY ::ChNativeZp+$15
::ChNativeP8282:
  INC ::ChNativeZp+$00
::ChNativeP8284:
  JSR ::ChNativeP833D
::ChNativeP8287:
  PHA
::ChNativeP8288:
  EOR ::ChNativeZp+$0f
::ChNativeP828A:
  BEQ ::ChNativeP8291
::ChNativeP828C:
  STA ::ChNativeZp+$0f
::ChNativeP828E:
  JSR ::ChNativeP818B
::ChNativeP8291:
  PLA
::ChNativeP8292:
  STA ::ChNativeZp+$0f
::ChNativeP8294:
  RTS
::ChNativeP8295:
  LDY ::ChNativeRam+$00,x
::ChNativeP8298:
  BEQ ::ChNativeP829D
::ChNativeP829A:
  JSR ::ChNativeP8661
::ChNativeP829D:
  LDA ::ChNativeZp+$00
::ChNativeP829F:
  LSR A
::ChNativeP82A0:
  BCS ::ChNativeP82C1
::ChNativeP82A2:
  JSR ::ChNativeP8697
::ChNativeP82A5:
  LDA ::ChNativeZp+$13
::ChNativeP82A7:
  BEQ ::ChNativeP82B1
::ChNativeP82A9:
  CPX #$01
::ChNativeP82AB:
  BEQ ::ChNativeP82B2
::ChNativeP82AD:
  LDA ::ChNativeZp+$15
::ChNativeP82AF:
  BEQ ::ChNativeP82B7
::ChNativeP82B1:
  RTS
::ChNativeP82B2:
  DEC ::ChNativeRam+$10,x
::ChNativeP82B5:
  BNE ::ChNativeP82B1
::ChNativeP82B7:
  LDA ::ChNativeRam+$04,x
::ChNativeP82BA:
  AND #$04
::ChNativeP82BC:
  BNE ::ChNativeP82B1
::ChNativeP82BE:
  JMP ::ChNativeP8580
::ChNativeP82C1:
  LDA #$00
::ChNativeP82C3:
  STA ::ChNativeZp+$04
::ChNativeP82C5:
  JSR ::ChNativeP833D
::ChNativeP82C8:
  LSR A
::ChNativeP82C9:
  BCC ::ChNativeP82D7
::ChNativeP82CB:
  PHA
::ChNativeP82CC:
  JSR ::ChNativeP833D
::ChNativeP82CF:
  STA ::ChNativeZp+$03
::ChNativeP82D1:
  LDA ::ChNativeZp+$04
::ChNativeP82D3:
  JSR ::ChNativeP82DD
::ChNativeP82D6:
  PLA
::ChNativeP82D7:
  BEQ ::ChNativeP82EA
::ChNativeP82D9:
  INC ::ChNativeZp+$04
::ChNativeP82DB:
  BNE ::ChNativeP82C8
::ChNativeP82DD:
  jsr ChNativeDispatch82DD
::ChNativeP82EA:
  JSR ::ChNativeP833D
::ChNativeP82ED:
  TAY
::ChNativeP82EE:
  BNE ::ChNativeP8300
::ChNativeP82F0:
  STA ::ChNativeRam+$10,x
::ChNativeP82F3:
  LDA ::ChNativeRam+$04,x
::ChNativeP82F6:
  AND #$f8
::ChNativeP82F8:
  ORA #$04
::ChNativeP82FA:
  STA ::ChNativeRam+$04,x
::ChNativeP82FD:
  JMP ::ChNativeP80A3
::ChNativeP8300:
  LDA ::ChNativeRam+$04,x
::ChNativeP8303:
  ORA #$20
::ChNativeP8305:
  STA ::ChNativeRam+$04,x
::ChNativeP8308:
  LDA ::ChNativeRam+$18,x
::ChNativeP830B:
  ASL A
::ChNativeP830C:
  LDA #$54
::ChNativeP830E:
  BCS ::ChNativeP8312
::ChNativeP8310:
  LDA #$0a
::ChNativeP8312:
  STA ::ChNativeRam+$1c,x
::ChNativeP8315:
  TYA
::ChNativeP8316:
  BPL ::ChNativeP8322
::ChNativeP8318:
  CPX #$01
::ChNativeP831A:
  BNE ::ChNativeP831F
::ChNativeP831C:
  JSR ::ChNativeP858B
::ChNativeP831F:
  JMP ::ChNativeP8621
::ChNativeP8322:
  JSR ::ChNativeP858B
::ChNativeP8325:
  LDA #$ff
::ChNativeP8327:
  STA ::ChNativeRam+$7c,x
::ChNativeP832A:
  DEY
::ChNativeP832B:
  TXA
::ChNativeP832C:
  BNE ::ChNativeP8336
::ChNativeP832E:
  STA ::ChNativeZp+$03
::ChNativeP8330:
  TYA
::ChNativeP8331:
  EOR #$0f
::ChNativeP8333:
  JMP ::ChNativeP8613
::ChNativeP8336:
  TYA
::ChNativeP8337:
  CLC
::ChNativeP8338:
  ADC ::ChNativeZp+$12
::ChNativeP833A:
  JMP ::ChNativeP85BB
::ChNativeP833D:
  LDY #$00
::ChNativeP833F:
  jsr ChNativeLDAD0
::ChNativeP8341:
  INC ::ChNativeZp+$10
::ChNativeP8343:
  BNE ::ChNativeP8347
::ChNativeP8345:
  INC ::ChNativeZp+$11
::ChNativeP8347:
  RTS
::ChNativeP8348:
  TXA
::ChNativeP8349:
  ORA #$28
::ChNativeP834B:
  TAX
::ChNativeP834C:
  LDA ::ChNativeRam+$28,x
::ChNativeP834F:
  ORA ::ChNativeRam+$2c,x
::ChNativeP8352:
  BEQ ::ChNativeP8381
::ChNativeP8354:
  LDA ::ChNativeRam+$38,x
::ChNativeP8357:
  BEQ ::ChNativeP8382
::ChNativeP8359:
  LDY ::ChNativeRam+$00,x
::ChNativeP835C:
  BEQ ::ChNativeP8364
::ChNativeP835E:
  JSR ::ChNativeP8661
::ChNativeP8361:
  JSR ::ChNativeP8697
::ChNativeP8364:
  LDA ::ChNativeRam+$40,x
::ChNativeP8367:
  SEC
::ChNativeP8368:
  SBC ::ChNativeZp+$07
::ChNativeP836A:
  STA ::ChNativeRam+$40,x
::ChNativeP836D:
  BEQ ::ChNativeP8371
::ChNativeP836F:
  BCS ::ChNativeP8374
::ChNativeP8371:
  JSR ::ChNativeP8580
::ChNativeP8374:
  LDA ::ChNativeRam+$38,x
::ChNativeP8377:
  SEC
::ChNativeP8378:
  SBC ::ChNativeZp+$07
::ChNativeP837A:
  STA ::ChNativeRam+$38,x
::ChNativeP837D:
  BEQ ::ChNativeP8382
::ChNativeP837F:
  BCC ::ChNativeP8382
::ChNativeP8381:
  RTS
::ChNativeP8382:
  JSR ::ChNativeP8553
::ChNativeP8385:
  CMP #$20
::ChNativeP8387:
  BCS ::ChNativeP838F
::ChNativeP8389:
  JSR ::ChNativeP8458
::ChNativeP838C:
  JMP ::ChNativeP8382
::ChNativeP838F:
  PHA
::ChNativeP8390:
  ROL A
::ChNativeP8391:
  ROL A
::ChNativeP8392:
  ROL A
::ChNativeP8393:
  ROL A
::ChNativeP8394:
  AND #$07
::ChNativeP8396:
  TAY
::ChNativeP8397:
  DEY
::ChNativeP8398:
  LDA ::ChNativeRam+$30,x
::ChNativeP839B:
  ASL A
::ChNativeP839C:
  ASL A
::ChNativeP839D:
  BPL ::ChNativeP83A4
::ChNativeP839F:
  LDA $a76a,y
::ChNativeP83A2:
  BNE ::ChNativeP83BB
::ChNativeP83A4:
  ASL A
::ChNativeP83A5:
  ASL A
::ChNativeP83A6:
  LDA $a771,y
::ChNativeP83A9:
  BCC ::ChNativeP83BB
::ChNativeP83AB:
  STA ::ChNativeZp+$03
::ChNativeP83AD:
  LDA ::ChNativeRam+$30,x
::ChNativeP83B0:
  AND #$ef
::ChNativeP83B2:
  STA ::ChNativeRam+$30,x
::ChNativeP83B5:
  LDA ::ChNativeZp+$03
::ChNativeP83B7:
  LSR A
::ChNativeP83B8:
  CLC
::ChNativeP83B9:
  ADC ::ChNativeZp+$03
::ChNativeP83BB:
  CLC
::ChNativeP83BC:
  ADC ::ChNativeRam+$38,x
::ChNativeP83BF:
  STA ::ChNativeRam+$38,x
::ChNativeP83C2:
  TAY
::ChNativeP83C3:
  PLA
::ChNativeP83C4:
  AND #$1f
::ChNativeP83C6:
  BNE ::ChNativeP83CE
::ChNativeP83C8:
  JSR ::ChNativeP8580
::ChNativeP83CB:
  JMP ::ChNativeP8452
::ChNativeP83CE:
  PHA
::ChNativeP83CF:
  STY ::ChNativeZp+$04
::ChNativeP83D1:
  LDA ::ChNativeRam+$3c,x
::ChNativeP83D4:
  STA ::ChNativeZp+$01
::ChNativeP83D6:
  JSR ::ChNativeP8006
::ChNativeP83D9:
  LDA ::ChNativeZp+$01
::ChNativeP83DB:
  BNE ::ChNativeP83DF
::ChNativeP83DD:
  LDA #$01
::ChNativeP83DF:
  STA ::ChNativeRam+$40,x
::ChNativeP83E2:
  PLA
::ChNativeP83E3:
  TAY
::ChNativeP83E4:
  DEY
::ChNativeP83E5:
  LDA ::ChNativeRam+$30,x
::ChNativeP83E8:
  BPL ::ChNativeP83F5
::ChNativeP83EA:
  LDA ::ChNativeRam+$18,x
::ChNativeP83ED:
  BNE ::ChNativeP840A
::ChNativeP83EF:
  JSR ::ChNativeP8621
::ChNativeP83F2:
  JMP ::ChNativeP843F
::ChNativeP83F5:
  JSR ::ChNativeP858B
::ChNativeP83F8:
  LDA ::ChNativeZp+$0f
::ChNativeP83FA:
  LSR A
::ChNativeP83FB:
  BCS ::ChNativeP840A
::ChNativeP83FD:
  STY ::ChNativeZp+$03
::ChNativeP83FF:
  TXA
::ChNativeP8400:
  AND #$03
::ChNativeP8402:
  TAY
::ChNativeP8403:
  LDA #$ff
::ChNativeP8405:
  STA ::ChNativeRam+$7c,y
::ChNativeP8408:
  LDY ::ChNativeZp+$03
::ChNativeP840A:
  TXA
::ChNativeP840B:
  AND #$03
::ChNativeP840D:
  BNE ::ChNativeP841C
::ChNativeP840F:
  STA ::ChNativeZp+$03
::ChNativeP8411:
  TYA
::ChNativeP8412:
  AND #$0f
::ChNativeP8414:
  EOR #$0f
::ChNativeP8416:
  JSR ::ChNativeP8613
::ChNativeP8419:
  JMP ::ChNativeP843F
::ChNativeP841C:
  LDA #$08
::ChNativeP841E:
  STA ::ChNativeZp+$04
::ChNativeP8420:
  LDA ::ChNativeRam+$30,x
::ChNativeP8423:
  BIT ::ChNativeZp+$04
::ChNativeP8425:
  BEQ ::ChNativeP842A
::ChNativeP8427:
  CLC
::ChNativeP8428:
  ADC #$02
::ChNativeP842A:
  STY ::ChNativeZp+$03
::ChNativeP842C:
  AND #$07
::ChNativeP842E:
  TAY
::ChNativeP842F:
  LDA ::ChNativeZp+$03
::ChNativeP8431:
  CLC
::ChNativeP8432:
  ADC $a778,y
::ChNativeP8435:
  CLC
::ChNativeP8436:
  ADC ::ChNativeZp+$0b
::ChNativeP8438:
  CLC
::ChNativeP8439:
  ADC ::ChNativeRam+$34,x
::ChNativeP843C:
  JSR ::ChNativeP85BB
::ChNativeP843F:
  LDA ::ChNativeRam+$30,x
::ChNativeP8442:
  TAY
::ChNativeP8443:
  AND #$40
::ChNativeP8445:
  ASL A
::ChNativeP8446:
  STA ::ChNativeZp+$04
::ChNativeP8448:
  TYA
::ChNativeP8449:
  AND #$7f
::ChNativeP844B:
  ORA ::ChNativeZp+$04
::ChNativeP844D:
  STA ::ChNativeRam+$30,x
::ChNativeP8450:
  BPL ::ChNativeP8457
::ChNativeP8452:
  LDA #$ff
::ChNativeP8454:
  STA ::ChNativeRam+$40,x
::ChNativeP8457:
  RTS
::ChNativeP8458:
  CMP #$04
::ChNativeP845A:
  BCC ::ChNativeP8465
::ChNativeP845C:
  STA ::ChNativeZp+$04
::ChNativeP845E:
  JSR ::ChNativeP8553
::ChNativeP8461:
  STA ::ChNativeZp+$03
::ChNativeP8463:
  LDA ::ChNativeZp+$04
::ChNativeP8465:
  jsr ChNativeDispatch8465
::ChNativeP849A:
  LDA #$20
::ChNativeP849C:
  BNE ::ChNativeP84AB
::ChNativeP849E:
  LDA #$40
::ChNativeP84A0:
  BNE ::ChNativeP84AB
::ChNativeP84A2:
  LDA #$10
::ChNativeP84A4:
  ORA ::ChNativeRam+$30,x
::ChNativeP84A7:
  BNE ::ChNativeP84AE
::ChNativeP84A9:
  LDA #$08
::ChNativeP84AB:
  EOR ::ChNativeRam+$30,x
::ChNativeP84AE:
  STA ::ChNativeRam+$30,x
::ChNativeP84B1:
  RTS
::ChNativeP84B2:
  LDA #$00
::ChNativeP84B4:
  STA ::ChNativeZp+$08
::ChNativeP84B6:
  JSR ::ChNativeP8553
::ChNativeP84B9:
  LDY ::ChNativeZp+$03
::ChNativeP84BB:
  STA ::ChNativeZp+$0a
::ChNativeP84BD:
  STY ::ChNativeZp+$09
::ChNativeP84BF:
  RTS
::ChNativeP84C0:
  LDA ::ChNativeZp+$03
::ChNativeP84C2:
  STA ::ChNativeRam+$3c,x
::ChNativeP84C5:
  RTS
::ChNativeP84C6:
  LDA ::ChNativeRam+$30,x
::ChNativeP84C9:
  AND #$f8
::ChNativeP84CB:
  ORA ::ChNativeZp+$03
::ChNativeP84CD:
  STA ::ChNativeRam+$30,x
::ChNativeP84D0:
  RTS
::ChNativeP84D1:
  LDA ::ChNativeZp+$03
::ChNativeP84D3:
  STA ::ChNativeZp+$0b
::ChNativeP84D5:
  RTS
::ChNativeP84D6:
  LDA ::ChNativeZp+$03
::ChNativeP84D8:
  STA ::ChNativeRam+$34,x
::ChNativeP84DB:
  RTS
::ChNativeP84DC:
  LDA #$00
::ChNativeP84DE:
  BEQ ::ChNativeP84EA
::ChNativeP84E0:
  LDA #$04
::ChNativeP84E2:
  BNE ::ChNativeP84EA
::ChNativeP84E4:
  LDA #$08
::ChNativeP84E6:
  BNE ::ChNativeP84EA
::ChNativeP84E8:
  LDA #$0c
::ChNativeP84EA:
  STA ::ChNativeZp+$02
::ChNativeP84EC:
  TXA
::ChNativeP84ED:
  CLC
::ChNativeP84EE:
  ADC ::ChNativeZp+$02
::ChNativeP84F0:
  TAY
::ChNativeP84F1:
  LDA ::ChNativeZp+$04
::ChNativeP84F3:
  CMP #$12
::ChNativeP84F5:
  BCS ::ChNativeP8508
::ChNativeP84F7:
  LDA ::ChNativeRam+$44,y
::ChNativeP84FA:
  SEC
::ChNativeP84FB:
  SBC #$01
::ChNativeP84FD:
  BCS ::ChNativeP8501
::ChNativeP84FF:
  LDA ::ChNativeZp+$03
::ChNativeP8501:
  STA ::ChNativeRam+$44,y
::ChNativeP8504:
  BEQ ::ChNativeP8527
::ChNativeP8506:
  BNE ::ChNativeP8516
::ChNativeP8508:
  LDA ::ChNativeRam+$44,y
::ChNativeP850B:
  SEC
::ChNativeP850C:
  SBC #$01
::ChNativeP850E:
  BNE ::ChNativeP8527
::ChNativeP8510:
  STA ::ChNativeRam+$44,y
::ChNativeP8513:
  JSR ::ChNativeP8536
::ChNativeP8516:
  JSR ::ChNativeP8553
::ChNativeP8519:
  STA ::ChNativeZp+$03
::ChNativeP851B:
  JSR ::ChNativeP8553
::ChNativeP851E:
  STA ::ChNativeRam+$28,x
::ChNativeP8521:
  LDA ::ChNativeZp+$03
::ChNativeP8523:
  STA ::ChNativeRam+$2c,x
::ChNativeP8526:
  RTS
::ChNativeP8527:
  LDA #$02
::ChNativeP8529:
  CLC
::ChNativeP852A:
  ADC ::ChNativeRam+$28,x
::ChNativeP852D:
  STA ::ChNativeRam+$28,x
::ChNativeP8530:
  BCC ::ChNativeP8535
::ChNativeP8532:
  INC ::ChNativeRam+$2c,x
::ChNativeP8535:
  RTS
::ChNativeP8536:
  LDA ::ChNativeRam+$30,x
::ChNativeP8539:
  AND #$97
::ChNativeP853B:
  ORA ::ChNativeZp+$03
::ChNativeP853D:
  STA ::ChNativeRam+$30,x
::ChNativeP8540:
  RTS
::ChNativeP8541:
  PLA
::ChNativeP8542:
  PLA
::ChNativeP8543:
  LDA #$00
::ChNativeP8545:
  STA ::ChNativeRam+$28,x
::ChNativeP8548:
  STA ::ChNativeRam+$2c,x
::ChNativeP854B:
  LDA ::ChNativeZp+$0f
::ChNativeP854D:
  LSR A
::ChNativeP854E:
  BCS ::ChNativeP8569
::ChNativeP8550:
  JMP ::ChNativeP80A3
::ChNativeP8553:
  LDA ::ChNativeRam+$28,x
::ChNativeP8556:
  LDY ::ChNativeRam+$2c,x
::ChNativeP8559:
  STA ::ChNativeZp+$01
  STA ChNativeMappedC1
::ChNativeP855B:
  STY ::ChNativeZp+$02
  jsr ChNativeMapC1High
::ChNativeP855D:
  LDY #$00
::ChNativeP855F:
  LDA (ChNativeMappedC1),y
::ChNativeP8561:
  INC ::ChNativeRam+$28,x
::ChNativeP8564:
  BNE ::ChNativeP8569
::ChNativeP8566:
  INC ::ChNativeRam+$2c,x
::ChNativeP8569:
  RTS
::ChNativeP8580:
  LDA ::ChNativeRam+$04,x
::ChNativeP8583:
  AND #$f8
::ChNativeP8585:
  ORA #$03
::ChNativeP8587:
  STA ::ChNativeRam+$04,x
::ChNativeP858A:
  RTS
::ChNativeP858B:
  TYA
::ChNativeP858C:
  PHA
::ChNativeP858D:
  LDY #$00
::ChNativeP858F:
  LDA ::ChNativeRam+$04,x
::ChNativeP8592:
  AND #$f8
::ChNativeP8594:
  STA ::ChNativeRam+$04,x
::ChNativeP8597:
  CPX #$29
::ChNativeP8599:
  BEQ ::ChNativeP85AD
::ChNativeP859B:
  CPX #$01
::ChNativeP859D:
  BNE ::ChNativeP85B4
::ChNativeP859F:
  LDA ::ChNativeZp+$13
::ChNativeP85A1:
  STA ::ChNativeZp+$01
::ChNativeP85A3:
  LDA ::ChNativeRam+$0c,x
::ChNativeP85A6:
  STA ::ChNativeZp+$04
::ChNativeP85A8:
  JSR ::ChNativeP8006
::ChNativeP85AB:
  LDY ::ChNativeZp+$01
::ChNativeP85AD:
  INY
::ChNativeP85AE:
  INC ::ChNativeRam+$04,x
::ChNativeP85B1:
  INC ::ChNativeRam+$04,x
::ChNativeP85B4:
  TYA
::ChNativeP85B5:
  STA ::ChNativeRam+$10,x
::ChNativeP85B8:
  PLA
::ChNativeP85B9:
  TAY
::ChNativeP85BA:
  RTS
::ChNativeP85BB:
  CMP #$60
::ChNativeP85BD:
  BCC ::ChNativeP85C1
::ChNativeP85BF:
  LDA #$5f
::ChNativeP85C1:
  STA ::ChNativeZp+$03
::ChNativeP85C3:
  INC ::ChNativeZp+$03
::ChNativeP85C5:
  CPX #$28
::ChNativeP85C7:
  BCC ::ChNativeP8607
::ChNativeP85C9:
  LDA ::ChNativeRam+$1c,x
::ChNativeP85CC:
  BEQ ::ChNativeP85FA
::ChNativeP85CE:
  CMP ::ChNativeZp+$03
::ChNativeP85D0:
  BNE ::ChNativeP85D9
::ChNativeP85D2:
  LDA ::ChNativeRam+$30,x
::ChNativeP85D5:
  BPL ::ChNativeP85FA
::ChNativeP85D7:
  BMI ::ChNativeP8621
::ChNativeP85D9:
  LDA ::ChNativeRam+$18,x
::ChNativeP85DC:
  BEQ ::ChNativeP85FA
::ChNativeP85DE:
  BCS ::ChNativeP85E4
::ChNativeP85E0:
  ORA #$80
::ChNativeP85E2:
  BNE ::ChNativeP85E6
::ChNativeP85E4:
  AND #$7f
::ChNativeP85E6:
  STA ::ChNativeRam+$18,x
::ChNativeP85E9:
  LDA ::ChNativeRam+$04,x
::ChNativeP85EC:
  ORA #$20
::ChNativeP85EE:
  STA ::ChNativeRam+$04,x
::ChNativeP85F1:
  LDA ::ChNativeZp+$03
::ChNativeP85F3:
  LDY ::ChNativeRam+$1c,x
::ChNativeP85F6:
  STY ::ChNativeZp+$03
::ChNativeP85F8:
  BNE ::ChNativeP8604
::ChNativeP85FA:
  LDA ::ChNativeRam+$04,x
::ChNativeP85FD:
  AND #$df
::ChNativeP85FF:
  STA ::ChNativeRam+$04,x
::ChNativeP8602:
  LDA ::ChNativeZp+$03
::ChNativeP8604:
  STA ::ChNativeRam+$1c,x
::ChNativeP8607:
  ASL ::ChNativeZp+$03
::ChNativeP8609:
  LDY ::ChNativeZp+$03
::ChNativeP860B:
  LDA $ab19,y
::ChNativeP860E:
  STA ::ChNativeZp+$03
::ChNativeP8610:
  LDA $ab1a,y
::ChNativeP8613:
  STA ::ChNativeRam+$24,x
::ChNativeP8616:
  LDA ::ChNativeZp+$03
::ChNativeP8618:
  STA ::ChNativeRam+$20,x
::ChNativeP861B:
  LDY #$04
::ChNativeP861D:
  LDA (ChNativeMappedC5),y
::ChNativeP861F:
  BMI ::ChNativeP8629
::ChNativeP8621:
  LDA ::ChNativeRam+$04,x
::ChNativeP8624:
  AND #$08
::ChNativeP8626:
  BNE ::ChNativeP8629
::ChNativeP8628:
  RTS
::ChNativeP8629:
  LDA #$00
::ChNativeP862B:
  STA ::ChNativeRam+$08,x
::ChNativeP862E:
  LDA ::ChNativeRam+$04,x
::ChNativeP8631:
  AND #$37
::ChNativeP8633:
  STA ::ChNativeRam+$04,x
::ChNativeP8636:
  RTS
::ChNativeP8637:
  CPX #$01
::ChNativeP8639:
  BNE ::ChNativeP863F
::ChNativeP863B:
  LDA ::ChNativeZp+$03
::ChNativeP863D:
  BNE ::ChNativeP8648
::ChNativeP863F:
  LDA ::ChNativeRam+$0c,x
::ChNativeP8642:
  AND #$c0
::ChNativeP8644:
  ORA ::ChNativeZp+$03
::ChNativeP8646:
  ORA #$30
::ChNativeP8648:
  STA ::ChNativeRam+$0c,x
::ChNativeP864B:
  RTS
::ChNativeP864C:
  INC ::ChNativeZp+$03
::ChNativeP864E:
  LDA ::ChNativeZp+$03
::ChNativeP8650:
  CMP ::ChNativeRam+$00,x
::ChNativeP8653:
  BEQ ::ChNativeP867D
::ChNativeP8655:
  STA ::ChNativeRam+$00,x
::ChNativeP8658:
  TAY
::ChNativeP8659:
  LDA ::ChNativeRam+$04,x
::ChNativeP865C:
  ORA #$08
::ChNativeP865E:
  STA ::ChNativeRam+$04,x
::ChNativeP8661:
  DEY
::ChNativeP8662:
  LDA #$00
::ChNativeP8664:
  STA ::ChNativeZp+$03
::ChNativeP8666:
  TYA
::ChNativeP8667:
  ASL A
::ChNativeP8668:
  ROL ::ChNativeZp+$03
::ChNativeP866A:
  ASL A
::ChNativeP866B:
  ROL ::ChNativeZp+$03
::ChNativeP866D:
  ASL A
::ChNativeP866E:
  ROL ::ChNativeZp+$03
::ChNativeP8670:
  CLC
::ChNativeP8671:
  ADC $ac02
::ChNativeP8674:
  STA ::ChNativeZp+$05
  sta ChNativeMappedC5
::ChNativeP8676:
  LDA ::ChNativeZp+$03
::ChNativeP8678:
  ADC $ac01
::ChNativeP867B:
  STA ::ChNativeZp+$06
  jsr ChNativeMapC5High
::ChNativeP867D:
  RTS
::ChNativeP867E:
  LDA ::ChNativeZp+$03
::ChNativeP8680:
  STA ::ChNativeRam+$14,x
::ChNativeP8683:
  RTS
::ChNativeP8684:
  LDA ::ChNativeZp+$03
::ChNativeP8686:
  STA ::ChNativeRam+$18,x
::ChNativeP8689:
  RTS
::ChNativeP868A:
  LDA ::ChNativeRam+$0c,x
::ChNativeP868D:
  AND #$0f
::ChNativeP868F:
  ORA ::ChNativeZp+$03
::ChNativeP8691:
  ORA #$30
::ChNativeP8693:
  STA ::ChNativeRam+$0c,x
::ChNativeP8696:
  RTS
::ChNativeP8697:
  LDA ::ChNativeRam+$10,x
::ChNativeP869A:
  STA ::ChNativeZp+$04
::ChNativeP869C:
  LDA ::ChNativeRam+$04,x
::ChNativeP869F:
  AND #$07
::ChNativeP86A1:
  jsr ChNativeDispatch86A1
::ChNativeP86AE:
  LDY #$00
::ChNativeP86B0:
  LDA (ChNativeMappedC5),y
::ChNativeP86B2:
  TAY
::ChNativeP86B3:
  LDA ::ChNativeZp+$04
::ChNativeP86B5:
  CLC
::ChNativeP86B6:
  ADC $aaf3,y
::ChNativeP86B9:
  BCS ::ChNativeP86BF
::ChNativeP86BB:
  CMP #$f0
::ChNativeP86BD:
  BCC ::ChNativeP86FA
::ChNativeP86BF:
  LDA #$f0
::ChNativeP86C1:
  BNE ::ChNativeP86F7
::ChNativeP86C3:
  LDY #$01
::ChNativeP86C5:
  LDA (ChNativeMappedC5),y
::ChNativeP86C7:
  BEQ ::ChNativeP86D8
::ChNativeP86C9:
  TAY
::ChNativeP86CA:
  LDA ::ChNativeZp+$04
::ChNativeP86CC:
  SEC
::ChNativeP86CD:
  SBC $aaf3,y
::ChNativeP86D0:
  BCC ::ChNativeP86D8
::ChNativeP86D2:
  LDY #$02
::ChNativeP86D4:
  CMP (ChNativeMappedC5),y
::ChNativeP86D6:
  BCS ::ChNativeP86FA
::ChNativeP86D8:
  LDY #$02
::ChNativeP86DA:
  LDA (ChNativeMappedC5),y
::ChNativeP86DC:
  JMP ::ChNativeP86F7
::ChNativeP86DF:
  TXA
::ChNativeP86E0:
  AND #$03
::ChNativeP86E2:
  CMP #$01
::ChNativeP86E4:
  BEQ ::ChNativeP86F5
::ChNativeP86E6:
  LDY #$03
::ChNativeP86E8:
  LDA (ChNativeMappedC5),y
::ChNativeP86EA:
  BEQ ::ChNativeP86FD
::ChNativeP86EC:
  TAY
::ChNativeP86ED:
  LDA ::ChNativeZp+$04
::ChNativeP86EF:
  SEC
::ChNativeP86F0:
  SBC $aaf3,y
::ChNativeP86F3:
  BCS ::ChNativeP86FA
::ChNativeP86F5:
  LDA #$00
::ChNativeP86F7:
  INC ::ChNativeRam+$04,x
::ChNativeP86FA:
  STA ::ChNativeRam+$10,x
::ChNativeP86FD:
  CPX #$28
::ChNativeP86FF:
  BCC ::ChNativeP8715
::ChNativeP8701:
  LDA ::ChNativeZp+$0f
::ChNativeP8703:
  LSR A
::ChNativeP8704:
  BCC ::ChNativeP8709
::ChNativeP8706:
  JMP ::ChNativeP887E
::ChNativeP8709:
  LDA ::ChNativeZp+$0d
::ChNativeP870B:
  LDY ::ChNativeZp+$0c
::ChNativeP870D:
  BMI ::ChNativeP8711
::ChNativeP870F:
  EOR #$ff
::ChNativeP8711:
  CMP #$ff
::ChNativeP8713:
  BNE ::ChNativeP871E
::ChNativeP8715:
  TXA
::ChNativeP8716:
  AND #$03
::ChNativeP8718:
  CMP #$01
::ChNativeP871A:
  BNE ::ChNativeP873E
::ChNativeP871C:
  BEQ ::ChNativeP8730
::ChNativeP871E:
  CPX #$29
::ChNativeP8720:
  BNE ::ChNativeP8739
::ChNativeP8722:
  STA ::ChNativeZp+$04
::ChNativeP8724:
  LDA ::ChNativeRam+$40,x
::ChNativeP8727:
  STA ::ChNativeZp+$01
::ChNativeP8729:
  JSR ::ChNativeP8006
::ChNativeP872C:
  LDA ::ChNativeZp+$01
::ChNativeP872E:
  BEQ ::ChNativeP8788
::ChNativeP8730:
  LDA ::ChNativeRam+$10,x
::ChNativeP8733:
  BEQ ::ChNativeP8788
::ChNativeP8735:
  LDA #$ff
::ChNativeP8737:
  BNE ::ChNativeP8788
::ChNativeP8739:
  CMP ::ChNativeRam+$10,x
::ChNativeP873C:
  BCC ::ChNativeP8741
::ChNativeP873E:
  LDA ::ChNativeRam+$10,x
::ChNativeP8741:
  LSR A
::ChNativeP8742:
  LSR A
::ChNativeP8743:
  LSR A
::ChNativeP8744:
  LSR A
::ChNativeP8745:
  EOR #$0f
::ChNativeP8747:
  STA ::ChNativeZp+$03
::ChNativeP8749:
  LDY #$06
::ChNativeP874B:
  LDA (ChNativeMappedC5),y
::ChNativeP874D:
  CMP #$05
::ChNativeP874F:
  BCC ::ChNativeP8775
::ChNativeP8751:
  STA ::ChNativeZp+$04
::ChNativeP8753:
  LDY ::ChNativeRam+$08,x
::ChNativeP8756:
  LDA ::ChNativeRam+$04,x
::ChNativeP8759:
  ASL A
::ChNativeP875A:
  ASL A
::ChNativeP875B:
  TYA
::ChNativeP875C:
  BCC ::ChNativeP8760
::ChNativeP875E:
  EOR #$ff
::ChNativeP8760:
  BEQ ::ChNativeP8775
::ChNativeP8762:
  STA ::ChNativeZp+$01
::ChNativeP8764:
  JSR ::ChNativeP8006
::ChNativeP8767:
  LDA ::ChNativeZp+$01
::ChNativeP8769:
  LSR A
::ChNativeP876A:
  LSR A
::ChNativeP876B:
  CMP #$10
::ChNativeP876D:
  BCS ::ChNativeP8783
::ChNativeP876F:
  CMP ::ChNativeZp+$03
::ChNativeP8771:
  BCC ::ChNativeP8775
::ChNativeP8773:
  STA ::ChNativeZp+$03
::ChNativeP8775:
  LDA #$10
::ChNativeP8777:
  STA ::ChNativeZp+$04
::ChNativeP8779:
  LDA ::ChNativeRam+$0c,x
::ChNativeP877C:
  SEC
::ChNativeP877D:
  SBC ::ChNativeZp+$03
::ChNativeP877F:
  BIT ::ChNativeZp+$04
::ChNativeP8781:
  BNE ::ChNativeP8788
::ChNativeP8783:
  LDA ::ChNativeRam+$0c,x
::ChNativeP8786:
  AND #$f0
::ChNativeP8788:
  LDY #$00
::ChNativeP878A:
  JSR ::ChNativeP80B7
::ChNativeP878D:
  TXA
::ChNativeP878E:
  AND #$03
::ChNativeP8790:
  TAY
::ChNativeP8791:
  LDA ::ChNativeRam+$7c,y
::ChNativeP8794:
  BMI ::ChNativeP87EA
::ChNativeP8796:
  LDY #$05
::ChNativeP8798:
  LDA (ChNativeMappedC5),y
::ChNativeP879A:
  BEQ ::ChNativeP87EA
::ChNativeP879C:
  STA ::ChNativeZp+$04
::ChNativeP879E:
  LDY ::ChNativeRam+$08,x
::ChNativeP87A1:
  LDA ::ChNativeRam+$04,x
::ChNativeP87A4:
  ASL A
::ChNativeP87A5:
  ASL A
::ChNativeP87A6:
  TYA
::ChNativeP87A7:
  BCC ::ChNativeP87AB
::ChNativeP87A9:
  EOR #$ff
::ChNativeP87AB:
  BEQ ::ChNativeP87EA
::ChNativeP87AD:
  STA ::ChNativeZp+$01
::ChNativeP87AF:
  JSR ::ChNativeP8006
::ChNativeP87B2:
  LDA ::ChNativeZp+$01
::ChNativeP87B4:
  LSR A
::ChNativeP87B5:
  ROR ::ChNativeZp+$02
::ChNativeP87B7:
  LSR A
::ChNativeP87B8:
  ROR ::ChNativeZp+$02
::ChNativeP87BA:
  LSR A
::ChNativeP87BB:
  ROR ::ChNativeZp+$02
::ChNativeP87BD:
  LSR A
::ChNativeP87BE:
  ROR ::ChNativeZp+$02
::ChNativeP87C0:
  TAY
::ChNativeP87C1:
  ORA ::ChNativeZp+$02
::ChNativeP87C3:
  BEQ ::ChNativeP87EA
::ChNativeP87C5:
  LDA ::ChNativeRam+$04,x
::ChNativeP87C8:
  BMI ::ChNativeP87D8
::ChNativeP87CA:
  CLC
::ChNativeP87CB:
  LDA ::ChNativeZp+$02
::ChNativeP87CD:
  ADC ::ChNativeRam+$20,x
::ChNativeP87D0:
  STA ::ChNativeZp+$02
::ChNativeP87D2:
  TYA
::ChNativeP87D3:
  ADC ::ChNativeRam+$24,x
::ChNativeP87D6:
  BNE ::ChNativeP87E7
::ChNativeP87D8:
  SEC
::ChNativeP87D9:
  LDA ::ChNativeRam+$20,x
::ChNativeP87DC:
  SBC ::ChNativeZp+$02
::ChNativeP87DE:
  STA ::ChNativeZp+$02
::ChNativeP87E0:
  LDA ::ChNativeRam+$24,x
::ChNativeP87E3:
  STY ::ChNativeZp+$01
::ChNativeP87E5:
  SBC ::ChNativeZp+$01
::ChNativeP87E7:
  TAY
::ChNativeP87E8:
  BNE ::ChNativeP87F2
::ChNativeP87EA:
  LDA ::ChNativeRam+$20,x
::ChNativeP87ED:
  STA ::ChNativeZp+$02
::ChNativeP87EF:
  LDY ::ChNativeRam+$24,x
::ChNativeP87F2:
  CPX #$28
::ChNativeP87F4:
  BCS ::ChNativeP8813
::ChNativeP87F6:
  LDA ::ChNativeZp+$16
::ChNativeP87F8:
  BPL ::ChNativeP8813
::ChNativeP87FA:
  LDA ::ChNativeZp+$18
::ChNativeP87FC:
  BEQ ::ChNativeP8813
::ChNativeP87FE:
  STA ::ChNativeZp+$04
::ChNativeP8800:
  STY ::ChNativeZp+$01
::ChNativeP8802:
  LDA ::ChNativeZp+$02
::ChNativeP8804:
  PHA
::ChNativeP8805:
  JSR ::ChNativeP8006
::ChNativeP8808:
  PLA
::ChNativeP8809:
  CLC
::ChNativeP880A:
  ADC ::ChNativeZp+$02
::ChNativeP880C:
  STA ::ChNativeZp+$02
::ChNativeP880E:
  LDA #$00
::ChNativeP8810:
  ADC ::ChNativeZp+$01
::ChNativeP8812:
  TAY
::ChNativeP8813:
  TXA
::ChNativeP8814:
  AND #$03
::ChNativeP8816:
  BNE ::ChNativeP8827
::ChNativeP8818:
  TYA
::ChNativeP8819:
  AND #$0f
::ChNativeP881B:
  LDY #$07
::ChNativeP881D:
  ORA (ChNativeMappedC5),y
::ChNativeP881F:
  STA ::ChNativeZp+$02
::ChNativeP8821:
  LDA #$00
::ChNativeP8823:
  STA ::ChNativeZp+$01
::ChNativeP8825:
  BEQ ::ChNativeP8862
::ChNativeP8827:
  TYA
::ChNativeP8828:
  LDY #$08
::ChNativeP882A:
  DEY
::ChNativeP882B:
  CMP $ab13,y
::ChNativeP882E:
  BCC ::ChNativeP882A
::ChNativeP8830:
  STA ::ChNativeZp+$01
::ChNativeP8832:
  TYA
::ChNativeP8833:
  CLC
::ChNativeP8834:
  ADC ::ChNativeZp+$01
::ChNativeP8836:
  TAY
::ChNativeP8837:
  AND #$07
::ChNativeP8839:
  CLC
::ChNativeP883A:
  ADC #$07
::ChNativeP883C:
  STA ::ChNativeZp+$01
::ChNativeP883E:
  TYA
::ChNativeP883F:
  AND #$38
::ChNativeP8841:
  EOR #$38
::ChNativeP8843:
  BEQ ::ChNativeP884E
::ChNativeP8845:
  LSR ::ChNativeZp+$01
::ChNativeP8847:
  ROR ::ChNativeZp+$02
::ChNativeP8849:
  SEC
::ChNativeP884A:
  SBC #$08
::ChNativeP884C:
  BNE ::ChNativeP8845
::ChNativeP884E:
  LDY #$00
::ChNativeP8850:
  LDA ::ChNativeRam+$14,x
::ChNativeP8853:
  BEQ ::ChNativeP8862
::ChNativeP8855:
  BPL ::ChNativeP8858
::ChNativeP8857:
  DEY
::ChNativeP8858:
  CLC
::ChNativeP8859:
  ADC ::ChNativeZp+$02
::ChNativeP885B:
  STA ::ChNativeZp+$02
::ChNativeP885D:
  TYA
::ChNativeP885E:
  ADC ::ChNativeZp+$01
::ChNativeP8860:
  STA ::ChNativeZp+$01
::ChNativeP8862:
  LDY #$02
::ChNativeP8864:
  LDA ::ChNativeZp+$02
::ChNativeP8866:
  JSR ::ChNativeP80B7
::ChNativeP8869:
  TXA
::ChNativeP886A:
  AND #$03
::ChNativeP886C:
  TAY
::ChNativeP886D:
  LDA ::ChNativeZp+$01
::ChNativeP886F:
  CMP ::ChNativeRam+$7c,y
::ChNativeP8872:
  BEQ ::ChNativeP887E
::ChNativeP8874:
  STA ::ChNativeRam+$7c,y
::ChNativeP8877:
  ORA #$08
::ChNativeP8879:
  LDY #$03
::ChNativeP887B:
  JSR ::ChNativeP80B7
::ChNativeP887E:
  LDA ::ChNativeRam+$04,x
::ChNativeP8881:
  AND #$20
::ChNativeP8883:
  BEQ ::ChNativeP88D8
::ChNativeP8885:
  LDA ::ChNativeRam+$18,x
::ChNativeP8888:
  BEQ ::ChNativeP88D0
::ChNativeP888A:
  LDY #$00
::ChNativeP888C:
  ASL A
::ChNativeP888D:
  PHP
::ChNativeP888E:
  BCC ::ChNativeP8896
::ChNativeP8890:
  EOR #$ff
::ChNativeP8892:
  CLC
::ChNativeP8893:
  ADC #$01
::ChNativeP8895:
  DEY
::ChNativeP8896:
  CLC
::ChNativeP8897:
  ADC ::ChNativeRam+$20,x
::ChNativeP889A:
  STA ::ChNativeRam+$20,x
::ChNativeP889D:
  TYA
::ChNativeP889E:
  ADC ::ChNativeRam+$24,x
::ChNativeP88A1:
  STA ::ChNativeRam+$24,x
::ChNativeP88A4:
  LDA ::ChNativeRam+$1c,x
::ChNativeP88A7:
  ASL A
::ChNativeP88A8:
  TAY
::ChNativeP88A9:
  SEC
::ChNativeP88AA:
  LDA ::ChNativeRam+$20,x
::ChNativeP88AD:
  SBC $ab19,y
::ChNativeP88B0:
  LDA ::ChNativeRam+$24,x
::ChNativeP88B3:
  AND #$3f
::ChNativeP88B5:
  SBC $ab1a,y
::ChNativeP88B8:
  LDA #$ff
::ChNativeP88BA:
  ADC #$00
::ChNativeP88BC:
  PLP
::ChNativeP88BD:
  ADC #$00
::ChNativeP88BF:
  BNE ::ChNativeP88D8
::ChNativeP88C1:
  TXA
::ChNativeP88C2:
  BEQ ::ChNativeP88D8
::ChNativeP88C4:
  LDA $ab19,y
::ChNativeP88C7:
  STA ::ChNativeRam+$20,x
::ChNativeP88CA:
  LDA $ab1a,y
::ChNativeP88CD:
  STA ::ChNativeRam+$24,x
::ChNativeP88D0:
  LDA ::ChNativeRam+$04,x
::ChNativeP88D3:
  AND #$df
::ChNativeP88D5:
  STA ::ChNativeRam+$04,x
::ChNativeP88D8:
  LDY #$04
::ChNativeP88DA:
  LDA (ChNativeMappedC5),y
::ChNativeP88DC:
  AND #$7f
::ChNativeP88DE:
  BEQ ::ChNativeP88F2
::ChNativeP88E0:
  CLC
::ChNativeP88E1:
  ADC ::ChNativeRam+$08,x
::ChNativeP88E4:
  STA ::ChNativeRam+$08,x
::ChNativeP88E7:
  BCC ::ChNativeP88F2
::ChNativeP88E9:
  LDA ::ChNativeRam+$04,x
::ChNativeP88EC:
  CLC
::ChNativeP88ED:
  ADC #$40
::ChNativeP88EF:
  STA ::ChNativeRam+$04,x
::ChNativeP88F2:
  RTS
::ChNativePAF99:
  TAY
::ChNativePAF9A:
  LDA $d1a0,y
::ChNativePAF9D:
  JMP ::ChNativeP8003
ChNativeDispatch8169:
  asl
  tay
  iny
  lda #255
  sta ChNativeDispatchBase
  pla
  pla
  lda #$81
  sta ChNativeZp+2
  jsr ChNativeMapC1High
  lda #$6b
  sta ChNativeZp+1
  sta ChNativeMappedC1
  jmp ChNativeP802C
ChNativeDispatch82DD:
  asl
  tay
  iny
  lda #7
  sta ChNativeDispatchBase
  pla
  pla
  lda #$82
  sta ChNativeZp+2
  jsr ChNativeMapC1High
  lda #$df
  sta ChNativeZp+1
  sta ChNativeMappedC1
  jmp ChNativeP802C
ChNativeDispatch8465:
  asl
  tay
  iny
  lda #12
  sta ChNativeDispatchBase
  pla
  pla
  lda #$84
  sta ChNativeZp+2
  jsr ChNativeMapC1High
  lda #$67
  sta ChNativeZp+1
  sta ChNativeMappedC1
  jmp ChNativeP802C
ChNativeDispatch86A1:
  asl
  tay
  iny
  lda #37
  sta ChNativeDispatchBase
  pla
  pla
  lda #$86
  sta ChNativeZp+2
  jsr ChNativeMapC1High
  lda #$a3
  sta ChNativeZp+1
  sta ChNativeMappedC1
  jmp ChNativeP802C
ChNativeSyncC1Low:
  php
  pha
  lda ChNativeZp+1
  sta ChNativeMappedC1
  pla
  plp
  rts
ChNativeMapC1High:
  php
  pha
  lda ChNativeZp+2
  clc
  adc #$22
  sta ChNativeMappedC1+1
  pla
  plp
  rts
ChNativeMapC5High:
  php
  pha
  lda ChNativeZp+6
  clc
  adc #$22
  sta ChNativeMappedC5+1
  pla
  plp
  rts
ChNativeLDAD0:
  php
  stx ChNativeTempX
  ldx #16
  jmp ChNativeRead
ChNativeRead:
  sty ChNativeTempY
  tya
  clc
  adc ChNativeZp,x
  sta ChNativePointer
  lda ChNativeZp+1,x
  adc #$22
  sta ChNativePointer+1
  ldy #0
  lda (ChNativePointer),y
  ldx ChNativeTempX
  ldy ChNativeTempY
  plp
  ora #0
  rts
ChNativeJump:
  php
  pha
  stx ChNativeTempX
  tya
  lsr
  clc
  adc ChNativeDispatchBase
  tax
  lda ChNativeTargetLo,x
  sta ChNativePointer
  lda ChNativeTargetHi,x
  sta ChNativePointer+1
  ldx ChNativeTempX
  pla
  plp
  jmp (ChNativePointer)
ChNativeSourceInit=ChNativePAF99
ChNativeSourcePlay=ChNativeP8000
ChNativeEnd:
.assert *<=$dfc0,lderror,"Chip code leaves original jump targets and gameplay bridge room"
.segment "CHIP_NATIVE_JUMP_SOURCE"
ChNativeTargetLo:
 .byte <::ChNativeP817C,<::ChNativeP817F,<::ChNativeP819B,<::ChNativeP81D8,<::ChNativeP81E0,<::ChNativeP81E7,<::ChNativeP81EE,<::ChNativeP8204,<::ChNativeP864C,<::ChNativeP868A,<::ChNativeP8637,<::ChNativeP8684,<::ChNativeP867E,<::ChNativeP849A,<::ChNativeP849E,<::ChNativeP84A2,<::ChNativeP84A9,<::ChNativeP8536,<::ChNativeP84B2,<::ChNativeP84C0,<::ChNativeP8637,<::ChNativeP864C,<::ChNativeP84C6,<::ChNativeP84D1,<::ChNativeP84D6,<::ChNativeP867E,<::ChNativeP8684,<::ChNativeP84DC,<::ChNativeP84E0,<::ChNativeP84E4,<::ChNativeP84E8,<::ChNativeP84DC,<::ChNativeP84E0,<::ChNativeP84E4,<::ChNativeP84E8,<::ChNativeP851B,<::ChNativeP8541,<::ChNativeP868A,<::ChNativeP86AE,<::ChNativeP86C3,<::ChNativeP86FD,<::ChNativeP86DF,<::ChNativeP88F2
.assert *<=$a300,lderror,"Chip low jump table exceeds real publisher gap"
.segment "CHIP_NATIVE_JUMP_TARGET"
ChNativeTargetHi:
 .byte >::ChNativeP817C,>::ChNativeP817F,>::ChNativeP819B,>::ChNativeP81D8,>::ChNativeP81E0,>::ChNativeP81E7,>::ChNativeP81EE,>::ChNativeP8204,>::ChNativeP864C,>::ChNativeP868A,>::ChNativeP8637,>::ChNativeP8684,>::ChNativeP867E,>::ChNativeP849A,>::ChNativeP849E,>::ChNativeP84A2,>::ChNativeP84A9,>::ChNativeP8536,>::ChNativeP84B2,>::ChNativeP84C0,>::ChNativeP8637,>::ChNativeP864C,>::ChNativeP84C6,>::ChNativeP84D1,>::ChNativeP84D6,>::ChNativeP867E,>::ChNativeP8684,>::ChNativeP84DC,>::ChNativeP84E0,>::ChNativeP84E4,>::ChNativeP84E8,>::ChNativeP84DC,>::ChNativeP84E0,>::ChNativeP84E4,>::ChNativeP84E8,>::ChNativeP851B,>::ChNativeP8541,>::ChNativeP868A,>::ChNativeP86AE,>::ChNativeP86C3,>::ChNativeP86FD,>::ChNativeP86DF,>::ChNativeP88F2
.assert *<=$dff0,lderror,"Chip genuine target table remains in C94"
.segment "CHIP_NATIVE_DATA_A"
ChNativeDataA:
.incbin "reference/new-roster-audio/chip/Chip 'n Dale Rescue Rangers [Chip to Dale no Daisakusen] (1990-06-08)(Capcom).nsf",128+$100,$1d00
.segment "CHIP_NATIVE_DATA_C"
ChNativeDataC:
.incbin "reference/new-roster-audio/chip/Chip 'n Dale Rescue Rangers [Chip to Dale no Daisakusen] (1990-06-08)(Capcom).nsf",128+$1e00,$11b0
.popseg
