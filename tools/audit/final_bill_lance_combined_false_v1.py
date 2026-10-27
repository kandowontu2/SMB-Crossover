"""Freeze the first ce635 Bill HUD observer FALSE; never launch an emulator."""
from pathlib import Path
import argparse,json
from final_bill_lance_combined_prepare_v2 import D,ROOT,PARENT,SHA,sha,put


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    ready=D/'final-bill-lance-combined-ce635-ready-v2'
    native=ready/'profiles/bill-hard/native'
    result=json.loads((native/'proof.json').read_text())
    assert result['ROM_sha256']==SHA and not result['passed'] and result['runner_exit']==1
    assert result['worker_released'] and result['launches']==1 and result['retries']==0 and result['dependencies_unchanged']
    first=json.loads((native/'first-failure.json').read_text())
    assert first==dict(y=6,phase=dict(name='machine',phase='grant-drain'),x=97,a=174,bank=4,
        message='Only Bill/Lance capsule moved to the new screen anchor',sp=240,pc=42426)
    assert not(ready/'profiles/lance-hard/native/launch.json').exists()
    hardware=result['analysis']['components']['hardware'];cadence=result['analysis']['components']['cadence']
    assert hardware['passed'] and hardware['complete256DMAs']==889 and hardware['safe_scoped_enables']==563
    assert cadence['passed'] and cadence['entries']==535 and cadence['finishes']==534
    from PIL import Image
    image=Image.frombytes('RGBA',(256,240),(native/'first-failure.argb').read_bytes(),'raw','BGRA')
    image.save(a.output/'actual-first-failure.png')
    proof=dict(passed=False,native_run=True,ROM_sha256=SHA,profile='bill-hard',launches=1,retries=0,
        worker_released=True,Lance_unrun=True,first_failure=first,
        observed_scope='Original v1 HUD observer asserts at genuine bank4 $A5BA MetaspriteRenderLoop; machine grant-drain after the first upgraded pickup. This is not a completed seven-case/HUD pass.',
        observer_defect='The v1 admission tests only AvDrawIndex20 and selected weapon. AvDrawIndex is a shared persistent loop cursor, not proof of helper/ArtPointer/immediate-render ownership.',
        unrecorded_failure_fields=['R4','R5','R6','R7','R0','R1','return-stack words','source caller return PC'],
        limits='Actual failure supplies PC/SP/physical bank/AXY and phase only. A later player/body caller is a source-backed hypothesis until separate CPU/Lua reproduction, not captured native caller evidence.',
        partial_hardware=hardware,partial_cadence=cadence,
        original_native_receipt=dict(path=str(native/'proof.json'),sha256=sha(native/'proof.json')),
        no_game_source_or_settings_changes=True,no_retry_or_new_grant=True)
    put(a.output/'proof.json',proof)
    files={Path(__file__),PARENT/'candidate.nes',PARENT/'candidate.dbg',PARENT/'source-manifest.json',
        ROOT/'tools/audit/final_bill_lance_combined_hud_v1.lua',ROOT/'tools/audit/final_bill_lance_combined_run_v1.py',
        ready/'final-freeze-v1/proof.json',ready/'final-freeze-v1/manifest.json',
        ready/'final-freeze-v1/bill-hard/proof.json',ready/'final-freeze-v1/bill-hard/ROOT-grant-bill-hard.json',
        a.output/'actual-first-failure.png',a.output/'proof.json'}
    files.update(f for f in native.iterdir()if f.is_file())
    put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),sha256=sha(f),bytes=f.stat().st_size)for f in sorted(files)]))
    print(json.dumps(dict(frozen=True,passed=False,worker_released=True,proof_sha256=sha(a.output/'proof.json'),bindings=len(files))))


if __name__=='__main__':main()
