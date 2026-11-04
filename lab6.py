import sys
import re
import math
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")


def run_tokenization():
    samples = [
        "AI, search!",
        "I can't log in.",
        "help@example.com",
        "CS4944 version 2.1",
        "",
        "یہ ایک مثال ہے"
    ]
    for text in samples:
        ws = text.split()
        words = re.findall(r"\b\w+\b", text, flags=re.UNICODE)
        print(f"Text: {repr(text)}")
        print(f"  Whitespace tokens ({len(ws)}): {ws}")
        print(f"  Regex word tokens ({len(words)}): {words}")


class FAQBot:
    def __init__(self, faqs):
        self.faqs = faqs

    def reply(self, query):
        q_clean = query.strip()
        if not q_clean:
            return "Please enter a question."

        for item in self.faqs:
            if q_clean.casefold() == item["question"].casefold():
                return f"{item['answer']} [source: {item['source']}]"

        q_words = set(re.findall(r"\b\w+\b", q_clean.lower()))
        matches = []
        for item in self.faqs:
            faq_words = set(re.findall(r"\b\w+\b", item["question"].lower()))
            overlap = len(q_words & faq_words)
            if overlap > 0:
                matches.append((item["question"], overlap))

        if not matches:
            return "No matching FAQ. Please contact the help desk."

        matches.sort(key=lambda x: x[1], reverse=True)
        lines = ["Possible matches:"]
        for q, score in matches[:3]:
            lines.append(f"  - {q} (overlap score: {score})")
        return "\n".join(lines)


def word_spans(text):
    return [(m.start(), m.end()) for m in re.finditer(r"\S+", text)]


def windows(text, size=40, overlap=10, offset=0):
    if size <= 0 or not 0 <= overlap < size:
        raise ValueError("Invalid size or overlap")
    spans = word_spans(text)
    result = []
    if not spans:
        return result
    step = size - overlap
    for i in range(0, len(spans), step):
        j = min(i + size, len(spans))
        result.append((offset + spans[i][0], offset + spans[j - 1][1]))
        if j == len(spans):
            break
    return result


def sentence_chunks(text, size=40):
    if size <= 0:
        raise ValueError("Size must be positive")
    cuts = [0] + [m.end() for m in re.finditer(r"[.!?]\s+", text)] + [len(text)]
    out = []
    pending = None
    count = 0
    for a, b in zip(cuts, cuts[1:]):
        segment = text[a:b]
        words_in_seg = len(segment.split())
        if not words_in_seg:
            continue
        if words_in_seg > size:
            if pending is not None:
                out.append(pending)
            out.extend(windows(segment, size, 0, a))
            pending, count = None, 0
        elif pending is not None and count + words_in_seg <= size:
            pending = (pending[0], b)
            count += words_in_seg
        else:
            if pending is not None:
                out.append(pending)
            pending = (a, b)
            count = words_in_seg
    if pending is not None:
        out.append(pending)
    return out


def make_chunks(docs, strategy):
    result = []
    for doc_id, text in docs.items():
        if strategy == "sentence":
            spans = sentence_chunks(text, size=40)
        else:
            spans = windows(text, size=40, overlap=int(strategy))
        for i, (start, end) in enumerate(spans):
            result.append({
                "id": f"{doc_id}:{i}",
                "doc": doc_id,
                "start": start,
                "end": end,
                "text": text[start:end]
            })
    return result


