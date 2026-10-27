"""Read-only current-code CHR costs, allocation facts and invariant counterexample."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location

D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
C=D/'robot-base-palette-candidate-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:Path(p).write_text(json.dumps(z,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    assert sha(C/'candidate.nes')=='dfbdca24019776262c4388e3ea782fb989e24b8fc0e3cf0bfe0bbb84a9f480ad'
    b=scoped_load(C/'candidate.nes');raw=b['raw'];cases=[]
    for special,hud,upper in itertools.product([0,1],[0,1],[0,1]):
        for entry in['X5PublishChr','BankSwitchCHR']:
            q=Arena(b,1);q.put(NmiDisable=255,ProtoVariant=1)
            q.invoke('X5ClearChrModes')
            q.put(SmChrBank=0);q.invoke('ProtoPublishBody')
            # Actual observed993 logical banks. This is a bound finite state,
            # not a claimed universal legacy-bank invariant.
            q.array('CurrentCHRBank',[0,20,21,22,23,24,25,26,4,5,6,7])
            q.put(SsChrActive=special,SsChrPhysical=113,X5SpecialChrUpper=upper,
                InvHudActive=hud,InvHudPhysical=243,X5HudChrUpper=upper,ReloadCHRBank=1)
            cpu,_=q.invoke(entry)
            stores=[(at,v)for at,v in q.m.writes if 0x5120<=at<=0x5130]
            cases.append(dict(entry=entry,special=special,hud=hud,upper=upper,cycles=cpu.processorCycles,
                regs=[cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp],CHR_IO=stores))
    default=next(x for x in cases if x['entry']=='BankSwitchCHR'and x['special']==x['hud']==x['upper']==0)
    actual=next(x for x in cases if x['entry']=='BankSwitchCHR'and x['special']==0 and x['hud']==1 and x['upper']==0)
    assert default['cycles']==435 and actual['cycles']==426
    q=Arena(b,9);q.put(RlVariant=1,RlPool=0,ProtoVariant=1,NmiDisable=255)
    chain=[]
    for name in['RlPublish','MenuResolveCharacter','Z2MenuPrepare','DrawPlayer_Intermediate']:
        if name=='MenuResolveCharacter':q.set('CrossoverMenuIndex',1)
        cpu,_=q.invoke(name)
        chain.append(dict(entry=name,SelectedCharacter=q.get('SelectedCharacter'),ProtoVariant=q.get('ProtoVariant'),
            X5ChrMode=[q.get('X5ChrMode',i)for i in range(12)],X5WideChrActive=q.get('X5WideChrActive'),cycles=cpu.processorCycles))
    assert chain[-1]['SelectedCharacter']==1 and chain[-1]['X5ChrMode']==[129,0,0,0,0,0,129,129,0,0,0,0]
    seg=b['segs'][b['syms']['X5PublishChr']['seg']]
    assert int(seg['start'],0)==0xa000 and int(seg['size'],0)==0x2b7
    for bank,first,last in[(62,0xa2b7,0xa300),(78,0xac00,0xad00)]:
        lo=16+bank*8192+(first&8191);hi=lo+last-first
        assert raw[lo:hi]==bytes([255])*(hi-lo)
        for g in b['segs'].values():
            if 'ooffs'not in g:continue
            a0=int(g['ooffs'],0);a1=a0+int(g['size'],0)
            assert a1<=lo or a0>=hi,('Compiled segment overlap',g)
    source=C/'source';names=['src/mmc5_expanded.s','src/mmc5.s','src/reset.s','src/protoman_cold.s','src/roll_render.s','src/character_select.s','src/zelda2_link_menu.s','smb1base-mmc5-expanded.cfg']
    put(a.output/'current-code-costs.json',cases);put(a.output/'compiled-transition-counterexample.json',chain)
    put(a.output/'proposal-only.json',dict(implementation=False,allocation=False,
        unguarded_selectedMega_only_invariant_closed=False,
        required_admission='SelectedCharacter==1 AND no negative bit inX5ChrMode1..11. Mode0 remains fulloriginaldirect/legacylogic; special4/HUD8 keep overrideupper andphysicalvalues.',
        guarded_sameA_tail_gate=dict(physical_bank=62,start='A2B7',end_exclusive='A300',available_verifiedFF_bytes=73,
            proposal_opcode_bytes=dict(owner_and11modeguard=42,Cmap_restore_bridge=25,literalfallback_LDAmode0_JMPresume=6),
            proposed_total_bytes=73,hook='Replace onlyoriginal3B LDAmode0 withJMPgate; fallbackexecutesgenuineLDAmode0 thenJMPoldnextinstruction, avoiding recursion/fakealias.',
            reserved_held_Chip_from_A300_untouched=True),
        proposed_fast_body=dict(physical_load_bank=78,load_address='AC00',true_C_run_alias='CC00',verified_currentFF_bytes=256,
            estimated_body_bytes_at_most=224,current_linker_has_no_overlap=True,
            external_future_reservation_closure_verified=False,
            proposed_linker_route='Source-declaredsplit ofbank78 memory atAC00/AD00 plusrun-onlyC alias; not implemented/allocated. Existing62/94Chip data and78A500..A698 adapter reservation remainuntouched.'),
        finite_instruction_budget_not_assembled=dict(actual_original_core_cycles=actual['cycles']-53,
            actual_original_full_CHR_cycles=actual['cycles'],estimated_fast_body=213,
            unchanged_outer_entry=9,tail_jump=3,owner_mode_admission=54,Cbridge=45,
            estimated_new_core=324,estimated_net_saving=49,
            original_other_owner_wide_overhead=15,original_legacy_wide0_overhead=0,
            guarded_rejected_Mega_stale_modes_overhead=61,
            note='Manualopcodebudgetonly; exactnewlayout/pagepenalties/ABI needfutureassembledproof. Not a measurednewcandidate ornativegain.'),
        ABI_and_interrupt_requirements=['GuardusesEOR/ORA soC/V/D/I retained; finalA/Y/P andall512xvalues/order matchoriginal, intentionalredundant5130zero stores omitted only.',
            'CbridgepublishesCurrentBankC/hardwaretogether andrestoresboth. Cfastbodyexecution cannotuseA-bank self-switch. No sharedfarcallSMC orRAMborrow.',
            'BridgeusesXtemporarily; actualresidentSwitchAreaCHR immediatelyTAX andBankSwitch clearsX0, soverifywholecaller ratherthanfalseX5helperXidentity.',
            'RegularNMIexecutesCHRbeforepostDMA CLI incurrent3b; lagguestNMIkeepsCHR. TrueNMI/IRQ/DMCandwriteboundary qualification stillrequired.',
            'Modeguard avoidsfalsecrossfamilyinvariant. Main privatelyupdates beforepublication; no hardcodedlegacyCurrentCHRBank constants permitted.'],
        suitability='Not sufficientalone: estimated49<actual993155cycledeadline distance, adds15foreignwidecycles and61staleMega fallbackcycles. No implementationrecommendedasstandalone993repair. Realqueuebackpressure oranotherprovencheapersameeventwork path needed.'))
    refs={str(source/n):sha(source/n)for n in names}
    put(a.output/'source-bindings.json',refs)
    put(a.output/'proof.json',dict(readonly_feasibility_complete=True,native_run=False,implementation=False,allocation=False,
        ROM_sha256=sha(C/'candidate.nes'),actual_existing_original_code_cases=len(cases),actual_default_CHR435=True,actual_HUDactive_CHR426=True,
        universal_selectedMega_onlyMode0_invariant_refuted_by_compiled_chain=True,
        current_X5_PUBLISH=dict(bank=62,start='A000',end_exclusive='A2B7',bytes=695),
        prefix73FF_current_segment_unallocated_before_reservedChip_A300=True,
        bank78_AC00_256FF_current_segment_unallocated=True,no_external_future_reservation_or_allocation_claim=True,
        proposal_is_not_enough_to_recover_actual993_epoch=True,no_hardcoded_mode_or_legacy_bank_admission=True,
        costs_sha256=sha(a.output/'current-code-costs.json'),counterexample_sha256=sha(a.output/'compiled-transition-counterexample.json'),
        proposal_sha256=sha(a.output/'proposal-only.json'),source_bindings_sha256=sha(a.output/'source-bindings.json'),tool_sha256=sha(__file__),
        limits='Compiledoldsourcecalls only. Legal-shapedcachedProto-afterRollmenu chain refutes optimizationpremise, not a newnativecorruptionverdict. No newfastpath compiled; manualcycle/sizeproposalrequiresfuturebuild/ABI/interruption/currentlayoutreview. No code/default/settings/Git/native changes.'))
    print(json.dumps(dict(proof=str(a.output/'proof.json'),sha256=sha(a.output/'proof.json'),actual435=default['cycles'],actual426=actual['cycles'],proposed_net_saving_unproved=49),indent=2))


if __name__=='__main__':main()
