"""Freeze ONE same5354 menu replay and its selected actual PPU review inputs."""
from pathlib import Path
import argparse,hashlib,json,itertools
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[2]
SHA='5354161f339548f2e12b955f5fc1481b9956fe83a63263a04f4b2816edbbdf30'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rows(path):
    with path.open()as f:
        for line in f:
            if line.strip():yield json.loads(line)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['run','old-run','ready','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    receipt=json.loads((a.run/'lifecycle-proof.json').read_text());assert receipt['ROM_sha256']==SHA
    components=receipt['components'];passed=receipt['passed']and all(q.get('passed')for q in components.values())
    raw=sorted(a.run.glob('frame-*.argb'));frames=[int(f.stem.removeprefix('frame-'))for f in raw]
    oldframes=sorted(a.old_run.glob('frame-*.argb'));matches=[];diffs=[]
    for f in oldframes:
        new=a.run/f.name
        if not new.exists():diffs.append(dict(frame=int(f.stem.removeprefix('frame-')),reason='new frame absent'));continue
        oldh,newh=sha(f),sha(new);(matches if oldh==newh else diffs).append(dict(frame=int(f.stem.removeprefix('frame-')),old_sha256=oldh,new_sha256=newh))
    (a.output/'same-ROM-RGB-prefix.json').write_text(json.dumps(dict(matched=matches,differed=diffs,original_negative_not_retagged=True),indent=2)+'\n')
    busmatches=0;busdiff=None
    def original_bus(path):
        for q in rows(path):
            if not q['kind'].startswith('lifecycle-HUD-'):yield q
    for i,(x,y)in enumerate(itertools.zip_longest(original_bus(a.old_run/'oam-bus.jsonl'),original_bus(a.run/'oam-bus.jsonl'))):
        if x is None:break
        if x!=y:busdiff=dict(index=i,original=x,new=y);break
        busmatches+=1
    (a.output/'same-ROM-original-bus-prefix.json').write_text(json.dumps(dict(matching_events=busmatches,first_difference=busdiff,new_additive_HUD_phase_events_excluded=True,original_negative_not_retagged=True),indent=2)+'\n')
    hud=list(rows(a.run/'hud-frames.jsonl'));life=list(rows(a.run/'lifecycle-events.jsonl'));scroll=list(rows(a.run/'scroll-events.jsonl'))
    terminal=next((q for q in life if q['kind']=='terminal-fixture-state'),None)
    active=next((q['finished']['frame']for q in hud if q['start']['ram']['OperMode']==1 and q['start']['ram']['GameEngineSubroutine']==8),None)
    font=next((q['finished']['frame']for q in hud if q['start']['ram']['InvHudActive']==3 and q['start']['ram']['OperMode']==1 and q['start']['chr'][8]==396),None)
    capture=next((q['capture']['ppu']['frame']for q in scroll if q['kind']=='capture-visible-frame'),None)
    selected=sorted(set(n for n in [266,278,290,302,314,326,349,369,375,376,active,capture,font,(font+1)if font else None,1797,1798,1799,1800]if n in frames))
    sheet=Image.new('RGB',(6*256,((len(selected)+5)//6)*260),'#151515');draw=ImageDraw.Draw(sheet);bindings=[]
    for i,n in enumerate(selected):
        f=a.run/f'frame-{n:06}.argb';im=Image.frombytes('RGBA',(256,240),f.read_bytes(),'raw','BGRA').convert('RGB');target=a.output/f'actual-PPU-{n}.png';im.save(target);sheet.paste(im,(i%6*256,i//6*260+20));draw.text((i%6*256,i//6*260),f'Actual PPU {n}',fill='white');bindings.append(dict(frame=n,raw_sha256=sha(f),PNG_sha256=sha(target)))
    sheet.save(a.output/'selected-actual-full-PPU.png');(a.output/'selected-frame-bindings.json').write_text(json.dumps(bindings,indent=2)+'\n')
    phase=components.get('lifecycle-native-result.json',{}).get('terminal_HUD_phase')
    if passed:
        assert frames==list(range(150,1801))and terminal and phase
        assert phase['start']['font']==396 and phase['IRQ_return']['font']==phase['endpoint']['font']==0
        assert phase['IRQ_entry']['ppu']['scanline']==31 and phase['IRQ_return']['PC']==0x8043
        assert components['lifecycle-native-result.json']['fresh_current_generation_updates']>=45
    failure_files=[str(f)for f in a.run.glob('*mismatch*.json')]+[str(f)for f in a.run.glob('*failure*.json')]
    evidence=dict(actual_terminal_preassert_event=terminal,actual_phase=phase,first_active_frame=active,first_capture_frame=capture,first_saved_HUD_font_frame=font,failure_snapshots=failure_files,IRQ_wording='IRQ_return observer executes at real RTI-entry PC8043, not after RTI. Endpoint is a later actual endFrame; separate8compiledIRQ tests prove RTI continuation under synthetic CPU states.',variant_readback_note='Terminal variant_readbacks uses the historical Lua serializer: integer0 is omitted when the table is serialized as an array. The unchanged native predicate explicitly requires keys0,1,2,3; actual per-frame HUD RAM/PPU records retain numeric variants. No all4 claim is inferred solely from that array.')
    (a.output/'terminal-phase-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    manifest={str(f.resolve()):sha(f)for f in a.run.rglob('*')if f.is_file()}
    for f in [a.ready/'proof.json',a.ready/'manifest.json',a.old_run/'lifecycle-proof.json',Path(__file__)]:manifest[str(f.resolve())]=sha(f)
    for f in a.output.iterdir():
        if f.is_file():manifest[str(f.resolve())]=sha(f)
    (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    q=dict(passed=bool(passed),native_run=True,launches=1,retries=0,native_worker_released=True,ROM_sha256=SHA,readiness_sha256=sha(a.ready/'proof.json'),component_results_present=sum(bool(x)for x in components.values()),component_results_required=5,component_bindings=receipt['component_bindings'],raw_ARGB_frames=len(raw),raw_frame_start=frames[0]if frames else None,raw_frame_end=frames[-1]if frames else None,terminal_phase_evidence_sha256=sha(a.output/'terminal-phase-evidence.json'),same_ROM_old_negative_RGB_prefix_matches=len(matches),same_ROM_old_negative_RGB_differences=len(diffs),same_ROM_old_original_bus_prefix_events=busmatches,original_bus_prefix_equal=busdiff is None,selected_actual_full_PPU_frames=selected,selected_frame_bindings_sha256=sha(a.output/'selected-frame-bindings.json'),manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),tool_sha256=sha(Path(__file__)),limits='ONE bounded natural-input OctopusEasy numeric0 menu1800 control only. Selected actual PPU review still requires human inspection, not allframe visual closure. Original failed receipt remains false. RTI observer is entry-before-instruction; laterendFrame and separatecompiledIRQ proof are distinct. No retry/death/area/body/adoption/fullroster/worstDMC verdict.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2));print('proof_sha256='+sha(a.output/'proof.json'))


if __name__=='__main__':main()
