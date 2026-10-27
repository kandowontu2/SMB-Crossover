"""ProtoHard14 on frozen ce635: identity-only fixture delta, no native launch."""
from pathlib import Path
import argparse, ast, copy, difflib, hashlib, json, shutil, sys
import final_megaproto_common_ce635_prepare_v1 as mega
import final_megaproto_common_ready_v5 as models
import final_megaproto_common_render_v3 as render
import final_megaproto_common_pharaoh_ready_v2 as release
from final_samus_hard_gallery_source_v1 import TraceArena, OWNER_NAMES
from final_item_abilities_remaining731_run_v1 import verify_manifest
from final_item_abilities_run import lua
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location
from parodius_visibility_hud_static_startup_v1 import MOCK

D,R,CAND,SHA=mega.D,mega.R,mega.CAND,mega.SHA
OLD=D/'currentce635-mega-common-ready-v1'
FINAL=D/'currentce635-mega-common-final-v1'
RUN=R/'tools/audit/final_megaproto_common_proto_ce635_run_v1.py'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def bind(p):return dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))

def actual_owner_cases(b):
    """Same complete native gateways and policies, with actual variant 1."""
    for n in ['SpecialWeapons','SpecialWeapons::MegaAttack','SpecialWeapons::Spawn',
              'MegaManSuperArmThrow','MegaManMovement','PlayerMovementSubs','InventoryUiTick']:
        if n not in OWNER_NAMES:OWNER_NAMES.append(n)
    rows=[]
    for face in [1,2]:
        for item,cost,typ in [(1,8,9),(2,4,10),(3,8,11),(4,4,12),(5,4,19),(6,4,15),(7,16,17)]:
            for kind in ['funded','underfunded','fullpool']:
                q=TraceArena(b)
                q.put(SelectedCharacter=1,ProtoVariant=1,CrossoverBehaviorVersion=1,
                      PlayerStatus=1,Player_X_Position=112,Player_PageLoc=0,
                      Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0,
                      ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=0,ScreenRight_PageLoc=0,
                      ScreenRight_X_Pos=255,PlayerFacingDir=face,TimerControl=0)
                q.set('InvOwnedLo',255,1);q.set('InvOwnedHi',0,1);q.set('InvSelected',item,1)
                stock=12 if item==4 and kind=='funded' else cost if kind=='funded' else cost-1 if kind=='underfunded' else 112
                q.set('InvAmmo',stock,16+item)
                col=(112+8+(10 if face==1 else -10))//16
                if item==1:q.set('Block_Buffer_1',0x51,160+col)
                if kind=='fullpool':
                    for i in range(10):
                        for n,v in [('RgShotType',10),('RgShotX',70+i*5),('RgShotPage',0),('RgShotY',72),('RgShotYHigh',1),('RgShotDir',face)]:q.set(n,v,i)
                def press(bits,move=False):
                    q.put(SavedJoypadBits=bits,SavedJoypad1Bits=bits,A_B_Buttons=bits&192,PreviousA_B_Buttons=0,InvPrevious=0)
                    q.invoke('RlUiDispatch')
                    if move:q.invoke('PlayerMovementSubs')
                    q.invoke('ProcFireball_Bubble')
                    assert q.get('ProtoVariant')==1
                press(132 if item==5 else 64,item==5)
                first=q.get('InvAmmo',16+item);types=[q.get('RgShotType',i)for i in range(10)]
                if item==1 and kind=='funded':
                    assert first==stock and q.get('SsHeld') and q.get('Block_Buffer_1',160+col)==0
                    press(0);press(64);assert q.get('SsHeld')==0
                expected=stock-(cost if kind=='funded' or kind=='fullpool' and item in [5,7] else 0)
                assert q.get('InvAmmo',16+item)==expected
                if kind=='funded':assert typ in types
                if kind=='underfunded':assert not any(types) and q.get('SsHeld')==0
                if kind=='fullpool':assert types==[10]*10
                if item==5:assert q.get('MmSliding')==1 and q.get('SsKick')==(2 if kind=='underfunded' else 1)
                names={z['owner']for c in q.calls for z in c['entries']}
                assert {'ProcFireball_Bubble','SpecialWeapons','InventoryUiTick'}<=names
                rows.append(dict(variant=1,face=face,item=item,kind=kind,before=stock,after=expected,calls=q.calls))
    cycles=[]
    for face in [1,2]:
        q=TraceArena(b);q.put(SelectedCharacter=1,ProtoVariant=1,CrossoverBehaviorVersion=1,PlayerFacingDir=face)
        q.set('InvOwnedLo',255,1);q.set('InvOwnedHi',0,1);choices=[]
        for item in [1,2,3,4,5,6,7,0]:q.invoke('InventoryCycle');choices.append(q.get('InvSelected',1))
        assert choices==[1,2,3,4,5,6,7,0] and q.get('ProtoVariant')==1
        cycles.append(dict(face=face,choices=choices,calls=q.calls))
    return dict(passed=True,variant=1,complete_owner_cells=len(rows),selection_cycles=cycles,rows=rows,source_only=True)

