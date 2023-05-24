import openai
import os
import time

openai.api_key = os.getenv("openai_api_key")


def generate_ai_response(v_crime, p_crime, city):

    prompt = f"""
    Act as a local familiar crime in {city}.

    Use this Crime data {city} for your response: violent crimes include {v_crime}, and property crimes include {p_crime}.

    Create a response based on the following:

    - Share the 3 most dangerous areas within {city} and explain why they are dangerous, and provide a safety tip accordingly.
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=.7,
        max_tokens=300,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    print(response)

    ai_resp = response.choices[0].message.content.strip()

    return ai_resp


def job():
    try:
        ai_resp = generate_ai_response("0", "0", "ivins, ut")
    # Do something with the response if needed
    except Exception as e:
        # Handle the error or perform any necessary actions
        print(f"Error occurred in generate_ai_response: {e}")

    # Schedule the next execution after 2.5 hours
    time.sleep(2.5 * 60 * 60)
    job()


# Start the initial execution
job()
