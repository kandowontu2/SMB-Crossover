"""Actual full GameCore post-return hook/native callback interrupt closure."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_native_stack_1102_v72 as S
import check_prince_post_return_core_1102_v79 as A
O=A.O


def main():
 source=Path(S.__file__);text=source.read_text().replace('v72','v80')
 text=text.replace('b,m,lab=C.loaded();fatal(m,b);scenarios=[]', "b,m,lab=CURRENT_LOADED();fresh=N.fork(m);fatal(m,b);scenarios=[]\n for i,v in enumerate([4,0,0]):m[address(b,'GameTimerDisplay')+i]=v")
 text=text.replace('_,m,_=C.loaded();N.put(m,ObjectOffset=5)','m=N.fork(fresh);N.put(m,ObjectOffset=5)')
 text=text.replace("'GameRoutines'", "'GameCoreRoutine'")
 text=text.replace("if c.sp<=180 and (0x15a<=c.pc<0x17b", "if (bank==252 and(0xa760<=c.pc<0xa76e or 0xa795<=c.pc<0xa7a0 or c.pc==0xad75))or(0x15a<=c.pc<0x17b")
 text=text.replace("assert ref['gateway_entries']==1,(name,ref)", "assert ref['gateway_entries']==(0 if target=='GameCoreRoutine'else 1),(name,ref)")
 text=text.replace("assert got['regs']==ref['regs']and state(z)==expected,(name,kind,cut)", "assert got['regs']==ref['regs']and state(z)==expected,(name,kind,cut,got['regs'],ref['regs'],[(k,hex(i),a,v)for k in range(4)for i,(a,v)in enumerate(zip(expected[0][k],z.ram[k]))if a!=v][:8],[(hex(i+0x200),a,v)for i,(a,v)in enumerate(zip(expected[4],bytes(z[0x200:0x800])))if a!=v][:8],expected[3],z.rawtags)")
 env=dict(__file__=str(Path(__file__)),__name__='prince_postreturn_stack_v80',CURRENT_LOADED=A.loaded);exec(compile(text,str(source),'exec'),env)
 try:env['main']()
 except Exception as error:
  (O/'post-return-stack-negative-v80.json').write_text(json.dumps(dict(passed=False,CPU_only=True,exception=repr(error)),indent=2)+'\n');raise
 path=O/'native-stack-CPU-v80.json';q=json.loads(path.read_text());q.update(new_hook_and_lifetimes_ungranted=True,tag_operand=0x0179,source_tag_zero_growth=True,scope='Actual complete GameCore earned-death request then native post-owner-return hook, actual death-update GameCore and genuine native star/1up gateway clients. Each reached shared/SMC/hook instruction runs real IRQ and lag-NMI continuation with full private/native memory, mapper, R0..7, five SMC bytes and returned AXYP/SP parity. Source code injected after old cold; no full changed-image auth/cold/native emulator/respawn/menu/install claim.')
 q['bindings'].update({p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),source,Path(A.__file__),O/'post-return-measurement-v78.json',O/'deferred-death-CPU-v79.json']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
