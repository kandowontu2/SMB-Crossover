"""Losslessly mux native ZMBV parts with the continuous native PCM recording."""
from pathlib import Path
import argparse
import decimal
from fractions import Fraction
from array import array
import hashlib
import json
import math
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/playthroughs'))
from roster_run import workspace_bytes, CAP_BYTES
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--directory',required=True,type=Path)
p.add_argument('--output',required=True,type=Path)
p.add_argument('--expected-frames',required=True,type=int)
p.add_argument('--workspace-cap-bytes',type=int,default=CAP_BYTES)
a=p.parse_args()
assert a.workspace_cap_bytes>0
a.workspace_cap_bytes=min(a.workspace_cap_bytes,CAP_BYTES)
source=a.directory.resolve();output=a.output.resolve()
assert source.is_relative_to(ROOT) and output.is_relative_to(ROOT)
assert output.suffix=='.mkv' and not output.exists()
parts=sorted(source.glob('part-*.avi'))
assert parts and [p.name for p in parts]==[f'part-{i:04d}.avi'for i in range(len(parts))]
wave=source/'native-audio.wav';assert wave.exists()
reserve=sum(p.stat().st_size for p in parts)+wave.stat().st_size+a.expected_frames*4096+64*1024*1024
used=workspace_bytes(ROOT)
assert used+reserve<a.workspace_cap_bytes,'Reserve existing compressed bytes plus generous remux overhead'
check=output.with_suffix('.verification')
check.mkdir(exist_ok=False)
report=dict(classification='Lossless remux; not gameplay completion by itself',result='running',workspace_bytes_before=used,
    workspace_cap_bytes=a.workspace_cap_bytes,remux_reserve_bytes=reserve,expected_frames=a.expected_frames,
    inputs=[],wave=dict(path=str(wave.relative_to(ROOT)),sha256=sha(wave)))
rp=check/'report.json'
def save():rp.write_text(json.dumps(report,indent=2)+'\n')
save()

def frames(path,dest):
    v=subprocess.run(['ffmpeg','-v','error','-i',str(path),'-map','0:v:0','-c:v','rawvideo','-pix_fmt','rgb24','-f','framemd5','-'],capture_output=True,check=True)
    dest.write_bytes(v.stdout)
    return [line.split(',')[-1].strip() for line in v.stdout.decode().splitlines() if line and not line.startswith('#')]
def pcm(path):
    proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-c:a','pcm_s16le','-f','s16le','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    h=hashlib.sha256();size=0;peak=0
    while block:=proc.stdout.read(1024*1024):
        h.update(block);size+=len(block)
        values=array('h');values.frombytes(block)
        if sys.byteorder!='little':values.byteswap()
        peak=max(peak,abs(min(values)),abs(max(values)))
    err=proc.stderr.read();code=proc.wait();assert code==0,err
    return dict(bytes=size,sha256=h.hexdigest(),peak=peak)

lines=['ffconcat version 1.0'];all_frames=[];rate=None
decimal.getcontext().prec=40
for i,path in enumerate(parts):
    probe=subprocess.run(['ffprobe','-v','error','-show_streams','-of','json',str(path)],capture_output=True,text=True,check=True)
    (check/f'part-{i:04d}.streams.json').write_text(probe.stdout)
    video=next(x for x in json.loads(probe.stdout)['streams']if x['codec_type']=='video')
    assert video['codec_name']=='zmbv' and video['width']==256 and video['height']==240
    current=Fraction(video['avg_frame_rate']);assert current>0
    if rate is None:rate=current
    assert rate==current
    hashes=frames(path,check/f'part-{i:04d}.rgb.framemd5');assert len(hashes)==int(video['nb_frames'])
    all_frames.extend(hashes)
    # Explicit VIDEO duration avoids the deliberately unused gapped AVI audio
    # deciding the concatenation timeline. No frame/sample interpolation.
    duration=decimal.Decimal(len(hashes))*decimal.Decimal(rate.denominator)/decimal.Decimal(rate.numerator)
    assert "'"not in str(path),'FFconcat quoting requires a path without apostrophes'
    lines.extend(["file '"+path.as_posix()+"'",'duration '+str(duration)])
    report['inputs'].append(dict(path=str(path.relative_to(ROOT)),sha256=sha(path),frames=len(hashes)))
assert len(all_frames)==a.expected_frames
concat=check/'video.ffconcat';concat.write_text('\n'.join(lines)+'\n')
command=['ffmpeg','-n','-hide_banner','-loglevel','warning','-f','concat','-safe','0','-i',str(concat),'-i',str(wave),
    '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','copy','-fps_mode','passthrough',str(output)]
run=subprocess.run(command,capture_output=True,text=True)
(check/'ffmpeg.log').write_text(run.stdout+run.stderr)
report['mux_exit']=run.returncode;save();assert run.returncode==0
actual=frames(output,check/'master.rgb.framemd5')
source_pcm,master_pcm=pcm(wave),pcm(output)
packets=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_packets','-show_entries',
    'packet=pts_time','-of','json',str(output)],capture_output=True,text=True,check=True)
(check/'master-timestamps.json').write_text(packets.stdout)
times=[float(p['pts_time'])for p in json.loads(packets.stdout)['packets']]
time_errors=[abs(t-i/float(rate))for i,t in enumerate(times)]
timing_ok=len(times)==len(actual) and all(a<b for a,b in zip(times,times[1:])) and max(time_errors)<0.0011
audio_seconds=master_pcm['bytes']/192000
video_seconds=len(actual)/float(rate)
report.update(video_rgb_identity=actual==all_frames,total_frames=len(actual),continuous_pcm_identity=source_pcm==master_pcm,
    source_pcm=source_pcm,master_pcm=master_pcm,output=dict(path=str(output.relative_to(ROOT)),bytes=output.stat().st_size,sha256=sha(output)),
    frame_hash_sequence_sha256=hashlib.sha256('\n'.join(actual).encode()).hexdigest(),
    ignored_segment_audio=True,video_reencoded=False,frame_or_sample_interpolation=False,
    timestamps_passed=timing_ok,max_video_timestamp_error_seconds=max(time_errors),
    audio_seconds=audio_seconds,video_seconds=video_seconds,
    audio_peak_dbfs=20*math.log10(master_pcm['peak']/32768)if master_pcm['peak']else None)
passed=(actual==all_frames and source_pcm==master_pcm and timing_ok and master_pcm['peak']>0
    and abs(audio_seconds-video_seconds)<0.1)
report['result']='passed-exact-rgb-and-pcm' if passed else 'failed-preserved-for-classification'
save();print(report['result'],len(actual),'frames',master_pcm['bytes'],'PCM bytes',flush=True)
raise SystemExit(0 if report['result'].startswith('passed-')else 1)
