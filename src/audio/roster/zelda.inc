.segment "ZELDA_AUDIO"
.scope ZeldaNative
SONG_END= $00
C_6		= $02
Db_3	= $04
Gb_5	= $06
REST	= $08
D_3		= $0A
Eb_3	= $0C
E_3		= $0E
F_3		= $10
Gb_3	= $12
G_3		= $14
Ab_3	= $16
A_3		= $18
Bb_3	= $1A
B_3		= $1C
C_4		= $1E
Db_4	= $20
D_4		= $22
Eb_4	= $24
E_4		= $26
F_4		= $28
Gb_4	= $2A
G_4		= $2C
Ab_4	= $2E
A_4		= $30
Bb_4	= $32
B_4		= $34
C_5		= $36
Db_5	= $38
D_5		= $3A
Eb_5	= $3C
E_5		= $3E
F_5		= $40
G_5		= $42
Ab_5	= $44
Bb_5	= $46
A_5		= $48
B_5		= $4A
E_6		= $4C
Db_6	= $4E
D_6		= $50
Eb_6	= $52
F_6		= $54
G_6		= $56
Ab_6	= $58
A_6		= $5A
B_6		= $5C
C_7		= $5E
Ab_7	= $60
E_2		= $62
F_2		= $64
Gb_2	= $66
Ab_2	= $68
A_2		= $6A
Bb_2	= $6C
B_2		= $6E
C_3		= $70

QUARTER_TRIPLET		= $87
DOTTED_HALF_NOTE	= $86
HALF_NOTE			= $85
DOTTED_QUARTER_NOTE	= $84
QUARTER_NOTE		= $83
EIGHTH_NOTE			= $81
SIXTEENTH_NOTE		= $80
EIGHTH_TRIPLET		= $82

.struct SongDescriptor
	unk1			.byte
	musicDataPtr	.addr
	offsetVoiceC	.byte
	offsetVoiceB	.byte
	offsetVoiceD	.byte
.endstruct
PPUCTRL		= $2000
PPUMASK		= $2001
PPUSTATUS	= $2002
OAMADDR		= $2003
OAMDATA		= $2004
PPUSCROLL	= $2005
PPUADDR		= $2006
PPUDATA		= $2007
OAMDMA		= $4014
APU_PULSE1CTRL  = $4000
APU_PULSE1RAMP  = $4001
APU_PULSE1FTUNE = $4002
APU_PULSE1CTUNE = $4003
APU_PULSE2CTRL  = $4004
APU_PULSE2RAMP  = $4005
APU_PULSE2FTUNE = $4006
APU_PULSE2STUNE = $4007
APU_TRICTRL1    = $4008
APU_TRICTRL2    = $4009
APU_TRIFREQ1    = $400A
APU_TRIFREQ2    = $400B
APU_NOISECTRL   = $400C
APU_NOISEFREQ1  = $400E
APU_NOISEFREQ2  = $400F
APU_MODCTRL     = $4010
APU_MODDA       = $4011
APU_MODADDR     = $4012
APU_MODLEN      = $4013
APU_CHANCTRL    = $4015
JOYPAD1	        = $4016
JOYPAD2	        = $4017
local0 = $00
local1 = $01
local2 = $02
local3 = $03
local4 = $04
local5 = $05
musicData = $66
gamePaused = $e0
musicRequest = RgZeldaRam+$100
musicEffectRequest = RgZeldaRam+$102
soundEffectRequest = RgZeldaRam+$104
currentSoundEffect = RgZeldaRam+$105
currentMusicEffect = RgZeldaRam+$107
currentMusic = RgZeldaRam+$109
musicOffsetVoiceA = RgZeldaRam+$10a
musicOffsetVoiceB = RgZeldaRam+$10b
musicOffsetVoiceC = RgZeldaRam+$10c
musicOffsetVoiceD = RgZeldaRam+$10d
noteDuration = RgZeldaRam+$110
musicTimer = RgZeldaRam+$111
songTable:
.byte songDescriptor0 - songTable
.byte songDescriptor1 - songTable
.byte songDescriptor2 - songTable
.byte songDescriptor3 - songTable
.byte songDescriptor4 - songTable
.byte songDescriptor5 - songTable
.byte songDescriptor6 - songTable
.byte songDescriptor7 - songTable
.byte songDescriptor8 - songTable
.byte songDescriptor9 - songTable
.byte songDescriptor10 - songTable
.byte songDescriptor11 - songTable
.byte songDescriptor12 - songTable
.byte songDescriptor13 - songTable
.byte songDescriptor14 - songTable
.byte songDescriptor15 - songTable
.byte songDescriptor16 - songTable
.byte songDescriptor17 - songTable
.byte songDescriptor18 - songTable
.byte songDescriptor19 - songTable
.byte songDescriptor20 - songTable
.byte songDescriptor21 - songTable
.byte songDescriptor22 - songTable
.byte songDescriptor23 - songTable
.byte songDescriptor24 - songTable
.byte songDescriptor25 - songTable
.byte songDescriptor26 - songTable
.byte songDescriptor27 - songTable
.byte songDescriptor28 - songTable
.byte songDescriptor29 - songTable
.byte songDescriptor30 - songTable
.byte songDescriptor31 - songTable
.byte songDescriptor32 - songTable
.byte songDescriptor33 - songTable
.byte songDescriptor34 - songTable
.byte songDescriptor35 - songTable

;Title theme
songDescriptor25:
.byte $20
.addr song25voiceA
.byte song25voiceC - song25voiceA
.byte song25voiceB - song25voiceA
.byte song25voiceD - song25voiceA
.byte $80
.byte $01

songDescriptor26:
.byte $20
.addr song26voiceA
.byte song26voiceC - song26voiceA
.byte song26voiceB - song26voiceA
.byte song26voiceD - song26voiceA
.byte $01
.byte $80

songDescriptor27:
songDescriptor30:
.byte $20
.addr song27voiceA
.byte song27voiceC - song27voiceA
.byte song27voiceB - song27voiceA
.byte song27voiceD - song27voiceA
.byte $80
.byte $80

songDescriptor28:
.byte $20
.addr song28voiceA
.byte song28voiceC - song28voiceA
.byte song28voiceB - song28voiceA
.byte song28voiceD - song28voiceA
.byte $80
.byte $80

songDescriptor29:
songDescriptor34:
.byte $20
.addr song29voiceA
.byte song29voiceC - song29voiceA
.byte song29voiceB - song29voiceA
.byte song29voiceD - song29voiceA
.byte $80
.byte $80

songDescriptor31:
.byte $20
.addr song31voiceA
.byte song31voiceC - song31voiceA
.byte song31voiceB - song31voiceA
.byte song31voiceD - song31voiceA
.byte $80
.byte $80

songDescriptor32:
.byte $20
.addr song32voiceA
.byte song32voiceC - song32voiceA
.byte song32voiceB - song32voiceA
.byte song32voiceD - song32voiceA
.byte $80
.byte $80

songDescriptor33:
.byte $20
.addr song33voiceA
.byte song33voiceC - song33voiceA
.byte song33voiceB - song33voiceA
.byte song33voiceD - song33voiceA
.byte $80
.byte $80

songDescriptor6:
songDescriptor7:
.byte $10
.addr song6voiceA

songDescriptor3:
.byte $10
.addr song3voiceA
.byte song3voiceC - song3voiceA
.byte song3voiceB - song3voiceA
.byte song3voiceD - song3voiceA
.byte $80

;Triforce receiving theme
songDescriptor2:
.byte $10
.addr song2voiceA
.byte song2voiceC - song2voiceA
.byte song2voiceB - song2voiceA
.byte song2voiceD - song2voiceA
.byte $80

;Main overworld theme - Intro
songDescriptor8:
.byte $10
.addr song8voiceA
.byte song8voiceC - song8voiceA
.byte song8voiceB - song8voiceA
.byte song8voiceD - song8voiceA
.byte $01
.byte $80

;Main overworld theme - 1st 8 beats
songDescriptor0:
songDescriptor4:
songDescriptor9:
songDescriptor12:
.byte $10
.addr song0voiceA
.byte song0voiceC - song0voiceA
.byte song0voiceB - song0voiceA
.byte song0voiceD - song0voiceA
.byte $01
.byte $80

songDescriptor10:
.byte $10
.addr song10voiceA
.byte song10voiceC - song10voiceA
.byte song10voiceB - song10voiceA
.byte song10voiceD - song10voiceA
.byte $01
.byte $80

songDescriptor13:
.byte $10
.addr song13voiceA
.byte song13voiceC - song13voiceA
.byte song13voiceB - song13voiceA
.byte song13voiceD - song13voiceA
.byte $01
.byte $80

songDescriptor11:
songDescriptor14:
.byte $10
.addr song11voiceA
.byte song11voiceC - song11voiceA
.byte song11voiceB - song11voiceA
.byte song11voiceD - song11voiceA
.byte $01
.byte $80

songDescriptor15:
.byte $00
.addr song15voiceA
.byte song15voiceC - song15voiceA
.byte song15voiceB - song15voiceA
.byte song15voiceD - song15voiceA
.byte $01
.byte $01

songDescriptor16:
.byte $00
.addr song16voiceA
.byte song16voiceC - song16voiceA
.byte song16voiceB - song16voiceA
.byte song16voiceD - song16voiceA
.byte $01
.byte $01

songDescriptor5:
.byte $10
.addr song5voiceA
.byte song5voiceC - song5voiceA
.byte song5voiceB - song5voiceA
.byte song5voiceD - song5voiceA
.byte $80
.byte $80

songDescriptor1:
.byte $10
.addr song1voiceA
.byte song1voiceC - song1voiceA
.byte song1voiceB - song1voiceA
.byte song1voiceD - song1voiceA
.byte $80
.byte $01

;Death screen music
songDescriptor17:
.byte $08
.addr song17voiceA
.byte song17voiceC - song17voiceA
.byte song17voiceB - song17voiceA
.byte song17voiceD - song17voiceA
.byte $01
.byte $80

songDescriptor18:
.byte $08
.addr song18voiceA
.byte song18voiceC - song18voiceA
.byte song18voiceB - song18voiceA
.byte song18voiceD - song18voiceA
.byte $01
.byte $80

songDescriptor19:
.byte $08
.addr song19voiceA
.byte song19voiceC - song19voiceA
.byte song19voiceB - song19voiceA
.byte song19voiceD - song19voiceA
.byte $80
.byte $80

songDescriptor20:
songDescriptor22:
.byte $08
.addr song20voiceA
.byte song20voiceC - song20voiceA
.byte song20voiceB - song20voiceA
.byte song20voiceD - song20voiceA
.byte $01
.byte $80

songDescriptor21:
.byte $08
.addr song21voiceA
.byte song21voiceC - song21voiceA
.byte song21voiceB - song21voiceA
.byte song21voiceD - song21voiceA
.byte $01
.byte $80

songDescriptor23:
.byte $08
.addr song23voiceA
.byte song23voiceC - song23voiceA
.byte song23voiceB - song23voiceA
.byte song23voiceD - song23voiceA
.byte $01
.byte $80

songDescriptor24:
.byte $08
.addr song24voiceA
.byte song24voiceC - song24voiceA
.byte song24voiceB - song24voiceA
.byte song24voiceD - song24voiceA
.byte $80
.byte $80

songDescriptor35:
.byte $10
.addr song35voiceA
.byte song35voiceC - song35voiceA
.byte song35voiceB - song35voiceA
.byte song35voiceD - song35voiceA
.byte $80
.byte $80

song3voiceA:
song3voiceD:
.byte EIGHTH_NOTE
.byte C_4
.byte Db_4
.byte D_4
.byte HALF_NOTE
.byte Eb_4
.byte SONG_END

song3voiceB:
.byte EIGHTH_NOTE
.byte A_4
.byte Bb_4
.byte B_4
.byte HALF_NOTE
.byte C_5

song3voiceC:
.byte EIGHTH_NOTE
.byte F_4
.byte Gb_4
.byte G_4
.byte HALF_NOTE
.byte Ab_4

song8voiceA:
.byte HALF_NOTE
.byte Bb_4
.byte EIGHTH_TRIPLET
.byte REST
.byte REST
.byte Bb_4
.byte Bb_4
.byte Bb_4
.byte Bb_4
.byte Bb_4
.byte REST
.byte Ab_4
.byte QUARTER_NOTE
.byte Bb_4
.byte EIGHTH_TRIPLET
.byte REST
.byte REST
.byte Bb_4
.byte Bb_4
.byte Bb_4
.byte Bb_4
.byte Bb_4
.byte REST
.byte Ab_4
.byte QUARTER_NOTE
.byte Bb_4
.byte EIGHTH_TRIPLET
.byte REST
.byte REST
.byte Bb_4
.byte Bb_4
.byte Bb_4
.byte Bb_4
.byte SIXTEENTH_NOTE
.byte Bb_4
.byte REST
.byte F_4
.byte F_4
.byte F_4
.byte REST
.byte F_4
.byte F_4
.byte F_4
.byte REST
.byte F_4
.byte F_4
.byte EIGHTH_NOTE
.byte F_4
.byte F_4

