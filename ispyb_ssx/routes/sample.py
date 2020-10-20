# encoding: utf-8
#
#  Project: py-ispyb
#  https://github.com/ispyb/py-ispyb
#
#  This file is part of py-ispyb software.
#
#  py-ispyb is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  py-ispyb is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with py-ispyb. If not, see <http://www.gnu.org/licenses/>.

"""

Example routes:

"""

import logging
from flask import request, current_app
from flask_restx._http import HTTPStatus

from flask_restx_patched import Resource

from app.extensions.api import api_v1, Namespace
from app.extensions.auth import token_required, authorization_required

from ispyb_ssx import schemas
from ispyb_ssx.modules import loaded_sample

from ispyb_service_connector import get_ispyb_resource


__license__ = "LGPLv3+"


log = logging.getLogger(__name__)
api = Namespace("Samples", description="Samples related namespace", path="/samples")
api_v1.add_namespace(api)



@api.route("", endpoint="loaded_samples")
@api.doc(security="apikey")
class LoadedSample(Resource):
    """Loaded sample resource"""

    #@token_required
    def get(self):
        """Returns all loaded samples"""
        # app.logger.info("Return all data collections")
        return loaded_sample.get_loaded_samples(request)

    #@token_required
    @api.expect(loaded_sample_schemas.loaded_sample_f_schema)
    #@api.marshal_with(loaded_sample_schemas.loaded_sample_f_schema, code=201)
    #@authorization_required
    def post(self):
        """Adds a new loaded sample"""
        result = loaded_sample.add_loaded_sample(api.payload)
        if result is not None:
            return result, HTTPStatus.OK
        else:
            api.abort(
                HTTPStatus.NOT_ACCEPTABLE,
                "Unable to add new loaded sample"
                )

@api.route("/crystal_slurry", endpoint="crystal_slurry")
@api.doc(security="apikey")
class CrystalSlurry(Resource):
    """Crystal slurry resource"""

    #@token_required
    def get(self):
        """Returns all crystal slurry"""
        # app.logger.info("Return all data collections")
        return loaded_sample.get_all_crystal_slurry()

    #@token_required
    @api.expect(crystal_slurry_schemas.crystal_slurry_f_schema)
    #@api.marshal_with(crystal_slurry_schemas.crystal_slurry_f_schema, code=201)
    @authorization_required
    def post(self):
        """Adds a new crystal slury"""
        return loaded_sample.add_crystal_slurry(api)


@api.route("/crystal_size_distribution", endpoint="crystal_size_distribution")
@api.doc(security="apikey")
class CrystalSizeDistribution(Resource):
    """Crystal size distribution resource"""

    #@token_required
    def get(self):
        """Returns all crystal size distributions"""
        # app.logger.info("Return all data collections")
        return loaded_sample.get_crystal_size_distributions()

    #@token_required
    @api.expect(crystal_size_distribution_schemas.crystal_size_distribution_f_schema)
    #@api.marshal_with(crystal_slurry_schemas.crystal_slurry_f_schema, code=201)
    @authorization_required
    def post(self):
        """Adds a new crystal slury"""
        return loaded_sample.add_crystal_size_distribution(api)

@api.route("/sample_stocks", endpoint="sample_stocks")
@api.doc(security="apikey")
class SampleStocks(Resource):
    """Sample stocks resource"""

    #@token_required
    def get(self):
        """Returns all sample stocks"""
        # app.logger.info("Return all data collections")
        return loaded_sample.get_sample_stocks()

    #@token_required
    @api.expect(sample_stock_schemas.sample_stock_f_schema)
    #@api.marshal_with(crystal_slurry_schemas.crystal_slurry_f_schema, code=201)
    @authorization_required
    def post(self):
        """Adds a new sample stock"""
        status_code, result = loaded_sample.add_sample_stock(api.payload)
        if status_code >= 400:
            api.abort(
                HTTPStatus.NOT_ACCEPTABLE,
                result)
        else:
            return status_code, result

@api.route("/delivery_devices", endpoint="sample_delivery_devices")
@api.doc(security="apikey")
class SamplDeliveryDevices(Resource):

    """SampleDeliveryDevice resource"""

    @token_required
    @authorization_required
    def get(self):
        """
        Returns sample delivery devices.

        Returns:
            dict: response dict.
        """
        return loaded_sample.get_sample_delivery_devices(request)

    @api.expect(sample_delivery_device_schemas.sample_delivery_device_f_schema)
    @api.marshal_with(sample_delivery_device_schemas.sample_delivery_device_f_schema, code=201)
    # @api.errorhandler(FakeException)
    # TODO add custom exception handling
    @token_required
    #@authorization_required
    def post(self):
        """Adds a new sample delivery device"""
        current_app.logger.info("Inserts a new sample delivery device")

        result = loaded_sample.add_sample_delivery_device(api.payload)
        if result:
            return result, HTTPStatus.OK
        else:
            api.abort(
                HTTPStatus.NOT_ACCEPTABLE,
                "Unable to add a new sample delivery device"
                )


#return get_ispyb_resource("ispyb_core", "schemas/available_names")
