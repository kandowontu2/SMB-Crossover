"""Compare continuous/segmented public-API captures pixel and PCM exactly.

This is capture calibration, not a new route or runtime test. All recordings
use the same fixed ordinary inputs and accepted ROM, without emulated writes.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
sys.path.insert(0,str(ROOT/'tools/playthroughs'))
import run_mesen
from roster_run import workspace_bytes

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--tag',required=True)
p.add_argument('--frames',type=int,default=1200)
p.add_argument('--interval',type=int,default=128)
a=p.parse_args()
assert 600<a.frames<2000 and 1<a.interval<a.frames
# Calibration deliberately exercises the bridge's unconfigured mode. A parent
# runner may have exported a guard for another destination or frame bound.
guard_names=('SMB_CAPTURE_WORKSPACE','SMB_CAPTURE_CAP_BYTES',
             'SMB_CAPTURE_SEGMENT_FRAMES','SMB_CAPTURE_FRAME_LIMIT')
cleared_guard_names=[name for name in guard_names if name in os.environ]
for name in guard_names:os.environ.pop(name,None)
used=workspace_bytes(ROOT)
reserve=a.frames*(256*240*4+8192)+512*1024*1024
assert used+reserve<30_000_000_000,'Calibration retains the conservative full-span reserve'
OUT=ROOT/'build/verification'/('capture-segments-'+a.tag)
OUT.mkdir(exist_ok=False)
rom=ROOT/'build/checkpoints/roster-audit-v45/smb-crossover-mmc3.nes'
assert sha(rom)=='e9c1a98961d26389bc54eefc4c63e725f8ddd91c0e801cf9c553bdf774ece1f1'
inputs=ROOT/'build/roster-through-2-2/mls45b-mario-fixed-a-0-v0-mmc3/inputs.csv'
fixed=list(csv.DictReader(inputs.open(newline='')))
assert len(fixed)>=a.frames
# The established runner first polls after endFrame1; there is no poll at0.
for i,row in enumerate(fixed[:a.frames]):assert int(row['poll'])==i+1 and int(row['frame'])==i+1
shutil.copyfile(inputs,OUT/'fixed-inputs.csv')
source=ROOT/'tools/playthroughs/capture_segments.c'
dll=OUT/'capture_segments.dll'
compile=subprocess.run(['gcc','-shared','-O2','-Wall','-Wextra','-Wno-cast-function-type','-o',str(dll),str(source)],capture_output=True,text=True)
(OUT/'compile.log').write_text(compile.stdout+compile.stderr)
assert compile.returncode==0
report=dict(classification='Lossless public recorder calibration; no route/final-video claim',
    rom_sha256=sha(rom),inputs_sha256=sha(inputs),source_sha256=sha(source),dll_sha256=sha(dll),
    workspace_bytes_before=used,conservative_reserve=reserve,frames=a.frames,interval=a.interval,
    guard_configuration='Explicitly absent in every calibration child',cleared_inherited_guard_names=cleared_guard_names,
    runs=[],result='running')
rp=OUT/'report.json'
rp.write_text(json.dumps(report,indent=2)+'\n')

def decode(path):
    # RGB24 checks every visible color byte. BGR0's fourth byte is undefined
    # padding, not alpha; the failed BGR0 comparison remains archived separately.
    md5=subprocess.run(['ffmpeg','-v','error','-i',str(path),'-map','0:v:0','-c:v','rawvideo','-pix_fmt','rgb24','-f','framemd5','-'],capture_output=True)
    assert md5.returncode==0,md5.stderr
    text=md5.stdout.decode()
    path.with_suffix('.framemd5').write_text(text)
    frames=[line.split(',')[-1].strip() for line in text.splitlines() if line and not line.startswith('#')]
    pcm=subprocess.run(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-c:a','pcm_s16le','-f','s16le','-'],capture_output=True)
    assert pcm.returncode==0,pcm.stderr
    probe=subprocess.run(['ffprobe','-v','error','-show_streams','-of','json',str(path)],capture_output=True,text=True,check=True)
    path.with_suffix('.streams.json').write_text(probe.stdout)
    streams=json.loads(probe.stdout)['streams']
    video=next(x for x in streams if x['codec_type']=='video')
    audio=next(x for x in streams if x['codec_type']=='audio')
    assert video['codec_name']=='zmbv' and video['width']==256 and video['height']==240
    assert audio['codec_name']=='pcm_s16le' and audio['sample_rate']=='48000' and audio['channels']==2
    return frames,pcm.stdout,dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path),bytes=path.stat().st_size,
        frames=len(frames),pcm_bytes=len(pcm.stdout),pcm_sha256=hashlib.sha256(pcm.stdout).hexdigest(),streams_sha256=sha(path.with_suffix('.streams.json')))

observed={}
for kind in ('continuous-original','continuous-new','segmented'):
    dest=OUT/kind
    dest.mkdir()
    bridge=ROOT/'build/capture_bridge.dll' if kind=='continuous-original' else dll
    os.environ['SMB_CROSSOVER_CAPTURE_AVI']=(dest/'native.avi').as_posix()
    os.environ['SMB_CAPTURE_SEGMENT_DIR']=dest.as_posix()
    script=dest/('capture-calibration-'+kind+'.lua')
    start='luaopen_capture_start' if kind=='continuous-original' else 'luaopen_segment_start'
    stop='luaopen_capture_stop' if kind=='continuous-original' else 'luaopen_segment_stop'
    script.write_text('local frame,poll=0,0\nlocal fixed={}\n'+
        'for line in io.lines('+json.dumps((OUT/'fixed-inputs.csv').as_posix())+')do local p,f,m=line:match("^(%d+),(%d+),(%d+)$");if p then fixed[tonumber(p)]={frame=tonumber(f),mask=tonumber(m)}end end\n'+
        'local start=assert(package.loadlib('+json.dumps(bridge.as_posix())+','+json.dumps(start)+'))\n'+
        'local stop=assert(package.loadlib('+json.dumps(bridge.as_posix())+','+json.dumps(stop)+'))\n'+
        'local waveStart=assert(package.loadlib('+json.dumps(dll.as_posix())+',"luaopen_segment_wave_start"))\n'+
        'local waveStop=assert(package.loadlib('+json.dumps(dll.as_posix())+',"luaopen_segment_wave_stop"))\n'+
        ('local next=assert(package.loadlib('+json.dumps(dll.as_posix())+',"luaopen_segment_next"))\n' if kind=='segmented' else '')+
        'start()\n'+
        'emu.addEventCallback(function()poll=poll+1;local v=assert(fixed[poll]);assert(v.frame==frame,"Fixed input phase");local b={};for n,k in pairs({a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1})do b[n]=(v.mask&k)>0 end;emu.setInput(b,0)end,emu.eventType.inputPolled)\n'+
        'emu.addEventCallback(function()frame=frame+1;'+
        'if frame==1 then waveStart()end;'+
        f'if frame=={a.frames} then stop();waveStop();print("PASS capture calibration fixed frames="..frame.." polls="..poll);emu.stop(0);return end;'+
        (f'if frame%{a.interval}==0 then next()end;' if kind=='segmented' else '')+
        'end,emu.eventType.endFrame)\n')
    code=run_mesen.run(script,rom,timeout=180,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
    native=ROOT/f'build/verification/{rom.stem}-{script.stem}.log'
    shutil.copyfile(native,dest/'native.log')
    assert code==0 and 'ERROR' not in native.read_text()
    parts=sorted(dest.glob('*.avi'))
    assert len(parts)==(1+(a.frames-1)//a.interval if kind=='segmented' else 1)
    hashes,audio,part_meta=[],bytearray(),[]
    for part in parts:
        vf,pcm,meta=decode(part);hashes.extend(vf);audio.extend(pcm);part_meta.append(meta)
    wave=dest/'native-audio.wav'
    pcm=subprocess.run(['ffmpeg','-v','error','-i',str(wave),'-map','0:a:0','-c:a','pcm_s16le','-f','s16le','-'],capture_output=True,check=True).stdout
    observed[kind]=(hashes,pcm)
    report['runs'].append(dict(kind=kind,native_exit=code,script_sha256=sha(script),native_log_sha256=sha(dest/'native.log'),
        parts=part_meta,total_frames=len(hashes),frame_hash_sequence_sha256=hashlib.sha256('\n'.join(hashes).encode()).hexdigest(),
        total_avi_pcm_bytes=len(audio),avi_pcm_sha256=hashlib.sha256(audio).hexdigest(),
        total_pcm_bytes=len(pcm),pcm_sha256=hashlib.sha256(pcm).hexdigest(),wave_sha256=sha(wave),
        wave_matches_avi_pcm=pcm==audio))
    rp.write_text(json.dumps(report,indent=2)+'\n')
    print(kind,len(hashes),'RGB frames',len(pcm),'continuous PCM bytes; AVI PCM',len(audio),flush=True)
base=observed['continuous-original']
report['new_bridge_identity']=observed['continuous-new']==base
report['segmented_identity']=observed['segmented']==base
report['expected_frame_count']=a.frames-1
report['result']='passed-exact-pixels-and-pcm' if len(base[0])==a.frames-1 and report['new_bridge_identity'] and report['segmented_identity'] else 'failed-preserved-for-classification'
rp.write_text(json.dumps(report,indent=2)+'\n')
print(report['result'],flush=True)
raise SystemExit(0 if report['result'].startswith('passed-') else 1)
