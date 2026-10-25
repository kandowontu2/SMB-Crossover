"""Stage a source-art Zelda II pause/upgrade pane on the contact repair."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys

ROOT=Path(__file__).resolve().parents[2]
BASE=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-contact-pp/candidate-v5')
OUT=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-zelda-pause-pq/candidate-v11')
ORIGINAL=Path('C:/NES/Zelda II - The Adventure of Link (USA).nes')

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tile(c):
    if c.isdigit():return 0xd0+int(c)
    if 'A'<=c<='Z':return 0xda+ord(c)-65
    return {' ':0xf4,'+':0xca,'-':0xcb,'|':0xcc,'>':0xfb}[c]

def main():
    OUT.mkdir(parents=True,exist_ok=False);s=OUT/'source';shutil.copytree(BASE/'source',s)
    changes={}
    def replace(n,old,new):
        p=s/n;v=p.read_text();assert v.count(old)==1,(n,v.count(old));before=sha(p)
        p.write_text(v.replace(old,new));changes[n]=dict(before=before,after=sha(p))
    # The original glyphs are the final1K of the original background bank1.
    raw=ORIGINAL.read_bytes();assert sha(ORIGINAL)=='9fca03064a5113e6a92f550d9f42bac9ac1ae248a84df1f653d7cd7f76a1803d'
    start=16+raw[4]*16384+7*1024
    font=s/'chr/characters/zelda2-pause-font.chr'
    data=bytearray(raw[start:start+1024])
    # Preserve every original white glyph pixel. Map the original transparent
    # backdrop to opaque black in palette1, preserving the world's sky color.
    for at in range(0,1024,16):
        for y in range(8):
            white=data[at+y]&~data[at+y+8]
            data[at+y]=255;data[at+y+8]=white^255
    font.write_bytes(data)
    ui=s/'src/zelda2_pause_panel.s';shutil.copyfile(ROOT/'tools/audit/fixtures/zelda2_pause_panel_pp.s',ui)
    stats=['+------------+','|            |','|NEXT |      |','+----+-------+',
        '|     >ATTACK|','| LEVEL    1 |','|     >MAGIC |','| LEVEL    1 |',
        '|     >LIFE  |','| LEVEL    1 |','+----+-------+','| UP | CANCEL|',
        '|A OK B BACK |','+------------+']
    # Cursor cells start blank; only the selected row receives source FB.
    stats=[r.replace('>',' ') for r in stats]
    spells=['+------------+','| MAGIC   MP |']
    for spell in ['SHIELD','JUMP','LIFE','FAIRY','FIRE','REFLECT','SPELL','THUNDER']:
        spells.append('| '+spell.ljust(7)+'    |')
    spells+=['|            |','|LR UPGRADES |','|A OK B BACK |','+------------+']
    assert len(stats)==len(spells)==14 and all(len(r)==14 for r in stats+spells),list(map(len,stats+spells))
    (s/'src/zelda2_pause_tables.inc').write_text('\n'.join(
        name+':\n'+'\n'.join(' .byte '+','.join('$%02x'%tile(c) for c in row) for row in rows)
        for name,rows in [('Z2PanelStats',stats),('Z2PanelSpells',spells)])+'\n')
    replace('src/entrypoint.s','.include "zelda2_link_ui.s"','.include "zelda2_link_ui.s"\n.include "zelda2_pause_panel.s"')
    replace('smb1base-mmc5-expanded.cfg','    VIC_CHR:load=VIC_CHR_MEM,type=ro;',
        '    VIC_CHR:load=VIC_CHR_MEM,type=ro;\n    Z2_UI_CHR:load=VIC_CHR_MEM,type=ro,start=$62c00;')
    replace('src/zelda2_link_menu.s',' sta Z2UiState\n rts',' sta Z2UiState\n sta Z2PanelActive\n rts')
    replace('src/zelda2_link_menu.s',' sta Z2PanelActive\n rts',' sta Z2PanelActive\n sta Z2PanelPending\n rts')
    replace('src/zelda2_inventory_glue.s',' jsr Z2AreaReset\n lda SavedJoypadBits',
        ' jsr Z2AreaReset\n lda #0\n sta Z2PanelActive\n lda SavedJoypadBits')
    replace('src/zelda2_link_ui.s',' jsr Z2EnsureInit\n lda SavedJoypad1Bits',
        ' jsr Z2EnsureInit\n jsr Z2PanelSync\n lda Z2PanelPending\n cmp #2\n jeq Done\n lda SavedJoypad1Bits')
    replace('src/zelda2_link_ui.s',' sta R4\n lda SavedJoypad1Bits',
        ' sta R4\n sta Z2PanelFresh\n lda SavedJoypad1Bits')
    replace('src/zelda2_link_ui.s',' jsr Z2ExpTick\n lda GamePauseStatus',
        ' jsr Z2ExpTick\n lda Z2PanelFresh\n sta R4\n lda GamePauseStatus')
    replace('src/zelda2_link_ui.s','ExpMenu:\n lda Z2Selection\n and #8\n bne Done\n ldx #2',
        'ExpMenu:\n ldx #2')
    replace('src/zelda2_link_ui.s','Check:\n stx R4\n txa\n jsr Z2Threshold',
        'Check:\n stx R4\n lda BitMasks,x\n and Z2DeferredMask\n bne NextCategory\n txa\n jsr Z2Threshold')
    replace('src/zelda2_link_ui.s',' ldx R4\n dex\n bpl Check',
        ' ldx R4\nNextCategory:\n dex\n bpl Check')
    replace('src/zelda2_link_ui.s',' jsr Z2LevelUp\n bcc Hud\n lda Z2Selection',
        ' jsr Z2LevelUp\n bcc Hud\n lda #0\n sta Z2DeferredMask\n lda Z2Selection')
    replace('src/zelda2_link_ui.s','Defer:\n lda Z2Selection\n ora #8\n sta Z2Selection',
        'Defer:\n jsr Z2Defer\n jcc Hud')
    replace('src/zelda2_link_ui.s',' lda #$80\n sta Z2UiState',' lda #$81\n sta Z2UiState')
    replace('src/zelda2_link_ui.s','MenuReady:\n lda R4','MenuReady:\n lda Z2PanelFresh\n and #B_Button\n jne Defer\n lda R4')
    replace('src/zelda2_link_ui.s','SpellReady:and #7\n sta R0',
        '''SpellReady:and #7
 sta R0
 tax
 lda BitMasks,x
 and Z2LearnedSpells
 bne Learned
 ; Bounded scan in the requested direction; never select a missing spell.
 ldx #8
FindSpell:
 dec R0
 lda Z2PanelFresh
 and #Up_Dir
 bne CheckSpell
 inc R0
 inc R0
CheckSpell:
 lda R0
 and #7
 sta R0
 tay
 lda BitMasks,y
 and Z2LearnedSpells
 bne Learned
 dex
 bne FindSpell
 jmp Hud
Learned:''')
    # Mask direction separately: A/Start plus Up must not become Down.
    p=s/'src/zelda2_link_ui.s';txt=p.read_text().replace(' ldy R4\n cpy #Up_Dir',' pha\n lda Z2PanelFresh\n and #Up_Dir\n tay\n pla\n cpy #Up_Dir')
    p.write_text(txt);changes['src/zelda2_link_ui.s']['after']=sha(p)
    replace('src/zelda2_link_ui.s',' beq Hud\n lda Z2Selection\n and #7',
        ' beq SpellConfirm\n lda Z2Selection\n and #7')
    replace('src/zelda2_link_ui.s',' jmp Hud\nStats:',
        ''' jmp Hud
SpellConfirm:
 lda Z2PanelFresh
 and #A_Button
 jeq Hud
 jmp Close
Stats:''')
    replace('src/zelda2_link_ui.s','.proc Z2Hud\n lda OperMode',
        '''.proc Z2Hud
 lda GamePauseStatus
 and #1
 jeq OrdinaryHud
 jmp Z2PanelTick
OrdinaryHud:
 jsr Z2PanelSync
 lda Z2PanelPending
 cmp #2
 bne HudReady
 rts
HudReady:
 lda OperMode''')
    # The old two-row paused HUD is superseded by the full pane. Keep its
    # live HP/MP/spell/EXP rows and decimal helpers; remove dead pause paths.
    p=s/'src/zelda2_link_ui.s';txt=p.read_text();at=txt.index('.proc Z2Hud\n')
    prefix,hud=txt[:at],txt[at:]
    hud=hud.replace(' lda Z2UiState\n bmi Paused\n','',1)
    first=hud.index('\nPaused:\n');last=hud.index('\nRow2:\n',first);hud=hud[:first]+hud[last:]
    hud=hud.replace(' lda Z2UiState\n bmi PauseRow2\n','',1)
    first=hud.index('\nPauseRow2:\n');last=hud.index('\nFinish:\n',first);hud=hud[:first]+hud[last:]
    p.write_text(prefix+hud);changes['src/zelda2_link_ui.s']['after']=sha(p)
    code=[sys.executable,str(s/'tools/build_mmc5_expanded.py'),'--workspace',str(s),
        '--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(OUT/'candidate.nes')]
    z=subprocess.run(code,cwd=s,capture_output=True,text=True);(OUT/'build.log').write_text(z.stdout+z.stderr)
    (OUT/'preparation.json').write_text(json.dumps(dict(prepared=z.returncode==0,accepted=False,
        parent_ROM_sha256=sha(BASE/'candidate.nes'),original_ROM_sha256=sha(ORIGINAL),
        font_source_offset=start,font_sha256=sha(font),changes=changes),indent=2)+'\n')
    assert z.returncode==0,(z.stdout+z.stderr)[-3000:]
    print(sha(OUT/'candidate.nes'))

if __name__=='__main__':main()
