"""Detached current entry owner/capacity census; no new code or CPU mount."""
from hashlib import sha256
import json
import re

import compose_dkjr_footer_bt91dc_current_1116 as C
import check_dkjr_carry_camera_route_1116 as Route

Plan=C.Camera.Plan
W=Route.Cold.W
H=lambda value:sha256(value).hexdigest()


def descriptor(parent):
    raw,composition=C.proposal(parent)
    assert C.inverse(raw)==parent and H(raw)==C.CANDIDATE
    body=C.Camera.payload(raw)
    whole,known=Plan.source_inputs()
    pre=''.join(f'{name}=${value:x}\n'for name,value in known.items())
    complete=Plan.Source.T.assemble(pre+Plan.Source.expand_branches(whole),dict(
        DKJR=(0xa000,8160),DK_MAIN=(0xd65e,73),DK_PAUSE=(0xd540,286),DK_PORTS=(0xd6a7,345)))
    labels=complete['symbols']
    # The helper's inferred linear DData aliases are not all published maps:
    # c3cd/c3ce are explicit later source labels. Authenticate the real map.
    published={name:int(value,16)for value,name in re.findall(
        r'^al ([0-9a-fA-F]+) \.(\w+)$',Plan.LABEL_PATH.read_text().replace('\r\n','\n'),re.M)}
    drift=[(name,value,labels.get(name))for name,value in published.items()if labels.get(name)!=value]
    assert not drift,drift[:16]
    def offset(pc):
        assert 0xa000<=pc<0xc000 or 0xd000<=pc<0xd800
        return pc-0xa000 if pc<0xc000 else 9*1024+pc-0xd000
    def fragment(first,end):
        source=whole[whole.index(first+':'):whole.index(end+':')]
        local=set(re.findall(r'^(\w+):',source,re.M))
        definitions=Plan.numeric(whole)+''.join(f'{n}=${v:x}\n'for n,v in labels.items()if n not in local)
        at,size=labels[first],labels[end]-labels[first]
        code=Plan.Source.T.assemble(definitions+'.segment "PART"\n'+Plan.Source.expand_branches(source),
            dict(PART=(at,size)))
        before=code['images']['PART']
        assert code['used']['PART']==size and body[offset(at):offset(at)+size]==before,(first,end)
        return dict(PC=at,end_exclusive=labels[end],bytes=size,old_hex=before.hex(),old_SHA256=H(before))
    anchor=fragment('DkNativeAnchorReady','DkjrComponentEnd')
    constructor=fragment('DkConstruct','DkUnavailable')
    pause=fragment('DkPauseMain','DkPauseEnd')
    assert anchor['PC']==0xbfc1 and anchor['bytes']==31
    body_guard=bytes.fromhex('adfec8c902f0034c27bd')
    assert body[0xbc8c-0xa000:0xbc96-0xa000]==body_guard,body[0xbc8c-0xa000:0xbc96-0xa000].hex()
    scroll=bytes(body[9*1024+0x240:9*1024+0x25e])
    assert scroll[-3:]==bytes.fromhex('4c40d5')
    main=body[9*1024+0x65e:9*1024+0x6a7]
    assert main[:3]==bytes.fromhex('20c1bf') and bytes.fromhex('2040d2')in main
    reads=[];retire_redirects=[]
    for row in complete['instructions']:
        if row['operand']!=0xc8fe:continue
        at=offset(row['pc']);expected=bytes(({'LDA':0xad,'STA':0x8d,'INC':0xee}[row['op']],0xfe,0xc8))
        if body[at:at+3]!=expected:
            assert row['pc']==0xbdc9 and expected==bytes.fromhex('8dfec8')
            assert body[at:at+3]==bytes.fromhex('20c1b7')
            assert body[0xb7c1-0xa000:0xb7c4-0xa000]==expected
            retire_redirects.append(dict(old_PC=row['pc'],current_JSR_hex='20c1b7',actual_writer_PC=0xb7c1,
                role='Delivered DkPipeReset writes Ready then resets existing helper lifecycle'))
            continue
        reads.append(dict(PC=row['pc'],operation=row['op'],hex=expected.hex()))
    reads.append(dict(PC=0xb7c1,operation='STA',hex='8dfec8'))
    callers=Plan.literal_calls(body,anchor['PC'],anchor['end_exclusive'])
    assert callers==[dict(pc=0xd65e,opcode=0x20,target=0xbfc1)]
    bundle=dict(W.Symbols.bundle());bundle['raw']=raw
    names=('MovePlayerVertically','Entrance_GameTimerSetupCore','PlayerEntrance','PlayerRdy',
        'PlayerStarting_X_Pos','PlayerStarting_Y_Pos','AltYPosOffset','CrossoverVanillaMovement')
    native={}
    for name in names:
        pc,at=W.address(bundle,name),W.location(bundle,name)
        size=8 if name.endswith('_Pos')or name=='AltYPosOffset'else 32
        native[name]=dict(PC=pc,file=at,physical_PRG=(at-16)//8192,preimage_hex=raw[at:at+size].hex(),
            SHA256=H(raw[at:at+size]))
    vertical_at=16+62*8192+0x1af9
    vertical=raw[vertical_at:vertical_at+96]
    native['actual_MovePlayerVertically_far_continuation']=dict(PC=0xbaf9,file=vertical_at,
        physical_PRG=62,preimage_hex=vertical.hex(),SHA256=H(vertical),
        compiled_names=[name for name,row in bundle['syms'].items()
            if int(row['val'],16 if row['val'].startswith('0x')else 10)==0xbaf9
            and row.get('seg')in bundle['segs']and W.location(bundle,name)==vertical_at])
    other_at=16+62*8192+0x1a75
    native['actual_nonMario_vertical_continuation']=dict(PC=0xba75,file=other_at,physical_PRG=62,
        preimage_hex=raw[other_at:other_at+132].hex(),SHA256=H(raw[other_at:other_at+132]))
    assert raw[other_at:other_at+23]==bytes.fromhex('a200ad4a07d005ad1107d00aad0b078503a9044cf88b60')
    fruit=fragment('D_d955','D_da14')
    draw=fragment('D_ea08','D_eb69')
    start,end=labels['D_d955'],labels['D_da14']
    wrappers=[]
    for match in re.finditer(r'^DIndirect_([0-9a-f]+): lda \$ffff,y$',whole,re.M):
        suffix=match[1];name='D_'+suffix;pc=labels[name]
        if not start<=pc<end:continue
        part=whole[whole.index(name+':'):match.end()]+'\n'
        assert re.findall(r' lda \$(c[0-9a-f]{3})\n',part)==['c091','c092']
        local=set(re.findall(r'^(\w+):',part,re.M))
        definitions=''.join(f'{n}=${v:x}\n'for n,v in labels.items()if n not in local)
        code=Plan.Source.T.assemble(definitions+'.segment "WRAP"\n'+part,dict(WRAP=(pc,64)))['images']['WRAP']
        assert body[offset(pc):offset(pc)+len(code)]==code
        wrappers.append(dict(label=name,PC=pc,bytes=len(code),preimage_hex=code.hex(),SHA256=H(code)))
    assert len(wrappers)==4 and all(row['bytes']==25 for row in wrappers)
    return dict(detached=True,parent91dc_SHA256=H(parent),source_candidate_a3fb_SHA256=H(raw),
        packet_SHA256=composition['packet_SHA256'],current_anchor=anchor,current_constructor=constructor,
        live_pause= dict(PC=pause['PC'],bytes=pause['bytes'],SHA256=pause['old_SHA256'],
            scroll_D240_tail=scroll[-3:].hex(),still_live_not_funding=True),
        current_Main=dict(PC=0xd65e,bytes=len(main),SHA256=H(main)),
        current_body_ready_guard=dict(PC=0xbc8c,bytes=10,old_hex=body_guard.hex(),SHA256=H(body_guard),
            rejects_ready1=True,direct_source_OAM_output=True),
        exact_ready_direct_operands=reads,current_retire_redirect=retire_redirects,anchor_external_literal_ingress=callers,
        native_existing_components=native,
        source_declared_capacity=dict(anchor_envelope=31,anchor_spare=0,
            old_1073_floor_entry_proposal_uninstalled_and_not_leased_here=True,
            fruit_original=fruit,draw_original=draw,fruit_four_exact_wrappers=wrappers,
            possible_fruit_savings_before_shared_helper=4*(25-3),
            old_private_14B_prefix_depended_on_unavailable_shared_reader=True,
            self_contained_reader_cost=26,possible_standalone_net_fruit_savings=62,
            no_fruit_relocation_ABI_or_current_helper_lease_claim=True,
            new_RAM=0,new_carriers=0,no_padding_lease=True),
        lifecycle_plan=dict(
            normal_grounded='Ready1 native ground0: retain current import/camera/Ready2 admission.',
            forced_fall='Ready1 only, declared falling entrance1, native falling2/high1/dry/real normal play: native descent owns motion until fresh native ground/contact.',
            cold_respawn='Real constructor/reset Ready0->1 and forced/ordinary header entry must be checked independently; no persistent fresh flag.',
            pipe_vine='Preserve engine7 scripted pipe/vine movement and admission of ground0/climb3; do not capture upward/recoil or scripted collision-disabled states.',
            underwater='Native water entrance has SwimmingFlag1; outside the dry forced-fall path and retains current behavior.',
            pause='Pending native descent must not advance under TimerControl; avoid admitting Ready2 early during a frozen forced fall.',
            visible_pending='Ready1 body must be projected onto actual native coordinates and narrowly admitted for drawing, without donor physics or Ready2 publication.'),
        modified_code_generated=False,CPU_executed=False,source_overlay=False,ROM_composed=False,outputs=0,
        scope='Current exact existing-code census and detached state-owner/capacity proposal only; no new byte arrays, source mount or implementation authorization.')


if __name__=='__main__':
    report=descriptor(C.BT.ROM.read_bytes())
    text=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_FORCED_ENTRY_PLAN '+text,flush=True)
    print('DKJR_FORCED_ENTRY_PLAN_SHA256 '+H(text.encode()),flush=True)
