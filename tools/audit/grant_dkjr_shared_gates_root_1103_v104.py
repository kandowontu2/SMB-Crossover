"""Approve only the measured DK Jr bbox and rare-selector source spans."""
import json
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/dkjr-shared-gates-root-1103-v104'
D=R/'docs/qa/allocations/dkjr-shared-gates-1103-v104.json'
PIN='cf7f157aa39493149b24039c190f09244ce68bc47f0a87f06f01adb47a2c70dd'
def main():
    O.mkdir(exist_ok=True);root=R/'build/dkjr-native-source-1102-v2';proofs=[root/n for n in['native-bbox-v66-CPU.json','native-bbox-v69-direct.json','native-bbox-v69-nested.json','native-rare-gate-v71.json','native-bbox-current-foreign-v73.json']]
    receipts=[]
    for path in proofs:
        q=json.loads(path.read_text());assert q['passed'],path
        for name,h in q.get('bindings',{}).items():assert sha(R/name)==h,name
        receipts.append(q)
    rare,foreign=receipts[-2:];assert rare['parent_ROM_SHA256']==foreign['parent_ROM_SHA256']==PIN
    assert rare['total_cases']==131072 and rare['exact_foreign_target_AXYP_SP_cases']==130560 and rare['intended_raw40_route_cases']==512
    assert foreign['positive_foreign_fullstate_cases']==144 and foreign['positive_owners']==[36,37,38,39]
    assert foreign['positive_current_owner_memory_SHA256']=='cba497aabf91ccb357a9392a4407f261c8fd33a66032ae9d7b2e1ba790ef490d'
    patches=[];raw=(R/'build/bub-initial-tier-1103-v87/bub-initial-tier.nes').read_bytes();assert sha(R/'build/bub-initial-tier-1103-v87/bub-initial-tier.nes')==PIN
    for proposal in[foreign['proposal'],rare['proposal']]:
        p={k:proposal[k]for k in['physical_PRG','CPU_half_open','file_offset']};p.update(old=proposal['old_hex'],new=proposal['new_hex'])
        assert len(bytes.fromhex(p['old']))==len(bytes.fromhex(p['new']))==p['CPU_half_open'][1]-p['CPU_half_open'][0]
        assert raw[p['file_offset']:p['file_offset']+len(bytes.fromhex(p['old']))]==bytes.fromhex(p['old'])
        patches.append(p)
    assert[len(bytes.fromhex(p['new']))for p in patches]==[37,1]
    assert raw[16+65*8192+0xdfd]==96
    grant=dict(status='APPROVED_PRIVATE_SOURCE_COMPOSITION_AND_NATIVE_TEST_ONLY',granted=True,owner='Donkey Kong Jr. raw40',reviewed_base_SHA256=PIN,current_positive_owner_memory_SHA256=foreign['positive_current_owner_memory_SHA256'],approved_exact_patches=patches,new_allocated_bytes=0,new_RAM_bytes=0,installation_authorized=False,menu_admission_authorized=False,review='Root inspected the actual37B PHP/selected36-or39/40/PLP source-funded gate, preservedADFD RTS and genuine HuFullBox/fallback path. All other selectors preserve actual native target/AXYP/SP and current authenticated Sh/Ex/Prince/Bub source/private/liveStack/SMC/maps. The1B current rare-classifier threshold extends only40; all130560foreign cases remain exact. Own bbox source/IRQ/FF/nested proofs remain bound separately. No new shared tail or state is allocated.',conditions=['Use only these37+1bytes; preserveADFD RTS, all downstream PCs, current Bub event gate, menu and owner payloads.','The new40 route may call only complete authenticated raw40 services; unimplemented rows must remain explicit rejects until implemented and proven.','Current payload-derived cookie/fullcold/readback/retirement/foreign transitions/actual native ingress/IRQ and controller gameplay remain required before installation.','No menu unlock, nightly installation, broader native collision manager change or platform placement is authorized by this internal span grant.'],bindings={f.relative_to(R).as_posix():sha(f)for f in[Path(__file__),*proofs,R/'docs/qa/allocations/joint-native-rare-gate-1102-v70.json',R/'docs/qa/checkpoints/2026-11-03/dkjr-items-bounds-v70/receipt.json']})
    D.write_text(json.dumps(grant,indent=2)+'\n');(O/'receipt.json').write_text(json.dumps(grant,indent=2)+'\n');print(json.dumps({k:v for k,v in grant.items()if k not in['bindings','review']}))
if __name__=='__main__':main()
