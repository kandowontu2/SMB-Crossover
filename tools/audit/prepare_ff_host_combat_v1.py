"""Link native FF target/damage consumers into the offline RAM3 image."""
from pathlib import Path
import json
import re
import subprocess
import sys
from prepare_ff_ram3_kernel_v1 import R, P, sha, write
from prepare_ff_current_component_v2 import qualified
from finalize_ff_current_component_v3 import dependencies
from check_tmnt_render_oa import location

K = R/'build/final-fantasy-ram3-kernel-v1'
O = R/'build/final-fantasy-host-combat-v1'
SOURCE = R/'tools/reference/final_fantasy_host_combat_v1.s'


if __name__ == '__main__':
    assert not O.exists()
    proof_path = K/'build-proof.json'
    proof = json.loads(proof_path.read_text())
    assert proof['passed'] and sha(K/'ram3.bin') == '9f8a0a9034232dd110670e02285dec3bf5c1fdcebb6a6851362fa60a862ecc51'
    for path, digest in proof['bindings'].items():
        assert sha(path) == digest, path
    b = qualified(P/'linked/candidate.nes')
    O.mkdir()
    write(O/'combat.s', SOURCE.read_text())
    for name in ['component.s','publisher.s']:
        write(O/name, (K/name).read_text())
    health_at = location(b, 'MegaManWeapons::HealthTable202')
    health = b['raw'][health_at:health_at+21]
    assert health == bytes([100,100,100,100,100,200,75,150,100,100,75,75,255,75,100,100,100,200,100,100,50])
    write(O/'ff-host-health.inc', '; Exact current native2.02 health table; no damage conversion.\n'
          'FF_NATIVE_BOX_COUNT=21\nFfHostHealth202:\n.byte '+','.join(map(str,health))+'\n')
    imports = {}
    for name in ['component.s','publisher.s','combat.s']:
        for line in (O/name).read_text().splitlines():
            match = re.fullmatch(r'\.import(zp)? (.+)', line)
            if match:
                for item in match[2].split(','):
                    item = item.strip()
                    if item.startswith('Ff'):
                        continue
                    suffix = 'zp' if match[1] else ''
                    assert imports.get(item,suffix) == suffix
                    imports[item] = suffix
    definitions = []
    for name, suffix in sorted(imports.items()):
        symbol = b['syms'][name]
        assert (symbol['addrsize'] == 'zeropage') == (suffix == 'zp'), name
        definitions += ['.export'+suffix+' '+name, name+'='+symbol['val'].replace('0x','$')]
    write(O/'host-definitions.s', '; Actual current host ABI; offline component only.\n'+'\n'.join(definitions)+'\n')
    cfg = (K/'kernel.cfg').read_text().replace(K.as_posix(),O.as_posix())
    cfg = cfg.replace('FINAL_FANTASY_ART:load=ART', 'FF_HOST_COMBAT:load=RAM3,type=ro,start=$b700;\nFINAL_FANTASY_ART:load=ART')
    write(O/'kernel.cfg', cfg)
    ca = R/'tools/Windows/cc65/bin/ca65.exe'
    logs = []
    names = ['component','publisher','host-definitions','combat']
    commands = [[str(ca), '-g', '--cpu', '6502x', '-I', str(O), '-I', str(R/'src'),
                 '--bin-include-dir', str(R), '--create-full-dep', str(O/(name+'.d')),
                 '-o', str(O/(name+'.o')), str(O/(name+'.s'))] for name in names]
    commands += [[str(ca.with_name('ld65.exe')), '-C', str(O/'kernel.cfg'),
                  '--dbgfile', str(O/'kernel.dbg'), '-Ln', str(O/'kernel.lbl'),
                  '-m', str(O/'kernel.map'), '-o', str(O/'unused-output.bin'),
                  *[str(O/(name+'.o')) for name in names]]]
    for command in commands:
        result = subprocess.run(command, cwd=R, capture_output=True, text=True)
        logs.append(dict(command=command, returncode=result.returncode,
                         stdout=result.stdout, stderr=result.stderr))
        write(O/'compile-log.json', json.dumps(logs,indent=2)+'\n')
        assert result.returncode == 0, result.stderr[-10000:]
    labels = {name:int(value,16) for value,name in re.findall(r'al ([0-9a-fA-F]+) \.(\S+)',(O/'kernel.lbl').read_text())}
    size = labels['FfHostCombatEnd']-labels['FfHostCombatBegin']
    assert labels['FfHostCombatBegin'] == 0xb700 and labels['FfHostCombatEnd'] <= 0xbfe0
    original, current = (K/'ram3.bin').read_bytes(), (O/'ram3.bin').read_bytes()
    changes = [i for i,(a,z) in enumerate(zip(original,current)) if a != z]
    assert all(0x1700 <= i < 0x1700+size for i in changes)
    assert all(original[i] == 255 for i in range(0x1700,0x1700+size))
    assert (O/'art.bin').read_bytes() == (K/'art.bin').read_bytes()
    assert (O/'art.chr').read_bytes() == (K/'art.chr').read_bytes()
    bindings = dict(proof['bindings'])
    files = {Path(__file__).resolve(), SOURCE, proof_path}
    for name in names:
        files.update(dependencies(O/(name+'.d')))
    files.update(path for path in O.iterdir() if path.is_file())
    bindings.update({str(path.resolve()):sha(path) for path in files})
    result = dict(passed=True, status='SOURCE_LINKED_NATIVE_FF_COMBAT_CONSUMERS_CPU_UNRUN',
                  source_CORE_ART_CHR_unchanged=True, image_sha256=sha(O/'ram3.bin'),
                  host_combat_bytes=size, start='B700', end=hex(labels['FfHostCombatEnd']),
                  host_imports=len(imports), extra_owned_RAM_bytes=0,
                  native=False, cartridge_or_common_hook_change=False,
                  limits=['Offline virtual image only, no resource grant or installed character.',
                          'Native target geometry, exact damage/score, slot-reuse and pause consumers require actual instruction controls next.',
                          'Scene, terrain, full render/palette/music/upgrade collection integration remains required.'],
                  bindings=bindings)
    write(O/'build-proof.json',json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','image_sha256','host_combat_bytes','end','host_imports']}))
