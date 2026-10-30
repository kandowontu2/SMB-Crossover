from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2];O=ROOT/'build/arthur-source-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    reports=['source-index.json','kernel-source-proof.json','build-proof.json','cpu-receipt.json','art-source.json',
      'art-8x16-proof.json','arena-build-proof.json','native/original-discovery-v1/manifest.json','native/leaf-arena-v1/manifest.json']
    stale=[]
    for name in reports:
        d=json.loads((O/name).read_text())
        for path,h in d.get('bindings',{}).items():
            if sha(path)!=h:stale.append(path)
        for path,h in d.get('evidence',{}).items():
            if sha(path)!=h:stale.append(path)
    assert not stale,stale
    cpu=json.loads((O/'cpu-receipt.json').read_text());native=json.loads((O/'native/leaf-arena-v1/receipt.json').read_text())
    assert cpu['status'].startswith('PASS_')and native['status'].startswith('PASS_')
    files=[O/n for n in reports]+[O/'REVIEW.md',O/'component.s',O/'native-kernels.s',O/'native-context.inc',
       O/'leaf.cfg',O/'leaf.bin',O/'leaf.lbl',O/'leaf.dbg',O/'arena.s',O/'arena.cfg',O/'arena-art.s',O/'arena.chr',
       O/'arena.nes',O/'arena.lbl',O/'arena.dbg',O/'arthur-original-sprites.chr',O/'arthur-adapted-8x16.chr',
       O/'source-art-contact-sheet.png',O/'native-leaf-contact-sheet.png']
    files += sorted((ROOT/'tools/audit').glob('arthur_*_v1.py'))+sorted((ROOT/'tools/audit').glob('arthur_*_v1.lua'))
    record=dict(status='FROZEN_SOURCE_LEAF_CPU_AND_NATIVE_ARENA_PASS_HOST_NOT_INTEGRATED',
      original_ROM_sha256=cpu['original_ROM_sha256'],leaf_sha256=cpu['leaf_sha256'],
      arena_ROM_sha256=sha(O/'arena.nes'),CPU_receipt_sha256=sha(O/'cpu-receipt.json'),
      native_arena_receipt_sha256=sha(O/'native/leaf-arena-v1/receipt.json'),
      capacity=cpu['capacity'],logical_8x16_CHR_bytes=4096,physical_host_leases=[],
      exact_instruction_records=cpu['native_instruction_check'],original_differential_cases=cpu['original_vs_ported']['cases'],
      native_arena=native,bindings={str(p.resolve()):sha(p)for p in files},
      limits='See REVIEW.md. No MMC5 host leases/hooks/admission. Next derivative must project scratch explicitly and prove original world/lifecycle interactions.')
    p=O/'handoff.json';p.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(dict(status=record['status'],handoff_sha256=sha(p),bindings=len(record['bindings']),leaf_sha256=record['leaf_sha256'],arena_ROM_sha256=record['arena_ROM_sha256'])))
if __name__=='__main__':main()
