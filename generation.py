from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph
from typing import List
from typing_extensions import TypedDict
from deep_translator import GoogleTranslator


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        instruction: The prompt given by user
        title_en: Title generated by llm in English
        seo_en: The article title
        summary_en: Summary generated by llm in English
        body_en: Article body generated by llm
        title_id: The Indonesian translated title
        seo_id: The Indonesian translated title
        summary_id: The Indonesian translated summary
        body_id: The Indonesian translated article body
        tags: Tags generated by llm
    """

    instruction: str
    title_en: str
    seo_en: str
    summary_en: str
    body_en: str
    title_id: str
    seo_id: str
    summary_id: str
    body_id: str
    tags: List[str]


class ArticleGenerator:
    def __init__(self, llm):
        self.workflow = StateGraph(GraphState)
        self.llm = llm
        self._set_up_workflow()

    def _set_up_workflow(self):
        # Add notes to the graph
        self.workflow.add_node("title_generator", self.title_generator)
        self.workflow.add_node("summary_generator", self.summary_generator)
        self.workflow.add_node("body_generator", self.body_generator)
        # workflow.add_node("llm_translator", llm_translator)
        self.workflow.add_node("translator", self.translator)
        self.workflow.add_node("tags_generator", self.tags_generator)

        self.workflow.set_entry_point("title_generator")

        self.workflow.add_edge("title_generator", "summary_generator")
        self.workflow.add_edge("summary_generator", "body_generator")
        self.workflow.add_edge("body_generator", "translator")
        self.workflow.add_edge("translator", "tags_generator")

    # Node
    def title_generator(self, state):
        """Tool for generating the title for the article"""
        title_prompt = PromptTemplate(
            template="""
            You are a content creation assistant that specialize in writing blog articles from various topics.
            You will be given an instruction that decide topic of the article, generate an appropriate title based on topic.
            The language of the instruction will be either in English or Indonesian, but the generated title must be in English.
            Follow these guidelines:
                - The title must be less than 60 characters.
                - The title must be one sentence
                - The must be able to catch readers' attention
                - Return the title in the JSON format with the key 'title_en' with no preamble or explanation.
    
            Title to be generated: {instruction}""",
            input_variables=["instruction"]
        )

        title_gen = title_prompt | self.llm | JsonOutputParser()
        print("Receiving instruction......")
        print("Generating title......")
        response = title_gen.invoke({"instruction": state["instruction"]})
        print("Generating title complete!")
        print("Generating SEO......")
        seo_en = response['title_en']
        print("Generating SEO complete!")
        return {'title_en': response['title_en'], 'seo_en': seo_en}

    def summary_generator(self, state):
        """Tool for generating the summary for the article"""
        summary_prompt = PromptTemplate(
            template="""
            You are a creative professional content creation assistant that specialize in writing blog articles from various topics.
            You will be given the title of an article, generate an appropriate summary based on the title.
            Follow these guidelines:
                - The summary must be related to the title.
                - The summary should be able to pique readers curiosity or interests.
                - Write in active voice. Use the passive voice only in rare cases.
                - The summary should be clear and concise
                - The summary should be 5 to 8 sentences long.
                - The summary must be approximately 100 words.
                - Return the summary in the JSON format with a single key 'summary_en' and no preamble or explanation.
    
            Title of the article: {title_en}""",
            input_variables=["title_en"]
        )
        summary_gen = summary_prompt | self.llm | JsonOutputParser()
        print("Receiving title......")
        print("Generating summary......")
        response = summary_gen.invoke({"title_en": state["title_en"]})
        print("Generating summary complete!")
        return {'summary_en': response['summary_en']}

    def body_generator(self, state):
        """Tool for generating the body for the article"""
        body_prompt = PromptTemplate(
            template="""
            You are a creative professional content creation assistant that specialize in writing blog articles from various topics.
            You will be given the title and summary of an article, generate appropriate body paragraphs based on the title and summary.
            Follow these guidelines:
                - Start the body paragraph with the body content without repeating the title
                - The body paragraph must elaborate on the title and expand the points in summary, using specific, recent, and relatable examples or events to engage the reader.
                - The body paragraph should be around 1000 words long.
                - Use everyday language for accessibility. If technical terms are necessary, explain them upon first reference.
                - You can add bullets point in the body
                - Maintain clarity by keeping the subject and verb close together.
                - Structure the body using markdowns and paragraphs to pique the reader's curiosity and maintain interest throughout.
                - Write in active voice, using passive voice only when absolutely necessary.
                - Ensure each paragraph has a clear topic sentence and transitions smoothly to the next point.
                - Return the body in the JSON format with a single key 'body_en' and no preamble or explanation.
                
            Title of the article: {title_en}
            Summary of the article: {summary_en}""",
            input_variables=["title_en", "summary_en"]
        )

        body_gen = body_prompt | self.llm | JsonOutputParser()
        print("Receiving title & summary......")
        print("Generating article body......")
        response = body_gen.invoke({"title_en": state["title_en"], "summary_en": state["summary_en"]})
        print("Generating article body complete!")
        return {'body_en': response['body_en']}

    def translator(self, state):
        """Tool for translating the article using deep translator"""
        title_en = state["title_en"]
        summary_en = state["summary_en"]
        body_en = state["body_en"]
        print("Translating title & SEO to Indonesian......")
        title_id = GoogleTranslator(source='en', target='id').translate(text=title_en)
        seo_id = title_id
        print("Translating summary to Indonesian......")
        summary_id = GoogleTranslator(source='en', target='id').translate(text=summary_en)
        print("Translating article body to Indonesian......")
        body_id = GoogleTranslator(source='en', target='id').translate(text=body_en)
        print("Translation complete!")
        return {"title_id": title_id, "seo_id": seo_id, "summary_id": summary_id,
                "body_id": body_id}

    def tags_generator(self, state):
        """Tool for generating the tags for the article"""
        tags_prompt = PromptTemplate(
            template="""
            You are a creative professional content creation assistant that specialize in writing blog articles from various topics.
            You will be given the title and summary of an article in Indonesian, generate relevant and effective tags for the article in Indonesian.
            Follow these guidelines:
                - Ensure the tags encapsulate the content and key points of the article.
                - Use concise words or phrases that capture the essence of the article.
                - Use general tags to improve the article's reachability and relevance.
                - Each tag must be one or two words long.
                - Generate the most fitting tags.
                - Return the tags in the JSON format with a single key 'tags' as a list of string and no preamble or explanation.
    
            Title of the article: {title_id}
            Points of the article: {summary_id}""",
            input_variables=["title_id", "summary_id"]
        )

        tags_gen = tags_prompt | self.llm | JsonOutputParser()
        print("Receiving title & summary......")
        print("Generating tags......")
        response = tags_gen.invoke({"title_id": state["title_id"], "summary_id": state["summary_id"]})
        print("Generating tags complete!")
        return {'tags': response['tags']}

    def generate_article(self, instruction):
        app = self.workflow.compile()
        result = app.invoke({"instruction": instruction})
        return result

    # def llm_translator(self, state):
    #     """Tool for translating the article using llm"""
    #     trans_prompt = PromptTemplate(
    #         template="""
    #         You are a professional translator that specialize in translating blog articles from English to Indonesian.
    #         You will be given the title, seo, summary, and body of an article, translate these to Indonesian.
    #         Follow these guidelines:
    #             - Ensure the translation accurately conveys the meaning of the original text.
    #             - Maintain the original tone and style.
    #             - Use culturally appropriate expressions and idioms.
    #             - Ensure the translation is grammatically correct and natural-sounding.
    #             - Avoid literal translations unless necessary for clarity.
    #             - If there are any ambiguities or unclear phrases in the original text, provide the most likely interpretation in the translation.
    #             - Return the translation in the JSON format with no preamble or explanation with the following keys:
    #                 - 'title_id'
    #                 - 'seo_id'
    #                 - 'summary_id'
    #                 - 'body_id'
    #
    #         Title of the article: {title_en}
    #         SEO of the article: {seo_en}
    #         Summary of the article: {summary_en}
    #         Body of the article: {body_en}""",
    #         input_variables=["title_en", "seo_en", "summary_en", "body_en"]
    #     )
    #
    #     trans_gen = trans_prompt | llm | JsonOutputParser()
    #
    #     response = trans_gen.invoke(
    #         {"title_en": state["title_en"], "seo_en": state.seo_en, "summary_en": state.summary_en,
    #          "body_en": state.body_en})
    #     return {"title_id": response["title_id"], "seo_id": response["seo_id"], "summary_id": response["summary_id"],
    #             "body_id": response["body_id"]}