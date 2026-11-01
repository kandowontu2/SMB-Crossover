"""Compile player-only one-palette alternatives; retain native world P1/P2/P3."""
from pathlib import Path
import collections,hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'tools/audit'),str(ROOT/'tools')]
from private_build_outputs_v1 import validate
OUT=ROOT/'build/metal-storm-coexistence-1101-v9';V7=ROOT/'build/metal-storm-render-host-1101-v7';V8=ROOT/'build/metal-storm-resource-host-1101-v8'
REF=ROOT/'tools/reference/metal_storm_palette_host_1101_v9.inc'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
# Each index permutation explicitly retains transparent0. Palette values are
# original NES codes, not display-RGB nearest-colour guesses.
VARIANTS={
 'original-body':dict(palette=[15,38,15,21],body=[0,1,2,3],shot=[0,1,1,2],description='Original body red/black/dark-red; blue shot colors become red/black.'),
 'red-white-black':dict(palette=[15,38,32,15],body=[0,1,3,1],shot=[0,1,2,3],description='Recommended: original dominant red and black outline; dark-red shading merges into red; white shot core retained.'),
 'blue-white-black':dict(palette=[15,33,32,15],body=[0,1,3,3],shot=[0,1,2,3],description='Blue body, white shot core, black outline; both red body tones are intentionally recolored.')}

