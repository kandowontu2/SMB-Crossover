"""Record natural pickup evidence and the unresolved route failure separately."""
from pathlib import Path
import json
from prepare_selected_native_packet_v1 import sha
R=Path(__file__).resolve().parents[2]
O=R/'build/mario-tank-pickup-1101-v1'
def main():
    records={}
    for n in ['probe3','probe5']:
        p=O/n
        result=json.loads((p/'capture/result.json').read_text())
        binding=json.loads((p/'capture/binding.json').read_text())
        ready=json.loads((p/'ready.json').read_text())
        assert binding['exit_code']==0 and binding['ready_sha256']==sha(p/'ready.json')
        assert result['natural_mushroom_collected'] and result['controller_only']
        for f,h in ready['bindings'].items():assert sha(Path(f))==h,f
        records[n]=dict(result=result,binding=binding)
    assert records['probe5']['result']['lost_life']
    q=dict(complete=False,ROM_sha256=records['probe3']['binding']['ROM_sha256'],
        verified='Controller-only mushroom release, collection and growth to status1; return to gameplay subroutine8.',
        route_limit='Extended route loses a life at world X1549. Its passed field refers ONLY to the mushroom predicate, not survival or stage completion. Earlier probe4 did not stop on life loss and followed a restart; do not use it as stage-clear evidence.',
        next_action='Improve pit routing and reach a flower naturally to test boot release/collection. Continue Metal Storm and Shinobi integration.',
        records=records)
    d=R/'docs/qa/checkpoints/2026-11-01/mario-the-tank-pickup-progress.json'
    d.write_text(json.dumps(q,indent=2)+'\n')
    p=R/'docs/qa/continuation-current.json';current=json.loads(p.read_text())
    current['previous_goal_turn_classification']='progress'
    current['mario_the_tank_natural_pickup']=str(d.relative_to(R))
    current['current_priority']='Mario the Tank natural first mushroom and growth verified on delivered7ec9. Extended route loses a life at X1549; full-stage and natural boot pickup remain unverified. Continue route/boot checks and Metal Storm/Shinobi integration; full roster goal incomplete.'
    p.write_text(json.dumps(current,indent=2)+'\n')
    print(json.dumps({k:v for k,v in q.items() if k!='records'}))
if __name__=='__main__':main()
