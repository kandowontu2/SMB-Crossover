"""Assemble and verify DK Jr.'s second-pipe stock girders on the current ROM."""
import argparse
from collections import Counter, deque
from dataclasses import dataclass
import json
from pathlib import Path
import sys

import check_dkjr_first_pipe_runtime_1110 as First
from check_remaining_roster_starts_1110 import W
from check_tmnt_render_oa import location
from nightly_patch_guard_v1 import check

B, N, S = First.D.B, First.D.N, First.S
R = S.R
sys.path.insert(0, str(R/'tools/reference'))
from sonic_sms_compact_cold_worker_1110 import assemble

NIGHTLY = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PARENT = '9897c2b85489024be25b4b296d0ea57975a579ba1e3ff37a71f7ac3e0b195b97'
SOURCE = R/'tools/reference/dkjr_second_pipe_lifts_1110.s'
CANDIDATE = R/'build/dkjr-second-pipe-native-1110/candidate.nes'
COOKIE_AT = 534485
OLD_COOKIE = bytes.fromhex('a72801d68084002c87dda880bef61afb')
LAYOUT = {'BOX':(0xbd3c,9),'CAMERA_START':(0xd2fc,4),
          'WORLD_LEFT':(0xd7fc,4),'PIPE':(0xd18b,117)}
LEFTS = (416,480,560,624)
PIPES = ((448,176),(608,160))


def offset(pc):
    return pc-0xa000 if pc<0xc000 else 9*1024+pc-0xd000


def area_tables(raw):
    b = W.bundle(raw)
    pointer = location(b,'AreaDataAddrLow')
    lows = raw[pointer:pointer+34]
    assert lows.count(0xcc) == 1 and lows[8] == 0xcc
    stage_table = location(b,'AreaAddrOffsets')
    stages = raw[stage_table:stage_table+36]
    assert stages[0]==0x25 and all((v&0x7f)!=0x25 for v in stages[1:])
    m = N.fresh(b)
    N.put(m,AreaPointer=37,WorldNumber=0,LevelNumber=0,Hidden1UpFlag=1,SelectedCharacter=40)
    N.invoke(m,'GetAreaDataAddrs')
    assert N.get(m,'AreaDataLow') == 0xce and N.get(m,'AreaAddrsLOffset') == 5
    lengths = N.address(b,'AreaObjectLength')
    m[lengths:lengths+3] = bytes([255])*3
    tile = N.address(b,'MetatileBuffer')
    caps = []
    for col in range(42):
        N.invoke(m,'AreaParserCore')
        assert N.get(m,'AreaDataLow') == 0xce
        caps += [(16*col,16*(row+2)) for row,code in enumerate(m[tile:tile+13])
                 if code in (0x10,0x12)]
        N.invoke(m,'IncrementColumnPos')
    assert tuple(caps) == PIPES


def proposal(raw):
    assert S.sha(raw) == PARENT
    carrier = bytearray(S.V.T.payload(raw))
    assert raw[COOKIE_AT:COOKIE_AT+16] == OLD_COOKIE
    assert OLD_COOKIE == b'\xa7\x28\x01'+bytes.fromhex(S.sha(carrier))[:13]
    first = S.V.M.read(First.PROOF)
    assert first['passed'] and first['cookie'] == OLD_COOKIE.hex()
    for row in first['patches']:
        at = row['file_offset']
        data = bytes.fromhex(row['new_hex'])
        assert raw[at:at+len(data)] == data
    area_tables(raw)
    linked = assemble(SOURCE.read_text(encoding='utf-8'),LAYOUT)
    labels = linked['symbols']
    assert labels['DkPipeScope']==0xd18b and labels['DkPipeEnd']==0xd200

    def replace(pc,old,new):
        at = offset(pc)
        assert carrier[at:at+len(old)]==old and len(new)==len(old),(hex(pc),old.hex())
        carrier[at:at+len(new)] = new

    # Both BodyDraw exits return before this padding. DkConstruct still starts
    # at BD45. D2FC is past the last FrameSmc index, and D7FC is metadata EOF.
    assert carrier[offset(0xbd3c)-8:offset(0xbd3c)] == bytes.fromhex('68a868aa68281860')
    assert carrier[offset(0xbd45):offset(0xbd45)+5] == bytes.fromhex('a9018d4ac0')
    assert carrier[offset(0xd2f7):offset(0xd2fc)] == bytes.fromhex('626a6c6d79')
    assert carrier[offset(0xd7f6):offset(0xd7fc)] == bytes.fromhex('20c4bd4c45bd')
    for name,pad in (('BOX',0xea),('CAMERA_START',0xff),('WORLD_LEFT',0xff)):
        at,size=LAYOUT[name]
        replace(at,bytes([pad])*size,linked['images'][name].ljust(size,bytes([pad])))
    original_pipe = bytes.fromhex(
        'ad530749010d64070d61070d1d07d01aad5407c905d013ad1f0738e981a829bfc9'
        '20b006ccfdc890016018609009a205b510f006ca10f94c54b6860dad1f07294009a0'
        '9576a9019510955d95a5a9259517a9c095bea94f8d6c01a9a78d6d01a982205a01'
        'a60da9059d4606b576297f8dfdc84c54b6')
    replace(0xd18b,original_pipe,linked['images']['PIPE'])
    replace(0xb7b8,bytes.fromhex('4cb7d1'),b'\x4c'+labels['DkPipeTry'].to_bytes(2,'little'))
    cookie = OLD_COOKIE[:3]+bytes.fromhex(S.sha(carrier))[:13]
    image = bytearray(raw)
    for i,page in enumerate(S.V.T.PAGES):
        at = S.Art.CHR+1024*page
        image[at:at+1024] = carrier[i*1024:(i+1)*1024]
    image[COOKIE_AT:COOKIE_AT+16] = cookie
    assert S.V.T.payload(image)==carrier
    return bytes(image),cookie,labels


