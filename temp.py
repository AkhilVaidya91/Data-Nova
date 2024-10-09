string = "Reviewed in India on 24 July 2024"

def get_demographics(string):
    if len(string) > 10:
        strings = string.split(" ")
        country = strings[2]
        date = strings[4]
        month = strings[5]
        year = strings[6]

        return str(country), int(date), str(month), int(year)
    else:
        return None, None, None, None
    
print(get_demographics(string))