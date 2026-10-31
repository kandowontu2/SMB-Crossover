"""Current a126 native parser/query/defeat ABI in an isolated WWF arena."""
from pathlib import Path
import collections,copy,hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from verify_native_relocation import NesMPU
from check_tmnt_render_oa import address,location
from prepare_ff_current_component_v2 import qualified
import ff_current_ready_cold_controls_v2 as C
from ff_wram_host_isr_v4 import clone as clone_host
H=C.H;L=R/'build/wwf-native-proxy-lab-v1';J=R/'build/contra-force-world-roles-1031-v2/joint';O=R/'build/wwf-native-proxy-controls-v3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def save(p,q):p.write_text(json.dumps(q,indent=2)+'\n')

def direct(m,pc,a=0x53,x=17,y=91,p=0x71,hook=None,limit=100000):
    c=NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,p,224;c.stPushWord(0x5aff);low=c.sp
    for step in range(limit):
        if c.pc==0x5b00:return c,low
        if hook:hook(m,c,step)
        low=min(low,c.sp);assert m[c.pc]!=0,('Native/selected BRK',hex(c.pc),m.rawtags)
        c.step()
    raise AssertionError(('Native/selected bound',hex(pc),hex(c.pc),m.rawtags))

def duplicate(m):
    n=NesMPU(memory=m,pc=0x5b00);return clone_host(m,n)[0]

