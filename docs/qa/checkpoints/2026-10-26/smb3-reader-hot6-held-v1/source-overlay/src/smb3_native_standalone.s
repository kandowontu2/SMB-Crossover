; Authenticated original SMB3 NSF, fixed twelve cold role contracts.
.if ::ENABLE_MMC5_EXPANDED
.pushseg
.segment "SMB3_NATIVE_CORE"
B3CoreStart:
.assert B3CoreStart=$cbe8,lderror,"SMB3 core actual freed C38 range"
B3SourceA000:
 LDA #$ff
B3SourceA002:
 STA $4017
B3SourceA005:
 LDA B3SourceImage+$27
B3SourceA008:
 jne ::B3SourceA017
B3SourceA00A:
 LDA B3SourceImage+$17
B3SourceA00D:
 jne ::B3SourceA04F
B3SourceA00F:
 LDA B3SourceImage+$1d
B3SourceA012:
 jne ::B3SourceA08F
B3SourceA014:
 JMP ::B3SourceA078
B3SourceA017:
 .byte $8d
B3SourceA018:
 .byte $e7
B3SourceA019:
 .byte $04
B3SourceA01A:
 .byte $8d
B3SourceA01B:
 .byte $ed
B3SourceA01C:
 .byte $04
B3SourceA01D:
 .byte $c9
B3SourceA01E:
 .byte $02
B3SourceA01F:
 .byte $d0
B3SourceA020:
 .byte $12
B3SourceA021:
 .byte $a9
B3SourceA022:
 .byte $00
B3SourceA023:
 .byte $8d
B3SourceA024:
 .byte $ed
B3SourceA025:
 .byte $04
B3SourceA026:
 .byte $8d
B3SourceA027:
 .byte $e7
B3SourceA028:
 .byte $04
B3SourceA029:
 .byte $8d
B3SourceA02A:
 .byte $15
B3SourceA02B:
 .byte $40
B3SourceA02C:
 .byte $a9
B3SourceA02D:
 .byte $0f
B3SourceA02E:
 .byte $8d
B3SourceA02F:
 .byte $15
B3SourceA030:
 .byte $40
B3SourceA031:
 .byte $d0
B3SourceA032:
 .byte $45
B3SourceA033:
 .byte $a9
B3SourceA034:
 .byte $00
B3SourceA035:
 .byte $8d
B3SourceA036:
 .byte $15
B3SourceA037:
 .byte $40
B3SourceA038:
 .byte $8d
B3SourceA039:
 .byte $e1
B3SourceA03A:
 .byte $04
B3SourceA03B:
 .byte $8d
B3SourceA03C:
 .byte $e2
B3SourceA03D:
 .byte $04
B3SourceA03E:
 .byte $8d
B3SourceA03F:
 .byte $e3
B3SourceA040:
 .byte $04
B3SourceA041:
 .byte $a9
B3SourceA042:
 .byte $0f
B3SourceA043:
 .byte $8d
B3SourceA044:
 .byte $15
B3SourceA045:
 .byte $40
B3SourceA046:
 .byte $a9
B3SourceA047:
 .byte $2a
B3SourceA048:
 .byte $8d
B3SourceA049:
 .byte $e0
B3SourceA04A:
 .byte $04
B3SourceA04B:
 .byte $a9
B3SourceA04C:
 .byte $68
B3SourceA04D:
 .byte $d0
B3SourceA04E:
 .byte $11
B3SourceA04F:
 .byte $ad
B3SourceA050:
 .byte $e0
B3SourceA051:
 .byte $04
B3SourceA052:
 .byte $c9
B3SourceA053:
 .byte $24
B3SourceA054:
 .byte $f0
B3SourceA055:
 .byte $08
B3SourceA056:
 .byte $c9
B3SourceA057:
 .byte $1e
B3SourceA058:
 .byte $f0
B3SourceA059:
 .byte $f1
B3SourceA05A:
 .byte $c9
B3SourceA05B:
 .byte $18
B3SourceA05C:
 .byte $d0
B3SourceA05D:
 .byte $09
B3SourceA05E:
 .byte $a9
B3SourceA05F:
 .byte $60
B3SourceA060:
 .byte $a2
B3SourceA061:
 .byte $84
B3SourceA062:
 .byte $a0
B3SourceA063:
 .byte $7f
B3SourceA064:
 .byte $20
B3SourceA065:
 .byte $b9
B3SourceA066:
 .byte $e7
B3SourceA067:
 .byte $ce
B3SourceA068:
 .byte $e0
B3SourceA069:
 .byte $04
B3SourceA06A:
 .byte $d0
B3SourceA06B:
 .byte $23
B3SourceA06C:
 .byte $a9
B3SourceA06D:
 .byte $00
B3SourceA06E:
 .byte $8d
B3SourceA06F:
 .byte $15
B3SourceA070:
 .byte $40
B3SourceA071:
 .byte $a9
B3SourceA072:
 .byte $00
B3SourceA073:
 .byte $8d
B3SourceA074:
 .byte $e7
B3SourceA075:
 .byte $04
B3SourceA076:
 .byte $f0
B3SourceA077:
 .byte $17
B3SourceA078:
 JSR ::B3SourceA661
B3SourceA07B:
 JSR ::B3SourceA2AB
B3SourceA07E:
 JSR ::B3SourceA449
B3SourceA081:
 JSR ::B3SourceA0A1
B3SourceA084:
 JSR ::B3SourceE34F
B3SourceA087:
 LDA #$00
B3SourceA089:
 STA B3SourceImage+$25
B3SourceA08C:
 STA B3SourceImage+$24
B3SourceA08F:
 LDA #$00
B3SourceA091:
 STA B3SourceImage+$21
B3SourceA094:
 STA B3SourceImage+$22
B3SourceA097:
 STA B3SourceImage+$23
B3SourceA09A:
 STA B3SourceImage+$26
B3SourceA09D:
 STA B3SourceImage+$27
B3SourceA0A0:
 RTS
B3SourceA0A1:
 LDA B3SourceImage+$26
B3SourceA0A4:
 jne ::B3SourceA0AC
B3SourceA0A6:
 LDA B3SourceImage+$16
B3SourceA0A9:
 jne ::B3SourceA0E0
B3SourceA0AB:
 RTS
B3SourceA0AC:
 .byte $c9
B3SourceA0AD:
 .byte $04
B3SourceA0AE:
 .byte $d0
B3SourceA0AF:
 .byte $0d
B3SourceA0B0:
 .byte $a2
B3SourceA0B1:
 .byte $00
B3SourceA0B2:
 .byte $8e
B3SourceA0B3:
 .byte $e5
B3SourceA0B4:
 .byte $04
B3SourceA0B5:
 .byte $8e
B3SourceA0B6:
 .byte $15
B3SourceA0B7:
 .byte $40
B3SourceA0B8:
 .byte $a2
B3SourceA0B9:
 .byte $0f
B3SourceA0BA:
 .byte $8e
B3SourceA0BB:
 .byte $15
B3SourceA0BC:
 .byte $40
B3SourceA0BD:
 .byte $8d
B3SourceA0BE:
 .byte $e6
B3SourceA0BF:
 .byte $04
B3SourceA0C0:
 .byte $a0
B3SourceA0C1:
 .byte $00
B3SourceA0C2:
 .byte $8c
B3SourceA0C3:
 .byte $ff
B3SourceA0C4:
 .byte $07
B3SourceA0C5:
 .byte $c8
B3SourceA0C6:
 .byte $4a
B3SourceA0C7:
 .byte $90
B3SourceA0C8:
 .byte $fc
B3SourceA0C9:
 .byte $b9
B3SourceA0CA:
 .byte $ae
B3SourceA0CB:
 .byte $a1
B3SourceA0CC:
 .byte $a8
B3SourceA0CD:
 .byte $b9
B3SourceA0CE:
 .byte $af
B3SourceA0CF:
 .byte $a1
B3SourceA0D0:
 .byte $85
B3SourceA0D1:
 .byte $73
B3SourceA0D2:
 .byte $b9
B3SourceA0D3:
 .byte $b0
B3SourceA0D4:
 .byte $a1
B3SourceA0D5:
 .byte $8d
B3SourceA0D6:
 .byte $fe
B3SourceA0D7:
 .byte $07
B3SourceA0D8:
 .byte $a9
B3SourceA0D9:
 .byte $01
B3SourceA0DA:
 .byte $8d
B3SourceA0DB:
 .byte $fd
B3SourceA0DC:
 .byte $07
B3SourceA0DD:
 .byte $8d
B3SourceA0DE:
 .byte $fb
B3SourceA0DF:
 .byte $07
B3SourceA0E0:
 .byte $ce
B3SourceA0E1:
 .byte $fd
B3SourceA0E2:
 .byte $07
B3SourceA0E3:
 .byte $d0
B3SourceA0E4:
 .byte $51
B3SourceA0E5:
 .byte $a4
B3SourceA0E6:
 .byte $73
B3SourceA0E7:
 .byte $e6
B3SourceA0E8:
 .byte $73
B3SourceA0E9:
 .byte $b9
B3SourceA0EA:
 .byte $c5
B3SourceA0EB:
 .byte $a1
B3SourceA0EC:
 .byte $f0
B3SourceA0ED:
 .byte $04
B3SourceA0EE:
 .byte $10
B3SourceA0EF:
 .byte $1f
B3SourceA0F0:
 .byte $d0
B3SourceA0F1:
 .byte $10
B3SourceA0F2:
 .byte $a9
B3SourceA0F3:
 .byte $08
B3SourceA0F4:
 .byte $8d
B3SourceA0F5:
 .byte $15
B3SourceA0F6:
 .byte $40
B3SourceA0F7:
 .byte $a9
B3SourceA0F8:
 .byte $0f
B3SourceA0F9:
 .byte $8d
B3SourceA0FA:
 .byte $15
B3SourceA0FB:
 .byte $40
B3SourceA0FC:
 .byte $a9
B3SourceA0FD:
 .byte $00
B3SourceA0FE:
 .byte $8d
B3SourceA0FF:
 .byte $e6
B3SourceA100:
 .byte $04
B3SourceA101:
 .byte $60
B3SourceA102:
 .byte $20
B3SourceA103:
 .byte $ac
B3SourceA104:
 .byte $a1
B3SourceA105:
 .byte $8d
B3SourceA106:
 .byte $fc
B3SourceA107:
 .byte $07
B3SourceA108:
 .byte $a4
B3SourceA109:
 .byte $73
B3SourceA10A:
 .byte $e6
B3SourceA10B:
 .byte $73
B3SourceA10C:
 .byte $b9
B3SourceA10D:
 .byte $c5
B3SourceA10E:
 .byte $a1
B3SourceA10F:
 .byte $8d
B3SourceA110:
 .byte $02
B3SourceA111:
 .byte $40
B3SourceA112:
 .byte $ad
B3SourceA113:
 .byte $e6
B3SourceA114:
 .byte $04
B3SourceA115:
 .byte $10
B3SourceA116:
 .byte $09
B3SourceA117:
 .byte $a9
B3SourceA118:
 .byte $0e
B3SourceA119:
 .byte $8d
B3SourceA11A:
 .byte $03
B3SourceA11B:
 .byte $40
B3SourceA11C:
 .byte $a2
B3SourceA11D:
 .byte $9f
B3SourceA11E:
 .byte $d0
B3SourceA11F:
 .byte $07
B3SourceA120:
 .byte $a9
B3SourceA121:
 .byte $08
B3SourceA122:
 .byte $8d
B3SourceA123:
 .byte $03
B3SourceA124:
 .byte $40
B3SourceA125:
 .byte $a2
B3SourceA126:
 .byte $97
B3SourceA127:
 .byte $a0
B3SourceA128:
 .byte $7f
B3SourceA129:
 .byte $20
B3SourceA12A:
 .byte $ab
B3SourceA12B:
 .byte $e7
B3SourceA12C:
 .byte $ad
B3SourceA12D:
 .byte $fc
B3SourceA12E:
 .byte $07
B3SourceA12F:
 .byte $8d
B3SourceA130:
 .byte $fd
B3SourceA131:
 .byte $07
B3SourceA132:
 .byte $a9
B3SourceA133:
 .byte $00
B3SourceA134:
 .byte $85
B3SourceA135:
 .byte $6f
B3SourceA136:
 .byte $ad
B3SourceA137:
 .byte $e6
B3SourceA138:
 .byte $04
B3SourceA139:
 .byte $c9
B3SourceA13A:
 .byte $04
B3SourceA13B:
 .byte $d0
B3SourceA13C:
 .byte $0a
B3SourceA13D:
 .byte $e6
B3SourceA13E:
 .byte $6f
B3SourceA13F:
 .byte $a4
B3SourceA140:
 .byte $6f
B3SourceA141:
 .byte $b9
B3SourceA142:
 .byte $9b
B3SourceA143:
 .byte $a1
B3SourceA144:
 .byte $8d
B3SourceA145:
 .byte $00
B3SourceA146:
 .byte $40
B3SourceA147:
 .byte $ac
B3SourceA148:
 .byte $fe
B3SourceA149:
 .byte $07
B3SourceA14A:
 .byte $f0
B3SourceA14B:
 .byte $4f
B3SourceA14C:
 .byte $ce
B3SourceA14D:
 .byte $fb
B3SourceA14E:
 .byte $07
B3SourceA14F:
 .byte $d0
B3SourceA150:
 .byte $3e
B3SourceA151:
 .byte $ac
B3SourceA152:
 .byte $fe
B3SourceA153:
 .byte $07
B3SourceA154:
 .byte $ee
B3SourceA155:
 .byte $fe
B3SourceA156:
 .byte $07
B3SourceA157:
 .byte $b9
B3SourceA158:
 .byte $c5
B3SourceA159:
 .byte $a1
B3SourceA15A:
 .byte $10
B3SourceA15B:
 .byte $0f
B3SourceA15C:
 .byte $20
B3SourceA15D:
 .byte $ac
B3SourceA15E:
 .byte $a1
B3SourceA15F:
 .byte $8d
B3SourceA160:
 .byte $fa
B3SourceA161:
 .byte $07
B3SourceA162:
 .byte $ac
B3SourceA163:
 .byte $fe
B3SourceA164:
 .byte $07
B3SourceA165:
 .byte $ee
B3SourceA166:
 .byte $fe
B3SourceA167:
 .byte $07
B3SourceA168:
 .byte $b9
B3SourceA169:
 .byte $c5
B3SourceA16A:
 .byte $a1
B3SourceA16B:
 .byte $c9
B3SourceA16C:
 .byte $7e
B3SourceA16D:
 .byte $d0
B3SourceA16E:
 .byte $07
B3SourceA16F:
 .byte $a9
B3SourceA170:
 .byte $10
B3SourceA171:
 .byte $8d
B3SourceA172:
 .byte $04
B3SourceA173:
 .byte $40
B3SourceA174:
 .byte $d0
B3SourceA175:
 .byte $0f
B3SourceA176:
 .byte $8d
B3SourceA177:
 .byte $06
B3SourceA178:
 .byte $40
B3SourceA179:
 .byte $a2
B3SourceA17A:
 .byte $08
B3SourceA17B:
 .byte $8e
B3SourceA17C:
 .byte $07
B3SourceA17D:
 .byte $40
B3SourceA17E:
 .byte $a2
B3SourceA17F:
 .byte $55
B3SourceA180:
 .byte $a0
B3SourceA181:
 .byte $7f
B3SourceA182:
 .byte $20
B3SourceA183:
 .byte $b2
B3SourceA184:
 .byte $e7
B3SourceA185:
 .byte $ad
B3SourceA186:
 .byte $fa
B3SourceA187:
 .byte $07
B3SourceA188:
 .byte $8d
B3SourceA189:
 .byte $fb
B3SourceA18A:
 .byte $07
B3SourceA18B:
 .byte $a9
B3SourceA18C:
 .byte $00
B3SourceA18D:
 .byte $85
B3SourceA18E:
 .byte $70
B3SourceA18F:
 .byte $e6
B3SourceA190:
 .byte $70
B3SourceA191:
 .byte $a4
B3SourceA192:
 .byte $70
B3SourceA193:
 .byte $b9
B3SourceA194:
 .byte $9b
B3SourceA195:
 .byte $a1
B3SourceA196:
 .byte $09
B3SourceA197:
 .byte $50
B3SourceA198:
 .byte $8d
B3SourceA199:
 .byte $04
B3SourceA19A:
 .byte $40
B3SourceA19B:
 .byte $60
B3SourceA19C:
 .byte $97
B3SourceA19D:
 .byte $96
B3SourceA19E:
 .byte $96
B3SourceA19F:
 .byte $95
B3SourceA1A0:
 .byte $95
B3SourceA1A1:
 .byte $95
B3SourceA1A2:
 .byte $94
B3SourceA1A3:
 .byte $94
B3SourceA1A4:
 .byte $94
B3SourceA1A5:
 .byte $93
B3SourceA1A6:
 .byte $93
B3SourceA1A7:
 .byte $92
B3SourceA1A8:
 .byte $92
B3SourceA1A9:
 .byte $91
B3SourceA1AA:
 .byte $91
B3SourceA1AB:
 .byte $91
B3SourceA1AC:
 .byte $29
B3SourceA1AD:
 .byte $7f
B3SourceA1AE:
 .byte $60
B3SourceA1AF:
 .byte $08
B3SourceA1B0:
 .byte $0a
B3SourceA1B1:
 .byte $0c
B3SourceA1B2:
 .byte $0e
B3SourceA1B3:
 .byte $10
