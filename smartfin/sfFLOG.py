from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional

import matplotlib.pyplot as plt


@dataclass
class FLOGEntry:
    timestamp: int
    message: str
    parameter: int
    sequence: int

def importFlog(flog_path: Path) -> List[FLOGEntry]:
    entries: List[FLOGEntry] = []
    with open(flog_path) as f:
        for seq_idx, line in enumerate(f):
            timestamp = int(line[:8].strip())
            message = line[9:41].strip()
            parameter = int(line[56:].strip(), 16)
            entries.append(FLOGEntry(
                timestamp=timestamp,
                message=message,
                parameter=parameter,
                sequence=seq_idx
            ))
    return entries

class STATES(Enum):
    STATE_NULL          = 0x0000
    STATE_DEEP_SLEEP    = 0x0001
    STATE_SESSION_INIT  = 0x0002
    STATE_DEPLOYED      = 0x0003
    STATE_UPLOAD        = 0x0004
    STATE_CLI           = 0x0005
    STATE_MFG_TEST      = 0x0006
    STATE_TMP_CAL       = 0x0007
    STATE_CHARGE        = 0x0008

def plotStateSequence(entries: List[FLOGEntry], ax: Optional[plt.Axes] = None):
    if ax is None:
        ax = plt.gca()
    ax.plot([state.sequence for state in entries], [state.parameter for state in entries])
    ax.set_yticks([state.value for state in STATES], [state.name for state in STATES])
    ax.grid()
