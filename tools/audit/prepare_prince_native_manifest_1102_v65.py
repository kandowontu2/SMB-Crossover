"""Exact privately granted current Prince image plus native rare gate."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prepare_prince_collision_manifest_1102_v59 as P
O=P.O;A=P.A;BASE=P.BASE;PIN=P.PIN;sha=P.sha


def bundle():
 base,prior,patches,details=P.bundle();proposal=json.loads((O/'native-nr-gate-proposal-v64.json').read_text());assert proposal['passed']and proposal['prior_memory_SHA256']==sha(prior['raw'])
 for path,digest in proposal['bindings'].items():assert sha((R/path).read_bytes())==digest,path
 grant=json.loads((R/'docs/qa/allocations/prince-native-rare-gate-1102-v64.json').read_text());assert grant['status']=='APPROVED_FOR_PRIVATE_SOURCE_COMPOSITION_ONLY'
 post=bytearray(prior['raw']);written={i for p in patches for i in range(p['file_offset'],p['file_offset']+p['bytes'])}
 for p in proposal['patches']:
  at=p['file_offset'];old=bytes.fromhex(p['old_hex']);blob=bytes.fromhex(p['new_hex']);assert post[at:at+len(old)]==old and not written&set(range(at,at+len(blob)));post[at:at+len(blob)]=blob
 assert sha(post)==proposal['expected_memory_only_SHA256']
 return base,dict(base,raw=bytes(post)),patches+proposal['patches'],dict(details,execution_extensions_granted=True,actual_native_rare_gate_granted=True,all_New_Prince_native_ingress_qualification_required=True)


def main():
 base,new,patches,details=bundle();q=dict(passed=True,status='PRIVATELY_GRANTED_SOURCE_IMAGE_NATIVE_QUALIFICATION_PENDING',ROM_written=False,installed=False,base=BASE.relative_to(R).as_posix(),base_SHA256=PIN,expected_memory_only_SHA256=sha(new['raw']),patches=patches,details=details,scope='Exact current16a9 private source image carries original Prince actor/control/world/combat/art, source-derived native policies and root-granted native rare gate. All Sunny/menu/Bub/Thomas bytes retained; no menu admission or native-ready/fullstage/install claim. Actual native ingresses/lifecycle/rendering tests remain required. Original sound/music event latches retained; mixer/mapping remains incomplete.',bindings={p.relative_to(R).as_posix():sha(p.read_bytes())for p in [Path(__file__),BASE,O/'collision-manifest-v59.json',O/'native-nr-gate-proposal-v64.json',R/'docs/qa/allocations/prince-collision-lifetime-1102-v62.json',R/'docs/qa/allocations/prince-native-rare-gate-1102-v64.json']})
 (O/'native-manifest-v65.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['patches','bindings','details']}))


if __name__=='__main__':main()
