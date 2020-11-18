"""
Project: py-ispyb.

https://github.com/ispyb/py-ispyb

This file is part of py-ispyb software.

py-ispyb is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

py-ispyb is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with py-ispyb. If not, see <http://www.gnu.org/licenses/>.
"""


__license__ = "LGPLv3+"

from sqlalchemy import func

from app.extensions import db, auth_provider

from ispyb_core import models, schemas

from ispyb_core.modules import beamline_setup, data_collection, proposal
from ispyb_core.modules import contacts


def get_sessions(request):
    """Returns session based on query parameters

    Args:
        query_params ([type]): [description]

    Returns:
        [type]: [description]


    From SynchWeb valid query parameters include:
    prop (injected as a parameter for all queries when a proposal is selected)
    current (get the next, prev and cm visit for each beamline by type)
    all (find sessions across proposals - else get a proposal id via prop. The normal case is we want sessions from a given proposal)
    year
    month
    prev (last visit/session for this proposal)
    next (next upcoming visit/session for this proposal)
    started
    bl (beamline)
    cm (commissioning)
    ty (specific proposal types, mx, em etc)
    s (search term)
    scheduled
    per_page (number of records to return - equivalent to limit)
    page     (the page number - equivalent to offset)
    sort_by (can be ST = start date, EN = end date, VIS = visit_number, BL = beamline, LC = beamline operator, COMMENT = comment (not sure used that much!))
    order (can be 'asc' = ascending, else descending)

    We also append the data collection count, proposal type (based on beamline)

    """
    user_info = auth_provider.get_user_info_by_auth_header(
        request.headers.get("Authorization")
    )

    person_id = contacts.get_person_id_by_login(user_info["username"])

    # Primary table is the sessions table
    query = models.BLSession.query

    # Marshall the query parameters
    query_params = request.args.to_dict()

    # Session zero is used for special cases, 'all' refers to actual user sessions
    if 'all' in query_params:
        query = query.filter(models.BLSession.visit_number > 0)
    # Has a proposal been requested?
    else if 'prop' in query_params:
        query = query.join(models.Proposal).\
                filter(models.Proposal.proposalId == models.BLSession.proposalId).\
                filter(func.concat(models.Proposal.proposalCode,models.Proposal.proposalNumber) == query_params['prop'])

    # Determine which sessions this user should be able to see (assuming they are not staff/admin)
    if not user_info.get("is_admin") and person_id:
        # In reality we would want to know what sessions are coming, past, commissioning
        query = query.join(models.SessionHasPerson).\
            filter(models.SessionHasPerson.sessionId == models.BLSession.sessionId).\
            filter(models.SessionHasPerson.personId == person_id)

    if 'bl' in query_params:
        query = query.filter(models.BLSession.beamLineName == query_params['bl'])

    if 'per_page' in query_params:
        query = query.limit(query_params['per_page'])

    if 'page' in query_params:
        query = query.offset(query_params['page'])

    data = schemas.session.ma_schema.dump(query, many=True)

    response = {}
    response['total'] = len(data[0])
    response['data'] = data[0]

    return response



def add_session(data_dict):
    """Adds new session

    Args:
        session_dict ([type]): [description]

    Returns:
        [type]: [description]
    """
    return db.add_db_item(models.BLSession, schemas.session.ma_schema, data_dict)


def get_session_by_id(session_id):
    """Returns session info by its sessionId

    Args:
        session_id (int): corresponds to sessionId in db

    Returns:
        dict: info about session as dict
    """
    data_dict = {"sessionId": session_id}
    return db.get_db_item_by_params(
        models.BLSession, schemas.session.ma_schema, data_dict
    )


def get_session_info_by_id(session_id):
    """Returns session info by its sessionId

    Args:
        session_id (int): corresponds to sessionId in db

    Returns:
        dict: info about session as dict
    """
    session_json = get_session_by_id(session_id)
    if session_json:
        session_json["proposal"] = proposal.get_proposal_by_id(
            session_json["proposalId"]
        )
        session_json["beamline_setup"] = beamline_setup.get_beamline_setup_by_id(
            session_json["beamLineSetupId"]
        )
        # session_json["data_collections_groups"] = data_collection.get_data_collection_groups({"sessionId" : session_id})["data"]["rows"]

    return session_json


def get_sessions_by_date(start_date=None, end_date=None, beamline=None):
    """Returns list of sessions by start_date, end_date and beamline.

    Args:
        start_date (datetime, optional): start date. Defaults to None.
        end_date (datetime, optional): end date. Defaults to None.
        beamline (str, optional): beamline name. Defaults to None.

    Returns:
        list: list of session dicts
    """
    query = models.BLSession.query
    if start_date:
        query = query.filter(models.BLSession.startDate >= start_date)
    if end_date:
        query = query.filter(models.BLSession.endDate <= end_date)
    if beamline:
        query = query.filter(models.BLSession.beamLineName == beamline)
    return schemas.session.ma_schema.dump(query, many=True)
