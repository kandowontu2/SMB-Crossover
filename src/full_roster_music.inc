; Generated original-game frame masks; existing families stay unchanged.
.if ::ENABLE_MMC5_EXPANDED
.pushseg
.segment "X5_FULL_MUSIC_00"
X5MusicBank00:
.incbin "audio/full-roster/full-00.bin"
.segment "X5_FULL_MUSIC_01"
X5MusicBank01:
.incbin "audio/full-roster/full-01.bin"
.segment "X5_FULL_MUSIC_02"
X5MusicBank02:
.incbin "audio/full-roster/full-02.bin"
.segment "X5_FULL_MUSIC_03"
X5MusicBank03:
.incbin "audio/full-roster/full-03.bin"
.segment "X5_FULL_MUSIC_04"
X5MusicBank04:
.incbin "audio/full-roster/full-04.bin"
.segment "X5_FULL_MUSIC_05"
X5MusicBank05:
.incbin "audio/full-roster/full-05.bin"
.segment "X5_FULL_MUSIC_06"
X5MusicBank06:
.incbin "audio/full-roster/full-06.bin"
.segment "X5_FULL_MUSIC_07"
X5MusicBank07:
.incbin "audio/full-roster/full-07.bin"
.segment "X5_FULL_MUSIC_08"
X5MusicBank08:
.incbin "audio/full-roster/full-08.bin"
.segment "X5_FULL_MUSIC_09"
X5MusicBank09:
.incbin "audio/full-roster/full-09.bin"
.segment "X5_FULL_MUSIC_0A"
X5MusicBank0A:
.incbin "audio/full-roster/full-0a.bin"
.segment "X5_FULL_MUSIC_0B"
X5MusicBank0B:
.incbin "audio/full-roster/full-0b.bin"
.segment "X5_FULL_MUSIC_0C"
X5MusicBank0C:
.incbin "audio/full-roster/full-0c.bin"
.segment "X5_FULL_MUSIC_0D"
X5MusicBank0D:
.incbin "audio/full-roster/full-0d.bin"
.segment "X5_FULL_MUSIC_0E"
X5MusicBank0E:
.incbin "audio/full-roster/full-0e.bin"
.segment "X5_FULL_MUSIC_0F"
X5MusicBank0F:
.incbin "audio/full-roster/full-0f.bin"
.popseg
.macro FullXgAreaBanks
 .byte .bank(X5MusicBank00),.bank(X5MusicBank02),.bank(X5MusicBank03),.bank(X5MusicBank05),.bank(X5MusicBank07),.bank(X5MusicBank09),.bank(X5MusicBank0A),.bank(X5MusicBank0C),.bank(X5MusicBank02),.bank(X5MusicBank03),.bank(X5MusicBank05),.bank(X5MusicBank07),.bank(X5MusicBank09),.bank(X5MusicBank0A)
.endmacro
.macro FullXgAreaLo
 .byte <(X5MusicBank00+$0000),<(X5MusicBank02+$0173),<(X5MusicBank03+$117c),<(X5MusicBank05+$0e20),<(X5MusicBank07+$1e1d),<(X5MusicBank09+$05f3),<(X5MusicBank0A+$05c5),<(X5MusicBank0C+$10a8),<(X5MusicBank02+$0173),<(X5MusicBank03+$117c),<(X5MusicBank05+$0e20),<(X5MusicBank07+$1e1d),<(X5MusicBank09+$05f3),<(X5MusicBank0A+$05c5)
.endmacro
.macro FullXgAreaHi
 .byte >(X5MusicBank00+$0000),>(X5MusicBank02+$0173),>(X5MusicBank03+$117c),>(X5MusicBank05+$0e20),>(X5MusicBank07+$1e1d),>(X5MusicBank09+$05f3),>(X5MusicBank0A+$05c5),>(X5MusicBank0C+$10a8),>(X5MusicBank02+$0173),>(X5MusicBank03+$117c),>(X5MusicBank05+$0e20),>(X5MusicBank07+$1e1d),>(X5MusicBank09+$05f3),>(X5MusicBank0A+$05c5)
.endmacro
.macro FullXgLoopBanks
 .byte .bank(X5MusicBank00),.bank(X5MusicBank02),.bank(X5MusicBank03),.bank(X5MusicBank05),.bank(X5MusicBank07),.bank(X5MusicBank09),.bank(X5MusicBank0A),.bank(X5MusicBank0C),.bank(X5MusicBank02),.bank(X5MusicBank03),.bank(X5MusicBank05),.bank(X5MusicBank07),.bank(X5MusicBank09),.bank(X5MusicBank0A)
