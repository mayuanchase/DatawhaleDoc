# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_search_dataset_step.py
    @date：2024/1/10 10:33
    @desc:
"""
import os
from typing import List, Dict

from django.db.models import QuerySet

from application.chat_pipeline.I_base_chat_pipeline import ParagraphPipelineModel
from application.chat_pipeline.step.search_dataset_step.i_search_dataset_step import ISearchDatasetStep
from common.config.embedding_config import VectorStore, EmbeddingModel
from common.db.search import native_search
from common.util.file_util import get_file_content
from dataset.models import Paragraph
from embedding.models import SearchMode
from smartdoc.conf import PROJECT_DIR
import logging
from typing import List


class BaseSearchDatasetStep(ISearchDatasetStep):

    def execute(self, problem_text: str, dataset_id_list: List[str], exclude_document_id_list: List[str],
                exclude_paragraph_id_list: List[str], top_n: int, similarity: float, padding_problem_text: str = None,
                search_mode: str = None, **kwargs) -> List['ParagraphPipelineModel']:
        """
        Execute the query on the vector database.

        :param problem_text: The query text.
        :param dataset_id_list: List of dataset IDs to include in the query.
        :param exclude_document_id_list: List of document IDs to exclude from the query.
        :param exclude_paragraph_id_list: List of paragraph IDs to exclude from the query.
        :param top_n: Number of top results to return.
        :param similarity: Similarity threshold for filtering results.
        :param padding_problem_text: Optional padded query text.
        :param search_mode: Mode of search to be used.
        :param kwargs: Additional keyword arguments.
        :return: List of processed paragraphs.
        """
        exec_problem_text = padding_problem_text if padding_problem_text else problem_text

        try:
            # Get the embedding model and embed the query text
            embedding_model = EmbeddingModel.get_embedding_model()
            embedding_value = embedding_model.embed_query(exec_problem_text)
        except Exception as e:
            logging.error(f"Error embedding query text: {e}")
            return []

        try:
            # Retrieve the embedding vector from the vector store
            vector = VectorStore.get_embedding_vector()
            embedding_list = vector.query(exec_problem_text, embedding_value, dataset_id_list, exclude_document_id_list,
                                          exclude_paragraph_id_list, True, top_n, similarity, SearchMode(search_mode))
        except Exception as e:
            logging.error(f"Error querying the vector store: {e}")
            return []

        if embedding_list is None:
            logging.info("No embeddings found for the given query.")
            return []

        try:
            # Retrieve and process the paragraphs based on the embedding list
            paragraph_list = self.list_paragraph(embedding_list, vector)
            result = [self.reset_paragraph(paragraph, embedding_list) for paragraph in paragraph_list]
        except Exception as e:
            logging.error(f"Error processing paragraphs: {e}")
            return []

        return result

    def list_paragraph(self, embedding_list, vector):
        # Implement your method to list paragraphs based on embedding_list and vector
        pass

    def reset_paragraph(self, paragraph, embedding_list):
        # Implement your method to reset a paragraph based on the embedding list
        pass

    @staticmethod
    def reset_paragraph(paragraph: Dict, embedding_list: List) -> ParagraphPipelineModel:
        filter_embedding_list = [embedding for embedding in embedding_list if
                                 str(embedding.get('paragraph_id')) == str(paragraph.get('id'))]
        if filter_embedding_list is not None and len(filter_embedding_list) > 0:
            find_embedding = filter_embedding_list[-1]
            return (ParagraphPipelineModel.builder()
                    .add_paragraph(paragraph)
                    .add_similarity(find_embedding.get('similarity'))
                    .add_comprehensive_score(find_embedding.get('comprehensive_score'))
                    .add_dataset_name(paragraph.get('dataset_name'))
                    .add_document_name(paragraph.get('document_name'))
                    .add_hit_handling_method(paragraph.get('hit_handling_method'))
                    .add_directly_return_similarity(paragraph.get('directly_return_similarity'))
                    .build())

    @staticmethod
    def get_similarity(paragraph, embedding_list: List):
        filter_embedding_list = [embedding for embedding in embedding_list if
                                 str(embedding.get('paragraph_id')) == str(paragraph.get('id'))]
        if filter_embedding_list is not None and len(filter_embedding_list) > 0:
            find_embedding = filter_embedding_list[-1]
            return find_embedding.get('comprehensive_score')
        return 0

    @staticmethod
    def list_paragraph(embedding_list: List, vector):
        paragraph_id_list = [row.get('paragraph_id') for row in embedding_list]
        if paragraph_id_list is None or len(paragraph_id_list) == 0:
            return []
        paragraph_list = native_search(QuerySet(Paragraph).filter(id__in=paragraph_id_list),
                                       get_file_content(
                                           os.path.join(PROJECT_DIR, "apps", "application", 'sql',
                                                        'list_dataset_paragraph_by_paragraph_id.sql')),
                                       with_table_name=True)
        # 如果向量库中存在脏数据 直接删除
        if len(paragraph_list) != len(paragraph_id_list):
            exist_paragraph_list = [row.get('id') for row in paragraph_list]
            for paragraph_id in paragraph_id_list:
                if not exist_paragraph_list.__contains__(paragraph_id):
                    vector.delete_by_paragraph_id(paragraph_id)
        # 如果存在直接返回的则取直接返回段落
        hit_handling_method_paragraph = [paragraph for paragraph in paragraph_list if
                                         (paragraph.get(
                                             'hit_handling_method') == 'directly_return' and BaseSearchDatasetStep.get_similarity(
                                             paragraph, embedding_list) >= paragraph.get(
                                             'directly_return_similarity'))]
        if len(hit_handling_method_paragraph) > 0:
            # 找到评分最高的
            return [sorted(hit_handling_method_paragraph,
                           key=lambda p: BaseSearchDatasetStep.get_similarity(p, embedding_list))[-1]]
        return paragraph_list

    def get_details(self, manage, **kwargs):
        step_args = self.context['step_args']

        return {
            'step_type': 'search_step',
            'paragraph_list': [row.to_dict() for row in self.context['paragraph_list']],
            'run_time': self.context['run_time'],
            'problem_text': step_args.get(
                'padding_problem_text') if 'padding_problem_text' in step_args else step_args.get('problem_text'),
            'model_name': EmbeddingModel.get_embedding_model().model_name,
            'message_tokens': 0,
            'answer_tokens': 0,
            'cost': 0
        }