song6voiceA:
.byte SONG_END

song8voiceC:
.byte QUARTER_NOTE
.byte Bb_3
.byte EIGHTH_TRIPLET
.byte Bb_3
.byte Bb_3
.byte Bb_3
.byte QUARTER_NOTE
.byte Bb_3
.byte EIGHTH_TRIPLET
.byte Bb_3
.byte Bb_3
.byte Bb_3
.byte QUARTER_NOTE
.byte Ab_3
.byte EIGHTH_TRIPLET

song6voiceC:
song7voiceC:
.byte Ab_3
.byte Ab_3
.byte Ab_3
.byte QUARTER_NOTE
.byte Ab_3
.byte EIGHTH_TRIPLET
.byte Ab_3
.byte Ab_3
.byte Ab_3
.byte QUARTER_NOTE
.byte Gb_3
.byte EIGHTH_TRIPLET
.byte Gb_3
.byte Gb_3
.byte Gb_3
.byte QUARTER_NOTE
.byte Gb_3
.byte EIGHTH_TRIPLET
.byte Gb_3
.byte Gb_3
.byte Gb_3
.byte QUARTER_NOTE
.byte F_3
.byte F_3
.byte F_3
.byte EIGHTH_NOTE
.byte G_3
.byte A_3

song8voiceB:
.byte HALF_NOTE
.byte D_4
.byte EIGHTH_TRIPLET
.byte REST
.byte REST
.byte D_4
.byte D_4
.byte D_4
.byte D_4
.byte C_4
.byte REST
.byte C_4
.byte QUARTER_NOTE
.byte C_4
.byte REST
.byte EIGHTH_TRIPLET
.byte C_4
.byte C_4
.byte C_4
.byte Db_4
.byte REST
.byte Db_4
.byte QUARTER_NOTE
.byte Db_4
.byte EIGHTH_TRIPLET
.byte REST
.byte REST
.byte Db_4
.byte Db_4
.byte Db_4
.byte Db_4
.byte SIXTEENTH_NOTE
.byte Db_4
.byte REST
.byte A_3
.byte A_3
.byte EIGHTH_NOTE
.byte A_3
.byte SIXTEENTH_NOTE
.byte A_3
.byte A_3
.byte EIGHTH_NOTE
.byte A_3
.byte SIXTEENTH_NOTE
.byte A_3
.byte A_3
.byte EIGHTH_NOTE
.byte A_3
.byte A_3

song6voiceB:
song7voiceB:
song8voiceD:
.byte $B1
.byte $90
.byte $90
.byte $90
.byte $B1
.byte $90
.byte $90
.byte $90
.byte $B1
.byte $90
.byte $90
.byte $90
.byte $D0
.byte $D0
.byte $D0
.byte D_6
.byte D_6

song0voiceA:
song4voiceA:
song9voiceA:
song12voiceA:
.byte EIGHTH_NOTE
.byte Bb_4
.byte REST
.byte DOTTED_QUARTER_NOTE
.byte F_4
.byte SIXTEENTH_NOTE
.byte REST
.byte Bb_4
.byte Bb_4
.byte C_5
.byte D_5
.byte Eb_5
.byte HALF_NOTE
.byte F_5
.byte EIGHTH_NOTE
.byte REST
.byte F_5
.byte EIGHTH_TRIPLET
.byte F_5
.byte Gb_5
.byte Ab_5
.byte SONG_END

song0voiceB:
song4voiceB:
song9voiceB:
song12voiceB:
.byte EIGHTH_NOTE
.byte D_4
.byte REST
.byte EIGHTH_TRIPLET
.byte D_4
.byte D_4
.byte C_4
.byte EIGHTH_NOTE
.byte D_4
.byte SIXTEENTH_NOTE

song6voiceD:
song7voiceD:
.byte REST
.byte D_4
.byte D_4
.byte Eb_4
.byte F_4
.byte G_4
.byte EIGHTH_NOTE
.byte Ab_4
.byte SIXTEENTH_NOTE
.byte REST
.byte Bb_4
.byte Bb_4
.byte C_5
.byte D_5
.byte Eb_5
.byte QUARTER_NOTE
.byte F_5
.byte EIGHTH_TRIPLET
.byte Ab_4
.byte Bb_4
.byte C_5

song0voiceC:
song4voiceC:
song9voiceC:
song12voiceC:
.byte QUARTER_NOTE
.byte Bb_3
.byte EIGHTH_TRIPLET
.byte Bb_3
.byte Bb_3
.byte Ab_3
.byte QUARTER_NOTE
.byte Bb_3
.byte Bb_3
.byte Ab_3
.byte EIGHTH_TRIPLET
.byte Ab_3
.byte Ab_3
.byte Gb_3
.byte QUARTER_NOTE
.byte Ab_3
.byte Ab_3

song10voiceA:
.byte HALF_NOTE
.byte Bb_5
.byte EIGHTH_TRIPLET
.byte REST
.byte Bb_5
.byte Bb_5
.byte Bb_5
.byte Ab_5
.byte Gb_5
.byte EIGHTH_TRIPLET
.byte Ab_5
.byte REST
.byte Gb_5
.byte HALF_NOTE
.byte F_5
.byte QUARTER_NOTE
.byte F_5
.byte EIGHTH_NOTE
.byte Eb_5
.byte SIXTEENTH_NOTE
.byte Eb_5
.byte F_5
.byte HALF_NOTE
.byte Gb_5
.byte EIGHTH_NOTE
.byte F_5
.byte Eb_5
.byte EIGHTH_NOTE
.byte Db_5
.byte SIXTEENTH_NOTE
.byte Db_5
.byte Eb_5
.byte HALF_NOTE
.byte F_5
.byte EIGHTH_NOTE
.byte Eb_5
.byte Db_5
.byte SONG_END

song10voiceB:
.byte EIGHTH_NOTE
.byte Db_5
.byte SIXTEENTH_NOTE
.byte REST
.byte Gb_4
.byte Gb_4
.byte Ab_4
.byte Bb_4
.byte C_5
.byte EIGHTH_TRIPLET
.byte Db_5
.byte REST
.byte Db_5
.byte Db_5
.byte C_5
.byte Bb_4
.byte Db_5
.byte REST
.byte Ab_4
.byte Ab_4
.byte Ab_4
.byte Gb_4
.byte Ab_4
.byte REST
.byte Ab_4
.byte Ab_4
.byte Gb_4
.byte Ab_4
.byte EIGHTH_NOTE
.byte Gb_4
.byte SIXTEENTH_NOTE
.byte Gb_4
.byte F_4
.byte EIGHTH_NOTE
.byte Gb_4
.byte SIXTEENTH_NOTE
.byte Gb_4
.byte Ab_4
.byte QUARTER_NOTE
.byte Bb_4
.byte EIGHTH_NOTE
.byte Ab_4
.byte Gb_4
.byte EIGHTH_NOTE
.byte F_4
.byte SIXTEENTH_NOTE
.byte F_4
.byte Eb_4
.byte EIGHTH_NOTE
.byte F_4
.byte SIXTEENTH_NOTE
.byte F_4
.byte Gb_4
.byte QUARTER_NOTE
.byte Ab_4
.byte EIGHTH_NOTE
.byte Gb_4
.byte F_4

song10voiceC:
.byte QUARTER_NOTE
.byte Gb_3
.byte EIGHTH_TRIPLET
.byte Gb_3
.byte Gb_3
.byte E_3
.byte QUARTER_NOTE
.byte Gb_3
.byte Gb_3
.byte Db_4
.byte EIGHTH_TRIPLET
.byte Db_4
.byte Db_4
.byte C_4
.byte QUARTER_NOTE
.byte Db_4
.byte Db_4
.byte B_3
.byte EIGHTH_TRIPLET
.byte B_3
.byte B_3
.byte Bb_3
.byte QUARTER_NOTE
.byte B_3
.byte EIGHTH_TRIPLET
.byte B_3
.byte B_3
.byte B_3
.byte QUARTER_NOTE
.byte Bb_3
.byte EIGHTH_TRIPLET
.byte Bb_3
.byte Bb_3
.byte Ab_3
.byte QUARTER_NOTE
.byte Bb_3
.byte EIGHTH_TRIPLET
.byte Bb_3
.byte Bb_3
.byte Bb_3

song0voiceD:
song4voiceD:
song9voiceD:
song10voiceD:
song12voiceD:
.byte $D0
.byte $90
.byte $90
.byte $90
.byte $D0
.byte $D0
.byte SONG_END

song11voiceA:
song14voiceA:
.byte EIGHTH_NOTE
.byte C_5
.byte SIXTEENTH_NOTE
.byte C_5
.byte D_5
.byte HALF_NOTE
.byte E_5
.byte QUARTER_NOTE
.byte G_5
.byte SIXTEENTH_NOTE
.byte F_5
.byte REST
.byte F_4
.byte F_4
.byte F_4
.byte REST
.byte F_4
.byte F_4
.byte F_4
.byte REST
.byte F_4
.byte F_4
.byte EIGHTH_NOTE
.byte F_4
.byte F_4
.byte SONG_END

song11voiceB:
song14voiceB:
.byte QUARTER_NOTE
.byte E_4
.byte EIGHTH_NOTE
.byte E_4
.byte SIXTEENTH_NOTE
.byte E_4
.byte F_4
.byte EIGHTH_NOTE
.byte G_4
.byte SIXTEENTH_NOTE
.byte G_4
.byte A_4
.byte EIGHTH_NOTE
.byte Bb_4
.byte C_5
.byte EIGHTH_NOTE
.byte A_4
.byte SIXTEENTH_NOTE
.byte A_3
.byte A_3
.byte EIGHTH_NOTE
.byte A_3
.byte SIXTEENTH_NOTE
.byte A_3
.byte A_3
.byte EIGHTH_NOTE
.byte A_3
.byte SIXTEENTH_NOTE
.byte A_3
.byte A_3
.byte EIGHTH_NOTE
.byte A_3
.byte A_3

song11voiceC:
song14voiceC:
.byte QUARTER_NOTE
.byte C_4
.byte EIGHTH_TRIPLET
.byte C_4
.byte C_4
.byte B_3
.byte QUARTER_NOTE
.byte C_4
.byte EIGHTH_TRIPLET
.byte C_4
.byte C_4
.byte C_4
.byte QUARTER_NOTE
.byte F_3
.byte F_3
.byte F_3
.byte EIGHTH_NOTE
.byte G_3
.byte A_3

song13voiceA:
.byte DOTTED_HALF_NOTE
.byte Bb_5
.byte QUARTER_NOTE
.byte Db_6
.byte EIGHTH_NOTE
.byte C_6
.byte REST
.byte HALF_NOTE
.byte A_5
.byte QUARTER_NOTE
.byte F_5
.byte DOTTED_HALF_NOTE
.byte Gb_5
.byte QUARTER_NOTE
.byte Bb_5
.byte EIGHTH_NOTE
.byte A_5
.byte REST
.byte HALF_NOTE
.byte F_5
.byte QUARTER_NOTE
.byte F_5
.byte DOTTED_HALF_NOTE
.byte Gb_5
.byte QUARTER_NOTE
.byte Bb_5
.byte EIGHTH_NOTE
.byte A_5
.byte REST
.byte HALF_NOTE
.byte F_5
.byte QUARTER_NOTE
.byte D_5
.byte DOTTED_HALF_NOTE
.byte Eb_5
.byte QUARTER_NOTE
.byte Gb_5
.byte EIGHTH_NOTE
.byte F_5
.byte REST
.byte HALF_NOTE
.byte Db_5
.byte QUARTER_NOTE
.byte Bb_4
.byte SONG_END

song13voiceB:
.byte DOTTED_HALF_NOTE
.byte Db_5
.byte QUARTER_NOTE
.byte E_5
.byte EIGHTH_NOTE
.byte Eb_5
.byte REST
.byte HALF_NOTE
.byte C_5
.byte QUARTER_NOTE
.byte A_4
.byte DOTTED_HALF_NOTE
.byte B_4
.byte QUARTER_NOTE
.byte Db_5
.byte EIGHTH_NOTE
.byte C_5
.byte REST
.byte HALF_NOTE
.byte A_4
.byte QUARTER_NOTE
.byte A_4
.byte DOTTED_HALF_NOTE
.byte B_4
.byte QUARTER_NOTE
.byte Db_5
.byte EIGHTH_NOTE
.byte C_5
.byte REST
.byte HALF_NOTE
.byte A_4
.byte QUARTER_NOTE
.byte A_4
.byte DOTTED_HALF_NOTE
.byte Gb_4
.byte QUARTER_NOTE
.byte B_4
.byte EIGHTH_NOTE
.byte Bb_4
.byte REST
.byte HALF_NOTE
.byte F_4
.byte QUARTER_NOTE
.byte Db_4

