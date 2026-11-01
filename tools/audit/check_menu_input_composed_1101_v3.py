"""Check the real composed menu; never overlay or publish code.

--prepare records compact old public-PC and native input/init baselines while
the parent explicitly holds its pre-menu build stable. Default validation
requires the parent's new terminal --expected ROM hash.
"""
from pathlib import Path
import argparse,copy,hashlib,itertools,json,sys,traceback
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'tools/audit'),str(ROOT/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
import check_hogan_current_bounded_v1 as C
import ff_wram_host_controls_v7 as H
BASE=ROOT/'build/karnov-host-resource-base-1101-v1'
OUT=ROOT/'build/karnov-menu-input-composed-1101-v3'
COMPONENT=ROOT/'build/karnov-menu-input-component-1101-v3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
OLD='993d4489b6f944ea42646fda33d046357deb7088332038b97327d3e094f6d6e0'
INSTALLED=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
COUNTS=[7,2,2,2,2,4,2,2,2,3,3,2,2,2,3,1,4,4,4,2,2,4,1,2,8,1,2,1,6,2,4,2]

def prepare():
    OUT.mkdir(exist_ok=True)
    assert not(OUT/'baseline.json').exists(),'Do not replace captured old baseline'
    assert sha(BASE/'candidate.nes')==OLD
    dbgsha=sha(BASE/'candidate.dbg');b=scoped_load(BASE/'candidate.nes')
    roots=set()
    for line in(BASE/'candidate.dbg').read_text().splitlines():
        if line.startswith('scope\t'):
            d=dict(x.split('=',1)for x in line[6:].split(',')if'='in x)
            if'parent'not in d:roots.add(d['id'])
    public={}
    for name,s in b['syms'].items():
        if s.get('scope')not in roots or s.get('type')!='lab' or name.startswith('$')or'::'in name:continue
        pc=address(b,name);pos=location(b,name)if'seg'in s and'ooffs'in b['segs'][s['seg']]else None
        public[name]=[pc,pos]
    protected={}
    for name in ['CrossoverMenuInput','CrossoverMenuInput::BuildScreen','CrossoverMenuInput::SelectInput','CrossoverMenuInput::CheckConfirm','CrossoverMenuInput::CheckDirection','CrossoverMenuInput::Changed','CrossoverInit','NrGlobalInit','MenuResolveCharacter','QueueSelection','DrawSelectionPreview','QueueVariantHint','MenuPreviewBudget','NativeRareGameMenuRoutineCore::ChkContinue']:
        protected[name]=[address(b,name),location(b,name)]
    assert sha(BASE/'candidate.nes')==OLD and sha(BASE/'candidate.dbg')==dbgsha
    q=dict(passed=True,old_ROM_sha256=OLD,old_dbg_sha256=dbgsha,public_PC_count=len(public),public=public,protected=protected,scope='Address/location manifest only; no ROM, debug, PRG, object or source tree copied. Captured before parent menu-input compilation.')
    (OUT/'baseline.json').write_text(json.dumps(q,separators=(',',':'))+'\n')
    print(json.dumps({k:v for k,v in q.items()if k not in['public','protected']}))

def check(expected):
    OUT.mkdir(exist_ok=True);q=dict(passed=False,source_CPU=True,native=False,installed=False,code_overlay=False,shared_host_modified=False)
    bindings={str(p.resolve()):sha(p)for p in[Path(__file__),OUT/'baseline.json',COMPONENT/'result.json',BASE/'candidate.nes',BASE/'candidate.dbg',BASE/'character_select.s',BASE/'characters.s',BASE/'entrypoint.s',BASE/'candidate.cfg',BASE/'menu-input.inc',ROOT/'tools/reference/menu_input_1101_v3.inc',INSTALLED,ROOT/'tools/audit/check_hogan_current_bounded_v1.py',ROOT/'tools/audit/ff_wram_host_controls_v7.py',ROOT/'tools/audit/arthur_cache_host_controls_v1.py']}
    try:
        assert len(expected)==64 and sha(BASE/'candidate.nes')==expected
        baseline=json.loads((OUT/'baseline.json').read_text());component=json.loads((COMPONENT/'result.json').read_text())
        assert baseline['passed']and baseline['old_ROM_sha256']==OLD and component['passed']and component['base_ROM_sha256']==OLD
        b=H.C.qualified(BASE/'candidate.nes');raw=b['raw'];patches=component['layout']['patches'];exact=0
        assert(BASE/'menu-input.inc').read_bytes()==(ROOT/'tools/reference/menu_input_1101_v3.inc').read_bytes(),'Actual copied macro source differs'
        for p in patches:
            f=COMPONENT/({'EDGE':'edge','RETAIN':'retain','COLDHOOK':'coldhook','HELPER':'helper','COLD':'cold'}[p['segment']]+'.bin')
            data=f.read_bytes();assert hashlib.sha256(data).hexdigest()==p['after_sha256']
            assert raw[p['file_offset']:p['file_offset']+p['bytes']]==data,('Composed menu differs from qualified isolated bytes',p['segment'])
            bindings[str(f.resolve())]=sha(f);exact+=len(data)
        moved=[]
        for name,[pc,pos]in baseline['public'].items():
            if name not in b['syms']:moved.append([name,'missing']);continue
            now=address(b,name);newpos=location(b,name)if pos is not None else None
            if[pc,pos]!=[now,newpos]:moved.append([name,[pc,pos],[now,newpos]])
        assert not moved,('Old global/native PCs moved',moved[:20],len(moved))
        for name,pair in baseline['protected'].items():assert[address(b,name),location(b,name)]==pair,('Protected native caller moved',name)
        # Genuine installed ROM is a separate read-only original initializer
        # reference, not an overlay or a second generated ROM.
        installedraw=INSTALLED.read_bytes()
        expected_installed='be751275d00757ecaa51defcd2ccd5ea235921aa4b1f34337fa6c5c6e1877962'
        assert hashlib.sha256(installedraw).hexdigest()==expected_installed
        for name,skip,size in [('CrossoverInit',18,142),('NrGlobalInit',0,71)]:
            at=location(b,name);assert raw[at+skip:at+size]==installedraw[at+skip:at+size],('Existing native initializer body changed',name)
        old=copy.deepcopy(b);old['raw']=installedraw # both loaded ROMs remain their genuine complete emitted bytes
        calls=0;minimum=224;digest=hashlib.sha256()
        def invoke(m,name,**kw):
            nonlocal calls,minimum
            bank=m.rawtags[1];c=H.start(m,name,**kw);live=bytes(m[0x101+c.sp+2:0x200]);c,low=H.finish(m,c)
            calls+=1;minimum=min(minimum,low)
            assert c.sp==kw.get('sp',224)and bytes(m[0x101+c.sp:0x200])==live
            assert m.rawtags[1]==bank and H.get(m,'CurrentBank')==bank
            return c
        def fresh(bundle=b):
            m=C.fresh(bundle);H.put(m,CrossoverMenuState=0,CrossoverMenuButtons=0,CrossoverTitleDrawn=0,CrossoverOptionsFocus=0,CrossoverMenuIndex=0);return m
        def tick(m,p1=0,p2=0,mask=None,**kw):
            state=H.get(m,'CrossoverMenuState');H.put(m,SavedJoypad1Bits=p1,SavedJoypad2Bits=p2,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,Mirror_PPUMASK=(0 if state in[1,3,5,7]else 24)if mask is None else mask)
            return invoke(m,'CrossoverMenuInput',**kw)
        def tap(m,key,pad=1):
            z=tick(m,key if pad==1 else 0,key if pad==2 else 0);tick(m);return z
        def roster(m):
            tick(m);tick(m,16);assert H.get(m,'CrossoverMenuState')==1;tick(m);tick(m);assert H.get(m,'CrossoverMenuState')==2
        def snap(m):return tuple(H.get(m,n)for n in['CrossoverMenuState','CrossoverMenuIndex','SelectedCharacter','FmAlts','FmGroups','MarioVariant','CrossoverContinue'])
        vn=['MarioVariant','BillVariant','ProtoVariant','Z2Variant','Cv3Variant','DarkwingVariant','CdVariant','M3Variant','VvVariant','KbVariant','TnVariant','RlVariant','RcVariant','MacVariant','IcVariant'];vn=[n for n in vn if n in b['syms']]
        def variants(m):return tuple(H.get(m,n)for n in vn)+tuple(m[a]for a in[0x5fe3,0x5fee,0x5fef])
        # Actual complete native init body, with source-prescribed default0
        # folded variants, retains native output registers/bank context.
        initcases=0
        fields=['SelectedCharacter','BillVariant','MarioVariant','CrossoverMenuIndex','CrossoverMenuButtons','CrossoverTitleDrawn','CrossoverMenuState','CrossoverMenuPressed','CrossoverContinue','CheatInvincible','CheatStartLevel','CrossoverBehaviorVersion','PlayerOutlinesOff']
        for flags,pattern in itertools.product([0x30,0x31,0x71,0xf1],[0,90,255]):
            pair=[fresh(z)for z in[old,b]];results=[]
            for m in pair:H.put(m,FmAlts=pattern,FmGroups=pattern);results.append(invoke(m,'CrossoverInit',a=pattern,x=73,y=91,p=flags))
            ca,cb=results
            assert(ca.a,ca.x,ca.y,ca.p)==(cb.a,cb.x,cb.y,cb.p)and pair[0].rawtags==pair[1].rawtags
            assert all(H.get(pair[0],n)==H.get(pair[1],n)for n in fields)
            assert(H.get(pair[1],'FmAlts'),H.get(pair[1],'FmGroups'))==(0,0)
            initcases+=1
        normal=combined=deferred=reentries=0
        for pad,hard,outlines,continued,confirm in itertools.product([1,2],[0,1],[0,1],[0,128],[16,128]):
            m=fresh();H.put(m,CrossoverBehaviorVersion=hard,PlayerOutlinesOff=outlines);roster(m);H.put(m,CrossoverContinue=continued);tap(m,2,pad)
            assert H.get(m,'CrossoverMenuIndex')==7 and H.get(m,'SelectedCharacter')==7
            for simultaneous in[False,True]:
                n=C.fork(m)
                if not simultaneous:tap(n,32,pad)
                keys=(32 if simultaneous else 0)|confirm
                c=tick(n,keys if pad==1 else 0,keys if pad==2 else 0)
                assert H.get(n,'CrossoverMenuState')==0 and H.get(n,'SelectedCharacter')==34 and H.get(n,'FmAlts')&1
                assert H.get(n,'CrossoverContinue')==continued and c.a==continued|16
                if simultaneous:combined+=1
                else:normal+=1
            tap(m,32,pad);tap(m,64,pad);tick(m,16 if pad==1 else 0,16 if pad==2 else 0);tick(m);tick(m)
            assert H.get(m,'SelectedCharacter')==34 and H.get(m,'FmAlts')&1;reentries+=1
            for held,waits in itertools.product([False,True],[0,3]):
                n=C.fork(m);tap(n,64,pad);tick(n,16 if pad==1 else 0,16 if pad==2 else 0)
                for i in range(waits):tick(n,32 if pad==1 else 0,32 if pad==2 else 0,mask=24)
                tick(n,32 if pad==1 else 0,32 if pad==2 else 0)
                assert H.get(n,'CrossoverMenuState')==2
                keys=(32 if held else 0)|confirm;tick(n,keys if pad==1 else 0,keys if pad==2 else 0)
                assert H.get(n,'CrossoverMenuState')==0 and H.get(n,'SelectedCharacter')==7 and not H.get(n,'FmAlts')&1 and H.get(n,'CrossoverContinue')==0
                deferred+=1
        profiles=confirmcases=combinedcases=retained=0;ready=0
        for slot,total in enumerate(COUNTS):
            m=fresh();H.put(m,CrossoverMenuState=2,CrossoverMenuIndex=slot);invoke(m,'MenuResolveCharacter');invoke(m,'QueueSelection')
            for variant in range(total):
                if variant:tap(m,32)
                pending=bool(invoke(m,'FmPending').p&1);ready+=not pending
                for key in[16,128]:
                    n=C.fork(m);c=tick(n,key)
                    assert(H.get(n,'CrossoverMenuState')==0)!=pending,(slot,variant,key,pending,snap(n))
                    if not pending:assert c.a&16
                    confirmcases+=1
                    separate,simultaneous=C.fork(m),C.fork(m);tap(separate,32);tick(separate,key);tick(simultaneous,32|key)
                    assert snap(separate)==snap(simultaneous)and variants(separate)==variants(simultaneous),(slot,variant,key)
                    digest.update(bytes(snap(simultaneous)));combinedcases+=1
                n=C.fork(m);saved=snap(n)[1:6];v=variants(n);tap(n,64);tick(n,16);tick(n);tick(n)
                assert snap(n)[1:6]==saved and variants(n)==v,(slot,variant);retained+=1;profiles+=1
        assert profiles==90 and ready==86
        assert digest.hexdigest()==component['trace_sha256'],'Composed roster trace differs from isolated native proof'
        assert all(sha(p)==h for p,h in bindings.items()),'Read-only reference/candidate changed during check'
        q.update(passed=True,ROM_sha256=expected,actual_composed_code=True,overlay=False,isolated_proposal_emitted_bytes_exact=exact,old_global_native_address_locations_exact=len(baseline['public']),protected_menu_native_endpoints_exact=len(baseline['protected']),real_native_CrossoverInit_pairs=initcases,normal_Karnov_contexts=normal,simultaneous_Karnov_contexts=combined,deferred_BuildScreen_contexts=deferred,Karnov_B_title_reentry_contexts=reentries,identities=profiles,playable=ready,Start_A_cases=confirmcases,combined_equals_separate_cases=combinedcases,all_identity_title_reentries=retained,actual_native_calls=calls,minimum_standalone_SP=minimum,trace_sha256=digest.hexdigest(),scope='Actual compiled candidate and genuine installed original initializer ROM; no overlay, ROM/debug/source copy or shared writes. Exact107Bhelper,26Bwrapper and44Bhooks match isolated proof. All old public/native PCs and protected callers retained. Finite CPU control/init cases only; no Mesen/controller-device/raster/audio or Main+ISR stack qualification, complete gameplay or nightly installation claim.')
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']=bindings;(OUT/'result.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['bindings']}));assert q['passed'],q.get('error')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepare',action='store_true');p.add_argument('--expected');args=p.parse_args()
    if args.prepare:return prepare()
    assert args.expected,'Wait for root terminal hash; --expected is required'
    check(args.expected)
if __name__=='__main__':main()