class SimpleTFIDF:
    def __init__(self, documents):
        self.documents = documents
        self.doc_tokens = [re.findall(r"\b\w+\b", d.lower()) for d in documents]
        self.total_docs = len(documents)
        self.df = Counter()
        for dt in self.doc_tokens:
            for term in set(dt):
                self.df[term] += 1
        self.vocab = sorted(list(self.df.keys()))
        self.vocab_map = {term: idx for idx, term in enumerate(self.vocab)}
        self.idf = {t: math.log((self.total_docs + 1) / (self.df[t] + 1)) + 1 for t in self.vocab}
        self.vectors = [self.vectorize(t) for t in self.doc_tokens]

    def vectorize(self, tokens):
        tf = Counter(tokens)
        vec = [0.0] * len(self.vocab)
        for term, freq in tf.items():
            if term in self.vocab_map:
                vec[self.vocab_map[term]] = freq * self.idf[term]
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    def search(self, query):
        tokens = re.findall(r"\b\w+\b", query.lower())
        q_vec = self.vectorize(tokens)
        scored = []
        for i, d_vec in enumerate(self.vectors):
            score = sum(a * b for a, b in zip(q_vec, d_vec))
            scored.append((i, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored


def evaluate_retrieval(chunks, queries):
    corpus_texts = [c["text"] for c in chunks]
    engine = SimpleTFIDF(corpus_texts)
    hits = []
    reciprocals = []

    for item in queries:
        target_doc = item["doc"]
        evidence = item.get("evidence")
        if target_doc is None:
            continue
        search_results = engine.search(item["query"])
        ranks = []
        for rank, (chunk_idx, score) in enumerate(search_results[:3], 1):
            chunk = chunks[chunk_idx]
            if chunk["doc"] == target_doc and (evidence is None or evidence in chunk["text"]):
                ranks.append(rank)
        hits.append(1 if ranks else 0)
        reciprocals.append(1.0 / ranks[0] if ranks else 0.0)

    hit_at_3 = sum(hits) / len(hits) if hits else 0.0
    mrr_at_3 = sum(reciprocals) / len(reciprocals) if reciprocals else 0.0
    return hit_at_3, mrr_at_3


if __name__ == "__main__":
    print("--- Task 1: Tokenization Comparison ---")
    run_tokenization()

    print("\n--- Task 1: FAQ Chatbot ---")
    faq_data = [
        {"question": "How do I reset my password?", "answer": "Use the recovery link on the login page.", "source": "it_help.txt"},
        {"question": "Where do I submit my assignment?", "answer": "Use the assignment upload page in the learning portal.", "source": "assessment.txt"},
        {"question": "Can illness justify a late submission?", "answer": "Request an extension with medical evidence before the deadline.", "source": "handbook.txt"}
    ]
    bot = FAQBot(faq_data)
    print("Exact:", bot.reply("How do I reset my password?"))
    print("Suggestion:", bot.reply("password reset"))
    print("Unsupported:", bot.reply("volcano geology"))

    print("\n--- Task 2: Chunking ---")
    docs = {
        "doc1": "Late submission is normally penalized. Students with illness may request an extension with medical evidence before the deadline. Assignments must be submitted in PDF format.",
        "doc2": "Reset a forgotten password using the recovery link. Never share recovery codes with anyone."
    }
    chunks_sent = make_chunks(docs, "sentence")
    chunks_win0 = make_chunks(docs, "0")
    chunks_win10 = make_chunks(docs, "10")
    print(f"Sentence Chunks: {len(chunks_sent)} | Window(overlap=0): {len(chunks_win0)} | Window(overlap=10): {len(chunks_win10)}")

    print("\n--- Task 3: Retrieval Evaluation ---")
    queries = [
        {"query": "illness late submission", "doc": "doc1", "evidence": "medical evidence", "split": "dev"},
        {"query": "forgot password link", "doc": "doc2", "evidence": "recovery link", "split": "dev"},
        {"query": "what is the capital of France?", "doc": None, "evidence": None, "split": "test"}
    ]
    hit, mrr = evaluate_retrieval(chunks_sent, queries)
    print(f"Sentence Chunks -> Hit@3: {hit:.3f}, MRR@3: {mrr:.3f}")
    hit_w, mrr_w = evaluate_retrieval(chunks_win10, queries)
    print(f"Window(10) Chunks -> Hit@3: {hit_w:.3f}, MRR@3: {mrr_w:.3f}")
