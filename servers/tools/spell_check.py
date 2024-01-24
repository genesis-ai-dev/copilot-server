import tools.edit_distance as edit_distance
import json
import os
from typing import List, Dict

class Dictionary:
    def __init__(self, project_path) -> None:
        self.path = project_path + '/dictionary'
        self.dictionary = self.load_dictionary()  # load the .dictionary (json file)
    
    def load_dictionary(self) -> Dict:
        if os.path.exists(self.path):
            with open(self.path, 'r') as file:
                data = json.load(file)
                return data
        else:
            return {"entries": []}

    def save_dictionary(self) -> None:
        with open(self.path, 'w') as file:
            json.dump(self.dictionary, file, indent=2)

    def define(self, word: str, level='unverified') -> None:
        # Add a word if it does not already exist
        if not any(entry['headWord'] == word for entry in self.dictionary['entries']):
            self.dictionary['entries'].append({'headWord': word, 'level': level})
            self.save_dictionary()

    def remove(self, word: str) -> None:
        # Remove a word
        self.dictionary['entries'] = [entry for entry in self.dictionary['entries'] if entry['headWord'] != word]
        self.save_dictionary()

    

class SpellCheck:
    def __init__(self, dictionary: Dictionary, relative_checking=False):
        self.dictionary = dictionary
        self.relative_checking = relative_checking
        self.level_flag = 'verified auto' if relative_checking else 'verified'
    
    def is_correction_needed(self, word: str) -> bool:
        return not any(
            entry['headWord'] == word for entry in self.dictionary.dictionary['entries']
            if entry['level'] in self.level_flag
        )

    def check(self, word: str) -> List[str]:
        if not self.is_correction_needed(word):
            return [word]  # No correction needed, return the original word

        entries = self.dictionary.dictionary['entries']
        possibilities = [
            (entry['headWord'], edit_distance.distance(entry['headWord'], word))
            for entry in entries
            if entry['level'] in self.level_flag]
        
        sorted_possibilities = sorted(possibilities, key=lambda x: x[1])
        suggestions = [word for word, _ in sorted_possibilities]
        return suggestions[:5]
    
    def complete(self, word: str) -> List[str]:
        entries = self.dictionary.dictionary['entries']
        completions = [
            entry['headWord'] for entry in entries
            if entry['level'] == 'verified' and word in entry['headWord']
        ]

        sorted_completions = sorted(completions, key=lambda x: edit_distance.distance(x, word))
        return sorted_completions[:5]
