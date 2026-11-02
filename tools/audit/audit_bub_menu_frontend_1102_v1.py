"""Actual installed-menu closure for a gated 33rd Bub/Bob position.

No ROM is written. This consumes the frozen navigation proposal read-only and
executes its in-memory counterpart solely to prove the existing resolver chain.
"""
from pathlib import Path
import sys,json,hashlib,collections,copy
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import check_hogan_current_bounded_v1 as M
from check_tmnt_render_oa import address,location
from link_pit_rygar_sophia_audit_cpu import scoped_load
from verify_native_relocation import NesMPU
O=R/'build/bub-menu-integration-1102-v1'
BASE=R/'build/excitebike-pose-1101-v3/current4.nes'
PIN='cf1412eb78ed6531d2f7478c9790f96314a95f2f3fdd6c2b80bfbefd24fca3a8'
COUNTS=[8,2,2,2,2,4,2,2,2,3,3,2,2,2,3,1,4,4,4,2,2,4,1,2,8,1,2,1,6,2,4,2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def invoke(m,name,*,a=85,x=7,y=91,p=0x31,watch=None):
    b=m.bundle;target=address(b,name)
    m[address(b,'SafecallA_SMC')+1]=a
    m[address(b,'FarcallJmpTarget_SMC')+1]=target&255
    m[address(b,'FarcallJmpTarget_SMC')+2]=target>>8
    c=NesMPU(memory=m,pc=address(b,'FarCallCommon'))
    c.a=((location(b,name)-16)//8192)|128;c.x=x;c.y=y;c.p=p;c.sp=224;c.stPushWord(0x5aff)
    low=c.sp
    for _ in range(500000):
        if c.pc==0x5b00:break
        low=min(low,c.sp)
        if watch:watch(c)
        assert m[c.pc]!=0,('Actual BRK',name,hex(c.pc),m.rawtags)
        c.step()
    else:raise AssertionError(('Source call bound',name,hex(c.pc),m.rawtags))
    assert c.sp==224
    return dict(A=c.a,X=c.x,Y=c.y,P=c.p,minimum_SP=low)

def commands(m):
    at=address(m.bundle,'VRAM_Buffer1');end=M.get(m,'VRAM_Buffer1_Offset');out=[];i=0
    while i<end:
        hi,lo,length=m[at+i:at+i+3];n=length&63
        out.append(dict(address=(hi<<8)|lo,length=length,bytes=list(m[at+i+3:at+i+3+n])))
        i+=3+(1 if length&64 else n)
    return out

def main():
    O.mkdir(exist_ok=True);assert sha(BASE)==PIN
    b=scoped_load(BASE);raw=b['raw']
    grant_path=R/'docs/qa/allocations/bub-menu-1102-v1.json';grant=json.loads(grant_path.read_text())
    nav_root=R/'build/bub-menu-navigation-1102-v1';nav=json.loads((nav_root/'proposal.json').read_text())
    assert grant['granted']and grant['base_ROM_SHA256']==PIN and nav['passed']
    lo=16+66*8192+0xd39;hi=16+66*8192+0xd7b
    assert sha(nav_root/'proposal.json')==grant['navigation']['proposal_SHA256']
    assert hashlib.sha256(raw[lo:hi]).hexdigest()==grant['front_end_PRG']['preimage_SHA256']
    symbols=[]
    for n,s in b['syms'].items():
        try:at=location(b,n)
        except (AssertionError,KeyError,ValueError,TypeError):continue
        if lo<=at<hi:symbols.append(dict(name=n,address=address(b,n),size=s.get('size')))
    refs=[]
    for f in (R/'src').rglob('*'):
        if f.suffix not in ['.s','.inc']:continue
        for i,line in enumerate(f.read_text(errors='replace').splitlines(),1):
            if 'CursorLow'in line or 'CursorHigh'in line:refs.append(dict(file=f.relative_to(R).as_posix(),line=i,text=line.strip()))
    assert {z['file']for z in refs}=={'src/character_select.s'}
    # Change only the already-granted navigation in memory. No candidate file.
    nr=bytearray(raw);start=16+124*8192;nr[start:start+224]=(nav_root/'navigation.bin').read_bytes()
    for z in nav['patches']:
        at=z['offset'];old=bytes.fromhex(z['old']);new=bytes.fromhex(z['new'])
        assert nr[at:at+len(old)]==old;nr[at:at+len(new)]=new
    nb=dict(b);nb['raw']=bytes(nr)
    m=M.fresh(nb);M.put(m,CrossoverMenuIndex=32,FmAlts=0,FmGroups=0)
    chain_names=['MenuResolveCharacter','FmResolve','CmHostResolveCharacter','NrMenuCharacter','NrMenuAltTail']
    points={(address(b,n),((location(b,n)-16)//8192)|128):n for n in chain_names}
    seen=collections.Counter()
    def chain(c):
        if c.pc>=0x8000:
            n=points.get((c.pc,c.memory.rawtags[(c.pc-0x8000)//8192]))
            if n:seen[n]+=1
    resolved=invoke(m,'MenuResolveCharacter',watch=chain)
    assert M.get(m,'SelectedCharacter')==39 and seen['FmResolve']and seen['CmHostResolveCharacter']and seen['NrMenuCharacter']
    pending=invoke(m,'FmPending');assert not pending['P']&1
    resolver=dict(passed=True,SelectedCharacter=39,chain=dict(seen),result=resolved,
                  old_pending_result=pending,extra_resolver_bytes_required=0,
                  pending_wrapper_required_for_raw_resolution=False,
                  menu_admitted=False,navigation_applied_only_in_memory=True)
    # All actual current profiles: collect cold native UI consumers rather than
    # assuming ready confirmations imply their old pending data is dead.
    domains=collections.Counter();previews=collections.Counter();rows=[];all_calls=collections.Counter()
    name_pc=address(b,'FmQueueName')+3;draw_pc=address(b,'FmDrawPreviewSelected')
    def watch(c):
        if c.pc<0x8000:return
        tag=c.memory.rawtags[(c.pc-0x8000)//8192]
        if tag==204 and c.pc==name_pc:domains[c.a]+=1
        if tag==204 and c.pc==draw_pc:previews[c.a]+=1
        for name in ['FmDrawCfPreview','BtColdPortrait','FmCfRestoreP1']:
            if c.pc==address(b,name)and tag==((location(b,name)-16)//8192)|128:all_calls[name]+=1
    for slot,count in enumerate(COUNTS):
        m=M.fresh(b);M.put(m,CrossoverMenuIndex=slot)
        invoke(m,'MenuResolveCharacter',watch=watch);invoke(m,'QueueSelection',watch=watch)
        for variant in range(count):
            if variant:
                M.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0)
                invoke(m,'CrossoverMenuInput',watch=watch)
            q=commands(m)
            row=dict(slot=slot,variant=variant,raw=M.get(m,'SelectedCharacter'),groups=M.get(m,'FmGroups'),alts=M.get(m,'FmAlts'),names=[z['bytes']for z in q if z['address']==0x2328])
            starts=[]
            for key in [16,128]:
                n=M.fork(m);M.put(n,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=key,SavedJoypad2Bits=0)
                invoke(n,'CrossoverMenuInput');starts.append(M.get(n,'CrossoverMenuState')==0)
            assert starts[0]==starts[1],(slot,variant,starts)
            row['confirm_launches']=starts[0];rows.append(row)
        print('profiles',slot,len(rows),flush=True)
    assert len(rows)==91 and sum(z['confirm_launches']for z in rows)==90
    q=dict(passed=True,ROM_SHA256=PIN,ROM_written=False,menu_admitted=False,
           granted_fallback_closure=dict(symbols=symbols,source_references=refs,bytes=66,
             public_thunk_preserved=True,root_public_thunk_cases=nav['cursor_full_thunk_cases']),
           new_slot_resolver=resolver,actual_profiles=len(rows),actual_ready=90,
           FmQueueName_observed_indices={str(k):v for k,v in domains.items()},
           FmDrawPreview_observed_indices={str(k):v for k,v in previews.items()},cold_UI_calls=dict(all_calls),profiles=rows,
           selector_rejections=dict(bit7='Current CF preview ORA80; restore AND3F clears it.',bit5='Retained BT Rash/Zitz selector; direct sharing couples identities.'),
           selector_candidate='Unify identical CF/BT P1 markers onto bit6 before reserving bit7; complete transition proof pending.',
           bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),BASE,grant_path,nav_root/'proposal.json',nav_root/'navigation.bin']})
    (O/'frontend-closure.json').write_text(json.dumps(q,indent=2)+'\n')
    files=[p for p in O.rglob('*')if p.is_file()];assert sum(p.stat().st_size for p in files)<16000000 and len(files)<=128
    print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','profiles','granted_fallback_closure']}))
if __name__=='__main__':main()
