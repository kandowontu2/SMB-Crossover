"""Bounded source/CPU audit and private Ryu primary/Jump Slash guard proposal.

No emulator, install, Git operation, or root source mutation. Exact active MMC5
baseline is retained; all build outputs live in the caller's external directory.
"""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/audit'))
from check_tmnt_render_oa import load, address, location
from robots_weapon_cpu_v1 import Arena
from verify_native_relocation import NesMPU

ACTIVE = 'f00c2a7ad0459a3cd0b369bb4fbc9f374dc27d9335b2cc1fe1867f3f98d73d23'
CV3 = Path("C:/NES/Castlevania III - Dracula's Curse (USA).nes")
CV3_SHA = '085ec6395681c7ebfda19c2986069c21a3d27738cc61ada76249de70a07ed7d3'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def primary(bundle, slash, selected, mode, state, wall, held=0x40, previous=0):
    q = Arena(bundle, char=10)
    q.put(CrossoverBehaviorVersion=mode, Player_State=state,
          AvSlash=slash, AvFlip=slash, XgWall=wall,
          SavedJoypadBits=held, RgPreviousButtons=previous)
    q.set('InvSelected', selected, 10)
    q.set('InvOwnedLo', 0xff, 10)
    q.set('InvAmmo', 40, 160)
    # Full real linked ExpandedWeapons; empty actor pools and no enemy or PPU
    # stubs. Inventory spending and the common farcall trampoline execute.
    c, seen = q.invoke('ExpandedWeapons')
    assert not seen
    return dict(attack=q.get('RgAttack'), kind=q.get('RgAttackKind'),
                slash=q.get('AvSlash'), flip=q.get('AvFlip'),
                ammo=q.get('InvAmmo',160), cycles=c.processorCycles,
                minimum_sp=q.m.low_sp if hasattr(q.m,'low_sp') else None)


def cv3_source_jump(bundle):
    """Source fixed-arc leaves and measured current Sypha accommodation."""
    assert sha(CV3) == CV3_SHA
    ref = ROOT/'build/player-guide-agent/cv3-private/reference/source/code/playerStateProcessing_b1c.s'
    assert sha(ref) == 'ee048f3dbe4d3e2b4ed7a4e71cf763d372ffd5cce97fbfaa76c82fed549e6392'
    raw = CV3.read_bytes()
    authenticated = 0
    for m in re.finditer(r'^B28_([0-9a-f]{4}):.*;\s*((?:[0-9a-f]{2}\s*)+)$',ref.read_text(),re.M|re.I):
        offset = int(m[1],16)
        if 0x18bf <= offset < 0x190c:
            code = bytes.fromhex(m[2])
            assert raw[16+28*8192+offset:16+28*8192+offset+len(code)] == code
            authenticated += len(code)
    fixed = []
    for phase,idx in itertools.product((0,1), range(1,30)):
        q = Arena(bundle,char=5)
        q.put(Cv3Variant=3,Cv3JumpPhase=phase,Cv3JumpIndex=idx,
              Cv3VyHi=255,Player_Y_Speed=255)
        q.invoke('Cv3JumpVelocity')
        m = bytearray(65536)
        for bank,at in ((28,0x8000),(29,0xa000),(31,0xe000)):
            m[at:at+8192]=raw[16+bank*8192:16+(bank+1)*8192]
        m[0x5d8],m[0x5c1],m[0x565]=idx,phase,8
        c=NesMPU(memory=m,pc=0x98bf);c.sp=0xfd;c.stPushWord(0x5aff)
        for _ in range(1000):
            if c.pc==0x5b00:break
            c.step()
        else:raise AssertionError(('CV3 source timeout',hex(c.pc)))
        got=tuple(q.get(n)for n in ('Cv3VyHi','Cv3JumpIndex','Cv3JumpPhase'))
        want=tuple(m[n]for n in (0x520,0x5d8,0x5c1))
        assert got==want,(phase,idx,got,want)
        fixed.append(dict(phase=phase,index=idx,velocity=got[0]))
    q=Arena(bundle,char=5)
    q.put(Cv3Variant=2,Cv3JumpIndex=9,Cv3JumpPhase=0)
    trajectory=[];height=0
    for tick in range(52):
        q.set('Player_Y_Speed',q.get('Cv3VyHi'))
        q.invoke('Cv3SyphaArc')
        v=q.get('Cv3VyLo')+256*q.get('Cv3VyHi')
        if v>=32768:v-=65536
        height+=v
        trajectory.append(dict(tick=tick,velocity_q8=v,displacement_q8=height))
    return dict(authenticated_source_jump_instruction_bytes=authenticated,
                alucard_fixed_arc_leaf_cases=len(fixed),
                sypha_current_arc=dict(launch_q8=-1536,gravity_q8=64,
                    fall_cap_q8=1536,apex_pixels=-min(r['displacement_q8'] for r in trajectory)/256,
                    trajectory=trajectory),
                scope='Fixed-jump arithmetic against authenticated original CPU instructions; Sypha is the explicit previously adopted SMB traversal adaptation, not original CV3 table motion. Real integration/collisions/input timing are excluded.')


