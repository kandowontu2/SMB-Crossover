; Actual original instructions projected from ce2f8461. Generated, not guessed.
.pushseg
.segment "GIMMICK_CORE"
GmN30_8000:
 lda GmRam0090 ;30:8000 a590
GmN30_8002:
 cmp #$d0 ;30:8002 c9d0
GmN30_8004:
 jcc GmN30_8026 ;30:8004 9020
GmN30_8006:
 lda GmRam0091 ;30:8006 a591
GmN30_8008:
 jpl GmN30_8025 ;30:8008 101b
GmN30_800A:
 cmp #$d0 ;30:800A c9d0
GmN30_800C:
 jcs GmN30_8025 ;30:800C b017
GmN30_800E:
 cmp #$a0 ;30:800E c9a0
GmN30_8010:
 jcc GmN30_801F ;30:8010 900d
GmN30_8012:
 lda #$d0 ;30:8012 a9d0
GmN30_8014:
 sta GmRam0091 ;30:8014 8591
GmN30_8016:
 lda #$00 ;30:8016 a900
GmN30_8018:
 sta GmRam038D ;30:8018 8d8d03
GmN30_801B:
 sta GmRam0351 ;30:801B 8d5103
GmN30_801E:
 rts ;30:801E 60
GmN30_801F:
 lda #$00 ;30:801F a900
GmN30_8021:
 sta GmRam0091 ;30:8021 8591
GmN30_8023:
 sta GmRam00D7 ;30:8023 85d7
GmN30_8025:
 rts ;30:8025 60
GmN30_8026:
 lda SavedJoypadBits ;30:8026 a5f7
GmN30_8028:
 and #$40 ;30:8028 2940
GmN30_802A:
 jne GmN30_8031 ;30:802A d005
GmN30_802C:
 sta GmRam0055 ;30:802C 8555
GmN30_802E:
 jmp GmN30_8094 ;30:802E 4c9480
GmN30_8031:
 lda GmRam0055 ;30:8031 a555
GmN30_8033:
 jeq GmN30_8037 ;30:8033 f002
GmN30_8035:
 dec GmRam0055 ;30:8035 c655
GmN30_8037:
 lda SavedJoypadBits ;30:8037 a5f7
GmN30_8039:
 and #$08 ;30:8039 2908
GmN30_803B:
 jeq GmN30_8094 ;30:803B f057
GmN30_803D:
 lda GmRam0036 ;30:803D a536
GmN30_803F:
 jsr GmInventoryJump
 .word GmN30_804A,GmN30_804D,GmN30_807F,GmN30_808B
GmN30_804A:
 jmp GmN30_8094
GmN30_804D:
 lda GmFresh ;30:804D a5f5
GmN30_804F:
 and #$40 ;30:804F 2940
GmN30_8051:
 jeq GmN30_8094 ;30:8051 f041
GmN30_8053:
 lda GmRam0039 ;30:8053 a539
GmN30_8055:
 cmp #$03 ;30:8055 c903
GmN30_8057:
 jeq GmN30_8060 ;30:8057 f007
GmN30_8059:
 lda GmRam002B ;30:8059 a52b
GmN30_805B:
 cmp GmRam0346 ;30:805B cd4603
GmN30_805E:
 jeq GmN30_8094 ;30:805E f034
GmN30_8060:
 lda #$1c ;30:8060 a91c
GmN30_8062:
 jsr GmQueueSound ;30:8062 2085f2
GmN30_8065:
 lda #$50 ;30:8065 a950
GmN30_8067:
 sta GmRam0055 ;30:8067 8555
GmN30_8069:
 lda GmRam002B ;30:8069 a52b
GmN30_806B:
 sta GmRam0346 ;30:806B 8d4603
GmN30_806E:
 lda GmRam0037 ;30:806E a537
GmN30_8070:
 sta GmRam0036 ;30:8070 8536
GmN30_8072:
 lda GmRam0038 ;30:8072 a538
GmN30_8074:
 sta GmRam0037 ;30:8074 8537
GmN30_8076:
 lda #$00 ;30:8076 a900
GmN30_8078:
 sta GmRam0038 ;30:8078 8538
GmN30_807A:
 dec GmRam0039 ;30:807A c639
GmN30_807C:
 jmp GmN30_8094 ;30:807C 4c9480
GmN30_807F:
 lda GmRam0091 ;30:807F a591
GmN30_8081:
 jne GmN30_8094 ;30:8081 d011
GmN30_8083:
 lda #$01 ;30:8083 a901
GmN30_8085:
 sta GmRam0351 ;30:8085 8d5103
GmN30_8088:
 jmp GmN30_8094 ;30:8088 4c9480
GmN30_808B:
 lda GmRam0091 ;30:808B a591
GmN30_808D:
 jne GmN30_8094 ;30:808D d005
GmN30_808F:
 lda #$02 ;30:808F a902
GmN30_8091:
 sta GmRam0351 ;30:8091 8d5103
GmN30_8094:
 lda GmFresh ;30:8094 a5f5
GmN30_8096:
 and #$04 ;30:8096 2904
GmN30_8098:
 jeq GmN30_80CE ;30:8098 f034
GmN30_809A:
 lda GmRam0091 ;30:809A a591
GmN30_809C:
 jpl GmN30_80A2 ;30:809C 1004
GmN30_809E:
 cmp #$d0 ;30:809E c9d0
GmN30_80A0:
 jcc GmN30_80CE ;30:80A0 902c
GmN30_80A2:
 lda GmRam0039 ;30:80A2 a539
GmN30_80A4:
 cmp #$02 ;30:80A4 c902
GmN30_80A6:
 jcc GmN30_80CE ;30:80A6 9026
GmN30_80A8:
 jne GmN30_80B9 ;30:80A8 d00f
GmN30_80AA:
 lda GmRam0036 ;30:80AA a536
GmN30_80AC:
 sta R0 ;30:80AC 8500
GmN30_80AE:
 lda GmRam0037 ;30:80AE a537
GmN30_80B0:
 sta GmRam0036 ;30:80B0 8536
GmN30_80B2:
 lda R0 ;30:80B2 a500
GmN30_80B4:
 sta GmRam0037 ;30:80B4 8537
GmN30_80B6:
 jmp GmN30_80C9 ;30:80B6 4cc980
GmN30_80B9:
 lda GmRam0036 ;30:80B9 a536
GmN30_80BB:
 sta R0 ;30:80BB 8500
GmN30_80BD:
 lda GmRam0037 ;30:80BD a537
GmN30_80BF:
 sta GmRam0036 ;30:80BF 8536
GmN30_80C1:
 lda GmRam0038 ;30:80C1 a538
GmN30_80C3:
 sta GmRam0037 ;30:80C3 8537
GmN30_80C5:
 lda R0 ;30:80C5 a500
GmN30_80C7:
 sta GmRam0038 ;30:80C7 8538
GmN30_80C9:
 lda #$14 ;30:80C9 a914
GmN30_80CB:
 jsr GmQueueSound ;30:80CB 2085f2
GmN30_80CE:
 lda GmRam0090 ;30:80CE a590
GmN30_80D0:
 cmp #$02 ;30:80D0 c902
GmN30_80D2:
 jne GmN30_80E4 ;30:80D2 d010
GmN30_80D4:
 lda #$20 ;30:80D4 a920
GmN30_80D6:
 sta GmRam03C8 ;30:80D6 8dc803
GmN30_80D9:
 ldx #$00 ;30:80D9 a200
GmN30_80DB:
 jsr GmScriptedCall ;30:80DB 206dfd
GmN30_80DE:
 lda #$15 ;30:80DE a915
GmN30_80E0:
 sta GmRam0300 ;30:80E0 8d0003
GmN30_80E3:
 rts ;30:80E3 60
GmN30_80E4:
 ldx #$00 ;30:80E4 a200
GmN30_80E6:
 stx GmTickSlot ;30:80E6 8619
GmN30_80E8:
 lda #$01 ;30:80E8 a901
GmN30_80EA:
 sta GmRam0090 ;30:80EA 8590
GmN30_80EC:
 lda GmClock ;30:80EC a5ed
GmN30_80EE:
 and #$dc ;30:80EE 29dc
GmN30_80F0:
 jne GmN30_80F3 ;30:80F0 d001
GmN30_80F2:
 inx ;30:80F2 e8
GmN30_80F3:
 stx GmRam0300 ;30:80F3 8e0003
GmN30_80F6:
 ldy #0
 jmp GmN30_8132
GmN30_8132:
 lda GmRam038C ;30:8132 ad8c03
GmN30_8135:
 cmp #$66 ;30:8135 c966
GmN30_8137:
 jcc GmN30_8149 ;30:8137 9010
GmN30_8139:
 lda GmRam0091 ;30:8139 a591
GmN30_813B:
 cmp #$03 ;30:813B c903
GmN30_813D:
 jcc GmN30_8146 ;30:813D 9007
GmN30_813F:
 cmp #$d0 ;30:813F c9d0
GmN30_8141:
 jcs GmN30_8146 ;30:8141 b003
GmN30_8143:
 jmp GmN30_81FB ;30:8143 4cfb81
GmN30_8146:
 jmp GmN30_82A1 ;30:8146 4ca182
GmN30_8149:
 lda #$02 ;30:8149 a902
GmN30_814B:
 sta R0 ;30:814B 8500
GmN30_814D:
 lda GmRam035A ;30:814D ad5a03
GmN30_8150:
 and #$7f ;30:8150 297f
GmN30_8152:
 cmp #$07 ;30:8152 c907
GmN30_8154:
 jne GmN30_815C ;30:8154 d006
GmN30_8156:
 lda GmClock ;30:8156 a5ed
GmN30_8158:
 and #$01 ;30:8158 2901
GmN30_815A:
 sta R0 ;30:815A 8500
GmN30_815C:
 lda SavedJoypadBits ;30:815C a5f7
GmN30_815E:
 and #$01 ;30:815E 2901
GmN30_8160:
 jeq GmN30_8170 ;30:8160 f00e
GmN30_8162:
 sta GmRam030A ;30:8162 8d0a03
GmN30_8165:
 lda GmRam00CC ;30:8165 a5cc
GmN30_8167:
 cmp #$17 ;30:8167 c917
GmN30_8169:
 jpl GmN30_8170 ;30:8169 1005
GmN30_816B:
 clc ;30:816B 18
GmN30_816C:
 adc R0 ;30:816C 6500
GmN30_816E:
 sta GmRam00CC ;30:816E 85cc
GmN30_8170:
 lda SavedJoypadBits ;30:8170 a5f7
GmN30_8172:
 and #$02 ;30:8172 2902
GmN30_8174:
 jeq GmN30_8186 ;30:8174 f010
GmN30_8176:
 lda #$00 ;30:8176 a900
GmN30_8178:
 sta GmRam030A ;30:8178 8d0a03
GmN30_817B:
 lda GmRam00CC ;30:817B a5cc
GmN30_817D:
 cmp #$e9 ;30:817D c9e9
GmN30_817F:
 jmi GmN30_8186 ;30:817F 3005
GmN30_8181:
 sec ;30:8181 38
GmN30_8182:
 sbc R0 ;30:8182 e500
GmN30_8184:
 sta GmRam00CC ;30:8184 85cc
GmN30_8186:
 lda GmRam0053 ;30:8186 a553
GmN30_8188:
 jmi GmN30_8194 ;30:8188 300a
GmN30_818A:
 lda GmRam036E ;30:818A ad6e03
GmN30_818D:
 jpl GmN30_8194 ;30:818D 1005
GmN30_818F:
 lda #$0f ;30:818F a90f
GmN30_8191:
 jsr GmQueueSound ;30:8191 2085f2
GmN30_8194:
 lda GmRam036E ;30:8194 ad6e03
GmN30_8197:
 sta GmRam0053 ;30:8197 8553
GmN30_8199:
 lda GmFresh ;30:8199 a5f5
GmN30_819B:
 and GmRam036E ;30:819B 2d6e03
GmN30_819E:
 jeq GmN30_81AB ;30:819E f00b
GmN30_81A0:
 lda #$ac ;30:81A0 a9ac
GmN30_81A2:
 sta GmRam00C2 ;30:81A2 85c2