def decode(p):
 return [[((p[(y//8)*16+y%8]>>(7-x))&1)+2*((p[(y//8)*16+y%8+8]>>(7-x))&1)for x in range(8)]for y in range(16)]

def remap(data,mapping):
 assert len(data)%32==0 and mapping[0]==0 and all(v for v in mapping[1:])
 out=bytearray(len(data))
 for n in range(len(data)//32):
  for y,row in enumerate(decode(data[n*32:n*32+32])):
   a=n*32+(y//8)*16+y%8
   for x,v in enumerate(row):
    z=mapping[v];out[a]|=(z&1)<<(7-x);out[a+8]|=(z>>1)<<(7-x)
 return bytes(out)

def main():
 inputs=json.loads((OUT/'palette-inputs.json').read_text());assert inputs['passed']
 for p,h in inputs['bindings'].items():assert sha(p)==h,p
 for v in[V7,V8]:
  s=json.loads((v/'source-stage.json').read_text());assert s['passed']and sha(v/'source-proof.zip')==s['archive_sha256']
 render=(V8/'renderer-adapted.inc').read_text();render='.include "metal_storm_palette_host_1101_v9.inc"\n'+render
 before=' lda MsPacket,y\n ora MsFlip\n sta MsPacket,y';assert render.count(before)==1
 render=render.replace(before,' lda MsPacket,y\n Ms9ShotPalette0\n ora MsFlip\n sta MsPacket,y')
 before=' cpy #12\n bcc MsPaletteByte';assert render.count(before)==1;render=render.replace(before,' cpy #6\n bcc MsPaletteByte')
 before='MsPalettePacket:.byte $3f,$11,3,$26,$0f,$15,$3f,$15,3,$21,$20,$01';assert render.count(before)==1
 render=render.replace(before,'MsPalettePacket:Ms9PalettePacket')
 (OUT/'renderer-palette.inc').write_text(render)
 (OUT/'renderer.s').write_text('.setcpu "6502"\n.macpack longbranch\n.import MsState,MsLifeUnsupported\n.include "renderer-palette.inc"\n')
 cc=ROOT/'tools/Windows/cc65/bin';commands=[]
 def command(cmd):
  guard=validate(cmd,OUT,cwd=ROOT);r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True)
  commands.append(dict(command=list(map(str,cmd)),guard=guard,returncode=r.returncode,stderr=r.stderr));assert r.returncode==0,r.stderr
 def assemble(name,source):
  command([cc/'ca65.exe','-g','-I',OUT,'-I',V7,'--bin-include-dir',V7,'-I',ROOT/'build/metal-storm-objects-host-1101-v6','-I',ROOT/'build/metal-storm-terrain-host-1101-v5','-I',ROOT/'tools/reference',source,'-o',OUT/(name+'.o')])
 assemble('actor',V7/'actor.s');assemble('renderer',OUT/'renderer.s')
 body=(V7/'body.chr').read_bytes();shots=(V7/'shots.chr').read_bytes();results={}
 for name,v in VARIANTS.items():
  pixels={};art=bytearray();sourcepal=inputs['Metal_source_palette']
  for kind,data,length,basepal in[('body',body,4608,0),('shot',shots,160,1)]:
   changed=0;oldcounts=collections.Counter();newcounts=collections.Counter()
   converted=remap(data[:length],v[kind]);art.extend(converted)
   for n in range(length//32):
    old=decode(data[n*32:n*32+32]);new=decode(converted[n*32:n*32+32])
    for yy in range(16):
     for xx in range(8):
      a,z=old[yy][xx],new[yy][xx];assert bool(a)==bool(z)
      if a:
       oa=sourcepal[basepal*4+a];nz=v['palette'][z];oldcounts[oa]+=1;newcounts[nz]+=1;changed+=oa!=nz
   pixels[kind]=dict(unique_patterns=length//32,opaque_pixels=sum(oldcounts.values()),RGB_index_exact=sum(oldcounts.values())-changed,intentionally_recolored_pixels=changed,source_color_counts=dict(sorted(oldcounts.items())),adapted_color_counts=dict(sorted(newcounts.items())),opaque_mask_exact=True)
  (OUT/(name+'.chr')).write_bytes(art+bytes(5120-len(art)))
  symbols=(V8/'symbols.s').read_text()+''.join(f'.export Ms9Color{i}={v["palette"][i]}\n'for i in range(1,4))
  (OUT/(name+'-symbols.s')).write_text(symbols);assemble(name+'-symbols',OUT/(name+'-symbols.s'))
  cfg='MEMORY{ACTOR:start=$a000,size=$1fe0,file="'+(OUT/(name+'-actor.bin')).as_posix()+'";RENDER:start=$cd00,size=$12e0,file="'+(OUT/(name+'-render.bin')).as_posix()+'";}SEGMENTS{CODE:load=ACTOR,type=ro;RENDER:load=RENDER,type=ro;}'
  (OUT/(name+'.cfg')).write_text(cfg)
  command([cc/'ld65.exe','-C',OUT/(name+'.cfg'),OUT/'actor.o',OUT/'renderer.o',OUT/(name+'-symbols.o'),'-o',OUT/(name+'-unused.bin'),'-Ln',OUT/(name+'.lbl')])
  labels={m[2]:int(m[1],16)for line in(OUT/(name+'.lbl')).read_text().splitlines()if(m:=re.fullmatch(r'al ([0-9a-fA-F]+) \.(\S+)',line))}
  actor=(OUT/(name+'-actor.bin')).read_bytes();render=(OUT/(name+'-render.bin')).read_bytes();oldactor=(V8/'actor.bin').read_bytes();oldlab=json.loads((V8/'assembly.json').read_text())['labels']
  positions=[i for i in range(len(oldactor)-2)if oldactor[i:i+3]==bytes([32,oldlab['MsObjectLifecycle']&255,oldlab['MsObjectLifecycle']>>8])];assert len(positions)==1
  allowed={positions[0]+1,positions[0]+2};diffs=[i for i,(a,z)in enumerate(zip(oldactor,actor))if a!=z]
  assert len(actor)==len(oldactor)==8083 and set(diffs)<=allowed,(name,diffs)
  assert actor[positions[0]:positions[0]+3]==bytes([32,labels['MsObjectLifecycle']&255,labels['MsObjectLifecycle']>>8])
  assert len(render)==2350 and len(art)==4768
  results[name]=dict(**v,pixel_counts=pixels,actor_bytes=len(actor),renderer_bytes=len(render),actor_relocation_only_offsets=diffs,labels=labels)
 assert len({sha(OUT/(name+'-actor.bin'))for name in VARIANTS})==1
 files=[Path(__file__),REF,OUT/'palette-inputs.json',V7/'source-stage.json',V8/'source-stage.json',V8/'renderer-adapted.inc',V8/'symbols.s',V8/'actor.bin',V7/'actor.s',V7/'body.chr',V7/'shots.chr',V7/'body-meta.bin',V7/'shot-meta.bin',V7/'render-life.inc',OUT/'renderer-palette.inc',OUT/'renderer.s']
 files+=[OUT/(name+ext)for name in VARIANTS for ext in['.chr','-symbols.s','.cfg','-actor.bin','-render.bin','.lbl']]
 result=dict(passed=True,native=False,installed=False,resource_granted=False,recommended='red-white-black',variant_pixel_counts_basis='Each of144unique8x16body patterns and5unique8x16shot patterns counted once; not animation/dwell weighted.',variants=results,commands=commands,scope='Assembled original actor/terrain/lifecycle plus player-only palette adaptation. Native P1/P2/P3 and all native world bitplanes unchanged. Caches and physical CHR placement remain test fixtures, not a runtime admission.',bindings={str(p.resolve()):sha(p)for p in files})
 (OUT/'palette-assembly.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,recommended=result['recommended'],variants={n:r['pixel_counts']for n,r in results.items()},renderer_bytes=2350,actor_bytes=8083)))
if __name__=='__main__':main()
