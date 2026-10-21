; Imported from https://github.com/lsmmega/mm2 at 8e378590488ce589c526f0d24ad4dee60afd14a3.
; Original Capcom sound engine and music; adapted by tools/reference/import_megaman_audio.py.
.pushseg
.segment "MM2_AUDIO"
.scope Mm2
;base mm2_note index set
.ENUM
	C_0
	Db0
	D_0
	Eb0
	E_0
	F_0
	Gb0
	G_0
	Ab0
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

;base mm2_note value set
	nC_0 = $0000
	nDb0 = $0000
	nD_0 = $0000
	nEb0 = $0000
	nE_0 = $0000
	nF_0 = $0000
	nGb0 = $0000
	nG_0 = $0000
	nAb0 = $0000
	nA_0 = $07F2
	nBb0 = $07D6
	nB_0 = $0714
	nC_1 = $06AE
	nDb1 = $064E
	nD_1 = $05F3
	nEb1 = $0594
	nE_1 = $054D
	nF_1 = $0501
	nGb1 = $04BB
	nG_1 = $0475
	nAb1 = $0436
	nA_1 = $03F9
	nBb1 = $03BF
	nB_1 = $038A
	nC_2 = $0357
	nDb2 = $0327
	nD_2 = $02FA
	nEb2 = $02CF
	nE_2 = $02A7
	nF_2 = $0281
	nGb2 = $025D
	nG_2 = $023B
	nAb2 = $021A
	nA_2 = $01FC
	nBb2 = $01E0
	nB_2 = $01C5
	nC_3 = $01AB
	nDb3 = $0193
	nD_3 = $017D
	nEb3 = $0167
	nE_3 = $0153
	nF_3 = $0140
	nGb3 = $012E
	nG_3 = $011D
	nAb3 = $010D
	nA_3 = $00FE
	nBb3 = $00F0
	nB_3 = $00E2
	nC_4 = $00D5
	nDb4 = $00C9
	nD_4 = $00BE
	nEb4 = $00B3
	nE_4 = $00A9
	nF_4 = $00A0
	nGb4 = $0097
	nG_4 = $008E
	nAb4 = $0086
	nA_4 = $007F
	nBb4 = $0078
	nB_4 = $0071
	nC_5 = $006A
	nDb5 = $0064
	nD_5 = $005F
	nEb5 = $0059
	nE_5 = $0054
	nF_5 = $0050
	nGb5 = $004B
	nG_5 = $0047
	nAb5 = $0043
	nA_5 = $003F
	nBb5 = $003C
	nB_5 = $0038
	nC_6 = $0035
	nDb6 = $0032
	nD_6 = $002F
	nEb6 = $002C
	nE_6 = $002A
	nF_6 = $0028
	nGb6 = $0025
	nG_6 = $0023
	nAb6 = $0021
	nA_6 = $001F
	nBb6 = $001E
	nB_6 = $001C
	nC_7 = $001A
	nDb7 = $0019
	nD_7 = $0017
	nEb7 = $0016
	nE_7 = $0015
	nF_7 = $0014
	nGb7 = $0012
	nG_7 = $0011
	nAb7 = $0010
	nA_7 = $000F
	nBb7 = $000F
	nB_7 = $000E

;sfx channel flags
	sfx_pulse_1  = 1 << 0
	sfx_pulse_2  = 1 << 1
	sfx_triangle = 1 << 2
	sfx_noise    = 1 << 3

	volume_attack = 0
	volume_decay  = 1 << 7

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

;track ids
.ENUM
	track_flashman
	track_woodman
	track_crashman
	track_heatman
	track_airman
	track_metalman
	track_quickman
	track_bubbleman
	track_wily1_2
	track_wily3_4_5
	track_boss_show
	track_boss_fighting
	track_stage_select
	track_title
	track_opening
	track_game_over
	track_password
	track_wily_castle
	track_wily_ufo
	track_ending
	track_staff_roll
	track_boss_defeated
	track_wily_defeated
	track_get_weapon
	track_18
	track_19
	track_1a
	track_1b
	track_1c
	track_1d
	track_1e
	track_1f
	track_20
	track_time_stopper
	track_22
	track_metal_blade
	track_mega_buster
	track_enemy_bullet
	track_megaman_hit
	track_force_beam
	track_refill
	track_landing
	track_wily_control
	track_enemy_hit
	track_mecha_dragon
	track_enemy_immune
	track_crash_bomber_grab
	track_select
	track_teleport_in
	track_leaf_shield
	track_open_menu
	track_33
	track_door
	track_atomic_fire_charge_1
	track_atomic_fire_charge_2
	track_atomic_fire_charge_3
	track_atomic_fire_release
	track_fly_boy
	track_teleport_out
	track_jump_into_water
	track_appearing_block
	track_red_liquid_1
	track_red_liquid_2
	track_air_shooter
	track_40
	track_death
	track_1up
	music_playmultispeed = $FC
	music_fade_in_out
	mute_sfx
	mute_music
.ENDENUM

zaudio_header = $e0
zsfx_channel = $e1
ztrack_pointers = $e2
zplayback_flag = $e4
zaudio_E5 = $e5
zsfx_apu_register_index = $e6
zmusic_playmultispeed = $e7
zfade_in_out_rate = $e8
zfade_in_out_level = $e9
zaudio_frame = $ea
zmusic_apu_register_index = $eb
zaudio_ram_pointers = $ec
zmusic_channel = $ee
zundo_sfx_channel = $ef
zsfx_pointers = $f0
zsfx_frame = $f2
zsfx_loop = $f3
zaudio_F4 = $f4
zaudio_F5 = $f5
zpause = $41
aaudio_ram = Mm2AudioRam
amodulation_pointers = Mm2AudioRam + $7c
.MACRO mm2_tempo b
	@current_tempo .SET b
	.BYTE $00, b
.ENDMACRO

.MACRO mm2_pitch_envelope b
	.BYTE $01, b
.ENDMACRO

.MACRO mm2_duty_cycle b
	.BYTE $02, b << 6
.ENDMACRO

.MACRO mm2_noise_duty_cycle b
	.BYTE $02, b << 7
.ENDMACRO

.MACRO mm2_volume b
	.IF b & $0F
		.BYTE $03, b | $30
	.ELSE
		.ERROR "Invaild mm2_volume."
	.ENDIF
.ENDMACRO

.MACRO mm2_triangle_note_length b
	.BYTE $03, b
.ENDMACRO

.MACRO mm2_loop b, c
	.BYTE $04, b
	.WORD c
.ENDMACRO

.MACRO mm2_base_note b
	@current_base_note .SET b
	.BYTE $05, b
.ENDMACRO

.MACRO mm2_dotted_note_set
	.BYTE $06
.ENDMACRO

.MACRO mm2_volume_envelope b, c, d
	.BYTE $07, b | d, c << 4
.ENDMACRO

.MACRO mm2_modulator b
	.BYTE $08, b
.ENDMACRO

.MACRO mm2_music_end
	.BYTE $09
.ENDMACRO

.MACRO mm2_music_header
	.BYTE $0F
.ENDMACRO

.MACRO mm2_number_of_note_tied b
	.IF b > 0 && b < 9
		.BYTE b - 1 | $20
	.ELSE
		.ERROR "Number of mm2_note tied from 1 to 8."
	.ENDIF
.ENDMACRO

.MACRO mm2_triplet_note_set
	.BYTE $30
.ENDMACRO

.MACRO mm2_note b, c
	@d .SET b - @current_base_note
	@e .SET @current_tempo & 1
		.IF @d > 0 && @d < $20
			.IF c = 2 && @e
				.ERROR "Note can't play under its mm2_tempo correctly."
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
				.ERROR "Invaild mm2_note length."
			.ENDIF
		.ELSE
			.ERROR "Note is out of bound."
		.ENDIF
.ENDMACRO

.MACRO mm2_rest b
	@c .SET @current_tempo & 1
		.IF b = 2 && @c
			.ERROR "Note can't play under its mm2_tempo correctly."
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
			.ERROR "Invaild mm2_note length."
		.ENDIF
.ENDMACRO

.MACRO mm2_noise_note b, c
	@d .SET b ^ $0F
	@e .SET @current_tempo & 1
		.IF c = 2 && @e
			.ERROR "Note can't play under its mm2_tempo correctly."
		.ELSEIF c = 2 && b = 15
			.BYTE $50
		.ELSEIF c = 4 && b = 15
			.BYTE $70
		.ELSEIF c = 8 && b = 15
			.BYTE $90
		.ELSEIF c = 16 && b = 15
			.BYTE $B0
		.ELSEIF c = 32 && b = 15
			.BYTE $D0
		.ELSEIF c = 64 && b = 15
			.BYTE $F0
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
			.ERROR "Invaild mm2_note length or name."
		.ENDIF
.ENDMACRO

.MACRO mm2_modulator_set b, c, d, e, f, g
	.BYTE d, b << 5 | c, e | g, f
.ENDMACRO

.MACRO mm2_sfx_priority b
	.BYTE b << 4
.ENDMACRO

.MACRO mm2_sfx_frames b
	.BYTE $00, b
.ENDMACRO

.MACRO mm2_sfx_modulator_set b, c, d, e, f, g
	.BYTE $05, d, b << 5 | c, e | g, f
.ENDMACRO

.MACRO mm2_sfx_end
	.BYTE $06
.ENDMACRO

.MACRO mm2_sfx_note b
	.DBYT b | $8000
.ENDMACRO

.MACRO mm2_sfx_noise_note b
	.IF b = 15
		.DBYT $8010
	.ELSE
		.DBYT b ^ $0F | $8000
	.ENDIF
.ENDMACRO

.MACRO mm2_sfx_note_tied
	.DBYT $8FFF
.ENDMACRO

.MACRO mm2_track_queue b
	LDA #b
	JSR _track_queue
.ENDMACRO

;aaudio_ram
;00 = channel pointers lo
;01 = channel pointers hi
;02 = mm2_note length lo
;03 = mm2_note length hi
;04 = mm2_tempo
;05 = triplet mm2_note/mm2_loop
;06 = mm2_note tied/mm2_modulator
;07 = freq table lo
;08 = freq table hi
;09 = pitch envelope
;0A = freq lo
;0B = freq hi
;0C = duty cycle/mm2_volume
;0D = mm2_volume envelope direction/frame
;0E = mm2_volume envelope frame counter
;0F = mm2_volume envelope unit
;10 = sfx pitch envelope
;11 = sfx freq lo
;12 = sfx freq hi
;13 = sfx duty cycle/mm2_volume
;14 = mm2_modulator pitch frame
;15 = mm2_modulator pitch envelope/invert
;16 = mm2_modulator mm2_volume envelope direction/frame
;17 = mm2_modulator mm2_volume envelope unit
;18 = modualtor pitch frame counter
;19 = pitch invert
;1A = pitch bend lo
;1B = pitch bend hi
;1C = apu register hi flag
;1D = modualtor mm2_volume envelope frame counter
;1E = modualtor current mm2_volume

_nmi_audio_processing:
	JMP _audio_processing

_nmi_audio_track_queue:
	CMP #music_playmultispeed
	BNE @not_music_playmultispeed
	JMP _music_playmultispeed

@not_music_playmultispeed:
	CMP #music_fade_in_out
	BNE @not_music_fade_in_out
	JMP _music_fade_in_out

@not_music_fade_in_out:
	CMP #mute_sfx
	BNE @not_mute_sfx
	LDA #$01
	STA z:zplayback_flag
	LDA #$00
	STA z:zaudio_ram_pointers
	JMP _mute_sfx

@not_mute_sfx:
	CMP #mute_music
	BNE @not_mute_music
	LDA #$01
	STA z:zplayback_flag
	LDA #$00
	STA z:zaudio_ram_pointers
	JMP _mute_music

@not_mute_music:
	ASL
	TAX
	LDA track_pointers, X
	STA z:ztrack_pointers
	LDA track_pointers + 1, X
	STA z:ztrack_pointers + 1
	LDY #$00
	LDA (ztrack_pointers), Y
	TAX
	AND #%00001111
	BEQ @is_sfx
	LDA z:zaudio_header
	AND #%00001111
	STA z:zaudio_E5
	CPX z:zaudio_E5
	BCS @is_music
	RTS

@is_music:
	STX z:zaudio_E5
	LDA z:zaudio_header
	AND #%11110000
	ORA z:zaudio_E5
	STA z:zaudio_header
	LDA #$01
	STA z:zplayback_flag
	LDA #$00
	STA z:zaudio_ram_pointers
	LDA #$00
	STA z:zmusic_playmultispeed
	STA z:zfade_in_out_rate
	LDA #$04
	STA z:zaudio_E5
	LDA #$01

@mainloop:
	CLC
	ADC z:ztrack_pointers
	STA z:ztrack_pointers
	LDA #$00
	ADC z:ztrack_pointers + 1
	STA z:ztrack_pointers + 1
	LDX z:zaudio_ram_pointers
	LDY #$00

@channel_pointers_loop:
	LDA (ztrack_pointers), Y
	STA aaudio_ram, X
	INX
	INY
	CPY #$02
	BNE @channel_pointers_loop
	LDY #$0E
	LDA #$00

@init_loop:
	STA aaudio_ram, X
	INX
	DEY
	BNE @init_loop
	LDA z:zsfx_channel
	LSR
	BCS @skip_1
	JSR _audio_init_common

@skip_1:
	JSR _redirect_channel_ram_pointers_with_sfx
	DEC z:zaudio_E5
	BEQ @done
	LDA #$02
	JMP @mainloop

@done:
	LDY #$02
	LDA (ztrack_pointers), Y
	STA amodulation_pointers
	INY
	LDA (ztrack_pointers), Y
	STA amodulation_pointers + 1
	JSR _init_sfx_channel
	LDA #$00
	STA z:zplayback_flag
	RTS

@is_sfx:
	LDA z:zaudio_header
	AND #%11110000
	STA z:zaudio_E5
	CPX z:zaudio_E5
	BCS @init_sfx
	RTS

@init_sfx:
	STX z:zaudio_E5
	LDA z:zaudio_header
	AND #%00001111
	ORA z:zaudio_E5
	STA z:zaudio_header
	LDA #$01
	STA z:zplayback_flag
	LDA #$00
	STA z:zaudio_ram_pointers
	LDX #$00
	LDA #$02
	CLC
	ADC z:ztrack_pointers
	STA z:zsfx_pointers
	TXA
	ADC z:ztrack_pointers + 1
	STA z:zsfx_pointers + 1
	STX z:zsfx_frame
	STX z:zsfx_loop
	LDY #$01
	LDA (ztrack_pointers), Y
	AND #%00001111
	TAX
	ORA z:zsfx_channel
	PHA
	STX z:zsfx_channel
	LDA #$04
	STA z:zaudio_E5
	LDA #$02
	STA z:zsfx_apu_register_index

@mm2_loop:
	PLA
	LSR
	PHA
	BCC @skip_2
	JSR _audio_init_common
	LDA z:zsfx_channel
	LSR
	BCS @skip_2
	JSR _handle_sfx_mute_channel

@skip_2:
	JSR _redirect_channel_ram_pointers_with_sfx
	LDA #$04
	CLC
	ADC z:zsfx_apu_register_index
	STA z:zsfx_apu_register_index
	DEC z:zaudio_E5
	BNE @mm2_loop
	JSR _init_sfx_channel
	LDA z:zsfx_channel
	STA z:zundo_sfx_channel
	PLA
	LDA #$00
	STA z:zplayback_flag
	RTS

_music_playmultispeed:
	INY
	STY z:zmusic_playmultispeed
	RTS

_music_fade_in_out:
	STY z:zfade_in_out_rate
	LDA #$01
	STA z:zfade_in_out_level
	LDA z:zaudio_frame
	AND #%00000001
	STA z:zaudio_frame
	RTS

_mute_sfx:
	LDA z:zaudio_header
	AND #%00001111
	STA z:zaudio_header
	LDA #$04
	STA z:zaudio_E5
	LDA #$02
	STA z:zsfx_apu_register_index

@mm2_loop:
	LDA z:zsfx_channel
	LSR
	BCC @skip
	JSR _audio_init_common
	JSR _handle_sfx_mute_channel

@skip:
	JSR _redirect_channel_ram_pointers_with_sfx
	LDA #$04
	CLC
	ADC z:zsfx_apu_register_index
	STA z:zsfx_apu_register_index
	DEC z:zaudio_E5
	BNE @mm2_loop
	LDA #$00
	STA z:zsfx_channel
	STA z:zundo_sfx_channel
	LDA #$00
	STA z:zplayback_flag
	RTS

_handle_sfx_mute_channel:
	LDA z:zaudio_ram_pointers
	CLC
	ADC #$0A
	TAX
	LDA aaudio_ram, X
	ORA aaudio_ram + 1, X
	BNE _handle_sfx_mute_modulator
	LDY z:zaudio_E5
	LDX z:zsfx_apu_register_index
	JSR _init_channel
	LDX z:zaudio_ram_pointers
	LDA aaudio_ram, X
	ORA aaudio_ram + 1, X
	BNE _handle_sfx_mute_modulator
	RTS

_mute_music:
	LDA z:zaudio_header
	AND #%11110000
	STA z:zaudio_header
	LDA #$00
	STA z:zmusic_playmultispeed
	STA z:zfade_in_out_rate
	LDA #$04
	STA z:zaudio_E5

@mm2_loop:
	LDA #$00
	LDX z:zaudio_ram_pointers
	STA aaudio_ram, X
	STA aaudio_ram + 1, X
	JSR _redirect_channel_ram_pointers
	DEC z:zaudio_E5
	BNE @mm2_loop
	LDA #$00
	STA z:zplayback_flag
	RTS

_audio_init_common:
	LDY #$0F
	LDA #$10
	CLC
	ADC z:zaudio_ram_pointers
	TAX
	LDA #$00

@mm2_loop:
	STA aaudio_ram, X
	INX
	DEY
	BNE @mm2_loop
	RTS

_handle_sfx_mute_modulator:
	LDA z:zaudio_E5
	PHA
	LDA z:zsfx_apu_register_index
	PHA
	LDA amodulation_pointers
	STA z:zaudio_E5
	LDA amodulation_pointers + 1
	STA z:zsfx_apu_register_index
	LDA z:zaudio_ram_pointers
	CLC
	ADC #$06
	TAX
	LDA aaudio_ram, X
	AND #%00011111
	BEQ @zmodulator
	TAY
	LDA #$00

@loop_multi4:
	CLC
	ADC #$04
	DEY
	BNE @loop_multi4

@zmodulator:
	TAY
	TXA
	CLC
	ADC #$0E
	TAX
	LDA #$04

@mm2_loop:
	PHA
	LDA (zaudio_E5), Y
	STA aaudio_ram, X
	INY
	INX
	PLA
	SEC
	SBC #$01
	BNE @mm2_loop
	PLA
	STA z:zsfx_apu_register_index
	PLA
	STA z:zaudio_E5
	RTS

