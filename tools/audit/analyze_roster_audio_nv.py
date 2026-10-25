"""Read-only capacity study of all retained new-roster source APU captures."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/reference'))
import build_new_roster_audio as codec
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
OUT=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-roster-audio-nv')


def main():
    out=OUT/'mask-lz-capacity';out.mkdir(parents=True,exist_ok=False)
    manifest=json.loads((codec.SOURCE/'captures-manifest.json').read_text())
    plan=json.loads((codec.SOURCE/'playlist-plan.json').read_text())
    plan['meta']={**plan['kirby'],'tracks':{**plan['kirby']['tracks'],'normal':13,'hurry':13}}
    music={f"{role if role!='meta'else'kirby'}-{p['tracks'][kind]:02d}"for role,p in plan.items()for kind in codec.AREAS+['hurry']}
    needed={f"{role if role!='meta'else'kirby'}-{n:02d}"for role,p in plan.items()for n in p['tracks'].values()}
    for role,p in plan.items():
        source=ROOT/p['source'];assert sha(source)==p['source_sha256'],role
    streams={};records={}
    for key in sorted(needed):
        r=manifest[key];assert Path(r['path']).is_file(),key
        fs,dpcm=codec.frames(r);loop=codec.cycle(fs)if key in music else None
        segments={'intro':fs[:loop[0]],'loop':fs[loop[0]:loop[0]+loop[1]]}if loop else{'intro':fs}
        sizes={}
        for label,frames in segments.items():
            mask=codec.encode(frames)+(b'\xfe'if loop and label=='intro'else b'\xff')
            packed=codec.lz(mask);name=key+'-'+label
            (out/(name+'.bin')).write_bytes(packed);streams[name]=packed;sizes[label]=dict(raw=len(mask),compressed=len(packed))
        records[key]=dict(frames=len(fs),loop=loop,capture_sha256=r['capture_sha256'],DPCM_writes_not_encoded=dpcm,sizes=sizes)
        print(key,sum(len(v)for v in set(streams.values())),flush=True)
    total=sum(len(v)for v in set(streams.values()))
    by_role={role:sum(sum(s['compressed']for s in records[k]['sizes'].values())for k in records if k.startswith(role+'-'))for role in plan if role!='meta'}
    report=dict(total_bytes=total,reserved_bytes=26*8192,fits=total<=26*8192,streams=records,by_role=by_role,
                captured_tracks=len(records),source_manifest_sha256=sha(codec.SOURCE/'captures-manifest.json'),
                codec_sha256=sha(ROOT/'tools/reference/build_new_roster_audio.py'),
                installed_assets_changed=False,scope='Full retained captures; no shortening, fallback substitution, ROM, game or installed asset edits. DPCM remains an explicit unsupported part of this existing codec.')
    (out/'capacity.json').write_text(json.dumps(report,indent=2)+'\n')
    local=ROOT/'build/verification/roster-audio-nv';local.mkdir(exist_ok=True)
    (local/'capacity-location.json').write_text(json.dumps(dict(path=str(out/'capacity.json'),sha256=sha(out/'capacity.json'),bytes=total,fits=report['fits']),indent=2)+'\n')
    print(json.dumps(dict(total_bytes=total,available=26*8192,fits=report['fits'],by_role=by_role)))


if __name__=='__main__':main()
