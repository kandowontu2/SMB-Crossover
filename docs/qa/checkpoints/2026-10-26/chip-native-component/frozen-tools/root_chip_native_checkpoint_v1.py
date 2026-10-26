"""Freeze original-player components and actual CPU results, without adoption."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
OUT = ROOT/'docs/qa/checkpoints/2026-10-26/chip-native-component'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not OUT.exists()
    OUT.mkdir(parents=True)
    catalog = {}

    def copy(p, name):
        p = Path(p)
        q = OUT/name
        q.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(p,q)
        assert sha(p)==sha(q)
        catalog[name] = dict(source=str(p),sha256=sha(p))

    for version, expected in [(2,'13dddaa169164a9d83d4f0d78b5a0e092cc1b5f894c41a1d38111cfb0597d5c0'),
                              (5,'2a116f44a768d0ab9a94c88df0191144f0a85ae377211263dabdceb43ede12f6')]:
        p = D/f'root-chip-native-relocation-v{version}'
        assert sha(p/'candidate.nes')==expected
        cpu = p/f'cpu18000-v{version}/proof.json'
        q = json.loads(cpu.read_text())
        assert q['passed'] and q['candidate_ROM_sha256']==expected
        assert sum(r['calls'] for r in q['tracks'])==198011
        assert sum(r['ordered_original_APU_stores'] for r in q['tracks'])==904219
        for file in [p/'preparation.json',cpu]:
            copy(file,f'v{version}/'+('preparation.json' if file.name=='preparation.json' else 'original-source-cpu.json'))
        for file in (p/'source').rglob('*'):
            if file.is_file():
                copy(file,f'v{version}/changed-source/'+file.relative_to(p/'source').as_posix())
    for version in [1,3,4]:
        p = D/f'root-chip-native-relocation-v{version}'
        for name in ['build.log','preparation.json']:
            copy(p/name,f'intermediate-v{version}/'+name)
        for file in p.glob('cpu512-*/proof.json'):
            copy(file,f'intermediate-v{version}/'+file.parent.name+'-proof.json')
    domain = D/'root-chip-native-relocation-v5/pointer-domain-v1/proof.json'
    q = json.loads(domain.read_text())
    assert q['passed'] and q['compiled_helper_reads']==74040 and q['cross_window_boundary_reads']==520
    copy(domain,'v5/pointer-domain-proof.json')
    names = ([f'root_chip_native_relocation_v{v}.py' for v in range(1,6)] +
             [f'root_chip_native_cpu_v{v}.py' for v in range(1,6)] +
             ['root_chip_native_pointer_cpu_v1.py',Path(__file__).name])
    for name in names:
        copy(ROOT/'tools/audit'/name,'frozen-tools/'+name)
    report = ROOT/'docs/qa/chip-native-music-component-2026-10-26.txt'
    assert not report.exists()
    report.write_text('''Chip/Dale original music component, 2026-10-26

PRIVATE CPU COMPONENT. No gameplay dispatch, native playthrough, waveform,
performance acceptance, production installation or roster-completion claim.

Original authenticated Rescue Rangers NSF6a8b3729 is executed by a relocated
player. Original numeric song pointers stay intact. All original ROM data is
retained; the pure-code8000..80ff page is compiled separately rather than
duplicated as data. No guessed pointer-byte patching or captured-prefix loop.
The static source closure includes1087instructions and all43slots from four
genuine inline dispatch tables. The selected11songs are actually qualified.

Only original free A62/C94 tails change. Publisher/Mac-art prefixes, every
other bank/header/CHR and every old scoped symbol remain exact. State uses
the existing exclusive audio-history lane and four existing audio-ZP bytes.
No production RAM allocation, CHR, menu or gameplay changes are installed.

Initial13dd and optimized2a116 each pass198011original calls and904219ordered
rawAPUstores, original numeric RAM state, actual6502flags and A/X/Y/SP.
VirtualB/unused stack-status bits are explicitly outside physical-flag equality;
no sourceAPU bytes or timer-high writes are masked. V5 additionally passes
74040compiled read controls,44424real cache-setter controls and520reads across
the discontinuous92ff/9300 data boundary, preserving foregroundZP ownership.

V5 caches only the real score pointer, maps other reads through a constant
page table and dispatches through the original command index. The full-track
maximum falls26485->17973CPUcycles, before game adapter/mixer/interrupt costs.
This is still a performance concern. Mean active tracks are roughly3494..4881.
No original source tick, event, voice or song data is skipped. Native cadence
is untested. IRQ ownership, gameplay routing, event/pause/end behavior, exact
ordinary rebuilds and composition with other current private changes remain.

The first source preparation exposed an additional fourth inline dispatcher;
the corrected closure includes it. Retained V1 cannot link: segment ordering
and code capacity were wrong. V2 relocates the pure first code page and orders
segments after their real prefixes. IntermediateV3/V4 and fullV2/V5 results
are retained separately. No old failure or slower result is retagged.

Production/default/Downloads remain50b51c3c. Raw gold traces, private ROMs,
lossless recordings and large build artifacts remain in the external archive.
''',encoding='utf-8',newline='\n')
    copy(report,'report.txt')
    review = dict(accepted=False,production_adopted=False,native_run=False,
                  full_original_calls_per_component=198011,ordered_original_APU_stores=904219,
                  private_ROMs={str(v):sha(D/f'root-chip-native-relocation-v{v}/candidate.nes') for v in [2,3,4,5]},
                  remaining=['gameplay adapter','event/pause/end behavior','IRQ/outer callers','ordinary rebuilds','native source/cadence'],
                  copied_bindings=catalog)
    (OUT/'root-review.json').write_text(json.dumps(review,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(OUT),files=len(catalog),accepted=False)))


if __name__=='__main__':
    main()