GmN30_81A4:
 sta GmRam004B ;30:81A4 854b
GmN30_81A6:
 lda #$0d ;30:81A6 a90d
GmN30_81A8:
 jsr GmQueueSound ;30:81A8 2085f2
GmN30_81AB:
 lda GmRam004B ;30:81AB a54b
GmN30_81AD:
 jeq GmN30_81C3 ;30:81AD f014
GmN30_81AF:
 lda SavedJoypadBits ;30:81AF a5f7
GmN30_81B1:
 jmi GmN30_81C3 ;30:81B1 3010
GmN30_81B3:
 lda GmRam00C2 ;30:81B3 a5c2
GmN30_81B5:
 jpl GmN30_81BF ;30:81B5 1008
GmN30_81B7:
 cmp #$e8 ;30:81B7 c9e8
GmN30_81B9:
 jpl GmN30_81BF ;30:81B9 1004
GmN30_81BB:
 lda #$e8 ;30:81BB a9e8
GmN30_81BD:
 sta GmRam00C2 ;30:81BD 85c2
GmN30_81BF:
 lda #$00 ;30:81BF a900
GmN30_81C1:
 sta GmRam004B ;30:81C1 854b
GmN30_81C3:
 lda GmRam0091 ;30:81C3 a591
GmN30_81C5:
 cmp #$01 ;30:81C5 c901
GmN30_81C7:
 jeq GmN30_81F8 ;30:81C7 f02f
GmN30_81C9:
 cmp #$02 ;30:81C9 c902
GmN30_81CB:
 jeq GmN30_81F8 ;30:81CB f02b
GmN30_81CD:
 cmp #$d0 ;30:81CD c9d0
GmN30_81CF:
 jcs GmN30_81F8 ;30:81CF b027
GmN30_81D1:
 lda GmRam03C8 ;30:81D1 adc803
GmN30_81D4:
 jne GmN30_81FB ;30:81D4 d025
GmN30_81D6:
 lda GmRam0055 ;30:81D6 a555
GmN30_81D8:
 jne GmN30_81FB ;30:81D8 d021
GmN30_81DA:
 lda SavedJoypadBits ;30:81DA a5f7
GmN30_81DC:
 and #$40 ;30:81DC 2940
GmN30_81DE:
 jeq GmN30_81FB ;30:81DE f01b
GmN30_81E0:
 lda GmRam0091 ;30:81E0 a591
GmN30_81E2:
 jne GmN30_81F2 ;30:81E2 d00e
GmN30_81E4:
 lda #$10 ;30:81E4 a910
GmN30_81E6:
 jsr GmQueueSound ;30:81E6 2085f2
GmN30_81E9:
 lda #$7f ;30:81E9 a97f
GmN30_81EB:
 sta GmRam0091 ;30:81EB 8591
GmN30_81ED:
 lda #$00 ;30:81ED a900
GmN30_81EF:
 sta GmRam030B ;30:81EF 8d0b03
GmN30_81F2:
 cmp #$a9 ;30:81F2 c9a9
GmN30_81F4:
 jeq GmN30_81F8 ;30:81F4 f002
GmN30_81F6:
 inc GmRam0091 ;30:81F6 e691
GmN30_81F8:
 jmp GmN30_82A1 ;30:81F8 4ca182
GmN30_81FB:
 lda GmRam0091 ;30:81FB a591
GmN30_81FD:
 cmp #$a0 ;30:81FD c9a0
GmN30_81FF:
 jcs GmN30_820D ;30:81FF b00c
GmN30_8201:
 lda #$00 ;30:8201 a900
GmN30_8203:
 sta GmRam0091 ;30:8203 8591
GmN30_8205:
 sta GmRam00D7 ;30:8205 85d7
GmN30_8207:
 sta GmRam0351 ;30:8207 8d5103
GmN30_820A:
 jmp GmN30_82A1 ;30:820A 4ca182
GmN30_820D:
 ldy #$00 ;30:820D a000
GmN30_820F:
 sty GmRam0379 ;30:820F 8c7903
GmN30_8212:
 sty GmRam036F ;30:8212 8c6f03
GmN30_8215:
 sty GmRam038D ;30:8215 8c8d03
GmN30_8218:
 sty GmRam0035 ;30:8218 8435
GmN30_821A:
 sty GmRam0333 ;30:821A 8c3303
GmN30_821D:
 iny ;30:821D c8
GmN30_821E:
 sty GmRam0091 ;30:821E 8491
GmN30_8220:
 ldy GmRam0351 ;30:8220 ac5103
GmN30_8223:
 jeq GmN30_8233 ;30:8223 f00e
GmN30_8225:
 lda GmRam0037 ;30:8225 a537
GmN30_8227:
 sta GmRam0036 ;30:8227 8536
GmN30_8229:
 lda GmRam0038 ;30:8229 a538
GmN30_822B:
 sta GmRam0037 ;30:822B 8537
GmN30_822D:
 lda #$00 ;30:822D a900
GmN30_822F:
 sta GmRam0038 ;30:822F 8538
GmN30_8231:
 dec GmRam0039 ;30:8231 c639
GmN30_8233:
 lda GmN30_8608,y ;30:8233 b90886
GmN30_8236:
 jsr GmQueueSound ;30:8236 2085f2
GmN30_8239:
 lda GmRam00B8 ;30:8239 a5b8
GmN30_823B:
 sta GmRam00B9 ;30:823B 85b9
GmN30_823D:
 lda GmRam00AE ;30:823D a5ae
GmN30_823F:
 sta GmRam00AF ;30:823F 85af
GmN30_8241:
 lda GmRam009A ;30:8241 a59a
GmN30_8243:
 sec ;30:8243 38
GmN30_8244:
 sbc GmN30_83E9,y ;30:8244 f9e983
GmN30_8247:
 sta GmRam009B ;30:8247 859b
GmN30_8249:
 lda GmRam00A4 ;30:8249 a5a4
GmN30_824B:
 sbc GmN30_83EC,y ;30:824B f9ec83
GmN30_824E:
 sta GmRam00A5 ;30:824E 85a5
GmN30_8250:
 lda GmN30_83EF,y ;30:8250 b9ef83
GmN30_8253:
 sta GmRam0315 ;30:8253 8d1503
GmN30_8256:
 lda GmN30_83F2,y ;30:8256 b9f283
GmN30_8259:
 sta GmRam031F ;30:8259 8d1f03
GmN30_825C:
 lda #$70 ;30:825C a970
GmN30_825E:
 sta GmRam0329 ;30:825E 8d2903
GmN30_8261:
 lda #$20 ;30:8261 a920
GmN30_8263:
 sta GmRam033D ;30:8263 8d3d03
GmN30_8266:
 lda GmRam030A ;30:8266 ad0a03
GmN30_8269:
 sta GmRam030B ;30:8269 8d0b03
GmN30_826C:
 lda GmRam0351 ;30:826C ad5103
GmN30_826F:
 cmp #$01 ;30:826F c901
GmN30_8271:
 jne GmN30_8278 ;30:8271 d005
GmN30_8273:
 lda #$00 ;30:8273 a900
GmN30_8275:
 jmp GmN30_827D ;30:8275 4c7d82
GmN30_8278:
 lda GmRam00C2 ;30:8278 a5c2
GmN30_827A:
 cmp #$7f ;30:827A c97f
GmN30_827C:
 ror a ;30:827C 6a
GmN30_827D:
 clc ;30:827D 18
GmN30_827E:
 adc GmN30_83DE,y ;30:827E 79de83
GmN30_8281:
 jvc GmN30_8285 ;30:8281 5002
GmN30_8283:
 lda #$7f ;30:8283 a97f
GmN30_8285:
 sta GmRam00C3 ;30:8285 85c3
GmN30_8287:
 sta GmRam0397 ;30:8287 8d9703
GmN30_828A:
 lda GmRam030A ;30:828A ad0a03
GmN30_828D:
 asl a ;30:828D 0a
GmN30_828E:
 asl a ;30:828E 0a
GmN30_828F:
 adc GmRam0351 ;30:828F 6d5103
GmN30_8292:
 tay ;30:8292 a8
GmN30_8293:
 lda GmRam00CC ;30:8293 a5cc
GmN30_8295:
 cmp #$7f ;30:8295 c97f
GmN30_8297:
 ror a ;30:8297 6a
GmN30_8298:
 clc ;30:8298 18
GmN30_8299:
 adc GmN30_83E1,y ;30:8299 79e183
GmN30_829C:
 sta GmRam00CD ;30:829C 85cd
GmN30_829E:
 sta GmRam03A1 ;30:829E 8da103
GmN30_82A1:
 lda GmRam035A ;30:82A1 ad5a03
GmN30_82A4:
 cmp #$88 ;30:82A4 c988
GmN30_82A6:
 jeq GmN30_82AE ;30:82A6 f006
GmN30_82A8:
 and #$7f ;30:82A8 297f
GmN30_82AA:
 cmp #$07 ;30:82AA c907
GmN30_82AC:
 jne GmN30_82B9 ;30:82AC d00b
GmN30_82AE:
 lda SavedJoypadBits ;30:82AE a5f7
GmN30_82B0:
 and #$03 ;30:82B0 2903
GmN30_82B2:
 jeq GmN30_82EA ;30:82B2 f036
GmN30_82B4:
 lda #$02 ;30:82B4 a902
GmN30_82B6:
 jmp GmN30_82D5 ;30:82B6 4cd582
GmN30_82B9:
 lda GmRam00CC ;30:82B9 a5cc
GmN30_82BB:
 jpl GmN30_82C2 ;30:82BB 1005
GmN30_82BD:
 lda #$00 ;30:82BD a900
GmN30_82BF:
 sec ;30:82BF 38
GmN30_82C0:
 sbc GmRam00CC ;30:82C0 e5cc
GmN30_82C2:
 cmp #$02 ;30:82C2 c902
GmN30_82C4:
 jcs GmN30_82D1 ;30:82C4 b00b
GmN30_82C6:
 ldx #$04 ;30:82C6 a204
GmN30_82C8:
 stx GmRam0382 ;30:82C8 8e8203
GmN30_82CB:
 lda SavedJoypadBits ;30:82CB a5f7
GmN30_82CD:
 and #$03 ;30:82CD 2903
GmN30_82CF:
 jeq GmN30_82EA ;30:82CF f019
GmN30_82D1:
 lsr a ;30:82D1 4a
GmN30_82D2:
 lsr a ;30:82D2 4a
GmN30_82D3:
 lsr a ;30:82D3 4a
GmN30_82D4:
 lsr a ;30:82D4 4a
GmN30_82D5:
 sec ;30:82D5 38
GmN30_82D6:
 adc GmRam0382 ;30:82D6 6d8203
GmN30_82D9:
 cmp #$3d ;30:82D9 c93d
GmN30_82DB:
 jcc GmN30_82E0 ;30:82DB 9003
GmN30_82DD:
 sec ;30:82DD 38
GmN30_82DE:
 sbc #$3d ;30:82DE e93d
GmN30_82E0:
 sta GmRam0382 ;30:82E0 8d8203
GmN30_82E3:
 tax ;30:82E3 aa
GmN30_82E4:
 lda GmN30_83A1,x ;30:82E4 bda183
GmN30_82E7:
 sta GmRam0300 ;30:82E7 8d0003
GmN30_82EA:
 ldx #$00 ;30:82EA a200
GmN30_82EC:
 jsr GmIntegrateCall
 rts
GmN30_83A1:
 .byte $02
GmN30_83A2:
 .byte $02
GmN30_83A3:
 .byte $02
GmN30_83A4:
 .byte $02
GmN30_83A5:
 .byte $02
GmN30_83A6:
 .byte $02
GmN30_83A7:
 .byte $02
GmN30_83A8:
 .byte $03
GmN30_83A9:
 .byte $03
GmN30_83AA:
 .byte $03
GmN30_83AB:
 .byte $03
GmN30_83AC:
 .byte $03
GmN30_83AD:
 .byte $03
GmN30_83AE:
 .byte $03
GmN30_83AF:
 .byte $03
GmN30_83B0:
 .byte $03
GmN30_83B1:
 .byte $03
GmN30_83B2:
 .byte $03
GmN30_83B3:
 .byte $03
