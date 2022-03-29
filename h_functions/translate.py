
cyr_lat = {
    "а":"a", "б":"b", "в":"v", "г":"g", "д":"d", 
    "е":"e", "ё":"yo", "ж":"je", "з":"ze", "и":"i", 

    "й":"ii", "к":"k", "л":"l", "м":"m", "н":"n", 
    "о":"o", "п":"p", "р":"r", "с":"s", "т":"t", 

    "у":"u", "ф":"f", "х":"h", "ц":"c", "ч":"ch", 
    "ш":"sh", "щ":"s", "ъ":"", "э":"ae", "ь":"", 

    "ю":"u", "я":"ya", " ":"_"#, "\\":"\n"
}


def cyrIntoLat(cyrilic_str:str):
    p_str = cyrilic_str.lower()
    n_str = ""
    
    accepted = list(cyr_lat.keys())

    for s in p_str:
        if s in accepted:
            n_str += cyr_lat[s]

    return n_str

