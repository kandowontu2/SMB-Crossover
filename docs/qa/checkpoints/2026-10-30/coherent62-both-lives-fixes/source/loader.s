.import FwPaletteMapC
.import BackgroundColorCtrl
.import FwForceColors,VRAM_Buffer1_Offset
.include "inc/charmap.inc"
.import FmQueueName,FfVariant,VRAM_Buffer1
; Private selected-raw22 FF loader/router. Real source-linked imports only.
.macpack longbranch
.import SelectedCharacter,OperMode,DisableScreenFlag,NmiDisable
.import Mirror_PPUMASK,Mirror_PPUCTRL,HorizontalScroll,VerticalScroll
.import CurrentBank,CurrentBankC,ReloadCHRBank,X5PublishChr
.import FarCallCommon,FarcallJmpTarget_SMC,SafecallA_SMC
.import MoveAllSpritesOffscreen,FwPreviewPortrait,SpecialRosterClear
.importzp R0,R1
.export FwLoad,FwCheck,FwSceneInit,FwRetire,FwInvalidate,FwSelectedReset
.export FwMapPage,FwCopy256,FwVerify256,FwPublishCookie,FwRestorePPU
.export FwRestoreContext,FwRestoreC,FwCookie,FwCallEnter
.segment "FF_ROM_HOST"

; Stand-in for exactly the existing native InitScreen farcall. The original
; MoveAllSpritesOffscreen remains first; its AXYP/stack/scratch result survives.
FwSceneInit:
 sta SafecallA_SMC+1
 lda #<MoveAllSpritesOffscreen
 sta FarcallJmpTarget_SMC+1
 lda #>MoveAllSpritesOffscreen
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(MoveAllSpritesOffscreen)|$80)
 jsr FarCallCommon
 php
 pha
 txa
 pha
 tya
 pha
 jsr FwMuxScene
 jsr FwLoad
 bcc FwSceneInitRestore
 ; Scene/life constructor follows verified load, before native lives display.
 ; Ensure detects actual life loss; unconditional AreaReset clears same-area
 ; transient state while preserving earned tier/charges and selected class.
 jsr FwEnsure
 jsr FwAreaReset
FwSceneInitRestore:
 pla
 tay
 pla
 tax
 pla
 plp
 rts

; Only C is a result; AXY and every other incoming flag survive. All sixteen
; cookie bytes are checked. No PPU access and no code execution from RAM3.
FwCheck:
 php
 pha
 txa
 pha
 lda CurrentBankC
 pha
 lda SelectedCharacter
 cmp #22
 bne FwCheckNo
 lda #3
 sta CurrentBankC
 sta $5116
 ldx #15
FwCheckByte:
 lda $dfe0,x
 cmp FwCookie,x
 bne FwCheckNo
 dex
 bpl FwCheckByte
 tsx
 lda $0104,x
 ora #1
 bne FwCheckSet
FwCheckNo:
 tsx
 lda $0104,x
 and #$fe
FwCheckSet:
 sta $0104,x
 pla
 sta CurrentBankC
 sta $5116
 pla
 tax
 pla
 plp
 rts

; Full cold loader: ROM A62 executes while the destination is raw C3. No
; $5102/$5103/$5113 writes. AXY/P (except result C) and R0/R1 are preserved.
FwLoad:
 php
 pha
 txa
 pha
 tya
 pha
 lda R0
 pha
 lda R1
 pha
 lda CurrentBankC
 pha
 lda ReloadCHRBank
 pha
 lda SelectedCharacter
 cmp #22
 jne FwLoadRejected
 lda OperMode
 jeq FwLoadRejected
 lda Mirror_PPUMASK
 and #$18
 jne FwLoadRejected
 lda DisableScreenFlag
 jeq FwLoadRejected
 lda NmiDisable
 jpl FwLoadRejected
 jsr FwCheck
 jcs FwLoadWarm
 sei
 lda #0
 sta ReloadCHRBank
 ; Native forcedblank checkpoint establishes all twelve write-only CHR
 ; latches from the real software publication and upper0 before borrowing11.
 jsr X5PublishChr
 lda #3
 sta CurrentBankC
 sta $5116
 lda #0
 sta $dfe0                    ; first destination write, validity invalid FIRST
 lda Mirror_PPUCTRL
 and #$fb                     ; buffered increment1
 ora #$20                     ; select last-written BG set with8x16 enabled
 sta $2000
 lda #0
 sta R0
 lda #$c0
 sta R1
