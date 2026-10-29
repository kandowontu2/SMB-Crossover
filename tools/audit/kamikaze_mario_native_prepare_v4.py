"""Prepare one bounded genuine menu/lives/controller1-1 skin run; no launch."""
from pathlib import Path
import argparse,json
import current_roster_compact_11_v1 as base
from roster_expansion_native_prepare_v2 import navigation
def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--expected-sha256',required=True);p.add_argument('--output',type=Path,required=True)
 p.add_argument('--mode',choices=['easy','hard'],default='easy');p.add_argument('--frames',type=int,default=7000);p.add_argument('--private-emulator',type=Path,required=True);a=p.parse_args()
 a.identity='kamikaze';a.policy=base.ROOT/'tools/playthroughs/kamikaze_mario_upgrades_11_v2.lua';a.replay=None
 base.BASE.update(kamikaze=(0,0,'MarioVariant',3));base.navigation=navigation;base.SCRIPT=Path(__file__).with_name('roster_expansion_cold_capture_v3.lua')
 base.prepare(a);ready=a.output.resolve()/'ready.json';d=json.loads(ready.read_text())
 for dep in[Path(__file__),Path(__file__).with_name('roster_expansion_native_prepare_v2.py')]:d['bindings'][str(dep.resolve())]=base.sha(dep)
 e=a.private_emulator.resolve();proof=e.parent/'proof.json';j=json.loads(proof.read_text());assert j['passed']and j['host_callback_1_3_seconds_completed']
 assert j['only_setting_changed']=='Debug.ScriptWindow.ScriptTimeout'
 for path,h in j['bindings'].items():assert base.sha(path)==h;d['bindings'][path]=h
 d['bindings'][str(proof)]=base.sha(proof)
 assert d['command'][d['command'].index('--emulator')+1]=='C:/Mesen2/Mesen.exe'
 d['command'][d['command'].index('--emulator')+1]=str(e)
 d['host_callback_budget_seconds']=5
 d['controller_scope']='Genuine cold menu Select toMarioVariant3, real lives, ordinary controller1-1. Hardware sprite limit on; <=8 exported whole frames; bounded lossless stream; no RAM writes/cheats.'
 ready.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(dict(ready=str(ready),sha256=base.sha(ready))))
if __name__=='__main__':main()