def main():
    assert not O.exists();O.mkdir();q=dict(passed=False,source_CPU_lab=True,native_launch=False,no_host_allocation=True,no_ready_state_preload=True,checks={})
    p=json.loads((L/'build-proof.json').read_text());lab=p['labels'];b=qualified(J/'candidate.nes');H.O=J
    for path,h in p['bindings'].items():assert sha(path)==h,path
    try:
        m=C.fresh(b,0)
        H.put(m,CrossoverMenuIndex=0,FmAlts=0,FmGroups=0,CrossoverMenuState=2,SelectedCharacter=0)
        for n in ['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:C.invoke(m,n)
        H.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0,CrossoverMenuButtons=0)
        start=C.invoke(m,'CrossoverMenuInput');assert H.get(m,'SelectedCharacter')==0
        C.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['AXYP_SP'][0],x=start['AXYP_SP'][1],y=start['AXYP_SP'][2],p=start['AXYP_SP'][3]);C.invoke(m,'PauseRoutine',a=0)
        parser=[]
        for age in range(600):
            if H.get(m,'OperMode_Task')==3 and H.get(m,'GameEngineSubroutine')==8:break
            H.put(m,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
            z=C.invoke(m,'GameLoop');C.A.consume(m);parser.append([age,H.get(m,'ScreenRoutineTask'),H.get(m,'GameEngineSubroutine')])
        else:raise AssertionError(('Native parser bound',parser[-3:]))
        assert any(m[address(b,'Block_Buffer_1'):address(b,'Block_Buffer_1')+416])
        q['checks']['native_cold_parser']=dict(passed=True,actual_GameLoop_NMI_pairs=len(parser),final_engine=8,WWF_cache_preloaded_during_parser=False)
        # Private lab executable injection only, never a source-ready/cookie.
        # The actual source constructor is executed after this memory setup.
        m.ram[3][:]=(L/'vm.bin').read_bytes();m.ram[2][:]=(L/'c2.bin').read_bytes()
        m[0x5115]=3;m[0x5116]=2;H.put(m,CurrentBank=3,CurrentBankC=2,SelectedCharacter=29)
        def invoke(name,**kw):
            origin=m.rawtags[:];live=bytes(m[0x1e1:0x200]);scratch=bytes(m[address(b,'R0'):address(b,'R0')+8]);c,low=direct(m,lab[name],**kw)
            assert m.rawtags==origin and bytes(m[0x1e1:0x200])==live and bytes(m[address(b,'R0'):address(b,'R0')+8])==scratch,(name,'Native return frame/scratch/maps')
            return c,low
        invoke('WfHostCold',a=5,x=0,y=55)
        for _ in range(63):invoke('WfIntroFillCore')
        assert m.ram[2][0x79]==m.ram[2][0x7a]==200
        ctx=lab['WfProxyContext'];r0=address(b,'R0');count=0
        def point(x,page,y,yhi,pflags):
            for name,value in [('WfPointX',x),('WfPointPage',page),('WfPointY',y),('WfPointYHi',yhi)]:m[lab[name]]=value
            c,_=invoke('WfHostPoint',a=0x53,x=17,y=91,p=pflags)
            assert[c.a,c.x,c.y,c.sp]==[0x53,17,91,224]
            assert(c.p&~1)==(pflags&~1)and(c.p&1)==m[lab['WfProxyResult']]
            return c.p&1
        # First inspect the real parsed world, without replacing its cells.
        natural=[]
        for x,y in itertools.product([16,40,112,255],[32,176,207,208,224]):
            page=H.get(m,'Player_PageLoc');lo=m[address(b,'BlockBufferAddr')+(page&1)];hi=m[address(b,'BlockBufferAddr')+2+(page&1)];at=(lo+(x>>4))+256*hi+(y&240)-32
            tile=m[at];expected=int(m[address(b,'MTileAttribute')+tile]&3==1);actual=point(x,page,y,1,0x71);assert actual==expected
            natural.append([x,page,y,tile,actual])
        q['checks']['actual_parsed_world_points']=dict(passed=True,cases=len(natural),rows=natural)
        # Finite native-format unit cells exercise every metatile/all flags.
        for tile,page,bits in itertools.product(range(256),[0,1],range(64)):
            flags=0x30|(bits&15)|((bits&48)<<2);x,y=0x7f,0xb7;lo=m[address(b,'BlockBufferAddr')+page];hi=m[address(b,'BlockBufferAddr')+2+page];at=lo+(x>>4)+256*hi+(y&240)-32;m[at]=tile
            expected=int(m[address(b,'MTileAttribute')+tile]&3==1);assert point(x,page,y,1,flags)==expected;count+=1
        for y,yhi,bits in itertools.product([0,31,240,255],[0,1,2],range(64)):
            assert point(128,0,y,yhi,0x30|(bits&15)|((bits&48)<<2))==0;count+=1
        q['checks']['native_point_ABI']=dict(passed=True,cases=count,all_native256_metatiles=True,all64flags=True,AXYP_except_C_R0R7_live_upper_page1_maps_exact=True)
        # Grounded ordinary native actor; every field comes from the actual ABI.
        def enemy(slot=0,ID=6,x=140,y=176,page=0):
            values={'Enemy_Flag':1,'Enemy_ID':ID,'Enemy_State':0,'Enemy_PageLoc':page,'Enemy_X_Position':x,'Enemy_Y_HighPos':1,'Enemy_Y_Position':y,'Enemy_BoundBoxCtrl':0,'Enemy_MovingDir':2}
            for name,value in values.items():m[address(b,name)+slot]=value
        H.put(m,Player_X_Position=128,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0)
        invoke('WfHostImport');enemy();invoke('WfProxyNoteReuse',x=0)
        m.writes.clear();m.ram_writes.clear();base=duplicate(m)
        rejection=0
        fields=['Enemy_Flag','Enemy_ID','Enemy_State','Enemy_PageLoc','Enemy_X_Position','Enemy_Y_HighPos','Enemy_Y_Position','Enemy_BoundBoxCtrl','Enemy_MovingDir']
        for field,bits in itertools.product(fields,range(64)):
            m=duplicate(base)
            enemy();invoke('WfProxySnapshot',x=0);assert m[lab['WfProxyValid']]==1
            # Genuine original action opcodeE91A..E92D produces the victim loss.
            before=m.ram[2][0x7a];direct(m,lab['WfN_E91A'],x=0,p=0x30)
            assert m.ram[2][0x7a]<before;invoke('WfProxyCollect');assert m[lab['WfProxyHitKind']]==1
            at=address(b,field);m[at]^=1;native_before={name:bytes(m[address(b,name):address(b,name)+6])for name in ['Enemy_State','Enemy_Flag']}
            calls=[]
            c,_=invoke('WfProxyCommit',p=0x30|(bits&15)|((bits&48)<<2),hook=lambda mem,cpu,step:calls.append(cpu.pc)if cpu.pc==address(b,'ShellOrBlockDefeat')else None)
            assert not c.p&1 and not calls and native_before=={name:bytes(m[address(b,name):address(b,name)+6])for name in ['Enemy_State','Enemy_Flag']};rejection+=1
        # Identical reused actor tuple is rejected through the required epoch API.
        for bits in range(64):
            m=duplicate(base)
            enemy();invoke('WfProxySnapshot',x=0);direct(m,lab['WfN_E91A'],x=0,p=0x30);invoke('WfProxyCollect');invoke('WfProxyNoteReuse',x=0);enemy()
            c,_=invoke('WfProxyCommit',p=0x30|(bits&15)|((bits&48)<<2));assert not c.p&1;rejection+=1
        q['checks']['changed_actor_reject_before_defeat']=dict(passed=True,cases=rejection,tuple_fields=fields,identical_reuse_epoch_cases=64,shared_epoch_hooks_installed=False)
        def native_return(state,cpu):
            target=(state[0x100+((cpu.sp+1)&255)]+256*state[0x100+((cpu.sp+2)&255)]+1)&65535
            sp=(cpu.sp+2)&255
            for _ in range(100000):
                if cpu.pc==target and cpu.sp==sp:return cpu
                assert state[cpu.pc]!=0,('Native endpointBRK',hex(cpu.pc));cpu.step()
            raise AssertionError(('Native endpointbound',hex(cpu.pc)))
        accepted=0;native_rows=[]
        excluded=set(range(0x100,0x200))|set(range(r0,r0+8))|{address(b,'ObjectOffset')}|set(range(ctx,ctx+64))
        for bits,slot in itertools.product(range(64),[0,5]):
            m=duplicate(base);enemy(slot);invoke('WfProxyNoteReuse',x=slot);invoke('WfProxySnapshot',x=slot)
            before=m.ram[2][0x7a];direct(m,lab['WfN_E91A'],x=0,p=0x30);invoke('WfProxyCollect')
            assert m[lab['WfProxyHealthBefore']]==before and m[lab['WfProxyHealthAfter']]==before-17
            capture=[]
            def hit(mem,cpu,step):
                if cpu.pc==address(b,'ShellOrBlockDefeat'):
                    assert cpu.x==slot and H.get(mem,'ObjectOffset')==slot and H.get(mem,'R1')==slot
                    capture.append((clone_host(mem,cpu),len(mem.writes)))
            flags=0x30|(bits&15)|((bits&48)<<2);c,_=invoke('WfProxyCommit',p=flags,hook=hit)
            assert len(capture)==1 and c.p&1 and[c.a,c.x,c.y,c.sp]==[0x53,17,91,224]and(c.p&~1)==(flags&~1)
            (expected,ec),write_start=capture[0];expected.writes.clear();native_return(expected,ec)
            assert list(m[lab['WfProxyNativeReturn']:lab['WfProxyNativeReturn']+4])==[ec.a,ec.x,ec.y,ec.p]
            assert all(m[a]==expected[a]for a in range(0x8000)if a not in excluded)
            for bank in range(4):
                assert all(a==v or(bank==2 and ctx-0xc000<=i<ctx-0xc000+64)for i,(a,v)in enumerate(zip(m.ram[bank],expected.ram[bank])))
            actual_writes=[(a,v)for a,v in m.writes[write_start:]if a not in excluded]
            expected_writes=[(a,v)for a,v in expected.writes if a not in excluded]
            assert actual_writes==expected_writes and m.rawtags==expected.rawtags
            assert m[address(b,'Enemy_State')+slot]&32 and not m[lab['WfProxyValid']]
            accepted+=1
            if bits==0:native_rows.append(dict(slot=slot,source_health_before=before,source_health_after=before-17,native_return=[ec.a,ec.x,ec.y,ec.p],actual_native_state=m[address(b,'Enemy_State')+slot]))
        q['checks']['source_hit_real_native_defeat']=dict(passed=True,cases=accepted,all64flags=True,actual_native_callback_once=True,raw_source_packet=native_rows,original_damage_opcode='E91A..E92D authored action-entry API fixture, not natural controller eligibility',ordered_native_application_writes_exact=True)
        motion=0
        for bits,x,page,opcode in itertools.product(range(64),[0,1,254,255],[0,1,2],['WfN_E90A','WfN_E907']):
            m=duplicate(base);H.put(m,Player_X_Position=x,Player_PageLoc=page,Player_State=0);invoke('WfHostImport')
            depth=m.ram[2][0x2e];direct(m,lab[opcode],x=0,p=0x30);delta=4 if opcode=='WfN_E90A'else-1
            c,_=invoke('WfHostExport',p=0x30|(bits&15)|((bits&48)<<2))
            assert H.get(m,'Player_X_Position')+256*H.get(m,'Player_PageLoc')==(x+256*page+delta)&65535
            assert H.get(m,'Player_X_Scroll')==delta&255 and m.ram[2][0x2e]==depth
            motion+=1
        for bits,y,hi,opcode in itertools.product(range(64),[0,1,176,255],[0,1,2],['WfN_E8EB','WfN_E8F4']):
            m=duplicate(base);H.put(m,Player_Y_Position=y,Player_Y_HighPos=hi,Player_State=0);invoke('WfHostImport')
            depth=m.ram[2][0x2e];direct(m,lab[opcode],x=0,p=0x30);delta=-3 if opcode=='WfN_E8EB'else 3
            invoke('WfHostExport',p=0x30|(bits&15)|((bits&48)<<2))
            assert H.get(m,'Player_Y_Position')+256*H.get(m,'Player_Y_HighPos')==(y+256*hi+delta)&65535
            assert m.ram[2][0x2e]==depth;motion+=1
        q['checks']['source_coordinate_delta']=dict(passed=True,cases=motion,all64flags=True,source_motion_opcodes=True,ring_depth_unchanged=True,native16bit_page_carry_exact=True)
        gravity=0;gravity_fields=['Player_Y_Position','Player_Y_HighPos','Player_Y_Speed','Player_Y_MoveForce','Player_YMoveForceFractional']
        for bits,speed in itertools.product(range(64),[0,1,3,4]):
            m=duplicate(base);H.put(m,Player_State=2,Player_Y_Speed=speed,Player_Y_MoveForce=0x70,Player_YMoveForceFractional=0x60)
            invoke('WfHostImport');capture=[]
            def fall(mem,cpu,step):
                if cpu.pc==address(b,'ImposeGravitySprObj'):
                    assert cpu.x==0 and cpu.a==4 and H.get(mem,'R0')==H.get(mem,'VerticalForce')
                    capture.append(clone_host(mem,cpu))
            invoke('WfHostExport',p=0x30|(bits&15)|((bits&48)<<2),hook=fall);assert len(capture)==1
            expected,ec=capture[0];native_return(expected,ec)
            assert[H.get(m,n)for n in gravity_fields]==[H.get(expected,n)for n in gravity_fields]
            assert m.ram[2][0x30]==0 and m.ram[2][0x2e]==base.ram[2][0x2e];gravity+=1
        q['checks']['genuine_native_unsupported_fall']=dict(passed=True,cases=gravity,all64flags=True,actual_ImposeGravitySprObj_once=True,fields_exact=gravity_fields,source_jump_and_ring_depth_unchanged=True)
        q.update(passed=True,retained_fixture_negative='V1 reused the same target health across independent stale-guard cases until original victim health reached0, so the next genuine damage opcode correctly produced no further decrease. V2 clones a state produced by the real constructor+intro for each independent case; no health/ready value is seeded.',limits=p['limits']+['WWF executable bytes are explicitly injected into this isolated API arena after a genuine native cold parser; no WWF loader/ready/cookie is preloaded or claimed.','Source VM/native wholeMain routing and native terrain/platform hook placement remain uninstalled.','The actual epoch-notify interface is tested, but physical native constructor/erase hook coverage remains a resource-reviewed integration obligation.'])
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc());raise
    finally:
        paths=[Path(__file__),Path(C.__file__),Path(H.__file__),R/'tools/audit/verify_native_relocation.py',L/'build-proof.json',L/'proxy.s',L/'native-imports.s',L/'c2.bin',L/'vm.bin',J/'candidate.nes',J/'candidate.dbg']
        q['bindings']={str(path.resolve()):sha(path)for path in paths};save(O/'controls.json',q);print(json.dumps({k:q.get(k)for k in ['passed','checks','error']}))
if __name__=='__main__':main()
