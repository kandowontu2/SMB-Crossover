"""Check exact1966 frontend composition in memory and freeze native test plans.

This proposal writes no ROM, executable packet, menu-admission byte or backend
asset. A final composer must consume the backend owner's flattened exact grant
manifest and a separate root native-candidate grant before it can emit a ROM.
"""
from pathlib import Path
import copy,hashlib,json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from prepare_selected_native_packet_v1 import sha
import prepare_bub_menu_qualification_1102_v2 as N

O=R/'build/bub-menu-candidate-1102-v2'
BASE=R/'build/wwf-death-1102-v2/candidate.nes'
PARENT=R/'build/metal-reservation-1102-v42/candidate.nes'
PIN='1966a4883a888a5e62f90c4d3e96d25ecf028ddd7d714214727793418d633243'
GATE=16+66*8192+0xd64

def fold_patches(base,patches):
    """Exact preimages and disjoint ownership; used by the eventual composer."""
    out=bytearray(base);claimed={};changed=set()
    for row in patches:
        at=row['offset'];old=bytes.fromhex(row['old']);new=bytes.fromhex(row['new'])
        assert len(old)==len(new)>0 and 16<=at<=len(base)-len(old),row
        assert base[at:at+len(old)]==old,('preimage',at,row.get('role'))
        for i,v in enumerate(new,at):
            assert i not in claimed,('overlapping typed patch ownership',i)
            claimed[i]=v
            if base[i]!=v:changed.add(i)
        out[at:at+len(new)]=new
    assert bytes(out[:16])==base[:16] and len(out)==len(base)
    assert all(a==b or i in changed for i,(a,b)in enumerate(zip(base,out)))
    return bytes(out),claimed,changed

def control_plan(identity):
    # These are actual source controls and measured Main epochs. The first
    # qualification stays near the native spawn, before the first enemy.
    return dict(identity=identity,source_controls=dict(A='original jump/held-A bubble ride',B='original bubbles',Left_Right='original movement'),
        phases=[dict(name='idle',Main_updates=60,buttons=[],assertion='No horizontal drift; authenticated same identity/ready, lives unchanged'),
                dict(name='right',Main_updates=24,buttons=['right'],assertion='World X increases from actual source updates'),
                dict(name='left',Main_updates=24,buttons=['left'],assertion='World X decreases without native position writes'),
                dict(name='jump',Main_updates=80,buttons=['a'],hold_updates=40,assertion='Actual source ascent reaches43px from flat support, then native grounded landing'),
                dict(name='bubble',Main_updates=50,buttons=['b'],hold_updates=6,assertion='A real source-owned bubble slot activates; original shot cooldown advances'),
                dict(name='rest',Main_updates=40,buttons=[],assertion='Lives retained; stable native support and source state')],
        Main_epoch_guard='FrameCounter advances once per observed source epoch; no reset admitted in this stationary1-1 run',
        hardware_assertions=['Body CHR is physical441, source odd tiles1..49 only; source packet art reads at most799',
            'Actual PPUpalette is Bub2A/26/30 or Bob2C/23/30; native queued HUD/name packet matches admitted identity',
            'ObjectMetasprite zero header/SmPosePtr and OAM alignment follow actual backend helper ABI',
            'Fresh writes C300 selected identity and C304A7 only while RAM2 bankC=2; active GameEngineSubroutine8'],
        screenshots=['selected-owner','cold-active-owner','source-jump','source-bubble'],
        maximum_PNGs=4,maximum_physical_frames=4200,wall_timeout_seconds=210,
        controller_only=True,terrain_or_full_stage_claim=False,
        failure_preservation='Every terminal run remains immutable; successor uses a distinct packet name')

