"""Declared current-world tests of an unallocated static-floor predicate.

Only instruction fetches at its virtual measurement address are supplied by
an immutable Python byte string. Existing ROM and private code are unchanged.
This is not cartridge placement, native replay, or an ownership lease.
"""
from hashlib import sha256
import argparse
import json

import measure_dkjr_floor_entry_handlers_1114 as M

S=M.S;F=S.Replay;G=F.Gate
Q,P,H,N,W,L=G.Q,G.P,G.H,G.N,G.W,G.L


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--current-kind',choices=M.Input.KINDS,default='hidden-421')
    args=ap.parse_args();measured=M.measure(current_kind=args.current_kind);record=measured['static_floor_validator']
    code=bytes.fromhex(record['generated_hex']);entry=record['measurement_origin']
    _,old=F.load_inputs();raw,_=S.proposal(old)
    _,seed=H.cold(raw,raw[P.B.COOKIE_AT:P.B.COOKIE_AT+16])
    source_cases=(('both_feet',0,1,176,8,False,True),
        ('left_foot_only',0,None,176,8,False,True),
        ('right_foot_only',1,None,176,8,False,True),
        ('no_floor',None,None,176,8,False,False),
        ('far_page_only',None,None,176,8,True,False),
        ('not_aligned',0,1,175,8,False,False),
        ('off_left_representation',0,1,176,7,False,False),
        ('off_right_representation',14,15,176,232,False,False),
        ('both_toes_past_left_edge',0,None,176,13,False,False),
        ('helper_without_static',None,None,176,8,False,False))
    cases=[]
    for name,first,second,y,relative,far_floor,expected in source_cases:
        m=Q.mounted(seed,raw);camera=2561;world=camera+relative
        N.put(m,Player_X_Position=world&255,Player_PageLoc=world>>8,
            ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8,
            ScreenRight_X_Pos=(camera+255)&255,ScreenRight_PageLoc=(camera+255)>>8,
            Player_Y_Position=y,Player_Y_HighPos=1,Player_State=0)
        for index,buffer in enumerate(('Block_Buffer_1','Block_Buffer_2')):
            at=W.address(m.bundle,buffer);m[at:at+208]=bytes(208)
            if index==0:
                for col in (first,second):
                    if col is not None:m[at+176+col]=0x54
            elif far_floor:m[at+176:at+192]=bytes((0x54,))*16
        m.ram[2][0x6b]=m.ram[2][0x6c]=4;m.ram[2][0x76]=194
        m.ram[2][0x210]=216;m.ram[2][0x213]=255;m.ram[2][0x8f5]=y+32
        actor_count=None
        if name=='helper_without_static':
            slot=3
            for field,value in dict(Enemy_ID=37,Enemy_Flag=1,Enemy_X_Position=2576&255,
                Enemy_PageLoc=2576>>8,Enemy_Y_Position=208,Enemy_Y_HighPos=1).items():
                m[W.address(m.bundle,field)+slot]=value
            N.invoke(m,'InitEnemyObject',x=slot)
            for field,value in dict(Enemy_ID=37,Enemy_Flag=1,Enemy_State=0,
                Enemy_X_Position=2576&255,Enemy_PageLoc=2576>>8,Enemy_Y_Position=208,
                Enemy_Y_HighPos=1,Enemy_BoundBoxCtrl=5,PlatformCollisionFlag=255).items():
                m[W.address(m.bundle,field)+slot]=value
            H.call(m,P.frozen_labels()['DkjrNativeRefreshPlatforms'])
            box=list(m[0x658+4*(slot+1):0x65c+4*(slot+1)])
            m.ram[2][0x3e:0x42]=bytes((11,box[1]-17,20,box[1]-2));m.ram[2][0x8db]=3
            H.call(m,P.frozen_labels()['DkjrNativeWorldBuild'])
            actor_count=m.ram[2][0x8dd]
            assert actor_count>0,('Declared native helper did not provide its control plane',box)
        saved_query=bytes((9,77,23,91));m.ram[2][0x3e:0x42]=saved_query;m.ram[2][0x8db]=4
        state_before=bytes(m.ram[2][0x6b:0x88]);body_before=bytes(m.ram[2][0x210:0x230])
        Base=type(m)
        class VirtualCode(Base):
            def __getitem__(self,at):
                if isinstance(at,int)and entry<=at<entry+len(code):return code[at-entry]
                return super().__getitem__(at)
        m.__class__=VirtualCode
        query_kinds=[]
        def observe(memory,cpu):
            if cpu.pc==P.frozen_labels()['DkjrNativeWorldBuild']and memory.rawtags[1]==3:
                query_kinds.append(memory.ram[2][0x8db])
        result=H.call(m,entry,p=0x61,observe=observe)
        assert query_kinds in ([],[2])
        assert bool(result.p&1)==expected,(name,result.p,list(m.ram[2][0x880:0x88c]))
        assert bytes(m.ram[2][0x3e:0x42])==saved_query and m.ram[2][0x8db]==4
        assert bytes(m.ram[2][0x6b:0x88])==state_before
        assert bytes(m.ram[2][0x210:0x230])==body_before
        cases.append(dict(name=name,qualified_static_floor=bool(result.p&1),
            native_relative_x=relative,native_y=y,stale_native_grounded_state=0,
            original_source_y=216,world_query_kinds=query_kinds,
            valid_helper_control_kind3_bytes=actor_count,
            static_rectangles=list(m.ram[2][0x880:0x880+m.ram[2][0x8dd]])if query_kinds else None,
            original_query_kind_body_fall_fields_preserved=True))
    print('DKJR_STATIC_FLOOR_PROBE '+json.dumps(dict(passed=True,
        private_input_SHA256=S.PIN,virtual_code_SHA256=sha256(code).hexdigest(),
        current_review_input=measured['current_review_input'],
        virtual_code_bytes=len(code),cases=cases,
        no_actor_plane_in_world_kind2=True,old_native_adder_and_current_tables_exact=True,
        ROM_composed=False,ROM_written=False,CHR_or_RAM_lease_granted=False,outputs_written=0,
        scope='Unallocated virtual fragment calls actual current WorldBuild with kind2 at exact native feet3/12,Y32. Declared static geometry differentiates stale grounded/no-floor, one-toe support, left edge and far-page cases; not a real route or resource ownership proof.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
