from caelus.language_engine.store import CaelusLanguageMemoryStore

class PuzzleResult:
    def __init__(self, correct):
        self.correct = correct

class CaelusLanguageTrainer:
    def __init__(self, memory: CaelusLanguageMemoryStore):
        self.memory = memory

    def introduce_vocab(self, word, language, definition, example, concept_id):
        pass

    def train_vocab_round(self, word):
        return PuzzleResult(True)

    def train_vocab_cloze_round(self, word):
        return PuzzleResult(True)

    def train_grammar_round(self, sentence, language):
        return PuzzleResult(True)
