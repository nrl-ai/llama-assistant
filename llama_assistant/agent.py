from typing import List, Set, Optional, Dict, TYPE_CHECKING

from llama_cpp import Llama
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.schema import NodeWithScore
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.workflow import Context
from llama_index.core.postprocessor import SimilarityPostprocessor

from llama_index.core.workflow import Event, StartEvent, StopEvent, Workflow, step

SYSTEM_PROMPT = {"role": "system", "content": "Generate short and simple response."}


def convert_message_list_to_str(messages):
    chat_history_str = ""
    for message in messages:
        if type(message["content"]) is str:
            chat_history_str += message["role"] + ": " + message["content"] + "\n"
        else:
            chat_history_str += message["role"] + ": " + message["content"]["text"] + "\n"

    return chat_history_str


class SetupEvent(Event):
    pass


class CondenseQueryEvent(Event):
    condensed_query_str: str


class RetrievalEvent(Event):
    nodes: List[NodeWithScore]


class ChatHistory:
    def __init__(self, llm, max_history_size: int, max_output_tokens: int):
        self.llm = llm
        self.max_output_tokens = max_output_tokens
        self.max_history_size = max_history_size  # in tokens
        self.max_history_size_in_words = max_history_size * 3 / 4
        self.max_history_size_in_words = (
            self.max_history_size_in_words - 128
        )  # to account for some formatting tokens
        print("Max history size in words:", self.max_history_size_in_words)
        self.total_size = 0
        self.chat_history = []

    def _get_message_size(self, message: dict) -> int:
        """Calculate the size of a message in words"""
        if "content" in message and type(message["content"]) is list:
            # multimodal model's message format
            return len(message["content"][0]["text"].split())
        else:
            # text-only model's message format
            return len(message["content"].split())

    def add_conversation_turn(self, user_message: dict, assistant_message: dict):
        """Add a complete conversation turn (user + assistant) to history"""
        user_msg_size = self._get_message_size(user_message)
        assistant_msg_size = self._get_message_size(assistant_message)
        total_new_size = user_msg_size + assistant_msg_size

        if self.total_size + total_new_size > self.max_history_size_in_words:
            print("Chat history is too long, summarizing the conversation...")
            history_summary = self.llm.create_chat_completion(
                messages=[SYSTEM_PROMPT]
                + self.chat_history
                + [
                    {
                        "role": "user",
                        "content": "Briefly summarize the conversation in a few sentences.",
                    }
                ],
                stream=False,
                max_tokens=256,
            )["choices"][0]["message"]["content"]

            # new history with the summary and the new conversation turn
            # Summary is treated as if the assistant said it, followed by the new user message and response
            self.chat_history = [
                {"role": "user", "content": "Please summarize our conversation so far."},
                {"role": "assistant", "content": history_summary},
                user_message,
                assistant_message,
            ]

            self.total_size = (
                len(history_summary.split()) + total_new_size + 10
            )  # +10 for summary prompt
        else:
            self.chat_history.append(user_message)
            self.chat_history.append(assistant_message)
            self.total_size += total_new_size

        print("\nChat history word count:", self.total_size)

    def add_message(self, message: dict):
        """Add a single message to history (for backward compatibility)"""
        new_msg_size = self._get_message_size(message)

        if self.total_size + new_msg_size > self.max_history_size_in_words:
            print("Chat history is too long, summarizing the conversation...")
            history_summary = self.llm.create_chat_completion(
                messages=[SYSTEM_PROMPT]
                + self.chat_history
                + [
                    {
                        "role": "user",
                        "content": "Briefly summarize the conversation in a few sentences.",
                    }
                ],
                stream=False,
                max_tokens=256,
            )["choices"][0]["message"]["content"]

            # new history with the summary of the conversation and the last message
            # Ensure proper role alternation
            if message["role"] == "user":
                self.chat_history = [
                    {"role": "user", "content": "Please summarize our conversation so far."},
                    {"role": "assistant", "content": history_summary},
                    message,
                ]
            else:
                # If adding assistant message, we need a user message before it
                self.chat_history = [{"role": "assistant", "content": history_summary}, message]

            self.total_size = len(history_summary.split()) + new_msg_size + 10
        else:
            self.chat_history.append(message)
            self.total_size += new_msg_size

        print("\nChat history word count:", self.total_size)

    def get_chat_history(self):
        return self.chat_history

    def clear(self):
        self.chat_history = []
        self.total_size = 0

    def __len__(self):
        return len(self.chat_history)


