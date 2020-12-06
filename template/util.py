import yaml
from matplotlib.ticker import FuncFormatter


def millions(x, pos):
    return "£%1.1fM" % (x * 1e-6)


formatter = FuncFormatter(millions)


def loader(fname):
    with open(fname) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    return data
