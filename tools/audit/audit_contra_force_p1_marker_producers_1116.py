"""Read-only current6a3 CF tag-producer inventory; no proposed bytes or mount."""
from collections import Counter
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch
import json,re
import compose_bowser_life_gain_signed_1116 as Current
import profile_contra_force_current_costs_1115 as P

C,W,N=P.C,P.W,P.N
CURRENT_SHA='2b5d81f056991636bf2498d4871645ea1cd80b003d2d986504b46b89d8b013b7'
PROFILE_SHA='721d91c5220c20f71d31cb61683b05cfb3612244b4f86aff1d3c6c692d8f1a94'
SOURCES={
 'build/contra-force-projectile-contact-1031-v3/kernel/p1-runtime.s':'e15911ff74498252b944ce25075ff80706214729197a0b0b219ab250247e2483',
 'build/contra-force-scroll-publisher-1031-v2/kernel/render.s':'ec13de394b343ff25413ee5dd19b44decda54beb6682d9ef432ecd4efa5ebf11',
 'build/contra-force-world-roles-1031-v2/kernel/host-runtime.s':'8062a45639ab0e69190a3e602d4f3a4f6b06311c385508d7c9b08fab37156f52',
 'build/contra-force-p1-kernel-v1/a2-router.s':'410d81b56f20bbff77c1732164a9879395aef8ce3d2ee6daf6c9c7be76ce56c2',
 'build/contra-force-projectile-contact-1031-v3/kernel/component.s':'2150e84fb80f740f84fab66b23ce3bdef5785175888dc519698d69beaa46b201',
 'build/contra-force-projectile-contact-1031-v3/kernel/state.inc':'c67cb5cfb5932ff7f32e12203db59b26ae7488e6344a355d8fa02574dd958cf8',
 'src/metasprite_engine.s':'f328cab1c2a649317e0dbebe6c6dc892b27e105046acc0207e1c6a3ceaf00ebe',
 'src/native_goomba_draw.s':'5bf1375a0c57ff49dfa592723ce3f569b940f1a195b39cd9c38d838673a4a97f'}


@lru_cache(maxsize=1)
def bindings(raw):
    assert C.H(Path(Current.__file__).read_bytes())==CURRENT_SHA
    assert C.H(Path(P.__file__).read_bytes())==PROFILE_SHA
    assert isinstance(raw,bytes)and C.H(raw)==Current.CANDIDATE,'Exact current6a3 required'
    reference=Current.inverse(raw);assert C.H(reference)==C.CANDIDATE
    q=P.bindings(reference);b=dict(q['bundle'],raw=raw)
    assert b['raw']is raw and raw[P.CHR+935*1024:P.CHR+959*1024]==q['carrier']
    # All native dispatcher/table code is in the unchanged PRG half. The only
    # life correction is a distinct CHR carrier plus its declared two views.
    changes={i for i,(x,y)in enumerate(zip(raw,reference,strict=True))if x!=y}
    owned=set()
    for at,old,new in Current.spans():
        assert raw[at:at+len(new)]==new and reference[at:at+len(old)]==old
        owned.update(range(at,at+len(old)))
    assert len(owned)==72 and len(changes)==56 and changes<=owned
    texts={}
    for path,pin in SOURCES.items():
        data=(C.R/path).read_bytes();assert C.H(data)==pin,(path,'Changed source')
        texts[path]=data.decode()
    segments={};symbols={};lines={};spans={}
    for line in(P.KERNEL/'runtime.dbg').read_text().splitlines():
        if not line.startswith(('seg\t','sym\t','line\t','span\t')):continue
        row=P.fields(line);kind=line.split('\t',1)[0]
        {'seg':segments,'sym':symbols,'line':lines,'span':spans}[kind][int(row['id'])]=row
    return dict(raw=raw,reference=reference,q=q,bundle=b,texts=texts,segments=segments,symbols=symbols,lines=lines,spans=spans)


def symbol(z,name):
    rows=[r for r in z['symbols'].values()if r.get('name')==name and'val'in r and'seg'in r]
    out={(int(r['val'],0),int(r['seg']))for r in rows};assert len(out)==1,(name,out)
    pc,seg=out.pop();return pc,z['segments'][seg]


def private_read(z,name,count):
    pc,seg=symbol(z,name);tag=int(seg['oname'][3]);at=(tag-1)*8192+(pc&8191)
    return z['q']['carrier'][at:at+count],dict(name=name,physical_RAM=tag,PC=pc,bytes=count)


