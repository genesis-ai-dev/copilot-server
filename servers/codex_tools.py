import json
import re


class CodexReader:
    def __init__(self, verse_chunk_size=4):
        self.verse_chunk_size = verse_chunk_size

    def read_file(self, filename):
        with open(filename, 'r') as file:
            data = json.load(file)
            return self.process_cells(data.get('cells', []))

    def process_cells(self, cells):
        chapters = []
        current_chapter = None

        for cell in cells:
            if cell['kind'] == 1:  # Markdown cell representing a chapter
                current_chapter = {"verse_chunks": []}
                chapters.append(current_chapter)
            elif cell['kind'] == 2:  # Scripture cell
                if current_chapter is not None:
                    verses = self.split_verses(cell['value'])
                    verse_chunks = self.chunk_verses(verses, cell['language'])
                    current_chapter["verse_chunks"].extend(verse_chunks)

        return {"chapters": chapters}

    def split_verses(self, scripture_text):
        marker_match = re.search(r'([A-Z]+) \d+:\d+', scripture_text)
        if marker_match:
            marker = marker_match.group(1)
            # Split the verses and keep the markers
            parts = re.split(f'({marker} \d+:\d+)', scripture_text)
            # Re-combine markers with verses
            verses = [parts[i] + parts[i + 1] for i in range(0, len(parts) - 1, 2)]
            if len(parts) % 2 != 0:
                verses.append(parts[-1])
        else:
            
            parts = re.split(r'(\w+ \d+:\d+)', scripture_text)
            verses = [parts[i] + parts[i + 1] for i in range(0, len(parts) - 1, 2)]
            if len(parts) % 2 != 0:
                verses.append(parts[-1])
        return verses

    def chunk_verses(self, verses, language):
        verses = list(filter(None, verses))
        return [self.combine_verses(verses[i:i+self.verse_chunk_size], language) for i in range(0, len(verses), self.verse_chunk_size)]

    def combine_verses(self, verse_chunk, language):
        first_verse_info = re.search(r'([A-Z]+) (\d+:\d+)', verse_chunk[0])
        last_verse_info = re.search(r'([A-Z]+) (\d+:\d+)', verse_chunk[-1])

        if first_verse_info and last_verse_info and first_verse_info.group(1) == last_verse_info.group(1):
            chunk_name = f"{language} {first_verse_info.group(1)} {first_verse_info.group(2)} - {last_verse_info.group(2)}"
        else:
            chunk_name = f"{language} Chunk (problematic schema)"

        combined_text = ''.join(re.sub(r'[A-Z]+\s\d+:\d+\n?', '', verse) for verse in verse_chunk)

        return {chunk_name: combined_text.strip()}
    
    def get_embed_format(self, filename):
        result = self.read_file(filename=filename)
        chapters = result['chapters']
        chunks = []
        for chapter in chapters:
            for chunk in chapter['verse_chunks']:
                chunks.append(tuple(chunk.items())[0])
        return chunks


# Example usage
reader = CodexReader(verse_chunk_size=5)
result = reader.get_embed_format("C:\\Users\\danie\\example_workspace\\drafts\\Bible\\ZEP.codex")

for i in result:
    print(i)