def verify_admission(raw,cookie,labels):
    seed=S.C.cold(raw,cookie)
    result=Counter()

    def fixture(cam, seen, occupied=0):
        m=S.slim_fork(seed)
        m.raw_page(1,3)
        m.raw_page(2,2)
        N.put(m,CurrentBank=3,CurrentBankC=2,AreaDataLow=0xce,WorldNumber=0,LevelNumber=0,
              ScreenLeft_X_Pos=cam&255,ScreenLeft_PageLoc=cam>>8,ObjectOffset=0)
        m.ram[2][0x8fd]=seen
        for i in range(6):
            m[N.address(m.bundle,'Enemy_Flag')+i]=int(i<occupied)
            m[N.address(m.bundle,'Enemy_ID')+i]=6
        return m

    for cam in range(768):
        for seen in range(5):
            m=fixture(cam,seen)
            c=S.direct(m,labels['DkPipeScope'])
            rows=[i for i,left in enumerate(LEFTS) if i>=seen and 256<=left-cam<=287]
            assert bool(c.p&1)==bool(rows),(cam,seen,rows)
            assert m.ram[2][0x8fd]==(rows[0] if rows else seen)
            result['camera_and_cursor_pairs']+=1
    for i,left in enumerate(LEFTS):
        for cam in (left-287,left-256):
            for slot in range(6):
                m=fixture(cam,i,6)
                S.direct(m,0xb624)
                assert m.ram[2][0x8fd]==i
                flag=N.address(m.bundle,'Enemy_Flag')+slot
                m[flag]=0
                expected_regs=(bytes(m[3:11]),bytes(m[0x15a:0x17b]),tuple(m.rawtags))
                S.direct(m,0xb624)
                assert (bytes(m[3:11]),bytes(m[0x15a:0x17b]),tuple(m.rawtags))==expected_regs
                assert m.ram[2][0x8fd]==i+1 and m[flag]==1
                assert (B.world(m,'Enemy_X_Position','Enemy_PageLoc',slot),
                        N.get(m,'Enemy_Y_Position',slot),N.get(m,'Enemy_ID',slot),
                        N.get(m,'Enemy_BoundBoxCtrl',slot),N.get(m,'Enemy_State',slot))==(left,192,0x25,5,0)
                assert m[0x47+slot]==(128 if i<2 else 177)
                m[flag]=0
                S.direct(m,0xb624)
                assert m[flag]==0 and m.ram[2][0x8fd]==i+1
                result['full_pool_retry_and_single_birth']+=1
    for value in (0,0xcc,0xcf):
        m=fixture(129,0)
        N.put(m,AreaDataLow=value)
        c=S.direct(m,labels['DkPipeScope'])
        assert not c.p&1 and m.ram[2][0x8fd]==0
        result['outside_loaded_1_1']+=1
    m=fixture(384,4)
    N.invoke(m,'HuFresh')
    assert m.ram[2][0x8fd]==0
    result['warm_life_reset']=1
    return dict(result)