FwLoadPage:
 jsr FwMapPage
 ldx #4
FwCopy256:
 lda $2007
 sta (R0),y
 iny
 bne FwCopy256
 inc R1
 dex
 bne FwCopy256
 lda R1
 sec
 sbc #4
 sta R1
 jsr FwMapPage
 ldx #4
FwVerify256:
 lda $2007
 cmp (R0),y
 bne FwLoadFailed
 iny
 bne FwVerify256
 inc R1
 dex
 bne FwVerify256
 lda R1
 cmp #$e0
 bne FwLoadPage
 ldx #15
FwPublishCookie:
 lda FwCookie,x
 sta $dfe0,x
 dex
 bne FwPublishCookie
 lda #$a7
 sta $dfe0                    ; valid published LAST, after full8192B verify
 tsx
 lda $0108,x
 ora #1
 sta $0108,x
 jmp FwRestorePPU
FwLoadFailed:
 lda #0
 sta $dfe0
 tsx
 lda $0108,x
 and #$fe
 sta $0108,x
FwRestorePPU:
 jsr X5PublishChr             ; genuine twelve-window checkpoint restore
 lda Mirror_PPUCTRL
 sta $2000
 bit $2002
 lda HorizontalScroll
 sta $2005
 lda VerticalScroll
 sta $2005                    ; native latch0, no black-background address leak
 jmp FwRestoreContext
FwLoadWarm:
 tsx
 lda $0108,x
 ora #1
 sta $0108,x
 jmp FwRestoreContext
FwLoadRejected:
 tsx
 lda $0108,x
 and #$fe
 sta $0108,x
FwRestoreContext:
 pla
 sta ReloadCHRBank
 pla
 sta CurrentBankC
 sta $5116
 pla
 sta R1
 pla
 sta R0
 pla
 tay
 pla
 tax
 pla
 plp
 rts

; Physical893+destination1KB index0..7. Destination C000..DFFF aliases A3.
FwMapPage:
 lda #3
 sta $5130
 lda R1
 sec
 sbc #$c0
 lsr
 lsr
 clc
 adc #$7d
 sta $512b
 bit $2002
 lda #$0c
 sta $2006
 lda #0
 sta $2006
 lda $2007                    ; actual buffered-read discard
 ldy #0
 rts

; Context-safe explicit retirement/newgame APIs. SceneInit retires on a
; foreign resolved owner; eventual common profile hooks remain root-reviewed.
FwRetire:
 php
 pha
 lda SelectedCharacter
 cmp #22
 beq FwRetireDone
 jsr FwInvalidate
FwRetireDone:
 pla
 plp
 rts
FwInvalidate:
 php
 pha
 lda CurrentBankC
 pha
 lda #3
 sta CurrentBankC
 sta $5116
 lda $dfe0
 cmp #$a7
 bne FwInvalidateDone
 lda $dfe1
 cmp #22
 bne FwInvalidateDone
 lda #0
 sta $dfe0
FwInvalidateDone:
 pla
 sta CurrentBankC
 sta $5116
 pla
 plp
 rts

; Actual area/life service19, not the boot/newgame initializer. Native
; RosterClearState calls through LmResetGate on every InitializeArea. Code
; readiness may be cold here: keep earned FF records untouched and defer the
; genuine Ensure/AreaReset to successful InitScreen in that case.
FwSelectedReset:
 lda SelectedCharacter
 cmp #22
 bne FwSelectedResetUnavailable
 lda #0
 sta SafecallA_SMC+1
 lda #<SpecialRosterClear
 sta FarcallJmpTarget_SMC+1
 lda #>SpecialRosterClear
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(SpecialRosterClear)|$80)
 jsr FarCallCommon
 jsr FwCheck
 bcc FwSelectedResetUnavailable
 jsr FwEnsure
 jmp FwAreaReset
