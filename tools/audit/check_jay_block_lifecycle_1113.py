"""Pair cracked-rock head effects through the full native block lifecycle."""

import json

import compose_jay_head_bridge_1113 as P

B=P.B
N,W=B.Current.N,B.Current.W
BLOCKS=('Block_State','Block_RepFlag','Block_Metatile','Block_Y_Position','Block_Y_HighPos',
        'Block_Orig_YPos','Block_BBuf_Low','Block_X_Position','Block_PageLoc','BlockMetasprite')


def fixture(seed, *, tier=1, maximum=3, tile=0x54):
    """Declared on-screen terrain/ceiling fixture; never a natural-route claim."""
    m=B.Current.C.L.clone(seed)
    m.raw_page(1,3);m.raw_page(2,2)
    N.put(m,CurrentBank=3,CurrentBankC=2,JnOwnedTier=tier,JnMaxHearts=maximum,JnHealth=maximum*2,
          Player_X_Position=77,Player_PageLoc=1,Player_Y_Position=161,Player_Y_HighPos=1,
          Player_Y_Speed=253,Player_State=1,ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=221,
          ScreenRight_PageLoc=1,ScreenRight_X_Pos=220,BlockBounceTimer=0,GuestHurtTicks=0)
    ram=B.Gun.C.Jay.build()['ram']
    for logical,value in {0x0b:253,0x0e:10,0x0f:224,0x10:20,0x11:208,
                          0x12:11,0x13:16,0x19:4,0x1c:0,0x32:0}.items():
        m[ram[logical]]=value
    m[0x445]=tile
    assert not any(N.get(m,'Block_State',i) for i in (0,1))
    return m


def snapshot(m):
    return dict(tile=m[0x445],**{name:[N.get(m,name,i)for i in (0,1)]for name in BLOCKS})


def native_head(m,tile):
    # Same authenticated row/column consumed by the ordinary native caller.
    B.direct(m,W.address(m.bundle,'GetBlockBufferAddr'),a=21)
    N.put(m,R2=112,R3=tile)
    assert m[N.get(m,'R6')+256*N.get(m,'R7')+112]==tile
    B.direct(m,W.address(m.bundle,'PlayerHeadCollision'),a=tile,x=0,y=1)


def finish_pair(bridge,oracle,expected):
    rows=[snapshot(bridge)]
    assert rows[0]==snapshot(oracle)
    stable=0
    for tick in range(120):
        for m in (bridge,oracle):
            m.controller_pad=0
            B.Current.Frames.frame(m)
            assert N.get(m,'NumberofLives')==2
        actual=snapshot(bridge)
        assert actual==snapshot(oracle),(tick,actual,snapshot(oracle))
        rows.append(actual)
        done=actual['tile']==expected and not any(actual['Block_State']+actual['Block_RepFlag'])
        stable=stable+1 if done else 0
        if stable>=8:
            return dict(updates=tick+1,immediate=rows[0],terminal=actual,retained_updates=stable,
                        full_native_Main=True,exact_native_oracle=True)
    raise AssertionError(('Native block lifecycle bound',expected,rows[-3:]))


def check(image,info):
    _,seed=P.cold(image,P.NEW_COOKIE,P.CANDIDATE_PIN)
    original=B.Gun.C.Jay.build()
    cancel=info['fields']['cancel']-0xa000
    old=original['images']['PRIVATE'][cancel:cancel+6]
    cases=[]
    for tile in (0x54,0x61):
        for tier,maximum in ((1,3),(1,4),(2,4),(3,4)):
            bridge=fixture(seed,tier=tier,maximum=maximum,tile=tile)
            oracle=B.Current.C.L.clone(bridge)
            oracle.ram[3][cancel:cancel+6]=old
            B.direct(bridge,original['symbols']['QueryVertical'],x=0,y=0)
            B.direct(oracle,original['symbols']['QueryVertical'],x=0,y=0)
            attributes=bridge[W.address(bridge.bundle,'MTileAttribute')+tile]
            assert (attributes&7)==(1 if tile==0x54 else 5)
            if tile==0x54:
                native_head(oracle,tile)
                assert N.get(bridge,'Block_State',0)==0x12
                expected=0
            else:
                assert not any(N.get(bridge,'Block_State',i)for i in (0,1))
                expected=tile
            result=finish_pair(bridge,oracle,expected)
            cases.append(dict(tile=tile,tier=tier,maximum=maximum,attributes=attributes,
                              result=result))
    references=[]
    for size,expected in ((1,0x54),(0,0)):
        first=fixture(seed)
        # Native Mario's actual head adder is18px small,4px big. Choose
        # a real upward contact in row9 with low nibble4 in either case.
        N.put(first,SelectedCharacter=0,PlayerSize=size,PlayerStatus=1-size,
              Player_Y_Position=130 if size else 144)
        native_head(first,0x54)
        other=B.Current.C.L.clone(first)
        result=finish_pair(first,other,expected)
        references.append(dict(native_Mario_size=size,result=result))
    return dict(ROM_SHA256=P.CANDIDATE_PIN,terrain_fixture=True,natural_rock_placement=False,
        cases=cases,native_small_and_big_references=references,output_files=0,
        policy='Jay raw16 uses the existing Mike-family large native head at every tested Jn tier; cracked rock54 shatters, hard ground61 is excluded. Native small Mario bumps/restores54.')


if __name__=='__main__':
    installed=B.Current.ROM.read_bytes()
    image,info=P.proposal(P.inverse(installed)if P.digest(installed)==P.CANDIDATE_PIN else installed)
    print(json.dumps(check(image,info)),flush=True)
