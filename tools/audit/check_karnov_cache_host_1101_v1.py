"""Actual linked Karnov cold loader, mapper/PPU readback and guarded ingress.

This does not qualify gameplay, native cadence, sound or menu admission.
"""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import battletoads_current_loader_controls_v1 as L
import ff_wram_host_controls_v7 as H
from check_tmnt_render_oa import address
O=R/'build/karnov-host-resource-base-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    q=dict(passed=False,source_CPU=True,native=False,installed=False,menu_admitted=False,no_cache_preload=True)
    try:
        stage=json.loads((O/'cache-assembly.json').read_text())
        for p,h in stage['bindings'].items():assert sha(p)==h,p
        b=H.C.qualified(O/'candidate.nes');image=(O/'kr-kernel.bin').read_bytes();cookie=(O/'kr-cookie.bin').read_bytes()
        expected_state=bytearray(8192);expected_state[0x1fe0:0x1ff0]=cookie
        def make(**kw):
            m=L.make(b);H.put(m,SelectedCharacter=7,FmAlts=1);H.put(m,**kw)
            m.ppuctrl=H.get(m,'Mirror_PPUCTRL');m.writes.clear();m.ram_writes.clear();return m
        smcnames=[('NextBank_SMC',1),('SafecallA_SMC',1),('FarcallJmpTarget_SMC',1),('FarcallJmpTarget_SMC',2),('SafereturnA_SMC',1)]
        smc=lambda m:bytes(m[address(b,n)+d]for n,d in smcnames)
        def call(m,name,**kw):
            frames=[];returns=[];c=H.start(m,name,**kw);r0=bytes(m[3:11]);maps=m.rawtags[:]
            def hook(mem,c,step):
                if c.pc==address(b,name):frames.append(smc(mem))
                end=name+'Return'
                if end in b['syms']and c.pc==address(b,end):returns.append(smc(mem))
            c,low=H.finish(m,c,hook)
            assert c.sp==kw.get('sp',224)and(c.a,c.x,c.y)==(kw.get('a',85),kw.get('x',7),kw.get('y',91))
            # The genuine outer FarCallCommon reloads A on return, setting NZ
            # from caller A. V/D/I survive and A=85 has NZ clear.
            assert c.p&0xce==kw.get('p',0x71)&0x4c,(name,'outer caller flags',c.p)
            assert bytes(m[3:11])==r0 and m.rawtags==maps
            if name in ['KrLoad','KrDispatch']:assert len(frames)==len(returns)==1 and frames==returns,('SMC scope',name,frames,returns)
            return c,low
        rows=[];seed=None
        for wide,reload,ctrl in itertools.product([0,1],[0,1],[128,160,164]):
            m=make(X5WideChrActive=wide,ReloadCHRBank=reload,Mirror_PPUCTRL=ctrl)
            H.invoke(m,'X5PublishChr');latches=m.chr_latches[:];host=bytes(m[0x5c00:0x8000]);foreign=[bytes(z)for z in m.ram[:2]]
            m.writes.clear();m.ram_writes.clear();reads=m.ppu_reads
            c,low=call(m,'KrLoad');assert c.p&1
            assert m.ram[3]==image and m.ram[2]==expected_state
            assert [bytes(z)for z in m.ram[:2]]==foreign and bytes(m[0x5c00:0x8000])==host
            assert m.ram_writes[:2]==[(3,0x1fe0,0),(2,0x1fe0,0)]
            assert m.ram_writes[-2:]==[(3,0x1fe0,167),(2,0x1fe0,167)]
            assert all(bank in [2,3]for bank,_,_ in m.ram_writes)
            assert m.ppu_reads-reads==16400
            assert m.chr_latches==latches and m.upper==0 and m.ppuctrl==ctrl and m.toggle==0
            assert m.ppu_log[-2:]==[(0x2005,73),(0x2005,32)]
            assert H.get(m,'ReloadCHRBank')==reload and m.protection==[2,1]
            assert not any(a in [0x5102,0x5103,0x5113]for a,v in m.writes)
            nr=m.ppu_reads;nw=len(m.ram_writes);cw,_=call(m,'KrLoad');assert cw.p&1 and nr==m.ppu_reads and nw==len(m.ram_writes)
            rows.append(dict(wide=wide,reload=reload,ctrl=ctrl,cycles=c.processorCycles,warm_cycles=cw.processorCycles,minimum_SP=low))
            if seed is None:seed=L.fork(m)
        negatives=[]
        cases=[('rygar',dict(FmAlts=0)),('foreign',dict(SelectedCharacter=0)),('wrongraw',dict(SelectedCharacter=8)),('title',dict(OperMode=0)),('othermode',dict(OperMode=2)),('active',dict(DisableScreenFlag=0)),('mask',dict(Mirror_PPUMASK=30)),('NMI',dict(NmiDisable=0)),('notcommit',dict(FamilyMainCommit=0))]
        for name,values in cases:
            m=make();H.put(m,**values);ram=[bytes(z)for z in m.ram];c,_=call(m,'KrLoad')
            assert not c.p&1 and [bytes(z)for z in m.ram]==ram and not m.ppu_reads
            negatives.append(name)
        for name,protection,corrupt in [('locked',[0,0],None),('state',[2,1],(2,23)),('code',[2,1],(3,17)),('last-code-page',[2,1],(3,7268))]:
            m=make();m.protection=protection;m.corrupt_at=corrupt;c,_=call(m,'KrLoad');assert not c.p&1
            assert all(m.ram[i][0x1fe0]!=167 for i in [2,3])and m.protection==protection
            negatives.append(name)
        poisoned=0;checked=0
        for bank,index in [(None,None)]+list(itertools.product([2,3],range(16))):
            origin=L.fork(seed)
            if bank is not None:origin.ram[bank][0x1fe0+index]^=1
            for f in range(64):
                m=L.fork(origin);nr=m.ppu_reads;c,_=call(m,'KrCheckCode',p=L.flags(f));assert bool(c.p&1)==(bank is None)
                assert not m.ram_writes and m.ppu_reads==nr;checked+=1
            poisoned+=int(bank is not None)
        # Every legal row is entered only after complete authentication, and
        # still returns false because gameplay services have not been authored.
        dispatches=0;entered=0
        for valid,row,f in itertools.product([0,1],range(37),[0,63]):
            m=L.fork(seed)
            if not valid:m.ram[2][0x1fe0]=0
            hits=[];nr=m.ppu_reads;c=H.start(m,'KrDispatch',y=row,p=L.flags(f));snap=[];restore=[]
            def hook(mem,c,step):
                if c.pc==address(b,'KrDispatch'):snap.append(smc(mem))
                if c.pc==address(b,'KrDispatchReturn'):restore.append(smc(mem))
                if 0xa000<=c.pc<0xc000 and mem.rawtags[1]==3:
                    if not hits:assert(c.a,c.x,c.y,c.p&0xcf)==(85,7,row,L.flags(f)&0x4d),('child ABI',valid,row,f,c.a,c.x,c.y,c.p)
                    hits.append(c.pc)
            c,low=H.finish(m,c,hook)
            assert(c.a,c.x,c.y,c.sp)==(85,7,row,224)and c.p&0xcf==L.flags(f)&0x4c,('dispatch ABI',valid,row,f,c.a,c.x,c.y,c.sp,c.p)
            assert snap==restore and len(snap)==1 and m.rawtags==seed.rawtags
            assert bool(hits)==bool(valid and row<36),(valid,row,hits[:4])
            if hits:assert hits[0]==address(b,'KrCacheServices')+3*row;entered+=1
            assert not m.ram_writes and m.ppu_reads==nr;dispatches+=1
        retired=0
        for bank,index in [(None,None)]+list(itertools.product([2,3],range(16))):
            m=L.fork(seed)
            if bank is not None:m.ram[bank][0x1fe0+index]^=1
            before=[bytes(z)for z in m.ram];call(m,'KrRetire')
            for i in [2,3]:
                want=bytearray(before[i])
                if i!=bank:want[0x1fe0]=0
                assert m.ram[i]==want,(bank,index,i)
            retired+=1
        q.update(passed=True,ROM_sha256=stage['ROM_sha256'],loader_cases=rows,negative_cases=negatives,cookie_checks=checked,poisoned_cookie_bytes=poisoned,dispatch_cases=dispatches,authenticated_RAM_entries=entered,retirement_cases=retired,all_foreign_RAM0_1_SRAM_exRAM_restored=True,caller_AXYP_except_C_SP_R0_R7_SMC_exact=True,all_existing_runtime_symbols_exact=True,scope='Actual emitted bank29 loader reads its8KB CHR image via buffered2007 and verifies RAM3/C2; all32header bytes guarded,36typed rows plus bounds, full caller/map/SMC restoration. Kernel services deliberately reject; no scene/Main/menu hook or gameplay/audio/render admission.')
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):sha(p)for p in [Path(__file__),Path(L.__file__),Path(H.__file__),R/'tools/audit/arthur_cache_host_controls_v1.py',O/'cache-assembly.json',O/'candidate.nes',O/'candidate.dbg',O/'kr-kernel.bin',O/'kr-cookie.bin']}
    (O/'cache-CPU-controls.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','traceback','loader_cases']}));assert q['passed'],q.get('error')

if __name__=='__main__':main()