B3SourceA1B4:
 .byte $14
B3SourceA1B5:
 .byte $14
B3SourceA1B6:
 .byte $12
B3SourceA1B7:
 .byte $00
B3SourceA1B8:
 .byte $00
B3SourceA1B9:
 .byte $37
B3SourceA1BA:
 .byte $00
B3SourceA1BB:
 .byte $11
B3SourceA1BC:
 .byte $20
B3SourceA1BD:
 .byte $31
B3SourceA1BE:
 .byte $00
B3SourceA1BF:
 .byte $3c
B3SourceA1C0:
 .byte $00
B3SourceA1C1:
 .byte $44
B3SourceA1C2:
 .byte $00
B3SourceA1C3:
 .byte $10
B3SourceA1C4:
 .byte $00
B3SourceA1C5:
 .byte $83
B3SourceA1C6:
 .byte $35
B3SourceA1C7:
 .byte $32
B3SourceA1C8:
 .byte $2f
B3SourceA1C9:
 .byte $2c
B3SourceA1CA:
 .byte $2a
B3SourceA1CB:
 .byte $28
B3SourceA1CC:
 .byte $25
B3SourceA1CD:
 .byte $23
B3SourceA1CE:
 .byte $21
B3SourceA1CF:
 .byte $1f
B3SourceA1D0:
 .byte $1d
B3SourceA1D1:
 .byte $1c
B3SourceA1D2:
 .byte $1a
B3SourceA1D3:
 .byte $18
B3SourceA1D4:
 .byte $16
B3SourceA1D5:
 .byte $00
B3SourceA1D6:
 .byte $84
B3SourceA1D7:
 .byte $12
B3SourceA1D8:
 .byte $15
B3SourceA1D9:
 .byte $19
B3SourceA1DA:
 .byte $1f
B3SourceA1DB:
 .byte $23
B3SourceA1DC:
 .byte $2a
B3SourceA1DD:
 .byte $32
B3SourceA1DE:
 .byte $3f
B3SourceA1DF:
 .byte $47
B3SourceA1E0:
 .byte $54
B3SourceA1E1:
 .byte $64
B3SourceA1E2:
 .byte $8a
B3SourceA1E3:
 .byte $7f
B3SourceA1E4:
 .byte $00
B3SourceA1E5:
 .byte $82
B3SourceA1E6:
 .byte $7e
B3SourceA1E7:
 .byte $84
B3SourceA1E8:
 .byte $12
B3SourceA1E9:
 .byte $15
B3SourceA1EA:
 .byte $19
B3SourceA1EB:
 .byte $1f
B3SourceA1EC:
 .byte $23
B3SourceA1ED:
 .byte $2a
B3SourceA1EE:
 .byte $32
B3SourceA1EF:
 .byte $3f
B3SourceA1F0:
 .byte $47
B3SourceA1F1:
 .byte $54
B3SourceA1F2:
 .byte $64
B3SourceA1F3:
 .byte $8a
B3SourceA1F4:
 .byte $7f
B3SourceA1F5:
 .byte $00
B3SourceA1F6:
 .byte $85
B3SourceA1F7:
 .byte $6a
B3SourceA1F8:
 .byte $5f
B3SourceA1F9:
 .byte $87
B3SourceA1FA:
 .byte $47
B3SourceA1FB:
 .byte $00
B3SourceA1FC:
 .byte $85
B3SourceA1FD:
 .byte $2a
B3SourceA1FE:
 .byte $8a
B3SourceA1FF:
 .byte $23
B3SourceA200:
 .byte $00
B3SourceA201:
 .byte $85
B3SourceA202:
 .byte $54
B3SourceA203:
 .byte $47
B3SourceA204:
 .byte $3f
B3SourceA205:
 .byte $35
B3SourceA206:
 .byte $8a
B3SourceA207:
 .byte $2a
B3SourceA208:
 .byte $00
B3SourceA209:
 .byte $88
B3SourceA20A:
 .byte $14
B3SourceA20B:
 .byte $14
B3SourceA20C:
 .byte $8a
B3SourceA20D:
 .byte $14
B3SourceA20E:
 .byte $00
B3SourceA20F:
 .byte $9f
B3SourceA210:
 .byte $9b
B3SourceA211:
 .byte $98
B3SourceA212:
 .byte $96
B3SourceA213:
 .byte $95
B3SourceA214:
 .byte $94
B3SourceA215:
 .byte $92
B3SourceA216:
 .byte $90
B3SourceA217:
 .byte $90
B3SourceA218:
 .byte $9a
B3SourceA219:
 .byte $97
B3SourceA21A:
 .byte $95
B3SourceA21B:
 .byte $93
B3SourceA21C:
 .byte $92
B3SourceA21D:
 .byte $8c
B3SourceA21E:
 .byte $e1
B3SourceA21F:
 .byte $04
B3SourceA220:
 .byte $a9
B3SourceA221:
 .byte $08
B3SourceA222:
 .byte $8d
B3SourceA223:
 .byte $e0
B3SourceA224:
 .byte $04
B3SourceA225:
 .byte $d0
B3SourceA226:
 .byte $08
B3SourceA227:
 .byte $4e
B3SourceA228:
 .byte $f1
B3SourceA229:
 .byte $04
B3SourceA22A:
 .byte $b0
B3SourceA22B:
 .byte $03
B3SourceA22C:
 .byte $4c
B3SourceA22D:
 .byte $54
B3SourceA22E:
 .byte $a3
B3SourceA22F:
 .byte $ce
B3SourceA230:
 .byte $e0
B3SourceA231:
 .byte $04
B3SourceA232:
 .byte $ad
B3SourceA233:
 .byte $e0
B3SourceA234:
 .byte $04
B3SourceA235:
 .byte $f0
B3SourceA236:
 .byte $08
B3SourceA237:
 .byte $c9
B3SourceA238:
 .byte $04
B3SourceA239:
 .byte $d0
B3SourceA23A:
 .byte $12
B3SourceA23B:
 .byte $a9
B3SourceA23C:
 .byte $6e
B3SourceA23D:
 .byte $d0
B3SourceA23E:
 .byte $07
B3SourceA23F:
 .byte $a9
B3SourceA240:
 .byte $08
B3SourceA241:
 .byte $8d
B3SourceA242:
 .byte $e0
B3SourceA243:
 .byte $04
B3SourceA244:
 .byte $a9
B3SourceA245:
 .byte $72
B3SourceA246:
 .byte $a2
B3SourceA247:
 .byte $b4
B3SourceA248:
 .byte $a0
B3SourceA249:
 .byte $7f
B3SourceA24A:
 .byte $20
B3SourceA24B:
 .byte $b9
B3SourceA24C:
 .byte $e7
B3SourceA24D:
 .byte $60
B3SourceA24E:
 .byte $8c
B3SourceA24F:
 .byte $e1
B3SourceA250:
 .byte $04
B3SourceA251:
 .byte $a9
B3SourceA252:
 .byte $42
B3SourceA253:
 .byte $d0
B3SourceA254:
 .byte $05
B3SourceA255:
 .byte $8c
B3SourceA256:
 .byte $e1
B3SourceA257:
 .byte $04
B3SourceA258:
 .byte $a9
B3SourceA259:
 .byte $34
B3SourceA25A:
 .byte $a2
B3SourceA25B:
 .byte $82
B3SourceA25C:
 .byte $a0
B3SourceA25D:
 .byte $a7
B3SourceA25E:
 .byte $20
B3SourceA25F:
 .byte $b9
B3SourceA260:
 .byte $e7
B3SourceA261:
 .byte $a9
B3SourceA262:
 .byte $28
B3SourceA263:
 .byte $8d
B3SourceA264:
 .byte $e0
B3SourceA265:
 .byte $04
B3SourceA266:
 .byte $ad
B3SourceA267:
 .byte $e0
B3SourceA268:
 .byte $04
B3SourceA269:
 .byte $c9
B3SourceA26A:
 .byte $25
B3SourceA26B:
 .byte $d0
B3SourceA26C:
 .byte $06
B3SourceA26D:
 .byte $a2
B3SourceA26E:
 .byte $5f
B3SourceA26F:
 .byte $a0
B3SourceA270:
 .byte $f6
B3SourceA271:
 .byte $d0
B3SourceA272:
 .byte $08
B3SourceA273:
 .byte $c9
B3SourceA274:
 .byte $20
B3SourceA275:
 .byte $d0
B3SourceA276:
 .byte $2f
B3SourceA277:
 .byte $a2
B3SourceA278:
 .byte $48
B3SourceA279:
 .byte $a0
B3SourceA27A:
 .byte $bc
B3SourceA27B:
 .byte $20
B3SourceA27C:
 .byte $ab
B3SourceA27D:
 .byte $e7
B3SourceA27E:
 .byte $d0
B3SourceA27F:
 .byte $26
B3SourceA280:
 .byte $8c
B3SourceA281:
 .byte $e1
B3SourceA282:
 .byte $04
B3SourceA283:
 .byte $a9
B3SourceA284:
 .byte $05
B3SourceA285:
 .byte $a0
B3SourceA286:
 .byte $99
B3SourceA287:
 .byte $d0
B3SourceA288:
 .byte $07
B3SourceA289:
 .byte $8c
B3SourceA28A:
 .byte $e1
B3SourceA28B:
 .byte $04
B3SourceA28C:
 .byte $a9
B3SourceA28D:
 .byte $0a
B3SourceA28E:
 .byte $a0
B3SourceA28F:
 .byte $93
B3SourceA290:
 .byte $a2
B3SourceA291:
 .byte $9e
B3SourceA292:
 .byte $8d
B3SourceA293:
 .byte $e0
B3SourceA294:
 .byte $04
B3SourceA295:
 .byte $a9
B3SourceA296:
 .byte $26
B3SourceA297:
 .byte $20
B3SourceA298:
 .byte $b9
B3SourceA299:
 .byte $e7
B3SourceA29A:
 .byte $ad
B3SourceA29B:
 .byte $e0
B3SourceA29C:
 .byte $04
B3SourceA29D:
 .byte $c9
B3SourceA29E:
 .byte $06
B3SourceA29F:
 .byte $d0
B3SourceA2A0:
 .byte $05
B3SourceA2A1:
 .byte $a9
B3SourceA2A2:
 .byte $bb
B3SourceA2A3:
 .byte $8d
B3SourceA2A4:
 .byte $01
B3SourceA2A5:
 .byte $40
B3SourceA2A6:
 .byte $d0
B3SourceA2A7:
 .byte $7d
B3SourceA2A8:
 .byte $4c
B3SourceA2A9:
 .byte $27
B3SourceA2AA:
 .byte $a2
B3SourceA2AB:
 LDY B3SourceImage+$21
B3SourceA2AE:
 jeq ::B3SourceA2D0
B3SourceA2B0:
 .byte $30
B3SourceA2B1:
 .byte $9c
B3SourceA2B2:
 .byte $4e
B3SourceA2B3:
 .byte $f1
B3SourceA2B4:
 .byte $04
B3SourceA2B5:
 .byte $b0
B3SourceA2B6:
 .byte $9e
B3SourceA2B7:
 .byte $4e
B3SourceA2B8:
 .byte $f1
B3SourceA2B9:
 .byte $04
B3SourceA2BA:
 .byte $b0
B3SourceA2BB:
 .byte $cd
B3SourceA2BC:
 .byte $4e
B3SourceA2BD:
 .byte $f1
B3SourceA2BE:
 .byte $04
B3SourceA2BF:
 .byte $b0
B3SourceA2C0:
 .byte $41
B3SourceA2C1:
 .byte $4e
B3SourceA2C2:
 .byte $f1
B3SourceA2C3:
 .byte $04
B3SourceA2C4:
 .byte $b0
B3SourceA2C5:
 .byte $61
B3SourceA2C6:
 .byte $4e
B3SourceA2C7:
 .byte $f1
B3SourceA2C8:
 .byte $04
B3SourceA2C9:
 .byte $b0
B3SourceA2CA:
 .byte $2b
B3SourceA2CB:
 .byte $4e
B3SourceA2CC:
 .byte $f1
B3SourceA2CD:
 .byte $04
B3SourceA2CE:
 .byte $b0
B3SourceA2CF:
 .byte $b0
B3SourceA2D0:
 LDA B3SourceImage+$11
B3SourceA2D3:
 jeq ::B3SourceA2E9
B3SourceA2D5:
 .byte $30
B3SourceA2D6:
 .byte $8f
B3SourceA2D7:
 .byte $4a
B3SourceA2D8:
 .byte $b0
B3SourceA2D9:
 .byte $25
B3SourceA2DA:
 .byte $4a
B3SourceA2DB:
 .byte $b0
B3SourceA2DC:
 .byte $bd
B3SourceA2DD:
 .byte $4a
B3SourceA2DE:
 .byte $b0
B3SourceA2DF:
 .byte $33
B3SourceA2E0:
 .byte $4a
B3SourceA2E1:
 .byte $b0
B3SourceA2E2:
 .byte $57
B3SourceA2E3:
 .byte $4a
B3SourceA2E4:
 .byte $b0
B3SourceA2E5:
 .byte $13
B3SourceA2E6:
 .byte $4a
B3SourceA2E7:
 .byte $b0
B3SourceA2E8:
 .byte $b1
B3SourceA2E9:
 LDA B3SourceImage+$11
B3SourceA2EC:
 CMP #$40
B3SourceA2EE:
 jeq ::B3SourceA2A8
B3SourceA2F0:
 LSR B3SourceImage+$21
B3SourceA2F3:
 jcs ::B3SourceA2FC
B3SourceA2F5:
 RTS
B3SourceA2F6:
 .byte $4c
B3SourceA2F7:
 .byte $64
B3SourceA2F8:
 .byte $a3
B3SourceA2F9:
 .byte $4c
B3SourceA2FA:
 .byte $6c
B3SourceA2FB:
 .byte $a3
B3SourceA2FC:
 .byte $4c
B3SourceA2FD:
 .byte $1d
B3SourceA2FE:
 .byte $a2
B3SourceA2FF:
 .byte $4c
B3SourceA300:
 .byte $66
B3SourceA301:
 .byte $a2
B3SourceA302:
 .byte $8c
B3SourceA303:
 .byte $e1
B3SourceA304:
 .byte $04
B3SourceA305:
 .byte $a9
B3SourceA306:
 .byte $0e
B3SourceA307:
 .byte $8d
B3SourceA308:
 .byte $e0
B3SourceA309:
 .byte $04
B3SourceA30A:
 .byte $a0
B3SourceA30B:
 .byte $9c
B3SourceA30C:
 .byte $a2
B3SourceA30D:
 .byte $9e
B3SourceA30E:
 .byte $a9
B3SourceA30F:
 .byte $42
B3SourceA310:
 .byte $20
B3SourceA311:
 .byte $b9
B3SourceA312:
 .byte $e7
B3SourceA313:
 .byte $ac
B3SourceA314:
 .byte $e0
B3SourceA315:
 .byte $04
B3SourceA316:
 .byte $b9
B3SourceA317:
 .byte $0e
B3SourceA318:
 .byte $a2
B3SourceA319:
 .byte $8d
B3SourceA31A:
 .byte $00
B3SourceA31B:
 .byte $40
B3SourceA31C:
 .byte $c0
B3SourceA31D:
 .byte $06
B3SourceA31E:
 .byte $d0
B3SourceA31F:
 .byte $05
B3SourceA320:
 .byte $a9
B3SourceA321:
 .byte $9e
B3SourceA322:
 .byte $8d
B3SourceA323:
 .byte $02
B3SourceA324:
 .byte $40
B3SourceA325:
 .byte $d0
B3SourceA326:
 .byte $28
B3SourceA327:
 .byte $8c
B3SourceA328:
 .byte $e1
B3SourceA329:
 .byte $04
B3SourceA32A:
 .byte $a9
B3SourceA32B:
 .byte $0e
B3SourceA32C:
 .byte $a0
B3SourceA32D:
 .byte $cb
B3SourceA32E:
 .byte $a2
B3SourceA32F:
 .byte $9f
B3SourceA330:
 .byte $8d
B3SourceA331:
 .byte $e0
B3SourceA332:
 .byte $04
B3SourceA333:
 .byte $a9
B3SourceA334:
 .byte $44
B3SourceA335:
 .byte $20
B3SourceA336:
 .byte $b9
B3SourceA337:
 .byte $e7
B3SourceA338:
 .byte $d0
B3SourceA339:
 .byte $15
B3SourceA33A:
 .byte $ac
B3SourceA33B:
 .byte $e0
B3SourceA33C:
 .byte $04
B3SourceA33D:
 .byte $c0
B3SourceA33E:
 .byte $08
B3SourceA33F:
 .byte $d0
B3SourceA340:
 .byte $09
B3SourceA341:
 .byte $a9
B3SourceA342:
 .byte $a0
B3SourceA343:
 .byte $8d
B3SourceA344:
 .byte $02
B3SourceA345:
 .byte $40
B3SourceA346:
 .byte $a9
B3SourceA347:
 .byte $9f
B3SourceA348:
 .byte $d0
B3SourceA349:
 .byte $02
B3SourceA34A:
 .byte $a9
B3SourceA34B:
 .byte $90
B3SourceA34C:
 .byte $8d
B3SourceA34D:
 .byte $00
B3SourceA34E:
 .byte $40
B3SourceA34F:
 .byte $ce
B3SourceA350:
 .byte $e0
B3SourceA351:
 .byte $04
B3SourceA352:
 .byte $d0
B3SourceA353:
 .byte $0f