song13voiceC:
.byte QUARTER_NOTE
.byte Gb_3
.byte EIGHTH_TRIPLET
.byte Gb_3
.byte Gb_3
.byte E_3
.byte QUARTER_NOTE
.byte Gb_3
.byte Gb_3
.byte F_3
.byte EIGHTH_TRIPLET
.byte F_3
.byte F_3
.byte Eb_3
.byte QUARTER_NOTE
.byte F_3
.byte F_3
.byte EIGHTH_TRIPLET
.byte E_3
.byte Bb_3
.byte Db_4
.byte E_4
.byte Bb_4
.byte Db_5
.byte HALF_NOTE
.byte E_5
.byte QUARTER_NOTE
.byte F_5
.byte EIGHTH_TRIPLET
.byte F_3
.byte F_3
.byte F_3
.byte HALF_NOTE
.byte F_3
.byte EIGHTH_TRIPLET
.byte E_3
.byte Bb_3
.byte Db_4
.byte E_4
.byte Bb_4
.byte Db_5
.byte HALF_NOTE
.byte E_5
.byte QUARTER_NOTE
.byte F_5
.byte EIGHTH_TRIPLET
.byte F_3
.byte F_3
.byte F_3
.byte HALF_NOTE
.byte F_3
.byte QUARTER_NOTE
.byte B_3
.byte EIGHTH_TRIPLET
.byte B_3
.byte B_3
.byte Bb_3
.byte QUARTER_NOTE
.byte B_3
.byte EIGHTH_TRIPLET
.byte B_3
.byte B_3
.byte B_3
.byte QUARTER_NOTE
.byte Bb_3
.byte EIGHTH_TRIPLET
.byte Bb_3
.byte Bb_3
.byte Ab_3
.byte QUARTER_NOTE
.byte Bb_3
.byte EIGHTH_TRIPLET
.byte Bb_3
.byte Bb_3
.byte Bb_3

song11voiceD:
song13voiceD:
song14voiceD:
.byte $D0
.byte $90
.byte $90
.byte $90
.byte $D0
.byte $D0
.byte SONG_END

song15voiceA:
song15voiceD:
.byte QUARTER_NOTE
.byte G_4
.byte D_5
.byte G_4
.byte D_5
.byte G_4
.byte D_5
.byte G_4
.byte D_5
.byte Gb_4
.byte D_5
.byte Gb_4
.byte D_5
.byte Gb_4
.byte D_5
.byte Gb_4
.byte D_5
.byte F_4
.byte D_5
.byte F_4
.byte D_5
.byte F_4
.byte D_5
.byte F_4
.byte D_5
.byte E_4
.byte D_5
.byte E_4
.byte D_5
.byte E_4
.byte D_5
.byte E_4
.byte D_5
.byte SONG_END

song15voiceB:
.byte EIGHTH_NOTE
.byte REST
.byte QUARTER_NOTE
.byte Bb_4
.byte Eb_5
.byte Bb_4
.byte Eb_5
.byte Bb_4
.byte Eb_5
.byte Bb_4
.byte Eb_5
.byte A_4
.byte Eb_5
.byte A_4
.byte Eb_5
.byte A_4
.byte Eb_5
.byte A_4
.byte Eb_5
.byte Ab_4
.byte Eb_5
.byte Ab_4
.byte Eb_5
.byte Ab_4
.byte Eb_5
.byte Ab_4
.byte Eb_5
.byte G_4
.byte Eb_5
.byte G_4
.byte Eb_5
.byte G_4
.byte Eb_5
.byte G_4
.byte Eb_5

song15voiceC:
.byte HALF_NOTE
.byte G_4
.byte REST
.byte Bb_4
.byte D_5
.byte Db_5
.byte Gb_4
.byte REST
.byte REST
.byte F_4
.byte REST
.byte QUARTER_NOTE
.byte F_4
.byte EIGHTH_NOTE
.byte REST
.byte Ab_4
.byte QUARTER_NOTE
.byte REST
.byte Db_5
.byte HALF_NOTE
.byte C_5
.byte E_4
.byte REST
.byte REST

song16voiceA:
song16voiceD:
.byte QUARTER_NOTE
.byte Eb_4
.byte C_5
.byte Eb_4
.byte C_5
.byte Eb_4
.byte C_5
.byte Eb_4
.byte C_5
.byte D_4
.byte C_5
.byte D_4
.byte C_5
.byte D_4
.byte C_5
.byte D_4
.byte C_5
.byte C_4
.byte A_4
.byte Gb_4
.byte C_5
.byte A_4
.byte Eb_5
.byte Eb_5
.byte Eb_5
.byte A_5
.byte A_5
.byte SONG_END

song16voiceB:
.byte EIGHTH_NOTE
.byte REST
.byte QUARTER_NOTE
.byte G_4
.byte D_5
.byte G_4
.byte D_5
.byte G_4
.byte D_5
.byte G_4
.byte D_5
.byte G_4
.byte D_5
.byte G_4
.byte D_5
.byte G_4
.byte D_5
.byte G_4
.byte D_5
.byte Gb_4
.byte C_5
.byte A_4
.byte Eb_5
.byte C_5
.byte C_5
.byte Gb_5
.byte Gb_5
.byte Gb_5
.byte C_6

song16voiceC:
.byte EIGHTH_NOTE
.byte Eb_4
.byte D_4
.byte HALF_NOTE
.byte Eb_4
.byte QUARTER_NOTE
.byte REST
.byte G_4
.byte EIGHTH_NOTE
.byte REST
.byte Eb_5
.byte QUARTER_NOTE
.byte REST
.byte D_5
.byte EIGHTH_NOTE
.byte D_4
.byte Db_4
.byte HALF_NOTE
.byte D_4
.byte QUARTER_NOTE
.byte REST
.byte G_4
.byte EIGHTH_NOTE
.byte REST
.byte D_5
.byte QUARTER_NOTE
.byte REST
.byte Db_5
.byte EIGHTH_NOTE
.byte D_4
.byte Gb_4
.byte A_4
.byte Gb_4
.byte A_4
.byte C_5
.byte A_4
.byte C_5
.byte Eb_5
.byte C_5
.byte Eb_5
.byte Gb_5
.byte A_5
.byte Gb_5
.byte Eb_5
.byte C_5
.byte Eb_5
.byte C_5
.byte A_4
.byte Gb_4

song2voiceA:
song2voiceD:
.byte EIGHTH_TRIPLET
.byte D_4
.byte D_4
.byte D_4
.byte DOTTED_HALF_NOTE
.byte G_4
.byte SIXTEENTH_NOTE
.byte G_4
.byte A_4
.byte B_4
.byte C_5
.byte DOTTED_HALF_NOTE
.byte D_5
.byte EIGHTH_TRIPLET
.byte D_5
.byte D_5
.byte D_5
.byte DOTTED_HALF_NOTE
.byte G_5
.byte SIXTEENTH_NOTE
.byte G_5
.byte A_5
.byte B_5
.byte C_6
.byte DOTTED_HALF_NOTE
.byte D_6
.byte SIXTEENTH_NOTE
.byte D_4
.byte D_4
.byte REST
.byte D_4
.byte DOTTED_QUARTER_NOTE
.byte G_4
.byte SONG_END

song2voiceB:
.byte HALF_NOTE
.byte REST
.byte EIGHTH_TRIPLET
.byte D_3
.byte D_3
.byte D_3
.byte DOTTED_HALF_NOTE
.byte G_3
.byte SIXTEENTH_NOTE
.byte G_3
.byte A_3
.byte B_3
.byte C_4
.byte DOTTED_HALF_NOTE
.byte D_4
.byte EIGHTH_TRIPLET
.byte D_4
.byte D_4
.byte D_4
.byte DOTTED_HALF_NOTE
.byte G_4
.byte SIXTEENTH_NOTE
.byte G_4
.byte A_4
.byte B_4
.byte C_5
.byte QUARTER_NOTE
.byte D_5
.byte SIXTEENTH_NOTE
.byte Gb_3
.byte EIGHTH_NOTE
.byte Gb_3
.byte SIXTEENTH_NOTE
.byte Gb_3
.byte DOTTED_QUARTER_NOTE
.byte B_3

song2voiceC:
.byte QUARTER_NOTE
.byte REST
.byte HALF_NOTE
.byte G_4
.byte G_4
.byte F_4
.byte F_4
.byte Eb_4
.byte Eb_4
.byte D_4
.byte QUARTER_NOTE
.byte D_4
.byte SIXTEENTH_NOTE
.byte C_4
.byte C_4
.byte REST
.byte C_4
.byte DOTTED_QUARTER_NOTE
.byte D_4

song5voiceA:
.byte DOTTED_QUARTER_NOTE
.byte B_3
.byte QUARTER_NOTE
.byte C_4
.byte EIGHTH_NOTE
.byte Ab_3
.byte DOTTED_HALF_NOTE
.byte A_3
.byte HALF_NOTE
.byte REST
.byte DOTTED_QUARTER_NOTE
.byte B_3
.byte QUARTER_NOTE
.byte C_4
.byte EIGHTH_NOTE
.byte Ab_3
.byte DOTTED_HALF_NOTE
.byte A_3
.byte HALF_NOTE
.byte REST
.byte DOTTED_QUARTER_NOTE
.byte B_3
.byte QUARTER_NOTE
.byte C_4
.byte EIGHTH_NOTE
.byte F_4
.byte HALF_NOTE
.byte E_4
.byte EIGHTH_NOTE
.byte REST
.byte B_3
.byte QUARTER_TRIPLET
.byte D_4
.byte Db_4
.byte A_3
.byte C_4
.byte B_3
.byte Ab_3
.byte B_3
.byte Bb_3
.byte G_3
.byte DOTTED_QUARTER_NOTE
.byte F_4
.byte QUARTER_NOTE
.byte Gb_4
.byte EIGHTH_NOTE
.byte D_4
.byte DOTTED_HALF_NOTE
.byte Eb_4
.byte HALF_NOTE
.byte REST
.byte DOTTED_QUARTER_NOTE
.byte F_4
.byte QUARTER_NOTE
.byte Gb_4
.byte EIGHTH_NOTE
.byte D_4
.byte DOTTED_HALF_NOTE
.byte Eb_4
.byte HALF_NOTE
.byte REST
.byte DOTTED_QUARTER_NOTE
.byte F_4
.byte QUARTER_NOTE
.byte Gb_4
.byte EIGHTH_NOTE
.byte B_4
.byte HALF_NOTE
.byte Bb_4
.byte EIGHTH_NOTE
.byte REST
.byte F_4
.byte QUARTER_TRIPLET
.byte A_4
.byte Ab_4
.byte Eb_4
.byte G_4
.byte Gb_4
.byte D_4
.byte Gb_4
.byte F_4
.byte Db_4
.byte SONG_END

song5voiceB:
.byte DOTTED_QUARTER_NOTE
.byte F_3
.byte QUARTER_NOTE
.byte Gb_3
.byte EIGHTH_NOTE
.byte D_3
.byte DOTTED_HALF_NOTE
.byte Eb_3
.byte HALF_NOTE
.byte REST
.byte DOTTED_QUARTER_NOTE
.byte F_3
.byte QUARTER_NOTE
.byte Gb_3
.byte EIGHTH_NOTE
.byte D_3
.byte DOTTED_HALF_NOTE
.byte Eb_3
.byte HALF_NOTE
.byte REST
.byte DOTTED_QUARTER_NOTE
.byte F_3
.byte QUARTER_NOTE
.byte Gb_3
.byte EIGHTH_NOTE
.byte B_3
.byte HALF_NOTE
.byte Bb_3
.byte EIGHTH_NOTE
.byte REST
.byte F_3
.byte QUARTER_TRIPLET
.byte Ab_3
.byte G_3
.byte Eb_3
.byte Gb_3
.byte F_3
.byte D_3
.byte F_3
.byte E_3
.byte Db_3
.byte DOTTED_QUARTER_NOTE
.byte B_3
.byte QUARTER_NOTE
.byte C_4
.byte EIGHTH_NOTE
.byte Ab_3
.byte DOTTED_HALF_NOTE
.byte A_3
.byte HALF_NOTE
.byte REST
.byte DOTTED_QUARTER_NOTE
.byte B_3
.byte QUARTER_NOTE
.byte C_4
.byte EIGHTH_NOTE
.byte Ab_3
.byte DOTTED_HALF_NOTE
.byte A_3
.byte HALF_NOTE
.byte REST
.byte DOTTED_QUARTER_NOTE
.byte B_3
.byte QUARTER_NOTE
.byte C_4
.byte EIGHTH_NOTE
.byte F_4
.byte HALF_NOTE
.byte E_4
.byte EIGHTH_NOTE
.byte REST
.byte B_3
.byte QUARTER_TRIPLET
.byte D_4
.byte Db_4
.byte A_3
.byte C_4
.byte B_3
.byte Ab_3
.byte B_3
.byte Bb_3
.byte G_3

song5voiceC:
.byte $F8
.byte EIGHTH_NOTE
.byte C_4
.byte C_4
.byte $F0
.byte $F8
.byte EIGHTH_NOTE
.byte B_3
.byte B_3
.byte $F0
.byte $F8
.byte EIGHTH_NOTE
.byte Bb_3
.byte Bb_3
.byte $F0
.byte $F4
.byte EIGHTH_NOTE
.byte A_3
.byte A_3
.byte $F0
.byte $F8
.byte EIGHTH_NOTE
.byte Gb_4
.byte Gb_4
.byte $F0
.byte $F8
.byte EIGHTH_NOTE
.byte F_4
.byte F_4
.byte $F0
.byte $F8
.byte EIGHTH_NOTE
.byte E_4
.byte E_4
.byte $F0
.byte $F4
.byte EIGHTH_NOTE
.byte Eb_4
.byte Eb_4
.byte $F0

