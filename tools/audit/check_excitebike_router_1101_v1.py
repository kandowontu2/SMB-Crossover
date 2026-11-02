"""Prove current source-funded shared router in memory, including ISR cuts."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
import check_hogan_current_bounded_v1 as M
from prepare_excitebike_host_1101_v1 import BASE,PIN
from prepare_excitebike_dispatch_1101_v1 import O,sha,save

def bundles():
    old=scoped_load(BASE);assert sha(BASE)==PIN
    q=json.loads((O/'router-assembly.json').read_text());assert q['base_ROM_SHA256']==PIN
    new=scoped_load(BASE);raw=bytearray(new['raw'])
    for patch in q['patches']:
        at=patch['offset'];before=bytes.fromhex(patch['old']);after=bytes.fromhex(patch['new'])
        assert raw[at:at+len(before)]==before and len(before)==len(after)
        raw[at:at+len(after)]=after
    new['raw']=bytes(raw);return old,new

def endpoint(m,name,*,a=0x55,x=7,y=91,p=0x31,cut=None,interrupt=None,trace=None):
    b=m.bundle;target=address(b,name)
    m[address(b,'SafecallA_SMC')+1]=a
    m[address(b,'FarcallJmpTarget_SMC')+1]=target&255
    m[address(b,'FarcallJmpTarget_SMC')+2]=target>>8
    c=M.NesMPU(memory=m,pc=address(b,'FarCallCommon'));c.a=((location(b,name)-16)//8192)|128
    c.x=x;c.y=y;c.p=p;c.sp=224;c.stPushWord(0x5aff)
    entered=False;injected=False
    for _ in range(10000):
        if c.pc==target and m.rawtags[1]==207:entered=True
        if entered and trace is not None:trace.append((c.pc,c.sp))
        if entered and cut is not None and not injected and (c.pc,c.sp)==cut:
            injected=True;pc,sp=c.pc,c.sp
            if interrupt=='IRQ':
                assert not c.p&4; c.irq()
            else:c.nmi()
            for _ in range(200000):
                if c.pc==pc and c.sp==sp:break
                assert m[c.pc]!=0,('Actual ISR BRK',interrupt,hex(c.pc));c.step()
            else:raise AssertionError(('Actual ISR return bound',interrupt,cut))
        callback=name in ['HuUpdateDrops','HuRemainingWeapons']
        route_stop=entered and m.rawtags[1]==207 and (
            (callback and c.pc==address(b,'NextBank_SMC'))or
            (not callback and c.pc in [address(b,'FarCallCommon')+3,address(b,'HuNativeWorldPalette')]))
        if route_stop:
            smc=[m[address(b,n)+1]for n in ['NextBank_SMC','SafecallA_SMC','FarcallJmpTarget_SMC']]
            smc+=[m[address(b,'FarcallJmpTarget_SMC')+2],m[address(b,'SafereturnA_SMC')+1]]
            return dict(regs=[c.a,c.x,c.y,c.p,c.sp],SMC=smc,
                        R0_7=list(m[address(b,'R0'):address(b,'R7')+1]),maps=list(m.rawtags),
                        target=[smc[0],smc[2]+256*smc[3]],stop_pc=c.pc,injected=injected)
        assert m[c.pc]!=0,('Actual routing BRK',name,hex(c.pc),m.rawtags)
        c.step()
    raise AssertionError(('Actual endpoint bound',name,hex(c.pc)))

def comparable(q):return {k:v for k,v in q.items()if k!='injected'}

def main():
    old,new=bundles();seeds=[M.fresh(b)for b in [old,new]]
    callback_cases=0;routes=0;exroutes=0;domains=set();cut_trace=[]
    for char in range(38):
      for variant,alts,z2 in [(0,0,0),(1,0,0),(0,4,0),(0,64,0),(0,68,0),(0,0,1)]:
        for name in ['HuUpdateDrops','HuRemainingWeapons']:
          for flags in [0x30,0x31,0x70,0xf1]:
            results=[]
            for seed in seeds:
                m=M.fork(seed);M.put(m,SelectedCharacter=char,RdVariant=variant,FmAlts=alts,Z2Variant=z2)
                results.append(endpoint(m,name,p=flags))
            assert comparable(results[0])==comparable(results[1]),('Callback ABI',char,variant,alts,z2,name,flags,results)
            domains.add(tuple(results[1]['target']));callback_cases+=1
    assert len(domains)==6,domains
    # Actual public native service entry points. Foreign owners must select
    # exactly the same child and preserve all original endpoint ABI/state.
    for char in range(38):
      for row in range(36):
        name='ExRouterProbe'
        for b in [old,new]:
            b['syms'][name]=dict(b['syms']['HuMovement'],val=str(0xb600+16*row))
        for flags in [0x30,0x31,0x70,0xf1]:
            results=[]
            for seed in seeds:
                m=M.fork(seed);M.put(m,SelectedCharacter=char,RdVariant=0,FmAlts=0)
                results.append(endpoint(m,name,p=flags))
            if char<37:
                assert comparable(results[0])==comparable(results[1]),('Foreign route ABI',char,row,flags,results)
                routes+=1
            else:
                actual=results[1]
                if row==32:assert actual['stop_pc']==address(new,'HuNativeWorldPalette')
                else:
                    assert actual['target']==[193,0xb08c+3*row],(row,actual)
                    assert actual['regs'][1:3]==[7,91] and actual['regs'][4]==results[0]['regs'][4]
                    assert actual['R0_7']==results[0]['R0_7']and actual['maps']==results[0]['maps']
                exroutes+=1
    # Every instruction in the actual compacted stack restoration, under
    # IRQ, normal NMI and the native lag-NMI short path. Callback target
    # publication is the same after an interrupt returns at identical PC/SP.
    interrupts={'IRQ':0,'NMI':0,'lagNMI':0}
    for role in ['HuUpdateDrops','HuRemainingWeapons']:
        m=M.fork(seeds[1]);M.put(m,SelectedCharacter=2,RdVariant=1,FmAlts=0,NmiDisable=0)
        trace=[];reference=endpoint(m,role,p=0x31,trace=trace)
        cuts=list(dict.fromkeys((pc,sp)for pc,sp in trace if 0xbf91<=pc<0xbfa1))
        assert len(cuts)==14,len(cuts)
        for mode in interrupts:
          for cut in cuts:
            n=M.fork(seeds[1]);M.put(n,SelectedCharacter=2,RdVariant=1,FmAlts=0,NmiDisable=255 if mode=='lagNMI'else 0)
            result=endpoint(n,role,p=0x31,cut=cut,interrupt='IRQ'if mode=='IRQ'else 'NMI')
            assert result['injected']and comparable(result)==comparable(reference),(mode,role,cut,result,reference)
            interrupts[mode]+=1
    raw=old['raw'][16+79*8192:16+80*8192]
    wordrefs={}
    for name,word in [('Hi',0xbfa4),('Bank',0xbfaa)]:
        needle=word.to_bytes(2,'little');positions=[0xa000+i for i in range(8191)if raw[i:i+2]==needle]
        assert len(positions)==1,(name,positions);wordrefs[name]=positions
    q=dict(passed=True,proposal_only=True,ROM_written=False,base_ROM_SHA256=PIN,
           memory_candidate_SHA256=hashlib.sha256(new['raw']).hexdigest(),
           actual_callback_ABI_cases=callback_cases,actual_callback_target_domains=[list(z)for z in sorted(domains)],
           foreign_service_ABI_cases=routes,Excitebike_service_routes=exroutes,
           original_XY_P_SP_SMC_R0_7_maps_exact=True,ISR_instruction_cuts=interrupts,
           complete_PRG79_table_word_references=wordrefs,extra_source_grant_bytes=0,
           installed=False,native_emulator=False,
           scope='Actual current callback/public service routing instructions, complete current private table word-reference census, source macro ownership, real IRQ/NMI/lag-NMI returns at each compacted restore instruction. No callee gameplay/Main/native replay claim.',
           bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),O/'router-assembly.json',BASE]})
    save('router-CPU.json',q);print(json.dumps(q))

if __name__=='__main__':main()