def build(out, overlay):
    rom=out/'candidate.nes'
    cmd=[sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),
         '--source-overlay',str(overlay),'--output',str(rom)]
    result=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
    (out/'build.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0,(out/'build.log').read_text()[-3000:]
    return rom


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    assert sha(a.rom)==ACTIVE
    old=load(a.rom)
    script=ROOT/'reference/crossover2/extracted/scripts/com/smbc/characters/Ryu.as'
    text=script.read_text()
    assert 'if(cState != ST_ATTACK && !this.jumpSlash)' in text
    rows=[]
    # A legal retained slash remains active while paused selection cycles. The
    # first four rows prove that transition using InventoryCycle itself.
    for selected in (1,2,3,4):
        q=Arena(old,char=10);q.put(AvSlash=1,GamePauseStatus=1,InvFresh=2)
        q.set('InvOwnedLo',1|(1<<5)|(1<<selected),10)
        q.set('InvSelected',5,10)
        q.invoke('InventoryCycle')
        assert q.get('InvSelected',10)==selected and q.get('AvSlash')==1
        result=primary(old,1,selected,1,1,0)
        assert result['attack']==14 and result['slash']==1
        rows.append(dict(selection=selected,result=result))
    (a.output/'baseline-failure.json').write_text(json.dumps(dict(
        passed=False,defect_reproduced=True,ROM_sha256=ACTIVE,
        source_Ryu_sha256=sha(script),source_rule='pressAtkBtn: cState != ST_ATTACK && !jumpSlash',
        cases=rows,scope='Real paused InventoryCycle preserves AvSlash; full assembled ExpandedWeapons then incorrectly starts14-update primary while airborne slash remains active.'),indent=2)+'\n')
    # Freeze all include inputs before building the proposal. No preparation
    # scripts regenerate art or change root files.
    stage=a.output/'source';stage.mkdir()
    shutil.copytree(ROOT/'src',stage/'src')
    for cfg in ('smb1base-mmc5-expanded.cfg',):shutil.copyfile(ROOT/cfg,stage/cfg)
    frozen={str(q.relative_to(stage)):sha(q) for q in stage.rglob('*') if q.is_file()}
    check=a.output/'baseline-rebuild';check.mkdir()
    baseline=build(check,stage)
    assert sha(baseline)==ACTIVE,'Frozen root inputs no longer reproduce assigned active baseline; do not propose against another candidate'
    f=stage/'src/expanded_weapons.s';s=f.read_text()
    needle='  lda XgWall\n  bne ExistingAttackDone\n  lda InvSelected+CHARACTER_RYU'
    assert s.count(needle)==1
    f.write_text(s.replace(needle,'  jsr RyuPrimaryBlocked\n  bne ExistingAttackDone\n  lda InvSelected+CHARACTER_RYU'))
    f=stage/'src/entrypoint.s'
    with f.open('a')as h:h.write('\n.if ::ENABLE_CROSSOVER\n.include "cv3_ryu_audit_sword_guard.s"\n.endif\n')
    (stage/'src/cv3_ryu_audit_sword_guard.s').write_text('''; Source2.02 Ryu.pressAtkBtn rejects primary while Jump Slash remains live.
; Appended after all EXPANDED_EX contributors; every old label remains fixed.
.pushseg
.segment "EXPANDED_EX"
.proc RyuPrimaryBlocked
  lda XgWall
  ora AvSlash
  rts
.endproc
.popseg
''')
    candidate=build(a.output,stage);new=load(candidate)
    before=old['raw'];after=new['raw']
    diffs=[i for i,(x,y)in enumerate(zip(before,after))if x!=y]
    # Same-size three-byte replacement plus the appended seven-byte leaf.
    assert len(before)==len(after)
    helper=location(new,'RyuPrimaryBlocked')
    oldseg=next(g for g in old['segs'].values()if g.get('name')=='"EXPANDED_EX"')
    assert helper==int(oldseg['ooffs'],0)+int(oldseg['size'],0)
    assert len([i for i in diffs if i<helper])<=3
    assert all(i<16+1024*1024 for i in diffs)
    assert before[:16]==after[:16] and before[16+1024*1024:]==after[16+1024*1024:]
    for name,row in old['syms'].items():
        if row.get('scope')=='1' and 'val'in row and 'seg'in row:
            assert address(new,name)==int(row['val'],0),name
    def labels(path):
        return {m[2]:m[1] for line in path.read_text().splitlines()if(m:=re.fullmatch(r'al (\w+) (.+)',line))}
    ol,nl=labels(a.rom.with_suffix('.lbl')),labels(candidate.with_suffix('.lbl'))
    assert all(nl.get(k)==v for k,v in ol.items())
    regressions=[];repaired=0
    for slash,selected,mode,state,wall in itertools.product((0,1),(0,1,2,3,4,5),(0,1),(0,1),(0,1)):
        x=primary(old,slash,selected,mode,state,wall)
        y=primary(new,slash,selected,mode,state,wall)
        # Grounded slash is deliberately included only as a no-new-primary
        # robustness boundary. Legal live Slash is airborne.
        expected=bool(slash and not wall and (selected!=5 or state==0))
        if expected:
            assert x['attack']==14 and y['attack']==0
            assert y['slash']==slash and y['ammo']==x['ammo']
            repaired+=1
        else:
            assert {k:v for k,v in x.items()if k!='cycles'}=={k:v for k,v in y.items()if k!='cycles'},(slash,selected,mode,state,wall,x,y)
        regressions.append(dict(slash=slash,selected=selected,mode=mode,state=state,wall=wall,
                                before=x,after=y,repaired=expected))
    changes={str(q.relative_to(stage)):dict(before_sha256=frozen.get(str(q.relative_to(stage))),after_sha256=sha(q))
             for q in stage.rglob('*')if q.is_file()and frozen.get(str(q.relative_to(stage)))!=sha(q)}
    motion=cv3_source_jump(old)
    (a.output/'motion-source-proof.json').write_text(json.dumps(motion,indent=2)+'\n')
    (a.output/'cases.json').write_text(json.dumps(regressions,indent=2)+'\n')
    proof=dict(passed=True,adopted=False,goal_complete=False,ROM_sha256=sha(candidate),
        baseline_ROM_sha256=ACTIVE,baseline_rebuild_exact=True,
        source_swf_sha256=sha(ROOT/'reference/crossover2/source.swf'),
        source_Ryu_sha256=sha(script),CV3_ROM_sha256=CV3_SHA,
        source_changes=changes,cases=len(regressions),repaired_boundary_cases=repaired,
        legal_airborne_repaired_cases=sum(r['repaired']and r['state']==1 for r in regressions),
        old_failure_retained=str(a.output/'baseline-failure.json'),
        changed_offsets=diffs,appended_leaf_bytes=7,
        all_preexisting_public_PC_RAM_CHR_header_exact=True,
        scope='Private MMC5 only. Full linked ExpandedWeapons and legal paused selection component execute with real farcalls; empty shot/enemy pools, no emulator/PPU/audio/interrupt/campaign proof. +16 CPU cycles and two transient stack bytes on a primary admission check; native stack/IRQ regression still required before adoption.')
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(proof,indent=2))


if __name__=='__main__':main()