def variant_arena(base,counts):
    """Parameterize only the library's scene seed; execute original CPU code."""
    class ProtoArena(base):
        def put(self,**values):
            if values.get('SelectedCharacter')==1:
                values['ProtoVariant']=1
            return super().put(**values)
        def invoke(self,*args,**kwargs):
            robot=self.get('SelectedCharacter')==1
            if robot:assert self.get('ProtoVariant')==1
            result=super().invoke(*args,**kwargs)
            if robot:assert self.get('ProtoVariant')==1
            counts[args[0]]=counts.get(args[0],0)+1
            return result
    return ProtoArena

def menu_and_publication(b):
    for n in ['CrossoverMenuInput','QueueSelectName','PlayerGfxHandler','SamusFreezeDrawAll','DrawAllMetasprites','RosterOamReady']:
        assert n in b['syms']
        if n not in OWNER_NAMES:OWNER_NAMES.append(n)
    rows=[]
    for variant in [0,1]:
        q=TraceArena(b);q.put(SelectedCharacter=1,ProtoVariant=variant,CrossoverBehaviorVersion=1,
                            CrossoverMenuState=2,CrossoverMenuIndex=1,VRAM_Buffer1_Offset=0)
        q.invoke('QueueSelectName')
        data=[q.get('VRAM_Buffer1',i)for i in range(q.get('VRAM_Buffer1_Offset')+1)]
        assert data[:3]==[0x23,0x28,16] and data[-1]==0
        table=location(b,'QueueSelectName::Names')+16*(14 if variant else 1)
        assert data[3:19]==list(b['raw'][table:table+16])
        rows.append(dict(kind='actual-compiled-menu-name',variant=variant,queue=data,calls=q.calls))
    for before in [0,1]:
        q=TraceArena(b);q.put(SelectedCharacter=1,ProtoVariant=before,CrossoverBehaviorVersion=1,
                            CrossoverMenuState=2,CrossoverMenuIndex=1,CrossoverMenuButtons=0,
                            SavedJoypad1Bits=32,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0)
        q.invoke('CrossoverMenuInput');assert q.get('ProtoVariant')==1-before
        rows.append(dict(kind='actual-compiled-Select-toggle',before=before,after=q.get('ProtoVariant'),calls=q.calls))
    q=TraceArena(b);q.put(SelectedCharacter=1,ProtoVariant=1,PlayerStatus=1);q.set('InvOwnedLo',255,1);q.set('InvOwnedHi',0,1)
    q.invoke('PlayerGfxHandler');q.invoke('SamusFreezeDrawAll')
    assert q.get('ProtoVariant')==1 and q.get('GuestOamRotationActive')==1
    assert any(z['owner']=='RosterOamReady'for z in q.calls[-1]['entries'])
    rows.append(dict(kind='full-Proto-body-publication',rotation=1,calls=q.calls))
    return dict(passed=True,source_only=True,rows=rows,scope='Complete compiled menu/name/Select and PlayerGfx to rotated publication owners, not actual PPU or deadline evidence.')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--lua-root',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    assert sha(CAND/'candidate.nes')==SHA
    source_manifest=json.loads((CAND/'source-manifest.json').read_text());assert len(source_manifest)==871
    for n,h in source_manifest.items():assert sha(CAND/'source'/n)==h
    assert verify_manifest(OLD/'manifest.json')==1902;verify_manifest(FINAL/'manifest.json')
    oldcfg=json.loads((OLD/'native/config.json').read_text());b=scoped_load(CAND/'candidate.nes')
    cfg=mega.metadata(b,oldcfg);assert cfg==oldcfg
    cfg['identity']['variant']=1
    reverse=copy.deepcopy(cfg);reverse['identity']['variant']=0;assert reverse==oldcfg
    oldscript=(OLD/'native/run.lua').read_text();prefix='FINAL_ITEM_PROGRESSIVE='+lua(oldcfg)+'\n';assert oldscript.startswith(prefix)
    script='FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n'+oldscript[len(prefix):]
    assert script.split('\n',1)[1]==oldscript.split('\n',1)[1]
    assert not any(x in script for x in ["w('ProtoVariant'","w('SelectedCharacter'","w('CrossoverBehaviorVersion'","w('InvSelected'"])
    put(a.output/'identity-delta.json',dict(passed=True,deliberate_config_delta={'identity.variant':[0,1]},all_other_config_exact=True,body_after_prefix_literal=True,controller_mechanics_seeds_guards_and_finalizers_literal=True,mechanical_family='megaman',display_identity='Proto Man',old_script_sha256=sha(OLD/'native/run.lua')))
    put(a.output/'fresh-owner-controls.json',actual_owner_cases(b));put(a.output/'menu-publication-controls.json',menu_and_publication(b))
    render.SHA=release.SHA=SHA;release.B=CAND;counts={};saved_render=render.TraceArena;saved_release=release.ReleaseArena
    try:
        render.TraceArena=variant_arena(saved_render,counts);release.ReleaseArena=variant_arena(saved_release,counts)
        rendered=render.compiled(b,cfg);released=release.compiled(b)
    finally:render.TraceArena=saved_render;release.ReleaseArena=saved_release
    put(a.output/'fresh-render-controls.json',rendered);put(a.output/'fresh-release-controls.json',released)
    put(a.output/'compiled-variant-seeds.json',dict(passed=True,variant=1,only_library_input_override='SelectedCharacter1 scene seeds set ProtoVariant1; all complete actual gateways/branches/return logic unchanged.',actual_gateway_invocations=counts))
    sys.path.insert(0,str(a.lua_root));from lupa.lua54 import LuaRuntime
    previous=models.model_runtime;previous_release=release.model_runtime
    def runtime(LuaRuntime,body,config,bundle):
        suffix=''
        if config.get('identity',{}).get('variant')==1:
            suffix='''
function PROTO_CASE(k)PROTO_PRIOR_CASE(k);mem[L.ProtoVariant]=1 end
function PROTO_SETUP(k,kind)
 TEST_CASE(k);mem={};ppu={};writes={}
 mem[L.SelectedCharacter]=C.character;mem[L.CrossoverBehaviorVersion]=C.mode_value;mem[L.ProtoVariant]=1
 mem[L.InvSelected+C.character]=current.q.item;setup(kind)
 assert(mem[L.ProtoVariant]==1)
end
function TEST_MENU(v)
 wall=120;menuPhase='select';mem[L.CrossoverMenuState]=2;mem[L.CrossoverMenuIndex]=C.slot;mem[L.ProtoVariant]=v
 return menu()
end
function TEST_COLD(v,mode,selected)
 entered=false;done=false;phase='next';index=1;updates=0;age=0;wall=200
 mem[L.OperMode]=1;mem[L.OperMode_Task]=3;mem[L.GameEngineSubroutine]=8
 mem[L.SelectedCharacter]=selected;mem[L.ProtoVariant]=v;mem[L.CrossoverBehaviorVersion]=mode
 TEST_HOOK('GameLoop');return entered
end
'''
        # This suffix must share the generated script's lexical C/menu/setup
        # scope. The qualified base exports are installed later in that same
        # chunk; aliases below wrap them without redefining native callbacks.
        rt=previous(LuaRuntime,body+suffix,config,bundle)
        if suffix:rt.execute('PROTO_PRIOR_CASE=TEST_CASE;TEST_CASE=PROTO_CASE;TEST_SETUP=PROTO_SETUP')
        return rt
    try:
        models.model_runtime=release.model_runtime=runtime
        art=models.renderer_models(LuaRuntime,script,cfg,b,rendered)
        seeds=models.setup_models(LuaRuntime,script,cfg,b)
        fault=script.replace('local caseOwner=current;','local owner=current;').replace('current==caseOwner and','current==owner and')
        callbacks=release.callback_models(LuaRuntime,fault,script,cfg,b,released)
        rt=runtime(LuaRuntime,script,cfg,b)
        # Rejected readback intentionally enters the unchanged failure writer.
        # An empty host-model buffer lets its original assertion propagate;
        # no pixels are fabricated or counted as native/PPU evidence.
        rt.execute('emu.getScreenBuffer=function()return{}end')
        assert rt.globals().TEST_MENU(0)['select'] is True and rt.globals().TEST_MENU(1)['a'] is True
        bad=[]
        for v,mode,selected in [(0,1,1),(1,0,1),(1,1,9)]:
            message=None
            try:rt.globals().TEST_COLD(v,mode,selected);rejected=False
            except Exception as e:message=str(e);rejected='Cold-selected Bass and actual numeric mode' in message
            assert rejected,(v,mode,selected,message)
            bad.append(dict(variant=v,mode=mode,selected=selected,rejected=True,error=message))
        assert rt.globals().TEST_COLD(1,1,1) is True
    finally:models.model_runtime=previous;release.model_runtime=previous_release
    put(a.output/'fresh-Lua-controls.json',dict(passed=True,art=art,complete_setup=seeds,full_release_callback=callbacks,actual_menu_input=[{'variant':0,'select':True},{'variant':1,'a':True}],cold_readback_positive=True,cold_readback_negatives=bad))
    rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(MOCK+'\nL={};OUTPUT="mock/";emu.write=function()error("Startup mutation")end;emu.getScreenBuffer=function()local t={};for i=1,61440 do t[i]=0xff000000 end;return t end\n'+script)
    assert rt.eval('#callbacks')==74 and rt.eval('callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==65535')
    rt.execute('emu.addMemoryCallback=function()error("Runtime registration")end;emu.removeMemoryCallback=function()error("Runtime removal")end')
    for frame in [1,2,3]:rt.execute(f"state['ppu.frameCount']={frame};runevents(emu.eventType.startFrame);runevents(emu.eventType.endFrame)")
    assert rt.eval('#callbacks')==74
    oldrunner=(R/'tools/audit/final_megaproto_common_ce635_run_v1.py').read_text();runner=RUN.read_text();normalized=runner.replace('ProtoHard14','MegaHard14').replace('proto-hard-common','mega-hard-common').replace("cfg['identity']['variant']==1","cfg['identity']['variant']==0")
    assert normalized==oldrunner
    (a.output/'runner.patch').write_text(''.join(difflib.unified_diff(oldrunner.splitlines(True),runner.splitlines(True),fromfile='ce635-MegaHard14-runner',tofile='ce635-ProtoHard14-runner')),encoding='utf-8')
    put(a.output/'literal-invariants.json',dict(passed=True,runner_delta='Docstring/profile tag and required variant1 only; all collector predicates, ordered witness helper, caps/guards and launch mechanics unchanged.',reverse_exact=True,static_callbacks=74,dispatcher_last=True,three_inactive_frames=True,compiled_case_plans=cfg['cases'],all_prior_Mega_native_hashes_preserved=True))
    out=a.output/'native';out.mkdir()
    for ext in ['nes','dbg','lbl','map']:shutil.copy2(CAND/('candidate.'+ext),out/('candidate.'+ext))
    put(out/'config.json',cfg);(out/'run.lua').write_text(script,encoding='utf-8');shutil.copy2(OLD/'native/inherited-NMI-stack-APU-guards.lua',out/'inherited-NMI-stack-APU-guards.lua')
    assert sha(out/'inherited-NMI-stack-APU-guards.lua')=='6ab7cd71f41f441f4d4d752e2412f83c2b16da06b9e10d3cdf05180c63bf5fdf'
    env=copy.deepcopy(json.loads((OLD/'environment.json').read_text()));runtime_dir=a.output/'emulator';runtime_dir.mkdir()
    for q in Path(env['emulator']).parent.iterdir():
        if q.is_file():shutil.copy2(q,runtime_dir/q.name)
    env['emulator']=str(runtime_dir/'Mesen.exe');env['user_context_sha256']=sha('C:/Mesen2/settings.json')
    for name,key in [('Mesen.exe','emulator_sha256'),('MesenCore.dll','core_sha256'),('settings.json','worker_settings_sha256')]:assert sha(runtime_dir/name)==env[key]
    put(a.output/'environment.json',env);put(a.output/'plans.json',cfg['cases'])
    files={Path(q['path'])for q in json.loads((OLD/'manifest.json').read_text())['bindings']}
    files.update(CAND/'source'/n for n in source_manifest)
    files.update({CAND/'proof.json',CAND/'source-manifest.json',OLD/'proof.json',OLD/'manifest.json',FINAL/'proof.json',FINAL/'manifest.json',RUN,Path(__file__),Path('C:/Mesen2/settings.json'),Path(sys.executable),Path(sys.modules[LuaRuntime.__module__].__file__)})
    pending=[Path(__file__),RUN];seen=set()
    while pending:
        q=pending.pop()
        if q in seen:continue
        seen.add(q);files.add(q)
        for node in ast.walk(ast.parse(q.read_text(encoding='utf-8-sig'))):
            names=[node.module]if isinstance(node,ast.ImportFrom)else[z.name for z in node.names]if isinstance(node,ast.Import)else[]
            for name in names:
                dep=R/'tools/audit'/((name or '').split('.')[0]+'.py')
                if name and dep.is_file():pending.append(dep)
    files.update(q for q in a.output.rglob('*')if q.is_file());put(a.output/'manifest.json',dict(bindings=[bind(q)for q in sorted(files,key=str)]));count=verify_manifest(a.output/'manifest.json')
    command='python -B tools/audit/final_megaproto_common_proto_ce635_run_v1.py --ready "'+a.output.as_posix()+'" --native-grant'
    put(a.output/'proof.json',dict(prepared=True,native_run=False,native_granted=False,profile_local_OAM_encoding='attributeE3-v2',ROM_sha256=SHA,profile='proto-hard-common',mode_value=1,variant=1,maximum_cases=14,maximum_launches=1,maximum_owned_workers=1,retry=False,automatic_other_profiles=False,manifest_sha256=sha(a.output/'manifest.json'),bindings=count,output=str(out),script_sha256=sha(out/'run.lua'),environment=env,stable_command=command,lane='B',acquisition=False,all_prior_FALSEs_preserved=True,Mega_native_proof=bind(FINAL/'proof.json')))
    print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=count,script_sha256=sha(out/'run.lua'),stable_command=command),indent=2))
if __name__=='__main__':main()
