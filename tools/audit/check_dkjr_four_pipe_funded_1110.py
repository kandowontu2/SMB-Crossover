"""Build and verify the funded eight-row DK Jr. allocator in memory."""
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from unittest.mock import patch

import check_dkjr_cold_space_1110_v2 as Cold
import check_dkjr_second_pipe_lifts_1110 as Previous


R, B, N, S = Previous.R, Previous.B, Previous.N, Previous.S
SOURCE = R/'tools/reference/dkjr_four_pipe_funded_1110.s'
PARENT = Cold.V1.Gap.SECOND
PIN = 'b031802c7bc4f4e9596683e66f2f53c124b3a3ac155b80bbec03c5965b8e4e65'
NIGHTLY = Previous.NIGHTLY
COOKIE_AT = Previous.COOKIE_AT
COOKIE = bytes.fromhex('a72801590fbf90c3715698c8af6e16e3')
LEFTS = (416,480,560,624,688,752,880,944)
CENTERS = (128,128,177,177,169,169,161,161)
LAYOUT = {'BOX':(0xbd3c,9),'CAMERA_START':(0xd2fc,4),'WINDOW_MASK':(0xd7fc,4),
          'ROWS':(0xd2c4,17),'ORDINAL':(0xb6a2,3),'PIPE':(0xd18b,117),
          'REFRESH_TARGET':(0xb7b8,3),'REFRESH':(0xb624,126),'DK_COLD':(0xd25e,102)}


def patch_once(source, before, after):
    assert source.count(before)==1,before
    return source.replace(before,after)


def proposal(raw):
    """Return exact candidate bytes, typed cookie, and linked labels for a20d."""
    assert sha256(raw).hexdigest()==PARENT
    assert raw[COOKIE_AT:COOKIE_AT+16]==COOKIE
    carrier = bytearray(S.V.T.payload(raw))
    assert COOKIE==bytes.fromhex('a72801')+sha256(carrier).digest()[:13]
    source = SOURCE.read_text(encoding='utf-8')
    new = Previous.assemble(source+Cold.SOURCE.read_text(encoding='utf-8'),LAYOUT)
    assert new['used']=={'BOX':8,'CAMERA_START':3,'WINDOW_MASK':3,'ROWS':16,'ORDINAL':3,
                         'PIPE':117,'REFRESH_TARGET':3,'REFRESH':126,'DK_COLD':102}
    labels = new['symbols']
    assert (labels['DkPipeEnd'],labels['DkRefreshPlatformEnd'],labels['DkColdEnd'])==(0xd200,0xb6a2,0xd2c4)
    assert sha256(new['images']['DK_COLD']).hexdigest()=='c47ddf12e6df4f8abf189ab9c78c58ffdcd5f80c3ade8e610f51d977f45889d7'

    previous = Previous.SOURCE.read_bytes()
    assert sha256(previous).hexdigest()=='5bfc17c02fac82c37d75fa0944be7498ad71a15b7420af8ee959c5d59c5eed4c'
    refresh = source[source.index('.segment "REFRESH"'):]
    refresh = patch_once(refresh,'    bmi RefreshReturn','    jmp RefreshReturn')
    refresh = patch_once(refresh,'    jsr NativeRelative\n','    jsr NativeRelative\n    ldx ObjectOffset\n')
    dependencies = ('R0 = $03\nNativeOffscreen = $8ae9\nNativeRelative = $8aa0\n'
                    'NativeLargeBBox = $b7ca\nNativeSmallBBox = $b7d9\n'
                    'DkRefreshSave = $b7ac\nFrameSmc = $d2f7\n')
    old = Previous.assemble(previous.decode()+dependencies+refresh,
                            dict(Previous.LAYOUT,REFRESH=(0xb624,129)))
    assert old['used']['REFRESH']==129 and old['symbols']['RefreshStart']==0xb654
    cold_at = Previous.offset(0xd25e)
    old_cold = bytes(carrier[cold_at:cold_at+119])
    assert sha256(old_cold).hexdigest()==Cold.V1.PREIMAGE
    preimages = {0xb624:old['images']['REFRESH'],0xbd3c:old['images']['BOX'].ljust(9,b'\xea'),
                 0xd2fc:old['images']['CAMERA_START'].ljust(4,b'\xff'),0xd7fc:old['images']['WORLD_LEFT'],
                 0xd18b:old['images']['PIPE'],0xb7b8:b'\x4c'+old['symbols']['DkPipeTry'].to_bytes(2,'little'),
                 0xd25e:old_cold}
    images = new['images']
    patches = {0xb624:images['REFRESH']+images['ORDINAL'],0xbd3c:images['BOX'].ljust(9,b'\xea'),
               0xd2fc:images['CAMERA_START'].ljust(4,b'\xff'),0xd7fc:images['WINDOW_MASK'].ljust(4,b'\xff'),
               0xd18b:images['PIPE'],0xb7b8:images['REFRESH_TARGET'],
               0xd25e:images['DK_COLD']+images['ROWS'].ljust(17,b'\xff')}
    for pc,replacement in patches.items():
        at = Previous.offset(pc)
        assert len(replacement)==len(preimages[pc])
        assert carrier[at:at+len(replacement)]==preimages[pc],hex(pc)
        carrier[at:at+len(replacement)] = replacement

    cookie = COOKIE[:3]+sha256(carrier).digest()[:13]
    image = bytearray(raw)
    pages = []
    for i,page in enumerate(S.V.T.PAGES):
        at = S.Art.CHR+1024*page
        updated = carrier[1024*i:1024*(i+1)]
        if updated!=raw[at:at+1024]:
            pages.append(page)
            image[at:at+1024] = updated
    assert pages==[881,883,960,961],pages
    image[COOKIE_AT:COOKIE_AT+16] = cookie
    assert S.V.T.payload(image)==carrier
    atlas = json.loads(S.Art.ATLAS.read_text())
    alias = json.loads(S.OLD_ART.read_text())
    assert alias['passed'] and alias['hanging_tile_aliases']=={str(k):v for k,v in S.Art.ALIASES.items()}
    call,source_art,_ = alias['patches']
    at = call['file_offset']
    assert image[at:at+3]==raw[at:at+3]==bytes.fromhex(call['new_hex'])
    at = source_art['file_offset']
    assert image[at:at+11]==raw[at:at+11]==bytes.fromhex(source_art['new_hex'])[:11]
    for selection in atlas['all_legal_8x16_selections']:
        page = selection['physical_page']
        first,last = selection['physical_byte_half_open']
        if page==960 and selection['native_tile'] in S.Art.ALIASES:
            assert selection['role']=='hanging' and 384<=first<last<=512
            tile = S.Art.ALIASES[selection['native_tile']]
            assert S.Art.art(raw,tile)==S.Art.art(image,tile)
            continue
        at = S.Art.CHR+page*1024
        assert image[at+first:at+last]==raw[at+first:at+last]
    assert sha256(image).hexdigest()==PIN
    return bytes(image),cookie,labels


