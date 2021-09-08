import logging


class CookieMoneyHelper:
    KNOWN_SUFFIXES = {
        'million': 1_000_000,
        'billion': 1_000_000_000
    }

    @staticmethod
    def convert_string_value_to_int(value: str) -> int:
        if len(val_list := value.split()) > 1:
            # im assuming there is only 2 elements in this str -> 1.2 Trillion | 3.4 Billion etc
            suffix_val = CookieMoneyHelper.KNOWN_SUFFIXES.get(val_list[1].lower(), 0)
            if not suffix_val:
                logging.warning("Unknown suffix %s encountered", val_list[1])
            return int(val_list[0].replace('.', '')) * suffix_val

        return int(value.replace(',', ''))
