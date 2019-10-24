from collections import defaultdict


def create_reverse_index(block_filter, cbf_map, sig_rec_map, config):
    """

    :param block_filter: The combined blocking filter - a numpy bool array.
    :param cbf_map: Dict mapping blocking filter index to list of signatures.
    :param sig_rec_map: Dict mapping signatures to records.
    :return:
        Dict mapping block indentification to list of records.
    """
    method_type = config.get('type', 'not provided')
    if method_type == 'not provided':
        raise ValueError("reverse-index type not provided.")

    if method_type == 'index-based-blocks':
        return _single_index_reverse_index(block_filter, cbf_map, sig_rec_map, config)
    elif method_type == 'signature-based-blocks':
        return _signature_based_reverse_index(block_filter, cbf_map, sig_rec_map, config)
    else:
        raise ValueError("reverse index type '{}' is not recognized.".format(method_type))


def _single_index_reverse_index(blocking_filter, cbf_map, sig_to_record_map, config):
    """
    Each 1 in the blocking filter represents a block.
    :param blocking_filter:
    :param cbf_map:
    :param sig_to_record_map:
    :param config:
    :return:
        Dict mapping block indentification to list of records.
    """
    # We do not use the config here
    block_map = {}
    for i in range(len(blocking_filter)):
        if blocking_filter[i] == 1:
            block_map[i] = [y for x in cbf_map[i] for y in sig_to_record_map[x]]
    return block_map


def _signature_based_reverse_index(block_filter, cbf_map, sig_rec_map, config):
    raise NotImplementedError("implement me, please")


def create_block_list_lookup(block_filter, cbf_map, sig_rec_map, config):
    """

    :param block_filter: The combined blocking filter - a numpy bool array.
    :param cbf_map: Dict mapping blocking filter index to list of signatures.
    :param sig_rec_map: Dict mapping signatures to records.
    :return:
        Dict mapping record id to list of blocks it belongs to.
    """
    method_type = config.get('type', 'not provided')
    if method_type == 'not provided':
        raise ValueError("reverse-index type not provided.")

    if method_type == 'index-based-blocks':
        return _single_index_block_list_lookup(block_filter, cbf_map, sig_rec_map)
    elif method_type == 'signature-based-blocks':
        return _signature_based_block_list_lookup(block_filter, cbf_map, sig_rec_map)
    else:
        raise ValueError("reverse index type '{}' is not recognized.".format(method_type))


def _single_index_block_list_lookup(blocking_filter, cbf_map, sig_to_record_map):
    """
    Each 1 in the blocking filter represents a block.
    :param blocking_filter:
    :param cbf_map:
    :param sig_to_record_map:
    :return:
        Dict mapping record id to list of blocks it belongs to.
    """
    block_map = defaultdict(list)
    for i in range(len(blocking_filter)):
        if blocking_filter[i] == 1:
            for x in cbf_map[i]:
                for y in sig_to_record_map[x]:
                    block_map[y].append(i)
    return block_map


def _signature_based_block_list_lookup(block_filter, cbf_map, sig_rec_map):
    # reverse cbf_map
    sig_pos = defaultdict(list)
    for pos, sig_list in cbf_map.items():
        for sig in sig_list:
            sig_pos[sig].append(pos)
    for sig, positions in sig_pos.items():
        if not all(block_filter[i] for i in positions):
            del sig_rec_map[sig]
    #now reverse sig_rec_map...
    block_map = defaultdict(list)
    for sig, rec_ids in sig_rec_map.items():
        for rec_id in rec_ids:
            block_map[rec_id].append(sig)
    return block_map
