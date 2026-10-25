"""Read-only whole-route CPU scopes on the currently qualified Mega Man run."""
from pathlib import Path
import sys,hashlib,json,importlib.util,subprocess,csv,collections,statistics
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent
BASE=D.parent/'2026-10-24-native-head-pz';O=BASE/'profile-megaman-v4';O.mkdir(exist_ok=False);(O/'frames').mkdir()
ROM=D/'ryu-head-candidate-v5/candidate.nes';route=BASE/'finish-v2/discover-megaman-easy'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
helper=R/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py'
spec=importlib.util.spec_from_file_location('profile_image',helper);im=importlib.util.module_from_spec(spec);spec.loader.exec_module(im);image=im.Image(ROM)
profiler=R/'build/verification/root49-current-f-samus-exclusive-profile-bj/profile-actual-ram-return.lua'
assert sha(profiler)=='69876d2888b8461512b4129537fa4f30919dc09d2a9bdab0437be9a1a24c47b5'
frozen=O/'profiler.lua';frozen.write_bytes(profiler.read_bytes())
names=['GameLoop','GameCoreRoutine','EnemiesAndLoopsCore','PlayerGfxHandler','DrawAllMetasprites','DrawMetasprite','AreaParserTaskHandler','BlockObjectsCore','MiscObjectsCore','GuestPostEnemyCollision','InventoryUiTick','PlayerCtrlRoutine','MegaManMovement','MegaManWeapons','MegaManDrawShots','MegaManGraphics','RemainingWeapons','AudioUpdate','MegaManAudioUpdate','MegaManAudioNativeUpdate','ExpandedAudioUpdate','GuestAudioBegin','GuestAudioMix','CrossoverGraphicsBank']
hooks={};missing=[]
for n in names:
 try:hooks[n]=image.hook(n)
 except AssertionError:missing.append(n)
assert all(n in hooks for n in ['GameLoop','GameCoreRoutine','DrawAllMetasprites','MegaManMovement','MegaManWeapons','AudioUpdate'])
hooks.update(NMI=image.hook('NonMaskableInterrupt'),IRQ=image.hook('IrqScrollSplit'),NMI_END=image.hook('NonMaskableInterrupt',delta='last'),IRQ_END=image.hook('IrqScrollSplit',delta='last'))
assert hooks['NMI_END']['bytes'][0]==hooks['IRQ_END']['bytes'][0]==0x40
pc=image.ram['FarcallJmpTarget_SMC']+3;ret=image.hook('FarCallCommon',delta=pc-image.ram['FarCallCommon'])
policy=O/'policy.lua';policy.write_text('ORDINARY_PROFILE='+im.lua(dict(hooks=hooks,ram=image.ram,ram_return=ret,start_frame=350,stop_frame=4500,base_policy=(route/'policy.lua').as_posix()))+'\nreturn dofile('+im.lua(frozen.as_posix())+')\n')
t=(route/'run.lua').read_text();a='out='+json.dumps(route.as_posix()+'/');assert t.count(a)==1;t=t.replace(a,'out='+json.dumps(O.as_posix()+'/'))
a='policy='+json.dumps((route/'policy.lua').as_posix());assert t.count(a)==1;t=t.replace(a,'policy='+json.dumps(policy.as_posix()))
assert t.count('replay=nil')==1;t=t.replace('replay=nil','replay='+json.dumps((route/'inputs.csv').as_posix()));script=O/'run.lua';script.write_text(t)
(O/'binding.json').write_text(json.dumps(dict(ROM_sha256=sha(ROM),source_manifest_sha256=sha(route/'manifest.json'),source_policy_sha256=sha(route/'policy.lua'),literal_profiler_sha256=sha(frozen),hooks=hooks,ram_return=ret,unavailable_named_scopes=missing,controller_changes=False,emulated_writes=False),indent=2))
with(O/'host.log').open('w')as f:p=subprocess.run([sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(O),str(script),str(ROM),'--timeout','240','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false'],cwd=R,stdout=f,stderr=subprocess.STDOUT)
assert p.returncode==0,(O/'host.log').read_text()[-2000:]
for n in ['inputs.csv','trace.csv','events.csv','render.csv','oam.csv','chr.csv','scroll-writes.csv','audio-events.csv','stomp-events.csv']:assert(O/n).read_bytes()==(route/n).read_bytes(),n
assert json.loads((O/'result.json').read_text())==json.loads((route/'result.json').read_text())
groups=collections.defaultdict(list)
for line in(O/'ordinary-profile.jsonl').open():
 z=json.loads(line);assert z['exclusive_cycles']>=0;groups[z['name']].append(z)
summary={}
for n,rows in groups.items():
 values=sorted(x['exclusive_cycles']for x in rows);summary[n]=dict(calls=len(rows),median=statistics.median(values),p95=values[int((len(values)-1)*.95)],maximum=max(values),total=sum(values),ISR_depths=sorted(set(x['entry_ISR_depth']for x in rows)))
q=dict(passed=True,ROM_sha256=sha(ROM),native_route_exact=True,scopes=summary,scope='Actual qualified full1-1 fixed controller replay. Sampled function durations exclude nested interrupt cycles but contain child functions; do not sum overlapping scopes as independent shares. Actual return PCs/SP/banks/instruction guards required. No game or controller mutation and no optimization claim.')
(O/'proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(q,indent=2),flush=True)
