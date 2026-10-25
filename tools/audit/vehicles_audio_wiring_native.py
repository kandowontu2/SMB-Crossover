"""One sequential Mesen worker for explicit current TMNT music/performance ROMs."""
from pathlib import Path
import argparse,gzip,hashlib,json,subprocess,sys

ROOT=Path(__file__).resolve().parents[2]
OB=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-native-audio-ob')
sys.path.insert(0,str(ROOT/'tools/audit'))
from check_tmnt_render_oa import load,address,location
from observe_chip_committed_write import lua


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['rom','output']:p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--emulator',required=True);p.add_argument('--mode',choices=['music','performance'],required=True)
 p.add_argument('--variant',type=int,default=0);p.add_argument('--hard',action='store_true')
 p.add_argument('--timeout',type=int,default=120)
 a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(exist_ok=False)
 b=load(a.rom)
 smc=next(g for g in b['segs'].values()if g.get('name')=='"SMCCODE"')
 cfg=dict(nmi=address(b,'NonMaskableInterrupt'),
          nmi_return=address(b,'NonMaskableInterrupt')+int(b['syms']['NonMaskableInterrupt']['size'],0)-1,
          smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2],
          stack_floor=(int(smc['start'],0)+int(smc['size'],0))&255,
          stack_start=int(smc['start'],0)&255,
          music=int(a.mode=='music'),chr_observer=(ROOT/'tools/audit/chr_commit_observer.lua').as_posix())
 guards=ROOT/'tools/audit/vehicles_audio_wiring_guards.lua'
 lines=['VEHICLE_AUDIO_CONFIG='+lua(cfg),guards.read_text()]
 deps=[guards,ROOT/'tools/audit/chr_commit_observer.lua']
 if a.mode=='music':
  fixture=ROOT/'tests/tmnt-native-audio-oc.lua';deps.append(fixture)
  seg=next(g for g in b['segs'].values()if g.get('name')=='"MUSIC"')
  lines+=['TMNT_GOLDEN={}',f"TMNT_VANILLA_MUSIC_BANK={(int(seg['ooffs'],0)-16)//8192}"]
  coverage=json.loads((OB/'probe-v2/coverage.json').read_text());deps.append(OB/'probe-v2/coverage.json')
  for song in [1,2,3,5,6,8,10,11,12,13,15]:
   f=OB/f'probe-v2/song-{song:02d}.json.gz';deps.append(f)
   assert sha(f)==coverage['songs'][str(song)]['capture_sha256']
   source=json.loads(gzip.decompress(f.read_bytes()));image=bytearray(20);frames=[]
   for q in source[:1502]:
    for at,v in q['writes']:
     if 0x4000<=at<=0x4013:image[at-0x4000]=v
    frames.append('"'+''.join(f'\\{v:03d}'for v in image)+'"')
   lines.append(f'TMNT_GOLDEN[{song}]={{'+','.join(frames)+'}')
  lines.append(fixture.read_text())
 else:
  fixture=ROOT/'tests/tmnt-performance.lua';observer=ROOT/'tools/audit/tmnt_performance_observer.lua';deps+=[fixture,observer]
  lines+=['TMNT_CFG='+lua(dict(variant=a.variant,mode='hard'if a.hard else'easy',observer=observer.as_posix())),fixture.read_text()]
 script=out/'run.lua';script.write_text('\n'.join(lines))
 with(out/'host.log').open('w')as log:
  z=subprocess.run([sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(out),
    '--emulator',a.emulator,str(script),str(a.rom.resolve()),'--timeout',str(a.timeout),'--option=--doNotSaveSettings',
    '--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false',
    '--option=--nes.randomizeMapperPowerOnState=false'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 report=dict(passed=False,ROM_sha256=sha(a.rom),mode=a.mode,variant=a.variant,hard=a.hard,
             emulator_sha256=sha(Path(a.emulator)),tool_sha256=sha(Path(__file__)),script_sha256=sha(script),
             dependencies={str(d):sha(d)for d in deps},exit=z.returncode,scope='Explicitly staged native audio or equal-update native performance arena. Not a campaign clear.')
 for name in ['proof.json','result.json','ownership-guards.json','chr-commit.json']:
  f=out/name
  if f.exists():report[name]=json.loads(f.read_text())
 report['passed']=z.returncode==0 and report.get('ownership-guards.json',{}).get('passed',False)and report.get('chr-commit.json',{}).get('passed',False)
 if a.mode=='music':report['passed']&=report.get('proof.json',{}).get('passed',False)
 else:report['passed']&=report.get('result.json',{}).get('passed',False)
 (out/'native-result.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items()if k!='dependencies'},indent=2));return 0 if report['passed']else 1


if __name__=='__main__':raise SystemExit(main())
