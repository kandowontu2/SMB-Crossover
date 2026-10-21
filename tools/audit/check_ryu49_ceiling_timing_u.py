"""Retain the old ceiling negative and test actual source-disjoint launch timing.

The candidate's original broad-suite failure is never replaced. This component
uses the same twenty seeded arenas; only the two ceiling timing assertions are
revised against independently pinned source bounds, with real banked probes.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import shutil
import sys
import time
import xml.etree.ElementTree as ET

R = Path(__file__).resolve().parents[2]
H = R / 'build/verification/root49-ryu-ceiling-timing-u'
P = R / 'build/verification/agent-lsr-s2-head-n2-a'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def prepare():
    assert not H.exists()
    original = R / 'tests/ryu-ground-wall-launch.lua'
    suite = json.loads((P / 'root-qa-suite-a/report.json').read_text())
    assert suite['status'] == 'FAIL_RETAINED_PRIVATE_HEAD_REGRESSIONS'
    assert suite['cases'] == 759
    assert sha(original) == suite['fixture_and_runner_hashes']['tests/ryu-ground-wall-launch.lua']
    source = R / 'reference/crossover2'
    assert sha(source / 'main.xml') == '8edb72ebad459813b25303ce1f27d8df35e5a01192690d6e4d2ce23ce5e685df'
    assert sha(source / 'source.swf') == '6374c72426556bfc3cc16f7594ce4443a5867fe2d367514136c99cc8458b70af'
    sys.path.insert(0, str(R / 'tools/reference'))
    from prepare_crossover import frames
    items = list(ET.parse(source / 'main.xml').getroot().iter('item'))
    sprites = {i.get('spriteId'): i for i in items if i.get('type') == 'DefineSpriteTag'}
    hrect = next(i for i in sprites['14'].iter('item') if i.get('type') == 'PlaceObject2Tag')
    assert hrect.get('characterId') == '13'
    shape = next(i for i in items if i.get('type') == 'DefineShapeTag' and i.get('shapeId') == '13')
    assert [int(shape.find('shapeBounds').get(k)) for k in ('Xmin', 'Ymin', 'Xmax', 'Ymax')] == [0, 0, 160, 160]
    rects = []
    for f in frames(sprites['106']):
        for placement in f['display'].values():
            if placement.get('characterId') == '14':
                m = placement['matrix']
                assert not float(m.get('rotateSkew0', 0)) and not float(m.get('rotateSkew1', 0))
                top, bottom = float(m['translateY']) / 40, (float(m['translateY']) + 160 * float(m['scaleY'])) / 40
                rects.append(dict(frame=f['frame'], labels=f['labels'], top_NES=top,
                                  bottom_NES=bottom, matrix=m))
    # The pinned unrotated body family never extends above the 27px envelope.
    assert rects and all(q['top_NES'] >= -27.001 for q in rects)
    stand = next(q for q in rects if q['frame'] == 1)
    falling = next(q for q in rects if q['frame'] == 23)
    assert stand['top_NES'] == -27 and falling['top_NES'] == -25
    text = original.read_text()
    def replace(old, new):
        nonlocal text
        assert text.count(old) == 1, old
        text = text.replace(old, new)
    replace("local sourceLaunchVy,ceilingReceipts=nil,0", "local sourceLaunchVy,ceilingReceipts=nil,0\nlocal ceilingFirst,ceilingLater,ceilingHead,ceilingHeadEnd,ceilingFirstNative")
    replace("active=q;firstJump=false;", "active=q;ceilingFirst=nil;ceilingLater=nil;ceilingHead=nil;ceilingHeadEnd=nil;ceilingFirstNative=0;firstJump=false;")
    needle = " row('completed-collision',launches[1])"
    replace(needle, needle + "\n if active.kind=='ceiling'and launchCount>0 then\n  local v={age=age,yQ=r('Player_Y_Position')*65536+r('MmYFraction')+256*r('MmYFraction',1),vyQ=math.floor(velocity()*65536+.5),native=r('Player_Y_Speed')}\n  if not ceilingFirst then ceilingFirst=v elseif v.native<128 and v.vyQ>=0 then ceilingLater=v end\n end")
    old = "if q.kind=='ceiling'then check(j.yspeed<128 and ceilingReceipts>0,'actual overhead collision still reaches native stop and stops rising motion')"
    new = """if q.kind=='ceiling'then
    -- Independent source envelope: foot=PY+32, largest HRect height=27.
    -- Launch -540/120 plus gravity1400/7200 is Q16 -282169, so even
    -- the largest body's first top is176.69444, below the ceiling bottom176.
    local expectedVy=-294912+12743
    local expectedY=176*65536+expectedVy
    check(ceilingFirst and ceilingFirst.yQ==expectedY and ceilingFirst.vyQ==expectedVy,'source-disjoint first update retains full integrated position and velocity')
    check(expectedY+5*65536>176*65536,'pinned largest27px source body is strictly disjoint from the roof')
    check(ceilingHead and ceilingHead.yQ==expectedY and ceilingHead.vyQ==expectedVy,'actual guarded first head query sees source-disjoint body')
    check(ceilingHeadEnd and ceilingHeadEnd.yQ==expectedY and ceilingHeadEnd.vyQ==expectedVy,'actual complete head continuation preserves the disjoint source position and velocity')
    check(ceilingFirstNative==0,'disjoint first update cannot execute native ceiling stop')
    check(ceilingReceipts>0 and ceilingLater and ceilingLater.age>ceilingFirst.age,'actual later overhead collision still reaches native stop and stops rising motion')"""
    replace(old, new)
    probe = r'''
-- Additive read-only observers, admitted against the actual physical bank and
-- eight ROM bytes. Existing fixture setup and all eighteen other arenas stay.
local function ceilingValid(h)
 local p=emu.convertAddress(h.address)
 if not p or p.memType~=emu.memType.nesPrgRom or p.address//8192~=h.bank then return false end
 for i,b in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==b,'ceiling physical8 '..h.name)end
 return true
end
for _,h in ipairs(CEILING_HOOKS)do
 emu.addMemoryCallback(function()
  if not active or active.kind~='ceiling'or interruptDepth~=0 or launchCount==0 or not ceilingValid(h)then return end
  if h.name=='Head'and not ceilingHead then
   ceilingHead={age=age,yQ=r('Player_Y_Position')*65536+r('MmYFraction')+256*r('MmYFraction',1),vyQ=math.floor(velocity()*65536+.5)}
   row('guarded-first-head-entry')
  elseif h.name=='HeadEnd'and ceilingHead and not ceilingHeadEnd then
   ceilingHeadEnd={age=age,yQ=r('Player_Y_Position')*65536+r('MmYFraction')+256*r('MmYFraction',1),vyQ=math.floor(velocity()*65536+.5)}
   row('guarded-first-head-end')
  elseif h.name=='Stop'and not ceilingFirst then ceilingFirstNative=ceilingFirstNative+1 end
 end,emu.callbackType.exec,h.address)
end
'''
    replace("local function finish()", probe + "\nlocal function finish()")
    H.mkdir()
    core = H / 'revised-ceiling.lua'
    core.write_text(text)
    shutil.copyfile(original, H / 'original-ceiling.lua')
    sys.path.insert(0, str(R / 'build/verification/agent49g-samus-crouch-fix-proposal-b'))
    from image import Image, lua
    bindings = []
    for variant in ['control-s2', 'candidate-n2']:
        for mapper in ['mmc3', 'mmc5']:
            folder = H / (variant + '-' + mapper)
            (folder / 'tests').mkdir(parents=True)
            shutil.copyfile(R / 'tests/menu-bootstrap.lua', folder / 'tests/menu-bootstrap.lua')
            rom = (R if variant == 'control-s2' else P / 'source') / ('build/smb-crossover-' + mapper + '.nes')
            im = Image(rom)
            hooks = []
            for name, label in [('Head', 'PlayerHeadProbe'), ('HeadEnd', 'DoFootCheck'), ('Stop', 'NYSpd')]:
                h = im.hook(label)
                hooks.append(dict(name=name, address=h['address'], bank=h['physical_bank'], bytes=h['bytes']))
            fixture = folder / 'tests/ryu-ground-wall-launch.lua'
            fixture.write_text(original.read_text() if variant == 'control-s2' else 'CEILING_HOOKS=' + lua(hooks) + '\n' + text)
            bindings.append(dict(variant=variant, mapper=mapper, folder=str(folder),
                fixture=str(fixture), fixture_sha256=sha(fixture), ROM=str(rom), ROM_sha256=sha(rom),
                compiled=im.metadata(), hooks=hooks))
    refs = [original, R / 'tests/menu-bootstrap.lua', R / 'tools/run_mesen.py', P / 'root-qa-suite-a/report.json',
            source / 'main.xml', source / 'source.swf', source / 'extracted/scripts/com/smbc/characters/Character.as',
            source / 'extracted/scripts/com/smbc/characters/Ryu.as', R / 'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py']
    report = dict(status='PREPARED_SOURCE_CEILING_TIMING_COMPONENT_NOT_EXECUTED', script_sha256=sha(__file__),
        references={str(p.relative_to(R)): sha(p) for p in refs}, bindings=bindings,
        original_fixture_sha256=sha(H / 'original-ceiling.lua'), revised_core_sha256=sha(core),
        source_rectangles=rects, first_integrated_vy_Q16=-282169, first_integrated_y_Q16=11252167,
        source_envelope_first_top_Q16=11579847, roof_bottom_Q16=11534336,
        runtime_changes=False, source_fixture_changes=False,
        limits='Twenty explicit seeded native arenas. Source envelope rejection and later genuine stop, not ordinary traversal or full wall/ceiling source fidelity. The original759-pass/two-fail suite remains intact.')
    (H / 'preparation.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PREPARED', sha(H / 'preparation.json'), flush=True)


def run(name):
    prep = json.loads((H / 'preparation.json').read_text())
    assert sha(__file__) == prep['script_sha256']
    b = next(b for b in prep['bindings'] if b['variant'] + '-' + b['mapper'] == name)
    folder = Path(b['folder'])
    report = folder / 'result.json'
    assert not report.exists()
    assert sha(b['ROM']) == b['ROM_sha256'] and sha(b['fixture']) == b['fixture_sha256']
    assert all(sha(R / n) == h for n, h in prep['references'].items())
    spec = importlib.util.spec_from_file_location('isolated_runner', R / 'tools/run_mesen.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = folder
    start = time.monotonic()
    code = module.run(Path(b['fixture']), Path(b['ROM']), timeout=120)
    result = dict(status='PASS' if code == 0 else 'NEGATIVE_RETAINED', native_exit=code,
        elapsed_seconds=time.monotonic()-start, binding=b,
        artifacts={str(p.relative_to(folder)): dict(sha256=sha(p), bytes=p.stat().st_size)
                   for p in (folder / 'build/verification').glob('*') if p.is_file()},
        explicit_seeded_arenas=True, route_proof=False, runtime_changes=False)
    report.write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'], name, sha(report), flush=True)
    raise SystemExit(code)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run')
    args = parser.parse_args()
    run(args.run) if args.run else prepare()
