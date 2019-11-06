"""Blocking result object."""


class CandidateBlockingResult:
    """Object for holding blocking results."""

    def __init__(self, blocks, extra={}):
        """Initalize a blocking result object.

        :param blocks: dict
        :param extra: dict (optional)
        """
        self.blocks = blocks
        self.extra = extra