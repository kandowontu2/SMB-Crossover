"""Prepare/review one small controller-only 1-1 run. Never launches Mesen.

No archived policies, source/runtime copies, fixture seeds or old receipt forest.
The caller launches the printed central-guard command separately after review.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import re
import struct
import zlib

from final_inventory_compact_capture_v1 import records, verify

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).with_suffix('.lua')
CURRENT = 'fb2a608e4670788c0a170d6a17e7802b226e9e6933cd44103cb1b9212db54eed'
BASE = {
    'mario': (0, 0, 'MarioVariant', 0), 'luigi': (0, 8, 'MarioVariant', 1),
    'megaman': (1, 1, 'ProtoVariant', 0), 'proto': (1, 1, 'ProtoVariant', 1),
    'samus': (2, 2, None, 0), 'bill': (3, 3, 'BillVariant', 0), 'lance': (3, 3, 'BillVariant', 1),
    'link': (4, 4, 'Z2Variant', 0), 'zelda2': (4, 4, 'Z2Variant', 1),
    'simon': (5, 5, 'Cv3Variant', 0), 'grant': (5, 5, 'Cv3Variant', 1),
    'sypha': (5, 5, 'Cv3Variant', 2), 'alucard': (5, 5, 'Cv3Variant', 3),
    'pit': (6, 6, None, 0), 'rygar': (7, 7, None, 0),
    'scrooge': (8, 12, 'DarkwingVariant', 0), 'darkwing': (8, 12, 'DarkwingVariant', 1),
    'bass': (9, 9, 'RlVariant', 0), 'roll': (9, 9, 'RlVariant', 1),
    'ryu': (10, 10, None, 0), 'sophia': (11, 11, None, 0),
    'kirby': (12, 13, 'KbVariant', 0), 'meta': (12, 13, 'KbVariant', 1),
    'chip': (13, 14, 'CdVariant', 0), 'dale': (13, 14, 'CdVariant', 1),
    'mac': (14, 15, None, 0), 'mike': (15, 16, None, 0),
    'mario3': (16, 17, 'M3Variant', 0), 'luigi3': (16, 17, 'M3Variant', 1),
    'vic': (17, 18, 'VvVariant', 0), 'octopus': (17, 18, 'VvVariant', 1),
    'twinbee': (17, 18, 'VvVariant', 2), 'pentarou': (17, 18, 'VvVariant', 3),
    'leonardo': (18, 19, 'TnVariant', 0), 'raphael': (18, 19, 'TnVariant', 1),
    'michelangelo': (18, 19, 'TnVariant', 2), 'donatello': (18, 19, 'TnVariant', 3),
}
MARKERS = ['first-active', 'corner-332', 'corner-345', 'corner-360',
           'power-change', 'flagpole', 'endpoint', 'failure']


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def lua(value):
    if value is None:
        return 'nil'
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, dict):
        return '{'+','.join('['+lua(str(k))+']='+lua(v) for k, v in value.items())+'}'
    if isinstance(value, list):
        return '{'+','.join(lua(v) for v in value)+'}'
    return json.dumps(value)


def linked(rom):
    syms, segs = {}, {}
    with rom.with_suffix('.dbg').open() as f:
        for line in f:
            if not line.startswith(('sym\t', 'seg\t')):
                continue
            q = dict(p.split('=', 1) for p in line[4:].strip().split(',') if '=' in p)
            if line.startswith('seg\t'):
                segs[q['id']] = q
            elif 'val' in q:
                syms[q['name'].strip('"')] = q
    raw = rom.read_bytes()
    def address(name):
        return int(syms[name]['val'], 0)
    def location(name):
        s = syms[name]; g = segs[s['seg']]
        return int(g['ooffs'], 0)+address(name)-int(g['start'], 0)
    def hook(name, tail=False, offset=0):
        delta = int(syms[name]['size'], 0)-1 if tail else offset
        at = location(name)+delta
        if tail:
            assert raw[at] in (0x40, 0x60), (name, 'Genuine final RTI/RTS')
        return dict(name=name, pc=address(name)+delta, bank=(at-16)//8192, bytes=list(raw[at:at+3]))
    return raw, syms, address, location, hook


def policy_for(name):
    if name in ('megaman', 'proto', 'bass'):
        return 'megaman_bass_v34_policy.lua'
    if name in ('samus', 'bill', 'lance'):
        return 'roster_samus_contra.lua'
    if name in ('mario', 'luigi'):
        return 'mario_luigi_scrooge_policy.lua'
    if name in ('link', 'simon', 'ryu'):
        return 'link_simon_ryu_policy.lua'
    if name in ('pit', 'rygar', 'sophia'):
        return 'pit_rygar_sophia_dry_policy.lua'
    return 'full_roster_policy_og.lua'


def policy_dependencies(path):
    found, pending = set(), [path.resolve()]
    while pending:
        p = pending.pop()
        if p in found:
            continue
        assert p.is_relative_to(ROOT/'tools/playthroughs'), 'Only surviving tracked controller files'
        source = p.read_text()
        assert not re.search(r'\bemu\.(?:write\w*|setState|setInput|loadSavestate|reset)\s*\(', source), p
        assert 'io.open' not in source, ('Policy adds an undeclared output', p)
        found.add(p)
        for rel in re.findall(r'''dofile\(root\.\.["']([^"']+)["']''', source):
            pending.append(ROOT/rel.lstrip('/'))
    return found


def navigation(raw, location, target):
    edges = {key: list(raw[location('X5Menu'+key.title()):location('X5Menu'+key.title())+19])
             for key in ('left', 'right', 'up', 'down')}
    answer = []
    for start in range(19):
        queue, seen = [(start, [])], {start}
        for node, route in queue:
            if node == target:
                answer.append(route[0] if route else '');break
            for key, table in edges.items():
                next_node = table[node]
                assert 0 <= next_node < 19
                if next_node not in seen:
                    seen.add(next_node);queue.append((next_node, route+[key]))
        else:
            raise AssertionError('Menu target unreachable')
    return answer


def prepare(a):
    rom, out = a.rom.resolve(), a.output.resolve()
    assert out.is_relative_to(ROOT/'build') and out != ROOT/'build'
    assert not out.exists() or not any(out.iterdir()), 'One fresh isolated run directory, no overwrite'
    assert 600 <= a.frames <= 8000
    assert sha(rom) == a.expected_sha256
    raw, syms, address, location, hook = linked(rom)
    assert raw[:4] == b'NES\x1a' and ((raw[6]>>4)|(raw[7]&0xf0)|((raw[8]&15)<<8)) == 5
    menu_index, character, variant_symbol, variant = BASE[a.identity]
    policy = (a.policy or ROOT/'tools/playthroughs'/policy_for(a.identity)).resolve()
    policies = policy_dependencies(policy)
    menu_char = raw[location('X5MenuCharacters')+menu_index]
    assert menu_char == (0 if character == 8 else character)
    post = location('PostDmaMaskEnable')
    assert raw[post-3:post] == b'\x8d\x14\x40'
    mirror = address('Mirror_PPUMASK')
    load = bytes([0xa5, mirror]) if mirror < 256 else bytes([0xad, mirror&255, mirror>>8])
    assert raw[post:post+len(load)+3] == load+b'\x8d\x01\x20'
    hooks = dict(loop=hook('GameLoop'), loop_return=hook('GameLoop', tail=True),
                 nmi=hook('NonMaskableInterrupt'), nmi_return=hook('NonMaskableInterrupt', tail=True),
                 irq=hook('IrqScrollSplit'), irq_return=hook('IrqScrollSplit', tail=True),
                 dma_complete=hook('PostDmaMaskEnable', offset=len(load)))
    cfg = dict(name=a.identity, character=character, menu_index=menu_index,
               variant_symbol=variant_symbol, variant=variant, mode_value=0 if a.mode=='easy' else 1,
               root=ROOT.as_posix(), out=out.as_posix()+'/', prefix=out.as_posix()+'/',
               policy=policy.as_posix(), limit=a.frames, capture_bytes=512*1024*1024,
               ROM_sha256=a.expected_sha256, navigation=navigation(raw, location, menu_index),
               marker_names=MARKERS, hooks=hooks, dma_store_return=address('PostDmaMaskEnable'),
               smc_fields=[address(n)+1 for n in ('NextBank_SMC', 'SafecallA_SMC', 'SafereturnA_SMC', 'FarcallJmpTarget_SMC')]
                          +[address('FarcallJmpTarget_SMC')+2],
               replay=a.replay.resolve().as_posix() if a.replay else None)
    text = SCRIPT.read_text()
    refs = set(re.findall(r'''\br\(['"]([^'"]+)['"]''', text))
    for f in policies:
        refs.update(re.findall(r'''\br\(['"]([^'"]+)['"]''', f.read_text()))
    if variant_symbol:
        refs.add(variant_symbol)
    assert not(refs-syms.keys()), ('Required actual labels unavailable', sorted(refs-syms.keys()))
    assert not re.search(r'emu\.(?:write\w*|setState|loadSavestate|reset)\s*\(', text)
    assert 'menu-bootstrap' not in text.replace('-- No menu-bootstrap,', '')
    bass_observer = ROOT/'tools/audit/bass_corner_native_observer_v1.lua'
    bass = a.identity == 'bass'
    if bass:
        for n in ('PlayerBGCollision', 'SamusAfterBGCollisionBridge', 'MegaMan202AfterBG', 'SamusStopAtWallBanked', 'MmVY', 'MmYFraction', 'SmCeilingHit'):
            assert n in syms, n
    dependencies = policies | {SCRIPT, Path(__file__), ROOT/'tools/audit/final_inventory_compact_capture_v1.lua',
        ROOT/'tools/audit/final_inventory_compact_capture_v1.py', ROOT/'tools/audit/run_mesen_isolated.py',
        ROOT/'tools/run_mesen.py', ROOT/'tools/audit/capture_budget.py', rom, rom.with_suffix('.dbg'), rom.with_suffix('.lbl')}
    if bass:
        dependencies.add(bass_observer)
    if a.replay:
        dependencies.add(a.replay.resolve())
    out.mkdir(parents=True, exist_ok=True)
    run = out/'run.lua'
    run.write_text('ROSTER_CONFIG='+lua(cfg)+'\n'+
        ('ROSTER_CONFIG.bass_close=dofile('+lua(bass_observer.as_posix())+')(ROSTER_CONFIG.prefix)\n' if bass else '')+
        'dofile('+lua(SCRIPT.as_posix())+')\n', encoding='utf-8')
    dependencies.add(run)
    command = ['python', '-B', str(ROOT/'tools/audit/run_mesen_isolated.py'), '--output', str(out),
               '--emulator', 'C:/Mesen2/Mesen.exe', str(run), str(rom), '--timeout', '600',
               '--option=--doNotSaveSettings', '--option=--nes.removeSpriteLimit=false',
               '--option=--nes.ramPowerOnState=AllZeros', '--option=--nes.randomizeCpuPpuAlignment=false',
               '--option=--nes.randomizeMapperPowerOnState=false']
    receipt = dict(prepared=True, native_run=False, ROM_sha256=sha(rom), config=cfg, command=command,
                   bindings={str(q): sha(q) for q in sorted(dependencies)},
                   current_policy_status='Surviving tracked discovery policy, NOT a current-ROM clear proof',
                   max_total_frames=8000, container_cap_bytes=cfg['capture_bytes'], central_run_cap_bytes=2_000_000_000,
                   screenshot_files_during_native=0, maximum_offline_selected_frames=8,
                   no_source_runtime_clones=True, no_emulated_writes=True, no_cheats=True,
                   explicit_endpoint='World0/Level0 seen; natural World0/Level1 entry; >=25 completed active updates and >5px control there; zero deaths',
                   remaining_dependencies='Only listed current build/debug/labels, tracked scripts/controllers and existing C:/Mesen2 runtime/settings. No deleted archive inputs, Lua/Python package downloads or capture bridge.')
    (out/'ready.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(dict(prepared=True, native_run=False, ready=str(out/'ready.json'),
                         ready_sha256=sha(out/'ready.json'), bindings=len(dependencies),
                         tracked_policy_files=len(policies), command=command), indent=2))


def png(path, raw_images):
    """One contact sheet of at most eight actual ARGB buffers, no frame tree."""
    count = len(raw_images);assert 0 < count <= 8
    cols = min(2, count);rows = (count+cols-1)//cols;w,h=cols*256,rows*240
    pixels = bytearray(w*h*4)
    for image, raw in enumerate(raw_images):
        col,row=image%cols,image//cols
        for y in range(240):
            for x in range(256):
                word = struct.unpack_from('<I', raw, (y*256+x)*4)[0]
                p=((row*240+y)*w+col*256+x)*4
                pixels[p:p+4]=bytes([(word>>16)&255,(word>>8)&255,word&255,(word>>24)&255])
    def chunk(kind, data):
        return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    lines=b''.join(b'\0'+pixels[y*w*4:(y+1)*w*4] for y in range(h))
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(lines,9))+chunk(b'IEND',b''))


def review(a):
    out=a.ready.resolve().parent;ready=json.loads(a.ready.read_text());cfg=ready['config']
    assert all(sha(p)==h for p,h in ready['bindings'].items()), 'Actual prepared inputs changed'
    result=json.loads((out/'result.json').read_text())
    decoded=verify(out/'captures.nesppuv1',out/'captures-index.jsonl')
    trace=list(csv.DictReader((out/'trace.csv').open(newline='')))
    inputs=list(csv.DictReader((out/'inputs.csv').open(newline='')))
    assert result['frames']==len(trace) and result['polls']==len(inputs)
    assert [int(q['poll']) for q in inputs]==list(range(1,len(inputs)+1))
    assert result['full_frames']==decoded['full_frames']
    assert result['ROM_sha256']==ready['ROM_sha256'] and result['identity']==cfg['name']
    events=[json.loads(q) for q in (out/'events.jsonl').read_text().splitlines()]
    markers=[q['data']['name'] for q in events if q['kind']=='capture-marker'];assert len(markers)<=8
    actual_aliases=[q for q in decoded['named_capture_index'] if q['type']=='alias']
    assert [q['name'] for q in actual_aliases]==[n+'.argb' for n in markers]
    assert result['adapter']['screenshots']==result['adapter']['per_frame_files']==0
    comparison=None
    if a.compare:
        before=a.compare.resolve().parent
        comparison=dict(inputs_exact=(out/'inputs.csv').read_bytes()==(before/'inputs.csv').read_bytes(),
                        trace_exact=(out/'trace.csv').read_bytes()==(before/'trace.csv').read_bytes())
        previous=verify(before/'captures.nesppuv1',before/'captures-index.jsonl')
        comparison['PPU_stream_exact']=previous['decoded_full_sha256']==decoded['decoded_full_sha256']
        assert all(comparison.values()), 'Independent replay differs; retain original and current outputs'
    sheet=None
    if a.sheet and markers:
        by_record={q['record']:q['name'][:-5] for q in actual_aliases};images={}
        for q,raw in records(out/'captures.nesppuv1'):
            if q['record'] in by_record:images[by_record[q['record']]]=raw
        names=[n for n in markers if n in images];target=out/'selected-whole-frames.png';assert not target.exists()
        png(target,[images[n] for n in names]);sheet=dict(path=str(target),sha256=sha(target),placements=[dict(name=n,row=i//2,column=i%2,source=result['markers'][n]) for i,n in enumerate(names)])
    proof=dict(passed=bool(result['passed'] and result['zero_deaths'] and result['cheats_off'] and result['actual_mode']==cfg['mode_value']),
               native=result,container=decoded,independent_replay=comparison,selected_whole_frames=sheet,
               agent_visual_review=False,visual_scope='Images prepared only; no automatic all-pixel/art/physics verdict',
               ready_sha256=sha(a.ready),outputs={q.name:sha(q) for q in out.iterdir() if q.is_file() and q.name!='review.json'})
    target=out/'review.json';assert not target.exists();target.write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(passed=proof['passed'],proof=str(target),proof_sha256=sha(target),full_frames=decoded['full_frames'],sheet=sheet),indent=2))


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    q=sub.add_parser('prepare');q.add_argument('--identity',choices=BASE,default='bass');q.add_argument('--mode',choices=('easy','hard'),default='hard')
    q.add_argument('--rom',type=Path,default=ROOT/'build/smb-crossover-mmc5-expanded.nes');q.add_argument('--expected-sha256',default=CURRENT)
    q.add_argument('--output',type=Path,required=True);q.add_argument('--frames',type=int,default=8000);q.add_argument('--policy',type=Path);q.add_argument('--replay',type=Path)
    q=sub.add_parser('review');q.add_argument('--ready',type=Path,required=True);q.add_argument('--compare',type=Path);q.add_argument('--sheet',action='store_true')
    a=p.parse_args();prepare(a) if a.action=='prepare' else review(a)


if __name__=='__main__':
    main()
