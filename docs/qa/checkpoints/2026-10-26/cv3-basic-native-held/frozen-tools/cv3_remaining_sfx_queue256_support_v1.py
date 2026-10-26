"""Explicit owned-voice interpretation for the private256-slot proposal."""
from cv3_remaining_sfx_complete_cpu_v1 import init,sound,EVENTS,source_voices
def target_voices(q):
 owned=q.get('Cv3FxOwned')
 noise=q.get('Cv3FxNoiseID')if owned&8 else 0
 if q.get('Cv3NoiseActive')==1:noise=0x1f if q.get('Cv3NoiseIndex')<28 else 0
 return(q.get('Cv3FxPulseID')if owned&1 else 0,noise)