song5voiceD:
.byte $49
.byte SONG_END

song1voiceA:
song1voiceD:
.byte EIGHTH_NOTE
.byte G_3
.byte C_4
.byte F_4
.byte Ab_3
.byte Db_4
.byte Gb_4
.byte A_3
.byte D_4
.byte G_4
.byte QUARTER_TRIPLET
.byte Ab_4
.byte A_4
.byte HALF_NOTE
.byte Bb_4
.byte SONG_END

song1voiceB:
.byte SIXTEENTH_NOTE
.byte REST
.byte EIGHTH_NOTE
.byte G_3
.byte C_4
.byte F_4
.byte Ab_3
.byte Db_4
.byte Gb_4
.byte A_3
.byte D_4
.byte SIXTEENTH_NOTE
.byte G_4
.byte QUARTER_TRIPLET
.byte Eb_4
.byte E_4
.byte HALF_NOTE
.byte F_4

song1voiceC:
.byte DOTTED_QUARTER_NOTE
.byte G_3
.byte Ab_3
.byte A_3
.byte QUARTER_TRIPLET
.byte Bb_4
.byte B_4
.byte HALF_NOTE
.byte C_5

song17voiceA:
song18voiceA:
.byte QUARTER_NOTE
.byte G_6
.byte G_5
.byte C_6
.byte E_6
.byte Eb_6
.byte G_5
.byte B_6
.byte B_5
.byte A_6
.byte C_6
.byte E_6
.byte A_6
.byte G_6
.byte C_6
.byte D_6
.byte E_6
.byte A_6
.byte C_6
.byte F_6
.byte A_6
.byte Ab_6
.byte C_6
.byte D_6
.byte F_6
.byte E_6
.byte G_5
.byte C_6
.byte E_6
.byte D_6
.byte A_5
.byte B_5
.byte D_6
.byte SONG_END

song17voiceC:
.byte QUARTER_TRIPLET
.byte REST
.byte REST
.byte REST
.byte REST
.byte REST
.byte REST
.byte REST
.byte QUARTER_NOTE
.byte REST
.byte G_3
.byte A_3
.byte B_3

song18voiceC:
.byte QUARTER_NOTE
.byte C_4
.byte G_4
.byte G_3
.byte G_4
.byte B_3
.byte G_4
.byte G_3
.byte G_4
.byte C_4
.byte G_4
.byte G_3
.byte G_4
.byte C_4
.byte C_4
.byte D_4
.byte E_4
.byte F_4
.byte C_5
.byte C_4
.byte C_5
.byte F_4
.byte C_5
.byte C_4
.byte C_5
.byte E_4
.byte C_5
.byte G_3
.byte G_4
.byte B_3
.byte G_3
.byte A_3
.byte B_3

song17voiceB:
song18voiceB:
.byte QUARTER_TRIPLET
.byte REST
.byte REST
.byte REST
.byte REST
.byte REST
.byte REST
.byte REST
.byte REST

song17voiceD:
song18voiceD:
.byte $C9
.byte SONG_END

song19voiceA:
.byte DOTTED_HALF_NOTE
.byte G_5
.byte QUARTER_NOTE
.byte E_5
.byte HALF_NOTE
.byte Eb_5
.byte B_5
.byte HALF_NOTE
.byte A_5
.byte REST
.byte G_5
.byte REST
.byte DOTTED_HALF_NOTE
.byte A_5
.byte QUARTER_NOTE
.byte B_5
.byte HALF_NOTE
.byte D_6
.byte C_6
.byte DOTTED_HALF_NOTE
.byte G_5
.byte QUARTER_NOTE
.byte E_5
.byte HALF_NOTE
.byte D_5
.byte REST
.byte SONG_END

song19voiceB:
.byte DOTTED_HALF_NOTE
.byte E_5
.byte QUARTER_NOTE
.byte C_5
.byte HALF_NOTE
.byte B_4
.byte Eb_5
.byte E_5
.byte REST
.byte E_5
.byte REST
.byte DOTTED_HALF_NOTE
.byte F_5
.byte QUARTER_NOTE
.byte F_5
.byte HALF_NOTE
.byte F_5
.byte F_5
.byte DOTTED_HALF_NOTE
.byte C_5
.byte QUARTER_NOTE
.byte C_5
.byte HALF_NOTE
.byte B_4
.byte REST

song20voiceA:
song22voiceA:
.byte EIGHTH_TRIPLET
.byte G_5
.byte EIGHTH_NOTE
.byte E_5
.byte EIGHTH_TRIPLET
.byte Eb_5
.byte SIXTEENTH_NOTE
.byte Eb_5
.byte DOTTED_QUARTER_NOTE
.byte G_5
.byte SIXTEENTH_NOTE
.byte B_5
.byte EIGHTH_TRIPLET
.byte A_5
.byte EIGHTH_NOTE
.byte E_5
.byte QUARTER_TRIPLET
.byte G_5
.byte EIGHTH_TRIPLET
.byte A_5
.byte EIGHTH_NOTE
.byte B_5
.byte SONG_END

song21voiceA:
.byte QUARTER_NOTE
.byte D_6
.byte HALF_NOTE
.byte C_6
.byte QUARTER_NOTE
.byte A_5
.byte EIGHTH_TRIPLET
.byte G_5
.byte EIGHTH_NOTE
.byte E_5
.byte QUARTER_TRIPLET
.byte D_5
.byte SONG_END

song20voiceB:
song22voiceB:
.byte EIGHTH_TRIPLET
.byte E_5
.byte EIGHTH_NOTE
.byte C_5
.byte EIGHTH_TRIPLET
.byte B_4
.byte SIXTEENTH_NOTE
.byte B_4
.byte DOTTED_QUARTER_NOTE
.byte Eb_5
.byte SIXTEENTH_NOTE
.byte Eb_5
.byte EIGHTH_TRIPLET
.byte E_5
.byte EIGHTH_NOTE
.byte C_5
.byte QUARTER_TRIPLET
.byte E_5
.byte EIGHTH_TRIPLET
.byte C_5
.byte EIGHTH_NOTE
.byte D_5

song21voiceB:
.byte QUARTER_NOTE
.byte F_5
.byte HALF_NOTE
.byte E_5
.byte QUARTER_NOTE
.byte C_5
.byte EIGHTH_TRIPLET
.byte B_4
.byte EIGHTH_NOTE
.byte G_4
.byte QUARTER_TRIPLET
.byte F_4

song19voiceC:
song20voiceC:
song22voiceC:
.byte QUARTER_NOTE
.byte C_4
.byte G_4
.byte G_3
.byte G_4
.byte B_3
.byte G_4
.byte G_3
.byte G_4
.byte C_4
.byte G_4
.byte G_3
.byte G_4
.byte C_4
.byte C_4
.byte D_4
.byte E_4
.byte F_4
.byte C_5
.byte C_4
.byte C_5

song21voiceC:
.byte F_4
.byte C_5
.byte C_4
.byte C_5
.byte E_4
.byte C_5
.byte G_3
.byte G_4
.byte B_3
.byte G_3
.byte A_3
.byte B_3

song23voiceA:
.byte QUARTER_NOTE
.byte D_6
.byte HALF_NOTE
.byte C_6
.byte QUARTER_NOTE
.byte D_6
.byte QUARTER_TRIPLET
.byte E_6
.byte HALF_NOTE
.byte REST
.byte QUARTER_NOTE
.byte E_6
.byte E_6
.byte SONG_END

song23voiceB:
.byte QUARTER_NOTE
.byte F_5
.byte HALF_NOTE
.byte E_5
.byte QUARTER_NOTE
.byte F_5
.byte QUARTER_TRIPLET
.byte Ab_5
.byte HALF_NOTE
.byte REST
.byte QUARTER_NOTE
.byte Ab_5
.byte Ab_5

song23voiceC:
.byte F_4
.byte C_5
.byte C_4
.byte C_5
.byte E_4
.byte E_5
.byte B_4
.byte E_5
.byte E_4
.byte E_5
.byte B_4
.byte E_5

song19voiceD:
song20voiceD:
song21voiceD:
song22voiceD:
song23voiceD:
.byte $C8
.byte $11
.byte F_3
.byte $C8
.byte $D0
.byte SONG_END

song24voiceA:
.byte HALF_NOTE
.byte D_6
.byte C_6
.byte REST
.byte QUARTER_NOTE
.byte B_5
.byte A_5
.byte DOTTED_HALF_NOTE
.byte G_5
.byte QUARTER_NOTE
.byte E_5
.byte HALF_NOTE
.byte A_5
.byte E_5
.byte QUARTER_NOTE
.byte D_5
.byte E_5
.byte F_5
.byte Gb_5
.byte HALF_NOTE
.byte G_5
.byte E_5
.byte QUARTER_TRIPLET
.byte C_5
.byte REST
.byte SONG_END

song24voiceB:
.byte HALF_NOTE
.byte F_5
.byte F_5
.byte REST
.byte QUARTER_NOTE
.byte F_5
.byte F_5
.byte DOTTED_HALF_NOTE
.byte C_5
.byte QUARTER_NOTE
.byte G_4
.byte HALF_NOTE
.byte Db_5
.byte G_4
.byte QUARTER_NOTE
.byte F_4
.byte G_4
.byte A_4
.byte Bb_4
.byte HALF_NOTE
.byte B_4
.byte G_4
.byte QUARTER_NOTE
.byte E_4
.byte DOTTED_QUARTER_NOTE
.byte E_4
.byte SIXTEENTH_NOTE
.byte E_4
.byte DOTTED_QUARTER_NOTE
.byte REST
.byte SIXTEENTH_NOTE
.byte F_4
.byte DOTTED_QUARTER_NOTE
.byte G_4
.byte SIXTEENTH_NOTE
.byte F_4
.byte QUARTER_TRIPLET
.byte E_4

song24voiceC:
.byte QUARTER_NOTE
.byte F_4
.byte C_5
.byte C_4
.byte C_5
.byte F_4
.byte C_5
.byte E_4
.byte D_4
.byte C_4
.byte G_4
.byte G_3
.byte G_4
.byte Db_4
.byte G_3
.byte A_3
.byte G_3
.byte D_4
.byte E_4
.byte F_4
.byte Gb_4
.byte G_4
.byte G_3
.byte A_3
.byte B_3
.byte C_4
.byte DOTTED_QUARTER_NOTE
.byte C_4
.byte SIXTEENTH_NOTE
.byte C_4
.byte DOTTED_QUARTER_NOTE
.byte REST
.byte SIXTEENTH_NOTE
.byte D_4
.byte DOTTED_QUARTER_NOTE
.byte E_4
.byte SIXTEENTH_NOTE
.byte D_4
.byte QUARTER_NOTE
.byte C_4
.byte G_3
.byte A_3
.byte B_3

song24voiceD:
.byte $C8
.byte $11
.byte F_3
.byte $C8
.byte $D0
.byte SONG_END

song25voiceA:
.byte EIGHTH_NOTE
.byte Bb_4
.byte DOTTED_QUARTER_NOTE
.byte REST
.byte F_4
.byte F_4
.byte Bb_4
.byte EIGHTH_TRIPLET
.byte Ab_4
.byte Gb_4
.byte EIGHTH_NOTE
.byte Ab_4
.byte SIXTEENTH_NOTE
.byte REST
.byte EIGHTH_NOTE
.byte Bb_4
.byte DOTTED_QUARTER_NOTE
.byte REST
.byte Gb_4
.byte Gb_4
.byte Bb_4
.byte EIGHTH_TRIPLET
.byte A_4
.byte G_4
.byte EIGHTH_NOTE
.byte A_4
.byte SIXTEENTH_NOTE
.byte REST
.byte SONG_END

song25voiceB:
.byte QUARTER_NOTE
.byte REST
.byte EIGHTH_NOTE
.byte Bb_4
.byte DOTTED_QUARTER_NOTE
.byte REST
.byte F_4
.byte F_4
.byte Bb_4
.byte EIGHTH_TRIPLET
.byte Ab_4
.byte Gb_4
.byte EIGHTH_NOTE
.byte Ab_4
.byte SIXTEENTH_NOTE
.byte REST
.byte EIGHTH_NOTE
.byte Bb_4
.byte DOTTED_QUARTER_NOTE
.byte REST
.byte Gb_4
.byte Gb_4
.byte Bb_4
.byte EIGHTH_TRIPLET
.byte A_4
.byte G_4
.byte EIGHTH_NOTE
.byte A_4
.byte SIXTEENTH_NOTE
.byte REST

song25voiceC:
.byte DOTTED_HALF_NOTE
.byte Bb_3
.byte F_4
.byte EIGHTH_NOTE
.byte Bb_4
.byte DOTTED_HALF_NOTE
.byte Ab_3
.byte Eb_4
.byte EIGHTH_NOTE
.byte Ab_4
.byte DOTTED_HALF_NOTE
.byte Gb_3
.byte Db_4
.byte EIGHTH_NOTE
.byte Gb_4
.byte DOTTED_HALF_NOTE
.byte F_3
.byte C_4
.byte EIGHTH_NOTE
.byte F_4

