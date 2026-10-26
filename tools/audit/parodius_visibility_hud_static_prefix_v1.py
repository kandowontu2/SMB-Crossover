"""Compare a retained host AV with a granted source-equivalent static replay."""
from pathlib import Path
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--failed',type=Path,required=True);p.add_argument('--replay',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);x=a.failed/'baseline-early';y=a.replay/'baseline-early';before=json.loads((x/'proof.json').read_text());after=json.loads((y/'scroll-proof.json').read_text());assert before['emulator_exit']==0xc0000005 and not before['passed'];assert after['passed'];assert sha(x/'candidate.nes')==sha(y/'candidate.nes')=='df5154bc035ba2c392bb8d34068897a2bccf7a78a6f4554bd6790d31a586c357'
 oldmodule=ROOT/'tools/audit/parodius_visibility_observer.lua';newmodule=ROOT/'tools/audit/parodius_visibility_hud_static_observer_v1.lua';text=(x/'run.lua').read_text().replace(oldmodule.read_text(),newmodule.read_text()).replace(x.as_posix(),y.as_posix()).replace((a.failed/'controller').as_posix(),(a.replay/'controller').as_posix());text+='\n-- FINAL startup registration: all HUD/scroll/controller static hooks precede returns.\nPARODIUS_STATIC_INSTALL_RETURNS()\n';assert text==(y/'run.lua').read_text()
 inputs={}
 for name in ['inputs.csv','trace.csv','events.csv','completed-loop-motion.csv']:
  b=(x/name).read_bytes();old=b.splitlines();new=(y/name).read_bytes().splitlines();partial=None
  if b and not b.endswith(b'\n'):partial=old.pop();assert new[len(old)].startswith(partial),(name,'partial tail')
  assert old==new[:len(old)],(name,'complete prefix')
  inputs[name]=dict(complete_prefix_rows=len(old),partial_tail=partial.decode()if partial else None,failed_sha256=sha(x/name),replay_sha256=sha(y/name))
 rows={}
 for name in ['hud-frames.jsonl','hud-events.jsonl','scroll-events.jsonl','oam-bus.jsonl','epochs.jsonl','body-writes.jsonl']:
  u=[json.loads(s)for s in(x/name).read_text().splitlines()];v=[json.loads(s)for s in(y/name).read_text().splitlines()];assert u==v[:len(u)],(name,next((i for i,(l,r)in enumerate(zip(u,v))if l!=r),None));rows[name]=dict(exact_prefix_events=len(u),last_failed_event=u[-1]if name=='oam-bus.jsonl'else None,failed_sha256=sha(x/name),replay_sha256=sha(y/name))
 captures=[]
 for f in sorted(x.glob('*.argb')):assert f.read_bytes()==(y/f.name).read_bytes();captures.append(dict(name=f.name,sha256=sha(f)))
 q=dict(matched_static_observer_replay=True,original_AV_retained=True,native_replay_passed=True,goal_complete=False,ROM_sha256=sha(x/'candidate.nes'),same_script_except_registration_and_paths=True,CSV_prefixes=inputs,JSON_event_prefixes=rows,identical_PPU_captures=captures,failed_proof_sha256=sha(x/'proof.json'),replay_proof_sha256=sha(y/'scroll-proof.json'),tool_sha256=sha(Path(__file__)),limits='Compare all actually flushed old data only. Missing buffered crash tails are not inferred. A successful repaired-observer replay supports the host-cause diagnosis and this exact bounded game control; it does not relabel the crash, prove all eight controls, or establish global gameplay/fidelity/timing closure.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(matched_prefix=True,PPU_captures=len(captures),events={n:r['exact_prefix_events']for n,r in rows.items()},proof_sha256=sha(a.output/'proof.json'))))

if __name__=='__main__':main()
