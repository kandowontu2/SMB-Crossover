"""Freeze the current source, exact metadata and compact native menu receipts."""
from pathlib import Path
import sys,json,zipfile,hashlib
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from prepare_selected_native_packet_v1 import sha
O=R/'build/bub-menu-candidate-1102-v2';P=R/'build/bub-menu-integration-1102-v1'
PIN='90a7108003343ad9f5f9719f860f44f09d1e1932194d5eac1c89bc473e932dd8'

def main():
    assert sha(O/'candidate.nes')==PIN
    prior=json.loads((P/'frontend-source-freeze.json').read_text())
    for path,digest in prior['bindings'].items():assert sha(R/path)==digest,path
    native=O/'native-menu3/capture';result=json.loads((native/'result.json').read_text());binding=json.loads((native/'binding.json').read_text())
    assert result['passed']and result['positions']==33 and result['observations']==55 and result['screenshots']==4
    assert not result['gameplay_launch']and binding['exit_code']==0 and binding['ROM_sha256']==PIN
    assert result['active_data_writes']==result['late_enables']==0
    for packet in['native-menu3','native-ordered-bt-start','native-ordered-cf-start']:
        ready=json.loads((O/packet/'ready.json').read_text())
        for path,digest in ready['bindings'].items():assert sha(path)==digest,(packet,path)
    source_names=['compose_bub_menu_candidate_1102_v2.py','bub_menu_qualification_1102_v2.lua','prepare_bub_menu_qualification_1102_v2.py','repair_bub_menu_symbols_1102_v3.py','prepare_bub_menu_ordered_input_1102_v3.py','prepare_bub_menu_launch_probes_1102_v3.py',Path(__file__).name]
    sources=[R/'tools/audit'/name for name in source_names]+[R/'docs/qa/bub-menu-native-1102-v3.md']
    # The source proposal is already immutable in root's checkpoint. Include
    # its small exact patch/assembly receipts, not a recursive dependency tree.
    inputs=[P/name for name in['frontend-source-freeze.json','controls-proposal.json','art-proposal.json','flag-proposal.json','art-CPU-closure.json']]
    inputs +=[O/name for name in['candidate.json','candidate.dbg','candidate.lbl','candidate-importer-negative.dbg','metadata-repair.json','ordered-input-v3/CPU-ordered-input.json','ordered-input-v3/native-menu-plans.json']]
    for folder in['native-menu','native-menu2']:
        inputs +=[O/folder/name for name in['ready.json','controller.lua','capture/binding.json','capture/candidate-controller.log']]
    inputs.append(O/'native-menu2/capture/observations.csv')
    inputs +=[O/'native-menu3'/name for name in['ready.json','controller.lua','run.py','capture/result.json','capture/binding.json','capture/observations.csv','capture/candidate-controller.log']]
    pngs=[native/(name+'.png')for name in['bt-zitz','cf-beans','new-bub','new-bob']];inputs+=pngs
    # Include the prior seven source files without altering their checkpoint.
    old_sources=[R/path for path in prior['source_files_to_stage']]
    files=list(dict.fromkeys(sources+old_sources+inputs))
    hashes={p.relative_to(R).as_posix():sha(p)for p in files}
    archive=O/'frontend-current-source-v3.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in files:z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        assert all(hashlib.sha256(z.read(n)).hexdigest()==d for n,d in hashes.items())
    q=dict(passed=True,private_frontend_native_pass=True,ROM_SHA256=PIN,base='1cd8e192',menu_admitted=False,backend_native=False,installed=False,full_stage=False,
        native_result=result,archive=archive.relative_to(R).as_posix(),archive_SHA256=sha(archive),
        prior_immutable_checkpoint='docs/qa/checkpoints/2026-11-02/bub-static-frontend-v3',prior_seven_sources_exact=True,
        new_source_files_to_stage=[p.relative_to(R).as_posix()for p in sources],bindings=hashes,
        negative_packets=['native-menu: DBG importer before Lua','native-menu2: incorrect observer Select/confirm priority'],
        visual_review=dict(PNGs=4,new_graphical_defect_seen=False,source_art_unscaled=True,Bub_Bob_source_colors_distinct=True,new_icon_left=32,new_icon_card_top=160,new_icon_body_top=168,no_new_pending_star=True),
        unexecuted_packets=['build/bub-menu-candidate-1102-v2/native-ordered-bt-start','build/bub-menu-candidate-1102-v2/native-ordered-cf-start'],
        remaining=['Root executes old BT/CF actual Start/P1 restoration probes.','Compose actual raw39 backend and preserve WWF1966 disjoint3B update.','Root approves qualified private raw39 gate rebind, then genuine Bub/Bob gameplay/control/terrain/full1-1 and delivery.'],
        scope='Native static frontend only. No new shared runtime ownership, no Bub/Bob gameplay admission, no install/Git by this worker.')
    (O/'frontend-current-freeze-v3.json').write_text(json.dumps(q,indent=2)+'\n')
    allfiles=[p for p in O.rglob('*')if p.is_file()];assert sum(p.stat().st_size for p in allfiles)<32000000 and len(allfiles)<=128
    print(json.dumps(dict(passed=True,archive=q['archive'],archive_SHA256=q['archive_SHA256'],source_files=q['new_source_files_to_stage'],bytes=sum(p.stat().st_size for p in allfiles),files=len(allfiles))))
if __name__=='__main__':main()