FwSelectedResetUnavailable:
 clc
 rts

; Every genuine worker has a typed source gate. Cookie guard saves originalP;
; real FarCallCommon loads originalA and raw03. Source C output is restored
; explicitly without consuming intentional R0/R1 or any new scratch lease.
.macro FW_GATE public,target
 .import target
 .export public
 public:
  php
  jsr FwCheck
  jcc FwGateUnavailable
  plp
  sta SafecallA_SMC+1
  lda #<target
  sta FarcallJmpTarget_SMC+1
  lda #>target
  sta FarcallJmpTarget_SMC+2
  jmp FwCallEnter
.endmacro
FwGateUnavailable:
 plp
 clc
 rts
FwCallEnter:
 lda CurrentBankC
 pha
 lda #3
 jsr FarCallCommon
 ; Drop savedC underneath the complete source result using only caller-owned
 ; CPUstack. No output pointer or application state is used as transport.
FwRestoreC:
 php
 pha
 tya
 pha
 txa
 pha
 tsx
 lda $0105,x
 sta CurrentBankC
 sta $5116
 lda $0104,x
 sta $0105,x
 lda $0103,x
 sta $0104,x
 lda $0102,x
 sta $0103,x
 lda $0101,x
 sta $0102,x
 inx
 txs
 pla
 tax
 pla
 tay
 pla
 plp
 rts

; Explicit own ABI retirement: old FwGlobalInit had no emitted consumer.
.export FwMenuName
FwMenuName:
 sta SafecallA_SMC+1
 lda #<FmQueueName
 sta FarcallJmpTarget_SMC+1
 lda #>FmQueueName
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(FmQueueName)|$80)
 jmp FarCallCommon
 .res 23-(*-FwMenuName),$ea
FW_GATE FwEnsure,FfEnsure
FW_GATE FwAreaReset,FfAreaReset
; Retired unused source aliases; live movement/collection use typed host gates.
FwHudNames:
 .byte "RETHGIF ","M ETIHW ","M KCALB ","  FEIHT "
; Only class*8 +0..6 reads the32B table above. This19B helper occupies
; its explicit previously unused20B own padding, preserving every old PC.
FwLivesBodyColors:
 php
 pha
 txa
 pha
 tya
 pha
 jsr FwCheck                 ; all16 cookie bytes before any RAM3 ACK access
 lda #2                      ; cold force: no authenticated-state writes
 bcc :+
 lda #1                      ; valid force: queue body and commit ACK on success
:pha
 jmp FwPaletteMapC           ; genuine saved-context C mapper/queue/restore
 .res 52-(*-FwHudNames),$ea
FW_GATE FwFullPower,FfFullPower
FW_GATE FwInjuryStatus,FfInjuryStatus
FW_GATE FwInjuryStart,FfInjuryStart
FW_GATE FwDeathStart,FfDeathStart
FW_GATE FwDeathUpdate,FfDeathUpdate
; Actual status caller supplies A0 after native MARIO text was copied.
.export FwStatusName
FwStatusName:
 cmp #0
 beq FwStatusOwn
 cmp #1
 bne FwStatusDone
 cpy #30
 bne FwStatusDone
 sty VRAM_Buffer1_Offset
 jmp FwLivesColors
FwStatusOwn:
 php
 txa
 pha
 tya
 pha
 lda FfVariant
 and #3
 asl
 asl
 asl
 tax
 ldy #6
FwStatusCopy:
 lda FwHudNames,x
 sta VRAM_Buffer1+11,y
 inx
 dey
 bpl FwStatusCopy
 pla
 tay
 pla
 tax
 plp
 lda #0
FwStatusDone:
 rts
 .res 52-(*-FwStatusName),$ea
