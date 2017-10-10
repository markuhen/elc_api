"""
RESTful API controller.

Endpoint for queries on geolocated locales.
Dataset identifiers are returned for Neotoma and collection identifiers
for the PBDB.
"""

from flask import request, jsonify
import requests
import time
from statistics import mean


def loc(occid=None, bbox=None, minage=None, maxage=None, agescale=None, timerule=None, taxon=None, includelower=None):
    """
    Return locale identifiers from Neotoma and PBDB.

    A locale in PBDB is a collection, in Neotoma it is every individual
    dataset in a site.
    """
    # Initialization and parameter checks

    if request.args == {}:
        return jsonify(status_code=400, error='No parameters provided.')

    desc_obj = dict()
    loc_return = list()
    age_units = 'ma'
    geog_units = 'dec_deg_modern'
    full_return = False

    #
    # Query the Neotoma Database (Datasets)
    #
    # t0 = time.time()
    # neotoma_base = 'http://apidev.neotomadb.org/v1/data/datasets'
    # payload = dict()

    # ### if occid:

    # if bbox:
    #     payload.update(bbox=bbox)

    # if agescale and agescale.lower() == 'yr':
    #     age_scaler = 1
    #     age_units = 'yr'
    #     if minage:
    #         payload.update(ageyoung=int(minage))
    #     if maxage:
    #         payload.update(ageold=int(maxage))
    # elif agescale and agescale.lower() == 'ka':
    #     age_scaler = 1e-03
    #     age_units = 'ka'
    #     if minage:
    #         payload.update(ageyoung=int(minage/age_scaler))
    #     if maxage:
    #         payload.update(ageold=int(maxage/age_scaler))
    # else:
    #     age_scaler = 1e-06
    #     age_units = 'ma'
    #     if minage:
    #         payload.update(ageyoung=int(minage/age_scaler))
    #     if maxage:
    #         payload.update(ageold=int(maxage/age_scaler))

    # if timerule and timerule.lower() == 'major':
    #     payload.update(agedocontain=0)
    # elif timerule and timerule.lower() == 'overlap':
    #     payload.update(agedocontain=1)

    # if includelower and includelower.lower() == 'false':
    #     payload.update(nametype='tax', taxonname=taxon)
    # else:
    #     payload.update(nametype='base', taxonname=taxon)

    # neotoma_res = requests.get(neotoma_base, params=payload, timeout=None)
    
    # ### Parse neotoma response





    #
    # Query the Paleobiology Database (Collections)
    #

    t0 = time.time()
    base_url = 'http://paleobiodb.org/data1.2/colls/list.json'
    payload = dict()
    payload.update(vocab='pbdb', show='loc')

    # Parse arguments and format database api parameters

    if occid:
        payload.update(occ_id=occid)

    if bbox:
        bbox_list = bbox.split(',')
        payload.update(lngmin=bbox_list[0], latmin=bbox_list[1],
                       lngmax=bbox_list[2], latmax=bbox_list[3])

    if agescale and agescale.lower() == 'yr':
        age_scaler = 1e06
        age_units = 'yr'
        if minage:
            payload.update(min_ma=float(minage)/age_scaler)
        if maxage:
            payload.update(max_ma=float(maxage)/age_scaler)
    elif agescale and agescale.lower() == 'ka':
        age_scaler = 1e03
        age_units = 'ka'
        if minage:
            payload.update(min_ma=float(minage)/age_scaler)
        if maxage:
            payload.update(max_ma=float(maxage)/age_scaler)
    else:
        age_scaler = 1
        age_units = 'ma'
        if minage:
            payload.update(min_ma=minage)
        if maxage:
            payload.update(max_ma=maxage)

    if timerule:
        payload.update(timerule=timerule)

    if includelower and includelower.lower() == 'false':
        payload.update(taxon_name=taxon)
    else:
        payload.update(base_name=taxon)

    # Issue GET request to database API
    resp = requests.get(base_url, params=payload, timeout=5)

    if resp.status_code == 200:
        resp_json = resp.json()
        if 'records' in resp_json:
            for rec in resp_json['records']:
                loc_obj = dict()
                loc_id = 'pbdb:loc:' + str(rec.get('collection_no'))
                loc_obj.update(lat=rec.get('lat'),
                                lon=rec.get('lng'),
                                name=rec.get('collection_name'),
                                dataset_type='faunal',
                                min_age=min_age,
                                max_age=max_age,
                                age_basis=None,
                                loc_id=loc_id,
                                occurrences=occ_list)

                # Add the fomatted locale data to the return
                loc_return.append(loc_obj)

            # Build the JSON description object
            t1 = round(time.time()-t0, 3)
            desc_obj.update(pbdb={'response_time': t1,
                                  'subqueries': resp.url,
                                  'record_count': len(resp_json['records'])})
    # Composite response

    return jsonify(description=desc_obj, records=loc_return)