def main():
    assert sha(BASE)==PIN
    frozen=json.loads((O/'frontend-current-freeze-v3.json').read_text())
    assert sha(R/frozen['archive'])==frozen['archive_SHA256']
    for name,digest in frozen['bindings'].items():assert sha(R/name)==digest,name
    grant=R/'docs/qa/allocations/roster-rebase-1102-v4.json';rebase=json.loads(grant.read_text())
    assert rebase['granted'] and rebase['successor_ROM_SHA256']==PIN
    old=PARENT.read_bytes();base=BASE.read_bytes()
    delta=rebase['only_patch'];at=delta['file_offset'];before=bytes.fromhex(delta['old']);after=bytes.fromhex(delta['new'])
    assert old[at:at+3]==before and base[at:at+3]==after
    assert len(old)==len(base) and [i for i,(a,b)in enumerate(zip(old,base))if a!=b]==list(range(at,at+3))
    proposal=R/'build/bub-menu-integration-1102-v1/controls-proposal.json'
    patches=json.loads(proposal.read_text())['all_patches']
    prospective,owned,changed=fold_patches(base,patches)
    assert len(changed)==1249 and not set(range(at,at+3))&set(owned)
    assert prospective[at:at+3]==after and prospective[GATE]==0x38
    prior=(O/'candidate.nes').read_bytes()
    assert sha(O/'candidate.nes')==frozen['ROM_SHA256']
    assert [i for i,(a,b)in enumerate(zip(prior,prospective))if a!=b]==list(range(at,at+3))
    # Exercise the guard itself: a changed preimage and an overlapping owner
    # must be rejected before the future composer can write anything.
    for rows in [[dict(patches[0],old='ff'*len(bytes.fromhex(patches[0]['old'])))],[patches[0],patches[0]]]:
        try:fold_patches(base,rows)
        except AssertionError:pass
        else:raise AssertionError('Invalid exact ownership fixture accepted')
    ordered=O/'ordered-input-v3/native-menu-plans.json'
    plans=json.loads(ordered.read_text())['plans']
    cold={k:copy.deepcopy(plans[k])for k in['bub-start','bob-start','bt-start','cf-start']}
    for mode,identity in [('bub-start',0),('bob-start',1)]:
        p=cold[mode];assert p['launch']['bob']==identity and p['steps'][-1]['kind']=='launch'
        assert p['launch']['groups']==identity*128
        p['gameplay_controls']=control_plan(identity)
        p['maxFrames']=4200;p['scope']='Actual cold menu simultaneous Select/confirm, owner authentication, source controls and hardware art. No full-stage or delivery claim.'
    ex=R/'build/excitebike-pose-1101-v3/native5/controller.lua'
    extext=ex.read_text()
    assert 'local phases='in extext and "{'prepare',40,65}"in extext and 'source_color_calls'in extext
    for mode,p in cold.items():
        assert p['launch']['groups']in[0,128,32,24]
        assert p['steps'][-1]['keys'] in[['select','a'],['select','start']]
    document=dict(passed=True,source_plan_only=True,ROM_written=False,packet_prepared=False,native=False,installed=False,
        base_ROM_SHA256=PIN,frontend_changed_bytes=1249,frontend_patch_records=len(patches),
        memory_only_frontend_plus_WWF_SHA256=hashlib.sha256(prospective).hexdigest(),
        WWF_exact3B_preserved=True,all_other_current_bytes_preserved=True,gate_still_SEC=True,
        invalid_preimage_and_overlap_rejected=True,
        composition_contract=dict(required_backend_base=PIN,flattened_backend_rows=['offset','old','new','role','grant'],
            required_backend_bindings='Every emitted backend blob, source recipe, finite-closure receipt and formal grant has an exact SHA256',
            backend_assets_read_only=True,backend_frontend_byte_overlap_forbidden=True,
            gate_AD64='Preserve SEC until exact root native-candidate grant separately approves owned CLC rebind',
            preserve_ranges='Every byte outside the exact union of granted frontend/backend/gate rows remains identical to1966, including Metal/Arthur/WWF/Ex cookies',
            debug='Complete native-importable segment metadata and minimal globals; explicit L/B controller symbols; no synthetic incomplete segment records',
            no_automatic_admission_or_delivery=True),
        pending=['Final1966 backend flattened patch/grant/binding manifest','Root common routing/contact/Sh ports and native-candidate grant','Exact source-address rebind of controls/hardware observations to final compiled backend'],
        native_plans=cold,
        existing_Ex_regression=dict(controller=ex.relative_to(R).as_posix(),SHA256=sha(ex),
            action='Rebind unchanged native5 controller to final combined ROM with explicit original globals and retained source callback addresses',
            assertions='Idle/throttle/coast/reverse/rest, source61px backlean jump/landing, CHR736..739, palette/HUD/alignedOAM, no life loss',
            wall_timeout_seconds=150,maximum_PNGs=3,full_stage_claim=False),
        ordering=['Cold Bub/Bob source controls before extended terrain controller',
            'Old BT/CF simultaneous Select+confirm verifies actual P1 restore queue before native owner launch',
            'Excitebike unchanged native5 validates the rewritten shared loader/dispatch seam'],
        helpers_added=False,root_owns_Mesen_install_Git=True,
        bindings={p.relative_to(R).as_posix():sha(p)for p in[Path(__file__),BASE,PARENT,grant,proposal,ordered,ex,O/'frontend-current-freeze-v3.json',O/'candidate.nes']})
    dest=O/'combined-front-plan-v1.json';assert not dest.exists(),'Frozen proposal is immutable'
    dest.write_text(json.dumps(document,indent=2)+'\n')
    files=[p for p in O.rglob('*')if p.is_file()]
    assert sum(p.stat().st_size for p in files)<32000000 and len(files)<=128
    print(json.dumps(dict(passed=True,ROM_written=False,frontend_bytes=1249,WWF3B_preserved=True,
        proposed_modes=list(cold)+['ex-native5'],bytes=sum(p.stat().st_size for p in files),files=len(files))))

if __name__=='__main__':main()
