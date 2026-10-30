"""Compose authentic Rogue with the existing Kamikaze and GB Pit backends."""
from pathlib import Path
import json
import re
import subprocess
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import prepare_rogue_current_menu_v1 as base

M=R/'build/full-roster-menu-v5'
O=R/'build/rogue-current-menu-v5'
EXTRA=[]


def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new)


def source(out):
    current=base.dependencies(M/'main.d')
    current_by_name={p.name:p for p in current if p.suffix in ['.s','.inc']}
    original=base.dependencies(base.P/'assembler-full.dep')
    rogue_by_name={p.name:p for p in original if p.suffix in ['.s','.inc']}
    # These current changes are all authored against the exact original
    # files consumed by Rogue; no conflicting Rogue change is discarded.
    names=['expanded.s','mmc5_expanded.s','samus.s','x5_menu_ui.s']
    for name in names:
        assert rogue_by_name[name].read_bytes()==(R/'src'/name).read_bytes(),name
        (out/'src'/name).write_bytes(current_by_name[name].read_bytes())
    old=(R/'src/new_roster_dispatch.s').read_text()
    cur=current_by_name['new_roster_dispatch.s'].read_text()
    start=old.index(' lda MarioVariant\n beq NrToLuigi',old.index('.proc NrMenuToggle'))
    end=old.index('NrMarioPublish:sta MarioVariant',start)
    new_start=cur.index(' jsr KmNextVariant',cur.index('.proc NrMenuToggle'))
    new_end=cur.index('NrMarioPublish:sta MarioVariant',new_start)
    dispatch=once(rogue_by_name['new_roster_dispatch.s'].read_text(),old[start:end],cur[new_start:new_end])
    base.put(out/'src/new_roster_dispatch.s',dispatch)
    # Real 3-way merge: current skin selector and Rogue's actual flagpole
    # collision fix touch separate source hunks in PlayerGfxHandler/controls.
    merged=subprocess.run(['git','merge-file','-p',str(current_by_name['player.s']),
        str(R/'src/player.s'),str(rogue_by_name['player.s'])],cwd=R,capture_output=True,text=True)
    assert merged.returncode==0,merged.stdout[-5000:]+merged.stderr
    base.put(out/'src/player.s',merged.stdout)
    menu=(out/'src/character_select.s').read_text()
    menu=once(menu,'  farcall NrMenuNavigate\n  cmp #$ff',
        '  jsr GbPitMenuNavigate\n  jmp GbPitNavContinue\n  .res 12,$ea\nGbPitNavContinue:\n  cmp #$ff')
    menu=once(menu,'  farcall RdUiName,jmp\n','  jmp GbPitQueueName\n  .res 15,$ea\n')
    base.put(out/'src/character_select.s',menu)
    # Name ownership chain: GB Pit -> Kamikaze -> Rogue -> original roster.
    # Kamikaze's exact foreign branch owns sufficient source-authored tail.
    kama=(R/'src/kamikaze_mario.s').read_text()
    kama=once(kama,' jmp NrQueueSelectName\nName:',
        ' farcall RdUiName,jmp\nName:')
    base.put(out/'src/kamikaze_mario.s',kama)
    current_entry=(M/'entrypoint.s').read_text()
    at=current_entry.index('.if ::ENABLE_MMC5_EXPANDED\n.import GbPitPose')
    end=current_entry.index('\n.include "full_roster_menu.s"',at)
    declarations=current_entry[at:end]
    entry=(out/'entrypoint.s').read_text()
    entry=once(entry,'\n.include "full_roster_menu.s"',
        '\n.include "kamikaze_mario.s"\n.import KmGraphics,KmPortrait\n'+declarations+
        '\n.include "full_roster_menu.s"')
    entry+='\n.export KmNativeGraphics := PlayerGfxHandler::KmNativeGraphics\n'
    render=(R/'src/kamikaze_mario_render_v2.inc').read_text()
    render=once(render,'farcall PlayerGfxHandler::KmNativeGraphics','farcall KmNativeGraphics')
    base.put(out/'src/kamikaze-render-body.inc',render)
    extern=['MarioVariant','CmHostGraphics','ObjectMetasprite','SmChrBank','PlayerChrBank',
        'CurrentCHRBank','PlayerFacingDir','SmPosePtr','X5ChrMode','X5WideChrActive','ReloadCHRBank',
        'METASPRITE_SAMUS_BODY','CurrentBankC','SelectedCharacter','HpPrepareNativePointers',
        'DrawMetasprite','CmHostPortraitRender','SafecallA_SMC','FarcallJmpTarget_SMC','FarCallCommon',
        'MMC5_PRG_ROM','MMC5_PRG_BANK_C']
    b=base.scoped_load(M/'candidate.nes')
    prefix='.macpack longbranch\n.feature force_range\n.include "inc/common.inc"\n'
    prefix+=''.join(('.importzp 'if b['syms'][n].get('addrsize')=='zeropage'else'.import ')+n+'\n'for n in extern)
    prefix+='.import KmNativeGraphics\n.export KmGraphics,KmPortrait\n'
    entry+=''.join(('.exportzp 'if b['syms'][n].get('addrsize')=='zeropage'else'.export ')+n+'\n'for n in extern)
    banking=(R/'src/mmc5.s').read_text()
    for name in ['BankPRGC','_BANK_INNER']:
        start=banking.index('.macro '+name+' ');end=banking.index('.endmacro',start)+len('.endmacro')
        prefix+=banking[start:end]+'\n'
    prefix+='''.macro farcall Target,Mode
 sta SafecallA_SMC+1
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(Target)|$80)
 .if .xmatch({Mode},{jmp})
 jmp FarCallCommon
 .else
 jsr FarCallCommon
 .endif
.endmacro
.include "kamikaze-render-body.inc"
'''
    base.put(out/'kama-render.s',prefix)
    base.put(out/'entrypoint.s',entry)
    cfg=(out/'full-menu.cfg').read_text()
    if 'FULL_ROSTER_PREVIEW_CHR:'not in cfg:
        cfg=once(cfg,'    ROGUE_DAWN_CHR: load=ROGUE_DAWN_CHR_MEM,type=ro,optional=yes;',
            '    FULL_ROSTER_PREVIEW_CHR:load=LM_UNUSED_CHR_MEM,type=ro,start=$af000;\n'
            '    ROGUE_DAWN_CHR: load=ROGUE_DAWN_CHR_MEM,type=ro,optional=yes;')
    for line in (M/'full-menu.cfg').read_text().splitlines():
        if line.strip().startswith(('KAMIKAZE_CHR:','KAMIKAZE_NMI:','KAMIKAZE_CORE:',
                                   'GB_PIT_MENU:','GB_PIT_RENDER:','GB_PIT_CHR:')):
            assert line.strip().split(':',1)[0]+':'not in cfg
            # ld65 processes segments for a memory region in declaration
            # order. Insert before later explicit addresses in that region,
            # keeping every existing automatic allocation in its old order.
            memory=re.search(r'load\s*=\s*([^,;]+)',line)[1]
            target=int(re.search(r'start\s*=\s*\$([0-9a-f]+)',line,re.I)[1],16)
            lines=cfg.splitlines(True);position=None
            for i,existing in enumerate(lines):
                load=re.search(r'load\s*=\s*([^,;]+)',existing)
                start=re.search(r'start\s*=\s*\$([0-9a-f]+)',existing,re.I)
                if load and load[1]==memory and start and int(start[1],16)>target:
                    position=i;break
            if position is None:
                position=next(i for i,x in enumerate(lines)if x.startswith('SYMBOLS'))-1
            lines.insert(position,line+'\n');cfg=''.join(lines)
    base.put(out/'full-menu.cfg',cfg)
    extra=EXTRA
    extra.extend([Path(__file__).resolve(),M/'build-proof.json',M/'skin.o',M/'gb.o',out/'kama-render.s',
                  R/'src/kamikaze_mario_render_v2.inc',out/'src/kamikaze-render-body.inc'])
    for name in ['skin.d','gb.d']:
        extra.append(M/name);extra+=base.dependencies(M/name)
    extra+=list(current_by_name[n]for n in names+['new_roster_dispatch.s','player.s'])
    extra+=[M/'entrypoint.s',M/'full-menu.cfg']
    base.put(out/'backend-composition.json',json.dumps(dict(
        source_only=True,shared_installation=False,
        origins=dict(rogue=base.sha(base.P/'candidate.nes'),current=base.sha(M/'candidate.nes')),
        source_changes=names+['new_roster_dispatch.s','player.s','character_select.s','kamikaze_mario.s'],
        player_clean_three_way=True,name_dispatch=['GB Pit','Kamikaze','Rogue','native'],
        required_remaining=['all80 menu and launch gates','actual Rogue route and native IRQ/NMI',
                            'Kamikaze and GB Pit preserved gameplay/CHR/palette checks']),indent=2)+'\n')
    return extra


