"""Finite full caller/queue/IRQ controls for the5a queued-HP successor."""
from pathlib import Path
import hashlib
import itertools
import json

from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location
from cv3_life_gain_controls_v1 import fresh, run, regs, live, clone, BASE
from cv3_watch_single_owner_controls_v1 import TimedMPU
from proto_palette_coalesce_controls_v1 import update
from chip_hud_queue_controls_v1 import arena, queue, compare, irq_live, nmi_run, nmi_buses
import current_chip_dale_earned_cpu_v1 as earned

R=Path(__file__).resolve().parents[2]
B=R/'build'
P=B/'kirby-mike-polish-production.nes'
N=B/'chip_hud_queue_complete.nes'
OLD='5a0a37a97e95ce3c1086f91f6000ad0157bb477f923027d39f0342d9389e6db2'
NEW='129dabe88489c78e1ead49b17e898979bd01ee0806d44eba2efc1871d4dd227f'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
HP=lambda v:bytes.fromhex('204b04241119')+bytes([v])
T1=bytes.fromhex('265c022424267c022424206d020001206206240000000300')
T2=bytes.fromhex('26400224242660022424206d020002206206240000000800')
COLOR=bytes.fromhex('3f0c040f17170f')


def expected(prefix,health):
    """Independent bounded packet/address oracle; unknown native formats decline."""
    cursor=0
    valid=False
    while cursor<len(prefix):
        if cursor+3>=len(prefix):return False
        high,low,header=prefix[cursor:cursor+3]
        count=header&63
        if not 0x20<=high<0x40 or header&192 or count==0:return False
        end=cursor+3+count
        if end>len(prefix):return False
        addresses=[((high<<8)|low)+i for i in range(count)]
        # Potentially identical physical nametable cells under ANY mirroring.
        overlaps=any(0x2000<=a<0x3f00 and 0x4b<=a%1024<=0x4e for a in addresses)
        if overlaps:valid=prefix[cursor:end]==HP(health)
        cursor=end
    return valid


def actual_sequence(old,new,which):
    hp=3 if which==1289 else 2
    qs=[arena(b,health=hp)for b in(old,new)]
    cycles=[0,0]
    stages=[]
    def draw():
        for i,q in enumerate(qs):
            c,_=run(q,'CdHud');cycles[i]+=c.processorCycles
        stages.append([q.get('VRAM_Buffer1_Offset')for q in qs])
    def append(data):
        for q in qs:
            at=q.get('VRAM_Buffer1_Offset')
            for i,v in enumerate(data+b'\0'):q.set('VRAM_Buffer1',v,at+i)
            q.set('VRAM_Buffer1_Offset',at+len(data))
    draw()
    if which==1289:draw();draw();append(T1);draw()
    else:append(T2);draw();append(COLOR);draw()
    before=[queue(q).hex()for q in qs]
    assert len(bytes.fromhex(before[0]))==53
    assert before[0]==((HP(hp)*3+T1+HP(hp))if which==1289 else(HP(hp)+T2+HP(hp)+COLOR+HP(hp))).hex()+'00'
    assert len(bytes.fromhex(before[1]))==(32 if which==1289 else 39)
    consumers=[update(q)for q in qs]
    assert consumers[0][1]==consumers[1][1]
    stripped=lambda v:[(a,z)for a,z in v if not 0x204b<=a<=0x204e]
    assert stripped(consumers[0][2])==stripped(consumers[1][2])
    saving=504 if which==1289 else 336
    assert consumers[0][0]-consumers[1][0]==saving
    return dict(original_point=which,staged_producer_order=stages,queue_hex=before,
        queue_bytes=[len(bytes.fromhex(q))-1 for q in before],PPUDATA=[len(c[2])for c in consumers],
        source_CdHud_cycles=cycles,foreground_delta=cycles[1]-cycles[0],
        source_UpdateScreen_cycles=[c[0]for c in consumers],NMI_consumer_saving=saving,
        exact_final_PPU_map=True,ordered_non_HP_PPUDATA_exact=True,
        scope='Reconstructed actual native packet producer order with current5a original CdHud reference. This is source CPU cost, not actual successor native timing/cadence.')


