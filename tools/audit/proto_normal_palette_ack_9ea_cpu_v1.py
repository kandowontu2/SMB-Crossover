"""Finite compiled caller/queue/IRQ controls for the three-byte Proto cache fix."""
from pathlib import Path
import itertools,json,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
from current_mega_arsenal_prepare_v1 import EXPECTED,sha,campaign
from link_pit_rygar_sophia_audit_cpu import scoped_load
from robots_weapon_cpu_v1 import Arena
from check_tmnt_render_oa import address,location
from proto_palette_coalesce_controls_v1 import run,ppu

P=R/'build/bill_early_cache.nes';N=R/'build/proto_normal_palette_ack_9ea.nes'
NEW='cb8fce744c3f95aaf11e1e52b605535dce8a301bb7a7ca5d7a73c186c79ebc62'

def main():
    assert sha(P)==EXPECTED and sha(N)==NEW;old,new=scoped_load(P),scoped_load(N)
    diagnostic=R/'build/current-9ea-proto-arsenal-diagnostic-v2/native/handoff-diagnostic.jsonl'
    data=[json.loads(x) for x in diagnostic.read_text().splitlines()]
    failed=[x for x in data if x['event']=='PPUMASK-before-original-assert' and x.get('value',0)&24 and x['ppu.scanline']==1][-1]
    entry=[x for x in data if x['event']=='nmi-entry' and x['nmi_sequence']==failed['nmi_sequence']][0]
    observed=bytes.fromhex(entry['queue1'])[:entry['offset1']+1];assert len(observed)==54
    assert observed[47:]==bytes.fromhex('3f11030f161000')
    prefix=observed[:28]
    def fresh(b,state=None,payload=prefix):
        state=state or{};q=Arena(b,state.get('SelectedCharacter',1),proto=state.get('ProtoVariant',1))
        q.put(DisableScreenFlag=0,OperMode_Task=3,PlayerStatus=1,AreaType=1,CurrentPlayer=0,
              SsLastPalette=0,MmLastPalette=0,Player_SprAttrib=3,Player_Rel_XPos=64,Player_X_Position=64,
              Player_PageLoc=0,ScreenLeft_PageLoc=0,Player_Y_Position=176,Player_State=0)
        q.put(**{k:v for k,v in state.items()if k!='selected'})
        q.set('InvSelected',state.get('selected',0),1)
        q.array('VRAM_Buffer1',list(payload)+[0]);q.set('VRAM_Buffer1_Offset',len(payload));return q
    def regs(c):return c.a,c.x,c.y,c.p&207,c.sp
    def compare(qs,cs,allowed=()):
        assert regs(cs[0])==regs(cs[1]) and qs[0].m.banks==qs[1].m.banks
        differences=[i for i in range(0x8000) if qs[0].m[i]!=qs[1].m[i] and i not in allowed]
        assert not differences,[(hex(i),qs[0].m[i],qs[1].m[i]) for i in differences[:12]]
    rows=[]
    states=[dict(ProtoVariant=p,PlayerStatus=t,selected=s,MmLastPalette=cache)
            for p,t,s,cache in itertools.product([0,1],[0,1,2],[0,1,8],[0,1,5])]
    states += [{k:v} for k,v in [('GuestPowerupActive',1),('StarInvincibleTimer',1),('MmChargeFrames',1),('MmChargeFrames',33),('MmChargeFrames',48),('MmChargeFrames',87)]]
    states += [dict(SelectedCharacter=c,ProtoVariant=0) for c in [0,2,3,4,5,9,11,15,18,19]]
    for state,flags in itertools.product(states,[0x20,0x21,0x60,0xa2,0xef]):
        qs=[fresh(b,state) for b in [old,new]];cs=[run(q,'X5GetPlayerColors',flags=flags)[0] for q in qs]
        compare(qs,cs,{address(old,'MmLastPalette')})
        eligible=(state.get('SelectedCharacter',1)==1 and state.get('ProtoVariant',1)==1 and
                  state.get('PlayerStatus',1)<2 and not state.get('selected',0) and
                  not any(state.get(k,0) for k in ['GuestPowerupActive','StarInvincibleTimer','MmChargeFrames']))
        assert qs[1].get('MmLastPalette')==(1 if eligible else qs[0].get('MmLastPalette'))
        assert qs[0].m.writes==[(a,v) for a,v in qs[1].m.writes if a!=address(old,'MmLastPalette')],state
        delta=cs[1].processorCycles-cs[0].processorCycles;assert delta==(4 if eligible else 0),(state,delta)
        rows.append(dict(state=state,flags=flags,ack=eligible,delta=delta))
    # Direct malformed/special-owner controls preserve all output state and
    # never acknowledge a header/colors/extent that the source rejects.
    negatives=[]
    good=observed[:47]
    for i in [40,41,42,44,45,46,47]:
        payload=bytearray(good+b'\0');payload[i]^=1
        qs=[fresh(b,payload=payload[:-1]) for b in [old,new]]
        for q in qs:q.set('VRAM_Buffer1',payload[47],47)
        cs=[run(q,'ProtoFixAndAcknowledgePalette')[0] for q in qs]
        compare(qs,cs);assert qs[1].get('MmLastPalette')==0
        negatives.append(dict(modified_offset=i,all_RAM_AXYP_SP_banks_exact=True))
    # Genuine observed producer chronology:28HUD bytes -> complete19-color
    # legacy caller -> graphics palette/pose. New cache removes no live data.
    route=[];qs=[fresh(b) for b in [old,new]]
    for q in qs:
        a,_=run(q,'X5GetPlayerColors');mid=bytes(q.get('VRAM_Buffer1',i) for i in range(q.get('VRAM_Buffer1_Offset')+1))
        c,_=run(q,'MegaManGraphics');packet=bytes(q.get('VRAM_Buffer1',i) for i in range(q.get('VRAM_Buffer1_Offset')+1))
        route.append(dict(after_GetColors_hex=mid.hex(),queue_hex=packet.hex(),queue_bytes=len(packet)-1,GetColors_cycles=a.processorCycles,Graphics_cycles=c.processorCycles))
    assert bytes.fromhex(route[0]['queue_hex'])==observed
    assert route[1]['queue_bytes']==47 and bytes.fromhex(route[1]['queue_hex'])==observed[:47]+b'\0'
    # Full Graphics final live state must agree; only the genuinely removed
    # queue suffix and its source parser's terminal index may differ. Actual
    # GameLoop campaigns below separately prove completed caller semantics.
    consumers=[]
    for b,route_row in zip([old,new],route):
        q=fresh(b,payload=bytes.fromhex(route_row['queue_hex'])[:-1]);p=address(b,'VRAM_Buffer1')
        q.put(NmiR0=p&255,NmiR1=p>>8)
        q.m.page(2,(location(b,'FastNmiVramCopy')-16)//8192)
        c,_=run(q,'UpdateScreen');image,bus=ppu(q.m.writes)
        consumers.append(dict(cycles=c.processorCycles-6,image=image,bus=bus,PPUDATA_writes=len(bus)))
    assert consumers[0]['image']==consumers[1]['image']
    assert consumers[0]['bus'][:-3]==consumers[1]['bus'] and consumers[0]['bus'][-3:]==[(0x3f11,15),(0x3f12,22),(0x3f13,16)]
    saving=consumers[0]['cycles']-consumers[1]['cycles'];assert saving==152
    # Actual hardware-vector IRQ at every reached helper boundary. Compare
    # complete same-candidate return and all low SRAM/SMC, not a stub IRQ.
    base=fresh(new);run(base,'X5LegacyGetPlayerColors')
    image=list(base.m);banks=base.m.banks[:]
    def again():
        q=Arena(new,1,proto=1);list.__setitem__(q.m,slice(None),image);q.m.banks=banks[:];return q
    q=again();c,trace=run(q,'ProtoFixAndAcknowledgePalette',record=True)
    lo=address(new,'ProtoFixAndAcknowledgePalette');hi=lo+int(new['syms']['ProtoFixAndAcknowledgePalette']['size'],0)
    keys=sorted({x for x in trace if x[1]==66 and lo<=x[0]<hi})
    def stable(q):
        # IRQ leaves dead high stack residues. Low stack/SMC remain live and
        # compare exactly; no entire-page stack exclusion is used.
        # The real IRQ intentionally leaves the PPUADDR write port at its
        # native final split value; verify its ordered native IO below.
        return bytes(q.m[:0x1c0]+q.m[0x200:0x2006]+q.m[0x2007:0x8000]),q.m.banks
    wanted=(regs(c),stable(q));irqs=[]
    for key in keys:
        t=again();cpu,_=run(t,'ProtoFixAndAcknowledgePalette',inject=key)
        assert (regs(cpu),stable(t))==wanted,('IRQ',key)
        live_write=lambda a:not 0x1c0<=a<0x200
        non_irq=[(a,v) for i,(a,v) in enumerate(t.m.writes) if i not in t.m.irq_indices and live_write(a)]
        assert non_irq==[(a,v) for a,v in q.m.writes if live_write(a)]
        io=[(a,v) for i,(a,v) in enumerate(t.m.writes) if i in t.m.irq_indices and a>=0x2000]
        split=base.get('IrqNewScroll');control=base.get('IrqPPUCTRL')
        assert io==[(0x2006,(control&1)<<2),(0x5128,0),(0x2005,32),(0x2005,split),(0x2006,128|(split>>3))],io
        assert t.m[0x2006]==io[-1][1]
        irqs.append(dict(PC=key[0],bank=key[1],IRQ_extra_cycles=cpu.processorCycles-c.processorCycles,native_ordered_IO=io))
    # Current complete earned-arsenal campaigns independently retain all
    # collections/costs/contacts/launches/refills on both identities.
    full=[campaign(new,v) for v in [0,1]]
    assert all(p['passed'] and p['complete_GameLoop_calls']==2195 for p in full)
    for result in full:
        # The reusable campaign's default report constant names its original
        # parent; these executions use the actual new bundle above.
        assert result.pop('ROM_sha256')==EXPECTED
        result['executed_ROM_sha256']=NEW
        result['reused_campaign_original_metadata_constant']=EXPECTED
    # Shared kernel/transfers/CHR bytes are wholly unchanged. A small
    # representative actual CHR caller still must keep full CPU+bus state.
    chr_rows=[]
    for wide,reload in itertools.product([0,1],[0,1]):
        pair=[fresh(b,dict(X5WideChrActive=wide,ReloadCHRBank=reload,InvHudActive=1,InvHudPhysical=243)) for b in [old,new]]
        for q in pair:q.array('CurrentCHRBank',bytes.fromhex(next(x['current_chr'] for x in data if x['event']=='chr-entry' and x['nmi_sequence']==entry['nmi_sequence'])))
        cpus=[run(q,'BankSwitchCHR')[0] for q in pair];compare(pair,cpus);assert pair[0].m.writes==pair[1].m.writes
        chr_rows.append(dict(wide=wide,reload=reload,cycles=cpus[0].processorCycles))
    proof=dict(passed=True,source_CPU_only=True,native_run=False,parent_sha256=EXPECTED,candidate_sha256=NEW,
        complete_GetColors_AXYP_SP_all_RAM_banks_ordered_writes_cases=len(rows),source_cases=rows,
        malformed_ack_negatives=negatives,actual_recorded_packet=observed.hex(),producer_route=route,
        consumer=consumers,actual_UpdateScreen_savings=saving,actual_IRQ=irqs,CHR_callers=chr_rows,
        full_GameLoop_campaigns=full,observed_NMI=dict(entry_cycle=entry['cpu.cycleCount'],enable_cycle=failed['cpu.cycleCount'],
            elapsed=failed['nmi_CPU'],actual_PPU=[failed['ppu.frameCount'],failed['ppu.scanline'],failed['ppu.cycle']],
            original_guard='VBlank241..260 or prerender-1dot<=274',minimum_model_saving_to_guard_CPU=138,
            projected_saving_CPU=152,observed_case_projected_margin_CPU=14,native_remeasurement_required=True),
        limits='No new native/NMI/DMA/DMC/cadence or universal budget certification. Only complete source-caller and actual packet reconstruction; intended deletion of3 superseded palette writes. No emulated timing/deadline/queue guard relaxation.',
        bindings={str(p):sha(p) for p in [Path(__file__),P,P.with_suffix('.dbg'),N,N.with_suffix('.dbg'),R/'src/proto_palette_ack.s',R/'src/megaman_palette.s',R/'src/proto_palette_coalesce.s',R/'src/x5_palette.s',diagnostic,R/'build/proto_normal_palette_ack_9ea_build.json']})
    out=R/'build/proto_normal_palette_ack_9ea_cpu.json';assert not out.exists();out.write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=True,output=str(out),sha256=sha(out),GetColors_cases=len(rows),IRQ_cases=len(irqs),source_GameLoops=sum(x['complete_GameLoop_calls'] for x in full),packet_savings=saving)))

if __name__=='__main__':main()
