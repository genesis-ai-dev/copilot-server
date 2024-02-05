try:
    import tools.edit_distance as edit_distance
except ImportError:
    import edit_distance
import json
import os
from typing import List, Dict
import uuid
# from codex_types.types import Dictionary as DictionaryType
# from codex_types.types import DictionaryEntry
import string
translator = str.maketrans('', '', string.punctuation)

def remove_punctuation(text):
    return text.translate(translator).strip()
class Dictionary():
    def __init__(self, project_path) -> None:
        self.path = project_path + '/project.dictionary' # TODO: #4 Use all .dictionary files in drafts directory
        self.dictionary = self.load_dictionary()  # load the .dictionary (json file)
    
    def load_dictionary(self) -> Dict:
        try:
            with open(self.path, 'r') as file:
                data = json.load(file)
                return data
        except FileNotFoundError:
            # Create the directory if it does not exist
            os.makedirs(os.path.dirname(self.path), exist_ok=True)

            # Create the dictionary and write it to the file
            new_dict = {"entries": []}
            with open(self.path, 'w') as file:
                json.dump(new_dict, file)
            return new_dict

    def save_dictionary(self) -> None:
        with open(self.path, 'w') as file:
            json.dump(self.dictionary, file, indent=2)

    def define(self, word: str, level='unverified') -> None:
        word = remove_punctuation(word)
        
        # Add a word if it does not already exist
        if not any(entry['headWord'] == word for entry in self.dictionary['entries']):
            new_entry = {
                'headWord': word, 
                'level': level, 
                'id': str(uuid.uuid4()),
                'definition': '',
                'translationEquivalents': [],
                'links': [],
                'linkedEntries': [],
                'metadata': {'extra': {}},
                'notes': [],
                'extra': {}
            }
            
            self.dictionary['entries'].append(new_entry)
            self.save_dictionary()

    def remove(self, word: str) -> None:
        word = remove_punctuation(word)
        # Remove a word
        self.dictionary['entries'] = [entry for entry in self.dictionary['entries'] if entry['headWord'] != word]
        self.save_dictionary()

    

class SpellCheck:
    def __init__(self, dictionary: Dictionary, relative_checking=False):
        self.dictionary = dictionary
        self.relative_checking = relative_checking
        self.level_flag = 'verified auto' if relative_checking else 'verified' # TODO: #3 use enum for level_flag
    
    def is_correction_needed(self, word: str) -> bool:
        word = word.lower()
        word = remove_punctuation(word)
        return not any(
            entry['headWord'].lower() == word for entry in self.dictionary.dictionary['entries']
            if entry['level'] in self.level_flag
        )

    def check(self, word: str) -> List[str]:
        word = remove_punctuation(word).lower()
        if not self.is_correction_needed(word):
            return [word]  # No correction needed, return the original word

        entries = self.dictionary.dictionary['entries']
        possibilities = [
            (entry['headWord'], edit_distance.distance(entry['headWord'], word) / len(entry['headWord']) if len(entry['headWord']) > 0 else 0)
            for entry in entries
            if entry['level'] in self.level_flag
        ]

        # Adjust the threshold based on word length
        threshold_multiplier = 0.08  # You can adjust this value based on your needs
        possibilities = [
            (word, edit_distance) for word, edit_distance in possibilities
            if edit_distance <= threshold_multiplier * len(word)
        ]

        if not possibilities:
            return [sorted(entries, key=lambda x: x['headWord'])[0]['headWord']]  # Return the top result if no other suggestions

        sorted_possibilities = sorted(possibilities, key=lambda x: x[1])
        suggestions = [word for word, _ in sorted_possibilities]
        return suggestions[:5]
    
    def complete(self, word: str) -> List[str]:
        word = remove_punctuation(word)
        entries = self.dictionary.dictionary['entries']
        completions = [
            entry['headWord'][len(word):] for entry in entries
            if entry['level'] == 'verified' and word in entry['headWord']
        ]

        sorted_completions = sorted(completions, key=lambda x: edit_distance.distance(x, word))
        return sorted_completions[:5]


if __name__ == "__main__":

    path = 'C:\\Users\\danie\\example_workspace\\project_data'
    d = Dictionary(path)
    s = SpellCheck(d, True)
    print(s.complete('comp'))