def nmi_checked(q,key):
    # Different interruption points have legitimately different live Y. The
    # original stream reader's exact STY SavedY snapshot is checked against
    # that real CPU Y, not incorrectly forced equal to another entry's Y.
    pc=address(q.b,'CdHud');q.m.page(1,79);q.set('CurrentBank',207)
    c=TimedMPU(memory=q.m,pc=pc);c.a,c.x,c.y,c.p,c.sp=103,137,171,32,253;c.stPushWord(0x5aff)
    q.m.writes=[];q.m.nmi_indices=set();q.m.nmi_snapshot_indices=set()
    writer=address(q.b,'ExpandedAudioTick::Byte')+2
    at=location(q.b,'ExpandedAudioTick::Byte')+2
    saved=address(q.b,'XgLzSavedY')
    assert saved==235 and (at-16)//8192==38 and q.b['raw'][at:at+2]==bytes([0x84,saved])
    entry=None;inside=False
    smc=[address(q.b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(q.b,'FarcallJmpTarget_SMC')+2]
    for _ in range(150000):
        if c.pc==0x5b00:break
        bank=q.m.banks[(c.pc-32768)//8192]if c.pc>=32768 else -1
        if (c.pc,bank)==key and entry is None:
            entry=(regs(c),c.pc,q.m.banks[:],[q.m[a]for a in smc],queue(q))
            before=len(q.m.writes);c.nmi();q.m.nmi_indices.update(range(before,len(q.m.writes)));inside=True;continue
        pc=c.pc;opcode=q.m[pc];y=c.y;before=len(q.m.writes);c.step()
        if inside:
            q.m.nmi_indices.update(range(before,len(q.m.writes)))
            if pc==writer and bank==38:
                assert q.m.writes[before:]==[(saved,y)],'Actual source STY XgLzSavedY equals real CPU Y'
                q.m.nmi_snapshot_indices.add(before)
            if opcode==64:
                assert regs(c)==entry[0] and c.pc==entry[1] and q.m.banks==entry[2]
                assert [q.m[a]for a in smc]==entry[3] and queue(q)==entry[4]
                inside=False
    else:raise AssertionError(('Lag NMI timeout',hex(c.pc),q.m.banks))
    assert entry is not None and not inside and c.sp==253 and q.get('NmiSkipped')==1
    return c


def checked_nmi_buses(q):
    keep=set()
    for g in q.b['segs'].values():
        if g['name']=='"SMCCODE"':keep.update(range(int(g['start'],0),int(g['start'],0)+int(g['size'],0)))
    foreground=[];interrupt=[]
    for i,(a,v)in enumerate(q.m.writes):
        if 256<=a<512 and a not in keep:continue
        if i in q.m.nmi_snapshot_indices:
            assert a==235
            value='actual-source-preserved-Y' # value was already checked at its genuine STY instruction.
        else:value=v
        (interrupt if i in q.m.nmi_indices else foreground).append((a,value))
    return foreground,interrupt


def main():
    assert sha(P)==OLD and sha(N)==NEW
    old,new=scoped_load(P),scoped_load(N)
    out=B/'chip_hud_queue_complete_controls.json';assert not out.exists()
    cases=[('empty',b''),('whole-HP',HP(3)),('changed-health',HP(2)),('HP-before-other',HP(3)+T1),
        ('HP-after-other',T1+HP(3)),('two-HP',HP(3)*2),('three-current-HP',HP(3)+T1+HP(3)+COLOR+HP(3)),
        ('latest-changed',HP(3)+HP(2)),('latest-corrected',HP(2)+HP(3)),
        ('partial-then-new-HP',HP(3)+bytes.fromhex('204c0111')+HP(3)),
        ('overlap-after-HP',HP(3)+bytes.fromhex('204d0111')),
        ('RLE-conservative',HP(3)+bytes.fromhex('22204724')),
        ('vertical-conservative',HP(3)+bytes.fromhex('2220822424')),
        ('zero256-conservative',HP(3)+bytes.fromhex('22204024')),
        ('high-address-alias',HP(3)+bytes.fromhex('604b0105')),
        ('fake-header-payload',bytes.fromhex('222007')+HP(3)),
        ('truncated-header',HP(3)+bytes.fromhex('2220')),
        ('truncated-data',HP(3)+bytes.fromhex('2220092424')),
        ('premature-terminator',HP(3)+b'\0'*4)]
    for high,start,count in itertools.product([0x20,0x24,0x28,0x2c,0x30,0x34,0x38,0x3c],
            [0x3f,0x40,0x4a,0x4b,0x4c,0x4e,0x4f,0x50,0xf0,0xff],[1,2,4,16,63]):
        cases.append(('alias-overlap-range',HP(3)+bytes([high,start,count])+b'\x24'*count))
    for count in range(1,64):
        other=bytes([0x22,0x20,count])+b'\x24'*count
        cases.extend([('literal-length-after',HP(3)+other),('literal-length-before',other+HP(3))])
    direct=[];maximum=0
    for name,prefix in cases:
        assert len(prefix)<77
        suppress=expected(prefix,3)
        qs=[arena(b,prefix)for b in(old,new)]
        cs=[run(q,'CdHud')[0]for q in qs]
        compare(qs,cs,suppress)
        assert queue(qs[1])==(prefix+b'\0'if suppress else queue(qs[0]))
        delta=cs[1].processorCycles-cs[0].processorCycles;maximum=max(maximum,delta)
        if len(direct)<19:direct.append(dict(name=name,prefix=prefix.hex(),suppressed=suppress,
            cycles=[c.processorCycles for c in cs],delta=delta))
    # Retain arbitrary entry flags, both real alternates/modes, real health
    # changes, full original admission/capacity semantics and malformed tail.
    boundaries=0
    for hp,pending,variant,mode,flags in itertools.product([0,1,2,3,255],[1,3],[0,1],[0,1],[0x20,0x61,0xeb]):
        prefix=HP(pending)+T2+HP(hp)+COLOR
        qs=[arena(b,prefix,hp,variant,mode)for b in(old,new)]
        cs=[run(q,'CdHud',flags=flags)[0]for q in qs];compare(qs,cs,True);boundaries+=1
    guards=[]
    for state in [dict(SelectedCharacter=13),dict(SelectedCharacter=17),dict(OperMode=0),dict(OperMode=2),dict(DisableScreenFlag=1),dict(DisableScreenFlag=255)]:
        qs=[arena(b,HP(3),state=state)for b in(old,new)];cs=[run(q,'CdHud')[0]for q in qs]
        compare(qs,cs);assert cs[0].processorCycles==cs[1].processorCycles
        guards.append(state)
    for offset in [77,78,83,84,255]:
        qs=[arena(b,HP(3))for b in(old,new)]
        for q in qs:q.set('VRAM_Buffer1_Offset',offset)
        cs=[run(q,'CdHud')[0]for q in qs];compare(qs,cs);assert cs[0].processorCycles==cs[1].processorCycles
        guards.append(dict(offset=offset))
    for prefix in [HP(3),HP(3)+T2]:
        qs=[arena(b,prefix)for b in(old,new)]
        for q in qs:q.set('VRAM_Buffer1',0x22,len(prefix))
        cs=[run(q,'CdHud')[0]for q in qs];compare(qs,cs);assert queue(qs[0])==queue(qs[1])
    full=[]
    for identity,mode in itertools.product(BASE,[0,1]):
        qs=[fresh(b,identity,mode)for b in(old,new)]
        for q in qs:q.put(DisableScreenFlag=0,VRAM_Buffer1_Offset=0,VRAM_Buffer1=0)
        cs=[run(q,'GameLoop')[0]for q in qs];compare(qs,cs)
        delta=cs[1].processorCycles-cs[0].processorCycles
        assert delta==(7 if identity in('chip','dale')else 0),(identity,delta)
        full.append(dict(identity=identity,mode=mode,delta=delta))
    outer=[]
    for identity,mode,caller,prefix in itertools.product(['chip','dale'],[0,1],['CdNewDrawDispatch','DrawAllMetasprites'],[HP(3),HP(3)+T2+COLOR]):
        qs=[fresh(b,identity,mode)for b in(old,new)]
        for q in qs:q.put(DisableScreenFlag=0,NmiDisable=255,VRAM_Buffer1_Offset=len(prefix));q.array('VRAM_Buffer1',list(prefix)+[0])
        cs=[run(q,caller)[0]for q in qs];compare(qs,cs,True,outer=caller=='DrawAllMetasprites')
        outer.append(dict(identity=identity,mode=mode,caller=caller,prefix_bytes=len(prefix),cycles=[c.processorCycles for c in cs],terminal_X=[c.x for c in cs]))
    irqs=[];nmis=[]
    for prefix in [b'',HP(3),HP(3)+T2+COLOR,T2+HP(3),HP(3)+bytes.fromhex('244c0105'),HP(3)+bytes.fromhex('22204724')]:
        q=arena(new,prefix);image,banks=list(q.m),q.m.banks[:]
        reference=clone(new,image,banks);c,trace=run(reference,'CdHud',record=True)
        lo=address(new,'CdQueueHud');hi=lo+int(new['syms']['CdQueueHud']['size'],0)
        keys=sorted({t for t in trace if t[1]==79 and lo<=t[0]<hi})
        for key in keys:
            t=clone(new,image,banks);d,_=run(t,'CdHud',inject=key)
            assert regs(c)==regs(d)and irq_live(t)==irq_live(reference)
            # Separate genuine IRQ's five hardware writes from foreground.
            from cv3_life_gain_controls_v1 import bus
            assert bus(t)==bus(reference)
            io=[(a,v)for i,(a,v)in enumerate(t.m.writes)if i in t.m.irq_indices and a>=8192]
            assert io==[(0x2006,0),(0x5128,0),(0x2005,32),(0x2005,37),(0x2006,132)]
            irqs.append(dict(prefix_bytes=len(prefix),pc=key[0],bank=79))
        reference=clone(new,image,banks);c=nmi_checked(reference,(address(new,'CdHud'),79))
        for key in keys[::max(1,len(keys)//5)]:
            t=clone(new,image,banks);d=nmi_checked(t,key)
            assert regs(c)==regs(d)and live(t)==live(reference)and checked_nmi_buses(t)==checked_nmi_buses(reference)
            nmis.append(dict(prefix_bytes=len(prefix),pc=key[0],bank=79,source_savedY_stores_checked=len(t.m.nmi_snapshot_indices),immediate_RTI_AXYP_SP_PC_banks_SMC_queue_exact=True))
    prior=earned.SHA
    try:
        earned.SHA=NEW
        campaigns=[earned.campaign(new,v,m)for v,m in itertools.product([0,1],[0,1])]
    finally:earned.SHA=prior
    actual=[actual_sequence(old,new,n)for n in [1289,1476]]
    result=dict(passed=True,source_CPU_only=True,native_run=False,parent_sha256=OLD,candidate_sha256=NEW,
        direct_packet_cases=len(cases),representative_direct=direct,maximum_direct_foreground_delta=maximum,
        health_flags_variant_mode_cases=boundaries,original_guard_capacity_cases=guards,full_all37_Main=full,
        full_draw_callers=outer,actual_IRQs=irqs,actual_lag_NMIs=nmis,earned_source_campaigns=campaigns,
        actual_two_packet_reconstructions=actual,new_RAM=0,NMI_changes=0,
        NMI_contract='All final live RAM, immediate RTI and foreground order exact. Complete raw hardware/APU/other source RAM store order exact. Only bank38 CB05 STY XgLzSavedY transient snapshots use their actual input CPU Y contract and equal address/count; old overbroad same-value comparison retained as negative.',
        semantics='Only identical current last-effective queued HP suppresses a new append. Existing data untouched. Any possible NT alias/partial overlap invalidates; unknown/RLE/vertical/native256/malformed retains original append. No persistent cache or stale-reset dependency.',
        limitations='Full assembled source CPU only. Main helper may cost more on nonempty queues; measured costs above are not a native lag-free or deadline/whole-route guarantee. d49f full-route FALSE remains retained.',
        bindings={str(p):sha(p)for p in [Path(__file__),P,P.with_suffix('.dbg'),N,N.with_suffix('.dbg'),
            B/'chip_hud_queue_complete_build.json',R/'tools/audit/chip_hud_queue_controls_v1.py',
            R/'src/chip_dale_health.s',R/'src/chip_dale_dispatch.s',R/'src/reset.s',R/'tools/audit/current_chip_dale_earned_cpu_v1.py']})
    out.write_text(json.dumps(result,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=True,path=str(out),sha256=sha(out),packets=len(cases),boundaries=boundaries,
        full_Main=len(full),outer=len(outer),IRQ=len(irqs),lagNMI=len(nmis),earned_Main=sum(c['GameLoop_calls']for c in campaigns),actual=actual)))


if __name__=='__main__':main()
