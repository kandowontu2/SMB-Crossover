import sys,subprocess
from pathlib import Path
sys.path.insert(0,'tools/audit')
from prepare_selected_native_packet_v1 import prepare,sha
source=Path('build/mini-combined-camera-native-1110/route/controller.lua');rom=Path('build/mini-combined-camera-native-1110/candidate.nes');out=Path('build/mini-combined-camera-native-1110/route-v2')
s=source.read_text();assert s.count('read(0x071a)*256+read(0x071c)')==1;s=s.replace('read(0x071a)*256+read(0x071c)','read(0x071d)*256+read(0x071f)')
prepare(out,rom,s,{source},expected=sha(rom),timeout=180,allow_interactive=True,scope='Correct native camera address observer; retained full1-1 and offscreen spawn assertions.')
subprocess.run([sys.executable,'-B',str(out/'run.py')],check=True)