_redirect_channel_ram_pointers_with_sfx:
	LSR z:zsfx_channel
	BCC _redirect_channel_ram_pointers
	LDA z:zsfx_channel
	ORA #%10000000
	STA z:zsfx_channel

_redirect_channel_ram_pointers:
	LDA #$1F
	CLC
	ADC z:zaudio_ram_pointers
	STA z:zaudio_ram_pointers
	RTS

_init_sfx_channel:
	LSR z:zsfx_channel
	LSR z:zsfx_channel
	LSR z:zsfx_channel
	LSR z:zsfx_channel
	RTS

_init_channel:
	CPY #$01
	BEQ @is_noise
	LDA #$00
	JSR ::MegaManAudioWrite0
	JSR ::MegaManAudioWrite1
	RTS

@is_noise:
	LDA #$07
	JSR ::MegaManAudioStatus
	RTS

_audio_processing:
	INC z:zaudio_frame
	LDA z:zplayback_flag
	BEQ @process
	RTS

@process:
	LDX #$00
	LDY #>Mm2AudioRam
	STX z:zaudio_ram_pointers
	STY z:zaudio_ram_pointers + 1
	LDA #$00
	STA z:zmusic_apu_register_index
	LDA #$04
	STA z:zmusic_channel

@mainloop:
	LDA #$01
	LDY #$18
	CLC
	ADC (zaudio_ram_pointers), Y
	STA (zaudio_ram_pointers), Y
	LDA #$01
	LDY #$1D
	CLC
	ADC (zaudio_ram_pointers), Y
	STA (zaudio_ram_pointers), Y
	LDA z:zundo_sfx_channel
	LSR
	BCC @skip_1
	JSR _handle_sfx

@skip_1:
	LDA z:zpause
	LSR
	BCC @unpause
	JMP @skip_2

@unpause:
	LDY #$00
	LDA (zaudio_ram_pointers), Y
	INY
	ORA (zaudio_ram_pointers), Y
	BEQ @skip_2
	LDA #$01
	LDY #$0E
	CLC
	ADC (zaudio_ram_pointers), Y
	STA (zaudio_ram_pointers), Y
	JSR _music_playingmulticheck
	JMP @done_1

@skip_2:
	LDA z:zundo_sfx_channel
	LSR
	BCS @done_1
	LDX z:zmusic_apu_register_index
	INX
	INX
	LDY z:zmusic_channel
	JSR _init_channel

@done_1:
	LSR z:zundo_sfx_channel
	BCC @skip_3
	LDA z:zundo_sfx_channel
	ORA #%10000000
	STA z:zundo_sfx_channel

@skip_3:
	DEC z:zmusic_channel
	BEQ @done_2
	LDA #$04
	CLC
	ADC z:zmusic_apu_register_index
	STA z:zmusic_apu_register_index
	LDA #$1F
	CLC
	ADC z:zaudio_ram_pointers
	STA z:zaudio_ram_pointers
	LDA #$00
	ADC z:zaudio_ram_pointers + 1
	STA z:zaudio_ram_pointers + 1
	JMP @mainloop

@done_2:
	LDA z:zfade_in_out_rate
	AND #%01111111
	BEQ @skip_4
	CMP z:zaudio_frame
	BNE @skip_4
	LDA z:zaudio_frame
	AND #%00000001
	STA z:zaudio_frame
	INC z:zfade_in_out_level
	LDA #$10
	CMP z:zfade_in_out_level
	BNE @skip_4
	LDA z:zfade_in_out_rate
	BMI @fade_out
	LDA #$00
	STA z:zfade_in_out_rate

@fade_out:
	LDA #$0F
	STA z:zfade_in_out_level

@skip_4:
	LDA z:zsfx_frame
	BEQ @zframe
	DEC z:zsfx_frame

@zframe:
	LSR z:zundo_sfx_channel
	LSR z:zundo_sfx_channel
	LSR z:zundo_sfx_channel
	LSR z:zundo_sfx_channel
	RTS

_handle_played:
	LDY #$0C
	LDA (zaudio_ram_pointers), Y
	LDY #$02
	CPY z:zmusic_channel
	BEQ @is_triangle_1
	AND #%00001111

@is_triangle_1:
	STA z:zaudio_F4
	LDA z:zfade_in_out_rate
	AND #%01111111
	BEQ @handle_fade_in_out_done
	LDA z:zfade_in_out_level
	LDY #$02
	CPY z:zmusic_channel
	BNE @not_triangle
	LDX #$0C

@loop_1:
	CLC
	ADC z:zfade_in_out_level
	DEX
	BNE @loop_1

@not_triangle:
	TAY
	LDA z:zfade_in_out_rate
	BMI @fade_out
	LDX #$FF

@loop_2:
	INX
	CPX z:zaudio_F4
	BEQ @handle_fade_in_out_done
	DEY
	BNE @loop_2
	STX z:zaudio_F4
	JMP @handle_fade_in_out_done

@fade_out:
@loop_3:
	DEC z:zaudio_F4
	BEQ @handle_fade_in_out_done
	DEY
	BNE @loop_3

@handle_fade_in_out_done:
	LDA #$02
	CMP z:zmusic_channel
	BEQ @is_triangle_2
	LDY #$0D
	LDA (zaudio_ram_pointers), Y
	TAX
	AND #%01111111
	BEQ @zframe
	INY
	CMP (zaudio_ram_pointers), Y
	BEQ @eframe
	INY
	LDA (zaudio_ram_pointers), Y
	AND #%00001111
	JMP @compare_volume

@eframe:
	LDA #$00
	STA (zaudio_ram_pointers), Y
	INY
	LDA (zaudio_ram_pointers), Y
	LSR
	LSR
	LSR
	LSR
	STA z:zaudio_F5
	TXA
	BPL @increase
	LDA #$00
	SEC
	SBC z:zaudio_F5
	STA z:zaudio_F5

@increase:
	LDA (zaudio_ram_pointers), Y
	AND #%00001111
	CLC
	ADC z:zaudio_F5
	BPL @compare_volume
	LDA #$00
	JMP @s_or_negative

@compare_volume:
	CMP z:zaudio_F4
	BCC @s_or_negative
	LDA z:zaudio_F4

@s_or_negative:
	STA z:zaudio_F4
	LDA (zaudio_ram_pointers), Y
	AND #%11110000
	ORA z:zaudio_F4
	STA (zaudio_ram_pointers), Y

@is_triangle_2:
@zframe:
	LDA z:zundo_sfx_channel
	LSR
	BCS @skip
	LDA #$0C
	STA z:zaudio_F5
	JMP _handle_modulator_volume_envelope

@skip:
	LDA #$09
	STA z:zaudio_F5
	JMP _pitch_envelope_common

_handle_modulator_volume_envelope:
	LDY #$16
	LDA (zaudio_ram_pointers), Y
	AND #%01111111
	BEQ @le
	LDY #$1D
	CMP (zaudio_ram_pointers), Y
	BEQ @eframe
	JMP @compare_volume

@eframe:
	LDA #$00
	STA (zaudio_ram_pointers), Y
	LDY #$17
	LDA (zaudio_ram_pointers), Y
	LDY #$1E
	CLC
	ADC (zaudio_ram_pointers), Y
	BEQ @zvolume
	BPL @not_volume_negative

@zvolume:
	LDA #$01
	STA (zaudio_ram_pointers), Y
	JMP @continue

@not_volume_negative:
	STA (zaudio_ram_pointers), Y
	CMP #$10
	BCC @compare_volume
	LDA #$0F
	STA (zaudio_ram_pointers), Y

@continue:
	LDA #$00
	LDY #$17
	SEC
	SBC (zaudio_ram_pointers), Y
	STA (zaudio_ram_pointers), Y

@compare_volume:
	LDY #$1E
	LDA (zaudio_ram_pointers), Y
	CMP z:zaudio_F4
	BCS @le
	STA z:zaudio_F4

@le:
	LDY #$02
	CPY z:zmusic_channel
	BEQ @is_triangle
	LDA z:zaudio_F5
	AND #%01111111
	TAY
	LDA (zaudio_ram_pointers), Y
	AND #%11110000
	ORA z:zaudio_F4
	STA z:zaudio_F4

@is_triangle:
	LDX z:zmusic_apu_register_index
	LDA z:zaudio_F4
	JSR ::MegaManAudioWrite0
	LDA z:zaudio_F5
	BPL @not_sfx
	LDA #$10 | 1 << 7
	STA z:zaudio_F5
	JMP _pitch_envelope_common

@not_sfx:
	LDA #$09
	STA z:zaudio_F5

_pitch_envelope_common:
	LDA z:zaudio_F5
	AND #%01111111
	TAY
	LDX #$00
	LDA (zaudio_ram_pointers), Y
	BEQ @zpitch_envelope
	BPL @not_pitch_envelope_negative
	DEX

@not_pitch_envelope_negative:
	INY
	CLC
	ADC (zaudio_ram_pointers), Y
	STA (zaudio_ram_pointers), Y
	TXA
	INY
	ADC (zaudio_ram_pointers), Y
	STA (zaudio_ram_pointers), Y

@zpitch_envelope:
	LDA z:zaudio_F5
	BMI @handle_pitch_bend
	LDA z:zundo_sfx_channel
	LSR
	BCC @handle_pitch_bend
	RTS

@handle_pitch_bend:
	LDY #$14
	LDA (zaudio_ram_pointers), Y
	AND #%01111111
	BNE @nz
	JMP @skip_or_handle_common

@nz:
	LDY #$18
	CMP (zaudio_ram_pointers), Y
	BEQ @eframe
	JMP @skip_or_handle_common

@eframe:
	LDA #$00
	STA (zaudio_ram_pointers), Y
	TAX
	LDY #$15
	LDA (zaudio_ram_pointers), Y
	ROL
	ROL
	ROL
	ROL
	AND #%00000111
	STA z:zaudio_F4
	LDY #$19
	LDA (zaudio_ram_pointers), Y
	ASL
	BCC @pitch_down
	LDA #$00
	SEC
	SBC z:zaudio_F4
	STA z:zaudio_F4
	DEX

@pitch_down:
	LDA z:zaudio_F4
	CLC
	LDY #$1A
	ADC (zaudio_ram_pointers), Y
	STA (zaudio_ram_pointers), Y
	INY
	TXA
	ADC (zaudio_ram_pointers), Y
	STA (zaudio_ram_pointers), Y
	LDY #$15
	LDA (zaudio_ram_pointers), Y
	AND #%00011111
	STA z:zaudio_F4
	LDY #$19
	LDA (zaudio_ram_pointers), Y
	CLC
	ADC #$01
	STA (zaudio_ram_pointers), Y
	AND #%01111111
	CMP z:zaudio_F4
	BNE @skip_or_handle_common
	LDA (zaudio_ram_pointers), Y
	AND #%10000000
	STA (zaudio_ram_pointers), Y
	LDY #$14
	LDA (zaudio_ram_pointers), Y
	ASL
	BCS @change_pitch_direction
	LDA (zaudio_ram_pointers), Y
	ORA #%10000000
	STA (zaudio_ram_pointers), Y
	LDY #$19
	LDA (zaudio_ram_pointers), Y
	BPL @change_pitch_up
	AND #%01111111
	STA (zaudio_ram_pointers), Y
	JMP @skip_or_handle_common

@change_pitch_up:
	ORA #%10000000
	STA (zaudio_ram_pointers), Y
	JMP @skip_or_handle_common

@change_pitch_direction:
	LDA (zaudio_ram_pointers), Y
	AND #%01111111
	STA (zaudio_ram_pointers), Y

@skip_or_handle_common:
	LDA z:zaudio_F5
	AND #%01111111
	STA z:zaudio_F5
	INC z:zaudio_F5
	LDY #$1A
	LDA (zaudio_ram_pointers), Y
	LDY z:zaudio_F5
	CLC
	ADC (zaudio_ram_pointers), Y
	TAX
	LDY #$1B
	LDA (zaudio_ram_pointers), Y
	INC z:zaudio_F5
	LDY z:zaudio_F5
	ADC (zaudio_ram_pointers), Y
	TAY
	LDA #$01
	CMP z:zmusic_channel
	BNE @not_noise
	LDA #$0F
	JSR ::MegaManAudioStatus
	TXA
	AND #%00001111
	TAX
	INC z:zaudio_F5
	LDY z:zaudio_F5
	LDA (zaudio_ram_pointers), Y
	AND #%10000000
	STA z:zaudio_F4
	TXA
	ORA z:zaudio_F4
	TAX
	LDY #$00

@not_noise:
	TXA
	LDX z:zmusic_apu_register_index
	INX
	INX
	JSR ::MegaManAudioWrite0
	TYA
	LDY #$1C
	CMP (zaudio_ram_pointers), Y
	BNE @done
	RTS

@done:
	STA (zaudio_ram_pointers), Y
	ORA #$08
	JSR ::MegaManAudioWrite1
	RTS

_break_frame:
	LDY #$01
	CPY z:zmusic_channel
	BNE @not_noise
	LDA #$07
	JSR ::MegaManAudioStatus
	RTS

@not_noise:
	LDA #$00
	LDX z:zmusic_apu_register_index
	INX
	INX
	JSR ::MegaManAudioWrite0
	JSR ::MegaManAudioWrite1
	RTS

_play_note_with_modulator:
	LDY #$14
	LDA (zaudio_ram_pointers), Y
	AND #%01111111
	STA (zaudio_ram_pointers), Y
	LDY #$16
	LDA (zaudio_ram_pointers), Y
	ASL
	BCC @increase
	LDY z:zaudio_F4
	LDA (zaudio_ram_pointers), Y
	LDX #$02
	CPX z:zmusic_channel
	BEQ @is_triangle
	AND #%00001111

@is_triangle:
	LDY #$1E
	STA (zaudio_ram_pointers), Y

@increase:
	LDX #$06
	LDA #$00
	LDY #$18

@mm2_loop:
	STA (zaudio_ram_pointers), Y
	INY
	DEX
	BNE @mm2_loop
	LDA #$FF
	LDY #$1C
	STA (zaudio_ram_pointers), Y
	RTS

_play_note_with_tied:
	LDY #$1C
	LDA (zaudio_ram_pointers), Y
	PHA
	JSR _play_note_with_modulator
	PLA
	LDY #$1C
	STA (zaudio_ram_pointers), Y
	RTS

_audio_cmd_jmp:
	TXA
	ASL
	TAY
	INY
	PLA
	STA z:zaudio_F4
	PLA
	STA z:zaudio_F5
	LDA (zaudio_F4), Y
	TAX
	INY
	LDA (zaudio_F4), Y
	STA z:zaudio_F5
	STX z:zaudio_F4
	JMP (zaudio_F4)

_handle_sfx:
	LDA z:zsfx_frame
	BNE @nz
	JMP _read_sfx_data

@nz:
	LDY #$11
	LDA (zaudio_ram_pointers), Y
	INY
	ORA (zaudio_ram_pointers), Y
	BNE @undone
	RTS

@undone:
	INY
	LDA (zaudio_ram_pointers), Y
	LDY #$02
	CPY z:zmusic_channel
	BEQ @is_triangle
	AND #%00001111

@is_triangle:
	STA z:zaudio_F4
	LDA #$13 | 1 << 7
	STA z:zaudio_F5
	JMP _handle_modulator_volume_envelope

_read_sfx_data:
	JSR _read_next_sfx_data
	ASL
	BCS @is_note
	JMP _sfx_cmd

@is_note:
	TXA
	AND #%00001111
	CMP #$0F
	BNE @not_note_tied
	JSR _read_next_sfx_data
	JMP _play_note_with_tied

@not_note_tied:
	AND #%00000111
	STA z:zaudio_F4
	JSR _read_next_sfx_data
	LDY #$11
	STA (zaudio_ram_pointers), Y
	INY
	LDA z:zaudio_F4
	STA (zaudio_ram_pointers), Y
	LDA #$13
	STA z:zaudio_F4
	JSR _play_note_with_modulator
	JMP _break_frame

_sfx_cmd:
	JSR _audio_cmd_jmp

	.WORD _sfx_cmd_frame
	.WORD _sfx_cmd_pitch_envelope
	.WORD _sfx_cmd_duty_cycle
	.WORD _sfx_cmd_volume
	.WORD _sfx_cmd_loop
	.WORD _sfx_cmd_modulator
	.WORD _sfx_cmd_end

_sfx_cmd_frame:
	JSR _read_next_sfx_data
	STA z:zsfx_frame
	JMP _read_sfx_data

_sfx_cmd_pitch_envelope:
	JSR _read_next_sfx_data
	LDY #$10
	STA (zaudio_ram_pointers), Y
	JMP _read_sfx_data

_sfx_cmd_duty_cycle:
	JSR _read_next_sfx_data
	STA z:zaudio_F4
	LDY #$13
	LDA (zaudio_ram_pointers), Y
	AND #%00111111
	ORA z:zaudio_F4
	JMP _sfx_cmd_write_duty_cycle_volume_common

_sfx_cmd_volume:
	JSR _read_next_sfx_data
	LDY #$02
	CPY z:zmusic_channel
	BEQ @is_triangle
	STA z:zaudio_F4
	LDY #$13
	LDA (zaudio_ram_pointers), Y
	AND #%11000000
	ORA z:zaudio_F4

@is_triangle:
_sfx_cmd_write_duty_cycle_volume_common:
	LDY #$13
	STA (zaudio_ram_pointers), Y
	JMP _read_sfx_data

_sfx_cmd_loop:
	JSR _read_next_sfx_data
	TXA
	BEQ @infinity_loop
	CPX z:zsfx_loop
	BEQ @regular_loop
	INC z:zsfx_loop

@infinity_loop:
	JSR _read_next_sfx_data
	STA z:zaudio_F4
	JSR _read_next_sfx_data
	STA z:zsfx_pointers + 1
	LDA z:zaudio_F4
	STA z:zsfx_pointers
	JMP _read_sfx_data

@regular_loop:
	LDA #$00
	STA z:zsfx_loop
	LDA #$02
	CLC
	ADC z:zsfx_pointers
	STA z:zsfx_pointers
	LDA #$00
	ADC z:zsfx_pointers + 1
	STA z:zsfx_pointers + 1
	JMP _read_sfx_data

_sfx_cmd_modulator:
	LDA #$14
	STA z:zaudio_F4

@mm2_loop:
	JSR _read_next_sfx_data
	LDY z:zaudio_F4
	STA (zaudio_ram_pointers), Y
	INC z:zaudio_F4
	LDY z:zaudio_F4
	CPY #$18
	BNE @mm2_loop
	JMP _read_sfx_data

_sfx_cmd_end:
	LDA z:zsfx_pointers
	SEC
	SBC #$01
	STA z:zsfx_pointers
	LDA z:zsfx_pointers + 1
	SBC #$00
	STA z:zsfx_pointers + 1
	LDA z:zaudio_header
	AND #%00001111
	STA z:zaudio_header
	LDA #$00
	STA z:zsfx_channel
	LDA z:zundo_sfx_channel
	AND #%11111110
	STA z:zundo_sfx_channel
	LDY #$0A
	LDA (zaudio_ram_pointers), Y
	INY
	ORA (zaudio_ram_pointers), Y
	BNE @return_play_music
	LDX z:zmusic_apu_register_index
	INX
	INX
	LDY z:zmusic_channel
	JSR _init_channel
	LDY #$00
	LDA (zaudio_ram_pointers), Y
	INY
	ORA (zaudio_ram_pointers), Y
	BNE @return_play_music
	RTS

