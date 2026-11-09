"""Verify and deliver the exact Mini/Karnov manual platform and title-credit build."""

import argparse
import json
from pathlib import Path
import re
import subprocess

import compose_manual_title_1110 as C
import prepare_manual_platform_native_1110 as Manual
from deliver_helper_camera_render_1110 import mini_evidence, run
from deliver_shared_side_tank_1110 import same_mini
from deliver_shared_sparse_draw_1110 import ASSET, REPO
from nightly_patch_guard_v1 import check
from prepare_mario_tank_source_1101_v1 import apply as apply_ips
from prepare_selected_native_packet_v1 import prepare, sha
from release_expanded_playable_1030_v1 import make_ips
from check_tmnt_render_oa import address


R, NIGHTLY = C.R, C.NIGHTLY
PIN = '9906787a73b6d319cd30a2d3a89f50e4aa6892d912a9c22e9c5e19a14e581835'
PROOF = R/'build/manual-title-compose-1110/proof.json'
OLD_MINI = R/'build/mega-giant-delivery-1110/mini'
SMALL = R/'tools/audit/run_small_mesen_packet_1110.py'
SOURCE_BASE = Path('C:/NES/Super Mario Bros. (World).nes')
SOURCE_PIN = '0b3d9e1f01ed1668205bab34d6c82b0e281456e137352e4f36a9b2cfa3b66dea'
SYMBOLS = (Manual.SYMBOL_BASE.with_suffix('.lbl'), Manual.SYMBOL_BASE.with_suffix('.dbg'))
OWNERS = {'mini': 41, 'karnov': 34}
PPU_ROWS = {0x2246: '      START       ', 0x2286: '      OPTIONS     ', 0x22c6: C.CREDIT}


def qualified(rom, proof_path):
    q = C.read(proof_path)
    C.check_paths(q['bindings'])
    assert q['passed'] and not q['ROM_written'] and q['parent_SHA256'] == C.PIN
    assert q['expected_memory_only_SHA256'] == PIN
    rebuilt, rows = C.compose()
    assert rows == q['patches'] and rebuilt == rom.read_bytes() and C.digest(rebuilt) == PIN
    return rebuilt


def rebind(source, old, new):
    assert source.count(old) == 1 and new not in source
    return source.replace(old, new, 1)


def mini_source(raw):
    prior = OLD_MINI/'controller.lua'
    old = prior.read_text(encoding='utf-8')
    # Bind the same Mini entry PCs and their observed instruction bytes.
    at = 16 + 128*8192 + 962*1024
    kernel = raw[at:at+5120]
    before = C.BASE.read_bytes()
    old_hash = C.digest(before[at:at+5120])
    q = C.read(C.MANUAL)
    hooks = re.findall(r'\["([^"\n]+)"\]=\{\["name"\]="[^"]+",\["pc"\]=(\d+),'
                       r'\["physical"\]=(\d+),\["memory"\]="(nesWorkRam|nesPrgRom)",'
                       r'\["bytes"\]=\{([\d,]+)\}', old)
    assert len(hooks) == 6
    for name, pc, physical, memory, values in hooks:
        pc, physical = int(pc), int(physical)
        expected = bytes(int(v) for v in values.split(','))
        if memory == 'nesWorkRam':
            assert q['labels'][name] == pc and physical == 3*8192 + (pc & 8191)
            assert kernel[pc-0xa000:pc-0xa000+len(expected)] == expected
        else:
            assert name == 'GameCoreRoutine' and raw[16+physical:16+physical+len(expected)] == expected
    return rebind(rebind(old, C.PIN, PIN), old_hash, C.digest(kernel))


def stage_mini(out, rom, proof_path):
    raw = qualified(rom, proof_path)
    prior = mini_evidence(OLD_MINI, C.PIN)
    assert prior['cadence'] == dict(physical=3494, updates=3494, lag_nmi=0, zero_update=0)
    out.mkdir(exist_ok=True)
    prepare(out/'mini', rom, mini_source(raw), {Path(__file__), proof_path, C.MANUAL, SMALL,
            OLD_MINI/'controller.lua', OLD_MINI/'ready.json', OLD_MINI/'capture/binding.json',
            OLD_MINI/'capture/result.json'}, expected=PIN, timeout=180, allow_interactive=True,
            rom_symbols=SYMBOLS, scope='Unchanged Mini 1-1 input policy on the manual-platform and title build.')


