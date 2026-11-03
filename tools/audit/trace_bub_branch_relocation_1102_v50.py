"""Locate first original-instruction divergence in a private compact body."""
import json
from pathlib import Path
import check_bub_original_upgrades_1102_v49 as Q
from prepare_selected_native_packet_v1 import R
O=R/'build/bub-upgrades-root-trace-1102-v50'

def main():
    O.mkdir(exist_ok=True);old,new,route,q=Q.bundles();N=Q.N;actual=N.NesMPU;traces=[];inits=[]
    previous=Q.U.labels(R/'build/bubble-bobble-source-1101-v1/component.lbl');successor=Q.U.labels(R/'build/bub-upgrades-root-1102-v47/component.lbl')
    for bundle,labs in[(old,previous),(new,successor)]:
        m=Q.Q.fresh(bundle,route,0);Q.L.E.main_fields(m);N.put(m,Player_X_Position=96,FrameCounter=0,SavedJoypadBits=0,SavedJoypad1Bits=0,VRAM_Buffer1_Offset=0)
        inits.append(bytes(m.ram[2][:1024]));reverse={pc:name for name,pc in labs.items()if name.startswith('BbOriginal_')};rows=[]
        class Trace(actual):
            def step(self):
                if self.memory.rawtags[1]==3 and self.pc in reverse:
                    rows.append(dict(label=reverse[self.pc],A=self.a,X=self.x,Y=self.y,P=self.p,actor=list(self.memory.ram[2][0x2e:0x36]),OAM=list(self.memory.ram[2][0x100:0x108])))
                return super().step()
        N.NesMPU=Trace
        try:N.invoke(m,'GameCoreRoutine',x=0,y=0)
        finally:N.NesMPU=actual
        traces.append(rows)
    a,b=traces;at=next((i for i in range(min(len(a),len(b)))if a[i]!=b[i]),None)
    if at is None:
        result=dict(expected_negative=True,source_trace_same=True,initial_private_differences=[dict(offset=i,old=inits[0][i],new=inits[1][i])for i in range(1024)if inits[0][i]!=inits[1][i]],total_trace_rows=[len(a),len(b)],last_source_rows=a[-4:],ROM_written=False)
        (O/'negative.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));return
    result=dict(expected_negative=True,initial_private_differences=[dict(offset=i,old=inits[0][i],new=inits[1][i])for i in range(1024)if inits[0][i]!=inits[1][i]],first_divergent_trace_index=at,total_trace_rows=[len(a),len(b)],old=a[max(0,at-8):at+8],new=b[max(0,at-8):at+8],ROM_written=False)
    (O/'negative.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':main()