@return_play_music:
	LDY #$06
	LDA (zaudio_ram_pointers), Y
	AND #%00011111
	TAX
	JSR _handle_modulator_data
	LDA #$0C
	STA z:zaudio_F4
	JMP _play_note_with_modulator

_read_next_sfx_data:
	LDY #$00
	LDA (zsfx_pointers), Y
	TAX
	LDA #$01
	CLC
	ADC z:zsfx_pointers
	STA z:zsfx_pointers
	LDA #$00
	ADC z:zsfx_pointers + 1
	STA z:zsfx_pointers + 1
	TXA
	RTS

_music_playingmulticheck:
	LDA z:zmusic_playmultispeed
	BEQ _music_playing

@mm2_loop:
	PHA
	JSR _music_playing
	PLA
	SEC
	SBC #$01
	BNE @mm2_loop
	RTS

_music_playing:
	LDY #$05
	LDA (zaudio_ram_pointers), Y
	ASL
	BCC _play_note
	LDA z:zaudio_frame
	AND #%00000001
	BEQ _play_note
	JSR _play_note

_play_note:
	LDY #$02
	LDA (zaudio_ram_pointers), Y
	INY
	ORA (zaudio_ram_pointers), Y
	BEQ @done
	LDX #$FF
	DEY
	LDA (zaudio_ram_pointers), Y
	SEC
	SBC #$04
	STA (zaudio_ram_pointers), Y
	TXA
	INY
	ADC (zaudio_ram_pointers), Y
	STA (zaudio_ram_pointers), Y
	DEY
	ORA (zaudio_ram_pointers), Y
	BEQ @done
	LDY #$0A
	LDA (zaudio_ram_pointers), Y
	INY
	ORA (zaudio_ram_pointers), Y
	BNE @not_rest
	RTS

@not_rest:
	JMP _handle_played

@done:
	LDY #$05
	LDA (zaudio_ram_pointers), Y
	AND #%01111111
	STA (zaudio_ram_pointers), Y

_read_music_data:
	JSR _read_next_music_data
	AND #%11110000
	BNE @not_cmd
	JMP _music_cmd

@not_cmd:
	CMP #$20
	BNE @not_note_tied
	TXA
	AND #%00000111
	PHA
	JSR _read_music_data
	PLA
	JMP _handle_note_tied

@not_note_tied:
	CMP #$30
	BNE @not_triplet_note_set
	JMP _handle_triplet_note_flag

@not_triplet_note_set:
	TXA
	ROL
	ROL
	ROL
	ROL
	AND #%00000111
	TAY
	LDA _regular_note_length_table, Y
	JSR _calc_note_length

_handle_note_common:
	LDY #$06
	LDA (zaudio_ram_pointers), Y
	AND #%11100000
	BEQ @no_note_tied
	SEC
	SBC #$20
	STA z:zaudio_F4
	LDA (zaudio_ram_pointers), Y
	AND #%00011111
	ORA z:zaudio_F4
	STA (zaudio_ram_pointers), Y
	LDA z:zundo_sfx_channel
	LSR
	BCC @sfx_channel_not_used_1
	RTS

@sfx_channel_not_used_1:
	JMP _play_note_with_tied

@no_note_tied:
	TXA
	AND #%00011111
	BNE @not_rest
	TAX
	JMP @skip_read_freq_table

@not_rest:
	LDY #$01
	CPY z:zmusic_channel
	BNE @not_noise
	LDX #$00
	JMP @skip_read_freq_table

@not_noise:
	ASL
	LDY #$07
	CLC
	ADC (zaudio_ram_pointers), Y
	STA z:zaudio_F4
	LDA #$00
	INY
	ADC (zaudio_ram_pointers), Y
	STA z:zaudio_F5
	LDY #$01
	LDA (zaudio_F4), Y
	TAX
	DEY
	LDA (zaudio_F4), Y

@skip_read_freq_table:
	LDY #$0A
	STA (zaudio_ram_pointers), Y
	INY
	TXA
	STA (zaudio_ram_pointers), Y
	LDY #$0D
	LDA (zaudio_ram_pointers), Y
	STA z:zaudio_F4
	AND #%01111111
	BEQ @zframe
	JSR _init_volume_envelope

@zframe:
	LDA z:zundo_sfx_channel
	LSR
	BCC @sfx_channel_not_used_2
	RTS

@sfx_channel_not_used_2:
	LDA #$0C
	STA z:zaudio_F4
	JSR _play_note_with_modulator
	JMP _break_frame

_handle_note_tied:
	ROR
	ROR
	ROR
	ROR
	AND #%11100000
	STA z:zaudio_F4
	LDY #$06
	LDA (zaudio_ram_pointers), Y
	AND #%00011111
	ORA z:zaudio_F4
	STA (zaudio_ram_pointers), Y
	RTS

_handle_triplet_note_flag:
	LDA #%10000000
	LDY #$05
	ORA (zaudio_ram_pointers), Y
	STA (zaudio_ram_pointers), Y
	JMP _read_music_data

_music_cmd:
	JSR _audio_cmd_jmp

	.WORD _cmd_tempo
	.WORD _cmd_pitch_envelope
	.WORD _cmd_duty_cycle
	.WORD _cmd_volume
	.WORD _cmd_loop
	.WORD _cmd_base_note
	.WORD _cmd_dotted_note_set
	.WORD _cmd_volume_envelope
	.WORD _cmd_modulator
	.WORD _cmd_music_end

_cmd_tempo:
	JSR _read_next_music_data
	LDY #$04
	STA (zaudio_ram_pointers), Y
	JMP _read_music_data

_cmd_pitch_envelope:
	JSR _read_next_music_data
	LDY #$09
	STA (zaudio_ram_pointers), Y
	JMP _read_music_data

_cmd_duty_cycle:
	JSR _read_next_music_data
	STA z:zaudio_F4
	LDY #$0C
	LDA (zaudio_ram_pointers), Y
	AND #%00111111
	ORA z:zaudio_F4
	JMP _cmd_write_common

_cmd_volume:
	JSR _read_next_music_data
	LDY #$02
	CPY z:zmusic_channel
	BEQ _cmd_write_common
	STA z:zaudio_F4
	LDY #$0C
	LDA (zaudio_ram_pointers), Y
	AND #%11000000
	ORA z:zaudio_F4

_cmd_write_common:
	LDY #$0C
	STA (zaudio_ram_pointers), Y
	JMP _read_music_data

_cmd_loop:
	JSR _read_next_music_data
	TXA
	BEQ @infinity_loop
	LDY #$05
	LDA (zaudio_ram_pointers), Y
	AND #%01111111
	STA z:zaudio_F4
	CPX z:zaudio_F4
	BEQ @regular_loop
	INC z:zaudio_F4
	LDA (zaudio_ram_pointers), Y
	AND #%10000000
	ORA z:zaudio_F4
	STA (zaudio_ram_pointers), Y

@infinity_loop:
	JSR _read_next_music_data
	PHA
	JSR _read_next_music_data
	PLA
	LDY #$00
	STA (zaudio_ram_pointers), Y
	INY
	TXA
	STA (zaudio_ram_pointers), Y
	JMP _read_music_data

@regular_loop:
	LDA (zaudio_ram_pointers), Y
	AND #%10000000
	STA (zaudio_ram_pointers), Y
	LDY #$00
	LDA #$02
	CLC
	ADC (zaudio_ram_pointers), Y
	STA (zaudio_ram_pointers), Y
	INY
	LDA #$00
	ADC (zaudio_ram_pointers), Y
	STA (zaudio_ram_pointers), Y
	JMP _read_music_data

_cmd_base_note:
	JSR _read_next_music_data
	LDX #<_base_note_table
	LDY #>_base_note_table
	STX z:zaudio_F4
	STY z:zaudio_F5
	ASL
	LDY #$07
	CLC
	ADC z:zaudio_F4
	STA (zaudio_ram_pointers), Y
	LDA #$00
	ADC z:zaudio_F5
	INY
	STA (zaudio_ram_pointers), Y
	JMP _read_music_data

_cmd_dotted_note_set:
	JSR _read_next_music_data
	ROL
	ROL
	ROL
	ROL
	AND #%00000111
	TAY
	LDA _dotted_note_length_table, Y
	JSR _calc_note_length
	JMP _handle_note_common

_cmd_volume_envelope:
	JSR _read_next_music_data
	LDY #$0D
	STA (zaudio_ram_pointers), Y
	PHA
	JSR _read_next_music_data
	LDY #$0F
	STA (zaudio_ram_pointers), Y
	PLA
	STA z:zaudio_F4
	AND #%01111111
	BEQ @zframe
	JSR _init_volume_envelope

@zframe:
	JMP _read_music_data

_init_volume_envelope:
	LDA #$00
	LDY #$0E
	STA (zaudio_ram_pointers), Y
	LDA z:zaudio_F4
	BPL @increase
	LDA #$0F
	JMP @decay

@increase:
	LDA #$00

@decay:
	STA z:zaudio_F4
	LDY #$0F
	LDA (zaudio_ram_pointers), Y
	AND #%11110000
	ORA z:zaudio_F4
	STA (zaudio_ram_pointers), Y
	RTS

_cmd_modulator:
	JSR _read_next_music_data
	STA z:zaudio_F4
	LDY #$06
	LDA (zaudio_ram_pointers), Y
	AND #%11100000
	ORA z:zaudio_F4
	STA (zaudio_ram_pointers), Y
	LDA z:zundo_sfx_channel
	LSR
	BCS @skip
	JSR _handle_modulator_data

@skip:
	JMP _read_music_data

_handle_modulator_data:
	TXA
	BEQ @zmodulator
	LDA #$00

@loop_multi4:
	CLC
	ADC #$04
	DEX
	BNE @loop_multi4

@zmodulator:
	CLC
	ADC amodulation_pointers
	STA z:zaudio_F4
	LDA #$00
	ADC amodulation_pointers + 1
	STA z:zaudio_F5
	LDX #$00
	LDY #$14

@mm2_loop:
	LDA (zaudio_F4, X)
	STA (zaudio_ram_pointers), Y
	INY
	CPY #$18
	BNE @undone
	RTS

@undone:
	LDA #$01
	CLC
	ADC z:zaudio_F4
	STA z:zaudio_F4
	LDA #$00
	ADC z:zaudio_F5
	STA z:zaudio_F5
	JMP @mm2_loop

_cmd_music_end:
	LDY #$00
	LDA #$00
	STA (zaudio_ram_pointers), Y
	INY
	STA (zaudio_ram_pointers), Y
	LDA z:zaudio_header
	AND #%11110000
	STA z:zaudio_header
	LDA z:zundo_sfx_channel
	LSR
	BCC @init
	RTS

@init:
	LDX z:zmusic_apu_register_index
	INX
	INX
	LDY z:zmusic_channel
	JMP _init_channel

_read_next_music_data:
	LDY #$00
	LDA (zaudio_ram_pointers), Y
	STA z:zaudio_F4
	INY
	LDA (zaudio_ram_pointers), Y
	STA z:zaudio_F5
	DEY
	LDA (zaudio_F4), Y
	TAX
	LDA #$01
	CLC
	ADC z:zaudio_F4
	STA (zaudio_ram_pointers), Y
	LDA #$00
	ADC z:zaudio_F5
	INY
	STA (zaudio_ram_pointers), Y
	TXA
	RTS

_calc_note_length:
	STA z:zaudio_F4
	LDA #$00
	STA z:zaudio_F5
	LDY #$04
	LDA (zaudio_ram_pointers), Y
	TAY
	LDA #$00

@mm2_loop:
	CLC
	ADC z:zaudio_F4
	BCC @not_9bits
	INC z:zaudio_F5

@not_9bits:
	DEY
	BNE @mm2_loop
	LDY #$02
	STA (zaudio_ram_pointers), Y
	INY
	LDA z:zaudio_F5
	STA (zaudio_ram_pointers), Y
	RTS

_regular_note_length_table:
	.BYTE 0  ;unused
	.BYTE 0  ;unused
	.BYTE 2  ;2
	.BYTE 4  ;4
	.BYTE 8  ;8
	.BYTE 16 ;16
	.BYTE 32 ;32
	.BYTE 64 ;64

_dotted_note_length_table:
	.BYTE 0  ;unused
	.BYTE 0  ;unused
	.BYTE 3  ;2
	.BYTE 6  ;4
	.BYTE 12 ;8
	.BYTE 24 ;16
	.BYTE 48 ;32
	.BYTE 96 ;64

_base_note_table:
	.WORD nC_0
	.WORD nDb0
	.WORD nD_0
	.WORD nEb0
	.WORD nE_0
	.WORD nF_0
	.WORD nGb0
	.WORD nG_0
	.WORD nAb0
	.WORD nA_0
	.WORD nBb0
	.WORD nB_0
	.WORD nC_1
	.WORD nDb1
	.WORD nD_1
	.WORD nEb1
	.WORD nE_1
	.WORD nF_1
	.WORD nGb1
	.WORD nG_1
	.WORD nAb1
	.WORD nA_1
	.WORD nBb1
	.WORD nB_1
	.WORD nC_2
	.WORD nDb2
	.WORD nD_2
	.WORD nEb2
	.WORD nE_2
	.WORD nF_2
	.WORD nGb2
	.WORD nG_2
	.WORD nAb2
	.WORD nA_2
	.WORD nBb2
	.WORD nB_2
	.WORD nC_3
	.WORD nDb3
	.WORD nD_3
	.WORD nEb3
	.WORD nE_3
	.WORD nF_3
	.WORD nGb3
	.WORD nG_3
	.WORD nAb3
	.WORD nA_3
	.WORD nBb3
	.WORD nB_3
	.WORD nC_4
	.WORD nDb4
	.WORD nD_4
	.WORD nEb4
	.WORD nE_4
	.WORD nF_4
	.WORD nGb4
	.WORD nG_4
	.WORD nAb4
	.WORD nA_4
	.WORD nBb4
	.WORD nB_4
	.WORD nC_5
	.WORD nDb5
	.WORD nD_5
	.WORD nEb5
	.WORD nE_5
	.WORD nF_5
	.WORD nGb5
	.WORD nG_5
	.WORD nAb5
	.WORD nA_5
	.WORD nBb5
	.WORD nB_5
	.WORD nC_6
	.WORD nDb6
	.WORD nD_6
	.WORD nEb6
	.WORD nE_6
	.WORD nF_6
	.WORD nGb6
	.WORD nG_6
	.WORD nAb6
	.WORD nA_6
	.WORD nBb6
	.WORD nB_6
	.WORD nC_7
	.WORD nDb7
	.WORD nD_7
	.WORD nEb7
	.WORD nE_7
	.WORD nF_7
	.WORD nGb7
	.WORD nG_7
	.WORD nAb7
	.WORD nA_7
	.WORD nBb7
	.WORD nB_7

;unused
	.BYTE $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
	.BYTE $FF, $FF, $FF

track_pointers:
	.WORD music_flashman
	.WORD music_silence
	.WORD music_silence
	.WORD music_silence
	.WORD music_silence
	.WORD music_silence
	.WORD music_silence
	.WORD music_bubbleman
	.WORD music_silence
	.WORD music_silence
	.WORD music_boss_show
	.WORD music_boss_fighting
	.WORD music_silence
	.WORD music_title
	.WORD music_silence
	.WORD music_game_over
	.WORD music_silence
	.WORD music_silence
	.WORD music_silence
	.WORD music_silence
	.WORD music_silence
	.WORD music_boss_defeated
	.WORD music_silence
	.WORD music_get_weapon
	.WORD music_game_over
	.WORD music_game_over
	.WORD music_game_over
	.WORD music_game_over
	.WORD music_game_over
	.WORD music_game_over
	.WORD music_game_over
	.WORD music_game_over
	.WORD music_game_over
	.WORD music_silence
	.WORD music_silence
	.WORD music_silence
	.WORD sfx_mega_buster
	.WORD music_silence
	.WORD sfx_megaman_hit
	.WORD music_silence
	.WORD sfx_refill
	.WORD sfx_landing
	.WORD music_silence
	.WORD sfx_enemy_hit
	.WORD music_silence
	.WORD sfx_enemy_immune
	.WORD music_silence
	.WORD sfx_select
	.WORD sfx_teleport_in
	.WORD music_silence
	.WORD music_silence
	.WORD music_silence
	.WORD sfx_door
	.WORD sfx_atomic_fire_charge_1
	.WORD sfx_atomic_fire_charge_2
	.WORD sfx_atomic_fire_charge_3
	.WORD sfx_atomic_fire_release
	.WORD music_silence
	.WORD music_silence
	.WORD music_silence
	.WORD music_silence
	.WORD music_silence
	.WORD music_silence
	.WORD music_silence
	.WORD music_silence
	.WORD sfx_death
	.WORD sfx_1up

music_silence: .byte $0f
.word 0,0,0,0,0
music_boss_defeated:
	mm2_music_header
	.WORD music_boss_defeated_pulse_1
	.WORD music_boss_defeated_pulse_2
	.WORD music_boss_defeated_triangle
	.WORD $0000
	.WORD music_boss_defeated_modulator

music_boss_defeated_pulse_1:
	mm2_tempo 6
	mm2_volume 15
	mm2_base_note Eb3
	mm2_volume_envelope volume_decay, 1, 9
	mm2_rest 64
	mm2_note Db4, 4
	mm2_note Db4, 4
	mm2_rest 8
	mm2_note Eb4, 4
	mm2_note Eb4, 4
	mm2_rest 8
	mm2_note E_4, 4
	mm2_note E_4, 4
	mm2_rest 8
	mm2_note Gb4, 4
	mm2_note E_4, 4
	mm2_note Gb4, 4
	mm2_dotted_note_set
	mm2_note Ab4, 64
	mm2_music_end

music_boss_defeated_pulse_2:
	mm2_tempo 6
	mm2_volume 15
	mm2_base_note Eb3
	mm2_volume_envelope volume_decay, 1, 9
	mm2_rest 64
	mm2_note A_3, 4
	mm2_note A_3, 4
	mm2_rest 8
	mm2_note B_3, 4
	mm2_note B_3, 4
	mm2_rest 8
	mm2_note Db4, 4
	mm2_note Db4, 4
	mm2_rest 8
	mm2_note Eb4, 4
	mm2_note Db4, 4
	mm2_note Eb4, 4
	mm2_dotted_note_set
	mm2_note E_4, 64
	mm2_music_end