def title_controller():
    b = Manual.W.bundle(C.BASE.read_bytes())
    addresses = {key: address(b, key) for key in ('CrossoverTitleDrawn', 'DisableScreenFlag', 'OperMode')}
    rows = ','.join(f'{{{at},{{{",".join(map(str, C.encode(text)))}}}}}' for at, text in PPU_ROWS.items())
    return f'''local rows={{{rows}}}
local frame=0
local function r(at) return emu.read(at,emu.memType.nesDebug) end
local function finish(ok,reason)
 local result=assert(io.open(OUTPUT..'result.json','w'))
 result:write(string.format('{{"passed":%s,"reason":%q,"ROM_sha256":"{PIN}","controller_only":true,"script_RAM_writes":false,"frame":%d,"PPU_start":8902,"expected_credit":"BY KANDOWONTU"}}\\n',tostring(ok),reason,frame))
 result:close()
 local image=assert(io.open(OUTPUT..'title.png','wb'))
 image:write(emu.takeScreenshot());image:close()
 emu.stop(ok and 0 or 1)
end
emu.addEventCallback(function()
 frame=frame+1
 if frame>=600 then return finish(false,'Title did not become ready') end
 if frame<70 or r({addresses['CrossoverTitleDrawn']})~=1 or r({addresses['DisableScreenFlag']})~=0 or r({addresses['OperMode']})~=0 then return end
 for _,row in ipairs(rows) do
  for i,tile in ipairs(row[2]) do
   local at=row[1]+i-1
   if at==0x224a then tile=0x2a end -- Native START selection cursor occupies this blank.
   if emu.read(at,emu.memType.nesPpuDebug)~=tile then return finish(false,string.format('Title tile mismatch at $%04X',at)) end
  end
 end
 finish(true,'Actual title START, OPTIONS and footer VRAM rows match')
end,emu.eventType.endFrame)
'''


def downloads_packets(out, proof_path):
    refs = {Path(__file__), proof_path, C.MANUAL, C.TITLE, SMALL}
    for name in OWNERS:
        previous = C.MANUAL_NATIVE/name
        source = rebind((previous/'controller.lua').read_text(encoding='utf-8'), C.MANUAL_PIN, PIN)
        prepare(out/('downloads-'+name), NIGHTLY, source, refs|{previous/'controller.lua',
                previous/'ready.json', previous/'capture/result.json', previous/'capture/binding.json'},
                expected=PIN, timeout=90, allow_interactive=True, rom_symbols=SYMBOLS,
                scope='Actual Downloads Up+Select edge, native vertical lift motion, carry, and replacement.')
    prepare(out/'downloads-title', NIGHTLY, title_controller(), refs, expected=PIN, timeout=50,
            allow_interactive=True, rom_symbols=SYMBOLS, scope='Actual title nametable rows and one screenshot.')


def downloads_evidence(out):
    evidence = {}
    for name, owner in OWNERS.items():
        packet = out/('downloads-'+name)
        reference = C.MANUAL_NATIVE/name
        assert (packet/'controller.lua').read_text(encoding='utf-8') == rebind(
            (reference/'controller.lua').read_text(encoding='utf-8'), C.MANUAL_PIN, PIN)
        result = C.manual_result(packet, NIGHTLY, PIN, owner)
        previous = C.manual_result(reference, C.MANUAL_NATIVE/'candidate.nes', C.MANUAL_PIN, owner)
        assert {k:v for k,v in result.items() if k != 'ROM_sha256'} == {
            k:v for k,v in previous.items() if k != 'ROM_sha256'}
        evidence[name] = dict(owner=owner, births=result['birth_events'], lives=result['terminal']['lives'],
                              result_SHA256=sha(packet/'capture/result.json'))
    packet = out/'downloads-title'
    title = C.native_result(packet, NIGHTLY, PIN)
    assert title['PPU_start'] == 0x22c6 and title['expected_credit'] == C.CREDIT.strip()
    assert (packet/'controller.lua').read_text(encoding='utf-8') == title_controller()
    png = packet/'capture/title.png'
    assert png.read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
    evidence['title'] = dict(PPU_start=title['PPU_start'], text=title['expected_credit'],
                             screenshot=str(png), screenshot_SHA256=sha(png),
                             result_SHA256=sha(packet/'capture/result.json'))
    return evidence


def ips_for(raw):
    original = SOURCE_BASE.read_bytes()
    assert C.digest(original) == SOURCE_PIN and len(original) < len(raw) < 0x454f46
    # The equal-length encoder treats this suffix as all changed so every
    # expansion byte is emitted, including any final zero bytes.
    template = original + bytes(x ^ 255 for x in raw[len(original):])
    patch = make_ips(template, raw)
    assert apply_ips(original, patch)[0] == raw
    return patch


def verify_mini(packet, rom, raw):
    ready = C.read(packet/'ready.json')
    assert Path(ready['ROM']).resolve() == rom and not ready['emulated_writes']
    assert (packet/'controller.lua').read_text(encoding='utf-8') == mini_source(raw)
    result = mini_evidence(packet, PIN)
    same_mini(mini_evidence(OLD_MINI, C.PIN), result)
    return result


