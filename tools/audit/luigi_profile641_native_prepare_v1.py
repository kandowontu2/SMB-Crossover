"""Prepare exactly two controller-only private Luigi-profile item components; never run Mesen."""
from pathlib import Path
import argparse
import copy
import difflib
import hashlib
import itertools
import json
import re
import shutil
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/audit'))
from check_tmnt_render_oa import load,address,location
from observe_chip_committed_write import lua
from mario_powerups_current3cee_static_v2 import runtime,symbols,chr_equivalence
from mario_flower900_prepare_v4 import controller_controls
from luigi_flower731_rg_prepare_v1 import trace_call
from luigi_mario_profile731_cpu_v1 import CURRENT
from mario_luigi731_coefficients_v1 import make,movement,coord
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
SOURCE=D/'luigi-mario-profile731-v3';OLD=D/'luigi-flower731-rg-owner-v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def get(p):return json.loads(Path(p).read_text())
def put(p,q):assert not p.exists();p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')


def arc_controls(b,mode):
    results=[]
    at=location(b,'BoundBoxCtrlData');body=list(b['raw'][at:at+4]);reward=list(b['raw'][at+36:at+40])
    assert body==[2,8,14,32] and reward==[3,14,13,20]
    for start,fraction in itertools.product(range(1288,1293),[0,0x5555,0xaaaa,0xffff]):
        q=make(b,8,mode);q.put(MarioSourceActive=1,Player_PageLoc=start//256,Player_X_Position=start%256,PlayerFacingDir=2,Player_MovingDir=2)
        q.array('MmXFraction',[fraction&255,fraction>>8]);path=[]
        for t in range(48):
            x=coord(q,'X');v=q.get('Player_X_Speed');v=v-256 if v>=128 else v
            direction=2 if x>1252 else 1 if x<1244 else 2 if v>1 else 1 if v< -1 else 0
            bits=194 if t==0 else (128 if t<32 else 0)+64+direction
            movement(q,bits);x=coord(q,'X');y=coord(q,'Y')-256
            overlap=x+body[0]<1248+reward[2] and x+body[2]>1248+reward[0] and y+body[1]<119+reward[3] and y+body[3]>119+reward[1]
            path.append(dict(update=t+1,x=x,y=y,vy=q.get('Player_Y_Speed'),flower_overlap=overlap,input=bits))
        first=next(z for z in path if z['flower_overlap']);landing=next(z for p,z in zip(path,path[1:])if p['y']<=112<z['y'] and z['vy']<128)
        assert first['update']<=38 and 1232<=landing['x']+3<1280
        assert min(z['y'] for z in path)>95
        results.append(dict(start=start,fraction=fraction,first_overlap=first,lower_row_descent=landing,path=path))
    return results


def mode_guard(LuaRuntime,folder,module,b,rom):
    cfg=get(folder/'configuration.json');labels,banks=symbols(b,rom);labels.update(cfg['item']['ram']);cases=[]
    for supplied in [cfg['item']['mode'],1-cfg['item']['mode']]:
        rt=runtime(LuaRuntime,labels,banks)
        rt.execute('ROSTER_CONFIG='+lua(cfg['roster'])+';MARIO_FLOWER_CONFIG='+lua(cfg['item']));rt.execute(module.read_text())
        rt.execute("emu.addMemoryCallback=function()error('Runtime registration forbidden')end;emu.removeMemoryCallback=function()error('Runtime removal forbidden')end")
        m=rt.globals().mem
        for n,v in dict(OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,SelectedCharacter=8,MarioVariant=1,CrossoverBehaviorVersion=supplied,PlayerStatus=0).items():m[labels[n]]=v
        try:rt.execute('runevents(emu.eventType.endFrame)')
        except Exception as e:
            assert supplied!=cfg['item']['mode'] and 'Real cold selected Luigi mode'in str(e)
            cases.append(dict(actual_numeric_mode=supplied,rejected=True))
        else:
            assert supplied==cfg['item']['mode'];cases.append(dict(actual_numeric_mode=supplied,admitted=True))
    return cases


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
    ready=SOURCE/'source-ready-v1/readiness.json';assert sha(ready)=='518556a39e0045bca8edebf5298420d0fc8ca6ee236d5eacf0b95dfcf55f2680'
    q=get(ready)
    for f,h in q['bindings'].items():assert sha(f)==h,f
    proof=OLD/'native-result-freeze-v1/proof.json';assert sha(proof)=='2db2a43bd8a1b87f951f1a1aa6c27e65ac682e1f88585f7e1355711d6369b551'
    prior=get(proof)
    for f,h in prior['bindings'].items():assert sha(f)==h,f
    rom=SOURCE/'candidate.nes';assert sha(rom)==CURRENT;b=load(rom)
    original=ROOT/'tools/audit/luigi_flower731_native_v2.lua';module=ROOT/'tools/audit/luigi_profile641_native_v1.lua'
    before=original.read_text();after=module.read_text()
    assert before.split('function MARIO_FLOWER_CONTROL(c,base)',1)[1].split('emu.addEventCallback',1)[0]==after.split('function MARIO_FLOWER_CONTROL(c,base)',1)[1].split('emu.addEventCallback',1)[0]
    assert before.split('function MARIO_FLOWER_RIGHT_CONTROL(c)',1)[1].split('function MARIO_FLOWER_CONTROL',1)[0]==after.split('function MARIO_FLOWER_RIGHT_CONTROL(c)',1)[1].split('function MARIO_FLOWER_CONTROL',1)[0]
    (out/'observer-mode-only.diff').write_text(''.join(difflib.unified_diff(before.splitlines(keepends=True),after.splitlines(keepends=True),fromfile=original.name,tofile=module.name)),encoding='utf-8',newline='\n')
    env=get(OLD/'readiness.json')['environment']
    for n in ['emulator','core','worker_settings','user_settings']:assert sha(env[n])==env[n+'_sha256'],n
    lua_root=D/'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1';sys.path.insert(0,str(lua_root));from lupa.lua54 import LuaRuntime
    profiles=[];components=[];parent=OLD/'luigi-easy'
    for mode,name in [(0,'luigi-easy'),(1,'luigi-hard')]:
        folder=out/name;folder.mkdir();(folder/'frames').mkdir()
        cfg=copy.deepcopy(get(parent/'configuration.json'));cfg['roster'].update(name='luigi',behavior='hard'if mode else'easy',out=folder.as_posix()+'/',policy=(folder/'policy.lua').as_posix(),audit=(folder/'audit.lua').as_posix())
        item=cfg['item'];item.update(mode=mode,ROM_sha256=CURRENT)
        for n in item['ram']:assert address(b,n)==item['ram'][n]
        for n,h in item['hooks'].items():
            at=16+h['bank']*8192+h['address']%8192;assert list(b['raw'][at:at+3])==h['bytes']
            if n not in ['RgAllocationStore','RgFireRequestStore']:assert address(b,n)==h['address']
        for n in ['policy.lua','harness.lua','audit.lua']:shutil.copyfile(parent/n,folder/n);assert sha(parent/n)==sha(folder/n)
        put(folder/'configuration.json',cfg)
        script='ROSTER_CONFIG='+lua(cfg['roster'])+'\nMARIO_FLOWER_CONFIG='+lua(item)+'\ndofile('+lua(module.as_posix())+')\ndofile('+lua((folder/'harness.lua').as_posix())+')\nassert(MARIO_POWERUP_INSTALL_CHR_DISPATCHER)()\n'
        (folder/'run.lua').write_text(script,encoding='utf-8',newline='\n')
        assert not re.search(r'\bemu\.(?:write\w*|setState|loadSavestate|reset)\s*\(',script+after+''.join((folder/n).read_text()for n in['policy.lua','harness.lua','audit.lua']))
        labels,banks=symbols(b,rom);labels.update(item['ram']);rt=runtime(LuaRuntime,labels,banks);rt.execute(script);count=rt.eval('#callbacks')
        rt.execute("emu.addMemoryCallback=function()error('Runtime registration forbidden')end;emu.removeMemoryCallback=function()error('Runtime removal forbidden')end")
        for frame in range(1,440):rt.execute("state['ppu.frameCount']="+str(frame)+";runevents(emu.eventType.inputPolled);runevents(emu.eventType.endFrame)")
        assert rt.eval('#callbacks')==count and rt.eval('inputCalls')==439
        original_dynamic=D/'current3cee-remaining27-routes-v1/native/luigi-easy/audit.lua'
        chrcheck=chr_equivalence(LuaRuntime,original_dynamic.read_text(),(folder/'audit.lua').read_text(),labels,banks,8)
        controller_controls(folder,module,b,rom,folder/'controller-controls')
        source=[]
        for power,kind in [(0,0),(1,1)]:
            z=Arena(b,8);z.put(CrossoverBehaviorVersion=mode,PlayerStatus=power,GuestPowerupActive=0);z.set('PowerUpType',kind,5)
            z.invoke('GuestBeginPowerup',x=5);assert z.get('GuestPowerupTarget')==power+1
            for age in range(60):assert z.get('GuestPowerupAge')==age;z.invoke('GuestPowerupUpdate')
            assert z.get('PlayerStatus')==power+1 and z.get('GuestPowerupActive')==0
            source.append(dict(power_before=power,authored_type=kind,target=power+1,actual_growth_calls=60))
        z=Arena(b,8);z.put(CrossoverBehaviorVersion=mode,PlayerStatus=2,SavedJoypadBits=64,A_B_Buttons=64,PreviousA_B_Buttons=0,RgPreviousButtons=0)
        stores=trace_call(z,'ProcFireball_Bubble');alloc=[r for r in stores if r['destination']==address(b,'RgShotType')+9 and r['value']==3]
        assert len(alloc)==1 and z.get('MmBulletType')==30
        component=dict(mode=mode,actual_compiled_growth=source,actual_fire_allocation=alloc,conditional_right_arc_cases=arc_controls(b,mode),
            numeric_cold_mode_controls=mode_guard(LuaRuntime,folder,module,b,rom),startup_mock_frames=439,startup_callbacks=count,
            runtime_callback_mutations=0,static_CHR_equivalence=chrcheck,not_native=True)
        put(folder/'source-controls.json',component);components.append(component)
        command=[sys.executable,'-B',str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(folder),'--emulator',env['emulator'],str(folder/'run.lua'),str(rom),'--timeout','180']+['--option='+v for v in env['deterministic_command_overrides']]
        profiles.append(dict(name=name,character=8,variant=1,mode=mode,fixture=str(folder),command=command,
            limit_physical_frames=6500,endpoint='Actual mushroom->flower,120growth,real Rg3 live enemy contact/source fire request,45neutral/all10slots empty'))
    deps=dict(q['bindings']);deps.update(prior['bindings'])
    for f in [ready,proof,Path(__file__),module,original,ROOT/'tools/audit/luigi_profile641_native_run_v1.py',ROOT/'docs/qa/luigi-profile641-native-preparation-2026-10-26.txt']:
        deps[str(f)]=sha(f)
    for f in out.rglob('*'):
        if f.is_file():deps[str(f)]=sha(f)
    result=dict(passed=True,status='PREPARE_DO_NOT_RUN',native_executed=False,native_grant=False,native_workers=1,
        ROM_sha256=CURRENT,parent_source_readiness_sha256=sha(ready),environment=env,profiles=profiles,
        stop_first_failure=True,automatic_retries=0,original_731_outcomes_immutable=True,
        gameplay_controller_and_semantic_guards_unchanged=True,numeric_modes_read_back=True,bindings=deps,
        scope='Two proposed natural-input finite components only. Conditional CPU trajectories and synthetic startup/owner mocks are not actual gameplay. No native/contact/PPU/art/audio/cadence/full1-1 adoption result.')
    put(out/'readiness.json',result)
    put(out/'command.json',dict(not_executed=True,explicit_new_ROOT_grant_required=True,command=[sys.executable,'-B',str(ROOT/'tools/audit/luigi_profile641_native_run_v1.py'),'--packet',str(out),'--expected-readiness-sha256',sha(out/'readiness.json'),'--native-grant']))
    print(json.dumps(dict(passed=True,native_executed=False,bindings=len(deps),readiness_sha256=sha(out/'readiness.json'),command_sha256=sha(out/'command.json')),indent=2))


from robots_weapon_cpu_v1 import Arena
if __name__=='__main__':main()
