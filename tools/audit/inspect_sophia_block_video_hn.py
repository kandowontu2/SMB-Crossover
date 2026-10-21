"""Retained, read-only inspection of the user's Sophia block-shift video."""
from pathlib import Path
import hashlib
import json
import subprocess
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'build/verification/root49-sophia-block-shift-hn'
OUT.mkdir(parents=True, exist_ok=True)
VIDEO = Path('C:/Users/kando/Downloads/a.mp4')
probe = json.loads(subprocess.check_output([
    'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_frames',
    '-show_entries', 'frame=best_effort_timestamp_time,pkt_duration_time',
    '-of', 'json', str(VIDEO)]))
(OUT/'video-frames.json').write_text(json.dumps(probe, indent=2), encoding='utf-8')
raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(VIDEO),
    '-vf', 'fps=1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', 'pipe:1'])
size = 256*240*3
assert len(raw) % size == 0
count = len(raw)//size
sheet = Image.new('RGB', (8*256, ((count+7)//8)*264), '#262626')
draw = ImageDraw.Draw(sheet)
for n in range(count):
    x,y = (n%8)*256, (n//8)*264
    sheet.paste(Image.frombytes('RGB', (256,240), raw[n*size:(n+1)*size]), (x,y+24))
    draw.text((x+4,y+4), f'{n}s', fill='white')
sheet.save(OUT/'overview.png')
(OUT/'video-review-binding.json').write_text(json.dumps({
    'input': str(VIDEO), 'sha256': hashlib.sha256(VIDEO.read_bytes()).hexdigest(),
    'bytes': VIDEO.stat().st_size, 'decoded_frames': len(probe['frames']),
    'private_cap_bytes': 100_000_000, 'reserve_bytes': 20_000_000,
    'global_cap_bytes': 100_000_000_000,
    'scope': 'Read-only video and bounded source/native Sophia block-shift diagnosis. Retain all files.'
}, indent=2), encoding='utf-8')
print(json.dumps({'frames':len(probe['frames']), 'overview':str(OUT/'overview.png')}))
