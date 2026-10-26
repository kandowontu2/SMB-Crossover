"""Prepare only one exact641 Easy discovery plus conditional independent replay."""
from pathlib import Path
import argparse,ast,copy,difflib,hashlib,json,re,shutil,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/audit'))
from check_tmnt_render_oa import load,address,location
from observe_chip_committed_write import lua
from mario_powerups_current3cee_static_v2 import runtime,symbols,chr_equivalence
from final_item_abilities_current731_prepare_v1 import protocol,dma_mocks
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
S=D/'luigi-mario-profile731-v3';I=D/'luigi-profile641-native-ready-v2'
H=D/'current3cee-remaining27-routes-v1/native/mario-easy'
ROM='641460e2646806c03fb98cf84f8a8c2e8de99c74dac8c5876c50f05ef1eb512c'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def get(p):return json.loads(Path(p).read_text())
def put(p,q):assert not p.exists(),p;p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')


def hook(b,name,size=3,delta=0):
    off=location(b,name)+delta;return dict(pc=address(b,name)+delta,bank=(off-16)//8192,bytes=list(b['raw'][off:off+size]))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
    frozen=I/'native-result-freeze-v1/proof.json';assert sha(frozen)=='d950a12be58aa7ec848d3e951186a00c81f84940178579ea79378efbefc58df3'
    old=get(frozen)
    for f,h in old['bindings'].items():assert sha(f)==h,f
    rom=S/'candidate.nes';assert sha(rom)==ROM;b=load(rom)
    env=get(I/'readiness.json')['environment']
    for n in ['emulator','core','worker_settings','user_settings']:assert sha(env[n])==env[n+'_sha256'],n
    # Exact old Mario controller body: it already routes both character0/8
    # through its Mario movement policy. Only the isolated guard path changes.
    body=(H/'policy.lua').read_text().split('\n',1)[1]
    assert 'if c.char==0 or c.char==8 then return mario(c)end' in body
    assert not re.search(r'\bemu\.(?:write\w*|setState|loadSavestate|reset)\s*\(',body)
    cfg=copy.deepcopy(get(H/'manifest.json')['config'])
    cfg.update(name='luigi',slot=0,character=8,variant=1,variantSymbol='MarioVariant',menuName='LUIGI',behavior='easy',limit=8000,capture=12)
    # All original module bodies are copied unchanged, including controller menu
    # and original committed body CHR observation with startup-static returns.
    hooks={
        'NmiEntry':hook(b,'NonMaskableInterrupt'),
        'NmiReturn':hook(b,'NonMaskableInterrupt',1,int(b['syms']['NonMaskableInterrupt']['size'],0)-1),
        'IrqEntry':hook(b,'IrqScrollSplit'),
        'IrqReturn':hook(b,'IrqScrollSplit',1,int(b['syms']['IrqScrollSplit']['size'],0)-1),
        'GameLoop':hook(b,'GameLoop'),
        'GameLoopReturn':hook(b,'GameLoop',1,int(b['syms']['GameLoop']['size'],0)-1),
        'DrawAll':hook(b,'DrawAllMetasprites'),
        'EnemyStomped':hook(b,'EnemyStomped')}
    assert all(hooks[n]['bytes']==[64]for n in ['NmiReturn','IrqReturn'])
    assert hooks['GameLoopReturn']['bytes']==[96]
    reference=get(D/'root-presentation450-731-v1/config.json')
    smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2]
    assert smc==reference['smc']
    observation=dict(ROM_sha256=ROM,dma_protocol=protocol(b),hooks=hooks,smc=smc,
                     literal_qualified_DMA_source=str(ROOT/'tools/audit/final_item_abilities_dma731_v1.lua'),
                     max_frames=8000,mode=0,character=8,variant=1)
    module=ROOT/'tools/audit/luigi_profile641_route_observer_v1.lua';dmatext=(ROOT/'tools/audit/final_item_abilities_dma731_v1.lua').read_text()
    marker='-- QUALIFIED_DMA_BODY';assert module.read_text().count(marker)==1
    supplement=module.read_text().replace(marker,dmatext)
    assert supplement.replace(dmatext,marker,1)==module.read_text()
    (out/'observer.lua').write_text(supplement,encoding='utf-8',newline='\n')
    profile=[];motions=[]
    motion_source=D/'current3cee-remaining27-routes-v1/native/native-guard.lua'
    motion_prefix=motion_source.read_text().split('local checks,maxWorld,maxCamera=',1)[0]
    # Existing public PCs/RAM unchanged; actual opcode/bank binding still checked.
    assert address(b,'GameLoop')+int(b['syms']['GameLoop']['size'],0)-1==33621
    for name in ['discovery','replay']:
        folder=out/name;folder.mkdir();(folder/'frames').mkdir()
        c=copy.deepcopy(cfg);c.update(out=folder.as_posix()+'/',policy=(folder/'policy.lua').as_posix(),audit=(folder/'audit.lua').as_posix(),replay=(out/'discovery/inputs.csv').as_posix()if name=='replay'else None,prefix=None)
        put(folder/'configuration.json',dict(roster=c,observation=observation))
        shutil.copyfile(H/'harness.lua',folder/'harness.lua')
        shutil.copyfile(I/'luigi-easy/audit.lua',folder/'audit.lua')
        assert sha(folder/'harness.lua')==sha(H/'harness.lua')
        guard=folder/'native-guard.lua';guard.write_bytes(motion_source.read_bytes())
        policy='dofile('+lua(guard.as_posix())+')\n'+body;(folder/'policy.lua').write_text(policy,encoding='utf-8',newline='\n')
        assert policy.split('\n',1)[1]==body
        text='ROSTER_CONFIG='+lua(c)+'\nLUIGI_ROUTE_OBSERVER='+lua(observation)+'\ndofile('+lua((out/'observer.lua').as_posix())+')\ndofile('+lua((folder/'harness.lua').as_posix())+')\nassert(MARIO_POWERUP_INSTALL_CHR_DISPATCHER)()\n'
        (folder/'run.lua').write_text(text,encoding='utf-8',newline='\n')
        command=[sys.executable,'-B',str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(folder),'--emulator',env['emulator'],str(folder/'run.lua'),str(rom),'--timeout','240']+['--option='+v for v in env['deterministic_command_overrides']]
        profile.append(dict(name=name,fixture=str(folder),command=command,conditional_on_discovery_pass=name=='replay',max_frames=8000,timeout_seconds=240))
    lua_root=D/'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1';sys.path.insert(0,str(lua_root));from lupa.lua54 import LuaRuntime
    labels,banks=symbols(b,rom);rt=runtime(LuaRuntime,labels,banks)
    rt.execute('emu.getScreenBuffer=function()local t={};for i=1,61440 do t[i]=0xff000000 end;return t end')
    rt.execute((out/'discovery/run.lua').read_text());count=rt.eval('#callbacks')
    assert rt.eval('callbacks[#callbacks].kind==2 and callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==65535')
    rt.execute("emu.addMemoryCallback=function()error('Runtime registration forbidden')end;emu.removeMemoryCallback=function()error('Runtime removal forbidden')end")
    for frame in range(1,25):
        rt.execute(f"state['ppu.frameCount']={frame};runevents(emu.eventType.inputPolled);runevents(emu.eventType.endFrame)")
    assert rt.eval('#callbacks')==count and rt.eval('inputCalls')==24
    mocks=dma_mocks(LuaRuntime,dmatext,dict(dma_protocol=observation['dma_protocol']))
    assert len(mocks)==13 and all(s['passed']for s in mocks)
    # Replay only changes output/policy/audit paths and the literal input source;
    # body/audit/harness/observer must remain exact. Its input file does not exist
    # before genuine discovery and will be sealed immediately before launch2.
    assert all(sha(out/'discovery'/n)==sha(out/'replay'/n)for n in ['harness.lua','audit.lua','native-guard.lua'])
    original_dynamic=D/'current3cee-remaining27-routes-v1/native/luigi-easy/audit.lua'
    chrproof=chr_equivalence(LuaRuntime,original_dynamic.read_text(),(out/'discovery/audit.lua').read_text(),labels,banks,8)
    controls=dict(passed=True,native_executed=False,actual_generated_discovery_loaded=True,startup_callbacks=count,
        last_startup_callback_is_fixed_broad_CHR_dispatcher=True,inactive_controller_fullPPU_mock_frames=24,runtime_registration_removal=0,
        original_policy_body_exact=True,original_harness_audit_byte_exact=True,qualified_DMA_body_literal_exact=True,DMA_model_cases=mocks,
        CHR_original_static_equivalence=chrproof,real_compiled_hooks=hooks,real_E008_complete=observation['dma_protocol'],
        replay_input_source_unknown_until_discovery=True,source_palette_movement_or_ROM_changes=False,
        scope='Complete generated startup, unchanged policy/source bodies and13 qualified DMA rejection mocks; synthetic API frames are not gameplay/NMI/timing/stomp proof.')
    put(out/'static-controls.json',controls)
    costs=D/'luigi-profile641-owned-cost-v1/freeze.json';cost=get(costs)
    for f,h in cost['bindings'].items():assert sha(f)==h,f
    files=set(Path(f)for f in old['bindings'])|{frozen,costs,Path(__file__),module,ROOT/'tools/audit/luigi_profile641_route_run_v1.py',ROOT/'tools/audit/final_item_abilities_dma731_v1.lua',ROOT/'tools/audit/final_item_abilities_current731_prepare_v1.py',original_dynamic,H/'policy.lua',H/'manifest.json',H/'stomp-events.csv',H/'stomp-summary.json',motion_source,D/'root-presentation450-731-v1/config.json'}
    files|={Path(f)for f in cost['bindings']}
    # Transitive local Python imports and exact Lua runtime native modules.
    pending=[Path(__file__),ROOT/'tools/audit/luigi_profile641_route_run_v1.py'];seen=set()
    while pending:
        f=pending.pop()
        if f in seen:continue
        seen.add(f);files.add(f)
        for node in ast.walk(ast.parse(f.read_text(encoding='utf-8-sig'))):
            mods=[node.module]if isinstance(node,ast.ImportFrom)else[z.name for z in node.names]if isinstance(node,ast.Import)else[]
            for n in mods:
                if n:
                    dep=ROOT/'tools/audit'/(n.split('.')[0]+'.py')
                    if dep.is_file():pending.append(dep)
    files|={Path(sys.executable),Path(sys.modules['lupa'].__file__),Path(sys.modules[LuaRuntime.__module__].__file__)}
    files|={f for f in out.rglob('*')if f.is_file()}
    bindings={str(f.resolve()):sha(f)for f in sorted(files,key=str)}
    readiness=dict(passed=True,status='PREPARE_DO_NOT_RUN',native_executed=False,native_grant=False,ROM_sha256=ROM,
        profiles=profile,maximum_launches=2,native_workers=1,automatic_retries=0,stop_first_failure=True,environment=env,bindings=bindings,
        ownership='Genuine Luigi8/MarioVariant1/Easy0; original Mario adaptive body already handles0/8. No controller changes/jump retuning or state writes.',
        replay='Launch2 only after real clear/zero deaths/ordinary stomp/CHR/motion/observer PASS; bind genuine discovery inputs and require byte-exact inputs/trace/result/PPU stream in independent replay.',
        target='Surface1-1 through genuine moving1-2 entry; physical first mushroom and any native acquired abilities are observed, not promised; existing two-item Easy/Hard evidence remains separate.',
        timing='Qualified E008 full256/per-write destination/mask/rawhardware/startFrame/scoped-enable body plus actual NMI/IRQ AXY/SP/fiveSMC/shadows; all-endFramePPU and update/draw/publication/deadline/ordinary-stomp observations. No pre-run pass claim.',
        source_owned_costs='20legal completeCPU pairs cost+411..1368cycles; finite CPU timing does not predict native cadence or prove a free change.')
    put(out/'readiness.json',readiness)
    put(out/'command.json',dict(not_executed=True,new_explicit_ROOT_grant_required=True,maximum_native_launches=2,command=[sys.executable,'-B',str(ROOT/'tools/audit/luigi_profile641_route_run_v1.py'),'--packet',str(out),'--expected-readiness-sha256',sha(out/'readiness.json'),'--native-grant']))
    print(json.dumps(dict(passed=True,native_executed=False,bindings=len(bindings),readiness_sha256=sha(out/'readiness.json'),command_sha256=sha(out/'command.json'),startup_callbacks=count),indent=2))


if __name__=='__main__':main()
