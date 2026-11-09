import sys
from pathlib import Path
sys.path.insert(0,'tools/audit')
from prepare_selected_native_packet_v1 import prepare,sha
import subprocess
source=Path('build/mini-move-offscreen-recovery-v2-1110/controller.lua');rom=Path('build/mini-box-terrain-visible-1110/candidate.nes');out=Path('build/mini-move-baseline-recovery-1110')
text=source.read_text().replace('b096eaa968c1b52b60477b7105fae79b2b13bee164e00414795ba7742845c673',sha(rom))
prepare(out,rom,text,{source},expected=sha(rom),timeout=180,allow_interactive=True,scope='Same improved controller on installed6af baseline, real1-1 three lifts and active1-2.')
subprocess.run([sys.executable,'-B',str(out/'run.py')],check=True)
