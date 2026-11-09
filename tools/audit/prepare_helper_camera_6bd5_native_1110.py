"""Qualify the camera-helper rebase on the exact three-component Mini build."""

import argparse
import json
from pathlib import Path
import re
import shutil

import check_helper_camera_admission_1110_v1 as Camera
import check_helper_camera_irq_1110_v1 as CameraIRQ
import check_native_platform_collision_dispatch_1110_v1 as Platform
import prepare_helper_camera_routes_1110_v1 as Routes
import prepare_mini_platform_firebar_native_1110 as Mini
from check_mini_funded_actor_1108_v3 import install
from compose_mini_frame_budget_1108 import check_full_cpu, digest, load
from prepare_mini_lane_audio_native_1110 import bound_rom, verify_interrupts, verify_parent, verify_payload
from prepare_selected_native_packet_v1 import R, prepare, sha


BUILD = R/'build'
CURRENT = BUILD/'mini-platform-firebar-native-1110/candidate.nes'
CURRENT_VECTORS = BUILD/'mini-platform-firebar-vectors-1110/proof.json'
PIN = '6bd5e4b1976e26ecccd9b7c0512944020d6eb7a6e2c8c35ab50c53d0441e7491'
SOURCE = BUILD/'helper-camera-admission-1110/proof.json'
HISTORY = SOURCE.with_name('a226-irq.json')
A226 = BUILD/'mini-lane-audio-native-1110/candidate.nes'
HISTORICAL = BUILD/'helper-camera-native-1110/candidate.nes'
HISTORICAL_PIN = '5444f3e3bcb07c8314ba6f17b067f2e678eb4ec668786456e4f26d56ba8d75a2'
THOMAS = BUILD/'helper-camera-thomas-gap-v5-1110'
GOKU = HISTORICAL.parent/'goku'
KARNOV = BUILD/'helper-camera-karnov-combat-1110'


def bind_image(output):
    raw = bound_rom(CURRENT, PIN)
    _, projected = Mini.build_image()
    assert projected == raw
    vectors = load(CURRENT_VECTORS)
    assert vectors['passed'] and vectors['candidate_SHA256'] == PIN
    assert vectors['bindings'][str(CURRENT.resolve())] == PIN
    for file, h in vectors['bindings'].items():
        assert sha(Path(file)) == h, file
    declared = bound_rom(Camera.ROM, Camera.PIN)
    _, proof, spans = verify_parent(declared, SOURCE)
    history = load(HISTORY)
    previous = bound_rom(A226, history['parent_SHA256'])
    assert digest(install(previous, proof['patches'])) == HISTORICAL_PIN
    verify_interrupts(SOURCE, HISTORY, proof | dict(parent_SHA256=digest(previous),
                                                   expected_memory_only_SHA256=HISTORICAL_PIN))
    assert bound_rom(HISTORICAL, HISTORICAL_PIN) == install(previous, proof['patches'])

    symbols = Camera.P.bundle(raw)
    placements = [(Camera.TH_CHR+Camera.TH_GATE-0xa000, Camera.TH_END-Camera.TH_GATE),
                  (Camera.P.location(symbols,'ThCookie'),16),
                  (Camera.bank_at(26,Camera.DP_TICK),Camera.DP_END-Camera.DP_TICK),
                  (Camera.bank_at(26,Camera.HP_CONFIGURE_RELEASE),3)]
    assert [(lo,hi-lo) for lo,hi,_,_ in spans] == placements
    for lo,hi,old,_ in spans:
        assert raw[lo:hi] == declared[lo:hi] == old
    for path in Mini.COMPONENTS:
        for row in load(path)['patches']:
            lo = row['file_offset']
            hi = lo+len(bytes.fromhex(row['old_hex']))
            assert all(hi <= a or lo >= b for a,b,_,_ in spans), path

    image, changes, linked, kernel, state, cookie = Camera.compose(raw,output)
    assert changes == proof['patches'] and linked == proof['symbols']
    assert image == install(raw,proof['patches']) and len(image) == len(raw)
    verify_payload(raw,Mini.NEW_KERNEL)
    verify_payload(image,Mini.NEW_KERNEL)
    assert image[Mini.CODE:Mini.CODE+7168] == raw[Mini.CODE:Mini.CODE+7168]
    assert image[Mini.COOKIE:Mini.COOKIE+16] == raw[Mini.COOKIE:Mini.COOKIE+16]
    return raw,image,proof,kernel,state,cookie


