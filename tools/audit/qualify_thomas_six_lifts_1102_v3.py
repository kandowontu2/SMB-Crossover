"""Require all six observed crossings and active1-2 from the exact candidate."""
import json
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha

def main():
    root=R/'build/thomas-current-candidate-1102-v3'
    packet=root/'native-six-lifts'
    ready=json.loads((packet/'ready.json').read_text())
    binding=json.loads((packet/'capture/binding.json').read_text())
    result=json.loads((packet/'capture/result.json').read_text())
    pin='d0b445a71d6c539804d7c559fafc2c328ebf97ab4e35e8f3273f94ff8a25d01d'
    assert sha(root/'candidate.nes')==ready['ROM_sha256']==binding['ROM_sha256']==result['ROM_sha256']==pin
    assert binding['ready_sha256']==sha(packet/'ready.json') and binding['exit_code']==0
    for name,digest in ready['bindings'].items(): assert sha(name)==digest,name
    assert result['passed'] and result['reason']=='Full1-1 active1-2'
    assert [p['pipe_X'] for p in result['pipe_clears']]==[448,608,736,912,2608,2864]
    assert all(p['X']>=p['pipe_X']+48 for p in result['pipe_clears'])
    for name in ['nmi','irq','vectors','software_rti','software_target']:
        assert result['counters'][name]>0,name
    assert len(list((packet/'capture').glob('*.png')))<=4
    receipt=dict(passed=True,native=True,installed=False,ROM_sha256=pin,
                 frames=result['frames'],Main=result['Main'],pipe_clears=result['pipe_clears'],
                 scope='Thomas only: cold selection/lives/game art, native six-lift crossings and non-shortcut1-1 into active1-2 with unchanged lives; actual ISR observations. No all-powerup/both-mode/audio qualification.',
                 helper_additions=[dict(stage='1-1',left_x=x,center_x=x+16,initial_y=192,width=32) for x in [2560,2816]],
                 bindings={str(p):sha(p) for p in [Path(__file__),packet/'ready.json',packet/'capture/binding.json',packet/'capture/result.json',root/'composition.json']})
    (root/'native-qualified.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))

if __name__=='__main__':main()
