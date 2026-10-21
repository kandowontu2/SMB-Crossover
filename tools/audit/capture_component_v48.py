"""Capture provisional48 and compare to the retained literal accepted47 control."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT/'build/verification/goomba46-47-ppu-preparation/capture_compare46_47.py'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(HELPER) == '420b0897382062723281068ef33ff7205668c029ab3210b6e81b8da89eaacda7'
spec = importlib.util.spec_from_file_location('literal_capture47', HELPER)
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
OUT = ROOT/'build/verification/goomba47-48-ppu-samus-e-a'
OLD = ROOT/'build/verification/goomba46-47-ppu-samus-e-a'
CP = ROOT/'build/checkpoints/roster-audit-v48-provisional-a'
ROM = CP/'smb-crossover-mmc5.nes'


def main():
    assert not OUT.exists(), 'Fresh output only'
    assert sha(h.INPUT) == h.INPUT_SHA and sha(h.BRIDGE) == h.BRIDGE_SHA
    manifest_path = ROOT/'build/checkpoints/roster-audit-v47/manifest.json'
    assert sha(manifest_path) == '12d650833e3b7fae9ecfab91c37a9d284492cdd9af313a0ab4503917906140db'
    manifest = json.loads(manifest_path.read_text())
    assert sha(OLD/'report.json') == manifest['proofs']['screen_and_pcm_negative']['sha256']
    old_report = json.loads((OLD/'report.json').read_text())
    old = OLD/'candidate47'
    binding = old_report['runs'][1]
    assert binding['name'] == 'candidate47'
    assert binding['provenance']['rom_sha256'] == '3f5e8fdff30ce057ebf136a6e93d5f5481ff8962345dc98039458e3abb679dc8'
    assert sha(old/'part-0000.avi') == binding['avi_sha256'] == '1091898ccedfd336b2c46bee8b1e94d5cfaa2d1df4e5f9250557b463b7b3e996'
    assert sha(old/'native-audio.wav') == binding['wave_sha256'] == 'a8d93cae677cfd51b75410df488970964e3535ea09e24ca4d07703a8d716a92c'
    assert sha(old/'actual-inputs.csv') == binding['actual_inputs_sha256'] == '8799d5b153b4f7ef14d76024468de34fd085800568750a5a8f6310f5a18807f7'
    pins = {
        'smb-crossover-mmc5.nes': '54d27a36bd04a2c54aeb0219fc6c6317394af7861ba4aa4a2d4b1c1a68d97da7',
        'smb-crossover-mmc5.dbg': '82f1df8d02c14fde923ca71edcef4f969e3dc28091d0c57fd1f2d1b24db7b1ac',
        'smb-crossover-mmc5.lbl': '6ebaa77d7910425391220cdfef4049a9bacfabf4a9e065957c0aa04e5c18e24e',
        'candidate.json': 'c5c6f358495ffc43d4d2acc3bd7ffdbf67a1ebc7028d2c671474f35644af13d5',
        'source-v48a.zip': '7380253997cd499000c1be966a9ae5b8890ffe39e066a39fe16661d2245527e7',
    }
    assert all(sha(CP/n) == v for n,v in pins.items())
    with zipfile.ZipFile(CP/'source-v48a.zip') as z:
        assert hashlib.sha256(z.read('src/ground_goomba_terrain.s')).hexdigest() == '4ae7bc04fe9e046e0fdb8680749bd7fdd14bcaecc5189fef0d1c921af7485144'
    used = h.workspace_bytes(ROOT)
    assert used+h.PAIR_RESERVE < h.CAP, ('No recorder opened: full pair reserve', used)
    OUT.mkdir()
    dest = OUT/'candidate48'
    dest.mkdir()
    fixed = OUT/'fixedE-first1200.csv'
    fixed.write_bytes(b''.join(h.INPUT.read_bytes().splitlines(keepends=True)[:h.FRAMES+1]))
    assert sha(fixed) == old_report['prefix_sha256'] == '859d2887a8dded5ad26dc0378fc4d892b0485f04368ae8327ae906ee47933131'
    report = dict(result='running-unaccepted', checkpoint_pins=pins,
        script_sha256=sha(Path(__file__)), helper_sha256=sha(HELPER),
        control_report_sha256=sha(OLD/'report.json'), control_native_binding=binding,
        control_source='Retained accepted47 literal native AVI/WAV; not reencoded',
        source_inputs_sha256=sha(h.INPUT), prefix_sha256=sha(fixed),
        memory_or_register_writes=False, final_route_proof=False,
        workspace_before=used, full_pair_reserve_bytes=h.PAIR_RESERVE,
        workspace_cap_bytes=h.CAP, all_native_artifacts_retained=True)
    rp = OUT/'report.json'
    def save(): rp.write_text(json.dumps(report,indent=2)+'\n')
    save()
    script = dest/'public-capture48.lua'
    script.write_text(h.lua_capture(h.BRIDGE,fixed,dest),encoding='utf8')
    prior = {n:os.environ.get(n) for n in h.ENV}
    try:
        for n in h.ENV: os.environ.pop(n,None)
        os.environ['SMB_CAPTURE_SEGMENT_DIR'] = dest.as_posix()
        fresh = h.workspace_bytes(ROOT)
        assert fresh+h.PAIR_RESERVE < h.CAP, ('Full pair reserve recheck',fresh)
        report['pre_capture_workspace'] = fresh
        save()
        code = h.run_mesen.run(script,ROM,timeout=180,emulator_options=[
            '--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false',
            '--nes.randomizeMapperPowerOnState=false','--audio.sampleRate=48000'])
        native = ROOT/'build/verification'/f'{ROM.stem}-{script.stem}.log'
        shutil.copyfile(native,dest/'native.log')
        actual = json.loads((dest/'capture-result.json').read_text())
        report.update(native_exit=code,native_result=actual,native_log_sha256=sha(dest/'native.log'))
        save()
        assert code == 0 and actual == binding['native_result']
        assert 'SEGMENT START: active=1' in native.read_text() and 'WAVE START: active=1' in native.read_text()
        assert len(list(dest.glob('part-*.avi'))) == 1
        assert not (dest/'capture-budget-stop.json').exists()
    except Exception as exc:
        report.update(result='failed-preserved',exception=repr(exc))
        save()
        raise
    finally:
        for n,v in prior.items():
            if v is None: os.environ.pop(n,None)
            else: os.environ[n] = v
    video = next(s for s in h.probe(dest/'part-0000.avi',dest/'avi-streams.json') if s['codec_type']=='video')
    audio = next(s for s in h.probe(dest/'native-audio.wav',dest/'wave-streams.json') if s['codec_type']=='audio')
    assert video['codec_name']=='zmbv' and int(video['nb_frames'])==1199 and video['width']==256 and video['height']==240
    assert audio['codec_name']=='pcm_s16le' and audio['sample_rate']=='48000' and audio['channels']==2
    rgb = h.exact_rgb(old/'part-0000.avi',dest/'part-0000.avi',OUT)
    a = h.pcm(old/'native-audio.wav',OUT/'control47-pcm.stderr.log')
    b = h.pcm(dest/'native-audio.wav',OUT/'candidate48-pcm.stderr.log')
    first = next((i for i,(x,y) in enumerate(zip(a,b)) if x!=y), None)
    if first is None and len(a)!=len(b): first=min(len(a),len(b))
    inputs_equal = (old/'actual-inputs.csv').read_bytes()==(dest/'actual-inputs.csv').read_bytes()
    report.update(rgb24=rgb,actual_inputs_identical=inputs_equal,
        continuous_pcm=dict(literal_equal=a==b,before_bytes=len(a),after_bytes=len(b),
            before_sha256=hashlib.sha256(a).hexdigest(),after_sha256=hashlib.sha256(b).hexdigest(),
            first_difference_byte=first,first_difference_seconds=None if first is None else first//4/48000,
            resampling=False,offset_alignment=False),
        candidate_artifacts={n:sha(dest/n) for n in ('part-0000.avi','native-audio.wav','actual-inputs.csv','capture-result.json')},
        workspace_after=h.workspace_bytes(ROOT),
        qualification='PCM differences retained; no waveform or all-character audiovisual identity inferred.')
    report['result'] = 'exact-rgb24-and-pcm' if rgb['literal_rgb24_identity'] and a==b and inputs_equal else 'diagnostic-preserved'
    save()
    print(report['result'],json.dumps(dict(rgb=rgb,pcm=report['continuous_pcm'])),flush=True)
    return 0 if report['result']=='exact-rgb24-and-pcm' else 2

if __name__=='__main__':
    raise SystemExit(main())
