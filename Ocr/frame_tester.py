from overwatch_matchers.assist_matcher import if_assist
from overwatch_matchers.eliminated_matcher import if_got_elimed, if_menu, if_objective_defense, if_orb_gain, if_blocking
from overwatch_matchers.elimination_matcher import if_got_elim
from overwatch_matchers.elimination_counter import count_elim_on_frame
from overwatch_matchers.healing_matcher import if_healing
from overwatch_matchers.prepare_matcher import if_prepare_attack, if_prepare_defense, if_escort, if_contested
from overwatch_matchers.slept_matches import if_slept
from overwatch_matchers.spawn_room_matcher import if_in_hero_room, if_in_queue


class FrameTester:
    """
        A text testing class for text ocr'd out of frames
    """

    def is_elimed_frame(self, text: str) -> bool:
        """

        :param text: The frame text to check for the elimed condition
        :return: if the condition matches
        """
        return if_got_elimed(text)

    def is_first_menu_frame(self, text: str) -> bool:
        """

        :param text: The frame text to check for the elimed condition
        :return: if the condition matches
        """
        return if_menu(text);

    def is_elim_frame(self, text: str) -> bool:
        """

        :param text: The frame text to check for the elimed condition
        :return: if the condition matches
        """
        return if_got_elim(text)

    def is_defense(self, text: str) -> bool:
        """

        :param text: The frame text to check for the elimed condition
        :return: if the condition matches
        """
        return if_objective_defense(text)

    def is_orb_gained(self, text: str) -> bool:
        """

        :param text: The frame text to check for the elimed condition
        :return: if the condition matches
        """
        return if_orb_gain(text)

    def is_blocking(self, text: str) -> bool:
        """

        :param text: The frame text to check for the elimed condition
        :return: if the condition matches
        """
        return if_blocking(text)

    def is_elim_frame(self, text: str) -> bool:
        """

        :param text: The frame text to check for the elim condition
        :return: if the condition matches
        """
        return if_got_elim(text)

    def is_spawn_room_frame(self, text: str) -> bool:
        """

        :param text: The frame text to check for the spawn_room condition
        :return: if the condition matches
        """
        return if_in_hero_room(text)

    def is_in_queue(selfself, text: str) -> bool:
        """

        :param text: The frame text to check for the in_queue condition
        :return: if the condition matches
        """
        return if_in_queue(text)

    def is_heal_frame(self, text) -> bool:
        """

        :param text: The frame text to check for the heal condition
        :return: if the condition matches
        """
        return if_healing(text)

    def is_slept_frame(self, text) -> bool:
        """

        :param text: The frame text to check for the heal condition
        :return: if the condition matches
        """
        return if_slept(text)

    def is_assist_frame(self, text) -> bool:
        """

        :param text: The frame text to check for the heal condition
        :return: if the condition matches
        """
        return if_assist(text)

    def count_elim_frame(self, text) -> int:
        """

        :param text: The frame text to check for the elim condition
        :return: How many times the condition matches
        """
        return count_elim_on_frame(text)

    def is_in_prepare_attack(self, text) -> bool:
        """

        :param text: The frame text to check for the prepare_attack condition
        :return: if the condition matches
        """
        return if_prepare_attack(text)

    def is_in_escort(self, text) -> bool:
        """

           :param text: The frame text to check for the escort condition
           :return: if the condition matches
           """
        return if_escort(text)
    def is_in_contested(self, text) -> bool:
        """

           :param text: The frame text to check for the escort condition
           :return: if the condition matches
           """
        return if_contested(text)


    def is_in_prepare_defense(self, text) -> bool:
        """

        :param text: The frame text to check for the prepare_defense condition
        :return: if the condition matches
        """
        return if_prepare_defense(text)
