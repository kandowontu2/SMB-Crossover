"""Verify and finish the completed first capture after a host read-all error."""
from pathlib import Path
import csv,gzip,hashlib,json,struct
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;out=D/'copies-easy-food-v3-direct-v1';rom=D/'food-candidate-v3/candidate.nes'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for data in iter(lambda:f.read(1048576),b''):h.update(data)
 return h.hexdigest()
raw=out/'direct.argb';archive=out/'direct.argb.gz';assert raw.exists()and archive.exists()and not(out/'proof.json').exists()
assert 'Mesen exit: 0' in(out/'host.log').read_text()
assert json.loads((out/'copy-result.json').read_text())['passed']
assert sha(raw)==sha(archive)or raw.stat().st_size>archive.stat().st_size
hr=hashlib.sha256();hz=hashlib.sha256();nr=nz=0
for p,h,israw in [(raw,hr,True),(archive,hz,False)]:
 with (p.open('rb')if israw else gzip.open(p,'rb'))as f:
  for data in iter(lambda:f.read(1048576),b''):
   h.update(data)
   if israw:nr+=len(data)
   else:nz+=len(data)
assert nr==nz==raw.stat().st_size and hr.digest()==hz.digest()
rows=list(csv.DictReader((out/'direct-frame-index.csv').open()));frames=0;header=struct.Struct('<IIQQ')
with raw.open('rb')as f:
 for row in rows:
  record=f.read(header.size);assert len(record)==header.size;frame,pixels,ppu,cycle=header.unpack(record)
  assert frame==ppu==200+frames==int(row['frame'])and pixels==256*240
  assert ppu==int(row['ppuFrame'])and cycle==int(row['cpuCycle'])
  data=f.read(pixels*4);assert len(data)==pixels*4
  values=np.frombuffer(data,dtype='<u4').reshape(240,256);rgb=np.stack(((values>>16)&255,(values>>8)&255,values&255),axis=2).astype(np.uint8)
  p=out/'frames'/f'{frame:06d}.png'
  assert hashlib.sha256(rgb.tobytes()).hexdigest()==row['RGB_sha256']and sha(p)==row['PNG_sha256']
  with Image.open(p)as image:assert np.array_equal(np.asarray(image.convert('RGB')),rgb)
  frames+=1
 assert not f.read(1)
assert frames==6919
fixture=D/'kirby-copies-final-v3/easy/run.lua';assert sha(fixture)==sha(out/'fixture.lua')
q=dict(passed=True,goal_complete=False,inventory_complete=False,exit=0,ROM_sha256=sha(rom),source_fixture=str(fixture),source_fixture_sha256=sha(fixture),immutable_fixture_copy_sha256=sha(out/'fixture.lua'),fixture_copy_exact=True,driver_sha256=sha(D/'capture_food_v3.py'),observer_sha256=sha(out/'observer.lua'),harness_sha256=sha(out/'run.lua'),direct_physical_frames=frames,actual_PPU_frame_ids_complete=True,every_saved_PNG_RGB_exact=True,raw_stream_bytes=nr,raw_stream_sha256=hr.hexdigest(),archive_sha256=sha(archive),raw_gzip_roundtrip_exact=True,temporary_raw_removed_after_exact_lossless_roundtrip=False,trace_sha256=sha(out/'trace.csv'),inputs_sha256=sha(out/'inputs.csv'),audio_sha256=sha(out/'audio.csv'),frame_index_sha256=sha(out/'direct-frame-index.csv'),recovery_driver_sha256=sha(Path(__file__)),raw_retained=True,scope='Original emulator run passed and all actual PPU records were converted before a host read-all error during final digest. This streaming recovery independently verifies raw/gzip byte identity, every PNG pixel and frame index. Raw is retained. No emulator rerun or gameplay assertion change.')
(out/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=True,frames=frames,raw_retained=True)))
