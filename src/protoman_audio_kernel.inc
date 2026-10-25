; Imported from https://github.com/lsmmega/mm3 at 8ecd0a9247ed17709e8cd9cc692c38288daa2bc5.
; Original Capcom sound engine and music; adapted by tools/reference/import_megaman_audio.py.
.pushseg
.segment "PROTO_MM3_AUDIO"
.scope ProtoMm3
;base pm3_note index set
.ENUM
	_E_1 ;non-standard pm3_note
	_Gb1 ;non-standard pm3_note
	_A_1 ;non-standard pm3_note
	_Db2 ;non-standard pm3_note
	_E_2 ;non-standard pm3_note
	_A_2 ;non-standard pm3_note
	_D_3 ;non-standard pm3_note
	_Bb3 ;non-standard pm3_note
	_C_5 ;non-standard pm3_note
	A_0
	Bb0
	B_0
	C_1
	Db1
	D_1
	Eb1
	E_1
	F_1
	Gb1
	G_1
	Ab1
	A_1
	Bb1
	B_1
	C_2
	Db2
	D_2
	Eb2
	E_2
	F_2
	Gb2
	G_2
	Ab2
	A_2
	Bb2
	B_2
	C_3
	Db3
	D_3
	Eb3
	E_3
	F_3
	Gb3
	G_3
	Ab3
	A_3
	Bb3
	B_3
	C_4
	Db4
	D_4
	Eb4
	E_4
	F_4
	Gb4
	G_4
	Ab4
	A_4
	Bb4
	B_4
	C_5
	Db5
	D_5
	Eb5
	E_5
	F_5
	Gb5
	G_5
	Ab5
	A_5
	Bb5
	B_5
	C_6
	Db6
	D_6
	Eb6
	E_6
	F_6
	Gb6
	G_6
	Ab6
	A_6
	Bb6
	B_6
	C_7
	Db7
	D_7
	Eb7
	E_7
	F_7
	Gb7
	G_7
	Ab7
	A_7
	Bb7
	B_7
.ENDENUM

;channel flags
	no_channel_flags_set     = 0
	channel_octave_jump_set  = 1 << 3
	channel_triplet_note_set = 1 << 5
	channel_connect_note_set = 1 << 6

;sfx global channel flags
	sfx_loop_set             = 1 << 0
	sfx_ads_set              = 1 << 1
	sfx_global_transpose_set = 1 << 2

;sfx channel flags
	sfx_pulse_1  = 1 << 0
	sfx_pulse_2  = 1 << 1
	sfx_triangle = 1 << 2
	sfx_noise    = 1 << 3

;sfx channel set flags
	sfx_instruments_set          = 1 << 0
	sfx_duty_cycle_set           = 1 << 1
	sfx_volume_set               = 1 << 2
	sfx_triangle_note_length_set = 1 << 2
	sfx_pitch_slide_set          = 1 << 3
	sfx_pitch_tune_set           = 1 << 4

.ENUM
	PPU_CTRL = $2000
	PPU_MASK
	PPU_STATUS
	PPU_OAM_ADDR
	PPU_OAM_DATA
	PPU_SCROLL
	PPU_ADDRESS
	PPU_DATA
.ENDENUM

;ppu ctrl
	background_table_left  = 0
	draw_horizontal        = 0
	nametable_top_left     = 0
	nametable_top_right    = 1
	nametable_bottom_left  = 2
	nametable_bottom_right = 3
	all_nametable          = 3
	draw_vertical          = 1 << 2
	sprite_table_right     = 1 << 3
	background_table_right = 1 << 4
	nmi_enable             = 1 << 7

;ppu mask
	background_leftmost_enable = 1 << 1
	sprites_leftmost_enable    = 1 << 2
	background_enable          = 1 << 3
	sprite_enable              = 1 << 4

	SQ1_VOL           = $4000
	SQ1_SWEEP         = $4001
	SQ1_LO            = $4002
	SQ1_HI            = $4003
	SQ2_VOL           = $4004
	SQ2_SWEEP         = $4005
	SQ2_LO            = $4006
	SQ2_HI            = $4007
	TRI_LINEAR        = $4008
	TRI_LO            = $400A
	TRI_HI            = $400B
	NOISE_VOL         = $400C
	NOISE_LO          = $400E
	NOISE_HI          = $400F
	DMC_FREQ          = $4010
	OAM_DMA           = $4014
	APU_STATUS        = $4015
	JOY1              = $4016
	JOY2_FRAME        = $4017 ;read
	APU_FRAME_COUNTER = $4017 ;write

zplayback_flag = $c0
zaudio_C1 = $c1
zaudio_C2 = $c2
zaudio_C3 = $c3
zaudio_C4 = $c4
zinstrument_lo = $c5
zinstrument_hi = $c6
zdec_note_length = $c7
zdec_note_length_rate = $c8
ztempo_hi = $c9
ztempo_lo = $ca
zglobal_transpose = $cb
zfade_direction = $cc
zfade_level = $cd
zsfx_priority = $ce
zsfx_channel = $cf
zsfx_lo = $d0
zsfx_hi = $d1
zsfx_global_transpose = $d2
zsfx_frames = $d3
zsfx_ads = $d4
zsfx_ads_remain = $d5
zsfx_loop = $d6
zsfx_repeat = $d7
zsfx_pitch_tune = $d8
zmusic_queue = $d9
zsfx_queue_index = $da
zsfx_queue_index_undo = $db
zsfx_queue = $dc
achannel_instrument = Mm3AudioRam + $00
astats_adsr_state = Mm3AudioRam + $04
ainvert_vibrato = Mm3AudioRam + $08
achannel_volume_duty_cycle = Mm3AudioRam + $0c
aadsr_volume = Mm3AudioRam + $10
achannel_pitch_tune = Mm3AudioRam + $14
achannel_pitch_slide = Mm3AudioRam + $18
anote = Mm3AudioRam + $1c
afreq_lo = Mm3AudioRam + $20
afreq_hi = Mm3AudioRam + $24
amusic_lo = Mm3AudioRam + $28
amusic_hi = Mm3AudioRam + $2c
anote_flags = Mm3AudioRam + $30
achannel_transpose = Mm3AudioRam + $34
anote_length_remain = Mm3AudioRam + $38
anote_ads = Mm3AudioRam + $3c
anote_ads_remain = Mm3AudioRam + $40
achannel_loop_counter = Mm3AudioRam + $44
achannel_handle = Mm3AudioRam + $7c
.MACRO pm3_instrument_set b, c, d, e, f, g, h, i
	.BYTE b, c, (d + $0F) << 4, e, f, g, h, i << 7
.ENDMACRO

.MACRO pm3_music_header
	.BYTE $00
.ENDMACRO

.MACRO pm3_triplet_note_set
	.BYTE $00
.ENDMACRO

.MACRO pm3_connect_note_set
	.BYTE $01
.ENDMACRO

.MACRO pm3_dotted_note_set
	.BYTE $02
.ENDMACRO

.MACRO pm3_octave_jump
	.IF current_octave_jump
		current_octave_jump .SET 0
	.ELSE
		current_octave_jump .SET 1
	.ENDIF
	.BYTE $03
.ENDMACRO

.MACRO pm3_channel_flags b
	.IF b & channel_octave_jump_set
		current_octave_jump .SET 1
	.ELSE
		current_octave_jump .SET 0
	.ENDIF
	.BYTE $04, b
.ENDMACRO

.MACRO pm3_tempo b, c
	.BYTE $05, b, c
.ENDMACRO

.MACRO pm3_note_ads b
	.BYTE $06, b
.ENDMACRO

.MACRO pm3_volume b
	.IF b >= 0 && b < 16
		.BYTE $07, b
	.ELSE
		.ERROR "Invaild pm3_volume."
	.ENDIF
.ENDMACRO

.MACRO pm3_instrument b
	.BYTE $08, b
.ENDMACRO

.MACRO pm3_octave b
	current_octave .SET b
	.BYTE $09, b
.ENDMACRO

.MACRO pm3_global_transpose b
	current_global_transpose .SET b
	.BYTE $0A, b
.ENDMACRO

.MACRO pm3_channel_transpose b
	current_channel_transpose .SET b
	.BYTE $0B, b
.ENDMACRO

.MACRO pm3_pitch_tune b
	.BYTE $0C, b
.ENDMACRO

.MACRO pm3_pitch_slide b
	.BYTE $0D, b
.ENDMACRO

.MACRO pm3_loop_1 b, c
	.IF b
		.BYTE $0E, b
		.DBYT c
	.ELSE
		.ERROR "pm3_loop_1 cannot be 0, Please use pm3_music_jump."
	.ENDIF
.ENDMACRO

.MACRO pm3_loop_2 b, c
	.IF b
		.BYTE $0F, b
		.DBYT c
	.ELSE
		.ERROR "pm3_loop_2 cannot be 0, Please use pm3_music_jump."
	.ENDIF
.ENDMACRO

.MACRO pm3_loop_3 b, c
	.IF b
		.BYTE $10, b
		.DBYT c
	.ELSE
		.ERROR "pm3_loop_3 cannot be 0, Please use pm3_music_jump."
	.ENDIF
.ENDMACRO

.MACRO pm3_loop_4 b, c
	.IF b
		.BYTE $11, b
		.DBYT c
	.ELSE
		.ERROR "pm3_loop_4 cannot be 0, Please use pm3_music_jump."
	.ENDIF
.ENDMACRO

.MACRO pm3_break_1 b, c
	.BYTE $12, b
	.DBYT c
.ENDMACRO

.MACRO pm3_break_2 b, c
	.BYTE $13, b
	.DBYT c
.ENDMACRO

.MACRO pm3_break_3 b, c
	.BYTE $14, b
	.DBYT c
.ENDMACRO

.MACRO pm3_break_4 b, c
	.BYTE $15, b
	.DBYT c
.ENDMACRO

.MACRO pm3_music_jump b
	.BYTE $16
	.DBYT b
.ENDMACRO

.MACRO pm3_music_end
	.BYTE $17
.ENDMACRO

.MACRO pm3_duty_cycle b
	.BYTE $18, b << 6
.ENDMACRO

.MACRO pm3_note b, c
	@d .SET b - current_octave_jump * $18 - current_octave * $0C - current_global_transpose - current_channel_transpose + 1
		.IF @d > 0 && @d < $20
			.IF c = 1
				.BYTE @d | $20
			.ELSEIF c = 2
				.BYTE @d | $40
			.ELSEIF c = 4
				.BYTE @d | $60
			.ELSEIF c = 8
				.BYTE @d | $80
			.ELSEIF c = 16
				.BYTE @d | $A0
			.ELSEIF c = 32
				.BYTE @d | $C0
			.ELSEIF c = 64
				.BYTE @d | $E0
			.ELSE
				.ERROR "Invaild pm3_note length."
			.ENDIF
		.ELSE
			.ERROR "Note is out of bound."
		.ENDIF
.ENDMACRO

.MACRO pm3_rest b
	.IF b = 1
		.BYTE $20
	.ELSEIF b = 2
		.BYTE $40
	.ELSEIF b = 4
		.BYTE $60
	.ELSEIF b = 8
		.BYTE $80
	.ELSEIF b = 16
		.BYTE $A0
	.ELSEIF b = 32
		.BYTE $C0
	.ELSEIF b = 64
		.BYTE $E0
	.ELSE
		.ERROR "Invaild pm3_note length."
	.ENDIF
.ENDMACRO

.MACRO pm3_noise_note b, c
	.IF b >= 0 && b < $10
		.IF c = 1
			.BYTE b + 1 | $20
		.ELSEIF c = 2
			.BYTE b + 1 | $40
		.ELSEIF c = 4
			.BYTE b + 1 | $60
		.ELSEIF c = 8
			.BYTE b + 1 | $80
		.ELSEIF c = 16
			.BYTE b + 1 | $A0
		.ELSEIF c = 32
			.BYTE b + 1 | $C0
		.ELSEIF c = 64
			.BYTE b + 1 | $E0
		.ELSE
			.ERROR "Invaild pm3_note length."
		.ENDIF
	.ELSE
		.ERROR "Note is out of bound."
	.ENDIF
.ENDMACRO

.MACRO pm3_sfx_priority b
	.IF b
		.BYTE b
	.ELSE
		.ERROR "Non sfx."
	.ENDIF
.ENDMACRO

.MACRO pm3_sfx_global_channel_flags b
	.IF b & sfx_loop_set
		current_sfx_loop_set .SET 1
	.ELSE
		current_sfx_loop_set .SET 0
	.ENDIF
	.IF b & sfx_ads_set
		current_sfx_ads_set .SET 1
	.ELSE
		current_sfx_ads_set .SET 0
	.ENDIF
	.IF b & sfx_global_transpose_set
		current_sfx_global_transpose_set .SET 1
	.ELSE
		current_sfx_global_transpose_set .SET 0
	.ENDIF
	.BYTE b
.ENDMACRO

.MACRO pm3_sfx_loop b, c
	.IF current_sfx_loop_set
		.BYTE b
		.DBYT c
	.ELSE
		.ERROR "sfx loop is not set."
	.ENDIF
.ENDMACRO

.MACRO pm3_sfx_ads b
	.IF current_sfx_ads_set
		.BYTE b
	.ELSE
		.ERROR "sfx ads is not set."
	.ENDIF
.ENDMACRO

.MACRO pm3_sfx_global_transpose b
	.IF current_sfx_global_transpose_set
		current_sfx_global_transpose .SET b
		.BYTE b
	.ELSE
		.ERROR "sfx global transpose is not set."
	.ENDIF
.ENDMACRO

.MACRO pm3_sfx_frames b
	.BYTE b
.ENDMACRO

.MACRO pm3_sfx_channel_flags b
	.IF b & sfx_instruments_set
		current_sfx_instruments_set .SET 1
	.ELSE
		current_sfx_instruments_set .SET 0
	.ENDIF
	.IF b & sfx_duty_cycle_set
		current_sfx_duty_cycle_set .SET 1
	.ELSE
		current_sfx_duty_cycle_set .SET 0
	.ENDIF
	.IF b & sfx_volume_set
		current_sfx_volume_set .SET 1
	.ELSE
		current_sfx_volume_set .SET 0
	.ENDIF
	.IF b & sfx_triangle_note_length_set
		current_sfx_triangle_note_length_set .SET 1
	.ELSE
		current_sfx_triangle_note_length_set .SET 0
	.ENDIF
	.IF b & sfx_pitch_slide_set
		current_sfx_pitch_slide_set .SET 1
	.ELSE
		current_sfx_pitch_slide_set .SET 0
	.ENDIF
	.IF b & sfx_pitch_tune_set
		current_sfx_pitch_tune_set .SET 1
	.ELSE
		current_sfx_pitch_tune_set .SET 0
	.ENDIF
	.BYTE b
.ENDMACRO

.MACRO pm3_sfx_instruments b
	.IF current_sfx_instruments_set
		.BYTE b
	.ELSE
		.ERROR "sfx instruments is not set."
	.ENDIF
.ENDMACRO

.MACRO pm3_sfx_duty_cycle b
	.IF current_sfx_duty_cycle_set
		.BYTE b << 6
	.ELSE
		.ERROR "sfx duty cycle is not set."
	.ENDIF
.ENDMACRO

.MACRO pm3_sfx_volume b
	.IF current_sfx_volume_set
		.IF b >= 0 && b < 16
			.BYTE b
		.ELSE
			.ERROR "Invaild pm3_volume."
		.ENDIF
	.ELSE
		.ERROR "sfx pm3_volume is not set."
	.ENDIF
.ENDMACRO

.MACRO pm3_sfx_triangle_note_length b
	.IF current_sfx_triangle_note_length_set
		.BYTE b
	.ELSE
		.ERROR "sfx triangle pm3_note length is not set."
	.ENDIF
.ENDMACRO

.MACRO pm3_sfx_pitch_slide b
	.IF current_sfx_pitch_slide_set
		.BYTE b
	.ELSE
		.ERROR "sfx pitch slide is not set."
	.ENDIF
.ENDMACRO

.MACRO pm3_sfx_pitch_tune b
	.IF current_sfx_pitch_tune_set
		.BYTE b
	.ELSE
		.ERROR "sfx pitch tune is not set."
	.ENDIF
.ENDMACRO

.MACRO pm3_sfx_note b
	.BYTE b + 1 - current_sfx_global_transpose
.ENDMACRO

.MACRO pm3_sfx_noise_note b
	.BYTE b + 1
.ENDMACRO

.MACRO pm3_sfx_end
	.BYTE $FF
.ENDMACRO

.MACRO pm3_music_queue b
	LDA #b
	JSR _music_queue
.ENDMACRO

.MACRO pm3_sfx_queue b
	LDA #b
	JSR _sfx_queue
.ENDMACRO

_nmi_audio_processing:
	JMP _audio_processing

_nmi_audio_track_queue:
	JMP _audio_track_queue

_fraction255:
.if ::MAPPER_MMC5
 ; Same four-byte prefix keeps every native code/data address unchanged.
 JMP _fraction255_mmc5
 NOP
.else
 LDA #$00
 STA z:zaudio_C2
.endif
	LDY #$08

@loop:
	ASL z:zaudio_C2
	ROL z:zaudio_C1
	BCC @not_9bits
	CLC
	LDA z:zaudio_C2
	ADC z:zaudio_C4
	STA z:zaudio_C2
	LDA z:zaudio_C1
	ADC #$00
	STA z:zaudio_C1

@not_9bits:
	DEY
	BNE @loop
	RTS

_audio_cmd_jmp:
	ASL
	TAY
	INY
	PLA
	STA z:zaudio_C1
	PLA
	STA z:zaudio_C2
	LDA (zaudio_C1), Y
	PHA
	INY
	LDA (zaudio_C1), Y
	STA z:zaudio_C2
	PLA
	STA z:zaudio_C1
	JMP (zaudio_C1)

_read_audio_data:
 STY z:zaudio_C1
 STA z:zaudio_C2
 LDY #0
 LDA (zaudio_C1),y
 RTS

_audio_processing:
	LDA z:zplayback_flag
	LSR
	BCS @done
	LDA z:zsfx_lo
	ORA z:zsfx_hi
	BEQ @no_sfx
	JSR _is_sfx

@no_sfx:
	CLC
	LDA z:ztempo_lo
	ADC z:zdec_note_length_rate
	STA z:zdec_note_length_rate
	LDA z:ztempo_hi
	ADC #$00
	STA z:zdec_note_length
	LDA z:zsfx_channel
	PHA
	LDX #$03

@loop:
	LSR z:zsfx_channel
	BCC @skip
	LDA z:zsfx_channel
	ORA #$80
	STA z:zsfx_channel
	JSR _handle_sfx_channel

@skip:
	LDA z:zplayback_flag
	AND #%00000010
	BNE @pause
	TXA
	PHA
	JSR _handle_music
	PLA
	TAX

@pause:
	DEX
	BPL @loop
	PLA
	STA z:zsfx_channel
	LSR z:zplayback_flag
	ASL z:zplayback_flag
	LDA z:zfade_direction
	AND #%01111111
	BEQ @done
	LDY #$00
	STY z:zaudio_C1
	LDY #$04

@shift_loop:
	ASL
	ROL z:zaudio_C1
	DEY
	BNE @shift_loop
	CLC
	ADC z:zplayback_flag
	STA z:zplayback_flag
	LDA z:zaudio_C1
	ADC z:zfade_level
	BCC @not_max
	LDA z:zfade_direction
	AND #%10000000
	STA z:zfade_direction
	LDA #$FF

@not_max:
	STA z:zfade_level

@done:
	RTS

_init_channel:
	TXA
	AND #%00000011
	EOR #%00000011
	ASL
	ASL
	TAY
	LDA #$30
	CPY #$08
	BNE @not_triangle
	LDA #$00

@not_triangle:
.if ::MAPPER_MMC5
	JMP ::GuestNativeStoreSTA00Y
	NOP
.else
	JSR ::GuestNativeStoreSTA00Y
	RTS
.endif

_handle_channel:
	PHA
	TXA
	AND #%00000011
	EOR #%00000011
	ASL
	ASL
	STY z:zaudio_C4
	ORA z:zaudio_C4
	TAY
	PLA
.if ::MAPPER_MMC5
	JMP ::GuestNativeStoreSTA00Y
	NOP
.else
	JSR ::GuestNativeStoreSTA00Y
	RTS
.endif

_audio_track_queue:
	INC z:zplayback_flag
	JSR _branch_audio_track_queue
	DEC z:zplayback_flag
	RTS

_branch_audio_track_queue:
	CMP #$F0
	BCC @is_regular_audio_track_queue
	JMP _is_sound_cmd

@is_regular_audio_track_queue:
@loop:
	CMP no_of_track_pointers
	BCC _read_track_pointers
	SEC
	SBC no_of_track_pointers
	BCS @loop

_read_track_pointers:
	ASL
	TAX
	LDY track_pointers + 1, X
	TYA
	ORA track_pointers, X
	BEQ @skip
	LDA track_pointers, X
	JSR _read_audio_data
	TAY
	BEQ _is_music
	LDY #$00
	INX
	STA z:zaudio_C4
	AND #%01111111
	CMP z:zsfx_priority
	BCC @skip
	STA z:zsfx_priority
	BNE @not_init_repeat
	LDA z:zsfx_loop
	BPL @not_init_repeat
	LDA z:zaudio_C4
	BMI @not_init_repeat
	STY z:zsfx_repeat

@not_init_repeat:
	STY z:zsfx_loop
	ASL z:zaudio_C4
	ROR z:zsfx_loop
	BPL @no_sfx_repeat
	STX z:zsfx_repeat

@no_sfx_repeat:
	INC z:zaudio_C1
	LDA z:zaudio_C1
	STA z:zsfx_lo
	BNE @nz
	INC z:zaudio_C2

@nz:
	LDA z:zaudio_C2
	STA z:zsfx_hi
	TYA
	STA z:zsfx_global_transpose
	STA z:zsfx_frames
	STA z:zsfx_ads
	STA z:zsfx_ads_remain
	LDY #$27

@loop:
	STA achannel_instrument, Y
	DEY
	BPL @loop

@skip:
	RTS

_is_music:
	LDX #$01
	STX z:ztempo_hi
	LDX #$99
	STX z:ztempo_lo
	STA z:zdec_note_length_rate
	STA z:zglobal_transpose
	STA z:zfade_direction
	STA z:zfade_level
	LDX #$53

@init_loop:
	STA amusic_lo, X
	DEX
	BPL @init_loop
	LDX #$03

@loop:
	INC z:zaudio_C1
	BNE @nz_1
	INC z:zaudio_C2

@nz_1:
	LDY z:zaudio_C1
	LDA z:zaudio_C2
	JSR _read_audio_data
	STA amusic_hi + $28, X
	INC z:zaudio_C1
	BNE @nz_2
	INC z:zaudio_C2

@nz_2:
	LDY z:zaudio_C1
	LDA z:zaudio_C2
	JSR _read_audio_data
	STA amusic_lo + $28, X
	DEX
	BPL @loop
	BMI _init_channel_pointers_common

_is_sound_cmd:
	STY z:zaudio_C3
	AND #%00000111
	JSR _audio_cmd_jmp

	.WORD _init_audio
	.WORD _init_sfx_pointers
	.WORD _init_music_pointers
	.WORD _pause_music
	.WORD _play_music
	.WORD _fade_in
	.WORD _fade_out
	.WORD _sfx_pitch_tune

_init_audio:
	JSR _init_music_pointers

_init_sfx_pointers:
	LDA #$00
	STA z:zsfx_priority
	STA z:zsfx_lo
	STA z:zsfx_hi
	STA z:zsfx_repeat
	STA z:zsfx_pitch_tune

_init_sfx:
	LDA z:zsfx_channel
	BEQ @skip
	EOR #%00001111
	STA z:zsfx_channel
	JSR _init_channel_pointers_common
	LDA #$00
	STA z:zsfx_channel

@skip:
	RTS

_init_music_pointers:
	LDA #$00
	LDX #$03

@loop:
	STA amusic_hi + $28, X
	STA amusic_lo + $28, X
	DEX
	BPL @loop

_init_channel_pointers_common:
	LDA z:zsfx_channel
	PHA
	LDX #$03

@loop:
	LSR z:zsfx_channel
	BCS @skip
	JSR _init_channel
	LDA amusic_hi + $28, X
	ORA amusic_lo + $28, X
	BEQ @skip
	LDA #$FF
	STA achannel_handle, X

@skip:
	DEX
	BPL @loop
	PLA
	STA z:zsfx_channel
	LDA #%00001000
	JSR ::GuestNativeStoreSTA01
	JSR ::GuestNativeStoreSTA05
	LDA #%00001111
	JSR ::GuestNativeStatusSTA
	RTS

_pause_music:
	LDA z:zplayback_flag
	ORA #%00000010
	STA z:zplayback_flag
	BNE _init_channel_pointers_common

_play_music:
	LDA z:zplayback_flag
	AND #%11111101
	STA z:zplayback_flag
	RTS

_fade_in:
	ASL z:zaudio_C3
	BEQ _fade_out
	SEC
	ROR z:zaudio_C3

_fade_out:
	LDA z:zplayback_flag
	AND #%00001111
	STA z:zplayback_flag
	LDY z:zaudio_C3
	STY z:zfade_direction
	BEQ @init_fade_level
	LDY #$FF
	CPY z:zfade_level
	BNE @not_max
	INY

