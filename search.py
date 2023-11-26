import difflib
def preprocess_text(text):
    ptext = ''
    for e in text:
        if e.isalnum() or e.isspace():
            ptext += e.lower()
        else:
            ptext += " "
    return ptext.split()

def calculate_similarity(tokens_a, tokens_b):
    print("tokens_a = ",tokens_a)
    print("tokens_b = ",tokens_b)
    # Calculate similarity based on Levenshtein distance of tokens
    total_similarity = sum(max(difflib.SequenceMatcher(None, token_a, token_b).ratio() for token_b in tokens_b) for token_a in tokens_a)
    total_similarity /= len(tokens_a)
    print("total_similarity = ",total_similarity)
    return total_similarity

def search_strings(dictionary, search_string):
    search_tokens = preprocess_text(search_string)
    relevant_ids = []

    for key, value in dictionary.items():
        value_tokens = preprocess_text(value)
        similarity = calculate_similarity(search_tokens, value_tokens)
        
        # Adjust the threshold as needed
        if similarity > 0.6:  # You can modify this threshold
            relevant_ids.append(key)

    return relevant_ids

## Example dictionary
#example_dict = {
#    1: "John plays with his dog.",
#    2: "Hotdog competition.",
#    3: "Bird drinks water.",
#    # Add more strings to your dictionary
#}
#
## Search for a query
#query = "birs drink water"  # Change the query as needed
#result_ids = search_strings(example_dict, query)
#print("IDs of relevant strings:", result_ids)
#
