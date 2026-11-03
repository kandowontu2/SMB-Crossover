"""Use the actual published row34 consumer, not an unrelated old Hu symbol."""
from collections import Counter
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_strike_lifetime_1102_v125 as V
C,N,O=V.C,V.N,V.O


def callback(m):
 actual=N.NesMPU;calls=Counter()
 class Trace(actual):
  def step(self):
   if self.memory.rawtags[0]==254:
    if self.pc==0x9af8:calls['ShellOrBlockDefeat']+=1
    if self.pc==C.address(self.memory.bundle,'KillPlayer'):calls['KillPlayer']+=1
   return super().step()
 N.NesMPU=Trace
 try:out=C.C.C.I.invoke(m,193,0xb08c+3*34,(83,0,0,0x21))
 finally:N.NesMPU=actual
 out['native_calls']=dict(calls);return out


def main():
 source=Path(V.__file__);text=source.read_text().replace('v125','v126').replace("e['run'](m,'HuWeapons',lab)",'CALLBACK(m)')
 env=dict(__file__=str(Path(__file__)),__name__='prince_strike_lifetime_v126',CALLBACK=callback);exec(compile(text,str(source),'exec'),env);env['main']()
 path=O/'strike-lifetime-CPU-v126.json';q=json.loads(path.read_text());q.update(consumer_entry='Actual published65:B0F2 row34 via FarCallCommon; completeGameLoop follows this exact source route.',retained_fixture_negative='v125 invoked old globally bound HuWeapons directly, which does not reach this published consumer; it observed no native call and made no positive claim.')
 q['bindings'].update({p.relative_to(R).as_posix():C.C.C.M.sha(p.read_bytes())for p in [Path(__file__),source,O/'strike-lifetime-negative-v125.json']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'strike-lifetime-negative-v126.json').write_text(json.dumps(dict(passed=False,CPU_only=True,source_injected=True,exception=repr(error)),indent=2)+'\n');raise