B3SourceA354:
 .byte $a2
B3SourceA355:
 .byte $00
B3SourceA356:
 .byte $8e
B3SourceA357:
 .byte $e1
B3SourceA358:
 .byte $04
B3SourceA359:
 .byte $a2
B3SourceA35A:
 .byte $1e
B3SourceA35B:
 .byte $8e
B3SourceA35C:
 .byte $15
B3SourceA35D:
 .byte $40
B3SourceA35E:
 .byte $a2
B3SourceA35F:
 .byte $0f
B3SourceA360:
 .byte $8e
B3SourceA361:
 .byte $15
B3SourceA362:
 .byte $40
B3SourceA363:
 .byte $60
B3SourceA364:
 .byte $8c
B3SourceA365:
 .byte $e1
B3SourceA366:
 .byte $04
B3SourceA367:
 .byte $a9
B3SourceA368:
 .byte $2f
B3SourceA369:
 .byte $8d
B3SourceA36A:
 .byte $e0
B3SourceA36B:
 .byte $04
B3SourceA36C:
 .byte $ad
B3SourceA36D:
 .byte $e0
B3SourceA36E:
 .byte $04
B3SourceA36F:
 .byte $4a
B3SourceA370:
 .byte $b0
B3SourceA371:
 .byte $10
B3SourceA372:
 .byte $4a
B3SourceA373:
 .byte $b0
B3SourceA374:
 .byte $0d
B3SourceA375:
 .byte $29
B3SourceA376:
 .byte $02
B3SourceA377:
 .byte $f0
B3SourceA378:
 .byte $09
B3SourceA379:
 .byte $a0
B3SourceA37A:
 .byte $91
B3SourceA37B:
 .byte $a2
B3SourceA37C:
 .byte $9a
B3SourceA37D:
 .byte $a9
B3SourceA37E:
 .byte $68
B3SourceA37F:
 .byte $20
B3SourceA380:
 .byte $b9
B3SourceA381:
 .byte $e7
B3SourceA382:
 .byte $4c
B3SourceA383:
 .byte $4f
B3SourceA384:
 .byte $a3
B3SourceA385:
 .byte $23
B3SourceA386:
 .byte $2f
B3SourceA387:
 .byte $35
B3SourceA388:
 .byte $2a
B3SourceA389:
 .byte $47
B3SourceA38A:
 .byte $54
B3SourceA38B:
 .byte $6a
B3SourceA38C:
 .byte $74
B3SourceA38D:
 .byte $6a
B3SourceA38E:
 .byte $64
B3SourceA38F:
 .byte $5c
B3SourceA390:
 .byte $52
B3SourceA391:
 .byte $5c
B3SourceA392:
 .byte $52
B3SourceA393:
 .byte $4c
B3SourceA394:
 .byte $44
B3SourceA395:
 .byte $66
B3SourceA396:
 .byte $70
B3SourceA397:
 .byte $66
B3SourceA398:
 .byte $60
B3SourceA399:
 .byte $58
B3SourceA39A:
 .byte $4e
B3SourceA39B:
 .byte $58
B3SourceA39C:
 .byte $4e
B3SourceA39D:
 .byte $48
B3SourceA39E:
 .byte $40
B3SourceA39F:
 .byte $56
B3SourceA3A0:
 .byte $60
B3SourceA3A1:
 .byte $56
B3SourceA3A2:
 .byte $50
B3SourceA3A3:
 .byte $48
B3SourceA3A4:
 .byte $3e
B3SourceA3A5:
 .byte $48
B3SourceA3A6:
 .byte $3e
B3SourceA3A7:
 .byte $38
B3SourceA3A8:
 .byte $30
B3SourceA3A9:
 .byte $30
B3SourceA3AA:
 .byte $7e
B3SourceA3AB:
 .byte $3e
B3SourceA3AC:
 .byte $40
B3SourceA3AD:
 .byte $32
B3SourceA3AE:
 .byte $7e
B3SourceA3AF:
 .byte $40
B3SourceA3B0:
 .byte $42
B3SourceA3B1:
 .byte $34
B3SourceA3B2:
 .byte $7e
B3SourceA3B3:
 .byte $42
B3SourceA3B4:
 .byte $44
B3SourceA3B5:
 .byte $36
B3SourceA3B6:
 .byte $7e
B3SourceA3B7:
 .byte $44
B3SourceA3B8:
 .byte $46
B3SourceA3B9:
 .byte $38
B3SourceA3BA:
 .byte $7e
B3SourceA3BB:
 .byte $46
B3SourceA3BC:
 .byte $48
B3SourceA3BD:
 .byte $3a
B3SourceA3BE:
 .byte $7e
B3SourceA3BF:
 .byte $48
B3SourceA3C0:
 .byte $4a
B3SourceA3C1:
 .byte $3c
B3SourceA3C2:
 .byte $7e
B3SourceA3C3:
 .byte $4a
B3SourceA3C4:
 .byte $4c
B3SourceA3C5:
 .byte $3e
B3SourceA3C6:
 .byte $7e
B3SourceA3C7:
 .byte $4c
B3SourceA3C8:
 .byte $4e
B3SourceA3C9:
 .byte $8c
B3SourceA3CA:
 .byte $e2
B3SourceA3CB:
 .byte $04
B3SourceA3CC:
 .byte $a9
B3SourceA3CD:
 .byte $35
B3SourceA3CE:
 .byte $a2
B3SourceA3CF:
 .byte $8d
B3SourceA3D0:
 .byte $d0
B3SourceA3D1:
 .byte $07
B3SourceA3D2:
 .byte $8c
B3SourceA3D3:
 .byte $e2
B3SourceA3D4:
 .byte $04
B3SourceA3D5:
 .byte $a9
B3SourceA3D6:
 .byte $06
B3SourceA3D7:
 .byte $a2
B3SourceA3D8:
 .byte $98
B3SourceA3D9:
 .byte $8d
B3SourceA3DA:
 .byte $e8
B3SourceA3DB:
 .byte $04
B3SourceA3DC:
 .byte $a0
B3SourceA3DD:
 .byte $7f
B3SourceA3DE:
 .byte $a9
B3SourceA3DF:
 .byte $5e
B3SourceA3E0:
 .byte $20
B3SourceA3E1:
 .byte $2b
B3SourceA3E2:
 .byte $e8
B3SourceA3E3:
 .byte $ad
B3SourceA3E4:
 .byte $e8
B3SourceA3E5:
 .byte $04
B3SourceA3E6:
 .byte $c9
B3SourceA3E7:
 .byte $30
B3SourceA3E8:
 .byte $d0
B3SourceA3E9:
 .byte $05
B3SourceA3EA:
 .byte $a9
B3SourceA3EB:
 .byte $54
B3SourceA3EC:
 .byte $8d
B3SourceA3ED:
 .byte $06
B3SourceA3EE:
 .byte $40
B3SourceA3EF:
 .byte $d0
B3SourceA3F0:
 .byte $37
B3SourceA3F1:
 .byte $8c
B3SourceA3F2:
 .byte $e2
B3SourceA3F3:
 .byte $04
B3SourceA3F4:
 .byte $a9
B3SourceA3F5:
 .byte $20
B3SourceA3F6:
 .byte $8d
B3SourceA3F7:
 .byte $e8
B3SourceA3F8:
 .byte $04
B3SourceA3F9:
 .byte $a0
B3SourceA3FA:
 .byte $94
B3SourceA3FB:
 .byte $a9
B3SourceA3FC:
 .byte $1c
B3SourceA3FD:
 .byte $d0
B3SourceA3FE:
 .byte $0d
B3SourceA3FF:
 .byte $ad
B3SourceA400:
 .byte $e8
B3SourceA401:
 .byte $04
B3SourceA402:
 .byte $c9
B3SourceA403:
 .byte $18
B3SourceA404:
 .byte $d0
B3SourceA405:
 .byte $22
B3SourceA406:
 .byte $a0
B3SourceA407:
 .byte $93
B3SourceA408:
 .byte $a9
B3SourceA409:
 .byte $34
B3SourceA40A:
 .byte $a2
B3SourceA40B:
 .byte $9f
B3SourceA40C:
 .byte $4c
B3SourceA40D:
 .byte $25
B3SourceA40E:
 .byte $a4
B3SourceA40F:
 .byte $8c
B3SourceA410:
 .byte $e2
B3SourceA411:
 .byte $04
B3SourceA412:
 .byte $a9
B3SourceA413:
 .byte $36
B3SourceA414:
 .byte $8d
B3SourceA415:
 .byte $e8
B3SourceA416:
 .byte $04
B3SourceA417:
 .byte $ad
B3SourceA418:
 .byte $e8
B3SourceA419:
 .byte $04
B3SourceA41A:
 .byte $4a
B3SourceA41B:
 .byte $b0
B3SourceA41C:
 .byte $0b
B3SourceA41D:
 .byte $a8
B3SourceA41E:
 .byte $b9
B3SourceA41F:
 .byte $8a
B3SourceA420:
 .byte $a3
B3SourceA421:
 .byte $a2
B3SourceA422:
 .byte $5d
B3SourceA423:
 .byte $a0
B3SourceA424:
 .byte $7f
B3SourceA425:
 .byte $20
B3SourceA426:
 .byte $2b
B3SourceA427:
 .byte $e8
B3SourceA428:
 .byte $ce
B3SourceA429:
 .byte $e8
B3SourceA42A:
 .byte $04
B3SourceA42B:
 .byte $d0
B3SourceA42C:
 .byte $0f
B3SourceA42D:
 .byte $a2
B3SourceA42E:
 .byte $00
B3SourceA42F:
 .byte $8e
B3SourceA430:
 .byte $e2
B3SourceA431:
 .byte $04
B3SourceA432:
 .byte $a2
B3SourceA433:
 .byte $0d
B3SourceA434:
 .byte $8e
B3SourceA435:
 .byte $15
B3SourceA436:
 .byte $40
B3SourceA437:
 .byte $a2
B3SourceA438:
 .byte $0f
B3SourceA439:
 .byte $8e
B3SourceA43A:
 .byte $15
B3SourceA43B:
 .byte $40
B3SourceA43C:
 .byte $60
B3SourceA43D:
 .byte $4c
B3SourceA43E:
 .byte $cf
B3SourceA43F:
 .byte $a4
B3SourceA440:
 .byte $4c
B3SourceA441:
 .byte $c9
B3SourceA442:
 .byte $a3
B3SourceA443:
 .byte $4c
B3SourceA444:
 .byte $d6
B3SourceA445:
 .byte $a4
B3SourceA446:
 .byte $4c
B3SourceA447:
 .byte $07
B3SourceA448:
 .byte $a5
B3SourceA449:
 LDA B3SourceImage+$12
B3SourceA44C:
 AND #$40
B3SourceA44E:
 jne ::B3SourceA4AE
B3SourceA450:
 LDY B3SourceImage+$22
B3SourceA453:
 jeq ::B3SourceA47A
B3SourceA455:
 .byte $30
B3SourceA456:
 .byte $ef
B3SourceA457:
 .byte $4e
B3SourceA458:
 .byte $f2
B3SourceA459:
 .byte $04
B3SourceA45A:
 .byte $b0
B3SourceA45B:
 .byte $e4
B3SourceA45C:
 .byte $4e
B3SourceA45D:
 .byte $f2
B3SourceA45E:
 .byte $04
B3SourceA45F:
 .byte $b0
B3SourceA460:
 .byte $dc
B3SourceA461:
 .byte $4e
B3SourceA462:
 .byte $f2
B3SourceA463:
 .byte $04
B3SourceA464:
 .byte $b0
B3SourceA465:
 .byte $dd
B3SourceA466:
 .byte $4e
B3SourceA467:
 .byte $f2
B3SourceA468:
 .byte $04
B3SourceA469:
 .byte $b0
B3SourceA46A:
 .byte $86
B3SourceA46B:
 .byte $4e
B3SourceA46C:
 .byte $f2
B3SourceA46D:
 .byte $04
B3SourceA46E:
 .byte $b0
B3SourceA46F:
 .byte $2a
B3SourceA470:
 .byte $4e
B3SourceA471:
 .byte $f2
B3SourceA472:
 .byte $04
B3SourceA473:
 .byte $b0
B3SourceA474:
 .byte $9a
B3SourceA475:
 .byte $4e
B3SourceA476:
 .byte $f2
B3SourceA477:
 .byte $04
B3SourceA478:
 .byte $b0
B3SourceA479:
 .byte $2c
B3SourceA47A:
 LDA B3SourceImage+$12
B3SourceA47D:
 jeq ::B3SourceA496
B3SourceA47F:
 .byte $30
B3SourceA480:
 .byte $16
B3SourceA481:
 .byte $4a
B3SourceA482:
 .byte $b0
B3SourceA483:
 .byte $19
B3SourceA484:
 .byte $4a
B3SourceA485:
 .byte $b0
B3SourceA486:
 .byte $61
B3SourceA487:
 .byte $4a
B3SourceA488:
 .byte $b0
B3SourceA489:
 .byte $5e
B3SourceA48A:
 .byte $4a
B3SourceA48B:
 .byte $b0
B3SourceA48C:
 .byte $13
B3SourceA48D:
 .byte $4a
B3SourceA48E:
 .byte $b0
B3SourceA48F:
 .byte $0d
B3SourceA490:
 .byte $4a
B3SourceA491:
 .byte $b0
B3SourceA492:
 .byte $84
B3SourceA493:
 .byte $4a
B3SourceA494:
 .byte $b0
B3SourceA495:
 .byte $18
B3SourceA496:
 RTS
B3SourceA497:
 .byte $4c
B3SourceA498:
 .byte $32
B3SourceA499:
 .byte $a5
B3SourceA49A:
 .byte $4c
B3SourceA49B:
 .byte $d2
B3SourceA49C:
 .byte $a3
B3SourceA49D:
 .byte $4c
B3SourceA49E:
 .byte $e3
B3SourceA49F:
 .byte $a3
B3SourceA4A0:
 .byte $4c
B3SourceA4A1:
 .byte $ff
B3SourceA4A2:
 .byte $a3
B3SourceA4A3:
 .byte $4c
B3SourceA4A4:
 .byte $28
B3SourceA4A5:
 .byte $a4
B3SourceA4A6:
 .byte $8c
B3SourceA4A7:
 .byte $e2
B3SourceA4A8:
 .byte $04
B3SourceA4A9:
 .byte $a9
B3SourceA4AA:
 .byte $30
B3SourceA4AB:
 .byte $8d
B3SourceA4AC:
 .byte $e8
B3SourceA4AD:
 .byte $04
B3SourceA4AE:
 .byte $ad
B3SourceA4AF:
 .byte $e8
B3SourceA4B0:
 .byte $04
B3SourceA4B1:
 .byte $a2
B3SourceA4B2:
 .byte $03
B3SourceA4B3:
 .byte $4a
B3SourceA4B4:
 .byte $b0
B3SourceA4B5:
 .byte $ed
B3SourceA4B6:
 .byte $ca
B3SourceA4B7:
 .byte $d0
B3SourceA4B8:
 .byte $fa
B3SourceA4B9:
 .byte $a8
B3SourceA4BA:
 .byte $b9
B3SourceA4BB:
 .byte $84
B3SourceA4BC:
 .byte $a3
B3SourceA4BD:
 .byte $8d
B3SourceA4BE:
 .byte $06
B3SourceA4BF:
 .byte $40
B3SourceA4C0:
 .byte $a2
B3SourceA4C1:
 .byte $82
B3SourceA4C2:
 .byte $a0
B3SourceA4C3:
 .byte $7f
B3SourceA4C4:
 .byte $20
B3SourceA4C5:
 .byte $b2
B3SourceA4C6:
 .byte $e7
B3SourceA4C7:
 .byte $a9
B3SourceA4C8:
 .byte $08
B3SourceA4C9:
 .byte $8d
B3SourceA4CA:
 .byte $07
B3SourceA4CB:
 .byte $40
B3SourceA4CC:
 .byte $4c
B3SourceA4CD:
 .byte $28
B3SourceA4CE:
 .byte $a4
B3SourceA4CF:
 .byte $8c
B3SourceA4D0:
 .byte $e2
B3SourceA4D1:
 .byte $04
B3SourceA4D2:
 .byte $a9
B3SourceA4D3:
 .byte $10
B3SourceA4D4:
 .byte $d0
B3SourceA4D5:
 .byte $05
B3SourceA4D6:
 .byte $8c
B3SourceA4D7:
 .byte $e2
B3SourceA4D8:
 .byte $04
B3SourceA4D9:
 .byte $a9
B3SourceA4DA:
 .byte $20
B3SourceA4DB:
 .byte $8d
B3SourceA4DC:
 .byte $e8
B3SourceA4DD:
 .byte $04
B3SourceA4DE:
 .byte $a9
B3SourceA4DF:
 .byte $7f
B3SourceA4E0:
 .byte $8d
B3SourceA4E1:
 .byte $05
B3SourceA4E2:
 .byte $40
B3SourceA4E3:
 .byte $a9
B3SourceA4E4:
 .byte $00
B3SourceA4E5:
 .byte $8d
B3SourceA4E6:
 .byte $e9
B3SourceA4E7:
 .byte $04
B3SourceA4E8:
 .byte $ee
B3SourceA4E9:
 .byte $e9
B3SourceA4EA:
 .byte $04
B3SourceA4EB:
 .byte $ad
B3SourceA4EC:
 .byte $e9
B3SourceA4ED:
 .byte $04
B3SourceA4EE:
 .byte $4a