def put_slot(m,slot,**fields):
    for name,value in fields.items():
        m[N.address(m.bundle,name)+slot] = value


def fixture(seed,cam,seen,occupied=0):
    m = S.slim_fork(seed)
    m.raw_page(1,3)
    m.raw_page(2,2)
    N.put(m,CurrentBank=3,CurrentBankC=2,AreaDataLow=0xce,AreaType=1,
          ScreenLeft_X_Pos=cam&255,ScreenLeft_PageLoc=cam>>8,
          ScreenRight_X_Pos=(cam+255)&255,ScreenRight_PageLoc=(cam+255)>>8,ObjectOffset=0)
    m.ram[2][S.SEEN] = seen
    for slot in range(6):
        put_slot(m,slot,Enemy_Flag=int(slot<occupied),Enemy_ID=6)
    return m


def abi(m):
    return bytes(m[3:11]),bytes(m[0x15a:0x17b]),tuple(m.rawtags),N.get(m,'ObjectOffset')


def verify_admission(seed,labels):
    counts = Counter()
    for cam,seen in product(range(1024),range(9)):
        m = fixture(seed,cam,seen)
        row = next((i for i,left in enumerate(LEFTS) if i>=seen and 256<=left-cam<=287),None)
        c = S.direct(m,labels['DkPipeScope'])
        assert bool(c.p&1)==(row is not None),(cam,seen,row)
        assert m.ram[2][S.SEEN]==(seen if row is None else row)
        counts['camera_and_cursor'] += 1
    for row,(left,center) in enumerate(zip(LEFTS,CENTERS,strict=True)):
        for cam,slot in product((left-287,left-256),range(6)):
            m = fixture(seed,cam,row,6)
            saved = abi(m)
            S.direct(m,labels['DkRefreshPlatform'])
            assert m.ram[2][S.SEEN]==row and abi(m)==saved
            put_slot(m,slot,Enemy_Flag=0)
            c = S.direct(m,labels['DkRefreshPlatform'])
            assert (c.a,c.x,c.y,c.p&0xef)==(85,7,91,0x21) and abi(m)==saved
            assert (B.world(m,'Enemy_X_Position','Enemy_PageLoc',slot),m[0x47+slot],
                    N.get(m,'Enemy_Y_Position',slot),N.get(m,'Enemy_ID',slot),
                    N.get(m,'Enemy_Flag',slot),N.get(m,'Enemy_BoundBoxCtrl',slot),
                    N.get(m,'Enemy_State',slot))==(left,center,192,0x25,1,5,0)
            assert all((N.get(m,'Enemy_Flag',other),N.get(m,'Enemy_ID',other))==(1,6)
                       for other in range(6) if other!=slot)
            assert m.ram[2][S.SEEN]==row+1
            put_slot(m,slot,Enemy_Flag=0)
            S.direct(m,labels['DkRefreshPlatform'])
            assert N.get(m,'Enemy_Flag',slot)==0 and m.ram[2][S.SEEN]==row+1
            counts['full_pool_retry_and_birth'] += 1
    m = fixture(seed,LEFTS[4]-287,4)
    N.put(m,AreaDataLow=0)
    assert not S.direct(m,labels['DkPipeScope']).p&1 and m.ram[2][S.SEEN]==4
    m = fixture(seed,700,8)
    N.invoke(m,'HuFresh')
    assert m.ram[2][S.SEEN]==0
    return dict(counts,wrong_loaded_room=1,warm_life_reset=1)


