import openai
import os

openai.api_key = os.getenv("openai_api_key")


def generate_ai_response(crime_data, city):

    violent_crime_list = []
    violent_crimes = crime_data['Violent Crimes']
    for crime_name, crime_values in violent_crimes.items():
        crime_value = crime_values['value']
        national_crime = crime_values['national']
        violent_crime_list.append(
            f"{crime_name} index of {crime_value} compared to the national average of {national_crime}")

    property_crime_list = []
    property_crimes = crime_data['Property Crimes']
    for crime_name, crime_values in property_crimes.items():
        crime_value = crime_values['value']
        national_crime = crime_values['national']
        property_crime_list.append(
            f"{crime_name} index of {crime_value} compared to the national average of {national_crime}")

    prompt = f"""
    Crime data for the city of {city}.

    Violent Crimes:
    {violent_crime_list}.

    Property Crimes:
    {property_crime_list}.

    Explain the summary of violent and property crimes for {city}'s crime. Provide percentages of the differences between the national and {city}'s crime rates so a 10 year old could understand.

    Share the three most dangerous areas within {city} and explain why they are dangerous.

    Provide safety tips specific to the most common crime rates within {city} and its most dangerous areas. Explain how these safety tips relate to the most common crime rates.

    format your response using tailwind css (full width with no backgound color) and html like this:

    summary 

    most dangerous areas and specific streets to stay away from

    safety tips specific to area and crime (numbered)
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=.5,
        max_tokens=750,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    print(response)

    ai_resp = response.choices[0].message.content.strip()

    return ai_resp
