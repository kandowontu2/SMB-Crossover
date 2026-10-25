from pathlib import Path
D=Path(__file__).resolve().parent
t=(D/'run_kirby_copies_v2.py').read_text()
old="rom=R/'build/checkpoints/native-items-px/candidate.nes'";assert t.count(old)==1
t=t.replace(old,"rom=D/'wave-candidate-v1/candidate.nes'").replace('kirby-copies-v2','kirby-copies-wave-v1')
(D/'run_kirby_copies_wave_v1.py').write_text(t)
