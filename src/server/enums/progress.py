from enum import Enum


class AnnihilationProgressEnum(Enum):
    """
    Enumeration representing progress states for an annihilation process.

    This enum defines standard milestones in a long-running annihilation operation,
    with each state assigned a percentage value indicating completion progress.
    The values progress from 0 (not started) to 100 (complete/error), with
    intermediate states showing the workflow progression.

    Note:
        The ERROR state is set to 100% to indicate process completion with failure,
        while DONE represents successful completion at 100%.

    Parameters:
        NOT_STARTED (0): Process has not yet begun
        PREPARE_WORK (15): Initial preparation phase
        STARTING_WORK (30): Process initialization
        WORK_STARTED (50): Main work has begun
        WORK_COMPLETED (80): Primary work finished
        FINALIZING_WORK (90): Cleanup and finalization
        DONE (100): Successful completion
        ERROR (100): Process failed but reached completion state
    """

    NOT_STARTED = 0
    PREPARE_WORK = 15
    STARTING_WORK = 30
    WORK_STARTED = 50
    WORK_COMPLETED = 80
    FINALIZING_WORK = 90
    DONE = 100
    ERROR = 100

    def __repr__(self) -> str:
        """
        Returns a human-readable string representation of the progress state.

        Returns:
            str: The name of the enum member in title case
        """
        return self.name.replace("_", " ").title()