def qualify(raw, image, proof, kernel, state, cookie):
    old, new = [Camera.P.bundle(q) for q in (raw,image)]
    # The original checker reads this cartridge for both the stale Thomas
    # cookie and the foreign-owner baseline. Use the actual current parent.
    saved = Camera.ROM
    Camera.ROM = CURRENT
    try:
        seed, loader = Camera.thomas_seed(new,kernel,state,cookie)
        foreground = Camera.qualify(new,seed)
        vectors = CameraIRQ.vectors(old,new,kernel,state,cookie)
    finally:
        Camera.ROM = saved
    assert foreground['CPU'] == proof['CPU'] and foreground['spawn_relative_range'] == [256,287]
    assert loader['previous_cookie_rejected'] and vectors['owners'] == [10,24,34]
    assert all(vectors['cuts'][name] > 0 for name in ('lag_FF','IRQ','nested_IRQ'))
    print(json.dumps(dict(camera_CPU=foreground['CPU'], thomas_loader=loader, vectors=vectors)),flush=True)

    # Keep the complete current Mini runtime payload and both authentication
    # headers live in six-actor fixtures, including exact mapper and OAM state.
    pair = [Platform.scene_seed(b,3,3) for b in (old,new)]
    expected_kernel = Mini.NEW_KERNEL.read_bytes()
    expected_cookie = raw[Mini.COOKIE:Mini.COOKIE+16]
    expected_metadata = raw[Mini.CODE+5120:Mini.CODE+5120+0x300]
    attr_pin = load(Mini.PROJECTION)['exact_runtime_attribute_SHA256']
    for m in pair:
        assert bytes(m.ram[3][:5120]) == expected_kernel
        assert all(bytes(m.ram[bank][0x1fe0:0x1ff0]) == expected_cookie for bank in (2,3))
        assert bytes(m.ram[2][0x1000:0x1300]) == expected_metadata
        assert digest(m.ram[2][0x1300:0x1400]) == attr_pin
    mini_updates = 16
    for tick in range(mini_updates):
        key = 0 if tick < 8 else 192
        results = []
        for m in pair:
            Camera.N.put(m,SavedJoypadBits=key,SavedJoypad1Bits=key,VRAM_Buffer1_Offset=0,
                         VRAM_Buffer_AddrCtrl=0,NmiDisable=0)
            results.append(Camera.N.invoke(m,'GameLoop',x=0,y=0))
        assert results[0] == results[1], (tick,results)
        assert Platform.memory(pair[0]) == Platform.memory(pair[1]), tick
    core = check_full_cpu(raw,image,{})
    assert all(row['min_saved'] == row['max_saved'] == 0 for row in core)
    return dict(CPU=foreground['CPU'], thomas_loader=loader, vectors=vectors,
                Mini_GameLoop_updates=mini_updates, Mini_GameCore=core,
                Mini_kernel_SHA256=sha(Mini.NEW_KERNEL), Mini_cookie=expected_cookie.hex())