def private_records(z):
    result=[]
    for family,frames,count in(('Body',192,156),('Shot',139,123)):
        index,index_binding=private_read(z,'Cf'+family+'FrameIndex',frames)
        sizes,size_binding=private_read(z,'Cf'+family+'Bytes',count)
        lo,_=private_read(z,'Cf'+family+'Lo',count);hi,_=private_read(z,'Cf'+family+'Hi',count)
        assert set(index)-{255}==set(range(count))
        bank=size_binding['physical_RAM'];attrs=Counter();lengths=Counter();record_hashes=[]
        for i,n in enumerate(sizes):
            assert n>0 and n%4==0,(family,i,n)
            ptr=lo[i]+256*hi[i];at=(bank-1)*8192+(ptr&8191)
            data=z['q']['carrier'][at:at+n];assert len(data)==n
            # CF records have no length prefix: dy,dx,tile,attributes.
            values=data[3::4];assert not any(a&24 for a in values),(family,i,values.hex())
            attrs.update(values);lengths[n]+=1;record_hashes.append(C.H(data))
        row=dict(family=family,frame_index=index_binding,bytes_table=size_binding,unique_records=count,
            total_parts=sum(attrs.values()),attribute_values=[dict(value=a,parts=n)for a,n in sorted(attrs.items())],
            record_lengths=dict(sorted(lengths.items())),record_hashes_SHA256=C.H(''.join(record_hashes).encode()),
            all_record_attribute_tag_bits_18_zero=True)
        if family=='Shot':
            loan,binding=private_read(z,'CfShotNeedsLoan',count);assert set(loan)<={0,1}
            row.update(loan_binding=binding,loan_records=sum(loan),nonloan_records=loan.count(0))
        result.append(row)
    return result


def compiled_marker_refs(z):
    refs=[]
    for sym in z['symbols'].values():
        target=sym
        if'val'not in target and'exp'in target:target=z['symbols'][int(target['exp'])]
        if target.get('val')!='0xC2DF':continue
        for n in map(int,filter(None,sym.get('ref','').split('+'))):
            line=z['lines'][n];item=dict(alias=sym['name'],source_file_id=int(line['file']),line=int(line['line']))
            codes=[]
            for sn in map(int,filter(None,line.get('span','').split('+'))):
                sp=z['spans'][sn];seg=z['segments'][int(sp['seg'])]
                if seg.get('oname')not in('ram1.bin','ram2.bin','ram3.bin'):continue
                tag=int(seg['oname'][3]);pc=int(seg['start'],0)+int(sp['start'],0)
                nbytes=int(sp['size'],0);at=(tag-1)*8192+(pc&8191)
                codes.append(dict(physical_RAM=tag,PC=pc,hex=z['q']['carrier'][at:at+nbytes].hex()))
            item['compiled_spans']=codes;refs.append(item)
    assert {r['source_file_id']for r in refs}=={8,13,15}
    state=z['texts']['build/contra-force-projectile-contact-1031-v3/kernel/state.inc']
    component=z['texts']['build/contra-force-projectile-contact-1031-v3/kernel/component.s']
    aliases={name:int(offset,16)for name,offset in re.findall(r'^(\w+)\s*=\s*CfState\+\$([0-9a-f]+)',state,re.I|re.M)}
    assert all(v!=0x2df for v in aliases.values())
    indirect=[(i,line.strip())for i,line in enumerate(component.splitlines(),1)if re.match(r'\s*(sta|stx|sty|inc|dec|asl|lsr|rol|ror)\s+\(',line,re.I)]
    assert len(indirect)==1 and indirect[0][1]=='STA (CfPointers),Y'
    assert 'ram_score = CfState+$006e'in state
    assert '.word ram_score      ; 00 p1'in component and '.word ram_score + $03  ; 02 p2'in component
    potential=[]
    for i,line in enumerate(component.splitlines(),1):
        match=re.match(r'\s*(sta|stx|sty|inc|dec|asl|lsr|rol|ror)\s+(\w+)(?:\s*\+\s*\$([0-9a-f]+))?\s*,\s*([xy])\b',line,re.I)
        if not match or match[2]not in aliases:continue
        offset=aliases[match[2]]+int(match[3]or'0',16)
        if 0x2df-255<=offset<=0x2df:
            potential.append(dict(line=i,source=line.strip(),base_offset=offset,index_to_marker=0x2df-offset))
    return dict(marker_physical_RAM=2,marker_PC=0xc2df,compiled_alias_references=refs,
        literal_area_reset_source='CfHostAreaReset: LDA0/STA CfState+$02df, then clears pages3/4',
        constructor_source='CfHostConstruct: exact five-page bulk clear includes C2DF',
        native_component_indirect_writes=[dict(line=i,source=s)for i,s in indirect],
        sole_indirect_score_destination_half_open=[0xc06e,0xc074],
        original_named_state_alias_at_marker=False,
        native_indexed_store_leads_requiring_actor_index_bound=potential)


