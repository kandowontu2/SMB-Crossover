"""Source-link the verified Rogue engine into the current32-slot front end."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

R=Path(__file__).resolve().parents[2]
P=R/'build/rogue-dawn-victory-pose-v4'
O=R/'build/rogue-current-menu-v2'
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import build_full_roster_menu_v1 as menu
from prepare_rogue_dawn_host_body_handoff_v1 import dependencies
from prepare_cv3_dmc_mirror import prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,newline='\n')


def main(*,output=None,source_hook=None,link_hook=None,extra_dependencies=()):
    global O
    if output is not None:O=Path(output)
    assert not O.exists() or '--resume' in sys.argv
    assert not (O/'build-proof.json').exists(), 'Preserve qualified preparation'
    assert sha(P/'candidate.nes')=='ba3033e17e12705ffa141d0908a01188e17779df717a6843fd12c638f1b0f5dc'
    handoff=json.loads((P/'handoff.json').read_text())
    bindings={b['path']:b['sha256']for b in handoff['bindings']}
    for path,h in bindings.items():assert sha(path)==h,path
    O.mkdir(parents=True,exist_ok='--resume' in sys.argv);(O/'src').mkdir(exist_ok=True)
    if '--resume'in sys.argv:
        negative=O/'negative-previous-source'
        i=1
        while negative.exists():
            i+=1;negative=O/f'negative-previous-source-{i}'
        negative.mkdir(exist_ok=False)
        for name in ['compile-log.json','entrypoint.s','private.cfg','frontend.s','kama-render-build.json']:
            if(O/name).exists():(negative/name).write_bytes((O/name).read_bytes())
        for p in (O/'src').iterdir():
            assert p.is_file()and p.resolve().is_relative_to(O.resolve())
            p.rename(negative/p.name)
        put(O/'negative-previous-source.json',json.dumps(dict(
            reason='Retain source/config from previous rejected preparation before rebuilding.',
            rejected_build_phase='See previous compile log.',
            existing_candidate_sha256=sha(O/'candidate.nes')),indent=2)+'\n')
    for n in ['main.c','entrypoint.s','private.cfg']:(O/n).write_bytes((P/n).read_bytes())
    cmd=json.loads((P/'build.json').read_text())['executed_commands'][-1]
    cmd=[v.replace(str(P),str(O))for v in cmd]
    idx=cmd.index('--asm-include-dir')
    cmd[idx:idx]=['--asm-include-dir',str(O/'src'),'--asm-include-dir',str(P)]
    commands=[]

    def build(label):
        proc=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        commands.append(dict(phase=label,command=cmd.copy(),returncode=proc.returncode,
                             stdout=proc.stdout,stderr=proc.stderr))
        put(O/'compile-log.json',json.dumps(commands,indent=2)+'\n')
        assert proc.returncode==0,proc.stderr[-12000:]
        prepare(R,O/'candidate.nes')

    build('exact_parent_reproduction')
    assert sha(O/'candidate.nes')==sha(P/'candidate.nes')
    original=dependencies(P/'assembler-full.dep')
    select=[p for p in original if p.name=='character_select.s'];assert len(select)==1
    # The existing front-end generator consumes its native host's source;
    # provide the actual Rogue host under its expected filenames.
    shim=O/'host-source'
    put(shim/'src/character_select.s',select[0].read_text())
    put(shim/'entrypoint.s',(P/'entrypoint.s').read_text())
    put(shim/'smb1base-mmc5-expanded.cfg',(P/'private.cfg').read_text())
    menu.BASE=shim
    pictures,facts,asset_bindings=menu.assets(O)
    layout=menu.pack(O,pictures)
    menu.source(O)
    hook_dependencies=source_hook(O)if source_hook else []
    source=(O/'src/full_roster_menu.s').read_text()
    old=' lda #1\n sec\n rts\nNotRogue:'
    assert source.count(old)==1
    put(O/'src/full_roster_menu.s',source.replace(old,
        ' lda #1\n clc ; source/native-qualified Rogue backend now present\n rts\nNotRogue:'))
    cfg=(O/'full-menu.cfg').read_text()
    assert 'FULL_ROSTER_MENU:load=FULL_MENU_MEM' in cfg
    if 'FULL_ROSTER_PREVIEW_CHR:'not in cfg:
        # This branch predates Kamikaze's separate incbin. The preview still
        # has its own exact700..703 physical lease in the same memory region.
        assert 'LM_UNUSED_CHR_MEM: start=$ae000,size=$2000,'in cfg
        cfg=cfg.replace('    ROGUE_DAWN_CHR: load=ROGUE_DAWN_CHR_MEM,type=ro,optional=yes;',
            '    FULL_ROSTER_PREVIEW_CHR:load=LM_UNUSED_CHR_MEM,type=ro,start=$af000;\n'
            '    ROGUE_DAWN_CHR: load=ROGUE_DAWN_CHR_MEM,type=ro,optional=yes;')
    assert 'FULL_ROSTER_PREVIEW_CHR:'in cfg
    needle='PARODIUS_CHR_MEM: start=$d0000,size=$30000,type=ro,fill=yes,file=%O,fillval=$00;'
    assert cfg.count(needle)==1
    cfg=cfg.replace(needle,
        'PARODIUS_CHR_MEM: start=$d0000,size=$9000,type=ro,fill=yes,file=%O,fillval=$00;\n'
        '    RECLAIMED_PARODIUS_CHR_MEM: start=$d9000,size=$27000,type=ro,fill=yes,file=%O,fillval=$00;')
    put(O/'private.cfg',cfg)
    pn=R/'build/parodius-chr-compact-v1'
    ice=R/'build/ice-pose-aliases-v2'
    for p in [pn/'vic_viper.s',pn/'parodius.s',pn/'parodius_art.inc',pn/'parodius_death.s',
              ice/'ice_climbers.s',ice/'ice_climbers_art.inc']:
        (O/'src'/p.name).write_bytes(p.read_bytes());bindings[str(p)]=sha(p)
    # The authentic Rogue assembly already approaches ca65's per-object
    # segment limit. Compile the new UI and its preview graphics separately;
    # all call/data operands are genuine imported source symbols.
    original_bundle=scoped_load(P/'candidate.nes')
    fm=(O/'src/full_roster_menu.s').read_text()
    code=re.sub(r'"[^"\n]*"','',re.sub(r';[^\n]*','',fm))
    tokens=set(re.findall(r'\b[A-Za-z_][A-Za-z_0-9]*\b',code))
    defined=set(re.findall(r'(?m)^\s*(?:\.proc\s+)?([A-Za-z_][A-Za-z_0-9]*)\s*(?=:|=)',code))
    defined.update(re.findall(r'\.proc\s+([A-Za-z_][A-Za-z_0-9]*)',code))
    extern={n:s for n,s in original_bundle['syms'].items()
            if n in tokens and n not in defined and '::'not in n and not n.startswith('Fm')
            and n not in {'ENABLE_MMC5_EXPANDED','MAPPER_MMC5'}}
    extern.update({n:original_bundle['syms'][n]for n in
        ['SafecallA_SMC','FarcallJmpTarget_SMC','FarCallCommon']})
    exports=['FmPending','FmResolve','FmToggle','FmQueueName','FmNativePrepare','FmDrawPreview','FmAlts','FmGroups']
    entry=(O/'entrypoint.s').read_text()
    inline='\n.include "full_roster_menu.s"\n.pushseg\n.segment "FULL_ROSTER_PREVIEW_CHR"\n'
    inline+='.incbin "'+(O/'pending-previews.chr').as_posix()+'"\n.popseg\n'
    assert entry.count(inline)==1
    # Keep genuine later export/alias declarations from backend composition.
    entry=entry.replace(inline,'\n')+'\n'+''.join('.import '+n+'\n'for n in exports)
    entry+=''.join(('.exportzp 'if s.get('addrsize')=='zeropage'else'.export ')+n+'\n'
                   for n,s in sorted(extern.items()))
    put(O/'entrypoint.s',entry)
    prefix='.macpack longbranch\n.feature force_range\n.include "inc/charmap.inc"\n'
    prefix+=''.join(('.importzp 'if s.get('addrsize')=='zeropage'else'.import ')+n+'\n'
                    for n,s in sorted(extern.items()))
    prefix+=''.join('.export '+n+'\n'for n in exports)
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
.include "full_roster_menu.s"
.segment "FULL_ROSTER_PREVIEW_CHR"
'''
    prefix+='.incbin "'+(O/'pending-previews.chr').as_posix()+'"\n'
    put(O/'frontend.s',prefix)
    ca=R/'tools/Windows/cc65/bin/ca65.exe'
    definitions=[]
    for i,v in enumerate(cmd):
        if v=='--asm-define':definitions+=['-D',cmd[i+1]]
    external_cmd=[str(ca),'--cpu','6502x','-g','-I',str(O/'src'),'-I',str(R),
        *definitions,'--create-full-dep',str(O/'frontend.dep'),'-o',str(O/'frontend.o'),str(O/'frontend.s')]
    proc=subprocess.run(external_cmd,cwd=R,capture_output=True,text=True)
    commands.append(dict(phase='external_frontend',command=external_cmd,returncode=proc.returncode,
                         stdout=proc.stdout,stderr=proc.stderr))
    put(O/'compile-log.json',json.dumps(commands,indent=2)+'\n')
    assert proc.returncode==0,proc.stderr[-12000:]
    cmd.append(str(O/'frontend.o'))
    if link_hook:link_hook(cmd,O)
    build('current_frontend_Rogue_and_lossless_data_layouts')
    b=scoped_load(O/'candidate.nes')
    oldbundle=scoped_load(P/'candidate.nes')
    assert address(b,'IcArtEnd')==0xc58f
    for n in ['RdNonSolidBGEnd','RdVictoryPublishChr','RdDeathRecordA','RdDeathRecordEnd']:
        assert address(b,n)==address(oldbundle,n),n
    newdeps=dependencies(O/'assembler-full.dep')+dependencies(O/'frontend.dep')+hook_dependencies+list(extra_dependencies)
    for name in ['character_select.s','full_roster_menu.s','parodius_art.inc','ice_climbers_art.inc']:
        assert O/'src'/name in newdeps,('Unselected override',name)
    bindings.update(asset_bindings)
    for p in newdeps:bindings[str(p)]=sha(p)
    for p in [Path(__file__).resolve(),R/'tools/audit/build_full_roster_menu_v1.py',
              O/'entrypoint.s',O/'frontend.s',O/'private.cfg',O/'menu.nam',O/'menu.rle',O/'packed.chr',
              O/'pending-previews.chr',P/'handoff.json']:
        bindings[str(p)]=sha(p)
    report=dict(status='PRIVATE_CURRENT_MENU_WITH_AUTHENTIC_ROGUE_BACKEND_CONTROLS_PENDING',
        ROM_sha256=sha(O/'candidate.nes'),verified_backend_parent_sha256=sha(P/'candidate.nes'),
        exact_parent_reproduction=True,slots=32,profiles=80,expected_ready=48,expected_pending=32,
        admission='Private frontend only: Rogue raw2/variant1 enabled. Expected ready count describes flags, not backend parity; this branch must not be installed.',
        existing_backend_parity_unproven=[n for n in ['GbPitPose','KmNmiSlot0','KmBodyDraw']if n not in b['syms']],
        preserved='Complete verified Rogue native movement/abilities/items/audio/flagpole/victory source; current32-slot menu; densePN and page-safeIce data layouts.',
        frontend=layout,preview_sources=facts,commands=commands,source_bindings=bindings,
        native_run=False,shared_installation=False,
        limits=['Existing47-profile backend parity requires controls; restored symbols alone do not qualify gameplay.',
                'Actual current-menu all80 profile controls and Rogue route replay pending',
                'Later source composition with four-host/Quick/Arthur branches remains required'])
    put(O/'build-proof.json',json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k]for k in ['ROM_sha256','exact_parent_reproduction','expected_ready']}))


if __name__=='__main__':main()
