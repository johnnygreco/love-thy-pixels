from IPython.display import Image


def _get_image(url, width):
    return Image(url=url, width=width)


def earth_atm_opacity(width=1000):
    url = 'https://upload.wikimedia.org/wikipedia/commons/'\
          '3/34/Atmospheric_electromagnetic_opacity.svg'
    return _get_image(url, width)


def anglular_diameter(width=800):
    url = 'https://upload.wikimedia.org/wikipedia/commons/'\
          'e/ed/Angular_diameter.jpg'
    return _get_image(url, width)