@init_fade_level:
	STY z:zfade_level

@not_max:
	RTS

_sfx_pitch_tune:
	LDA #$00
	SEC
	SBC z:zaudio_C3
	STA z:zsfx_pitch_tune
	RTS

_is_sfx:
	LDA z:zsfx_frames
	BEQ _handle_sfx_data
	DEC z:zsfx_frames
	DEC z:zsfx_ads_remain
	RTS

_handle_sfx_data:
	JSR _read_sfx_data
	STA z:zaudio_C4
	ASL
	BCC @not_sfx_end
	STY z:zsfx_priority
	LDA z:zsfx_repeat
	LSR
	BCC @no
	JSR _read_track_pointers
	JMP _handle_sfx_data

@no:
	JMP _init_sfx_pointers

@not_sfx_end:
	LSR z:zaudio_C4
	BCC @check_sfx_ads
	JSR _read_sfx_data
	ASL
	BEQ @loop_z
	ASL z:zsfx_loop
	PHP
	CMP z:zsfx_loop
	BEQ @set_loop_count
	PLP
	ROR z:zsfx_loop
	INC z:zsfx_loop

@loop_z:
	JSR _read_sfx_data
	TAX
	JSR _read_sfx_data
	STA z:zsfx_lo
	STX z:zsfx_hi
	BNE _handle_sfx_data

@set_loop_count:
	TYA
	PLP
	ROR
	STA z:zsfx_loop
	CLC
	LDA #$02
	ADC z:zsfx_lo
	STA z:zsfx_lo
	BCC @check_sfx_ads
	INC z:zsfx_hi

@check_sfx_ads:
	LSR z:zaudio_C4
	BCC @check_sfx_global_transpose
	JSR _read_sfx_data
	STA z:zsfx_ads

@check_sfx_global_transpose:
	LSR z:zaudio_C4
	BCC @done
	JSR _read_sfx_data
	STA z:zsfx_global_transpose

@done:
	JSR _read_sfx_data
	STA z:zsfx_frames
	STA z:zaudio_C1
	LDA z:zsfx_ads
	STA z:zaudio_C4
	JSR _fraction255
	LDY z:zaudio_C1
	INY
	STY z:zsfx_ads_remain
	INC z:zplayback_flag
	JSR _read_sfx_data
	PHA
	EOR z:zsfx_channel
	BEQ @same
	STA z:zsfx_channel
	JSR _init_sfx

@same:
	PLA
	STA z:zsfx_channel
	RTS

_handle_sfx_channel:
	LDY achannel_instrument, X
	BEQ @no_instrument_set
	JSR _read_instrument_pointers

@no_instrument_set:
	LDA z:zplayback_flag
	LSR
	BCS @handle_sfx
	JSR _handle_adsr
	LDA z:zsfx_frames
	BEQ @done
	CPX #$01
	BEQ @is_triangle
	LDA z:zsfx_ads_remain
	BEQ @is_release

@done:
	RTS

@is_triangle:
	DEC aadsr_volume, X
	BNE @done

@is_release:
	LDA astats_adsr_state, X
	AND #%00000100
	BNE @done
	JMP _play_rest

@handle_sfx:
	LDA #$00
	STA z:zaudio_C4
	JSR _read_sfx_data

@loop:
	LSR
	BCC @skip
	PHA
	JSR _read_sfx_data
	STA z:zaudio_C3
	LDA z:zaudio_C4
	JSR _sfx_cmd
	PLA

@skip:
	BEQ _sfx_cmd_done
	INC z:zaudio_C4
	BNE @loop

_sfx_cmd:
	JSR _audio_cmd_jmp

	.WORD _cmd_instrument
	.WORD _cmd_duty_cycle
	.WORD _cmd_volume
	.WORD _cmd_pitch_slide
	.WORD _cmd_pitch_tune

_sfx_cmd_done:
	JSR _read_sfx_data
	TAY
	BNE @nz
	STA aadsr_volume, X
	LDA astats_adsr_state, X
	AND #%11111000
	ORA #$04
	STA astats_adsr_state, X
	JMP _init_channel

@nz:
	LDA astats_adsr_state, X
	ORA #$20
	STA astats_adsr_state, X
	LDA achannel_pitch_slide, X
	ASL
	LDA #$54
	BCS @max
	LDA #$0A

@max:
	STA anote, X
	TYA
	BPL @next_sfx_note
	CPX #$01
	BNE @not_triangle
	JSR _init_adsr

@not_triangle:
	JMP _connect_had_set

@next_sfx_note:
	JSR _init_adsr
	LDA #$FF
	STA achannel_handle, X
	DEY
	TXA
	BNE @not_noise
	STA z:zaudio_C3
	TYA
	EOR #%00001111
	JMP _write_freq

@not_noise:
	TYA
	CLC
	ADC z:zsfx_global_transpose
	JMP _handle_freq_index

_read_sfx_data:
	LDY z:zsfx_lo
	LDA z:zsfx_hi
	INC z:zsfx_lo
	BNE @nz
	INC z:zsfx_hi

@nz:
	JMP _read_audio_data

_handle_music:
 LDA ::MmAudioEngine
 CMP #2
 BNE :+
 RTS
:
	TXA
	ORA #$28
	TAX
	LDA amusic_lo, X
	ORA amusic_hi, X
	BEQ @skip
	LDA anote_length_remain, X
	BEQ _play_note_done
	LDY achannel_instrument, X
	BEQ @no_instrument_set
	JSR _read_instrument_pointers
	JSR _handle_adsr

@no_instrument_set:
	LDA anote_ads_remain, X
	SEC
	SBC z:zdec_note_length
	STA anote_ads_remain, X
	BEQ @is_release
	BCS @is_ads

@is_release:
	JSR _play_rest

@is_ads:
	LDA anote_length_remain, X
	SEC
	SBC z:zdec_note_length
	STA anote_length_remain, X
	BEQ _play_note_done
	BCC _play_note_done

@skip:
	RTS

_play_note_done:
	JSR _read_music_data
	CMP #$20
	BCS _is_note
	JSR _music_cmd
	JMP _play_note_done

_is_note:
	PHA
	ROL
	ROL
	ROL
	ROL
	AND #%00000111
	TAY
	DEY
	LDA anote_flags, X
	ASL
	ASL
	BPL @is_regular_length
	LDA _triplet_note_length_table, Y
	BNE @get_note_length_done

@is_regular_length:
	ASL
	ASL
	LDA _regular_note_length_table, Y
	BCC @get_note_length_done

;set dotted pm3_note length
	STA z:zaudio_C3
	LDA anote_flags, X
	AND #%11101111
	STA anote_flags, X
	LDA z:zaudio_C3
	LSR
	CLC
	ADC z:zaudio_C3

@get_note_length_done:
	CLC
	ADC anote_length_remain, X
	STA anote_length_remain, X
	TAY
	PLA
	AND #%00011111
	BNE @not_rest
	JSR _play_rest
	JMP @max_ads

@not_rest:
	PHA
	STY z:zaudio_C4
	LDA anote_ads, X
	STA z:zaudio_C1
	JSR _fraction255
	LDA z:zaudio_C1
	BNE @fraction_done
	LDA #$01

@fraction_done:
	STA anote_ads_remain, X
	PLA
	TAY
	DEY
	LDA anote_flags, X
	BPL @connect_had_not_set
	LDA achannel_pitch_slide, X
	BNE @freq_handling
	JSR _connect_had_set
	JMP @connect_switch

@connect_had_not_set:
	JSR _init_adsr
	LDA z:zsfx_channel
	BMI @freq_handling
	STY z:zaudio_C3
	TXA
	AND #%00000011
	TAY
	LDA #$FF
	STA achannel_handle, Y
	LDY z:zaudio_C3

@freq_handling:
	TXA
	AND #%00000011
	BNE @not_noise
	STA z:zaudio_C3
	TYA
	AND #%00001111
	EOR #%00001111
	JSR _write_freq
	JMP @connect_switch

@not_noise:
	STY z:zaudio_C3
	LDA anote_flags, X
	AND #%00001111
	TAY
	LDA _octave_table, Y
	CLC
	ADC z:zaudio_C3
	CLC
	ADC z:zglobal_transpose
	CLC
	ADC achannel_transpose, X
	JSR _handle_freq_index

@connect_switch:
	LDA anote_flags, X
	TAY
	AND #%01000000
	ASL
	STA z:zaudio_C4
	TYA
	AND #%01111111
	ORA z:zaudio_C4
	STA anote_flags, X
	BPL @disable_done

@max_ads:
	LDA #$FF
	STA anote_ads_remain, X

@disable_done:
	RTS

_music_cmd:
	CMP #$04
	BCC @single_byte
	STA z:zaudio_C4
	JSR _read_music_data
	STA z:zaudio_C3
	LDA z:zaudio_C4

@single_byte:
	JSR _audio_cmd_jmp

	.WORD _cmd_triplet_note_set
	.WORD _cmd_connect_note_set
	.WORD _cmd_dotted_note_set
	.WORD _cmd_octave_jump
	.WORD _cmd_channel_flags
	.WORD _cmd_tempo
	.WORD _cmd_note_ads
	.WORD _cmd_volume
	.WORD _cmd_instrument
	.WORD _cmd_octave
	.WORD _cmd_global_transpose
	.WORD _cmd_channel_transpose
	.WORD _cmd_pitch_tune
	.WORD _cmd_pitch_slide
	.WORD _cmd_loop_1
	.WORD _cmd_loop_2
	.WORD _cmd_loop_3
	.WORD _cmd_loop_4
	.WORD _cmd_break_1
	.WORD _cmd_break_2
	.WORD _cmd_break_3
	.WORD _cmd_break_4
	.WORD _cmd_music_jump
	.WORD _cmd_music_end
	.WORD _cmd_duty_cycle

_cmd_triplet_note_set:
	LDA #%00100000
	BNE _switch_cmd_note_flags

_cmd_connect_note_set:
	LDA #%01000000
	BNE _switch_cmd_note_flags

_cmd_dotted_note_set:
	LDA #%00010000
	ORA anote_flags, X
	BNE _switch_cmd_note_flags_done

_cmd_octave_jump:
	LDA #$08

_switch_cmd_note_flags:
	EOR anote_flags, X

_switch_cmd_note_flags_done:
	STA anote_flags, X
	RTS

_cmd_tempo:
	LDA #$00
	STA z:zdec_note_length_rate
	JSR _read_music_data
	LDY z:zaudio_C3
	STA z:ztempo_lo
	STY z:ztempo_hi
	RTS

_cmd_note_ads:
	LDA z:zaudio_C3
	STA anote_ads, X
	RTS

_cmd_octave:
	LDA anote_flags, X
	AND #%11111000
	ORA z:zaudio_C3
	STA anote_flags, X
	RTS

_cmd_global_transpose:
	LDA z:zaudio_C3
	STA z:zglobal_transpose
	RTS

_cmd_channel_transpose:
	LDA z:zaudio_C3
	STA achannel_transpose, X
	RTS

_cmd_loop_1:
_cmd_break_1:
	LDA #$00
	BEQ _set_cmd_loop_pointers

_cmd_loop_2:
_cmd_break_2:
	LDA #$04
	BNE _set_cmd_loop_pointers

_cmd_loop_3:
_cmd_break_3:
	LDA #$08
	BNE _set_cmd_loop_pointers

_cmd_loop_4:
_cmd_break_4:
	LDA #$0C

_set_cmd_loop_pointers:
	STA z:zaudio_C2
	TXA
	CLC
	ADC z:zaudio_C2
	TAY
	LDA z:zaudio_C4
	CMP #$12
	BCS @break
	LDA achannel_loop_counter, Y
	SEC
	SBC #$01
	BCS @nz
	LDA z:zaudio_C3

@nz:
	STA achannel_loop_counter, Y
	BEQ _skip_2bytes
	BNE @read_2bytes

@break:
	LDA achannel_loop_counter, Y
	SEC
	SBC #$01
	BNE _skip_2bytes
	STA achannel_loop_counter, Y
	JSR _cmd_channel_flags

@read_2bytes:
	JSR _read_music_data
	STA z:zaudio_C3

_cmd_music_jump:
	JSR _read_music_data
	STA amusic_lo, X
	LDA z:zaudio_C3
	STA amusic_hi, X
	RTS

_skip_2bytes:
	LDA #$02
	CLC
	ADC amusic_lo, X
	STA amusic_lo, X
	BCC @nz
	INC amusic_hi, X

@nz:
	RTS

_cmd_channel_flags:
	LDA anote_flags, X
	AND #%10010111
	ORA z:zaudio_C3
	STA anote_flags, X
	RTS

_cmd_music_end:
	PLA
	PLA
	LDA #$00
	STA amusic_lo, X
	STA amusic_hi, X
	LDA z:zsfx_channel
	BMI @sfx_handling
	JMP _init_channel

@sfx_handling:
	RTS

_read_music_data:
	LDY amusic_lo, X
	LDA amusic_hi, X
	INC amusic_lo, X
	BNE @nz
	INC amusic_hi, X

@nz:
	JMP _read_audio_data

_play_rest:
	LDA astats_adsr_state, X
	AND #%11111000
	ORA #%00000011
	STA astats_adsr_state, X
	RTS

_init_adsr:
	TYA
	PHA
	LDY #$00
	LDA astats_adsr_state, X
	AND #%11111000
	STA astats_adsr_state, X
	CPX #$29
	BEQ @is_triangle
	CPX #$01
	BNE @not_triangle
	LDA z:zsfx_frames
	STA z:zaudio_C1
	LDA achannel_volume_duty_cycle, X
	STA z:zaudio_C4
	JSR _fraction255
	LDY z:zaudio_C1

@is_triangle:
	INY
	INC astats_adsr_state, X
	INC astats_adsr_state, X

@not_triangle:
	TYA
	STA aadsr_volume, X
	PLA
	TAY
	RTS

_handle_freq_index:
	CMP #$60
	BCC @not_overflow
	LDA #$5F

@not_overflow:
	STA z:zaudio_C3
	INC z:zaudio_C3
	CPX #$28
	BCC @is_sfx
	LDA anote, X
	BEQ @skip
	CMP z:zaudio_C3
	BNE @not_same_note
	LDA anote_flags, X
	BPL @skip
	BMI _connect_had_set

@not_same_note:
	LDA achannel_pitch_slide, X
	BEQ @skip
	BCS @pitch_down
	ORA #%10000000
	BNE @pitch_up

@pitch_down:
	AND #%01111111

@pitch_up:
	STA achannel_pitch_slide, X
	LDA astats_adsr_state, X
	ORA #%00100000
	STA astats_adsr_state, X
	LDA z:zaudio_C3
	LDY anote, X
	STY z:zaudio_C3
	BNE @not_rest

@skip:
	LDA astats_adsr_state, X
	AND #%11011111
	STA astats_adsr_state, X
	LDA z:zaudio_C3

@not_rest:
	STA anote, X

@is_sfx:
	ASL z:zaudio_C3
	LDY z:zaudio_C3
	LDA _note_freq_table - 2, Y
	STA z:zaudio_C3
	LDA _note_freq_table - 1, Y

_write_freq:
	STA afreq_hi, X
	LDA z:zaudio_C3
	STA afreq_lo, X
	LDY #$04
	LDA (zinstrument_lo), Y
	BMI _instrument_done

_connect_had_set:
	LDA astats_adsr_state, X
	AND #%00001000
	BNE _instrument_done
	RTS

_instrument_done:
	LDA #$00
	STA ainvert_vibrato, X
	LDA astats_adsr_state, X
	AND #%00110111
	STA astats_adsr_state, X
	RTS

_cmd_volume:
	CPX #$01
	BNE @not_triangle
	LDA z:zaudio_C3
	BNE @done

@not_triangle:
	LDA achannel_volume_duty_cycle, X
	AND #%11000000
	ORA z:zaudio_C3
	ORA #%00110000

@done:
	STA achannel_volume_duty_cycle, X
	RTS

_cmd_instrument:
	INC z:zaudio_C3
	LDA z:zaudio_C3
	CMP achannel_instrument, X
	BEQ _skip_cmd_instrument_set
	STA achannel_instrument, X
	TAY
	LDA astats_adsr_state, X
	ORA #%00001000
	STA astats_adsr_state, X

_read_instrument_pointers:
	DEY
	LDA #$00
	STA z:zaudio_C3
	TYA
	ASL
	ROL z:zaudio_C3
	ASL
	ROL z:zaudio_C3
	ASL
	ROL z:zaudio_C3
	CLC
	ADC instrument_pointers + 1
	STA z:zinstrument_lo
	LDA z:zaudio_C3
	ADC instrument_pointers
	STA z:zinstrument_hi

_skip_cmd_instrument_set:
	RTS

_cmd_pitch_tune:
	LDA z:zaudio_C3
	STA achannel_pitch_tune, X
	RTS

_cmd_pitch_slide:
	LDA z:zaudio_C3
	STA achannel_pitch_slide, X
	RTS

_cmd_duty_cycle:
	LDA achannel_volume_duty_cycle, X
	AND #%00001111
	ORA z:zaudio_C3
	ORA #%00110000
	STA achannel_volume_duty_cycle, X
	RTS

_handle_adsr:
	LDA aadsr_volume, X
	STA z:zaudio_C4
	LDA astats_adsr_state, X
	AND #%00000111
	JSR _audio_cmd_jmp

	.WORD @adsr_attack
	.WORD @adsr_decay
	.WORD @adsr_sustain
	.WORD @adsr_release
	.WORD @adsr_nothing

@adsr_attack:
	LDY #$00
	LDA (zinstrument_lo), Y
	TAY
	LDA z:zaudio_C4
	CLC
	ADC _adr_table, Y
	BCS @lef0
	CMP #$F0
	BCC @save_adsr

@lef0:
	LDA #$F0
	BNE @inc_adsr_state

@adsr_decay:
	LDY #$01
	LDA (zinstrument_lo), Y
	BEQ @decay_done
	TAY
	LDA z:zaudio_C4
	SEC
	SBC _adr_table, Y
	BCC @decay_done
	LDY #$02
	CMP (zinstrument_lo), Y
	BCS @save_adsr

@decay_done:
	LDY #$02
	LDA (zinstrument_lo), Y
	JMP @inc_adsr_state

@adsr_release:
	TXA
	AND #%00000011
	CMP #$01
	BEQ @is_triangle
	LDY #$03
	LDA (zinstrument_lo), Y
	BEQ @adsr_sustain
	TAY
	LDA z:zaudio_C4
	SEC
	SBC _adr_table, Y
	BCS @save_adsr

@is_triangle:
	LDA #$00

@inc_adsr_state:
	INC astats_adsr_state, X

@save_adsr:
	STA aadsr_volume, X

@adsr_sustain:
	CPX #$28
	BCC @is_sfx
	LDA z:zsfx_channel
	BPL @not_sfx_data_handling
	JMP @not_replace

@not_sfx_data_handling:
	LDA z:zfade_level
	LDY z:zfade_direction
	BMI @fade_in
	EOR #%11111111

@fade_in:
	CMP #$FF
	BNE @not_max

@is_sfx:
	TXA
	AND #%00000011
	CMP #$01
	BNE @not_sfx_triangle
	BEQ @is_sfx_triangle

@not_max:
	CPX #$29
	BNE @not_music_triangle
	STA z:zaudio_C4
	LDA anote_ads_remain, X
	STA z:zaudio_C1
	JSR _fraction255
	LDA z:zaudio_C1
	BEQ @not_mute

@is_sfx_triangle:
	LDA aadsr_volume, X
	BEQ @not_mute
	LDA #$FF
	BNE @not_mute

@not_music_triangle:
	CMP aadsr_volume, X
	BCC @not_adsr_volume

@not_sfx_triangle:
	LDA aadsr_volume, X

@not_adsr_volume:
	LSR
	LSR
	LSR
	LSR
	EOR #%00001111
	STA z:zaudio_C3
	LDY #$06
	LDA (zinstrument_lo), Y
	CMP #$05
	BCC @skip_volume_vibrato_handle
	STA z:zaudio_C4
	LDY ainvert_vibrato, X
	LDA astats_adsr_state, X
	ASL
	ASL
	TYA
	BCC @volume_down
	EOR #%11111111

@volume_down:
	BEQ @skip_volume_vibrato_handle
	STA z:zaudio_C1
	JSR _fraction255
	LDA z:zaudio_C1
	LSR
	LSR
	CMP #$10
	BCS @mute
	CMP z:zaudio_C3
	BCC @skip_volume_vibrato_handle
	STA z:zaudio_C3

@skip_volume_vibrato_handle:
	LDA #%00010000
	STA z:zaudio_C4
	LDA achannel_volume_duty_cycle, X
	SEC
	SBC z:zaudio_C3
	BIT z:zaudio_C4
	BNE @not_mute

@mute:
	LDA achannel_volume_duty_cycle, X
	AND #%11110000

@not_mute:
	LDY #$00
	JSR _handle_channel
	TXA
	AND #%00000011
	TAY
	LDA achannel_handle, Y
	BMI @do_regular_freq
	LDY #$05
	LDA (zinstrument_lo), Y
	BEQ @do_regular_freq
	STA z:zaudio_C4
	LDY ainvert_vibrato, X
	LDA astats_adsr_state, X
	ASL
	ASL
	TYA
	BCC @pitch_down
	EOR #%11111111

@pitch_down:
	BEQ @do_regular_freq
	STA z:zaudio_C1
	JSR _fraction255
	LDA z:zaudio_C1
	LSR
	ROR z:zaudio_C2
	LSR
	ROR z:zaudio_C2
	LSR
	ROR z:zaudio_C2
	LSR
	ROR z:zaudio_C2
	TAY
	ORA z:zaudio_C2
	BEQ @do_regular_freq
	LDA astats_adsr_state, X
	BMI @pitch_top_to_bottom
	CLC
	LDA z:zaudio_C2
	ADC afreq_lo, X
	STA z:zaudio_C2
	TYA
	ADC afreq_hi, X
	BNE @up

@pitch_top_to_bottom:
	SEC
	LDA afreq_lo, X
	SBC z:zaudio_C2
	STA z:zaudio_C2
	LDA afreq_hi, X
	STY z:zaudio_C1
	SBC z:zaudio_C1

@up:
	TAY
	BNE @common

@do_regular_freq:
	LDA afreq_lo, X
	STA z:zaudio_C2
	LDY afreq_hi, X

@common:
	CPX #$28
	BCS @skip_sfx_pitch_tune
	LDA z:zsfx_loop
	BPL @skip_sfx_pitch_tune
	LDA z:zsfx_pitch_tune
	BEQ @skip_sfx_pitch_tune
	STA z:zaudio_C4
	STY z:zaudio_C1
	LDA z:zaudio_C2
	PHA
	JSR _fraction255
	PLA
	CLC
	ADC z:zaudio_C2
	STA z:zaudio_C2
	LDA #$00
	ADC z:zaudio_C1
	TAY

@skip_sfx_pitch_tune:
	TXA
	AND #%00000011
	BNE @not_noise
	TYA
	AND #%00001111
	LDY #$07
	ORA (zinstrument_lo), Y
	STA z:zaudio_C2
	LDA #$00
	STA z:zaudio_C1
	BEQ @done

@not_noise:
	TYA
	LDY #$08

@loop_octave:
	DEY
	CMP _note_freq_index_table, Y
	BCC @loop_octave
	STA z:zaudio_C1
	TYA
	CLC
	ADC z:zaudio_C1
	TAY
	AND #%00000111
	CLC
	ADC #$07
	STA z:zaudio_C1
	TYA
	AND #%00111000
	EOR #%00111000
	BEQ @octave7

@loop_freq:
	LSR z:zaudio_C1
	ROR z:zaudio_C2
	SEC
	SBC #$08
	BNE @loop_freq

@octave7:
	LDY #$00
	LDA achannel_pitch_tune, X
	BEQ @done
	BPL @pitch_tune_msb_not_set
	DEY

@pitch_tune_msb_not_set:
	CLC
	ADC z:zaudio_C2
	STA z:zaudio_C2
	TYA
	ADC z:zaudio_C1
	STA z:zaudio_C1

@done:
	LDY #$02
	LDA z:zaudio_C2
	JSR _handle_channel
	TXA
	AND #%00000011
	TAY
	LDA z:zaudio_C1
	CMP achannel_handle, Y
	BEQ @not_replace
	STA achannel_handle, Y
	ORA #%00001000
	LDY #$03
	JSR _handle_channel

@not_replace:
	LDA astats_adsr_state, X
	AND #%00100000
	BEQ @skip
	LDA achannel_pitch_slide, X
	BEQ @no_pitch_slide
	LDY #$00
	ASL
	PHP
	BCC @not_negative
	EOR #%11111111
	CLC
	ADC #$01
	DEY

@not_negative:
	CLC
	ADC afreq_lo, X
	STA afreq_lo, X
	TYA
	ADC afreq_hi, X
	STA afreq_hi, X
	LDA anote, X
	ASL
	TAY
	SEC
	LDA afreq_lo, X
	SBC _note_freq_table - 2, Y
	LDA afreq_hi, X
	AND #%00111111
	SBC _note_freq_table - 1, Y
	LDA #$FF
	ADC #$00
	PLP
	ADC #$00
	BNE @skip
	TXA
	BEQ @skip
	LDA _note_freq_table - 2, Y
	STA afreq_lo, X
	LDA _note_freq_table - 1, Y
	STA afreq_hi, X

