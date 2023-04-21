import openai
import os

openai.api_key = os.getenv("openai_api_key")


def generate_ai_response(crime_data, city):

    violent_crime_list = []
    violent_crimes = crime_data['Violent Crimes']

    for crime_name, crime_values in violent_crimes.items():
        crime_value = crime_values['value']
        national_crime = crime_values['national']
        violent_crime_list.append({
            'crime': crime_name,
            'city': crime_value,
            'national': national_crime
        })

    property_crime_list = []
    property_crimes = crime_data['Property Crimes']
    for crime_name, crime_values in property_crimes.items():
        crime_value = crime_values['value']
        national_crime = crime_values['national']
        property_crime_list.append({
            "crime": crime_name,
            "city": crime_value,
            "national": national_crime
        })

    prompt = f"""
    Use this Crime data for {city}: violent crimes include {violent_crime_list}, and property crimes include {property_crime_list}.

    Create a response based on the following:
    
    - Share the 3 most dangerous areas within {city} and explain why they are dangerous, and provide a safety tip accordingly.
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=.7,
        max_tokens=320,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    print(response)

    ai_resp = response.choices[0].message.content.strip()

    return ai_resp