song25voiceD:
.byte F_5
.byte SONG_END

song26voiceA:
.byte EIGHTH_NOTE
.byte Db_3
.byte REST
.byte EIGHTH_NOTE
.byte Db_3
.byte REST
.byte DOTTED_HALF_NOTE
.byte Bb_4
.byte SIXTEENTH_NOTE
.byte F_4
.byte DOTTED_QUARTER_NOTE
.byte Bb_4
.byte EIGHTH_TRIPLET
.byte Bb_4
.byte C_5
.byte D_5
.byte Eb_5
.byte EIGHTH_NOTE
.byte F_5
.byte REST
.byte DOTTED_HALF_NOTE
.byte Bb_4
.byte SIXTEENTH_NOTE
.byte F_4
.byte DOTTED_QUARTER_NOTE
.byte Bb_4
.byte EIGHTH_TRIPLET
.byte Bb_4
.byte C_5
.byte D_5
.byte Eb_5
.byte EIGHTH_NOTE
.byte F_5
.byte REST
.byte SONG_END

song26voiceD:
.byte $11
.byte $90
.byte $90
.byte SONG_END

song26voiceC:
.byte $F6
.byte DOTTED_QUARTER_NOTE
.byte Bb_3
.byte EIGHTH_TRIPLET
.byte Bb_3
.byte Bb_3
.byte DOTTED_QUARTER_NOTE
.byte Bb_3
.byte EIGHTH_TRIPLET
.byte Bb_3
.byte Bb_3
.byte $F0
.byte $F2
.byte DOTTED_QUARTER_NOTE
.byte Ab_3
.byte EIGHTH_TRIPLET
.byte Ab_3
.byte Ab_3
.byte DOTTED_QUARTER_NOTE
.byte Ab_3
.byte EIGHTH_TRIPLET
.byte Ab_3
.byte Ab_3
.byte $F0
.byte $F2
.byte DOTTED_QUARTER_NOTE
.byte Gb_3
.byte EIGHTH_TRIPLET
.byte Gb_3
.byte Gb_3
.byte DOTTED_QUARTER_NOTE
.byte Gb_3
.byte EIGHTH_TRIPLET
.byte Gb_3
.byte Gb_3
.byte $F0
.byte $F2
.byte DOTTED_QUARTER_NOTE
.byte F_3
.byte EIGHTH_TRIPLET
.byte F_3
.byte F_3
.byte DOTTED_QUARTER_NOTE
.byte F_3
.byte EIGHTH_TRIPLET
.byte F_3
.byte F_3
.byte $F0

song26voiceB:
.byte DOTTED_QUARTER_NOTE
.byte F_3
.byte EIGHTH_TRIPLET
.byte F_3
.byte Bb_2
.byte DOTTED_QUARTER_NOTE
.byte F_3
.byte EIGHTH_TRIPLET
.byte F_3
.byte Bb_2
.byte DOTTED_QUARTER_NOTE
.byte F_3
.byte EIGHTH_TRIPLET
.byte F_3
.byte Bb_2
.byte F_3
.byte Bb_2
.byte F_3
.byte Bb_2
.byte DOTTED_QUARTER_NOTE
.byte F_3
.byte EIGHTH_TRIPLET
.byte F_3
.byte Bb_2
.byte DOTTED_QUARTER_NOTE
.byte F_3
.byte EIGHTH_TRIPLET
.byte F_3
.byte Bb_2
.byte DOTTED_QUARTER_NOTE
.byte F_3
.byte EIGHTH_TRIPLET
.byte F_3
.byte Bb_2
.byte F_3
.byte Bb_2
.byte F_3
.byte Bb_2
.byte DOTTED_QUARTER_NOTE
.byte F_3
.byte EIGHTH_TRIPLET
.byte F_3
.byte Bb_2
.byte DOTTED_QUARTER_NOTE
.byte F_3
.byte EIGHTH_TRIPLET
.byte F_3
.byte Bb_2
.byte DOTTED_QUARTER_NOTE
.byte F_3
.byte EIGHTH_TRIPLET
.byte F_3
.byte Bb_2
.byte F_3
.byte Bb_2
.byte F_3
.byte Bb_2
.byte DOTTED_QUARTER_NOTE
.byte Eb_3
.byte Bb_3
.byte EIGHTH_TRIPLET
.byte Bb_3
.byte C_4
.byte D_4
.byte Eb_4
.byte DOTTED_QUARTER_NOTE
.byte F_4
.byte EIGHTH_TRIPLET
.byte Eb_3
.byte Ab_2
.byte Eb_3
.byte Ab_2
.byte Eb_3
.byte Ab_2
.byte DOTTED_QUARTER_NOTE
.byte Db_3
.byte EIGHTH_TRIPLET
.byte Db_3
.byte Gb_2
.byte DOTTED_QUARTER_NOTE
.byte Db_3
.byte EIGHTH_TRIPLET
.byte Db_3
.byte Gb_2
.byte DOTTED_QUARTER_NOTE
.byte Db_3
.byte EIGHTH_TRIPLET
.byte Db_3
.byte Gb_2
.byte Db_3
.byte Gb_2
.byte Db_3
.byte Gb_2
.byte DOTTED_QUARTER_NOTE
.byte C_3
.byte Bb_3
.byte EIGHTH_TRIPLET
.byte Bb_3
.byte C_4
.byte D_4
.byte Eb_4
.byte DOTTED_QUARTER_NOTE
.byte F_4
.byte EIGHTH_TRIPLET
.byte C_3
.byte F_2
.byte C_3
.byte F_2
.byte C_3
.byte F_2

song27voiceA:
song30voiceA:
.byte DOTTED_QUARTER_NOTE
.byte Bb_4
.byte REST
.byte SIXTEENTH_NOTE
.byte F_4
.byte DOTTED_QUARTER_NOTE
.byte Bb_4
.byte EIGHTH_TRIPLET
.byte Bb_4
.byte C_5
.byte D_5
.byte Eb_5
.byte EIGHTH_NOTE
.byte F_5
.byte DOTTED_QUARTER_NOTE
.byte REST
.byte F_5
.byte HALF_NOTE
.byte F_5
.byte Gb_5
.byte QUARTER_TRIPLET
.byte Ab_5
.byte SONG_END

song27voiceB:
song30voiceB:
.byte DOTTED_QUARTER_NOTE
.byte D_4
.byte REST
.byte HALF_NOTE
.byte D_4
.byte D_4
.byte QUARTER_TRIPLET
.byte C_4
.byte DOTTED_QUARTER_NOTE
.byte D_4
.byte EIGHTH_TRIPLET
.byte REST
.byte D_4
.byte D_4
.byte Eb_4
.byte F_4
.byte G_4
.byte DOTTED_QUARTER_NOTE
.byte Ab_4
.byte EIGHTH_TRIPLET
.byte REST
.byte Bb_4
.byte Bb_4
.byte C_5
.byte D_5
.byte Eb_5
.byte DOTTED_HALF_NOTE
.byte F_5
.byte HALF_NOTE
.byte Ab_4
.byte Bb_4
.byte QUARTER_TRIPLET
.byte C_5

song27voiceC:
song30voiceC:
.byte $F2
.byte DOTTED_QUARTER_NOTE
.byte Bb_3
.byte EIGHTH_TRIPLET
.byte Bb_3
.byte Bb_3
.byte DOTTED_QUARTER_NOTE
.byte Bb_3
.byte EIGHTH_TRIPLET
.byte Bb_3
.byte Bb_3
.byte $F0
.byte $F2
.byte DOTTED_QUARTER_NOTE
.byte Ab_3
.byte EIGHTH_TRIPLET
.byte Ab_3
.byte Ab_3
.byte DOTTED_QUARTER_NOTE
.byte Ab_3
.byte EIGHTH_TRIPLET
.byte Ab_3
.byte Ab_3
.byte $F0

song28voiceA:
.byte EIGHTH_NOTE
.byte Bb_5
.byte HALF_NOTE
.byte REST
.byte REST
.byte Bb_5
.byte Bb_5
.byte QUARTER_TRIPLET
.byte Ab_5
.byte Gb_5
.byte Ab_5
.byte HALF_NOTE
.byte REST
.byte Gb_5
.byte EIGHTH_NOTE
.byte F_5
.byte DOTTED_HALF_NOTE
.byte F_5
.byte DOTTED_QUARTER_NOTE
.byte Eb_5
.byte EIGHTH_TRIPLET
.byte Eb_5
.byte F_5
.byte EIGHTH_NOTE
.byte Gb_5
.byte DOTTED_QUARTER_NOTE
.byte F_5
.byte Eb_5
.byte Db_5
.byte EIGHTH_TRIPLET
.byte Db_5
.byte Eb_5
.byte EIGHTH_NOTE
.byte F_5
.byte DOTTED_QUARTER_NOTE
.byte Eb_5
.byte Db_5
.byte SONG_END

song28voiceB:
.byte DOTTED_QUARTER_NOTE
.byte Gb_4
.byte EIGHTH_TRIPLET
.byte REST
.byte Gb_4
.byte Gb_4
.byte Ab_4
.byte Bb_4
.byte C_5
.byte HALF_NOTE
.byte Db_5
.byte REST
.byte QUARTER_TRIPLET
.byte Db_5
.byte Db_5
.byte HALF_NOTE
.byte C_5
.byte Bb_4
.byte HALF_NOTE
.byte Db_5
.byte REST
.byte QUARTER_TRIPLET
.byte Bb_4
.byte HALF_NOTE
.byte Ab_4
.byte Ab_4
.byte Gb_4
.byte HALF_NOTE
.byte Ab_4
.byte REST
.byte QUARTER_TRIPLET
.byte Ab_4
.byte Ab_4
.byte HALF_NOTE
.byte Gb_4
.byte Ab_4
.byte DOTTED_QUARTER_NOTE
.byte Gb_4
.byte EIGHTH_TRIPLET
.byte Gb_4
.byte F_4
.byte DOTTED_QUARTER_NOTE
.byte Gb_4
.byte EIGHTH_TRIPLET
.byte Gb_4
.byte Ab_4
.byte DOTTED_HALF_NOTE
.byte Bb_4
.byte DOTTED_QUARTER_NOTE
.byte Ab_4
.byte Gb_4
.byte DOTTED_QUARTER_NOTE
.byte F_4
.byte EIGHTH_TRIPLET
.byte F_4
.byte Eb_4
.byte DOTTED_QUARTER_NOTE
.byte F_4
.byte EIGHTH_TRIPLET
.byte F_4
.byte Gb_4
.byte DOTTED_HALF_NOTE
.byte Ab_4
.byte DOTTED_QUARTER_NOTE
.byte Gb_4
.byte F_4

song27voiceD:
song28voiceD:
song30voiceD:
.byte $11
.byte $90
.byte $90
.byte SONG_END

song28voiceC:
.byte $F2
.byte DOTTED_QUARTER_NOTE
.byte Gb_3
.byte EIGHTH_TRIPLET
.byte Gb_3
.byte Gb_3
.byte DOTTED_QUARTER_NOTE
.byte Gb_3
.byte EIGHTH_TRIPLET
.byte Gb_3
.byte Gb_3
.byte $F0
.byte $F2
.byte DOTTED_QUARTER_NOTE
.byte Db_4
.byte EIGHTH_TRIPLET
.byte Db_4
.byte Db_4
.byte DOTTED_QUARTER_NOTE
.byte Db_4
.byte EIGHTH_TRIPLET
.byte Db_4
.byte Db_4
.byte $F0
.byte $F2
.byte DOTTED_QUARTER_NOTE
.byte B_3
.byte EIGHTH_TRIPLET
.byte B_3
.byte B_3
.byte DOTTED_QUARTER_NOTE
.byte B_3
.byte EIGHTH_TRIPLET
.byte B_3
.byte B_3
.byte $F0
.byte $F2
.byte DOTTED_QUARTER_NOTE
.byte Bb_3
.byte EIGHTH_TRIPLET
.byte Bb_3
.byte Bb_3
.byte DOTTED_QUARTER_NOTE
.byte Bb_3
.byte EIGHTH_TRIPLET
.byte Bb_3
.byte Bb_3
.byte $F0

song29voiceA:
song34voiceA:
.byte DOTTED_HALF_NOTE
.byte E_4
.byte DOTTED_QUARTER_NOTE
.byte E_4
.byte EIGHTH_TRIPLET
.byte E_4
.byte F_4
.byte DOTTED_QUARTER_NOTE
.byte G_4
.byte EIGHTH_TRIPLET
.byte G_4
.byte A_4
.byte DOTTED_QUARTER_NOTE
.byte Bb_4
.byte C_5
.byte A_3
.byte EIGHTH_TRIPLET
.byte A_3
.byte A_3
.byte DOTTED_QUARTER_NOTE
.byte Ab_3
.byte EIGHTH_TRIPLET
.byte Ab_3
.byte Ab_3
.byte DOTTED_QUARTER_NOTE
.byte G_3
.byte EIGHTH_TRIPLET
.byte G_3
.byte G_3
.byte DOTTED_QUARTER_NOTE
.byte Gb_3
.byte Gb_3
.byte SONG_END