@no_pitch_slide:
	LDA astats_adsr_state, X
	AND #%11011111
	STA astats_adsr_state, X

@skip:
	LDY #$04
	LDA (zinstrument_lo), Y
	AND #%01111111
	BEQ @adsr_nothing
	CLC
	ADC ainvert_vibrato, X
	STA ainvert_vibrato, X
	BCC @adsr_nothing
	LDA astats_adsr_state, X
	CLC
	ADC #$40
	STA astats_adsr_state, X

@adsr_nothing:
	RTS

_triplet_note_length_table:
	.BYTE 2   ;1
	.BYTE 4   ;2
	.BYTE 8   ;4
	.BYTE 16  ;8
	.BYTE 32  ;16
	.BYTE 64  ;32
	.BYTE 128 ;64

_regular_note_length_table:
	.BYTE 3   ;1
	.BYTE 6   ;2
	.BYTE 12  ;4
	.BYTE 24  ;8
	.BYTE 48  ;16
	.BYTE 96  ;32
	.BYTE 192 ;64

_octave_table:
	.BYTE $00 ;0
	.BYTE $0C ;1
	.BYTE $18 ;2
	.BYTE $24 ;3
	.BYTE $30 ;4
	.BYTE $3C ;5
	.BYTE $48 ;6
	.BYTE $54 ;7

;octave_jump_set_table
	.BYTE $18 ;2
	.BYTE $24 ;3
	.BYTE $30 ;4
	.BYTE $3C ;5
	.BYTE $48 ;6
	.BYTE $54 ;7
	.BYTE $60 ;7
	.BYTE $6C ;7

_adr_table:
	.BYTE 0   ;00
	.BYTE 1   ;01
	.BYTE 2   ;02
	.BYTE 3   ;03
	.BYTE 4   ;04
	.BYTE 5   ;05
	.BYTE 6   ;06
	.BYTE 7   ;07
	.BYTE 8   ;08
	.BYTE 9   ;09
	.BYTE 10  ;0A
	.BYTE 11  ;0B
	.BYTE 12  ;0C
	.BYTE 14  ;0D
	.BYTE 15  ;0E
	.BYTE 16  ;0F
	.BYTE 18  ;10
	.BYTE 19  ;11
	.BYTE 20  ;12
	.BYTE 22  ;13
	.BYTE 24  ;14
	.BYTE 27  ;15
	.BYTE 30  ;16
	.BYTE 35  ;17
	.BYTE 40  ;18
	.BYTE 48  ;19
	.BYTE 60  ;1A
	.BYTE 80  ;1B
	.BYTE 126 ;1C
	.BYTE 127 ;1D
	.BYTE 254 ;1E
	.BYTE 255 ;1F

_note_freq_index_table:
	.BYTE $00, $07, $0E, $15, $1C, $23, $2A, $31

_note_freq_table:
	.BYTE $5C, $37 ;_E_1, non-standard pm3_note
	.BYTE $9C, $36 ;_Gb1, non-standard pm3_note
	.BYTE $E7, $35 ;_A_1, non-standard pm3_note
	.BYTE $3C, $35 ;_Db2, non-standard pm3_note
	.BYTE $9B, $34 ;_E_2, non-standard pm3_note
	.BYTE $02, $34 ;_A_2, non-standard pm3_note
	.BYTE $72, $33 ;_D_3, non-standard pm3_note
	.BYTE $EA, $32 ;_Bb3, non-standard pm3_note
	.BYTE $6A, $32 ;_C_5, non-standard pm3_note
	.BYTE $F1, $31 ;A_0
	.BYTE $80, $31 ;Bb0
	.BYTE $14, $31 ;B_0
	.BYTE $5C, $30 ;C_1
	.BYTE $9C, $2F ;Db1
	.BYTE $E7, $2E ;D_1
	.BYTE $3C, $2E ;Eb1
	.BYTE $9B, $2D ;E_1
	.BYTE $02, $2D ;F_1
	.BYTE $72, $2C ;Gb1
	.BYTE $EA, $2B ;G_1
	.BYTE $6A, $2B ;Ab1
	.BYTE $F1, $2A ;A_1
	.BYTE $80, $2A ;Bb1
	.BYTE $14, $2A ;B_1
	.BYTE $5C, $29 ;C_2
	.BYTE $9C, $28 ;Db2
	.BYTE $E7, $27 ;D_2
	.BYTE $3C, $27 ;Eb2
	.BYTE $9B, $26 ;E_2
	.BYTE $02, $26 ;F_2
	.BYTE $72, $25 ;Gb2
	.BYTE $EA, $24 ;G_2
	.BYTE $6A, $24 ;Ab2
	.BYTE $F1, $23 ;A_2
	.BYTE $80, $23 ;Bb2
	.BYTE $14, $23 ;B_2
	.BYTE $5C, $22 ;C_3
	.BYTE $9C, $21 ;Db3
	.BYTE $E7, $20 ;D_3
	.BYTE $3C, $20 ;Eb3
	.BYTE $9B, $1F ;E_3
	.BYTE $02, $1F ;F_3
	.BYTE $72, $1E ;Gb3
	.BYTE $EA, $1D ;G_3
	.BYTE $6A, $1D ;Ab3
	.BYTE $F1, $1C ;A_3
	.BYTE $80, $1C ;Bb3
	.BYTE $14, $1C ;B_3
	.BYTE $5C, $1B ;C_4
	.BYTE $9C, $1A ;Db4
	.BYTE $E7, $19 ;D_4
	.BYTE $3C, $19 ;Eb4
	.BYTE $9B, $18 ;E_4
	.BYTE $02, $18 ;F_4
	.BYTE $72, $17 ;Gb4
	.BYTE $EA, $16 ;G_4
	.BYTE $6A, $16 ;Ab4
	.BYTE $F1, $15 ;A_4
	.BYTE $80, $15 ;Bb4
	.BYTE $14, $15 ;B_4
	.BYTE $5C, $14 ;C_5
	.BYTE $9C, $13 ;Db5
	.BYTE $E7, $12 ;D_5
	.BYTE $3C, $12 ;Eb5
	.BYTE $9B, $11 ;E_5
	.BYTE $02, $11 ;F_5
	.BYTE $72, $10 ;Gb5
	.BYTE $EA, $0F ;G_5
	.BYTE $6A, $0F ;Ab5
	.BYTE $F1, $0E ;A_5
	.BYTE $80, $0E ;Bb5
	.BYTE $14, $0E ;B_5
	.BYTE $5C, $0D ;C_6
	.BYTE $9C, $0C ;Db6
	.BYTE $E7, $0B ;D_6
	.BYTE $3C, $0B ;Eb6
	.BYTE $9B, $0A ;E_6
	.BYTE $02, $0A ;F_6
	.BYTE $72, $09 ;Gb6
	.BYTE $EA, $08 ;G_6
	.BYTE $6A, $08 ;Ab6
	.BYTE $F1, $07 ;A_6
	.BYTE $80, $07 ;Bb6
	.BYTE $14, $07 ;B_6
	.BYTE $5C, $06 ;C_7
	.BYTE $9C, $05 ;Db7
	.BYTE $E7, $04 ;D_7
	.BYTE $3C, $04 ;Eb7
	.BYTE $9B, $03 ;E_7
	.BYTE $02, $03 ;F_7
	.BYTE $72, $02 ;Gb7
	.BYTE $EA, $01 ;G_7
	.BYTE $6A, $01 ;Ab7
	.BYTE $F1, $00 ;A_7
	.BYTE $80, $00 ;Bb7
	.BYTE $14, $00 ;B_7

; Charge effects: https://github.com/lsmmega/mm4 at 07eb0e6f03416720baf2348b6516dbc93dd2eb70.
no_of_track_pointers:
	.BYTE (track_pointers_end - track_pointers) / 2

instrument_pointers:
	.DBYT instrument_table_pointers

track_pointers:
	.DBYT music_title
	.DBYT music_protoman_whistle
	.DBYT music_ending
	.DBYT music_staff_roll
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT sfx_landing
	.DBYT sfx_1up
	.DBYT sfx_mega_buster
	.DBYT sfx_megaman_hit
	.DBYT sfx_death
	.DBYT sfx_enemy_hit
	.DBYT sfx_enemy_immune
	.DBYT $0000
	.DBYT sfx_select
	.DBYT sfx_refill
	.DBYT sfx_door
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT sfx_teleport_out
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT $0000
	.DBYT sfx_charge_shot_charging
	.DBYT sfx_charge_shot_full_charging_2
	.DBYT sfx_full_charge_shot
	.DBYT sfx_pharaoh_shot
	.DBYT sfx_pharaoh_full_charge_shot
	.DBYT sfx_refill_continuous
	.DBYT sfx_metal_blade
track_pointers_end:

instrument_table_pointers:
 .FEATURE FORCE_RANGE
	pm3_instrument_set $1F, $01, -0,  $18, $80, 0,   0,   0 
	pm3_instrument_set $1F, $01, -0,  $18, $E4, 6,   0,   0 
	pm3_instrument_set $1E, $00, -0,  $10, $80, 0,   0,   1 
	pm3_instrument_set $1F, $13, -6,  $01, $D6, 7,   0,   0 
	pm3_instrument_set $1F, $11, -10, $01, $E2, 0,   71,  0 
	pm3_instrument_set $1F, $14, -0,  $04, $EE, 4,   0,   0 
	pm3_instrument_set $1F, $19, -5,  $08, $00, 0,   0,   0 
	pm3_instrument_set $1F, $00, -4,  $09, $E3, 2,   0,   0 
	pm3_instrument_set $1F, $0D, -12, $01, $E3, 6,   0,   0 
	pm3_instrument_set $1F, $1B, -5,  $05, $CB, 2,   60,  0 
	pm3_instrument_set $1F, $03, -10, $12, $00, 0,   0,   0 
	pm3_instrument_set $1F, $0A, -5,  $0E, $00, 0,   0,   1 
	pm3_instrument_set $1F, $19, -10, $10, $9E, 32,  38,  0 
	pm3_instrument_set $1D, $09, -6,  $03, $CB, 1,   55,  0 
	pm3_instrument_set $1F, $1F, -1,  $1B, $9E, 88,  124, 0 
	pm3_instrument_set $1F, $1B, -1,  $10, $B8, 0,   30,  0 
	pm3_instrument_set $15, $14, -0,  $04, $00, 0,   0,   0 
	pm3_instrument_set $1A, $14, -0,  $04, $00, 0,   0,   0 
	pm3_instrument_set $1F, $17, -5,  $04, $80, 0,   0,   0 
	pm3_instrument_set $19, $01, -2,  $02, $00, 0,   0,   0 
	pm3_instrument_set $1F, $1D, -4,  $0C, $E4, 5,   0,   0 
	pm3_instrument_set $1A, $18, -6,  $07, $00, 0,   0,   0 
	pm3_instrument_set $1F, $02, -3,  $13, $80, 0,   0,   0 
	pm3_instrument_set $1F, $02, -3,  $15, $5D, 6,   6,   0 
	pm3_instrument_set $1F, $1E, -2,  $0A, $FF, 2,   60,  0 
	pm3_instrument_set $1E, $18, -6,  $01, $C6, 25,  50,  0 
	pm3_instrument_set $1F, $17, -7,  $06, $E4, 2,   40,  0 
	pm3_instrument_set $1F, $17, -8,  $01, $5A, 3,   0,   0 
	pm3_instrument_set $1F, $1C, -4,  $06, $00, 0,   0,   0 
	pm3_instrument_set $1F, $1D, -4,  $0C, $00, 0,   0,   1 
	pm3_instrument_set $1F, $1A, -5,  $05, $FF, 1,   51,  0 
	pm3_instrument_set $1E, $1A, -5,  $05, $E4, 4,   0,   0 
	pm3_instrument_set $1F, $19, -5,  $02, $00, 0,   0,   0 
	pm3_instrument_set $1F, $04, -7,  $02, $80, 0,   0,   0 
	pm3_instrument_set $1F, $1E, -5,  $01, $C6, 0,   50,  0 
	pm3_instrument_set $1F, $1F, -6,  $09, $FF, 0,   45,  0 
	pm3_instrument_set $1F, $1C, -7,  $01, $00, 0,   0,   0 
	pm3_instrument_set $1F, $1E, -5,  $02, $EF, 0,   70,  0 
	pm3_instrument_set $17, $02, -1,  $0F, $80, 0,   0,   0 
	pm3_instrument_set $1F, $1B, -5,  $01, $B0, 7,   98,  0 
	pm3_instrument_set $1F, $1F, -0,  $1F, $00, 0,   0,   0 
	pm3_instrument_set $1F, $1F, -0,  $1F, $FF, 2,   0,   0 
	pm3_instrument_set $1F, $1F, -0,  $1F, $92, 127, 0,   0 
	pm3_instrument_set $1F, $1F, -0,  $1F, $E3, 127, 0,   0 
	pm3_instrument_set $1F, $1F, -0,  $1F, $FF, 76,  0,   0 
	pm3_instrument_set $1F, $1F, -0,  $1F, $99, 127, 0,   0 
	pm3_instrument_set $1D, $1F, -0,  $1F, $80, 0,   0,   0 
	pm3_instrument_set $1F, $1F, -0,  $1F, $B7, 39,  0,   0 
	pm3_instrument_set $1F, $1F, -0,  $04, $80, 0,   0,   0 
	pm3_instrument_set $1F, $1F, -0,  $1F, $A6, 127, 0,   1 
	pm3_instrument_set $1F, $1F, -0,  $1F, $80, 0,   0,   1 
	pm3_instrument_set $1F, $1C, -1,  $1F, $DA, 127, 0,   0 
	pm3_instrument_set $1F, $1F, -0,  $1F, $FF, 10,  0,   0 
	pm3_instrument_set $1C, $13, -14, $1F, $FF, 127, 0,   0 
	pm3_instrument_set $1F, $01, -15, $0F, $E3, 127, 0,   0 
	pm3_instrument_set $1F, $1F, -0,  $08, $00, 0,   0,   0 
	pm3_instrument_set $1F, $15, -5,  $14, $00, 0,   0,   0 
	pm3_instrument_set $1F, $1F, -0,  $1F, $FF, 127, 0,   0 
	pm3_instrument_set $1F, $1F, -0,  $1F, $A5, 127, 0,   0 
	pm3_instrument_set $1F, $1F, -0,  $1F, $D0, 22,  0,   0 
	pm3_instrument_set $1F, $1A, -5,  $07, $CF, 54,  0,   1 
	pm3_instrument_set $12, $02, -5,  $05, $00, 0,   0,   0 
	pm3_instrument_set $1F, $01, -0,  $05, $E1, 13,  0,   0 
	pm3_instrument_set $1F, $12, -11, $1E, $FF, 127, 81,  1 
	pm3_instrument_set $1D, $04, -13, $12, $00, 0,   0,   0 
music_title:
	pm3_music_header
	.DBYT music_title_pulse_1
	.DBYT music_title_pulse_2
	.DBYT music_title_triangle
	.DBYT music_title_noise

;reset
	current_global_transpose .SET 0

music_title_pulse_1:
	current_octave_jump .SET 0
	current_octave .SET 0
	current_channel_transpose .SET 0
	pm3_global_transpose 1
	pm3_tempo $01, $11
	pm3_note_ads $C8
	pm3_volume 13
	pm3_duty_cycle 1
	pm3_instrument 32
	pm3_octave 1
	pm3_octave_jump
	pm3_note Db4, 8
	pm3_rest 8
	pm3_rest 4
	pm3_note Gb3, 4
	pm3_note A_3, 4
	pm3_note B_3, 4
	pm3_note B_3, 1
	pm3_note Db4, 8
	pm3_rest 8
	pm3_dotted_note_set
	pm3_rest 4
	pm3_rest 1
	pm3_note E_4, 8
	pm3_note_ads $BE
	pm3_note Eb4, 8
	pm3_rest 8
	pm3_rest 4
	pm3_note Db4, 4
	pm3_note B_3, 4
	pm3_note D_4, 8
	pm3_rest 8
	pm3_dotted_note_set
	pm3_rest 8
	pm3_note Db4, 4
	pm3_note B_3, 4
	pm3_note B_3, 1
	pm3_dotted_note_set
	pm3_note Db4, 2
	pm3_note A_3, 4
	pm3_note Gb3, 4
	pm3_rest 4
	pm3_note E_3, 4
	pm3_note Gb3, 4
	pm3_rest 4
	pm3_note A_3, 4
	pm3_rest 4
	pm3_note Gb3, 4
	pm3_rest 4
	pm3_note A_3, 4
	pm3_rest 4
	pm3_note B_3, 4
	pm3_rest 4
	pm3_note B_3, 1
	pm3_dotted_note_set
	pm3_note C_4, 2
	pm3_note B_3, 4
	pm3_note A_3, 4
	pm3_note Gb3, 4
	pm3_note A_3, 8
	pm3_rest 8
	pm3_note B_4, 1
	pm3_dotted_note_set
	pm3_note C_5, 2
	pm3_note B_4, 4
	pm3_note A_4, 4
	pm3_note Gb4, 4
	pm3_note A_4, 4
	pm3_instrument 0
	pm3_note A_4, 4
	pm3_dotted_note_set
	pm3_note B_4, 8
	pm3_instrument 32
	pm3_rest 4
	pm3_note Gb3, 4
	pm3_note Ab3, 4
	pm3_note A_3, 4
	pm3_note B_3, 4
	pm3_note Db4, 4
	pm3_note E_4, 4
	pm3_note Gb4, 4
	pm3_rest 4
	pm3_note Db4, 4
	pm3_rest 4
	pm3_note E_4, 4
	pm3_rest 4
	pm3_note Gb4, 4
	pm3_rest 4
	pm3_note Bb4, 1
	pm3_dotted_note_set
	pm3_connect_note_set
	pm3_note B_4, 2
	pm3_connect_note_set
	pm3_note B_4, 2
	pm3_rest 2
	pm3_rest 4
	pm3_note A_4, 4
	pm3_rest 4
	pm3_note Gb4, 4
	pm3_note E_4, 4
	pm3_rest 4
	pm3_note F_4, 1
	pm3_dotted_note_set
	pm3_note Gb4, 2
	pm3_rest 4
	pm3_note F_4, 4
	pm3_note Db4, 8
	pm3_rest 8
	pm3_note F_4, 4
	pm3_note Gb4, 4
	pm3_rest 4
	pm3_octave 2
	pm3_note C_5, 1
	pm3_dotted_note_set
	pm3_note Db5, 2
	pm3_note A_4, 4
	pm3_note Gb4, 4
	pm3_note Db4, 4
	pm3_octave_jump
	pm3_note Gb3, 4
	pm3_note Ab3, 4
	pm3_note A_3, 4
	pm3_connect_note_set
	pm3_note B_3, 2
	pm3_connect_note_set
	pm3_note B_3, 4
	pm3_note_ads $64
	pm3_connect_note_set
	pm3_note Db4, 2
	pm3_connect_note_set
	pm3_note Db4, 4
	pm3_connect_note_set
	pm3_note E_4, 2
	pm3_connect_note_set
	pm3_note E_4, 2
	pm3_connect_note_set
	pm3_note Gb4, 2
	pm3_connect_note_set
	pm3_note Gb4, 4
	pm3_connect_note_set
	pm3_octave_jump
	pm3_note A_4, 2
	pm3_connect_note_set
	pm3_note A_4, 4
	pm3_connect_note_set
	pm3_note B_4, 2
	pm3_connect_note_set
	pm3_note B_4, 2
	pm3_note_ads $78
	pm3_triplet_note_set
	pm3_note B_4, 2
	pm3_connect_note_set
	pm3_note Db5, 2
	pm3_connect_note_set
	pm3_note Db5, 4
	pm3_note B_4, 8
	pm3_note A_4, 8
	pm3_note Gb4, 8
	pm3_note A_4, 8
	pm3_note Ab4, 8
	pm3_note Db4, 8
	pm3_note F_4, 8
	pm3_note Ab4, 8
	pm3_note B_4, 8
	pm3_note Db5, 8
	pm3_note F_5, 8

music_title_pulse_1_loop_1:
	pm3_channel_flags channel_octave_jump_set
	pm3_duty_cycle 1
	pm3_instrument 22
	pm3_octave 1
	pm3_tempo $02, $16
	pm3_note Db4, 4
	pm3_note Db4, 4
	pm3_note B_3, 4
	pm3_note Db4, 4
	pm3_rest 4
	pm3_note B_3, 4
	pm3_rest 4
	pm3_note Db4, 4
	pm3_rest 4
	pm3_note B_3, 4
	pm3_rest 4
	pm3_note Db4, 4
	pm3_note Db4, 4
	pm3_rest 4
	pm3_note B_3, 4
	pm3_rest 4
	pm3_loop_1 1, music_title_pulse_1_loop_1
	pm3_note A_3, 4
	pm3_note Gb3, 4
	pm3_note Ab3, 4
	pm3_note A_3, 4
	pm3_note B_3, 4
	pm3_note Ab3, 4
	pm3_note A_3, 4
	pm3_note B_3, 4
	pm3_note Db4, 4
	pm3_note A_3, 4
	pm3_note B_3, 4
	pm3_note Db4, 4
	pm3_note E_4, 4
	pm3_note D_4, 4
	pm3_note Db4, 4
	pm3_note B_3, 4

music_title_pulse_1_loop_2:
	pm3_channel_flags channel_octave_jump_set
	pm3_note Ab4, 4
	pm3_note Gb4, 4
	pm3_note Db4, 4
	pm3_loop_1 3, music_title_pulse_1_loop_2
	pm3_note Ab4, 4
	pm3_note Gb4, 4
	pm3_note F_4, 4
	pm3_note Db4, 4

music_title_pulse_1_main:
	pm3_channel_flags no_channel_flags_set

music_title_pulse_1_loop_3:
	pm3_channel_flags no_channel_flags_set
	pm3_duty_cycle 1
	pm3_instrument 28
	pm3_octave 2
	pm3_tempo $02, $2E
	pm3_note Gb3, 8
	pm3_note B_3, 8
	pm3_note Db4, 8
	pm3_note Gb3, 8
	pm3_note E_4, 8
	pm3_note Gb3, 8
	pm3_note Eb4, 8
	pm3_note Gb3, 8
	pm3_note B_3, 8
	pm3_note E_4, 8
	pm3_note Gb3, 8
	pm3_note Eb4, 8
	pm3_note Gb3, 8
	pm3_note Db4, 8
	pm3_break_1 no_channel_flags_set, music_title_pulse_1_break_1
	pm3_note Gb3, 8
	pm3_note B_3, 8
	pm3_loop_1 1, music_title_pulse_1_loop_3

music_title_pulse_1_break_1:
	current_octave_jump .SET 0
	pm3_note E_4, 8
	pm3_connect_note_set
	pm3_octave_jump
	pm3_note Ab4, 8
	pm3_connect_note_set
	pm3_note Ab4, 16
	pm3_note Gb4, 8
	pm3_note E_4, 8
	pm3_rest 8
	pm3_note Db4, 8
	pm3_note E_4, 8
	pm3_connect_note_set
	pm3_note Ab4, 8
	pm3_connect_note_set
	pm3_note Ab4, 16
	pm3_note Gb4, 8
	pm3_note E_4, 8
	pm3_rest 8
	pm3_note Eb4, 8
	pm3_rest 8
	pm3_connect_note_set
	pm3_note E_4, 8
	pm3_connect_note_set
	pm3_note E_4, 8
	pm3_note Eb4, 8
	pm3_note Db4, 8
	pm3_rest 8
	pm3_note Db4, 8
	pm3_rest 8
	pm3_octave_jump
	pm3_note B_3, 8
	pm3_rest 8
	pm3_note B_3, 8
	pm3_note Db4, 8
	pm3_rest 8
	pm3_connect_note_set
	pm3_note Db4, 32
	pm3_connect_note_set
	pm3_note Db4, 8

music_title_pulse_1_loop_4:
	pm3_channel_flags no_channel_flags_set
	pm3_note Db4, 8
	pm3_note E_4, 8
	pm3_note Gb4, 8
	pm3_note Db4, 8
	pm3_octave_jump
	pm3_note B_4, 8
	pm3_note Db4, 8
	pm3_note A_4, 8
	pm3_note Db4, 8
	pm3_note Ab4, 8
	pm3_note Db4, 8
	pm3_note Gb4, 8
	pm3_note Db4, 8
	pm3_note E_4, 8
	pm3_break_1 channel_octave_jump_set, music_title_pulse_1_break_2
	pm3_note Gb4, 8
	pm3_rest 8
	pm3_connect_note_set
	pm3_note Ab4, 8
	pm3_connect_note_set
	pm3_note Ab4, 8
	pm3_note E_4, 8
	pm3_note Db4, 8
	pm3_octave_jump
	pm3_note B_3, 8
	pm3_note Db4, 8
	pm3_note E_4, 8
	pm3_rest 8
	pm3_octave_jump
	pm3_note Ab4, 8
	pm3_note E_4, 8
	pm3_note Db4, 8
	pm3_octave_jump
	pm3_note B_3, 8
	pm3_note Db4, 8
	pm3_rest 8
	pm3_note Db4, 8
	pm3_rest 8
	pm3_connect_note_set
	pm3_note Db4, 8
	pm3_loop_1 1, music_title_pulse_1_loop_4