def native_records(z):
    raw=z['raw'];b=z['bundle'];rightlo=W.location(b,'MetaspriteTableRightLo');righthi=W.location(b,'MetaspriteTableRightHi')
    leftlo=W.location(b,'MetaspriteTableLeftLo');lefthi=W.location(b,'MetaspriteTableLeftHi')
    bank=(rightlo-16)//8192;base=16+bank*8192;attrs=Counter();parts=0;records=[]
    for mid in range(1,145):
        for facing,tl,th in(('Right',rightlo,righthi),('Left',leftlo,lefthi)):
            ptr=raw[tl+mid]+256*raw[th+mid];at=base+(ptr&8191);count=raw[at]
            assert count%4==0 and at+count+1<=base+8192,(mid,facing,count,ptr)
            data=raw[at:at+count+1];values=data[2::4]
            assert not any(a&16 for a in values),(mid,facing,values.hex())
            attrs.update(values);parts+=len(values);records.append(C.H(data))
    direct=[]
    for name in('FirebarSprite1','FirebarSprite2','DrawBrickDebris::Chunk'):
        at=W.location(b,name);data=raw[at:at+raw[at]+1];assert len(data)==5 and not data[2]&24
        direct.append(dict(name=name,file=at,physical_PRG=(at-16)//8192,PC=W.address(b,name),record_hex=data.hex()))
    callbacks=[]
    for name in('MetaspriteRenderLoop','NativeGoombaRender','DrawWorldFirebars','DrawBrickDebris','FloateyNumberRender',
                 'SamusFreezeFlashOwner','SamusFreezeColorActor','SamusDrawShots','MegaManFullShotBank',
                 'RlSpecialDrawDispatch','JnSpecialDrawDispatch','Z2LateWorldAdmission'):
        at=W.location(b,name);assert raw[at:at+32]==z['reference'][at:at+32]
        callbacks.append(dict(name=name,file=at,PC=W.address(b,name),physical_PRG=(at-16)//8192,first32_hex=raw[at:at+32].hex()))
    return dict(native_world_pose_domain=[1,144],facing_cases=288,total_parts=parts,
        native_record_tag10_zero=True,native_generic_and_fast_Goomba_mask_F3_clears_tag08=True,
        record_attribute_values=[dict(value=a,parts=n)for a,n in sorted(attrs.items())],
        record_hashes_SHA256=C.H(''.join(records).encode()),native_table_bank_SHA256=C.H(raw[base:base+8192]),
        direct_records=direct,callback_preimages=callbacks,
        proposed_conservative_native_marker='Mark40 for every nonzero ObjectMetasprite in slots1..23, including >=145; original CPY145 mask rejection remains',
        direct_static_attribute_contracts={'firebars':'R3=0/C0, descriptor attr2','brick_chunks':'R3=(FrameCounter<<4)&C0 |3, descriptor attr0',
          'score_numbers':'R3=0; immutable native metasprite records','vine':'fixed21/61 attributes','wind_leaves':'fixed41 attributes'},
        foreign_owner_and_actual_dispatch_closure_pending=True)


def audit(raw):
    z=bindings(raw)
    return dict(execution_input_SHA256=C.H(raw),metadata_reference_bc5_SHA256=C.H(z['reference']),
        actual_current_CF_payload_SHA256=C.H(z['q']['carrier']),all_CF_owned_payload_bytes_equal_reference=True,
        exact_new_input_boundary='6a3 -> signed72 portable inverse -> exactbc5, reference only',
        sources=SOURCES,private_pose_records=private_records(z),marker_refs=compiled_marker_refs(z),
        native_OAM_sources=native_records(z),new_code_arrays_or_game_opcode_changes=0,
        no_source_overlay_or_ROM_or_native_or_delivery=True,outputs=0)


if __name__=='__main__':
    raw=C.ROM.read_bytes()
    reader=Path.read_bytes
    def read(path):
        assert path.resolve()!=C.ROM.resolve(),'No second mutable Nightly read'
        return reader(path)
    def deny(*a,**kw):raise AssertionError('Read-only marker inventory attempted files/native')
    with patch.object(Path,'read_bytes',read),patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=audit(raw)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
