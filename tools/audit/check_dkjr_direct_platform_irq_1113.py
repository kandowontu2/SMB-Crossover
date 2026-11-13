"""All direct-fast/worker PCs with actual IRQ and matched busy NMI."""
import compose_dkjr_direct_platform_1113 as T
import check_dkjr_platform_contact_irq_1113 as V


class Adapter:
    PARENT,ENTRY,PIN=T.PARENT,T.ENTRY,T.PIN
    load_parent=staticmethod(T.load_parent)
    transform=staticmethod(T.transform)
    controller=staticmethod(T.controller)

    @staticmethod
    def parts():
        linked,rows=T.parts()
        # Preserve the common vector harness's exact native/foreign bank map.
        for item in linked['instructions']:
            item['segment']={'POLICY':'RESTORE','WORKER_A':'GENERIC_A','WORKER_B':'GENERIC_B'}.get(item['segment'],item['segment'])
        return linked,rows


if __name__=='__main__':
    V.T=Adapter;V.Q.T=Adapter
    V.main()
