"""Source-equivalent predecoded FX, conservative culling and real vector cuts."""
from pathlib import Path
import itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_host_render_controls_v2 as T
from check_tmnt_render_oa import address
P=R/'build/final-fantasy-host-render-v7'
O=R/'build/final-fantasy-host-render-fast-controls-v1'
C=T.C;put=T.put;get=T.get;setv=T.setv;run=T.run


def decoded(b):
    cases=0
    for entry,face,window,shadows in itertools.product(range(144,158),[0,1,2],range(4),[0,1]):
        m=T.setup(b,shadows=shadows);ref=T.setup(b,shadows=shadows)
        for chunk in range(8):
            source=T.records(ref,entry,chunk,window,face)
            if source is None:break
            put(m,FfTargetX=entry,FfTargetPage=chunk,FfTargetY=window,FfTargetW=0,FfSlot=face)
            setv(m,'FfProjectile',125,7)
            run(m,'FfHostCullChunk')
            run(m,'FfHostDecodeFx')
            n=get(ref,'FfRenderBuffer')
            for name,count in [('FfRenderBuffer',n+1),('FfRenderYOffset',2),
                               ('FfRenderPage',1),('SmChrBank',1),('FfTemp2',1),('R0',2)]:
                assert [get(m,name,i)for i in range(count)]==[get(ref,name,i)for i in range(count)],(entry,chunk,face,window,shadows,name)
            cases+=1
    return dict(source_descriptor_pairs=cases,both_shadow_options=True,three_source_faces_all_four_windows=True,
                all_signed_Y_offsets_physical_pages_and_actual_descriptors_exact=True)


def culling(b):
    cases=0;rejected=0
    for entry in range(144,158):
        m=T.setup(b);ref=T.setup(b)
        for chunk in range(8):
            source=T.records(ref,entry,chunk,0,1)
            if source is None:break
            parts,off,page=source
            for center in range(256):
                put(m,FfTargetX=entry,FfTargetPage=chunk,FfTargetW=0)
                setv(m,'FfProjectile',center,7)
                c,_,_=run(m,'FfHostCullChunk')
                valid=[p for p in parts if 31<=center+off+(p[2]-256 if p[2]&128 else p[2])<=239]
                if not c.p&1:
                    assert not valid,('culling removes visible source record',entry,chunk,center)
                    rejected+=1
                cases+=1
    return dict(actual_chunk_origin_cases=cases,whole_chunks_rejected=rejected,
                never_discards_a_native_visible_source_record=True)


def reserved_fields(b):
    m=T.setup(b);ref=T.setup(b)
    for slot in [0,12,24]:
        for arena in [m,ref]:
            for index,value in [(0,1),(1,0),(4,128),(5,1),(7,125),(8,1)]:
                setv(arena,'FfProjectile',value,slot+index)
        setv(m,'FfProjectile',179,slot+2);setv(m,'FfProjectile',93,slot+3)
    cursor={address(b,'FfProjectile')+slot+i for slot in [0,12,24]for i in [2,3]}
    for tick in range(24):
        for arena in [m,ref]:
            put(arena,FfClock=3)
            run(arena,'FfWeapons')
        for at in range(0x5c00,0x5c80):
            if at not in cursor:assert m[at]==ref[at],('source consumes reserved cursor as gameplay',tick,hex(at))
    # Genuine source allocation, rather than an authored reset, initializes
    # both cursor bytes for every new spell identity.
    for slot in [0,12,24]:
        m=T.setup(b)
        for i in range(36):setv(m,'FfProjectile',255,i)
        setv(m,'FfProjectile',0,slot)
        put(m,FfSpell=1)
        c,_,_=run(m,'FfAllocate')
        assert c.p&1
        assert get(m,'FfProjectile',slot+2)==0 and get(m,'FfProjectile',slot+3)==0
    return dict(genuine_source_weapon_ticks=24,all_three_reserved_cursor_pairs_nonsemantic=True,
                actual_source_allocation_resets_all_three_slots=True,
                synthetic_stress='Three simultaneous records test storage/identity safety; source prepare/cast timing is not bypassed in real gameplay.')


def vectors(b):
    def make(kind):
        m=T.setup(b,variant=2,tier=2,shadows=1,rotation=68)
        for index,value in [(0,2),(1,2),(2,1),(3,7),(4,128),(5,1),(7,125),(8,2)]:
            setv(m,'FfProjectile',value,index)
        put(m,NmiDisable=0 if kind=='normalNMI' else 255)
        return m
    m=make('IRQ');_,trace,_=run(m,'FfHostDrawShots')
    # Sample the complete actual callback, plus every executed SMC instruction,
    # native renderer entry, descriptor substitution and mapping handoff.
    landmarks={address(b,n)for n in ['NativeSubset','FfGraphicsBank','FfHostDecodeFx','FfRamPhysicalChr']}
    landmarks.add(address(b,'FfGraphicsBank')+5)
    landmarks.add(address(b,'MetaspriteRenderLoop'))
    cuts=set(range(0,len(trace),97))|{len(trace)-1}
    cuts|={i for i,(pc,bank)in enumerate(trace)if 0x15a<=pc<0x17b or pc in landmarks}
    rows=[];low=255
    for kind,cut in itertools.product(['normalNMI','lagNMI','IRQ'],sorted(cuts)):
        m=make(kind);fired=[]
        def hook(m,c,step):
            nonlocal low
            if step!=cut:return
            before=T.T.ffstate(m)
            result=T.ISR.interrupt(m,c,'IRQ'if kind=='IRQ'else'NMI')
            assert T.T.ffstate(m)==before
            low=min(low,result['minimum_SP']);fired.append(True)
        run(m,'FfHostDrawShots',hook=hook)
        assert fired;rows.append([kind,cut])
    return dict(actual_full_callback_instructions=len(trace),real_vector_cuts=len(rows),minimum_ISR_SP=low,
                all143_FF_bytes_all33SMC_live_page1_R0R1_R6R7_and_all4payload_banks=True,
                cut_selection='Every executed SMC PC and actual mapper/render/temporary-descriptor handoff plus97instruction spacing; not every instruction cut.')


if __name__=='__main__':
    assert not O.exists();O.mkdir();h=json.loads((P/'build-proof.json').read_text())
    for path,d in h['bindings'].items():assert C.sha(path)==d,path
    b=C.bundle(P);checks={};failures={}
    for name,fn in dict(decoded_source_equivalence=decoded,culling=culling,reserved_fields=reserved_fields,actual_vectors=vectors).items():
        try:checks[name]=fn(b);print(json.dumps(dict(group=name,passed=True,checks=checks[name])),flush=True)
        except Exception as e:failures[name]=dict(error=repr(e),traceback=traceback.format_exc());print(json.dumps(dict(group=name,passed=False,error=repr(e))),flush=True)
    bindings={**h['bindings'],str((P/'build-proof.json').resolve()):C.sha(P/'build-proof.json')}
    for p in [Path(__file__).resolve(),Path(T.__file__).resolve()]:bindings[str(p)]=C.sha(p)
    report=dict(passed=not failures,image_sha256=C.sha(P/'ram3.bin'),checks=checks,failures=failures,
                native=False,full_Main=False,bindings=bindings)
    (O/'controls.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=not failures,groups=len(checks),failed=list(failures))))
    if failures:raise SystemExit(1)
