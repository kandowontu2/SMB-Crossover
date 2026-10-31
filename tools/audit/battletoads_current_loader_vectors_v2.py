"""Actual vector interruptions through BT loader, row and sourceInit frames."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import battletoads_current_loader_controls_v1 as T
H,V=T.H,T.V
from check_tmnt_render_oa import address
O=T.O;J=T.J
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def begin(m,name,slot=None):
    c=H.start(m,name,p=0x30)
    if slot is not None:
        pc=address(m.bundle,name)+3*slot
        m[address(m.bundle,'FarcallJmpTarget_SMC')+1]=pc&255
        m[address(m.bundle,'FarcallJmpTarget_SMC')+2]=pc>>8
    return c


def main():
    out=O/'loader-vectors-v2.json';assert not out.exists()
    q=dict(passed=False,source_CPU=True,native=False,real_vectors=True,no_RAM3_preload=True)
    try:
        b=H.C.qualified(J/'candidate.nes');cold=T.make(b);warm=T.fork(cold);T.call(warm,'BtLoad')
        rows=[]
        plans=[('cold-load',cold,'BtLoad',None,False),('check',warm,'BtCheck',None,True),
               ('row',warm,'BtServiceVeneers',0,True),('source-init',warm,'BtServiceVeneers',15,True),
               ('retire',warm,'BtRetire',None,True)]
        for family,seed,name,slot,active in plans:
            m=T.fork(seed);H.put(m,NmiDisable=0 if active else 255)
            c=begin(m,name,slot);seen=set();cuts=[]
            for step in range(500000):
                if c.pc==0x5b00:break
                tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
                own=(tag in[0xdd,0xd7,3]and 0xa000<=c.pc<0xc000)or 0x15a<=c.pc<0x17b
                key=(tag,c.pc)
                if own and key not in seen:
                    cuts.append((step,c.pc,tag,bool(c.p&4)));seen.add(key)
                c.step()
            else:raise AssertionError('trace bound')
            assert c.sp==224
            for step,pc,tag,masked in cuts:
                kinds=[('NMI',0,0),('NMI',255,0),('NMI',0,1)]if active else[('NMI',255,0)]
                if not masked:kinds.append(('IRQ',255,0))
                for kind,lag,pause in kinds:
                    z=T.fork(seed);H.put(z,NmiDisable=lag,GamePauseStatus=pause)
                    cc=begin(z,name,slot)
                    for i in range(step):cc.step()
                    assert cc.pc==pc and (z.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else -1)==tag
                    audio=[];original=cc.step
                    def stepping():
                        if cc.pc==address(b,'AudioUpdate'):audio.append(cc.pc)
                        return original()
                    cc.step=stepping
                    r=V.interrupt(z,cc,kind)
                    cc.step=original
                    assert len(audio)==(1 if kind=='NMI' else 0),(family,kind,hex(pc),len(audio))
                    H.finish(z,cc)
                    assert cc.sp==224 and z.rawtags[1]==seed.rawtags[1]and z.rawtags[2]==seed.rawtags[2]
                    if family=='cold-load':
                        expected=bytearray((J/'bt/cache.bin').read_bytes());expected[0x1fe0:0x1ff0]=(J/'bt/cookie.bin').read_bytes()
                        assert z.ram[3]==expected and z.ppu_reads==16400
                    elif family=='source-init':assert z.ram[3][address(b,'BtHostReady')&8191]==1
                    elif family=='retire':assert z.ram[3][0x1fe0]==0
                    rows.append(dict(family=family,step=step,pc=pc,tag=tag,lag=lag,pause=pause,
                        original_AudioUpdate_entries=len(audio),**r))
        q.update(passed=True,actual_vector_cases=len(rows),families={n:sum(r['family']==n for r in rows)for n,*_ in plans},
            normal_lag_pause_and_legal_IRQ=True,all33SMC_livepage1_rawmaps_and_borrowed_pairs_exact=True,
            original_AudioUpdate_once_per_NMI=True,cold_real_buffered_loader_resumes_to_exact8192image=True,
            sourceInit_ready_publication_interrupted=True,rows=rows,
            scope='Actual loader/ROMrow/cookie/sourceInit vectors. Source movement/terrain/render/Main remains unintegrated; not native or readiness evidence.')
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(T.__file__),Path(V.__file__),O/'source-stage.json',
        O/'loader-controls.json',J/'candidate.nes',J/'candidate.dbg',J/'bt/cache.bin',J/'bt/cookie.bin']}
    out.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['rows','bindings','traceback']}));assert q['passed'],q.get('error')


if __name__=='__main__':main()
