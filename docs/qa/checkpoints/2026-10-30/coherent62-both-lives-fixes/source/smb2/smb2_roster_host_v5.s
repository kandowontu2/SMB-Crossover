; Genuine current Fresh/forcedblank consumers in retired old wrapper span.
.pushseg
.segment "CHEATS_FOUR"
.export S2BoundaryLateUI,S2InitScreenPrepare,S2TypedHostBegin,S2TypedHostEnd
S2TypedHostBegin:
.assert *=$aa21,lderror,"Retired S2-only wrapper span"
; True late caller is GameCore::ClrPlrPal, within begun foreground.
; Caller A=0 and original ResetPalStar kills A/NZ; preserve its full incoming
; flags/registers until the genuine source or original worker is entered.
.proc S2BoundaryLateUI
 php
 pha
 lda SelectedCharacter
 cmp #25
 bne Foreign
 lda FamilyMainCommit
 and #1
 beq Foreign
 lda S2Ready
 cmp #$b2
 bne Foreign
 lda GamePauseStatus
 and #1
 bne Foreign
 pla
 plp
 farcall S2MainEnd,jmp
Foreign:
 pla
 plp
 farcall ResetPalStar,jmp
 .assert *-S2BoundaryLateUI=70,lderror,"Own70B guarded late worker"
 .res 4,$ea
.endproc
.proc S2InitScreenPrepare
 farcall QwSceneInit          ; genuine Quick/Ar/FF/nativeMove exactly once
 php
 pha
 lda SelectedCharacter
 cmp #25
 bne Done
 lda FamilyMainCommit
 and #1
 beq Done                     ; constructor publication interval owns state
 txa
 pha
 tya
 pha
 lda CurrentBankC
 pha
 farcall S2Ensure              ; retain earned health/carry across real areas
 bcc Restore
 farcall S2Graphics
 bcc Restore
 farcall S2PublishBody         ; actual original body CHR/descriptor producer
 lda #$ff
 sta S2PaletteAck              ; native screen ROM palettes run before ack
Restore:
 pla
 BankPRGC a
 pla
 tay
 pla
 tax
Done:pla
 plp
 rts
.endproc
S2TypedHostCodeEnd:
.export S2TypedWorldPalette,S2TypedScene,S2TypedGraphics,S2ServiceVeneers,S2ServiceVeneersEnd,S2ServiceUnavailable,S2ServiceCodeEnd
; Genuine same-bank copy of the original native world palette arithmetic.
.proc S2TypedWorldPalette
 lda AreaType
 asl
 sta R0
 asl
 clc
 adc R0
 adc #6
 tay
 rts
.endproc
.assert *<=$ab00,lderror,"Owned cold workers plus native arithmetic"
.res 223-(*-S2TypedHostBegin),$ff
S2ServiceVeneers:
; 0 Movement: no second integrator; requires sole actual S2MainGame hook
 jmp S2Tail_S2MainNativeNoop
; 1 Graphics: genuine descriptor and physical body CHR publication at actual graphics callback
 jmp S2TypedGraphics
; 2 Draw: native prebody pass: source vegetables only
 jmp S2Tail_S2MainDraw
; 3 Portrait: existing source portrait producer
 jmp S2MenuPortrait
; 4 Weapons: genuine source projectile contact pass
 jmp S2Tail_S2MainProjectiles
; 5 Injury: real admitted enemy X and relativeX
 jmp S2Tail_S2MainInjury
; 6 InjuryStatus: source health owns death; return X1
 jmp S2Tail_S2MainStatus
; 7 DeathStart: genuine source death initialization
 jmp S2Tail_S2DeathStart
; 8 Death: genuine source death tick
 jmp S2Tail_S2DeathUpdate
; 9 Visible: carry visible policy
 jmp S2Tail_S2MainVisible
; 10 Head: genuine fixed native head query
 jmp S2Tail_S2Head
; 11 BodyPolicy: actual admitted native actor overlap
 jmp S2Tail_S2MainBody