song29voiceD:
song34voiceD:
.byte $11
.byte $90
.byte $90
.byte SONG_END

song29voiceB:
song34voiceB:
.byte DOTTED_QUARTER_NOTE
.byte C_5
.byte EIGHTH_TRIPLET
.byte C_5
.byte D_5
.byte EIGHTH_NOTE
.byte E_5
.byte DOTTED_HALF_NOTE
.byte G_5
.byte EIGHTH_TRIPLET
.byte F_5
.byte REST
.byte F_4
.byte F_4
.byte F_4
.byte REST
.byte F_4
.byte F_4
.byte F_4
.byte REST
.byte F_4
.byte F_4
.byte DOTTED_QUARTER_NOTE
.byte F_4
.byte F_4

song29voiceC:
song34voiceC:
.byte $F2
.byte DOTTED_QUARTER_NOTE
.byte C_4
.byte EIGHTH_TRIPLET
.byte C_4
.byte C_4
.byte DOTTED_QUARTER_NOTE
.byte C_4
.byte EIGHTH_TRIPLET
.byte C_4
.byte C_4
.byte $F0
.byte DOTTED_QUARTER_NOTE
.byte F_4
.byte EIGHTH_TRIPLET
.byte F_3
.byte F_3
.byte DOTTED_QUARTER_NOTE
.byte F_3
.byte EIGHTH_TRIPLET
.byte F_3
.byte F_3
.byte DOTTED_QUARTER_NOTE
.byte F_3
.byte EIGHTH_TRIPLET
.byte F_3
.byte F_3
.byte DOTTED_QUARTER_NOTE
.byte F_3
.byte EIGHTH_TRIPLET
.byte G_3
.byte A_3

song31voiceA:
.byte EIGHTH_NOTE
.byte Db_5
.byte DOTTED_HALF_NOTE
.byte REST
.byte E_5
.byte DOTTED_QUARTER_NOTE
.byte Eb_5
.byte REST
.byte EIGHTH_NOTE
.byte C_5
.byte DOTTED_HALF_NOTE
.byte A_4
.byte SONG_END

song31voiceB:
.byte EIGHTH_NOTE
.byte Bb_5
.byte DOTTED_HALF_NOTE
.byte REST
.byte Db_6
.byte DOTTED_QUARTER_NOTE
.byte C_6
.byte REST
.byte EIGHTH_NOTE
.byte A_5
.byte DOTTED_HALF_NOTE
.byte F_5

song31voiceC:
.byte $F2
.byte DOTTED_QUARTER_NOTE
.byte Gb_3
.byte EIGHTH_TRIPLET
.byte Gb_3
.byte Gb_3
.byte DOTTED_QUARTER_NOTE
.byte Gb_3
.byte EIGHTH_TRIPLET
.byte Gb_3
.byte Gb_3
.byte $F0
.byte $F2
.byte DOTTED_QUARTER_NOTE
.byte F_3
.byte EIGHTH_TRIPLET
.byte F_3
.byte F_3
.byte DOTTED_QUARTER_NOTE
.byte F_3
.byte EIGHTH_TRIPLET
.byte F_3
.byte F_3
.byte $F0

song31voiceD:
.byte $11
.byte $90
.byte $90
.byte SONG_END

song32voiceA:
.byte HALF_NOTE
.byte E_2
.byte Bb_2
.byte Db_3
.byte E_3
.byte QUARTER_TRIPLET
.byte Bb_3
.byte Db_4
.byte EIGHTH_NOTE
.byte E_4
.byte DOTTED_HALF_NOTE
.byte F_4
.byte HALF_NOTE
.byte F_3
.byte F_3
.byte QUARTER_TRIPLET
.byte F_3
.byte EIGHTH_NOTE
.byte F_3
.byte HALF_NOTE
.byte E_2
.byte Bb_2
.byte Db_3
.byte E_3
.byte QUARTER_TRIPLET
.byte Bb_3
.byte Db_4
.byte EIGHTH_NOTE
.byte E_4
.byte DOTTED_HALF_NOTE
.byte F_4
.byte HALF_NOTE
.byte F_3
.byte F_3
.byte QUARTER_TRIPLET
.byte F_3
.byte EIGHTH_NOTE
.byte F_3
.byte SONG_END

song32voiceB:
.byte EIGHTH_NOTE
.byte Gb_5
.byte DOTTED_HALF_NOTE
.byte REST
.byte Bb_5
.byte DOTTED_QUARTER_NOTE
.byte A_5
.byte REST
.byte EIGHTH_NOTE
.byte F_5
.byte DOTTED_HALF_NOTE
.byte F_5
.byte EIGHTH_NOTE
.byte Gb_5
.byte DOTTED_HALF_NOTE
.byte REST
.byte Bb_5
.byte DOTTED_QUARTER_NOTE
.byte A_5
.byte REST
.byte EIGHTH_NOTE
.byte F_5
.byte DOTTED_HALF_NOTE
.byte D_5

song32voiceC:
.byte $F2
.byte DOTTED_QUARTER_NOTE
.byte E_3
.byte EIGHTH_TRIPLET
.byte E_3
.byte E_3
.byte DOTTED_QUARTER_NOTE
.byte E_3
.byte EIGHTH_TRIPLET
.byte E_3
.byte E_3
.byte $F0
.byte $F2
.byte DOTTED_QUARTER_NOTE
.byte F_3
.byte EIGHTH_TRIPLET
.byte F_3
.byte F_3
.byte DOTTED_QUARTER_NOTE
.byte F_3
.byte EIGHTH_TRIPLET
.byte F_3
.byte F_3
.byte $F0
.byte $F2
.byte DOTTED_QUARTER_NOTE
.byte E_3
.byte EIGHTH_TRIPLET
.byte E_3
.byte E_3
.byte DOTTED_QUARTER_NOTE
.byte E_3
.byte EIGHTH_TRIPLET
.byte E_3
.byte E_3
.byte $F0
.byte $F2
.byte DOTTED_QUARTER_NOTE
.byte F_3
.byte EIGHTH_TRIPLET
.byte F_3
.byte F_3
.byte DOTTED_QUARTER_NOTE
.byte F_3
.byte EIGHTH_TRIPLET
.byte F_3
.byte F_3
.byte $F0

song33voiceA:
.byte EIGHTH_NOTE
.byte Gb_4
.byte DOTTED_HALF_NOTE
.byte REST
.byte B_4
.byte DOTTED_QUARTER_NOTE
.byte Bb_4
.byte REST
.byte EIGHTH_NOTE
.byte F_4
.byte DOTTED_HALF_NOTE
.byte Db_4
.byte SONG_END

song32voiceD:
song33voiceD:
.byte $11
.byte $90
.byte $90
.byte SONG_END

song33voiceB:
.byte EIGHTH_NOTE
.byte Eb_5
.byte DOTTED_HALF_NOTE
.byte REST
.byte Gb_5
.byte DOTTED_QUARTER_NOTE
.byte F_5
.byte REST
.byte EIGHTH_NOTE
.byte Db_5
.byte DOTTED_HALF_NOTE
.byte Bb_4

song33voiceC:
.byte $F2
.byte DOTTED_QUARTER_NOTE
.byte B_3
.byte EIGHTH_TRIPLET
.byte B_3
.byte B_3
.byte DOTTED_QUARTER_NOTE
.byte B_3
.byte EIGHTH_TRIPLET
.byte B_3
.byte B_3
.byte $F0
.byte $F2
.byte DOTTED_QUARTER_NOTE
.byte Bb_3
.byte EIGHTH_TRIPLET
.byte Bb_3
.byte Bb_3
.byte DOTTED_QUARTER_NOTE
.byte Bb_3
.byte EIGHTH_TRIPLET
.byte Bb_3
.byte Bb_3
.byte $F0

song35voiceA:
song35voiceD:
.byte HALF_NOTE
.byte C_5
.byte SIXTEENTH_NOTE
.byte C_5
.byte C_5
.byte EIGHTH_NOTE
.byte C_5
.byte EIGHTH_TRIPLET
.byte Bb_4
.byte G_4
.byte D_5
.byte HALF_NOTE
.byte C_5
.byte SIXTEENTH_NOTE
.byte C_5
.byte C_5
.byte EIGHTH_NOTE
.byte C_5
.byte EIGHTH_TRIPLET
.byte Bb_4
.byte G_4
.byte D_5
.byte QUARTER_NOTE
.byte C_5
.byte SIXTEENTH_NOTE
.byte C_4
.byte C_4
.byte C_4
.byte C_4
.byte HALF_NOTE
.byte C_4
.byte SONG_END

song35voiceB:
.byte HALF_NOTE
.byte E_4
.byte SIXTEENTH_NOTE
.byte E_4
.byte E_4
.byte EIGHTH_NOTE
.byte E_4
.byte EIGHTH_TRIPLET
.byte D_4
.byte C_4
.byte F_4
.byte HALF_NOTE
.byte E_4
.byte SIXTEENTH_NOTE
.byte E_4
.byte E_4
.byte EIGHTH_NOTE
.byte E_4
.byte EIGHTH_TRIPLET
.byte D_4
.byte C_4
.byte F_4
.byte QUARTER_NOTE
.byte G_4
.byte SIXTEENTH_NOTE
.byte G_3
.byte G_3
.byte G_3
.byte G_3
.byte HALF_NOTE
.byte G_3

song35voiceC:
.byte EIGHTH_TRIPLET
.byte E_4
.byte C_4
.byte E_4
.byte G_4
.byte E_4
.byte G_4
.byte Bb_4
.byte G_4
.byte Bb_4
.byte D_5
.byte Bb_4
.byte D_5
.byte E_4
.byte C_4
.byte E_4
.byte G_4
.byte E_4
.byte G_4
.byte Bb_4
.byte G_4
.byte Bb_4
.byte D_5
.byte Bb_4
.byte D_5
.byte QUARTER_NOTE
.byte C_5
.byte SIXTEENTH_NOTE
.byte C_4
.byte C_4
.byte C_4
.byte C_4
.byte HALF_NOTE
.byte C_4
;9825
.proc process_audio
		LDA gamePaused
		BEQ lbl_9835
		LDA #$00		;Silence all channels
		STA APU_CHANCTRL
		LDA #$0F
		STA APU_CHANCTRL
		BNE lbl_9846
	lbl_9835:
		LDA #$FF
		STA $4017
		JSR process_music_effect
		JSR sub_99a0
		JSR sub_9b85
		JSR process_music
	lbl_9846:
		JSR process_sound_effect
		LDA #$00
		STA RgZeldaRam+$104
		STA RgZeldaRam+$103
		STA RgZeldaRam+$102
		STA RgZeldaRam+$101
		STA RgZeldaRam+$100
		RTS
.endproc
	
.byte $1C
.byte $4C
.byte $27
.byte $5C
.byte $46
.byte $67
.byte $07
.byte $95
.byte $50
.byte $08
.byte $08
.byte $08
.byte $08
.byte $08
.byte $90
.byte $08
.byte $08
.byte $08
.byte $08
.byte $08
.byte $08
.byte $08
.byte $08
.byte $08
.byte $08
.byte $08
.byte $08
.byte $00
.byte $82
.byte $4A
.byte $48
.byte $4A
.byte $08
.byte $08
.byte $08
.byte $08
.byte $08
.byte $08
.byte $00
.byte $9F
.byte $1E
.byte $22
.byte $24
.byte $26
.byte $9F
.byte $28
.byte $2A
.byte $2C
.byte $2E
.byte $9A
.byte $28
.byte $2A
.byte $2C
.byte $2E
.byte $9C
.byte $28
.byte $2A
.byte $2C
.byte $2E
.byte $96
.byte $28
.byte $2A
.byte $2C
.byte $2E
.byte $98
.byte $28
.byte $2A
.byte $2C
.byte $2E
.byte $00
.byte $99
.byte $42
.byte $4A
.byte $50
.byte $54
.byte $00
.byte $99
.byte $70
.byte $0A
.byte $70
.byte $0E
.byte $70
.byte $10
.byte $9F
.byte $70
.byte $2A
.byte $12
.byte $1E
.byte $2A
.byte $70
.byte $1E
.byte $00
.byte $9A
.byte $42
.byte $08
.byte $08
.byte $56
.byte $08
.byte $08
.byte $00
.byte $08
.byte $08
.byte $00
.byte $9F
.byte $40
.byte $30
.byte $40
.byte $3A
.byte $28
.byte $00
lbl_98c9:
	JMP sub_9d46
process_sound_effect:
	LDA soundEffectRequest
	BMI lbl_98c9
	BEQ lbl_98dc
	CMP #$40
	BNE lbl_98e2
	LDX RgZeldaRam+$105
	BEQ lbl_98e2
lbl_98dc:
	LDA RgZeldaRam+$105
	BNE lbl_98f1
	RTS