music_title_pulse_1_break_2:
	current_octave_jump .SET 1
	pm3_connect_note_set
	pm3_note Gb4, 8
	pm3_connect_note_set
	pm3_note Gb4, 16
	pm3_note Ab4, 8
	pm3_note Ab4, 8
	pm3_note Gb4, 8
	pm3_note Ab4, 8
	pm3_rest 8
	pm3_note Ab4, 8
	pm3_note Gb4, 8
	pm3_note Ab4, 8
	pm3_note Db5, 8
	pm3_note Db5, 8
	pm3_note B_4, 8
	pm3_note Db5, 8
	pm3_rest 8
	pm3_note B_4, 8
	pm3_note Db5, 8
	pm3_rest 8
	pm3_music_jump music_title_pulse_1_main
	pm3_music_end

music_title_pulse_2:
	current_octave_jump .SET 0
	current_octave .SET 0
	current_channel_transpose .SET 0
	pm3_note_ads $C8
	pm3_volume 10
	pm3_duty_cycle 1
	pm3_instrument 32
	pm3_octave 1
	pm3_octave_jump
	pm3_note A_3, 8
	pm3_rest 8
	pm3_rest 4
	pm3_note Gb3, 4
	pm3_note Db4, 4
	pm3_note Gb3, 4
	pm3_note A_3, 1
	pm3_dotted_note_set
	pm3_connect_note_set
	pm3_note Ab3, 2
	pm3_connect_note_set
	pm3_note Ab3, 4
	pm3_rest 8
	pm3_triplet_note_set
	pm3_note A_3, 8
	pm3_note Gb3, 8
	pm3_note E_3, 8
	pm3_triplet_note_set
	pm3_note Eb3, 16
	pm3_note Eb3, 4
	pm3_note E_3, 4
	pm3_note Gb3, 4
	pm3_note A_3, 16
	pm3_rest 4
	pm3_note Ab3, 16
	pm3_octave_jump
	pm3_note Gb2, 8
	pm3_note Db3, 8
	pm3_note A_2, 8
	pm3_note B_2, 8
	pm3_note Gb2, 8
	pm3_note Db3, 8
	pm3_note A_2, 8
	pm3_note B_2, 8
	pm3_dotted_note_set
	pm3_note D_2, 32
	pm3_instrument 0
	pm3_octave_jump
	pm3_note D_4, 4
	pm3_dotted_note_set
	pm3_note D_4, 8
	pm3_volume 8
	pm3_instrument 19
	pm3_note Gb3, 32
	pm3_note A_3, 32
	pm3_note Db4, 32
	pm3_note E_3, 16
	pm3_note F_3, 16
	pm3_note Gb3, 32
	pm3_note A_3, 32
	pm3_note Db4, 64
	pm3_channel_flags no_channel_flags_set
	pm3_duty_cycle 2
	pm3_instrument 22
	pm3_octave 1

music_title_pulse_2_loop_1:
	pm3_channel_flags no_channel_flags_set
	pm3_note Gb3, 4
	pm3_note Gb3, 4
	pm3_note Gb3, 4
	pm3_note Gb3, 4
	pm3_rest 4
	pm3_note Gb3, 4
	pm3_rest 4
	pm3_note Gb3, 4
	pm3_rest 4
	pm3_note Gb3, 4
	pm3_rest 4
	pm3_note Gb3, 4
	pm3_note Gb3, 4
	pm3_rest 4
	pm3_note Gb3, 4
	pm3_rest 4
	pm3_loop_1 1, music_title_pulse_2_loop_1
	pm3_note Gb3, 4
	pm3_note D_3, 4
	pm3_note E_3, 4
	pm3_note Gb3, 4
	pm3_octave_jump
	pm3_note Ab3, 4
	pm3_note E_3, 4
	pm3_note Gb3, 4
	pm3_note Ab3, 4
	pm3_note A_3, 4
	pm3_note Gb3, 4
	pm3_note Ab3, 4
	pm3_note A_3, 4
	pm3_note Db4, 4
	pm3_note B_3, 4
	pm3_note A_3, 4
	pm3_note Ab3, 4
	pm3_volume 12
	pm3_instrument 17
	pm3_note Db3, 16
	pm3_note F_3, 16
	pm3_note Ab3, 16
	pm3_note Db4, 16

music_title_pulse_2_main:
	pm3_channel_flags no_channel_flags_set
	pm3_dotted_note_set
	pm3_rest 4

music_title_pulse_2_loop_2:
	pm3_channel_flags no_channel_flags_set
	pm3_duty_cycle 1
	pm3_instrument 28
	pm3_volume 10
	pm3_octave 2
	pm3_tempo $02, $2E
	pm3_note Gb3, 8
	pm3_note B_3, 8
	pm3_note Db4, 8
	pm3_note Gb3, 8
	pm3_note E_4, 8
	pm3_note Gb3, 8
	pm3_note Eb4, 8
	pm3_note Gb3, 8
	pm3_note B_3, 8
	pm3_note E_4, 8
	pm3_note Gb3, 8
	pm3_note Eb4, 8
	pm3_note Gb3, 8
	pm3_note Db4, 8
	pm3_break_1 no_channel_flags_set, music_title_pulse_2_break_1
	pm3_note Gb3, 8
	pm3_note B_3, 8
	pm3_loop_1 1, music_title_pulse_2_loop_2

music_title_pulse_2_break_1:
	current_octave_jump .SET 0
	pm3_note E_4, 8
	pm3_rest 2
	pm3_duty_cycle 2
	pm3_volume 14
	pm3_instrument 9
	pm3_octave 1

music_title_pulse_2_loop_3:
	pm3_channel_flags no_channel_flags_set
	pm3_note E_3, 8
	pm3_note A_2, 8
	pm3_note Db3, 8
	pm3_note A_2, 8
	pm3_loop_1 3, music_title_pulse_2_loop_3
	pm3_note Gb3, 8
	pm3_note Db3, 8
	pm3_note E_3, 8
	pm3_note Db3, 8
	pm3_note Gb3, 8
	pm3_note Db3, 8
	pm3_note E_3, 8
	pm3_note Db3, 8
	pm3_note Gb3, 8
	pm3_note Db3, 8
	pm3_octave_jump
	pm3_note Ab3, 8
	pm3_note Db3, 8
	pm3_note Gb3, 8
	pm3_note Db3, 8
	pm3_note E_3, 8
	pm3_note Db3, 8
	pm3_volume 10
	pm3_instrument 19
	pm3_connect_note_set
	pm3_note Db4, 32
	pm3_instrument 5
	pm3_connect_note_set
	pm3_note Db4, 32
	pm3_instrument 19
	pm3_connect_note_set
	pm3_note B_3, 32
	pm3_instrument 5
	pm3_connect_note_set
	pm3_note B_3, 32
	pm3_instrument 19
	pm3_connect_note_set
	pm3_note E_4, 32
	pm3_instrument 5
	pm3_connect_note_set
	pm3_note E_4, 32
	pm3_instrument 19
	pm3_note Eb4, 32
	pm3_note B_3, 32
	pm3_connect_note_set
	pm3_note Ab3, 32
	pm3_instrument 5
	pm3_connect_note_set
	pm3_note Ab3, 32
	pm3_instrument 19
	pm3_connect_note_set
	pm3_note Gb3, 32
	pm3_instrument 5
	pm3_connect_note_set
	pm3_note Gb3, 32
	pm3_instrument 19
	pm3_connect_note_set
	pm3_note Db3, 32
	pm3_instrument 5
	pm3_note Db3, 32
	pm3_connect_note_set
	pm3_note Db3, 64
	pm3_music_jump music_title_pulse_2_main
	pm3_music_end

music_title_triangle:
	current_octave_jump .SET 0
	current_octave .SET 0
	current_channel_transpose .SET 0
	pm3_note_ads $FF
	pm3_instrument 2
	pm3_octave 2
	pm3_note Gb3, 32
	pm3_dotted_note_set
	pm3_note E_3, 16
	pm3_note E_3, 4
	pm3_note Gb3, 4
	pm3_connect_note_set
	pm3_note B_2, 16
	pm3_connect_note_set
	pm3_note B_2, 4
	pm3_note Db3, 4
	pm3_rest 4
	pm3_note D_3, 32
	pm3_note F_3, 4
	pm3_note Gb3, 32
	pm3_note E_3, 32
	pm3_dotted_note_set
	pm3_note D_3, 32
	pm3_note D_3, 4
	pm3_dotted_note_set
	pm3_note E_3, 8
	pm3_note Gb3, 32
	pm3_dotted_note_set
	pm3_note E_3, 16
	pm3_note E_3, 4
	pm3_note Gb3, 4
	pm3_dotted_note_set
	pm3_note B_2, 16
	pm3_rest 4
	pm3_note C_3, 4
	pm3_note Db3, 32
	pm3_dotted_note_set
	pm3_note Gb3, 16
	pm3_note Gb3, 4
	pm3_note F_3, 4
	pm3_dotted_note_set
	pm3_note E_3, 16
	pm3_note E_3, 4
	pm3_note Eb3, 4
	pm3_note D_3, 32
	pm3_note Db4, 32
	pm3_octave 3
	pm3_note_ads $C8
	pm3_note D_3, 4
	pm3_note D_3, 4
	pm3_note D_3, 4
	pm3_note D_3, 4
	pm3_rest 4
	pm3_note D_3, 4
	pm3_rest 4
	pm3_note D_3, 4
	pm3_rest 4
	pm3_note D_3, 4
	pm3_rest 4
	pm3_note D_3, 4
	pm3_note D_3, 4
	pm3_rest 4
	pm3_note D_3, 4
	pm3_rest 4
	pm3_note E_3, 4
	pm3_note E_3, 4
	pm3_note E_3, 4
	pm3_note E_3, 4
	pm3_rest 4
	pm3_note E_3, 4
	pm3_rest 4
	pm3_note E_3, 4
	pm3_rest 4
	pm3_note E_3, 4
	pm3_rest 4
	pm3_note E_3, 4
	pm3_note E_3, 4
	pm3_rest 4
	pm3_note E_3, 4
	pm3_rest 4
	pm3_note Gb3, 16
	pm3_note Ab3, 16
	pm3_note A_3, 16
	pm3_note B_3, 16
	pm3_note_ads $E6
	pm3_instrument 14
	pm3_note Ab4, 8
	pm3_rest 4
	pm3_note Ab4, 8
	pm3_rest 4
	pm3_note Ab4, 8
	pm3_rest 4
	pm3_note Ab4, 8
	pm3_rest 4
	pm3_note Bb4, 4
	pm3_note Bb4, 4
	pm3_note Bb4, 8

music_title_triangle_main:
	pm3_channel_flags no_channel_flags_set

music_title_triangle_loop_1:
	pm3_channel_flags no_channel_flags_set
	pm3_note_ads $C8
	pm3_instrument 2
	pm3_note Gb3, 4
	pm3_rest 4
	pm3_note Gb3, 4
	pm3_note Gb3, 4
	pm3_note_ads $F0
	pm3_instrument 14
	pm3_note Gb4, 8
	pm3_note_ads $C8
	pm3_instrument 2
	pm3_note Gb3, 4
	pm3_note Gb3, 4
	pm3_loop_1 7, music_title_triangle_loop_1

music_title_triangle_loop_2:
	pm3_channel_flags no_channel_flags_set
	pm3_note A_3, 4
	pm3_rest 4
	pm3_note A_3, 4
	pm3_note A_3, 4
	pm3_note_ads $F0
	pm3_instrument 14
	pm3_note Gb4, 8
	pm3_instrument 2
	pm3_note_ads $C8
	pm3_note A_3, 4
	pm3_note A_3, 4
	pm3_loop_1 1, music_title_triangle_loop_2

music_title_triangle_loop_3:
	pm3_channel_flags no_channel_flags_set
	pm3_note B_3, 4
	pm3_rest 4
	pm3_note B_3, 4
	pm3_note B_3, 4
	pm3_instrument 14
	pm3_note_ads $F0
	pm3_note Gb4, 8
	pm3_instrument 2
	pm3_note_ads $C8
	pm3_note B_3, 4
	pm3_note B_3, 4
	pm3_loop_1 1, music_title_triangle_loop_3

music_title_triangle_loop_4:
	pm3_channel_flags no_channel_flags_set
	pm3_note Db3, 4
	pm3_rest 4
	pm3_note Db3, 4
	pm3_note Db3, 4
	pm3_instrument 14
	pm3_note_ads $F0
	pm3_note Gb4, 8
	pm3_instrument 2
	pm3_note_ads $C8
	pm3_note Db3, 4
	pm3_note Db3, 4
	pm3_loop_1 2, music_title_triangle_loop_4
	pm3_instrument 14
	pm3_note_ads $E6
	pm3_note Bb4, 4
	pm3_note Bb4, 4
	pm3_note F_4, 8
	pm3_note Bb4, 4
	pm3_note Bb4, 4
	pm3_note F_4, 8

music_title_triangle_loop_5:
	pm3_channel_flags no_channel_flags_set
	pm3_instrument 2
	pm3_note_ads $C8
	pm3_note A_3, 4
	pm3_rest 4
	pm3_note A_3, 4
	pm3_note A_3, 4
	pm3_instrument 14
	pm3_note_ads $F0
	pm3_note Gb4, 8
	pm3_instrument 2
	pm3_note_ads $C8
	pm3_note A_3, 4
	pm3_note A_3, 4
	pm3_loop_1 1, music_title_triangle_loop_5

music_title_triangle_loop_6:
	pm3_channel_flags no_channel_flags_set
	pm3_note B_3, 4
	pm3_rest 4
	pm3_note B_3, 4
	pm3_note B_3, 4
	pm3_instrument 14
	pm3_note_ads $F0
	pm3_note Gb4, 8
	pm3_instrument 2
	pm3_note_ads $C8
	pm3_note B_3, 4
	pm3_note B_3, 4
	pm3_loop_1 1, music_title_triangle_loop_6

music_title_triangle_loop_7:
	pm3_channel_flags no_channel_flags_set
	pm3_note Db4, 4
	pm3_rest 4
	pm3_note Db4, 4
	pm3_note Db4, 4
	pm3_instrument 14
	pm3_note_ads $F0
	pm3_note Gb4, 8
	pm3_instrument 2
	pm3_note_ads $C8
	pm3_note Db4, 4
	pm3_note Db4, 4
	pm3_loop_1 2, music_title_triangle_loop_7
	pm3_note B_3, 4
	pm3_rest 4
	pm3_note B_3, 4
	pm3_note B_3, 4
	pm3_instrument 14
	pm3_note_ads $F0
	pm3_note Gb4, 8
	pm3_instrument 2
	pm3_note_ads $C8
	pm3_note B_3, 4
	pm3_note B_3, 4

music_title_triangle_loop_8:
	pm3_channel_flags no_channel_flags_set
	pm3_note A_3, 4
	pm3_rest 4
	pm3_note A_3, 4
	pm3_note A_3, 4
	pm3_instrument 14
	pm3_note_ads $F0
	pm3_note Gb4, 8
	pm3_instrument 2
	pm3_note_ads $F0
	pm3_note A_3, 4
	pm3_note A_3, 4
	pm3_loop_1 1, music_title_triangle_loop_8

music_title_triangle_loop_9:
	pm3_channel_flags no_channel_flags_set
	pm3_note B_3, 4
	pm3_rest 4
	pm3_note B_3, 4
	pm3_note B_3, 4
	pm3_instrument 14
	pm3_note_ads $F0
	pm3_note Gb4, 8
	pm3_instrument 2
	pm3_note_ads $C8
	pm3_note B_3, 4
	pm3_note B_3, 4
	pm3_loop_1 1, music_title_triangle_loop_9

music_title_triangle_loop_10:
	pm3_channel_flags no_channel_flags_set
	pm3_note Db3, 4
	pm3_rest 4
	pm3_note Db3, 4
	pm3_note Db3, 4
	pm3_instrument 14
	pm3_note_ads $F0
	pm3_note Gb4, 8
	pm3_instrument 2
	pm3_note_ads $C8
	pm3_note Db3, 4
	pm3_note Db3, 4
	pm3_loop_1 2, music_title_triangle_loop_10
	pm3_instrument 14
	pm3_note_ads $F0
	pm3_rest 4
	pm3_note Bb4, 8
	pm3_rest 4
	pm3_note Bb4, 8
	pm3_note Bb4, 4
	pm3_note Bb4, 4
	pm3_music_jump music_title_triangle_main
	pm3_music_end

music_title_noise:
	pm3_note_ads $C8
	pm3_instrument 12
	pm3_volume 12

music_title_noise_loop_1:
	pm3_channel_flags no_channel_flags_set
	pm3_rest 64
	pm3_loop_1 7, music_title_noise_loop_1

music_title_noise_loop_2:
	pm3_channel_flags no_channel_flags_set
	pm3_noise_note 7, 4
	pm3_noise_note 7, 4
	pm3_noise_note 7, 4
	pm3_noise_note 7, 4
	pm3_rest 4
	pm3_noise_note 7, 4
	pm3_rest 4
	pm3_noise_note 7, 4
	pm3_rest 4
	pm3_noise_note 7, 4
	pm3_rest 4
	pm3_noise_note 7, 4
	pm3_noise_note 7, 4
	pm3_rest 4
	pm3_noise_note 7, 4
	pm3_rest 4
	pm3_loop_1 1, music_title_noise_loop_2
	pm3_noise_note 10, 16
	pm3_noise_note 10, 16
	pm3_noise_note 10, 16
	pm3_noise_note 10, 16

music_title_noise_loop_3:
	pm3_channel_flags no_channel_flags_set
	pm3_noise_note 11, 4
	pm3_noise_note 7, 4
	pm3_noise_note 4, 4
	pm3_loop_1 3, music_title_noise_loop_3
	pm3_noise_note 11, 4
	pm3_noise_note 7, 4
	pm3_noise_note 4, 4
	pm3_noise_note 7, 4

music_title_noise_main:
	pm3_channel_flags no_channel_flags_set

music_title_noise_loop_4:
	pm3_channel_flags no_channel_flags_set
	pm3_noise_note 2, 4
	pm3_rest 4
	pm3_noise_note 14, 4
	pm3_noise_note 14, 4
	pm3_noise_note 7, 4
	pm3_rest 4
	pm3_noise_note 14, 4
	pm3_noise_note 14, 4
	pm3_loop_1 30, music_title_noise_loop_4
	pm3_noise_note 2, 4
	pm3_noise_note 7, 4
	pm3_noise_note 11, 4
	pm3_noise_note 9, 4
	pm3_noise_note 7, 4
	pm3_noise_note 11, 4
	pm3_noise_note 9, 4
	pm3_noise_note 7, 4
	pm3_music_jump music_title_noise_main
	pm3_music_end

sfx_landing:
	pm3_sfx_priority 6

;1
	current_sfx_global_transpose .SET 0
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $6F
	pm3_sfx_frames 3
	.BYTE sfx_pulse_2 | sfx_noise

;sfx_pulse_2
	pm3_sfx_channel_flags sfx_instruments_set | sfx_duty_cycle_set | sfx_volume_set | sfx_pitch_slide_set | sfx_pitch_tune_set
	pm3_sfx_instruments 53
	pm3_sfx_duty_cycle 1
	pm3_sfx_volume 15
	pm3_sfx_pitch_slide $90
	pm3_sfx_pitch_tune $08
	pm3_sfx_note E_5

;sfx_noise
	pm3_sfx_channel_flags sfx_instruments_set | sfx_volume_set | sfx_pitch_slide_set | sfx_pitch_tune_set
	pm3_sfx_instruments 49
	pm3_sfx_volume 15
	pm3_sfx_pitch_slide $2A
	pm3_sfx_pitch_tune $7F
	pm3_sfx_noise_note 15

;2
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $82
	pm3_sfx_frames 2
	.BYTE sfx_pulse_2 | sfx_noise

;sfx_pulse_2
	pm3_sfx_channel_flags no_channel_flags_set
	pm3_sfx_note E_5

;sfx_noise
	pm3_sfx_channel_flags no_channel_flags_set
	pm3_sfx_noise_note 15
	pm3_sfx_end

sfx_1up:
	pm3_sfx_priority 20

;1
	current_sfx_global_transpose .SET 0
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 3
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags sfx_instruments_set | sfx_duty_cycle_set | sfx_volume_set
	pm3_sfx_instruments 40
	pm3_sfx_duty_cycle 3
	pm3_sfx_volume 15
	pm3_sfx_note Db5

;2
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 3
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags no_channel_flags_set
	pm3_sfx_note Eb5

;3
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 3
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags no_channel_flags_set
	pm3_sfx_note F_5

;4
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 3
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags no_channel_flags_set
	pm3_sfx_note Gb5

;5
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 3
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags no_channel_flags_set
	pm3_sfx_note Ab5

;6
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 3
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags no_channel_flags_set
	pm3_sfx_note Bb5

;7
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 3
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags no_channel_flags_set
	pm3_sfx_note C_6

;8
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 3
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags no_channel_flags_set
	pm3_sfx_note Db6

;9
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 3
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags sfx_volume_set
	pm3_sfx_volume 8
	pm3_sfx_note Db5

;10
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 3
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags no_channel_flags_set
	pm3_sfx_note Eb5

;11
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 3
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags no_channel_flags_set
	pm3_sfx_note F_5

;12
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 3
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags no_channel_flags_set
	pm3_sfx_note Gb5

;13
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 3
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags no_channel_flags_set
	pm3_sfx_note Ab5

;14
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 3
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags no_channel_flags_set
	pm3_sfx_note Bb5

;15
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 3
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags no_channel_flags_set
	pm3_sfx_note C_6

;16
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 3
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags no_channel_flags_set
	pm3_sfx_note Db6
	pm3_sfx_end

sfx_mega_buster:
	pm3_sfx_priority 7

;1
	current_sfx_global_transpose .SET 0
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $EB
	pm3_sfx_frames 10
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags sfx_instruments_set | sfx_duty_cycle_set | sfx_volume_set | sfx_pitch_slide_set
	pm3_sfx_instruments 54
	pm3_sfx_duty_cycle 1
	pm3_sfx_volume 15
	pm3_sfx_pitch_slide $FF
	pm3_sfx_note D_4
	pm3_sfx_end

sfx_megaman_hit:
	pm3_sfx_priority 16

;1
	current_sfx_global_transpose .SET 0
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $6F
	pm3_sfx_frames 3
	.BYTE sfx_pulse_2 | sfx_noise

;sfx_pulse_2
	pm3_sfx_channel_flags sfx_instruments_set | sfx_duty_cycle_set | sfx_volume_set | sfx_pitch_slide_set
	pm3_sfx_instruments 44
	pm3_sfx_duty_cycle 3
	pm3_sfx_volume 15
	pm3_sfx_pitch_slide $40
	pm3_sfx_note G_1

;sfx_noise
	pm3_sfx_channel_flags sfx_instruments_set | sfx_volume_set | sfx_pitch_slide_set
	pm3_sfx_instruments 45
	pm3_sfx_volume 15
	pm3_sfx_pitch_slide $7F
	pm3_sfx_noise_note 5

;2
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 11
	.BYTE sfx_pulse_2 | sfx_noise

;sfx_pulse_2
	pm3_sfx_channel_flags sfx_instruments_set | sfx_volume_set | sfx_pitch_slide_set
	pm3_sfx_instruments 47
	pm3_sfx_volume 8
	pm3_sfx_pitch_slide $7F
	pm3_sfx_note B_3

;sfx_noise
	pm3_sfx_channel_flags sfx_instruments_set | sfx_pitch_slide_set
	pm3_sfx_instruments 46
	pm3_sfx_pitch_slide $FF
	pm3_sfx_noise_note 6
	pm3_sfx_end

sfx_death:
	pm3_sfx_priority 21

;1
	current_sfx_global_transpose .SET 0
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 14
	.BYTE sfx_pulse_1 | sfx_pulse_2

;sfx_pulse_1
	pm3_sfx_channel_flags sfx_instruments_set | sfx_duty_cycle_set | sfx_volume_set | sfx_pitch_slide_set
	pm3_sfx_instruments 42
	pm3_sfx_duty_cycle 2
	pm3_sfx_volume 15
	pm3_sfx_pitch_slide $7F
	pm3_sfx_note Db5

;sfx_pulse_2
	pm3_sfx_channel_flags sfx_instruments_set | sfx_duty_cycle_set | sfx_volume_set | sfx_pitch_slide_set
	pm3_sfx_instruments 42
	pm3_sfx_duty_cycle 1
	pm3_sfx_volume 15
	pm3_sfx_pitch_slide $7F
	pm3_sfx_note Db5

;2
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 14
	.BYTE sfx_pulse_1 | sfx_pulse_2

;sfx_pulse_1
	pm3_sfx_channel_flags sfx_volume_set
	pm3_sfx_volume 12
	pm3_sfx_note Db5

;sfx_pulse_2
	pm3_sfx_channel_flags sfx_volume_set
	pm3_sfx_volume 12
	pm3_sfx_note Db5

;3
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 14
	.BYTE sfx_pulse_1 | sfx_pulse_2

;sfx_pulse_1
	pm3_sfx_channel_flags sfx_volume_set
	pm3_sfx_volume 9
	pm3_sfx_note Db5

;sfx_pulse_2
	pm3_sfx_channel_flags sfx_volume_set
	pm3_sfx_volume 9
	pm3_sfx_note Db5

