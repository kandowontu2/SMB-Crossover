"""Fund ROM-owned HUD retirement in existing Karnov cold code only.

Pure source transformation. No allocation, owning build or ROM mutation.
The active loop permits only rows0..11. V is overwritten by BIT2002; C is dead
until SEC or the row-count CMP. Native caller flags remain independently saved.
"""


def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new)


def transform_sources(*,resident,carrier_helper):
    pair=' sta CurrentBankC\n sta $5116'
    for begin,end,count in [('KrRetire:\n','; Cold load is allowed',1),('KrLoad:\n','KrLoadReturn:\n',5)]:
        lo=resident.index(begin);hi=resident.index(end,lo);part=resident[lo:hi]
        assert part.count(pair)==count,(begin,part.count(pair))
        resident=resident[:lo]+part.replace(pair,' jsr KrHudMapC')+resident[hi:]
    assert carrier_helper.count(pair)==1
    carrier_helper=carrier_helper.replace(pair,' jsr KrHudMapC')
    carrier_helper=once(carrier_helper,'''KrCarrierMap:
 ldx R2
 lda #3
 cpx #8
 bcs :+
 lsr                         ; first8 rows use upper1, the four C2 rows upper3
:sta $5130
 lda KrCarrierChrLo,x
 sta $512b
 rts''','''KrCarrierMap:
 ldx R2
 lda #1
 cpx #8
 bcc KrCarrierLow
 lda #3
KrCarrierLow:
 sta $5130
 txa
 bcc KrCarrierChr
 adc #99                    ; rows8..11 enter C1; yield108..111/C0
KrCarrierChr:
 adc #143                   ; first8 rows enter C0; exact143..150/251..254
 sta $512b
 rts''')
    carrier_helper=once(carrier_helper,'KrCarrierChrLo:.byte <399,<400,<401,<402,<403,<404,<405,<406,<1019,<1020,<1021,<1022\n','')
    carrier_helper=once(carrier_helper,'KrCarrierHelpersEnd:','''; Only cold loader/retirement sites share this pair. AXY/P unchanged.
KrHudMapC:
 sta CurrentBankC
 sta $5116
 rts
KrCarrierHelpersEnd:''')
    resident=once(resident,'KrRetire:\n php\n pha\n','''KrRetire:
 php
 pha
 ; Clear our HUD even when its cache header has since been corrupted.
 ; No C2 code is called before or after header invalidation.
 lda InvHudActive
 cmp #$e9
 bne :+
 lda #0
 sta InvHudActive
 lda #1
 sta ReloadCHRBank
:
''')
    return dict(resident=resident,fragments={'kr-loader-carrier-v6.inc':carrier_helper},
                cold_map_pairs_shared=7,hot_dispatch_changed=False,icon_font_owner=0xe9)