def link(cmd,out):
    definitions=[]
    for i,v in enumerate(cmd):
        if v=='--asm-define':definitions+=['-D',cmd[i+1]]
    command=[str(R/'tools/Windows/cc65/bin/ca65.exe'),'--cpu','6502x','-g','-I',str(out/'src'),
        '-I',str(R/'src'),'-I',str(R),*definitions,'--create-full-dep',str(out/'kama-render.dep'),
        '-o',str(out/'kama-render.o'),str(out/'kama-render.s')]
    result=subprocess.run(command,cwd=R,capture_output=True,text=True)
    base.put(out/'kama-render-build.json',json.dumps(dict(command=command,returncode=result.returncode,
        stdout=result.stdout,stderr=result.stderr),indent=2)+'\n')
    assert result.returncode==0,result.stderr[-5000:]
    EXTRA.extend(base.dependencies(out/'kama-render.dep'))
    EXTRA.extend([out/'kama-render-build.json',out/'kama-render.dep'])
    cmd.extend([str(M/'skin.o'),str(M/'gb.o'),str(out/'kama-render.o')])


if __name__=='__main__':
    assert base.sha(M/'candidate.nes')=='5b09a3ed02aa678fb1d6fca57d905224e95c7b8f0f4e12f13901bf3f41f12d1e'
    base.main(output=O,source_hook=source,link_hook=link,
              extra_dependencies=[Path(__file__).resolve(),O/'backend-composition.json'])
