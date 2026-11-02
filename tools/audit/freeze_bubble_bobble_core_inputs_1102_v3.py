"""One compact reproducible source-core input checkpoint; no ROM/debug/media."""
import hashlib,json,zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'build/bubble-bobble-source-1101-v1'
sha=lambda b:hashlib.sha256(b).hexdigest()


def main():
 names=['instruction-index.json','upstream-notices.txt','discovery.json','donor-source.s','donor-source.cfg','source-closure.json','CPU-closure.json','chr-closure.json','donor-chr-closure.bin','component.s','component.cfg','component-layout.json','component-CPU.json','component-native.chr','native-art.json']
 files={n:(O/n).read_bytes()for n in names}
 assert json.loads(files['CPU-closure.json'])['passed']and json.loads(files['component-CPU.json'])['passed']and json.loads(files['native-art.json'])['passed']
 manifest=dict(passed=True,ROM_included=False,debug_or_media_included=False,native_adapter_in_progress_included=False,donor_SHA256='e34901acf6917495890ef79ddb33e4641ea309a803d777a27a198e8802c9b4a0',boundary_upstream_commit='5980e1a5f1731181ced5d195d85f9551d5ac7f28',source_core_bytes=5434,source_state_bytes=1024,normal_art_bytes=800,files={n:dict(bytes=len(v),sha256=sha(v))for n,v in files.items()},replay='Pinned local original ROM plus these exact instruction-boundary inputs and tracked audit recipes; use the same bounded task root. Reassemble donor/core from the retained .s/.cfg on demand; no large reference/source tree needed.',scope='Only qualified original/source-core/art inputs. Independent native frame/camera/loader work is deliberately excluded.')
 files['files.json']=(json.dumps(manifest,indent=2)+'\n').encode();dest=O/'core-inputs.zip'
 with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for n,v in files.items():z.writestr(n,v)
 with zipfile.ZipFile(dest)as z:
  assert set(z.namelist())==set(files)
  for n,v in files.items():assert z.read(n)==v
 q=dict(passed=True,archive=dest.relative_to(R).as_posix(),archive_SHA256=sha(dest.read_bytes()),archive_bytes=dest.stat().st_size,members=len(files),expanded_bytes=sum(map(len,files.values())),source_core_qualified=True,ROM_included=False,in_progress_native_included=False)
 (O/'core-inputs.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
