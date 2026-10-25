"""Prepare or run one explicit frozen Mike native music/performance worker."""
from pathlib import Path
from collections import deque
import argparse,gzip,hashlib,json,re,subprocess,sys
from link_pit_rygar_sophia_audit_cpu import scoped_load as load
from check_tmnt_render_oa import address,location
from observe_chip_committed_write import lua
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['rom','output']:p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--pilot',action='store_true');p.add_argument('--gold',type=Path);p.add_argument('--emulator',type=Path);p.add_argument('--mode',choices=['music','performance'],required=True);p.add_argument('--hard',action='store_true');p.add_argument('--run',action='store_true');p.add_argument('--timeout',type=int,default=240)
 a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False);b=load(a.rom)
 fixture=ROOT/'tools/audit/mike_native_music_native.lua';guards=ROOT/'tools/audit/vehicles_audio_wiring_guards.lua';observer=ROOT/'tools/audit/tmnt_performance_observer.lua';chr=ROOT/'tools/audit/chr_commit_observer.lua'
 used=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",fixture.read_text()))|set(re.findall(r'L\.([A-Za-z_][A-Za-z_0-9]*)',fixture.read_text()))
 cfg=dict(music=int(a.mode=='music'),hard=int(a.hard),pilot=int(a.pilot),ram={n:address(b,n)for n in used if n in b['syms']})
 if a.mode=='music':
  assert a.gold is not None
  golden=out/'gold';golden.mkdir();cfg['gold']=golden.as_posix()+'/'
  coverage=json.loads((a.gold/'coverage.json').read_text())
  assert coverage['source_sha256']=='e67ccc9d3950a62d850d6da27aaecd32fdd50db05c9c341d36dc99b6bfa95845'
  components={}
  for lo,hi,at,target in coverage['pointer_components']:components[lo]=('<',target);components[hi]=('>',target)
  from mike_native_music_cpu import translated
  for song in [1,2,4,5,9,11,13,14,15,17,22]:
   f=a.gold/f'song-{song:02d}.jsonl.gz';assert sha(f)==coverage['songs'][str(song)]['capture_sha256'];data=bytearray()
   with gzip.open(f,'rt')as stream:
    for i,line in enumerate(stream):
     if i>5001:break
     row=json.loads(line);assert len(row['writes'])<256;data.append(len(row['writes']))
     for at,v in row['writes']:assert 0x4000<=at<=0x400f or at==0x4015;data.extend([at-0x4000,v])
     state=translated(b,row,components);data.extend(state['ram']);data.extend(state['zp'])
   (golden/f'song-{song}.bin').write_bytes(data)
  for n in ['StNativeRam','StNativeZp','StNativeSourceInit','StNativeSourcePlay','StNativeMusicPlay','StNativeMusicUpdate','ExpandedAudioDecoded']:cfg['ram'][n]=address(b,n)
 count=address(b,'X5MenuPresent')-address(b,'X5MenuCharacters');tab=lambda n:list(b['raw'][location(b,n):location(b,n)+count]);cfg['menu_target']=tab('X5MenuCharacters').index(16)
 maps={n.lower():tab('X5Menu'+n)for n in ['Up','Down','Left','Right']};cfg['menu_moves']=[]
 for start in range(count):
  todo=deque([(start,[])]);seen={start}
  while todo:
   node,path=todo.popleft()
   if node==cfg['menu_target']:cfg['menu_moves'].append(path[0]if path else'');break
   for direction,links in maps.items():
    if links[node]not in seen:seen.add(links[node]);todo.append((links[node],path+[direction]))
  else:raise AssertionError('Mike menu unreachable')
 smc=next(g for g in b['segs'].values()if g.get('name')=='"SMCCODE"')
 gc=dict(nmi=address(b,'NonMaskableInterrupt'),nmi_return=address(b,'NonMaskableInterrupt')+int(b['syms']['NonMaskableInterrupt']['size'],0)-1,smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2],stack_floor=(int(smc['start'],0)+int(smc['size'],0))&255,stack_start=int(smc['start'],0)&255,music=cfg['music'],chr_observer=chr.as_posix())
 perf=observer.read_text().replace('==19','==16').replace('L.TnMovement','L.JnMovement').replace('B.TnMovement','B.JnMovement').replace("'GameLoop','TnMovement'","'GameLoop','JnMovement','JnWeapons','JnGraphics','TnMovement'").replace("r('TnShotKind',i)","r('JnShotKind',i)").replace('for i=0,2 do','for i=0,5 do')
 (out/'performance-observer.lua').write_text(perf);cfg['observer']=(out/'performance-observer.lua').as_posix()
 script=out/'run.lua';script.write_text('VEHICLE_AUDIO_CONFIG='+lua(gc)+'\n'+guards.read_text().replace('character=19','character=16')+'\nMIKE_NATIVE_CONFIG='+lua(cfg)+'\n'+fixture.read_text())
 parser=ROOT/'build/verification/agent47-samus-controller-batch-h-preparation/parser'
 provenance=json.loads((parser/'provenance.json').read_text())
 for q in[provenance['wheel']]+provenance['extracted']:assert sha(Path(q['path']))==q['sha256']
 py=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
 compiler='import pathlib,sys;sys.path.insert(0,sys.argv[1]);from lupa.lua54 import LuaRuntime;LuaRuntime().eval("function(s)local f,e=load(s);assert(f,e);return true end")(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"));print("Lua54 parse PASS")'
 parsed=subprocess.run([str(py),'-c',compiler,str(parser/'runtime'),str(script)],capture_output=True,text=True);(out/'parse.log').write_text(parsed.stdout+parsed.stderr);assert parsed.returncode==0,parsed.stderr
 assert '["hard"]='+str(int(a.hard))in script.read_text()and not re.search(r'\b(?:True|False)\b',script.read_text())
 binding=dict(ROM_sha256=sha(a.rom),mode=a.mode,hard=a.hard,runner_sha256=sha(Path(__file__)),fixture_sha256=sha(fixture),script_sha256=sha(script),config=cfg,dependencies={str(x):sha(x)for x in [guards,observer,chr]},prepared_only=not a.run)
 (out/'binding.json').write_text(json.dumps(binding,indent=2)+'\n')
 if not a.run:print(json.dumps(binding));return
 assert a.emulator is not None
 with(out/'host.log').open('w')as log:
  z=subprocess.run([sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(out),'--emulator',str(a.emulator),str(script),str(a.rom.resolve()),'--timeout',str(a.timeout),'--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false'],stdout=log,stderr=subprocess.STDOUT,cwd=ROOT)
 result=binding|dict(passed=False,prepared_only=False,emulator_sha256=sha(a.emulator),exit=z.returncode)
 for name in ['proof.json','ownership-guards.json','chr-commit.json','nmi-depth.json','mode-readback.json']:
  f=out/name
  if f.exists():result[name]=json.loads(f.read_text())
 result['passed']=z.returncode==0 and all(result.get(n,{}).get('passed',False)for n in ['proof.json','ownership-guards.json','chr-commit.json','nmi-depth.json'])and result.get('mode-readback.json',{}).get('actual')==int(a.hard)
 (out/'native-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in ['config','dependencies']},indent=2));raise SystemExit(0 if result['passed']else 1)
if __name__=='__main__':main()
