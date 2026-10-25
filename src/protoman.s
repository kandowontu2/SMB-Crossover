; Expanded-only complete alternate; no new raw family/inventory owner.
PROTO_CHR_FIRST=256
PROTO_HURT_BANK_OFFSET=11
.assert .hibyte(PROTO_CHR_FIRST)=.hibyte(PROTO_CHR_FIRST+19),error,"Proto family quarter"
.include "protoman_cold.s"
.include "protoman_audio_kernel.inc"
.include "protoman_art.inc"
.pushseg
.segment "PROTO_COLD"
.include "protoman_legacy_shots.inc"
.segment "PROTO_GFX"
.res $1108-(*-ProtoArtBegin), $ff
.incbin "chr/characters/protoman-common-records.bin"
.assert *=$D368,error,"Original audio entry address"
.include "protoman_native_audio.inc"
.segment "X5_CHR_MORE"
.incbin "chr/characters/protoman.chr"
.popseg
