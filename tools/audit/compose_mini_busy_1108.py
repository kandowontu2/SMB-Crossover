"""Compose and compare the independently proved Mini busy-frame changes."""
import argparse
import json
from pathlib import Path
import shutil

from prepare_mini_no_wall_1108 import BASE, CURRENT
from prepare_prince_resume_1108 import NIGHTLY
from prepare_mini_mario_native_power_1103_v56 import N, bundle
from prepare_selected_native_packet_v1 import R, sha
from profile_mini_busy_1108_v1 import fixture

FIRE = R/'build/mini-busy-fire-1108-v1/result.json'
PARSER = R/'build/mini-parser-health-1108-v1/health-fold.json'
GEOMETRY = R/'build/mini-motion-fast-1108/candidate.nes'


def load(path):
    return json.loads(path.read_text())


def apply_patch(raw, offset, before, after):
    before, after = bytes.fromhex(before), bytes.fromhex(after)
    assert len(before) == len(after) and raw[offset:offset+len(before)] == before, hex(offset)
    raw[offset:offset+len(after)] = after


def compare(a, b):
    assert a[:0x100] == b[:0x100] and a[0x200:0x8000] == b[0x200:0x8000]
    assert a.rawtags == b.rawtags
    for index, (left, right) in enumerate(zip(a.ram, b.ram, strict=True)):
        # Authenticated ROM bytes and the two moved temporary coordinate
        # pairs are the only exclusions. Output tile/flags/address stay live.
        excluded = {2: [(0x274,0x278),(0x2e0,0x2e4),(0x1fe3,0x1ff0)],
                    3: [(0,5120),(0x1fe3,0x1ff0)]}.get(index, [])
        assert all(x == y or any(lo <= offset < hi for lo,hi in excluded)
                   for offset, (x,y) in enumerate(zip(left,right,strict=True))), index
    for field in ('oam','ppuctrl','ppumask','chr_regs','ppu_vram'):
        assert getattr(a,field,None) == getattr(b,field,None), field


def verify(images):
    cases = []
    for enemies, terrain, parser, powered in [(0,False,False,False),(2,True,False,False),
                                             (4,False,True,False),(5,False,False,True)]:
        pair = [fixture(b,enemies,terrain,parser) for b in images]
        if powered:
            for memory in pair:
                N.put(memory,PlayerStatus=2,PlayerSize=0)
        costs = []
        for frame in range(2,38):
            if powered:
                key = 64 if frame in (5,7,23,26) else 0
            else:
                key = (1 if frame < 28 else 2) | (128 if 10 <= frame <= 24 else 0)
            result = []
            for memory in pair:
                N.put(memory,FrameCounter=frame,SavedJoypadBits=key,SavedJoypad1Bits=key,
                      VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0)
                result.append(N.invoke(memory,'GameCoreRoutine',x=0,y=0))
            assert all(result[0][n] == result[1][n] for n in ('A','X','Y','P')), (frame,result)
            compare(*pair)
            costs.append([row['CPU'] for row in result])
        savings = [old-new for old,new in costs]
        assert min(savings) > 0
        cases.append(dict(enemies=enemies,terrain=terrain,parser=parser,powered=powered,
                          updates=len(costs),mean_cycles_saved=sum(savings)/len(savings),
                          min_saving=min(savings),max_saving=max(savings),
                          worst_before=max(r[0] for r in costs),worst_after=max(r[1] for r in costs)))
    return cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert sha(BASE) == CURRENT
    motion = load(GEOMETRY.with_name('candidate.json'))
    fire, parser_proof = load(FIRE), load(PARSER)
    assert motion['parent_SHA256'] == fire['parent_SHA256'] == parser_proof['base_SHA256'] == CURRENT
    assert fire['passed'] and parser_proof['passed'] and sha(GEOMETRY) == motion['candidate_SHA256']
    for proof, key in [(motion,'bindings'),(fire,'source_bindings'),(parser_proof,'bindings')]:
        for path,digest in proof[key].items():
            source = R/Path(path)
            if source.resolve() == NIGHTLY.resolve():
                source = BASE  # The retained byte-identical baseline survives nightly replacement.
            assert sha(source) == digest, path
    raw = bytearray(GEOMETRY.read_bytes())
    for row in fire['patches']:
        apply_patch(raw,row['offset'],row['preimage'],row['replacement'])
    for row in parser_proof['patches']:
        apply_patch(raw,row['file_offset'],row['old_hex'],row['new_hex'])
    cases = verify([bundle(BASE.read_bytes()),bundle(raw)])
    args.output.mkdir()
    candidate = args.output/'candidate.nes'
    candidate.write_bytes(raw)
    for ext in ('.lbl','.dbg'):
        shutil.copyfile(BASE.with_suffix(ext),candidate.with_suffix(ext))
    report = dict(passed=True,candidate_SHA256=sha(candidate),parent_SHA256=CURRENT,
                  whole_GameCore=cases,wall_grab_removed=False,
                  scope='Native CPU fixtures compare state, actor motion, CHR and OAM. Actual Mesen cadence is measured separately.',
                  bindings={str(path):sha(path) for path in (Path(__file__),BASE,GEOMETRY,FIRE,PARSER)})
    (args.output/'candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
