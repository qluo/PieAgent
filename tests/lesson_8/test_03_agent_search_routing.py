from agent.agent import Agent


class RoutingLlm:
    def __init__(self, should_search):
        self.should_search = should_search
        self.search_decisions = []
        self.answers = []
        self.context_answers = []

    def needs_search(self, prompt):
        self.search_decisions.append(prompt)
        return self.should_search

    def answer(self, user_text):
        self.answers.append(user_text)
        return "direct answer"

    def answer_with_context(self, user_text, context):
        self.context_answers.append((user_text, context))
        return "search answer"


class RecordingSearchTool:
    def __init__(self):
        self.queries = []

    def search(self, query):
        self.queries.append(query)
        return "search context"


def make_agent(llm, search):
    return Agent(
        face_state=None,
        wake_word=None,
        stt=None,
        tts=None,
        llm=llm,
        tools={"search": search},
    )


def test_agent_responds_directly_when_search_is_not_needed():
    llm = RoutingLlm(should_search=False)
    search = RecordingSearchTool()

    assert make_agent(llm, search).respond("Tell me a joke") == "direct answer"
    assert "Tell me a joke" in llm.search_decisions[0]
    assert "Tell me a joke" in llm.answers[0]
    assert search.queries == []


def test_agent_uses_search_context_when_the_llm_requests_it():
    llm = RoutingLlm(should_search=True)
    search = RecordingSearchTool()

    assert make_agent(llm, search).respond("What happened today?") == "search answer"
    assert search.queries == ["What happened today?"]
    prompt, context = llm.context_answers[0]
    assert "What happened today?" in llm.search_decisions[0]
    assert "What happened today?" in prompt
    assert context == "search context"