music_boss_defeated_triangle:
	mm2_tempo 6
	mm2_triangle_note_length $30
	mm2_base_note Eb3
	mm2_pitch_envelope $10
	mm2_note Ab5, 8
	mm2_note Ab5, 8
	mm2_note Ab5, 4
	mm2_note F_5, 4
	mm2_rest 4
	mm2_note Eb5, 8
	mm2_note Eb5, 8
	mm2_note Eb5, 4
	mm2_note Db5, 4
	mm2_rest 4
	mm2_note Bb4, 4
	mm2_rest 4
	mm2_pitch_envelope $00
	mm2_triangle_note_length $81
	mm2_note Gb3, 4
	mm2_note Gb3, 4
	mm2_rest 8
	mm2_note Ab3, 4
	mm2_note Ab3, 4
	mm2_rest 8
	mm2_note A_3, 4
	mm2_note A_3, 4
	mm2_rest 8
	mm2_note B_3, 4
	mm2_note A_3, 4
	mm2_note B_3, 4
	mm2_dotted_note_set
	mm2_note B_3, 64
	mm2_music_end

music_boss_defeated_modulator:
	mm2_modulator_set 0, 0, 0, volume_decay, 0, 0

music_boss_fighting:
	mm2_music_header
	.WORD music_boss_fighting_pulse_1
	.WORD music_boss_fighting_pulse_2
	.WORD music_boss_fighting_triangle
	.WORD music_boss_fighting_noise
	.WORD music_boss_fighting_modulator

music_boss_fighting_pulse_1:
	mm2_tempo 6
	mm2_volume 12
	mm2_duty_cycle 3
	mm2_base_note G_1
	mm2_volume_envelope volume_decay, 1, 96
	mm2_modulator 1
	mm2_note Eb2, 64
	mm2_note Gb2, 64
	mm2_note A_2, 64
	mm2_note C_3, 32
	mm2_note A_2, 4
	mm2_note C_3, 4
	mm2_note Eb3, 4
	mm2_note C_3, 4
	mm2_note Eb3, 4
	mm2_note C_3, 4
	mm2_note Eb3, 4
	mm2_note Gb3, 4
	mm2_modulator 0

@loop_1:
	mm2_volume_envelope volume_decay, 2, 6
	mm2_base_note G_2
	mm2_duty_cycle 3
	mm2_note C_4, 4
	mm2_note C_4, 4
	mm2_rest 4
	mm2_note C_4, 4
	mm2_rest 4
	mm2_note C_4, 4
	mm2_note C_4, 4
	mm2_rest 8
	mm2_note C_4, 4
	mm2_note C_4, 4
	mm2_rest 4
	mm2_note C_4, 4
	mm2_rest 4
	mm2_note C_4, 4
	mm2_note C_4, 4
	mm2_volume_envelope volume_decay, 2, 3
	mm2_note C_4, 8
	mm2_rest 4
	mm2_note C_4, 4
	mm2_rest 16
	mm2_note G_4, 8
	mm2_rest 4
	mm2_note G_4, 4
	mm2_note F_4, 8
	mm2_note G_4, 8
	mm2_volume_envelope volume_decay, 2, 6
	mm2_note Bb3, 4
	mm2_note Bb3, 4
	mm2_rest 4
	mm2_note Bb3, 4
	mm2_rest 4
	mm2_note Bb3, 4
	mm2_note Bb3, 4
	mm2_rest 8
	mm2_note Bb3, 4
	mm2_note Bb3, 4
	mm2_rest 4
	mm2_note Bb3, 4
	mm2_rest 4
	mm2_note Bb3, 4
	mm2_note Bb3, 4
	mm2_volume_envelope volume_decay, 2, 3
	mm2_note Bb3, 8
	mm2_rest 4
	mm2_note Bb3, 4
	mm2_rest 16
	mm2_note G_4, 8
	mm2_rest 4
	mm2_note G_4, 4
	mm2_note F_4, 8
	mm2_note G_4, 8
	mm2_volume_envelope volume_decay, 2, 6
	mm2_note A_3, 4
	mm2_note A_3, 4
	mm2_rest 4
	mm2_note A_3, 4
	mm2_rest 4
	mm2_note A_3, 4
	mm2_note A_3, 4
	mm2_rest 8
	mm2_note A_3, 4
	mm2_note A_3, 4
	mm2_rest 4
	mm2_note A_3, 4
	mm2_rest 4
	mm2_note A_3, 4
	mm2_note A_3, 4
	mm2_volume_envelope volume_decay, 2, 3
	mm2_note A_3, 8
	mm2_rest 4
	mm2_note A_3, 4
	mm2_rest 16
	mm2_note G_4, 8
	mm2_rest 4
	mm2_note G_4, 4
	mm2_note F_4, 8
	mm2_note G_4, 8
	mm2_volume_envelope volume_decay, 2, 6
	mm2_note F_3, 4
	mm2_note F_3, 4
	mm2_rest 4
	mm2_note F_3, 4
	mm2_rest 4
	mm2_note F_3, 4
	mm2_note F_3, 4
	mm2_rest 8
	mm2_note F_3, 4
	mm2_note F_3, 4
	mm2_rest 4
	mm2_note F_3, 4
	mm2_rest 4
	mm2_note F_3, 4
	mm2_note F_3, 4
	mm2_modulator 1
	mm2_note G_3, 16
	mm2_note B_3, 16
	mm2_note D_4, 16
	mm2_note G_4, 16
	mm2_modulator 0
	mm2_loop 0, @loop_1

music_boss_fighting_pulse_2:
	mm2_tempo 6
	mm2_volume 11
	mm2_duty_cycle 0
	mm2_volume_envelope volume_decay, 1, 10
	mm2_base_note G_2
	mm2_note C_3, 16
	mm2_rest 4
	mm2_note A_3, 4
	mm2_note Gb3, 4
	mm2_note Eb3, 4
	mm2_note C_3, 32
	mm2_note Eb3, 16
	mm2_rest 4
	mm2_note C_4, 4
	mm2_note A_3, 4
	mm2_note Gb3, 4
	mm2_note Eb3, 32
	mm2_note Gb3, 16
	mm2_rest 4
	mm2_note Eb4, 4
	mm2_note C_4, 4
	mm2_note A_3, 4
	mm2_note Gb3, 32
	mm2_note A_3, 16
	mm2_rest 4
	mm2_note Gb4, 4
	mm2_note Eb4, 4
	mm2_note A_3, 4
	mm2_note C_4, 32

@loop_1:
	mm2_base_note G_2
	mm2_duty_cycle 3
	mm2_volume_envelope volume_decay, 2, 6
	mm2_note G_3, 4
	mm2_note G_3, 4
	mm2_rest 4
	mm2_note G_3, 4
	mm2_rest 4
	mm2_note G_3, 4
	mm2_note G_3, 4
	mm2_rest 8
	mm2_note G_3, 4
	mm2_note G_3, 4
	mm2_rest 4
	mm2_note G_3, 4
	mm2_rest 4
	mm2_note G_3, 4
	mm2_note G_3, 4
	mm2_volume_envelope volume_decay, 2, 3
	mm2_note G_3, 8
	mm2_rest 4
	mm2_note G_3, 4
	mm2_rest 16
	mm2_note Eb4, 8
	mm2_rest 4
	mm2_note Eb4, 4
	mm2_note D_4, 8
	mm2_note Eb4, 8
	mm2_loop 1, @loop_1
	mm2_duty_cycle 3
	mm2_volume_envelope volume_decay, 2, 6
	mm2_note F_3, 4
	mm2_note F_3, 4
	mm2_rest 4
	mm2_note F_3, 4
	mm2_rest 4
	mm2_note F_3, 4
	mm2_note F_3, 4
	mm2_rest 8
	mm2_note F_3, 4
	mm2_note F_3, 4
	mm2_rest 4
	mm2_note F_3, 4
	mm2_rest 4
	mm2_note F_3, 4
	mm2_note F_3, 4
	mm2_volume_envelope volume_decay, 2, 3
	mm2_note F_3, 8
	mm2_rest 4
	mm2_note F_3, 4
	mm2_rest 16
	mm2_note Eb4, 8
	mm2_rest 4
	mm2_note Eb4, 4
	mm2_note D_4, 8
	mm2_note Eb4, 8
	mm2_volume_envelope volume_decay, 2, 6
	mm2_note D_3, 4
	mm2_note D_3, 4
	mm2_rest 4
	mm2_note D_3, 4
	mm2_rest 4
	mm2_note D_3, 4
	mm2_note D_3, 4
	mm2_rest 8
	mm2_note D_3, 4
	mm2_note D_3, 4
	mm2_rest 4
	mm2_note D_3, 4
	mm2_rest 4
	mm2_note D_3, 4
	mm2_note D_3, 4
	mm2_modulator 1
	mm2_note D_3, 16
	mm2_note G_3, 16
	mm2_note B_3, 16
	mm2_note D_4, 16
	mm2_modulator 0
	mm2_loop 0, @loop_1

music_boss_fighting_triangle:
	mm2_tempo 6
	mm2_triangle_note_length $30
	mm2_base_note G_2

@loop_1:
	mm2_note C_4, 4
	mm2_note C_4, 4
	mm2_note C_4, 4
	mm2_note Bb3, 4
	mm2_loop 13, @loop_1
	mm2_triangle_note_length $20
	mm2_pitch_envelope $15
	mm2_note G_3, 4
	mm2_note G_3, 4
	mm2_note F_3, 4
	mm2_note F_3, 4
	mm2_note Eb3, 4
	mm2_note Eb3, 4
	mm2_note Db3, 4
	mm2_note Db3, 4
	mm2_triangle_note_length $50
	mm2_pitch_envelope $00

@loop_2:
	mm2_triangle_note_length $40
	mm2_note C_4, 4
	mm2_note C_4, 4
	mm2_rest 4
	mm2_note C_4, 4
	mm2_note Eb4, 8
	mm2_note F_4, 4
	mm2_note C_4, 4
	mm2_rest 4
	mm2_note Bb3, 4
	mm2_note C_4, 4
	mm2_note B_3, 4
	mm2_note F_3, 8
	mm2_note Gb3, 4
	mm2_note G_3, 4
	mm2_loop 6, @loop_2
	mm2_note G_3, 4
	mm2_note G_3, 4
	mm2_note G_4, 4
	mm2_rest 4
	mm2_note F_4, 4
	mm2_note G_4, 4
	mm2_rest 4
	mm2_note G_3, 4
	mm2_rest 4
	mm2_note G_3, 4
	mm2_note G_4, 4
	mm2_rest 4
	mm2_note F_4, 4
	mm2_note G_4, 4
	mm2_note Eb4, 4
	mm2_note D_4, 4
	mm2_loop 0, @loop_2

music_boss_fighting_noise:
	mm2_tempo 6
	mm2_volume_envelope volume_decay, 1, 8
	mm2_volume 15

@loop_1:
	mm2_volume_envelope volume_decay, 15, 2
	mm2_noise_note 13, 16
	mm2_noise_note 13, 16
	mm2_noise_note 13, 16
	mm2_volume_envelope volume_decay, 1, 4
	mm2_noise_note 8, 16
	mm2_loop 1, @loop_1

@loop_2:
	mm2_volume_envelope volume_decay, 10, 2
	mm2_noise_note 12, 8
	mm2_noise_note 12, 8
	mm2_volume_envelope volume_decay, 4, 4
	mm2_noise_note 8, 8
	mm2_volume_envelope volume_decay, 10, 2
	mm2_noise_note 12, 8
	mm2_loop 2, @loop_2
	mm2_volume_envelope volume_decay, 4, 4
	mm2_noise_note 9, 4
	mm2_noise_note 9, 4
	mm2_noise_note 9, 4
	mm2_noise_note 9, 4
	mm2_noise_note 8, 4
	mm2_noise_note 8, 4
	mm2_noise_note 8, 4
	mm2_noise_note 8, 4

@loop_3:
	mm2_volume_envelope volume_decay, 13, 3
	mm2_noise_note 13, 4
	mm2_noise_note 13, 4
	mm2_rest 4
	mm2_noise_note 13, 4
	mm2_volume_envelope volume_decay, 4, 4
	mm2_noise_note 8, 8
	mm2_volume_envelope volume_decay, 10, 2
	mm2_noise_note 13, 4
	mm2_noise_note 13, 4
	mm2_loop 0, @loop_3

music_boss_fighting_modulator:
	mm2_modulator_set 0, 0, 0, volume_decay, 0, 0
	mm2_modulator_set 3, 2, 1, volume_decay, 0, 0

music_boss_show:
	mm2_music_header
	.WORD music_boss_show_pulse_1
	.WORD music_boss_show_pulse_2
	.WORD music_boss_show_triangle
	.WORD $0000
	.WORD music_boss_show_modulator

music_boss_show_pulse_1:
	mm2_tempo 6
	mm2_duty_cycle 0
	mm2_volume 10
	mm2_volume_envelope volume_attack, 10, 2
	mm2_base_note B_2
	mm2_note C_4, 4
	mm2_note C_4, 4
	mm2_note C_4, 4
	mm2_rest 4
	mm2_note C_4, 4
	mm2_note Bb3, 8
	mm2_number_of_note_tied 2
	mm2_note C_4, 4
	mm2_note C_4, 32
	mm2_note D_4, 4
	mm2_note D_4, 4
	mm2_note D_4, 4
	mm2_rest 4
	mm2_note D_4, 4
	mm2_note C_4, 8
	mm2_number_of_note_tied 2
	mm2_note D_4, 4
	mm2_note D_4, 32
	mm2_note Eb4, 4
	mm2_note Eb4, 4
	mm2_rest 4
	mm2_note Eb4, 4
	mm2_rest 16
	mm2_note Gb4, 4
	mm2_note Gb4, 4
	mm2_rest 4
	mm2_note Gb4, 4
	mm2_rest 16
	mm2_rest 4
	mm2_note G_4, 4
	mm2_rest 4
	mm2_number_of_note_tied 2
	mm2_note F_4, 4
	mm2_note F_4, 4
	mm2_note Eb4, 4
	mm2_note F_4, 4
	mm2_note Gb4, 4
	mm2_volume_envelope volume_decay, 8, 2
	mm2_note G_4, 2
	mm2_note Ab4, 2
	mm2_note G_4, 2
	mm2_note Ab4, 2
	mm2_note G_4, 2
	mm2_note Ab4, 2
	mm2_number_of_note_tied 2
	mm2_note G_4, 2
	mm2_modulator 1
	mm2_volume_envelope volume_attack, 10, 2
	mm2_note G_4, 16
	mm2_music_end

music_boss_show_pulse_2:
	mm2_tempo 6
	mm2_duty_cycle 1
	mm2_volume 10
	mm2_base_note B_1
	mm2_volume_envelope volume_attack, 10, 2
	mm2_note Eb3, 4
	mm2_note Eb3, 4
	mm2_note Eb3, 4
	mm2_rest 4
	mm2_note Eb3, 4
	mm2_note D_3, 8
	mm2_number_of_note_tied 2
	mm2_note Eb3, 4
	mm2_note Eb3, 32
	mm2_note F_3, 4
	mm2_note F_3, 4
	mm2_note F_3, 4
	mm2_rest 4
	mm2_note F_3, 4
	mm2_note Eb3, 8
	mm2_number_of_note_tied 2
	mm2_note F_3, 4
	mm2_note F_3, 32
	mm2_note G_3, 4
	mm2_note G_3, 4
	mm2_rest 4
	mm2_note G_3, 4
	mm2_rest 16
	mm2_note A_3, 4
	mm2_note A_3, 4
	mm2_rest 4
	mm2_note A_3, 4
	mm2_rest 16
	mm2_rest 4
	mm2_note B_3, 4
	mm2_rest 4
	mm2_note Ab3, 4
	mm2_note Ab3, 4
	mm2_note G_3, 4
	mm2_note Ab3, 4
	mm2_note Ab3, 4
	mm2_modulator 1
	mm2_note D_4, 32
	mm2_music_end

music_boss_show_triangle:
	mm2_tempo 6
	mm2_triangle_note_length $81
	mm2_base_note B_2
	mm2_note C_4, 32
	mm2_rest 4
	mm2_note C_4, 4
	mm2_note C_4, 4
	mm2_note C_4, 4
	mm2_note C_4, 4
	mm2_dotted_note_set
	mm2_note B_3, 8
	mm2_note Bb3, 32
	mm2_rest 4
	mm2_note Bb3, 4
	mm2_note Bb3, 4
	mm2_note Bb3, 4
	mm2_note Bb3, 4
	mm2_dotted_note_set
	mm2_note A_3, 8
	mm2_note Ab3, 4
	mm2_note Ab3, 4
	mm2_rest 4
	mm2_note Ab3, 4
	mm2_pitch_envelope $10
	mm2_rest 4
	mm2_note E_5, 4
	mm2_note E_5, 8
	mm2_pitch_envelope $00
	mm2_note D_4, 4
	mm2_note D_4, 4
	mm2_rest 4
	mm2_note D_4, 4
	mm2_pitch_envelope $10
	mm2_rest 4
	mm2_note E_5, 4
	mm2_note E_5, 8
	mm2_pitch_envelope $00
	mm2_modulator 1
	mm2_note G_3, 64
	mm2_music_end

music_boss_show_modulator:
	mm2_modulator_set 0, 0, 0, volume_decay, 0, 0
	mm2_modulator_set 3, 2, 1, volume_decay, 0, 0

music_bubbleman:
	mm2_music_header
	.WORD music_bubbleman_pulse_1
	.WORD music_bubbleman_pulse_2
	.WORD music_bubbleman_triangle
	.WORD music_bubbleman_noise
	.WORD music_bubbleman_modulator

music_bubbleman_pulse_1:
	mm2_tempo 5

@loop_1:
	mm2_duty_cycle 0
	mm2_base_note G_1
	mm2_volume 13
	mm2_volume_envelope volume_decay, 1, 18
	mm2_note G_2, 32
	mm2_note Ab2, 16
	mm2_note Bb2, 8
	mm2_note G_2, 64
	mm2_rest 8
	mm2_note F_2, 32
	mm2_note F_2, 16
	mm2_note G_2, 8
	mm2_note A_1, 8
	mm2_duty_cycle 3
	mm2_base_note G_2
	mm2_note G_4, 8
	mm2_note G_4, 8
	mm2_pitch_envelope $25
	mm2_note F_4, 8
	mm2_rest 8
	mm2_pitch_envelope $00
	mm2_note G_4, 8
	mm2_note G_4, 8
	mm2_pitch_envelope $25
	mm2_note F_4, 8
	mm2_rest 8
	mm2_pitch_envelope $00
	mm2_loop 1, @loop_1

@loop_5:
	mm2_duty_cycle 2

@loop_2:
	mm2_base_note G_1
	mm2_note C_3, 16
	mm2_pitch_envelope $10
	mm2_note C_4, 8
	mm2_pitch_envelope $00
	mm2_note C_3, 8
	mm2_rest 8
	mm2_note Bb2, 8
	mm2_pitch_envelope $10
	mm2_note C_4, 8
	mm2_pitch_envelope $00
	mm2_note C_3, 8
	mm2_loop 1, @loop_2

