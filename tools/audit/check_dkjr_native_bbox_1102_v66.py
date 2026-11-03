"""Typed current-anchor bbox and ungranted gate finite CPU differentials."""
import collections,itertools,json,re
from pathlib import Path
import check_dkjr_native_item_status_1102_v61 as P
A,R,O,W,N=P.A,P.R,P.O,P.W,P.N


def fixture(gate=False):
    b,m,_,_=P.fixture();q=json.loads((O/'native-bbox-v65-layout.json').read_text());L=q['labels']
    m.ram[3][:0x1fe0]=[255]*0x1fe0;part=(O/'native-bbox-v65.bin').read_bytes();m.ram[3][:len(part)]=part
    for kind,at in [('pause',0x1540),('main',0x165e),('ports',0x16a7)]:
        part=(O/f'native-bbox-{kind}-v65.bin').read_bytes();m.ram[2][at:at+len(part)]=part
    if gate:
        patch=q['ungranted_shared_gate_proposal'];raw=bytearray(b['raw']);at=patch['file_offset'];old=bytes.fromhex(patch['old_hex'])
        assert raw[at:at+len(old)]==old
        raw[at:at+len(old)]=bytes.fromhex(patch['new_hex'])
        assert raw[at+37]==0x60
        b=dict(b);b['raw']=bytes(raw);m.bundle=b
    return b,m,L,q


def main():
    b,old,L,q=fixture(False);_,new,_,_=fixture(True)
    # Port predicate finite proof includes arbitrary incoming C/V/N/Z.
    GL={n:int(v,16)for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'native-bbox-gate-v65.lbl').read_text(),re.M)}
    pred=0
    for char,flags in itertools.product(range(256),[0x30,0x31,0x71,0xf1]):
        m=N.fork(new);N.put(m,SelectedCharacter=char);m.raw_page(1,193)
        c=N.NesMPU(memory=m,pc=0xadd8);c.p,c.sp=flags,224;c.stPushWord(0x5ffe)
        for _ in range(30):
            if c.pc in [GL['DkBBoxExtended'],GL['DkBBoxFallback']]:break
            c.step()
        assert(c.pc==GL['DkBBoxExtended'])==(char in [36,39,40]),(char,flags,hex(c.pc))
        pred+=1
    foreign=0
    for char,(x,y),mode,flags in itertools.product([i for i in range(256)if i!=40],[(8,32),(120,176),(240,208)],[0,1],[0x30,0xf1]):
        pair=[]
        for seed in [old,new]:
            m=N.fork(seed);N.put(m,SelectedCharacter=char,Player_Rel_XPos=x,Player_Rel_YPos=y,Player_X_Position=x,Player_Y_Position=y,Player_Y_HighPos=1,CrossoverBehaviorVersion=mode)
            out=N.invoke(m,'LmBoundingBoxGate',a=165,x=0,y=0,p=flags);pair.append((m,out))
        a,aa=pair[0];z,zz=pair[1]
        assert[aa[k]for k in['A','X','Y','P']]==[zz[k]for k in['A','X','Y','P']],('foreignAXYP',char,x,y,mode,flags)
        assert not P.differences(P.native(a),P.native(z))and a.ram==z.ram and a.rawtags==z.rawtags,('foreignstate',char,x,y,mode,flags)
        foreign+=1
    own=0;anchors=[(8,0,32),(255,135,176),(256,16,208),(700,660,144)]
    for state,direction,grip,(world,camera,y),(dx,dy)in itertools.product(range(1,5),[0,3,4],range(3),anchors,[(0,0),(37,17),(-19,-11)]):
        m=N.fork(new);N.put(m,Player_X_Position=world&255,Player_PageLoc=world>>8,Player_Y_Position=y,Player_Y_HighPos=1,ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8)
        m.ram[2][0x6b]=state;m.ram[2][0x54]=direction;m.ram[2][0x71]=grip
        for i in range(8):
            m.ram[2][0x213+4*i]=(m.ram[2][0x213+4*i]+dx)&255
            m.ram[2][0x210+4*i]=(m.ram[2][0x210+4*i]+dy)&255
        P.P.direct(m,L['DkjrBounds']);source=bytes(m.ram[2][:0x800]);shape=list(m.ram[2][0x5fc:0x600]);sx,sy=m.ram[2][0x213],m.ram[2][0x210]
        expected=[(v+((world-camera-8-sx)if i%2==0 else(y+15-sy)))&255 for i,v in enumerate(shape)]
        out=N.invoke(m,'LmBoundingBoxGate',a=165,x=0,y=0,p=0x31)
        at=W.address(b,'BoundingBox_UL_Corner')
        assert list(m[at:at+4])==expected,(state,direction,grip,world,camera,y,dx,dy,expected,list(m[at:at+4]))
        assert bytes(m.ram[2][:0x800])==source and out['X']==out['Y']==0
        own+=1
    counts=collections.Counter();base=N.NesMPU
    class Trace(base):
        def step(self):
            if self.memory.rawtags[1]==3 and self.pc==L['DkFullBox']:counts['actual_private_FullBox']+=1
            return super().step()
    N.NesMPU=Trace
    try:
        m=N.fork(new)
        for i in range(6):m[W.address(b,'Enemy_Flag')+i]=0
        P.P.direct(m,L['DkjrNativeFruitReset']);N.put(m,FrameCounter=1,SavedJoypadBits=0,SavedJoypad1Bits=0,VRAM_Buffer1_Offset=0,NmiDisable=255)
        N.invoke(m,'GameCoreRoutine',a=85,x=0,y=0,p=0x31)
        assert counts['actual_private_FullBox']==1 and N.get(m,'NumberofLives')==2
    finally:N.NesMPU=base
    out=dict(passed=True,qualified=False,source_funding_proposal_only=True,shared_grant=False,ROM_written=False,native_owner_admitted=False,
        selector_predicate_cases=pred,foreign_header_reject_native_bbox_fullstate_cases=foreign,
        own_original_D2BD_current_anchor_cases=own,actual_Main_private_FullBox_entries=counts['actual_private_FullBox'],
        body_bytes=q['body_bytes'],metadata_end=q['metadata_end'],metadata_spare=q['metadata_spare'],proposal=q['ungranted_shared_gate_proposal'],
        scope='Exact37B source-funded port reduces original38B body without expanding oldspan. All256selectors×fourflags classify exactly36/39/40; all255foreign IDs×positions×modes×flags preserve fullnativeAXYP/application/SMC/maps/private state in rejected-header fixtures.432original state/facing/grip/camera/stale-OAM shapes transport unchanged D2BD dimensions to current native pixels; actual Main now reaches16 once. Positive authenticated current Sh/Bub/Prince bodies, latestowner rebind and fullIRQ still required before any sharedgrant/nativecandidate.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),Path(P.__file__),O/'native-bbox-v65-layout.json',O/'native-bbox-v65.bin',O/'native-bbox-ports-v65.bin',O/'native-bbox-gate-v65.bin']})
    (O/'native-bbox-v66-CPU.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in['passed','selector_predicate_cases','foreign_header_reject_native_bbox_fullstate_cases','own_original_D2BD_current_anchor_cases','actual_Main_private_FullBox_entries','metadata_spare']}))


if __name__=='__main__':main()
