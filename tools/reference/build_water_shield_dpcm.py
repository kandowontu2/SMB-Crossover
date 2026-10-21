"""Adapt 2.02's embedded Water Shield clip to the NES's native DMC codec.

Honor the SWF seek count and source sample count, then encode at the highest
NTSC DMC rate that fits the fixed bank. Playback never depends on switchable
graphics banks, emulator audio callbacks, or CPU-driven PCM writes.
"""
from pathlib import Path
import hashlib
import json
import math
import struct
import subprocess
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]


def main():
    sound=next(i for i in ET.parse(ROOT/'reference/crossover2/main.xml').getroot().iter('item')
               if i.get('type')=='DefineSoundTag' and i.get('soundId')=='198')
    raw=bytes.fromhex(sound.get('soundData'));seek=struct.unpack('<h',raw[:2])[0]
    pcm=subprocess.check_output(['ffmpeg','-v','error','-f','mp3','-i','pipe:0',
                                  '-ar','22050','-ac','1','-f','s16le','pipe:1'],input=raw[2:])
    samples=struct.unpack('<'+'h'*(len(pcm)//2),pcm)
    samples=samples[seek:seek+int(sound.get('soundSampleCount'))]
    rate=1789773/72                 # NTSC DMC rate 14, IRQ/loop disabled.
    target=[]
    for n in range(math.ceil(len(samples)*rate/22050)):
        at=n*22050/rate;index=int(at);fraction=at-index
        value=samples[index]*(1-fraction)+samples[min(index+1,len(samples)-1)]*fraction
        target.append(64+value*45/32768)
    # Smoothly return the DAC to the game's silent zero bias.
    target.extend(max(0,64-n*2) for n in range(40))
    length=math.ceil((math.ceil(len(target)/8)-1)/16)*16+1
    target.extend([0]*(length*8-len(target)))
    level=64;data=bytearray(length)
    for n,value in enumerate(target):
        if value>=level:
            data[n//8]|=1<<(n%8)
            if level<=125:level+=2
        elif level>=2:level-=2
    assert level<=2 and len(data)<=3400
    folder=ROOT/'audio/bass';folder.mkdir(exist_ok=True)
    (folder/'water-shield.dmc').write_bytes(data)
    meta={'source_sound_id':198,'source_format':'MP3','source_seek_samples':seek,
          'source_samples':len(samples),'source_sample_rate':22050,
          'source_mp3_sha256':hashlib.sha256(raw[2:]).hexdigest(),
          'encoding':'NES DPCM','ntsc_dmc_rate':14,'sample_rate':rate,'bytes':len(data),
          'sha256':hashlib.sha256(data).hexdigest()}
    (ROOT/'docs/reference/bass-water-audio.json').write_text(json.dumps(meta,indent=2)+'\n')
    print('Water Shield source clip:',len(data),'fixed-bank DPCM bytes')


if __name__=='__main__':main()
