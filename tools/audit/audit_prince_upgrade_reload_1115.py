"""Read-only upgrade/cold audit and genuine-earned public reload component."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import argparse,json,re,sys
import check_prince_full_fresh_current_1115 as Current
import replay_prince_full_fresh_current_1115 as Factory
import prince_cold_packet_1111 as Packet

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/reference'))
import prince_original_cpu_1101_v1 as Original
from py65.disassembler import Disassembler
from py65.devices.mpu6502 import MPU

N,W,Frames=Current.Base.N,Current.Base.Candidate.W,Current.Base.Candidate.Frames


def instructions(data,origin):
    memory=[0]*65536;memory[origin:origin+len(data)]=data
    d=Disassembler(MPU(memory=memory));pc=origin;rows=[]
    while pc<origin+len(data):
        size,text=d.instruction_at(pc);rows.append(dict(PC=pc,bytes=bytes(memory[pc:pc+size]).hex(),text=text));pc+=size
    return rows


def static(raw):
    assert sha256(raw).hexdigest()==Factory.PIN
    head,parts,_=Packet.extract(raw);bundle=dict(W.Symbols.bundle(),raw=raw)
    status=W.address(bundle,'PlayerStatus');assert status==0x75b
    offset=0xc65f+(0xc7b3-0xc766)-0xc100
    pickup=parts[2][offset:offset+72]
    assert pickup[:3]==bytes.fromhex('adcfc6')
    assert bytes.fromhex('a9018deec6a95b2051aa')in pickup
    assert bytes.fromhex('a9018d5b074ce0c7')in pickup
    init=parts[2][:0x50]
    assert bytes.fromhex('a9058dcfc68dd1c6')in init and bytes.fromhex('ad5b07')not in init
    final=parts[0][0x1fa3:0x1fe0]
    importer=parts[1][0xddbe-0xc800:0xde99-0xc800]
    assert sha256(importer).hexdigest()=='6b497c065c93baaea7bc525fba89bfd20dec48dfeb38d36b797a205147c22bb9'
    labels=json.loads((R/'build/prince-actor-1101-v1/native-labels-v153.json').read_bytes())
    pc=labels['PpNativeRetire'];retire=parts[1][pc-0xc800:pc-0xc800+12]
    donor=Original.donor();writers=[]
    for bank in range(8):
        block=donor[16+bank*16384:16+(bank+1)*16384];origin=0xc000 if bank==7 else 0x8000
        for at in range(len(block)-2):
            if block[at]in(0x8d,0x9d,0x99,0xee,0xce)and block[at+1:at+3]==b'\xee\x06':
                writers.append(dict(bank=bank,PC=origin+at,opcode=block[at:at+3].hex(),
                    context=block[max(0,at-8):at+11].hex(),classification='Raw operand census; code ingress must be authenticated separately'))
    expected=bytes.fromhex('a577d020a9018ddd06a9008dd504a570d005a9008dee06adee06c902d00bceee064cf285a9018dde06')
    at=16+5*16384+0x5c9;assert donor[at:at+len(expected)]==expected
    original_cases=[]
    for selector in(0,1,2,9):
      for sword in(0,1,2):
        c=Original.machine();c.memory.switch(5)
        c.memory[0x77]=0;c.memory[0x70]=selector;c.memory[0x6ee]=sword;c.pc=0x85c9
        Original.until(c,0x85f2,limit=100)
        assert c.memory[0x6ee]==(0 if selector==0 else min(sword,1))
        original_cases.append(dict(selector70=selector,before=sword,after=c.memory[0x6ee]))
    q=dict(passed=True,ROM_SHA256=Factory.PIN,native_PlayerStatus_address=status,
        retained_late_sword_status_is_native_PlayerStatus=True,
        actual_pickup=dict(live_PC=0xc7b3,cold_stream=2,staged_offset=offset,bytes=pickup.hex(),SHA256=sha256(pickup).hexdigest()),
        actual_HostInit=dict(PC=0xc0b0,bytes=init.hex(),SHA256=sha256(init).hexdigest()),
        actual_ColdFinalize=dict(PC=0xbfa3,bytes=final.hex(),code=instructions(final,0xbfa3)),
        actual_Retire=dict(PC=pc,bytes=retire.hex()),importer_SHA256=sha256(importer).hexdigest(),
        donor_SHA256=Original.SHA,original_85C9_bytes=expected.hex(),original_85C9_explicit_primitives=original_cases,
        donor_06EE_raw_write_operand_census=writers,
        caveat='Original selector70 is not yet named as level; primitives are not original campaign/level-clear evidence',
        outputs=0,Mesen=False)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


def state(m):
    s=m.ram[2]
    return dict(x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),y=N.get(m,'Player_Y_Position'),
        world=N.get(m,'WorldNumber'),level=N.get(m,'LevelNumber'),area=N.get(m,'AreaNumber'),
        area_type=N.get(m,'AreaType'),task=N.get(m,'OperMode_Task'),engine=N.get(m,'GameEngineSubroutine'),
        native_PlayerStatus=N.get(m,'PlayerStatus'),HP=s[0x6cf],Sword=s[0x6ee],
        lives=N.get(m,'NumberofLives'),Ready=s[0xab],epoch_valid=s[0xaa],action=s[0x616],
        pose=s[0x617],mode=s[0x618],guard=s[0x6e0],selector70=s[0x70],maps=list(m.rawtags))


def component(raw):
    text=Factory.controller(raw);assert sha256(text.encode()).hexdigest()=='53c107fec29692356caa88d727fb64aea096c39f0220be2a5749da81e01b8235'
    phase='cold';ticks=0;writes=[];cpu_now=None;baseline_bus=W.ControllerBus;baseline_cpu=N.NesMPU
    class Bus(baseline_bus):
        def __setitem__(self,at,value):
            if isinstance(at,int)and cpu_now is not None and cpu_now.memory is self and hasattr(self,'rawtags'):
                if at==0x75b or at in(0xc6ee,0xc6cf)and self.rawtags[2]==2:
                    before=self[at]
                    if value!=before:
                        assert len(writes)<96
                        writes.append(dict(phase=phase,Main=ticks,address=at,before=before,after=value,
                            instruction_PC=cpu_now.instruction_PC,SP=cpu_now.sp,maps=list(self.rawtags)))
            return super().__setitem__(at,value)
    class CPU(baseline_cpu):
        def step(self):
            nonlocal cpu_now
            cpu_now=self;self.instruction_PC=self.pc
            return super().step()
    with patch.object(W,'ControllerBus',Bus),patch.object(N,'NesMPU',CPU):
        m,opening=Current.cold(raw);parent=type(m);phase='ordinary-earned-prefix';checkpoint=None;prefix_proof=None
        class Reached(Exception):pass
        real_frame=Frames.frame
        def frame(model,*args,**kwargs):
            nonlocal ticks,checkpoint
            result=real_frame(model,whole_pass=True);ticks+=1
            if model.ram[2][0x6ee]==1:
                checkpoint=state(model)
                assert checkpoint['HP']>0 and checkpoint['lives']==2 and checkpoint['native_PlayerStatus']==1
                raise Reached()
            return result
        with patch.object(Current.Base.Candidate.Game,'controller',lambda image:text),patch.object(Current.Base.Candidate.Game.Frames,'frame',frame):
            try:prefix_proof=Current.Base.Candidate.Game.route(m,raw,3500)
            except Reached:pass
        m.__class__=parent
        if checkpoint is None:
            return dict(passed=False,diagnostic_complete=True,reason='No genuinely earned Flower/Sword checkpoint',
                prefix=prefix_proof,terminal=state(m),writes=writes,outputs=0,Mesen=False,
                scope='Retained prefix-fixture negative; no reload or persistence conclusion')
        print(json.dumps(dict(event='genuine-earned-upgrade-checkpoint',Main=ticks,state=checkpoint),separators=(',',':')),flush=True)
        baseline=N.fork(m);phase='warm-neutral-control'
        for _ in range(32):baseline.controller_pad=0;real_frame(baseline,whole_pass=True)
        warm=state(baseline);assert warm['Sword']==1 and warm['native_PlayerStatus']==1 and warm['lives']==2
        phase='public-ChgAreaMode-component';b=m.bundle;pc=W.address(b,'ChgAreaMode');at=W.location(b,'ChgAreaMode')
        entry=dict(symbol='ChgAreaMode',PC=pc,physical=at,bytes=raw[at:at+12].hex())
        N.invoke(m,'ChgAreaMode',a=0,x=0,y=0,p=0x21);requested=state(m)
        assert requested['task']==0 and requested['native_PlayerStatus']==checkpoint['native_PlayerStatus']
        phase='actual-reload-Main';stable=0;trace=[];previous=None
        for reload_Main in range(600):
            m.controller_pad=0;real_frame(m,cold=True,whole_pass=True);s=state(m)
            key=tuple(s[k]for k in('task','engine','Ready','Sword','native_PlayerStatus','HP'))
            if key!=previous:trace.append(dict(Main=reload_Main+1,**s));previous=key
            assert s['lives']==2
            if s['task']==3 and s['engine']==8 and s['Ready']==0xa7:stable+=1
            else:stable=0
            if stable>=25:break
        else:raise AssertionError(('Public reload component did not become active',state(m)))
        terminal=state(m)
    q=dict(passed=True,ROM_SHA256=Factory.PIN,frozen_full_Lua_SHA256=sha256(text.encode()).hexdigest(),
        opening=opening,earned_Main=ticks,genuinely_earned=checkpoint,warm_no_reload_control=warm,
        public_reload_entry=entry,after_public_request=requested,reload_Main=reload_Main+1,
        terminal=terminal,trace=trace,actual_writes=writes,gameplay_state_seeds=0,source_array_mounts=0,
        scope='Ordinary earned Flower followed by explicit compiled public ChgAreaMode reload component; not a natural full-stage replay or native proof',outputs=0,Mesen=False)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--component',action='store_true');args=ap.parse_args()
    def deny(*args,**kwargs):raise AssertionError('Upgrade audit attempted file output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        raw=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
        q=static(raw);print(json.dumps(dict(event='upgrade-static',**q),separators=(',',':')),flush=True)
        if args.component:
            q=component(raw);print(json.dumps(q,separators=(',',':')),flush=True)
            if not q['passed']:raise SystemExit(1)