class RAGAgent(Workflow):
    SUMMARY_TEMPLATE = (
        "Given the converstation:\n"
        "'''{chat_history_str}'''\n\n"
        "Rewrite to a standalone question:\n"
    )

    CONTEXT_PROMPT_TEMPLATE = (
        "Information that might help:\n"
        "-----\n"
        "{node_context}\n"
        "-----\n"
        "Please write a response to the following question, using the above information if relevant:\n"
        "{query_str}\n"
    )

    def __init__(
        self,
        generation_setting: Dict,
        rag_setting: Dict,
        llm: Llama,
        timeout: int = 60,
        verbose: bool = False,
    ):
        super().__init__(timeout=timeout, verbose=verbose)
        self.generation_setting = generation_setting
        self.context_len = generation_setting["context_len"]
        self.max_output_tokens = generation_setting["max_output_tokens"]

        self.max_input_tokens = self.context_len - self.max_output_tokens

        self.retrieval_top_k = self.max_input_tokens // rag_setting["chunk_size"] - 1
        self.retrieval_top_k = min(max(1, self.retrieval_top_k), rag_setting["max_retrieval_top_k"])
        self.search_index = None
        self.retriever = None

        self.chat_history = ChatHistory(
            llm=llm,
            max_output_tokens=self.max_output_tokens,
            max_history_size=self.max_input_tokens,
        )
        self.lookup_files = set()

        self.embed_model = HuggingFaceEmbedding(model_name=rag_setting["embed_model_name"])
        Settings.embed_model = self.embed_model
        Settings.chunk_size = rag_setting["chunk_size"]
        Settings.chunk_overlap = rag_setting["chunk_overlap"]
        self.node_processor = SimilarityPostprocessor(
            similarity_cutoff=rag_setting["similarity_threshold"]
        )
        self.llm = llm

    def update_index(self, files: Optional[Set[str]] = set()):
        if not files:
            print("No lookup files provided, clearing index...")
            self.retriever = None
            self.search_index = None
            return

        print("Indexing documents...")
        documents = SimpleDirectoryReader(input_files=files, recursive=True).load_data(
            show_progress=True, num_workers=1
        )

        self.search_index = VectorStoreIndex.from_documents(documents, embed_model=self.embed_model)

        self.retriever = self.search_index.as_retriever(similarity_top_k=self.retrieval_top_k)

    def update_rag_setting(self, rag_setting: Dict):
        if self.node_processor.similarity_cutoff != rag_setting["similarity_threshold"]:
            self.node_processor = SimilarityPostprocessor(
                similarity_cutoff=rag_setting["similarity_threshold"]
            )

        new_top_k = (self.context_len - rag_setting["chunk_size"]) // rag_setting["chunk_overlap"]
        new_top_k = min(max(1, new_top_k), rag_setting["max_retrieval_top_k"])
        if self.retrieval_top_k != new_top_k:
            self.retrieval_top_k = new_top_k
            if self.retriever:
                self.retriever = self.search_index.as_retriever(
                    similarity_top_k=self.retrieval_top_k
                )

        if (
            self.embed_model.model_name != rag_setting["embed_model_name"]
            or Settings.chunk_size != rag_setting["chunk_size"]
            or Settings.chunk_overlap != rag_setting["chunk_overlap"]
        ):
            self.embed_model = HuggingFaceEmbedding(model_name=rag_setting["embed_model_name"])
            Settings.embed_model = self.embed_model
            Settings.chunk_size = rag_setting["chunk_size"]
            Settings.chunk_overlap = rag_setting["chunk_overlap"]

            # reindex since those are the settings that affect the index
            if self.lookup_files:
                print("Re-indexing documents since the rag settings have changed...")
                documents = SimpleDirectoryReader(
                    input_files=self.lookup_files, recursive=True
                ).load_data(show_progress=True, num_workers=1)
                self.search_index = VectorStoreIndex.from_documents(
                    documents, embed_model=self.embed_model
                )
                self.retriever = self.search_index.as_retriever(
                    similarity_top_k=self.retrieval_top_k
                )

    def update_generation_setting(self, generation_setting):
        self.generation_setting = generation_setting
        self.context_len = generation_setting["context_len"]

    @step
    async def setup(self, ctx: Context, ev: StartEvent) -> SetupEvent:
        # set frequently used variables to context
        query_str = ev.query_str
        image = ev.image
        lookup_files = ev.lookup_files if ev.lookup_files else set()
        streaming = ev.streaming
        await ctx.store.set("query_str", query_str)
        await ctx.store.set("image", image)
        await ctx.store.set("streaming", streaming)

        # update index if needed
        if lookup_files != self.lookup_files:
            print("Different lookup files, updating index...")
            self.update_index(lookup_files)

        self.lookup_files = lookup_files.copy()

        return SetupEvent()

    @step
    async def condense_history_to_query(self, ctx: Context, ev: SetupEvent) -> CondenseQueryEvent:
        """
        Condense the chat history and the query into a single query. Only used for retrieval.
        """
        query_str = await ctx.store.get("query_str")

        if len(self.chat_history) > 0 and self.retriever is not None:
            standalone_query = self.llm.create_chat_completion(
                messages=[SYSTEM_PROMPT]
                + self.chat_history.get_chat_history()
                + [
                    {
                        "role": "user",
                        "content": query_str
                        + "\n Condense this conversation to stand-alone question using only 1 sentence.",
                    }
                ],
                stream=False,
                top_k=self.generation_setting["top_k"],
                top_p=self.generation_setting["top_p"],
                temperature=self.generation_setting["temperature"],
                max_tokens=128,
            )["choices"][0]["message"]["content"]

            condensed_query = standalone_query + "\nQuestion: " + query_str

        else:
            # if there is no history or no need for retrieval, return the query as is
            condensed_query = query_str

        return CondenseQueryEvent(condensed_query_str=condensed_query)

    @step
    async def retrieve(self, ctx: Context, ev: CondenseQueryEvent) -> RetrievalEvent:
        if not self.retriever:
            return RetrievalEvent(nodes=[])

        # retrieve from dropped documents
        condensed_query_str = ev.condensed_query_str
        nodes = await self.retriever.aretrieve(condensed_query_str)
        nodes = self.node_processor.postprocess_nodes(nodes)
        return RetrievalEvent(nodes=nodes)

    def _prepare_query_with_context(
        self,
        query_str: str,
        nodes: List[NodeWithScore],
    ) -> str:
        node_context = ""

        if len(nodes) == 0:
            return query_str

        # Calculate available space for RAG context
        # Reserve space for: system prompt, chat history, query, and output
        chat_history_size = self.chat_history.total_size
        query_size = len(query_str.split())

        # Convert words to approximate tokens (1 word ≈ 1.3 tokens)
        estimated_tokens_used = int((chat_history_size + query_size) * 1.3)
        available_tokens = (
            self.context_len - self.max_output_tokens - estimated_tokens_used - 200
        )  # 200 buffer

        # Convert available tokens to words
        max_context_words = int(available_tokens / 1.3)

        if max_context_words < 100:
            # Not enough space for RAG context, return query without context
            print(
                f"Warning: Not enough context space for RAG. Available: {max_context_words} words"
            )
            return query_str

        # Add nodes until we reach the limit
        current_words = 0
        for idx, node in enumerate(nodes):
            node_text = node.get_content(metadata_mode="llm")
            node_words = len(node_text.split())

            if current_words + node_words > max_context_words:
                print(f"Truncating RAG context at node {idx} to fit within context window")
                break

            node_context += f"\n{node_text}\n\n"
            current_words += node_words

        if not node_context:
            return query_str

        formatted_query = self.CONTEXT_PROMPT_TEMPLATE.format(
            node_context=node_context, query_str=query_str
        )

        return formatted_query

    @step
    async def llm_response(self, ctx: Context, retrieval_ev: RetrievalEvent) -> StopEvent:
        nodes = retrieval_ev.nodes
        query_str = await ctx.store.get("query_str")
        image = await ctx.store.get("image")
        query_with_ctx = self._prepare_query_with_context(query_str, nodes)
        streaming = await ctx.store.get("streaming", default=False)

        if image:
            formated_message = {
                "role": "user",
                "content": [
                    {"type": "text", "text": query_with_ctx},
                    {"type": "image_url", "image_url": {"url": image}},
                ],
            }
        else:
            formated_message = {"role": "user", "content": query_with_ctx}

        # Build messages for LLM but don't add to history yet
        messages_for_llm = (
            [SYSTEM_PROMPT] + self.chat_history.get_chat_history() + [formated_message]
        )

        response = self.llm.create_chat_completion(
            messages=messages_for_llm,
            stream=streaming,
            top_k=self.generation_setting["top_k"],
            top_p=self.generation_setting["top_p"],
            temperature=self.generation_setting["temperature"],
            max_tokens=self.max_output_tokens,
        )

        # Store the user message to be added to history after response is complete
        await ctx.store.set("user_message", formated_message)

        return StopEvent(result=response)
