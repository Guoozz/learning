class RegisterClass(type):

    def __init__(cls, name, bases, dit):
        super(RegisterClass, cls).__init__(name, bases, dit)
        if not hasattr(cls, "register"):
            cls.register = set()
        for base in bases:
            if "Mixin" in base.__name__:
                cls.register.add(base)

    def __str__(cls):
        return ",".join([c.__name__ for c in cls.register])

    def __iter__(cls):
        return iter(cls.register)


class AMixin(object):
    def __init__(self):
        self.a1 = 3


class BMixin(object):
    def __init__(self):
        self.b1 = 4


class CMixin(object):
    def __init__(self):
        self.c1 = 5


class BaseManager(metaclass=RegisterClass):

    def __init__(self):
        for Mixin in self.register:
            instance = Mixin()
            for key, value in instance.__dict__.items():
                if hasattr(self, key):
                    raise TypeError("existed key: {}".format(key))
                setattr(self, key, value)


class AManger(BaseManager, AMixin, BMixin, CMixin):
    pass


m = AManger()
print(m.a1)
print(m.b1)
print(m.c1)

