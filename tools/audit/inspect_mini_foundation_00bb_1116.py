"""Read-only exact-current Mini carrier/policy and compact proof inventory.

No CPU, historical image normalization, archive extraction or game outputs.
Only three named old mushroom proof members are read for versioned reference.
"""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile
import json,re
import check_ff_white_mushroom_current_1110 as W

R=W.R;ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN='00bb2664647a4ef47b5dfa01c96d50549581d215a33d19a2a6390d1e09078e21'
H=lambda b:sha256(b).hexdigest()
PACKET=R/'docs/qa/checkpoints/2026-11-03/roster-resume-v62/mini-public.zip'
PACKET_SHA='be5ee2381ce815c75833147fcfb816c3e0c000fd298b7b9aba35d8f9b3c9cf0c'
MEMBERS={
 'build/mini-mario-power-contract-1103-v51/mini-native-power-v59.json':'d0a60c71635f09ac228bf0aed00429bbebe5a2523e95b4c3cb6284dfb4e03b68',
 'build/mini-mario-power-contract-1103-v51/earned-mushroom58/controller.lua':'a3c8673a3af6c1bc4aced403d8a25de7998f087987590163b56cbe00d79e52a7',
 'build/mini-mario-power-contract-1103-v51/earned-mushroom58/capture/result.json':'54056d7f8b095b7c36428ebd45c8745e3aa41364234ec23fc1c5df2980be602e',
}


