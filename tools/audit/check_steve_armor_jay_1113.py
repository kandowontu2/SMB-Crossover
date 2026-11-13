"""Preserve the delivered Jay head/helper behavior under Steve's shared cookie."""

import argparse
import json

import check_jay_head_bridge_1113 as HeadChecks
import check_jay_pickup_helper_1113 as HelperChecks
import compose_jay_head_bridge_1113 as Head
import compose_jay_pickup_helper_1113 as Helper
import compose_quick_climb_material_1113 as Quick
import replay_steve_armor_native_1113 as Native


PARENT = 'aa50112845d1cf70cae0924f03326647b3d2514f876c756d70b134ee44f971d1'
CANDIDATE = '2aa5096391ddc303c4dc346293db1b628ddee36222fb3a7eaa20649c003b6cea'


def check(parent,candidate,info):
    digest = Native.Packet.Entry.digest
    pin = digest(candidate)
    assert digest(parent) == PARENT and pin in (CANDIDATE,Native.IDLE_CANDIDATE)
    base = Head.inverse(Helper.inverse(Quick.inverse(parent)))
    assert digest(base) == Native.Packet.QUALIFICATION_PARENT
    head,head_info = Head.proposal(base)
    jay,helper_info = Helper.proposal(head)
    assert Quick.transform(jay)[0] == parent
    for page in (232,234,331,332):
        assert Native.Live.Art.page(parent,page) == Native.Live.Art.page(candidate,page),page
    opening,model = Head.cold(candidate,info['cookie'],pin)
    body = helper_info['new']['images']['HELPERS']
    assert bytes(model.ram[3][0x1d20:0x1d20+len(body)]) == body
    for name,(pc,_) in head_info['code']['layout'].items():
        body = head_info['code']['images'][name]
        assert bytes(model.ram[3][pc-0xa000:pc-0xa000+len(body)]) == body,name
    return dict(parent=PARENT,candidate=pin,opening=opening,
                physical_Jay_pages_unchanged=[232,234,331,332],
                actual_cold_helper_and_head_bytes_exact=True,
                genuine_QueryVertical=HeadChecks.caller_tiles(model,head_info['fields']),
                head_interrupts=HeadChecks.vectors(model,head_info),
                helper_finite=HelperChecks.finite(candidate,helper_info),
                helper_guards=HelperChecks.guards(candidate,helper_info),
                output_files=0,Mesen_run=False,
                scope='Actual native Jay cold/opening followed by supplied-model genuine head caller cases. Helper decision fixtures overlay only their already byte-verified helper body. Full authored-stage qualification remains separate.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--idle',action='store_true')
    args = parser.parse_args()
    parent = Native.Live.Art.D.HOST.read_bytes()
    if args.idle:
        import steve_armor_idle_1113 as Idle
        candidate,info = Idle.proposal(parent)
    else:
        candidate,info = Native.proposal(parent)
    print(json.dumps(check(parent,candidate,info),sort_keys=True),flush=True)