GmN30_83B4:
 .byte $03
GmN30_83B5:
 .byte $03
GmN30_83B6:
 .byte $03
GmN30_83B7:
 .byte $03
GmN30_83B8:
 .byte $04
GmN30_83B9:
 .byte $04
GmN30_83BA:
 .byte $04
GmN30_83BB:
 .byte $04
GmN30_83BC:
 .byte $04
GmN30_83BD:
 .byte $04
GmN30_83BE:
 .byte $04
GmN30_83BF:
 .byte $05
GmN30_83C0:
 .byte $05
GmN30_83C1:
 .byte $05
GmN30_83C2:
 .byte $05
GmN30_83C3:
 .byte $05
GmN30_83C4:
 .byte $05
GmN30_83C5:
 .byte $05
GmN30_83C6:
 .byte $06
GmN30_83C7:
 .byte $06
GmN30_83C8:
 .byte $06
GmN30_83C9:
 .byte $06
GmN30_83CA:
 .byte $06
GmN30_83CB:
 .byte $06
GmN30_83CC:
 .byte $06
GmN30_83CD:
 .byte $06
GmN30_83CE:
 .byte $06
GmN30_83CF:
 .byte $06
GmN30_83D0:
 .byte $06
GmN30_83D1:
 .byte $06
GmN30_83D2:
 .byte $06
GmN30_83D3:
 .byte $06
GmN30_83D4:
 .byte $06
GmN30_83D5:
 .byte $06
GmN30_83D6:
 .byte $06
GmN30_83D7:
 .byte $07
GmN30_83D8:
 .byte $07
GmN30_83D9:
 .byte $07
GmN30_83DA:
 .byte $07
GmN30_83DB:
 .byte $07
GmN30_83DC:
 .byte $07
GmN30_83DD:
 .byte $07
GmN30_83DE:
 .byte $30
GmN30_83DF:
 .byte $00
GmN30_83E0:
 .byte $d0
GmN30_83E1:
 .byte $d8
GmN30_83E2:
 .byte $e8
GmN30_83E3:
 .byte $e4
GmN30_83E4:
 .byte $00
GmN30_83E5:
 .byte $28
GmN30_83E6:
 .byte $18
GmN30_83E7:
 .byte $1c
GmN30_83E8:
 .byte $00
GmN30_83E9:
 .byte $00
GmN30_83EA:
 .byte $80
GmN30_83EB:
 .byte $00
GmN30_83EC:
 .byte $01
GmN30_83ED:
 .byte $00
GmN30_83EE:
 .byte $01
GmN30_83EF:
 .byte $f0
GmN30_83F0:
 .byte $00
GmN30_83F1:
 .byte $e0
GmN30_83F2:
 .byte $00
GmN30_83F3:
 .byte $02
GmN30_83F4:
 .byte $00
GmN30_8608:
 .byte $13
GmN30_8609:
 .byte $44
GmN30_860A:
 .byte $13
.popseg
.pushseg
.segment "GIMMICK_CORE"
GmN29_8023:
 ldx #$01 ;29:8023 a201
GmN29_8025:
 stx GmTickSlot ;29:8025 8619
GmN29_8027:
 lda GmRam0091 ;29:8027 a591
GmN29_8029:
 cmp #$02 ;29:8029 c902
GmN29_802B:
 jne GmN29_8042 ;29:802B d015
GmN29_802D:
 lda #$20 ;29:802D a920
GmN29_802F:
 sta GmRam03C9 ;29:802F 8dc903
GmN29_8032:
 ldx #$01 ;29:8032 a201
GmN29_8034:
 jsr GmScriptedCall ;29:8034 206dfd
GmN29_8037:
 lda GmClock ;29:8037 a5ed
GmN29_8039:
 and #$01 ;29:8039 2901
GmN29_803B:
 ora GmRam03C9 ;29:803B 0dc903
GmN29_803E:
 sta GmRam03C9 ;29:803E 8dc903
GmN29_8041:
 rts ;29:8041 60
GmN29_8042:
 ldy #0
 jmp GmN29_8071
GmN29_8071:
 lda GmRam0091 ;29:8071 a591
GmN29_8073:
 jpl GmN29_80E7 ;29:8073 1072
GmN29_8075:
 cmp #$d1 ;29:8075 c9d1
GmN29_8077:
 jeq GmN29_80A4 ;29:8077 f02b
GmN29_8079:
 cmp #$d0 ;29:8079 c9d0
GmN29_807B:
 jeq GmN29_80CF ;29:807B f052
GmN29_807D:
 and #$7f ;29:807D 297f
GmN29_807F:
 tax ;29:807F aa
GmN29_8080:
 lda GmN29_8C33,x ;29:8080 bd338c
GmN29_8083:
 sta GmRam0301 ;29:8083 8d0103
GmN29_8086:
 lda GmRam00AE ;29:8086 a5ae
GmN29_8088:
 sta GmRam00AF ;29:8088 85af
GmN29_808A:
 lda GmRam00B8 ;29:808A a5b8
GmN29_808C:
 sta GmRam00B9 ;29:808C 85b9
GmN29_808E:
 lda GmRam009A ;29:808E a59a
GmN29_8090:
 sta GmRam009B ;29:8090 859b
GmN29_8092:
 lda GmRam00A4 ;29:8092 a5a4
GmN29_8094:
 sec ;29:8094 38
GmN29_8095:
 sbc #$01 ;29:8095 e901
GmN29_8097:
 sta GmRam00A5 ;29:8097 85a5
GmN29_8099:
 lda GmClock ;29:8099 a5ed
GmN29_809B:
 and #$01 ;29:809B 2901
GmN29_809D:
 ora GmRam03C9 ;29:809D 0dc903
GmN29_80A0:
 sta GmRam03C9 ;29:80A0 8dc903
GmN29_80A3:
 rts ;29:80A3 60
GmN29_80A4:
 lda #$00 ;29:80A4 a900
GmN29_80A6:
 sta GmRam00D7 ;29:80A6 85d7
GmN29_80A8:
 lda GmRam038D ;29:80A8 ad8d03
GmN29_80AB:
 lsr a ;29:80AB 4a
GmN29_80AC:
 lsr a ;29:80AC 4a
GmN29_80AD:
 clc ;29:80AD 18
GmN29_80AE:
 adc #$1b ;29:80AE 691b
GmN29_80B0:
 sta GmRam0301 ;29:80B0 8d0103
GmN29_80B3:
 inc GmRam038D ;29:80B3 ee8d03
GmN29_80B6:
 lda GmRam038D ;29:80B6 ad8d03
GmN29_80B9:
 cmp #$20 ;29:80B9 c920
GmN29_80BB:
 jeq GmN29_80BE ;29:80BB f001
GmN29_80BD:
 rts ;29:80BD 60
GmN29_80BE:
 lda #$00 ;29:80BE a900
GmN29_80C0:
 sta GmRam0091 ;29:80C0 8591
GmN29_80C2:
 sta GmRam0351 ;29:80C2 8d5103
GmN29_80C5:
 rts ;29:80C5 60
GmN29_80C6:
 lda #$d0 ;29:80C6 a9d0
GmN29_80C8:
 sta GmRam0091 ;29:80C8 8591
GmN29_80CA:
 lda #$00 ;29:80CA a900
GmN29_80CC:
 sta GmRam038D ;29:80CC 8d8d03
GmN29_80CF:
 lda #$00 ;29:80CF a900
GmN29_80D1:
 sta GmRam00D7 ;29:80D1 85d7
GmN29_80D3:
 ldy GmRam038D ;29:80D3 ac8d03
GmN29_80D6:
 lda GmN29_8C23,y ;29:80D6 b9238c
GmN29_80D9:
 sta GmRam0301 ;29:80D9 8d0103
GmN29_80DC:
 inc GmRam038D ;29:80DC ee8d03
GmN29_80DF:
 lda GmRam038D ;29:80DF ad8d03
GmN29_80E2:
 cmp #$10 ;29:80E2 c910
GmN29_80E4:
 jeq GmN29_80BE ;29:80E4 f0d8
GmN29_80E6:
 rts ;29:80E6 60
GmN29_80E7:
 jmp GmN29_8103
GmN29_8103:
 lda #$01 ;29:8103 a901
GmN29_8105:
 sta GmRam0091 ;29:8105 8591
GmN29_8107:
 lda GmRam0379 ;29:8107 ad7903
GmN29_810A:
 jpl GmN29_811A ;29:810A 100e
GmN29_810C:
 lda GmRam03A1 ;29:810C ada103
GmN29_810F:
 eor #$ff ;29:810F 49ff
GmN29_8111:
 clc ;29:8111 18
GmN29_8112:
 adc #$01 ;29:8112 6901
GmN29_8114:
 sta GmRam00CD ;29:8114 85cd
GmN29_8116:
 lda #$40 ;29:8116 a940
GmN29_8118:
 sta GmRam00D7 ;29:8118 85d7
GmN29_811A:
 lda GmRam00CD ;29:811A a5cd
GmN29_811C:
 sta GmRam03A1 ;29:811C 8da103
GmN29_811F:
 lda GmProperty+1
 bmi GmN29_80C6
GmN29_8124:
 lda GmRam00CD ;29:8124 a5cd
GmN29_8126:
 ora GmRam00C3 ;29:8126 05c3
GmN29_8128:
 jne GmN29_812D ;29:8128 d003
GmN29_812A:
 inc GmRam038D ;29:812A ee8d03
GmN29_812D:
 lda GmRam038D ;29:812D ad8d03
GmN29_8130:
 cmp #$08 ;29:8130 c908
GmN29_8132:
 jcs GmN29_80C6 ;29:8132 b092
GmN29_8134:
 lda GmRam036F ;29:8134 ad6f03
GmN29_8137:
 jpl GmN29_8151 ;29:8137 1018
GmN29_8139:
 lda GmRam0383 ;29:8139 ad8303
GmN29_813C:
 jmi GmN29_8143 ;29:813C 3005
GmN29_813E:
 lda #$15 ;29:813E a915
GmN29_8140:
 jsr GmQueueSound ;29:8140 2085f2
GmN29_8143:
 lda GmRam0397 ;29:8143 ad9703
GmN29_8146:
 eor #$ff ;29:8146 49ff
GmN29_8148:
 clc ;29:8148 18
GmN29_8149:
 adc #$09 ;29:8149 6909
GmN29_814B:
 sta GmRam00C3 ;29:814B 85c3
GmN29_814D:
 lda #$40 ;29:814D a940
GmN29_814F:
 sta GmRam00D7 ;29:814F 85d7
GmN29_8151:
 lda GmRam00C3 ;29:8151 a5c3
GmN29_8153:
 sta GmRam0397 ;29:8153 8d9703
GmN29_8156:
 lda GmRam036F ;29:8156 ad6f03
GmN29_8159:
 sta GmRam0383 ;29:8159 8d8303
GmN29_815C:
 ldx #$01 ;29:815C a201
GmN29_815E:
 jsr GmIntegrateCall ;29:815E 2096f5
GmN29_8161:
 lda #$14 ;29:8161 a914
GmN29_8163:
 sta GmRam0301 ;29:8163 8d0103
GmN29_8166:
 lda GmClock ;29:8166 a5ed
GmN29_8168:
 and #$01 ;29:8168 2901
GmN29_816A:
 ora GmRam03C9 ;29:816A 0dc903
GmN29_816D:
 sta GmRam03C9 ;29:816D 8dc903
GmN29_8170:
 rts ;29:8170 60
GmN29_8171:
 ldx #$01 ;29:8171 a201
GmN29_8173:
 stx GmTickSlot ;29:8173 8619
GmN29_8175:
 lda #$00 ;29:8175 a900
GmN29_8177:
 sta GmRam03C9 ;29:8177 8dc903
GmN29_817A:
 lda GmRam0091 ;29:817A a591
GmN29_817C:
 jpl GmN29_81E2 ;29:817C 1064
GmN29_817E:
 cmp #$d0 ;29:817E c9d0
GmN29_8180:
 jeq GmN29_81BE ;29:8180 f03c
GmN29_8182:
 cmp #$a9 ;29:8182 c9a9
GmN29_8184:
 jne GmN29_8191 ;29:8184 d00b
