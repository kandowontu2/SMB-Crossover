"""Executed passive private-X registration/target mocks; no game CPU or edits."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

import replay_dkjr_fourth_private_x_bc5_1115 as F
import check_dkjr_fourth_first_loss_registration_v2_1115 as M

H = lambda value: sha256(value).hexdigest()

EXPOSE = '''
function host.privateXRow()return flFirst.private_x_decrease end
function host.witnessCount()local n=0;for _ in pairs(flFirst)do n=n+1 end;return n end
'''


def run(raw, prior_text):
    text, descriptor = F.from_probe_text(prior_text, raw)
    config, _ = F.bindings(raw)
    lua = M.runtime(raw)
    lua.execute(text)
    host = lua.globals().host
    labels = M.labels(lua)
    assert len(host.callbacks) == 36 and len(host.events) == 2
    assert labels['first-loss privateXwrite'] == 1
    assert labels['first-loss wall entry'] == 0
    assert labels['first-loss support entry'] == labels['first-loss plane entry'] == 1
    assert host.events[1]['label'] == 'input' and host.events[2]['label'] == 'frame'
    assert lua.globals().guarded is None
    for row in list(host.callbacks.values()):
        if row['kind'] == 1:lua.execute(f'host.exec({row["first"]},220,0)')
        else:row['fn'](row['first'], 0)
    host.events[1]['fn']();host.events[2]['fn']()
    assert host.status is None and len(host.prints) == 0

    probe = M.runtime(raw)
    probe.execute(text+M.EXPOSE+EXPOSE)
    probe.execute('host.armObserver()')
    qhost = probe.globals().host
    qhost.mem[2*8192+0x213] = 72
    qhost.mem[0x71f], qhost.mem[0x71d] = 80, 3
    qhost.mem[2*8192+0x435], qhost.mem[2*8192+0x436] = 79, 3
    qhost.mem[2*8192+0x438], qhost.mem[0x571] = 1, 79
    qhost.mem[2*8192+0x56] = 96
    fn = next(row['fn'] for row in qhost.callbacks.values()
              if row['label'] == 'first-loss privateXwrite')
    # A wrong bank mapping is rejected before any capture.
    fn(F.SOURCE_X, 71)
    assert qhost.privateXRow() is None
    probe.execute('''local old=emu.convertAddress
function emu.convertAddress(pc)
 if pc==0xc213 then return{memType=emu.memType.nesWorkRam,address=2*8192+0x213}end
 return old(pc)
end''')
    fn(F.SOURCE_X, 72)
    assert qhost.privateXRow() is None
    writer = config['writers'][0]
    for i, value in enumerate(writer['near_bytes']):
        qhost.mem[writer['observed_post_pc']-6+i] = value
    qhost.cpu['cpu.pc'] = writer['observed_post_pc']
    qhost.cpu['cpu.x'] = 16
    qhost.cpu['cpu.a'] = 71
    fn(F.SOURCE_X, 71)
    row = qhost.privateXRow()
    assert row is not None and row['old_source_x'] == 72 and row['new_source_x'] == 71
    assert row['source_x'] == 72 and row['PC'] == writer['observed_post_pc']
    assert row['X'] == 16 and row['known_writer'] == 'camera-shift-indexed'
    assert row['known_window_matches'] and row['writer_pc'] == writer['store_pc']
    assert row['camera_cached'] == 847 and row['camera'] == 848 and row['camera_delta'] == 1
    assert row['fraction_x'] == 96 and row['world_relative_x'] == 80
    assert row['anchor_source_x'] == 72 and row['anchor_world_x'] == 928
    fn(F.SOURCE_X, 70)
    assert qhost.privateXRow()['new_source_x'] == 71 and qhost.witnessCount() == 2
    assert qhost.status is None and len(qhost.prints) == 0
    assert F.restore_v2(text, raw) == prior_text
    report = dict(passed=True, ROM_SHA256=F.PIN,
        parent_Lua_SHA256=F.V2_LUA_SHA, Lua_SHA256=H(text.encode()),
        executed_registration=dict(memory_callbacks=36, event_callbacks=2,
            global_guarded_still_nil=True, all_inactive_closures_and_events_executed=True,
            labels=dict(sorted(labels.items()))),
        private_X_mock=dict(wrong_mapping_rejected=True, nondecrease_rejected=True,
            first_decrease_only=True, indexed_camera_writer_PC=writer['store_pc'],
            actual_write_target=F.SOURCE_X, WorkRAM_mapping=F.SOURCE_X_MAPPING,
            known_runtime_code_window_verified=True, captured_old_private_X=72,
            old_mock_camera=847, current_mock_camera=848, source_delta=1,
            PC_after_store_is_explicit=True),
        binding_preimages=descriptor, exact_v2_v1_ed3e_restoration=True,
        maximum_specific_witnesses=8, controls_changed=False, game_writes=False,
        scope='Executed Lua observer API mocks only; native writer not yet observed',
        output_files=0, PNGs=0)
    encoded = json.dumps(report, sort_keys=True, separators=(',', ':'))
    print('DKJR_FOURTH_PRIVATE_X_REGISTRATION '+encoded, flush=True)
    print('DKJR_FOURTH_PRIVATE_X_REGISTRATION_SHA256 '+H(encoded.encode()), flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--from-probe', type=Path)
    args = ap.parse_args()
    raw = F.V2.V1.F.Prior.Early.Old.NIGHTLY.read_bytes()
    prior = (args.from_probe.read_bytes().decode() if args.from_probe
             else F.V2.controller(raw)[0])
    run(raw, prior)
