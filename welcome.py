class Welcome(Selection):
    """Ammonia welcome screen."""

    INTERACTIONS = {
        LCD.UP: {'method': 'select_next_item', 'args': ()},
        LCD.DOWN: {'method': 'select_prev_item', 'args': ()},
        LCD.SELECT: {'method': 'transition_to_item', 'args': ()}
    }

    ITEMS = ('measure', 'calibrate')


    def __init__(self, lcd):
        super(Selection, self).__init__(lcd, self.INTERACTIONS, self.ITEMS)
