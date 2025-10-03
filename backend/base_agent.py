from llm_main import llm

def baseAgent(pet):

    prompt = f"""
      Give me top 5 names for {pet}
    """
    res = llm.invoke(prompt)
    print(res.content)
    return res

if __name__ == "__main__":
    baseAgent("dog")