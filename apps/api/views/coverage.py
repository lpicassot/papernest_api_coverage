import json
import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.api.utils import get_address, get_coverage, get_provider_name

logger = logging.getLogger(__name__)

class CoverageView(APIView):
    """
    Response with all coverages from a user address.
    """
   
    def get(self, request):
        address = request.GET.get('q', None)
        logger.info("Received address request: {}".format(address))
        message = {}
        try:
            if address is not None:
                # Retrieve Address from provided API
                transformed_address = get_address(address)
                if transformed_address is None:
                    message['status'] = 'Error: Provided Address can not be get located or is wrong'
                    return Response(message, status=status.HTTP_400_BAD_REQUEST)
                transformed_address_json = json.loads(transformed_address)
  

                # Check if response contains relevant data
                if transformed_address_json.get('features', None) is None or len(transformed_address_json.get('features')) == 0:
                    message['status'] = 'Error: Address couldnt be found'
                    return Response(message, status=status.HTTP_400_BAD_REQUEST)
                
                # Retrieve from options the one with higher probability of accuracy
                selected_address = {"properties": {"score": 0}}
                minimum_score = 0.4
                for feature in transformed_address_json.get('features'):
                    if feature['properties']['score'] > selected_address['properties']['score'] and feature['properties']['score'] > minimum_score:
                        selected_address = feature
                logger.info(selected_address)

                # Address not identified from API. Response with error
                if selected_address['properties']['score'] < minimum_score:
                    message['status'] = 'Error: Address provided couldnt be identified'
                    return Response(message, status=status.HTTP_400_BAD_REQUEST)
                    

                # Extract coordinates (long and lat) from API response
                coordinates = [selected_address['geometry']['coordinates'][0],selected_address['geometry']['coordinates'][1]]
                logger.info(coordinates)

                # Obtain coverage for selected coordinates and check if it was found
                coverage_data = get_coverage(coordinates)
                if coverage_data is None:
                    message['status'] = 'Error: Address not found in database'
                    return Response(message, status=status.HTTP_400_BAD_REQUEST)
                
                # Create object with desired format for Response
                logger.info(coverage_data)
                for key, value in coverage_data.items():
                    message[get_provider_name(key)] = {
                          '2G': True if value[0] else False,
                          '3G': True if value[1] else False,
                          '4G': True if value[2] else False,
                        }

                logger.info(message)
                # Return Response in json format
                return Response(message, status=status.HTTP_200_OK)
            else:
                message['status'] = 'Error: Address not provided'
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.warning("There was an exception exceutin CoverageView")
            logger.exception(e)
            message['status'] = 'There was an internal server Error'
            return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)