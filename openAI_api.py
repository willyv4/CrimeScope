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
    Act as a local crime expert sharing safety tips about crime.

    Here is Crime data for {city} to reference throughout your response: violent crimes include {violent_crime_list}, and property crimes include {property_crime_list}.

    - Provide overall differences between national and {city}'s crime rates using percentages.

    - Illustrate the likelihood of being a victim in {city}.

    - Share the 3 most dangerous areas within {city} and explain why they are dangerous in detail. 

    - Provide in-depth safety tips specific to the most dangerous areas and the crimes with the highest rate in {city}'s neighborhoods. 

    - Explain how your safety tips will decrease being invovled with crime.
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=.9,
        max_tokens=850,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    print(response)

    ai_resp = response.choices[0].message.content.strip()

    return ai_resp

#     <div class = "w-full p-4" >
#   <p class="pt-2 pb-2 mb-2">

#   </p>
#   <div class="flex flex-wrap">
#     <div class="w-full lg:w-1/2">
#       <h1 class="text-xl font-bold mb-2">Violent Crime</h1>
#       <ul class="list-disc ml-4">
#         <li>Assault:</li>
#         <li>Murder:</li>
#         <li>Rape:</li>
#         <li>Robbery:</li>
#       </ul>
#     </div>
#     <div class="w-full lg:w-1/2">
#       <h1 class="text-xl font-bold mb-2">Property Crime</h1>
#       <ul class="list-disc ml-4">
#         <li>Burglary:</li>
#         <li>Theft:</li>
#         <li>Motor Vehicle Theft:</li>
#       </ul>
#     </div>
#   </div>
#   <div class='mt-2 mb-2'>
#   <p>
#   </p>
#   </div>
#   <h3 class="text-2xl mb-2 mt-2 font-bold">Dangerous Areas in {city}<h3>
#   <p class="pt-2 pb-2 mb-2">

#   </p>
#   <p class="pt-2 pb-2 mb-2">
#     Explain why they are dangerous.
#   </p>
#   <h3 class="text-2xl mt-2 mb-2 font-bold">Safety Tips for {city}</h3>
#   <p class="pt-2 pb-2 mb-2">
#   </p>
#   <div class="mb-2 mt-2">
#   <p class="pt-2 pb-2">
#   </p>
#   </div>
# </div>
