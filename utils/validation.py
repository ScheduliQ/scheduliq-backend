from cerberus import Validator

def validate_data(data, schema):
    """
    Validates the given data against the provided schema.
    
    Args:
        data (dict): The data to validate.
        schema (dict): The schema to validate against.
    
    Returns:
        dict: The validated and normalized data.
    
    Raises:
        ValueError: If validation fails.
    """
    validator = Validator(schema)
    if not validator.validate(data):
        raise ValueError(f"Validation failed: {validator.errors}")
    return validator.document  # Return validated and normalized data
