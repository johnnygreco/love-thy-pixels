from IPython.display import Image


wikipath = 'https://upload.wikimedia.org/wikipedia/commons/'


def _get_image(url, width):
    return Image(url=url, width=width)


def earth_atm_opacity(width=1000):
    url =  wikipath + '3/34/Atmospheric_electromagnetic_opacity.svg'
    return _get_image(url, width)


def anglular_diameter(width=800):
    url = wikipath + 'e/ed/Angular_diameter.jpg'
    return _get_image(url, width)


def star_field(width=800):
    url = wikipath + '8/89/Sagittarius_Star_Cloud.jpg'
    return _get_image(url, width)


def stellar_evolution(width=800):
    url = wikipath + '/4/47/Star_Life_Cycle_Chart.jpg'
    return _get_image(url, width)
