"""Two-line case-table rename with actual compiled ReleaseBalloon callback models."""
from pathlib import Path
import argparse, ast, copy, difflib, hashlib, json, re, shutil, sys
from final_megaproto_common_source_v2 import D, R, B, SHA
from final_megaproto_common_ready_v5 import model_runtime
from final_samus_hard_gallery_source_v1 import TraceArena, OWNER_NAMES
from final_item_abilities_remaining731_run_v1 import verify_manifest
from check_tmnt_render_oa import address, location
from link_pit_rygar_sophia_audit_cpu import scoped_load
from verify_native_relocation import NesMPU
from parodius_visibility_hud_static_startup_v1 import MOCK
OLD=D/'current0a-mega-common-oam-ready-v2'
NEG=D/'current0a-mega-common-pharaoh-negative-final-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def bind(p):return dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))

class ReleaseArena(TraceArena):
    """Full actual gateways, plus read-only snapshots at genuine release endpoints."""
    def snapshot(self,c):
        fields=['InvSelected','SsSelected','RgSlot','StarInvincibleTimer','InvDirty']
        return dict(cpu={n:getattr(c,n)for n in['a','x','y','p','sp','pc']},banks=list(self.m.banks),stock=self.get('InvAmmo',20),selected=self.get('InvSelected',1),fields={n:self.get(n)for n in fields},types=[self.get('RgShotType',i)for i in range(10)],ages=[self.get('RgShotAge',i)for i in range(10)],stack=[self.m[0x100+i]for i in range(256)])
    def invoke(self,name,a=0,x=0,y=0):
        b=self.b;at=address(b,name);bank=(location(b,name)-16)//8192;w=(at-0x8000)//8192;self.m.page(w,bank)
        if w in[1,2]:self.set('CurrentBank'if w==1 else'CurrentBankC',bank|128)
        c=NesMPU(memory=self.m,pc=at);c.a,c.x,c.y,c.p,c.sp=a,x,y,0x30,0xfd;c.stPushWord(0x5aff);self.m.writes=[];trace=[];entries=[];pending=[];returns=[]
        wanted={(address(b,n),(location(b,n)-16)//8192):n for n in OWNER_NAMES if n in b['syms']}
        for _ in range(200000):
            physical=self.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
            for q in list(pending):
                if(c.pc,physical,c.sp)==(q['return_pc'],q['return_bank'],q['return_sp']):
                    pending.remove(q);z=dict(**q,returned_a=c.a,returned_x=c.x,returned_y=c.y,returned_p=c.p)
                    if q['owner']=='SpecialWeapons::ReleaseBalloon':z['snapshot']=self.snapshot(c)
                    returns.append(z)
            if c.pc==0x5b00:
                assert c.sp==0xfd and not pending
                self.calls.append(dict(gateway=name,cycles=c.processorCycles,entries=entries,returns=returns,returned=dict(a=c.a,x=c.x,y=c.y,p=c.p,sp=c.sp)));return c,trace
            n=wanted.get((c.pc,physical))
            if n:
                ret=(self.m[0x100+((c.sp+1)&255)]+256*self.m[0x100+((c.sp+2)&255)]+1)&65535;rb=self.m.banks[(ret-0x8000)//8192]if ret>=0x8000 else-1
                q=dict(owner=n,entry_pc=c.pc,entry_bank=physical,entry_sp=c.sp,return_pc=ret,return_bank=rb,return_sp=(c.sp+2)&255)
                if n=='SpecialWeapons::ReleaseBalloon':q['snapshot']=self.snapshot(c)
                entries.append(q);pending.append(q)
            pc=c.pc;before=len(self.m.writes);c.step();trace.extend(dict(pc=pc,bank=physical,address=p,value=v)for p,v in self.m.writes[before:])
        raise AssertionError(('full gateway timeout',name,hex(c.pc)))

def compiled(b):
    for n in['SpecialWeapons','SpecialWeapons::Motion','SpecialWeapons::ReleaseBalloon','InventoryIndex']:
        if n not in OWNER_NAMES:OWNER_NAMES.append(n)
    cases=[]
    # Both facings/actual slots9,0; named boundary/stock/count/star branches.
    plan=[(63,s,1,0)for s in[0,4,8,12,112]]+[(44,8,1,0),(45,8,1,0),(45,8,2,0),(63,8,2,0),(63,8,1,1)]
    for face,slot in[(1,9),(2,0)]:
        for effective_age,stock,count,star in plan:
            q=ReleaseArena(b);q.put(SelectedCharacter=1,ProtoVariant=0,CrossoverBehaviorVersion=1,PlayerStatus=1,Player_X_Position=112,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0,ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=0,ScreenRight_PageLoc=0,ScreenRight_X_Pos=255,PlayerFacingDir=face,TimerControl=0,StarInvincibleTimer=star,SavedJoypadBits=0,SavedJoypad1Bits=0,A_B_Buttons=0,PreviousA_B_Buttons=0,InvPrevious=0)
            q.set('InvOwnedLo',255,1);q.set('InvOwnedHi',0,1);q.set('InvSelected',4,1);q.set('InvAmmo',stock,20)
            for n,v in[('RgShotType',18),('RgShotAge',effective_age-1),('RgShotDir',face),('RgShotX',120),('RgShotPage',0),('RgShotY',167),('RgShotYHigh',1)]:q.set(n,v,slot)
            if count==2:
                extra=8 if slot==9 else 1
                for n,v in[('RgShotType',10),('RgShotDir',face),('RgShotX',70),('RgShotPage',0),('RgShotY',100),('RgShotYHigh',1)]:q.set(n,v,extra)
            q.invoke('RlUiDispatch');q.invoke('ProcFireball_Bubble');call=q.calls[-1];entry=next(z for z in call['entries']if z['owner']=='SpecialWeapons::ReleaseBalloon');ret=next(z for z in call['returns']if z['owner']=='SpecialWeapons::ReleaseBalloon')
            es=entry['snapshot'];rs=ret['snapshot'];assert es['cpu']['x']==es['fields']['RgSlot']==slot and es['ages'][slot]==effective_age and es['selected']==es['fields']['SsSelected']==4 and sum(t!=0 for t in es['types'])==count and es['stock']==stock
            expected=max(0,stock-8)if effective_age>=45 and count<2 and not star else stock;assert rs['stock']==q.get('InvAmmo',20)==expected
            assert es['fields']['StarInvincibleTimer']==rs['fields']['StarInvincibleTimer']==star
            got={z['owner']for z in call['entries']};assert{'ProcFireball_Bubble','SpecialWeapons','SpecialWeapons::Motion','SpecialWeapons::ReleaseBalloon'}<=got
            assert entry['return_pc']==ret['return_pc']and entry['return_sp']==ret['return_sp']and entry['return_bank']==ret['return_bank']==60
            off=16+60*8192+(ret['return_pc']-3)%8192;assert b['raw'][off:off+3]==bytes([0x20,address(b,'SpecialWeapons::Motion')&255,address(b,'SpecialWeapons::Motion')>>8])
            cases.append(dict(face=face,slot=slot,effective_age=effective_age,before=stock,count=count,star=star,after=expected,entry=entry,returned=ret,gateway_calls=q.calls))
    return dict(passed=True,source_only=True,ROM_sha256=SHA,complete_UI_Proc_Motion_Release_cases=len(cases),cases=cases,scope='Declared legal source states and real assembled full gateways. Actual entry age/count/slot/banks/stack and complete native return stock drive Lua callback models; not a native acquisition/use result.')

EXTRA='''
function TEST_RELEASE_CASE(k)
 TEST_CASE(k);current.component='funded';current.beforeStock=0
end
function TEST_RELEASE_RESULT()
 return current.nativeSpent,current.zeroWitness~=nil
end
function TEST_SWAP_CASE()local previous=current;current={q=previous.q,component='funded',nativeSpent=0,nativeCredits=0};return previous end
'''

def callback_models(LuaRuntime,before,after,cfg,b,cpu):
    rows=[]
    def start(script,z):
        rt=model_runtime(LuaRuntime,script+EXTRA,cfg,b);rt.globals().TEST_RELEASE_CASE(7 if z['face']==1 else 8);rt.execute('emu.write=function()error("Observer write")end;emu.addMemoryCallback=function()error("Runtime registration")end;emu.removeMemoryCallback=function()error("Runtime removal")end')
        s=z['entry']['snapshot'];mem=rt.globals().mem;state=rt.globals().state
        for n,v in s['cpu'].items():state['cpu.'+n]=v
        rt.globals().BANKA=s['banks'][1];rt.globals().CB=s['banks'][2]
        for i,v in enumerate(s['stack']):mem[256+i]=v
        mem[cfg['ram']['InvSelected']+1]=s['selected'];mem[cfg['ram']['InvAmmo']+20]=s['stock']
        for n,v in s['fields'].items():
            if n!='InvSelected':mem[cfg['ram'][n]]=v
        for i,v in enumerate(s['types']):mem[cfg['ram']['RgShotType']+i]=v
        for i,v in enumerate(s['ages']):mem[cfg['ram']['RgShotAge']+i]=v
        return rt
    def enter(rt):rt.globals().TEST_HOOK('SpecialWeapons::ReleaseBalloon')
    def endpoint(rt,z,delta_sp=0,delta_pc=0,wrong_bank=False):
        s=z['returned']['snapshot'];rt.globals().mem[cfg['ram']['InvAmmo']+20]=s['stock'];rt.globals().BANKA=z['returned']['return_bank']^(1 if wrong_bank else 0);rt.globals().TEST_RETURN(z['returned']['return_pc']+delta_pc,(z['returned']['return_sp']+delta_sp)%256)
    def expect_error(name,fn,needle=None):
        try:fn();error=None
        except Exception as e:error=str(e)
        assert error is not None and(needle is None or needle in error),(name,error);rows.append(dict(kind=name,expected='reject',passed=True,error=error))
    base=next(z for z in cpu['cases']if z['face']==1 and z['before']==8 and z['effective_age']==63 and z['count']==1 and z['star']==0)
    old=start(before,base);expect_error('reproduce_original_exact_table_call',lambda:enter(old),"attempt to call a table value (local 'owner')")
    for z in cpu['cases']:
        rt=start(after,z);count=rt.eval('#callbacks');enter(rt);endpoint(rt,z);spent,zero=rt.globals().TEST_RELEASE_RESULT();assert spent==z['before']-z['after']and zero==(z['before']>0 and z['after']==0);assert rt.eval('#callbacks')==count
        # The registered static slot is consumed, never a second fake debit.
        endpoint(rt,z);assert rt.globals().TEST_RELEASE_RESULT()==(spent,zero)
        rows.append(dict(kind='actual_compiled_entry_and_return',face=z['face'],slot=z['slot'],age=z['effective_age'],before=z['before'],count=z['count'],star=z['star'],after=z['after'],observed_spent=spent,zero=zero,passed=True))
    for kind in['wrong-selected-owner','wrong-selected-item','wrong-native-slot']:
        rt=start(after,base)
        if kind=='wrong-selected-owner':rt.globals().mem[cfg['ram']['InvSelected']+1]=0;rt.globals().mem[cfg['ram']['InvSelected']+9]=4
        if kind=='wrong-selected-item':rt.globals().mem[cfg['ram']['SsSelected']]=3
        if kind=='wrong-native-slot':rt.globals().mem[cfg['ram']['RgSlot']]=8
        expect_error(kind,lambda:enter(rt),'Real selected Pharaoh release owner/slot')
    for kind in['wrong-current-case','changed-star','wrong-stock-return']:
        rt=start(after,base);enter(rt)
        if kind=='wrong-current-case':rt.globals().TEST_SWAP_CASE()
        if kind=='changed-star':rt.globals().mem[cfg['ram']['StarInvincibleTimer']]=1
        if kind=='wrong-stock-return':
            rt.globals().mem[cfg['ram']['InvAmmo']+20]=1;rt.globals().TEST_RETURN(base['returned']['return_pc'],base['returned']['return_sp']) if False else None
            expect_error(kind,lambda:rt.globals().TEST_RETURN(base['returned']['return_pc'],base['returned']['return_sp']),'direct eight-unit/clamp');continue
        expect_error(kind,lambda:endpoint(rt,base),'Same finite release owner')
    for kind,kw in[('wrong-return-SP',dict(delta_sp=1)),('wrong-return-PC',dict(delta_pc=1)),('wrong-return-bank',dict(wrong_bank=True))]:
        rt=start(after,base);enter(rt);endpoint(rt,base,**kw);assert rt.globals().TEST_RELEASE_RESULT()==(0,False);endpoint(rt,base);assert rt.globals().TEST_RELEASE_RESULT()==(8,True);rows.append(dict(kind=kind,expected='defer until genuine endpoint',passed=True))
    rt=start(after,base);rt.globals().BANKA=59;enter(rt);endpoint(rt,base);assert rt.globals().TEST_RELEASE_RESULT()==(0,False);rows.append(dict(kind='wrong-entry-bank-does-not-admit',passed=True))
    return dict(passed=True,models=len(rows),rows=rows,complete_real_source_cases=20,original_fault_reproduced=True,actual_generated_hook_and_static_dispatcher=True,no_observer_emulated_writes=True,no_runtime_registration=True)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--lua-root',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    assert verify_manifest(OLD/'manifest.json')==967;verify_manifest(NEG/'manifest.json');oldproof=json.loads((OLD/'proof.json').read_text());old=OLD/'native';cfg=json.loads((old/'config.json').read_text());before=(old/'run.lua').read_text()
    start=before.index("hook('SpecialWeapons::ReleaseBalloon',function()");end=before.index('\nlocal function clearArena()',start);part=before[start:end];assert part.count('local owner=current;')==1 and part.count('current==owner and')==1
    replacement=part.replace('local owner=current;','local caseOwner=current;').replace('current==owner and','current==caseOwner and');after=before[:start]+replacement+before[end:];assert after.replace(replacement,part)==before
    (a.output/'observer.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='frozen-E3-native-Lua-error',tofile='PHARAOH-case-capture-rename')),encoding='utf-8')
    # Specific introduced-helper audit, not a claimed general Lua parser.
    assert len(re.findall(r'local function owner\(',after))==1 and len(re.findall(r'local owner=',after))==1
    assert len(re.findall(r'local function ammoIndex\(',after))==1 and not re.search(r'local ammoIndex[=, ]|function\([^)]*\bammoIndex\b',after)
    refill=after[after.index("hook('InventoryUiTick',function()"):after.index('-- Read-only full real ReleaseBalloon owner.')];assert 'local owner=current'in refill and 'owner()'not in refill
    assert after.count('local caseOwner=')==1 and after.count('current==caseOwner and')==1
    put(a.output/'helper-name-audit.json',dict(passed=True,helpers=['owner','ammoIndex'],original_conflict='PHARAOH local owner table shadows introduced owner() helper',corrected_capture='caseOwner',remaining_owner_capture='InventoryUiTick closure contains no owner() call; fundedCredit is lexically defined outside that capture.',source_contexts=dict(refill=refill,release=replacement),scope='Exact two introduced helper names and their literal binding/reference sites in this frozen script, plus compiled Lua models; not universal lexical analysis.'))
    b=scoped_load(B/'candidate.nes');assert sha(B/'candidate.nes')==SHA;cpu=compiled(b);put(a.output/'compiled-full-release-controls.json',cpu)
    sys.path.insert(0,str(a.lua_root));from lupa.lua54 import LuaRuntime
    models=callback_models(LuaRuntime,before,after,cfg,b,cpu);put(a.output/'actual-callback-models.json',models)
    rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(MOCK+'\nL={};OUTPUT="mock/";emu.write=function()error("Startup mutation")end;emu.getScreenBuffer=function()local t={};for i=1,61440 do t[i]=0xff000000 end;return t end\n'+after);count=rt.eval('#callbacks');assert count==74 and rt.eval('callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==65535');rt.execute('emu.addMemoryCallback=function()error("Runtime registration")end;emu.removeMemoryCallback=function()error("Runtime removal")end')
    for frame in[1,2,3]:rt.execute(f"state['ppu.frameCount']={frame};runevents(emu.eventType.startFrame);runevents(emu.eventType.endFrame)")
    assert rt.eval('#callbacks')==count
    put(a.output/'invariants.json',dict(passed=True,two_line_local_capture_only=True,reverse_normalization_exact=True,all_config_controller_seeds_caps_guards_raw_DMA_E3_art_HUD_mechanics_identical=True,ROM_sha256=SHA,old_script_sha256=sha(old/'run.lua'),new_script_sha256=hashlib.sha256(after.encode()).hexdigest(),fixed_callbacks=74,dispatcher_last=True,three_inactive_frames=True,original_negative_proof_sha256=sha(NEG/'proof.json')))
    out=a.output/'native';out.mkdir()
    for ext in['nes','dbg','lbl','map']:shutil.copy2(old/('candidate.'+ext),out/('candidate.'+ext))
    shutil.copy2(old/'config.json',out/'config.json');shutil.copy2(old/'inherited-NMI-stack-APU-guards.lua',out/'inherited-NMI-stack-APU-guards.lua');(out/'run.lua').write_text(after,encoding='utf-8');assert sha(out/'candidate.nes')==SHA
    env=copy.deepcopy(oldproof['environment']);runtime=a.output/'emulator';runtime.mkdir()
    for q in Path(env['emulator']).parent.iterdir():
        if q.is_file():shutil.copy2(q,runtime/q.name)
    env['emulator']=str(runtime/'Mesen.exe');env['user_context_sha256']=sha(Path('C:/Mesen2/settings.json'));assert sha(runtime/'Mesen.exe')==env['emulator_sha256']and sha(runtime/'MesenCore.dll')==env['core_sha256']and sha(runtime/'settings.json')==env['worker_settings_sha256'];put(a.output/'environment.json',env);put(a.output/'plans.json',cfg['cases'])
    files={Path(z['path'])for z in json.loads((OLD/'manifest.json').read_text())['bindings']}|{OLD/'proof.json',OLD/'manifest.json',OLD/'ROOT-grant.json',NEG/'proof.json',NEG/'manifest.json',Path(__file__),Path('C:/Mesen2/settings.json'),Path(sys.executable),Path(sys.modules[LuaRuntime.__module__].__file__)}
    pending=[Path(__file__)];seen=set()
    while pending:
        q=pending.pop()
        if q in seen:continue
        seen.add(q);files.add(q)
        for node in ast.walk(ast.parse(q.read_text(encoding='utf-8-sig'))):
            names=[node.module]if isinstance(node,ast.ImportFrom)else[z.name for z in node.names]if isinstance(node,ast.Import)else[]
            for name in names:
                if name:
                    dep=R/'tools/audit'/(name.split('.')[0]+'.py')
                    if dep.is_file():pending.append(dep)
    files.update(q for q in a.output.rglob('*')if q.is_file());put(a.output/'manifest.json',dict(bindings=[bind(q)for q in sorted(files,key=str)]));bindings=verify_manifest(a.output/'manifest.json');command='python -B tools/audit/final_megaproto_common_oam_run_v1.py --ready "'+a.output.as_posix()+'" --native-grant'
    put(a.output/'proof.json',dict(prepared=True,native_run=False,native_granted=False,profile_local_OAM_encoding='attributeE3-v2',ROM_sha256=SHA,profile='mega-hard-common',mode_value=1,variant=0,maximum_cases=14,maximum_launches=1,maximum_owned_workers=1,retry=False,automatic_other_profiles=False,manifest_sha256=sha(a.output/'manifest.json'),bindings=bindings,output=str(out),script_sha256=sha(out/'run.lua'),environment=env,stable_command=command,source_controls_sha256=sha(a.output/'actual-callback-models.json'),lane='B',acquisition=False,original_FALSEs_preserved=True))
    print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=bindings,script_sha256=sha(out/'run.lua'),compiled_cases=20,callback_models=models['models'],stable_command=command),indent=2))
if __name__=='__main__':main()
