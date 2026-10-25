; Full-roster ABI implemented with genuine MMC3 banking. Private candidate.
X5ChrMode=$73e0
X5SpecialChrUpper=$73ec
X5HudChrUpper=$73ed
X5WideChrActive=$73ee
M3CacheProfile=$73db
M3CacheLoads=$73dc
.export M3CacheProfile,M3CacheLoads,M3CacheEnsure,M3CacheBoot
; The native Contra/Zelda sound engine is inactive in every wide-art profile.
; Its two160B scratch images hold the graphics cache directory and upload queue.
M3Masks=RgAudioZp
M3Wanted=RgAudioZp+144
M3Map=RgAudioCpuZp
M3Queue=RgAudioCpuZp+64
M3Pending=RgAudioCpuZp+75
M3Cursor=RgAudioCpuZp+76
M3Victim=RgAudioCpuZp+77
M3Target=RgAudioCpuZp+78
M3Count=RgAudioCpuZp+79
M3HardwareBody=RgAudioCpuZp+80
M3Scan=RgAudioCpuZp+81
M3DrawSlot=RgAudioCpuZp+82
M3HardwareSpecial=RgAudioCpuZp+83
M3CacheBase=132
.export M3Pending,M3HardwareBody,M3HardwareSpecial,M3ResolveOam,M3NmiUpload
.export X5ChrMode,X5SpecialChrUpper,X5HudChrUpper,X5WideChrActive
.export X5PublishChr,X5ColdInit,X5SetPhysicalChr,X5SetSpecialChr,X5ClearChrModes
.pushseg
.segment "X5_PUBLISH"
X5ColdInit:
 lda #0
 ldx #15
:sta X5MenuVariants,x
 dex
 bpl :-
 jsr X5ClearChrModes
 lda #0
 sta M3CacheProfile
 sta M3CacheLoads
 sta M3Pending
 lda CurrentBankC
 pha
 BankPRGC #.bank(M3CacheBoot)
 jsr M3CacheBoot
 pla
 BankPRGC a
 rts
X5PublishChr:
 rts
M3CacheEnsure:
 jsr M3ChooseProfile
 cmp M3CacheProfile
 beq DoneEnsure
 sta $020f
 lda CurrentBankC
 pha
 BankPRGC #.bank(M3CacheLoad)
 jsr M3CacheLoad
 pla
 BankPRGC a
 jsr X5ClearChrModes
DoneEnsure:rts
M3ChooseProfile:
 lda SelectedCharacter
 cmp #1
 bne CheckDw
 lda ProtoVariant
 beq LegacyProfile
 lda #1
 rts
CheckDw:cmp #12
 bne CheckZ2
 lda DarkwingVariant
 beq LegacyProfile
 lda #2
 rts
CheckZ2:cmp #4
 bne CheckCv3
 lda Z2Variant
 beq LegacyProfile
 lda #3
 rts
CheckCv3:cmp #5
 bne CheckRow
 lda Cv3Variant
 beq LegacyProfile
 clc
 adc #6
 rts
CheckRow:sec
 sbc #13
 bcc LegacyProfile
 cmp #7
 bcs LegacyProfile
 tax
 lda M3RowProfiles,x
 rts
LegacyProfile:lda #0
 rts
M3RowProfiles:.byte 4,6,10,11,12,5,13
X5SetPhysicalChr:
 cpy #5
 beq IgnorePartner
 ; All private body pages are resident at 52+offset in the selected family.
 ldy M3CacheProfile
 sec
 sbc M3FirstLo,y
 clc
 adc #52
 sta CurrentCHRBank+2
 lda #$80
 sta X5ChrMode
 lda #1
 sta X5WideChrActive
 sta ReloadCHRBank
IgnorePartner:
 rts
X5SetSpecialChr:
 ; The OAM resolver chooses a background-preserving composite after drawing.
 lda #2
 sta SsChrPhysical
 lda #1
 sta SsChrActive
 sta ReloadCHRBank
 rts
X5ClearChrModes:
 lda #0
 ldx #11
