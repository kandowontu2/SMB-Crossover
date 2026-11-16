"""Independent current-only shared ingress review; no proposed CPU or image."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import inspect,json,re
import current_jay_natural_stock_00bb_1116 as J

PLAN='tools/audit/plan_jay_status_publication_00bb_1116.py'
PLAN_SHA='0ae3ac71e6fa8f7e0f40fe0da13ce33af9ad79dec18367f01b0ae9698bbb0295'


def run(raw):
    assert J.H((J.R/PLAN).read_bytes())==PLAN_SHA
    q=J.bindings(raw);prg=lambda bank,pc:16+8192*bank+(pc&8191)
    hot=raw[prg(94,0xb27f):prg(94,0xb27f)+112]
    assert hot[:22].hex()=='08488a489848ad0260c910d046ad0b73691f2940f03d'
    page=lambda p:raw[1048592+p*1024:1048592+(p+1)*1024]
    packet,carrier,motion,extra=map(page,(218,222,232,234))
    assert packet[0x343:0x352].hex()=='4caab3baa201a0ff3809004c00b88d'
    assert packet[0x3ea:0x3f8].hex()=='082c0b737004284c7bb6284cd4be'
    assert carrier[0x27b:0x27e]==bytes.fromhex('4cf6a7')and carrier[0x28d:0x290]==bytes.fromhex('4c00b8')
    assert extra[0x2d4:0x2df]==bytes.fromhex('4c00c2')+b'\xea'*8
    # Derive one actual Steve cold through the already-qualified compiled
    # menu recipe. Only a second real Select and its expected name differ.
    frozen=J.Previous.Frozen;source=inspect.getsource(frozen.cold)
    edits=(('    W.UI.key(m,32)\n','    W.UI.key(m,32)\n    W.UI.key(m,32)\n'),
           ("=='JAY MCCRAY'","=='STEVE HERMANN'"),('m[0x730b]&96==32','m[0x730b]&96==64'))
    for before,after in edits:assert source.count(before)==1;source=source.replace(before,after)
    namespace=dict(frozen.__dict__,bindings=lambda image:q if image is raw else (_ for _ in()).throw(AssertionError('Unknown image')),
        primary=lambda image:J.primary(image))
    exec(compile(source,'<ordinary compiled Steve Select2 cold>','exec'),namespace);m=namespace['cold'](raw)
    assert m.bundle['raw']is raw and J.N.get(m,'SelectedCharacter')==16 and m[0x730b]&96==64
    assert bytes(m.ram[3][0x13aa:0x13b8])==packet[0x3ea:0x3f8]
    assert bytes(m.ram[3][0x1ed4:0x1edf])==extra[0x2d4:0x2df]
    def b3(pc,n):return bytes(m.ram[3][pc-0xa000:pc-0xa000+n])
    def b2(pc,n):return bytes(m.ram[2][pc-0xc000:pc-0xc000+n])
    token=b2(0xc200,447);assert token[:3]==bytes.fromhex('c0e2d0')
    other=(0xc204+int.from_bytes(token[3:4],'little',signed=True))&65535
    otherjump=b2(other,3);assert otherjump[0]==0x4c
    nativeother=int.from_bytes(otherjump[1:],'little');nativejump=b3(nativeother,3)
    assert nativejump==bytes.fromhex('4c00dc'),('Current NativeOther',hex(nativeother),nativejump.hex())
    worker=b2(0xdc00,992);assert worker[:3]==bytes.fromhex('c0e0d0')
    fallback=0xdc04+int.from_bytes(worker[3:4],'little',signed=True)
    assert b2(fallback,2)==bytes.fromhex('1860')
    mirror=bytes.fromhex('ad3e5f0aa9002a8d5b07')
    mirrors=[0xdc00+m.start()for m in re.finditer(re.escape(mirror),worker)]
    assert len(mirrors)==1
    # The unchanged whole current prefix reaches the native mirror through
    # its own three Mike calls, not by calling the proposed Jay leaf.
    prefix=worker[:mirrors[0]-0xdc00+len(mirror)]
    assert bytes.fromhex('200ea0')not in prefix # native Mike calls use existing transport
    points={(222,0xb27f):'Hot94',(3,0xb303):'PrivateMux',(3,0xb3aa):'SharedMux',
        (3,0xb67b):'ProgressStub',(3,0xb67f):'PauseMux',(3,0xb68d):'JayMoveJmp',
        (3,0xb30e):'RetiredJayJmp',(3,0xb800):'JayPrivateUpdate',(3,0xbed4):'TokenJmp',
        (2,0xc200):'SteveToken',(3,nativeother):'SteveOther',(2,0xdc00):'SteveMovement',
        (2,mirrors[0]):'SteveMirror',(224,0xa2cb):'OriginalJnMovement'}
    counts=Counter();witnesses=[];base=J.N.NesMPU
    def tag(pc):return m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
    class CPU(base):
        def step(self):
            name=points.get((tag(self.pc),self.pc))
            if name:
                counts[name]+=1;counts[name+':Y'+format(self.y,'02x')]+=1
                if len(witnesses)<16:witnesses.append(dict(name=name,PC=self.pc,SP=self.sp,tag=tag(self.pc),A=self.a,Y=self.y,P=self.p,
                    variant=m[0x730b],stars=J.N.get(m,'JnStars'),status=J.N.get(m,'PlayerStatus')))
            return super().step()
    pads=[0]*4+[1]*8+[129]*8+[0]*4+[64]*2+[0]*6
    with patch.object(J.N,'NesMPU',CPU):
        for pad in pads:m.controller_pad=pad;J.Frames.frame(m,whole_pass=True)
    assert counts['SharedMux']and counts['SteveToken']and counts['SteveMovement']and counts['SteveMirror']
    assert all(counts[name]==0 for name in('ProgressStub','PauseMux','JayMoveJmp','RetiredJayJmp','JayPrivateUpdate'))
    known={}
    for name,basepc,data in(('primary',0xa000,J.primary(raw)),('packet',0xafc0,packet),('carrier',0xb400,carrier),('motion',0xb800,motion),('extra',0xbc00,extra)):
        known[name]=[basepc+i for i in range(len(data)-2)if data[i]in(0x20,0x4c,0x6c)and data[i+1:i+3]==bytes.fromhex('00b8')]
    assert known==dict(primary=[],packet=[0xb30e],carrier=[0xb68d],motion=[],extra=[])
    out=dict(passed=True,kind='Independent actual00bb shared ingress inspection and original-only witness',parent_SHA256=J.PIN,
        frozen_plan_SHA256=PLAN_SHA,hot112_SHA256=J.H(hot),current_supported_variants={'Mike00':False,'Jay20':True,'Steve40':True,'illegal60':False},
        exact_SharedMux_hex=packet[0x3ea:0x3f8].hex(),nativeOther=dict(token_branch_PC=other,target=nativeother,hex=nativejump.hex(),entry=0xdc00,nonE0_fallback=fallback),
        current_SteveMirror_PC=mirrors[0],current_StevePrefix_hex=prefix.hex(),current_StevePrefix_SHA256=J.H(prefix),
        known_local_B800_direct_calls=known,original_only_ordinary_updates=len(pads),counts=dict(counts),witnesses=witnesses,
        terminal=dict(x=J.N.get(m,'Player_X_Position')+256*J.N.get(m,'Player_PageLoc'),y=J.N.get(m,'Player_Y_Position'),
            health=J.N.get(m,'JnHealth'),status=J.N.get(m,'PlayerStatus'),stars=J.N.get(m,'JnStars'),lives=J.N.get(m,'NumberofLives')),
        no_proposed_CPU_or_overlay=True,new_image_created=False,outputs=0,
        remaining_qualification='Exact old B830/retired-pad interior ingress census and new-code reached IRQ/busyNMI remain separate allocation/CPU obligations; this witness does not invent arbitrary private entry eligibility.',
        source_SHA256=J.H(Path(__file__).read_bytes()))
    out['receipt_SHA256']=J.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':
    raw=J.load_current_image()
    def deny(*a,**kw):raise AssertionError('Independent shared ingress review attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
