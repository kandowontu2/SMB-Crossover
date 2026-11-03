"""Current qualified full-cold image: complete native pickup/body ingresses."""
from pathlib import Path
from types import SimpleNamespace
import ast,hashlib,inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools/reference')]
import check_prince_current_cold_1102_v98 as C
import check_prince_current_ingress_1102_v61 as F
import check_prince_native_ingress_1102_v66 as OLD
O=C.O


def main():
 base,manifest=C.image();parent,_=C.M.parent()
 def bundle():return parent,base,None,dict(cookie=manifest['details']['Prince_cookie'])
 adapter=SimpleNamespace(bundle=bundle,PIN=manifest['parent_memory_SHA256'],sha=C.M.sha)
 text=inspect.getsource(F.main)
 tree=ast.parse(inspect.getsource(OLD.main))
 changes=ast.literal_eval(next(n.value for n in ast.walk(tree)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='changes'for t in n.targets)))
 for old,new in changes.items():assert old in text,old;text=text.replace(old,new)
 for old,new in {
  'native-ingress-negative-v66.json':'current-native-ingress-negative-v108.json',
  'native-ingress-CPU-v66.json':'current-native-ingress-CPU-v108.json',
  'native-labels-v49.json':'native-labels-v78.json',
  'collision-owner-v59.lbl':'post-owner-v97.lbl',
  'native-manifest-v65.json':'post-return-manifest-v97.json',
  'M.BASE':"O/'post-return-manifest-v97.json'",
  "O/'collision-shared-CPU-v60.json'":"O/'current-foreign-hot-CPU-v103.json'",
  "O/'collision-services-CPU-v56.json'":"O/'current-game-loop-ISR-CPU-v102.json'",
  "O/'current-foreign-CPU-v52.json'":"O/'current-shared-cold-CPU-v99.json'",
 }.items():assert old in text,old;text=text.replace(old,new)
 # The raw256 cookie test must use the actual new three-owner tables.
 labels=C.M.A.L.P.T.labels(O/'post-owner-v97.lbl')
 text=text.replace("off=0x1003 if owner==39 else 0xff3 if owner==37 else ownerlab['PrCookie']-0xa000", "off=COOKIE_LABELS[owner]-0xa000")
 env=dict(F.__dict__,M=adapter,COOKIE_LABELS={37:labels['CoExCookie'],38:labels['PrCookie'],39:labels['CoBBCookie']},__file__=str(Path(__file__)))
 exec(compile(text,str(Path(__file__)),'exec'),env);env['main']()
 path=O/'current-native-ingress-CPU-v108.json';q=json.loads(path.read_text());assert q['passed']
 q.update(private_proposal_only=False,new_execution_granted=True,qualified_current_shared_cold=True,source_fixture_SHA256=hashlib.sha256(text.encode()).hexdigest(),scope='Exact current Prince97 over Bub66, actual complete resident cold and original Fresh. Complete native PowerUpObjHandler all4types reaches maturity/rectangle/pickup; genuine PlayerEnemyCollision reaches original defender for all3sword modes and4actions. Native lives/engine unchanged by fixture assertions; native actors and source inventory/action are explicit CPU preconditions, not emulator or outcome seeds. No menu/ROM/install/native-play claim. Original audio event production retained; native mixer/mapping incomplete.')
 q['bindings'].update({p.relative_to(R).as_posix():C.M.sha(p.read_bytes())for p in [Path(__file__),Path(OLD.__file__),Path(F.__file__),O/'post-return-manifest-v97.json',O/'native-labels-v78.json',O/'post-owner-v97.lbl',R/'docs/qa/allocations/joint-native-rare-gate-1102-v70.json']})
 path.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings']}))


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'current-native-ingress-negative-v108.json').write_text(json.dumps(dict(passed=False,CPU_only=True,exception=repr(error)),indent=2)+'\n');raise
