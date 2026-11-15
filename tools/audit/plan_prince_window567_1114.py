"""Read-only exact-span sprite proposal math, without a mounted image/overlay."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import audit_prince_sprite_window_options_1114 as Census


def geometry(data,frame,*,new=False):
    tag=int.from_bytes(data[2*frame:2*frame+2],'little')
    if tag==65535:return None
    at=tag&0x3fff;header=data[at];n,pages=header&15,(header>>4)&3
    prefix=bytes(data[at:at+2+pages]);at+=2+pages
    rows=[]
    def raw(count):
        nonlocal at
        for _ in range(count):rows.append(tuple(data[at:at+3]));at+=3
    def grid(count,compact,bx,by):
        nonlocal at
        for i in range(count):
            if compact:
                if not i&1:pair=data[at];at+=1
                nib=(pair&15)if i&1 else pair>>4
                tile=data[at];at+=1
                coord=((nib&12)<<2)|(nib&3)|((tile&1)<<2)
                tile=(tile|1)if new else(tile&254)
            else:coord,tile=data[at:at+2];at+=2
            rows.append(((by+8*(coord&15))&255,tile,(bx+8*(coord>>4))&255))
    if tag&0xc000==0x4000:
        control,bx,by=data[at:at+3];at+=3;k=control&127
        raw(k);grid(n-k,bool(control&128),bx,by)
    elif tag&0x8000:
        bx,by=data[at:at+2];at+=2
        grid(n,bool(tag&0x4000),bx,by)
    else:raw(n)
    assert len(rows)==n
    return prefix,bytes(v for row in rows for v in row)


def tile_locations(data):
    locations={};packets={};types=Counter();protected=set();per_packet={};local_locations={}
    def record(at,kind):
        old=data[at];delta=64 if kind=='compact'else 65
        assert old+delta<=255
        row=(kind,old,old+delta)
        if at in locations:assert locations[at]==row
        locations[at]=row;types[kind]+=1
        local_locations[at]=row
    for frame in range(239):
        tag=int.from_bytes(data[frame*2:frame*2+2],'little')
        if tag==65535 or tag in packets:continue
        local_locations={}
        start=at=tag&0x3fff;header=data[at];n,pages=header&15,(header>>4)&3
        protected.update(range(at,at+2+pages));at+=2+pages
        def raw(count):
            nonlocal at
            for _ in range(count):
                protected.update((at,at+2));record(at+1,'raw');at+=3
        def grid(count,compact):
            nonlocal at
            for i in range(count):
                if compact:
                    if not i&1:protected.add(at);at+=1
                    record(at,'compact');at+=1
                else:protected.add(at);record(at+1,'wide');at+=2
        if tag&0xc000==0x4000:
            control=data[at];protected.update(range(at,at+3));at+=3;k=control&127
            raw(k);grid(n-k,bool(control&128))
        elif tag&0x8000:
            protected.update((at,at+1));at+=2;grid(n,bool(tag&0x4000))
        else:raw(n)
        packets[tag]=(start,at)
        per_packet[tag]=local_locations
    spans=sorted(packets.values())
    assert all(lo>=478 and lo<hi<=0x174e for lo,hi in spans)
    overlaps=[(a,b)for a,b in zip(spans,spans[1:])if a[1]>b[0]]
    return locations,packets,types,protected,per_packet


def run(raw):
    assert sha256(raw).hexdigest()==Census.Current.BT.CANDIDATE,'Exact current f11 read-only input'
    P=Census.Old.New.Previous.Prince
    _,chunks,_=P.extract(raw);runtime,metadata,state=chunks
    locations,packets,types,protected,per_packet=tile_locations(metadata)
    # These are isolated proposal arrays only. They are never mounted in
    # NesBus, composed into a ROM, cold-loaded, or presented as a candidate.
    independent={}
    for tag,(lo,hi)in packets.items():
        packet=bytearray(metadata[lo:hi])
        for at,(_,old,new)in per_packet[tag].items():
            assert packet[at-lo]==old;packet[at-lo]=new
        independent[tag]=bytes(packet)
    blobs=sorted(set(independent.values()),key=lambda b:(-len(b),b))
    blobs=[b for i,b in enumerate(blobs)if not any(b in a for a in blobs[:i])]
    while len(blobs)>1:
        best=(0,0,0)
        for i,a in enumerate(blobs):
            for j,b in enumerate(blobs):
                if i==j:continue
                overlap=next((k for k in range(min(len(a),len(b)),0,-1)if a[-k:]==b[:k]),0)
                if overlap>best[0]:best=(overlap,i,j)
        overlap,i,j=best
        if not overlap:break
        merged=blobs[i]+blobs[j][overlap:]
        blobs=[b for k,b in enumerate(blobs)if k not in(i,j)]+[merged]
    packed=b''.join(blobs);old_data_end=max(hi for lo,hi in packets.values())
    assert 478+len(packed)<=old_data_end,('Pose data funding deficit',478+len(packed)-old_data_end)
    transformed=bytearray(metadata)
    transformed[478:478+len(packed)]=packed
    for frame in range(239):
        tag=int.from_bytes(metadata[frame*2:frame*2+2],'little')
        if tag==65535:continue
        at=478+packed.index(independent[tag]);newtag=(tag&0xc000)|at
        transformed[frame*2:frame*2+2]=newtag.to_bytes(2,'little')
    root=Census.Old.R
    base=root/'tools/audit/prepare_prince_climb_funded_1109_v1.py'
    mixed=root/'tools/audit/check_prince_run_support_funding_1110.py'
    from types import SimpleNamespace
    oldgeom=Census.Old.pure_function(base,'geometry',{})
    oldgeom=Census.Old.pure_function(mixed,'geometry',{'P':SimpleNamespace(geometry=oldgeom)})
    poses=parts=0
    for frame in range(239):
        old=geometry(metadata,frame);assert old==oldgeom(metadata,frame)
        proposed=geometry(transformed,frame,new=True)
        if old is None:assert proposed is None;continue
        prefix,records=old;newprefix,newrecords=proposed
        assert prefix==newprefix and len(records)==len(newrecords)
        for i in range(0,len(records),3):
            y,tile,x=records[i:i+3];ny,ntile,nx=newrecords[i:i+3]
            assert(ny,nx)==(y,x)and ntile==tile+65
            assert Census.Old.tile_window(ntile)==Census.Old.tile_window(tile)+5
            assert ntile&62==tile&62
            parts+=1
        poses+=1
    assert poses==204 and parts==1289
    needle=bytes.fromhex('29fe8db1d7');hits=[i for i in range(0xf00,0xf9c)if metadata[i:i+5]==needle]
    at,=hits
    assert runtime[0x1c40:0x1c43]==bytes.fromhex('ac04bd')
    assert runtime[0x1c43:0x1c45]==bytes.fromhex('a975')
    assert metadata[at+5:at+9]==bytes.fromhex('6829010a')
    changes=[dict(stream=0,offset=0x1c40,live_PC=0xbc40,old_hex='ac04bd',new_hex='c8c8c8',role='metadata cursor2+index to privatewindow5+index'),
        dict(stream=1,offset=at,live_PC=0xc800+at,old_hex='29fe',new_hex='0901',role='cache transformed compact tile as odd8x16')]
    changes.append(dict(stream=1,offset=0,live_PC=0xc800,bytes=old_data_end,
        old_SHA256=sha256(metadata[:old_data_end]).hexdigest(),
        new_SHA256=sha256(transformed[:old_data_end]).hexdigest(),
        role='239 bounded pose tags and exact equivalent immutable pose packet records'))
    for change in changes[:2]:
        change['old_SHA256']=sha256(bytes.fromhex(change['old_hex'])).hexdigest()
        change['new_SHA256']=sha256(bytes.fromhex(change['new_hex'])).hexdigest()
    table=[dict(offset=at,kind=kind,old=old,new=new)for at,(kind,old,new)in sorted(locations.items())]
    digest=lambda value:sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return dict(current_input=dict(kind='exact-f11-readonly',public_input_SHA256=sha256(raw).hexdigest()),source_stream_SHA256=list(map(lambda x:sha256(x).hexdigest(),chunks)),
        explicit_proposal_code=changes,unique_pose_packets=len(packets),metadata_tile_byte_count=len(table),
        metadata_tile_kinds=dict(types),metadata_tile_preimages_and_plan_SHA256=digest(table),
        rejected_direct_tile_rewrite_aliases=sorted(set(locations)&protected),
        pose_data_existing_half_open=[478,old_data_end],repacked_pose_data_half_open=[478,478+len(packed)],
        source_metadata_SHA256=sha256(metadata).hexdigest(),proposed_tile_data_only_SHA256=sha256(transformed).hexdigest(),
        frame_cases=239,present_poses=poses,facings=2,pattern_coordinate_cases=parts*2,
        geometry_coordinates_and_pages_exact=True,all_pattern_pair_offsets_exact=True,
        metadata_extent_exact=True,all_pose_pointers_rebound_to_identical_formatted_records=True,
        unowned_metadata_after_pose_extent_exact=transformed[old_data_end:]==metadata[old_data_end:],added_storage_bytes=0,new_scratch=0,
        CPU_cost_proposal=dict(publisher_added_cycles_per_page=2,compact_AND_to_ORA_added_cycles=0),
        local_ABI_reasoning=dict(publisher='A/X and C/V/I/D unchanged; INY N/Z immediately replaced by LDA#75; streamY saved before and restored after farcall',
            compact='AND/ORA both preserve C/V and X/Y; STA then PLA replace transient N/Z; compact coordinate bit is decoded from unchanged raw lowbit',
            tile_consumer='Returned tile is intentionally remapped; next ReadX BIT replaces N/V/Z and C remains unchanged',
            pending='Current bounded CPU/caller/IRQ/lifecycle proof has not executed this proposal'),
        proof_limits='Pure declared decoder math only; actual CPU/current publisher/flags/IRQ/lifecycle proof pending',
        mounted_arrays=0,ROM_composition=False,allocation_granted=False,Mesen=False,outputs=0)


if __name__=='__main__':
    q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print(json.dumps(q,separators=(',',':')),flush=True)