def inspect(raw):
    assert isinstance(raw,bytes)and H(raw)==PIN
    code_at=1048592+962*1024;payload=raw[code_at:code_at+7168];kernel=payload[:5120]
    cookie_at=16+65*8192+0x1003;cookie=raw[cookie_at:cookie_at+16]
    assert len(payload)==7168 and cookie==bytes((167,41,1))+sha256(payload).digest()[:13]
    roles={0:'movement',4:'shot fallback',5:'injury',15:'fresh life',16:'body bounds',23:'pickup eligibility',24:'pickup',33:'power update',34:'weapon tail',36:'scene constructor'}
    vectors=[]
    for i,role in roles.items():
        at=i*3;assert kernel[at]==0x4c;pc=int.from_bytes(kernel[at+1:at+3],'little');owned=0xa000<=pc<0xb400
        meta=0xd000<=pc<0xd400
        vectors.append(dict(service=i,role=role,public_PC=0xa000+at,target_PC=pc,target_in_five_code_pages=owned,
            target_metadata967=meta,target_hex=(kernel[pc-0xa000:pc-0xa000+28]if owned else payload[5120+pc-0xd000:5120+pc-0xd000+28]if meta else b'').hex()))
    assert H(PACKET.read_bytes())==PACKET_SHA
    refs={}
    with ZipFile(PACKET)as z:
        for name,pin in MEMBERS.items():
            data=z.read(name);assert H(data)==pin;refs[name]=data
    old=json.loads(refs[next(n for n in refs if n.endswith('v59.json'))])
    result=json.loads(refs[next(n for n in refs if n.endswith('result.json'))])
    control=refs[next(n for n in refs if n.endswith('controller.lua'))].decode()
    hooks={}
    for name in('MiniStep','MiniHostMain','MiniHostFresh','MiniHostHead','MiniHostBox'):
        marker='["'+name+'"]={'
        if marker not in control:continue
        start=control.index(marker)+len(marker)-1;depth=0;end=start
        for end in range(start,len(control)):
            depth+=(control[end]=='{')-(control[end]=='}')
            if depth==0:break
        text=control[start:end+1]
        fields={n:re.search(r'\["'+n+r'"\]=(\d+)',text)for n in('pc','physical')}
        data=re.search(r'\["bytes"\]=\{([\d,]+)\}',text)
        if all(fields.values())and data:
            pc,physical=(int(fields[n][1])for n in('pc','physical'));expected=bytes(map(int,data[1].split(',')))
            actual=kernel[pc-0xa000:pc-0xa000+len(expected)]
            hooks[name]=dict(pc=pc,old_physical=physical,expected_hex=expected.hex(),actual_current_hex=actual.hex(),exact_preimage=actual==expected)
    matches=[i for i in range(len(kernel)-11)if kernel[i:i+3]==bytes.fromhex('a5dc8d')and kernel[i+5:i+8]==bytes.fromhex('292cf0')and kernel[i+9:i+11]==bytes.fromhex('c924')];assert len(matches)==1
    manual_at=matches[0];manual=kernel[manual_at:manual_at+96]
    assert bytes.fromhex('a90148a242a014')in manual,'Actual right-starting horizontal input branch'
    b=dict(W.Symbols.bundle(),raw=raw)
    native={}
    for name in('KmNextVariant','HandlePowerUpCollision','MarioSourcePowerupCollision','GuestBeginPowerup','GuestPowerupUpdate','PlayerMovementSubs','GameLoop'):
        pc,at=W.address(b,name),W.location(b,name)
        native[name]=dict(pc=pc,file_offset=at,bank=(at-16)//8192,hex=raw[at:at+16].hex())
    frames={}
    for tag,off in dict(A=0x2e0,B=0x3e0,C=0x3a0,D=0x3c0).items():
        data=payload[5120+off:5120+off+32];points=[]
        for y in range(16):
            tile=y//8*16;row=y%8
            for x in range(8):
                if((data[tile+row]>>(7-x))&1)|(((data[tile+row+8]>>(7-x))&1)<<1):points.append((x,y))
        frames[tag]=dict(hex=data.hex(),opaque_pixels=len(points),bounds=[min(x for x,y in points),min(y for x,y in points),max(x for x,y in points),max(y for x,y in points)]if points else None)
    files=['tools/audit/replay_mini_platform_regression_1113.py','tools/playthroughs/mini_native_lifts_11_1108.lua','tools/reference/mini_mario_native_host_1103_v22.inc','tools/reference/mini_mario_fireball_1103.s','tools/reference/mini_fireball_art_1108.s','tools/reference/mini_manual_dual_platform_1110.inc','tools/audit/check_manual_wide_horizontal_1110.py']
    return dict(passed=True,ROM_SHA256=PIN,source_CPU_run=False,outputs=0,Mesen=False,
        carriers=[dict(page=962+i,file_offset=code_at+i*1024,SHA256=H(payload[i*1024:(i+1)*1024]))for i in range(7)],
        kernel_bytes=5120,kernel_SHA256=H(kernel),payload_bytes=7168,payload_SHA256=H(payload),cookie_file_offset=cookie_at,cookie_hex=cookie.hex(),
        metadata967_SHA256=H(payload[5120:6144]),atlas968_SHA256=H(payload[6144:]),vectors=vectors,
        native=native,fireball_frames_in_metadata967=frames,
        manual_dispatch=dict(pc=0xa000+manual_at,hex=manual.hex(),right_branch_present=True,full_runtime_semantics_not_retested=True),
        immutable_M_packet=dict(path=PACKET.relative_to(R).as_posix(),SHA256=PACKET_SHA,members=MEMBERS,
            versioned_result_passed=result.get('passed'),result_keys=sorted(result),old_source_labels={k:v for k,v in old.get('labels',{}).items()if k in('MiniHostPickup','MiniHostPowerup','MiniStep','MiniHostFresh','MiniHostMain')},
            retained_M_hooks_actual_preimages=hooks,
            scope='Old9d291 M control/result reference only; no old ROM/default recipe run and no current-item claim'),
        full_reference=dict(path='build/complete-roster-native-1110/packets/regression/mini/controller.lua',SHA256='d20ec6a9c7481b902a5b45033e1a2e4448df4555ba31d4e0981d1a371e920677',not_read=True,
            source_recipe='replay_mini_platform_regression_1113.py accepts at most strict12397; never called on00bb'),
        source_bindings={name:H((R/name).read_bytes())for name in files},
        scope='Exact00bb static ownership and three named immutable M proof members; no cold/menu/route/item/native preservation beyond stated bytes')


if __name__=='__main__':
    def deny(*args,**kw):raise AssertionError('Mini foundation attempted artifacts/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=inspect(ROM.read_bytes())
    q['receipt_SHA256']=H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