@loop_3:
	mm2_note D_3, 16
	mm2_pitch_envelope $10
	mm2_note C_4, 8
	mm2_pitch_envelope $00
	mm2_note D_3, 8
	mm2_rest 8
	mm2_note C_3, 8
	mm2_pitch_envelope $10
	mm2_note C_4, 8
	mm2_pitch_envelope $00
	mm2_note D_3, 8
	mm2_loop 1, @loop_3

@loop_4:
	mm2_note C_3, 16
	mm2_pitch_envelope $10
	mm2_note C_4, 8
	mm2_pitch_envelope $00
	mm2_note C_3, 8
	mm2_rest 8
	mm2_note Bb2, 8
	mm2_pitch_envelope $10
	mm2_note C_4, 8
	mm2_pitch_envelope $00
	mm2_note C_3, 8
	mm2_loop 1, @loop_4
	mm2_note D_3, 16
	mm2_pitch_envelope $10
	mm2_note C_4, 8
	mm2_pitch_envelope $00
	mm2_note D_3, 8
	mm2_rest 8
	mm2_note C_3, 8
	mm2_pitch_envelope $10
	mm2_note C_4, 8
	mm2_pitch_envelope $00
	mm2_note D_3, 8
	mm2_note B_2, 16
	mm2_pitch_envelope $10
	mm2_note C_4, 8
	mm2_pitch_envelope $00
	mm2_note D_3, 8
	mm2_rest 8
	mm2_note B_2, 8
	mm2_pitch_envelope $10
	mm2_note C_4, 8
	mm2_pitch_envelope $00
	mm2_note D_3, 8
	mm2_duty_cycle 3
	mm2_volume 13
	mm2_volume_envelope volume_decay, 1, 18
	mm2_base_note G_2
	mm2_number_of_note_tied 2
	mm2_note Eb4, 16
	mm2_modulator 1
	mm2_note Eb4, 16
	mm2_modulator 0
	mm2_note Eb4, 8
	mm2_note F_4, 8
	mm2_rest 8
	mm2_note G_4, 8
	mm2_rest 8
	mm2_note F_4, 8
	mm2_rest 8
	mm2_note Eb4, 8
	mm2_rest 8
	mm2_note Eb4, 8
	mm2_note F_4, 16
	mm2_note D_4, 8
	mm2_note Eb4, 8
	mm2_rest 8
	mm2_note D_4, 8
	mm2_rest 8
	mm2_note C_4, 8
	mm2_rest 8
	mm2_number_of_note_tied 2
	mm2_note Bb3, 8
	mm2_modulator 1
	mm2_note Bb3, 16
	mm2_rest 8
	mm2_dotted_note_set
	mm2_note Bb4, 16
	mm2_modulator 0
	mm2_note Ab4, 16
	mm2_number_of_note_tied 2
	mm2_note G_4, 16
	mm2_modulator 1
	mm2_note G_4, 16
	mm2_modulator 0
	mm2_note G_4, 8
	mm2_note F_4, 8
	mm2_note Eb4, 8
	mm2_note Bb4, 8
	mm2_rest 8
	mm2_note Ab4, 8
	mm2_rest 8
	mm2_dotted_note_set
	mm2_note G_4, 16
	mm2_note C_5, 8
	mm2_number_of_note_tied 2
	mm2_note B_4, 8
	mm2_modulator 1
	mm2_note B_4, 32
	mm2_modulator 0
	mm2_base_note G_3
	mm2_rest 8
	mm2_note G_4, 8
	mm2_note B_4, 8
	mm2_number_of_note_tied 2
	mm2_note D_5, 8
	mm2_modulator 1
	mm2_note D_5, 64
	mm2_modulator 0
	mm2_base_note G_2
	mm2_note G_3, 16
	mm2_rest 8
	mm2_note F_3, 8
	mm2_number_of_note_tied 2
	mm2_note F_3, 8
	mm2_modulator 1
	mm2_note F_3, 16
	mm2_modulator 0
	mm2_note Eb3, 8
	mm2_rest 8
	mm2_note F_3, 8
	mm2_number_of_note_tied 2
	mm2_note F_3, 8
	mm2_modulator 1
	mm2_note F_3, 16
	mm2_modulator 0
	mm2_note C_3, 8
	mm2_note Eb3, 8
	mm2_note F_3, 8
	mm2_note G_3, 16
	mm2_note F_3, 8
	mm2_note Bb3, 16
	mm2_note Ab3, 16
	mm2_note G_3, 16
	mm2_note F_3, 16
	mm2_note Eb3, 16
	mm2_note D_3, 16
	mm2_rest 8
	mm2_note G_3, 16
	mm2_rest 8
	mm2_note F_3, 8
	mm2_number_of_note_tied 2
	mm2_note F_3, 8
	mm2_modulator 1
	mm2_note F_3, 16
	mm2_modulator 0
	mm2_note Eb3, 8
	mm2_rest 8
	mm2_note F_3, 8
	mm2_number_of_note_tied 2
	mm2_note F_3, 8
	mm2_modulator 1
	mm2_note F_3, 16
	mm2_modulator 0
	mm2_note C_3, 8
	mm2_note Eb3, 8
	mm2_note F_3, 8
	mm2_note G_3, 16
	mm2_note F_3, 8
	mm2_note Bb3, 16
	mm2_note Ab3, 16
	mm2_note G_3, 16
	mm2_note B_3, 16
	mm2_note D_4, 16
	mm2_note F_4, 16
	mm2_note G_4, 8
	mm2_loop 0, @loop_5

music_bubbleman_pulse_2:
	mm2_tempo 5

@loop_1:
	mm2_volume 7
	mm2_duty_cycle 2
	mm2_base_note G_1
	mm2_volume_envelope volume_decay, 2, 18
	mm2_rest 4
	mm2_note Eb2, 8
	mm2_note G_3, 8
	mm2_note Eb3, 8
	mm2_note Eb2, 8
	mm2_note G_3, 8
	mm2_note C_3, 8
	mm2_note Eb3, 8
	mm2_note Ab2, 8
	mm2_note G_3, 8
	mm2_note Eb3, 8
	mm2_note Eb2, 8
	mm2_note Eb3, 8
	mm2_note G_3, 8
	mm2_note Eb2, 8
	mm2_note Eb3, 8
	mm2_note G_3, 8
	mm2_note D_2, 8
	mm2_note F_3, 8
	mm2_note D_3, 8
	mm2_note D_2, 8
	mm2_note F_3, 8
	mm2_note Bb2, 8
	mm2_note D_3, 8
	mm2_note G_2, 4
	mm2_duty_cycle 3
	mm2_volume 13
	mm2_base_note G_2
	mm2_note D_4, 8
	mm2_note D_4, 8
	mm2_rest 16
	mm2_note D_4, 8
	mm2_note D_4, 8
	mm2_rest 16
	mm2_loop 1, @loop_1

@loop_3:
	mm2_pitch_envelope $00
	mm2_volume 8
	mm2_duty_cycle 2
	mm2_base_note G_1
	mm2_rest 4
	mm2_note Eb2, 8
	mm2_note G_3, 8
	mm2_note Eb3, 8
	mm2_note Eb2, 8
	mm2_note G_3, 8
	mm2_note C_3, 8
	mm2_note Eb3, 8
	mm2_note Ab2, 8
	mm2_note G_3, 8
	mm2_note Eb3, 8
	mm2_note Eb2, 8
	mm2_note Eb3, 8
	mm2_note G_3, 8
	mm2_note Eb2, 8
	mm2_note Eb3, 8
	mm2_note G_3, 8
	mm2_note D_2, 8
	mm2_note F_3, 8
	mm2_note D_3, 8
	mm2_note D_2, 8
	mm2_note F_3, 8
	mm2_note Bb2, 8
	mm2_note D_3, 8
	mm2_note G_2, 8
	mm2_note F_3, 8
	mm2_note D_3, 8
	mm2_note D_2, 8
	mm2_note D_3, 8
	mm2_note F_3, 8
	mm2_note D_2, 8
	mm2_note D_3, 8
	mm2_note F_3, 8
	mm2_note Eb2, 8
	mm2_note G_3, 8
	mm2_note Eb3, 8
	mm2_note Eb2, 8
	mm2_note G_3, 8
	mm2_note C_3, 8
	mm2_note Eb3, 8
	mm2_note Ab2, 8
	mm2_note G_3, 8
	mm2_note Eb3, 8
	mm2_note Eb2, 8
	mm2_note Eb3, 8
	mm2_note G_3, 8
	mm2_note Eb2, 8
	mm2_note Eb3, 8
	mm2_note G_3, 8
	mm2_note D_2, 8
	mm2_note F_3, 8
	mm2_note D_3, 8
	mm2_note D_2, 8
	mm2_note F_3, 8
	mm2_note Bb2, 8
	mm2_note D_3, 8
	mm2_note G_2, 8
	mm2_note F_3, 8
	mm2_note D_3, 8
	mm2_note D_2, 8
	mm2_note D_3, 8
	mm2_note F_3, 8
	mm2_note D_2, 8
	mm2_note D_3, 8
	mm2_note F_3, 4
	mm2_duty_cycle 3
	mm2_volume 8
	mm2_volume_envelope volume_decay, 1, 18
	mm2_base_note G_2
	mm2_dotted_note_set
	mm2_rest 8
	mm2_note Eb4, 32
	mm2_note Eb4, 8
	mm2_note F_4, 8
	mm2_rest 8
	mm2_note G_4, 8
	mm2_rest 8
	mm2_note F_4, 8
	mm2_rest 8
	mm2_note Eb4, 8
	mm2_rest 8
	mm2_note Eb4, 8
	mm2_note F_4, 16
	mm2_note D_4, 8
	mm2_note Eb4, 8
	mm2_rest 8
	mm2_note D_4, 8
	mm2_rest 8
	mm2_note C_4, 8
	mm2_rest 8
	mm2_number_of_note_tied 2
	mm2_note Bb3, 8
	mm2_note Bb3, 16
	mm2_rest 8
	mm2_dotted_note_set
	mm2_note Bb4, 16
	mm2_note Ab4, 16
	mm2_note G_4, 32
	mm2_note G_4, 8
	mm2_note F_4, 8
	mm2_note Eb4, 8
	mm2_note Bb4, 8
	mm2_rest 8
	mm2_note Ab4, 8
	mm2_rest 8
	mm2_dotted_note_set
	mm2_note G_4, 16
	mm2_note C_5, 8
	mm2_number_of_note_tied 2
	mm2_note B_4, 8
	mm2_note B_4, 32
	mm2_base_note G_3
	mm2_rest 8
	mm2_note G_4, 8
	mm2_note B_4, 4
	mm2_note D_5, 64

@loop_2:
	mm2_base_note G_2
	mm2_note Eb3, 16
	mm2_rest 8
	mm2_note D_3, 8
	mm2_dotted_note_set
	mm2_note D_3, 16
	mm2_note C_3, 8
	mm2_rest 8
	mm2_note D_3, 8
	mm2_dotted_note_set
	mm2_note D_3, 16
	mm2_note Ab2, 8
	mm2_note C_3, 8
	mm2_note D_3, 8
	mm2_note Ab4, 4
	mm2_note Eb4, 4
	mm2_note C_4, 4
	mm2_note C_5, 4
	mm2_note Ab4, 4
	mm2_note Eb4, 4
	mm2_note C_4, 4
	mm2_note C_5, 4
	mm2_note Ab4, 4
	mm2_note Eb4, 4
	mm2_note C_4, 4
	mm2_note C_5, 4
	mm2_note Ab4, 4
	mm2_note Eb4, 4
	mm2_note C_4, 4
	mm2_note C_5, 4
	mm2_note G_4, 4
	mm2_note D_4, 4
	mm2_note B_3, 4
	mm2_note G_3, 4
	mm2_note G_4, 4
	mm2_note D_4, 4
	mm2_note B_3, 4
	mm2_note G_3, 4
	mm2_note G_4, 4
	mm2_note D_4, 4
	mm2_note B_3, 4
	mm2_note G_3, 4
	mm2_note G_4, 4
	mm2_note D_4, 4
	mm2_note B_3, 4
	mm2_note G_3, 4
	mm2_loop 1, @loop_2
	mm2_loop 0, @loop_3

music_bubbleman_triangle:
	mm2_tempo 5
	mm2_triangle_note_length $35
	mm2_base_note G_2
	mm2_note Eb3, 8
	mm2_note G_4, 8
	mm2_note Eb4, 8
	mm2_note Eb3, 8
	mm2_note G_4, 8
	mm2_note C_4, 8
	mm2_note Eb4, 8
	mm2_note Ab3, 8
	mm2_note G_4, 8
	mm2_note Eb4, 8
	mm2_note Eb3, 8
	mm2_note Eb4, 8
	mm2_note G_4, 8
	mm2_note Eb3, 8
	mm2_note Eb4, 8
	mm2_note G_4, 8
	mm2_note D_3, 8
	mm2_note F_4, 8
	mm2_note D_4, 8
	mm2_note D_3, 8
	mm2_note F_4, 8
	mm2_note Bb3, 8
	mm2_note D_4, 8
	mm2_note G_3, 8
	mm2_note F_4, 8
	mm2_note D_4, 8
	mm2_note D_3, 8
	mm2_note D_4, 8
	mm2_note F_4, 8
	mm2_note D_3, 8
	mm2_note D_4, 8
	mm2_note F_4, 8
	mm2_note Eb3, 8
	mm2_note G_4, 8
	mm2_note Eb4, 8
	mm2_note Eb3, 8
	mm2_note G_4, 8
	mm2_note C_4, 8
	mm2_note Eb4, 8
	mm2_note Ab3, 8
	mm2_note G_4, 8
	mm2_note Eb4, 8
	mm2_note Eb3, 8
	mm2_note Eb4, 8
	mm2_note G_4, 8
	mm2_note Eb3, 8
	mm2_note Eb4, 8
	mm2_note G_4, 8
	mm2_note D_3, 8
	mm2_note F_4, 8
	mm2_note D_4, 8
	mm2_note D_3, 8
	mm2_note F_4, 8
	mm2_note Bb3, 8
	mm2_note D_4, 8
	mm2_note G_3, 8
	mm2_note F_4, 8
	mm2_note D_4, 8
	mm2_note D_3, 8
	mm2_note D_4, 8
	mm2_pitch_envelope $10
	mm2_note C_5, 4
	mm2_note C_5, 4
	mm2_note C_5, 4
	mm2_note C_5, 4
	mm2_note A_4, 4
	mm2_note A_4, 4
	mm2_note Gb4, 4
	mm2_note Gb4, 4
	mm2_pitch_envelope $00

@loop_1:
	mm2_note Eb3, 8
	mm2_note G_4, 8
	mm2_note Eb4, 8
	mm2_note Eb3, 8
	mm2_note G_4, 8
	mm2_note C_4, 8
	mm2_note Eb4, 8
	mm2_note Ab3, 8
	mm2_note G_4, 8
	mm2_note Eb4, 8
	mm2_note Eb3, 8
	mm2_note Eb4, 8
	mm2_note G_4, 8
	mm2_note Eb3, 8
	mm2_note Eb4, 8
	mm2_note G_4, 8
	mm2_note D_3, 8
	mm2_note F_4, 8
	mm2_note D_4, 8
	mm2_note D_3, 8
	mm2_note F_4, 8
	mm2_note Bb3, 8
	mm2_note D_4, 8
	mm2_note G_3, 8
	mm2_note F_4, 8
	mm2_note D_4, 8
	mm2_note D_3, 8
	mm2_note D_4, 8
	mm2_note F_4, 8
	mm2_note D_3, 8
	mm2_note D_4, 8
	mm2_note F_4, 8
	mm2_loop 3, @loop_1
	mm2_note C_4, 8
	mm2_note Eb4, 8
	mm2_note D_4, 8
	mm2_note C_4, 8
	mm2_note Bb3, 16
	mm2_rest 8
	mm2_note Ab3, 8
	mm2_rest 8
	mm2_note Bb3, 8
	mm2_note Bb3, 16
	mm2_rest 8
	mm2_note Ab3, 8
	mm2_note C_4, 8
	mm2_note D_4, 8

@loop_2:
	mm2_note Ab3, 8
	mm2_loop 7, @loop_2

@loop_3:
	mm2_note B_3, 8
	mm2_loop 7, @loop_3
	mm2_note C_4, 8
	mm2_note Eb4, 8
	mm2_note D_4, 8
	mm2_note C_4, 8
	mm2_note Bb3, 16
	mm2_rest 8
	mm2_note Ab3, 8
	mm2_rest 8
	mm2_note Bb3, 8
	mm2_note Bb3, 16
	mm2_rest 8
	mm2_note Ab3, 8
	mm2_note C_4, 8
	mm2_note D_4, 8
	mm2_note Ab3, 8
	mm2_note C_4, 8
	mm2_note Eb4, 8
	mm2_note Ab3, 8
	mm2_note C_4, 8
	mm2_note Eb4, 8
	mm2_note Ab3, 8
	mm2_note C_4, 8
	mm2_note D_4, 8
	mm2_note G_3, 8
	mm2_note B_3, 8
	mm2_note D_4, 8
	mm2_note G_3, 8
	mm2_note B_3, 8
	mm2_note D_4, 8
	mm2_note G_4, 8
	mm2_loop 0, @loop_1

music_bubbleman_noise:
	mm2_tempo 5
	mm2_volume_envelope volume_decay, 1, 8
	mm2_volume 8

@loop_1:
	mm2_volume_envelope volume_decay, 7, 2
	mm2_noise_note 12, 8
	mm2_loop 23, @loop_1
	mm2_volume_envelope volume_decay, 4, 4
	mm2_pitch_envelope $FF
	mm2_noise_note 4, 8
	mm2_noise_note 4, 8
	mm2_rest 16
	mm2_noise_note 4, 8
	mm2_noise_note 4, 8
	mm2_rest 16
	mm2_pitch_envelope $00

@loop_2:
	mm2_volume_envelope volume_decay, 7, 2
	mm2_noise_note 12, 8
	mm2_loop 23, @loop_2
	mm2_volume_envelope volume_decay, 4, 4
	mm2_pitch_envelope $FF
	mm2_noise_note 4, 8
	mm2_noise_note 4, 8
	mm2_rest 16
	mm2_noise_note 4, 4
	mm2_noise_note 4, 4
	mm2_noise_note 4, 4
	mm2_noise_note 4, 4
	mm2_noise_note 4, 4
	mm2_noise_note 4, 4
	mm2_noise_note 5, 4
	mm2_noise_note 5, 4
	mm2_pitch_envelope $00

@loop_3:
	mm2_volume 13
	mm2_volume_envelope volume_decay, 7, 2
	mm2_noise_note 12, 8
	mm2_noise_note 12, 8
	mm2_volume_envelope volume_decay, 4, 4
	mm2_pitch_envelope $FF
	mm2_noise_note 4, 8
	mm2_pitch_envelope $00
	mm2_volume_envelope volume_decay, 7, 2
	mm2_noise_note 12, 8
	mm2_loop 0, @loop_3

