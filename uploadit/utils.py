

def callable_from_string(string_or_callable):
    """
        Thanks to https://github.com/mbi/django-simple-captcha/blob/master/captcha/conf/settings.py#L31
        for this snippet.
    """
    if string_or_callable is None:
        return
    elif callable(string_or_callable):
        return string_or_callable
    else:
        return getattr(__import__('.'.join(string_or_callable.split('.')[:-1]), {}, {}, ['']), string_or_callable.split('.')[-1])