B3SourceA4EF:
 .byte $a8
B3SourceA4F0:
 .byte $cc
B3SourceA4F1:
 .byte $e8
B3SourceA4F2:
 .byte $04
B3SourceA4F3:
 .byte $f0
B3SourceA4F4:
 .byte $0c
B3SourceA4F5:
 .byte $a9
B3SourceA4F6:
 .byte $9d
B3SourceA4F7:
 .byte $8d
B3SourceA4F8:
 .byte $04
B3SourceA4F9:
 .byte $40
B3SourceA4FA:
 .byte $b9
B3SourceA4FB:
 .byte $a9
B3SourceA4FC:
 .byte $a3
B3SourceA4FD:
 .byte $20
B3SourceA4FE:
 .byte $31
B3SourceA4FF:
 .byte $e8
B3SourceA500:
 .byte $60
B3SourceA501:
 .byte $4c
B3SourceA502:
 .byte $2d
B3SourceA503:
 .byte $a4
B3SourceA504:
 .byte $4c
B3SourceA505:
 .byte $7a
B3SourceA506:
 .byte $a4
B3SourceA507:
 .byte $ac
B3SourceA508:
 .byte $f2
B3SourceA509:
 .byte $04
B3SourceA50A:
 .byte $c0
B3SourceA50B:
 .byte $80
B3SourceA50C:
 .byte $d0
B3SourceA50D:
 .byte $04
B3SourceA50E:
 .byte $a9
B3SourceA50F:
 .byte $1f
B3SourceA510:
 .byte $d0
B3SourceA511:
 .byte $17
B3SourceA512:
 .byte $c0
B3SourceA513:
 .byte $90
B3SourceA514:
 .byte $d0
B3SourceA515:
 .byte $04
B3SourceA516:
 .byte $a9
B3SourceA517:
 .byte $00
B3SourceA518:
 .byte $f0
B3SourceA519:
 .byte $0f
B3SourceA51A:
 .byte $c0
B3SourceA51B:
 .byte $a0
B3SourceA51C:
 .byte $d0
B3SourceA51D:
 .byte $04
B3SourceA51E:
 .byte $a9
B3SourceA51F:
 .byte $57
B3SourceA520:
 .byte $d0
B3SourceA521:
 .byte $07
B3SourceA522:
 .byte $ad
B3SourceA523:
 .byte $e2
B3SourceA524:
 .byte $04
B3SourceA525:
 .byte $d0
B3SourceA526:
 .byte $dd
B3SourceA527:
 .byte $a9
B3SourceA528:
 .byte $6c
B3SourceA529:
 .byte $8d
B3SourceA52A:
 .byte $e8
B3SourceA52B:
 .byte $04
B3SourceA52C:
 .byte $98
B3SourceA52D:
 .byte $29
B3SourceA52E:
 .byte $b0
B3SourceA52F:
 .byte $8c
B3SourceA530:
 .byte $e2
B3SourceA531:
 .byte $04
B3SourceA532:
 .byte $ee
B3SourceA533:
 .byte $e8
B3SourceA534:
 .byte $04
B3SourceA535:
 .byte $ac
B3SourceA536:
 .byte $e8
B3SourceA537:
 .byte $04
B3SourceA538:
 .byte $b9
B3SourceA539:
 .byte $5b
B3SourceA53A:
 .byte $a5
B3SourceA53B:
 .byte $f0
B3SourceA53C:
 .byte $16
B3SourceA53D:
 .byte $10
B3SourceA53E:
 .byte $05
B3SourceA53F:
 .byte $8d
B3SourceA540:
 .byte $e9
B3SourceA541:
 .byte $04
B3SourceA542:
 .byte $d0
B3SourceA543:
 .byte $ee
B3SourceA544:
 .byte $a2
B3SourceA545:
 .byte $7f
B3SourceA546:
 .byte $8e
B3SourceA547:
 .byte $05
B3SourceA548:
 .byte $40
B3SourceA549:
 .byte $ae
B3SourceA54A:
 .byte $e9
B3SourceA54B:
 .byte $04
B3SourceA54C:
 .byte $8e
B3SourceA54D:
 .byte $04
B3SourceA54E:
 .byte $40
B3SourceA54F:
 .byte $20
B3SourceA550:
 .byte $31
B3SourceA551:
 .byte $e8
B3SourceA552:
 .byte $60
B3SourceA553:
 .byte $a9
B3SourceA554:
 .byte $00
B3SourceA555:
 .byte $8d
B3SourceA556:
 .byte $e8
B3SourceA557:
 .byte $04
B3SourceA558:
 .byte $4c
B3SourceA559:
 .byte $2d
B3SourceA55A:
 .byte $a4
B3SourceA55B:
 .byte $9f
B3SourceA55C:
 .byte $30
B3SourceA55D:
 .byte $34
B3SourceA55E:
 .byte $36
B3SourceA55F:
 .byte $38
B3SourceA560:
 .byte $9f
B3SourceA561:
 .byte $3a
B3SourceA562:
 .byte $3c
B3SourceA563:
 .byte $3e
B3SourceA564:
 .byte $40
B3SourceA565:
 .byte $9a
B3SourceA566:
 .byte $3a
B3SourceA567:
 .byte $3c
B3SourceA568:
 .byte $3e
B3SourceA569:
 .byte $40
B3SourceA56A:
 .byte $9c
B3SourceA56B:
 .byte $3a
B3SourceA56C:
 .byte $3c
B3SourceA56D:
 .byte $3e
B3SourceA56E:
 .byte $40
B3SourceA56F:
 .byte $96
B3SourceA570:
 .byte $3a
B3SourceA571:
 .byte $3c
B3SourceA572:
 .byte $3e
B3SourceA573:
 .byte $40
B3SourceA574:
 .byte $98
B3SourceA575:
 .byte $3a
B3SourceA576:
 .byte $3c
B3SourceA577:
 .byte $3e
B3SourceA578:
 .byte $40
B3SourceA579:
 .byte $00
B3SourceA57A:
 .byte $9f
B3SourceA57B:
 .byte $2e
B3SourceA57C:
 .byte $2a
B3SourceA57D:
 .byte $26
B3SourceA57E:
 .byte $22
B3SourceA57F:
 .byte $9d
B3SourceA580:
 .byte $2e
B3SourceA581:
 .byte $2a
B3SourceA582:
 .byte $7e
B3SourceA583:
 .byte $7e
B3SourceA584:
 .byte $9f
B3SourceA585:
 .byte $30
B3SourceA586:
 .byte $2e
B3SourceA587:
 .byte $2a
B3SourceA588:
 .byte $28
B3SourceA589:
 .byte $9d
B3SourceA58A:
 .byte $30
B3SourceA58B:
 .byte $2e
B3SourceA58C:
 .byte $7e
B3SourceA58D:
 .byte $7e
B3SourceA58E:
 .byte $9f
B3SourceA58F:
 .byte $38
B3SourceA590:
 .byte $34
B3SourceA591:
 .byte $32
B3SourceA592:
 .byte $30
B3SourceA593:
 .byte $9d
B3SourceA594:
 .byte $38
B3SourceA595:
 .byte $34
B3SourceA596:
 .byte $32
B3SourceA597:
 .byte $30
B3SourceA598:
 .byte $9a
B3SourceA599:
 .byte $38
B3SourceA59A:
 .byte $34
B3SourceA59B:
 .byte $32
B3SourceA59C:
 .byte $30
B3SourceA59D:
 .byte $9c
B3SourceA59E:
 .byte $38
B3SourceA59F:
 .byte $34
B3SourceA5A0:
 .byte $32
B3SourceA5A1:
 .byte $30
B3SourceA5A2:
 .byte $97
B3SourceA5A3:
 .byte $38
B3SourceA5A4:
 .byte $34
B3SourceA5A5:
 .byte $32
B3SourceA5A6:
 .byte $30
B3SourceA5A7:
 .byte $98
B3SourceA5A8:
 .byte $38
B3SourceA5A9:
 .byte $34
B3SourceA5AA:
 .byte $32
B3SourceA5AB:
 .byte $30
B3SourceA5AC:
 .byte $94
B3SourceA5AD:
 .byte $38
B3SourceA5AE:
 .byte $34
B3SourceA5AF:
 .byte $32
B3SourceA5B0:
 .byte $30
B3SourceA5B1:
 .byte $00
B3SourceA5B2:
 .byte $9f
B3SourceA5B3:
 .byte $42
B3SourceA5B4:
 .byte $40
B3SourceA5B5:
 .byte $7e
B3SourceA5B6:
 .byte $7e
B3SourceA5B7:
 .byte $9f
B3SourceA5B8:
 .byte $46
B3SourceA5B9:
 .byte $48
B3SourceA5BA:
 .byte $7e
B3SourceA5BB:
 .byte $7e
B3SourceA5BC:
 .byte $9a
B3SourceA5BD:
 .byte $4a
B3SourceA5BE:
 .byte $4e
B3SourceA5BF:
 .byte $50
B3SourceA5C0:
 .byte $52
B3SourceA5C1:
 .byte $96
B3SourceA5C2:
 .byte $4e
B3SourceA5C3:
 .byte $52
B3SourceA5C4:
 .byte $54
B3SourceA5C5:
 .byte $56
B3SourceA5C6:
 .byte $00
B3SourceA5C7:
 .byte $90
B3SourceA5C8:
 .byte $7e
B3SourceA5C9:
 .byte $7e
B3SourceA5CA:
 .byte $97
B3SourceA5CB:
 .byte $4c
B3SourceA5CC:
 .byte $4e
B3SourceA5CD:
 .byte $90
B3SourceA5CE:
 .byte $7e
B3SourceA5CF:
 .byte $7e
B3SourceA5D0:
 .byte $95
B3SourceA5D1:
 .byte $52
B3SourceA5D2:
 .byte $54
B3SourceA5D3:
 .byte $56
B3SourceA5D4:
 .byte $58
B3SourceA5D5:
 .byte $94
B3SourceA5D6:
 .byte $52
B3SourceA5D7:
 .byte $54
B3SourceA5D8:
 .byte $56
B3SourceA5D9:
 .byte $58
B3SourceA5DA:
 .byte $93
B3SourceA5DB:
 .byte $52
B3SourceA5DC:
 .byte $54
B3SourceA5DD:
 .byte $56
B3SourceA5DE:
 .byte $58
B3SourceA5DF:
 .byte $00
B3SourceA5E0:
 .byte $55
B3SourceA5E1:
 .byte $81
B3SourceA5E2:
 .byte $aa
B3SourceA5E3:
 .byte $02
B3SourceA5E4:
 .byte $74
B3SourceA5E5:
 .byte $b7
B3SourceA5E6:
 .byte $a5
B3SourceA5E7:
 .byte $04
B3SourceA5E8:
 .byte $92
B3SourceA5E9:
 .byte $a9
B3SourceA5EA:
 .byte $08
B3SourceA5EB:
 .byte $69
B3SourceA5EC:
 .byte $58
B3SourceA5ED:
 .byte $4a
B3SourceA5EE:
 .byte $11
B3SourceA5EF:
 .byte $61
B3SourceA5F0:
 .byte $21
B3SourceA5F1:
 .byte $51
B3SourceA5F2:
 .byte $81
B3SourceA5F3:
 .byte $21
B3SourceA5F4:
 .byte $61
B3SourceA5F5:
 .byte $a2
B3SourceA5F6:
 .byte $23
B3SourceA5F7:
 .byte $64
B3SourceA5F8:
 .byte $a5
B3SourceA5F9:
 .byte $76
B3SourceA5FA:
 .byte $01
B3SourceA5FB:
 .byte $0e
B3SourceA5FC:
 .byte $0e
B3SourceA5FD:
 .byte $0d
B3SourceA5FE:
 .byte $0b
B3SourceA5FF:
 .byte $06
B3SourceA600:
 .byte $0c
B3SourceA601:
 .byte $0f
B3SourceA602:
 .byte $0a
B3SourceA603:
 .byte $09
B3SourceA604:
 .byte $03
B3SourceA605:
 .byte $0d
B3SourceA606:
 .byte $08
B3SourceA607:
 .byte $0d
B3SourceA608:
 .byte $06
B3SourceA609:
 .byte $0c
B3SourceA60A:
 .byte $47
B3SourceA60B:
 .byte $49
B3SourceA60C:
 .byte $42
B3SourceA60D:
 .byte $4a
B3SourceA60E:
 .byte $43
B3SourceA60F:
 .byte $4b
B3SourceA610:
 .byte $8c
B3SourceA611:
 .byte $e3
B3SourceA612:
 .byte $04
B3SourceA613:
 .byte $a9
B3SourceA614:
 .byte $06
B3SourceA615:
 .byte $8d
B3SourceA616:
 .byte $ea
B3SourceA617:
 .byte $04
B3SourceA618:
 .byte $ad
B3SourceA619:
 .byte $ea
B3SourceA61A:
 .byte $04
B3SourceA61B:
 .byte $a8
B3SourceA61C:
 .byte $b9
B3SourceA61D:
 .byte $09
B3SourceA61E:
 .byte $a6
B3SourceA61F:
 .byte $8d
B3SourceA620:
 .byte $0a
B3SourceA621:
 .byte $40
B3SourceA622:
 .byte $a9
B3SourceA623:
 .byte $18
B3SourceA624:
 .byte $8d
B3SourceA625:
 .byte $08
B3SourceA626:
 .byte $40
B3SourceA627:
 .byte $8d
B3SourceA628:
 .byte $0b
B3SourceA629:
 .byte $40
B3SourceA62A:
 .byte $d0
B3SourceA62B:
 .byte $20
B3SourceA62C:
 .byte $8c
B3SourceA62D:
 .byte $e3
B3SourceA62E:
 .byte $04
B3SourceA62F:
 .byte $a9
B3SourceA630:
 .byte $20
B3SourceA631:
 .byte $8d
B3SourceA632:
 .byte $ea
B3SourceA633:
 .byte $04
B3SourceA634:
 .byte $ad
B3SourceA635:
 .byte $ea
B3SourceA636:
 .byte $04
B3SourceA637:
 .byte $4a
B3SourceA638:
 .byte $90
B3SourceA639:
 .byte $12
B3SourceA63A:
 .byte $a8
B3SourceA63B:
 .byte $be
B3SourceA63C:
 .byte $fa
B3SourceA63D:
 .byte $a5
B3SourceA63E:
 .byte $b9
B3SourceA63F:
 .byte $29
B3SourceA640:
 .byte $a7
B3SourceA641:
 .byte $8d
B3SourceA642:
 .byte $0c
B3SourceA643:
 .byte $40
B3SourceA644:
 .byte $8e
B3SourceA645:
 .byte $0e
B3SourceA646:
 .byte $40
B3SourceA647:
 .byte $a9
B3SourceA648:
 .byte $18
B3SourceA649:
 .byte $8d
B3SourceA64A:
 .byte $0f
B3SourceA64B:
 .byte $40
B3SourceA64C:
 .byte $ce
B3SourceA64D:
 .byte $ea
B3SourceA64E:
 .byte $04
B3SourceA64F:
 .byte $d0
B3SourceA650:
 .byte $0f
B3SourceA651:
 .byte $a9
B3SourceA652:
 .byte $f0
B3SourceA653:
 .byte $8d
B3SourceA654:
 .byte $0c
B3SourceA655:
 .byte $40
B3SourceA656:
 .byte $a9
B3SourceA657:
 .byte $00
B3SourceA658:
 .byte $8d
B3SourceA659:
 .byte $08
B3SourceA65A:
 .byte $40
B3SourceA65B:
 .byte $a9
B3SourceA65C:
 .byte $00
B3SourceA65D:
 .byte $8d
B3SourceA65E:
 .byte $e3
B3SourceA65F:
 .byte $04
B3SourceA660:
 .byte $60
B3SourceA661:
 LDA B3SourceImage+$13
B3SourceA664:
 CMP #$08
B3SourceA666:
 jne ::B3SourceA66B
B3SourceA668:
 .byte $4c
B3SourceA669:
 .byte $ff
B3SourceA66A:
 .byte $a6
B3SourceA66B:
 LDA B3SourceImage+$13
B3SourceA66E:
 jmi ::B3SourceA618
B3SourceA670:
 LDY B3SourceImage+$23
B3SourceA673:
 jeq ::B3SourceA690
B3SourceA675:
 .byte $30
B3SourceA676:
 .byte $99
B3SourceA677:
 .byte $4e
B3SourceA678:
 .byte $f3
B3SourceA679:
 .byte $04
B3SourceA67A:
 .byte $b0
B3SourceA67B:
 .byte $b0
B3SourceA67C:
 .byte $4e
B3SourceA67D:
 .byte $f3
B3SourceA67E:
 .byte $04
B3SourceA67F:
 .byte $b0
B3SourceA680:
 .byte $24
B3SourceA681:
 .byte $4e
B3SourceA682:
 .byte $f3
B3SourceA683:
 .byte $04
B3SourceA684:
 .byte $b0
B3SourceA685:
 .byte $52
B3SourceA686:
 .byte $4e
B3SourceA687:
 .byte $f3
B3SourceA688:
 .byte $04
B3SourceA689:
 .byte $b0
B3SourceA68A:
 .byte $6c
B3SourceA68B:
 .byte $4e
B3SourceA68C:
 .byte $f3
B3SourceA68D:
 .byte $04
B3SourceA68E:
 .byte $b0
B3SourceA68F:
 .byte $29
B3SourceA690:
 LDA B3SourceImage+$13
