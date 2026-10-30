"""Save Arthur's actual normal-eight-sprite smoke and its timing limitations."""
from pathlib import Path
import json
from checkpoint_host_progress_1030_v9 import packets
from checkpoint_roster_progress_1030_v2 import R,save,sha
from capture_budget import inventory,WORKSPACE_BYTES,WORKSPACE_SCAN_FILES


if __name__=='__main__':
    hs,b=packets([
        ('build/arthur-body-fair-v3/handoff.json','fc8b79c93dc3c036ef5ac4067b3c01f5327ee4bacc92621f0558627d8fdf40eb'),
        ('build/arthur-body-fair-v3/native-handoff-v7.json','c77526b923b7672226253922fdf7201070021be9dab836a8842509c0f26f2ea1')])
    source,native=hs
    assert native['process_exit']==0 and native['normal_eight_sprite_limit']
    assert native['actual_body_hardware']['actual_source_permutations']==186
    assert native['actual_body_hardware']['hardware_OAM_first8_checks']==401
    assert native['comparison']['lag_before']==212 and native['comparison']['lag_after']==216
    b[str(Path(__file__).resolve())]=sha(__file__)
    root_visual='Root viewed all six untouched wholeframes in the derived2x3 contact sheet. Menu/lives/jump/lance/final Arthur body black contours and blueworld/nativeground/HUD are coherent; inherited cyan menu band remains. Immediate engine8 game-start predraw capture is byteexact to baseline.'
    save('arthur-required-body-fair-native',dict(
        status=native['status'],ROM_sha256=native['candidate_sha256'],
        source_body_hardware8_cases=source['source_body_hardware8_cases'],
        actual64record_permutations=source['actual64record_permutations'],
        stable_tail_cycles=source['stable_tail_cycles'],
        source_foreign_Main=source['foreign_Main'],
        native_semantics=native['semantic_result'],
        native_hardware=native['actual_body_hardware'],
        actual_native_comparison=native['comparison'],
        root_wholeframe_visual_review=root_visual,
        limits=native['limits']),b)
    p=R/'docs/qa/host-integration-progress-2026-10-30.json';j=json.loads(p.read_text())
    j['root_completed_this_continuation'] += [
        'Arthur09237b6f normal8 native400controller smoke exits0:186actual64recordpermutations/401actualDMAfirst8checks/39320mappedCHRblackpixels/max11bodyrecords. Allsourcecache/movement/doublejump/lance/scroll/palette guards pass; root viewed6wholeframes. v6reservationdefault failure beforeMesen retained; v7sameROM/controller only tightens isolated reservation to512MiB/64files.',
        'Arthur requiredbodypriority graphicsPASS but performanceHOLD: same400physical source134ticks; lag212to216,meanforeground23356.681to23878.396(+521.715),max33210to35233. ExistingstandaloneA79common1939B overlaps currentjointliveB5E0..<BF93. No privatepromotion or newRAM1allocation.'
    ]
    j['active_work']['Arthur']='Private09237 native graphicsPASS/normal8 with requiredblackbodyprotected and fairtail,400controller/6PNGs/33files/36946B. PerformanceHOLD216lagvs212,mean+521.715CPU; genuinejointA79overlap blockscomposition. ActualROMcold/NMI/table/CHRownershipaudit underway for explicitcapacityproposal; RAM1notgranted. PublicArthurblacklayer alreadyindependentofShadows.'
    v=inventory(R,WORKSPACE_BYTES,WORKSPACE_SCAN_FILES);assert v.complete
    j['measured_workspace_bytes']=v.bytes
    j['measured_workspace_files']=v.files
    p.write_text(json.dumps(j,indent=2)+'\n')
    print(json.dumps(dict(workspace_bytes=v.bytes,workspace_files=v.files,under_70GB=True)))
