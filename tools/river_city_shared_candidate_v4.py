"""Retain v3 thumbnail color-class counterexample; build corrected successor."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    original=R/'tools/river_city_shared_candidate_v3.py'
    proof=R/'build/river-city-shared-v3-overlay/build-proof.json'
    d=json.loads(proof.read_text())
    assert next(r['sha256']for r in d['bindings']if Path(r['path'])==original)==sha(original)
    src=original.read_text()
    a='colors={1:(0,0,0,255),2:(248,248,248,255),3:(248,176,104,255),4:(40,96,192,255)}'
    b='colors={1:(0,0,0,255),2:(248,176,104,255),3:(248,248,248,255),4:(40,96,192,255)}'
    assert src.count(a)==1
    src=src.replace(a,b).replace('river-city-shared-v3','river-city-shared-v4')
    generated=R/'build/river_city_shared_v4_build.py';assert not generated.exists();generated.write_text(src,newline='\n')
    negative=R/'build/river-city-shared-v3-thumbnail-negative.json'
    negative.write_text(json.dumps(dict(ROM_sha256=d['ROM_sha256'],source_sha256=sha(original),native_run=False,
        reason='Thumbnail construction swapped authentic RCR color classes2(skin) and3(white). Runtime body palette unaffected. Correct in successor before native acceptance.'),indent=2)+'\n')
    subprocess.run([sys.executable,'-B',str(generated)],cwd=R,check=True)
    p=R/'build/river-city-shared-v4-overlay/build-proof.json';out=json.loads(p.read_text())
    out['bindings'].append(dict(path=str(Path(__file__).resolve()),sha256=sha(__file__)))
    out['retained_thumbnail_negative']=dict(path=str(negative),sha256=sha(negative))
    p.write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
