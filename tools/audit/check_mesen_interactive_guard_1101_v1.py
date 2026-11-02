"""Check that explicit interactive coexistence never admits automated overlap."""
import json
from pathlib import Path
from types import SimpleNamespace
import mesen_session_guard_v1 as G
from prepare_selected_native_packet_v1 import R
O=R/'build/mesen-interactive-guard-1101-v1'
def main():
 O.mkdir(exist_ok=True);rom=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
 def rec(cmd):return dict(ProcessId=101,Name='Mesen.exe',CommandLine=cmd)
 exe='"C:/mesen2/Mesen.exe" '
 cases=[('plain-nightly',exe+'"'+str(rom)+'"',True),('plain-local',exe+'"'+str(R/'build/private/candidate.nes')+'"',True),('plain-unquoted',exe+str(rom),True),('automated',exe+'--testRunner C:/Temp/test.lua "'+str(rom)+'"',False),('scripted',exe+'"'+str(R/'test.lua')+'" "'+str(rom)+'"',False),('optioned',exe+'--doNotSaveSettings "'+str(rom)+'"',False),('script-only',exe+'"'+str(R/'test.lua')+'"',False)]
 rows=[];original=G.subprocess.run
 try:
  for name,cmd,interactive in cases:
   record=rec(cmd);assert G.interactive_session(record,R,rom)==interactive,name
   for allow in [False,True]:
    G.subprocess.run=lambda *args,**kw:SimpleNamespace(stdout=json.dumps(record))
    blocked=False
    try:G.require_free_workspace(R,rom,allow_interactive=allow)
    except RuntimeError:blocked=True
    assert blocked==(not(allow and interactive)),(name,allow,blocked)
    rows.append(dict(case=name,allow_interactive=allow,blocked=blocked))
  # A user window does not hide an owned automated run in the same snapshot.
  user=rec(cases[0][1]);automated=rec(cases[3][1]);automated['ProcessId']=102
  G.subprocess.run=lambda *args,**kw:SimpleNamespace(stdout=json.dumps([user,automated]))
  try:G.require_free_workspace(R,rom,allow_interactive=True)
  except RuntimeError as e:assert '102'in str(e)
  else:raise AssertionError('Automated overlap admitted')
  rows.append(dict(case='user-and-automated',allow_interactive=True,blocked=True))
 finally:G.subprocess.run=original
 q=dict(passed=True,cases=len(rows),rows=rows,scope='Read-only process snapshot fixtures; actual plain user commandline versus explicit testRunner/Lua/extra-option cases. No processes killed or real emulator launched. Coexistence remains opt-in.')
 (O/'result.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='rows'}))
if __name__=='__main__':main()
