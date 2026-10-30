from .bearnet import BearNet
from .donkeynet import DonkeyNet

arch_registry = {
    "bearnet": BearNet,
    "donkeynet": DonkeyNet,
}

def create_custom_model(arch: str, *args, **kwargs):
    model_constructor = arch_registry.get(arch)
    if not model_constructor:
        raise ValueError(f"Model architecture: {arch} is not registered.")
    return model_constructor(*args, **kwargs)
