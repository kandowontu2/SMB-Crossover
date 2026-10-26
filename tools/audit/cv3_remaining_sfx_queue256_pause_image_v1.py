"""Retain per-update voice images across actual pause and pending release."""
from pathlib import Path
import hashlib,json
from check_tmnt_render_oa import load
from cv3_remaining_sfx_queue256_support_v1 import init,sound
from cv3_dmc_complete_cpu_v1 import apu
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/cv3-remaining-queue256-v1')
p=D/'candidate-v3/candidate.nes';q=init(load(p),3);sound(q,0x24);rows=[]
def row(stage):
 rows.append(dict(stage=stage,pulse={n:[q.get(n,i)for i in range(4)]for n in ['GuestNativeApu','GuestApuLast','GuestNativeDirty','Cv3FxPulseApu','Cv3FxPulseMusic']},state={n:q.get(n)for n in ['Cv3FxOwned','Cv3NoiseActive','Cv3FxPendingNoise','Cv3FxPendingPulse','Cv3FxPulseID','Cv3FxPulseFrame','RgAudioSilenced','GamePauseStatus']},APU=apu(q)))
for i in range(12):q.invoke('AudioUpdate');row('active'+str(i))
q.put(GamePauseStatus=1);sound(q,0x13);row('incoming')
for i in range(3):q.invoke('AudioUpdate');row('pause'+str(i))
q.put(GamePauseStatus=0,RgAudioSilenced=0)
for i in range(4):q.invoke('AudioUpdate');row('resume'+str(i))
out=D/'pause-image-negative-v1';out.mkdir(exist_ok=False);(out/'proof.json').write_text(json.dumps(dict(accepted=False,ROM_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),rows=rows),indent=2)+'\n');print(json.dumps(rows[-9:],indent=2))
