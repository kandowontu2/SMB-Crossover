"""Install the exact qualified camera/render composition, then replay Downloads."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

import deliver_mini_nightly_root_1103_v30 as delivery
from prepare_selected_native_packet_v1 import sha

PREVIOUS = '6bd5e4b1976e26ecccd9b7c0512944020d6eb7a6e2c8c35ab50c53d0441e7491'
PLACEMENTS = {'thomas': (10, (400,560,688,864,2560,2816),192),
              'goku': (24, (688,872),208), 'karnov': (34, (688,872),208)}


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def bindings(rows):
    for path, digest in rows.items():
        assert sha(Path(path)) == digest, path


def camera_evidence(root, pin, overrides):
    evidence = {}
    for name, (owner, lefts, top) in PLACEMENTS.items():
        packet = overrides.get(name) or root/name
        ready = read(packet/'ready.json')
        binding = read(packet/'capture/binding.json')
        result = read(packet/'capture/result.json')
        helper = read(packet/'capture/helper-camera.json')
        assert ready['ROM_sha256'] == binding['ROM_sha256'] == helper['ROM_sha256'] == pin
        assert binding['exit_code'] == 0 and binding['ready_sha256'] == sha(packet/'ready.json')
        bindings(ready['bindings'])
        assert result['passed'] and helper['passed'] and ready['emulated_writes'] is False
        if name != 'thomas':
            assert result['controller_only']
        if 'ROM_sha256' in result:
            assert result['ROM_sha256'] == pin
        assert not result.get('script_RAM_writes', False)
        assert helper['owner'] == owner
        assert tuple(row['left_x'] for row in helper['placements']) == lefts
        for row in helper['placements']:
            assert row['initial_y'] == top and row['center_x'] == row['left_x']+16
            assert row['crossed'] and 256 <= row['relative_left'] <= 287
            assert 'board_x' in row and 'board_y' in row
        if name == 'goku':
            assert result['full_stage'] and result['initial_lives'] == result['final_lives']
        elif name == 'karnov':
            assert result['stage_complete'] and not result['died']
        else:
            assert result['reason'] == 'Full1-1 active1-2'
        evidence[name] = helper
    return evidence


def mini_evidence(packet, pin):
    result = delivery.proof(packet, pin)
    assert result['full_stage'] and result['last']['lives'] == 2
    end = result['terminal_native']
    assert (end['WorldNumber'],end['LevelNumber'],end['GameEngineSubroutine']) == (0,1,8)
    lifts = result['phases']['fullstage']['lifts']
    assert tuple(row['left'] for row in lifts) == (560,688,864)
    assert all(row['boarded'] and row['departed'] and row['spawn_relative_x'] >= 256 for row in lifts)
    audio = read(packet/'capture/audio-order.json')
    timing = read(packet/'capture/timing.json')
    assert audio['ROM_sha256'] == timing['ROM_sha256'] == pin
    assert audio['packed_frames'] == audio['packed_status_writes'] > 3000
    return dict(audio=audio, cadence=timing['cadence']['fullstage'], lifts=lifts)


def run(argv):
    q = subprocess.run([sys.executable,'-B',*argv], text=True, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT)
    print(q.stdout[-1800:], flush=True)
    assert q.returncode == 0, (argv,q.returncode)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    for name in PLACEMENTS:
        parser.add_argument('--'+name+'-packet', type=Path)
    args = parser.parse_args()
    root, out = args.candidate.resolve(), args.output.resolve()
    pin = sha(root/'candidate.nes')
    proof = read(root/'proof.json')
    assert proof['passed'] and proof['parent_SHA256'] == PREVIOUS and proof['candidate_SHA256'] == pin
    assert len(proof['groups']) == 4
    bindings(proof['bindings'])
    for group in proof['group_source_bindings'].values():
        bindings(group)
    overrides = {name:getattr(args,name+'_packet') for name in PLACEMENTS}
    cameras = camera_evidence(root,pin,overrides)
    mini = mini_evidence(root/'mini',pin)
    common = ['--candidate',str(root),'--route',str(root/'mini'),
              '--idle',str(root/'native/idle'),'--power',str(root/'native/power'),
              '--fire',str(root/'native/fire'),'--output',str(out),'--previous',PREVIOUS]
    installer = 'tools/audit/deliver_mini_lifts_art_1108.py'
    run([installer,'install',*common])
    run([str(out/'downloads-smoke/run.py')])
    assert mini_evidence(out/'downloads-smoke',pin) == mini
    run([installer,'finalize',*common])
    path = out/'verified-delivery.json'
    receipt = read(path)
    assert receipt['Downloads_launch_verified'] and receipt['IPS_roundtrip']
    receipt.update(camera_routes=cameras, composite_proof_SHA256=sha(root/'proof.json'),
                   native_audio=mini['audio'], previous_comparable_missed_reads=306,
                   lag_free=mini['cadence']['no_controller_read'] == 0)
    path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    notes = out/'release-notes.txt'
    text = notes.read_text(encoding='utf-8')
    text += ('\nThomas, Goku and Karnov helper platforms now spawn beyond the screen edge '
             'and scroll into view. All authored assisted crossings pass native full-stage tests. '
             'Shared relative-position, offscreen, Goomba edge rendering and native platform '
             'bounding-box paths use fewer CPU cycles. '
             f'The Mini route records {mini["cadence"]["no_controller_read"]} missed reads '
             f'over {mini["cadence"]["physical"]} physical frames; previous build: 306/3506. '
             'Busy-stage zero-lag work remains in progress.\n')
    notes.write_text(text,encoding='utf-8')
    print(json.dumps(dict(delivered=True,ROM_SHA256=pin,IPS_SHA256=receipt['IPS_SHA256'],
                          cadence=mini['cadence'])),flush=True)


if __name__ == '__main__':
    main()