def verify_refresh(before,after,labels):
    count = 0
    for slot,enemy,flag,dx in product(range(6),range(0x24,0x2d),(0,1,0x80),(-32,0,63,255,288)):
        results = []
        for seed in (before,after):
            cam = 1024
            m = fixture(seed,cam,0)
            x = cam+dx
            put_slot(m,slot,Enemy_Flag=flag,Enemy_ID=enemy,Enemy_X_Position=x&255,
                     Enemy_PageLoc=x>>8,Enemy_Y_Position=192,Enemy_Y_HighPos=1,
                     Enemy_BoundBoxCtrl=4 if enemy>=0x2b else 5)
            m.writes.clear()
            m.ppu_log.clear()
            c = S.direct(m,labels['DkRefreshPlatform'])
            # Branch relaxation moves JSR return addresses in the dead stack.
            # Compare every other write, including the live low-stack SMC.
            writes = [(at,value) for at,value in m.writes if not 0x17b<=at<0x200]
            results.append(((c.a,c.x,c.y,c.p,c.sp),abi(m),bytes(m[:0x100]),bytes(m[0x200:0x800]),
                            bytes(m.ram[2][:0x900]),writes,m.ppu_log))
        assert results[0]==results[1],(slot,enemy,flag,dx)
        count += 1
    return count


def cold(raw,cookie):
    # Observe the actual cold leaf return before the original constructor
    # writes the five mutable C210 address operands into the RAM3 program.
    payload = S.V.T.payload(raw)
    completed = []
    hook = S.C.I.F
    original = hook.invoke

    def observe_init(m,name,*args,**kwargs):
        if name!='InitScreen':
            return original(m,name,*args,**kwargs)
        watch = kwargs.pop('watch',None)
        exit_point = None

        def observe(c):
            nonlocal exit_point
            if watch is not None:
                watch(c)
            if c.pc==0xd25e and m.rawtags[2]==2:
                assert exit_point is None
                back = m[0x101+c.sp]+256*m[0x102+c.sp]+1
                exit_point = back&0xffff,c.sp+2
            if exit_point==(c.pc,c.sp):
                assert c.p&1
                assert bytes(m.ram[3])==payload[:0x2000]
                assert bytes(m.ram[2][0x1000:0x1800])==payload[9*1024:]
                completed.append(True)
                exit_point = None

        return original(m,name,*args,watch=observe,**kwargs)

    with patch.object(hook,'invoke',observe_init):
        seed = S.C.cold(raw,cookie)
    assert completed==[True]
    for bank in (2,3):
        assert bytes(seed.ram[bank][0x1fe0:0x1ff0])==cookie
    assert bytes(seed.ram[3][0x1ff0:])==payload[0x1ff0:0x2000]
    return seed


def main():
    raw = NIGHTLY.read_bytes()
    image,cookie,labels = proposal(raw)
    before,after = [cold(b,c) for b,c in ((raw,COOKIE),(image,cookie))]
    counts = verify_admission(after,labels)
    counts['equivalent_refresh_cases'] = verify_refresh(before,after,labels)
    counts['actual_cold_readback_and_committed_headers'] = 2
    print(json.dumps(dict(parent_SHA256=PARENT,memory_only_SHA256=sha256(image).hexdigest(),
        cookie=cookie.hex(),labels={k:hex(v) for k,v in labels.items() if k.startswith('Dk')},
        checks=counts,output_files=0),separators=(',',':')),flush=True)


if __name__=='__main__':
    main()
