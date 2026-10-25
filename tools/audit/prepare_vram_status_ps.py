"""Stage the first-writer VRAM fix on the combined contact/pause candidate."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
PARENT=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-zelda-pause-pq/candidate-v11')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    assert sha(PARENT/'candidate.nes')=='842e0a6a7be05a0886d1b1053b7ff2ac8cfb69aba5e0fe4b2d031e029b991664'
    a.output.mkdir(parents=True,exist_ok=False);s=a.output/'source';shutil.copytree(PARENT/'source',s)
    changes={}
    def edit(name,old,new):
        path=s/name;v=path.read_text();assert v.count(old)==1,(name,v.count(old),old[:100])
        changes.setdefault(name,dict(before=sha(path)));path.write_text(v.replace(old,new));changes[name]['after']=sha(path)
    edit('src/bill_native_rare.s','BillNativeReturnSelector: .res 1','''BillNativeReturnSelector: .res 1
.if ::ENABLE_MMC5_EXPANDED
; SRAM is fully assigned through$7fff. Use the two unassigned global
; ExRAM bytes immediately after the existing expanded bounce state.
NativeStatusPending=$5ff6
NativeStatusCursor=$5ff7
.endif''')
    # Preserve the existing five-byte printer site. Reject before its first
    # header write; the slot remains on the original stack until this branch.
    for name,facade in [('src/bill_native_rare.s','BillNativeStatusReserve'),('src/hud_tail.s','HudNativeStatusReserve')]:
        edit(name,'    ldx VRAM_Buffer1_Offset  ;get current buffer pointer\n    lda #$20                 ;put at top of screen by default',
            f''' .if ::ENABLE_MMC5_EXPANDED
    jsr {facade}
    bcs RejectedNumbers
 .else
    ldx VRAM_Buffer1_Offset  ;get current buffer pointer
    lda #$20                 ;put at top of screen by default
 .endif''')
        edit(name,'ExitOutputN:\n  rts','''ExitOutputN:
  rts
.if ::ENABLE_MMC5_EXPANDED
RejectedNumbers:
  pla
  rts
.endif''')
        # This same-bank facade translates the explicit A result to carry;
        # the mapper's farcall does not promise carry survives publication.
        extra=f'''
.if ::ENABLE_MMC5_EXPANDED
.proc {facade}
  farcall X5NativeStatusReserve
  beq Full
  ldx VRAM_Buffer1_Offset
  lda #$20
  clc
  rts
Full:sec
  rts
.endproc
.endif
'''
        if name.endswith('bill_native_rare.s'):
            edit(name,'BillNativeRareEnd:',extra+'\nBillNativeRareEnd:')
        else:
            # Append in the same bank's tail, outside the printer's scope.
            path=s/name;path.write_text(path.read_text()+'\n.pushseg\n.segment "HUD_TAIL_COLD"\n'+extra+'\n.popseg\n')
            changes[name]['after']=sha(path)
    # A rejected score has no score tail. Never apply leading-zero suppression
    # to a coin/world packet just because the last length happened to differ.
    edit('src/hud_tail.s','  ldy VRAM_Buffer1_Offset\n  lda VRAM_Buffer1-6,y',
        '''  ldy VRAM_Buffer1_Offset
.if ::ENABLE_MMC5_EXPANDED
  cpy #9
  bcc NoZSup
  lda VRAM_Buffer1-9,y
  cmp #$20
  bne NoZSup
  lda VRAM_Buffer1-8,y
  cmp #$62
  bne NoZSup
  lda VRAM_Buffer1-7,y
  cmp #6
  bne NoZSup
.endif
  lda VRAM_Buffer1-6,y''')
    edit('smb1base-mmc5-expanded.cfg','WORLD_SPRITE_PALETTE: load=PRGA_03, type=ro, optional=yes, start=$bf91;',
        'WORLD_SPRITE_PALETTE: load=PRGA_03, type=ro, optional=yes, start=$bfc9;')
    edit('src/x5_bounce.s','.proc X5OwnInventoryUi\n php\n pha\n phx',
        '''.proc X5OwnInventoryUi
 php
 pha
 phx
 phy
 jsr X5NativeStatusFlush
 ply''')
    path=s/'src/x5_bounce.s';path.write_text(path.read_text()+'\n'+(ROOT/'tools/audit/fixtures/vram_status_ps.s').read_text());changes['src/x5_bounce.s']['after']=sha(path)
    aliases='''Z2HudCacheValid=$5d96
Z2HudCacheHp=$5d97
Z2HudCacheMp=$5d98
Z2HudCacheExpLo=$5d99
Z2HudCacheExpHi=$5d9a
Z2HudCacheSpell=$5d9b
'''
    edit('src/zelda2_pause_panel.s','Z2PanelPending=$5d95\n','Z2PanelPending=$5d95\n'+aliases)
    edit('src/zelda2_link_menu.s',' sta Z2PanelPending\n rts',' sta Z2PanelPending\n sta Z2HudCacheValid\n rts')
    edit('src/zelda2_inventory_glue.s',' sta Z2PanelActive\n lda SavedJoypadBits',
        ' sta Z2PanelActive\n sta Z2PanelPending\n sta Z2HudCacheValid\n lda SavedJoypadBits')
    edit('src/zelda2_link_ui.s',' ldx VRAM_Buffer1_Offset\n cpx #$32 ;34B HUD + terminator must fit84B native queue\n jcs Done',
        ''' ; Native terrain and numeric packets have priority. Do not append a
 ; duplicate live pane while the area renderer owns the other queue.
 lda Z2HudCacheValid
 beq Changed
 lda Z2Hp
 cmp Z2HudCacheHp
 bne Changed
 lda Z2Mp
 cmp Z2HudCacheMp
 bne Changed
 lda Z2ExpLo
 cmp Z2HudCacheExpLo
 bne Changed
 lda Z2ExpHi
 cmp Z2HudCacheExpHi
 bne Changed
 lda Z2Selection
 and #7
 cmp Z2HudCacheSpell
 jeq Done
Changed:
 ldx VRAM_Buffer1_Offset
 jne Done
 lda Z2Hp
 sta Z2HudCacheHp
 lda Z2Mp
 sta Z2HudCacheMp
 lda Z2ExpLo
 sta Z2HudCacheExpLo
 lda Z2ExpHi
 sta Z2HudCacheExpHi
 lda Z2Selection
 and #7
 sta Z2HudCacheSpell
 lda #1
 sta Z2HudCacheValid''')
    cmd=[sys.executable,str(s/'tools/build_mmc5_expanded.py'),'--workspace',str(s),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/'candidate.nes')]
    z=subprocess.run(cmd,cwd=s,capture_output=True,text=True);(a.output/'build.log').write_text(z.stdout+z.stderr)
    report=dict(prepared=z.returncode==0,accepted=False,parent_ROM_sha256=sha(PARENT/'candidate.nes'),changes=changes)
    if z.returncode==0:report['ROM_sha256']=sha(a.output/'candidate.nes')
    (a.output/'preparation.json').write_text(json.dumps(report,indent=2)+'\n')
    assert z.returncode==0,(z.stdout+z.stderr)[-2500:]
    print(report['ROM_sha256'],flush=True)
if __name__=='__main__':main()