; 12 Adder: incoming A raw25 native adder contract
 jmp S2Tail_S2MainAdder
; 13 Box: incoming A raw25 source crouch profile
 jmp S2Tail_S2MainBoxProfile
; 14 Side: genuine fixed native side query
 jmp S2Tail_S2Side
; 15 Fresh: requires remove v6 earlier Fresh constructor hook when this route is joined; exactly one constructor
 jmp S2Tail_S2ColdInit
; 16 FullBox: genuine source full collision box
 jmp S2Tail_S2MainBox
; 17 Actual cold draw: preparation is service3; native OAM consumer here.
 jmp S2PortraitDrawC
; 18 MenuName: actual source queued name
 jmp S2MenuName
; 19 Reset: native JnResetDispatch once, then source Ensure/import
 jmp S2TypedScene
; 20 Prepare: genuine native source pickup metadata
 jmp S2Tail_S2MainPrepare
; 21 Rise: native engine owns generic rise
 jmp S2Tail_S2MainNativeNoop
; 22 Private: no separate source inventory pickup collision
 jmp S2Tail_S2MainNativeNoop
; 23 MatureCollision: maturity only, never collect
 jmp S2Tail_S2MainMature
; 24 Pickup: real collector X and source mushroom/flower; native star/1up fallback
 jmp S2Tail_S2MainPickup
; 25 FullPower: genuine source maxHP and vegetable reserve
 jmp S2Tail_S2FullPower
; 26 Colors: actual native GetPlayerColors invalidation; source P0 only, eye-role composition pending
 jmp S2HostForcePalette
; 27 BounceOnly: real successful native stomp impulse only
 jmp S2Tail_S2MainStomp
; 28 HeadWithinOnly: genuine shared native terrain query
 jmp S2Tail_Z2HeadWithinTerrain
; 29 UI: source HUD retract/early policy
 jmp S2Tail_S2HudEarly
; 30 Status: genuine seven-character native status packet
 jmp S2MenuStatus
; 31 Bounce: same real native stomp consumer
 jmp S2Tail_S2MainStomp
; 32 WorldPalette: exact native AreaType*6+6/Y contract
 jmp S2TypedWorldPalette
; 33 Powerup: native star/power animation, requires integrated source color hook
 jmp S2Tail_GuestPowerupUpdate
; 34 WeaponTail: genuine source projectile contact pass
 jmp S2Tail_S2MainProjectiles
; 35 Vine: actual native six-vine-sprite reservation/render consumer
 jmp S2Tail_MmReserveVine
S2ServiceVeneersEnd:
.assert *=$ab6c,lderror,"Exactly36 genuine3-byte JMP slots"
S2ServiceUnavailable:
 clc
 rts
.macro S2TypedTail Name,Target,ExpectedBank
.proc Name
 ; Actual common ingress has already saved sourceA in SafecallA_SMC.
 ; Preserve it across the extra same-source target preparation. LDA/STA/JMP
 ; retain CVDI; FarCallCommon reloads originalA and its genuine NZ at target.
 .assert .bank(Target)=ExpectedBank,lderror,"Linked actual target bank"
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(Target)|$80)
 ; The first3 bytes store NextBank, not SavedA. Enter the real start because
 ; this tail passes targetbank in A rather than prewriting NextBank_SMC.
 jmp FarCallCommon
 .assert *-Name=15,lderror,"Owned tail only; never overwrite sourceA"
