import openai
import os

openai.api_key = os.getenv("openai_api_key")


def generate_ai_response(crime_data, city):

    violent_crime_list = []
    violent_crimes = crime_data['Violent Crimes']
    for crime_name, crime_values in violent_crimes.items():
        crime_value = crime_values['value']
        national_crime = crime_values['national']
        difference = national_crime - crime_value
        percent_difference = difference / national_crime * 100
        percent_difference = int(round(percent_difference))

        violent_crime_list.append({
            'crime': crime_name,
            'city': crime_value,
            'national': national_crime,
            'difference': difference,
            'percent_difference': percent_difference
        })

    # extract and compare property crime data
    property_crime_list = []
    property_crimes = crime_data['Property Crimes']
    for crime_name, crime_values in property_crimes.items():
        crime_value = crime_values['value']
        national_crime = crime_values['national']
        difference = national_crime - crime_value
        percent_difference = difference / national_crime * 100
        percent_difference = int(round(percent_difference))
        property_crime_list.append({
            'crime': crime_name,
            'city': crime_value,
            'national': national_crime,
            'difference': difference,
            'percent_difference': percent_difference
        })

    prompt = f"""
    Act as a local familiar crime in {city}.

    Use this Crime data {city} for your response: violent crimes include {violent_crime_list}, and property crimes include {property_crime_list}.

    Create a response based on the following:
    
    - Share the 3 most dangerous areas within {city} and explain why they are dangerous, and provide a safety tip accordingly.
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=.7,
        max_tokens=360,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    print(response)

    ai_resp = response.choices[0].message.content.strip()

    return ai_resp