GmN29_8186:
 lda GmClock ;29:8186 a5ed
GmN29_8188:
 lsr a ;29:8188 4a
GmN29_8189:
 and #$03 ;29:8189 2903
GmN29_818B:
 clc ;29:818B 18
GmN29_818C:
 adc #$3d ;29:818C 693d
GmN29_818E:
 jmp GmN29_8197 ;29:818E 4c9781
GmN29_8191:
 and #$7f ;29:8191 297f
GmN29_8193:
 tay ;29:8193 a8
GmN29_8194:
 lda GmN29_8C5E,y ;29:8194 b95e8c
GmN29_8197:
 sta GmRam0301 ;29:8197 8d0103
GmN29_819A:
 lda GmRam00AE ;29:819A a5ae
GmN29_819C:
 sta GmRam00AF ;29:819C 85af
GmN29_819E:
 lda GmRam00B8 ;29:819E a5b8
GmN29_81A0:
 sta GmRam00B9 ;29:81A0 85b9
GmN29_81A2:
 lda GmRam009A ;29:81A2 a59a
GmN29_81A4:
 sta GmRam009B ;29:81A4 859b
GmN29_81A6:
 lda GmRam00A4 ;29:81A6 a5a4
GmN29_81A8:
 sec ;29:81A8 38
GmN29_81A9:
 sbc #$01 ;29:81A9 e901
GmN29_81AB:
 sta GmRam00A5 ;29:81AB 85a5
GmN29_81AD:
 lda GmRam0091 ;29:81AD a591
GmN29_81AF:
 cmp #$9e ;29:81AF c99e
GmN29_81B1:
 jcs GmN29_81BD ;29:81B1 b00a
GmN29_81B3:
 lda GmClock ;29:81B3 a5ed
GmN29_81B5:
 and #$01 ;29:81B5 2901
GmN29_81B7:
 ora GmRam03C9 ;29:81B7 0dc903
GmN29_81BA:
 sta GmRam03C9 ;29:81BA 8dc903
GmN29_81BD:
 rts ;29:81BD 60
GmN29_81BE:
 lda #$00 ;29:81BE a900
GmN29_81C0:
 sta GmRam00D7 ;29:81C0 85d7
GmN29_81C2:
 jsr GmN29_8D5C ;29:81C2 205c8d
GmN29_81C5:
 lda GmRam038D ;29:81C5 ad8d03
GmN29_81C8:
 lsr a ;29:81C8 4a
GmN29_81C9:
 clc ;29:81C9 18
GmN29_81CA:
 adc #$35 ;29:81CA 6935
GmN29_81CC:
 sta GmRam0301 ;29:81CC 8d0103
GmN29_81CF:
 inc GmRam038D ;29:81CF ee8d03
GmN29_81D2:
 lda GmRam038D ;29:81D2 ad8d03
GmN29_81D5:
 cmp #$10 ;29:81D5 c910
GmN29_81D7:
 jeq GmN29_81DA ;29:81D7 f001
GmN29_81D9:
 rts ;29:81D9 60
GmN29_81DA:
 lda #$00 ;29:81DA a900
GmN29_81DC:
 sta GmRam0091 ;29:81DC 8591
GmN29_81DE:
 sta GmRam0351 ;29:81DE 8d5103
GmN29_81E1:
 rts ;29:81E1 60
GmN29_81E2:
 lda #$00 ;29:81E2 a900
GmN29_81E4:
 sta GmRam00D7 ;29:81E4 85d7
GmN29_81E6:
 lda #$01 ;29:81E6 a901
GmN29_81E8:
 sta GmRam0091 ;29:81E8 8591
GmN29_81EA:
 lda #$03 ;29:81EA a903
GmN29_81EC:
 ldy GmRam030B ;29:81EC ac0b03
GmN29_81EF:
 jne GmN29_81F3 ;29:81EF d002
GmN29_81F1:
 lda #$fd ;29:81F1 a9fd
GmN29_81F3:
 clc ;29:81F3 18
GmN29_81F4:
 adc GmRam00CD ;29:81F4 65cd
GmN29_81F6:
 jvs GmN29_81FA ;29:81F6 7002
GmN29_81F8:
 sta GmRam00CD ;29:81F8 85cd
GmN29_81FA:
 jsr GmN29_8D5C ;29:81FA 205c8d
GmN29_81FD:
 lda GmRam00CD ;29:81FD a5cd
GmN29_81FF:
 jpl GmN29_8203 ;29:81FF 1002
GmN29_8201:
 eor #$ff ;29:8201 49ff
GmN29_8203:
 clc ;29:8203 18
GmN29_8204:
 adc GmRam0397 ;29:8204 6d9703
GmN29_8207:
 sta GmRam0397 ;29:8207 8d9703
GmN29_820A:
 jcc GmN29_820F ;29:820A 9003
GmN29_820C:
 inc GmRam03A1 ;29:820C eea103
GmN29_820F:
 lda GmRam03A1 ;29:820F ada103
GmN29_8212:
 cmp #$0c ;29:8212 c90c
GmN29_8214:
 jcc GmN29_821B ;29:8214 9005
GmN29_8216:
 lda #$00 ;29:8216 a900
GmN29_8218:
 sta GmRam03A1 ;29:8218 8da103
GmN29_821B:
 clc ;29:821B 18
GmN29_821C:
 adc #$29 ;29:821C 6929
GmN29_821E:
 sta GmRam0301 ;29:821E 8d0103
GmN29_8221:
 jsr GmSpawnEffect
 rts
GmN29_82AB:
 ldx #$00 ;29:82AB a200
GmN29_82AD:
 stx GmRam030B ;29:82AD 8e0b03
GmN29_82B0:
 inx ;29:82B0 e8
GmN29_82B1:
 stx GmTickSlot ;29:82B1 8619
GmN29_82B3:
 lda GmRam0091 ;29:82B3 a591
GmN29_82B5:
 cmp #$02 ;29:82B5 c902
GmN29_82B7:
 jne GmN29_82C4 ;29:82B7 d00b
GmN29_82B9:
 lda #$20 ;29:82B9 a920
GmN29_82BB:
 sta GmRam03C9 ;29:82BB 8dc903
GmN29_82BE:
 ldx #$01 ;29:82BE a201
GmN29_82C0:
 jsr GmScriptedCall ;29:82C0 206dfd
GmN29_82C3:
 rts ;29:82C3 60
GmN29_82C4:
 ldy #0
 jmp GmN29_82F3
GmN29_82F3:
 lda GmRam0091 ;29:82F3 a591
GmN29_82F5:
 jmi GmN29_82FA ;29:82F5 3003
GmN29_82F7:
 jmp GmN29_83FC ;29:82F7 4cfc83
GmN29_82FA:
 cmp #$d1 ;29:82FA c9d1
GmN29_82FC:
 jne GmN29_8301 ;29:82FC d003
GmN29_82FE:
 jmp GmN29_80A4 ;29:82FE 4ca480
GmN29_8301:
 cmp #$d0 ;29:8301 c9d0
GmN29_8303:
 jeq GmN29_833B ;29:8303 f036
GmN29_8305:
 and #$7f ;29:8305 297f
GmN29_8307:
 tax ;29:8307 aa
GmN29_8308:
 lda GmN29_8C89,x ;29:8308 bd898c
GmN29_830B:
 sta GmRam0301 ;29:830B 8d0103
GmN29_830E:
 lda GmRam00AE ;29:830E a5ae
GmN29_8310:
 sta GmRam00AF ;29:8310 85af
GmN29_8312:
 lda GmRam00B8 ;29:8312 a5b8
GmN29_8314:
 sta GmRam00B9 ;29:8314 85b9
GmN29_8316:
 lda GmRam009A ;29:8316 a59a
GmN29_8318:
 sta GmRam009B ;29:8318 859b
GmN29_831A:
 lda GmRam00A4 ;29:831A a5a4
GmN29_831C:
 sec ;29:831C 38
GmN29_831D:
 sbc #$01 ;29:831D e901
GmN29_831F:
 sta GmRam00A5 ;29:831F 85a5
GmN29_8321:
 lda GmRam0091 ;29:8321 a591
GmN29_8323:
 cmp #$9e ;29:8323 c99e
GmN29_8325:
 jcs GmN29_8331 ;29:8325 b00a
GmN29_8327:
 lda GmClock ;29:8327 a5ed
GmN29_8329:
 and #$01 ;29:8329 2901
GmN29_832B:
 ora GmRam03C9 ;29:832B 0dc903
GmN29_832E:
 sta GmRam03C9 ;29:832E 8dc903
GmN29_8331:
 rts ;29:8331 60
GmN29_8332:
 lda #$d0 ;29:8332 a9d0
GmN29_8334:
 sta GmRam0091 ;29:8334 8591
GmN29_8336:
 lda #$00 ;29:8336 a900
GmN29_8338:
 sta GmRam038D ;29:8338 8d8d03
GmN29_833B:
 lda GmClock ;29:833B a5ed
GmN29_833D:
 and #$01 ;29:833D 2901
GmN29_833F:
 ora GmRam03C9 ;29:833F 0dc903
GmN29_8342:
 sta GmRam03C9 ;29:8342 8dc903
GmN29_8345:
 lda #$00 ;29:8345 a900
GmN29_8347:
 sta GmRam00D7 ;29:8347 85d7
GmN29_8349:
 ldy GmRam038D ;29:8349 ac8d03
GmN29_834C:
 jne GmN29_8353 ;29:834C d005
GmN29_834E:
 lda #$42 ;29:834E a942
GmN29_8350:
 jsr GmQueueSound ;29:8350 2085f2
GmN29_8353:
 lda GmN29_8D44,y ;29:8353 b9448d
GmN29_8356:
 sta GmRam0301 ;29:8356 8d0103
GmN29_8359:
 inc GmRam038D ;29:8359 ee8d03
GmN29_835C:
 lda GmRam038D ;29:835C ad8d03
GmN29_835F:
 cmp #$19 ;29:835F c919
GmN29_8361:
 jne GmN29_836B ;29:8361 d008
GmN29_8363:
 lda #$00 ;29:8363 a900
GmN29_8365:
 sta GmRam0091 ;29:8365 8591
GmN29_8367:
 sta GmRam0351 ;29:8367 8d5103
GmN29_836A:
 rts ;29:836A 60
GmN29_836B:
 lda GmN29_8CB4,y ;29:836B b9b48c
GmN29_836E:
 sta GmRam0329 ;29:836E 8d2903
GmN29_8371:
 lda GmN29_8CCC,y ;29:8371 b9cc8c
GmN29_8374:
 sta GmRam0333 ;29:8374 8d3303
GmN29_8377:
 lda GmN29_8CE4,y ;29:8377 b9e48c
GmN29_837A:
 sta GmRam0315 ;29:837A 8d1503
GmN29_837D:
 lda GmN29_8CFC,y ;29:837D b9fc8c
GmN29_8380:
 sta GmRam031F ;29:8380 8d1f03
GmN29_8383:
 lda GmRam009B ;29:8383 a59b
GmN29_8385:
 clc ;29:8385 18
GmN29_8386:
 adc GmN29_8D14,y ;29:8386 79148d
GmN29_8389:
 sta GmRam009B ;29:8389 859b
GmN29_838B:
 lda GmRam00A5 ;29:838B a5a5
GmN29_838D:
 adc GmN29_8D2C,y ;29:838D 792c8d
GmN29_8390:
 sta GmRam00A5 ;29:8390 85a5
GmN29_8392:
 jsr GmSpawnEffect
 rts
GmN29_83FC:
 jmp GmN29_840C
GmN29_8409:
 jmp GmN29_8332
GmN29_840C:
 lda #$40 ;29:840C a940
GmN29_840E:
 sta GmRam00D7 ;29:840E 85d7
GmN29_8410:
 lda #$01 ;29:8410 a901
GmN29_8412:
 sta GmRam0091 ;29:8412 8591
GmN29_8414:
 lda GmProperty+1
 bmi GmN29_8409
GmN29_8419:
 lda GmRam038D ;29:8419 ad8d03
GmN29_841C:
 cmp #$08 ;29:841C c908
GmN29_841E:
 jcs GmN29_8409 ;29:841E b0e9
