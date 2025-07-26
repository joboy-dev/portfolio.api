import random
from fastapi import HTTPException
from typing import List, Optional

from api.v1.schemas.base import AdditionalInfoSchema


def generate_logo_url(name: str):
    return f"https://ui-avatars.com/api/?name={name}"


def generate_unique_id(
    name: Optional[str]="Korede", 
    passes: int = 6
):
    '''Function to geenrate a random unique id
    '''
        
    first_three_letters = name[:3].upper()
    
    # Convert first three letter to ascii
    ascii_str = ''.join(str(ord(char)) for char in first_three_letters)
    ascii_int = int(ascii_str)
    
    # Determine number of number passes for the loop
    if passes < 5:
        passes = 5
    elif passes > 10:
        passes = 10
        
    number_string = ""
    
    for _ in range(passes):
        random_number = f'{random.randint(0, 9)}'
        number_string +=random_number
    
    # Generate unique id
    id_number = ascii_int + int(number_string)
    unique_id = f"{first_three_letters}{id_number}"
        
    return unique_id


def format_additional_info_create(additional_info: List[AdditionalInfoSchema]):
    '''Function to help format additional info for create endpoints into JSON format'''
    
    data = {info.key: info.value for info in additional_info}
    print(data)

    return data
    

def format_additional_info_update(
    additional_info: List[AdditionalInfoSchema], 
    model_instance, 
    model_instance_additional_info_name: str = 'additional_info',
    keys_to_remove: Optional[List[str]]=None
):
    '''Function to help format additional info for update endpoints for an existing object'''
    
    current_additional_info_dict_copy = (
        getattr(model_instance, model_instance_additional_info_name).copy() 
        if getattr(model_instance, model_instance_additional_info_name) 
        else {}
    )
    
    for info in additional_info:
        current_additional_info_dict_copy[info.key] = info.value
    
    if keys_to_remove:    
        for key in keys_to_remove:
            if key not in list(current_additional_info_dict_copy.keys()):
                print(f'Key {key} does not exist in dictionary')
                continue
            
            del current_additional_info_dict_copy[key]
    
    print(current_additional_info_dict_copy)
    return current_additional_info_dict_copy


def format_attributes_update(attributes: List[AdditionalInfoSchema], model_instance, keys_to_remove: Optional[List[str]]=None):
    '''Function to help format attributes for update endpoints for an existing object'''
    
    current_attributes_dict_copy = model_instance.attributes.copy()
    
    for info in attributes:
        current_attributes_dict_copy[info.key] = info.value
    
    if keys_to_remove:
        for key in keys_to_remove:
            if key not in list(current_attributes_dict_copy.keys()):
                print(f'Key {key} does not exist in dictionary')
                continue
            
            del current_attributes_dict_copy[key]
    
    print(current_attributes_dict_copy)
    return current_attributes_dict_copy


def check_user_is_owner(user_id: str, model_instance, user_fk_name: str):
    """
    Check if the user has permission to access a resource based on a foreign key field.
    user_id is not necessariyl going to be a id field on the User table. It could be a
    id field on any table that mimicks user in a way eg supplier, customer, business partner.
    """
    
    resource_user_id = getattr(model_instance, user_fk_name, None)
    
    if resource_user_id is None:
        raise HTTPException(500, f"Model `{model_instance.__name__}` does not have attribute `{user_fk_name}`")
    
    if user_id != resource_user_id:
        raise HTTPException(403, 'You do not have permission to access this resource')
    

def generate_random_hex():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))


def generate_pin(passes: int = 4):
    '''Function to generate a pin'''
    
    number_string = ""
    
    for _ in range(passes):
        random_number = f'{random.randint(0, 9)}'
        number_string +=random_number
        
    return number_string


def format_seconds_to_hms(seconds: float) -> str:
    """
    Convert seconds to HH:MM:SS format
    
    Args:
        seconds: Time duration in seconds (can be float or int)
        
    Returns:
        str: Formatted time string (HH:MM:SS)
        
    Examples:
        >>> format_seconds_to_hms(3661.5)
        '01:01:01'
        >>> format_seconds_to_hms(45)
        '00:00:45'
    """
    
    # Handle negative values
    is_negative = seconds < 0
    seconds = abs(seconds)
    
    # Calculate components
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    # Format as 2-digit strings
    hours_str = f"{int(hours):02d}"
    minutes_str = f"{int(minutes):02d}"
    seconds_str = f"{int(seconds):02d}"
    
    # Combine with sign if needed
    sign = "-" if is_negative else ""
    return f"{sign}{hours_str}:{minutes_str}:{seconds_str}"


# async def translate_text(text: str, destination_language: str='fr'):
#     '''Function to help translate text with googletrans package'''
    
#     translator = Translator()
#     result = await translator.translate(text, dest=destination_language)
#     return result.text
