; PRIVATE consumer-only adapter; no resident/common hook in this component.
; Common caller must retire the previous audio owner, initialize shared images
; without an invented DAC write, call Acquire, then commit GuestAudioCharacter25.
; Tick is exactly once per REAL outer NMI, including lag/pause, never Main.
S2HostWorld=RgAudioRam+69
S2HostScene=RgAudioRam+70
S2HostLives=RgAudioRam+71
S2HostTheme=RgAudioRam+72
S2HostTask=RgAudioRam+73
S2HostEngine=RgAudioRam+74
S2HostStar=RgAudioRam+75
S2HostValid=RgAudioRam+76
S2HostContextBusy=$5fb6      ; common protocol bit0 ONLY; no new meaning/write.
.pushseg
.segment "KIRBY_ABILITIES"
S2HostAudioBegin:
.assert S2HostAudioBegin=$bcb7,lderror,"owned A74 tail preimage moved"

.proc S2HostAcquireNmi
 S2ASave
 lda CrossoverMenuState
 cmp #8
 beq Done
 lda OperMode
 beq Done
 lda RgAudioCharacter
 cmp #25
 beq Initialize
 lda $4015                  ; never clear a foreign owner's active DMC.
 and #$10
 bne Done
Initialize:
 jsr S2AudioInitialize
 lda #0
 ldx #7
Clear:sta S2HostWorld,x
 dex
 bpl Clear
Done:jmp S2AudioReturn
.endproc

.proc S2HostNmiTick
 S2ASave
 lda CrossoverMenuState
 cmp #8                     ; SoundTest's recursive call is NOT another NMI.
 beq Done
 lda OperMode
 beq Done
 lda GuestAudioCharacter
 cmp #25                    ; external owner is initialized/committed last.
 bne Done
 lda RgAudioCharacter
 cmp #25
 bne Done
 ; The genuine clock farcall changes these five operands. Preserve their
 ; interrupted values, not a fabricated all-zero/constant SMC image.
 lda SafecallA_SMC+1
 pha
 lda FarcallJmpTarget_SMC+1
 pha
 lda FarcallJmpTarget_SMC+2
 pha
 lda NextBank_SMC+1
 pha
 lda SafereturnA_SMC+1
 pha
 farcall S2NmiClock
 jsr S2AudioPollDmc
 lda GamePauseStatus
 and #1
 beq :+
 lda #$41                   ; original Stack100 pause discriminator.
:sta S2AudioPause
 jsr S2HostContext
 jsr S2HostCues
 jsr S2AudioEffectTick       ; one literal source callback, even context-busy.
 lda S2AudioEnable
 sta GuestNativeEnable      ; final mixer/status route remains common-owned.
 pla
 sta SafereturnA_SMC+1
 pla
 sta NextBank_SMC+1
 pla
 sta FarcallJmpTarget_SMC+2
 pla
 sta FarcallJmpTarget_SMC+1
 pla
 sta SafecallA_SMC+1
Done:jmp S2AudioReturn
.endproc

.proc S2HostContext
 lda S2HostContextBusy
 and #1
 bne Done                   ; effects/clock are NOT deferred by this barrier.
 lda S2HostValid
 beq Scene
 lda S2World
 cmp S2HostWorld
 bne Scene
 lda S2Area
 cmp S2HostScene
 beq Stable
Scene:
 lda AreaType
 and #3
 tax
 lda Theme,x
 sta S2HostTheme
 ldx StarInvincibleTimer
 beq :+
 lda #$10                   ; a new scene must not replace active Star music.
: 
 sta S2AudioState+20         ; authored SMB scene -> authentic source song.
Stable:
 lda S2World
 sta S2HostWorld
 lda S2Area
 sta S2HostScene
 lda S2Life
 sta S2HostLives             ; a life gain is not a source driver reset.
 lda OperMode_Task
 sta S2HostTask
 lda GameEngineSubroutine
 sta S2HostEngine
 lda StarInvincibleTimer
 beq NoStar
 lda #1
 ldx S2HostStar
 bne StarStore
 ldx #$10
 stx S2AudioState+20
 bne StarStore
NoStar:
 ldx S2HostStar
 beq StarStore
 ldx S2HostTheme
 stx S2AudioState+20
StarStore:
 sta S2HostStar
 lda #1
 sta S2HostValid
Done:rts
Theme:.byte 4,1,4,8          ; water/ground/cave/castle; explicit adaptation.
.endproc

.proc S2HostCues
 lda EventMusicQueue
 beq Area
 lda #0
 sta AreaMusicQueue          ; native MusicHandler gives pending event priority.
 jmp Event
Area:
 lda AreaMusicQueue
 beq Event
 ldy #0
 sta S2AudioState+20         ; temporary input, replaced before driver runs.
 lda #0
 sta AreaMusicQueue
 lda S2AudioState+20
AreaBit:
 lsr
 bcs AreaFound
 iny
 bne AreaBit
AreaFound:
 lda AreaMap,y
 cpy #7
 bne Song
 sta S2AudioState+23         ; silence is the authentic source Stop event.
 lda #0
Song:
 sta S2AudioState+20
 cpy #6
 bcs Event
 sta S2HostTheme
Event:
 lda EventMusicQueue
 beq Done
 ldy #0
 pha
 lda #0
 sta EventMusicQueue
 pla
EventBit:
 lsr
 bcs EventFound
 iny
 bne EventBit
EventFound:
 lda EventMap,y
 beq Done                   ; hurry keeps theme; shared warning stays intact.
 sta S2AudioState+23
Done:rts
AreaMap:.byte 1,4,4,8,$20,4,$10,$80
EventMap:.byte 8,$10,4,2,$10,$20,0,$80
.endproc

.proc S2HostRetireNmi
 php
 pha
 txa
 pha
 tya
 pha
 lda RgAudioCharacter        ; OLD owner, valid after SelectedCharacter changes.
 cmp #25
 bne Done
 jsr S2AudioCancelInner      ; stop -> E127 -> release, never4011.
 lda #0
 sta S2HostValid
 lda #$ff
 sta RgAudioCharacter
Done:jmp S2AudioReturn
.endproc

; Input/output A is a status image. X/Y/P/SP and A/C/SMC are preserved.
; Common GuestDmcStatus must route here ONLY for the actual old SMB2 owner.
; A foreign owner returns input A unchanged without private-state reads.
.proc S2HostDmcStatus
 php
 pha
 lda RgAudioCharacter
 cmp #25
 bne Foreign
 lda S2AudioActiveBank
 beq Off
 lda $4015
 and #$10
 bne Busy
 lda #$ff
 sta $5117                  ; real hardware completion, no sample restart.
 lda #0
 sta S2AudioActiveBank
Off:
 pla
 and #15
 plp
 rts
Busy:
 pla
 ora #$10
 plp
 rts
Foreign:
 pla
 plp
 rts
.endproc
S2HostAudioEnd:
.assert S2HostAudioEnd<=$c000,lderror,"owned A74 adapter exceeds841B"
.export S2HostAcquireNmi,S2HostNmiTick,S2HostRetireNmi,S2HostDmcStatus
.export S2HostAudioBegin,S2HostAudioEnd
.export S2HostWorld,S2HostScene,S2HostLives,S2HostTheme,S2HostTask,S2HostEngine,S2HostStar,S2HostValid
.popseg
