class RedditUser:
    def __init__(
        self,
        name: str,
        can_submit_guess: bool = True,
        is_potential_winner: bool = False,
        num_guesses: int = 0,
    ) -> None:
        """
        Parametrized constructor
        """

        self.name = name
        self.can_submit_guess = can_submit_guess
        self.is_potential_winner = is_potential_winner
        self.num_guesses = num_guesses