;4
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 14
	.BYTE sfx_pulse_1 | sfx_pulse_2

;sfx_pulse_1
	pm3_sfx_channel_flags sfx_volume_set
	pm3_sfx_volume 6
	pm3_sfx_note Db5

;sfx_pulse_2
	pm3_sfx_channel_flags sfx_volume_set
	pm3_sfx_volume 6
	pm3_sfx_note Db5

;5
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 14
	.BYTE sfx_pulse_1 | sfx_pulse_2

;sfx_pulse_1
	pm3_sfx_channel_flags sfx_volume_set
	pm3_sfx_volume 3
	pm3_sfx_note Db5

;sfx_pulse_2
	pm3_sfx_channel_flags sfx_volume_set
	pm3_sfx_volume 3
	pm3_sfx_note Db5

;6
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 14
	.BYTE sfx_pulse_1 | sfx_pulse_2

;sfx_pulse_1
	pm3_sfx_channel_flags sfx_volume_set
	pm3_sfx_volume 1
	pm3_sfx_note Db5

;sfx_pulse_2
	pm3_sfx_channel_flags sfx_volume_set
	pm3_sfx_volume 1
	pm3_sfx_note Db5
	pm3_sfx_end

sfx_enemy_hit:
	pm3_sfx_priority 9

;1
	current_sfx_global_transpose .SET 0
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $C8
	pm3_sfx_frames 28
	.BYTE sfx_noise

;sfx_noise
	pm3_sfx_channel_flags sfx_instruments_set | sfx_volume_set | sfx_pitch_slide_set
	pm3_sfx_instruments 50
	pm3_sfx_volume 15
	pm3_sfx_pitch_slide $FF
	pm3_sfx_noise_note 13
	pm3_sfx_end

sfx_enemy_immune:
	pm3_sfx_priority 9

;1
	current_sfx_global_transpose .SET 0
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 4
	.BYTE sfx_pulse_2 | sfx_triangle

;sfx_pulse_2
	pm3_sfx_channel_flags sfx_instruments_set | sfx_duty_cycle_set | sfx_volume_set
	pm3_sfx_instruments 40
	pm3_sfx_duty_cycle 0
	pm3_sfx_volume 15
	pm3_sfx_note A_6

;sfx_triangle
	pm3_sfx_channel_flags sfx_instruments_set | sfx_triangle_note_length_set | sfx_pitch_slide_set
	pm3_sfx_instruments 40
	pm3_sfx_triangle_note_length $AF
	pm3_sfx_pitch_slide $00
	pm3_sfx_note A_7
	pm3_sfx_end

sfx_select:
	pm3_sfx_priority 2

;1
	current_sfx_global_transpose .SET 0
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 5
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags sfx_instruments_set | sfx_duty_cycle_set | sfx_volume_set
	pm3_sfx_instruments 40
	pm3_sfx_duty_cycle 3
	pm3_sfx_volume 15
	pm3_sfx_note Ab4

;2
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 8
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags sfx_duty_cycle_set
	pm3_sfx_duty_cycle 1
	pm3_sfx_note Db4
	pm3_sfx_end

sfx_door:
	pm3_sfx_priority 8

;1
	current_sfx_global_transpose .SET 0

sfx_door_loop_1:
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 2
	.BYTE sfx_pulse_2 | sfx_noise

;sfx_pulse_2
	pm3_sfx_channel_flags sfx_instruments_set | sfx_duty_cycle_set | sfx_volume_set | sfx_pitch_slide_set
	pm3_sfx_instruments 44
	pm3_sfx_duty_cycle 2
	pm3_sfx_volume 15
	pm3_sfx_pitch_slide $6E
	pm3_sfx_note E_7

;sfx_noise
	pm3_sfx_channel_flags sfx_instruments_set | sfx_volume_set | sfx_pitch_slide_set
	pm3_sfx_instruments 60
	pm3_sfx_volume 15
	pm3_sfx_pitch_slide $4A
	pm3_sfx_noise_note 8

;2
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 4
	.BYTE 0

;3
	pm3_sfx_global_channel_flags sfx_loop_set | sfx_ads_set
	pm3_sfx_loop 2, sfx_door_loop_1
	pm3_sfx_ads $FF
	pm3_sfx_frames 2
	.BYTE sfx_pulse_2 | sfx_noise

;sfx_pulse_2
	pm3_sfx_channel_flags sfx_instruments_set | sfx_duty_cycle_set | sfx_volume_set | sfx_pitch_slide_set
	pm3_sfx_instruments 44
	pm3_sfx_duty_cycle 2
	pm3_sfx_volume 15
	pm3_sfx_pitch_slide $6E
	pm3_sfx_note E_7

;sfx_noise
	pm3_sfx_channel_flags sfx_instruments_set | sfx_volume_set | sfx_pitch_slide_set
	pm3_sfx_instruments 60
	pm3_sfx_volume 15
	pm3_sfx_pitch_slide $4A
	pm3_sfx_noise_note 8
	pm3_sfx_end

sfx_teleport_out:
	pm3_sfx_priority 1

;1
	current_sfx_global_transpose .SET 0
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 6
	.BYTE sfx_pulse_2 | sfx_noise

;sfx_pulse_2
	pm3_sfx_channel_flags sfx_instruments_set | sfx_duty_cycle_set | sfx_volume_set | sfx_pitch_slide_set
	pm3_sfx_instruments 57
	pm3_sfx_duty_cycle 3
	pm3_sfx_volume 15
	pm3_sfx_pitch_slide $FF
	pm3_sfx_note Eb5

;sfx_noise
	pm3_sfx_channel_flags sfx_instruments_set | sfx_volume_set | sfx_pitch_slide_set
	pm3_sfx_instruments 57
	pm3_sfx_volume 6
	pm3_sfx_pitch_slide $7F
	pm3_sfx_noise_note 15

;2
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 1
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags no_channel_flags_set 
	pm3_sfx_note B_5
	pm3_sfx_end

sfx_refill:
	pm3_sfx_priority 9

;1
	current_sfx_global_transpose .SET 0

sfx_refill_loop_1:
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 4
	.BYTE sfx_pulse_1 | sfx_pulse_2

;sfx_pulse_1
	pm3_sfx_channel_flags sfx_instruments_set | sfx_duty_cycle_set | sfx_volume_set
	pm3_sfx_instruments 41
	pm3_sfx_duty_cycle 1
	pm3_sfx_volume 15
	pm3_sfx_note C_5

;sfx_pulse_2
	pm3_sfx_channel_flags sfx_instruments_set | sfx_duty_cycle_set | sfx_volume_set
	pm3_sfx_instruments 41
	pm3_sfx_duty_cycle 1
	pm3_sfx_volume 15
	pm3_sfx_note E_5

;2
	pm3_sfx_global_channel_flags sfx_loop_set
	pm3_sfx_loop 2, sfx_refill_loop_1
	pm3_sfx_frames 0
	.BYTE 0
	pm3_sfx_end

sfx_charge_shot_charging:
	pm3_sfx_priority 7

;1
	current_sfx_global_transpose .SET 0
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 8
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags sfx_instruments_set | sfx_duty_cycle_set | sfx_volume_set | sfx_pitch_slide_set | sfx_pitch_tune_set
	pm3_sfx_instruments 62
	pm3_sfx_duty_cycle 1
	pm3_sfx_volume 12
	pm3_sfx_pitch_slide $C8
	pm3_sfx_pitch_tune $00
	pm3_sfx_note B_2

;2
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 7
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags no_channel_flags_set
	pm3_sfx_note C_3

;3
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 7
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags no_channel_flags_set
	pm3_sfx_note Db3

;4
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 7
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags no_channel_flags_set
	pm3_sfx_note D_3

;5
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 7
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags no_channel_flags_set
	pm3_sfx_note Eb3

;6
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 7
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags no_channel_flags_set
	pm3_sfx_note E_3

;7
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 7
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags no_channel_flags_set
	pm3_sfx_note F_3

;8
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 7
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags no_channel_flags_set
	pm3_sfx_note Gb3

;9
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 7
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags sfx_volume_set
	pm3_sfx_volume 10
	pm3_sfx_note G_3



;1
	current_sfx_global_transpose .SET 0
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 12
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags sfx_instruments_set | sfx_duty_cycle_set | sfx_volume_set | sfx_pitch_slide_set
	pm3_sfx_instruments 63
	pm3_sfx_duty_cycle 1
	pm3_sfx_volume 15
	pm3_sfx_pitch_slide $8E
	pm3_sfx_note Ab3
	pm3_sfx_end

sfx_charge_shot_full_charging_2:
	pm3_sfx_priority $87

;1
	current_sfx_global_transpose .SET 0
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 10
	.BYTE sfx_pulse_2

;sfx_pulse_2
	pm3_sfx_channel_flags sfx_instruments_set | sfx_duty_cycle_set | sfx_volume_set | sfx_pitch_slide_set | sfx_pitch_tune_set
	pm3_sfx_instruments 62
	pm3_sfx_duty_cycle 1
	pm3_sfx_volume 10
	pm3_sfx_pitch_slide $0B
	pm3_sfx_pitch_tune $EC
	pm3_sfx_note C_4
	pm3_sfx_end

sfx_full_charge_shot:
	pm3_sfx_priority 8

;1
	current_sfx_global_transpose .SET 0
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 7
	.BYTE sfx_triangle | sfx_noise

;sfx_triangle
	pm3_sfx_channel_flags sfx_instruments_set | sfx_triangle_note_length_set
	pm3_sfx_instruments 54
	pm3_sfx_triangle_note_length $05
	pm3_sfx_note C_2

;sfx_noise
	pm3_sfx_channel_flags sfx_instruments_set | sfx_volume_set | sfx_pitch_slide_set
	pm3_sfx_instruments 54
	pm3_sfx_volume 12
	pm3_sfx_pitch_slide $54
	pm3_sfx_noise_note 9

;2
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 5
	.BYTE sfx_triangle | sfx_noise

;sfx_triangle
	pm3_sfx_channel_flags sfx_instruments_set | sfx_triangle_note_length_set | sfx_pitch_slide_set
	pm3_sfx_instruments 62
	pm3_sfx_triangle_note_length $06
	pm3_sfx_pitch_slide $7F
	pm3_sfx_note D_3

;sfx_noise
	pm3_sfx_channel_flags sfx_instruments_set | sfx_volume_set | sfx_pitch_slide_set
	pm3_sfx_instruments 62
	pm3_sfx_volume 15
	pm3_sfx_pitch_slide $7F
	pm3_sfx_noise_note 14
	pm3_sfx_end

sfx_pharaoh_shot:
	pm3_sfx_priority 7

;1
	current_sfx_global_transpose .SET 0
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 64
	.BYTE sfx_pulse_2 | sfx_noise

;sfx_pulse_2
	pm3_sfx_channel_flags sfx_instruments_set | sfx_duty_cycle_set | sfx_volume_set | sfx_pitch_slide_set
	pm3_sfx_instruments 64
	pm3_sfx_duty_cycle 0
	pm3_sfx_volume 15
	pm3_sfx_pitch_slide $B4
	pm3_sfx_note D_2

;sfx_noise
	pm3_sfx_channel_flags sfx_instruments_set | sfx_volume_set
	pm3_sfx_instruments 64
	pm3_sfx_volume 14
	pm3_sfx_noise_note 12
	pm3_sfx_end

sfx_pharaoh_full_charge_shot:
	pm3_sfx_priority 6

;1
	current_sfx_global_transpose .SET 0
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 47
	.BYTE sfx_noise

;sfx_noise
	pm3_sfx_channel_flags sfx_instruments_set | sfx_volume_set | sfx_pitch_slide_set
	pm3_sfx_instruments 65
	pm3_sfx_volume 15
	pm3_sfx_pitch_slide $9A
	pm3_sfx_noise_note 15
	pm3_sfx_end

sfx_refill_continuous:
	pm3_sfx_priority 9

;1
	current_sfx_global_transpose .SET 0

sfx_refill_continuous_loop_1:
	pm3_sfx_global_channel_flags sfx_ads_set
	pm3_sfx_ads $FF
	pm3_sfx_frames 4
	.BYTE sfx_pulse_1 | sfx_pulse_2

;sfx_pulse_1
	pm3_sfx_channel_flags sfx_instruments_set | sfx_duty_cycle_set | sfx_volume_set
	pm3_sfx_instruments 41
	pm3_sfx_duty_cycle 1
	pm3_sfx_volume 15
	pm3_sfx_note C_5

;sfx_pulse_2
	pm3_sfx_channel_flags sfx_instruments_set | sfx_duty_cycle_set | sfx_volume_set
	pm3_sfx_instruments 41
	pm3_sfx_duty_cycle 1
	pm3_sfx_volume 15
	pm3_sfx_note E_5

;2
	pm3_sfx_global_channel_flags sfx_loop_set
	pm3_sfx_loop 0, sfx_refill_continuous_loop_1
	pm3_sfx_frames 0
	.BYTE 0
	pm3_sfx_end

sfx_metal_blade:
 pm3_sfx_priority 7
 current_sfx_global_transpose .SET 0
 pm3_sfx_global_channel_flags sfx_ads_set
 pm3_sfx_ads $ff
 pm3_sfx_frames 3
 .byte sfx_pulse_2 | sfx_noise
 pm3_sfx_channel_flags sfx_instruments_set | sfx_duty_cycle_set | sfx_volume_set
 pm3_sfx_instruments 41
 pm3_sfx_duty_cycle 0
 pm3_sfx_volume 15
 pm3_sfx_note C_3
 pm3_sfx_channel_flags sfx_instruments_set | sfx_volume_set
 pm3_sfx_instruments 51
 pm3_sfx_volume 15
 pm3_sfx_noise_note 5
 pm3_sfx_global_channel_flags sfx_ads_set
 pm3_sfx_ads $ff
 pm3_sfx_frames 3
 .byte sfx_pulse_2 | sfx_noise
 pm3_sfx_channel_flags sfx_instruments_set | sfx_duty_cycle_set | sfx_volume_set
 pm3_sfx_instruments 41
 pm3_sfx_duty_cycle 0
 pm3_sfx_volume 15
 pm3_sfx_note C_3
 pm3_sfx_channel_flags sfx_instruments_set | sfx_volume_set
 pm3_sfx_instruments 51
 pm3_sfx_volume 15
 pm3_sfx_noise_note 5
 pm3_sfx_global_channel_flags sfx_ads_set
 pm3_sfx_ads $ff
 pm3_sfx_frames 4
 .byte sfx_pulse_2 | sfx_noise
 pm3_sfx_channel_flags sfx_instruments_set | sfx_duty_cycle_set | sfx_volume_set
 pm3_sfx_instruments 41
 pm3_sfx_duty_cycle 3
 pm3_sfx_volume 8
 pm3_sfx_note A_5
 pm3_sfx_channel_flags sfx_instruments_set | sfx_volume_set
 pm3_sfx_instruments 51
 pm3_sfx_volume 15
 pm3_sfx_noise_note 8
 pm3_sfx_global_channel_flags sfx_ads_set
 pm3_sfx_ads $ff
 pm3_sfx_frames 4
 .byte sfx_pulse_2 | sfx_noise
 pm3_sfx_channel_flags sfx_instruments_set | sfx_duty_cycle_set | sfx_volume_set
 pm3_sfx_instruments 41
 pm3_sfx_duty_cycle 3
 pm3_sfx_volume 8
 pm3_sfx_note A_5
 pm3_sfx_channel_flags sfx_instruments_set | sfx_volume_set
 pm3_sfx_instruments 51
 pm3_sfx_volume 11
 pm3_sfx_noise_note 8
 pm3_sfx_global_channel_flags sfx_ads_set
 pm3_sfx_ads $ff
 pm3_sfx_frames 4
 .byte sfx_pulse_2 | sfx_noise
 pm3_sfx_channel_flags sfx_instruments_set | sfx_duty_cycle_set | sfx_volume_set
 pm3_sfx_instruments 41
 pm3_sfx_duty_cycle 3
 pm3_sfx_volume 8
 pm3_sfx_note A_5
 pm3_sfx_channel_flags sfx_instruments_set | sfx_volume_set
 pm3_sfx_instruments 51
 pm3_sfx_volume 7
 pm3_sfx_noise_note 8
 pm3_sfx_global_channel_flags sfx_ads_set
 pm3_sfx_ads $ff
 pm3_sfx_frames 4
 .byte sfx_pulse_2 | sfx_noise
 pm3_sfx_channel_flags sfx_instruments_set | sfx_duty_cycle_set | sfx_volume_set
 pm3_sfx_instruments 41
 pm3_sfx_duty_cycle 3
 pm3_sfx_volume 8
 pm3_sfx_note A_5
 pm3_sfx_channel_flags sfx_instruments_set | sfx_volume_set
 pm3_sfx_instruments 51
 pm3_sfx_volume 3
 pm3_sfx_noise_note 8
 pm3_sfx_end

.if ::MAPPER_MMC5
; MMC5 owns this multiplier only during native audio; current foreground/IRQ
; code has no consumer. Retain native A/V (last set-bit partial product),
; X/C3 and complete final private memory, in addition to the unsigned product.
; Full compiled CPU units and interrupt/hardware ownership checks are required.
.proc _fraction255_mmc5
 lda $c1
 beq Zero
 txa
 pha
 lda $c3
 pha
 lda $c1
 sta $5205
 tay
 lda $c4
 sta $5206
 lda $5205
 sta $c2
 sta $c3
 lda $5206
 sta $c1
 ldx _fractionTrailingZeros,y
 beq PartialReady
Shift:
 lsr a
 ror $c3
 dex
 bne Shift
PartialReady:
 cmp #$80
 bne ClearOverflow
 ldy $c3
 cpy $c4
 bcs ClearOverflow
 bit _fractionOverflowMask
 jmp Restore
ClearOverflow:
 clv
Restore:
 tay
 pla
 sta $c3
 pla
 tax
 tya
 ldy #0
 clc
 rts
Zero:
 ldy #0
 sty $c2
 clc
 rts
_fractionOverflowMask: .byte $40
.endproc
.align $100
_fractionTrailingZeros:
 .byte 0,0,1,0,2,0,1,0,3,0,1,0,2,0,1,0
 .byte 4,0,1,0,2,0,1,0,3,0,1,0,2,0,1,0
 .byte 5,0,1,0,2,0,1,0,3,0,1,0,2,0,1,0
 .byte 4,0,1,0,2,0,1,0,3,0,1,0,2,0,1,0
 .byte 6,0,1,0,2,0,1,0,3,0,1,0,2,0,1,0
 .byte 4,0,1,0,2,0,1,0,3,0,1,0,2,0,1,0
 .byte 5,0,1,0,2,0,1,0,3,0,1,0,2,0,1,0
 .byte 4,0,1,0,2,0,1,0,3,0,1,0,2,0,1,0
 .byte 7,0,1,0,2,0,1,0,3,0,1,0,2,0,1,0
 .byte 4,0,1,0,2,0,1,0,3,0,1,0,2,0,1,0
 .byte 5,0,1,0,2,0,1,0,3,0,1,0,2,0,1,0
 .byte 4,0,1,0,2,0,1,0,3,0,1,0,2,0,1,0
 .byte 6,0,1,0,2,0,1,0,3,0,1,0,2,0,1,0
 .byte 4,0,1,0,2,0,1,0,3,0,1,0,2,0,1,0
 .byte 5,0,1,0,2,0,1,0,3,0,1,0,2,0,1,0
 .byte 4,0,1,0,2,0,1,0,3,0,1,0,2,0,1,0
.endif
music_protoman_whistle:
	pm3_music_header
	.DBYT music_protoman_whistle_pulse_1
	.DBYT music_protoman_whistle_pulse_2
	.DBYT music_protoman_whistle_triangle
	.DBYT music_protoman_whistle_noise

;reset
	.FEATURE FORCE_RANGE
	current_global_transpose .SET 0

music_protoman_whistle_pulse_1:
	current_octave_jump .SET 0
	current_octave .SET 0
	current_channel_transpose .SET 0
	pm3_global_transpose -2
	pm3_tempo $01, $11
	pm3_note_ads $C8
	pm3_volume 12
	pm3_instrument 38
	pm3_duty_cycle 2
	pm3_octave 3
	pm3_triplet_note_set
	pm3_octave_jump
	pm3_note G_5, 8
	pm3_note Bb5, 8

music_protoman_whistle_pulse_1_loop_1:
	pm3_channel_flags channel_octave_jump_set | channel_connect_note_set
	pm3_note Bb5, 1
	pm3_pitch_slide $28
	pm3_note C_6, 1
	pm3_note C_6, 2
	pm3_dotted_note_set
	pm3_note C_6, 8
	pm3_triplet_note_set
	pm3_connect_note_set
	pm3_note C_6, 16
	pm3_note Bb5, 8
	pm3_note D_6, 32
	pm3_pitch_slide $00
	pm3_note G_5, 8
	pm3_note Bb5, 8
	pm3_connect_note_set
	pm3_note Bb5, 1
	pm3_pitch_slide $28
	pm3_note Db6, 1
	pm3_note Db6, 2
	pm3_note Db6, 4
	pm3_connect_note_set
	pm3_note Db6, 8
	pm3_pitch_slide $00
	pm3_note C_6, 16
	pm3_note Bb5, 8
	pm3_note F_5, 8
	pm3_break_1 channel_octave_jump_set | channel_triplet_note_set, music_protoman_whistle_pulse_1_break_1
	pm3_note G_5, 32
	pm3_note G_5, 8
	pm3_note Bb5, 8
	pm3_loop_1 1, music_protoman_whistle_pulse_1_loop_1

music_protoman_whistle_pulse_1_break_1:
	current_octave_jump .SET 1
	pm3_dotted_note_set
	pm3_triplet_note_set
	pm3_note G_5, 32
	pm3_music_end

music_protoman_whistle_pulse_2:
	current_octave_jump .SET 0
	current_octave .SET 0
	current_channel_transpose .SET 0
	pm3_music_end

music_protoman_whistle_triangle:
	current_octave_jump .SET 0
	current_octave .SET 0
	current_channel_transpose .SET 0
	pm3_music_end

music_protoman_whistle_noise:
	pm3_music_end

music_ending:
	pm3_music_header
	.DBYT music_ending_pulse_1
	.DBYT music_ending_pulse_2
	.DBYT music_ending_triangle
	.DBYT music_ending_noise

;reset
	.FEATURE FORCE_RANGE
	current_global_transpose .SET 0

music_ending_pulse_1:
	current_octave_jump .SET 0
	current_octave .SET 0
	current_channel_transpose .SET 0
	pm3_global_transpose -2
	pm3_tempo $01, $11
	pm3_note_ads $C8
	pm3_volume 12
	pm3_instrument 38
	pm3_duty_cycle 2
	pm3_octave 3
	pm3_triplet_note_set
	pm3_octave_jump
	pm3_note G_5, 8
	pm3_note Bb5, 8

music_ending_pulse_1_loop_1:
	pm3_channel_flags channel_octave_jump_set | channel_connect_note_set
	pm3_note Bb5, 1
	pm3_pitch_slide $28
	pm3_note C_6, 1
	pm3_note C_6, 2
	pm3_dotted_note_set
	pm3_note C_6, 8
	pm3_triplet_note_set
	pm3_connect_note_set
	pm3_note C_6, 16
	pm3_note Bb5, 8
	pm3_note D_6, 32
	pm3_pitch_slide $00
	pm3_note G_5, 8
	pm3_note Bb5, 8
	pm3_connect_note_set
	pm3_note Bb5, 1
	pm3_pitch_slide $28
	pm3_note Db6, 1
	pm3_note Db6, 2
	pm3_note Db6, 4
	pm3_connect_note_set
	pm3_note Db6, 8
	pm3_pitch_slide $00
	pm3_note C_6, 16
	pm3_note Bb5, 8
	pm3_note F_5, 8
	pm3_break_1 channel_octave_jump_set | channel_triplet_note_set, music_ending_pulse_1_break_1
	pm3_note G_5, 32
	pm3_note G_5, 8
	pm3_note Bb5, 8
	pm3_loop_1 1, music_ending_pulse_1_loop_1

music_ending_pulse_1_break_1:
	current_octave_jump .SET 1
	pm3_tempo $00, $CC
	pm3_note G_5, 16
	pm3_tempo $00, $88
	pm3_note Bb5, 16
	pm3_tempo $00, $66
	pm3_note C_6, 16

music_ending_pulse_1_loop_2:
	pm3_channel_flags channel_octave_jump_set | channel_connect_note_set
	pm3_note_ads $64
	pm3_instrument 17
	pm3_tempo $01, $11
	pm3_note C_6, 1
	pm3_pitch_slide $28
	pm3_note D_6, 1
	pm3_note D_6, 2
	pm3_dotted_note_set
	pm3_connect_note_set
	pm3_note D_6, 8
	pm3_pitch_slide $00
	pm3_note G_5, 4
	pm3_note Bb5, 4
	pm3_note D_6, 4
	pm3_connect_note_set
	pm3_note Bb5, 1
	pm3_pitch_slide $28
	pm3_note C_6, 1
	pm3_note C_6, 2
	pm3_connect_note_set
	pm3_note C_6, 8
	pm3_pitch_slide $00
	pm3_note Bb5, 8
	pm3_note A_5, 4
	pm3_dotted_note_set
	pm3_note Bb5, 8
	pm3_break_1 channel_octave_jump_set, music_ending_pulse_1_break_2
	pm3_note G_5, 8
	pm3_note G_5, 4
	pm3_note A_5, 8
	pm3_note A_5, 4
	pm3_pitch_slide $28
	pm3_connect_note_set
	pm3_note Ab5, 1
	pm3_note Bb5, 1
	pm3_note Bb5, 2
	pm3_dotted_note_set
	pm3_connect_note_set
	pm3_note Bb5, 8
	pm3_pitch_slide $00
	pm3_note A_5, 8
	pm3_note G_5, 4
	pm3_dotted_note_set
	pm3_note A_5, 8
	pm3_loop_1 1, music_ending_pulse_1_loop_2

