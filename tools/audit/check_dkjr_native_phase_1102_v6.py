"""Execute original CD91 dispatcher versus the private native phase.

Only explicitly native-owned stage services are intercepted: stage enemy AI,
old goal/pause/demo/UI and the old body-enemy dispatcher. Original fruit leaves,
packet bounds, clock, movement and source effects execute on both sides.
"""
import collections,hashlib,itertools,json,re
from pathlib import Path
import prepare_dkjr_native_phase_1102_v6 as P
R=P.R;O=P.O;D=P.D;W=P.W


def main():
    layout=json.loads((O/'native-phase-v6-layout.json').read_text());blob=(O/'native-phase-v6.bin').read_bytes();assert W.P.sha(blob)==layout['code_SHA256'];L=layout['labels']
    original=D.Bus();raw=bytearray(D.donor());counts=collections.Counter();imports=collections.Counter();minimum_sp=255;digest=hashlib.sha256()
    # An isolated, identical source-format arena replaces only the donor's
    # stage1 geometry table DATA. All original executable instructions remain.
    for pc,ptr in [(0xc440,0x600),(0xc448,0x640),(0xc450,0x680)]:
        for stage in range(4):
            pos=16+(pc-0xc000)+stage*2;raw[pos:pos+2]=ptr.to_bytes(2,'little')
    floor=bytes(v for x in range(0,192,16)for v in [x,208,x+15,223])+bytes([255])
    arena={0x600:floor,0x640:bytes([80,32,80,208,96,32,96,208,255]),0x680:bytes([255])}
    active,_=D.active();seed=bytearray(active.memory[:2048])
    class Flat(list):pass
    data_addresses={v:(L['DkjrSourceData']+v-0xc2cd if v<0xc3cd else L['DData_%04x'%v])for v in range(0xc2cd,0xc3cf)}
    reverse_data={v:k for k,v in data_addresses.items()}
    def translate(r,to_private):
        r=bytearray(r)
        for p in [2,0x91]:
            v=r[p]+256*r[p+1]
            if to_private and v in data_addresses:v=data_addresses[v]
            elif not to_private:
                if v in reverse_data:v=reverse_data[v]
            r[p:p+2]=v.to_bytes(2,'little')
        return r
    def fresh(r=None):
        q=D.Bus(bytes(raw));q[:2048]=r or seed
        for pc,data in arena.items():q[pc:pc+len(data)]=data
        m=Flat([0]*65536);m[0xa000:0xa000+len(blob)]=blob;m[0xc000:0xc800]=translate(q[:2048],True)
        for a,b in [(0x600,0xc800),(0x640,0xc840),(0x680,0xc880)]:m[b:b+len(arena[a])]=arena[a]
        run(m,'DkjrUseNativeGeometry')
        return q,m
    def run(m,entry,regs=(0x57,7,9,0xf1)):
        nonlocal minimum_sp
        c=D.T.NesMPU(memory=m,pc=L[entry]if isinstance(entry,str)else entry);c.a,c.x,c.y,c.p=regs;c.sp=224;c.stPushWord(0x5ffe)
        for _ in range(80000):
            if c.pc==0x5fff:break
            minimum_sp=min(minimum_sp,c.sp);assert m[c.pc]!=0,('private BRK',entry,hex(c.pc));c.step()
        else:raise AssertionError(('private bound',entry,hex(c.pc)))
        assert c.sp==224
        return c,(c.a,c.x,c.y,c.p,c.sp)
    def original_run(q,entry,regs=(0x57,7,9,0xf1),phase=False):
        c=D.T.NesMPU(memory=q,pc=entry);c.a,c.x,c.y,c.p=regs;c.sp=224;c.stPushWord(0x5ffe)
        for _ in range(80000):
            if c.pc==0x5fff:break
            if phase:
                if c.pc in [0xcdfd,0xced4,0xcf9d,0xcf62]:
                    imports['native_owned_%04x'%c.pc]+=1;c.pc=(c.stPopWord()+1)&65535;continue
                if c.pc in [0xd2fc,0xcef4]:
                    imports['original_%04x_to_original_fruit_leaf'%c.pc]+=1
                    c.pc=0xd43a if c.pc==0xd2fc else 0xdbb3
            assert q[c.pc]!=0,('original BRK',entry,hex(c.pc));c.step()
        else:raise AssertionError(('original bound',hex(entry),hex(c.pc)))
        assert c.sp==224
        return c,(c.a,c.x,c.y,c.p,c.sp)
    def compare(q,m,cohort,regs=(0x57,7,9,0xf1),entry=0xcd91,private='DkjrNativeSourcePhase',phase=True):
        d,z=original_run(q,entry,regs,phase);c,got=run(m,private,regs)
        a=translate(m[0xc000:0xc800],False)
        # Original fixture geometry storage is an oracle input; the private
        # producer context is C800, outside the original actor's2KB image.
        indices=list(range(256))+list(range(0x200,0x600))+list(range(0x700,0x800))
        if private=='DkjrNativePhase' and q[0x0f]==0 and a[0x0f]==0:
            # A miss leaves the last scanned rectangle in42..45. A complete
            # oracle floor and the bounded native local window have different
            # last nonintersecting cells; these are not a published hit box.
            indices=[i for i in indices if not 0x42<=i<0x46]
            if q[0x6b]!=2 and q[0x71]==0 and a[0x71]==0:
                # E8D2/E8D4 cache that same nonhit rectangle as grip anchors
                # even on a failed vine probe. Actual grip admission rewrites
                # both anchors before DA48 uses them; active grips stay exact.
                indices=[i for i in indices if i not in [0x73,0x74]]
        diff=[(i,q[i],a[i])for i in indices if q[i]!=a[i]]
        assert not diff,(cohort,hex(entry),diff[:12])
        if not phase:assert z[:3]==got[:3]and z[3]&0xef==got[3]&0xef,('helper AXYP',hex(entry),z,got)
        counts[cohort]+=1;digest.update(bytes(a[:256])+bytes(a[0x200:0x600]));return c
    # New imports include the original packet overflow's nonlocal stack return.
    for entry in [0xed44,0xed7b,0xec3b,0xefce,0xf1c5,0xecb7]:
        for offset,flags,x,y in itertools.product([0,2,56,60,62],[0x20,0xf1],[0,3,4,5,6],[0,3]):
            r=bytearray(seed);r[0x4a]=1;r[0x4e]=0;r[0x49]=0;r[0x330]=offset;r[0x301]=0;r[0x300]=0;r[0x302:0x330]=bytes(46)
            r[0x95:0x9a]=bytes([0x22,0x24,0x24,0x5c,0x5d]);r[0:4]=bytes([0x40,0x21,0x95,0]);r[0x9e]=1;r[0x9f]=1;r[0x5c7]=0
            q,m=fresh(r);compare(q,m,'original_source_import_leaves',(0x57,x,y,flags),entry,'D_%04x'%entry,False)
    # Source phase uses a real donor body; only its initial pose is positioned
    # by the genuine source renderer at a controlled legal arena location.
    def actor(x=40,y=191,state=1):
        q=D.Bus(bytes(raw));q[:2048]=seed;q[0]=x;q[1]=y;q[2]=0x18
        c=D.T.NesMPU(memory=q,pc=0);D.T.run(c,0xe9ee,0,0,0,0x20)
        q[0x6b]=q[0x6c]=state;q[0x4a]=1;q[0x4e]=0;q[0x6d]=1;q[0x54]=q[0x55]=4
        q[0x68]=0;q[0x8c]=0;q[0xa0]=q[0xb0]=1;q[0x2c0]=q[0x2e0]=255;q[0x330]=0;q[0x301]=q[0x300]=0;q[0x302:0x330]=bytes(46)
        q[0x9a:0x9e]=bytes(4);return bytearray(q[:2048])
    cases=[('idle',actor(),[0]*60),('directional_jump',actor(),[0x81]+[2]*55+[0]*20),
           ('right_walk',actor(),[1]*90),('vine_up',actor(65,191),[1]*20+[8]*100),
           ('vine_down',actor(65,120,2),[4]*50+[1]*40),('death',actor(40,191,5),[1]*180)]
    phase_rows=[]
    for name,r,controls in cases:
        q,m=fresh(r);starts=[];clocks=[];ys=[];directions=[]
        if name=='directional_jump':q[0x640]=m[0xc840]=255
        for epoch,pad in enumerate(controls):
            original_run(q,0xf23e,(pad,0,9,0x20));run(m,'DkjrNormalizePad',(pad,0,9,0x20))
            previous=q[0x6b];compare(q,m,'phase_'+name);ys.append(q[0x210]);directions.append(q[0x54]);clocks.append(q[0x38])
            if previous!=3 and q[0x6b]==3:starts.append(epoch+1)
        if name=='directional_jump':assert min(ys)==176 and directions[0]==4 and directions[1:44]==[4]*43,(min(ys),directions[:48])
        if name=='death':assert len(set(clocks))==1
        phase_rows.append(dict(case=name,epochs=len(controls),minimum_source_y=min(ys),source_jump_starts=starts,final_source_state=q[0x6b]))
    # A source-format hanging fruit is touched by the original body, falls and
    # strikes an original source-format enemy proxy. No seeded hit/freeze state.
    fruit_rows=[]
    for family in [1,2]:
        r=actor(40,191);r[0x91:0x93]=(0x500).to_bytes(2,'little');r[0x93]=7;r[0x500:0x508]=bytes([7,60,191,0xa4,0x24,0x24,0x24,0x24]);r[0x9a]=1;r[0x8d]=2
        r[0x4a]=1 if family==1 else 2;r[0xb0]=1;r[0x2c0]=200;r[0x2c3]=54;r[0xa3]=0;r[0x240]=190;r[0x243]=54
        q,m=fresh(r);release=hit=finished=None;frozen_clock=None;score_codes=[]
        for epoch in range(100):
            original_run(q,0xf23e,(0,0,9,0x20));run(m,'DkjrNormalizePad',(0,0,9,0x20));before_hit=q[0x68]
            compare(q,m,'earned_source_fruit_family%d'%family)
            if release is None and q[0x8c]:release=epoch+1
            if hit is None and q[0x68]:hit=epoch+1;frozen_clock=q[0x38]
            if before_hit and q[0x68]:assert q[0x38]==frozen_clock
            if before_hit and not q[0x68]:assert q[0x38]==0x40
            if hit and not q[0x68]:finished=epoch+1;break
        assert release and hit and finished and q[0x9a]==0,(family,release,hit,finished)
        for at in range(0,q[0x301],2):
            if q[0x302+at]&0xf0==0x10:score_codes.append(q[0x303+at])
        assert score_codes==[4,8],(family,score_codes)
        fruit_rows.append(dict(family=family,touch_epoch=release,fruit_collision_epoch=hit,hit_animation_terminal_epoch=finished,source_score_BCD_hundreds=score_codes,clock_frozen=True))
    # Actual native gate and normalized input execute on a legal empty native
    # floor. The inherited native-platform/coordinate tests already cover its
    # outcalls; this fixture has no active enemy and makes no new owner claim.
    native=layout['native_bindings'];guards=0
    for engine,timer,profile,state in itertools.product([0,6,8,11],[0,1],[1,2],[0,1,3,4,5,6]):
        q,m=fresh(actor());m[native['GameEngineSubroutine']]=engine;m[native['TimerControl']]=timer;m[0xc04a]=profile;m[0xc06b]=state
        before=bytes(m[0xc000:0xc900]);accepted=engine==8 and timer==0 and profile==1 and 1<=state<=5
        if accepted:continue
        _,z=run(m,'DkjrNativePhase');assert not z[3]&1 and before==bytes(m[0xc000:0xc900]);guards+=1
    native_phase_rows=[]
    prior_layout=json.loads((O/'native-link-v5-layout.json').read_text());native_raw=W.CURRENT.read_bytes()
    pos=prior_layout['native_MTileAttribute_file_offset'];attributes=native_raw[pos:pos+256]
    assert W.P.sha(attributes)==prior_layout['native_MTileAttribute_SHA256']
    for camera in [0,255,511]:
        q,m=fresh(actor());q[0x640]=m[0xc840]=255
        # The independent oracle gets whole metatile cells at this camera
        # phase, not a broad floor whose irrelevant hit rectangle differs.
        cells=[]
        for left in range(-(camera&15),192,16):cells.extend([max(0,left),208,left+15,223])
        q[0x600:0x600+len(cells)+1]=bytes(cells+[255])
        m[native['GameEngineSubroutine']]=8;m[native['TimerControl']]=0
        m[native['ScreenLeft_X_Pos']]=camera&255;m[native['ScreenLeft_PageLoc']]=camera>>8;m[0xc8da]=1
        m[native['MTileAttribute']:native['MTileAttribute']+256]=attributes
        for block in ['Block_Buffer_1','Block_Buffer_2']:
            for row in [11,12]:m[native[block]+row*16:native[block]+row*16+16]=[0x54]*16
        for epoch,pad in enumerate([0]*20+[0x81]+[2]*55+[0]*20+[1]*40):
            original_run(q,0xf23e,(pad,0,9,0x20));m[native['SavedJoypadBits']]=pad
            compare(q,m,'actual_native_phase_BlockBuffer',private='DkjrNativePhase')
            expected=(camera+q[0x213]+8)&65535
            assert m[native['Player_X_Position']]+256*m[native['Player_PageLoc']]==expected
            assert m[native['Player_Y_Position']]==q[0x210]-15 and m[native['Player_Y_HighPos']]==1
        native_phase_rows.append(dict(camera=camera,epochs=epoch+1,final_native_x=expected,final_native_y=m[native['Player_Y_Position']],original_body_state_exact=True))
    prior=(O/'native-link-v5.bin').read_bytes();changed=[i for i in range(len(prior))if prior[i]!=blob[i]];allowed=[]
    for pc in [0xecb7,0xed44,0xed7b,0xefce,0xf1c5]:allowed.extend([L['DImport_%04x'%pc]-0xa000+1,L['DImport_%04x'%pc]-0xa000+2])
    assert set(changed)<=set(allowed)
    result=dict(passed=True,native_emulator=False,ROM_written=False,native_owner_admitted=False,component_bytes=len(blob),header_reserved_spare=8160-len(blob),component_SHA256=W.P.sha(blob),
        checks=dict(counts),phase_trajectories=phase_rows,earned_source_fruit=fruit_rows,actual_native_phase_trajectories=native_phase_rows,rejected_native_phase_guards=guards,original_native_owned_seams=dict(imports),
        source_state_digest=digest.hexdigest(),minimum_CPU_SP=minimum_sp,old_component_prefix_changes=changed,
        remaining_native_ports=['World-fruit producer and current native enemy hit/defeat/token lifecycle','Native source-score queue consumer and hanging/point/body art/OAM presenter','Current camera transport, typed fullbox/head/side/contact/pickup/scene and public owner/cold/ISR routing'],
        scope='Original CD91 dispatcher executes, with only declared native-owned stage services intercepted. Real source fruit touch->fall->hit->freeze->score request and bounded packet imports agree. This is private source/native-terrain phase qualification, not actual new rawID gameplay, native fruit scoring/rendering or source2/3 jump-over bonus admission.',
        bindings={p.relative_to(R).as_posix():W.P.sha(p.read_bytes())for p in [Path(__file__),Path(P.__file__),O/'native-phase-v6.s',O/'native-phase-v6.bin',O/'native-phase-v6-layout.json']})
    (O/'native-phase-v6-CPU.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k]for k in ['passed','component_bytes','header_reserved_spare','component_SHA256','checks','earned_source_fruit','rejected_native_phase_guards','minimum_CPU_SP']}))


if __name__=='__main__':main()
