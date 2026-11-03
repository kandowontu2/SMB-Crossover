"""Actual deep GameRoutines ISR test of the ungranted v73 factoring."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import check_prince_native_stack_1102_v72 as S
import measure_prince_death_ack_1102_v73 as A
O=A.O


def loaded():
 b,m,lab=A.loaded()
 # Match a live native render epoch after the cold forced-blank constructor.
 # A lag NMI legally sets this native mirror to1E; starting it at stale cold0
 # would make the final whole-native-memory comparison a fixture mismatch.
 A.N.put(m,Mirror_PPUMASK=30);m[0x2001]=30
 return b,m,lab


def main():
 source=Path(S.__file__);text=source.read_text().replace('v72','v74')
 text=text.replace('b,m,lab=C.loaded();fatal(m,b);scenarios=[]','b,m,lab=CURRENT_LOADED();fresh=N.fork(m);fatal(m,b);scenarios=[]')
 text=text.replace('_,m,_=C.loaded();N.put(m,ObjectOffset=5)','m=N.fork(fresh);N.put(m,ObjectOffset=5)')
 text=text.replace('0x15a<=c.pc<0x17b or bank==2 and', '0x15a<=c.pc<0x17b or bank==2 and 0xc766<=c.pc<0xc780 or bank==2 and')
 text=text.replace("assert got['regs']==ref['regs']and state(z)==expected,(name,kind,cut)", "assert got['regs']==ref['regs']and state(z)==expected,(name,kind,cut,got['regs'],ref['regs'],[(k,hex(i),a,v)for k in range(4)for i,(a,v)in enumerate(zip(expected[0][k],z.ram[k]))if a!=v][:8],[(hex(i),a,v)for i,(a,v)in enumerate(zip(expected[4],bytes(z[0x200:0x800])))if a!=v][:8])")
 env=dict(__file__=str(Path(__file__)),__name__='prince_ack_stack_v74',CURRENT_LOADED=loaded)
 exec(compile(text,str(source),'exec'),env)
 try:env['main']()
 except Exception as error:
  (O/'death-ack-stack-negative-v74.json').write_text(json.dumps(dict(passed=False,CPU_only=True,ROM_written=False,exception=repr(error)),indent=2)+'\n');raise
 path=O/'native-stack-CPU-v74.json';q=json.loads(path.read_text());q.update(death_ack_ungranted=True,private_ack_interval=[0xc766,0xc77f],selector_bytes=171,scope='Actual deep native GameRoutines kill/death update and native star/1up calls in source-injected CPU fixture. Proposed after-auth exact row7 factoring avoids duplicate private transport, retaining full real native death-start initialization. Full cold/retirement/auth-code binding and new interval are unqualified and ungranted.')
 q['bindings'].update({p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),source,Path(A.__file__),O/'death-ack-measurement-v73.json']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