music_ending_pulse_1_break_2:
	current_octave_jump .SET 1
	pm3_connect_note_set
	pm3_note C_6, 1
	pm3_pitch_slide $28
	pm3_note D_6, 1
	pm3_note D_6, 2
	pm3_connect_note_set
	pm3_note D_6, 4
	pm3_pitch_slide $00
	pm3_note D_6, 4
	pm3_note C_6, 8
	pm3_connect_note_set
	pm3_note C_6, 4
	pm3_pitch_slide $28
	pm3_connect_note_set
	pm3_note D_6, 16
	pm3_pitch_slide $00
	pm3_octave 2
	pm3_instrument 32
	pm3_note G_4, 4
	pm3_note Bb4, 4
	pm3_note D_5, 4
	pm3_note C_5, 4
	pm3_note Bb4, 4
	pm3_note A_4, 4
	pm3_instrument 17

music_ending_pulse_1_loop_3:
	pm3_channel_flags channel_octave_jump_set | channel_connect_note_set
	pm3_octave 3
	pm3_note C_6, 1
	pm3_pitch_slide $28
	pm3_note D_6, 1
	pm3_note D_6, 2
	pm3_dotted_note_set
	pm3_connect_note_set
	pm3_note D_6, 8
	pm3_pitch_slide $00
	pm3_note G_5, 4
	pm3_note Bb5, 4
	pm3_note D_6, 4
	pm3_connect_note_set
	pm3_note Bb5, 1
	pm3_pitch_slide $28
	pm3_note C_6, 1
	pm3_note C_6, 2
	pm3_connect_note_set
	pm3_note C_6, 8
	pm3_pitch_slide $00
	pm3_note Bb5, 8
	pm3_note A_5, 4
	pm3_dotted_note_set
	pm3_note Bb5, 8
	pm3_break_1 channel_octave_jump_set, music_ending_pulse_1_break_3
	pm3_note G_5, 8
	pm3_note G_5, 4
	pm3_note A_5, 8
	pm3_note A_5, 4
	pm3_pitch_slide $28
	pm3_connect_note_set
	pm3_note Ab5, 1
	pm3_note Bb5, 1
	pm3_note Bb5, 2
	pm3_dotted_note_set
	pm3_connect_note_set
	pm3_note Bb5, 8
	pm3_pitch_slide $00
	pm3_note A_5, 8
	pm3_note G_5, 4
	pm3_dotted_note_set
	pm3_note A_5, 8
	pm3_loop_1 1, music_ending_pulse_1_loop_3

music_ending_pulse_1_break_3:
	current_octave_jump .SET 1
	pm3_octave 2
	pm3_connect_note_set
	pm3_note F_5, 1
	pm3_pitch_slide $28
	pm3_note G_5, 1
	pm3_note G_5, 2
	pm3_connect_note_set
	pm3_note G_5, 4
	pm3_note G_5, 4
	pm3_note A_5, 8
	pm3_note A_5, 4
	pm3_octave 3
	pm3_connect_note_set
	pm3_note Bb5, 32
	pm3_connect_note_set
	pm3_note Bb5, 8
	pm3_pitch_slide $00
	pm3_octave 2
	pm3_instrument 39
	pm3_triplet_note_set
	pm3_note Eb4, 1
	pm3_note G_4, 1
	pm3_note Bb4, 1
	pm3_triplet_note_set
	pm3_connect_note_set
	pm3_note D_5, 2
	pm3_dotted_note_set
	pm3_connect_note_set
	pm3_note D_5, 32
	pm3_dotted_note_set
	pm3_rest 8

music_ending_pulse_1_main:
	pm3_channel_flags no_channel_flags_set
	pm3_instrument 17
	pm3_duty_cycle 2
	pm3_octave 3
	pm3_tempo $01, $11

music_ending_pulse_1_loop_4:
	pm3_channel_flags no_channel_flags_set
	pm3_rest 16
	pm3_rest 4
	pm3_note G_4, 4
	pm3_note Bb4, 4
	pm3_note C_5, 4
	pm3_triplet_note_set
	pm3_note C_5, 2
	pm3_pitch_slide $3C
	pm3_triplet_note_set
	pm3_note Db5, 8
	pm3_dotted_note_set
	pm3_note C_5, 8
	pm3_triplet_note_set
	pm3_octave_jump
	pm3_note F_5, 8
	pm3_note Eb5, 8
	pm3_break_1 channel_octave_jump_set | channel_triplet_note_set, music_ending_pulse_1_break_4
	pm3_pitch_slide $00
	pm3_triplet_note_set
	pm3_note D_5, 16
	pm3_rest 4
	pm3_triplet_note_set
	pm3_note Eb5, 8
	pm3_note F_5, 8
	pm3_triplet_note_set
	pm3_note D_5, 8
	pm3_note Bb4, 4
	pm3_dotted_note_set
	pm3_note Bb4, 8
	pm3_triplet_note_set
	pm3_rest 2
	pm3_triplet_note_set
	pm3_note Bb4, 4
	pm3_note C_5, 4
	pm3_pitch_slide $3C
	pm3_note Db5, 16
	pm3_rest 4
	pm3_triplet_note_set
	pm3_note Eb5, 8
	pm3_note F_5, 8
	pm3_pitch_slide $00
	pm3_triplet_note_set
	pm3_note C_5, 8
	pm3_octave_jump
	pm3_note Ab4, 4
	pm3_dotted_note_set
	pm3_note Ab4, 8
	pm3_triplet_note_set
	pm3_rest 2
	pm3_triplet_note_set
	pm3_note F_4, 4
	pm3_note Ab4, 4
	pm3_note Bb4, 16
	pm3_rest 4
	pm3_note Bb4, 4
	pm3_note C_5, 4
	pm3_note Bb4, 4
	pm3_note A_4, 8
	pm3_note Gb4, 4
	pm3_note D_4, 16
	pm3_rest 4
	pm3_loop_1 1, music_ending_pulse_1_loop_4

music_ending_pulse_1_break_4:
	current_octave_jump .SET 1
	pm3_triplet_note_set
	pm3_note D_5, 16
	pm3_rest 4
	pm3_triplet_note_set
	pm3_note Eb5, 8
	pm3_note F_5, 8
	pm3_pitch_slide $00
	pm3_triplet_note_set
	pm3_note G_5, 8
	pm3_note Eb5, 4
	pm3_dotted_note_set
	pm3_note C_5, 8
	pm3_triplet_note_set
	pm3_rest 2
	pm3_triplet_note_set
	pm3_octave_jump
	pm3_note G_4, 4
	pm3_note A_4, 4
	pm3_note Bb4, 16
	pm3_rest 4
	pm3_note Bb4, 4
	pm3_note C_5, 4
	pm3_note Bb4, 4
	pm3_note A_4, 8
	pm3_note G_4, 8
	pm3_note F_4, 8
	pm3_note A_4, 8
	pm3_dotted_note_set
	pm3_note G_4, 32
	pm3_rest 8
	pm3_note D_5, 4
	pm3_note Eb5, 4

music_ending_pulse_1_loop_5:
	pm3_channel_flags channel_connect_note_set
	pm3_note Eb5, 1
	pm3_pitch_slide $28
	pm3_octave_jump
	pm3_note F_5, 1
	pm3_note F_5, 2
	pm3_connect_note_set
	pm3_note F_5, 4
	pm3_pitch_slide $00
	pm3_note F_5, 4
	pm3_note F_5, 8
	pm3_note F_5, 8
	pm3_dotted_note_set
	pm3_note F_5, 8
	pm3_note Eb5, 8
	pm3_note D_5, 8
	pm3_note C_5, 8
	pm3_octave_jump
	pm3_note A_4, 8
	pm3_note Bb4, 4
	pm3_note A_4, 8
	pm3_note G_4, 8
	pm3_note F_4, 16
	pm3_dotted_note_set
	pm3_rest 8
	pm3_break_1 no_channel_flags_set, music_ending_pulse_1_break_5
	pm3_note D_5, 4
	pm3_note Eb5, 4
	pm3_loop_1 1, music_ending_pulse_1_loop_5

music_ending_pulse_1_break_5:
	current_octave_jump .SET 0
	pm3_octave_jump
	pm3_note F_5, 4
	pm3_note Gb5, 4
	pm3_connect_note_set
	pm3_note Gb5, 1
	pm3_pitch_slide $28
	pm3_note Ab5, 1
	pm3_note Ab5, 2
	pm3_connect_note_set
	pm3_note Ab5, 4
	pm3_pitch_slide $00
	pm3_note Ab5, 4
	pm3_note Ab5, 8
	pm3_note Ab5, 8
	pm3_dotted_note_set
	pm3_note Ab5, 8
	pm3_note Gb5, 8
	pm3_note F_5, 8
	pm3_note Eb5, 8
	pm3_note C_5, 8
	pm3_note Db5, 4
	pm3_note C_5, 8
	pm3_octave_jump
	pm3_note Ab4, 8
	pm3_dotted_note_set
	pm3_note Bb4, 8
	pm3_note Bb4, 8
	pm3_note C_5, 8
	pm3_note Db5, 8
	pm3_note Ab4, 32
	pm3_rest 8
	pm3_connect_note_set
	pm3_octave_jump
	pm3_note Gb5, 1
	pm3_pitch_slide $28
	pm3_note Ab5, 1
	pm3_note Ab5, 2
	pm3_connect_note_set
	pm3_note Ab5, 4
	pm3_pitch_slide $00
	pm3_note Gb5, 8
	pm3_note F_5, 8
	pm3_note Eb5, 16
	pm3_rest 4
	pm3_note Eb5, 4
	pm3_note F_5, 4
	pm3_note Eb5, 4
	pm3_note D_5, 32
	pm3_rest 16
	pm3_rest 4
	pm3_octave_jump
	pm3_note G_4, 4
	pm3_note Bb4, 4
	pm3_note C_5, 4
	pm3_triplet_note_set
	pm3_note C_5, 2
	pm3_pitch_slide $3C
	pm3_triplet_note_set
	pm3_note Db5, 8
	pm3_dotted_note_set
	pm3_note C_5, 8
	pm3_triplet_note_set
	pm3_octave_jump
	pm3_note F_5, 8
	pm3_note Eb5, 8
	pm3_pitch_slide $00
	pm3_triplet_note_set
	pm3_note D_5, 16
	pm3_rest 4
	pm3_triplet_note_set
	pm3_note Eb5, 8
	pm3_note F_5, 8
	pm3_triplet_note_set
	pm3_note G_5, 8
	pm3_note Eb5, 4
	pm3_dotted_note_set
	pm3_note C_5, 8
	pm3_triplet_note_set
	pm3_rest 2
	pm3_triplet_note_set
	pm3_octave_jump
	pm3_note G_4, 4
	pm3_note A_4, 4
	pm3_note Bb4, 16
	pm3_rest 4
	pm3_note Bb4, 4
	pm3_note C_5, 4
	pm3_note Bb4, 4
	pm3_note A_4, 8
	pm3_note G_4, 8
	pm3_note F_4, 8
	pm3_note A_4, 8
	pm3_note G_4, 32
	pm3_octave 1
	pm3_instrument 28
	pm3_octave_jump
	pm3_note D_4, 4
	pm3_note D_4, 4
	pm3_note C_4, 4
	pm3_note D_4, 8
	pm3_octave 2
	pm3_note G_4, 4
	pm3_note Eb5, 4
	pm3_note D_5, 4

music_ending_pulse_1_loop_6:
	pm3_channel_flags channel_octave_jump_set
	pm3_instrument 32
	pm3_note Eb5, 16
	pm3_rest 4
	pm3_instrument 28
	pm3_note G_4, 4
	pm3_note Eb5, 4
	pm3_note D_5, 4
	pm3_instrument 32
	pm3_note Eb5, 16
	pm3_rest 4
	pm3_instrument 28
	pm3_note F_4, 4
	pm3_note Eb5, 4
	pm3_note D_5, 4
	pm3_note F_5, 8
	pm3_note Eb5, 4
	pm3_note Eb5, 8
	pm3_note D_5, 8
	pm3_note C_5, 4
	pm3_note C_5, 4
	pm3_break_1 channel_octave_jump_set, music_ending_pulse_1_break_6
	pm3_note Bb4, 4
	pm3_note C_5, 4
	pm3_note D_5, 8
	pm3_note F_4, 4
	pm3_note Eb5, 4
	pm3_note D_5, 4
	pm3_loop_1 1, music_ending_pulse_1_loop_6

music_ending_pulse_1_break_6:
	current_octave_jump .SET 1
	pm3_note D_5, 4
	pm3_note G_4, 4
	pm3_note F_4, 8
	pm3_instrument 28
	pm3_note Eb4, 4
	pm3_note Eb4, 4
	pm3_note D_4, 4
	pm3_instrument 32
	pm3_note D_4, 16
	pm3_rest 4
	pm3_instrument 28
	pm3_note Eb4, 4
	pm3_note Eb4, 4
	pm3_note D_4, 4
	pm3_instrument 32
	pm3_note D_4, 16
	pm3_rest 4
	pm3_note D_4, 4
	pm3_note G_4, 4
	pm3_note A_4, 4
	pm3_note C_5, 16
	pm3_note Bb4, 8
	pm3_note A_4, 4
	pm3_note Bb4, 16
	pm3_dotted_note_set
	pm3_rest 8
	pm3_note Bb4, 4
	pm3_note C_5, 4
	pm3_note D_5, 16
	pm3_rest 4
	pm3_note Bb4, 4
	pm3_note Bb4, 4
	pm3_note C_5, 4
	pm3_note D_5, 8
	pm3_note C_5, 8
	pm3_note D_5, 8
	pm3_note Eb5, 8
	pm3_note C_5, 8
	pm3_tempo $01, $00
	pm3_note A_4, 8
	pm3_tempo $00, $F0
	pm3_note A_4, 8
	pm3_tempo $00, $DF
	pm3_note F_4, 8
	pm3_tempo $00, $CC
	pm3_note F_4, 8
	pm3_tempo $00, $BD
	pm3_note D_4, 8
	pm3_tempo $00, $88
	pm3_note Eb4, 8
	pm3_tempo $00, $44
	pm3_note F_4, 8
	pm3_music_jump music_ending_pulse_1_main
	pm3_music_end

music_ending_pulse_2:
	current_octave_jump .SET 0
	current_octave .SET 0
	current_channel_transpose .SET 0
	pm3_note_ads $64
	pm3_volume 12
	pm3_instrument 32
	pm3_duty_cycle 2
	pm3_octave 1
	pm3_triplet_note_set
	pm3_rest 16
	pm3_triplet_note_set
	pm3_rest 64
	pm3_rest 64
	pm3_rest 64
	pm3_rest 64

music_ending_pulse_2_loop_1:
	pm3_channel_flags channel_octave_jump_set
	pm3_note G_3, 16
	pm3_rest 4
	pm3_note D_4, 4
	pm3_note Bb3, 4
	pm3_note F_3, 16
	pm3_rest 16
	pm3_rest 4
	pm3_break_1 channel_octave_jump_set, music_ending_pulse_2_break_1
	pm3_note Eb3, 8
	pm3_note Eb3, 4
	pm3_note F_3, 8
	pm3_note F_3, 4
	pm3_dotted_note_set
	pm3_note G_3, 16
	pm3_note Eb3, 4
	pm3_dotted_note_set
	pm3_note F_3, 8
	pm3_loop_1 1, music_ending_pulse_2_loop_1

music_ending_pulse_2_break_1:
	current_octave_jump .SET 1
	pm3_note Bb3, 8
	pm3_note Bb3, 4
	pm3_note A_3, 8
	pm3_note A_3, 4
	pm3_connect_note_set
	pm3_note Bb3, 32
	pm3_connect_note_set
	pm3_note Bb3, 8

music_ending_pulse_2_loop_2:
	pm3_channel_flags channel_octave_jump_set
	pm3_note G_3, 16
	pm3_rest 4
	pm3_note D_4, 4
	pm3_note Bb3, 4
	pm3_note F_3, 16
	pm3_rest 16
	pm3_rest 4
	pm3_break_1 channel_octave_jump_set, music_ending_pulse_2_break_2
	pm3_note Eb3, 8
	pm3_note Eb3, 4
	pm3_note F_3, 8
	pm3_note F_3, 4
	pm3_dotted_note_set
	pm3_note G_3, 16
	pm3_note Eb3, 4
	pm3_dotted_note_set
	pm3_note F_3, 8
	pm3_loop_1 1, music_ending_pulse_2_loop_2

music_ending_pulse_2_break_2:
	current_octave_jump .SET 1
	pm3_note Bb3, 8
	pm3_note Bb3, 4
	pm3_note C_4, 8
	pm3_note C_4, 4
	pm3_connect_note_set
	pm3_note D_4, 32
	pm3_connect_note_set
	pm3_note D_4, 8
	pm3_rest 64

music_ending_pulse_2_main:
	pm3_channel_flags no_channel_flags_set
	pm3_duty_cycle 1

music_ending_pulse_2_loop_3:
	pm3_channel_flags no_channel_flags_set
	pm3_note G_2, 8
	pm3_note Bb2, 8
	pm3_note D_3, 8
	pm3_note Bb2, 8
	pm3_note Gb2, 8
	pm3_note A_2, 8
	pm3_note D_3, 8
	pm3_note A_2, 8
	pm3_note F_2, 8
	pm3_note Ab2, 8
	pm3_note Bb2, 8
	pm3_note D_3, 8
	pm3_break_1 no_channel_flags_set, music_ending_pulse_2_break_3
	pm3_note Eb2, 8
	pm3_note G_2, 8
	pm3_note Bb2, 8
	pm3_note D_3, 8
	pm3_note Eb2, 8
	pm3_note Gb2, 8
	pm3_note Bb2, 8
	pm3_note Db3, 8
	pm3_note Db2, 8
	pm3_note F_2, 8
	pm3_note Ab2, 8
	pm3_note C_3, 8
	pm3_note C_2, 8
	pm3_note Eb2, 8
	pm3_note G_2, 8
	pm3_note Bb2, 8
	pm3_note D_2, 8
	pm3_note Gb2, 8
	pm3_note A_2, 8
	pm3_note Gb2, 8
	pm3_loop_1 1, music_ending_pulse_2_loop_3

music_ending_pulse_2_break_3:
	current_octave_jump .SET 0
	pm3_note E_2, 8
	pm3_note G_2, 8
	pm3_note Bb2, 8
	pm3_note D_3, 8
	pm3_note Eb2, 8
	pm3_note G_2, 8
	pm3_note Bb2, 8
	pm3_note D_3, 8
	pm3_note F_2, 8
	pm3_note A_2, 8
	pm3_note C_3, 8
	pm3_note D_3, 8
	pm3_note G_1, 8
	pm3_note B_1, 8
	pm3_note D_2, 8
	pm3_note G_2, 8
	pm3_note B_2, 8
	pm3_note D_3, 8
	pm3_octave_jump
	pm3_note G_3, 8
	pm3_note B_3, 8

music_ending_pulse_2_loop_4:
	pm3_channel_flags no_channel_flags_set
	pm3_note C_2, 8
	pm3_note Eb2, 8
	pm3_note G_2, 8
	pm3_note Bb2, 8
	pm3_note C_2, 8
	pm3_note F_2, 8
	pm3_note A_2, 8
	pm3_note F_2, 8
	pm3_note Bb1, 8
	pm3_note D_2, 8
	pm3_note F_2, 8
	pm3_note D_2, 8
	pm3_note Bb1, 8
	pm3_note D_2, 8
	pm3_note F_2, 8
	pm3_note D_2, 8
	pm3_loop_1 1, music_ending_pulse_2_loop_4
	pm3_note Eb2, 8
	pm3_note Gb2, 8
	pm3_note Bb2, 8
	pm3_note Db3, 8
	pm3_note Ab1, 8
	pm3_note C_2, 8
	pm3_note Eb2, 8
	pm3_note Gb2, 8
	pm3_note Db2, 8
	pm3_note F_2, 8
	pm3_note Ab2, 8
	pm3_note C_3, 8
	pm3_note E_2, 8
	pm3_note G_2, 8
	pm3_note Bb2, 8
	pm3_note Db3, 8
	pm3_note Eb2, 8
	pm3_note Gb2, 8
	pm3_note Bb2, 8
	pm3_note Db3, 8
	pm3_note Eb2, 8
	pm3_note Gb2, 8
	pm3_note Bb2, 8
	pm3_note Db3, 8
	pm3_note Bb2, 8
	pm3_note Eb3, 8
	pm3_octave_jump
	pm3_note F_3, 8
	pm3_note Eb3, 8
	pm3_note Bb2, 8
	pm3_note D_3, 8
	pm3_note F_3, 8
	pm3_note D_3, 8
	pm3_octave_jump
	pm3_note G_2, 8
	pm3_note Bb2, 8
	pm3_note D_3, 8
	pm3_note Bb2, 8
	pm3_note Gb2, 8
	pm3_note A_2, 8
	pm3_note D_3, 8
	pm3_note A_2, 8
	pm3_note F_2, 8
	pm3_note Ab2, 8
	pm3_note Bb2, 8
	pm3_note D_3, 8
	pm3_note E_2, 8
	pm3_note G_2, 8
	pm3_note Bb2, 8
	pm3_note D_3, 8
	pm3_note Eb2, 8
	pm3_note G_2, 8
	pm3_note Bb2, 8
	pm3_note D_3, 8
	pm3_note F_2, 8
	pm3_note A_2, 8
	pm3_note C_3, 8
	pm3_note D_3, 8
	pm3_note G_1, 8
	pm3_note B_1, 8
	pm3_note D_2, 8
	pm3_note G_2, 8
	pm3_instrument 28
	pm3_octave_jump
	pm3_note G_4, 4
	pm3_note G_4, 4
	pm3_note G_4, 4
	pm3_connect_note_set
	pm3_note G_4, 4
	pm3_connect_note_set
	pm3_note G_4, 16
	pm3_duty_cycle 2

music_ending_pulse_2_loop_5:
	pm3_channel_flags no_channel_flags_set
	pm3_instrument 32
	pm3_note C_2, 4
	pm3_note Eb2, 4
	pm3_note G_2, 4
	pm3_note Bb2, 4
	pm3_note C_3, 4
	pm3_note Eb3, 4
	pm3_octave_jump
	pm3_note G_3, 4
	pm3_note Eb3, 4
	pm3_octave_jump
	pm3_note F_2, 4
	pm3_note A_2, 4
	pm3_note C_3, 4
	pm3_note Eb3, 4
	pm3_octave_jump
	pm3_note F_3, 4
	pm3_note A_3, 4
	pm3_note C_4, 4
	pm3_note A_3, 4
	pm3_octave_jump
	pm3_note Bb1, 4
	pm3_note D_2, 4
	pm3_note F_2, 4
	pm3_note A_2, 4
	pm3_note Bb2, 4
	pm3_note D_3, 4
	pm3_octave_jump
	pm3_note F_3, 4
	pm3_note Bb3, 4
	pm3_note D_4, 4
	pm3_note Bb3, 4
	pm3_note F_3, 4
	pm3_note D_3, 4
	pm3_note Bb2, 4
	pm3_octave_jump
	pm3_note G_2, 4
	pm3_note Eb2, 4
	pm3_note D_2, 4
	pm3_loop_1 1, music_ending_pulse_2_loop_5

music_ending_pulse_2_loop_6:
	pm3_channel_flags no_channel_flags_set
	pm3_note D_2, 4
	pm3_note Gb2, 4
	pm3_note A_2, 4
	pm3_note C_3, 4
	pm3_note Eb3, 4
	pm3_note C_3, 4
	pm3_note A_2, 4
	pm3_note Gb2, 4
	pm3_loop_1 1, music_ending_pulse_2_loop_6
	pm3_note G_2, 4
	pm3_note Bb2, 4
	pm3_note D_3, 4
	pm3_note Bb2, 4
	pm3_note F_2, 4
	pm3_note A_2, 4
	pm3_note C_3, 4
	pm3_note A_2, 4
	pm3_note Eb2, 4
	pm3_note G_2, 4
	pm3_note Bb2, 4
	pm3_note D_3, 4
	pm3_note Eb3, 4
	pm3_octave_jump
	pm3_note G_3, 4
	pm3_note Bb3, 4
	pm3_note D_4, 4
	pm3_duty_cycle 1
	pm3_octave_jump
	pm3_note C_2, 8
	pm3_note Eb2, 8
	pm3_note G_2, 8
	pm3_note Bb2, 8
	pm3_note C_2, 8
	pm3_note Eb2, 8
	pm3_note G_2, 8
	pm3_note Bb2, 8
	pm3_note F_2, 8
	pm3_note A_2, 8
	pm3_note C_3, 8
	pm3_note Eb3, 8
	pm3_note F_2, 8
	pm3_note A_2, 8
	pm3_note C_3, 8
	pm3_note Eb3, 8
	pm3_music_jump music_ending_pulse_2_main
	pm3_music_end