B3SourceA693:
 jeq ::B3SourceA6A4
B3SourceA695:
 .byte $4a
B3SourceA696:
 .byte $b0
B3SourceA697:
 .byte $9c
B3SourceA698:
 .byte $4a
B3SourceA699:
 .byte $b0
B3SourceA69A:
 .byte $12
B3SourceA69B:
 .byte $4a
B3SourceA69C:
 .byte $b0
B3SourceA69D:
 .byte $42
B3SourceA69E:
 .byte $4a
B3SourceA69F:
 .byte $b0
B3SourceA6A0:
 .byte $5e
B3SourceA6A1:
 .byte $4a
B3SourceA6A2:
 .byte $b0
B3SourceA6A3:
 .byte $1d
B3SourceA6A4:
 RTS
B3SourceA6A5:
 .byte $8c
B3SourceA6A6:
 .byte $e3
B3SourceA6A7:
 .byte $04
B3SourceA6A8:
 .byte $a9
B3SourceA6A9:
 .byte $40
B3SourceA6AA:
 .byte $8d
B3SourceA6AB:
 .byte $ea
B3SourceA6AC:
 .byte $04
B3SourceA6AD:
 .byte $ad
B3SourceA6AE:
 .byte $ea
B3SourceA6AF:
 .byte $04
B3SourceA6B0:
 .byte $4a
B3SourceA6B1:
 .byte $a8
B3SourceA6B2:
 .byte $a2
B3SourceA6B3:
 .byte $0f
B3SourceA6B4:
 .byte $b9
B3SourceA6B5:
 .byte $08
B3SourceA6B6:
 .byte $a7
B3SourceA6B7:
 .byte $d0
B3SourceA6B8:
 .byte $88
B3SourceA6B9:
 .byte $8c
B3SourceA6BA:
 .byte $e3
B3SourceA6BB:
 .byte $04
B3SourceA6BC:
 .byte $a9
B3SourceA6BD:
 .byte $0e
B3SourceA6BE:
 .byte $8d
B3SourceA6BF:
 .byte $ea
B3SourceA6C0:
 .byte $04
B3SourceA6C1:
 .byte $ad
B3SourceA6C2:
 .byte $ea
B3SourceA6C3:
 .byte $04
B3SourceA6C4:
 .byte $a8
B3SourceA6C5:
 .byte $b9
B3SourceA6C6:
 .byte $e0
B3SourceA6C7:
 .byte $a5
B3SourceA6C8:
 .byte $29
B3SourceA6C9:
 .byte $0f
B3SourceA6CA:
 .byte $09
B3SourceA6CB:
 .byte $10
B3SourceA6CC:
 .byte $aa
B3SourceA6CD:
 .byte $b9
B3SourceA6CE:
 .byte $e0
B3SourceA6CF:
 .byte $a5
B3SourceA6D0:
 .byte $4a
B3SourceA6D1:
 .byte $4a
B3SourceA6D2:
 .byte $4a
B3SourceA6D3:
 .byte $4a
B3SourceA6D4:
 .byte $09
B3SourceA6D5:
 .byte $10
B3SourceA6D6:
 .byte $d0
B3SourceA6D7:
 .byte $df
B3SourceA6D8:
 .byte $8c
B3SourceA6D9:
 .byte $e3
B3SourceA6DA:
 .byte $04
B3SourceA6DB:
 .byte $a9
B3SourceA6DC:
 .byte $0c
B3SourceA6DD:
 .byte $8d
B3SourceA6DE:
 .byte $ea
B3SourceA6DF:
 .byte $04
B3SourceA6E0:
 .byte $ad
B3SourceA6E1:
 .byte $ea
B3SourceA6E2:
 .byte $04
B3SourceA6E3:
 .byte $a8
B3SourceA6E4:
 .byte $b9
B3SourceA6E5:
 .byte $ee
B3SourceA6E6:
 .byte $a5
B3SourceA6E7:
 .byte $29
B3SourceA6E8:
 .byte $0f
B3SourceA6E9:
 .byte $09
B3SourceA6EA:
 .byte $10
B3SourceA6EB:
 .byte $aa
B3SourceA6EC:
 .byte $b9
B3SourceA6ED:
 .byte $ee
B3SourceA6EE:
 .byte $a5
B3SourceA6EF:
 .byte $4a
B3SourceA6F0:
 .byte $4a
B3SourceA6F1:
 .byte $4a
B3SourceA6F2:
 .byte $4a
B3SourceA6F3:
 .byte $09
B3SourceA6F4:
 .byte $10
B3SourceA6F5:
 .byte $d0
B3SourceA6F6:
 .byte $df
B3SourceA6F7:
 .byte $8c
B3SourceA6F8:
 .byte $e3
B3SourceA6F9:
 .byte $04
B3SourceA6FA:
 .byte $a9
B3SourceA6FB:
 .byte $40
B3SourceA6FC:
 .byte $8d
B3SourceA6FD:
 .byte $ea
B3SourceA6FE:
 .byte $04
B3SourceA6FF:
 .byte $ad
B3SourceA700:
 .byte $ea
B3SourceA701:
 .byte $04
B3SourceA702:
 .byte $4a
B3SourceA703:
 .byte $4a
B3SourceA704:
 .byte $aa
B3SourceA705:
 .byte $09
B3SourceA706:
 .byte $10
B3SourceA707:
 .byte $d0
B3SourceA708:
 .byte $ec
B3SourceA709:
 .byte $15
B3SourceA70A:
 .byte $16
B3SourceA70B:
 .byte $16
B3SourceA70C:
 .byte $17
B3SourceA70D:
 .byte $17
B3SourceA70E:
 .byte $18
B3SourceA70F:
 .byte $19
B3SourceA710:
 .byte $19
B3SourceA711:
 .byte $1a
B3SourceA712:
 .byte $1a
B3SourceA713:
 .byte $1c
B3SourceA714:
 .byte $1d
B3SourceA715:
 .byte $1d
B3SourceA716:
 .byte $1e
B3SourceA717:
 .byte $1e
B3SourceA718:
 .byte $1f
B3SourceA719:
 .byte $1f
B3SourceA71A:
 .byte $1f
B3SourceA71B:
 .byte $1f
B3SourceA71C:
 .byte $1e
B3SourceA71D:
 .byte $1d
B3SourceA71E:
 .byte $1c
B3SourceA71F:
 .byte $1e
B3SourceA720:
 .byte $1f
B3SourceA721:
 .byte $1f
B3SourceA722:
 .byte $1e
B3SourceA723:
 .byte $1d
B3SourceA724:
 .byte $1c
B3SourceA725:
 .byte $1a
B3SourceA726:
 .byte $18
B3SourceA727:
 .byte $16
B3SourceA728:
 .byte $14
B3SourceA729:
 .byte $15
B3SourceA72A:
 .byte $16
B3SourceA72B:
 .byte $16
B3SourceA72C:
 .byte $17
B3SourceA72D:
 .byte $17
B3SourceA72E:
 .byte $18
B3SourceA72F:
 .byte $19
B3SourceA730:
 .byte $19
B3SourceA731:
 .byte $1a
B3SourceA732:
 .byte $1a
B3SourceA733:
 .byte $1c
B3SourceA734:
 .byte $1d
B3SourceA735:
 .byte $1d
B3SourceA736:
 .byte $1e
B3SourceA737:
 .byte $1e
B3SourceA738:
 .byte $1f
B3SourceA739:
 .byte $a5
B3SourceA73A:
 .byte $8b
B3SourceA73B:
 .byte $c9
B3SourceA73C:
 .byte $03
B3SourceA73D:
 .byte $f0
B3SourceA73E:
 .byte $10
B3SourceA73F:
 .byte $c0
B3SourceE2C0:
 LDA B3SourceTimers+$00
B3SourceE2C3:
 CMP #$7e
B3SourceE2C5:
 jeq ::B3SourceE2D6
B3SourceE2C7:
 LDA B3SourceTimers+$00
B3SourceE2CA:
 jne ::B3SourceE2E1
B3SourceE2CC:
 LDA B3SourceTimers+$01
B3SourceE2CF:
 jeq ::B3SourceE2D6
B3SourceE2D1:
 DEC B3SourceImage+$28
B3SourceE2D4:
 jne ::B3SourceE2E0
B3SourceE2D6:
 LDA #$00
B3SourceE2D8:
 STA B3SourceTimers+$01
B3SourceE2DB:
 LDA #$0f
B3SourceE2DD:
 jsr B3Write4015
B3SourceE2E0:
 RTS
B3SourceE2E1:
 STA B3SourceTimers+$01
B3SourceE2E4:
 TAY
B3SourceE2E5:
 jsr B3Hot6E2E5
 nop
 nop
B3SourceE2E8:
 STA $4010
B3SourceE2EB:
 STA $7aff
B3SourceE2EE:
 jsr B3Hot6E2EE
 nop
 nop
B3SourceE2F1:
 jsr B3Write4012
B3SourceE2F4:
 jsr B3Hot6E2F4
 nop
 nop
B3SourceE2F7:
 STA $4013
B3SourceE2FA:
 LDA #$a0
B3SourceE2FC:
 STA B3SourceImage+$28
B3SourceE2FF:
 LDA #$0f
B3SourceE301:
 jsr B3Write4015
B3SourceE304:
 LDA #$1f
B3SourceE306:
 jsr B3Write4015
B3SourceE309:
 RTS
B3SourceE30A:
 .byte $80
B3SourceE30B:
 .byte $82
B3SourceE30C:
 .byte $6e
B3SourceE30D:
 .byte $82
B3SourceE30E:
 .byte $a6
B3SourceE30F:
 .byte $ca
B3SourceE310:
 .byte $ca
B3SourceE311:
 .byte $aa
B3SourceE312:
 .byte $aa
B3SourceE313:
 .byte $60
B3SourceE314:
 .byte $60
B3SourceE315:
 .byte $ca
B3SourceE316:
 .byte $70
B3SourceE317:
 .byte $b8
B3SourceE318:
 .byte $b8
B3SourceE319:
 .byte $b8
B3SourceE31A:
 .byte $08
B3SourceE31B:
 .byte $1c
B3SourceE31C:
 .byte $08
B3SourceE31D:
 .byte $40
B3SourceE31E:
 .byte $10
B3SourceE31F:
 .byte $20
B3SourceE320:
 .byte $14
B3SourceE321:
 .byte $38
B3SourceE322:
 .byte $38
B3SourceE323:
 .byte $34
B3SourceE324:
 .byte $34
B3SourceE325:
 .byte $10
B3SourceE326:
 .byte $1c
B3SourceE327:
 .byte $48
B3SourceE328:
 .byte $48
B3SourceE329:
 .byte $48
B3SourceE32A:
 .byte $0f
B3SourceE32B:
 .byte $0f
B3SourceE32C:
 .byte $0f
B3SourceE32D:
 .byte $0f
B3SourceE32E:
 .byte $0f
B3SourceE32F:
 .byte $0f
B3SourceE330:
 .byte $0e
B3SourceE331:
 .byte $0f
B3SourceE332:
 .byte $0e
B3SourceE333:
 .byte $0f
B3SourceE334:
 .byte $0e
B3SourceE335:
 .byte $0d
B3SourceE336:
 .byte $0f
B3SourceE337:
 .byte $0f
B3SourceE338:
 .byte $0e
B3SourceE339:
 .byte $0d
B3SourceE33A:
 .byte $60
B3SourceE33B:
 AND #$0f
B3SourceE33D:
 CLC
B3SourceE33E:
 ADC B3SourceImage+$2d
B3SourceE341:
 ADC $7af7
B3SourceE344:
 TAY
B3SourceE345:
 jsr B3Hot6E345
 nop
 nop
B3SourceE348:
 RTS
B3SourceE349:
 JMP ::B3SourceE3EE
B3SourceE34C:
 .byte $4c
B3SourceE34D:
 .byte $01
B3SourceE34E:
 .byte $e5
B3SourceE34F:
 LDA B3SourceImage+$24
B3SourceE352:
 jne ::B3SourceE349
B3SourceE354:
 LDA B3SourceImage+$14
B3SourceE357:
 jeq ::B3SourceE364
B3SourceE359:
 LDA B3SourceImage+$25
B3SourceE35C:
 jeq ::B3SourceE361
B3SourceE35E:
 .byte $8d
B3SourceE35F:
 .byte $f5
B3SourceE360:
 .byte $07
B3SourceE361:
 JMP ::B3SourceE4C5
B3SourceE364:
 LDA B3SourceImage+$24
B3SourceE367:
 jne ::B3SourceE349
B3SourceE369:
 LDA B3SourceImage+$25
B3SourceE36C:
 AND #$f0
B3SourceE36E:
 jeq ::B3SourceE349
B3SourceE370:
 LDA B3SourceImage+$25
B3SourceE373:
 jne ::B3SourceE37B
B3SourceE375:
 .byte $ad
B3SourceE376:
 .byte $e5
B3SourceE377:
 .byte $04
B3SourceE378:
 .byte $d0
B3SourceE379:
 .byte $71
B3SourceE37A:
 .byte $60
B3SourceE37B:
 STA B3SourceImage+$15
B3SourceE37E:
 LDY #$00
B3SourceE380:
 STY B3SourceImage+$14
B3SourceE383:
 LSR A
B3SourceE384:
 LSR A
B3SourceE385:
 LSR A
B3SourceE386:
 LSR A
B3SourceE387:
 TAY
B3SourceE388:
 jsr B3KnownE388
 nop
 nop
B3SourceE38B:
 STA $7ae0
B3SourceE38E:
 jsr B3KnownE38E
 nop
 nop
B3SourceE391:
 CLC
B3SourceE392:
 ADC #$02
B3SourceE394:
 STA $7ae1
B3SourceE397:
 jsr B3KnownE397
 nop
 nop
B3SourceE39A:
 STA $7ae2
B3SourceE39D:
 LDA $7ae0
B3SourceE3A0:
 STA B3SourceImage+$0f
B3SourceE3A3:
 INC B3SourceImage+$0f
B3SourceE3A6:
 LDY B3SourceImage+$0f
B3SourceE3A9:
 CPY $7ae1
B3SourceE3AC:
 jne ::B3SourceE3B6
B3SourceE3AE:
 LDA $7ae2
B3SourceE3B1:
 jne ::B3SourceE3A0
B3SourceE3B3:
 .byte $4c
B3SourceE3B4:
 .byte $01
B3SourceE3B5:
 .byte $e5
B3SourceE3B6:
 jsr B3KnownE3B6
 nop
 nop
B3SourceE3B9:
 TAY
B3SourceE3BA:
 jsr B3KnownE3BA
 nop
 nop
B3SourceE3BD:
 STA B3SourceImage+$2d
B3SourceE3C0:
 jsr B3KnownE3C0
 nop
 nop
B3SourceE3C3:
 STA z:B3SourceZp+0
B3SourceE3C5:
 jsr B3KnownE3C5
 nop
 nop
B3SourceE3C8:
 STA z:B3SourceZp+1
B3SourceE3CA:
 jsr B3KnownE3CA
 nop
 nop
B3SourceE3CD:
 STA B3SourceImage+$00
B3SourceE3D0:
 jsr B3KnownE3D0
 nop
 nop
B3SourceE3D3:
 STA B3SourceImage+$2f
B3SourceE3D6:
 jsr B3KnownE3D6
 nop
 nop
B3SourceE3D9:
 STA B3SourceImage+$01
B3SourceE3DC:
 STA B3SourceTimers+$03
B3SourceE3DF:
 jsr B3KnownE3DF
 nop
 nop
B3SourceE3E2:
 STA B3SourceImage+$02
B3SourceE3E5:
 STA B3SourceImage+$0e
B3SourceE3E8:
 JMP ::B3SourceE48C
B3SourceE3EB:
 JMP ::B3SourceE4C5
B3SourceE3EE:
 LDA B3SourceImage+$24
B3SourceE3F1:
 jne ::B3SourceE445
B3SourceE3F3:
 LDA B3SourceImage+$25
B3SourceE3F6:
 jne ::B3SourceE401
B3SourceE3F8:
 LDA B3SourceImage+$14
B3SourceE3FB:
 ORA B3SourceImage+$15
B3SourceE3FE:
 jne ::B3SourceE3EB
B3SourceE400:
 RTS
B3SourceE401:
 STA B3SourceImage+$15
B3SourceE404:
 CMP #$09
B3SourceE406:
 jeq ::B3SourceE411
B3SourceE408:
 CMP #$0a
B3SourceE40A:
 jeq ::B3SourceE411
B3SourceE40C:
 LDY #$00
B3SourceE40E:
 STY $7af7
B3SourceE411:
 LDY #$00
B3SourceE413:
 STY B3SourceImage+$14
B3SourceE416:
 TAY
B3SourceE417:
 jsr B3KnownE417
 nop
 nop
B3SourceE41A:
 STA $7ae0
B3SourceE41D:
 jsr B3KnownE41D
 nop
 nop
B3SourceE420:
 CLC
B3SourceE421:
 ADC #$02
B3SourceE423:
 STA $7ae1
B3SourceE426:
 jsr B3KnownE426
 nop
 nop
B3SourceE429:
 STA $7ae2
B3SourceE42C:
 LDA $7ae0
B3SourceE42F:
 STA B3SourceImage+$0f
B3SourceE432:
 INC B3SourceImage+$0f
B3SourceE435:
 LDY B3SourceImage+$0f
B3SourceE438:
 CPY $7ae1
B3SourceE43B:
 jne ::B3SourceE45A
B3SourceE43D:
 LDA $7ae2
