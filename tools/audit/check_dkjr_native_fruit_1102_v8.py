"""Private world fruit/camera versus donor phase and current native services."""
import collections,itertools,json
from pathlib import Path
import prepare_dkjr_native_fruit_1102_v8 as P
import check_hogan_current_bounded_v1 as N
R=P.R;O=P.O;D=P.D;W=P.W


def main():
    b=W.scoped_load(R/'build/excitebike-pose-1101-v3/current4.nes');b['raw']=P.CURRENT.read_bytes();assert W.P.sha(b['raw'])==P.PIN
    q=json.loads((O/'native-fruit-v8-layout.json').read_text());L=q['labels'];blob=(O/'native-fruit-v8.bin').read_bytes();assert W.P.sha(blob)==q['code_SHA256']
    active,_=D.active();seed=bytes(active.memory[:2048]);counts=collections.Counter();minimum_sp=255;phase_rows=[]
    def put(m,name,value,i=0):m[N.address(b,name)+i]=value
    def get(m,name,i=0):return N.get(m,name,i)
    def call(m,name,a=0x57,x=7,y=9,p=0xf1):
        nonlocal minimum_sp
        c=N.NesMPU(memory=m,pc=L[name]);c.a,c.x,c.y,c.p,c.sp=a,x,y,p,224;c.stPushWord(0x5ffe)
        for _ in range(100000):
            if c.pc==0x5fff:break
            minimum_sp=min(minimum_sp,c.sp);assert m[c.pc]!=0,('private BRK',name,hex(c.pc),m.rawtags);c.step()
        else:raise AssertionError(('private bound',name,hex(c.pc),m.rawtags))
        assert c.sp==224;return(c.a,c.x,c.y,c.p,c.processorCycles)
    def fresh(camera=0,player=0):
        m=N.Bus(b);m.ram[3][:len(blob)]=blob;m.ram[2][:2048]=seed;m.raw_page(1,3);m.raw_page(2,2)
        N.put(m,CurrentBank=3,CurrentBankC=2,SelectedCharacter=0,CurrentPlayer=player,OperMode=1,GameEngineSubroutine=8,TimerControl=0,VRAM_Buffer1_Offset=0,ObjectOffset=4,
            ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8)
        m.ram[2][0x400:0x439]=bytes(57)
        for i in range(6):put(m,'DigitModifier',0,i)
        call(m,'DkjrNativeFruitReset');return m
    def native_score(m,player=0):
        at=N.address(b,'Player%dScoreDisplay'%(player+1));return sum(m[at+i]*10**(6-i)for i in range(6))
    # Actual AddToScore, with donor C61B selection and original F044 arithmetic.
    source_amounts=list(D.Bus()[0xc61b:0xc622]);score_cpu=[]
    for index,player,value,flags in itertools.product(range(7),[0,1],[0,12340,99990],[0x20,0xf1]):
        m=fresh(player=player)
        for p in [0,1]:
            for i,v in enumerate('%06d'%(value//10)):put(m,'Player%dScoreDisplay'%(p+1),int(v),i)
        donor=D.Bus();donor[:2048]=seed;donor[0x24+4*player]=0;donor[0x25+4*player:0x28+4*player]=bytes.fromhex('%06d'%value);donor[0]=source_amounts[index];donor[1]=8|player
        d=D.T.NesMPU(memory=donor,pc=0);D.T.run(d,0xf044);expected=int(bytes(donor[0x25+4*player:0x28+4*player]).hex())
        scratch=bytes(m[N.address(b,'R0'):N.address(b,'R0')+8]);smc=bytes(m[0x15a:0x17b]);maps=list(m.rawtags);off=get(m,'ObjectOffset');state=bytes(m.ram[2][:2048])
        z=call(m,'DkjrNativeAwardSourcePoints',x=index,p=flags);assert z[:4]==(0x57,index,9,flags|0x30)
        assert native_score(m,player)==expected and native_score(m,player^1)==value
        assert scratch==bytes(m[N.address(b,'R0'):N.address(b,'R0')+8])and smc==bytes(m[0x15a:0x17b])and maps==m.rawtags and off==get(m,'ObjectOffset')and state==bytes(m.ram[2][:2048])
        score_cpu.append(z[4]);counts['actual_native_direct_award_matches_original_C61B_F044_preserves_AXYP_maps_SMC_R0_actor']=1+counts['actual_native_direct_award_matches_original_C61B_F044_preserves_AXYP_maps_SMC_R0_actor']
    # Every source body/effect cell, including indices128..252, moves once.
    for camera,delta in itertools.product([0,1,255,256,511,65535],range(-8,9)):
        m=fresh(camera)
        for i in range(64):m.ram[2][0x200+4*i]=255 if i%3==0 else 32+i;m.ram[2][0x203+4*i]=(11*i)&255
        before=bytearray(m.ram[2][:2048]);world=(camera+delta)&65535;put(m,'ScreenLeft_X_Pos',world&255);put(m,'ScreenLeft_PageLoc',world>>8)
        z=call(m,'DkjrNativeShiftCamera');assert z[3]&1
        for i in range(64):
            if before[0x200+4*i]!=255:before[0x203+4*i]=(before[0x203+4*i]-delta)&255
        before[0x435]=world&255;before[0x436]=world>>8;before[0x437]=0xd7;before[0x438]=delta&255
        assert before==bytes(m.ram[2][:2048]),('camera cell transport',camera,delta)
        again=bytes(m.ram[2][:2048]);call(m,'DkjrNativeShiftCamera');expected=bytearray(again);expected[0x438]=0;assert expected==bytes(m.ram[2][:2048])
        counts['all64_source_OAM_cells_camera_shift_and_repeat_idempotence']+=1
    for delta in [-257,-256,-17,-9,9,17,256,257]:
        m=fresh(256);before=bytearray(m.ram[2][:2048]);world=(256+delta)&65535;put(m,'ScreenLeft_X_Pos',world&255);put(m,'ScreenLeft_PageLoc',world>>8)
        z=call(m,'DkjrNativeShiftCamera');assert not z[3]&1;before[0x438]=delta&255;assert before==bytes(m.ram[2][:2048]);counts['script_camera_jump_requires_explicit_resync_before_actor_mutation']+=1
    for camera,relative,slot,available in itertools.product([0,1,15,255,256,65520],[0,7,15,239,240,255,256,65535],range(4),[0,1]):
        m=fresh(camera);world=(camera+relative)&65535
        for name,v in [('R0',world&255),('R1',world>>8),('R2',80),('R3',slot%3)]:
            # RAM aliases are native consecutive R0..3, not extra host bytes.
            m[N.address(b,'R0')+int(name[1:])]=v
        low=bytes(m[:256])+bytes(m[0x200:0x800]);z=call(m,'DkjrNativeFruitSet',x=slot);assert z[3]&1 and low==bytes(m[:256])+bytes(m[0x200:0x800])
        m.ram[2][0x430+slot]=available;call(m,'DkjrNativeFruitProject');r=m.ram[2];visible=bool(available and relative<240)
        assert r[0x93]==7*(slot+1)and r[0x400]==7*(slot+1)and r[0x91:0x93]==bytes([0,4])
        assert r[0x9a+slot]==int(visible)and r[0x430+slot]==available
        if visible:assert r[0x401+7*slot:0x408+7*slot]==bytes([relative,80,0xa4+4*(slot%3),0x24,0x24,0x24,0x24])
        # Removal does not reset jump fractions, pose or timers, and projection
        # must not resurrect a consumed fruit when it reenters the viewport.
        if visible:
            r[0x8c]=slot+1;r[0x9a+slot]=0;before=bytearray(r[:2048]);z=call(m,'DkjrNativeFruitRemove');before[0x430+slot]=0;assert before==bytes(r[:2048])and z[:4]==(0x57,7,9,0xf1)
            call(m,'DkjrNativeFruitRemove');call(m,'DkjrNativeFruitProject');assert r[0x9a+slot]==0 and r[0x430+slot]==0
        counts['world_projection_boundaries_and_once_only_source_removal']+=1
    for slot,y,kind in itertools.product([0,3,4,255],[0,31,32,200,201,255],[0,2,3,255]):
        if slot<4 and 32<=y<=200 and kind<3:continue
        m=fresh();m[N.address(b,'R0')+2]=y;m[N.address(b,'R0')+3]=kind;before=[bytes(x)for x in m.ram];z=call(m,'DkjrNativeFruitSet',x=slot)
        assert not z[3]&1 and before==[bytes(x)for x in m.ram];counts['malformed_fruit_set_rejects_before_private_write']+=1
    # Actual donor CD91, with the same declared native-owned stage seams asv6.
    original_raw=bytearray(D.donor())
    for at,ptr in [(0xc440,0x600),(0xc448,0x650),(0xc450,0x680)]:
        pos=16+at-0xc000;original_raw[pos:pos+2]=ptr.to_bytes(2,'little')
    def original_phase(donor,pad):
        d=D.T.NesMPU(memory=donor,pc=0);D.T.run(d,0xf23e,pad,0,9,0x20);d.pc=0xcd91;d.sp=224;d.stPushWord(0x5ffe)
        for _ in range(100000):
            if d.pc==0x5fff:return
            if d.pc in[0xcdfd,0xced4,0xcf9d,0xcf62]:d.pc=(d.stPopWord()+1)&65535;continue
            if d.pc in[0xd2fc,0xcef4]:d.pc=0xd43a if d.pc==0xd2fc else 0xdbb3
            assert donor[d.pc]!=0;d.step()
        raise AssertionError(('donor phase bound',hex(d.pc)))
    data=L['DkjrSourceData']
    def ptr_translate(r):
        r=bytearray(r)
        for p in [2,0x91]:
            v=r[p]+256*r[p+1]
            if 0xc2cd<=v<0xc3cd:r[p:p+2]=(data+v-0xc2cd).to_bytes(2,'little')
        return r
    for camera,fruit in itertools.product([0,255,511],[False,True]):
        donor=D.Bus(bytes(original_raw));donor[:2048]=seed;donor[0:3]=bytes([40,191,0x18]);c=D.T.NesMPU(memory=donor,pc=0);D.T.run(c,0xe9ee,0,0,0,0x20)
        for a,v in [(0x6b,1),(0x6c,1),(0x6d,1),(0x54,4),(0x55,4),(0x4a,1),(0x4e,0),(0x68,0),(0x8c,0),(0xa0,1),(0xb0,1),(0x2c0,255),(0x2e0,255),(0x330,0),(0x301,0),(0x300,0)]:donor[a]=v
        donor[0x9a:0x9e]=bytes(4);donor[0x302:0x330]=bytes(46);donor[0x650]=donor[0x680]=255
        cells=[]
        for left in range(-(camera&15),192,16):cells.extend([max(0,left),208,left+15,223])
        donor[0x600:0x600+len(cells)+1]=bytes(cells+[255]);m=fresh(camera);m.ram[2][:2048]=ptr_translate(donor[:2048]);call(m,'DkjrNativeWorldEnable');call(m,'DkjrNativeFruitReset')
        for block in['Block_Buffer_1','Block_Buffer_2']:
            for row in[11,12]:m[N.address(b,block)+16*row:N.address(b,block)+16*row+16]=[0x54]*16
        if fruit:
            wx=(camera+60)&65535
            for i,v in enumerate([wx&255,wx>>8,191,0]):m[N.address(b,'R0')+i]=v
            call(m,'DkjrNativeFruitSet',x=0);donor[0x91:0x93]=(0x500).to_bytes(2,'little');donor[0x93]=7;donor[0x500:0x508]=bytes([7,60,191,0xa4,0x24,0x24,0x24,0x24]);donor[0x9a]=1;donor[0x8d]=0
            controls=[0]*80
        else:
            donor[0x93]=0;controls=[0]*20+[0x81]+[2]*55+[0]*20+[1]*40
        initial=native_score(m);released=0;min_y=255
        for epoch,pad in enumerate(controls):
            original_phase(donor,pad);put(m,'SavedJoypadBits',pad);call(m,'DkjrNativePhase');r=m.ram[2];min_y=min(min_y,r[0x210])
            indices=list(range(0x14,0x91))+list(range(0x94,0x100))+list(range(0x200,0x300))+list(range(0x439,0x500))+list(range(0x508,0x600))+list(range(0x700,0x800))
            # Nonhit rectangle/grip scratch depends on the last nonintersecting
            # cell in a whole-floor oracle versus a local native query window.
            if donor[0xf]==0 and r[0xf]==0:
                indices=[i for i in indices if not 0x42<=i<0x46]
                if donor[0x6b]!=2 and donor[0x71]==0 and r[0x71]==0:indices=[i for i in indices if i not in[0x73,0x74]]
            diffs=[(i,donor[i],r[i])for i in indices if donor[i]!=r[i]];assert not diffs,('native source phase',camera,fruit,epoch+1,diffs[:12])
            world=(camera+r[0x213]+8)&65535;assert get(m,'Player_X_Position')+256*get(m,'Player_PageLoc')==world and get(m,'Player_Y_Position')==r[0x210]-15
            if fruit and not r[0x430]:released+=1
            counts['current_native_Main_source_actor_OAM_phase_parity']+=1
        if fruit:assert released==80 and native_score(m)-initial==400 and m.ram[2][0x8c]==0
        else:assert min_y==176 and native_score(m)==initial
        phase_rows.append(dict(camera=camera,world_fruit=fruit,epochs=len(controls),native_score_delta=native_score(m)-initial,minimum_source_y=min_y,source_phase_exact=True))
    out=dict(passed=True,native_emulator=False,ROM_written=False,native_owner_admitted=False,base_ROM_SHA256=P.PIN,component_SHA256=q['code_SHA256'],component_bytes=len(blob),header_reserved_spare=8160-len(blob),checks=dict(counts),native_phase_trajectories=phase_rows,minimum_CPU_SP=minimum_sp,native_score_CPU=dict(minimum=min(score_cpu),maximum=max(score_cpu)),
        resource_scope='Typed C400..C438 world records reuse source-dead native-profile geometry inside the existing2KB measurement state; no extra RAM/physical grant. Indirect/interrupt/public reader closure still required before allocation.',
        scope='Current native services execute on isolated legal Mario0. Real donor CD91 actor/fruit/phase and source OAM agree after replacing donor-only score/VRAM queues with actual native score and world/OAM fruit removal. World fruit touched/falls/retires, score400 once; no native victim, draw or full-stage claim.',
        bindings={p.relative_to(R).as_posix():W.P.sha(p.read_bytes())for p in[Path(__file__),Path(P.__file__),O/'native-fruit-v8.s',O/'native-fruit-v8.bin',O/'native-fruit-v8-layout.json',P.CURRENT]})
    (O/'native-fruit-v8-CPU.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in['passed','component_bytes','header_reserved_spare','component_SHA256','checks','minimum_CPU_SP']}))


if __name__=='__main__':main()
