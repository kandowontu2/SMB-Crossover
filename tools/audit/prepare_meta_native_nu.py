"""Prepare read-only live Meta OAM audits from linked and original cartridge data."""
from pathlib import Path
import argparse,gzip,hashlib,json,re,shutil
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--source',type=Path,default=Path("C:/NES/Kirby's Adventure (USA) (Rev 1).nes"));p.add_argument('--native-captures',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rom=a.rom.read_bytes();original=a.source.read_bytes();assert sha(a.source)=='a7a742f5288cd4ab220f530ee7c8d0e3714b8bf107e89c9bf03039217fec5829';assert rom[4]==64 and rom[5]==128
labels={m[2]:int(m[1],16)for line in a.rom.with_suffix('.lbl').read_text().splitlines()if(m:=re.fullmatch(r'al ([0-9A-Fa-f]+) \.(\w+)',line))};segments={};z=a.rom.with_suffix('.dbg.gz');debug=gzip.decompress(z.read_bytes()).decode()if z.exists()else a.rom.with_suffix('.dbg').read_text()
for line in debug.splitlines():
 if line.startswith('seg\t')and'ooffs='in line:
  d=dict(x.split('=',1)for x in line[4:].split(','));segments[d['id']]=(int(d['start'],16),int(d['ooffs']))
 if line.startswith('sym\t')and'name="MkBodyLo"'in line:
  d=dict(x.split('=',1)for x in line[4:].split(',')if'='in x);sid=d['seg']
start,offset=segments[sid];read=lambda addr:rom[offset+addr-start];source_prg=original[16:16+524288];source_chr=original[16+524288:];source_read=lambda addr:source_prg[0x31*8192+(addr&8191)];word=lambda addr:source_read(addr)+256*source_read(addr+1);sign=lambda v:v if v<128 else v-256
poses=[];lua=['META_POSES={}']
for pose in range(90):
 pointer=read(labels['MkBodyLo']+pose)+256*read(labels['MkBodyHi']+pose);assert read(pointer)%4==0;source=word(0x8000+pose*2)
 parts=[dict(tile=read(pointer+1+i*4),attr=read(pointer+2+i*4),dy=sign(read(pointer+3+i*4)),dx=sign(read(pointer+4+i*4)))for i in range(read(pointer)//4)]
 native=[dict(dx=sign(source_read(source+1+i*4)),dy=sign(source_read(source+2+i*4)),tile=source_read(source+3+i*4),attr=source_read(source+4+i*4))for i in range(source_read(source))]
 page=256+read(labels['MkBodyChr']+pose);poses.append(dict(pose=pose,pointer=pointer,page=page,parts=parts,native=native));packed=','.join('{'+','.join(str(v[k])for k in ['tile','attr','dy','dx'])+'}'for v in parts);lua.append(f'META_POSES[{pose}]={{pointer={pointer},page={page},parts={{{packed}}}}}')
orders=[];hashes={}
for path in sorted(a.native_captures.glob('pose-*-state.json')):
 state=json.loads(path.read_text());stem=path.name.removesuffix('-state.json');files={n:a.native_captures/(stem+n)for n in ['-oam.bin','-palette.bin','-chr.bin']};raw=files['-oam.bin'].read_bytes();palette=files['-palette.bin'].read_bytes();physical=files['-chr.bin'].read_bytes();assert physical==source_chr[0xa4*1024:0xa6*1024]and list(palette[29:32])==[0x36,0x14,0x0f]and list(palette[21:24])==[0x30,0x37,0x17]
 parts=poses[state['pose']]['native'];indices=[];used=set()
 for slot in range(64):
  quad=tuple(raw[slot*4:slot*4+4])
  for index,part in enumerate(parts):
   x=state['x']-state['cameraX']+part['dx'];y=state['y']-state['cameraY']+part['dy']
   if index not in used and 0<=x<256 and 0<=y<240 and quad==(y,part['tile']|1,part['attr'],x):indices.append(index);used.add(index);break
 visible=[i for i,v in enumerate(parts)if 0<=state['x']-state['cameraX']+v['dx']<256 and 0<=state['y']-state['cameraY']+v['dy']<240];assert indices==visible,'Original hardware must establish descriptor-forward priority'
 orders.append(dict(pose=state['pose'],frame=state['frame'],hardware_indices=indices,descriptor_forward=True,descriptor_reverse=indices==visible[::-1]));hashes[path.name]=sha(path)
 for path in files.values():hashes[path.name]=sha(path)
assert len(orders)>=30
oracle=dict(ROM_sha256=sha(a.rom),source_sha256=sha(a.source),port_chr_offset=16+1048576,source_chr_offset=16+524288,poses=poses,original_hardware_order=orders,original_capture_hashes=hashes)
(out/'oracle.json').write_text(json.dumps(oracle,indent=2)+'\n');(out/'poses.lua').write_text('\n'.join(lua)+'\n');driver=ROOT/'tests/meta-knight-nes-moves.lua';shutil.copyfile(driver,out/'moves-driver.lua');observer=Path(__file__).with_name('meta_native_observer_nu.lua')
for mode in ['easy','hard']:
 folder=out/f'moves-{mode}';folder.mkdir();text='META_AUDIT_OUT=[=['+folder.as_posix()+'/]=]\nMETA_HARD='+str(mode=='hard').lower()+'\ndofile([=['+(out/'poses.lua').as_posix()+']=])\nlocal finish=assert(dofile([=['+observer.resolve().as_posix()+']=]))\nlocal stop=emu.stop;emu.stop=function(code)finish();stop(code)end\ndofile([=['+(out/'moves-driver.lua').as_posix()+']=])\n';(folder/'run.lua').write_text(text)
(out/'preparation.json').write_text(json.dumps(dict(ROM_sha256=sha(a.rom),source_sha256=sha(a.source),preparer_sha256=sha(Path(__file__)),observer_sha256=sha(observer),driver_sha256=sha(driver),original_hardware_poses=len(orders),read_only_observer=True,separate_driver_injected_arenas=True),indent=2)+'\n')
print(json.dumps(dict(output=str(out),ROM_sha256=sha(a.rom),original_hardware_poses=len(orders))))
