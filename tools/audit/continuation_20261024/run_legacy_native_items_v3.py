from pathlib import Path
import argparse,hashlib,importlib.util,json,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;P=D/'native-probes-qa-v2'
sys.path.insert(0,str(R/'tools/audit'))
from check_tmnt_render_oa import load,location
sp=importlib.util.spec_from_file_location('image',R/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py');im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im)
sp=importlib.util.spec_from_file_location('runner',R/'tools/run_mesen.py');runner=importlib.util.module_from_spec(sp);sp.loader.exec_module(runner)
p=argparse.ArgumentParser();p.add_argument('names',nargs='+');p.add_argument('--version',default='v1');a=p.parse_args();O=P/('legacy-native-items-'+a.version);O.mkdir(exist_ok=False);ROM=P/'candidate.nes';image=im.Image(ROM);bundle=load(ROM);sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
fixture=D/'legacy-native-items-v3.lua';frozen=O/'fixture.lua';frozen.write_bytes(fixture.read_bytes())
def value(n,i):return bundle['raw'][location(bundle,n)+i]
attacks={1:{1:(9,'b'),2:(10,'b'),3:(11,'b'),4:(12,'b'),5:(19,'b'),6:(15,'b'),7:(17,'b'),8:(20,'b')},9:{1:(9,'b'),2:(10,'b'),3:(11,'b'),4:(12,'b'),5:(19,'b'),6:(15,'b'),7:(17,'b')},2:{2:(41,'special'),3:(46,'b')},3:{1:(1,'b'),2:(42,'b'),3:(43,'b'),4:(2,'b'),5:(3,'b'),6:(3,'b')},4:{1:(33,'special'),2:(32,'special'),3:(5,'special')},5:{2:(35,'special'),3:(36,'special'),4:(-180,'special'),5:(38,'special'),6:(6,'special')},10:{1:(5,'special'),2:(39,'special'),3:(8,'special'),4:(40,'special')},11:{1:(44,'special'),2:(45,'special')}}
aggregate=json.loads((P/'full-roster-aggregate-v1/proof.json').read_text());report=dict(ROM_sha256=sha(ROM),complete=False,passed=False,goal_complete=False,runs=[],fixture_sha256=sha(frozen),scope='Cold Hard owner, declared mature-item/native-floor arena seeded only at guarded completed native update entry. Real collision grants/exclusivity and declared controller attacks. Not random block delivery/full emergence, every-item audio fidelity, hardware or campaign proof.')
for name in a.names:
 original=next(x for x in aggregate['runs']if x['identity']==name);config=json.loads(Path(original['discovery']).read_text())['config'];c=config['character'];assert c in attacks
 cfg=dict(name=name,character=c,slot=config['slot'],variantSymbol=config['variantSymbol'],variant=config['variant'],hard=True,mushroomMask=1|value('InvMushroomLo',c)|(256*value('InvMushroomHi',c)),steps=[dict(id=0,type=0)])
 for i in range(1,value('InvItemCount',c)+1):
  step=dict(id=i,type=1,exclusive=value('InvSingleLo',c*16+i)+256*value('InvSingleHi',c*16+i),selectable=value('InvSelectable',c*16+i)!=0)
  if i in attacks[c]:
   step['attack'],step['button']=attacks[c][i]
   if c in(1,9):
    step.update(arm=i==1,kick=i==5)
    if i==6:step['alternate']=16
   if c==5:
    step['watch']=i==4
    if i==3:step['alternate']=37
  cfg['steps'].append(step)
 out=O/name;out.mkdir();runner.ROOT=out;script=out/'run.lua';script.write_text('LEGACY_ITEMS='+im.lua(cfg)+'\nLEGACY_HOOKS='+im.lua(dict(entry=image.hook('GameLoop'),finish=image.hook('GameLoop',delta='last')))+'\ndofile('+im.lua(frozen.as_posix())+')\n');(out/'config.json').write_text(json.dumps(cfg,indent=2))
 code=runner.run(script,ROM,emulator=str(D/'mmc3-flag-fix-v23/script-budget-probe-v2/emulator/Mesen.exe'),timeout=180,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false','--doNotSaveSettings'])
 result=out/'build/verification/native-legacy-items.json';row=dict(name=name,exit=code,passed=code==0 and result.exists(),config_sha256=sha(out/'config.json'),script_sha256=sha(script),result=json.loads(result.read_text())if result.exists()else None)
 report['runs'].append(row);(O/'progress.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(name=name,exit=code,passed=row['passed'])),flush=True)
report.update(complete=True,passed=all(x['passed']for x in report['runs']));(O/'proof.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(complete=True,passed=report['passed'])),flush=True)
