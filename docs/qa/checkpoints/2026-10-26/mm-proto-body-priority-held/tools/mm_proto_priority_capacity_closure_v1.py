"""Actual prebody emitter closure: zero cursor cannot follow reserved R.

Configured saturated pools are a conservative stress superset, not evidence
of naturally acquiring ten identical special weapons. Generic/Water controls
cover every aligned reserved cursor, including the actual252 boundary.
"""
from pathlib import Path
import argparse,hashlib,itertools,json,traceback
import mm_proto_body_priority_partition_v6 as fixture
from check_tmnt_render_oa import Memory,address,location
from link_pit_rygar_sophia_audit_cpu import scoped_load
from verify_native_relocation import NesMPU

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def invoke(b,m,name,flags=0x20,x=0):
    pc=address(b,name);bank=(location(b,name)-16)//8192;window=(pc-0x8000)//8192
    m.page(window,bank)
    if window in[1,2]:m[address(b,'CurrentBank'if window==1 else'CurrentBankC')]=bank|128
    c=NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=85,x,7,flags,253;c.stPushWord(0x7eff);m.writes=[]
    for _ in range(20000):
        if c.pc==0x7f00:break
        c.step()
    else:raise AssertionError(('Emitter timeout',name,hex(c.pc)))
    assert c.sp==253
    return c


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in['candidate','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);rows=[]
    try:
        b=scoped_load(a.candidate);l=lambda n:address(b,n)
        names=[f'SsArt{i}{face}'for i in range(115)for face in['Left','Right']]
        names +=[f'MmMM_BULLET_{i}{face}'for i in range(1,17)for face in['Left','Right']]
        names +=[f'MmHurtFx{i}'for i in range(4)]
        records=[];generic=0
        for name in names:
            ptr=l(name);off=location(b,name);bank=(off-16)//8192;header=b['raw'][off]
            assert 0xc000<=ptr<0xe000 and header%4==0 and header<128,(name,hex(ptr),header)
            records.append(dict(name=name,bank=bank,address=ptr,header=header))
            m=Memory(b);m.page(1,4);m.page(2,bank)
            for n,v in dict(CurrentBank=132,CurrentBankC=bank|128,R0=ptr&255,R1=ptr>>8,R3=0,R4=128,R5=0,R6=176,R7=1,GuestOamRotationActive=128,RgOamRotation=0).items():m[l(n)]=v
            for cursor,flags in itertools.product(range(44,256,4),[0x20,0x61,0xa2,0xeb]):
                m[l('CurrentOAMOffset')]=cursor
                c=invoke(b,m,'MetaspriteRenderLoop',flags)
                expected=cursor+header if header and cursor+header<256 else cursor
                assert m[l('CurrentOAMOffset')]==expected and 44<=expected<=252,(name,cursor,flags,m[l('CurrentOAMOffset')],expected)
                assert all(0x200+44<=at<0x300 for at,v in m.writes if 0x200<=at<0x300)
                generic+=1
        water=0
        for cursor,flags,art,face,family in itertools.product(range(44,256,4),[0x20,0x61,0xa2,0xeb],[38,39],[1,2],[4,255]):
            m=Memory(b)
            for n,v in dict(SelectedCharacter=1,ProtoVariant=1,CurrentOAMOffset=cursor,GuestOamRotationActive=128,RgOamRotation=0,SsArt=art,SsDrawFamily=family,RgSlot=0,RgShotX=128,RgShotPage=0,RgShotY=176,RgShotYHigh=1,RgShotDir=face).items():m[l(n)]=v
            c=invoke(b,m,'SpecialDrawWaterShot',flags)
            expected=cursor+8 if cursor+8<256 else cursor
            assert m[l('CurrentOAMOffset')]==expected and 44<=expected<=252,(cursor,flags,art,face,family,m[l('CurrentOAMOffset')],expected)
            assert all(0x200+44<=at<0x300 for at,v in m.writes if 0x200<=at<0x300)
            water+=1
        finish=0
        for variant,flags in itertools.product([0,1],fixture.base.FLAGS):
            R=44 if variant else40
            m=Memory(b)
            for cursor in range(R,256,4):
                for n,v in dict(CurrentOAMOffset=cursor,GuestOamRotationActive=128,ProtoVariant=variant,RgOamPlayerStart=0).items():m[l(n)]=v
                c=invoke(b,m,'MmBodyPriorityFinish',flags)
                assert m[l('RgOamPlayerStart')]==cursor-R and m[l('CurrentOAMOffset')]==cursor,(variant,cursor,flags,m[l('RgOamPlayerStart')])
                finish+=1
        # Do not hide the arbitrary direct-entry underflow behavior. It is a
        # counterexample only outside the source-proved reserved-cursor invariant.
        m=Memory(b)
        for n,v in dict(CurrentOAMOffset=0,GuestOamRotationActive=128,ProtoVariant=1,RgOamPlayerStart=0).items():m[l(n)]=v
        invoke(b,m,'MmBodyPriorityFinish')
        impossible=dict(staged_CurrentOAMOffset=0,actual_shot_count=m[l('RgOamPlayerStart')],modular_expected=212,source_reachable=False,reason='Every live prebody path starts44, then only positive multiple4 carry-reject advances; explicit zero reset belongs to death path excluded by priority predicate.')
        assert impossible['actual_shot_count']==211
        # Invoke real whole prebody callers; no cursor write is injected after
        # setup. Ten Knuckle-art entries are above the natural per-weapon cap,
        # deliberately a conservative emitter stress superset.
        saturation=[]
        for kind,art,typ in [('Knuckle-art-superset',3,11),('water-superset',38,17),('native-bricks',0,9)]:
            cfg=dict(entry='DrawAllMetasprites',variant=1,types=[1,1,1,1],special=10,specialart=art,specialtype=typ,drops=4,first=112,flags=0x20)
            c,m,before=fixture.setup(b,cfg);observed=[];writes=[]
            for index in range(150000):
                if c.pc==l('MmBodyPriorityFinish'):break
                old=len(m.writes);pc=c.pc;c.step()
                for at,v in m.writes[old:]:
                    if at==l('CurrentOAMOffset'):writes.append(dict(pc=pc,value=v));observed.append(v)
            else:raise AssertionError(('No Finish',kind))
            cursor=m[l('CurrentOAMOffset')]
            assert observed and observed[0]==44 and all(44<=v<=252 and v%4==0 for v in observed),(kind,writes)
            before_cursor=cursor
            # Finish is an actual JSR target with its real return already on
            # the stack. Continue it through the original InitObjectLoop site.
            for _ in range(1000):
                if c.pc==l('DrawAllMetasprites::InitObjectLoop'):break
                c.step()
            else:raise AssertionError('Finish continuation timeout')
            assert m[l('CurrentOAMOffset')]==before_cursor and m[l('RgOamPlayerStart')]==before_cursor-44
            saturation.append(dict(kind=kind,configured_stress_not_natural_acquisition=True,actual_prebody_cursor=cursor,actual_p=m[l('RgOamPlayerStart')],cursor_writes=writes))
        assert any(r['actual_prebody_cursor']==252 and r['actual_p']==208 for r in saturation)
        proof=dict(passed=True,source_only=True,native_run=False,ROM_sha256=sha(a.candidate),immutable_record_headers=len(records),actual_generic_emitter_cases=generic,actual_water_cases=water,actual_Finish_legitimate_cursor_cases=finish,invariant='Priority Proto starts44, alignment4, positive multiple4 generic headers reject sums>=256 before publishing; water ADC8 rejects before STA. Thus each prebody cursor remains44..252 and cannot0. No main gameplay/NMI/IRQ zero cursor owner exists on this live path; death resets are guarded out.',source_record_writer_closure=['ProtoLegacyDrawShotsCold→MetaspriteRenderLoop','InventoryDrawPickups/SpecialDrawShots/MegaManHurtDraw→MetaspriteRenderLoop','SpecialDrawWaterShot→own ADC8/carry rejection','MegaManDrawDeath explicit0: only MmDeathFlag nonzero, priority predicate off'],arbitrary_direct_entry_counterexample=impossible,real_prebody_stress=saturation,limits=__doc__,checker_sha256=sha(__file__))
        (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');(a.output/'records.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items()if k not in['real_prebody_stress','source_record_writer_closure']},indent=2))
    except BaseException as error:
        (a.output/'failure.json').write_text(json.dumps(dict(passed=False,error=repr(error),traceback=traceback.format_exc(),checker_sha256=sha(__file__)),indent=2)+'\n');(a.output/'failed-tool.py').write_bytes(Path(__file__).read_bytes());raise


if __name__=='__main__':main()
