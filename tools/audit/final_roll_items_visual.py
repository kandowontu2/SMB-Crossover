"""Offline lossless frame review sheets from the FAILED8ff Hard pilot."""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
from PIL import Image, ImageDraw

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def pixels(p):
    a=np.frombuffer(p.read_bytes(),dtype='<u4').reshape(240,256)
    return Image.fromarray(np.stack([(a>>16)&255,(a>>8)&255,a&255],2).astype('uint8'))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();receipt=json.loads((a.native/'proof.json').read_text(encoding='utf-8'))
    assert receipt['passed']is False and receipt['mode']=='hard'
    events=[json.loads(x)for x in(a.native/'events.jsonl').read_text(encoding='utf-8').splitlines()]
    starts={e['step']:e for e in events if e['kind']=='step-started'}
    hud={e['step']:e for e in events if e['kind']=='committed-resource-hud'}
    assert set(starts)==set(hud)==set(range(1,37))
    a.output.mkdir(parents=True,exist_ok=False);sheets=[];frames=[]
    for group in range(6):
        im=Image.new('RGB',(512,32+6*278),'#20202a');draw=ImageDraw.Draw(im)
        draw.text((6,6),'8ff Hard: FAILED final receipt; diagnostic frame review only',fill='white')
        for row,step in enumerate(range(group*6+1,group*6+7)):
            y=32+row*278
            for col,(suffix,e)in enumerate([('start',starts[step]),('committed-hud',hud[step])]):
                f=a.native/f'{step:02d}-{suffix}.argb';im.paste(pixels(f),(col*256,y+34))
                state=e['data']['before']if suffix=='start'else e['data']
                draw.text((col*256+4,y+2),f'{step:02d} {suffix} u{e["update"]}',fill='white')
                draw.text((col*256+4,y+17),f'HP{state["hp"]:02d} EN{state["energy"]:02d} food{state["food"]} lives{state["lives"]}',fill='#ffe5a0')
                frames.append(dict(file=str(f),sha256=sha(f),step=step,kind=suffix,source_event=e))
        f=a.output/f'before-after-{group+1}.png';im.save(f);sheets.append(dict(file=str(f),sha256=sha(f)))
    z=dict(native_passed=False,goal_complete=False,source_native_receipt_sha256=sha(a.native/'proof.json'),
           script_sha256=sha(Path(__file__)),scope=__doc__,frames=frames,sheets=sheets,
           limits='Frame pixels retain actual committed display; labels are source event state/time. All36 committed HUD events passed their actual PPU digit assertions, but final native receipt remains FAILED. No new native execution or game-change qualification.')
    (a.output/'proof.json').write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(frames=len(frames),sheets=len(sheets),proof_sha256=sha(a.output/'proof.json'),native_passed=False)))


if __name__=='__main__':main()