music_bubbleman_modulator:
	mm2_modulator_set 0, 0, 0, volume_decay, 0, 0
	mm2_modulator_set 3, 2, 2, volume_decay, 0, 0

music_flashman:
	mm2_music_header
	.WORD music_flashman_pulse_1
	.WORD music_flashman_pulse_2
	.WORD music_flashman_triangle
	.WORD music_flashman_noise
	.WORD music_flashman_modulator

music_flashman_pulse_1:
	mm2_tempo 6
	mm2_volume 13
	mm2_volume_envelope volume_decay, 1, 6
	mm2_base_note B_1

@loop_1:
	mm2_duty_cycle 0
	mm2_note E_2, 16
	mm2_note G_2, 4
	mm2_rest 4
	mm2_note B_2, 4
	mm2_rest 4
	mm2_dotted_note_set
	mm2_note D_3, 8
	mm2_dotted_note_set
	mm2_note Db3, 8
	mm2_note A_2, 8
	mm2_dotted_note_set
	mm2_note C_3, 8
	mm2_dotted_note_set
	mm2_note B_2, 8
	mm2_note G_2, 8
	mm2_note A_2, 4
	mm2_rest 4
	mm2_note G_2, 4
	mm2_rest 4
	mm2_note E_2, 4
	mm2_note D_2, 4
	mm2_rest 4
	mm2_note E_2, 4
	mm2_rest 8
	mm2_note Gb3, 4
	mm2_note Gb3, 4
	mm2_note Gb3, 4
	mm2_note G_3, 4
	mm2_rest 8
	mm2_note Gb3, 4
	mm2_note Gb3, 4
	mm2_note Gb3, 4
	mm2_note G_3, 4
	mm2_dotted_note_set
	mm2_rest 16
	mm2_note Gb3, 4
	mm2_note Gb3, 4
	mm2_note Gb3, 4
	mm2_note G_3, 4
	mm2_rest 4
	mm2_note B_3, 4
	mm2_rest 4
	mm2_note B_3, 4
	mm2_note A_3, 4
	mm2_rest 4
	mm2_note G_3, 4
	mm2_rest 4
	mm2_note Gb3, 8
	mm2_loop 2, @loop_1
	mm2_note E_2, 16
	mm2_note G_2, 4
	mm2_rest 4
	mm2_note B_2, 4
	mm2_rest 4
	mm2_dotted_note_set
	mm2_note D_3, 8
	mm2_dotted_note_set
	mm2_note Db3, 8
	mm2_note A_2, 8
	mm2_dotted_note_set
	mm2_note C_3, 8
	mm2_dotted_note_set
	mm2_note B_2, 8
	mm2_note G_2, 8
	mm2_note A_2, 4
	mm2_rest 4
	mm2_note G_2, 4
	mm2_rest 4
	mm2_note E_2, 4
	mm2_note D_2, 4
	mm2_rest 4
	mm2_note E_2, 4

@loop_2:
	mm2_rest 8
	mm2_note Gb3, 4
	mm2_note Gb3, 4
	mm2_note Gb3, 4
	mm2_note G_3, 4
	mm2_loop 1, @loop_2
	mm2_rest 16
	mm2_note A_3, 4
	mm2_note A_3, 4
	mm2_rest 4
	mm2_note A_3, 4
	mm2_rest 4
	mm2_note A_3, 4
	mm2_rest 4
	mm2_note A_3, 4
	mm2_note B_3, 16
	mm2_rest 16
	mm2_base_note B_2

@loop_3:
	mm2_duty_cycle 1
	mm2_volume 13
	mm2_volume_envelope volume_decay, 1, 18
	mm2_rest 8
	mm2_note E_3, 8
	mm2_note B_3, 8
	mm2_note A_3, 8
	mm2_note B_3, 16
	mm2_note A_3, 8
	mm2_note G_3, 8
	mm2_note A_3, 8
	mm2_note B_3, 8
	mm2_rest 8
	mm2_number_of_note_tied 2
	mm2_note E_3, 16
	mm2_modulator 1
	mm2_note E_3, 16
	mm2_modulator 0
	mm2_note G_3, 8
	mm2_note Gb3, 8
	mm2_rest 8
	mm2_note Gb3, 8
	mm2_rest 8
	mm2_note Gb3, 8
	mm2_note E_3, 8
	mm2_note D_3, 8
	mm2_number_of_note_tied 2
	mm2_note E_3, 8
	mm2_note E_3, 32
	mm2_rest 8
	mm2_note E_3, 8
	mm2_note G_3, 8
	mm2_note A_3, 8
	mm2_rest 8
	mm2_note E_3, 8
	mm2_note B_3, 8
	mm2_note A_3, 8
	mm2_note B_3, 16
	mm2_note A_3, 8
	mm2_note G_3, 8
	mm2_note A_3, 8
	mm2_note B_3, 8
	mm2_rest 8
	mm2_number_of_note_tied 2
	mm2_note E_3, 16
	mm2_modulator 1
	mm2_note E_3, 16
	mm2_modulator 0
	mm2_note G_3, 8
	mm2_note Gb3, 8
	mm2_rest 8
	mm2_note Gb3, 8
	mm2_rest 8
	mm2_note G_3, 8
	mm2_note A_3, 8
	mm2_note Gb3, 8
	mm2_number_of_note_tied 2
	mm2_note E_3, 8
	mm2_number_of_note_tied 2
	mm2_note E_3, 16
	mm2_modulator 1
	mm2_note E_3, 16
	mm2_modulator 0
	mm2_rest 8
	mm2_note E_3, 8
	mm2_note G_3, 8
	mm2_note B_3, 8
	mm2_duty_cycle 3
	mm2_volume_envelope volume_decay, 1, 34
	mm2_number_of_note_tied 2
	mm2_note D_4, 32
	mm2_modulator 1
	mm2_note D_4, 32
	mm2_modulator 0
	mm2_number_of_note_tied 2
	mm2_note Db4, 16
	mm2_modulator 1
	mm2_note Db4, 16
	mm2_modulator 0
	mm2_number_of_note_tied 2
	mm2_note C_4, 16
	mm2_modulator 1
	mm2_note C_4, 16
	mm2_modulator 0
	mm2_duty_cycle 2
	mm2_note G_3, 8
	mm2_dotted_note_set
	mm2_note E_3, 16
	mm2_rest 8
	mm2_note E_3, 8
	mm2_note G_3, 8
	mm2_note A_3, 8
	mm2_note Bb3, 8
	mm2_note B_3, 8
	mm2_note Bb3, 8
	mm2_note B_3, 8
	mm2_note A_3, 8
	mm2_note G_3, 8
	mm2_note E_3, 8
	mm2_note D_3, 8
	mm2_duty_cycle 3
	mm2_number_of_note_tied 2
	mm2_note D_4, 32
	mm2_modulator 1
	mm2_note D_4, 32
	mm2_modulator 0
	mm2_number_of_note_tied 2
	mm2_note Db4, 16
	mm2_modulator 1
	mm2_note Db4, 16
	mm2_modulator 0
	mm2_number_of_note_tied 2
	mm2_note C_4, 16
	mm2_modulator 1
	mm2_note C_4, 16
	mm2_modulator 0
	mm2_duty_cycle 2
	mm2_note G_3, 8
	mm2_dotted_note_set
	mm2_note E_3, 16
	mm2_rest 8
	mm2_note E_3, 8
	mm2_note G_3, 8
	mm2_note A_3, 8
	mm2_note E_4, 8
	mm2_note B_3, 8
	mm2_note B_3, 8
	mm2_note B_3, 8
	mm2_note Eb4, 8
	mm2_note Gb4, 8
	mm2_note A_4, 8
	mm2_note B_4, 8
	mm2_loop 0, @loop_3

music_flashman_pulse_2:
	mm2_tempo 6
	mm2_duty_cycle 0
	mm2_base_note B_1

@loop_1:
	mm2_volume_envelope volume_decay, 1, 96
	mm2_volume 8
	mm2_rest 8
	mm2_note E_2, 16
	mm2_note G_2, 4
	mm2_rest 4
	mm2_note B_2, 4
	mm2_rest 4
	mm2_dotted_note_set
	mm2_note D_3, 8
	mm2_dotted_note_set
	mm2_note Db3, 8
	mm2_note A_2, 8
	mm2_dotted_note_set
	mm2_note C_3, 8
	mm2_dotted_note_set
	mm2_note B_2, 8
	mm2_note G_2, 8
	mm2_note A_2, 4
	mm2_rest 4
	mm2_note G_2, 4
	mm2_rest 4
	mm2_note E_2, 4
	mm2_note D_2, 4
	mm2_rest 4
	mm2_note E_2, 4
	mm2_note D_3, 4
	mm2_note D_3, 4
	mm2_note D_3, 4
	mm2_note E_3, 4
	mm2_rest 8
	mm2_note D_3, 4
	mm2_note D_3, 4
	mm2_note D_3, 4
	mm2_note E_3, 4
	mm2_rest 16
	mm2_rest 8
	mm2_note D_3, 4
	mm2_note D_3, 4
	mm2_note D_3, 4
	mm2_note E_3, 4
	mm2_rest 4
	mm2_note G_3, 4
	mm2_rest 4
	mm2_note G_3, 4
	mm2_note Gb3, 4
	mm2_rest 4
	mm2_note E_3, 4
	mm2_rest 4
	mm2_note D_3, 8
	mm2_loop 2, @loop_1
	mm2_rest 8
	mm2_note E_2, 16
	mm2_note G_2, 4
	mm2_rest 4
	mm2_note B_2, 4
	mm2_rest 4
	mm2_dotted_note_set
	mm2_note D_3, 8
	mm2_dotted_note_set
	mm2_note Db3, 8
	mm2_note A_2, 8
	mm2_dotted_note_set
	mm2_note C_3, 8
	mm2_dotted_note_set
	mm2_note B_2, 8
	mm2_note G_2, 8
	mm2_note A_2, 4
	mm2_rest 4
	mm2_note G_2, 4
	mm2_rest 4
	mm2_note E_2, 4
	mm2_note D_2, 4
	mm2_rest 4
	mm2_note E_2, 4
	mm2_note D_3, 4
	mm2_note D_3, 4
	mm2_note D_3, 4
	mm2_note E_3, 4
	mm2_rest 8
	mm2_note D_3, 4
	mm2_note D_3, 4
	mm2_note D_3, 4
	mm2_note E_3, 4
	mm2_rest 16
	mm2_note Gb3, 4
	mm2_note Gb3, 4
	mm2_rest 4
	mm2_note Gb3, 4
	mm2_rest 4
	mm2_note Gb3, 4
	mm2_rest 4
	mm2_note Gb3, 4
	mm2_note G_3, 16
	mm2_rest 16

@loop_4:
	mm2_base_note B_2

@loop_2:
	mm2_volume 7
	mm2_note G_3, 4
	mm2_note A_3, 4
	mm2_rest 4
	mm2_note G_3, 4
	mm2_rest 4
	mm2_note G_3, 4
	mm2_note A_3, 4
	mm2_note G_3, 4
	mm2_note Gb3, 4
	mm2_note G_3, 4
	mm2_rest 4
	mm2_note Gb3, 4
	mm2_rest 4
	mm2_note Gb3, 4
	mm2_note G_3, 4
	mm2_note Gb3, 4
	mm2_note D_3, 4
	mm2_note E_3, 4
	mm2_rest 4
	mm2_note E_3, 4
	mm2_rest 4
	mm2_note D_3, 4
	mm2_note E_3, 8
	mm2_note D_3, 4
	mm2_note E_3, 4
	mm2_rest 4
	mm2_note E_3, 4
	mm2_rest 4
	mm2_note D_3, 4
	mm2_note E_3, 8
	mm2_loop 3, @loop_2

@loop_3:
	mm2_duty_cycle 3
	mm2_volume 10
	mm2_volume_envelope volume_decay, 1, 34
	mm2_note B_3, 64
	mm2_note Bb3, 32
	mm2_note A_3, 32
	mm2_volume_envelope volume_decay, 1, 6
	mm2_duty_cycle 0
	mm2_rest 8
	mm2_note G_3, 8
	mm2_note A_3, 8
	mm2_note G_3, 8
	mm2_note B_3, 8
	mm2_note G_3, 8
	mm2_rest 8
	mm2_note G_3, 8
	mm2_note A_3, 8
	mm2_note G_3, 8
	mm2_note B_3, 8
	mm2_note G_3, 8
	mm2_rest 8
	mm2_note G_3, 8
	mm2_note Gb3, 8
	mm2_note G_3, 8
	mm2_loop 1, @loop_3
	mm2_loop 0, @loop_4

music_flashman_triangle:
	mm2_tempo 6
	mm2_triangle_note_length $25
	mm2_base_note B_2
	mm2_triangle_note_length $30

@loop_1:
	mm2_note E_3, 16
	mm2_note G_3, 4
	mm2_rest 4
	mm2_note B_3, 4
	mm2_rest 4
	mm2_dotted_note_set
	mm2_note D_4, 8
	mm2_dotted_note_set
	mm2_note Db4, 8
	mm2_note A_3, 8
	mm2_dotted_note_set
	mm2_note C_4, 8
	mm2_dotted_note_set
	mm2_note B_3, 8
	mm2_note G_3, 8
	mm2_note A_3, 4
	mm2_rest 4
	mm2_note G_3, 4
	mm2_rest 4
	mm2_note E_3, 4
	mm2_note D_3, 4
	mm2_rest 4
	mm2_note E_3, 8
	mm2_rest 4
	mm2_note E_3, 8
	mm2_note E_3, 4
	mm2_rest 4
	mm2_note E_3, 8
	mm2_note E_3, 4
	mm2_rest 4
	mm2_note E_3, 8
	mm2_note E_3, 4
	mm2_rest 4
	mm2_note E_3, 8
	mm2_note E_3, 4
	mm2_rest 4
	mm2_note E_3, 8
	mm2_note Gb3, 4
	mm2_rest 4
	mm2_note Gb3, 8
	mm2_note G_3, 4
	mm2_rest 4
	mm2_note B_3, 4
	mm2_rest 4
	mm2_note D_3, 16
	mm2_loop 2, @loop_1
	mm2_note E_3, 16
	mm2_note G_3, 4
	mm2_rest 4
	mm2_note B_3, 4
	mm2_rest 4
	mm2_dotted_note_set
	mm2_note D_4, 8
	mm2_dotted_note_set
	mm2_note Db4, 8
	mm2_note A_3, 8
	mm2_dotted_note_set
	mm2_note C_4, 8
	mm2_dotted_note_set
	mm2_note B_3, 8
	mm2_note G_3, 8
	mm2_note A_3, 4
	mm2_rest 4
	mm2_note G_3, 4
	mm2_rest 4
	mm2_note E_3, 4
	mm2_note D_3, 4
	mm2_rest 4
	mm2_note E_3, 8
	mm2_rest 4
	mm2_note E_3, 8
	mm2_note E_3, 4
	mm2_rest 4
	mm2_note E_3, 8
	mm2_note E_3, 4
	mm2_rest 4
	mm2_note E_3, 8
	mm2_note E_3, 4
	mm2_rest 4
	mm2_note E_3, 8
	mm2_note D_3, 4
	mm2_note D_3, 4
	mm2_rest 4
	mm2_note D_3, 4
	mm2_rest 4
	mm2_note D_3, 4
	mm2_rest 4
	mm2_note D_3, 4
	mm2_note E_3, 4
	mm2_pitch_envelope $10
	mm2_note B_4, 4
	mm2_note B_4, 4
	mm2_note Gb3, 4
	mm2_note F_3, 4
	mm2_note E_3, 4
	mm2_note Eb3, 4
	mm2_note D_3, 4

@loop_2:
	mm2_base_note B_2
	mm2_triangle_note_length $30
	mm2_pitch_envelope $00
	mm2_note E_3, 8
	mm2_note E_3, 8
	mm2_rest 8
	mm2_note E_3, 8
	mm2_note E_3, 4
	mm2_note G_3, 4
	mm2_rest 4
	mm2_note B_3, 4
	mm2_rest 4
	mm2_note G_3, 4
	mm2_note E_3, 8
	mm2_note E_3, 8
	mm2_note E_3, 8
	mm2_rest 8
	mm2_note E_3, 8
	mm2_note E_3, 4
	mm2_note G_3, 4
	mm2_rest 4
	mm2_note B_3, 4
	mm2_rest 4
	mm2_note G_3, 4
	mm2_note E_3, 8
	mm2_note D_3, 8
	mm2_note D_3, 8
	mm2_rest 8
	mm2_note D_3, 8
	mm2_note D_3, 4
	mm2_note Gb3, 4
	mm2_rest 4
	mm2_note A_3, 4
	mm2_rest 4
	mm2_note Gb3, 4
	mm2_note D_3, 8
	mm2_note E_3, 8
	mm2_note E_3, 8
	mm2_rest 8
	mm2_note E_3, 8
	mm2_note E_3, 4
	mm2_note G_3, 4
	mm2_rest 4
	mm2_note B_3, 4
	mm2_rest 4
	mm2_note G_3, 4
	mm2_note E_3, 8
	mm2_loop 1, @loop_2

@loop_3:
	mm2_pitch_envelope $00
	mm2_base_note B_2
	mm2_note G_3, 4
	mm2_rest 4
	mm2_note G_3, 8
	mm2_note G_3, 4
	mm2_rest 4
	mm2_note G_3, 8
	mm2_note G_3, 4
	mm2_rest 4
	mm2_note G_3, 8
	mm2_note G_3, 4
	mm2_rest 4
	mm2_note G_3, 8
	mm2_note Gb3, 4
	mm2_rest 4
	mm2_note Gb3, 8
	mm2_note Gb3, 4
	mm2_rest 4
	mm2_note Gb3, 8
	mm2_note F_3, 4
	mm2_rest 4
	mm2_note F_3, 8
	mm2_note F_3, 4
	mm2_rest 4
	mm2_note F_3, 8
	mm2_rest 8
	mm2_note E_3, 8
	mm2_note Gb3, 8
	mm2_note E_3, 8
	mm2_note G_3, 8
	mm2_note E_3, 8
	mm2_rest 8
	mm2_note E_3, 8
	mm2_pitch_envelope $10
	mm2_note D_5, 8
	mm2_note D_5, 8
	mm2_note Bb3, 8
	mm2_note Bb3, 8
	mm2_note E_5, 4
	mm2_note E_5, 4
	mm2_note Bb3, 8
	mm2_note A_3, 8
	mm2_note A_3, 8
	mm2_loop 1, @loop_3
	mm2_loop 0, @loop_2

music_flashman_noise:
	mm2_tempo 6

