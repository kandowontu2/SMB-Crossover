"""Record the real constructor/entrance overwrite before repairing it."""
import csv,json,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/prince-spawn-negative-freeze-1103-v107'
D=R/'docs/qa/checkpoints/2026-11-03/prince-native-spawn-negative-v107'
def main():
    O.mkdir(exist_ok=True);p=R/'build/prince-actor-1101-v1';c=p/'native-spawn-diagnostic-v144/capture';rows=list(csv.DictReader((c/'spawn-first-write.csv').open()))
    assert len(rows)==129
    initial=next(r for r in rows if r['event']=='PpNativeInit-return')
    tick=next(r for r in rows if r['event']=='PpNativeTick-entry')
    overwrite=next(r for r in rows if r['event']=='PlayerY-write'and int(r['frame'])==1043)
    assert(initial['native_y'],initial['y_high'],initial['physical_foot'])==('0','0','65312')
    assert(tick['native_y'],tick['y_high'],tick['epoch_valid'])==('176','1','0')
    assert(overwrite['pc'],overwrite['value'],overwrite['epoch_valid'])==('50104','0','1')
    sources=[Path(__file__),*(R/'tools/audit'/name for name in['prepare_prince_first_native_1103_v142.py','prepare_prince_first_native_1103_v143.py','prepare_prince_spawn_diagnostic_1103_v144.py'])]
    files=sources[:]
    for name in['native-first-controls-v143','native-spawn-diagnostic-v144']:
        a=p/name;ready=json.loads((a/'ready.json').read_text());binding=json.loads((a/'capture/binding.json').read_text())
        assert binding['exit_code']==1 and binding['ready_sha256']==sha(a/'ready.json')
        for f,h in ready['bindings'].items():assert sha(f)==h,f
        files.extend([a/'controller.lua',a/'ready.json',a/'run.py',a/'capture/binding.json',a/'capture/handoff-age360.json',a/'capture/handoff-active.json',a/'capture/source-controls.csv',a/'capture/prince-private-v140-controller.log'])
    files.extend([c/'spawn-first-write.csv',p/'native-first-controls-v143/capture/cold-active-prince.png',p/'native-first-controls-v143/capture/prince-menu.png'])
    D.mkdir(parents=True);target=D/'inputs.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for f in files:z.writestr(f.relative_to(R).as_posix(),f.read_bytes())
    assert target.stat().st_size<256000
    with zipfile.ZipFile(target)as z:
        for f in files:assert z.read(f.relative_to(R).as_posix())==f.read_bytes()
    out=dict(passed=True,tests_passed=False,installed_ROM_changed=False,private_ROM_SHA256='b684ff8aaf52aaf41f668e272f9e28704463f8cde50c9254445ec96881a451e1',checkpoint=D.relative_to(R).as_posix(),archive_SHA256=sha(target),archive_bytes=target.stat().st_size,event_trace_rows=129,constructor=initial,first_native_tick=tick,first_wrong_export=overwrite,source_files=[f.relative_to(R).as_posix()for f in sources],scope='Actual same-ROM read-only native trace, not a seeded arena. Native entrance writes legitimate Y176/high1 before first8 tick; earlier constructor at Y0/high0 cached source footFF20, then first tick marks epoch valid and writes nativeY0 at CPUC3B8. This is the real spawn defect. Stage handoff occurs at age423, so142 fixed360 was a fixture failure.143/144 Right16 also underallows original windup (historical original startup needs longer), independently of confirmed Y overwrite. Viewed actual cold screenshot has black backdrop/no visiblePrince/MARIO HUD; menu portrait is visible. Real GetPlayerColors/PpColors calls observed, no X5QueueAreaBackdrop or NrStatusName calls. No candidate fix/install, active RAM writes or native gameplay pass.',bindings={f.relative_to(R).as_posix():sha(f)for f in files})
    (D/'receipt.json').write_text(json.dumps(out,indent=2)+'\n');(O/'receipt.json').write_text(json.dumps(out,indent=2)+'\n')
    a=R/'docs/qa/continuation-current.json';h=json.loads(a.read_text());h['Prince_native_current_1103'].update(status='PRIVATE_NATIVE_SPAWN_EPOCH_BACKDROP_STATUS_DEFECT_CONFIRMED',spawn_negative_checkpoint=D.relative_to(R).as_posix(),native_diagnosis=out['scope'],remaining='Repair first8 source geometry import from actual native entrance epoch; add genuine area-backdrop/status ingresses. Retain original acceleration; native controller must allow source-proven windup. Then exact CPU/cold/IRQ +rootMesen replay/real sword/1-1. Nightly remainscf7.')
    h['root_queue_current_1102'].update(status='FREE',last_Prince_native_terminal=['controls139-icon-fixture-negative','controls142-fixed360-fixture-negative','controls143-spawn-and-windup-negative','diagnostic144-nativeY176-to0-overwrite-confirmed'],next='Princehelper fixes sourcegeometryepoch/nativebackdrop/status; rootqueueFREE. Bubhelper sourcefunded fullauth directSide transport measurement; DKcurrentfour-owner cold81/foreign82 remainprivateproposal. Installednightlycf7unchanged.')
    a.write_text(json.dumps(h,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k not in['bindings','constructor','first_native_tick','first_wrong_export']}))
if __name__=='__main__':main()