def deliver(out, rom, proof_path, mini_packet):
    raw = qualified(rom, proof_path)
    mini = verify_mini(mini_packet, rom, raw)
    patch = ips_for(raw)
    before = check(NIGHTLY)
    assert before['ROM_sha256'] == C.PIN
    assert not any(NIGHTLY.with_suffix(ext).exists() for ext in ('.lbl', '.dbg', '.dbg.gz'))
    assert not any((out/name).exists() for name in ('verified-delivery.json', ASSET,
                                                   'downloads-mini', 'downloads-karnov', 'downloads-title'))
    out.mkdir(exist_ok=True)
    try:
        NIGHTLY.write_bytes(raw)
        assert check(NIGHTLY)['ROM_sha256'] == PIN and NIGHTLY.read_bytes() == raw
        downloads_packets(out, proof_path)
        for name in (*OWNERS, 'title'):
            run([str(SMALL), str(out/('downloads-'+name)/'run.py')])
        actual = downloads_evidence(out)
        guard = check(NIGHTLY)
        assert guard['ROM_sha256'] == PIN and apply_ips(SOURCE_BASE.read_bytes(), patch)[0] == NIGHTLY.read_bytes()
        ips = out/ASSET
        ips.write_bytes(patch)
        q = dict(installed=True, Downloads_launch_verified=True, backup_created=False, IPS_roundtrip=True,
                 ROM_SHA256=PIN, previous_ROM_SHA256=C.PIN, before=before, after=guard,
                 base_SHA256=SOURCE_PIN, IPS_SHA256=sha(ips), IPS_bytes=ips.stat().st_size,
                 candidate_proof_SHA256=sha(proof_path), candidate_mini_packet=str(mini_packet),
                 candidate_mini_result_SHA256=sha(mini_packet/'capture/result.json'),
                 mini_cadence=mini['cadence'], mini_existing_lifts=mini['lifts'], actual_Downloads=actual)
        (out/'verified-delivery.json').write_text(json.dumps(q, indent=2)+'\n', encoding='utf-8')
    except (Exception, KeyboardInterrupt):
        NIGHTLY.write_bytes(C.BASE.read_bytes())
        assert check(NIGHTLY)['ROM_sha256'] == C.PIN
        raise
    print('Verified exact Downloads ROM and clean-base IPS:', PIN, flush=True)


def publish(out, rom, proof_path):
    raw = qualified(rom, proof_path)
    path, ips = out/'verified-delivery.json', out/ASSET
    q = C.read(path)
    assert q['Downloads_launch_verified'] and q['IPS_roundtrip'] and not q['backup_created']
    assert q['candidate_proof_SHA256'] == sha(proof_path) and q['ROM_SHA256'] == check(NIGHTLY)['ROM_sha256'] == PIN
    mini_packet = Path(q['candidate_mini_packet'])
    mini = verify_mini(mini_packet, rom, raw)
    assert q['candidate_mini_result_SHA256'] == sha(mini_packet/'capture/result.json') and q['mini_cadence'] == mini['cadence']
    assert q['actual_Downloads'] == downloads_evidence(out)
    assert q['IPS_SHA256'] == sha(ips) and ips.read_bytes() == ips_for(NIGHTLY.read_bytes())
    notes = out/'release-notes.txt'
    notes.write_text('Current MMC5 work-in-progress nightly.\n\n'
                     'Apply this IPS to clean, headered Super Mario Bros. (World).\n'
                     f'Base SHA-256 {SOURCE_PIN}\nPatched ROM SHA-256 {PIN}\n\n'
                     'Mini Mario and Karnov can press Up + Select in gameplay to create a moving '
                     'vertical platform beneath them. A fresh press replaces their previous platform. '
                     'If every native actor slot is occupied, the request waits for one to open.\n\n'
                     'The title screen reads BY KANDOWONTU. The exact candidate passed the existing '
                     'Mini Mario 1-1 route with both lives, and the installed Downloads ROM passed '
                     'both manual-platform checks and the title screen check.\n', encoding='utf-8')

    def release(endpoint):
        return json.loads(subprocess.check_output(['gh', 'api', f'repos/{REPO}/releases/{endpoint}'], encoding='utf-8'))

    current = release('tags/Current')
    existing, = current['assets']
    assert current['tag_name'] == 'Current' and existing['name'] == ASSET
    digest = 'sha256:'+q['IPS_SHA256']
    if existing['digest'] != digest:
        subprocess.run(['gh', 'release', 'upload', 'Current', str(ips), '--clobber', '--repo', REPO], check=True)
    subprocess.run(['gh', 'release', 'edit', 'Current', '--latest', '--notes-file', str(notes), '--repo', REPO], check=True)
    latest = release('latest')
    asset, = latest['assets']
    assert latest['tag_name'] == 'Current' and latest['id'] == current['id']
    assert asset['name'] == ASSET and asset['digest'] == digest and asset['size'] == ips.stat().st_size
    q.update(release_tag='Current', release_is_latest=True, sole_asset=ASSET,
             release_asset_digest=digest, final_patch_guard=check(NIGHTLY))
    path.write_text(json.dumps(q, indent=2)+'\n', encoding='utf-8')
    print('Verified sole Current asset and Latest status:', digest, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'deliver', 'publish'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--proof', type=Path, default=PROOF)
    parser.add_argument('--mini-packet', type=Path)
    args = parser.parse_args()
    out, rom, proof = args.output.resolve(), args.rom.resolve(), args.proof.resolve()
    assert out.is_relative_to(R/'build') and out != R/'build'
    if args.action == 'prepare':
        stage_mini(out, rom, proof)
    elif args.action == 'deliver':
        assert args.mini_packet
        deliver(out, rom, proof, args.mini_packet.resolve())
    else:
        publish(out, rom, proof)


if __name__ == '__main__':
    main()