music_ending_triangle:
	current_octave_jump .SET 0
	current_octave .SET 0
	current_channel_transpose .SET 0
	pm3_note_ads $B4
	pm3_instrument 0
	pm3_octave 3
	pm3_triplet_note_set
	pm3_rest 16
	pm3_triplet_note_set
	pm3_rest 64
	pm3_rest 64
	pm3_rest 64
	pm3_rest 64
	pm3_connect_note_set
	pm3_note G_3, 16
	pm3_dotted_note_set
	pm3_connect_note_set
	pm3_note G_3, 8
	pm3_connect_note_set
	pm3_note D_3, 32
	pm3_connect_note_set
	pm3_note D_3, 4
	pm3_dotted_note_set
	pm3_note Eb3, 8
	pm3_dotted_note_set
	pm3_note F_3, 8
	pm3_dotted_note_set
	pm3_note G_3, 16
	pm3_note F_3, 16
	pm3_connect_note_set
	pm3_note Eb3, 16
	pm3_dotted_note_set
	pm3_connect_note_set
	pm3_note Eb3, 8
	pm3_connect_note_set
	pm3_note D_3, 32
	pm3_connect_note_set
	pm3_note D_3, 4
	pm3_dotted_note_set
	pm3_note Eb3, 8
	pm3_dotted_note_set
	pm3_note F_3, 8
	pm3_note G_3, 16
	pm3_note G_3, 8
	pm3_note D_4, 8
	pm3_note F_3, 8
	pm3_connect_note_set
	pm3_note Eb3, 16
	pm3_dotted_note_set
	pm3_connect_note_set
	pm3_note Eb3, 8
	pm3_connect_note_set
	pm3_note D_3, 32
	pm3_connect_note_set
	pm3_note D_3, 4
	pm3_dotted_note_set
	pm3_note Eb3, 8
	pm3_dotted_note_set
	pm3_note F_3, 8
	pm3_dotted_note_set
	pm3_note G_3, 16
	pm3_note F_3, 16
	pm3_connect_note_set
	pm3_note Eb3, 16
	pm3_dotted_note_set
	pm3_connect_note_set
	pm3_note Eb3, 8
	pm3_connect_note_set
	pm3_note D_3, 32
	pm3_connect_note_set
	pm3_note D_3, 4
	pm3_dotted_note_set
	pm3_note C_3, 8
	pm3_dotted_note_set
	pm3_note D_3, 8
	pm3_connect_note_set
	pm3_note Eb3, 32
	pm3_connect_note_set
	pm3_note Eb3, 8
	pm3_rest 32
	pm3_rest 8
	pm3_note F_3, 8
	pm3_note Bb3, 8
	pm3_note A_3, 8

music_ending_triangle_main:
	pm3_channel_flags channel_connect_note_set
	pm3_note G_3, 16
	pm3_connect_note_set
	pm3_note G_3, 4
	pm3_note G_3, 4
	pm3_note Bb3, 4
	pm3_note G_3, 4
	pm3_dotted_note_set
	pm3_note Gb3, 16
	pm3_note Gb3, 8
	pm3_connect_note_set
	pm3_note F_3, 16
	pm3_connect_note_set
	pm3_note F_3, 4
	pm3_note F_3, 4
	pm3_note Bb3, 4
	pm3_note F_3, 4
	pm3_dotted_note_set
	pm3_note Eb3, 16
	pm3_note Eb3, 8
	pm3_connect_note_set
	pm3_note Eb3, 16
	pm3_connect_note_set
	pm3_note Eb3, 4
	pm3_note Gb3, 4
	pm3_note F_3, 4
	pm3_note Eb3, 4
	pm3_dotted_note_set
	pm3_note Db3, 16
	pm3_note Db3, 8
	pm3_connect_note_set
	pm3_note C_3, 16
	pm3_connect_note_set
	pm3_note C_3, 4
	pm3_note C_3, 4
	pm3_note F_3, 4
	pm3_note Eb3, 4
	pm3_dotted_note_set
	pm3_note D_3, 16
	pm3_note D_3, 4
	pm3_note F_3, 4

music_ending_triangle_loop_2:
	pm3_channel_flags channel_connect_note_set
	pm3_note G_3, 16
	pm3_connect_note_set
	pm3_note G_3, 4
	pm3_note G_3, 4
	pm3_note Bb3, 4
	pm3_note G_3, 4
	pm3_dotted_note_set
	pm3_note Gb3, 16
	pm3_note Gb3, 8
	pm3_connect_note_set
	pm3_note F_3, 16
	pm3_connect_note_set
	pm3_note F_3, 4
	pm3_note F_3, 4
	pm3_note Bb3, 4
	pm3_note F_3, 4
	pm3_dotted_note_set
	pm3_note E_3, 16
	pm3_note E_3, 8
	pm3_connect_note_set
	pm3_note Eb3, 16
	pm3_connect_note_set
	pm3_note Eb3, 4
	pm3_note Eb3, 4
	pm3_note Bb3, 4
	pm3_note Eb3, 4
	pm3_note F_3, 16
	pm3_note Bb3, 8
	pm3_note A_3, 8
	pm3_connect_note_set
	pm3_note G_3, 32
	pm3_connect_note_set
	pm3_note G_3, 8
	pm3_note B_3, 4
	pm3_note C_4, 4
	pm3_note D_4, 4
	pm3_note Db4, 4
	pm3_note D_4, 4
	pm3_note F_3, 4
	pm3_break_2 no_channel_flags_set, music_ending_triangle_break_1

music_ending_triangle_loop_1:
	pm3_channel_flags channel_connect_note_set
	pm3_note C_3, 16
	pm3_connect_note_set
	pm3_note C_3, 4
	pm3_note C_3, 4
	pm3_note D_3, 4
	pm3_note Eb3, 4
	pm3_dotted_note_set
	pm3_note F_3, 16
	pm3_note F_3, 4
	pm3_note G_3, 4
	pm3_connect_note_set
	pm3_note Bb2, 16
	pm3_connect_note_set
	pm3_note Bb2, 4
	pm3_note Bb2, 8
	pm3_note Bb2, 4
	pm3_note Bb2, 32
	pm3_loop_1 1, music_ending_triangle_loop_1
	pm3_connect_note_set
	pm3_note Eb3, 16
	pm3_connect_note_set
	pm3_note Eb3, 4
	pm3_note Eb3, 4
	pm3_note F_3, 4
	pm3_note Gb3, 4
	pm3_dotted_note_set
	pm3_note Ab3, 16
	pm3_note Ab3, 4
	pm3_note Gb3, 4
	pm3_dotted_note_set
	pm3_note Db3, 16
	pm3_note Db3, 4
	pm3_note Eb3, 4
	pm3_dotted_note_set
	pm3_note E_3, 16
	pm3_note Ab3, 4
	pm3_note Gb3, 4
	pm3_dotted_note_set
	pm3_note Eb3, 16
	pm3_note Ab3, 4
	pm3_note Bb3, 4
	pm3_note Ab3, 8
	pm3_dotted_note_set
	pm3_note Eb3, 16
	pm3_connect_note_set
	pm3_note F_3, 16
	pm3_connect_note_set
	pm3_note F_3, 4
	pm3_note F_3, 4
	pm3_note Ab3, 4
	pm3_note A_3, 4
	pm3_note Bb3, 32
	pm3_loop_2 1, music_ending_triangle_loop_2

music_ending_triangle_break_1:
	current_octave_jump .SET 0

music_ending_triangle_loop_3:
	pm3_channel_flags channel_connect_note_set
	pm3_note C_3, 16
	pm3_connect_note_set
	pm3_note C_3, 4
	pm3_note C_3, 4
	pm3_note D_3, 4
	pm3_note Eb3, 4
	pm3_dotted_note_set
	pm3_note F_3, 16
	pm3_note F_3, 4
	pm3_note G_3, 4
	pm3_connect_note_set
	pm3_note Bb2, 16
	pm3_connect_note_set
	pm3_note Bb2, 4
	pm3_note Bb2, 8
	pm3_note Bb2, 4
	pm3_dotted_note_set
	pm3_note Bb2, 16
	pm3_note Bb2, 4
	pm3_note C_3, 4
	pm3_loop_1 1, music_ending_triangle_loop_3
	pm3_connect_note_set
	pm3_note D_3, 16
	pm3_connect_note_set
	pm3_note D_3, 4
	pm3_note D_3, 4
	pm3_note Eb3, 4
	pm3_note F_3, 4
	pm3_connect_note_set
	pm3_note D_3, 16
	pm3_connect_note_set
	pm3_note D_3, 4
	pm3_note D_3, 4
	pm3_note Bb3, 4
	pm3_note A_3, 4
	pm3_note G_3, 16
	pm3_note F_3, 16
	pm3_dotted_note_set
	pm3_note Eb3, 16
	pm3_note Eb3, 4
	pm3_note D_3, 4
	pm3_dotted_note_set
	pm3_note C_3, 16
	pm3_note C_3, 8
	pm3_connect_note_set
	pm3_note C_3, 16
	pm3_connect_note_set
	pm3_note C_3, 4
	pm3_note C_3, 4
	pm3_note D_3, 4
	pm3_note Eb3, 4
	pm3_note F_3, 16
	pm3_note G_3, 16
	pm3_note A_3, 16
	pm3_note C_4, 16
	pm3_music_jump music_ending_triangle_main
	pm3_music_end

music_ending_noise:
	pm3_music_end

music_staff_roll:
	pm3_music_header
	.DBYT music_staff_roll_pulse_1
	.DBYT music_staff_roll_pulse_2
	.DBYT music_staff_roll_triangle
	.DBYT music_staff_roll_noise

;reset
	current_global_transpose .SET 0

music_staff_roll_pulse_1:
	current_octave_jump .SET 0
	current_octave .SET 0
	current_channel_transpose .SET 0
	pm3_tempo $01, $C7
	pm3_note_ads $FF
	pm3_volume 15
	pm3_duty_cycle 1
	pm3_instrument 22
	pm3_octave 0
	pm3_rest 64
	pm3_global_transpose 5
	pm3_octave_jump
	pm3_note D_4, 16
	pm3_triplet_note_set
	pm3_note C_4, 1
	pm3_note Bb3, 1
	pm3_note A_3, 1
	pm3_note G_3, 1
	pm3_note F_3, 1
	pm3_note E_3, 1
	pm3_note D_3, 1
	pm3_note E_3, 1
	pm3_note C_3, 1
	pm3_note Bb2, 1
	pm3_note A_2, 1
	pm3_note G_2, 1
	pm3_note F_2, 1
	pm3_octave_jump
	pm3_note E_2, 1
	pm3_note D_2, 1
	pm3_note C_2, 1
	pm3_note Bb1, 1
	pm3_note A_1, 1
	pm3_note G_1, 1
	pm3_note F_1, 1
	pm3_rest 16
	pm3_duty_cycle 3
	pm3_note_ads $96
	pm3_instrument 28
	pm3_triplet_note_set
	pm3_octave_jump
	pm3_note C_4, 8
	pm3_note D_4, 8
	pm3_note Eb4, 8

music_staff_roll_pulse_1_loop_1:
	pm3_channel_flags channel_octave_jump_set
	pm3_octave 1
	pm3_note F_4, 8
	pm3_note Eb4, 8
	pm3_note D_4, 4
	pm3_note C_4, 8
	pm3_note F_4, 8
	pm3_dotted_note_set
	pm3_note Eb4, 8
	pm3_note D_4, 4
	pm3_note C_4, 8
	pm3_connect_note_set
	pm3_note D_4, 4
	pm3_break_1 channel_octave_jump_set | channel_connect_note_set, music_staff_roll_pulse_1_break_1
	pm3_note D_4, 32
	pm3_connect_note_set
	pm3_note D_4, 8
	pm3_note C_4, 8
	pm3_note D_4, 8
	pm3_note Eb4, 8
	pm3_loop_1 1, music_staff_roll_pulse_1_loop_1

music_staff_roll_pulse_1_break_1:
	current_octave_jump .SET 1
	pm3_instrument 22
	pm3_note_ads $64
	pm3_connect_note_set
	pm3_note D_4, 8
	pm3_dotted_note_set
	pm3_note D_4, 8
	pm3_note D_4, 8
	pm3_note D_4, 8
	pm3_connect_note_set
	pm3_note D_4, 16
	pm3_connect_note_set
	pm3_note D_4, 4
	pm3_note Eb4, 8
	pm3_note D_4, 8

music_staff_roll_pulse_1_main:
	pm3_channel_flags no_channel_flags_set
	pm3_instrument 28
	pm3_octave 2
	pm3_volume 15
	pm3_note Db4, 2
	pm3_dotted_note_set
	pm3_note D_4, 4
	pm3_note C_4, 4
	pm3_note B_3, 8
	pm3_note C_4, 8
	pm3_dotted_note_set
	pm3_note B_3, 8
	pm3_note A_3, 4
	pm3_note G_3, 8
	pm3_connect_note_set
	pm3_note A_3, 4
	pm3_connect_note_set
	pm3_note A_3, 32
	pm3_rest 8
	pm3_note E_3, 8
	pm3_note G_3, 4
	pm3_note E_3, 8
	pm3_connect_note_set
	pm3_note B_3, 4
	pm3_connect_note_set
	pm3_note B_3, 16
	pm3_note C_4, 16
	pm3_note B_3, 8
	pm3_note A_3, 8
	pm3_note G_3, 8
	pm3_note A_3, 4
	pm3_connect_note_set
	pm3_note B_3, 4
	pm3_note B_3, 32
	pm3_connect_note_set
	pm3_note B_3, 8
	pm3_note D_4, 8
	pm3_note B_3, 8
	pm3_connect_note_set
	pm3_note Gb3, 8
	pm3_connect_note_set
	pm3_note Gb3, 32
	pm3_connect_note_set
	pm3_note F_3, 16
	pm3_connect_note_set
	pm3_note F_3, 16
	pm3_rest 8
	pm3_note E_3, 8
	pm3_note E_3, 4
	pm3_note Gb3, 8
	pm3_connect_note_set
	pm3_note G_3, 32
	pm3_connect_note_set
	pm3_note G_3, 4
	pm3_rest 8
	pm3_note E_3, 8
	pm3_note E_3, 4
	pm3_note Gb3, 8
	pm3_note G_3, 8
	pm3_dotted_note_set
	pm3_note A_3, 8
	pm3_note B_3, 8
	pm3_note C_4, 8
	pm3_note Db4, 2
	pm3_dotted_note_set
	pm3_connect_note_set
	pm3_note D_4, 32
	pm3_dotted_note_set
	pm3_connect_note_set
	pm3_note D_4, 4
	pm3_note_ads $FF
	pm3_instrument 22
	pm3_note F_4, 8
	pm3_rest 8
	pm3_note F_4, 8
	pm3_note E_4, 16
	pm3_note D_4, 8
	pm3_note C_4, 16
	pm3_note Eb4, 2
	pm3_dotted_note_set
	pm3_connect_note_set
	pm3_note E_4, 4
	pm3_connect_note_set
	pm3_note E_4, 16
	pm3_triplet_note_set
	pm3_note D_4, 2
	pm3_note C_4, 2
	pm3_note B_3, 2
	pm3_note A_3, 2
	pm3_connect_note_set
	pm3_note G_3, 4
	pm3_dotted_note_set
	pm3_triplet_note_set
	pm3_connect_note_set
	pm3_note G_3, 8
	pm3_rest 4
	pm3_note_ads $96
	pm3_instrument 28
	pm3_note E_3, 8
	pm3_note G_3, 8
	pm3_note A_3, 8
	pm3_note B_3, 16
	pm3_note Bb3, 8
	pm3_note B_3, 16
	pm3_note D_4, 16
	pm3_connect_note_set
	pm3_note G_3, 8
	pm3_connect_note_set
	pm3_note G_3, 32
	pm3_note B_3, 8
	pm3_note G_3, 8
	pm3_note E_3, 8
	pm3_connect_note_set
	pm3_note B_3, 8
	pm3_connect_note_set
	pm3_note B_3, 64
	pm3_rest 16
	pm3_note E_3, 16
	pm3_note G_3, 8
	pm3_note B_3, 16
	pm3_connect_note_set
	pm3_note C_4, 8
	pm3_note_ads $64
	pm3_connect_note_set
	pm3_note C_4, 8
	pm3_note C_4, 8
	pm3_note B_3, 16
	pm3_note D_4, 8
	pm3_note B_3, 16
	pm3_connect_note_set
	pm3_note A_3, 8
	pm3_dotted_note_set
	pm3_note A_3, 32
	pm3_connect_note_set
	pm3_note A_3, 8
	pm3_connect_note_set
	pm3_note A_3, 8
	pm3_connect_note_set
	pm3_note A_3, 8
	pm3_note B_3, 8
	pm3_dotted_note_set
	pm3_note Ab3, 16
	pm3_note Gb4, 8
	pm3_note E_4, 8
	pm3_note D_4, 4
	pm3_connect_note_set
	pm3_note E_4, 4
	pm3_note E_4, 32
	pm3_connect_note_set
	pm3_note E_4, 8
	pm3_octave 1
	pm3_note_ads $64
	pm3_note E_3, 8
	pm3_note Gb3, 8
	pm3_note Ab3, 8
	pm3_dotted_note_set
	pm3_octave_jump
	pm3_note Db4, 8
	pm3_dotted_note_set
	pm3_note B_3, 8
	pm3_dotted_note_set
	pm3_note A_3, 8
	pm3_dotted_note_set
	pm3_note G_3, 8
	pm3_note Gb3, 4
	pm3_rest 4
	pm3_octave_jump
	pm3_note E_3, 4
	pm3_rest 4
	pm3_connect_note_set
	pm3_note Eb3, 32
	pm3_connect_note_set
	pm3_note Eb3, 8
	pm3_note B_3, 4
	pm3_rest 4
	pm3_octave_jump
	pm3_note Db4, 4
	pm3_rest 4
	pm3_octave_jump
	pm3_note Eb3, 4
	pm3_connect_note_set
	pm3_note F_3, 4
	pm3_note F_3, 32
	pm3_connect_note_set
	pm3_note F_3, 8
	pm3_note F_3, 8
	pm3_note Gb3, 8
	pm3_note Ab3, 8
	pm3_dotted_note_set
	pm3_note A_3, 8
	pm3_dotted_note_set
	pm3_note G_3, 8
	pm3_dotted_note_set
	pm3_octave_jump
	pm3_note C_4, 8
	pm3_dotted_note_set
	pm3_note Bb3, 8
	pm3_note A_3, 4
	pm3_rest 4
	pm3_note G_3, 4
	pm3_rest 4
	pm3_dotted_note_set
	pm3_note A_3, 8
	pm3_dotted_note_set
	pm3_note G_3, 8
	pm3_dotted_note_set
	pm3_note C_4, 8
	pm3_dotted_note_set
	pm3_note Bb3, 8
	pm3_note A_3, 4
	pm3_rest 4
	pm3_note G_3, 4
	pm3_rest 4
	pm3_connect_note_set
	pm3_note A_3, 32
	pm3_connect_note_set
	pm3_note A_3, 8
	pm3_note A_3, 8
	pm3_note Bb3, 8
	pm3_connect_note_set
	pm3_note C_4, 8
	pm3_note C_4, 32
	pm3_connect_note_set
	pm3_note C_4, 8
	pm3_note A_3, 8
	pm3_note Bb3, 8
	pm3_note C_4, 8
	pm3_connect_note_set
	pm3_note Db4, 32
	pm3_connect_note_set
	pm3_note Db4, 8
	pm3_note Db4, 8
	pm3_note B_3, 8
	pm3_note A_3, 8
	pm3_dotted_note_set
	pm3_note Ab3, 8
	pm3_dotted_note_set
	pm3_note Gb3, 8
	pm3_note F_3, 4
	pm3_rest 4
	pm3_dotted_note_set
	pm3_note Gb3, 8
	pm3_dotted_note_set
	pm3_note Ab3, 8
	pm3_note A_3, 4
	pm3_rest 4
	pm3_connect_note_set
	pm3_note Eb4, 32
	pm3_connect_note_set
	pm3_note Eb4, 8
	pm3_note Eb4, 8
	pm3_note Db4, 8
	pm3_note Eb4, 8
	pm3_dotted_note_set
	pm3_note Eb4, 8
	pm3_note E_4, 4
	pm3_rest 8
	pm3_connect_note_set
	pm3_note Db4, 32
	pm3_connect_note_set
	pm3_note Db4, 8
	pm3_dotted_note_set
	pm3_note Db4, 8
	pm3_dotted_note_set
	pm3_note B_3, 8
	pm3_dotted_note_set
	pm3_note E_4, 8
	pm3_dotted_note_set
	pm3_note D_4, 8
	pm3_note Db4, 4
	pm3_rest 4
	pm3_note B_3, 4
	pm3_rest 4
	pm3_dotted_note_set
	pm3_note Bb3, 8
	pm3_dotted_note_set
	pm3_note A_3, 8
	pm3_dotted_note_set
	pm3_note C_4, 8
	pm3_dotted_note_set
	pm3_note Bb3, 8
	pm3_note A_3, 4
	pm3_rest 4
	pm3_note G_3, 4
	pm3_rest 4
	pm3_pitch_tune $03
	pm3_note D_4, 64
	pm3_instrument 0
	pm3_note_ads $B4
	pm3_volume 12
	pm3_dotted_note_set
	pm3_note D_4, 8
	pm3_dotted_note_set
	pm3_note D_4, 8
	pm3_note D_4, 4
	pm3_note D_4, 4
	pm3_dotted_note_set
	pm3_note D_4, 8
	pm3_dotted_note_set
	pm3_note D_4, 8
	pm3_note D_4, 4
	pm3_note D_4, 4
	pm3_triplet_note_set
	pm3_note D_5, 2
	pm3_note A_4, 2
	pm3_note F_4, 2
	pm3_note D_4, 2
	pm3_note A_3, 2
	pm3_note F_3, 2
	pm3_pitch_tune $00
	pm3_music_jump music_staff_roll_pulse_1_main
	pm3_music_end

music_staff_roll_pulse_2:
	current_octave_jump .SET 0
	current_octave .SET 0
	current_channel_transpose .SET 0
	pm3_note_ads $C8
	pm3_volume 6
	pm3_duty_cycle 1
	pm3_instrument 17
	pm3_octave 0
	pm3_rest 64
	pm3_octave_jump
	pm3_note Gb3, 64
	pm3_note A_3, 64
	pm3_note Gb3, 64
	pm3_note A_3, 64
	pm3_volume 9
	pm3_note_ads $64
	pm3_instrument 22
	pm3_note Gb3, 8
	pm3_dotted_note_set
	pm3_note Gb3, 8
	pm3_note Gb3, 8
	pm3_note Gb3, 8
	pm3_connect_note_set
	pm3_note Gb3, 16
	pm3_connect_note_set
	pm3_note Gb3, 4
	pm3_note G_3, 8
	pm3_note_ads $C8
	pm3_note Gb3, 8

music_staff_roll_pulse_2_main:
	pm3_channel_flags no_channel_flags_set
	pm3_rest 8
	pm3_dotted_note_set
	pm3_rest 32
	pm3_duty_cycle 1
	pm3_octave 1
	pm3_volume 6
	pm3_instrument 17
	pm3_note_ads $C8
	pm3_octave_jump
	pm3_note C_4, 32
	pm3_note E_4, 16
	pm3_note A_4, 16
	pm3_connect_note_set
	pm3_note D_4, 32
	pm3_connect_note_set
	pm3_note D_4, 8
	pm3_instrument 22
	pm3_note Gb4, 4
	pm3_note A_4, 4
	pm3_rest 4
	pm3_dotted_note_set
	pm3_note C_5, 8
	pm3_instrument 17
	pm3_note B_4, 32
	pm3_note Bb4, 32
	pm3_note A_4, 32
	pm3_note Ab4, 32
	pm3_note G_4, 64
	pm3_note Gb4, 64
	pm3_dotted_note_set
	pm3_connect_note_set
	pm3_note F_4, 32
	pm3_connect_note_set
	pm3_note F_4, 8
	pm3_instrument 22
	pm3_connect_note_set
	pm3_note A_4, 8
	pm3_connect_note_set
	pm3_note A_4, 8
	pm3_note A_4, 8
	pm3_note G_4, 16
	pm3_note G_4, 8
	pm3_note F_4, 16
	pm3_rest 8
	pm3_instrument 17
	pm3_note G_4, 64
	pm3_duty_cycle 2
	pm3_note B_4, 64
	pm3_octave 1
	pm3_duty_cycle 1
	pm3_volume 12
	pm3_note_ads $B4
	pm3_instrument 36
	pm3_note E_5, 8
	pm3_note B_4, 8
	pm3_note G_4, 8
	pm3_note E_5, 8
	pm3_note Eb5, 8
	pm3_note B_4, 8
	pm3_note G_4, 8
	pm3_connect_note_set
	pm3_note D_5, 8
	pm3_connect_note_set
	pm3_note D_5, 8
	pm3_note B_4, 8
	pm3_note G_4, 8
	pm3_note D_5, 8
	pm3_note Db5, 8
	pm3_note A_4, 8
	pm3_note Gb4, 8
	pm3_instrument 28
	pm3_connect_note_set
	pm3_note G_4, 8
	pm3_dotted_note_set
	pm3_note G_4, 32
	pm3_connect_note_set
	pm3_note G_4, 8
	pm3_note C_5, 4
	pm3_triplet_note_set
	pm3_note B_4, 2
	pm3_note A_4, 2
	pm3_note G_4, 2
	pm3_triplet_note_set
	pm3_rest 8
	pm3_volume 10
	pm3_note_ads $64
	pm3_note G_4, 8
	pm3_note G_4, 16
	pm3_note A_4, 8
	pm3_note A_4, 16
	pm3_connect_note_set
	pm3_note B_3, 8
	pm3_dotted_note_set
	pm3_note B_3, 32
	pm3_connect_note_set
	pm3_note B_3, 8
	pm3_connect_note_set
	pm3_note B_3, 8
	pm3_connect_note_set
	pm3_note B_3, 8
	pm3_note B_3, 8
	pm3_note B_3, 16
	pm3_octave 0
	pm3_note_ads $C8
	pm3_instrument 22
	pm3_note E_4, 4
	pm3_note D_4, 4
	pm3_note Db4, 4
	pm3_note D_4, 4
	pm3_note E_4, 4
	pm3_octave 1
	pm3_note Gb4, 4
	pm3_note Ab4, 4
	pm3_note A_4, 4
	pm3_octave_jump
	pm3_note E_3, 8
	pm3_note E_3, 4
	pm3_note E_3, 4
	pm3_note E_3, 4
	pm3_note E_3, 8
	pm3_note E_3, 4
	pm3_rest 32
	pm3_volume 5
	pm3_instrument 17
	pm3_note A_2, 16
	pm3_note Db3, 16
	pm3_note E_3, 16
	pm3_note G_3, 16

