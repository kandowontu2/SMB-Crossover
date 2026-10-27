"""One-expression current-task deadline successor; reuse unchanged source proof."""
from pathlib import Path
import argparse,hashlib,json

ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',choices=['darkwing','roll'],required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output=a.output.resolve();assert a.output.is_relative_to(ROOT/'build')and not a.output.exists()
    old=ROOT/'build'/('current-ab221e-'+a.identity+'-hard-earned-v1');ready=json.loads((old/'prepared-not-run.json').read_text())
    assert all(sha(Path(q['path']))==q['sha256']for q in ready['bindings'])
    v1=ROOT/'tools/audit/current_darkwing_roll_earned_v1.lua';v2=ROOT/'tools/audit/current_darkwing_roll_earned_v2.lua'
    text1,text2=v1.read_text(),v2.read_text();wrong='C.plan[math.min(index,#C.plan)].limit'
    assert text1.count(wrong)==1 and text1.replace(wrong,'task.limit')==text2
    start='-- All callback registration is startup-static.';end='emu.addEventCallback(function()\n if not entered'
    guard=text2[text2.index(start):text2.index(end)]
    assert len(guard.encode())==4058 and hashlib.sha256(guard.encode()).hexdigest()==ready['literal_hardware_guard_sha256']
    controls=[]
    for label,age,current,next_limit,wanted in [('actual-arrow-complete',307,420,80,True),('arrow-boundary',540,420,80,False),('arrow-overrun',541,420,80,False),('short-case-within',199,80,420,True),('short-case-boundary',200,80,420,False),('final-case-within',25,40,40,True)]:
        actual=age<current+120;assert actual==wanted
        controls.append(dict(name=label,age=age,current_limit=current,next_limit=next_limit,correct=actual,old_next_index=age<next_limit+120))
    a.output.mkdir(parents=True)
    for n in ['config.json','source-controls.json']:(a.output/n).write_bytes((old/n).read_bytes())
    run=(old/'run.lua').read_text();assert run.count(v1.as_posix())==1
    (a.output/'run.lua').write_text(run.replace(v1.as_posix(),v2.as_posix()),newline='\n')
    cmd=json.loads((old/'command.json').read_text());argv=cmd['argv']
    argv=[str(a.output/'native')if x==str(old/'native')else str(a.output/'run.lua')if x==str(old/'run.lua')else x for x in argv]
    cmd['argv']=argv;put(a.output/'command.json',cmd)
    paths=[Path(x['path'])for x in ready['bindings']]+[v2,Path(__file__),old/'prepared-not-run.json']+[a.output/n for n in ['config.json','source-controls.json','run.lua','command.json']]
    paths=list(dict.fromkeys(paths))
    ready.update(status='PREPARED_DO_NOT_RUN',native_run=False,passed=False,
        deadline_correction=dict(source_only=True,old_ready_sha256=sha(old/'prepared-not-run.json'),original_FALSE_preserved=True,exact_expression_from=wrong,exact_expression_to='task.limit',all_other_module_text_exact=True,all_other_native_controller_mechanics_seeds_guards_caps_exact=True,source_CPU_proof_reused_unchanged=True,source_controls_sha256=sha(a.output/'source-controls.json'),Lua_VM_executed=False,finite_controls=controls),
        bindings=[dict(path=str(x),bytes=x.stat().st_size,sha256=sha(x))for x in paths])
    put(a.output/'prepared-not-run.json',ready)
    assert all(sha(Path(q['path']))==q['sha256']for q in ready['bindings'])
    print(json.dumps(dict(prepared=True,native_run=False,ready=str(a.output/'prepared-not-run.json'),sha256=sha(a.output/'prepared-not-run.json'),bindings=len(paths),source_GameLoop_calls_reused=ready['source_GameLoop_calls'])))


if __name__=='__main__':main()
