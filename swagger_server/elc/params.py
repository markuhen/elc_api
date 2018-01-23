"""Common parameter parsing functions for the API controllers."""


def set_options(req_args, endpoint):
    """Return a dictionary with runtime options and config."""
    from ..elc import config

    # Add aditional formats and controls below (default is param[0])
    spec = dict()
    spec.update(occ=['json', 'csv'])
    spec.update(loc=['json', 'csv'])
    spec.update(tax=['json', 'csv'])
    spec.update(ref=['bibjson', 'ris', 'itis'])
    spec.update(show=['all', 'poll', 'idx'])
    spec.update(age=['ma', 'ka', 'yr'])
    spec.update(geog=['paleo', 'modern'])

    # Configure options

    options = dict()

    if 'output' in req_args.keys():
        if req_args.get('output').lower() in spec.get(endpoint):
            options.update(output=req_args.get('output'))
        else:
            msg = 'Allowable formats: {0:s}'.format(str(spec.get(endpoint)))
            raise ValueError(400, msg)
    else:
        options.update(output=spec.get(endpoint)[0])

    if 'show' in req_args.keys():
        if req_args.get('show').lower() in spec.get('show'):
            options.update(show=req_args.get('show'))
        else:
            msg = 'Allowable show args: {0:s}'.format(str(spec.get('show')))
            raise ValueError(400, msg)
    else:
        options.update(show=spec.get('show')[0])

    if 'ageunits' in req_args.keys():
        if req_args.get('ageunits').lower() in spec.get('age'):
            options.update(ageunits=req_args.get('ageunits'))
        else:
            msg = 'Allowable age units: {0:s}'.format(str(spec.get('age')))
            raise ValueError(400, msg)
    else:
        options.update(ageunits=config.get('default', 'ageunits'))

    if 'coords' in req_args.keys():
        if req_args.get('coords').lower() in spec.get('geog'):
            options.update(coords=req_args.get('coords'))
        else:
            msg = 'Allowable coordinates: {0:s}'.format(str(spec.get('geog')))
            raise ValueError(400, msg)
    else:
        options.update(coords=config.get('default', 'coordinates'))

    return options


def id_parse(ids, db, endpoint):
    """
    Separate database:datatype:id_number from a list.
    
    :arg ids: array of database specific object identifiers in above format
    :type ids: list (of str)
    :arg db: database name to parse on
    :type db: str
    :arg endpoint: endpoint to parse on 
    :type endpoint: str

    """
    import re

    numeric_ids = list()
    db_tag = db[:4]

    # Add additional db specific locale eqivalents here
    loc_spec = ['col', 'dst']

    for id in ids:
        database = re.search('^\w+(?=:)', id).group()
        datatype = re.search('(?<=:).+(?=:)', id).group()
        id_num = int(re.search('\d+$', id).group())

        if endpoint == 'loc':
            if database.lower() == db_tag and datatype.lower() in loc_spec:
                numeric_ids.append(id_num)
        elif endpoint not in loc_spec:
            if database.lower() == db_tag and datatype.lower() == endpoint:
                numeric_ids.append(id_num)

    return numeric_ids


def parse(req_args, db, endpoint):
    """Return a Requests payload specific to resource target."""
    import ast
    from ..elc import config, aux

    spec = dict()
    spec.update(occ=['bbox', 'minage', 'maxage', 'ageunits', 'timerule',
                     'taxon', 'includelower', 'limit', 'offset', 'show',
                     'output'])
    spec.update(loc=['occid', 'bbox', 'minage', 'maxage', 'ageunits',
                     'timerule', 'taxon', 'includelower', 'limit', 'offset',
                     'show'])
    spec.update(tax=['taxon', 'includelower', 'hierarchy'])
    spec.update(ref=['idnumbers', 'format'])

    # Bad or missing parameter checks

    if not bool(req_args):
        msg = 'No parameters provided.'
        raise ValueError(400, msg)

    for param in req_args.keys():
        if param not in spec.get(endpoint):
            msg = 'Unknown parameter \'{0:s}\''.format(param)
            raise ValueError(400, msg)

    if db not in config.db_list():
        msg = 'Database support lacking: \'{0:s}\''.format(db)
        raise ValueError(501, msg)

    # Set defaults

    if 'includelower' in req_args.keys():
        inc_sub_taxa = ast.literal_eval(req_args.get('includelower'))
    else:
        inc_sub_taxa = config.get('default', 'includelower')

    if 'ageunits' in req_args.keys():
        age_units = req_args.get('ageunits')
    else:
        age_units = config.get('default', 'ageunits')

    if 'limit' in req_args.keys():
        resp_limit = req_args.get('limit')
    else:
        resp_limit = config.get('default', 'limit')

    # Generate sub-query api payload

    payload = dict()

    payload.update(limit=resp_limit)

    payload.update(aux.set_db_special(db))

    if 'taxon' in req_args.keys():
        try:
            payload.update(aux.set_taxon(db=db,
                                         taxon=req_args.get('taxon'),
                                         inc_sub_taxa=inc_sub_taxa))
        except SyntaxError as err:
            raise ValueError(err[0], err[1])

    if 'offset' in req_args.keys():
        payload.update(offset=req_args.get('offset'))

    return payload