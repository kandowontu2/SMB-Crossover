"""Source/mock qualification of additional displayed font/label pairing guard."""
from pathlib import Path
import argparse,hashlib,json,sys
from parodius_visibility_hud_static_startup_v1 import MOCK
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['preparation','negative-run','lua-root','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);sys.path.insert(0,str(a.lua_root));from lupa import LuaRuntime
 z=json.loads((a.preparation/'death/preparation.json').read_text());script=Path(z['script']);cfg=json.loads(script.with_name('config.json').read_text());layer=ROOT/'tools/audit/parodius_visibility_hud_lease_native_v1.lua'
 rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(MOCK+'\nPARODIUS_VISIBILITY={output=""}\n'+layer.read_text());rows=[]
 def check(spec,variant,labels,font,expected,**kw):
  q=rt.table_from(dict(variant=variant,labels=rt.table_from(labels),font=font,**kw));ok,why=rt.globals().PARODIUS_HUD_VISIBLE_PAIR_OK(q,rt.table_from(cfg['hud_labels'][str(variant)]));assert ok==expected,(spec,variant,font,why)
  rows.append(dict(case=spec,variant=variant,font=font,accepted=ok,reason=why,foreground_fields_not_substituted_for_actual_PPU=True))
 for v in [1,2,3]:
  labels=cfg['hud_labels'][str(v)];font=395+v;changed=labels[:];changed[5]^=1
  for spec,tiles,physical,expected in [('custom',labels,font,True),('blank',[36]*28,0,True),('wrong-font',labels,0,False),('wrong-variant-font',labels,395+(v%3+1),False),('blank-custom-font',[36]*28,font,False),('changed-label',changed,font,False),('missing-label',labels[:-1],font,False),('unknown-font',labels,1023,False)]:check(spec,v,tiles,physical,expected)
  check('retained-hardware-pair-with-foreground-lease-cleared',v,labels,font,True,active=0,source_generation=2,current_generation=3)
 actual=[json.loads(x)for x in(a.negative_run/'hud-frames.jsonl').read_text().splitlines()]
 for frame,expected in [(514,True),(515,False),(812,True)]:
  q=next(x['start']for x in actual if x['finished']['frame']==frame);check('actual5354-frame'+str(frame),q['ram']['VvVariant'],q['labels'],q['chr'][8],expected,active=q['ram']['InvHudActive'])
 scroll=[json.loads(x)for x in(a.negative_run/'scroll-events.jsonl').read_text().splitlines()];q=next(x['state']for x in scroll if x['kind']=='visible-start'and x['state']['ppu']['frame']==813);check('actual5354-frame813',1,q['labels'],q['font'],False,active=q['active'])
 text=script.read_text()
 originals=['parodius_visibility_hud_static_observer_v2.lua','parodius_visibility_hud_native_v1.lua','parodius_visibility_hud_scroll_native_v2.lua','parodius_visibility_hud_transition_v1.lua','parodius_visibility_hud_lifecycle_bridge_v4.lua']
 assert all(text.count((ROOT/'tools/audit'/n).read_text())==1 for n in originals)
 (a.output/'cases.json').write_text(json.dumps(rows,indent=2)+'\n');q=dict(passed=True,native_run=False,cases=len(rows),
          actual_old_native_pair_cases=4,all_original_five_guard_layers_literal_exact=True,additional_guard_only=True,
          actual_displayed_pair_independent_of_later_foreground_RAM=True,old_native_wrong_pairs_rejected=True,
          layer_sha256=sha(layer),script_sha256=sha(script),tool_sha256=sha(Path(__file__)),cases_sha256=sha(a.output/'cases.json'),
          limits='Pure source/mock additional pairing predicate and four real old-frame metadata replays. No new native/hardware image certification. Original scroll/prelease/font/lifecycle/epoch assertions remain unchanged; current foreground lease values never replace actual displayed PPU pair.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