lbl_98e2:
	STA RgZeldaRam+$105
	LDY #$00
lbl_98e7:
	INY
	LSR
	BCC lbl_98e7
	LDA $aafa,Y
	STA RgZeldaRam+$10e
lbl_98f1:
	LDY RgZeldaRam+$10e
	INC RgZeldaRam+$10e
	LDA $aafb,Y
	BMI lbl_9911
	BNE lbl_991d
	LDX #$90
	STX APU_PULSE1CTRL
	LDX #$18
	STX $4003
	LDX #$00
	STX APU_PULSE1FTUNE
	STX RgZeldaRam+$105
	RTS
lbl_9911:
	STA APU_PULSE1CTRL
	LDY RgZeldaRam+$10e
	INC RgZeldaRam+$10e
	LDA $aafb,Y
lbl_991d:
	JSR sub_9c0d
	LDA #$7F
	STA APU_PULSE1RAMP
	RTS
lbl_9926:
	LDA #$0F
	STA APU_CHANCTRL
	LDA #$00
	STA RgZeldaRam+$108
	STA currentMusicEffect
	STA RgZeldaRam+$11a
	STA RgZeldaRam+$f6
	RTS
lbl_993a:
	STY RgZeldaRam+$106
	LDA #$05
	STA $69
	LDA RgZeldaRam+$104
	AND #$EF
	BNE lbl_994b
	STA RgZeldaRam+$104
lbl_994b:
	LDY $69
	LDA $b25b,Y
	BNE lbl_996e
lbl_9952:
	STY RgZeldaRam+$106
	LDA #$38
	STA $69
lbl_9959:
	LDA #$0D
	STA $68
lbl_995d:
	DEC $68
	LDY $68
	BEQ lbl_9959
	CPY #$07
	BCC lbl_996b
	LDA #$10
	BNE lbl_997b
lbl_996b:
	LDA $b198,Y
lbl_996e:
	TAX
	AND #$0F
	STA APU_NOISEFREQ1
	TXA
	LSR
	LSR
	LSR
	LSR
	ORA #$10
lbl_997b:
	STA APU_NOISECTRL
	LDA #$08
	STA APU_NOISEFREQ2
	DEC $69
lbl_9985:
	BNE lbl_9991
	LDA #$F0
	STA APU_NOISECTRL
	LDA #$00
	STA RgZeldaRam+$106
lbl_9991:
	RTS
lbl_9992:
	STY RgZeldaRam+$106
	LDA #$0A
	STA $69
lbl_9999:
	LDY $69
	LDA $b251,Y
	BNE lbl_996e
sub_99a0:
	LDY RgZeldaRam+$103
	BMI lbl_9926
	LDA RgZeldaRam+$106
	LSR RgZeldaRam+$103
	BCS lbl_9992
	LSR
	BCS lbl_9999
	LSR RgZeldaRam+$103
	BCS lbl_993a
	LSR
	BCS lbl_994b
	LSR RgZeldaRam+$103
	BCS lbl_99e7
	LSR
	BCS lbl_99ee
	LSR RgZeldaRam+$103
	BCS lbl_9952
	LSR
	BCS lbl_995d
	LSR RgZeldaRam+$103
	BCS lbl_99d9
	LSR
	BCS lbl_99e0
	LSR
	BCS lbl_9a09
	LSR RgZeldaRam+$103
	BCS lbl_99fd
	RTS
lbl_99d9:
	STY RgZeldaRam+$106
	LDA #$18
	STA $69
lbl_99e0:
	LDY $69
	LDA $acdc,Y
	BNE lbl_996e
lbl_99e7:
	STY RgZeldaRam+$106
	LDA #$20
	STA $69
lbl_99ee:
	LDA $69
	LSR
	TAY
	LDX #$0E
	STX APU_NOISEFREQ1
	LDA $b260,Y
	JMP lbl_997b
lbl_99fd:
	STY RgZeldaRam+$106
	LDA #$D0
	STA RgZeldaRam+$f3
	LDA #$10
	STA $68
lbl_9a09:
	LDA RgZeldaRam+$f3
	CMP #$BF
	BCC lbl_9a14
	INC $68
	BNE lbl_9a28
lbl_9a14:
	LDA RgZeldaRam+$f3
	LSR
	BCC lbl_9a28
	LSR
	BCC lbl_9a28
	LSR
	BCC lbl_9a28
	LDA $68
	CMP #$10
	BEQ lbl_9a28
	DEC $68
lbl_9a28:
	LDA $68
	STA APU_NOISECTRL
	LDX #$03
	STX APU_NOISEFREQ1
	LDA #$08
	STA APU_NOISEFREQ2
	DEC RgZeldaRam+$f3
	JMP lbl_9985
.byte $1F
.byte $2F
.byte $2E
.byte $3F
.byte $3F
.byte $4C
.byte $4E
.byte $5F
.byte $6F
.byte $6F
.byte $7E
.byte $8F
.byte $9E
.byte $AF
.byte $BE
.byte $CF
.byte $DE
.byte $EF
.byte $FE
.byte $FD
.byte $FE
.byte $FF
.byte $FF
.byte $FE
.byte $0C
.byte $08
.byte $11
.byte $1C
.byte $28
.byte $33
.byte $40
.byte $62
.byte $8A
.byte $4E
.byte $58
.byte $60
.byte $8A
.byte $5E
.byte $94
.byte $60
.byte $00
.byte $8A
.byte $42
.byte $06
.byte $3C
.byte $30
.byte $2E
.byte $3E
.byte $44
.byte $CC
.byte $02
.byte $00
.byte $83
.byte $40
.byte $42
.byte $48
.byte $4A
.byte $02
.byte $50
.byte $4C
.byte $54
.byte $94
.byte $56
.byte $00
.byte $94
.byte $3A
.byte $3E
.byte $A8
.byte $50
.byte $8A
.byte $4E
.byte $02
.byte $CC
.byte $4A
.byte $00
.byte $81
.byte $28
.byte $3E
.byte $24
.byte $82
.byte $3A
.byte $81
.byte $16
.byte $30
.byte $1A
.byte $82
.byte $34
.byte $00
.byte $94
.byte $56
.byte $42
.byte $02
.byte $4C
.byte $52
.byte $42
.byte $5C
.byte $4A
.byte $5A
.byte $02
.byte $4C
.byte $5A
.byte $56
.byte $02
.byte $50
.byte $4C
.byte $5A
.byte $02
.byte $54
.byte $5A
.byte $58
.byte $02
.byte $50
.byte $54
.byte $4C
.byte $42
.byte $02
.byte $4C
.byte $50
.byte $48
.byte $4A
.byte $50
.byte $00
.byte $8A
.byte $08
.byte $08
.byte $08
.byte $85
.byte $3C
.byte $3A
.byte $38
.byte $36
.byte $3A
.byte $38
.byte $36
.byte $34
.byte $38
.byte $36
.byte $34
.byte $32
.byte $36
.byte $34
.byte $32
.byte $30
.byte $34
.byte $32
.byte $30
.byte $2E
.byte $2A
.byte $28
.byte $A8
.byte $26
.byte $00
process_music_effect:
	LDA musicEffectRequest
	BMI lbl_9ae2
	BNE lbl_9ae7
	LDA currentMusicEffect
	BNE lbl_9afa
	RTS
lbl_9ae2:
	JSR sub_9d46
	LDA #$80
lbl_9ae7:
	STA currentMusicEffect
	LDY #$00
lbl_9aec:
	INY
	LSR
	BCC lbl_9aec
	LDA $acf4,Y
	STA RgZeldaRam+$118
	LDA #$01
	STA $6F
lbl_9afa:
	DEC $6F
	BNE lbl_9b47
	LDY RgZeldaRam+$118
	INC RgZeldaRam+$118
	LDA $acf5,Y
	BMI lbl_9b25
	BNE lbl_9b32
	LDA currentMusicEffect
	CMP #$40
	BEQ lbl_9ae7
	LDX #$90
	STX APU_PULSE2CTRL
	LDX #$18
	STX APU_PULSE2STUNE
	LDX #$00
	STX currentMusicEffect
	STX APU_PULSE2FTUNE
	RTS
lbl_9b25:
	AND #$7F
	STA $6E
	LDY RgZeldaRam+$118
	INC RgZeldaRam+$118
	LDA $acf5,Y
lbl_9b32:
	JSR sub_9c2b
	LDA #$7F
	STA APU_PULSE2RAMP
	LDA #$86
	STA APU_PULSE2CTRL
	LDA $6E
	STA $6F
	LDA #$1F
	STA $6D
lbl_9b47:
	LDA currentMusicEffect
	AND #$90
	BEQ lbl_9b64
	LDY $6D
	BEQ lbl_9b54
	DEC $6D
lbl_9b54:
	LDA $ae05,Y
	STA APU_PULSE2CTRL
	LDA $6F
	LDX $6B
	JSR sub_9c54
	STX APU_PULSE2FTUNE
lbl_9b64:
	RTS
.byte $95
.byte $96
.byte $97
.byte $98
.byte $99
.byte $9A
.byte $9B
.byte $9C
.byte $9D
.byte $9E
.byte $9F
.byte $9F
.byte $9F
.byte $9F
.byte $9F
.byte $9F
.byte $9F
.byte $9F
.byte $9F
.byte $9F
.byte $9F
.byte $9F
.byte $9F
.byte $9E
.byte $9D
.byte $9C
.byte $9B
.byte $9A
.byte $99
.byte $98
.byte $97
.byte $96

.proc sub_9b85
        RTS ; DPCM samples need a reserved fixed sample bank
        .byte $00,$00
		BMI lbl_9bb3
		BNE lbl_9baf
		LDA RgZeldaRam+$108
		BEQ lbl_9ba9
		DEC RgZeldaRam+$f2
		BNE return
		LDA RgZeldaRam+$108
		BMI lbl_9bb3
		AND #$70
		BNE lbl_9baf
		LDA #$00
		STA RgZeldaRam+$108
		LDA #$0F
		STA APU_CHANCTRL
	lbl_9ba9:
		LDA RgZeldaRam+$f6
		BNE lbl_9bb7
	return:
		RTS
	lbl_9baf:
		LDX #$00
		BEQ lbl_9bb7
	lbl_9bb3:
		LDX #$7F
		AND #$F0
	lbl_9bb7:
		STX APU_MODDA
		STA RgZeldaRam+$108
		TAX
		AND #$F0
		BEQ lbl_9bc5
		STA RgZeldaRam+$f6
	lbl_9bc5:
		TXA
		LDY #$00
	lbl_9bc8:
		INY
		LSR
		BCC lbl_9bc8
		LDA $ae9b,Y
		STA APU_MODCTRL
		LDA $ae8d,Y
		STA APU_MODADDR
		LDA $ae94,Y
		STA APU_MODLEN
		LDA #$A0
		STA RgZeldaRam+$f2
		LDA #$0F
		STA APU_CHANCTRL
		LDA #$1F
		STA APU_CHANCTRL
		RTS
.endproc

.byte $00
.byte $4C
.byte $80
.byte $1D
.byte $20
.byte $28
.byte $4C
.byte $75
.byte $C0
.byte $40
.byte $0A
.byte $B0
.byte $90
.byte $D0
.byte $0F
.byte $0F
.byte $0D
.byte $0F
.byte $0E
.byte $0F
.byte $0E

.proc sub_9c03
		STY APU_PULSE1RAMP
		STX APU_PULSE1CTRL
		RTS
.endproc

.byte $20
.byte $03
.byte $9C
sub_9c0d:
	TAY
	LDA $b1a1,Y
	BEQ lbl_9c20
	STA $6A
	STA APU_PULSE1FTUNE
	LDA noteTable,Y
	ORA #$08
	STA $4003
lbl_9c20:
	RTS
	
.proc sub_9c21
		STX APU_PULSE2CTRL
		STY APU_PULSE2RAMP
		RTS
.endproc

.byte $20
.byte $21
.byte $9C

.proc sub_9c2b
		TAY
		LDA $b1a1,Y
		BEQ lbl_9c20
		STA $6B
		STA APU_PULSE2FTUNE
		LDA noteTable,Y
		ORA #$08
		STA APU_PULSE2STUNE
		RTS
.endproc

.proc sub_9c3f
		TAY
		LDA $b1a1,Y
		BEQ lbl_9c20
		STA RgZeldaRam+$f0
		STA APU_TRIFREQ1
		LDA noteTable,Y
		ORA #$08
		STA APU_TRIFREQ2
		RTS
.endproc

.proc sub_9c54
		CMP #$10
		BCC return
		LSR
		LSR
		LSR
		BCS lbl_9c62
		TXA
		ADC #$01
		BNE lbl_9c66
	lbl_9c62:
		TXA
		CLC
		ADC #$FF
	lbl_9c66:
		TAX
	return:
		RTS
.endproc	

lbl_9c68:
	JMP lbl_9d2c
;9C6B
.proc process_music
		LDA musicRequest	;Check if a song is requested
		BNE start_song		;If so, start it.
		LDA currentMusic
		BNE lbl_9c68
		RTS
.endproc
	
start_song:
	STA currentMusic
	BMI lbl_9c93
	CMP #6
	BNE lbl_9c83
	LDY #$24
	BNE lbl_9ce5
