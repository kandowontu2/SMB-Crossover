; Exact original command vectors with direct high-nibble indexing.
; A180..A1B1 was linker-declared FF fill, outside all source data and helpers.
.assert *=$a173,lderror,"Unchanged multiply helper end"
.res 13,$ff
TnParserVectors:
 .byte $fb,$ac
 .res 14,$ff
 .byte $22,$ad
 .res 14,$ff
 .byte $70,$ad
 .res 14,$ff
 .byte $66,$ae
.assert TnParserVectors=$a180,lderror,"Verified unused native writer tail"
.assert *=$a1b2,lderror,"Complete four interleaved original vectors"
.export TnParserVectors
