from rest_framework.serializers import ValidationError as SerializerValidationError


def structure_api_data_or_send_validation_error(data, raise_exception=False):
    success = data.get("success", None)
    print("Success", success)
    if success is None:
        if raise_exception == True:
            raise SerializerValidationError(data.get("api_data"))
    if success == True:
        del data["success"]
        del data["error"]
        return data.get("api_data")
    
    if raise_exception == True:
        raise SerializerValidationError(data.get("api_data"))
    
    return data.get("api_data")

