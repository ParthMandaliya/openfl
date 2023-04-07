import ray


def make_remote(f: callable, ref=None):
    f = ray.put

    @ray.remote
    def wrapper(*args, **kwrgs):
        clone = args[0]
        f = getattr(clone, args[1])
        collaborator = ref

        f()

        if hasattr(collaborator, 'init_a'):
            print (collaborator.init_a)

    return wrapper
