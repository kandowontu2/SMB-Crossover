"""Create review excerpts of identified defects from retained native masters."""
from pathlib import Path
import csv,json,subprocess,hashlib
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2];O=R/'Playthrough Videos/Review Clips'
assert not O.exists();O.mkdir()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)],text=True))
clips=[('Bill-green-tiles-1-3',3,0,239.,248.),('Bass-underground-block-colors',9,0,96.,102.),('Rygar-screen-jump',7,0,81.,84.),('Lance-screen-jump',3,1,108.,111.),('Pit-block-contact-review',6,0,231.,234.),('Ryu-wall-contact-review',10,0,86.,91.)]
manifest=[]
for label,ch,v,start,end in clips:
 packet=R/'build/roster-through-2-2'/f'claude-final-video-{ch}-v{v}-mmc3';source=packet/'playthrough-lossless.mkv';m=json.loads((packet/'manifest.json').read_text())
 # These are editorial extracts of existing footage, not fresh gameplay replays.
 master=O/(label+'-lossless.mkv');delivery=O/(label+'.mp4')
 subprocess.run(['ffmpeg','-v','error','-ss',str(start),'-i',str(source),'-t',str(end-start),'-map','0:v:0','-map','0:a:0','-c:v','ffv1','-level','3','-c:a','pcm_s16le',str(master)],check=True)
 subprocess.run(['ffmpeg','-v','error','-i',str(master),'-vf','scale=768:720:flags=neighbor','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(delivery)],check=True)
 info=probe(delivery);streams={s['codec_type']:s for s in info['streams']};assert 'audio'in streams and 'video'in streams;assert streams['video']['width']==768 and streams['video']['height']==720
 # Decode both streams fully to check the delivery, keeping diagnostics small.
 subprocess.run(['ffmpeg','-v','error','-i',str(delivery),'-f','null','-'],check=True)
 manifest.append(dict(label=label,source=str(source.relative_to(R)),source_sha256=sha(source),rom_sha256=m['rom_sha256'],start_seconds=start,end_seconds=end,lossless_master_sha256=sha(master),mp4_sha256=sha(delivery),duration=float(info['format']['duration']),native_audio=True,controller_input=str((packet/'inputs.csv').relative_to(R)),kind='Excerpt from existing full controller recording; no gameplay alteration.'))
 (O/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8');print('REVIEW_CLIP',label,manifest[-1]['duration'],flush=True)
# Save one clear representative frame separately for the user's reference.
 source=R/'build/roster-through-2-2/claude-final-video-3-v0-mmc3/playthrough-lossless.mkv'
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(source),'-vf','select=eq(n\\,14598)','-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
 Image.frombytes('RGB',(256,240),raw).resize((768,720),Image.Resampling.NEAREST).save(O/'Bill-green-tiles-frame-14599.png')
print('COMPLETE',len(manifest),flush=True)
