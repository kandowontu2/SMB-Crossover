"""Timing-only Mesen trial with an explicitly temporary PRG placement."""

import json

import check_dkjr_constant_service_trial_1123 as Service
import compose_dkjr_scene_hot_1123 as Scene
import run_sparse_sprite_scan_native_1123 as Native


BANK = 65
CURRENT = Native.Current
PREVIOUS = Native.Previous
TIMING = Native.Timing


def offset(pc):
    return 16 + BANK * 8192 + (pc & 8191)


def probe(raw):
    assert TIMING.H(raw) == Scene.PIN
    assembly = Scene.Head.assemble(Service.SOURCE.read_text(), {
        'TRIAL': (Service.TRIAL, 110),
        'EARLY_TRIAL': (Service.EARLY, 110),
    })
    code = assembly['images']['EARLY_TRIAL']
    image = bytearray(Scene.compose(raw))
    begin = offset(Service.EARLY)
    image[begin:begin + len(code)] = code
    for pc in Service.SERVICES:
        target = 0xA7E4 if pc in (0xB0B0, 0xB0B3) else 0xAF9D
        at = offset(pc)
        assert image[at:at + 3] == bytes((0x4C, target & 255, target >> 8))
        image[at:at + 3] = bytes((0x4C, Service.EARLY & 255, Service.EARLY >> 8))
    return bytes(image), len(code)


def controller(template, digest, code_size, trial):
    assert template.count(TIMING.PIN) == 1
    text = template.replace(TIMING.PIN, digest, 1)
    field = 'phases=phases,terminal=state(),'
    assert text.count(field) == 1
    text = 'local probeHits=0\n' + text.replace(field, field + 'probe_hits=probeHits,', 1)
    first, last = Service.EARLY, Service.EARLY + code_size - 1
    if trial:
        text += f'''
emu.addMemoryCallback(guarded(function(addr)
 local p=emu.convertAddress(addr)
 if p and p.memType==emu.memType.nesPrgRom and p.address=={offset(first) - 16} then
  probeHits=probeHits+1
 end
end),emu.callbackType.exec,{first},{first})
'''
    else:
        text += f'''
local function checkSample(addr)
 local p=emu.convertAddress(addr)
 if p and p.memType==emu.memType.nesPrgRom and p.address=={BANK}*8192+(addr%8192) then
  probeHits=probeHits+1
  error('The original opening used the timing trial address')
 end
end
emu.addMemoryCallback(guarded(checkSample),emu.callbackType.read,{first},{last})
emu.addMemoryCallback(guarded(checkSample),emu.callbackType.exec,{first},{last})
'''
    PREVIOUS.LuaRuntime().compile(text)
    return text.encode()


def main():
    downloads = PREVIOUS.check(TIMING.ROM)
    raw = TIMING.ROM.read_bytes()
    candidate, code_size = probe(raw)
    reference = CURRENT.reference(raw)
    roster = PREVIOUS.roster(raw)
    script_template = CURRENT.controller(reference, roster['DONKEY KONG JR'])
    work = TIMING.SHARED
    rom, script = work / 'candidate.nes', work / 'controller.lua'
    assert set(work.iterdir()) == {rom, script} and rom.read_bytes() == raw
    PREVIOUS.require_free_workspace(TIMING.R, TIMING.ROM, allow_interactive=True)
    original = script.read_bytes()
    try:
        for trial, path, image in ((False, TIMING.ROM, raw), (True, rom, candidate)):
            digest = TIMING.H(image)
            if trial:
                rom.write_bytes(candidate)
            assert PREVIOUS.check(path)['ROM_sha256'] == digest
            script.write_bytes(controller(script_template, digest, code_size, trial))
            result = PREVIOUS.run(script, path, work / 'capture', digest, 90)
            assert not result['outputs_written'] and not result['images']
            receipt = result['receipt']
            metrics = {key: receipt.get(key) for key in (
                'reason', 'probe_hits', 'phases', 'terminal', 'inclusive_video_frames',
                'measured_Main', 'Main_return_histogram', 'native_lag_NMI', 'inclusive_Main_costs',
            )}
            print(json.dumps(dict(trial=trial, ROM=digest, receipt_SHA256=result['receipt_SHA256'],
                                  metrics=metrics), separators=(',', ':')), flush=True)
            assert result['passed'], receipt['reason']
            assert (receipt['probe_hits'] > 0) == trial
    finally:
        rom.write_bytes(raw)
        script.write_bytes(original)
        assert set(work.iterdir()) == {rom, script} and rom.read_bytes() == TIMING.ROM.read_bytes() == raw
        assert PREVIOUS.check(TIMING.ROM) == downloads


if __name__ == '__main__':
    main()
