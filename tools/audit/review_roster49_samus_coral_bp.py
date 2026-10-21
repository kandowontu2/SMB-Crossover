"""Verify the real native coral displacement and its first responsible routines."""
from pathlib import Path
import csv,hashlib,importlib.util,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-current-f-samus-coral-diagnostic-bn';P=R/'build/roster-through-2-2/root49-f-samus-coral-bn-2-v0-mmc3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):
    with p.open(newline='')as f:return list(csv.DictReader(f))
def main():
    out=V/'root49-samus-f-coral-defect-review-bp.json';assert not out.exists()
    n=json.loads((H/'native-result.json').read_text());pre=json.loads((H/'preparation.json').read_text())
    assert sha(H/'preparation.json')==n['preparation_sha256']and sha(H/'native.log')==n['native_log_sha256']and sha(P/'manifest.json')==n['manifest_sha256']
    for name,h in pre['dependencies'].items():assert sha(R/name)==h,name
    assert sha(H/'policy.lua')==pre['policy_sha256']
    m=json.loads((P/'manifest.json').read_text());assert m['result']['frames']==29945 and m['result']['failure']=='frame limit'
    assert m['controller_only']and m['full_frame_audit']and not m['memory_or_register_writes']and not m['config']['record']
    assert m['rom_sha256']==sha(P/'smb-crossover-mmc3.nes')=='ae0f981a8846238185d2d69549accf69f68b779832cafa7dd35bc431b00b09ca'
    parent=R/'build/roster-through-2-2/root49-f-samus-route-v-2-v0-mmc3';trace=rows(P/'trace.csv')
    assert trace==rows(parent/'trace.csv')[:29945]and rows(P/'inputs.csv')==rows(parent/'inputs.csv')[:29944]
    helper=V/'agent49g-samus-crouch-fix-proposal-b/image.py';sp=importlib.util.spec_from_file_location('coral_defect_image',helper);im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im);image=im.Image(P/'smb-crossover-mmc3.nes')
    for h in pre['hooks'].values():assert list(image.raw[h['rom_offset']:h['rom_offset']+8])==h['bytes']
    table=image.hook('BlockBuffer_Y_Adder',delta=58);assert table['bytes'][0]==7
    data=rows(P/'coral-writers.csv');assert len(data)==335
    first=[z for z in data if z['frame']=='29923']
    enter=next(z for z in first if z['event']=='SamusHeadProbe');done=next(z for z in first if z['event']=='HeadProbeDone')
    assert enter['playerX']=='1235'and enter['playerY']=='171'and enter['Y']=='58'
    assert done['playerX']=='1235'and done['playerY']=='185'and done['SmCeilingHit']=='1'and done['SmTempY']=='185'
    # Diagnostic header R0..R7 is raw ZP00..07, while actual symbols start at3.
    assert image.ram['R0']==3 and image.ram['R2']==5
    assert done['R5']=='144'and 144+48-table['bytes'][0]==185
    left=next(z for z in first if z['event']=='WallLeftClamp');assert left['playerX']=='1235'and left['playerY']=='185'and left['R3']=='2'
    clamped=next(z for z in first if z['event']=='write-Player_X_Position'and z['pc']=='41719');assert clamped['writeValue']=='223'and clamped['playerX']=='1235'
    assert trace[29921]['x']=='1233'and trace[29922]['x']=='1247'and trace[29923]['x']=='1263'and trace[29930]['x']=='1375'
    assert trace[29922]['y']=='185'and trace[29930]['y']=='192'
    report=dict(status='CONFIRMED_CURRENT_F_SAMUS_CORAL_HEAD_SEPARATION_AND_SIDE_CLAMP_DEFECT',script_sha256=sha(__file__),preparation_sha256=sha(H/'preparation.json'),manifest_sha256=sha(P/'manifest.json'),
      writer_log_sha256=sha(P/'coral-writers.csv'),literal_parent_trace_rows=29945,literal_parent_input_rows=29944,writer_records=335,actual_entry=enter,actual_head_return=done,actual_left_clamp_entry=left,actual_left_clamp_write=clamped,
      source_causal_sequence='Real movement moves X1233→1235 and Y176→171. SamusHeadProbe right span sees solid coral tile105 at the side, computes144+48−7=185 and marks a ceiling. Source wall hook then takes left contact/R0=2 while already embedded, clamps1235→1247 and then sixteen pixels per update. Post-BG hook retains185; later floor snaps192.',
      diagnostic_scratch_label_correction='The logger header R0..R7 represents raw addresses00..07. Actual R0 starts03; actualR2 is raw05=144, not raw02=0. No original log rewritten. Full RAM symbol addresses are bound by the F image metadata.',
      quarantined_scope='The V route after frame29923 is invalid movement evidence. Do not count X1375 as a legitimate coral traversal or avoid this defect with a different jump controller. Prior T five-stage route and unrelated character proofs retain their original scopes.',
      next_action='Add a minimal authored coral-side jump regression for Easy/Hard and water/dry, preserve baseline failure. Trace previous/current head and side classification against pinned2.02 terrain HitTester, then build an isolated source-correct fix. Recheck head/brick/wall/pickup matrices and ordinary exact V controller prefix on both maps before adoption.',
      primary_sources={name:sha(R/name)for name in ['src/samus.s','reference/crossover2/extracted/scripts/com/smbc/characters/Character.as','reference/crossover2/extracted/scripts/com/smbc/main/AnimatedObject.as','reference/crossover2/extracted/scripts/com/smbc/level/Level.as']},
      fixture_gap='Existing zero-wall arenas separate static wall cases from overhead upward head cases. They do not combine an actual fresh supported jump at a coral side with horizontal movement and fractional X.',
      repaired=False,shared_source_or_ROM_changed=False,accepted_release=False,goal_complete=False)
    out.write_text(json.dumps(report,indent=2)+'\n');print(report['status'],sha(out),flush=True)
if __name__=='__main__':main()