B3SourceE440:
 jne ::B3SourceE42F
B3SourceE442:
 .byte $4c
B3SourceE443:
 .byte $01
B3SourceE444:
 .byte $e5
B3SourceE445:
 STA B3SourceImage+$14
B3SourceE448:
 LDY B3SourceImage+$15
B3SourceE44B:
 STY B3SourceTimers+$05
B3SourceE44E:
 LDY #$00
B3SourceE450:
 STY B3SourceImage+$15
B3SourceE453:
 STY $7af7
B3SourceE456:
 INY
B3SourceE457:
 LSR A
B3SourceE458:
 jcc ::B3SourceE456
B3SourceE45A:
 jsr B3KnownE45A
 nop
 nop
B3SourceE45D:
 TAY
B3SourceE45E:
 jsr B3KnownE45E
 nop
 nop
B3SourceE461:
 STA B3SourceImage+$2d
B3SourceE464:
 jsr B3KnownE464
 nop
 nop
B3SourceE467:
 STA z:B3SourceZp+0
B3SourceE469:
 jsr B3KnownE469
 nop
 nop
B3SourceE46C:
 STA z:B3SourceZp+1
B3SourceE46E:
 jsr B3KnownE46E
 nop
 nop
B3SourceE471:
 STA B3SourceImage+$00
B3SourceE474:
 jsr B3KnownE474
 nop
 nop
B3SourceE477:
 STA B3SourceImage+$2f
B3SourceE47A:
 jsr B3KnownE47A
 nop
 nop
B3SourceE47D:
 STA B3SourceImage+$01
B3SourceE480:
 STA B3SourceTimers+$03
B3SourceE483:
 jsr B3KnownE483
 nop
 nop
B3SourceE486:
 STA B3SourceImage+$02
B3SourceE489:
 STA B3SourceImage+$0e
B3SourceE48C:
 LDA #$01
B3SourceE48E:
 STA B3SourceImage+$04
B3SourceE491:
 STA B3SourceImage+$06
B3SourceE494:
 STA B3SourceImage+$09
B3SourceE497:
 STA B3SourceImage+$0a
B3SourceE49A:
 STA B3SourceImage+$0c
B3SourceE49D:
 LDA #$00
B3SourceE49F:
 STA B3SourceImage+$2e
B3SourceE4A2:
 STA B3SourceImage+$2a
B3SourceE4A5:
 STA $7af0
B3SourceE4A8:
 STA $7af4
B3SourceE4AB:
 LDA B3SourceImage+$14
B3SourceE4AE:
 CMP #$01
B3SourceE4B0:
 jne ::B3SourceE4BB
B3SourceE4B2:
 LDA #$00
B3SourceE4B4:
 STA B3SourceImage+$11
B3SourceE4B7:
 LDA #$08
B3SourceE4B9:
 jne ::B3SourceE4BD
B3SourceE4BB:
 LDA #$0b
B3SourceE4BD:
 jsr B3Write4015
B3SourceE4C0:
 LDA #$0f
B3SourceE4C2:
 jsr B3Write4015
B3SourceE4C5:
 DEC B3SourceImage+$04
B3SourceE4C8:
 jeq ::B3SourceE4CD
B3SourceE4CA:
 JMP ::B3SourceE57A
B3SourceE4CD:
 LDY B3SourceImage+$2e
B3SourceE4D0:
 INC B3SourceImage+$2e
B3SourceE4D3:
 jsr B3Read6B
B3SourceE4D5:
 jeq ::B3SourceE4DB
B3SourceE4D7:
 jpl ::B3SourceE53D
B3SourceE4D9:
 jne ::B3SourceE51E
B3SourceE4DB:
 LDA B3SourceImage+$14
B3SourceE4DE:
 jeq ::B3SourceE4F7
B3SourceE4E0:
 CMP #$40
B3SourceE4E2:
 jne ::B3SourceE501
B3SourceE4E4:
 .byte $a9
B3SourceE4E5:
 .byte $10
B3SourceE4E6:
 .byte $8d
B3SourceE4E7:
 .byte $f7
B3SourceE4E8:
 .byte $7a
B3SourceE4E9:
 .byte $ad
B3SourceE4EA:
 .byte $f5
B3SourceE4EB:
 .byte $07
B3SourceE4EC:
 .byte $c9
B3SourceE4ED:
 .byte $09
B3SourceE4EE:
 .byte $f0
B3SourceE4EF:
 .byte $2b
B3SourceE4F0:
 .byte $c9
B3SourceE4F1:
 .byte $0a
B3SourceE4F2:
 .byte $f0
B3SourceE4F3:
 .byte $27
B3SourceE4F4:
 .byte $4c
B3SourceE4F5:
 .byte $7b
B3SourceE4F6:
 .byte $e3
B3SourceE4F7:
 LDA B3SourceImage+$15
B3SourceE4FA:
 AND #$f0
B3SourceE4FC:
 jeq ::B3SourceE518
B3SourceE4FE:
 JMP ::B3SourceE3A3
B3SourceE501:
 LDA #$00
B3SourceE503:
 STA B3SourceImage+$14
B3SourceE506:
 STA B3SourceImage+$15
B3SourceE509:
 STA B3SourceTimers+$05
B3SourceE50C:
 STA $7af7
B3SourceE50F:
 jsr B3Write4015
B3SourceE512:
 LDX #$0f
B3SourceE514:
 jsr B3Write4015X
B3SourceE517:
 RTS
B3SourceE518:
 JMP ::B3SourceE432
B3SourceE51B:
 .byte $4c
B3SourceE51C:
 .byte $01
B3SourceE51D:
 .byte $e4
B3SourceE51E:
 CMP #$ff
B3SourceE520:
 jne ::B3SourceE528
B3SourceE522:
 .byte $ee
B3SourceE523:
 .byte $fe
B3SourceE524:
 .byte $04
B3SourceE525:
 .byte $4c
B3SourceE526:
 .byte $cd
B3SourceE527:
 .byte $e4
B3SourceE528:
 TAX
B3SourceE529:
 AND #$f0
B3SourceE52B:
 STA B3SourceTimers+$07
B3SourceE52E:
 TXA
B3SourceE52F:
 JSR ::B3SourceE33B
B3SourceE532:
 STA B3SourceImage+$03
B3SourceE535:
 LDY B3SourceImage+$2e
B3SourceE538:
 INC B3SourceImage+$2e
B3SourceE53B:
 jsr B3Read6B
B3SourceE53D:
 TAX
B3SourceE53E:
 LDA B3SourceImage+$12
B3SourceE541:
 jne ::B3SourceE574
B3SourceE543:
 TXA
B3SourceE544:
 JSR ::B3SourceE831
B3SourceE547:
 TAY
B3SourceE548:
 jne ::B3SourceE550
B3SourceE54A:
 LDA B3SourceImage+$2b
B3SourceE54D:
 JMP ::B3SourceE559
B3SourceE550:
 LDA B3SourceImage+$03
B3SourceE553:
 LDX B3SourceImage+$2b
B3SourceE556:
 JSR ::B3SourceE756
B3SourceE559:
 STA B3SourceImage+$05
B3SourceE55C:
 LDY B3SourceImage+$2e
B3SourceE55F:
 INC B3SourceImage+$2e
B3SourceE562:
 jsr B3Read6B
B3SourceE564:
 CMP #$ff
B3SourceE566:
 jne ::B3SourceE571
B3SourceE568:
 .byte $ad
B3SourceE569:
 .byte $f6
B3SourceE56A:
 .byte $07
B3SourceE56B:
 .byte $8d
B3SourceE56C:
 .byte $f4
B3SourceE56D:
 .byte $7a
B3SourceE56E:
 .byte $4c
B3SourceE56F:
 .byte $35
B3SourceE570:
 .byte $e5
B3SourceE571:
 DEC B3SourceImage+$2e
B3SourceE574:
 LDA B3SourceImage+$03
B3SourceE577:
 STA B3SourceImage+$04
B3SourceE57A:
 LDA B3SourceImage+$12
B3SourceE57D:
 jne ::B3SourceE5A7
B3SourceE57F:
 LDA $7af4
B3SourceE582:
 jeq ::B3SourceE58C
B3SourceE584:
 .byte $ad
B3SourceE585:
 .byte $d4
B3SourceE586:
 .byte $04
B3SourceE587:
 .byte $a2
B3SourceE588:
 .byte $04
B3SourceE589:
 .byte $20
B3SourceE58A:
 .byte $57
B3SourceE58B:
 .byte $e8
B3SourceE58C:
 LDY B3SourceImage+$05
B3SourceE58F:
 jeq ::B3SourceE594
B3SourceE591:
 DEC B3SourceImage+$05
B3SourceE594:
 LDA B3SourceImage+$03
B3SourceE597:
 LDX B3SourceTimers+$07
B3SourceE59A:
 JSR ::B3SourceE785
B3SourceE59D:
 jsr B3ImageSTA04
B3SourceE5A0:
 LDX #$7f
B3SourceE5A2:
 jsr B3ImageSTX05
B3SourceE5A5:
 jne ::B3SourceE5AC
B3SourceE5A7:
 .byte $a9
B3SourceE5A8:
 .byte $00
B3SourceE5A9:
 .byte $8d
B3SourceE5AA:
 .byte $f4
B3SourceE5AB:
 .byte $7a
B3SourceE5AC:
 DEC B3SourceImage+$06
B3SourceE5AF:
 jne ::B3SourceE62B
B3SourceE5B1:
 LDY B3SourceImage+$2f
B3SourceE5B4:
 INC B3SourceImage+$2f
B3SourceE5B7:
 jsr B3Read6B
B3SourceE5B9:
 jpl ::B3SourceE5DA
B3SourceE5BB:
 CMP #$ff
B3SourceE5BD:
 jne ::B3SourceE5C5
B3SourceE5BF:
 .byte $ee
B3SourceE5C0:
 .byte $ff
B3SourceE5C1:
 .byte $04
B3SourceE5C2:
 .byte $4c
B3SourceE5C3:
 .byte $b1
B3SourceE5C4:
 .byte $e5
B3SourceE5C5:
 TAX
B3SourceE5C6:
 AND #$f0
B3SourceE5C8:
 STA B3SourceTimers+$08
B3SourceE5CB:
 TXA
B3SourceE5CC:
 JSR ::B3SourceE33B
B3SourceE5CF:
 STA B3SourceImage+$29
B3SourceE5D2:
 LDY B3SourceImage+$2f
B3SourceE5D5:
 INC B3SourceImage+$2f
B3SourceE5D8:
 jsr B3Read6B
B3SourceE5DA:
 TAY
B3SourceE5DB:
 jne ::B3SourceE5EC
B3SourceE5DD:
 LDA #$83
B3SourceE5DF:
 jsr B3ImageSTA00
B3SourceE5E2:
 LDA #$94
B3SourceE5E4:
 jsr B3ImageSTA01
B3SourceE5E7:
 STA B3SourceImage+$2a
B3SourceE5EA:
 jne ::B3SourceE5B1
B3SourceE5EC:
 TAX
B3SourceE5ED:
 LDA B3SourceImage+$11
B3SourceE5F0:
 ORA B3SourceImage+$16
B3SourceE5F3:
 jne ::B3SourceE625
B3SourceE5F5:
 TXA
B3SourceE5F6:
 JSR ::B3SourceE7BF
B3SourceE5F9:
 jne ::B3SourceE601
B3SourceE5FB:
 LDA B3SourceImage+$2b
B3SourceE5FE:
 JMP ::B3SourceE60A
B3SourceE601:
 LDA B3SourceImage+$29
B3SourceE604:
 LDX B3SourceImage+$2c
B3SourceE607:
 JSR ::B3SourceE756
B3SourceE60A:
 STA B3SourceImage+$07
B3SourceE60D:
 LDY B3SourceImage+$2f
B3SourceE610:
 INC B3SourceImage+$2f
B3SourceE613:
 jsr B3Read6B
B3SourceE615:
 CMP #$ff
B3SourceE617:
 jne ::B3SourceE622
B3SourceE619:
 .byte $ad
B3SourceE61A:
 .byte $f2
B3SourceE61B:
 .byte $07
B3SourceE61C:
 .byte $8d
B3SourceE61D:
 .byte $f0
B3SourceE61E:
 .byte $7a
B3SourceE61F:
 .byte $4c
B3SourceE620:
 .byte $d2
B3SourceE621:
 .byte $e5
B3SourceE622:
 DEC B3SourceImage+$2f
B3SourceE625:
 LDA B3SourceImage+$29
B3SourceE628:
 STA B3SourceImage+$06
B3SourceE62B:
 LDA B3SourceImage+$11
B3SourceE62E:
 ORA B3SourceImage+$16
B3SourceE631:
 jne ::B3SourceE660
B3SourceE633:
 LDA $7af0
B3SourceE636:
 jeq ::B3SourceE640
B3SourceE638:
 .byte $a2
B3SourceE639:
 .byte $00
B3SourceE63A:
 .byte $ad
B3SourceE63B:
 .byte $d6
B3SourceE63C:
 .byte $04
B3SourceE63D:
 .byte $20
B3SourceE63E:
 .byte $57
B3SourceE63F:
 .byte $e8
B3SourceE640:
 LDY B3SourceImage+$07
B3SourceE643:
 jeq ::B3SourceE648
B3SourceE645:
 DEC B3SourceImage+$07
B3SourceE648:
 LDA B3SourceImage+$29
B3SourceE64B:
 LDX B3SourceTimers+$08
B3SourceE64E:
 JSR ::B3SourceE785
B3SourceE651:
 jsr B3ImageSTA00
B3SourceE654:
 LDA B3SourceImage+$2a
B3SourceE657:
 jne ::B3SourceE65B
B3SourceE659:
 LDA #$7f
B3SourceE65B:
 jsr B3ImageSTA01
B3SourceE65E:
 jne ::B3SourceE665
B3SourceE660:
 .byte $a9
B3SourceE661:
 .byte $00
B3SourceE662:
 .byte $8d
B3SourceE663:
 .byte $f0
B3SourceE664:
 .byte $7a
B3SourceE665:
 LDA B3SourceImage+$00
B3SourceE668:
 jeq ::B3SourceE6BD
B3SourceE66A:
 DEC B3SourceImage+$09
B3SourceE66D:
 jne ::B3SourceE6BD
B3SourceE66F:
 LDY B3SourceImage+$00
B3SourceE672:
 INC B3SourceImage+$00
B3SourceE675:
 jsr B3Read6B
B3SourceE677:
 jpl ::B3SourceE68E
B3SourceE679:
 JSR ::B3SourceE33B
B3SourceE67C:
 STA B3SourceImage+$08
B3SourceE67F:
 LDA #$1f
B3SourceE681:
 jsr B3ImageSTA08
B3SourceE684:
 LDY B3SourceImage+$00
B3SourceE687:
 INC B3SourceImage+$00
B3SourceE68A:
 jsr B3Read6B
B3SourceE68C:
 jeq ::B3SourceE6B4
B3SourceE68E:
 JSR ::B3SourceE835
B3SourceE691:
 jeq ::B3SourceE6B2
B3SourceE693:
 LDA B3SourceImage+$08
B3SourceE696:
 CMP #$0a
B3SourceE698:
 jcc ::B3SourceE6A6
B3SourceE69A:
 CMP #$13
B3SourceE69C:
 jcc ::B3SourceE6AA
B3SourceE69E:
 CMP #$25
B3SourceE6A0:
 jcs ::B3SourceE6AE
B3SourceE6A2:
 LDA #$50
B3SourceE6A4:
 jne ::B3SourceE6B4
B3SourceE6A6:
 LDA #$18
B3SourceE6A8:
 jne ::B3SourceE6B4
B3SourceE6AA:
 LDA #$20
B3SourceE6AC:
 jne ::B3SourceE6B4
B3SourceE6AE:
 LDA #$ff
B3SourceE6B0:
 jne ::B3SourceE6B4
B3SourceE6B2:
 LDA #$80
B3SourceE6B4:
 jsr B3ImageSTA08
B3SourceE6B7:
 LDX B3SourceImage+$08
B3SourceE6BA:
 STX B3SourceImage+$09
B3SourceE6BD:
 LDA B3SourceImage+$01
B3SourceE6C0:
 jeq ::B3SourceE6FD
B3SourceE6C2:
 DEC B3SourceImage+$0a
B3SourceE6C5:
 jne ::B3SourceE6FD
B3SourceE6C7:
 LDY B3SourceImage+$01
B3SourceE6CA:
 INC B3SourceImage+$01
B3SourceE6CD:
 jsr B3Read6B
B3SourceE6CF:
 jeq ::B3SourceE700
B3SourceE6D1:
 jpl ::B3SourceE6E3
B3SourceE6D3:
 JSR ::B3SourceE33B
B3SourceE6D6:
 STA B3SourceImage+$0b
B3SourceE6D9:
 LDY B3SourceImage+$01
B3SourceE6DC:
 INC B3SourceImage+$01
B3SourceE6DF:
 jsr B3Read6B
B3SourceE6E1:
 jeq ::B3SourceE700
B3SourceE6E3:
 LSR A
B3SourceE6E4:
 TAY
B3SourceE6E5:
 jsr B3Hot6E6E5
 nop
 nop
B3SourceE6E8:
 jsr B3ImageSTA0C
B3SourceE6EB:
 jsr B3Hot6E6EB
 nop
 nop
B3SourceE6EE:
 jsr B3ImageSTA0E
B3SourceE6F1:
 jsr B3Hot6E6F1
 nop
 nop
