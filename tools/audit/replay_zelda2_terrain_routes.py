"""Independently replay both Zelda II terrain routes with lossless PPU capture."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import subprocess
import sys
from PIL import Image,ImageDraw
from check_tmnt_render_oa import load,location

ROOT=Path(__file__).resolve().parents[2]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['candidate','archive','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();folder=a.candidate.resolve();rom=folder/'candidate.nes';out=a.output.resolve()
    assert not out.is_relative_to(ROOT);out.mkdir(exist_ok=False)
    source=folder/'native-routes-v3/proof.json';native=json.loads(source.read_text())
    sha=hashlib.sha256(rom.read_bytes()).hexdigest();assert native['passed']and native['ROM_sha256']==sha
    driver=a.archive/'streaming-replay-v1/capture.py';b=load(rom);irq=(location(b,'IrqScrollSplit')-16)//8192
    report=dict(passed=False,complete=False,goal_complete=False,ROM_sha256=sha,runs=[],
                scope='Independent fixed-input Easy/Hard1-1 native playthroughs. Exact input/trace, each physical PPU frame/PNG RGB, lossless raw roundtrip, actual stage split, native CHR and world/camera bounds. Contact sheets are samples; not all items/audio/moving-platform or full-release certification.')
    for mode in ['easy','hard']:
        row=next(r for r in native['runs']if r['mode']==mode);route=Path(row['folder']);capture=out/mode
        with(out/(mode+'-host.log')).open('w')as log:
            result=subprocess.run([sys.executable,str(driver),'--rom',str(rom),'--route',str(route),
                                   '--output',str(capture)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        assert result.returncode==0,(out/(mode+'-host.log')).read_text()[-3000:]
        q=json.loads((capture/'proof.json').read_text())
        assert q['passed']and q['ROM_sha256']==sha
        for key in ['fixed_inputs_and_trace_exact','every_saved_PNG_RGB_exact','actual_PPU_frame_ids_complete','raw_gzip_roundtrip_exact']:assert q[key]
        assert json.loads((capture/'chr-commit.json').read_text())['passed']
        motion=json.loads((capture/'completed-loop-motion.json').read_text());assert motion['passed']
        frames=list(csv.DictReader((capture/'direct-frame-index.csv').open()))
        assert [int(r['frame'])for r in frames]==list(range(200,q['result']['frames']))
        rows=list(csv.DictReader((capture/'trace.csv').open()))
        active=[r for r in rows if r['engine']=='8'and r['mode']=='1'and r['task']=='3'and r['world']==r['level']=='0']
        pairs=[(x,y)for x,y in zip(active,active[1:])if int(y['frame'])==int(x['frame'])+1]
        world=max(abs(int(y['x'])-int(x['x']))for x,y in pairs)
        camera=[int(y['camera'])-int(x['camera'])for x,y in pairs]
        assert world<=8 and min(camera)>=0 and max(camera)<=4
        visible=[r for r in csv.DictReader((capture/'scroll-writes.csv').open())if r['engine']=='8'and r['mode']=='1'and r['task']=='3'and r['world']==r['level']=='0'and r['screenDisabled']=='0'and r['renderingEnabled']=='1']
        assert visible and all(r['scanline']=='31'and int(r['writerBank'])==irq for r in visible)
        chosen=[int(frames[round(i*(len(frames)-1)/15)]['frame'])for i in range(16)]
        sheet=Image.new('RGB',(1024,1040),(24,28,36));draw=ImageDraw.Draw(sheet)
        for i,frame in enumerate(chosen):
            with Image.open(capture/'frames'/f'{frame:06d}.png')as im:sheet.paste(im.convert('RGB'),(i%4*256,i//4*260+20))
            draw.text((i%4*256+3,i//4*260+3),f'Zelda II {mode} frame{frame}',fill='white')
        sheet.save(out/(mode+'-overview.png'))
        entry=dict(mode=mode,passed=True,folder=str(capture),physical_frames=len(frames),raw_max_world_step=world,camera_range=[min(camera),max(camera)],visible_split_writes=len(visible),motion=motion)
        report['runs'].append(entry);(out/'progress.json').write_text(json.dumps(report,indent=2));print(json.dumps(entry),flush=True)
    report.update(passed=True,complete=True);(out/'proof.json').write_text(json.dumps(report,indent=2))


if __name__=='__main__':main()