.endmacro
.macro FullXgLoopLo
 .byte <(X5MusicBank00+$0000),<(X5MusicBank02+$0173),<(X5MusicBank03+$117c),<(X5MusicBank05+$0e20),<(X5MusicBank07+$1e1d),<(X5MusicBank09+$05f3),<(X5MusicBank0A+$05c5),<(X5MusicBank0C+$10a8),<(X5MusicBank02+$0173),<(X5MusicBank03+$117c),<(X5MusicBank05+$0e20),<(X5MusicBank07+$1e1d),<(X5MusicBank09+$05f3),<(X5MusicBank0A+$05c5)
.endmacro
.macro FullXgLoopHi
 .byte >(X5MusicBank00+$0000),>(X5MusicBank02+$0173),>(X5MusicBank03+$117c),>(X5MusicBank05+$0e20),>(X5MusicBank07+$1e1d),>(X5MusicBank09+$05f3),>(X5MusicBank0A+$05c5),>(X5MusicBank0C+$10a8),>(X5MusicBank02+$0173),>(X5MusicBank03+$117c),>(X5MusicBank05+$0e20),>(X5MusicBank07+$1e1d),>(X5MusicBank09+$05f3),>(X5MusicBank0A+$05c5)
.endmacro
.macro FullXgEventBanks
 .byte .bank(X5MusicBank0B),.bank(X5MusicBank0B),.bank(X5MusicBank0C),.bank(X5MusicBank0C),.bank(X5MusicBank0B),.bank(X5MusicBank0C),.bank(X5MusicBank0C),.bank(X5MusicBank0B),.bank(X5MusicBank0B),.bank(X5MusicBank0C),.bank(X5MusicBank0C),.bank(X5MusicBank0B),.bank(X5MusicBank0C),.bank(X5MusicBank0C)
.endmacro
.macro FullXgEventLo
 .byte <(X5MusicBank0B+$17bd),<(X5MusicBank0B+$1fc0),<(X5MusicBank0C+$09c8),<(X5MusicBank0C+$0bf4),<(X5MusicBank0B+$1fc0),<(X5MusicBank0C+$09c8),<(X5MusicBank0C+$10a8),<(X5MusicBank0B+$17bd),<(X5MusicBank0B+$1fc0),<(X5MusicBank0C+$09c8),<(X5MusicBank0C+$0bf4),<(X5MusicBank0B+$1fc0),<(X5MusicBank0C+$09c8),<(X5MusicBank0C+$10a8)
.endmacro
.macro FullXgEventHi
 .byte >(X5MusicBank0B+$17bd),>(X5MusicBank0B+$1fc0),>(X5MusicBank0C+$09c8),>(X5MusicBank0C+$0bf4),>(X5MusicBank0B+$1fc0),>(X5MusicBank0C+$09c8),>(X5MusicBank0C+$10a8),>(X5MusicBank0B+$17bd),>(X5MusicBank0B+$1fc0),>(X5MusicBank0C+$09c8),>(X5MusicBank0C+$0bf4),>(X5MusicBank0B+$1fc0),>(X5MusicBank0C+$09c8),>(X5MusicBank0C+$10a8)
.endmacro
.macro FullXgEventLoopBanks
 .byte .bank(X5MusicBank0B),.bank(X5MusicBank0B),.bank(X5MusicBank0C),.bank(X5MusicBank0C),.bank(X5MusicBank0B),.bank(X5MusicBank0C),.bank(X5MusicBank0C),.bank(X5MusicBank0B),.bank(X5MusicBank0B),.bank(X5MusicBank0C),.bank(X5MusicBank0C),.bank(X5MusicBank0B),.bank(X5MusicBank0C),.bank(X5MusicBank0C)
.endmacro
.macro FullXgEventLoopLo
 .byte <(X5MusicBank0B+$17bd),<(X5MusicBank0B+$1fc0),<(X5MusicBank0C+$09c8),<(X5MusicBank0C+$0bf4),<(X5MusicBank0B+$1fc0),<(X5MusicBank0C+$09c8),<(X5MusicBank0C+$10a8),<(X5MusicBank0B+$17bd),<(X5MusicBank0B+$1fc0),<(X5MusicBank0C+$09c8),<(X5MusicBank0C+$0bf4),<(X5MusicBank0B+$1fc0),<(X5MusicBank0C+$09c8),<(X5MusicBank0C+$10a8)
.endmacro
.macro FullXgEventLoopHi
 .byte >(X5MusicBank0B+$17bd),>(X5MusicBank0B+$1fc0),>(X5MusicBank0C+$09c8),>(X5MusicBank0C+$0bf4),>(X5MusicBank0B+$1fc0),>(X5MusicBank0C+$09c8),>(X5MusicBank0C+$10a8),>(X5MusicBank0B+$17bd),>(X5MusicBank0B+$1fc0),>(X5MusicBank0C+$09c8),>(X5MusicBank0C+$0bf4),>(X5MusicBank0B+$1fc0),>(X5MusicBank0C+$09c8),>(X5MusicBank0C+$10a8)
.endmacro
.endif
