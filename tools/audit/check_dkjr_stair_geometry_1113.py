"""Read exact donor/current body and terrain rectangle domains; no artifacts."""
from hashlib import sha256
import json

import prepare_dkjr_native_source_1102_v2 as Original
import compose_dkjr_direct_platform_1113 as Current
import check_dkjr_direct_platform_1113 as Gate


def main():
    donor=Original.D.donor();mem=Original.D.Bus(donor)
    lists,tables=Original.original_geometry(mem)
    source_lists={name:[dict(stage=i+1,pointer=ptr,
        rects=[list(lists[ptr][j:j+4])for j in range(0,len(lists[ptr])-1,4)]if ptr in lists else None)
        for i,ptr in enumerate(ptrs)]for name,ptrs in tables.items()}
    _,raw=Current.load_inputs();body=Current.P.T.payload(raw)
    bounds=bytes(mem[0xc379:0xc399]);matches=[];start=0
    while True:
        at=body.find(bounds,start)
        if at<0:break
        matches.append(0xa000+at);start=at+1
    assert len(matches)==1,matches
    W=Gate.W;b=W.Symbols.bundle();b['raw']=raw
    native={}
    for name in('BlockBufferAdderData','BlockBuffer_X_Adder','BlockBuffer_Y_Adder'):
        at=W.location(b,name);native[name]=dict(CPU=W.address(b,name),file=at,
            bytes=list(raw[at:at+(11 if name=='BlockBufferAdderData'else 86)]))
    all_labels=Current.P.frozen_labels()
    labels={name:pc for name,pc in all_labels.items()if name in('DkjrWallProbe','DkjrSupportProbe',
        'DkjrNativeTerrainHook','DkjrNativeWorldBuild','DkjrNativeSourcePhase',
        'DkjrBounds','DkjrLand','DkjrTransition','DkjrNativePublishAnchor',
        'DkNativeAdder','DkNativeBoxProfile','D_d5e7','D_d631')}
    current_leaves={name:body[Current.P.T.offset(pc):Current.P.T.offset(pc)+8].hex()
        for name,pc in labels.items()if name in('DkNativeAdder','DkNativeBoxProfile','D_d5e7','D_d631')}
    solid_rect=bytes.fromhex('ade2c88de5c818690f8de7c8')
    solid_at=body.find(solid_rect)
    assert solid_at>=0 and body.find(solid_rect,solid_at+1)<0
    publish=labels['DkjrNativePublishAnchor'];publish_at=publish-0xa000
    publish_body=body[publish_at:publish_at+80];publish_writers={}
    for name in('Player_X_Position','Player_Y_Position'):
        field=W.address(b,name);pattern=bytes((0x85,field))
        offsets=[i for i in range(len(publish_body)-1)if publish_body[i:i+2]==pattern]
        assert len(offsets)==1
        point=publish+offsets[0]
        publish_writers[name]=dict(store_PC=point,opcode_hex=pattern.hex(),
            observed_post_store_PC=point+2)
    print('DKJR_STAIR_GEOMETRY '+json.dumps(dict(candidate_SHA256=sha256(raw).hexdigest(),
        original_SHA256=sha256(donor).hexdigest(),original_geometry=source_lists,
        original_body_PC=0xc379,current_identical_body_PC=matches[0],
        body_rect_offsets=[list(bounds[i:i+4])for i in range(0,32,4)],
        source_origin=dict(X='nativeX-cameraX-8',Y='nativeY+15'),
        unchanged_body_bytes=True,native_probe_tables=native,retained_source_labels=labels,
        current_leaf_preimages=current_leaves,
        current_solid_rect_PC=0xa000+solid_at,
        current_solid_rect_preimage=body[solid_at:solid_at+22].hex(),
        publisher_position_writers=publish_writers,
        scope='Read-only source/table census. No same-cut runtime equivalence or bug conclusion.',
        outputs_written=0),separators=(',',':')),flush=True)


if __name__=='__main__':main()
