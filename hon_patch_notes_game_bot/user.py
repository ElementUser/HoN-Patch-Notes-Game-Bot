
class RedditUser:
    def __init__(self, id, username: str) -> None:
        """
        Parametrized constructor

        Attributes:
            id
            username
        """

        self.id = id
        self.username = username
        self.can_submit_guess = True
        self.is_potential_winner = False
        self.num_guesses = 1
        self.guess_post_ids = []