"""Record verified delivery and the separate unfinished Shinobi traversal."""
import json
from pathlib import Path
from prepare_selected_native_packet_v1 import sha
R=Path(__file__).resolve().parents[2]
def main():
 o=R/'build/metal-storm-idle-shots-1101-v41';dest=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
 digest=sha(dest);assert digest==sha(o/'candidate.nes')
 c=o/'downloads/capture';b=json.loads((c/'binding.json').read_text());r=json.loads((c/'result.json').read_text())
 assert b['exit_code']==0 and b['ROM_sha256']==digest and r['passed']
 delivery=json.loads((o/'delivery.json').read_text());delivery['downloads_launch_verified']=True
 delivery['scope']=delivery['scope'].replace('Downloads launch pending.','Actual Downloads cold launch/selection/idle/walk passed.')
 (o/'delivery.json').write_text(json.dumps(delivery,indent=2)+'\n')
 path=R/'docs/qa/continuation-current.json';q=json.loads(path.read_text())
 q={'parallel_roster_followup':dict(installed_ROM_sha256=digest,installed_candidate=str(o.relative_to(R)/'candidate.nes'),
   nightly_scope='Metal Storm no-shot409-cycle saving; same throughput80 idle/78 walk updates per120 physical frames; full1-1 to1-2 no life loss; actualDownloads launch pass. No backup.',
   shinobi_candidate='build/shinobi-camera-1101-v20/candidate.nes',shinobi_sha256='fe4e9a6d5aef0c2e3848a501f487e7791cd75b9db5cf5297ebad395162560ad9',
   shinobi_status='Private only. Source export now supplies Player_Pos_ForScroll via13-byte D690..D69D worker, hookShStoreFace. New cookie. Opening controller now crosses firsttwo pipes; holdingB blocked jumping, release-before-pipe variant reachedX648 then lostlife. Do not claim impossible jump/helper need or enemy-contact defect without further diagnosis. Render still dark/HUD artifact concern; nameMARIO.',
   next='Continue Shinobi route/contacts and graphics ownership. Merge Metal v41 byte diff into next private Shinobi successor; never regress installed update. Agents working Excitebike resource closure and Arthur lag. Named helper inventory written, assisted crossings incomplete.'),**q}
 q['previous_goal_turn_classification']='progress'
 path.write_text(json.dumps(q,indent=2)+'\n')
 doc=R/'docs/qa/metal-storm-idle-shots-1101.md'
 t=doc.read_text().replace('Not installed; native verification remains pending.','Installed in Downloads and tested from that exact path; no backup created.')
 t+='\nNative verification: full1-1 through active1-2 passed in5480 physical frames, both lives retained. Idle/walk completed80/78 updates per120 physical frames, unchanged throughput; mean cycles32229.4/34043.0, exactly409 belowv40. Downloads cold launch/select/idle/walk also passed. No full roster or all-powerup claim.\n'
 doc.write_text(t)
 print(json.dumps(dict(installed=digest,downloads_verified=True,goal_complete=False)))
if __name__=='__main__':main()
