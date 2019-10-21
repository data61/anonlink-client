def filter_signatures(candidate_signatures, filter_config):
    typ = filter_config.get('type', 'not specified')
    if typ == 'none':
        return candidate_signatures
    else:
        NotImplementedError(f"filter type '{typ}' is not implemented, yet")
