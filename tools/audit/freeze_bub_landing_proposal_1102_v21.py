"""Freeze the measured three-span private landing proposal, without a ROM."""
import json
from pathlib import Path
import measure_bub_landing_1102_v21 as L

O=L.O;R=L.R;P=L.P

def main():
    old,new,q,route=L.bundle()
    proofs=[O/'landing-v21-CPU.json',O/'landing-v21-transport-CPU.json']
    for path in proofs:
        a=json.loads(path.read_text());assert a['passed']and a['base_ROM_sha256']==L.PIN
        for rel,digest in a['bindings'].items():assert P.sha((R/rel).read_bytes())==digest,rel
    patches=[]
    for page in[301,305,337,362,363,440,819,666,441]:
        at=1048592+page*1024;a=old['raw'][at:at+1024];b=new['raw'][at:at+1024]
        if a!=b:patches.append(dict(offset=at,old=a.hex(),new=b.hex(),role='Existing Bub owned carrier'+str(page),changed_bytes=sum(x!=y for x,y in zip(a,b))))
    at=q['cookie_offset'];a=old['raw'][at:at+16];b=new['raw'][at:at+16]
    assert a!=b;patches.append(dict(offset=at,old=a.hex(),new=b.hex(),role='Existing complete BB ownercookie only; allmanagerinstructions/Excookie/retireoperand exact',changed_bytes=sum(x!=y for x,y in zip(a,b))))
    legal={i for z in patches for i in range(z['offset'],z['offset']+len(bytes.fromhex(z['new'])))}
    actual=[i for i,(x,y)in enumerate(zip(old['raw'],new['raw']))if x!=y]
    assert set(actual)<=legal and len(patches)==3
    files=[Path(__file__),R/'tools/audit/measure_bub_landing_1102_v21.py',R/'tools/audit/check_bub_landing_1102_v21.py',R/'tools/audit/check_bub_landing_transport_1102_v21.py',
           O/'landing-v21-layout.json',O/'landing-v21-image.bin',O/'landing-v21-helper.chr',*proofs,O/'stair-route-v20-CPU.json']
    q=dict(passed=True,proposal_only=True,private_candidate_grant_pending=True,ROM_written=False,native=False,
        base_ROM_sha256=L.PIN,expected_candidate_sha256=P.sha(new['raw']),actual_changed_bytes=len(actual),patches=patches,
        only_original_landing_reset_adaptation=True,original5434_source_bytes_exact=True,shared_resident_instruction_bytes_exact=True,
        menu_Metal_Arthur_Thomas_Ex_Shinobi_WWF_exact=True,new_RAM_bytes=0,new_physical_pages=0,new_resident_bytes=0,
        funding=dict(private_added=18,private_dead_telemetry_removed=10,existing_measured_spare_used=8,code_end='BFE0',code_header_start='BFE0'),
        CPU_scope='Bothidentities actualnative16pxstairs/43pxnormaljumps; originalD41C16resetdifferentials;900flatmovementMaincoordinatepairs;18air/injuryrejects;9rowcold/readbackfault/warm;256rawauthparity;32completeheaderpoisons;13actualIRQ+13busyNMIcuts. Nativecontroller/fullstage/finalgrant pending.',
        files={str(p.relative_to(R)):dict(SHA256=P.sha(p.read_bytes()),bytes=p.stat().st_size)for p in files})
    target=O/'landing-v21-proposal.json';target.write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:v for k,v in q.items()if k not in['files','patches']}));print('manifest_SHA256='+P.sha(target.read_bytes()))

if __name__=='__main__':main()
