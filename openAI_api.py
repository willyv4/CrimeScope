import openai
from config import openai_api_key


openai.api_key = openai_api_key


def generate_ai_response(crime_data, city):
    # structure api data dynamically for prompt

    # extract and compare violent crime data
    violent_crime_list = []
    violent_crimes = crime_data['Violent Crimes']
    for crime_name, crime_values in violent_crimes.items():
        crime_value = crime_values['value']
        national_crime = crime_values['national']
        violent_crime_list.append(
            f"{crime_name} index of {crime_value} compared to the national average of {national_crime}")

    # extract and compare property crime data
    property_crime_list = []
    property_crimes = crime_data['Property Crimes']
    for crime_name, crime_values in property_crimes.items():
        crime_value = crime_values['value']
        national_crime = crime_values['national']
        property_crime_list.append(
            f"{crime_name} index of {crime_value} compared to the national average of {national_crime}")

    # Set up the crime data prompt
    prompt = f"""
    Crime data for the city of {city}

    Violent Crimes:
    {violent_crime_list}

    Property Crimes:
    {property_crime_list}

    Provide a simple summary about {city}'s crime and illustrate the likelihood of crime victimization as a percentage.

    If there is crime related dangerous areas within {city} name the top 3 and explain why and provide 3 safety tips in this {city}.

    If not explain 3 ways to safe in {city} and it's surrounding areas in terms of weather and wildlife.
    """

    # Set up the chat API parameters
    model = "text-davinci-003"
    temperature = .75
    max_tokens = 750

    # Call the chat API to generate a response
    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    # Print the response
    ai_resp = response.choices[0].text.strip()

    print("#############################################")
    print("#############################################")
    print("#############################################")
    print(crime_data)
    print("#############################################")
    print("#############################################")
    print("#############################################")
    print(prompt)
    print("#############################################")
    print("#############################################")
    print("#############################################")
    print(ai_resp)
    print("#############################################")
    print("#############################################")
    print("#############################################")

    return ai_resp