@loop_1:
	mm2_volume_envelope volume_decay, 10, 4
	mm2_volume 15
	mm2_pitch_envelope $05
	mm2_noise_note 9, 4
	mm2_pitch_envelope $00
	mm2_volume_envelope volume_decay, 6, 2
	mm2_volume 6
	mm2_noise_note 11, 4
	mm2_noise_note 11, 4
	mm2_noise_note 11, 4
	mm2_loop 59, @loop_1
	mm2_volume_envelope volume_decay, 1, 1
	mm2_volume 9
	mm2_pitch_envelope $12
	mm2_noise_note 9, 4
	mm2_noise_note 9, 4
	mm2_rest 4
	mm2_noise_note 9, 4
	mm2_rest 4
	mm2_noise_note 9, 4
	mm2_rest 4
	mm2_noise_note 9, 4
	mm2_noise_note 12, 4
	mm2_noise_note 12, 4
	mm2_noise_note 11, 4
	mm2_noise_note 11, 4
	mm2_noise_note 10, 4
	mm2_noise_note 10, 4
	mm2_noise_note 9, 4
	mm2_noise_note 9, 4

@loop_2:
	mm2_volume 14
	mm2_pitch_envelope $10
	mm2_volume_envelope volume_decay, 10, 2
	mm2_noise_note 11, 16
	mm2_volume_envelope volume_decay, 6, 4
	mm2_dotted_note_set
	mm2_noise_note 2, 8
	mm2_volume_envelope volume_decay, 10, 2
	mm2_noise_note 11, 4
	mm2_noise_note 11, 4
	mm2_noise_note 11, 4
	mm2_noise_note 11, 8
	mm2_volume_envelope volume_decay, 6, 4
	mm2_noise_note 2, 16
	mm2_loop 7, @loop_2

@loop_3:
	mm2_volume_envelope volume_decay, 10, 2
	mm2_noise_note 11, 8
	mm2_noise_note 11, 8
	mm2_loop 2, @loop_3
	mm2_volume_envelope volume_decay, 6, 4
	mm2_noise_note 2, 16

@loop_4:
	mm2_volume_envelope volume_decay, 10, 2
	mm2_noise_note 11, 4
	mm2_rest 4
	mm2_noise_note 11, 8
	mm2_volume_envelope volume_decay, 6, 4
	mm2_noise_note 2, 16
	mm2_loop 5, @loop_4

@loop_5:
	mm2_volume_envelope volume_decay, 10, 2
	mm2_noise_note 11, 8
	mm2_noise_note 11, 8
	mm2_loop 2, @loop_5
	mm2_volume_envelope volume_decay, 6, 4
	mm2_noise_note 2, 16

@loop_6:
	mm2_volume_envelope volume_decay, 10, 2
	mm2_noise_note 11, 8
	mm2_noise_note 11, 8
	mm2_volume_envelope volume_decay, 6, 4
	mm2_noise_note 2, 16
	mm2_loop 3, @loop_6
	mm2_volume_envelope volume_decay, 10, 4
	mm2_volume 8
	mm2_noise_note 12, 8
	mm2_noise_note 12, 8
	mm2_noise_note 11, 8
	mm2_noise_note 11, 8
	mm2_noise_note 10, 4
	mm2_noise_note 10, 4
	mm2_noise_note 10, 8
	mm2_noise_note 9, 8
	mm2_noise_note 9, 8
	mm2_loop 0, @loop_2

music_flashman_modulator:
	mm2_modulator_set 0, 0, 0, volume_decay, 0, 0
	mm2_modulator_set 3, 2, 2, volume_decay, 0, 0

music_game_over:
	mm2_music_header
	.WORD music_game_over_pulse_1
	.WORD music_game_over_pulse_2
	.WORD music_game_over_triangle
	.WORD music_game_over_noise
	.WORD music_game_over_modulator

music_game_over_pulse_1:
	mm2_tempo 6
	mm2_volume 15
	mm2_duty_cycle 0
	mm2_base_note Eb3
	mm2_volume_envelope volume_decay, 1, 47
	mm2_note Eb4, 4
	mm2_note Eb4, 4
	mm2_rest 4
	mm2_note Eb4, 4
	mm2_rest 4
	mm2_note Eb4, 4
	mm2_rest 4
	mm2_note Eb4, 4
	mm2_rest 16
	mm2_note E_4, 4
	mm2_note Gb4, 4
	mm2_rest 4
	mm2_number_of_note_tied 3
	mm2_note Ab4, 4
	mm2_note Ab4, 16
	mm2_modulator 0
	mm2_note Ab4, 32
	mm2_music_end

music_game_over_pulse_2:
	mm2_tempo 6
	mm2_duty_cycle 1
	mm2_base_note Eb3
	mm2_volume 15
	mm2_volume_envelope volume_decay, 1, 47
	mm2_note C_4, 4
	mm2_note C_4, 4
	mm2_rest 4
	mm2_note C_4, 4
	mm2_rest 4
	mm2_note C_4, 4
	mm2_rest 4
	mm2_note C_4, 4
	mm2_rest 16
	mm2_note Db4, 4
	mm2_note Eb4, 4
	mm2_rest 4
	mm2_number_of_note_tied 3
	mm2_note F_4, 4
	mm2_note F_4, 16
	mm2_modulator 0
	mm2_note F_4, 32
	mm2_music_end

music_game_over_triangle:
	mm2_tempo 6
	mm2_triangle_note_length $30
	mm2_base_note Eb3
	mm2_note Ab3, 4
	mm2_note Ab3, 4
	mm2_rest 4
	mm2_note Ab3, 4
	mm2_rest 4
	mm2_note Ab3, 4
	mm2_rest 4
	mm2_note Ab3, 8
	mm2_pitch_envelope $10
	mm2_note Ab5, 4
	mm2_note Eb5, 8
	mm2_pitch_envelope $00
	mm2_note A_3, 4
	mm2_note B_3, 8
	mm2_triangle_note_length $7F
	mm2_number_of_note_tied 2
	mm2_note Db4, 4
	mm2_number_of_note_tied 2
	mm2_note Db4, 8
	mm2_note Db4, 16
	mm2_triangle_note_length $30
	mm2_pitch_envelope $10
	mm2_note Ab5, 4
	mm2_note Gb5, 4
	mm2_note D_5, 16
	mm2_music_end

music_game_over_noise:
	mm2_tempo 6
	mm2_volume_envelope volume_decay, 15, 3
	mm2_volume 15
	mm2_rest 8
	mm2_rest 4
	mm2_noise_note 13, 8
	mm2_noise_note 13, 8
	mm2_noise_note 13, 8
	mm2_rest 64
	mm2_music_end

music_game_over_modulator:
	mm2_modulator_set 3, 2, 1, volume_decay, 0, 0

music_get_weapon:
	mm2_music_header
	.WORD $0000
	.WORD $0000
	.WORD music_get_weapon_triangle
	.WORD music_get_weapon_noise
	.WORD music_get_weapon_modulator

music_get_weapon_triangle:
	mm2_tempo 5
	mm2_triangle_note_length $30
	mm2_base_note B_2

@loop_1:
	mm2_pitch_envelope $10
	mm2_note C_4, 8
	mm2_rest 8
	mm2_note E_5, 16
	mm2_rest 8
	mm2_note C_4, 4
	mm2_note C_4, 4
	mm2_note E_5, 16
	mm2_note C_4, 8
	mm2_rest 8
	mm2_note E_5, 16
	mm2_note C_4, 4
	mm2_note C_4, 4
	mm2_note C_4, 4
	mm2_note C_4, 4
	mm2_note E_5, 16
	mm2_loop 0, @loop_1

music_get_weapon_noise:
	mm2_tempo 5
	mm2_volume 15
	mm2_volume_envelope volume_decay, 3, 2
	mm2_pitch_envelope $FF

@loop_1:
	mm2_rest 16
	mm2_noise_note 4, 16
	mm2_loop 0, @loop_1

music_get_weapon_modulator:

music_title:
	mm2_music_header
	.WORD music_title_pulse_1
	.WORD music_title_pulse_2
	.WORD music_title_triangle
	.WORD music_title_noise
	.WORD music_title_modulator

music_title_pulse_1:
	mm2_tempo 5

@loop_1:
	mm2_volume 12
	mm2_duty_cycle 0
	mm2_base_note B_2
	mm2_volume_envelope volume_decay, 1, 26
	mm2_note C_4, 8
	mm2_note C_4, 4
	mm2_note C_4, 4
	mm2_note C_4, 8
	mm2_note C_4, 4
	mm2_note C_4, 4
	mm2_note C_4, 8
	mm2_note D_4, 8
	mm2_rest 8
	mm2_number_of_note_tied 2
	mm2_note Bb3, 32
	mm2_modulator 1
	mm2_note Bb3, 32
	mm2_modulator 0
	mm2_note Bb3, 8
	mm2_note Ab3, 8
	mm2_note Ab3, 4
	mm2_note Ab3, 4
	mm2_note Ab3, 8
	mm2_note F_3, 8
	mm2_rest 8
	mm2_note F_3, 8
	mm2_rest 8
	mm2_note G_3, 32
	mm2_note G_3, 8
	mm2_note Ab3, 8
	mm2_note Bb3, 8
	mm2_rest 16
	mm2_note C_4, 8
	mm2_note C_4, 4
	mm2_note C_4, 4
	mm2_note C_4, 8
	mm2_note C_4, 4
	mm2_note C_4, 4
	mm2_note C_4, 8
	mm2_note D_4, 8
	mm2_rest 8
	mm2_number_of_note_tied 2
	mm2_note Bb3, 32
	mm2_modulator 1
	mm2_note Bb3, 32
	mm2_modulator 0
	mm2_note Bb3, 8
	mm2_note Ab3, 16
	mm2_note Ab3, 8
	mm2_note Bb3, 8
	mm2_rest 8
	mm2_note Bb3, 8
	mm2_rest 8
	mm2_number_of_note_tied 2
	mm2_note C_4, 8
	mm2_modulator 1
	mm2_note C_4, 32
	mm2_modulator 0
	mm2_duty_cycle 2
	mm2_volume_envelope volume_decay, 7, 3
	mm2_base_note B_3
	mm2_note G_5, 4
	mm2_note F_5, 4
	mm2_note Eb5, 4
	mm2_note F_5, 4
	mm2_note Eb5, 4
	mm2_note D_5, 4
	mm2_note Db5, 4
	mm2_note C_5, 4
	mm2_loop 1, @loop_1
	mm2_volume_envelope volume_decay, 1, 4
	mm2_base_note B_2
	mm2_duty_cycle 3
	mm2_note C_4, 8
	mm2_note C_4, 8
	mm2_note G_3, 8
	mm2_note E_3, 8
	mm2_note E_4, 8
	mm2_note C_4, 8
	mm2_note G_3, 8
	mm2_note G_4, 16
	mm2_note F_4, 8
	mm2_note E_4, 8
	mm2_note D_4, 8
	mm2_note E_4, 8
	mm2_note C_4, 16
	mm2_rest 8
	mm2_note Bb3, 8
	mm2_note Bb3, 8
	mm2_note A_3, 8
	mm2_note F_3, 8
	mm2_note D_4, 16
	mm2_note Bb3, 8
	mm2_note G_3, 8
	mm2_note Bb3, 4
	mm2_note Bb3, 4
	mm2_note F_3, 4
	mm2_note D_4, 4
	mm2_note Bb3, 4
	mm2_note F_4, 4
	mm2_note D_4, 4
	mm2_note Bb4, 4
	mm2_note F_4, 8
	mm2_note Bb3, 16
	mm2_rest 8
	mm2_note A_3, 8

@loop_2:
	mm2_note A_3, 4
	mm2_note C_4, 4
	mm2_note A_3, 4
	mm2_note E_3, 4
	mm2_note C_3, 8
	mm2_loop 1, @loop_2
	mm2_note A_3, 4
	mm2_note C_4, 4
	mm2_note Ab4, 4
	mm2_note A_4, 4
	mm2_note Ab4, 4
	mm2_note A_4, 4
	mm2_note Ab4, 4
	mm2_note A_4, 4
	mm2_note E_4, 4
	mm2_note C_4, 4
	mm2_rest 8
	mm2_duty_cycle 3
	mm2_note A_3, 16
	mm2_rest 8
	mm2_triplet_note_set
	mm2_note C_3, 8
	mm2_triplet_note_set
	mm2_note Eb3, 8
	mm2_triplet_note_set
	mm2_note Ab3, 8
	mm2_triplet_note_set
	mm2_note Eb3, 8
	mm2_triplet_note_set
	mm2_note Ab3, 8
	mm2_triplet_note_set
	mm2_note C_4, 8
	mm2_triplet_note_set
	mm2_note Ab3, 8
	mm2_triplet_note_set
	mm2_note C_4, 8
	mm2_triplet_note_set
	mm2_note Eb4, 8
	mm2_triplet_note_set
	mm2_note C_4, 8
	mm2_triplet_note_set
	mm2_note Eb4, 8
	mm2_triplet_note_set
	mm2_note Ab4, 8
	mm2_note Ab3, 8
	mm2_note Ab3, 8
	mm2_note Ab3, 8
	mm2_note Ab3, 8
	mm2_rest 8
	mm2_note Bb3, 16
	mm2_rest 8
	mm2_volume_envelope volume_decay, 1, 26
	mm2_duty_cycle 0
	mm2_note C_4, 8
	mm2_note C_4, 4
	mm2_note C_4, 4
	mm2_note C_4, 8
	mm2_note C_4, 4
	mm2_note C_4, 4
	mm2_note C_4, 8
	mm2_note D_4, 8
	mm2_rest 8
	mm2_number_of_note_tied 2
	mm2_note Bb3, 32
	mm2_modulator 1
	mm2_note Bb3, 32
	mm2_modulator 0
	mm2_note Bb3, 8
	mm2_note Ab3, 8
	mm2_note Ab3, 4
	mm2_note Ab3, 4
	mm2_note Ab3, 8
	mm2_note F_3, 8
	mm2_rest 8
	mm2_note F_3, 8
	mm2_rest 8
	mm2_note G_3, 32
	mm2_note G_3, 8
	mm2_note Ab3, 8
	mm2_note Bb3, 8
	mm2_rest 16
	mm2_note C_4, 8
	mm2_note C_4, 4
	mm2_note C_4, 4
	mm2_note C_4, 8
	mm2_note C_4, 4
	mm2_note C_4, 4
	mm2_note C_4, 8
	mm2_note D_4, 8
	mm2_rest 8
	mm2_number_of_note_tied 2
	mm2_note Bb3, 32
	mm2_note Bb3, 32
	mm2_rest 8
	mm2_note G_3, 8
	mm2_note G_3, 8
	mm2_note A_3, 8
	mm2_note C_4, 8
	mm2_rest 8
	mm2_note G_3, 8
	mm2_note A_3, 8
	mm2_note C_4, 8
	mm2_rest 8
	mm2_note G_3, 8
	mm2_note A_3, 8
	mm2_note C_4, 8
	mm2_rest 8
	mm2_note G_4, 8
	mm2_note A_4, 8
	mm2_note C_5, 8
	mm2_music_end

music_title_pulse_2:
	mm2_tempo 5

@loop_1:
	mm2_volume 12
	mm2_duty_cycle 0
	mm2_base_note B_2
	mm2_volume_envelope volume_decay, 1, 26
	mm2_note G_3, 8
	mm2_note G_3, 4
	mm2_note G_3, 4
	mm2_note G_3, 8
	mm2_note G_3, 4
	mm2_note G_3, 4
	mm2_note G_3, 8
	mm2_note G_3, 8
	mm2_rest 8
	mm2_note F_3, 64
	mm2_note G_3, 8
	mm2_note Eb3, 8
	mm2_note Eb3, 4
	mm2_note Eb3, 4
	mm2_note Eb3, 8
	mm2_note D_3, 8
	mm2_rest 8
	mm2_note D_3, 8
	mm2_rest 8
	mm2_note E_3, 32
	mm2_note E_3, 8
	mm2_note Eb3, 8
	mm2_note F_3, 8
	mm2_rest 16
	mm2_note G_3, 8
	mm2_note G_3, 4
	mm2_note G_3, 4
	mm2_note G_3, 8
	mm2_note G_3, 4
	mm2_note G_3, 4
	mm2_note G_3, 8
	mm2_note G_3, 8
	mm2_rest 8
	mm2_note F_3, 64
	mm2_note G_3, 8
	mm2_note Eb3, 16
	mm2_note Eb3, 8
	mm2_note F_3, 8
	mm2_rest 8
	mm2_note F_3, 8
	mm2_rest 8
	mm2_number_of_note_tied 2
	mm2_note G_3, 8
	mm2_note G_3, 32
	mm2_duty_cycle 2
	mm2_volume 6
	mm2_base_note B_3
	mm2_volume_envelope volume_decay, 7, 3
	mm2_rest 4
	mm2_note G_5, 4
	mm2_note F_5, 4
	mm2_note Eb5, 4
	mm2_note F_5, 4
	mm2_note Eb5, 4
	mm2_note D_5, 4
	mm2_note Db5, 4
	mm2_loop 1, @loop_1
	mm2_volume_envelope volume_decay, 1, 4
	mm2_base_note B_2
	mm2_volume 12
	mm2_duty_cycle 3
	mm2_note G_3, 8
	mm2_volume 7
	mm2_rest 8
	mm2_note C_4, 8
	mm2_note G_3, 8
	mm2_note E_3, 8
	mm2_note E_4, 8
	mm2_note C_4, 8
	mm2_note G_3, 8
	mm2_note G_4, 16
	mm2_note F_4, 8
	mm2_note E_4, 8
	mm2_note D_4, 8
	mm2_volume 12
	mm2_note G_3, 16
	mm2_rest 8
	mm2_note F_3, 8
	mm2_volume 7
	mm2_rest 8
	mm2_note Bb3, 8
	mm2_note A_3, 8
	mm2_note F_3, 8
	mm2_note D_4, 16
	mm2_note Bb3, 8
	mm2_note G_3, 8
	mm2_note Bb3, 4
	mm2_note Bb3, 4
	mm2_note F_3, 4
	mm2_note D_4, 4
	mm2_note Bb3, 4
	mm2_note F_4, 4
	mm2_note D_4, 4
	mm2_note Bb4, 4
	mm2_volume 12
	mm2_note F_3, 16
	mm2_rest 8
	mm2_note E_3, 8
	mm2_volume 7
	mm2_rest 4

