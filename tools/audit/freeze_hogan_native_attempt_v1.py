"""Retain the small incomplete native attempt before refining its observer."""
from pathlib import Path
import csv,hashlib,json,zipfile
R=Path(__file__).resolve().parents[2]
N=R/'build/hogan-native-active'
O=R/'build/hogan-native-review'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists()
    ready=json.loads((N/'ready.json').read_text())
    for p,h in ready['bindings'].items():assert sha(p)==h,p
    binding=json.loads((N/'capture/binding.json').read_text())
    assert binding['ready_sha256']==sha(N/'ready.json')and binding['exit_code']!=0
    rows=list(csv.DictReader((N/'capture/updates.csv').open()))
    files=[p for p in N.rglob('*')if p.is_file()]
    files +=[Path(p)for p in ready['bindings']if Path(p).is_relative_to(R/'tools')]
    files=list(set(files));assert len(files)<32 and sum(p.stat().st_size for p in files)<2_000_000
    O.mkdir()
    with zipfile.ZipFile(O/'native-attempt.zip','x',zipfile.ZIP_DEFLATED)as z:
        for p in files:z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(O/'native-attempt.zip')as z:
        for p in files:assert hashlib.sha256(z.read(p.relative_to(R).as_posix())).hexdigest()==sha(p)
    q=dict(recorded=True,native=True,qualified=False,passed=False,
           outcome='Emulator90second limit before controller route finished',ROM_sha256=ready['ROM_sha256'],
           complete_Main_rows=len(rows),last_physical_frame=int(rows[-1]['frame']),
           maximum_X=max(int(q['X'])for q in rows),maximum_camera=max(int(q['camera'])for q in rows),
           source_damage_events=max(int(q['source_damage'])for q in rows),native_defeats=max(int(q['native_defeat'])for q in rows),
           viewed_images=['selected.png','lives.png','gameplay.png'],
           visual_observation='Compared with baseline Peach, captured lives background has white HUD atY61 instead of16 (45px down). Sprite pixels are original. Persistence versus early-transition capture requires further native diagnostics. No sprite-position patch was made.',
           source_CPU_scroll_trace='build/hogan-current/scroll-cpu/trace.json: no nonzero2005 stores in the actual cold CPU path; this model does not establish raster timing.',
           archive_sha256=sha(O/'native-attempt.zip'),files={p.relative_to(R).as_posix():sha(p)for p in files})
    (O/'record.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(recorded=True,qualified=False,Main_rows=len(rows),archive_bytes=(O/'native-attempt.zip').stat().st_size)))


if __name__=='__main__':main()
