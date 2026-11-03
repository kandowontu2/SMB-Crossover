"""Rebase granted-only Prince in memory onto exact five-patch Sunny nightly."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prepare_prince_current_manifest_1102_v51 as P
O=P.O;A=P.A
BASE=R/'build/sunny-growth-prelude-1102-v9/candidate.nes'
PIN='16a9de64b18370a03885ff503141fc08edd25f3bd026d480854a1754efa1490b'
RECEIPT=R/'docs/qa/checkpoints/2026-11-02/sunny-palette-v9/receipt.json'
sha=lambda b:hashlib.sha256(b).hexdigest()


def bundle():
 old,prior,patches,details=P.bundle();raw=BASE.read_bytes();assert sha(raw)==PIN
 receipt=json.loads(RECEIPT.read_text());assert receipt['passed']and receipt['installed']and receipt['exact_delta_reconstruction']
 assert receipt['base_ROM_SHA256']==P.PIN and receipt['ROM_sha256']==PIN and len(receipt['patches'])==5
 reconstruct=bytearray(old['raw']);sunny=set();writes={i for p in patches for i in range(p['file_offset'],p['file_offset']+p['bytes'])}
 rows=[]
 for patch in receipt['patches']:
  at=patch['offset'];pre=bytes.fromhex(patch['old']);blob=bytes.fromhex(patch['new']);assert len(pre)==len(blob)
  extent=set(range(at,at+len(blob)));assert not extent&sunny and not extent&writes,('Sunny/Prince write overlap',at)
  assert reconstruct[at:at+len(pre)]==pre
  reconstruct[at:at+len(blob)]=blob;sunny|=extent
  rows.append(dict(file_offset=at,bytes=len(blob),old_hex=pre.hex(),new_hex=blob.hex(),old_SHA256=sha(pre),new_SHA256=sha(blob)))
 assert bytes(reconstruct)==raw,('Sunny is not exact published five-patch delta',sha(reconstruct))
 post=bytearray(raw)
 for patch in patches:
  at=patch['file_offset'];pre=bytes.fromhex(patch['old_hex']);blob=bytes.fromhex(patch['new_hex'])
  assert raw[at:at+len(pre)]==pre,('Prince current preimage drift',at)
  post[at:at+len(blob)]=blob
 for row in rows:
  at=row['file_offset'];blob=bytes.fromhex(row['new_hex']);assert post[at:at+len(blob)]==blob
 for at,length in details['all55_Bub_event_spans_retained']:assert post[at:at+length]==raw[at:at+length]
 changed={i for i,(a,z)in enumerate(zip(raw,post))if a!=z};assert changed<=writes
 # The only differences from the already qualified Prince image are precisely
 # the same five Sunny patches, including its palette producer carry branch.
 expected=bytearray(prior['raw'])
 for row in rows:
  at=row['file_offset'];pre=bytes.fromhex(row['old_hex']);blob=bytes.fromhex(row['new_hex']);assert expected[at:at+len(pre)]==pre;expected[at:at+len(blob)]=blob
 assert bytes(expected)==bytes(post)
 details=dict(details,previous_qualified_Prince_memory_SHA256=sha(prior['raw']),sunny_five_exact_extents=rows,sunny_write_extent_bytes=len(sunny),sunny_extents_disjoint_all_Prince_write_extents=True,prior_current_inherited_bytes_retained=details['current_inherited_bytes_retained'],current_inherited_bytes_retained=details['current_inherited_bytes_retained']+sum(a!=z for a,z in zip(old['raw'],raw)),Sunny_palette_gate_and_local_C_skip_ABI_preserved=True,unchanged_foreign_CPU_receipt='current-foreign-CPU-v52.json',new_changed_bytes=len(changed))
 current=dict(old,raw=raw)
 return current,dict(current,raw=bytes(post)),patches,details


def main():
 base,new,patches,details=bundle()
 q=dict(status='PRIVATE_GRANTED_ONLY_SOURCE_REBASE_NO_NATIVE_ADMISSION',passed=True,ROM_written=False,installed=False,base=BASE.relative_to(R).as_posix(),base_SHA256=PIN,expected_memory_only_SHA256=sha(new['raw']),patches=patches,details=details,scope='Exact current Sunny five-patch rebase of granted v47/v51 Prince image only. No C780 audio or v49 collision proposal included. Sunny palette gate, local carry skip and padding unchanged. Prior complete foreign CPU proof retained by identical Prince bytes and exact disjoint Sunny delta; actual current shared-owner/cold/Fresh/scene/ISR qualification remains separate.',bindings={p.relative_to(R).as_posix():sha(p.read_bytes())for p in [Path(__file__),BASE,RECEIPT,O/'current-manifest-v51.json',O/'current-foreign-CPU-v52.json',O/'current-services-CPU-v53.json',R/'docs/qa/allocations/prince-battle-lifetime-1102-v46.json',R/'docs/qa/allocations/prince-shared-successor-1102-v30.json']})
 (O/'sunny-rebase-manifest-v54.json').write_text(json.dumps(q,indent=2)+'\n')
 print(json.dumps({k:v for k,v in q.items()if k not in ['patches','bindings','details']}));print(json.dumps(details))


if __name__=='__main__':main()
