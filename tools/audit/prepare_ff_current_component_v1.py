"""Genuinely link the frozen FF source against current host exports; no admission."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R/'tools/audit'), str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from prepare_cv3_dmc_mirror import prepare

P = R/'build/required-rcr-ink-v2/candidate'
OLD = R/'build/final-fantasy-component-v1'
O = R/'build/final-fantasy-current-component-v1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(value, newline='\n')


def dependencies(path):
    raw = path.read_text().replace('\\\n', ' ').replace('\\ ', '\0')
    return [Path(x.replace('\0', ' ')) for x in raw.split(': ', 1)[1].split()]


def main():
    assert not O.exists(), O
    assert sha(P/'candidate.nes') == '753b6bd1e51bb6c427206f841e63790bfd79fe2a3cca964e04254408f87ead53'
    original = (P/'candidate.nes').read_bytes()
    base = scoped_load(P/'candidate.nes')
    recipe = [x['command'] for x in json.loads((P/'compile-log.json').read_text())]
    assert len(recipe) == 2
    old_component = (OLD/'component.s').read_text()
    host_names = re.findall(r'^(\w+)=', old_component.split('.macpack')[0], re.M)
    assert len(set(host_names)) == len(host_names)
    for name in host_names:
        assert name in base['syms'], name
    O.mkdir()
    commands = []

    def run(command, log):
        result = subprocess.run(command, cwd=R, capture_output=True, text=True)
        commands.append(dict(command=command, returncode=result.returncode,
                             stdout=result.stdout, stderr=result.stderr))
        write(log, json.dumps(commands, indent=2)+'\n')
        assert result.returncode == 0, result.stderr[-12000:]

    def stage(name, component=False):
        out = O/name
        out.mkdir()
        entry = (P/'entrypoint.s').read_text()
        cfg = (P/'private.cfg').read_text()
        if component:
            exports = []
            imports = []
            for name in host_names:
                suffix = 'zp' if base['syms'][name]['addrsize'] == 'zeropage' else ''
                exports.append('.export'+suffix+' '+name)
                imports.append('.import'+suffix+' '+name)
            entry += '\n; Actual exports for the separately assembled FF component.\n'+'\n'.join(exports)+'\n'
            preamble = old_component[old_component.index('.macpack'):]
            assert preamble.count('.include "final_fantasy.s"') == 1
            preamble = preamble.replace('.include "final_fantasy.s"',
                '.pushseg\n.segment "FINAL_FANTASY_CORE"\nFfCoreBegin:\n.popseg\n'
                '.include "final_fantasy.s"\n'
                '.pushseg\n.segment "FINAL_FANTASY_CORE"\nFfCoreEnd:\n'
                '.assert FfCoreEnd-FfCoreBegin <= $c90,error,"FF core reservation"\n'
                '.export FfCoreBegin,FfCoreEnd,FfArtStart,FfArtEnd\n.popseg')
            write(out/'ff-component.s', '; Host addresses are real imports, not old absolute aliases.\n'+'\n'.join(imports)+'\n'+preamble)
            old_mem = 'X5_NEW_5D_AFTER_BBOX:start=$afe7,size=$1019,type=ro,file=%O,fill=yes,fillval=$ff,bank=$5d;'
            assert cfg.count('X5_NEW_5D_AFTER_BBOX') == 1
            assert cfg.count(old_mem) == 1
            cfg = cfg.replace(old_mem,
                'X5_NEW_5D_AFTER_BBOX:start=$afe7,size=$19,type=ro,file=%O,fill=yes,fillval=$ff,bank=$5d;\n'
                '    FF_ART_MEM:start=$d000,size=$1000,type=ro,file=%O,fill=yes,fillval=$ff,bank=$5d;')
            needle = '    KAMIKAZE_CORE: load=X5_NEW_3E,type=ro,start=$b690,optional=yes;'
            assert cfg.count(needle) == 1
            cfg = cfg.replace(needle,
                '    FINAL_FANTASY_CORE:load=X5_NEW_3E,type=ro,start=$aa00;\n'
                '    FINAL_FANTASY_ART:load=FF_ART_MEM,type=ro;\n'+needle)
            needle = '    DRAGON_POWER_CHR: load=TMNT_CHR_TAIL,type=ro,start=$c5000,optional=yes;'
            assert cfg.count(needle) == 1
            cfg = cfg.replace(needle, '    FINAL_FANTASY_CHR:load=TMNT_CHR_TAIL,type=ro,start=$bd000;\n'+needle)
        write(out/'entrypoint.s', entry)
        write(out/'private.cfg', cfg)
        main_command = [v.replace(str(P), str(out)) for v in recipe[0]]
        at = main_command.index('-I')
        main_command[at:at] = ['-I', str(out), '-I', str(P)]
        run(main_command, out/'compile-log.json')
        if component:
            run([recipe[0][0], '-g', '--cpu', '6502x', '-I', str(R/'src'),
                 '--bin-include-dir', str(R), '--create-full-dep', str(out/'ff.d'),
                 '-o', str(out/'ff-component.o'), str(out/'ff-component.s')], out/'compile-log.json')
        link = [v.replace(str(P), str(out)) for v in recipe[1]]
        if component:
            at = link.index('-m')
            link[at:at] = [str(out/'ff-component.o')]
        run(link, out/'compile-log.json')
        prepare(R, out/'candidate.nes')
        return out

    reproduced = stage('reproduce')
    assert (reproduced/'candidate.nes').read_bytes() == original
    candidate = stage('linked', component=True)
    raw = (candidate/'candidate.nes').read_bytes()
    assert len(raw) == len(original) == 2097168
    leases = [dict(name='FINAL_FANTASY_CORE', start=16+62*8192+0xa00, size=0xc90, fill=255),
              dict(name='FINAL_FANTASY_ART', start=16+93*8192+0x1000, size=4096, fill=255),
              dict(name='FINAL_FANTASY_CHR', start=16+1048576+756*1024, size=32768, fill=0)]
    changes = [i for i, (a, b) in enumerate(zip(original, raw)) if a != b]
    for lease in leases:
        lo, hi = lease['start'], lease['start']+lease['size']
        assert original[lo:hi] == bytes([lease['fill']])*lease['size'], lease
        lease['changed_bytes'] = sum(lo <= i < hi for i in changes)
    assert sum(x['changed_bytes'] for x in leases) == len(changes)
    current = scoped_load(candidate/'candidate.nes')
    moved = {name: [symbol['val'], current['syms'].get(name, {}).get('val')]
             for name, symbol in base['syms'].items()
             if current['syms'].get(name, {}).get('val') != symbol['val']}
    assert not moved, moved
    imports = {name: dict(value=current['syms'][name]['val'],
                          address_size=base['syms'][name]['addrsize']) for name in host_names}
    actual_deps = set()
    for out in [reproduced, candidate]:
        for dep in ['main.d']+(['ff.d'] if out == candidate else []):
            actual_deps.update(dependencies(out/dep))
    objects = [Path(v) for v in recipe[1] if v.endswith('.o')]
    for p in objects:
        assert p.is_file(), p
    bindings = {str(p.resolve()): sha(p) for p in actual_deps | set(objects)}
    for p in [Path(__file__).resolve(), P/'compile-log.json', P/'candidate.nes',
              P/'candidate.dbg', OLD/'component.s', OLD/'handoff.json',
              *[p for out in [reproduced, candidate] for p in out.iterdir() if p.is_file()]]:
        bindings[str(p)] = sha(p)
    proof = dict(passed=True, source_only=True, native=False, shared_installation=False,
                 status='GENUINE_CURRENT_HOST_EXPORTS_COMPONENT_LINK_NO_ADMISSION',
                 parent_ROM_sha256=sha(P/'candidate.nes'), ROM_sha256=sha(candidate/'candidate.nes'),
                 exact_parent_source_reproduction=True, changed_bytes=len(changes), leases=leases,
                 unchanged_old_symbol_values=True, genuine_host_imports=imports,
                 CORE_bytes=int(current['syms']['FfCoreEnd']['val'], 0)-int(current['syms']['FfCoreBegin']['val'], 0),
                 ART_bytes=int(current['syms']['FfArtEnd']['val'], 0)-int(current['syms']['FfArtStart']['val'], 0),
                 actual_dependencies=len(actual_deps), bindings=bindings,
                 limits=['Payload linked only: FF menu admission, terrain/combat/render/palette adapters are still absent.',
                         'No native gameplay, interrupts, performance, music or full-powerup claim.',
                         'No new bank/WRAM/CHR allocation; existing documented FF ranges only.'])
    write(O/'build-proof.json', json.dumps(proof, indent=2)+'\n')
    print(json.dumps({k:proof[k] for k in ['status','ROM_sha256','CORE_bytes','ART_bytes','changed_bytes','actual_dependencies']}))


if __name__ == '__main__':
    main()
