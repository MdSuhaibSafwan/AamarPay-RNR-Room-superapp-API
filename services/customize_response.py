def customize_response(response, custom_message):
    if response.data is None:
        response.data = {
            'detail': 'Successful'
        }
    else:
        response.data = {
            'detail': response.data
        }
    response.data['message'] = custom_message
    return response