GmN29_8420:
 lda GmRam036F ;29:8420 ad6f03
GmN29_8423:
 jpl GmN29_8450 ;29:8423 102b
GmN29_8425:
 lda GmRam0397 ;29:8425 ad9703
GmN29_8428:
 cmp #$7f ;29:8428 c97f
GmN29_842A:
 ror a ;29:842A 6a
GmN29_842B:
 eor #$ff ;29:842B 49ff
GmN29_842D:
 clc ;29:842D 18
GmN29_842E:
 adc #$01 ;29:842E 6901
GmN29_8430:
 sta GmRam00C3 ;29:8430 85c3
GmN29_8432:
 lda GmRam035B ;29:8432 ad5b03
GmN29_8435:
 jmi GmN29_8450 ;29:8435 3019
GmN29_8437:
 lda GmRam00CD ;29:8437 a5cd
GmN29_8439:
 jmi GmN29_8447 ;29:8439 300c
GmN29_843B:
 sec ;29:843B 38
GmN29_843C:
 sbc #$01 ;29:843C e901
GmN29_843E:
 jpl GmN29_8442 ;29:843E 1002
GmN29_8440:
 lda #$00 ;29:8440 a900
GmN29_8442:
 sta GmRam00CD ;29:8442 85cd
GmN29_8444:
 jmp GmN29_8450 ;29:8444 4c5084
GmN29_8447:
 clc ;29:8447 18
GmN29_8448:
 adc #$01 ;29:8448 6901
GmN29_844A:
 jmi GmN29_844E ;29:844A 3002
GmN29_844C:
 lda #$00 ;29:844C a900
GmN29_844E:
 sta GmRam00CD ;29:844E 85cd
GmN29_8450:
 lda GmRam00C3 ;29:8450 a5c3
GmN29_8452:
 sta GmRam0397 ;29:8452 8d9703
GmN29_8455:
 lda GmRam00CD ;29:8455 a5cd
GmN29_8457:
 ora GmRam00C3 ;29:8457 05c3
GmN29_8459:
 jne GmN29_845E ;29:8459 d003
GmN29_845B:
 inc GmRam038D ;29:845B ee8d03
GmN29_845E:
 ldx #$01 ;29:845E a201
GmN29_8460:
 jsr GmIntegrateCall ;29:8460 2096f5
GmN29_8463:
 lda #$41 ;29:8463 a941
GmN29_8465:
 sta GmRam0301 ;29:8465 8d0103
GmN29_8468:
 rts ;29:8468 60
GmN29_8D5C:
 ldy #$00 ;29:8D5C a000
GmN29_8D5E:
 lda GmRam00CC,x ;29:8D5E b5cc
GmN29_8D60:
 jpl GmN29_8D63 ;29:8D60 1001
GmN29_8D62:
 dey ;29:8D62 88
GmN29_8D63:
 sty R0 ;29:8D63 8400
GmN29_8D65:
 clc ;29:8D65 18
GmN29_8D66:
 adc GmRam00AE,x ;29:8D66 75ae
GmN29_8D68:
 sta GmRam00AE,x ;29:8D68 95ae
GmN29_8D6A:
 lda GmRam00B8,x ;29:8D6A b5b8
GmN29_8D6C:
 adc R0 ;29:8D6C 6500
GmN29_8D6E:
 sta GmRam00B8,x ;29:8D6E 95b8
GmN29_8D70:
 ldy #$00 ;29:8D70 a000
GmN29_8D72:
 lda GmRam00C2,x ;29:8D72 b5c2
GmN29_8D74:
 jpl GmN29_8D77 ;29:8D74 1001
GmN29_8D76:
 dey ;29:8D76 88
GmN29_8D77:
 sty R0 ;29:8D77 8400
GmN29_8D79:
 clc ;29:8D79 18
GmN29_8D7A:
 adc GmRam009A,x ;29:8D7A 759a
GmN29_8D7C:
 sta GmRam009A,x ;29:8D7C 959a
GmN29_8D7E:
 lda GmRam00A4,x ;29:8D7E b5a4
GmN29_8D80:
 adc R0 ;29:8D80 6500
GmN29_8D82:
 sta GmRam00A4,x ;29:8D82 95a4
GmN29_8D84:
 rts ;29:8D84 60
GmN29_828B:
 .byte $70
GmN29_828C:
 .byte $c0
GmN29_828D:
 .byte $20
GmN29_828E:
 .byte $80
GmN29_828F:
 .byte $a0
GmN29_8290:
 .byte $f0
GmN29_8291:
 .byte $90
GmN29_8292:
 .byte $30
GmN29_8293:
 .byte $ff
GmN29_8294:
 .byte $fe
GmN29_8295:
 .byte $fe
GmN29_8296:
 .byte $ff
GmN29_8297:
 .byte $fe
GmN29_8298:
 .byte $ff
GmN29_8299:
 .byte $ff
GmN29_829A:
 .byte $fe
GmN29_829B:
 .byte $90
GmN29_829C:
 .byte $90
GmN29_829D:
 .byte $c0
GmN29_829E:
 .byte $b0
GmN29_829F:
 .byte $60
GmN29_82A0:
 .byte $50
GmN29_82A1:
 .byte $20
GmN29_82A2:
 .byte $c0
GmN29_82A3:
 .byte $00
GmN29_82A4:
 .byte $ff
GmN29_82A5:
 .byte $00
GmN29_82A6:
 .byte $ff
GmN29_82A7:
 .byte $00
GmN29_82A8:
 .byte $00
GmN29_82A9:
 .byte $ff
GmN29_82AA:
 .byte $ff
GmN29_8C23:
 .byte $15
GmN29_8C24:
 .byte $15
GmN29_8C25:
 .byte $16
GmN29_8C26:
 .byte $16
GmN29_8C27:
 .byte $17
GmN29_8C28:
 .byte $17
GmN29_8C29:
 .byte $18
GmN29_8C2A:
 .byte $18
GmN29_8C2B:
 .byte $17
GmN29_8C2C:
 .byte $17
GmN29_8C2D:
 .byte $18
GmN29_8C2E:
 .byte $18
GmN29_8C2F:
 .byte $19
GmN29_8C30:
 .byte $19
GmN29_8C31:
 .byte $1a
GmN29_8C32:
 .byte $1a
GmN29_8C33:
 .byte $00
GmN29_8C34:
 .byte $00
GmN29_8C35:
 .byte $01
GmN29_8C36:
 .byte $01
GmN29_8C37:
 .byte $02
GmN29_8C38:
 .byte $02
GmN29_8C39:
 .byte $03
GmN29_8C3A:
 .byte $03
GmN29_8C3B:
 .byte $04
GmN29_8C3C:
 .byte $04
GmN29_8C3D:
 .byte $05
GmN29_8C3E:
 .byte $05
GmN29_8C3F:
 .byte $06
GmN29_8C40:
 .byte $06
GmN29_8C41:
 .byte $07
GmN29_8C42:
 .byte $07
GmN29_8C43:
 .byte $08
GmN29_8C44:
 .byte $08
GmN29_8C45:
 .byte $09
GmN29_8C46:
 .byte $09
GmN29_8C47:
 .byte $0a
GmN29_8C48:
 .byte $0a
GmN29_8C49:
 .byte $0b
GmN29_8C4A:
 .byte $0b
GmN29_8C4B:
 .byte $0c
GmN29_8C4C:
 .byte $0c
GmN29_8C4D:
 .byte $0d
GmN29_8C4E:
 .byte $0d
GmN29_8C4F:
 .byte $0e
GmN29_8C50:
 .byte $0e
GmN29_8C51:
 .byte $0e
GmN29_8C52:
 .byte $0e
GmN29_8C53:
 .byte $0f
GmN29_8C54:
 .byte $0f
GmN29_8C55:
 .byte $0f
GmN29_8C56:
 .byte $10
GmN29_8C57:
 .byte $10
GmN29_8C58:
 .byte $10
GmN29_8C59:
 .byte $11
GmN29_8C5A:
 .byte $11
GmN29_8C5B:
 .byte $11
GmN29_8C5C:
 .byte $14
GmN29_8C5D:
 .byte $ff
GmN29_8C5E:
 .byte $00
GmN29_8C5F:
 .byte $00
GmN29_8C60:
 .byte $01
GmN29_8C61:
 .byte $01
GmN29_8C62:
 .byte $02
GmN29_8C63:
 .byte $02
GmN29_8C64:
 .byte $03
GmN29_8C65:
 .byte $03
GmN29_8C66:
 .byte $04
GmN29_8C67:
 .byte $04
GmN29_8C68:
 .byte $05
GmN29_8C69:
 .byte $05
GmN29_8C6A:
 .byte $06
GmN29_8C6B:
 .byte $06
GmN29_8C6C:
 .byte $07
GmN29_8C6D:
 .byte $07
GmN29_8C6E:
 .byte $08
GmN29_8C6F:
 .byte $08
GmN29_8C70:
 .byte $09
GmN29_8C71:
 .byte $09
GmN29_8C72:
 .byte $0a
GmN29_8C73:
 .byte $0a
GmN29_8C74:
 .byte $0b
GmN29_8C75:
 .byte $0b
GmN29_8C76:
 .byte $0c
GmN29_8C77:
 .byte $0c
GmN29_8C78:
 .byte $0d
GmN29_8C79:
 .byte $0d
GmN29_8C7A:
 .byte $0e
GmN29_8C7B:
 .byte $0e
GmN29_8C7C:
 .byte $23
GmN29_8C7D:
 .byte $23
GmN29_8C7E:
 .byte $24
GmN29_8C7F:
 .byte $24
GmN29_8C80:
 .byte $25
GmN29_8C81:
 .byte $25
GmN29_8C82:
 .byte $26
GmN29_8C83:
 .byte $26
GmN29_8C84:
 .byte $27
GmN29_8C85:
 .byte $27
GmN29_8C86:
 .byte $28
GmN29_8C87:
 .byte $28
GmN29_8C88:
 .byte $ff
GmN29_8C89:
 .byte $00
GmN29_8C8A:
 .byte $00
GmN29_8C8B:
 .byte $01
GmN29_8C8C:
 .byte $01
GmN29_8C8D:
 .byte $02
GmN29_8C8E:
 .byte $02
GmN29_8C8F:
 .byte $03
GmN29_8C90:
 .byte $03
GmN29_8C91:
 .byte $04
GmN29_8C92:
 .byte $04
GmN29_8C93:
 .byte $05
GmN29_8C94:
 .byte $05
GmN29_8C95:
 .byte $06
GmN29_8C96:
 .byte $06
GmN29_8C97:
 .byte $07
GmN29_8C98:
 .byte $07
GmN29_8C99:
 .byte $08
GmN29_8C9A:
 .byte $08
GmN29_8C9B:
 .byte $09
GmN29_8C9C:
 .byte $09
GmN29_8C9D:
 .byte $0a
GmN29_8C9E:
 .byte $0a
GmN29_8C9F:
 .byte $0b
GmN29_8CA0:
 .byte $0b
GmN29_8CA1:
 .byte $0c
GmN29_8CA2:
 .byte $0c
GmN29_8CA3:
 .byte $0d
GmN29_8CA4:
 .byte $0d
GmN29_8CA5:
 .byte $0e
GmN29_8CA6:
 .byte $0e
GmN29_8CA7:
 .byte $15
GmN29_8CA8:
 .byte $15
GmN29_8CA9:
 .byte $16
GmN29_8CAA:
 .byte $16
GmN29_8CAB:
 .byte $17
GmN29_8CAC:
 .byte $17
GmN29_8CAD:
 .byte $18
GmN29_8CAE:
 .byte $18
GmN29_8CAF:
 .byte $17
GmN29_8CB0:
 .byte $17
GmN29_8CB1:
 .byte $18
GmN29_8CB2:
 .byte $41
GmN29_8CB3:
 .byte $ff
GmN29_8CB4:
 .byte $70
GmN29_8CB5:
 .byte $70
GmN29_8CB6:
 .byte $80
GmN29_8CB7:
 .byte $b0
GmN29_8CB8:
 .byte $e0
GmN29_8CB9:
 .byte $10
GmN29_8CBA:
 .byte $40
