import logging

import angr
import archinfo

from .plugin_base import PluginBase

log = logging.getLogger(__name__)


class CCDomainDetection(PluginBase):
    """
    This analysis monitors for calls to functions that are commonly used to communicate with Command and Control Severs
    """

    supported_arch = [arch_info[3] for arch_info in archinfo.arch_id_map]

    def __init__(self, proj: angr.Project, simgr: angr.SimulationManager):
        super().__init__(proj, simgr)
        log.debug("C&C Domain plugin initialized")
        self.functions_monitored = [
            "socket",
            "InternetUrlOpenA",
            "Open",
            "HttpSendRequestA",
            "HttpOpenRequestA",
            "InternetConnectA",
        ]

    def simprocedure(self, state: angr.SimState):
        """
        Tracks all SimProcedure calls and checks if it is calling a monitored function
        """

        proc = state.inspect.simprocedure
        if proc is None:
            # Handle syscall SimProcedures
            log.debug("Reached a syscall SimProcedure")
            return
        proc_name = proc.display_name
        #log.debug(f"TRACKING: SimProcedure call:{proc_name}")

        if proc_name not in self.functions_monitored:
            return

        if proc_name == "socket":
            log.info(
                f"Detected possible C&C Domain: {proc.arg(0)} with DoC {state.doc.concreteness:.2f}"
            )

        if proc_name == "InternetOpenUrlA":
            log.info(
                f"Detected possible C&C Domain: {proc.arg(1)} with DoC {state.doc.concreteness:.2f}"
            )

        if proc_name == "Open":
            if proc.library_name == "IWinHttpRequest":
                log.info(
                    f"Detected possible C&C Domain: {proc.arg(1)} with DoC {state.doc.concreteness:.2f}"
                )

        if proc_name == "HttpSendRequestA":
            log.info(
                f"Detected possible unknown external C&C with DoC {state.doc.concreteness:.2f}"
            )
            
        if proc_name == "HttpOpenRequestA":
            log.info(
                f"Detected possible C&C domain: {proc.arg(0)} {state.doc.concreteness:.2f}"
            )
        if proc_name == "InternetConnectA":
            log.info(
                f"Detected possible C&C domain: {proc.arg(1)} {state.doc.concreteness:.2f}"
            )
        
