"""Resolve a suspected CF score-HUD anomaly using actual passive PPU reads."""
from pathlib import Path
import csv
import hashlib
import json

R = Path(__file__).resolve().parents[2]
O = R/'build/contra-force-score-queue-analysis-1031-v1'
N = R/'build/contra-force-score-queue-native-1031-v2/burns'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists()
    ready = json.loads((N/'ready.json').read_text())
    binding = json.loads((N/'capture/binding.json').read_text())
    result = json.loads((N/'capture/result.json').read_text())
    for q in [ready,binding]:
        for path,digest in q['bindings'].items():
            assert sha(path)==digest,path
    assert binding['exit_code']==0 and result['passed']
    assert binding['ready_sha256']==sha(N/'ready.json')
    assert ready['ROM_sha256']==binding['ROM_sha256']==result['ROM_sha256']
    rows = list(csv.DictReader((N/'capture/score-lifecycle.csv').open()))
    # The fixed126 FloateyCore hook cannot alias physical RAM3. The additional
    # diagnostic A-window helper hooks used convertAddress without checking its
    # memory type and include RAM3 coincidences; exclude them as execution proof.
    valid = [q for q in rows if q['hook'] in ['FloateyCore','finish']]
    assert len(valid)==result['main_updates']+1
    first_score = next(q for q in valid if q['score']=='0:0:0:0:1:0')
    first_ppu = next(q for q in valid if q['PPU2062']=='36:0:0:0:1:0')
    assert 0<=int(first_ppu['Main'])-int(first_score['Main'])<=2
    assert all(q['score']=='0:0:0:0:0:0' for q in valid if int(q['Main'])<int(first_score['Main']))
    assert all(q['score']=='0:0:0:0:1:0' for q in valid if int(q['Main'])>=int(first_score['Main']))
    assert all(q['PPU2062']=='36:0:0:0:1:0' for q in valid if int(q['Main'])>=int(first_ppu['Main']))
    assert valid[-1]['pending']=='0' and result['native_defeats']==1
    assert result['earned']['original_impact_verified']
    files=[Path(__file__),N/'ready.json']+list((N/'capture').glob('*'))
    O.mkdir()
    q=dict(passed=True,native=True,ROM_sha256=ready['ROM_sha256'],
           suspected_HUD_bug_reproduced=False,product_change_required=False,
           actual_native_earned_defeats=1,score_value_points=100,
           first_internal_score=first_score,first_hardware_PPU_score=first_ppu,
           endpoint=valid[-1],fixed_bank_qualified_observations=len(valid),
           diagnosis='Native score storage and PPU2062 numeric tiles update normally. The earlier screenshot reading was mistaken; the earned-shot image precedes normal delayed score credit.',
           observer_limit='A-window helper execution hooks in the passive diagnostic include RAM3/ROM3 address coincidences because convertAddress memory type was not checked. They are not used to establish call counts or product behavior here. Fixed126 FloateyCore and direct PPU/RAM reads establish this conclusion.',
           root_reviewed_full_frame_PNGs={p.name:sha(p) for p in (N/'capture').glob('*.png')},
           bindings={str(p.resolve()):sha(p) for p in files if p.is_file()})
    out=O/'controls.json';out.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,output=str(out),sha256=sha(out),first_internal_Main=first_score['Main'],first_PPU_Main=first_ppu['Main'],product_change_required=False)))


if __name__=='__main__':
    main()