.endproc
.endmacro
S2TypedTail S2Tail_S2MainNativeNoop,S2MainNativeNoop,118
S2TypedTail S2Tail_S2MainDraw,S2MainDraw,118
S2TypedTail S2Tail_S2MainProjectiles,S2MainProjectiles,118
S2TypedTail S2Tail_S2MainInjury,S2MainInjury,118
S2TypedTail S2Tail_S2MainStatus,S2MainStatus,118
S2TypedTail S2Tail_S2DeathStart,S2DeathStart,118
S2TypedTail S2Tail_S2DeathUpdate,S2DeathUpdate,118
S2TypedTail S2Tail_S2MainVisible,S2MainVisible,118
S2TypedTail S2Tail_S2Head,S2Head,118
S2TypedTail S2Tail_S2MainBody,S2MainBody,118
S2TypedTail S2Tail_S2MainAdder,S2MainAdder,118
S2TypedTail S2Tail_S2MainBoxProfile,S2MainBoxProfile,118
S2TypedTail S2Tail_S2Side,S2Side,118
S2TypedTail S2Tail_S2ColdInit,S2ColdInit,118
S2TypedTail S2Tail_S2MainBox,S2MainBox,118
S2TypedTail S2Tail_S2MainPrepare,S2MainPrepare,118
S2TypedTail S2Tail_S2MainMature,S2MainMature,118
S2TypedTail S2Tail_S2MainPickup,S2MainPickup,118
S2TypedTail S2Tail_S2FullPower,S2FullPower,118
S2TypedTail S2Tail_S2MainStomp,S2MainStomp,118
S2TypedTail S2Tail_Z2HeadWithinTerrain,Z2HeadWithinTerrain,71
S2TypedTail S2Tail_S2HudEarly,S2HudEarly,118
S2TypedTail S2Tail_GuestPowerupUpdate,GuestPowerupUpdate,10
S2TypedTail S2Tail_MmReserveVine,MmReserveVine,66
.proc S2TypedScene
 ; Preserve the real native area initializer's control-flow return. Source
 ; scene import alone is not an InitializeArea implementation.
 farcall JnResetDispatch      ; genuine native area-reset path, NOT blank screen
 farcall S2MainScene,jmp
.endproc
.proc S2TypedGraphics
 farcall S2Graphics
 bcc Done
 farcall S2PublishBody,jmp
Done:rts
.endproc
S2ServiceCodeEnd:
.macro S2BoundaryGate Name,Owned,Legacy
.export Name
.proc Name
 php
 pha
 lda SelectedCharacter
 cmp #25
 beq Own
 pla
 plp
 farcall Legacy,jmp
Own:pla
 plp
 farcall Owned,jmp
 .assert *-Name=49,lderror,"Exact own49B owner boundary"
.endproc
.endmacro
S2BoundaryGate S2BoundaryGame,S2MainGame,HuGameRoutinesDirect
S2BoundaryGate S2BoundaryImmunity,S2MainImmunity,MarioSourceBodyImmunity
S2BoundaryCodeEnd:
.assert *=$ad83,lderror,"Reuse exactly remaining98B, no following shift"
S2TypedHostEnd:
.assert *=$ad83,lderror,"Following menu/HUD/palette PCs exact"
.popseg
; PRIVATE additive menu/lives endpoints; source gameplay/audio are unchanged.
; A118 and C80 occupy only the previously measured remainder of their leases.
.pushseg
.segment "CHEATS_FOUR"
.export S2MenuResolve,S2MenuName,S2MenuStatus,S2MenuPortrait,S2MenuToggle
S2MenuCodeBegin:
.proc S2MenuResolve
 ; Preserve the actual former owner on the stack, not a global overlay flag.
 ; CmHostResolve defines X itself. Recover its genuine incoming A unchanged.
 pha
 lda SelectedCharacter
 pha
 tsx
 lda $0102,x
 farcall QwMenuResolve
 php
 pha
 cmp #25
 bne Done
 phx
 phy
 tsx
 lda $0105,x                    ; actual previous SelectedCharacter, before resolve.
 cmp #25
 bne Cold
 farcall S2Ensure                   ; same owner/variant may preserve Continue rewards.
 jmp Restored
Cold:farcall S2ColdInit              ; new selection precedes EVERY Ready read.
Restored:
 ply
 plx
Done:pla
 plp
 pla
 pla
 lda SelectedCharacter          ; exact original resolver's returned A/N/Z.
 rts
.endproc
.proc S2MenuName
 php
 pha
 lda SelectedCharacter
 cmp #25
 beq Own
 pla
 plp
 farcall NrQueueSelectName,jmp
