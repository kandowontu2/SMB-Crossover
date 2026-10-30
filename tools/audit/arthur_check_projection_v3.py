"""Re-use the exact declared-transformation/CPU oracle on relaxed v3 bytes."""
from pathlib import Path
import importlib.util,json
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('arthur_projection_oracle_v2',ROOT/'tools/audit/arthur_check_projection_v2.py')
A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)
A.OUT=ROOT/'build/arthur-projected-leaf-v3';A.S=A.symbols(A.OUT/'leaf.lbl')
A.RAW=(A.OUT/'leaf.bin').read_bytes();A.Q=json.loads((A.OUT/'projection-proof.json').read_text())
def main():
    A.main();p=A.OUT/'cpu-receipt.json';d=json.loads(p.read_text())
    d['bindings'][str(Path(__file__).resolve())]=A.sha(__file__)
    p.write_text(json.dumps(d,indent=2)+'\n')
    print(json.dumps(dict(final_receipt_sha256=A.sha(p))))
if __name__=='__main__':main()