lbl_9c83:
	CMP #$01
	BEQ lbl_9c9b
	CMP #$40
	BEQ lbl_9c97
	CMP #$10
	BNE lbl_9c9f
	LDY #$11
	BNE lbl_9c9d
	
lbl_9c93:
	LDY #$19
	BNE lbl_9c9d
lbl_9c97:
	LDY #$0F
	BNE lbl_9c9d
lbl_9c9b:
	LDY #$08
lbl_9c9d:
	STY $6C
lbl_9c9f:	;
	TAX
	BMI lbl_9cd2
	CMP #$01
	BEQ lbl_9cc6
	CMP #$40
	BEQ lbl_9cba
	CMP #$10
	BNE lbl_9cde
	INC $6C
	LDY $6C
	CPY #$1A
	BNE lbl_9ce5
	LDY #$14
	BNE lbl_9c9d
lbl_9cba:
	INC $6C
	LDY $6C
	CPY #$12
	BNE lbl_9ce5
	LDY #$0F
	BNE lbl_9c9d
lbl_9cc6:
	INC $6C
	LDY $6C
	CPY #$10
	BNE lbl_9ce5
	LDY #$09
	BNE lbl_9c9d
lbl_9cd2:
	INC $6C
	LDY $6C
	CPY #$24
	BNE lbl_9ce5
	LDY #$19
	BNE lbl_9c9d
lbl_9cde:
	TXA
	LDY #$00
lbl_9ce1:
	INY
	LSR
	BCC lbl_9ce1
lbl_9ce5:	;Y = song id
	LDA songTable - 1, Y
	TAY													;Y = offset of song descriptor
	LDA songTable + SongDescriptor::unk1, Y				;Note delay?
	STA RgZeldaRam+$f4
	LDA songTable + SongDescriptor::musicDataPtr, Y		;Get address of music data
	STA musicData	;low byte
	LDA songTable + SongDescriptor::musicDataPtr+1, Y
	STA musicData+1	;high byte
	LDA songTable + SongDescriptor::offsetVoiceC, Y		;Get offset of music data for voice C
	STA musicOffsetVoiceC
	LDA songTable + SongDescriptor::offsetVoiceB, Y		;Get offset of music data for voice B
	STA musicOffsetVoiceB
	LDA songTable + SongDescriptor::offsetVoiceD, Y		;Get offset of music data for voice D
	STA musicOffsetVoiceD
	STA RgZeldaRam+$f5
	LDA songTable+6,Y
	STA RgZeldaRam+$119
	LDA songTable+7,Y
	STA RgZeldaRam+$f1
	LDA #1
	STA musicTimer
	STA RgZeldaRam+$113
	STA RgZeldaRam+$116
	STA RgZeldaRam+$117
	LSR
	STA musicOffsetVoiceA
lbl_9d2c:	;Continue playing song?
	DEC musicTimer
	BNE lbl_9d83
	LDY musicOffsetVoiceA
	INC musicOffsetVoiceA
	LDA (musicData),Y		;Get next byte of song
	BEQ end_of_song			;0 marks end of song
	BPL set_note			;Upper bit clear is a note
	BNE set_duration		;Upper bit set is a duration
end_of_song:
	LDA currentMusic
	AND #$F1
	BNE lbl_9d54
sub_9d46:
	LDA #$00
	STA currentMusic
	STA APU_CHANCTRL
	LDA #$0F
	STA APU_CHANCTRL
	RTS
lbl_9d54:
	JMP lbl_9c9f
set_duration:
	JSR sub_9ee6
	STA noteDuration
	LDY musicOffsetVoiceA
	INC musicOffsetVoiceA
	LDA (musicData),Y				;Get next byte of song and set that note.
set_note:
	LDX currentMusicEffect
	BNE lbl_9d7d
	JSR sub_9c2b
	BEQ lbl_9d72
	JSR sub_9f72
lbl_9d72:
	STA RgZeldaRam+$112
	JSR sub_9c21
	LDA #$00
	STA RgZeldaRam+$11b
lbl_9d7d:
	LDA noteDuration
	STA musicTimer
lbl_9d83:
	LDY currentMusicEffect
	BNE lbl_9dae
	INC RgZeldaRam+$11b
	LDY RgZeldaRam+$112
	BEQ lbl_9d93
	DEC RgZeldaRam+$112
lbl_9d93:
	JSR sub_9f7c
	STA APU_PULSE2CTRL
	LDX #$7F
	STX APU_PULSE2RAMP
	LDA currentMusic
	BPL lbl_9dae
	LDA RgZeldaRam+$11b
	LDX $6B
	JSR sub_9c54
	STX APU_PULSE2FTUNE
lbl_9dae:
	LDY musicOffsetVoiceB
	BEQ lbl_9e19
	DEC RgZeldaRam+$113
	BNE lbl_9dee
	LDY musicOffsetVoiceB
	INC musicOffsetVoiceB
	LDA (musicData),Y
	BPL lbl_9dd0
	JSR sub_9ee6
	STA RgZeldaRam+$10f
	LDY musicOffsetVoiceB
	INC musicOffsetVoiceB
	LDA (musicData),Y
lbl_9dd0:
	LDX RgZeldaRam+$105
	BNE lbl_9de8
	JSR sub_9c0d
	BEQ lbl_9ddd
	JSR sub_9f72
lbl_9ddd:
	STA RgZeldaRam+$114
	JSR sub_9c03
	LDA #$00
	STA RgZeldaRam+$11c
lbl_9de8:
	LDA RgZeldaRam+$10f
	STA RgZeldaRam+$113
lbl_9dee:
	LDX currentSoundEffect
	BNE lbl_9e19
	INC RgZeldaRam+$11c
	LDY RgZeldaRam+$114
	BEQ lbl_9dfe
	DEC RgZeldaRam+$114
lbl_9dfe:
	JSR sub_9f7c
	STA APU_PULSE1CTRL
	LDA currentMusic
	BPL lbl_9e14
	LDA RgZeldaRam+$11c
	LDX $6A
	JSR sub_9c54
	STX APU_PULSE1FTUNE
lbl_9e14:
	LDA #$7F
	STA APU_PULSE1RAMP
lbl_9e19:
	LDA musicOffsetVoiceC
	BNE lbl_9e21
	JMP lbl_9e95
lbl_9e21:
	DEC RgZeldaRam+$116
	BNE lbl_9e78
lbl_9e26:
	LDY musicOffsetVoiceC
	INC musicOffsetVoiceC
	LDA (musicData),Y
	BEQ lbl_9e92
	BPL lbl_9e6a
	CMP #$F0
	BEQ lbl_9e47
	BCC lbl_9e55
	SEC
	SBC #$F0
	STA RgZeldaRam+$11e
	LDA musicOffsetVoiceC
	STA RgZeldaRam+$11f
	JMP lbl_9e26
lbl_9e47:
	DEC RgZeldaRam+$11e
	BEQ lbl_9e52
	LDA RgZeldaRam+$11f
	STA musicOffsetVoiceC
lbl_9e52:
	JMP lbl_9e26
lbl_9e55:
	JSR sub_9ee6
	STA RgZeldaRam+$115
	LDA #$1F
	STA APU_TRICTRL1
	LDY musicOffsetVoiceC
	INC musicOffsetVoiceC
	LDA (musicData),Y
	BEQ lbl_9e92
lbl_9e6a:
	JSR sub_9c3f
	LDA #$00
	STA RgZeldaRam+$11d
	LDX RgZeldaRam+$115
	STX RgZeldaRam+$116
lbl_9e78:
	INC RgZeldaRam+$11d
	LDA RgZeldaRam+$11d
	LDX RgZeldaRam+$f0
	JSR sub_9c54
	STX APU_TRIFREQ1
	LDA RgZeldaRam+$f1
	BPL lbl_9e90
	LDA #$1F
	BNE lbl_9e92
lbl_9e90:
	LDA #$FF
lbl_9e92:
	STA APU_TRICTRL1
lbl_9e95:
	LDA currentMusic
	AND #$91
	BEQ lbl_9ed3
	DEC RgZeldaRam+$117
	BNE lbl_9ed3
lbl_9ea1:
	LDY musicOffsetVoiceD
	INC musicOffsetVoiceD
	LDA (musicData),Y
	BNE lbl_9eb3
	LDA RgZeldaRam+$f5
	STA musicOffsetVoiceD
	BNE lbl_9ea1
lbl_9eb3:
	JSR sub_9ee0
	STA RgZeldaRam+$117
	TXA
	AND #$3E
	LSR
	LSR
	LSR
	LSR
	TAY
	LDA $b174,Y
	STA APU_NOISECTRL
	LDA $b178,Y
	STA APU_NOISEFREQ1
	LDA $b17c,Y
	STA APU_NOISEFREQ2
lbl_9ed3:
	RTS
.byte $10
.byte $1C
.byte $1C
.byte $1C
.byte $00
.byte $03
.byte $0A
.byte $03
.byte $00
.byte $18
.byte $18
.byte $58

sub_9ee0:
	TAX
	ROR
	TXA
	ROL
	ROL
	ROL
sub_9ee6:
	AND #$07
	CLC
	ADC RgZeldaRam+$f4
	TAY
	LDA $b271,Y
	RTS
	
.byte $29
.byte $07
.byte $A8
.byte $B9
.byte $D1
.byte $9F
.byte $60
.byte $CB
.byte $0E
.byte $0E
.byte $4C
.byte $6D
.byte $8C
.byte $CD
.byte $FF

;9F00
; Note frequency table
noteTable:
	.byte $00,$23	;G7
	.byte $00,$6A	;C6
	.byte $03,$27
	.byte $00,$97
	.byte $00,$00
	.byte $02,$F9
	.byte $02,$CF
	.byte $02,$A6
	.byte $02,$80
	.byte $02,$5C
	.byte $02,$3A
	.byte $02,$1A
	.byte $01,$FC
	.byte $01,$DF
	.byte $01,$C4
	.byte $01,$AB
	.byte $01,$93
	.byte $01,$7C
	.byte $01,$67
	.byte $01,$53
	.byte $01,$40
	.byte $01,$2E
	.byte $01,$1D
	.byte $01,$0D
	.byte $00,$FE
	.byte $00,$EF
	.byte $00,$E2
	.byte $00,$D5
	.byte $00,$C9
	.byte $00,$BE
	.byte $00,$B3
	.byte $00,$A9
	.byte $00,$A0
	.byte $00,$8E
	.byte $00,$86
	.byte $00,$77
	.byte $00,$7E
	.byte $00,$71
	.byte $00,$54
	.byte $00,$64
	.byte $00,$5F
	.byte $00,$59
	.byte $00,$50
	.byte $00,$47
	.byte $00,$43
	.byte $00,$3F
	.byte $00,$38
	.byte $00,$32
	.byte $00,$21
	.byte $05,$4D
	.byte $05,$01
	.byte $04,$B9
	.byte $04,$35
	.byte $03,$F8
	.byte $03,$BF
	.byte $03,$89
	.byte $03,$57

sub_9f72:
	LDA RgZeldaRam+$119
	LDA #$20
	LDX #$82
	LDY #$7F
	RTS
	
sub_9f7c:
	LDA RgZeldaRam+$119
	BPL lbl_9f88
	LDA $b232,Y
	AND #$0F
	BNE lbl_9f8f
lbl_9f88:
	LDA $b232,Y
	LSR
	LSR
	LSR
	LSR
lbl_9f8f:
	ORA #$90
	RTS
.byte $04
.byte $24
.byte $24
.byte $34
.byte $34
.byte $35
.byte $35
.byte $35
.byte $45
.byte $45
.byte $46
.byte $46
.byte $46
.byte $46
.byte $46
.byte $46
.byte $46
.byte $46
.byte $57
.byte $57
.byte $57
.byte $57
.byte $68
.byte $68
.byte $68
.byte $68
.byte $79
.byte $79
.byte $79
.byte $68
.byte $68
.byte $57
.byte $47
.byte $67
.byte $87
.byte $A8
.byte $B9
.byte $9A
.byte $8A
.byte $5A
.byte $9B
.byte $8B
.byte $FB
.byte $F9
.byte $9D
.byte $6E
.byte $3F
.byte $1A
.byte $1A
.byte $1C
.byte $1D
.byte $1D
.byte $1E
.byte $1E
.byte $1F
.byte $1F
.byte $1E
.byte $1A
.byte $19
.byte $16
.byte $13
.byte $11
.byte $11
.byte $03
.byte $0A
.byte $01
.byte $14
.byte $05
.byte $28
.byte $3C
.byte $70
.byte $07
.byte $1B
.byte $35
.byte $14
.byte $0D
.byte $28
.byte $3C
.byte $50
.byte $06
.byte $0C
.byte $08
.byte $18
.byte $24
.byte $30
.byte $48
.byte $10
.byte $07
.byte $0D
.byte $09
.byte $1B
.byte $24
.byte $36
.byte $48
.byte $10
.byte $3C
.byte $50
.byte $0A
.byte $05
.byte $14
.byte $0D
.byte $28
.byte $0E

.endscope
