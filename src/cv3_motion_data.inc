.pushseg
.segment "CV3_CORE"
Cv3FixedJump:
 .byte $80,$fa,$fa,$fa,$fa,$fa,$fb,$fb,$fb,$fb,$fb,$fd,$fd,$fd,$fd,$fd,$fe,$fe,$fe,$ff,$ff,$ff,$ff,$00,$ff,$00,$00,$00,$00,$81
Cv3GrantJump:
 .byte $80,$f9,$f9,$f9,$f9,$f9,$f9,$f9,$f9,$f9,$f9,$f9,$f9,$f9,$f9,$f9,$f9,$f9,$f9,$f9,$fa,$fa,$fa,$fa,$fa,$fa,$fb,$fb,$fb,$fb,$fb,$fc,$fc,$fc,$fc,$fc,$fd,$fd,$fd,$fd,$fd,$fd,$fe,$fe,$fe,$fe,$fe,$ff,$ff,$ff,$ff,$ff,$00,$00,$00,$00,$00,$81
.popseg
