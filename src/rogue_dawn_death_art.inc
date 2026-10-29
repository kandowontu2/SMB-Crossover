; Additive original Rogue Dawn1.21 frame35, generated from actual DE4A.
; Include AFTER A95 host code. Preserve frozen C94/CORE/body asset.
; Callback sets the C95 pointer without mapping away its live C94 bridge.
; Actual first-record owner must lease C95 for this frame before reading.
RD_DEATH_CHR=689
RD_DEATH_RECORD_C=$df00
RD_DEATH_RECORD_LEFT_C=$df19
RD_DEATH_SOURCE_X=24
.pushseg
.segment "ROGUE_DAWN_HOST"
.assert (*-RdHsFrozenDispatch) <= $1900,error,"Reserve death ART tail"
 .res $1900-(*-RdHsFrozenDispatch),$ff
.export RdDeathRecordA,RD_DEATH_RECORD_C,RD_DEATH_CHR,RD_DEATH_SOURCE_X
.export RdDeathRecordLeftA,RD_DEATH_RECORD_LEFT_C
RdDeathRecordA:
 .byte $18,$00,$20,$fc,$fe,$02,$20,$fc,$06,$04,$20,$fc,$0e,$06,$20,$0c,$fe,$08,$20,$0c,$06,$0a,$20,$0c,$0e
RdDeathRecordLeftA:
 .byte $18,$0c,$20,$fc,$fe,$0e,$20,$fc,$06,$10,$20,$fc,$0e,$12,$20,$0c,$fe,$14,$20,$0c,$06,$16,$20,$0c,$0e
RdDeathRecordEnd:
.assert .loword(RdDeathRecordA)=$bf00,lderror,"C95 mirrored descriptor"
.assert *-RdDeathRecordA <= 256,error,"Original A95 tail reservation"
.popseg