B3SourceE6F4:
 jsr B3ImageSTA0F
B3SourceE6F7:
 LDA B3SourceImage+$0b
B3SourceE6FA:
 STA B3SourceImage+$0a
B3SourceE6FD:
 JMP ::B3SourceE709
B3SourceE700:
 LDA B3SourceTimers+$03
B3SourceE703:
 STA B3SourceImage+$01
B3SourceE706:
 JMP ::B3SourceE6C7
B3SourceE709:
 LDA B3SourceImage+$02
B3SourceE70C:
 jeq ::B3SourceE738
B3SourceE70E:
 DEC B3SourceImage+$0c
B3SourceE711:
 jne ::B3SourceE738
B3SourceE713:
 LDY B3SourceImage+$02
B3SourceE716:
 INC B3SourceImage+$02
B3SourceE719:
 jsr B3Read6B
B3SourceE71B:
 jeq ::B3SourceE741
B3SourceE71D:
 jpl ::B3SourceE72F
B3SourceE71F:
 JSR ::B3SourceE33B
B3SourceE722:
 STA B3SourceImage+$0d
B3SourceE725:
 LDY B3SourceImage+$02
B3SourceE728:
 INC B3SourceImage+$02
B3SourceE72B:
 jsr B3Read6B
B3SourceE72D:
 jeq ::B3SourceE741
B3SourceE72F:
 STA B3SourceTimers+$00
B3SourceE732:
 LDA B3SourceImage+$0d
B3SourceE735:
 STA B3SourceImage+$0c
B3SourceE738:
 JSR ::B3SourceE2C0
B3SourceE73B:
 LDA #$00
B3SourceE73D:
 STA B3SourceTimers+$00
B3SourceE740:
 RTS
B3SourceE741:
 LDA B3SourceImage+$0e
B3SourceE744:
 STA B3SourceImage+$02
B3SourceE747:
 JMP ::B3SourceE713
B3SourceE74A:
 .byte $10
B3SourceE74B:
 .byte $1e
B3SourceE74C:
 .byte $1f
B3SourceE74D:
 .byte $1f
B3SourceE74E:
 .byte $00
B3SourceE74F:
 .byte $03
B3SourceE750:
 .byte $0a
B3SourceE751:
 .byte $02
B3SourceE752:
 .byte $00
B3SourceE753:
 .byte $18
B3SourceE754:
 .byte $18
B3SourceE755:
 .byte $58
B3SourceE756:
 CMP #$13
B3SourceE758:
 jcc ::B3SourceE75E
B3SourceE75A:
 LDA #$3f
B3SourceE75C:
 jne ::B3SourceE760
B3SourceE75E:
 LDA #$16
B3SourceE760:
 LDX #$82
B3SourceE762:
 LDY #$7f
B3SourceE764:
 RTS
B3SourceE765:
 .byte $96
B3SourceE766:
 .byte $b1
B3SourceE767:
 .byte $ed
B3SourceE768:
 .byte $b1
B3SourceE769:
 .byte $44
B3SourceE76A:
 .byte $b2
B3SourceE76B:
 .byte $9c
B3SourceE76C:
 .byte $b2
B3SourceE76D:
 .byte $0a
B3SourceE76E:
 .byte $b3
B3SourceE76F:
 .byte $61
B3SourceE770:
 .byte $b3
B3SourceE771:
 .byte $ed
B3SourceE772:
 .byte $b1
B3SourceE773:
 .byte $a1
B3SourceE774:
 .byte $b3
B3SourceE775:
 .byte $d6
B3SourceE776:
 .byte $b1
B3SourceE777:
 .byte $2d
B3SourceE778:
 .byte $b2
B3SourceE779:
 .byte $84
B3SourceE77A:
 .byte $b2
B3SourceE77B:
 .byte $dc
B3SourceE77C:
 .byte $b2
B3SourceE77D:
 .byte $f3
B3SourceE77E:
 .byte $b2
B3SourceE77F:
 .byte $4a
B3SourceE780:
 .byte $b3
B3SourceE781:
 .byte $2d
B3SourceE782:
 .byte $b2
B3SourceE783:
 .byte $e1
B3SourceE784:
 .byte $b3
B3SourceE785:
 PHA
B3SourceE786:
 TXA
B3SourceE787:
 AND #$70
B3SourceE789:
 LSR A
B3SourceE78A:
 LSR A
B3SourceE78B:
 LSR A
B3SourceE78C:
 TAX
B3SourceE78D:
 PLA
B3SourceE78E:
 CMP #$13
B3SourceE790:
 jcc ::B3SourceE79E
B3SourceE792:
 jsr B3Hot6E792
 nop
 nop
B3SourceE795:
 STA z:B3SourceZp+4
B3SourceE797:
 jsr B3Hot6E797
 nop
 nop
B3SourceE79A:
 STA z:B3SourceZp+5
B3SourceE79C:
 jne ::B3SourceE7A8
B3SourceE79E:
 jsr B3Hot6E79E
 nop
 nop
B3SourceE7A1:
 STA z:B3SourceZp+4
B3SourceE7A3:
 jsr B3Hot6E7A3
 nop
 nop
B3SourceE7A6:
 STA z:B3SourceZp+5
B3SourceE7A8:
 jsr B3Read71
B3SourceE7AA:
 RTS
B3SourceE7AB:
 .byte $8c
B3SourceE7AC:
 .byte $01
B3SourceE7AD:
 .byte $40
B3SourceE7AE:
 .byte $8e
B3SourceE7AF:
 .byte $00
B3SourceE7B0:
 .byte $40
B3SourceE7B1:
 .byte $60
B3SourceE7B2:
 .byte $8e
B3SourceE7B3:
 .byte $04
B3SourceE7B4:
 .byte $40
B3SourceE7B5:
 .byte $8c
B3SourceE7B6:
 .byte $05
B3SourceE7B7:
 .byte $40
B3SourceE7B8:
 .byte $60
B3SourceE7B9:
 .byte $8e
B3SourceE7BA:
 .byte $00
B3SourceE7BB:
 .byte $40
B3SourceE7BC:
 .byte $8c
B3SourceE7BD:
 .byte $01
B3SourceE7BE:
 .byte $40
B3SourceE7BF:
 LDX #$00
B3SourceE7C1:
 CMP #$7e
B3SourceE7C3:
 jne ::B3SourceE7C8
B3SourceE7C5:
 LDA #$00
B3SourceE7C7:
 RTS
B3SourceE7C8:
 LDY #$01
B3SourceE7CA:
 STY $7ae3
B3SourceE7CD:
 PHA
B3SourceE7CE:
 TAY
B3SourceE7CF:
 jmi ::B3SourceE7D9
B3SourceE7D1:
 INC $7ae3
B3SourceE7D4:
 SEC
B3SourceE7D5:
 SBC #$18
B3SourceE7D7:
 jpl ::B3SourceE7D1
B3SourceE7D9:
 CLC
B3SourceE7DA:
 ADC #$18
B3SourceE7DC:
 TAY
B3SourceE7DD:
 jsr B3Hot6E7DD
 nop
 nop
B3SourceE7E0:
 STA z:B3SourceZp+2
B3SourceE7E2:
 jsr B3Hot6E7E2
 nop
 nop
B3SourceE7E5:
 STA z:B3SourceZp+3
B3SourceE7E7:
 LSR z:B3SourceZp+3
B3SourceE7E9:
 ROR z:B3SourceZp+2
B3SourceE7EB:
 DEC $7ae3
B3SourceE7EE:
 jne ::B3SourceE7E7
B3SourceE7F0:
 PLA
B3SourceE7F1:
 CMP #$38
B3SourceE7F3:
 jcc ::B3SourceE7F7
B3SourceE7F5:
 DEC z:B3SourceZp+2
B3SourceE7F7:
 TXA
B3SourceE7F8:
 CMP #$04
B3SourceE7FA:
 jne ::B3SourceE808
B3SourceE7FC:
 LDA B3SourceTimers+$08
B3SourceE7FF:
 CMP #$e0
B3SourceE801:
 jeq ::B3SourceE818
B3SourceE803:
 LDA $7af0,X
B3SourceE806:
 jne ::B3SourceE851
B3SourceE808:
 LDA z:B3SourceZp+2
B3SourceE80A:
 jsr B3ImageSTA02X
B3SourceE80D:
 STA B3SourceTimers+$02,X
B3SourceE810:
 LDA z:B3SourceZp+3
B3SourceE812:
 ORA #$08
B3SourceE814:
 jsr B3ImageSTA03X
B3SourceE817:
 RTS
B3SourceE818:
 LDA z:B3SourceZp+2
B3SourceE81A:
 SEC
B3SourceE81B:
 SBC #$02
B3SourceE81D:
 jsr B3ImageSTA06
B3SourceE820:
 STA B3SourceTimers+$06
B3SourceE823:
 LDA z:B3SourceZp+3
B3SourceE825:
 ORA #$08
B3SourceE827:
 jsr B3ImageSTA07
B3SourceE82A:
 RTS
B3SourceE82B:
 .byte $8e
B3SourceE82C:
 .byte $04
B3SourceE82D:
 .byte $40
B3SourceE82E:
 .byte $8c
B3SourceE82F:
 .byte $05
B3SourceE830:
 .byte $40
B3SourceE831:
 LDX #$04
B3SourceE833:
 jne ::B3SourceE7C1
B3SourceE835:
 LDX #$08
B3SourceE837:
 jne ::B3SourceE7C1
B3SourceE839:
 .byte $b8
B3SourceE83A:
 .byte $1a
B3SourceE83B:
 .byte $38
B3SourceE83C:
 .byte $19
B3SourceE83D:
 .byte $cc
B3SourceE83E:
 .byte $17
B3SourceE83F:
 .byte $78
B3SourceE840:
 .byte $16
B3SourceE841:
 .byte $34
B3SourceE842:
 .byte $15
B3SourceE843:
 .byte $04
B3SourceE844:
 .byte $14
B3SourceE845:
 .byte $e4
B3SourceE846:
 .byte $12
B3SourceE847:
 .byte $d4
B3SourceE848:
 .byte $11
B3SourceE849:
 .byte $d4
B3SourceE84A:
 .byte $10
B3SourceE84B:
 .byte $e0
B3SourceE84C:
 .byte $0f
B3SourceE84D:
 .byte $fc
B3SourceE84E:
 .byte $0e
B3SourceE84F:
 .byte $24
B3SourceE850:
 .byte $0e
B3SourceE851:
 .byte $a5
B3SourceE852:
 .byte $6d
B3SourceE853:
 .byte $9d
B3SourceE854:
 .byte $f2
B3SourceE855:
 .byte $07
B3SourceE856:
 .byte $60
B3SourceE857:
 .byte $4a
B3SourceE858:
 .byte $90
B3SourceE859:
 .byte $06
B3SourceE85A:
 .byte $4a
B3SourceE85B:
 .byte $90
B3SourceE85C:
 .byte $03
B3SourceE85D:
 .byte $de
B3SourceE85E:
 .byte $f0
B3SourceE85F:
 .byte $7a
B3SourceE860:
 .byte $bd
B3SourceE861:
 .byte $f0
B3SourceE862:
 .byte $7a
B3SourceE863:
 .byte $dd
B3SourceE864:
 .byte $f2
B3SourceE865:
 .byte $07
B3SourceE866:
 .byte $b0
B3SourceE867:
 .byte $08
B3SourceE868:
 .byte $a9
B3SourceE869:
 .byte $00
B3SourceE86A:
 .byte $9d
B3SourceE86B:
 .byte $f0
B3SourceE86C:
 .byte $7a
B3SourceE86D:
 .byte $bd
B3SourceE86E:
 .byte $f2
B3SourceE86F:
 .byte $07
B3SourceE870:
 .byte $9d
B3SourceE871:
 .byte $02
B3SourceE872:
 .byte $40
B3SourceE873:
 .byte $60
B3SourceE874:
 .byte $08
B3SourceE875:
 .byte $08
B3SourceE876:
 .byte $0b
B3SourceE877:
 .byte $0a
B3SourceE878:
 .byte $10
B3SourceE879:
 .byte $18
B3SourceE87A:
 .byte $15
B3SourceE87B:
 .byte $16
B3SourceE87C:
 .byte $20
B3SourceE87D:
 .byte $30
B3SourceE87E:
 .byte $40
B3SourceE87F:
 .byte $60

; Existing exclusive native-music history storage, NOT a new RAM allocation.
; Standalone context only: future host source-state borrow/lifecycle unproved.
B3VirtualMaps=XgLzHistory+$700
B3SavedR0=XgLzHistory+$708
B3SavedR1=XgLzHistory+$709
B3SavedX=XgLzHistory+$70a
B3SavedY=XgLzHistory+$70b
B3Value=XgLzHistory+$70c
B3SavedABank=XgLzHistory+$70d
B3Index=XgLzHistory+$70e
B3AddressLo=XgLzHistory+$70f
B3AddressHi=XgLzHistory+$710
B3Source4012=XgLzHistory+$711
B3Source4015=XgLzHistory+$712
B3PendingClone=XgLzHistory+$713
B3ActiveClone=XgLzHistory+$714
B3WorkEnd=XgLzHistory+$715
.assert B3VirtualMaps=$7b00,error,"Standalone native image work placement"

B3ReadAbsX:
 php
 stx B3SavedX
 sty B3SavedY
 stx B3Index
 jmp B3ReadAbsolute
B3ReadAbsY:
 php
 stx B3SavedX
 sty B3SavedY
 sty B3Index
B3ReadAbsolute:
 jsr B3BorrowPointer
 tsx
 lda $0102,x
 sta R0
 lda $0103,x
 sta R1
 ldy #1
 lda (R0),y
 sta B3AddressLo
 iny
 lda (R0),y
 sta B3AddressHi
 lda R0
 clc
 adc #2
 sta $0102,x
 lda R1
 adc #0
 sta $0103,x
 lda B3AddressLo
 clc
 adc B3Index
 sta R0
 lda B3AddressHi
 adc #0
 sta R1
 jmp B3ReadAddress
B3Read6B:
 php
 stx B3SavedX
 sty B3SavedY
 jsr B3BorrowPointer
 lda z:B3SourceZp
 clc
 adc B3SavedY
 sta R0
 lda z:B3SourceZp+1
 adc #0
 sta R1
 jmp B3ReadAddress
B3Read71:
 php
 stx B3SavedX
 sty B3SavedY
 jsr B3BorrowPointer
 lda z:B3SourceZp+4
 clc
 adc B3SavedY
 sta R0
 lda z:B3SourceZp+5
 adc #0
 sta R1
B3ReadAddress:
 lda R1
 bpl B3ReadRAM
 lda #86|MMC5_PRG_ROM
 nop
 sta B3SavedABank
 lda R1
 sec
 sbc #$80
 lsr
 lsr
 lsr
 lsr
 tay
 lda B3VirtualMaps,y
 tay
 lda B3PayloadBanks,y
 ora #MMC5_PRG_ROM
 BankPRGA a
 lda R1
 and #$0f
 ora #$b0
 sta R1
 ldy #0
 lda (R0),y
 sta B3Value
 lda B3SavedABank
 BankPRGA a
 jmp B3ReadRestore
B3ReadRAM:
 ldy #0
 lda (R0),y
 sta B3Value
B3ReadRestore:
 lda B3SavedR0
 sta R0
 lda B3SavedR1
 sta R1
 ldx B3SavedX
 ldy B3SavedY
 plp
 lda B3Value
 rts
B3BorrowPointer:
 lda R0
 sta B3SavedR0
 lda R1
 sta B3SavedR1
 rts
B3PayloadBanks:
 .byte 78,86,90,93,95,96,98,118,119

; Logical source4012 is retained independently from translated hardware4012.
; Source cadence/4010/4011/4013/4015 and every source event are unchanged.
B3Write4012:
 php
 pha
 sta B3Source4012
 phx
 phy
 lda B3Source4012
 ldx #6
B3SampleFind:
 cmp B3OriginalAddresses,x
 beq B3SampleFound
 dex
 bpl B3SampleFind
 brk ; Outside qualified twelve-role request domain; never silent fallback.
B3SampleFound:
 lda B3TranslatedAddresses,x
 sta $4012
 lda #70|MMC5_PRG_ROM
 cpx #6
 bne B3SampleClone
 lda #97|MMC5_PRG_ROM
B3SampleClone:
 sta B3PendingClone
 lda B3Source4015
 and #16
 bne B3SampleDone
 lda B3PendingClone
 sta B3ActiveClone
 sta $5117
B3SampleDone:
 ply
 plx
 pla
 plp
 rts
.proc B3Write4015
 php
 pha
 sta B3Source4015
 sta GuestNativeEnable
 and #16
 beq Disable
 lda B3PendingClone
 sta B3ActiveClone
 sta $5117
 lda #4
 sta BassDmcActive
 lda #$80
 sta Cv3DmcPriority
 pla
 pha
 jsr Publish
 jmp Done
Disable:
 pla
 pha
 jsr Publish ; ORIGINAL disable precedes any E-bank restoration.
 lda #0
 sta BassDmcActive
 sta Cv3DmcPriority
 lda #$ff
 sta $5117
Done:pla
 plp
 rts
Publish:sta GuestCombinedEnable
 lda GuestMixMask
 and #8
 ora GuestCombinedEnable
 sta GuestCombinedEnable
 sta $4015
 rts
.endproc
B3Write4015X:
 php
 pha
 txa
 jsr B3Write4015
 pla
 plp
 rts
