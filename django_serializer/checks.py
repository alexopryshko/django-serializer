def check_registered_views(app_config, **kwargs):
    errors = []
    for view in registered_views:
        errors.extend(view.check(app_config, **kwargs))

    return errors
