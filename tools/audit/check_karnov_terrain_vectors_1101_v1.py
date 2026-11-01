"""Real host interrupt cuts through Karnov's actual typed terrain services."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import battletoads_current_loader_controls_v1 as L
import ff_wram_host_controls_v7 as H
import ff_host_pickups_vectors_v2 as V
from check_tmnt_render_oa import address
O=R/'build/karnov-host-resource-base-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    q=dict(passed=False,source_CPU=True,native=False,installed=False,menu_admitted=False)
    try:
        stage=json.loads((O/'terrain-assembly.json').read_text())
        for p,h in stage['bindings'].items():assert sha(p)==h,p
        b=H.C.qualified(O/'candidate.nes');old=V.pending_store
        def pending(m,c,slot,op):
            if old(m,c,slot,op):return True
            value={0x8d:c.a,0x8e:c.x,0x8c:c.y}.get(m[c.pc]);reg=0x5115 if slot==1 else 0x5116
            return value is not None and bytes(m[c.pc+1:c.pc+3])==reg.to_bytes(2,'little')and value==H.get(m,'CurrentBank'if slot==1 else'CurrentBankC')
        V.pending_store=pending
        def run(m,row,hook=None):
            c=H.start(m,'KrServiceVeneers',a=85,x=7,y=30,p=0x70);target=address(b,'KrServiceVeneers')+3*row
            m[address(b,'FarcallJmpTarget_SMC')+1]=target&255;m[address(b,'FarcallJmpTarget_SMC')+2]=target>>8
            trace=[];low=c.sp
            for i in range(500000):
                if c.pc==0x5b00:break
                if hook:hook(m,c,i)
                trace.append((c.pc,m.rawtags[1],m.rawtags[2]));low=min(low,c.sp);assert m[c.pc]!=0;c.step()
            else:raise AssertionError(('service bound',row,hex(c.pc)))
            return c,trace,low
        seed=L.make(b);H.put(seed,SelectedCharacter=7,FmAlts=1,SavedJoypadBits=129)
        c,_=L.call(seed,'KrLoad');assert c.p&1
        c,_,_=run(seed,15);assert c.p&1
        def state(m):
            names=['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_State','Player_Y_Speed','Player_X_Speed','Player_X_Scroll','Player_Pos_ForScroll']
            return [bytes(z)for z in m.ram],m.rawtags[:],H.get(m,'CurrentBank'),H.get(m,'CurrentBankC'),bytes(m[3:11]),bytes(m[0x15a:0x17b]),[H.get(m,n)for n in names]
        rows=[];minimum=255
        for slot in [0,10,14,15,27]:
            origin=L.fork(seed);baseline=L.fork(origin);bc,trace,_=run(baseline,slot)
            unique={}
            for i,pc in enumerate(trace):unique.setdefault(pc,i)
            positions=sorted(unique.values());cuts={0,len(trace)-2,*positions[::max(1,len(positions)//24)]}
            # Source pointer stores and both dispatcher result publications.
            for key,i in unique.items():
                if key[0]in [address(b,n)for n in ['KrInlineDispatch','KrSourceFrame','KrDispatchReturn']]:cuts.add(i)
            for cut in sorted(cuts):
                for kind in ['NMI','IRQ']:
                    m=L.fork(origin);events=[]
                    def hook(mem,c,i):
                        if i==cut:events.append(V.interrupt(mem,c,kind))
                    c,_,low=run(m,slot,hook)
                    assert len(events)==1 and state(m)==state(baseline)and V.cpu_state(c)==V.cpu_state(bc),(slot,kind,cut,'resumption mismatch')
                    minimum=min(minimum,low,events[0]['minimum_SP']);rows.append(dict(service=slot,cut=cut,PC=f'{trace[cut][0]:04X}',**events[0]))
        assert minimum>0x7b,'Live stack reached the actual FarCallCommon SMC operands'
        q.update(passed=True,ROM_sha256=stage['ROM_sha256'],real_interrupt_cuts=len(rows),minimum_SP=minimum,typed_services=[0,10,14,15,27],actual_host_vectors=True,source_never_borrows_NMI_ZP=True,scope='Real emitted dispatcher, selected A3/C2 movement/head/side/constructor/post-terrain services and unchanged host IRQ/NMI vectors. Forced-blank lag NMI fixture, with source actor/typed query result and complete conditional RAM/maps/SMC/foreground scratch/world exports restored. No normal-frame cadence, menu admission or native controller traversal claim.',rows=rows)
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):sha(p)for p in [Path(__file__),Path(V.__file__),O/'terrain-assembly.json',O/'candidate.nes',O/'candidate.dbg']}
    (O/'terrain-vectors.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','rows','traceback']}));assert q['passed'],q.get('error')

if __name__=='__main__':main()
