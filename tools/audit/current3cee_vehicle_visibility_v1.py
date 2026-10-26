"""Prepare/run two read-only exact-input vehicle attribution replays."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,re,sys,subprocess
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
SHA='3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99'
sys.path.insert(0,str(ROOT/'tools/audit'))
from check_tmnt_render_oa import load,address,location
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def get(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def lua(v):
 if isinstance(v,str):return json.dumps(v)
 if isinstance(v,bool):return 'true'if v else'false'
 if isinstance(v,(int,float)):return str(v)
 if isinstance(v,list):return'{'+','.join(lua(x)for x in v)+'}'
 return'{'+','.join('['+lua(k)+']='+lua(x)for k,x in v.items())+'}'
COMMON=['SelectedCharacter','CrossoverBehaviorVersion','OperMode','OperMode_Task','GameEngineSubroutine','FrameCounter','PlayerFacingDir','Player_X_Position','Player_PageLoc','Player_Rel_XPos','Player_Y_Position','Player_Y_HighPos','Player_State','PlayerStatus','PlayerOutlinesOff','ObjectMetasprite','ObjectVerticalFlip','SavedJoypadBits','ScreenLeft_X_Pos','ScreenLeft_PageLoc','GuestHurtTicks','GuestInvulTicks','GuestHurtVisible','GuestFlickerPhase','InjuryTimer','GuestPowerupActive','MmDeathFlag','RgPose','RgCrouch','RgAttack','RgAttackAge','RgShootPose','RgOamPlayerStart','RgOamRotation','RgOamFirst','RgOamUsed','GuestOamRotationActive','CurrentOAMOffset','SmChrBank','CurrentBank','CurrentBankC']
OCT=['VvVariant','VvHurt','VvShield','PnFrame','PnDrawFlags','PnPool','PnContact','PnPhase','PnPunch','PnBigStage','PnBigTimerHi','PnBigTimerLo','PnActive','PnX','PnY','VvDrawFirst','PnAutoFireAge']
SOPHIA=['XgWall','XgCeiling','XgHoverActive','XgJumpUsed','XgWalkTick','XgWalkPhase','XgWalkDirection','AvBombHurt','XgIndex']
def prepare(a):
 out=a.packet.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
 parent=D/'current3cee-remaining27-routes-v1';candidate=D/'root-chip-hud-composed-v1';rom=candidate/'candidate.nes';capture=parent/'capture.py';assert sha(rom)==SHA
 inherited=get(parent/'readiness.json')['bindings'];assert all(sha(p)==h for p,h in inherited.items())
 bundle=load(rom);observer=ROOT/'tools/audit/current3cee_vehicle_visibility_v1.lua';text=observer.read_text();assert not re.search(r'\bemu\.(?:write\w*|setState|loadSavestate|reset)\s*\(',text)
 sys.path.insert(0,str(a.parser_root));from luaparser import ast;ast.parse(text)
 (out/'observer.lua').write_bytes(observer.read_bytes());hooks={}
 for n in['DrawAllMetasprites','DrawMetasprite','MetaspriteRenderLoop','RosterOamReady']:
  at=location(bundle,n);hooks[n]=dict(address=address(bundle,n),bank=(at-16)//8192,bytes=list(bundle['raw'][at:at+3]))
 at=location(bundle,'OAMandReadJoypad');assert bundle['raw'][at:at+7]==bytes([169,2,141,20,64,162,1])
 hooks['DMA_complete_after_LDX']=dict(address=address(bundle,'OAMandReadJoypad')+7,bank=(at-16)//8192,bytes=list(bundle['raw'][at+7:at+10]))
 cases=[];deps={Path(p)for p in inherited}|{parent/'readiness.json',capture,Path(__file__),observer,ROOT/'tools/audit/current3cee_megaman_visibility_v1.py'}
 for name in['octopus','sophia']:
  case=name+'-easy';route=parent/'native'/case;ref=parent/'native'/(case+'-direct');m=get(route/'manifest.json');r=get(ref/'proof.json');assert m['result']['cleared']and r['passed']and r['ROM_sha256']==SHA
  names=COMMON+(OCT if name=='octopus'else SOPHIA);arrays={'CurrentCHRBank':8,'X5ChrMode':8}
  arrays.update({'PnFrame':28,'PnDrawFlags':28,'PnType':28,'PnPalette':28,'PnActive':28,'PnPhase':28}if name=='octopus'else{'RgShotType':10,'RgShotX':10,'RgShotY':10,'RgShotDir':10,'RgShotAge':10,'SophiaEffectAge':6})
  required=set(names)|set(arrays)|{'R0','R1','R3','R4','R5','R6','R7','M1','Sprite_Data'};ram={n:address(bundle,n)for n in sorted(required)}
  c=dict(character=m['config']['character'],first=480,last=4100,output=(out/name/'native').as_posix()+'/',names=names,arrays=arrays,ram=ram,hooks=hooks)
  folder=out/name;folder.mkdir();put(folder/'config.json',c);added='VEHICLE_VISIBILITY='+lua(c)+'\n'+text;ast.parse(added);(folder/'added-observer.lua').write_text(added,encoding='utf-8')
  for directory in[route,ref]:deps|={f for f in directory.iterdir()if f.is_file()and f.suffix in['.json','.csv','.lua']}
  deps.add(Path(r['raw_lossless_archive']['path']));cases.append(dict(name=name,route=str(route),reference=str(ref),reference_proof_sha256=sha(ref/'proof.json'),reference_raw_sha256=r['raw_stream_sha256'],reference_frame_index_sha256=sha(ref/'direct-frame-index.csv'),config=str(folder/'config.json'),observer=str(folder/'added-observer.lua'),output=str(folder/'native')))
 deps|={f for f in out.rglob('*')if f.is_file()}
 # Bind the actual parser implementation used only for static readiness.
 parser=Path(a.parser_root);deps|={f for sub in['luaparser','antlr4']for f in(parser/sub).rglob('*.py')}
 bindings={str(p.resolve()):sha(p)for p in sorted(deps,key=str)}
 q=dict(passed=True,native_executed=False,native_workers=1,ROM_sha256=SHA,rom=str(rom),capture=str(capture),cases=cases,bindings=bindings,static_lua_parse=True,no_emulated_writes=True,added_callbacks_static_only=True,full_original_capture_layer_retained=True,scope='Exactly2sequential read-only full original-input replays. Added hardware/publication/flags observations480..4100actualPPUframes. Full raw stream/frameindex/gameplay log equality required; no controller/source/settings changes or automatic retry. Attribution/repair not assumed.')
 put(out/'readiness.json',q);print(json.dumps(dict(prepared=True,native_executed=False,readiness_sha256=sha(out/'readiness.json'),bindings=len(bindings),cases=[z['name']for z in cases],observer_source_sha256=sha(observer)),indent=2))
def run(a):
 assert a.native_grant;q=get(a.packet/'readiness.json');assert not q['native_executed'];assert all(sha(p)==h for p,h in q['bindings'].items());assert not(a.packet/'launch.json').exists()
 put(a.packet/'launch.json',dict(readiness_sha256=sha(a.packet/'readiness.json'),command_scope='exact2sequential fixed-input instrumented replays',runner_sha256=sha(Path(__file__))))
 completed=[]
 for case in q['cases']:
  spec=importlib.util.spec_from_file_location('vehicle_frozen_capture_'+case['name'],q['capture']);capture=importlib.util.module_from_spec(spec);spec.loader.exec_module(capture);original=capture.OBSERVER;added=Path(case['observer']).read_text();capture.OBSERVER=added+'\n'+original
  sys.argv=[q['capture'],'--rom',q['rom'],'--route',case['route'],'--output',case['output']]
  try:
   capture.main();native=Path(case['output']);ref=Path(case['reference']);compared={}
   for n in['inputs.csv','trace.csv','render.csv','events.csv','audio-events.csv','oam.csv','chr.csv','scroll-writes.csv','stomp-events.csv','completed-loop-motion.csv','chr-commit.csv','direct-frame-index.csv']:
    assert(native/n).read_bytes()==(ref/n).read_bytes(),n;compared[n]=sha(native/n)
   current=get(native/'proof.json');reference=get(ref/'proof.json');assert current['passed']and current['raw_stream_sha256']==reference['raw_stream_sha256']and current['raw_stream_bytes']==reference['raw_stream_bytes']
   raw=Path(q['rom']).read_bytes();chrstart=16+128*8192;pages=[]
   for f in native.glob('physical-chr-*.bin'):
    page=int(f.stem.split('-')[-1]);assert f.read_bytes()==raw[chrstart+page*1024:chrstart+(page+1)*1024];pages.append(dict(page=page,path=str(f),sha256=sha(f)))
   stats=get(native/'added-observer-result.json');assert stats['no_added_runtime_registrations']and stats['rows']==7242
   s=dict(passed=True,name=case['name'],ROM_sha256=SHA,full_original_direct_stream_exact=True,all_original_frame_pixels_exact=True,original_logs=compared,physical_pages=pages,added_observer=stats,source_observer_sha256=sha(Path(case['observer'])),visibility_frames_sha256=sha(native/'visibility-frames.jsonl'),bus_sha256=sha(native/'visibility-bus.jsonl'),publications_sha256=sha(native/'visibility-publications.jsonl'),native_proof_sha256=sha(native/'proof.json'),worker_released=True,scope='Read-only exact replay and observation integrity only. Pixel/owner attribution follows offline; no game fix.')
   put(a.packet/case['name']/'proof.json',s);completed.append(s);print(json.dumps(dict(completed=case['name'],passed=True,raw_stream_exact=True,logged_rows=stats['rows'])),flush=True)
  except BaseException as error:
   put(a.packet/'execution.json',dict(passed=False,worker_released=True,completed=[z['name']for z in completed],failure_profile=case['name'],error=repr(error),no_retry=True));raise
 assert all(sha(p)==h for p,h in q['bindings'].items())
 put(a.packet/'execution.json',dict(passed=True,worker_released=True,completed=[z['name']for z in completed],readiness_sha256=sha(a.packet/'readiness.json'),cases=completed));print(json.dumps(dict(passed=True,worker_released=True,completed=[z['name']for z in completed]),indent=2))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['prepare','run']);p.add_argument('--packet',type=Path,required=True);p.add_argument('--parser-root',type=Path);p.add_argument('--native-grant',action='store_true');a=p.parse_args();prepare(a)if a.mode=='prepare'else run(a)
if __name__=='__main__':main()
