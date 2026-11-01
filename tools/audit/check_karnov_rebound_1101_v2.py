"""Actual native bounce ingress must survive the next original actor updates."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import battletoads_current_loader_controls_v1 as L
import ff_wram_host_controls_v7 as H
import check_hogan_current_bounded_v1 as C
from check_tmnt_render_oa import address,location
O=R/'build/karnov-host-resource-base-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    result=dict(passed=False,source_CPU=True,native=False,installed=False)
    refs=[Path(__file__),R/'tools/reference/karnov_host_rebound_1101_v2.inc',O/'terrain-assembly.json',O/'candidate.nes',O/'candidate.dbg']
    try:
        stage=json.loads((O/'terrain-assembly.json').read_text())
        assert stage['passed'] and stage['rebound'] and stage['service_count']==37
        for p,h in stage['bindings'].items():assert sha(p)==h,p
        b=H.C.qualified(O/'candidate.nes')
        seed=C.fresh(b)
        H.put(seed,SelectedCharacter=34,FmAlts=1,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,NumberofLives=2)
        C.invoke(seed,'InitScreen')
        assert seed.ram[2][address(b,'KrReady')&8191]==167
        H.put(seed,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,GamePauseStatus=0,Player_Y_Position=144,Player_Y_HighPos=1,Player_State=2,Player_X_Position=80,Player_PageLoc=1,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=1,SavedJoypadBits=0,DisableScreenFlag=0,Mirror_PPUMASK=30,NmiDisable=0)
        def run(m,name,p=0x70):
            seen=[];c=H.start(m,name,a=0xfd,x=3,y=0xc7,p=p)
            def watch(mem,c,i):
                if mem.rawtags[1]==3:
                    for n in ['KrBounce','KrPostTerrain','KrSourceFrame']:
                        if c.pc==address(b,n):seen.append(n)
            c,low=H.finish(m,c,watch)
            return c,low,seen
        cases=0;minimum=255;trace=hashlib.sha256()
        names=['HuBounceOnly','HuBounce','MegaManBounceVelocity']
        for name,face,old_selector,flags in itertools.product(names,[0,128],[8|64,9|64,23,24], [0x30,0x71,0xfe]):
            m=L.fork(seed)
            m.ram[2][0x62]=old_selector|face
            for a,v in [(0x66,5),(0x6a,83),(0x6b,4)]:m.ram[2][a]=v
            before=[H.get(m,n)for n in ['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos']]
            scratch=bytes(m[3:11]);c,low,seen=run(m,name,flags)
            assert seen==['KrBounce'],(name,seen)
            assert m.ram[2][0x62]==face|8 and m.ram[2][0x66]==32
            assert m.ram[2][0x6a]==m.ram[2][0x6b]==0
            assert H.get(m,'Player_State')==1 and H.get(m,'Player_Y_Speed')==253
            assert [H.get(m,n)for n in ['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos']]==before
            assert bytes(m[3:11])==scratch
            # Post-BG is a different real native entry, and a legal rising
            # phase must not immediately turn into a landing or ceiling hit.
            _,lo,seen=run(m,'ThPostNativeHot',flags)
            assert seen==['KrPostTerrain'] and m.ram[2][0x62]==face|8
            heights=[]
            for epoch in range(1,49):
                H.put(m,FrameCounter=epoch)
                _,lo2,seen=run(m,'HuMovement',flags)
                assert seen==['KrSourceFrame']
                heights.append(H.get(m,'Player_Y_Position'));minimum=min(minimum,lo2)
            assert min(heights)==96 and heights[-1]>96,('Unchanged source jump rise/fall',name,heights)
            trace.update(bytes(heights));minimum=min(minimum,low,lo);cases+=1
        post_cases=0
        for face,selector in itertools.product([0,128],[8|64,9|64,23,24]):
            m=L.fork(seed);H.put(m,Player_State=0)
            m.ram[2][0x62]=face|selector
            for a in [0x66,0x6a,0x6b]:m.ram[2][a]=7
            _,_,seen=run(m,'ThPostNativeHot')
            assert seen==['KrPostTerrain'] and m.ram[2][0x62]==face
            assert all(m.ram[2][a]==0 for a in [0x66,0x6a,0x6b]);post_cases+=1
        rejected=0
        for field,value in [('KrReady',0),('GameEngineSubroutine',7),('GamePauseStatus',1)]:
            m=L.fork(seed)
            if field=='KrReady':m.ram[2][address(b,field)&8191]=value
            else:H.put(m,**{field:value})
            before=bytes(m.ram[2]);c,_,seen=run(m,'HuBounceOnly')
            assert not c.p&1 and bytes(m.ram[2])==before;rejected+=1
        result.update(passed=True,ROM_sha256=stage['ROM_sha256'],actual_bounce_ingress_cases=cases,original_jump_updates=cases*48,post_BG_landing_cases=post_cases,rejected_inactive_cases=rejected,minimum_SP=minimum,jump_trace_sha256=trace.hexdigest(),private_post_BG_row=36,public_bounce_rows=[27,31],scope='Actual HuBounceOnly/HuBounce/MegaManBounceVelocity and ThPostNativeHot execute through authenticated transport. Both facings, four falling selectors, three incoming flag combinations;48 unchanged original actor updates per bounce retain48px rise. Source-CPU fixtures, not a controller-earned stomp or a full-stage playthrough.')
    except Exception as e:result.update(error=repr(e),traceback=traceback.format_exc())
    result['bindings']={str(p.resolve()):sha(p)for p in refs}
    (O/'rebound-CPU-controls.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k not in ['bindings','traceback']}))
    assert result['passed'],result.get('error')


if __name__=='__main__':main()
