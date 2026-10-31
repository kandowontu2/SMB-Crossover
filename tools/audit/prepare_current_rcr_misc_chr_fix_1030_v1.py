"""Move RCR's mandatory ink away from native misc sprites, source-only build."""
from pathlib import Path
import difflib
import hashlib
import json
import re
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R/'tools/audit'), str(R/'tools')]
from private_build_outputs_v1 import validate
from current_roster_compact_11_v1 import linked
from prepare_cv3_dmc_mirror import prepare

P = R/'build/celeste-menu-name-current-v2/joint'
O = R/'build/current-rcr-misc-chr-fix-1030-v1'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(p, data):
    p.write_text(json.dumps(data,indent=2)+'\n')


def run(command, phase):
    outputs = validate(command,O,cwd=R)
    save(O/(phase+'-outputs.json'),outputs)
    completed = subprocess.run(command,cwd=R,capture_output=True,text=True)
    save(O/(phase+'.json'),dict(command=command,returncode=completed.returncode,
                               stdout=completed.stdout,stderr=completed.stderr))
    assert completed.returncode == 0, completed.stderr[-5000:]


def main():
    assert not O.exists()
    assert sha(P/'candidate.nes') == 'a7ccbaaa7aab598d36e8806e30475eab36174ee1948f25f90ae72e6640f43f48'
    h = json.loads((P.parent/'handoff.json').read_text())
    for f,digest in h['bindings'].items():
        assert sha(f) == digest, f
    O.mkdir()
    # A complete small source tree avoids include precedence accidentally
    # selecting an older adjacent .inc. Every inherited object stays read-only.
    copied = []
    for p in P.rglob('*'):
        if p.is_file() and p.suffix in {'.s','.inc','.cfg'}:
            q = O/p.relative_to(P)
            q.parent.mkdir(parents=True,exist_ok=True)
            q.write_bytes(p.read_bytes())
            copied.append(q)
    patches = []
    p = O/'src/river_city_required_ink_v1.inc'
    old = p.read_text()
    needle = 'lda RcInkChr\n ldy #1\n jsr Window'
    assert old.count(needle) == 1
    new = old.replace(needle,'lda RcInkChr\n ldy #5\n jsr Window')
    new = new.replace('; A single source pose owns two1KB windows; never remap world/effect2/3.',
                      '; Body0/ink5 preserve native misc1 and enemy2/3 windows.')
    p.write_text(new)
    patches += list(difflib.unified_diff(old.splitlines(True),new.splitlines(True),
                        fromfile='parent/river_city_required_ink_v1.inc',tofile='new/river_city_required_ink_v1.inc'))
    p = O/'src/river_city_shared_palette_art.inc'
    old = p.read_text()
    lines, active, header, records, parts = [], False, False, 0, 0
    for line in old.splitlines(True):
        label = re.fullmatch(r'(\w+):\s*',line.strip())
        if label:
            active = re.fullmatch(r'RcV[01]Ink\d+[RL]',label[1]) is not None
            header = active
            records += int(active)
        if active and re.match(r'\s*\.byte\s+',line):
            if header:
                header = False
            else:
                match = re.match(r'(\s*\.byte\s+)([0-9]+)(,.*)',line)
                assert match, line
                tile = int(match[2]); assert 0x40 <= tile <= 0x7e and tile&1 == 0
                line = match[1]+str(tile|1)+match[3]+ ('\n' if line.endswith('\n') else '')
                parts += 1
        lines.append(line)
    assert records == 72 and parts > 300, (records,parts)
    new = ''.join(lines)
    p.write_text(new)
    patches += list(difflib.unified_diff(old.splitlines(True),new.splitlines(True),
                        fromfile='parent/river_city_shared_palette_art.inc',tofile='new/river_city_shared_palette_art.inc'))
    (O/'source.patch').write_text(''.join(patches))
    p = O/'private.cfg'
    cfg = p.read_text().replace(str(P),str(O)).replace(P.as_posix(),O.as_posix())
    p.write_text(cfg)
    compile_cmd = json.loads((P/'label-main-build.json').read_text())['command']
    compile_cmd = [v.replace(str(P),str(O)) for v in compile_cmd]
    # Source assets may still resolve through the immutable donor/source roots.
    compile_cmd[1:1] = ['--bin-include-dir',str(P),'--bin-include-dir',str(P/'src')]
    link_cmd = json.loads((P/'label-link.json').read_text())['command']
    # Rewrite outputs/config/new Main only; all other inherited objects retain
    # their original exact paths, preventing implicit rebuilds or mutation.
    link_cmd = [v.replace(str(P/'candidate'),str(O/'candidate'))
                 .replace(str(P/'private.cfg'),str(O/'private.cfg'))
                 .replace(str(P/'main.o'),str(O/'main.o')) for v in link_cmd]
    inputs = {Path(v):sha(v) for v in link_cmd if v.endswith('.o') and Path(v)!=O/'main.o'}
    run(compile_cmd,'compile-main')
    run(link_cmd,'link')
    prepare(R,O/'candidate.nes')
    assert all(sha(f)==digest for f,digest in inputs.items())
    oldraw, oldsyms, addr, loc, _ = linked(P/'candidate.nes')
    raw, syms, _, _, _ = linked(O/'candidate.nes')
    assert len(raw) == len(oldraw) and raw[:16] == oldraw[:16]
    assert all(name in syms and sym['val']==syms[name]['val'] for name,sym in oldsyms.items())
    expected = set()
    for name in oldsyms:
        if re.fullmatch(r'RcV[01]Ink\d+[RL]',name):
            at = loc(name); size = oldraw[at]; assert size%4==0
            for off in range(1,size+1,4):
                expected.add(at+off)
                assert raw[at+off] == oldraw[at+off]|1
    at = loc('RcPublish')
    block = oldraw[at:at+int(oldsyms['RcPublish']['size'],0)]
    match = bytes([0xad,addr('RcInkChr')&255,addr('RcInkChr')>>8,0xa0,1,0x20])
    assert block.count(match)==1
    expected.add(at+block.index(match)+4)
    changes = {i for i,(a,b) in enumerate(zip(oldraw,raw)) if a!=b}
    assert changes == expected and len(changes)==parts+1, (len(changes),parts)
    assert raw[1048592:] == oldraw[1048592:], 'All CHR is unchanged'
    for f,digest in h['bindings'].items():
        assert sha(f)==digest, f
    files = set(copied)|set(inputs)|{Path(__file__).resolve(),P.parent/'handoff.json',P/'candidate.nes',
        R/'tools/audit/private_build_outputs_v1.py'}|{q for q in O.rglob('*') if q.is_file()}
    proof = dict(passed=True,native=False,admitted=False,installed=False,
        parent_ROM_sha256=sha(P/'candidate.nes'),ROM_sha256=sha(O/'candidate.nes'),
        parent_bindings_verified=len(h['bindings']),source_ink_records=records,source_ink_parts=parts,
        changed_ROM_bytes=len(changes),changed_file_offsets=sorted(changes),
        changed_sources=['src/river_city_required_ink_v1.inc','src/river_city_shared_palette_art.inc'],
        all_prior_symbol_values_header_CHR_and_other_PRG_exact=True,
        source_semantics='RCR body stayswindow0; intrinsic ink moveswindow1 to5 using only tile bit0. Native misc1, enemies2/3 and all source pixels/art bytes remain available.',
        limits=['Source build only. Actual palette-index body equivalence, native misc pixels, fullgame/foreign/ISR and native routes remain required.'],
        bindings={str(f):sha(f) for f in sorted(files)})
    save(O/'source-proof.json',proof)
    print(json.dumps({k:proof[k] for k in ['passed','ROM_sha256','source_ink_parts','changed_ROM_bytes','parent_bindings_verified']}))


if __name__=='__main__':
    main()
