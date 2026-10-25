"""Package the verified ordinary Easy progression as a postable local video."""
from pathlib import Path
from fractions import Fraction
import json,hashlib,csv,subprocess
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[2];P=R/'build/roster-through-2-2/bill-easy-showcase-z-3-v0-mmc3';W=R/'build/roster-through-2-2/bill-easy-progression-w-3-v0-mmc3'
O=R/'Playthrough Videos/Showcases';assert not O.exists();O.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):
 with p.open(newline='')as f:return list(csv.DictReader(f))
manifest=json.loads((P/'manifest.json').read_text());proof=json.loads((P/'playthrough-lossless.verification/report.json').read_text());assert proof['result']=='passed-exact-rgb-and-pcm'
assert manifest['recording_metadata']['passed']and manifest['result']['deaths']==0 and manifest['result']['frames']==3000
assert (P/'trace.csv').read_bytes()==b''.join((W/'trace.csv').read_bytes().splitlines(keepends=True)[:3001])
assert (P/'inputs.csv').read_bytes()==b''.join((W/'inputs.csv').read_bytes().splitlines(keepends=True)[:3000])
trace=rows(P/'trace.csv');render=rows(P/'render.csv');assert all(t['behaviorVersion']=='0'for t in render)
powers={p:next(int(z['frame'])for z in trace if int(z['power'])==p)for p in (1,2)}
fps=Fraction(15205,253);start=540;seconds=float(start/fps)
labels=['BILL / EASY / NORMAL RIFLE','BILL / EASY / MUSHROOM: MACHINE GUN','BILL / EASY / FIRE FLOWER: SPREAD SHOT']
font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',24)
for n,label in enumerate(labels):
 img=Image.new('RGB',(768,48),'#16191e');d=ImageDraw.Draw(img);box=d.textbbox((0,0),label,font=font);d.text(((768-(box[2]-box[0]))//2,10),label,font=font,fill='white');img.save(O/f'Bill-Easy-label-{n}.png')
a=(powers[1]-1-start)/float(fps);b=(powers[2]-1-start)/float(fps)
filters=f"[0:v]trim=start_frame={start},setpts=PTS-STARTPTS,scale=768:720:flags=neighbor,pad=768:768:0:48:black[v];[v][1:v]overlay=0:0:shortest=1:enable='lt(t,{a})'[v1];[v1][2:v]overlay=0:0:shortest=1:enable='between(t,{a},{b})'[v2];[v2][3:v]overlay=0:0:shortest=1:enable='gte(t,{b})'[vo];[0:a]atrim=start={seconds},asetpts=PTS-STARTPTS[ao]"
master=O/'Bill-Easy-Progression-lossless.mkv';delivery=O/'Bill-Easy-Progression.mp4'
cmd=['ffmpeg','-v','error','-i',str(P/'playthrough-lossless.mkv')]
for n in range(3):cmd+=['-loop','1','-i',str(O/f'Bill-Easy-label-{n}.png')]
cmd+=['-filter_complex',filters,'-map','[vo]','-map','[ao]','-c:v','ffv1','-level','3','-pix_fmt','bgr0','-c:a','pcm_s16le','-t',str((2999-start)/float(fps)),'-shortest',str(master)]
subprocess.run(cmd,check=True)
subprocess.run(['ffmpeg','-v','error','-i',str(master),'-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(delivery)],check=True)
info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(delivery)],text=True));video=next(s for s in info['streams']if s['codec_type']=='video');audio=next(s for s in info['streams']if s['codec_type']=='audio')
assert int(video['nb_frames'])==2999-start and video['width']==video['height']==768 and audio['sample_rate']=='48000'
subprocess.run(['ffmpeg','-v','error','-i',str(delivery),'-f','null','-'],check=True)
report=dict(status='VERIFIED_ORDINARY_EASY_PROGRESSION_EXCERPT',rom_sha256=manifest['rom_sha256'],source_packet=str(P.relative_to(R)),source_master_sha256=sha(P/'playthrough-lossless.mkv'),source_proof_sha256=sha(P/'playthrough-lossless.verification/report.json'),native_frames=2999,source_capture_frames=3000,original_discovery_and_fixed_replay_traces_and_inputs_literal=True,controller_input=str((P/'inputs.csv').relative_to(R)),source_start_frame=start,output_frames=int(video['nb_frames']),seconds=float(info['format']['duration']),power_frames=powers,labels=labels,lossless_master_sha256=sha(master),mp4_sha256=sha(delivery),native_audio=True,behavior='Easy',gameplay_altered=False,edit='Remove menu/loading prefix, nearest-neighbor3x scaling, add phase captions above image. No gameplay cuts after the start.',goal_complete=False,limits='This bounded demonstration ends in1-1. Hard upgrades, enemy-landing comparison and final all-character routes remain open.')
(O/'Bill-Easy-Progression.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
frames=[560,1280,2620,2900];expr='+'.join(f'eq(n\\,{f-1})'for f in frames)
raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(P/'playthrough-lossless.mkv'),'-vf','select='+expr,'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
sheet=Image.new('RGB',(1024,264),'#252525');d=ImageDraw.Draw(sheet);size=256*240*3
for n,f in enumerate(frames):sheet.paste(Image.frombytes('RGB',(256,240),raw[n*size:(n+1)*size]),(n*256,24));d.text((n*256+3,3),f'frame {f}',fill='white')
sheet.save(O/'Bill-Easy-review.png')
