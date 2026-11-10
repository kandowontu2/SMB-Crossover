"""Reach the final no-manual floor guard and the actual generic sine decoder."""
import argparse
from hashlib import sha256
import inspect
import json
from pathlib import Path

import check_manual_floor_scope_1110 as F
import check_generic_helper_camera_1110 as G

W,P,N,R=F.W,F.P,F.N,F.R
OUT=F.OUT
FLOOR=OUT/'floor-proof.json'


def sha(path):return sha256(path.read_bytes()).hexdigest()


def image():
    q=json.loads(FLOOR.read_text())
    for path,digest in q['bindings'].items():assert sha(R/path)==digest,path
    raw=W.BASE.read_bytes();assert W.sha(raw)==q['parent_SHA256']
    trial=P.install(raw,q['patches']);assert W.sha(trial)==q['expected_memory_only_SHA256']
    return P.bundles(raw,trial)[1],q


def floor_seed(bundle,owner,case):
    m=P.scene(bundle,owner)
    x=560 if case=='authored-inside' else 1583
    if case=='authored-inside':
        for right in (553,681,857):
            P.L.spawn(m,right)
        assert m.ram[2][0x30c]==7
    camera=max(0,x-112)
    N.put(m,Player_X_Position=x&255,Player_PageLoc=x>>8,
          Player_Y_Position=160 if case=='authored-inside' else 176,Player_Y_HighPos=1,
          ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8,
          ScreenRight_X_Pos=(camera+255)&255,ScreenRight_PageLoc=(camera+255)>>8)
    m.ram[2][0x30b]=3
    assert m.ram[2][0x30e]==m.ram[2][0x30f]==0
    if case=='manual-bypass':
        z=N.invoke(m,'ManualPlatform',x=0x42,y=20)
        assert z['X'] in range(1,7)
        m.ram[2][0x30f]=z['X']
    return m


def generic_seed(bundle,owner,advances=0):
    # Actual authored original-six accommodation,8-1 record28. This reaches
    # the same shared decoder with ordinary native audio rather than WWF's
    # independently ticking legacy sound capsule.
    m=P.scene(bundle,0)
    N.put(m,SelectedCharacter=0,FmGroups=0,WorldNumber=7,LevelNumber=0,AreaPointer=48,
          CrossoverBehaviorVersion=0,GameEngineSubroutine=8,TimerControl=0)
    N.invoke(m,'GetAreaDataAddrs')
    m.raw_page(1,154);N.put(m,CurrentBank=154)
    G.direct(m,G.LOAD)
    assert m[0x7387]==1
    center=m[P.L.M.address(bundle,'HpXLo')]+256*m[P.L.M.address(bundle,'HpXHi')]
    left=center-4*m[P.L.M.address(bundle,'HpWidth')]
    assert G.scan(m,left-271)==1
    G.scan(m,left-112)
    player=left-30
    N.put(m,Player_X_Position=player&255,Player_PageLoc=player>>8,Player_Y_Position=176,
          Player_Y_HighPos=1,Player_Pos_ForScroll=82,Player_Rel_XPos=82)
    slot=m[P.L.M.address(bundle,'HpActorSlot')]-1
    assert slot in range(6)
    N.put(m,ObjectOffset=slot)
    for _ in range(advances):G.direct(m,0xae40,x=slot)
    N.consume(m)
    N.put(m,NmiDisable=255,FamilyMainCommit=1)
    return m


def qualify(bundle,labels,case,table_pc):
    generic=case.startswith('generic-sine')
    source=inspect.getsource(P.vectors).replace('def vectors(','def check(',1)
    source=source.replace('for owner in (41,34)','for owner in (0,)' if generic else 'for owner in (41,)')
    source=source.replace("for scenario in ('birth','full','replacement'):",f'for scenario in ({case!r},):')
    source=source.replace('SavedJoypadBits=0x28, SavedJoypad1Bits=0x28','SavedJoypadBits=0, SavedJoypad1Bits=0')
    old="assert bool(owned(m)) == (scenario != 'full') and final(c) == target"
    assert source.count(old)==1
    source=source.replace(old,'assert final(c) == target')
    if generic:
        hot=f'tag == 154 and {table_pc} <= pc < {table_pc+256}'
    else:
        hot=f'tag == 3 and {labels["MiniPlatformFloor"]} <= pc < {labels["MiniHostGraphics"]}'
    source=source.replace('if not inside or key in seen:',f'if not (inside or {hot}) or key in seen:')
    source=source.replace('m.vector_floor,m.written_stack = 0x100+z.sp,set()',
        'm.vector_floor,m.written_stack = 0x100+z.sp,set()\n        m.hp_irq_probe = True')
    source=source.replace('m.vector_floor = None\n        after = live(z)',
        'm.vector_floor = None\n        m.hp_irq_probe = False\n        after = live(z)')
    env=dict(P.__dict__)
    class HelperGuard(P.StackGuard):
        hp_irq_probe=False
        def __getitem__(self,at):
            if self.hp_irq_probe and isinstance(at,int):
                assert at not in (0x73d7,0x73d9),('ISR reads helper decoder state',hex(at))
            return super().__getitem__(at)
    env['StackGuard']=HelperGuard
    def snapshot(c,fn):
        prior=c.memory.hp_irq_probe;c.memory.hp_irq_probe=False
        try:return (*fn(c),bytes(c.memory[0x7382:0x73dd]))
        finally:c.memory.hp_irq_probe=prior
    env['live']=lambda c:snapshot(c,P.live)
    env['final']=lambda c:snapshot(c,P.final)
    if generic:
        source=source.replace("assert after == before, (kind, owner, entry)",
            "assert after == before, (kind, owner, entry, diagnostic(before,after))")
        def diagnostic(a,b):
            out=[]
            for i,(x,y) in enumerate(zip(a,b)):
                if x==y:continue
                if i==8:
                    out.append((i,[(j,[(k,u,v)for k,(u,v)in enumerate(zip(r,s))if u!=v][:8])for j,(r,s)in enumerate(zip(x,y))if r!=s]))
                else:out.append((i,x if len(str(x))<150 else str(x)[:150],y if len(str(y))<150 else str(y)[:150]))
            return out
        env['diagnostic']=diagnostic
    env['scene']=(lambda b,o:generic_seed(b,o,int(case.rsplit('-',1)[-1]))) if generic else lambda b,o:floor_seed(b,o,case)
    exec(source,env)
    result=env['check'](bundle,labels)
    assert result['counts']['lag_FF']>0
    return result


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--probe',action='store_true');args=ap.parse_args()
    bundle,q=image();result={}
    for case in (('generic-sine-16',) if args.probe else
                 ('late-no-manual','authored-inside','manual-bypass','generic-sine-0','generic-sine-16','generic-sine-64','generic-sine-160')):
        result[case]=qualify(bundle,q['labels'],case,q['format']['table_pc'])
        print('Actual supplemental vectors',case,result[case],flush=True)
        if args.probe:break
    if not args.probe:
        receipt=dict(passed=True,expected_memory_only_SHA256=q['expected_memory_only_SHA256'],
            floor_proof_SHA256=sha(FLOOR),vectors=result,
            full_helper_SRAM_preserved=True,ISR_decoder_state_read_trap=[0x73d7,0x73d9],
            source_generic_fixture='Actual original-six8-1 record28, genuine constructor/manager, phases from0/16/64/160 real helper advances; native regular audio publication before hotFF.',
            bindings={Path(__file__).relative_to(R).as_posix():sha(Path(__file__))})
        (OUT/'supplement-irq.json').write_text(json.dumps(receipt,indent=2)+'\n')


if __name__=='__main__':main()