:sta X5ChrMode,x
 dex
 bpl :-
 sta X5WideChrActive
 sta X5SpecialChrUpper
 sta X5HudChrUpper
 rts
M3FirstLo:
 .byte <0,<256,<276,<308,<340,<380,<412,<460,<460,<460,<668,<708,<524,<604
.popseg

.pushseg
.segment "M3_CACHE"
; Bulk transfers run from the C window while A reads raw graphics. Rendering,
; NMI and IRQ are disabled for the transfer; foreground SMC is untouched.
M3CacheBoot:
 jsr M3Blank
 lda #0
 sta $0200
 sta $0201
 sta $0202
 sta $0203
BootPages:
 jsr M3UploadPage
 inc $0200
 inc $0202
 bne BootPages
 jmp M3Unblank
M3CacheLoad:
 jsr M3Blank
 ldx $020f
 stx M3CacheProfile
 inc M3CacheLoads
 lda M3FamilyLo,x
 sta $0200
 lda M3FamilyHi,x
 sta $0201
 lda M3FamilyCount,x
 sta $0203
 lda #52
 sta $0202
FamilyPages:
 jsr M3UploadPage
 inc $0200
 bne :+
 inc $0201
:inc $0202
 dec $0203
 bne FamilyPages
 ldx M3CacheProfile
 cpx #2
 bcc FinishLoad
 lda #0
 sta M3Pending
 sta M3Victim
 ldx #143
ClearMasks:sta M3Masks,x
 dex
 cpx #$ff
 bne ClearMasks
 lda #M3CacheBase
 sta $0202
Template:
 lda #0
 sta $0201
 lda #2
 sta $0200
 jsr M3UploadPage
 inc $0200
 inc $0202
 jsr M3UploadPage
 inc $0202
 lda $0202
 cmp #168
 bcc Template
FinishLoad:
 ; The SMB3 status font differs only in six HUD-only glyphs. MMC3 shares
 ; background banks across the split, so install that font at physical0
 ; while this family owns the cache, and restore it on every other family.
 lda #0
 sta $0200
 sta $0201
 sta $0202
 lda M3CacheProfile
 cmp #12
 bne FontReady
 lda #<545
 sta $0200
 lda #>545
 sta $0201
FontReady:
 jsr M3UploadPage
 jmp M3Unblank
M3Blank:
 lda #0
 sta PPUCTRL
 sta PPUMASK
 sta IRQDISABLE
 bit PPUSTATUS
 rts
M3Unblank:
 BankPRGA CurrentBank
 lda #1
 sta ReloadCHRBank
 lda Mirror_PPUCTRL
 sta PPUCTRL
 rts
M3UploadPage:
 ; source=$0201:$0200 (1 KiB page), destination=$0202 (CHR-RAM page).
 lda $0201
 asl
 asl
 asl
 asl
 asl
 sta R0
 lda $0200
 lsr
 lsr
 lsr
 ora R0
 clc
 adc #100
 BankPRGA a
 lda $0200
 and #7
 asl
 asl
 ora #$a0
 sta R1
 lda #0
 sta R0
 lda #PRG_FIXED_8|2
 sta BANK_SELECT
 lda $0202
 sta BANK_DATA
 bit PPUSTATUS
 lda #$10
 sta PPUADDR
 lda #0
 sta PPUADDR
 ldx #4
 ldy #0
CopyPage:
 lda (R0),y
 sta PPUDATA
 iny
 bne CopyPage
 inc R1
 dex
 bne CopyPage
 rts
M3FamilyLo:.byte <52,<256,<276,<308,<340,<380,<412,<460,<460,<460,<668,<708,<524,<604
M3FamilyHi:.byte >52,>256,>276,>308,>340,>380,>412,>460,>460,>460,>668,>708,>524,>604
M3FamilyCount:.byte 116,20,32,32,40,32,48,64,64,64,40,48,80,64
M3SpecialLo:.byte 0,0,<302,<335,0,0,<425,<518,<520,<522,<704,<710,<544,0
M3SpecialHi:.byte 0,0,>302,>335,0,0,>425,>518,>520,>522,>704,>710,>544,0

