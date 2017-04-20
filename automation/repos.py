import os

class Repos():
    def callsign_from_group_num(self, group_num):
        digits = ["ZERO", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE"]
        callsign = [digits[int(d)] for d in str(group_num)]
        return "".join(callsign)

    def generate_uri(self, api_address, callsign):
        uri = api_address + "/diffusion/" + callsign + "/"
        return uri

repos = Repos()
