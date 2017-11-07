"""
RESTful API controller.

Endpoint for miscelaneous queries on specific species taxonomy.
"""

import requests
import time
import connexion
from flask import request, jsonify
from statistics import mean
from .ControllerCommon import params, settings, formatters

def taxon(taxon=None, includelower=None, hierarchy=None):
    """
    Return taxonomic hierarchy and subtaxa in various formats.

    :arg format: json, itis or csv formatted return
    """
    # Parameter checks
    if not bool(request.args):
        return connexion.problem(status=400,
                                 title='Bad Request',
                                 detail='No parameters provided.',
                                 type='about:blank')

    # Init core returned objects
    desc_obj = dict()
    indicies = set()
    occ_return = list()

    # Parse return type
    if show:
        show_params = show.lower().split(',')
    else:
        show_params = list()

    # Query PBDB from systemics
    if hiearchy:
        t0 = time.tim()
        base_url = settings.config('db_api', 'pbdb') + 'taxa/list.json'
        payload = dict()
        payload.update(vocab='pbdb', show='full', order='hierarchy')
        payload.update(name=taxon)

        resp = requests.get(base_url,
                            params=payload,
                            timeout=settings.config('timeout', 'pbdb'))
