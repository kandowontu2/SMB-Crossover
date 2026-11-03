"""Original packed-BCD score oracle versus actual current native score service."""
import collections,itertools,json
from pathlib import Path
import prepare_dkjr_native_score_1102_v7 as P
import check_hogan_current_bounded_v1 as N
R=P.R;O=P.O;D=P.D;W=P.W


def main():
    # Repeat the phase comparisons against this linked successor. The source
    # queues are empty in the actual native terrain trajectories; score cases
    # below execute the real banked service separately on legal Mario0.
    path=R/'tools/audit/check_dkjr_native_phase_1102_v6.py';src=path.read_text().replace('import prepare_dkjr_native_phase_1102_v6 as P','import prepare_dkjr_native_score_1102_v7 as P')
    src=src.replace('native-phase-v6','native-score-v7-phase')
    # The phase source is the same linked binary, not a duplicate generated copy.
    for suffix in ['.bin','.s','-layout.json']:
        src=src.replace('native-score-v7-phase'+suffix,'native-score-v7'+suffix)
    env={'__name__':'dkjr_v7_phase_regression','__file__':__file__};exec(compile(src,str(path),'exec'),env);env['main']()
    b=W.scoped_load(R/'build/excitebike-pose-1101-v3/current4.nes');b['raw']=P.CURRENT.read_bytes();assert W.P.sha(b['raw'])==P.PIN
    q=json.loads((O/'native-score-v7-layout.json').read_text());blob=(O/'native-score-v7.bin').read_bytes();assert W.P.sha(blob)==q['code_SHA256'];L=q['labels'];counts=collections.Counter();min_sp=255;cycles=[]
    active,_=D.active();seed=bytes(active.memory[:2048])
    def get(m,name,i=0):return N.get(m,name,i)
    def put(m,name,value,i=0):m[N.address(b,name)+i]=value
    def fresh(player=0):
        m=N.Bus(b);m.ram[3][:len(blob)]=blob;m.ram[2][:2048]=seed;m.raw_page(1,3);m.raw_page(2,2)
        N.put(m,CurrentBank=3,CurrentBankC=2,SelectedCharacter=0,CurrentPlayer=player,OperMode=1,GameEngineSubroutine=8,TimerControl=0,VRAM_Buffer1_Offset=0,ObjectOffset=4)
        for i in range(8):put(m,'R0',0x80+i,i)
        for i in range(6):put(m,'DigitModifier',0,i)
        m.ram[2][0x300:0x330]=bytes(48)
        return m
    def call(m,regs=(0x57,7,9,0xf1)):
        nonlocal min_sp
        c=N.NesMPU(memory=m,pc=L['DkjrNativePublishScore']);c.a,c.x,c.y,c.p,c.sp=*regs,224;c.stPushWord(0x5ffe)
        for _ in range(100000):
            if c.pc==0x5fff:break
            min_sp=min(min_sp,c.sp);assert m[c.pc]!=0,('native score BRK',hex(c.pc),m.rawtags);c.step()
        else:raise AssertionError(('native score bound',hex(c.pc),m.rawtags))
        assert c.sp==224 and(c.a,c.x,c.y,c.p)==(*regs[:3],regs[3]|0x30)
        return c.processorCycles
    def digits(m,player):return list(m[N.address(b,'Player%dScoreDisplay'%(player+1)):N.address(b,'Player%dScoreDisplay'%(player+1))+6])
    def decimal(values):return sum(v*10**(6-i)for i,v in enumerate(values))
    cases=[]
    for amount,player,value,flags,offset in itertools.product([0x01,0x02,0x03,0x04,0x08,0x12,0x16],[0,1],[0,12340,99990],[0x20,0xf1],[0,17,48]):
        m=fresh(player);initial=[int(ch)for ch in '%06d'%(value//10)]
        for p in [0,1]:
            for i,v in enumerate(initial):put(m,'Player%dScoreDisplay'%(p+1),v,i)
        put(m,'VRAM_Buffer1_Offset',offset)
        m.ram[2][0x300]=44;m.ram[2][0x301]=0;m.ram[2][0x32e]=0x18|player;m.ram[2][0x32f]=amount
        source=D.Bus();source[:2048]=seed;source[0x24+4*player]=0;source[0x25+4*player:0x28+4*player]=bytes.fromhex('%06d'%value)
        source[0]=amount;source[1]=8|player;c=D.T.NesMPU(memory=source,pc=0);D.T.run(c,0xf044)
        packed=bytes(source[0x25+4*player:0x28+4*player]);expected=int(packed.hex())
        maps=list(m.rawtags);scratch=bytes(m[N.address(b,'R0'):N.address(b,'R0')+8]);smc=bytes(m[0x15a:0x17b]);object_offset=get(m,'ObjectOffset');private=bytes(m.ram[2][:2048])
        duration=call(m,(0x57,7,9,flags));cycles.append(duration)
        assert decimal(digits(m,player))==expected,(amount,player,value,digits(m,player),expected)
        assert digits(m,player^1)==initial and maps==m.rawtags and scratch==bytes(m[N.address(b,'R0'):N.address(b,'R0')+8])and smc==bytes(m[0x15a:0x17b])and get(m,'ObjectOffset')==object_offset
        expected_private=bytearray(private);expected_private[0x300]=0;expected_private[0x32e]=0
        assert bytes(m.ram[2][:2048])==expected_private
        assert bytes(m[N.address(b,'DigitModifier'):N.address(b,'DigitModifier')+6])==bytes(6)
        score_before=digits(m,player);call(m,(0x57,7,9,flags));assert digits(m,player)==score_before
        counts['actual_native_score_matches_original_packed_BCD_and_is_once_only']+=1
        if len(cases)<7:cases.append(dict(original_BCD_hundreds=amount,native_score_added=expected-value,CPU=duration))
    skip_cycles=[]
    for player,index,kind,amount in itertools.product([0,1],[0,2,44],[0,0x30,0x40,0x20,0x18,0x19],[0x01,0x1a]):
        m=fresh(player);m.ram[2][0x300]=index;m.ram[2][0x302+index]=kind;m.ram[2][0x303+index]=amount
        before=bytes(m[:256])+bytes(m[0x200:0x800]);maps=list(m.rawtags);state=bytes(m.ram[2][:2048]);score=[digits(m,i)for i in [0,1]]
        legal_point=kind in[0x18,0x19]and kind&1==player and amount==1
        if legal_point:continue
        duration=call(m);skip_cycles.append(duration)
        assert before==bytes(m[:256])+bytes(m[0x200:0x800])and maps==m.rawtags and score==[digits(m,i)for i in[0,1]]
        expected=bytearray(state)
        if kind in[0x30,0x40]:expected[0x302+index]=0;expected[0x300]=(index+2)%46
        assert bytes(m.ram[2][:2048])==expected
        counts['empty_UI_and_invalid_requests_do_not_award_or_corrupt_native_state']+=1
    for index in [1,3,45,46,128,255]:
        m=fresh();m.ram[2][0x300]=index;before=bytes(m[:256])+bytes(m[0x200:0x800]);state=[bytes(x)for x in m.ram];call(m)
        assert before==bytes(m[:256])+bytes(m[0x200:0x800])and state==[bytes(x)for x in m.ram];counts['malformed_ring_index_rejects_before_write']+=1
    phase=json.loads((O/'native-score-v7-phase-CPU.json').read_text());assert phase['passed']and phase['component_SHA256']==q['code_SHA256']
    out=dict(passed=True,native_emulator=False,native_owner_admitted=False,ROM_written=False,base_ROM_SHA256=P.PIN,component_SHA256=q['code_SHA256'],component_bytes=len(blob),header_reserved_spare=8160-len(blob),
        checks=dict(counts),original_phase_comparisons=phase['checks'],source_amount_examples=cases,minimum_CPU_SP=min_sp,score_CPU=dict(minimum=min(cycles),maximum=max(cycles),empty_UI_invalid_maximum=max(skip_cycles)),
        scope='Actual current banked AddToScore runs in isolated legal Mario0/current-player fixtures. Original F044 packed-BCD arithmetic independently proves100/200/300/400/800/1200/1600, with native HUD queue side effects, pointer wrap/once-only, AXYP/maps/R0..7/ObjectOffset/all33SMC preservation. No DK public row, real native enemy/fruit/OAM/IRQ or physical resource admission.',
        bindings={p.relative_to(R).as_posix():W.P.sha(p.read_bytes())for p in [Path(__file__),Path(P.__file__),O/'native-score-v7.s',O/'native-score-v7.bin',O/'native-score-v7-layout.json',O/'native-score-v7-phase-CPU.json',P.CURRENT]})
    (O/'native-score-v7-CPU.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in ['passed','component_bytes','header_reserved_spare','component_SHA256','checks','minimum_CPU_SP','score_CPU']}))


if __name__=='__main__':main()
