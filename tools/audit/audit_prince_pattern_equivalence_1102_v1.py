"""Measure lossless hardware-flip pair equivalence before requesting CHR space."""
from pathlib import Path
import hashlib,json
from recover_prince_core_1101_v1 import O,P,R


def main():
 p=O/'prince-body-8x16.chr';data=p.read_bytes();assert len(data)==31072
 pairs=[data[i:i+32]for i in range(0,len(data),32)];assert len(pairs)==971 and len(set(pairs))==971
 reverse=bytes(int(f'{i:08b}'[::-1],2)for i in range(256))
 h=lambda p:p.translate(reverse)
 v=lambda p:p[16:24][::-1]+p[24:32][::-1]+p[0:8][::-1]+p[8:16][::-1]
 modes={'none':lambda p:[p],'H':lambda p:[p,h(p)],'HV':lambda p:[p,h(p),v(p),h(v(p))]}
 counts={k:len({min(f(p))for p in pairs})for k,f in modes.items()}
 art=json.loads((O/'source-art.json').read_text());parts=[p for q in art['poses'][::2]for p in q['parts_8x16']]
 xs=[p['x']for p in parts];ys=[p['y']for p in parts]
 q=dict(passed=True,source_analysis_only=True,donor_sha256=P.SHA,original_pairs=len(pairs),hardware_flip_equivalence_pair_counts=counts,hardware_flip_equivalence_pages={k:(n*32+1023)//1024 for k,n in counts.items()},body_local_x_range=[min(xs),max(xs)],body_local_y_range=[min(ys),max(ys)],can_pack_HV_in_unused_signed_coordinate_bits=all(-64<=p['x']<64 and -64<=p['y']<64 for p in parts),limits=['Equivalence count only; no transformed atlas/metadata/renderer emitted or allocated.','Every canonical pair would still require exact per-pose hardware flip and raster comparison before use.'],bindings={str(x.relative_to(R)):hashlib.sha256(x.read_bytes()).hexdigest()for x in [Path(__file__),p,O/'source-art.json']})
 (O/'pattern-equivalence.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
