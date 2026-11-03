"""Finish165 cold alias after generated harness imports; retain negative."""
from pathlib import Path
import inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_live_policy_isr_1103_v165 as V
O=V.O;ORIGINAL_ENV=V.environment


def environment():
 e,text=ORIGINAL_ENV();a=e['address'];l=e['location']
 e['address']=lambda b,n:0xae00 if n=='PrinceColdProposed'else a(b,n)
 e['location']=lambda b,n:16+65*8192+0xe00 if n=='PrinceColdProposed'else l(b,n)
 return e,text


def scenarios():
 old=V.environment;V.environment=environment
 try:return V.scenarios()
 finally:V.environment=old


def main():
 text=inspect.getsource(V.main).replace('v165','v168');env=dict(V.__dict__,__file__=str(Path(__file__)),scenarios=scenarios);exec(compile(text,str(Path(V.__file__)),'exec'),env);env['main']()
 path=O/'live-policy-ISR-v168.json';q=json.loads(path.read_text());q['bindings'].update({p.relative_to(R).as_posix():V.V.M.sha(p.read_bytes())for p in [Path(__file__),Path(V.__file__),O/'live-policy-ISR-negative-v165.json']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'live-policy-ISR-negative-v168.json').write_text(json.dumps(dict(passed=False,exception=repr(error)),indent=2)+'\n');raise
