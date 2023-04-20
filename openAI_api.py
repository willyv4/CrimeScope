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

    prompt = f"""Crime data for {city}: violent crimes include {violent_crime_list}, and property crimes include {property_crime_list}.
    Provide an easy-to-understand summary of the differences between national and {city}'s crime rates.
    Also, please share the three most dangerous areas within {city}, explain why they are dangerous, and provide safety tips related to the most common crime rates in those areas.
    Use Tailwind CSS and HTML to format your response(full width, no background color) like this Summary, Dangerous Areas, Safety Tips.
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=.4,
        max_tokens=650,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    print(response)

    ai_resp = response.choices[0].message.content.strip()

    return ai_resp