B3OriginalAddresses:
 .byte $b8,$a6,$aa,$80,$6d,$82,$60
B3TranslatedAddresses:
 .byte $d7,$c5,$c9,$ea,$f4,$ec,$c5

; Known absolute sites: every possible byte index stays in its logical4K page.
; CurrentBank remains foreground/fixture shadow; no A lease or new state.
; Preserve all original flags except LDA N/Z and X/Y; never borrow R0/R1.
B3KnownE2E5:
 php
 jsr B3KnownPage6
 lda $b329,y
 jmp B3KnownRestore
B3KnownE2EE:
 php
 jsr B3KnownPage6
 lda $b309,y
 jmp B3KnownRestore
B3KnownE2F4:
 php
 jsr B3KnownPage6
 lda $b319,y
 jmp B3KnownRestore
B3KnownE345:
 php
 jsr B3KnownPage6
 lda $b874,y
 jmp B3KnownRestore
B3KnownE388:
 php
 jsr B3KnownPage3
 lda $b52f,y
 jmp B3KnownRestore
B3KnownE38E:
 php
 jsr B3KnownPage3
 lda $b53b,y
 jmp B3KnownRestore
B3KnownE397:
 php
 jsr B3KnownPage3
 lda $b547,y
 jmp B3KnownRestore
B3KnownE3B6:
 php
 jsr B3KnownPage3
 lda $b3ff,y
 jmp B3KnownRestore
B3KnownE3BA:
 php
 jsr B3KnownPage3
 lda $b42d,y
 jmp B3KnownRestore
B3KnownE3C0:
 php
 jsr B3KnownPage3
 lda $b42e,y
 jmp B3KnownRestore
B3KnownE3C5:
 php
 jsr B3KnownPage3
 lda $b42f,y
 jmp B3KnownRestore
B3KnownE3CA:
 php
 jsr B3KnownPage3
 lda $b430,y
 jmp B3KnownRestore
B3KnownE3D0:
 php
 jsr B3KnownPage3
 lda $b431,y
 jmp B3KnownRestore
B3KnownE3D6:
 php
 jsr B3KnownPage3
 lda $b432,y
 jmp B3KnownRestore
B3KnownE3DF:
 php
 jsr B3KnownPage3
 lda $b433,y
 jmp B3KnownRestore
B3KnownE417:
 php
 jsr B3KnownPage2
 lda $b86c,y
 jmp B3KnownRestore
B3KnownE41D:
 php
 jsr B3KnownPage2
 lda $b87b,y
 jmp B3KnownRestore
B3KnownE426:
 php
 jsr B3KnownPage2
 lda $b88a,y
 jmp B3KnownRestore
B3KnownE45A:
 php
 jsr B3KnownPage2
 lda $b73f,y
 jmp B3KnownRestore
B3KnownE45E:
 php
 jsr B3KnownPage2
 lda $b76c,y
 jmp B3KnownRestore
B3KnownE464:
 php
 jsr B3KnownPage2
 lda $b76d,y
 jmp B3KnownRestore
B3KnownE469:
 php
 jsr B3KnownPage2
 lda $b76e,y
 jmp B3KnownRestore
B3KnownE46E:
 php
 jsr B3KnownPage2
 lda $b76f,y
 jmp B3KnownRestore
B3KnownE474:
 php
 jsr B3KnownPage2
 lda $b770,y
 jmp B3KnownRestore
B3KnownE47A:
 php
 jsr B3KnownPage2
 lda $b771,y
 jmp B3KnownRestore
B3KnownE483:
 php
 jsr B3KnownPage2
 lda $b772,y
 jmp B3KnownRestore
B3KnownE6E5:
 php
 jsr B3KnownPage6
 lda $b74a,y
 jmp B3KnownRestore
B3KnownE6EB:
 php
 jsr B3KnownPage6
 lda $b74e,y
 jmp B3KnownRestore
B3KnownE6F1:
 php
 jsr B3KnownPage6
 lda $b752,y
 jmp B3KnownRestore
B3KnownE792:
 php
 jsr B3KnownPage6
 lda $b765,x
 jmp B3KnownRestore
B3KnownE797:
 php
 jsr B3KnownPage6
 lda $b766,x
 jmp B3KnownRestore
B3KnownE79E:
 php
 jsr B3KnownPage6
 lda $b775,x
 jmp B3KnownRestore
B3KnownE7A3:
 php
 jsr B3KnownPage6
 lda $b776,x
 jmp B3KnownRestore
B3KnownE7DD:
 php
 jsr B3KnownPage6
 lda $b839,y
 jmp B3KnownRestore
B3KnownE7E2:
 php
 jsr B3KnownPage6
 lda $b83a,y
 jmp B3KnownRestore
B3Known9001:
 php
 jsr B3KnownPage1
 lda $b300,x
 jmp B3KnownRestore
B3Known900D:
 php
 jsr B3KnownPage1
 lda $b100,x
 jmp B3KnownRestore
B3Known9011:
 php
 jsr B3KnownPage1
 lda $b200,x
 jmp B3KnownRestore
B3Known9017:
 php
 jsr B3KnownPage1
 lda $b400,x
 jmp B3KnownRestore
B3KnownPage1:
 sty B3SavedY
 ldy B3VirtualMaps+1
 lda B3PayloadBanks,y
 ora #MMC5_PRG_ROM
 BankPRGA a
 ldy B3SavedY
 rts
B3KnownPage2:
 sty B3SavedY
 ldy B3VirtualMaps+2
 lda B3PayloadBanks,y
 ora #MMC5_PRG_ROM
 BankPRGA a
 ldy B3SavedY
 rts
B3KnownPage3:
 sty B3SavedY
 ldy B3VirtualMaps+3
 lda B3PayloadBanks,y
 ora #MMC5_PRG_ROM
 BankPRGA a
 ldy B3SavedY
 rts
B3KnownPage6:
 sty B3SavedY
 ldy B3VirtualMaps+6
 lda B3PayloadBanks,y
 ora #MMC5_PRG_ROM
 BankPRGA a
 ldy B3SavedY
 rts
B3KnownRestore:
 sta B3Value
 lda #86|MMC5_PRG_ROM
 nop
 BankPRGA a
 plp
 lda B3Value
 rts
B3ImageSTA00:
 sta GuestNativeApu+0
 php
 inc GuestNativeDirty+0
 plp
 rts
B3ImageSTA01:
 sta GuestNativeApu+1
 php
 inc GuestNativeDirty+1
 plp
 rts
B3ImageSTA02X:
 sta GuestNativeApu+2,x
 php
 inc GuestNativeDirty+2,x
 plp
 rts
B3ImageSTA03X:
 sta GuestNativeApu+3,x
 php
 inc GuestNativeDirty+3,x
 plp
 rts
B3ImageSTA04:
 sta GuestNativeApu+4
 php
 inc GuestNativeDirty+4
 plp
 rts
B3ImageSTA06:
 sta GuestNativeApu+6
 php
 inc GuestNativeDirty+6
 plp
 rts
B3ImageSTA07:
 sta GuestNativeApu+7
 php
 inc GuestNativeDirty+7
 plp
 rts
B3ImageSTA08:
 sta GuestNativeApu+8
 php
 inc GuestNativeDirty+8
 plp
 rts
B3ImageSTA0C:
 sta GuestNativeApu+12
 php
 inc GuestNativeDirty+12
 plp
 rts
B3ImageSTA0E:
 sta GuestNativeApu+14
 php
 inc GuestNativeDirty+14
 plp
 rts
B3ImageSTA0F:
 sta GuestNativeApu+15
 php
 inc GuestNativeDirty+15
 plp
 rts
B3ImageSTX05:
 stx GuestNativeApu+5
 php
 inc GuestNativeDirty+5
 plp
 rts
B3SourceImage=XgLzHistory
B3SourceTimers=XgLzHistory+$40
B3SourceZp=XgAudioPtr
B3SourceZpImage=XgLzHistory+$50
B3SavedCpuZp=XgLzHistory+$56
B3Pending=XgAudioSelection
; Owned shared DMC value4 uses the existing priority byte only as lease marker.
; It is mutually exclusive with active CV3. Existing owners0..3 are unchanged.
.segment "SMB3_NATIVE_CORE"
.proc B3ExpandedRoutes
 cmp #18
 bcs ShipOrOther
 BankPRGA #86
 jmp B3MusicUpdate
ShipOrOther:
 bne Legacy
 lda VvVariant
 bne Legacy
 BankPRGA #.bank(GradiusAudioUpdate)
 jmp GradiusAudioUpdate
Legacy:jmp LmNativeMusicGate
.endproc
.proc B3HostMute
 lda #0
 sta GuestNativeEnable
 sta GuestCombinedEnable
 sta $4015
 sta BassDmcActive
 sta Cv3DmcPriority
 lda #$ff
 sta $5117
 rts
.endproc
.proc B3ResetImage
 jsr B3HostMute
 lda #0
 ldx #47
ClearImage:sta B3SourceImage,x
 dex
 bpl ClearImage
 ldx #10
ClearTimers:sta B3SourceTimers,x
 dex
 bpl ClearTimers
 ldx #31
ClearScratch:sta XgLzHistory+$6e0,x
 dex
 bpl ClearScratch
 ldx #5
ClearZp:sta B3SourceZpImage,x
 dex
 bpl ClearZp
 ldx #15
ClearApu:sta GuestNativeApu,x
 lda #1
 sta GuestNativeDirty,x
 lda #0
 dex
 bpl ClearApu
 rts
.endproc
.proc B3Borrow
 lda z:B3SourceZp+0
 sta B3SavedCpuZp+0
 lda B3SourceZpImage+0
 sta z:B3SourceZp+0
 lda z:B3SourceZp+1
 sta B3SavedCpuZp+1
 lda B3SourceZpImage+1
 sta z:B3SourceZp+1
 lda z:B3SourceZp+2
 sta B3SavedCpuZp+2
 lda B3SourceZpImage+2
 sta z:B3SourceZp+2
 lda z:B3SourceZp+3
 sta B3SavedCpuZp+3
 lda B3SourceZpImage+3
 sta z:B3SourceZp+3
 lda z:B3SourceZp+4
 sta B3SavedCpuZp+4
 lda B3SourceZpImage+4
 sta z:B3SourceZp+4
 lda z:B3SourceZp+5
 sta B3SavedCpuZp+5
 lda B3SourceZpImage+5
 sta z:B3SourceZp+5
 rts
.endproc
.proc B3Restore
 lda z:B3SourceZp+0
 sta B3SourceZpImage+0
 lda B3SavedCpuZp+0
 sta z:B3SourceZp+0
 lda z:B3SourceZp+1
 sta B3SourceZpImage+1
 lda B3SavedCpuZp+1
 sta z:B3SourceZp+1
 lda z:B3SourceZp+2
 sta B3SourceZpImage+2
 lda B3SavedCpuZp+2
 sta z:B3SourceZp+2
 lda z:B3SourceZp+3
 sta B3SourceZpImage+3
 lda B3SavedCpuZp+3
 sta z:B3SourceZp+3
 lda z:B3SourceZp+4
 sta B3SourceZpImage+4
 lda B3SavedCpuZp+4
 sta z:B3SourceZp+4
 lda z:B3SourceZp+5
 sta B3SourceZpImage+5
 lda B3SavedCpuZp+5
 sta z:B3SourceZp+5
 rts
.endproc
; Same-bank software cleanup before genuine vanilla SoundEngine.
.segment "SMB3_VANILLA_GATE"
.proc B3VanillaMusicGate
 php
 lda XgAudioCharacter
 cmp #$fa
 bne CheckOwner
 lda #$ff
 sta XgAudioCharacter
CheckOwner:lda BassDmcActive
 cmp #4
 bne Done
 lda #0
 sta $4015
 sta BassDmcActive
 sta Cv3DmcPriority
 sta $4011
 lda #$ff
 sta $5117
Done:plp
 jmp SoundEngine
.endproc
.assert *<=$c000,lderror,"Only verified bank5 tail after Sophia cold"

.segment "SMB3_NATIVE_CORE"
B3Hot6E2E5:
 lda #93|MMC5_PRG_ROM
 BankPRGA a
 lda $b329,y
 rts
B3Hot6E2EE:
 lda #93|MMC5_PRG_ROM
 BankPRGA a
 lda $b309,y
 rts
B3Hot6E2F4:
 lda #93|MMC5_PRG_ROM
 BankPRGA a
 lda $b319,y
 rts
B3Hot6E345:
 lda #93|MMC5_PRG_ROM
 BankPRGA a
 lda $b874,y
 rts
B3Hot6E6E5:
 lda #93|MMC5_PRG_ROM
 BankPRGA a
 lda $b74a,y
 rts
B3Hot6E6EB:
 lda #93|MMC5_PRG_ROM
 BankPRGA a
 lda $b74e,y
 rts
B3Hot6E6F1:
 lda #93|MMC5_PRG_ROM
 BankPRGA a
 lda $b752,y
 rts
B3Hot6E792:
 lda #93|MMC5_PRG_ROM
 BankPRGA a
 lda $b765,x
 rts
B3Hot6E797:
 lda #93|MMC5_PRG_ROM
 BankPRGA a
 lda $b766,x
 rts
B3Hot6E79E:
 lda #93|MMC5_PRG_ROM
 BankPRGA a
 lda $b775,x
 rts
B3Hot6E7A3:
 lda #93|MMC5_PRG_ROM
 BankPRGA a
 lda $b776,x
 rts
B3Hot6E7DD:
 lda #93|MMC5_PRG_ROM
 BankPRGA a
 lda $b839,y
 rts
B3Hot6E7E2:
 lda #93|MMC5_PRG_ROM
 BankPRGA a
 lda $b83a,y
 rts
B3Hot6Play:
 jsr B3SourceA000
 php
 pha
 lda #86|MMC5_PRG_ROM
 BankPRGA a
 pla
 plp
 rts
B3CoreEnd:
.assert B3CoreEnd<=$dfe8,lderror,"SMB3 native core exceeds actual5120B free C38 span"
.segment "SMB3_NATIVE_COLD"
B3ColdStart:
.assert B3ColdStart=$a800,lderror,"SMB3 cold bridge verified86 gap"
B3StandaloneCold:
 php
 pha
 phx
 phy
 ldx #7
B3ResetMaps:
 lda B3InitialMaps,x
 sta B3VirtualMaps,x
 dex
 bpl B3ResetMaps
 lda #0
 sta B3Source4012
 sta B3Source4015
 sta B3PendingClone
 sta B3ActiveClone
 ply
 plx
 pla
 plp
 jmp B3Source9000
B3InitialMaps:
 .byte 7,0,1,2,5,6,3,4
B3Source9000:
 TAX
B3Source9001:
 jsr B3Known9001
 nop
 nop
B3Source9004:
 sta B3VirtualMaps+4
B3Source9007:
 CLC
B3Source9008:
 ADC #$01
B3Source900A:
 sta B3VirtualMaps+5
B3Source900D:
 jsr B3Known900D
 nop
 nop
B3Source9010:
 TAY
B3Source9011:
 jsr B3Known9011
 nop
 nop
B3Source9014:
 STA B3SourceImage+$20,Y
B3Source9017:
 jsr B3Known9017
 nop
 nop
B3Source901A:
 STA $7af7
B3Source901D:
 RTS
.segment "SMB3_NATIVE_COLD"

.proc B3MusicUpdate
 lda #0
 sta RgAudioRequest
 lda XgAudioCharacter
 cmp #$fa
 beq Initialized
 lda #$fa
 sta XgAudioCharacter
 lda #0
 sta RgAudioSilenced
 lda #9
 sta B3Pending
Initialized:
 lda AreaMusicQueue
 ora EventMusicQueue
 and #Silence
 beq Area
 lda #1
 sta RgAudioSilenced
Area:lda AreaMusicQueue
 and #$7f
 beq Event
 ldx #0
FindArea:lsr
 bcs AreaFound
 inx
 bne FindArea
AreaFound:lda Areas,x
 sta B3Pending
 lda #0
 sta RgAudioSilenced
Event:lda EventMusicQueue
 and #$7f
 beq Pause
 ldx #0
FindEvent:lsr
 bcs EventFound
 inx
 bne FindEvent
EventFound:lda Events,x
 sta B3Pending
 lda #0
 sta RgAudioSilenced
Pause:lda GamePauseStatus
 and #1
 bne Mute
 lda RgAudioSilenced
 bne Mute
 lda B3Pending
 bne Restart
 ; Restore held ordinary voices after pause; never fabricate a DMC retrigger.
 lda B3Source4015
 and #15
 sta GuestNativeEnable
 jsr B3Borrow
 lda #0
 ldx #0
 ldy #0
 jsr B3Hot6Play
 jsr B3Restore
 jmp Queues
Restart:sta RgAudioSong
 inc XgAudioSong
 jsr B3ResetImage
 jsr B3Borrow
 lda RgAudioSong
 sec
 sbc #1
 ldx #0
 ldy #0
 jsr B3StandaloneCold
 jsr B3Restore
 lda #0
 sta B3Pending
 jmp Queues
Mute:jsr B3HostMute
Queues:lda #0
 sta AreaMusicQueue
 sta EventMusicQueue
 sta Square1SoundQueue
 sta Square2SoundQueue
 sta NoiseSoundQueue
 rts
Areas:.byte 9,11,12,23,14,1,13
Events:.byte 43,42,39,39,42,38,27
.endproc
B3ColdEnd:
.assert B3ColdEnd<=$aa00,lderror,"SMB3 cold pool exceeds512B"
.popseg
.endif
