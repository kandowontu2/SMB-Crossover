"""Require whole-control original/static observer equivalence on exact df515."""
from pathlib import Path
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--original',type=Path,required=True);p.add_argument('--replay',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);x=a.original/'baseline-early';y=a.replay/'baseline-early';before=json.loads((x/'scroll-proof.json').read_text());after=json.loads((y/'scroll-proof.json').read_text());assert before['passed']and after['passed'];assert sha(x/'candidate.nes')==sha(y/'candidate.nes')=='df5154bc035ba2c392bb8d34068897a2bccf7a78a6f4554bd6790d31a586c357'
 oldmodule=ROOT/'tools/audit/parodius_visibility_observer.lua';newmodule=ROOT/'tools/audit/parodius_visibility_hud_static_observer_v1.lua';text=(x/'run.lua').read_text().replace(oldmodule.read_text(),newmodule.read_text()).replace(x.as_posix(),y.as_posix()).replace((a.original/'controller').as_posix(),(a.replay/'controller').as_posix());text+='\n-- FINAL startup registration: all HUD/scroll/controller static hooks precede returns.\nPARODIUS_STATIC_INSTALL_RETURNS()\n';assert text==(y/'run.lua').read_text()
 CSV={}
 for name in ['inputs.csv','trace.csv','events.csv','completed-loop-motion.csv']:
  assert(x/name).read_bytes()==(y/name).read_bytes(),name;CSV[name]=dict(sha256=sha(x/name),rows=len((x/name).read_text().splitlines()))
 events={}
 for name in ['hud-frames.jsonl','hud-events.jsonl','scroll-events.jsonl','oam-bus.jsonl','epochs.jsonl','body-writes.jsonl']:
  u=[json.loads(s)for s in(x/name).read_text().splitlines()];v=[json.loads(s)for s in(y/name).read_text().splitlines()];assert u==v,(name,len(u),len(v),next((i for i,(l,r)in enumerate(zip(u,v))if l!=r),None));events[name]=dict(events=len(u),original_sha256=sha(x/name),replay_sha256=sha(y/name))
 captures=[];files=sorted(x.glob('*.argb'));assert len(list(x.glob('frame-*.argb')))==len(list(y.glob('frame-*.argb')))==201;assert sorted(f.name for f in files)==sorted(f.name for f in y.glob('*.argb'))
 for f in files:assert f.read_bytes()==(y/f.name).read_bytes(),f.name;captures.append(dict(name=f.name,sha256=sha(f)))
 q=dict(passed=True,native_run=False,whole_observation_layer_equivalent=True,goal_complete=False,ROM_sha256=sha(x/'candidate.nes'),same_script_except_registration_and_paths=True,CSV=CSV,JSON_event_streams=events,identical_raw_PPU_images=captures,original_proof_sha256=sha(x/'scroll-proof.json'),replay_proof_sha256=sha(y/'scroll-proof.json'),tool_sha256=sha(Path(__file__)),limits='Whole one-controller640-frame equality between actual completed original/static observation layers, including all201 lossless full frames and capture duplicate. No different-profile equivalence, lifecycle or global game conclusion.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=True,identical_images=len(captures),events={n:v['events']for n,v in events.items()},proof_sha256=sha(a.output/'proof.json'))))

if __name__=='__main__':main()
