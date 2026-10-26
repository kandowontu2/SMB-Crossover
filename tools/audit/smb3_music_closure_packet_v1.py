"""Freeze compact, additive link metadata for original SMB3 dynamic traces."""
from pathlib import Path
import argparse
import csv
import gzip
import hashlib
import io
import json
import shutil

from mike_parodius_music_probe import spans
from py65.devices import mpu6502

ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
expand=lambda rows:{i for a,b in rows for i in range(a,b+1)}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--trace',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--report',type=Path,required=True)
    a=p.parse_args();trace=a.trace.resolve();out=a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True,exist_ok=False)
    proof=json.loads((trace/'proof.json').read_text())
    assert sha(trace/'proof.json')=='fd6d4c2dc248943b225063ce3c1ce3dacb7739221981b10abb4a849ed60f3e9e'
    assert proof['passed'] and proof['source_calls']==216012
    for f,h in proof['dependencies'].items():assert sha(f)==h,f
    closure=json.loads((trace/'dynamic-closure.json').read_text())
    assert sha(trace/'dynamic-closure.json')==proof['dynamic_closure_sha256']
    raw=Path(proof['source']).read_bytes()[128:]
    manifest=json.loads((ROOT/'reference/new-roster-audio/captures-manifest.json').read_text())
    classifications={};cold=set();configs=set();observed_instruction_IO=[]
    for role,r in proof['roles'].items():
        for f,h in r['output_files'].items():assert sha(trace/f)==h,f
        folder=trace/f"{role}-{r['one_based_track']:02d}"
        foot=json.loads((folder/'footprint.json').read_text())
        cold|=expand(foot['cold_zero_read_before_first_write_ranges'])
        configs|={tuple(tuple(x)if isinstance(x,list)else x for x in row)for row in foot['DPCM_configs']}
        # All observed explicit load/RMW absolute bases and pointer targets
        # are checked, closing the old generic Bus's narrower IO counter.
        for q in foot['instruction_rows']:
            if q['mode']in['abs','abx','aby'] and q['mnemonic']not in['STA','STX','STY','JMP','JSR']:
                off=q['physical_PC'];base=raw[off+1]+256*raw[off+2]
                extent=255 if q['mode']in['abx','aby']else 0
                if base<=0x5fff and base+extent>=0x2000:
                    observed_instruction_IO.append([role,q,base,extent])
        assert not any(0x2000<=q[7]<0x6000 for q in foot['indirect_pointer_accesses'])
        m=manifest[f"mario3-{r['one_based_track']:02d}"]
        capture_rows=list(csv.DictReader(io.StringIO(gzip.decompress(Path(m['path']).read_bytes()).decode())))
        n=r['original_native_capture_ordered_prefix_stores']
        row=dict(exact_ordered_prefix_stores=n,remaining_old_capture_stores=len(capture_rows)-n,
                 original_first_divergence=r['first_old_capture_divergence'])
        if n<len(capture_rows):
            row['next_old_capture_rows']=capture_rows[n:n+25]
            row['classification']='SOURCE_WRITES_DIFFER_FROM_OLD_CAPTURE'if r['first_old_capture_divergence']else'OLD_CAPTURE_HAS_EXTRA_TAIL_AFTER_SOURCE_CUE_BECOMES_QUIET'
        else:row['classification']='ALL_OLD_CAPTURE_STORES_MATCH_PREFIX'
        classifications[role]=row
    assert not observed_instruction_IO
    live=(expand(closure['RAM_reads'])|expand(closure['RAM_writes']))-set(range(0x100,0x200))
    ranges=[]
    for lo,hi in closure['required_observed_ROM_ranges']:
        ranges.append(dict(source_payload_first=lo,source_payload_last_inclusive=hi,bytes=hi-lo+1,
                           sha256=hashlib.sha256(raw[lo:hi+1]).hexdigest()))
    metadata=dict(original_NSF_sha256=proof['source_sha256'],source_calls=216012,
                  ordered_original_APU_stores=proof['ordered_original_APU_stores'],
                  source_payload_bytes=len(raw),observed_required_bytes=closure['required_observed_ROM_bytes'],
                  observed_source_ranges=ranges,source_live_RAM_addresses=sorted(live),
                  cold_zero_read_before_first_write_addresses=sorted(cold),
                  actual_indirect_pointer_cell_pairs=sorted({(q[3],q[4])for q in closure['indirect_pointer_accesses']}),
                  actual_indirect_access_bindings=len(closure['indirect_pointer_accesses']),
                  original_DPCM_configs=sorted(map(list,configs)),
                  DPCM_config_columns=['4010','4011','4012','4013','CPU_start','bytes','payload_first','payload_last','original_4KiB_maps'],
                  all_observed_absolute_read_RMW_operand_ranges_and_indirect_targets_exclude_IO=True,
                  old_native_capture_classification=classifications,
                  integration_status='NOT_RELOCATED_LINKED_ALLOCATED_OR_NATIVE_QUALIFIED',
                  keep_all_unobserved_source_payload=True,
                  scope='Dynamic fixed-cold18,000-call-per-role closure only. No universal source/input/71-song reachability or safe byte removal. Preserve original numeric pointers through a later mapped reader, or separately prove every relocation.19 zero-initial RAM dependencies and all source DPCM control/loop bits are retained.')
    (out/'link-inputs.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    tools=out/'tools';tools.mkdir()
    names=['smb3_original_music_closure_v3.py','smb3_original_music_closure_v2.py',
           'smb3_original_music_closure_v1.py.failed.txt','smb3_music_closure_packet_v1.py',
           'mike_parodius_music_probe.py','verify_native_relocation.py']
    for name in names:shutil.copy2(ROOT/'tools/audit'/name,tools/name)
    files=[q for q in trace.rglob('*')if q.is_file()]
    files += list(tools.iterdir())+[out/'link-inputs.json',a.report.resolve(),Path(mpu6502.__file__)]
    receipt=dict(passed=True,source_dynamic_closure_only=True,original_trace_sha256=sha(trace/'proof.json'),
                 source_calls=216012,ordered_original_APU_stores=proof['ordered_original_APU_stores'],
                 role_count=12,live_source_RAM_bytes=len(live),cold_zero_dependencies=len(cold),
                 actual_indirect_pointer_bindings=len(closure['indirect_pointer_accesses']),
                 observed_required_source_ROM_bytes=closure['required_observed_ROM_bytes'],
                 allocations=False,integration=False,native_launch=False,production_game_changes=False,
                 files={str(q):dict(sha256=sha(q),bytes=q.stat().st_size)for q in sorted(files)},
                 direct_original_dependencies=proof['dependencies'],
                 limitations='No full old-native-capture equivalence: all reset/restart/extra tails are retained and explicitly classified. Source golden calls/stores are immutable and complete for the finite cold contract. No payload removal, banking/RAM reservation, clock reduction, sample/voice omission or native performance claim.')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,receipt=str(out/'receipt.json'),sha256=sha(out/'receipt.json'),files=len(files)),indent=2))


if __name__=='__main__':main()