GmN29_8CBB:
 .byte $60
GmN29_8CBC:
 .byte $70
GmN29_8CBD:
 .byte $70
GmN29_8CBE:
 .byte $80
GmN29_8CBF:
 .byte $b0
GmN29_8CC0:
 .byte $e0
GmN29_8CC1:
 .byte $10
GmN29_8CC2:
 .byte $40
GmN29_8CC3:
 .byte $60
GmN29_8CC4:
 .byte $90
GmN29_8CC5:
 .byte $b0
GmN29_8CC6:
 .byte $c0
GmN29_8CC7:
 .byte $e0
GmN29_8CC8:
 .byte $f0
GmN29_8CC9:
 .byte $00
GmN29_8CCA:
 .byte $10
GmN29_8CCB:
 .byte $10
GmN29_8CCC:
 .byte $00
GmN29_8CCD:
 .byte $00
GmN29_8CCE:
 .byte $00
GmN29_8CCF:
 .byte $00
GmN29_8CD0:
 .byte $00
GmN29_8CD1:
 .byte $01
GmN29_8CD2:
 .byte $01
GmN29_8CD3:
 .byte $01
GmN29_8CD4:
 .byte $00
GmN29_8CD5:
 .byte $00
GmN29_8CD6:
 .byte $00
GmN29_8CD7:
 .byte $00
GmN29_8CD8:
 .byte $00
GmN29_8CD9:
 .byte $01
GmN29_8CDA:
 .byte $01
GmN29_8CDB:
 .byte $01
GmN29_8CDC:
 .byte $01
GmN29_8CDD:
 .byte $01
GmN29_8CDE:
 .byte $01
GmN29_8CDF:
 .byte $01
GmN29_8CE0:
 .byte $01
GmN29_8CE1:
 .byte $02
GmN29_8CE2:
 .byte $02
GmN29_8CE3:
 .byte $02
GmN29_8CE4:
 .byte $e0
GmN29_8CE5:
 .byte $e0
GmN29_8CE6:
 .byte $e0
GmN29_8CE7:
 .byte $60
GmN29_8CE8:
 .byte $c0
GmN29_8CE9:
 .byte $40
GmN29_8CEA:
 .byte $60
GmN29_8CEB:
 .byte $e0
GmN29_8CEC:
 .byte $e0
GmN29_8CED:
 .byte $e0
GmN29_8CEE:
 .byte $e0
GmN29_8CEF:
 .byte $60
GmN29_8CF0:
 .byte $c0
GmN29_8CF1:
 .byte $40
GmN29_8CF2:
 .byte $60
GmN29_8CF3:
 .byte $e0
GmN29_8CF4:
 .byte $e0
GmN29_8CF5:
 .byte $60
GmN29_8CF6:
 .byte $60
GmN29_8CF7:
 .byte $c0
GmN29_8CF8:
 .byte $c0
GmN29_8CF9:
 .byte $20
GmN29_8CFA:
 .byte $20
GmN29_8CFB:
 .byte $40
GmN29_8CFC:
 .byte $00
GmN29_8CFD:
 .byte $00
GmN29_8CFE:
 .byte $00
GmN29_8CFF:
 .byte $01
GmN29_8D00:
 .byte $01
GmN29_8D01:
 .byte $02
GmN29_8D02:
 .byte $02
GmN29_8D03:
 .byte $02
GmN29_8D04:
 .byte $00
GmN29_8D05:
 .byte $00
GmN29_8D06:
 .byte $00
GmN29_8D07:
 .byte $01
GmN29_8D08:
 .byte $01
GmN29_8D09:
 .byte $02
GmN29_8D0A:
 .byte $02
GmN29_8D0B:
 .byte $02
GmN29_8D0C:
 .byte $02
GmN29_8D0D:
 .byte $03
GmN29_8D0E:
 .byte $03
GmN29_8D0F:
 .byte $03
GmN29_8D10:
 .byte $03
GmN29_8D11:
 .byte $04
GmN29_8D12:
 .byte $04
GmN29_8D13:
 .byte $04
GmN29_8D14:
 .byte $00
GmN29_8D15:
 .byte $00
GmN29_8D16:
 .byte $00
GmN29_8D17:
 .byte $40
GmN29_8D18:
 .byte $30
GmN29_8D19:
 .byte $40
GmN29_8D1A:
 .byte $10
GmN29_8D1B:
 .byte $40
GmN29_8D1C:
 .byte $00
GmN29_8D1D:
 .byte $00
GmN29_8D1E:
 .byte $00
GmN29_8D1F:
 .byte $40
GmN29_8D20:
 .byte $30
GmN29_8D21:
 .byte $40
GmN29_8D22:
 .byte $10
GmN29_8D23:
 .byte $40
GmN29_8D24:
 .byte $00
GmN29_8D25:
 .byte $40
GmN29_8D26:
 .byte $00
GmN29_8D27:
 .byte $30
GmN29_8D28:
 .byte $00
GmN29_8D29:
 .byte $30
GmN29_8D2A:
 .byte $00
GmN29_8D2B:
 .byte $10
GmN29_8D2C:
 .byte $00
GmN29_8D2D:
 .byte $00
GmN29_8D2E:
 .byte $00
GmN29_8D2F:
 .byte $00
GmN29_8D30:
 .byte $00
GmN29_8D31:
 .byte $00
GmN29_8D32:
 .byte $00
GmN29_8D33:
 .byte $00
GmN29_8D34:
 .byte $ff
GmN29_8D35:
 .byte $00
GmN29_8D36:
 .byte $00
GmN29_8D37:
 .byte $00
GmN29_8D38:
 .byte $00
GmN29_8D39:
 .byte $00
GmN29_8D3A:
 .byte $00
GmN29_8D3B:
 .byte $00
GmN29_8D3C:
 .byte $00
GmN29_8D3D:
 .byte $00
GmN29_8D3E:
 .byte $00
GmN29_8D3F:
 .byte $00
GmN29_8D40:
 .byte $00
GmN29_8D41:
 .byte $00
GmN29_8D42:
 .byte $00
GmN29_8D43:
 .byte $00
GmN29_8D44:
 .byte $42
GmN29_8D45:
 .byte $43
GmN29_8D46:
 .byte $44
GmN29_8D47:
 .byte $45
GmN29_8D48:
 .byte $46
GmN29_8D49:
 .byte $47
GmN29_8D4A:
 .byte $48
GmN29_8D4B:
 .byte $49
GmN29_8D4C:
 .byte $42
GmN29_8D4D:
 .byte $43
GmN29_8D4E:
 .byte $44
GmN29_8D4F:
 .byte $45
GmN29_8D50:
 .byte $46
GmN29_8D51:
 .byte $47
GmN29_8D52:
 .byte $48
GmN29_8D53:
 .byte $49
GmN29_8D54:
 .byte $4a
GmN29_8D55:
 .byte $4b
GmN29_8D56:
 .byte $4c
GmN29_8D57:
 .byte $4d
GmN29_8D58:
 .byte $4e
GmN29_8D59:
 .byte $4f
GmN29_8D5A:
 .byte $50
GmN29_8D5B:
 .byte $51
.popseg
.pushseg
.segment "GIMMICK_MOVE"
GmN31_F670:
 lda GmRam00AE,x ;31:F670 b5ae
GmN31_F672:
 clc ;31:F672 18
GmN31_F673:
 adc #$10 ;31:F673 6910
GmN31_F675:
 sta GmRam00AE,x ;31:F675 95ae
GmN31_F677:
 jcc GmN31_F67B ;31:F677 9002
GmN31_F679:
 inc GmRam00B8,x ;31:F679 f6b8
GmN31_F67B:
 jmp GmN31_F689 ;31:F67B 4c89f6
GmN31_F67E:
 lda GmRam00AE,x ;31:F67E b5ae
GmN31_F680:
 sec ;31:F680 38
GmN31_F681:
 sbc #$10 ;31:F681 e910
GmN31_F683:
 sta GmRam00AE,x ;31:F683 95ae
GmN31_F685:
 jcs GmN31_F689 ;31:F685 b002
GmN31_F687:
 dec GmRam00B8,x ;31:F687 d6b8
GmN31_F689:
 lda GmRam00CC,x ;31:F689 b5cc
GmN31_F68B:
 jmi GmN31_F699 ;31:F68B 300c
GmN31_F68D:
 sec ;31:F68D 38
GmN31_F68E:
 sbc #$01 ;31:F68E e901
GmN31_F690:
 jpl GmN31_F694 ;31:F690 1002
GmN31_F692:
 lda #$00 ;31:F692 a900
GmN31_F694:
 sta GmRam00CC,x ;31:F694 95cc
GmN31_F696:
 jmp GmN31_F6A2 ;31:F696 4ca2f6
GmN31_F699:
 clc ;31:F699 18
GmN31_F69A:
 adc #$01 ;31:F69A 6901
GmN31_F69C:
 jmi GmN31_F6A0 ;31:F69C 3002
GmN31_F69E:
 lda #$00 ;31:F69E a900
GmN31_F6A0:
 sta GmRam00CC,x ;31:F6A0 95cc
GmN31_F6A2:
 jmp GmN31_F6F3 ;31:F6A2 4cf3f6
GmN31_F6A5:
 ldy #$01 ;31:F6A5 a001
GmN31_F6A7:
 lda GmClock ;31:F6A7 a5ed
GmN31_F6A9:
 and #$07 ;31:F6A9 2907
GmN31_F6AB:
 jeq GmN31_F6AE ;31:F6AB f001
GmN31_F6AD:
 dey ;31:F6AD 88
GmN31_F6AE:
 sty R0 ;31:F6AE 8400
GmN31_F6B0:
 lda GmRam00CC,x ;31:F6B0 b5cc
GmN31_F6B2:
 jmi GmN31_F6C0 ;31:F6B2 300c
GmN31_F6B4:
 sec ;31:F6B4 38
GmN31_F6B5:
 sbc R0 ;31:F6B5 e500
GmN31_F6B7:
 jpl GmN31_F6BB ;31:F6B7 1002
GmN31_F6B9:
 lda #$00 ;31:F6B9 a900
GmN31_F6BB:
 sta GmRam00CC,x ;31:F6BB 95cc
GmN31_F6BD:
 jmp GmN31_F6CA ;31:F6BD 4ccaf6
GmN31_F6C0:
 clc ;31:F6C0 18
GmN31_F6C1:
 adc R0 ;31:F6C1 6500
GmN31_F6C3:
 jmi GmN31_F6C8 ;31:F6C3 3003
GmN31_F6C5:
 lda #$00 ;31:F6C5 a900
GmN31_F6C7:
 iny ;31:F6C7 c8
GmN31_F6C8:
 sta GmRam00CC,x ;31:F6C8 95cc
GmN31_F6CA:
 jmp GmN31_F6F3 ;31:F6CA 4cf3f6
GmN31_F6CD:
 lda GmRam00CC,x ;31:F6CD b5cc
GmN31_F6CF:
 cmp #$20 ;31:F6CF c920
GmN31_F6D1:
 jpl GmN31_F6D8 ;31:F6D1 1005
GmN31_F6D3:
 clc ;31:F6D3 18
GmN31_F6D4:
 adc #$03 ;31:F6D4 6903
GmN31_F6D6:
 sta GmRam00CC,x ;31:F6D6 95cc
GmN31_F6D8:
 jmp GmN31_F6F3 ;31:F6D8 4cf3f6
GmN31_F6DB:
 lda GmRam00CC,x ;31:F6DB b5cc
GmN31_F6DD:
 cmp #$f0 ;31:F6DD c9f0
GmN31_F6DF:
 jpl GmN31_F6E5 ;31:F6DF 1004
GmN31_F6E1:
 lda #$f0 ;31:F6E1 a9f0
GmN31_F6E3:
 sta GmRam00CC,x ;31:F6E3 95cc
GmN31_F6E5:
 lda GmRam00CC,x ;31:F6E5 b5cc
GmN31_F6E7:
 cmp #$20 ;31:F6E7 c920
GmN31_F6E9:
 jpl GmN31_F6F0 ;31:F6E9 1005
GmN31_F6EB:
 clc ;31:F6EB 18
GmN31_F6EC:
 adc #$01 ;31:F6EC 6901
