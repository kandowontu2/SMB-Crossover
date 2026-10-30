"""Prepared only; one explicit root grant is required for this exact command."""
import json,os,sys
import prepare_current_quick_ui_v13 as B
import arthur_body_fair_budget_v7 as Q
O=B.O;N=B.N;F=O/'native-prepared';T=O/'native/cold-menu-ui-v13'
def main():
 assert sys.argv[1:]==['--launch']and not T.exists(),'No automatic native retry.'
 docs=[json.loads((O/'handoff.json').read_text()),json.loads((F/'prepared.json').read_text())]
 def verify():
  for d in docs:
   for path,value in d['bindings'].items():assert B.sha(path)==value,path
  assert docs[0]['candidate']==docs[1]['candidate']==B.sha(N/'candidate.nes')
 verify();T.parent.mkdir(exist_ok=True);os.environ['SMB_RUN_OUTPUT']=str(T.resolve())
 budget=Q.load(F/'capture-budget.py');run=Q.run_function(budget)
 meta=dict(candidate=docs[0]['candidate'],source_handoff=B.sha(O/'handoff.json'),prepared=B.sha(F/'prepared.json'),bindings_verified=sum(len(d['bindings'])for d in docs),config=docs[1]['config'],options=docs[1]['options'])
 (F/'native-preflight.json').write_text(json.dumps(meta,indent=2)+'\n')
 rc=run(F/'native-ui-v13.lua',N/'candidate.nes',timeout=60,emulator_options=docs[1]['options']);verify()
 (F/'native-postflight.json').write_text(json.dumps(dict(**meta,exit_code=rc,pre_post_bindings_exact=True),indent=2)+'\n')
 print(json.dumps(dict(native_terminal=True,exit_code=rc,output=str(T.resolve()),candidate=docs[0]['candidate'],bindings_pass=True)),flush=True);raise SystemExit(rc)
if __name__=='__main__':main()
