"""Bounded primary-source discovery and donor patch reconstruction."""
from pathlib import Path
import hashlib,json,urllib.request,zlib
R=Path(__file__).resolve().parents[2];O=R/'build/mario-tank-source-1101-v1'
COMMIT='a0f6383f8c0989f1bf60a19e7504d8c2e03c666d'
BASE=Path('C:/NES/Super Mario Bros. (World).nes')
PATCH_URL='https://www.smbarena.com/hacks/3/3692/Mario%20The%20Tank.ips'
PATCH_SHA='6aa3141872cb4a2b88bf8c14d2d650d825495cba7a24bfa83de80bff1b0fd92a'
sha=lambda b:hashlib.sha256(b).hexdigest()
def fetch(url):return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.smbarena.com/hack?id=3692&p=0'}),timeout=30).read()
def apply(base,patch):
 assert patch.startswith(b'PATCH');out=bytearray(base);i=5;rows=[]
 while patch[i:i+3]!=b'EOF':
  at=int.from_bytes(patch[i:i+3],'big');n=int.from_bytes(patch[i+3:i+5],'big');i+=5
  if n:data=patch[i:i+n];i+=n
  else:n=int.from_bytes(patch[i:i+2],'big');data=patch[i+2:i+3]*n;i+=3
  if len(out)<at+n:out.extend(bytes(at+n-len(out)))
  out[at:at+n]=data;rows.append([at,n])
 i+=3
 if len(patch)>i:assert len(patch)==i+3;out=out[:int.from_bytes(patch[i:i+3],'big')]
 return bytes(out),rows
def donor():
 b=BASE.read_bytes();assert sha(b)=='0b3d9e1f01ed1668205bab34d6c82b0e281456e137352e4f36a9b2cfa3b66dea'
 normalized=bytes.fromhex('4e45531a020101000000000000000000')+b[16:]
 assert zlib.crc32(normalized)==0x3337ec46 and hashlib.sha1(normalized).hexdigest()=='ea343f4e445a9050d4b4fbac2c77d0693b1d0922'
 patch=(O/'Mario The Tank.ips').read_bytes();assert sha(patch)==PATCH_SHA
 out,rows=apply(normalized,patch);return out,dict(local_base=str(BASE),local_base_sha256=sha(b),normalization='Only16-byte header normalized to the author-required original iNES header; PRG/CHR bytes identical.',normalized_CRC32='3337ec46',normalized_SHA1=hashlib.sha1(normalized).hexdigest(),patch_URL=PATCH_URL,patch_sha256=sha(patch),patch_records=len(rows),donor_sha256=sha(out),donor_bytes=len(out),header=out[:16].hex(),PRG_bytes=out[4]*16384,CHR_bytes=out[5]*8192,mapper=(out[6]>>4)|(out[7]&240),direct_local_donor_found=False,ROM_copy_retained=False)
def main():
 O.mkdir(exist_ok=True);S=O/'source';S.mkdir(exist_ok=True)
 patch=O/'Mario The Tank.ips'
 if not patch.exists():patch.write_bytes(fetch(PATCH_URL))
 paths=['src/collision.s','src/common.s','src/gamecore.s','src/gamemode.s','src/player.s','src/metasprite.s','src/sprite_render.s','src/objects/powerup.s','src/objects/fireball_bubble.s','src/tiles/brick.s','src/screen_render.s','src/reset.s','src/tiles/flagpole.s','src/tiles/level.s','inc/memory.inc','inc/constants.inc','inc/metasprite.inc','inc/metasprite_custom.inc','inc/metasprite_p.inc','inc/common.inc','inc/globals.inc','inc/player.inc','inc/memory_p.inc','src/memory.s','chr/sprites_mario.chr','chr/sprites_enemies.chr','chr/sprites_misc.chr','CMakeLists.txt','README.md']
 rows=[]
 for path in paths:
  p=S/path;p.parent.mkdir(parents=True,exist_ok=True)
  if not p.exists():p.write_bytes(fetch('https://raw.githubusercontent.com/AleFunky/mariothetank/'+COMMIT+'/'+path))
  b=p.read_bytes();rows.append(dict(path=path,bytes=len(b),sha256=sha(b),Git_blob_SHA1=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()))
 out,q=donor();q.update(passed=True,source_repository='https://github.com/AleFunky/mariothetank',source_commit=COMMIT,source_files=rows,
  credits=dict(hack='AleFunky',inspiration='Doogtoons, Ultimate World1-1 SPEEDRUN trick, https://www.youtube.com/shorts/_v0GDYD8c28',base='SMB1Base; Nintendo original game'),
  primary_pages=['https://romhackplaza.org/romhacks/mario-the-tank-nes','https://alefunky.dev/hacks/mario-the-tank/','https://www.smbarena.com/hack?id=3692&p=0'],
  limits=['Author source recovered and IPS reconstructed from local base; source/main-vs-patch build identity is not yet proved.','No playable crossover integration or roster edits, native emulator, screenshots/video, or per-frame files.'])
 (O/'donor-identity.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in['passed','donor_sha256','donor_bytes','PRG_bytes','CHR_bytes','mapper','source_commit']}))
if __name__=='__main__':main()