; Render-time relocation of tagged wide weapon OAM. Every admitted sprite pair
; occupies a tile pair unused by both SMB terrain and retained native sprites.
; Eighteen complete2KiB composites are resident; animation repeats are cache hits.
.segment "X5_PUBLISH"
M3ResolveOam:
 lda M3CacheProfile
 cmp #2
 bcs :+
 rts
:lda #0
 sta M3Count
 ldx #7
ClearWanted:sta M3Wanted,x
 dex
 bpl ClearWanted
 ldx #63
ClearMap:sta M3Map,x
 dex
 bpl ClearMap
 lda #0
 sta M3DrawSlot
 ; Rotated admission shares rare >11-unique-pair overload across video frames.
 lda FrameCounter
 asl
 asl
 sta M3Scan
Scan:
 ldx M3Scan
 lda Sprite_Y_Position,x
 cmp #240
 bcs NextScan
 lda Sprite_Attributes,x
 and #$10
 beq NextScan
 lda Sprite_Tilenumber,x
 jsr M3SourcePair
 tax
 lda M3Map,x
 bne NextScan
 lda M3Count
 cmp #11
 bcs NextScan
 tay
 inc M3Count
 lda M3Count
 sta M3Map,x
 txa
 pha
 and #7
 tay
 lda M3Bits,y
 sta R0
 pla
 lsr
 lsr
 lsr
 tay
 lda M3Wanted,y
 ora R0
 sta M3Wanted,y
NextScan:
 lda M3Scan
 clc
 adc #4
 sta M3Scan
 inc M3DrawSlot
 lda M3DrawSlot
 cmp #64
 bcc Scan
 lda M3Count
 bne Search
 lda #2
 sta SsChrPhysical
 jmp M3OamDone
Search:
 ; Canonical sorted assignment makes the64-bit key sufficient for cache hits.
 lda #0
 sta M3Count
 ldx #0
Assign:
 lda M3Map,x
 beq AssignNext
 inc M3Count
 lda M3Count
 sta M3Map,x
AssignNext:inx
 cpx #64
 bcc Assign
 ldx #0
CacheSearch:
 stx M3Target
 txa
 asl
 asl
 asl
 sta R0
 ldy #0
Compare:
 ldx R0
 lda M3Masks,x
 cmp M3Wanted,y
 bne Miss
 inc R0
 iny
 cpy #8
 bcc Compare
 jmp Found
Miss:ldx M3Target
 inx
 cpx #18
 bcc CacheSearch
 lda M3Victim
 asl
 clc
 adc #M3CacheBase
 cmp M3HardwareSpecial
 bne SafeVictim
 inc M3Victim
 lda M3Victim
 cmp #18
 bcc SafeVictim
 lda #0
 sta M3Victim
SafeVictim:
 lda M3Victim
 sta M3Target
 inc M3Victim
 lda M3Victim
 cmp #18
 bcc :+
 lda #0
 sta M3Victim
:lda M3Target
 asl
 asl
 asl
 sta R0
 ldy #0
SaveKey:ldx R0
 lda M3Wanted,y
 sta M3Masks,x
 inc R0
 iny
 cpy #8
 bcc SaveKey
 lda #0
 sta M3Pending
 sta M3Cursor
 ldx #0
Queue:
 lda M3Map,x
 beq QueueNext
 ldy M3Pending
 txa
 sta M3Queue,y
 inc M3Pending
QueueNext:inx
 cpx #64
 bcc Queue
Found:
 lda M3Target
 asl
 clc
 adc #M3CacheBase
 sta SsChrPhysical
 ; All tagged OAM now refers to its packed composite, never raw world tiles.
 ldx #0
Patch:
 stx M3DrawSlot
 lda Sprite_Attributes,x
 and #$10
 beq PatchNext
 lda Sprite_Attributes,x
 and #$ef
 sta Sprite_Attributes,x
 lda Sprite_Tilenumber,x
 jsr M3SourcePair
 tay
 lda M3Map,y
 beq Hide
 tay
 lda M3FreeTiles-1,y
 ldx M3DrawSlot
 sta Sprite_Tilenumber,x
 jmp PatchNext
