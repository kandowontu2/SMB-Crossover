"""Read-only provisional48 audio origin check against retained accepted47 logs."""
from pathlib import Path
import csv
import hashlib
import importlib.util
import itertools
import json
import os
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

BASE=ROOT/'build/verification/goomba46-47-apu-origin-preparation'
old=load('apu_observer47',BASE/'observe_compare.py')
cap=load('ppu_capture47',old.CAPTURE)
CP=ROOT/'build/checkpoints/roster-audit-v48-provisional-a'
ROM=CP/'smb-crossover-mmc5.nes'
CONTROL=ROOT/'build/verification/goomba46-47-apu-samus-e-a'
OUT=ROOT/'build/verification/goomba47-48-apu-samus-e-a'

def main():
    assert not OUT.exists()
    manifest_path=ROOT/'build/checkpoints/roster-audit-v47/manifest.json'
    assert sha(manifest_path)=='12d650833e3b7fae9ecfab91c37a9d284492cdd9af313a0ab4503917906140db'
    accepted=json.loads(manifest_path.read_text())
    assert sha(BASE/'freeze.json')==accepted['proofs']['apu_freeze']['sha256']
    # The accepted freeze and actual report bind the unchanged observer and its
    # prior raw control; this new wrapper binds the new physical addresses.
    prior=json.loads((CONTROL/'report.json').read_text())
    assert sha(CONTROL/'report.json')==accepted['proofs']['actual_apu_origin']['sha256']
    assert sha(BASE/'observe_compare.py')==prior['script_sha256']
    assert sha(BASE/'apu_origin.lua')==prior['observer_sha256']
    control=CONTROL/'candidate47'
    run=prior['runs'][1]
    for name,receipt in run['artifacts'].items():
        assert sha(control/name)==receipt['sha256']
    capture=json.loads((ROOT/'build/verification/goomba47-48-ppu-samus-e-a/report.json').read_text())
    assert all(sha(CP/n)==digest for n,digest in capture['checkpoint_pins'].items())
    assert sha(cap.INPUT)==cap.INPUT_SHA
    assert cap.workspace_bytes(ROOT)+old.RESERVE<cap.CAP
    OUT.mkdir()
    dest=OUT/'candidate48'
    dest.mkdir()
    fixed=OUT/'fixedE-first1200.csv'
    fixed.write_bytes(b''.join(cap.INPUT.read_bytes().splitlines(keepends=True)[:1201]))
    assert sha(fixed)==capture['prefix_sha256']
    hooks,queues,procedures=old.debug(ROM)
    core=dest/'observer.lua'
    shutil.copyfile(BASE/'apu_origin.lua',core)
    with zipfile.ZipFile(CP/'source-v48a.zip')as z:
        sources={n:hashlib.sha256(z.read(n)).hexdigest()for n in old.SOURCES}
    prior_binding=json.loads((control/'binding.json').read_text())
    assert sources==prior_binding['archived_audio_source_hashes']
    config=dict(output=dest.as_posix(),inputs=fixed.as_posix(),frames=1200,
                max_output_bytes=old.LIMIT,hooks=hooks,queues=sorted(queues))
    wrapper=dest/'apu-origin48.lua'
    wrapper.write_text('APU_ORIGIN_CONFIG='+old.lua(config)+'\ndofile('+old.lua(core.as_posix())+')\n')
    binding=dict(checkpoint_pins=capture['checkpoint_pins'],archived_audio_source_hashes=sources,
        queue_labels=queues,interrupt_hooks=hooks,procedures=procedures,config=config,
        wrapper_sha256=sha(wrapper),observer_sha256=sha(core))
    (dest/'binding.json').write_text(json.dumps(binding,indent=2)+'\n')
    report=dict(result='running-unaccepted',script_sha256=sha(Path(__file__)),
        original_runner_sha256=sha(BASE/'observe_compare.py'),observer_sha256=sha(core),
        accepted_control_report_sha256=sha(CONTROL/'report.json'),
        negative_capture_report_sha256=sha(ROOT/'build/verification/goomba47-48-ppu-samus-e-a/report.json'),
        binding_sha256=sha(dest/'binding.json'),emulated_memory_register_or_PC_writes=False,
        capture_apis=False,final_route_proof=False,workspace_cap_bytes=cap.CAP,
        max_output_bytes=old.LIMIT,all_raw_negatives_retained=True)
    rp=OUT/'report.json'
    def save():rp.write_text(json.dumps(report,indent=2)+'\n')
    save()
    previous={n:os.environ.get(n)for n in old.GUARD_ENV}
    try:
        for n in old.GUARD_ENV:os.environ.pop(n,None)
        used=cap.workspace_bytes(ROOT)
        assert used+old.RESERVE<cap.CAP
        report['workspace_before']=used
        save()
        code=cap.run_mesen.run(wrapper,ROM,timeout=240,emulator_options=[
            '--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false',
            '--nes.randomizeMapperPowerOnState=false','--audio.sampleRate=48000'])
        shutil.copyfile(ROOT/'build/verification'/f'{ROM.stem}-{wrapper.stem}.log',dest/'native.log')
        report.update(native_exit=code,artifacts={p.name:dict(bytes=p.stat().st_size,sha256=sha(p))for p in dest.iterdir()if p.is_file()})
        save()
        assert code==0
        report['native_result']=json.loads((dest/'native-result.json').read_text())
    except Exception as exc:
        report.update(result='failed-preserved',exception=repr(exc))
        save()
        raise
    finally:
        for n,v in previous.items():
            if v is None:os.environ.pop(n,None)
            else:os.environ[n]=v
    before,after=control/'events.csv',dest/'events.csv'
    comparison={}
    owner=['frame','kind','address','value','pc','physicalBank','physicalRomOffset',
        'nmiDepth','irqDepth','context','selected','guestAudioCharacter','mixOwner',
        'mixMask','nativeEnable','combinedEnable','remainingId','remainingRequest',
        'expandedCharacter','expandedEvent','mmSfx','smSfx','bassDmc']
    for name,kinds in [('apu',{'apu'}),('queues',{'queue'}),('combined',{'apu','queue'})]:
        comparison[name+'_ordered_values']=old.compare_events(before,after,kinds,['kind','address','value'])
        comparison[name+'_same_frame_values']=old.compare_events(before,after,kinds,['frame','kind','address','value'])
        comparison[name+'_same_frame_ownership']=old.compare_events(before,after,kinds,owner)
    def rows(p):
        with p.open(newline='')as f:return list(csv.DictReader(f))
    frame_differences=[]
    for a,b in itertools.zip_longest(rows(control/'frames.csv'),rows(dest/'frames.csv')):
        if a!=b:frame_differences.append(dict(before=a,after=b))
    (OUT/'frame-differences.json').write_text(json.dumps(frame_differences,indent=2)+'\n')
    report.update(comparison=comparison,frame_state_difference_count=len(frame_differences),
        inputs_identical=(control/'actual-inputs.csv').read_bytes()==(dest/'actual-inputs.csv').read_bytes(),
        inputs_identical_to_capture=(dest/'actual-inputs.csv').read_bytes()==(ROOT/'build/verification/goomba47-48-ppu-samus-e-a/candidate48/actual-inputs.csv').read_bytes(),
        result='completed-read-only-diagnostic-pcm-negative-retained',
        qualification='Ordered values, owner, physical frame and cycle timing compared separately. PCM equality is not inferred.',
        workspace_after=cap.workspace_bytes(ROOT))
    save()
    print(report['result'],json.dumps(comparison),flush=True)

if __name__=='__main__':main()
