"""Prepare or run one explicit frozen Mac native music/performance worker."""
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
 p.add_argument('--gold',type=Path);p.add_argument('--emulator',type=Path);p.add_argument('--mode',choices=['music','performance'],required=True);p.add_argument('--hard',action='store_true');p.add_argument('--run',action='store_true');p.add_argument('--timeout',type=int,default=240)
 a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False);b=load(a.rom)
 fixture=ROOT/'tools/audit/mac_native_music_native.lua';guards=ROOT/'tools/audit/vehicles_audio_wiring_guards.lua';observer=ROOT/'tools/audit/tmnt_performance_observer.lua';chr=ROOT/'tools/audit/chr_commit_observer.lua'
 used=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",fixture.read_text()))|set(re.findall(r'L\.([A-Za-z_][A-Za-z_0-9]*)',fixture.read_text()))
 cfg=dict(music=int(a.mode=='music'),hard=int(a.hard),direct_zp=int('LmNativeDirectZp'in b['syms']),ram={n:address(b,n)for n in used if n in b['syms']})
 if a.mode=='music':
  assert a.gold is not None
  golden=out/'gold';golden.mkdir();cfg['gold']=golden.as_posix()+'/'
  coverage=json.loads((a.gold/'coverage.json').read_text())
  assert coverage['source_sha256']=='9a7a3ae5f16b745f74296478ec208b5b87ad5ec2773a14b243f7e631a2dd8d68'
  for song in [1,2,4,6,7,9,20,22,23]:
   f=a.gold/f'song-{song:02d}.json.gz';assert sha(f)==coverage['songs'][str(song)]['capture_sha256']
   records=json.loads(gzip.decompress(f.read_bytes()));data=bytearray()
   for row in records[:5002]:
    assert len(row['writes'])<256;data.append(len(row['writes']))
    for at,v in row['writes']:assert 0x4000<=at<=0x4017;data.extend([at-0x4000,v])
    data.extend(row['ram']);data.extend(row['zp'])
   (golden/f'song-{song}.bin').write_bytes(data)
  for n in ['LmNativeRam','LmNativeZp','LmNativeSourceInit','LmNativeSourcePlay','LmNativeMusicPlay','LmNativeMusicUpdate','ExpandedAudioDecoded']:cfg['ram'][n]=address(b,n)
 count=address(b,'X5MenuPresent')-address(b,'X5MenuCharacters');tab=lambda n:list(b['raw'][location(b,n):location(b,n)+count]);cfg['menu_target']=tab('X5MenuCharacters').index(15)
 maps={n.lower():tab('X5Menu'+n)for n in ['Up','Down','Left','Right']};cfg['menu_moves']=[]
 for start in range(count):
  todo=deque([(start,[])]);seen={start}
  while todo:
   node,path=todo.popleft()
   if node==cfg['menu_target']:cfg['menu_moves'].append(path[0]if path else'');break
   for direction,links in maps.items():
    if links[node]not in seen:seen.add(links[node]);todo.append((links[node],path+[direction]))
  else:raise AssertionError('Mac menu unreachable')
 smc=next(g for g in b['segs'].values()if g.get('name')=='"SMCCODE"')
 gc=dict(nmi=address(b,'NonMaskableInterrupt'),nmi_return=address(b,'NonMaskableInterrupt')+int(b['syms']['NonMaskableInterrupt']['size'],0)-1,smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2],stack_floor=(int(smc['start'],0)+int(smc['size'],0))&255,stack_start=int(smc['start'],0)&255,music=cfg['music'],chr_observer=chr.as_posix())
 perf=observer.read_text().replace("==19","==15").replace('L.TnMovement','L.LmMovementGate').replace('B.TnMovement','B.LmMovementGate').replace("'GameLoop','TnMovement'","'GameLoop','LmMovementGate','LmWeaponsGate','LmGraphicsGate','TnMovement'")
 (out/'performance-observer.lua').write_text(perf);cfg['observer']=(out/'performance-observer.lua').as_posix()
 script=out/'run.lua';script.write_text('VEHICLE_AUDIO_CONFIG='+lua(gc)+'\n'+guards.read_text().replace('character=19','character=15')+'\nMAC_NATIVE_CONFIG='+lua(cfg)+'\n'+fixture.read_text())
 binding=dict(ROM_sha256=sha(a.rom),mode=a.mode,hard=a.hard,runner_sha256=sha(Path(__file__)),fixture_sha256=sha(fixture),script_sha256=sha(script),config=cfg,dependencies={str(x):sha(x)for x in [guards,observer,chr]},prepared_only=not a.run)
 (out/'binding.json').write_text(json.dumps(binding,indent=2)+'\n')
 if not a.run:print(json.dumps(binding));return
 assert a.emulator is not None
 with(out/'host.log').open('w')as log:
  z=subprocess.run([sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(out),'--emulator',str(a.emulator),str(script),str(a.rom.resolve()),'--timeout',str(a.timeout),'--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false'],stdout=log,stderr=subprocess.STDOUT,cwd=ROOT)
 result=binding|dict(passed=False,prepared_only=False,emulator_sha256=sha(a.emulator),exit=z.returncode)
 for name in ['proof.json','ownership-guards.json','chr-commit.json']:
  f=out/name
  if f.exists():result[name]=json.loads(f.read_text())
 result['passed']=z.returncode==0 and all(result.get(n,{}).get('passed',False)for n in ['proof.json','ownership-guards.json','chr-commit.json'])
 (out/'native-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in ['config','dependencies']},indent=2));raise SystemExit(0 if result['passed']else 1)
if __name__=='__main__':main()