Hide:ldx M3DrawSlot
 lda #$f8
 sta Sprite_Y_Position,x
PatchNext:ldx M3DrawSlot
 inx
 inx
 inx
 inx
 bne Patch
M3OamDone:
 lda #1
 sta SsChrActive
 sta ReloadCHRBank
 rts
M3SourcePair:
 ; $c0..fe were source window4; $80..be were source window5.
 and #$7e
 eor #$40
 lsr
 rts
M3Bits:.byte 1,2,4,8,16,32,64,128
M3FreeTiles:.byte $c0,$c2,$da,$dc,$de,$ea,$f2,$f6,$fa,$fc,$fe

; NMI upload-only frame. Main code remains parked with NmiDisable=0 and the
; previous OAM/composite remains displayed. Three32B pairs fit the VBlank budget.
.segment "M3_CACHE"
M3NmiUpload:
 lda Mirror_PPUCTRL
 and #$fb
 sta PPUCTRL
 lda #3
 sta R7
Upload:
 ldy M3CacheProfile
 lda M3SpecialLo,y
 sta R0
 lda M3SpecialHi,y
 sta R1
 ldy M3Cursor
 lda M3Queue,y
 sta R6
 lsr
 lsr
 lsr
 lsr
 lsr
 clc
 adc R0
 sta R0
 bcc :+
 inc R1
:lda R1
 asl
 asl
 asl
 asl
 asl
 sta R2
 lda R0
 and #7
 asl
 asl
 ora #$a0
 sta R1
 lda R0
 lsr
 lsr
 lsr
 ora R2
 clc
 adc #100
 BankPRGA a
 lda R6
 and #7
 asl
 asl
 asl
 asl
 asl
 sta R0
 lda R6
 and #24
 lsr
 lsr
 lsr
 clc
 adc R1
 sta R1
 lda #PRG_FIXED_8|2
 sta BANK_SELECT
 lda SsChrPhysical
 clc
 adc #1
 sta BANK_DATA
 ldy M3Cursor
 lda M3UploadFreeTiles,y
 and #$3e
 asl
 asl
 asl
 asl
 sta R3
 lda M3UploadFreeTiles,y
 and #$3e
 lsr
 lsr
 lsr
 lsr
 ora #$10
 bit PPUSTATUS
 sta PPUADDR
 lda R3
 sta PPUADDR
 ldy #0
 .repeat 32,I
  lda (R0),y
  sta PPUDATA
  iny
 .endrepeat
 inc M3Cursor
 lda M3Cursor
 cmp M3Pending
 beq Uploaded
 dec R7
 jne Upload
 jmp RestoreBody
Uploaded:lda #0
 sta M3Pending
RestoreBody:
 lda #PRG_FIXED_8|2
 sta BANK_SELECT
 lda M3HardwareBody
 sta BANK_DATA
 bit PPUSTATUS
 lda #0
 sta PPUADDR
 sta PPUADDR
 rts
M3UploadFreeTiles:.byte $c0,$c2,$da,$dc,$de,$ea,$f2,$f6,$fa,$fc,$fe
.popseg

.pushseg
.segment "FIXED"
M3NmiCacheAllowed:
 ; The directory overlays inactive native sound scratch. Menu portraits and
 ; legacy Contra/Link audio may leave arbitrary bytes in its queue fields;
 ; those bytes must never become CHR upload jobs.
 lda M3CacheProfile
 cmp #2
 bcc NotOwned
 cmp #14
 bcs NotOwned
 lda NmiDisable
 rts
NotOwned:lda #1
 rts
.segment "LOWCODE"
M3NmiCacheBridge:
 jsr M3NmiCacheAllowed
 bne NoUpload
 lda M3Pending
 beq NoUpload
 BankPRGC #.bank(M3NmiUpload)
 jsr M3NmiUpload
 BankPRGA CurrentBank
 sec
 rts
NoUpload:clc
 rts
.popseg