GmN31_F6EE:
 sta GmRam00CC,x ;31:F6EE 95cc
GmN31_F6F0:
 jmp GmN31_F6FE ;31:F6F0 4cfef6
GmN31_F6F3:
 lda GmRam00C2,x ;31:F6F3 b5c2
GmN31_F6F5:
 clc ;31:F6F5 18
GmN31_F6F6:
 adc #$04 ;31:F6F6 6904
GmN31_F6F8:
 jvc GmN31_F6FC ;31:F6F8 5002
GmN31_F6FA:
 lda #$7f ;31:F6FA a97f
GmN31_F6FC:
 sta GmRam00C2,x ;31:F6FC 95c2
GmN31_F6FE:
 ldy #$00 ;31:F6FE a000
GmN31_F700:
 lda GmRam00CC,x ;31:F700 b5cc
GmN31_F702:
 jpl GmN31_F705 ;31:F702 1001
GmN31_F704:
 dey ;31:F704 88
GmN31_F705:
 sty R0 ;31:F705 8400
GmN31_F707:
 clc ;31:F707 18
GmN31_F708:
 adc GmRam00AE,x ;31:F708 75ae
GmN31_F70A:
 sta GmRam00AE,x ;31:F70A 95ae
GmN31_F70C:
 lda GmRam00B8,x ;31:F70C b5b8
GmN31_F70E:
 adc R0 ;31:F70E 6500
GmN31_F710:
 sta GmRam00B8,x ;31:F710 95b8
GmN31_F712:
 ldy #$00 ;31:F712 a000
GmN31_F714:
 lda GmRam00C2,x ;31:F714 b5c2
GmN31_F716:
 jpl GmN31_F719 ;31:F716 1001
GmN31_F718:
 dey ;31:F718 88
GmN31_F719:
 sty R0 ;31:F719 8400
GmN31_F71B:
 clc ;31:F71B 18
GmN31_F71C:
 adc GmRam009A,x ;31:F71C 759a
GmN31_F71E:
 sta GmRam009A,x ;31:F71E 959a
GmN31_F720:
 lda GmRam00A4,x ;31:F720 b5a4
GmN31_F722:
 adc R0 ;31:F722 6500
GmN31_F724:
 sta GmRam00A4,x ;31:F724 95a4
GmN31_F726:
 and #$0f ;31:F726 290f
GmN31_F728:
 cmp #$0c ;31:F728 c90c
GmN31_F72A:
 jcc GmN31_F72F ;31:F72A 9003
GmN31_F72C:
 rts
GmN31_F72F:
 rts
.segment "GIMMICK_COLD"
GmN31_FCFD:
 lda #$00 ;31:FCFD a900
GmN31_FCFF:
 sta GmRam036E,x ;31:FCFF 9d6e03
GmN31_FD02:
 sta GmRam0378,x ;31:FD02 9d7803
GmN31_FD05:
 tya ;31:FD05 98
GmN31_FD06:
 and #$f0 ;31:FD06 29f0
GmN31_FD08:
 cmp #$20 ;31:FD08 c920
GmN31_FD0A:
 jne GmN31_FD1A ;31:FD0A d00e
GmN31_FD0C:
 lda GmRam00C2,x ;31:FD0C b5c2
GmN31_FD0E:
 jpl GmN31_FD29 ;31:FD0E 1019
GmN31_FD10:
 lda GmRam00A4,x ;31:FD10 b5a4
GmN31_FD12:
 sec ;31:FD12 38
GmN31_FD13:
 sbc #$10 ;31:FD13 e910
GmN31_FD15:
 sta GmRam00A4,x ;31:FD15 95a4
GmN31_FD17:
 jmp GmN31_FD29 ;31:FD17 4c29fd
GmN31_FD1A:
 cmp #$30 ;31:FD1A c930
GmN31_FD1C:
 jne GmN31_FD29 ;31:FD1C d00b
GmN31_FD1E:
 lda GmRam00C2,x ;31:FD1E b5c2
GmN31_FD20:
 jmi GmN31_FD29 ;31:FD20 3007
GmN31_FD22:
 lda GmRam00A4,x ;31:FD22 b5a4
GmN31_FD24:
 clc ;31:FD24 18
GmN31_FD25:
 adc #$10 ;31:FD25 6910
GmN31_FD27:
 sta GmRam00A4,x ;31:FD27 95a4
GmN31_FD29:
 tya ;31:FD29 98
GmN31_FD2A:
 and #$07 ;31:FD2A 2907
GmN31_FD2C:
 asl a ;31:FD2C 0a
GmN31_FD2D:
 asl a ;31:FD2D 0a
GmN31_FD2E:
 sta R0 ;31:FD2E 8500
GmN31_FD30:
 asl a ;31:FD30 0a
GmN31_FD31:
 sta R1 ;31:FD31 8501
GmN31_FD33:
 lda GmRam009A,x ;31:FD33 b59a
GmN31_FD35:
 sec ;31:FD35 38
GmN31_FD36:
 sbc #$10 ;31:FD36 e910
GmN31_FD38:
 rol a ;31:FD38 2a
GmN31_FD39:
 lda GmRam00AE,x ;31:FD39 b5ae
GmN31_FD3B:
 rol a ;31:FD3B 2a
GmN31_FD3C:
 rol a ;31:FD3C 2a
GmN31_FD3D:
 and #$03 ;31:FD3D 2903
GmN31_FD3F:
 ora R0 ;31:FD3F 0500
GmN31_FD41:
 tay ;31:FD41 a8
GmN31_FD42:
 lda GmN31_FEDB,y ;31:FD42 b9dbfe
GmN31_FD45:
 ora R1 ;31:FD45 0501
GmN31_FD47:
 sta GmRam0382,x ;31:FD47 9d8203
GmN31_FD4A:
 and #$38 ;31:FD4A 2938
GmN31_FD4C:
 jne GmN31_FD5E ;31:FD4C d010
GmN31_FD4E:
 lda GmRam009A,x ;31:FD4E b59a
GmN31_FD50:
 cmp #$10 ;31:FD50 c910
GmN31_FD52:
 lda GmRam00A4,x ;31:FD52 b5a4
GmN31_FD54:
 sbc #$00 ;31:FD54 e900
GmN31_FD56:
 clc ;31:FD56 18
GmN31_FD57:
 adc #$01 ;31:FD57 6901
GmN31_FD59:
 sta GmRam00A4,x ;31:FD59 95a4
GmN31_FD5B:
 jmp GmN31_FD69 ;31:FD5B 4c69fd
GmN31_FD5E:
 cmp #$08 ;31:FD5E c908
GmN31_FD60:
 jne GmN31_FD69 ;31:FD60 d007
GmN31_FD62:
 ora GmRam00C2,x ;31:FD62 15c2
GmN31_FD64:
 and #$88 ;31:FD64 2988
GmN31_FD66:
 sta GmRam0382,x ;31:FD66 9d8203
GmN31_FD69:
 lda #$02 ;31:FD69 a902
GmN31_FD6B:
 sta GmRam0090,x ;31:FD6B 9590
GmN31_FD6D:
 lda GmRam0382,x ;31:FD6D bd8203
GmN31_FD70:
 jmi GmN31_FDE3 ;31:FD70 3071
GmN31_FD72:
 tay ;31:FD72 a8
GmN31_FD73:
 lda GmN31_FE1B,y ;31:FD73 b91bfe
GmN31_FD76:
 and #$f0 ;31:FD76 29f0
GmN31_FD78:
 sta GmRam00AE,x ;31:FD78 95ae
GmN31_FD7A:
 lda GmN31_FE1B,y ;31:FD7A b91bfe
GmN31_FD7D:
 and #$0f ;31:FD7D 290f
GmN31_FD7F:
 jeq GmN31_FD8C ;31:FD7F f00b
GmN31_FD81:
 cmp #$01 ;31:FD81 c901
GmN31_FD83:
 jeq GmN31_FD87 ;31:FD83 f002
GmN31_FD85:
 lda #$ff ;31:FD85 a9ff
GmN31_FD87:
 clc ;31:FD87 18
GmN31_FD88:
 adc GmRam00B8,x ;31:FD88 75b8
GmN31_FD8A:
 sta GmRam00B8,x ;31:FD8A 95b8
GmN31_FD8C:
 lda GmN31_FE4B,y ;31:FD8C b94bfe
GmN31_FD8F:
 and #$f0 ;31:FD8F 29f0
GmN31_FD91:
 sta GmRam009A,x ;31:FD91 959a
GmN31_FD93:
 lda GmN31_FE4B,y ;31:FD93 b94bfe
GmN31_FD96:
 and #$0f ;31:FD96 290f
GmN31_FD98:
 jeq GmN31_FDA5 ;31:FD98 f00b
GmN31_FD9A:
 cmp #$01 ;31:FD9A c901
GmN31_FD9C:
 jeq GmN31_FDA0 ;31:FD9C f002
GmN31_FD9E:
 lda #$ff ;31:FD9E a9ff
GmN31_FDA0:
 clc ;31:FDA0 18
GmN31_FDA1:
 adc GmRam00A4,x ;31:FDA1 75a4
GmN31_FDA3:
 sta GmRam00A4,x ;31:FDA3 95a4
GmN31_FDA5:
 lda GmRam0382,x ;31:FDA5 bd8203
GmN31_FDA8:
 and #$07 ;31:FDA8 2907
GmN31_FDAA:
 cmp #$07 ;31:FDAA c907
GmN31_FDAC:
 jne GmN31_FDDF ;31:FDAC d031
GmN31_FDAE:
 lda #$01 ;31:FDAE a901
GmN31_FDB0:
 sta GmRam0090,x ;31:FDB0 9590
GmN31_FDB2:
 lda #$00 ;31:FDB2 a900
GmN31_FDB4:
 sta R0 ;31:FDB4 8500
GmN31_FDB6:
 rol GmRam0382,x ;31:FDB6 3e8203
GmN31_FDB9:
 rol R0 ;31:FDB9 2600
GmN31_FDBB:
 rol GmRam0382,x ;31:FDBB 3e8203
GmN31_FDBE:
 rol GmRam0382,x ;31:FDBE 3e8203
GmN31_FDC1:
 rol R0 ;31:FDC1 2600
GmN31_FDC3:
 rol GmRam0382,x ;31:FDC3 3e8203
GmN31_FDC6:
 rol R0 ;31:FDC6 2600
GmN31_FDC8:
 rol GmRam0382,x ;31:FDC8 3e8203
GmN31_FDCB:
 rol R0 ;31:FDCB 2600
GmN31_FDCD:
 ldy R0 ;31:FDCD a400
GmN31_FDCF:
 lda GmN31_FEF3,y ;31:FDCF b9f3fe
GmN31_FDD2:
 sta GmRam00C2,x ;31:FDD2 95c2
GmN31_FDD4:
 lda GmN31_FF03,y ;31:FDD4 b903ff
GmN31_FDD7:
 sta GmRam00CC,x ;31:FDD7 95cc
GmN31_FDD9:
 lda #$00 ;31:FDD9 a900
GmN31_FDDB:
 sta GmRam0382,x ;31:FDDB 9d8203
GmN31_FDDE:
 rts ;31:FDDE 60
GmN31_FDDF:
 inc GmRam0382,x ;31:FDDF fe8203
GmN31_FDE2:
 rts ;31:FDE2 60
GmN31_FDE3:
 and #$3f ;31:FDE3 293f
GmN31_FDE5:
 tay ;31:FDE5 a8
GmN31_FDE6:
 lda GmN31_FE7B,y ;31:FDE6 b97bfe
GmN31_FDE9:
 and #$f0 ;31:FDE9 29f0
GmN31_FDEB:
 sta GmRam00AE,x ;31:FDEB 95ae
GmN31_FDED:
 lda GmN31_FE7B,y ;31:FDED b97bfe
GmN31_FDF0:
 and #$0f ;31:FDF0 290f
GmN31_FDF2:
 jeq GmN31_FDFF ;31:FDF2 f00b
GmN31_FDF4:
 cmp #$01 ;31:FDF4 c901
GmN31_FDF6:
 jeq GmN31_FDFA ;31:FDF6 f002
