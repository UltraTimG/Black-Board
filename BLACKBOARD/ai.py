from openai import OpenAI

client = OpenAI(
  api_key="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"
)

def ask_query(query):
  response = client.responses.create(
      model="gpt-4o-mini",
      input=query,
      store=True,
  )
  return response.output_text
  return ' this is a response to our ask query'
