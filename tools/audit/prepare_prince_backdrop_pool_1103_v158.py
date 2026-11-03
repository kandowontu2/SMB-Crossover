"""Compact actual157 backdrop pool; component fixtures remain in memory."""
from pathlib import Path
import json,re,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import measure_prince_backdrop_binding_1103_v157 as B
import measure_prince_lzdict_1102_v9 as D
O=B.O;M=B.M


def main():
 images=B.images();packed=[D.encode(v)for v in images];text=(O/'cold-worker-v154.s').read_text();rows=[]
 for name,data,p in zip(['Runtime','Metadata','State'],images,packed):
  start=0xc500 if name=='Runtime'else 0xc300 if name=='State'else 0xe100-len(p)
  for suffix,value in [('Input',start),('Packed',len(p)),('Bytes',len(data))]:
   text,n=re.subn(r'(?m)^'+name+suffix+r'=\$[0-9a-f]+$',name+suffix+f'=${value:04x}',text);assert n==1
  rows.append(dict(name=name,uncompressed_bytes=len(data),compressed_bytes=len(p),source_start=start,SHA256=M.sha(data)))
 cfg=f'MEMORY{{B:start=$d25e,size=$100,file=%O;W:start=$c100,size=$200,file=%O;}}SEGMENTS{{BOOT:load=B,type=ro;WORKER:load=W,type=ro;}}'
 worker,lab=M.C.M.A.assemble('cold-worker-v158',text,cfg)
 for ext in ['o','cfg','lbl']:(O/('cold-worker-v158.'+ext)).unlink()
 assert len(worker)==444 and lab['PpColdBoot']==0xd25e
 art=(O/'prince-body-8x16.chr').read_bytes();decoder=(O/'cold-decoder-v25.bin').read_bytes();payload=art+decoder+worker+b''.join(packed);assert len(payload)<=45056
 (O/'cold-pool-v158.bin').write_bytes(payload)
 q=dict(passed=True,backing_measurement_only=True,actual_decoder_fullcold_pending=True,ROM_written=False,physical_pages=44,physical_spare=45056-len(payload),payload_bytes=len(payload),source_art_SHA256=M.sha(art),images=rows,worker_labels=lab,scope='Same qualified lossless codec and444B typed worker source. Only three source-declared kind0 target table bytes change153/149 images to exact CE:A296 backdrop. All fixtures kept in memory; actual wholecold decoder comparison required next.',bindings={p.relative_to(R).as_posix():M.sha(p.read_bytes())for p in [Path(__file__),Path(B.__file__),O/'backdrop-binding-v157.json',O/'cold-worker-v154.s',O/'cold-worker-v158.s',O/'cold-worker-v158.bin',O/'cold-pool-v158.bin']})
 (O/'backdrop-pool-v158.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','worker_labels']}))


if __name__=='__main__':main()
