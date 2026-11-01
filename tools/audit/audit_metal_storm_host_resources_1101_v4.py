"""Read-only pinned layout evidence and explicitly ungranted Metal resources."""
from pathlib import Path
import hashlib,json,sys,zipfile
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/audit'))
import metal_storm_cpu_1101_v2 as M
OUT=ROOT/'build/metal-storm-host-contract-1101-v4'
HOST=ROOT/'docs/qa/checkpoints/2026-11-01/karnov-menu-health-nightly-v3/source.zip'
INVENTORY=ROOT/'build/karnov-current-resource-audit-1101-v1/inventory.json'
INSTALLED=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    old=json.loads(INVENTORY.read_text());assert old['passed']
    with zipfile.ZipFile(HOST)as z:cfg=z.read('host/candidate.cfg').decode();fm=z.read('host/full_roster_menu.s').decode();nr=z.read('host/new_roster_dispatch.s').decode();union=z.read('host/union.s').decode()
    # Read current installed bytes ONCE; publication may legitimately replace
    # that file after this point. No old ROM/backup is written or retained.
    raw=INSTALLED.read_bytes();installed_sha=hashlib.sha256(raw).hexdigest()
    kernel=list(range(247,251))+list(range(827,831));meta=[831];body=list(range(1019,1024));pages=kernel+meta+body
    assert len(set(pages))==14
    evidence=[]
    for p in pages:
        historical=old['pages'][p];actual=raw[1048592+p*1024:1048592+(p+1)*1024]
        assert historical['owners']==[]and historical['zero']and len(actual)==1024 and not any(actual)
        evidence.append(dict(page=p,old_emission_owners=[],current_preimage_sha256=hashlib.sha256(actual).hexdigest(),zero=True))
    assert'BW_BODY_POST:start=$cec00,size=$1400'in cfg and'CF_CHR_POST:start=$f2400,size=$dc00'in cfg
    assert'::GmOnlyHigh:\n cmp #35'in nr and'cmp #34\n beq KrUnionBank'in union
    # Exact pending block remains a rejection: this component does NOT change
    # source files, name stars, menu readiness or native raw-ID dispatch.
    assert'cpx #11\n bne Groups\n lda FmAlts\n and #2\n beq Ready\n lda #4\n sec\n rts'in fm
    # Original projectile integration is outside the actor span; retain a
    # compact genuine-donor observation rather than inferring units from0C.
    movement=[];maximum_active=0
    for direction in[0,2]:
        c=M.boot()
        for t in range(600):M.frame(c,16 if t in[120,121,300,301,480,481]else 0)
        for t in range(3):M.frame(c,direction)
        for t in range(8):
            before=[(c.memory[0x510+i],c.memory[0x480+i]+256*c.memory[0x498+i])for i in[2,3]]
            M.frame(c,64|direction);maximum_active=max(maximum_active,sum(bool(c.memory[0x510+i])for i in[2,3]))
            for i,(active,x)in zip([2,3],before):
                if active and c.memory[0x510+i]:
                    delta=(c.memory[0x480+i]+256*c.memory[0x498+i]-x+32768)%65536-32768;movement.append(delta)
    assert set(movement)=={-12,12}and maximum_active==2
    q=dict(passed=True,source_layout_only=True,native=False,installed=False,host_admitted=False,installed_read_once_sha256=installed_sha,layout_packet_sha256=sha(HOST),baseline_inventory_ROM=old['candidate'],proposed_raw_owner=35,base_owner_preserved=dict(menu_slot=11,raw=11,name='Sophia',alternate_bit=2),actual_pending_rejection_verified=True,required_native_gates=['FmPending slot11 Cclear only after complete admission','FmResolve cold ROM tail maps11+bit2 to raw35','FmStartRetireFlags then Metal bit2 retention','HuGenericIndex raw35 -> own typed37row service transport','GmOnlyHigh35 ->36 only after complete raw35 capsule exists','cold ROM metadata/colors/name/portrait before any cache opcode','all service and foreground/terrain/render/audio ownership explicit; no legacy raw35 indexing'],conditional_resources=dict(A3=[0xa000,0xbfe0],C2_source=[0xc000,0xc800],C2_host=[0xc800,0xc810],C2_graphics_metadata_proposal=[0xc900,0xc900+1002],full_signatures_C2_C3=[0xdfe0,0xdff0],shared_RAM0_1_untouched=True,foreground_ZP=[3,4],NMI_ZP_never_borrowed=[0,1,2],source_pointer_save=[0xc7fe,0xc7ff]),candidate_static_storage=dict(granted=False,kernel_pages=kernel,metadata_page=meta,body_pages=body,code_loader_requires_scatter=True,original_body_bytes=4608,body_tail_spare_bytes=512,metadata_bytes=1002,metadata_spare_bytes=22,physical_preimages=evidence,limitation='Unemitted/zero evidence and pinned configuration are NOT a resource grant or complete runtime-selector proof. Audit original low-CHR consumers247..250, Bowser824..826 selectors and SMB3PLUS969..1018 selector bounds before changing these14pages. Root must arbitrate other agents and code/audio growth.'),resident_ROM_funding=dict(granted=False,needed='45B cold leaves plus authenticated loader/retirement/typed ingress/ROM-only renderer or shared descriptors',Karnov_ROM29_not_assumed_free=True,preferred='Factor the existing selected-owner loader into a descriptor-based cold ROM service; prove both old Karnov and new owner contexts/SMC/ISR. Otherwise perform a separate genuine source compaction with public-PC preservation.'),source_ports=dict(FF1E='Original EB22 lookup consumes source59/5A,5B/5C etc; return a private flags packet through foreground pointer03/04. Translate SMB metatile semantics; never reinterpret raw metatile IDs.',FF33='Original side/contact response with gravity-dependent masks/order.',FF36='Original slope/support response; host has no original slopes but must preserve flat-floor/ceiling support.',FF3F='Original DA71 normalization uses240-pixel source Y pages; adapter linearization is exhaustively checked.',FF27='Original DCAE begins INC53 and updates source objects/animation. Recover only needed clock and slots2/3; never update SMB enemies with whole donor object loop.',FF39='Banked service and final scene tail; isolate required actor animation effects, no donor scene/VRAM dispatcher.',OTHER='8874 camera/CHR,8BCF platform displacement,9ED7 scripted actor andFF18 scene completion remain typed adaptation boundaries.'),weapons=dict(original_spawn='B05C..B239 is already in unchanged core: heldB, even53 clock, first free slot2/3, original aim/direction/muzzle placement and12px source bullet speed.',state_arrays='Active510+slot, X480/498+slot, Y4B0/4C8+slot, flags540+slot, VX558+slot,VY570+slot, lifetime660+slot; slots2/3 are independent.',remaining='Recover original slot handlers/shot CHR/GravityFire/armor, then native enemy/brick/effects/score/audio and collectible progression. Existing body metadata covers actor0 only.'),scope='No allocation, source edits, mutableO reads, native Mesen, ROM backup or nightly change. This contract records concrete tested source components and explicit future graft/funding boundaries.')
    q['original_projectile_observation']=dict(genuine_donor_CPU=True,native_host=False,maximum_concurrent_slots=maximum_active,world_X_displacements=sorted(set(movement)),active_motion_pairs=len(movement),scope='Original donor reset/NMI, held horizontal B; original projectile object integrator is observed but is not recovered or ported here.')
    q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(M.__file__),M.ROM,HOST,INVENTORY,OUT/'assembly.json',OUT/'CPU-controls.json']}
    (OUT/'host-contract.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k in['passed','installed_read_once_sha256','proposed_raw_owner','actual_pending_rejection_verified','scope']}))
if __name__=='__main__':main()