Own:
 pla
 plp
 farcall FmQueueName,jmp
 .res 3,$ea ; same23B own suffix; nativeHUD/statusunchanged
.endproc
.proc S2MenuToggle
 php
 pha
 lda SelectedCharacter
 cmp #25
 beq Own
 pla
 plp
 farcall NrMenuToggle,jmp
Own:pla
 plp
 lda CrossoverMenuPressed
 and #Select_Button
 beq No
 inc S2Variant
 lda S2Variant
 and #3
 sta S2Variant
 sec
 rts
No:clc
 rts
.endproc
.proc S2MenuStatus
S2LivesOwnStart:
 php
 pha
 lda SelectedCharacter
 cmp #25
 beq Own
 pla
 plp
 farcall JnStatusName,jmp
Own:
 ; SourceA remains in the entry stack while originalX/Y are pushed.
 phx
 phy
 tsx
 lda $0103,x
 tax
 ldy CurrentBankC
 ; Exact selected path from source S2GraphicsBank, A74 remains mapped.
 lda #80|$80
 sta CurrentBankC
 sta $5116
 jsr S2TextStatusC
 sty CurrentBankC              ; A74 stays mapped while C is restored.
 sty $5116
 ply
 plx
 pla                           ; original sourceA0/1/other contract.
 plp
 rts
 .assert *-S2LivesOwnStart<=71,error,"Existing71B public Status envelope"
 .res 71-(*-S2LivesOwnStart),$ea
.endproc
.proc S2MenuPortrait
 farcall S2Ensure
 farcall S2GraphicsBank
 lda S2NativeCharacter
 asl
 ora S2Size
 .repeat 5
 asl
 .endrepeat
 ora #1                        ; authentic standing, unheld, source-facing1.
 tax
 lda S2BodyRecord,x
 farcall S2Graphics::SetBody         ; genuine shared descriptor/CHR tail, no copy.
 farcall S2PublishBody              ; actual X5PortraitRender consumes this record.
 lda #$ff
 sta S2PaletteAck
 farcall S2MainPalette,jmp
.endproc
S2MenuCodeEnd:
.assert *<=$c000,lderror,"SMB2 menu exceeds remaining CORE118 lease"
.segment "CHEATS_FOUR"
S2MenuGlobalBegin:
.proc S2MenuGlobal
 lda #0
 sta S2Variant                 ; dedicated selector, never overlay Ready.
 farcall IcGlobalInit,jmp
.endproc
S2MenuGlobalEnd:
.assert *<=$c000,lderror,"SMB2 menu exceeds remaining A74 lease"
.segment "CD_GFX"
S2MenuArtBegin:
.proc S2MenuNameC
 ldx VRAM_Buffer1_Offset
 cpx #65                       ; 19-byte command plus terminator within84B.
 bcs Done
 stx R1
 lda #$23
 sta VRAM_Buffer1,x
 lda #<X5MenuNameAddress
 sta VRAM_Buffer1+1,x
 lda #16
 sta VRAM_Buffer1+2,x
 lda #$24
 ldy #15
Blank:sta VRAM_Buffer1+3,x
 inx
 dey
 bpl Blank
 ldx R1
 txa
 clc
 adc #7
 tax
 lda #8
 sta R0
 jsr S2MenuCopyC
 txa
 clc
 adc #4
 tax
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
Done:rts
.endproc
.proc S2MenuCopyC
 ; Genuine A118 caller explicitly leases C80 before this direct JSR.
 lda S2Variant
 and #3
 asl
 asl
 asl
 tay
Loop:lda Names,y
 sta VRAM_Buffer1,x
 inx
 iny
 dec R0
 bne Loop
 rts
Names:.byte "MARIO   ","LUIGI   ","TOAD    ","PEACH   "
.endproc
S2MenuArtEnd:
.assert *<=$d600,lderror,"SMB2 menu exceeds remaining C80 lease"
.popseg
