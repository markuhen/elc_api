"""
RESTful API controller.

Endpoint for miscelaneous queries on specific species taxonomy.
"""

import connexion
import flask_csv
from ..elc import config, params, aux, subreq
from ..handlers import router
from http_status import Status
from time import time
from flask import jsonify


def tax(taxon=None, idlist=None, includelower=None, hierarchy=None, run=None):
    """Information about specific taxa."""
    return_obj = list()
    desc_obj = dict()

    # Set runtime options

    try:
        options = params.set_options(req_args=connexion.request.args,
                                     endpoint='tax')

    except ValueError as err:
        return connexion.problem(status=err.args[0],
                                 title=Status(err.args[0]).name,
                                 detail=err.args[1],
                                 type='about:blank')

    run_list = aux.get_run_list(connexion.request.args.get('run'))

    # Cycle through external databases

    for db in run_list:

        t0 = time()
        options.update(skip=False)

        # Configure parameter payload for api subquery

        try:
            payload = params.parse(req_args=connexion.request.args,
                                   options=options,
                                   db=db,
                                   endpoint='tax')

        except ValueError as err:
            return connexion.problem(status=err.args[0],
                                     title=Status(err.args[0]).name,
                                     detail=err.args[1],
                                     type='about:blank')

        # skip this database if no ids specified

        if options.get('skip'):
            continue

        # Database API call

        url_path = ''.join([config.get('resource_api', db),
                            config.get('db_tax_endpt', db)])

        try:
            resp_json, api_call = subreq.trigger(url_path, payload, db)

        except ValueError as err:
            return connexion.problem(status=err.args[0],
                                     title=Status(err.args[0]).name,
                                     detail=err.args[1],
                                     type='about:blank')

        # Parse database response

        return_obj = router.response_decode(resp_json=resp_json,
                                            return_obj=return_obj,
                                            options=options,
                                            db=db,
                                            endpoint='tax')

        # Build returned metadata object

        desc_obj.update(aux.build_meta(options))

        desc_obj.update(aux.build_meta_sub(data=return_obj,
                                           source=api_call,
                                           t0=t0,
                                           sub_tag=db,
                                           options=options))

    # Return composite data structure to client

    if options.get('output') == 'json':
        if options.get('show') == 'poll':
            return jsonify(desc_obj)
        if options.get('show') == 'idx':
            return jsonify(aux.get_id_numbers(data=return_obj,
                                              endpoint='tax'))
        else:
            return jsonify(metadata=desc_obj, records=return_obj)

    elif options.get('output') == 'csv':
        if return_obj:
            filename = aux.build_filename(endpoint='tax', data=return_obj)
            return flask_csv.send_csv(return_obj,
                                      filename,
                                      return_obj[0].keys())
        else:
            msg = 'Unable to generate CSV file. Search returned no records.'
            return jsonify(status=204,
                           title=Status(204).name,
                           detail=msg,
                           type='about:blank')
    # DEVELOPMENT
    return jsonify(options)