@dataclass
class Girder:
    left: int
    slot: int | None = None
    birth: dict | None = None
    earlier_top: int | None = None

    def top(self,m):
        i=self.slot
        if (i is not None and N.get(m,'Enemy_Flag',i)==1 and N.get(m,'Enemy_ID',i)==0x25
                and B.world(m,'Enemy_X_Position','Enemy_PageLoc',i)==self.left):
            return N.get(m,'Enemy_Y_Position',i)
        return None


def route(raw,cookie,labels,*,second=True):
    m = B.launch(raw)
    girders = {x:Girder(x) for x in LEFTS}
    idle = N.address(m.bundle,'IdleLoop')
    assert bytes(m[idle+9:idle+12]) == b'\x20'+N.address(m.bundle,'GameLoop').to_bytes(2,'little')
    trace, phases, crossings, carries = deque(maxlen=28),[],[],Counter()
    phase, pipe, hold, rearm = 'approach',0,0,0
    active_epoch = None
    N.put(m,NmiDisable=0)

    def change(name, *extra):
        nonlocal phase
        phase = name
        phases.append([pipe+1,name,epoch,B.player(m),N.get(m,'Player_Y_Position'),*extra])

    def observe(c):
        pc=c.pc
        if pc==labels['DkPipeCreated'] and B.V.Q.tags(c)==3:
            left = B.world(m,'Enemy_X_Position','Enemy_PageLoc',c.x)
            g = girders[left]
            assert g.birth is None
            g.slot = c.x
            cam = B.camera(m)
            assert 256 <= left-cam <= 287 and g.top(m)==192
            assert N.get(m,'Enemy_BoundBoxCtrl',c.x)==5 and N.get(m,'Enemy_State',c.x)==0
            center=128 if left<512 else 177
            assert m[0x47+c.x]==center
            g.birth = dict(left=left,center=left+16,top=192,motion_center=center,camera=cam,slot=c.x,epoch=epoch)
        if pc==0xac29 and B.V.Q.tags(c)==199:
            for g in girders.values():
                top = g.top(m)
                if c.x==g.slot and top is not None:
                    y = N.get(m,'Player_Y_Position')
                    if (top-32==y and m.ram[2][0x210]==y+15 and m.ram[2][0x6b]==1):
                        carries[g.left] += 1

    for epoch in range(4300):
        keys=0
        x,y=B.player(m),N.get(m,'Player_Y_Position')
        source=m.ram[2][0x6b]
        mode,task,engine,lives=(N.get(m,n) for n in ('OperMode','OperMode_Task','GameEngineSubroutine','NumberofLives'))
        ready=(mode,task,engine,m.ram[2][0x8fe])==(1,3,8,2)
        if active_epoch is not None and (lives!=2 or source==5 or engine==11):
            break
        if ready:
            assert (N.get(m,'WorldNumber'),N.get(m,'LevelNumber'),N.get(m,'AreaAddrsLOffset'))==(0,0,5)
            assert N.get(m,'AreaDataLow')==0xce and N.get(m,'CrossoverBehaviorVersion')==0
            if active_epoch is None:
                active_epoch=epoch
                assert bytes(m.ram[2][0x1fe0:0x1ff0])==bytes(m.ram[3][0x1fe0:0x1ff0])==cookie
            pipe_x,cap=PIPES[pipe]
            up,down=(girders[left] for left in LEFTS[2*pipe:2*pipe+2])
            top,lower=up.top(m),down.top(m)
            grounded=source==1 and N.get(m,'Player_State')==0
            if phase=='approach':
                keys=1
                near=any(N.get(m,'Enemy_Flag',i)==1 and N.get(m,'Enemy_ID',i) in (2,6)
                         and not N.get(m,'Enemy_State',i)&32
                         and 8<=B.world(m,'Enemy_X_Position','Enemy_PageLoc',i)-x<=30
                         for i in range(6))
                if grounded and near and epoch>=rearm and x<up.left-24:
                    hold,rearm=epoch+8,epoch+47
                    phases.append([pipe+1,'enemy-hop',epoch,x,y])
                if x>=up.left+10:
                    keys=0
                    change('board')
            if phase=='board' and top is not None:
                if grounded and top-32==y and y<176:
                    change('rise',top)
                elif grounded and epoch>=rearm and 192<=top<=208:
                    hold,rearm=epoch+8,epoch+47
                    phases.append([pipe+1,'board-hop',epoch,x,y,top])
            if phase=='rise' and top is not None:
                edge=up.left+(29 if pipe else 23)
                keys=int(x<edge)
                if x>=edge and grounded and top-32==y and cap-6<=top<=cap:
                    hold=epoch+8
                    change('cross',top)
            if phase=='cross':
                keys=1
                if x>=pipe_x+4 and grounded and y==cap-32:
                    change('roof')
            if phase=='roof' and carries[down.left] and grounded and lower is not None and lower-32==y:
                change('lower',lower)
            if phase=='roof':
                keys=int(x<down.left-2)
                if (x>=down.left-2 and grounded and lower is not None and down.earlier_top is not None
                        and cap+8<=lower<=cap+17 and lower<=down.earlier_top):
                    change('step-down',lower,down.earlier_top)
            if phase=='step-down':
                keys=int(x<down.left+8)
                if carries[down.left] and lower is not None and grounded and lower-32==y:
                    change('lower',lower)
            if phase=='lower' and lower is not None:
                keys=int(x<down.left+31)
                if (x>=down.left+31 and grounded and lower-32==y and 192<=lower<=208
                        and down.earlier_top is not None and lower>=down.earlier_top):
                    change('depart',lower)
            if phase=='depart':
                keys=1
                if x>=down.left+36 and grounded and y==176:
                    crossings.append(dict(pipe=pipe+1,x=x,y=y,lives=lives,epoch=epoch))
                    if not second or pipe==1:
                        break
                    pipe+=1
                    change('approach')
            if epoch<hold:
                keys|=128
            trace.append([epoch,x,y,B.camera(m),source,keys,phase,top,lower])
            down.earlier_top=lower
        m.controller_pad=keys
        N.consume(m)
        c=N.NesMPU(memory=m,pc=idle)
        c.sp,c.p=255,0x31
        c.stPushWord(0xe33b)
        if ready:
            B.run(c,lambda p:(p.pc,p.sp)==(idle+12,252),observe)
        else:
            for _ in range(200000):
                if (c.pc,c.sp)==(idle+12,252):
                    break
                observe(c)
                assert m[c.pc],('Cold opcode',epoch,hex(c.pc))
                c.step()
            else:
                raise AssertionError(('Cold execution bound',epoch,hex(c.pc),c.sp))
        B.C.I.C.clear(m)
    receipt=dict(passed=len(crossings)==(2 if second else 1),
                 crossings=crossings,births=[g.birth for g in girders.values()],
                 carries=dict(carries),phases=phases,epochs=epoch+1,
                 terminal=dict(x=B.player(m),y=N.get(m,'Player_Y_Position'),source=m.ram[2][0x6b],
                               lives=N.get(m,'NumberofLives'),engine=N.get(m,'GameEngineSubroutine')),
                 trace_tail=list(trace))
    print(json.dumps(receipt,sort_keys=True),flush=True)
    assert receipt['passed'] and all(carries[x]>0 for x in (LEFTS if second else LEFTS[:2]))
    return receipt


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--admission-only',action='store_true')
    args=parser.parse_args()
    guard=check(NIGHTLY)
    raw=NIGHTLY.read_bytes()
    assert S.sha(raw)==guard['ROM_sha256']
    if guard['ROM_sha256']!=PARENT:
        # Keep the old input reproducible after replacing the nightly.
        from deliver_smb2_menu_tier_1110 import Recipe
        raw=Recipe.proposal(Recipe.V1.BASE.read_bytes())[0]
    image,cookie,labels=proposal(raw)
    print(json.dumps(dict(admission=verify_admission(image,cookie,labels)),sort_keys=True),flush=True)
    if not args.admission_only:
        route(image,cookie,labels)
    if args.output:
        assert args.output.resolve()==CANDIDATE.parent and not CANDIDATE.parent.exists()
        CANDIDATE.parent.mkdir()
        CANDIDATE.write_bytes(image)
        assert CANDIDATE.read_bytes()==image
    print(json.dumps(dict(passed=True,ROM_SHA256=S.sha(image),cookie=cookie.hex(),
        labels={k:v for k,v in labels.items() if k.startswith('Dk')},route_run=not args.admission_only,
        output_files=int(bool(args.output)))),
        flush=True)


if __name__=='__main__':
    main()
