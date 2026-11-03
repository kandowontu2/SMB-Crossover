"""All actual FF foreground instructions, including I1 NMI eligibility."""
from collections import Counter
from pathlib import Path
import hashlib,inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_current_game_loop_isr_1102_v102 as C
O=C.O;N=C.N


def environment():
 source=inspect.getsource(C.environment).replace("CAPTURE['env']=env;return","CAPTURE['env']=env;CAPTURE['source']=text;return").replace("return capture['env']","return capture")
 ns=dict(C.__dict__);exec(compile(source,str(Path(__file__)),'exec'),ns);cap=ns['environment']();text=cap['source'];env=cap['env']
 old='cut=(c.pc,c.sp,m.rawtags[1])';assert text.count(old)==1
 text=text.replace(old,"cut=(c.pc,c.sp,m.rawtags[1],int(bool(c.p&4)))\n  if N.get(m,'NmiDisable')==255 and c.p&4:cuts.add(cut)")
 old='assert not c.p&4;assert';assert text.count(old)==1
 text=text.replace(old,"assert interrupt[0]=='lagNMI' or not c.p&4;assert")
 env['COUNTS']=Counter();env['AUDIO']=Counter();exec(compile(text,str(Path(C.V.S.__file__)),'exec'),env);return env,text


def fold(cuts):
 best={}
 for cut in cuts:
  key=(cut[0],cut[2],cut[3])
  if key not in best or cut[1]<best[key][1]:best[key]=cut
 return sorted(best.values())


def main():
 e,source=environment();lab,cases=C.scenarios(e);rows=[];minimum=224;total=0
 for name,seed,target in cases:
  m=N.fork(seed);ref=e['run'](m,target,lab);want=C.V.normalized_state(m);cuts=fold(c for c in ref['cuts']if c[3]);print('All-PC actualFF I1',name,len(cuts),flush=True)
  for cut in cuts:
   m=N.fork(seed);out=e['run'](m,target,lab,('lagNMI',cut));assert out['regs']==ref['regs']and C.V.normalized_state(m)==want,(name,cut);minimum=min(minimum,out['minSP']);total+=1
  rows.append(dict(name=name,actual_I1_FF_NMI_cuts=len(cuts),foreground_minimum_SP=ref['minSP'],I1_cut_minimum_SP=min((c[1]for c in cuts),default=None)))
 q=dict(passed=True,CPU_only=True,ROM_written=False,memory_only_SHA256=C.C.C.image()[1]['expected_memory_only_SHA256'],all_actual_FF_foreground_I1_PC_A_bank_deepest_SP_cuts=total,minimum_SP=minimum if total else None,scenarios=rows,collection_scope='Every foreground instruction while actual NmiDisableFF and I1, independent of old transport/gateway PC filters; cut key includes I flag to prevent an earlier I0 visit masquerading as I1.',standalone_IRQ_remains_I0_only=True,lag_branch_PC_and_INC_NmiSkipped_and_no_regular_branch_asserted=True,full_private_R0_R7_SMC_mapper_AXYP_SP_and_native_audio_exception_exact=True,source_fixture_SHA256=hashlib.sha256(source.encode()).hexdigest(),supersedes_scope='v102/v104 retained unchanged. Their recorded watched cuts are I0; they did not establish eligibility at all possible I1 native callee PCs.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),Path(C.__file__),O/'post-return-manifest-v97.json',R/'src/reset.s']})
 (O/'current-I1-lag-CPU-v112.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'current-I1-lag-negative-v112.json').write_text(json.dumps(dict(passed=False,CPU_only=True,exception=repr(error)),indent=2)+'\n');raise