FW_GATE FwBox,FfBox
.import FwPreviewPublish,DrawMetasprite
.export FwPortraitDraw
; Genuine Only-service17 is the actual title/lives DRAW callback. Service3
; already built SmPosePtr/body0, and HpPrepareNativePointers took its snapshot.
FwPortraitDraw:
 php
 pha
 txa
 pha
 tya
 pha
 jsr FwPreviewPublish
 pla
 tay
 pla
 tax
 pla
 plp
 sta SafecallA_SMC+1
 lda #<DrawMetasprite
 sta FarcallJmpTarget_SMC+1
 lda #>DrawMetasprite
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(DrawMetasprite)|$80)
 jmp FarCallCommon
FwLivesColors:
 lda BackgroundColorCtrl
 pha
 lda #2
 sta BackgroundColorCtrl
 jsr FwLivesBodyColors
 pla
 sta BackgroundColorCtrl
 lda #1
 rts
 .assert *-FwPortraitDraw<=52,error,"OWN retired FF two-gate span"
 .res 52-(*-FwPortraitDraw),$ea
FW_GATE FwSide,FfSide
.include "ff-epoch-rom.inc"
FW_GATE FwProjectileEntry,FfProjectileEntry
FW_GATE FwGraphics,FfGraphics
FW_GATE FwRenderChunk,FfRenderChunk
FW_GATE FwPublishChunk,FfPublishChunk
.import FfPortrait
.export FwPortrait
FwPortrait:
 php
 jsr FwCheck
 bcs FwPortraitReady
 lda SelectedCharacter
 cmp #22
 bne FwPortraitNo
 plp
 lda CurrentBankC
 pha
 jsr FwPreviewPortrait
 jmp FwRestoreC
FwPortraitNo:
 plp
 clc
 rts
FwPortraitReady:
 plp
 sta SafecallA_SMC+1
 lda #<FfPortrait
 sta FarcallJmpTarget_SMC+1
 lda #>FfPortrait
 sta FarcallJmpTarget_SMC+2
 jmp FwCallEnter
; Two obsolete unused exports are explicitly retired; fixed52B region.
.import FwMuxMenuA,FwMuxSceneA,SmFreezeLastBlue
.export FwMuxMenuResolve,FwMuxScene
FwMuxMenuResolve:
 sta SafecallA_SMC+1
 lda #<FwMuxMenuA
 sta FarcallJmpTarget_SMC+1
 lda #>FwMuxMenuA
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(FwMuxMenuA)|$80)
 jmp FarCallCommon
FwMuxScene:
 lda SmFreezeLastBlue
 bmi FwMuxSceneOwn
 lda SelectedCharacter
 cmp #22
 beq FwMuxSceneOwn
 jmp FwRetire
FwMuxSceneOwn:
 sta SafecallA_SMC+1
 lda #<FwMuxSceneA
 sta FarcallJmpTarget_SMC+1
 lda #>FwMuxSceneA
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(FwMuxSceneA)|$80)
 jmp FarCallCommon
 .res 52-(*-FwMuxMenuResolve),$ea
 .assert *-FwMuxMenuResolve=52,error,"Own retired gate region"

FwCookie:
.incbin "ff-cookie.bin"

FW_GATE FwHostMovement,FfHostMovement
FW_GATE FwHostHeadWithin,FfHostHeadWithin
FW_GATE FwHostHead,FfHostHead
FW_GATE FwHostFeet,FfHostFeet
FW_GATE FwHostSide,FfHostSide
FW_GATE FwHostWall,FfHostWall
FW_GATE FwHostAfterTerrain,FfHostAfterTerrain
FW_GATE FwHostBox,FfHostBox
FW_GATE FwHostAdder,FfHostAdder
FW_GATE FwHostTarget,FfHostTarget
FW_GATE FwHostDamage,FfHostDamage
FW_GATE FwHostContact,FfHostContact
FW_GATE FwHostWeapons,FfHostWeapons
FW_GATE FwHostNewEnemy,FfHostNewEnemy
FW_GATE FwHostFresh,FfHostFresh
FW_GATE FwHostCollect,FfHostCollect
FW_GATE FwHostPowerupTick,FfHostPowerupTick
FW_GATE FwHostGraphics,FfHostGraphics
FW_GATE FwHostBody,FfHostBody
FW_GATE FwHostImpulseAccepted,FfHostImpulseAccepted

FW_GATE FwVisible,FfVisible

.export FwGateUnavailable
