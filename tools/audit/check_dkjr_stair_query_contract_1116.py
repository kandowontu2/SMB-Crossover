"""Read-only actual a3fb query/shape bindings for the root stair observer."""
from hashlib import sha256
import json

import compose_dkjr_footer_bt91dc_current_1116 as C
import check_dkjr_platform_query_lifecycle_1114 as Source

H=lambda value:sha256(value).hexdigest()


def contract(raw):
    assert H(raw)==C.CANDIDATE
    proof,labels=Source.closure(raw)
    body=C.Camera.payload(raw)
    old=C.historical_reference(raw)
    assert C.Camera.payload(old)==body
    selected=[r for r in proof['assembled_exact_current_fragments']if r['first']in
        ('D_e893','DkjrNativeTerrainHook','DkjrNativeWorldBuild','DkjrNativePhase','DkjrNativeSourcePhase')]
    entries={}
    for name in('DkjrSupportProbe','D_e8a5','D_e8a7','DkjrNativeTerrainHook','DkjrNativeWorldBuild',
        'NativeObjects','Platforms','DkjrNativeShiftCamera','DkjrNativePublishAnchor','DkjrBounds'):
        pc=labels[name];at=Source.H.T.offset(pc)
        entries[name]=dict(PC=pc,WRAM_bank=3 if pc<0xc000 else 2,preimage16=body[at:at+16].hex())
    rows={}
    for name,expected in(('DData_c379',bytes((7,0,24,15))),('DData_c389',bytes((9,0,25,15)))):
        pc=labels[name];at=Source.H.T.offset(pc)
        assert body[at:at+4]==expected
        rows[name]=dict(PC=pc,bytes=list(expected))
    return dict(passed=True,actual_image_SHA256=H(raw),same_query_payload_as_f544=True,
        historical_f544_used_only_for_payload_equality=True,authenticated_fragments=selected,entries=entries,
        shape_records=rows,
        shape_only_counterexample='For unchanged sourceX72, jump record gives left81/right97; ground gives left79/right96. This is a one-pixel right-foot shrink on landing, independent of an X write. Camera epoch still needs the actual query witness.',
        list_contract=dict(source_query='C03E..C041 [left,top,right,bottom]',last_contact='C042..C045, not a newly built list',
            WKind=0xc8db,WCount=0xc8dd,WWindow='C8E8..C8EB [left,right,top,bottom]',
            cached_camera='C435+256*C436',ready=0xc437,delta=0xc438,source_player_X=0xc213,
            kinds={'0_and_1':'C840','2':'C880','3_and_4':'C800'},
            records='4-byte [left,top,right,bottom], max60bytes then FF sentinel; WCount is byte length',
            timing='TerrainHook saves incoming A kind and calls WorldBuild every enabled query. WorldBuild captures current C03E..41, expands kind3 vertical window to bottom+1..bottom+2, and uses the current native ScreenLeft coordinate during tile enumeration. Original wrapper consumes rebuilt list after hook return.'),
        source_only=True,CPU_executed=False,outputs=0,stair_game_cause_not_yet_claimed=True)


if __name__=='__main__':
    raw,_=C.proposal(C.BT.ROM.read_bytes());q=contract(raw)
    encoded=json.dumps(q,sort_keys=True,separators=(',',':'))
    print('DKJR_STAIR_QUERY_CONTRACT '+encoded,flush=True);print('DKJR_STAIR_QUERY_CONTRACT_SHA256 '+H(encoded.encode()),flush=True)
