"""Read-only installed stream reachability and shared fixed-E placement audit."""
from pathlib import Path
import argparse, hashlib, json, re, sys
from check_tmnt_render_oa import load, location, address
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/reference'))
from build_playlist_audio import lz
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=True)
 r=load(a.rom);raw=r['raw'];prg=raw[16:1048592]
 assert sha(raw)=='52918588bab0eec3f3a1f857bf084d2d799e88a5c781c75233c098ccc5f54f3f'
 installed=b''.join((ROOT/f'audio/expanded/playlist-{i:02x}.bin').read_bytes()for i in range(20))
 assert prg[39*8192:39*8192+len(installed)]==installed
 cache=json.loads((ROOT/'build/reference-playlist/encoding-cache.json').read_text());meta=json.loads((ROOT/'docs/reference/expanded-playlist-encoding.json').read_text())
 built=bytearray();segments=[]
 for key in [*meta['streams'],'silent']:
  for part,end in [('intro',b'\x1c' if key+':loop'in cache['streams']else b'\xff'),('loop',b'\xff')]:
   k=key+':'+part
   if k not in cache['streams']:continue
   blob=lz(bytes.fromhex(cache['streams'][k])+end);start=len(built);built.extend(blob)
   segments.append(dict(key=k,start=start,end=len(built),bytes=len(blob),sha256=sha(blob)))
 assert bytes(built)==installed
 macros={}
 for n,pairs in cache['macros'].items():
  b=b''.join(bytes.fromhex(v)for v in pairs)+b'\x1f';pos=location(r,'XgMacro'+n);assert raw[pos:pos+len(b)]==b
  macros[n]=dict(file_offset=pos,bytes=len(b),sha256=sha(b))
 def table(name,n):
  v=location(r,name);return raw[v:v+n]
 roots=[];old_live=set();full_roots=set()
 families={6:'Pit / expanded fallback',7:'Rygar / TMNT fallback',8:'Luigi unreachable recorded table',9:'Bass',10:'Ryu',11:'Sophia',12:'Scrooge / Darkwing',13:'Kirby',14:'Meta Knight'}
 for prefix in ('XgArea','XgLoop','XgEvent','XgEventLoop'):
  banks,lo,hi=[table(prefix+s,63)for s in ('Banks','Lo','Hi')]
  for i,(bank,l,h)in enumerate(zip(banks,lo,hi)):
   family=6+i//7;pos=(bank-39)*8192+(l+(h<<8)-0xa000);live=family!=8
   rec=dict(table=prefix,index=i,family=family,family_name=families[family],bank=bank,address=l+(h<<8),reachable=live)
   if bank==7:
    key='ScroogeMusicLoop'if prefix in('XgLoop','XgEventLoop')else'ScroogeMusicIntro';assert address(r,key)==l+(h<<8)
    path=ROOT/('audio/expanded/scrooge-loop.bin'if key.endswith('Loop')else'audio/expanded/scrooge-intro.bin');blob=path.read_bytes();loc=location(r,key);assert raw[loc:loc+len(blob)]==blob
    rec.update(stream=key,bytes=len(blob),sha256=sha(blob),file_offset=loc)
   elif bank<100:
    hit=[s for s in segments if s['start']==pos];assert len(hit)==1,(rec,pos)
    rec['stream']=hit[0]['key'];rec['offset']=pos
    if live:old_live.add(pos)
   else:
    off=(bank-100)*8192+(l+(h<<8)-0xa000);rec['offset']=off
    if live:full_roots.add(off)
   roots.append(rec)
 full=b''.join((ROOT/f'audio/full-roster/full-{i:02x}.bin').read_bytes()for i in range(16));assert prg[100*8192:100*8192+len(full)]==full
 def span(start):
  cursor=start;history=bytearray();flag=0;bits=0;pending=[]
  def byte():
   nonlocal cursor,flag,bits,pending
   if pending:
    v=history[-pending[0]];pending[1]-=1
    if not pending[1]:pending=[]
   else:
    if bits==0:flag=full[cursor];cursor+=1;bits=8
    compressed=flag&1;flag>>=1;bits-=1
    if compressed:
     x,y=full[cursor:cursor+2];cursor+=2;pending=[1+x+((y&7)<<8),(y>>3)+3]
     return byte()
    v=full[cursor];cursor+=1
   history.append(v);return v
  frames=0
  while True:
   tag=byte()
   if tag in (254,255):break
   if tag<128:frames+=tag;continue
   assert tag in(128,129),(start,tag,cursor)
   mask=byte()+(byte()<<8)
   for _ in range(mask.bit_count()+(tag&1)):byte()
   frames+=1
  return dict(start=start,end=cursor,bytes=cursor-start,first_bank=100+start//8192,last_bank=100+(cursor-1)//8192,frames=frames,sha256=sha(full[start:cursor]))
 spans=[span(s)for s in sorted(full_roots)]
 covered={b for s in spans for b in range(s['first_bank'],s['last_bank']+1)};assert covered==set(range(100,116)),covered
 for s in segments:s['reachable']=s['start']in old_live
 blank=[b for b in range(128)if prg[b*8192:(b+1)*8192]==b'\xff'*8192]
 assert blank==[63,123,124,125]
 incbins=[]
 for f in (ROOT/'src').glob('*'):
  if f.is_file():
   for path in re.findall(r'\.incbin\s+"([^"]+)"',f.read_text(errors='replace')):
    if path.startswith('audio/'):incbins.append(dict(source=str(f.relative_to(ROOT)),path=path))
 assert not any('/music-'in q['path']for q in incbins)
 result=dict(ROM_sha256=sha(raw),blank_PRG_banks=blank,installed_old_playlist=dict(bytes=len(installed),banks=[39,58],sha256=sha(installed),exact_reconstruction=True,segments=segments,macros=macros),call_table_roots=roots,full_roster=dict(bytes=len(full),sha256=sha(full),reachable_spans=spans,reachable_banks=sorted(covered)),source_incbins=incbins,not_installed=['audio/expanded/music-*.bin obsolete external raw assets','Mac recorded79685B preparatory capture assets'],no_track_removed=True,placement=dict(Mac=123,TMNT_A=63,TMNT_B=124,shared_E_mirror_and_cold=125,mirror_primary72=[0xf140,0xf581],mirror_Sypha75=[0xf5c0,0xf681],TMNT_cold_future_C=[0xd700,0xdaf7],new_manager_C=[0xdaf7,0xde11],fixed_resident_helpers=[['FE15','FE40'],['FEE1','FF00']]),scope='MMC5 expanded only. No music data or source changed. Full implementation and native qualification remain pending.')
 (out/'storage.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k]for k in('ROM_sha256','blank_PRG_banks','placement','scope')},indent=2));print('unrooted old streams',[(s['key'],s['bytes'])for s in segments if not s['reachable']]);print('full banks',sorted(covered))
if __name__=='__main__':main()
