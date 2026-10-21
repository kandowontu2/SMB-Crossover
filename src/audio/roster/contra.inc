.segment "CONTRA_AUDIO"
.scope ContraNative
APU_DMC = $4010
APU_DMC_COUNTER = $4011
APU_DMC_SAMPLE_ADDR = $4012
APU_DMC_SAMPLE_LEN = $4013
APU_NOISE_CONFIG = $400c
APU_PULSE2_CONFIG = $4004
APU_PULSE2_SWEEP = $4005
APU_PULSE_CONFIG = $4000
APU_PULSE_LENGTH = $4003
APU_PULSE_PERIOD = $4002
APU_PULSE_SWEEP = $4001
APU_STATUS = $4015
APU_TRIANGLE_CONFIG = $4008
DECRESCENDO_END_PAUSE = RgContraRam+$30
INIT_SOUND_CODE = RgContraRam+$22
LEVEL_END_PLAYERS_ALIVE = RgContraRam+$94
LVL_PULSE_VOL_INDEX = RgContraRam+$2a
NEW_SOUND_CODE_HIGH_ADDR = RgContraRam+$6c
NEW_SOUND_CODE_LOW_ADDR = RgContraRam+$66
PAUSE_STATE = $25
PAUSE_STATE_01 = RgContraRam+$2f
PERCUSSION_INDEX_BACKUP = RgContraRam+$21
PULSE_NOTE = RgContraRam+$7c
PULSE_VOLUME = RgContraRam+$60
PULSE_VOL_DURATION = RgContraRam+$2a
SOUND_CFG_HIGH = RgContraRam+$4e
SOUND_CFG_LOW = RgContraRam+$42
SOUND_CHNL_REG_OFFSET = RgContraRam+$23
SOUND_CMD_HIGH_ADDR = RgContraRam+$18
SOUND_CMD_LENGTH = RgContraRam+$0
SOUND_CMD_LOW_ADDR = RgContraRam+$12
SOUND_CODE = RgContraRam+$6
SOUND_CURRENT_SLOT = RgContraRam+$20
SOUND_FLAGS = RgContraRam+$24
SOUND_LENGTH_MULTIPLIER = RgContraRam+$54
SOUND_PERIOD_ROTATE = RgContraRam+$5a
SOUND_PITCH_ADJ = RgContraRam+$32
SOUND_PULSE_LENGTH = RgContraRam+$c
SOUND_PULSE_PERIOD = RgContraRam+$72
SOUND_REPEAT_COUNT = RgContraRam+$48
SOUND_TABLE_PTR = $ec
SOUND_TRIANGLE_CFG = RgContraRam+$44
SOUND_VOL_ENV = RgContraRam+$1e
SOUND_VOL_TIMER = RgContraRam+$7a
UNKNOWN_SOUND_00 = RgContraRam+$36
UNKNOWN_SOUND_01 = RgContraRam+$3c
VIBRATO_AMOUNT = RgContraRam+$80
VIBRATO_CTRL = RgContraRam+$78
VIBRATO_DELAY = RgContraRam+$7e
; Contra US Disassembly - v1.4
; https://github.com/vermiceli/nes-contra-us
; Bank 1 is responsible for audio and sprites.  The audio code takes up about
; 3/4 of the bank. The remaining 1/4 of the bank is for sprite data and code to
; draw sprites.



; import labels from bank 7

; export labels used in other banks

; Every PRG ROM bank starts with a single byte specifying which number it is
.byte $01