@loop_2:
	mm2_note A_3, 4
	mm2_note C_4, 4
	mm2_note A_3, 4
	mm2_note E_3, 4
	mm2_note C_3, 8
	mm2_loop 1, @loop_2
	mm2_note A_3, 4
	mm2_note C_4, 4
	mm2_note Ab4, 4
	mm2_note A_4, 4
	mm2_note Ab4, 4
	mm2_note A_4, 4
	mm2_note Ab4, 4
	mm2_note A_4, 4
	mm2_note E_4, 4
	mm2_note C_4, 4
	mm2_rest 4
	mm2_volume 12
	mm2_duty_cycle 3
	mm2_note E_3, 16
	mm2_rest 8
	mm2_triplet_note_set
	mm2_note Eb3, 8
	mm2_triplet_note_set
	mm2_note Ab3, 8
	mm2_triplet_note_set
	mm2_note C_4, 8
	mm2_triplet_note_set
	mm2_note Ab3, 8
	mm2_triplet_note_set
	mm2_note C_4, 8
	mm2_triplet_note_set
	mm2_note Eb4, 8
	mm2_triplet_note_set
	mm2_note C_4, 8
	mm2_triplet_note_set
	mm2_note Eb4, 8
	mm2_triplet_note_set
	mm2_note Ab4, 8
	mm2_triplet_note_set
	mm2_note Eb4, 8
	mm2_triplet_note_set
	mm2_note Ab4, 8
	mm2_triplet_note_set
	mm2_note C_5, 8
	mm2_note Eb3, 8
	mm2_note Eb3, 8
	mm2_note Eb3, 8
	mm2_note Eb3, 8
	mm2_rest 8
	mm2_note F_3, 16
	mm2_rest 8
	mm2_volume_envelope volume_decay, 1, 26
	mm2_duty_cycle 0
	mm2_note G_3, 8
	mm2_note G_3, 4
	mm2_note G_3, 4
	mm2_note G_3, 8
	mm2_note G_3, 4
	mm2_note G_3, 4
	mm2_note G_3, 8
	mm2_note G_3, 8
	mm2_rest 8
	mm2_note F_3, 64
	mm2_note G_3, 8
	mm2_note Eb3, 8
	mm2_note Eb3, 4
	mm2_note Eb3, 4
	mm2_note Eb3, 8
	mm2_note D_3, 8
	mm2_rest 8
	mm2_note D_3, 8
	mm2_rest 8
	mm2_note E_3, 32
	mm2_note E_3, 8
	mm2_note Eb3, 8
	mm2_note F_3, 8
	mm2_rest 16
	mm2_note G_3, 8
	mm2_note G_3, 4
	mm2_note G_3, 4
	mm2_note G_3, 8
	mm2_note G_3, 4
	mm2_note G_3, 4
	mm2_note G_3, 8
	mm2_note G_3, 8
	mm2_rest 8
	mm2_note F_3, 64
	mm2_rest 8
	mm2_note E_3, 8
	mm2_note E_3, 8
	mm2_note F_3, 8
	mm2_note G_3, 8
	mm2_rest 8
	mm2_note E_3, 8
	mm2_note F_3, 8
	mm2_note G_3, 8
	mm2_rest 8
	mm2_note E_3, 8
	mm2_note F_3, 8
	mm2_note G_3, 8
	mm2_rest 8
	mm2_note E_4, 8
	mm2_note F_4, 8
	mm2_note G_4, 8
	mm2_music_end

music_title_triangle:
	mm2_tempo 5
	mm2_triangle_note_length $30
	mm2_base_note B_2

@loop_1:
	mm2_note C_4, 8
	mm2_note C_4, 4
	mm2_note C_4, 4
	mm2_loop 29, @loop_1
	mm2_note C_4, 8
	mm2_note G_3, 8
	mm2_note A_3, 8
	mm2_note C_4, 8

@loop_2:
	mm2_note C_4, 8
	mm2_note C_4, 4
	mm2_note C_4, 4
	mm2_loop 29, @loop_2
	mm2_note C_4, 8
	mm2_note G_3, 8
	mm2_note A_3, 8
	mm2_note C_4, 8
	mm2_triangle_note_length $30
	mm2_note E_3, 16
	mm2_pitch_envelope $14
	mm2_note E_5, 8
	mm2_rest 8
	mm2_note C_4, 8
	mm2_note C_4, 8
	mm2_note E_5, 8
	mm2_rest 8
	mm2_note C_4, 8
	mm2_note C_4, 8
	mm2_note E_5, 8
	mm2_note C_4, 8
	mm2_rest 8
	mm2_pitch_envelope $00
	mm2_note E_3, 8
	mm2_pitch_envelope $14
	mm2_note E_5, 8
	mm2_note E_5, 8
	mm2_pitch_envelope $00
	mm2_note D_3, 16
	mm2_pitch_envelope $14
	mm2_note E_5, 8
	mm2_rest 8
	mm2_note C_4, 8
	mm2_note C_4, 8
	mm2_note E_5, 8
	mm2_rest 8
	mm2_note C_4, 8
	mm2_note C_4, 8
	mm2_note E_5, 8
	mm2_note C_4, 8
	mm2_rest 8
	mm2_pitch_envelope $00
	mm2_note D_3, 8
	mm2_pitch_envelope $14
	mm2_note E_5, 8
	mm2_note E_5, 8
	mm2_pitch_envelope $00
	mm2_note C_3, 8
	mm2_rest 8
	mm2_pitch_envelope $14
	mm2_note E_5, 8
	mm2_rest 8
	mm2_note C_4, 8
	mm2_note C_4, 8
	mm2_note E_5, 8
	mm2_rest 8
	mm2_note C_4, 8
	mm2_note C_4, 8
	mm2_note E_5, 8
	mm2_note C_4, 8
	mm2_rest 8
	mm2_pitch_envelope $00
	mm2_note C_3, 8
	mm2_pitch_envelope $14
	mm2_note E_5, 8
	mm2_note E_5, 8
	mm2_pitch_envelope $00
	mm2_note C_3, 8
	mm2_rest 8
	mm2_pitch_envelope $14
	mm2_note E_5, 8
	mm2_rest 8
	mm2_note Gb3, 8
	mm2_note Gb3, 8
	mm2_note E_5, 16
	mm2_note E_5, 4
	mm2_note E_5, 4
	mm2_note E_5, 8
	mm2_note D_5, 4
	mm2_note D_5, 4
	mm2_note D_5, 8
	mm2_note C_5, 4
	mm2_note C_5, 4
	mm2_note C_5, 8
	mm2_note E_5, 4
	mm2_note E_5, 4
	mm2_note D_5, 4
	mm2_note B_4, 4
	mm2_pitch_envelope $00

@loop_3:
	mm2_note C_4, 8
	mm2_note C_4, 4
	mm2_note C_4, 4
	mm2_loop 23, @loop_3
	mm2_note C_4, 8
	mm2_note C_4, 8
	mm2_note D_4, 8
	mm2_note E_4, 8
	mm2_rest 8
	mm2_note C_4, 8
	mm2_note D_4, 8
	mm2_note E_4, 8
	mm2_rest 8
	mm2_note C_4, 8
	mm2_note D_4, 8
	mm2_note E_4, 8
	mm2_rest 8
	mm2_note C_4, 8
	mm2_note D_4, 8
	mm2_note E_4, 8
	mm2_music_end

music_title_noise:
	mm2_tempo 5
	mm2_volume_envelope volume_decay, 10, 2
	mm2_volume 15

@loop_1:
	mm2_noise_note 13, 8
	mm2_noise_note 13, 4
	mm2_noise_note 13, 4
	mm2_volume_envelope volume_decay, 8, 4
	mm2_pitch_envelope $FE
	mm2_noise_note 2, 8
	mm2_pitch_envelope $00
	mm2_volume_envelope volume_decay, 10, 2
	mm2_noise_note 13, 4
	mm2_noise_note 13, 4
	mm2_loop 59, @loop_1
	mm2_noise_note 12, 8
	mm2_noise_note 12, 8
	mm2_noise_note 12, 8
	mm2_noise_note 12, 8
	mm2_rest 8
	mm2_noise_note 12, 8
	mm2_noise_note 12, 8
	mm2_noise_note 12, 8
	mm2_rest 8
	mm2_noise_note 12, 8
	mm2_noise_note 12, 8
	mm2_noise_note 12, 8
	mm2_rest 8
	mm2_noise_note 12, 8
	mm2_noise_note 12, 8
	mm2_noise_note 12, 8
	mm2_music_end

music_title_modulator:
	mm2_modulator_set 0, 0, 0, volume_decay, 0, 0
	mm2_modulator_set 3, 2, 2, volume_decay, 0, 0

sfx_1up:
	mm2_sfx_priority 15
	.BYTE sfx_pulse_2

;1
;sfx_pulse_2
	mm2_sfx_frames 3
	mm2_duty_cycle 3
	mm2_volume 15
	mm2_sfx_note nDb5

;2
;sfx_pulse_2
	mm2_sfx_frames 3
	mm2_sfx_note nEb5

;3
;sfx_pulse_2
	mm2_sfx_frames 3
	mm2_sfx_note nF_5

;4
;sfx_pulse_2
	mm2_sfx_frames 3
	mm2_sfx_note nGb5

;5
;sfx_pulse_2
	mm2_sfx_frames 3
	mm2_sfx_note nAb5

;6
;sfx_pulse_2
	mm2_sfx_frames 3
	mm2_sfx_note nBb5

;7
;sfx_pulse_2
	mm2_sfx_frames 3
	mm2_sfx_note nC_6

;8
;sfx_pulse_2
	mm2_sfx_frames 3
	mm2_sfx_note nDb6

;9
;sfx_pulse_2
	mm2_sfx_frames 3
	mm2_volume 8
	mm2_sfx_note nDb5

;10
;sfx_pulse_2
	mm2_sfx_frames 3
	mm2_sfx_note nEb5

;11
;sfx_pulse_2
	mm2_sfx_frames 3
	mm2_sfx_note nF_5

;12
;sfx_pulse_2
	mm2_sfx_frames 3
	mm2_sfx_note nGb5

;13
;sfx_pulse_2
	mm2_sfx_frames 3
	mm2_sfx_note nAb5

;14
;sfx_pulse_2
	mm2_sfx_frames 3
	mm2_sfx_note nBb5

;15
;sfx_pulse_2
	mm2_sfx_frames 3
	mm2_sfx_note nC_6

;16
;sfx_pulse_2
	mm2_sfx_frames 3
	mm2_sfx_note nDb6
	mm2_sfx_end

sfx_atomic_fire_charge_1:
	mm2_sfx_priority 3
	.BYTE sfx_pulse_2 | sfx_noise

;1
;sfx_pulse_2
@loop_1:
	mm2_duty_cycle 1
	mm2_volume 15
	mm2_pitch_envelope $F6
	mm2_sfx_note nC_5

;sfx_noise
	mm2_sfx_frames 3
	mm2_volume 4
	mm2_sfx_noise_note 7
	mm2_loop 2, @loop_1
	mm2_sfx_end

sfx_atomic_fire_charge_2:
	mm2_sfx_priority 3
	.BYTE sfx_pulse_2 | sfx_noise

;1
;sfx_pulse_2
@loop_1:
	mm2_duty_cycle 1
	mm2_volume 15
	mm2_pitch_envelope $F6
	mm2_sfx_note nDb5

;sfx_noise
	mm2_sfx_frames 3
	mm2_volume 8
	mm2_sfx_noise_note 5
	mm2_loop 2, @loop_1
	mm2_sfx_end

sfx_atomic_fire_charge_3:
	mm2_sfx_priority 3
	.BYTE sfx_pulse_2 | sfx_noise

;1
;sfx_pulse_2
@loop_1:
	mm2_duty_cycle 1
	mm2_volume 15
	mm2_pitch_envelope $F1
	mm2_sfx_note nD_5

;sfx_noise
	mm2_sfx_frames 3
	mm2_volume 8
	mm2_sfx_noise_note 1
	mm2_loop 3, @loop_1
	mm2_sfx_end

sfx_atomic_fire_release:
	mm2_sfx_priority 3
	.BYTE sfx_pulse_2 | sfx_noise

;1
;sfx_pulse_2
	mm2_duty_cycle 3
	mm2_volume 15
	mm2_sfx_note nDb1

;sfx_noise
	mm2_sfx_frames 3
	mm2_noise_duty_cycle 1
	mm2_volume 15
	mm2_sfx_noise_note 4

;2
;sfx_pulse_2
@loop_1:
	mm2_pitch_envelope $02
	mm2_sfx_note nDb1

;sfx_noise
	mm2_sfx_frames 4
	mm2_noise_duty_cycle 0
	mm2_sfx_noise_note 0
	mm2_loop 10, @loop_1
	mm2_sfx_end

sfx_death:
	mm2_sfx_priority 15
	.BYTE sfx_pulse_1 | sfx_pulse_2

;1
;sfx_pulse_1
	mm2_duty_cycle 2
	mm2_pitch_envelope $2F
	mm2_volume 15
	mm2_sfx_note nC_6

;sfx_pulse_2
	mm2_sfx_frames 16
	mm2_duty_cycle 0
	mm2_pitch_envelope $2F
	mm2_volume 15
	mm2_sfx_note nBb5

;2
;sfx_pulse_1
	mm2_volume 12
	mm2_sfx_note nC_6

;sfx_pulse_2
	mm2_sfx_frames 16
	mm2_volume 12
	mm2_sfx_note nBb5

;3
;sfx_pulse_1
	mm2_volume 9
	mm2_sfx_note nC_6

;sfx_pulse_2
	mm2_sfx_frames 16
	mm2_volume 9
	mm2_sfx_note nBb5

;4
;sfx_pulse_1
	mm2_volume 6
	mm2_sfx_note nC_6

;sfx_pulse_2
	mm2_sfx_frames 16
	mm2_volume 6
	mm2_sfx_note nBb5

;5
;sfx_pulse_1
	mm2_volume 4
	mm2_sfx_note nC_6

;sfx_pulse_2
	mm2_sfx_frames 16
	mm2_volume 4
	mm2_sfx_note nBb5

;6
;sfx_pulse_1
	mm2_volume 2
	mm2_sfx_note nC_6

;sfx_pulse_2
	mm2_sfx_frames 16
	mm2_volume 2
	mm2_sfx_note nBb5
	mm2_sfx_end

sfx_door:
	mm2_sfx_priority 8
	.BYTE sfx_pulse_2 | sfx_noise

;1
;sfx_pulse_2
@loop_1:
	mm2_duty_cycle 2
	mm2_volume 15
	mm2_sfx_modulator_set 4, 5, 3, volume_decay, 2, 1
	mm2_pitch_envelope $B1
	mm2_sfx_note nEb4

;sfx_noise
	mm2_sfx_frames 6
	mm2_noise_duty_cycle 1
	mm2_sfx_modulator_set 4, 5, 3, volume_decay, 2, 1
	mm2_sfx_noise_note 6
	mm2_loop 30, @loop_1
	mm2_sfx_end

sfx_enemy_hit:
	mm2_sfx_priority 8
	.BYTE sfx_pulse_2 | sfx_noise

;1
;sfx_pulse_2
	mm2_duty_cycle 1
	mm2_volume 15
	mm2_sfx_modulator_set 0, 5, 0, volume_decay, 7, 6
	mm2_pitch_envelope $40
	mm2_sfx_note nB_7

;sfx_noise
	mm2_sfx_frames 21
	mm2_noise_duty_cycle 1
	mm2_pitch_envelope $4F
	mm2_volume 15
	mm2_sfx_noise_note 0
	mm2_sfx_end

sfx_enemy_immune:
	mm2_sfx_priority 8
	.BYTE sfx_pulse_2 | sfx_triangle

;1
;sfx_pulse_2
	mm2_volume 15
	mm2_pitch_envelope $81
	mm2_sfx_note nBb6

;sfx_triangle
	mm2_sfx_frames 4
	mm2_triangle_note_length $3F
	mm2_sfx_note nA_7
	mm2_sfx_end

sfx_landing:
	mm2_sfx_priority 2
	.BYTE sfx_pulse_2

;1
;sfx_pulse_2
@loop_1:
	mm2_sfx_frames 4
	mm2_duty_cycle 1
	mm2_pitch_envelope $8B
	mm2_volume 15
	mm2_sfx_modulator_set 2, 6, 1, volume_decay, 1, 2
	mm2_sfx_note nA_5
	mm2_loop 1, @loop_1
	mm2_sfx_end

sfx_mega_buster:
	mm2_sfx_priority 3
	.BYTE sfx_pulse_2

;1
;sfx_pulse_2
	mm2_sfx_frames 16
	mm2_duty_cycle 1
	mm2_volume 15
	mm2_sfx_modulator_set 2, 4, 2, volume_decay, 0, 0
	mm2_pitch_envelope $E0
	mm2_sfx_note nAb3
	mm2_sfx_end

sfx_megaman_hit:
	mm2_sfx_priority 13
	.BYTE sfx_pulse_2 | sfx_noise

;1
;sfx_pulse_2
	mm2_duty_cycle 3
	mm2_volume 15
	mm2_sfx_modulator_set 5, 3, 2, volume_decay, 7, 0
	mm2_pitch_envelope $5F
	mm2_sfx_note nB_4

;sfx_noise
	mm2_sfx_frames 5
	mm2_sfx_modulator_set 2, 3, 1, volume_decay, 7, 0
	mm2_pitch_envelope $5F
	mm2_volume 15
	mm2_sfx_noise_note 5

;2
;sfx_pulse_2
	mm2_volume 8
	mm2_sfx_note nDb5

;sfx_noise
	mm2_sfx_frames 13
	mm2_sfx_modulator_set 2, 3, 1, volume_decay, 7, 0
	mm2_pitch_envelope $F1
	mm2_noise_duty_cycle 1
	mm2_sfx_noise_note 10
	mm2_sfx_end

sfx_refill:
	mm2_sfx_priority 12
	.BYTE sfx_pulse_1 | sfx_pulse_2

;1
;sfx_pulse_1
@loop_1:
	mm2_sfx_modulator_set 2, 1, 1, volume_decay, 0, 0
	mm2_volume 15
	mm2_duty_cycle 1
	mm2_sfx_note nC_5

;sfx_pulse_2
	mm2_sfx_frames 4
	mm2_duty_cycle 1
	mm2_sfx_modulator_set 2, 1, 1, volume_decay, 0, 0
	mm2_volume 15
	mm2_sfx_note nE_5
	mm2_loop 2, @loop_1
	mm2_sfx_end

sfx_select:
	mm2_sfx_priority 14
	.BYTE sfx_pulse_2

;1
;sfx_pulse_2
	mm2_sfx_frames 5
	mm2_volume 15
	mm2_duty_cycle 3
	mm2_sfx_note nAb4

;2
;sfx_pulse_2
	mm2_sfx_frames 8
	mm2_volume 15
	mm2_sfx_modulator_set 7, 0, 0, volume_decay, 0, 0
	mm2_duty_cycle 1
	mm2_sfx_note nDb4
	mm2_sfx_end

sfx_teleport_in:
	mm2_sfx_priority 14
	.BYTE sfx_pulse_2 | sfx_noise

;1
;sfx_pulse_2
	mm2_duty_cycle 3
	mm2_pitch_envelope $25
	mm2_sfx_modulator_set 3, 2, 1, volume_decay, 4, 2
	mm2_volume 15
	mm2_sfx_note nGb5 + 2

;sfx_noise
	mm2_sfx_frames 4
	mm2_volume 5
	mm2_sfx_noise_note 10

;2
;sfx_pulse_2
	mm2_pitch_envelope $F0
	mm2_sfx_note nGb5 + 2

;sfx_noise
	mm2_sfx_frames 5
	mm2_volume 3
	mm2_sfx_noise_note 10
	mm2_sfx_end

.endscope
.popseg
