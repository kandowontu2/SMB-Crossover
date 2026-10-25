from pathlib import Path
import subprocess,json
R=Path(__file__).resolve().parents[2];P=R/'build/roster-through-2-2/bill-easy-showcase-z-3-v0-mmc3/playthrough-lossless.mkv';E=R/'Playthrough Videos/Showcases/Verified/Bill-Easy-Progression-lossless.mkv'
O=R/'build/verification/showcase-pixels-ah';assert not O.exists();O.mkdir()
def framehash(p,filters):
 s=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-an','-vf',filters,'-f','framemd5','-'],text=True)
 return [line.rsplit(',',1)[1].strip()for line in s.splitlines()if line and not line.startswith('#')]
a=framehash(P,'trim=start_frame=540,format=rgb24');b=framehash(E,'crop=768:720:0:48,scale=256:240:flags=neighbor,format=rgb24')
def pcm(p,filters=None):
 cmd=['ffmpeg','-v','error','-i',str(p),'-vn']
 if filters:cmd+=['-af',filters]
 return subprocess.check_output(cmd+['-c:a','pcm_s16le','-f','hash','-hash','sha256','-'],text=True).strip()
start=540*253/15205;pa=pcm(P,f'atrim=start={start},asetpts=PTS-STARTPTS');pb=pcm(E)
report=dict(source_frames=len(a),edit_frames=len(b),different_gameplay_pixel_frames=sum(x!=y for x,y in zip(a,b)),native_pcm_identical=pa==pb,source_pcm=pa,edited_pcm=pb,limits='Checks the lossless editorial master, not the lossy posting MP4.')
(O/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