; pointer table for music of level 1 (#$08 * #$02 = #$10 bytes)
; related to pulse channel config registers
; CPU address $8001
pulse_volume_ptr_tbl:
    .addr lvl_1_pulse_volume_00 ; CPU address $91dd
    .addr lvl_1_pulse_volume_01 ; CPU address $91e5
    .addr lvl_1_pulse_volume_02 ; CPU address $91ea
    .addr lvl_1_pulse_volume_03 ; CPU address $91f7
    .addr lvl_1_pulse_volume_04 ; CPU address $9204
    .addr lvl_1_pulse_volume_05 ; CPU address $9216
    .addr lvl_1_pulse_volume_06 ; CPU address $9229
    .addr lvl_1_pulse_volume_07 ; CPU address $923c

; music of level 2 (#$08 * #$02 = #$10 bytes)
    .addr lvl_2_pulse_volume_00 ; CPU address $a3db
    .addr lvl_2_pulse_volume_01 ; CPU address $a3e8
    .addr lvl_2_pulse_volume_02 ; CPU address $a3ee
    .addr lvl_2_pulse_volume_03 ; CPU address $a3f5
    .addr lvl_2_pulse_volume_04 ; CPU address $a402
    .addr lvl_2_pulse_volume_05 ; CPU address $a40f
    .addr lvl_2_pulse_volume_06 ; CPU address $a706
    .addr lvl_2_pulse_volume_07 ; CPU address $aa5f

; music of level 3 (#$08 * #$02 = #$10 bytes)
    .addr lvl_3_pulse_volume_00 ; CPU address $aa6c
    .addr lvl_3_pulse_volume_01 ; CPU address $aa73
    .addr lvl_3_pulse_volume_02 ; CPU address $ab04
    .addr lvl_3_pulse_volume_03 ; CPU address $ab11
    .addr lvl_3_pulse_volume_04 ; CPU address $ab1e
    .addr lvl_3_pulse_volume_05 ; CPU address $ab29
    .addr lvl_3_pulse_volume_06 ; CPU address $aa78
    .addr lvl_3_pulse_volume_07 ; CPU address $98ca

; music of level 4 (#$08 * #$02 = #$10 bytes)
    .addr lvl_4_pulse_volume_00 ; CPU address $98d5
    .addr lvl_4_pulse_volume_01 ; CPU address $98ea
    .addr lvl_4_pulse_volume_02 ; CPU address $98f1
    .addr lvl_4_pulse_volume_03 ; CPU address $98fd
    .addr lvl_4_pulse_volume_04 ; CPU address $9904
    .addr lvl_4_pulse_volume_05 ; CPU address $9909
    .addr lvl_4_pulse_volume_06 ; CPU address $9915
    .addr lvl_4_pulse_volume_07 ; CPU address $991c

; music of level 5 (#$08 * #$02 = #$10 bytes)
    .addr lvl_5_pulse_volume_00 ; CPU address $9928
    .addr lvl_5_pulse_volume_01 ; CPU address $9e71
    .addr lvl_5_pulse_volume_02 ; CPU address $9e7d
    .addr lvl_5_pulse_volume_03 ; CPU address $9c43
    .addr lvl_5_pulse_volume_04 ; CPU address $9c50
    .addr lvl_5_pulse_volume_05 ; CPU address $9c59
    .addr lvl_5_pulse_volume_06 ; CPU address $9c65
    .addr lvl_5_pulse_volume_07 ; CPU address $a064

; music of level 6 (#$08 * #$02 = #$10 bytes)
    .addr lvl_6_pulse_volume_00 ; CPU address $a072
    .addr lvl_6_pulse_volume_01 ; CPU address $a080
    .addr lvl_6_pulse_volume_02 ; CPU address $a088
    .addr lvl_6_pulse_volume_03 ; CPU address $9e84
    .addr lvl_6_pulse_volume_04 ; CPU address $9e90
    .addr lvl_6_pulse_volume_05 ; CPU address $9e9c
    .addr lvl_6_pulse_volume_06 ; CPU address $a713
    .addr lvl_6_pulse_volume_07 ; CPU address $a71b

; music of level 7 (#$06 * #$02 = #$0c bytes)
    .addr lvl_7_pulse_volume_00 ; CPU address $a728
    .addr lvl_7_pulse_volume_01 ; CPU address $abd2
    .addr lvl_7_pulse_volume_02 ; CPU address $abda
    .addr lvl_7_pulse_volume_03 ; CPU address $abea
    .addr lvl_7_pulse_volume_04 ; CPU address $abeb
    .addr lvl_7_pulse_volume_05 ; CPU address $aa85

; silences pulse wave channel
; after pause or level end, or anytime need to silence pulse wave channel
; input
;  * x - sound register offset
;  * y - APU channel register offset
mute_pulse_channel:
    lda #$30                       ; a = #$30
    sta $4000,x                    ; set volume to 0 and duty cycle to 25%
    jsr wait                       ; execute #$0a nop instructions
    bne set_pulse_timer_and_length ; always branch to set pulse timer and length

; mutes/unmutes pulse wave channel based on pause state
; input
;  * x - sound register offset
mute_unmute_pulse_channel:
    lda SOUND_FLAGS,x      ; load the current sound slot's sound flags
    and #$41               ; keep bits .x.. ...x
    ora PAUSE_STATE_01     ; merge with current game pause state (0 = unpaused, 1 = paused)
    bne mute_pulse_channel ; branch if paused

; input
;  * x - sound channel register config offset
;  * y - sound channel register offset
unmute_pulse_channel:
    lda PULSE_VOLUME,x   ; load current volume
    ora SOUND_CFG_HIGH,x
    sta $4000,y
    jsr wait             ; execute #$0a nop instructions

set_pulse_timer_and_length:
    lda SOUND_PULSE_PERIOD,x ; load in memory pulse period value
    sta APU_PULSE_PERIOD,y   ; set APU pulse period value
    jsr wait                 ; execute #$0a nop instructions
    lda SOUND_PULSE_LENGTH,x ; load in memory pulse length value
    sta APU_PULSE_LENGTH,y   ; set the APU pulse channel length
    jmp wait                 ; execute #$0a nop instructions

; see if pausing/unpausing
; if unpausing, turn on level music, otherwise stop bg music
sound_check_pause:
    lda PAUSE_STATE      ; #$01 for paused, #$00 for not paused
    cmp PAUSE_STATE_01   ; compare to last frame pause state
    beq sound_check_exit ; pause already handled, exit
    sta PAUSE_STATE_01   ; set current pause value (0 = unpaused, 1 = paused)
    cmp #$00             ; see if unpausing
    beq @unpausing       ; if unpausing, continue to play level music
    jmp reset_channels   ; pausing, reset triangle, noise, and pulse channels to stop level music

@unpausing:
    lda SOUND_CODE+4          ; load sound code for sound slot 4
    beq @toggle_pulse_channel ; branch if not playing game pausing jingle
    lda SOUND_FLAGS+4         ; still playing game pausing jingle, load sound slot #$04 (pulse 1 channel) read index
                              ; this is the channel that the pause jingle uses
    bpl @unmute_pulse_2       ; branch if still playing the game pausing jingle
    lda PULSE_VOL_DURATION+3
    sta APU_PULSE_SWEEP

; unpausing in middle of pause jingle
@unmute_pulse_2:
    ldx #$04                 ; x = #$04 (pulse 2 channel config register)
    ldy #$00                 ; y = #$00 (pulse 1 channel register offset)
    jsr unmute_pulse_channel ; could have been optimized to a jmp call with no rts
    rts

@toggle_pulse_channel:
    lda SOUND_CODE                ; load sound slot 0's sound code (pulse 1 channel)
    beq sound_check_exit          ; exit if not playing anything
    ldx #$00                      ; x = #$00
    ldy #$00                      ; y = #$00
    jsr mute_unmute_pulse_channel ; mutes/unmutes pulse wave channel based on pause state

sound_check_exit:
    rts

; sound and music entry point, check each sound slot and if populated, execute
; that slot's sound command
handle_sound_slots:
    jsr sound_check_pause ; if unpausing, turn off level music, otherwise play music
    ldx #$00              ; initialize sound slot loop
    ldy #$00              ; initialize sound channel register offset to #$00 (pulse 1 channel)

; input
;  * x - sound slot index
;  * y - channel register offset, e.g. #$00 (pulse 1 channel), #$04 (pulse 2 channel), #$08 (triangle channel), #$0c (noise/dmc channel)
@sound_slot_loop:
    stx SOUND_CURRENT_SLOT    ; set the current sound slot to the current loop index
    sty SOUND_CHNL_REG_OFFSET ; set sound channel config register offset (#$00, #$04, #$08, or #$0c)
    lda SOUND_CODE,x          ; load sound code for sound slot
    beq @prep_next_loop       ; prep to move to next sound slot, or exit if looped through all slots
    tay                       ; sound slot has a sound code, transfer sound code to offset register y
    jsr handle_sound_code     ; read and interpret sound code in slot x

@prep_next_loop:
    inx                            ; increment sound slot index
    cpx #$06                       ; compare to after last sound slot
    beq sound_music_entry_exit     ; exit if looped through all sound slots
    cpx #$05                       ; see if last sound slot
    bne @load_sound_channel_offset ; branch if not the last sound slot
    lda #$0c                       ; sound slot #$05, set sound register offset to #$0c (noise channel)
    jmp @loop_next                 ; loop to last sound slot with the sound channel register to use being the noise channel

; all sound slots except #$05
; slot #$05 is always the noise channel
@load_sound_channel_offset:
    txa      ; transfer sound slot index to a
    asl      ; double sound slot index
    asl      ; double sound slot index again
    and #$0f ; keep low nibble, this is the new sound channel register offset
             ; (e.g. #$00 = pulse 1 channel, #$04 = pulse 2 channel)

@loop_next:
    tay                  ; set SOUND_CHNL_REG_OFFSET (e.g. #$00 = pulse 1 channel, #$04 = pulse 2 channel)
    jmp @sound_slot_loop

sound_music_entry_exit:
    rts

; read and interpret loaded sound code in slot x
; output
;  * x - sound slot with the sound code to handle
handle_sound_code:
    lda PAUSE_STATE_01         ; load current game pause state (0 = unpaused, 1 = paused)
    beq @check_sound_command   ; branch if game not paused
    lda SOUND_CODE,x           ; game paused, load sound code for current slot
    cmp #$54                   ; see if sound code is the pause jingle (sound_54)
    bne sound_music_entry_exit ; exit if not the game pausing jingle sound

@check_sound_command:
    jsr load_sound_code_addr   ; gets the sound_xx pointer for sound slot from SOUND_CMD_LOW_ADDR and stores in ($e0)
                               ; also sets y to point to beginning, i.e. #$00
    lda SOUND_FLAGS,x          ; load the current sound slot's sound flags
                               ; (0 = sound_xx command byte >= #$30, 1 = sound_xx command byte 0 < #$30)
    dec SOUND_CMD_LENGTH,x     ; decrement the remaining number of video frames sound should play for
                               ; before continuing to the next sound command
    bne @pulse_vol_and_vibrato ; branch if sound command hasn't finished executing
    jmp read_sound_command_00  ; finished with any previous sound command (or first command), read next/first sound command

@pulse_vol_and_vibrato:
    and #$41                      ; keep bit 0 and 6 of the sound slot's sound flags (mute flags)
    bne handle_sound_code_exit_00 ; exit if bit 0 or bit 6 is set (mute flags set)
    cpx #$02                      ; compare sound slot to #$02 (triangle channel)
    beq handle_sound_code_exit_00 ; exit if sound slot #$02 (triangle channel)
    cpx #$03                      ; compare sound slot to #$03 (noise/dmc channel)
    beq handle_sound_code_exit_00 ; exit if sound slot #$03 (noise/dmc channel)
    cpx #$02                      ; compare sound slot to #$02 (triangle channel)
    bcs @check_pulse_volume       ; branch if sound slot #$04 (pulse 1 channel), or #$05 (noise channel)
                                  ; not sure why developer didn't compare to #$04 here since they've already compared to #$02 and #$03 !(HUH)
    lda VIBRATO_CTRL,x            ; sound slot is #$00 (pulse 1 channel) or #$01 (pulse 2 channel)
                                  ; load VIBRATO_CTRL,x (#$80 = no vibrato)
    bmi @check_pulse_volume       ; skip incrementing SOUND_VOL_TIMER,x if VIBRATO_CTRL,x is negative
    inc SOUND_VOL_TIMER,x         ; VIBRATO_CTRL,x is [#$00-#$03], increment vibrato counter (increments up to VIBRATO_DELAY)
    lda VIBRATO_DELAY,x           ; load vibrato delay amount
    cmp SOUND_VOL_TIMER,x         ; see if vibrato timer has counted up to vibrato delay, if so, start checking vibrato
    bcs @check_pulse_volume       ; branch if SOUND_VOL_TIMER,x < VIBRATO_DELAY,x (vibrato hasn't started)
    jsr pulse_sustain_note        ; sustain the current pitch with optional vibrato (note: vibrato portion not used in Contra)
                                  ; SOUND_VOL_TIMER >= VIBRATO_DELAY

; see if volume is set or should be lowered
@check_pulse_volume:
    lda SOUND_FLAGS,x        ; load the current sound slot's sound flags
    and #$20                 ; see if volume decrescendo is complete by checking bit 5
    bne @check_volume_source ; branch if bit 5 set, indicating to no longer lower the volume (pause decrescendo)
                             ; bit 5 not set, check where volume should come from, and set volume
    lda SOUND_VOL_ENV,x      ; see if pulse volume range amount bit 7 is set (specifying to decrescendo)
    bmi lower_pulse_volume   ; branch when bit 7 set to lower the pulse volume by using and decrementing PULSE_VOLUME,x

; SOUND_VOL_ENV is greater than or equal to #$00 or decrescendo is complete
; pulse volume control override
@check_volume_source:
    lda SOUND_FLAGS,x               ; re-load the current sound slot's sound flags
    tay                             ; transfer sound flags to the y register
    and #$04                        ; keep bit 2
    bne handle_possible_decrescendo ; branch if bit 2 of the sound flags are set, indicating to use existing PULSE_VOLUME and not pulse_volume_ptr_tbl
                                    ; this method handles when decrescendo should pause and continue

; shapes volume envelope for note
; set new PULSE_VOLUME,x byte from lvl_x_pulse_volume_xx based on LVL_PULSE_VOL_INDEX,x and set pulse 1 and 2 configuration (volume)
; based on newly loaded PULSE_VOLUME,x, UNKNOWN_SOUND_01, and SOUND_CFG_HIGH,x
; called for simple sound commands as well
; CPU address $8154
; input
;  * x - sound channel offset
lvl_config_pulse:
    lda SOUND_VOL_ENV,x          ; pulse_volume_ptr_tbl offset, i.e. the current level music segment volume envelop to use (lvl_x_pulse_volume_xx)
    asl                          ; double since each entry is #$02 bytes
    tay                          ; transfer to offset register
    lda pulse_volume_ptr_tbl,y   ; read the low byte of the lvl_x_pulse_volume_xx address
    sta $e4                      ; set the low byte of the lvl_x_pulse_volume_xx address
    lda pulse_volume_ptr_tbl+1,y ; read the high byte of the lvl_x_pulse_volume_xx address
    sta $e5                      ; set the high byte of the lvl_x_pulse_volume_xx address

lvl_pulse_volume_byte:
    lda LVL_PULSE_VOL_INDEX,x      ; load read offset into lvl_x_pulse_volume_xx
    tay                            ; transfer to offset register
    lda ($e4),y                    ; read byte from lvl_x_pulse_volume_xx
    cmp #$fe                       ; see if reached end of data
    bcs lvl_pulse_volume_ctrl_code ; branch if lvl_x_pulse_volume_xx byte is greater than or equal to #$fe
                                   ; to handle control code
                                   ; #$fe means to set new offset based on next byte (not used in this game)
                                   ; #$ff means to set bit 2 of SOUND_FLAGS,x then exit
    inc LVL_PULSE_VOL_INDEX,x      ; increment lvl_x_pulse_volume_xx read offset
    and #$1f                       ; keep bits ...x xxxx of the lvl_x_pulse_volume_xx byte

; sets PULSE_VOLUME,x value to a, then updates APU_PULSE_CONFIG to one of
;  * (a - UNKNOWN_SOUND_01) | SOUND_CFG_HIGH,x
;  * #$00 | SOUND_CFG_HIGH,x
;  * a | SOUND_CFG_HIGH,x
; input
;  * a - the PULSE_VOLUME,x value
;  * x - current sound slot
set_pulse_config_a:
    sta PULSE_VOLUME,x ; set current lvl_x_pulse_volume_xx byte

; sets APU_PULSE_CONFIG value to one of the following
; only used when setting pulse channel 1 or 2 config register
;  * (PULSE_VOLUME,x - UNKNOWN_SOUND_01) | SOUND_CFG_HIGH,x
;  * #$00 | SOUND_CFG_HIGH,x
;  * PULSE_VOLUME,x | SOUND_CFG_HIGH,x
; input
;  * a - PULSE_VOLUME,x
;  * x - current sound slot
set_pulse_config:
    cmp #$02
    bcc @continue        ; branch if volume is less than #$02
    sec                  ; volume greater than #$02, set carry flag in preparation for subtraction
    sbc UNKNOWN_SOUND_01
    bpl @continue        ; branch if subtraction is a positive answer
    lda #$00             ; a = #$00 (negative volume, just use #$00)

@continue:
    ora SOUND_CFG_HIGH,x       ; merge with high nibble of pulse config value
    jsr ldx_pulse_triangle_reg ; set x to apu channel register [0, 1, 4, 5, 8, #$c]
    bcs @exit                  ; exit if there is already a sound playing on that channel that has priority
    sta APU_PULSE_CONFIG,x     ; set either pulse channel 1 or 2 config
                               ; a is either (PULSE_VOLUME,x - UNKNOWN_SOUND_01) | SOUND_CFG_HIGH,x
                               ; or #$00 | SOUND_CFG_HIGH,x
                               ; or PULSE_VOLUME,x | SOUND_CFG_HIGH,x

@exit:
    ldx SOUND_CURRENT_SLOT ; load current sound slot

handle_sound_code_exit_00:
    rts

; handle lvl_x_pulse_volume_xx byte control code
; #$fe means to set new offset based on next byte (unused in this game)
; #$ff means to set bit 2 of SOUND_FLAGS,x then exit
; input
;  * empty flag, set when lvl_x_pulse_volume_xx byte is #$fe
lvl_pulse_volume_ctrl_code:
    bne disable_lvl_pulse_ctrl_exit ; branch if #$ff, i.e. not #$fe to enable automatic decrescendo logic
                                    ; !(UNUSED) dead code, not ever executed in gameplay
                                    ; no lvl_x_pulse_volume_xx byte is #$fe
    iny                             ; byte is #$fe, increment offset into lvl_x_pulse_volume_xx
    lda ($e4),y                     ; load next byte from lvl_x_pulse_volume_xx
    sta LVL_PULSE_VOL_INDEX,x       ; set new offset
    jsr check_decrescendo_end_pause ; see if the decrescendo should resume and if so update SOUND_FLAGS,x
    jmp lvl_pulse_volume_byte       ; go back to read the next lvl_x_pulse_volume_xx byte

; set bit 2 of SOUND_FLAGS, which indicates to check handle_possible_decrescendo
; setting disables use of pulse_volume_ptr_tbl and instead use automatic decrescendo
disable_lvl_pulse_ctrl_exit:
    lda SOUND_FLAGS,x ; load the current sound slot's sound flags
    ora #$04          ; set bit 2
    sta SOUND_FLAGS,x
    rts

; bit 2 of SOUND_FLAGS,x indicating to grab volume from memory, handling when decrescendo should pause and continue
; input
;  * y - SOUND_FLAGS,x
handle_possible_decrescendo:
    tya                    ; transfer SOUND_FLAGS,x to a
    and #$02               ; keep bit 1
    bne resume_decrescendo ; branch if bit 1 set
                           ; this means both bit 1 and 2 are set, indicating DECRESCENDO_END_PAUSE has triggered
                           ; branching will resume the decrescendo

; pulse channel only
; see if the number of remaining frames in the sound command is less than the decrescendo pause end
; if so, decrescendo should resume, specify this by setting bits 1 and 2 in the SOUND_FLAGS,x
check_decrescendo_end_pause:
    lda SOUND_CMD_LENGTH,x      ; load the remaining length of the sound command
    cmp DECRESCENDO_END_PAUSE,x ; compare remaining length of the sound command to when decrescendo should resume
    bcs @exit                   ; exit if shouldn't resume decrescendo
    lda SOUND_FLAGS,x           ; resume decrescendo, load the current sound slot's sound flags
    ora #$06                    ; set bits 1 and 2
    sta SOUND_FLAGS,x           ; save sound flags now specify that decrescendo should resume

@exit:
    rts

; lowers the pulse volume by using and decrementing PULSE_VOLUME,x
; compare to resume_decrescendo
lower_pulse_volume:
    dec PULSE_VOL_DURATION,x      ; decrement pulse volume decrescendo duration (how many frames to lower the volume)
    bmi @pause_decrescendo        ; if volume decrescendo length elapsed, branch to pause decrescendo
    dec PULSE_VOLUME,x            ; decrement current volume
    bmi handle_sound_code_exit_01 ; branch if volume is negative
    lda PULSE_VOLUME,x            ; re-load volume
    jmp set_pulse_config          ; set pulse channel 1 or 2 config register based on PULSE_VOLUME,x, UNKNOWN_SOUND_01, and SOUND_CFG_HIGH,x

; set bit 5 and bit 2
@pause_decrescendo:
    lda SOUND_FLAGS,x               ; load the current sound slot's sound flags
    ora #$20                        ; set bit 5 (stop decrescendo)
    sta SOUND_FLAGS,x               ; store updated sound flags
    jmp disable_lvl_pulse_ctrl_exit

; set the pulse volume by using and decrementing PULSE_VOLUME,x
; called after DECRESCENDO_END_PAUSE has triggered and the decrescendo starts again
resume_decrescendo:
    dec PULSE_VOLUME,x            ; decrement volume
    beq handle_sound_code_exit_01 ; branch if volume is #$00
    lda PULSE_VOLUME,x            ; re-load volume
    jmp set_pulse_config          ; set pulse channel 1 or 2 config register based on PULSE_VOLUME,x, UNKNOWN_SOUND_01, and SOUND_CFG_HIGH,x

handle_sound_code_exit_01:
    inc PULSE_VOLUME,x ; reset the previous volume level
    rts

; one of two modes (along with read_high_sound_cmd) of parsing sound commands.
; This mode is used for pulse channels only
; read sound byte and if not [#$fd-#$ff] interpret_sound_byte otherwise sound_cmd_routine_03
; SOUND_FLAGS,x is odd, indicating initial sound code byte was < #$30
; CPU address $81e7
read_low_sound_cmd:
    lda ($e0),y               ; read sound_xx byte at current offset
    cmp #$fd                  ; compare to #$fd
    bcc @interpret_sound_byte ; branch if not #$fd, #$fe, nor #$ff
    and #$0f                  ; sound_xx byte is either #$fd, #$fe, or #$ff, keep low nibble
    jmp sound_cmd_routine_03

@interpret_sound_byte:
    jmp interpret_sound_byte ; interprets sound_xx byte

; sustains the current pitch (PULSE_NOTE,x) with optional vibrato (not used in Contra)
; input
;  * y - sound code read offset (always #$00 from handle_sound_code -> load_sound_code_addr) !(HUH)
;  * x - sound slot, either #$00 (pulse 1 channel) or #$01 (pulse 2 channel)
; jungle and hangar level music
pulse_sustain_note:
    tya                       ; transfer sound code read offset (#$00) to a
    pha                       ; backup y to the stack
    ldy SOUND_CHNL_REG_OFFSET ; load sound channel config register offset (#$00, #$04, #$08, or #$0c)
    sec                       ; set carry flag in preparation for subtraction
    sbc VIBRATO_DELAY,x       ; negate vibrato duration (or #$100 - vibrato duration)
                              ; y - VIBRATO_DELAY,x --> #$00 - VIBRATO_DELAY,x
    sta $e4                   ; store result in $e4
    lda VIBRATO_AMOUNT,x      ; load vibrato amount to apply
    and #$f0                  ; keep high nibble
    lsr
    lsr
    lsr
    lsr                       ; move to low nibble
    cmp $e4                   ; compare vibrato amount to negated VIBRATO_DELAY,x
    bne @check_vibrato_ctrl   ; branch if (negated $071e,x) is not equal to ($0180,x >> 4) to skip vibrato
    lda VIBRATO_DELAY,x       ; the following 8 lines of code are never executed in contra meaning no vibrato is used in contra !(UNUSED)
                              ; also not used in Japanese version which has one extra level track 'DEMO'
                              ; load period vibrato adjustment amount
    sta SOUND_VOL_TIMER,x     ; set vibrato counter; increments up to VIBRATO_DELAY before stopping
    inc VIBRATO_CTRL,x        ; increment vibrato control mode [#$00-#$03]
    lda VIBRATO_CTRL,x        ; load vibrato control mode [#$00-#$03]
    cmp #$04                  ; see if vibrato has gone more than #$03
    bcc @check_vibrato_ctrl   ; branch if vibrato control mode has not yet gone past max value (#$03)
    lda #$00                  ; a = #$00
    sta VIBRATO_CTRL,x        ; reset vibrato control mode back to #$00

@check_vibrato_ctrl:
    lda VIBRATO_CTRL,x ; load vibrato control mode [#$00-#$03]
    and #$01           ; keep bit 0
    bne @apply_vibrato ; branch if vibrato amount is odd (#$01 or #$03)
                       ; to add vibrato to note by pitching down (#$01) or up (#$03)
    lda PULSE_NOTE,x   ; vibrato amount is even, load existing pulse period value

; set pulse channel period to a
; pop a from stack
; input
;  * y - SOUND_CHNL_REG_OFFSET
@set_pulse_period:
    sta APU_PULSE_PERIOD,y
    jsr wait               ; execute #$0a nop instructions
    pla                    ; restore y value from stack (by loading into a)
    tay                    ; restore y value from before call
    rts

; VIBRATO_CTRL,x is #$01 or #$03 (odd), add vibrato to note by pitching up or down
@apply_vibrato:
    lda VIBRATO_AMOUNT,x  ; load vibrato amount adjust
    and #$0f              ; keep low nibble
    sta $e4
    lda VIBRATO_CTRL,x    ; reload vibrato amount
    and #$02              ; keep bit 1
    bne @pitch_up         ; branch if vibrato amount is #$03
    lda $e4               ; vibrato amount is #$01, pitching down
                          ; vibrato is #$01, add $e4 (low byte of VIBRATO_AMOUNT,x) to PULSE_NOTE,x (APU pulse period value)
    clc                   ; clear carry in preparation for addition
    adc PULSE_NOTE,x      ; add $e4 to APU pulse period value
    bcc @set_pulse_period ; set pulse channel period to a
    lda #$ff              ; overflow occurred, set maximum period (a = #$ff)
    jmp @set_pulse_period ; set pulse channel period to a

; VIBRATO_CTRL,x is #$03, subtract $e4 (low byte of VIBRATO_AMOUNT,x) from PULSE_NOTE,x (APU pulse period value)
@pitch_up:
    lda PULSE_NOTE,x      ; load note that is sustained or has the vibrato applied to, in Contra only ever sustained
    sec                   ; set carry flag in preparation for subtraction
    sbc $e4               ; subtract low byte of VIBRATO_AMOUNT,x from PULSE_NOTE,x
    jmp @set_pulse_period ; set pulse channel period to a

; called when SOUND_FLAGS,x is not zero
; input
;  * a - SOUND_FLAGS,x
;  * y - sound_xx byte read offset
read_sound_command_00:
    lsr                    ; shift bit 0 of SOUND_FLAGS,x to carry
                           ; (0 = sound_xx command byte >= #$30, 1 = sound_xx command byte 0 < #$30)
    bcs read_low_sound_cmd ; branch if byte 0 of sound_xx was less than #$30
                           ; reads sound byte and if not [#$fd-#$ff] interpret_sound_byte otherwise sound_cmd_routine_03

; sound code starts with byte that is greater than or equal to #$30
; reads the sound byte and handles it
; input
;  * ($e0) - pointer to sound byte
;  * y - sound byte read offset
; output
;  * x - SOUND_CURRENT_SLOT [0-3]
read_high_sound_cmd:
    lda SOUND_CURRENT_SLOT   ; load sound slot index
    cmp #$03                 ; compare to sound slot #$03 (noise/dmc channel)
    beq parse_percussion_cmd ; branch if sound slot #$03 (noise/dmc channel)
    lda ($e0),y              ; not noise channel, load sound byte
    and #$f0                 ; keep high nibble
    cmp #$c0                 ; compare to #$c0
    bcs @regular_sound_cmd   ; branch if high nibble is greater than or equal to #$c0 to process the sound command
    jmp simple_sound_cmd     ; simple sound command, just a note and length multiplier

; sound byte >= #$c0
@regular_sound_cmd:
    and #$30                  ; keep bits ..xx .... of high nibble
    lsr
    lsr
    lsr
    tax
    lda sound_cmd_ptr_tbl,x   ; load low byte of address pointer
    sta $e4                   ; set low byte of address pointer
    lda sound_cmd_ptr_tbl+1,x ; load high byte of address pointer
    sta $e5                   ; set high byte of address pointer
    ldx SOUND_CURRENT_SLOT    ; load current sound slot
    lda ($e0),y               ; load sound code byte
    and #$0f                  ; keep low nibble
    jmp ($e4)                 ; jump to sound_cmd_routine_xx

; only for sound slot #$03 (noise and dmc channel)
parse_percussion_cmd:
    lda ($e0),y              ; load sound code byte
    and #$f0                 ; keep high nibble
    cmp #$f0                 ; see if high nibble is #$f
    bne @continue            ; branch if high nibble isn't #$f
    lda ($e0),y              ; high nibble is #$f
    and #$0f                 ; keep low nibble
    jmp sound_cmd_routine_03 ; high nibble #$f, go to sound_cmd_routine_03 with low nibble
                             ; either #$0e or #$f
                             ; moves to next (child or parent) sound command
                             ; or finished with entire sound command and re-initialize channel

; high nibble isn't #$f
@continue:
    cmp #$d0
    beq @control_nibble_d            ; branch if sound command high nibble is #$0d to determine SOUND_LENGTH_MULTIPLIER
                                     ; and then loop to actually play percussion sound
    jmp calc_cmd_len_play_percussion ; high nibble isn't #$0f nor #$d
                                     ; play percussive sound (dpcm sample)

; high nibble is #$0d (delay command)
; load low nibble and set it as SOUND_LENGTH_MULTIPLIER before looping to actually
; play the percussion sound sample
@control_nibble_d:
    lda ($e0),y                   ; read slot #$03 sound command byte
    and #$0f                      ; keep low nibble
    sta SOUND_LENGTH_MULTIPLIER,x ; set sound length multiplier
    iny                           ; increment sound_xx read offset
    jmp parse_percussion_cmd      ; recursively loop to read next byte of percussion command

; uses low nibble of sound_xx byte to determine sound code to play
; plays dmc sample for percussive track
; also will play sound_02 (bass drum/tom drum) for sound slots 0 and 1 (short percussive tick on noise channel)
play_percussive_sound:
    lda ($e0),y                 ; load sound_xx byte
    lsr
    lsr
    lsr
    lsr                         ; move high nibble to low nibble
    cmp #$0c                    ; see if high nibble was #$0c
    beq @exit                   ; exit if high nibble was #$0c
    tax                         ; transfer percussion_tbl offset to x
    sta PERCUSSION_INDEX_BACKUP ; backup percussion_tbl offset
    lda percussion_tbl,x        ; load sound code based on high nibble from sound_xx
    jsr play_sound              ; play percussion sound (sound_02, sound_25, sound_5a, sound_5b, sound_5c)
    lda PERCUSSION_INDEX_BACKUP ; restore percussion_tbl offset
    cmp #$03                    ; see if shifted sound nibble offset was less than #$03
    bcc @exit                   ; exit if index less than #$03
    lda #$02                    ; shifted sound nibble is greater than or equal to #$03, play sound_02 (bass drum/tom drum) as well
                                ; note that offset 5 (sound_25) is also slot #$05 and will cause sound_02 to not play
    jsr play_sound              ; play sound_02 (short percussive tick)

@exit:
    ldx SOUND_CURRENT_SLOT ; load current sound slot
    rts

; contains sound codes to play the intro theme (#$08 bytes)
; related to music tracks instruments
; CPU address $82cd
;  * sound_02 - percussive tick (bass drum/tom drum)
;  * sound_25 - game intro tune song noise explosion
;  * sound_5a - dmc sample (high hat)
;  * sound_5b - dmc sample (snare)
;  * sound_5c - dmc sample (high hat)
percussion_tbl:
    .byte $02,$5a,$5b,$5a,$5b,$25,$5c,$5d

; low sound command - interprets sound_xx byte
; input
;  * a - sound_xx byte
;  * y - sound code read offset
interpret_sound_byte:
    and #$f0               ; keep high nibble
    cmp #$20               ; see if high nibble is #$20, this is a control byte
    bne @high_nibble_not_2 ; branch if high nibble isn't #$20
    lda ($e0),y            ; high nibble is #$20, this is a control byte, reload sound byte
                           ; #$02 - sets the number of video frames to wait before reading the next sound
                           ; command (`SOUND_LENGTH_MULTIPLIER`) as well as the high nibble of the APU
                           ; configuration register for the sound channel (`SOUND_CFG_HIGH`).
    and #$0f               ; keep low nibble to see if using low nibble for SOUND_LENGTH_MULTIPLIER or the entire next byte
    bne @continue          ; branch if low nibble isn't #$0f to use low nibble for SOUND_LENGTH_MULTIPLIER
    iny                    ; low nibble is #$f, i.e. sound_xx byte is #$2f, use next byte as full byte multiplier
    lda ($e0),y            ; increment sound_xx byte read offset

@continue:
    sta SOUND_LENGTH_MULTIPLIER,x ; store low nibble (or next full byte) in SOUND_LENGTH_MULTIPLIER,x
    iny                           ; increment sound_xx byte read offset
    lda ($e0),y                   ; load new sound byte
    sta SOUND_CFG_HIGH,x          ; store pulse config high nibble value
    iny                           ; increment sound_xx byte read offset
    beq @high_nibble_not_2        ; !(WHY?) I don't think this will branch as y wouldn't go up to #$ff
    jmp read_low_sound_cmd        ; read sound byte and if not [#$fd-#$ff] interpret_sound_byte otherwise sound_cmd_routine_03

; high nibble wasn't 2, see if #$01 (flatten note or set sweep), or not #$01 (@high_nibble_not_1)
; - #$10 will set sweep, #$1x will flatten note
@high_nibble_not_2:
    cmp #$10                        ; see if sound code high nibble is #$10
    bne @high_nibble_not_1          ; branch if the high nibble isn't #$1
                                    ; branching sets command length, apu channel config, and note value
    lda ($e0),y                     ; high nibble is #$1, reload full byte, if #$10 set optional sweep and continue
                                    ; otherwise flatten note (not used in Contra)
    iny                             ; increment sound_xx read offset
    cmp #$10                        ; compare full byte to #$10
    bne @flatten_note               ; branch if full byte of sound_xx isn't #$10 to slightly flatten the note
    lda ($e0),y                     ; sound byte is #$10, load next sound_xx byte for setting optional sweep and continue
    bne @set_sweep                  ; branch if there is a sweep value to load it
    lda SOUND_FLAGS,x               ; no sweep, strip bit 7 (has sweep flag)
                                    ; load the current sound slot's sound flags
    and #$7f                        ; strip bit 7 (has sweep flag)
    sta SOUND_FLAGS,x               ; set new sound flags for sound slot (disable sweep)
    lda #$7f                        ; a = #$7f (pulse 1 channel disable sweep)
    bne @pulse_1_set_sweep_continue ; always branch to continue setting APU registers

; sound byte wasn't #$00, set sweep and pulse 1 decrescendo duration PULSE_VOL_DURATION if sound slot #$04
@set_sweep:
    lda SOUND_FLAGS,x ; load the current sound slot's sound flags
    ora #$80          ; set bit 7
    sta SOUND_FLAGS,x ; set bit 7 (sweep flag)
    lda ($e0),y       ; load APU_PULSE_SWEEP value

; sets the pulse 1 channel PULSE_VOL_DURATION if current sound slot is #$04 (pulse 1 channel)
@pulse_1_set_sweep_continue:
    cpx #$04                 ; see if sound slot 4 (pulse 1 channel)
    bne @set_sweep_continue  ; skip setting duration if not sound slot 4
    sta PULSE_VOL_DURATION+3 ; set slot 3's (noise/dmc channel) volume duration

@set_sweep_continue:
    jsr ldx_pulse_triangle_reg        ; set x to apu channel register [0, 1, 4, 5, 8, #$c]
    bcs @next_high_control_sound_byte ; branch if there is already a sound playing on that channel that has priority
    sta APU_PULSE_SWEEP,x             ; enable or disable sweep

@next_high_control_sound_byte:
    ldx SOUND_CURRENT_SLOT ; load current sound slot
    iny
    jmp read_low_sound_cmd ; read sound byte and if not [#$fd-#$ff] interpret_sound_byte otherwise sound_cmd_routine_03

@flatten_note:
    lda SOUND_FLAGS,x      ; load the current sound slot's sound flags
    ora #$10               ; set bit 4 (slightly flatten note flag)
    sta SOUND_FLAGS,x      ; set new sound slot flag values
    jmp read_low_sound_cmd ; read sound byte and if not [#$fd-#$ff] interpret_sound_byte otherwise sound_cmd_routine_03

; low sound command high nibble of sound code is not #$10
; now will set command length, apu channel config, note value, and then exit
; to allow sound to play for expected duration
@high_nibble_not_1:
    lda SOUND_LENGTH_MULTIPLIER,x ; load sound command length
    sta SOUND_CMD_LENGTH,x        ; set loop counter
    lda ($e0),y                   ; load volume
    cmp #$f8
    bne @set_in_mem_cfg
    iny                           ; sound byte is #$f8, increment sound byte read offset
    lda ($e0),y                   ; load next sound byte

@set_in_mem_cfg:
    lsr
    lsr
    lsr
    lsr                  ; move high nibble to low nibble
    sta SOUND_CFG_LOW,x  ; set new PULSE_VOLUME value to high nibble of sound_xx byte
    lda SOUND_CFG_HIGH,x ; load configuration high byte
    and #$10             ; keep bit 4 (C - constant volume flag)
    beq @dont_set_volume ; branch to restore SOUND_CFG_HIGH,x to not include volume when setting configuration
    lda SOUND_CFG_LOW,x  ; reload high nibble of sound_xx byte
    ora SOUND_CFG_HIGH,x ; merge previous sound byte with high nibble of current sound byte

; set config register ($4000, $4004, or $400c) and period & length register
@set_cfg_period_length:
    jsr ldx_pulse_triangle_reg  ; set x to apu channel register [0, 1, 4, 5, 8, #$c]
    bcs @load_set_period_length ; branch if there is already a sound playing on that channel that has priority
    sta $4000,x                 ; set pulse, triangle, or noise channel configuration

@load_set_period_length:
    ldx SOUND_CURRENT_SLOT ; load current sound slot
    lda ($e0),y            ; read current sound_xx byte
    and #$0f               ; keep low nibble
    sta $ef                ; store high byte (3 bits) of note period ($4003/$4007)
    iny                    ; increment sound_xx read offset
    lda ($e0),y            ; load next sound_xx byte
    sta $ee                ; store low byte of note period ($4002/$4006)
    jmp set_note           ; set note value

; C is set on APU configuration, indicating constant volume, restore full high byte of configuration
@dont_set_volume:
    lda SOUND_CFG_HIGH,x       ; load high nibble for when storing in pulse config register
    jmp @set_cfg_period_length

cfg_triangle_channel:
    lda SOUND_TRIANGLE_CFG  ; load triangle config
    sta APU_TRIANGLE_CONFIG ; set triangle config
    jmp clear_mute_set_note

prep_pulse_set_note:
    lda SOUND_CFG_LOW,x      ; load new PULSE_VOLUME
    jsr set_pulse_config_a   ; sets PULSE_VOLUME,x value to a, then updates APU_PULSE_CONFIG
    lda SOUND_VOL_ENV,x      ; load the pulse volume range amount (low nibble) (how many frames to lower the volume)
    and #$0f                 ; keep low nibble
    sta PULSE_VOL_DURATION,x ; set the pulse volume decrescendo duration (how many frames to lower the volume)
    jmp clear_mute_set_note  ; set note (APU_PULSE_LENGTH) based on sound byte

; play a single note with a specified length change from previous note
; called from read_high_sound_cmd, sound byte high nibble less than #$0c
; sound_xx byte
;  * high nibble - indirect offset into note_period_tbl
;  * low nibble - multiplier to use with previous note's base length
;    for example, if the previous note was #$09 and #$04 and the low nibble is #$04, then note length will be the same
simple_sound_cmd:
    jsr calc_cmd_len_play_percussion ; calculates SOUND_CMD_LENGTH and DECRESCENDO_END_PAUSE
                                     ; doesn't play any percussion since simple_sound_cmd doesn't execute for sound slot #$03
    cpx #$02                         ; compare to sound slot #$02 (triangle channel)
    beq cfg_triangle_channel         ; branch if slot #$02 (triangle channel)
    lda SOUND_VOL_ENV,x              ; pulse_volume_ptr_tbl offset, i.e. the current level music segment to play (lvl_x_pulse_volume_xx)
    bmi prep_pulse_set_note
    lda #$00                         ; a = #$00
    sta LVL_PULSE_VOL_INDEX,x
    sty $e6                          ; backup sound_xx read offset
    jsr lvl_config_pulse             ; read lvl_x_pulse_volume_xx based on LVL_PULSE_VOL_INDEX,x and set pulse 1 and 2 configuration
    ldy $e6                          ; restore sound_xx read offset

clear_mute_set_note:
    lda SOUND_FLAGS,x      ; load the current sound slot's sound flags
    and #$99               ; keep bits x..x x..x, clearing volume and mute flags
    sta SOUND_FLAGS,x      ; update sound flags
    lda ($e0),y            ; load sound_xx byte
    and #$f0               ; keep high nibble
    lsr
    lsr
    lsr                    ; shift high nibble right 3 bits
    tax                    ; transfer to offset register
    tya                    ; transfer sound_xx read offset to a for backing up
    pha                    ; back up sound_xx read offset to stack
    ldy SOUND_CURRENT_SLOT ; load current sound slot
    lda SOUND_PITCH_ADJ,y  ; load sound period value for slot
    beq @continue          ; if loaded value is #$00 branch
    txa                    ; load the high nibble (now in low nibble) from the sound_xx byte
    clc                    ; clear carry in preparation for addition
    adc SOUND_PITCH_ADJ,y  ; add adjustment to offset current note_period_tbl offset
    tax                    ; set the note_period_tbl read offset

@continue:
    pla                       ; restore sound_xx read offset
    tay                       ; restore sound_xx read offset to y
    lda note_period_tbl,x     ; load low period byte music note
    sta $ee                   ; store low byte of note period ($4002/$4006)
    lda note_period_tbl+1,x   ; load high period byte music note
    sta $ef                   ; store high byte (3 bits) of note period ($4003/$4007)
    ldx SOUND_CURRENT_SLOT    ; load current sound slot (!(HUH) this value is overwritten two lines down)
    lda SOUND_PERIOD_ROTATE,x ; load pitch shifting amount
    tax                       ; transfer amount to x

@loop:
    cpx #$04       ; only shift if the value is not #$04
    beq @exit_loop ; exit if SOUND_PERIOD_ROTATE,x is #$04
    lsr $ef        ; shift right high byte (3 bits) of note period ($4003/$4007)
    ror $ee        ; rotate low byte of note period ($4002/$4006)
    inx            ; increment shift counter
    bne @loop      ; branch until reach #$00

@exit_loop:
    ldx SOUND_CURRENT_SLOT  ; load current sound slot
    cpx #$02                ; compare to sound slot #$02 (triangle channel)
    bcs set_note            ; branch if slot #$02 (triangle), #$03 (noise), #$04 (pulse 1), or #$05 (noise)
    lda VIBRATO_CTRL,x      ; sound slot is #$00 (pulse 1) or #$01 (pulse 2), load vibrato control #$80 = no vibrato
    bmi set_note            ; branch to set period and length directly if no vibrato
    lda $ee                 ; load low byte of note period ($4002/$4006)
    sta PULSE_NOTE,x        ; store low byte of note period in memory for later when checking for vibrato
    lda SOUND_FLAGS,x       ; load the current sound slot's sound flags
    and #$10                ; keep bit 4 (slightly flatten note flag)
    beq @load_slot_set_note ; branch if note should not be flattened slightly
    inc PULSE_NOTE,x        ; increase period, which lowers the frequency of the note

; load sound slot and set the period and length registers to specify the note to play
@load_slot_set_note:
    ldx SOUND_CURRENT_SLOT ; load current sound slot

; sets the period and length registers to specify the note to play
; input
;  * $ee - low byte of note period ($4002/$4006)
;  * $ef - high byte (3 bits) of note period ($4003/$4007)
set_note:
    lda SOUND_FLAGS,x ; load the current sound slot's sound flags
    and #$10          ; keep bit 4 (flatten note bit)
    beq @continue_00  ; branch if bit it clear, indicating to not flatten the specified note
    inc $ee           ; increment low byte of note period ($4002/$4006), slightly flattens a note
    bne @continue_00  ; branch if no overflow occurred
    inc $ef           ; increment high byte (3 bits) of note period ($4003/$4007)

@continue_00:
    lda $ef                  ; load high byte (3 bits) of note period ($4003/$4007)
    cpx #$02                 ; compare to sound slot #$02 (triangle channel)
    beq @set_length          ; branch if sound slot #$02 (triangle channel) to set APU_PULSE_LENGTH
    cpx #$05                 ; compare to sound slot #$05 (noise channel)
    beq @continue_01         ; branch if sound slot #$05 (noise channel) to set APU_PULSE_LENGTH
                             ; !(HUH) could have branched to @set_length directly, a already has $ef
    cmp SOUND_PULSE_LENGTH,x ; compare to the current pulse/noise length
    bne @set_length          ; set new length if not already set
    lda SOUND_FLAGS,x        ; load the current sound slot's sound flags
    bmi @continue_01         ; branch if sound flags negative to set APU_PULSE_LENGTH
    lda SOUND_CFG_HIGH,x     ; load high nibble for when storing in pulse config register
    and #$10                 ; keep bits ...x ....
    bne @set_period          ; skip setting APU_PULSE_LENGTH if SOUND_CFG_HIGH,x bit 4 set

@continue_01:
    lda $ef

; set length and high 3 bits of timer
@set_length:
    sta SOUND_PULSE_LENGTH,x   ; set in memory copy of current pulse length
    ora #$08                   ; set bit 0 of high timer to be 1
    jsr ldx_pulse_triangle_reg ; set x to apu channel register [0, 1, 4, 5, 8, #$c]
    bcs @set_period            ; branch if there is already a sound playing on that channel that has priority
    sta APU_PULSE_LENGTH,x     ; set duration and high 3 bits of the pulse, or triangle channel

; set low period
@set_period:
    lda $ee                  ; load low byte of note period ($4002/$4006)
    ldx SOUND_CURRENT_SLOT   ; load current sound slot
    cpx #$02                 ; compare to sound slot #$02 (triangle channel)
    bcs @set_apu_period      ; branch if slot #$02 (triangle), #$03 (noise), #$04 (pulse 1), or #$05 (noise)
    sta SOUND_PULSE_PERIOD,x ; set in memory pulse period value

@set_apu_period:
    jsr ldx_pulse_triangle_reg   ; set x to apu channel register [0, 1, 4, 5, 8, #$c]
    bcs @restore_x_adv_sound_ptr ; branch if there is already a sound playing on that channel that has priority
                                 ; continue to restore x to the sound slot index, update SOUND_CMD_LOW_ADDR value, and exit
    sta APU_PULSE_PERIOD,x       ; update APU pulse period

@restore_x_adv_sound_ptr:
    ldx SOUND_CURRENT_SLOT ; load current sound slot

; simple_sound_cmd - finished parsing 'sound command' and next frame will pick up at new location
; which is just after parsed sound command.
; updates the sound_xx read offset, i.e. SOUND_CMD_LOW_ADDR to point to current read location + 1
; game logic uses load_sound_code_addr to know where to read
; input
;  * y - current sound_xx read offset
;  * $e0 - SOUND_CMD_LOW_ADDR (address low byte)
;  * $e1 - SOUND_CMD_HIGH_ADDR (address high byte)
adv_sound_cmd_addr:
    iny                       ; increment sound_xx sound command read offset
    tya                       ; transfer sound_xx sound command read offset to a
    clc                       ; clear carry in preparation for addition
    adc $e0                   ; add to current read offset address low byte
    sta SOUND_CMD_LOW_ADDR,x  ; set new starting position to read sound_xx data (low byte)
    lda #$00                  ; a = #$00
    adc $e1                   ; add any carry from previous addition to current read offset address high byte
    sta SOUND_CMD_HIGH_ADDR,x ; set new starting position to read sound_xx data (high byte)
    rts

; e.g. sound_1b - level 1 jungle boss siren
restore_parent_sound_cmd_addr:
    lda NEW_SOUND_CODE_LOW_ADDR,x  ; load new sound code address low byte
    sta $e0                        ; set new sound code address low byte
    lda NEW_SOUND_CODE_HIGH_ADDR,x ; load new sound code address high byte
    sta $e1                        ; set new sound code address high byte
    lda SOUND_FLAGS,x              ; load the current sound slot's sound flags
    and #$f7                       ; strip bit 7 (sweep flag)
    sta SOUND_FLAGS,x              ; set the sound slot's sound flags
    ldy #$00
    jmp read_sound_command_01

; sound_cmd_routine_03 - low nibble #$0f
; either initialize sound channel, or finished with 'sound_xx_part' go back to 'parent' sound command and parse it
low_nibble_f:
    lda SOUND_FLAGS,x                 ; load the current sound slot's sound flags
    and #$08
    bne restore_parent_sound_cmd_addr ; branch if bit 3 is set
    lda SOUND_CODE,x                  ; bit 3 not set, load sound code
    sta $e6                           ; backup sound code
    lda #$00

; input
;  * a - sound code (#$00 is always passed in)
;  * x - sound slot offset
exe_channel_init_ptr_tbl_routine:
    sta SOUND_CODE,x             ; clear sound code
    txa                          ; transfer sound slot offset to a for doubling
    asl                          ; double sound slot offset since each entry in channel_init_ptr_tbl is #$02 bytes
    tax                          ; transfer back to x
    lda channel_init_ptr_tbl,x   ; load low byte of address
    sta $e4                      ; store low byte in $e4
    lda channel_init_ptr_tbl+1,x ; load high byte of address
    sta $e5                      ; store high byte in $e5
    ldx SOUND_CURRENT_SLOT       ; restore current sound slot
    jmp ($e4)

; moves to next (child or parent) sound command, or finished with entire sound command and re-initialize channel
; - could be entering a shared sound command used for playing shared sound data across different sound_xx commands (#$fd)
; - could be entering a repeat subcommand used to repeat sound parts (#$fe)
; - could be exiting a shared sound command and need to return to parent sound command (#$ff)
; - could be finished reading entire sound (#$ff)
;  * a - low nibble of sound byte value
sound_cmd_routine_03:
    cmp #$0e                       ; compare low nibble of sound byte to #$e
    beq @repeat_cmd                ; branch if sound command is #$fe to allow repeating a shared sound part ($e0),y+1 times
    bcs low_nibble_f
    jsr move_sound_code_read_addr  ; sound command is #$fd, move to sound command address to shared sound part beginning
    iny                            ; increment sound code read offset from address byte
    tya                            ; transfer sound_xx read offset to a
    clc                            ; clear carry before updating ($e0)'s address
    adc $e0                        ; skip the 2 address bytes that specified SOUND_CMD_LOW_ADDR
    sta NEW_SOUND_CODE_LOW_ADDR,x  ; set sound command return location low byte once shared sound command part specified in move_sound_code_read_addr executes
    lda #$00
    tay
    adc $e1                        ; add any carry from low byte address to high byte
    sta NEW_SOUND_CODE_HIGH_ADDR,x ; set sound command return location high byte once shared sound command part specified in move_sound_code_read_addr executes
    lda SOUND_FLAGS,x              ; load the current sound slot's sound flags
    ora #$08                       ; set bit 3
    sta SOUND_FLAGS,x              ; save sound slot's flags
    jmp @load_sound_code_addr      ; gets the sound_xx pointer for sound slot from SOUND_CMD_LOW_ADDR and stores in ($e0)
                                   ; then begins reading that sound command

; #$fe command, i.e. a repeat command. Allows repeating a section of music a specified number of times
; .byte $fe,$03 ; repeat #$03 times
; .addr sound_3e
@repeat_cmd:
    inc SOUND_REPEAT_COUNT,x         ; increment sound part repeat counter
    lda SOUND_REPEAT_COUNT,x         ; load current sound part repeat counter
    iny                              ; increment sound code read byte offset
    cmp ($e0),y                      ; compare SOUND_REPEAT_COUNT,x to sound code byte
    beq skip_3_read_sound_command_01 ; looped ($e0),y times, don't loop any more, move to next sound command
    bmi @move_sound_code_read_addr   ; branch if SOUND_REPEAT_COUNT,x < number of times to repeat shared sound part
    dec SOUND_REPEAT_COUNT,x         ; not sure if ever executed, shouldn't go past ($e0),y, but if so, decrement and repeat !(WHY?)

@move_sound_code_read_addr:
    jsr move_sound_code_read_addr ; update the sound code read address based on the next two bytes of the sound code

@load_sound_code_addr:
    jsr load_sound_code_addr ; gets the sound_xx pointer for sound slot from SOUND_CMD_LOW_ADDR and stores in ($e0)
                             ; also sets y to point to beginning, i.e. #$00

read_sound_command_01:
    lda SOUND_FLAGS,x       ; load the current sound slot's sound flags
    lsr                     ; shift bit 0 to carry (0 = sound_xx byte >= #$30, 1 = sound_xx byte 0 < #$30)
    bcs @read_low_sound_cmd ; branch if byte 0 of sound_xx was less than #$30
                            ; read sound byte and if not [#$fd-#$ff] interpret_sound_byte otherwise sound_cmd_routine_03
    jmp read_high_sound_cmd ; read sound_xx,y byte and handle it

@read_low_sound_cmd:
    jmp read_low_sound_cmd ; read sound byte and if not [#$fd-#$ff] interpret_sound_byte otherwise sound_cmd_routine_03

; skips the shared sound repeat loop counter (1 byte), and the specified address (2 bytes), then reads next sound command (read_sound_command_01)
; also resets shared sound part repeat counter
; input
;  * x - sound slot index
;  * y - sound byte read offset
skip_3_read_sound_command_01:
    lda #$00                  ; clear a register
    sta SOUND_REPEAT_COUNT,x  ; reset shared sound part repeat counter
    iny
    iny
    iny                       ; skip #$03 bytes of sound_xx code
    tya                       ; transfer sound_xx read offset to a
    clc                       ; clear carry in preparation for addition
    adc $e0                   ; add to sound byte read location's low byte
    sta $e0                   ; set new sound code read location's low byte
    lda #$00
    tay                       ; clear y register
    adc $e1                   ; add any carry from previous addition into high byte of sound byte read location
    sta $e1                   ; set any carry for new read location pointer address
    jmp read_sound_command_01 ; logically same as read_sound_command_00
                              ;  (except SOUND_FLAGS are loaded within read_sound_command_00)

; set sound channel configuration (mute), advance sound command address
; input
;  * a - amount to multiply SOUND_CMD_LENGTH by
;  * y - current sound_xx read offset
sound_cmd_routine_00:
    jsr calc_cmd_delay   ; multiply SOUND_CMD_LENGTH by a
    lda #$00             ; sound config low nibble = #$00 (mute sound channel)
    cpx #$02             ; see if sound slot #$02 (triangle channel)
    beq @continue
    lda SOUND_CFG_HIGH,x ; pulse/noise channels use SOUND_CFG_HIGH,x

@continue:
    jsr ldx_pulse_triangle_reg ; set x to apu channel register [0, 1, 4, 5, 8, #$c]
    bcs @adv_read_addr         ; branch if there is already a sound playing on that channel that has priority
    sta $4000,x                ; set pulse 1, pulse 2, or triangle configuration

@adv_read_addr:
    ldx SOUND_CURRENT_SLOT ; load current sound slot
    lda SOUND_FLAGS,x      ; load the current sound slot's sound flags
    ora #$40               ; set bit 6 (mute flag)
    sta SOUND_FLAGS,x
    jmp adv_sound_cmd_addr ; set the sound_xx command read offset to current read location + 1

; set in memory configuration for channel, set multiplier, and sometimes read_high_sound_cmd
; input
;  * a - low nibble of sound byte value
;  * y - current sound_xx read offset
sound_cmd_routine_01:
    sta SOUND_LENGTH_MULTIPLIER,x        ; store value used to calculate SOUND_CMD_LENGTH
    iny                                  ; increment sound code read offset
    lda ($e0),y                          ; load sound code byte
    cpx #$02                             ; compare current sound slot to sound slot #$02 (triangle channel)
    beq set_sound_triangle_config        ; branch if triangle channel to set triangle config in memory and read_high_sound_cmd
    and #$0f                             ; not triangle sound slot, get low nibble
    sec
    sbc UNKNOWN_SOUND_01
    bpl @set_cfg_read_sound_byte         ; if result is positive set full in memory apu config and read_high_sound_cmd
    lda #$00                             ; used to set SOUND_CODE,x to #$00
    jmp exe_channel_init_ptr_tbl_routine ; initialize sound channel

@set_cfg_read_sound_byte:
    sta SOUND_CFG_LOW,x     ; set result of sound_xx low nibble - UNKNOWN_SOUND_01
    lda ($e0),y             ; load sound code byte
    and #$f0                ; keep high nibble
    sta SOUND_CFG_HIGH,x    ; store high nibble of pulse config value (see set_pulse_config)
    iny                     ; increment sound code read offset
    lda ($e0),y             ; load sound volume envelop control byte
                            ; when bit 7 set, automatic decrescendo, otherwise, will follow pattern from pulse_volume_ptr_tbl
    sta SOUND_VOL_ENV,x     ; set indicator whether or not to lower the volume (see @check_pulse_volume)
    iny                     ; increment sound code read offset
    lda ($e0),y             ; load sound code byte
    and #$0f
    sta UNKNOWN_SOUND_00,x  ; see calc_cmd_len_play_percussion, amount to multiply to SOUND_CMD_LENGTH,x when calculating DECRESCENDO_END_PAUSE,x
    iny
    jmp read_high_sound_cmd ; reads sound_xx,y byte and handles it

; sets in-memory value for triangle configuration SOUND_TRIANGLE_CFG
; called only from sound_cmd_routine_01 for triangle sound slot
; input
;  * a - sound byte value that was the byte after the sound_cmd_routine_01 control byte
set_sound_triangle_config:
    sta SOUND_TRIANGLE_CFG  ; set in memory value for triangle config
    iny
    jmp read_high_sound_cmd ; reads sound_xx,y byte and handles it

; set/adjust pitch, and read_high_sound_cmd
; input
;  * a - low nibble of control byte
;  * y - sound byte read offset
sound_cmd_routine_02:
    cmp #$05                  ; compare low nibble of sound code to #$05
                              ; when less than #$05 it is referring to a sound slot
    bcs @high_val             ; branch if more than #$05
    sta SOUND_PERIOD_ROTATE,x ; when not #$04, the number of times to shift the high byte of note_period_tbl into the low byte
    iny                       ; increment read offset
    jmp read_high_sound_cmd   ; reads sound_xx,y byte and handles it

@high_val:
    cmp #$08
    beq @flip_flatten_note_adv
    cmp #$0b
    beq @set_vibrato_vars_adv
    cmp #$0c
    beq @set_pitch_adj_adv
    iny                        ; unknown low byte, move to next sound byte
    jmp read_high_sound_cmd    ; reads sound_xx,y byte and handles it

; low nibble of control byte is #$08, flip bit specifying whether to slightly flatten note
@flip_flatten_note_adv:
    lda SOUND_FLAGS,x       ; load the current sound slot's sound flags
    eor #$10                ; flip bit 4 (whether or not to slightly flatten note)
    sta SOUND_FLAGS,x
    iny                     ; increment sound_xx read offset
    jmp read_high_sound_cmd ; reads sound_xx,y byte and handles it

; sound_cmd_routine_02 -> low nibble #$b
; set vibrato variables, and move to next sound byte
; jungle and hangar music
@set_vibrato_vars_adv:
    iny                     ; increment sound_xx read offset
    lda ($e0),y             ; load sound_xx byte
    sta VIBRATO_DELAY,x     ; set delay until SOUND_VOL_TIMER has counted up to this value before checking vibrato
    cmp #$ff                ; see if sound_xx byte is #$ff
    beq @end_of_sound_code  ; branch if sound_xx byte is #$ff
    iny                     ; increment sound_xx read offset
    lda ($e0),y             ; load sound_xx byte
    sta VIBRATO_AMOUNT,x    ; set the amount of vibrato to apply
    lda #$00                ; a = #$00
    sta VIBRATO_CTRL,x      ; set vibrato mode to #$00
    iny                     ; increment sound_xx read offset
    jmp read_high_sound_cmd ; loop to read next sound_xx,y byte and handle it

; sound_xx byte is #$ff, read entire sound_xx code
@end_of_sound_code:
    lda #$80                ; disable vibrato check
    sta VIBRATO_CTRL,x      ; set to not use vibrato (0 = yes, #$80 = no)
    iny
    jmp read_high_sound_cmd ; read sound_xx,y byte and handle it

; sound_cmd_routine_02 -> low nibble #$c
; sets the pitch adjustment, and move to next sound byte
@set_pitch_adj_adv:
    iny                     ; increment sound_xx read offset
    lda ($e0),y             ; load sound_xx byte
    asl a                   ; double value since each entry in note_period_tbl is #$02 bytes
    sta SOUND_PITCH_ADJ,x   ; set sound period adjustment (adjusts note frequency/pitch)
    iny                     ; increment sound_xx read offset
    jmp read_high_sound_cmd ; reads sound_xx,y byte and handles it

; called from calc_cmd_len_play_percussion when sound slot is #$03 (noise/dmc channel)
; advance sound_xx read offset, and plays dpcm sample based on low nibble
adv_sound_play_percussive:
    jsr adv_sound_cmd_addr    ; advance the sound_xx read offset (SOUND_CMD_LOW_ADDR) to current read location + 1
    dey                       ; decrement sound_xx read offset (it was incremented by adv_sound_cmd_addr)
    jmp play_percussive_sound ; play appropriate intro sound code based on next sound_xx high nibble

; load sound_xx byte and calculate new SOUND_CMD_LENGTH and DECRESCENDO_END_PAUSE
; for simple_sound_cmd, high nibble is less than #$c
; for read_high_sound_cmd sound slot #$03, also play a percussion sound sample (adv_sound_play_percussive)
; input
;  * x - sound slot index [0-3]
calc_cmd_len_play_percussion:
    lda ($e0),y ; load sound byte
    and #$0f    ; keep low nibble

; input
;  * a - amount (+1) multiplied to SOUND_LENGTH_MULTIPLIER,x to get total delay
;        ex: a = #$03, SOUND_LENGTH_MULTIPLIER,x = #$09 => #$24 == #$04 * #$09
calc_cmd_delay:
    sta $e4                       ; set amount of times to add $0154 to itself
    beq @skip_loop                ; don't loop if multiplier is #$00
    lda SOUND_LENGTH_MULTIPLIER,x

@calc_delay_loop:
    clc                           ; clear carry in preparation for addition
    adc SOUND_LENGTH_MULTIPLIER,x ; add $0154 to itself
    dec $e4                       ; decrement loop counter
    bne @calc_delay_loop          ; loop if not finished adding to itself
    beq @loop_complete            ; break loop if added $0154 $e4 times

@skip_loop:
    lda SOUND_LENGTH_MULTIPLIER,x ; load new loop counter, i.e. SOUND_LENGTH_MULTIPLIER,x * $e4

@loop_complete:
    sta SOUND_CMD_LENGTH,x ; set new $0154 value in $0100
    cpx #$02               ; compare to sound slot #$02 (triangle channel)
    bcs @continue          ; branch if slot #$02 (triangle), #$03 (noise), #$04 (pulse 1), or #$05 (noise)
    lda VIBRATO_CTRL,x     ; load whether or not to use vibrato (0 = yes, #$80 = no)
    bmi @continue          ; skip resetting SOUND_VOL_TIMER,x if VIBRATO_CTRL,x has bit 7 set
    lda #$00
    sta SOUND_VOL_TIMER,x  ; clear SOUND_VOL_TIMER,x value

@continue:
    cpx #$02                        ; compare to sound slot #$02 (triangle channel)
    beq @exit                       ; exit if sound slot #$02 (triangle channel)
    cpx #$03                        ; compare to sound slot #$03 (noise/dmc channel)
    beq adv_sound_play_percussive   ; play dmc sample if sound slot #$03 (noise/dmc channel)
    lda UNKNOWN_SOUND_00,x          ; load sound byte low nibble
    jsr @calc_decrescendo_pause_end ; calculate the high #$02 nibbles of the #$03 nibble result of a * SOUND_CMD_LENGTH,x
    sta DECRESCENDO_END_PAUSE,x     ; set result in DECRESCENDO_END_PAUSE,x

@exit:
    rts

; calculate the high #$02 nibbles of the #$03 nibble multiplication result of a * SOUND_CMD_LENGTH,x
; if the result is less than #$02 nibbles, then #$00 will be returned
; ex: a = #$0a, SOUND_CMD_LENGTH,x = #$24 -> #$0a * #$24 -> #$168 -> #$16
; ex: a = #$06, SOUND_CMD_LENGTH,x = #$24 -> #$06 * #$24 -> #$0d8 -> #$d8
; result: #$16
; input
;  * a - sound byte low nibble
;  * SOUND_CMD_LENGTH,x
; output
;  * a - the high #$02 nibbles of the #$03 nibble multiplication result of a * SOUND_CMD_LENGTH,x
@calc_decrescendo_pause_end:
    and #$0f ; keep low nibble of UNKNOWN_SOUND_00,x
             ; (should already be stripped to low nibble)
    sta $e4  ; set low nibble in $e4
    lda #$00
    sta $e6
    sta $e7

@loop:
    dec $e4                ; decrement multiplier
    bmi @set_e7_exit       ; return high nibble of a
    clc
    lda SOUND_CMD_LENGTH,x
    adc $e6                ; add SOUND_CMD_LENGTH,x to total
    sta $e6                ; store result back in $e6
    bcc @loop              ; branch to loop if no overflow occurred
    inc $e7                ; carry occurred keep track in $e7
    bne @loop              ; always loop

; shift high nibble from a into low nibble of $e7
; any previous overflow is now in the high nibble of $e7
@set_e7_exit:
    asl
    rol $e7
    asl
    rol $e7
    asl
    rol $e7
    asl
    rol $e7
    lda $e7
    rts

; gets the sound_xx pointer for sound slot from SOUND_CMD_LOW_ADDR and stores in ($e0)
; also sets y to point to beginning, i.e. #$00
load_sound_code_addr:
    ldy #$00                  ; reset sound code read offset
    lda SOUND_CMD_LOW_ADDR,x  ; load sound_xx address low byte
    sta $e0                   ; set sound_xx address low byte
    lda SOUND_CMD_HIGH_ADDR,x ; load sound_xx address high byte
    sta $e1                   ; set sound_xx address high byte
    rts

; updates the sound code read address (SOUND_CMD_LOW_ADDR) based on the next two bytes of the sound code
move_sound_code_read_addr:
    iny                       ; increment sound code read offset
    lda ($e0),y               ; load new sound code location low byte read offset
    sta SOUND_CMD_LOW_ADDR,x  ; set new sound code location low byte read offset
    iny                       ; increment sound code read offset
    lda ($e0),y               ; load new sound code location high byte read offset
    sta SOUND_CMD_HIGH_ADDR,x ; set new sound code location high byte read offset
    rts

; get the APU configuration register offset (SOUND_CHNL_REG_OFFSET) for sound slot, e.g. #$01 --> #$04
; if 2 pulse channel 1 sounds are playing, this will set the carry to indicate no way to play sound
; input
;  * x - sound slot
; output
;  * x - sound channel configuration register offset
;  * carry flag - clear to update the apu register, set to not update apu register
;    when set, there is already a sound playing on that channel that has priority
ldx_pulse_triangle_reg:
    pha                    ; backup a on the stack
    cpx #$01               ; compare to sound slot #$02 (pulse channel 2)
    bcc @move_next_apu_reg ; branch if pulse channel 0

; requested register is not for sound slot 0
; exit with x set to SOUND_CHNL_REG_OFFSET and the carry clear
@clc_exit:
    clc                       ; clear carry to signal to update sound register
    ldx SOUND_CHNL_REG_OFFSET ; load sound channel config register offset (#$00, #$04, #$08, or #$0c)
    pla                       ; restore a from stack
    rts

; sound slot is #$00 (pulse channel 1), prefer sound slot #$04 (pulse 1) (higher priority)
@move_next_apu_reg:
    inx
    inx
    inx
    inx
    lda SOUND_CODE,x       ; load sound slot 4's sound code to see if a sound is playing for that slot
    beq @clc_exit          ; exit if no sound is playing in slot #$4, use that slot instead of #$0
                           ; carry will clear and x will be set to SOUND_CHNL_REG_OFFSET
    ldx SOUND_CURRENT_SLOT ; otherwise, load current sound slot, set carry, and exit
    sec                    ; set carry flag to signal to not update sound register
    pla

sound_exit_00:
    rts

; mutes the current sound channel, and for sound slot 1, see if playing boss heart destroyed sound
; if so, play end of level song
; input
;  * x - current sound slot
mute_channel:
    lda #$30                   ; a = #$30 (mute pulse channel register)
    jsr ldx_pulse_triangle_reg ; set x to apu channel register [0, 1, 4, 5, 8, #$c]
    bcs @continue              ; branch if there is already a sound playing on that channel that has priority
    sta $4000,x                ; update pulse channel config (mute pulse channel 1 or 2 register)

@continue:
    ldx SOUND_CURRENT_SLOT      ; load current sound slot
    cpx #$01                    ; compare to sound slot #$01 (pulse 2 channel)
    bne sound_exit_00           ; exit if not sound slot 01
    lda $e6                     ; sound slot #$01 (pulse 2 channel)
    cmp #$57                    ; see if boss heart destroyed - big blast with echo
    bne sound_exit_00           ; exit if not sound_57
    lda LEVEL_END_PLAYERS_ALIVE ; see if any players are alive still at after defeating boss heart
    beq sound_exit_00           ; exit if no players are alive
    lda #$46                    ; a = #$46 (sound_46)
    jsr play_sound              ; play end of level song
                                ; could have been optimized to a jmp and no rts !(OBS)
    rts

init_triangle_channel:
    lda #$0b                ; %0000 1011
    sta APU_STATUS          ; disable triangle channel (while also enabling noise, and pulse channels)
    lda #$00                ; a = #$00
    sta APU_TRIANGLE_CONFIG
    lda #$0f                ; a = #$0f
    sta APU_STATUS          ; re-enable triangle channel (enable noise, triangle, and pulse channels)
    rts

init_pulse_channel:
    ldx SOUND_CHNL_REG_OFFSET     ; load pulse wave channel register offset, i.e. #$04 for second pulse channel #$00 for first
    lda #$30                      ; a = #$30
    sta APU_PULSE_CONFIG,x        ; mute the pulse channel 0 register
    jsr wait                      ; execute #$0a nop instructions
    lda #$7f                      ; bit 7 set to 0 all other bits 1
    sta APU_PULSE_SWEEP,x         ; disable pulse 1 channel sweep
    txa
    lsr
    lsr
    tax
    lda SOUND_CODE,x
    beq sound_code_00             ; branch if sound code is #$00
    ldy SOUND_CHNL_REG_OFFSET     ; load sound channel config register offset (#$00, #$04, #$08, or #$0c)
    jsr mute_unmute_pulse_channel ; mutes/unmutes pulse wave channel based on pause state
    ldx SOUND_CURRENT_SLOT        ; load current sound slot
    rts

; mutes the noise channel
mute_noise_channel:
    lda #$30             ; a = #$30
    sta APU_NOISE_CONFIG ; initialize noise config with no volume
    lda $e6
    cmp #$4a             ; compare to the end credits music
    bne sound_exit_00    ;
    lda #$4e             ; end credits finished, load a = #$4e (sound_4e)
    jsr play_sound       ; play after credits music (presented by konami)
                         ; could have been optimized to jmp with no rts
    rts

sound_code_00:
    ldx SOUND_CURRENT_SLOT ; load current sound slot
    lda $e6
    jmp sound_exit_00

; pointer table for ? (#$07 * #$02 = e bytes)
channel_init_ptr_tbl:
    .addr mute_channel          ; CPU address $8651
    .addr mute_channel          ; CPU address $8651
    .addr init_triangle_channel ; CPU address $8673
    .addr mute_noise_channel    ; CPU address $86a6
    .addr init_pulse_channel    ; CPU address $8683
    .addr mute_noise_channel    ; CPU address $86a6
    .addr mute_channel          ; CPU address $8651 (not sure if possible, only #$06 sound slots) !(WHY?)

; pointer table for ? (#$04 * #$02 = #$08 bytes)
sound_cmd_ptr_tbl:
    .addr sound_cmd_routine_00 ; CPU address $8500 - set sound channel configuration, advance sound command address
    .addr sound_cmd_routine_01 ; CPU address $8522 - set in memory configuration for channel, set multiplier, and sometimes read_high_sound_cmd
    .addr sound_cmd_routine_02 ; CPU address $855c - set/adjust pitch, and read_high_sound_cmd
    .addr sound_cmd_routine_03 ; CPU address $84a2 - move to next (child or parent) sound command, or finished with entire sound command and re-initialize channel

; table for note period to use when writing notes to the APU (#$30 bytes)
; the frequency of the pulse channels is a division of the CPU Clock (1.789773MHz NTSC, 1.662607MHz PAL)
; the output frequency (f) of the generator can be determined by the 11-bit period value (f_pulse) written to $4002-$4003/$4006-$4007
; note that triangle channel is one octave lower
; frequency = cpu_speed / (#$0f * (f_pulse + 1))
; ex: 1789773 / (#$10 * (#$06ae + 1)) => 65.38 Hz
note_period_tbl:
    .byte $ae,$06 ; $06AE - 1,710 - 65.38 Hz (c 2/deep c)
    .byte $4e,$06 ; $064E - 1,614 - 69.26 Hz (c#/d flat 2)
    .byte $f4,$05 ; $05F4 - 1,524 - 73.35 Hz (d 2)
    .byte $9e,$05 ; $059E - 1,438 - 77.74 Hz (d#/e flat 2)
    .byte $4e,$05 ; $054E - 1,358 - 82.31 Hz (e 2)
    .byte $01,$05 ; $0501 - 1,281 - 87.25 Hz (f 2)
    .byte $b9,$04 ; $04B9 - 1,209 - 92.45 Hz (f#/g flat 2)
    .byte $76,$04 ; $0476 - 1,142 - 97.87 Hz (g 2)
    .byte $36,$04 ; $0436 - 1,078 - 103.67 Hz (g#/a flat 2)
    .byte $f9,$03 ; $03F9 - 1,017 - 109.88 Hz (a 2)
    .byte $c0,$03 ; $03C0 - 960 - 116.40 Hz (a#/b flat 2)
    .byte $8a,$03 ; $038A - 906 - 123.33 Hz (b 2)
    .byte $57,$03 ; $0357 - 855 - 130.68 Hz (c 3)
    .byte $27,$03 ; $0327 - 807 - 138.44 Hz (c#/d flat 3)
    .byte $fa,$02 ; $02FA - 762 - 146.61 Hz (d 3)
    .byte $cf,$02 ; $02CF - 719 - 155.36 Hz (d#/e flat 3)
    .byte $a7,$02 ; $02A7 - 679 - 164.50 Hz (e 3)
    .byte $81,$02 ; $0281 - 641 - 174.24 Hz (f 3)
    .byte $5d,$02 ; $025D - 605 - 184.59 Hz (f#/g flat 3)
    .byte $3b,$02 ; $023B - 571 - 195.56 Hz (g 3)
    .byte $1b,$02 ; $021B - 539 - 207.15 Hz (g#/a flat 3)
    .byte $fd,$01 ; $01FD - 509 - 219.33 Hz (a 3)
    .byte $e0,$01 ; $01E0 - 480 - 232.56 Hz (b 3)
    .byte $c5,$01 ; $01C5 - 453 - 246.39 Hz (c 4/middle c)

; 10 nop instructions
wait:
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    rts

; pointer for master lookup table (#$02 bytes)
sound_master_ptr_tbl:
    .addr sound_table_00 ; CPU address $88e8

; set pulse channel duty cycle, volume, and sweep data, mute noise channel
init_pulse_and_noise_channels:
    txa      ; temporarily save current value of x to be restored after function call
    pha      ; push a to stack
    tya      ; temporarily save current value of y to be restored after function call
    pha      ; push a to stack
    lda #$00
    tax

; write #$00 to all sound slots' sound code
@loop:
    sta SOUND_CODE,x
    inx
    cpx #$06
    bcc @loop
    sta UNKNOWN_SOUND_01+4
    sta UNKNOWN_SOUND_01+2
    sta UNKNOWN_SOUND_01      ; adjusts pulse channel control (see set_pulse_config)
    jsr init_triangle_channel ; re-initialize triangle channel
    lda #$30                  ; both duty cycle bits set to 1 (%0011 0000)
    sta APU_PULSE_CONFIG      ; set the duty cycle of pulse 1 channel to 75% high
                              ; duty affects the audio's tone
    jsr wait                  ; execute #$0a nop instructions
    sta APU_PULSE2_CONFIG     ; set the duty cycle of pulse 2 channel to 75% high
    jsr wait                  ; execute #$0a nop instructions
    sta APU_NOISE_CONFIG      ; mute noise channel
    jsr wait                  ; execute #$0a nop instructions
    ldx #$7f                  ; load disable pulse channel sweep value
    stx APU_PULSE_SWEEP       ; disable pulse 1 channel sweep
    jsr wait                  ; execute #$0a nop instructions
    stx APU_PULSE2_SWEEP      ; disable pulse 2 channel sweep
    pla                       ; pop saved value y back from stack
    tay                       ; restore y value from before init_pulse_and_noise_channels
    pla                       ; pop saved value x back from stack
    tax                       ; restore x value from before init_pulse_and_noise_channels
    rts

; reset triangle, pulse, and noise channels
reset_channels:
    jsr init_triangle_channel ; re-initialize triangle channel
    lda #$30                  ; a = #$30
    sta APU_PULSE_CONFIG      ; set constant volume and halt any envelope loops
    jsr wait                  ; execute #$0a nop instructions
    sta APU_PULSE2_CONFIG     ; set constant volume and halt any envelope loops
    jsr wait                  ; execute #$0a nop instructions
    sta APU_NOISE_CONFIG      ; set constant volume and halt any envelope loops
    jsr wait                  ; execute #$0a nop instructions
    ldx #$7f                  ; x = #$7f
    stx APU_PULSE_SWEEP       ; disable pulse 1 channel sweep
    jsr wait                  ; execute #$0a nop instructions
    stx APU_PULSE2_SWEEP      ; disable pulse 2 channel sweep
    rts

; dead code, never called !(UNUSED)
bank_1_unused_label_00:
    txa
    pha
    tya
    pha
    ldx #$00                  ; x = #$00
    stx $e6
    lda SOUND_CODE+4
    beq @pop_and_exit
    stx SOUND_CODE+4          ; set sound channel config register offset (#$00, #$04, #$08, or #$0c)
    stx SOUND_CHNL_REG_OFFSET ; set sound channel config register offset (#$00, #$04, #$08, or #$0c)
    jsr init_pulse_channel

@pop_and_exit:
    pla
    tay
    pla
    tax
    rts

; dead code, never called !(UNUSED)
bank_1_unused_label_01:
    sta UNKNOWN_SOUND_01+2
    sta UNKNOWN_SOUND_01+5
    lda #$00               ; a = #$00
    sta UNKNOWN_SOUND_01   ; reset pulse channel adjustment (see set_pulse_config)
    rts

; plays the specified sound
; input
;  * a - the sound code to play
init_sound_code_vars:
    sta INIT_SOUND_CODE               ; store the sound code to play
    cmp #$01
    bne @check_dmc_init               ; branch if sound code isn't #$01
    jmp init_pulse_and_noise_channels ; sound code #$01, init pulse and noise channels
                                      ; sets pulse channel duty cycle, volume, and sweep data, mute noise channel

@check_dmc_init:
    cmp #$5a                              ; compare sound code to #$5a
    bcc @check_boss_heart_destroyed_sound ; branch if sound code is less than #$5a
    jmp play_dpcm_sample                  ; sound code larger than or equal to #$5a, sound code is a DPCM sample
                                          ; jump to configure DMC (delta modulation channel) and play sample

@check_boss_heart_destroyed_sound:
    cmp #$57                          ; compare to #$57 (sound_57) (boss heart destroyed - big blast with echo)
    bne @check_end_level_sound        ; branch if not boss heart destroyed sound
    jsr init_pulse_and_noise_channels ; sound code #$57 - boss heart destroyed, initialize pulse and noise channels
                                      ; sets pulse channel duty cycle, volume, and sweep data, mute noise channel
    jmp @play_sound                   ; play sound boss heart destroyed - big blast with echo

@check_end_level_sound:
    cmp #$46                    ; compare to #$46 (sound_46) (end of level song)
    bne @check_dmc_play_sound   ; branch to play the sound if not end of level song
    lda SOUND_CODE+1            ; sound code is end of level sound, load sound code of next sound channel
    cmp #$57                    ; wait for SOUND_CODE of next sound channel to clear
    bne @play_end_of_level_tune ; play end of level tune if not already playing it
    rts                         ; SOUND_CODE+1 is #$57, exit

; play end of level tune if not already playing it
@play_end_of_level_tune:
    cmp #$46                  ; see if currently playing end of level song
    bne @check_dmc_play_sound ; continue to play end of level tune if not already playing it
    rts                       ; exit if already playing the end of level tune

; plays a sound from the sound table, but first checks for specific sounds to
; see if dmc counter needs to be cleared
; input
;  * a - sound code to play
@check_dmc_play_sound:
    cmp #$2a                   ; see if starting to play jungle/hangar song
    beq @init_dmc_sample_value ; branch to clear dmc counter before playing sound if jungle/hangar
    cmp #$2e                   ; see if starting to play waterfall waterfall
    bne @play_sound            ; branch to play sound without clearing dmc counter if not waterfall

; jungle, hangar, and waterfall
@init_dmc_sample_value:
    lda #$00            ; a = #$00
    sta APU_DMC_COUNTER ; reset DMC starting value for sample

@play_sound:
    txa                        ; backup x to a
    pha                        ; push a to stack (backup)
    tya                        ; backup y to a
    pha                        ; push a to stack (backup)
    lda sound_master_ptr_tbl   ; load low byte of sound_table_00 (only one entry in sound_master_ptr_tbl)
    sta SOUND_TABLE_PTR        ; store low byte of sound_table_00
    lda sound_master_ptr_tbl+1 ; load high byte of sound_table_00 (only one entry in sound_master_ptr_tbl)
    sta SOUND_TABLE_PTR+1      ; store high byte of sound_table_00
    lda #$03                   ; read counter index (each entry is #$03 bytes)
    sta $ea                    ; set loop counter to 3 so that the entire entry is read

; each entry in sound_master_ptr_tbl is 3 bytes, find offset based on INIT_SOUND_CODE by looping
@loop:
    lda INIT_SOUND_CODE     ; load the sound code to play
    clc                     ; clear carry in preparation for addition
    adc SOUND_TABLE_PTR     ; add INIT_SOUND_CODE to the low byte of the of the sound_table_00 (keeping track of if a carry happens)
    sta SOUND_TABLE_PTR     ; store offset back to SOUND_TABLE_PTR
    lda #$00
    adc SOUND_TABLE_PTR+1   ; add 1 to the high byte if a carry happened when adding INIT_SOUND_CODE to low byte
    sta SOUND_TABLE_PTR+1   ; set new value if overflow
    dec $ea                 ; decrement read calculation counter (3 rounds to get actual offset into sound_table_00)
                            ; this is essentially multiplying INIT_SOUND_CODE by 3 and adding that result to SOUND_TABLE_PTR
    bne @loop               ; continue if haven't calculated final read index
    ldy #$00                ; y = #$00
    sty $eb                 ; set number of bytes read to #$00
    lda (SOUND_TABLE_PTR),y ; read first byte of sound_code entry in the sound_table_00
    lsr
    lsr
    lsr
    and #$03                ; keep bits ...x x... of original byte 0 (control byte) of sound_code entry
                            ; this is the total number of sound slots to fill for the specified sound code
    sta $ea                 ; set how many times to loop load_sound_code_entry

; read the sound code entry and load appropriate variables in memory as part of init_sound_code_vars
load_sound_code_entry:
    lda $eb                   ; load number of entries away from initial entry to read (can be #$00)
    asl                       ; double the value
    clc                       ; clear carry in preparation for addition
    adc $eb                   ; add entry to itself
                              ; since each entry is #$03 bytes, multiplied by #$03 to get new offset
    tay                       ; transfer sound_table_00 read offset to y
    lda (SOUND_TABLE_PTR),y   ; read first byte from sound_table_00 entry triple (control byte)
    and #$07                  ; keep bits .... .xxx (sound slot offset)
    tax                       ; transfer offset to x
    lda INIT_SOUND_CODE       ; load the sound code to play
    cmp SOUND_CODE,x          ; see if another sound code (sound effect) is playing for the current slot
    bcc play_sound_code_exit  ; exit if a existing sound gets priority
    lda #$00                  ; a = #$00
    sta SOUND_CODE,x          ; clear sound code slot value
    iny                       ; increment sound_table_00 read offset
    lda (SOUND_TABLE_PTR),y   ; read low byte of sound_xx address from sound_table_00 triple
    sta SOUND_CMD_LOW_ADDR,x  ; set low byte of sound_xx address
    sta $e8                   ; set low byte of sound_xx address
    iny                       ; increment read offset
    lda (SOUND_TABLE_PTR),y   ; load high byte of sound_xx address
    sta SOUND_CMD_HIGH_ADDR,x ; set high byte of sound_xx address
    sta $e9                   ; set high byte of sound_xx address
    lda #$f8                  ; a = #$f8
    sta SOUND_PULSE_LENGTH,x  ; set pulse length to #$f8 (note length 30)
    lda #$01                  ; a = #$01
    sta SOUND_CMD_LENGTH,x    ; initialize SOUND_CMD_LENGTH to #$01 so that when sound command is read for the first time
                              ; the data is parsed as a new sound and not a sound that's already playing (@check_sound_command)
    cpx #$03                  ; see if sound slot is #$03 or more
    bcs @continue             ; branch if sound slot is #$03 or greater
    cpx #$02                  ; see if sound slot is #$02
    beq @clear_pitch_adj      ; branch if sound slot #$02
    lda #$80                  ; sound slot #$00 or #$01 (pulse channel 1 or 2) set a = #$80
    sta VIBRATO_CTRL,x        ; set to not use vibrato (0 = yes, #$80 = no)

@clear_pitch_adj:
    lda #$00              ; a = #$00
    sta SOUND_PITCH_ADJ,x ; clear sound period adjustment value

@continue:
    lda #$00                 ; a = #$00
    sta SOUND_REPEAT_COUNT,x ; initialize shared sound part repeat counter to #$00
    tay                      ; set sound_xx read offset to #$00
    lda ($e8),y              ; read sound_xx byte 0
    iny                      ; increment sound_xx read offset
    cmp #$30
    bcc @config_channel
    dey                      ; control code greater than or equal to #$30
                             ; y will be #$00 for setting SOUND_FLAGS,x
                             ; indicating to use read_high_sound_cmd
    sty UNKNOWN_SOUND_01+2
    sty UNKNOWN_SOUND_01

@config_channel:
    tya                        ; transfer sound_xx read offset to a
    sta SOUND_FLAGS,x          ; set to either #$00 or #$01 depending whether byte 0 is greater than #$30 of sound_xx
                               ; 0 when sound byte is greater than or equal to #$30, 1 is when sound byte is less than #$30
                               ; this specifies whether the sound commands in the code will be processed as a 'high code', or a 'low code'
    lda INIT_SOUND_CODE        ; load sound code to play
    sta SOUND_CODE,x           ; store sound code to play in sound slot x
    txa                        ; transfer sound slot index to a
    cmp #$01                   ; compare to #$01 (pulse 2 channel)
    bcc move_to_pulse_2        ; branch if pulse 1 channel
    cpx #$05                   ; see if sound slot #$05 (noise channel)
    bne convert_slot_to_offset ; branch if not sound slot #$05 (noise channel)
    lda #$0c                   ; sound slot #$05 (noise channel), set sound channel register offset to #$0c (noise/dmc channel)
    jmp cfg_channel

; converts the channel slot index to the channel register offset
;  * #$00: #$00 (pulse 1 channel)
;  * #$01: #$04 (pulse 2 channel)
;  * #$02: #$08 (triangle channel)
;  * #$03: #$0c (noise/dmc channel)
;  * #$04: #$00 (pulse 1 channel)
;  * #$05: do not call this method for sound slot #$05
; input
;  * a - sound slot index
; output
;  * a - sound channel register offset (#$00, #$04, #$08, or #$0c)
; note: does not work for sound slot #$05, must check if slot #$05 before calling this method
convert_slot_to_offset:
    asl
    asl
    and #$0f ; keep low nibble

; configure pulse or noise channel
cfg_channel:
    tax               ; transfer sound channel register offset to x
    lda #$00          ; a = #$00
    cpx #$08          ; see if sound channel register offset is triangle channel
    beq @set_cfg_exit ; exit if triangle channel
    lda #$30          ; set pulse channel or noise channel to play note indefinitely and that v bits will control volume
                      ; until another value is written to pulse to $4000/$4004

@set_cfg_exit:
    sta $4000,x           ; either set pulse channel or noise channel to #$30 or set triangle channel to #$00
    jsr wait              ; execute #$0a nop instructions
    lda #$7f              ; a = #$7f (disable sweep)
    sta APU_PULSE_SWEEP,x ; disable sweep

play_sound_code_exit:
    inc $eb         ; move to next entry in sound_table_00
    dec $ea         ; load number of additional slots required for sound code
    bpl @load_entry
    pla
    tay
    pla
    tax
    rts

@load_entry:
    jmp load_sound_code_entry

; input
;  * a - sound slot index
;  * x - sound slot
; output
;  * a - sound slot index for pulse 2 channel (#$04)
move_to_pulse_2:
    ora #$04                   ; set bits .... .x..
    tay
    lda SOUND_CODE,y
    bne play_sound_code_exit
    txa                        ; transfer sound slot to a
    jmp convert_slot_to_offset ; determine sound channel register offset for slot

; configure DMC (delta modulation channel) and play DPCM sample from bank 7
; !(BUG?) special sound code #$ff (used by end of snow field level after boss defeated)
; sounds like door sliding opening
;  * dpcm_sample_data_tbl offset is #$94
;  * sampling rate #$03 (5593.04 Hz), no loop
;  * counter length #$77
;  * offset #$97 --> $c000 + (#$97 * #$40) --> $e5c0 --> (collision_box_codes_03)
;  * sample length #$19
play_dpcm_sample:
    rts

dpcm_sample_data_tbl:
    .byte $0f,$2f,$f0,$05 ; sound_5a - sample address $fc00 (dpcm_sample_00) (#$51 bytes)
    .byte $0f,$75,$f3,$25 ; sound_5b - sample address $fcc0 (dpcm_sample_01) (#$251 bytes)
    .byte $0f,$00,$f0,$05 ; sound_5c - sample address $fc00 (dpcm_sample_00) (#$51 bytes)
    .byte $0f

; CPU address $88e8
; main look-up table for sounds and music #$5e * #$03 = #$11a bytes)
; groups of #$03 bytes
; read by @play_sound
; byte 0 - ...y yxxx ->
;  * x - sound slot offset
;  * y - how many sound additional sound codes to play
;        note that subsequent sound codes don't read/use the y bits of their byte 0
; byte 1 and 2 - address to sound data
; see level_vert_scroll_and_song (bank 7)
sound_table_00:
    .byte $00,$f3,$25 ; these bytes are for dpcm_sample_data_tbl, lowest sound code is #$01
                      ; sample address $fcc0 (dpcm_sample_01)

    ; unused, empty/silence (noise/dmc channel)
    ; #$00 additional sound code entries, sound slot #$03
    .byte $03
    .addr sound_01 ; CPU address $8a24

    ; percussive tick (bass drum/tom drum), used by other sound codes (noise channel)
    ; #$00 additional sound code entries, sound slot #$05
    .byte $05
    .addr sound_02 ; CPU address $8a02

    ; player landing on ground or water (pulse 1 channel)
    ; #$01 additional sound code entry, sound slot #$04
    .byte $0c
    .addr sound_03 ; CPU address $8a25

    ; FOOT - player landing on ground or water (noise channel)
    ; #$00 additional sound code entries, sound slot #$05
    .byte $05
    .addr sound_04 ; CPU address $8a36

    ; ROCK - waterfall rock landing on ground (pulse 1 channel)
    ; #$00 additional sound code entries, sound slot #$04
    .byte $04
    .addr sound_05 ; CPU address $8a41

    ; TYPE 1 - unused, keyboard typing in Japanese version of game (pulse 1 channel)
    ; #$01 additional sound code entry, sound slot #$04
    .byte $0c
    .addr sound_06 ; CPU address $8a78

    ; TYPE 1 - unused, keyboard typing in Japanese version of game (noise channel)
    ; #$00 additional sound code entries, sound slot #$05
    .byte $05
    .addr sound_07 ; CPU address $8a82

    ; unused, rumbling (noise channel)
    ; #$00 additional sound code entries, sound slot #$05
    .byte $05
    .addr sound_08 ; CPU address $8a90

    ; FIRE - energy zone fire beam (noise channel)
    ; #$00 additional sound code entries, sound slot #$05
    .byte $05
    .addr sound_09 ; CPU address $8c81

    ; SHOTGUN1 - regular bullet firing (pulse 1 channel)
    ; #$01 additional sound code entry, sound slot #$04
    .byte $0c
    .addr sound_0a ; CPU address $8ab3

    ; SHOTGUN1 - regular bullet firing (noise channel)
    ; #$00 additional sound code entries, sound slot #$05
    .byte $05
    .addr sound_0b ; CPU address $8adc

    ; SHOTGUN2 - M weapon firing, turret man (pulse 1 channel)
    ; #$01 additional sound code entry, sound slot #$04
    .byte $0c
    .addr sound_0c ; CPU address $8b05

    ; SHOTGUN2 - M weapon firing, turret man (noise channel)
    ; #$00 additional sound code entries, sound slot #$05
    .byte $05
    .addr sound_0d ; CPU address $8b32

    ; LASER - L weapon firing (pulse 1 channel)
    ; #$01 additional sound code entry, sound slot #$04
    .byte $0c
    .addr sound_0e ; CPU address $8b59

    ; LASER - L weapon firing (noise channel)
    ; #$00 additional sound code entries, sound slot #$05
    .byte $05
    .addr sound_0f ; CPU address $8b90

    ; PL FIRE - F bullet firing (pulse 1 channel)
    ; #$01 additional sound code entry, sound slot #$04
    .byte $0c
    .addr sound_10 ; CPU address $8bf3

    ; PL FIRE - F bullet firing (noise channel)
    ; #$00 additional sound code entries, sound slot #$05
    .byte $05
    .addr sound_11 ; CPU address $8c07

    ; SPREAD - S bullet firing (pulse 1 channel)
    ; #$01 additional sound code entry, sound slot #$04
    .byte $0c
    .addr sound_12 ; CPU address $8c19

    ; SPREAD - S bullet firing (noise channel)
    ; #$00 additional sound code entries, sound slot #$05
    .byte $05
    .addr sound_13 ; CPU address $8c27

    ; HIBIWARE - bullet shielded wall plating ting (pulse 1 channel)
    ; #$00 additional sound code entries, sound slot #$04
    .byte $04
    .addr sound_14 ; CPU address $8cba

    ; CHAKUCHI - energy zone boss landing (pulse 1 channel)
    ; #$00 additional sound code entries, sound slot #$04
    .byte $04
    .addr sound_15 ; CPU address $8d49

    ; DAMEGE 1 - bullet to metal collision ting (pulse 1 channel)
    ; #$01 additional sound code entry, sound slot #$04
    .byte $0c
    .addr sound_16 ; CPU address $8cd4

    ; DAMEGE 1 - bullet to metal collision ting (noise channel)
    ; #$00 additional sound code entries, sound slot #$05
    .byte $05
    .addr sound_17 ; CPU address $8cf7

    ; DAMEGE 2 - alien heart boss hit (pulse 1 channel)
    ; #$00 additional sound code entries, sound slot #$04
    .byte $04
    .addr sound_18 ; CPU address $8d1c

    ; TEKI OUT - enemy destroyed (pulse 1 channel)
    ; #$00 additional sound code entries, sound slot #$04
    .byte $04
    .addr sound_19 ; CPU address $8d33

    ; HIRAI 1 - ice grenade whistling noise (pulse 1 channel)
    ; #$00 additional sound code entries, sound slot #$04
    .byte $04
    .addr sound_1a ; CPU address $8ddd

    ; SENSOR - level 1 jungle boss siren (pulse 1 channel)
    ; #$00 additional sound code entries, sound slot #$04
    .byte $04
    .addr sound_1b ; CPU address $8d76

    ; KANDEN - electrocution sound (pulse 1 channel)
    ; #$01 additional sound code entry, sound slot #$04
    .byte $0c
    .addr sound_1c ; CPU address $8ea5

    ; KANDEN - electrocution sound (noise channel)
    ; #$00 additional sound code entries, sound slot #$05
    .byte $05
    .addr sound_1d ; CPU address $8ec6

    ; CAR - tank advancing (pulse 1 channel)
    ; #$00 additional sound code entries, sound slot #$04
    .byte $04
    .addr sound_1e ; CPU address $8e2f

    ; POWER UP - pick up weapon item (pulse 1 channel)
    ; #$00 additional sound code entries, sound slot #$04
    .byte $04
    .addr sound_1f ; CPU address $8e47

    ; 1UP - extra life (pulse 1 channel)
    ; #$00 additional sound code entries, sound slot #$04
    .byte $04
    .addr sound_20 ; CPU address $8e5e

    ; HERI - helicopter rotors (pulse 1 channel)
    ; #$02 additional sound code entries, sound slot #$04
    .byte $14
    .addr sound_21 ; CPU address $8ee3

    ; HERI - helicopter rotors (pulse 2 channel)
    ; #$00 additional sound code entries, sound slot #$01
    .byte $01
    .addr sound_21 ; CPU address $8ee3

    ; HERI - helicopter rotors (noise channel)
    ; #$00 additional sound code entries, sound slot #$05
    .byte $05
    .addr sound_23 ; CPU address $8f83

    ; BAKUHA 1 - explosion (noise channel)
    ; #$00 additional sound code entries, sound slot #$05
    .byte $05
    .addr sound_24 ; CPU address $8fc2

    ; BAKUHA 2 - game intro explosion, indoor wall explosion, and island explosion (noise channel)
    ; #$00 additional sound code entries, sound slot #$05
    .byte $05
    .addr sound_25 ; CPU address $9001

    ; TITLE - game intro tune (pulse 1 channel)
    ; #$03 additional sound code entries, sound slot #$00
    .byte $18
    .addr sound_26 ; CPU address $9195

    ; TITLE - game intro tune (pulse 2 channel)
    ; #$00 additional sound code entries, sound slot #$01
    .byte $01
    .addr sound_27 ; CPU address $91ab

    ; TITLE - game intro tune (triangle channel)
    ; #$00 additional sound code entries, sound slot #$02
    .byte $02
    .addr sound_28 ; CPU address $91c3

    ; TITLE - game intro tune (noise/dmc channel)
    ; #$00 additional sound code entries, sound slot #$03
    .byte $03
    .addr sound_29 ; CPU address $91d3

    ; BGM 1 - level 1 jungle and level 7 hangar music (pulse 1 channel)
    ; #$03 additional sound code entries, sound slot #$00
    .byte $18
    .addr sound_2a ; CPU address $9428

    ; BGM 1 - level 1 jungle and level 7 hangar music (pulse 2 channel)
    ; #$00 additional sound code entries, sound slot #$01
    .byte $01
    .addr sound_2b ; CPU address $924e

    ; BGM 1 - level 1 jungle and level 7 hangar music (triangle channel)
    ; #$00 additional sound code entries, sound slot #$02
    .byte $02
    .addr sound_2c ; CPU address $95c7

    ; BGM 1 - level 1 jungle and level 7 hangar music (noise/dmc channel)
    ; #$00 additional sound code entries, sound slot #$03
    .byte $03
    .addr sound_2d ; CPU address $9775

    ; BGM 2 - level 3 waterfall music (pulse 1 channel)
    ; #$03 additional sound code entries, sound slot #$00
    .byte $18
    .addr sound_2e ; CPU address $9985

    ; BGM 2 - level 3 waterfall music (pulse 2 channel)
    ; #$00 additional sound code entries, sound slot #$01
    .byte $01
    .addr sound_2f ; CPU address $9a71

    ; BGM 2 - level 3 waterfall music (triangle channel)
    ; #$00 additional sound code entries, sound slot #$02
    .byte $02
    .addr sound_30 ; CPU address $9b67

    ; BGM 2 - level 3 waterfall music (noise/dmc channel)
    ; #$00 additional sound code entries, sound slot #$03
    .byte $03
    .addr sound_31 ; CPU address $9bce

    ; BGM 3 - level 5 snow field music (pulse 1 channel)
    ; #$03 additional sound code entries, sound slot #$00
    .byte $18
    .addr sound_32 ; CPU address $9ca4

    ; BGM 3 - level 5 snow field music (pulse 2 channel)
    ; #$00 additional sound code entries, sound slot #$01
    .byte $01
    .addr sound_33 ; CPU address $9d32

    ; BGM 3 - level 5 snow field music (triangle channel)
    ; #$00 additional sound code entries, sound slot #$02
    .byte $02
    .addr sound_34 ; CPU address $9d9a

    ; BGM 3 - level 5 snow field music (noise/dmc channel)
    ; #$00 additional sound code entries, sound slot #$03
    .byte $03
    .addr sound_35 ; CPU address $9e1e

    ; BGM 4 - level 6 energy zone (pulse 1 channel)
    ; #$03 additional sound code entries, sound slot #$00
    .byte $18
    .addr sound_36 ; CPU address $9ea8

    ; BGM 4 - level 6 energy zone (pulse 2 channel)
    ; #$00 additional sound code entries, sound slot #$01
    .byte $01
    .addr sound_37 ; CPU address $9f46

    ; BGM 4 - level 6 energy zone (triangle channel)
    ; #$00 additional sound code entries, sound slot #$02
    .byte $02
    .addr sound_38 ; CPU address $9fb8

    ; BGM 4 - level 6 energy zone (noise/dmc channel)
    ; #$00 additional sound code entries, sound slot #$03
    .byte $03
    .addr sound_39 ; CPU address $a003

    ; BGM 5 - level 8 alien's lair music (pulse 1 channel)
    ; #$03 additional sound code entries, sound slot #$00
    .byte $18
    .addr sound_3a ; CPU address $a092

    ; BGM 5 - level 8 alien's lair music (pulse 2 channel)
    ; #$00 additional sound code entries, sound slot #$01
    .byte $01
    .addr sound_3b ; CPU address $a1a7

    ; BGM 5 - level 8 alien's lair music (triangle channel)
    ; #$00 additional sound code entries, sound slot #$02
    .byte $02
    .addr sound_3c ; CPU address $a295

    ; BGM 5 - level 8 alien's lair music (noise/dmc channel)
    ; #$00 additional sound code entries, sound slot #$03
    .byte $03
    .addr sound_3d ; CPU address $a32f

    ; 3D BGM - indoor/base level music (pulse 1 channel)
    ; #$03 additional sound code entries, sound slot #$00
    .byte $18
    .addr sound_3e ; CPU address $a468

    ; 3D BGM - indoor/base level music (pulse 2 channel)
    ; #$00 additional sound code entries, sound slot #$01
    .byte $01
    .addr sound_3f ; CPU address $a570

    ; 3D BGM - indoor/base level music (triangle channel)
    ; #$00 additional sound code entries, sound slot #$02
    .byte $02
    .addr sound_40 ; CPU address $a5eb

    ; 3D BGM - indoor/base level music (noise/dmc channel)
    ; #$00 additional sound code entries, sound slot #$03
    .byte $03
    .addr sound_41 ; CPU address $a67a

    ; BOSS - indoor/base boss screen music (pulse 1 channel)
    ; #$03 additional sound code entries, sound slot #$00
    .byte $18
    .addr sound_42 ; CPU address $a793

    ; BOSS - indoor/base boss screen music (pulse 2 channel)
    ; #$00 additional sound code entries, sound slot #$01
    .byte $01
    .addr sound_43 ; CPU address $a878

    ; BOSS - indoor/base boss screen music (triangle channel)
    ; #$00 additional sound code entries, sound slot #$02
    .byte $02
    .addr sound_44 ; CPU address $a8fb

    ; BOSS - indoor/base boss screen music (noise/dmc channel)
    ; #$00 additional sound code entries, sound slot #$03
    .byte $03
    .addr sound_45 ; CPU address $aa0e

    ; PCLR - end of level tune (pulse 1 channel)
    ; #$03 additional sound code entries, sound slot #$00
    .byte $18
    .addr sound_46 ; CPU address $aa92

    ; PCLR - end of level tune (pulse 2 channel)
    ; #$00 additional sound code entries, sound slot #$01
    .byte $01
    .addr sound_47 ; CPU address $aab3

    ; PCLR - end of level tune (triangle channel)
    ; #$00 additional sound code entries, sound slot #$02
    .byte $02
    .addr sound_48 ; CPU address $aad4

    ; PCLR - end of level tune (noise/dmc channel)
    ; #$00 additional sound code entries, sound slot #$03
    .byte $03
    .addr sound_49 ; CPU address $aaef

    ; ENDING - end credits (pulse 1 channel)
    ; #$03 additional sound code entries, sound slot #$00
    .byte $18
    .addr sound_4a ; CPU address $ac9f

    ; ENDING - end credits (pulse 2 channel)
    ; #$00 additional sound code entries, sound slot #$01
    .byte $01
    .addr sound_4b ; CPU address $ad1a

    ; ENDING - end credits (triangle channel)
    ; #$00 additional sound code entries, sound slot #$02
    .byte $02
    .addr sound_4c ; CPU address $ae05

    ; ENDING - end credits (noise/dmc channel)
    ; #$00 additional sound code entries, sound slot #$03
    .byte $03
    .addr sound_4d ; CPU address $ae87

    ; OVER - game over/after end credits, presented by konami (pulse 1 channel)
    ; #$03 additional sound code entries, sound slot #$00
    .byte $18
    .addr sound_4e ; CPU address $ab34

    ; OVER - game over/after end credits, presented by konami (pulse 2 channel)
    ; #$00 additional sound code entries, sound slot #$01
    .byte $01
    .addr sound_4f ; CPU address $ab5c

    ; OVER - game over/after end credits, presented by konami (triangle channel)
    ; #$00 additional sound code entries, sound slot #$02
    .byte $02
    .addr sound_50 ; CPU address $ab86

    ; OVER - game over/after end credits, presented by konami (noise/dmc channel)
    ; #$00 additional sound code entries, sound slot #$03
    .byte $03
    .addr sound_51 ; CPU address $abb2

    ; PL OUT - player death (pulse 1 channel)
    ; #$01 additional sound code entry, sound slot #$04
    .byte $0c
    .addr sound_52 ; CPU address $9117

    ; PL OUT - player death (noise channel)
    ; #$00 additional sound code entries, sound slot #$05
    .byte $05
    .addr sound_53 ; CPU address $916a

    ; game pausing jingle (pulse 1 channel)
    ; #$00 additional sound code entries, sound slot #$04
    .byte $04
    .addr sound_54 ; CPU address $8a0a

    ; BOSS BK - tank, boss ufo, boss giant, alien guardian destroyed (pulse 1 channel)
    ; #$01 additional sound code entry, sound slot #$04
    .byte $0c
    .addr sound_55 ; CPU address $903c

    ; BOSS BK - tank, boss ufo, boss giant, alien guardian destroyed (noise channel)
    ; #$00 additional sound code entries, sound slot #$05
    .byte $05
    .addr sound_56 ; CPU address $9055

    ; BOSS OUT - boss destroyed (pulse 1 channel)
    ; #$02 additional sound code entries, sound slot #$04
    .byte $14
    .addr sound_57 ; CPU address $9094

    ; BOSS OUT - boss destroyed (pulse 2 channel)
    ; #$00 additional sound code entries, sound slot #$01
    .byte $01
    .addr sound_58 ; CPU address $9098

    ; BOSS OUT - boss destroyed (noise channel)
    ; #$00 additional sound code entries, sound slot #$05
    .byte $05
    .addr sound_59 ; CPU address $90dc

    ; #$00 additional sound code entries, sound slot #$03 (noise/dmc channel)
    .byte $03
    .addr sound_01 ; CPU address $8a24 - 5a

    ; #$00 additional sound code entries, sound slot #$03 (noise/dmc channel)
    .byte $03
    .addr sound_01 ; CPU address $8a24 - 5b

    ; #$00 additional sound code entries, sound slot #$03 (noise/dmc channel)
    .byte $03
    .addr sound_01 ; CPU address $8a24 - 5c

    ; #$00 additional sound code entries, sound slot #$03 (noise/dmc channel)
    .byte $03
    .addr sound_01 ; CPU address $8a24 - 5d

; percussive tick (bass drum/tom drum), used by other sound codes (noise channel)
; CPU address $8a02
sound_02:
    .byte $21,$30,$60,$03,$f8,$10,$01,$ff

; game pausing jingle (pulse 1 channel)
sound_54:
    .byte $25,$82,$00,$d5,$00,$8e,$00,$a9,$22,$b0,$e0,$6a,$d0,$6a,$b0,$6a
    .byte $a0,$6a,$90,$6a,$70,$6a,$50,$6a,$40,$6a

; CPU address $8a24
; unused, empty/silence
sound_01:
    .byte $ff

; player landing on ground or water (pulse 1 channel)
; CPU address $8a25
sound_03:
    .byte $21,$30,$40,$f0,$00,$00,$00,$00,$21,$f0,$f8,$20,$0a,$f8,$10,$0b
    .byte $ff

; FOOT - player landing on ground or water (noise channel)
; CPU address $8a36
sound_04:
    .byte $21,$0f,$a0,$0c,$00,$00,$23,$30,$30,$02,$ff

; ROCK - waterfall rock landing on ground (pulse 1 channel)
; CPU address $8a41
sound_05:
    .byte $21,$70,$10,$83,$f3,$8c,$f2,$f6,$f3,$15,$73,$77,$d3,$8c,$00,$00
    .byte $d3,$15,$00,$00,$d3,$8c,$b3,$45,$33,$11,$b3,$50,$73,$33,$b4,$00
    .byte $00,$00,$b2,$dd,$00,$00,$00,$00,$a3,$50,$00,$00,$73,$22,$00,$00
    .byte $53,$50,$00,$00,$32,$ee,$ff

; TYPE 1 - unused, keyboard typing in Japanese version of game (pulse 1 channel)
; CPU address $8a78
sound_06:
    .byte $26,$30,$10,$99,$60,$8e,$f8,$20,$8e,$ff

; TYPE 1 - unused, keyboard typing in Japanese version of game (noise channel)
; CPU address $8a82
sound_07:
    .byte $21,$30,$b0,$06,$70,$02,$50,$06,$30,$02,$f8,$10,$02,$ff

; unused, rumbling (noise/dmc channel)
; CPU address $8a90
sound_08:
    .byte $21,$30,$c0,$0e,$c0,$0f,$fe,$02
    .addr sound_08

sound_08_part_00:
    .byte $24,$30,$a0,$0f,$90,$0e,$80,$0f,$70,$0f,$60,$0f,$50,$0f,$40,$0f
    .byte $30,$0f,$f8,$20,$0f,$f8,$10,$0f,$ff

; SHOTGUN1 - regular bullet firing (pulse 1 channel)
; CPU address $8ab3
sound_0a:
    .byte $25,$70,$10,$83,$d2,$86,$b0,$c0,$21,$f0,$a0,$09,$25,$70,$60,$f2
    .byte $21,$f0,$a0,$0a,$25,$70,$51,$2b,$41,$76,$31,$d3,$f8,$22,$44,$f8
    .byte $12,$dd,$f8,$13,$99,$f8,$14,$7e,$ff

; SHOTGUN1 - regular bullet firing (noise/dmc channel)
; CPU address $8adc
sound_0b:
    .byte $21,$30,$f0,$09,$d0,$0e,$f8,$20,$0a,$f8,$20,$09,$00,$00,$fe,$02
    .addr sound_0b

; CPU address $8aee
sound_0b_part_00:
    .byte $23,$30,$70,$0b,$f8,$20,$0e,$30,$0e,$f8,$20,$0b,$00,$00,$30,$0a
    .byte $f8,$20,$0d,$f8,$10,$0b,$ff

; SHOTGUN2 - M weapon firing, turret man (pulse 1 channel)
; CPU address $8b05
sound_0c:
    .byte $21,$f0,$10,$83,$c2,$3b,$81,$0d,$71,$c5,$c0,$08,$fe,$02
    .addr sound_0c

sound_0c_part_00:
    .byte $25,$f0,$60,$f2,$21,$f0,$b0,$08,$25,$f0,$51,$2b,$41,$76,$31,$d3
    .byte $f8,$22,$44,$f8,$12,$dd,$f8,$13,$99,$f8,$14,$7e,$ff

; SHOTGUN2 - M weapon firing, turret man (noise/dmc channel)
; CPU address $8b32
sound_0d:
    .byte $21,$30,$f0,$09,$d0,$0e,$f8,$20,$0a,$f8,$10,$09,$fe,$02
    .addr sound_0d

; CPU address $8b42
sound_0d_part_00:
    .byte $23,$30,$70,$0b,$f8,$20,$0e,$30,$0e,$f8,$20,$0b,$00,$00,$30,$0a
    .byte $f8,$20,$0d,$f8,$10,$0b,$ff

; LASER - L weapon firing (pulse 1 channel)
; CPU address $8b59
sound_0e:
    .byte $22,$30,$10,$83,$30,$39,$40,$40,$50,$47,$60,$50,$70,$5a,$80,$65
    .byte $90,$71,$a0,$7f,$a0,$8f,$90,$a0,$90,$b4,$80,$ca,$80,$e2,$80,$fe
    .byte $81,$1d,$71,$40,$71,$68,$61,$94,$61,$c5,$61,$fc,$62,$36,$62,$81
    .byte $52,$cf,$53,$27,$53,$8a,$ff

; LASER - L weapon firing (noise/dmc channel)
; CPU address $8b90
sound_0f:
    .byte $21,$30,$30,$0b,$40,$0a,$50,$09,$60,$08,$70,$07,$70,$06,$80,$06
    .byte $80,$06,$80,$06,$80,$06,$80,$06,$80,$06,$80,$07,$80,$06,$80,$07
    .byte $80,$07,$80,$08,$80,$07,$80,$08,$80,$08,$80,$09,$80,$08,$80,$09
    .byte $80,$09,$80,$0a,$70,$09,$70,$0a,$70,$0a,$70,$0b,$70,$0a,$70,$0b
    .byte $70,$0b,$70,$0c,$70,$0b,$70,$0c,$70,$0c,$60,$0d,$60,$0c,$60,$0d
    .byte $60,$0d,$50,$0e,$50,$0d,$50,$0e,$50,$0e,$50,$0e,$50,$0e,$40,$0e
    .byte $40,$0e,$ff

; PL FIRE - F bullet firing (pulse 1 channel)
; CPU address $8bf3
sound_10:
    .byte $23,$f0,$10,$82,$b0,$35,$90,$50,$70,$78,$fe,$03
    .addr sound_10

sound_10_part_00:
    .byte $30,$b4,$f8,$21,$0d,$ff

; PL FIRE - F bullet firing (noise/dmc channel)
; CPU address $8c07
sound_11:
    .byte $23,$30,$40,$06,$50,$08,$60,$0a,$fe,$03
    .addr sound_11

sound_11_part_00:
    .byte $30,$0c,$f8,$10,$0d,$ff

; SPREAD - S bullet firing (pulse 1 channel)
; CPU address $8c19
sound_12:
    .byte $2a,$30,$10,$8b,$b2,$66,$72,$66,$32,$66,$f8,$12,$66,$ff

; SPREAD - S bullet firing (noise/dmc channel)
; CPU address $8c27
sound_13:
    .byte $21,$30,$b0,$0e,$b0,$0d,$b0,$0c,$b0,$0b,$b0,$0a,$b0,$09,$b0,$08
    .byte $b0,$07,$b0,$06,$b0,$05,$70,$0e,$70,$0d,$70,$0c,$70,$0b,$70,$0a
    .byte $70,$09,$70,$08,$70,$07,$70,$06,$70,$05,$30,$0e,$30,$0d,$30,$0c
    .byte $30,$0b,$30,$0a,$30,$09,$30,$08,$30,$07,$30,$06,$30,$05,$f8,$10
    .byte $0e,$f8,$10,$0d,$f8,$10,$0c,$f8,$10,$0b,$f8,$10,$0a,$f8,$10,$09
    .byte $f8,$10,$08,$f8,$10,$07,$f8,$10,$06,$ff

; FIRE - energy zone fire beam (noise/dmc channel)
; CPU address $8c81
sound_09:
    .byte $22,$30,$f0,$0e,$f0,$0d,$f0,$0c,$a0,$07,$a0,$08,$b0,$09,$c0,$0a
    .byte $c0,$0b,$c0,$0c,$c0,$0d,$23,$30,$f0,$0e,$e0,$0e,$d0,$0e,$c0,$0e
    .byte $b0,$0e,$a0,$0e,$90,$0e,$80,$0e,$70,$0e,$60,$0e,$50,$0e,$40,$0e
    .byte $30,$0e,$f8,$20,$0e,$f8,$10,$0e,$ff

; HIBIWARE - bullet shielded wall plating ting (pulse 1 channel)
; CPU address $8cba
sound_14:
    .byte $21,$30,$90,$20,$c0,$08,$60,$80,$fe,$02
    .addr sound_14

sound_14_part_00:
    .byte $30,$20,$24,$30,$30,$80,$30,$20,$50,$08,$f8,$10,$80,$ff

; DAMEGE 1 - bullet to metal collision ting (pulse 1 channel)
; CPU address $8cd4
sound_16:
    .byte $23,$f0,$10,$82,$b0,$33,$22,$30,$10,$8e,$b0,$66,$70,$5a,$50,$50
    .byte $40,$48,$30,$40,$30,$3f,$f8,$20,$3f,$f8,$20,$3f,$f8,$10,$3f,$f8
    .byte $10,$3f,$ff

; DAMEGE 1 - bullet to metal collision ting (noise/dmc channel)
; CPU address $8cf7
sound_17:
    .byte $21,$30,$d0,$0b,$50,$0a,$30,$09,$70,$0a,$50,$09,$50,$09,$40,$0a
    .byte $40,$0b,$30,$0b,$40,$0b,$30,$0b,$f8,$20,$0b,$f8,$20,$0b,$f8,$10
    .byte $0b,$f8,$10,$0a,$ff

; DAMEGE 2 - alien heart boss hit (pulse 1 channel)
; CPU address $8d1c
sound_18:
    .byte $21,$30,$10,$81,$f0,$59,$24,$f0,$10,$82,$f0,$fe,$c0
    .addr sound_25_part_01

sound_18_part_00:
    .byte $59,$70,$d5,$51,$59,$31,$7f,$ff

; TEKI OUT - enemy destroyed (pulse 1 channel)
; CPU address $8d33
sound_19:
    .byte $28,$b0,$10,$83,$f1,$0d,$28,$f0,$10,$82,$f0,$fe,$c0,$d5,$50,$b3
    .byte $30,$a0,$f8,$10,$a0,$ff

; CHAKUCHI - energy zone boss landing (pulse 1 channel)
; CPU address $8d49
sound_15:
    .byte $23,$b0,$10,$82,$f2,$70,$00,$00,$23,$b0,$f1,$ab,$f1,$67,$e1,$ab
    .byte $d1,$67,$c1,$ab,$b1,$67,$a1,$ab,$91,$67,$81,$ab,$71,$67,$61,$ab
    .byte $51,$67,$41,$ab,$31,$67,$f8,$21,$ab,$f8,$11,$67,$ff

; SENSOR - level 1 jungle boss siren (pulse 1 channel)
; CPU address $8d76
sound_1b:
    .byte $21,$b0,$00,$00,$fd
    .addr sound_1b_part_00
    .byte $fd
    .addr sound_1b_part_00
    .byte $fd
    .addr sound_1b_part_00
    .byte $ff

; CPU address $8d84
sound_1b_part_00:
    .byte $21,$f0,$10,$85,$f8,$12,$e0,$f8,$22,$c0,$32,$a0,$42,$80,$52,$60
    .byte $62,$40,$72,$20,$82,$00,$91,$e0,$a1,$c0,$b1,$a0,$c1,$80,$d1,$60
    .byte $d1,$50,$d1,$48,$d1,$44,$d1,$40,$10,$86

; CPU address $8dae
sound_1b_part_01:
    .byte $e1,$40,$a1,$41,$fe,$0c
    .addr sound_1b_part_01

sound_1b_part_02:
    .byte $b1,$40,$b1,$40,$a1,$40,$a1,$40,$51,$40,$24,$f0,$10,$82,$b1,$40
    .byte $b1,$40,$71,$40,$71,$40,$31,$40,$31,$40,$f8,$11,$40,$f8,$11,$40
    .byte $f8,$11,$40,$f8,$11,$40,$ff

; HIRAI 1 - ice grenade whistling noise (pulse 1 channel)
; CPU address $8ddd
sound_1a:
    .byte $23,$f0,$f8,$10,$1f,$f8,$20,$20,$30,$21,$40,$22,$50,$23,$60,$24
    .byte $70,$25,$80,$26,$90,$27,$a0,$28,$a0,$29,$a0,$2a,$90,$2b,$90,$2c
    .byte $90,$2d,$80,$2e,$80,$2f,$80,$30,$70,$31,$70,$32,$70,$33,$60,$34
    .byte $60,$35,$60,$36,$50,$37,$50,$38,$50,$39,$40,$3a,$40,$3b,$40,$3c
    .byte $30,$3d,$30,$3e,$30,$3f,$30,$40,$f8,$20,$41,$f8,$20,$42,$f8,$20
    .byte $43,$ff

; CAR - tank advancing (pulse 1 channel)
; CPU address $8e2f
sound_1e:
    .byte $21,$b0,$10,$82,$c3,$02,$21,$70,$f8,$20,$66,$21,$b0,$c3,$01,$03
    .byte $01,$c3,$01,$21,$70,$30,$33,$ff

; POWER UP - pick up weapon item (pulse 1 channel)
; CPU address $8e47
sound_1f:
    .byte $28,$b0,$10,$8b,$a3,$fa,$b1,$7d,$70,$7f,$50,$5f,$40,$5f,$30,$5f
    .byte $f8,$20,$5f,$f8,$10,$5f,$ff

; 1UP - extra life (pulse 1 channel)
; CPU address $8e5e
sound_20:
    .byte $22,$30,$f0,$7f,$21,$30,$f0,$7f,$00,$00,$00,$00,$25,$f0,$d0,$3f
    .byte $22,$30,$d0,$7f,$25,$f0,$b0,$3f,$22,$30,$b0,$7f,$25,$f0,$90,$3f
    .byte $22,$30,$90,$7f,$25,$f0,$70,$3f,$22,$30,$70,$7f,$25,$f0,$50,$3f
    .byte $22,$50,$30,$7f,$25,$f0,$30,$3f,$22,$30,$30,$7f,$25,$f0,$f8,$10
    .byte $3f,$22,$30,$f8,$10,$7f,$ff

; KANDEN - electrocution sound (pulse 1 channel)
; CPU address $8ea5
sound_1c:
    .byte $21,$30,$10,$89,$d1,$fd,$fe,$28
    .addr sound_1c

sound_1c_part_00:
    .byte $c1,$fd,$b1,$fd,$b1,$fd,$91,$fd,$91,$fd,$71,$fd,$61,$fd,$51,$fd
    .byte $51,$fd,$31,$fd,$31,$fd,$ff

; KANDEN - electrocution sound (noise/dmc channel)
; CPU address $8ec6
sound_1d:
    .byte $21,$30,$70,$06,$fe,$28
    .addr sound_1d

sound_1d_part_00:
    .byte $60,$06,$60,$06,$50,$06,$50,$06,$50,$06,$40,$06,$40,$06,$40,$06
    .byte $30,$06,$30,$06,$ff

; HERI - helicopter rotors (pulse 1 and pulse 2 channel)
; CPU address $8ee3
sound_21:
    .byte $21,$30,$10,$82,$63,$83,$33,$63,$f8,$23,$53,$00,$00

; CPU address $8ef0
sound_21_part_00:
    .byte $73,$83,$33,$64,$f8,$23,$53,$00,$00,$fe,$0f
    .addr sound_21_part_00

; CPU address $8efd
sound_21_part_01:
    .byte $83,$83,$43,$65,$33,$53,$f8,$13,$33,$fe,$10
    .addr sound_21_part_01

; CPU address $8f0a
sound_21_part_02:
    .byte $93,$83,$43,$66,$33,$53,$f8,$13,$33,$fe,$10
    .addr sound_21_part_02

; CPU address $8f17
sound_21_part_03:
    .byte $a3,$83,$43,$67,$33,$53,$f8,$13,$33,$fe,$10
    .addr sound_21_part_03

; CPU address $8f24
sound_21_part_04:
    .byte $93,$83,$43,$66,$33,$53,$f8,$13,$33,$fe,$08
    .addr sound_21_part_04

; CPU address $8f31
sound_21_part_05:
    .byte $83,$83,$43,$65,$33,$53,$f8,$13,$33,$fe,$08
    .addr sound_21_part_05

; CPU address $8f3e
sound_21_part_06:
    .byte $73,$83,$33,$65,$f8,$23,$53,$00,$00,$fe,$08
    .addr sound_21_part_06

; CPU address $8f4b
sound_21_part_07:
    .byte $63,$83,$33,$63,$f8,$23,$53,$00,$00,$fe,$08
    .addr sound_21_part_07

; CPU address $8f58
sound_21_part_08:
    .byte $53,$83,$f8,$23,$63,$f8,$13,$53,$00,$00,$fe,$08
    .addr sound_21_part_08

; CPU address $8f66
sound_21_part_09:
    .byte $43,$83,$f8,$23,$63,$f8,$13,$53,$00,$00,$fe,$08
    .addr sound_21_part_09

; CPU address $8f74
sound_21_part_0a:
    .byte $33,$83,$f8,$13,$63,$f8,$13,$53,$00,$00,$fe,$08
    .addr sound_21_part_0a
    .byte $ff

; HERI - helicopter rotors (noise/dmc channel)
; CPU address $8f83
sound_23:
    .byte $2e,$30

; CPU address $8f85
sound_23_part_00:
    .byte $f8,$20,$0e,$f8,$20,$0e,$fe,$03
    .addr sound_23_part_00

; CPU address $8f8f
sound_23_part_01:
    .byte $30,$0e,$30,$0e,$fe,$04
    .addr sound_23_part_01

; CPU address $8f97
sound_23_part_02:
    .byte $40,$0e,$40,$0e,$fe,$04
    .addr sound_23_part_02

; CPU address $8f9f
sound_23_part_03:
    .byte $50,$0e,$50,$0e,$fe,$06
    .addr sound_23_part_03

; CPU address $8fa7
sound_23_part_04:
    .byte $40,$0e,$40,$0e,$fe,$04
    .addr sound_23_part_04

; CPU address $8faf
sound_23_part_05:
    .byte $30,$0e,$30,$0e,$fe,$04
    .addr sound_23_part_05

; CPU address $8fb7
sound_23_part_06:
    .byte $f8,$20,$0e,$f8,$20,$0e,$fe,$04
    .addr sound_23_part_06
    .byte $ff

; BAKUHA 1 - explosion (noise/dmc channel)
; CPU address $8fc2
sound_24:
    .byte $21,$30,$f0,$0e,$f0,$0f,$fe,$02
    .addr sound_24

sound_24_part_00:
    .byte $22,$30,$f0,$0f,$f0,$08,$f0,$0f,$f0,$08,$f0,$0f,$f0,$0c,$f0,$0b
    .byte $f0,$0b,$f0,$0b,$e0,$0b,$d0,$0b,$c0,$0d,$b0,$0c,$a0,$0b,$90,$0b
    .byte $b0,$0b,$70,$0b,$60,$0b,$23,$30,$50,$0b,$40,$0b,$30,$0c,$f8,$20
    .byte $0c,$f8,$10,$0b,$ff

; BAKUHA 2 - game intro explosion, indoor wall explosion, and island explosion (noise/dmc channel)
; CPU address $9001
sound_25:
    .byte $21,$30,$f0,$0e,$f0,$0f,$fe,$04
    .addr sound_25

sound_25_part_00:
    .byte $22,$30,$f0,$0f,$f0,$08,$f0,$0f,$27,$30,$f0,$0c,$f0,$0b,$f0,$0b
    .byte $f0,$0b,$e0,$0b,$d0,$0b,$c0,$0d,$b0,$0c,$a0,$0b,$90,$0b,$80,$0b
    .byte $70,$0b,$60,$0c,$50,$0b,$40,$0b,$30,$0c

; CPU address $9035
sound_25_part_01:
    .byte $f8,$20,$0c,$f8,$10,$0b,$ff

; BOSS BK - tank, boss ufo, boss giant, alien guardian destroyed (pulse 1 channel)
; CPU address $903c
sound_55:
    .byte $23,$b0,$10,$83,$d2,$11,$d2,$11,$26,$b0,$c0,$b8,$b0,$bc,$a0,$c0
    .byte $90,$c5,$70,$ca,$50,$cf,$30,$d4,$ff

; BOSS BK - tank, boss ufo, boss giant, alien guardian destroyed (noise channel)
; CPU address $9055
sound_56:
    .byte $21,$30,$f0,$0e,$f0,$0f,$fe,$02
    .addr sound_56

sound_56_part_00:
    .byte $25,$30,$f0,$0f,$f0,$0a,$f0,$0f,$f0,$0a,$f0,$0f,$f0,$0c,$f0,$0c
    .byte $f0,$0b,$f0,$0b,$e0,$0b,$d0,$0c,$c0,$0d,$b0,$0d,$a0,$0c,$90,$0c
    .byte $b0,$0c,$70,$0c,$60,$0c,$23,$30,$50,$0c,$40,$0c,$30,$0d,$f8,$20
    .byte $0d,$f8,$20,$0c,$ff

; BOSS OUT - boss destroyed (pulse 1 channel)
; CPU address $9094
sound_57:
    .byte $21,$b0,$00,$00

; BOSS OUT - boss destroyed (pulse 2 channel)
; CPU address $9098
sound_58:
    .byte $25,$b0,$10,$83,$f1,$fd,$10,$83,$f0,$fe,$2f,$b0,$10,$83,$f0,$fe
    .byte $10,$83,$91,$12,$10,$83,$b1,$23,$10,$83,$d1,$01,$10,$83,$91,$12
    .byte $10,$83,$51,$1d,$10,$83,$41,$2e,$10,$83,$31,$40,$10,$83,$31,$1d
    .byte $10,$83,$f8,$21,$2e,$10,$83,$f8,$21,$40,$10,$83,$f8,$11,$1d,$24
    .byte $b0,$00,$00,$ff

; BOSS OUT - boss destroyed (noise channel)
; CPU address $90dc
sound_59:
    .byte $21,$30,$f0,$0e,$f0,$0f,$fe,$04
    .addr sound_59

sound_59_part_00:
    .byte $22,$30,$f0,$0f,$f0,$08,$f0,$0f,$2a,$30,$f0,$0c,$f0,$0b,$f0,$0b
    .byte $f0,$0b,$e0,$0b,$d0,$0b,$c0,$0d,$b0,$0c,$a0,$0b,$90,$0b,$80,$0b
    .byte $70,$0b,$60,$0c,$50,$0b,$40,$0b,$30,$0c,$f8,$20,$0c,$f8,$10,$0b
    .byte $ff

; PL OUT - player death (pulse 1 channel)
; CPU address $9117
sound_52:
    .byte $23,$f0,$10,$81,$f0,$fe,$70,$fe,$30,$fe,$22,$30,$00,$00,$22,$30
    .byte $10,$83,$f0,$8e,$f0,$97,$f0,$9b,$f0,$ad,$f0,$b7,$f0,$cd,$f0,$d9
    .byte $f0,$f4,$e1,$02,$e1,$21,$e1,$32,$e1,$57,$d1,$6b,$d1,$97,$d1,$af
    .byte $d1,$e4,$c2,$01,$c2,$3f,$c2,$61,$c2,$ab,$b2,$d3,$b3,$2b,$b3,$5b
    .byte $b3,$c4,$b3,$fa,$b4,$76,$b4,$ba,$b5,$4e,$b5,$9e,$b6,$4e,$b6,$ae
    .byte $b6,$ae,$ff

; PL OUT - player death (noise channel)
; CPU address $916a
sound_53:
    .byte $23,$30,$50,$0c,$40,$06,$30,$03,$22,$30,$00,$00,$24,$30,$50,$02
    .byte $50,$03,$50,$04,$50,$05,$50,$06,$50,$07,$60,$08,$60,$09,$60,$0a
    .byte $60,$0b,$70,$0c,$70,$0d,$70,$0e,$70,$0f,$ff

; TITLE - game intro tune (pulse 1 channel)
; CPU address $9195
sound_26:
    .byte $e8,$d9,$f8,$87,$0a,$e3,$03,$d9,$f7,$84,$06,$e2,$93,$73,$23,$da
    .byte $f7,$84,$02,$e2,$4f,$ff

; TITLE - game intro tune (pulse 2 channel)
; CPU address $91ab
sound_27:
    .byte $d9,$39,$86,$0a,$e3,$53,$d9,$3a,$87,$05,$e1,$03,$e2,$b3,$73,$da
    .byte $38,$85,$03,$95,$e1,$21,$47,$ff

; TITLE - game intro tune (triangle channel)
; CPU address $91c3
sound_28:
    .byte $d9,$6f,$e3,$53,$e1,$43,$23,$e2,$b3,$da,$90,$e3,$95,$21,$97,$ff

; TITLE - game intro tune (noise/dmc channel)
; CPU address $91d3
sound_29:
    .byte $d9,$33,$03,$03,$33,$da,$55,$11,$17,$ff

; from pointer table at pulse_volume_ptr_tbl (level 1)
; volume envelop for pulse channel 2 on level 1
lvl_1_pulse_volume_00:
    .byte $05,$06,$07,$06,$05,$04,$03,$ff

; volume control 3, 4, 3, 2 loops
lvl_1_pulse_volume_01:
    .byte $03,$04,$03,$02,$ff

lvl_1_pulse_volume_02:
    .byte $07,$06,$05,$04,$03,$02,$01,$00,$00,$00,$02,$02,$ff

lvl_1_pulse_volume_03:
    .byte $06,$05,$04,$03,$02,$01,$00,$00,$00,$00,$01,$01,$ff

lvl_1_pulse_volume_04:
    .byte $07,$06,$05,$04,$03,$03,$02,$01,$00,$00,$00,$00,$00,$00,$00,$02
    .byte $02,$ff

lvl_1_pulse_volume_05:
    .byte $07,$06,$05,$04,$03,$00,$00,$00,$00,$00,$00,$00,$01,$01,$01,$01
    .byte $01,$01,$ff

lvl_1_pulse_volume_06:
    .byte $05,$04,$03,$02,$01,$01,$00,$00,$00,$00,$00,$00,$01,$01,$01,$01
    .byte $01,$01,$ff

lvl_1_pulse_volume_07:
    .byte $06,$05,$04,$03,$02,$02,$02,$01,$00,$00,$00,$00,$00,$00,$00,$01
    .byte $01,$ff

; BGM 1 - level 1 jungle and level 7 hangar music (pulse 2 channel)
; CPU address $924e
sound_2b:
    .byte $ec,$01,$eb,$2a,$22,$d6,$f7,$84,$00,$e1,$40,$20,$e2,$b0,$90,$b0
    .byte $90,$70,$60,$70,$60,$40,$20,$40,$e3,$90,$b0,$e2,$20

; CPU address $926b
sound_2b_part_00:
    .byte $d6,$f0,$00,$04,$e2,$49,$b0,$c0,$90,$b1,$e1,$10,$2f,$e2,$49,$b0
    .byte $c0,$90,$b1,$e1,$10,$e2,$7e,$c0,$fe,$02
    .addr sound_2b_part_00

sound_2b_part_01:
    .byte $d6,$f7,$02,$00,$e2,$b0,$c0,$d6,$f7,$84,$01,$b2,$e1,$12,$d6,$f7
    .byte $02,$00,$20,$c0,$20,$c0,$d6,$f1,$80,$00,$c0,$20,$c0,$20,$d6,$f7
    .byte $02,$00,$e1,$10,$c0,$d6,$f7,$84,$01,$12,$22,$d6,$f7,$02,$00,$40
    .byte $c0,$40,$c0,$20,$d6,$f7,$84,$01,$42,$d6,$f7,$02,$00,$e2,$b0,$c0
    .byte $d6,$f7,$84,$01,$b2,$e1,$12,$d6,$f7,$02,$00,$20,$c0,$20,$c0,$d6
    .byte $f1,$80,$00,$c0,$20,$c0,$20,$d6,$f7,$02,$00,$e1,$10,$c0,$d6,$f7
    .byte $84,$01,$12,$22,$d6,$f7,$00,$00,$43,$93,$d6,$f7,$84,$00,$e1,$60
    .byte $40,$e0,$10,$e1,$b0,$90,$80,$60,$40,$60,$40,$e1,$10,$e2,$b0,$e1
    .byte $10,$e2,$b0,$90,$80,$eb,$2a,$24,$d6,$f7,$85,$01,$e3,$b2,$c0,$d6
    .byte $f7,$04,$00,$b0,$e2,$11,$20,$61,$41,$20,$11,$e3,$90,$d6,$f7,$84
    .byte $03,$bf,$d6,$f7,$04,$00,$83,$90,$b2,$e2,$13,$20,$42,$63,$80,$91
    .byte $b0,$e1,$13,$e2,$b0,$eb,$2a,$22,$d6,$f7,$84,$03,$e3,$b0,$e2,$20
    .byte $40,$60,$40,$60,$e3,$b1,$b0,$e2,$20,$40,$61,$90,$80,$90,$81,$40
    .byte $6f,$e3,$83,$90,$b2,$e2,$13,$20,$42,$60,$60,$60,$c0,$60,$81,$90
    .byte $e1,$13,$e2,$b3,$d6,$f7,$05,$00,$e2,$90,$90,$90,$92,$90,$90,$90
    .byte $91,$91,$d6,$f7,$84,$03,$82,$d6,$f7,$05,$00,$60,$60,$60,$62,$60
    .byte $60,$60,$61,$61,$d6,$f7,$84,$03,$82,$d6,$f7,$05,$00,$90,$90,$90
    .byte $92,$90,$90,$90,$91,$91,$d6,$f7,$84,$03,$82,$d6,$f7,$05,$00,$60
    .byte $60,$60,$62,$60,$80,$90,$b0,$e1,$10,$e2,$b1,$d6,$f7,$84,$03,$82
    .byte $d6,$f7,$05,$00,$e1,$10,$10,$10,$12,$10,$10,$10,$11,$11,$d6,$f7
    .byte $84,$03,$e2,$b2,$d6,$f7,$05,$00,$90,$90,$90,$92,$90,$90,$90,$91
    .byte $91,$d6,$f7,$84,$03,$b2,$d6,$f7,$05,$00,$e1,$10,$10,$10,$12,$10
    .byte $10,$10,$11,$11,$d6,$f7,$84,$03,$22,$d6,$f7,$05,$00,$40,$40,$40
    .byte $42,$40,$40,$40,$43,$d6,$f8,$00,$00,$e3,$b0,$e2,$20,$40,$60,$40
    .byte $60,$e3,$b1,$b0,$e2,$20,$40,$60,$40,$60,$91,$90,$80,$90,$60,$40
    .byte $60,$e3,$b1,$b0,$e2,$20,$40,$c0,$60,$c0,$80,$c0,$92,$fe,$ff
    .addr sound_2b_part_00

; BGM 1 - level 1 jungle and level 7 hangar music (pulse 1 channel)
; CPU address $9428
sound_2a:
    .byte $ec,$01,$e8,$d6,$f6,$01,$04,$e2,$b0,$90,$60,$40,$60,$40,$20,$10
    .byte $20,$10,$e3,$b0,$90,$90,$40,$60,$90,$d6,$f6,$01,$04

; CPU address $9445
sound_2a_part_00:
    .byte $e3,$b9,$e2,$60,$c0,$40,$61,$70,$9f,$e3,$b9,$e2,$60,$c0,$40,$61
    .byte $80,$2e,$c0,$fe,$02
    .addr sound_2a_part_00

sound_2a_part_01:
    .byte $d6,$f7,$03,$00,$e2,$60,$c0,$62,$82,$90,$c0,$90,$c0,$d6,$b6,$85
    .byte $00,$c0,$e2,$60,$90,$b0,$d6,$f7,$03,$00,$e2,$80,$c0,$82,$92,$b0
    .byte $c0,$b0,$c0,$90,$d6,$f4,$81,$00,$b2,$d6,$f7,$03,$00,$e2,$60,$c0
    .byte $62,$82,$90,$c0,$90,$c0,$d6,$b6,$85,$00,$c0,$e2,$60,$90,$b0,$d6
    .byte $f7,$03,$00,$e2,$80,$c0,$82,$92,$d6,$f5,$83,$00,$b3,$e1,$43,$d6
    .byte $f3,$81,$00,$e1,$60,$40,$60,$40,$e0,$10,$e1,$b0,$90,$80,$60,$40
    .byte $60,$40,$e1,$10,$e2,$b0,$e1,$10,$e2,$b0,$d6,$f5,$83,$03,$e3,$63
    .byte $d6,$f7,$07,$03,$60,$e2,$11,$20,$61,$41,$20,$11,$e3,$90,$d6,$f7
    .byte $86,$00,$e4,$b0,$b0,$b1,$b0,$d6,$f7,$85,$00,$e3,$12,$22,$e4,$b0
    .byte $e3,$40,$62,$d6,$f5,$07,$00,$e3,$43,$60,$82,$93,$b0,$e2,$12,$23
    .byte $20,$41,$60,$93,$80,$d6,$f7,$84,$03,$e3,$b0,$e2,$20,$40,$60,$40
    .byte $60,$e3,$b1,$b0,$e2,$20,$40,$61,$90,$80,$90,$81,$40,$d6,$37,$84
    .byte $03,$e2,$60,$40,$60,$e3,$b1,$b0,$e2,$20,$40,$61,$90,$80,$90,$b1
    .byte $e1,$10,$d6,$f7,$84,$03,$e3,$43,$60,$82,$93,$b0,$e2,$12,$20,$20
    .byte $20,$c0,$20,$41,$60,$93,$83,$d6,$f7,$06,$00,$e2,$60,$60,$60,$62
    .byte $60,$60,$60,$61,$61,$42,$20,$20,$20,$22,$20,$20,$20,$21,$21,$42
    .byte $60,$60,$60,$62,$60,$60,$60,$61,$61,$42,$20,$20,$20,$22,$20,$40
    .byte $60,$80,$90,$81,$42,$90,$90,$90,$92,$90,$90,$90,$91,$91,$82,$60
    .byte $60,$60,$62,$60,$60,$60,$61,$61,$82,$90,$90,$90,$92,$90,$90,$90
    .byte $91,$81,$92,$b0,$b0,$b0,$b2,$b0,$b0,$b0,$b3,$d6,$f6,$00,$00,$e3
    .byte $60,$b0,$e2,$10,$20,$10,$20,$e3,$61,$60,$b0,$e2,$10,$20,$10,$20
    .byte $61,$60,$40,$60,$20,$10,$20,$e3,$61,$60,$b0,$e2,$10,$c0,$d6,$f6
    .byte $01,$04,$20,$c0,$40,$c0,$62,$fe,$ff
    .addr sound_2a_part_00

; BGM 1 - level 1 jungle and level 7 hangar music (triangle channel)
; CPU address $95c7 - jungle/hangar triangle
sound_2c:
    .byte $ec,$01,$d6,$12,$e1,$40,$20,$e2,$b0,$90,$b0,$90,$70,$60,$70,$60
    .byte $40,$20,$40,$e3,$90,$b0,$e2,$20

; CPU address $95df
sound_2c_part_00:
    .byte $d6,$0f,$e3,$b0,$90,$b0,$41,$40,$70,$90,$b0,$90,$b0,$e2,$21,$20
    .byte $10,$20,$e3,$b0,$90,$b0,$41,$40,$70,$90,$b0,$c0,$e2,$20,$e3,$b0
    .byte $e2,$20,$11,$e3,$90,$fe,$03
    .addr sound_2c_part_00

sound_2c_part_01:
    .byte $e3,$b0,$90,$b0,$41,$40,$70,$90,$b0,$90,$b0,$e2,$21,$20,$10,$20
    .byte $e3,$b0,$90,$b0,$41,$40,$70,$90,$b0,$90,$b0,$e2,$21,$20,$40,$60
    .byte $d6,$12,$e3,$b1,$b2,$e2,$12,$21,$e3,$b0,$e2,$41,$60,$90,$b0,$11
    .byte $11,$c0,$22,$41,$41,$20,$d6,$7f,$40,$40,$40,$d6,$12,$e3,$b1,$b2
    .byte $e2,$12,$21,$e3,$b0,$e2,$41,$60,$90,$b0,$11,$12,$22,$e2,$d6,$7f
    .byte $40,$40,$40,$40,$90,$90,$90,$90,$d6,$10,$e1,$60,$40,$e0,$10,$e1
    .byte $b0,$90,$80,$60,$40,$60,$40,$10,$e2,$b0,$e1,$10,$e2,$b0,$90,$80
    .byte $d6,$10,$e3,$b1,$b1,$b0,$e2,$11,$20,$e3,$b1,$e2,$10,$21,$e3,$60
    .byte $90,$a0,$b0,$b0,$b1,$b0,$d6,$1a,$e2,$12,$22,$d6,$10,$e3,$b0,$e2
    .byte $40,$d6,$7f,$60,$60,$60,$d6,$0f,$41,$40,$40,$41,$40,$40,$e3,$91
    .byte $90,$90,$91,$90,$90,$e2,$21,$20,$20,$21,$20,$20,$e3,$61,$60,$60
    .byte $40,$60,$80,$90

; CPU address $96bc
sound_2c_part_02:
    .byte $b1,$b0,$b0,$fe,$04
    .addr sound_2c_part_02

; CPU address $96c3
sound_2c_part_03:
    .byte $e2,$21,$20,$20,$fe,$04
    .addr sound_2c_part_03

sound_2c_part_04:
    .byte $41,$40,$40,$41,$40,$40,$e3,$91,$90,$90,$91,$90,$90,$e2,$20,$20
    .byte $21,$d6,$20,$20,$41,$20,$d6,$3f,$63,$43,$d6,$10,$e2,$60,$60,$60
    .byte $60,$c1,$60,$60,$60,$60,$c0,$60,$c0,$d6,$2f,$42,$d6,$10,$20,$20
    .byte $20,$20,$c1,$20,$20,$20,$20,$c0,$20,$c0,$d6,$2f,$42,$d6,$10,$60
    .byte $60,$60,$60,$c1,$60,$60,$60,$60,$c0,$60,$c0,$d6,$2f,$42,$d6,$10
    .byte $20,$20,$20,$20,$c1,$20,$40,$60,$80,$90,$80,$c0,$d6,$2f,$42,$d6
    .byte $10,$60,$60,$60,$60,$c1,$60,$60,$60,$60,$c0,$60,$c0,$40,$60,$80
    .byte $20,$20,$20,$20,$c1,$20,$20,$20,$20,$c0,$20,$c0,$20,$20,$40,$60
    .byte $60,$60,$60,$c1,$60,$60,$60,$60,$c0,$60,$c0,$20,$40,$60,$40,$40
    .byte $40,$40,$c1,$40,$40,$40,$40,$c1,$c3,$cf,$c7,$d6,$10,$e3,$c0,$60
    .byte $c0,$80,$c0,$d6,$2f,$92,$fe,$ff
    .addr sound_2c_part_00

; BGM 1 - level 1 jungle and level 7 hangar music (noise/dmc channel)
; CPU address $9775
sound_2d:
    .byte $d6,$00,$00,$00,$00,$fe,$03
    .addr sound_2d

; CPU address $977e
sound_2d_part_00:
    .byte $40,$40,$30,$40

; CPU address $9782
sound_2d_part_01:
    .byte $30,$30,$30,$30,$20,$00,$30,$30,$00,$10,$00,$10,$20,$30,$30,$30
    .byte $30,$30,$30,$30,$20,$00,$30,$30,$00,$10,$00,$10,$20,$40,$30,$40
    .byte $fe,$03
    .addr sound_2d_part_01

sound_2d_part_02:
    .byte $30,$30,$30,$30,$20,$00,$30,$30,$00,$10,$00,$10,$20,$30,$30,$30
    .byte $30,$30,$30,$30,$20,$00,$30,$30,$20,$20,$00,$20,$20,$00,$20,$20
    .byte $40,$00,$40,$30,$00,$20,$00,$30,$40,$10,$40,$10,$00,$30,$30,$30
    .byte $40,$00,$40,$30,$00,$40,$00,$30,$40,$10,$40,$10,$40,$40,$30,$30
    .byte $40,$00,$40,$30,$00,$40,$00,$30,$40,$10,$40,$10,$00,$30,$30,$30
    .byte $40,$00,$40,$30,$00,$40,$00,$30,$40,$10,$40,$10,$40,$40,$30,$40
    .byte $30,$00,$00,$00,$10,$00,$00,$00,$30,$00,$00,$00,$40,$00,$40,$40
    .byte $30,$30,$30,$30,$20,$00,$30,$30,$00,$10,$00,$10,$20,$30,$30,$30
    .byte $30,$30,$30,$30,$20,$00,$30,$30,$00,$10,$00,$10,$20,$30,$40,$40
    .byte $30,$30,$30,$30,$20,$00,$30,$30,$00,$10,$00,$10,$20,$30,$30,$30
    .byte $30,$30,$30,$30,$20,$00,$30,$30,$00,$10,$00,$10,$30,$40,$40,$40

; CPU address $9856
sound_2d_part_03:
    .byte $30,$30,$30,$30,$20,$00,$30,$30,$00,$10,$00,$10,$20,$30,$30,$30
    .byte $fe,$03
    .addr sound_2d_part_03

sound_2d_part_04:
    .byte $40,$40,$40,$00,$40,$41,$40,$20,$01,$00,$20,$01,$00

; CPU address $9877
sound_2d_part_05:
    .byte $30,$30,$30,$30,$20,$00,$30,$30,$30,$10,$00,$10,$20,$31,$30,$fe
    .byte $03
    .addr sound_2d_part_05

sound_2d_part_06:
    .byte $30,$30,$30,$30,$20,$00,$40,$40,$40,$20,$40,$20,$10,$40,$30,$30

; CPU address $989a
sound_2d_part_07:
    .byte $30,$30,$30,$30,$20,$00,$30,$30,$30,$10,$00,$10,$20,$31,$30,$fe
    .byte $03
    .addr sound_2d_part_07

sound_2d_part_08:
    .byte $40,$40,$40,$40,$10,$00,$40,$40,$40,$40,$c1,$c3

; CPU address $98b9
sound_2d_part_09:
    .byte $33,$fe,$06
    .addr sound_2d_part_09

sound_2d_part_0a:
    .byte $30,$40,$30,$40,$30,$40,$00,$30,$fe,$ff
    .addr sound_2d_part_01

lvl_3_pulse_volume_07:
    .byte $07,$06,$05,$04,$03,$03,$00,$00,$00,$02,$ff

lvl_4_pulse_volume_00:
    .byte $03,$04,$05,$06,$07,$07,$07,$06,$06,$06,$06,$05,$05,$05,$05,$04
    .byte $04,$04,$04,$03,$ff

lvl_4_pulse_volume_01:
    .byte $06,$07,$06,$05,$04,$03,$ff

lvl_4_pulse_volume_02:
    .byte $06,$07,$06,$05,$04,$03,$00,$00,$00,$00,$01,$ff

lvl_4_pulse_volume_03:
    .byte $04,$05,$06,$05,$04,$03,$ff

lvl_4_pulse_volume_04:
    .byte $04,$05,$04,$03,$ff

lvl_4_pulse_volume_05:
    .byte $03,$04,$03,$03,$03,$03,$00,$00,$00,$00,$01,$ff

lvl_4_pulse_volume_06:
    .byte $04,$05,$06,$05,$04,$03,$ff

lvl_4_pulse_volume_07:
    .byte $08,$07,$06,$05,$04,$03,$00,$00,$00,$00,$01,$ff

lvl_5_pulse_volume_00:
    .byte $ff

; CPU address $9929
sound_2e_part_00:
    .byte $d6,$35,$19,$03,$e2,$41,$d6,$f5,$1d,$02,$50,$71,$d6,$f5,$1c,$02
    .byte $92,$51,$d6,$f5,$1d,$02,$20,$e3,$b1,$d6,$f5,$1e,$04,$e3,$90,$e2
    .byte $70,$d6,$f8,$86,$0a,$e4,$92,$e3,$00,$e4,$90,$e3,$20,$20,$e4,$91
    .byte $e3,$00,$00,$e4,$92,$71,$60,$fe,$02
    .addr sound_2e_part_00

sound_2e_part_01:
    .byte $d6,$f7,$1d,$02,$e2,$91,$70,$90,$b1,$90,$b0,$e1,$01,$e2,$b0,$e1
    .byte $00,$23,$e2,$b1,$70,$b0,$e1,$01,$e2,$b0,$e1,$00,$21,$00,$20,$43
    .byte $ff

; BGM 2 - level 3 waterfall music (pulse 1 channel)
; CPU address $9985
sound_2e:
    .byte $d6,$b8,$18,$01,$e3,$9f,$e2,$2f,$4f,$7f,$d6,$b8,$18,$00,$bf,$d6
    .byte $b3,$80,$01,$bf

; CPU address $9999
sound_2e_part_02:
    .byte $fd
    .addr sound_2e_part_00

sound_2e_part_03:
    .byte $d6,$f8,$87,$00,$e4,$71,$e2,$40,$e4,$90,$90,$e2,$40,$e4,$90,$90
    .byte $e2,$20,$e4,$90,$90,$e2,$00,$e4,$90,$90,$e2,$41,$e4,$71,$e2,$40
    .byte $e4,$90,$90,$e2,$40,$e4,$90,$90,$e2,$20,$e4,$90,$90,$e2,$00,$e4
    .byte $90,$90,$e2,$41,$fd
    .addr sound_2e_part_00

sound_2e_part_04:
    .byte $e8,$d6,$36,$85,$00,$e2,$90,$70,$40,$20,$40,$20,$00,$e3,$90,$e2
    .byte $00,$e3,$90,$70,$90,$c3,$c7,$e8,$d6,$f7,$1f,$02,$e3,$40,$40,$41
    .byte $51,$51,$d6,$36,$83,$02,$e2,$01,$00,$00,$00,$00,$20,$42,$21,$41
    .byte $61,$01,$00,$00,$00,$00,$20,$42,$21,$00,$e3,$b2,$e2,$01,$00,$00
    .byte $00,$00,$20,$42,$21,$41,$61,$00,$20,$40,$21,$40,$60,$41,$60,$70
    .byte $61,$70,$91,$fe,$ff
    .addr sound_2e_part_02

; CPU address $9a2a
sound_2e_part_05:
    .byte $d6,$f7,$19,$02,$e2,$91,$d6,$f7,$1a,$02,$b0,$e1,$01,$d6,$f7,$19
    .byte $02,$22,$e2,$b1,$d6,$f7,$1a,$02,$70,$41,$d6,$f7,$1b,$04,$e2,$90
    .byte $e1,$70,$65,$e2,$90,$e1,$60,$48,$fe,$02
    .addr sound_2e_part_05

sound_2e_part_06:
    .byte $d6,$f7,$19,$03,$e1,$51,$20,$50,$71,$50,$70,$91,$70,$90,$b3,$71
    .byte $40,$70,$91,$70,$90,$b1,$90,$b0,$e0,$03,$ff

; BGM 2 - level 3 waterfall music (pulse 2 channel)
; CPU address $9a71
sound_2f:
    .byte $d6,$f6,$17,$00

; CPU address $9a75
sound_2f_part_00:
    .byte $e1,$70,$40,$60,$71,$70,$40,$60,$70,$40,$60,$71,$70,$40,$60,$fe
    .byte $06
    .addr sound_2f_part_00

; CPU address $9a88
sound_2f_part_01:
    .byte $fd
    .addr sound_2e_part_05

; CPU address $9a8b
sound_2f_part_02:
    .byte $d6,$f7,$1f,$02

; CPU address $9a8f
sound_2f_part_03:
    .byte $e3,$71,$e1,$90,$e2,$90,$90,$e1,$70,$e2,$90,$90,$e1,$60,$e2,$90
    .byte $90,$e1,$40,$e2,$90,$90,$e1,$71,$fe,$02
    .addr sound_2f_part_03
    .byte $fd
    .addr sound_2e_part_05

sound_2f_part_04:
    .byte $d6,$f9,$87,$00,$e1,$90,$70,$40,$20,$40,$20,$00,$e2,$90,$e1,$00
    .byte $e2,$90,$70,$90,$c3,$c7,$d6,$f7,$1f,$02,$e3,$90,$90,$91,$81,$81
    .byte $d6,$f8,$85,$02,$e2,$91,$90,$90,$90,$90,$b0,$e1,$02,$e2,$b1,$e1
    .byte $01,$21,$e2,$91,$90,$90,$90,$90,$b0,$e1,$02,$e2,$b1,$90,$72,$91
    .byte $90,$90,$90,$90,$b0,$e1,$02,$e2,$b1,$e1,$01,$21,$e2,$40,$60,$70
    .byte $61,$70,$90,$71,$90,$b0,$91,$b0,$e1,$01,$fe,$ff
    .addr sound_2f_part_01

; CPU address $9b0c
sound_2f_part_05:
    .byte $d6,$14,$e3,$91,$d6,$0e,$e2,$00,$e3,$90,$e2,$20,$20,$d6,$14,$e3
    .byte $91,$d6,$0e,$e2,$00,$00,$d6,$1b,$e3,$92,$d6,$0f,$71,$80,$fe,$04
    .addr sound_2f_part_05

sound_2f_part_06:
    .byte $d6,$14,$e3,$51,$d6,$0e,$90,$50,$e2,$20,$20,$d6,$14,$e3,$91,$d6
    .byte $0e,$e2,$00,$00,$d6,$1b,$e3,$92,$d6,$0f,$51,$60,$d6,$15,$e3,$71
    .byte $d6,$0e,$b0,$70,$e2,$20,$20,$d6,$14,$e3,$b1,$d6,$0e,$e2,$00,$00
    .byte $d6,$1b,$e3,$92,$d6,$0f,$51,$60,$ff

; BGM 2 - level 3 waterfall music (triangle channel)
; CPU address $9b67
sound_30:
    .byte $d6,$0d,$e2

; CPU address $9b6a
sound_30_part_00:
    .byte $90,$fe,$60
    .addr sound_30_part_00

; CPU address $9b6f
sound_30_part_01:
    .byte $fd
    .addr sound_2f_part_05

; CPU address $9b72
sound_30_part_02:
    .byte $d6,$0f,$e3,$71,$e2,$90,$e3,$90,$90,$e2,$70,$e3,$90,$90,$e2,$60
    .byte $e3,$90,$90,$e2,$40,$e3,$90,$90,$e2,$71,$fe,$02
    .addr sound_30_part_02
    .byte $fd
    .addr sound_2f_part_05

sound_30_part_03:
    .byte $d6,$0f,$e2,$90,$70,$40,$20,$40,$20,$00,$e3,$90,$e2,$00,$e3,$90
    .byte $70,$90,$c3,$c7,$90,$90,$90,$c0,$b0,$c0,$b0,$c0,$d6,$0f,$e2,$91
    .byte $91,$cb,$91,$91,$c7,$71,$71,$91,$91,$cb,$e2,$90,$90,$90,$90,$c2
    .byte $01,$20,$40,$20,$20,$40,$61,$fe,$ff
    .addr sound_30_part_01

; BGM 2 - level 3 waterfall music (noise/dmc channel)
; CPU address $9bce
sound_31:
    .byte $d6

; CPU address $9bcf
sound_31_part_00:
    .byte $00,$fe,$50
    .addr sound_31_part_00

; CPU address $9bd4
sound_31_part_01:
    .byte $40,$fe,$10
    .addr sound_31_part_01

; CPU address $9bd9
sound_31_part_02:
    .byte $30,$10,$30,$30,$40,$30,$00,$30,$31,$30,$30,$40,$31,$30,$30,$10
    .byte $30,$30,$40,$30,$00,$30,$31,$30,$30,$40,$40,$00,$40,$fe,$07
    .addr sound_31_part_02

sound_31_part_03:
    .byte $40,$40,$40,$40,$40,$40,$40,$40,$40,$40,$40,$40,$c3,$40,$42,$33
    .byte $40,$40,$40,$c0,$40,$30,$40,$30,$31,$31,$00,$00,$01,$00,$00,$01
    .byte $00,$02,$31,$31,$00,$00,$01,$00,$00,$01,$01,$01,$31,$31,$00,$00
    .byte $01,$00,$00,$01,$00,$02,$30,$30,$30,$30,$40,$40,$40,$40,$40,$40
    .byte $40,$40,$40,$40,$41,$fe,$ff
    .addr sound_31_part_02

lvl_5_pulse_volume_03:
    .byte $08,$07,$06,$05,$04,$00,$00,$00,$00,$00,$00,$01,$ff

lvl_5_pulse_volume_04:
    .byte $08,$07,$06,$05,$04,$03,$02,$01,$ff

lvl_5_pulse_volume_05:
    .byte $07,$06,$05,$04,$03,$02,$01,$00,$00,$00,$01,$ff

lvl_5_pulse_volume_06:
    .byte $04,$03,$02,$02,$02,$00,$00,$00,$00,$00,$01,$ff

; CPU address $9c71
sound_32_part_00:
    .byte $d6,$f7,$24,$00,$e2,$91,$e1,$21,$31,$20,$01,$e2,$a0,$e1,$01,$e2
    .byte $71,$91,$91,$e1,$21,$31,$20,$51,$30,$71,$e2,$71,$91,$d6,$35,$25
    .byte $00

; CPU address $9c92
sound_32_part_01:
    .byte $e1,$21,$91,$e0,$21,$e1,$91,$fe,$02
    .addr sound_32_part_01

sound_32_part_02:
    .byte $21,$51,$91,$91,$21,$51,$ff

; BGM 3 - level 5 snow field music (pulse 1 channel)
; CPU address $9ca4
sound_32:
    .byte $e8,$d6,$37,$26,$00,$e3

; CPU address $9caa
sound_32_part_03:
    .byte $41,$fe,$10
    .addr sound_32_part_03

sound_32_part_04:
    .byte $e8

; CPU address $9cb0
sound_32_part_05:
    .byte $d6,$f8,$86,$05,$e2,$50,$46,$d6,$36,$84,$0f,$81,$41,$81,$91,$fe
    .byte $04
    .addr sound_32_part_05

sound_32_part_06:
    .byte $d6,$f8,$86,$05,$e2,$80,$76,$d6,$36,$84,$0f,$b1,$71,$b1,$e1,$01
    .byte $fe,$04
    .addr sound_32_part_06

; CPU address $9cd7
sound_32_part_07:
    .byte $d6,$f8,$86,$05,$e2,$b0,$a6,$d6,$36,$84,$0f,$e2,$21,$21,$21,$21
    .byte $d6,$f8,$86,$05,$e1,$10,$06,$d6,$36,$84,$0f,$e2,$41,$41,$41,$41
    .byte $fe,$02
    .addr sound_32_part_07
    .byte $fd
    .addr sound_32_part_00

sound_32_part_08:
    .byte $91,$91,$fd
    .addr sound_32_part_00

sound_32_part_09:
    .byte $93,$fe,$ff
    .addr sound_32_part_05

; CPU address $9d08
sound_32_part_0a:
    .byte $d6,$f7,$24,$00,$e1,$21,$91,$a1,$90,$71,$50,$71,$01,$21,$21,$91
    .byte $a1,$90,$e0,$01,$e1,$a0,$e0,$01,$e1,$01,$2f,$c1,$d6,$35,$25,$00
    .byte $e1,$51,$91,$e0,$21,$01,$e1,$51,$91,$ff

; BGM 3 - level 5 snow field music (pulse 2 channel)
; CPU address $9d32
sound_33:
    .byte $d6,$f7,$23,$00,$e4

; CPU address $9d37
sound_33_part_00:
    .byte $41,$fe,$10
    .addr sound_33_part_00

; CPU address $9d3c
sound_33_part_01:
    .byte $d6,$f8,$86,$05,$e2,$90,$86,$d6,$37,$86,$00,$b1,$91,$b1,$e1,$01
    .byte $fe,$04
    .addr sound_33_part_01

sound_33_part_02:
    .byte $d6,$f8,$86,$05,$e1,$00,$e2,$b6,$d6,$37,$86,$00,$e1,$21,$01,$21
    .byte $31,$fe,$04
    .addr sound_33_part_02

; CPU address $9d65
sound_33_part_03:
    .byte $d6,$f8,$86,$05,$e1,$30,$26,$d6,$37,$86,$00,$e2,$a1,$91,$a1,$e1
    .byte $01,$d6,$f8,$86,$05,$e1,$50,$46,$d6,$37,$86,$00,$e2,$a1,$91,$a1
    .byte $e1,$01,$fe,$02
    .addr sound_33_part_03
    .byte $fd
    .addr sound_32_part_0a

sound_33_part_04:
    .byte $e0,$21,$01,$fd
    .addr sound_32_part_0a

sound_33_part_05:
    .byte $e0,$23,$fe,$ff
    .addr sound_33_part_01

; BGM 3 - level 5 snow field music (triangle channel)
; CPU address $9d9a
sound_34:
    .byte $d6,$0e,$e2

; CPU address $9d9d
sound_34_part_00:
    .byte $41,$fe,$10
    .addr sound_34_part_00

; CPU address $9da2
sound_34_part_01:
    .byte $d6,$0e,$50,$d6,$20,$42,$d6,$0e,$41,$41,$41,$41,$41,$41,$fe,$04
    .addr sound_34_part_01

; CPU address $9db4
sound_34_part_02:
    .byte $d6,$0e,$80,$d6,$20,$72,$d6,$0e,$71,$71,$71,$71,$71,$71,$fe,$04
    .addr sound_34_part_02

; CPU address $9dc6
sound_34_part_03:
    .byte $d6,$0e,$e2,$b0,$d6,$20,$a2,$d6,$0e,$a1,$a1,$a1,$a1,$a1,$a1,$e1
    .byte $10,$d6,$20,$02,$d6,$0e,$01,$01,$01,$01,$01,$01,$fe,$02
    .addr sound_34_part_03

sound_34_part_04:
    .byte $d6,$0e,$e2

; CPU address $9de9
sound_34_part_05:
    .byte $21,$fe,$10
    .addr sound_34_part_05

; CPU address $9dee
sound_34_part_06:
    .byte $21,$91,$fe,$08
    .addr sound_34_part_06

sound_34_part_07:
    .byte $d6,$0e,$e2

; CPU address $9df7
sound_34_part_08:
    .byte $21,$fe,$10
    .addr sound_34_part_08

; CPU address $9dfc
sound_34_part_09:
    .byte $21,$91,$fe,$08
    .addr sound_34_part_09
    .byte $fe,$ff
    .addr sound_34_part_01

; CPU address $9e06
sound_34_part_0a:
    .byte $30,$32,$31,$31,$31,$31,$41,$30,$00,$fe,$03
    .addr sound_34_part_0a

sound_34_part_0b:
    .byte $30,$32,$31,$31,$30,$00,$31,$30,$00,$31,$ff

; BGM 3 - level 5 snow field music (noise/dmc channel)
; CPU address $9e1e
sound_35:
    .byte $d6

; CPU address $9e1f
sound_35_part_00:
    .byte $31,$fe,$10
    .addr sound_35_part_00

; CPU address $9e24
sound_35_part_01:
    .byte $fd
    .addr sound_34_part_0a
    .byte $fd
    .addr sound_34_part_0a

; CPU address $9e2a
sound_35_part_02:
    .byte $30,$32,$31,$31,$31,$31,$41,$30,$00,$fe,$03
    .addr sound_35_part_02

sound_35_part_03:
    .byte $31,$31,$31,$31,$40,$40,$41,$40,$40,$41

; CPU address $9e41
sound_35_part_04:
    .byte $31,$31,$41,$31,$31,$31,$41,$30,$00,$fe,$03
    .addr sound_35_part_04

sound_35_part_05:
    .byte $31,$31,$41,$31,$41,$41,$41,$40,$40

; CPU address $9e57
sound_35_part_06:
    .byte $31,$31,$41,$31,$31,$31,$41,$30,$00,$fe,$03
    .addr sound_35_part_06

sound_35_part_07:
    .byte $31,$31,$41,$31,$41,$41,$40,$40,$41,$fe,$ff
    .addr sound_35_part_01

lvl_5_pulse_volume_01:
    .byte $08,$07,$06,$05,$04,$03,$00,$00,$00,$00,$01,$ff

lvl_5_pulse_volume_02:
    .byte $06,$07,$06,$05,$04,$03,$ff

lvl_6_pulse_volume_03:
    .byte $05,$04,$03,$03,$03,$03,$00,$00,$00,$00,$01,$ff

lvl_6_pulse_volume_04:
    .byte $08,$07,$06,$05,$04,$03,$03,$00,$00,$00,$01,$ff

lvl_6_pulse_volume_05:
    .byte $06,$05,$04,$03,$02,$00,$00,$00,$00,$00,$01,$ff

; BGM 4 - level 6 energy zone (pulse 1 channel)
; CPU address $9ea8
sound_36:
    .byte $e8,$d6,$f9,$87,$00,$e3,$c8

; CPU address $9eaf
sound_36_part_00:
    .byte $d6,$f9,$87,$00,$e3,$70,$80,$a0,$d6,$37,$84,$05,$e2,$08,$00,$10
    .byte $30,$71,$56,$50,$30,$10,$31,$19,$31,$13,$e3,$a1,$73,$e2,$08,$00
    .byte $10,$30,$71,$56,$50,$30,$10,$31,$13,$d6,$38,$86,$04,$e2,$81,$73
    .byte $e2,$31,$13,$e3,$a1,$73

; CPU address $9ee5
sound_36_part_01:
    .byte $d6,$37,$21,$00,$e2,$01,$00,$d6,$b7,$21,$00,$e3,$32,$62,$02,$fe
    .byte $04
    .addr sound_36_part_01

; CPU address $9ef8
sound_36_part_02:
    .byte $d6,$37,$21,$00,$e3,$71,$70,$d6,$b7,$21,$00,$e3,$a2,$e2,$12,$e3
    .byte $72,$fe,$03
    .addr sound_36_part_02

sound_36_part_03:
    .byte $d6,$37,$21,$00,$e2,$71,$70,$d6,$f7,$21,$00,$e3,$a2,$e2,$80,$80
    .byte $80,$a0,$a0,$a0,$d6,$f4,$82,$00,$e0,$51,$00,$e1,$80,$e0,$00,$e1
    .byte $80,$50,$80,$50,$00,$50,$00,$e2,$80,$e1,$50,$00,$e2,$80,$e1,$00
    .byte $e2,$80,$50,$80,$50,$fe,$ff
    .addr sound_36_part_00

; BGM 4 - level 6 energy zone (pulse 2 channel)
; CPU address $9f46
sound_37:
    .byte $d6,$f9,$87,$04,$e2,$c8

; CPU address $9f4c
sound_37_part_00:
    .byte $d6,$f8,$85,$05,$e2,$00,$10,$30

; CPU address $9f54
sound_37_part_01:
    .byte $e2,$58,$50,$70,$80,$e1,$01,$e2,$a6,$a0,$80,$70,$81,$79,$81,$73
    .byte $31,$03,$fe,$02
    .addr sound_37_part_01

sound_37_part_02:
    .byte $d6,$f7,$21,$00

; CPU address $9f6e
sound_37_part_03:
    .byte $e2,$51,$50,$e3,$32,$62,$02,$fe,$04
    .addr sound_37_part_03

; CPU address $9f79
sound_37_part_04:
    .byte $e1,$01,$00,$e3,$a2,$e2,$12,$e3,$72,$fe,$03
    .addr sound_37_part_04

sound_37_part_05:
    .byte $e1,$01,$00,$e3,$a2,$e1,$10,$10,$10,$30,$30,$30,$d6,$f7,$83,$00
    .byte $e0,$50,$00,$e1,$80,$e0,$00,$e1,$80,$50,$80,$50,$00,$50,$00,$e2
    .byte $80,$e1,$50,$00,$e2,$80,$e1,$00,$e2,$80,$50,$80,$50,$00,$fe,$ff
    .addr sound_37_part_00

; BGM 4 - level 6 energy zone (triangle channel)
; CPU address $9fb8
sound_38:
    .byte $d6,$0e,$e2,$c8

; CPU address $9fbc
sound_38_part_00:
    .byte $d6,$0e,$e2,$00,$10,$30

; CPU address $9fc2
sound_38_part_01:
    .byte $50,$c0,$50,$fe,$0f
    .addr sound_38_part_01

sound_38_part_02:
    .byte $00,$10,$30

; CPU address $9fcc
sound_38_part_03:
    .byte $50,$c0,$50,$fe,$0f
    .addr sound_38_part_03

sound_38_part_04:
    .byte $00,$10,$30,$d6,$12

; CPU address $9fd8
sound_38_part_05:
    .byte $e2,$52,$32,$62,$02,$fe,$04
    .addr sound_38_part_05

; CPU address $9fe1
sound_38_part_06:
    .byte $e2,$02,$e3,$a2,$e2,$12,$e3,$72,$fe,$03
    .addr sound_38_part_06

sound_38_part_07:
    .byte $e2,$01,$00,$e3,$a2,$d6,$10,$e2,$10,$10,$10,$30,$30,$30,$d6,$90
    .byte $5b,$38,$fe,$ff
    .addr sound_38_part_00

; BGM 4 - level 6 energy zone (noise/dmc channel)
; CPU address $a003
sound_39:
    .byte $d6

; CPU address $a004
sound_39_part_00:
    .byte $20,$fe,$09
    .addr sound_39_part_00

; CPU address $a009
sound_39_part_01:
    .byte $d6,$40,$40,$40

; CPU address $a00d
sound_39_part_02:
    .byte $31,$30,$40,$00,$00,$31,$30,$40,$30,$30,$fe,$03
    .addr sound_39_part_02

sound_39_part_03:
    .byte $31,$30,$40,$00,$00,$31,$30,$40,$40,$40

; CPU address $a025
sound_39_part_04:
    .byte $31,$30,$40,$00,$00,$31,$30,$40,$30,$30,$fe,$03
    .addr sound_39_part_04

sound_39_part_05:
    .byte $31,$30,$40,$00,$00,$31,$30,$40,$40,$40

; CPU address $a03d
sound_39_part_06:
    .byte $31,$30,$40,$00,$00,$31,$00,$40,$00,$00,$fe,$07
   .addr sound_39_part_06

sound_39_part_07:
    .byte $31,$30,$40,$30,$30,$40,$40,$40,$40,$40,$40

; CPU address $a056
sound_39_part_08:
    .byte $30,$00,$00,$fe,$06
    .addr sound_39_part_08

sound_39_part_09:
    .byte $40,$40,$40,$fe,$ff
    .addr sound_39_part_01

lvl_5_pulse_volume_07:
    .byte $07,$06,$05,$04,$03,$03,$03,$03,$00,$00,$00,$00,$01,$ff

lvl_6_pulse_volume_00:
    .byte $05,$04,$03,$03,$03,$03,$03,$03,$00,$00,$00,$00,$01,$ff

lvl_6_pulse_volume_01:
    .byte $05,$06,$07,$06,$05,$04,$03,$ff

lvl_6_pulse_volume_02:
    .byte $0b,$0a,$09,$08,$07,$06,$05,$04,$03,$ff

; BGM 5 - level 8 alien's lair music (pulse 1 channel)
; CPU address $a092
sound_3a:
    .byte $dc,$f7,$29,$02,$e1,$1d,$7d,$3d,$9d

; CPU address $a09b
sound_3a_part_00:
    .byte $d7,$37,$28,$00,$e3,$a2,$e2,$32,$a1,$e1,$31,$e2,$01,$e1,$53,$e8
    .byte $d7,$b9,$87,$00,$e3,$00,$50,$50,$e2,$00,$e1,$00,$e2,$00,$e8,$fe
    .byte $02
    .addr sound_3a_part_00

sound_3a_part_01:
    .byte $e8,$d7,$34,$82,$00,$e2,$a1

; CPU address $a0c5
sound_3a_part_02:
    .byte $e2,$a0,$e1,$a0,$80,$60,$50,$30,$10,$00,$e2,$a0,$80,$fe,$02
    .addr sound_3a_part_02

sound_3a_part_03:
    .byte $e2,$a0,$e1,$a0,$80,$60,$50,$30,$10,$00,$e8,$e8,$d7,$fa,$88,$00

; CPU address $a0e6
sound_3a_part_04:
    .byte $e3,$00,$e2,$00,$fe,$03
    .addr sound_3a_part_04

sound_3a_part_05:
    .byte $d7,$f7,$85,$00,$e4,$a0,$e3,$a0,$e4,$a1,$a1,$d7,$fa,$88,$00

sound_3a_part_06:
    .byte $e3,$00,$e2,$00,$fe,$03
    .addr sound_3a_part_06
    .byte $d7,$f7,$85,$00,$e4,$90,$e3,$90,$e4,$91,$91,$d7,$fa,$88,$00

; CPU address $a114
sound_3a_part_08:
    .byte $e3,$00,$e2,$00,$fe,$03
    .addr sound_3a_part_08

sound_3a_part_09:
    .byte $d7,$f7,$85,$00,$e4,$80,$e3,$80,$e4,$81,$81,$d7,$37,$84,$00,$e2
    .byte $30,$e3,$a0,$70,$e2,$20,$e3,$90,$60,$e2,$10,$e3,$80,$60,$e2,$00
    .byte $e3,$60,$30,$d7,$fa,$88,$00

; CPU address $a143
sound_3a_part_0a:
    .byte $e3,$00,$e2,$00,$fe,$03
    .addr sound_3a_part_0a

; CPU address $a14b
sound_3a_part_0b:
    .byte $d7,$f7,$85,$00,$e4,$a0,$e3,$a0,$e4,$a1,$a1,$d7,$fa,$88,$00

; CPU address $a15a
sound_3a_part_0c:
    .byte $e3,$00,$e2,$00,$fe,$03
    .addr sound_3a_part_0c

sound_3a_part_0d:
    .byte $d7,$f7,$85,$00,$e4,$90,$e3,$90,$e4,$91,$91,$e8,$d7,$f6,$84,$02
    .byte $e3,$80,$80,$80,$80,$80,$80,$81,$80,$a2,$e2,$80,$80,$80,$80,$80
    .byte $80,$81,$a1,$e1,$30,$70,$60,$60,$60,$30,$30,$30,$60,$60,$20,$20
    .byte $50,$50,$10,$10,$60,$60,$60,$30,$30,$30,$80,$80,$50,$50,$a0,$e0
    .byte $12,$fe,$ff
    .addr sound_3a_part_00

; BGM 5 - level 8 alien's lair music (pulse 2 channel)
; CPU address $a1a7
sound_3b:
    .byte $dc,$f7,$29,$02,$e1,$6d,$e0,$0d,$e1,$8d,$e0,$2d

; CPU address $a1b3
sound_3b_part_00:
    .byte $d7,$f7,$27,$00,$e2,$32,$62,$e1,$31,$61,$e2,$51,$e1,$93,$d7,$3b
    .byte $89,$00,$e4,$00,$50,$50,$e3,$00,$e2,$00,$e3,$00,$fe,$02
    .addr sound_3b_part_00

; CPU address $a1d3
sound_3b_part_01:
    .byte $d7,$39,$86,$00,$e2,$a0,$e1,$a0,$80,$60,$50,$30,$10,$00,$e2,$a0
    .byte $80,$fe,$03
    .addr sound_3b_part_01

sound_3b_part_02:
    .byte $d7,$37,$2a,$04,$e1,$75,$d7,$fa,$87,$00,$e4,$a0,$e3,$a0,$e4,$a1
    .byte $a1,$d7,$37,$2a,$04,$e1,$65,$d7,$fa,$87,$00,$e4,$90,$e3,$90,$e4
    .byte $91,$91,$d7,$37,$2a,$04,$e1,$55,$d7,$fa,$87,$00,$e4,$80,$e3,$80
    .byte $e4,$81,$81,$d7,$fb,$8a,$00,$e1,$30,$e3,$a0,$70,$e2,$20,$e3,$90
    .byte $60,$e2,$10,$e3,$80,$60,$e2,$00,$e3,$60,$30,$d7,$37,$2a,$04,$e1
    .byte $75,$d7,$fa,$87,$00,$e4,$a0,$e3,$a0,$e4,$a1,$a1,$d7,$37,$2a,$04
    .byte $e1,$65,$d7,$fa,$87,$00,$e4,$90,$e3,$90,$e4,$91,$91,$d7,$f8,$86
    .byte $02,$e2,$10,$10,$10,$10,$10,$10,$11,$10,$32,$e1,$10,$10,$10,$10
    .byte $10,$10,$11,$31,$70,$a0,$e0,$30,$30,$30,$e1,$a0,$a0,$a0,$e0,$20
    .byte $20,$e1,$a0,$a0,$e0,$10,$10,$e1,$80,$80,$e0,$30,$30,$30,$e1,$a0
    .byte $a0,$a0,$e0,$50,$50,$00,$00,$60,$82,$fe,$ff
    .addr sound_3b_part_00

; BGM 5 - level 8 alien's lair music (triangle channel)
; CPU address $a295
sound_3c:
    .byte $d7,$12,$e2,$33,$43,$33,$43,$33,$43,$fe,$04
    .addr sound_3c

; CPU address $a2a2
sound_3c_part_00:
    .byte $d7,$0f,$e2,$00,$e1,$00,$fe,$16
    .addr sound_3c_part_00

sound_3c_part_01:
    .byte $d7,$20,$e1,$12,$02,$d7,$12,$e2,$a1,$81,$d7,$20,$a2,$82,$d7,$12
    .byte $61,$51,$d7,$20,$62,$52,$d7,$12,$31,$11

; CPU address $a2c6
sound_3c_part_02:
    .byte $d7,$0e,$e2,$00,$e1,$00,$e2,$00,$e1,$00,$e2,$00,$e1,$00,$d7,$90
    .byte $e1,$05,$fe,$03
    .addr sound_3c_part_02

sound_3c_part_03:
    .byte $d7,$17,$e1,$30,$e2,$a0,$70,$e1,$20,$e2,$90,$60,$e1,$10,$e2,$80
    .byte $60,$e1,$00,$e2,$60,$30

sound_3c_part_04:
    .byte $d7,$0e,$e2,$00,$e1,$00,$e2,$00,$e1,$00,$e2,$00,$e1,$00,$d7,$90
    .byte $e1,$05,$fe,$02
    .addr sound_3c_part_04
    .byte $d7,$0e

; CPU address $a30a
sound_3c_part_06:
    .byte $e2,$10,$e1,$10,$fe,$0c
    .addr sound_3c_part_06

sound_3c_part_07:
    .byte $d7,$2f,$e2,$32,$32,$21,$21,$d7,$10,$10,$10,$10,$10,$d7,$2f,$32
    .byte $32,$51,$51,$d7,$10,$60,$80,$80,$80,$fe,$ff
    .addr sound_3c_part_00

; BGM 5 - level 8 alien's lair music (noise/dmc channel)
; CPU address $a32f
sound_3d:
    .byte $d7

; CPU address $a330
sound_3d_part_00:
    .byte $33,$fe,$16

; CPU address $a333
sound_3d_part_01:
    .addr sound_3d_part_00

; CPU address $a335
sound_3d_part_02:
    .byte $40,$40,$40,$40,$40,$40,$40,$30

; CPU address $a33d
sound_3d_part_03:
    .byte $30,$30,$30,$30,$00,$00,$40,$00,$30,$00,$40,$00,$40,$00,$00,$00
    .byte $30,$30,$40,$40,$40,$40,$fe,$02
    .addr sound_3d_part_03

; CPU address $a357
sound_3d_part_04:
    .byte $30,$00,$00,$30,$00,$00,$40,$00,$30,$00,$fe,$02
    .addr sound_3d_part_04

sound_3d_part_05:
    .byte $30,$00,$00,$30,$00,$00,$40,$40,$40,$40

; CPU address $a36f
sound_3d_part_06:
    .byte $30,$30,$30,$30,$30,$30,$40,$40,$40,$30,$40,$30,$fe,$03
    .addr sound_3d_part_06

sound_3d_part_07:
    .byte $40,$40,$40,$40,$40,$40,$40,$40,$40,$40,$40,$40,$30,$30,$30,$30
    .byte $30,$30,$40,$40,$40,$30,$40,$30,$30,$30,$30,$30,$30,$30,$40,$40
    .byte $40,$40,$40,$40,$30,$30,$30,$40,$30,$30,$30,$00,$30,$40,$30,$30
    .byte $30,$30,$30,$40,$30,$30,$30,$00,$30,$40,$40,$40,$40,$30,$30,$40
    .byte $30,$30,$40,$30,$40,$30,$40,$40,$40,$40,$40,$30,$30,$40,$30,$30
    .byte $40,$30,$40,$30,$40,$40,$40,$30,$fe,$ff
    .addr sound_3d_part_03

lvl_2_pulse_volume_00:
    .byte $07,$07,$06,$05,$04,$03,$00,$00,$00,$01,$01,$01,$ff

lvl_2_pulse_volume_01:
    .byte $07,$06,$05,$04,$03,$ff

lvl_2_pulse_volume_02:
    .byte $03,$04,$05,$04,$03,$02,$ff

lvl_2_pulse_volume_03:
    .byte $06,$07,$06,$05,$04,$03,$00,$00,$00,$00,$01,$01,$ff

lvl_2_pulse_volume_04:
    .byte $07,$06,$05,$04,$03,$00,$00,$00,$00,$00,$01,$01,$ff

lvl_2_pulse_volume_05:
    .byte $05,$04,$03,$03,$03,$00,$00,$00,$00,$00,$01,$01,$ff

; CPU address $a41c
sound_3e_part_00:
    .byte $d6,$35,$08,$02,$e2,$41,$41,$d6,$35,$0a,$01,$71,$41,$b2,$92,$71
    .byte $fe,$03
    .addr sound_3e_part_00

sound_3e_part_01:
    .byte $d6,$35,$08,$02,$e2,$41,$41,$d6,$35,$0a,$01,$71,$41,$92,$b2,$e1
    .byte $01

; CPU address $a44a
sound_3e_part_02:
    .byte $d6,$f7,$08,$02,$e2,$51,$51,$d6,$35,$0a,$01,$91,$51,$e1,$02,$e2
    .byte $b2,$91,$fe,$03
    .addr sound_3e_part_02

sound_3e_part_03:
    .byte $d6,$f7,$08,$02,$51,$51,$d6,$35,$0a,$01,$91,$51,$b2,$e1,$02,$11
    .byte $ff

; 3D BGM - indoor/base level music (pulse 1 channel)
; CPU address $a468
sound_3e:
    .byte $ec,$01,$d6,$f7,$08,$02,$e2,$41,$41,$d6,$f5,$0a,$01,$71,$41,$b2
    .byte $92,$71,$fe,$03
    .addr sound_3e

sound_3e_part_04:
    .byte $d6,$f7,$08,$02,$e2,$41,$41,$d6,$f5,$0a,$01,$71,$41,$92,$b2,$e1
    .byte $01

; CPU address $a48f
sound_3e_part_05:
    .byte $d6,$f7,$08,$02,$e2,$51,$51,$d6,$f5,$0a,$01,$91,$51,$e1,$02,$e2
    .byte $b2,$91,$fe,$03
    .addr sound_3e_part_05

sound_3e_part_06:
    .byte $d6,$f7,$08,$02,$51,$51,$d6,$f5,$0a,$01,$91,$51,$b2,$e1,$02,$11

; CPU address $a4b5
sound_3e_part_07:
    .byte $d6,$37,$0b,$02,$e2,$00,$01,$e3,$b4,$d6,$f7,$0d,$03,$e2,$91,$91
    .byte $b3,$d6,$37,$0b,$02,$e3,$90,$91,$b4,$d6,$f7,$0d,$03,$e1,$01,$01
    .byte $23,$d6,$37,$0b,$02,$e2,$00,$01,$e3,$b4,$d6,$f7,$0d,$03,$e1,$41
    .byte $41,$53,$d6,$37,$0b,$02,$e3,$90,$91,$b4,$d6,$f7,$0d,$02,$e1,$90
    .byte $92,$90,$92,$fd
    .addr sound_3e_part_00

; CPU address $a4fb
sound_3e_part_08:
    .byte $d6,$35,$84,$08,$e3,$73,$43,$83,$43,$fe,$04
    .addr sound_3e_part_08

; CPU address $a508
sound_3e_part_09:
    .byte $71,$71,$41,$41,$81,$81,$41,$41,$fe,$04
    .addr sound_3e_part_09
    .byte $fd
    .addr sound_3e_part_00
    .byte $fe,$ff
    .addr sound_3e_part_07

; CPU address $a51b
sound_3e_part_0a:
    .byte $d6,$f7,$08,$02,$e2,$91,$91,$d6,$f7,$09,$01,$e1,$01,$e2,$91,$e1
    .byte $32,$22,$01,$fe,$03
    .addr sound_3e_part_0a

sound_3e_part_0b:
    .byte $d6,$f7,$08,$02,$e2,$91,$91,$d6,$f7,$09,$01,$e1,$01,$e2,$91,$e1
    .byte $22,$32,$41

; CPU address $a545
sound_3e_part_0c:
    .byte $d6,$f7,$08,$02,$e2,$b1,$b1,$d6,$f7,$09,$01,$e1,$21,$e2,$b1,$e1
    .byte $52,$42,$21,$fe,$03
    .addr sound_3e_part_0c

sound_3e_part_0d:
    .byte $d6,$f7,$08,$02,$e2,$b1,$b1,$d6,$f7,$09,$01,$e1,$21,$e2,$b1,$e1
    .byte $42,$52,$61,$ff

; 3D BGM - indoor/base level music (pulse 2 channel)
; CPU address $a570
sound_3f:
    .byte $ec,$01,$fd
    .addr sound_3e_part_0a

sound_3f_part_00:
    .byte $d6,$f7,$0b,$02,$e2,$50,$51,$44,$d6,$b7,$0c,$03,$e1,$21,$21,$43
    .byte $d6,$f7,$0b,$02,$e2,$20,$21,$44,$d6,$b7,$0c,$03,$e1,$51,$51,$73
    .byte $d6,$f7,$0b,$02,$e2,$50,$51,$44,$d6,$b7,$0c,$03,$e1,$91,$91,$b3
    .byte $d6,$f7,$0b,$02,$e2,$20,$21,$44,$d6,$b7,$0c,$03,$e0,$20,$22,$40
    .byte $42,$fd
    .addr sound_3e_part_0a

; CPU address $a5b9
sound_3f_part_01:
    .byte $d6,$38,$87,$08,$e2,$03,$e3,$93,$e2,$13,$e3,$93,$fe,$04
    .addr sound_3f_part_01

; CPU address $a5c9
sound_3f_part_02:
    .byte $e2,$01,$01,$e3,$91,$91,$e2,$11,$11,$e3,$91,$91,$fe,$04
    .addr sound_3f_part_02
    .byte $fe,$ff
    .addr sound_3f

; CPU address $a5dd
sound_3f_part_03:
    .byte $d6,$10,$e3

; CPU address $a5e0
sound_3f_part_04:
    .byte $91,$fe,$20
    .addr sound_3f_part_04

; CPU address $a5e5
sound_3f_part_05:
    .byte $b1,$fe,$20
    .addr sound_3f_part_05
    .byte $ff

; 3D BGM - indoor/base level music (triangle channel)
; CPU address $a5eb
sound_40:
    .byte $ec,$01,$d6,$10,$e2,$91,$91,$cb,$fe,$04
    .addr sound_40

; CPU address $a5f7
sound_40_part_00:
    .byte $e3,$b1,$fe,$20
    .addr sound_40_part_00

; CPU address $a5fd
sound_40_part_01:
    .byte $d6,$10,$e2,$50,$50,$c0,$d6,$7f,$44,$d6,$10,$21,$21,$43,$20,$20
    .byte $c0,$d6,$7f,$44,$d6,$10,$51,$51,$73,$50,$50,$c0,$d6,$7f,$44,$d6
    .byte $10,$91,$91,$b3,$20,$20,$c0,$d6,$7f,$44,$d6,$10,$20,$22,$40,$42
    .byte $fd
    .addr sound_3f_part_03

; CPU address $a630
sound_40_part_02:
    .byte $d6,$15,$e2,$03,$93,$13,$93,$fe,$04
    .addr sound_40_part_02

; CPU address $a63b
sound_40_part_03:
    .byte $01,$01,$91,$91,$11,$11,$91,$91,$fe,$04
    .addr sound_40_part_03
    .byte $fd
    .addr sound_3f_part_03
    .byte $fe,$ff
    .addr sound_40_part_01

; CPU address $a64e
sound_40_part_04:
    .byte $31,$01,$41,$01,$31,$31,$41,$01,$fe,$03
    .addr sound_40_part_04

sound_40_part_05:
    .byte $31,$01,$41,$01,$31,$31,$41,$40,$40

; CPU address $a663
sound_40_part_06:
    .byte $31,$01,$41,$01,$31,$31,$41,$01,$fe,$03
    .addr sound_40_part_06

sound_40_part_07:
    .byte $31,$01,$41,$01,$40,$40,$41,$41,$40,$40,$ff

; 3D BGM - indoor/base level music (noise/dmc channel)
; CPU address $a67a
sound_41:
    .byte $d6,$31,$31,$03,$03,$03,$fe,$03
    .addr sound_41

sound_41_part_00:
    .byte $31,$31,$33,$33,$40,$40,$41

; CPU address $a68b
sound_41_part_01:
    .byte $31,$01,$41,$01,$31,$31,$41,$01,$fe,$03
    .addr sound_41_part_01

sound_41_part_02:
    .byte $31,$01,$41,$01,$31,$31,$41,$40,$40

; CPU address $a6a0
sound_41_part_03:
    .byte $40,$40,$30,$40,$00,$00,$31,$31,$31,$41,$00,$00,$fe,$03
    .addr sound_41_part_03

sound_41_part_04:
    .byte $40,$40,$30,$40,$00,$00,$31,$40,$40,$00,$00,$40,$40,$00,$00,$fd
    .addr sound_40_part_04

sound_41_part_05:
    .byte $31,$31,$41,$01,$31,$31,$41,$01,$31,$01,$41,$01,$31,$31,$41,$01
    .byte $31,$31,$41,$01,$31,$31,$41,$01,$31,$01,$41,$01,$31,$31,$40,$40
    .byte $40,$40

; CPU address $a6e4
sound_41_part_06:
    .byte $31,$31,$41,$31,$fe,$03
    .addr sound_41_part_06

; CPU address $a6ec
sound_41_part_07:
    .byte $31,$31,$41,$41

; CPU address $a6f0
sound_41_part_08:
    .byte $31,$31,$41,$31,$fe,$03
    .addr sound_41_part_08

sound_41_part_09:
    .byte $40,$40,$41,$40,$40,$40,$40,$fd
    .addr sound_40_part_04
    .byte $fe,$ff
    .addr sound_41_part_03

lvl_2_pulse_volume_06:
    .byte $05,$06,$05,$04,$03,$02,$00,$00,$00,$00,$00,$01,$ff

lvl_6_pulse_volume_06:
    .byte $0c,$0b,$0a,$09,$08,$07,$06,$ff

lvl_6_pulse_volume_07:
    .byte $08,$07,$06,$05,$04,$03,$03,$00,$00,$00,$00,$01,$ff

lvl_7_pulse_volume_00:
    .byte $0a,$09,$08,$07,$06,$05,$04,$00,$00,$00,$00,$01,$ff

; CPU address $a735
sound_43_part_00:
    .byte $e4,$60,$80,$60,$90,$60,$80,$60,$80,$60,$b0,$60,$80,$fe,$02
    .addr sound_43_part_00

; CPU address $a746
sound_43_part_01:
    .byte $e4,$80,$90,$80,$b0,$80,$90,$80,$90,$80,$e3,$10,$e4,$80,$90,$fe
    .byte $02
    .addr sound_43_part_01

; CPU address $a759
sound_43_part_02:
    .byte $e4,$90,$b0,$90,$e3,$10,$e4,$90,$b0,$90,$b0,$90,$e3,$10,$e4,$90
    .byte $b0,$fe,$02
    .addr sound_43_part_02

sound_43_part_03:
    .byte $e4,$b0,$e3,$10,$e4,$b0,$e3,$20,$e4,$b0,$e3,$10,$e4,$b0,$e3,$10
    .byte $e4,$b0,$e3,$20,$e4,$b0,$e3,$10,$10,$20,$10,$40,$10,$20,$10,$40
    .byte $10,$50,$10,$80,$ff

; BOSS - indoor/base boss screen music (pulse 1 channel)
; CPU address $a793
sound_42:
    .byte $d7,$36,$0e,$00,$e2,$60,$61,$60,$90,$80,$63,$40,$50,$e2,$60,$e3
    .byte $61,$60,$e2,$90,$80,$91,$81,$41,$80,$81,$80,$b0,$90,$83,$60,$70
    .byte $e2,$80,$e3,$81,$80,$e2,$b0,$90,$b1,$91,$81,$90,$91,$90,$e1,$10
    .byte $e2,$b0,$93,$e2,$70,$80,$90,$e3,$91,$90,$e1,$10,$e2,$b0,$e1,$11
    .byte $e2,$b1,$91,$b0,$b1,$b0,$e1,$20,$10,$e2,$b3,$e2,$b0,$e1,$00,$10
    .byte $e2,$11,$10,$e1,$40,$50,$11,$51,$81,$fe,$02
    .addr sound_42

sound_42_part_00:
    .byte $e8,$d7,$38,$2f,$00,$e2,$20,$21,$e3,$b0,$b1,$d7,$38,$87,$00,$e2
    .byte $20,$20,$20,$20,$20,$20,$20,$20,$20,$20,$20,$10,$20,$20,$20,$20
    .byte $20,$20,$d7,$38,$2f,$00,$e2,$20,$21,$80,$81,$e1,$10,$10,$10,$10
    .byte $10,$10,$10,$10,$10,$10,$10,$e2,$b0,$e1,$10,$10,$10,$10,$10,$10
    .byte $e2,$60,$61,$40,$41,$d7,$38,$87,$00,$e2,$20,$20,$20,$20,$20,$20
    .byte $20,$20,$20,$20,$20,$10,$20,$20,$20,$20,$20,$20,$d7,$36,$2f,$00
    .byte $e2,$20,$21,$80,$81,$e1,$10,$10,$10,$10,$10,$10,$10,$10,$10,$10
    .byte $10,$10,$40,$40,$40,$40,$40,$40,$d7,$f6,$2f,$00,$e8,$e1,$60,$60
    .byte $60,$60,$61,$c5,$fe,$ff
    .addr sound_42

; BOSS - indoor/base boss screen music (pulse 2 channel)
; CPU address $a878
sound_43:
    .byte $d7,$f8,$2e,$00,$fd
    .addr sound_43_part_00
    .byte $fd
    .addr sound_43_part_00

sound_43_part_04:
    .byte $d7,$f8,$30,$00,$e2,$60,$61,$40,$41,$d7,$f8,$87,$00,$e1,$60,$60
    .byte $60,$60,$60,$60,$80,$80,$80,$80,$80,$80,$90,$90,$90,$90,$90,$90
    .byte $b0,$b0,$b0,$b0,$b0,$b0,$60,$60,$60,$60,$60,$60,$80,$80,$80,$80
    .byte $80,$80,$90,$90,$90,$90,$90,$90,$e0,$10,$10,$10,$10,$10,$10,$e1
    .byte $60,$60,$60,$60,$60,$60,$80,$80,$80,$80,$80,$80,$90,$90,$90,$90
    .byte $90,$90,$b0,$b0,$b0,$b0,$b0,$b0,$60,$60,$60,$60,$60,$60,$80,$80
    .byte $80,$80,$80,$80,$90,$90,$90,$90,$90,$90,$e0,$10,$10,$10,$10,$d7
    .byte $f8,$30,$00,$11,$c5,$fe,$ff
    .addr sound_43

; BOSS - indoor/base boss screen music (triangle channel)
; CPU address $a8fb
sound_44:
    .byte $d7,$12,$e2,$60,$60,$c0,$60,$90,$80,$d7,$7f,$63,$d7,$10,$40,$50
    .byte $e2,$60,$d7,$12,$e3,$61,$60,$e2,$90,$80,$d1,$2f,$e2,$80,$dd,$28
    .byte $90,$d7,$28,$81,$41,$d7,$12,$80,$80,$c0,$80,$b0,$90,$d7,$7f,$83
    .byte $d7,$10,$60,$70,$e2,$80,$d7,$12,$e3,$81,$80,$e2,$b0,$90,$d7,$2f
    .byte $b1,$91,$81,$d7,$12,$90,$90,$c0,$90,$e1,$10,$e2,$b0,$d7,$7f,$93
    .byte $d7,$10,$e2,$70,$80,$90,$e3,$91,$90,$e1,$10,$e2,$b0,$d7,$2f,$e1
    .byte $11,$e2,$b1,$91,$d7,$12,$b0,$b0,$c0,$b0,$e1,$20,$10,$d7,$7f,$e2
    .byte $b3,$d7,$10,$e2,$b0,$e1,$00,$10,$d7,$12,$e2,$11,$10,$e1,$40,$50
    .byte $d7,$2f,$11,$51,$81,$fe,$02
    .addr sound_44

sound_44_part_00:
    .byte $d7,$12,$e2,$60,$61,$40,$41,$d7,$10,$e2,$20,$20,$20,$20,$20,$20
    .byte $20,$20,$20,$20,$20,$10,$20,$20,$20,$20,$20,$20,$d7,$12,$e2,$20
    .byte $21,$80,$81,$d7,$10,$60,$60,$60,$60,$60,$60,$60,$60,$60,$60,$60
    .byte $40,$60,$60,$60,$60,$60,$60,$d7,$12,$e2,$60,$61,$40,$41,$d7,$10
    .byte $20,$20,$20,$20,$20,$20,$20,$20,$20,$20,$20,$10,$20,$20,$20,$20
    .byte $20,$20,$d7,$12,$20,$21,$80,$81,$d7,$0f,$60,$60,$60,$60,$60,$60
    .byte $80,$80,$80,$80,$80,$80,$90,$90,$90,$90,$90,$90,$d7,$0f,$60,$60
    .byte $60,$60,$60,$c0,$c5,$fe,$ff
    .addr sound_44

; CPU address $a9fd
sound_45_part_00:
    .byte $40,$40,$00,$40,$40,$00

; CPU address $aa03
sound_45_part_01:
    .byte $40,$40,$40,$40,$40,$30,$fe,$03
    .addr sound_45_part_01
    .byte $ff

; BOSS - indoor/base boss screen music (noise/dmc channel)
; CPU address $aa0e
sound_45:
    .byte $d7,$30,$40,$10,$30,$40,$30,$30,$10,$00,$10,$40,$40,$30,$40,$10
    .byte $30,$40,$30,$40,$30,$40,$30,$40,$40,$fe,$07
    .addr sound_45

sound_45_part_02:
    .byte $30,$40,$10,$30,$40,$30,$30,$10,$00,$10,$40,$40,$30,$40,$10,$30
    .byte $40,$30,$40,$40,$40,$40,$40,$40,$fd
    .addr sound_45_part_00
    .byte $fd
    .addr sound_45_part_00
    .byte $fd
    .addr sound_45_part_00
    .byte $fd
    .addr sound_45_part_00

sound_45_part_03:
    .byte $40,$40,$40,$40,$40,$00,$40,$30,$40,$30,$40,$40,$fe,$ff
    .addr sound_45

lvl_2_pulse_volume_07:
    .byte $08,$07,$06,$05,$04,$03,$03,$00,$00,$00,$00,$01,$ff

lvl_3_pulse_volume_00:
    .byte $06,$07,$06,$05,$04,$03,$ff

lvl_3_pulse_volume_01:
    .byte $04,$05,$04,$03,$ff

lvl_3_pulse_volume_06:
    .byte $09,$08,$07,$06,$05,$04,$03,$00,$00,$00,$00,$01,$ff

lvl_7_pulse_volume_05:
    .byte $08,$07,$06,$05,$04,$03,$03,$00,$00,$00,$00,$01,$ff

; PCLR - end of level tune (pulse 1 channel)
; CPU address $aa92 - end of level tune
sound_46:
    .byte $d7,$f7,$35,$00,$e1,$c0,$10,$10,$10,$12,$30,$30,$30,$30,$e2,$b0
    .byte $b0,$b0,$b1,$d7,$f7,$0f,$00,$e2,$40,$50,$90,$d7,$f7,$11,$02,$bd
    .byte $ff

; PCLR - end of level tune (pulse 2 channel)
; CPU address $aab3
sound_47:
    .byte $d7,$f7,$16,$00,$e1,$c0,$40,$40,$40,$42,$60,$60,$60,$60,$20,$20
    .byte $20,$21,$d7,$f7,$0f,$00,$e2,$90,$b0,$e1,$20,$d7,$f7,$10,$02,$4d
    .byte $ff

; PCLR - end of level tune (triangle channel)
; CPU address $aad4
sound_48:
    .byte $d7,$10,$e2,$c0,$90,$90,$90,$90,$c1,$b0,$b0,$b0,$b0,$70,$70,$70
    .byte $70,$c0,$e3,$70,$90,$e2,$00,$d7,$90,$4d,$ff

; PCLR - end of level tune (noise/dmc channel)
; CPU address $aaef
sound_49:
    .byte $d7,$c0,$40,$40,$40,$40,$11,$40,$40,$40,$40,$40,$40,$40,$40,$c0
    .byte $30,$40,$40,$40,$ff

lvl_3_pulse_volume_02:
    .byte $08,$07,$06,$05,$04,$03,$03,$00,$00,$00,$00,$01,$ff

lvl_3_pulse_volume_03:
    .byte $06,$05,$04,$03,$03,$03,$03,$00,$00,$00,$00,$01,$ff

lvl_3_pulse_volume_04:
    .byte $05,$04,$03,$02,$02,$02,$00,$00,$00,$01,$ff

lvl_3_pulse_volume_05:
    .byte $08,$07,$06,$05,$04,$03,$00,$00,$00,$01,$ff

; OVER - game over/after end credits, presented by konami (pulse 1 channel)
; CPU address $ab34
sound_4e:
    .byte $e8,$d7,$b7,$12,$02,$e2,$c0,$41,$42,$d7,$f7,$13,$02,$70,$90,$b0
    .byte $40,$41,$22,$03,$e1,$00,$20,$45,$e2,$22,$32,$41,$e8,$d7,$f3,$14
    .byte $00,$e1,$41,$11,$e2,$a1,$97,$ff

; OVER - game over/after end credits, presented by konami (pulse 2 channel)
; CPU address $ab5c
sound_4f:
    .byte $d7,$f8,$12,$02,$e2,$c0,$91,$92,$70,$90,$b0,$90,$91,$72,$53,$d7
    .byte $38,$12,$02,$e1,$00,$20,$45,$d7,$f8,$12,$02,$e2,$72,$82,$91,$d7
    .byte $37,$15,$00,$e0,$41,$11,$e1,$a1,$97,$ff

; OVER - game over/after end credits, presented by konami (triangle channel)
; CPU address $ab86
sound_50:
    .byte $d7,$10,$e2,$c0,$90,$c0,$90,$c0,$c0,$e3,$70,$90,$b0,$90,$91,$72
    .byte $d7,$7f,$53,$d7,$2f,$e2,$00,$20,$d7,$7f,$45,$d7,$10,$e3,$72,$82
    .byte $91,$d7,$0f,$e2,$41,$11,$e3,$a1,$d7,$90,$97,$ff

; OVER - game over/after end credits, presented by konami (noise/dmc channel)
; CPU address $abb2
sound_51:
    .byte $d7,$c0,$30,$00,$31,$c0,$00,$00,$00,$40,$40,$30,$40,$40,$30,$43
    .byte $00,$00,$05,$30,$00,$00,$30,$00,$00,$31,$d7,$01,$01,$01,$01,$ff

lvl_7_pulse_volume_01:
    .byte $07,$08,$07,$06,$05,$04,$03,$ff

lvl_7_pulse_volume_02:
    .byte $07,$06,$05,$04,$03,$03,$03,$03,$03,$03,$00,$00,$00,$00,$01,$ff

lvl_7_pulse_volume_03:
    .byte $ff

lvl_7_pulse_volume_04:
    .byte $ff

; CPU address $abec
sound_4a_part_00:
    .byte $d6,$37,$85,$03,$e2,$75,$e4,$00,$00,$01,$01,$c1,$e2,$77,$e4,$00
    .byte $00,$01,$01,$c1,$e2,$b7,$e4,$00,$00,$e2,$52,$72,$91,$47,$07,$e2
    .byte $57,$52,$42,$21,$07,$e3,$42,$52,$71,$e2,$25,$70,$90,$77,$e3,$b7
    .byte $b2,$e2,$02,$21,$e2,$75,$e4,$00,$00,$01,$01,$c1,$e2,$77,$e4,$00
    .byte $00,$01,$01,$c1,$e2,$b7,$e4,$00,$00,$e2,$52,$72,$91,$47,$07,$27
    .byte $22,$02,$e3,$b1,$e2,$07,$42,$52,$71,$e2,$25,$20,$40,$27,$70,$90
    .byte $b1,$90,$b0,$e1,$01,$e2,$57,$d6,$37,$32,$00,$e1,$01,$01,$e2,$b1
    .byte $e1,$03,$01,$e2,$b1,$e1,$01,$e2,$b1,$b1,$91,$b3,$b1,$91,$b1,$91
    .byte $91,$71,$91,$d6,$37,$85,$03,$92,$b2,$e1,$01,$d6,$37,$84,$08,$43
    .byte $23,$03,$e2,$b3,$d6,$37,$32,$00,$e1,$21,$21,$01,$23,$21,$01,$21
    .byte $21,$21,$11,$23,$21,$11,$21,$21,$21,$01,$21,$d6,$37,$85,$03,$22
    .byte $42,$51,$ff

; ENDING - end credits (pulse 1 channel)
; CPU address $ac9f
sound_4a:
    .byte $e8,$fd
    .addr sound_4a_part_00

sound_4a_part_01:
    .byte $e1,$47,$57,$fd
    .addr sound_4a_part_00

sound_4a_part_02:
    .byte $e1,$47,$5f,$ff

; CPU address $acad
sound_4a_part_03:
    .byte $d6,$f8,$31,$03,$e2,$77,$72,$e1,$22,$09,$02,$52,$49,$92,$b2,$e0
    .byte $01,$e1,$77,$47,$97,$92,$72,$51,$47,$42,$22,$01,$e2,$7f,$27,$42
    .byte $52,$71,$e2,$77,$72,$e1,$22,$09,$02,$52,$49,$92,$b2,$e0,$01,$e1
    .byte $77,$47,$57,$52,$42,$21,$47,$42,$22,$01,$e2,$75,$70,$90,$77,$b0
    .byte $e1,$00,$21,$00,$20,$41,$d6,$f8,$31,$03,$e1,$97,$79,$53,$41,$59
    .byte $43,$21,$07,$02,$22,$41,$d6,$f9,$85,$08,$e1,$93,$73,$53,$43,$d6
    .byte $f8,$31,$03,$9f,$77,$72,$52,$41,$57,$52,$72,$91,$ff

; ENDING - end credits (pulse 2 channel)
; CPU address $ad1a
sound_4b:
    .byte $fd
    .addr sound_4a_part_03

sound_4b_part_00:
    .byte $77,$b7,$fd
    .addr sound_4a_part_03

; CPU address $ad22
sound_4b_part_01:
    .byte $77,$bf,$ff

; CPU address $ad25
sound_4b_part_02:
    .byte $d6,$7f,$e2,$05,$d6,$0e,$00,$00,$01,$01,$c1,$00,$00,$fe,$03
    .addr sound_4b_part_02

; CPU address $ad36
sound_4b_part_03:
    .byte $d6,$7f,$05,$d6,$0e,$00,$00,$41,$41,$c1,$41,$d6,$7f,$55,$d6,$0e
    .byte $50,$50,$51,$51,$c1,$50,$50,$d6,$7f,$45,$d6,$0e,$40,$40,$41,$41
    .byte $c1,$40,$40

; CPU address $ad59
sound_4b_part_04:
    .byte $d6,$7f,$75,$d6,$0e,$70,$70,$71,$71,$c1,$70,$70,$fe,$02
    .addr sound_4b_part_04

; CPU address $ad69
sound_4b_part_05:
    .byte $d6,$7f,$e2,$05,$d6,$0e,$00,$00,$01,$01,$c1,$00,$00,$fe,$03
    .addr sound_4b_part_05

; CPU address $ad7a
sound_4b_part_06:
    .byte $d6,$7f,$05,$d6,$0e,$00,$00,$41,$41,$c1,$41,$d6,$7f,$55,$d6,$0e
    .byte $50,$50,$51,$51,$c1,$50,$50,$d6,$7f,$45,$d6,$0e,$40,$40,$41,$41
    .byte $c1,$40,$40

; CPU address $ad9d
sound_4b_part_07:
    .byte $d6,$7f,$75,$d6,$0e,$70,$70,$71,$71,$c1,$70,$70,$fe,$02
    .addr sound_4b_part_07

sound_4b_part_08:
    .byte $d6,$7f,$e2,$05,$d6,$0e,$00,$00,$01,$01,$c1,$00,$00,$d6,$7f,$e3
    .byte $b5,$d6,$0e,$b0,$b0,$b1,$b1,$c1,$b0,$b0,$d6,$7f,$a5,$d6,$0e,$a0
    .byte $a0,$a1,$a1,$c1,$a0,$a0,$d6,$7f,$95,$d6,$0e,$90,$90,$91,$91,$c1
    .byte $90,$90,$d6,$7f,$e2,$25,$d6,$0e,$20,$20,$21,$21,$c1,$20,$20,$d6
    .byte $7f,$15,$d6,$0e,$10,$10,$11,$11,$c1,$10,$10,$d6,$7f,$25,$d6,$0e
    .byte $20,$20,$21,$21,$c1,$20,$20,$ff

; ENDING - end credits (triangle channel)
; CPU address $ae05
sound_4c:
    .byte $fd
    .addr sound_4b_part_02

sound_4c_part_00:
    .byte $d6,$7f,$e3,$b5,$d6,$0e,$b0,$b0,$e2,$71,$71,$c1,$71,$fd
    .addr sound_4b_part_02

sound_4c_part_01:
    .byte $d6,$90,$e3,$bf,$b7,$ff

; CPU address $ae1e
sound_4c_part_02:
    .byte $d6,$31,$01,$41,$00,$00,$31,$31,$41,$01,$fe,$03
    .addr sound_4c_part_02

sound_4c_part_03:
    .byte $31,$01,$41,$00,$00,$31,$41,$01,$40,$40

; CPU address $ae36
sound_4c_part_04:
    .byte $31,$01,$41,$00,$00,$31,$31,$41,$01,$fe,$03
    .addr sound_4c_part_04

; CPU address $ae43
sound_4c_part_05:
    .byte $31,$01,$41,$00,$00,$31,$31,$41,$41

; CPU address $ae4c
sound_4c_part_06:
    .byte $31,$01,$41,$00,$00,$31,$31,$41,$01,$fe,$03
    .addr sound_4c_part_06

sound_4c_part_07:
    .byte $31,$01,$41,$00,$00,$31,$31,$41,$40,$40

; CPU address $ae63
sound_4c_part_08:
    .byte $31,$01,$41,$00,$00,$31,$31,$41,$01,$fe,$03
    .addr sound_4c_part_08

; CPU address $ae70
sound_4c_part_09:
    .byte $31,$01,$41,$00,$00,$31,$31,$41,$41

; CPU address $ae79
sound_4c_part_0a:
    .byte $31,$01,$01,$30,$30,$31,$31,$41,$01,$fe,$07
    .addr sound_4c_part_0a
    .byte $ff

; ENDING - end credits (noise/dmc channel)
; CPU address $ae87
sound_4d:
    .byte $fd
    .addr sound_4c_part_02

sound_4d_part_00:
    .byte $31,$01,$01,$30,$30,$41,$41,$31,$40,$40,$fd
    .addr sound_4c_part_02

sound_4d_part_01:
    .byte $33,$03,$33,$03,$c7,$ff

play_sound:
  jmp init_sound_code_vars
.endscope
