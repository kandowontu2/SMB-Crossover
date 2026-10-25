"""Compare actual Roll custom draw admission with assembled shared-host fade. CPU only."""
from pathlib import Path
import argparse, hashlib, itertools, json
from collections import Counter
from final_roll_items_cpu import ready
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location
from verify_native_relocation import NesMPU

BASE='9bac46e934d3301e378139783febf2d54c4fd5753a62e082f2d7e6580946d58c'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def cpu_at(q,name,flags=0x30,x=0,y=7):
    b,m=q.b,q.m;pc=address(b,name);bank=(location(b,name)-16)//8192;window=(pc-0x8000)//8192
    if m.banks[window]!=bank:m.page(window,bank)
    if window in [1,2]:q.set('CurrentBank'if window==1 else'CurrentBankC',bank|128)
    m.writes=[];c=NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=0x55,x,y,flags,0xfd
    return c


def invoke(q,name,flags=0x30,x=0,y=7):
    c=cpu_at(q,name,flags,x,y);c.stPushWord(0x5aff);trace=[];low=255
    for _ in range(100000):
        if c.pc==0x5b00:
            assert c.sp==0xfd
            for n,i in [('CurrentBank',1),('CurrentBankC',2)]:assert q.get(n)==q.m.banks[i]|128
            return dict(registers=[c.a,c.x,c.y,c.p&0xcf,c.sp],writes=trace,cycles=c.processorCycles,min_sp=low)
        pc=c.pc;bank=q.m.banks[(pc-0x8000)//8192]if pc>=0x8000 else-1
        low=min(low,c.sp);start=len(q.m.writes);c.step()
        trace.extend(dict(pc=pc,bank=bank,address=p,value=v)for p,v in q.m.writes[start:])
    raise AssertionError(('CPU timeout',name,hex(c.pc)))


def actual_host_admits(q,slot):
    c=cpu_at(q,'InventoryDrawPickups::Drops',x=slot)
    yes,no=address(q.b,'InventoryDrawPickups::Visible'),address(q.b,'InventoryDrawPickups::NextDrop')
    for _ in range(50):
        if c.pc in [yes,no]:return c.pc==yes
        c.step()
    raise AssertionError(('Host admission timeout',hex(c.pc)))


def actor(q,kind,meter,age,frame,slot,x=168,page=1,y=208):
    for n,v in dict(InvDropKind=kind,AvDropItem=meter,InvDropAge=age&255,
                    InvDropAgeHi=age>>8,InvDropX=x,InvDropPage=page,
                    InvDropY=y).items():q.set(n,v,slot)
    q.set('FrameCounter',frame)


def nonstack(r):return[(t['address'],t['value'])for t in r['writes']if not 0x17b<=t['address']<0x200]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--private',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();build=json.loads((a.private/'proof.json').read_text(encoding='utf-8'))
    baseline=a.private/'baseline/candidate.nes';candidate=a.private/'candidate.nes'
    assert sha(baseline)==build['base_sha256']==BASE and sha(candidate)==build['candidate_sha256']
    a.output.mkdir(parents=True,exist_ok=False);old,new=map(scoped_load,[baseline,candidate]);rows=[]
    # Execute the actual shared admission branch, then compare helper output to
    # the real original LDA opcode for visible/empty render states. Covers all
    # live source ages0..420 plus explicitly unreachable high-age CPU controls.
    ages=list(range(421))+[511,512,65535];flags=[0x30|c|i|d|v for c,i,d,v in itertools.product([0,1],[0,4],[0,8],[0,64])]
    host=ready(old);fixed=ready(new);reference=ready(old);helper_cases=0;digest=hashlib.sha256()
    site=address(old,'RlDraw::Drops')+3
    for age,kind,frame,slot in itertools.product(ages,[0,1,2],[42,43],range(4)):
        actor(host,kind,128,age,frame,slot);admit=actual_host_admits(host,slot)
        actor(fixed,kind,128,age,frame,slot)
        for f in flags:
            reference.set('InvDropKind',kind if admit else 0,slot)
            c=cpu_at(reference,'RlDraw::Drops',f,slot);c.pc=site;c.step()
            want=[c.a,c.x,c.y,c.p&0xcf,c.sp]
            got=invoke(fixed,'RlDropVisibleKind',f,slot)
            assert got['registers']==want,(age,kind,frame,slot,f,want,got['registers'])
            assert not nonstack(got)
            helper_cases+=1;digest.update(bytes([age&255,age>>8,kind,frame,slot,f,int(admit)]))
    # Execute the whole custom renderer. The unchanged supplied art is the
    # visible oracle; an empty original actor is the exact hidden-output oracle.
    def draw_case(mode,kind,meter,age,frame,slot,offset,x=168,page=1,y=208):
        h=ready(old,mode);actor(h,kind,meter,age,frame,slot,x,page,y)
        admit=actual_host_admits(h,slot)
        qs=[ready(b,mode)for b in [old,new]]
        for j,q in enumerate(qs):
            actor(q,kind if j or admit else 0,meter,age,frame,slot,x,page,y)
            q.set('CurrentOAMOffset',offset)
        before,after=[invoke(q,'RlDraw')for q in qs]
        assert before['registers']==after['registers'],(mode,kind,meter,age,frame,slot,offset,x,page,y)
        assert nonstack(before)==nonstack(after),(mode,kind,meter,age,frame,slot,offset,x,page,y)
        if not admit:assert not[t for t in after['writes']if 0x200<=t['address']<0x300]
        rows.append(dict(case='whole_custom_draw_exact_host_admission_oracle',mode=mode,kind=kind,meter=meter,age=age,frame=frame,slot=slot,offset=offset,x=x,page=page,y=y,admitted=admit,cycles=after['cycles'],min_sp=after['min_sp']))
    for args in itertools.product([0,1],[1,2],[0,128],[0,1,239,240,241,247,255,256,419,420],[42,43],[0,3],[0,144,159,160]):draw_case(*args)
    for mode,x,page,y,age in itertools.product([0,1],[0,8,168,255],[0,1,2],[31,32,208,239,240],[239,240]):draw_case(mode,1,128,age,43,3,128,x,page,y)
    # Actual old custom renderer's first OAM write at native-observed policy
    # counterexample. No native per-byte PC is claimed by this CPU record.
    q=ready(old);actor(q,1,128,240,43,3);q.set('CurrentOAMOffset',0)
    bad=invoke(q,'RlDraw');first=next(t for t in bad['writes']if 0x200<=t['address']<0x300)
    assert not actual_host_admits(q,3)
    proof=dict(passed=True,native_passed=False,goal_complete=False,scope=__doc__,
        baseline_SHA256=BASE,candidate_SHA256=sha(candidate),script_SHA256=sha(Path(__file__)),build_proof_SHA256=sha(a.private/'proof.json'),
        helper_cases=helper_cases,helper_case_digest=digest.hexdigest(),helper_age_values=len(ages),preserved_helper_registers='Exact A/X/Y andNV-DIZC versus actual originalLDA with host admission; SPFDreturn.',
        whole_draw_cases=len(rows),case_counts=dict(Counter(r['case']for r in rows)),checks=rows,
        baseline_CPU_first_wrong_OAM_write=first,baseline_native_observation='Native9bac Hardage240/frame43 andEasyage241/frame125 each emitted16OAMbytes; actual24agewindowframes showvisibleorb. Nativebyte-writePCnotcaptured; firstwriteaboveisactualassembledCPUtrace.',
        preserved='Whole customdraw exact ordered nonstack application/SMC/mapper/OAM writes andreturnregisters vs unchanged art/empty-actor host-admission oracle; both sizes/meters/modes,slots0/3,capacity/viewport/yedges. Helper noRAMwrites except ownstack.',
        limits=['Direct CPU actor/age/frame/camera controls. No native fade requalification, current-ROM adoption, original mobile timing/audio or full-goal claim.','Existing single-owner9bac native lifecycle receipts remain their exacthash andscope; this new candidate is sourceCPUonly.'])
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in proof.items()if k not in ['checks','limits']}))


if __name__=='__main__':main()