GmN31_FDF8:
 lda #$ff ;31:FDF8 a9ff
GmN31_FDFA:
 clc ;31:FDFA 18
GmN31_FDFB:
 adc GmRam00B8,x ;31:FDFB 75b8
GmN31_FDFD:
 sta GmRam00B8,x ;31:FDFD 95b8
GmN31_FDFF:
 lda GmN31_FEAB,y ;31:FDFF b9abfe
GmN31_FE02:
 and #$f0 ;31:FE02 29f0
GmN31_FE04:
 sta GmRam009A,x ;31:FE04 959a
GmN31_FE06:
 lda GmN31_FEAB,y ;31:FE06 b9abfe
GmN31_FE09:
 and #$0f ;31:FE09 290f
GmN31_FE0B:
 jeq GmN31_FE18 ;31:FE0B f00b
GmN31_FE0D:
 cmp #$01 ;31:FE0D c901
GmN31_FE0F:
 jeq GmN31_FE13 ;31:FE0F f002
GmN31_FE11:
 lda #$ff ;31:FE11 a9ff
GmN31_FE13:
 clc ;31:FE13 18
GmN31_FE14:
 adc GmRam00A4,x ;31:FE14 75a4
GmN31_FE16:
 sta GmRam00A4,x ;31:FE16 95a4
GmN31_FE18:
 jmp GmN31_FDA5 ;31:FE18 4ca5fd
GmN31_FE1B:
 .byte $20
GmN31_FE1C:
 .byte $40
GmN31_FE1D:
 .byte $60
GmN31_FE1E:
 .byte $80
GmN31_FE1F:
 .byte $a0
GmN31_FE20:
 .byte $c0
GmN31_FE21:
 .byte $e0
GmN31_FE22:
 .byte $01
GmN31_FE23:
 .byte $80
GmN31_FE24:
 .byte $80
GmN31_FE25:
 .byte $80
GmN31_FE26:
 .byte $80
GmN31_FE27:
 .byte $80
GmN31_FE28:
 .byte $80
GmN31_FE29:
 .byte $80
GmN31_FE2A:
 .byte $80
GmN31_FE2B:
 .byte $e0
GmN31_FE2C:
 .byte $c0
GmN31_FE2D:
 .byte $a0
GmN31_FE2E:
 .byte $80
GmN31_FE2F:
 .byte $80
GmN31_FE30:
 .byte $80
GmN31_FE31:
 .byte $80
GmN31_FE32:
 .byte $80
GmN31_FE33:
 .byte $80
GmN31_FE34:
 .byte $80
GmN31_FE35:
 .byte $80
GmN31_FE36:
 .byte $80
GmN31_FE37:
 .byte $60
GmN31_FE38:
 .byte $40
GmN31_FE39:
 .byte $20
GmN31_FE3A:
 .byte $ff
GmN31_FE3B:
 .byte $80
GmN31_FE3C:
 .byte $80
GmN31_FE3D:
 .byte $80
GmN31_FE3E:
 .byte $80
GmN31_FE3F:
 .byte $a0
GmN31_FE40:
 .byte $c0
GmN31_FE41:
 .byte $e0
GmN31_FE42:
 .byte $01
GmN31_FE43:
 .byte $20
GmN31_FE44:
 .byte $40
GmN31_FE45:
 .byte $60
GmN31_FE46:
 .byte $80
GmN31_FE47:
 .byte $80
GmN31_FE48:
 .byte $80
GmN31_FE49:
 .byte $80
GmN31_FE4A:
 .byte $80
GmN31_FE4B:
 .byte $00
GmN31_FE4C:
 .byte $00
GmN31_FE4D:
 .byte $00
GmN31_FE4E:
 .byte $00
GmN31_FE4F:
 .byte $00
GmN31_FE50:
 .byte $00
GmN31_FE51:
 .byte $00
GmN31_FE52:
 .byte $00
GmN31_FE53:
 .byte $a0
GmN31_FE54:
 .byte $c0
GmN31_FE55:
 .byte $e0
GmN31_FE56:
 .byte $01
GmN31_FE57:
 .byte $20
GmN31_FE58:
 .byte $40
GmN31_FE59:
 .byte $60
GmN31_FE5A:
 .byte $80
GmN31_FE5B:
 .byte $00
GmN31_FE5C:
 .byte $00
GmN31_FE5D:
 .byte $00
GmN31_FE5E:
 .byte $00
GmN31_FE5F:
 .byte $20
GmN31_FE60:
 .byte $40
GmN31_FE61:
 .byte $60
GmN31_FE62:
 .byte $80
GmN31_FE63:
 .byte $60
GmN31_FE64:
 .byte $40
GmN31_FE65:
 .byte $20
GmN31_FE66:
 .byte $00
GmN31_FE67:
 .byte $00
GmN31_FE68:
 .byte $00
GmN31_FE69:
 .byte $00
GmN31_FE6A:
 .byte $00
GmN31_FE6B:
 .byte $a0
GmN31_FE6C:
 .byte $c0
GmN31_FE6D:
 .byte $e0
GmN31_FE6E:
 .byte $01
GmN31_FE6F:
 .byte $00
GmN31_FE70:
 .byte $00
GmN31_FE71:
 .byte $00
GmN31_FE72:
 .byte $00
GmN31_FE73:
 .byte $00
GmN31_FE74:
 .byte $00
GmN31_FE75:
 .byte $00
GmN31_FE76:
 .byte $00
GmN31_FE77:
 .byte $ef
GmN31_FE78:
 .byte $c0
GmN31_FE79:
 .byte $a0
GmN31_FE7A:
 .byte $70
GmN31_FE7B:
 .byte $e0
GmN31_FE7C:
 .byte $c0
GmN31_FE7D:
 .byte $a0
GmN31_FE7E:
 .byte $80
GmN31_FE7F:
 .byte $60
GmN31_FE80:
 .byte $40
GmN31_FE81:
 .byte $20
GmN31_FE82:
 .byte $ff
GmN31_FE83:
 .byte $80
GmN31_FE84:
 .byte $80
GmN31_FE85:
 .byte $80
GmN31_FE86:
 .byte $80
GmN31_FE87:
 .byte $80
GmN31_FE88:
 .byte $80
GmN31_FE89:
 .byte $80
GmN31_FE8A:
 .byte $80
GmN31_FE8B:
 .byte $80
GmN31_FE8C:
 .byte $80
GmN31_FE8D:
 .byte $80
GmN31_FE8E:
 .byte $80
GmN31_FE8F:
 .byte $a0
GmN31_FE90:
 .byte $c0
GmN31_FE91:
 .byte $e0
GmN31_FE92:
 .byte $01
GmN31_FE93:
 .byte $20
GmN31_FE94:
 .byte $40
GmN31_FE95:
 .byte $60
GmN31_FE96:
 .byte $80
GmN31_FE97:
 .byte $80
GmN31_FE98:
 .byte $80
GmN31_FE99:
 .byte $80
GmN31_FE9A:
 .byte $80
GmN31_FE9B:
 .byte $e0
GmN31_FE9C:
 .byte $c0
GmN31_FE9D:
 .byte $a0
GmN31_FE9E:
 .byte $80
GmN31_FE9F:
 .byte $80
GmN31_FEA0:
 .byte $80
GmN31_FEA1:
 .byte $80
GmN31_FEA2:
 .byte $80
GmN31_FEA3:
 .byte $80
GmN31_FEA4:
 .byte $80
GmN31_FEA5:
 .byte $80
GmN31_FEA6:
 .byte $80
GmN31_FEA7:
 .byte $60
GmN31_FEA8:
 .byte $40
GmN31_FEA9:
 .byte $20
GmN31_FEAA:
 .byte $ff
GmN31_FEAB:
 .byte $00
GmN31_FEAC:
 .byte $00
GmN31_FEAD:
 .byte $00
GmN31_FEAE:
 .byte $00
GmN31_FEAF:
 .byte $00
GmN31_FEB0:
 .byte $00
GmN31_FEB1:
 .byte $00
GmN31_FEB2:
 .byte $00
GmN31_FEB3:
 .byte $60
GmN31_FEB4:
 .byte $40
GmN31_FEB5:
 .byte $20
GmN31_FEB6:
 .byte $00
GmN31_FEB7:
 .byte $ef
GmN31_FEB8:
 .byte $c0
GmN31_FEB9:
 .byte $a0
GmN31_FEBA:
 .byte $70
GmN31_FEBB:
 .byte $60
GmN31_FEBC:
 .byte $40
GmN31_FEBD:
 .byte $20
GmN31_FEBE:
 .byte $00
GmN31_FEBF:
 .byte $00
GmN31_FEC0:
 .byte $00
GmN31_FEC1:
 .byte $00
GmN31_FEC2:
 .byte $00
GmN31_FEC3:
 .byte $00
GmN31_FEC4:
 .byte $00
GmN31_FEC5:
 .byte $00
GmN31_FEC6:
 .byte $00
GmN31_FEC7:
 .byte $20
GmN31_FEC8:
 .byte $40
GmN31_FEC9:
 .byte $60
GmN31_FECA:
 .byte $80
GmN31_FECB:
 .byte $00
GmN31_FECC:
 .byte $00
GmN31_FECD:
 .byte $00
GmN31_FECE:
 .byte $00
GmN31_FECF:
 .byte $ef
GmN31_FED0:
 .byte $c0
GmN31_FED1:
 .byte $a0
GmN31_FED2:
 .byte $70
GmN31_FED3:
 .byte $a0
GmN31_FED4:
 .byte $c0
GmN31_FED5:
 .byte $e0
GmN31_FED6:
 .byte $01
GmN31_FED7:
 .byte $00
GmN31_FED8:
 .byte $00
GmN31_FED9:
 .byte $00
GmN31_FEDA:
 .byte $00
GmN31_FEDB:
 .byte $00
GmN31_FEDC:
 .byte $80
GmN31_FEDD:
 .byte $00
GmN31_FEDE:
 .byte $80
GmN31_FEDF:
 .byte $00
GmN31_FEE0:
 .byte $00
GmN31_FEE1:
 .byte $80
GmN31_FEE2:
 .byte $80
GmN31_FEE3:
 .byte $80
GmN31_FEE4:
 .byte $80
GmN31_FEE5:
 .byte $00
GmN31_FEE6:
 .byte $00
GmN31_FEE7:
 .byte $00
GmN31_FEE8:
 .byte $00
GmN31_FEE9:
 .byte $80
GmN31_FEEA:
 .byte $80
GmN31_FEEB:
 .byte $00
GmN31_FEEC:
 .byte $00
GmN31_FEED:
 .byte $80
GmN31_FEEE:
 .byte $80
GmN31_FEEF:
 .byte $80
GmN31_FEF0:
 .byte $80
GmN31_FEF1:
 .byte $00
GmN31_FEF2:
 .byte $00
GmN31_FEF3:
 .byte $00
GmN31_FEF4:
 .byte $20
GmN31_FEF5:
 .byte $20
GmN31_FEF6:
 .byte $00
GmN31_FEF7:
 .byte $00
GmN31_FEF8:
 .byte $e0
GmN31_FEF9:
 .byte $00
GmN31_FEFA:
 .byte $00
GmN31_FEFB:
 .byte $00
GmN31_FEFC:
 .byte $e0
GmN31_FEFD:
 .byte $00
GmN31_FEFE:
 .byte $20
GmN31_FEFF:
 .byte $e0
GmN31_FF00:
 .byte $00
GmN31_FF01:
 .byte $00
GmN31_FF02:
 .byte $00
GmN31_FF03:
 .byte $20
GmN31_FF04:
 .byte $00
GmN31_FF05:
 .byte $00
GmN31_FF06:
 .byte $e0
GmN31_FF07:
 .byte $20
GmN31_FF08:
 .byte $00
GmN31_FF09:
 .byte $00
GmN31_FF0A:
 .byte $00
GmN31_FF0B:
 .byte $e0
GmN31_FF0C:
 .byte $00
GmN31_FF0D:
 .byte $20
GmN31_FF0E:
 .byte $00
GmN31_FF0F:
 .byte $00
GmN31_FF10:
 .byte $e0
GmN31_FF11:
 .byte $00
GmN31_FF12:
 .byte $00
.popseg
