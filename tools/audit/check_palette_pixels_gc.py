"""Compare every native frame; palette changes must stay in world sprite bounds."""
from pathlib import Path
import csv,hashlib,json,subprocess,traceback,wave
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2];O=R/'build/verification/world-palette-pixels-gc'
A=R/'build/roster-through-2-2/root-rygar-current-fl-av-fq-7-v0-mmc3'
B=R/'build/roster-through-2-2/root-rygar-palette-av-fy-7-v0-mmc3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def read(pipe,size):
    data=bytearray()
    while len(data)<size:
        x=pipe.read(size-len(data))
        if not x:break
        data.extend(x)
    return data

def pcm(path):
    with wave.open(str(path),'rb')as w:
        h=hashlib.sha256();count=w.getnframes();p=dict(channels=w.getnchannels(),width=w.getsampwidth(),rate=w.getframerate(),frames=count)
        while x:=w.readframes(48000):h.update(x)
    return dict(**p,PCM_sha256=h.hexdigest())

def main():
    assert not O.exists();O.mkdir();report=dict(status='REVIEWING',goal_complete=False)
    try:
        identical={}
        for n in ('trace.csv','inputs.csv','oam.csv','chr.csv','render.csv','audio-events.csv'):
            assert sha(A/n)==sha(B/n),n;identical[n]=sha(A/n)
        for folder in(A,B):
            m=json.loads((folder/'manifest.json').read_text());p=json.loads((folder/'playthrough-lossless.verification/report.json').read_text())
            assert m['verified_through_2_2']and m['recording_verified']and p['result']=='passed-exact-rgb-and-pcm'
            assert sha(folder/'playthrough-lossless.mkv')==p['output']['sha256']
        dmas={}
        for row in csv.DictReader((A/'oam.csv').open()):dmas[int(row['frame'])]=bytes.fromhex(row['oamHex'])
        pipes=[subprocess.Popen(['ffmpeg','-v','error','-i',str(p/'playthrough-lossless.mkv'),'-an','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)for p in(A,B)]
        count=changed_frames=changed_pixels=0;last=None;captures={};bad=[]
        while True:
            data=[read(p.stdout,256*240*3)for p in pipes]
            if not any(data):break
            assert all(len(x)==256*240*3 for x in data)
            count+=1;pixels=[np.frombuffer(x,np.uint8).reshape(240,256,3)for x in data]
            current=dmas.get(count-1,dmas.get(count,last))
            mask=np.zeros((240,256),dtype=bool)
            # DMA labels precede the physical-frame boundary. Use both owners
            # around that boundary; this is a conservative rectangle bound,
            # not an assertion that every covered pixel is a visible sprite.
            for owner in(last,current):
                if owner:
                    for yy,tile,attr,xx in np.frombuffer(owner,np.uint8).reshape(64,4):
                        if int(attr)&3!=3:continue
                        y=int(yy)+1;x=int(xx)
                        if y<240:mask[y:min(240,y+16),x:min(256,x+8)]=True
            diff=np.any(pixels[0]!=pixels[1],axis=2);n=int(diff.sum())
            if n:changed_frames+=1;changed_pixels+=n
            outside=int((diff&~mask).sum())
            if outside and len(bad)<20:bad.append(dict(frame=count,pixels=outside))
            if count in(4496,4500,4504,4507):captures[count]=[p.copy()for p in pixels]
            last=current
        errors=[p.stderr.read().decode()for p in pipes];assert all(p.wait()==0 for p in pipes),errors
        assert count==20680
        sheet=Image.new('RGB',(512,len(captures)*264),'#202020');draw=ImageDraw.Draw(sheet)
        for i,(frame,pair)in enumerate(captures.items()):
            for j,p in enumerate(pair):sheet.paste(Image.fromarray(p),(j*256,i*264))
            draw.text((4,i*264+242),f'{frame}: old FL',fill='white');draw.text((260,i*264+242),'native world palette',fill='white')
        sheet.save(O/'underground-before-after.png')
        audio=[pcm(p/'native-audio.wav')for p in(A,B)]
        report.update(status='PASS_PIXEL_CHANGES_BOUNDED_TO_PALETTE3_WORLD_SPRITE_RECTANGLES'if not bad else'PIXEL_DIFFERENCES_REQUIRE_INSPECTION',
            compared_frames=count,identical_physical_replay_logs=identical,changed_frames=changed_frames,changed_pixels=changed_pixels,
            changes_outside_world_sprite_rectangle_union=bad,PCM=audio,PCM_identical=audio[0]==audio[1],
            qualification='Every RGB frame compared. The mask conservatively includes prior/current committed palette3 sprite rectangles. Static all88Rygar body/disk/chain parts are palette0, whose packet/graphics remain unchanged; native pickup/walk/return/outline tests separately exercise actual drawing. Not a claim that all sprite palette colors of other characters are repaired.')
        print(json.dumps({k:report[k]for k in('status','compared_frames','changed_frames','changed_pixels','PCM_identical')}),flush=True)
    except Exception as error:
        report.update(status='FAILURE_RETAINED',error=repr(error),traceback=traceback.format_exc());raise
    finally:(O/'summary.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
