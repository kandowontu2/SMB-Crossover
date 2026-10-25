"""Compose frozen Mac v7 music onto accepted529 without installing sources."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from check_tmnt_audio_fallback_oc import qualified

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT = '52918588bab0eec3f3a1f857bf084d2d799e88a5c781c75233c098ccc5f54f3f'
DONOR = 'f4c6a5b12d33ece173da71ba40933e1368b749d8e44c7b81a6774073df120b9b'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(exist_ok=False)
    donor = D/'mac-native-music-v1/proposal-v7'
    parent = ROOT/'build/smb-crossover-mmc5-expanded.nes'
    assert sha(parent)==PARENT and sha(donor/'candidate.nes')==DONOR
    bindings = json.loads((donor/'source-bindings.json').read_text(encoding='utf-8'))
    for name, expected in bindings.items():
        assert sha(donor/'source'/name)==expected, name
    performance = D/'mac-native-music-v1/performance-v7-vs-parent.json'
    native = D/'mac-native-music-v1/native-music-v7/native-result.json'
    cpu = D/'mac-native-music-v1/cpu-final-v7/proof.json'
    for path in [performance, native, cpu]:
        assert json.loads(path.read_text(encoding='utf-8'))['passed'], path
    source = out/'source'
    shutil.copytree(ROOT/'src', source/'src')
    shutil.copytree(ROOT/'inc', source/'inc')
    shutil.copy2(ROOT/'smb1base-mmc5-expanded.cfg', source/'smb1base-mmc5-expanded.cfg')
    old_source = out/'baseline-source'
    files = {}
    for name in bindings:
        current = ROOT/name
        raw = current.read_bytes() if current.exists() else None
        target = source/name
        if raw is not None:
            saved = old_source/name
            saved.parent.mkdir(parents=True, exist_ok=True)
            saved.write_bytes(raw)
        if name=='src/mac_native_music.s':
            assert raw is None
            target.write_bytes((donor/'source'/name).read_bytes().replace(b'\r\n', b'\n'))
        else:
            eol = b'\r\n' if b'\r\n' in raw else b'\n'
            replacements = {
                'src/entrypoint.s': (b'.include "gradius_audio.s"', b'.include "gradius_audio.s"\n.include "mac_native_music.s"'),
                'src/gradius_audio.s': (b'  jmp ExpandedAudioTick', b'  jmp LmNativeMusicGate'),
                'smb1base-mmc5-expanded.cfg': (b'    VIC_NATIVE_AUDIO:load=X5_NEW_7A,type=ro;', b'    VIC_NATIVE_AUDIO:load=X5_NEW_7A,type=ro;\n    MAC_NATIVE_AUDIO:load=X5_NEW_7B,type=ro;'),
                'src/collision.s': (b'  .res 44,$ea\n  .assert *-SmallPlatformCollision=63',
                    b'::LmNativeMusicGate:\n  lda SelectedCharacter\n  cmp #15\n  bne LmNativeMusicLegacy\n  BankPRGA #.bank(LmNativeMusicUpdate)\n  jmp LmNativeMusicUpdate\nLmNativeMusicLegacy:\n  jmp ExpandedAudioTick\n  .res 26,$ea\n  .assert *-SmallPlatformCollision=63')}
            before, after = [v.replace(b'\n',eol) for v in replacements[name]]
            assert raw.count(before)==1, name
            target.write_bytes(raw.replace(before, after))
        files[name] = dict(before_sha256=hashlib.sha256(raw).hexdigest() if raw is not None else None,
                           after_sha256=sha(target), donor_sha256=bindings[name])
    for suffix in ['.nes','.dbg','.lbl','.map']:
        shutil.copy2(parent.with_suffix(suffix), out/('baseline'+suffix))
    command = [sys.executable, str(ROOT/'tools/build_mmc5_expanded.py'), '--source-overlay', str(source)]
    with (out/'compile.log').open('w', encoding='utf-8') as log:
        subprocess.run(command+['--output',str(out/'candidate.nes')], cwd=ROOT, check=True, stdout=log, stderr=subprocess.STDOUT)
    old, new, repair = parent.read_bytes(), (out/'candidate.nes').read_bytes(), (donor/'candidate.nes').read_bytes()
    assert old[:16]==new[:16] and old[16+1048576:]==new[16+1048576:]
    changed = [i for i,(x,y) in enumerate(zip(old,new)) if x!=y]
    banks = [38,123,126]
    assert sorted({(i-16)//8192 for i in changed})==banks
    for bank in range(128):
        span = slice(16+bank*8192,16+(bank+1)*8192)
        assert new[span]==(repair if bank in banks else old)[span], bank
    before, after = qualified(parent), qualified(out/'candidate.nes')
    assert all(after.get(name)==value for name,value in before.items()), 'Old qualified PC/RAM moved'
    ordinary = {}
    for mapper, expected in [('mmc3','d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),
                             ('mmc5','f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:
        target=out/('ordinary-'+mapper+'.nes')
        with (out/(mapper+'-compile.log')).open('w',encoding='utf-8') as log:
            subprocess.run(command+['--flag-off',mapper,'--output',str(target)],cwd=ROOT,check=True,stdout=log,stderr=subprocess.STDOUT)
        assert sha(target)==expected
        ordinary[mapper]=expected
    proof = dict(composed=True, native_qualified=False, adopted=False, goal_complete=False,
                 parent_ROM_sha256=PARENT, donor_ROM_sha256=DONOR, ROM_sha256=sha(out/'candidate.nes'),
                 changed_bytes=len(changed), changed_PRG_banks=banks,
                 donor_repaired_banks_exact=True, all_other_complete_banks_exact=True,
                 old_qualified_symbols=len(before), retained_PC_RAM_CHR_exact=True,
                 fixed_DPCM_exact=True, new_RAM_bytes=0, new_CHR_bytes=0,
                 source_files=files, ordinary_target_hashes=ordinary,
                 donor_receipts={str(path):sha(path) for path in [performance,native,cpu]},
                 tool_sha256=sha(Path(__file__)),
                 scope='Private current529 composition only. Original raw source line endings retained; new Mac file uses LF. Must independently qualify actual current-hash source/audio/hardware/cadence before installation.')
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(proof,indent=2))


if __name__=='__main__':
    main()
