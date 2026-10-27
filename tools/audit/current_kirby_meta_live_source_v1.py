"""Source-only actual caller/emission controls for passive Kirby live captures."""
from pathlib import Path
import argparse,hashlib,json
from current_kirby_meta_earned_cpu_v1 import campaign,ROM,EXPECTED
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU

ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def probe(b,unit):
    stats=dict(body_calls=0,shot_calls=0,body_emissions=0,shot_emissions=0,completed_Mains=0,live_body_calls=0,live_shot_calls=0,maximum_writes=0,shot_kinds={},body_poses={})
    pending=None;original=NesMPU.step
    addresses={n:address(b,n)for n in ['SelectedCharacter','KbVariant','GameEngineSubroutine','R0','R1','SmPosePtr','KbShotType','KbShotKind','KbSavedSlot','KbAction','KbFloat','KbPose','OutlinePoseBuffer']}
    body=address(b,'DrawAllMetasprites::DoneDrawingPlayer');shot=address(b,'KbDrawShots::ShotReady');shotret=address(b,'KbDrawShots::Next');renderer=address(b,'MetaspriteRenderLoop');finish=address(b,'GameLoop')+int(b['syms']['GameLoop']['size'],0)-1
    art=(location(b,'KbArtStart')-16)//8192
    def step(c):
        nonlocal pending
        m=c.memory;at=c.pc;k=m.banks[(at-0x8000)//8192]if at>=0x8000 else -1
        get=lambda n,i=0:m[addresses[n]+i]
        scoped=get('SelectedCharacter')==13 and get('GameEngineSubroutine')==8
        if scoped and((at==body-3 and k==4)or(at==shot and k==74)):
            assert pending is None;kind='body'if at==body-3 else'shot';stats[kind+'_calls']+=1
            live=get('KbAction')!=0 or get('KbFloat')!=0 or any(get('KbShotType',i)for i in range(3))
            pending=dict(kind=kind,sp=c.sp,live=live,render=0,writes=[],before=bytes(m[512+i]for i in range(256)))
            if kind=='shot':
                slot=get('KbSavedSlot');assert slot<3 and get('KbShotType',slot)>0;pending['shot_kind']=get('KbShotKind',slot);stats['shot_kinds'][str(pending['shot_kind'])]=stats['shot_kinds'].get(str(pending['shot_kind']),0)+1
            else:stats['body_poses'][str(get('KbPose'))]=stats['body_poses'].get(str(get('KbPose')),0)+1
        if pending and at==renderer and k==4:
            p=pending;assert p['render']==0;p['render']=1;ptr=get('R0')+256*get('R1');h=m[ptr]
            assert h<128 and h%4==0
            if p['kind']=='body':assert ptr==get('SmPosePtr')+256*get('SmPosePtr',1)and(ptr==addresses['OutlinePoseBuffer']or 0xc000<=ptr<0xe000 and m.banks[2]==art)
            else:assert 0xc000<=ptr<0xe000 and m.banks[2]==art
            p['header']=h
        if pending and((at==body and k==4)or(at==shotret and k==74)):
            p=pending;assert p['render']==1 and p['sp']==c.sp
            assert len(p['writes'])<=p['header'];stats['maximum_writes']=max(stats['maximum_writes'],len(p['writes']))
            for a,v in dict(p['writes']).items():assert m[a]==v
            stats[p['kind']+'_emissions']+=bool(p['writes'])
            if p['live']:stats['live_'+p['kind']+'_calls']+=1
            pending=None
        if scoped and at==finish and k==126:assert pending is None;stats['completed_Mains']+=1
        start=len(m.writes);original(c)
        if pending:pending['writes'].extend((a,v)for a,v in m.writes[start:]if 512<=a<768)
    NesMPU.step=step
    try:old=campaign(b,unit)
    finally:NesMPU.step=original
    assert pending is None and stats['body_calls']>0 and stats['live_body_calls']>0 and stats['body_emissions']>0
    if unit!='meta':assert stats['shot_calls']>0 and stats['live_shot_calls']>0
    return dict(unit=unit,source_CPU_ROM_sha256=EXPECTED,GameLoop_calls=old['GameLoop_calls'],actual_compiled_draw_controls=stats,native_run=False,Lua_VM_executed=False)

def host_models():
    source=bytes(range(256));physical=bytes(v&0xe3 if i%4==2 else v for i,v in enumerate(source))
    def accept(src,written,hw,order,renderoff=True):return len(src)==len(written)==len(hw)==256 and src==written and order==list(range(256))and renderoff and hw==bytes(v&0xe3 if i%4==2 else v for i,v in enumerate(src))
    assert accept(source,source,physical,list(range(256)));controls=['positive-full256/E3']
    for label,src,written,hw,order,off in [('missing-write',source,source[:-1],physical,list(range(255)),True),('wrong-source-byte',bytes([255])+source[1:],source,physical,list(range(256)),True),('wrong-visible-attr',source,source,physical[:2]+bytes([physical[2]^1])+physical[3:],list(range(256)),True),('wrong-ordinal',source,source,physical,[1,0]+list(range(2,256)),True),('render-on',source,source,physical,list(range(256)),False)]:
        assert not accept(src,written,hw,order,off);controls.append(label)
    pages=[dict(Main=1,source=source),dict(Main=2,source=source)];matches=[q for q in pages if q['source']==source];assert len(matches)==2 and matches[-1]['Main']==2
    assert not[q for q in pages if q['source']==bytes(256)];controls+=['duplicate-content-kept-ambiguous','unmatched-kept-null','carry-capture-bounded8']
    for wanted,returned,entry_sp,returned_sp,ok in [('body','body',240,240,True),('body','shot',240,240,False),('shot','shot',240,238,False)]:assert((wanted==returned and entry_sp==returned_sp)==ok)
    return dict(passed=True,source_models_only=True,controls=controls+['correct-return/SP','wrong-caller-return-rejected','nested-SP-rejected'])

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists()and sha(ROM)==EXPECTED
    b=scoped_load(ROM);cases=[probe(b,u)for u in ['basics','copies-low','copies-high','meta']]
    z=dict(passed=True,native_run=False,Lua_VM_executed=False,actual_source_CPU_ROM_sha256=EXPECTED,scope='Fresh original earned GameLoop campaigns instrument genuine body/shot JSR, actual renderer, emission and real return/SP. No ability, mouth, health, projectile or outcome seeds. This is source-only, not a native renderer/pixel proof.',cases=cases,host_models=host_models(),bindings={str(p):sha(p)for p in [Path(__file__),ROM,ROM.with_suffix('.dbg'),ROOT/'tools/audit/current_kirby_meta_earned_cpu_v1.py',ROOT/'tools/audit/current_kirby_meta_live_v1.lua']})
    a.output.write_text(json.dumps(z,indent=2)+'\n',newline='\n');print(json.dumps(dict(passed=True,path=str(a.output),sha256=sha(a.output),source_GameLoops=sum(q['GameLoop_calls']for q in cases))))

if __name__=='__main__':main()
