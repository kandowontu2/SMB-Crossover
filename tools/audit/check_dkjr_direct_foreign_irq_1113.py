"""Isolated Ryu28 emitted-PC real-vector study; fast packing is not enabled."""
from hashlib import sha256
import json
from pathlib import Path

import check_dkjr_direct_foreign_funding_1113 as Fit
import check_dkjr_platform_contact_irq_1113 as V

P,Q,N,W=Fit.P,Fit.Q,Fit.N,Fit.W
PIN='295eddbe81bd23338b35a31a14d126671223c7a31f30cec7a24eef88dc14ee7e'


class Study:
    PARENT=Fit.T.PARENT
    ENTRY=0xb98e
    PIN=PIN

    @staticmethod
    def load_parent():return Fit.T.load_inputs(reuse_private=True)[0]

    @staticmethod
    def transform(parent):
        fixture,info=Fit.parts(parent)
        assert sha256(fixture).hexdigest()==PIN
        Study._parent=parent
        return fixture,info

    @staticmethod
    def parts():
        linked=Fit.H.T.assemble(Fit.SOURCE.read_text(),Fit.LAYOUT)
        linked['instructions']=[i for i in linked['instructions']if i['segment']=='RYU']
        return linked,[]

    @staticmethod
    def controller(raw):
        assert sha256(raw).hexdigest()==PIN
        parent=Study._parent
        assert sha256(parent).hexdigest()==Study.PARENT and Fit.parts(parent)[0]==raw
        text=P.controller(parent)
        assert text.count(Study.PARENT)==1
        return text.replace(Study.PARENT,PIN,1)


if __name__=='__main__':
    V.T=Study;V.Q.T=Study
    original_frame=Q.frame
    def declared_wrong_ID_frame(m,pad,observe=None):
        # Additional explicit legal ID25 actor in the actual cold Ryu Main.
        # Authored ID28 admission remains the existing separate fixture.
        if N.get(m,'SelectedCharacter')==10 and N.get(m,'LevelNumber')==0 and not getattr(m,'ryu28_wrong_ID_fixture',False):
            slot=3
            if N.get(m,'Enemy_Flag',slot)==1:
                m[W.address(m.bundle,'Enemy_ID')+slot]=37
                m[W.address(m.bundle,'Enemy_Y_Position')+slot]=(N.get(m,'Player_Y_Position')+32)&255
                N.invoke(m,'InitEnemyObject',x=slot)
                m[W.address(m.bundle,'Enemy_BoundBoxCtrl')+slot]=5
                m.ryu28_wrong_ID_fixture=True
        return original_frame(m,pad,observe)
    Q.frame=declared_wrong_ID_frame
    V.main()
    print('DKJR_RYU28_VECTOR_STUDY '+json.dumps(dict(
        isolated_fixture_SHA256=PIN,adapter_SHA256=sha256(Path(__file__).read_bytes()).hexdigest(),
        source_SHA256=sha256(Fit.SOURCE.read_bytes()).hexdigest(),
        ordinary_Ryu_declared_native_ID37=True,authored_Ryu_declared_native_ID40=True,
        full_fast_dispatch_enabled=False,grant=False,outputs_written=0),separators=(',',':')),flush=True)
