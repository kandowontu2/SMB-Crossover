from pathlib import Path
import importlib.util,shutil,json,hashlib
D=Path(__file__).resolve().parent;base=D/'extend_pz_mmc3_v8.py'
spec=importlib.util.spec_from_file_location('v8',base);v8=importlib.util.module_from_spec(spec);spec.loader.exec_module(v8)
def once(t,a,b):
 assert t.count(a)==1,(a,t.count(a));return t.replace(a,b)
def apply(source):
 v8.apply(source)
 packed=D/'mmc3-menu-packed-pz-v1';rawfile=source/'chr/characters/oversized-raw.chr';raw=bytearray(rawfile.read_bytes());before=bytes(raw)
 atlas=(packed/'chr/characters/mmc3-menu-previews.chr').read_bytes();assert len(atlas)==74*1024
 raw[756*1024:830*1024]=atlas;assert raw[:756*1024]==before[:756*1024]and raw[830*1024:]==before[830*1024:];rawfile.write_bytes(raw)
 shutil.copy2(packed/'ports/mmc3-oversized/menu_art.inc',source/'src/mmc3_menu_art.inc')
 shutil.copy2(packed/'chr/characters/mmc3-menu-previews.chr',source/'chr/characters/mmc3-menu-previews.chr')
 p=source/'src/mmc3_menu.s';t=p.read_text();t=once(t,' adc #33',' adc #37');t=once(t,' lda #66\n sta $0203',' lda #74\n sta $0203')
 t=once(t,'NotScrooge:cpx #12','''NotScrooge:cpx #9
 bne NotBass
 ldx RlVariant
 beq Chosen
 lda #33
 bne Chosen
NotBass:cpx #12''')
 t=once(t,'NotM3:cpx #18','''NotM3:cpx #17
 bne NotShip
 lda VvVariant
 beq ShipBase
 clc
 adc #33
 jmp Chosen
ShipBase:lda #27
 bne Chosen
NotShip:cpx #18''');p.write_text(t)
 p=source/'src/mmc3_oversized.s';t=p.read_text();t=once(t,' cmp #14\n bcs NotOwned',' cmp #18\n bcs NotOwned');p.write_text(t)
 # MMC3 has six logical banks and one direct body mode. The panel's previous
 # MMC5 +11 state accesses would overwrite unrelated RAM on this mapper.
 p=source/'src/zelda2_pause_panel.s';t=p.read_text()
 t=once(t,' lda Z2PanelChr\n sta CurrentCHRBank+11\n lda Z2PanelMode\n sta X5ChrMode+11\n inc ReloadCHRBank',' jsr M3Z2PanelFontClose\n inc ReloadCHRBank')
 t=once(t,' lda CurrentCHRBank+11\n sta Z2PanelChr\n lda X5ChrMode+11\n sta Z2PanelMode\n','')
 t=once(t,' lda #.lobyte(395)\n sta CurrentCHRBank+11\n lda #$81\n sta X5ChrMode+11\n inc ReloadCHRBank',' jsr M3Z2PanelFontOpen\n inc ReloadCHRBank')
 t=once(t,' lda #0\n sta $5204\n bit $5204\n sta PPUMASK',' lda #0\n sta IRQDISABLE\n sta PPUMASK')
 a='.include "zelda2_pause_tables.inc"';assert t.count(a)==1
 helper='''; The panel has admitted a fully blank native frame. All four overwritten
; OAM bytes are kept on the actual stack; the pane only backs up Y normally.
M3Z2PanelFontOpen:
 ldy #1
 bne M3Z2PanelFont
M3Z2PanelFontClose:
 ldy #0
M3Z2PanelFont:
 ldx #3
M3Z2SaveOam:
 lda $0200,x
 pha
 dex
 bpl M3Z2SaveOam
 lda #3
 sta $0200
 lda #0
 sta $0201
 cpy #0
 beq M3Z2FontSourceReady
 lda #<395
 sta $0200
 lda #>395
 sta $0201
M3Z2FontSourceReady:
 lda #3
 sta $0202
 lda CurrentBankC
 pha
 BankPRGC #.bank(M3Z2PanelFontCore)
 jsr M3Z2PanelFontCore
 pla
 BankPRGC a
 ldx #0
M3Z2RestoreOam:
 pla
 sta $0200,x
 inx
 cpx #4
 bcc M3Z2RestoreOam
 rts
.pushseg
.segment "M3_CACHE"
M3Z2PanelFontCore:
 lda #0
 sta PPUCTRL
 jsr M3UploadPage
 BankPRGA CurrentBank
 lda Mirror_PPUCTRL
 and #$fb
 sta PPUCTRL
 rts
.popseg
'''
 t=t.replace(a,helper+a);p.write_text(t)
 (source.parent/'private-changes-v9.json').write_text(json.dumps(dict(menu_identities=37,outline_settings=2,source_captures=str(D/'mmc3-menu-source-pz-v1'),menu_atlas_sha256=hashlib.sha256(atlas).hexdigest(),menu_raw_pages=[756,829],new_RAM_bytes=0,pause_font_source_page=395,pause_font_destination_and_restore_source_page=3,pause_preserves_four_OAM_scratch_bytes_on_real_stack=True,NMI_foreground_shared_SMC_added=False,scope='Private candidate, not yet runtime-qualified.'),indent=2))
