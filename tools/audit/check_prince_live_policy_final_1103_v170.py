"""Exact newcold cut domain; preserve168's stopped overbroad harness run."""
from pathlib import Path
import inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_live_policy_current_1103_v168 as V
O=V.O


def environment():
 e,text=V.environment()
 old="target=address(b,'ShellOrBlockDefeat');bank=";assert text.count(old)==1
 text=text.replace(old,"defeat_target=address(b,'ShellOrBlockDefeat');bank=").replace('native[(target+3,bank)]','native[(defeat_target+3,bank)]').replace('native.pop((target,bank))','native.pop((defeat_target,bank))')
 # The old strike observer reused target as its local defeat address. Keep
 # the public request string live for the newcold-only domain predicate.
 exec(compile(text,str(Path(__file__)),'exec'),e);a=e['address'];l=e['location']
 e['address']=lambda b,n:0xae00 if n=='PrinceColdProposed'else a(b,n)
 e['location']=lambda b,n:16+65*8192+0xe00 if n=='PrinceColdProposed'else l(b,n)
 return e,text


def scenarios():
 old=V.V.environment;V.V.environment=environment
 try:return V.V.scenarios()
 finally:V.V.environment=old


def main():
 text=inspect.getsource(V.V.main).replace('v165','v170');env=dict(V.V.__dict__,__file__=str(Path(__file__)),scenarios=scenarios);exec(compile(text,str(Path(V.V.__file__)),'exec'),env);env['main']()
 path=O/'live-policy-ISR-v170.json';q=json.loads(path.read_text());q.update(stopped_historical_168='168 source observer overwritten target string with nativeDefeat integer, yielding847 olddecoder+newcold PCs. Owned child238620 stopped before bounded600s budget; no source outputs/ROM/captures mutated.170 retains target string, qualifies only declared newcold seams; prior1177live IRQ/FF outputs re-executed.')
 q['bindings'].update({p.relative_to(R).as_posix():V.V.V.M.sha(p.read_bytes())for p in [Path(__file__),Path(V.__file__),Path(V.V.__file__),O/'live-policy-ISR-negative-v165.json']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'live-policy-ISR-negative-v170.json').write_text(json.dumps(dict(passed=False,exception=repr(error)),indent=2)+'\n');raise
