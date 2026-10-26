"""Checkpoint the original-score optimization and its remaining native lag."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
OUT=ROOT/'docs/qa/checkpoints/2026-10-26/chip-native-optimization-held'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not OUT.exists();OUT.mkdir(parents=True);catalog={}
    def copy(p,name):
        p=Path(p);q=OUT/name;q.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(p,q);assert sha(p)==sha(q)
        catalog[name]=dict(source=str(p),sha256=sha(p))
    ready=D/'root-chip-native-audio-v3/readiness-source-v1'
    manifest=json.loads((ready/'manifest.json').read_text())
    assert len(manifest)==73
    for p,h in manifest.items():assert sha(p)==h,p
    copy(ready/'proof.json','source-readiness.json')
    copy(ready/'manifest.json','external-source-bindings.json')
    for version,digest in [(6,'4b85059fc41534bf2c6926d14a8cdea374b373368ab20814074371138d4b8c64'),
                           (7,'b83c69a9da2e7f98deb6d4f8dc980dead632e15e9b12a9f777e22d7af9a050e6')]:
        p=D/f'root-chip-native-relocation-v{version}';assert sha(p/'candidate.nes')==digest
        for name in ['preparation.json','cpu-full-v1/proof.json','cpu-full-v1/progress.json']:
            copy(p/name,f'component-v{version}/'+name)
        copy(p/'source/src/chip_native_music.s',f'component-v{version}/chip_native_music.s')
        copy(p/'source/smb1base-mmc5-expanded.cfg',f'component-v{version}/layout.cfg')
    exp=D/'root-chip-native-adapter-v6'
    assert sha(exp/'candidate.nes')=='8b4accd2672b4b85508a365f81f499fb786f25e5572932aafc21837d5e591824'
    copy(exp/'preparation.json','adapter/preparation.json')
    for p in (exp/'source').rglob('*'):
        if p.is_file():copy(p,'adapter/changed-source/'+p.relative_to(exp/'source').as_posix())
    for name in ['adapter-cpu-v1','all-foreign-v1','irq-v1','irq-v2','mac-render-v1','outer-return-v1','build-controls-v1']:
        p=exp/name;copy(p/'proof.json','adapter/'+name+'.json')
        if (p/'cases.json').exists():copy(p/'cases.json','adapter/'+name+'-cases.json')
    native=D/'root-chip-native-audio-v3/candidate'
    assert json.loads((native/'launch.json').read_text())['passed']
    for name in ['preparation.json','manifest.json','launch-started.json','launch.json','run.lua',
                 'cadence.csv','audio-native.json','ownership-guards.json']:
        copy(native/name,'native/'+name)
    for p in native.glob('ppu-*.png'):copy(p,'native/'+p.name)
    review=D/'root-chip-native-audio-v3/paired-review-v1/proof.json'
    q=json.loads(review.read_text());assert not q['performance_gate_passed'] and q['extra_missed_DMA_starts']==28
    for p,h in q['bindings'].items():assert sha(p)==h,p
    copy(review,'paired-native-review.json')
    names=['root_chip_native_relocation_v6.py','root_chip_native_relocation_v7.py',
           'root_chip_native_pointer_liveness_v1.py','root_chip_native_cpu_v6.py',
           'root_chip_native_cpu_v7.py','root_chip_native_layout_cpu_v1.py',
           'root_chip_native_mac_render_v1.py','root_chip_native_adapter_prepare_v6.py',
           'root_chip_native_adapter_cpu_v3.py','root_chip_native_adapter_irq_v4.py',
           'root_chip_native_adapter_irq_v5.py','root_chip_native_adapter_builds_v3.py',
           'root_chip_native_audio_return_v2.py','root_chip_native_audio_prepare_v3.py',
           'root_chip_native_audio_run_v3.py','root_chip_native_optimized_checkpoint_v1.py']
    for name in names:copy(ROOT/'tools/audit'/name,'frozen-tools/'+name)
    report=ROOT/'docs/qa/chip-native-music-optimization-held-2026-10-26.txt'
    assert not report.exists()
    report.write_text('''Original Chip/Dale music optimization: STILL HELD, 2026-10-26

Installed/default/Downloads remains50b51c3c. No production adoption, new roster
slot, finished-character or full1-1/item verdict. Earlier startup failure and
the f7cf37-extra-missed-draw trial remain unchanged in the prior checkpoint.

Repacked complete original8100..afaf score data uniformly+2200 across actual
A62/C94 windows. No untyped numeric pointer/score byte was guessed or edited.
The first pure-code page remains separately compiled. Original Mac immutable
pose records genuinely moveC000->D1B0, with real typed pointers reassembled.
All21record byte streams, CHR and all other existing scoped symbols remain
exact. Reconstructing the entire changed Mac code bank from six actual typed
table operands plus its star pointer accounts for all14changed code bytes.
This is an explicit real metadata move, not a fictitious callable alias.

The initial v6 caches every C1/C2 arithmetic write. Its198,011 source calls /
904,219 ordered original APU stores and physical CPU state pass, but it is
slower (worst20,966cycles). This cost negative remains preserved. V7 uses a
conservative original call/abort graph:2,436 control states, all1,087 source
instructions and each real inline dispatcher table/34destinations. Only
writers live before actual pointer reads maintain the mapped cache. Ordinary
data-stack contents and numeric branch feasibility are not modeled by that
graph; actual original source traces independently check those contracts.
Every executed C1/C5 indirect read checks its mapped address before execution.

V7 again passes all11tracks /198,011calls /904,219 ordered original APU stores,
original writtenRAM values and complete physical CPU AXYP/SP flags. Worst
component update is15,949cycles, versus17,973 in the old qualified V5. No
source tick, clock, voice, note, score byte, timer-high store or sound event is
removed. Six borrowed foreground pointer bytes are restored by the adapter.

New adapter8b4a passes5,643 original source calls,4,176 complete audio callers
for the other35identities,192 whole AudioUpdate return controls,1,098 reached
compiled IRQ/RTI boundaries, canonical and ordinary MMC3/MMC5 flag-off builds.
The earlier158-IRQ result used obsolete address bounds and is explicitly
partial; the new checker targets the genuine moved executable range. Mac's
actual LmSetPose and complete DrawAll pass480cases over all20poses, both
modes, facings, flags and edge coordinates: exact final256-byte/ordered OAM,
hardware writes, AXYP/SP and physical banks, zero DrawAll cost difference.

ONE new real cold-menu idle1300 launch, no retry:909completed active updates,
910original source calls/6,429 ordered raw source APU stores. Main bank/stack,
all five shared SMC operands, mapper/visible-PPU guards and unchanged settings
pass. Source/private callbacks register only at startup; controller input is
the only game-state action. The actual hardware8-sprite limit remains enabled.

PERFORMANCE STILL FAILS: baseline908 DMA starts, new880 versus prior871.
NmiSkipped10->38 gives28extra missed draws, improving nine from the prior37.
Eight actual full-PPU snapshots are byte/RGB identical; ROOT viewed1200.
This static equality does not qualify scrolling, all-track native playback,
complete hardware256-byte DMA streams, waveform capture, ability/campaign
coverage or no-lag acceptance. The improvement stays private until the
remaining native timing regression is resolved.

All original ROM/NSF/large gold/raw settings files stay external. This public
checkpoint includes real source, frozen tools, exact receipts and original
lossless selected PNGs; no copyrighted ROM binaries are staged.
''',encoding='utf-8',newline='\n')
    copy(report,'report.txt')
    result=dict(accepted=False,production_adopted=False,performance_gate_passed=False,
                native_launches=1,retries=0,extra_idle_missed_DMA_starts=28,
                recovered_missed_draws_vs_previous_trial=9,verified_readiness_bindings=len(manifest),
                copied_bindings=catalog)
    (OUT/'root-review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(OUT),copied=len(catalog),performance_gate_passed=False)))


if __name__=='__main__':main()
