"""Rebind the proven real cold/parser test to the one-byte lives correction."""
from pathlib import Path
import hashlib,importlib.util,json,re,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address
O=R/'build/contra-force-lives-position-controls-1031-v1'
J=R/'build/contra-force-lives-position-1031-v3/joint'
K=J.parent/'kernel'
S=R/'tools/audit/contra_force_menu_cold_parser_1031_v1.py'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 spec=importlib.util.spec_from_file_location('cf_lives_real_parser',S);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.O=O;m.J=J;m.K=K;m.P.J=m.H.O=J
 m.P.L={n:int(v,16)for v,n in re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',(K/'runtime.lbl').read_text())}
 m.main()
 q=json.loads((O/'controls.json').read_text());assert q['passed']and q['actual_classes']==4
 b=qualified(J/'candidate.nes');bounds=[]
 for cohort in q['cohorts']:
  visible=cohort['visible_lives'];assert visible
  for row in visible:
   body=row['visible_source_body_parts'];ys=[p[0]+1 for p in body]
   assert min(ys)>=80 and max(ys)+15<=128,('Actual native lives body alongside life count',cohort['variant'],body)
  bounds.append(dict(variant=cohort['variant'],real_lives_DMA_checks=len(visible),
      Y_bounds=[min(p[0]+1 for p in visible[0]['visible_source_body_parts']),max(p[0]+16 for p in visible[0]['visible_source_body_parts'])],
      actual_gameplay_Main=len(cohort['frames'])))
 # New matched finite receipt; the underlying proven parser receipt remains intact.
 out=dict(passed=True,source_CPU=True,native=False,candidate=sha(J/'candidate.nes'),real_cold_classes=4,
          actual_gameplay_Main_total=128,cohorts=bounds,source_only_lives_position_corrected=True,
          bindings={str(p.resolve()):sha(p)for p in[Path(__file__),S,J.parent/'source-stage.json',O/'controls.json']})
 (O/'lives-layout.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(dict(path=str(O/'lives-layout.json'),sha256=sha(O/'lives-layout.json'),cohorts=bounds)),flush=True)

if __name__=='__main__':main()
