import django.dispatch

log_event = django.dispatch.Signal(providing_args=["domain", "actor", "variable", "pre_value", "post_value"])
