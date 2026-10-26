"""Preserve the native startup repair and the still-failing music draw budget."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
OUT=ROOT/'docs/qa/checkpoints/2026-10-26/chip-native-adapter-held'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not OUT.exists();OUT.mkdir(parents=True)
    catalog={}
    def copy(p,name):
        p=Path(p);q=OUT/name;q.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(p,q);assert sha(q)==sha(p)
        catalog[name]=dict(source=str(p),sha256=sha(p))
    for version,expected in [(4,'a53747c271bbaf540e69f39390bed419edd809e498e5d7aae9eeabc2d8659c4c'),
                             (5,'f7cf83bb7b3bfd7ecc138dd3a7dcf2e8a3caa27bcece32ba89ef1fa6e958f7d2')]:
        p=D/f'root-chip-native-adapter-v{version}';assert sha(p/'candidate.nes')==expected
        copy(p/'preparation.json',f'v{version}/preparation.json')
        for f in (p/'source').rglob('*'):
            if f.is_file():copy(f,f'v{version}/changed-source/'+f.relative_to(p/'source').as_posix())
        for relative in (['cpu512-v1','foreign-v1','irq-v2','build-controls-v1']if version==4 else
                         ['cpu512-v2','foreign-v1','irq-v3','outer-return-v1','build-controls-v2']):
            proof=p/relative/'proof.json';j=json.loads(proof.read_text());assert j['passed']
            copy(proof,f'v{version}/'+relative+'.json')
    launches=[D/'root-chip-native-audio-v1/baseline',D/'root-chip-native-audio-v1/candidate',
              D/'root-chip-native-audio-v2/candidate']
    for i,p in enumerate(launches):
        j=json.loads((p/'launch.json').read_text());assert j['settings_unchanged']
        assert j['passed']==(i!=1)
        for name in ['preparation.json','launch-started.json','launch.json','manifest.json','run.lua',
                     'audio-native.json','ownership-guards.json','cadence.csv']:
            if (p/name).exists():copy(p/name,f'native-{i}/'+name)
        # All lossless original PNGs remain external as well.
        for f in p.glob('ppu-*.png'):copy(f,f'native-{i}/'+f.name)
    review=D/'root-chip-native-audio-v2/paired-review-v1/proof.json'
    j=json.loads(review.read_text());assert not j['performance_gate_passed'] and j['extra_missed_DMA_starts']==37
    assert all(row['RGB_equal']for row in j['selected_actual_PPU_comparisons'])
    copy(review,'paired-native-review.json')
    tools=list(ROOT.glob('tools/audit/root_chip_native_adapter_*.py'))+list(ROOT.glob('tools/audit/root_chip_native_audio_*.py'))
    for f in tools:copy(f,'frozen-tools/'+f.name)
    report=ROOT/'docs/qa/chip-native-music-adapter-held-2026-10-26.txt'
    assert not report.exists()
    report.write_text('''Chip/Dale native music adapter: PERFORMANCE HELD, 2026-10-26

No production installation or goal-completion claim. Default/download ROM
remains50b51c3c. This checkpoint preserves actual source implementations,
the native startup failure, its repair, and the remaining measured lag.

The original11-track player component remains byte-exact to qualified2a116.
New route uses A78 free code space, the original A62/C94 free tails and a
real18-byte resident dispatcher span. All60,694 old scoped symbols retain
their addresses. Header/CHR and other banks are unchanged. Existing music
requests choose all11original tracks; pause, held requests, silence and
foreground pointer restoration are checked. No source tick, voice, timer-high
store, song data, clock or original sound request is omitted.

Initiala537 passes5,643 source calls,4,176 complete foreign audio calls across
35unchanged identities,1,109 actual compiled IRQ boundaries and both ordinary
mapper builds. Its cold native run nevertheless stays black before gameplay.
Root cause: the new adapter changed CurrentBank to206, while the full audio
caller/NMI must retain the interrupted main bank215. Returning then remapped
physicalA78 over mainA87. Unit-only adapter checks missed that outer contract.
The native failure remains false and all original PNGs/records are retained.

Repairedf7cf preserves the foreground shadow and uses a physical-only,
NMI-private A-window roundtrip, as existing native drivers do.192 complete
AudioUpdate return cases explicitly reproduce/reject the old fault and pass
both modes/Chip-Dale/title/pause/event conditions on the repair. Fresh5,643
source calls,4,176 unchanged-identity calls,1,103 actualIRQ boundaries and
canonical/ordinary flagoff builds pass. All shared SMC code is untouched.

Three total native launches, no retries: baseline50b1300, rejecteda5371300,
and repairedf7cf1300. The repaired run cold-starts normally and checks910
original source calls/6,429 ordered raw source APU stores and original written
RAM states.908 nativeNMI/IRQ guards pass, every fiveSMC operand and main bank
is restored, no visible-world PPU address write. These are source-image and
actual register-stream checks; no recorded waveform claim.

PERFORMANCE FAILS: both completed909active logic updates, but DMA starts
fall908->871. NmiSkipped rises10->47 instead of remaining10. EndFrame logic
snapshots differ41times, beginning with a within-frame completion difference;
they are not described as matching all completed display epochs. Eight
selected actual wholePPU PNGs are RGB/byte identical; ROOT viewed1200. This
idle visual equality does not excuse37missed draws or qualify scrolling.
The trial remains excluded from the installed build until the real player
cost is reduced and native source/cadence checks pass.

All runtime callbacks register at startup. Native controls use only real
menu/controller input, no emulated state or outcome writes. Hardware8-sprite
limit, no runahead/extra scanlines, original settings unchanged. No complete
OAM-transfer, full1-1, all-item, all-track-native, waveform or roster verdict.
Native raw settings, gold traces, ROMs and lossless captures remain external.
''',encoding='utf-8',newline='\n')
    copy(report,'report.txt')
    result=dict(accepted=False,production_adopted=False,performance_gate_passed=False,
                actual_native_launches=3,extra_idle_missed_DMA_starts=37,
                original_startup_failure_retained=True,outer_return_fault_repaired=True,
                selected_actual_full_PPU_frames_ROOT_viewed=[1200],copied_bindings=catalog)
    (OUT/'root-review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(OUT),copied=len(catalog),performance_gate_passed=False)))


if __name__=='__main__':main()