def packet_input(packet, before_rom, candidate, proof, actor):
    controller = packet/'controller.lua'
    ready_path = packet/'ready.json'
    ready = load(ready_path)
    old_sha = sha(before_rom)
    expected = digest(candidate)
    assert ready['prepared'] and not ready['emulated_writes'] and ready['ROM_sha256'] == old_sha
    assert Path(ready['ROM']).resolve() == before_rom.resolve()
    refs = {Path(p).resolve() for p in ready['bindings']}
    assert controller.resolve() in refs and before_rom.resolve() in refs
    for path,h in ready['bindings'].items():
        assert sha(Path(path)) == h, path
    text = controller.read_text(encoding='utf-8')
    assert all(token not in text for token in ('emu.write(', 'emu.reset(', 'emu.loadSavestate('))
    assert 1 <= text.count(old_sha) <= 2
    text = text.replace(old_sha,expected)
    if actor == 'mini':
        assert text.count(sha(Mini.NEW_KERNEL)) == 1
        audio = Mini.Audio
        assert text.endswith('\n'+audio.audio_config(candidate,load(audio.RUNTIME))+
                             audio.OBSERVER.read_text(encoding='utf-8'))
        hooks = re.findall(r'\["physical"\]=(\d+),\["memory"\]="nesPrgRom",'
                           r'\["bytes"\]=\{([\d,]+)\}', text)
        assert hooks
        for address,data in hooks:
            at,word = 16+int(address),bytes(map(int,data.split(',')))
            assert candidate[at:at+len(word)] == word, address
    else:
        config = re.search(r'helperCameraObserver\{owner=(\d+),tag=(\d+),pc=(\d+),',text)
        assert config
        owner,tag,pc = map(int,config.groups())
        assert owner == {'thomas':10,'goku':24,'karnov':34}[actor]
        assert tag == (3 if actor == 'thomas' else 154)
        at = Camera.TH_CHR+pc-0xa000 if tag == 3 else Camera.bank_at(26,pc)
        assert candidate[at:at+3] == bytes.fromhex('205a01'), actor
        if actor == 'goku':
            # The canonical controller builder also binds all six native
            # timing hooks to their exact instructions and physical banks.
            canonical,_ = Routes.controller(candidate,expected,proof,actor)
            assert text == canonical
        if actor in ('goku','karnov'):
            binding, result, helper = [packet/'capture'/name for name in
                                       ('binding.json','result.json','helper-camera.json')]
            q,p,h = [load(path) for path in (binding,result,helper)]
            assert q['exit_code'] == 0 and q['ready_sha256'] == sha(ready_path)
            assert q['ROM_sha256'] == h['ROM_sha256'] == old_sha and p['passed'] and p['controller_only']
            assert h['passed'] and h['owner'] == owner
            assert [r['left_x'] for r in h['placements']] == list(Camera.DP_LEFTS)
            assert all(r['crossed'] and 256 <= r['relative_left'] <= 287 for r in h['placements'])
            refs.update((binding,result,helper))
    refs.update((ready_path,controller,Path(__file__),SOURCE,HISTORY,CURRENT_VECTORS,Mini.NEW_KERNEL))
    return text,refs,ready


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--thomas-packet',type=Path,default=THOMAS)
    args = parser.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(BUILD) and output != BUILD and not output.exists()
    output.mkdir()
    raw,image,proof,kernel,state,cookie = bind_image(output)
    result = qualify(raw,image,proof,kernel,state,cookie)
    expected = digest(image)
    routes = {'mini':(CURRENT.parent/'route',CURRENT), 'thomas':(args.thomas_packet,HISTORICAL),
              'goku':(GOKU,HISTORICAL),'karnov':(KARNOV,HISTORICAL)}
    prepared = {name:packet_input(path,parent,image,proof,name) for name,(path,parent) in routes.items()}

    camera_proof = output/'camera-rebase-proof.json'
    inputs = (Path(__file__),Path(Camera.__file__),Path(CameraIRQ.__file__),CURRENT,CURRENT_VECTORS,SOURCE,
              HISTORY,Camera.TH_KERNEL,Camera.TH_STATE,Mini.NEW_KERNEL,Mini.NEW_KERNEL.with_suffix('.lbl'))
    receipt = dict(passed=True, source_CPU_only=True, native_route_pending=True,
                   parent_SHA256=PIN, expected_memory_only_SHA256=expected,
                   declared_parent_SHA256=proof['parent_SHA256'], historical_native_SHA256=HISTORICAL_PIN,
                   patches=proof['patches'], symbols=proof['symbols'], **result,
                   bindings={str(path.resolve()):sha(path) for path in inputs})
    camera_proof.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    rom = output/'candidate.nes'
    rom.write_bytes(image)
    assert sha(rom) == expected
    for ext in ('.dbg','.lbl'):
        shutil.copyfile(CURRENT.with_suffix(ext),rom.with_suffix(ext))
    manifest = rom.with_suffix('.json')
    meta = load(CURRENT.with_suffix('.json'))
    assert meta['candidate_SHA256'] == PIN and meta['kernel_SHA256'] == sha(Mini.NEW_KERNEL)
    meta.update(parent_SHA256=PIN,candidate_SHA256=expected,verification='Private native camera replay pending',
                camera_rebase_SHA256=sha(camera_proof),camera_source_proof_SHA256=sha(SOURCE),
                camera_historical_controller_SHA256=HISTORICAL_PIN)
    manifest.write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    for name,(text,refs,ready) in prepared.items():
        path = output/name
        timeout = ready['timeout']
        assert 1 <= timeout <= 450
        prepare(path,rom,text,refs | {camera_proof,manifest},expected=expected,timeout=min(timeout,240),
                scope=ready['scope'],allow_interactive=True)
        if timeout > 240:
            q = load(path/'ready.json')
            q['timeout'] = timeout
            (path/'ready.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(candidate_SHA256=expected,parent_SHA256=PIN,packets=list(routes),
                          source_CPU_passed=True,native_route_pending=True)),flush=True)


if __name__ == '__main__':
    main()