music_staff_roll_pulse_2_loop_1:
	pm3_channel_flags no_channel_flags_set
	pm3_volume 10
	pm3_note_ads $96
	pm3_instrument 22
	pm3_note Ab2, 8
	pm3_octave_jump
	pm3_note Ab4, 8
	pm3_note Gb4, 4
	pm3_note Ab4, 8
	pm3_rest 4
	pm3_note Ab4, 8
	pm3_note Gb4, 4
	pm3_connect_note_set
	pm3_note Ab4, 4
	pm3_connect_note_set
	pm3_note Ab4, 16
	pm3_loop_1 1, music_staff_roll_pulse_2_loop_1

music_staff_roll_pulse_2_loop_2:
	pm3_channel_flags no_channel_flags_set
	pm3_octave 1
	pm3_rest 8
	pm3_octave_jump
	pm3_note F_4, 8
	pm3_note E_4, 4
	pm3_note F_4, 8
	pm3_rest 4
	pm3_note F_4, 8
	pm3_note E_4, 4
	pm3_note F_4, 8
	pm3_rest 4
	pm3_octave 2
	pm3_note F_5, 4
	pm3_note F_5, 4
	pm3_loop_1 1, music_staff_roll_pulse_2_loop_2
	pm3_note_ads $FF
	pm3_octave_jump
	pm3_note E_4, 2
	pm3_dotted_note_set
	pm3_note F_4, 8
	pm3_dotted_note_set
	pm3_note E_4, 8
	pm3_connect_note_set
	pm3_note C_4, 32
	pm3_dotted_note_set
	pm3_connect_note_set
	pm3_note C_4, 4
	pm3_duty_cycle 0
	pm3_volume 13
	pm3_instrument 0
	pm3_rest 8
	pm3_octave_jump
	pm3_note C_5, 4
	pm3_rest 8
	pm3_note C_5, 4
	pm3_rest 8
	pm3_note C_5, 4
	pm3_volume 10
	pm3_octave 1
	pm3_note D_4, 4
	pm3_note E_4, 4
	pm3_note F_4, 4
	pm3_note G_4, 4
	pm3_note Ab4, 4
	pm3_note A_4, 4
	pm3_note Bb4, 4
	pm3_volume 8
	pm3_instrument 17
	pm3_connect_note_set
	pm3_note B_4, 64
	pm3_connect_note_set
	pm3_note B_4, 16
	pm3_note A_4, 16
	pm3_note Ab4, 16
	pm3_note Gb4, 16

music_staff_roll_pulse_2_loop_3:
	pm3_channel_flags channel_octave_jump_set
	pm3_duty_cycle 1
	pm3_note_ads $96
	pm3_instrument 28
	pm3_volume 10
	pm3_note Eb4, 8
	pm3_note Eb5, 4
	pm3_note Db5, 4
	pm3_note Eb4, 4
	pm3_note B_3, 4
	pm3_duty_cycle 2
	pm3_instrument 32
	pm3_note E_4, 8
	pm3_duty_cycle 1
	pm3_instrument 28
	pm3_note Eb5, 4
	pm3_note Db5, 4
	pm3_note Eb4, 4
	pm3_note B_3, 4
	pm3_duty_cycle 2
	pm3_instrument 32
	pm3_note Gb4, 16
	pm3_loop_1 1, music_staff_roll_pulse_2_loop_3
	pm3_volume 6
	pm3_duty_cycle 1
	pm3_instrument 17
	pm3_octave 1
	pm3_dotted_note_set
	pm3_note Db5, 16
	pm3_dotted_note_set
	pm3_note B_4, 16
	pm3_note Gb4, 16
	pm3_dotted_note_set
	pm3_note C_5, 16
	pm3_dotted_note_set
	pm3_note Bb4, 16
	pm3_note F_4, 16
	pm3_volume 6
	pm3_note D_5, 64
	pm3_duty_cycle 0
	pm3_instrument 0
	pm3_volume 12
	pm3_note_ads $B4
	pm3_dotted_note_set
	pm3_note D_5, 8
	pm3_dotted_note_set
	pm3_note D_5, 8
	pm3_note D_5, 4
	pm3_note D_5, 4
	pm3_dotted_note_set
	pm3_note D_5, 8
	pm3_dotted_note_set
	pm3_note D_5, 8
	pm3_note D_5, 4
	pm3_note D_5, 4
	pm3_triplet_note_set
	pm3_note D_5, 2
	pm3_note A_4, 2
	pm3_note F_4, 2
	pm3_note D_4, 2
	pm3_note A_3, 2
	pm3_note F_3, 2
	pm3_music_jump music_staff_roll_pulse_2_main
	pm3_music_end

music_staff_roll_triangle:
	current_octave_jump .SET 0
	current_octave .SET 0
	current_channel_transpose .SET 0
	pm3_note_ads $E6
	pm3_instrument 14
	pm3_octave 2
	pm3_octave_jump
	pm3_note D_5, 4
	pm3_note D_5, 4
	pm3_note Bb4, 8
	pm3_note D_5, 4
	pm3_note D_5, 4
	pm3_note Bb4, 8
	pm3_rest 4
	pm3_note D_5, 4
	pm3_rest 4
	pm3_note D_5, 4
	pm3_triplet_note_set
	pm3_note D_5, 4
	pm3_note D_5, 4
	pm3_note D_5, 4
	pm3_triplet_note_set
	pm3_note Bb4, 8
	pm3_instrument 2
	pm3_note_ads $78
	pm3_octave 3

music_staff_roll_triangle_loop_1:
	pm3_channel_flags no_channel_flags_set
	pm3_note D_4, 8
	pm3_note D_4, 8
	pm3_note A_3, 4
	pm3_note C_4, 8
	pm3_note D_4, 8
	pm3_note D_4, 8
	pm3_note A_3, 4
	pm3_note C_4, 8
	pm3_note D_4, 8
	pm3_break_1 no_channel_flags_set, music_staff_roll_triangle_break_1
	pm3_note Eb4, 8
	pm3_note Eb4, 8
	pm3_note A_3, 4
	pm3_note C_4, 8
	pm3_note Eb4, 8
	pm3_note Eb4, 8
	pm3_note A_3, 4
	pm3_note C_4, 8
	pm3_note Eb4, 8
	pm3_loop_1 2, music_staff_roll_triangle_loop_1

music_staff_roll_triangle_break_1:
	current_octave_jump .SET 0
	pm3_note D_4, 8

music_staff_roll_triangle_main:
	pm3_channel_flags no_channel_flags_set
	pm3_rest 8
	pm3_dotted_note_set
	pm3_rest 32
	pm3_note_ads $C8
	pm3_note A_3, 16
	pm3_octave 2
	pm3_note E_3, 16
	pm3_note A_3, 16
	pm3_note E_3, 16
	pm3_note D_3, 16
	pm3_note A_3, 16
	pm3_note D_3, 16
	pm3_note A_3, 16
	pm3_note B_3, 16
	pm3_note Gb3, 8
	pm3_note B_3, 8
	pm3_note Bb3, 16
	pm3_note Gb3, 8
	pm3_note Bb3, 8
	pm3_note A_3, 16
	pm3_note Gb3, 8
	pm3_note A_3, 8
	pm3_note Ab3, 16
	pm3_note E_3, 16
	pm3_note C_4, 16
	pm3_note G_3, 16
	pm3_note C_4, 16
	pm3_note G_3, 8
	pm3_note C_4, 8
	pm3_note D_4, 16
	pm3_note A_3, 16
	pm3_note D_4, 16
	pm3_note E_4, 8
	pm3_note Gb4, 8
	pm3_note G_4, 16
	pm3_note D_4, 16
	pm3_note G_4, 16
	pm3_note D_4, 8
	pm3_note F_4, 8
	pm3_rest 8
	pm3_note F_4, 8
	pm3_note E_4, 16
	pm3_note D_4, 8
	pm3_note D_4, 16
	pm3_note C_4, 8
	pm3_note C_4, 16
	pm3_note G_3, 16
	pm3_note C_4, 16
	pm3_note G_3, 16
	pm3_note Db4, 16
	pm3_note Ab3, 8
	pm3_note Db4, 16
	pm3_note Db4, 16
	pm3_connect_note_set
	pm3_note E_4, 8
	pm3_connect_note_set
	pm3_note E_4, 8
	pm3_note E_4, 8
	pm3_note E_4, 8
	pm3_note Eb4, 16
	pm3_note Eb4, 16
	pm3_connect_note_set
	pm3_note D_4, 8
	pm3_connect_note_set
	pm3_note D_4, 8
	pm3_note B_3, 8
	pm3_note G_3, 8
	pm3_note Db4, 16
	pm3_note A_3, 8
	pm3_note Gb3, 16
	pm3_note C_4, 16
	pm3_note G_3, 16
	pm3_note C_4, 8
	pm3_note G_3, 16
	pm3_note Db4, 8
	pm3_rest 8
	pm3_note Db4, 8
	pm3_note Db4, 16
	pm3_note D_4, 8
	pm3_note B_3, 16
	pm3_note A_3, 8
	pm3_octave 1
	pm3_rest 8
	pm3_note E_3, 8
	pm3_note E_3, 8
	pm3_note E_3, 8
	pm3_note E_3, 8
	pm3_note E_3, 16
	pm3_octave 2
	pm3_note E_3, 8
	pm3_rest 8
	pm3_note E_3, 8
	pm3_connect_note_set
	pm3_note E_3, 16
	pm3_connect_note_set
	pm3_note E_3, 16
	pm3_note Bb3, 16
	pm3_note E_4, 4
	pm3_note E_4, 4
	pm3_note A_3, 8
	pm3_note Db4, 4
	pm3_rest 4
	pm3_note Db4, 8
	pm3_note E_4, 4
	pm3_rest 4
	pm3_note E_4, 8
	pm3_note Ab4, 4
	pm3_rest 4
	pm3_note Ab4, 8
	pm3_note E_4, 4
	pm3_note G_4, 4
	pm3_note A_3, 8
	pm3_note Db4, 4
	pm3_rest 4
	pm3_note Db4, 8
	pm3_note E_4, 4
	pm3_rest 4
	pm3_note E_4, 8
	pm3_note G_4, 4
	pm3_rest 4
	pm3_note G_4, 8
	pm3_note Eb4, 4
	pm3_note Gb4, 4
	pm3_note Ab3, 8
	pm3_note B_3, 4
	pm3_rest 4
	pm3_note B_3, 8
	pm3_note Eb4, 4
	pm3_rest 4
	pm3_note Eb4, 8
	pm3_note Gb4, 4
	pm3_rest 4
	pm3_note Gb4, 8
	pm3_note Ab3, 8
	pm3_rest 4
	pm3_note Ab3, 4
	pm3_rest 4
	pm3_note Ab3, 4
	pm3_note B_3, 4
	pm3_note D_4, 4
	pm3_note F_4, 8
	pm3_note E_4, 8
	pm3_note D_4, 8
	pm3_note B_3, 8
	pm3_note Bb3, 4
	pm3_note G_3, 4
	pm3_note Bb3, 8
	pm3_note D_4, 4
	pm3_rest 4
	pm3_note D_4, 8
	pm3_note F_4, 4
	pm3_rest 4
	pm3_note F_4, 8
	pm3_note G_3, 4
	pm3_rest 4
	pm3_note G_3, 8
	pm3_note C_4, 4
	pm3_note E_4, 4
	pm3_note C_4, 8
	pm3_note G_3, 4
	pm3_rest 4
	pm3_note G_3, 8
	pm3_note Bb3, 4
	pm3_rest 4
	pm3_note Bb3, 8
	pm3_note C_4, 4
	pm3_rest 4
	pm3_note C_4, 8
	pm3_note C_4, 4
	pm3_note E_4, 4
	pm3_note F_3, 8
	pm3_note A_3, 4
	pm3_rest 4
	pm3_note A_3, 8
	pm3_note C_4, 4
	pm3_rest 4
	pm3_note C_4, 8
	pm3_note E_4, 4
	pm3_rest 4
	pm3_note E_4, 8
	pm3_dotted_note_set
	pm3_note F_3, 8
	pm3_note F_3, 4
	pm3_rest 4
	pm3_note F_3, 4
	pm3_note E_4, 4
	pm3_note F_4, 4
	pm3_note F_3, 4
	pm3_note F_4, 4
	pm3_note F_3, 4
	pm3_note A_3, 4
	pm3_note Bb3, 4
	pm3_note C_4, 4
	pm3_note D_4, 4
	pm3_note E_4, 4
	pm3_dotted_note_set
	pm3_note Gb3, 8
	pm3_note Db4, 4
	pm3_dotted_note_set
	pm3_note Db4, 8
	pm3_note Gb3, 4
	pm3_dotted_note_set
	pm3_note Gb3, 8
	pm3_note Db4, 4
	pm3_note Db4, 8
	pm3_note Gb3, 8
	pm3_dotted_note_set
	pm3_note B_3, 8
	pm3_note Gb4, 4
	pm3_dotted_note_set
	pm3_note Gb4, 8
	pm3_note B_3, 4
	pm3_dotted_note_set
	pm3_note B_3, 8
	pm3_note Gb4, 4
	pm3_note Gb4, 8
	pm3_note B_3, 8
	pm3_dotted_note_set
	pm3_note Ab3, 8
	pm3_note Eb4, 4
	pm3_dotted_note_set
	pm3_note Eb4, 8
	pm3_note Ab3, 4
	pm3_dotted_note_set
	pm3_note Ab3, 8
	pm3_note Eb4, 4
	pm3_note Eb4, 8
	pm3_note Ab3, 8
	pm3_dotted_note_set
	pm3_note Db4, 8
	pm3_note Ab4, 4
	pm3_dotted_note_set
	pm3_note Ab4, 8
	pm3_note Db4, 4
	pm3_note A_4, 8
	pm3_note Ab4, 8
	pm3_note Gb4, 8
	pm3_note Db4, 8
	pm3_dotted_note_set
	pm3_note G_3, 8
	pm3_dotted_note_set
	pm3_note C_4, 8
	pm3_dotted_note_set
	pm3_note Gb4, 16
	pm3_note G_3, 16
	pm3_dotted_note_set
	pm3_note Bb3, 8
	pm3_dotted_note_set
	pm3_note F_4, 8
	pm3_dotted_note_set
	pm3_note Bb4, 16
	pm3_note F_4, 16
	pm3_dotted_note_set
	pm3_note Eb3, 8
	pm3_dotted_note_set
	pm3_note Bb3, 8
	pm3_dotted_note_set
	pm3_note Eb4, 16
	pm3_note Bb3, 16
	pm3_note Eb4, 8
	pm3_rest 4
	pm3_note Eb4, 8
	pm3_rest 4
	pm3_note Eb4, 4
	pm3_note Eb4, 4
	pm3_note Eb4, 8
	pm3_rest 4
	pm3_note Eb4, 8
	pm3_rest 4
	pm3_note Eb4, 4
	pm3_note Eb4, 4
	pm3_note Eb4, 8
	pm3_music_jump music_staff_roll_triangle_main
	pm3_music_end

music_staff_roll_noise:
	pm3_instrument 12
	pm3_volume 12
	pm3_note_ads $96
	pm3_noise_note 11, 4
	pm3_noise_note 7, 4
	pm3_noise_note 4, 4
	pm3_noise_note 7, 4
	pm3_noise_note 11, 4
	pm3_noise_note 7, 4
	pm3_noise_note 4, 4
	pm3_noise_note 7, 4
	pm3_noise_note 2, 4
	pm3_noise_note 7, 4
	pm3_noise_note 2, 4
	pm3_noise_note 7, 4
	pm3_noise_note 11, 4
	pm3_noise_note 7, 4
	pm3_noise_note 4, 8

music_staff_roll_noise_loop_1:
	pm3_channel_flags no_channel_flags_set
	pm3_noise_note 7, 4
	pm3_noise_note 14, 4
	pm3_noise_note 7, 4
	pm3_noise_note 14, 4
	pm3_noise_note 2, 4
	pm3_noise_note 2, 4
	pm3_noise_note 14, 4
	pm3_noise_note 7, 4
	pm3_noise_note 14, 4
	pm3_noise_note 7, 4
	pm3_noise_note 14, 4
	pm3_noise_note 2, 4
	pm3_noise_note 2, 4
	pm3_rest 4
	pm3_noise_note 2, 4
	pm3_rest 4
	pm3_loop_1 3, music_staff_roll_noise_loop_1
	pm3_noise_note 7, 4
	pm3_rest 4
	pm3_noise_note 7, 4
	pm3_rest 4
	pm3_noise_note 7, 4
	pm3_noise_note 7, 4
	pm3_rest 4
	pm3_noise_note 7, 4
	pm3_rest 4
	pm3_dotted_note_set
	pm3_noise_note 7, 8
	pm3_noise_note 7, 4
	pm3_rest 4
	pm3_noise_note 7, 4
	pm3_rest 4
	pm3_noise_note 7, 4
	pm3_rest 4

music_staff_roll_noise_main:
	pm3_channel_flags no_channel_flags_set
	pm3_note_ads $96
	pm3_rest 8
	pm3_rest 32
	pm3_noise_note 14, 4
	pm3_noise_note 14, 4
	pm3_noise_note 12, 8

music_staff_roll_noise_loop_2:
	pm3_channel_flags no_channel_flags_set
	pm3_noise_note 2, 4
	pm3_noise_note 14, 4
	pm3_noise_note 12, 4
	pm3_noise_note 14, 4
	pm3_noise_note 7, 4
	pm3_noise_note 2, 4
	pm3_rest 4
	pm3_noise_note 2, 4
	pm3_rest 4
	pm3_noise_note 2, 4
	pm3_rest 4
	pm3_noise_note 2, 4
	pm3_noise_note 7, 4
	pm3_noise_note 7, 4
	pm3_break_1 no_channel_flags_set, music_staff_roll_noise_break_1
	pm3_noise_note 14, 8
	pm3_loop_1 6, music_staff_roll_noise_loop_2

music_staff_roll_noise_break_1:
	pm3_noise_note 7, 8
	pm3_rest 8
	pm3_noise_note 7, 8
	pm3_noise_note 7, 16
	pm3_noise_note 7, 8
	pm3_noise_note 7, 8
	pm3_rest 8
	pm3_noise_note 7, 8

music_staff_roll_noise_loop_3:
	pm3_channel_flags no_channel_flags_set
	pm3_noise_note 2, 4
	pm3_noise_note 14, 4
	pm3_noise_note 12, 4
	pm3_noise_note 14, 4
	pm3_noise_note 7, 4
	pm3_noise_note 2, 4
	pm3_rest 4
	pm3_noise_note 2, 4
	pm3_rest 4
	pm3_noise_note 2, 4
	pm3_rest 4
	pm3_noise_note 2, 4
	pm3_noise_note 7, 4
	pm3_noise_note 7, 4
	pm3_noise_note 14, 8
	pm3_loop_1 1, music_staff_roll_noise_loop_3

music_staff_roll_noise_loop_4:
	pm3_channel_flags no_channel_flags_set
	pm3_noise_note 2, 4
	pm3_noise_note 14, 4
	pm3_noise_note 12, 4
	pm3_noise_note 14, 4
	pm3_noise_note 7, 4
	pm3_noise_note 14, 4
	pm3_noise_note 12, 4
	pm3_noise_note 14, 4
	pm3_noise_note 2, 4
	pm3_noise_note 14, 4
	pm3_noise_note 12, 4
	pm3_noise_note 14, 4
	pm3_noise_note 7, 4
	pm3_noise_note 14, 4
	pm3_noise_note 12, 4
	pm3_noise_note 14, 4
	pm3_loop_1 1, music_staff_roll_noise_loop_4
	pm3_noise_note 2, 4
	pm3_noise_note 14, 4
	pm3_noise_note 12, 4
	pm3_noise_note 14, 4
	pm3_noise_note 7, 4
	pm3_noise_note 2, 4
	pm3_rest 4
	pm3_noise_note 2, 4
	pm3_rest 4
	pm3_noise_note 2, 4
	pm3_rest 4
	pm3_noise_note 2, 4
	pm3_noise_note 7, 4
	pm3_noise_note 7, 4
	pm3_noise_note 14, 8
	pm3_rest 8
	pm3_noise_note 7, 8
	pm3_noise_note 7, 16
	pm3_noise_note 7, 8
	pm3_noise_note 7, 16
	pm3_noise_note 7, 8
	pm3_rest 8
	pm3_noise_note 7, 8
	pm3_noise_note 7, 8
	pm3_noise_note 7, 8
	pm3_noise_note 7, 8
	pm3_noise_note 7, 8
	pm3_rest 8
	pm3_noise_note 7, 8
	pm3_rest 8
	pm3_noise_note 7, 8
	pm3_noise_note 7, 16
	pm3_noise_note 7, 4
	pm3_noise_note 7, 4
	pm3_note_ads $FF
	pm3_noise_note 12, 8
	pm3_note_ads $96
	pm3_noise_note 7, 4
	pm3_noise_note 7, 4
	pm3_note_ads $FF
	pm3_noise_note 12, 8
	pm3_note_ads $96

music_staff_roll_noise_loop_5:
	pm3_channel_flags no_channel_flags_set
	pm3_note_ads $96
	pm3_noise_note 2, 4
	pm3_noise_note 14, 4
	pm3_noise_note 12, 4
	pm3_noise_note 14, 4
	pm3_noise_note 7, 4
	pm3_noise_note 14, 4
	pm3_noise_note 12, 4
	pm3_noise_note 14, 4
	pm3_noise_note 2, 4
	pm3_noise_note 14, 4
	pm3_noise_note 12, 4
	pm3_noise_note 14, 4
	pm3_noise_note 7, 4
	pm3_noise_note 14, 4
	pm3_noise_note 12, 4
	pm3_noise_note 14, 4
	pm3_break_1 no_channel_flags_set, music_staff_roll_noise_break_2
	pm3_noise_note 2, 4
	pm3_noise_note 14, 4
	pm3_noise_note 12, 4
	pm3_noise_note 14, 4
	pm3_noise_note 7, 4
	pm3_noise_note 14, 4
	pm3_noise_note 12, 4
	pm3_noise_note 14, 4
	pm3_noise_note 2, 4
	pm3_noise_note 9, 4
	pm3_noise_note 14, 4
	pm3_noise_note 2, 4
	pm3_noise_note 7, 4
	pm3_noise_note 14, 4
	pm3_note_ads $FF
	pm3_noise_note 12, 8
	pm3_loop_1 7, music_staff_roll_noise_loop_5

music_staff_roll_noise_break_2:
	pm3_dotted_note_set
	pm3_noise_note 7, 8
	pm3_dotted_note_set
	pm3_noise_note 7, 8
	pm3_noise_note 7, 4
	pm3_noise_note 7, 4
	pm3_dotted_note_set
	pm3_noise_note 7, 8
	pm3_dotted_note_set
	pm3_noise_note 7, 8
	pm3_noise_note 7, 4
	pm3_noise_note 7, 4
	pm3_noise_note 7, 8
	pm3_music_jump music_staff_roll_noise_main
	pm3_music_end

.endscope
.popseg

.assert ProtoMm3::_nmi_audio_processing=Mm3::_nmi_audio_processing,error,"Copied driver entry CPU address"
.assert ProtoMm3::_nmi_audio_track_queue=Mm3::_nmi_audio_track_queue,error,"Copied queue CPU address"
.assert ProtoMm3::_init_channel_pointers_common=Mm3::_init_channel_pointers_common,error,"Copied pause entry CPU address"
