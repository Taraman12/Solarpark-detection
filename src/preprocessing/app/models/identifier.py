import re


class Identifier:
    def __init__(self, identifier_string):
        IDENTIFIER_REGEX = re.compile(
            r"""(?P<mission>S2[A-B])_MSI
                (?P<product_level>L[1-2][A-C])_
                (?P<sensing_time>\d{8}T\d{6})_
                (?P<processing_baseline>N\d{4})_
                (?P<relative_orbit>R\d{3})_T
                (?P<utm_code>\d{2})
                (?P<latitude_band>\w{1})
                (?P<square>\w{2})_
                (?P<year>\d{4})
                (?P<month>\d{2})
                (?P<day>\d{2})T
                (?P<product_time>\d{6})""",
            re.VERBOSE,
        )
        match = IDENTIFIER_REGEX.match(identifier_string)
        if match:
            self.mission = match.group("mission")
            self.product_level = match.group("product_level")
            self.sensing_time = match.group("sensing_time")
            self.processing_baseline = match.group("processing_baseline")
            self.relative_orbit = match.group("relative_orbit")
            self.utm_code = match.group("utm_code")
            self.latitude_band = match.group("latitude_band")
            self.square = match.group("square")
            self.year = match.group("year")
            self.month = match.group("month")
            self.day = match.group("day")
            # remove leading zero
            self.month_no_leading_zeros = str(int(match.group("month")))
            self.day_no_leading_zeros = str(int(match.group("day")))
            self.product_time = match.group("product_time")
            self.tile = f"{self.utm_code}{self.latitude_band}{self.square}"
            self.tile_date = f"{self.year}-{self.month}-{self.day}"
            self.tile_date_no_leading_zeros = (
                f"{self.year}-{self.month_no_leading_zeros}-{self.day_no_leading_zeros}"
            )
        else:
            raise ValueError(f"Invalid identifier string: {identifier_string}")

    def to_string(self):
        return f"{self.mission}_MSI{self.product_level}_{self.sensing_time}_{self.processing_baseline}_{self.relative_orbit}_T{self.utm_code}{self.latitude_band}{self.square}_{self.year}{self.month}{self.day}T{self.product_time}"
